# ARCH-010 — Admin

`moda-interact-admin` is internal-only. No ARCH-010 Admin task creates merchant access.

| Task | Status | Purpose |
|---|---|---|
| ARCH-010-ADMIN-001 | Pending | Move the default lifetime Free grant from plan-catalog semantics into platform billing controls while keeping the legacy BillingPlan field non-authoritative for compatibility. |
| ARCH-010-ADMIN-002 | Pending | Triage merchant support into exact purchase-lot/whole-credit partial refund requests without holding or provider action. |
| ARCH-010-ADMIN-003 | Pending | SUPER_ADMIN approve/hold and manually settle partial top-up refunds/credits in Shopify Partner Dashboard, then finalize local credits exactly once. |
| ARCH-010-ADMIN-004 | Pending | SUPER_ADMIN grant one idempotent, audited promotional-credit allocation to an exact shop and show its separate balance/history. |
| ARCH-010-ADMIN-005 | Pending | Apply the same grant primitive to a bounded multi-shop targeted campaign with per-shop idempotency and explicit partial-failure results. |
Partial top-up refund workflow: ADMIN-002 creates an exact purchase-lot/credit request from an explicit merchant support message; ADMIN-003 revalidates and holds capacity, requires a human Shopify Partner Dashboard REFUND or CREDIT action, and finalizes local credit removal with provider evidence. No subscription refund/cancellation authority is added.


Promotional credits are a dedicated non-refundable bucket. Admin must not use `BillingAllowanceAdjustment(FREE_RECOVERY_LIFETIME)` for campaign/test grants. Campaign grants create no Shopify/App Event and do not activate an otherwise non-executable shop.
