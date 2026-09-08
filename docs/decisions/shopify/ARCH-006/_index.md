# ARCH-006 Shopify Tasks

Architecture: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Assigned Agent: `moda_app`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| SHOPIFY-001 | Implement merchant support server capability | Complete | DATABASE-002, SHARED-002, SHARED-004, ARCH-005-DATABASE-001 |
| SHOPIFY-002 | Emit one subscription-ended SYSTEM message from the authoritative billing transition | Complete | SHOPIFY-001 |
| SHOPIFY-003 | Build the merchant Messages UI | Complete | SHOPIFY-001, BACKGROUND-007, ARCH-005-SHOPIFY-002 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
The individual task file YAML metadata is authoritative. SHOPIFY-001, SHOPIFY-002 and SHOPIFY-003 are independently architect-accepted Complete. BACKGROUND-007 and ARCH-005-SHOPIFY-002 are also Complete. SHOPIFY-003 Attempt 4 was validation/test-only: it removed the task-owned duplicate-import diagnostic and added explicit `COALESCE("readAt", NOW())` idempotency regression coverage without changing the accepted Attempt 3 production implementation. Terminal ARCH-006 system testing remains deliberately deferred behind the developer's manual integrated-validation checkpoint.
