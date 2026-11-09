---
id: ARCH-068-ADMIN-001
architecture_id: ARCH-068
title: Author and preview optional AI wrapper media
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ['ARCH-068-SHARED-003']
enables: ["ARCH-068-ADMIN-002"]
created: 2026-11-09
updated: 2026-11-09
---
# Author and preview optional AI wrapper media

## Architecture and objective
Implement the owned portion of [binding ARCH-068](../../../architecture/ARCH-068-optional-conversation-product-image.md). The entire contract is normative, including exact schemas, transport/failure rules, initialization, rollout and acceptance matrix. Read it before execution.

## Context and scope
ADMIN-001 consumes Shared publication. Touch authoring/{types,validation,compiler,preview}.ts, compilation/{wrapper-compiler,reconstruction,contracts}.ts, wrappers/{eligibility,preview,service}.ts, translation source snapshot/protected binding checks, DTO/server actions/routes that carry draft/prepared/preview, components under authoring (template-content-editor, wrapper-structure-editor, template-read-only-preview, template-editor-steps) and wrappers/wrapper-before-after-preview/compilation/conversation-wrapper-review-preview. Add a wrapper-only toggle default false with explanatory “One verified product image above the response; omitted when unavailable” and an illustrative preview. Uses exact shared schema. Binding preserved in compile/clone/translation/review, included source/prepared hashes; locale eligibility requires binding equality across all locales. Meta AST rejects this key; HUMAN/SHARED wrapper editor rejects it for this phase; supported audience AI only, checked server-side. Existing text URL fields remain text. Do not fetch live merchant images in Admin preview or read R2 secrets there.

The initializer script is owned by ADMIN-002; do not implement or run it in this task.

## Interfaces and contracts
The named exported schemas/APIs and exact JSON shapes in the binding contract are authoritative. Existing v1 template hashes/legacy records remain compatible. No clothing-specific fields/model image URL or Meta recovery contract extension.

## Work Items
- [ ] Verify dependencies and current owned source against binding touch points.
- [ ] Implement every requirement in the owned scope and binding contract.
- [ ] Add deterministic success/failure/compatibility tests specified above.
- [ ] Run declared repository validation and record exact evidence.
- [ ] Publish implementation and parent report on mirrored task branches for review.

## Dependencies
ARCH-068-SHARED-003

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

## Accepted publication handoff — 2026-11-09
SHARED003 is Complete / independently Accepted Attempt1. Install exactly `@modainteract/moda-interact-shared@5.12.0`, registry https://registry.npmjs.org/, SRI `sha512-RD3pGDVZHK8sRwbi91SpdouRDVkyf+4rhdB4eczaG48avsnEOQRhRccqzX2YI9KhXa1jXE4S2LHfz7D9DR5PEw==`, tarball SHA256 `e4416c765079a6c8c8ca04894e87e3822c3af0acf19428a5d3f542effe697393`. Release source `12d0b85aaeefba4dfc46bb12637004f19d462b19` includes both accepted Shared capabilities. Use browser-safe `/commerce/presentation` for contracts and Node-only `/commerce/presentation/node` for media preparation; no sibling source import or copied generic mechanics. Ready at unchanged Attempt0, executor/claimed_at null; no claim or implementation begins here.
