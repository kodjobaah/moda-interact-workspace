# ARCH-008 — Shopify

Architecture: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

| Task | Status | Purpose |
|---|---|---|
| `ARCH-008-SHOPIFY-001` | Ready — Changes Requested | Require an exact provider/local current billing cycle before creating a new recovery-credit-pack UsageEvent. |
| `ARCH-008-SHOPIFY-003` | Superseded | Mock-only billing/options prototype replaced by the real server-backed `/app/billing/options` implementation in `ARCH-010-SHOPIFY-008`. |

Current frontier:

- `ARCH-008-SHOPIFY-001` Attempt 1 was reviewed on 2026-09-09 and returned **Changes Requested**. The same task remains Ready for its next attempt; accepted `ARCH-007-SHOPIFY-004` remains Complete.
- `ARCH-008-BACKGROUND-002` remains Pending until SHOPIFY-001 is architect-accepted Complete.
- `ARCH-008-SHOPIFY-003` must not be resumed. Its useful existing screen/component work may be reused by ARCH-010, but mock billing state and mock-only behaviour are not production requirements.
