# ARCH-008 — Shopify

Architecture: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

| Task | Status | Purpose |
|---|---|---|
| `ARCH-008-SHOPIFY-001` | Ready | Require an exact provider/local current billing cycle before creating a new recovery-credit-pack UsageEvent. |

Current frontier:

- `ARCH-008-SHOPIFY-001` is Ready because accepted
  `ARCH-007-SHOPIFY-004` is Complete.
- It enables `ARCH-008-BACKGROUND-002`.
- No ARCH-008 database task is required by the architect reconciliation
  preflight.
