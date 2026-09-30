---
id: ARCH-020-SHOPIFY-001
architecture_id: ARCH-020
title: Expose merchant capability feature preferences
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 170
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-020-SHARED-001
  - ARCH-016-SHOPIFY-002
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Expose merchant capability feature preferences

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Let merchants select eligible optional features while retaining the existing discount-policy controls.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Embedded merchant feature-selection read/action/UI services and existing recovery-settings integration only.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

### Duplicate-action protection

Every state-changing or costly UI action in this task must prevent duplicate
activation, including mouse double-click, double-tap, Enter/Space repetition and
form-submit plus button-click combinations. Acquire a synchronous submission
guard before awaiting work (a render-delayed disabled state alone is insufficient),
and route all activation paths through the same submit handler. Disable the
trigger and conflicting controls immediately, show a meaningful pending label,
and expose accessible busy/status feedback. Do not lock unrelated navigation.

Keep the guard until the operation has definitively completed, failed or been
cancelled. A client timeout is an unknown outcome: reconcile the original
operation before allowing a retry, rather than silently creating a second one.
On a known failure, restore controls and preserve input for an intentional retry.
Ignore stale completions so an earlier request cannot reset a newer request's
pending state. Debounce alone is not sufficient for mutations or paid previews.
Server authorisation and duplicate protection are required independently of the
browser controls; inspect direct duplicate requests as well as UI behaviour.

## Work Items

- [x] Load arbitrary Admin-created feature identities and current plan mappings from the database; do not whitelist development seed keys. Creating a Feature alone does not establish plan eligibility. Test a newly created non-seed key through enabled mapping and opt-in, including absent preference. Absence of Commerce configuration must not rewrite a billing feature or its saved preference.

- [x] Keep merchant UI selecting existing features; tools/templates are team-configured in Studio and selected via the capability's feature binding. Do not expose tool authoring to merchants.

- [x] Preserve existing merchant followUpEnabled/followUpDelayMinutes controls, max one no-response follow-up, delay validation and credit-warning copy. C13 distinguishes a separately chargeable proactive follow-up from conversational replies; do not introduce another follow-up editor or reset pending schedules from feature saves. Include double-submit tests for this existing settings form.

- [x] Inspect current feature-selection surfaces and reuse them where present; local source inspection found no ShopFeaturePreference editor to rely on.
- [x] Present active eligible feature keys with current enabled/effective state and persist authenticated ShopFeaturePreference changes.
- [x] Use the shared pure selection contract with authoritative plan facts; enforce ownership/eligibility server-side and preserve ALWAYS_ENABLED/system-required policy.
- [x] Keep NONE/FIXED/AI offer choice in existing Recovery Settings, available to eligible Free and Paid shops; explain its effect on discount assistance.
- [x] Add locale-complete labels and loading/denied/error states without exposing Studio internals or creating another feature catalogue.

- [x] Guard preference switches and feature/recovery-settings save actions. Send explicit desired values, never a toggle command; use the existing unique shop/feature preference and transactional upsert/update-if-changed semantics. Duplicate equal-value requests produce no second state transition or secondary effect. Serialize conflicting writes for the same form/resource and ignore stale UI responses.

## Interfaces / Contracts

Existing Feature/plan mappings/ShopFeaturePreference and ARCH-016 recovery policy; shared selection DTOs.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C1, C9**. Also apply **C13** for outreach/continuation semantics. These are required acceptance inputs, not optional examples.

Implement a feature-preferences service/action and embedded page using current Shopify session ownership, never caller-supplied shopId. Display authoritative active eligible mapped features; disallow edits to ALWAYS_ENABLED/systemRequired or inactive/unmapped items. Write explicit desired enabled value with unique shop/feature row. Keep existing recovery-offer form as the only NONE/FIXED/AI editor.

### Required evidence

Use Free/Paid, enabled/disabled mapping, active/inactive feature, missing opt-in, required feature and override fixtures. Test forged shop, same-value concurrent requests and conflicting same-form requests with refetch. Add all labels to existing supported locale files; run declared locale checker or document if none exists.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-SHARED-001
- ARCH-016-SHOPIFY-002

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-012

- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Unauthorised, inactive, other-shop and plan-ineligible preferences cannot be written through direct actions.
- [x] Merchant selection drives the initial capability grant for a new conversation; billing/plan prices and existing admin override precedence are unchanged.
- [x] Discount assistance is not accidentally introduced as a paid-only feature.

- [x] Double-clicking a switch or Save results in the intended state once, not an immediate reversal, duplicate preference row or repeated secondary action. Direct repeated requests are idempotent; validation/network failure preserves inputs and restores controls for a deliberate retry.

## Validation

- [x] Feature on/off fixtures alter tools for eligible new conversations; existing grants never gain newly mapped tools. Recovery-policy discount access retains its existing semantics.

- [x] Test same-tick mouse double-click, repeated keyboard/form submission, delayed success, known error/cancel and timeout with unknown outcome; assert one operation, visible pending state, preserved input and a deliberate successful retry. For server mutations/previews also send concurrent duplicate requests directly and verify persisted effects/provider invocation counts.
- [x] Run focused merchant action/selection policy tests and declared typecheck/lint/localisation validation.
- [x] Inspect embedded UI with local fixtures for Free/Paid, opt-in/required, disabled feature and override states.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; its real repository must be provisioned before execution preparation.

## Completion Report

### Status

Ready for Review — Attempt 1, implemented by codex on 2026-09-20. Repository-local evidence is complete; no architect acceptance or downstream promotion is asserted.

### Files Changed

- `app/services/feature-preferences/{access.server,feature-preferences.server}.ts`: authenticated ownership, database eligibility, Shared selection and serialized explicit-value persistence.
- `app/routes/app/settings-save/route.ts`, `app/routes.ts`: authenticated resource action with strict field allowlist, correlated responses and conflict/denied/validation results.
- `app/components/settings/{FeaturePreferences,SettingsForm}.tsx`, `submission.ts`: existing feature identities, immutable required features, synchronous form exclusion, accessible pending/error/status feedback and frozen-intent reconciliation.
- Recovery Settings route/view and recovery-policy service: reuse the existing policy editor, revision checks and update-if-changed transactions; retain override precedence and follow-up controls.
- All 20 existing locale files: 15 feature labels each. Existing text and duplicate entries preserved.
- `package.json`, lockfile: exact published Shared 0.13.1; jsdom development dependencies for real DOM tests.
- Six focused unit test files, PostgreSQL integration fixture and isolated `tests/fixtures/settings-preview` browser fixture.

### Work Completed

Arbitrary database feature keys are loaded through active features and enabled mappings on an active plan/subscription. Missing opt-in is false. ALWAYS_ENABLED and systemRequired features are not editable; systemRequired does not bypass plan eligibility or opt-in semantics. No Commerce configuration is required to retain a billing feature/preference. Shared `selectCapabilities` evaluates authoritative facts; local synthetic binding keys are only an adapter for deriving effective feature state, not a second published capability catalogue.

Actions derive the shop from `authenticate.admin` and the existing shop/access policy. Caller shopId fields are rejected and query ownership is ignored. Feature writes lock the active shop row, re-read eligibility, compare a snapshot revision and upsert only changes against the existing unique shop/feature key. Equal-value requests do not update timestamps. Stale conflicting forms require refetch. Recovery writes use the same serialization and unchanged-policy short circuit, preserving current discount validation and Admin override precedence. Neither path invokes providers, edits billing prices, creates grants, sends messages or resets outreach schedules.

Switch autosave and both Save buttons use one synchronous controller per form. Controls disable before awaiting; duplicate click/form/keyboard paths are excluded. Known failure retains input and permits intentional retry. Timeout/network failure keeps the form locked; Check status replays the frozen original operation ID, desired values and revision. Repeated reconciliation activation is guarded, and superseded/disposed responses cannot reset a newer operation. Strict Mode mount cleanup is covered.

### Requirement-to-Fixture Matrix

| Requirement | Fixture and expected side effects | Result |
| --- | --- | --- |
| Arbitrary identities, Free/Paid, absent opt-in | PostgreSQL non-seed keys, both plan kinds, missing preference -> false; inactive/unmapped omitted; required/ALWAYS immutable | Passed; no writes for denied identities |
| Inactive/other-shop/unauthorized | PostgreSQL frozen subscription, inactive plan, uninstalled shop; action auth rejection, forged body shopId and query shop | Passed; no cross-shop preference writes |
| Direct duplicates | Two concurrent equal desired values; repeat with original revision | Passed; one unique row, unchanged timestamp on repeat, recovery settings unchanged |
| Conflicting forms/refetch | Concurrent changes from one revision; fresh read then resubmit; mapping disabled afterward | Passed; one winner, stale conflict, fresh success; saved preference retained after mapping removal |
| Initial selection/original provenance | Persisted opt-in feeds Shared selection + tool deduplication; original empty grant filtered with new eligibility | Passed; new initial tools change, original grant cannot gain tools; no Background admission execution claimed |
| Discount policy and overrides | Shared NONE/FIXED/AI for Free/Paid; existing parser/discount eligibility unit cases; PostgreSQL AI merchant policy with active NONE override and expiry | Passed; policy selection remains independent of paid feature gating; expiry restores merchant policy |
| Recovery duplicate action/follow-up | Concurrent identical recovery saves, stale differing save; existing delay/parser validation and one-follow-up copy retained | Passed; equal requests return the same updatedAt, stale request conflicts; no scheduling/provider call added |
| Switch/Save repeated activation | jsdom actual components, double checkbox click, double Save and repeated submit events; browser repeated Enter | Passed; one request, no immediate reversal, controls disabled and visible pending state |
| Failure/unknown/stale lifecycle | Deferred promises, known failure followed by successful deliberate retry, timeout, frozen reconciliation, rejected request, stale response and disposed view | Passed; input retained; unknown never unlocks for a new intent; matching success unlocks |
| Localized UI | 15 feature keys in all 20 locales; all 38 existing recovery keys | Passed; no separate locale CLI is declared, so focused locale tests are the checker |
| Rendered UI | Local actual-view fixture: Free off, Paid on, required on/disabled, empty eligibility, active override vs merchant NONE | Inspected in in-app browser; visible toggles and all recovery options preserved |

### Validation Results

Agent-executed, using Node 24.19.0 via the primary workspace bootstrap and the isolated implementation worktree:

```bash
npm run prisma:generate
MODA_SETTINGS_POSTGRES=1 npm test -- tests/integration/merchant-feature-preferences.test.ts
npm test -- tests/unit/settings-submission.test.ts tests/unit/recovery-settings-submit-guard.test.tsx tests/unit/merchant-settings-action.test.ts tests/unit/merchant-features-i18n.test.ts tests/unit/recovery-settings-i18n.test.ts tests/unit/recovery-policy.test.ts
npm run lint
npm run typecheck
npm run build
git diff --cached --check
```

- Prisma generation: passed against the pinned database source.
- PostgreSQL: **6/6 passed**, about 10 seconds, disposable PostgreSQL 15 with the pinned migrations and automatic teardown.
- Focused tests: **18/18 passed**, six files, about 2 seconds. Includes actual DOM tests rather than source-string guards.
- Build: passed.
- Diff whitespace check: passed.
- Full typecheck: failed with **76 diagnostics**, all in unchanged files; none in task-modified/new files. Existing repository debt is tracked by `docs/development-baseline.md` / TYPECHECK-001.
- Full lint: failed with **19 errors and 2 warnings**, all in unchanged files (billing/dashboard, privacy, recovery cursor and existing tests); no task-file diagnostic. These checks are not reported as globally passing.
- Local UI command: `npm exec vite -- --config tests/fixtures/settings-preview/vite.config.ts --host 127.0.0.1 --port 4182`. Inspected `?scenario=free`, `paid`, `override`, `empty`; Free switch double activation and repeated Enter on Paid Save showed pending disabled controls. Fixture saves are synthetic; database persistence evidence comes from the PostgreSQL tests.
- Shopify AI Toolkit documentation search was run with instrumentation disabled for authenticated embedded requests; resource actions retain `authenticate.admin`.

No developer-owned long/live validation was launched. No task-specific live validator is declared. Actual embedded Shopify authentication and cross-service conversation admission remain integration validation for the developer and explicitly invoked ARCH-020-SYSTEM-TEST-001, rather than claims from this local fixture. Do not invent a system-test command before that task's harness exists.

### Deviations

The persistent local database has an older incompatible BillingPlan schema (`defaultOutboundSoftLimit` required outside the pinned Prisma model). Validation uses the repository's existing disposable Testcontainers approach, applying the exact pinned migrations; the persistent schema was not changed. The initial failed fixture setup created no merchant rows there. A fixture status was corrected to the pinned FROZEN enum before the final passing run.

The old recovery locale expectation omitted five already-existing catalogue labels; it now validates all 38. The old submit-guard source-string test was replaced by behavioral DOM evidence. No second feature catalogue, discount editor, Studio surface or schema change was introduced.

### Assumptions

Published Shared 0.13.1 is the accepted consumer dependency. Background owns production conversation admission and preservation of original grants; this task proves the persisted preference/Shared selection boundary, not deployment of downstream consumers. Admin catalog text is displayed as data, while application labels are locale-complete.

### Unresolved Issues

Repository-wide typecheck/lint debt remains outside this task. Local fixture evidence does not establish live Shopify or cross-service behavior. No additional task-scoped implementation defect is known.

### Architectural Concerns

No contract/schema change is requested. Revision tokens are repository-local concurrency controls, not Shared wire identities. Required features retain the canonical activation/eligibility semantics rather than acquiring an entitlement bypass.

### Git / VCS

- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-SHOPIFY-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-SHOPIFY-001`.
- Both branches: `task/ARCH-020-SHOPIFY-001`; no other task worktree reused, and neither shared checkout was switched or edited for task implementation.
- Launcher start-of-attempt synchronization: new task branches; remote task fast-forward not needed; parent and implementation origin/main already current. Initial parent `05d3dfa3dea5dc71633fed4e4cab9d401b6cf329`; initial implementation `f92e06c3a3f6bb9b9947a0185acde8257076b981`.
- Recursive database submodule materialized and generated at `5abfd87f57038bae515aaa09ec7c8db62adcfb98`; no pin update.
- Parent claim `8f18471bac7613c70fd2f972bb839591f06a6fd4` was pushed before implementation. Attempt 1 retained.
- Implementation commit **4693bba629fd53812b819c7dc43c52673a2bdab7**, pushed to `origin/task/ARCH-020-SHOPIFY-001`.
- Parent review submission: the commit containing this report (`task(ARCH-020-SHOPIFY-001): submit for architect review`), published to the matching parent remote task branch; exact resulting SHA is returned in the execution response.
- Parent staging is restricted to this task file. No service gitlink, Architect Review, architecture/index/frontier or main branch changed. Neither branch was merged to main.

## Architect Review

### Review Status

**Accepted — Complete at Attempt 1, 2026-09-20, moda_architect.** Reviewed
implementation `4693bba629fd53812b819c7dc43c52673a2bdab7` and report
`c5016d73f1a7241cfbc661f4b0a0a8d43f044eda`; both published task heads verified.
No blocking functional findings remain. Automatic completion applies.

### Functional Review

Shop identity comes from authenticated Shopify session/access resolution; direct
actions reject caller shop fields. The service loads arbitrary active database
features through enabled current-plan mappings and denies inactive shop,
subscription or plan state. Shared 0.13.1 selection preserves missing-opt-in,
ALWAYS_ENABLED and systemRequired semantics without adding entitlement bypasses
or a second feature catalogue. Required features cannot be changed through the
merchant action. Disabled mappings retain saved preferences without granting use.

Explicit desired-value writes serialize on the shop row, re-read eligibility and
compare revisions before changes. Equal-value repeats return current state without
another timestamp update; conflicting changes require an authoritative refresh.
Feature saves do not modify recovery settings, schedule outreach or call providers.

The actual form/switch components use synchronous submission exclusion, immediate
pending controls, frozen-intent reconciliation and stale/disposed-response guards.
Known failures retain input for retry; an unknown outcome stays locked while the
same original values are reconciled. The existing recovery form remains the sole
NONE/FIXED/AI editor, retains follow-up delay/credit controls, and preserves Admin
override precedence and Free/Paid availability. No new billing or Studio surface.

### Validation Reviewed

- Architect reran the six focused unit/DOM/action/locale/policy files: **18 tests
  passed**, including duplicate activation, failure/retry, unknown outcome and
  response correlation. Committed whitespace check passed.
- Reviewed supplied **6 passing PostgreSQL integration tests**, including arbitrary
  feature identities, eligibility denial, equal-value concurrency, stale conflicts,
  preserved preferences and unchanged recovery state. This local persistence plus
  Shared selection evidence supports the scoped merchant boundary; it does not
  claim deployed Background conversation admission.
- Reviewed supplied build and browser fixture checks and locale completeness for
  all 20 locales. No redundant PostgreSQL/build/browser rerun was required.
- Full typecheck/lint remain reported failures in unchanged files: 76 TypeScript
  diagnostics (TYPECHECK-001), 19 lint errors and 2 warnings. These are retained
  limitations, not represented as globally passing or task-created defects.

### Ownership and Follow-up

Reviewed the changed services/resource action, route/view integration, submission
controller/components, recovery-policy delta, exact Shared dependency, locale and
validation changes. Prepared claim `8f18471b`, dedicated mirrored worktrees,
start-of-attempt synchronization, accepted prerequisites and unchanged database
pin `5abfd87f57038bae515aaa09ec7c8db62adcfb98` are recorded consistently. No
implementation edit, gitlink update, main integration or downstream launch by review.

The developer owns final integration. SYSTEM-TEST-001 is the sole enabled task;
its other implementation prerequisites remain incomplete, so it stays Pending
and explicitly developer-invoked. ARCH-020 is not Implemented. Existing live
Shopify/cross-service validation remains part of that terminal integration boundary.

## Dependency readiness — 2026-09-20

All listed prerequisites are architect-accepted Complete following SHARED-001 Attempt 2 acceptance. Consume exact published Shared 0.13.1 (commerce and commerce/runner exports). Ready is eligibility only: no claim or execution is made by this review. Normal preparation must synchronize the canonical task worktrees and verify dependency source availability; do not silently use an older database/service revision.
