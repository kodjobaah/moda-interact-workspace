# ARCH-044 Commerce Tasks

Architecture: [ARCH-044-commerce-baseline-stabilisation](../../../architecture/ARCH-044-commerce-baseline-stabilisation.md).

Reconciled on 2026-11-02. Individual task frontmatter and review reports are authoritative. Superseded tasks must not be executed.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-044-COMMERCE-001](COMMERCE-001-stabilise-packaged-code-runtime.md) | Make packaged Code Runtime deterministic and preserve compile-only semantics | complete | — |
| [ARCH-044-COMMERCE-002](COMMERCE-002-deterministic-disposable-test-harness.md) | Provide isolated disposable PostgreSQL Redis and complete Vitest fixtures | complete | — |
| [ARCH-044-COMMERCE-003](COMMERCE-003-reconcile-shopify-admin-authoring.md) | Reconcile persisted Shopify Admin Tool authoring with MCP-extracted architecture | complete | — |
| [ARCH-044-COMMERCE-004](COMMERCE-004-reconcile-new-tool-authoring.md) | Reconcile New Tool authoring and WooCommerce provider-local boundaries | complete | — |
| [ARCH-044-COMMERCE-005](COMMERCE-005-reconcile-studio-workspace-tests.md) | Restore Studio Workspace authoring behavior and regression tests | complete | — |
| [ARCH-044-COMMERCE-006](COMMERCE-006-reconcile-agent-and-mcp-contract-boundaries.md) | Reconcile deprecated Agent template validation and MCP extraction boundaries | complete | — |
| [ARCH-044-COMMERCE-007](COMMERCE-007-repair-postgres-cas-and-publication.md) | Repair durable agent-configuration CAS and publication transaction validation | complete | `ARCH-044-COMMERCE-002` |
| [ARCH-044-COMMERCE-008](COMMERCE-008-correct-markdown-prompt-editor-refs.md) | Fix Markdown prompt editor React ref violations without changing CodeMirror behavior | complete | — |
