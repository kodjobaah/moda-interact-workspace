---
id: ARCH-019-SHOPIFY-001
architecture_id: ARCH-019
title: Implement bounded recovery cohort metrics and list readers
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: codex
claimed_at: 2026-09-20T12:12:28Z
attempt: 1
depends_on:
  - ARCH-019-DATABASE-001
enables:
  - ARCH-019-SHOPIFY-003
  - ARCH-019-SHOPIFY-005
  - ARCH-019-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Implement bounded recovery cohort metrics and list readers

## Architecture

Architecture ID: ARCH-019

Architecture document: docs/architecture/ARCH-019-merchant-recovery-experience.md

Coordinator: moda_architect. Read the complete parent architecture and referenced dependency tasks before execution; it supplies exact data, route, access, compatibility and rollout contracts.

## Objective

Return correct tenant-scoped recovery cohort metrics and cursor pages without loading conversation history.

## Context

This task contributes one bounded capability to the recovery-first merchant journey. The previous UI mixed billing-period navigation, all-time recovery figures and a customer modal. The new design separates recovery performance, recovery conversation history and billing usage.

## Scope

New app/services/recoveries cohort/query/list modules and local DTOs; focused tests; database Gitlink update to the architect-accepted DATABASE-001 commit in this implementation task only.

## Out of Scope

Other repository implementation; billing/credit/provider semantics; new automated messages; reply/takeover controls; unrelated refactoring; main merges/pushes; live deployment. Do not start enabled tasks. Parent architecture/index reconciliation belongs to moda_architect.

## Requirements

The parent architecture's behavioural contracts are binding. Preserve current tenant/lifecycle rules and accepted ARCH-017 onboarding behaviour; do not restore stale ARCH-013 permissions. Follow repo-local AGENTS.md and the assigned logical agent definition. Never copy mockup sample data into production. Preserve unrelated changes by using canonical task worktrees.

## Work Items

- [x] Implement the shared app-local date/filter parser, merchant-zone half-open cohort predicate and query contracts in the parent architecture.
- [x] Aggregate cohort counts/statuses and completed checkout values by currency in PostgreSQL with decimal-safe money handling and explicit unknown-value counts.
- [x] Implement deterministic (detectedAt DESC, id DESC) keyset recovery pages of 25 rows (maximum 50) plus one lookahead, and a five-row overview preview.
- [x] Implement bounded, parameterized customer name/email search using the architecture-defined semantics, safe projection and shop scope; validate cursor/filter binding.
- [x] Return a fixed-size summary plus bounded rows; exclude messages, lineItems, checkoutToken, checkoutUrl and accounting identifiers from list DTOs.

## Interfaces / Contracts

App-local recovery-query and recovery-list DTOs from the parent architecture. No new shared package contract or Shopify API call.

## Dependencies

- ARCH-019-DATABASE-001

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

- ARCH-019-SHOPIFY-003
- ARCH-019-SHOPIFY-005
- ARCH-019-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Summary and preview/list use the same detectedAt cohort; zero denominator produces null rate, not a misleading 0% value.
- [x] DST boundaries, inclusive date inputs, null money/currency, multiple currencies and end-date exclusion behave as specified.
- [x] Duplicate timestamps paginate deterministically; malformed or mismatched cursors cannot read another shop or trigger an unbounded fetch.
- [x] Search does not hydrate all customers/recoveries; aggregate counts ignore list search/status filters, as documented, and rows reflect the filters.
- [x] Money aggregation retains decimal precision and no cross-currency sum is returned.
- [x] Accepted index dependency is consumed deliberately without staging a parent-workspace service Gitlink.

## Validation

- [x] Run npm test -- tests/unit/recovery-cohort-readers.test.ts (create this focused suite).
- [x] Run npm run typecheck and git diff --check; record existing baseline failures separately.
- [x] Prove generated query bounds/selects with local tests and supply the exact local PostgreSQL fixture command for query-result validation if the suite requires long infrastructure startup.

New test filenames above are required deliverables, not claims that those suites already exist. Use current package.json scripts; do not invent success when a command cannot run. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md: fast local checks are agent-owned; long infrastructure/live commands are developer-owned unless exactly authorized. Required developer evidence may remain pending at review, never at acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's Work Items, Acceptance Criteria, Validation and Completion Report, publish task-owned mirrored branches and return to review. Record exact pending developer-validation commands if needed. Stop; do not start enabled tasks, merge/push main, or mark your own task Complete.

## Implementation Notes

Use scripts/start-agent-task.py through the normal /moda-task preparation path. Task creation has not claimed execution. Dedicated parent and implementation worktrees, synchronization and recursive database submodule preparation are mandatory when execution starts. Follow docs/agent-vcs-ownership-policy.md. The repository agent may update only this task's execution/report fields in parent docs; shared indexes and parent architecture remain architect-owned.

## Completion Report

### Status

Ready for Review. Attempt 1, executor `codex`. No architect acceptance decision is asserted. The existing Architect Review is Pending and contains no Changes Requested corrections.

### Files Changed

Implementation repository only:

- `app/services/recoveries/recovery-query.server.ts`: app-local date/filter normalization, zone-aware calendar boundaries, stable validation codes, bounded shop/filter-bound cursors.
- `app/services/recoveries/recovery-readers.server.ts`: SQL cohort aggregates, safe bounded keyset pages and repeatable-read overview summary/five-row preview; exported local DTOs.
- `app/services/recoveries/README.md`: consumer/authentication contract, validation commands and evidence limits.
- `tests/unit/recovery-cohort-readers.test.ts`: required focused suite with opt-in rolled-back local PostgreSQL fixture.
- `tests/tsconfig.recovery-readers.json`: reproducible focused TypeScript validation, without unrelated JS diagnostics.
- `tests/fixtures/recovery-cohort-query-plans.json`: actual local aggregate/list/keyset/search EXPLAIN ANALYZE BUFFERS evidence.

Parent workspace: this task file only. No parent implementation Gitlink change.

### Work Completed

- All readers use the normalized merchant-zone half-open detectedAt cohort. Date input is inclusive, capped at 366 calendar dates, defaults to 30 dates, and rejects invalid/reversed/future ranges before reads. Zone resolution/fallback reuses merchantUiContext. Tests cover London DST, Lord Howe half-hour DST, midnight gaps and a skipped calendar date.
- One PostgreSQL aggregate query computes current statuses/counts and per-currency completed checkout values as exact decimal strings. Missing price/currency has an explicit unknown count; zero denominator returns null; list search/status never changes the cohort summary.
- One bounded SQL list query selects safe fields, tenant-constrains both recovery and customer join, escapes literal wildcard search, uses (detectedAt,id) ordering, and limits transfer to pageSize+1 (default 26, max 51). Next/previous cursors carry original keys and normalized shop/filter binding; deleted boundaries require no lookup. Empty live pages retain an opposite-direction return cursor.
- Overview clears list filters and reads summary plus five newest rows in one repeatable-read snapshot. No messages, lineItems, tokens, checkout URLs or accounting identifiers enter DTOs. Display labels are localization-ready descriptors.
- Accepted database dependency is already integrated at recorded Gitlink `9c6a4d8402a01840e2ea8dc18e89171f00564d29`. `git diff 54c0ec2 HEAD` in the database submodule is empty: integrated and architect-accepted task revisions have identical full trees. No downgrade or redundant Gitlink update was necessary.

### Validation Results

Agent-executed:

- `npm test -- tests/unit/recovery-cohort-readers.test.ts`: initial 25 unit tests passed; final suite adds unknown-only coverage and the opt-in PostgreSQL fixture.
- `RECOVERY_TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moda_interact RECOVERY_TEST_PLAN_OUTPUT=/tmp/arch019-shopify001-plans.json npm test -- tests/unit/recovery-cohort-readers.test.ts`: **27 passed**, exit 0, 0.907 seconds final run. The fixture uses a transaction-owned isolated schema with rollback and statement timeout, never commerce application data. It validates actual generated SQL with schema substitution, exact decimal sums, inclusive/exclusive dates, cross-shop customer safety, search, status filters and duplicate/deleted key traversal. Its pg adapter explicitly matches Prisma UTC timestamp semantics; an initial adapter conversion failure was corrected and revalidated.
- `npm run typecheck`: **failed**, exit 2, seven existing parser errors in `tests/unit/merchant-route-access-policy.test.ts` at lines 201, 219–220. That file exactly matches the starting implementation commit and is untouched. This differs from the historical 48-error TYPECHECK-001 summary; no claim that full typechecking passed or that those errors were resolved.
- Focused TypeScript initially identified a new transaction callback annotation issue, now fixed. With imported JS diagnostics enabled it reports only three existing global Prisma typing errors in `app/db.server.js`; new TypeScript files report none. Final reproducible command: `./node_modules/.bin/tsc --project tests/tsconfig.recovery-readers.json`: **passed**, exit 0 (explicitly disables unrelated JS diagnostics).
- `./node_modules/.bin/eslint app/services/recoveries/*.ts tests/unit/recovery-cohort-readers.test.ts`: passed, exit 0.
- Prettier applied only to the three new TypeScript files. `git diff --check`: passed.
- Stored query plans show an aggregate over tenant/date index scan + sort, and Limit/nested-loop index scans for list, keyset and search on the tiny local fixture. Actual transferred page rows are bounded. This is query-result/shape evidence, not a representative production throughput claim.

Developer validation required: none for this bounded reader task; the local fixture ran successfully without infrastructure startup. Exact rerun command is above. Architecture terminal system validation and production rollout remain outside this task.

### Deviations

No database Gitlink change: the launcher materialized the already-merged, tree-identical accepted index revision. No additional prerequisite integration needed.

Bootstrap script discovers the workspace from the current directory rather than honoring the supplied sibling worktree root. Sourcing it from the canonical workspace before navigating to the implementation worktree resolved the local toolchain issue without policy/script changes. Existing source-checkout node_modules is linked for read-only dependency reuse; no install, generation or dependency mutation was performed.

### Assumptions

Consuming route loaders must authenticate and guard the merchant surface before passing an owned shop ID. Normalized queries are server-produced objects, never deserialized client authority. Cursor hashes bind navigation context but are not authorization/signatures; independent SQL shop/date/limit predicates remain authoritative. Summary values group distinct recorded currencies; no conversion or cross-currency total is introduced.

### Unresolved Issues

Repository-wide TypeScript validation remains blocked by pre-existing syntax errors, plus existing JS global typing debt in a focused diagnostic. Baseline documentation reconciliation belongs to moda_architect. No task-source failure remains after focused validation.

### Architectural Concerns

Substring search and aggregation still scale with cohort size. Small-fixture plans do not establish representative capacity. Downstream route/UI localization, lifecycle guards and full experience validation remain their separately assigned tasks.

### Git / VCS

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent physical worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-019-SHOPIFY-001`; branch `task/ARCH-019-SHOPIFY-001`.
- Implementation physical worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-019-SHOPIFY-001`; branch `task/ARCH-019-SHOPIFY-001`.
- Launcher parent task-branch fast-forward: not-needed; origin/main incorporated: yes (final claim resync already-current); prepared parent HEAD `518d2e4efde3d0929adf3db8954a352df65d0393`.
- Launcher implementation task-branch fast-forward: not-needed; origin/main incorporated: already-current; starting HEAD `c4fd514b54a34bac8ee4770dd6c9b0fe7a4059e5`.
- Recursive submodule sync/update: passed, ready; database at `9c6a4d8402a01840e2ea8dc18e89171f00564d29`.
- Durable Attempt 1 claim: `e12d46c6f8bda73899a267d4ce4e59332db34658`, pushed by launcher.
- Shared/default workspace or implementation checkout switched/mutated for implementation work: no. Another task worktree reused: no.
- Implementation publication: `08af00b85508d3ae7e653890abbc8a5ca0c0cc9d`, committed and pushed to `origin/task/ARCH-019-SHOPIFY-001`.
- Parent publication: this report commit on the mirrored task branch; only this task file staged. Final commit/push identity is recorded in the execution handoff to avoid a self-referential hash.
- No parent service Gitlink staged. Neither main branch merged, switched or pushed. Enabled tasks remain untouched.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation submitted.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Awaiting implementation review.

### Follow-up

Reconcile task/index/frontier after accepted implementation; terminal system test remains manually invoked.
