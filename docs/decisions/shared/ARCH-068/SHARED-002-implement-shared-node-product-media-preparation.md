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
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
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
- [ ] Verify dependencies and current owned source against binding touch points.
- [ ] Implement every requirement in the owned scope and binding contract.
- [ ] Add deterministic success/failure/compatibility tests specified above.
- [ ] Run declared repository validation and record exact evidence.
- [ ] Publish implementation and parent report on mirrored task branches for review.

## Dependencies
ARCH-068-SHARED-001

## Acceptance criteria
All owned scope above is complete, exact contract tests pass and no TODO/placeholder or unresolved cross-service choice remains. For this Shared task, validate its owned source and built public exports; publication evidence is owned by SHARED-003; no sibling source imports/copied mechanics. Record actual changed paths and checks. Preserve existing grounded text, product identity, moderation/send fences, initial/proactive Meta flows.

## Out of Scope
No redesign of aspects 1 and 3, Meta submission/WABA validation, inventory write, unrelated cleanup, budget increase, production mutation or automatic live initializer.

## Agent execution and review
Execution is owned by the assigned agent, not a human developer. Use /moda-task with canonical isolated parent/implementation worktrees and mirrored task branches. Do not claim on authoring. Implement only this repository portion; use published Shared APIs. If an actual source conflict contradicts the exact binding contract, report it to the architect with path/symbol/evidence; do not invent a replacement architecture or leave a placeholder. No main merge/push, production mutation, real send or live initializer execution is part of this task.

## Completion Report
Not started. Record changed paths, exact source SHA, isolated worktree/preparation evidence, tests with counts, public package version/integrity where consumed, dependency evidence, and any remaining risks.

## Architect Review
Not reviewed.

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
