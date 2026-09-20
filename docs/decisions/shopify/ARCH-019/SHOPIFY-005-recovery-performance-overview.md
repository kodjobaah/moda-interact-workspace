---
id: ARCH-019-SHOPIFY-005
architecture_id: ARCH-019
title: Replace the usage-first home page with the recovery overview
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 60
executor: codex
claimed_at: 2026-09-20T15:45:23Z
attempt: 2
depends_on:
  - ARCH-019-SHOPIFY-001
  - ARCH-019-SHOPIFY-003
  - ARCH-019-SHOPIFY-004
enables:
  - ARCH-019-SHOPIFY-006
  - ARCH-019-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Replace the usage-first home page with the recovery overview

## Architecture

Architecture ID: ARCH-019

Architecture document: docs/architecture/ARCH-019-merchant-recovery-experience.md

Coordinator: moda_architect. Read the complete parent architecture and referenced dependency tasks before execution; it supplies exact data, route, access, compatibility and rollout contracts.

## Objective

Make home answer recovery-performance questions with truthful cohort metrics and bounded data loading.

## Context

This task contributes one bounded capability to the recovery-first merchant journey. The previous UI mixed billing-period navigation, all-time recovery figures and a customer modal. The new design separates recovery performance, recovery conversation history and billing usage.

## Scope

app/routes/app/home/route.jsx; overview/dashboard components and styles; relevant home tests and locale catalogues. Existing pending-recovery and billing-setup components may be composed, but their business policy is not owned here.

## Out of Scope

Other repository implementation; billing/credit/provider semantics; new automated messages; reply/takeover controls; unrelated refactoring; main merges/pushes; live deployment. Do not start enabled tasks. Parent architecture/index reconciliation belongs to moda_architect.

## Requirements

The parent architecture's behavioural contracts are binding. Preserve current tenant/lifecycle rules and accepted ARCH-017 onboarding behaviour; do not restore stale ARCH-013 permissions. Follow repo-local AGENTS.md and the assigned logical agent definition. Never copy mockup sample data into production. Preserve unrelated changes by using canonical task worktrees.

## Work Items

- [x] Render the agreed performance metrics, five recent recoveries and date controls using SHOPIFY-001; link into the list/detail routes with preserved date context.
- [x] Show current recovery capacity using the existing authoritative billing projection, clearly separate from historical date filters; preserve source/expiry distinctions and unavailable states.
- [x] Preserve onboarding, billing-setup and restriction banners and the current pending-recoveries capability gate; label pending queue candidates separately from ongoing durable recoveries.
- [x] Remove the home path’s unbounded recovery/message/usage-event hydration and full-payload debug logging; no synthetic metrics or guessed product details.
- [x] Redirect authorized legacy /app?view=detail&bill=... requests to /app/usage with validated bill context before performance reads; leave initial onboarding behaviour unchanged.

## Interfaces / Contracts

SHOPIFY-001 aggregate/list DTOs; existing billing capacity and onboarding services remain authorities. No billing mutation or usage-accounting changes.

## Dependencies

- ARCH-019-SHOPIFY-001
- ARCH-019-SHOPIFY-003
- ARCH-019-SHOPIFY-004

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

- ARCH-019-SHOPIFY-006
- ARCH-019-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Metrics/list cohort definitions match; empty data, unknown values and mixed currencies display without invented totals or percentages.
- [x] No all-shop messages or usage history is fetched to render Overview; the old customer modal is not reachable from the new home.
- [x] Historical lifecycle states retain readable performance/history; capacity exhaustion alone does not hide past records.
- [x] An empty pending queue does not imply recovery is healthy, disabled, or fully complete.
- [x] Legacy bookmarked billing-detail URLs land on billing usage, not silently on an unrelated date cohort.
- [x] Overview links work with dates and merchant embed context, and locale keys have parity.

## Validation

- [x] Run npm test -- tests/unit/home-route.test.ts tests/unit/recovery-overview.test.ts tests/unit/merchant-pricing-usage-overview.test.jsx tests/unit/merchant-i18n.test.ts (update obsolete assertions deliberately).
- [x] Run npm run typecheck, npm run lint and git diff --check.
- [x] Verify local browser fixtures for ACTIVE, ONBOARDING, NO_CONTRACT, FROZEN, BILLING_ATTENTION, zero history, capacity unavailable and legacy URL entry.

New test filenames above are required deliverables, not claims that those suites already exist. Use current package.json scripts; do not invent success when a command cannot run. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md: fast local checks are agent-owned; long infrastructure/live commands are developer-owned unless exactly authorized. Required developer evidence may remain pending at review, never at acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's Work Items, Acceptance Criteria, Validation and Completion Report, publish task-owned mirrored branches and return to review. Record exact pending developer-validation commands if needed. Stop; do not start enabled tasks, merge/push main, or mark your own task Complete.

## Implementation Notes

Use scripts/start-agent-task.py through the normal /moda-task preparation path. Task creation has not claimed execution. Dedicated parent and implementation worktrees, synchronization and recursive database submodule preparation are mandatory when execution starts. Follow docs/agent-vcs-ownership-policy.md. The repository agent may update only this task's execution/report fields in parent docs; shared indexes and parent architecture remain architect-owned.

## Completion Report

### Status

Ready for Review. Attempt 1 implemented by codex on 2026-09-20. No architect acceptance decision made.

### Files Changed

Implementation commit `d5319e8eacd075e5d8cba633b4459ce150872042` changes 37 files:

- `app/routes/app/home/route.jsx` and `overview.server.ts`: bounded cohort loading, validated legacy redirect, preserved lifecycle/onboarding and pending gates.
- `app/components/dashboard/RecoveryOverview.tsx` and `.css`: metrics, date controls, five-row preview, source-specific current capacity and billing composition.
- `app/components/dashboard/PendingRecoveries.jsx`: optional date/embed URL context for pagination/refresh, explicit prop types and React import; admission/queue business policy unchanged.
- Twenty `app/i18n/locales/*.json` catalogues: nineteen overview keys each; all prior parsed values preserved.
- Required home, overview and pricing-overview tests, shared synthetic fixture, browser fixture/readme and four screenshot artifacts under `tests/browser/recovery-overview/`.

Parent changes are limited to this task file. Architect Review is preserved verbatim.

### Work Completed

- Replaced home’s all-shop recovery/conversation/message hydration, billing-period usage includes, usage-event scans and payload logging with accepted SHOPIFY-001 `readRecoveryOverview`. The existing two-read repeatable-read transaction supplies the date cohort summary and five newest rows.
- Home accepts merchant-local date filters only, with accepted normalization, today/7/30/custom controls and bounded invalid-input presentation. List status/search/cursor do not alter overview metrics. List, ongoing and detail links preserve dates and trusted shop/host/embedded context.
- Zero cohort rate/value use em dashes; unknown-only value is unavailable; known currency groups remain separate decimal strings; omitted counts are localized. No revenue uplift, product, comparison or message-count metrics invented.
- Current capacity is separate from historical filters and preserves source balances, reservations, refunding and known paid-period end. Null projection remains neutral Unavailable. Exhaustion/restrictions do not hide history.
- Preserved original onboarding and durable billing-setup precedence, restriction/cancellation/pending-plan notices, no-contract plan catalogue and management flow. Pending candidates are explicitly distinct from ongoing durable recoveries and do not imply service health when empty.
- Legacy authorized `view=detail` requests redirect before capacity/performance/pending reads. Billing mode is allowlisted, bill ID is bounded and tenant-validated by a single `findFirst`, and only validated billing/embed parameters are retained. Initial onboarding still returns onboarding/setup.

### Validation Results

Agent-executed:

- Required command `npm test -- tests/unit/home-route.test.ts tests/unit/recovery-overview.test.ts tests/unit/merchant-pricing-usage-overview.test.jsx tests/unit/merchant-i18n.test.ts`: 47 tests passed. Final run adds `tests/unit/pending-recoveries-display-state.test.ts`: **49 tests / 5 suites passed**.
- `npm run typecheck`: nonzero, **131 diagnostics in 23 unchanged files**. Every diagnostic file compared byte-for-byte with its pre-implementation HEAD version; no changed/new task-owned file has a diagnostic. Removing old home hydration and typing the touched pending component also removes existing diagnostics on those paths.
- `npm run lint`: nonzero, **20 errors and 2 warnings in 15 unchanged files**. All diagnostic paths compared unchanged against pre-implementation HEAD. Explicit focused ESLint over all changed/new JS/TS code, fixtures and tests passed.
- `git diff --check` and staged whitespace check passed.
- Locale parity/ICU formatting passed for all 20 catalogues. Independent parsed comparison confirmed nineteen additions per locale and no previous value changes.
- Local browser fixtures verified ACTIVE, ONBOARDING, NO_CONTRACT, FROZEN, BILLING_ATTENTION, empty history, unavailable capacity, legacy billing entry, error and loading states. Custom 5–12 September dates survive form submission, list and direct detail navigation with embed context. At 1024/320/390 viewport widths there is no horizontal overflow; French and RTL checked at 390. Evidence and limitations are documented in `tests/browser/recovery-overview/README.md` and its screenshots.
- Temporary fixture server and agent-created browser tab stopped/closed; viewport override reset.

No live Shopify or infrastructure commands were required or executed. Browser fixture redirects/destinations are synthetic; production authorization, tenant validation and redirect order are covered by loader unit tests. Terminal architecture system-test work remains outside this task; enabled tasks were not started.

### Deviations

No business-contract deviation. Existing capacity DTO has no promotional expiry timestamp: show explicit unavailable expiry instead of guessing or changing the billing service contract. Full repository checks retain the above unrelated baseline failures; focused checks pass.

### Assumptions

Consumed accepted SHOPIFY-001/003/004 source present in prepared implementation HEAD `dbed756007823990d4e325911ec6d4a141d5b659`; dependency completion was verified by the launcher from the authoritative parent task branch. Historical recovery cohort semantics remain owned by SHOPIFY-001, and billing/pending admission remain their existing services’ responsibility.

### Unresolved Issues

Unrelated full typecheck/lint baseline failures remain. No task-owned validation failure remains. Promotional expiry is unavailable in the existing projection and is labelled accordingly.

### Architectural Concerns

None requiring a contract change. Capacity projection remains read-only, and no billing/provider/accounting or recovery-admission semantics were modified.

### Git / VCS

- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent physical worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-019-SHOPIFY-005`.
- Implementation physical worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-019-SHOPIFY-005`.
- Both branches: `task/ARCH-019-SHOPIFY-005`.
- Prepared launcher reused/synchronized parent, incorporated origin/main and recorded parent HEAD `8a79dd07f18d6e3746a405347b443077911178ed`; created/synchronized implementation with main already current at `dbed756007823990d4e325911ec6d4a141d5b659`. No repeated startup synchronization performed.
- Recursive submodule sync/update verified database commit `9c6a4d8402a01840e2ea8dc18e89171f00564d29` ready; no remote-tracking submodule update used.
- Attempt 1 claim committed/pushed as `7c1847f1cf2f651d920e7648944106f84280f879` at `2026-09-20T14:59:09Z`.
- Implementation `d5319e8eacd075e5d8cba633b4459ce150872042` committed and pushed successfully to `origin/task/ARCH-019-SHOPIFY-005` in the verified `kodjobaah/moda-interact` origin.
- This report is the parent task review-submission commit, published on the mirrored parent task branch. Commit identity is recorded by Git and reported in the final execution response.
- No parent service Gitlink, architecture/index/rollup, other task, or main branch changed. No merge into main, main push, force push, deployment, or enabled-task execution performed.

## Architect Review

### Review Status

**Changes Requested — Attempt 1, 2026-09-20, moda_architect.**

Reviewed implementation `d5319e8eacd075e5d8cba633b4459ce150872042` and report `eac1c4302cb1b6d1fb64011760d1eb0e9ea44fc7`; both remote task heads verified. Task returns to Ready, executor/claimed_at cleared, attempt 1 preserved. No architect acceptance is granted.

### Review Notes

**[P2] Do not silently replace an explicitly requested unavailable billing period (`app/routes/app/home/route.jsx:120-128`).** The new legacy redirect retains `billId` only when the tenant-scoped lookup succeeds. For a well-formed unknown/deleted/foreign ID it redirects to `/app/usage?shop=...&bill=current|past` without that ID. Usage then selects its default OPEN/CLOSED period. Thus an explicit bookmark can show a different period's usage with no unavailable indication. The architecture's Billing bridge contract requires an explicit unavailable/not-found state for an unknown or foreign requested period; defaults apply only when no billId was requested.

For example, an authorized request to `/app?view=detail&bill=past&billId=missing-period` whose lookup returns null loses its explicit selection and displays the default past period. `tests/unit/home-route.test.ts` currently asserts this lossy behavior in “drops unauthorized or malformed legacy bill ID”. This also prevents SHOPIFY-006's planned Usage not-found handling from distinguishing the request later: the selection has already been discarded upstream.

Preserve a safe, explicit unavailable outcome for a requested period that cannot be validated, while keeping only validated billing/embed context and maintaining identical missing/foreign behavior. Do not use an arbitrary return URL, expose another tenant's data, or treat an unvalidated ID as authority. Keep the correction bounded to legacy compatibility; the broader bounded Usage implementation remains SHOPIFY-006. Update regression coverage to distinguish absent ID (default allowed), valid owned ID, and explicit missing/deleted/foreign or malformed ID (no silent period substitution). Retain onboarding/restriction precedence and redirect-before-performance-read coverage.

### Reviewed Files

Home loader and overview service; RecoveryOverview component/styles; pending component changes; existing lifecycle banner and capacity DTO; Usage period-selection consumer; required unit tests; local browser fixture README/mobile screenshot and task completion/isolation report.

### Validation Reviewed

- Architect reran the required expanded command: `npm test -- tests/unit/home-route.test.ts tests/unit/recovery-overview.test.ts tests/unit/merchant-pricing-usage-overview.test.jsx tests/unit/merchant-i18n.test.ts tests/unit/pending-recoveries-display-state.test.ts`: **49 tests passed across 5 suites**. The legacy invalid-ID test currently codifies the reported defect.
- Architect reran full typecheck: **131 diagnostics in 23 files**; full lint: **20 errors / 2 warnings**. All **33 distinct diagnostic files** are unchanged from prepared implementation base `dbed756`. These remain baseline failures, not clean global checks.
- Committed-diff whitespace check passed; implementation worktree clean. Submitted browser evidence covers synthetic lifecycle, responsive, date and link scenarios; no independent browser replay or live Shopify validation is claimed by this review.
- Dedicated mirrored worktrees, prepared synchronization, accepted dependency consumption, recursive database state and durable Attempt 1 claim are recorded and consistent with inspected history. Architect made no implementation edits.

### Architecture Conformance

Inspected bounded cohort loading, separate current capacity, preserved lifecycle/pending gates and date/embed links conform to their contracts. Legacy explicit-period fallback remains an unresolved task-owned compatibility failure. ARCH-019 remains In Progress; SHOPIFY-006 and terminal SYSTEM-TEST-001 remain Pending.

### Follow-up

moda_app must reclaim SHOPIFY-005 for Attempt 2, correct the legacy unavailable-period outcome, rerun the relevant validation and submit both mirrored branches. Preserve this review and Attempt 1 evidence. No downstream task was promoted or launched.
