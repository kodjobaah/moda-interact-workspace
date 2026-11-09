---
id: ARCH-068-SHARED-003
architecture_id: ARCH-068
title: Publish reviewed conversation image contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ['ARCH-068-SHARED-001', 'ARCH-068-SHARED-002']
enables: ["ARCH-068-ADMIN-001", "ARCH-068-BACKGROUND-001", "ARCH-068-COMMERCE-001"]
created: 2026-11-09
updated: 2026-11-09
---
# Publish reviewed conversation image contracts

## Architecture and objective
Implement the owned portion of [binding ARCH-068](../../../architecture/ARCH-068-optional-conversation-product-image.md). The entire contract is normative, including exact schemas, transport/failure rules, initialization, rollout and acceptance matrix. Read it before execution.

## Context and scope
Publication only. Require SHARED-001/002 Complete/Accepted and record their exact final source/build provenance. Select an unused semver version according to existing package release policy, recording exact version here and in handoff; do not predeclare an invented version. Version metadata only, pack/publish accepted source; no implementation redesign or broad validation rerun merely for release. Verify downloaded public tarball SHA256/SRI matches reviewed archive and installed JS+declaration imports of binding/schema/plan/Node preparer and all legacy entrypoints. Record browser/Node separation, package engine/runtime dependencies and exact consumer install version/SRI. Consumers stay Pending until completion/public availability. Update owned publication receipt and dependency-ready statuses only through normal architect reconciliation. No consumer edits/main merge/deployment.

## Interfaces and contracts
The named exported schemas/APIs and exact JSON shapes in the binding contract are authoritative. Existing v1 template hashes/legacy records remain compatible. No clothing-specific fields/model image URL or Meta recovery contract extension.

## Work Items
- [ ] Verify both implementation prerequisites are Complete/Accepted and identify their exact accepted source/build provenance.
- [ ] Select an unused release version and apply only authorized release metadata.
- [ ] Pack/publish accepted artifacts using approved release mechanics without implementation revalidation.
- [ ] Verify the exact registry version and downloaded tarball hash/SRI; verify installed JS/declaration exports and legacy entrypoints.
- [ ] Push release changes and the publication receipt on mirrored task branches; stop for architect review.

## Dependencies
ARCH-068-SHARED-001 and ARCH-068-SHARED-002 — both Complete / Accepted Attempt1.

## Acceptance criteria
Both accepted capabilities are included in the released artifact. Exact version, archive SHA256/SRI, registry availability, runtime/declaration imports, browser/Node separation and consumer install coordinates are recorded. Source changes are limited to release metadata. No consumer implementation, deployment or activation occurs.

## Validation
- [ ] Both implementation prerequisites are Complete/Accepted before release.
- [ ] Approved unused version and accepted source/build artifacts identified.
- [ ] Publication succeeds and exact version is available at the intended registry.
- [ ] Downloaded archive SHA256/SRI matches the reviewed release artifact.
- [ ] Installed public runtime/declaration export checks pass, including legacy exports.
- [ ] No unauthorized implementation source changed; do not rerun unit/integration tests, lint, typecheck or production build merely to revalidate accepted code. A package command's required artifact-packaging lifecycle is release mechanics, not a discretionary implementation rerun.

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

## Architect readiness handoff — 2026-11-09
Ready, Attempt0 unclaimed. Accepted SHARED001 source `0b06467c37cbc4cd6ce67fcfa6e9c3fd7da66822` is an ancestor of accepted SHARED002 source `8f8a298de90803671b789ba0ef2fe03058a8023e`. Use this exact accepted source/artifact provenance; task completion does not imply main integration. Both task records carry independent acceptance. No implementation worktree or release claim is created by readiness reconciliation. Consumers stay Pending until this publication is accepted Complete and exact public artifact coordinates are recorded.
