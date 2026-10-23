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
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-BACKGROUND-001
  - ARCH-035-BACKGROUND-002
enables:
  - ARCH-048-BACKGROUND-001
  - ARCH-048-BACKGROUND-002
  - ARCH-048-BACKGROUND-003
  - ARCH-048-BACKGROUND-004
created: '2026-10-23'
updated: '2026-10-23'
---

# ARCH-048-BACKGROUND-006 — Define Background-local Woo recovery service contracts

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Portable **Attempt 5 architect proposal**. Defined but not materialised; no developer branch, worktree, claim, commit or approval is asserted. Source is the user-supplied 23 October snapshot and Attempts 3–4 proposals. The developer confirms `ARCH-046-BACKGROUND-004` Complete after the snapshot; do not reopen it.

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

- [ ] Introduce the single type-only module and imports of canonical existing Woo capture event types.
- [ ] Define the Woo candidate, common checkout reference, basket evidence and observed terminal-state discriminants.
- [ ] Define candidate lookup/cancel, terminal read and checkout coordination dependency interfaces.
- [ ] Define the four canonical named business capability interfaces and their discriminated outcomes, including BG003 `already-exists` and BG004 retry-safe enqueue/dispatch.
- [ ] Add compile-time/mock conformity fixtures, prevent bidirectional imports to implementations and verify unchanged Shopify legacy routing shape at type level.

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

- [ ] The contract module compiles, is internally imported without runtime/service cycles, and defines one canonical shape and exact agreed name for every cross-BG-task interface.
- [ ] A `WooPendingCandidate` cannot type-check without explicit Woo source, shop-scoped checkout identity, last-activity marker and basket evidence.
- [ ] Test fakes can implement all four business interfaces and all injected candidate/terminal/coordination interfaces independently, without importing another service implementation.
- [ ] `none-observed` is not represented as a proven Woo unpaid state; missing basket items are not represented as empty; duplicate/already-existing outcomes do not imply a new send or charge.
- [ ] Existing Woo capture schemas and Shopify candidate data are unchanged, with no worker wiring, API change or database migration.

## Validation

- [ ] Focused TypeScript typecheck/contract tests with strict fake adapter fixtures.
- [ ] Source inspection confirms no import from service implementations, workers or entrypoints into the contract module.
- [ ] Repository-declared lint/typecheck relevant to modified contract/test files and `git diff --check`.

## Stop Condition

After the bounded contract module, Acceptance Criteria and required Validation are complete, populate the Completion Report, set status `review`, return control to `moda_architect` and **STOP**. Do not begin BG001–004 or wire any workers. Record dedicated parent/implementation task worktrees, physical isolation, start-of-attempt synchronisation and both branch revisions as required by the repository policy.

## Implementation Notes

These are local TypeScript types, not independently deployed services or remotely addressable endpoints. A service class may implement more than one justified capability interface when appropriate.

Use the actual launch-prepared worktrees and pinned Background dependency versions. Resolve a schema/type incompatibility with the approved existing code as a contract correction for architect review, not four independent service-local adaptations. Do not modify `docs/decisions/**/_index.md` before architect session closure. No new Shared contract is required unless a later separately approved change modifies the existing cross-service Woo activity wire format.

## Completion Report

### Status

Developer takeover recorded before preparation; task is materialised and ready for claim.

### Execution Ownership Amendment

On 24 October 2026, the developer explicitly invoked `/moda_developer_create ARCH-048-BACKGROUND-006` while this task still declared agent execution. The task remains assigned to `moda_background`; execution is transferred to the developer and completion remains developer-controlled for this attempt.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; repository implementation has not started.

### Deviations

None.

### Assumptions

ARCH-035 capture tasks are Complete in the uploaded snapshot. Confirm live developer state before materialisation.

### Unresolved Issues

None within type-only contract scope; runtime lease/retention proof belongs to implementing service tasks and BG005 integration.

### Architectural Concerns

Outbound-only events cannot establish the state of Woo events never delivered to Moda. Keep Woo outbound disabled until the separate rollout safety gate is approved.

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
