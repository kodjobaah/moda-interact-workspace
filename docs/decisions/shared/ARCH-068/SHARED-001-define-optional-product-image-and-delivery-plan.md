---
id: ARCH-068-SHARED-001
architecture_id: ARCH-068
title: Define shared optional image binding and one-message delivery plan
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-11-09T20:42:01Z
attempt: 1
depends_on: []
enables: ["ARCH-068-SHARED-002"]
created: 2026-11-09
updated: 2026-11-09
---
# Define shared optional image binding and one-message delivery plan

## Architecture and objective
Implement the owned portion of [binding ARCH-068](../../../architecture/ARCH-068-optional-conversation-product-image.md). The entire contract is normative, including exact schemas, transport/failure rules, initialization, rollout and acceptance matrix. Read it before execution.

## Context and scope
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

## Interfaces and contracts
The named exported schemas/APIs and exact JSON shapes in the binding contract are authoritative. Existing v1 template hashes/legacy records remain compatible. No clothing-specific fields/model image URL or Meta recovery contract extension.

## Work Items
- [ ] Verify dependencies and current owned source against binding touch points.
- [ ] Implement every requirement in the owned scope and binding contract.
- [ ] Add deterministic success/failure/compatibility tests specified above.
- [ ] Run declared repository validation and record exact evidence.
- [ ] Publish implementation and parent report on mirrored task branches for review.

## Dependencies
None; Ready for normal agent launch. No claim yet.

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
