---
id: ARCH-068-BACKGROUND-001
architecture_id: ARCH-068
title: Deliver one frozen free-form text or image reply
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-11-10T00:04:10Z
attempt: 1
depends_on: ['ARCH-068-SHARED-003', 'ARCH-068-DATABASE-001']
enables: ["ARCH-068-ADMIN-002", "ARCH-068-SYSTEM-TEST-001"]
created: 2026-11-09
updated: 2026-11-10
---
# Deliver one frozen free-form text or image reply

## Architecture and objective
Implement the owned portion of [binding ARCH-068](../../../architecture/ARCH-068-optional-conversation-product-image.md). The entire contract is normative, including exact schemas, transport/failure rules, initialization, rollout and acceptance matrix. Read it before execution.

## Context and scope
Own package pins/lock/database gitlink; commerce/{host,presentation-receipt,product-context-repository}.ts; services/conversation-wrappers/{contracts,service,repository if present}.ts; services/conversation-wrappers/compose-ai-outbound.ts; services/conversation-turn-processor.service.ts; new services/conversation-product-media.ts; platform-configuration/consumers.ts; outbound-whatsapp-admission.service.ts; outbound-whatsapp-admission/{outbound-whatsapp-admission.types,outbound-message-delivery.service,general-outbound-send-fence.service}.ts; recovery-conversation/outbound-send-fence.service.ts; integration/whatsapp/types.ts; services/whatsapp.service.ts and provider port/mocks. Replace extracted generic media functions with Shared imports as described above, retaining initial-outreach wrappers/golden tests.

Host keeps verified envelope.replyText as agent content, exact pair order and freshly authorized products through final verification; do not replace content with deterministic candidates. Internal image preparation is after valid text composition and before durable preparation, signal/deadline bounded. Read R2 with current existing consumers. Use same Shared APIs as Studio. Wrapper applicationKey/responseDigest/replay evidence must cover validated complete deliveryPlan, including image hash/url/pair, not body alone. An admitted retry loads exact persisted plan and verifies equality; it must not regenerate image bytes/config-dependent URL or reuse a new plan under old digest.

Add `sendPreparedConversation` (AGENT aspect2 only) accepting admission + validated deliveryPlan + expected control/inbound versions/productContextUpdate and correlation. Keep sendPreparedText delegating for legacy callers; keep template methods unchanged. Before any provider permit: prepare content plus outboundPresentation atomically on same PENDING/never-admitted message, using existing message locks/transaction; reject mismatch on existing non-null plan. Moderate complete body through existing AGENT_MESSAGE path. Product media is server-selected from verified merchant data; existing text moderation remains, no new model image moderation claim. Final admission compares both content and stored JSON plan using parsed canonical equality; unknown schema refuses, no fallback. Extend recovery fence deliveryKind with IMAGE; treat IMAGE identically to TEXT for free-form window, billing/caps, AGENT product-context commit and control/inbound gates. Replace every `deliveryKind==='TEXT'` gate that semantically means service-window reply with explicit TEXT-or-IMAGE; do not grant IMAGE template privileges. At final transaction time require latest inbound window open; expired -> suppression, no image/text send and no proactive-template substitution. General fence must explicitly enforce the same window for this new AGENT method; it cannot bypass recovery scope. HUMAN, automation, initial/outside-window templates retain prior behavior. No provider/R2 I/O while database locks held.

Provider `sendWhatsAppImage({to,link,caption,replyToProviderMessageId?},signal?)` sends one request `messaging_product:'whatsapp',type:'image',image:{link:plan.image.publicUrl,caption:plan.body}` plus existing reply context. No inline markdown URL, no Meta template name/components, no WABA new validation. IMAGE receipt follows existing markSent/provider failure/unknown outcome pathway. Dispatch key acquired before I/O, immutable thereafter, no duplicate send on requeue. Textplan uses existing sendWhatsAppText. A provider media failure after permit is a delivery failure, not permission to send a second text. Caption/body persisted once, one admission/counter/receipt. On cancellation/stale control/new inbound before admission no provider dispatch or context replacement. Document observable media omission reason and stage using existing shared logging; no tokens/source URLs/raw bodies.

## Interfaces and contracts
The named exported schemas/APIs and exact JSON shapes in the binding contract are authoritative. Existing v1 template hashes/legacy records remain compatible. No clothing-specific fields/model image URL or Meta recovery contract extension.

## Work Items
- [ ] Verify dependencies and current owned source against binding touch points.
- [ ] Implement every requirement in the owned scope and binding contract.
- [ ] Add deterministic success/failure/compatibility tests specified above.
- [ ] Run declared repository validation and record exact evidence.
- [ ] Publish implementation and parent report on mirrored task branches for review.

## Dependencies
ARCH-068-SHARED-003, ARCH-068-DATABASE-001

## Acceptance criteria
All owned scope above is complete, exact contract tests pass and no TODO/placeholder or unresolved cross-service choice remains. For tasks consuming Shared, prove the dependency using the exact published artifact; no sibling source imports/copied mechanics. Record actual changed paths and checks. Preserve existing grounded text, product identity, moderation/send fences, initial/proactive Meta flows.

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

## Database dependency reconciliation — 2026-11-09
DATABASE001 Complete at independently Accepted Attempt1, implementation75669477. This prerequisite is satisfied; task remains Pending because SHARED003 publication is still Pending. No claim, attempt increment or implementation started. Deploy accepted migration before referencing the new field; accepted source does not imply deployment.

## Accepted publication handoff — 2026-11-09
SHARED003 is Complete / independently Accepted Attempt1. Install exactly `@modainteract/moda-interact-shared@5.12.0`, registry https://registry.npmjs.org/, SRI `sha512-RD3pGDVZHK8sRwbi91SpdouRDVkyf+4rhdB4eczaG48avsnEOQRhRccqzX2YI9KhXa1jXE4S2LHfz7D9DR5PEw==`, tarball SHA256 `e4416c765079a6c8c8ca04894e87e3822c3af0acf19428a5d3f542effe697393`. Release source `12d0b85aaeefba4dfc46bb12637004f19d462b19` includes both accepted Shared capabilities. Use browser-safe `/commerce/presentation` for contracts and Node-only `/commerce/presentation/node` for media preparation; no sibling source import or copied generic mechanics. Ready at unchanged Attempt0, executor/claimed_at null; no claim or implementation begins here.
DATABASE001 is also Complete / Accepted Attempt1 (source75669477); both explicit dependencies are satisfied. Migration deployment remains a separate rollout prerequisite before runtime use.
