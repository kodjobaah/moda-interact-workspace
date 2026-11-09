---
id: ARCH-068
title: Optional verified product images in service-window conversation replies
status: in_progress
coordinator: moda_architect
created: 2026-11-09
updated: 2026-11-09
---
# ARCH-068 — Optional conversation product image binding

## Outcome and boundaries
This initiative implements aspect 2 only: free-form CommerceAgent replies within the customer service window, using an internal Moda conversation wrapper. Initial abandoned-checkout outreach and proactive follow-up outside that window continue through their existing Meta-approved templates, with no changes to submission, registration, WABA validation, initial-outreach image selection or eligibility. Studio does not send messages or validate a WABA. Background retains final send admission, moderation, consent/control, billing and the 24-hour gate.

The agent writes the answer. The wrapper inserts response.body without replacing it with a deterministic dump of product descriptions, stock or options. Existing final-answer grounding, verified selection checks, inventory semantics and response limits remain. Product images are optional. Merchant shipping/returns/knowledge answers work without a product, image or R2 configuration. Do not force an unrelated recommendation/image onto a policy answer. No category, clothing, color, size or platform-specific assumption belongs in the common contract.

## Closed decisions
1. Add one optional structured wrapper property `productImage`, not an inline text token. UI calls it “Optional product image”. Its variable is `response.productImage`. Existing URL text variables keep their existing semantics. Do not reinterpret shopBrand.logoUrl or add image variables to Meta recovery semantic bindings.
2. Media layout is `BEFORE_BODY`: WhatsApp displays an image above its caption. Arbitrary inline placement inside text is not supported. Admin shows this truthfully. This binding is not sent to Meta for approval.
3. Select the first pair in the final, successfully verified displayed product order, at most three pairs. Use only that pair's fresh product.imageUrl. If it has no image, omit the image; do not substitute another product, first variant, brand logo, historical image, model URL or arbitrary search result. No selections means no image. A policy reply with no displayed product has no image even if earlier turns had products.
4. Use one WhatsApp provider message per reply: text-only, or an image with the entire rendered text as caption. Caption cap is 1024 Unicode code points; text cap remains the existing 4096-character contract. If the complete wrapped text exceeds the caption cap, send the complete text-only reply and record CAPTION_TOO_LONG. Never truncate text, make an extra model call just to shorten it, split into extra sends, or consume an extra message admission. This deliberately preserves answer quality when the optional image cannot fit.
5. Prepare the verified image in public R2 using one Shared Node implementation. Studio and Background inject configuration/credentials, correlation, trusted tenant and abort signal. Shared owns generic safe fetch, transform, content-addressed key, immutable put/head verification and public probe; hosts own authorization, current product reads and environment/configuration lookups. Do not import application source across repositories.
6. Media preparation failure never discards a valid text answer. Missing R2 config, unsafe URL, timeout, transform/upload/probe failure become an explicit media omission. A malformed/tampered wrapper remains a wrapper refusal; do not silently accept an invalid binding.
7. Persist the exact one-message delivery plan before final admission. Retries never regenerate an admitted plan or downgrade an image after an unknown provider outcome. Provider transport errors follow existing ambiguity handling. No automatic second text send after image rejection/timeout.
8. No new table. Add one nullable JSONB field to the existing outbound message for durable plan equality. Existing text/initial/template paths retain null and old rows remain readable. Existing template AST JSONB stores the optional binding; no template schema migration.
9. Seed script is Admin-owned and uses its compiler/save/activation services. It creates an AI-only wrapper, not SHARED/HUMAN, with an empty header/footer, only response.body, no checkout conditional, and optional product image. All supported languages contain the same protected slot/binding with no prose; no machine translation or invented review identity. Initialization must not overwrite an occupied slot.

## Shared public browser-safe contract — SHARED-001
Own `src/commerce/presentation/product-image.ts` (new), wrapper-contracts.ts, wrapper-projection.ts, wrapper-render.ts, compose.ts, index.ts and their tests. Keep this export browser-safe. Reuse the existing Zod version, CommerceProductSchema native identity validators, canonical JSON/digest utilities and envelope validators. Export the following exact schemas/types (imports abbreviated only):
```ts
const NativeProductId = CommerceProductSchema.shape.productId;
const NativeVariantId = CommerceProductSchema.shape.variantId;
const BoundId = z.string().min(1).max(256);
const Sha256 = z.string().regex(/^[a-f0-9]{64}$/);
const HttpsUrl = z.string().max(2048).url().refine(v => new URL(v).protocol === 'https:');
export const ConversationProductImageBindingSchema = z.strictObject({
  variable: z.literal('response.productImage'),
  placement: z.literal('BEFORE_BODY'),
  optional: z.literal(true),
});
export const ConversationPreparedProductImageSchema = z.strictObject({
  schemaVersion: z.literal(1),
  shopId: BoundId,
  productId: NativeProductId,
  variantId: NativeVariantId,
  publicUrl: HttpsUrl,
  objectKey: z.string().max(300).regex(/^conversation-products\/v1\/[a-f0-9]{64}\/[a-f0-9]{64}\/[a-f0-9]{64}\.jpg$/),
  contentSha256: Sha256,
  contentType: z.literal('image/jpeg'),
  byteLength: z.number().int().min(1).max(5 * 1024 * 1024 - 1),
  width: z.literal(1125), height: z.literal(600),
});
export const ConversationDeliveryPlanSchema = z.discriminatedUnion('kind', [
  z.strictObject({schemaVersion:z.literal(1),kind:z.literal('TEXT'),body:z.string().min(1).max(4096)}),
  z.strictObject({schemaVersion:z.literal(1),kind:z.literal('IMAGE'),body:z.string().min(1).max(4096),
    image:ConversationPreparedProductImageSchema}),
]).superRefine((v,ctx) => {
  if(v.kind==='IMAGE' && Array.from(v.body).length>1024)
    ctx.addIssue({code:'custom',path:['body'],message:'CAPTION_TOO_LONG'});
});
```
All control-character and existing text validation still applies before constructing a plan; these snippets do not waive those checks. Export z.infer types. No new model-visible image URL/selection field: reuse existing verified product selections and exact displayed pairs.

Add `productImage?: ConversationProductImageBinding` to PreparedWrapper and wrapper authoring projection. Omitted property is legacy text-only and must not be materialized as null/default (preserve all old hashes). readPreparedWrapper allows only this additional key, validates it with the shared schema, preserves it in returned projection and hash. Duplicate/unknown placement/nonoptional/model URL fields refuse PREPARED_INVALID. Export the schema for Admin validation rather than duplicating it.

Export `chooseConversationProductImageSource({shopId,displayedPairs,verifiedProducts})`: displayedPairs is max3 unique native pairs; verifiedProducts are CommerceProductSchema values from the same host-authorized final verification phase. Return `{kind:'SOURCE',shopId,productId,variantId,sourceUrl}` for the first exact pair with its HTTPS image; otherwise `{kind:'OMITTED',reason:'NO_PRESENTED_PRODUCT'|'NO_PRODUCT_IMAGE'|'PRODUCT_NOT_VERIFIED'}`. No later-pair fallback. CommerceProductSchema has no tenant or platform fields. Therefore verifiedProducts is NOT a naked product array: it is a strict provenance envelope `{shopId: BoundId, platform: z.enum(["SHOPIFY","WOOCOMMERCE"]), products: z.array(CommerceProductSchema).max(3)}`. Add required platform to the selector input and SOURCE result. Reject envelope shopId/platform mismatches with PRODUCT_IMAGE_IDENTITY_INVALID before reading a URL. Require exact variant/parent identity and unique pairs. Hosts construct this envelope from the final authorized verification reads; never from model output or persisted historical products. The helper checks provenance consistency, not authorization itself. Invalid/non-HTTPS imageUrl produces NO_PRODUCT_IMAGE without network I/O.

Export `buildConversationDeliveryPlan({body,binding,image,shopId,displayedPairs})` returning `{plan: ConversationDeliveryPlan,mediaOmission: reason|null}`. Missing binding -> TEXT/BINDING_DISABLED; no selected product -> TEXT/NO_PRESENTED_PRODUCT; body >1024 code points -> TEXT/CAPTION_TOO_LONG; no prepared image -> TEXT/IMAGE_UNAVAILABLE; foreign/mismatched image -> TEXT/IMAGE_IDENTITY_MISMATCH (never emit that URL); otherwise IMAGE. Validate image.shopId and first displayed pair exactly. Input body must already be successfully wrapped. Stable plan digest is SHA256 of existing canonical stable JSON of the complete validated plan; host injects existing digest function, no browser crypto dependency.

Finish the partial responseStyle AGENT work in compose.ts: explicit `responseStyle:'AGENT'` preserves normalized envelope.replyText for all valid answer dispositions, after existing fact/selection validation, with no deterministic product fact substitution. Do not infer displayed identities by matching generated prose against deterministic fact strings. Consumers retain verified selected pair order associated with this complete, unsliced reply; invalid/unobserved selection still refuses. Existing legacy style remains unchanged for unrelated consumers. No added model call or body truncation.

## Shared Node media preparation — SHARED-002
New explicit entrypoint `@modainteract/moda-interact-shared/commerce/presentation/node`, backed by `src/commerce/presentation/node/index.ts`, product-image.ts and extracted generic media modules. Add package exports, tsup entry, declaration output, required AWS S3/sharp runtime dependencies and package-lock. Browser presentation barrel must not export/import the Node entrypoint.

Public `prepareConversationProductImage({source,publicOrigin,bucketName,r2,signal})` returns READY with ConversationPreparedProductImage or OMITTED with reason CONFIGURATION_UNAVAILABLE|UNSAFE_IMAGE_SOURCE|SOURCE_UNAVAILABLE|IMAGE_TRANSFORM_FAILED|R2_UNAVAILABLE|PUBLIC_IMAGE_UNAVAILABLE|MEDIA_DEADLINE. r2 is `{endpoint,accessKeyId,secretAccessKey}` server-only; source is the SOURCE result above. Dependency-injected fetch/transform/S3/probe implementations and clock enable deterministic tests. Never log input config, URLs containing query strings, raw images or provider bodies.

Extract common mechanics from Background `services/shop-brand-media/{contracts,safe-fetch,image-transformer,metadata-verifier,public-probe,r2-writer}.ts`, `services/merchant-knowledge-network-policy.ts` and `services/recovery-product-media/product-image-transformer.ts` where needed; remove application-specific imports from Shared. Keep initial-outreach attempt selection/fencing/key format and host configuration outside Shared. Background consumer replaces extracted generic bodies with reexports/adapters after publication; preserve initial brand/outreach byte/security behavior with golden vectors. Do not copy generic mechanics into Commerce.

Image processing uses existing safe image fetch semantics (DNS/private/loopback/link-local/cloud-metadata rejection on initial and every redirected URL, pinned address/TLS verification; HTTPS only), max3 redirects, max10MiB source bytes, existing decompression/pixel/SVG restrictions; never loosen current stricter restrictions. Existing product transform produces 1125x600 JPEG with its existing contain/white-padding/quality policy, <5MiB; use golden input/output metadata and preserve behavior. Key exactly `conversation-products/v1/<sha256(shopId)>/<sha256(stableJson({productId,variantId}))>/<sha256(transformedBytes)>.jpg`, UTF8 canonical input and lowercase hex. Public URL is validated publicOrigin + '/' + objectKey, never source URL/signed URL. Use existing immutable If-None-Match put and HEAD metadata equality (type,length,hash) and public byte/hash probe; an existing identical object is reuse, a conflicting object is omission. No source URL secrets in key. Abort all stages on caller signal; close owned transports. No background jobs, new media table, cleanup job, bucket/public ACL mutation or fallback to merchant source URL.

Preparation budget is min(5000ms, remaining turn deadline minus1000ms); <=0 means omit without I/O. Hosts create one child signal covering fetch/transform/upload/probe and retain their original turn deadline. Source selection once, one preparation attempt per turn; no retries/modeltool budget increment for internal media preparation. Shared returns bounded stage/reason; hosts extend existing domain logs with shop/conversation/run, pair, omission/stage/duration and plan kind only.

## Durable storage — DATABASE-001
Exact addition to `ConversationMessage` in prisma/schema.prisma:
```prisma
  // Frozen aspect-2 delivery plan; null for legacy/other message paths.
  outboundPresentation Json? @db.JsonB
```
Migration SQL is only:
```sql
ALTER TABLE "whatsapp"."ConversationMessage"
ADD COLUMN "outboundPresentation" JSONB;
```
No default/backfill/index/new table/enum change. Application validates ConversationDeliveryPlanSchema and additionally matches plan.body to content. Image plans use existing contentType TEXT and ordinary caption content for current history/moderation compatibility; actual provider media classification is in outboundPresentation, not reused inbound AUDIO/transcription fields. Do not populate providerMediaId with an R2 URL. Existing providerMessageId remains the one provider receipt. No credentials, recipient, source URL or model prose beyond existing body in this JSON. Migration deploys before Background references this field. Null means existing legacy send behavior; plan never inferred from text.

## Admin authoring and initializer
ADMIN-001 consumes Shared publication. Touch authoring/{types,validation,compiler,preview}.ts, compilation/{wrapper-compiler,reconstruction,contracts}.ts, wrappers/{eligibility,preview,service}.ts, translation source snapshot/protected binding checks, DTO/server actions/routes that carry draft/prepared/preview, components under authoring (template-content-editor, wrapper-structure-editor, template-read-only-preview, template-editor-steps) and wrappers/wrapper-before-after-preview/compilation/conversation-wrapper-review-preview. Add a wrapper-only toggle default false with explanatory “One verified product image above the response; omitted when unavailable” and an illustrative preview. Uses exact shared schema. Binding preserved in compile/clone/translation/review, included source/prepared hashes; locale eligibility requires binding equality across all locales. Meta AST rejects this key; HUMAN/SHARED wrapper editor rejects it for this phase; supported audience AI only, checked server-side. Existing text URL fields remain text. Do not fetch live merchant images in Admin preview or read R2 secrets there.

ADMIN-002 adds `scripts/initialize-conversation-wrapper.mjs`, server core `src/lib/admin/whatsapp-templates/wrappers/initialize.ts`, package command `whatsapp:initialize-conversation-wrapper`, README and disposable DB tests. Exact CLI: `--environment=test|production --actor-admin-id=<id> --dry-run|--apply --reason=<10..500 chars>`; default dry-run, mutually exclusive modes, unknown args fail. Resolve trusted deployment environment using existing Admin runtime configuration and require exact match with requested environment; production is supported but never executed by implementation/tests. Actor must already exist and have SUPER_ADMIN role; never synthesize/elevate actor.

Exact source: schemaVersion1/family MODA_CONVERSATION_WRAPPER/sourceLanguageTag en/audience AI/header[]/body[{type:'slot',name:'response.body'}]/footer[]/conditionals[]/productImage{variable:'response.productImage',placement:'BEFORE_BODY',optional:true}. Use canonical compiler and hash helpers. Stable submission UUID is `e14e7967-05bb-4a5c-bacf-0663b42b37d5`, derive definitionIdForSubmit(actorId,uuid). Same actor repeat verifies byte-identical immutable source/prepared; mismatch fails, never edits existing definition. Existing occupied AI slot: identical canonical desired prepared/binding and eligible definition -> UNCHANGED even if different author ID; any other active definition -> SLOT_OCCUPIED, no writes, no overwrite/force flag. Empty slot -> create/save immutable definition and locales and activate atomically in one SERIALIZABLE transaction; concurrent empty-slot initialization loses cleanly with conflict, no orphan partial template.

All20 existing REVIEW_LANGUAGES locales use precisely the slot-only AST, identical binding, no prose. English SOURCE_SAVED; other languages REVIEWED with supplied superadmin actor, common transaction timestamp, providerLanguageCode null. This is operator approval of language-invariant structural content, not fabricated translation review. Reuse existing eligibility and activation/audit semantics via extracted transaction-internal service functions, not nested transactions or direct unchecked pointer SQL. Audit metadata identifies script/version/structural-only locales/source+content hashes/previous slot; reason provided by operator. Never create a Meta registration/submission job. Dry-run writes nothing and reports planned definition ID/hash/locale count/current pointer; apply returns CREATED_AND_ACTIVATED or UNCHANGED; failures typed INVALID_ARGUMENT/ENVIRONMENT_MISMATCH/ACTOR_DENIED/IMMUTABLE_CONFLICT/SLOT_OCCUPIED/CONCURRENT_STATE_CHANGE. Output no secrets/customer data. No automatic execution against test/production in task.

## Commerce Studio adoption
Own package pins/lock and src/commerce/preview/{presentation,recommendation-presentation,presented-pairs,service,types,product-context,store,redis-store}.ts; src/studio/test-conversations/{client.ts,contracts.ts,test-conversation-view-types.ts,test-conversation-drawer.tsx,conversation-panel.tsx,test-conversations-screen.tsx}; platform-configuration/{runtime,service}.ts and lib/server config seams; add `preview/conversation-product-media.ts`. Both local provider reads and standalone MCP supply the existing canonical product.imageUrl. Reuse fresh final-verification products to choose first pair; if recommendation path lacks them, get exactly selected first pair using existing authorized get_product with remaining remote-call/turn budgets (deduplicate within final verification). No hidden unbudgeted provider read. Other selected facts must not be dropped.

Use responseStyle AGENT, shared source selector, Node preparer, shared delivery-plan builder. Load merchant.knowledge.r2 and shopBrand.publicMedia via the existing sealed configuration mechanism/server key, extending typed allowed-key reader only; never environment-secret fallback, inline decrypt fork, client secret prop or new platform setting. No binding/no selected pair/caption too long -> skip configuration read/preparation entirely. If wrapper disabled image, no R2 write. Media plan output propagated as optional `deliveryPlan` in ready WhatsAppPreview DTO; old ready results without plan render text-only. Keep body/agentOutput distinction. Store result atomically with assistant reply/context; budget, cancellation, replay and storage bounds include media metadata. UI uses plan IMAGE publicUrl and body as caption; TEXT displays body. Hide implementation metadata except diagnostic panel. Image load error shows text without broken-image placeholder and leaves plan diagnostics. Latest successful displayed pairs only, no prose-match receipt. A shipping/returns/knowledge reply with no selection must succeed text-only with R2 missing. No sends, WABA reads or Meta template validations. Existing initial-outreach preview unaffected.

## Background adoption and exact admission changes
Own package pins/lock/database gitlink; commerce/{host,presentation-receipt,product-context-repository}.ts; services/conversation-wrappers/{contracts,service,repository if present}.ts; services/conversation-wrappers/compose-ai-outbound.ts; services/conversation-turn-processor.service.ts; new services/conversation-product-media.ts; platform-configuration/consumers.ts; outbound-whatsapp-admission.service.ts; outbound-whatsapp-admission/{outbound-whatsapp-admission.types,outbound-message-delivery.service,general-outbound-send-fence.service}.ts; recovery-conversation/outbound-send-fence.service.ts; integration/whatsapp/types.ts; services/whatsapp.service.ts and provider port/mocks. Replace extracted generic media functions with Shared imports as described above, retaining initial-outreach wrappers/golden tests.

Host keeps verified envelope.replyText as agent content, exact pair order and freshly authorized products through final verification; do not replace content with deterministic candidates. Internal image preparation is after valid text composition and before durable preparation, signal/deadline bounded. Read R2 with current existing consumers. Use same Shared APIs as Studio. Wrapper applicationKey/responseDigest/replay evidence must cover validated complete deliveryPlan, including image hash/url/pair, not body alone. An admitted retry loads exact persisted plan and verifies equality; it must not regenerate image bytes/config-dependent URL or reuse a new plan under old digest.

Add `sendPreparedConversation` (AGENT aspect2 only) accepting admission + validated deliveryPlan + expected control/inbound versions/productContextUpdate and correlation. Keep sendPreparedText delegating for legacy callers; keep template methods unchanged. Before any provider permit: prepare content plus outboundPresentation atomically on same PENDING/never-admitted message, using existing message locks/transaction; reject mismatch on existing non-null plan. Moderate complete body through existing AGENT_MESSAGE path. Product media is server-selected from verified merchant data; existing text moderation remains, no new model image moderation claim. Final admission compares both content and stored JSON plan using parsed canonical equality; unknown schema refuses, no fallback. Extend recovery fence deliveryKind with IMAGE; treat IMAGE identically to TEXT for free-form window, billing/caps, AGENT product-context commit and control/inbound gates. Replace every `deliveryKind==='TEXT'` gate that semantically means service-window reply with explicit TEXT-or-IMAGE; do not grant IMAGE template privileges. At final transaction time require latest inbound window open; expired -> suppression, no image/text send and no proactive-template substitution. General fence must explicitly enforce the same window for this new AGENT method; it cannot bypass recovery scope. HUMAN, automation, initial/outside-window templates retain prior behavior. No provider/R2 I/O while database locks held.

Provider `sendWhatsAppImage({to,link,caption,replyToProviderMessageId?},signal?)` sends one request `messaging_product:'whatsapp',type:'image',image:{link:plan.image.publicUrl,caption:plan.body}` plus existing reply context. No inline markdown URL, no Meta template name/components, no WABA new validation. IMAGE receipt follows existing markSent/provider failure/unknown outcome pathway. Dispatch key acquired before I/O, immutable thereafter, no duplicate send on requeue. Textplan uses existing sendWhatsAppText. A provider media failure after permit is a delivery failure, not permission to send a second text. Caption/body persisted once, one admission/counter/receipt. On cancellation/stale control/new inbound before admission no provider dispatch or context replacement. Document observable media omission reason and stage using existing shared logging; no tokens/source URLs/raw bodies.

## Rollout, acceptance and agent lifecycle
All normal tasks have execution_mode agent and completion_mode automatic, executor/claim null/attempt0 at definition. No developer takeover implied by authorship. Use normal /moda-task launcher-resolved isolated worktrees and mirrored task branches. No task agent merges/pushes main. Publication is a separate task with immutable archive/integrity/public-runtime/declaration evidence. Consumers pin recorded exact version/integrity, not sibling sources. Definition creation does not start any implementation or live initialization.

Order: Shared pure -> Shared Node -> publish; Database may proceed independently. Deploy migration, then Background and Commerce compatible readers; Admin editor/initializer activation only after both consumers report the new binding supported. Old readers reject unknown binding, so do not activate early. Script task depends on both consumer completion and Admin; manual deployment/readiness check also required before live operator use. System validation is terminal and requires explicit user launch for real infrastructure; fixtures may run within tasks. No production mutation or real WhatsApp send as automatic acceptance.

Deterministic acceptance uses fixed clocks/scripted model outputs/provider fixtures, two platforms and arbitrary merchandise (e.g. varnish volume and tree height, no clothes-only schema). Cases: one/multiple products first-only; selected variant exact; first missing image despite second available; known stock0/nottracked/unknown; product get without image; no selected product policy/returns/knowledge; Merchant Knowledge disabled; absent R2; timeout/unsafe URL/redirect/rebinding/transform/put/probe; contenthash reuse/collision; wrapper off/legacy/invalid hash/tampered binding; translated protected binding; Unicode caption1024/1025 and body4096/4097; agent prose preserved; no historical image leakage; longreply text-only without truncation; atomic plan/context/store; cancellation/inbound/control races; openwindow/closedwindow; retries/providerunknown no duplicate; initial/proactive approved template unchanged. Compare Studio plan to Background frozen plan for same inputs byte-for-byte after excluding no fields (clock not in plan). Assert exactly one provider call with expected payload or zero on gate refusal. No quality claim based solely on live model smoke.

## Task graph
SHARED-001 -> SHARED-002 -> SHARED-003(publication).
SHARED-003 -> ADMIN-001 and COMMERCE-001.
DATABASE-001 + SHARED-003 -> BACKGROUND-001.
ADMIN-001 + COMMERCE-001 + BACKGROUND-001 -> ADMIN-002(initializer).
All consumer/initializer tasks -> SYSTEM-TEST-001.

## Sources / transport constraints
[WhatsApp service-window policy](https://business.whatsapp.com/policy) and [Meta image media object](https://whatsapp.github.io/WhatsApp-Nodejs-SDK/api-reference/types/ImageMediaObject/) distinguish approved templates from free-form media. The 1024 code-point image-caption limit is the conservative implementation contract here; full text is retained when image omitted. No policy/pricing reinterpretation is introduced.

## Exact repository roots and completion handoff
All implementation paths above are relative to their named repository. Shared presentation files are under `src/commerce/presentation/`. Background service paths are under `src/services/`, its integration paths under `src/integration/`, and commerce host paths under `src/commerce/`. Admin service paths are under `src/lib/admin/whatsapp-templates/`, and UI paths under `src/components/admin/whatsapp-templates/`. Database schema is `prisma/schema.prisma`; migration directory follows the existing timestamped Prisma convention. Each task report must enumerate actual changed files and affected callers, including tests/mocks and serialization boundaries. A path renamed since definition must be traced by symbol and documented, not silently skipped.

Source provenance envelope is an internal host-to-Shared input only; it does not add fields to CommerceProductSchema, model tools or persisted public product contracts. Prepared image tenant/pair constraints are verified again by delivery-plan construction and final Background admission. SOURCE contains the platform for provenance; prepared image keys remain tenant/pair/content based. Allowed omission unions are closed; an unrecognized omission is a contract failure in tests, not a new runtime behavior invented by a consumer.

Initialization readiness check: before running APPLY on a deployed environment, the operator must record deployed Commerce and Background commit/package versions and their successful fixture smoke for the binding. Implementation tests never infer deployed compatibility from local source. The script itself reads no deployment API and cannot prove this prerequisite; its README must present it immediately before the apply command.

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

## Database accepted/completed frontier — 2026-11-09
DATABASE001 Complete at independently Accepted Attempt1, implementation75669477; exact nullable JSONB schema/DDL and fresh/upgrade/old-writer TEXT+IMAGE evidence pass. SHARED003 remains Pending; BACKGROUND001 remains Pending on that publication (Database prerequisite satisfied). SYSTEM-TEST001 remains Pending/manual-gated on unfinished consumers. No readiness promotion, task execution, migration deployment, activation or architectureImplemented claim.

## Shared Node accepted/completed frontier — 2026-11-09
SHARED001 and SHARED002 are Complete / independently Accepted Attempt1. Combined accepted Shared source `8f8a298de90803671b789ba0ef2fe03058a8023e` includes pure contract source `0b06467c37cbc4cd6ce67fcfa6e9c3fd7da66822`. Node extraction preserves original Background behavior; cancellation plumbing does not change golden encoded outputs. Optional absolute deadlineAt supplements the documented host child-signal contract; it retains the original turn deadline and subtracts the1000ms margin, capped5000ms.

SHARED003 is Ready, agent/automatic, Attempt0 unclaimed, explicitly depending on both accepted implementation tasks and restricted to release mechanics. ADMIN001, COMMERCE001 and BACKGROUND001 remain Pending until publication; DATABASE001 is already Complete. ADMIN002 remains Pending on its consumers/editor; SYSTEM-TEST001 remains Pending and manual-gated. Architecture remains In Progress. Readiness is not a claim, release, main integration, deployment, activation or live operation.

## Current accepted publication and execution frontier — 2026-11-09
SHARED003 Complete / independently Accepted Attempt1. Exact consumer pin `@modainteract/moda-interact-shared@5.12.0`; registry https://registry.npmjs.org/; SRI `sha512-RD3pGDVZHK8sRwbi91SpdouRDVkyf+4rhdB4eczaG48avsnEOQRhRccqzX2YI9KhXa1jXE4S2LHfz7D9DR5PEw==`; tarball SHA256 `e4416c765079a6c8c8ca04894e87e3822c3af0acf19428a5d3f542effe697393`. Release source12d0b85aaeefba4dfc46bb12637004f19d462b19 contains accepted Shared001/002 unchanged. Public archive matches reviewed upload and installed runtime/declaration/browser-isolation checks. This current frontier supersedes earlier readiness snapshots; historical records remain evidence of prior decisions.

| Task | Owner | Current status | Depends on |
|---|---|---|---|
| ARCH-068-SHARED-001 | moda_shared | Complete / Accepted Attempt1 | None |
| ARCH-068-SHARED-002 | moda_shared | Complete / Accepted Attempt1 | ARCH-068-SHARED-001 |
| ARCH-068-SHARED-003 | moda_shared | Complete / Accepted Attempt1 | ARCH-068-SHARED-001, ARCH-068-SHARED-002 |
| ARCH-068-DATABASE-001 | moda_database | Complete / Accepted Attempt1 | None |
| ARCH-068-ADMIN-001 | moda_admin | Ready / Attempt0 unclaimed | ARCH-068-SHARED-003 |
| ARCH-068-COMMERCE-001 | moda_commerce | Ready / Attempt0 unclaimed | ARCH-068-SHARED-003 |
| ARCH-068-BACKGROUND-001 | moda_background | Ready / Attempt0 unclaimed | ARCH-068-SHARED-003, ARCH-068-DATABASE-001 |
| ARCH-068-ADMIN-002 | moda_admin | Pending / Attempt0 | ARCH-068-ADMIN-001, ARCH-068-COMMERCE-001, ARCH-068-BACKGROUND-001 |
| ARCH-068-SYSTEM-TEST-001 | moda_system_test | Pending / manual-gated | ARCH-068-COMMERCE-001, ARCH-068-BACKGROUND-001, ARCH-068-ADMIN-002 |

Consumers pin exact5.12.0 with this integrity; browser contracts and Node media remain separate public subpaths. Readiness starts no implementation. Architecture remains In Progress; deploy migration before Background runtime field use, deploy both compatible consumers before activation, retain initializer/operator deployment check and terminal manual system validation. No main merge/push, gitlink advance, migration deployment, initializer run, activation or real send occurred in this review.
