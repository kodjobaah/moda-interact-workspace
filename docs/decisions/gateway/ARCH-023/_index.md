# ARCH-023 gateway tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge.md).

Assigned agent: `moda_gateway`.

Repository: `moda-interact-gateway`.

Coordinator: `moda_architect`.

ARCH-023 requires one infrastructure/deployment task:

```text
BACKGROUND-005
SHOPIFY-005
COMMERCE-002
      \ | /
       \|/
 GATEWAY-001
```

Individual task YAML is authoritative.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [GATEWAY-001](GATEWAY-001-wire-merchant-knowledge-deployment.md) | Deploy the dedicated Merchant Knowledge worker and wire private R2, upload limits, embeddings and Commerce bootstrap configuration | Ready | BACKGROUND-005, SHOPIFY-005, COMMERCE-002 |

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

Ready: `ARCH-023-GATEWAY-001`.

All declared prerequisites are now Complete / architect-accepted:

```text
ARCH-023-BACKGROUND-005 = Complete — Accepted Attempt 2
ARCH-023-SHOPIFY-005    = Complete — Accepted Attempt 3
ARCH-023-COMMERCE-002   = Complete — Accepted Attempt 4
```

The task remains unclaimed. Start it only through the normal `/moda-task ARCH-023-GATEWAY-001` launcher.

## No new HTTP service

ARCH-023 adds no Merchant Knowledge web/private service and no new Gateway route.

The deployed data paths remain:

```text
Shopify app -> PostgreSQL / BullMQ / private R2
Background Merchant Knowledge worker -> Redis / PostgreSQL / private R2 / embedding provider
Commerce -> PostgreSQL / embedding provider
```

## Browser upload CORS

GATEWAY-001 must document and verify the private Cloudflare R2 bucket CORS policy required by SHOPIFY-005: exact deployed Moda Shopify application origin(s), `PUT`, `Content-Type` plus `If-None-Match`, no wildcard origin and no public read/list exposure. It must also prove a create-only signed PUT succeeds once and replay to the same generated key is rejected without replacing the immutable object.
