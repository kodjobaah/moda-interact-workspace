---
id: ARCH-006-BACKGROUND-009
architecture_id: ARCH-006
title: Correct PostgreSQL enum parameter bindings in translation lifecycle
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: review
priority: 85
executor: copilot
claimed_at: 2026-09-07T09:45:26Z
attempt: 1
depends_on:
  - ARCH-006-BACKGROUND-005
  - ARCH-006-BACKGROUND-006
  - ARCH-006-BACKGROUND-007
  - ARCH-006-BACKGROUND-008
enables: []
created: 2026-09-07
updated: 2026-09-07T10:49:00Z
---

# ARCH-006-BACKGROUND-009: Correct PostgreSQL enum parameter bindings in translation lifecycle

## Architecture

Canonical: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Detailed translation reliability: `docs/architecture/ARCH-006-translation-batching-reliability.md`

This corrective task was created from live manual validation after the accepted
ARCH-006 translation implementation reached the real PostgreSQL runtime.

## Objective

Make every remaining **dynamic Prisma-bound value** written by the Background
translation lifecycle into a PostgreSQL enum column explicitly use the correct
schema-qualified enum cast, and prove those writes against the real migrated
PostgreSQL schema.

## Context

Manual integrated validation of an Admin-requested translation reached the Background
worker and failed in:

```text
TranslationBatchSubmitService.persistFailure()
```

with PostgreSQL SQLSTATE `42804`:

```text
column "status" is of type support."MerchantTranslationBatchStatus"
but expression is of type text
```

The current code computes a JavaScript status value:

```ts
const nextStatus =
  classification === "AMBIGUOUS_CREATE"
    ? "SUBMISSION_UNKNOWN"
    : ...
      ? "FAILED"
      : "READY";
```

and writes it through:

```ts
"status" = ${nextStatus}
```

`Prisma.sql` binds `${nextStatus}` as PostgreSQL `text`. PostgreSQL does not
implicitly coerce a prepared/bound `text` parameter to the enum column type.

The database schema is authoritative:

```prisma
enum MerchantMessageTranslationStatus {
  PENDING
  AVAILABLE
  FAILED

  @@schema("support")
}

enum MerchantTranslationBatchStatus {
  READY
  SUBMITTING
  SUBMISSION_UNKNOWN
  SUBMITTED
  PROVIDER_COMPLETED
  COMPLETED
  FAILED
  EXPIRED
  CANCELLED

  @@schema("support")
}
```

Architect inspection of the **current attached Background source** found exactly five
remaining dynamic bound enum writes in the translation lifecycle:

```text
1. translation-batch-submit.service.ts
   MerchantTranslationBatch.status
   ${nextStatus}

2. translation-batch-poll.service.ts
   MerchantTranslationBatch.status
   ${providerStatus.toUpperCase()}

3. translation-batch-poll.service.ts
   MerchantMessageTranslation.status
   ${shouldRetry ? "PENDING" : "FAILED"}

4. translation-batch-results.service.ts
   MerchantMessageTranslation.status
   ${retry ? "PENDING" : "FAILED"}

5. translation-reconciliation.service.ts
   MerchantTranslationBatch.status
   ${completed ? "PROVIDER_COMPLETED" : "SUBMITTED"}
```

The task corrects this one demonstrated SQL-typing defect class across the complete
Background translation lifecycle so the developer does not discover the same `42804`
one stage at a time.

The current SQL **literal** enum writes such as:

```sql
'READY'
'SUBMITTING'
'SUBMITTED'
'PROVIDER_COMPLETED'
'COMPLETED'
'FAILED'
'PENDING'
'PROCESSING'
```

are not the demonstrated problem. PostgreSQL can contextually type SQL literals from
the destination enum column. Do not mechanically rewrite them.

The error happened in `persistFailure()`, which means a provider/preparation/create
operation had already failed. The enum error can therefore mask the original upstream
translation/provider failure. Once this task is corrected, the original failure may
become visible and should be reported as runtime evidence rather than hidden by a
secondary persistence error.

## Scope

Correct exactly the five dynamic enum-bound writes listed in Context.

Add focused generated-`Prisma.Sql` regressions for all five writes.

Add one disposable PostgreSQL integration regression that executes the affected
service paths against the real migrated ARCH-006 database schema using the accepted
BACKGROUND-008 integration harness.

## Out of Scope

- Database schema or migration changes.
- New enum values.
- Shared contract changes.
- Queue payload/job-ID changes.
- Provider API changes.
- Retry-policy changes.
- New failure classifications.
- Translation batching redesign.
- Reconciliation redesign.
- Admin or Shopify changes.
- Gateway/deployment changes.
- System-test execution.
- Converting all raw SQL to Prisma Client model operations.
- Mechanically casting enum values that are already SQL literals.
- Fixing any upstream provider failure revealed after the enum persistence bug is
  removed unless that failure is proven to be task-owned by these exact edits.

## Requirements

### 1. Submission failure Batch status

In `src/services/translation-batch-submit.service.ts`, preserve the existing
`nextStatus` calculation and retry semantics.

Current invalid form:

```ts
"status" = ${nextStatus},
```

Required form:

```ts
"status" = CAST(
  ${nextStatus}
  AS "support"."MerchantTranslationBatchStatus"
),
```

The value must remain a Prisma-bound parameter.

Do not change:

```text
AMBIGUOUS_CREATE -> SUBMISSION_UNKNOWN
terminal/attempt-exhausted -> FAILED
retryable -> READY
```

Do not change `nextSubmitAt`, `failureCode`, attempt counting, create semantics or
the `SUBMITTING` compare-and-set predicate.

### 2. Poll terminal Batch status

In `src/services/translation-batch-poll.service.ts`, preserve the provider terminal
status mapping:

```ts
providerStatus.toUpperCase()
```

for the normalized provider statuses:

```text
failed    -> FAILED
expired   -> EXPIRED
cancelled -> CANCELLED
```

Current invalid form:

```ts
"status" = ${providerStatus.toUpperCase()},
```

Required form:

```ts
"status" = CAST(
  ${providerStatus.toUpperCase()}
  AS "support"."MerchantTranslationBatchStatus"
),
```

Do not replace the normalized provider-status model or introduce a second mapping
table merely for this correction.

### 3. Poll terminal translation status

In the same poll service, preserve:

```ts
const shouldRetry =
  retryable && item.retryCount < configuredMaxAutoRetries();
```

Current invalid form:

```ts
"status" = ${shouldRetry ? "PENDING" : "FAILED"},
```

Required form:

```ts
"status" = CAST(
  ${shouldRetry ? "PENDING" : "FAILED"}
  AS "support"."MerchantMessageTranslationStatus"
),
```

Do not change retry count, retry delay, current-Batch clearing, message failure
promotion or ownership/CAS predicates.

### 4. Provider result translation status

In `src/services/translation-batch-results.service.ts`, preserve the existing result
retry decision:

```ts
const retry =
  retryable && record.retryCount < maxAutoRetries();
```

Current invalid form:

```ts
"status" = ${retry ? "PENDING" : "FAILED"},
```

Required form:

```ts
"status" = CAST(
  ${retry ? "PENDING" : "FAILED"}
  AS "support"."MerchantMessageTranslationStatus"
),
```

Do not change successful `AVAILABLE` handling, result membership validation,
idempotency/CAS predicates, message availability transition or Batch completion.

### 5. SUBMISSION_UNKNOWN reconciliation Batch status

In `src/services/translation-reconciliation.service.ts`, preserve:

```ts
const completed = correlation.batch.status === "completed";
```

Current invalid form:

```ts
"status" = ${completed ? "PROVIDER_COMPLETED" : "SUBMITTED"},
```

Required form:

```ts
"status" = CAST(
  ${completed ? "PROVIDER_COMPLETED" : "SUBMITTED"}
  AS "support"."MerchantTranslationBatchStatus"
),
```

Do not change provider correlation lookup, conflict handling, no-match behavior,
adoption semantics, poll/results restoration or the `SUBMISSION_UNKNOWN` CAS
predicate.

### Bound-parameter invariant

For all five corrections:

```text
JavaScript value
    ↓
Prisma bound parameter
    ↓
CAST(parameter AS schema-qualified PostgreSQL enum)
    ↓
enum column
```

Never use:

```text
Prisma.raw(dynamicValue)
string concatenation
template-built SQL enum literals
unsafe interpolation
```

to avoid the cast.

### Complete current-service audit

Before returning to review, re-run a source search over `src/services` for dynamic
bound writes to enum-backed `status`/`direction`/`scope`/`kind` columns.

If another **dynamic bound JavaScript value** is found writing into a PostgreSQL enum
column in the ARCH-006 translation lifecycle, do not silently broaden scope. Record
the exact file/query/schema evidence in the Completion Report and return the task
`blocked` to `moda_architect`.

Do not treat ordinary IDs, dates, strings, booleans or numeric parameters as enum
defects.

## Work Items

- [x] Add `MerchantTranslationBatchStatus` cast to submission failure persistence.
- [x] Add `MerchantTranslationBatchStatus` cast to terminal poll Batch persistence.
- [x] Add `MerchantMessageTranslationStatus` cast to terminal poll item persistence.
- [x] Add `MerchantMessageTranslationStatus` cast to failed provider-result
      persistence.
- [x] Add `MerchantTranslationBatchStatus` cast to unknown-Batch correlation
      adoption.
- [x] Add generated-`Prisma.Sql` unit regressions for all five dynamic bindings.
- [x] Add disposable PostgreSQL integration coverage for the affected service paths.
- [x] Run the complete current-service dynamic-enum audit and record the result.
- [x] Run required repository validation and return only this task to `review`.

## Interfaces / Contracts

No cross-repository contract changes.

Database enum types remain:

```text
"support"."MerchantTranslationBatchStatus"
"support"."MerchantMessageTranslationStatus"
```

The durable state machine remains exactly the one accepted by DATABASE-002 and
BACKGROUND-005/006/007.

No queue schema/version or Shared package export changes.

## Dependencies

All YAML dependencies are already architect-accepted Complete:

```text
ARCH-006-BACKGROUND-005
ARCH-006-BACKGROUND-006
ARCH-006-BACKGROUND-007
ARCH-006-BACKGROUND-008
```

BACKGROUND-008 supplies the accepted disposable PostgreSQL/Redis integration harness.

This is a corrective implementation task. It must not depend on a system-test task.

## Enables

No non-system-test implementation task.

Architect coordination rule: ARCH-006 terminal system tests must not be invoked until
this corrective task is architect-accepted Complete. They remain deliberately
manual-gated by the developer.

## Acceptance Criteria

- [x] `persistFailure()` writes bound `READY`, `FAILED` and `SUBMISSION_UNKNOWN`
      through `"support"."MerchantTranslationBatchStatus"`.
- [x] Terminal poll Batch status writes bound `FAILED`/`EXPIRED`/`CANCELLED`
      through `"support"."MerchantTranslationBatchStatus"`.
- [x] Terminal poll translation retry/failure writes bound `PENDING`/`FAILED`
      through `"support"."MerchantMessageTranslationStatus"`.
- [x] Failed provider-result retry/failure writes bound `PENDING`/`FAILED`
      through `"support"."MerchantMessageTranslationStatus"`.
- [x] SUBMISSION_UNKNOWN correlation adoption writes bound
      `PROVIDER_COMPLETED`/`SUBMITTED` through
      `"support"."MerchantTranslationBatchStatus"`.
- [x] All five dynamic values remain Prisma-bound parameters.
- [x] Existing SQL-literal enum writes are not mechanically rewritten.
- [x] Existing retry, idempotency, correlation and queue semantics are unchanged.
- [x] Focused unit tests inspect the actual generated `Prisma.Sql` objects rather
      than only source text.
- [x] A disposable migrated PostgreSQL integration test executes the affected
      runtime writes without SQLSTATE `42804`.
- [x] No schema, migration, Shared, Admin, Shopify, Gateway or system-test change is
      made.

## Validation

### Focused unit validation

Run:

```bash
npx vitest run \
  tests/unit/services/translation-batch-submit.service.test.ts \
  tests/unit/services/translation-batch-poll.service.test.ts \
  tests/unit/services/translation-batch-results.service.test.ts \
  tests/unit/services/translation-reconciliation.service.test.ts
```

The tests must inspect the actual `Prisma.Sql` supplied to `$executeRaw()`.

Required deterministic assertions:

#### Submission

For the existing failure paths, prove the generated Batch update contains:

```text
"support"."MerchantTranslationBatchStatus"
```

and the bound `values` contain the expected logical status for representative
cases:

```text
READY
FAILED
SUBMISSION_UNKNOWN
```

Do not assert only that the source contains the word `CAST`.

#### Poll

For a terminal failed provider Batch, prove:

```text
Batch UPDATE
  -> bound FAILED
  -> CAST(... AS "support"."MerchantTranslationBatchStatus")

translation UPDATE
  -> bound FAILED (or PENDING in the chosen retry fixture)
  -> CAST(... AS "support"."MerchantMessageTranslationStatus")
```

Preserve existing CAS/ownership tests.

#### Results

For a failed provider result, prove the actual translation UPDATE contains:

```text
"support"."MerchantMessageTranslationStatus"
```

and the bound values contain the expected `PENDING` or `FAILED`.

Preserve successful-result and replay/idempotency tests.

#### Reconciliation

For a matched SUBMISSION_UNKNOWN correlation, prove the adoption UPDATE contains:

```text
"support"."MerchantTranslationBatchStatus"
```

and the bound values contain `PROVIDER_COMPLETED` for a completed correlation and/or
`SUBMITTED` for a nonterminal correlation.

Preserve no-create, conflict and lost-CAS behavior.

### Real PostgreSQL regression

Add:

```text
tests/integration/translation-enum-bindings.integration.test.ts
```

Use the same integration-test conventions as
`translation-batch-assembly.concurrency.integration.test.ts`:

```text
TEST_DATABASE_URL absent -> describe.skip
TEST_DATABASE_URL present -> use a fresh PrismaClient
unique random IDs
try/finally cleanup
no real OpenAI calls
no real Redis requirement for the tested service path
```

Run it through the accepted disposable harness:

```bash
npm run test:integration -- \
  tests/integration/translation-enum-bindings.integration.test.ts
```

The integration test must exercise the **real service code**, not duplicate the five
UPDATE statements inside the test.

It must use fake provider/queue collaborators and real PostgreSQL.

Cover these four scenarios, which collectively execute all five dynamic enum writes:

```text
A. TranslationBatchSubmitService
   seed READY Batch
   force a definite retryable/terminal/ambiguous provider-side failure
   execute submit()
   verify persisted Batch status
   -> exercises dynamic submission Batch status

B. TranslationBatchPollService
   seed SUBMITTED Batch + one PENDING translation/current Batch item
   fake provider terminal failure
   execute poll()
   verify terminal Batch status and translation retry/failure status
   -> exercises BOTH dynamic poll enum writes

C. TranslationBatchResultsService
   seed PROVIDER_COMPLETED Batch + one PENDING translation/current Batch item
   fake provider result failure
   execute apply()
   verify translation becomes PENDING or FAILED as configured
   -> exercises dynamic result translation status

D. TranslationReconciliationService
   seed SUBMISSION_UNKNOWN Batch
   fake one exact provider correlation match
   execute reconcile()
   verify adopted SUBMITTED or PROVIDER_COMPLETED status
   -> exercises dynamic reconciliation Batch status
```

For scenarios requiring a message/translation, follow the existing integration fixture
shape:

```text
commerce.Shop
  -> support.MerchantSupportThread
  -> support.MerchantSupportMessage
  -> support.MerchantMessageTranslation
  -> support.MerchantTranslationBatch
  -> support.MerchantTranslationBatchItem
```

Use SQL **literals** for seed enum values (for example `'PENDING'`, `'SUBMITTED'`) so
the fixture itself does not reproduce the bound-parameter defect being tested.

Do not call OpenAI. Do not require a live BullMQ job. Pass queue stubs where needed.

The integration assertion must verify persisted database status after each service
call. Merely asserting "did not throw" is insufficient.

### Repository validation

Also run:

```bash
npm run test:unit
npm run build
npm run prisma:validate
git diff --check
```

Run lint only if this repository declares a lint command; do not invent one.

Known unrelated baseline failures may remain only when they exactly match the durable
development baseline/current accepted repository state. Any new failure in a touched
file/path is task-owned.

## Implementation Notes

This is one bounded corrective task despite touching four services because all edits
repair one inseparable defect class: dynamic Prisma-bound text parameters being
written into ARCH-006 PostgreSQL enum columns.

Do not reopen or rewrite BACKGROUND-005, BACKGROUND-006 or BACKGROUND-007 task
history. Their accepted designs remain valid; this task records the runtime correction
discovered afterwards.

The visible `persistFailure()` SQL error may currently mask the original provider
failure. After the fix, manual validation may expose that original failure. Do not
pre-emptively change provider logic in this task.

Luna-specific execution rule:

```text
make only the five exact cast corrections
+ focused generated-SQL tests
+ one real PostgreSQL integration regression
+ validate
+ return BACKGROUND-009 to review
+ STOP
```

Do not claim another task.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/src/services/translation-batch-submit.service.ts`
- `moda-interact-background/src/services/translation-batch-poll.service.ts`
- `moda-interact-background/src/services/translation-batch-results.service.ts`
- `moda-interact-background/src/services/translation-reconciliation.service.ts`
- `moda-interact-background/tests/unit/services/translation-batch-submit.service.test.ts`
- `moda-interact-background/tests/unit/services/translation-batch-poll.service.test.ts`
- `moda-interact-background/tests/unit/services/translation-batch-results.service.test.ts`
- `moda-interact-background/tests/unit/services/translation-reconciliation.service.test.ts`
- `moda-interact-background/tests/integration/translation-enum-bindings.integration.test.ts`

### Work Completed

- Added schema-qualified PostgreSQL enum casts for all five dynamic Prisma-bound status writes while preserving existing retry, CAS, reconciliation and queue semantics.
- Added generated-`Prisma.Sql` assertions covering bound `READY`, `FAILED`, `SUBMISSION_UNKNOWN`, poll terminal statuses, result retry status, and reconciliation adoption status.
- Added a disposable real-PostgreSQL regression covering submission failure, terminal polling, failed provider results, and `SUBMISSION_UNKNOWN` correlation adoption through the actual services with fake provider/queue collaborators.
- Completed the `src/services` dynamic enum audit: no additional dynamic bound writes to enum-backed `status`, `direction`, `scope`, or `kind` columns were found in the ARCH-006 translation lifecycle.

### Validation Results

- Focused lifecycle unit tests: `npx vitest run tests/unit/services/translation-batch-submit.service.test.ts tests/unit/services/translation-batch-poll.service.test.ts tests/unit/services/translation-batch-results.service.test.ts tests/unit/services/translation-reconciliation.service.test.ts` passed, 42 tests.
- Direct integration regression: `npx vitest run tests/integration/translation-enum-bindings.integration.test.ts` passed, 4 tests.
- Disposable integration harness: `npm run test:integration -- tests/integration/translation-enum-bindings.integration.test.ts` passed, 4 tests.
- `npm run test:unit`: 222 passed, 3 failed in unrelated pre-existing recovery paths (`recovery-routing.service.test.ts` and `pending-recovery-candidate.service.test.ts`); no touched translation lifecycle test failed.
- `npx tsc --noEmit --pretty false`: passed.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- No lint script is declared in `package.json`; no lint command was invented.

### Deviations

The complete unit suite remains non-green because of three unrelated recovery-service failures. This task introduced no failures in the touched services or tests.

### Assumptions

The accepted DATABASE-002 schema in the Background `database` submodule is
authoritative for the enum type names in this task.

### Unresolved Issues

The three unrelated recovery-service unit failures remain for their owning work; the corrected translation persistence exposes no new provider or database error.

### Architectural Concerns

None beyond the demonstrated raw-SQL enum parameter typing defect.

### Review Status

Ready for Review.

## Architect Review

Pending.
