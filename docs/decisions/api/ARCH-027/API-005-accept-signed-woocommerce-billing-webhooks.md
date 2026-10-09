---
id: ARCH-027-API-005
architecture_id: ARCH-027
title: Accept and durably persist signed WooCommerce billing webhooks
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 40
executor: copilot
claimed_at: 2026-10-09T10:23:57Z
attempt: 1
depends_on:
  - ARCH-027-API-004
enables:
  - ARCH-027-BACKGROUND-002
  - ARCH-027-GATEWAY-001
created: 2026-10-03
updated: 2026-10-09
---

# Accept and durably persist signed WooCommerce billing webhooks

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Add exactly one public Woo Marketplace SaaS Billing webhook ingress route:

```text
POST /v1/billing/webhooks/woocommerce
```

The route has one bounded responsibility:

```text
Woo HTTPS webhook
    -> read exact raw request body with a hard size bound
    -> verify Woo HMAC-SHA256 signature over those exact bytes
    -> validate the supported Woo billing topic and minimum provider contract shape
    -> compute SHA-256 of the exact raw bytes
    -> persist one WooCommerceBillingWebhookReceipt
    -> acknowledge Woo only after the receipt commit succeeds
```

The route MUST NOT apply Moda business state.

It MUST NOT:

- activate or switch a `Subscription`;
- rotate/open/close a `BillingPeriod`;
- change `BillingPeriodEntitlementCounter`;
- activate or refund a `RecoveryCreditPurchase`;
- complete a `RecoveryCreditRefund`;
- mark a `BillingOperation` confirmed;
- resolve/materialize a target paid `BillingPlan`;
- enqueue a second copy of the receipt;
- require the Woo WordPress installation bearer credential.

The durable PostgreSQL receipt is the ARCH-027 v1 API -> Background handoff. Background will later claim unprocessed receipts directly from PostgreSQL and interpret the Woo-specific provider payload against Moda operations/business state.

No Shared lifecycle-event package is introduced for this boundary.

## Context

ARCH-027 has deliberately converged on a minimal provider-edge design:

- API-003 initiates recurring Woo create/switch/cancel commands but does not apply entitlements;
- API-004 initiates one predefined top-up charge but leaves its `RecoveryCreditPurchase` in `REQUESTED`;
- verified provider evidence is required before Moda applies paid subscription/top-up state;
- `ARCH-027-DATABASE-001` already defines the durable provider receipt:
  `woocommerce.WooCommerceBillingWebhookReceipt`;
- the user explicitly rejected a second normalized Shared lifecycle abstraction for the API -> Background handoff;
- the receipt table itself is the durable cross-repository boundary.

Woo's current Marketplace SaaS Billing documentation states:

- the application configures one public webhook URL for the SaaS application;
- the endpoint is not protected with application authentication or IP whitelisting;
- Woo places the lifecycle topic in `X-WC-Webhook-Topic`;
- Woo signs the exact request body with the application API secret and sends
  `X-WC-Webhook-Signature`;
- validation is `base64(HMAC-SHA256(rawBody, apiSecret))`;
- a non-success response is treated as failed delivery and Woo retries up to five times;
- webhook payloads contain a provider contract snapshot and do not contain merchant identity;
- the current documented topics are:

```text
saas_billing_contract.activated
saas_billing_contract.updated
saas_billing_contract.renewed
saas_billing_contract.paused
saas_billing_contract.canceled
saas_billing_contract.prepaid_term_ended
saas_billing_contract.refunded
```

Provider reference verified 3 October 2026:

`https://developer.woocommerce.com/docs/woo-marketplace/billing-api-saas`

This task implements only provider authentication + durable acceptance. The later Background tasks own topic semantics and Moda lifecycle transitions.

## Scope

Modify only `moda-interact-api` implementation/tests/OpenAPI/runtime code required for signed Woo webhook ingress and durable receipt creation, plus the nested `database/` gitlink only when required to consume the newest compatible architect-accepted database commit.

Expected implementation areas are conceptually:

```text
src/
  billing/
    webhooks/
      woo-billing-webhook-route.ts
      woo-billing-webhook-signature.ts
      woo-billing-webhook-payload.ts
      woo-billing-webhook-receipt.service.ts
  server/router integration...
openapi/
  woocommerce-billing-webhook-v1.yaml
tests/
  ... raw-body / signature / dedupe / persistence tests
```

Exact repository-local filenames may differ after API-001 through API-004 establish the accepted internal route/server structure.

Reuse:

- the accepted `WOO_BILLING_API_SECRET` configuration from API-003;
- the existing database client/transaction boundary;
- the Shared structured logger;
- existing framework/OpenTelemetry HTTP instrumentation;
- existing generic request correlation conventions.

Do not create a competing generic logger, HTTP metrics layer, queue transport or provider lifecycle framework.

## Out of Scope

- Woo recurring command initiation.
- Woo top-up command initiation.
- Merchant/install bearer authentication on the webhook endpoint.
- IP allowlisting.
- Woo provider API Basic authentication on inbound requests.
- Applying `Subscription`, `BillingPeriod`, allowance, purchase or refund transitions.
- Mapping Woo topics into provider-neutral lifecycle enums/events.
- A Shared webhook/lifecycle package.
- BullMQ/outbox publication of accepted receipts.
- Background receipt claiming/retry semantics.
- Reconciliation of `OUTCOME_UNKNOWN` create operations.
- Purchase/refund business logic.
- Woo WordPress UI.
- Woo return-URL handling.
- Gateway/Render infrastructure changes.
- Editing Prisma schema/migrations.
- Updating `docs/architecture/_index.md`.
- Woo sandbox certification.

## Requirements

### R1 — Exact public webhook route

Implement exactly:

```text
POST /v1/billing/webhooks/woocommerce
```

It is a provider-to-provider route.

It MUST NOT require:

```text
X-Moda-Installation-Id
Authorization: Bearer <installation credential>
Woo Shop domain
shopId
```

and MUST NOT accept tenant identity in the query string or request body.

No query parameters are required or interpreted.

The route must be publicly reachable through the existing hosted API topology once the later Gateway/configuration task is deployed.

### R2 — Exact supported provider headers

Require exactly one non-blank value for each:

```text
X-WC-Webhook-Signature
X-WC-Webhook-Topic
```

HTTP header matching is case-insensitive.

Reject ambiguous duplicate values rather than selecting one arbitrarily.

Do not require:

```text
X-WC-Webhook-ID
X-WC-Webhook-Delivery-ID
X-WC-Webhook-Source
```

for correctness.

Those generic Woo webhook headers may be present but are not durable identity for ARCH-027 SaaS Billing acceptance.

### R3 — Raw body must be available before JSON parsing

The HMAC contract is over the **exact raw request bytes** received from Woo.

The route MUST read/buffer the raw body before any JSON parser, middleware, whitespace normalization, character conversion or object serialization changes it.

Maximum accepted raw body size:

```text
262144 bytes
```

(256 KiB).

If the stream exceeds the bound:

```text
413 webhook_payload_too_large
```

and no receipt is written.

Do not partially parse or persist an oversized body.

### R4 — Content type and content encoding

Require a JSON media type:

```text
application/json
application/json; charset=<...>
```

Case-insensitive media-type parsing is allowed.

Other content types:

```text
415 unsupported_webhook_content_type
```

Require absent or identity content encoding.

Reject compressed/encoded request bodies such as:

```text
gzip
br
deflate
```

with:

```text
415 unsupported_webhook_content_encoding
```

ARCH-027 signature verification is defined over the exact bytes Woo sends; this task does not introduce transparent decompression semantics.

### R5 — Exact Woo signature algorithm

Reuse the API-003 runtime secret:

```text
WOO_BILLING_API_SECRET
```

The expected signature is exactly:

```text
HMAC-SHA256(
    key  = UTF-8 bytes of WOO_BILLING_API_SECRET,
    data = exact raw request-body bytes
)

then standard Base64 encode the 32-byte digest
```

For validation:

1. read the single `X-WC-Webhook-Signature` value;
2. trim only HTTP optional surrounding whitespace;
3. decode as standard Base64;
4. require exactly 32 decoded bytes;
5. compute the expected 32-byte HMAC digest over the exact raw body;
6. compare the two byte buffers using a constant-time comparison.

Do not:

- compare secrets;
- use hexadecimal HMAC strings;
- HMAC a reserialized JSON object;
- HMAC the topic/header set;
- accept a caller-supplied alternative secret.

Missing/malformed/wrong signature:

```text
401 invalid_webhook_signature
```

No receipt is written.

### R6 — Verify signature before trusting topic or JSON semantics

The route may perform transport-level bounds checks before HMAC verification, but it MUST NOT trust or act on:

```text
X-WC-Webhook-Topic
provider contract ID
contract status
transaction/refund amounts
```

until the body signature is valid.

After valid HMAC verification, validate the topic and JSON/provider shape.

This ordering prevents unsigned input from driving provider/billing behavior or database writes.

### R7 — Exact supported Woo SaaS Billing topic allowlist

After signature verification, accept exactly:

```text
saas_billing_contract.activated
saas_billing_contract.updated
saas_billing_contract.renewed
saas_billing_contract.paused
saas_billing_contract.canceled
saas_billing_contract.prepaid_term_ended
saas_billing_contract.refunded
```

The stored `topic` is the exact accepted canonical string above.

A missing/blank topic returns:

```text
400 invalid_webhook_topic
```

A validly signed but unsupported topic returns:

```text
422 unsupported_webhook_topic
```

and no receipt is written.

Do not silently return success for an unsupported provider lifecycle event. A non-2xx response allows Woo retries/monitoring to surface provider-contract drift rather than permanently discarding an unknown event.

### R8 — Minimum signed payload envelope

After signature and topic validation, parse the raw bytes as UTF-8 JSON.

The JSON root must be an object.

Require **exactly one** provider contract wrapper:

```text
subscription
```

or:

```text
charge
```

The selected wrapper must be a JSON object.

Require:

```text
wrapper.id
    non-blank string
    <= 255 UTF-8 characters

wrapper.status
    non-blank string
    <= 64 UTF-8 characters
```

Do not require merchant/customer PII. Woo's documented SaaS billing webhook contract intentionally omits merchant information.

Reject invalid JSON or invalid envelope:

```text
422 invalid_webhook_payload
```

and write no receipt.

### R9 — Topic/contract-kind compatibility

The provider documentation explicitly identifies these as subscription-only topics:

```text
saas_billing_contract.updated
saas_billing_contract.renewed
saas_billing_contract.paused
```

For those topics:

```text
subscription wrapper REQUIRED
charge wrapper REJECTED
```

For:

```text
activated
canceled
prepaid_term_ended
refunded
```

accept either signed contract wrapper and defer the exact business meaning to Background.

Do not map either wrapper into a Moda lifecycle event in API-005.

### R10 — Provider contract ID extraction only

Persist:

```text
providerContractId = wrapper.id
```

This is WooCommerce.com external contract identity.

The ingress route MUST NOT attempt to derive or accept:

```text
shopId
WooCommerceInstallation.id
Subscription.id
RecoveryCreditPurchase.id
merchantPricingPlanId
merchantPricingUsageEventId
```

from provider input.

The route MUST NOT require `providerContractId` already to exist in a local operation/subscription/purchase before durable acceptance.

That is important for provider race/recovery cases. Trusted contract-to-Shop/business-state correlation belongs to Background.

### R11 — Exact raw-body receipt digest

Compute:

```text
payloadSha256 = SHA-256(exact raw request body bytes)
```

Store the raw 32-byte digest.

Do not hash a parsed or reserialized JSON value.

This digest is independent from the HMAC and exists for exact-delivery identity/dedupe.

### R12 — `normalizedPayload` remains Woo provider-shaped

ARCH-027 v1 deliberately introduces no separate Shared normalized lifecycle event.

Persist `normalizedPayload` as the signed Woo contract JSON shape:

For a subscription delivery:

```json
{
  "subscription": { "...Woo signed contract fields..." }
}
```

For a one-time-charge delivery:

```json
{
  "charge": { "...Woo signed contract fields..." }
}
```

Rules:

- retain the selected signed wrapper object as parsed JSON;
- drop unrelated/unknown top-level keys;
- do not rename Woo fields;
- do not convert the topic to a Moda lifecycle enum;
- do not add `shopId`;
- do not add a local operation/purchase identifier;
- do not add credentials/signature/header values;
- do not add raw request bytes/base64;
- do not use the JSONB value later for HMAC verification.

The 256 KiB raw-body limit bounds the persisted provider snapshot.

Background later consumes the Woo-specific provider shape directly and owns semantic validation required by each lifecycle transition.

### R13 — Durable receipt insert

For a new accepted delivery create exactly one:

```text
WooCommerceBillingWebhookReceipt
    topic              = accepted topic
    providerContractId = wrapper.id
    billingOperationId = NULL
    payloadSha256      = SHA-256 exact raw body
    normalizedPayload  = provider-shaped snapshot from R12
    receivedAt         = database/default current time
    processedAt        = NULL
    processingError    = NULL
```

Do not set processing/reconciliation state in API-005 beyond initial receipt creation.

The successful HTTP response MUST NOT be sent until the database commit has succeeded.

### R14 — Exact-delivery dedupe

DATABASE-001 defines exact-delivery uniqueness as:

```text
UNIQUE(topic, payloadSha256)
```

API-005 MUST use that contract.

If two concurrent requests contain the same supported topic and exact raw bytes with valid signatures:

```text
one receipt row
both provider requests receive success
```

On the specific unique conflict for `(topic, payloadSha256)`:

1. re-read the existing receipt by exactly that key;
2. require its `providerContractId` equals the ID deterministically extracted from this signed payload;
3. if it matches, treat the request as an exact duplicate and return success;
4. if it does not match, treat this as durable integrity corruption, log bounded evidence and return non-success.

Do not create a second receipt.

Do not treat semantically equivalent but byte-distinct JSON as duplicate. Different raw bytes legitimately produce different `payloadSha256` values and separate receipts; later reconciliation must remain idempotent.

### R15 — Success acknowledgement

For:

```text
new durably committed receipt
or
verified exact duplicate receipt
```

return exactly:

```text
HTTP 204 No Content
```

with:

```text
Cache-Control: no-store
```

and no response body.

Do not wait for Background reconciliation before acknowledging Woo.

### R16 — Persistence failure must remain retryable by Woo

If the signed payload is valid but durable receipt creation cannot be committed because PostgreSQL is unavailable or another transient storage error occurs:

```text
503 webhook_acceptance_unavailable
```

Do not return 2xx.

Woo treats non-success as failed delivery and may retry. This preserves the durable-acceptance invariant.

Do not enqueue or keep an in-memory fallback receipt.

### R17 — No tenant/business lookup on the ingress hot path

API-005 MUST NOT require any of the following before durable acceptance:

```text
Shop lookup
Subscription lookup
BillingPlan lookup
BillingOperation lookup
RecoveryCreditPurchase lookup
RecoveryCreditRefund lookup
Woo provider GET
```

The ingress hot path is intentionally:

```text
bound
verify
parse minimum envelope
hash
insert receipt
ACK
```

This keeps provider acknowledgement independent from downstream business state and allows Background to handle out-of-order/racing evidence.

### R18 — No business-state mutation

The route MUST NOT modify:

```text
Shop
ShopEntitlementCounter
Subscription
BillingPeriod
BillingPeriodEntitlementCounter
BillingOperation
RecoveryCreditPurchase
RecoveryCreditRefund
UsageEvent
UsageReservation
```

The only business database write owned by API-005 is creation of the webhook receipt row.

An `activated` webhook therefore does **not** synchronously activate either a paid subscription or top-up.

### R19 — No additional transport

After receipt insertion, API-005 MUST NOT:

```text
publish BullMQ
publish Redis
write an outbox event
call Background HTTP
call Woo again
```

The accepted ARCH-027 v1 handoff is PostgreSQL itself:

```text
API writes WooCommerceBillingWebhookReceipt
Background later claims unprocessed rows
```

A future architecture may introduce another transport only if measured operational need justifies it.

### R20 — Provider topic header limitation is not hidden

Woo's documented HMAC covers the request body, while the lifecycle topic is delivered in a separate header.

API-005 must implement the provider protocol exactly; it MUST NOT invent a non-provider signature scheme over the topic.

Security/correctness therefore relies on all of:

- TLS/provider delivery;
- body HMAC validation;
- exact topic allowlist;
- topic/contract-kind compatibility checks;
- exact-delivery dedupe;
- Background state/evidence validation and idempotent transitions.

Do not log `X-WC-Webhook-Signature`, so a valid body/signature pair is not made reusable through application logs.

### R21 — Logging and telemetry

Use the canonical Shared structured logger.

Allowed bounded fields after successful signature verification include:

```text
topic
providerContractId
receiptId
duplicate
safe error code
```

Before successful signature verification, do not log provider contract/body-derived values as trusted identifiers.

Never log:

```text
WOO_BILLING_API_SECRET
X-WC-Webhook-Signature
raw request body
normalized full payload
Authorization headers
installation bearer credentials
Woo API key
payment/customer data
```

Use existing framework/OpenTelemetry HTTP telemetry. Do not add custom generic request-count/duration metrics that duplicate approved instrumentation.

A domain-semantic accepted/duplicate/error log is sufficient for this task unless the repository already has an approved billing webhook metric abstraction to reuse.

### R22 — Error responses are bounded

Provider-facing errors MUST be bounded and contain no payload/provider secrets.

Canonical error codes:

```text
invalid_webhook_signature
webhook_payload_too_large
unsupported_webhook_content_type
unsupported_webhook_content_encoding
invalid_webhook_topic
unsupported_webhook_topic
invalid_webhook_payload
webhook_acceptance_unavailable
webhook_receipt_integrity_error
```

Do not echo:

- raw body;
- signature;
- provider contract payload;
- vendor secret;
- database exception text.

### R23 — OpenAPI/provider documentation

Document the route as provider-to-provider ingress, including:

```text
POST /v1/billing/webhooks/woocommerce
X-WC-Webhook-Signature required
X-WC-Webhook-Topic required
application/json
256 KiB maximum
204 accepted/duplicate
401 invalid signature
413 oversized
415 unsupported media/encoding
422 unsupported topic/invalid payload
503 persistence unavailable
```

The OpenAPI document must not model merchant installation authentication on this route.

Document that business state changes asynchronously after durable receipt acceptance.

## Work Items

- [ ] Add exactly `POST /v1/billing/webhooks/woocommerce`.
- [ ] Ensure the route owns exact raw-body buffering before JSON parsing.
- [ ] Enforce the exact 256 KiB raw body limit.
- [ ] Enforce JSON content type and absent/identity content encoding.
- [ ] Reuse `WOO_BILLING_API_SECRET`; do not add a second webhook secret.
- [ ] Implement exact Woo Base64 HMAC-SHA256 verification over raw bytes.
- [ ] Use constant-time digest comparison and reject malformed/non-32-byte signatures.
- [ ] Require exactly one signature and one topic header value.
- [ ] Add the exact seven-topic SaaS Billing allowlist.
- [ ] Parse only after successful signature verification.
- [ ] Require exactly one `subscription` or `charge` wrapper with bounded non-blank `id` and `status`.
- [ ] Enforce documented subscription-only topic/wrapper compatibility.
- [ ] Extract only external `providerContractId`; do not resolve Shop/business state on ingress.
- [ ] Compute raw 32-byte SHA-256 over exact body bytes.
- [ ] Persist provider-shaped `normalizedPayload` with only the selected root wrapper.
- [ ] Insert one initial unprocessed `WooCommerceBillingWebhookReceipt` with `billingOperationId = NULL`; ingress performs no operation correlation.
- [ ] Implement race-safe exact-delivery dedupe on `(topic, payloadSha256)`.
- [ ] Return `204 No Content` only after commit or verified exact duplicate.
- [ ] Return non-2xx on durable acceptance failure so Woo may retry.
- [ ] Prove no business tables are mutated.
- [ ] Prove no BullMQ/Redis/outbox/Background call occurs after receipt creation.
- [ ] Add bounded structured logs with no signature/body/secret leakage.
- [ ] Update OpenAPI/provider documentation.
- [ ] Add focused signature/raw-body/topic/payload/dedupe/database failure tests.

## Interfaces / Contracts

### Provider HTTP ingress

```text
POST /v1/billing/webhooks/woocommerce

Content-Type: application/json
X-WC-Webhook-Topic: <supported topic>
X-WC-Webhook-Signature: <Base64 HMAC-SHA256>
```

No Moda merchant authentication headers are required.

### Signature contract

Provider-defined external contract:

```text
Base64(
  HMAC-SHA256(
    WOO_BILLING_API_SECRET,
    exact raw request body bytes
  )
)
```

Owner:

WooCommerce Marketplace SaaS Billing provider protocol.

### Durable API -> Background handoff

Owner:

`ARCH-027-DATABASE-001`

Table:

```text
woocommerce.WooCommerceBillingWebhookReceipt
```

Producer:

```text
moda-interact-api / ARCH-027-API-005
```

Consumer:

```text
moda-interact-background / later ARCH-027 Background tasks
```

Durable fields:

```text
topic
providerContractId
billingOperationId = NULL
payloadSha256
normalizedPayload
receivedAt
processedAt
processingError
```

Dedupe:

```text
UNIQUE(topic, payloadSha256)
```

`normalizedPayload` remains Woo provider-shaped and is not a new provider-neutral Shared contract.

### Background transport

ARCH-027 v1 transport is PostgreSQL receipt claiming.

Conceptually later Background processing will select:

```text
processedAt IS NULL
```

using bounded database row locking/claim semantics appropriate to the existing Background reconciliation patterns.

No queue contract is created by API-005.

## Dependencies

- `ARCH-027-API-004`

API-004 must be architect-accepted Complete before API-005 becomes Ready so this same repository task can reuse the accepted:

- `WOO_BILLING_API_SECRET` configuration;
- service runtime/router structure;
- database client conventions;
- structured logging/correlation conventions;
- Woo billing environment separation.

Through API-004's dependency chain, the task also relies on the accepted ARCH-027 database receipt schema.

## Enables

- `ARCH-027-BACKGROUND-001`

The first Background task may consume durably accepted Woo receipts only after this ingress contract is accepted.

## Acceptance Criteria

- [ ] Exactly `POST /v1/billing/webhooks/woocommerce` is implemented.
- [ ] Route does not require Woo installation bearer authentication.
- [ ] Route accepts no caller-supplied tenant identity.
- [ ] Raw body is read exactly once and HMAC-verified before JSON parsing.
- [ ] Raw body larger than 262144 bytes is rejected with no receipt.
- [ ] Non-JSON content type is rejected.
- [ ] Non-identity content encoding is rejected.
- [ ] Missing, malformed or incorrect signature is rejected with no receipt.
- [ ] Signature algorithm is standard Base64 HMAC-SHA256 over exact raw bytes using `WOO_BILLING_API_SECRET`.
- [ ] Signature comparison is constant-time after exact digest-length validation.
- [ ] Exactly the seven documented SaaS Billing topics are accepted.
- [ ] Unsupported validly signed topics are non-2xx and are not silently discarded.
- [ ] Exactly one `subscription` or `charge` provider wrapper is required.
- [ ] Provider contract `id` and `status` are non-blank and bounded.
- [ ] `updated`, `renewed` and `paused` reject a `charge` wrapper.
- [ ] `providerContractId` comes only from the signed wrapper `id`.
- [ ] No Shop/Subscription/operation/purchase lookup is required for durable acceptance.
- [ ] `payloadSha256` is SHA-256 of exact raw body bytes.
- [ ] `normalizedPayload` remains Woo provider-shaped and contains only the selected signed wrapper.
- [ ] New valid delivery creates exactly one receipt with `processedAt = NULL` and `processingError = NULL`.
- [ ] Exact concurrent duplicate deliveries create one row and both receive 204.
- [ ] Duplicate detection is exactly `(topic, payloadSha256)`.
- [ ] Byte-distinct semantically equivalent payloads remain separately receipted.
- [ ] Provider response is exactly `204 No Content` after successful commit or verified exact duplicate.
- [ ] PostgreSQL acceptance failure returns non-2xx/503 and does not acknowledge durable success.
- [ ] No business-state table is mutated.
- [ ] No queue/outbox/background HTTP handoff is emitted.
- [ ] No secret, signature or raw/full payload is logged.
- [ ] OpenAPI documents provider ingress without merchant auth.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect `moda-interact-api/package.json` and accepted API-004 implementation before choosing exact commands. The supplied pre-task snapshot currently declares `test`, `typecheck`, `lint` and `build`; use the actual accepted repository state rather than assuming it remains identical.

Required validation categories:

- [ ] repository-declared focused/unit tests;
- [ ] repository typecheck;
- [ ] repository lint or changed-file lint;
- [ ] repository production build when required by repository instructions;
- [ ] exact known-body/known-secret signature acceptance vector;
- [ ] one-byte body mutation with old signature -> invalid signature;
- [ ] whitespace-different body with independently valid signature -> independently receipted raw digest;
- [ ] malformed Base64 signature rejection;
- [ ] decoded signature wrong length rejection;
- [ ] duplicate signature header rejection;
- [ ] duplicate topic header rejection;
- [ ] missing signature/topic tests;
- [ ] body limit exact-bound and over-bound tests;
- [ ] non-JSON content-type rejection;
- [ ] compressed content-encoding rejection;
- [ ] all seven allowed topics positive tests;
- [ ] unsupported topic negative test;
- [ ] invalid JSON negative test after valid HMAC;
- [ ] root-not-object negative test;
- [ ] neither-wrapper negative test;
- [ ] both-wrappers negative test;
- [ ] blank/oversized contract ID negative tests;
- [ ] blank/oversized status negative tests;
- [ ] `activated` subscription positive test;
- [ ] `activated` charge positive test;
- [ ] `updated`/`renewed`/`paused` subscription positive tests;
- [ ] `updated`/`renewed`/`paused` charge negative tests;
- [ ] canceled/refunded provider wrapper coverage;
- [ ] exact `payloadSha256` byte-vector test;
- [ ] receipt provider-shape persistence test;
- [ ] exact duplicate receipt idempotency test;
- [ ] concurrent duplicate insert race test;
- [ ] same topic + different raw-body hash creates distinct receipts;
- [ ] same raw body + different supported topic follows `(topic, hash)` database contract;
- [ ] database unavailable/commit failure -> non-2xx and zero durable receipt;
- [ ] accepted receipt has null `processedAt`/`processingError`;
- [ ] negative assertion proving no Shop/Subscription/BillingPeriod/operation/purchase/refund/counter mutation;
- [ ] negative assertion proving no Redis/BullMQ/outbox/background call;
- [ ] structured-log redaction test for secret/signature/raw payload;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, synchronization, branch and push evidence in the Completion Report.

Real Woo sandbox execution is not required for API-005. The later Gateway/system-test/sandbox work verifies the actual public callback URL and provider delivery.

## Stop Condition

After all defined Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
    -> set task status to review
    -> return to moda_architect
    -> STOP
```

Do not begin Background receipt processing, Woo UI, Gateway deployment or sandbox certification.

## Implementation Notes

Keep this route intentionally small.

The preferred shape is:

```text
HTTP raw bytes
    -> transport bounds
    -> HMAC
    -> minimum provider envelope
    -> durable receipt
    -> 204
```

Do not move provider business interpretation into the request lifecycle merely because the payload is already parsed.

The later Background implementation should be able to change reconciliation logic without changing the public webhook authenticity/durable-acceptance boundary.

The `X-WC-Webhook-Topic` header is part of Woo's provider protocol but is not part of the documented body HMAC. API-005 must not pretend otherwise. Correctness must therefore also depend on Background validating each requested state transition against durable Moda operation/subscription/purchase state.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- API-004 has established accepted Woo billing configuration/runtime conventions.
- Woo continues to sign SaaS Billing webhook bodies with the application API secret using Base64 HMAC-SHA256.
- Woo's documented SaaS Billing webhook root contains a `subscription` or `charge` contract snapshot.
- PostgreSQL is the accepted durable API -> Background handoff for ARCH-027 v1.

### Unresolved Issues

- Real Woo sandbox delivery/header/payload behavior remains to be certified later.
- Background topic semantics, receipt claiming/retry state and business reconciliation are intentionally outside API-005.
- `OUTCOME_UNKNOWN` provider-create recovery beyond later provider evidence/manual inspection remains a separate architectural concern.

### Architectural Concerns

Woo's documented signature authenticates the request body while the lifecycle topic is supplied separately in a header. API-005 follows that provider protocol exactly and does not invent a stronger non-provider signature. Background must therefore validate topic-driven transitions against durable state and remain idempotent.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
