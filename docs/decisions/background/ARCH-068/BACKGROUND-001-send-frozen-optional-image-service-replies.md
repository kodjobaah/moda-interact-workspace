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
status: complete
priority: 30
executor: null
claimed_at: null
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
- [x] Verify dependencies and current owned source against binding touch points.
- [x] Implement every requirement in the owned scope and binding contract.
- [x] Add deterministic success/failure/compatibility tests specified above.
- [x] Run declared repository validation and record exact evidence.
- [x] Publish implementation and parent report on mirrored task branches for review.

## Dependencies
ARCH-068-SHARED-003, ARCH-068-DATABASE-001

## Acceptance criteria
All owned scope above is complete, exact contract tests pass and no TODO/placeholder or unresolved cross-service choice remains. For tasks consuming Shared, prove the dependency using the exact published artifact; no sibling source imports/copied mechanics. Record actual changed paths and checks. Preserve existing grounded text, product identity, moderation/send fences, initial/proactive Meta flows.

## Out of Scope
No redesign of aspects 1 and 3, Meta submission/WABA validation, inventory write, unrelated cleanup, budget increase, production mutation or automatic live initializer.

## Agent execution and review
Execution is owned by the assigned agent, not a human developer. Use /moda-task with canonical isolated parent/implementation worktrees and mirrored task branches. Do not claim on authoring. Implement only this repository portion; use published Shared APIs. If an actual source conflict contradicts the exact binding contract, report it to the architect with path/symbol/evidence; do not invent a replacement architecture or leave a placeholder. No main merge/push, production mutation, real send or live initializer execution is part of this task.

## Completion Report
### Attempt 1 — Ready for Review (2026-11-10)

Implementation: `383efdce24fb60888ff91bc260ff13b4b524b7dd`, committed and pushed to implementation `task/ARCH-068-BACKGROUND-001`; independently matched `git ls-remote` and clean implementation worktree. This repository-agent return awaits architect review; no acceptance/completion decision is made here.

Implemented the original scope: AGENT answer prose and verified pair order survive wrapper composition; trusted REFER_TO_STORE contact/language normalization remains before the verified envelope is passed to the wrapper. Optional media uses the public Shared selector/preparer/builder, original deadline and bounded configuration wait. Complete validated plans bind wrapper response/application digests and replay. Atomic preparation scopes the locked outbound AGENT message to canonical tenant/conversation, writes body plus JSON, refuses plan replacement and legacy downgrade. General/recovery final fences compare body/plan and independent message/conversation/inbound/control/tenant/first-pair receipt, apply free-form window gates, and acquire the existing dispatch permit before one provider call. IMAGE cannot claim template privileges. Existing moderation, billing/caps, product-context atomic commit, provider unknown handling and legacy templates remain in their existing pipeline. Cancelled host signals do not dispatch or replace context.

Generic fetch/DNS/TLS, byte verification, brand/product transforms, immutable PUT/HEAD and public probe bodies were replaced by published Shared reexports; Background retains configuration, orchestration, brand/outreach key predicates and final fences. No image byte/key/hash golden expectation was regenerated.

Exact dependency: `@modainteract/moda-interact-shared@5.12.0`, lockfile SRI `sha512-RD3pGDVZHK8sRwbi91SpdouRDVkyf+4rhdB4eczaG48avsnEOQRhRccqzX2YI9KhXa1jXE4S2LHfz7D9DR5PEw==`; installed public registry artifact, no sibling imports. Prepared database gitlink `5329d5390d346042895219663f3a040ea54ae168` retained unchanged, generated Prisma client passed. Migration deployment remains a separate runtime rollout prerequisite; no deployment or activation occurred.

Preparation reused the exact launcher packet paths: primary workspace `moda-interact-workspace`, parent `moda-interact-workspace-task-ARCH-068-BACKGROUND-001`, implementation `moda-interact-workspace.worktrees/ARCH-068-BACKGROUND-001`, both mirrored branch `task/ARCH-068-BACKGROUND-001`. Parent baseline `2e175c89e5cfd47c12f1e3412aceeb16973fb5c9` reused; implementation baseline `40a43b7e90bcac65ed2270f4e586d00bda0dd0dd` created; own-remote FF not needed, main synchronization passed, recursive database submodule initialized/ready. Dependencies SHARED003 and DATABASE001 Complete were launcher-verified. Claim `65d25169d01b08cda7b27ed8d3522cbed7d12d15`, codex at `2026-11-10T00:04:10Z`; Attempt 1 preserved, claim cleared on return.

Validation:

- Existing media/security/fixed-output compatibility: 14 files / 146 tests passed. Included unchanged brand/outreach fetch, transform, writer, processor and resolver behavior.
- Final owned regression group: 49 files / 564 tests passed, covering wrappers/plan replay and both-platform IMAGE composition, processor signal cancellation, outbound admission/delivery, moderation, billing/credit, brand/outreach and template preparation. No deleted cases, skips or expected failures were introduced.
- Declared `test:commerce-host` configuration: 78 tests passed. Preserves attacker-contact referral rejection/trusted locale fallback and proves grounded ANSWER prose with exact fresh selected product metadata. Prior deterministic ANSWER candidate-shrink assertions were adapted to the normative full-answer behavior; oversize full wrapper still refuses rather than silently shrinking facts.
- Actual disposable PostgreSQL (`node scripts/test-integration.mjs tests/integration/arch068-conversation-image.integration.test.ts tests/integration/general-outbound-stop-fence.integration.test.ts`): 2 files / 19 tests passed. Sixteen new cases prove body/plan persistence, one image dispatch under concurrent sends, unknown-provider replay/no second text, current free-form window, receipt and cross-shop zero-write refusal, legacy IMAGE downgrade refusal, immutable/unknown-schema mismatch, recovery IMAGE control/inbound/window/tamper/pair gates and context committed once. Three existing STOP/Shop-lock ordering cases retained. Eligibility/moderation/provider boundaries are scripted; database locks, preparation, final permits and context persistence are real SQL. Existing billing suites supply the preserved caps/credit semantics; the new recovery final-permit fixture does not claim a live entitlement/billing integration.
- Final focused IMAGE-kind guard: 5 tests passed, including missing plan and IMAGE-to-TEMPLATE mismatch denied before SQL.
- Declared `npm run build` passed (exit 0), including Prisma generation, application/provision TypeScript and artifact packaging. Standalone compiler checks also passed.
- All changed/new TypeScript scoped ESLint and `git diff --check` passed. Full `npm run lint` exits 1 solely on untouched `src/providers/shopify-whatsapp-consent.provider.ts:151:37` (`no-control-regex`, `\x00`), byte-identical to prepared baseline `40a43b7e90bcac65ed2270f4e586d00bda0dd0dd`. No task diagnostic remains; no baseline ID is invented.

Evidence logs: `/private/tmp/arch068-background-media.log`, `arch068-background-regressions.log`, `arch068-background-host2.log`, `arch068-background-final-guard-db.log`, `arch068-background-kind-fence.log`, `arch068-background-final-build.log` and `.exit`, `arch068-background-final-lint.log` and `.exit`, `arch068-background-final-scoped-lint.log`. Final build exit 0; full lint exit 1 as stated above.

No main merge, live provider/customer send, R2 live write, deployment, initializer activation, other implementation repository edit or follow-on execution occurred. Studio parity uses the same public Shared plan construction input/output in the wrapper fixtures; terminal cross-host system validation remains SYSTEM-TEST001-owned.

Changed paths:
```text
package-lock.json
package.json
src/agents/types.ts
src/commerce/host.ts
src/integration/whatsapp/types.ts
src/services/conversation-delivery-plan.ts
src/services/conversation-product-media.ts
src/services/conversation-turn-processor.service.ts
src/services/conversation-wrappers/compose-ai-outbound.ts
src/services/conversation-wrappers/contracts.ts
src/services/conversation-wrappers/service.ts
src/services/merchant-knowledge-network-policy.ts
src/services/outbound-whatsapp-admission.service.ts
src/services/outbound-whatsapp-admission/general-outbound-send-fence.service.ts
src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts
src/services/recovery-conversation/outbound-send-fence.service.ts
src/services/recovery-product-media/product-image-transformer.ts
src/services/shop-brand-media/contracts.ts
src/services/shop-brand-media/image-transformer.ts
src/services/shop-brand-media/metadata-verifier.ts
src/services/shop-brand-media/public-probe.ts
src/services/shop-brand-media/r2-writer.ts
src/services/shop-brand-media/safe-fetch.ts
src/services/whatsapp.service.ts
tests/integration/arch068-conversation-image.integration.test.ts
tests/integration/commerce/host-suites/recommendations.ts
tests/unit/services/arch068-conversation-media.test.ts
tests/unit/services/conversation-turn-processor.service.test.ts
tests/unit/services/conversation-wrappers/service.test.ts
tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts
tests/unit/services/whatsapp.service.test.ts
```


## Architect Review
### Review Status
Accepted — Attempt 1, 2026-11-10. Automatic completion applied; executor and claimed_at remain null.

### Review Notes
Independently reviewed implementation `383efdce24fb60888ff91bc260ff13b4b524b7dd` and published report `427d2bbb9484bbc482b15020f09ab3893997a95e`. Actual source preserves grounded ANSWER prose, verified pair order and trusted referral normalization; uses published Shared media primitives without duplicate generic bodies; freezes validated complete plans in wrapper digests and scoped atomic preparation; and compares tenant/pair/message/inbound/control/body/plan under final locks before one provider dispatch. IMAGE retains service-window, moderation, eligibility/billing and context gates and cannot claim TEMPLATE privileges. Legacy null records and pending frozen plans cannot silently upgrade/downgrade; unknown provider outcome does not trigger a second text send.

### Reviewed Files
Host and processor; wrapper contracts/composition/service; conversation-product-media and conversation-delivery-plan; public admission/delivery; general and recovery final fences; WhatsApp image transport; compatibility media reexports; package lock; new durable DB, wrapper, processor and transport fixtures.

### Validation Reviewed
Inspected actual source diffs and recorded outputs: 564 tests/49 files, host78, real PostgreSQL19 (including concurrent dispatch, context-once, replay, tenant/control/window/plan refusals), focused kind guards5; build exit0, scoped lint exit0 and diff check pass. Existing media146 tests retain original golden behavior. Full lint exits1 solely for untouched consent-provider line151 control-regex diagnostic, verified identical to prepared baseline; this task introduces no lint diagnostic. No implementation validation was waived or represented as live-provider/system acceptance.

### Architecture Conformance
Conforms to binding ARCH-068 and repository ownership. Exact public Shared5.12.0 SRI and unchanged prepared database gitlink are recorded above. Physical isolation verified from prepared packet: primary `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-068-BACKGROUND-001`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-068-BACKGROUND-001`; both branch `task/ARCH-068-BACKGROUND-001`. Parent remote FF not-needed/main incorporated; implementation remote FF not-needed/main already-current; recursive database sync/update initialized exact5329d5390d346042895219663f3a040ea54ae168 and ready. Shared/default checkouts were not switched or mutated and no other task worktree was reused.

### Follow-up
No same-task correction remains. Admin001 and Commerce001 retain their independently published review states, not Complete; Admin002 remains Pending on those consumers and SystemTest001 remains Pending/manual-gated. Deploy the accepted database migration before runtime field use and both compatible consumers before wrapper activation. No deployment, activation, npm release, real send, main merge or follow-on execution is authorized by this acceptance.

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
