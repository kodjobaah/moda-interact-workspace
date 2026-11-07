---
id: ARCH-065-BACKGROUND-002
architecture_id: ARCH-065
title: provision versioned meta template sample object
task_kind: publication
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 50
executor: developer
claimed_at: 2026-11-07T03:36:15Z
attempt: 1
depends_on: ["ARCH-065-BACKGROUND-001"]
enables: ["ARCH-065-SYSTEM-TEST-001"]
created: 2026-11-06
updated: 2026-11-07
---
# Provision versioned meta template sample object

## Architecture
ARCH-065; docs/architecture/ARCH-065-r2-meta-template-submission-sample.md. Coordinator moda_architect.

## Objective
Provision versioned meta template sample object using existing public-media configuration and immutable R2 infrastructure.

## Context
Meta image sample uploader currently fetches website-hosted JPEG before resumable Meta upload. Use fixed platform-owned R2 asset while preserving trusted handle boundary.

## Scope
moda-interact-background code/artifact or accepted provisioning mechanics as specified below. Site source is read-only evidence; no crossrepo runtime import.

| Existing file | Exact surface | Required change |
|---|---|---|
| moda-interact-background/package.json | accepted meta:sample:provision script | Release/provision mechanics only: execute accepted artifact CLI plan/apply/verify in development with existing config, record receipts. |


## Out of Scope
Merchant header substitution, private knowledge bucket, Admin authoring sample PNG records, new config/schema/bucket infrastructure, fallback website URL and unrequested production upload/deployment.

## Requirements
## Exact asset and ownership decision
Move Meta template submission IMAGE header sample source off website hosting. Existing source `moda-interact-site/assets/whatsup-sample.jpeg` is 28251 bytes, JPEG 505x757, SHA-256 `14af14ebb7b71df4b0a32d31ba7d8df82a7d18f47e56143a4bc0b5ea46587717`. During implementation COPY these exact bytes into NEW Background `assets/meta-template-samples/v1/14af14ebb7b71df4b0a32d31ba7d8df82a7d18f47e56143a4bc0b5ea46587717.jpeg`; package it with the Background artifact. Do not delete the site asset or change other references. Runtime never reads a sibling site directory. Add NEW `src/services/meta-template-management/sample-asset.ts` with frozen version1 metadata (hash,size,width,height,contentType image/jpeg,filename moda-whatsapp-template-sample.jpeg,objectKey below), no configurable URL/key/asset mode.

Object key is exactly `platform/whatsapp/template-submission-samples/v1/14af14ebb7b71df4b0a32d31ba7d8df82a7d18f47e56143a4bc0b5ea46587717.jpeg`. This is platform-owned sample namespace, not merchant ShopBrand header images, Admin template-samples PNG role records or private Merchant Knowledge objects. Do not insert ShopBrand/merchant rows or substitute merchant header data. Asset is public non-customer sample; reader uses existing validated shopBrand.publicMedia.publicOrigin + fixed key. Bucket is existing shopBrand.publicMedia.bucketName (default moda-interact-shop-brands; publicOrigin default https://shop-brands.modainteract.com), environment resolved from current platform configuration. Do not hardcode deployment defaults over configured values.

Existing Admin platform configuration SUPER_ADMIN controls already manage publicOrigin/bucketName; no new Admin screen, configuration key/schema, Shared package or bucket is needed. Provisioner gets R2 endpoint/accessKeyId/secretAccessKey via existing readR2Configuration and loadShopBrandR2Credentials, then uses public-media bucket from policy; NEVER use private readR2Configuration.bucket for this asset. Runtime source reader needs public origin only, not R2 credentials. Config changes do not prove delivery; verify exact object before activation/worker rollout. No arbitrary source URL from template, merchant, operator CLI or model.

## Exact implementation and API composition
Replace META_TEMPLATE_SAMPLE_URL constant with injected sample source `read():Promise<{bytes:Buffer;declaredContentType:'image/jpeg'}>`; NEW `createProductionMetaTemplateSampleSource` resolves readShopBrandPublicMediaConfiguration per upload and constructs exact URL using URL(fixedKey, validated origin). Reuse createSafeImageFetcher({maxBytes:5000000,maxRedirects:0}); current fetcher has bounded deadline/DNS/IP restrictions. Require HTTPS exact configured origin/fixed path and no query/userinfo/redirect; compare resulting bytes length exactly28251, SHA256 exactly frozen hash, declared MIME image/jpeg and JPEG signature/EOI matching existing isJpeg. Do not transform/recompress bytes. Invalid/hash mismatch/missing config/object is explicit blocked/unavailable failure; zero Meta upload calls until source validated. No fallback to website, bundled runtime bytes, merchant image, arbitrary R2 key or stale cache. Package bytes serve provisioning only; runtime fetches public R2 object.

MetaImageHeaderSampleUploader constructor retains injectable request boundary and adds injectable sample source, defaulting production factory; MetaGraphTemplateAdapter composition continues calling it from uploadImageHeaderSample after active configured WABA/app credentials admission. Existing image-header-sample.ts upload input/app validation, Meta resumable session POST and byte upload, file type/length/name and returned opaque-handle validation remain unchanged. Preserve module-private WeakSet trust; never treat URL/string/foreign object as trusted Meta handle. Header NONE/TEXT and unsupported compiled header format follow existing service path, never fetch/provision sample or upload. A valid sample does not bypass supported component validation or WABA binding.

Preserve 5,000,000-byte source safety maximum and fetch deadline. Exact frozen asset size/hash adds stronger integrity. Meta session10s and upload30s remain finite; enforce same deadlines through response body parsing, bounded8192-byte success JSON bodies for session/handle and bounded4096-byte failure bodies; preserve current retry/outcome classifications (transient/uncertain vs blocked) without blindly replaying create. Source404/hash/MIME/unsupported is blocked with fixed reason; R2/network timeout/429/5xx unavailable/retryable using existing safe MetaManagementError path. Request cancellation propagates and no raw credentials/source URL/Meta handle/provider body in new logs. Reuse existing Shared structured logger only for bounded asset version/hash/stage/reason, no generic logging copy.

## Immutable provisioning primitive and package path
Reuse createBrandR2S3Transport, loadShopBrandR2Credentials and putGuardedImmutableR2Object; do not create another S3 client/signing/HEAD-PUT engine. Current helper hardcodes1125x600, so add optional caller-owned `expectedDimensions:{width:number;height:number}` input, default1125x600 for existing callers. Validate positive safe bounded dimensions <=40000000 pixels then compare verified image; platform sample passes505x757. Existing brand wrapper and merchant contracts remain1125x600, no image-policy weakening or fake dimensions. Preserve acceptsKey strict predicate, SHA validation, conditional IfNoneMatch:* PUT, immutable cache header, ContentType/Length/sha256 metadata HEAD comparison and collision rejection. Same asset rerun HEAD matches ->zero PUT. Existing differing object metadata/content at fixed key fails, never overwrite/delete. Verify public GET hash after HEAD/PUT; HEAD alone cannot prove public body.

NEW `scripts/provision-meta-template-sample.ts` uses compiled module entrypoint/package script `meta:sample:provision` with arguments --environment <existing environment> --mode plan|apply|verify and explicit --confirm-production for production apply. No URL/bucket/key/file override flags. Environment must equal trusted current deployment identity; config is read from matching current platform config, no cross-env fallback. Default mode plan: local asset integrity + resolved nonsecret destination plan only, no upload/Meta calls. apply finite total60s, guarded R2 operations deadline15s each including SDK maxAttempts2, then public fetch/hash verify. verify finite public GET/hash with optional HEAD, no writes. Add optional close():void to existing BrandR2Transport and implement it with client.destroy() in createBrandR2S3Transport; provisioning finally closes this transport and local DB handles, runtime existing callers remain compatible. Print bounded JSON receipt `{schemaVersion:1,environment,assetVersion:1,objectKey,sha256,sizeBytes,contentType,bucketName,publicOrigin,mode,outcome:'PLANNED'|'UPLOADED'|'UNCHANGED'|'VERIFIED'|'FAILED',reasonCode?}`; no credentials or Meta handles. File packaging resolved relative import.meta.url/process artifact root, not cwd sibling repo path; package smoke test from clean temporary artifact includes JPEG.

## Provisioning gate, rollout and ownership
Three tasks: Background implementation/package/provision CLI; separately gated Background provisioning task; terminal System Test. No Gateway task: no bucket/topology creation; existing configured public-media bucket/origin must exist. Missing bucket/access/public route is explicit provisioning failure, not authorization to change infrastructure. Provisioning task uses already accepted CLI to plan/apply/verify target development environment using authorized existing credentials, records receipt and rerun zero PUT. Production upload/deployment not inferred from task definition; explicit production confirmation required. No actual live upload in this architecture authorship.

Compatible rollout: accept implementation/artifact, run asset provision+public verification per intended environment BEFORE deploying new reader/activating template image submissions. New reader has no website fallback; missing R2 readiness blocks submissions with safe explicit error. Rollback to prior known reader version is a deliberate application rollback, never hidden runtime fallback; keep immutable object, do not delete to roll back. Public-media config changes require re-provision/verify at new destination before switching workers. Existing merchant/header and Admin authoring sample namespaces untouched. No DB migration/new config. Runtime observability remains existing service logging/failure classification; no generic metric/tracing work.

## Deterministic acceptance matrix
Exact packaged JPEG hash/dimensions/size pass; modified bytes, HTML/PNG/empty/oversize/MIME mismatch reject before Meta network. Public404/redirect/private DNS/unavailable origin/timeout fail with bounded safe classification, website request count always0. Valid R2 sample produces existing Meta session+bytes upload+trusted WeakSet handle; forged handle/string/URL rejected. NONE/TEXT/unsupported headers perform zero sample fetch/Meta sample upload. WABA/token/app admission unchanged. R2 identical HEAD yields zero PUT, absent yields one conditional PUT then HEAD+public verify, collision/concurrent conditional conflict uses existing safe recheck no overwrite. Secret/error/Meta-handle canaries absent from receipts/logs. Worker startup/import performs zero config/network I/O. Clean packaged artifact provision plan works without sibling site source. System test uses real composition with disposable mock R2 public HTTP and mock Meta; live Meta submission is not required or performed by definition.

## Work Items
- [ ] Verify prerequisite accepted Complete and exact artifact metadata/hash; no implementation fixes or repeated code tests.
- [ ] Run plan, apply, verify and rerun apply using accepted CLI; public fetch hash exact, second apply UNCHANGED/zero PUT; record environment/config destination and bounded receipts.
- [ ] If bucket/access/public origin missing, stop with exact provisioning failure and return to architect; do not create infrastructure or fallback to website.

## Interfaces / Contracts
Fixed code-owned version1 asset metadata above; existing shopBrand.publicMedia public origin/bucket and existing R2 credential config, injected source.read, guarded R2 transport and opaque WeakSet Meta handle. No new cross-service wire package or persisted configuration key.

## Dependencies
- ARCH-065-BACKGROUND-001

## Enables
- ARCH-065-SYSTEM-TEST-001

## Acceptance Criteria
- [ ] Verify prerequisite accepted Complete and exact artifact metadata/hash; no implementation fixes or repeated code tests.
- [ ] Run plan, apply, verify and rerun apply using accepted CLI; public fetch hash exact, second apply UNCHANGED/zero PUT; record environment/config destination and bounded receipts.
- [ ] If bucket/access/public origin missing, stop with exact provisioning failure and return to architect; do not create infrastructure or fallback to website.

## Validation
- [ ] Accepted artifact release/provision mechanics only: plan/apply/verify/rerun receipts and exact public hash. Do not rerun implementation unit/integration tests, lint/build/typecheck or modify runtime source.
- [ ] Receipt contains environment/destination/fixed hash and no credentials; same asset idempotent, no live Meta call.

## Stop Condition
Finish scoped work/criteria/validation, submit report for authorized review and STOP. Explicit developer completion required. No enabled execution automatic; System Test terminal/manually invoked.

## Implementation Notes
Definition only, no upload/claim started. Use normal launcher isolated/synchronized task worktrees when requested. Preserve exact source bytes, existing default brand dimensions and Meta trust flow. Missing deployed bucket/config is explicit gap, never silent fallback or unapproved infrastructure creation. Provision task cannot fix implementation code.

## Completion Report

### Status

In Progress — Attempt 1; authorized development provisioning.
### Files Changed
None
### Work Completed
None
### Validation Results
Definition only.
### Deviations
None
### Assumptions
Existing public-media bucket/origin and credential sources can be provisioned with current authorized runtime configuration; verify in provisioning task.
### Unresolved Issues
No implementation-blocking design question. Live object/bucket readiness not yet verified or claimed.
### Architectural Concerns
Return actual infrastructure access/config gap rather than inventing new storage.

## Architect Review
### Review Status
Pending
### Review Notes
Definition inspected against source bytes, uploader, public-media configuration and R2 helper guard; no implementation reviewed.
### Reviewed Files
Verified touchpoints above.
### Validation Reviewed
Definition metadata/path/hash evidence only.
### Architecture Conformance
Background owns runtime/artifact/provision; no duplicate generic R2 runtime or merchant sample substitution.
### Follow-up
None

## Dependency Reconciliation - 2026-11-07
BACKGROUND-001 Attempt 1 explicitly developer-completed after passing review. Sole dependency satisfied; Ready at unchanged Attempt 0, executor/claimed_at null. Accepted CLI source f914bcc7e7b9b04a31ae77cbcd48bb97df9cdc07 is published on implementation task/ARCH-065-BACKGROUND-001 and must be incorporated before provisioning. No provisioning execution or upload performed by this reconciliation.
