---
id: ARCH-030-COMMERCE-001
architecture_id: ARCH-030
title: Complete WooCommerce REST tool Test step
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables:
  - ARCH-030-COMMERCE-002
created: 2026-10-14
updated: 2026-10-16
---

# Complete WooCommerce REST tool Test step

## Architecture

`ARCH-030` — `docs/architecture/ARCH-030-woocommerce-commerce-tool-authoring.md`. Coordinator: `moda_architect`.

## Objective

Replace the WooCommerce Test placeholder with a working, store-specific GET test and preview that gates navigation to Review for the current authorized store and authoring draft.

## Context

The WooCommerce Request, Response and Result Template tabs already create structured drafts. `src/studio/tools/authoring/test/woocommerce-rest-test.tsx` shows a placeholder, while `src/studio/tools/new-tool-editor.tsx` disables Next at Test. The existing revision-based authoring test state can be reused and extended for shop changes and overlapping attempts. The Woo read-operation catalogue is Commerce-local.

## Scope

Only `moda-interact-commerce`: WooCommerce Test component, Commerce-side Woo GET test handler/validation, current-test state and navigation, relevant focused tests. Reuse existing store-specific Woo authorization/transport if demonstrably available; do not create or modify a hosted Moda API feature.

## Out of Scope

WooCommerce Review/Save, new provider catalogue, arbitrary methods/hosts, Woo writes, Shopify/external tools, plugin, Shared, API, Gateway, Database, Background, MCP, merchant Studio rollout and publication/runtime execution.

## Requirements

1. Support every existing operation offered by the WooCommerce Request tab, without per-operation removal based on one store's permissions. Always use the selected store's legitimate authenticated connection; the action must independently authorize store access server-side.
2. Resolve `FIXED` parameters and accept example values for `AGENT_INPUT`, validating types, allowed values, required paths and bounded query parameters. Permit omission of `UNUSED` parameters. Reject malformed/unsafe values before sending a request.
3. Display store domain/identity, method `GET`, safe resolved relative path and query, sanitized response status and bounded preview. Never display credentials, authorization headers or secret-bearing provider URLs.
4. Transform the returned response through the configured WooCommerce Response field selection, shape and limits, then render the Result Template using the existing approved template engine; show mapping/type/template errors separately from provider failures.
5. Display WooCommerce `401`/`403` permission denial, missing/unapproved connection, `404`, network error and timeout as clear user-facing test failures. A store-specific authorization failure does not automatically revoke or disconnect an otherwise valid connection.
6. Disable concurrent/double-click execution; handle retry and stale/late responses safely. Treat Test as passed only for the exact selected Shop, operation, definition, request, response and template; relevant edits or Shop changes invalidate previous success even if Review was previously unlocked.
7. Generate bounded server-verifiable and expiring successful-test proof scoped to the authorised Shop and canonical draft fingerprint, without storing sensitive test payloads. Pass this proof to the later Review/Save task; a browser-edited `PASSED` flag is never sufficient for server-side Save authorization. A valid successful test unlocks Next/Review. Pending, failed, stale or unrun tests cannot advance; returning to edit remains available. No save, publish or general tool runtime changes in this task.
8. Use the architect-approved Commerce-local, server-only Woo REST-read grant consumer and safe GET-only transport defined in ARCH-030 (14 October 2026). Resolve the existing grant by shopId, decrypt with the approved `MODA_WOO_REST_READ_KEYRING` envelope/keyring convention, require principal/shop authorization and active REST-read scope, and revalidate the grant after request I/O. Do not create a new credential store, grant lifecycle, arbitrary provider proxy or API/Shared/Gateway dependency. Fail closed if the approved safeguards cannot be met.

## Work Items

- [ ] Confirm the approved Commerce-local server-only existing Woo REST-read grant resolver/transport is safe and matches ARCH-030; fail closed if its safeguards cannot be demonstrated.
- [ ] Implement typed example input validation, store-scoped WooCommerce GET test call and bounded result classification.
- [ ] Implement request, provider response, mapped output and template previews with safe redaction and explicit errors.
- [ ] Wire snapshot/store-bound test status, stale response protection and Test -> Review gating in the new-tool wizard.
- [ ] Add focused UI/server tests for the operation catalogue, input modes, forbidden responses, errors, concurrency and stale changes.

## Interfaces / Contracts

Commerce-owned `WooCommerceRequestDraft`, `WooCommerceResponseDraft`, `ResponseTemplate` and `NewToolAuthoringState`, using `getWooCommerceReadOperation()` as source of operation/path truth. Store authorization is server-side; Commerce consumes the existing WooCommerce REST-read grant and the approved server-only decryption keyring without owning grant creation, rotation, or revocation. UI Test status remains local/ephemeral, backed by server-verifiable expiring test proof for Save, and is not a published runtime contract.

## Dependencies

None (beyond existing Commerce tool-authoring capabilities). No API/Shared/Gateway task dependency is authorized.

## Enables

`ARCH-030-COMMERCE-002` after architect acceptance and required developer completion.

## Acceptance Criteria

- [ ] Every catalogued WooCommerce GET selection can be attempted against the selected authorized store with valid values; an operation-specific denial is shown instead of hiding the option.
- [ ] No arbitrary URL, write request, credential exposure, unauthorized Shop access or unbounded response is possible through Test.
- [ ] Request, sanitized response, selected output and result-template preview show the actual test outcome or an accurate failure.
- [ ] Only a current successful test unlocks Review, including after Shop changes, edits, repeated submissions or out-of-order completions.
- [ ] Targeted security/error/UI regression tests pass; a mocked response alone is not represented as proof of live store integration.

## Validation

- [ ] Focused WooCommerce authoring unit, React UI and server test suites, including denied store permission, missing grant, invalid arguments, timeout and stale completion.
- [ ] Typecheck, relevant lint/build checks actually provided by the Commerce repository and required by the task.
- [ ] `git diff --check`; task worktree isolation and synchronization evidence in Completion Report.

## Stop Condition

When Work Items, Acceptance Criteria and required Validation pass, set task to `review`, submit Completion Report to `moda_architect`, and STOP. If live authorization cannot be safely satisfied, report the blocker rather than claiming completion.

## Implementation Notes

Keep the provider-specific UI outside `new-tool-editor.tsx` except for wiring. Reuse existing validators, template engine and shared logger. Do not use browser-originated direct Woo requests, fabricate authorization or add a blanket cross-service API solely to pass the test.

## Completion Report

### Status

Changes Requested — Attempt 1 was returned to `ready`; Attempt 2 was claimed and reviewed with no implementation changes. The task is `ready`, `executor: null`, `claimed_at: null`, `attempt: 2`. The existing implementation remains published on the same task branch for correction.

### Files Changed

- `.env.example`
- `src/commerce/execution/renderer.ts`
- `src/commerce/woocommerce/authoring-credential.ts`
- `src/commerce/woocommerce/authoring-live-test.ts`
- `src/commerce/woocommerce/authoring-transport.ts`
- `src/studio/tools/authoring/test/woocommerce-rest-test-model.ts`
- `src/studio/tools/authoring/test/woocommerce-rest-test.tsx`
- `src/studio/tools/new-tool-authoring-state.ts`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/woocommerce-test-server-actions.ts`
- `tests/preview-runner-diagnostic-log-fields.test.ts`
- `tests/woocommerce-rest-live-test-model.test.ts`
- `tests/woocommerce-rest-live-test-service.test.ts`
- `tests/woocommerce-rest-live-test-ui.test.tsx`

### Work Completed

- Implemented catalogue-driven WooCommerce GET request preparation, input validation, response projection and result-template rendering.
- Added Woo installation/grant lookup, local AEAD credential decryption, direct bounded Woo HTTP transport, post-request grant revalidation, and signed expiring test proof.
- Added server action, Test UI and wizard navigation wiring, plus model/service/UI tests.
- The implementation currently duplicates API-owned grant decryption and provider transport inside Commerce; this does not establish an approved Commerce-to-API boundary.

### Validation Results

- Focused tests (`woocommerce-rest-live-test-model`, `woocommerce-rest-live-test-service`, `woocommerce-rest-live-test-ui`, `new-tool-authoring-state`): **39 passed, 1 failed**. The failure is `tracks WooCommerce Response edits independently after the operation is selected`; its fixture submits values already equal to the default `products.retrieve` field, so it does not exercise an actual edit while expecting revision increments.
- `npm run typecheck`: **PASS**.
- Changed-file ESLint: **FAIL**, `react-hooks/refs` in `woocommerce-rest-test.tsx` because `current.current` is assigned during render.
- `git diff --check origin/main...HEAD`: **PASS**.
- Production build: not run.
- No real authorized WooCommerce store request was made; service tests use an injected mock provider response and are not live-store integration evidence.

### Deviations

The implementation introduced a Commerce-local database grant decryptor and outbound Woo transport before an approved private API consumer boundary was available. Current ARCH-030 records place grant/transport ownership in API-008/API-001; API-002 and GATEWAY-001 are pending, and SHARED-002 is pending. This exceeds/contradicts the task's instruction to reuse an approved path or stop and report the blocker.

### Assumptions

None recorded.

### Unresolved Issues

- No approved Commerce-to-API test execution boundary is available in this task snapshot. The implementation instead decrypts Woo credentials in Commerce and directly sends requests.
- The success proof fingerprint includes Shop and draft but excludes `examples`, even though examples determine the actual request path/query. Add a regression proving a proof cannot be reused with changed test inputs and bind the proof to the effective request inputs.
- The raw provider response preview is only redacted for the exact Woo consumer key/secret strings; arbitrary catalogued responses can contain customer PII or sensitive Woo settings, which are currently displayed without field-aware redaction.
- Changed-file ESLint fails on a ref assignment during render.
- Focused validation has one failing no-op revision test; no production build or live authorized-store request was run.

### Architectural Concerns

The Commerce implementation must not become a second credential owner or unrestricted cross-service transport. Wait for architect-approved API/Shared/Gateway boundaries or have the architect amend the task scope/dependencies before integrating them. Do not claim live-store proof from mocked responses.

## Developer Self-Review

### Review Status

Changes Requested.

### Required Corrections

- Remove Commerce-owned Woo grant decryption and direct provider transport. Follow the explicit stop condition until an architect-approved, authenticated Commerce-to-API boundary exists; API-002 and GATEWAY-001 are pending, and confirm the task scope/dependencies are amended before consuming that boundary.
- Restrict response previews to the configured mapped fields and approved bounded output. Add tests showing unselected customer/private Woo fields cannot appear in the preview, logs, or proof.
- Bind the successful-test proof to the canonical effective request, including validated example inputs, and add a test proving changed examples invalidate an otherwise identical proof.
- Fix the `react-hooks/refs` lint error without reading or writing a ref during render; rerun ESLint on all changed production files.
- Change the response-revision test to submit a value different from the default `products.retrieve` field, then rerun the focused four-file suite and confirm all 40 tests pass.
- After the approved boundary is available, run the required typecheck, lint, production build and `git diff --check`; obtain authorized-store evidence if the environment provides a merchant-approved test store. Do not describe mock provider tests as live integration proof.

### Validation Reviewed

Focused suite: 39 passed, 1 failed. Typecheck passed. Changed-file ESLint failed on a render-time ref assignment. Diff check passed. Production build and live authorized-store test were not run.

### Decision

Return the task to `ready`, clear `executor` and `claimed_at`, and preserve `attempt: 1`. Do not create Attempt 2 or merge the implementation branch. The architect must resolve the transport ownership/boundary before the task can proceed with a live request.

## Architect Review

### Review Status

Changes Requested — architecture ownership clarified; Attempt 1 is still Ready and unclaimed.

### Review Notes

The developer's 14 October 2026 explicit choice authorises a Commerce-local server-only Woo REST-read grant consumer and safe GET transport, using `shopId` and `MODA_WOO_REST_READ_KEYRING` (as Background does). ARCH-030 now records that boundary. The Developer Self-Review's instruction to **remove** the Commerce-local resolver/transport and wait for API-002/GATEWAY-001 is **superseded**; preserve those historical findings as review evidence. Commerce does not own grant creation, rotation or revocation, and MUST retain scoped server-side shop authorization, an active read grant, keyring-compatible AEAD decryption and SSRF-safe GET transport. The remaining developer review corrections are in force.

### Reviewed Files

`src/commerce/woocommerce/authoring-credential.ts`, `authoring-transport.ts`, `authoring-live-test.ts`, `src/studio/tools/authoring/test/woocommerce-rest-test.tsx`, the task report and ARCH-030 architecture document (from the uploaded task snapshot).

### Validation Reviewed

Developer report: 39 passing and 1 failing focused tests, typecheck PASS, changed-file ESLint FAIL, build and real-store testing not performed. The correction implementation and its tests require rerunning; no success is presumed from this review.

### Architecture Conformance

Commerce-local grant **consumption**, not grant lifecycle ownership, is permitted only for server-side Studio GET testing under the recorded security constraints. The implementation is not accepted until proof/example binding, selected-field-only preview, React ref handling, test revision fixture and required validation are corrected.

### Follow-up

1. Retain the current Commerce-local grant/transport boundary (previous reviewer correction 1 superseded).
2. Restrict all preview fields to the Response projection and keep sensitive provider fields outside logs and proof.
3. Bind signed test proof to validated examples and effective request; carry only ephemeral validated examples to Review/Save for verification.
4. Remove render-time ref writes and validate stale response handling.
5. Correct the no-op response revision test and rerun all focused tests, lint, typecheck, build and live-store test when merchant-approved credentials are available.
6. Preserve `status: ready`, `attempt: 1`, `executor: null`, `claimed_at: null` until the next authorized developer claim. Do not begin COMMERCE-002 yet.

## Developer Claim — Attempt 2

- Claimed by developer at `2026-10-16T10:35:08+0100`; `status: in_progress`, `executor: developer`, `attempt: 2`.
- The task had no declared dependencies and was `ready` with no executor claim before this attempt.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-030-COMMERCE-001`, branch `task/ARCH-030-COMMERCE-001`; merged current `origin/main` at `98f228f2989eb167a6ddbbde1c982bacac8e4d24`. Parent task commit at preparation: `7f605f2dfc438193f768bd06429dbd12fda25f8c`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-030-COMMERCE-001`, repository `moda-interact-commerce`, branch `task/ARCH-030-COMMERCE-001`; implementation commit `4c17338b0a444653d5d3340d06fdbdc28237794d` matches `origin/task/ARCH-030-COMMERCE-001`, and current `origin/main` `ac3e515f2cae00d162b96d6c124489f6e39beffb` is an ancestor.
- Both canonical task worktrees were clean at claim. Recursive Commerce `database` submodule is initialized at `d5497286f2575c8e0b2fd2453e9dbdba4fc1136a`, matching the implementation worktree gitlink. No implementation worktree edits or branch merge to `main` occurred during claim.
- The shared/default workspace and Commerce source/reference checkout have unrelated pre-existing changes; they were preserved and are not part of this claim.
- Attempt 2 corrections remain: restrict previews to configured mapped fields; bind successful proof to validated examples/effective request; remove render-time ref writes and validate stale response handling; fix the no-op response revision test; rerun focused tests, typecheck, lint, build and diff check. Preserve the architect-approved Commerce-local grant consumer/transport and do not claim mock tests as live-store evidence.
- No implementation changes or implementation validation were performed as part of claiming this attempt.

## Developer Self-Review — Attempt 2

### Review Status

Changes Requested. The developer claim was published, but no Attempt 2 implementation changes were made.

### Reconciliation Evidence

- Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-030-COMMERCE-001` is clean on `task/ARCH-030-COMMERCE-001`. `HEAD` and `origin/task/ARCH-030-COMMERCE-001` both point to `4c17338b0a444653d5d3340d06fdbdc28237794d` (`feat(commerce)`); `origin/main` at `ac3e515f2cae00d162b96d6c124489f6e39beffb` is an ancestor. The task diff is the existing 14-file Attempt 1 implementation; there are no Attempt 2 implementation commits or uncommitted changes.
- The Commerce `database` submodule is initialized at `d5497286f2575c8e0b2fd2453e9dbdba4fc1136a`, matching the implementation worktree gitlink. The parent workspace's unrelated submodules remain uninitialized; no submodule was initialized or modified for this review.
- Parent task worktree was clean after the claim commit before this review update. Attempt 2 claim commit `512345fa6cf322885c74a8b46d866b1db079b1c9` is published on `origin/task/ARCH-030-COMMERCE-001`; current parent `origin/main` is `98f228f2989eb167a6ddbbde1c982bacac8e4d24` and is included in the parent task branch.
- No Attempt 2 implementation tests, typecheck, lint or build were run. `git diff --check origin/main...HEAD` on the implementation task branch passed, but this does not validate the outstanding behavior or substitute for the required test/build checks.

### Required Corrections

- Restrict provider previews to the configured WooCommerce Response projection and approved bounded output; add regression tests proving unselected customer/private fields are absent from previews, logs and proof.
- Bind the expiring successful-test proof to the canonical effective request, including validated example inputs; add a test proving changed examples cannot reuse a prior proof. Carry only ephemeral validated examples to Review/Save for verification.
- Remove render-time ref reads/writes and test that concurrent, stale and late responses cannot unlock Review for a changed Shop or draft.
- Correct the response-revision fixture so it changes the default `products.retrieve` field, then rerun the focused four-file suite and confirm all 40 tests pass.
- Preserve the architect-approved Commerce-local server-only grant consumer and safe GET transport. Continue to enforce principal/shop authorization, active REST-read scope, approved keyring-compatible decryption, SSRF-safe GET-only transport and post-I/O grant revalidation; Commerce must not own grant creation, rotation or revocation.
- Run the required focused unit/UI/server tests, typecheck, changed-file lint, production build and `git diff --check`. Do not report mocked provider responses as live-store evidence; use a real store only with merchant-approved credentials.

### Decision

Return the task to `ready`, clear `executor` and `claimed_at`, and preserve `attempt: 2`. No Work Items or Acceptance Criteria are complete based on this attempt. Do not begin ARCH-030-COMMERCE-002.
