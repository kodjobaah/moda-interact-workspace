# ARCH-017 Shopify Tasks

Architecture:

`docs/architecture/ARCH-017-billing-plan-materialisation-dynamic-features.md`

Assigned Agent:

`moda_app`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| SHOPIFY-001 | Lazily materialise BillingPlan and manage merchant feature preferences | Complete — Attempt 4 Accepted | ARCH-017-DATABASE-001 |
| SHOPIFY-002 | Decouple callback onboarding milestone from Moda billing reconciliation | Complete | SHOPIFY-001 |
| SHOPIFY-003 | Enforce current BillingPeriod plan projection | Complete | SHOPIFY-002 |

`SHOPIFY-001` was developer-reopened and accepted on Attempt 4. Its later correction requires provider confirmation of the requested current/pending managed-pricing selection before the monotonic onboarding milestone is committed. This supersedes SHOPIFY-002's earlier callback-entry subrule without reopening or deleting SHOPIFY-002's historical acceptance.

The individual task files remain authoritative for task state.
