# ARCH-023 gateway tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge.md).

Assigned agent: `moda_gateway`.

Repository: `moda-interact-gateway`.

Coordinator: `moda_architect`.

ARCH-023 requires one infrastructure/deployment task:

```text
BACKGROUND-005 -> BACKGROUND-008 --+
SHOPIFY-005 ------------------------+--> GATEWAY-001
COMMERCE-002 -----------------------+
```

Individual task YAML is authoritative.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [GATEWAY-001](GATEWAY-001-wire-merchant-knowledge-deployment.md) | Deploy the dedicated Merchant Knowledge worker and wire private R2, upload limits, embeddings and Commerce bootstrap configuration | Complete — Accepted Attempt 2 | BACKGROUND-005, BACKGROUND-008, SHOPIFY-005, COMMERCE-002 |

## Deployment boundary

Gateway owns:

```text
Render test/production topology
dedicated Merchant Knowledge worker service
Redis/PostgreSQL wiring
private R2 configuration/credential placement and exact-origin create-only browser PUT CORS prerequisite
upload-limit placement
embedding configuration placement
Commerce bootstrap-admin environment
deployment/rollback documentation
Blueprint validation
```

Gateway does **not** own:

```text
application business logic
Merchant Knowledge Feature/plan provisioning
PlatformAdmin creation
R2 upload/read implementation
embedding implementation
Commerce bootstrap implementation
system tests
```

## Execution frontier

`ARCH-023-GATEWAY-001` is Complete / Accepted Attempt 2. Static Blueprint, topology, secret-hygiene and observability validation passed. Live Render deployment and real-origin R2 CORS/create-only PUT evidence are intentionally deferred to developer/manual validation and `ARCH-023-SYSTEM-TEST-002`; they are not represented as already executed.

Gateway acceptance completes the final declared dependency of `ARCH-023-SYSTEM-TEST-002`, which is now Ready and may remain unclaimed while the developer performs the documented deployed-environment checks.

## No new HTTP service

ARCH-023 adds no Merchant Knowledge web/private service and no new Gateway route.

The deployed data paths remain:

```text
Shopify app -> PostgreSQL / BullMQ / private R2
Background Merchant Knowledge worker -> Redis / PostgreSQL / private R2 / embedding provider
Commerce -> PostgreSQL / embedding provider
```

## Browser upload CORS

GATEWAY-001 documents the private Cloudflare R2 bucket CORS policy required by SHOPIFY-005; live deployed-origin verification is deferred to developer/manual validation and SYSTEM-TEST-002: exact deployed Moda Shopify application origin(s), `PUT`, `Content-Type` plus `If-None-Match`, no wildcard origin and no public read/list exposure. It must also prove a create-only signed PUT succeeds once and replay to the same generated key is rejected without replacing the immutable object.
