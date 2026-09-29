---
id: ARCH-021-COMMERCE-086
architecture_id: ARCH-021
title: Publish and link the Result Template user guide
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 86
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-084
  - ARCH-021-COMMERCE-085
enables: []
created: 2026-09-28
updated: 2026-09-28
---

# Publish and link the Result Template user guide

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Publish the approved non-developer Result Template guide as a static Commerce Studio manual and add one contextual link from the Result Template authoring tab to that manual, without changing Result Template grammar, validation, generation, rendering, authoring state or persistence behaviour.

## Context

COMMERCE-084 owns the accepted Result Template grammar, validator, generator and renderer. COMMERCE-085 owns the Result Template authoring editor and available-result-data experience.

The Result Template language is intentionally richer than plain text: users may need loops, conditions, comparisons, boolean expressions and simple arithmetic. The Studio therefore requires user-facing help written for staff who are not software developers.

The approved manual supplied by `moda_architect` is:

```text
Result Template Guide | Moda Commerce Studio
```

and must be published at the exact application path:

```text
/manuals/result-template-guide.html
```

The manual is deliberately a self-contained static HTML document so it does not depend on a separate documentation service, JavaScript runtime, external assets or authenticated API call.

## Scope

Implementation repository:

```text
moda-interact-commerce/
```

Required manual destination:

```text
public/manuals/result-template-guide.html
```

Primary UI integration area after COMMERCE-085:

```text
src/studio/tools/authoring/result-template-tab.tsx
```

or the exact Result Template editor component introduced by COMMERCE-085 if that task moves the visible tab implementation to another Commerce-owned file.

Focused tests must extend the Result Template UI test packet, normally:

```text
tests/result-template-tab.test.tsx
```

If COMMERCE-085 renames that test file, update the corresponding accepted Result Template editor test rather than creating a duplicate test suite solely for the link.

## Out of Scope

- Changing the `nunjucks.v1` / accepted Result Template grammar.
- Changing parser, validator, generator or renderer behaviour.
- Changing CodeMirror/editor semantics.
- Changing generated template content.
- Changing Result Template validation freshness or dirty-state semantics.
- Changing Test behaviour.
- Changing Save/Review gating.
- Adding an external documentation service.
- Adding a CMS.
- Adding a database model for documentation.
- Fetching the guide over an external network request.
- Adding analytics/tracking for guide usage.
- Rewriting the approved manual into developer-oriented language.

## Requirements

### R1 — publish the exact approved manual as a static asset

Create exactly:

```text
public/manuals/result-template-guide.html
```

using the architect-approved Result Template manual supplied with this task/handoff.

The published file must be self-contained:

```text
- HTML and CSS only;
- no JavaScript;
- no external fonts;
- no remote images;
- no remote stylesheets;
- no iframe;
- no external script/resource request.
```

The file must retain this exact document title:

```text
Result Template Guide | Moda Commerce Studio
```

and the visible top-level heading:

```text
Result Template Guide
```

Do not convert the guide into developer API documentation. Preserve its non-developer wording and examples.

### R2 — manual content must match the accepted C084 grammar

Before publishing, compare the guide examples against the architect-accepted COMMERCE-084 grammar.

The guide must document only constructs that C084 actually accepts after Architect Review.

The expected user-facing grammar for this task is:

```text
value interpolation             {{ path }}
for / else / endfor
if / elif / else / endif
comparisons                     == != < <= > >=
boolean expressions             and or not
parentheses for grouping
numeric arithmetic              + - * / %
primitive string/number/boolean/null literals where C084 permits them
nested supported loops
```

The guide must not instruct users to use unsupported constructs such as:

```text
set
macro / call
include / import / from / extends / block
function or method calls
filters
arbitrary globals
bracket/computed access
loop.*
```

If the accepted C084 implementation differs from the expected grammar above, do **not** silently publish incorrect examples. Stop and return the task to `moda_architect` as Blocked with the exact grammar mismatch. Do not alter C084 from this task.

### R3 — one contextual link in Result Template

Add exactly one persistent help link to the visible Result Template authoring surface.

The rendered link text must be exactly:

```text
Open Result Template guide
```

The link target must be exactly:

```text
/manuals/result-template-guide.html
```

Render it as a normal anchor, not a button:

```tsx
<a
  href="/manuals/result-template-guide.html"
  target="_blank"
  rel="noopener noreferrer"
>
  Open Result Template guide
</a>
```

Mechanical JSX formatting may differ, but the semantic attributes above must not differ.

Do not use `window.open`, a click handler, router navigation or a Server Action for the manual link.

### R4 — exact placement

Place the guide link in the Result Template tab's introductory/header area:

```text
Result Template
[short existing/generated-template explanation]
Open Result Template guide
[editor / available result data / validation controls]
```

The user must be able to see the guide link without expanding diagnostics and without first validating the template.

Do not place the only link:

```text
- in Review;
- in Test;
- inside a validation error;
- inside a collapsed disclosure;
- at the bottom after the editor;
- only when validation fails.
```

### R5 — link availability is independent of authoring state

The link remains available when the Result Template is:

```text
UNVALIDATED
VALIDATING
VALID
INVALID
STALE
```

It must not be disabled by:

```text
pending validation
provider selection
Response validity
Test status
Save eligibility
read-only Review state
```

Opening the guide must not change any authoring-session value, revision, dirty/freshness state, Test state or persistence state.

### R6 — manual route requires no Studio data request

The guide is a static public application asset. Opening:

```text
/manuals/result-template-guide.html
```

must not invoke:

```text
Studio Server Actions
CommerceBackend
database queries
Shopify APIs
external provider APIs
LLM APIs
```

No customer/shop/tool data is embedded into the manual.

### R7 — no duplicate help surfaces

Do not create another Result Template manual, modal, drawer or embedded full guide in React.

The canonical user guide for this task is the one static file at:

```text
public/manuals/result-template-guide.html
```

The Result Template UI contains only the contextual link plus any concise editor guidance already owned by C085.

## Work Items

- [ ] Confirm COMMERCE-084 is Complete/Accepted and record the accepted grammar used by the guide.
- [ ] Confirm COMMERCE-085 is Complete/Accepted and locate the final Result Template editor/header component.
- [ ] Compare every template-language example in the approved manual with the accepted C084 grammar.
- [ ] If the manual and accepted grammar differ, mark this task Blocked and STOP instead of publishing misleading help.
- [ ] Add the approved manual at `public/manuals/result-template-guide.html` unchanged except for corrections explicitly required to match accepted C084 grammar.
- [ ] Confirm the manual contains no external resource dependencies.
- [ ] Add exactly one `Open Result Template guide` anchor to the Result Template header/introductory area.
- [ ] Use exact href `/manuals/result-template-guide.html`, `target="_blank"`, and `rel="noopener noreferrer"`.
- [ ] Prove opening/rendering the link does not mutate authoring state or invoke persistence/server actions.
- [ ] Add focused UI/link regression coverage.
- [ ] Run required validation and complete the Completion Report.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-084
  accepted Result Template language contract

ARCH-021-COMMERCE-085
  accepted Result Template editor / header surface
```

Produces no runtime API, database or cross-repository contract.

Static user-documentation contract:

```text
URL:   /manuals/result-template-guide.html
Title: Result Template Guide | Moda Commerce Studio
H1:    Result Template Guide
```

## Dependencies

- ARCH-021-COMMERCE-084
- ARCH-021-COMMERCE-085

## Enables

None.

## Acceptance Criteria

- [ ] `public/manuals/result-template-guide.html` exists.
- [ ] The manual title is exactly `Result Template Guide | Moda Commerce Studio`.
- [ ] The visible H1 is exactly `Result Template Guide`.
- [ ] The manual is written for non-developers and explains Result Templates through plain-language examples.
- [ ] Every documented grammar example is accepted by the architect-approved C084 grammar.
- [ ] Unsupported constructs are not presented as supported.
- [ ] The manual contains no JavaScript or remote resource dependency.
- [ ] Result Template displays exactly one contextual link labelled `Open Result Template guide`.
- [ ] The link href is exactly `/manuals/result-template-guide.html`.
- [ ] The link opens in a new tab using `target="_blank"` and `rel="noopener noreferrer"`.
- [ ] The link remains available regardless of validation/Test/dirty state.
- [ ] Clicking/opening the guide performs zero Tool/ToolRevision/audit/persistence mutation.
- [ ] Existing Result Template editor, validation, generation and Test behaviour are unchanged.

## Validation

- [ ] `test -f public/manuals/result-template-guide.html`
- [ ] `grep -F '<title>Result Template Guide | Moda Commerce Studio</title>' public/manuals/result-template-guide.html`
- [ ] verify the manual contains no `<script`, remote `<link`, remote `<img`, or `<iframe` resources
- [ ] run the accepted C085 Result Template editor/UI test file with new link assertions
- [ ] focused assertion: accessible link name equals `Open Result Template guide`
- [ ] focused assertion: href equals `/manuals/result-template-guide.html`
- [ ] focused assertion: target equals `_blank`
- [ ] focused assertion: rel contains both `noopener` and `noreferrer`
- [ ] focused assertion: link is present while template is stale/invalid
- [ ] focused assertion: rendering/clicking the anchor causes no authoring-state mutation or Server Action call
- [ ] targeted ESLint for changed React/test files
- [ ] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [ ] `git diff --check`

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not modify C084/C085 or begin unrelated follow-on work.

## Implementation Notes

The manual is intentionally shipped as a static asset because it is user help, contains no tenant data and must remain available without creating another documentation runtime dependency.

Do not expose repository/GitHub links to end users as the manual target.

Do not replace the static manual link with an in-app modal containing a copied version of the same guide; that creates two user-facing sources of truth.

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
