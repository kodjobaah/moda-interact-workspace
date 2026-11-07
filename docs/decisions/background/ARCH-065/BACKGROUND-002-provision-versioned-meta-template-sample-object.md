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
status: complete
priority: 50
executor: null
claimed_at: null
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
- [x] Verify prerequisite accepted Complete and exact artifact metadata/hash; no implementation fixes or repeated code tests.
- [x] Run plan, apply, verify and rerun apply using accepted CLI; public fetch hash exact, second apply UNCHANGED/zero PUT; record environment/config destination and bounded receipts.
- [x] If bucket/access/public origin missing, stop with exact provisioning failure and return to architect; do not create infrastructure or fallback to website.

## Interfaces / Contracts
Fixed code-owned version1 asset metadata above; existing shopBrand.publicMedia public origin/bucket and existing R2 credential config, injected source.read, guarded R2 transport and opaque WeakSet Meta handle. No new cross-service wire package or persisted configuration key.

## Dependencies
- ARCH-065-BACKGROUND-001

## Enables
- ARCH-065-SYSTEM-TEST-001

## Acceptance Criteria
- [x] Verify prerequisite accepted Complete and exact artifact metadata/hash; no implementation fixes or repeated code tests.
- [x] Run plan, apply, verify and rerun apply using accepted CLI; public fetch hash exact, second apply UNCHANGED/zero PUT; record environment/config destination and bounded receipts.
- [x] If bucket/access/public origin missing, stop with exact provisioning failure and return to architect; do not create infrastructure or fallback to website.

## Validation
- [x] Accepted artifact release/provision mechanics only: plan/apply/verify/rerun receipts and exact public hash. Do not rerun implementation unit/integration tests, lint/build/typecheck or modify runtime source.
- [x] Receipt contains environment/destination/fixed hash and no credentials; same asset idempotent, no live Meta call.

## Stop Condition
Finish scoped work/criteria/validation, submit report for authorized review and STOP. Explicit developer completion required. No enabled execution automatic; System Test terminal/manually invoked.

## Implementation Notes
Definition only, no upload/claim started. Use normal launcher isolated/synchronized task worktrees when requested. Preserve exact source bytes, existing default brand dimensions and Meta trust flow. Missing deployed bucket/config is explicit gap, never silent fallback or unapproved infrastructure creation. Provision task cannot fix implementation code.

## Completion Report

### Status
Complete — Attempt 1 accepted and explicitly developer-completed on 2026-11-07.

### Work Completed / Validation
Accepted BACKGROUND-001 source f914bcc incorporated into synchronized implementation baseline eb673898dd911ca78e1ba96234deec816ac10bea. Used its previously built and validated dist-cli artifact (from canonical BACKGROUND-001 worktree) from BACKGROUND-002 execution directory; did not rebuild/retest or modify runtime source. CLI validates packaged exact asset before each operation. Ran Node bootstrap with canonical MODA_WORKSPACE_ROOT, then accepted compiled scripts/provision-meta-template-sample.js with `--environment development --mode plan`, `--mode apply`, `--mode verify`, and `--mode apply` in that order. Every run exited0. Apply public validation and independent verify matched frozen SHA256/28251 bytes; second apply UNCHANGED means guarded HEAD matched and no PUT executed. Existing public bucket used; private R2 credential bucket was not destination. No Meta calls, new infrastructure, production override or deployment.

### Bounded Receipts
```jsonl
{"schemaVersion": 1, "environment": "development", "assetVersion": 1, "objectKey": "platform/whatsapp/template-submission-samples/v1/14af14ebb7b71df4b0a32d31ba7d8df82a7d18f47e56143a4bc0b5ea46587717.jpeg", "sha256": "14af14ebb7b71df4b0a32d31ba7d8df82a7d18f47e56143a4bc0b5ea46587717", "sizeBytes": 28251, "contentType": "image/jpeg", "bucketName": "moda-interact-shop-brands", "publicOrigin": "https://shop-brands.modainteract.com", "mode": "plan", "outcome": "PLANNED"}
{"schemaVersion": 1, "environment": "development", "assetVersion": 1, "objectKey": "platform/whatsapp/template-submission-samples/v1/14af14ebb7b71df4b0a32d31ba7d8df82a7d18f47e56143a4bc0b5ea46587717.jpeg", "sha256": "14af14ebb7b71df4b0a32d31ba7d8df82a7d18f47e56143a4bc0b5ea46587717", "sizeBytes": 28251, "contentType": "image/jpeg", "bucketName": "moda-interact-shop-brands", "publicOrigin": "https://shop-brands.modainteract.com", "mode": "apply", "outcome": "UPLOADED"}
{"schemaVersion": 1, "environment": "development", "assetVersion": 1, "objectKey": "platform/whatsapp/template-submission-samples/v1/14af14ebb7b71df4b0a32d31ba7d8df82a7d18f47e56143a4bc0b5ea46587717.jpeg", "sha256": "14af14ebb7b71df4b0a32d31ba7d8df82a7d18f47e56143a4bc0b5ea46587717", "sizeBytes": 28251, "contentType": "image/jpeg", "bucketName": "moda-interact-shop-brands", "publicOrigin": "https://shop-brands.modainteract.com", "mode": "verify", "outcome": "VERIFIED"}
{"schemaVersion": 1, "environment": "development", "assetVersion": 1, "objectKey": "platform/whatsapp/template-submission-samples/v1/14af14ebb7b71df4b0a32d31ba7d8df82a7d18f47e56143a4bc0b5ea46587717.jpeg", "sha256": "14af14ebb7b71df4b0a32d31ba7d8df82a7d18f47e56143a4bc0b5ea46587717", "sizeBytes": 28251, "contentType": "image/jpeg", "bucketName": "moda-interact-shop-brands", "publicOrigin": "https://shop-brands.modainteract.com", "mode": "apply", "outcome": "UNCHANGED"}
```

### Deviations / Git Evidence
First runtime bootstrap lacked explicit workspace root; no CLI/upload ran, corrected by exporting canonical MODA_WORKSPACE_ROOT. No secret inspection or credential output. No implementation code changes. Launcher synchronized canonical task branches and set Attempt1 before report-format error; normalized report and published durable claim5149de362. Parent worktree /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-065-BACKGROUND-002; implementation /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-065-BACKGROUND-002; both task/ARCH-065-BACKGROUND-002. Implementation eb673898dd911ca78e1ba96234deec816ac10bea published on matching task ref. Source artifact remained in prior accepted task worktree, not reused as this task's implementation checkout. Shared checkouts not switched; no gitlink staged or main merge/push. No unresolved provisioning failures.

## Architect Review
### Review Status
Accepted — Attempt1, 2026-11-07 under explicit developer authority to review/complete if passing.
### Review Notes
Actual accepted CLI receipts establish configured development destination, guarded initial upload, exact public bytes and idempotent rerun. No code fixes/retests or infrastructure changes performed. All scoped provisioning criteria satisfied; no production/deployment/Meta-send claim. Existing implementation integrity and guarded primitive establish zero PUT for UNCHANGED receipt.
### Validation Reviewed
Four successful CLI outcomes above, fixed asset integrity, public hash verification and bounded credential-free receipts.
### Architecture Conformance
Existing public-media configuration/bucket, fixed immutable platform key and accepted provisioning primitive preserved. No fallback or merchant/private namespace substitution.

## Developer Completion Decision
2026-11-07: User explicitly authorized acceptance/completion if passing. Review passes on actual provisioning evidence. Complete at unchanged Attempt1; executor/claimed_at null. System Test becomes dependency-ready but remains manual-gated; no test execution started.

## Dependency Reconciliation - 2026-11-07
BACKGROUND-001 Attempt 1 explicitly developer-completed after passing review. Sole dependency satisfied; Ready at unchanged Attempt 0, executor/claimed_at null. Accepted CLI source f914bcc7e7b9b04a31ae77cbcd48bb97df9cdc07 is published on implementation task/ARCH-065-BACKGROUND-001 and must be incorporated before provisioning. No provisioning execution or upload performed by this reconciliation.

## Explicit Completion Reconfirmation - 2026-11-07
Developer invoked `/moda_developer_update ARCH-065-BACKGROUND-002 complete`. Existing Accepted review and completion65d4a69a0 verified; no required criterion incomplete. Status remains Complete, accepted Attempt1 unchanged, executor/claimed_at null. Implementation eb673898dd911ca78e1ba96234deec816ac10bea and parent65d4a69a01f09b91257c0d87868bc69cae313753 matched their published task refs with clean canonical worktrees. Existing successful plan/apply/verify/UNCHANGED receipts retained; no upload or validation rerun.

Dependency-frontier recheck: SYSTEM-TEST-001 task record on this completion branch is Ready at Attempt0, unclaimed and manual-gated, with both explicit dependencies Complete. Launcher may still resolve Pending from an unintegrated primary snapshot; this does not authorize changing main or starting System Test. No main merge/push or new attempt.
