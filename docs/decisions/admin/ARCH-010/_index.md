# ARCH-010 — Admin

`moda-interact-admin` is internal-only. No ARCH-010 Admin task creates merchant access.

| Task | Status | Purpose |
|---|---|---|
| ARCH-010-ADMIN-001 | Ready | Move the default lifetime Free grant from plan-catalog semantics into platform billing controls while keeping the legacy BillingPlan field non-authoritative for compatibility. |
| ARCH-010-ADMIN-002 | Ready | Triage merchant support into exact purchase-lot/whole-credit partial refund requests without holding or provider action. |
| ARCH-010-ADMIN-003 | Pending | SUPER_ADMIN approve/hold and manually settle partial top-up refunds/credits in Shopify Partner Dashboard, then finalize local credits exactly once. |
| ARCH-010-ADMIN-004 | Ready | SUPER_ADMIN create/activate optional GLOBAL, PLAN or SHOP promotion campaigns; activation grants no merchant credits. |
| ARCH-010-ADMIN-005 | Pending | Catalogue all campaigns, close them and reopen the same campaign by changing expiry only while preserving immutable targeting/quantity and lifecycle audit. |
| ARCH-010-ADMIN-006 | Pending | Report per-campaign merchant selection/use/remaining allocation from campaign-linked grant history. |
Partial top-up refund workflow: ADMIN-002 creates an exact purchase-lot/credit request from an explicit merchant support message; ADMIN-003 revalidates and holds capacity, requires a human Shopify Partner Dashboard REFUND or CREDIT action, and finalizes local credit removal with provider evidence. No subscription refund/cancellation authority is added.


Promotions are optional merchant offers. Admin creates campaigns but does not push credits directly onto shops. New campaigns have exactly one GLOBAL/PLAN/SHOP scope; merchants opt in through SHOPIFY-021. Reopen preserves the same campaign and merchant allocations and only changes expiry/status with audit evidence.
