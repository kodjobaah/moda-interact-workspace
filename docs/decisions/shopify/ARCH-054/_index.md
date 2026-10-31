# ARCH-054 Shopify Tasks

Architecture: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`
Owner: `moda_app`
Coordinator: `moda_architect`

The individual task YAML frontmatter is authoritative.

| Task | Bounded outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-054-SHOPIFY-001](SHOPIFY-001-add-merchant-ai-response-delay-settings.md) | Expose the merchant-configurable 0–30 minute AI response delay | Complete | `ARCH-054-DATABASE-001`, `ARCH-054-SHARED-002` |
| [ARCH-054-SHOPIFY-002](SHOPIFY-002-invalidate-shopify-pending-ai-on-handover.md) | Invalidate pending AI on Shopify handover | Ready | `ARCH-054-DATABASE-001` |
