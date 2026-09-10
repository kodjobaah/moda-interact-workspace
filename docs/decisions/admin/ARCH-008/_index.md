# ARCH-008 — Admin

Architecture: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

Current frontier: `ARCH-008-ADMIN-003` is Ready for Attempt 3 after architect Changes Requested on Attempt 2.

| Task | Status | Purpose |
|---|---|---|
| `ARCH-008-ADMIN-001` | Complete | Establish truthful asynchronous billing terminology and safe bounded read primitives. |
| `ARCH-008-ADMIN-002` | Complete | Simplify the global Billing workspace into five URL-backed tabs and reusable detail drawers. |
| `ARCH-008-ADMIN-003` | Ready | Attempt 3 required: complete tenant billing detail semantics, build validation, and canonical Completion Report. |

Execution order:

```text
ADMIN-001 -> ADMIN-002 -> ADMIN-003
```

The UI tasks are serialised intentionally. ADMIN-002 creates/reuses the common right-side billing drawer/tab primitives; ADMIN-003 then reuses those primitives rather than independently inventing another drawer mechanism.
