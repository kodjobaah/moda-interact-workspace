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
| SHOPIFY-003 | Add OpenTelemetry to Shopify ingress | Ready | GATEWAY-001 |
| SHOPIFY-004 | Use published shared package in Shopify application | Ready | GATEWAY-001 |

Environment model:

```text
render.test.yaml
render.production.yaml
```

The same application health/start/build/package contracts must support both
deployed environments; environment-specific state/secrets are supplied by
infrastructure.

The individual task file is authoritative for task state.
