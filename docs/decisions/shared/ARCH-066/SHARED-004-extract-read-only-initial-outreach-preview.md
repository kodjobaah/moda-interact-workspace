---
id: ARCH-066-SHARED-004
architecture_id: ARCH-066
title: Extract read-only checkout outreach evaluation and rendering
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
depends_on: ["ARCH-066-SHARED-001", "ARCH-066-SHARED-002", "ARCH-066-SHARED-006"]
enables: ["ARCH-066-SHARED-005"]
created: 2026-11-08
updated: 2026-11-08
---
# Extract read-only checkout outreach evaluation and rendering

## Normative contract
Implement [the complete outreach contract](../../../architecture/ARCH-066-initial-outreach-contract.md), sections1–7. It fixes exported schemas/signatures, strict input/result shapes, source relocation, ordered live reads, error mapping, offer behavior, rendering and tests. It overrides the earlier shell definition. No architecture choices are delegated to the implementor.

## Owned files and work
- NEW `src/commerce/outreach/{contracts,evaluate,reconcile,selection,render,index}.ts` and matching `.test.ts` files; public package export `./commerce/outreach` and build/export checks. Internal pure helpers may be split under this directory only.
- Port sources listed in contract section3, including actual pure template helpers in `recovery-template-preparation`, not the service facade. Export evaluateInitialOutreach with preview alias; one implementation for production/preview.
- All public payloads use strict Zod and inferred types. Replace source z.custom placeholders for nested price/eligibility/combination data with actual field validators; canonical money/product/tool/offer schemas reused.
- Live exact product reads before selection and revalidation after selection, including NONE; sequential first-occurrence order, duplicate reuse, no catalogue search. Preserve checkout quantity and historical price. Existing production fingerprint/admission IDs stay host-owned.
- NONE uses zero model/offer calls. Existing bounded checkout-offer graph/eligibility/combination rules apply otherwise. New checkout-only schema rejects alternative-product choices; historical parsing stays host-owned.
- Render frozen approved initial template bindings using the same checkout summary/selection/parameter algorithms in both hosts. Prepared media and catalogue inputs only; no upload/DB/send orchestration. No conversation wrapper substitution.
- Add `scripts/validate-commerce-outreach.mjs`, registered as `validate:commerce-outreach`; import all four public schemas, evaluator and renderer from packed public JS/declarations. This task builds/packs locally but does not publish.

## Required acceptance evidence
- [x] Strict schema fixtures and all closed refusal reasons from contract section5; malformed nested payload rejected before use.
- [x] Ordered port-call spy: ready NONE reads each distinct checkout pair exactly twice, never model/offer/search; duplicate lines retain their quantities/order.
- [x] Changed-price/current-facts, currency, missing product, wrong parent/tenant, revoked access, cancellation, deadline and exhausted-budget tests. Final-return regression coverage added in Attempt 2; see correction disposition below.
- [x] Existing checkout-offer goldens preserved except explicit checkout-only restriction; no stale checkout price used as live evidence. Sendable method projection restored in Attempt 2; see correction disposition below.
- [x] Both-provider fixtures for clothing/nail varnish/trees/custom label; identical code path and no merchandise enum.
- [x] Exact prepared-template parameter/body/header goldens, no-ready-image TEXT fallback, missing approved template/locale, escaped/control/Unicode/4096 boundaries.
- [x] Package typecheck/build, focused tests, `validate:commerce-outreach`, pack public import/declaration check and diff check. Record unavailable checks candidly; no claimed publication.

## Execution / completion
Attempt 2 passes developer self-review, including both Attempt 1 corrections. Explicit developer completion remains required. Preserve unrelated edits; Shared owns no service repository edits. SHARED-005 publishes accepted source. No production send/deploy authorized.

Generic product payload validation uses accepted SHARED-006 implementation as source prerequisite; no competing schema edits. Source subtree ordering is006 then004, followed by005 publication.

## Dependency frontier reconciliation — 2026-11-08

ARCH-066-SHARED-006 is Complete at accepted Attempt 1, recorded and pushed in parent task commit `918e45713ff5ca80d7832ca46480ddb2514894a1`, with accepted implementation `2bc7f02c16840a41154f2135a26f9ba52c71fad7`. Together with completed SHARED-001 and SHARED-002, all explicit dependencies are satisfied. This task is Ready, unclaimed at Attempt 0; this reconciliation does not start implementation. SHARED-005 remains Pending until SHARED-004 completes.

## Completion Report

### Status

Passed / Accepted — Attempt 2. Both required corrections pass developer self-review. Status remains Review pending explicit developer completion.

### Preparation

Canonical launcher synchronized dedicated parent and implementation task worktrees, verified completed dependencies and recursive submodules, and set developer Attempt 1. Its report update stopped because the original definition lacked this section. Added the required section and published the existing claim without incrementing again. Explicit implementation and task-branch publication authorization retained; developer completion remains explicit.

### Implementation / source evidence

Current Attempt 2 implementation `987a05dd06e79aa465d11fce8a4d4fe8b8d52703` is pushed to `origin/task/ARCH-066-SHARED-004`; local HEAD equals the published ref and the implementation worktree is clean. Original Attempt 1 implementation `2a31e9cd7202833bd4a35242e3999fed191a7289` remains its ancestor; historical review evidence is preserved below. Source baseline `b8743a2` already contains accepted SHARED-006 `2bc7f02c16840a41154f2135a26f9ba52c71fad7` (ancestry verified). No competing generic product schemas, consumer changes or package version bump. Source package remains 5.6.0; this local packed artifact has not been published. SHARED-005 owns the immutable release.

Initial implementation changed 28 task-owned files; Attempt 2 adds the internal sendable-offer helper and corrects the seven files recorded below. Initial file scope: package export/script and tsup entry; new `scripts/validate-commerce-outreach.mjs`; the outreach contracts/evaluator/reconciliation/selection/renderer and extracted pure eligibility, combinations, money, instructions, template bindings/summary/initial-slot/variable helpers; focused fixtures/tests and source-relocation README. Background source reference `d7e78bdb5e75248b9a15e2c84d07dcdc89027c19` was inspected read-only. No service repository was edited. Existing source algorithms are retained under Shared-local imports; model/tool services are replaced with injected ports. The deliberate checkout-only amendment excludes alternative-product search/promotion and rejects unexpected choices with OUTSIDE_CHECKOUT. Host recovery/admission identity and write/send fences remain outside Shared.

### Acceptance / implementation review report

- Strict public evaluation/render input/result schemas and inferred types; real nested eligibility/group/price/registration/binding validators replace source placeholder validation. Canonical Commerce product, currency, money, environment and tool contracts are reused. Input native IDs, unique line keys, nullable merchant revision pair, discount authorization and pre-I/O UTF8 bound are checked. Unknown tool names/arguments and malformed nested results fail closed; all closed evaluation refusal codes have exercised paths.
- Ready NONE has sequential first-occurrence exact reads before and after selection, deduplicated by product/variant pair; duplicates retain original line order and quantities. No model, offer or search calls occur in NONE. Current availability, exact parent/variant, provider and observation freshness are checked; authenticated tenant scoping is the host port's responsibility, with trusted run/shop/platform/signal supplied by Shared. Foreign output envelopes are rejected rather than trusted.
- Reconciliation retains historical and current unit prices, uses decimal-safe minor units and original quantities, and labels only a current merchandise subtotal. Fingerprint uses the ordered canonical price-basket content algorithm without host recovery/attempt identity. No payable-total or checkout-repricing proof is fabricated.
- FIXED reads authorized details only; AI lists bounded checkout options, reads tied details and submits identifier-only choices. Existing eligibility and max-three compatible combination algorithms remain authoritative, including unknown targeting/customer/usage restrictions and Shopify/Woo rules. Existing POLICY_NONE/NO_AUTHORISED_DISCOUNTS/NO_APPLICABLE_OFFER reason codes retained. Missing eligible discounts produce a successful no-offer decision. Malformed or outside-checkout choices refuse.
- Same signal, admitted deadline/model-step/remote-call/token budgets and bounded activity apply throughout. Every actual tool/model attempt counts, deduplicated reuse does not; no automatic retry loop. Cancellation/deadline overrides late results. Final reads verify every distinct product and every selected offer's details/eligibility. Observation timestamp refresh alone is not a fact change; changed facts or revoked access cannot return ready. No raw provider body/credentials enter diagnostics.
- Frozen registration/variant/binding field names and digest/token/slot/summary/parameter algorithms are preserved. Synchronous prepared variable/media resolution performs no DB/network/upload calls. Optional host-prepared approved TEXT fallback goes through the same selection/status/locale/hash checks when IMAGE lacks ready media. Exact parameter order, provenance and full text header/body/footer are tested; body 4096 UTF16 admitted and 4097 refused without truncating parameters/URLs/offer terms. Missing approved assignment, locale, bindings, values or media refuses. No conversation wrapper substitute.
- Both-provider clothing/nail-varnish/tree/custom-label fixtures use the same evaluator with open merchant facts. Existing product-fact/presentation/runner compatibility checks pass; no merchandise enum is introduced. Packed public imports include generic description/attributes, verifyCommerceProductFacts and PRODUCT_DETAILS alongside outreach.

### Validation

Node 24.19.0 from canonical workspace bootstrap; `npm ci --ignore-scripts` installed the existing lockfile with no dependency/version edits.

- `npm run typecheck`: passed after final source changes.
- `node --import tsx --test src/commerce/outreach/*.test.ts src/commerce/product-facts.test.ts src/commerce/product-context.test.ts src/commerce/presentation/facts.test.ts src/commerce/presentation/presentation.test.ts src/commerce/runner/runner.test.ts`: **171 passed, 0 failed, 0 skipped**, confirmed again during Attempt 2 review. Includes all new contract/reconciliation/assignment/offer/evaluation/render goldens and affected existing compatibility tests.
- `npm run build`: ESM plus declarations passed for final runtime source.
- `npm run validate:commerce-entrypoints`: passed; existing commerce/runner clean-process imports and R1/R2 regressions retained.
- `npm run validate:commerce-presentation`: passed in Node and browser-like bundled context, with no new browser export dependency on server globals.
- `npm run validate:commerce-outreach`: passed. Packs locally, installs that exact tarball in an isolated temporary project, typechecks all four public schemas and exported types/functions through the public declaration path, then evaluates deterministic NONE and renders a hash-verified ready frozen template through installed public JS. Verifies strict rejection, exact subtotal/call count/parameters/text/provenance, alias identity, prior presentation imports and generic description/attribute/PRODUCT_DETAILS compatibility. Temporary project removed; no npm publication.
- `git diff --check` and staged diff check: passed.
- Lint unavailable: package declares no lint script or lint dependency. It is not claimed passed, and unrelated tooling was not added.

### Isolation / publication / lifecycle

Canonical dedicated parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-066-SHARED-004` and implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-066-SHARED-004` were used on mirrored `task/ARCH-066-SHARED-004` branches. Deterministic developer preparation fetched/synchronized parent and implementation, verified the completed 001/002/006 dependency gate and recursive submodules, then set Attempt 1. Report-format repair and durable claim `3340bc39b` retained that same attempt. Current primary checkout was used only as canonical routing/read-only source reference. No subagent assistance was used in this attempt; the Codex root adopted moda_shared implementation scope under the developer's explicit implementation/publication authorization.

Implementation publication succeeded; this parent record is the corresponding review submission. No task branch was merged into main, no main push or feature gitlink staging, and no package release, migration, deployment or production message occurred. No known scoped acceptance item remains incomplete at submission. Formal `/moda_developer_update ARCH-066-SHARED-004` reconciliation/acceptance and subsequent explicit completion are pending; no passing Architect Review is fabricated here. Attempt stays 1, executor/claimed_at cleared for review. SHARED-005 remains Pending until this task is accepted and explicitly completed; no downstream task is claimed.

## Developer Self-Review - Changes Requested — Attempt 1

2026-11-08: Reconciled the complete task/contract, actual implementation diff and key evaluation/rendering boundaries, existing Background sendable-offer preparation and claimed validation. Implementation `2a31e9cd7202833bd4a35242e3999fed191a7289` equals the published origin task ref (verified directly with ls-remote). Parent submission `e1e4e459012fda729c29cf16f4cb6f6d6343a403` equals its tracking ref. Both canonical worktrees were clean before this review record. Dedicated worktrees, synchronization/claim repair, source ancestry and absence of subagent assistance remain as recorded above. No implementation source was changed during review.

Existing validation is real but insufficient for acceptance: a fresh `node --import tsx --test src/commerce/outreach/*.test.ts` run passed **57/57** tests, while the two independent boundary reproductions below expose missing cases. Initial `npx tsx --test` review invocation could not open its IPC socket under local filesystem restrictions; Node's supported import-loader invocation ran the same tests successfully. Previous 156-pass focused compatibility, typecheck/build/public entrypoint/packed-artifact evidence remains recorded; it does not cover these defects. Lint remains unavailable and is not claimed passed.

### Required corrections

1. **[P1] Recheck cancellation and deadline at the actual ready-return boundary.** In `src/commerce/outreach/evaluate.ts:263–270`, the last check runs before fingerprint/result assembly, evaluatedAt capture, byte/schema validation and the final COMPLETE log callback. No check follows those operations. A deterministic NONE reproduction using existing fixture/ports counted 26 clock reads, then advanced the clock to run expiry on read 26 (the result's evaluatedAt capture). It returned `{kind:"ready",evaluatedAt:"2026-11-08T17:00:01.000Z"}` at the exact expiry `2026-11-08T17:00:01.000Z`. A second reproduction aborted the shared signal in the final COMPLETE log callback; it returned ready with `signal.aborted === true`. This violates the contract that cancellation/deadline wins over later completion. Add a final fence after all result construction/validation and any externally supplied callback before returning ready; route expiry/cancellation through the typed refusal path. Add deterministic tests for expiry crossing during finalization/evaluatedAt capture, cancellation during finalization/COMPLETE callback, and a just-before-expiry valid result. Assert no ready result at or after expiry or with an aborted signal. Reuse the original signal and preserve bounded activity; do not add retries or budgets.

2. **[P2] Preserve mixed-method checkout offer presentation before rendering.** In `src/commerce/outreach/render.ts:13–24`, any CODE member chooses CODE_OFFER, but offerCount includes all members. `variables.ts:50–60` then requires either exactly one member or all members to be CODE and joins all descriptions. The evaluator/combination contract permits compatible CODE plus AUTOMATIC members. Existing Background `automated-recovery-template.service.ts:443–468` deterministically groups by method, selects the largest sendable method group (stable first-occurrence tie), and derives presentation/codes/description from that group; the template preparer uses the code count. Reproducing a valid ordered supported CODE+AUTOMATIC decision with an approved single-code frozen template returns NO_APPROVED_ASSIGNMENT in Shared because two total members demand offer.codes, although the source algorithm selects the first CODE singleton and supplies offer.code. With a multi-code binding, the all-CODE variable check also rejects a mixed set. Relocate/reuse that existing deterministic sendable-method projection in the Shared rendering path, consistently deriving purpose, binding count, codes and description from the same selected group without mutating evaluation evidence or inventing terms. Add goldens for one CODE plus one AUTOMATIC in both orders, larger CODE and larger AUTOMATIC groups, homogeneous single/multiple CODE, and automatic-only groups. Verify exact parameters, text and purpose against the existing host algorithm. Keep eligibility/revalidation on the original selected evidence and preserve the intentional no-alternative-products amendment.

### Required validation / transition

Both findings require source and regression-test changes; a no-source-change revalidation is not a corrected attempt. Rerun focused outreach plus affected product/presentation/runner compatibility tests, package typecheck/build, existing commerce-entrypoint/browser presentation checks, packed public JS/declaration smoke and diff check after correction. Record each correction separately as implemented or concretely blocked. Do not edit an Architect Review section or fabricate acceptance.

Transition to Ready, executor/claimed_at null, reviewed Attempt 1 unchanged; execution_mode/completion_mode developer retained. The next canonical developer preparation claims Attempt 2 once. No passing review or completion is recorded. SHARED-005 remains Pending, and no downstream task is promoted or claimed. This parent review record is committed/pushed on task/ARCH-066-SHARED-004; implementation remains published unchanged. No package publication, service modification, main merge or main push.

## Attempt 2 Correction Report — 2026-11-08

### Review contract / scope

Read the entire synchronized task, including the latest complete Attempt 1 Changes Requested review and its two mandatory source/test correction requirements, before implementation. No separate Architect Review section exists. This attempt implements both requested corrections on the same canonical mirrored task branches; historical Attempt 1 submission/review is preserved. The developer explicitly authorized implementation, validation and claim/source/report publication. No subagents were used.

### Correction disposition

1. **Implemented — final ready cancellation/deadline fence.** `src/commerce/outreach/evaluate.ts` performs the final check after fingerprint/result construction, evaluatedAt capture, byte/schema validation and the COMPLETE diagnostic callback, immediately before returning ready. The check uses one captured clock value and rechecks the original signal after the clock callback, so cancellation during that callback also wins. Expiry/cancellation takes the existing typed refusal path; original signal, activity accounting, no retries and admitted limits are preserved. Five `evaluate.test.ts` regressions cover expiry during evaluatedAt finalization, expiry in COMPLETE, cancellation in COMPLETE, cancellation during the final clock callback, and a ready result one millisecond before expiry. They assert exact refusal reasons, two NONE product reads, no model/offer calls, unchanged signal and bounded activity.

2. **Implemented — shared sendable-method projection.** New internal `src/commerce/outreach/sendable-offer.ts` relocates the existing Background largest-method-group rule with stable first-observed-method ties and original within-group order. `render.ts` selects once and uses that group's presentation/member count for assignment/purpose; the same projection is injected into `PreparedVariableResolver` for single/multiple codes and descriptions. Description joining now preserves the original host's comma separator. Evaluation evidence is neither filtered nor mutated. Nine `render.test.ts` fixed goldens cover CODE+AUTOMATIC and AUTOMATIC+CODE ties, larger CODE and larger AUTOMATIC groups, one/two/three homogeneous CODE members and one/two automatic-only members. They assert exact purpose, body/button parameters, text and unchanged original evaluation. An additional `offers.test.ts` integration test retains all three compatible original mixed selected members, checks supported eligibility and exactly two detail reads per selected offer, proving display grouping does not narrow final evidence revalidation. Alternative-product exclusion remains unchanged.

### Regression proof / validation

The newly requested evaluation/render cases were executed before source corrections and exposed the reviewed defects: four final-ready fence cases failed; mixed-group rendering and multi-description host-separator cases failed, while valid controls passed. After correction all targeted tests passed. Final validation on the published correction source:

- `npm run typecheck`: passed.
- `node --import tsx --test src/commerce/outreach/*.test.ts src/commerce/product-facts.test.ts src/commerce/product-context.test.ts src/commerce/presentation/facts.test.ts src/commerce/presentation/presentation.test.ts src/commerce/runner/runner.test.ts`: **171 passed, 0 failed, 0 skipped** (15 new correction tests over the previous 156). The supported Node import-loader form avoids tsx CLI IPC restrictions while executing the same test files.
- `npm run build`: final ESM and declaration builds passed.
- `npm run validate:commerce-entrypoints`: passed, including clean imports and R1/R2 regressions.
- `npm run validate:commerce-presentation`: Node and browser-like entrypoints passed.
- `npm run validate:commerce-outreach`: passed, packing/installing the exact local tarball in an isolated temporary project and checking public JS/declarations, deterministic evaluation and frozen ready rendering, generic product facts/PRODUCT_DETAILS and prior presentation compatibility. No package publication.
- `git diff --check` and staged diff check: passed.
- Lint remains unavailable because no lint script/dependency is declared; no passing lint claim or unrelated tooling change.

### Files / publication / lifecycle

Seven task-owned source/test files changed: evaluate.ts/evaluate.test.ts, render.ts/render.test.ts, variables.ts, new sendable-offer.ts and offers.test.ts. Correction commit `987a05dd06e79aa465d11fce8a4d4fe8b8d52703` is pushed to origin/task/ARCH-066-SHARED-004; implementation HEAD equals that remote ref and its worktree is clean. No dependency/version, public payload shape, service repository, production-send or deployment changes.

Launcher reused the canonical parent and implementation worktrees on task/ARCH-066-SHARED-004. Parent before claim `dd4a1ad8457f4436b151a3520fff239fbcd209b6`, implementation before correction `2a31e9cd7202833bd4a35242e3999fed191a7289`; both remote fast-forwards not needed and current origin/main already incorporated. Recursive submodule sync/update passed with no entries. Dependency gate 001/002/006 passed. Claim `36ced1dba256b347234ce57b7890ba0de40c9a2d` durably incremented 1 to 2 exactly once under executor developer at 2026-11-08T17:31:41Z. No shared checkout switching, unrelated worktree reuse, feature gitlink staging, main merge/push or force push.

This updated report is the Attempt 2 review submission, not fabricated architect acceptance. Both requested corrections are implemented with no known outstanding scoped correction at submission. Status Review, Attempt 2 unchanged, executor/claimed_at null; execution/completion modes remain developer. Formal `/moda_developer_update ARCH-066-SHARED-004` review and subsequent explicit completion remain pending. SHARED-005 stays Pending until completion; no downstream claim or package release.

## Developer Self-Review — Passed / Accepted Attempt 2

2026-11-08: Reconciled the full current task, normative contract, complete Attempt 1 Changes Requested review, seven-file correction diff, new regression assertions and original host sendable-method projection. Reviewed implementation `987a05dd06e79aa465d11fce8a4d4fe8b8d52703` matches local HEAD, origin tracking ref and directly verified published remote task ref. Parent correction submission `5dc6f9952e22fc4e10e0a5890ce1c200ba75577f` matches its published tracking ref. Both canonical worktrees were clean before this review record. No source edits or new attempt were made during review; original accepted dependency ancestry, isolated worktrees, synchronization/claim evidence and no-subagent assistance remain as recorded above.

### Correction review disposition

1. **Accepted: actual ready-return fence.** The final check now follows fingerprint/result assembly, evaluatedAt capture, output byte/schema validation and the COMPLETE host callback. No further callback runs before ready is returned. The check captures the clock once and checks the shared signal after the clock callback, so cancellation during that callback also refuses. Five deterministic regressions explicitly assert expiry during evaluatedAt capture, expiry/cancellation in COMPLETE, cancellation during the final clock callback and a valid just-before-expiry result. They also retain the original signal, bounded activity, two NONE reads and no model/offer calls. Both independently reproduced Attempt 1 failures are addressed by source changes and behavioral assertions.

2. **Accepted: stable sendable offer projection.** The new internal helper groups members by CODE/AUTOMATIC, chooses the largest group with first-observed-method ties, and preserves member order, matching the existing Background algorithm. Render purpose/count and code/description resolution consume that same projection. Comma-joined descriptions preserve the host's original output. Nine fixed goldens assert exact purpose, body/button parameters and text for both mixed tie orders, each larger mixed group and homogeneous single/multiple groups; the original evaluation remains unchanged. The additional mixed-selection test verifies all three original selected offers remain supported and receive final detail revalidation. Eligibility, evidence, public result shapes and the no-alternative-products restriction remain intact.

### Validation / acceptance limits

Fresh review run: `node --import tsx --test src/commerce/outreach/*.test.ts src/commerce/product-facts.test.ts src/commerce/product-context.test.ts src/commerce/presentation/facts.test.ts src/commerce/presentation/presentation.test.ts src/commerce/runner/runner.test.ts` passed **171/171**, no failures/skips. `npm run typecheck` and `git diff --check` passed. Recorded final-source ESM/declaration build, commerce/runner entrypoint checks, browser-like presentation check and isolated installed-tarball public JS/declaration evaluation/render smoke remain applicable to this exact unchanged source and were reconciled; no redundant build or package installation was needed. Lint is explicitly unavailable because the package declares no lint script/dependency; it is not claimed passed and this task introduces no new lint regression.

No outstanding scoped correction or incomplete required acceptance item was found. Review does not claim live provider/model validation, consumer integration/deployment or npm publication; SHARED-005 still owns the combined immutable release. Historical Attempt 1 Changes Requested and Attempt 2 correction reports are retained, and no Architect Review section is fabricated or modified.

Status remains Review, executor/claimed_at null and accepted Attempt 2 unchanged, with completion_mode developer. Passing review and current Completion Report are published on the parent task branch. Explicit `/moda_developer_update ARCH-066-SHARED-004 complete` is pending; SHARED-005 remains Pending until completion/frontier reconciliation. No downstream task was promoted/claimed, no implementation gitlink staged and neither task branch was merged or pushed into main.
