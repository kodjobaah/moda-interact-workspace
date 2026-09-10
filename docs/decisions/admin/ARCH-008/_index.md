# ARCH-008 — Admin

Architecture: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

Current frontier: `ARCH-008-ADMIN-003` is Ready after architect acceptance of ADMIN-002.

| Task | Status | Purpose |
|---|---|---|
| `ARCH-008-ADMIN-001` | Complete | Establish truthful asynchronous billing terminology and safe bounded read primitives. |
| `ARCH-008-ADMIN-002` | Complete | Simplify the global Billing workspace into five URL-backed tabs and reusable detail drawers. |
| `ARCH-008-ADMIN-003` | Ready | Simplify Tenant Directory -> Billing into four URL-backed sub-tabs with progressive disclosure. |

Execution order:

```text
ADMIN-001 -> ADMIN-002 -> ADMIN-003
```

The UI tasks are serialised intentionally. ADMIN-002 creates/reuses the common right-side billing drawer/tab primitives; ADMIN-003 then reuses those primitives rather than independently inventing another drawer mechanism.
