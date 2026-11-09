---
id: ARCH-067-SHARED-001
architecture_id: ARCH-067
title: Define shared references, stock facts and WhatsApp composition
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
created: 2026-11-09
updated: 2026-11-09
---
# Define shared references, stock facts and WhatsApp composition

## Objective and binding specification
Implement the owned portion of [ARCH-067](../../../architecture/ARCH-067-product-reference-and-current-stock-parity.md). Every schema, mapping, persistence, rendering, diagnostic and compatibility rule there is normative. No merchandise-specific behavior. Dependencies must be complete before execution.

## Exact work and touch points
Owned touch points: src/commerce/schemas.ts; product-context.ts and tests; instructions.ts; runner/graph/nodes/invoke-model.ts; runner/index.ts; runner/preflight.ts; model/openrouter-model-client.internal.ts serialization tests; presentation/facts.ts, fact-messages.ts, schemas.ts, compose.ts, render.ts, index.ts; commerce public index.ts and public import validation scripts. Implement every Shared contract in the architecture document; extend exported types and generated tool output JSON schemas through existing generation. Do not create parallel inventory facts/renderers in hosts. Test built public runtime and declarations, not only source imports. Tests: legacy context/product fixtures; selected options arbitrary names (height, finish, volume as well as color); presentation ordered [20,3] survives recency sorting [3,20]; ambiguous labels require clarification; all stock states and0; invalid/negative/unsafe count normalization semantics; context size/TTL/ownership; no stale count authority; exact WhatsApp body and locale/length boundaries. Run npm run typecheck, npm run build and targeted product-context/presentation/runner/model tests using repository scripts. Record accepted source/build archive provenance for publication.

## Exact Zod additions and public API (binding)
Use the existing `zod` dependency and `z.infer`; no second validation library, hand-written duplicate host interfaces or new database schema. This section specifies the implementation, not an already implemented API.

### 1. `src/commerce/schemas.ts`
Add before CommerceProductSchema:
```ts
export const CommerceProductStockSchema = z.discriminatedUnion('status', [
  z.strictObject({
    status: z.literal('KNOWN'),
    quantity: z.number().int().min(0).max(Number.MAX_SAFE_INTEGER),
    scope: z.enum(['PRODUCT', 'VARIANT']),
  }),
  z.strictObject({ status: z.literal('NOT_TRACKED') }),
  z.strictObject({ status: z.literal('UNAVAILABLE') }),
]);
export type CommerceProductStock = z.infer<typeof CommerceProductStockSchema>;
export function normalizeCommerceStockQuantity(value: unknown): number | null {
  return typeof value === 'number' && Number.isSafeInteger(value)
    ? Math.max(0, value) : null;
}
```
Add exactly this property to existing CommerceProductSchema; retain all existing properties:
```ts
stock: CommerceProductStockSchema.optional(),
```
Do not coerce numeric strings, null, booleans or decimals. No quantity/default on NOT_TRACKED/UNAVAILABLE: strict schemas reject such fields. Numeric negative provider quantities normalize to0 before schema parsing, but a negative wire quantity fails validation. `available` retains its independent current behavior. Public CommerceToolOutputs search/get already reference CommerceProductSchema: retain that relationship; update their generated descriptor projections rather than introducing separate schemas.

### 2. `src/commerce/product-context.ts`
Replace the inline reference object with these exported schemas, using existing `id` (string1..128) and `date` (UTC z.iso.datetime({offset:false})):
```ts
export const CommerceProductReferencePairSchema = z.strictObject({
  productId: id,
  variantId: id.nullable(),
});
export type CommerceProductReferencePair =
  z.infer<typeof CommerceProductReferencePairSchema>;
export const CommerceConversationProductReferenceSchema =
  CommerceProductReferencePairSchema.extend({
    title: z.string().min(1).max(512),
    observedAt: date,
    selectedOptions: CommerceProductSelectedOptionsSchema.optional(),
  });
export const CommerceProductPresentationSchema = z.strictObject({
  references: z.array(CommerceProductReferencePairSchema).max(3).refine(
    rows => new Set(rows.map(r => JSON.stringify([r.productId,r.variantId]))).size === rows.length,
    'Duplicate presented product',
  ),
  presentedAt: date,
});
export type CommerceProductPresentation =
  z.infer<typeof CommerceProductPresentationSchema>;
```
Import CommerceProductSelectedOptionsSchema from schemas.ts. It is the existing canonical normalizer: at most16 selected name/value pairs; reuse its optionLabel constraints and normalization exactly, without introducing color/size enums. Each existing optionLabel replaces CR/LF/tab sequences with one space, trims, requires1..128 characters and rejects remaining C0/C1 control characters; selectedOptions normalizes non-arrays to[], examines first16 entries, drops invalid labels and deduplicates exact name/value pairs. Keep reference title/observedAt unchanged; native identity validation still runs in the outer context.

The complete context object shape before superRefine is exactly:
```ts
z.strictObject({
  schemaVersion: z.literal(1),
  shopId: id,
  conversationId: id,
  platform: z.enum(['SHOPIFY','WOOCOMMERCE']),
  references: z.array(CommerceConversationProductReferenceSchema).max(20),
  updatedAt: date,
  presentation: CommerceProductPresentationSchema.optional(),
})
```
Retain the existing platform-specific native-ID and32768-byte checks. Extend superRefine to reject any presentation pair absent from references and any duplicate pair in references. A zero-length presentation is valid and explicitly clears the last displayed list; absence means legacy/no recorded list. No stock/price/description fields are admitted in context. Freshness remains a merge/read concern, using the existing24-hour window and identity.now (not Date.now inside pure helpers).

Expose this exact signature:
```ts
export function recordCommerceProductPresentation(
  context: CommerceConversationProductContext,
  pairs: readonly CommerceProductReferencePair[],
  identity: CommerceProductContextIdentity,
): CommerceConversationProductContext;
```
Algorithm: first merge(context,[],identity) to enforce ownership/freshness; safeParse a copied pairs array against presentation references schema; reject duplicate/missing/expired pairs with Error('PRODUCT_PRESENTATION_INVALID'); preserve supplied order; attach presentedAt=new Date(identity.now).toISOString(); leave general references/updatedAt unchanged; parse the complete result. Do not silently truncate supplied pairs. Final size failure also raises PRODUCT_PRESENTATION_INVALID. All successful replies record the actual rendered ordered pairs (empty when no product is displayed), so 'first' never refers to an older list hidden by a later reply.

In mergeConversationProductContext, copy normalized selectedOptions from each canonical observation when supplied; retain previous optional value when a newer observation omits it, replace when newer observation supplies it (including []). Preserve previous presentation only while presentedAt and every referenced pair remain fresh and retained; otherwise remove it entirely. Merge must not create/reorder presentation from search results. When trimming for byte budget, remove presentation first, then existing oldest-reference trimming. Validate final object. Existing exact-ID/title resolver signature and MISSING/AMBIGUOUS behavior remain; no fuzzy automatic selection introduced.

### 3. `src/commerce/presentation/facts.ts`
Extend the existing CommerceProductFactSchema with exactly:
```ts
stock: CommerceProductStockSchema,
observedAt: DateSchema,
```
Import both existing schemas from their canonical modules; retain current IDs,title,description,attributes,options,selectedOptions unchanged. `verifyCommerceProductFacts` retains its current signature/result union and exact-pair checks. In each verified fact set:
```ts
stock: product.data.stock ?? {status:'UNAVAILABLE'},
observedAt: product.data.observedAt,
```
No freshness claim is made merely by parsing observedAt: the host must supply the fresh authorized read stipulated in the contract. The model's answer schema stays unchanged: productDetailSelections is at most3 unique productId/variantId pairs, never stock quantities. Reuse PRODUCT_DETAILS rather than adding an INVENTORY answer kind.

In fact-messages.ts add a typed per-supported-locale stock message record (all existing supported locales required; no English fallback). English source strings are exactly: PRODUCT known `Available quantity: {quantity}.`; VARIANT known `Available quantity for this option: {quantity}.`; NOT_TRACKED `Exact stock quantities are not tracked.`; UNAVAILABLE `Exact stock quantity is currently unavailable.` Render after existing description/attribute/option lines. Localize quantity with Intl.NumberFormat(locale,{useGrouping:false,maximumFractionDigits:0}); replace only the quantity placeholder, with no interpolation of model prose. Keep existing partial-description notices. Stock unknown must not force referral when product identity/details are otherwise verified.

### 4. Exports, JSON and compatibility tests
Export all new schemas/types/functions from commerce public index.ts; presentation index.ts retains/export updated fact schemas. Generated declarations must resolve through published `@modainteract/moda-interact-shared/commerce`. No root/private-path import required. Do not change response disposition enum, presentation selection schema, existing optional fields or database schemaVersion.

Add exact parser boundary tests: quantities0 and Number.MAX_SAFE_INTEGER pass; -1,0.5,MAX_SAFE_INTEGER+1,'2',null fail KNOWN wire parsing; NOT_TRACKED with quantity fails; stock omission on legacy product passes but verified fact yields UNAVAILABLE; legacy context lacking both additions passes; reference21/presentation4/duplicate/missing pair fails; ordered presentation preserves input independent of lexical IDs; selectedOptions uses existing normalization; serialized32768/32769 boundary; future/expired observations and foreign shop/conversation fail existing read/merge fences. Built OpenRouter request JSON must include ordered presentation plus selectedOptions, without stock as persisted reference authority. Test successful composition then failed next turn retains state, and successful no-product reply clears presentation. Preserve all existing wrapper/body limits and public schema export checks.

## Acceptance criteria
All owned requirements above and architecture contract are implemented and verified. List every actual changed path and test result. Shared behavior must be imported through published public exports; no copied cross-repository source. Unknown inventory remains distinct from zero. Existing authorization, checkout ownership, WhatsApp composition and replay rules pass regression checks. No unresolved design choices may be silently substituted; report a concrete contract conflict before implementing an alternative.

## Non-goals
No inventory mutation, new database table, token-refresh redesign, new template approval/WABA validation, category sequencing redesign or budget increase.

## Completion Report
Status: Not started.
Implementation SHA: Pending.
Validation: Pending.
Deployment/compatibility evidence: Pending.

## Architect Review
Status: Not reviewed.
