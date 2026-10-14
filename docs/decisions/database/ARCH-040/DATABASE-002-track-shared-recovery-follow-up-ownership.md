---
id: ARCH-040-DATABASE-002
architecture_id: ARCH-040
title: Track shared recovery follow-up ownership
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-DATABASE-001
enables:
  - ARCH-040-SHARED-001
  - ARCH-040-API-004
  - ARCH-040-BACKGROUND-003
  - ARCH-040-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040-DATABASE-002 — Track shared recovery follow-up ownership

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Make the **existing** `commerce.RecoveryOutreachAttempt` sequence-2 row the single, immutable claim for a recovery's one post-window follow-up, regardless of whether the merchant or CommerceAgent initiated it. Provide durable initiator provenance and message/recovery integrity, without creating a new Conversation or credit ledger.

## Context

Existing schema: `RecoveryOutreachAttempt` has `@@unique([checkoutRecoveryId, sequence])`, statuses `PENDING`, `WAITING_FOR_RESPONSE`, `ENGAGED`, `NO_RESPONSE`, `CAPACITY_BLOCKED`, `CANCELLED`, `FAILED`, a unique optional `outboundMessageId`, `sentAt`, and `trigger=INITIAL | NO_RESPONSE_FOLLOW_UP`. The existing automated processor uses `sequence=2` and `recovery-outreach:<attempt.id>` for outbound idempotency; `RecoveryBillingService.admit({shopId, recoveryId, outreachAttemptId})` already derives a stable credit source key from the **attempt ID**.

## Scope

- Extend `RecoveryOutreachAttempt` in `moda-interact-database/prisma/schema.prisma` with claim provenance and a trigger capable of representing a post-window merchant-initiated follow-up.
- Add the fresh-database schema migration, integrity checks and focused PostgreSQL concurrency tests; no upgrade/backfill tests.
- Preserve the existing attempt, existing status lifecycle, `outboundMessageId`, and provider/billing linkage. The existing `(checkoutRecoveryId, sequence)` unique constraint remains the **only** count-of-follow-ups gate.

## Out of Scope

- No `HumanFollowUp`, second outreach table, new `Conversation`, new `UsageReservation`, usage event, credit counter or new billing identity.
- No producer claim logic, provider call, 24-hour eligibility calculator, Meta template selector, state-machine rewrite, scheduled-worker change or retry dispatch implementation; API-004/BACKGROUND-003 own these.
- No new merchant-only second attempt after the automated attempt has claimed sequence 2, and no regeneration of sequence 2 under a different row ID.
- No `docs/decisions/**/_index.md` updates pending user confirmation.

## Requirements

### Exact Prisma extension

```prisma
enum RecoveryOutreachInitiator {
  HUMAN
  AGENT
  AUTOMATION
  @@schema("commerce")
}

// Extend existing RecoveryOutreachTrigger with:
// POST_WINDOW_FOLLOW_UP
// Keep INITIAL and NO_RESPONSE_FOLLOW_UP for existing records/automated no-response.

// Add nullable fields on existing RecoveryOutreachAttempt:
initiatedBy           RecoveryOutreachInitiator?
initiationKey         String? @unique @db.VarChar(255)
claimedAt             DateTime? @db.Timestamptz(3)
```

- `sequence=1` stays `trigger=INITIAL`; `sequence=2` is the only permitted follow-up. Its trigger can be `NO_RESPONSE_FOLLOW_UP` for the existing automatic no-response schedule or `POST_WINDOW_FOLLOW_UP` for an otherwise eligible manual/AI post-window initiation. **Trigger describes the reason, `initiatedBy` describes the author**; never infer which actor sent the message solely from `trigger`.
- `initiationKey` is the stable durable **logical follow-up claim identity**, not the outbound Meta message ID and not the recovery credit reservation ID. A winning claim atomically writes `initiatedBy`, `initiationKey` and `claimedAt`. No staff principal or source-platform fields are persisted for any initiator. The key and initiator fields are immutable once populated. Use PostgreSQL constraints/trigger protection for set-once provenance; allow normal status/receipt reconciliation.
- The existing unique `(checkoutRecoveryId, sequence)` ensures **one** sequence-2 row per recovery; a conditional update against unclaimed `initiationKey IS NULL` ensures **one** initiator wins. If an automated job has created an unclaimed PENDING sequence-2 row first, a later human may atomically claim **that same row**, but cannot replace a winner. Do not treat an `upsert(..., update: {})` as ownership of the claim.
- Once claimed, any retry must reuse the original sequence-2 `id`, `initiationKey`, sender/author identity, and deterministic outbound and credit identities. Provider-uncertain sends remain claimed until reconciled; do not clear `initiationKey` after timeouts. A definitively failed send is not billable and may be retried only under the same logical attempt, according to BACKGROUND-003 policy; never create a fresh sequence-2 row or second distinct claim.
- Maintain existing provider-message relation. Add a PostgreSQL **constraint trigger** on setting/changing `outboundMessageId` that proves `ConversationMessage.conversationId` points to the `Conversation` whose `checkoutRecoveryId` equals this attempt's `checkoutRecoveryId`; a normal Prisma FK alone does not enforce this cross-table condition.
- Add `CHECK` rules: `sequence IN (1,2)`; sequence/trigger pairing; claim presence consistency (`initiationKey`, `claimedAt`, `initiatedBy` are collectively null or nonnull); `initiatedBy` restricted to HUMAN/AGENT/AUTOMATION (no staff actor fields). A claimed sequence-2 row does **not** need a sent message yet. Keep existing `PENDING`/`FAILED`/`CAPACITY_BLOCKED` states and `sentAt` unchanged: they express delivery lifecycle, not the right to claim. Preserve the existing `@@unique([outboundMessageId])` and existing indexes; add an index only if an actual query needs one not covered by them.
- **Credit invariant:** follow-up credit stays `createRecoveryIdempotencyKey(shopId, "recovery-outreach:" + outreachAttempt.id)` through existing `RecoveryBillingService`. Schema must neither charge by `initiationKey`, `HUMAN` staff identifier, nor create a new recovery-conversation record. One initial outreach may consume one recovery credit; successful sequence 2 consumes one more credit for the **same conversation thread**.

### Development-only schema delivery

- **Fresh development database only:** extend the existing `RecoveryOutreachAttempt` model and create its SQL checks/triggers through the repository's normal migrations. Do not implement historic sequence-2 initiator backfill, legacy-data inspection, upgrade-repair logic or rollback procedures.
- Fresh seed fixtures must cover sequence-1 INITIAL, unclaimed sequence-2 PENDING, and claimed sequence-2 by HUMAN/AGENT/AUTOMATION. A newly created sequence-2 row may start unclaimed; its claim fields become populated atomically when one initiator wins.
- Do not weaken `(checkoutRecoveryId, sequence)` uniqueness or the same-conversation `outboundMessageId` validation to simplify test setup.

## Work Items

- [ ] Preserve the canonical sequence-1/sequence-2 unique key and add `POST_WINDOW_FOLLOW_UP` trigger variant without replacing existing enum values.
- [ ] Add initiator/claim fields, matching checks, set-once protections, and unique initiationKey.
- [ ] Add cross-table constraint trigger protecting outboundMessageId from belonging to another conversation/recovery.
- [ ] Add the fresh-database schema migration and seed-based constraints/tests; no historical attempt backfill or data-repair tooling.
- [ ] Add focused concurrency and FK/constraint tests for competing HUMAN vs AUTOMATION/AGENT claims.

## Interfaces / Contracts

- `ARCH-040-DATABASE-001` provides conversation control/revision. `ARCH-040-SHARED-001` defines producer/consumer claim outcomes using `initiatedBy` as HUMAN/AGENT/AUTOMATION with no individual staff identity.
- `API-004` and `BACKGROUND-003` must claim **the same** sequence-2 row in a transaction, then use existing recovery-billing admission and provider idempotency keyed by the row ID. For a human follow-up, DATABASE-003 will additionally relate the accepted command to that attempt.
- Keep existing `RecoveryOutreachStatus` as **outreach/delivery** state; no new parallel `humanFollowUpSent` boolean, no counters on `Conversation`, and no duplicate credit source key.

## Dependencies

- ARCH-040-DATABASE-001

## Enables

- ARCH-040-SHARED-001
- ARCH-040-API-004
- ARCH-040-BACKGROUND-003
- ARCH-040-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Two competing initiators for the same recovery produce one `sequence=2` attempt and exactly one durable claimant; losing claimant cannot overwrite the winning actor/claim key.
- [ ] A row inserted as unclaimed PENDING may be claimed by one initiator; a claimed or provider-uncertain row cannot be re-claimed as another person's follow-up.
- [ ] An initial outreach and one follow-up still reference the **same existing Conversation** and independently identified messages; attempting to attach a foreign-conversation message fails at PostgreSQL level.
- [ ] Existing `status`, `sentAt`, provider message ID, credit reservation/source identity, and retry semantics remain usable; a provider-status update cannot mutate initiator evidence.
- [ ] Fresh schema rejects sequence 3, mismatched sequence/trigger pairs, invalid actor/claim combinations and attempts to change a winning claim.
- [ ] No new usage reservation/conversation row is introduced merely by claiming sequence 2; one confirmed follow-up is counted by existing recovery billing exactly once, independent of sender.

## Validation

- [ ] Prisma validate and generate client for the new schema.
- [ ] Apply migrations to an empty disposable PostgreSQL database; seed PENDING, FAILED, SENT and CAPACITY_BLOCKED sequence-2 records and verify constraints. No historic/upgrade fixtures.
- [ ] Parallel transaction race tests (one HUMAN and one AUTOMATION), claim immutability, no third sequence, malformed initiator cases, cross-conversation message association, and idempotent rerun.
- [ ] Confirm `@@unique([checkoutRecoveryId, sequence])` and `outboundMessageId` uniqueness work on a clean database; run `git diff --check`.
- [ ] Record isolated task-worktree and migration/submodule synchronization evidence.

## Stop Condition

Complete only DATABASE-002; set its task to review with evidence and return to `moda_architect`. Do not implement background claim/charging logic or start DATABASE-003.

## Implementation Notes

This is a **schema and persistence-invariant** task, not a billing rewrite. An ordinary PostgreSQL foreign key from `outboundMessageId` to `ConversationMessage.id` cannot prove recovery ownership; use a trigger for that cross-row rule. The user’s earlier one-conversation clarification is mandatory: **one `Conversation.id`, multiple authors and messages; initial/follow-up are outreach/credit events, not conversation rows.** The schema supports the currently open business-policy question (follow-up after earlier customer engagement) without answering it inside DATABASE-002.

## Completion Report

### Status
Not Started

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
The architecture is proposed; implementation starts only after agreed/materialised task definition.

### Unresolved Issues
None recorded at definition time.

### Architectural Concerns
Return newly discovered contract or ownership gaps to moda_architect.

## Architect Review

### Review Status
Pending

### Review Notes
Not reviewed.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending.

### Follow-up
None.
