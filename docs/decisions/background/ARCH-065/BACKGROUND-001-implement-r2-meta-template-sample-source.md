---
id: ARCH-065-BACKGROUND-001
architecture_id: ARCH-065
title: implement r2 meta template sample source
task_kind: implementation
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
depends_on: []
enables: ["ARCH-065-BACKGROUND-002", "ARCH-065-SYSTEM-TEST-001"]
created: 2026-11-06
updated: 2026-11-07
---
# Implement r2 meta template sample source

## Architecture
ARCH-065; docs/architecture/ARCH-065-r2-meta-template-submission-sample.md. Coordinator moda_architect.

## Objective
Implement r2 meta template sample source using existing public-media configuration and immutable R2 infrastructure.

## Context
Meta image sample uploader currently fetches website-hosted JPEG before resumable Meta upload. Use fixed platform-owned R2 asset while preserving trusted handle boundary.

## Scope
moda-interact-background code/artifact or accepted provisioning mechanics as specified below. Site source is read-only evidence; no crossrepo runtime import.

| Existing file | Exact surface | Required change |
|---|---|---|
| moda-interact-background/src/services/meta-template-management/image-header-sample.ts | META_TEMPLATE_SAMPLE_URL/MetaImageHeaderSampleUploader/isJpeg | Replace website constant with production source injection, hash validation and bounded Meta JSON body parsing; preserve WeakSet trust. |
| moda-interact-background/src/services/meta-template-management/meta-graph.adapter.ts | MetaGraphTemplateAdapter constructor/uploadImageHeaderSample | Retain validated WABA/app token composition and inject new source without caller URL. |
| moda-interact-background/src/services/meta-template-management/service.ts | IMAGE header sample branch | Preserve supported header checks, skip source on non-image/unsupported, retain trusted handle use. |
| moda-interact-background/src/services/shop-brand-media/r2-writer.ts | putGuardedImmutableR2Object/createBrandR2S3Transport | Add bounded expectedDimensions override for platform sample, preserve brand default and guarded immutable mechanism. |
| moda-interact-background/src/services/shop-brand-media/r2-config.ts | loadShopBrandR2Credentials | Reuse endpoint/credential validation unchanged. |
| moda-interact-background/src/services/platform-configuration/consumers.ts | readR2Configuration/readShopBrandPublicMediaConfiguration | Reuse current config sources, no new key. |
| moda-interact-background/package.json | build and CLI scripts | Include packaged JPEG and add meta:sample:provision entrypoint with plan/apply/verify. |
| moda-interact-site/assets/whatsup-sample.jpeg | read-only source evidence | Copy exact source once into Background; no runtime sibling access/site deletion. |


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
- [x] Create exact NEW assets/meta-template-samples/v1/<fixedhash>.jpeg, sample-asset.ts, sample-source.ts and scripts/provision-meta-template-sample.ts; implement contract above.
- [x] Add unit/image-header-sample, existing R2 writer, package smoke and full mock source->Meta tests with zero website calls.

## Interfaces / Contracts
Fixed code-owned version1 asset metadata above; existing shopBrand.publicMedia public origin/bucket and existing R2 credential config, injected source.read, guarded R2 transport and opaque WeakSet Meta handle. No new cross-service wire package or persisted configuration key.

## Dependencies
None

## Enables
- ARCH-065-BACKGROUND-002
- ARCH-065-SYSTEM-TEST-001

## Acceptance Criteria
- [x] Create exact NEW assets/meta-template-samples/v1/<fixedhash>.jpeg, sample-asset.ts, sample-source.ts and scripts/provision-meta-template-sample.ts; implement contract above.
- [x] Add unit/image-header-sample, existing R2 writer, package smoke and full mock source->Meta tests with zero website calls.

## Validation
- [x] Background: npx vitest run tests/unit/services/meta-template-management/image-header-sample.test.ts tests/unit/services/shop-brand-media/r2-writer.test.ts plus NEW tests/unit/services/meta-template-management/sample-source.test.ts and provision-sample.test.ts; run npm run build and clean-artifact package smoke. System Test: node --test test/arch065-meta-template-sample.test.js and npm run typecheck.
- [x] Capture source/R2/Meta calls and assert deterministic matrix, zero website requests, safe failures and credential/handle canaries absent.

## Stop Condition
Finish scoped work/criteria/validation, submit report for authorized review and STOP. Explicit developer completion required. No enabled execution automatic; System Test terminal/manually invoked.

## Implementation Notes
Definition only, no upload/claim started. Use normal launcher isolated/synchronized task worktrees when requested. Preserve exact source bytes, existing default brand dimensions and Meta trust flow. Missing deployed bucket/config is explicit gap, never silent fallback or unapproved infrastructure creation. Provision task cannot fix implementation code.

## Completion Report

### Status
Complete — Attempt 1 passed developer self-review and explicitly developer-completed on 2026-11-07.

### Files Changed
18 task-owned paths recorded in f914bcc: fixed JPEG; sample-asset.ts, sample-source.ts, provision-sample.ts; image-header-sample.ts; existing r2-writer.ts; compiled provision/package/smoke scripts; tsconfig.provision.json; package.json, Dockerfile, .gitignore; focused sample/source/provision/Meta/R2 tests. No site, schema or lockfile changes.

### Work Completed
Copied exact 28251-byte 505x757 JPEG with frozen SHA256 14af14ebb7b71df4b0a32d31ba7d8df82a7d18f47e56143a4bc0b5ea46587717. Runtime source resolves existing public-media configuration per read and fetches only the fixed HTTPS origin/key using safe fetch (5MB, no redirects). Integrity/MIME/signature checks precede Meta calls; website/bundled/merchant runtime fallback absent. Existing WABA/app admission, non-image paths and WeakSet trusted-handle boundary retained.

Uploader retains finite10s/30s request deadlines through bounded8192-byte success and4096-byte failure body parsing with cancellation/reader cleanup. Safe source/provider classifications retained. Reused immutable R2 transport with optional bounded expectedDimensions; brand defaults1125x600 unchanged; client.destroy close added. Plan/apply/verify CLI validates current deployment identity, requires production-apply confirmation, reuses existing public bucket/R2 config, guards writes with exact key/conditional immutable semantics and verifies public bytes.15s R2 operation and60s total bounds include cleanup; receipts are bounded and credential-free. Transport/local DB cleanup retained. Build packages JPEG with worker/compiled CLI; Dockerfile includes new build inputs.

### Validation Results
- `npx vitest run tests/unit/services/meta-template-management/image-header-sample.test.ts tests/unit/services/shop-brand-media/r2-writer.test.ts tests/unit/services/meta-template-management/sample-source.test.ts tests/unit/services/meta-template-management/provision-sample.test.ts tests/unit/services/meta-template-management/meta-management.test.ts`: 73 passed.
- `npm run build`: passed, worker and compiled CLI.
- `npm run test:meta-sample:artifact`: passed from clean temporary compiled artifact without sibling site source/live credentials.
- Targeted ESLint on changed production modules/scripts: passed.
- `git -c core.fsmonitor=false diff --check`: passed.
Fixtures cover exact metadata/integrity, tamper/MIME/size rejection,404/redirect/private DNS,429/503,stalled success/failure bodies/body cap/cancellation, opaque handle trust, non-image skip, conditional writes/idempotency/collision, public tamper, operation/total deadlines, environment/production gates and safe receipts. No website request occurs in new source flow.

### Deviations / Assistance
Material moda_background agent assistance implemented source/tests under explicit developer authorization; root handled publication/report. Launcher synchronized canonical worktrees then set Attempt1 before report-format failure; normalized report and published claim02103b675 without incrementing. Added Dockerfile inputs and .gitignore/compiled CLI configuration as necessary artifact packaging. Git fsmonitor IPC warning worked around per-command with core.fsmonitor=false; no global configuration changed.

### Validation Limits / Unresolved Issues
No live R2 provisioning/readiness, Meta submission, deployment, Docker build or terminal System Test claimed. Docker packaging checked statically plus clean compiled artifact smoke. Follow-on provisioning must verify intended destination before worker rollout. No scoped implementation blocker remains.

### Git / VCS
Task branch: task/ARCH-065-BACKGROUND-001.
Canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-065-BACKGROUND-001.
Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-065-BACKGROUND-001.
Both dedicated worktrees use matching task branch; shared/default checkout not switched for task work, no other task worktree reused. Launcher synchronized before Attempt1; implementation baseline ada7a5450914175220ffa8d32f2c3f3924df57a0; recursive database pinned379d563f6b9ee070305e284615dddbc0b97afeb0. Claim02103b6750734f05267005564439bac3b871a319 published. Implementation f914bcc7e7b9b04a31ae77cbcd48bb97df9cdc07 pushed origin/task/ARCH-065-BACKGROUND-001. Report committed/pushed on matching parent branch, exact commit available in Git history. No submodule gitlink staged, main merge/push, enabled-task execution or live upload.

## Developer Self-Review - Passed
2026-11-07: Attempt 1 reconciled under `/moda_developer_update ARCH-065-BACKGROUND-001`. Reviewed actual implementation f914bcc7e7b9b04a31ae77cbcd48bb97df9cdc07 against all task requirements and the recorded 73-test/build/artifact-smoke/lint evidence. No source changes since that passing validation; no redundant rerun required. Implementation HEAD matches origin/task/ARCH-065-BACKGROUND-001; parent report57f8fe89f matches its published ref; both worktrees clean.

Accepted scoped implementation evidence: exact packaged JPEG/frozen metadata; configured fixed-key HTTPS safe source without fallback; source integrity before Meta I/O; existing WABA/header/WeakSet admission; finite Meta request/body bounds; reused conditional immutable R2 primitive with bounded dimension override and unchanged brand defaults; plan/apply/verify CLI using current environment/public-media policy and explicit production gate; per-operation/total deadlines, cleanup and safe receipts; compiled package and Docker inputs. No new schema/config/key or other-repository source edits. Material assigned-agent assistance and physical synchronization evidence are retained above.

Validation limits remain explicit: clean compiled artifact/local mocks establish implementation behavior; no live R2 readiness, Meta submission, Docker build, deployment or terminal System Test is claimed. Follow-on provisioning must run before new reader rollout. Required System Test commands in the combined validation section belong to the separate manual terminal task, not evidence claimed by this Background implementation review. No unresolved implementation correction found.

Status remains review, executor/claimed_at null, accepted attempt1 unchanged, completion_mode developer preserved. Explicit `/moda_developer_update ARCH-065-BACKGROUND-001 complete` remains pending. BACKGROUND-002 and SYSTEM-TEST-001 are not promoted by passing review alone; dependency-frontier reconciliation occurs on completion. No enabled task started and no main merge/push.

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

## Developer Completion Decision
2026-11-07: Developer explicitly invoked `/moda_developer_update ARCH-065-BACKGROUND-001 complete`. Durable passing review eca856769d45c547ff824e25ff293ba358532dc8 verified. Implementation f914bcc7e7b9b04a31ae77cbcd48bb97df9cdc07 matches its published task ref; both canonical worktrees clean at verification. All scoped requirements satisfied within recorded local validation limits. Accepted Attempt 1 unchanged; executor/claimed_at remain null. No main merge/push or live provisioning.

### Dependency-frontier reconciliation
BACKGROUND-002 becomes Ready at unchanged Attempt 0, unclaimed, because its sole explicit dependency is Complete. SYSTEM-TEST-001 remains Pending/manual-gated until BACKGROUND-002 provisioning is Complete. No enabled task started, upload performed or deployment readiness asserted.
