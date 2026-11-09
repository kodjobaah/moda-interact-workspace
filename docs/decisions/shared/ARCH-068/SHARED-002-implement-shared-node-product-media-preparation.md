---
id: ARCH-068-SHARED-002
architecture_id: ARCH-068
title: Implement reusable Node product image preparation
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on: ['ARCH-068-SHARED-001']
enables: ["ARCH-068-SHARED-003"]
created: 2026-11-09
updated: 2026-11-09
---
# Implement reusable Node product image preparation

## Architecture and objective
Implement the owned portion of [binding ARCH-068](../../../architecture/ARCH-068-optional-conversation-product-image.md). The entire contract is normative, including exact schemas, transport/failure rules, initialization, rollout and acceptance matrix. Read it before execution.

## Context and scope
New explicit entrypoint `@modainteract/moda-interact-shared/commerce/presentation/node`, backed by `src/commerce/presentation/node/index.ts`, product-image.ts and extracted generic media modules. Add package exports, tsup entry, declaration output, required AWS S3/sharp runtime dependencies and package-lock. Browser presentation barrel must not export/import the Node entrypoint.

Public `prepareConversationProductImage({source,publicOrigin,bucketName,r2,signal})` returns READY with ConversationPreparedProductImage or OMITTED with reason CONFIGURATION_UNAVAILABLE|UNSAFE_IMAGE_SOURCE|SOURCE_UNAVAILABLE|IMAGE_TRANSFORM_FAILED|R2_UNAVAILABLE|PUBLIC_IMAGE_UNAVAILABLE|MEDIA_DEADLINE. r2 is `{endpoint,accessKeyId,secretAccessKey}` server-only; source is the SOURCE result above. Dependency-injected fetch/transform/S3/probe implementations and clock enable deterministic tests. Never log input config, URLs containing query strings, raw images or provider bodies.

Extract common mechanics from Background `services/shop-brand-media/{contracts,safe-fetch,image-transformer,metadata-verifier,public-probe,r2-writer}.ts`, `services/merchant-knowledge-network-policy.ts` and `services/recovery-product-media/product-image-transformer.ts` where needed; remove application-specific imports from Shared. Keep initial-outreach attempt selection/fencing/key format and host configuration outside Shared. Background consumer replaces extracted generic bodies with reexports/adapters after publication; preserve initial brand/outreach byte/security behavior with golden vectors. Do not copy generic mechanics into Commerce.

Image processing uses existing safe image fetch semantics (DNS/private/loopback/link-local/cloud-metadata rejection on initial and every redirected URL, pinned address/TLS verification; HTTPS only), max3 redirects, max10MiB source bytes, existing decompression/pixel/SVG restrictions; never loosen current stricter restrictions. Existing product transform produces 1125x600 JPEG with its existing contain/white-padding/quality policy, <5MiB; use golden input/output metadata and preserve behavior. Key exactly `conversation-products/v1/<sha256(shopId)>/<sha256(stableJson({productId,variantId}))>/<sha256(transformedBytes)>.jpg`, UTF8 canonical input and lowercase hex. Public URL is validated publicOrigin + '/' + objectKey, never source URL/signed URL. Use existing immutable If-None-Match put and HEAD metadata equality (type,length,hash) and public byte/hash probe; an existing identical object is reuse, a conflicting object is omission. No source URL secrets in key. Abort all stages on caller signal; close owned transports. No background jobs, new media table, cleanup job, bucket/public ACL mutation or fallback to merchant source URL.

Preparation budget is min(5000ms, remaining turn deadline minus1000ms); <=0 means omit without I/O. Hosts create one child signal covering fetch/transform/upload/probe and retain their original turn deadline. Source selection once, one preparation attempt per turn; no retries/modeltool budget increment for internal media preparation. Shared returns bounded stage/reason; hosts extend existing domain logs with shop/conversation/run, pair, omission/stage/duration and plan kind only.

## Interfaces and contracts
The named exported schemas/APIs and exact JSON shapes in the binding contract are authoritative. Existing v1 template hashes/legacy records remain compatible. No clothing-specific fields/model image URL or Meta recovery contract extension.

## Work Items
- [x] Verify dependencies and current owned source against binding touch points.
- [x] Implement every requirement in the owned scope and binding contract.
- [x] Add deterministic success/failure/compatibility tests specified above.
- [x] Run declared repository validation and record exact evidence.
- [x] Publish implementation and parent report on mirrored task branches for review.

## Dependencies
ARCH-068-SHARED-001

## Acceptance criteria
All owned scope above is complete, exact contract tests pass and no TODO/placeholder or unresolved cross-service choice remains. For this Shared task, validate its owned source and built public exports; publication evidence is owned by SHARED-003; no sibling source imports/copied mechanics. Record actual changed paths and checks. Preserve existing grounded text, product identity, moderation/send fences, initial/proactive Meta flows.

## Out of Scope
No redesign of aspects 1 and 3, Meta submission/WABA validation, inventory write, unrelated cleanup, budget increase, production mutation or automatic live initializer.

## Agent execution and review
Execution is owned by the assigned agent, not a human developer. Use /moda-task with canonical isolated parent/implementation worktrees and mirrored task branches. Do not claim on authoring. Implement only this repository portion; use published Shared APIs. If an actual source conflict contradicts the exact binding contract, report it to the architect with path/symbol/evidence; do not invent a replacement architecture or leave a placeholder. No main merge/push, production mutation, real send or live initializer execution is part of this task.

## Completion Report

### Status

Ready for Review — Attempt1 implemented and published by moda_shared/codex. No architect acceptance/completion decision is made by this implementation agent; execution_mode agent/completion_mode automatic remain unchanged.

### Accepted dependency and extraction provenance

Accepted SHARED001 source0b06467c37cbc4cd6ce67fcfa6e9c3fd7da66822 is already an ancestor of the prepared implementation baseline df87e770a56db61617f1d9c2fd9397005add692d, verified through Git ancestry. The pure contract/browser implementation is retained without modification. No assumption of missing main integration, copied contract or extra integration merge was needed.

Immutable Background extraction source **db32bdf1e69944b0a15f7c76400f222f00244be4**. Every source file was read with git show at that commit, not a mutable working copy. Source path/file SHA256/moved-symbol map is committed in src/commerce/presentation/node/EXTRACTION.md. Before original-regression execution, the eight relevant current Background files matched that immutable source. Its sharp0.35.4/@aws-sdk/client-s3 3.1143.0 exact versions and applicable sharp native-package lock versions match the new Shared dependencies.

Relocated symbols: createSafeImageFetcher and pinned HTTPS/DNS/stream ports; normalizeIpAddress/isPublicIpAddress/resolveAllDnsAnswers/resolveAndValidateDestination/addressesMatch/createPinnedLookup and original network error types/codes; verifyEncodedBrandImage; assertSelfContainedSvg/createShopBrandImageTransformer; createOutreachProductImageTransformer; createBrandR2S3Transport/BrandR2Transport/sanitizeR2ProviderMessage/putGuardedImmutableR2Object/cache-control/bucket validation; createShopBrandPublicMediaProbe; transitive generic media constants/errors/image/fetch/transform/probe ports. Compatibility names/error codes are retained. Host acquisition policy constants, configuration lookup/credential loading, brand/outreach key adapters, domain normalizers, source generations, recovery/attempt/recipient fences and orchestration stay Background.

The product preset has optional AbortSignal plumbing around Sharp metadata/encoding and cancellation checks; its encoder operations remain unchanged. Product1125×600 JPEG contain/white padding, rotate/sRGB/metadata stripping, quality ladder86/76/66/56/46, 1MiB quality target and strict<5MiB bound match original. Brand presets remain unchanged. No intentional byte change: four fixed source golden outputs match original encoded SHA256, size, MIME and dimensions. The golden was generated from temporary modules populated with the immutable ORIGINAL source, using the same pinned native dependency versions; the temporary originals were removed. Expectations were not regenerated from the Shared implementation.

### Final behavior

Public Node entrypoint @modainteract/moda-interact-shared/commerce/presentation/node exports prepareConversationProductImage and relocated compatibility primitives/types. Browser presentation never imports/exports it. The coordinator is thin: same safe source fetch → same product preset → conversation content-addressed key → same immutable conditional PUT/HEAD → same byte/hash public probe (redirects disabled). Keys exactly hash trusted shopId, stableJson native pair and encoded bytes; no source URL/credential enters the key or returned metadata. It does not use the brand preset, historical object identity, source URL fallback or fabricated outreach attempt.

Input is a trusted internal SOURCE result and host-validated public origin/bucket/R2 credentials, child signal, optional original absolute deadlineAt. Config lookup/loading remains host-owned. Missing/invalid configuration and exhausted/pre-aborted budget skip I/O. Deadline budget is min5000ms/remaining turn minus1000ms; absent deadlineAt requires the host child signal already bounded to remaining turn, while Shared still caps5000ms. Single child signal covers all awaits; noncooperative injected ports are raced, native product metadata/encoder work is destroyed on abort, clock checked between stages AND after transport construction. Factory-created transports close in finally on success/failure/cancellation. No network/model/provider send occurs inside any database transaction (there is no database dependency here).

Results are READY with validated prepared-image metadata, or OMITTED with only closed reason/stage/bounded duration. Failures map to CONFIGURATION_UNAVAILABLE, UNSAFE_IMAGE_SOURCE, SOURCE_UNAVAILABLE, IMAGE_TRANSFORM_FAILED, R2_UNAVAILABLE, PUBLIC_IMAGE_UNAVAILABLE or MEDIA_DEADLINE. No config, source/query URL, raw bytes/body or provider error text is logged/returned by the coordinator. Existing bounded sanitizer remains available for legacy media consumers. No added retry loop or model-tool budget usage; relocated SDK/immutable writer retain their original behavior. Identical HEAD is reuse, conflicting object is never overwritten. Optional media failure preserves valid text through the pure plan contract; it never authorizes an extra send after admission.

### Actual changed paths (17)

- package.json: explicit Node export, validator command, exact existing AWS S3/sharp runtime dependencies. Version remains5.11.1; no release/publication.
- package-lock.json:54 added package entries for required dependencies; no existing package version changed or removed. Production/dev role metadata updates follow the new dependency graph, without unrelated refresh.
- tsup.config.ts: Node ESM/declaration entrypoint.
- scripts/validate-conversation-product-image-node.mjs: built public function imports, no-I/O omission smoke and browser bundle/VM isolation from Node/sharp/AWS/Prisma/logging/observability/LangChain.
- src/commerce/presentation/node/index.ts: Node-only public barrel.
- src/commerce/presentation/node/contracts.ts: extracted transitive generic media ports/constants/error/sanitizer; structural credential type only.
- src/commerce/presentation/node/network-policy.ts: relocated generic DNS/IP/pinning security and error types, preserving original restrictions.
- src/commerce/presentation/node/safe-fetch.ts: relocated pinned HTTPS fetch, redirects, source size/encoding/deadline/peer checks.
- src/commerce/presentation/node/metadata-verifier.ts: relocated independent encoded-byte/metadata verification.
- src/commerce/presentation/node/image-transformer.ts: relocated SVG security and existing brand presets.
- src/commerce/presentation/node/product-image-transformer.ts: relocated original sole product preset with optional cancellation only.
- src/commerce/presentation/node/r2-writer.ts: relocated generic S3/immutable writer and sanitization, excluding host brand key adapter/config loader; exposes existing bucket check as isValidMediaBucket.
- src/commerce/presentation/node/public-probe.ts: relocated encoded bytes/type/hash public verification.
- src/commerce/presentation/node/product-image.ts: new conversation key predicate/builder and thin injectable preparation coordinator/types.
- src/commerce/presentation/node/media.test.ts: deterministic golden/security/immutable/race/config/omission/budget/abort/default-adapter integration cases.
- src/commerce/presentation/node/transform-golden.json: fixed SVG and four immutable original product/brand receipts.
- src/commerce/presentation/node/EXTRACTION.md: exact original source fingerprints and moved symbols, retained host ownership, API/deadline and compatibility migration instructions.

No sibling runtime or committed test source imports. Background implementation bodies are deliberately unchanged until its separately owned BACKGROUND001 adoption after publication; that task must replace generic bodies with published Shared imports/compatibility re-exports and retain its host/domain adapters. This extraction does not claim deployed consumer adoption or authorize a parallel pipeline.

### Validation

Canonical bootstrap Node24.19.0/npm11.17.0. No live R2/provider/Meta request, new infrastructure, application database, bucket/ACL operation, migration, publication or deployment. All source/probe/S3 ports are fixtures for execution tests.

- Final `node --import tsx --test src/commerce/presentation/node/media.test.ts`: **10 passed**, no fail/skip. Four original golden transforms; DNS/private/metadata/mapped IPv6/redirect/rebinding/peer protection; 10MiB inherited source policy with lower injected byte limits and encoding refusal; no-redirect probe; exact content key; immutable reuse/collision/409/412 races; public hash/type mismatch; config/budget no-I/O; closed omissions/privacy; abort at every stage including noncooperative ports; real relocated product preset/probe; native abort; injected-clock and slow-factory budget rejection before storage I/O; owned transport close.
- Declared full `npm test`: **670 passed, 0 failed, 3 existing opt-in skips** (673 cases). Final small clock check after factory construction and its additional focused case were then validated by final10 focused tests/types/build/public checks; unrelated full suite was not redundantly repeated.
- Required existing Background media baseline: Vitest read-only execution of shop-brand-media/safe-fetch.test.ts, image-transformer.test.ts, r2-writer.test.ts and recovery-product-media/product-image-transformer.test.ts, product-r2-writer.test.ts: **41 passed**, five files. Invoked existing Background Vitest with its root from this task's execution shell; no Background tracked source/config was edited. This baseline plus the Shared golden/port tests proves preservation; it is not a claim that Background has migrated to the new public package.
- Final `npm run typecheck`: passed, explicit exit0.
- Final `npm run build`: ESM/DTS passed, explicit exit0.
- Final `npm run validate:conversation-product-image-node`: passed, explicit exit0, new public Node runtime exports and browser isolation/VM execution with no provider I/O.
- Temporary public consumer imported Node preparation input/result/dependencies, credential/fetch/transform/probe/transport types and pure SOURCE through package exports against built declarations with NodeNext tsc: passed, exit0. Temporary fixture removed.
- Accepted source ancestry, original file equality, sharp/native lock compatibility and git diff/staged checks passed. No declared lint script exists; none invented. No unresolved source conflict or validation failure remains.

Local receipts: /tmp/arch068-shared002-golden-generation.log, /tmp/arch068-shared002-original-regressions.log, /tmp/arch068-shared002-all-tests.log, /tmp/arch068-shared002-final-focused.log, /tmp/arch068-shared002-final-types.log, /tmp/arch068-shared002-final-build.log, /tmp/arch068-shared002-final-public.log and /tmp/arch068-shared002-declarations.log. Logs are local execution evidence; source provenance/golden/validator are committed for reproduction.

### Git / VCS and isolated preparation

Task branch task/ARCH-068-SHARED-002 in both repositories. Canonical workspace /Users/kwadwoadomafriyie/project/moda-interact-workspace; reused parent /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-068-SHARED-002; created implementation /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-068-SHARED-002. No shared/default checkout switched for implementation, other task worktree reused or subagent assistance.

Launcher dependency gate passed SHARED001 Complete. Parent remote task fast-forwarded yes and origin/main incorporated yes; implementation remote FF not needed, origin/main already current. Recursive submodule sync/update passed with no entries. Parent preclaim6c55cc5e1a170437b60473f8a2820fd38187d286; implementation baseline df87e770a56db61617f1d9c2fd9397005add692d. Durable codex Attempt1 claim at2026-11-09T21:44:22Z, parent94e355ee0ddee92a54d3fcb387f22dff4855223f, committed/pushed by launcher.

Implementation moda-interact-shared **8f8a298de90803671b789ba0ef2fe03058a8023e**, committed/pushed to origin/task/ARCH-068-SHARED-002, clean. This matching parent report is committed/pushed on its task branch. No gitlink staged, main merge/push/force-push, registry publication or downstream promotion.

### Review / compatibility handoff

Complete Architect Review read before source inspection: Not reviewed, no Changes Requested correction list; preserved. All owned requirements are implemented and submitted for review, with the symbol/source map and byte invariants above. Host readiness, credential readers, actual image sending/admission/persisted plan, initializer and consumer re-exports remain their named tasks. SHARED003 owns version selection, immutable package publication/archive/integrity and public installed-consumer evidence after this prerequisite is actually Complete. No guessed release version/integrity or consumer dependency update here. Browser-only consumers remain free of Node media dependencies.

No operational wrapper binding activation, rollout, public-object migration/deletion/cleanup, new bucket/credentials/ACL, database write or real message occurred. Architecture/index/downstream task records are not changed by this implementation agent. Return to moda_architect; no architect acceptance or completion inferred from these tests.

## Architect Review

### Review Status
Accepted — Attempt 1, 2026-11-09.

### Review Notes
Independent moda_architect review of implementation `8f8a298de90803671b789ba0ef2fe03058a8023e` against baseline `df87e770a56db61617f1d9c2fd9397005add692d`, parent report `59435d21a0f2ef66edbf6adf2109ff5b0865da51`, accepted SHARED001, and the binding architecture. No required correction remains.

Compared relocated code directly to immutable Background `db32bdf1e69944b0a15f7c76400f222f00244be4`: fetch differs only in its local network import; metadata verifier, brand presets and public probe are unchanged; product encoder preserves operations and adds optional cancellation; generic immutable writer removes host key/config adapters. Generic network policy retains DNS/IP/pinning protections. Four golden receipts preserve encoded bytes/hash/dimensions/MIME. Background adoption remains a separate published-package consumer task.

The thin coordinator uses the sole product preset, exact tenant/pair/content key, immutable reuse/collision checks and no-redirect byte/hash probe. Configuration failure, exhausted deadline and cancellation omit media; stages share one bounded signal, clock checks prevent late storage entry, and owned transports close. Omission outputs expose no source URLs, credentials, bytes or provider errors. No database/configuration lookup, send, new retry loop or application-source import is introduced. Browser barrel stays isolated from Node/native/SDK dependencies. Exact dependency pins match extraction provenance; package version is unchanged and no release occurred.

### Reviewed Files
All 17 changed paths, including package/lock/tsup, Node exports, contracts/network/fetch/verifier/transforms/writer/probe/coordinator, extraction inventory, golden receipts, tests and public validator; original Background source comparison; task and architecture ownership/rollout requirements.

### Validation Reviewed
Independent rerun in the canonical implementation worktree: **10/10 focused media tests**, `npm run typecheck`, and `npm run validate:conversation-product-image-node` all passed (exit0). Public validator imports the built Node entrypoint and bundles/executes the browser barrel without Node/sharp/AWS/host runtime dependencies or provider I/O. Inspected implementation evidence for full670 passes/3 existing opt-in skips, final ESM/DTS build/public consumer declarations, and 41 original Background regressions. No unresolved failure or additional broad rerun required.

### Architecture Conformance
Conforms to this repository-owned scope and binding contract. Verified launcher-resolved dedicated parent/implementation worktrees on matching task branches, clean submitted states and matching pushed refs. Prepared claim `94e355ee0ddee92a54d3fcb387f22dff4855223f`, recorded start-of-attempt synchronization and recursive-submodule evidence are consistent with task history; no shared checkout substitution. Review made no implementation edits, implementation push, main merge, gitlink update, package publication, deployment or live operation.

### Follow-up
No correction required. SHARED003 is the sole newly executable task: publication of both accepted Shared capabilities. Consumers remain gated on publication; system validation remains terminal/manual-gated. Host consumers must preserve child-signal/original-turn deadline semantics and replace Background generic bodies with published Shared imports as already required.

## Completion Decision — 2026-11-09
The user explicitly authorized independent architect review and, if passing, completion and pushing the decision/frontier. Accepted Attempt1 above satisfies automatic completion: status Complete, executor/claimed_at null, attempt unchanged. Mechanical parent-branch commit/push is explicitly delegated. SHARED003 Pending→Ready, Attempt0 unclaimed; its release-only contract explicitly lists both accepted implementation prerequisites. Architecture remains In Progress. No follow-on execution or integration is implied.


## Existing Background reuse inventory — mandatory, not a second pipeline

Background already prepares both brand and checkout-product images. SHARED-002 relocates the existing generic implementation; BACKGROUND-001 switches its callers to the published implementation. Do not introduce a parallel fetcher, transformer, uploader or verifier.

| Existing source under Background `src/services/` | Required disposition |
|---|---|
| `shop-brand-media/safe-fetch.ts`: `createSafeImageFetcher`, pinned HTTP/DNS implementation | Move generic implementation and its ports to Shared Node; keep a Background compatibility re-export. Both old paths and the conversation path use it. |
| `shop-brand-media/metadata-verifier.ts`: `verifyEncodedBrandImage` | Move byte/metadata verification to Shared Node; compatibility re-export. |
| `shop-brand-media/image-transformer.ts`: `assertSelfContainedSvg`, `createShopBrandImageTransformer` | Move existing SVG check and brand transform presets to Shared Node unchanged; compatibility re-export. Do not use the brand preset for product images. |
| `recovery-product-media/product-image-transformer.ts`: `createOutreachProductImageTransformer` | Move this existing product preset to Shared Node unchanged and export it under the existing name. Conversation preparation calls this same function. Preserve 1125×600 JPEG, contain/white padding, orientation, sRGB, metadata stripping, quality steps `[86,76,66,56,46]`, 1MiB quality target and strict output `<5MiB`. Align the new prepared-image validator to this strict bound (`max(5*1024*1024-1)`). Keep compatibility re-export. |
| `shop-brand-media/r2-writer.ts`: `createBrandR2S3Transport`, `putGuardedImmutableR2Object` | Move these existing generic transport/immutable PUT+HEAD functions and transport types to Shared Node. Preserve key predicate injection. Background brand/product wrappers retain their own accepted-key predicates. Conversation preparation passes its conversation-key predicate into this same writer. |
| `shop-brand-media/public-probe.ts`: `createShopBrandPublicMediaProbe` | Move existing byte/hash probe to Shared Node with compatibility re-export. Preserve no-redirect public verification. |
| `shop-brand-media/contracts.ts`, `merchant-knowledge-network-policy.ts` | Extract only transitive generic types/errors/security functions required above; keep domain/DB/configuration concerns in Background. Preserve exported compatibility names and error codes. |
| `shop-brand-media/processor.ts`, `shop-brand-media-orchestration/*`, `shop-brand-media-runtime/*` | Remain Background orchestration. Update generic imports only; preserve role/source-generation/fingerprint checks and `shop-brands/` key behavior. |
| `recovery-product-media/product-r2-writer.ts`, `outreach-product-object-key.ts`, `merchant-site-segment.ts` | Remain Background outreach adapters and identity/key policy. Use extracted common writer; preserve `outreach-products/` key format and all existing keys/URLs. |
| `recovery-product-media/recovery-product-image-resolver.ts`: `RecoveryProductImageResolver` | Remain Background. Preserve live MCP product read, recovery/generation/attempt/recipient/sequence checks, 30s preparation budget and final `validateBeforeBinding` fence. Change generic imports only. Never fabricate an outreach attempt to call it from Studio or a conversational reply. |
| `shop-brand-media/r2-config.ts` and platform configuration consumers | Keep configuration lookup/credential loading in Background. Shared receives validated configuration from each host and performs no Prisma/platform-setting reads. |

New code is limited to conversation-specific source selection, the optional wrapper binding, a thin preparation coordinator using the relocated components, the conversation key predicate/key builder, delivery-plan handling, Studio display and Background media-send wiring. Distinct `conversation-products/` keys isolate conversational lifecycle from outreach-attempt keys; they do not require another bucket, credentials, uploader or transform preset. Existing public objects are not migrated, copied or deleted. Reusing image-processing code does not mean reusing a historical object's identity without fresh product verification.

Before SHARED-002 is accepted, record the original Background source commit and every moved symbol. Before BACKGROUND-001 is accepted, prove both existing brand and outreach callers use the published Shared primitives and that no second implementation body remains. Run existing brand/outreach tests plus fixed-image golden regression tests with unchanged keys, bytes, dimensions, hashes and error/fence behavior. Keep orchestration-specific checks in their original host. The task agent must report any intentional byte change as a contract violation, not silently regenerate golden expectations.

## Coherence amendment — exact handoff and precedence

This section resolves terminology in earlier sections; it does not authorize another implementation. The original Background product transformer is the only product preset. Its output is strictly less than 5MiB, uses contain/white padding (not crop), and retains its quality ladder. Host configuration readers and credential loading stay in their host repositories. Only the generic media operations move to Shared.

Shared SHARED-001 also exports these exact strict provenance schemas, reusing the validators already defined above:
```ts
export const ConversationProductPairSchema = z.strictObject({
  productId: NativeProductId, variantId: NativeVariantId,
});
export const ConversationVerifiedProductsSchema = z.strictObject({
  shopId: BoundId,
  platform: z.enum(['SHOPIFY', 'WOOCOMMERCE']),
  products: z.array(CommerceProductSchema).max(3),
});
export const ConversationProductImageSourceSchema = z.strictObject({
  kind: z.literal('SOURCE'), shopId: BoundId,
  platform: z.enum(['SHOPIFY', 'WOOCOMMERCE']),
  productId: NativeProductId, variantId: NativeVariantId, sourceUrl: HttpsUrl,
});
```
Selector input is exactly `{shopId, platform, displayedPairs, verifiedProducts}`; displayedPairs is an array of ConversationProductPairSchema with maximum 3 and uniqueness by canonical productId/variantId tuple. Verified product array pairs must also be unique. Schema/provenance mismatch throws an Error with code PRODUCT_IMAGE_IDENTITY_INVALID; missing exact first pair returns PRODUCT_NOT_VERIFIED. No new native-ID format validation is introduced. This result is internal and is never accepted from a browser or model as proof of authorization. Shared task tests must cover WooCommerce simple products (`variantId:null`) and both platforms' native variant IDs.

Plan construction first validates the body and binding. Omitted binding produces TEXT/BINDING_DISABLED. A present invalid binding throws PREPARED_INVALID; it cannot silently become text. With a valid binding, precedence is NO_PRESENTED_PRODUCT, CAPTION_TOO_LONG, IMAGE_UNAVAILABLE, IMAGE_IDENTITY_MISMATCH, then IMAGE success. Host source/preparation omissions are logged with their original reason; buildConversationDeliveryPlan's IMAGE_UNAVAILABLE is the delivery-level summary. IMAGE_IDENTITY_MISMATCH logs at error severity and never dispatches that URL. Source absence or optional preparation failure still allows valid text. Hosts skip media configuration/network work when the first two applicable omission conditions already determine TEXT.

Schema files do not implement final send authorization. Background requires persisted plan.image.shopId to equal the locked message's conversation shop, and its exact pair to equal the verified selected first pair in the matching receipt. Persisted JSON alone is not a receipt. Null is legacy only: a newly prepared aspect-2 reply always persists TEXT or IMAGE. Legacy text retry remains legacy; it cannot be upgraded to IMAGE. No later retry rewrites a previously admitted plan.

SHARED-001 owns changes to Shared source only. SHARED-002 can read Background source as extraction input but writes only Shared. BACKGROUND-001 owns replacement of Background implementation bodies and updates every compatibility caller/mock. ADMIN-001 owns authoring only; ADMIN-002 owns script/extracted transaction helpers. DATABASE-001 owns schema/migration/generation validation only; it does not implement Shared validation or Background admission. Each task's acceptance applies only to its repository and explicitly owned interfaces; the whole acceptance matrix is integrated by SYSTEM-TEST-001.

SYSTEM-TEST-001 creates `src/harness/conversation-product-image/{fixtures.js,scenario.js,assertions.js}` and `test/conversation-product-image.test.js`; wires the existing package.json test command using the repository's existing test runner and documents launch in README.md. Reuse `src/whatsapp-emulator.js`, `src/harness/aimock/runtime.js`, `src/harness/environment.js` for transport/model/environment control; extend them only where IMAGE payload capture is missing. Fixtures use the same compiled wrapper, product bytes, public origin and scripted envelope for both hosts; assert complete plan equality, media omission, one provider call, body preservation and legacy behavior. Add the mandatory failure/race cases above. Tests use disposable local infrastructure/provider emulator; launching real infrastructure or sending real WhatsApp messages requires separate explicit user authorization. Do not mark blocked merely because optional live infrastructure was not authorized when local acceptance can run.

Script `--apply` is opt-in and a separate operator action. Implementation completion does not activate a wrapper. Existing occupied slots are never replaced. Source contains no header logo or fixed product facts: only response.body and the optional structured binding. Existing all-language eligibility rules remain authoritative; obtain REVIEW_LANGUAGES from its existing export, not a copied locale list or hardcoded loop count. Tests assert the current count and exact coverage from that export.

## Accepted prerequisite handoff — 2026-11-09

SHARED001 independently Accepted by moda_architect and explicitly completed at Attempt1. Exact accepted moda-interact-shared source0b06467c37cbc4cd6ce67fcfa6e9c3fd7da66822 on task/ARCH-068-SHARED-001, baseline608e60b8758de809ace2c6f89755e1c357616278. The canonical completed task record is synchronized in this parent branch. Ready at unchanged Attempt0, executor/claimed_at null; no implementation worktree/claim or automatic execution.

This is a SOURCE dependency, not a new npm publication. Do not assume current unmerged main contains these APIs. Future implementation must carry the exact accepted contract source into its own task branch using normal authorized dependency integration, preserve its schemas/legacy hashes/AGENT behavior, and perform only the owned Node extraction. No main merge, invented release version/integrity, duplicate pipeline or premature consumer activation. SHARED003 retains publication ownership after002 completion.

Readiness synchronized into this canonical parent from completion967afb246. The completed SHARED001 record is present for branch-local dependency gating; no implementation worktree or claim created.
