# ARCH-052 Shopify Tasks

Architecture: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`
Owner: `moda_app`
Coordinator: `moda_architect`

These are portable task definitions, **defined but not materialised**; the individual task YAML frontmatter is authoritative. Superseded tasks must never be executed.

| Task | Bounded outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-052-SHOPIFY-001](SHOPIFY-001-select-multiple-authorised-recovery-discounts.md) | Make Shopify merchant discount selection match WooCommerce checkboxes | Ready | `ARCH-052-BACKGROUND-009` |

SHOPIFY-001 is Ready for Attempt 3 after architect review found that the required PostgreSQL catalogue-sync race is not exercised; see the task report for the exact validation gap.
