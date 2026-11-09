# ARCH-066 — Conversation product context and final WhatsApp preview parity

Date: 2026-11-08. State: Partially implemented; current task-record summary below. Coordinator: moda_architect.

## Current authoritative amendment — 2026-11-08

Read [consumer and acceptance contract](ARCH-066-consumer-contract.md) and [initial outreach contract](ARCH-066-initial-outreach-contract.md) before any pending implementation. They supersede earlier pending-task prose where inconsistent; completed attempt/release evidence stays historical and unchanged.

There are14 tasks. Recorded Complete: SHARED-001/002/003 (original5.6.0). DATABASE-001 remains Ready. MCP-001 returns Pending because amended generic-facts scope requires new SHARED-005. Other consumers/system tasks remain Pending/unclaimed. SHARED-006 adds generic facts -> SHARED-004 outreach -> SHARED-005 combined immutable publication -> MCP/consumers. SHARED-005 records actual version/integrity on acceptance;5.6.0 is not retroactively changed. Dependency readiness is not a task claim.

Generic descriptions/attributes requested earlier are now explicitly owned by SHARED-006, and pending provider adapters/bootstrap/profile/hosts/tests consume them. Old options/PRODUCT_OPTIONS APIs remain available; new PRODUCT_DETAILS/productFacts are additive. Original decisions1–6 below describe accepted options-only baseline; amendments define the pending generic/outreach expansion. Domain indexes show current frontmatter; historical frontier notes below do not override this summary.

## Outcome
Commerce Studio must exercise the same product/option contracts, runner recovery and pure response composition as Background. A Studio assistant bubble defaults to the final conversational WhatsApp body after prepared-wrapper composition, with raw agent output available separately. Studio remains read-only and never sends, bills, moderates for admission or registers a Meta template.

## Evidence and problem
Conversation 472f1bc5-f9e2-4df6-b9c8-0d37dbf60b69 on 2026-11-08: product search returned three shirts, but the sizing turn a9c54d1f-3645-4b34-b9c2-1ff35f9131f3 first received Woo HTTP404/woocommerce_rest_product_invalid_id, then four INVALID_INPUT results, then a successful product search. Final answer was REFER_TO_STORE. Logs do not establish the submitted ID; do not claim proven hallucination. Studio persists only text history across turns; Shared CommerceProductSchema has no options/selectedOptions; runner currently latches referral on every ERROR. Background currently owns recommendation revalidation/rendering and prepared conversation wrapper composition; Studio displays the runner reply before these stages. Formatting markers are displayed literally. These are distinct defects.

## Decision 1 — Additive product options, not a new tool or inferred sizes
Retain commerce.v1, response.v1, canonical tool names, grants and feature keys. CommerceProductSchema gets two optional fields:

- `options: {status:'AVAILABLE'|'NOT_PROVIDED'|'PARTIAL'; items:Array<{name:string;values:string[];usedForVariants:boolean|null}>}`. Bounds: items<=16, name trimmed1..128, values<=64 per item, each trimmed1..128; exact case-sensitive duplicates removed preserving provider order. Preserve label spelling and units. Reject controls other than ordinary whitespace; normalize CR/LF/tab to a single space in names/values. Empty values are omitted. AVAILABLE means complete provider option list, not in-stock availability. NOT_PROVIDED requires empty items. PARTIAL means a bounded subset; never imply list is exhaustive. Bound fields by clipping collection counts only, never cutting a string into a different factual label; overlong/malformed labels are omitted and mark PARTIAL. Missing attributes -> NOT_PROVIDED; successfully read empty attributes -> NOT_PROVIDED. A legacy absent optional field means unknown, not verified absence.
- `selectedOptions: Array<{name:string;value:string}>` <=16 with same string normalization/limits, preserving provider order. Only native selected variant attributes populate it; parent options cannot fabricate a variant selection. Simple parent -> empty selectedOptions. Missing field on old outputs remains valid.

Shopify parent option labels/values and exact variant selections are read using existing pinned schema and read_products admission. Woo parent attributes (including attributes not used for variants) and native variation selections are read through the existing products endpoints and parent membership checks. No product description/HTML field is added in this architecture. Do not infer 'classic white' from a generic product name or assert every listed size is available. Stock, purchasability, prices and promotion eligibility still require their current native facts. Do not map English-only size-name aliases: expose all native options and let the model identify the customer's requested attribute.

No pagination expansion/new product-detail endpoint is introduced: expose bounded parent options plus selected variant options through current search/get results. PARTIAL requires truthful incomplete-list wording; selecting an unavailable combination is never silently resolved.

## Decision 2 — Typed product references across turns
New Shared `CommerceConversationProductContextSchema` strict shape:
`{schemaVersion:1,shopId:string,conversationId:string,platform:'SHOPIFY'|'WOOCOMMERCE',references:Array<{productId:string,variantId:string|null,title:string,observedAt:ISO-UTC-string}>,updatedAt:ISO-UTC-string}`.
Use existing ID bounds<=128 and title<=512; at most20 references and serialized UTF8 JSON<=32768 bytes. Reject mismatched identity or native ID format: Shopify Product/ProductVariant GIDs, Woo positive safe integer strings. Context is trusted-origin reference data but catalogue labels are untrusted; never executable instructions, grants or current evidence.

`mergeConversationProductContext(previous, observations, identity)` admits only host-validated successful product observations, current tenant/conversation/provider. Input previous may be null; identity has current time. Ignore observations older than 24h or in the future relative to identity.now. Deduplicate by exact productId+variantId; latest observedAt wins, ties later observation wins. Order newest observation first then productId and variantId lexically; keep20, then evict oldest until<=32768bytes. Expired previous context (updatedAt older24h) becomes empty. Persist titles/IDs/timestamps only: never prices, stock, offers, raw tool bodies or customer messages.

Runner optional input `productContext` defaults null; wrong identity fails preflight, never silently borrowed. Add a matching optional trusted host `platform` ('SHOPIFY'|'WOOCOMMERCE') used to validate references; when productContext supplied platform is required. No references are resolved from reply text. After successful turn, `productContextUpdate` is the merged bounded payload from validated successful product tools; if none observed return existing nonexpired payload unchanged or omit when empty. Failed turns do not publish updates.

`resolveConversationProductReference` accepts exact known IDs or a trimmed case-folded exact title. A single matching product/variant => MATCH; more than one distinct match => AMBIGUOUS; no match => MISSING. A bare 'yes' does not select the first item from a multi-product list. Model can use references to make fresh exact reads or ask clarification; host validates arguments/provider membership as before. Deleted ID may be recovered by fresh search, never guessed arithmetic IDs. New current facts must be checked before asserting sizes/prices/offers; context does not become evidence.

## Decision 3 — Narrow lookup recovery and precise failure diagnostics
INVALID_INPUT / NOT_FOUND tool results are correctable observations: append to model tool history, consume normal budgets, do not set requiredReferral. Do not auto-retry them unchanged. Require truthful limited reply when correction never yields needed facts; no invented answer. DENIED/revoked grant is sticky requiredReferral TOOL_REVOKED; UNAVAILABLE/THROTTLED/DEADLINE sticky TOOL_UNAVAILABLE; STALE_TURN, cancellation and execution deadline stay terminal. A later successful search cannot clear a prior hard failure. Schema-invalid raw results remain host failures; do not reinterpret malicious payloads as correctable user arguments.

No new circuit breaker, automatic parallel tool executor, increased budgets or changed provider/model is authorized here. The existing bounded retry rule for transient errors remains. Emit current bounded event diagnostics for input format, wrong parent/provider, not-found and output-limit, without raw argument or response dumps. Provider finishReason length + no visible text + no calls => BUDGET_EXHAUSTED/MODEL_OUTPUT_TOKENS_EXHAUSTED at model.route, with existing bounded usage summary. Mixed finalResponse/tool calls and other invalid routes remain INVALID_FINAL. Zero automatic model retries or budget changes.

## Decision 4 — One pure verified response composer
Use new browser-safe Shared `/commerce/presentation` export; do not import Background source from Studio. Move existing deterministic recommendations/money/localization/candidate generation and prepared wrapper pure primitives into this export. Retain public Background wrappers/delegates only for service contracts and I/O; delete duplicated pure implementation after migration.

Export `CommerceVerifiedPresentationSchema` with `{schemaVersion:1,brandName:string|null,locale:existingSupportedLanguageTag,disposition:'STANDARD'|'OUT_OF_SCOPE_REDIRECT'|'SHIPPING_INFORMATION_UNVERIFIED'|'PRODUCT_OPTIONS',storeUrl:string,products:existing RenderRecommendationProduct[] (max3),optionFacts:Array<{productId:string,variantId:string|null,title:string,options:decision1Options,selectedOptions:decision1SelectedOptions}> (max3),requiresShipping:boolean|null,policyUrl:string|null,includeNoVerifiedOffer:boolean}`. All URLs must meet existing safe current-shop URL rules; title/option labels are inert. Product-only facts may omit a buying URL by retaining them in optionFacts, never bypassing recommendation purchase-readiness requirements. Reuse existing supported locale catalogues and price/offer projections, do not drop locales.

Export `verifyCommerceOptionFacts(selection,currentProducts)` as pure deterministic selector: selection list max3 exact productId+variantId pairs, output only exact currentProducts matches with validated options/selectedOptions, same tenant/provider checked by caller. No title match inside verification. Missing match returns a typed limitation, not fabricated facts. Production and Studio must use this selector after fresh authorized reads. Extend existing final presentation selection details with optional `productOptionSelections:Array<{productId,variantId}>` max3; this is a selection request only, never caller-supplied options. Commerce bootstrap and deterministic system sync must publish a new immutable default conversational profile/release adding that property explicitly before model may select it; preserve existing details-schema compatibility validation and deterministic sync. No arbitrary unknown details acceptance.

`composeCommerceWhatsAppPreview` consumes final envelope, verified projection, locale and prepared wrapper input. It composes options deterministically when disposition PRODUCT_OPTIONS, existing recommendation composition for controlled recommendations, else normalized envelope.replyText. In missing/partial option cases use localized truthful labels. No broad product recommendation is required merely because a size question is ambiguous; clarification is valid.

Text formatting: output plain text, not HTML. For model-authored reply text convert balanced **text** -> text and ~~text~~ -> text, preserving inner text; [label](https URL) -> 'label: URL' only for parsed https URLs with no credentials. Unmatched delimiters remain literal; do not globally delete '*' from titles/URLs. Never render model HTML as HTML. Deterministic product/size renderer writes ordinary newlines and bullets directly. No arbitrary Markdown parser, eval or HTML sanitizer dependency required. Do not strip useful prices, URLs, offer terms or currency codes.

Return at most three ordered complete candidates (full, first-product, minimal), preserving existing candidate logic/deduplication. Never split a URL or terms mid-string to fit. Shared composes with the selected prepared wrapper and chooses first valid complete candidate that fits4096 UTF16 code units INCLUDING wrapper. Existing variable bound2048, control rejection, checkout conditional handling, exact response slot and already-wrapped guards remain unchanged. Configured invalid wrapper refuses; no active wrapper returns explicit unwrapped result. Preserve original referral safety; use saved name when available without inventing contact information. Wrapper provenance recorded as definitionId,localeId,contentHash,slotEditVersion. Pure composition is not moderation, Meta approval or send admission.

## Decision 5 — Conversation wrapper versus initial outreach template
This architecture targets the existing MODA_CONVERSATION_WRAPPER and AI active slot, inserting generated body into response.body. Initial outreach's approved Meta template, R2 sample image, WABA registration and parameter/header contracts remain unchanged. Preview must not claim an arbitrary free-form conversational answer fits an initial-outreach template or permits messaging outside the provider's allowed window. Background alone applies existing conversation/window/template admission, moderation and outbox delivery rules.

Move pure `PreparedToken/PreparedWrapper` projection validation, hash/canonical-json and language/slot selection rules into Shared alongside rendering. Preserve current schemas verbatim; no new authoring AST/version. Shared exports functions equivalent to existing readPreparedWrapper, stableJson, digest, chooseSlot, languageChoices, validDefinition, renderPreparedWrapper. Digest is injected (same SHA256 algorithm) for browser-safe code; service secrets/I/O never enter Shared. Existing replay/applicationKey ownership remains Background. Consumers validate DB projections/hashes before passing prepared wrapper. Studio uses the same selected active AI slot and locale, synthetic customer name Test customer, no checkout and saved shop name. UI labels those synthetic values. Same exact explicit context inputs yield byte-identical final text; real customer data can legitimately alter production wrappers.

## Decision 6 — Persistence and fencing
Database task adds one disposable reference-context table, no inventory storage or new feature. Background's `product-context-repository.ts` resolves tenant from the real checkoutRecovery.shopId; missing recovery or conflicting Conversation.shopId refuses. Read row by conversationId AND shopId. Validate JSON via Shared and expiry; invalid/expired means logged empty context, never a grant failure.

Write in the existing successful turn transaction or a dedicated short transaction that locks Conversation row FOR UPDATE, verifies canonical owner and inboundVersion equals expected turn version, and checks existing sourceInboundVersion <= expected version. On existing same sourceInboundVersion treat byte-identical payload as idempotent no-op; differing payload refuses overwrite and logs CONTEXT_WRITE_CONFLICT. For newer inboundVersion, update with revision=previousRevision+1 using compare-and-swap; missing row inserts revision1. Persist expiresAt=now+24h. Do not hold DB lock across provider/model I/O. Stale/cancelled/failed run cannot replace current state. Context failure is best-effort diagnostics and must not cause duplicate sending; existing delivery state remains authoritative.

Studio retains optional productContext inside its existing separate Redis conversation record, same run-finalization fencing/history transaction, existing retention/capacity/purge semantics; no production conversation rows for staff previews. Old Redis records load with empty context. User purge deletes this cache too. No new Redis global key/cross-shop cache.

## Handoff and verification gates

| Task | Objective | Depends on |
|---|---|---|
| [ARCH-066-SHARED-001](../../docs/decisions/shared/ARCH-066/SHARED-001-define-product-context-and-recoverable-lookup-contracts.md) | Define product options, trusted context and lookup recovery contracts | None |
| [ARCH-066-SHARED-002](../../docs/decisions/shared/ARCH-066/SHARED-002-extract-pure-whatsapp-response-composition.md) | Extract the pure WhatsApp response composition contract | ARCH-066-SHARED-001 |
| [ARCH-066-DATABASE-001](../../docs/decisions/database/ARCH-066/DATABASE-001-persist-conversation-product-reference-context.md) | Persist tenant-scoped conversation product references | ARCH-066-SHARED-001 |
| [ARCH-066-SHARED-003](../../docs/decisions/shared/ARCH-066/SHARED-003-publish-product-context-and-presentation-package.md) | Publish product context and presentation package | ARCH-066-SHARED-001, ARCH-066-SHARED-002 |
| [ARCH-066-MCP-001](../../docs/decisions/mcp/ARCH-066/MCP-001-expose-provider-options-and-native-id-diagnostics.md) | Expose provider product options and exact ID diagnostics | ARCH-066-SHARED-003 |
| [ARCH-066-BACKGROUND-001](../../docs/decisions/background/ARCH-066/BACKGROUND-001-integrate-trusted-product-context-and-whatsapp-composer.md) | Integrate product context and the shared WhatsApp composer | ARCH-066-DATABASE-001, ARCH-066-SHARED-003, ARCH-066-MCP-001 |
| [ARCH-066-COMMERCE-001](../../docs/decisions/commerce/ARCH-066/COMMERCE-001-preview-verified-product-details-and-final-whatsapp-message.md) | Preview verified product context and final WhatsApp message | ARCH-066-SHARED-003, ARCH-066-MCP-001 |
| [ARCH-066-SYSTEM-TEST-001](../../docs/decisions/system-test/ARCH-066/SYSTEM-TEST-001-verify-multiturn-product-and-whatsapp-parity.md) | Verify multi-turn product recovery and WhatsApp parity | ARCH-066-BACKGROUND-001, ARCH-066-COMMERCE-001 |

Only SHARED-001 starts Ready. All others remain Pending until explicit prerequisite completion; no claims/worktrees or implementation created by this definition. Publication records an immutable version/integrity; all consumers pin it exactly. Database migration must precede Background rollout; MCP product output and Shared release precede consumers. Additive fields permit old services during rolling deployment. Roll back consumers before package pins/schema removal; do not drop the cache table while updated Background is active. No existing customer data reset/backfill required.

System test must prove three-turn behavior and byte-identical composed bodies for identical facts/locale/wrapper/context, hard authorization failures, soft lookup correction, missing options, token truncation, snapshot compatibility, storage limits/purge and replay. Real-model Render TEST smoke is supplemental evidence, not a replacement for deterministic fixtures. No production deploy or real message send is authorized by task creation.

Release handoff: Shared5.7.0 published/download-verified (exact integrity below), SHARED-005 review/completion pending; database migration/commit pending; consumer commits pending; parity artifact pending. This architecture does not claim complete test-to-delivery equivalence for production-only moderation/window/billing checks; Studio must identify those as not evaluated.

## Dependency frontier - 2026-11-08
SHARED-001 accepted Attempt2 explicitly developer-completed, source c3f9f07 and review5bd56f332 published. SHARED-002 and DATABASE-001 now Ready/unclaimed. SHARED-003 remains Pending on SHARED-002; consumers and terminal System Test remain gated. No package publication, migration, deployment or enabled execution performed.

## Two execution purposes and Studio testing
See [Background and Studio sequence diagrams](ARCH-066-background-and-studio-sequences.md). Studio must support separate checkout-scoped initial-outreach tests and subsequent CommerceAgent conversations. The initial-outreach preview branch is an additional required workstream: current ARCH-066 tasks cover conversational parity and do not yet define its implementation. Do not treat the existing checkout-preview exclusion as satisfying this requirement. Production initial-outreach template and delivery contracts remain unchanged.

## Initial outreach preview implementation tasks
The earlier checkout-preview exclusion is superseded by SHARED-004, BACKGROUND-002, COMMERCE-002 and SYSTEM-TEST-002. These tasks require live exact checkout product/variant reads, even without an offer; checkout quantities and historical prices remain separate from current facts. No unrelated catalogue products. SHARED-003 is an already completed immutable5.6.0 release and does not include SHARED-004. SHARED-005 now defines the separate publication gate after SHARED-004; its actual immutable version/integrity is recorded only when published. Studio uses existing same-shop CheckoutRecovery records without creating an outreach attempt. Both execution purposes are tested separately.

2026-11-08: SHARED-002 accepted Attempt1 explicitly developer-completed; implementation7255db5 and passing review60836eb38 verified published. SHARED-003 now Ready/unclaimed because both Shared implementation dependencies Complete. Consumers remain publication-gated. No npm publication, deployment or automatic execution.

## Immutable package handoff - 2026-11-08
Shared5.6.0 published/downloaded and isolated public-import/browser smoke verified under SHARED-003 Attempt1; review/completion pending. Consumers MCP-001, BACKGROUND-001 and COMMERCE-001 pin exactly5.6.0. dist.integrity: sha512-tDuW+C8MdteWMJWwmuFI2cTAugMejOJwTk0KkemBMwpN/lL92WPI8CX/A5dDa2nhG0RYiIeHSR490WPCrTz42w==; SHA256 a576e87de3d74965f7b4b392bb4470bfa74a1759297840c60fe22222a2a8c550. Tarball https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-5.6.0.tgz. No deployment/consumer execution or dependency promotion asserted. Database migration and consumer revisions remain pending owner evidence.

2026-11-08: SHARED-003 accepted Attempt1 explicitly Complete, exact5.6.0 immutable release verified. MCP-001 becomes Ready/unclaimed. DATABASE-001 remains Ready; BACKGROUND-001 and COMMERCE-001 remain Pending on their other explicit dependencies. Terminal System Test remains Pending/manual-gated. No consumer execution/deployment or automatic task start.

2026-11-08: MCP-001 accepted Attempt1 explicitly Complete, implementation fd53bb5 and passing review45316cecf verified published. COMMERCE-001 newly Ready/unclaimed. BACKGROUND-001 remains Pending on DATABASE-001 (Ready); terminal System Test remains Pending/manual-gated. No downstream execution or deployment.

2026-11-08: SHARED-006 accepted Attempt1 explicitly Complete (source2bc7f02, passing review55ad2ed2d). SHARED-004 dependencies all Complete, now Ready/unclaimed. SHARED-005 remains Pending on004; consumers remain combined-release gated. No source publication/deployment or enabled task execution.

2026-11-08: DATABASE001 Attempt1 Accepted at review after exact cache schema, full-history fresh/upgrade row-preservation/constraint tests and Prisma generation. MigrationSHA2563e99659d71c8e1d5933a95ad933a10bffea03bd25395795cc8de704f27ff686a; explicit developer completion pending. No live migration/service/deployment or integrated completion claimed.

### 2026-11-08 — Outreach source completion frontier

2026-11-08 explicit completion: DATABASE001 Attempt1 Complete, sourceb7f58d5/migrationSHA2563e99659d71c8e1d5933a95ad933a10bffea03bd25395795cc8de704f27ff686a. Canonical Background001 Pending on Shared005; Shared004 Ready and Shared005 Pending, MCP001 Complete. No newly Ready task from DB completion; concurrent Commerce001 Ready record preserved, dependency consistency requires owner reconciliation before execution. Terminal System Tests remain gated; no live migration/backfill/main/integrated completion.

### SHARED-005 selected outreach release — 2026-11-08

Exact selected pin: `@modainteract/moda-interact-shared@5.7.0`, verified unused after inspecting all published 5.x versions (highest 5.6.0). Accepted outreach source `987a05dd06e79aa465d11fce8a4d4fe8b8d52703` includes generic product facts and accepted 5.6.0 ancestry. Publication/download verification and exact integrity recording remain in progress under SHARED-005 Attempt 1. Consumers remain gated; no rollout is authorized by this version-selection record.

### SHARED-005 immutable outreach artifact — published and download-verified

Exact consumer pin: `@modainteract/moda-interact-shared@5.7.0`.

- dist.integrity: `sha512-2/Ew2Blo83eY/LKthULJh84kHoJfq701e3RCpjPEQNXYnSai6IEQO08n4QNct1QzwWGyNxf9M2lokLlCHKyoXg==`
- Tarball SHA256: `c14d0195981acb2a31287b6e026322225dd34d29c0b60bd59c44a0141314936d`
- Release source commit: `09e249c5717c8866996624f8855a7d649dfd2c43`; accepted outreach source `987a05dd06e79aa465d11fce8a4d4fe8b8d52703`, including accepted generic product facts and original5.6.0 ancestry.
- Registry tarball: https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-5.7.0.tgz

Published once on2026-11-08, then registry metadata/download hashes and isolated installed-artifact public JS/declaration/evaluation/frozen-render/generic-facts checks passed. Prior34 public export definitions remain intact. This record supersedes the earlier version/integrity-pending selection text. SHARED-005 remains Review at Attempt1 pending developer acceptance and explicit completion; consumer dependency gates remain in force. Consumers must pin this exact artifact after the gate completes; no latest/range inference, package republish, consumer rollout or real message delivery is implied.

### 2026-11-08 — Accepted release completion frontier

SHARED-005 is explicitly Complete at accepted Attempt1 after passing review `a2590514fd2d75db56391015ef5460feaefdb0f5`. The exact accepted consumer artifact is Shared5.7.0 with the integrity/SHA256/source recorded above. BACKGROUND-001 and COMMERCE-001 have all explicit prerequisites Complete and are Ready, Attempt0/unclaimed. Historical DATABASE-001/MCP-001 Complete records are preserved; no new MCP scope acceptance is inferred. BACKGROUND-002 waits for BACKGROUND-001; COMMERCE-002 waits for COMMERCE-001/BACKGROUND-002; system tests retain consumer dependency and manual gates. Consumer execution remains a separate claim; no rollout or production send occurs here.

## Explicit checkout-led withdrawal disposition — 2026-11-08
Developer confirmed production turns retain real CheckoutRecovery, synthetic Studio preview remains isolated. SHARED007 Superseded at Attempt1, SHARED008/MCP002 Superseded unclaimed; do not publish standalone package. Historical technical reviews retained, no successful implementation completion claimed.009/010 product-detail correction unaffected. Background/Commerce require same-task checkout-led source review and real recovery ownership, verified reference/composition tests; standalone blocker/dependencies withdrawn, other genuine gaps/System Test manual gates remain. No source rollback/main/live/follow-on execution.


Dependency handoff2026-11-08: canonical Background001 Complete atb9470dd27/AcceptedAttempt2; Background002 Ready Attempt0/unclaimed, developer execution/completion. No standalone release/main/live/follow-on action.

## Initial outreach Shared compatibility blocker — 2026-11-08
BACKGROUND002 Attempt1 is Blocked, not Accepted: exact5.8.0 SemanticKeySchema advertises shopBrand.logoAltText/logoWidth/logoHeight/squareLogoAltText, but public frozen renderer refuses all4positive valid saved-value fixtures. Shared011 Ready defines bounded strict prepared-brand/media compatibility; Shared012 Pending publishes accepted correction. Original Background002 then adopts corrected artifact/revalidates same task, no duplicate local renderer/internal import. Unaffected evaluator/selection/admission38 and supported parity/generation7 pass; compiler passed, broader unresolved regressions remain explicitly recorded in task report. Commerce002/SystemTest002 remain gated; no follow-on/main/live/release or integrated completion. Checkout-led withdrawal controls,007/008/MCP002 remain superseded.

## Corrected release unblocks original Background rework — 2026-11-08
SHARED012 explicitly Complete, public5.9.0/sourceb65e04f verified. BACKGROUND002 Ready for correction only, historical Attempt1/72failures/source8be7e962 preserved, claim null; no acceptance or increment. Exact release dependency record and explicit same-task correction checklist materialized. Other concurrent states/manual System Test gates unchanged; no source/npm/main/live/follow-on execution.

## Frozen outreach compatibility gap — 2026-11-08
BACKGROUND002 adoption proves published5.8.0 enumerates valid savedbrand alt/dimension semantic keys but resolver refuses them; existing supported production frozen bindings cannot be silently removed. SHARED011 Ready defines bounded strict data/resolver compatibility; SHARED012 Pending immutable correction publication. BACKGROUND002 remains Blocked until corrected artifact adoption and same-task review. No generic local renderer workaround/unsupported internal import, no main/release/live/follow-on execution. Checkout-led scope remains controlling: production retains real recovery, standalone007/008/MCP002 withdrawn; this correction does not resurrect them.

## SHARED012 publication handoff — 2026-11-08
SHARED011 explicitly Complete at Accepted Attempt1, source6c8bbe194337c7c2afb141047d24aeeeb23c48ca, review750d5119/decision9eb1af515. Exact completed prerequisite record materialized here;010Complete preserved.012Ready Attempt0/unclaimed, release-only scope/developer completion. No implementation worktree/claim/npm publication created by reconciliation. Background002 remains Blocked pending exact accepted corrected artifact and its72unresolvedfailures; no consumer/main/live/follow-on execution or standalone resurrection.

## Canonical synchronization disposition — 2026-11-08
Main-to-task documentation conflict resolved preserving both histories and canonical completed011/012records. Current authoritative state: Shared011CompleteAttempt1 (9eb1af515), Shared012CompleteAttempt1 (4b5ff8d7f), public immutable5.9.0 verified; Background001CompleteAttempt2, Background002Ready for same-task correction at priorAttempt1/unclaimed. Existing72failures and latest correction checklist remain mandatory, no acceptance or increment. Checkout-led withdrawal and007/008/MCP002supersession preserved; no source/main/live/release/follow-on work performed by this sync. Earlier contradictory readiness/review narratives are historical and superseded by individual current task metadata.

## Background initial outreach correction review — 2026-11-08
BACKGROUND002 Attempt2 Accepted at Review, explicit developer completion pending; current source0a6010315fb97ab47c105c9f93bb792f1cd07b49 clean/published. ExactShared5.9.0 strict savedbrand/independent authorized BODY media adapter adopted; former72failures resolved. Final residual13files155passed, recommendations204passed, deliveryconsent/moderation/credit/outbox/replay/send231passed; compiler/finalbuild/scopedlintpass. Full lint sole untouched consent-provider151 no-control-regex remains explicit. Real Shopify/Woo full NONEchain proves2distinct-pair reads/no model/offer/preflight/fallback, historical/current separation, full body/parameters/provenance bytes and final generation admission; IMAGEunavailability cannot bypass invalid mandatory BODY evidence, approvedTEXTfallback retained. Legacy active host pricing/admission/FOLLOW_UP semantics remain separate; public Shared owns migrated initial evaluation/arithmetic/render. Commerce002/SystemTest002 remain dependency/manual-gated until actual Background completion; no consumerexecution or integrated architecture completion claimed. Checkout-led withdrawal/no standalone/main/live/release/follow-on retained.

Preserve the checkout-led scope and all accepted historical releases. The product-detail correction remains immutable5.8.0; frozen outreach binding compatibility requires the separate SHARED-012 publication gate after accepted SHARED-011. In this merged snapshot SHARED-012 is Ready at Attempt0, not accepted or published; no new version/integrity or consumer readiness is inferred. BACKGROUND-002 remains Blocked until corrected artifact adoption and its remaining validation are resolved. Earlier pending/ready frontier entries are dated history; terminal system tests remain manually gated.

## Commerce outreach executable handoff — 2026-11-08
Background002 explicitly CompleteAcceptedAttempt2 at35a0e227f (source0a601031/review806d17ad); canonical Commerce001CompleteAttempt3 remote181bd35f and Shared005/012Complete verified. Exact completed dependency records materialized here. Commerce002ReadyAttempt0/unclaimed, execution/completion developer retained; exact5.9.0 pin/strict brand/media mapping and common frozen fixture handoff in task. No implementation worktree/claim/execution. SystemTest001 alreadyReady/manual-gated, SystemTest002Pending on Commerce002; no main/live/npm/follow-on action.


### 2026-11-09 configured sender public identity boundary
Commerce initial outreach remains blocked until a least-privilege public configured WABA projection exists. Never decrypt messaging.sender in Commerce or infer configured identity from template assignment. SHARED013 defines the strict public schema; SHARED014 publishes it; ADMIN001 atomically derives messaging.senderIdentity beside sender secret mutation with a current-active source-version fence. COMMERCE002 then consumes the published projection and metadata without secret values. No database/infrastructure change or live backfill is authorized.

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-066-SHARED-013 | moda_shared | Ready | ARCH-066-SHARED-012 |
| ARCH-066-SHARED-014 | moda_shared | Pending | ARCH-066-SHARED-012, ARCH-066-SHARED-013 |
| ARCH-066-ADMIN-001 | moda_admin | Pending | ARCH-066-SHARED-014 |


2026-11-09 correction definition publication update: developer explicitly authorized the three prepared branches; SHARED013/014/ADMIN001 definitions are now remotely verified at201f3922e/af5e4bc6a/90e6bb38d respectively. This supersedes prior local-only publication limitation, not Commerce002 Blocked status or any implementation acceptance. SHARED013Ready;014/Admin001Pending. No claim or implementation started.


2026-11-09 completionfrontier: COMMERCE003CompleteAcceptedAttempt1 atb7fb1c0fa, source6f01c096cleanpublished. COMMERCE002Ready for SAME-taskrework, priorAttempt1/claimnull, originalHOST/lifecyclechecklistmandatory/noacceptance; all explicitdepsComplete. SystemTest002remainsgated002; withdrawn senderchain/currentconcurrentstatespreserved. No claim/source/tests/live/main/follow-onexecution.


## Commerce initial outreach host rework review — 2026-11-09
COMMERCE002 Accepted at ReviewAttempt2, explicitdevelopercompletionpending. Source40b59e777db5b85d8f3444da1abe07170e70496f clean/published after normalmain→task resolution87c835 preserving003exact5.10Studio source and prior002history. Realdefaultfactory now wires trusted actor/shop/currentimmutablepurposeprofile/model/instructions/policy/locale/brandREADYmedia, localcredential-backed and isolatedMCP reads, Redis reservations/fences and boundedcancel/deadline/overflow. CurrentWoo pricecurrency derives from authenticated existing currentcurrencyendpoint, never checkoutpresentmentcurrency.19prior003proofs retained; final11files74PASS/no skips, compiler/scopedlintpass, exactunchangedAdminpurgeLua realRedisproof additionalPASS. Tests use actualHTTP/defaultfactory/registeredadapters with externalIOmocked; no liveprovider/customer effects or deployment verified. Shared5.10publicrenderer/purposehelpers retained, production validation and withdrawn senderchain unchanged. SystemTest002 staysgated until explicit002Complete; architecture remainsInProgress and terminalmanualsystemvalidation separate.


2026-11-09 explicitCommerce002completionfrontier: COMMERCE002CompleteAcceptedAttempt2/claimnull source40b59e7/reviewbffd7e9verifiedcleanpublished. SystemTest002ReadyAttempt0/unclaimed, execution/completiondeveloper and manualcheckpoint preserved; SystemTest001alreadyReadyunchanged. Latest5.10Studio-only/parityamendment controls, Background5.9productionfencesretain. No tests/main/live/npm/follow-onexecution; architectureInProgress/manualterminalvalidationremaining.
