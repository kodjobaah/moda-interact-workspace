---
id: ARCH-068-SYSTEM-TEST-001
architecture_id: ARCH-068
title: Verify Studio and Background text/media parity
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ['ARCH-068-COMMERCE-001', 'ARCH-068-BACKGROUND-001', 'ARCH-068-ADMIN-002']
enables: []
created: 2026-11-09
updated: 2026-11-10
---
# Verify Studio and Background text/media parity

## Architecture and objective
Implement the owned portion of [binding ARCH-068](../../../architecture/ARCH-068-optional-conversation-product-image.md). The entire contract is normative, including exact schemas, transport/failure rules, initialization, rollout and acceptance matrix. Read it before execution.

## Context and scope
All normal tasks have execution_mode agent and completion_mode automatic, executor/claim null/attempt0 at definition. No developer takeover implied by authorship. Use normal /moda-task launcher-resolved isolated worktrees and mirrored task branches. No task agent merges/pushes main. Publication is a separate task with immutable archive/integrity/public-runtime/declaration evidence. Consumers pin recorded exact version/integrity, not sibling sources. Definition creation does not start any implementation or live initialization.

Order: Shared pure -> Shared Node -> publish; Database may proceed independently. Deploy migration, then Background and Commerce compatible readers; Admin editor/initializer activation only after both consumers report the new binding supported. Old readers reject unknown binding, so do not activate early. Script task depends on both consumer completion and Admin; manual deployment/readiness check also required before live operator use. System validation is terminal and requires explicit user launch for real infrastructure; fixtures may run within tasks. No production mutation or real WhatsApp send as automatic acceptance.

Deterministic acceptance uses fixed clocks/scripted model outputs/provider fixtures, two platforms and arbitrary merchandise (e.g. varnish volume and tree height, no clothes-only schema). Cases: one/multiple products first-only; selected variant exact; first missing image despite second available; known stock0/nottracked/unknown; product get without image; no selected product policy/returns/knowledge; Merchant Knowledge disabled; absent R2; timeout/unsafe URL/redirect/rebinding/transform/put/probe; contenthash reuse/collision; wrapper off/legacy/invalid hash/tampered binding; translated protected binding; Unicode caption1024/1025 and body4096/4097; agent prose preserved; no historical image leakage; longreply text-only without truncation; atomic plan/context/store; cancellation/inbound/control races; openwindow/closedwindow; retries/providerunknown no duplicate; initial/proactive approved template unchanged. Compare Studio plan to Background frozen plan for same inputs byte-for-byte after excluding no fields (clock not in plan). Assert exactly one provider call with expected payload or zero on gate refusal. No quality claim based solely on live model smoke.

## Interfaces and contracts
The named exported schemas/APIs and exact JSON shapes in the binding contract are authoritative. Existing v1 template hashes/legacy records remain compatible. No clothing-specific fields/model image URL or Meta recovery contract extension.

## Work Items
- [ ] Verify dependencies and current owned source against binding touch points.
- [ ] Implement every requirement in the owned scope and binding contract.
- [ ] Add deterministic success/failure/compatibility tests specified above.
- [ ] Run declared repository validation and record exact evidence.
- [ ] Publish implementation and parent report on mirrored task branches for review.

## Dependencies
ARCH-068-COMMERCE-001, ARCH-068-BACKGROUND-001, ARCH-068-ADMIN-002

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
COMMERCE001 and BACKGROUND001 Complete satisfy consumer prerequisites; task remains Pending until ADMIN002 Complete, terminal manual execution gate unchanged.


## Accepted implementation frontier / manual launch handoff — 2026-11-10
Ready at unchanged Attempt0, executor/claimed_at null. Explicit prerequisites COMMERCE001, BACKGROUND001 and ADMIN002 are independently Accepted/Complete at Attempt1; accepted source commits are respectively `ee42e4e4894361138ea13aad4ce5e7213461d47e`, `383efdce24fb60888ff91bc260ff13b4b524b7dd` and `40fc5b67e6a814020668a6d4ae25eaa7c0d5f17a`. Their accepted task records accompany this parent handoff. Shared remains exact published5.12.0 with SRI `sha512-RD3pGDVZHK8sRwbi91SpdouRDVkyf+4rhdB4eczaG48avsnEOQRhRccqzX2YI9KhXa1jXE4S2LHfz7D9DR5PEw==`.

Readiness is not a claim or execution. The developer manually exercises the completed feature and explicitly launches this terminal task when ready. Disposable local fixtures/provider emulators are the acceptance path; real infrastructure or WhatsApp sends require separate explicit authorization. No initializer apply, migration deployment or activation occurs here. Source acceptance does not imply main integration or deployed compatibility; consume the accepted versions through the task's normal isolated preparation. Architecture remains In Progress pending integrated validation/architect acceptance.
