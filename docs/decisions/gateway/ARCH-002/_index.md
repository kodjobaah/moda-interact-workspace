# ARCH-002 Gateway Tasks

Architecture:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Assigned Agent:

`moda_gateway`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| GATEWAY-001 | Inspect platform and define deployment prerequisites | Complete | - |
| GATEWAY-002 | Create public Moda Interact gateway | Complete | GATEWAY-001 |
| GATEWAY-007 | Implement host-based admin gateway routing | Pending | GATEWAY-002, ADMIN-008 |
| GATEWAY-005 | Validate npm-based shared package production builds | Pending | GATEWAY-001, SHOPIFY-004, BACKGROUND-004 |
| GATEWAY-006 | Configure OpenTelemetry transport/environment wiring | Ready | GATEWAY-002, SHOPIFY-007, MESSAGING-004, MESSAGING-005, ADMIN-009, BACKGROUND-007, BACKGROUND-009 |
| GATEWAY-003 | Create Render test and production deployment topology | Pending | GATEWAY-002, GATEWAY-005, GATEWAY-006, GATEWAY-007, SHOPIFY-001, SHOPIFY-002, MESSAGING-001, ADMIN-001, ADMIN-003, BACKGROUND-001, BACKGROUND-002 |
| GATEWAY-004 | Validate gateway and Render infrastructure | Pending | GATEWAY-003 |

Canonical ARCH-002 Render Blueprints:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

The two Blueprints must manage distinct resources.

`GATEWAY-003` must remain Pending until every declared dependency is
architect-accepted Complete.

The production Admin browser contract is host based:

```text
admin.modainteract.com -> gateway -> private moda-interact-admin
```

`GATEWAY-007` resolves the provisional `/admin/*` mapping without reopening the
accepted GATEWAY-002 task.

`SYSTEM-TEST-001` already exists and remains Pending on the final
`GATEWAY-004` infrastructure-validation gate.

The individual task file is authoritative for task state.
