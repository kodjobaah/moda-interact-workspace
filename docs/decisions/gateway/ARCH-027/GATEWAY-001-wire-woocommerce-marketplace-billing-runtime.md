---
id: ARCH-027-GATEWAY-001
architecture_id: ARCH-027
title: Wire WooCommerce Marketplace billing runtime and webhook ingress
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 100
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-GATEWAY-001
  - ARCH-027-API-005
enables: []
created: 2026-10-04
updated: 2026-10-09
---

# Wire WooCommerce Marketplace billing runtime and webhook ingress

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Add the **minimum infrastructure wiring** required for the already-existing private `moda-interact-api` service to execute Woo Marketplace SaaS Billing commands and receive signed Woo billing webhooks.

ARCH-026 already owns:

```text
public API host
    -> public moda-interact-gateway
    -> private moda-interact-api
```

with canonical hosts:

```text
test:
    api-test.modainteract.com

production:
    api.modainteract.com
```

ARCH-027 therefore does **not** create:

```text
a second API service
a billing-specific public service
a second gateway host
a webhook microservice
a billing reverse proxy
```

This task adds only:

```text
environment-isolated Woo billing runtime configuration
    +
secret injection into the private API service only
    +
explicit proof that the existing API-host routing preserves
Woo webhook signature headers and raw body bytes
    +
deployment/runbook instructions for the provider webhook URL
```

The final network path remains:

```text
WooCommerce.com
        |
        | HTTPS
        | X-WC-Webhook-Topic
        | X-WC-Webhook-Signature
        | exact raw JSON body
        v
api-test.modainteract.com
or
api.modainteract.com
        |
        v
moda-interact-gateway
        |
        | existing API_PUBLIC_HOST exact-host routing
        | no body/header transformation
        v
private moda-interact-api
        |
        v
POST /v1/billing/webhooks/woocommerce
```

Provider command traffic uses the same private API service:

```text
moda-interact-api
    -> https://sandbox.woocommerce.com/...   (test)
    -> https://woocommerce.com/...           (production)
```

## Context

### ARCH-026 already deploys/routes the hosted API

`ARCH-026-GATEWAY-001` owns the existing:

```text
moda-interact-api-test
moda-interact-api-production

API_PUBLIC_HOST
MODA_API_UPSTREAM

api-test.modainteract.com
api.modainteract.com
```

topology.

ARCH-027 MUST consume that accepted topology rather than duplicating it.

### ARCH-027 API runtime configuration is already fixed

API-003 defines exactly:

```text
WOO_BILLING_ENVIRONMENT = sandbox | production
WOO_BILLING_API_KEY
WOO_BILLING_API_SECRET
```

and derives provider base URLs in application code:

```text
sandbox:
    https://sandbox.woocommerce.com/wp-json/wccom/billing/1.0/

production:
    https://woocommerce.com/wp-json/wccom/billing/1.0/
```

The Gateway MUST NOT provide an arbitrary provider base URL.

API-004 reuses the same command credentials for `/charges`.

API-005 reuses:

```text
WOO_BILLING_API_SECRET
```

as the Woo webhook HMAC secret.

There is intentionally **one Woo billing application secret per environment runtime**, not a second webhook-only secret.

### Webhook ingress contract

API-005 exposes exactly:

```text
POST /v1/billing/webhooks/woocommerce
```

and authenticates:

```text
Base64(
  HMAC-SHA256(
    WOO_BILLING_API_SECRET,
    exact raw request body bytes
  )
)
```

from:

```text
X-WC-Webhook-Signature
```

with lifecycle topic in:

```text
X-WC-Webhook-Topic
```

Therefore Gateway correctness depends on **byte-for-byte request-body preservation** and transparent forwarding of those headers.

The Gateway must not parse, decompress, canonicalize or reserialize the webhook body.

### Existing Gateway request-body limits

The Gateway already owns a general:

```text
CLIENT_MAX_BODY_SIZE
```

ceiling and API-005 owns its route-specific:

```text
262144 bytes
```

limit.

ARCH-027 MUST NOT add a smaller gateway-specific Woo webhook limit.

The Gateway can pass requests larger than 256 KiB to the private API; API-005 remains authoritative for returning the route-specific `413`.

## Scope

Modify only `moda-interact-gateway` infrastructure/configuration/tests/documentation required for Woo billing configuration and existing API-host webhook transport validation.

Expected files include:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml

moda-interact-gateway/tests/run-tests.sh
moda-interact-gateway/tests/fixtures/upstream.py
moda-interact-gateway/tests/validate-render-blueprints.sh
moda-interact-gateway/tests/validate-render-blueprints-negative.sh

moda-interact-gateway/docs/render-topology.md
moda-interact-gateway/docs/deployment-prerequisites.md
moda-interact-gateway/docs/woocommerce-billing-deployment.md
```

`haproxy/haproxy.cfg` and `docker/entrypoint.sh` should remain unchanged **unless** the accepted ARCH-026 API-host implementation is missing a behavior required below.

Do not make cosmetic routing changes merely because ARCH-027 exists.

## Out of Scope

- Deploying another `moda-interact-api`.
- Changing API public hostnames.
- Changing `MODA_API_UPSTREAM`.
- Adding another public custom domain.
- API business logic.
- API webhook HMAC implementation.
- Background receipt reconciliation.
- Woo plugin code.
- Admin code.
- Database schema/migrations.
- Redis/BullMQ.
- Woo vendor-dashboard configuration mutation.
- Live Render deployment.
- Live DNS changes.
- Creating/rotating real secret values.
- Woo sandbox certification.
- Rate limiting/WAF/API-management products.
- Browser CORS expansion.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Exact environment groups

Add exactly one Woo billing environment group per Render environment.

Test:

```text
moda-interact-test-woo-billing-config
```

Production:

```text
moda-interact-production-woo-billing-config
```

Do not reuse Shopify provider credential groups.

### R2 — Exact test group contract

Test group contains exactly these ARCH-027 Woo billing keys:

```yaml
- key: WOO_BILLING_ENVIRONMENT
  value: sandbox

- key: WOO_BILLING_API_KEY
  sync: false

- key: WOO_BILLING_API_SECRET
  sync: false
```

Rules:

- `WOO_BILLING_ENVIRONMENT` is committed non-secret configuration;
- the key/secret values are Render-managed placeholders only;
- no fixed placeholder value is committed for the key/secret;
- no production Woo value appears in the test group.

### R3 — Exact production group contract

Production group contains exactly:

```yaml
- key: WOO_BILLING_ENVIRONMENT
  value: production

- key: WOO_BILLING_API_KEY
  sync: false

- key: WOO_BILLING_API_SECRET
  sync: false
```

No sandbox environment value appears in the production group.

### R4 — Attach Woo billing config only to private API service

Attach:

```text
moda-interact-test-woo-billing-config
```

only to:

```text
moda-interact-api-test
```

Attach:

```text
moda-interact-production-woo-billing-config
```

only to:

```text
moda-interact-api-production
```

Do not attach either group to:

```text
moda-interact-gateway
moda-interact
moda-interact-admin
moda-interact-background workers
moda-interact-commerce
moda-interact-messaging
merchant-knowledge worker
```

The WordPress plugin receives none of these values through Gateway infrastructure.

### R5 — API service remains private

ARCH-027 must not change the accepted API service from:

```text
Render private service
```

to:

```text
public web service
```

The API service itself receives no custom domain.

Public ingress remains the ARCH-026 Gateway.

### R6 — Reuse the existing API host

Webhook URLs are exactly:

```text
test:
https://api-test.modainteract.com/v1/billing/webhooks/woocommerce

production:
https://api.modainteract.com/v1/billing/webhooks/woocommerce
```

Do not add:

```text
billing-test.modainteract.com
billing.modainteract.com
webhooks.modainteract.com
```

or another host.

### R7 — No new HAProxy path routing is required

The accepted ARCH-026 API host routes:

```text
API_PUBLIC_HOST/*
    -> private moda-interact-api
```

Therefore:

```text
/v1/billing/webhooks/woocommerce
```

must naturally traverse the existing API backend.

Do not add a webhook-specific backend/path rewrite when the existing host routing already satisfies this.

If source inspection proves the accepted API-host routing is narrower than the ARCH-026 contract, correct only the minimum defect and document the deviation.

### R8 — Preserve Woo signature headers transparently

Gateway tests must prove these inbound headers reach the private API upstream unchanged:

```text
X-WC-Webhook-Topic
X-WC-Webhook-Signature
```

Header-name casing may follow normal HTTP/HAProxy semantics; header values must be unchanged.

Do not:

```text
strip
rewrite
log secret signature values
interpret topic values
```

### R9 — Preserve exact webhook body bytes

Add a controlled Gateway test that sends a non-trivial JSON body through:

```text
Host: API_PUBLIC_HOST
POST /v1/billing/webhooks/woocommerce
```

and proves the fixture upstream receives exactly the same bytes by comparing:

```text
base64(raw body)
SHA-256(raw body)
provider-style HMAC-SHA256(raw body)
```

The test must include whitespace/newlines/order-sensitive JSON bytes so reserialization would be detected.

Reuse the existing upstream fixture raw-body/HMAC support where possible.

### R10 — API host remains transparent for webhook content type

Gateway must transparently pass:

```text
Content-Type: application/json
```

without body parsing.

Do not add transparent decompression or content transformation.

API-005 owns:

```text
JSON media-type validation
identity content-encoding requirement
256 KiB body bound
```

### R11 — Do not add a smaller Woo webhook body limit in Gateway

The existing global Gateway request ceiling remains authoritative at infrastructure level.

Require the Gateway configuration used for API host traffic to permit at least:

```text
262144 bytes
```

so API-005 can enforce its own exact limit.

Do not add:

```text
API host body limit = 256 KiB
```

in HAProxy because that would duplicate application policy and can interfere with exact route-level behavior.

A Gateway test should prove a body at the API-005 maximum is not rejected by Gateway due solely to Gateway size policy.

### R12 — No public browser CORS expansion

Do not add:

```text
Access-Control-Allow-Origin: *
```

or other permissive browser CORS for the API host.

The merchant browser architecture remains:

```text
browser -> local WordPress REST -> PHP -> API host
```

The public Woo webhook does not require browser CORS.

### R13 — Do not expose vendor secrets through Gateway environment

The public Gateway service MUST NOT receive:

```text
WOO_BILLING_API_KEY
WOO_BILLING_API_SECRET
WOO_BILLING_ENVIRONMENT
```

The secrets/config belong only to private `moda-interact-api`.

### R14 — Do not expose Woo billing credentials to Background

Background reconciles signed durable database receipts and never calls Woo provider APIs in ARCH-027.

Therefore Background service groups MUST NOT receive:

```text
WOO_BILLING_API_KEY
WOO_BILLING_API_SECRET
```

### R15 — Positive Blueprint validation

Extend canonical Blueprint validation to prove in **both** environments:

1. exact Woo billing group name exists;
2. exact three keys exist;
3. environment value is correct:
   - test `sandbox`;
   - production `production`;
4. key/secret use `sync:false` with no committed `value`;
5. group is attached to exactly the environment's private API service;
6. group is not attached to any other service;
7. API remains private;
8. API public domain remains owned by Gateway, not API service;
9. existing API upstream/host wiring remains intact.

### R16 — Negative Blueprint validation

Add deterministic rejected fixtures for at least:

```text
missing Woo billing group
wrong WOO_BILLING_ENVIRONMENT
test group uses production
production group uses sandbox
missing WOO_BILLING_API_KEY
missing WOO_BILLING_API_SECRET
hardcoded Woo API key
hardcoded Woo API secret
Woo group attached to Gateway
Woo group attached to Background
Woo group attached to WordPress/Shopify app service
test Woo group attached to production API
production Woo group attached to test API
Woo config attached to public/non-API service
API made public
```

Negative validators must fail for the intended reason.

### R17 — Gateway runtime route test uses API host

Extend runtime Gateway tests so the API host proves:

```text
POST /v1/billing/webhooks/woocommerce
    -> API upstream fixture
```

without path rewrite.

Also preserve existing assertions for:

```text
unknown-host rejection
gateway-local /health
other service hosts
```

ARCH-027 must not break existing routing.

### R18 — Gateway-local `/health` remains local

For the API host:

```text
GET /health
```

continues to return Gateway liveness rather than proxying to API.

API application health remains:

```text
GET /health/live
GET /health/ready
```

through the API host.

### R19 — Deployment documentation fixes exact provider webhook URLs

Add:

```text
docs/woocommerce-billing-deployment.md
```

documenting:

```text
test provider webhook:
https://api-test.modainteract.com/v1/billing/webhooks/woocommerce

production provider webhook:
https://api.modainteract.com/v1/billing/webhooks/woocommerce
```

Make clear:

- configure the matching environment's Woo SaaS application/webhook with that URL;
- do not point Woo to a merchant WordPress site;
- do not point Woo directly to Render private service hostnames;
- the webhook uses the same `WOO_BILLING_API_SECRET` configured for that environment's API runtime.

Do not include real secret values.

### R20 — Document secret provisioning without performing it

Operator prerequisites:

Test:

```text
Render env group:
moda-interact-test-woo-billing-config

WOO_BILLING_API_KEY     = Woo sandbox application key
WOO_BILLING_API_SECRET  = Woo sandbox application secret
```

Production:

```text
Render env group:
moda-interact-production-woo-billing-config

WOO_BILLING_API_KEY     = Woo production application key
WOO_BILLING_API_SECRET  = Woo production application secret
```

Secret creation/rotation is an operator/provider action, not committed code.

### R21 — Safe deployment order

Document:

```text
1. ARCH-026 API/Gateway topology is already deployed.
2. Required ARCH-027 database migrations are applied.
3. Deploy accepted ARCH-027 API command/webhook implementation.
4. Provision the environment-specific Woo billing key/secret in Render.
5. Deploy/update private moda-interact-api with the Woo billing env group.
6. Verify API /health/live and /health/ready through the existing API host.
7. Configure the matching Woo SaaS application webhook URL.
8. Exercise controlled signed webhook transport.
9. Only then run real Woo sandbox billing certification.
10. Production credentials/webhook are provisioned only for production rollout.
```

Do not require a Gateway redeploy for every application-only API change once the env topology is accepted.

### R22 — Logs/observability remain secret-safe

No Gateway config/test/documentation may log/commit:

```text
Woo API key
Woo API secret
X-WC-Webhook-Signature value in production logs
Authorization headers
raw payment/customer data
```

Test fixtures may use clearly fake deterministic HMAC values/secrets.

### R23 — Existing topology remains unchanged

Shopify, Admin, Messaging, Commerce, Merchant Knowledge and workers retain their existing routing/env-group behavior.

This task is additive only.

## Work Items

- [ ] Add exact test Woo billing env group.
- [ ] Add exact production Woo billing env group.
- [ ] Attach each group only to its private environment-specific API service.
- [ ] Add positive Blueprint validation for exact key/value/secret/group/service wiring.
- [ ] Add negative Blueprint fixtures for missing/wrong/hardcoded/cross-environment/leaked Woo billing config.
- [ ] Add API-host Woo webhook runtime routing test.
- [ ] Add `X-WC-Webhook-Topic` / `X-WC-Webhook-Signature` forwarding test.
- [ ] Add exact raw-body/base64/SHA-256/HMAC preservation test through API host.
- [ ] Prove API-005 max-size payload is not rejected by a smaller Gateway host-specific rule.
- [ ] Preserve Gateway-local `/health`, API `/health/live` and `/health/ready` behavior.
- [ ] Add Woo billing deployment/runbook documentation with exact test/production webhook URLs.
- [ ] Document environment-specific secret provisioning and safe deployment order.
- [ ] Verify no CORS expansion, new public service/domain, Woo credential leakage or business logic is introduced.

## Interfaces / Contracts

### Existing public API hosts

Owner:

`ARCH-026-GATEWAY-001`

```text
https://api-test.modainteract.com
https://api.modainteract.com
```

### Existing private API services

```text
moda-interact-api-test
moda-interact-api-production
```

### New environment groups

```text
moda-interact-test-woo-billing-config
moda-interact-production-woo-billing-config
```

### API runtime keys

Owner:

`ARCH-027-API-003`

```text
WOO_BILLING_ENVIRONMENT
WOO_BILLING_API_KEY
WOO_BILLING_API_SECRET
```

### Public Woo webhook

Owner:

`ARCH-027-API-005`

```text
POST /v1/billing/webhooks/woocommerce
```

Public URLs:

```text
https://api-test.modainteract.com/v1/billing/webhooks/woocommerce
https://api.modainteract.com/v1/billing/webhooks/woocommerce
```

Gateway transports the request but does not authenticate/interpret it.

## Dependencies

- `ARCH-026-GATEWAY-001`
- `ARCH-027-API-005`

ARCH-026-GATEWAY-001 must be architect-accepted Complete because ARCH-027 reuses its API service/host topology.

API-005 must be architect-accepted Complete because this task must validate the exact accepted public webhook path and raw-body/header requirements.

Through API-005's dependency chain, API-003's exact Woo runtime keys are fixed.

## Enables

None yet.

Expected follow-ons:

```text
ARCH-027 Shopify regression/compatibility validation
ARCH-027 integrated system/mock validation
ARCH-027 Woo sandbox certification
```

System/sandbox tasks remain terminal and are not implementation dependencies.

## Acceptance Criteria

- [ ] Exactly one Woo billing env group exists per environment with the specified names.
- [ ] Test uses `WOO_BILLING_ENVIRONMENT=sandbox`.
- [ ] Production uses `WOO_BILLING_ENVIRONMENT=production`.
- [ ] Woo API key/secret are `sync:false` with no committed values.
- [ ] Woo billing group is attached only to the environment's private `moda-interact-api` service.
- [ ] Gateway, Background, Shopify app, Admin, Commerce, Messaging and WordPress receive no Woo vendor credentials.
- [ ] No second API/billing/webhook service or public host is introduced.
- [ ] Existing `api-test.modainteract.com` / `api.modainteract.com` hosts remain authoritative.
- [ ] `/v1/billing/webhooks/woocommerce` reaches the API upstream without path rewrite.
- [ ] `X-WC-Webhook-Topic` value is preserved.
- [ ] `X-WC-Webhook-Signature` value is preserved.
- [ ] Exact webhook raw body bytes are preserved through Gateway.
- [ ] Gateway introduces no smaller Woo-specific request-body limit than API-005's 256 KiB application limit.
- [ ] Gateway-local `/health` remains local on the API host.
- [ ] API `/health/live` and `/health/ready` remain routable through the API host.
- [ ] No permissive CORS is added.
- [ ] Positive Blueprint validation proves exact environment isolation/secret attachment.
- [ ] Negative Blueprint validation catches all specified credential leakage/cross-environment/public-service mistakes.
- [ ] Deployment documentation includes exact test/production webhook URLs and secret provisioning sequence.
- [ ] No real secret values are committed.
- [ ] Existing Gateway routing/topology validation remains green.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect the accepted Gateway repository scripts after ARCH-026 implementation before selecting exact commands.

Required categories:

- [ ] `tests/validate-render-blueprints.sh`;
- [ ] `tests/validate-render-blueprints-negative.sh`;
- [ ] `tests/validate-observability-config.sh`;
- [ ] full Gateway runtime test suite `tests/run-tests.sh`;
- [ ] Ruby/Psych parse of both canonical Render Blueprints;
- [ ] exact Woo billing env-group positive tests in both environments;
- [ ] missing-group negative test;
- [ ] wrong sandbox/production environment value negative tests;
- [ ] missing-key/missing-secret negative tests;
- [ ] hardcoded API key/secret negative tests;
- [ ] Woo billing group attached to Gateway negative test;
- [ ] Woo billing group attached to Background negative test;
- [ ] Woo billing group attached to non-API public service negative test;
- [ ] test/production Woo group crossover negative tests;
- [ ] API private-service/public-domain regression test;
- [ ] API-host Woo webhook route test;
- [ ] exact Woo topic/signature header forwarding test;
- [ ] exact raw body base64/SHA-256/HMAC preservation test;
- [ ] 262144-byte API-host body is not rejected by a smaller Gateway-specific rule;
- [ ] Gateway `/health` local behavior regression test;
- [ ] API health-path routing regression tests;
- [ ] unknown-host rejection regression;
- [ ] existing Shopify/Messaging/Admin/Commerce routing tests remain green;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, start-of-attempt synchronization and pushed task-branch evidence.

No live Render deployment, real credential value or Woo sandbox call is required for this implementation task.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete:

```text
finish Completion Report
    -> status: review
    -> return to moda_architect
    -> STOP
```

Do not begin system/sandbox validation.

## Implementation Notes

This task should be much smaller than ARCH-026-GATEWAY-001.

ARCH-026 already solved:

```text
public API host
private API service
HAProxy exact-host routing
DNS/TLS topology
```

ARCH-027 adds:

```text
Woo billing environment
Woo vendor secret attachment
proof of transparent signed webhook transport
provider webhook deployment documentation
```

Do not duplicate the existing API topology merely to make Woo billing feel separate.

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

- ARCH-026-GATEWAY-001 is accepted and the private API/public API-host topology exists.
- API-003/API-005 use exactly the three documented Woo billing runtime variables.
- Existing Gateway API-host routing forwards arbitrary API paths and raw request bodies transparently.
- Render env-group `sync:false` remains the accepted secret-provisioning mechanism.

### Unresolved Issues

- Real Woo sandbox credential provisioning and provider webhook registration remain external deployment/certification actions.
- Real provider delivery/signature behavior remains a later sandbox/system-test gate.

### Architectural Concerns

None.

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
