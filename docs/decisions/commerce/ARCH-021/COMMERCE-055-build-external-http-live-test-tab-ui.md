---
id: ARCH-021-COMMERCE-055
architecture_id: ARCH-021
title: Build the decomposed External HTTP live Test tab
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-054
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Build the decomposed External HTTP live Test tab

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the External HTTP Test placeholder with a decomposed React surface that lets the author provide ephemeral Tool arguments, run COMMERCE-054 against the exact current non-durable Request + Response candidate, and understand each execution stage, safe provider observation, processed result and result-contract outcome without persisting anything or duplicating Request/Response authoring.

## Context

By the time an author reaches Test:

```text
Request
  has already defined and validated how the provider request is constructed

Response
  has already defined and validated how the provider response is processed

Test
  now asks whether those two definitions actually work together against the real provider
```

The Tool still does not exist durably.

COMMERCE-054 owns the live backend and returns explicit stages:

```text
Request construction
Connection resolution
Provider request
Response processing
Result validation
```

This task owns presentation/orchestration only.

The existing Request/Response task chains are accepted baseline capabilities and are not dependencies here. Automatic Response generation is independent and is not a Test prerequisite.

## Scope

Primary implementation files are expected to include bounded components under:

```text
moda-interact-commerce/src/studio/external-http/
moda-interact-commerce/src/studio/tools/
moda-interact-commerce/app/styles.css

moda-interact-commerce/tests/external-tools-ui.test.tsx
moda-interact-commerce/tests/tool-authoring-screen.test.tsx
```

A small Test-specific hook/controller module is permitted and encouraged when it keeps asynchronous orchestration out of presentation components.

## Out of Scope

- Backend provider/network/processing implementation; COMMERCE-054 owns it.
- Request or Response authoring controls.
- Automatic generation.
- Synthetic/sample-provider response fixture UI.
- Persisting Tool/Test state.
- Save/Create/Publish behavior.
- Publication/live-test receipts or publication proof.
- Phase 2 tab gating.
- Agent conversational preview.
- Database/Shared/Gateway changes.

## Requirements

### R1 — run the exact current local candidate

`Run live test` must submit the current canonical local authoring candidate to COMMERCE-054, including current unsaved Request/Response edits that have been promoted into canonical local state.

Do not reload a persisted Tool revision or require a Tool identifier.

If visible Request/Response raw local state is currently invalid and therefore cannot form a runnable canonical candidate, Test must show an actionable local message directing the author back to the relevant tab rather than silently testing stale older state.

### R2 — ephemeral Test arguments

Provide a bounded `Test arguments` authoring control for the Tool invocation inputs needed by the current Request.

Arguments are:

```text
browser-local/session-only
used only for this live Test
not part of the Tool definition
not durably persisted
```

Reuse existing accepted argument parsing/validation helpers where practical.

Do not introduce synthetic provider response samples.

### R3 — explicit Run action and pending behavior

Provide one clear action:

```text
Run live test
```

While pending:

```text
prevent duplicate Run submissions
keep all tabs navigable
show bounded progress
```

A retry after failure is allowed.

### R4 — Test tab MUST be decomposed into bounded responsibilities

`ExternalHttpTestTab` is an orchestration/layout component, not a monolithic implementation of every Test concern.

Use bounded components/responsibilities equivalent to:

```text
ExternalHttpTestTab
  orchestration + composition only

TestArgumentsForm
  ephemeral Tool invocation inputs

RunLiveTestAction
  run/pending/retry interaction

LiveTestStages
  five stage outcomes

LiveTestRequestSummary
  safe GET URL/authored headers/redacted auth state

LiveTestProviderResponse
  bounded status/content type/body/JSON presentation

LiveTestProcessedResult
  processed Tool result + result-contract outcome

LiveTestErrorSummary
  stage-specific actionable failure guidance
```

Exact filenames/component grouping may follow repository conventions. Do not create artificial micro-components purely to satisfy names, but the listed responsibilities must not collapse into one giant Test component.

A hook/controller such as:

```text
useExternalHttpLiveTest
```

is encouraged for request identity, pending state, stale-result suppression and Server Action orchestration.

### R5 — render stage-by-stage execution truthfully

Present all five COMMERCE-054 stages:

```text
Request construction
Connection resolution
Provider request
Response processing
Result validation
```

Use clear states:

```text
Passed
Failed
Not run
```

If an earlier stage fails, later stages display `Not run`; do not present them as failed.

Provider HTTP status/content type should appear with the provider stage where available.

### R6 — safe Request summary

When COMMERCE-054 returns a request summary, show:

```text
GET safe URL
authentication: not configured | configured/redacted
authored safe headers
```

Never display resolved credential values.

The Request summary is read-only. Editing Request belongs in the Request tab.

### R7 — bounded provider response

Show the real provider observation returned by COMMERCE-054:

```text
HTTP status
content type
bounded body/JSON
```

Long output must use a bounded scrollable read-only code/pre surface.

Do not show provider response headers or server/internal stack details.

### R8 — processed result and result-contract outcome

When processing runs, show the actual processed Tool result read-only.

Show Result validation independently:

```text
Valid
Invalid
Not run
```

When invalid, render bounded actionable issue paths/messages supplied by COMMERCE-054.

Do not add result-schema editing controls to Test.

### R9 — errors stay in Test

Live-Test failures are presented in the Test tab by the stage that failed.

At minimum distinguish user-facing categories equivalent to:

```text
invalid Test arguments
current Request not runnable
current Response not runnable
shop required/not authorized
Connection unavailable
provider security/network/deadline failure
provider non-2xx response
response processing failure
result contract failure
live-Test service unavailable
forbidden
```

Stable codes/technical details may be secondary. Raw internal/provider/QuickJS messages are not primary user text.

### R10 — staleness and concurrent completion

A displayed live Test result is valid only for the exact candidate/arguments/shop that produced it.

Immediately mark/remove the result as stale when any Test-affecting state changes:

```text
Test arguments
Connection revision
Request
Response format/media types
result path
response processing
result schema
selected shop
```

If Run A is pending, the author edits and runs B, and A resolves after B, A must not replace B/current state.

Use deterministic local request identity rather than assuming promise completion order.

### R11 — zero persistence remains visible in the product semantics

Running Test performs no Save/Create/Publish action.

Do not display language suggesting that a successful Test was saved, attached to a revision or recorded as publication proof.

A successful Test means only:

```text
the current local candidate worked for this live execution
```

Durable creation occurs later when the author explicitly completes the creation flow.

### R12 — no synthetic Test mode or duplicated authoring

The Test tab must not render:

```text
synthetic fixture selector
sample provider-response editor
Source path
response-processing mode selector
Visual mapping/tree controls
filters/sort/limit
processed-result schema editor
JavaScript Response editor
Automatic generation controls
Request construction/mapping editor
```

Direct the author to Request/Response when those definitions need changing.

### R13 — no tab gating

Passed/failed/not-run Test state does not lock or unlock authoring tabs in this phase.

## Work Items

- [ ] Build ephemeral Test-arguments authoring over existing accepted argument helpers.
- [ ] Wire one `Run live test` action to COMMERCE-054 using the exact current local candidate.
- [ ] Decompose Test presentation/orchestration into bounded responsibilities rather than one large component.
- [ ] Render five execution stages with Passed/Failed/Not run semantics.
- [ ] Render safe Request summary without credentials.
- [ ] Render bounded provider response read-only.
- [ ] Render processed result and independent result-contract outcome read-only.
- [ ] Render stage-specific actionable Test errors locally.
- [ ] Add pending/double-submit protection, result staleness and stale-promise suppression.
- [ ] Prove Test causes no creation/save/publication mutation and exposes no synthetic fixture mode.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-054
non-durable External HTTP live-Test backend result contract

accepted current local Tool authoring composition
```

Produces only Studio presentation/client orchestration.

No cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-054

## Enables

None.

## Acceptance Criteria

- [ ] Test runs the exact current local Request + Response candidate rather than a saved revision.
- [ ] Test arguments are ephemeral and never persisted in the Tool definition.
- [ ] `ExternalHttpTestTab` remains an orchestration/composition component rather than a monolithic Test implementation.
- [ ] Argument authoring, Run interaction, stage presentation, Request summary, provider response, processed result and failure presentation have bounded component/responsibility boundaries.
- [ ] All five execution stages are visible and correctly distinguish Passed/Failed/Not run.
- [ ] Safe Request summary contains no credential value.
- [ ] Provider output and processed result are bounded/read-only.
- [ ] Result-contract validity is displayed independently from provider/processing status.
- [ ] Failures are actionable and shown in Test without raw internal messages.
- [ ] Candidate/argument/shop changes invalidate stale Test results.
- [ ] Out-of-order older promises cannot overwrite newer Test state.
- [ ] Duplicate Run while pending is prevented.
- [ ] No Request/Response/Automatic authoring controls are duplicated in Test.
- [ ] No synthetic provider-response fixture mode appears.
- [ ] Running Test performs no Save/Create/Publish/receipt/proof mutation.
- [ ] Test does not imply persistence or publication proof.
- [ ] All authoring tabs remain freely navigable.

## Mandatory Regression Scenarios

Add focused coverage proving at least:

```text
1. Test renders ephemeral arguments + Run live test.
2. prohibited Request/Response/Automatic/synthetic controls are absent.
3. malformed Test arguments do not invoke live backend.
4. successful 200 flow shows all five stages Passed.
5. provider non-2xx shows Provider Failed and later stages Not run.
6. response-processing failure preserves provider outcome, Processing Failed, Validation Not run.
7. result-contract mismatch shows processed result + Result validation Failed.
8. credential material is absent from Request/provider presentation.
9. long provider/result output uses bounded read-only presentation.
10. Request edit after success marks/removes result stale.
11. Response edit after success marks/removes result stale.
12. Test-argument edit after success marks/removes result stale.
13. selected-shop change after success marks/removes result stale.
14. Run A then edit/Run B then late A resolution cannot replace B.
15. double Run while pending is prevented.
16. new local Tool Test performs no Create/Save.
17. no receipt/publication-proof language or action appears.
18. Test component composition is exercised through focused child/component tests where useful rather than one giant snapshot test only.
```

## Validation

Run at minimum:

- [ ] focused External HTTP Test-tab UI tests
- [ ] focused Tool-authoring-screen integration tests for current candidate/shop composition
- [ ] existing External UI/common Tool-authoring packet required by repository scripts when affected
- [ ] targeted ESLint on changed files
- [ ] changed-file TypeScript diagnostics contain no task-owned error
- [ ] `git diff --check`

Inspect `package.json` and task-owned scripts before choosing exact command names.

## Stop Condition

After the decomposed Test UI runs COMMERCE-054 against the exact current local candidate, renders truthful stage/result diagnostics, proves zero persistence semantics and passes required validation, set this task to `review`, complete the Completion Report and STOP. Do not begin publication-proof or Phase 2 gating work.

## Implementation Notes

The product model is:

```text
Request  -> author + validate
Response -> author + validate
Test     -> execute + observe
Create   -> first durable write
```

Do not make Test responsible for saving proof of itself.

## Completion Report

### Status

Not Started

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

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
