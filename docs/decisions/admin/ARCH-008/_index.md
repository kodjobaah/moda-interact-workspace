# ARCH-008 — Admin

Architecture: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

Current frontier: Admin implementation complete; terminal `ARCH-008-SYSTEM-TEST-001` is Ready but remains developer-invoked/manual-gated.

| Task | Status | Purpose |
|---|---|---|
| `ARCH-008-ADMIN-001` | Complete | Establish truthful asynchronous billing terminology and safe bounded read primitives. |
| `ARCH-008-ADMIN-002` | Complete | Simplify the global Billing workspace into five URL-backed tabs and reusable detail drawers. |
| `ARCH-008-ADMIN-003` | Complete | Simplify Tenant Directory -> Billing into four URL-backed tenant-scoped sub-tabs with progressive disclosure. |

Execution order:

```text
ADMIN-001 -> ADMIN-002 -> ADMIN-003
```

The UI tasks are serialised intentionally. ADMIN-002 creates/reuses the common right-side billing drawer/tab primitives; ADMIN-003 then reuses those primitives rather than independently inventing another drawer mechanism.
