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
attempt: 2
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

Review — Attempt2 developer self-review Passed; explicit developer completion pending.

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

## Developer Self-Review - Changes Requested
2026-11-08: Reviewed actual published implementation ce24e4550c0a7b2e93c1311437ac35a2d605ffae, task contract, product-context reducer, product option transforms, preflight, model projection, result assembly and tool-execution path. Both canonical worktrees clean; implementation and parent1068edae0 match published task refs. Existing 127-pass/1-skip, typecheck/build/entrypoint evidence remains valid for tested cases but does not prove the boundary below.

### Required Corrections
1. **Propagate normalized product outputs to the model.** In runner/tool-execution.ts, canonical product validation calls CommerceProductSchema.safeParse only to test success, then pushes the original result into runtimeMessages. The product options/selectedOptions schemas transform malformed/control/overlong labels and contradictory status into bounded safe output, but those parsed values are discarded. As a result, source options with status AVAILABLE and invalid labels can pass validation while the model receives raw labels/status rather than sanitized PARTIAL data. Replace canonical product payloads with parsed schema output before evidence/model history/context-update consumption; preserve other validated envelope fields. Review the existing built-in output validation for the same transform-discard pattern.
2. Add runner-level regression: canonical successful search/get returns options with controls/overlong labels/contradictory status and oversized option collections; capture the next model invocation and prove only bounded normalized product data arrives, truthful PARTIAL status is retained and selected options are normalized. Assert legacy products remain compatible and malformed non-option result fields still fail as host-invalid output. A standalone schema-normalizer test is insufficient.
3. Re-run affected runner/product contracts plus declared typecheck/build/commerce-entrypoint checks after correction. Keep lint unavailable explicitly documented because package has no lint script/dependency; do not claim passing lint or add unrelated tooling.

### Transition
Status ready; executor/claimed_at null; reviewed Attempt1 unchanged. Next `/moda_developer_create ARCH-066-SHARED-001` claims Attempt2 exactly once. Historical implementation/report/validation retained. No passing review/completion or downstream dependency promotion. Assigned-agent assistance, isolated worktree and publication evidence remain as recorded above. No source fixes made during this review; no main merge/push.

## Attempt 2 Correction Report - 2026-11-08

### Review Read / Scope
Read the complete synchronized task, normative architecture and latest Developer Self-Review Changes Requested before implementation. No separate Architect Review section was present in synchronized task/architecture or primary task record. Developer confirmed the requested reviews as intended correction set. Preserved all historical review/Attempt1 evidence; did not fabricate or modify architect acceptance.

### Correction Disposition
1. **Implemented:** runner/tool-execution.ts retains parsed built-in output and replaces canonical search/get product fields with parsed normalized values before purpose-schema checks, evidence, model history and successful context-update consumption. Other validated envelope/payload fields retained; nullable detail and existing search max20 maintained. Late validation-only discard removed.
2. **Implemented:** six runner.test.ts regressions capture the next model invocation and evidence callback. Tests prove controls/overlong labels/oversized collections produce bounded normalized PARTIAL data; selected options normalized; contradictory NOT_PROVIDED becomes PARTIAL; legacy absent option fields preserved; malformed mandatory non-option product fields fail as host-invalid result.
3. **Implemented:** required affected validations rerun after source correction:
- `npm run typecheck`: passed.
- `npx tsx --test src/commerce/product-context.test.ts src/commerce/runner/runner.test.ts src/commerce/selection.test.ts src/commerce/response.test.ts src/commerce/product-discovery-contracts.test.ts src/commerce/product-discovery-projection.test.ts src/commerce/runner/built-in-tools.test.ts`:134 total,133 passed,1 existing consumer-environment skip,0 failed.
- `npm run build`: ESM/declarations passed.
- `npm run validate:commerce-entrypoints`: passed.
- `git diff --check`: passed.
- Lint remains unavailable (no package lint script or ESLint dependency); not claimed passed and no unrelated tooling added.

### Files / VCS / Assistance
Only src/commerce/runner/tool-execution.ts and src/commerce/runner/runner.test.ts changed in correction commit c3f9f07, pushed origin/task/ARCH-066-SHARED-001. Material moda_shared implementation/test assistance retained under developer execution ownership; root reviewed correction and handled publication/report. No consumer/version/dependency/publication changes.
Same canonical parent and implementation worktrees reused on task/ARCH-066-SHARED-001. Launcher synchronized both before Attempt2, then report-format failure occurred after setting claim; normalized report and published claim83d1d1487 without another attempt increment. No unrelated edits or shared-checkout switching; no main merge/push or submodule gitlink staging. This report is published on matching parent task branch. No enabled task started; review/completion remains pending at unchanged Attempt2.

## Developer Self-Review - Passed / Accepted Attempt 2
2026-11-08: Reconciled full task and normative architecture, historical Attempt1 Changes Requested, complete Attempt2 correction diff and regression assertions. Implementation c3f9f07cfcf9ff60817f89d5c3d2aaca2dddfbf7 matches origin/task/ARCH-066-SHARED-001; parent f20decba0566453bd3b0b086794759798b3b4e26 matches published report. Both canonical worktrees clean; isolation, synchronization, claim and material assistance retained in preceding reports. No new attempt or source edits during this review.

All three requested corrections pass review:
1. Parsed built-in outputs retained; canonical search/get payloads replaced with parsed products before purpose validation, authorization continuation, evidence, model history and context updates. Existing max20 search and nullable detail preserved; validated envelope fields retained.
2. Six runner-boundary tests capture actual subsequent model invocation and evidence callback, proving truthful bounded PARTIAL/selected option normalization, no mutation of original provider object, legacy absence compatibility, context reference update and fatal malformed mandatory fields.
3. Recorded final checks after correction:133 passes/1 existing consumer-environment skip/0 failures; package typecheck, ESM/declaration build, commerce-entrypoint validation and diff check passed. No relevant source change after those checks, so no redundant rerun. Lint disposition: package has no declared lint script/dependency; record unavailable rather than passed. This tooling absence is not a newly introduced regression and no unrelated tooling change is required for scoped acceptance; existing skip is likewise explicitly retained.

No outstanding scoped code correction found. No npm publication, migration, consumer rollout, live model/provider validation or main merge is claimed. Source package remains5.5.0; follow-on publication owns immutable release integrity. Historical reviews preserved. Status review, executor/claimed_at null, accepted Attempt2 unchanged, completion_mode developer retained. Explicit `/moda_developer_update ARCH-066-SHARED-001 complete` is pending; downstream tasks remain gated until completion/frontier reconciliation.
