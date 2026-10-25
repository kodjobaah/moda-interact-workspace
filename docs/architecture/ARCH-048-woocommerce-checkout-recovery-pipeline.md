---
id: ARCH-048
title: WooCommerce outbound event-driven recovery with service-oriented Background orchestration
status: proposed
coordinator: moda_architect
created: 2026-10-23
updated: 2026-10-25
---

# ARCH-048 — WooCommerce checkout recovery, business-service orchestration

## Status

**Attempt 5: proposed capability-naming revision, not implemented or materialised.** Baseline: uploaded `moda-interact-workspace(20261023-185027).zip` and the Attempt 2 ARCH-048 review proposal. The developer separately confirms `ARCH-046-BACKGROUND-004` Complete; the snapshot has stale Blocked metadata. Verify the accepted implementation when used; **do not reopen it**. Do not update `docs/decisions/**/_index.md` until explicitly told the architecture session has concluded.

## Problem

ARCH-035 already captures Woo checkout and linked order activity and posts authenticated events to the existing Moda API, which publishes to distinct BullMQ Woo queues. The two Woo Background capture workers currently only validate/log events. Existing shared candidate and recovery infrastructure is partly Shopify-specific: `pending-recovery-candidate.worker.ts` unconditionally invokes Shopify-oriented materialisation. If Woo business rules are implemented directly in those workers, checkout scheduling, order terminal reconciliation, consent admission and billed messaging become tightly coupled, harder to test, and likely to conflict in parallel implementation work.

Woo can also send late checkout/order events after the original delayed BullMQ job has completed. The durable `CheckoutRecovery` in PostgreSQL, not a queue job's presence, determines whether first outreach already happened. The developer rejects opening a WordPress guest-checkout/session-reading endpoint and Background→API/WooCommerce state-read calls for ARCH-048.

## Goals

1. Preserve **Woo hooks → outbound authenticated Moda API → existing BullMQ queues → Background**; no new ingress or remote Woo read endpoint.
2. Establish one bounded Background-local contract module (BG006), then implement four independent business capabilities against its stable typed interfaces: checkout scheduling, order reconciliation, recovery admission and initial outreach/billing. The four service tasks do not depend on one another.
3. Use a thin Woo-specific orchestration service that delegates to those capabilities, and assign **all Background worker/entrypoint/composition edits to one final wiring task**.
4. On each relevant event, check the exact `(shopId, checkoutKey)` durable `CheckoutRecovery`, regardless of candidate/job presence. Only one initial recovery and at most one initial message/charge for the approved checkout lineage.
5. Reuse existing `Shop`, `Customer`, `CustomerPhone`, `CheckoutRecovery`, history, `RecoveryOutreachAttempt`, consent, STOP and billing records; no Moda database migration.
6. Suppress known placed/paid/cancelled order checkouts, handle empty/refilled baskets and ambiguous/duplicate/out-of-order updates safely, and preserve consent/STOP/Marketing-template enforcement.
7. Keep initial Woo sends default disabled until manual approval and terminal architecture/system tests; disable Woo follow-ups until independently reviewed.

## Non-Goals

- No new merchant WordPress remotely callable guest-session/cart/order-reading endpoint, no Woo live HTTP lookup from Background, no Background→Moda API lookup, no extra Moda API route or new WooCommerce session validation.
- No new PostgreSQL candidate/terminal table, new outbound event kind or cross-repository Shared publication by default. Local internal Background `WooPendingCandidate` source discriminator is permitted without altering existing public wire contracts.
- No automatic Shopify-equivalent verification of Woo changes that were **never successfully delivered** to Moda. This is an explicit residual safety limitation and outbound rollout decision gate.
- No separate unpaid-order reminder campaign, follow-up/reentry sending, checkout restoration feature, polling, consent wake-up or global Shopify refactor.

## Current Architecture (source-inspected)

- Woo plugin files: `includes/Checkout/CheckoutCapture.php`, `CheckoutSnapshot.php`, `CheckoutKey.php`, `OrderLifecycleCapture.php`, `CheckoutActivityPublisher.php`. Empty baskets can be omitted; order linkage uses `_moda_checkout_key`. Events use existing `CHECKOUT_UPDATED`, `ORDER_PLACED`, `ORDER_PAID`, `ORDER_CANCELLED` forms.
- API: existing authenticated `/v1/woocommerce/activity` (`moda-interact-api/src/woocommerce/activity/contract.ts`) resolves the installed shop and enqueues validated checkout/order jobs. No new API runtime work is justified merely to connect Background services.
- Background capture: `src/workers/woo-checkout-capture.worker.ts` and `woo-order-capture.worker.ts` currently log and acknowledge. `src/workers/pending-recovery-candidate.worker.ts` currently calls Shopify `checkoutRecoveryService.materializeMaturedCandidate` for every job. Existing candidate, order guard, recovery insertion/attempt, consent and credit services provide reuse points, but their Shopify-only parts must not receive Woo source jobs.
- Candidate model: `src/domain/pending-recovery-candidate.ts` currently lacks source identity and Woo bounded event evidence. The two services cannot rely on jobId existence to decide whether a durable recovery exists. Existing checkout lock duration and transient terminal marker alone are insufficient for unconditional race/retention guarantees.
- Database: existing `CheckoutRecovery` uniqueness `(shopId, checkoutToken, generation)` and status history/attempt/billing records persist after delayed jobs disappear.

## Proposed Architecture

```text
Merchant Woo checkout/order hooks
    -> Action Scheduler outbound event delivery
    -> existing authenticated Moda API /v1/woocommerce/activity
    -> existing Woo checkout / Woo order BullMQ capture queues
    -> Woo capture workers (validation and dispatch only)
           -> WooRecoveryOrchestratorService
                 |-> WooCheckoutActivityService (BG001)
                 |      -> durable recovery lookup, candidate/index/event watermark
                 |-> WooOrderReconciliationService (BG002)
                 |      -> placed/paid/cancelled fence and existing-row history
                 -> [delayed pending-recovery-candidate queue]
                          -> explicit candidate.source == "woocommerce" routing
                          -> WooRecoveryAdmissionService (BG003)
                               -> current consent + row-only first INSERT
                               -> ARCH-046 missing-consent notice seam
                          -> WooRecoveryOutreachService (BG004)
                               -> existing attempt, billing, Meta pre-send guard
    Note: BG006 owns the local interface contracts; BG005 alone wires workers and composes the four services.

Shopify or legacy candidate without a source discriminator:
    -> unchanged existing Shopify maturity/materialisation path
Unknown discriminator:
    -> fail closed; never guess based on token/domain
```

The diagram shows which service is invoked **for that event**, not that all four are called on every queue event. BG001/002 are independent business actions for checkout/order inputs. BG003/004 operate at maturity/initial-dispatch boundaries.

### Business service boundaries and worktree review ownership

| Task | Dedicated service and behavioural owner | Authorised touch points / files | Must NOT edit |
|---|---|---|---|
| `ARCH-048-BACKGROUND-006` | Background-local typed interfaces, candidate shape and outcome contracts | `src/services/woocommerce-recovery/contracts.ts`; compile-time contract fixtures/tests only | Runtime implementation, workers, billing, DB schema, remote API contracts |
| `ARCH-048-BACKGROUND-001` | `WooCheckoutActivityService` — checkout evidence/candidate scheduling, existing recovery lookup | `src/services/woocommerce-recovery/woo-checkout-activity.service.ts`; internal pending candidate type/index/lifecycle helpers; tests | Workers, entrypoints, order policy, materialisation, initial sends |
| `ARCH-048-BACKGROUND-002` | `WooOrderReconciliationService` — order terminal policy + existing recovery status/history | `src/services/woocommerce-recovery/woo-order-reconciliation.service.ts`; `checkout-order-guard.service.ts` as needed; tests | Workers, BG001 scheduler, consent, billing |
| `ARCH-048-BACKGROUND-003` | `WooRecoveryAdmissionService` — mature candidate policy and **row-only** first INSERT | `src/services/woocommerce-recovery/woo-recovery-admission.service.ts`; only genuinely neutral DB row helper; tests | Workers, Shopify-specific lookup, WhatsApp, billing |
| `ARCH-048-BACKGROUND-004` | `WooRecoveryOutreachService` — first attempt, credit reservations, final pre-send guard and compensation | `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`; Woo adapter/test modules | Workers, new billing ledger, BG001–003 business code |
| `ARCH-048-BACKGROUND-005` | `WooRecoveryOrchestratorService` — **composition, provider-aware routing and worker hookup only** | `src/services/woocommerce-recovery/woo-recovery-orchestrator.service.ts`, existing Woo capture workers, pending-recovery worker, relevant entrypoints/wiring/tests | Reimplementation or broad edits of BG001–004 business services |

BG006 is a **type-only** contract foundation and must not implement business behaviour. BG001 implements the candidate control interface, BG002 implements terminal-state and coordination interfaces, BG003 implements admission, and BG004 implements outreach. Each task may use independently mocked other interfaces. Names indicate intended owned modules; agents must inspect repository conventions and describe any bounded deviation in Completion Report. Do not build four new deployed microservices; these are injectable TypeScript services within `moda-interact-background`.

## Data Model

**No new PostgreSQL tables/migrations.** Reuse `WooCommerceInstallation`, `Shop`, `ShopSettings`, `Customer`, `CustomerPhone`, `CheckoutRecovery`, status history, outreach attempts, relevant Support notices, billing reservations and usage events. Use `checkoutKey` as `checkoutToken` **only for the authenticated shop**. Existing `(shopId,checkoutToken,generation)` uniqueness remains the row idempotency anchor; do not auto-increment generation just because the first job completed or old recovery expired.

Pre-materialisation candidate, latest received snapshot, watermark and order-first terminal evidence may use existing bounded Redis/BullMQ facilities. Candidate TTL/replay bounds must be calculated for the merchant-configured abandonment delay and retry horizon. These transient records are not permanent proof that an undelivered order/payment event did not occur. Once a recovery exists, persist received terminal transitions in its existing PostgreSQL history.

## Interfaces / Contracts

### External — unchanged

Existing plugin event kinds + schemas via authenticated Moda API and existing projected `WooCheckoutCapture` / `WooOrderCapture` Background queue data. No new public HTTP endpoint or published Shared schema. The plugin tasks add event coverage **without breaking these shapes**.

### Background-local — explicit service results

- `WooCheckoutActivityService.handleCheckout(WooCheckoutCapture)` → `scheduled | rescheduled | cancelled-empty | existing-recovery | ignored-terminal | ignored-stale | deferred-ambiguous | not-eligible`.
- `WooOrderReconciliationService.reconcileOrder(WooOrderCapture)` → `placed-suppressed | paid-terminal | cancelled-terminal | already-terminal | ignored-duplicate | ignored-stale | deferred-conflict`.
- `WooRecoveryAdmissionService.evaluateMatured(WooPendingCandidate, {jobId?})` → `created{recoveryId} | already-exists{recoveryId,status} | superseded | denied{reason} | deferred{reason}`. This service creates **only a row**. ARCH-046-BACKGROUND-002 attaches missing-consent merchant-notice behaviour here, without wiring workers.
- `WooRecoveryOutreachService.enqueueInitial(recoveryId)` / `processInitial(recoveryId)` → idempotent queued/previously-sent/blocked/send outcomes; existing delivery system retains durable attempt and usage ownership.
- `WooRecoveryOrchestratorService` injects these four services and wires queue event and maturity call sites **in BG005 only**. The orchestrator delegates rather than implementing domain rules.

**Internal candidate routing:** BG001 supplies a local `WooPendingCandidate` carrying explicit `source: "woocommerce"` and bounded latest received checkout/customer/item evidence. On maturity, BG005 routes strictly on this marker. Legacy unmarked Shopify candidate jobs continue to the existing Shopify materialisation path, including queued jobs written by the old release. Unknown values fail closed.

**Failure between row and enqueue:** A created row may persist before `enqueueInitial` succeeds. On retry, admission may return `already-exists{recoveryId,status}`; BG005 must safely recover the pending initial enqueue through BG004's idempotent attempt/outbound safeguards when eligible. It must never blindly issue a new initial send for an already-sent row. Do not solve this by introducing an unauthorised outbox table.

## Consistency, Ordering and Failure Handling

- Event delivery is at least once; no exactly-once guarantee or complete-event assumption. Stable `eventId` dedupes retry; current `occurredAt` has insufficient granularity to order same-second different updates. Conflicts must defer/quarantine rather than assume a preferred payload is latest. Truly unknown/undelivered events cannot be inferred from Redis/Postgres.
- BG001 and BG002 share **one checkout-scoped lock/fencing protocol**, but only BG002 owns order-policy changes; BG001 owns the candidate scheduling/index interface. BG001 and BG002 depend on BG006 contracts only; BG005 injects the accepted implementations. BG002 must not change BG001 candidate scheduling internals.
- Every checkout/order event that can affect a previously initiated recovery must check PostgreSQL independently of BullMQ candidate presence. Known placed/paid/cancelled outcomes suppress abandoned-cart work; `ORDER_PLACED` does not imply payment. Post-send order transition suppresses further outreach without undoing legitimately delivered charges.
- BG003 uses final row idempotency, exact customer and phone, current marketing consent, local STOP and order/watermark checks. Its row-only INSERT is never an implicit WhatsApp send. ARCH-048 BG004 owns independent initial outreach/billing; its `WooGuardedInitialSender` remains an **unimplemented injection boundary** until narrowed ARCH-046-BG004 supplies a tested final SQL consent/STOP/Marketing permit.
- Runtime wiring remains solely BG005; failed domain operations keep bounded BullMQ retry and preserve candidate indexes appropriately. Default Woo outbound disabled; no Woo follow-ups.
- A fully undelivered Woo order/payment or checkout update is an acknowledged safety limit. Before enabling Woo outbound in production, developer must explicitly accept that limitation or commission a separate outbound-only Woo-side verification mechanism. ARCH-048 does **not** silently imply Shopify-equivalent current-state lookup.

## Scalability / Observability / Security

Keep hot-path work bounded per event: parse, shop/checkout durable state lookup as needed, transient candidate update and optional terminal transition; no per-event Meta/provider calls, no Woo HTTP checkout reads, no new deployed worker processes. Reuse framework BullMQ/HTTP instrumentation where already available; use published Shared structured logger and bounded domain reason codes. Never log full baskets, phone, Woo session IDs, access tokens or credentials. Tenant guards use trusted authenticated `shopId` at every call and never infer identity from checkout key alone.

## Implementation dependency policy (Attempt 4)

**Do not encode the runtime sequence as an implementation dependency.** The four business services consume stable interfaces declared by `ARCH-048-BACKGROUND-006`; each compiled/tested independently. `ARCH-048-BACKGROUND-005` is the sole worker/composition task and depends on all four accepted services, ARCH-046-BG002 Woo notices **and** the narrowed ARCH-046-BG004 final initial-send guard. Woo plugin producer corrections are independent and gate **system testing and rollout**, not local Background service coding.

```text
 ARCH-048-BG006 (completed contracts)
      |                 |                 |                 |
      v                 v                 v                 v
 ARCH-048-BG001    ARCH-048-BG002    ARCH-048-BG003    ARCH-048-BG004
      |                 |                 |                 |
      |                 |                 v                 |
      |                 |          ARCH-046-BG002            |
      |                 |           (Woo notices)           |
      |                 |                 |                 |
      |                 +---------> ARCH-046-BG004 <--------+
      |                         (final initial-send guard)
      |                                  |
      +-------------------+--------------+
                          v
                 ARCH-048-BG005
                  (worker wiring)
                          |
                          v
                 ARCH-048-SYSTEM-TEST-001
                   ^              ^
                   |              |
                WOO-002        WOO-003
```

`ARCH-046-BG002` additionally consumes the **completed** ARCH-046-BG005 shared notifier, BG003 and current consent/STOP readers. `ARCH-046-BG004` additionally depends on the completed consent and STOP tasks. ARCH-048-BG005 requires **all** BG001–BG004 services and **both** ARCH-046 integrations to be accepted Complete.

The independent Woo plugin tasks converge only at the terminal system test, **not at BG005**. All ARCH-035 API/Woo capture prerequisites remain unchanged. The 25 October snapshot records ARCH-046-BG004 **blocked with no implementation**, so the task is now narrowed to the initial-send guard and awaits BG002 acceptance; do not treat prior conversational completion reports as implementation evidence.

### Canonical local contracts

BG006 defines **Background-internal** capability-oriented TypeScript interfaces and the discriminated `WooPendingCandidate` in one module. BG001–BG005 must import these unchanged rather than introduce parallel aliases. No new inter-repository event field, public route, Shared version or database migration is permitted by this change. Existing API-owned `woo.activity.v1` checkout/order queue payload validators continue to own the actual cross-repository wire shapes.

Cross-task contract ownership (business interfaces are named for capabilities; concrete implementations use the `Service` suffix):

| Contract / value | Contract owner | Implementation owner | Consumers |
|---|---|---|---|
| `WooPendingCandidate` / basket `nonempty \| empty \| unknown` | BG006 | BG001 populates/maintains | BG003, BG005 |
| `WooCandidateManager` | BG006 | BG001 | BG002, BG005 |
| `WooObservedOrderStateReader` | BG006 | BG002 | BG001, BG003, BG004 |
| `WooCheckoutCoordinator` | BG006 | BG002 adapts existing guard | BG001–BG004 |
| `WooCheckoutActivityHandler` | BG006 | BG001 | BG005 |
| `WooOrderReconciler` | BG006 | BG002 | BG005 |
| `WooRecoveryAdmissionEvaluator` / denial-result hook | BG006 | BG003; ARCH-046-BG002 injects notice adapter | BG005 |
| `WooRecoveryOutreachDispatcher` | BG006 | BG004 | BG005 |

Shared identity is always `(shopId, checkoutToken)`, where checkoutToken is the exact authenticated Woo checkoutKey. `none-observed` order state means **Moda has received no suppression event**, not that Woo currently has no order. Equal-time conflicting checkout evidence is ambiguous and cannot be admitted. `items: []` means known empty; missing `items` means unknown. An existing `CheckoutRecovery` is checked independently of any BullMQ job. The source discriminator is internal to Background; `source === "woocommerce"` routes to Woo, source absent preserves Shopify legacy, other sources fail closed. BG006's interfaces are frozen before parallel tasks start; any incompatible amendment returns to the architect.

## Rollout / Migration

Treat the user snapshot as a documentation baseline, not proof that code has been deployed. No database migration, new API route or new Shared publication is planned. Accept BG006 first; then BG001, BG002, BG003 and BG004 can be independently implemented/reviewed (including parallel work in dedicated task worktrees). Woo plugin WOOCOMMERCE-002 and WOOCOMMERCE-003 can proceed independently. With BG003 and the shared BG005 notifier now accepted, ARCH-046-BG002 is Ready to attach Woo merchant notices. ARCH-046-BG004 becomes Ready only after BG002 acceptance and implements the final initial-send provider fence. ARCH-048-BG005 waits for **both** ARCH-046 tasks plus the four accepted ARCH-048 business services, wires workers and preserves legacy Shopify routing. Woo producer tasks and BG005 are prerequisites of the integrated system test, not prerequisites of each other. Integrated ARCH-048-SYSTEM-TEST-001 and ARCH-046-SYSTEM-TEST-002 run only after implementation dependencies are architect-accepted, with manual developer validation before invocation if desired.

Keep Woo outbound **off** until manual approval after system tests. On rollback disable Woo scheduling/send composition or feature gate safely without deleting historical rows or accidentally rerouting queued Woo candidates into Shopify materialisation; a rollback must quarantine/hold Woo-specific candidates if the old worker cannot parse their discriminator.

## Decisions / Tasks

| Task | Repository | Proposed status | Depends on / purpose |
|---|---|---|---|
| ARCH-048-WOOCOMMERCE-001 | Woo | Superseded | Remote guest checkout reader rejected |
| ARCH-048-API-001 | API | Superseded | Hosted provider checkout reader rejected |
| ARCH-048-API-002 | API | Superseded | Background→Moda API lookup rejected |
| ARCH-048-WOOCOMMERCE-002 | Woo | Ready | Existing checkout producer; empty/refill coverage |
| ARCH-048-WOOCOMMERCE-003 | Woo | Ready | Existing order producer; paid/cancelled coverage |
| ARCH-048-BACKGROUND-006 | Background | Complete | Internal interfaces accepted |
| ARCH-048-BACKGROUND-001 | Background | Complete | Checkout scheduling service accepted |
| ARCH-048-BACKGROUND-002 | Background | Complete | Order reconciliation/terminal service accepted |
| ARCH-048-BACKGROUND-003 | Background | Complete | First-row admission and awaited denial hook accepted |
| ARCH-048-BACKGROUND-004 | Background | Complete | Initial-outreach service accepted; concrete guarded sender still required from ARCH-046-BG004 |
| ARCH-046-BACKGROUND-002 | ARCH-046 | Ready | Woo notice adapter consuming merged ARCH-046-BG005 notifier |
| ARCH-046-BACKGROUND-004 | ARCH-046 | Pending | Final initial-send permit; depends on ARCH-046-BG002 and ARCH-048-BG004 |
| ARCH-048-BACKGROUND-005 | Background | Pending | BG001–004 + ARCH-046-BG002 + ARCH-046-BG004; orchestrator/worker wiring |
| ARCH-048-SYSTEM-TEST-001 | System Test | Pending | BG005 and all relevant ARCH-048/046 implementation dependencies |

`ARCH-046-SYSTEM-TEST-002` also depends on ARCH-048-BACKGROUND-005 for integrated consent verification. **No non-system-test task depends on a system-test task.** ARCH-046-BACKGROUND-004 is not Complete in the supplied snapshot; its revised task definition is a required prerequisite to BG005. Domain `_index.md` files remain unchanged during this architecture session.

## Open Questions / Decision Gates

1. The user accepted event-driven design but has not approved the safety implication of **completely lost** payment/checkout events for live outbound marketing. System tests must expose rather than conceal this. Keep outbound off pending an explicit rollout decision.
2. Existing source-event timestamp precision cannot reliably order two conflicting versions from the same second; current approach fails closed. A future source-revision contract would require separate Shared/API/Woo work if desired.
3. No unattended Woo unpaid-order marketing or cart-resume link is authorised in this initiative.

## Change History

- 2026-10-23 — Attempt 5 renames ARCH-048 local interfaces to business-capability names without changing their method signatures, outcomes, ownership or dependency graph.

- 2026-10-23 — Attempt 1 introduced Woo checkout-reading endpoint/hosted provider reads.
- 2026-10-23 — Attempt 2 removed remote read/guest-session validation, added existing PostgreSQL recovery lookup and order event reconciliation.
- 2026-10-23 — Attempt 4 separates implementation dependencies from runtime order, defines new BG006 Background-local interfaces, makes BG001–004 independent and gates integration at BG005.
- 2026-10-23 — Attempt 3 proposed **four dedicated Woo business services + BG005 thin orchestrator/worker composition**, explicit ownership, testable interfaces, provider-aware candidate routing and crash/retry handoff; ARCH-046 integration remains in its proper ownership boundary.

- 2026-10-25 — Reconciled accepted ARCH-048 business services and merged ARCH-046 shared notifier; BG005 integration now depends on both Woo consent notice BG002 and narrowed final initial-send guard BG004. Woo follow-ups remain disabled.
