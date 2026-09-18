# ARCH-015 background tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-015-BACKGROUND-001](BACKGROUND-001-purchase-reconciliation.md) | complete | Candidate-centric provider reconciliation is complete; durable purchase event handles drive exact provider proof without singular BillingPlan pack-meter authority. |
| [ARCH-015-BACKGROUND-002](BACKGROUND-002-cross-plan-consumption.md) | complete | Historical/non-current ACTIVE lots are consumed before current-context lots with fail-closed local context classification. |
| [ARCH-015-BACKGROUND-003](BACKGROUND-003-refund-correction-reconciliation.md) | complete | Existing billing scheduler processes durable refunds using typed RecoveryCreditRefund correction evidence, submits safe negative/fractional corrections and reconciles completion. |
| [ARCH-015-BACKGROUND-004](BACKGROUND-004-provider-meter-refund-serialization.md) | complete | Defensively serialize automatic refund preparation per provider meter and classify exact-before / expected-after / conflicting provider evidence. |

## Current architect review state

`ARCH-015-BACKGROUND-001` Attempt 4 is **Accepted — Complete**.

The normal Background purchase-reconciliation path is now independent of the retired
singular BillingPlan pack-meter configuration. Durable REQUESTED+REPORTED purchases use
their own stored event handles against the complete live Shopify provider snapshot.

`ARCH-015-BACKGROUND-002` is now Ready. `ARCH-015-BACKGROUND-003` remains Pending until
`ARCH-015-SHOPIFY-003` is Complete.


## BACKGROUND-002 Attempt 2 review

`ARCH-015-BACKGROUND-002` remains **Ready** for Attempt 3. Attempt 2 correctly added
period-aware Shared provider-context derivation and ACTIVE-only current classification,
but malformed native-App-Pricing local projection evidence can still throw from the
ordering hint instead of failing closed to historical FIFO. Attempt 3 is limited to that
fail-closed classification correction and focused regressions.

## Post SHOPIFY-003 Attempt 2 acceptance

`ARCH-015-SHOPIFY-003` is now Complete. Together with already-complete
`ARCH-015-SHARED-001`, `ARCH-015-DATABASE-001` and `ARCH-015-BACKGROUND-001`, this
satisfies every declared prerequisite of `ARCH-015-BACKGROUND-003`.

`ARCH-015-BACKGROUND-003` is therefore **Ready**.

`ARCH-015-BACKGROUND-002` remains independently Ready / in its own review workflow and
does not gate BACKGROUND-003.

## BACKGROUND-002 Attempt 3 acceptance

`ARCH-015-BACKGROUND-002` Attempt 3 is **Accepted — Complete**. The local Subscription
projection is now a fail-closed ordering hint only: valid ACTIVE contexts derive canonical
Shared provider identity (including native App Pricing with a null legacy provider id),
while malformed, ambiguous, TRIALING or otherwise unusable projections classify every
spendable ACTIVE lot as historical rather than throwing.

Historical-first FIFO, replay affinity, refund-held exclusion, Serializable/CAS behavior
and local `NOT_APPLICABLE` consumption evidence remain intact.

`ARCH-015-SYSTEM-TEST-001` remains Pending because `ARCH-015-BACKGROUND-003` and the
downstream `ARCH-015-ADMIN-001` are not yet Complete. `ARCH-015-BACKGROUND-003` remains
Ready and is the current Background implementation frontier.


## Pre-implementation correction — typed automatic-refund evidence

Code/schema audit on 2026-09-16 found that the original BACKGROUND-003 contract referenced `UsageEvent.metadata`, but the current `UsageEvent` model has no metadata field. More importantly, provider baseline/expected-after values are authoritative refund settlement evidence and must not live in an untyped JSON blob.

`ARCH-015-DATABASE-002` is therefore inserted before BACKGROUND-003. BACKGROUND-003 returns to **Pending** until DATABASE-002 is architect-accepted Complete. Its corrected contract uses typed `RecoveryCreditRefund` fields plus a unique explicit FK to the automatic correction `UsageEvent`. Existing refund plan/period/provider-context/event/refund-amount fields remain the sole provenance/economic source; no duplicates are added.


## Post DATABASE-002 Attempt 1 acceptance

`ARCH-015-DATABASE-002` is now **Complete**. Its typed refund-correction evidence schema
and unique restrictive correction-UsageEvent relation satisfy the final declared
prerequisite of `ARCH-015-BACKGROUND-003`.

`ARCH-015-BACKGROUND-003` is therefore **Ready**. It must use the integrated typed
`RecoveryCreditRefund` evidence fields and must not fall back to `UsageEvent.metadata` or
process-local settlement evidence.

The pre-existing database P3009 must be recovered before deployed migration/integration
validation, but no additional DATABASE-002 implementation attempt is required.


## BACKGROUND-003 Attempt 2 architect review

`ARCH-015-BACKGROUND-003` remains **Ready** for Attempt 3. Attempt 2 established the typed
negative/fractional correction workflow, but architect review found five bounded production
corrections still required: native App Pricing context derivation, RECONCILE state proof
without a live-pricing dependency, proportional manual-fallback refund evidence, rollback
of unlinked correction events on a lost PREPARE link CAS, and the existing
`REFUND_COMPLETED` billing system message on atomic completion.

`ARCH-015-ADMIN-001` remains Pending until BACKGROUND-003 is architect-accepted Complete.


## BACKGROUND-003 Attempt 3 acceptance

`ARCH-015-BACKGROUND-003` Attempt 3 is **Accepted — Complete**. The five bounded Attempt-2 findings are closed: native App Pricing uses Shared fallback identity, RECONCILE no longer requires live pricing, manual fallback freezes proportional economics, a lost PREPARE link CAS rolls back the unlinked correction event, and automatic completion writes the deterministic `REFUND_COMPLETED` system message atomically.

`ARCH-015-ADMIN-001` is therefore **Ready**. `ARCH-015-SYSTEM-TEST-001` remains Pending until ADMIN-001 is Complete. The pre-existing database P3009 remains an external deployed-environment prerequisite.


## Post-implementation integration audit — 2026-09-16

`ARCH-015-BACKGROUND-004` is added as a bounded correction after cross-task audit found that multiple same-handle refunds could otherwise freeze the same provider baseline and that a REPORTED correction with a third provider state remained silently REQUESTED.

BACKGROUND-004 depends formally on accepted BACKGROUND-003 only. SHOPIFY-004 and BACKGROUND-004 are coordinated but may execute concurrently: Shopify hardens merchant admission while Background independently serializes/defends provider-meter correction processing. BACKGROUND-004 is **Ready** for its bounded Attempt-2 test completion. Different event handles remain independent. No schema, queue or generic-publisher redesign is authorized. SYSTEM-TEST-001 remains Pending until both correction tasks are Complete and manual-test authorization is given.

## BACKGROUND-004 Attempt 2 acceptance

`ARCH-015-BACKGROUND-004` Attempt 2 is **Accepted — Complete**. Attempt 2 was test-only and
did not alter the accepted production service. The focused regression suite now proves
different-handle purchase independence, terminal older-refund unblocking with a fresh
provider read, explicit fractional third-state conflict handling, transactional rollback
on PREPARE link-CAS loss, linked-refund reconciliation without event recreation, and
fractional frozen-evidence immutability across retries.

`ARCH-015-SYSTEM-TEST-001` remains Pending. SHOPIFY-004 and BACKGROUND-004 are parallel
correction tasks; terminal manual/integrated testing is not auto-launched by this
acceptance and still requires every declared correction dependency to be Complete plus
explicit architect authorization.
