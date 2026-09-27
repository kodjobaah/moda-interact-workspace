# ARCH-023 shared tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md).

Assigned agent: `moda_shared`. Repository: `moda-interact-shared`. Coordinator: `moda_architect`.

These are portable task definitions from the 2026-09-27 review patch; individual task YAML is authoritative. No task branch/worktree is materialised by this patch.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [SHARED-001](SHARED-001-define-store-aware-commerce-configuration-contracts.md) | Store-aware Commerce configuration contracts | Ready | - |
| [SHARED-002](SHARED-002-define-merchant-knowledge-contracts.md) | Merchant Knowledge contracts/content units | Ready | - |
| [SHARED-003](SHARED-003-harden-commerce-runner-instruction-trust.md) | Runner instruction trust contract | Ready | - |
| [SHARED-004](SHARED-004-publish-arch023-shared-contracts.md) | Publish ARCH-023 Shared contracts | Pending | SHARED-001, SHARED-002, SHARED-003 |

## Execution frontier

Ready: `ARCH-023-SHARED-001`, `ARCH-023-SHARED-002`, `ARCH-023-SHARED-003`
