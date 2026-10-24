---
id: ARCH-048-BACKGROUND-001
architecture_id: ARCH-048
title: Implement Woo checkout-activity and candidate-scheduling service
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 32
executor: developer
claimed_at: 2026-10-23T23:55:19Z
attempt: 1
depends_on:
- ARCH-048-BACKGROUND-006
- ARCH-035-BACKGROUND-001
- ARCH-035-API-008
enables:
- ARCH-048-BACKGROUND-005
created: '2026-10-23'
updated: 2026-10-24
---

## Execution Ownership Amendment

On 2026-10-24, the developer explicitly invoked `/moda_developer_create ARCH-048-BACKGROUND-001` for this ready agent-owned task. Execution is transferred to the developer for the next attempt; the assigned agent remains `moda_background`, and completion is developer-controlled.

# ARCH-048-BACKGROUND-001 — Implement Woo checkout-activity and candidate-scheduling service

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Originally a portable architect proposal drafted from the 23 October 2026 snapshot; subsequently materialised and claimed for **developer execution** through `/moda_developer_create ARCH-048-BACKGROUND-001`, as recorded in the Execution Ownership Amendment and frontmatter. The developer applied two implementation patch revisions within the same task **Attempt 1**, validated them, and pushed Background implementation commit `68d20c4` to `task/ARCH-048-BACKGROUND-001` on 24 October 2026. This record submits the task for review; no architect acceptance, developer completion, merge or release is claimed. The developer reports `ARCH-046-BACKGROUND-004` already complete; do not reopen it for BG001.

## Objective

Implement an independently testable `WooCheckoutActivityService` that reconciles an authenticated Woo checkout event against the existing durable recovery and order-guard state, then schedules, reschedules or cancels a pending maturity candidate **without touching any BullMQ worker or dispatching a message**.

## Context

The current `woo-checkout-capture.worker.ts` only validates/logs events. Shopify's existing `PendingRecoveryCandidateService` is a reusable queue/index mechanism but its event adapters and maturity consumer assume Shopify. ARCH-048-BACKGROUND-006 defines the canonical Background-local `WooPendingCandidate`, cancellation/guard interfaces and typed outcomes before this service is implemented. The Woo service implements those contracts, without owning worker orchestration. Absence of a candidate job is not absence of a `CheckoutRecovery`.

## Scope

- Own `src/services/woocommerce-recovery/woo-checkout-activity.service.ts` (or equivalently named cohesive module), focused unit/integration tests, and the smallest required **candidate lifecycle/index and internal Woo candidate type** extensions. The internal candidate must carry an explicit `source: "woocommerce"`; existing jobs without a source retain their current Shopify meaning. No wire/API schema change.
- Expose an injected `handleCheckout(event: WooCheckoutCapture): Promise<WooCheckoutActivityOutcome>` service method, with typed outcomes for `scheduled`, `rescheduled`, `cancelled-empty`, `existing-recovery`, `ignored-terminal`, `ignored-stale`, `deferred-ambiguous`, and `not-eligible`. Outcomes are service results, not instructions to send WhatsApp.
- Resolve `shopId` solely from the already authenticated queue event and confirm Woo installation/platform execution eligibility. Use `(shopId, checkoutKey)` as the immutable checkout lineage; resolve shopDomain from the trusted Shop, never the untrusted event.
- Under checkout-scoped coordination, query `CheckoutRecovery` by shop and checkout key **whether or not a BullMQ candidate is present**. If a first recovery exists, reconcile permitted external activity metadata but never create a new first-generation candidate or attempt; completed/removed BullMQ job is irrelevant.
- For no existing recovery, use existing candidate scheduling/index APIs and merchant abandonment delay. Explicit `items: []` cancels; missing items (including 51+ line snapshot omission) are unknown, never interpreted as empty or admissible.
- Capture the minimum bounded **latest successfully received** Woo event evidence required at maturity (checkout currency/total, bounded items, exact contact and source event identity) in the existing approved transient Redis/BullMQ candidate facilities, with expiration covering maturity + retries/replay. Do not add a table or log customer PII.
- Dedupe stable eventId, preserve event-time watermark and immutable terminal precedence; conflicting same-second versions cannot be ordered reliably and must suspend/fail closed rather than select a preferred basket.
- Consume the `WooObservedOrderStateReader` and checkout coordination interface defined by BG006 through dependency injection. BG002 owns the concrete terminal order policy; do not implement a competing terminal state store. Use existing checkout-scoped locking; do not independently rewrite terminal guard internals.

## Out of Scope

- No worker imports, worker `process` callbacks, queue/entrypoint registration, `CheckoutRecovery` INSERT, WhatsApp/attempt/billing code or merchant notices. All worker wiring belongs to BG005.
- No new public WordPress/Moda API route, guest-session verification or Background→Woo HTTP request. No rewrite of Shopify checkout service.

## Requirements

- **Business boundary:** own scheduling + candidate evidence only. Treat injected order guard and DB repository as dependencies; never decide consent, charge or send.
- Existing first recovery wins even if a job is delayed/active/missing. No second initial recovery for the same checkout key merely because a new hook fires.
- Output candidate must be explicitly attributable to Woo without prefix guessing. A legacy Shopify candidate must retain original shape/processing.
- Lock-protected operations must not permit a delayed duplicate to resurrect a terminal checkout; unresolved ordering fails closed.
- Don’t claim Woo source-state verification if the event never reached Moda; retain event-only limitation.

## Work Items

- [x] Implement test-injected WooCheckoutActivityService and typed outcomes; add only Background-local candidate evidence/index support for later maturity.
- [x] Cover missing-job + existing MESSAGE_SENT recovery, and candidate-present + existing recovery; verify no first-send candidate is recreated.
- [x] Add unit/integration coverage for new checkout, reschedule, empty, refill, duplicates/stale events, same-second conflicts, incomplete/oversized baskets, terminal order observation, tenant isolation and concurrency.
- [x] Check legacy Shopify candidate source handling and existing index behavior in the focused candidate test suite.

## Interfaces / Contracts

**Owned capability interface (declared only in BG006; implemented by this task; not published Shared):**

```ts
interface WooCheckoutActivityHandler {
  handleCheckout(event: WooCheckoutCapture): Promise<WooCheckoutActivityOutcome>;
}
// WooCheckoutActivityOutcome is a discriminated union of named domain outcomes.
```

**Inputs:** existing strictly parsed `WooCheckoutCapture` from ARCH-035 capture job; `shopId` from trusted API queue projection, `checkoutKey` used as recovery `checkoutToken`, `eventId`, `occurredAt`, bounded checkout snapshot.

**Outputs:** scheduling/result only; a `WooPendingCandidate` carries `source: "woocommerce"`, shop+checkout identity, activity watermark, bounded evidence and timeout/retry TTL. Do not construct an abandoned-checkout URL that was not captured.

**Dependencies consumed:** existing `PendingRecoveryCandidateLifecycleService`, `PendingRecoveryCandidateIndexStore`, `CheckoutRecovery` lookup, and BG006-defined `WooObservedOrderStateReader`, `WooCheckoutCoordinator`. BG002 supplies the concrete terminal implementation only when BG005 composes the accepted services. BG001 supplies the BG006-defined `WooCandidateManager` to order reconciliation at composition. **BG005 alone imports this service into workers.**

**File-boundary rule:** This task may change Woo service module, transient candidate type/index/lifecycle helpers and its own tests, but may not redefine the BG006 contract module. It must not change `src/workers/*`, `src/entrypoints/*`, `recovery-initiation.service.ts` or order-guard policy implementation; BG002/BG003/BG004/BG005 own those.

## Dependencies

- `ARCH-048-BACKGROUND-006`
- `ARCH-035-BACKGROUND-001`
- `ARCH-035-API-008`

## Enables

- `ARCH-048-BACKGROUND-005`

## Acceptance Criteria

- [x] Existing `CheckoutRecovery` lookup, including the no-BullMQ-job/MESSAGE_SENT case, prevents creation of a second initial candidate under checkout-scoped coordination (unit and integration evidence).
- [x] Updates reschedule one delayed candidate; explicit empty baskets cancel; incomplete/oversized evidence and time conflicts fail closed (focused unit evidence).
- [x] New Woo candidates have an explicit source; the legacy Shopify candidate remains distinct and the existing index tests pass.
- [x] Business service and tests are implemented without editing the Woo capture worker; BG005 alone owns worker composition. Architect acceptance remains pending.

## Validation

- [x] Focused service/unit tests with injected dependencies and deterministic clocks: 107/107 across 9 files (24 Oct log `typescript(20261024-010948)`). Tests predate the small Attempt 2 logging type-narrowing correction; no post-correction unit rerun is shown.
- [x] PostgreSQL + Redis lifecycle integration: 1/1 passed, including removed job/MESSAGE_SENT existing recovery and competing updates (24 Oct log `typescript(20261024-012223)`).
- [x] Existing Shopify candidate unit tests included in the 107-test run; repository TypeScript recheck passed after Attempt 2; touched-file ESLint, final service ESLint, `git diff --check` and `git diff --cached --check` ran without errors (24 Oct logs).

## Stop Condition

After completing only the task's scoped service, tests, Acceptance Criteria and Validation, populate the Completion Report, set status to `review`, return control to `moda_architect`, and **STOP**. Do not wire a worker or start a dependent task. Record launcher-prepared parent and implementation dedicated worktree paths, physical isolation, synchronisation, submodule state and both task branch revisions in the Completion Report.

## Implementation Notes

All input/output types must have reasoned explicit outcomes; no boolean `success` result that hides scheduling vs suppression. Use bounded retention, and explain retention calculations in Completion Report.

- Use `/moda-task` launcher preparation and the actual task worktrees on the developer's machine; a portable ZIP is not an execution claim or Git baseline.
- Respect service/file ownership and cross-repository boundaries in this task and the parent architecture. Do not modify `docs/decisions/**/_index.md` before explicit architect session closure.
- Reuse approved shared logging and existing domain infrastructure; inspect actual repository `package.json` and perform only relevant declared checks. Record exact evidence and any impossible test rather than inventing a pass.
- All checkout/session/phone/order logging must exclude raw PII, secrets, session tokens and full basket data; record bounded reason codes and structured correlation IDs only.

## Completion Report

### Status

Ready for Review — developer-executed Attempt 1, claimed at `2026-10-23T23:55:19Z` via `/moda_developer_create` and recorded on the parent task branch. Implementation commit `68d20c4` has been pushed. Implementation patch revisions 1 and 2 are corrections within this one task attempt, not additional task claims. The task remains `execution_mode: developer`, `completion_mode: developer`, and `executor: developer` pending the configured review/reconciliation path; the developer retains explicit completion authority after a passing review. Architect Review remains Pending; no acceptance or completion is implied.

### Files Changed

Implementation repository (`moda-interact-background`, commit `68d20c4`; nine files):

- `src/services/pending-recovery-candidate/candidate-index.store.ts`
- `src/services/woocommerce-recovery/woo-activity-watermark.store.ts`
- `src/services/woocommerce-recovery/woo-candidate-queue.service.ts`
- `src/services/woocommerce-recovery/woo-checkout-activity.adapters.ts`
- `src/services/woocommerce-recovery/woo-checkout-activity.service.ts`
- `tests/unit/services/woocommerce-recovery/woo-candidate-queue.service.test.ts`
- `tests/unit/services/woocommerce-recovery/woo-checkout-activity.adapters.test.ts`
- `tests/unit/services/woocommerce-recovery/woo-checkout-activity.service.test.ts`
- `tests/integration/woo-checkout-activity.integration.test.ts`

This handoff patch updates **only this parent-workspace task definition**. No worker, entrypoint, BG006 contract, parent architecture or `docs/decisions/**/_index.md` is changed.

### Work Completed

- Implemented `WooCheckoutActivityService` with typed outcomes and explicit `source: "woocommerce"` candidate projection; used injected shop/install eligibility, existing recovery repository, observed-order guard and checkout coordinator.
- Preserved `(shopId, checkoutKey)` lineage isolation; read existing durable `CheckoutRecovery` regardless of the BullMQ job's presence or lifecycle; existing recovery cannot initiate another first-send candidate.
- Added bounded candidate snapshot capture, Redis event watermarks, stable-ID dedupe, stale and same-second-conflict deferral, empty-basket cancellation, refill/reschedule and terminal/ambiguous-order suppression.
- Extended existing candidate index only for Woo-specific retention/identity needs; preserved legacy Shopify candidate/index use. Queue/index/watermark write errors propagate for retries; the retry path can repair a previously written queue candidate after a watermark failure.
- Kept checkout maturity orchestration, worker wiring, first-recovery persistence, consent, billing, WhatsApp delivery and merchant notices outside BG001. Those remain with their owning tasks, principally BG005 for wiring.
- Produced implementation patch revision 1 and a narrow revision 2 fixing a discriminated-union `reason` logging access in `woo-checkout-activity.service.ts`; both are contained in pushed commit `68d20c4`.
- Retention: watermark/index TTL is `max(0, maturityDueAt - now) + 24 hours`, capped at 30 days; an unsafe TTL or timestamp is rejected/deferred. The retained data are transient candidate evidence and bounded event identifiers, not proof of Woo changes Moda never received.

### Validation Results

| Command / evidence | Result |
| --- | --- |
| `git apply --check --whitespace=error-all` and application of both incremental implementation patches | Pass, no reported conflicts (`typescript(20261024-010948)`, `typescript(20261024-012223)`) |
| `npm run prisma:generate` | Pass: Prisma Client 6.19.3 generated from `database/prisma/schema.prisma` (`typescript(20261024-010948)`) |
| `npx vitest run tests/unit/services/woocommerce-recovery tests/unit/services/pending-recovery-candidate.service.test.ts tests/unit/services/pending-recovery-candidate` | Pass: 9 files, 107 tests; executed before the narrow Attempt 2 logging fix (`typescript(20261024-010948)`) |
| `npx tsc --noEmit -p tsconfig.json` | Initial Attempt 1 failed TS2339 for `outcome.reason`; after Attempt 2 correction, rerun completed without errors (`typescript(20261024-012223)`) |
| `npx eslint src/services/pending-recovery-candidate/candidate-index.store.ts src/services/woocommerce-recovery/woo-*.ts tests/unit/services/woocommerce-recovery tests/integration/woo-checkout-activity.integration.test.ts` | No errors shown in initial validation log (`typescript(20261024-010948)`) |
| `npx eslint src/services/woocommerce-recovery/woo-checkout-activity.service.ts` | Pass, no errors shown in final commit log (`typescript(20261024-012516)`) |
| `npm run test:integration -- tests/integration/woo-checkout-activity.integration.test.ts` | Pass: 1 test on PostgreSQL + Redis; removed-job/MESSAGE_SENT and competing-checkout-updates (`typescript(20261024-012223)`) |
| Direct `node scripts/test-integration.mjs` invocation | Initially blocked with `spawn prisma ENOENT`; rerunning via repository npm script resolved executable lookup and passed |
| `git diff --check`, `git diff --cached --check` | Pass; run before commit (`typescript(20261024-012516)`) |
| `git commit` then `git push origin task/ARCH-048-BACKGROUND-001` | Pass: `68d20c4` pushed to `https://github.com/kodjobaah/moda-interact-background.git` (`typescript(20261024-012516)`) |

### Deviations

- The original agent-owned task was explicitly transferred to `execution_mode: developer` via `/moda_developer_create` before implementation; the durable Execution Ownership Amendment, `claimed_at`, and task Attempt 1 are preserved. The developer applied assistant-prepared code patches and performed validation/commit/push; no agent execution or additional claim is asserted. Full launcher preparation/synchronisation evidence has not been provided with these logs and remains for review.
- Earlier direct integration invocation did not expose the `prisma` binary in PATH; `npm run test:integration -- ...` was successful without code changes.

### Assumptions

- This review-handoff correction is generated against the **actual uploaded parent worktree task definition** (`moda-interact-workspace-ARCH-048-BACKGROUND-001.zip`), not the older unclaimed portable task proposal. Preserve that branch's claim and execution-mode changes.
- The integration run used the developer's configured disposable PostgreSQL and Redis test services; their connection details are not part of this handoff.
- Woo checkout source-state limitations still apply: a missing provider event cannot be verified by this service.

### Unresolved Issues

- **Partial worktree evidence:** developer terminal output confirms the dedicated parent task worktree at `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-BACKGROUND-001` on `task/ARCH-048-BACKGROUND-001`. The implementation logs show `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-BACKGROUND-001` on the same branch. The task definition itself records a developer claim timestamp. These observations do **not** independently establish the launcher preparation packet, Git common-dir identity, start-of-attempt parent/implementation synchronization, or recursive submodule revision evidence. Supply these for review where required by the isolation policy.
- **Parent review commit not yet evidenced:** apply and push this task/report change on parent workspace branch `task/ARCH-048-BACKGROUND-001`; record the resulting parent commit SHA for the reviewer. Do not invent it in this portable patch.
- **Preparation evidence:** the task frontmatter contains the developer claim (`attempt: 1`, `claimed_at: 2026-10-23T23:55:19Z`); reviewer should verify the corresponding parent claim commit, launcher-resolved worktree evidence, and start-of-attempt synchronization rather than clearing or recreating a legitimate claim.

### Architectural Concerns

- `completion_mode: developer` requires an explicit developer completion action after a passing review; preparing this handoff does not advance BG005 or mark BG001 Complete.
- This remains an event-observation-only candidate scheduler. It does not prove Woo checkout state when events never reach Moda; BG005 must keep final maturity/consent/terminal guards before any outbound action.
- No code changes should be made solely to fabricate implementation-worktree evidence; review the existing commit and, where required, rerun validation in canonical worktrees before acceptance.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
