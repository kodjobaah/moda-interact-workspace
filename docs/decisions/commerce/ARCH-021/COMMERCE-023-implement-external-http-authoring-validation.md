---
id: ARCH-021-COMMERCE-023
architecture_id: ARCH-021
title: Implement External HTTP authoring validation and request preview
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-021-COMMERCE-017
  - ARCH-021-COMMERCE-019
  - ARCH-020-COMMERCE-030
enables:
  - ARCH-021-COMMERCE-021
created: 2026-09-24
updated: 2026-09-25
---

# Implement External HTTP authoring validation and request preview

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Implement the authoritative zero-provider-I/O validator and request-construction preview for canonical Phase 3 `EXTERNAL_HTTP` Tool definitions without depending on Shopify Admin compiler work.

## Context

COMMERCE-016 owns the canonical Commerce Tool definition, COMMERCE-017 owns bounded `buildRequest({args})`, and COMMERCE-019 owns the common validation result/auth/publication gate. This task composes only the External HTTP authoring semantics needed by COMMERCE-021.

## Scope

Primary files:

```text
src/commerce/tool-authoring/external-validation.ts
src/studio/tools/external-validation-server-actions.ts
src/commerce/external-publication/index.ts       # only existing structural helpers needed for visual/response validation
tests/external-tool-authoring-validation.test.ts
package.json
```

## Out of Scope

- Shopify Admin GraphQL validation.
- Real external HTTP requests.
- Credential display/decryption.
- Live-test receipts.
- Tool editor UI.

## Requirements

### R1 — full EXTERNAL_HTTP validation

For a candidate full definition:

1. parse through COMMERCE-016 `CommerceToolDefinitionSchema`;
2. require `execution.kind === 'EXTERNAL_HTTP'`;
3. confirm the exact immutable connection revision exists and its owning connection is enabled;
4. for `DECLARATIVE`, validate request mappings/static safe headers with no network call;
5. for `JAVASCRIPT`, compile through COMMERCE-017;
6. validate response mode:
   - DIRECT: JSON + resultPath/resultSchema structural contract;
   - OBJECT/LIST: accepted visual publication-shape compatibility;
   - JAVASCRIPT: compile the accepted response processor;
7. validate responseTemplate against the resulting resultSchema;
8. return deterministic issues using COMMERCE-019 `ToolAuthoringValidation`.

No DNS, HTTP, provider or credential operation is permitted.

### R2 — request-construction preview

Expose the named Server Action `src/studio/tools/external-validation-server-actions.ts` and require exactly `requireStudioPlatformRole('ADMIN')` before any database-backed validation/preview work. Do not create a function-valued production port or duplicate role matrix. The action accepts exactly:

```ts
{
  source?: string;
  request: unknown;
  arguments: unknown;
  inputSchema: unknown;
}
```

The exact DTO may be expressed as a strict discriminated union for declarative vs JavaScript request mode, but it MUST contain no connection credential value, provider response or absolute origin override.

Before request construction:

1. validate `arguments` through `compileSubset(inputSchema, 'input')`;
2. execute declarative mapping or COMMERCE-017 `buildRequest({args})`;
3. parse the result through COMMERCE-016 `ExternalRequestDescriptorSchema`;
4. return only `ToolAuthoringActionResult<ExternalRequestDescriptor>` using the COMMERCE-019 explicit error contract;
5. map database connectivity failures to `DATABASE_UNAVAILABLE`; never return `unknown`/`UNCONFIRMED` from this non-mutating action.

Preview performs no connection transport call.

### R3 — explicit errors and deterministic issue paths

Validation/preview are non-mutating. `FORBIDDEN`, `INVALID_INPUT`, `NOT_FOUND`, `DATABASE_UNAVAILABLE` and `INTERNAL_ERROR` must remain explicit COMMERCE-019 action results. A rejected validation/preview call MUST NOT be reconciled as a Tool mutation and MUST NOT create `UNCONFIRMED`. Unexpected errors are logged server-side through the approved shared structured logger.

External validation issues use stable paths under `/execution/...`, `/inputSchema` or `/responseTemplate` as appropriate. Maximum issue count and message-safety rules come from COMMERCE-019.

### R4 — publication relationship

This task proves structural validity only. It MUST NOT create a live-test receipt. After successful validation, publication remains blocked by COMMERCE-019 `LIVE_TEST_REQUIRED`.

### R5 — focused validation

Add `test:arch021-external-tool-authoring-validation` proving:

- valid declarative draft passes with zero network calls;
- missing/disabled connection fails;
- request JS syntax/entrypoint/descriptor errors surface;
- request preview validates CommerceAgent arguments before construction;
- DIRECT/Visual/response-JS branches validate deterministically;
- responseTemplate compatibility is enforced;
- provider transport is never called;
- common issue/auth contract comes from COMMERCE-019.

## Work Items

- [x] Add External HTTP full-definition validator.
- [x] Add named, hierarchy-authorized request-construction preview.
- [x] Compose request/response JS and visual/DIRECT structural validation.
- [x] Use COMMERCE-019 explicit action-result and COMMERCE-027 platform-role authorization contracts.
- [x] Add focused zero-provider-I/O tests.

## Interfaces / Contracts

Consumes COMMERCE-016 Tool contracts, COMMERCE-017 request processor and COMMERCE-019 common validation/auth contract.

Produces the authoritative External HTTP validation/preview boundary consumed by COMMERCE-021.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-021-COMMERCE-017
- ARCH-021-COMMERCE-019
- ARCH-020-COMMERCE-030

## Enables

- ARCH-021-COMMERCE-021

## Acceptance Criteria

- [x] External HTTP authoring validation is server authoritative and zero-provider-I/O.
- [x] Request preview receives only schema-validated Tool arguments and returns only a safe descriptor.
- [x] Connection/request/response/template failures use the common bounded diagnostics contract.
- [x] PLATFORM_ADMIN and PLATFORM_SUPER_ADMIN are admitted through hierarchy; merchant roles are denied.
- [x] Validation/preview errors remain explicit and never become mutation UNCONFIRMED state.
- [x] Validation creates no evidence that can satisfy the Phase 3 publication gate.

### Validation
- [x] `npm run test:arch021-external-tool-authoring-validation` (2 files, 37 tests passed, zero skipped)
- [x] `npm run test:arch020-external-publication` (1 file, 13 tests passed)
- [x] required Commerce-016/017/019 contract and authorization suite (6 files, 42 tests passed)
- [x] required ESLint scope (clean)
- [x] `git diff --check` (clean)
- [x] `npm run typecheck` (15 unrelated baseline diagnostics remain; zero diagnostics in task-owned files)
- [x] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not build Tool UI or execute a live HTTP request.

## Implementation Notes

Keep historical fixture utilities available for automated regressions only; they are not publication evidence.

## Completion Report

### Status
Ready for Review

### Files Changed
- `package.json`
- `src/commerce/integration/external/index.ts`
- `src/commerce/tool-authoring/external-validation.ts`
- `src/studio/tools/external-validation-server-actions.ts`
- `tests/external-tool-authoring-validation.test.ts`
- `tests/external-tool-authoring-server-actions.test.ts`

### Work Completed
- Added authoritative, zero-provider-I/O EXTERNAL_HTTP definition validation with canonical schema parsing, immutable connection-revision metadata checks, request/response processor compilation, visual/DIRECT structural validation, and bounded common authoring issues.
- Added the platform-role-authorized request-construction Server Action. It validates CommerceAgent arguments before declarative or JavaScript construction, returns only the safe external request descriptor, and maps explicit action errors without creating mutation evidence.
- Exposed the validator through the existing external integration facade without adding a transport, credential, or publication receipt path.
- Attempt 2 correction mapping: strict preview DTO parsing now occurs before processor construction; only known template incompatibilities map to `/responseTemplate`, while visual projection incompatibilities remain under `/execution/responseProcessing`; runtime processor failures remain explicit internal errors.
- Added executable Server Action tests for authorization denial, database/error mapping, strict DTO rejection, safe descriptor output, and runtime error mapping.
- Added production integration proof with injected DNS and transport spies; authoring validation performs neither provider operation.
- Attempt 3 adds the canonical 16,384 UTF-8-byte preview-source ceiling, representative forbidden top-level DTO rejection, missing/invalid/absent JavaScript descriptor coverage, full-definition compiler infrastructure error classification, LIST projection diagnostics, and credential-read non-access proof.

### Validation Results
- Fresh Attempt 3 launcher packet: prepare succeeded with `prepared_execution: true`, `status: in_progress`, dependency gate passed, execution state claimed, and claim commit `29ef7fabe444984963f617c826aef8d7d9b6d06b` pushed. Claim changed status from `ready` to `in_progress`, incremented attempt from 2 to 3, and recorded executor `copilot` at `2026-09-25T14:39:30Z`.
- Start synchronization evidence: parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-023`, branch `task/ARCH-021-COMMERCE-023`, was reused at launcher head `76c461c4617ff402fe75d9fb65666bde48579b71`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-023`, branch `task/ARCH-021-COMMERCE-023`, was reused at launcher head `3874a282ce400dac444aa86e9f4a4ce0431b9358`; both incorporated current `origin/main` and required no task-branch fast-forward.
- Recursive submodule evidence: `git submodule sync --recursive` and `git submodule update --init --recursive` passed; recursive status was ready and database submodule commit was `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Implementation publication: Attempt 3 commit `1b1e3484eb4446c5ae2e002ec7f85706c073a2db` is pushed to `origin/task/ARCH-021-COMMERCE-023`; local and remote SHAs match and the implementation worktree is clean.
- `npm run test:arch021-external-tool-authoring-validation`: PASS, 2 files and 37 tests.
- `npm run test:arch020-external-publication`: PASS, 1 file and 13 tests.
- Required contract/authorization command: PASS, 6 files and 42 tests.
- Required ESLint scope: PASS.
- `git diff --check`: PASS.
- `npm run typecheck`: non-zero only for 15 unrelated diagnostics in 7 untouched files; zero diagnostics remain in task-owned files.
- Final parent report publication: parent branch remains `task/ARCH-021-COMMERCE-023`; the final report commit is published after this reconciliation, with local/remote parity and a clean parent worktree recorded at handoff.

### Deviations
- None from the bounded Commerce-023 scope. No Shopify Admin validation, live HTTP request, credential display/decryption, live-test receipt, or Tool UI was added.

### Assumptions
- The existing `requireStudioPlatformRole('ADMIN')` hierarchy helper is the authoritative admission contract for platform administrators and super administrators and denial for merchant roles.
- The Attempt 3 implementation branch commit is `1b1e3484eb4446c5ae2e002ec7f85706c073a2db`.

### Unresolved Issues
- Repository-wide typecheck remains non-zero because of 15 unrelated existing diagnostics in untouched files: the code-response preview route imports, agent-configuration tests, C20 fixture test, external wiring test, local MCP diagnostic test, and selected-shop-context tests.
- Repository-wide typecheck remains non-zero because of 15 unrelated existing diagnostics in untouched preview, agent-configuration, C20 fixture, external-wiring, local MCP diagnostic, and selected-shop-context files.
- No C023-owned unresolved issue remains. The previously recorded Commerce-013 integration failures were not part of the Attempt 3 required validation command and remain outside this task-owned diff.

### Architectural Concerns
No new architectural concerns. Attempt 3 preserves the accepted Attempt 2 behavior and adds the canonical UTF-8 source bound, complete preview invalid-input proofs, full-definition runtime classification, credential boundary proof, and LIST projection coverage.

## Architect Review

### Review Status
Accepted — Attempt 3

### Review Notes

#### Attempt 3 review — Accepted — 2026-09-25

Reviewed implementation `1b1e3484eb4446c5ae2e002ec7f85706c073a2db` and the
submitted Attempt 3 Completion Report against the complete Attempt 2 correction
contract.

Attempt 3 is accepted.

A2-R1 is satisfied. The preview `source` trust boundary now uses
`TextEncoder().encode(value).length <= 16_384`, matching the canonical COMMERCE-016
UTF-8 byte ceiling rather than JavaScript string length. The focused Server Action
regression uses multibyte source and proves an over-limit value returns
`INVALID_INPUT` before request processor creation.

A2-R2 is satisfied. Executable preview regressions now prove:

```text
missing declarative mapped input -> INVALID_INPUT
invalid JavaScript descriptor    -> INVALID_INPUT
missing JavaScript descriptor    -> INVALID_INPUT
```

through the real `previewExternalRequestAction()` path, while the accepted safe
descriptor and runtime-failure classifications remain green.

A2-R3 is satisfied. The focused definition-validation path injects a request
processor that returns `RUNTIME_UNAVAILABLE`; the real
`processorDiagnostic(...) -> ExternalAuthoringRuntimeError -> named Server Action`
boundary returns `INTERNAL_ERROR` rather than a structural validation issue.

A2-R4 is satisfied. The strict top-level preview DTO is table-tested for
`unknownField`, `origin`, `credential`, `token`, `authorization`,
`providerResponse` and `body`; each returns `INVALID_INPUT` before processor
creation.

A2-R5 is satisfied. The production
`createExternalIntegration(...).authoringValidation.validate(...)` proof injects
throwing/spied DNS, transport and Prisma credential-read boundaries. Validation
completes structurally while:

```text
dns.resolve                              = 0 calls
transport.execute                        = 0 calls
commerceExternalCredential.findFirst     = 0 calls
```

No execution/credential-resolution/live-provider path is invoked.

A2-R6 is satisfied. Both OBJECT and LIST incompatible visual projections produce the
canonical bounded issue:

```text
path = /execution/responseProcessing
code = incompatible_response_processing
```

while valid DIRECT/OBJECT/LIST and response-template/response-JavaScript behavior
remain intact.

The submitted focused validation reports:

```text
test:arch021-external-tool-authoring-validation: 2 files / 37 tests PASS
test:arch020-external-publication:               1 file / 13 tests PASS
COMMERCE-016/017/019 contract/auth packet:       6 files / 42 tests PASS
targeted ESLint:                                 PASS
git diff --check:                                PASS
```

Inspection of the submitted `tsconfig.tsbuildinfo` shows zero semantic diagnostics in:

```text
src/commerce/tool-authoring/external-validation.ts
src/commerce/integration/external/index.ts
src/studio/tools/external-validation-server-actions.ts
tests/external-tool-authoring-validation.test.ts
tests/external-tool-authoring-server-actions.test.ts
```

The remaining 15 TypeScript diagnostics are confined to the documented unrelated
preview, Agent Configuration, COMMERCE-020 fixture, external-wiring, local MCP and
selected-shop-context baseline surfaces.

Attempt 2 -> Attempt 3 is narrowly scoped: runtime source changes only the canonical
UTF-8-byte preview-source refinement; the remaining task-owned changes are the exact
focused regressions/proofs required by the Architect Review. The additional Shopify
Admin authoring script visible in `package.json` is synchronized COMMERCE-024 state,
not COMMERCE-023 scope expansion.

The Completion Report records the fresh Attempt 3 launcher packet: canonical parent
and implementation worktrees, matching task branches, start synchronization,
fresh claim commit, recursive submodule materialization, database submodule
`0a8d3b9feade69690b6c1e33aeda051ea588bd45`, pushed implementation commit and clean
implementation worktree.

The final handoff identifies parent report commit
`7a889f629c8d582c610c1ae108bfbe0a8292b165`, while the embedded Completion Report
states that the final report commit is published after reconciliation without
recording that hash inline. The archive contains no Git metadata from which the
architect can reconstruct the final self-referential publication step. The durable
task content, cleared claim, reported branch parity and worktree evidence are
otherwise coherent, so this bookkeeping distinction does not block acceptance.

No live HTTP request, credential display/decryption, Tool UI, Shopify Admin
validation implementation or publication/live-test receipt was added.

`ARCH-021-COMMERCE-021` remains Pending after this acceptance because
`ARCH-021-COMMERCE-020` is still not Complete.

#### Historical Attempt 2 Changes Requested

#### Attempt 2 review — 2026-09-25

Reviewed implementation `9612be2b1cbcb5b0d34c863e2bf1f4bd568c2314` and the
submitted Attempt 2 Completion Report against the complete Attempt 1 correction
contract.

Attempt 2 fixes the core architectural defects and those changes MUST be preserved:

- Visual OBJECT/LIST projection incompatibility is reported under
  `/execution/responseProcessing` with `incompatible_response_processing`;
- response-template incompatibility remains under `/responseTemplate`;
- valid DIRECT, OBJECT and LIST processing are focused-tested;
- request/response JavaScript authoring diagnostics retain their execution-source
  paths;
- the preview action parses a strict top-level DTO before request processor creation;
- preview runtime/deadline/throttle/cancel failures map to `INTERNAL_ERROR`;
- named Server Action authorization denial and Prisma connectivity mapping are
  executable;
- the production `createExternalIntegration(...).authoringValidation.validate(...)`
  composition is exercised with injected DNS/transport spies and performs neither
  provider call;
- the focused command now executes both validation and Server Action suites;
- submitted `tsconfig.tsbuildinfo` contains zero semantic diagnostics in the
  COMMERCE-023 task-owned source/test files.

Attempt 2 is not accepted because one runtime contract still differs from the
canonical COMMERCE-016 boundary, several mandatory Attempt 1 proof cases are absent,
and the durable Attempt 2 execution packet/report commit evidence is incomplete.

The following is the complete and authoritative Attempt 3 correction contract. Do
not redesign the External HTTP validator, add Tool UI, perform live HTTP, or begin
COMMERCE-021.

##### A2-R1 — bound preview `source` by the canonical 16,384 UTF-8 BYTES

Change:

```text
src/commerce/tool-authoring/external-validation.ts
tests/external-tool-authoring-server-actions.test.ts
```

The current preview DTO uses:

```ts
source: z.string().max(16_384).optional()
```

`z.string().max()` bounds JavaScript string length, not UTF-8 bytes. COMMERCE-016
defines the persisted request-JavaScript source ceiling as:

```ts
new TextEncoder().encode(source).length <= 16_384
```

The preview trust boundary MUST use the same observable ceiling.

Required schema behavior:

```text
ASCII source <= 16,384 bytes      -> allowed
UTF-8 multibyte source <=16,384   -> allowed
UTF-8 multibyte source >16,384    -> INVALID_INPUT
```

Use the canonical COMMERCE-016 source schema/helper if one is exported without
broadening scope; otherwise use a local Zod refinement with `TextEncoder`. Do not
truncate source and do not use UTF-16 code-unit count as a proxy.

Add a Server Action regression using multibyte input (for example repeated `😀`) that
would pass `.max(16_384)` by character count but exceeds 16,384 UTF-8 bytes, and
assert:

```ts
{
  kind: 'error',
  code: 'INVALID_INPUT',
  retryable: false
}
```

The request processor must not be created/invoked for the oversized DTO.

##### A2-R2 — complete the exact INVALID_INPUT preview proofs from A1-R3

Change:

```text
tests/external-tool-authoring-server-actions.test.ts
```

Add executable cases through the real `previewExternalRequestAction()` proving:

```text
1. declarative mapped input is absent after input-schema validation
   -> INVALID_INPUT

2. JavaScript request processor returns a descriptor that fails
   ExternalRequestDescriptorSchema
   -> INVALID_INPUT

3. JavaScript request processor returns ok=true but no descriptor
   -> INVALID_INPUT
```

For case 1, the input schema must validly permit omission of the mapped property so
the failure occurs at the declarative mapping boundary rather than being rejected
earlier by `compileSubset()`.

For case 2, use a processor result such as:

```ts
{
  ok: true,
  descriptor: {
    path: 'https://forbidden.example/path',
    query: {},
    headers: {}
  }
}
```

or another descriptor that the canonical COMMERCE-016
`ExternalRequestDescriptorSchema` rejects.

Retain the current strict DTO, safe-descriptor and
RUNTIME_UNAVAILABLE/DEADLINE/THROTTLED/CANCELLED tests.

##### A2-R3 — prove full-definition compiler infrastructure failure is INTERNAL_ERROR

Change:

```text
tests/external-tool-authoring-server-actions.test.ts
```

The Attempt 1 contract requires authoring defects to become validation issues while
compiler/runtime infrastructure failures remain explicit internal action failures.

Add executable `validateExternalToolDefinitionAction()` coverage for at least one
request-processor or response-processor infrastructure result equivalent to:

```text
RUNTIME_UNAVAILABLE
```

through the real external authoring validator path, and assert:

```ts
{
  kind: 'error',
  code: 'INTERNAL_ERROR',
  retryable: false
}
```

Do not satisfy this by throwing an arbitrary Error directly from a mocked
`authoringValidation.validate`; the test must prove the
`processorDiagnostic(...) -> ExternalAuthoringRuntimeError -> Server Action`
classification path.

A bounded production-composition fixture with an injected failing processor is
acceptable if that is the cleanest existing seam.

##### A2-R4 — complete strict top-level DTO rejection coverage

Keep `z.strictObject` and add table-driven Server Action proof for representative
forbidden top-level values:

```text
unknownField
origin
credential
token
authorization
providerResponse
body
```

Each must return `INVALID_INPUT` before request processor creation.

Do not log or echo the rejected values.

##### A2-R5 — prove credential resolution/decryption remains outside authoring validation

Strengthen the existing production integration test in:

```text
tests/external-tool-authoring-validation.test.ts
```

The current DNS/transport spies are valid and must remain.

Also provide spy/throwing Prisma credential boundaries sufficient to prove
`integration.authoringValidation.validate(...)` does not read or resolve credentials.
At minimum expose spies for the credential persistence access used by the accepted
credential service, for example:

```text
commerceExternalCredential.findFirst
```

and assert it remains uncalled during authoring validation.

If the current credential service uses another exact Prisma credential read method in
this repository revision, spy on that exact method instead.

The test must continue to prove:

```text
transport.execute = 0 calls
dns.resolve       = 0 calls
credential read   = 0 calls
```

Do not invoke `integration.execution`, `credentials.resolveConnection`, or a live
provider path merely to prove the negative.

##### A2-R6 — add LIST-side incompatible visual projection proof

The current focused test proves the OBJECT-side incompatible projection. Add the
equivalent LIST-side structural failure and assert the same canonical boundary:

```text
path = /execution/responseProcessing
code = incompatible_response_processing
```

Do not copy/reimplement COMMERCE-016 `visualPublicationCompatible()`.

##### A2-R7 — retain all accepted Attempt 2 behavior

Do not regress:

```text
valid DIRECT / OBJECT / LIST
missing connection
disabled connection
request-JS syntax/entrypoint diagnostic path
response-JS diagnostic path
responseTemplate incompatibility path
strict top-level preview DTO
safe descriptor-only preview result
runtime/deadline/throttle/cancel -> INTERNAL_ERROR
authorization denial -> FORBIDDEN
Prisma connectivity -> DATABASE_UNAVAILABLE retryable=true
missing validator -> DATABASE_UNAVAILABLE retryable=true
zero DNS/HTTP provider calls
no live-test/publication receipt creation
COMMERCE-019 LIVE_TEST_REQUIRED publication relationship
```

No schema/database/Shared/cross-repository change is authorized.

##### A2-R8 — deterministic validation

Keep:

```text
test:arch021-external-tool-authoring-validation
```

executing both COMMERCE-023 focused test files.

Then run exactly:

```bash
npm run test:arch021-external-tool-authoring-validation
npm run test:arch020-external-publication

npm exec vitest run \
  tests/arch021-commerce-tool-contract.test.ts \
  tests/code-request-processor.test.ts \
  tests/tool-authoring-validation.test.ts \
  tests/tool-authoring-server-actions.test.ts \
  tests/auth-role-requirements.test.ts \
  tests/auth-permissions.test.ts

npm exec eslint \
  src/commerce/tool-authoring/external-validation.ts \
  src/commerce/integration/external/index.ts \
  src/studio/tools/external-validation-server-actions.ts \
  tests/external-tool-authoring-validation.test.ts \
  tests/external-tool-authoring-server-actions.test.ts

npm run typecheck
git diff --check
```

All COMMERCE-023 focused tests must execute with zero skips.

No diagnostic in these task-owned surfaces may be classified as baseline:

```text
src/commerce/tool-authoring/external-validation.ts
src/commerce/integration/external/index.ts
src/studio/tools/external-validation-server-actions.ts
tests/external-tool-authoring-validation.test.ts
tests/external-tool-authoring-server-actions.test.ts
```

##### A2-R9 — reconcile the fresh Attempt 3 launcher/report packet

Attempt 2 records the dedicated worktrees and implementation publication, but it does
not durably record all required final parent/report evidence. In particular the final
user handoff identifies parent report commit
`944b277bbd0ce445e1f4088a275903531601b3de`, which is not recorded in the embedded
Completion Report.

Attempt 3 must record the exact fresh launcher-provided:

```text
parent worktree path
implementation worktree path
parent branch = task/ARCH-021-COMMERCE-023
implementation branch = task/ARCH-021-COMMERCE-023
start-of-attempt parent synchronization
start-of-attempt implementation synchronization
Attempt 3 claim evidence / commit
recursive submodule materialization
database submodule commit
implementation commit
final parent report commit
push parity
clean parent worktree
clean implementation worktree
```

Do not reuse or infer Attempt 2 claim/synchronization values.

Reconcile `## Validation`, Work Items, Acceptance Criteria and Completion Report to
the final Attempt 3 counts/evidence.

Before handoff set exactly:

```yaml
status: review
attempt: 3
executor: null
claimed_at: null
```

##### Attempt 3 stop condition

Return to architect review only when:

```text
preview source obeys the 16,384 UTF-8 byte ceiling
AND missing mapped input -> INVALID_INPUT
AND invalid/missing JavaScript descriptor -> INVALID_INPUT
AND full-definition runtime/compiler infrastructure failure -> INTERNAL_ERROR
AND strict top-level DTO representative forbidden fields -> INVALID_INPUT
AND DNS + transport + credential reads are all zero during authoring validation
AND incompatible OBJECT and LIST projections use /execution/responseProcessing
AND every accepted Attempt 2 proof remains green
AND zero task-owned type/lint/diff diagnostics remain
AND the fresh Attempt 3 launcher/report packet is complete
```

Then push implementation and parent task branches, return control to
`moda_architect`, and STOP.

Do not begin COMMERCE-021.

#### Historical Attempt 1 review

#### Attempt 1 review — 2026-09-25

Reviewed implementation `fb5ed5ba` and parent report `c27bc7e1` against the complete
COMMERCE-023 task contract and ARCH-021 Phase 3 invariants.

The implementation direction is correct and MUST be preserved:

- the authoritative validator lives under `src/commerce/tool-authoring/`;
- canonical COMMERCE-016 `CommerceToolDefinitionSchema`,
  `ExternalRequestConstructionSchema`, `ExternalRequestDescriptorSchema` and
  `compileSubset()` are reused rather than redefined;
- exact immutable connection revision metadata and owning connection `enabled` state
  are read server-side;
- declarative request mappings/static headers remain schema-bounded;
- request JavaScript compiles through COMMERCE-017;
- response JavaScript compiles through the accepted response processor;
- request preview validates CommerceAgent arguments before request construction and
  returns only the safe descriptor shape;
- the named Server Actions use `requireStudioPlatformRole('ADMIN')`;
- no live HTTP request, DNS lookup, credential decryption/display or publication
  receipt was added;
- submitted typecheck metadata contains zero semantic diagnostics in the task-owned
  COMMERCE-023 source/test files.

Attempt 1 is not accepted because the Visual/response-template diagnostic boundary,
preview action input/error boundary, and the required focused zero-provider-I/O /
Server Action proof are incomplete.

The following is the complete and authoritative Attempt 2 correction contract.
Do not infer additional work from chat history and do not begin COMMERCE-021.

##### A1-R1 — distinguish Visual projection incompatibility from response-template incompatibility

Change:

```text
src/commerce/tool-authoring/external-validation.ts
tests/external-tool-authoring-validation.test.ts
```

The current validator does:

```ts
try {
  validateDefinitionForPublication(...);
} catch {
  issues.push(
    issue(
      '/responseTemplate',
      'incompatible_response_template',
      'Response template is incompatible with the result schema'
    )
  );
}
```

This is incorrect because `validateDefinitionForPublication()` also throws:

```text
External visual projection is incompatible with resultSchema
```

for OBJECT/LIST projection/resultSchema incompatibility. That failure belongs under
the execution boundary, not `/responseTemplate`.

Required observable result:

```text
Visual OBJECT/LIST projection incompatible with resultSchema
-> valid=false
-> issue.path    = /execution/responseProcessing
-> issue.code    = incompatible_response_processing
-> safe bounded message describing response-processing/result-schema incompatibility

Response template path/token incompatible with the resulting output schema
-> valid=false
-> issue.path    = /responseTemplate
-> issue.code    = incompatible_response_template
```

Continue to use the accepted COMMERCE-016 publication helper as the canonical
compatibility rule. Do NOT copy/reimplement `visualPublicationCompatible()` inside
COMMERCE-023.

A bounded wrapper may classify the accepted helper's known `TypeError` reason, or the
canonical helper may expose a compatible tagged reason while preserving all existing
COMMERCE-016 behavior/tests. Do not create a second visual-validation algorithm.

Add active regressions proving:

```text
valid DIRECT definition passes
valid OBJECT definition passes
valid LIST definition passes
incompatible OBJECT/LIST projection -> /execution/responseProcessing
valid projection + invalid template -> /responseTemplate
response JavaScript compile failure -> /execution/responseProcessing/source
```

The focused suite must no longer satisfy the "Visual" R5 bullet only indirectly.

##### A1-R2 — make the request-preview Server Action input an exact runtime contract

Change:

```text
src/commerce/tool-authoring/external-validation.ts
src/studio/tools/external-validation-server-actions.ts
tests/external-tool-authoring-server-actions.test.ts
```

The TypeScript `ExternalRequestPreviewInput` type is not a runtime trust boundary.
The named Server Action MUST strictly validate the top-level request DTO before
request construction.

Accept exactly:

```ts
{
  source?: string;
  request: unknown;
  arguments: unknown;
  inputSchema: unknown;
}
```

Requirements:

```text
unknown top-level keys -> INVALID_INPUT
top-level origin       -> INVALID_INPUT
top-level credential/token/auth value -> INVALID_INPUT
top-level provider response/body      -> INVALID_INPUT
```

If `source` remains supported, bound it to the same persisted request-JavaScript
source size ceiling. Do not log or echo rejected extra values.

Do not add connection origin, credential, method, body or provider-response fields to
the preview DTO.

The canonical nested request object must still be parsed through
`ExternalRequestConstructionSchema`, which remains responsible for rejecting
absolute origin/method/body/reserved-header capabilities.

##### A1-R3 — do not classify QuickJS runtime/infrastructure failure as INVALID_INPUT

Change:

```text
src/commerce/tool-authoring/external-validation.ts
src/studio/tools/external-validation-server-actions.ts
tests/external-tool-authoring-server-actions.test.ts
```

Current preview behavior collapses every `TypeError` into `INVALID_INPUT`.

That incorrectly turns runtime failures such as:

```text
RUNTIME_UNAVAILABLE
DEADLINE
THROTTLED
CANCELLED
```

into browser-input failures.

Required preview classification:

```text
Zod / strict DTO / schema-validation failure -> INVALID_INPUT
missing declarative mapped input             -> INVALID_INPUT
invalid JavaScript descriptor/output         -> INVALID_INPUT
request JavaScript syntax/entrypoint error    -> INVALID_INPUT

RUNTIME_UNAVAILABLE                           -> INTERNAL_ERROR
DEADLINE                                      -> INTERNAL_ERROR
THROTTLED                                     -> INTERNAL_ERROR
CANCELLED                                     -> INTERNAL_ERROR
unexpected processor/application failure      -> INTERNAL_ERROR
```

Use a small typed local error/result boundary rather than treating arbitrary
application `TypeError`s globally as invalid input.

For full-definition validation, request/response code **authoring errors** remain
bounded validation issues. If a compiler reports an infrastructure/runtime failure
rather than an authoring diagnostic, fail the Server Action explicitly as
`INTERNAL_ERROR`; do not present runtime unavailability as a structurally invalid
Tool definition.

Unexpected/internal failures must continue through the approved COMMERCE-019 shared
logger/error translator and MUST NOT become `unknown` or `UNCONFIRMED`.

Add executable tests for at least:

```text
preview invalid DTO                -> INVALID_INPUT
preview missing mapped input       -> INVALID_INPUT
preview invalid JS descriptor      -> INVALID_INPUT
preview RUNTIME_UNAVAILABLE        -> INTERNAL_ERROR
preview DEADLINE/THROTTLED         -> INTERNAL_ERROR
```

##### A1-R4 — prove the named Server Action authorization/error boundary

Add:

```text
tests/external-tool-authoring-server-actions.test.ts
```

Use module mocks only at the accepted named boundaries:

```text
requireStudioPlatformRole
getCommerceBackend
createCodeRequestProcessor
```

Required executable cases:

```text
authorization denied
-> FORBIDDEN
-> backend validation not called
-> request processor not called

validate action + Prisma P1001/P1002/P1008/P1017
-> DATABASE_UNAVAILABLE
-> retryable=true

missing external authoring validator
-> DATABASE_UNAVAILABLE
-> retryable=true

valid full-definition validation
-> kind:'ok'
-> bounded ToolAuthoringValidation returned

valid request preview
-> kind:'ok'
-> only {path, query, headers} descriptor returned
-> no unknown/UNCONFIRMED field exists
```

The role hierarchy itself remains owned/proved by COMMERCE-019/027. Do not create a
new role matrix.

##### A1-R5 — replace the fake transport assertion with an executable zero-provider-I/O proof

Change/add focused validation so R5 genuinely proves provider transport is untouched.

The current focused test:

```ts
const transport = vi.fn();
...
expect(transport).not.toHaveBeenCalled();
```

does not pass that spy into the implementation and therefore proves nothing.

Add one executable integration-boundary regression around the production
`createExternalIntegration(...).authoringValidation.validate(...)` composition.

Inject throwing/spied:

```text
ExternalHttpTransport.execute
DnsResolver.resolve
```

and call ONLY:

```text
integration.authoringValidation.validate(candidateDefinition)
```

Provide the minimum Prisma connection-revision metadata fixture required for that
validation.

Assert:

```text
validation completes deterministically
transport.execute call count = 0
dns.resolve call count        = 0
```

No connection credential resolution/decryption method may be invoked by
`authoringValidation.validate`.

If a small existing integration fixture already exposes suitable spies, reuse it.
Do not introduce a second production validation composition.

Also remove the current unused local `transport = vi.fn()` assertion from
`tests/external-tool-authoring-validation.test.ts`.

##### A1-R6 — retain all required structural branches and publication relationship

Do not regress the existing proof for:

```text
missing connection
disabled connection
declarative argument validation before request construction
request JavaScript compile errors
response JavaScript compile errors
safe descriptor output
responseTemplate compatibility
```

Add explicit valid Visual OBJECT/LIST coverage from A1-R1.

Validation remains structural only. It MUST NOT create or write any live-test/sample
receipt. Keep the COMMERCE-019 publication regression proving a successfully
validated new definition still fails publication with the exact
`LIVE_TEST_REQUIRED` gate.

##### A1-R7 — deterministic validation commands

Update:

```text
test:arch021-external-tool-authoring-validation
```

so it executes both:

```text
tests/external-tool-authoring-validation.test.ts
tests/external-tool-authoring-server-actions.test.ts
```

plus the zero-provider-I/O integration proof if it is placed in a separate file.

Then run exactly:

```bash
npm run test:arch021-external-tool-authoring-validation
npm run test:arch020-external-publication

npm exec vitest run \
  tests/arch021-commerce-tool-contract.test.ts \
  tests/code-request-processor.test.ts \
  tests/tool-authoring-validation.test.ts \
  tests/tool-authoring-server-actions.test.ts \
  tests/auth-role-requirements.test.ts \
  tests/auth-permissions.test.ts

npm exec eslint \
  src/commerce/tool-authoring/external-validation.ts \
  src/commerce/integration/external/index.ts \
  src/studio/tools/external-validation-server-actions.ts \
  tests/external-tool-authoring-validation.test.ts \
  tests/external-tool-authoring-server-actions.test.ts

npm run typecheck
git diff --check
```

All COMMERCE-023 focused tests must execute with zero skips.

No diagnostic in these surfaces may be classified as baseline:

```text
src/commerce/tool-authoring/external-validation.ts
src/commerce/integration/external/index.ts
src/studio/tools/external-validation-server-actions.ts
tests/external-tool-authoring-validation.test.ts
tests/external-tool-authoring-server-actions.test.ts
```

The two reported COMMERCE-013/backend bootstrap expectation failures may remain
documented only if they reproduce unchanged and no stack/task-owned source is
involved.

##### A1-R8 — record the exact Attempt 2 prepared-execution packet

The Attempt 1 Completion Report gives worktree paths and branch but does not record
the complete required launcher packet.

Attempt 2 must record the exact launcher-provided:

```text
parent worktree path
implementation worktree path
parent branch = task/ARCH-021-COMMERCE-023
implementation branch = task/ARCH-021-COMMERCE-023
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

Do not reuse/infer Attempt 1 values.

Reconcile the human-readable Validation section and Completion Report to the final
Attempt 2 command counts rather than retaining the Attempt 1 6-test count.

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
Visual structural failures have /execution/responseProcessing paths
AND template failures remain /responseTemplate
AND the preview top-level DTO is strict
AND expected authoring failures -> INVALID_INPUT
AND runtime/infrastructure failures -> INTERNAL_ERROR
AND named Server Action auth/database/result mapping is executable
AND real production validation composition proves zero transport + zero DNS
AND DIRECT/OBJECT/LIST/response-JS branches are all focused-tested
AND structural validation still creates no publication evidence
AND no task-owned type/lint/diff diagnostic remains
AND the fresh Attempt 2 launcher/report packet is complete
```

Then push implementation and parent task branches, return control to
`moda_architect`, and STOP.

Do not begin COMMERCE-021.

### Reviewed Files

- `src/commerce/tool-authoring/external-validation.ts`
- `src/studio/tools/external-validation-server-actions.ts`
- `src/commerce/integration/external/index.ts`
- `src/commerce/tool-authoring/contracts.ts`
- `src/commerce/tool-definition/contracts.ts`
- `src/commerce/tool-definition/publication.ts`
- `src/commerce/code-request/processor.ts`
- `src/commerce/code-response/processor.ts`
- `tests/external-tool-authoring-validation.test.ts`
- `tests/external-tool-authoring-server-actions.test.ts`
- `package.json`
- submitted `tsconfig.tsbuildinfo`
- Attempt 3 Completion Report
- Attempt 2 and Attempt 3 submitted snapshots for scoped diff comparison

### Validation Reviewed

- `npm run test:arch021-external-tool-authoring-validation`: 37/37 passed across
  2 files, zero skipped.
- `npm run test:arch020-external-publication`: 13/13 passed.
- Required COMMERCE-016/017/019 contract/auth packet: 42/42 passed across 6 files.
- Targeted ESLint over the COMMERCE-023 source/tests: passed.
- `git diff --check`: passed.
- Submitted full typecheck: 15 diagnostics on documented unrelated baseline files.
- Independent `tsconfig.tsbuildinfo` inspection: zero semantic diagnostics in all
  COMMERCE-023 task-owned source/test files.
- Independent Attempt 2 -> Attempt 3 diff inspection confirms only the UTF-8 source
  refinement plus required focused regression/proof changes in COMMERCE-023-owned
  code.

### Architecture Conformance

Conforms. External HTTP authoring validation remains server-authoritative and
zero-provider-I/O, reuses the canonical Commerce definition/request/descriptor
contracts and accepted QuickJS processors, returns bounded deterministic diagnostic
paths, and keeps preview errors explicit without mutation reconciliation. Structural
validation creates no live-test/publication evidence; COMMERCE-019
`LIVE_TEST_REQUIRED` remains the publication gate.

### Follow-up

`ARCH-021-COMMERCE-023` is Complete / Accepted at Attempt 3.

`ARCH-021-COMMERCE-021` remains Pending because
`ARCH-021-COMMERCE-020` is not yet Complete. Do not start COMMERCE-021 from this
review.
