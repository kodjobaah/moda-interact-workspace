---
id: ARCH-066-SHARED-001
architecture_id: ARCH-066
title: Define product options, trusted context and lookup recovery contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: ["ARCH-066-SHARED-002", "ARCH-066-DATABASE-001", "ARCH-066-SHARED-003"]
created: 2026-11-08
updated: 2026-11-08
---
# Define product options, trusted context and lookup recovery contracts

## Objective and read first
Implement only the owned work below. Read `docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md` first: its numbered contract decisions are normative and must not be redesigned by the implementor.

## Context / scope
Observed failure: a later sizing question used an invalid Woo product ID; several corrected calls failed and a successful search could not clear the runner's referral latch. Product outputs currently omit options. Own Shared schemas, context reducer and runner recovery; never edit service repositories.

## Touch points and exact work
- `src/commerce/schemas.ts`: add optional `options` and `selectedOptions` to CommerceProductSchema, according to architecture decision 1; retain commerce.v1 and all existing required fields. Existing persisted products must still parse.
- NEW `src/commerce/product-context.ts`; export from `src/commerce/index.ts`: implement CommerceConversationProductContextSchema, `mergeConversationProductContext(previous, observations, identity)` and `resolveConversationProductReference(context, reference)`. Use decision 2 exactly; no prices or tool authority from persisted context. Export observation type `{toolName, products: CommerceProduct[], observedAt}`; identity `{shopId,conversationId,platform,now}`; reference `{productId?:string,variantId?:string|null,title?:string}`. Return resolution `{kind:'MATCH',productId,variantId}|{kind:'AMBIGUOUS'}|{kind:'MISSING'}`; case-folded trimmed exact title matches only, no fuzzy guessing.
- `src/commerce/runner/types.ts`, `preflight.ts`, graph state, `tool-execution.ts`, `graph/nodes/validate-final-response.ts`, `final-response.ts`, `diagnostics.ts`, `diagnostic-messages.ts`, `graph/nodes/invoke-model.ts`: implement decision 3. Keep optional input `productContext` separate from arbitrary history; validate shop/conversation match before model I/O, project it into model context as untrusted references, never evidence.
- Add optional bounded result metadata `productContextUpdate` to successful runner results, populated only from successful validated commerce_search_products / commerce_get_product observations. No raw provider data, credentials or model-created IDs. Host supplies platform; preserve current final-response schema and selection authority.
- Recoverable errors: INVALID_INPUT and NOT_FOUND do not set requiredReferral. DENIED/revocation remains sticky. UNAVAILABLE/THROTTLED/DEADLINE remain sticky for the turn. STALE_TURN/cancellation remain terminal. Do not clear hard failures after a success. Correctable failures still consume normal budgets and appear in tool activity.
- On provider finishReason length with neither visible text nor calls return BUDGET_EXHAUSTED diagnostic MODEL_OUTPUT_TOKENS_EXHAUSTED at model.route, not MODEL_CALL_ROUTE_INVALID. Never fabricate a reply or silently retry/increase budgets.

## Acceptance / validation
- [x] Contract fixtures: old product, options bounds/duplicates/controls, partial options, selected variation, no sizes and malformed source handling.
- [x] Context tests: two products same name => AMBIGUOUS; foreign tenant/conversation rejected before model/tool I/O; expiry; deterministic eviction; deleted ID corrected through search; no price becomes evidence.
- [x] Runner tests: NOT_FOUND -> valid product lookup -> ANSWER allowed; invalid arguments -> valid lookup allowed; DENIED -> success still requires referral; provider outage -> success preserves hard latch; token truncation precise diagnostic.
- [x] Existing runner, grants, final-response/evidence, product-discovery and response.v1 tests pass. Run package typecheck/lint/build using repository scripts. No npm publication in this task.

## Execution boundary
Definition only. Do not claim or implement until explicit dependency tasks are Complete. Use the canonical launcher-resolved parent and implementation task worktrees; execution_mode and completion_mode are developer. Do not change unrelated work or another repository. Record exact Shared package version/integrity, database migration and provider schema artifact used. No production customer messages, Meta registrations or live mutations are authorized by this task.

## Completion Report

### Status
Ready for Review — Attempt1. Implementation and available declared validation passed; lint capability gap below. Acceptance/completion pending; no follow-on task started.

### Files Changed
14 task-owned source/test paths in implementation ce24e4550c0a7b2e93c1311437ac35a2d605ffae: commerce schemas/index/new product-context module/tests; runner types, preflight, result assembly, instructions, execution, model route, diagnostics/messages, invoke-model and runner tests. No consumer, package/lock/schema/provider artifact edits.

### Work Completed
Additive product options/selectedOptions retain commerce.v1 and legacy absent fields. Normalize ordinary whitespace, reject controls, omit malformed/overlong labels, preserve exact factual labels and provider order, deduplicate/bound collections with truthful PARTIAL status. Context strict schema admits bounded native Shopify/Woo IDs and tenant/conversation/platform identity; merge filters future/expired observations, latest exact identity wins, deterministic lexical order/20-reference/UTF8 bounds. Resolver uses exact known ID or case-folded trimmed exact title, preserving AMBIGUOUS/MISSING.

Runner preflight validates supplied context identity/platform before model I/O; model receives it separately as untrusted stale references, never grants/evidence. Successful result contextUpdate derives only validated successful canonical search/get observations and carries IDs/titles/timestamps, no prices/stock/offers/raw provider payloads. Failed turns emit none. INVALID_INPUT/NOT_FOUND remain normal budget-consuming tool observations; DENIED/revocation and outage/throttle/deadline remain sticky; stale/cancellation terminal behavior unchanged. Empty length-truncated model output reports BUDGET_EXHAUSTED/MODEL_OUTPUT_TOKENS_EXHAUSTED at model.route with no retries or increased budgets.

### Validation Results
- `npm run typecheck`: passed.
- `npx tsx --test src/commerce/product-context.test.ts src/commerce/runner/runner.test.ts src/commerce/selection.test.ts src/commerce/response.test.ts src/commerce/product-discovery-contracts.test.ts src/commerce/product-discovery-projection.test.ts src/commerce/runner/built-in-tools.test.ts`:128 total,127 passed,1 existing consumer-environment projector skip,0 failed.
- `npm run build`: ESM and declarations passed.
- `npm run validate:commerce-entrypoints`: passed.
- `git diff --check`: passed.
- Lint unavailable: repository declares no lint script or ESLint dependency. No new tooling added; this required-validation capability gap is submitted for reviewer disposition, not represented as passing lint.
Fixtures cover legacy products, malformed/partial options, selected options/control/bounds, same-title ambiguity, tenant/conversation preflight rejection, expiry/eviction, deleted-ID recovery, contextUpdate without price evidence, narrow argument/not-found recovery, sticky hard failures and token truncation.

### Deviations / Assistance
Material moda_shared assistance implemented source/tests under explicit developer authorization; root reviewed boundaries and handled publication/report. Actual graph delegates and result assembly changed where needed; no unnecessary state/final-response edits. Launcher synchronized canonical worktrees and set developer Attempt1 before Completion Report format failure; normalized task record and published claim58fc57cb8, no duplicate attempt. Interrupted initial codex launcher made no implementation changes; subsequent deterministic launch resolved developer execution.

### Package / Rollout Evidence
Source package remains5.5.0; no npm publication/new immutable archive integrity in this task. Follow-on SHARED-003 owns release integrity and consumer pins. No DB migration or provider schema artifact consumed/changed by this pure Shared contract implementation; those remain respective follow-on owner tasks. No live model/customer/Meta mutation or deployment claimed.

### Git / VCS
Canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-066-SHARED-001.
Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-066-SHARED-001.
Both branches task/ARCH-066-SHARED-001; launcher synchronized before Attempt1. Implementation baseline06c8fce5c06efee758670f69fb4865c5e2f21b1f. Shared checkouts not switched for task implementation; no other task worktree reused. Claim58fc57cb8 pushed. Implementation ce24e4550c0a7b2e93c1311437ac35a2d605ffae pushed origin/task/ARCH-066-SHARED-001. Parent report committed/pushed matching branch, exact commit available in Git history. No submodule gitlink staged; no main merge/push; no enabled task execution.
