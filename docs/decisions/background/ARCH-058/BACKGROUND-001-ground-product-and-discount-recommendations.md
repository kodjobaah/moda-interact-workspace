---
id: ARCH-058-BACKGROUND-001
architecture_id: ARCH-058
title: Ground inbound product and discount recommendations in current shop facts
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-058-MCP-002
- ARCH-058-COMMERCE-001
enables:
- ARCH-058-SYSTEM-TEST-001
created: '2026-11-04'
updated: '2026-11-04'
---

# ARCH-058-BACKGROUND-001: Ground inbound product and discount recommendations in current shop facts

## Architecture and execution boundary

Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`. Binding cross-service contracts: `docs/architecture/ARCH-058/contracts.md`. Source review: `docs/architecture/reviews/commerce-agent-product-discovery-20261104-015544-r03/review.md`, particularly sections 4.4, 6.4, 7.4–7.5 and 10. The parent contracts take precedence over descriptive examples here; an incompatible accepted dependency is an architect handoff, not permission to invent another wire shape.

Definition revision: 1. **Defined but not materialised.** Both prerequisites must be Complete and architect-accepted before claim. This definition asserts no task branch, worktree, implementation, package publication, deployment or test result. An earlier review patch is not a prerequisite.

Use the launcher-prepared dedicated parent/implementation worktrees and record its synchronization and recursive-submodule evidence. Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md` and `docs/observability/shared-logging.md`. Do not rediscover a valid preparation packet or derive a new task workspace from another task worktree.

## Objective

Make the normal inbound CommerceAgent use authorised published instructions, current shop policy and observed product/discount facts to produce useful product recommendations. Evaluate each proposed purchase separately, recheck selected claims within the existing turn budget, and compose the complete promotional reply from validated facts in the conversation language before the existing wrapper/moderation/admission/delivery path.

## Context

The snapshot host passes fixed recovery instructions and historical recovery context, while Studio previews and initial outreach have separate published-prompt loading. The host runs the existing generic Shared tool loop and already performs grant/turn checks and legacy evidence refresh. Canonical ARCH-052 options/details describe source conditions; they are not the quantified legacy evidence accepted by `evidenceIds`. Initial-outreach pure eligibility/combination helpers can be adapted without invoking its agent or fabricating an outreach attempt.

MCP-002 supplies current-policy conversational discount built-ins, provider-scoped products and the accepted optional-unavailable behavior. COMMERCE-001 supplies the standard published discovery tools, feature instructions and response contract. The parent targets Shared `4.0.0` conditional on the accepted baseline remaining `3.1.0`, and runner `1.1.0` with new release compatibility `>=1.1.0 <2.0.0`; consume the exact accepted SHARED-002 publication rather than guessing a version if that baseline changes. Sibling Shared source and an accepted task label alone do not prove the installed package contains the contract.

## Scope and exact file ownership

Paths below are relative to `moda-interact-background`. MODIFY authorises only the named responsibility, not an unrelated refactor.

| Existing path | Allowed change |
|---|---|
| `package.json`, `package-lock.json` | Adopt the architect-accepted Shared publication and add only the focused validation scripts described below if needed. Do not guess a package version. |
| `database` | Update only the gitlink to the accepted Database revision when required by the dependency handoff; generate Prisma normally. Never edit its schema/migrations here. |
| `src/agents/commerce.agent.ts` | Pass already-resolved trusted host dependencies when needed; retain one model invocation framework and existing observability wrapper. |
| `src/commerce/host.ts` | Wire context, registered observations, typed selection, final revalidation and host rendering into the existing loop/finalization; keep new business logic in the focused modules below. |
| `src/commerce/recovery-instructions.ts` | State the published grounding/selection/degradation rules and historical-basket limitations with the existing instruction precedence. |
| `src/commerce/grants.ts` | Consume accepted published/built-in grant identities and equality; preserve persisted grant authority and release validation. |
| `src/commerce/mcp-client.ts` | Encode the trusted conversation-purpose context, consume accepted manifest/result contracts and preserve original available source diagnostics through wrapping. No new transport. |
| `src/commerce/host-diagnostics.ts` | Preserve safe original source/SDK/Prisma details in existing structured failure events; keep codes/stages truthful. |
| `src/agents/initial-outreach-offer.eligibility.ts`, `src/agents/initial-outreach-offer.combinations.ts` | Delegate narrowly shared comparisons through adapters while preserving current initial-outreach inputs, lifecycle checks, decisions and conservative limitations. |
| `src/agents/initial-outreach-offer.graph.ts` | Only if required by the widened Shared output union: reject the conversation-only optional-unavailable branch before the existing success access. Do not adopt that fallback or change graph decisions. |
| `src/services/recovery-offers/current-outreach-offer-revalidation.service.ts` | The same compile-time union discrimination only if required; preserve initial-outreach failure/admission behavior. |
| `tests/integration/commerce/host.test.ts`, `tests/integration/commerce/host.fixture.ts` | Register the new focused suites and extend the existing fake-MCP/host fixture for accepted contracts and trusted context. |
| `tests/integration/commerce/host-suites/authority.ts`, `tests/integration/commerce/host-suites/grants.ts`, `tests/integration/commerce/host-suites/evidence.ts`, `tests/integration/commerce/host-suites/budgets.ts`, `tests/integration/commerce/host-suites/language.ts` | Focused compatibility regressions for built-in identities, budgets, retained grants, unchanged legacy evidence and current language. |
| `tests/unit/commerce/host-diagnostics.test.ts`, `tests/unit/commerce/mcp-client.test.ts` | Capture actual Shared sink records and propagation at the changed boundaries. |
| `tests/unit/agents/initial-outreach-offer.graph.test.ts`, `tests/unit/services/recovery-offers/current-outreach-offer-revalidation.service.test.ts` | If the union guards are needed, prove that the conversation-only unavailable object cannot become initial-outreach success or neutral-offer permission. |

Create only these production modules, each with one responsibility:

| New path | Responsibility |
|---|---|
| `src/commerce/recommendations/context.ts` | Trusted published instructions, effective policy, current conversation/purchase identity and bounded basket projection. |
| `src/commerce/recommendations/observations.ts` | Turn-local registry of validated canonical results bound to actual authorised tool calls and source identity. |
| `src/commerce/recommendations/eligibility.ts` | Common pure source-condition comparisons against an explicit purchase; lifecycle adapters stay with callers. |
| `src/commerce/recommendations/combinations.ts` | Reusable existing reciprocal/pair/subset checks with unchanged conservative provider semantics. |
| `src/commerce/recommendations/money.ts` | Exact decimal/minor-unit comparisons and narrowly supported merchandise calculations; no floating-point eligibility arithmetic. |
| `src/commerce/recommendations/revalidation.ts` | Refresh selected observations through the existing authorised MCP client under the remaining turn budget and current-turn checks. |
| `src/commerce/recommendations/render.ts` | Complete host-owned recommendation text from validated selections, facts and resolved locale; no model-authored promotion prose. |
| `src/commerce/recommendations/messages.ts` | Typed fixed-message catalogue for all 20 supported locales, using existing Shared internationalization conventions. |

Create these focused validation files: `tests/unit/commerce/recommendations/context.test.ts`, `observations.test.ts`, `eligibility.test.ts`, `combinations.test.ts`, `money.test.ts`, `revalidation.test.ts`, `render.test.ts` in the same new directory; `tests/integration/commerce/host-suites/instruction-composition.ts`, `recommendations.ts`, `recommendation-revalidation.ts`, `recommendation-failures.ts`; `tests/integration/commerce/recommendation-context.integration.test.ts`; and `tests/fixtures/commerce/product-recommendations.v1.json`.

Read-only reference paths include `src/agents/types.ts`, `src/commerce/evidence.ts`, `src/commerce/referral.ts`, `src/services/conversation-language.service.ts`, `src/services/recovery-policy.service.ts`, `src/services/recovery-offers/initial-outreach-agent-context.service.ts`, `src/services/recovery-offers/current-discount-source-fence.ts`, `src/services/recovery-pricing/checkout-price-reconciliation.service.ts`, `src/services/conversation-turn-processor.service.ts`, `src/services/conversation-wrappers/compose-ai-outbound.ts`, `src/workers/whatsapp.worker.ts` and `scripts/test-integration.mjs`. Return an essential additional writer or file to the architect before mutation.

## Requirements

### 1. Trusted instructions, policy and purchase context

1. Read the active published Platform and optional Shop prompt revision for the trusted environment/shop. Validate configuration/revision identity, `PUBLISHED` status, scope, ownership and existing size bounds. Follow accepted Platform-then-additive-Shop composition; preserve the Shared kernel, response contract and release-frozen Feature Behaviour. Required Platform instructions unavailable/invalid is not an empty successful prompt. Do not restore trusted instructions to generic MCP or import Studio application code.
2. Resolve current effective `NONE`, `FIXED` or `AI_BEST_APPLICABLE`, including active override and authorised selected IDs. Reuse existing policy semantics but never turn a failed policy read into `NONE`. Reconcile the trusted policy with current MCP results; a mismatch/revocation is guarded failure, not an optional catalogue outage. `NONE` performs no discount discovery; FIXED never escapes the authorised IDs; AI does not require merchant selection checkboxes.
3. Historical recovery values may establish an owned basket's identity, not current stock, prices or qualification. Bound the context and retain unknown provider IDs, sale status, currency and current prices as unknown. Provider reads remain through MCP; no Background-to-Shopify/Woo HTTP or new product database.
4. Consume `CommerceProductRecommendationSelectionSchema` from the accepted Shared package and the published `detailsSchema`. Both flat details fields must be present together: `productRecommendationVersion: "1"` and `productRecommendations` with one to three independent items. Each item contains `scope`, nullable `basketLineId`, `productId`, nullable `variantId`, integer `quantity` 1–99, `promotionKind` and at most three `offerIds`; exact structural bounds are fixed in the parent contract. The accepted Shared validator counts the details root as depth1 and therefore permits depth5 for the `offerIds` string items; consume that narrowly extended validator without increasing any other bound or introducing `oneOf`. There are no model-supplied prices, currency, savings, promotion prose or proof IDs in this selection.
5. Validate business relationships locally: PRODUCT_ONLY cannot silently add to a basket; PRODUCT_ONLY and ADD_TO_BASKET have null `basketLineId`; REPLACE_BASKET_LINE identifies the exact current owned line. ADD_TO_BASKET and replacement require the real owned basket. NONE/NATIVE_SALE have no offer IDs; DISCOUNT has one to three observed offer IDs. Each alternative is evaluated independently. An explicitly hypothetical one-item recommendation is possible when quantity is unspecified; three displayed alternatives do not form a three-item basket. A Woo simple product retains `variantId: null`. Do not manufacture a variant or an outreach attempt.

### 2. Source observations and supported claims

6. Record only successfully schema-validated results from the actual granted canonical product/options/details calls. Bind observations to the authenticated shop/provider, current conversation/inbound version, published or built-in descriptor identity, tool arguments and observed source identifiers. Identical-looking JSON from a different tool, tool-rendered prose, model arguments or conversation history cannot populate trusted product/discount observations.
7. Preserve the generic loop: the model can use direct product search for a clear noun, or a bounded category lookup when useful. Reference candidates never establish merchant inventory or discount coverage. Verify exact current product/variant IDs and native category/collection inclusions/exclusions; exclusions win. Do not reject products merely because the Store Category or reference taxonomy does not match.
8. Extract only reusable pure eligibility and combination comparisons from initial outreach. Keep initial-outreach report/attempt/generation checks in its adapter and current turn/proposal checks in this adapter. Preserve its `SUPPORTED`, `NOT_APPLICABLE`, `UNVERIFIABLE` distinctions. No general minimum-quantity scope, buy-X-get-Y, customer history or allocation engine is added by this task; unknown material conditions remain unverifiable. Native-sale claims require direct current sale-price evidence and permitted mode, not an invented coupon.
9. For a subtotal rule require complete current pricing for the evaluated purchase, valid exact decimals and matching known `subtotalRequirementCurrency`. Unknown Woo currency, historical checkout totals or another market's price do not qualify. Compare in exact integer minor units/decimal arithmetic and preserve currency precision. Compute a merchandise saving only for a represented, supported calculation with known price/currency, quantity, eligible lines and rounding/allocation semantics. Otherwise describe supported terms without an invented saving, discounted total, shipping/tax total or final-redemption guarantee.
10. Reuse reciprocal Shopify class/line compatibility and Woo individual-use/known extension restrictions. At most three selected offers must be individually supported and pairwise compatible; otherwise reduce to a supported subset/singleton or omit the claim. Never add percentages or calculate an unsupported combined total. Unknown targeting, customer restrictions, usage counts or combinations are not implicit unrestricted eligibility.
11. Distinguish no applicable permitted offer found, known unmet condition, unverifiable conditions, partial discovery and unavailable retrieval. A conditional statement about required quantity/subtotal needs represented scope as well as a number. Do not call bounded AI selection globally best or describe an unvisited page as catalogue exhaustion. Checking an offer never applies a code or mutates a basket.

### 3. Built-ins, failure semantics and final revalidation

12. Consume the accepted `manifest.builtInTools` and `grantedTools` union. Built-in identities contain the allowed tool name, definition version and canonical contract hash; they have no fabricated Studio tool/revision/capability IDs. Validate the full published identity and current policy, and preserve the existing persisted grant/release checks, including the accepted forward Database JSON-guard/trigger update. `encodeCommerceContext` must validate the existing turn assertion and attach `CommerceConversationToolContextSchema` under the opaque header field: `{purpose: "CONVERSATION", conversationId, inboundVersion, grantId}`. Use null grant only for initial resolution and the real retained ID after persistence; no model-provided context/descriptors/hashes. MCP verifies ownership/version/lease and reads the retained grant itself. Preserve the separate outreach context. Missing generic context does not grant conversational discounts. Do not silently widen an old grant, auto-reset grants, or introduce name-only execution. Standard product/category availability is supplied upstream; this task does not publish tools or edit plan mappings.
13. Taxonomy data outcomes are the parent-defined `CANDIDATES`, `NO_CANDIDATES` and `UNAVAILABLE` reasons. Discount options/details retain their existing success objects; the only new conversation-only optional failure object is `{outcome: "UNAVAILABLE", reasonCode: "TEMPORARY_UNAVAILABLE"}` inside an otherwise valid `OK` envelope. It contains neither fake offers nor fake details. Discriminate this branch before accessing success fields; do not accept it in initial outreach as a neutral-offer fallback.
14. Only the explicitly classified optional outcome permits an independently supported product answer without an unverified promotion. A terminal tool `ERROR` still forces referral; a later successful call cannot clear it. Tenant/auth failures, stale/cancelled turns, incompatible contracts, malformed source data and unexpected programming failures retain their existing guarded path. Do not wrap arbitrary exceptions as a successful empty catalogue.
15. Reserve capacity for selected-product/details refresh within the same resolved LIVE deadline, model/remote-call budgets and cancellation signal. Include all refresh calls in the turn count; do not create an independent ten-call budget or silently extend the lease. If the required checks cannot fit, reduce the supported selection or use the accepted unverifiable/referral outcome before making a claim.
16. At the existing host finalization point after model selection, refresh only the selected product/variant facts and offer details through the authorised MCP path, reread effective policy and relevant source/basket identity, and recompute the claim. Assert the same current turn/lease before and after awaits. Quantity, variant, availability, price/currency, offer status/identity, selected IDs, conditions or relevant source changes invalidate the earlier assessment. Discard unavailable or unsupported promotional claims according to the explicit failure policy and rebuild their text; never send the stale amount/code. This establishes current observed facts at host finalization, not atomic provider redemption or a new post-wrapper hook.
17. Keep legacy `evidenceIds`, extraction, qualifying outcome, money, identity and freshness validation intact. Canonical facts/`SUPPORTED` are not legacy evidence; never mint such an ID or weaken the validator. A result using the legacy path must still satisfy it independently.

### 4. Host composition, localization and existing outbound path

18. The recommendation branch must finalize through validated structured selections. Compose its entire customer message from supported product facts and selected conditions; do not forward the model's independent `replyText` for that branch. Missing/invalid selections, extra prose or an attempted empty-details bypass cannot deliver a model-authored discount claim. This is an explicit structured-output branch, not a claim that a schema or keyword regex semantically validates arbitrary prose. Preserve ordinary non-recommendation replies through their existing guarded path.
19. Resolve the current conversation language using the existing language service and accepted detection rules, not the taxonomy source language. Use Shared internationalization helpers for language tags, localized numbers/money and ICU formatting where applicable. The fixed-message catalogue must cover exactly `zh-Hans`, `zh-Hant`, `cs`, `da`, `nl`, `en`, `fi`, `fr`, `de`, `it`, `ja`, `ko`, `nb`, `pl`, `pt-BR`, `pt-PT`, `es`, `sv`, `th`, `tr`, checked against `MODA_SUPPORTED_LANGUAGE_TAGS`. Preserve placeholders; provide natural localized condition/unavailability text. Do not invent a regional language/currency relationship or use a new general translation service. Product titles and codes retain their source identity.
20. Return the rendered text through the same `CommerceAgentResult` and existing processor callsite. Keep history, customer/HUMAN takeover, STOP/consent, inbound-version ordering, admission, wrapper composition, whole-message moderation and provider delivery controls intact. Do not change the worker, processor, reservation, wrapper or send ordering. Strip custom details from the delivery adapter as today; retain only appropriate safe host diagnostics.

### 5. Original error evidence

21. Use `@modainteract/moda-interact-shared/logging` and existing host/client events. At changed boundaries preserve the original available safe error name/message, actual code/status/request identifier and source/stage, plus shop/conversation/turn/tool correlation. Pass sanitized available source failure/cause through wrappers; do not replace it with only `UNAVAILABLE`, a guessed provider explanation or a generic message. MCP owns logging its original provider failure when that detail is intentionally absent from the public envelope; Background must not fabricate it.
22. No generic local logger, redactor, serialization framework or duplicated HTTP metrics. Do not log prompts, complete product descriptions, customer content/phone, credentials, full headers or raw provider payloads. Verify real emitted Shared sink records, including original harmless diagnostic text, sensitive-sentinel removal, bounded fields and sink-failure isolation. Preserve actual failure behavior even when logging fails.

## Work items and acceptance criteria

- [ ] Verify accepted upstream commits, installed Shared export/version and the actual Background baseline; record rebase differences before edits.
- [ ] Load/validate Platform and optional Shop instructions with intended precedence, and construct trusted policy/purchase context without historical-price inference.
- [ ] Enforce published/built-in identity and current permission checks for observations; retained-grant mismatch never silently expands access.
- [ ] Validate all three proposal scopes, independent alternatives and nullable variants; prove same-shop/provider source matching and exclusion precedence.
- [ ] Preserve conservative initial-outreach behavior through the common-check adapters; support only represented money/condition/combination calculations.
- [ ] Enforce the exact optional outcome and terminal-error/referral boundary, including an error followed by a successful read.
- [ ] Revalidate selected facts within the real shared turn budget; changed/unavailable facts cannot leave stale promotional wording in the returned text.
- [ ] Render the full recommendation branch in the resolved language, with no raw free-text promotion bypass and complete 20-locale fixed-message coverage.
- [ ] Preserve legacy evidence validation and unchanged processor/wrapper/moderation/admission/HUMAN/ordering behavior.
- [ ] Capture original safe error diagnostics at the actual Shared sink with redaction and failure-isolation assertions.

## Focused fixtures and validation

`product-recommendations.v1.json` must cover two shops/providers reusing local IDs; a known-price simple product and nullable Woo variant; a variant mismatch; exact/category/collection targeting and exclusions; supported percentage/amount terms; native sale; conditional subtotal; unknown quantity scope/customer condition; currency mismatch; NONE/FIXED/AI plus override/selection change; compatible/incompatible offers; partial discovery; typed optional unavailable; terminal error; and before/after source changes. Mark synthetic products/IDs as fixtures, not real Shopify taxonomy evidence.

Host suites must assert complete returned text, not just `details`/IDs. Include null-grant initial context followed by real retained-grant context, malformed/cross-shop context rejection, a malicious raw model reply with a forged code/saving, missing selection, forged same-shaped result from an unrelated tool, changed price/quantity between selection and refresh, selected-offer revalidation failure, exhausted refresh budget, and stale/HUMAN cancellation during a blocked tool response. Use deterministic barriers/fake clocks rather than sleeps. The real PostgreSQL context test verifies published revision ownership, current policy/override, actual grant insertion through the updated database guard and source/basket changes against the accepted schema.

Before Node commands, use the workspace's existing bootstrap contract if Node is absent; do not install/select another version. From the implementation worktree run the actual package commands:

```sh
npm ci
npm run prisma:generate
npm run lint
npm run build
npm exec vitest run tests/unit/commerce/recommendations tests/unit/commerce/host-diagnostics.test.ts tests/unit/commerce/mcp-client.test.ts tests/unit/commerce/evidence.test.ts tests/unit/agents/initial-outreach-offer.eligibility.test.ts tests/unit/agents/initial-outreach-offer.combinations.test.ts tests/unit/agents/initial-outreach-offer.graph.test.ts tests/unit/services/recovery-offers/current-outreach-offer-revalidation.service.test.ts
npm exec vitest run tests/integration/commerce/host.test.ts tests/unit/services/conversation-turn-processor.service.test.ts
node scripts/test-integration.mjs tests/integration/commerce/recommendation-context.integration.test.ts
git diff --check
```

Use disposable/test configuration for the PostgreSQL command; no production migration or provider/send action is authorized by this task. Do not report skipped/blocked tests as passes or infer provider/model semantic quality from scripted host tests. Follow documented baseline IDs only when a matching condition is actually encountered; any new regression must be investigated.

## Dependencies, overlap and non-goals

MCP-002 and COMMERCE-001 are the only direct task prerequisites; their accepted dependency chain includes the Shared publication and Database work. Terminal SYSTEM-TEST-001 consumes this task, never gates it.

At launch rebase on the actual accepted Background state, especially ARCH-056 inbound persistence, initial credit/admission and recovery-progress work. Preserve those accepted changes and their active owners. This task deliberately leaves `conversation.service.ts`, `whatsapp.worker.ts`, `conversation-turn-processor.service.ts` and initial outbound/billing owners read-only. The two initial-outreach helper adapters and any strictly necessary union guards must preserve accepted behavior; a real concurrent writer requires scoped coordination, not blanket reopening of ARCH-056/052 or an invented prerequisite on every task.

No new agent/worker/queue, provider-proof service, cart mutation, discount creation, taxonomy storage/import, Admin/Redis changes, database migration, package publication, broad evidence redesign, deployment, indexes or task-status changes outside this task are authorized. No sibling application imports or implementation files in the parent workspace.

## Completion Report

Not started. On execution record the prepared worktree/synchronization packet; exact parent/implementation branches and commits; accepted dependency SHAs and installed Shared package/export evidence; changed files; the final context/selection/built-in adapters; budget and revalidation boundary; full-text and locale tests; actual commands/results; original safe/redacted sink evidence; source overlap resolutions; limitations and any blocked checks. Record implementation and parent task/report pushes or their exact failure; do not claim merges or deployment.

## Architect Review

Pending. Review both task/report and implementation histories, physical task isolation, accepted contracts, scoped initial-outreach preservation, error/evidence semantics, full-message composition and recorded validation before acceptance.
