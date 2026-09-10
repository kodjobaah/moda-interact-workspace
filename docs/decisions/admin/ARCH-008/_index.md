# ARCH-008 — Admin

Architecture: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

Current frontier: `ARCH-008-ADMIN-001` is Ready for Attempt 2 after architect Changes Requested on Attempt 1.

| Task | Status | Purpose |
|---|---|---|
| `ARCH-008-ADMIN-001` | Ready | Establish truthful asynchronous billing terminology and safe bounded read primitives. |
| `ARCH-008-ADMIN-002` | Pending | Simplify the global Billing workspace into five URL-backed tabs and detail drawers. |
| `ARCH-008-ADMIN-003` | Pending | Simplify Tenant Directory -> Billing into four URL-backed sub-tabs with progressive disclosure. |

Execution order:

```text
ADMIN-001 -> ADMIN-002 -> ADMIN-003
```

The UI tasks are serialised intentionally. ADMIN-002 creates/reuses the common right-side billing drawer/tab primitives; ADMIN-003 then reuses those primitives rather than independently inventing another drawer mechanism.
