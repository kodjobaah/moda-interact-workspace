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
status: complete
priority: 30
executor: null
claimed_at: null
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
- [x] Verify dependencies and current owned source against binding touch points.
- [x] Implement every requirement in the owned scope and binding contract.
- [x] Add deterministic success/failure/compatibility tests specified above.
- [x] Run declared repository validation and record exact evidence.
- [x] Publish implementation and parent report on mirrored task branches for review.

## Dependencies
None; Ready for normal agent launch. No claim yet.

## Acceptance criteria
All owned scope above is complete, exact contract tests pass and no TODO/placeholder or unresolved cross-service choice remains. For this Shared task, validate its owned source and built public exports; publication evidence is owned by SHARED-003; no sibling source imports/copied mechanics. Record actual changed paths and checks. Preserve existing grounded text, product identity, moderation/send fences, initial/proactive Meta flows.

## Out of Scope
No redesign of aspects 1 and 3, Meta submission/WABA validation, inventory write, unrelated cleanup, budget increase, production mutation or automatic live initializer.

## Agent execution and review
Execution is owned by the assigned agent, not a human developer. Use /moda-task with canonical isolated parent/implementation worktrees and mirrored task branches. Do not claim on authoring. Implement only this repository portion; use published Shared APIs. If an actual source conflict contradicts the exact binding contract, report it to the architect with path/symbol/evidence; do not invent a replacement architecture or leave a placeholder. No main merge/push, production mutation, real send or live initializer execution is part of this task.

## Completion Report

### Status

Complete — moda_architect Accepted Attempt 1 on 2026-11-09. Automatic completion applied under explicit developer authority; attempt 1 unchanged, executor/claimed_at null. Accepted implementation 0b06467c37cbc4cd6ce67fcfa6e9c3fd7da66822 is clean and published.

### Implementation and actual changed paths (7)

- src/commerce/presentation/product-image.ts: exact strict binding, prepared JPEG, native pair, verified provenance envelope, SOURCE and TEXT/IMAGE plan schemas with exported z.infer types. Reuses CommerceProductSchema native validators, existing Zod and stableJson; no new native ID format or browser crypto dependency. Prepared media preserves width1125/height600/JPEG, lowercase SHA256/key shape and strict byteLength<5MiB.
- Same file exports chooseConversationProductImageSource: strict max3 unique displayed/native verified pairs, required platform, exact envelope tenant/platform check BEFORE reading product fields/URLs, exact first pair only. Missing first product/image never substitutes another product/variant/logo/history/model URL. Invalid/non-HTTPS URL omits without network I/O. Provenance/schema mismatch uses PRODUCT_IMAGE_IDENTITY_INVALID; the host still owns authorization/fresh read provenance.
- Same file exports buildConversationDeliveryPlan: validates wrapped body/control characters and binding first; present invalid binding throws PREPARED_INVALID. Exact precedence BINDING_DISABLED → NO_PRESENTED_PRODUCT → CAPTION_TOO_LONG → IMAGE_UNAVAILABLE → IMAGE_IDENTITY_MISMATCH → IMAGE success. Valid text is retained in full; no truncation, extra send or model call. 4096 UTF16 text bound and1024 Unicode-code-point image caption bound are distinct. Exact first pair/shop match is checked before any prepared URL is emitted. digestConversationDeliveryPlan hashes the complete validated plan through injected existing digest and stableJson.
- src/commerce/presentation/wrapper-contracts.ts: optional structured productImage on PreparedWrapper, not an inline variable/token or Meta binding. Omission remains omission.
- src/commerce/presentation/wrapper-projection.ts: permits only the single additional compiled key, validates strict binding, includes it in original immutable hash verification/returned projection, preserves legacy output/hashes without null/default materialization. Unknown/nonoptional/duplicate-shaped/model-URL binding refuses. No Admin authoring AST/compiler is copied into Shared; Admin consumes the exported binding schema in its own task.
- src/commerce/presentation/wrapper-render.ts: direct runtime invocation also refuses an invalid present binding; valid optional media never changes existing body rendering or checkout/variable/control/bounds behavior.
- src/commerce/presentation/compose.ts: explicit responseStyle AGENT uses one complete normalized envelope.replyText candidate across valid dispositions, after existing envelope/projection and selection validation. Exact selected detail/option pairs must match ordered verified facts; mixed/invalid/unobserved selections refuse. No deterministic fact substitution, prose-to-identity matching, body slicing or shortening model call. Legacy/omitted style keeps the old deterministic behavior. Host authorization/verification remains authoritative for recommendation projections, as before.
- src/commerce/presentation/index.ts: browser-safe public schema/type/helper exports.
- src/commerce/presentation/product-image.test.ts: strict shape/byte/key/hash checks; both platforms' variants and Woo simple identity; first-only/missing image/foreign provenance/duplicate pairs; exact first variant mismatch; omission precedence; Unicode1024/1025 and text4096/4097; full text/digest identity; legacy hash/projection and tampered binding; agent details/options/recommendations/policy dispositions; mixed/foreign selection/control refusal; foreign envelope getter test proves URL is never inspected before tenant/platform rejection.

No package manifest/lock/version change, no Node media pipeline, dependency addition, provider/configuration lookup, application code or database change. Existing brand/outreach/initial Meta behavior is outside this pure contract task and unchanged. No sibling source/internal-dist imports. Current package metadata stays5.11.1; this task does NOT publish it or assert a new registry integrity receipt. SHARED-002 extraction and SHARED-003 immutable publication remain separate owned tasks.

### Validation

Canonical workspace bootstrap supplied Node24.19.0/npm11.17.0. npm ci --ignore-scripts installed the existing lock without tracked dependency changes. No live model/provider, public R2 write, Meta send, initializer or infrastructure was launched.

- Declared `npm test`: **659 passed, 0 failed, 3 existing opt-in skips** (662 cases). Runs the complete Shared regression suite, including unrelated legacy contracts. It completed before the final two focused additions/pre-URL guard; that bounded final change was then revalidated below rather than redundantly rerunning all unrelated tests.
- Final `node --import tsx --test src/commerce/presentation/*.test.ts`: **27 passed, 0 failed/skipped**, including the final provenance-before-URL test and all old presentation/fact tests. Existing legacy20-locale/60 golden output vectors remain byte-identical.
- Final `npm run typecheck`: passed, exit0.
- Final `npm run build`: passed, exit0; ESM and declaration outputs generated for public entrypoints.
- Final `npm run validate:commerce-presentation`: passed, exit0; package self-import plus browser-like bundled execution. Bundle rejects Node/Prisma/logging/observability/LangChain imports in presentation.
- Additional public smoke: all nine new named runtime exports present; delivery planning and provenance selection execute in a browser VM. A temporary public consumer imported all six schema-derived types and helpers against built declarations with NodeNext tsc: passed. Temporary fixture removed. The final guard changes no public shape/export; final build/browser validation were rerun afterward.
- git diff --check and staged diff check: passed. Repository declares no lint script; none invented. No resource/security budget raised. Initial test fixture import/type narrowing was corrected before final checks; malformed URL parsing was hardened to omit instead of throw, and final provenance check order explicitly tested. No unresolved validation failure or source conflict remains.

Local receipts: /tmp/arch068-shared001-all-tests.log, /tmp/arch068-shared001-verified-focused.log, /tmp/arch068-shared001-verified-types.log, /tmp/arch068-shared001-verified-build.log, /tmp/arch068-shared001-verified-public.log, /tmp/arch068-shared001-public-smoke.log, /tmp/arch068-shared001-declarations.log. These are local logs, not separately published artifacts.

### Git / VCS and physical worktrees

Task branch task/ARCH-068-SHARED-001 in both repositories. Canonical workspace /Users/kwadwoadomafriyie/project/moda-interact-workspace. Reused parent /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-068-SHARED-001; created implementation /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-068-SHARED-001. No shared/default checkout switched for task implementation; no previous task worktree reused; no subagent assistance.

Launcher dependency gate passed (no dependencies); both remote task fast-forwards not needed and origin/main already current. Recursive implementation submodule sync/update passed, no entries. Parent preclaimad865cdcb9d6e998ccebe949189259223f7efa38; implementation baseline608e60b8758de809ace2c6f89755e1c357616278. Durable codex Attempt1 claim at2026-11-09T20:42:01Z, parent113804306f81413ffe9e1c6f608942881d61e04c, committed/pushed by launcher.

Implementation moda-interact-shared commit0b06467c37cbc4cd6ce67fcfa6e9c3fd7da66822 committed/pushed to origin/task/ARCH-068-SHARED-001; implementation worktree clean. This matching parent report is committed/pushed on its task branch. No submodule gitlink staged; no main merge/push/force-push. No package publication or host activation.

### Review and downstream handoff

Read complete Architect Review: Not reviewed; no Changes Requested list. Preserved that section and all coherence amendments. All owned Work Items are implemented and submitted for review; source/compatibility validation does not claim cross-host authorization, image preparation or final sending. Consumers must construct the provenance envelope from fresh authorized reads and retain exact displayed pair order associated with complete AGENT prose; Shared cannot authenticate a plain product object.

SHARED-002 may consume these source contracts only after the prerequisite is actually Complete; SHARED-003 owns final publication/version/archive/integrity evidence. Consumers adopt the recorded public release and compatible readers before Admin activation. No downstream status/index/architecture change made by this repository agent. No production mutation, live initializer, deployment, R2/provider I/O or real message occurs here.

## Architect Review

### Accepted — Attempt 1, 2026-11-09

Independent moda_architect review requested explicitly by the developer. Reviewed implementation0b06467c37cbc4cd6ce67fcfa6e9c3fd7da66822 against baseline608e60b8758de809ace2c6f89755e1c357616278, parent report1fc599787a1fa0d8b89b2296f89beae59f3552ce, the complete task and binding architecture. No required correction remains.

The seven-file implementation conforms to the owned browser-safe contract. Strict image/binding/provenance/plan schemas reuse existing native identity validators and preserve specified JPEG/dimensions/byte/key/hash/text/Unicode-caption bounds. Selection checks tenant/platform provenance before image access and uses only the exact first displayed native pair. Omission retains complete text with prescribed precedence; invalid binding refuses, and a foreign image URL is never emitted.

PreparedWrapper admits only protected optional productImage. Omitted legacy hashes remain valid without null/default materialization. Present invalid/duplicate-shaped/nonoptional/unknown/model-URL bindings and hash tampering refuse; existing text token semantics remain unchanged. Explicit AGENT style validates envelope/projection and selected detail/option pairs against ordered verified facts, then preserves one complete normalized prose candidate. No deterministic fact substitution, prose identity inference, truncation or extra model call. Legacy style remains unchanged. Host authorization/freshness, including recommendation projections, remains authoritative; the envelope is not independent authorization proof.

Independent architect validation: **27/27 focused tests**, no failures/skips, and built Node/browser presentation validator passed. Receipts /tmp/arch068-shared001-architect-focused.log and /tmp/arch068-shared001-architect-browser.log. Reconciled reported full659 passes/3 opt-in skips, final typecheck/build, public runtime/declaration smoke and browser import restrictions; no redundant unrelated rerun needed.

Dedicated parent/implementation task worktrees and matching branches were verified clean at reviewed commits. Root additionally directly verified remote source0b06467c37cbc4cd6ce67fcfa6e9c3fd7da66822 and parent1fc599787a1fa0d8b89b2296f89beae59f3552ce. Launcher isolation/synchronization/no-submodule evidence is consistent. No implementation, dependency/version, database or rollout change occurred during review. No subagent implementation assistance; only the explicitly requested independent architect reviewer supplied this acceptance.

Accepted Attempt1. completion_mode automatic and explicit developer authority permit Complete, executor/claimed_at null, unchanged attempt1. Promote only SHARED002 after synchronizing completed prerequisite and accepted source handoff; remaining consumers retain explicit dependency gates. Publication remains SHARED003. No main merge, package release, deployment or wrapper activation is implied.

## Developer Completion Decision — 2026-11-09

The developer explicitly requested moda_architect review and, if passing, completion, publication of the decision and downstream reconciliation. Independent review passed above; Complete applied at unchanged accepted Attempt1, preserving execution_mode agent/completion_mode automatic and clearing executor/claimed_at. No separate implementation attempt, takeover or redundant validation. Root performs only the explicitly delegated mechanical parent-document publication; the architect reviewer made no source/doc edits or pushes.

Dependency frontier: SHARED002 Pending→Ready, Attempt0 unclaimed, because its sole explicit prerequisite is now Complete. Its canonical parent receives this complete record and exact accepted source0b06467c37cbc4cd6ce67fcfa6e9c3fd7da66822. Do NOT assume unmerged main contains those contracts. No Shared002 implementation worktree/claim is created here. SHARED003 remains Pending on002, other consumers retain their release/database/consumer prerequisites, terminal system task remains gated. Architecture is in_progress, not implemented. No main integration, package publication, database mutation, live initialization, activation, R2 operation or real message.


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
