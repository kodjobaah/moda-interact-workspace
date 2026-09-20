---
id: ARCH-019-SHOPIFY-003
architecture_id: ARCH-019
title: Build the recovery browsing page and guarded route
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-019-SHOPIFY-001
enables:
  - ARCH-019-SHOPIFY-004
  - ARCH-019-SHOPIFY-005
  - ARCH-019-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Build the recovery browsing page and guarded route

## Architecture

Architecture ID: ARCH-019

Architecture document: docs/architecture/ARCH-019-merchant-recovery-experience.md

Coordinator: moda_architect. Read the complete parent architecture and referenced dependency tasks before execution; it supplies exact data, route, access, compatibility and rollout contracts.

## Objective

Let merchants browse recovery records using accessible search, date/status filters and server pagination.

## Context

This task contributes one bounded capability to the recovery-first merchant journey. The previous UI mixed billing-period navigation, all-time recovery figures and a customer modal. The new design separates recovery performance, recovery conversation history and billing usage.

## Scope

app/routes.ts; new app/routes/app/recoveries list route/components/styles; app/services/shop/merchant-route-access-policy.ts for RECOVERY_HISTORY only; app-local query helpers from SHOPIFY-001; associated tests and all merchant locale catalogues.

## Out of Scope

Other repository implementation; billing/credit/provider semantics; new automated messages; reply/takeover controls; unrelated refactoring; main merges/pushes; live deployment. Do not start enabled tasks. Parent architecture/index reconciliation belongs to moda_architect.

## Requirements

The parent architecture's behavioural contracts are binding. Preserve current tenant/lifecycle rules and accepted ARCH-017 onboarding behaviour; do not restore stale ARCH-013 permissions. Follow repo-local AGENTS.md and the assigned logical agent definition. Never copy mockup sample data into production. Preserve unrelated changes by using canonical task worktrees.

## Work Items

- [x] Register /app/recoveries under the embedded app layout with independent authentication and RECOVERY_HISTORY authorization before recovery business reads.
- [x] Add RECOVERY_HISTORY permission only for ACTIVE, NO_CONTRACT, FROZEN and BILLING_ATTENTION; retain every other existing surface rule.
- [x] Build the date presets/custom range, customer search, status filters and one-recovery-per-row presentation using SHOPIFY-001.
- [x] Serialize filter and cursor state in safe URLs; reset pagination when filters change and preserve context for future detail navigation.
- [x] Implement loading, read-error/retry, never-used and filtered-empty states; localize labels and date/money formatting; make row actions keyboard links.

## Interfaces / Contracts

SHOPIFY-001 list DTO and query parser; parent architecture route/access matrix. Keep authenticated embed context intact in links.

## Dependencies

- ARCH-019-SHOPIFY-001

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

- ARCH-019-SHOPIFY-004
- ARCH-019-SHOPIFY-005
- ARCH-019-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Each visible row represents one recovery, with customer fallback, checkout value, accurate status and started date/time; no opaque database ID is the primary label.
- [x] All visible filters are functional and backed by server constraints; search/filter navigation cannot introduce cross-tenant reads.
- [x] No mutation controls or new top-level navigation item are added in this task; detail links are enabled only once SHOPIFY-004 provides the destination.
- [x] Mobile 320px/390px and desktop 1024px layouts remain usable; labels, focus and empty/error paths are accessible.
- [x] Locale catalogue parity and ICU syntax hold for every newly added key; no hard-coded English statuses remain.

## Validation

- [x] Run npm test -- tests/unit/recovery-list-route.test.ts tests/unit/merchant-route-access-policy.test.ts tests/unit/merchant-i18n.test.ts (create the new route suite).
- [x] Run npm run typecheck, npm run lint and git diff --check; document baseline-only failures.
- [x] Verify keyboard search/filter/pagination and responsive layout with local deterministic fixtures; record screenshots and actual browser evidence.

New test filenames above are required deliverables, not claims that those suites already exist. Use current package.json scripts; do not invent success when a command cannot run. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md: fast local checks are agent-owned; long infrastructure/live commands are developer-owned unless exactly authorized. Required developer evidence may remain pending at review, never at acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's Work Items, Acceptance Criteria, Validation and Completion Report, publish task-owned mirrored branches and return to review. Record exact pending developer-validation commands if needed. Stop; do not start enabled tasks, merge/push main, or mark your own task Complete.

## Implementation Notes

Use scripts/start-agent-task.py through the normal /moda-task preparation path. Task creation has not claimed execution. Dedicated parent and implementation worktrees, synchronization and recursive database submodule preparation are mandatory when execution starts. Follow docs/agent-vcs-ownership-policy.md. The repository agent may update only this task's execution/report fields in parent docs; shared indexes and parent architecture remain architect-owned.

## Completion Report

### Status

Ready for Review. Attempt 1, executor codex. Existing Architect Review is Pending with no Changes Requested corrections; no architect acceptance decision is asserted.

### Files Changed

- `app/routes.ts`: adds `/app/recoveries` under the existing embedded layout.
- `app/services/shop/merchant-route-access-policy.ts`: adds RECOVERY_HISTORY only for ACTIVE, NO_CONTRACT, FROZEN and BILLING_ATTENTION; other surface permissions and navigation remain unchanged.
- `app/routes/app/recoveries/{route.tsx,loader.server.ts,recovery-list-state.ts,RecoveryList.tsx,RecoveryList.css}`: independent authenticated loader, safe URL state, responsive localized list and loading/error/empty handling.
- All 20 `app/i18n/locales/*.json` catalogues: 36 recovery browsing keys each, preserving unrelated text; status translations reuse existing catalogue wording.
- `tests/unit/recovery-list-route.test.ts`: required new loader/navigation/render suite.
- `tests/unit/merchant-route-access-policy.test.ts`: repairs malformed duplicated test fragments and stale expectations, then verifies the complete current permission/navigation matrix including the new surface.
- `tests/browser/recovery-list/`: localhost-only deterministic fixture, browser evidence README and five actual screenshots.
- Parent workspace: this task file only.

### Work Completed

- Authentication and shop resolution precede independent RECOVERY_HISTORY authorization. Inactive shops are denied before settings/subscription or recovery reads. Active shops use current onboarding and subscription lifecycle policy. Browser shopId/shop/returnTo parameters never authorize a read; denial links preserve bounded embed context.
- Uses accepted SHOPIFY-001 date parser, cursor validation, DTOs and bounded page reader. Their source exactly matches accepted `08af00b` in the prepared starting implementation revision. No prerequisite branch integration or reader changes were needed.
- Date presets, editable inclusive dates, customer search and status filters serialize into explicit local URLs. GET form submission and presets reset cursor; pagination preserves normalized dates/status/search/pageSize and embed context. The shared local URL helper preserves current cursor by default for future detail-return context.
- One row per recovery shows customer name/email/Guest, localized latest status, exact reader value formatted through merchant i18n, and merchant-zone started time. Safe checkout date label replaces opaque ID display. No row-detail link is enabled before SHOPIFY-004 supplies its destination. No mutation control, new navigation item or detail route was added.
- Loading announces busy state with structural placeholders. Invalid inputs produce localized validation without recovery queries. Read errors retain filters and offer Refresh. A single tenant-scoped ID-only existence lookup on empty pages distinguishes never-used history from a filtered/date-empty page; no messages or all-history hydration.
- Native labels, GET controls, buttons and keyboard pagination links; visible focus outline; wrap-safe long email/RTL customer content; 320/390/1024 layouts. All locale catalogues retain parity and ICU validity.

### Validation Results

Agent-executed:

- `npm test -- tests/unit/recovery-list-route.test.ts tests/unit/merchant-route-access-policy.test.ts tests/unit/merchant-i18n.test.ts`: **72 tests passed across 3 files**, exit 0, final run 1.83s. Covers allowed/denied lifecycle states, authentication failures, owned-shop enforcement, invalid date/search/filter/cursor rejection, safe URL allowlist, error context, history-vs-filtered emptiness, safe rendering, exact access matrix and all-locale catalogue/ICU parity.
- `npm run typecheck`: **non-zero**, 171 errors in 27 untouched files after repairing the task-relevant malformed access-policy suite. Zero diagnostics in this task's changed/new files. A new readonly cursor assignment error found on the initial run was fixed before the final run. Every remaining diagnostic file is tracked at starting HEAD and unchanged by this task. TYPECHECK-001's historical 48-error summary is stale; previous syntax errors had prevented the compiler reaching this wider existing debt. Do not interpret this as a clean full typecheck.
- `npm run lint`: **non-zero**, 20 errors and 2 warnings in untouched files (unused imports/variables, existing JSX/props issues, explicit any/control regex, existing tests). No task-owned diagnostic.
- Focused ESLint over new route/state/loader/components, route registration, access policy, both changed test suites and browser fixture TS/TSX: **passed**, exit 0.
- `git diff --check` and staged diff check: **passed**.
- Local browser fixture launched with `./node_modules/.bin/vite --config tests/browser/recovery-list/vite.config.ts`; only 127.0.0.1:4179, synthetic data, no Shopify/database/live calls. Actual production component/CSS/locales rendered in a React Router data router. Real loader auth/query behaviour is tested separately by the unit suite.
- Actual Chromium evidence: 320px English controls/rows, 390px German labels, 1024px desktop grid; no horizontal overflow. Screenshots stored in `tests/browser/recovery-list/evidence/{320,320-rows,390,1024,error}.png`. Detailed observations and reproducible fixture command are in its README.
- Browser interactions verified Enter-submitted customer search, Next/Previous keyboard links, native status selection + Enter-submitted Apply, Today preset yielding filtered-empty, custom dates updating range/results, error Refresh recovering rows, and never-used state. Loading and focus outline were observed. Viewport override reset afterward. A native arrow-key selection attempt did not change selection through the automation bridge; native select-option selection and keyboard submission were verified separately.

Developer validation required: none remains for this bounded local page task. Full deployed Shopify embedding and terminal architecture system validation remain outside this task and are not claimed by local fixture evidence.

### Deviations

The required access-policy test contained duplicated trailing syntax and stale onboarding/billing/navigation expectations. Because this task directly changes and validates that policy, it repairs the test against current authoritative source without widening other permissions. This exposed broader existing typecheck debt rather than resolving unrelated implementation files.

Existing installed node_modules is linked into the dedicated implementation worktree for dependency reuse. Node bootstrap was sourced from the canonical workspace before navigating to the task worktree. No dependency upgrade or generated Prisma/submodule modification.

### Assumptions

Detail links remain absent until SHOPIFY-004 provides the independently guarded destination. Future detail navigation should reuse recoveryListUrl with validated filter/cursor data, never arbitrary returnTo. No top-level Recoveries item is introduced ahead of the navigation task.

### Unresolved Issues

Full repository typecheck/lint remain non-zero solely in untouched files. Baseline summary reconciliation belongs to moda_architect. No failing task-owned test or lint/type diagnostic remains. Local fixture does not substitute for later full embedded/live system validation.

### Architectural Concerns

None newly required. Authentication/lifecycle guards stay server-side, history browsing remains read-only, and SHOPIFY-001 remains the authoritative bounded reader. No provider API, queue, schema, accounting, or cross-repository contract changes.

### Git / VCS

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-019-SHOPIFY-003`, branch `task/ARCH-019-SHOPIFY-003`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-019-SHOPIFY-003`, branch `task/ARCH-019-SHOPIFY-003`.
- Launcher parent remote task fast-forward: not-needed; origin/main incorporated: yes; prepared HEAD `a565e0160e7aa57187874da10e9a7b3d14e6002e`. Final claim resync: already-current.
- Launcher implementation remote task fast-forward: not-needed; origin/main incorporated: already-current; starting HEAD `30c69f842e71407055aa5a02f0ecd0ded21179f0`.
- Recursive submodule sync/update: passed and ready, database `9c6a4d8402a01840e2ea8dc18e89171f00564d29`.
- Durable Attempt 1 claim: `8ceeee3dfd06fd523ff190bbdb14cbada03b8aca`, pushed by launcher.
- Implementation commit `37c62cde6c23f78b8cb61472d6bd0b4c4ee53199` committed and pushed to `origin/task/ARCH-019-SHOPIFY-003`.
- Parent report publication is this task-only commit on the mirrored task branch; final hash/push evidence is recorded in the execution handoff to avoid a self-referential hash.
- Shared/default checkout switched/mutated for task implementation: no. Another task worktree reused: no. Parent service Gitlink staged: no. Main merged/pushed: no. Enabled tasks started: no.

## Architect Review

### Review Status

Accepted — 2026-09-20, Attempt 1. Complete under `completion_mode: automatic`.

### Review Notes

Accepted implementation `37c62cde6c23f78b8cb61472d6bd0b4c4ee53199`, reviewed against report `c9f202f2ec48949549d1cb20a65728f680772079`. Both published remote task heads independently verified. No blocking implementation defect or workflow non-conformance found.

Independent loader authentication and owned-shop resolution precede lifecycle enforcement and recovery reads. RECOVERY_HISTORY is added only for ACTIVE, NO_CONTRACT, FROZEN and BILLING_ATTENTION; all other permissions and navigation are preserved. Query parsing and shop-bound cursor validation reuse accepted SHOPIFY-001. Search/date/status changes clear pagination, navigation retains bounded embed context, and empty-history detection uses a tenant-scoped ID-only existence query. Safe rendering, localized statuses, unknown-value fallback and disabled premature detail links satisfy this task's contract.

### Reviewed Files

All production additions and changes: route registration, loader/state/component/CSS, lifecycle policy, 20 catalogue diffs. Also inspected both modified/new unit suites, browser fixture and evidence README, captured 320px controls/rows, 390px German and 1024px desktop screenshots, existing merchant i18n/policy helpers, accepted reader dependency and task/architecture contracts.

### Validation Reviewed

- Architect rerun of required route/access-policy/i18n suite: **72 passed across 3 files**, exit 0.
- Architect rerun of full typecheck: exit 2, **171 diagnostics in 27 files**, none task-changed. Full lint: exit 1, **20 errors and 2 warnings**, none task-changed. All 37 distinct diagnostic files across both checks were compared byte-for-byte to the starting commit `30c69f8` and are unchanged. The access-policy syntax repair legitimately exposes older semantic debt; it does not establish a clean repository baseline. Reported focused ESLint success is consistent with the full lint result.
- All 20 catalogue diffs add exactly 36 keys each, with no existing values changed; catalogue parity and ICU validation pass in the required suite.
- Reviewed actual submitted responsive screenshots and detailed keyboard/search/status/date/next/previous/error-refresh browser evidence. Native controls, focus styles, wrapped RTL/long customer text and mobile layout agree with source. These are synthetic local component checks, not deployed Shopify embedding evidence; no independent browser replay or live-service check claimed by this review.
- Accepted SHOPIFY-001 reader source is unchanged from `08af00b`. Dedicated task worktree is clean; prepared baseline, recursive database gitlink `9c6a4d8`, synchronization and durable claim evidence agree with report/history. Committed-diff whitespace checks pass.

### Architecture Conformance

The bounded read-only browsing surface conforms. Repairing the malformed/stale access-policy tests is appropriate because this task directly changes that policy; no unrelated permission broadening or source repair occurred. No top-level navigation, detail route, mutation control, schema change or provider flow is introduced. Full embedding and terminal system validation remain later tasks. The complete architecture is not Implemented.

### Follow-up

SHOPIFY-003 is Complete at Attempt 1; claim cleared. SHOPIFY-002 is currently Review at Attempt 3 in its canonical parent worktree and is not accepted by this review. SHOPIFY-004 remains Pending until SHOPIFY-002 is Complete; SHOPIFY-005/006 and SYSTEM-TEST-001 remain gated. Preserve all current execution claims and reconcile accepted dependency copies into downstream task branches when their full dependency set is satisfied. Developer integration of the accepted implementation remains separate. Review publication follows the developer-delegated parent task commit/push workflow; no main merge/push or deployment performed.
