---
id: ARCH-030-COMMERCE-001
architecture_id: ARCH-030
title: Implement WooCommerce read-tool Test step with visible permission failures
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-030-SHARED-002
  - ARCH-030-API-002
  - ARCH-030-GATEWAY-001
enables:
  - ARCH-030-COMMERCE-002
created: 2026-10-14
updated: 2026-10-14
---

# Implement WooCommerce read-tool Test step with visible permission failures

## Architecture

Architecture ID: `ARCH-030`.

Architecture document: `docs/architecture/ARCH-030-woocommerce-commerce-tool-authoring.md`.

Coordinator: `moda_architect`.

## Objective

Replace the WooCommerce new-tool Test placeholder with full-catalogue live GET testing, transparent provider-permission failures, safe previews and correct test/navigation state.

## Context

`src/studio/tools/authoring/test/woocommerce-rest-test.tsx` is a placeholder, and `src/studio/tools/new-tool-editor.tsx` disables Next for Woo. The existing request/response/result-template draft models and `startAuthoringTest`/`completeAuthoringTest`/`isCurrentTestPassed` helpers already provide revision-based freshness semantics.

## Scope

- Add Commerce server-side authenticated Shop-scoped invocation of API-002 using Shared contract; no browser direct API/Woo call.
- Build provider-local Test inputs for every `AGENT_INPUT` and fixed value, resolved GET preview, Run/Retry, safe HTTP response/fields/processed result/template preview.
- Show actionable permission denied, read-grant-required, disconnected/unavailable, validation and timeout states without exposing secrets.
- Wire valid current test status to Test -> Review navigation; guard double submission, stale result and shop switch.

## Out of Scope

- No credential/secret loading in Commerce, no arbitrary Woo fetch, no merchant Studio exposure, no production MCP/background tool execution.
- Do not implement Woo Review/Save in this task: COMMERCE-002 owns that bounded follow-on.
- Do not silently hide methods from the Request catalogue based on guessed provider permissions.

## Requirements

- Only actual selected Shop authorization on server may start a test; tenant scope must not be inferred solely from a browser-posted shop ID.
- Use exact existing Request/Response/Result Template semantics and canonical Shared operation descriptors for every method.
- For provider 403/401, display clear permission-denied or reauthorization-required guidance and preserve edit/retry controls; never label denied as PASSED.
- Bound result preview; avoid unredacted PII/secrets; render provider content as inert text/JSON, never HTML.
- Current successful test must match tool/request/response/template revision AND selected Shop/grant context; edits or Shop switch invalidate it.
- In-flight buttons are single-flight; stale callbacks cannot advance Step or certify a revised tool.
- When response processing or template render fails, display a failed stage with detail safe for the actor; do not mark PASSED merely because provider returned HTTP 200.

## Work Items

- [ ] Implement server action/client adapter, server authorization tests, and Shared contract consumption.
- [ ] Implement parameter example form and deterministic request view for full GET catalogue.
- [ ] Execute one bounded request, process configured response fields and render template preview with safe errors.
- [ ] Integrate current authoring Test state and Next/Review navigation, including stale and concurrent completion cases.
- [ ] Add component and integration tests for success, forbidden endpoint, missing grant, malformed values, altered draft, changed Shop and stale response.

## Interfaces / Contracts

Consumes SHARED-001 contract via SHARED-002, API-002 private authenticated test route and GATEWAY-001 private transport. Reuse current new-tool draft revisions and response/template validators; do not invent client-side success flags. Commerce may publish no raw Woo body to logging.

## Dependencies

- `ARCH-030-SHARED-002`
- `ARCH-030-API-002`
- `ARCH-030-GATEWAY-001`

## Enables

- `ARCH-030-COMMERCE-002`

## Acceptance Criteria

- [ ] All catalogue GET options support example values and Test invocation without a product-only fallback.
- [ ] Woo 403, 401, unavailable, wrong Shop, network and processing failures display useful safe messages; a denied endpoint never counts as passed.
- [ ] A genuinely successful current test enables Review, while failed/stale/in-flight/changed-Shop outcomes cannot pass.
- [ ] Repeated Test clicks do not dispatch duplicates; older results cannot overwrite newer state.
- [ ] No credential exposure, direct browser Woo request or generic external HTTP bypass.

## Validation

- [ ] Focused Commerce Test step UI/state/server authorization and transport tests, including all-catalogue parity.
- [ ] Typecheck/lint/build scripts declared in Commerce package as relevant; git diff --check.
- [ ] Contract-driven API fixture test of permission denied and success; record blockers to live merchant Woo read proof honestly.

## Stop Condition

After all required Work Items, Acceptance Criteria and Validation pass, record a truthful Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not start dependent tasks or mark this task Complete.

## Implementation Notes

Test a selection of sensitive resources (orders/customers/webhooks/settings) for projection and least-privilege behavior. Do not expand Studio user roles now. No `_index.md` edits until the architect/user closes the task series.

## Completion Report

### Status

Not Started.

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

None recorded yet.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed: portable task definition only.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation.

### Follow-up

Await dependency-gated, launcher-materialised execution and independent review.
