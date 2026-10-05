---
id: ARCH-027-SYSTEM-TEST-002
architecture_id: ARCH-027
title: Certify WooCommerce Marketplace SaaS Billing in the real sandbox
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: developer
completion_mode: manual
status: pending
priority: 120
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-SYSTEM-TEST-001
enables: []
created: 2026-10-04
updated: 2026-10-04
---

# Certify WooCommerce Marketplace SaaS Billing in the real sandbox

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Terminal / External Provider Gate

This is the final ARCH-027 **real-provider certification task**.

It is deliberately:

```text
developer-gated
manual completion
terminal
```

Do not auto-start it.

It may begin only after:

```text
ARCH-027-SYSTEM-TEST-001 = architect-accepted Complete
```

and the developer explicitly authorizes real Woo sandbox activity.

This task may:

- create real Woo sandbox subscription contracts;
- create real Woo sandbox one-time charge contracts;
- cause sandbox payment/renewal/refund side effects;
- send real sandbox webhooks to the public test API;
- require manual merchant/vendor interaction in WooCommerce.com's sandbox UI.

It MUST NOT:

- use production Woo credentials;
- target `api.modainteract.com`;
- use production merchant/shop data;
- modify production code merely to make a provider capability appear supported;
- weaken an accepted ARCH-027 assertion to obtain a green result.

If the sandbox proves an accepted assumption false:

```text
record exact bounded evidence
mark the capability CHANGES_REQUIRED
return to moda_architect
STOP
```

Do not implement the architecture correction from this task.

## Objective

Certify the parts of ARCH-027 that local/mock integration cannot prove:

```text
real Woo /subscriptions request/response
real Woo /subscriptions/{contract} switch
real Woo cancellation
real Woo /charges
real confirmation/return URL behavior
real signed webhooks
real provider contract payload fields
real next_payment_date / end_date behavior
real proration behavior
real renewal/pause lifecycle behavior available in sandbox
real one-time-charge transaction/tax evidence
real refund request / vendor approval/rejection workflow
real provider monetary refund behavior as audit evidence
real refund/canceled webhook behavior
real cancellation -> Moda Free and later ordinary Free -> paid lifecycle
real response-loss/orphan-recovery capabilities exposed by Woo
```

The task must convert every external ARCH-027 billing assumption into one of:

```text
CERTIFIED
CERTIFIED_WITH_DOCUMENTED_LIMITATION
CHANGES_REQUIRED
BLOCKED_EXTERNAL
NOT_APPLICABLE
```

No capability may remain silently assumed after this task.

## Current Official Woo Provider Contract

This task is grounded in the Woo Marketplace SaaS Billing documentation current on 4 October 2026:

```text
https://developer.woocommerce.com/docs/woo-marketplace/billing-api-saas
```

Important published facts to verify against the live sandbox implementation:

- sandbox base URL:
  ```text
  https://sandbox.woocommerce.com/wp-json/wccom/billing/1.0/
  ```
- sandbox and production differ by domain and API credentials;
- vendor requests use Basic authentication;
- subscription creation returns a unique contract UUID and `confirmation_url`;
- one-time charge creation uses `/charges`;
- return URLs receive the provider contract ID;
- Woo sends signed `saas_billing_contract.*` webhooks;
- only one webhook endpoint is configured per SaaS application;
- the webhook body is HMAC-SHA256 signed with the application API secret;
- plan switching may move `next_payment_date` because of provider proration;
- `renewed` means a successful recurring renewal;
- `paused` means renewal was due but payment could not be processed and Woo may retry;
- canceled subscriptions retain prepaid entitlement until the provider term end;
- Woo follows canceled subscriptions with `prepaid_term_ended`;
- Woo supports one-time charge refunds;
- Woo says refund requests have no day-after-payment limit;
- merchant refund requests appear in the vendor `SaaS Apps -> Pending Refunds` workflow;
- approving a refund cancels the underlying SaaS contract and produces `refunded` / `canceled` provider lifecycle evidence;
- Woo may add tax on top of the price sent by Moda;
- Woo's sandbox provides a SaaS webhook testing tool whose available actions depend on current contract status.

The public documentation does **not** establish:

- that Moda can programmatically create a merchant refund request;
- that the vendor can initiate a refund without a Woo merchant refund request;
- that an arbitrary partial refund amount can be chosen/approved;
- that a rejected refund emits a signed webhook;
- that Woo exposes a deterministic idempotency/search key suitable for recovering a contract when the create response is lost.

Those are mandatory certification questions below.

## Prerequisites

### P1 — Accepted implementation baseline

Record and require clean deployed/tested SHAs for at least:

```text
moda-interact-database
moda-interact-api
moda-interact-background
moda-interact-woocommerce
moda-interact-admin
moda-interact-gateway
moda-interact
moda-interact-system-test
```

The SHAs must correspond to the architect-accepted ARCH-027 implementation baseline already proven by SYSTEM-TEST-001.

### P2 — Woo sandbox application access

The developer must have Woo-provided sandbox vendor application access.

Woo documents that sandbox access is granted during Marketplace onboarding/business review.

If no sandbox application/API credentials have been issued:

```text
result = BLOCKED_EXTERNAL
```

Do not substitute production credentials or a fake provider.

### P3 — Sandbox credentials only

Provision only the accepted test environment group:

```text
moda-interact-test-woo-billing-config
```

with:

```text
WOO_BILLING_ENVIRONMENT=sandbox
WOO_BILLING_API_KEY=<real sandbox key>
WOO_BILLING_API_SECRET=<real sandbox secret>
```

No real credential value is committed or written to evidence.

### P4 — Public test ingress

The sandbox SaaS application webhook URL must be:

```text
https://api-test.modainteract.com/v1/billing/webhooks/woocommerce
```

unless the architect explicitly approves a temporary public sandbox test receiver for one narrowly scoped provider-retry experiment.

Normal certification traffic must use the accepted Gateway/API ingress.

### P5 — Public merchant return surface

Woo does not accept `localhost` as the purchase `return_url`.

Use a public/non-production Woo/WordPress test installation whose accepted Moda plugin points to the test API environment.

Do not use a production merchant store.

### P6 — Dedicated sandbox merchant identity

Use a dedicated Woo sandbox merchant/test account.

Do not persist merchant personal data in system-test evidence.

## Scope

Modify only `moda-interact-system-test` test/evidence helpers required to coordinate and capture the real sandbox certification.

Expected additions conceptually:

```text
scripts/
  run-arch027-woo-sandbox-certification.mjs

src/arch027/
  woo-sandbox-evidence.ts
  woo-sandbox-capability-matrix.ts

docs/evidence/ARCH-027/
  SYSTEM-TEST-002-woo-sandbox-certification.json
  SYSTEM-TEST-002-woo-technical-review-notes.md
```

The exact repository shape may be smaller if the existing system-test evidence framework already supplies these primitives.

This task may call deployed test services and require browser/vendor-dashboard actions.

It does not modify production application repositories.

## Out of Scope

- Production Woo credentials.
- Production Marketplace activation.
- Production merchant billing.
- Changing ARCH-027 implementation.
- Adding a new provider base-URL override.
- Adding provider-specific business rules in system-test.
- Editing a real merchant's production subscription.
- Woo Marketplace business/commercial approval itself.
- Declaring QIT/plugin Marketplace technical review complete.
- Updating `docs/architecture/_index.md`.

## Result Model

Every scenario records:

```text
CERTIFIED
CERTIFIED_WITH_DOCUMENTED_LIMITATION
CHANGES_REQUIRED
BLOCKED_EXTERNAL
NOT_APPLICABLE
```

`overallResult = CERTIFIED` requires every release-blocking capability below to be either:

```text
CERTIFIED
or
CERTIFIED_WITH_DOCUMENTED_LIMITATION
```

where the documented limitation is already supported by accepted ARCH-027 behavior.

Any accepted architecture assumption disproven by Woo is:

```text
CHANGES_REQUIRED
```

and prevents ARCH-027 closure until `moda_architect` reconciles it.

## Requirements

### R1 — Capture provider reference/version context

At task start record:

```text
providerDocumentationUrl
providerDocumentationObservedAt
sandboxBaseUrl
sandboxApplicationConfigured = true
webhookUrl
testEnvironment
```

If the vendor dashboard/API reference exposes a version/build identifier, record it.

Do not persist credentials.

### R2 — Real subscription-create command

From the accepted Woo plugin Billing UI, perform a real:

```text
Free -> paid
```

flow.

Prove before confirmation:

```text
real POST /subscriptions succeeded
WooCommerceBillingOperation = AWAITING_CONFIRMATION
providerContractId persisted
confirmationUrl host = sandbox.woocommerce.com
current Moda Subscription remains Free
no paid BillingPeriod exists
```

Capture only bounded provider response evidence:

```text
contract UUID
confirmation URL host/path shape
HTTP status
response field names
```

Do not persist Authorization headers.

### R3 — Abandoned checkout does not activate paid state

Start one sandbox subscription checkout and deliberately return/navigate away without confirmation.

Prove:

```text
no activated provider evidence
Moda current plan remains Free
operation remains unresolved according to accepted state
no paid BillingPeriod/allowance appears
```

This certifies the Woo consent/confirmation boundary.

Clean up the sandbox contract if Woo provides a safe cancel action.

### R4 — Confirmed checkout / real activated webhook

Complete a real sandbox subscription checkout.

Prove all of:

```text
return URL contains the same provider contract ID
real webhook reaches API-005 through Gateway
HMAC is accepted
receipt is durably persisted
Background processes the receipt
same Moda Subscription becomes paid
```

Inspect the signed real contract snapshot and certify presence/shape of:

```text
subscription.id
subscription.status
subscription.next_payment_date
billing_intents
transactions
completed_at
amount
amount_refunded
```

The initial Woo BillingPeriod must match the accepted reconciliation rule:

```text
periodStart = verified completed payment timestamp
periodEnd   = signed next_payment_date
```

If the real provider payload cannot supply those facts:

```text
CHANGES_REQUIRED
```

### R5 — Real provider transaction amount / tax evidence

For the initial subscription and at least one one-time charge, record:

```text
Moda quoted pre-tax amount
Woo provider transaction amount
Woo amount_refunded
currency
```

Woo documents that tax may be added on top and is not reliably predictable by the vendor before checkout.

Therefore:

```text
provider transaction amount may equal quote
or
provider transaction amount may exceed quote
```

Both are valid.

If sandbox permits a taxable merchant profile, exercise one and certify the greater-than-quote path.

If sandbox produces no tax despite reasonable attempt:

```text
CERTIFIED_WITH_DOCUMENTED_LIMITATION:
    real tax-positive transaction not observed
```

provided SYSTEM-TEST-001 already proves provider-amount > quote handling.

### R6 — Real paid upgrade

From an active sandbox subscription, initiate/confirm a real upgrade.

Prove:

```text
same Woo contract ID
real updated webhook
active contract
target plan reflected
provider proration transaction/billing-intent evidence captured when present
signed next_payment_date captured
```

Then prove Moda:

```text
keeps same BillingPeriod ID/start
keeps committed/reserved/forfeited usage
changes plan/current allowance
sets periodEnd/currentPeriodEnd to signed updated next_payment_date
```

Do not assert a particular monetary proration formula beyond the provider's own observed evidence.

### R7 — Real paid downgrade

Initiate/confirm a real downgrade.

Woo's published model says a downgrade credits unused prepaid value by pushing `next_payment_date` into the future.

Certify the actual sandbox behavior:

```text
same provider contract
updated webhook
signed next_payment_date
old vs new provider next-payment date
```

For a price configuration where provider proration should extend the term, require the observed next payment date to move later.

Moda must keep the same local BillingPeriod/usage and move its current period end to the signed provider boundary.

If sandbox does not exhibit the documented behavior for the chosen plans, record exact observed evidence and return `CHANGES_REQUIRED` or repeat with a provider-supported comparison before concluding.

### R8 — Real cancellation returns Moda to Free

Cancel a real sandbox subscription through the accepted Moda UI/API.

Prove:

```text
DELETE accepted by Woo
canceled webhook delivered
provider contract is canceled
```

Then prove Moda projects:

```text
Subscription.status = ACTIVE
current plan = Free
providerSubscriptionId = NULL
billingPeriodId/currentPeriod* = NULL
```

and does not recreate/reset lifetime Free allowance.

Capture that the former paid BillingPeriod/counter remains durable but detached for allowance carry-forward testing.

### R9 — Real later subscription before the former paid period end uses normal Free -> paid

While still before the former paid BillingPeriod end, use the exact normal Free merchant paid-plan flow and confirm a new Woo subscription.

Prove:

```text
no special re-subscribe endpoint/state was used
new provider contract becomes current
paid ACTIVE
former usage is carried forward
```

For a controlled same-plan example with 10 granted / 4 committed, prove 6 included credits remain.

Record provider period dates as certification evidence, but a new contract ID must not by itself reset allowance.

### R10 — Real later subscription at/after former paid period end gets fresh allowance

Use the same normal Free -> paid path after the former paid period has ended, using only Woo-supported sandbox mechanisms/time controls.

Prove the old period is historical and the new paid period receives the full target-plan allowance.

If sandbox timing prevents this scenario, mark `BLOCKED_EXTERNAL` rather than creating fake provider state.

### R11 — Old canceled-contract lifecycle cannot mutate current Free or later paid state

After cancellation, old `prepaid_term_ended`/terminal evidence must not transition the already-Free current Subscription again.

After a later new paid activation, the old canceled contract's lifecycle must remain historical and cannot mutate the new current contract.

Also certify current-contract `paused -> FROZEN` and `renewed -> ACTIVE/next paid period` where coherent sandbox evidence is available.

### R12 — Real one-time charge purchase

From both:

```text
local Free
and
paid Woo subscription
```

where practical, initiate a real predefined top-up through the Woo plugin.

Prove:

```text
POST /charges response
unique charge contract ID
sandbox confirmation URL
no quantity field
merchant confirmation
return contract ID
real activated charge webhook
one completed provider transaction
purchase ACTIVE only after verified provider evidence
purchased credit grant exactly once
no Shopify UsageEvent acquisition row
```

At minimum one real charge path is release-blocking.

### R13 — Historical Woo charge remains provider-refundable

After a real one-time charge is active, change the recurring context:

```text
plan switch
or
paid -> Free cancellation/end where practical
```

without consuming all purchased credits.

Verify in the Woo sandbox merchant refund UI that the charge can still be selected/requested independently of the current recurring subscription period.

This certifies the provider side of ARCH-027's purchase-local Woo refund rule.

If the provider UI prevents refund solely because the recurring BillingPeriod changed:

```text
CHANGES_REQUIRED
```

### R14 — Refund initiation capability gate

This is release-blocking.

Start with a real Woo charge and create the normal Moda local refund request/hold through API-006.

Then inspect the Woo sandbox provider workflow.

Determine exactly which of the following is true:

```text
A. Moda/vendor can programmatically initiate the provider refund request.
B. Vendor dashboard can create a refund without a prior merchant Woo refund request.
C. Woo merchant must separately request the refund in WooCommerce.com before it appears in vendor Pending Refunds.
D. another Woo-supported initiation flow exists.
```

Record the exact sandbox/UI/API behavior.

The current public docs describe the merchant-request -> vendor Pending Refunds flow and do not document a vendor refund-initiation API.

If **Moda's current merchant refund action cannot cause or reach a provider refund workflow without an additional undisclosed merchant action**, current ARCH-027 merchant UX is incomplete:

```text
result = CHANGES_REQUIRED
```

The task must return to `moda_architect`; do not silently treat local hold creation as provider refund initiation.

### R15 — Vendor Pending Refunds linkage

For a real Woo merchant refund request, prove the vendor receives a corresponding item in:

```text
SaaS Apps -> Pending Refunds
```

Record bounded linkage evidence:

```text
charge/subscription contract ID
provider order/transaction identity if exposed
requested refund amount if exposed
request status
```

Do not record merchant personal information.

### R16 — Provider monetary refund behavior is informational to Moda allowance

Observe/classify Woo full/partial refund behavior for product/support evidence.

Moda must always freeze `finalCreditQuantity`, never derive credits from provider money, and remove exactly the held allowance after trusted refund completion.

A differing provider monetary amount is not an ADMIN over/under-refund condition and is not an allowance correctness failure.

### R17 — Refund approval webhook behavior

Approve a real sandbox refund.

Verify actual provider delivery of:

```text
saas_billing_contract.refunded
saas_billing_contract.canceled
```

and record observed order without assuming that order is guaranteed.

Inspect the signed charge/transaction evidence:

```text
amount
amount_refunded
provider transaction ID
completed_at
```

Prove BACKGROUND-005 matches the exact charge/purchase/local hold, completes `finalCreditQuantity` exactly once, and treats provider monetary amount as optional audit evidence rather than an allowance gate.

Duplicate/reordered provider delivery must remain business-idempotent.

### R18 — Refund rejection capability / lifecycle gate

Create a real Woo merchant refund request and **reject** it from the vendor sandbox dashboard with the provider-required reason.

Determine:

```text
does Woo emit any signed rejection webhook?
does the pending item expose a stable rejected status?
can Moda query that status through an API?
is email/dashboard the only rejection evidence?
```

Current public docs do not document a refund-rejected webhook.

If rejection produces no machine-readable provider evidence, record exactly what trusted operator/provider evidence is available. ARCH-027 must not release the allowance hold speculatively. If a deterministic rejection signal exists, return it to `moda_architect` for a bounded allowance-hold release task.

This scenario must not be skipped because approval succeeds.

### R19 — Full/partial provider refund does not change allowance arithmetic

When practical, observe different provider monetary outcomes against equivalent local held-credit scenarios. Prove `finalCreditQuantity` is unchanged, provider amount is audit-only, and no ADMIN-002 amount reconciliation exists.

### R20 — Contract response-loss recovery capability

Do not add a test-only provider base URL.

Instead, certify what Woo actually exposes for recovering a provider contract when Moda may have sent a create POST but lost the response before persisting:

```text
providerContractId
confirmationUrl
```

Inspect the current sandbox OpenAPI/reference and vendor dashboard.

Determine whether there is a deterministic supported capability to:

```text
list/search recent contracts for this application
query by a client-provided idempotency/request key
query by another Moda-controlled correlation value
recover a confirmation URL / contract ID
```

If a supported deterministic lookup exists, exercise it.

If no deterministic lookup/correlation exists:

```text
certify OUTCOME_UNKNOWN as non-retryable
record that automatic recovery is unavailable
```

and return a required architecture follow-up describing the only safe operator/provider support recovery mechanism.

Do not use:

```text
matching by price alone
matching by approximate time alone
matching by merchant PII
```

as deterministic recovery.

### R21 — Actual provider payload sufficiency / ordering evidence

Across activated, updated, renewed, paused, canceled and prepaid-term-ended scenarios, record whether the signed contract snapshots consistently contain the fields ARCH-027 uses for stale/current-state guards:

```text
next_payment_date
end_date
billing intent status/updated_at
transaction completed_at
contract status
contract ID
```

If a lifecycle topic lacks sufficient signed evidence to prevent stale-arrival regression under BACKGROUND-002:

```text
CHANGES_REQUIRED
```

Do not certify "last HTTP delivery wins."

### R22 — Webhook HMAC / Gateway certification with real Woo

For at least:

```text
one subscription webhook
one charge webhook
```

prove real Woo traffic traverses:

```text
sandbox.woocommerce.com
-> api-test.modainteract.com
-> Gateway
-> private API-005
```

and passes the actual HMAC verification.

Evidence stores only:

```text
topic
payload SHA-256
receipt ID
HTTP outcome
```

Never persist:

```text
X-WC-Webhook-Signature
API secret
raw Authorization
full customer/payment data
```

### R23 — Sandbox webhook testing tool behavior

Use Woo's sandbox-only SaaS webhook testing tool where needed.

For every tool-generated event record:

```text
contract status before
event selected
provider snapshot fields received
whether provider contract state changed
whether payment/transaction evidence changed
```

Do not treat a tool-generated topic as proof of real payment/renewal semantics when the signed snapshot does not support that conclusion.

### R24 — Return URL behavior

For real subscription create/switch and one-time charge checkout:

```text
return_url is accepted by Woo
localhost is not used
provider appends contract ID
browser returns to the intended test Woo Admin surface
plugin treats return as refresh signal only
```

Provider return must never activate local entitlement without webhook/provider reconciliation.

### R25 — USD-only compatibility

Confirm the sandbox rejects or otherwise does not support non-USD according to current provider capability.

The Moda Woo adapter remains:

```text
USD only
```

without imposing that restriction globally on the catalogue.

No destructive non-USD test is required if the current API reference/provider docs already make the sandbox contract unambiguous; record the source/version evidence.

### R26 — Provider technical-review readiness

At completion generate bounded notes sufficient for Woo's technical review:

```text
public test plugin/store URL
test API/webhook URL
merchant test instructions
subscription create/switch/cancel flow
one-time charge flow
refund flow actually supported after certification
known sandbox limitations
```

Do not include credentials.

Woo's technical approval itself is external and is not automatically claimed by this task.

## Mandatory Capability Matrix

The final evidence must contain at least these rows:

```text
SANDBOX_ACCESS
SUBSCRIPTION_CREATE
CHECKOUT_ABANDON
SUBSCRIPTION_ACTIVATED
CANCEL_TO_FREE
FREE_TO_PAID_CARRY_FORWARD
FREE_TO_PAID_FRESH_PERIOD
STALE_OLD_CONTRACT_END
PROVIDER_PERIOD_FIELDS
UPGRADE_PRORATION
DOWNGRADE_PRORATION
CANCEL_END_DATE
PREPAID_TERM_ENDED
RENEWED
PAUSED_RETRY
ONE_TIME_CHARGE
PROVIDER_TRANSACTION_AMOUNT
TAX_POSITIVE_OBSERVED
HISTORICAL_CHARGE_REFUND_ELIGIBILITY
REFUND_INITIATION
PENDING_REFUND_LINKAGE
PROVIDER_REFUND_AMOUNT_BEHAVIOR
REFUND_APPROVAL
REFUND_REJECTION
REFUND_WEBHOOK_ORDER
OUTCOME_UNKNOWN_RECOVERY
PAYLOAD_ORDERING_EVIDENCE
REAL_WEBHOOK_HMAC
RETURN_URL
USD_ONLY
TECHNICAL_REVIEW_READY
```

Each row records:

```text
result
observedAt
boundedEvidence
architectureImpact
followUpRequired
```

## Evidence Artifact

Generate:

```text
docs/evidence/ARCH-027/SYSTEM-TEST-002-woo-sandbox-certification.json
```

with:

```text
schemaVersion = 1
architectureId = ARCH-027
taskId = ARCH-027-SYSTEM-TEST-002
provider = WOOCOMMERCE_MARKETPLACE_SAAS_BILLING
providerDocumentationUrl
providerDocumentationObservedAt
sandboxBaseUrl
startedAt
completedAt
repositoryHeads[]
deploymentEvidence
capabilities[]
contractScenarios[]
refundScenarios[]
webhookEvidence[]
securityRedaction
overallResult
```

Generate companion:

```text
docs/evidence/ARCH-027/SYSTEM-TEST-002-woo-technical-review-notes.md
```

for the external Woo review handoff.

### Evidence redaction

Evidence MAY contain:

```text
sandbox contract UUID
sandbox transaction ID
Moda Shop/operation/purchase/refund IDs
amounts/currency
provider lifecycle dates
payload SHA-256
repository SHAs
bounded provider status
```

Evidence MUST NOT contain:

```text
Woo API key
Woo API secret
Authorization header
webhook signature
merchant name
merchant email
billing address
payment method/card data
raw provider transaction URL
full raw webhook payload
```

## Work Items

- [ ] Add developer-gated sandbox certification runner/evidence helpers.
- [ ] Record accepted repository/deployment baseline.
- [ ] Verify sandbox app/credentials/webhook configuration.
- [ ] Certify real subscription create + abandoned checkout.
- [ ] Certify real activated checkout and provider period fields.
- [ ] Certify real upgrade/downgrade proration and next-payment changes.
- [ ] Certify verified cancellation -> current Moda Free behavior.
- [ ] Certify replacement subscription before period end resumes same usage.
- [ ] Certify replacement subscription after period end starts fresh full allowance.
- [ ] Certify real/supportable prepaid-term-ended behavior.
- [ ] Certify real/supportable renewal behavior.
- [ ] Certify real/supportable paused -> renewed behavior.
- [ ] Certify real one-time charge activation and provider transaction amount.
- [ ] Verify historical charge remains refundable after recurring-context change.
- [ ] Determine the actual provider refund-initiation workflow.
- [ ] Determine/record provider full/partial monetary refund behavior as audit/product evidence.
- [ ] Certify real refund approval and provider webhooks.
- [ ] Certify refund rejection behavior and machine-readable evidence availability.
- [ ] Prove provider monetary variation does not change Moda finalCreditQuantity.
- [ ] Determine OUTCOME_UNKNOWN provider recovery capability.
- [ ] Prove actual signed payloads contain sufficient ordering/period evidence.
- [ ] Prove real Woo HMAC webhook ingress through Gateway/API.
- [ ] Exercise the sandbox webhook testing tool without overclaiming its semantics.
- [ ] Produce redacted certification JSON + technical-review notes.
- [ ] Return every unsupported/contradictory capability to `moda_architect`.

## Dependencies

- `ARCH-027-SYSTEM-TEST-001`

SYSTEM-TEST-001 must be architect-accepted Complete first.

This guarantees the product has already passed deterministic local integration and that sandbox activity is only answering genuinely external provider questions.

## Enables

None.

Successful architect acceptance of this task is the final ARCH-027 provider-certification gate before architecture closure/index reconciliation.

It does not enable unfinished implementation.

## Acceptance Criteria

- [ ] Real sandbox credentials/application were used; no production credential/provider was touched.
- [ ] Real subscription create/confirmation/activated flow is certified.
- [ ] Abandoned checkout does not activate Moda paid state.
- [ ] Real signed provider payload supplies the period/payment evidence BACKGROUND-002 requires.
- [ ] Real upgrade/downgrade behavior is compatible with same-period usage + signed next-payment movement.
- [ ] Verified cancellation immediately returns the current Moda Subscription to Free while preserving prior paid-period usage history for possible carry-forward.
- [ ] Re-subscribe before period end resumes same usage; after period end starts fresh full allowance.
- [ ] Old canceled-contract terminal evidence cannot end replacement current contract.
- [ ] prepaid_term_ended is certified only with coherent signed term-end state, otherwise explicitly BLOCKED_EXTERNAL.
- [ ] Renewal opens a new provider-backed Moda period only when real/supportable signed provider payment evidence exists.
- [ ] Paused produces FROZEN with no new paid allowance; owned fallback capacity remains usable.
- [ ] Real one-time charge purchase activates exactly once.
- [ ] Provider transaction amount/tax behavior is recorded without assuming quote equality.
- [ ] Woo historical one-time charge remains provider-refundable after recurring-context changes.
- [ ] Actual refund initiation path is known and compatible with Moda merchant UX; otherwise CHANGES_REQUIRED.
- [ ] Vendor Pending Refunds linkage is proven.
- [ ] Provider full/partial monetary refund behavior is classified, but Moda allowance never depends on monetary equality.
- [ ] Refund approval and actual amount_refunded webhook evidence are proven.
- [ ] Refund rejection behavior is classified and Moda has an accepted way to release the local hold; otherwise CHANGES_REQUIRED.
- [ ] Provider monetary amount differences are proven not to alter Moda finalCreditQuantity.
- [ ] OUTCOME_UNKNOWN recovery capability/limitation is explicitly resolved; no unsafe blind retry is introduced.
- [ ] Real payload fields are sufficient for the accepted stale/current-state lifecycle guards.
- [ ] Real Woo webhooks pass Gateway/API HMAC verification.
- [ ] Return URL contract-ID behavior is proven and remains a refresh signal only.
- [ ] USD-only provider compatibility remains bounded to Woo.
- [ ] Evidence contains no provider secrets or merchant/payment PII.
- [ ] Woo technical-review handoff notes are generated.
- [ ] No capability is silently left assumed.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Run the accepted system-test repository checks:

```text
npm test
npm run typecheck
npm run lint
```

plus the developer-gated sandbox certification command added by this task.

The Completion Report must record:

```text
command
repository SHA
exit code
manual provider action
provider capability result
```

for each scenario.

Also run:

- [ ] evidence JSON self-validation;
- [ ] evidence secret/PII scan;
- [ ] `git diff --check`;
- [ ] clean system-test worktree/task branch evidence.

## Stop Condition

Immediately STOP and return to `moda_architect` if any release-blocking provider fact is incompatible with accepted ARCH-027, including:

```text
required signed period fields absent
provider renewal semantics incompatible with the period model
historical one-time charge cannot be refunded as assumed
Moda refund action has no usable provider initiation path
refund rejection leaves an unrecoverable local hold
provider payload lacks safe lifecycle ordering evidence
```

Do not "fix" those from the system-test task.

If sandbox access itself is unavailable:

```text
status remains pending/review as appropriate
outcome = BLOCKED_EXTERNAL
```

Do not claim certification.

On successful provider certification:

```text
write evidence artifacts
finish Completion Report
status -> review
return to moda_architect
STOP
```

Architecture closure/index reconciliation happens only after architect review.

## Completion Report

### Status

Not Started

### Sandbox Access

Pending.

### Deployed Baseline

Pending.

### Capability Matrix

Pending.

### Subscription Evidence

Pending.

### Plan-Switch / Period Evidence

Pending.

### Cancellation / Renewal / Pause Evidence

Pending.

### One-Time Charge Evidence

Pending.

### Refund Initiation / Partial Refund Evidence

Pending.

### Refund Approval / Rejection Evidence

Pending.

### OUTCOME_UNKNOWN Recovery Evidence

Pending.

### Webhook / Security Evidence

Pending.

### Evidence Artifacts

Pending.

### Overall Result

Pending.

### Required Architecture Follow-up

Pending.

## Architect Review

### Review Status

Pending

### Review Notes

Pending sandbox execution.

### Reviewed Evidence

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
