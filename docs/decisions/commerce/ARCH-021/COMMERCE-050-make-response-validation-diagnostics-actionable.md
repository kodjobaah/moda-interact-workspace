---
id: ARCH-021-COMMERCE-050
architecture_id: ARCH-021
title: Make Response validation diagnostics actionable in Studio
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 65
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-049
enables: []
created: 2026-09-26
updated: 2026-09-26
---

# Make Response validation diagnostics actionable in Studio

## Architecture

Architecture ID: `ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: `moda_architect`

## Objective

Make External HTTP **Response** validation tell an administrator exactly what is wrong,
where it is wrong, and what action will correct it, without exposing raw Zod/parser
messages or internal JSON-pointer/code noise as the primary user-facing error.

The task is presentation/diagnostic fidelity only. It does not change Response processing
semantics, result-schema semantics, provider execution, persistence or authoring-tab
navigation.

## Context

Manual validation after C049 reproduced this ordinary Visual authoring state:

```text
Visual field: field2
Node type:    Scalar
Result type:  Choose type
```

The browser-local Visual tree is intentionally invalid and cannot yet be promoted to the
canonical Tool definition. `deriveVisualTreeContract(...)` already knows the real cause:

```text
MISSING_RESULT_TYPE
/fields/field2/resultType
Choose a result type for every Visual output field.
```

However, pressing **Validate response** currently follows this path:

```text
invalid browser-local Visual tree
    -> visualDerived.ok = false
    -> ResponseTab sends:
         responseProcessing: null
         resultSchema: null
    -> authoritative Server Action parses the null placeholders
    -> generic schema diagnostics
```

The UI therefore renders messages such as:

```text
/execution/responseProcessing (invalid_type): Invalid input: expected object, received null
/execution/resultSchema (custom): Invalid input
```

Those diagnostics describe the placeholder transport shape, not the administrator's
mistake. They are technically true but product-useless.

ARCH-021 already requires invalid local Response edits to remain visible with
**actionable Response-local errors**. C050 closes that diagnostic-presentation gap.

## Scope

Primary files:

```text
moda-interact-commerce/src/studio/external-http/response-tab.tsx
moda-interact-commerce/src/studio/external-http/visual-tree-editor.tsx
moda-interact-commerce/src/commerce/tool-authoring/external-validation.ts
moda-interact-commerce/tests/external-tools-ui.test.tsx
moda-interact-commerce/tests/external-tool-authoring-validation.test.ts
moda-interact-commerce/tests/external-tool-authoring-server-actions.test.ts
```

A small Commerce-local diagnostic formatter/helper may be extracted when that keeps
`response-tab.tsx` readable. Do not create a generic application-wide validation
framework for this task.

## Out of Scope

- Changing DIRECT/VISUAL/JAVASCRIPT runtime semantics.
- Changing C048/C049 Visual result-schema derivation or execution.
- Adding new Visual node kinds.
- Request-tab diagnostic changes; C047 owns the bounded Request compiler diagnostic path.
- Live provider calls or Test-tab execution.
- Database/Prisma/Shared changes.
- Publication policy changes.
- Navigation gating or mandatory wizard progression.
- Replacing Zod internally; the requirement concerns the user-facing diagnostic boundary.
- Broad visual redesign of the Response tab.

## Architectural Decision

### AD1 — local invalid authoring is diagnosed locally

The authoritative Response Server Action validates **canonical candidates**. It must not
be invoked with synthetic `null` placeholders merely because the current browser-local
Visual tree cannot yet be canonicalised.

For Visual mode:

```text
deriveVisualTreeContract(current local tree)
        |
        +-- ok
        |    -> call authoritative Response validation with exact processing/schema
        |
        +-- invalid
             -> DO NOT call the Server Action
             -> convert the derivation failure into one actionable local validation issue
             -> retain every attempted local value
```

This is not client-side replacement of authoritative validation. The server remains
authoritative whenever there is a canonical candidate to validate.

### AD2 — stable codes/paths remain internal contracts; prose is product-facing

Keep stable diagnostic `code` and `path` values for tests, routing and optional technical
details. Do not make users decode them in the normal validation result.

Default presentation should be equivalent to:

```text
Response configuration needs changes.

field2 — Result type
Choose a result type: string, integer, number, or boolean.
```

not:

```text
/execution/responseProcessing (invalid_type): Invalid input: expected object, received null
```

Raw path/code may be shown only in an optional secondary **Technical details** disclosure.
They must not be the only explanation.

### AD3 — format by stable semantic code, not arbitrary message parsing

For known Visual derivation failures, derive presentation from the stable C048/C049
error code/path/current authoring tree. Do not inspect English message substrings to
decide what happened.

For authoritative server issues, use stable issue `code` + deterministic path families.
Unknown issues receive a safe actionable fallback rather than raw Zod prose.

## Requirements

### R1 — exact Visual short-circuit

In `response-tab.tsx`, when:

```text
currentMode === VISUAL
and deriveVisualTreeContract(currentVisual).ok === false
```

clicking **Validate response** MUST:

```text
- not invoke onValidateResponse;
- set Response validation state to invalid;
- preserve all local authoring values;
- surface the exact local derivation problem in actionable form;
- keep onValidationChange(false);
- perform no canonical mutation/persistence.
```

Do not send:

```text
responseProcessing: null
resultSchema: null
```

as a substitute for the invalid local tree.

DIRECT/JAVASCRIPT and valid VISUAL candidates continue through the authoritative Server
Action exactly as before.

### R2 — actionable Visual diagnostic mapping

Provide deterministic user-facing mappings for at least these derivation codes:

```text
MISSING_RESULT_TYPE
INVALID_PATH
DUPLICATE_OUTPUT_NAME
UNSAFE_OUTPUT_NAME
INVALID_LIST_SETTINGS
INVALID_FILTER
NO_FIELDS
TOO_MANY_FIELDS
TOO_MANY_NODES
MAX_DEPTH
INVALID_RESULT_SCHEMA
```

The message must identify the affected field/control when the path permits it and state
the correction.

Required examples:

```text
MISSING_RESULT_TYPE on Scalar field "field2"
  title:   field2 — Result type
  message: Choose a result type: string, integer, number, or boolean.

MISSING_RESULT_TYPE on SCALAR_LIST field "tags"
  title:   tags — Item type
  message: Choose an item type: string, integer, number, or boolean.

INVALID_PATH on field "tags"
  title:   tags — Projection source
  message: Enter a non-empty safe dot path, for example product.tags.

INVALID_LIST_SETTINGS on a SCALAR_LIST limit
  title:   tags — Limit
  message: Enter a whole number from 1 to 20.

DUPLICATE_OUTPUT_NAME for "tags"
  title:   tags — Output name
  message: This output name is already used. Enter a unique output name.

UNSAFE_OUTPUT_NAME
  title:   <field> — Output name
  message: Enter a safe output identifier using the accepted name format.

NO_FIELDS
  title:   Visual projection
  message: Add at least one projected field.

MAX_DEPTH
  title:   Visual projection
  message: Nested Object/List containers support at most four container levels.
```

Equivalent concise wording is acceptable, but it must preserve the affected concept and
corrective action.

### R3 — distinguish Scalar from List-of-values type wording

`MISSING_RESULT_TYPE` is shared by C048 Scalar and C049 `SCALAR_LIST` authoring. The
formatter MUST inspect the current authoring node at the issue path so the UI says:

```text
Scalar       -> Result type
SCALAR_LIST  -> Item type
```

Do not display "result type" for a list-of-values item-type selector when the current
node is `SCALAR_LIST`.

### R4 — user-facing validation list must not lead with internal paths/codes

Replace the current default list rendering:

```tsx
<code>{entry.path}</code> ({entry.code}): {entry.message}
```

with a product-facing diagnostic presentation containing at least:

```text
human field/control title
corrective message
```

Internal `path` and `code` may be retained in DOM data attributes/tests and may appear
inside one collapsed `Technical details` disclosure.

The normal Response panel MUST NOT show generic parser phrases such as:

```text
expected object, received null
Invalid input
invalid_type
custom
```

when a more specific local/domain diagnostic is known.

### R5 — defensive authoritative-server messages

The server boundary still accepts `unknown` and must fail safely for malformed callers.
Improve Response-specific schema-issue mapping so ordinary top-level invalid values for:

```text
responseProcessing
resultSchema
responseFormat
resultPath
```

produce bounded domain messages rather than exposing raw Zod prose.

Examples:

```text
/responseProcessing invalid/missing canonical value
  code:    invalid_response_processing
  message: Response processing is incomplete or invalid.

/resultSchema invalid/missing canonical value
  code:    invalid_result_schema
  message: The processed result contract is incomplete or invalid.
```

Use more specific existing diagnostics when available. Do not weaken strict runtime
validation and do not echo rejected raw values.

### R6 — canonical server issues remain authoritative

For a valid local canonical candidate, continue to call the Response Server Action.
Translate returned issues into actionable presentation without changing their semantic
result.

At minimum cover:

```text
response format / media type
Source path
Visual processing/result-schema incompatibility
JavaScript compile diagnostic
Direct/JavaScript explicit result-schema failure
```

Do not hide JavaScript compiler information that is already safe and useful.

### R7 — keep local error and validation summary coherent

The Visual editor may continue to display an inline/local error close to the authoring
controls. The validation summary may repeat the same problem once, but must not show two
contradictory descriptions of the same edit.

Deduplicate identical issues by stable semantic identity such as:

```text
code + path
```

Do not clear the user's raw invalid value simply to remove duplicate messages.

### R8 — accessibility

Actionable diagnostics must remain discoverable without relying on colour.

Preserve/use:

```text
role="alert" for current authoring errors where appropriate
aria-live for validation status
associated field/control wording in visible text
```

Do not require users to infer the failing field solely from an internal JSON path.

### R9 — no workflow/gating change

Validation failure remains advisory for navigation:

```text
Request / Response / Test / Agent contract / Review remain freely navigable
```

Save/Create validity rules remain those already accepted by C045/C048/C049. This task
changes diagnostics, not canonical validity.

### R10 — no new I/O

The local invalid-Visual short-circuit performs zero provider/credential/network/database
work. Existing Response Server Action zero-I/O proofs must remain green.

## Work Items

- [ ] Add one Response diagnostic-presentation mapper for stable Visual/server issues.
- [ ] Short-circuit Validate response on an invalid local Visual tree instead of sending null placeholders.
- [ ] Distinguish Scalar `Result type` from SCALAR_LIST `Item type` diagnostics.
- [ ] Replace raw path/code-first validation rendering with actionable field/control text.
- [ ] Keep optional technical path/code details secondary/collapsed if retained.
- [ ] Translate top-level malformed Response Server Action values into bounded domain diagnostics.
- [ ] Preserve safe JavaScript compiler diagnostics and existing canonical validation behavior.
- [ ] Deduplicate local/server presentation without losing invalid raw edits.
- [ ] Add focused UI/server regressions for the manual reproduction and adjacent Visual cases.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-044
  Response-only authoritative validation boundary

ARCH-021-COMMERCE-045
  local raw/canonical Response state + stale-validation behavior

ARCH-021-COMMERCE-048
  recursive Visual derivation error codes/paths

ARCH-021-COMMERCE-049
  SCALAR_LIST authoring and item-type semantics
```

Produces no new cross-repository or durable contract.

## Dependencies

- ARCH-021-COMMERCE-049

## Enables

None.

## Acceptance Criteria

- [ ] Invalid local Visual authoring is diagnosed locally when Validate response is clicked; no null placeholder is sent to the Server Action.
- [ ] A missing Scalar result type names the actual field and tells the user to choose string/integer/number/boolean.
- [ ] A missing SCALAR_LIST item type says `Item type`, not generic `Result type`.
- [ ] Invalid Visual path, limit, duplicate name and empty projection have explicit corrective text.
- [ ] Normal UI no longer leads with JSON pointers, issue codes, `invalid_type`, `custom`, `Invalid input`, or `expected object, received null`.
- [ ] Optional technical details may retain deterministic path/code without replacing the actionable explanation.
- [ ] Valid Visual candidates still invoke authoritative Response validation exactly once.
- [ ] DIRECT and JAVASCRIPT authoritative validation behavior is unchanged apart from clearer presentation.
- [ ] Safe JavaScript compiler diagnostics remain visible.
- [ ] Malformed direct Server Action callers receive bounded Response-domain issues without raw rejected values.
- [ ] Invalid raw edits remain visible and previous validation remains stale.
- [ ] Other authoring tabs remain navigable.
- [ ] Response validation remains zero provider/credential/network/persistence I/O.
- [ ] No Shared/Prisma/database/result-schema/runtime-processing change is introduced.

## Mandatory Regression Scenarios

Add named tests proving at least:

```text
1. Visual OBJECT has fields value:string and field2:Scalar with blank Result type;
   click Validate response;
   onValidateResponse is NOT called;
   UI says `field2 — Result type` and tells user to choose string/integer/number/boolean.

2. Scenario 1 does not render:
   `expected object, received null`
   `Invalid input`
   `invalid_type`
   `(custom)`
   `/execution/responseProcessing`
   as the primary visible validation message.

3. SCALAR_LIST with blank Item type reports `tags — Item type` with supported choices.

4. SCALAR_LIST limit 21 reports `tags — Limit` and `whole number from 1 to 20`.

5. invalid Projection source reports the field and a safe-dot-path correction.

6. duplicate Visual output names retain both attempted names and report the duplicate name correction.

7. empty Visual projection reports `Add at least one projected field`.

8. valid Visual candidate invokes the authoritative Response Server Action exactly once and renders success.

9. authoritative Visual processing/result-schema mismatch renders a domain explanation rather than raw parser text.

10. malformed Server Action input with null responseProcessing/resultSchema returns bounded domain issue codes/messages.

11. JavaScript compile failure retains the accepted safe compiler diagnostic/presentation.

12. Direct invalid processed-result schema receives a clear processed-result-contract message.

13. editing after success still immediately returns validation state to `Not validated`.

14. all invalid-local cases retain attempted browser values and do not gate tab navigation.

15. zero-I/O Response validation regression remains green.
```

## Validation

Run the focused repository scripts covering:

```text
External HTTP UI
External Response authoring validation
External validation Server Actions
common Tool authoring regression packet where required by repository conventions
```

Then run targeted lint/diagnostics for changed files and:

```bash
git diff --check
```

Repository-wide typecheck may retain the established unrelated baseline only when no
C050-modified file has a diagnostic; record exact evidence in the Completion Report.

## Stop Condition

After the manual reproduction and mandatory diagnostic scenarios show field-specific,
corrective Response validation messages with no null-placeholder/raw-Zod primary errors,
set the task to `review`, complete the Completion Report and STOP.

Do not continue into Response visual redesign, provider/Test execution, new Visual node
kinds, publication policy or unrelated authoring diagnostics.

## Completion Report

### Status
Ready for Architect Review (Attempt 1; implementation commit `e4f6226` pushed)

### Files Changed
- `moda-interact-commerce/src/studio/external-http/response-tab.tsx`
- `moda-interact-commerce/src/commerce/tool-authoring/external-validation.ts`
- `moda-interact-commerce/tests/external-tools-ui.test.tsx`
- `moda-interact-commerce/tests/external-tool-authoring-validation.test.ts`
- `moda-interact-commerce/tests/external-tool-authoring-server-actions.test.ts`

### Work Completed
- Invalid browser-local Visual trees now short-circuit Response validation locally; canonical Visual candidates continue through the authoritative Server Action.
- Added field/control-specific Visual guidance for all stable derivation codes, including Scalar versus SCALAR_LIST item types; issue paths/codes are confined to collapsed Technical details.
- Mapped malformed top-level Response format, processing, schema, and path values to bounded domain diagnostics; preserved safe Response JavaScript compiler messages and locations.
- Added UI and Server Action regressions for the manual `field2` reproduction, SCALAR_LIST type/limit, unsafe paths, duplicates, empty projections, server mismatch, JavaScript causes, Direct schema failures, retained edits/navigation, and null payloads.

### Validation Results
- `npm run test:arch020-external-tools-ui`: passed, 40 tests.
- `npm run test:arch021-external-tool-authoring-validation`: passed, 54 tests across Response validation and Server Actions; includes the existing zero-I/O proof.
- Targeted `npx eslint` over all five modified files: passed with zero errors and warnings.
- Editor diagnostics via `get_errors`: no diagnostics in any of the five modified files.
- `git diff --check`: passed.
- `npm run typecheck`: repository baseline remains at 251 errors in 22 files; none reference a C050-modified file.
- `npm run test:arch021-tool-authoring-common`: 85 passed, 1 failed. The unrelated existing `tests/commerce-lifecycle.test.ts` publication fixture uses an empty result schema, so it fails with `INVALID_DEFINITION` before its expected `LIVE_TEST_REQUIRED` assertion. The exact test was rerun in isolation and reproduces the same failure; no lifecycle fixture or schema contract was changed for C050.
- Implementation commit `e4f6226` was pushed to `task/ARCH-021-COMMERCE-050`.

### Deviations
The common Tool-authoring packet has the unrelated lifecycle fixture failure recorded above; it was not changed because publication and result-schema semantics are outside C050.

### Assumptions
None.

### Unresolved Issues
The unrelated common-packet lifecycle fixture and repository-wide TypeScript baseline remain for their owning workstreams; no C050-specific issue is unresolved.

### Architectural Concerns
None.

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
