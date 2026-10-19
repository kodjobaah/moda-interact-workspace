---
id: ARCH-035-WOOCOMMERCE-004
architecture_id: ARCH-035
title: Add Shopify-parity Merchant Knowledge section within Recovery Settings
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-035-WOOCOMMERCE-003
enables:
  - ARCH-035-SYSTEM-TEST-001
created: 2026-10-11
updated: 2026-10-19
---

# ARCH-035-WOOCOMMERCE-004: Add Shopify-parity Merchant Knowledge section within Recovery Settings

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: portable architect definition materialised on the canonical parent task branch `task/ARCH-035-WOOCOMMERCE-004`; implementation task branch/worktree is being prepared for Attempt 1.

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-004` for this ready task. Execution and completion ownership are taken over from the assigned agent: `execution_mode` and `completion_mode` are now `developer`/`developer`; logical ownership remains `assigned_agent: moda_woocommerce`. Scope, dependencies, acceptance criteria and validation requirements are unchanged. Attempt 0 remains unclaimed until canonical preparation and dependency verification succeed.

## Objective

Build the Woo Recovery Settings Merchant Knowledge management UI following Shopify source list, add-source and status presentation.

## Context

Shopify MerchantKnowledgeSection.tsx is embedded inside Recovery Settings and supports URL/file source disclosure, plan capacity, status, refresh, reorder, edit, replace and delete. Woo currently has no such section.

Source references:
- Shopify: app/components/settings/MerchantKnowledgeSection.tsx; app/routes/app/recovery-settings/RecoverySettingsView.tsx.
- Woo: src/recovery-settings/recovery-settings-screen.js.

## Scope

- Implement a bounded section with source-count/capacity summary, add URL and upload disclosures, source cards, processing/failure badges and source actions.
- Match approved input concepts (name, purpose/type, language, URL or file) only where supported by the existing service read/write contracts.
- Separate source list, URL form, upload form, individual card, controller and API adapter; preserve URL safety and file validation at browser boundary.
- Do not create hosted upload intent or R2 CORS changes; when absent show explicit unavailable status and disable unsupported actions (including uploads).
- Preserve the Shopify-equivalent Merchant Knowledge accordion and vertically stacked Add web page / Upload file disclosures when the integration is unavailable. Keep inputs and actions non-submittable without an approved catalogue or permission data; show a bounded reason rather than replacing the entire section with only Retry.

## Out of Scope

- New Moda-hosted API routes, data migrations, shared contracts, Background workflow, Woo checkout/order event publishing and provider coupon integration.
- Artificial production records, local mock-success modes, or storage of authoritative merchant data in browser state.
- Shopify UI code copy/paste that imports Shopify authentication or Polaris-only server routes.
- Any `docs/decisions/**/_index.md` changes before explicit final reconciliation.

## Requirements

- Use WordPress Admin as the shell, React via @wordpress/element for content, native gettext/i18n, and existing Woo installation, nonce, capability and disconnect protections.
- Source alignment, accessibility, section placement and state meanings must follow the Shopify reference files named here; only platform chrome/provider-specific actions may differ.
- UI composition and state/transport must be modular; do not enlarge src/page.js or create new catch-all files (target <=200 lines, maximum 300 new production lines per file).
- The assigned task is **UI-only**: no DB schema/migrations, Shared contracts, hosted API implementation, background jobs, event ingestion, order reconciliation, coupon-provenance, payment-provider commands or business-rule changes.
- Do not invent new endpoints or use Shopify authentication from WordPress. The browser may use only an already-approved privileged WordPress API proxy; server-side Woo integration must remain within existing accepted contracts.
- A missing external dependency must not be silently faked. Fixture data are for tests/storyboards only; production shows honest unavailable/disabled states while preserving the page design. In particular, do not display invented source counts, plan limits, purposes, formats, permission grants or configured sources when the read fails. Denied/unauthorised states must remain fail-closed.
- State requests are single-flight or otherwise protected against duplicate clicks, and stale callbacks after disconnect/credential rotation cannot modify current UI.

## Work Items

- [x] Inspect and map source UI: Shopify: app/components/settings/MerchantKnowledgeSection.tsx; app/routes/app/recovery-settings/RecoverySettingsView.tsx.
- [x] Implement the bounded UI using separate presentation, controller/state, and supported transport modules.
- [x] Add fixture-driven component tests for primary, empty, loading, unavailable, denied and error states; assert that service-unavailable preserves the section layout and disables unsupported controls, whereas denied/unauthorised states expose no actionable configuration.
- [x] Provide 20-locales native gettext translation assets and WordPress keyboard/responsive checks.
- [x] Document any unsupported hosted API operation as a gap; never implement or fake a new backend service.
- [ ] At the next authorized developer claim, record launcher-resolved parent and implementation worktree paths/branches and the actual fetch, task-branch fast-forward, and current-`origin/main` synchronization results before execution. Do not infer or backfill Attempt 1 preparation evidence.

## Interfaces / Contracts

- Consume **only** existing approved Woo plugin/browser privileged REST interfaces and existing hosted API responses where implemented. Confirm the exact reachable contract from inspected source before wiring it.
- Do not create cross-repository DTOs or silently invent an `ARCH-035-API-*` prerequisite. If required data/action is unavailable, record an external dependency and keep production state truthful.
- UI fixture interfaces are local tests only; no fixtures enter the production bundle as merchant data.

## Dependencies

- `ARCH-035-WOOCOMMERCE-003` (architect-accepted Complete)

## Enables

- `ARCH-035-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Section is placed within Recovery Settings alongside store/assistant context, not an unapproved top-level page.
- [x] The Merchant Knowledge accordion contains vertically stacked Add web page and Upload file disclosures (not parallel two-column cards), with Shopify-aligned field order and a responsive field grid; web-page format is read-only and file format is selected from the approved catalogue when available.
- [x] In an integration-unavailable state, the complete Merchant Knowledge section remains visible with a clear localised explanation and unsupported inputs/actions disabled. The view does not collapse to an unavailable message and Retry button alone, claim an operation succeeded, or invent capacity, permissions, catalogue entries or source records. Unauthorised/denied views remain fail-closed.
- [x] Plan limits, processing/failure, reorder, refresh and edit controls have truthful disabled/loading/error states.
- [x] Drag/drop or file selection cannot send data to arbitrary cloud endpoints or claim success without server acknowledgement.
- [x] New strings are translated in all 20 supported Admin locales (admin UI locale, site fallback; store/conversation language unchanged).
- [x] Existing Billing/connection/category experience and WordPress capability/nonce safeguards remain intact.
- [x] No backend service or database code is changed.

## Validation

- [x] Focused JS controller/panel tests passed: 21 tests.
- [x] PHP admin navigation/capability/nonce tests not applicable; no PHP files were touched.
- [x] `npm run test:i18n` passed (28 tests); `npm run i18n:verify:20` passed (455 messages, 19/19 translation packs, 38 compiled assets across 20 locales).
- [x] `npm run test:js` passed before the review-driven module split (49 test files, 314 unit tests, and 37 Node integration/i18n tests). After the split, focused controller/panel tests (21), `npm run build`, and `npm run plugin-zip` passed on implementation HEAD `cd5e6d9` (113-entry archive, SHA-256 `cac004d8cd9dc5f02e68e909ee2304fe2316b5eabcd202ee22389a33f0c75cf6`).
- [x] `npm run test:knowledge-browser` passed (3 tests covering native Enter/Space disclosures, unavailable/denied states, narrow-screen stacking and overflow).
- [x] Task-owned Sass lint passed for both Merchant Knowledge partials, and targeted JS lint passed for the changed controller, action validator, and focused tests. Repository-wide `npm run lint:css` and `npm run lint:js` report unrelated Usage History/billing files from current `main`; these repository-wide diagnostics are recorded, not changed by this task.
- [x] `git diff --check` passed. The canonical route resolved the task to parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-004` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-004`. At review submission, implementation branch `task/ARCH-035-WOOCOMMERCE-004` is clean, pushed at `cd5e6d9`, and contains `origin/main`; the parent branch is clean and pushed at `309a24e8`, after its mainline synchronization/report update. This is reconciliation-time evidence only. No durable evidence establishes both worktrees' fetch/fast-forward/mainline state before Attempt 1 execution; do not infer or backfill it. Neither task branch is merged to main.
- [ ] Manual LocalWP checkpoint not performed in this environment; no result is claimed.

## Stop Condition

When Work Items, UI-only Acceptance Criteria and required validation are complete, finish the Completion Report, set task to `review` and STOP for moda_architect. Do not implement deferred cross-repository capabilities. Report unavailable validation accurately.

## Implementation Notes

Match the canonical Shopify page composition rather than the illustrative labels/numbers in the wireframe. Layout is not permission to add unsupported functionality. Keep controlled state, transport and presentational components isolated. Use semantic native WordPress markup and CSS, not a cloned Shopify-only runtime.

Developer-only manual checkpoint (outside repository-agent execution/acceptance): the developer launches LocalWP and checks connected/admin navigation, keyboard/responsive layout and truthful unavailable/error states, recording screenshots/results if desired. The implementing agent must not launch or manually operate LocalWP or claim those checks passed. Automated repository validation remains required.

18 October 2026 developer screenshot observation: Shopify displays the expanded knowledge section with vertically stacked Add web page and Upload file forms, while the captured WooCommerce view displays only the integration-unavailable message and Retry. This establishes a UI fallback gap; it is **not** evidence that live knowledge reads, uploads or source operations were exercised. Address the disabled UI shell here; real data/actions remain W015.

## ASCII Page Design

The following is the **required UI layout/interaction guide**, not invented runtime data, API schema, or pixel-perfect CSS. Bracketed items are placeholders, not sample production records. Show unsupported actions disabled with explanation.

```text
+-------------------------------------------------------------------------------+
| Recovery settings > Store and assistant context                               |
+-------------------------------------------------------------------------------+
| [Merchant Knowledge                         [count/limit if known]  -]          |
| [Feature-off notice only when confirmed by server]                             |
| [Capacity indicator if authoritative; otherwise unavailable explanation]        |
+-------------------------------------------------------------------------------+
| [Add web page                                                       -]          |
| Source name [                 ] Purpose [                v] Format [Web page]  |
| URL         [https://...      ] Language [                v] [Add web page/off] |
+-------------------------------------------------------------------------------+
| [Upload file                                                        -]          |
| Purpose     [                v] Format [CSV / XLSX          v] Name [       ]  |
| File        [Choose file ...]  [Maximum bytes only when supplied by server]    |
| Language    [                v] [Upload file/off]                              |
+-------------------------------------------------------------------------------+
| Sources                                                                       |
| +-------------------------------------------------------------------------+   |
| | [URL] [Source name]     READY       Language: en-GB                  |   |
| | [Move up/down] [Refresh] [Edit] [Delete]                              |   |
| +-------------------------------------------------------------------------+   |
| | [FILE] [Source name]     PROCESSING   [Replace when available]        |   |
| +-------------------------------------------------------------------------+   |
| | [URL] [Source name]     FAILED       [Retry when available]         |   |
| +-------------------------------------------------------------------------+   |
| [Empty / Processing / Error / No entitlement / Integration unavailable]         |
+-------------------------------------------------------------------------------+
```

## Completion Report

### Status

Attempt 1 implementation and automated validation are complete, but the architect returned the review as Changes Requested because durable pre-execution synchronization evidence for both worktrees is missing. The task is `ready`, `executor: null`, `claimed_at: null`, `attempt: 1`; no new attempt has been claimed. Record actual synchronization evidence at the next authorized developer claim before execution. Attempt 1 was claimed by developer at 2026-10-16T17:37:47Z. Attempt 0 remained unclaimed and has no review record.

### Files Changed

Implementation branch `task/ARCH-035-WOOCOMMERCE-004` (HEAD `cd5e6d9`, pushed) adds the Merchant Knowledge presentation, source list/cards, URL and upload forms, controller/action-validation/client modules, connection lifecycle integration, styles split by presentation surface, native gettext catalogs, fixture/controller/component/browser tests, and localized string updates. Relative to current `origin/main`, the implementation contains 59 changed files; no PHP, API, database, shared-contract, or Background files were changed for this task.

### Work Completed

- Embedded the Merchant Knowledge accordion within Recovery Settings > Store & assistant context, with vertically stacked native Add web page and Upload file disclosures and modular source cards/controller/client.
- Kept the production integration unavailable and fail-closed: the current Woo browser adapter has no approved knowledge-source or upload proxy contract, so it returns `KNOWLEDGE_UNAVAILABLE` and exposes no write methods. Unavailable forms and actions remain disabled; no catalogue, capacity, permissions, source records or success responses are fabricated. Denied state exposes no actionable configuration.
- Added localized source status/error presentation, source-capacity handling when authoritative data is available, browser URL/file validation, single-flight writes and stale-request invalidation on disconnect/credential rotation.
- Added keyboard and responsive browser checks, including unavailable and denied states, disabled controls, stacked narrow-screen layout and horizontal-overflow validation.
- Split action validation and source presentation styles into bounded modules to meet the task's per-file production line limit; corrected the Attempt 0 history statement above.

### Validation Results

- Passed on implementation HEAD `cd5e6d9`: focused controller/panel tests (21); `npm run test:knowledge-browser` (3); task-owned CSS lint on both Merchant Knowledge Sass partials; targeted JS lint on changed production modules and focused tests; `npm run build`; `npm run plugin-zip` (113 entries, SHA-256 `cac004d8cd9dc5f02e68e909ee2304fe2316b5eabcd202ee22389a33f0c75cf6`); and `git diff --check`.
- Also passed before the file-boundary-only review correction on parent implementation commit `e9a6a09`: `npm run test:js` (49 files, 314 unit tests and 37 Node checks); `npm run test:i18n` (28); and `npm run i18n:verify:20` (455 source messages, 19 translation packs, 38 generated assets). The corrected modules were then covered by the focused tests, targeted lints, build and package checks above.
- Repository-wide `npm run lint:css` and `npm run lint:js` did not pass after synchronizing current `main`: diagnostics are in existing Usage History/billing files, with no Merchant Knowledge JS diagnostics; task-owned stylesheet lint passes. Those unrelated diagnostics were not modified.
- Build completed with the existing webpack entrypoint-size/performance warning (357 KiB combined entrypoint; recommended limit 244 KiB).
- PHP tests were not run because no PHP files were touched. Manual LocalWP checkpoint was not performed; no live integration, source read/write, or upload behavior is asserted.

### Deviations

- Source operations remain unavailable because no approved Woo privileged proxy contract exists in this task's scope. Production intentionally displays the disabled UI shell; live source management/upload remains a follow-up integration dependency, not an implementation of this UI task.

### Assumptions

The portable definition is materialised on the canonical parent task branch. Attempt 0 is not claimed; any missing hosted API capability remains external to ARCH-035 and may require a separate architecture.

### Unresolved Issues

- No approved Woo API/WordPress proxy currently supports Merchant Knowledge catalogue/source reads, URL source mutations, or upload-intent/file lifecycle operations. These remain external dependencies for the separately scoped WOO-015 integration work; this task adds no endpoint or backend service.
- Repository-wide CSS/JS lint has unrelated diagnostics in current-main Usage History/billing files, recorded above.

### Architectural Concerns

None reported at definition time.

## Architect Review

### Review Status

Changes Requested — Attempt 1. The implementation and focused validation pass, but the required start-of-attempt synchronization evidence is missing. Task state is returned to `ready`; `executor` and `claimed_at` are cleared; `attempt: 1` is preserved.

### Review Notes

The architect reviewed the published implementation at `cd5e6d9` and parent report at `309a24e8`. The previous file-size and Attempt 0 history findings are resolved; no implementation-code correction is requested. The remaining finding is that the report identifies canonical paths and later synchronization, but does not establish the mandatory pre-execution synchronization of both worktrees. The implementation history records synchronization after the implementation feature work had begun, and the parent mainline merge is described as occurring for the report update. Current clean state and ancestry do not prove claim-time state.

### Reviewed Files

`docs/decisions/woocommerce/ARCH-035/WOOCOMMERCE-004-add-woocommerce-merchant-knowledge-management.md`; the published WooCommerce Merchant Knowledge implementation and tests on `task/ARCH-035-WOOCOMMERCE-004` at `cd5e6d9`.

### Validation Reviewed

Architect independently confirmed the focused and full JS, browser, i18n, locale, task-owned lint, build, package and whitespace checks recorded above. The build's 357 KiB entrypoint-size warning and the unrelated repository-wide Usage History/billing lint diagnostics remain accurately disclosed. Manual LocalWP was not run.

### Architecture Conformance

Implementation scope and truthful unavailable/denied behavior conform. Review is not accepted because required workflow preparation evidence is incomplete.

### Follow-up

Before the next developer claim, follow the canonical launcher synchronization sequence for both task worktrees. Record the actual fetch, fast-forward, and current-`origin/main` merge results at claim time; do not manufacture historical evidence. The previous Attempt 1 gap remains as a workflow-conformance finding. After the next authorised developer claim and any required implementation/report reconciliation, request architect review again. Do not increment the attempt as part of this review update.

## Developer Self-Review - Changes Requested (Attempt 1)

### Corrections Required

- At the next authorised developer claim, synchronise both canonical task worktrees before execution as required by `docs/agent-worktree-isolation-policy.md` and `docs/developer-task-workflow.md`. Record launcher-resolved paths/branches and the actual fetch, task-branch fast-forward and current-`origin/main` synchronization result. Do not infer or backfill the missing Attempt 1 preparation evidence.
- Preserve the architect finding that Attempt 1's pre-execution synchronization cannot be verified from the durable record. The implementation itself requires no correction based on this review.

### Validation Reviewed

Implementation at `cd5e6d9` is pushed and clean; focused tests, browser checks, task-owned lint, build, package generation and `git diff --check` passed as recorded above. Parent report at `309a24e8` is pushed and clean. Architect independently confirmed the reported full JS and i18n validations. Manual LocalWP remains unperformed.

### Decision

Return the task to `ready`, clear `executor` and `claimed_at`, and preserve `attempt: 1`. Do not create Attempt 2 in this review. The developer-controlled completion decision is not authorized because this review is Changes Requested.
