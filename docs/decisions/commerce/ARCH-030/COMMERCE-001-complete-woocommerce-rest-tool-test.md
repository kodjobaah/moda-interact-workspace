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
status: in_progress
priority: 30
executor: developer
claimed_at: 2026-10-14T09:14:23Z
attempt: 1
depends_on: []
enables:
  - ARCH-030-COMMERCE-002
created: 2026-10-14
updated: 2026-10-14
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
8. Before executing live requests, verify a safe existing server-side method to resolve an approved Woo store and its credentials. If unavailable in this snapshot, stop and report the concrete missing boundary; do not invent a credential store, unrestricted proxy or new API task.

## Work Items

- [ ] Inspect the selected-store context and existing Woo read authorization/transport; document the executable boundary or raise a blocker before implementing live execution.
- [ ] Implement typed example input validation, store-scoped WooCommerce GET test call and bounded result classification.
- [ ] Implement request, provider response, mapped output and template previews with safe redaction and explicit errors.
- [ ] Wire snapshot/store-bound test status, stale response protection and Test -> Review gating in the new-tool wizard.
- [ ] Add focused UI/server tests for the operation catalogue, input modes, forbidden responses, errors, concurrency and stale changes.

## Interfaces / Contracts

Commerce-owned `WooCommerceRequestDraft`, `WooCommerceResponseDraft`, `ResponseTemplate` and `NewToolAuthoringState`, using `getWooCommerceReadOperation()` as source of operation/path truth. Store authorization is server-side and follows approved existing Commerce/store integration. UI Test status remains local/ephemeral, backed by server-verifiable expiring test proof for Save, and is not a published runtime contract.

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

In Progress — Attempt 1 claimed by developer at 2026-10-14T09:14:23Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.
