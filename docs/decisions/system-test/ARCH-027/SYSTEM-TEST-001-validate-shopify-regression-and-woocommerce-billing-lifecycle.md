---
id: ARCH-027-SYSTEM-TEST-001
architecture_id: ARCH-027
title: Validate Shopify regression and WooCommerce billing lifecycle with local integration
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: manual
status: pending
priority: 110
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-DATABASE-001
  - ARCH-027-API-001
  - ARCH-027-API-002
  - ARCH-027-API-003
  - ARCH-027-API-004
  - ARCH-027-API-005
  - ARCH-027-API-006
  - ARCH-027-BACKGROUND-001
  - ARCH-027-BACKGROUND-002
  - ARCH-027-BACKGROUND-004
  - ARCH-027-BACKGROUND-005
  - ARCH-027-WOOCOMMERCE-001
  - ARCH-027-WOOCOMMERCE-002
  - ARCH-027-WOOCOMMERCE-003
  - ARCH-027-ADMIN-001
  - ARCH-027-GATEWAY-001
  - ARCH-027-SHOPIFY-001
enables:
  - ARCH-027-SYSTEM-TEST-002
created: 2026-10-04
updated: 2026-10-04
---

# Validate Shopify regression and WooCommerce billing lifecycle with local integration

## Terminal / Manual Gate

This is a **terminal system-test task**.

Do **not** auto-start it merely because its task file exists.

It may start only when:

1. every dependency above is architect-accepted `complete`;
2. the corresponding implementation commits are merged into the coordinated test baseline;
3. all required nested database submodules are synchronized to the accepted ARCH-027 database commit;
4. `moda_architect` / the developer explicitly authorizes terminal integrated testing.

This task enables no implementation work.

If integrated validation exposes an implementation defect:

```text
record the failing evidence
identify the owning implementation task/repository
return to moda_architect
STOP
```

Do not compensate by adding system-test-only business behavior or weakening an accepted assertion.

## Objective

Prove that the accepted ARCH-027 implementation composes correctly across:

```text
moda-interact-database
moda-interact-api
moda-interact-background
moda-interact-woocommerce
moda-interact-admin
moda-interact-gateway
moda-interact
```

without requiring real Woo provider credentials.

The task has two equally important outcomes:

```text
A. Woo local/mock lifecycle validation
B. Shopify regression / provider-isolation validation
```

The local Woo system harness may emulate **provider evidence delivery**, but it MUST NOT change production configuration merely to redirect the API's real Woo command client to a fake provider.

ARCH-027 intentionally hard-codes bounded Woo sandbox/production provider origins in API application code.

Therefore this task validates provider-command creation in the owning API repository's accepted integration tests and validates the cross-service lifecycle from the **accepted durable command boundary** onward by seeding only the durable records that API-003/API-004 are specified to commit before provider confirmation.

It then drives the real accepted:

```text
API-005 signed webhook ingress
    -> WooCommerceBillingWebhookReceipt
    -> Background billing worker
    -> durable Subscription/period/purchase/refund state
    -> API-002/API-006 reads
```

against disposable infrastructure.

Real Woo command/provider behavior remains SYSTEM-TEST-002 sandbox certification.

## Existing System-Test Infrastructure To Reuse

The supplied system-test repository already provides:

```text
npm test
npm run typecheck
npm run lint

ephemeral PostgreSQL fixture
ephemeral Redis fixture
Background worker Compose support
Render/Gateway topology validation helpers
```

ARCH-027 should extend those capabilities rather than creating a second test repository or harness framework.

The current platform database may require pgvector-enabled PostgreSQL migrations. For ARCH-027 database-backed integration, use the accepted project test image:

```text
pgvector/pgvector:pg17
```

rather than silently falling back to developer PostgreSQL or Render databases.

No ARCH-027 system test may use a production/shared merchant database.

## Scope

Modify only `moda-interact-system-test` implementation/tests/scripts/evidence documentation required for deterministic ARCH-027 integrated validation.

Expected additions conceptually:

```text
src/
  arch027/
    woo-webhook-fixture.js
    billing-db-fixture.js
    process-harness.js
    evidence.js

test/
  arch027-woo-billing-lifecycle.test.js
  arch027-shopify-regression.test.js
  arch027-security-idempotency.test.js

scripts/
  run-arch027-integrated-billing.js

docs/evidence/ARCH-027/
  SYSTEM-TEST-001-integrated-evidence.json
```

Exact filenames may differ if accepted repository structure suggests a smaller reuse.

No production repository source code is modified by this task.

## Out of Scope

- Real Woo sandbox subscription creation.
- Real Woo sandbox one-time charges.
- Real Woo vendor-dashboard refund actions.
- Real provider tax/proration behavior.
- Real provider response-loss recovery.
- Determining whether Woo supports arbitrary partial refunds.
- Production deployment.
- Production DNS/credentials.
- Modifying application behavior to satisfy tests.
- Browser visual redesign.
- Performance/capacity claims.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Pin the implementation baseline in evidence

Before scenarios run, record bounded provenance for every required repository:

```text
repository name
HEAD SHA
clean/dirty state
expected ARCH-027 task implementation SHA when available
database submodule SHA where applicable
```

Fail if a required implementation worktree is dirty unless the developer explicitly supplies a clean packaged baseline intended for the system test.

Do not record credentials or remote URLs containing secrets.

### R2 — Disposable PostgreSQL only

Run database-backed ARCH-027 scenarios against a newly created disposable PostgreSQL instance.

Use:

```text
pgvector/pgvector:pg17
```

or the exact architect-accepted pgvector PostgreSQL image if the accepted database task changed it.

Requirements:

```text
dynamic host port
unique database/user/password
no fallback to localhost developer DB
no Render/shared DB
cleanup in finally
```

Apply the accepted canonical database migrations before test state is created.

### R3 — Prove fresh and upgrade migration compatibility

The system task must capture:

#### Fresh

```text
empty disposable database
-> accepted migrations
-> successful ARCH-027 schema
```

#### Shopify upgrade fixture

Seed a bounded pre-ARCH-027-compatible Shopify billing fixture using the accepted migration rehearsal mechanism, then migrate and prove:

```text
existing RecoveryCreditPurchase.provider = SHOPIFY
existing RecoveryCreditRefund.provider = SHOPIFY
existing Shopify required evidence remains non-null
existing Shopify included counter currentAllowanceQuantity = NULL
```

Do not hand-edit post-migration rows to make the assertions pass.

### R4 — No real Woo provider dependency

SYSTEM-TEST-001 must succeed with:

```text
no real WOO_BILLING_API_KEY
no real WOO_BILLING_API_SECRET
no network access to sandbox.woocommerce.com required
no network access to woocommerce.com required
```

Use synthetic deterministic secrets only for:

```text
API-005 webhook HMAC
local test installation authentication
```

Do not claim real provider compatibility from this task.

### R5 — Do not add a test-only Woo provider base URL

Do not modify API production code/configuration to add:

```text
WOO_BILLING_BASE_URL
WOO_BILLING_EMULATOR_URL
```

or equivalent solely for SYSTEM-TEST-001.

API-003/API-004 outbound provider request correctness is evidence from their accepted repository integration tests.

Cross-service scenarios that need a provider-created contract begin from the architecture-approved durable command boundary:

```text
WooCommerceBillingOperation
RecoveryCreditPurchase where applicable
already-materialised BillingPlan where required
```

The fixture may create only those **pre-provider-confirmation** records.

It MUST NOT seed the business postconditions that Background is supposed to prove, such as:

```text
paid Subscription activation
plan switch result
purchase ACTIVE
refund COMPLETED
period rollover result
```

### R6 — Signed Woo webhook fixture

Add a deterministic Woo billing webhook fixture that can build provider-shaped:

```text
subscription
charge
```

payloads and send them to the accepted API-005 ingress with:

```text
X-WC-Webhook-Topic
X-WC-Webhook-Signature
Content-Type: application/json
```

Signature must be:

```text
Base64(HMAC-SHA256(secret, exact raw bytes))
```

The fixture must support:

```text
exact duplicate delivery
byte-distinct equivalent JSON
invalid signature
selected lifecycle topic/status
selected provider contract ID
selected charge transaction/refunded amount evidence
```

No customer/payment personal data is needed.

### R7 — Use the real API-005 durable ingress

Cross-service lifecycle scenarios must use the real accepted API process/route for provider evidence.

Do not directly insert `WooCommerceBillingWebhookReceipt` for the primary positive scenarios.

A direct receipt insert may be used only for a narrowly documented database failure/race fixture where the API route itself is not the behavior under test.

### R8 — Run the real Background billing cycle

The test must execute the accepted Background billing worker/reconciliation cycle containing:

```text
BACKGROUND-002 recurring receipts / provider-driven period renewal
BACKGROUND-004 charge acquisition
BACKGROUND-005 refund preparation/reconciliation
```

against the same disposable PostgreSQL database used by the API.

Do not reimplement those transitions inside the system-test repository.

The harness may start the accepted billing-worker entrypoint/process or invoke the accepted production reconciliation composition boundary when the repository explicitly exposes one for integration testing.

### R9 — First Woo connection and local Free activation

Using ARCH-026's accepted local-development connection proof fixture, prove:

```text
first verified Woo connection
    -> exactly one Woo Shop
    -> exactly one WooCommerceInstallation
    -> Shop.onboardingCompleted = true
    -> existing unique Subscription is ACTIVE Free
    -> providerSubscriptionId = NULL
    -> billingPeriodId = NULL
    -> lifetime Free grant created exactly once
```

Then reconnect/rotate the installation credential and prove:

```text
same Shop
same Subscription
same lifetime Free grant
no balance reset
```

Use the accepted connect endpoint and challenge proof rather than directly manufacturing the final connected/Free state.

### R10 — Authenticated Free billing read

With the real installation credential from R9, call:

```text
GET /v1/billing
GET /v1/billing/plans
```

and prove:

```text
current plan = Free
no recurring provider contract is required
Free lifetime capacity matches durable counter
plan catalogue uses opaque MerchantPricingPlan IDs
no Shopify plan handle/provider contract leaks
```

### R11 — Paid activation from durable create-command boundary

Seed accepted API-003 pre-provider state, deliver signed `activated`, and prove the same Subscription becomes paid with:

```text
periodStart = signed completed provider payment timestamp
periodEnd = signed next_payment_date
included grant/current allowance = target plan allowance
```

Do not assert a local +30-day end.

### R12 — Paid plan switch preserves usage and follows signed next-payment movement

For upgrade and downgrade, deliver signed `updated` and prove:

```text
same BillingPeriod id/start
plan/current allowance changes
committed/reserved/forfeited unchanged
periodEnd/currentPeriodEnd = signed updated next_payment_date
```

### R13 — Pause freezes paid included but preserves owned fallback capacity

Deliver `paused` and prove:

```text
Subscription = FROZEN
no successor paid period
paid included unavailable
promotional/purchased/lifetime-Free fallback usable when funded
```

Also preserve Shopify FROZEN hard-block regression.

### R14 — Renewed opens the next Woo paid period

Deliver signed `renewed` with a new completed payment and later next_payment_date.

Prove old period closes, exactly one new period/counter opens, included usage resets in that new provider period, and FROZEN becomes ACTIVE.

Also prove wall-clock expiry without renewed creates no new paid period.

### R15 — Woo cancellation returns the current Subscription to Free

Deliver verified Woo `canceled` for the current paid provider contract.

Prove atomically:

```text
Subscription.status = ACTIVE
current plan = Free
providerSubscriptionId = NULL
billingPeriodId = NULL
currentPeriodStart/currentPeriodEnd = NULL
cancelAtPeriodEnd = false
```

Prove:

```text
lifetime Free grant is not recreated/reset
purchased/lifetime-Free capacity is usable through Free policy
former paid BillingPeriod/counter remains durable as the single detached resumable allowance window
```

### R15A — Later paid purchase uses ordinary Free -> paid and carries usage only inside the former period

#### Activation before former period end

From the Free state above, execute/seed the normal API-003 Free -> paid `SUBSCRIPTION_CREATE` path and deliver verified activation before the detached former paid period end.

With:

```text
former allowance = 10
former committed = 4
```

prove:

```text
same Moda Subscription row
new provider contract current
paid ACTIVE
prior usage carried forward
same-plan remaining included = 6
```

A different target paid plan preserves prior usage and applies the target current allowance.

#### Activation at/after former period end

Execute the same normal Free -> paid path at/after the former period end.

Prove:

```text
former period closes/historical
new paid BillingPeriod
full target-plan allowance
committed/reserved/forfeited = 0
```

### R15B — Old canceled-contract terminal events cannot mutate current state

While the current Subscription is Free, old provider terminal evidence must not perform another plan transition.

After a later new paid activation, old canceled-contract `prepaid_term_ended`/other lifecycle evidence must not mutate the new current provider contract.

### R15C — Shopify cancellation/continuation regression

Shopify cancel-before-end keeps current paid period/allowance usable. Continuation before period end creates no new period/reset; normal provider-cycle rollover remains unchanged.

### R16 — Free top-up activation

While current Subscription is local Free, seed only the API-004 durable pre-provider state:

```text
REQUESTED Woo RecoveryCreditPurchase
billingPeriodId = NULL
providerSubscriptionIdSnapshot = NULL

linked ONE_TIME_CHARGE operation
state = AWAITING_CONFIRMATION
providerContractId = synthetic charge contract
```

Deliver a valid signed `activated` charge webhook.

Prove:

```text
purchase ACTIVE
currentAmount = creditsGranted
Woo provider evidence persisted
operation CONFIRMED
PURCHASED_RECOVERY_CREDITS grant increments exactly once
Free recurring provider contract remains NULL
no purchase UsageEvent is created
receipt processed
```

Deliver the exact webhook twice and prove no double grant.

### R17 — Paid top-up survives acquisition-period change

Repeat R16 for a paid Shop where API-004's purchase snapshot references the then-current BillingPeriod.

Close/advance that BillingPeriod before delivering the provider `activated` receipt.

Prove the purchase still activates successfully because purchase ownership/provider evidence is not dependent on the acquisition period remaining current/open.

### R18 — Cross-provider refund period semantics

#### Shopify

Create a Shopify top-up in billing period A, rotate the current Shopify provider context to billing period B, and prove the old period-A purchase is not normal merchant-refund eligible.

#### Woo

Create/activate a Woo one-time-charge purchase, then close/change its acquisition recurring BillingPeriod (or later return recurring billing to Free) while unused/unreserved credits remain.

Prove API-006 still reports the Woo purchase refund-eligible from its own durable purchase evidence.

This records the provider difference: Shopify corrections are current-period/meter bound; Woo SaaS one-time-charge refund requests have no day-after-payment limit.

### R19 — Canceled charge before activation clears the pending checkout

Seed a REQUESTED purchase + unresolved one-time-charge operation.

Deliver:

```text
canceled
or
prepaid_term_ended
```

charge evidence before activation.

Prove:

```text
operation = FAILED
lastErrorCode = WOO_CHARGE_CANCELED_BEFORE_ACTIVATION
purchase remains REQUESTED
currentAmount = 0
no purchased-capacity grant
API-002 no longer reports that failed attempt as unresolved same-bundle checkout
```

### R20 — Normal Woo refund allowance flow

Request a real local API-006 hold, wait for reservations, and prove BACKGROUND-005 freezes `finalCreditQuantity` with Woo expectedProviderAmount/currency null.

Deliver trusted refunded provider evidence and prove purchase/refund/counter complete exactly by finalCreditQuantity regardless of provider monetary amount.

### R21 — Refund reservations and pre-provider reactivation

Preserve REQUESTED reservation wait and reactivation race. Moda calculates no money.

### R22 — Provider monetary amount is audit-only

Use fixtures with different provider monetary evidence and prove identical held allowance completion; no NEEDS_ATTENTION merely because money differs.

### R23 — Unmatched provider refund is attention-only

Provider refund with no local hold leaves purchase/counters unchanged, invents no refund and infers no credits from money. ADMIN-001 projects read-only attention.

### R24 — Provider rejection hold-release remains external capability gate

Do not fabricate a rejection signal. No provider-started hold is released without trusted rejection/cancellation evidence; SYSTEM-TEST-002 owns real certification.

### R25 — Duplicate and byte-distinct webhook semantics

For at least one subscription and one charge lifecycle:

#### Exact duplicate

Same:

```text
topic
exact raw bytes
```

sent twice.

Prove:

```text
one receipt row for exact duplicate identity
both HTTP deliveries accepted
business state applied once
```

#### Byte-distinct equivalent JSON

Same semantic object but different whitespace/key formatting with valid independent HMAC.

Prove:

```text
distinct receipt rows
Background remains business-idempotent
```

### R26 — Invalid webhook signature

Send a valid provider-shaped payload with an invalid HMAC.

Prove:

```text
401 / accepted API error contract
zero receipt rows
zero billing-state mutation
```

No secret/raw payload appears in captured application logs.

### R27 — Cross-Shop provider contract collision fails closed

Create conflicting trusted local operation/subscription evidence that would map one synthetic provider contract to two Shops.

Deliver a valid signed webhook.

Prove:

```text
no cross-tenant mutation
receipt remains unprocessed with the accepted bounded conflict error where applicable
```

Do not relax the fixture merely to get the scenario green.

### R28 — API presentation agrees with durable state

After each major lifecycle stage, query the real:

```text
GET /v1/billing
GET /v1/billing/plans
GET /v1/billing/recovery-credit-purchases
```

as applicable and prove the merchant-safe projection agrees with durable database state.

At minimum validate:

```text
Free current plan
paid current plan
pending plan
pending cancellation
FROZEN
scheduled cancellation
top-up pending/confirmed/active
purchased available balance
refund REQUESTED
PROVIDER_ACTION_REQUIRED
NEEDS_ATTENTION
REFUNDED history
```

Do not read provider IDs/Shopify handles from browser-facing responses.

### R29 — Woo plugin contract composition evidence

Do not rebuild browser UI logic in the system-test repo.

Run/collect the accepted WOOCOMMERCE-001/002/003 repository validation evidence for:

```text
browser -> local WP REST -> PHP Moda client boundary
recurring confirmation redirect/return
one-bundle top-up redirect/return
purchase-history/refund/reactivation
no credential/provider-ID leakage
```

If the system-test environment already has a compatible accepted wp-env/browser harness, run one representative smoke for each surface against controlled API fixtures.

Otherwise reuse the prerequisite task's browser/DOM integration evidence and record the exact implementation SHA/test command rather than adding a second WordPress harness here.

### R30 — Shopify compatibility is part of terminal evidence

Run the accepted SHOPIFY-001 focused/full regression commands and record their evidence.

Additionally prove in the disposable database fixture that synthetic Woo rows do not enter Shopify projections under the accepted provider-scoped queries.

At minimum capture evidence for:

```text
Shopify BillingPlan materialisation reuse
Shopify top-up purchase provider=SHOPIFY
Shopify UsageEvent provider=SHOPIFY
Shopify purchase history excludes Woo rows
Shopify refund request/reactivation excludes Woo rows
Shopify currentAllowanceQuantity remains NULL
Shopify hosted pricing/subscription callback tests remain green
```

Do not require live Shopify Partner credentials for SYSTEM-TEST-001.

### R31 — Gateway configuration/transport evidence is included

Run/collect GATEWAY-001 evidence proving:

```text
test/production Woo billing env groups
secret attached only to private API
existing API host reused
Woo topic/signature headers preserved
raw webhook bytes preserved
no smaller Gateway webhook body limit
```

SYSTEM-TEST-001 does not provision real secrets or deploy Render.

### R32 — No secrets in evidence

Generated system evidence may contain:

```text
synthetic Shop IDs
synthetic operation/purchase/refund IDs
synthetic provider contract IDs
repository SHAs
bounded error codes
counts/quantities
synthetic amounts
```

It MUST NOT contain:

```text
real Woo key/secret
real Shopify credentials
installation bearer credential
raw Authorization headers
webhook signing secret
raw customer/payment data
```

Synthetic secrets should be redacted from persisted evidence even though they are test-only.

### R33 — Deterministic evidence artifact

Generate:

```text
docs/evidence/ARCH-027/SYSTEM-TEST-001-integrated-evidence.json
```

with at least:

```text
schemaVersion = 1
architectureId = ARCH-027
taskId = ARCH-027-SYSTEM-TEST-001
startedAt
completedAt
repositoryHeads[]
databaseMigrationEvidence
scenarios[]
shopifyRegression
gatewayEvidence
wooPluginEvidence
secretScan
overallResult
```

Every required scenario has:

```text
id
result = PASS | FAIL | BLOCKED
bounded evidence summary
```

`overallResult = PASS` only when every required non-external scenario is PASS.

No Woo sandbox-only scenario is marked PASS in this task.

## Acceptance Scenarios

At minimum the terminal matrix must include:

1. first Woo connection -> one-time Free activation;
2. reconnect preserves tenant/balances;
3. authenticated Free billing read;
4. Free -> paid verified activation;
5. paid upgrade same period;
6. paid downgrade below committed usage;
7. pause -> FROZEN with paid included blocked and owned fallback capacity usable;
8. renewed -> ACTIVE and opens the next provider-backed period;
9. wall-clock period expiry without renewed creates no new paid period;
10. delayed stale provider lifecycle cannot regress a newer provider period;
11. Woo cancellation -> current Moda Subscription immediately Free, former paid period preserved only as detached resumable history;
12. ordinary Free -> paid after cancellation, before former period end, carries prior usage;
13. ordinary Free -> paid after former period end starts new full-allowance period;
14. Free one-time top-up activation;
16. paid top-up activation after acquisition period changed;
17. canceled top-up checkout clears same-bundle pending state;
18. duplicate charge webhook no double grant;
19. normal Woo refund hold/preparation/completion;
20. reserved refund waits;
21. pre-provider reactivation;
22. Background-preparation/reactivation race;
23. provider monetary amount is audit-only and cannot change held allowance;
24. unmatched provider refund remains read-only attention/no allowance inference;
25. provider-started hold is not released without trusted rejection/cancellation evidence;
26. Shopify cancel/continuation before period end does not reset allowance;
27. unmatched provider under-refund has no mutation;
28. invalid webhook HMAC creates no receipt/state;
29. exact duplicate webhook dedupe;
30. byte-distinct equivalent webhook business idempotency;
31. cross-Shop provider-contract conflict fails closed;
32. API read models match durable lifecycle state;
33. Woo plugin accepted recurring/top-up/refund UI evidence;
34. Shopify compatibility/regression matrix;
35. Gateway Woo secret/routing/raw-body evidence;
36. evidence contains no secrets.

## Evidence To Capture

Capture bounded evidence such as:

```text
Shop / WooCommerceInstallation IDs
Subscription before/after
BillingPlan / MerchantPricingPlan IDs
BillingPeriod IDs/start/end/close reason
included counter quantities/current allowance
WooCommerceBillingOperation state
WooCommerceBillingWebhookReceipt id/topic/processed/error
RecoveryCreditPurchase status/quantities/provider
RecoveryCreditRefund status/reason/expected/actual provider amounts
PURCHASED_RECOVERY_CREDITS aggregate
API response summaries
Admin recovery result/audit ID
repository SHAs
test command exit codes
```

Do not persist full provider payloads or credentials.

## Work Items

- [ ] Add ARCH-027 local integration runner/harness to `moda-interact-system-test`.
- [ ] Add pgvector PostgreSQL disposable fixture use for the full current migration set.
- [ ] Add prerequisite repository SHA/clean-state collection.
- [ ] Add deterministic signed Woo webhook fixture.
- [ ] Add accepted API/Background process orchestration against one disposable database.
- [ ] Add Free connection/reconnect + authenticated billing-read scenarios.
- [ ] Add recurring lifecycle scenarios from durable API-003 command boundary.
- [ ] Add provider-driven renewal/FROZEN fallback period scenarios.
- [ ] Add top-up acquisition scenarios from durable API-004 command boundary.
- [ ] Add API-006/BACKGROUND-005 allowance-only refund scenarios.
- [ ] Add Woo cancel-to-Free + later ordinary Free->paid before/after-former-period scenarios.
- [ ] Add Shopify scheduled-cancel/no-reset regression.
- [ ] Add webhook duplicate/signature/tenant-isolation scenarios.
- [ ] Add API read-model consistency assertions.
- [ ] Reuse/collect accepted Woo plugin browser/REST integration evidence.
- [ ] Reuse/collect SHOPIFY-001 regression evidence and add cross-provider fixture assertions.
- [ ] Reuse/collect GATEWAY-001 transport/config evidence.
- [ ] Generate deterministic redacted JSON evidence.
- [ ] Add one command to execute the complete local ARCH-027 suite.

## Interfaces / Contracts

### Suggested repository command

Add one stable entry point such as:

```text
npm run validate:arch027:billing
```

The exact script name may follow repository conventions, but the task Completion Report must record the canonical command.

### External provider boundary

SYSTEM-TEST-001 emulates:

```text
signed provider webhook delivery
```

only.

It does not emulate the API-003/API-004 outbound provider origin by changing production configuration.

### Durable command fixture boundary

Allowed direct fixture creation is limited to the pre-provider-confirmation records accepted from:

```text
API-003
API-004
```

and must use production schema/invariants.

## Dependencies

All listed ARCH-027 implementation tasks must be architect-accepted Complete before this task runs.

This is deliberate: system-test is terminal validation, not a dependency used to unlock unfinished implementation.

## Enables

- `ARCH-027-SYSTEM-TEST-002`

SYSTEM-TEST-002 is the separately developer-gated real Woo sandbox certification task.

It consumes the accepted SYSTEM-TEST-001 baseline only after local/mock integration is Complete and does not enable unfinished implementation.

## Acceptance Criteria

- [ ] Task is manually authorized only after every implementation dependency is Complete.
- [ ] No production repository source is changed by system-test implementation.
- [ ] No shared/production database or real Woo credential is required.
- [ ] Full accepted database migration set runs on disposable pgvector PostgreSQL.
- [ ] Fresh + Shopify-upgrade persistence rehearsal passes.
- [ ] Primary provider webhook scenarios enter through real API-005, not direct receipt inserts.
- [ ] Background lifecycle scenarios execute the accepted production billing reconciliation composition.
- [ ] No test-only Woo provider base URL/configuration is introduced.
- [ ] Every required recurring lifecycle scenario passes.
- [ ] Every required provider-period renewal/FROZEN fallback scenario passes.
- [ ] Every required top-up acquisition scenario passes.
- [ ] Every required refund/reactivation/allowance-hold/provider-outcome scenario passes.
- [ ] Woo cancel-to-Free / later Free->paid carry-forward-or-fresh-period and Shopify cancel/no-reset scenarios pass.
- [ ] Duplicate/out-of-order/security/tenant-isolation assertions pass.
- [ ] API merchant-safe reads agree with durable database state.
- [ ] Woo plugin accepted browser/REST integration evidence is present for recurring/top-up/refund surfaces.
- [ ] Shopify compatibility/regression evidence is present and Woo rows cannot leak into Shopify projections.
- [ ] Gateway Woo secret isolation/raw-body/header transport evidence is present.
- [ ] Evidence JSON contains no secret/token/raw customer-payment data.
- [ ] Cross-provider refund-period semantics are validated: Shopify current-period restriction vs Woo purchase-local historical refund eligibility.
- [ ] No sandbox-only capability is falsely marked validated.
- [ ] All required scenario rows are PASS before `overallResult=PASS`.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

At minimum run:

```text
npm test
npm run typecheck
npm run lint
```

plus the new ARCH-027 integrated command.

The system task must also run or deterministically consume accepted commands/evidence from the prerequisite repositories. The final evidence must record:

```text
command
repository SHA
exit code
```

for each prerequisite validation reused.

Required final checks:

- [ ] `git diff --check`;
- [ ] evidence JSON schema/content self-validation;
- [ ] secret scan of generated evidence/log excerpts;
- [ ] no required test silently skipped;
- [ ] no required scenario marked PASS from mocked business postconditions;
- [ ] dedicated system-test task worktree/branch/push evidence.

## Stop Condition

STOP and return to `moda_architect` if:

- any dependency is not Complete;
- repository SHAs do not match the coordinated implementation baseline;
- a required production service cannot be run against disposable infrastructure;
- a scenario fails;
- a real provider capability is required to establish the result;
- the only way to pass would be to modify production behavior from this task.

On successful execution:

```text
write Completion Report
write SYSTEM-TEST-001-integrated-evidence.json
status -> review
return to moda_architect
STOP
```

Do not begin Woo sandbox certification automatically.

## Completion Report

### Status

Not Started

### Baseline

Populate during execution.

### Harness Changes

Populate during execution.

### Validation Commands

Populate during execution.

### Scenario Matrix

Populate during execution.

### Shopify Regression

Populate during execution.

### Gateway Evidence

Populate during execution.

### Woo Plugin Evidence

Populate during execution.

### Evidence Artifact

Pending.

### Outcome

Pending.

### Architect Review

Manual terminal gate; pending.
