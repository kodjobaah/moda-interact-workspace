---
id: ARCH-040-DATABASE-006
architecture_id: ARCH-040
title: Minimal schema support for application-owned follow-up reservation release
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

# ARCH-040-DATABASE-006 — Minimal schema support for application-owned follow-up release

## Architecture

- Initiative: `ARCH-040`; parent: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`.
- Owner: `moda_database` in `moda-interact-database`.
- Definition only; no claim, branch, implementation or test completion asserted.
- **Decision: Background application code owns ALL follow-up eligibility, ownership, cancellation, release and reclamation decisions.** PostgreSQL retains only existing uniqueness, referential/data integrity, immutability and narrow irreversibility guards. Do not build a database workflow engine.

## Objective

Make the **existing single** sequence-two `RecoveryOutreachAttempt` reusable after an application-authorised, definitively pre-provider cancellation without deleting immutable command history. Supply only the schema and minimal guard relaxation necessary for `ARCH-040-BACKGROUND-007` to perform the complete decision under PostgreSQL row locks.

## Context

Inspected 2026-10-19 snapshot:

- `commerce.RecoveryOutreachAttempt` already has `@@unique([checkoutRecoveryId, sequence])` and globally unique nullable `initiationKey`.
- `whatsapp.MerchantConversationSendCommand.recoveryOutreachAttemptId` is a nullable `@unique` FK with `onDelete: Restrict`; `RecoveryOutreachAttempt.merchantSendCommand` is a singular Prisma relation. Existing cancelled historical command A therefore prevents later command B from linking to the **same** attempt.
- `commerce.arch040_attempt_guard` forbids changing a non-null claim tuple. `whatsapp.arch040_command_guard` makes command payload, idempotency, accepted attempt link, provider permit and message identity immutable.
- A producer can reserve sequence two before asynchronous moderation. `BLOCK`/`REVIEW_REQUIRED` may cancel A before any provider permit, leaving sequence two claimed. BG007 owns the repair; this DB task only removes its incompatible schema obstacles.

## Scope — exact database changes

### D1. Keep the existing recovery/sequence uniqueness without modification

Retain **unchanged**:

```prisma
@@unique([checkoutRecoveryId, sequence])
```

Keep one physical row for `(checkoutRecoveryId, sequence=2)`. Keep `RecoveryOutreachAttempt.initiationKey` unique, the existing `Conversation` identity and the canonical billing source `recovery-outreach:<attemptId>`. **Do not** add a second attempt row, source key, follow-up table, claim-state table, release token, release counter or active-owner partial unique index. The application serialises owners by locking the existing row.

### D2. Allow immutable historical commands to link to one attempt

In `moda-interact-database/prisma/schema.prisma`:

```prisma
// MerchantConversationSendCommand — keep FK nullable, immutable and RESTRICT
recoveryOutreachAttemptId String? // REMOVE @unique
recoveryOutreachAttempt   RecoveryOutreachAttempt? @relation(fields: [recoveryOutreachAttemptId], references: [id], onDelete: Restrict)
// In this model add:
@@index([recoveryOutreachAttemptId], map: "MerchantSend_outreach_attempt_idx")

// RecoveryOutreachAttempt — replace the singular opposite side:
merchantSendCommands MerchantConversationSendCommand[]
```

Names here are normative for the new relation/index; use the Prisma formatting appropriate to the existing schema. Make one migration to `DROP INDEX "whatsapp"."MerchantConversationSendCommand_recoveryOutreachAttemptId_key"` (the actual existing unique index), and create the specified ordinary non-unique index. **Preserve** the FK, target key, `onDelete: Restrict`, `@@unique([shopId, idempotencyKey])`, command `providerDispatchKey` uniqueness and all unrelated indexes/guards. Historical `CANCELLED` command A keeps its original `recoveryOutreachAttemptId` permanently; eligible command B may subsequently reference the same attempt. Changing A's link remains forbidden. Do not invent a filtered active-owner index: Background owns that check under a transaction lock.

### D3. Make only a narrow exception to the existing attempt claim-immutability guard

Update `commerce.arch040_attempt_guard` in one **new** migration, without changing the accepted `20261017120000_arch040_recovery_human_handover` migration. On `UPDATE` of an already claimed attempt, continue to reject mutation of the immutable claim tuple **except** this single **claim-to-unclaimed** transition:

```text
OLD.initiationKey != NULL
NEW.initiationKey == NULL
NEW.initiatedBy == NULL
NEW.claimedAt == NULL
OLD.status == NEW.status == PENDING
OLD.outboundMessageId == NEW.outboundMessageId == NULL
OLD.sentAt == NEW.sentAt == NULL
NEW.(id, checkoutRecoveryId, sequence, trigger, recipient,
     configuredOfferMode, fixedShopifyDiscountId, offerSnapshot)
   == OLD.(same fields)
```

Existing `updatedAt` can advance; all other unrelated guarded identity/dispatch fields remain unchanged. **Do not** reset `trigger`, `recipient`, original offer snapshot, status, follow-up due time, or credit usage; the next legitimate claim may update `trigger` using the existing unclaimed path. Reject a reset if any linked historical/current command has non-null `providerDispatchKey` or `outboundMessageId`, or a `DISPATCH_ADMITTED`, `UNKNOWN` or `SENT` state; this is an irreversibility **integrity guard**, not a decision about customer eligibility, suspension, moderation, credit or the current owner. Preserve the original guard's outbound message set-once and recovery ownership checks.

The guard must **not** decide if moderation has blocked a message, whether a lease is current, which command is the owner, whether billing is released or whether another follow-up should run. Those checks belong exclusively in BG007. A narrow SQL guard does not authorise a caller to reset a claim without the BG007 application transaction.

### D4. Application contract (document, do not implement here)

BG007 performs a single short `SERIALIZABLE`-compatible or ordinary row-lock protected PostgreSQL transaction using the established Shop → Conversation → command → sequence-two attempt lock order, with guarded `UPDATE ... WHERE initiationKey = :originalKey AND status='PENDING' AND outboundMessageId IS NULL AND sentAt IS NULL` returning the changed row. The caller verifies the current command/lease, owner and provider/billing predicates **before** this update. Claiming after release continues through the existing `RecoveryFollowUpPolicyService.claimSequenceTwo()` under the same Shop/Conversation/attempt locking discipline.

- DB schema provides no automatic release, command cancellation, moderation call, billing compensation, new scheduler or provider send.
- If an application's guarded `UPDATE` affects zero rows, it must classify stale/already-released/unsafe; it must not weaken a constraint or retry an unconditional reset.

## Out of Scope

- No new DB-owned follow-up state machine, trigger-driven business eligibility, active-claim partial unique index, stored procedure choosing a claimant or extra ownership table.
- No change to `@@unique([checkoutRecoveryId, sequence])`; no deletion or mutation of old cancelled send commands; no second billing identity; no provider calls.
- No BG007 implementation, Shopify/Woo/API logic, UI changes, separate task branches or `_index.md` updates.
- No post-permit release (`DISPATCH_ADMITTED`, `UNKNOWN`, `SENT`, provider evidence) even if later delivery definitively fails.
- No production historical backfill, upgrade-support adapters or deployment rollback program: this initiative remains in development. Do retain a normal reproducible forward schema migration.

## Requirements

1. Minimal schema changes exactly as D2/D3; preserve all other ARCH-040 DATABASE-001 integrity contracts.
2. Prisma Client supports multiple historical commands pointing to one attempt; accepted commands remain immutable, replaying their idempotency keys returns original identity at the application boundary.
3. Existing recovery/sequence uniqueness is the **sole** sequence-two duplicate-row backstop; transactional application locking, not a new partial index, owns live claimant exclusivity.
4. Narrow claim reset is permitted only pre-provider with no outbound evidence; unrelated attempt mutations remain prohibited. The fact that a reset is structurally permitted does not authorise its use outside BG007.
5. Migrations are fresh-database reproducible and must not require rewriting accepted DATABASE-001 history.

## Work Items

- [ ] Inspect actual `schema.prisma`, accepted migration/guards and dependent Prisma selectors.
- [ ] Change the command-to-attempt relation to non-unique FK + specified non-unique index; update inverse relation to list.
- [ ] Add one migration dropping only the obsolete command FK unique index, creating the ordinary index and replacing the narrow attempt guard function.
- [ ] Prove unchanged recovery/sequence unique constraint, FK, command idempotency immutability and one-way provider permit.
- [ ] Prove claim reset succeeds only for the specified pre-provider state and retains command A's link; demonstrate command B may later reference the same row.
- [ ] Prove guard rejects provider evidence, post-permit reset, illegal claim tuple modifications and cross-recovery links.
- [ ] Record any generated-Prisma consumer compile impacts without editing another repository; report a concrete dependency gap if present.

## Interfaces / Contracts

- `commerce.RecoveryOutreachAttempt`: existing unique `(checkoutRecoveryId, sequence)` and nullable unique claim identity; no extra attempt row.
- `whatsapp.MerchantConversationSendCommand`: immutable nullable indexed FK to sequence-two attempt, many historical commands per attempt; no duplicate command idempotency.
- Guard: `commerce.arch040_attempt_guard` supports only the reset above; existing `whatsapp.arch040_command_guard` remains authoritative for immutable command payload and provider permit.
- Consumer: `ARCH-040-BACKGROUND-007` owns the lock-protected release operation and all business-policy decisions. No new Shared package.

## Dependencies

- `ARCH-040-DATABASE-001` (Complete in the inspected snapshot).

## Enables

- `ARCH-040-BACKGROUND-007` after architect acceptance and database-submodule sync.

## Acceptance Criteria

- [ ] Existing unique recovery/sequence attempt and command idempotency constraints are unchanged; command FK is non-unique but indexed and immutable.
- [ ] Same attempt can retain cancelled command A's historical FK and accept later command B's separate immutable FK; no duplicate sequence-two row exists.
- [ ] SQL permits only the narrow pre-provider claim reset and preserves identity and irreversible-provider guards; no application-side eligibility workflow has moved into PostgreSQL.
- [ ] Fresh schema validates; no accepted DATABASE-001 migration is rewritten.

## Validation

Focused implementation evidence to record in the Completion Report (developer-run certification is separate from these functional acceptance criteria):

- [ ] `npm run prisma:validate` and `npm run prisma:generate` (both defined in this snapshot).
- [ ] `npm run test:arch040-recovery-human-handover` and a new focused relation/guard schema check.
- [ ] Disposable PostgreSQL test: old command A linked → terminal-before-permit context → allowed structural reset → new command B linked; no second sequence-two row.
- [ ] Negative SQL tests: provider permit, outbound message, already sent, non-pending, FK mismatch, illegal guard changes, duplicate recovery/sequence.
- [ ] `npm run lint`; `git diff --check`; canonical task-worktree preparation and sync evidence.

## Stop Condition

After work items and required implementation evidence are recorded, set status `review`, return the Completion Report to `moda_architect` and STOP. Do not begin BG007.

## Implementation Notes

No SQL-only business release API is to be exposed; the guarded transition is invoked exclusively by BG007 after its own transactional eligibility checks. If the existing Prisma relation cannot be changed without impacting a consumer, report the exact consumer/selector issue rather than quietly adding a new ownership model or altering unrelated repositories.

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

October 19, 2026 source snapshot; execution must verify the prepared canonical task worktree.

### Unresolved Issues

None recorded.

### Architectural Concerns

Any need for a second active-owner index, trigger-driven release logic or new billing structure must be escalated to `moda_architect`, not silently implemented.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

BG007 becomes eligible only after DATABASE-006 is accepted.
