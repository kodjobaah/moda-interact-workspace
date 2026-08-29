# ARCH-002 Shopify Tasks

Architecture:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Assigned Agent:

`moda_app`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| SHOPIFY-001 | Add Shopify service health and readiness | Ready | GATEWAY-001 |
| SHOPIFY-002 | Separate database setup from replica startup | Ready | GATEWAY-001 |
| SHOPIFY-003 | Add OpenTelemetry to Shopify ingress | Ready | GATEWAY-001 |

The individual task file is authoritative for task state.
