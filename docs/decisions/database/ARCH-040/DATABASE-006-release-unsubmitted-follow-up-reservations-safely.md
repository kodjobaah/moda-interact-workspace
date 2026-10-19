---
id: ARCH-040-DATABASE-006
architecture_id: ARCH-040
title: Permit safe release and reuse of unsubmitted recovery follow-up reservations
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-DATABASE-001
enables:
  - ARCH-040-BACKGROUND-007
created: 2026-10-19
updated: 2026-10-19
---

# ARCH-040-DATABASE-006 — Safe release of unsubmitted sequence-two follow-up claims

## Architecture

- Initiative: `ARCH-040`.
- Canonical parent: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`.
- Coordinator: `moda_architect`.
- Owner: `moda_database`, repository `moda-interact-database`.
- **Definition only; not materialised or claimed.** A launcher-prepared task worktree, start-of-attempt synchronisation and dependency gating are still required.

## Objective

Enable a **strictly pre-provider, auditable and atomic relinquishment** of a sequence-two `RecoveryOutreachAttempt` owned by a cancelled HUMAN template command, so a later eligible command or the existing automated follow-up can claim the *same* sequence-two row without breaking historical send-command identity or allowing a second provider send/credit.

## Context

The 2026-10-18 21:47 snapshot contains `ARCH-040-DATABASE-001` (Complete) and the following currently enforced constraints:

1. `RecoveryOutreachAttempt` is unique on `(checkoutRecoveryId, sequence)`; sequence 2 is the one shared follow-up across HUMAN and AUTOMATION.
2. `MerchantConversationSendCommand.recoveryOutreachAttemptId` is a **unique** nullable FK with `ON DELETE RESTRICT`. The command guard makes this link immutable on updates.
3. `commerce.arch040_attempt_guard` rejects changing an already non-null claim tuple (`initiatedBy`, `initiationKey`, `claimedAt`, `trigger`, etc.).
4. Shopify's ARCH-040-SHOPIFY-001 implementation candidate reserves the sequence-two row in the same database transaction that accepts a merchant template command. The accepted command is then moderated asynchronously in Background.
5. A moderation `BLOCK`/`REVIEW_REQUIRED` decision or an earlier terminal policy refusal can cancel the command *before* `providerDispatchKey` exists. The attempt remains reserved. The 1:1 unique command-to-attempt FK and immutable claim together prevent simply clearing the claim or linking a second HUMAN command.

**These are database integrity constraints, not a Background-only implementation issue.** Removing the restriction without an alternative serialization/audit rule is prohibited. The existing single-credit source is still `recovery-outreach:<attemptId>`; this task does not create a new billing ledger or second follow-up.

## Scope

- Adjust `prisma/schema.prisma` and one forward-only Prisma migration for the smallest safe claim-release representation. Keep the unique `(checkoutRecoveryId, sequence)` and a single physical sequence-two attempt; preserve the FK and accepted-command payload/idempotency immutability.
- Replace only the **incompatible** uniqueness of `MerchantConversationSendCommand.recoveryOutreachAttemptId` with a safe historical-link design (such as an indexed many-to-one relation plus an active-owner uniqueness/fencing rule). Retain historical cancelled command rows linked to the attempt for audit; never delete them to release the slot.
- Amend `commerce.arch040_attempt_guard` or provide an equivalently migration-owned guarded operation that permits a **claim-to-unclaimed** transition solely when the exact prior HUMAN owner command is durably terminal `CANCELLED`, no Meta permit/send is possible, and all database claim guards hold. Keep other claim immutability rules unchanged.
- Encode the required preconditions with database-enforced checks wherever possible: same shop/recovery/sequence-two identity; exactly current initiation key/owner; `status='PENDING'`; null `outboundMessageId` and `sentAt`; **no** `providerDispatchKey`, outbound command message, `UNKNOWN`, `DISPATCH_ADMITTED`, or `SENT` owner/receipt. Ownership history remains recoverable from immutable command rows.
- Retain the one-way provider permit and credit identity; coordinate the Background requirement to verify/release any provisional billing admission before attempting the database relinquishment.
- Add focused schema/migration validation and disposable PostgreSQL fresh/upgrade/concurrency tests, including both distinct HUMAN commands over time and HUMAN vs scheduled automation.

## Out of Scope

- No application or Background implementation, no Meta calls, no new queue, no separate follow-up attempt, no second conversation, no new credit, no changes to session/authorization/Shopify/WooCommerce UI.
- No reset after provider permit, ambiguous/`UNKNOWN` outcome, recorded outbound message, provider acknowledgement, or paid/committed outreach. The safe operation is **pre-provider only**.
- Do not delete history, temporarily disable triggers, issue unsafe foreign-key writes, remove the one-sequence-two unique key, or relax tenant/control isolation.
- Do not reopen `DATABASE-001` or change `docs/decisions/**/_index.md`.

## Requirements

1. **Database invariant:** `(checkoutRecoveryId, sequence=2)` remains unique. A released claim leaves the same row eligible for a later claim only if all normal follow-up policy conditions are independently checked by the owning Background operation. Release alone does not grant send permission.
2. **Historical identity:** cancelled commands retain their immutable `id`, `shopId`, `conversationId`, `idempotencyKey`, `payloadSha256`, `expectedControlRevision`, `recipientSnapshot`, and existing attempt link. Replays of the same idempotency key cannot silently become a new command or new delivery.
3. **Atomicity:** when a Background caller has locked Shop, Conversation, command and attempt in the canonical order, cancelling the current unadmitted command and releasing the matching sequence-two claim must commit/roll back together. Retrying an already released state is an idempotent no-op; a stale or different owner is not releasable.
4. **Recovery path:** a cancelled-but-still-claimed historical row, left by an older worker or failure, can be reconciled under the same predicates. No provider-uncertain row can be reclaimed.
5. **Concurrency:** a competing merchant claim, scheduled automation, provider admission, cancellation, and two release workers cannot manufacture duplicate ownership or two successful sends. Guard ownership with persisted current command/claim identity, not a process-local flag.
6. **Credit safety:** no relinquishment if there is evidence of provider submission/committed usage; Background owns provisional-credit release before final relinquishment. The DB migration must not imply a credit was refunded or create another source key.
7. **Compatiblity:** test the changed Prisma relationship on all consumers using the generated client; if a consumer genuinely requires a now-removed unique selector, report and coordinate a consumer correction rather than reverting the integrity fix.
8. **Release representation:** choose and document the smallest compatible approach. For example, a guarded reset of `initiatedBy`/`initiationKey`/`claimedAt` to NULL can restore an unclaimed `PENDING` attempt, while command history remains immutable. If this approach cannot be made safe under the existing trigger/index protocol, stop and return a concrete alternative to `moda_architect`; do not silently broaden this task.

## Work Items

- [ ] Inspect accepted migration `20261017120000_arch040_recovery_human_handover` and relevant Prisma relations/triggers/indexes.
- [ ] Implement the minimal Prisma/SQL change for historical command links and safe current ownership (without a second follow-up row).
- [ ] Enforce pre-provider-only release with exact former-owner and null permit/message predicates; preserve all unrelated claim and command guards.
- [ ] Prove cancelled command and release are atomic under PostgreSQL locks and roll back together on injected failures.
- [ ] Prove replays, recovery scans and two concurrent claimers cannot resurrect a cancelled send or create second ownership.
- [ ] Validate migration on a fresh database and on an existing accepted ARCH-040 schema/database with an already-reserved command.
- [ ] Record generated-Prisma consumer implications and database-side contract in the Completion Report.

## Interfaces / Contracts

- Existing `commerce.RecoveryOutreachAttempt`: `(checkoutRecoveryId, sequence=2)` remains the sole shared follow-up and source key.
- Existing `whatsapp.MerchantConversationSendCommand`: immutable command identity/payload; canonical nullable `recoveryOutreachAttemptId` still references the one attempt; historical terminal rows must remain linkable.
- Existing SQL guards: `commerce.arch040_attempt_guard`, `whatsapp.arch040_command_guard` and related trigger(s). Modify only the permitted release transition, not provider-dispatch one-way invariants.
- Consumer owner: `ARCH-040-BACKGROUND-007` (`moda_background`); any new database release contract/function must be fully documented for its task and not independently reimplemented in Shopify/API.
- No new Shared package/wire contract unless a genuine cross-repository shape change is uncovered; escalate before adding one.

## Dependencies

- `ARCH-040-DATABASE-001` (Complete in supplied snapshot).

## Enables

- `ARCH-040-BACKGROUND-007`. The latter is Pending until this task is Complete and architect-accepted.

## Acceptance Criteria

- [ ] A moderation-blocked HUMAN follow-up cancelled before provider admission can relinquish its claim without deleting the attempt or historical command.
- [ ] A different eligible HUMAN command can subsequently reference/claim **the same sequence-two row**; its new immutable command link and idempotency key are independent of the old cancelled command.
- [ ] An eligible scheduled AUTOMATION claim competes for that same row; exactly one concurrent claimant wins.
- [ ] No release is possible for an active/retryable command, a foreign shop/recovery, a stale claim, a `DISPATCH_ADMITTED`/`UNKNOWN`/`SENT` command, non-null provider permit/message, or settled credit.
- [ ] Two concurrent releases converge; retries are harmless and do not erase the newer claim (no ABA or stale-owner reset).
- [ ] All earlier DATABASE-001 invariants (unique recovery/sequence, immutable command idempotency/payload, provider permit, message correspondence and audit) remain in force.
- [ ] Fresh and upgrade PostgreSQL migrations pass with no destructive history backfill.

## Validation

- [ ] `npm run prisma:validate`
- [ ] `npm run prisma:generate`
- [ ] `npm run test:arch040-recovery-human-handover`
- [ ] New focused schema/release validator or test added under the database repository.
- [ ] New disposable PostgreSQL fresh/upgrade transition, FK and contention tests, using the repository's existing migration harness; report exact invoked commands.
- [ ] `npm run lint` (confirm declared script in `package.json`).
- [ ] `git diff --check` and documented implementation worktree/branch isolation evidence.

## Stop Condition

After Work Items, Acceptance Criteria, and required Validation pass, complete the factual Completion Report, set task to `review`, clear its claim according to the launcher workflow, return to `moda_architect`, and **STOP**. Do not implement BACKGROUND-007 or touch other repositories as part of this task.

## Implementation Notes

- This is deliberately a database prerequisite, not a reopening of already completed DATABASE-001.
- Prefer narrow constraints and durable cancelled-command history over a newly invented broad lifecycle. If the new many-to-one link requires a partial unique index for active owners, prove its interaction with NULL/outbound/permitted states explicitly.
- No manual changes to production database without an approved migration; do not confuse a failed moderation decision with provider acceptance.
- This migration must precede Background adoption and Shopify/Woo use of the release-capable flow.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The supplied 2026-10-18 snapshot is the definition baseline; the live canonical worktree and remote state require launcher verification.

### Unresolved Issues

None recorded yet; resolve any incompatibility of immutable history and permitted relinquishment before requesting acceptance.

### Architectural Concerns

The existing unique command-attempt FK and immutable claim trigger prohibit safe reuse without this migration.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation, physical task-worktree evidence, and schema/transaction tests.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Accept this task before making `ARCH-040-BACKGROUND-007` Ready.
