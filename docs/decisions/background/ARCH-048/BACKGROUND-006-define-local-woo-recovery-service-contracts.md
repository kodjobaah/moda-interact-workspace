---
id: ARCH-048-BACKGROUND-006
architecture_id: ARCH-048
title: Define internal Woo recovery service contracts
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-035-BACKGROUND-001
  - ARCH-035-BACKGROUND-002
enables:
  - ARCH-048-BACKGROUND-001
  - ARCH-048-BACKGROUND-002
  - ARCH-048-BACKGROUND-003
  - ARCH-048-BACKGROUND-004
created: '2026-10-23'
updated: 2026-10-24
---

# ARCH-048-BACKGROUND-006 — Define Background-local Woo recovery service contracts

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

The **Attempt 5** definition was materialised and claimed through the developer execution workflow (`attempt: 1`). The implementation was reviewed and explicitly completed by the developer; it remains published at `b7c1b53`. The developer confirms `ARCH-046-BACKGROUND-004` is currently blocked; do not reopen or modify it as part of this task.

## Objective

Provide one canonical, type-checked, **Background-local** Woo recovery contract module so checkout scheduling (BG001), order reconciliation (BG002), row-only admission (BG003) and outreach/billing (BG004) can be implemented and reviewed **independently** against small injected interfaces, before BG005 composes them.

## Context

Attempt 3 placed BG001→BG002→BG003→BG004 in a serial implementation dependency chain despite their independent business responsibilities. At runtime they interact via candidate, terminal-state and recovery-ID boundaries, but one implementation does not need the other to be complete. Without stable interfaces, concurrent tasks may invent incompatible types or all edit the same worker/candidate helper. The current Woo input queue/event validators already exist from ARCH-035; do not redefine those wire contracts.

## Scope

- Own `src/services/woocommerce-recovery/contracts.ts` (or one equivalent **single** internal contract module) plus focused compile-time type fixtures/tests.
- Define only the identity/candidate shapes, reasoned outcome unions, and service/infrastructure interfaces listed under Interfaces / Contracts. Use type-only imports of the existing `WooCheckoutCapture` and `WooOrderCapture` parsed queue input types; no cloned versions of the API event schemas.
- Define `WooPendingCandidate` with `source: "woocommerce"`, immutable `(shopId, checkoutToken)`, latest accepted event ID/activity time, bounded basket evidence distinguishing known nonempty, known empty and unknown, and any minimal retry/candidate metadata required by the existing queue. Never invent a checkout URL or a Woo session token.
- Define `WooCandidateManager` (lookup/cancel pending candidate), `WooObservedOrderStateReader` (successfully received terminal evidence), and `WooCheckoutCoordinator` (one tenant+checkout-scoped guarded critical section). Define the four independently implementable service interfaces and typed result variants.
- Ensure the type-only module can compile with fixture/mock implementations independently of business service source files. Do not import BG001–BG005 implementations from this module.

## Out of Scope

- No worker wiring or worker/entrypoint edits, database schema changes, Redis runtime writes, candidate queue implementation, order reconciliation, consent, billing, messaging, gateway config or WooCommerce plugin edits.
- No cross-repository Shared package changes, publication, new Woo/API event fields, HTTP route or new event kind. No redesign of Shopify candidate processing.
- Do not modify completed `ARCH-046-BACKGROUND-004` or domain `_index.md` files.

## Requirements

1. Preserve the **existing** cross-service input contracts from ARCH-035. This module is entirely local to `moda-interact-background`.
2. `checkoutKey` from the authenticated Woo event is used as `checkoutToken`, always paired with trusted `shopId`; avoid phone/email matching for checkout identity.
3. Candidate `basket.kind` is exactly `nonempty`, `empty` or `unknown`: `items: []` maps to `empty`, omitted/oversized items maps to `unknown`, and conflicting same-time source versions are not treated as verified.
4. Source marker `woocommerce` is explicit; legacy unmarked candidate jobs continue through the existing Shopify path. Unknown source markers must fail closed.
5. Terminal state describes **observed** Woo events only: no observation is not a provider-confirmed unpaid/unplaced state. A placed-but-unpaid order suppresses abandoned-checkout outreach in v1, without being classified paid.
6. Guards operate at the narrow `(shopId, checkoutToken)` scope, not globally. Existing 10-second lease and 1-hour marker are not unconditional concurrency/durability guarantees; implementation tasks must prove correct fencing/retention or fail closed.
7. Return typed idempotency/denial/defer results. A service contract cannot imply a send, a bill or a new CheckoutRecovery INSERT just because a checkout event exists.
8. Outbound accepts only a **committed existing** recovery ID, never an uncommitted row or a contact-only payload.

## Work Items

- [x] Introduce the single type-only module and imports of canonical existing Woo capture event types.
- [x] Define the Woo candidate, common checkout reference, basket evidence and observed terminal-state discriminants.
- [x] Define candidate lookup/cancel, terminal read and checkout coordination dependency interfaces.
- [x] Define the four canonical named business capability interfaces and their discriminated outcomes, including BG003 `already-exists` and BG004 retry-safe enqueue/dispatch.
- [x] Add compile-time/mock conformity fixtures, prevent bidirectional imports to implementations and verify unchanged Shopify legacy routing shape at type level.

## Interfaces / Contracts

These are **canonical interface names and semantic requirements**, not permission to duplicate existing queue/event validators. The implementing agent may adjust TypeScript syntax to match repository conventions, but must preserve the interface names, method responsibilities, discriminants and identity/evidence. Material differences require architect review **before** dependent BG001–004 tasks start.

```ts
import type { WooCheckoutCapture } from "../../events/woo-checkout-capture.js";
import type { WooOrderCapture } from "../../events/woo-order-capture.js";

type WooCheckoutRef = Readonly<{ shopId: string; checkoutToken: string }>;

type WooBasketEvidence =
  | { kind: "nonempty"; checkout: WooCheckoutCapture["checkout"] & { items: [NonNullable<WooCheckoutCapture["checkout"]["items"]>[number], ...NonNullable<WooCheckoutCapture["checkout"]["items"]>[number][]] } }
  | { kind: "empty" }
  | { kind: "unknown"; reason: "items-omitted" | "conflicting-events" | "incomplete-snapshot" };

type WooPendingCandidate = WooCheckoutRef & {
  source: "woocommerce";
  lastEventId: string;
  lastActivityAt: string;
  basket: WooBasketEvidence;
};

type WooTerminalObservation =
  | { kind: "none-observed" }
  | { kind: "order-placed" | "order-paid" | "order-cancelled"; orderId: string }
  | { kind: "ambiguous"; reason: string };

interface WooCandidateManager {
  getPending(ref: WooCheckoutRef): Promise<WooPendingCandidate | null>;
  cancelPending(ref: WooCheckoutRef): Promise<"cancelled" | "absent">;
}
interface WooObservedOrderStateReader {
  read(ref: WooCheckoutRef): Promise<WooTerminalObservation>;
}
interface WooCheckoutCoordinator {
  withCheckoutLock<T>(ref: WooCheckoutRef, run: () => Promise<T>): Promise<T>;
}

type WooCheckoutActivityOutcome =
  | { kind: "scheduled" | "rescheduled"; dueAt: string }
  | { kind: "existing-recovery"; recoveryId: string }
  | { kind: "cancelled-empty" | "ignored-terminal" | "ignored-stale" | "deferred-ambiguous" | "not-eligible"; reason: string };
interface WooCheckoutActivityHandler {
  handleCheckout(event: WooCheckoutCapture): Promise<WooCheckoutActivityOutcome>;
}

type WooOrderReconciliationOutcome =
  | { kind: "placed-suppressed" | "paid-terminal" | "cancelled-terminal"; recoveryId?: string }
  | { kind: "already-terminal" | "ignored-duplicate" | "ignored-stale" | "deferred-conflict"; reason: string };
interface WooOrderReconciler {
  reconcileOrder(event: WooOrderCapture): Promise<WooOrderReconciliationOutcome>;
}

type WooAdmissionOutcome =
  | { kind: "created"; recoveryId: string }
  | { kind: "already-exists"; recoveryId: string; status: string }
  | { kind: "superseded" | "denied" | "deferred"; reason: string };
interface WooRecoveryAdmissionEvaluator {
  evaluateMatured(candidate: WooPendingCandidate, context: { jobId?: string }): Promise<WooAdmissionOutcome>;
}

type WooOutreachEnqueueOutcome =
  | { kind: "queued" | "already-initialized"; attemptId?: string }
  | { kind: "deferred" | "suppressed" | "failed-retryable"; reason: string };
type WooOutreachDispatchOutcome =
  | { kind: "sent" | "already-initialized"; attemptId: string }
  | { kind: "deferred" | "suppressed" | "failed-retryable"; reason: string };
interface WooRecoveryOutreachDispatcher {
  enqueueInitial(recoveryId: string): Promise<WooOutreachEnqueueOutcome>;
  processInitial(recoveryId: string): Promise<WooOutreachDispatchOutcome>;
}
```

**ARCH-048 naming rule:** Use capability-oriented interfaces for contracts and the `Service` suffix for concrete business implementations. Do not append `Port` to newly defined ARCH-048 interfaces. Declare an interface only when another Background capability, the orchestrator or a worker actually consumes it through dependency injection; avoid unused one-to-one class mirrors. The canonical names and ownership are:

| Capability interface | Implementing task | Concrete class/adapter | Consuming task(s) |
|---|---|---|---|
| `WooCheckoutActivityHandler` | BG001 | `WooCheckoutActivityService` | BG005 |
| `WooCandidateManager` | BG001 | Adapter over existing candidate queue/index | BG002, BG005 |
| `WooOrderReconciler` | BG002 | `WooOrderReconciliationService` | BG005 |
| `WooObservedOrderStateReader` | BG002 | Observed-order state adapter | BG001, BG003, BG004 |
| `WooCheckoutCoordinator` | BG002 | Checkout-scoped lock/fencing adapter | BG001–BG004 |
| `WooRecoveryAdmissionEvaluator` | BG003 | `WooRecoveryAdmissionService` | BG005 |
| `WooRecoveryOutreachDispatcher` | BG004 | `WooRecoveryOutreachService` | BG005 |

`WooCheckoutCoordinator` is only the checkout-scoped critical-section/fencing abstraction, not another business orchestrator. `WooObservedOrderStateReader` returns **order events that Moda has successfully received**, not live WooCommerce provider state. `WooRecoveryAdmissionEvaluator` still performs the specified idempotent first `CheckoutRecovery` INSERT when eligible; its name does not make admission read-only. All methods and result unions in the contracts above remain unchanged. BG005 may define `WooRecoveryOrchestrator` for worker-facing injection where actually consumed; its concrete implementation is `WooRecoveryOrchestratorService`.

The tuple must remain a **type-safe nonempty array** using the bounded existing Woo item fields; do not substitute `any` or infer that an event without items is an empty basket. No untrusted event payload is made authoritative merely because it matches this internal type. All events must first pass the existing Background capture parser and authenticated shop projection.

**Contract owner / implementation owner:** BG006 owns definitions; BG001 implements `WooCheckoutActivityHandler` and `WooCandidateManager`; BG002 implements `WooOrderReconciler`, `WooObservedOrderStateReader`, and supplies the approved coordination adapter; BG003 implements `WooRecoveryAdmissionEvaluator`; BG004 implements `WooRecoveryOutreachDispatcher`; BG005 injects/composes all of them.

**ARCH-046 handoff:** BG003 exposes an injectable pre-INSERT consent decision/result seam. ARCH-046-BACKGROUND-002 adds notice policy after BG003 acceptance; it does not block independent BG004 implementation. BG005 waits for both BG003 and ARCH-046-BACKGROUND-002 before wiring live jobs.

## Dependencies

- `ARCH-035-BACKGROUND-001`
- `ARCH-035-BACKGROUND-002`

## Enables

- `ARCH-048-BACKGROUND-001`
- `ARCH-048-BACKGROUND-002`
- `ARCH-048-BACKGROUND-003`
- `ARCH-048-BACKGROUND-004`

## Acceptance Criteria

- [x] The contract module compiles, is internally imported without runtime/service cycles, and defines one canonical shape and exact agreed name for every cross-BG-task interface.
- [x] A `WooPendingCandidate` cannot type-check without explicit Woo source, shop-scoped checkout identity, last-activity marker and basket evidence.
- [x] Test fakes can implement all four business interfaces and all injected candidate/terminal/coordination interfaces independently, without importing another service implementation.
- [x] `none-observed` is not represented as a proven Woo unpaid state; missing basket items are not represented as empty; duplicate/already-existing outcomes do not imply a new send or charge.
- [x] Existing Woo capture schemas and Shopify candidate data are unchanged, with no worker wiring, API change or database migration.

## Validation

- [x] Focused TypeScript typecheck/contract tests with strict fake adapter fixtures.
- [x] Source inspection confirms no import from service implementations, workers or entrypoints into the contract module.
- [x] Repository-declared lint/typecheck relevant to modified contract/test files and `git diff --check`.

## Stop Condition

After the bounded contract module, Acceptance Criteria and required Validation are complete, populate the Completion Report, set status `review`, return control to `moda_architect` and **STOP**. Do not begin BG001–004 or wire any workers. Record dedicated parent/implementation task worktrees, physical isolation, start-of-attempt synchronisation and both branch revisions as required by the repository policy.

## Implementation Notes

These are local TypeScript types, not independently deployed services or remotely addressable endpoints. A service class may implement more than one justified capability interface when appropriate.

Use the actual launch-prepared worktrees and pinned Background dependency versions. Resolve a schema/type incompatibility with the approved existing code as a contract correction for architect review, not four independent service-local adaptations. Do not modify `docs/decisions/**/_index.md` before architect session closure. No new Shared contract is required unless a later separately approved change modifies the existing cross-service Woo activity wire format.

## Completion Report

### Status

Complete — developer execution, Attempt 1 (claimed 2026-10-23T23:05:03Z; explicitly completed 2026-10-24). The Background implementation was committed and pushed as `b7c1b53` on `task/ARCH-048-BACKGROUND-006`. Two incremental implementation patch revisions belong to this single task attempt.

### Execution Ownership Amendment

On 24 October 2026, the developer explicitly invoked `/moda_developer_create ARCH-048-BACKGROUND-006` while this task still declared agent execution. The task remains assigned to `moda_background`; execution is transferred to the developer and completion remains developer-controlled for this attempt.

### Files Changed

Implementation repository (`moda-interact-background`):

- `src/services/woocommerce-recovery/contracts.ts` — canonical Background-local type-only contracts.
- `tests/typecheck/woocommerce-recovery-contracts.typecheck.ts` — positive/negative compile-time checks and independent fake service/adapters.
- `tests/typecheck/tsconfig.arch048-bg006.json` — focused, no-emit TypeScript fixture configuration.

Parent workspace: only this BG006 task-definition review handoff (after this patch is applied). No `_index.md`, architecture document or another task is changed.

### Work Completed

- Defined the seven named capability/infrastructure interfaces and their discriminated outcomes, with existing `WooCheckoutCapture` / `WooOrderCapture` type-only imports.
- Defined explicit `(shopId, checkoutToken)` identity, `woocommerce` source, last accepted event/activity, nonempty/empty/unknown basket evidence and observed-only order states.
- Typed BG001 checkout scheduling, BG002 order reconciliation, BG003 idempotent admission and BG004 retry-safe enqueue/dispatch accepting an existing recovery ID.
- Added compile-time contract assertions and independently implementable fakes, including required/optional identity, immutable checkout identity, nonempty item tuple, ambiguous/unknown observations and legacy Shopify candidate shape.
- Corrected an ESLint `no-empty-object-type` helper in the fixture with an incremental patch, leaving the contract module unchanged.
- No worker wiring, schema, billing logic, API, Woo plugin, consent/runtime guard or Shared package changes.

### Validation Results

Supplied terminal evidence: `typescript(20261023-231341)` and `typescript(20261023-231650)`. The uploaded combined archive `moda-interact-workspace-ARCH-048-BACKGROUND-006.zip` includes the three final files. Observed results:

- Initial implementation patch was applied with `git apply --check --whitespace=error-all` / `git apply --whitespace=error-all`; `git diff --check` reported no whitespace errors.
- `npx tsc --noEmit -p tests/typecheck/tsconfig.arch048-bg006.json`: no diagnostics in the latest terminal log.
- `npx tsc --noEmit -p tsconfig.json`: no diagnostics in the latest terminal log.
- `npx eslint src/services/woocommerce-recovery/contracts.ts tests/typecheck/woocommerce-recovery-contracts.typecheck.ts`: initially one fixture lint error, corrected; no diagnostics in the latest log.
- `git diff --check`: no diagnostics in the latest terminal log.
- `git commit -m "feat(ARCH-048-BACKGROUND-006): define Woo recovery service contracts"`: produced `b7c1b53`, three newly added files and 375 insertions.
- `git push origin task/ARCH-048-BACKGROUND-006`: successful new remote implementation branch push.
- The logs do not include explicit shell exit-code captures or independent CI. Worktree checkout and type-only scope were additionally inspected in the supplied combined archive; formal architectural/workflow acceptance remains pending.

### Deviations

- Initial lint failure in a test type helper was corrected by the second incremental implementation patch.
- The initial review-handoff documentation patch expected the unclaimed `agent` / `automatic` definition and failed on the actual developer-claimed parent task. This corrected handoff is rebased on the uploaded `developer` / `developer`, `in_progress`, `attempt: 1` task state.
- The implementation worktree terminal status listed an untracked local file named `typescript` (a terminal recording), which was not part of the committed files.

### Assumptions

- The ARCH-035 capture types and their runtime authenticated event parsing remain as in the supplied archive; the new contracts themselves are not trusted ingress validators.
- The parent task path observed by `pwd` and the archive helper is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-BACKGROUND-006`. The implementation task path reported by the helper and earlier validation log is `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-BACKGROUND-006`.
- The branch recorded in the task YAML is a developer claim; the uploaded logs do not independently prove all start-of-attempt launcher steps or the parent's currently checked-out branch.

### Unresolved Issues

- Start-of-attempt worktree preparation was supplied in the developer handoff; the canonical task and implementation worktrees were independently verified during reconciliation.
- The parent task worktree is on `task/ARCH-048-BACKGROUND-006`, and the task record was published at `0f94ebc7` before this completion decision.
- Runtime lease/retention proof, terminal-state fencing and live outage/provider-state semantics are downstream service/integration responsibilities, not type-only BG006 work.

### Architectural Concerns

- Outbound-only events cannot establish the state of Woo events never delivered to Moda. Keep Woo outbound disabled until the separate rollout safety gate is approved.
- The type contracts do not alone enforce authentication, consent, durable-state fencing, billing or send idempotency; owning downstream tasks must implement those guarantees.

## Architect Review

### Review Status

Pending.

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

## Developer Self-Review

### Review Status

Passed — reconciliation completed 2026-10-24.

### Evidence Reviewed

- Implementation branch `task/ARCH-048-BACKGROUND-006` is clean and published at `b7c1b53`.
- Parent task branch `task/ARCH-048-BACKGROUND-006` is clean and published at `fcf74dee0` before this review record.
- The implementation diff contains only the contract module and its two focused typecheck fixtures.
- The contract module has no imports from concrete services, workers or entrypoints.

### Validation Re-run

- `npx tsc --noEmit -p tests/typecheck/tsconfig.arch048-bg006.json` passed.
- `npx tsc --noEmit -p tsconfig.json` passed.
- `npx eslint src/services/woocommerce-recovery/contracts.ts tests/typecheck/woocommerce-recovery-contracts.typecheck.ts` passed.
- `git diff --check origin/main...HEAD` passed.

### Decision

The implementation satisfies the current ARCH-048-BACKGROUND-006 scope and acceptance criteria. The task was in `review` with a durable passing self-review; explicit developer completion is recorded below.

## Developer Completion Decision

The developer explicitly completed `ARCH-048-BACKGROUND-006` on 2026-10-24 after verifying the materialised task, durable passing review, complete work items and acceptance criteria, clean and published implementation branch `b7c1b53`, and publishable parent task record. No merge to `main` was required or performed. The accepted attempt remains `1`.
