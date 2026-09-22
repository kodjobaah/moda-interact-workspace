---
id: ARCH-020-COMMERCE-030
architecture_id: ARCH-020
title: Implement external tool publication validation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 150
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-003
  - ARCH-020-COMMERCE-021
  - ARCH-020-COMMERCE-025
  - ARCH-020-COMMERCE-026
enables:
  - ARCH-020-COMMERCE-031
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
created: 2026-09-21
updated: 2026-09-22
---

# Implement external tool publication validation

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/external-publication/** only. Implement complete external definition validation, exact-hash sample receipts and publication admission ports. No UI, preview lifecycle/routes, final factories or provider HTTP.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/external-publication/** only. Implement complete external definition validation, exact-hash sample receipts and publication admission ports. No UI, preview lifecycle/routes, final factories or provider HTTP.

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

- [x] Export section9 createExternalPublicationValidation with validateForPublication/validateSampleAndRecord/readReceipt and injected connection metadata, compiler/processor and receipt store ports.
- [x] Derive output wrapper/template schema; validate visual projection or code syntax/runtime and sample output before issuing receipt. No additional network call or guessed output schema.
- [x] Implement Redis receipt store/TTL/key hash and active tester checks; changed definition/sample outcomes never reuse stale success. Keep sample data/source out of receipt.
- [x] Provide real-validator sample->receipt->publication positive test plus stale/expired/unavailable and semantically invalid template tests.

## Interfaces / Contracts

C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies

- ARCH-020-SHARED-002
- ARCH-020-COMMERCE-003
- ARCH-020-COMMERCE-021
- ARCH-020-COMMERCE-025
- ARCH-020-COMMERCE-026

## Enables

- ARCH-020-COMMERCE-031
- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024

## Acceptance Criteria

- [x] PV01: saved external tool with valid sample receives exact definition/runtime receipt and passes full publication admission; both visual and code modes covered.
- [x] PV02: missing/expired/changed-hash/inactive-author receipt or Redis outage blocks; invalid schema/template/projection/syntax performs zero publication writes.
- [x] PV03: altered real response later fails same schema validation; published receipt is never treated as permission to skip runtime validation.

## Validation

Provide `test:arch020-external-publication` and scenario IDs from C21 section9. Start with the named positive path through the actual owned implementation. Add the specified rejection/race cases. Each report maps criterion -> test file/test name -> command -> observable result, not just a suite count. No claimed success based only on safe rejection or missing-config tests. Preserve each review reproduction as a committed regression alongside adjacent allowed/denied cases.

Use focused checks while implementing, then existing typecheck/build/lint where defined. Record unrun developer-owned PostgreSQL/container checks accurately; executable scenarios must still exist. No repeated unrelated full suites or screenshot quotas. No live credentials/WhatsApp delivery.

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

Review; Attempt 3 implementation committed and pushed for moda_architect review.

### Files Changed

- `moda-interact-commerce/src/commerce/external-publication/contracts.ts`
- `moda-interact-commerce/src/commerce/external-publication/index.ts`
- `moda-interact-commerce/src/commerce/external-publication/receipt-store.ts`
- `moda-interact-commerce/tests/external-publication.test.ts`
- `moda-interact-commerce/package.json`

### Work Completed

- Added typed `createExternalPublicationValidation` ports for saved-definition identity, connection metadata, compiler, visual/code processors, staff authorization, clock and digest injection.
- Implemented strict definition/sample bounds, visual and JavaScript sample processing, result-schema validation, semantic template validation, and no-network sample admission.
- Implemented Redis receipt storage with environment/revision/definition/runtime key binding, 24-hour TTL, bounded receipt fields, inactive-staff rejection and fail-closed unavailable handling.
- Added visual and code positive paths plus role/liveness, cross-author, MIME, strict receipt, expiry, write-outage, safe schema issue, list rendering and runtime revalidation regressions.
- Aligned saved-definition identity with the canonical `toolHashInput` content hash and removed credential existence from synthetic sample/publication admission; persisted connection scope/auth shape is still validated.

### Validation Results

| Criterion | Test / command | Observable result |
|---|---|---|
| PV01/PV02/PV03 | `tests/external-publication.test.ts` / 11 focused scenarios; `npm run test:arch020-external-publication` | Passed: visual/code admission, role and tester liveness, cross-author receipt, MIME/list rendering, strict receipt/expiry/write outage and runtime revalidation. |
| A2-R1 canonical hash | `tests/external-publication.test.ts` / `uses the canonical lifecycle hash and rejects the raw definition hash`; same command | Passed; canonical `toolHashInput` hash admits the sample/publication and raw definition hashing is rejected. |
| A2-R2 connection shape | `tests/external-publication.test.ts` / `validates persisted connection auth shape without requiring credentials`; same command | Passed; PLATFORM/PER_SHOP valid auth shapes pass without credential lookup, invalid scope/auth combinations reject. |
| Focused lint | `npx eslint src/commerce/external-publication/*.ts tests/external-publication.test.ts` | Passed with no warnings/errors. |
| Task-local diagnostics | VS Code diagnostics for all changed implementation/test files | No errors. |
| Repository lint | `npm run lint` | Blocked by pre-existing `src/studio/connections/connections-ui.tsx:235` hook error; no publication lint errors. |
| Repository typecheck/build | `npm run typecheck`; `npm run build` | Blocked by pre-existing Prisma/integration/CodeMirror/processor-test diagnostics; no publication diagnostics remain and the production bundle compiled before typecheck. |
| Diff check | `git diff --check` | Passed. |

Developer-owned PostgreSQL/container checks were not run; this task owns Redis receipt/admission ports and has no migration scope.

### Deviations

No scope deviation. The accepted Shared `validateDefinitionForPublication` helper is used for strict definition/template admission; provider HTTP, preview lifecycle, UI and final factories remain out of scope.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript are executed by the injected accepted processors. The saved-definition and connection ports are supplied by their owning lifecycle/credential implementations.

### Unresolved Issues

The full repository typecheck remains blocked by baseline Prisma generated-client and integration typing errors outside COMMERCE-030. Real Redis/PostgreSQL deployment checks remain developer-owned follow-up evidence.

### Architectural Concerns

Receipt creation is intentionally limited to successful sample processing and schema/template validation. Publication admission never treats a receipt as a substitute for fresh definition, compiler, schema or connection checks.

### Git / VCS

Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-030`; physical isolation confirmed by launcher. Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-030`.

Preparation packet: dependency gate passed for SHARED-002, COMMERCE-003, COMMERCE-021, COMMERCE-025 and COMMERCE-026; recursive database submodule sync/update passed at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`.

Implementation commit: `d15d3f5` (`fix(ARCH-020-COMMERCE-030): align hash and connection admission`), pushed to `origin task/ARCH-020-COMMERCE-030`.

## Architect Review

### Review Status

Changes Requested — Attempt 1.

### Review Notes

Reviewed by `moda_architect` against the exact submitted snapshot. The task records
implementation commit `59f0c34` (`feat(commerce): validate external publication
samples`).

The bounded C21 publication component exists and is directionally correct:
`createExternalPublicationValidation(...)` exposes the required three ports, the
definition/sample are parsed before processing, visual and JavaScript modes use the
accepted injected processors, successful output is checked against `resultSchema`,
the default digest is SHA-256, and the Redis store uses the required
environment/revision/definition/runtime key dimensions with a 24-hour default TTL.
The implementation also correctly keeps provider HTTP, credentials, preview lifecycle,
UI and final publication writes outside COMMERCE-030.

Attempt 1 is **not accepted** because four publication-safety gaps remain. They are
within the original C21/PV01–PV03 task scope. The corrections below are the complete
Attempt 1 rework contract; do not broaden the task beyond them.

#### A1-R1 — enforce sample-author / publisher roles and recheck the receipt author

**Source and focused-test changes required.**

C21 section 2.3 requires:

```text
successful sample receipt:
  written only by an authorized active staff author

publication admission:
  SUPER_ADMIN
  current publisher active
  matching receipt
  receipt tester still active

receipt from another active staff author:
  allowed

receipt from a deactivated tester:
  invalid
```

The current implementation does not satisfy this:

- `validateSampleAndRecord()` accepts an ADMIN/SUPER_ADMIN role without calling
  `staff.isActive(principal.id)`;
- `validateForPublication()` does not require `SUPER_ADMIN`;
- `readReceipt()` checks the requesting principal, not
  `receipt.testedByAdminId`;
- the current `active:false` test makes the publisher inactive and therefore does
  not prove the required cross-author tester-liveness behavior.

Keep the existing result union; do not invent a new authorization result code.

Implement these exact semantics:

```text
validateSampleAndRecord:
  principal.role must be ADMIN or SUPER_ADMIN
  staff.isActive(principal.id) must be true
  staff lookup throw/unavailable => VALIDATOR_UNAVAILABLE
  inactive/unauthorized => no processor call and no receipt write

validateForPublication:
  principal.role must be SUPER_ADMIN
  staff.isActive(principal.id) must be true
  staff lookup throw/unavailable => VALIDATOR_UNAVAILABLE

readReceipt:
  current requesting principal must be active
  receipt store read
  if found:
    staff.isActive(receipt.testedByAdminId) must be true
    false => treat receipt as missing/stale
    lookup throw => unavailable
```

The receipt may have `testedByAdminId !== publishingSuperAdmin.id`; that is the normal
cross-author case and must pass when both staff accounts remain active.

Focused regressions:

```text
ADMIN A active
  -> validateSampleAndRecord succeeds and writes receipt testedByAdminId=A

SUPER_ADMIN B active + A active
  -> validateForPublication succeeds using A's receipt

SUPER_ADMIN B active + A inactive
  -> publication rejected as missing/stale receipt
  -> no publication success

SUPER_ADMIN B inactive
  -> VALIDATOR_UNAVAILABLE

ADMIN A attempts validateForPublication
  -> rejected; no publication success

inactive ADMIN attempts validateSampleAndRecord
  -> no processor call
  -> no receipt write
```

No browser-supplied identity and no new role model.

#### A1-R2 — make receipt age/storage fail closed and exact

**Source and focused-test changes required.**

C21 makes the receipt a **24-hour** bounded Redis fact. The current Redis store
accepts an optional caller-supplied TTL, casts arbitrary JSON to `Receipt`, and the
validator does not independently reject an over-age `sampledAt`. In addition,
`receiptStore.write()` failures escape `validateSampleAndRecord()` as exceptions.

Use these exact rules:

```text
TTL:
  86_400 seconds exactly
  no caller override in createRedisReceiptStore

definitionHash/sampleHash/validatedOutputHash:
  lowercase SHA-256
  exactly 64 hex characters

runtimeVersion:
  visual.v1 | quickjs-sync.v1

environment:
  LOCAL | TEST | DEVELOPMENT | STAGING | PRODUCTION

sampledAt:
  valid UTC ISO timestamp
  sampledAt <= clock.now
  expired when clock.now - sampledAt >= 86_400_000 ms
```

Create one strict receipt parser for Redis/read-boundary data. It must accept only:

```text
environment
toolRevisionId
definitionHash
runtimeVersion
testedByAdminId
sampledAt
sampleHash
validatedOutputHash
```

and reject extra fields. Bound tool/admin IDs to nonblank <=128 characters.

`createRedisReceiptStore` behavior:

```text
write:
  receipt.environment must equal the store environment
  strict receipt validation before serialization
  key uses the store environment
  SET ... EX 86400

read:
  GET exact environment/revision/hash/runtime key
  null => missing
  malformed JSON / malformed receipt / wrong environment /
  wrong revision / wrong hash / wrong runtime => unavailable
  valid receipt => found
  Redis exception => unavailable
```

`readReceipt()` in the validator applies the 24-hour age check even if a custom
receipt store returns `found`; this prevents a non-Redis/test/store implementation
from extending receipt validity beyond C21.

`validateSampleAndRecord()` must catch receipt-write failure and return
`VALIDATOR_UNAVAILABLE`. It must never return `{ok:true}` after a failed receipt write.

Focused regressions:

```text
Redis SET
  -> EX 86400 exactly

caller cannot request a different TTL

write outage
  -> validateSampleAndRecord returns VALIDATOR_UNAVAILABLE
  -> no false success

read malformed JSON / extra rawBody field / wrong environment
  -> unavailable

receipt at 23h59m59s
  -> usable

receipt at exactly 24h
  -> expired/rejected

default digest path (do not inject constant digest)
  -> definitionHash/sampleHash/validatedOutputHash are lowercase 64-hex
  -> changed definition changes the definition hash/key
  -> changed sample changes sampleHash
  -> changed validated output changes validatedOutputHash
```

Receipt storage must still contain no source, sample body, processed output, provider
body or credential.

#### A1-R3 — validate sample MIME and reuse the real Commerce renderer/result boundary

**Source and focused-test changes required.**

C21 section 2.3 says sample mode comes from the saved definition and that sample
`contentType` is compared by normalized MIME (charset may be present). Attempt 1
never compares the sample MIME to `execution.responseFormat.mediaTypes`.

Normalize exactly:

```ts
const mime = sample.contentType
  .split(';', 1)[0]
  .trim()
  .toLowerCase();
```

and require `execution.responseFormat.mediaTypes.includes(mime)`. A mismatch is an
invalid sample and writes zero receipt.

The current local `renderTemplate()` duplicates production rendering and is not
equivalent. In particular, for:

```text
responseTemplate.kind = "items"
itemsPath = "values.items"
item = "{{item.name}}"
```

it ignores `itemsPath` and checks `item.name` against `{values}`, so a valid C21 list
sample cannot be admitted. It also does not exercise the production rendered-text
bound.

Delete the duplicate sample renderer and reuse the accepted Commerce rendering path.
After the processor returns:

1. validate the returned `values` with
   `compileSubset(execution.resultSchema, 'details')`;
2. use the **parsed** values to create the real external result data with
   `ExternalHttpResultDataSchema`:

```ts
{
  source: 'EXTERNAL_HTTP',
  connectionRevisionId: execution.connectionRevisionId,
  observedAt: new Date(now()).toISOString(),
  values: parsedValues,
}
```

3. construct the normal successful `CommerceToolResult`;
4. call the existing `renderDefinitionResult(...)` with external
   `maxSearchResults` capped at 20;
5. validate the rendered result with the existing `CommerceToolResultSchema`;
6. only after all five steps succeed may a receipt be written.

Do not copy renderer logic into `external-publication/**`.

Schema errors must satisfy the C21 error contract:

```text
path:
  JSON Pointer into processed output, rooted under /values
  e.g. /values/name or /values/items/0/price
  escape "~" => "~0", "/" => "~1"

message:
  expected type/rule only
  e.g. "Expected string"
       "Expected maxLength <= 100"
       "Unexpected field"

never:
  rejected raw value
  sample body
  source
  provider payload
  stack/host path
```

Use the Zod/subset issue metadata to produce a bounded safe rule message; do not echo
the rejected value.

`validatedOutputHash` must hash the schema-parsed values that were actually rendered,
not a pre-validation object.

Focused regressions:

```text
JSON definition allows application/json
sample contentType "text/plain"
  -> rejected before processor/receipt

sample contentType "application/json; charset=utf-8"
  -> normalized to application/json and allowed

valid LIST result:
  values = {items:[{name:"Moda"}]}
  template itemsPath = "values.items"
  item = "{{item.name}}"
  -> receipt recorded

rendered output exceeding the existing Commerce rendered-text bound
  -> no receipt

schema wrong type at name
  -> issue path /values/name
  -> message states expected string/rule
  -> raw rejected value absent
```

Keep the existing valid OBJECT/text and JavaScript positive controls.

#### A1-R4 — complete PV02/PV03 evidence and repository validation

**Focused tests / Completion Report changes required. Source changes only where the
new proofs expose a defect.**

PV02/PV03 are task Acceptance Criteria, not work that may be silently moved to a
later task.

Add committed regressions for:

```text
MISSING / STALE
- missing receipt -> "Run a sample test before publishing"
- changed current definition hash -> old receipt rejected
- expired receipt -> same bounded publication rejection
- receipt-store outage -> VALIDATOR_UNAVAILABLE

FRESH PUBLICATION CHECKS
- matching receipt exists but current connection is now disabled/missing credential
  -> publication rejected
- matching receipt exists but current JavaScript compiler now rejects source
  -> publication rejected
- invalid visual projection/template
  -> zero receipt write and publication rejection

PV03 RUNTIME REVALIDATION
- first record a valid sample receipt and obtain publication admission;
- then execute the same accepted EXTERNAL_HTTP definition through the already-owned
  `createExternalHttpExecutionPort` using controlled in-memory DNS/transport/
  connection/processor fixtures and a later processor output that violates
  `resultSchema`;
- assert the runtime result is bounded `ERROR/UNAVAILABLE` even though the
  publication receipt exists;
- the runtime execution path must not receive/read the publication receipt at all.

This is a focused integration regression only. Do not change COMMERCE-021 source and
do not make a live network call.

Also prove `validateForPublication()` performs **zero receipt writes**.

After the corrections run exactly:

```bash
npm run test:arch020-external-publication
npx eslint src/commerce/external-publication/*.ts tests/external-publication.test.ts
npm run lint
npm run typecheck
npm run build
git diff --check
```

If repository-wide lint/typecheck/build remain blocked solely by unchanged documented
baseline diagnostics outside:

```text
src/commerce/external-publication/**
tests/external-publication.test.ts
package.json
```

record the exact diagnostics and prove no task-owned diagnostic is present. Do not
repair unrelated Prisma/integration/UI code in COMMERCE-030.

Update Work Items, Acceptance Criteria and Validation checkboxes truthfully before
returning to Review. Record criterion -> exact committed test name -> command ->
observed result for PV01, PV02 and PV03.

### Reviewed Files

- `src/commerce/external-publication/contracts.ts`
- `src/commerce/external-publication/index.ts`
- `src/commerce/external-publication/receipt-store.ts`
- `tests/external-publication.test.ts`
- `src/commerce/execution/renderer.ts` (existing production renderer inspected; no
  modification authorized)
- `src/commerce/external-http/index.ts` (existing runtime schema-validation path
  inspected; no modification authorized)
- `package.json`
- C21 sections 2.3 and 9.5–9.6
- this task Completion Report

### Validation Reviewed

Submitted Attempt 1 evidence:

```text
npm run test:arch020-external-publication
  reported positive/rejection/receipt scenarios in Completion Report

npx eslint src/commerce/external-publication/*.ts tests/external-publication.test.ts
  PASS per Completion Report

task-local diagnostics
  PASS per Completion Report

npm run typecheck
  NON-ZERO — reported unrelated existing Prisma/integration diagnostics
```

The Completion Report does not record repository `npm run lint`, `npm run build` or
`git diff --check` for this attempt. Those checks are required on Attempt 2 as
specified above.

The uploaded archive contains no installed dependencies or Git remote metadata, so
dependency-backed commands and remote heads were not falsely claimed as independently
rerun from the review container. The functional defects above are established from
the submitted source and are independent of the repository-wide baseline.

### Architecture Conformance

Not yet conformant with C21 PV01–PV03.

The task remains correctly bounded to publication/sample validation and Redis receipt
storage, but acceptance is blocked by missing receipt-author liveness/role checks,
non-exact receipt expiry/storage behavior, sample MIME omission, duplicate/inaccurate
rendering logic, and incomplete PV02/PV03 evidence. No provider HTTP implementation,
credential service, UI, preview lifecycle, database schema, production publication
write, final factory or gateway work is authorized by this correction.

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
/moda-task ARCH-020-COMMERCE-030
```

must claim **Attempt 2 exactly once**.

The implementing agent must read this complete Architect Review before source
inspection, implement only A1-R1 through A1-R4, run the bounded validation above,
reconcile the Completion Report/checklists, set the task to review, clear the claim on
handoff, push both mirrored task branches and STOP.

Do not start COMMERCE-031, COMMERCE-024 or COMMERCE-012. They remain dependency-gated.

### Attempt 2 — Changes Requested (2026-09-22)

Reviewer: `moda_architect`.

**Changes Requested; Ready, Attempt 2 retained; executor/claimed_at remain null.
Not accepted.**

Reviewed the exact submitted Attempt 2 archive. The current remote parent task branch
resolves to `2f65bc460b8682d897017c68abeae14bc5dcd20c` (`docs(ARCH-020-COMMERCE-030):
submit attempt 2 for review`). The task records implementation commit `13463e5`
(`fix(ARCH-020-COMMERCE-030): tighten external publication validation`). The Commerce
implementation remote is not readable through the current review connector, so source
review is grounded in the exact submitted archive.

Attempt 2 materially closes the earlier receipt/liveness/rendering corrections and
those changes must be preserved:

- sample authors and publishers are role/liveness checked;
- a receipt from another active tester is allowed while a deactivated tester invalidates
  it;
- Redis receipt JSON is strictly bounded/validated with fixed 24-hour TTL;
- receipt-write failure fails closed;
- sample MIME is normalized/checked;
- successful output is schema-parsed, wrapped with `ExternalHttpResultDataSchema`,
  rendered through the production `renderDefinitionResult(...)` path and revalidated;
- schema failures expose bounded JSON-pointer/rule information without rejected values;
- valid LIST rendering is exercised;
- a later real external response is revalidated at runtime rather than trusting the
  publication receipt.

Submitted focused evidence reports **9/9 passed**, focused ESLint passed and
`git diff --check` passed. Repository-wide lint/typecheck/build remain blocked by
recorded unrelated baseline diagnostics and are not treated as task-owned regressions.

Two production-contract mismatches remain. These are the complete Attempt 2 correction
contract; do not broaden the task beyond them.

#### A2-R1 — use the canonical accepted tool-definition content hash

Files:
`src/commerce/external-publication/index.ts`,
`tests/external-publication.test.ts`.

The current saved-identity comparison still recomputes:

```ts
digest(canonicalJson(input.definition))
```

but the accepted ARCH-020 tool revision `contentHash` is produced by the existing
Commerce lifecycle/publication path as:

```ts
digest(canonicalJson(toolHashInput(definition)))
```

See the already accepted repository helper:

```ts
src/commerce/publication/validation.ts

export function toolContentHash(definition) {
  return digest(canonicalJson(toolHashInput(definition)));
}
```

Therefore a real persisted revision with the correct accepted `contentHash` can be
rejected by COMMERCE-030 even when its definition is byte-for-byte the same.

The current focused harness reproduces the same wrong raw-definition hash and therefore
cannot expose this mismatch.

Correction:

1. import `toolHashInput` from `@modainteract/moda-interact-shared/commerce`;
2. in the current-definition check compute exactly:

```ts
const expectedDefinitionHash =
  digest(canonicalJson(toolHashInput(input.definition)));
```

3. compare the saved `definitionHash` to that value;
4. use the persisted/canonical saved hash for the receipt key exactly as today;
5. do not introduce another hash shape and do not change the accepted lifecycle
   `toolContentHash(...)` contract.

Update the focused test helper so its saved revision hash and receipt hash are created
from `toolHashInput(definition)`, not raw `canonicalJson(definition)`.

Required focused proof:

```text
canonical lifecycle hash from toolHashInput(definition)
  -> sample succeeds
  -> receipt recorded
  -> publication admission succeeds

raw SHA256(canonicalJson(definition))
  -> is not accepted as the persisted canonical tool revision contentHash

change execution / responseProcessing / responseTemplate
  -> canonical definition hash changes
  -> old receipt cannot admit the changed definition
```

Use the real SHA-256 digest in these cases; do not mask identity behavior with a
constant digest.

#### A2-R2 — remove live credential existence from synthetic sample/publication admission

Files:
`src/commerce/external-publication/contracts.ts`,
`src/commerce/external-publication/index.ts`,
`tests/external-publication.test.ts`.

C21 states:

```text
Publication verifies known enabled revision/auth shape/result schema/template paths
without live HTTP.

PER_SHOP credentials need not exist for every shop at publish.
```

The current publication boundary still exposes:

```ts
type ConnectionMetadata = {
  enabled: boolean;
  revisionPresent: boolean;
  credentialAvailable: boolean;
};
```

and both sample and publication validation reject when
`credentialAvailable === false`.

That incorrectly makes a synthetic sample/publication dependent on current secret
provisioning and prevents legitimate PER_SHOP tools from being published before every
merchant configures a credential.

Replace the publication-only metadata contract with the persisted non-secret revision
shape:

```ts
type ConnectionMetadata = {
  enabled: boolean;
  revisionPresent: boolean;
  scope: 'PLATFORM' | 'PER_SHOP';
  authMode: 'NONE' | 'BEARER' | 'API_KEY';
  authHeader: string | null;
};
```

Use one local validation helper for both `validateSampleAndRecord()` and
`validateForPublication()`.

Required semantics:

```text
enabled !== true
  -> invalid

revisionPresent !== true
  -> invalid

PER_SHOP + NONE
  -> invalid

API_KEY
  -> authHeader must be a trimmed nonblank header name

BEARER
  -> authHeader must be null

NONE
  -> authHeader must be null

credential row exists / does not exist
  -> not queried
  -> not represented in this port
  -> not part of sample/publication admission
```

Do not add `shopId`, secret material, credential status, decrypt access or provider
HTTP to COMMERCE-030.

COMMERCE-024 will adapt the accepted connection/revision read facade into this
non-secret metadata port. Credential existence remains COMMERCE-028/032/live execution
ownership.

Required focused proof:

```text
PLATFORM + NONE, no credential concept
  -> sample/publication allowed when every other check passes

PER_SHOP + BEARER, no merchant credential
  -> sample/publication allowed

PER_SHOP + API_KEY + nonblank authHeader, no merchant credential
  -> sample/publication allowed

disabled or missing revision
  -> rejected

PER_SHOP + NONE
  -> rejected

API_KEY + null/blank authHeader
  -> rejected

BEARER/NONE + non-null authHeader
  -> rejected
```

The test harness must no longer contain `credentialAvailable`.

#### Attempt 3 validation and stop condition

Preserve all accepted Attempt 2 behavior and regressions. Do not rework receipt TTL,
staff liveness, MIME normalization, production rendering, schema diagnostics or runtime
revalidation unless one of these two changes directly requires a test-fixture update.

Run:

```bash
npm run test:arch020-external-publication

npx eslint \
  src/commerce/external-publication/*.ts \
  tests/external-publication.test.ts

npm run lint
npm run typecheck
npm run build
git diff --check
```

If repository-wide lint/typecheck/build remain non-zero solely on the documented
unchanged baseline outside the task-owned files, record the exact diagnostics and
demonstrate no `external-publication` diagnostic was introduced.

Before handoff:
1. update Work Items / Acceptance Criteria / Completion Report truthfully;
2. record exact focused test names/results for A2-R1 and A2-R2;
3. set `status: review`;
4. keep `attempt: 3` after the next normal claim;
5. clear `executor` and `claimed_at`;
6. push both task branches;
7. STOP.

Do not begin COMMERCE-031, COMMERCE-024 or COMMERCE-012.

### Review Status

Changes Requested.

### Reviewed Files

- `src/commerce/external-publication/contracts.ts`
- `src/commerce/external-publication/index.ts`
- `src/commerce/external-publication/receipt-store.ts`
- `tests/external-publication.test.ts`
- `src/commerce/publication/validation.ts` canonical `toolContentHash(...)`
- C21 publication/sample credential semantics
- Attempt 2 Completion Report

### Validation Reviewed

Submitted Attempt 2 evidence:

```text
npm run test:arch020-external-publication
  PASS — 9/9 focused scenarios

npx eslint src/commerce/external-publication/*.ts tests/external-publication.test.ts
  PASS

git diff --check
  PASS

repository lint/typecheck/build
  NON-ZERO only on documented unrelated baseline diagnostics per Completion Report
```

Static architect inspection confirms the receipt/liveness/MIME/renderer/runtime
revalidation corrections are present. A2-R1 and A2-R2 above remain independently
observable in the production source and focused harness.

### Architecture Conformance

Repository ownership remains correct and the publication validator is now close to
C21 conformance. Acceptance is blocked only by:
1. incompatibility with the accepted canonical tool revision content hash; and
2. incorrect coupling of synthetic sample/publication admission to credential
   existence.

No new architecture task or dependency is required.

### Follow-up

Return the same task through:

```text
/moda-task ARCH-020-COMMERCE-030
```

The next claim becomes **Attempt 3** exactly once. Dependants remain gated until
COMMERCE-030 is architect-accepted Complete.
