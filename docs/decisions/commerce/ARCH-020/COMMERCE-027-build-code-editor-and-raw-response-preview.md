---
id: ARCH-020-COMMERCE-027
architecture_id: ARCH-020
title: Build code editor and raw-response preview
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 150
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-017
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
created: 2026-09-21
updated: 2026-09-22
---

# Build code editor and raw-response preview

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Frontend only: src/studio/code-response/** exports CodeResponsePanel and RawResponseSamplePanel for023 slots. Implement exact C21 section6 controls and XN04 against injected ports. No host-page/sidebar changes, engine or live fetch.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Frontend only: src/studio/code-response/** exports CodeResponsePanel and RawResponseSamplePanel for023 slots. Implement exact C21 section6 controls and XN04 against injected ports. No host-page/sidebar changes, engine or live fetch.

## Out of Scope

Writes, OAuth, unsandboxed code, customer-specific lookups, live credentials or
WhatsApp sends, pricing/merchant feature overrides, automatic API discovery,
external-result caching and other owners' implementation files. No live deployment.

## Requirements

Use C21 named interfaces and bounded examples. All dependencies must be accepted
Complete before claim. Readiness is not execution. Component tasks may prove their
ports with fixtures; only024 and SYSTEM-TEST-002 claim real assembled flow.
Protect every UI command against double clicks, preserve same-operation retries,
and never expose secrets or raw external response data in errors/logs.

## Work Items

- [x] Provide locally bundled editor, source/version docs, format-aware raw sample and processed JSON/template panels. HTML/XML stay escaped text; no innerHTML/eval or external editor CDN.
- [x] Implement typed compile/test/cancel/read ports from section2.3, content-hash stale checks, save-before-run, duplicate guards, error retention and unknown-run reconciliation.
- [x] Show schema diagnostics with JSON Pointer, expected type and bounded safe message; no provider source/secret echoed in generic error. Existing successful result is stale after edits.
- [x] Include illustrative plain-text, JSON, HTML, XML and simple CSV extraction examples; explain no DOM/imports/full parser libraries. Published code read-only; source diff on new draft.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-SHARED-002
- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-017

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024

## Acceptance Criteria

- [x] X12/XN04: Text ->Code->sample->compile->save->run->schema failure->correct->save/run->return/publish handoff; same flow works for JSON.
- [x] No browser execution or active HTML, role/pending/cooldown/abort states accessible on keyboard/narrow layout; late results cannot validate changed code.
- [x] Both panels build/test independently of023/026 using agreed fixtures;024 owns actual host installation and engine calls.

## Validation

Provide `test:arch020-code-editor` in the owning repository and document its exact scope.
Run focused changed-boundary tests, then existing repository typecheck/build
and lint where defined. Inspect package scripts first; do not invent a claim that
an absent script passed. Use C21 controlled transports and isolated stores.
Follow current developer-owned live/container validation policy; clearly separate
actual agent results from required unrun developer checks. No arbitrary screenshot
quota or repeated full-suite runs without new changes/failures.

## Stop Condition

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
merge main, publish service deployments or update workspace service gitlinks.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

## Implementation Notes

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
implementation on main. Preserve unrelated work and existing task claims.

## Completion Report

### Status

Review-ready, Attempt 3 implementation submitted to `moda_architect`.

### Files Changed

- `moda-interact-commerce/src/studio/code-response/contracts.ts`
- `moda-interact-commerce/src/studio/code-response/code-response-panel.tsx`
- `moda-interact-commerce/src/studio/code-response/raw-response-sample-panel.tsx`
- `moda-interact-commerce/src/studio/code-response/index.ts`
- `moda-interact-commerce/tests/code-editor.test.tsx`
- `moda-interact-commerce/package.json`

### Work Completed

Added independently mountable `CodeResponsePanel` and
`RawResponseSamplePanel` with typed injected ports. The code panel provides
locally bundled source editing with line numbers, runtime/API guidance, five
bounded examples, validation diagnostics, save-before-run, duplicate guards,
cancel and unknown-run reconciliation, stale-result invalidation, draft restore,
read-only published mode and publish handoff. The raw-response panel captures
bounded status/content type/JSON-or-text/body input and displays processed JSON
and rendered text without HTML injection or browser execution. HTML/XML/CSV
examples remain escaped text and the UI explains that parsing is string-only.

The ports preserve the C21 content hash, preview run identity and sample fixture
contract; the panels do not perform network calls, evaluate source, or expose
credentials. Host route installation and real sandbox calls remain owned by
COMMERCE-024.

### Validation Results

- `npm run test:arch020-code-editor`: passed, 1 file and 4 tests.
- `npx eslint src/studio/code-response tests/code-editor.test.tsx`: passed.
- `npm run lint`: passed.
- `git diff --check`: passed.
- `npm run typecheck`: not clean because of existing unrelated errors in
  `src/commerce/integration/backend/executors.ts` and
  `tests/code-response-processor.test.ts`; no COMMERCE-027 source or test
  diagnostics were reported.
- `npm run build`: application compilation and QuickJS packaging/smoke passed,
  then Next type checking failed on the same 3 unrelated baseline errors.
- No live provider, sandbox, database, or assembled host-flow validation was
  claimed; those checks belong to COMMERCE-024/SYSTEM-TEST-002.

### Deviations

The panels use the accepted C21/Shared `0.14.2` contract shapes locally and
receive server-owned behavior through injected ports. The launcher dependency
gate passed for SHARED-002, COMMERCE-008 and COMMERCE-017; their physical
accepted SHAs were not included in the launcher packet and were not guessed.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript only inside the specified sandbox.

### Unresolved Issues

No known implementation blocker. COMMERCE-024 must install the exported panels
into U06/U14 and connect accepted compile/sample services before assembled-flow
acceptance.

### Architectural Concerns

No contract contradiction found. The repository-wide typecheck/build baseline
remains separately blocked by the 3 errors listed above.

### Git / VCS

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-027`
  parent branch: `task/ARCH-020-COMMERCE-027`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-027`
  implementation branch: `task/ARCH-020-COMMERCE-027`
  shared workspace checkout switched/mutated: no
  another task worktree reused: no

Start synchronization from launcher: parent and implementation branches were
already current; no remote fast-forward or main incorporation was needed.
Recursive implementation submodules: sync passed, update/init passed,
database at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`.
Implementation commits: `221c913`, `771c1ff`, pushed to the task branch.
Parent report claim commit: `fa865434fa888bf7bb33c241bc04dabd2158c042`;
this report update is the next mirrored parent commit.

### Attempt 2 Completion Evidence

Attempt 2 implements only the architect-requested C21 corrections A1-R1 through
A1-R7. It consumes Shared `TransformSample` and `ExternalResponseFormat` from
`@modainteract/moda-interact-shared@0.14.2`; the browser computes lowercase
SHA-256 over Shared `canonicalJson({ source, runtimeVersion })`; and the local
CodeMirror 6 dependencies are pinned at state `6.7.5`, view `6.43.12`, and
JavaScript `6.2.5`.

The implementation adds local CodeMirror editing, explicit JSON/TEXT raw sample
mode, saved-revision dispatch, retained UNKNOWN run identity, independent
read/cancel controls, cooldown feedback, bounded schema/failure presentation,
and the ADMIN/SUPER_ADMIN published-source and publication-review boundaries.
It remains frontend-only with injected ports. No host installation, sandbox,
live HTTP, credential, backend, receipt, or composition ownership moved into
this task.

Validation performed in the isolated implementation worktree:

- `npm run test:arch020-code-editor`: passed, 1 file and 11 tests.
- `npx eslint src/studio/code-response tests/code-editor.test.tsx`: passed.
- `git diff --check`: passed.
- `npm run lint`: non-zero only for pre-existing `src/studio/connections/connections-ui.tsx:235`; warnings also pre-exist in unrelated files. No touched C21 file diagnostic was reported.
- `npm run typecheck`: non-zero only for `src/commerce/integration/backend/executors.ts:17` (two discriminated-union property errors) and `tests/code-response-processor.test.ts:58` (readonly schema array mismatch). No task-owned diagnostic remains.
- `npm run build`: QuickJS packaging/smoke and application compilation passed; subsequent type checking stopped on the same three unrelated baseline diagnostics.

No live provider, sandbox, database, or assembled host-flow validation was run;
these remain COMMERCE-024/SYSTEM-TEST-002 scope.

Attempt 2 implementation commits: `22619b5`, `0c92e5e`, pushed to
`task/ARCH-020-COMMERCE-027`. The task is handed to `moda_architect` for review.

### Attempt 3 Completion Evidence

Attempt 3 implements every A2 correction from the latest Architect Review without
moving ownership beyond COMMERCE-027:

- **A2-R1:** `code-response-panel.tsx` grants ADMIN and SUPER_ADMIN author/test
  controls only for unpublished drafts. Published source remains read-only for
  both roles; Create draft is available to either role when injected; publication
  review is rendered only for an unpublished SUPER_ADMIN draft and requires the
  current saved hash, validation, completed sample and trimmed reason. The
  focused test proves the SUPER_ADMIN validate/save/run/complete/publish path and
  published immutability.
- **A2-R2:** `contracts.ts` defines and exports `SampleExecutionFailure` with
  MIME_OR_UTF8, CODE, OUTPUT and schema path/expected/message details. The panel
  maps typed failures without inferring SCHEMA from a generic diagnostic and
  preserves bounded safe presentation. The focused test proves schema details are
  shown and rejected values are absent.
- **A2-R3:** `runSample` separates save from run admission: save failure produces
  `Draft could not be saved. No sample run was started.`, allocates no run ID and
  calls no run port. Successful save retains one preview ID before dispatch;
  dispatch uncertainty remains UNKNOWN with that ID. Read and cancel handlers and
  controls serialize through the shared pending state. Focused tests prove
  pre-dispatch failure, retained-ID reconciliation and disabled cross-racing
  controls.

### Attempt 3 Files and Dependencies

- `src/studio/code-response/contracts.ts`
- `src/studio/code-response/code-response-panel.tsx`
- `src/studio/code-response/index.ts`
- `tests/code-editor.test.tsx`

The feature consumes the accepted Shared `TransformSample`, `ExternalResponseFormat`
and `canonicalJson` exports from `@modainteract/moda-interact-shared@0.14.2`. No
dependency or lockfile change was needed. Implementation commit `61d6310` is
pushed to `task/ARCH-020-COMMERCE-027`.

### Attempt 3 Validation

Agent-executed validation in the isolated implementation worktree:

- `npm run test:arch020-code-editor`: **passed**, 1 file and 14 tests.
- `npx eslint src/studio/code-response tests/code-editor.test.tsx`: **passed**.
- `npm run lint`: **non-zero only for the unchanged baseline error** at
  `src/studio/connections/connections-ui.tsx:235`; six unrelated warnings also
  remain. No task-owned lint diagnostic was reported.
- `npm run typecheck`: **non-zero on three unchanged baseline diagnostics only**:
  two discriminated-union property errors at
  `src/commerce/integration/backend/executors.ts:17` and the readonly schema array
  mismatch at `tests/code-response-processor.test.ts:58`. No task-owned type error
  remains.
- `npm run build`: QuickJS packaging, packaged smoke, Prisma client generation and
  Next application compilation **passed**; Next type checking stopped on the same
  three baseline diagnostics.
- `git diff --check`: **passed**.

No live provider, sandbox, database, or assembled host-flow validation was run;
those remain COMMERCE-024/SYSTEM-TEST-002 scope and require developer-owned
validation.

### Attempt 3 Git / VCS Evidence

The prepared launcher supplied and verified:

- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-027`
- parent branch: `task/ARCH-020-COMMERCE-027`
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-027`
- implementation branch: `task/ARCH-020-COMMERCE-027`
- parent and implementation synchronization: current at preparation; no main merge
- recursive submodules: sync/update/init passed; database at
  `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`
- shared/reference checkout or another task worktree mutated: no

Parent claim commit `1d10471770ba1bae2ae0a818ba1884e44e4e2ec2` was supplied by the
launcher. This report update is the next mirrored parent commit. Status is now
`review`; executor and claimed_at are cleared. Stop at Architect Review.

## Architect Review

### Review Status

Changes Requested — Attempt 1.

### Review Notes

Reviewed by `moda_architect` against the exact submitted snapshot representing
implementation `771c1ff` and reported parent handoff `6a7ff5ea`.

Attempt 1 establishes a useful component boundary: `CodeResponsePanel` and
`RawResponseSamplePanel` are independently exported under
`src/studio/code-response/**`, do not make network calls or execute guest source in
the browser, escape raw HTML/XML through normal React text rendering, provide the five
C21 example categories, and expose injected validation/run/read/cancel ports. Focused
tests pass 4/4 and repository/focused lint were reported clean apart from unrelated
baseline typecheck/build diagnostics.

Attempt 1 is **not accepted** because several C21 section 2.3 / section 6 / X12/XN04
requirements are not yet implemented. The items below are the complete Attempt 1
rework contract. Implement only these corrections; do not move host-page, backend,
sandbox, live HTTP, credential, publication-receipt or final composition ownership
into COMMERCE-027.

#### A1-R1 — consume the canonical Shared sample contract; do not invent JSON state

**Source and focused-test changes required.**

The current local `ExternalResponseFixture` adds:

```ts
json: unknown | null;
```

and `RawResponseSamplePanel` infers JSON-vs-TEXT from whether that field is null.
That contradicts C21 section 2.3:

```text
TransformSample = {
  status,
  contentType,
  bodyText
}
```

and the explicit rule that response mode comes from the saved tool definition,
never from inferred sample content.

This currently causes an observable bug: in JSON mode, entering malformed JSON or
the valid JSON value `null` sets `json` to null and silently flips the UI to TEXT.

Make the local UI contract use the accepted Shared package directly:

```ts
import type {
  ExternalResponseFormat,
  TransformSample,
} from '@modainteract/moda-interact-shared/commerce';
```

Remove the local `ExternalResponseFixture` type completely.

Use exactly:

```ts
type RawResponseSamplePanelProps = {
  sample: TransformSample;
  responseMode: ExternalResponseFormat['mode'];
  processed?: Record<string, unknown>;
  renderedText?: string;
  failure?: RawSampleFailure | null;
  onChange?: (sample: TransformSample) => void;
};
```

`responseMode` is supplied from the saved external-tool definition. COMMERCE-027
does not infer or persist it from sample content and does not add a competing
response-format editor owned by COMMERCE-023.

For display only:

- JSON mode may parse `bodyText` to show a bounded local "invalid JSON sample" state;
- that parser result must never be added to `TransformSample`;
- invalid JSON must remain JSON mode;
- JSON literal `null` must remain JSON mode;
- TEXT mode never attempts JSON inference.

The sample-run request must also match C21's saved-revision preview boundary.
Change the UI port request to:

```ts
type SampleRunInput = {
  previewRunId: string;
  toolRevisionId: string;
  fixtureId: string;
  arguments: Record<string, unknown>;
  externalResponseFixture: TransformSample;
};
```

Do **not** send browser-owned `source`, `runtimeVersion` or `contentHash` in
`runSample`. The preview backend runs the saved immutable revision identified by
`toolRevisionId`; source/runtime are validated/saved before dispatch.

Focused regressions:

```text
JSON mode + body "null"
  -> responseMode remains JSON
  -> TransformSample contains status/contentType/bodyText only

JSON mode + malformed body
  -> responseMode remains JSON
  -> explicit invalid-JSON sample state
  -> no automatic switch to TEXT

runSample request
  -> exact keys: previewRunId/toolRevisionId/fixtureId/arguments/externalResponseFixture
  -> no source/runtimeVersion/contentHash keys
```

#### A1-R2 — make content-hash and late-result guards real

**Source and focused-test changes required.**

The current code uses the prop unchanged:

```ts
const currentHash = contentHash;
```

and only protects late **run** results with `draftRevision`. A pending
`validateCode()` call can therefore resolve after source/sample changes and still set:

```text
validation = valid
```

for the new draft. That violates C21:

```text
Every source/sample/schema edit invalidates validation by content hash;
late results apply only to the same draft/hash.
```

Implement one explicit draft-generation guard for both validation and sample runs.

Requirements:

1. every source/sample change increments the generation and clears prior validation,
   processed output and publish eligibility;
2. `validateCode` snapshots `{generation, source, runtimeVersion, contentHash}`;
3. apply `ok` or `invalid` only when:
   - current generation still equals the snapshot generation; and
   - returned `contentHash` equals the exact requested hash;
4. a late validation response for an old generation is discarded with no status
   transition and no stale diagnostic;
5. run/read completion is applied only to the exact generation and exact retained
   `previewRunId`;
6. an external prop change to `toolRevisionId`, `contentHash`, source revision or
   response mode invalidates the old generation rather than leaving accepted success
   attached to a different revision.

C21 defines:

```text
contentHash = SHA256(canonical {source,runtimeVersion})
```

Do not rely on an unrelated stale prop after editing source. Add a browser-safe helper
inside `src/studio/code-response/**` that imports `canonicalJson` from
`@modainteract/moda-interact-shared/commerce` and computes SHA-256 with Web Crypto.
Do not add a second canonical-JSON implementation.

The helper must return lowercase hexadecimal SHA-256 of:

```ts
canonicalJson({ source, runtimeVersion })
```

and the component must use that exact hash for `validateCode` and draft save.

Regression:

```text
start validate for source A/hash A
edit source to B before response
resolve validation ok(hash A)
=> B is NOT marked valid
=> no A diagnostic/success is shown for B
```

#### A1-R3 — save the exact revision before Run and retain same-operation identity

**Source and focused-test changes required.**

C21 requires U06 Run sample to save the current draft first and then execute the
returned saved revision. The current `save()` ignores the returned
`toolRevisionId/editVersion/contentHash`, and `runSample()` continues to use the
original prop `toolRevisionId`.

Maintain an explicit current saved snapshot:

```ts
type SavedDraft = {
  toolRevisionId: string;
  editVersion: number;
  contentHash: string;
};
```

Requirements:

1. successful manual Save stores the returned `SavedDraft`;
2. Run sample first saves whenever the current draft differs from that saved snapshot;
3. the subsequent `runSample` uses the **returned** `SavedDraft.toolRevisionId`;
4. if save fails or cannot be confirmed, zero sample dispatch occurs;
5. the saved `contentHash` must equal the locally computed source/runtime hash before
   Run is enabled;
6. source changes after save mark the saved snapshot stale again.

Preserve exactly one preview identity per admitted Run command.

Before dispatch:

```text
allocate previewRunId once
retain it immediately
freeze exact run payload
```

If the transport throws after admission, the browser cannot prove whether the backend
accepted the run. Treat that as:

```text
status = UNKNOWN
previewRunId = original retained ID
```

and expose **Check original operation** / read status. Do not permit a new Run with a
new ID until the original is resolved terminally.

The current catch path only displays:

```text
Sample could not be started. Keep the input and reconcile before retrying.
```

while discarding the ID, so reconciliation is impossible.

Regression:

```text
run dispatch throws after admission
  -> UNKNOWN shown
  -> original previewRunId retained
  -> new Run disabled
  -> reconcile calls readRun with that exact ID
```

#### A1-R4 — Running, Cancel, cooldown and abort must remain independently usable

**Source and focused-test changes required.**

The current Run path awaits `readRun()` while `pending === "run"`. The Cancel button
therefore remains disabled for the entire read, so a genuinely running backend job
cannot be cancelled until the read finishes.

Do not hold the Run admission lock across status reads.

Required state machine:

```text
Run admitted
  -> dispatch runSample
  -> RUNNING
  -> clear run-command pending state
  -> render both:
       Check run status
       Cancel run

Check run status
  -> readRun(original previewRunId)

Cancel run
  -> cancelRun(original previewRunId)
  -> wait for backend response
  -> terminal CANCELLED or UNKNOWN
```

If cancel/read transport cannot confirm the result, retain the same preview ID and
move/show UNKNOWN. Never manufacture a replacement run.

The local injected port must also have a closed pre-dispatch result for the C21
5-second per-admin cooldown rather than collapsing it into a generic thrown message.
Use exactly:

```ts
type SampleStartResult =
  | { kind: 'accepted'; run: SampleRunResult }
  | { kind: 'cooldown'; retryAfterMs: number }
  | { kind: 'forbidden' }
  | { kind: 'unavailable' };
```

Bounds:

```text
retryAfterMs: integer 1..5000
```

The future COMMERCE-024/031 adapter maps backend quota/cooldown state into this local
UI result. COMMERCE-027 does not implement Redis or quota enforcement.

UI behavior:

- cooldown shows a bounded "Try again in N seconds" status;
- no sample command is in RUNNING state for cooldown;
- input/source/sample stay unchanged;
- duplicate clicks remain disabled while one command is admitted;
- keyboard focus remains on a usable control/status after cancel/reconcile.

#### A1-R5 — enforce the published/role boundary and real publication review

**Source and focused-test changes required.**

C21 section 6 says:

```text
Published source read-only; Create draft to edit.
ADMIN authors/tests.
SUPER_ADMIN publishes with source diff and reason.
```

The current expression:

```ts
const editable = !published || role === "SUPER_ADMIN";
```

allows SUPER_ADMIN to edit published source directly. The Publish button also has no
role gate, so ADMIN can invoke `onPublish`, and the publish callback accepts no reason
or source-diff context.

Use these exact role rules:

```text
published source:
  read-only for every role

ADMIN:
  may Create draft
  may edit an unpublished draft
  may Validate / Save / Run / Cancel / Reconcile
  may NOT Publish

SUPER_ADMIN:
  may inspect source/result
  may Publish an already saved/tested draft
  may NOT mutate published source in place
```

For publication review extend props to include:

```ts
publishedSource?: string;

onPublish?: (input: {
  contentHash: string;
  reason: string;
}) => Promise<void>;
```

Render a bounded publication-review section for SUPER_ADMIN only:

```text
Published source   (read-only)
Candidate source   (read-only)
Reason             (required, trim 1..1000 chars)
Publish
```

A simple side-by-side/read-only source comparison is sufficient; do not add a new
diff package. Publish remains disabled unless the candidate is saved, validation is
current, a successful sample for the same generation exists, and reason is valid.

Known publish failure retains source and reason and displays no success. Do not expose
a Publish control to ADMIN.

#### A1-R6 — implement the actual C21 local editor and bounded failure presentation

**Source/package/focused-test changes required.**

No existing code-editor dependency is present in the submitted package, so C21
requires CodeMirror 6 with locally bundled JavaScript mode. The current textarea plus
`data-language="javascript"` does not provide JavaScript highlighting.

Pin these exact direct dependencies and commit the resulting lockfile:

```text
@codemirror/state@6.7.5
@codemirror/view@6.43.12
@codemirror/lang-javascript@6.2.5
```

Use `EditorView`/`EditorState`, `lineNumbers()` and `javascript()` locally. No remote
CDN/script/theme download. The editor remains controlled by the component and honors
the read-only role/published state.

The visible API/limit reference must include at least:

```text
transform(response)
response.status
response.contentType
response.bodyText
response.json
source <= 16 KiB UTF-8
raw sample body <= 256 KiB UTF-8
processed output <= 48 KiB
maximum output depth 20
no fetch/imports/DOM/timers/host callbacks
```

Label HTML/XML/CSV examples explicitly as **limited string extraction examples, not
full parsers**.

The current `SampleRunResult.diagnostic` is never rendered. Add bounded sample-failure
presentation so code/runtime/output/schema failures are distinguishable. Schema
validation display must include JSON Pointer plus expected type/rule and a bounded safe
message; never render the rejected raw value, provider body, source code, credential,
stack or host path.

At minimum the local rendered failure states must distinguish:

```text
INVALID_JSON_SAMPLE
MIME_OR_UTF8
CODE
OUTPUT
SCHEMA
COOLDOWN
UNAVAILABLE
CANCELLED
UNKNOWN
```

These are UI presentation categories only; do not change Shared MCP error contracts.

#### A1-R7 — complete X12/XN04 focused evidence and reconcile the task record

**Focused validation and task-record changes required.**

The current four tests exercise useful basics but do not prove the task's required
late-validation, save-before-run, same-operation, role/publish, cooldown and raw-format
contracts.

Retain useful existing tests and add the following exact regressions:

```text
HASH / LATE RESULT
- validate A -> edit to B -> late ok(A): B remains unvalidated
- sample edit during run -> late prior result never appears

SAVE / RUN IDENTITY
- changed draft -> Run -> save succeeds -> run uses returned saved toolRevisionId
- save fails/unconfirmed -> zero run dispatch
- run dispatch throws -> UNKNOWN retains original previewRunId -> replay same ID

RUN / CANCEL / COOLDOWN
- RUNNING enables Cancel before any read completes
- Cancel calls exact retained previewRunId
- UNKNOWN read/reconcile never creates a new run ID
- cooldown renders bounded retry status and preserves inputs

RAW SAMPLE CONTRACT
- TransformSample has no json property
- JSON "null" stays JSON
- malformed JSON stays JSON and shows invalid-sample state
- malicious HTML remains literal text; no innerHTML/active node

ROLE / PUBLICATION
- published ADMIN source read-only
- published SUPER_ADMIN source read-only
- ADMIN has no Publish action
- SUPER_ADMIN publish requires valid reason and shows published/candidate source
- known publish failure retains reason and does not show success

EDITOR
- mounted editor is CodeMirror with line numbers and JavaScript language extension
- no remote editor script is added
```

Also render `RawResponseSamplePanel` directly in at least one focused test instead of
proving it only as a child of `CodeResponsePanel`.

After corrections run exactly:

```bash
npm run test:arch020-code-editor
npx eslint src/studio/code-response tests/code-editor.test.tsx
npm run lint
npm run typecheck
npm run build
git diff --check
```

If repository-wide typecheck/build still fail only on an unchanged documented baseline
outside:

```text
src/studio/code-response/**
tests/code-editor.test.tsx
package.json
package-lock.json
```

record the exact diagnostics and prove no task-owned diagnostic. Do not repair unrelated
Commerce execution/Prisma code in COMMERCE-027.

Update Work Items, Acceptance Criteria and Validation checkboxes truthfully in Attempt
2. The submitted Attempt 1 task moved to `review` with every checkbox still unchecked;
that contradicts the execution protocol even apart from the functional issues.

### Reviewed Files

- `src/studio/code-response/contracts.ts`
- `src/studio/code-response/code-response-panel.tsx`
- `src/studio/code-response/raw-response-sample-panel.tsx`
- `src/studio/code-response/index.ts`
- `tests/code-editor.test.tsx`
- `package.json`
- `package-lock.json`
- C21 sections 2.2, 2.3, 6 and 9.5
- this task Completion Report

### Validation Reviewed

Submitted Attempt 1 evidence:

```text
npm run test:arch020-code-editor
  PASS — 4 focused tests

npx eslint src/studio/code-response tests/code-editor.test.tsx
  PASS

npm run lint
  PASS

git diff --check
  PASS

npm run typecheck
  NON-ZERO — reported unrelated existing diagnostics in
  src/commerce/integration/backend/executors.ts and
  tests/code-response-processor.test.ts

npm run build
  QuickJS packaging/smoke and application compilation reached;
  subsequent Next type checking NON-ZERO on the same 3 reported unrelated errors
```

The baseline errors are not the reason for this review outcome. The task-owned
behavioral/contract defects above independently require correction.

### Architecture Conformance

Not yet conformant with C21 X12/XN04.

The component boundary and no-browser-execution principle are directionally correct,
but the submitted implementation currently permits stale validation, loses unknown-run
identity, blocks cancellation while reading, diverges from the Shared `TransformSample`
contract, sends unsaved source/runtime/hash through the sample-run UI port, permits
published SUPER_ADMIN editing, exposes Publish without the required role/reason/diff,
and does not implement the mandated local CodeMirror JavaScript editor.

No change to COMMERCE-023 host ownership, COMMERCE-026 sandbox, COMMERCE-030 receipts,
COMMERCE-031 backend, HTTP transport, credentials, database schema or final COMMERCE-024
composition is authorized by this correction.

### Follow-up

Return the same task to the normal execution path:

```yaml
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next:

```text
/moda-task ARCH-020-COMMERCE-027
```

must claim **Attempt 2 exactly once**.

The implementing agent must read this complete Architect Review before source
inspection, implement only A1-R1 through A1-R7, run the bounded validation above,
update the Completion Report and checkboxes, set the task to review, clear the claim on
handoff, push both mirrored task branches and STOP.

Do not start COMMERCE-024 or COMMERCE-012. They remain dependency-gated.

### Attempt 2 — Changes Requested (2026-09-22)

Reviewed by `moda_architect` against the exact submitted Attempt 2 snapshot
representing implementation commits `22619b5`, `0c92e5e` and parent handoff
`56bc050c`.

Attempt 2 materially closes A1-R1 through A1-R4 and most of A1-R6/A1-R7:

- Shared `TransformSample` / `ExternalResponseFormat` are now the canonical sample
  contract and JSON/TEXT mode is no longer inferred from parsed sample content;
- browser content hashes use Shared `canonicalJson({source,runtimeVersion})` plus
  Web Crypto SHA-256;
- late code-validation and sample-start results are generation-guarded;
- Run saves first and dispatches the `toolRevisionId` returned by that save;
- the admitted `previewRunId` is retained before dispatch and survives an uncertain
  transport outcome;
- RUNNING exposes independent status and cancel controls instead of awaiting an
  automatic read;
- cooldown is represented explicitly;
- the CodeMirror 6 editor is locally bundled with line numbers and JavaScript mode;
- published source is rendered read-only;
- raw JSON `null`, malformed JSON and active-HTML injection regressions are covered;
- focused validation reports 11/11 passing with scoped ESLint and diff checks clean.

Attempt 2 is **not accepted** because three bounded functional gaps remain. The items
below are the complete Attempt 2 rework contract. Do not redesign the editor or expand
COMMERCE-027 into host composition, backend, sandbox, receipt or live-provider work.

#### A2-R1 — make the SUPER_ADMIN publication path reachable without weakening published immutability

**Source and focused-test changes required.**

The current permission gates are:

```ts
const canAuthor = role === "ADMIN" && !published;
const canTest = role === "ADMIN" && !published;
```

while Publish is rendered only for `SUPER_ADMIN` and is disabled until:

```text
saved current hash
+ current validation == valid
+ current sample run == COMPLETED
+ nonblank reason
```

No real mount can satisfy that combination:

```text
ADMIN
  -> can save/validate/run
  -> never gets Publish

SUPER_ADMIN
  -> gets Publish
  -> cannot save/validate/run
  -> local validation remains idle
  -> local run remains absent
  -> Publish remains disabled forever
```

This is a functional X12 failure, not a role-label cosmetic issue.

For an **unpublished draft**, `SUPER_ADMIN` inherits the same author/test controls as
`ADMIN`; only publication remains SUPER_ADMIN-only. For a **published revision**,
source remains read-only for every role and must be cloned before editing.

Use exactly:

```ts
const canAuthor = !published && (role === "ADMIN" || role === "SUPER_ADMIN");
const canTest = !published && (role === "ADMIN" || role === "SUPER_ADMIN");
const canPublish = !published && role === "SUPER_ADMIN" && Boolean(onPublish);
```

`Create draft` from a published revision may be offered to either authorized role when
`onCreateDraft` is supplied. It must never make the published source editable in
place.

Render the publication-review section only for an **unpublished** SUPER_ADMIN draft:

```text
Published source   read-only
Candidate source   read-only
Reason             required trim 1..1000
Publish
```

Publish remains disabled until that same mounted draft has:

```text
current saved contentHash
current code validation success
current COMPLETED sample result
valid reason
```

and still calls:

```ts
onPublish({
  contentHash: currentHash,
  reason: reason.trim(),
})
```

Known publish failure retains source, sample and reason and displays no success.

Focused proof:

```text
SUPER_ADMIN + unpublished draft
  -> can edit
  -> Validate
  -> Save
  -> Run
  -> COMPLETED
  -> enter reason
  -> Publish enabled
  -> onPublish receives exact current hash + trimmed reason

SUPER_ADMIN + published revision
  -> editor read-only
  -> no Publish for the published revision
  -> Create draft available when onCreateDraft exists

ADMIN + unpublished draft
  -> author/test available
  -> no Publish control
```

Do not weaken server-side publication/receipt checks owned by COMMERCE-030/024.

#### A2-R2 — preserve typed runtime failure categories and schema `expected` details end-to-end

**Source and focused-test changes required.**

`RawSampleFailure` defines the required bounded UI categories, but
`SampleRunResult` still carries only an optional generic `diagnostic`, and
`runFailure()` currently collapses every failed run into:

```text
diagnostic present -> SCHEMA
otherwise          -> CODE
```

It also drops `CodeIssue.expected`.

Therefore these required C21 outcomes cannot currently be distinguished:

```text
MIME_OR_UTF8
OUTPUT
SCHEMA expected <rule/type>
```

and the schema panel cannot show the required expected rule/type from a failed sample
run.

Make the local run port structured. Use exactly this discriminated failure contract or
an equivalent shape with the same information:

```ts
export type SampleExecutionFailure =
  | {
      code: "MIME_OR_UTF8" | "CODE" | "OUTPUT";
      message?: string;
    }
  | {
      code: "SCHEMA";
      path: string;
      expected?: string;
      message?: string;
    };

export type SampleRunResult =
  | {
      previewRunId: string;
      status: "RUNNING" | "COMPLETED" | "CANCELLED" | "UNKNOWN";
      values?: Record<string, unknown>;
      renderedText?: string;
    }
  | {
      previewRunId: string;
      status: "FAILED";
      failure: SampleExecutionFailure;
    };
```

Do not use provider body, rejected raw value, source, credential, stack or host path in
the failure object.

Map terminal UI state exactly:

```text
FAILED/MIME_OR_UTF8 -> RawSampleFailure {code:"MIME_OR_UTF8", ...}
FAILED/CODE         -> RawSampleFailure {code:"CODE", ...}
FAILED/OUTPUT       -> RawSampleFailure {code:"OUTPUT", ...}
FAILED/SCHEMA       -> RawSampleFailure {
                         code:"SCHEMA",
                         path,
                         expected,
                         message
                       }
CANCELLED           -> CANCELLED
UNKNOWN             -> UNKNOWN
start cooldown      -> COOLDOWN
start unavailable   -> UNAVAILABLE
```

Keep `forbidden` as the existing bounded authorization message; do not invent a new
Shared MCP error.

The current `runFailure()` must no longer infer SCHEMA merely because a generic
diagnostic exists.

Focused proof:

```text
FAILED MIME_OR_UTF8
  -> visible MIME_OR_UTF8

FAILED OUTPUT
  -> visible OUTPUT

FAILED SCHEMA {
  path:"/price",
  expected:"number",
  message:"Expected number"
}
  -> visible SCHEMA /price expected number
  -> rejected raw value is absent

start unavailable
  -> visible UNAVAILABLE state

start cooldown
  -> visible COOLDOWN state
  -> input preserved
```

The UI categories remain frontend presentation data; do not change the published Shared
MCP error protocol.

#### A2-R3 — distinguish pre-dispatch save failure from UNKNOWN run, and serialize read/cancel reconciliation

**Source and focused-test changes required.**

The current `runSample()` wraps save and dispatch in one `try/catch`. If
`onSaveDraft()` throws **before a preview run is allocated or dispatched**, the catch
still reports:

```text
Run status is unknown. Check the original operation before retrying.
```

That statement is false: no run operation exists to reconcile. The existing Attempt 2
test currently locks in this incorrect message.

Split save from run admission.

Required flow:

```text
validate current draft
  -> save if needed

save fails / save cannot confirm exact current contentHash
  -> zero previewRunId allocation
  -> zero runSample call
  -> activeRun remains null
  -> message:
     "Draft could not be saved. No sample run was started."

save succeeds
  -> allocate exactly one previewRunId
  -> retain UNKNOWN with that ID immediately
  -> dispatch exact frozen run payload

dispatch throws / response cannot confirm same ID
  -> retain UNKNOWN with original previewRunId
  -> Check original operation uses that exact ID
```

Update the existing save-failure regression accordingly:

```text
save throws
  -> port.runSample called 0 times
  -> no Check original operation button
  -> "No sample run was started" visible
```

Also prevent `readRun` and `cancelRun` from racing each other through the single
`pending` state. While one reconciliation request is in flight, do not admit the other.
After it completes, expose the appropriate controls again for the retained run status.

A deterministic implementation is:

```text
pending === "read" || pending === "cancel"
  -> disable both Check status/reconcile and Cancel
```

while keeping both controls present for a RUNNING run when neither request is pending.

Focused proof:

```text
RUNNING
  -> Check run status + Cancel both initially enabled

deferred readRun admitted
  -> second read disabled
  -> Cancel disabled until read resolves
  -> no second reconciliation request admitted

deferred cancelRun admitted
  -> Check run status disabled until cancel resolves
  -> no read/cancel state overwrite
```

### Attempt 2 Validation Reviewed

Submitted evidence:

```text
npm run test:arch020-code-editor
  PASS — 11/11

npx eslint src/studio/code-response tests/code-editor.test.tsx
  PASS

git diff --check
  PASS

npm run lint
  NON-ZERO only on reported pre-existing
  src/studio/connections/connections-ui.tsx diagnostic/warnings

npm run typecheck
  NON-ZERO only on reported pre-existing
  src/commerce/integration/backend/executors.ts diagnostics and
  tests/code-response-processor.test.ts readonly-schema mismatch

npm run build
  QuickJS package/smoke + application compilation PASS;
  subsequent type checking stops on the same three unrelated diagnostics
```

No task-owned C21 diagnostic was reported. Those repository-wide baseline conditions
are not the reason for this review outcome.

For Attempt 3 run exactly:

```bash
npm run test:arch020-code-editor
npx eslint src/studio/code-response tests/code-editor.test.tsx
npm run lint
npm run typecheck
npm run build
git diff --check
```

If the repository-wide commands remain non-zero solely on the same unchanged baseline
outside the task-owned files, record the exact diagnostics and prove there is still no
diagnostic in:

```text
src/studio/code-response/**
tests/code-editor.test.tsx
package.json
package-lock.json
```

Do not repair unrelated Connections, executor or processor-test baseline code.

### Attempt 2 Architecture Conformance

Not yet Accepted.

A1-R1 through A1-R4 and the CodeMirror/raw-sample portions of A1-R6 are materially
corrected. Remaining non-conformance is limited to the unreachable SUPER_ADMIN publish
workflow, loss of typed MIME/OUTPUT/schema-expected failure semantics, and incorrect
UNKNOWN/reconciliation semantics around pre-dispatch save failure plus read/cancel
race admission.

No host-page/sidebar work, COMMERCE-023 visual authoring, COMMERCE-026 sandbox
implementation, COMMERCE-030 receipt logic, COMMERCE-031 preview backend, live HTTP,
credential, database or final COMMERCE-024 composition is authorized by this rework.

### Attempt 2 Follow-up

Return the same task to the normal execution path:

```yaml
status: ready
attempt: 2
executor: null
claimed_at: null
```

The next:

```text
/moda-task ARCH-020-COMMERCE-027
```

must claim **Attempt 3 exactly once**.

The implementing agent must read the complete latest Architect Review before source
inspection, implement only A2-R1 through A2-R3, add the focused regressions above, run
the bounded validation, update the Completion Report/checklists, set the task to
review, clear the claim on handoff, push both mirrored task branches and STOP.

Do not start COMMERCE-024 or COMMERCE-012. They remain dependency-gated.

### Attempt 3 — Accepted (2026-09-22)

Reviewed by `moda_architect` against the exact submitted Attempt 3 snapshot and
parent handoff `98dfc630bbc6e40807f8ce6eb2d265244b609449`. The parent remote
`task/ARCH-020-COMMERCE-027` branch matches that handoff commit. The submitted
implementation commit is `61d6310`; the Commerce implementation remote is not
readable through the current review connector, so implementation review is grounded
in the exact submitted archive.

**Accepted / Complete, Attempt 3.** The A2-R1 through A2-R3 correction contract is
satisfied without expanding ownership beyond the frontend code-response boundary.

Functional acceptance:

- unpublished `SUPER_ADMIN` inherits the same author/test controls as `ADMIN`, while
  publication remains SUPER_ADMIN-only;
- published source stays read-only for every role and exposes only Create draft when
  that injected action is available;
- publication review is rendered only for an unpublished SUPER_ADMIN draft and remains
  gated on the current saved content hash, current validation, current COMPLETED
  sample and a trimmed nonblank reason;
- failed sample results now preserve typed `MIME_OR_UTF8`, `CODE`, `OUTPUT` and
  `SCHEMA` categories, including schema path/expected/message, without exposing a
  rejected raw value;
- pre-dispatch save failure allocates no preview run ID, calls no run port and reports
  that no sample run started;
- once a run is admitted, the original preview ID is retained across dispatch
  uncertainty/read/cancel reconciliation;
- read and cancel reconciliation are mutually serialized and do not create replacement
  operation IDs;
- the accepted Shared `TransformSample`, `ExternalResponseFormat` and canonical
  content-hash behavior, locally bundled CodeMirror editor, browser-execution
  prohibition, saved-revision dispatch and raw-response safety corrections from prior
  attempts remain intact.

Submitted validation reviewed:

```text
npm run test:arch020-code-editor
  PASS — 14/14 focused tests

npx eslint src/studio/code-response tests/code-editor.test.tsx
  PASS

git diff --check
  PASS

npm run lint
  NON-ZERO only on the unchanged documented baseline error in
  src/studio/connections/connections-ui.tsx plus unrelated warnings

npm run typecheck
  NON-ZERO only on the three unchanged documented baseline diagnostics in
  src/commerce/integration/backend/executors.ts and
  tests/code-response-processor.test.ts

npm run build
  QuickJS packaging/smoke, Prisma generation and application compilation PASS;
  subsequent type checking stops on the same three unrelated baseline diagnostics
```

Those repository-wide baseline diagnostics are not regressions introduced by
COMMERCE-027 and do not block acceptance. No live provider, sandbox, database or
assembled host-flow proof is required from this frontend-only task; those remain
COMMERCE-024 / SYSTEM-TEST-002 ownership.

Architecture conformance: **conformant** with the C21 section 6 / X12-XN04 frontend
boundary. No host-page/sidebar, sandbox implementation, publication-receipt, live HTTP,
credential, database or production-composition ownership moved into this task.

No dependant is promoted solely by this acceptance. COMMERCE-024 still has multiple
incomplete dependencies and COMMERCE-012 remains the final implementation checkpoint.
No downstream task is launched automatically.
