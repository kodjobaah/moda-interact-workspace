# ARCH-007 Shopify Tasks

Architecture: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

Assigned Agent: `moda_app`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| SHOPIFY-001 | Implement Shopify App Pricing subscription verification and typed local projection | Complete | SHARED-002, DATABASE-003 |
| SHOPIFY-002 | Build merchant billing plan state, hosted-plan actions and billing SYSTEM-message CTAs | Complete | SHOPIFY-001 |
| SHOPIFY-003 | Make Shopify uninstall stop new billing admission while preserving pre-uninstall drain state | Complete | SHOPIFY-001 |
| SHOPIFY-004 | Let merchants request repeatable recovery-credit packs | **Ready** | SHOPIFY-002, DATABASE-005, SHARED-006, ADMIN-005 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
The individual task YAML metadata is authoritative.

Current architect-accepted/published Shared release is `@modainteract/moda-interact-shared@0.8.0`.

- SHOPIFY-001 is architect-accepted Complete after Attempt 3.
- SHOPIFY-002 Attempt 3 is architect-accepted Complete. The subscription-ended producer now persists Shared's canonical `BILLING_SUBSCRIPTION_ENDED` metadata and the producer-to-CTA regression is accepted.
- SHOPIFY-003 Attempt 2 is architect-accepted Complete. The accepted uninstall implementation is preserved and the Shopify Shared dependency baseline is restored to `^0.7.4` / resolved `0.7.4`.
- SHOPIFY-004 is Ready because SHOPIFY-002, DATABASE-005, SHARED-006 and ADMIN-005 are architect-accepted Complete.
- Cross-architecture `ARCH-005-SHOPIFY-004` is now Ready because ARCH-005-SHOPIFY-002, ARCH-006-SHOPIFY-003 and ARCH-007-SHOPIFY-002 are all Complete.
