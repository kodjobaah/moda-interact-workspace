# ARCH-023 system-test tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge.md).

Assigned agent: `moda_system_test`. Repository: `moda-interact-system-test`. Coordinator: `moda_architect`.

These are portable task definitions from the 2026-09-27 review patch; individual task YAML is authoritative. No task branch/worktree is materialised by this patch.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [TEST-001](SYSTEM-TEST-001-validate-store-category-prompt-localisation.md) | Validate Store Category/prompt localisation | Pending | implementation set |
| [TEST-002](SYSTEM-TEST-002-validate-merchant-knowledge-end-to-end.md) | Validate plan-entitled but merchant-opt-in Merchant Knowledge end to end | Ready | ADMIN-004, SHOPIFY-004/005, BACKGROUND-004/005, COMMERCE-002/004, GATEWAY-001 |

## Execution frontier

Ready: `ARCH-023-SYSTEM-TEST-002`. All declared implementation/infrastructure dependencies are Complete / architect-accepted. Per the architecture lifecycle, the developer may intentionally leave this task Ready while performing the documented live Render/R2 manual validation and invoke the terminal system test when satisfied.

Pending: `ARCH-023-SYSTEM-TEST-001` retains its own dependency state.
