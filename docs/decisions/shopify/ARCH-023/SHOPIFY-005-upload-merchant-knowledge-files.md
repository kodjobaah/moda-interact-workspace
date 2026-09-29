---
id: ARCH-023-SHOPIFY-005
architecture_id: ARCH-023
title: Upload and manage Merchant Knowledge CSV and XLSX sources
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 52
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-SHOPIFY-004
enables:
  - ARCH-023-GATEWAY-001
created: 2026-09-29
updated: 2026-09-29
---

# Upload and manage Merchant Knowledge CSV and XLSX sources

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Extend the Merchant Knowledge management surface with private direct-to-R2 CSV/XLSX uploads, upload finalisation, immutable uploaded-asset replacement and Reprocess.

The browser receives only a short-lived signed PUT and asset id; server credentials remain private. A source/revision is created only after the uploaded object is verified to exist and the current plan entitlement is re-checked.

## Context

R2 stores immutable original bytes only.

PostgreSQL remains authoritative for:

```text
shop ownership
asset metadata/status
source identity/order
revision lifecycle
normalized content/chunks/vectors
```

Background independently re-downloads and verifies bytes/hash/format before processing.

## Scope

Primary authorized implementation surface:

```text
package.json
package-lock.json

app/services/merchant-knowledge/r2-config.server.ts
app/services/merchant-knowledge/r2-client.server.ts
app/services/merchant-knowledge/upload.server.ts

app/routes/app/merchant-knowledge/upload-intent/route.ts
app/routes/app/merchant-knowledge/upload-finalize/route.ts
app/routes/app/merchant-knowledge/reprocess/route.ts

app/components/settings/MerchantKnowledgeSection.tsx
app/components/settings/MerchantKnowledgeUploadForm.tsx

tests/unit/merchant-knowledge-upload.test.ts
tests/unit/merchant-knowledge-upload-form.test.tsx
tests/integration/merchant-knowledge-upload.integration.test.ts
```

Extend SHOPIFY-004 services rather than duplicating entitlement/order/queue logic.

## Out of Scope

- R2 bucket/service deployment (Gateway).
- Background R2 reads/parsing.
- browser/service credentials.
- server proxy upload of file bytes.
- `.xls`, `.xlsm`, `.ods`, PDF, DOCX.
- changing purpose/data format of an existing source.
- automatic reprocess on plan increase.
- storing file bytes in PostgreSQL.

## Requirements

### R1 — exact server R2 environment contract

Read exactly:

```text
MERCHANT_KNOWLEDGE_R2_ENDPOINT
MERCHANT_KNOWLEDGE_R2_BUCKET
MERCHANT_KNOWLEDGE_R2_ACCESS_KEY_ID
MERCHANT_KNOWLEDGE_R2_SECRET_ACCESS_KEY
MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES
```

Rules:

```text
endpoint valid https URL
bucket/access key/secret non-empty
MAX_UPLOAD_BYTES positive safe integer
region = "auto"
```

Credentials are server-only and never serialized into loaders/actions.

Gateway will supply least-privilege values for this application.

### R2 — dependencies

Use:

```text
@aws-sdk/client-s3
@aws-sdk/s3-request-presigner
```

Do not add a second object-storage abstraction library.

Use one module-level/client-factory S3 client according to existing server service conventions.

### R3 — exact upload intent input

Authenticated server action accepts:

```ts
{
  purposeKey: MerchantKnowledgePurposeKey;
  dataFormatKey: "CSV" | "XLSX";
  originalFileName: string;
  contentType: string;
  sizeBytes: number;
}
```

The browser does not supply shopId or objectKey.

Validation:

```text
originalFileName trimmed 1..255
sizeBytes positive safe integer <= MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES
```

Load current entitlement using SHOPIFY-004 service.

Require exact `(purposeKey,dataFormatKey)` currently entitled and globally active.

Require Data Format:

```text
inputKind = UPLOAD
canonicalExtension:
  CSV  -> .csv
  XLSX -> .xlsx
```

Require case-insensitive original filename extension matches canonical extension.

Require `contentType` in the Data Format's persisted `acceptedContentTypes`.

Intent itself does not consume a source slot.

### R4 — asset and object key

Create `MerchantKnowledgeUploadedAsset` before signing:

```text
id = application/Prisma generated
shopId = authenticated shop
dataFormatId = resolved format
status = PENDING_UPLOAD
objectKey = merchant-knowledge/<shopId>/<assetId>/source.<canonical-extension-without-leading-dot>
originalFileName = exact trimmed name
uploadExpiresAt = now + 10 minutes
contentType/sizeBytes/sha256/availableAt = null
```

The object key is generated only on server.

Do not return `objectKey` as a separate response field.

### R5 — signed PUT

Presign exactly one:

```text
PutObjectCommand
Bucket = MERCHANT_KNOWLEDGE_R2_BUCKET
Key = persisted objectKey
ContentType = validated contentType
```

Expiration:

```text
600 seconds
```

Return exactly:

```ts
{
  assetId: string;
  uploadUrl: string;
  expiresAt: string;
  requiredHeaders: {
    "Content-Type": string;
  };
  maxUploadBytes: number;
}
```

No credentials.

Do not return an R2 GET URL.

### R6 — browser upload

The UI:

1. validates size/type/extension before requesting intent;
2. requests R3 intent;
3. uses browser `fetch(uploadUrl,{method:"PUT",body:file,headers:requiredHeaders})`;
4. does not send Shopify cookies/auth headers to R2 beyond presigned URL semantics;
5. computes lowercase SHA-256 of exact file bytes using Web Crypto;
6. calls finalization only after PUT succeeds.

Do not POST file bytes through Moda server.

### R7 — exact finalization input

Authenticated finalization accepts:

```ts
{
  assetId: string;
  purposeKey: MerchantKnowledgePurposeKey;
  name: string;
  languageTag: ModaSupportedLanguageTag;
  sizeBytes: number;
  sha256: string;
  contentType: string;
  sourceId?: string; // present only for file replacement
}
```

`dataFormatKey` is resolved from persisted asset and cannot be changed by browser.

Validate:

```text
name trimmed 1..160
sizeBytes positive <= max
sha256 lowercase 64 hex
languageTag Shared-supported
```

### R8 — verify uploaded object before database finalization

Before the final DB transaction:

1. load asset by `assetId`;
2. require same authenticated shop;
3. require:
   ```text
   status = PENDING_UPLOAD
   uploadExpiresAt >= now
   ```
4. use R2 `HeadObject` on persisted key;
5. require object exists;
6. require:
   ```text
   ContentLength == submitted sizeBytes
   ContentLength <= max
   persisted/HEAD ContentType is compatible with submitted contentType
   submitted contentType is in persisted Data Format acceptedContentTypes
   ```
7. do not trust/store an ETag as content hash.

The client SHA-256 remains declared metadata; Background recomputes it.

### R9 — create new uploaded source atomically

When `sourceId` absent:

Within one DB transaction:

1. lock Shop ordering scope;
2. reload asset and require still PENDING_UPLOAD/same shop;
3. re-resolve current entitlement/catalogue;
4. require asset Data Format + submitted Purpose exact pair is still currently allowed;
5. count current allowed source types exactly as SHOPIFY-004; require active slot available;
6. set asset:
   ```text
   status = AVAILABLE
   contentType = submitted contentType
   sizeBytes = submitted sizeBytes
   sha256 = submitted sha256
   availableAt = now
   ```
7. allocate next global source position;
8. create source:
   ```text
   purposeId = selected purpose
   dataFormatId = asset dataFormat
   name
   languageTag
   currentGeneration = 1
   ```
9. create revision:
   ```text
   generation = 1
   reason = CREATE
   requestedUrl = null
   uploadedAssetId = asset.id
   status = PENDING
   requestedAt = now
   ```
10. commit;
11. enqueue C4 best effort via SHOPIFY-004 helper.

### R10 — replace file atomically

When `sourceId` present:

1. source belongs to authenticated shop;
2. source Data Format must equal asset Data Format;
3. source Purpose is immutable; submitted `purposeKey` must equal source purpose;
4. source must be currently entitled;
5. lock source;
6. make asset AVAILABLE as R9;
7. increment `source.currentGeneration` exactly once;
8. update only:
   ```text
   source.name
   source.languageTag
   ```
9. create:
   ```text
   reason = FILE_REPLACE
   status = PENDING
   uploadedAssetId = new asset.id
   requestedUrl = null
   ```
10. commit then enqueue best effort.

The prior ACTIVE revision and prior immutable asset remain untouched.

### R11 — Reprocess

For an owned currently entitled uploaded source:

1. lock source;
2. load current-generation revision;
3. require `uploadedAssetId != null`;
4. require referenced asset:
   ```text
   status = AVAILABLE
   same shop
   dataFormatId = source.dataFormatId
   ```
5. increment generation;
6. create:
   ```text
   reason = REPROCESS
   uploadedAssetId = same asset.id
   requestedUrl = null
   status = PENDING
   ```
7. commit then enqueue best effort.

Reprocess never requires browser re-upload.

### R12 — abandoned upload behavior

If PUT/finalization is abandoned:

```text
asset stays PENDING_UPLOAD
no MerchantKnowledgeSource exists
no plan source slot consumed
```

Background cleanup owns expiry/tombstone/object deletion.

Shopify app does not delete R2 object synchronously on abandonment.

### R13 — UI

Extend existing Merchant Knowledge section.

For plan-entitled CSV/XLSX combinations:

- Data Format selector shows localized labels;
- file picker `accept` is derived from persisted canonical extension/content types;
- show max upload bytes;
- show upload progress states:
  ```text
  preparing
  uploading
  finalizing
  queued
  failed
  ```
- existing uploaded source shows original filename from referenced configured asset;
- actions:
  ```text
  Reprocess
  Replace file
  Edit name/language
  Delete
  Reorder
  ```

Purpose/Data Format stay immutable after source creation.

Delete/reorder reuse SHOPIFY-004 generic source operations. Deleting a source does not immediately delete historical uploaded assets; Background cleanup governs physical object deletion.

### R14 — secrets/object keys/model boundary

Never place:

```text
R2 access key
R2 secret
objectKey
signed PUT URL after upload workflow
uploaded bytes
```

in:

```text
database normalized knowledge content
Commerce Tool result
prompt/model context
application logs
```

The upload URL may exist only in the immediate authenticated browser response/state needed for PUT and must not be persisted.

### R15 — tests

Prove:

```text
cross-shop asset finalization rejected before HeadObject/DB mutation
disallowed current plan pair rejects intent/finalize
intent does not consume source slot
object key shape exact/server-generated
signed URL expires 600s and is PUT-only
oversized file rejects
extension/contentType mismatch rejects
HeadObject missing/size mismatch rejects
new finalization creates AVAILABLE asset + source + CREATE revision atomically
replace creates new immutable asset + FILE_REPLACE revision
old ACTIVE/old asset remain on replacement
Reprocess reuses same asset
queue failure leaves PENDING durable revision
abandoned PENDING_UPLOAD creates no source
browser never receives credentials/objectKey field
```

## Work Items

- [ ] Add R2 server configuration/client/presigner.
- [ ] Implement upload-intent transaction.
- [ ] Implement browser direct PUT + SHA-256.
- [ ] Implement HeadObject-backed finalization.
- [ ] Implement create/replace/reprocess source lifecycle.
- [ ] Extend Merchant Knowledge UI for uploads.
- [ ] Add security/lifecycle tests.

## Interfaces / Contracts

Extends SHOPIFY-004 source/entitlement/queue services.

Produces private R2 objects and existing C4 processing jobs.

Gateway later provides environment/secrets; Background later reads the same private objects.

## Dependencies

- `ARCH-023-SHOPIFY-004`

## Enables

- `ARCH-023-GATEWAY-001`

Gateway wiring may be finalized after both Shopify upload and Background worker contracts are architect-accepted.

## Acceptance Criteria

- [ ] Browser uploads directly to private R2 with short-lived signed PUT.
- [ ] Server credentials never reach browser.
- [ ] Source slot is allocated only at successful finalization.
- [ ] Current plan entitlement is rechecked at intent and finalization.
- [ ] File replacement is immutable/revisioned.
- [ ] Reprocess reuses existing immutable asset.
- [ ] Queue loss remains recoverable through durable PENDING state.
- [ ] No file bytes are stored in PostgreSQL.

## Validation

- [ ] focused upload/presign/finalization tests
- [ ] database transaction integration tests
- [ ] browser component tests with mocked PUT
- [ ] `npm run typecheck`
- [ ] `npm run lint`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP. Do not begin Gateway deployment.

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
