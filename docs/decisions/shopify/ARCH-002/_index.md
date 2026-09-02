# ARCH-002 Shopify Tasks

Architecture:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Assigned Agent:

`moda_app`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| SHOPIFY-001 | Add Shopify service health and readiness | Complete | GATEWAY-001 |
| SHOPIFY-002 | Separate database setup from replica startup | Complete | GATEWAY-001 |
| SHOPIFY-003 | Add OpenTelemetry to Shopify ingress | Superseded | Replaced by SHOPIFY-006/007 |
| SHOPIFY-004 | Use published shared package in Shopify application | Complete | GATEWAY-001 |
| SHOPIFY-005 | Eliminate existing Shopify application TypeScript baseline debt | Ready | SHOPIFY-002 |
| SHOPIFY-006 | Adopt shared observability runtime in Shopify process | Complete | GATEWAY-001, SHARED-010 |
| SHOPIFY-007 | Wire shared BullMQ telemetry on Shopify queue producers | Complete | SHOPIFY-006 |

Environment model:

```text
render.test.yaml
render.production.yaml
```

The same application health/start/build/package contracts must support both
deployed environments; environment-specific state/secrets are supplied by
infrastructure.

The individual task file is authoritative for task state.

## Shared Observability Amendment

`SHOPIFY-003` is pending on `SHARED-010`. It must consume the exact published
shared Node runtime and BullMQ adapter instead of maintaining service-local
NodeSDK/provider/exporter plumbing. Shopify-specific semantic telemetry remains
owned by `moda_app`.


## SHOPIFY-004 architect acceptance

`ARCH-002-SHOPIFY-004` is architect-accepted Complete.

The Shopify application uses the exact published shared-package dependency:

```text
@modainteract/moda-interact-shared@0.4.0
```

with registry-backed lockfile resolution and no sibling `file:` dependency.

This satisfies the `SHOPIFY-004` dependency edge for `GATEWAY-005`.

No downstream task is automatically promoted or started.
