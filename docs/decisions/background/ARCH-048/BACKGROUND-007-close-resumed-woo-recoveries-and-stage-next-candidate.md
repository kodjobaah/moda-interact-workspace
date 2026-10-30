---
id: ARCH-048-BACKGROUND-007
architecture_id: ARCH-048
title: Close resumed Woo recovery and stage a generation-aware candidate
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 28
executor: codex
claimed_at: 2026-10-30T06:58:03Z
attempt: 1
depends_on:
  - ARCH-048-BACKGROUND-005
enables:
  - ARCH-048-BACKGROUND-008
  - ARCH-048-BACKGROUND-009
  - ARCH-048-BACKGROUND-010
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-048-BACKGROUND-007 — Close resumed Woo recovery and stage a generation-aware candidate

## Architecture

Architecture ID: `ARCH-048`.

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md` (2026-10-29 recovery-generation amendment).

Coordinator: `moda_architect`. **Defined but not materialised**: this portable source-snapshot task has no launcher worktree, parent/implementation task branch, commit or push. Only `/moda-task ARCH-048-BACKGROUND-007` may claim/execute it after canonical materialisation.

## Objective

On a demonstrably new Woo checkout update, atomically close the currently active abandonment episode and stage or refresh the **next generation's** inactivity candidate, while making duplicates, crash replay and old candidate cleanup safe.

## Context

The accepted `WooCheckoutActivityService.evaluate()` currently calls `findExisting()` and returns `existing-recovery` after updating only `lastExternalActivityAt`; it never creates a second episode. `WooExistingRecoveryRepository.findExisting()` sorts generation **ascending**. `wooCandidateJobId(ref)` and Redis index/watermark are checkout-only; an old maturity job can collide with or delete a successor. `CheckoutRecovery` already has `generation`, `@@unique([shopId,checkoutToken,generation])`, status history and per-recovery attempts. Do not mutate a closed recovery's `lineItems`, `totalPrice` or `currency` to represent the new basket.

## Scope

**Permitted implementation paths in `moda-interact-background/`:**

- `src/services/woocommerce-recovery/contracts.ts` — **owner of the additive/staged v2 local contracts**, whose mandatory compile-time tightening is explicitly delegated to BG011 after BG008/BG009 are accepted.
- `src/services/woocommerce-recovery/woo-checkout-activity.service.ts` and `woo-checkout-activity.adapters.ts` — event comparison, newest-recovery lookup, atomic closure and replay repair.
- `src/services/woocommerce-recovery/woo-candidate-queue.service.ts` and `woo-activity-watermark.store.ts` — generation-scoped candidate identity, index ownership and watermark semantics.
- `src/services/pending-recovery-candidate/candidate-index.store.ts` — only a narrow additive **compare-and-delete-if-owned** API if required; do not alter existing Shopify methods/semantics.
- Corresponding focused tests under `tests/unit/services/woocommerce-recovery/`, `tests/integration/woo-checkout-activity.integration.test.ts` and candidate/Redis tests. Create named focused tests where absent.

**Do not edit** admission, outreach, order reconciliation, inbound routing, orchestrator, workers, entrypoints, public API/Shared schemas, WordPress plugin, Prisma schema, billing or other task documents.

## Out of Scope

- No new `CheckoutRecovery` INSERT, Meta send, billing charge/refund or conversation creation; these belong to BG008/BG009.
- No API/WordPress event revision, new checkout read endpoint, polling or remote Woo read.
- No cross-generation cooldown, lifetime send cap or attempt reuse.
- No production activation or Woo follow-up enablement.

## Requirements

1. **Canonical identity and ordering.** Use authenticated `(shopId, checkoutToken)`; find the **latest** recovery by `generation DESC, id DESC`, select `id`, `generation`, `status`, `lastExternalActivityAt` and the required terminal/admission history. Never use the first/oldest row or a removed BullMQ job as authority. Evaluate only `CHECKOUT_UPDATED` events that have passed the existing capture parser. Compare the trusted `occurredAt`, `eventId` and accepted fingerprint with the durable recovery boundary and Redis watermark. A same-event replay is **not** checkout resumption; older versions and unorderable same-second conflicts cannot start a generation or authorize outreach.
2. **When no prior recovery exists:** retain BG001's current full-basket, duplicate, empty/unknown, eligibility and delay policy and schedule `generation=1`.
3. **When latest generation is active** (`DETECTED`, `MESSAGE_SENT` or `ENGAGED`) **and a strictly newer qualified activity event arrives:** in a PostgreSQL transaction, lock/fence exactly that latest recovery; change it to `CANCELLED`, advance its `lastExternalActivityAt` monotonically and insert exactly one `CheckoutRecoveryStatusHistory` row with `source="woocommerce.checkout"`, `reason="CHECKOUT_RESUMED"` and bounded metadata `{eventId, nextGeneration}`. Preserve the original basket, conversation, sends, confirmed usage and history. Use an update CAS/row lock; a failed CAS triggers retry/re-read, never a second closure. **Do not cancel/release a possibly provider-admitted attempt here:** BG009 owns provider-aware settlement after closure, and the existing final SQL permit must reject `CANCELLED`.
4. **When latest is already closed:** replay of its recorded `CHECKOUT_RESUMED` event repairs the **same** next-generation candidate and returns the previous recovery ID for BG011's cleanup; it never increments again. Later qualified updates to that pending generation replace its basket and reset the timer. A non-order `EXPIRED` row may start `generation+1` only after newer evidence and order guards; `COMPLETED` or `CANCELLED` for an order/unknown terminal reason is never re-opened. Do not assume all `CANCELLED` rows mean resumption; check history reason/source. If terminal evidence is ambiguous, defer safely.
5. **Candidate and watermark contracts (additive until BG011):** **Every newly produced** `WooPendingCandidate` and `WooActivityWatermark` must contain a positive safe-integer `generation`, including generation 1. While existing admissions, worker callsites and tests remain v1, represent these fields as **optional at the type boundary only** (`generation?: number`) to preserve intermediate compilation; BG011 must make them mandatory and reject absent generation at all Woo worker entrypoints. Runtime code written by BG007 must validate its own produced generation and refuse a missing generation for successor G2. `WooCandidateManager.getPending(ref, expectedGeneration?)` and `cancelPending(ref, expectedGeneration?)` must not return/delete a different generation. Define `wooCandidateJobId(ref, generation = 1)` **temporarily** so existing one-argument worker callsites compile and generation-1 jobs use the same new deterministic algorithm; the digest must include the validated generation for **every** new Woo job. BG011 removes the default and passes generation explicitly. Its single checkout index identifies the current generation, never an older job. All comparisons must include shop ID, checkout key and event identity/digest. BG008 updates `sameAcceptedCandidate()`; do not change admission from this task.
6. **Atomic Redis index ownership:** stale maturity cleanup, cancellation and retry must never remove a successor's index, including if a Redis checkout lease expires. Implement a checkout-index **compare-and-delete** where the stored job ID is checked atomically before deletion; preserve Shopify's existing index API. Never blindly call `index.remove()` in a Woo code path when index ownership can have changed. The BG011 `clearMatured` wiring will consume this API.
7. **Candidate transitions:** for `nonempty`, schedule/reschedule the new generation from the last accepted checkout activity; for explicit `items: []`, cancel the pending candidate and do not admit until refill; for missing/oversized/conflicting basket, cancel unsafe candidate and defer until adequate new evidence. Do not borrow the previous generation's frozen items. Preserve the existing safe-time horizon and fail-closed rules; source timestamps do not establish order for distinct events within the same source second.
8. **Crash/replay:** the SQL closure and history commit **precede** Redis candidate publication, outside the SQL transaction. If scheduling/index/watermark fails, throw so BullMQ retries; replay must inspect the committed resumption evidence and repair generation `N+1` without adding history or incrementing twice. Never acknowledge a half-complete state as success. Retention/Redis loss must not cause a stale event to close a recovery again; use the durable latest row/history as the lower ordering boundary.
9. **Define staged local v2 discriminated outcomes without breaking unmodified consumers:** `WooCheckoutActivityOutcome` adds `resumed { previousRecoveryId, nextGeneration, candidateOutcome: "scheduled" | "rescheduled" | "cancelled-empty" | "deferred-ambiguous", dueAt? }` and `repair-existing-initial { recoveryId, generation }`; the activity service must provide `generation` on all newly produced `scheduled/rescheduled` results. `resumed` is also returned when replay repairs a prior closure. Until BG008/BG009 are implemented, `WooAdmissionOutcome` gains **type-optional** `generation?: number` on `created`/`already-exists` and `repairInitial?: boolean` on `already-exists`, and `WooRecoveryOutreachDispatcher` gains **type-optional** `settleResumed?(previousRecoveryId: string): Promise<void>`. These optional types are a **non-deployed, inter-task compilation bridge**, not acceptable final runtime contracts. BG008 must always actually return `generation` and `repairInitial` for those variants; BG009 must implement `settleResumed`; BG011 must make all three fields/methods and candidate/watermark generation **required**, remove the job-ID default and update remaining callsites/fakes. No service may interpret an absent `repairInitial` as true or call an optional missing settlement method. This is Background-local only: no new Shared event or wire compatibility adapter.
10. **Retry of the admission-origin event:** `repair-existing-initial` is permitted only if this exact event can be matched to the durable **admission** origin (`lastEventId` in admission status-history metadata supplied by BG008), the recovery is still `DETECTED`, and it has not been resumed/terminalized. Never use timestamp equality alone as proof. If old pre-amendment rows have no origin event ID, fail closed rather than treating an ambiguous replay as resumption or re-enqueue. BG011 owns the guarded enqueue on this outcome.
11. All runtime exceptions use `@modainteract/moda-interact-shared/logging` with bounded shop/recovery/generation/event-hash/stage/reason fields, log and rethrow; no silent swallow or raw phone, email, basket, checkout token, access token or provider payload in logs.

## Work Items

- [x] Implement additive staged `contracts.ts` v2 types/outcomes, including optional BG008/BG009 fields and the BG011 tightening handoff.
- [x] Replace oldest-row lookup with latest-row + durable status/admission/resumption history and safe event comparisons.
- [x] Implement idempotent SQL recovery closure with `CHECKOUT_RESUMED` history; Redis publication runs only after the transaction.
- [x] Implement generation-specific delayed candidate/job IDs, watermark generation, checkout-index ownership and conditional cleanup.
- [x] Implement replay-safe pending-generation update, empty/unknown handling and explicit outcomes.
- [x] Add focused unit, Redis and PostgreSQL coverage for transitions, ownership races and SQL-commit/Redis-publication replay.

## Interfaces / Contracts

- **Existing inbound (unchanged):** parsed `WooCheckoutCapture` (`events/woo-checkout-capture.ts`), authenticated `shopId`, `checkoutKey`, `eventId`, `occurredAt`, `checkout.items`.
- **Canonical internal v2 producer (staged):** `src/services/woocommerce-recovery/contracts.ts` exports optional **compile-bridge** `WooPendingCandidate.generation?`, `WooAdmissionOutcome.generation?/repairInitial?`, `WooRecoveryOutreachDispatcher.settleResumed?` plus new `WooCheckoutActivityOutcome` and manager signatures; **all BG007-produced candidates/watermarks/outcomes carry valid generation at runtime**. BG008/BG009 implement their optional contract members fully; BG011 is the **only** owner of final required-field tightening and remaining compile-site updates. No task invents an alternative contract.
- **DB:** `CheckoutRecovery(shopId,checkoutToken,generation,status,lastExternalActivityAt)` and `CheckoutRecoveryStatusHistory(source,reason,metadata,occurredAt)`; no migration.
- **Redis:** generation-aware Woo candidate job IDs, checkout index with compare-and-delete ownership, monotonic activity watermark; no Shopify job format change.
- **Cross-service:** no Shared/API/Woo event changes.

## Dependencies

- `ARCH-048-BACKGROUND-005` — Complete in the supplied snapshot. Must be materialised/merged into the developer's canonical task base before executing.

## Enables

- `ARCH-048-BACKGROUND-008` — generation-aware admission.
- `ARCH-048-BACKGROUND-009` — provider-aware old-generation settlement.
- `ARCH-048-BACKGROUND-010` — conversation routing for multiple generations.

## Acceptance Criteria

- [x] A valid checkout edit after a DETECTED/MESSAGE_SENT/ENGAGED recovery closes only the latest generation and records one `CHECKOUT_RESUMED` history entry with event ID.
- [x] Prior recovery basket, conversation, confirmed send, usage and history remain unchanged; closure only changes status and monotonic activity time.
- [x] Further edits during the next inactivity window update the same next-generation candidate.
- [x] Replay after SQL commit and before Redis scheduling restores the same next-generation candidate without duplicate closure/history.
- [x] Generation-specific jobs and compare-and-delete index ownership prevent prior-generation cleanup from removing the successor pointer.
- [x] Duplicate, stale, equal-second conflict, empty/unknown basket, observed order and Redis/DB failure paths are classified safely and errors propagate.
- [x] Watermarks include bounded-retention generation; durable recovery timestamps/history remain the ordering boundary after Redis loss.
- [x] `npm run build` succeeds with staged admission/outreach/worker consumers unmodified; incomplete branches remain non-deployable.
- [x] Shopify candidate routing/index methods and semantics were not changed; failure paths use the shared logger and rethrow.

## Validation

- [x] `npx vitest run tests/unit/services/woocommerce-recovery/woo-checkout-activity.service.test.ts tests/unit/services/woocommerce-recovery/woo-checkout-activity.adapters.test.ts tests/unit/services/woocommerce-recovery/woo-candidate-queue.service.test.ts` — passed, 3 files / 33 tests.
- [x] `node scripts/test-integration.mjs tests/integration/woo-checkout-activity.integration.test.ts` — passed, 1 PostgreSQL/Redis test including SQL-close then Redis-publication failure and same-generation replay repair.
- [x] `npm run build` — passed after generating the locked Prisma client.
- [x] `npm run lint` — passed.
- [x] `git diff --check` — passed; final inspection confirmed only permitted implementation files and the assigned task file changed.

## Stop Condition

After this bounded service/contract work, tests and Completion Report, set task `status: review`, return to `moda_architect` and **STOP**. Do not begin BG008–BG011, repair their code, or update another task/architecture/index.

## Implementation Notes

Use the launcher-resolved **dedicated parent and implementation worktrees** and record paths/revisions, preparation packet and synchronization evidence. The code above is a canonical task **specification**, not an instruction to create a parallel logger or independent microservice. Do not silently weaken invariants to make tests pass. Inspect actual script names before invoking them. The Woo candidate v2 format is an **internal breaking** pre-live change: release coordination must explicitly drain/replace obsolete test Woo candidate jobs while preserving real PostgreSQL state; keep live Woo outbound default-off. The task must not modify `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, or other task files.

## Completion Report

### Status

Implementation complete; branch publication blocked pending authorization of the remote destination.

### Files Changed

- `src/services/woocommerce-recovery/contracts.ts`
- `src/services/woocommerce-recovery/woo-checkout-activity.service.ts`
- `src/services/woocommerce-recovery/woo-checkout-activity.adapters.ts`
- `src/services/woocommerce-recovery/woo-candidate-queue.service.ts`
- `src/services/woocommerce-recovery/woo-activity-watermark.store.ts`
- `src/services/pending-recovery-candidate/candidate-index.store.ts`
- Focused Woo checkout activity and candidate queue tests under `tests/unit/services/woocommerce-recovery/`
- `tests/integration/woo-checkout-activity.integration.test.ts`

### Work Completed

- Recovery lookup selects the latest generation and reads bounded DETECTED/admission and `CHECKOUT_RESUMED` history evidence.
- Newer activity closes only an active latest recovery with an atomic status compare-and-set and one resumption history row in a PostgreSQL transaction. Basket, conversation, attempts and billing history are untouched.
- The service stages generation 1 or the same next generation, handles exact resumption replay, empty/unknown snapshots, same-second conflicts, and admission-origin replay as a separate staged outcome.
- New Woo candidates and watermarks carry validated generation. Job IDs include generation; get/cancel operations can be generation-scoped.
- Added Redis compare-and-delete checkout-index ownership while preserving the existing Shopify index API.
- Activity-service runtime failures are logged with bounded tenant/event-hash/stage/error-class fields and rethrown.

### Validation Results

- Focused Woo unit suite: 33 tests passed.
- PostgreSQL/Redis crash-replay integration: 1 test passed.
- `npm run build`: passed.
- `npm run lint`: passed.
- `git diff --check`: passed.
- Launcher packet supplied dedicated worktrees and synchronized task branches: parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-BACKGROUND-007` at prepared head `961ec7b2aa172ce86e7c0cf014f561b8ff7ff3b1`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-BACKGROUND-007` at prepared head `667d0ec219c72e8ed7e8aeedfa668695f9cdcf04`; `database` submodule at `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`. Implementation commit `f1f61f3` is on local `task/ARCH-048-BACKGROUND-007`; push to `https://github.com/kodjobaah/moda-interact-background.git` was rejected by auto-review because destination trust and exact publication authorization were not established. No retry was attempted.

### Deviations

None. No schema, queue payload outside the Background-local staged contracts, admission/outreach implementation, worker wiring, or other repository was changed.

### Assumptions

- Woo event timestamps remain source-second precision; distinct same-second snapshots are treated as unorderable.
- Admission-origin replay becomes actionable only after BG008 stores `lastEventId` in DETECTED status-history metadata. This task does not enqueue admission repair.
- BG009 supplies the optional resumed-attempt settlement method, and BG011 owns final required-field tightening and worker wiring.

### Unresolved Issues

Implementation branch push is blocked by the auto-review decision described under Validation Results. The staged BG008/BG009/BG011 contract handoffs above remain prerequisites before integration/deployment.

### Architectural Concerns

Woo events remain event-delivered evidence only; updates never received by Moda cannot establish checkout resumption. Woo sending remains default-off pending integrated system testing and explicit live-send approval.

### Git / VCS

- Task branch: `task/ARCH-048-BACKGROUND-007` in both repositories.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-BACKGROUND-007`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-BACKGROUND-007`.
- Shared workspace and shared implementation checkouts were not switched or used for task implementation; no other task worktree was reused.
- Start-of-attempt synchronization and claim were completed by the launcher; the supplied branch heads and database submodule commit are listed above.
- Implementation commit: `f1f61f3` on local `task/ARCH-048-BACKGROUND-007`; origin push: blocked by auto-review, not pushed.
- Parent task report commit: `3a0f4a7687f8321d00abaffb750c995255e78d2a` on local `task/ARCH-048-BACKGROUND-007`; push not attempted while implementation publication is blocked. Submodule gitlink was not staged. Neither task branch was merged to main.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
