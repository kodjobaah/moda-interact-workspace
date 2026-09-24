---
id: ARCH-021-COMMERCE-026
architecture_id: ARCH-021
title: Simplify prompt-template authoring to current template content
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-021-DATABASE-002
  - ARCH-021-COMMERCE-008
  - ARCH-021-COMMERCE-013
  - ARCH-021-COMMERCE-015
enables:
  - ARCH-021-COMMERCE-028
created: 2026-09-24
updated: 2026-09-24
---

# Simplify prompt-template authoring to current template content

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`


## Objective

Remove prompt-template draft/publish/revision machinery while keeping first-class template categories, current template content, platform-admin authoring, audit, CAS, and copy-on-use into immutable Agent Prompt revisions.

## Context

Prompt templates are an authoring convenience. Runtime behavior requires an effective immutable Agent Prompt revision, not a template revision history. DATABASE-002 moves current template text onto `CommercePromptTemplate.promptText` and removes `CommercePromptTemplateRevision`.

## Scope

Primary files:

```text
src/commerce/agent-configuration/prompt-template-service.ts
src/studio/agent-configuration/template-contracts.ts
src/studio/agent-configuration/template-server-actions.ts
src/studio/agent-configuration/prompt-template-library.tsx
tests/agent-configuration-template.test.ts
```

## Out of Scope

- Removing `CommercePromptTemplateCategory`.
- Merchant editing of platform templates.
- Agent Prompt publish lifecycle.
- Agent Configuration model/prompt service changes owned by COMMERCE-025.
- Generic Studio composition changes.

## Requirements

### R1. Exact service surface

The template service must expose only:

```text
listCategories
createCategory
updateCategory
setCategoryEnabled
listTemplates
getTemplate
createTemplate
updateTemplate
setTemplateEnabled
```

Remove template methods equivalent to `listRevisions`, `createDraft`, `updateDraft`, `publishRevision`.

### R2. Exact template DTO

Template DTO includes:

```text
id
key
categoryId
displayName
description
promptText
enabled
editVersion
createdAt
updatedAt
```

No template revision DTO is returned.

### R3. Template CAS

`updateTemplate` updates metadata and/or `promptText` using `expectedEditVersion` and increments `editVersion` exactly once.

Category CAS remains `expectedEditVersion` on the category row.

### R4. Explicit errors and lightweight reconciliation

Use the same result/error rules as COMMERCE-025:

```text
no kind:'unknown'
no payloadHash
no stored result replay
DATABASE_UNAVAILABLE remains explicit
operationId is audit/reconciliation correlation only
```

Template mutations write `CommerceAuditEvent.operationId` atomically.

### R5. Copy-on-use behavior

Remove all UI/service references to `sourceTemplateRevisionId`.

The Agent Prompt service in COMMERCE-025 owns copying `CommercePromptTemplate.promptText` into a new prompt DRAFT and storing `sourceTemplateId`.

Changing template text after copying must never mutate existing Agent Prompt revisions.

### R6. UI exact behavior

`PromptTemplateLibrary` must show categories and current templates grouped by category.

For a selected template, show/edit:

```text
display name
description
current prompt text
enabled state
editVersion-backed save
```

Remove:

```text
revision history
Save draft
Update draft
Publish revision
published revision hash/status copy
```

Keep category create/update/enable/disable and multiple templates per category.

## Work Items

- [x] Replace revision service API with R1 surface.
- [x] Replace template contracts/DTOs with R2.
- [x] Implement direct CAS update of promptText.
- [x] Remove template revision UI/history.
- [x] Update audit/reconciliation behavior and structured failure logging.
- [x] Update focused tests.

## Interfaces / Contracts

Consumes `CommercePromptTemplateCategory`, `CommercePromptTemplate.promptText`, and `CommerceAuditEvent.operationId`.

## Dependencies

- ARCH-021-DATABASE-002
- ARCH-021-COMMERCE-008
- ARCH-021-COMMERCE-013
- ARCH-021-COMMERCE-015

## Enables

- ARCH-021-COMMERCE-028

## Acceptance Criteria

- [x] Categories remain first-class and data-driven.
- [x] Multiple templates may exist in one category.
- [x] Template content is edited directly with CAS.
- [x] No template revision persistence/service/UI remains.
- [x] Existing Agent Prompt revisions remain unaffected by later template edits.
- [x] Errors are explicit and reconcilable; none are swallowed into `unknown`, and every caught infrastructure/unexpected failure translated into an error result is emitted through the approved shared structured logger with the original `Error` object.

## Validation

- [x] focused template service tests
- [x] focused template UI tests
- [x] stale CAS test
- [x] DB-unavailable error test
- [x] operation reconciliation test
- [x] structured error logging regression
- [x] targeted ESLint/typecheck
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.


## Implementation Notes

Do not remove categories and do not move templates into a JSON blob. The simplification removes template revision lifecycle only.

## Completion Report

### Status

Ready for architect review after Attempt 3.

### Attempt 3 Workflow Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-026`, `task/ARCH-021-COMMERCE-026`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-026`, `task/ARCH-021-COMMERCE-026`.
- Shared workspace checkout switched or mutated: no. Another task worktree reused: no.
- Start-of-attempt parent HEAD: `5a9d497cee29dd9f1573e41636da6303d4252fd3`; implementation HEAD: `9473b6006dbf008a5b0a04b124076804fcd4c420`.
- Parent and implementation task-branch synchronization: remote fast-forward `not-needed`; `origin/main` incorporation `already-current`.
- Recursive submodule sync/update passed; database submodule: `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Attempt 3 launcher claim commit: `1a8ee4ed026889d56818bd81d433e14c5e432847`.
- Published implementation commit: `f76939275ae185794b9b025cfb5da8fc49abc2a4`, pushed to `origin/task/ARCH-021-COMMERCE-026`.

### Files Changed

`moda-interact-commerce`: template contracts/service/actions/UI, platform template copy-on-use wiring, and focused template/platform tests. Production Studio composition was not broadened because its function-valued service props are owned by COMMERCE-029.

Attempt 3 changed `src/commerce/agent-configuration/prompt-template-service.ts`, `tests/agent-configuration-templates.test.ts`, and `tests/agent-configuration-templates-postgres.test.ts`.

### Work Completed

Removed template revision lifecycle and DTOs; direct `promptText` authoring now uses edit-version CAS. Audit operations use `CommerceAuditEvent.operationId` for correlation only, with independent audit IDs, explicit committed-operation/CAS/database/internal error semantics, and bounded structured logging. Enabled-state changes use the explicit CAS operation and cannot discard dirty prompt/metadata edits. Agent Prompt copy-on-use reads current template content and preserves immutable prompt revisions; the task-owned picker no longer requests or displays `sourceTemplateRevisionId`.

Attempt 3 corrected the stale PostgreSQL CAS assertion, classifies Prisma codes from structured error objects, reconciles CAS/P2002 losers exactly once after rollback, and logs translated mutation/reconciliation failures through the shared logger with raw errors and bounded operation IDs.


### Validation Results

Focused Vitest: 5 files passed, 19 tests passed. Targeted service regressions: 7 tests passed.

Disposable PostgreSQL proof used database `commerce026_attempt3_1790254377` in the isolated local `moda-arch021-postgres` container. After `prisma db push` and client generation, `COMMERCE_PROMPT_TEMPLATE_POSTGRES=1 DATABASE_URL=... npm exec vitest run tests/agent-configuration-templates-postgres.test.ts` passed all 3 tests: same-operation create, same-operation CAS, and different-operation stale CAS. No PostgreSQL test was skipped in the explicit proof.

Targeted ESLint passed with no warnings, and `git diff --check` passed. Full `npm run typecheck -- --pretty false` exits 2 with no diagnostics in `prompt-template-service.ts`, `agent-configuration-templates.test.ts`, or `agent-configuration-templates-postgres.test.ts`. Residual diagnostics are confined to `app/api/studio/code-response/validate/route.ts` (missing preview modules), `components/studio-workspace.tsx` (duplicate prop and StudioFailure shape), `src/commerce/agent-configuration/effective-configuration.ts` and `model-service.ts` (generated Prisma model surfaces), `src/commerce/agent-configuration/prompt-service.ts` (COMMERCE-025 prompt lifecycle/generated Prisma contract), `tests/agent-configuration-model-postgres.test.ts` and `tests/agent-configuration-prompts-postgres.test.ts` (sibling generated Prisma surfaces), `tests/c20-integration-fixture.test.ts`, `tests/connections-production.test.ts`, `tests/external-tools-ui.test.tsx`, `tests/external-wiring.test.ts`, and `tests/local-external-mcp-diagnostic.test.ts` (existing integration/tooling baselines).

### Deviations

The platform prompt picker was updated only at its template-consumer boundary so it can copy current `promptText`; Agent Prompt revision lifecycle and legacy prompt-service/contract references remain owned by COMMERCE-025 and were not modified by C026. The PostgreSQL proof used a fresh database inside the existing disposable local container; no shared development, staging, or production database was used.

### Assumptions

No additional assumptions.

### Unresolved Issues

Full repository typecheck remains blocked by the explicitly listed sibling/baseline diagnostics; task-owned files are clean. No task-owned unresolved implementation issues remain.

### Architectural Concerns

None beyond the listed repository-wide baseline/sibling typecheck failures.

## Architect Review

### Review Status

Accepted — Attempt 3

### Review Notes

#### Attempt 3 — Accepted — 2026-09-24

Reviewed implementation `f76939275ae185794b9b025cfb5da8fc49abc2a4`
and parent report `1c0d0c0e` against the complete Attempt 2 correction contract.

Attempt 3 is accepted.

The implementation now classifies Prisma `P2002` from the structured Prisma error
object rather than parsing `error.message`. Domain errors created by the
prompt-template service retain their explicit service-owned code parsing.

CAS and `P2002` losers are reconciled exactly once after the failed transaction has
rolled back by querying `CommerceAuditEvent.operationId`. A committed same-operation
receipt returns `OPERATION_ALREADY_COMMITTED`; a genuine different-operation stale
CAS returns `CAS_CONFLICT`; a `P2002` with no matching receipt fails closed as
`INTERNAL_ERROR`. Reconciliation lookup failure is itself classified and returned as
`DATABASE_UNAVAILABLE` or `INTERNAL_ERROR`; it is never treated as a fabricated
missing receipt.

Translated infrastructure/unexpected failures use the approved shared logger from
`@modainteract/moda-interact-shared/logging`. The service preserves the constructor
logger-injection seam and passes the original raw `Error` object to
`commerce.prompt_template.mutation_failed` or
`commerce.prompt_template.reconciliation_lookup_failed`. The logged operation id is
bounded to 128 characters. No service-local logger, `console.error`, payload hash,
stored result replay, generic `unknown` result, second audit table or advisory-lock
mechanism was introduced.

The PostgreSQL stale-CAS regression uses the current explicit result contract
(`kind: 'error'`, `code: 'CAS_CONFLICT'`). The submitted isolated disposable
PostgreSQL proof executed all three required concurrency scenarios: same-operation
create, same-operation CAS and different-operation stale CAS; all 3/3 passed.

The submitted focused packet reports 19 tests passed. Targeted ESLint and
`git diff --check` passed. Inspection of the submitted `tsconfig.tsbuildinfo`
confirms zero semantic diagnostics in the COMMERCE-026-owned service/contracts/UI and
Attempt 3 test files. The remaining diagnostics are confined to the exact sibling /
baseline files listed in the Completion Report.

The Completion Report records the canonical parent and implementation task worktrees,
matching task branches, start-of-attempt synchronization, Attempt 3 launcher claim,
recursive submodule materialization, database submodule commit, implementation
commit and isolated PostgreSQL evidence. Both branches were reported clean and
synchronized.

The supplied review archive does not contain `node_modules`, so Vitest, ESLint and
typecheck were not independently rerun by the architect. Static source inspection,
the focused tests, the executed PostgreSQL evidence and the submitted TypeScript
diagnostic artifact provide sufficient acceptance evidence.

#### Historical Attempt 2 Changes Requested

Attempt 2 is substantially improved and satisfies most of the Attempt 1 correction contract: current template content is edited directly with CAS, audit rows now use the canonical `CommerceAuditEvent.operationId` correlation column with independent audit IDs, the template result contract is explicit rather than `unknown`/replay-based, enabled-state changes use the dedicated CAS action without discarding dirty edits, task-owned `sourceTemplateRevisionId` UI provenance is removed, and the Completion Report now contains the required prepared-worktree/commit evidence.

Attempt 3 is deliberately narrow. Execute the following correction contract exactly; do not redesign the template service or introduce another reconciliation abstraction.

1. **Fix the stale PostgreSQL regression contract.** In `tests/agent-configuration-templates-postgres.test.ts`, replace the removed `result.kind === 'conflict'` expectation with the explicit result shape `result.kind === 'error' && result.code === 'CAS_CONFLICT'`. The submitted `tsconfig.tsbuildinfo` records TS2367 on this stale assertion, so this exact diagnostic must disappear before review.

2. **Read Prisma error codes from the Prisma error object, never from `error.message`.** In `src/commerce/agent-configuration/prompt-template-service.ts`, add or use one bounded helper with this behaviour:

   ```ts
   function prismaErrorCode(error: unknown): string | undefined {
     if (typeof error !== 'object' || error === null || !('code' in error)) return undefined;
     const code = (error as { code?: unknown }).code;
     return typeof code === 'string' ? code : undefined;
   }
   ```

   Do not use `error.message.split(':')` to recognize Prisma `P2002`. The existing domain failures created by `fail('CAS_CONFLICT', ...)`, `fail('INVALID_INPUT', ...)`, and `fail('NOT_FOUND', ...)` may continue to use their explicit domain-code parsing because those are service-owned errors, not Prisma errors.

3. **Reconcile a same-operation loser in one deterministic place after the failed transaction.** A unique collision or CAS miss may mean another request with the same `operationId` committed while this transaction was waiting. After the transaction has rolled back, query `CommerceAuditEvent` by `operationId` exactly once for that reconciliation decision. The required outcome order is:

   ```text
   transaction succeeds
       -> ok

   transaction fails with CAS_CONFLICT
       -> query CommerceAuditEvent.operationId
       -> receipt exists     -> OPERATION_ALREADY_COMMITTED
       -> no receipt         -> CAS_CONFLICT
       -> receipt query fails -> classify/log the receipt-query failure; never pretend no receipt exists

   transaction fails with Prisma P2002
       -> query CommerceAuditEvent.operationId
       -> receipt exists     -> OPERATION_ALREADY_COMMITTED
       -> no receipt         -> INTERNAL_ERROR
       -> receipt query fails -> classify/log the receipt-query failure; never pretend no receipt exists
   ```

   Do not add payload hashes, stored result replay, `kind: 'unknown'`, advisory locks, queues, or a second audit table.

4. **Do not swallow exceptions. Use the existing shared structured logger and pass the actual `Error` object.** Before editing, read `docs/observability/shared-logging.md`. The approved API is already available and already imported by this service:

   ```ts
   import {
     createLogger,
     type StructuredLogger,
   } from '@modainteract/moda-interact-shared/logging';
   ```

   Keep the existing constructor injection seam so tests can supply a logger:

   ```ts
   private readonly logger: StructuredLogger;

   constructor(private readonly db: PrismaClient, logger?: StructuredLogger) {
     this.logger = logger ?? createLogger({
       serviceName: 'moda-interact-commerce',
       environment: process.env.NODE_ENV ?? 'development',
     });
   }
   ```

   Do **not** add `console.error`, a service-local JSON logger, or custom Error serialization. The shared logger already provides JSON serialization, redaction, bounded values, `Error` serialization, and sink-failure isolation.

   When an infrastructure/unexpected exception is converted into `DATABASE_UNAVAILABLE` or `INTERNAL_ERROR`, emit exactly one mutation failure record before returning the result:

   ```ts
   this.logger.error('commerce.prompt_template.mutation_failed', {
     action,
     operationId: input.operationId.slice(0, 128),
     resultCode: 'DATABASE_UNAVAILABLE', // or 'INTERNAL_ERROR'
     prismaCode: prismaErrorCode(error),
     error,
   });
   ```

   Pass `error` as the raw field. **Do not** pass only `error.message`, stringify the error, or construct `{ name, message }` locally. The shared logger serializes an `Error` to bounded `name` and `message` and omits stack by default. Do not log `promptText`, template contents, request bodies, credentials, authorization headers, email addresses, or other customer/provider payloads. `operationId` must remain bounded to 128 characters.

   If the post-rollback reconciliation lookup itself throws, that exception must also be visible. Do not use `.catch(() => null)` or any equivalent silent fallback. Emit:

   ```ts
   this.logger.error('commerce.prompt_template.reconciliation_lookup_failed', {
     action,
     operationId: input.operationId.slice(0, 128),
     triggerPrismaCode: prismaErrorCode(triggerError),
     triggerError,
     error: reconciliationError,
   });
   ```

   Then return `DATABASE_UNAVAILABLE` when `reconciliationError` satisfies `isDatabaseUnavailable(...)`; otherwise return `INTERNAL_ERROR`. Do not fall through to `CAS_CONFLICT`, `OPERATION_ALREADY_COMMITTED`, or a fabricated "no receipt" result when the receipt lookup itself failed.

   Expected domain outcomes (`FORBIDDEN`, `INVALID_INPUT`, `NOT_FOUND`, a genuine `CAS_CONFLICT`, and a successfully detected `OPERATION_ALREADY_COMMITTED`) are already explicit results and do not need to be emitted as `error` logs merely to satisfy this correction. The no-swallow rule applies to caught infrastructure/unexpected exceptions that would otherwise disappear behind a translated result.

5. **Add deterministic logging regressions.** Use the shared logger rather than mocking `console`. A valid test pattern is:

   ```ts
   const records: LogRecord[] = [];
   const logger = createLogger({
     serviceName: 'moda-interact-commerce',
     environment: 'test',
     sink: (record) => records.push(record),
   });
   const service = new PromptTemplateService(db, logger);
   ```

   Add focused assertions proving:
   - an unexpected mutation exception returns `INTERNAL_ERROR` and emits `commerce.prompt_template.mutation_failed`;
   - a database-unavailable exception returns `DATABASE_UNAVAILABLE` and emits the same event with `resultCode: 'DATABASE_UNAVAILABLE'`;
   - the emitted record contains the bounded `operationId` and serialized `data.error.name` / `data.error.message`;
   - a reconciliation lookup failure emits `commerce.prompt_template.reconciliation_lookup_failed` and is not silently converted into "receipt missing";
   - the tests do not require or assert stack traces.

6. **Run the required PostgreSQL concurrency proof instead of skipping it.** Use an explicitly isolated/disposable PostgreSQL database only. Do not point this test at a shared development, staging, or production database. From `moda-interact-commerce`, run:

   ```bash
   COMMERCE_PROMPT_TEMPLATE_POSTGRES=1 \
   DATABASE_URL='<isolated-disposable-postgres-url>' \
   npm exec vitest run tests/agent-configuration-templates-postgres.test.ts
   ```

   All three PostgreSQL tests must execute and pass: same-operation create, same-operation CAS, and different-operation stale CAS. If an isolated PostgreSQL target is unavailable, leave the operation-reconciliation validation unchecked, set the task to `blocked`, document exactly what is unavailable, and STOP. Do not mark the PostgreSQL suite passed when Vitest reports it skipped.

7. **Run the bounded Attempt 3 validation in this order.**

   ```bash
   npm exec vitest run \
     tests/agent-configuration-templates.test.ts \
     tests/agent-configuration-template-server-actions.test.ts \
     tests/agent-configuration-template-ui.test.tsx \
     tests/agent-configuration-platform-prompt-ui.test.tsx \
     tests/agent-configuration-production.test.tsx

   COMMERCE_PROMPT_TEMPLATE_POSTGRES=1 \
   DATABASE_URL='<isolated-disposable-postgres-url>' \
   npm exec vitest run tests/agent-configuration-templates-postgres.test.ts

   npm exec eslint \
     src/commerce/agent-configuration/prompt-template-service.ts \
     tests/agent-configuration-templates.test.ts \
     tests/agent-configuration-templates-postgres.test.ts

   npm run typecheck -- --pretty false
   git diff --check
   ```

   The full typecheck may retain already-documented sibling/baseline diagnostics, but **zero diagnostics may remain in `prompt-template-service.ts`, `agent-configuration-templates.test.ts`, or `agent-configuration-templates-postgres.test.ts`**. Record the exact residual diagnostics and owners in the Completion Report rather than describing them generically.

8. **Stop condition.** Once the source changes and all required validation above are complete, update the task checklist and Completion Report, set `status: review`, clear `executor`/`claimed_at` as required by the handoff path, push the implementation and parent report commits, return control to `moda_architect`, and STOP. Do not start COMMERCE-028 or modify COMMERCE-025/027/029.

### Reviewed Files

- `src/commerce/agent-configuration/prompt-template-service.ts`
- `src/studio/agent-configuration/template-contracts.ts`
- `src/studio/agent-configuration/template-server-actions.ts`
- `src/studio/agent-configuration/prompt-template-library.tsx`
- `src/studio/agent-configuration/platform-prompt-configuration.tsx`
- `tests/agent-configuration-templates.test.ts`
- `tests/agent-configuration-templates-postgres.test.ts`
- `tests/agent-configuration-template-server-actions.test.ts`
- `tests/agent-configuration-template-ui.test.tsx`
- `tests/agent-configuration-platform-prompt-ui.test.tsx`
- `tests/agent-configuration-production.test.tsx`
- submitted `tsconfig.tsbuildinfo`
- Attempt 3 Completion Report

### Validation Reviewed

- Submitted focused validation: 5 files / 19 tests passed.
- Submitted targeted service regressions: 7 tests passed.
- Submitted isolated disposable PostgreSQL proof: 3/3 tests executed and passed.
- Submitted targeted ESLint: passed with no warnings.
- Submitted `git diff --check`: passed.
- Submitted full typecheck: non-zero only on the exact sibling/baseline files recorded
  in the Completion Report.
- Independent inspection of `tsconfig.tsbuildinfo`: zero semantic diagnostics in
  COMMERCE-026-owned prompt-template files and Attempt 3 test files.
- Independent source inspection confirms structured Prisma-code classification,
  post-rollback reconciliation, shared-logger raw-Error usage and no silent
  reconciliation fallback.

### Architecture Conformance

Conforms. Prompt templates retain first-class categories and current mutable
`promptText` with edit-version CAS while template revision lifecycle remains removed.
Audit correlation uses `CommerceAuditEvent.operationId`; no result replay/payload hash
or generic `unknown` mutation result is reintroduced. Error translation remains
explicit and observable through the approved shared structured logger. Copy-on-use
continues to isolate existing immutable Agent Prompt revisions from later template
edits. COMMERCE-025 remains the owner of the remaining Agent Prompt service/schema
migration and COMMERCE-028 remains the owner of the later consolidated UI /
reconciliation layer.

### Follow-up

`ARCH-021-COMMERCE-026` is architect-accepted Complete at Attempt 3.

`ARCH-021-COMMERCE-028` remains Pending because `ARCH-021-COMMERCE-025` and
`ARCH-021-COMMERCE-027` are still Ready rather than Complete. This acceptance does
not start either task and does not start COMMERCE-028.
