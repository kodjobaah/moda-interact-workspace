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
status: pending
priority: 31
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-BACKGROUND-001
enables:
  - ARCH-023-BACKGROUND-004
created: 2026-09-29
updated: 2026-09-29
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

- [ ] Add exact R2 runtime config validation.
- [ ] Add private S3-compatible R2 client.
- [ ] Implement bounded GET + hash/size validation.
- [ ] Implement deterministic CSV extraction.
- [ ] Implement XLSX ZIP safety preflight.
- [ ] Implement deterministic XLSX extraction.
- [ ] Implement safe upload-asset cleanup service.
- [ ] Add unit/integration tests.
- [ ] Confirm no R2 object key appears in logs/results.

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

- [ ] Cross-shop asset access is rejected before R2 access.
- [ ] Byte count and SHA-256 are independently verified.
- [ ] Upload/decompressed limits are enforced.
- [ ] CSV extraction follows the exact row/header rules.
- [ ] XLSX formulas are never executed and formula expressions are never emitted.
- [ ] Active content/external workbook mechanisms are rejected.
- [ ] Referenced assets can never be cleanup-deleted.
- [ ] R2 object keys/credentials never enter model-facing/source-text results or logs.
- [ ] No normalization/chunking/embedding/promotion is implemented here.

## Validation

- [ ] CSV extraction tests
- [ ] XLSX safety/extraction tests
- [ ] R2 acquirer tests using a fake/local S3-compatible client abstraction; no public network
- [ ] database-backed cleanup integration tests
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP. Do not start BACKGROUND-004.

## Completion Report

### Status
Not Started
### Files Changed
None.
### Work Completed
None.
### Validation Results
None.
### Deviations
None.
### Assumptions
None.
### Unresolved Issues
None.
### Architectural Concerns
None.

## Architect Review

### Review Status
Pending
### Review Notes
Pending.
### Reviewed Files
Pending.
### Validation Reviewed
Pending.
### Architecture Conformance
Pending.
### Follow-up
Pending.
