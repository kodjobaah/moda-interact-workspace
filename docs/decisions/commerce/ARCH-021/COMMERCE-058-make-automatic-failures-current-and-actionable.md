---
id: ARCH-021-COMMERCE-058
architecture_id: ARCH-021
title: Make Automatic generation failures current and actionable
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 73
executor: copilot
claimed_at: 2026-09-27T12:07:31Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-053
  - ARCH-021-COMMERCE-057
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Make Automatic generation failures current and actionable

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Correct the External HTTP Response `Automatic` workflow so a failed regeneration shows
only diagnostics for the **current** provider attempt, explains provider/decode failures
using COMMERCE-057 evidence, and never presents the previous successful Response
processing JSON as though it came from the failed Request.

A failed Automatic attempt must preserve the existing authored Response definition for
the user to return to and edit; it must not silently erase or replace previously
generated/manual Visual rules.

## Context

Manual testing reproduced this sequence:

```text
Request A is valid
    -> Automatic live generation succeeds
    -> Visual rules are generated

author changes Request to invalid path B
    -> GET /categor/products
    -> provider returns HTTP 404 text/html
    -> body says "Cannot GET /categor/products"

author opens Automatic and generates again
    -> generation fails
```

The current Response tab correctly leaves the previous canonical Response definition
unchanged, but while `Automatic` is selected it still renders the generic
`View response processing JSON` disclosure from that previous definition. The screen
therefore appears to associate stale successful processing data with the failed current
Request.

The same failure is currently generic because COMMERCE-051 loses provider decode
details. COMMERCE-057 restores those bounded diagnostics.

The desired ownership remains:

```text
Automatic
    creates/proposes Visual rules

Visual rules
    edits the Response definition

Test
    executes/observes the complete Tool candidate
```

Automatic is not a second Response editor and is not a persisted processing kind.

COMMERCE-055 and COMMERCE-056 may already be executing. This task MUST NOT edit,
re-gate, reopen or absorb either task.

## Scope

Primary implementation is expected in:

```text
moda-interact-commerce/src/studio/external-http/response-tab.tsx
moda-interact-commerce/tests/external-tools-ui.test.tsx
moda-interact-commerce/tests/tool-authoring-screen.test.tsx
```

A small bounded presentation helper/component may be extracted if it makes the
diagnostic responsibilities clearer.

## Out of Scope

- Changing provider transport or decode semantics; COMMERCE-057 owns the diagnostic
  evidence.
- Clearing existing Visual rules merely because a later Automatic call fails.
- Persisting `AUTOMATIC` in `responseProcessing`.
- Creating another Automatic field/tree editor.
- Changing COMMERCE-048/049 Visual semantics or terminology.
- Test-tab implementation/presentation.
- Tool persistence, live-test receipts or publication proof.
- Phase 2 navigation gating.
- Editing COMMERCE-055 or COMMERCE-056.

## Requirements

### 1. Automatic displays only current Automatic state

While `currentMode === "AUTOMATIC"`, the Response tab MUST NOT render the canonical
processing disclosure for the underlying persisted/current Response mode.

In particular, hide:

```text
View response processing JSON
View Visual processing JSON
Derived result contract JSON
Response schema field chips
```

unless they are explicitly part of a current Automatic candidate presentation owned by
this workflow. This task does not add such a duplicate editor/presentation.

The existing definition remains available after the author selects its normal
`Visual rules`, `Direct` or `JavaScript` mode.

### 2. Failure preserves existing Response authoring

A failed Automatic attempt must not:

- call `onChange(...)` with generated/replacement processing;
- change `responseProcessing`;
- change `resultSchema`;
- change `resultPath`;
- replace Visual drafts;
- mark Response dirty solely because generation failed;
- invalidate an existing Response definition solely because generation failed.

The failure panel must state:

```text
Existing Response definition was left unchanged.
```

The author can select `Visual rules` to inspect/edit the previous generated/manual
Visual tree.

### 3. Context changes invalidate transient Automatic results

Automatic candidate/failure state is scoped to the current generation context.

A change to any input that affects generation, including the current Request candidate,
Connection revision, shop, Sample Tool arguments, Input schema or authored Response
format, must make prior transient candidates/failures unavailable for the new context.

Do not retain a candidate produced for Request A and offer it as the candidate for
Request B.

### 4. Present non-success provider responses actionably

For a current provider response that is available but non-successful, show the HTTP
status first.

For the reproduced defect, the user-facing presentation must communicate:

```text
The provider returned HTTP 404.
Expected response: application/json
Received response: text/html

Provider response:
Cannot GET /categor/products

Existing Response definition was left unchanged.
```

Equivalent concise wording is acceptable, but all five pieces of information are
required when COMMERCE-057 supplies them.

### 5. Explain decode failure reason

Use the COMMERCE-057 diagnostic reason to explain why Automatic could not use the
response.

Examples:

```text
UNEXPECTED_MEDIA_TYPE
  -> provider returned a media type not accepted by this Response format

MALFORMED_JSON
  -> provider declared JSON but the body is not valid JSON

MISSING_CONTENT_TYPE
  -> provider did not declare a Content-Type

UNSUPPORTED_CHARSET
  -> provider declared a charset the External HTTP contract does not accept

BODY_TOO_LARGE
  -> provider body exceeded the accepted bounded response size
```

Do not make stable internal codes the primary user-facing message. A collapsed
`Technical details` disclosure may expose the stable reason/code in the style already
established by COMMERCE-050.

### 6. Provider preview is text only

Render `bodyPreview` as escaped text (`<pre>` or equivalent), never as HTML and never
through `dangerouslySetInnerHTML`.

Do not attempt to sanitize-and-render provider HTML. The body preview is evidence, not
page content.

### 7. Preserve successful Automatic behaviour

A successful generation continues to:

```text
observe current provider response
    -> infer accepted VisualAuthoringRoot candidate(s)
    -> select/apply candidate
    -> derive with deriveVisualTreeContract(...)
    -> install existing Visual draft
    -> switch to Visual rules
```

No new persisted/runtime processing kind is introduced.

### 8. Keep Automatic and Test separate

Do not move response editing into Test and do not add Automatic controls to Test.

If COMMERCE-055 later needs richer provider diagnostics, assess that after its current
attempt returns for architect review rather than modifying its task from here.

## Work Items

- [ ] Hide existing Response-processing/result disclosures whenever Automatic is the
      active authoring mode.
- [ ] Add a bounded Automatic failure presentation over COMMERCE-057 diagnostics.
- [ ] Show HTTP status, expected/received media type and safe provider body preview
      where available.
- [ ] Explain the stable decode reason in user-oriented language.
- [ ] State explicitly that the existing Response definition was left unchanged.
- [ ] Preserve existing Visual/Direct/JavaScript state on failed generation.
- [ ] Ensure generation-context changes invalidate transient candidates/failures.
- [ ] Keep provider body preview escaped/plain text.
- [ ] Add the exact valid-A -> invalid-B regression.
- [ ] Preserve successful Automatic -> Visual behaviour.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-053
  Automatic authoring workflow

ARCH-021-COMMERCE-057
  bounded provider response diagnostic

ARCH-021-COMMERCE-050
  established actionable diagnostic presentation conventions (transitively via C053)
```

Produces no new persisted Tool contract.

## Dependencies

- `ARCH-021-COMMERCE-053`
- `ARCH-021-COMMERCE-057`

## Enables

None.

## Acceptance Criteria

- [ ] Generate successfully from Request A, producing Visual rules.
- [ ] Change Request to Request B `/categor/products`.
- [ ] Provider returns `404 text/html` with body containing
      `Cannot GET /categor/products`.
- [ ] A new Automatic generation reports HTTP 404.
- [ ] The failure reports expected `application/json` and received `text/html`.
- [ ] The safe provider preview includes `Cannot GET /categor/products`.
- [ ] The failure states that the existing Response definition was left unchanged.
- [ ] While Automatic is selected, the previous successful
      `View response processing JSON` / Visual processing disclosure is absent.
- [ ] Switching back to Visual rules shows the previous Visual definition unchanged.
- [ ] The failed attempt did not replace processing, schema, result path or Visual
      drafts and did not dirty Response solely because it failed.
- [ ] Malformed `application/json` produces a JSON-specific explanation rather than a
      generic media-type message.
- [ ] Changing generation context invalidates old candidate/failure UI.
- [ ] Provider preview is rendered as text and cannot execute provider HTML.
- [ ] Successful Automatic generation still installs the candidate and switches to
      Visual rules.
- [ ] `AUTOMATIC` is still absent from persisted/runtime response-processing kinds.
- [ ] COMMERCE-055 and COMMERCE-056 are untouched.

## Validation

Before running commands, inspect `moda-interact-commerce/package.json` and use the
repository scripts that actually exist.

Required focused validation:

- [ ] External HTTP Response-tab UI tests.
- [ ] Tool-authoring screen tests covering Automatic composition.
- [ ] Exact successful-A -> failing-B stale-state regression.
- [ ] `404 text/html` actionable-diagnostic regression.
- [ ] malformed JSON diagnostic regression.
- [ ] context-change invalidation regression.
- [ ] successful Automatic -> Visual regression.
- [ ] targeted lint for changed files.
- [ ] changed-file TypeScript diagnostics.
- [ ] `git diff --check`.

Do not turn unrelated documented repository baseline failures into task-owned work.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete,
set the task to `review`, return the Completion Report to `moda_architect` and STOP.
Do not begin any Test follow-up or modify COMMERCE-055/056.

## Implementation Notes

The stale-data defect is a presentation/context problem, not permission to destroy
authored Response state.

Required mental model:

```text
Automatic attempt failed
        |
        +--> transient Automatic failure is current
        |
        +--> previous Response definition is preserved
                         |
                         +--> visible only when author returns to its normal editor
```

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run.

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

Pending.

### Follow-up

None
