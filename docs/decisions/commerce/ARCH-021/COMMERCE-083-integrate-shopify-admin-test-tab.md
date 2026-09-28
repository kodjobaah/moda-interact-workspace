---
id: ARCH-021-COMMERCE-083
architecture_id: ARCH-021
title: Integrate Shopify Admin Test and show the populated Result Template
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 75
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-078
  - ARCH-021-COMMERCE-082
enables:
  - ARCH-021-SYSTEM-TEST-002
created: 2026-09-28
updated: 2026-09-28
---

# Integrate Shopify Admin Test and show the populated Result Template

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the Shopify Admin Test placeholder with live candidate testing and make the populated Result Template the primary result for new and persisted Shopify Admin authoring.

## Context

COMMERCE-082 supplies the non-durable Admin live-Test action. The current new Tool Test surface contains only `Admin query validation is non-mutating`, while the persisted Admin editor has no equivalent complete Test presentation. The agreed authoring flow requires Test after Result Template and before Review.

## Scope

Primary implementation:

```text
src/studio/tools/new-tool-editor.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/shopify-admin-test-tab.tsx    # new reusable component
src/studio/tools/shopify-admin-live-test-server-actions.ts # consume
```

Tests:

```text
tests/shopify-admin-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
tests/shopify-admin-live-test-action.test.ts
```


## Out of Scope

- Backend execution semantics; COMMERCE-082.
- External Test UI; COMMERCE-081.
- Publication proof/gate changes.
- Automatic saving after Test.
- GraphQL authoring/Response derivation changes.

## Requirements

### R1 — one reusable Admin Test tab

Use one `ShopifyAdminTestTab` (or exact equivalent shared component) for:

```text
new Shopify Admin Tool
persisted Shopify Admin DRAFT
```

Do not implement separate Test UIs with divergent state semantics.

### R2 — Test consumes the exact current candidate

The action input must come from the same current assembled definition Review/Save would use, including Tool Definition/Request/Response/Result Template state. It must include current Test arguments and selected `shopId` only; no shop domain/token.

### R3 — local prerequisites point to owning steps

Disable/fail locally with actionable messages when:

```text
input schema/mappings invalid          -> Request
Admin result contract stale/invalid    -> Response
Result Template invalid/stale          -> Result Template
shop not selected                      -> Test: select a Studio shop
arguments invalid                      -> Test
```

No message may instruct the user to edit Agent Contract.

### R4 — primary output is what the agent receives

On success display first:

```text
Result shown to agent
<server returned renderedText>
```

Display canonical normalized processed values and the five C082 stage outcomes only as secondary diagnostics. The browser must not independently render the template.

### R5 — stale-result identity is complete

Clear/mark stale prior results when current Tool Definition fields, Request/inputSchema, GraphQL document/mappings, Response/result contract, Result Template, arguments or selected shop changes. Tab navigation alone does not stale the result.

### R6 — preserve local/explicit persistence boundaries

Running Test neither creates a new Tool nor saves a persisted draft. For new Tools, only Review -> Save may create. For persisted DRAFTs, only explicit Save draft may write.


### R7 — drive the C078 common Test checkpoint for new Tools

For the new-Tool Shopify Admin flow, C083 MUST consume the C078 common Test freshness model rather than create a second canonical pass/freshness checkpoint.

On Test start capture the exact C078 `currentAuthoringSnapshot(session)` and transition the common session Test state to `RUNNING`.

On C082 success complete the checkpoint with `PASSED`; on C082 failure complete it with `FAILED`.

If any Tool Definition, Request, Response or Result Template revision changed while C082 was running, the completion must become:

```text
status = STALE
testedSnapshot = null
```

and the provider result must not mark the current candidate passed.

The reusable Shopify Admin Test component may retain bounded provider-specific result/stage diagnostics separately. Those payloads must not be copied into the C078 common `test` state.

Use `isCurrentTestPassed(session)` for new-Tool current-pass decisions. Persisted-DRAFT Test freshness remains governed by the persisted authoring state model introduced by C079; do not force the new-Tool session object into persisted DRAFTs.

## Work Items

- [ ] Add one reusable Shopify Admin Test component.
- [ ] Integrate it in new Tool Shopify Test.
- [ ] Integrate it in persisted Shopify Admin DRAFT Test.
- [ ] Pass exact current complete candidate + arguments + shopId.
- [ ] Add owning-tab prerequisite messages.
- [ ] Show `Result shown to agent` first using server renderedText.
- [ ] Keep safe normalized-result/stage diagnostics secondary.
- [ ] Add complete stale-result identity.
- [ ] Drive the C078 common RUNNING/PASSED/FAILED/STALE checkpoint for new-Tool Test without storing provider payloads in it.
- [ ] Prove Test never invokes create/save mutation actions.
- [ ] Add new/persisted UI regressions.

## Interfaces / Contracts

Consumes C078 flow composition plus its common new-Tool Test checkpoint/freshness operations, and consumes the C082 Shopify Admin live-Test contract. No new persistent/cross-repository contract.

## Dependencies

- ARCH-021-COMMERCE-078
- ARCH-021-COMMERCE-082

## Enables

- ARCH-021-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] New and persisted Shopify Admin authoring render the same Test component.
- [ ] Test sends the exact current assembled candidate, arguments and shopId.
- [ ] Invalid/stale prerequisites point to Request, Response or Result Template correctly.
- [ ] Successful Test displays server `renderedText` first under `Result shown to agent`.
- [ ] Processed values/stages remain secondary and credential-safe.
- [ ] Any candidate/template/argument/shop change stales the prior result; tab selection does not.
- [ ] Test performs zero create/save mutation.
- [ ] Existing Explore/Response/Review behaviour remains intact.
- [ ] New-Tool Admin Test drives the C078 common checkpoint; stale in-flight completions cannot mark the current candidate passed.

## Validation

- [ ] `npx vitest run tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/shopify-admin-live-test-action.test.ts`
- [ ] focused new/persisted shared-component regression
- [ ] focused rendered-result DOM-order assertion
- [ ] focused stale-on-template/shop-change assertion
- [ ] focused zero-write assertion
- [ ] focused C078 RUNNING/PASSED/FAILED/STALE checkpoint integration assertions for the new-Tool flow
- [ ] targeted ESLint for changed files
- [ ] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [ ] `git diff --check`

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin an enabled or adjacent task.

## Implementation Notes

Do not infer rendering or result fields in React. C082 is the server authority for live execution and rendered agent output.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
