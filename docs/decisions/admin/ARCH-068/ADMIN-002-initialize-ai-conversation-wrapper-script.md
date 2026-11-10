---
id: ARCH-068-ADMIN-002
architecture_id: ARCH-068
title: Initialize AI conversation wrapper safely
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ['ARCH-068-ADMIN-001', 'ARCH-068-COMMERCE-001', 'ARCH-068-BACKGROUND-001']
enables: ["ARCH-068-SYSTEM-TEST-001"]
created: 2026-11-09
updated: 2026-11-09
---
# Initialize AI conversation wrapper safely

## Architecture and objective
Implement the owned portion of [binding ARCH-068](../../../architecture/ARCH-068-optional-conversation-product-image.md). The entire contract is normative, including exact schemas, transport/failure rules, initialization, rollout and acceptance matrix. Read it before execution.

## Context and scope
ADMIN-002 adds `scripts/initialize-conversation-wrapper.mjs`, server core `src/lib/admin/whatsapp-templates/wrappers/initialize.ts`, package command `whatsapp:initialize-conversation-wrapper`, README and disposable DB tests. Exact CLI: `--environment=test|production --actor-admin-id=<id> --dry-run|--apply --reason=<10..500 chars>`; default dry-run, mutually exclusive modes, unknown args fail. Resolve trusted deployment environment using existing Admin runtime configuration and require exact match with requested environment; production is supported but never executed by implementation/tests. Actor must already exist and have SUPER_ADMIN role; never synthesize/elevate actor.

Exact source: schemaVersion1/family MODA_CONVERSATION_WRAPPER/sourceLanguageTag en/audience AI/header[]/body[{type:'slot',name:'response.body'}]/footer[]/conditionals[]/productImage{variable:'response.productImage',placement:'BEFORE_BODY',optional:true}. Use canonical compiler and hash helpers. Stable submission UUID is `e14e7967-05bb-4a5c-bacf-0663b42b37d5`, derive definitionIdForSubmit(actorId,uuid). Same actor repeat verifies byte-identical immutable source/prepared; mismatch fails, never edits existing definition. Existing occupied AI slot: identical canonical desired prepared/binding and eligible definition -> UNCHANGED even if different author ID; any other active definition -> SLOT_OCCUPIED, no writes, no overwrite/force flag. Empty slot -> create/save immutable definition and locales and activate atomically in one SERIALIZABLE transaction; concurrent empty-slot initialization loses cleanly with conflict, no orphan partial template.

All20 existing REVIEW_LANGUAGES locales use precisely the slot-only AST, identical binding, no prose. English SOURCE_SAVED; other languages REVIEWED with supplied superadmin actor, common transaction timestamp, providerLanguageCode null. This is operator approval of language-invariant structural content, not fabricated translation review. Reuse existing eligibility and activation/audit semantics via extracted transaction-internal service functions, not nested transactions or direct unchecked pointer SQL. Audit metadata identifies script/version/structural-only locales/source+content hashes/previous slot; reason provided by operator. Never create a Meta registration/submission job. Dry-run writes nothing and reports planned definition ID/hash/locale count/current pointer; apply returns CREATED_AND_ACTIVATED or UNCHANGED; failures typed INVALID_ARGUMENT/ENVIRONMENT_MISMATCH/ACTOR_DENIED/IMMUTABLE_CONFLICT/SLOT_OCCUPIED/CONCURRENT_STATE_CHANGE. Output no secrets/customer data. No automatic execution against test/production in task.

## Interfaces and contracts
The named exported schemas/APIs and exact JSON shapes in the binding contract are authoritative. Existing v1 template hashes/legacy records remain compatible. No clothing-specific fields/model image URL or Meta recovery contract extension.

## Work Items
- [ ] Verify dependencies and current owned source against binding touch points.
- [ ] Implement every requirement in the owned scope and binding contract.
- [ ] Add deterministic success/failure/compatibility tests specified above.
- [ ] Run declared repository validation and record exact evidence.
- [ ] Publish implementation and parent report on mirrored task branches for review.

## Dependencies
ARCH-068-ADMIN-001, ARCH-068-COMMERCE-001, ARCH-068-BACKGROUND-001

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

## Commerce completion dependency reconciliation — 2026-11-10
COMMERCE001 and BACKGROUND001 Complete satisfy both consumer prerequisites; task remains Pending until ADMIN001 (currently Review) is Complete. No initialization/apply authorized by reconciliation.
