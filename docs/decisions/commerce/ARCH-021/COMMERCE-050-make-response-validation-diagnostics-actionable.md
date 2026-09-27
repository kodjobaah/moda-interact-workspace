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
status: complete
priority: 65
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-049
enables: []
created: 2026-09-26
updated: 2026-09-27
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

- [x] Add one Response diagnostic-presentation mapper for stable Visual/server issues.
- [x] Short-circuit Validate response on an invalid local Visual tree instead of sending null placeholders.
- [x] Distinguish Scalar `Result type` from SCALAR_LIST `Item type` diagnostics.
- [x] Replace raw path/code-first validation rendering with actionable field/control text.
- [x] Keep optional technical path/code details secondary/collapsed if retained.
- [x] Translate top-level malformed Response Server Action values into bounded domain diagnostics.
- [x] Preserve safe JavaScript compiler diagnostics and existing canonical validation behavior.
- [x] Deduplicate local/server presentation without losing invalid raw edits.
- [x] Add focused UI/server regressions for the manual reproduction and adjacent Visual cases.

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

- [x] Invalid local Visual authoring is diagnosed locally when Validate response is clicked; no null placeholder is sent to the Server Action.
- [x] A missing Scalar result type names the actual field and tells the user to choose string/integer/number/boolean.
- [x] A missing SCALAR_LIST item type says `Item type`, not generic `Result type`.
- [x] Invalid Visual path, limit, duplicate name and empty projection have explicit corrective text.
- [x] Normal UI no longer leads with JSON pointers, issue codes, `invalid_type`, `custom`, `Invalid input`, or `expected object, received null`.
- [x] Optional technical details may retain deterministic path/code without replacing the actionable explanation.
- [x] Valid Visual candidates still invoke authoritative Response validation exactly once.
- [x] DIRECT and JAVASCRIPT authoritative validation behavior is unchanged apart from clearer presentation.
- [x] Safe JavaScript compiler diagnostics remain visible.
- [x] Malformed direct Server Action callers receive bounded Response-domain issues without raw rejected values.
- [x] Invalid raw edits remain visible and previous validation remains stale.
- [x] Other authoring tabs remain navigable.
- [x] Response validation remains zero provider/credential/network/persistence I/O.
- [x] No Shared/Prisma/database/result-schema/runtime-processing change is introduced.

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

- [x] `npm run test:arch020-external-tools-ui`: 47 tests passed, zero skipped.
- [x] `npm run test:arch021-external-tool-authoring-validation`: 54 tests passed, zero skipped; includes Response Server Action zero-I/O coverage.
- [x] `npm run test:arch021-tool-authoring-common`: 85 passed; one unrelated `tests/commerce-lifecycle.test.ts` fixture failure is documented in the Completion Report.
- [x] Required targeted `npm exec eslint` over the five task-specified files: clean.
- [x] `npm run typecheck`: 251 diagnostics in 22 files; zero diagnostics in the five C050-modified files.
- [x] `git diff --check`: clean.

## Stop Condition

After the manual reproduction and mandatory diagnostic scenarios show field-specific,
corrective Response validation messages with no null-placeholder/raw-Zod primary errors,
set the task to `review`, complete the Completion Report and STOP.

Do not continue into Response visual redesign, provider/Test execution, new Visual node
kinds, publication policy or unrelated authoring diagnostics.

## Completion Report

### Status
Ready for Architect Review (Attempt 2; implementation commit recorded below and pushed)

### Physical Worktree Isolation
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-050`
- Parent branch: `task/ARCH-021-COMMERCE-050`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-050`
- Implementation branch: `task/ARCH-021-COMMERCE-050`
- Shared workspace checkout switched/mutated for task work: no.
- Shared implementation checkout switched/mutated for task work: no.
- Another task worktree reused: no.

### Start-of-Attempt Synchronization and Claim
- Parent task synchronization started from `b88fe45e` (Attempt 1 review corrections); `origin/main` was already an ancestor. The remote task branch was current before the Attempt 2 claim commit.
- Implementation synchronization started from `e4f622695c460a588dc788fead80de00ce2fde01`; local branch matched `origin/task/ARCH-021-COMMERCE-050`, and `origin/main` was already an ancestor. No fast-forward or mainline merge was needed.
- Attempt 2 claim evidence: parent commit `01177a2403d428f5858d0e6fd6083331db6d8b38`, which records `status: in_progress`, `executor: copilot`, `claimed_at: 2026-09-27T07:25:54Z`, `attempt: 2`.
- Recursive implementation submodules were materialized by the prepared execution. `git submodule status --recursive` verified database commit `0a8d3b9feade69690b6c1e33aeda051ea588bd45` with no uninitialized, mismatched, or unresolved entries. No `--remote` submodule update was used.

### Files Changed
- `moda-interact-commerce/src/studio/external-http/response-tab.tsx`
- `moda-interact-commerce/src/commerce/tool-authoring/external-validation.ts`
- `moda-interact-commerce/tests/external-tools-ui.test.tsx`
- `moda-interact-commerce/tests/external-tool-authoring-validation.test.ts`
- `moda-interact-commerce/tests/external-tool-authoring-server-actions.test.ts`

### Work Completed
- Invalid browser-local Visual trees now short-circuit Response validation locally; canonical Visual candidates continue through the authoritative Server Action.
- Added field/control-specific Visual guidance for all stable derivation codes, including Scalar versus SCALAR_LIST item types; issue paths/codes are confined to collapsed Technical details.
- Action-level validation failures now render as separate bounded system diagnostics for `DATABASE_UNAVAILABLE`, `INTERNAL_ERROR`, `FORBIDDEN`, and rejected Promises; server messages and fabricated Response paths are not shown, and `onValidationChange(false)` is preserved.
- Mapped malformed top-level Response format, processing, schema, and path values to bounded domain diagnostics; preserved safe Response JavaScript compiler messages and locations.
- Added UI and Server Action regressions for the manual `field2` reproduction, SCALAR_LIST type/limit, unsafe paths, duplicates, empty projections, server mismatch, JavaScript causes, Direct schema failures, retained edits/navigation, and null payloads.

### Validation Results
- `npm run test:arch020-external-tools-ui`: passed, 47 tests; includes `DATABASE_UNAVAILABLE`, `INTERNAL_ERROR`, `FORBIDDEN`, Promise rejection, raw-message suppression, retained Visual/Direct/JavaScript values, validation invalidation and real Request/Response navigation.
- `npm run test:arch021-external-tool-authoring-validation`: passed, 54 tests across Response validation and Server Actions; includes the existing zero-I/O proof.
- `npm run test:arch021-tool-authoring-common`: 85 passed, 1 failed. The unchanged `tests/commerce-lifecycle.test.ts` publication fixture uses an empty external `resultSchema`, so it fails with `INVALID_DEFINITION` before its expected `LIVE_TEST_REQUIRED` assertion. No lifecycle fixture or schema/publication semantics were changed for C050.
- Required `npm exec eslint` over `src/studio/external-http/response-tab.tsx`, `src/commerce/tool-authoring/external-validation.ts`, `tests/external-tools-ui.test.tsx`, `tests/external-tool-authoring-validation.test.ts`, and `tests/external-tool-authoring-server-actions.test.ts`: clean.
- `npm run typecheck`: 251 diagnostics in 22 files; final captured output contains no diagnostics in any of the five C050-modified files.
- `git diff --check`: clean.
- Implementation commit: `823dd4511d195343f2b76dcf1206377960f5b31a`; pushed to `origin/task/ARCH-021-COMMERCE-050`, with upstream parity verified.

### Deviations
The common Tool-authoring packet retains the unrelated lifecycle fixture failure recorded above; it is outside C050's Response-validation presentation scope.

### Assumptions
None.

### Unresolved Issues
The unrelated common-packet lifecycle fixture and repository-wide TypeScript baseline remain for their owning workstreams; no C050-specific issue is unresolved.

### Architectural Concerns
None.

### Attempt 2 Commits and Push Parity
- Implementation commit: `823dd4511d195343f2b76dcf1206377960f5b31a`; push to `origin/task/ARCH-021-COMMERCE-050` verified; implementation worktree clean.
- Final parent Completion Report commit: the parent task branch tip published with this report; exact SHA recorded in the task handoff.
- Parent push: to be verified against `origin/task/ARCH-021-COMMERCE-050`.
- Final parent worktree: to be verified clean after publication.

## Architect Review

### Review Status
Accepted — Attempt 2

### Review Notes

#### Attempt 2 review — Accepted — 2026-09-27

Reviewed implementation `823dd4511d195343f2b76dcf1206377960f5b31a` and the
submitted Attempt 2 Completion Report against the complete Attempt 1 correction
contract.

Attempt 2 is accepted.

The primary C050 local/canonical diagnostic split remains intact: invalid browser-local
Visual trees short-circuit locally; no synthetic null placeholders are sent; Scalar
and SCALAR_LIST result-type guidance remains distinct; canonical
Visual/DIRECT/JAVASCRIPT candidates continue through the authoritative Response
validation action; stable issue paths/codes remain secondary Technical details; and
the production validation composition remains zero provider/DNS/credential I/O.

The Attempt 1 action-error defect is corrected. Authoritative action failures are now
represented through a separate `ResponseActionDiagnostic` rather than fabricated
Response-field issues. The accepted visible guidance is bounded and code-driven:

```text
DATABASE_UNAVAILABLE
  Response validation is temporarily unavailable. Retry.

INTERNAL_ERROR
  Response validation could not be completed. Retry.

FORBIDDEN
  You are not allowed to validate this Response configuration.

rejected Promise / unknown action availability
  Response validation is unavailable. Keep your edits and retry.
```

For those action-level failures:

- no `/execution/responseProcessing` or other fake Response JSON pointer is created;
- the UI does not tell the administrator to change processing/schema/path fields;
- the raw Server Action/thrown message is not exposed;
- the stable action error code is available only in collapsed Technical details;
- local Visual/Direct/JavaScript authoring values remain unchanged;
- `onValidationChange(false)` is preserved;
- Request/Response navigation remains available.

The focused UI regressions prove `DATABASE_UNAVAILABLE` across all three Response
modes, plus explicit `FORBIDDEN`, `INTERNAL_ERROR`, rejected-Promise and real
Request-navigation cases. The normal server issue list remains reserved for
configuration diagnostics returned from successful authoritative validation.

All Work Items, Acceptance Criteria and Validation checkboxes are reconciled.

Submitted validation:

```text
npm run test:arch020-external-tools-ui:
  47/47 PASS, zero skipped

npm run test:arch021-external-tool-authoring-validation:
  54/54 PASS, zero skipped

npm run test:arch021-tool-authoring-common:
  85 PASS / 1 unrelated lifecycle fixture failure

targeted ESLint:
  PASS

npm run typecheck:
  251 diagnostics across 22 baseline files
  0 diagnostics in the five C050-modified files

git diff --check:
  PASS
```

Independent inspection of the submitted `tsconfig.tsbuildinfo` confirms zero semantic
diagnostics in:

```text
src/studio/external-http/response-tab.tsx
src/commerce/tool-authoring/external-validation.ts
tests/external-tools-ui.test.tsx
tests/external-tool-authoring-validation.test.ts
tests/external-tool-authoring-server-actions.test.ts
```

The common-packet failure remains the documented unrelated
`tests/commerce-lifecycle.test.ts` fixture whose empty EXTERNAL_HTTP `resultSchema`
fails as `INVALID_DEFINITION` before that test's expected `LIVE_TEST_REQUIRED`.
C050 changes no lifecycle, publication, result-schema or gate semantics, so that
fixture failure does not block this presentation-only task.

The Completion Report now records the canonical parent/implementation worktrees,
matching task branches, start-of-attempt synchronization, fresh Attempt 2 claim,
recursive submodule materialization, database submodule commit and implementation
push parity.

The final user handoff identifies parent report commit
`358a4482860bdac30544f2e9222fc47537bc40e2` and states both task branches are
upstream-aligned and clean. The embedded report intentionally cannot self-record that
final report-publication hash and still says the final parent push/clean state will be
verified after publication. The archive contains no Git metadata from which the
architect can reconstruct that self-referential final step. The explicit final
handoff supplies that evidence, so the bookkeeping distinction does not block
acceptance.

No new Visual node semantics, result-schema semantics, provider/Test execution,
persistence, publication policy or authoring-navigation gating was introduced.

C050 has no downstream task to promote.

#### Historical Attempt 1 Changes Requested

#### Attempt 1 review — 2026-09-27

Reviewed implementation `e4f6226` and parent report `b2cacad2` against the complete
C050 task contract.

The primary C050 implementation is architecturally correct and MUST be preserved:

- an invalid browser-local Visual tree short-circuits `Validate response` locally;
- no synthetic `responseProcessing:null` / `resultSchema:null` payload is sent for
  that local-invalid case;
- Scalar `MISSING_RESULT_TYPE` is presented as `Result type`;
- SCALAR_LIST `MISSING_RESULT_TYPE` is presented as `Item type`;
- stable Visual derivation codes are mapped to field/control-specific corrective
  guidance;
- the normal issue list leads with product-facing title/guidance while path/code are
  confined to collapsed Technical details;
- canonical Visual/DIRECT/JAVASCRIPT candidates still use the authoritative Response
  validation Server Action;
- malformed top-level Response values receive bounded Response-domain diagnostics;
- safe JavaScript compiler diagnostics remain visible;
- local invalid edits remain browser-local and do not gate Request/Response/Test/etc.
  navigation;
- the production authoring validation composition remains zero provider/DNS/
  credential I/O;
- submitted `tsconfig.tsbuildinfo` contains zero semantic diagnostics in all five
  C050-modified files.

Attempt 1 is not accepted because one action-level error path is currently presented
as if the administrator's Response processing were invalid, and the Completion
Report does not contain the mandatory prepared-execution/worktree packet or reconciled
task checkboxes.

The following is the complete and authoritative Attempt 2 correction contract.
Do not redesign Visual derivation, result schemas, provider execution, persistence,
publication policy or authoring navigation.

##### A1-R1 — do not turn Server Action availability/auth failures into Response-processing diagnostics

Change:

```text
moda-interact-commerce/src/studio/external-http/response-tab.tsx
moda-interact-commerce/tests/external-tools-ui.test.tsx
```

The current `result.kind === "error"` branch does:

```ts
setResponseValidation({
  state: "invalid",
  message: "Response validation is unavailable. Keep your edits and retry.",
  issues: [{
    path: "/execution/responseProcessing",
    code: result.code,
    message: result.message
  }]
});
```

`presentServerIssue()` then sees `/execution/responseProcessing` and renders guidance
equivalent to:

```text
Response processing
Choose a valid processing mode and correct its settings.
```

for failures such as:

```text
DATABASE_UNAVAILABLE
INTERNAL_ERROR
FORBIDDEN
```

That is product-wrong. The Response configuration may be perfectly valid; the
validation action itself failed.

Required presentation boundary:

```text
authoritative validation returns kind:'ok', valid:false
-> issue list remains field/control-specific Response configuration diagnostics

authoritative validation returns kind:'error'
-> DO NOT fabricate /execution/responseProcessing
-> DO NOT tell the user to change response-processing fields
-> preserve local authoring values
-> keep onValidationChange(false)
-> present one bounded validation-system diagnostic
```

Use deterministic code-based guidance for at least:

```text
DATABASE_UNAVAILABLE
  title:   Response validation
  message: Response validation is temporarily unavailable. Retry.

INTERNAL_ERROR
  title:   Response validation
  message: Response validation could not be completed. Retry.

FORBIDDEN
  title:   Response validation
  message: You are not allowed to validate this Response configuration.
```

Equivalent concise wording is acceptable, but it MUST NOT instruct the administrator
to edit Response processing/schema/path when the failure is action availability or
authorization.

The stable action error code may appear only inside collapsed Technical details.
There is no legitimate Response JSON-pointer path for this action-level failure; do
not invent one under `/execution/...`.

A small distinct `PresentedResponseIssue`/system-issue shape or a separate
action-error rendering branch is acceptable. Do not weaken the existing
`ResponseActionResult` contract.

Also preserve Promise-rejection behavior as an unavailable/retry presentation with
no fabricated Response-field issue.

##### A1-R2 — add executable action-error presentation regressions

In:

```text
moda-interact-commerce/tests/external-tools-ui.test.tsx
```

add focused tests through the actual Response tab for:

```text
1. validateExternalResponse action returns:
   {
     kind:'error',
     code:'DATABASE_UNAVAILABLE',
     message:'database unavailable',
     retryable:true
   }

   -> status/guidance says validation is temporarily unavailable / retry
   -> normal visible text does NOT say:
      "Choose a valid processing mode"
      "Correct the result schema"
      "/execution/responseProcessing"
   -> local Visual/Direct/JavaScript values remain unchanged
   -> onValidationChange remains false
   -> Request tab remains navigable

2. action returns FORBIDDEN
   -> visible guidance is authorization-specific
   -> no Response-field correction is suggested

3. action Promise rejects
   -> visible unavailable/retry message
   -> no fabricated Response-field issue
   -> no raw thrown message is exposed
```

If path/code technical data is retained for action errors, assert it is available only
inside collapsed Technical details and does not use a fake `/execution/...` path.

Keep the existing local-Visual and canonical-server issue regressions unchanged.

##### A1-R3 — reconcile Work Items and Acceptance Criteria

The task was moved to `review` with every Work Item and Acceptance Criterion still
unchecked.

After A1-R1/A1-R2 pass, update each actually satisfied:

```text
## Work Items
## Acceptance Criteria
## Validation
```

checkbox to `[x]`.

Do not mark a criterion satisfied solely from this Architect Review. The implementing
agent owns the durable checklist reconciliation.

The existing common-packet lifecycle failure MAY remain documented as unrelated:

```text
tests/commerce-lifecycle.test.ts
empty EXTERNAL_HTTP resultSchema fixture
-> INVALID_DEFINITION before expected LIVE_TEST_REQUIRED
```

only if it reproduces unchanged and no C050-modified file is involved. C050 MUST NOT
change lifecycle/publication/result-schema semantics merely to make that unrelated
fixture green.

##### A1-R4 — deterministic validation

Run exactly:

```bash
npm run test:arch020-external-tools-ui
npm run test:arch021-external-tool-authoring-validation
npm run test:arch021-tool-authoring-common

npm exec eslint \
  src/studio/external-http/response-tab.tsx \
  src/commerce/tool-authoring/external-validation.ts \
  tests/external-tools-ui.test.tsx \
  tests/external-tool-authoring-validation.test.ts \
  tests/external-tool-authoring-server-actions.test.ts

npm run typecheck
git diff --check
```

Required result:

```text
External HTTP UI: all tests pass, zero skipped
External Response authoring/Server Actions: all tests pass, zero skipped
common packet: all C050-relevant tests pass; only the explicitly unrelated lifecycle
fixture above may remain if unchanged
targeted ESLint: clean
git diff --check: clean
zero TypeScript diagnostics in all C050-modified files
```

No diagnostic in:

```text
src/studio/external-http/response-tab.tsx
src/commerce/tool-authoring/external-validation.ts
tests/external-tools-ui.test.tsx
tests/external-tool-authoring-validation.test.ts
tests/external-tool-authoring-server-actions.test.ts
```

may be classified as baseline.

##### A1-R5 — record the exact Attempt 2 prepared-execution packet

The submitted Completion Report records implementation/report commits and validation
results, but not the exact launcher-prepared physical-isolation/synchronization
packet required by the repository workflow.

Attempt 2 must record the exact launcher-provided:

```text
parent worktree path
implementation worktree path
parent branch = task/ARCH-021-COMMERCE-050
implementation branch = task/ARCH-021-COMMERCE-050
start-of-attempt parent synchronization
start-of-attempt implementation synchronization
Attempt 2 claim evidence / commit
recursive submodule materialization
database submodule commit
implementation commit
final parent report commit
push parity
clean parent worktree
clean implementation worktree
```

Do not infer or reuse Attempt 1 values.

Before handoff set exactly:

```yaml
status: review
attempt: 2
executor: null
claimed_at: null
```

##### Attempt 2 stop condition

Return to architect review only when:

```text
action-level validation failures no longer masquerade as Response-field failures
AND DATABASE_UNAVAILABLE / INTERNAL_ERROR / FORBIDDEN / Promise rejection have
    actionable non-field presentation
AND all existing C050 local/canonical diagnostic regressions remain green
AND task checkboxes are reconciled
AND zero C050-owned type/lint/diff diagnostics remain
AND the exact fresh Attempt 2 launcher/report packet is recorded
```

Then push implementation and parent task branches, return control to
`moda_architect`, and STOP.

Do not continue into Response visual redesign, provider/Test execution, new Visual
node kinds, publication policy or unrelated authoring diagnostics.

### Reviewed Files

- `moda-interact-commerce/src/studio/external-http/response-tab.tsx`
- `moda-interact-commerce/src/commerce/tool-authoring/external-validation.ts`
- `moda-interact-commerce/tests/external-tools-ui.test.tsx`
- `moda-interact-commerce/tests/external-tool-authoring-validation.test.ts`
- `moda-interact-commerce/tests/external-tool-authoring-server-actions.test.ts`
- submitted `tsconfig.tsbuildinfo`
- Attempt 2 Completion Report

### Validation Reviewed

- External HTTP UI: 47/47 passed, zero skipped.
- External Response authoring / Server Actions: 54/54 passed, zero skipped.
- Common Tool-authoring packet: 85 passed; one unchanged unrelated lifecycle fixture
  failure documented.
- Targeted ESLint over all five task-specified files: passed.
- `git diff --check`: passed.
- Full typecheck: 251 diagnostics across 22 baseline files; zero diagnostics in all
  five C050-modified files.
- Independent static review confirms action-level failures use a separate system
  diagnostic path with bounded code-based guidance, raw-message suppression,
  preserved authoring state and no fabricated Response JSON pointer.

### Architecture Conformance

Conforms. C050 changes only Response diagnostic presentation. Local invalid Visual
state remains local, canonical candidates remain server-authoritative, action-level
validation failures remain distinct from Response-field configuration failures,
stable technical codes remain secondary, and provider/persistence/publication/
navigation semantics are unchanged.

### Follow-up

`ARCH-021-COMMERCE-050` is Complete / Accepted at Attempt 2.

No downstream task is enabled by C050. Real provider execution and any future
Test-tab/sample-derived Direct/JavaScript result-schema work remain separate manual
validation follow-up and are not started from this review.
