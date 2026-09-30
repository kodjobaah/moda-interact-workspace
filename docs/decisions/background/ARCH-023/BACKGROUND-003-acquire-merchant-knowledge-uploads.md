---
id: ARCH-023-BACKGROUND-003
architecture_id: ARCH-023
title: Acquire and extract Merchant Knowledge uploads
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 31
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-023-BACKGROUND-001
enables:
  - ARCH-023-BACKGROUND-004
created: 2026-09-29
updated: 2026-09-30
---

# Acquire and extract Merchant Knowledge uploads

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Implement private Cloudflare R2 acquisition and deterministic CSV/XLSX extraction for Merchant Knowledge, plus safe cleanup of expired/unreferenced uploaded assets.

This task implements the BACKGROUND-001 uploaded-asset acquisition contract. It does not normalize, truncate, chunk, embed or promote source revisions.

## Scope

Authorized primary files:

```text
package.json
package-lock.json

src/services/merchant-knowledge-r2-config.ts
src/services/merchant-knowledge-r2-client.ts
src/services/merchant-knowledge-uploaded-asset-acquirer.ts
src/services/merchant-knowledge-csv-extraction.ts
src/services/merchant-knowledge-xlsx-extraction.ts
src/services/merchant-knowledge-upload-cleanup.service.ts

tests/unit/services/merchant-knowledge-csv-extraction.test.ts
tests/unit/services/merchant-knowledge-xlsx-extraction.test.ts
tests/unit/services/merchant-knowledge-uploaded-asset-acquirer.test.ts
tests/integration/merchant-knowledge-upload-cleanup.integration.test.ts
```

Use Cloudflare R2's S3-compatible API. Add only the package dependencies needed for S3 access and deterministic CSV/XLSX parsing/preflight.

## Out of Scope

- signed upload issuance (Shopify task).
- R2 bucket/credential deployment (Gateway task).
- browser upload.
- WEB_PAGE fetching.
- normalization/content-unit limits.
- chunking/embeddings/pgvector.
- revision promotion.
- plan entitlement reconciliation.
- source CRUD.
- Tool lookup.

## Requirements

### R1 — exact runtime environment contract

Read exactly:

```text
MERCHANT_KNOWLEDGE_R2_ENDPOINT
MERCHANT_KNOWLEDGE_R2_BUCKET
MERCHANT_KNOWLEDGE_R2_ACCESS_KEY_ID
MERCHANT_KNOWLEDGE_R2_SECRET_ACCESS_KEY

MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES
MERCHANT_KNOWLEDGE_MAX_XLSX_UNCOMPRESSED_BYTES
```

Rules:

```text
endpoint: valid https URL
bucket/access key/secret: trimmed non-empty
MAX_UPLOAD_BYTES: positive safe integer
MAX_XLSX_UNCOMPRESSED_BYTES: positive safe integer
```

Do not read generic browser-facing credentials.
Do not log secrets.
Use S3 region `"auto"`.

Gateway will wire these exact names later.

### R2 — R2 client

Use one S3-compatible client factory configured from R1.

Required operations only:

```text
GetObject
DeleteObject
HeadObject if needed for cleanup diagnostics
```

Do not generate signed URLs in Background.
Do not list the entire bucket.

The model/application result must never receive an R2 object key.

### R3 — uploaded-asset acquisition preconditions

`MerchantKnowledgeUploadedAssetAcquirer.acquire` must load the asset by `assetId` and require:

```text
asset exists
asset.shopId == input.shopId
asset.status == AVAILABLE
asset.dataFormat.key == input.dataFormatKey
asset.dataFormat.inputKind == UPLOAD
input.dataFormatKey IN ("CSV", "XLSX")
```

Also require persisted:

```text
sizeBytes > 0
sha256 = lowercase 64 hex
contentType non-empty
```

Reject cross-shop access before issuing R2 GET.

### R4 — bounded private R2 GET

GET exactly the persisted `objectKey`.

Stream bytes and abort when received bytes exceed:

```text
MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES
```

Also reject when persisted `sizeBytes` itself exceeds that limit before GET.

Compute SHA-256 while reading.

After download require:

```text
actual bytes length == persisted sizeBytes
actual lowercase sha256 == persisted sha256
```

Mismatch is permanent processing failure.

Never expose/log the object key.

### R5 — CSV validation and extraction

CSV requirements are exact:

```text
original filename extension .csv (case-insensitive)
bytes decode as UTF-8 using fatal decoding
optional UTF-8 BOM permitted
delimiter comma
RFC-style double-quote escaping
multiline quoted fields supported
first non-empty record = header
empty records ignored
blank header cell -> "Column <1-based-index>"
```

For each non-empty data record emit fields in header-column order:

```text
<Header 1>: <value>
<Header 2>: <value>
...
```

Rules:

```text
blank cell -> omit field
extra cells beyond header count -> ignore
missing trailing cells -> blank/omit
```

Separate non-empty data rows by exactly two LF characters.

Do not normalize whitespace globally; BACKGROUND-004 owns D3 normalization.

### R6 — XLSX archive safety preflight

Before loading workbook semantics, inspect the ZIP central directory.

Require:

```text
original filename extension .xlsx (case-insensitive)
valid ZIP/OOXML container
sum of all entry uncompressed sizes <= MERCHANT_KNOWLEDGE_MAX_XLSX_UNCOMPRESSED_BYTES
```

Reject archive containing any entry matching these prefixes/names case-insensitively:

```text
xl/vbaProject.bin
xl/externalLinks/
xl/embeddings/
xl/oleObjects/
xl/connections.xml
```

Reject encrypted/password-protected workbooks.

Do not execute macros, formulas, actions or external links.

The uncompressed-byte safety check must occur before the workbook parser is allowed to expand the workbook fully.

### R7 — deterministic XLSX extraction

Process only visible worksheets, in workbook order.

For each visible worksheet:

1. first non-empty row is header;
2. empty rows are ignored;
3. blank header cell -> `Column <1-based-index>`;
4. each later non-empty row emits:

```text
Worksheet: <worksheet name>
<Header 1>: <value>
<Header 2>: <value>
...
```

5. separate emitted rows by exactly two LF characters.

Scalar conversion:

```text
string  -> exact cell text
number  -> invariant decimal representation
boolean -> true | false
Date    -> ISO-8601 using Date.toISOString()
blank   -> omitted
formula -> cached scalar result only
```

A formula with no cached scalar contributes no value.

Unsupported complex cell values are omitted; do not serialize internal parser objects.

Never include the formula expression itself.

### R8 — acquisition result

Successful CSV/XLSX acquisition returns:

```ts
{
  contentType: asset.contentType;
  extractedText: <deterministic extracted text>;
  resolvedUrl: null;
  fetchedAt: null;
}
```

No object key, asset id, signed URL or raw workbook bytes appear in the result.

### R9 — safe cleanup model

Create `MerchantKnowledgeUploadCleanupService.cleanupOnce`.

Constants:

```text
pageSize = 100
AVAILABLE orphan grace = 24 hours
```

Eligible logical tombstones:

1. `PENDING_UPLOAD` where `uploadExpiresAt < now`;
2. `AVAILABLE` where `createdAt < now - 24h` and no revision references the asset;
3. already `DELETED` rows may be retried for physical R2 deletion.

For PENDING/AVAILABLE candidates:

1. transactionally lock asset row;
2. re-check zero `MerchantKnowledgeSourceRevision` references;
3. if any reference exists -> skip;
4. update status to `DELETED`;
5. set bounded `failureCode`:
   ```text
   UPLOAD_EXPIRED
   UNREFERENCED_ASSET
   ```
6. commit;
7. then issue `DeleteObject`.

If physical delete fails, keep the database tombstone `DELETED`; a later cleanup pass may retry physical delete. Do not restore it to AVAILABLE.

A referenced asset MUST NEVER be physically deleted.

Do not scan/list R2 globally to infer ownership.

### R10 — cleanup tests

Prove:

```text
expired unreferenced PENDING_UPLOAD -> tombstone + delete attempt
old unreferenced AVAILABLE -> tombstone + delete attempt
recent AVAILABLE -> retained
any referenced asset -> retained, no DeleteObject
race/recheck with new reference -> retained
DELETED orphan -> physical delete retry allowed
DeleteObject failure does not make asset AVAILABLE again
```

### R11 — package/dependency discipline

Use mature focused dependencies rather than implementing XLSX ZIP/XML parsing from scratch.

Allowed dependency categories:

```text
AWS SDK v3 S3 client
CSV parser
XLSX workbook parser
ZIP central-directory reader
```

Do not introduce a general cloud-storage abstraction framework.

The package lock must pin the actual installed versions.

## Work Items

- [x] Add exact R2 runtime config validation.
- [x] Add private S3-compatible R2 client.
- [x] Implement bounded GET + hash/size validation.
- [x] Implement deterministic CSV extraction.
- [x] Implement XLSX ZIP safety preflight.
- [x] Implement deterministic XLSX extraction.
- [x] Implement safe upload-asset cleanup service.
- [x] Add unit/integration tests.
- [x] Confirm no R2 object key appears in logs/results.

## Interfaces / Contracts

Implements BACKGROUND-001:

```text
MerchantKnowledgeUploadedAssetAcquirer
```

Consumed later by BACKGROUND-004.

Cleanup service is wired into the dedicated worker entrypoint by BACKGROUND-004.

## Dependencies

- `ARCH-023-BACKGROUND-001`

## Enables

- `ARCH-023-BACKGROUND-004`

## Acceptance Criteria

- [x] Cross-shop asset access is rejected before R2 access.
- [x] Byte count and SHA-256 are independently verified.
- [x] Upload/decompressed limits are enforced.
- [x] CSV extraction follows the exact row/header rules.
- [x] XLSX formulas are never executed and formula expressions are never emitted.
- [x] Active content/external workbook mechanisms are rejected.
- [x] Referenced assets can never be cleanup-deleted.
- [x] R2 object keys/credentials never enter model-facing/source-text results or logs.
- [x] No normalization/chunking/embedding/promotion is implemented here.

## Validation

- [x] CSV extraction tests
- [x] XLSX safety/extraction tests
- [x] R2 acquirer tests using a fake/local S3-compatible client abstraction; no public network
- [x] database-backed cleanup integration tests
- [x] `npm run build`
- [x] `git diff --check`
- [x] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP. Do not start BACKGROUND-004.

## Completion Report

### Status
Ready for Architect Review — Attempt 2
### Files Changed
Attempt 1 implementation commit `cde2632` added the private R2 acquisition, extraction, and cleanup services. Attempt 2 commit `ad38c3a04c3532755323f34a146d72d718c3181f` changes `src/services/merchant-knowledge-xlsx-extraction.ts`, `src/services/merchant-knowledge-upload-cleanup.service.ts`, `tests/unit/services/merchant-knowledge-xlsx-extraction.test.ts`, and `tests/integration/merchant-knowledge-upload-cleanup.integration.test.ts`. No database schema, migration, queue resource, worker entrypoint, or other repository was changed.
### Work Completed
Added exact private R2 configuration validation and an S3-compatible client factory configured for region `auto`, limited to `GetObject` and `DeleteObject`. Uploaded-asset acquisition validates ownership/status/format/metadata before GET, bounds streamed bytes, independently verifies persisted size and SHA-256, and returns only content type and deterministic extracted text with null URL/timestamp.

Added and lockfile-pinned `@aws-sdk/client-s3@3.1143.0`, `csv-parse@7.0.3`, `exceljs@4.4.0`, `yauzl@3.4.0`, and `@types/yauzl@3.4.0`.

Added strict UTF-8/RFC-style CSV extraction and XLSX central-directory preflight before ExcelJS workbook loading. XLSX extraction requires core OOXML parts, enforces archive expansion limits, rejects encryption and forbidden active-content/external-workbook paths, emits visible worksheets in workbook order, and uses cached scalar formula results only.

Added cleanup candidate paging (100), 24-hour AVAILABLE orphan grace, transactional asset row locks and fresh revision-reference checks, bounded tombstone failure codes, and post-commit physical deletion with retryable DELETED tombstones. Cleanup remains unwired to a worker entrypoint, as assigned to BACKGROUND-004.

Attempt 2 addressed both architect findings. A1-R1: XLSX scalar extraction now accepts both `formula` and `sharedFormula` cell objects and recursively emits only their cached scalar result; a serialized/reloaded shared-formula workbook proves master and follower cached values appear while neither formula expression nor shared reference is emitted. A1-R2: cleanup now advances by `(createdAt, id)` keyset across successive queries of at most 100 rows, so retained DELETED tombstones cannot pin the first page; the PostgreSQL regression uses 101 earlier tombstones followed by an expired upload and proves the later asset is tombstoned and physically deleted. Existing row locking, reference re-check, post-commit deletion, retained tombstones, and referenced-asset protection remain intact.
### Validation Results
Passed: focused CSV/XLSX/acquirer tests (3 files, 16 tests); cleanup database integration (1 test) using the repository disposable-infrastructure helper with `pgvector/pgvector:pg17` and the accepted migrations; `npm run build` (Prisma Client generation and TypeScript compile); `npm run prisma:validate`; `git diff --check`; changed-file diagnostics (no errors).

Attempt 2 passed: focused CSV/XLSX/acquirer unit suites (3 files, 16 tests); XLSX shared-formula suite (5/5); cleanup PostgreSQL integration (2/2) using the shared disposable-infrastructure helper with `pgvector/pgvector:pg17`; `npm run build`; `npm run prisma:validate`; `npx tsc --noEmit`; `git diff --check`; changed-file diagnostics (no errors). The repository `npm run test:integration` wrapper defaults to plain PostgreSQL and cannot apply the existing `vector` extension migration; the same shared helper was invoked with its supported pgvector image option to run the required disposable database test. Attempt 1 broad-suite failures remain unrelated and were not rerun for this bounded correction.

The full `npm test` run reported 82 files passed, 5 failed, and 13 skipped (1,187 tests passed, 12 failed, 25 skipped). Failures were outside this task: an evidence fixture resolved under a missing ARCH-020 worktree; four translation integration cases could not reach `localhost:5432`; three billing reconciliation expectation failures; one checkout recovery language expectation failure; and four observability startup/version failures. All BACKGROUND-003 focused tests passed, and the cleanup integration passed in the disposable pgvector environment.
### Deviations
No implementation-scope deviations. `npm install` reported five dependency audit findings in the installed dependency graph and install-script approval notices; no unrelated audit fixes or dependency upgrades were applied.
### Assumptions
Gateway will provide the six task-defined `MERCHANT_KNOWLEDGE_*` runtime variables in a later task. BACKGROUND-004 owns worker-entrypoint wiring for cleanup and acquisition composition.
### Unresolved Issues
The unrelated full-suite failures listed under Validation Results remain outside this task's scope. No task-scoped validation failure remains.
### Architectural Concerns
None identified. The implementation does not add schema changes, source normalization, chunking, embeddings, promotion, or a general cloud-storage abstraction.

### Execution Provenance
Physical worktree isolation:
- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-BACKGROUND-003`
- parent branch: `task/ARCH-023-BACKGROUND-003`
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-BACKGROUND-003`
- implementation branch: `task/ARCH-023-BACKGROUND-003`
- shared workspace checkout switched/mutated for task work: no
- shared implementation checkout switched/mutated for task work: no
- another task worktree reused: no

Start-of-attempt synchronization:
- parent remote task branch fast-forwarded: no; no fast-forward was needed
- parent `origin/main` incorporated: yes; already current at preparation
- implementation remote task branch fast-forwarded: no; no fast-forward was needed
- implementation `origin/main` incorporated: yes; already current at preparation

Recursive implementation submodules:
- `git submodule sync --recursive`: passed
- `git submodule update --init --recursive`: passed
- recorded database submodule commit: `2eb17ee910491e8f9df82736fc0a843844415947`
- Attempt 1 implementation commit: `cde2632` (`task/ARCH-023-BACKGROUND-003`)
- Attempt 2 implementation commit pushed: `ad38c3a04c3532755323f34a146d72d718c3181f` (`task/ARCH-023-BACKGROUND-003`)

## Architect Review

### Review Status
Accepted — Attempt 2

### Review Notes

#### Attempt 2 review — Accepted — 2026-09-30

Reviewed implementation commit `ad38c3a04c3532755323f34a146d72d718c3181f` and
submitted parent report commit `f95fc217a2f2a873e830471dd9437d99970574bc` against
the full BACKGROUND-003 contract and the complete Attempt 1 correction contract. Attempt 2
is accepted.

The private-R2 acquisition boundary remains conformant. `MerchantKnowledgeUploadedAssetAcquirer`
loads the persisted asset before storage access, rejects cross-shop/unavailable/wrong-format assets
before GET, streams only the persisted object key through the server-side R2 client, enforces the
configured byte ceiling during streaming, recomputes SHA-256 and exact byte length, and returns only
content type plus deterministic extracted text. The result contains no object key, asset id, signed
URL or raw workbook bytes.

CSV extraction remains deterministic and non-normalizing: fatal UTF-8 decoding with optional BOM,
comma/RFC-style quoting, first non-empty header, deterministic blank-header labels, omission of blank
cells, bounded header-column output and exactly two LF characters between emitted rows. XLSX safety
preflight still reads the ZIP central directory before ExcelJS expands workbook semantics, enforces
the aggregate uncompressed-byte limit, rejects encrypted entries and the architecture-forbidden
active/external-content paths, and processes only visible worksheets in workbook order.

A1-R1 is resolved. `scalar()` now treats both ExcelJS `formula` and `sharedFormula` value shapes as
formula cells and recursively emits only their cached `result`. The regression serializes and reloads
a real shared-formula workbook, verifies both the master and follower cached scalar values in the
extracted text, and verifies that neither the formula expression nor shared-formula reference is
emitted. No formula execution path or complex-object serialization was introduced.

A1-R2 is resolved. `cleanupOnce()` retains `pageSize = 100` but now keyset-pages by the stable
`(createdAt, id)` ordering. Each candidate is still reloaded under `FOR UPDATE`, revision references
are re-counted transactionally, eligible PENDING/AVAILABLE rows are tombstoned before commit, and
physical `DeleteObject` occurs only after commit. Referenced rows are skipped, successful/failed
physical deletion leaves the durable `DELETED` tombstone, and the service never lists R2 globally.
The new PostgreSQL regression places 101 earlier `DELETED` rows before a later expired upload and
proves the later asset is reached, tombstoned and physically deleted while the page size remains 100.

The implementation introduces no schema/migration change, queue contract, normalization, chunking,
embedding, revision-promotion behavior, worker entrypoint or Gateway wiring. BACKGROUND-004 retains
ownership of final worker composition. The reported broad-suite failures and npm audit findings are
outside the BACKGROUND-003 changed surface and are not acceptance blockers for this bounded task.

The review archive contains source/task state but no Git metadata or installed `node_modules`, so the
submitted commands were not independently rerun in this review container. The implementation and
authored regression paths were inspected directly, and the durable Completion Report records the
launcher-resolved parent/implementation worktrees, synchronization/submodule preparation, pushed
commits, clean handoff and the passing focused/disposable-database evidence.

### Reviewed Files

Implementation repository:

- `package.json`
- `package-lock.json`
- `src/services/merchant-knowledge-r2-config.ts`
- `src/services/merchant-knowledge-r2-client.ts`
- `src/services/merchant-knowledge-uploaded-asset-acquirer.ts`
- `src/services/merchant-knowledge-csv-extraction.ts`
- `src/services/merchant-knowledge-xlsx-extraction.ts`
- `src/services/merchant-knowledge-upload-cleanup.service.ts`
- `tests/unit/services/merchant-knowledge-csv-extraction.test.ts`
- `tests/unit/services/merchant-knowledge-xlsx-extraction.test.ts`
- `tests/unit/services/merchant-knowledge-uploaded-asset-acquirer.test.ts`
- `tests/integration/merchant-knowledge-upload-cleanup.integration.test.ts`
- `database/prisma/migrations/20260929160000_arch023_merchant_knowledge_schema/migration.sql`

Parent workspace:

- `docs/decisions/background/ARCH-023/BACKGROUND-003-acquire-merchant-knowledge-uploads.md`
- `docs/decisions/background/ARCH-023/_index.md`
- `docs/architecture/ARCH-023-merchant-knowledge.md`

### Validation Reviewed

- Attempt 2 focused CSV/XLSX/acquirer suites passed **16/16**.
- Shared-formula XLSX coverage passed **5/5** and exercises a serialized/reloaded shared-formula workbook.
- Disposable pgvector PostgreSQL cleanup integration passed **2/2**, including the >100-candidate progression case.
- `npm run build`, `npm run prisma:validate`, `npx tsc --noEmit`, changed-file diagnostics and `git diff --check` are recorded as passed.
- The cleanup regression uses the accepted migrations with a pgvector-capable disposable image rather than the wrapper's non-pgvector default.
- Broad-suite failures recorded by the implementing agent are outside the task-owned source/tests and do not contradict the focused acceptance evidence.

### Architecture Conformance

Conforms. BACKGROUND-003 owns only private uploaded-asset acquisition/extraction and safe cleanup.
PostgreSQL remains authoritative for tenant ownership and asset/revision lifecycle; Cloudflare R2
contains only immutable original bytes; object keys remain private runtime locators; spreadsheet
content remains untrusted runtime data; cleanup is reference-safe and database-led rather than
bucket-led. No responsibility belonging to Shopify, Gateway or BACKGROUND-004 was absorbed.

### Follow-up

`ARCH-023-BACKGROUND-003` is **Complete / Accepted at Attempt 2**.

`ARCH-023-BACKGROUND-004` remains Pending because its other dependency,
`ARCH-023-BACKGROUND-002`, is still Ready rather than Complete. This acceptance therefore does not
promote or start a downstream Background task.

#### Historical Attempt 1 — Changes Requested — 2026-09-30

##### Review Notes
The implementation is substantially aligned with the private-R2 acquisition, bounded byte/hash verification, deterministic CSV extraction, XLSX ZIP preflight, transactional cleanup and repository-boundary requirements. The submitted focused tests, disposable pgvector cleanup integration, build, Prisma validation, changed-file diagnostics and diff check are accepted as valid Attempt 1 evidence.

Two task-scoped corrections remain:

**A1-R1 — preserve cached scalar results for ExcelJS shared formulas.**

`merchant-knowledge-xlsx-extraction.ts` currently recognizes a formula value only when the cell-value object has a `formula` property. ExcelJS also represents shared-formula cells with `sharedFormula` plus an optional cached `result`. Such a cell is therefore treated as an unsupported complex value and its cached scalar is silently omitted. R7 requires every formula form to contribute its cached scalar result only, while never emitting or executing the expression.

Correct the scalar conversion so ordinary/master and shared formula representations use only their cached scalar result. Add an XLSX regression that round-trips an actual shared-formula workbook, proves its cached scalar appears in deterministic extracted text, and proves no formula/shared-formula expression is emitted.

**A1-R2 — cleanup must make progress beyond the first retained tombstone page.**

`cleanupOnce()` selects the oldest 100 eligible rows and leaves successfully deleted rows in `DELETED` state. Because every `DELETED` row remains eligible for later physical-delete retry, the same first 100 tombstones can be selected on every hourly run and permanently prevent later expired `PENDING_UPLOAD`, old unreferenced `AVAILABLE`, or later `DELETED` candidates from being considered. That does not satisfy the cleanup objective once the retained tombstone set reaches one page.

Correct candidate progression/fairness while preserving `pageSize = 100`, transactional row locking/reference re-checks, post-commit R2 deletion, retained `DELETED` tombstones, and the prohibition on bucket-wide R2 listing. No schema/migration change is authorised. Add a database-backed regression with more than one page of earlier retained `DELETED` candidates and a later eligible asset, proving the later asset is reached without physically deleting any referenced asset.

The reported npm dependency-audit findings are not an acceptance blocker for this task and no unrelated audit remediation is requested.

##### Reviewed Files
- `package.json`
- `package-lock.json`
- `src/services/merchant-knowledge-r2-config.ts`
- `src/services/merchant-knowledge-r2-client.ts`
- `src/services/merchant-knowledge-uploaded-asset-acquirer.ts`
- `src/services/merchant-knowledge-csv-extraction.ts`
- `src/services/merchant-knowledge-xlsx-extraction.ts`
- `src/services/merchant-knowledge-upload-cleanup.service.ts`
- `tests/unit/services/merchant-knowledge-csv-extraction.test.ts`
- `tests/unit/services/merchant-knowledge-xlsx-extraction.test.ts`
- `tests/unit/services/merchant-knowledge-uploaded-asset-acquirer.test.ts`
- `tests/integration/merchant-knowledge-upload-cleanup.integration.test.ts`
- `docs/decisions/background/ARCH-023/BACKGROUND-003-acquire-merchant-knowledge-uploads.md`
- `docs/architecture/ARCH-023-merchant-knowledge.md`

##### Validation Reviewed
Accepted Attempt 1 evidence:

- focused CSV/XLSX/acquirer tests: 16/16 passed;
- disposable pgvector cleanup integration: 1/1 passed;
- `npm run build`: passed;
- `npm run prisma:validate`: passed;
- `git diff --check`: passed;
- changed-file diagnostics: clean;
- broad-suite failures recorded in the Completion Report are outside the BACKGROUND-003 changed surface.

Attempt 2 must rerun the focused XLSX extraction tests, cleanup integration test, build, Prisma validation, changed-file diagnostics and `git diff --check` after the corrections.

##### Architecture Conformance
Conforms to ARCH-023 ownership and private-R2 boundaries except for A1-R1 and A1-R2 above. No database schema, queue contract, worker entrypoint, normalization/chunking/embedding/promotion behavior or Gateway deployment change is required for the requested correction.

##### Follow-up
Return the same task to `ready` with `attempt: 1`, no active executor/claim, for the next authorized claim to become Attempt 2.

Attempt 2 correction scope is exactly:

1. support cached scalar extraction from both ordinary/master and shared ExcelJS formula representations without emitting formula expressions;
2. add the shared-formula XLSX regression;
3. ensure cleanup progresses beyond an earlier retained `DELETED` page while keeping page size 100 and all existing reference-safety/transaction/R2 boundaries;
4. add the >100-candidate database-backed cleanup progression regression;
5. rerun the bounded validation listed above and update the Completion Report;
6. return to `moda_architect` review and STOP. Do not start BACKGROUND-004.
