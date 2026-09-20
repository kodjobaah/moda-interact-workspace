# ARCH-020 shopify tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_app. Repository: moda-interact. Coordinator: moda_architect.

Individual task YAML is authoritative. The accepted implementation and review live on the mirrored task branches; final integration is developer-owned.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-SHOPIFY-001](SHOPIFY-001-expose-merchant-capability-feature-preferences.md) | Expose merchant capability feature preferences | complete | ARCH-020-SHARED-001, ARCH-016-SHOPIFY-002 |

SHOPIFY-001 is architect-accepted Complete at Attempt 1 (`4693bba`, report
`c5016d73`). Merchant eligibility, explicit idempotent saves and guarded form
behavior conform; architect reran 18 passing focused checks and reviewed six
passing PostgreSQL tests plus build/browser evidence. Existing repository-wide
typecheck/lint limitations remain documented. SYSTEM-TEST-001 remains Pending
until all its implementation dependencies are accepted, then explicitly
user-invoked; no task is launched. Developer integration remains separate.
