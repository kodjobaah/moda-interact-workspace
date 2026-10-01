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
status: review
priority: 52
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-023-SHOPIFY-004
enables:
  - ARCH-023-GATEWAY-001
created: 2026-09-29
updated: 2026-10-01
---

# Upload and manage Merchant Knowledge CSV and XLSX sources

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Extend the Merchant Knowledge management surface with private direct-to-R2 CSV/XLSX uploads, upload finalisation, immutable uploaded-asset replacement and Reprocess.

The browser receives only a short-lived signed PUT and asset id; server credentials remain private. A source/revision is created only after the uploaded object is verified to exist and the current plan entitlement is re-checked.

This task inherits SHOPIFY-004's activation model: plan entitlement grants file-source configuration access, while `ShopFeaturePreference` controls effective Merchant Knowledge activation. CSV/XLSX assets/sources may be configured while OFF, but OFF must not start ingestion.

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

Load current **commercial** entitlement and merchant activation state using SHOPIFY-004 services.

Require exact `(purposeKey,dataFormatKey)` currently plan-entitled and globally active. Do not require `merchantEnabled` merely to configure/upload a source.

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

Presign exactly one **create-only** PUT:

```text
PutObjectCommand
Bucket = MERCHANT_KNOWLEDGE_R2_BUCKET
Key = persisted objectKey
ContentType = validated contentType
IfNoneMatch = "*"
```

`IfNoneMatch = "*"` is mandatory. The signed request MUST fail rather than overwrite when
the generated object key already exists. The 600-second presigned URL therefore cannot be
replayed after the first successful PUT to replace the immutable original bytes.

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
    "If-None-Match": "*";
  };
  maxUploadBytes: number;
}
```

Both headers are part of the signed request contract and the browser MUST send them unchanged.

No credentials.

Do not return an R2 GET URL.

### R6 — browser upload

The UI:

1. validates size/type/extension before requesting intent;
2. requests R3 intent;
3. uses browser `fetch(uploadUrl,{method:"PUT",body:file,headers:requiredHeaders})`;
   `requiredHeaders` MUST contain the signed `Content-Type` and `If-None-Match: *` values from R5;
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
11. when Merchant Knowledge is effectively enabled, enqueue C4 best effort via SHOPIFY-004 helper; when OFF, leave the revision PENDING without enqueue.

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
10. commit; enqueue best effort only when Merchant Knowledge is effectively enabled; otherwise leave PENDING.

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
7. commit; enqueue best effort only when Merchant Knowledge is effectively enabled; otherwise leave PENDING.

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

For plan-entitled CSV/XLSX combinations, regardless of current ON/OFF preference:

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
presigned request requires signed `Content-Type` and `If-None-Match: *` headers
reusing the same object key cannot overwrite an already-created object; live R2 replay proof is owned by GATEWAY-001/SYSTEM-TEST-002
oversized file rejects
extension/contentType mismatch rejects
HeadObject missing/size mismatch rejects
new finalization creates AVAILABLE asset + source + CREATE revision atomically
replace creates new immutable asset + FILE_REPLACE revision
old ACTIVE/old asset remain on replacement
Reprocess reuses same asset
queue failure leaves PENDING durable revision
merchant disabled -> finalized/create/replace/reprocess leaves PENDING and does not enqueue
merchant enabled -> normal best-effort enqueue
abandoned PENDING_UPLOAD creates no source
browser never receives credentials/objectKey field
```

## Work Items

- [x] Add R2 server configuration/client/presigner.
- [x] Implement upload-intent transaction.
- [x] Implement browser direct PUT + SHA-256.
- [x] Implement HeadObject-backed finalization.
- [x] Implement create/replace/reprocess source lifecycle.
- [x] Extend Merchant Knowledge UI for uploads.
- [x] Add security/lifecycle tests.

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

- [x] Browser uploads directly to private R2 with short-lived create-only signed PUT requiring `If-None-Match: *`.
- [x] Server credentials never reach browser.
- [x] Source slot is allocated only at successful finalization.
- [x] Current plan entitlement is rechecked at intent and finalization; merchant OFF does not block configuration.
- [x] A presigned upload cannot overwrite an already-created object key; file replacement is immutable/revisioned through a new asset/key.
- [x] Reprocess reuses existing immutable asset.
- [x] Merchant OFF leaves PENDING work durable without ingestion; merchant ON permits processing, with queue loss recoverable through durable PENDING state.
- [x] No file bytes are stored in PostgreSQL.

## Validation

- [x] focused upload/presign/finalization tests
- [x] database transaction integration tests
- [x] browser component tests with mocked PUT
- [x] `npm run typecheck`
- [ ] `npm run lint` (run; existing unrelated repository errors remain)
- [x] `npm run build`
- [x] `git diff --check`
- [x] changed-file diagnostics clean

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP. Do not begin Gateway deployment.

## Completion Report

### Status
Ready for Review.
### Files Changed
Attempt 2 implementation changes in `moda-interact`:

- `app/services/merchant-knowledge/r2-client.server.ts`
- `app/services/merchant-knowledge/upload.server.ts`
- `tests/unit/merchant-knowledge-upload.test.ts`
- `tests/unit/merchant-knowledge-upload-form.test.tsx`
- `tests/integration/merchant-knowledge-upload.integration.test.ts`

Earlier task implementation on the same task branch remains unchanged, including the R2 configuration and upload lifecycle services/routes, Merchant Knowledge settings UI/locales, related focused tests, and AWS SDK dependency files. Parent workspace change: this task file only. No Gateway code/configuration, database schema/source changes, task index, architecture document, or submodule gitlink changes were made. Architect Review is preserved verbatim.
### Work Completed
- A1-R1: Added `IfNoneMatch: "*"` to the signed `PutObjectCommand`; the R2 client requires the literal conditional value, and upload intent returns exactly `{ "Content-Type": validatedContentType, "If-None-Match": "*" }`. The browser already forwarded generic `requiredHeaders` unchanged; its mocked PUT assertion now proves both values arrive unchanged. Presigner coverage inspects `X-Amz-SignedHeaders` and verifies lowercase `if-none-match`. Existing asset creation, finalization, replacement, and Reprocess lifecycle remains unchanged.
- Deployed CORS/preflight and live replay validation remain owned by amended GATEWAY-001/SYSTEM-TEST-002; no Gateway implementation was added here.
- A1-R3: Made the PostgreSQL integration fixture create the opt-in Feature row when absent from the accepted migration state, matching the neighboring Merchant Knowledge lifecycle fixture; the existing purpose/format catalogue remains migration-backed. The prior ACTIVE revision fixture now satisfies the database content metadata constraint.
### Validation Results
- Focused upload service/presigner and browser component tests: 14 passed across `tests/unit/merchant-knowledge-upload.test.ts` and `tests/unit/merchant-knowledge-upload-form.test.tsx`.
- Disposable PostgreSQL transaction integration: 4 passed, 0 skipped, using `MODA_DISPOSABLE_INTEGRATION=1` and the per-command Colima socket settings. Testcontainers started PostgreSQL, deployed the accepted migrations, and executed intent/source-slot, cross-shop rejection, create/replace/reprocess immutability, and OFF/queue-failure transaction cases.
- `npm run typecheck`: passed.
- Changed-file ESLint: passed for all five Attempt 2 files; the existing TypeScript 5.9.3 versus parser `<5.4.0` support warning remains.
- Changed-file diagnostics: no errors in all five Attempt 2 files.
- `npm run build`: passed for client and SSR bundles; existing dependency annotation and large-chunk warnings remain.
- `git diff --check`: passed.
- Full `npm run lint`: run; reports the same 17 unrelated repository lint errors documented in Attempt 1. No changed file is among those errors; changed-file ESLint is clean.
### Deviations
- None for implementation scope. Required `If-None-Match: *` was implemented as directed by A1-R1. Audit findings from the earlier dependency installation remain outside this task's scope.
### Assumptions
- `If-None-Match: *` is signed by the AWS SDK S3 presigner as the lowercase `if-none-match` request header. Attempt 2 presigner coverage confirms that header is listed in `X-Amz-SignedHeaders`; browser component coverage confirms the required header is forwarded unchanged.
- Gateway CORS allowance and deployed replay rejection are validated by GATEWAY-001/SYSTEM-TEST-002, not this task.
### Unresolved Issues
- None blocking this review submission. Full repository lint retains 17 unrelated baseline errors; Gateway deployment/replay evidence remains assigned to its owning tasks.
### Architectural Concerns
- None newly identified. A1-R1, A1-R2, and A1-R3 are implemented with the evidence above.
- Attempt 2 launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-SHOPIFY-005`, branch `task/ARCH-023-SHOPIFY-005`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-SHOPIFY-005`, branch `task/ARCH-023-SHOPIFY-005`. At the start boundary, parent and implementation task-remote fast-forwards were both not needed; parent and implementation already contained current `origin/main`. Launcher-synchronized parent HEAD was `ef949a7a797bec37ad6f602bf52b27585be63b82`, followed by pushed Attempt 2 claim commit `79bbde8554d7ae5c260b86664810276b3b29caa0`; implementation prepared HEAD was `7c97d90cc9ae0eeacd4aa6121ef7801342437d7f`. Recursive submodule sync/update passed; `database` was clean at `a5e633a6ed1631e64510b936b2b19e8e50c7a5de`. Dependency ARCH-023-SHOPIFY-004 was complete. Claim: executor `copilot`, Attempt 2, claimed at `2026-10-01T09:31:32Z`.
- Submitted implementation HEAD: `244f3f60035c3651168571869234ab23654854d3`, pushed to `origin/task/ARCH-023-SHOPIFY-005`. Parent report is being submitted on the same task branch from claim HEAD `79bbde8554d7ae5c260b86664810276b3b29caa0`; its report commit will be the pushed parent branch HEAD at submission.

## Architect Review

### Review Status
Changes Requested — Attempt 1

### Review Notes

The upload implementation is substantially architecture-conformant, but Attempt 1 cannot be accepted because the exact R5 signed-PUT contract contradicts D23's immutable-original requirement.

**A1-R1 — make every presigned upload create-only.** The current `PutObjectCommand` signs only `Content-Type`. Because the URL remains valid for 600 seconds, the same signed PUT can be replayed against the same generated key after finalization and replace the bytes behind an `AVAILABLE` asset. Attempt 2 MUST:

1. add `IfNoneMatch: "*"` to the signed `PutObjectCommand`;
2. return exact required browser headers `{ "Content-Type": <validated>, "If-None-Match": "*" }`;
3. keep the browser generic `requiredHeaders` forwarding and prove both signed headers are sent unchanged;
4. add focused presigner/contract regressions proving `if-none-match` is a signed request header and the required-header response is exact;
5. preserve the current asset/source/finalization lifecycle otherwise; and
6. leave deployed Cloudflare CORS/replay validation to the amended `GATEWAY-001` / `SYSTEM-TEST-002` contracts.

Do not solve this by shortening the URL lifetime, deleting/replacing the object during finalization, changing object keys after PUT, proxying bytes through Moda, or trusting `HeadObject`/SHA metadata as an overwrite guard.

**A1-R2 — durable launcher/worktree evidence is incomplete.** The Completion Report states that the launcher prepared dedicated worktrees and that no shared checkout was reused, but it does not record the exact launcher-resolved parent/implementation physical paths and the four start-of-attempt synchronization outcomes required by `docs/agent-worktree-isolation-policy.md`. Attempt 2 MUST be reclaimed through `/moda-task ARCH-023-SHOPIFY-005` and record those exact values, recursive submodule status and final submitted heads. A later advance of `origin/main` is not itself a defect; the report must prove synchronization at the Attempt 2 start boundary.

**A1-R3 — run the required PostgreSQL transaction proof.** The four database integration cases were skipped because no container runtime was available. Attempt 2 MUST execute the task-owned disposable PostgreSQL cases against the accepted migrations before returning to review. If a safe disposable runtime is still unavailable, return the task blocked rather than treating skipped transaction coverage as acceptance evidence.

No other implementation-source correction is requested unless synchronization or refreshed validation exposes a regression. The repository-wide lint baseline and npm audit findings are not blockers for this task because changed-file validation is clean and dependency remediation is out of scope.

### Reviewed Files

Reviewed the SHOPIFY-005 task/report, R2 client/presigner, upload intent/finalization service, browser upload form, focused upload/action/UI tests, canonical ARCH-023 D23 upload contract, and GATEWAY-001 R2/CORS deployment contract.

### Validation Reviewed

Accepted as supporting evidence: task-recorded typecheck, production build, changed-file ESLint/diagnostics, locale validation, 25 focused passing tests and `git diff --check`. The four skipped PostgreSQL cases remain required for Attempt 2.

### Architecture Conformance

Changes Requested. The current unconditional presigned PUT does not preserve immutable original bytes for the lifetime of the URL. The corrected contract uses R2/S3 conditional `If-None-Match: *` on `PutObject`, with matching exact-origin CORS allowance and deployed replay proof.

### Follow-up

Return the same task to Ready at Attempt 1 with claim cleared. Reclaim normally as Attempt 2. `GATEWAY-001` and `SYSTEM-TEST-002` are amended by this architect reconciliation to require `If-None-Match` CORS/preflight and live replay rejection. GATEWAY-001 remains Pending behind SHOPIFY-005 and its other prerequisites.
