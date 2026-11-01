# ARCH-048 System Test Tasks

Architecture: [`ARCH-048-woocommerce-checkout-recovery-pipeline.md`](../../../architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md).

Assigned agent: `moda_system_test`. Coordinator: `moda_architect`.

This revised single terminal test task supersedes the former first-recovery-only acceptance contract; no separate parallel system test is introduced.

The individual task YAML is authoritative. These are portable definitions from the 2026-10-29 code snapshot; no developer Git branch/worktree/commit/push is implied.

| Task | Outcome | Status | Required Complete dependencies |
|---|---|---|---|
| [`SYSTEM-TEST-001`](SYSTEM-TEST-001-certify-woo-first-recovery-lifecycle.md) | Certify G1→G2→G3, consent, order, billing, routing and failures | **Pending** | `WOOCOMMERCE-002`, `WOOCOMMERCE-003`, `BACKGROUND-001`, `BACKGROUND-002`, `BACKGROUND-003`, `BACKGROUND-004`, `BACKGROUND-005`, `BACKGROUND-006`, `BACKGROUND-007`, `BACKGROUND-008`, `BACKGROUND-009`, `BACKGROUND-010`, `BACKGROUND-011`, `ARCH-046-BACKGROUND-002`, `ARCH-046-BACKGROUND-004`, `ARCH-046-WOOCOMMERCE-003`, `ARCH-045-BACKGROUND-005` |

## Execution frontier

SYSTEM-TEST-001 stays Pending until every prerequisite, including BG007–BG011 and ARCH-046-WOOCOMMERCE-003, is Complete. It must not gate implementation tasks.
The developer can manually validate after implementation and before invoking the terminal system test.
No production Woo provider send is authorised by system-test readiness.
Use the existing system-test catalogue/harness and report measured evidence; do not implement Background functionality in system-test.

## Implementation and review constraints

- Each task must run through `/moda-task <TASK_ID>` with launcher-resolved dedicated parent and implementation worktrees; never execute code changes in the shared workspace.
- Repository agent modifies only its explicitly permitted files, its own task metadata/Completion Report and tests. The architect alone modifies architecture documents, indexes and Architect Review.
- Use the canonical shared logger and fail-visible retries; never suppress technical exceptions or log customer carts/PII/secrets.
- Keep each generation independently eligible for initial outreach, but never allow duplicate attempts/charges inside a generation. Consent, STOP, order, MARKETING, provider and production-default-off guards remain mandatory.
