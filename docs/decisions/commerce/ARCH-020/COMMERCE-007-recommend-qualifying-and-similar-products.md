---
id: ARCH-020-COMMERCE-007
architecture_id: ARCH-020
title: Recommend qualifying and similar products
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 110
executor: null
claimed_at: null
attempt: 7
depends_on:
  - ARCH-020-COMMERCE-016
  - ARCH-020-COMMERCE-015
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-010
  - ARCH-020-COMMERCE-013
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-21
---

# Recommend qualifying and similar products

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Offer bounded factual add/replace suggestions whose eligibility and cost implications are explicit.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

commerce_find_qualifying_products, commerce_find_similar_products and server-side proposal/evidence validation.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

### Independent implementation contract

Binding **C18** in the implementation contracts is the single producer/consumer
specification, including the linked JSON seed and EC01–EC12 matrix.
Producer: return exactly the C18 structured recommendation output and preserve
evidence identity through004 dispatch. Implement EC01–EC12 in a producer/consumer
contract harness with actual recommendation/evaluator code and controlled provider
transport; host-only races are consumer expectations, not code to add to Commerce.
No Background import or prerequisite. SYSTEM-TEST-001 owns real worker integration.


- [ ] Deliver qualifying/similar recommendation helpers and example tool definitions without making them mandatory for every feature or conversation; reuse policy evidence and exact tool revisions.

- [ ] Implement products.findQualifying and products.findSimilar operations and seed their tool definitions/templates. Reuse the deterministic evaluator; do not execute free-form database calculations or loops.

- [ ] Find relevant current variants within bounded searches using inspected product attributes and merchant/customer constraints.
- [ ] Construct add/replace proposals and rerun the evaluator for each; keep similarity and discount qualification separate.
- [ ] Return no more than three customer-facing alternatives with extra spend, resulting total, currency, evidence and uncertainty.
- [ ] Rank unchanged-basket offers by known savings; avoid advertising a higher-spend basket as cheaper solely because its discount is larger.
- [ ] Support host-driven final revalidation through replay of the actual originally
  granted evidence-producing call under C4, including recommendation evidence.

## Interfaces / Contracts

SHARED-001 recommendation/evidence schemas and COMMERCE-016 evaluator; customer consent for future mutation remains out of scope.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C4, C8**. These are required acceptance inputs, not optional examples.

Implement the two recommendation operations exposed through database-defined tools and reuse the evaluator, not a second discount engine. Use C8 deterministic ranking/tie-breaks/provider bounds and C4 ADD/REPLACE proposals. Keep similarity independent of qualification. Exact-call evidence refresh uses the same authenticated grant and current inboundVersion.

### Deterministic review clarification

Implement the C4 Exact-call evidence refresh contract and its named fixtures.
Business MCP names remain arbitrary. Background captures/replays actual calls;
Commerce policy adapters return bounded structured evidence. No hard-coded
evaluator discovery, extra grant, new Shared field or new database table. Apply
C8 shared provider-request counter (including retries) and deterministic ranking
where recommendations are involved.

### Required evidence

Fixtures must cover same inputs->same ordered max3 results, no match, missing attributes, higher-spend proposals, wrong currency, unavailable variant, provider-call ceiling and a changed rule/basket between proposal and revalidation.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-COMMERCE-016
- ARCH-020-COMMERCE-015

All listed prerequisites must be Complete and architect-accepted before a claim.
Use accepted source in dedicated launcher worktrees; readiness never launches work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-010
- ARCH-020-COMMERCE-013
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] New unrelated public-query tools coexist with recommendation helpers; no feature-name switch or mandatory product tool is introduced.

- [ ] A nonqualifying basket receives a supported qualifying suggestion when fixture data permits; unsupported/no-match paths do not invent products or savings.
- [ ] Similar products are not labelled qualifying unless separately evaluated; unavailable variants are excluded.
- [ ] No cart mutation occurs and evidence cannot be replayed across shops, turns or different basket proposals.

## Validation

- [ ] Test custom mapped inputs/response templates on the existing operation, with unchanged proposal/evidence/quantity/currency bounds and no hidden grant expansion.

- [ ] Run fixture cases for qualifying additions, substitutions, irrelevant similarity, unavailable products, no-match, changed offers and extra-spend disclosures.
- [ ] Run local MCP sequence and tampered evidence tests; verify bounded provider calls/deadlines.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; the actual repository must be provisioned before execution preparation.

## Completion Report

### Status

Ready for Review.

### Files Changed

Implementation repository files:
- `src/commerce/products/recommendations.ts`
- `tests/recommendations.test.ts`
- `tests/recommendation-contract.test.ts`

### Work Completed

Implemented the qualifying and similar-product policy operations, deterministic proposal admission and ranking, bounded evaluator processing, currency-safe totals, unavailable-variant filtering, typed evaluator failures, and exact C4 evidence provenance checks. Added a local C18 producer/consumer contract harness using the accepted evaluator, definition executor, mapped authored inputs, controlled provider transport, fixed clock, and canonical evidence digests. Existing recovery and public product-search operations remain available.

#### Correction checklist

- A1-R1 deduplicated and deterministically ordered valid ADD/REPLACE proposals before the ten-evaluation admission cap; focused tests assert cheapest admission, duplicate collapse, call counts, stable ordering, truncation, and max-three output. Implemented in `src/commerce/products/recommendations.ts` and `tests/recommendations.test.ts`.
- A1-R2 preserved typed evaluator failures and deadline handling as fail-closed results; focused tests assert `DENIED` propagation and no subsequent evaluation after failure. Implemented in `src/commerce/products/recommendations.ts` and `tests/recommendations.test.ts`.
- A1-R3 excluded known cross-currency replacements and refused unknown quantities without fabricating a REPLACE proposal; focused tests cover both cases and preserve exact line/quantity semantics. Implemented in `src/commerce/products/recommendations.ts` and `tests/recommendations.test.ts`.
- A1-R4 completed the local C18 producer evidence with actual evaluator/evidence generation, arbitrary mapped definition dispatch, canonical digest verification, unchanged replay, changed basket/rule semantics, and controlled provider transport. Implemented in `tests/recommendation-contract.test.ts`.
- A2-R1 corrected REPLACE admission pricing to use source quantity and candidate/source unit prices, including known/unknown pricing and deterministic pre-cap ordering. Focused tests cover the eleven-candidate admission case, duplicate collapse, source quantity three, and final disclosed totals.
- A2-R2 added post-await and pre-publication deadline/cancellation guards across evaluator, qualifying, and similar paths. Focused tests cover cancellation after the last evaluator, expired deadlines after an earlier result, pending similar searches, and zero subsequent calls after stopping.
- A2-R3 completed the local C18 producer/consumer evidence with a shared provider-request counter that rejects reservation 13, arbitrary mapped tool replay, exact proposal matching, canonical digest/provenance assertions, tampered evidence rejection, configured limits, and fail-closed typed errors. The local contract fixture remains Commerce-owned and imports no Background code.
- A3-R1 remains preserved in the production recommendation implementation; the Attempt 5 fixture correction is limited to `tests/recommendation-contract.test.ts`.
- A4-R1.1 implemented: one top-level mapped execution now uses six valid candidates, one shared fresh budget, real search/rule/facts transport, and no counter preload or artificial request loop. Focused evidence observes `reservations=13`, `providerCalls<=12`, and typed `ERROR` on reservation 13.
- A4-R1.2 implemented in the task-owned consumer double: valid second evidence uses a computed digest; reverse-order two-item selection checks every selected ID; bad second IDs refer with zero deliveries/language writes; async refresh is invoked and counted.
- A4-R1.3 was the prior Attempt 5 fixture state; its legacy pending rows are superseded by the unified Attempt 6 replay flow below, while live host validation remains separate.
- A4-R1.4 was the prior report correction; Attempt 6 replaces its current-state claims with the executable rows recorded below.
- A5-R1.1 implemented in `tests/recommendation-contract.test.ts`: replaced both partial consumer helpers with one provenance-backed replay flow driven by the actual mapped producer fixture. Selected original evidence IDs resolve to authored `{name, toolRevisionId, arguments}` tuples; identical tuples are grouped and the async refresh callback is invoked once per tuple. Unknown IDs return before refresh (`refreshCalls=0`).
- A5-R1.2 implemented: refreshed envelopes are parsed through `CommerceToolOutputs...parse`, truncation is rejected, every selected original item requires exactly one fresh proposal/evidence match, and semantic identity fields, canonical digest and time window are checked before delivery/language writes. Reversed refreshed order accepts; invalid second IDs and truncated replies refer with `deliveries=0`, `languageWrites=0`.
- A5-R1.3 implemented: the same replay flow covers valid timestamp/digest refreshes, expiry beyond `03:01:00Z`, wrong turn, revoked grant and wrong currency. Deferred refresh cancellation returns before delivery. The real mapped producer path records provider activity and preserves exact authored name/arguments; no separately discovered call is used.
- A5-R1.4 implemented: report claims below are limited to executed Attempt 6 assertions. Live MCP/worker/Shopify and system validation remain explicitly developer-owned.
- A6-R1 implemented in `tests/recommendation-contract.test.ts`: replay provenance is a `{name, toolRevisionId, arguments}` tuple included in the grouping key and passed to the async refresh callback. The observed callback count is one for all three selected IDs, with exact arguments `{search: 'shirt', max: 3}` and revision `revision-1`. Each selected original evidence item now validates its canonical digest and time window before refresh; an expired original at `2026-09-21T03:01:01.000Z` returns `REFER` with `refreshCalls=0`, while an unexpired original with changed valid timestamps accepts with `refreshCalls=1`, `deliveries=1`, and `languageWrites=1`.
- C18 shared recommendation outputs and operation descriptors, C4 exact-call evidence identity, C8 deterministic ranking, max-three output, currency/extra-spend disclosure, evaluator bounds, and qualifying/similar separation remain preserved.

### Validation Results

Focused: `npx vitest run tests/recommendations.test.ts tests/recommendation-contract.test.ts` -> 2 files, 11 passed, 0 failed in Attempt 7. The callback spy observed one invocation for the three selected IDs with the exact mapped name, revision and arguments; expired-original validation observed `refreshCalls=0`; changed valid timestamps observed `refreshCalls=1`, `deliveries=1`, `languageWrites=1`.
Typecheck: `npm run typecheck` -> passed in Attempt 7 (`next typegen` and `tsc --noEmit`).
Lint: `npm run lint` -> passed with 0 warnings/errors in Attempt 7.
Build: `npm run build` -> passed in Attempt 7; Prisma client generation and Next.js production build completed.
Full tests: `npm run test` -> 38 files passed, 1 failed; 334 tests passed and 1 failed. The unrelated failure is `tests/discovery-limits.test.ts`, which timed out after 30 seconds in the Redis-backed sequential limit test. No recommendation or contract test failed. This remains an unrelated baseline/environment condition and was not changed.
Whitespace: `git diff --check` -> passed in Attempt 7.

#### Requirement-to-fixture matrix

| Requirement | Fixture/check | Expected side effect | Result |
|---|---|---|---|
| Same inputs produce ordered max-three results | `npx vitest run tests/recommendations.test.ts tests/recommendation-contract.test.ts`; ranking/cap fixture | stable order, cheapest admission, duplicate collapse, max-three output, truncation | passed; focused command 11/11 |
| No match or unsupported qualification | `tests/recommendations.test.ts`; nonqualifying-evidence fixture | empty alternatives, no invented savings | passed |
| Missing attributes and unavailable variant | `tests/recommendations.test.ts`; similarity fixture | exclude unknown type/unavailable product | passed |
| Higher-spend proposal disclosure | `tests/recommendations.test.ts`; exact pricing fixture | disclose exact extra spend and resulting total | passed |
| Wrong currency and unknown quantity | `tests/recommendations.test.ts`; replacement fixtures | zero replacement proposals/evaluations for unsupported inputs | passed |
| Provider/evaluator ceiling and typed failure | `tests/recommendations.test.ts`; 11-candidate, DENIED, deadline, and shared-counter fixtures | evaluate at most 10, reserve at most 12 provider requests, mark truncation, preserve typed error, stop after failure/exhaustion | passed; reservation 13 rejected, no later provider call |
| Changed basket/turn/proposal evidence | `npx vitest run tests/recommendation-contract.test.ts`; real evaluator/dispatch fixture | reject stale or mismatched evidence and produce a new digest after basket/rule change | passed |
| Arbitrary mapped definition and canonical evidence | `tests/recommendation-contract.test.ts`; fixed clock, mapped inputs, controlled provider, computed digest | preserve authored name, arguments, rendered response, canonical digest, and replay identity | passed; generated evidence and full replay proposal order asserted |
| Similarity versus qualification separation | `tests/recommendations.test.ts`; similarity fixture | no qualifying label without separate evidence | passed |
| EC01/02/12 original call and replay | `tests/recommendation-contract.test.ts`; mapped definition executor fixture | retain arbitrary tool name/revision/arguments, pass the tuple to refresh once, preserve mapped inputs, and avoid ungranted discovery | passed; callback observed once with `{name: 'mapped_replay_fixture', toolRevisionId: 'revision-1', arguments: {search: 'shirt', max: 3}}` |
| EC03/05 exact alternative matching | `tests/recommendation-contract.test.ts`, `executes one provenance-backed C18 replay flow...` | three selected alternatives from one call, reversed refresh order, bad second ID and truncated reply | passed; one refresh, exact proposal matching, bad/truncated `deliveries=0`, `languageWrites=0` |
| EC04 independent evidence fields | same contract test replay validation and tampered grant/currency rows | semantic/identity mismatches fail closed only after canonical digest validation | passed; tampered rows returned REFER with zero delivery/language writes |
| EC06/07/08/10 expiry, digest, identity and authorization | same contract test original-window gate, valid changed timestamp, wrong turn, revoked grant and currency rows | valid fresh digest accepted only while original evidence remains valid; expiry/identity/provenance mismatches fail closed | passed; expired original `refreshCalls=0`; changed valid timestamp `refreshCalls=1`, `deliveries=1`; wrong turn `refreshCalls=0`; invalid rows `deliveries=0` |
| EC09/11 typed failures and stale completion | same contract test deferred async refresh with cancellation | pending refresh completion cannot deliver or write language | passed locally; cancellation row returned `deliveries=0`, `languageWrites=0`; live host races remain developer-owned |
| EC01-EC12 producer/consumer effects | focused command above; actual mapped producer and unified replay fixture | arbitrary mapped call, generated evidence, exact replay, proposal/evidence bounds, and local delivery guards are executable; live worker/MCP remains developer-owned | passed locally for executed rows; provider-budget fixture remains reservation 13 with no later transport request |

### Deviations

The full-suite Redis-backed discovery admission timeout is unrelated to the changed recommendation file and remains the only full-suite failure (baseline condition). No live MCP, deployment, Shopify, or system-test validation was launched; those checks remain developer-owned.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Developer-owned live/system validation remains pending, including deployed MCP/worker/Shopify integration and the system-test path. Local producer/replay, tampered-evidence, exact-call provenance, bounded provider-budget and cancellation fixtures were executed and passed.

### Architectural Concerns

None newly reported.

### Git / VCS

Task branch: `task/ARCH-020-COMMERCE-007`, attempt 7; claim cleared for review (`status: review`, `executor: null`, `claimed_at: null`).
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-007`, branch `task/ARCH-020-COMMERCE-007`; this report is the task-owned evidence artifact.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-007`, branch `task/ARCH-020-COMMERCE-007`, final commit `e08b896` (`test(commerce): verify replay provenance and expiry`), pushed to `origin/task/ARCH-020-COMMERCE-007`; preceding implementation commits remain included.
- Recursive database submodule evidence: `5abfd87f57038bae515aaa09ec7c8db62adcfb98` (`database`, `heads/main`).
- No parent service gitlink, main branch integration, or other repository changes were performed.

## Architect Review

### Changes Requested — Attempt 6 — 2026-09-21

**Current decision: Changes Requested; Ready for one scoped harness/report correction. Attempt 6 retained; executor/claimed_at null. Not accepted.** Reviewed implementation `21e150fed34788ae084a30e4466b9fcdb45b1642` and report `73981c7b78168517286bf113ef837137e4d33c46`, verified against remote task heads. Both worktrees clean. No new production recommendation defect is alleged; preserve the runtime implementation.

Independent validation: **11/11 focused tests and 7/7 prior runtime reproductions pass**. The unified helper now uses actual producer evidence, invokes an async callback, checks every selected proposal, rejects truncation and accepts changed valid fresh timestamps/digests. These portions of A5-R1 are resolved. An isolated copy of the submitted test (`/tmp/c007-a6-review/review.test.ts`) confirms the budget still makes exactly 12 provider requests and denies reservation 13. Its two added replay assertions fail: expired original evidence is rescued by a fresh response; the callback receives no original-call arguments. Diff check passes. Typecheck/lint/build and full 334/335 are submitted evidence, not independent full reruns.

#### A6-R1 — Pass actual replay provenance and reject expired original evidence

Files: `tests/recommendation-contract.test.ts` and this report only. Keep the unified helper, real producer fixture and repaired budget path. No additional feature or exhaustive test matrix is requested.

**1. Connect provenance to the callback.** Current `refresh: () => Promise<unknown>` / `await refresh()` cannot prove the original authored call is replayed. `result.replayed.push(originalCall)` records a local intention, not callback arguments. The grouping key also omits the stored toolRevisionId.

Define a test-only call tuple `{name, toolRevisionId, arguments}`; include all three fields in the grouping key and map value. Change the callback to `refresh(originalCall)` and actually pass that tuple. In the happy-path fixture, capture/assert the received tuple and invoke the real definition executor using the corresponding original authorized call. The pinned revision is fixture provenance, not a new model-controlled MCP argument. Derive refresh assertions from observed callback invocations; assert exact original name/revision/arguments and one callback for multiple IDs from the same call. Keep controlled response callbacks for mutation fixtures.

**2. Validate original evidence before refreshing.** C18 explicitly says an expired original item cannot be rescued for this pending answer. The helper currently validates only fresh timestamps. Reproduction: original evidence expires at03:01:00; at03:01:02 return identical semantics with a valid digest, evaluatedAt03:01:01 and expiresAt03:01:31. Actual ACCEPT; required REFER, zero deliveries/language writes. Validate every selected provenance item's original digest and time window before issuing refresh; an expired/invalid original returns early. Preserve fresh validation after the await and acceptance of changed fresh timestamps while the original remains valid. Share the time/digest check rather than adding a second partial consumer.

**Acceptance:** the expired-original/valid-fresh fixture refers without refresh or delivery; an unexpired original with valid changed fresh timestamps still accepts. A callback spy receives exactly `{name:'mapped_replay_fixture',toolRevisionId:'revision-1',arguments:{search:'shirt',max:3}}` once for all selected IDs from that call. Keep the 11 focused tests/seven runtime regressions passing and the 12-request budget proof intact. Update the report with measured callback arguments/counts and both time-window outcomes. Run the existing required validation and publish mirrored branches with claims clear; no runtime code churn is requested.

Real deployed MCP/worker/Shopify validation remains developer-owned. No dependent promotion, new claim, main integration or gitlink update. This decision supersedes earlier current-state wording while preserving history. Architecture remains not yet Implemented.


### Changes Requested — Attempt 5 — 2026-09-21

**Current decision: Changes Requested; Ready for the remaining harness/report correction. Attempt 5 retained; executor/claimed_at null. Not accepted.** Verified implementation `caf5d38e8f020d4a9f12ab3faf60eeb8f837d0a4` and report `40ed0a43912b230af5f5de4d472ba71b25fc91e2` against remote task heads. Both dedicated worktrees clean. No new production recommendation defect is alleged; preserve the runtime fixes.

Independent checks: **11/11 focused tests and 7/7 prior runtime reproductions pass**. A temporary copy of the submitted contract test with an exact provider-count assertion confirms **12 actual requests, reservation 13 rejected, typed ERROR** during one top-level execution. **A4-R1.1 is resolved**; do not rework that fixture. Diff check passes. Submitted typecheck/lint/build and full 334/335 remain reported evidence rather than independently rerun full checks.

Two diagnostic assertions in `/tmp/c007-a5-review/review.test.ts` fail in the new `selectedConsumer`: `truncated:true` is ACCEPTED; unchanged evidence semantics with valid refreshed timestamps/recomputed digests is REFERRED because selected original IDs no longer equal refreshed IDs. These are test-double defects, not claims about the production Background consumer.

#### A5-R1 — Complete the one actual replay path; preserve the repaired budget fixture

Scope remains `tests/recommendation-contract.test.ts`, task-owned fixtures and this report. This is unfinished A4-R1.2–4, not new feature scope or a larger coverage target.

**Current problem:** there are now two incomplete consumer functions. The old function assigns `refreshCalls=1`; the new `selectedConsumer` increments a local counter but never calls a refresh transport. The new function checks digests only and ignores truncation/semantic/time/provenance checks in the other function. Passing separate tests against different partial functions does not establish the claimed C18 replay behavior. Its positive case reverses selected IDs, not the refreshed alternative order. Evidence for the matrix is still manually constructed separately from the actual producer fixture.

**Implement this single flow, replacing both helpers:**

1. Extract the existing real producer fixture so the matrix can obtain its reply and original authored call. Register each selected original evidenceId with its evidence and `{name,toolRevisionId,arguments}` provenance. This is test-only state.
2. Give the double an actual async `refresh(originalCall)` callback. Resolve selected original IDs through the provenance map, group identical call tuples, invoke/await the callback once per tuple, and derive refresh count from the callback spy. Unknown IDs/missing provenance must not issue a refresh. Capture and assert exact original name/arguments.
3. Parse the refreshed envelope, reject truncation, then for **each** selected original item require exactly one fresh offerId/canonical-proposal match. Compare required semantic/identity fields, validate its digest and time window, and reject the entire selection if any item fails. Do not search by the old digest: a fresh timestamp legitimately produces a new evidenceId. Only after all selected items validate may delivery/language-write spies run.
4. Run the existing positive/mutation/expiry/denial/deferred-completion rows through this same function. Two selected items in reversed refresh order must accept once; truncated refresh and invalid second item must refer; changed valid timestamps/digests with identical semantics must accept. For expiry/future rows recompute valid hashes so invalid-digest rejection does not mask the time check. Use a deferred callback for cancellation during refresh and assert no delivery/language write when it settles. Do not simulate a callback by incrementing a counter or returning literal side-effect counts.
5. Finish the already-requested local rows currently marked pending and align report claims to executable assertions. In particular, ordinary positive `CommerceToolOutputs.parse` is not a malformed-envelope rejection test, changing an expected grant string is not producer authorization denial, and no executed fixture currently proves the claimed async callback. Add the actual fixture boundary assertions or accurately leave their named claims pending; unfinished required local rows cannot be labeled completed. Keep real deployed MCP/worker/Shopify checks separate and developer-owned.

The repaired provider-budget case and seven runtime regressions should remain passing. No arbitrary test-count target, production-code churn, Background import, schema change or live service is requested. Run the focused checks and required repository validation after the scoped change; publish mirrored branches and return to Review with claims clear.

Readiness: no dependent promotion, new claim, main integration or gitlink update. Architecture is not yet Implemented. This decision supersedes earlier current-state wording while preserving review history.


### Changes Requested — Attempt 4 — 2026-09-21

**Current decision: Changes Requested; Ready for the remaining harness/report correction. Attempt 4 retained; executor/claimed_at null. Not accepted.** Verified implementation `91faf18e8163b8b4bba231fbb6b2a30477d2aeb8` (including `89780156`) and report `cb8f7f3d010cae05bc0ccfa9c41f3939c8bad356` against remote task heads. Both dedicated worktrees were clean. No implementation edit, new claim, dependent promotion, main merge or gitlink update.

Independent validation: **11/11 submitted focused tests and 7/7 prior runtime reproductions pass**. The earlier runtime corrections remain verified; this review alleges no new production recommendation defect. Diff check passes. Submitted typecheck/lint/build and full 311/312 remain reported evidence. Two diagnostic assertions against an isolated copy of the submitted harness (`/tmp/c007-a4-review/review.test.ts`) expose the incomplete proof: its exhaustion case performs zero actual provider requests, and its consumer accepts two selected IDs even though the second selected evidence has an invalid digest. These are defects in the test harness, not demonstrated production-consumer defects.

#### A4-R1 — Finish A3-R1's existing executable proof and correct the report

Scope remains `tests/recommendation-contract.test.ts`, task-owned fixtures and this Completion Report. Preserve working runtime code. No additional coverage target, live service or Background implementation is requested.

1. **Replace the counter preload with real nested work.** At line29 the budget sets reservations to12 before incrementing on its first request. Thus the exhaustion scenario rejects search immediately, with providerCalls0; `<=12` passes without exercising nested calls. Remove that preload and start each scenario at0. Use one top-level execute, several valid candidates (for example six), and the same budget object across search, rule reads and product facts. Let each actual fixture provider request reserve once; provide a valid response for the rule path instead of its current unexpected-operation throw. One search plus repeated rule/fact reads can reach12 and deny reservation13 naturally. Assert providerCalls===12, reservations===13, typed ERROR and zero transport after denial. Do not loop top-level execute or add an artificial11-request rule loop. Keep the separate exhausted-before-start test if useful, labeled correctly.

2. **Make the consumer double actually replay and inspect every selected item.** It currently assigns `refreshCalls=1` without calling any transport, accepts only one `expectedProposal`, and can accept selected IDs `[validFirst, invalidSecond]` after checking just the first. The second baseline evidence still has a fabricated `'b'.repeat(64)` digest. Extract the real producer fixture, generate both alternatives through it, and retain a provenance map keyed by original evidenceId with the authored call/revision/arguments. Pass an actual async refresh callback/spies into the test-only double; replay once per original call tuple and count invocations. For each selected original ID, require exactly one fresh offer/proposal match and validate its shape/digest/semantics/time; reject if any item fails. Do not require a fresh digest to equal the old digest, since timestamps may legitimately change. Test two selected valid alternatives with reversed refresh ordering, then a bad second item, plus changed valid timestamps/digest with unchanged semantics. Capture exact original name/arguments and assert no separately discovered evaluator call.

3. **Remove invalid-fixture and constant-counter shortcuts from the existing negative cases.** Expiry/future rows currently change timestamps without recomputing the digest, so digest failure masks whether time checks work. Recompute valid digests for those rows and use an independent positive control; only the intentional invalid-digest case should have a bad hash. Feed malformed envelopes through runtime Shared parsing. Invoke a deferred refresh callback before injecting cancellation/new inbound/lease loss, then assert delivery/language-write spies remain unused; the current `cancel:true` early return and literal counters do not prove stale completion handling. Producer denial must run through the fixture authorization boundary with provider count0; changing an expected grant string is not producer revocation. Preserve A3-R1's named EC rows, including original-provenance/unknown-ID zero-call checks and actual configured-limit clamping with enough candidates to observe the limit.

4. **Make report claims correspond to executed assertions.** The current report claims malformed-shape, imitation, producer-denial and configured-limit coverage absent from this file. It also claims two alternatives were accepted although only the first is selected in the positive case, and retains the stale “8 focused tests total” entry. Record exact EC row names, commands and observed callback/provider/delivery counts; mark any unimplemented row pending instead of passed. Keep typecheck/lint/build as actually executed after the correction. Passing the current 11 tests is not proof of behavior they never exercise.

Acceptance remains the bounded local C18 contract work already specified in A3-R1, with the existing runtime regressions preserved. Use test-only consumer code or an approved executed fixture; do not import or modify Background. Real deployed MCP/worker/Shopify validation stays developer-owned. Return to Review with mirrored branches pushed and claims clear; do not self-accept or start dependent tasks.


### Changes Requested — Attempt 3 — 2026-09-21

**Current decision: Changes Requested; Ready for a tests/report correction. Attempt 3 retained; executor/claimed_at null. Not accepted.** Verified implementation `bad71ef55e5942e74343c35b611c5177f0852a20` and final claim-cleared report `f8f59289e81cea193d16011b5af695e99b2f6b3c` (preceding report `aa87bb82`) against remote task heads. Both dedicated worktrees clean; database pin `5abfd87f57038bae515aaa09ec7c8db62adcfb98` unchanged.

Independent checks: **11/11 submitted focused tests pass**, and **7/7 prior architect reproductions pass** in `/tmp/c007-a2-review`. A2-R1 replacement pricing and A2-R2 post-await/publication cancellation guards are verified. Preserve those runtime fixes. Diff check passed. Lint/build/typecheck and full310 passes/two baseline failures remain submitted evidence; no live validation was run. No runtime defect is newly alleged by this decision. No dependent promotion, claim, main merge or gitlink update.

#### A3-R1 — P1 — Complete the claimed local contract assertions, not just the report matrix

Remaining scope is **A2-R3**, in `tests/recommendation-contract.test.ts`, task-owned test fixtures and this Completion Report. Do not change production recommendation code merely to manufacture a new runtime fix; production changes are needed only if the completed harness exposes a real defect.

**Observed evidence gaps:** the file has two tests. The first still changes basket price and rule fingerprint together, uses one alternative, then exhausts a shared counter by repeatedly executing the top-level tool. The second defines `exactMatch` locally: it checks proposal uniqueness plus three IDs only. It never reads `truncated`, expiry, digest, outcome, turn or semantic changes; its baseline evidenceId is `'a'.repeat(64)`, not a computed valid digest. There are no refresh/delivery/language-write counters. Consequently the report's EC03/05 two-alternative/truncated assertions, EC04 independent-field rejection and EC06/07/08/10 expiry/imitation/revocation claims are not established. Matching a fixture's expiry string or asserting a valid grant equals itself is not a rejection test.

**Implement this exact bounded test structure:**

1. Keep the working real evaluator/definition-executor fixture. Extract setup so each scenario has a fresh context/budget and returns the actual producer reply, original authorized call, provider spy and consumer-double counters. Use the canonical C18 seed/identities and actual generated evidence where applicable. Generate evidenceId from canonicalJson of every evidence field except evidenceId; recompute it after each semantic mutation, except the deliberately invalid-digest case.
2. Replace `exactMatch` with a test-only consumer double implementing the C18 admission/replay checks. It takes original call/provenance, selected evidence IDs, a refresh transport, current turn/clock/cancellation state and exposes `{decision, refreshCalls, deliveries, languageWrites}`. It replays the original name/arguments once per originating call, validates fresh evidence and matches exact proposal identity, never array position. Do not import Background or add consumer logic to Commerce production. Reuse an existing approved contract fixture instead if it implements these checks and is executed by the recorded command.
3. Add named/table-driven rows for the following existing matrix. Every negative row must first demonstrate its unmodified positive control succeeds, then change only the named condition, so unrelated invalid fixture data cannot mask a failure:

| Cases | Required assertions |
| --- | --- |
| EC01/02/12 | Actual arbitrary mapped call is captured/replayed once, exact original arguments preserved, identical proposal accepted, changed proposal refers, zero separately discovered/ungranted calls. |
| EC03/05 | Two generated alternatives with selected IDs from one call cause exactly one refresh; reverse result order and still match; separate duplicate/missing/empty/truncated cases refer with deliveries0. |
| EC04 | Separate basketFingerprint, ruleFingerprint, savings, resultingTotal, currency, outcome and proposal mutations, with recomputed valid digest, each refer; no simultaneous basket+rule mutation used as proof of individual rejection. |
| EC06/07 | Separate expiry boundary, future timestamp, invalid digest and malformed-shape cases reject; rendered/public-query imitation registers zero evidence IDs and causes zero refresh. |
| EC08/10 | Wrong shop/grant/release/version or revoked producer denies through the producer authorization boundary before provider work; consumer wrong turn/missing provenance/unknown ID/exhausted refresh budget fails closed with asserted zero calls where required. |
| EC09/11 | Typed/HTTP/transport failures do not retry refresh; cancellation/new inbound/lease-loss injected while refresh is pending cause deliveries0 and languageWrites0. These are consumer-double assertions only. |

4. Correct the budget fixture to exercise **one top-level remote tool execution** with a fresh12-request budget, enough admitted candidates and nested rule/fact requests to exhaust it. Assert each nested path shares that counter, reservation attempt13 issues no transport request, total actual requests<=12, and typed failure is returned rather than complete evidence. The current loop sharing one budget across many separate execute calls proves the counter throws, but not the requested nested per-call path. Retain it if useful, but do not label it that proof. Add a dispatch fixture with deliberately lower configured limits and enough candidates to observe the clamp; the current single-candidate call with maxRecommendations3 does not test limit enforcement.
5. Replace each report matrix claim with EC ID -> named test/table row -> command -> observed refresh/provider/reservation/delivery counts. If a case is not implemented, mark it pending rather than passed. Correct the stale “8 focused tests total” entry and distinguish a current typecheck run from a pre-attempt result/build TypeScript phase. Record actual checks after the tests change.

Acceptance requires the named local contract assertions above and all existing11 focused tests/seven architect regressions remaining passing. No arbitrary minimum test count is imposed; table-driven tests are fine. Run the focused suite and required repository validation, commit/push mirrored branches and return to review with claim clear. Real deployed MCP/worker/Shopify validation remains developer-owned and is not demanded here. No new feature scope, provider calls, schema or Shared publication is requested.

### Changes Requested — Attempt 2 — 2026-09-21

**Current decision: Changes Requested; Ready for corrections. Attempt 2 retained; executor/claimed_at null. Not accepted.** Reviewed implementation `dd86f4403c3dfed9ad33b16098e198a34545ed0d` and report `5f5fbed402569299765a10013a2a84df895f54a0`, verified against remote task heads. Both dedicated worktrees were clean; database pin remains `5abfd87f57038bae515aaa09ec7c8db62adcfb98`. No code edits, new claim, main integration, gitlink change or dependent promotion.

Independent validation: submitted recommendation/contract tests **8/8 passed**. The five original functional reproductions now pass (cheapest ADD admission, deduplication, typed DENIED, cross-currency exclusion, unknown replacement quantity). The isolated `/tmp/c007-a2-review/review.test.ts` contains those five plus two new checks: **5 passed, 2 failed**. The failures are replacement admission ordering and final-await cancellation. The former uses the actual evaluator with controlled facts; the latter uses a deterministic evaluator port that aborts the shared signal immediately before returning valid evidence. Diff check passed. Typecheck/lint/build and full308/309 are submitted evidence; Redis timeout is not a review blocker. A discarded unknown-savings probe supplied evidence forbidden by Shared and is not counted as a functional finding.

Retain the corrected ADD ordering/deduplication, typed evaluator error propagation, currency/quantity exclusions, arbitrary mapped definition fixture and canonical evidence digest check. Complete the following remaining portions of A1-R1/R2/R4, without changing scope or implementing Background.

#### A2-R1 — P1 — Use REPLACE cost for replacement admission

File: `src/commerce/products/recommendations.ts`, `similar` preparedCandidates sorting and final pricing; tests in `tests/recommendations.test.ts`.

The admission sort calls `proposedTotal(basket, product)`, which computes an ADD of one item. A REPLACE has different extra spend: `max(0, candidateUnitPrice * sourceQuantity - sourceUnitPrice * sourceQuantity)`. With a USD20 source and quantity1, ten `z-cheap-*` candidates priced1 and `a-equal-extra` priced19 all have extraSpend0. C8 therefore admits `a-equal-extra` first by variantId; current code treats its extraSpend as19 and excludes it before the10-evaluation cap.

Extract one replacement-pricing helper and call it both when constructing preparedCandidates and when building final alternatives. Using existing decimal/money helpers, its known-value calculation is:

```ts
const removed = decimal(sourceLine.unitPrice) * BigInt(sourceLine.quantity);
const added = decimal(product.unitPrice) * BigInt(sourceLine.quantity);
const delta = added - removed;
return {
  extraSpend: money(delta > 0n ? delta : 0n),
  resultingTotal: money(decimal(original.total) + delta),
  currency: original.currency,
};
```

Apply this only after checking known basket total, source unit price/quantity and candidate unit price with matching currency; otherwise return unknown pricing. Carry that computed pricing with each candidate. Deduplicate canonical proposals, sort by its actual extraSpend (unknown last), variantId and canonical proposal JSON, then slice10. Preserve the separate final similarity ranking and max3 output.

Acceptance: the11-candidate example above admits `a-equal-extra` and exactly10 proposals; permutations preserve admitted IDs/order. Include a source quantity3 case and known/unknown pricing; final disclosed totals must equal the same helper's values. Do not merely sort the already-admitted results.

#### A2-R2 — P1 — Recheck cancellation/deadline after awaits and before every successful return

File: `src/commerce/products/recommendations.ts`, `evaluate`, `qualifying`, `similar`; focused tests.

The wrapper checks `stopped(context)` only before evaluator dispatch. If the shared signal becomes aborted while the last admitted evaluation completes, it publishes `status: OK` with alternatives. The same publication guard is absent on no-evaluator similarity and empty/no-source early success paths. Typed errors now propagate correctly, but this requested post-completion guard is still missing.

Add the existing typed guard immediately after awaited dependencies and before producing success, including early empty results:

```ts
if (stopped(context)) return failure('DEADLINE', true);
```

Inside the discriminated evaluation helper use `{ error: failure('DEADLINE', true) }` after its await. Preserve the shared context/budget/signal/deadline object and existing typed non-cancellation errors; do not add retries or a new grant. Stop before another evaluation/provider call after cancellation or deadline expiry. This is a Commerce result-publication guard, not Background delivery logic.

Acceptance: abort inside the last evaluator completion -> DEADLINE, no successful alternatives; repeat with an expired fake-clock deadline, after an earlier qualified candidate, and with similar offerId:null while search is pending. A valid nonqualifying evaluation remains an OK empty result when not stopped. Assert subsequent call count0 after the stop.

#### A2-R3 — P1 — Finish the local C18 and provider-budget evidence; correct report claims

Files: `tests/recommendation-contract.test.ts`, task-owned contract fixtures and this Completion Report. The new real evaluator/definition executor fixture is useful, but it contains a single happy replay and changes basket/rule together. Its budget is `reserveProviderRequest() {}` and it only asserts providerCalls >0. There is no consumer double or EC01–EC12 case matrix in executable coverage. Existing eight tests therefore do not establish the report's “EC01–EC12 ... passed locally” or shared12-request ceiling claims. This is the remaining explicitly requested A1-R4 validation, not a new live-service requirement.

Use the canonical C18 seed and controlled provider transport, preserving actual evaluator/definition executor dispatch. Add a local consumer double (no Background import) and map each EC ID to executable assertions, or to an exact reused fixture that is actually run:

- EC01/02/12: capture the original arbitrary tool name/arguments, replay that same call once, retain mapped inputs, forbid separate ungranted evaluator discovery; identical proposal passes and changed proposal refers.
- EC03/05: two alternatives from one call need one refresh; match by exact proposal, not array position; absent/duplicate matches, empty and truncated replies cannot yield positive acceptance.
- EC04: vary basket hash, rule hash, savings, total, currency, outcome and proposal separately with recomputed canonical digests, so unrelated mismatches cannot mask the asserted condition.
- EC06/07/08/10: expiry/future/malformed/digest cases, imitation evidence, provenance/turn/budget failures and revoked/wrong identities fail closed. Producer authorization fixtures assert zero provider calls for denials; host provenance checks belong only in the consumer double.
- EC09/11: typed/transport failures get zero automatic refresh retries; cancellation/stale completion makes the double's delivery/language-write counts0. Do not implement host races in Commerce runtime.

Replace the no-op budget in a dedicated actual-adapter fixture with a shared counter that throws before reservation13. Observe provider transport invocation count <=12 across search plus nested facts/rule evaluation, with no subsequent call after exhaustion; ensure output fails closed rather than claiming complete evidence. A10-evaluation spy is not a12-provider-call check. Keep the existing success/digest fixture, and test configured maxRecommendations/maxSearchResults through the dispatcher without expanding original authority.

Update the report to list EC ID -> test/fixture -> command -> actual call/reservation/consumer counts and outcome. Remove the claim that the task-owned local renamed-call/tampered-evidence path is wholly developer-owned. Real deployed MCP/worker/Shopify validation remains separate and pending, as intended. Run focused tests, required lint/typecheck/build/diff checks after corrections and publish both task branches. Return to review, clear claims, and do not self-accept or start dependants.

### Changes Requested — Attempt 1 — 2026-09-21

**Current decision: Changes Requested; Ready for corrections. Attempt 1 retained; executor/claimed_at null. Not accepted.** Reviewed implementation `6821a49c5d8568227ff81085f0398c934df58332` and parent report `a67becf02f1332aad3783597c5d0bfe862c9d80c`, matching their remote task heads. Both dedicated worktrees were clean. Database remains `5abfd87f57038bae515aaa09ec7c8db62adcfb98`. No implementation changes, new claim, dependency promotion, main integration or gitlink update.

Independent validation: submitted recommendation tests **6/6 passed** and diff checks passed. The isolated `/tmp/c007-a1-review/review.test.ts` harness imports the actual recommendation operations and accepted discount evaluation adapter, with local basket/rule/product fixtures. It reproduces **five functional failures**: cheapest eleventh candidate omitted, duplicate proposals returned, DENIED converted to OK, cross-currency replacement emitted, and unknown quantity replaced with1. The authorization-failure case injects a typed evaluator failure; the other cases use the actual evaluator where evaluation is requested. Submitted typecheck/lint/build passes and full306/307 remain reported evidence, not independent architect reruns. The Redis discovery timeout is not the reason for this decision.

Retain the existing operation descriptors, Shared output schemas, exact decimal calculations, evaluator reuse, known availability filtering and turn/basket/proposal comparisons. The corrections below are scoped to functionality, not an expanded coverage target.

#### A1-R1 — P1 — Deduplicate and order proposals before applying the evaluation cap

Files: `src/commerce/products/recommendations.ts`, focused recommendation tests. Binding contract: C8 deterministic proposal admission and ranking.

**Observed:** `qualifying` and `similar` evaluate candidates in provider order, then sort only the retained alternatives. With ten eligible USD candidates priced20 through29 followed by an eligible USD1 candidate, the actual evaluator returns `costly-0` first; `cheapest` is never evaluated. Repeating the same candidate three times produces three identical ADD alternatives and consumes three evaluations. Besides poor suggestions, duplicate proposal matches break C18's exactly-one-match refresh requirement.

**Correct exactly:** construct valid ADD/REPLACE proposals across the bounded search set before evaluation; deduplicate by Shared canonical proposal JSON, retaining operation order. Compute known extra spend, order proposals by extraSpend ascending (unknown after known), variantId ascending, then canonical proposal JSON ascending. Only then admit at most10 unique proposals to the evaluator. Apply the specified final qualifying and similarity rankings after evaluation, including canonical proposal tie-breaks. For qualifying savings, ensure unknown sorts after known even with descending comparison. Mark truncation whenever bounded search, unique proposal admission or output limit omits candidates; preserve max3 and the existing effective configured limit from dispatch.

**Acceptance:** the11-candidate fixture evaluates `cheapest` and ranks it first with ten evaluations total; permutations of that candidate set produce the same admitted proposals and result order. Three identical candidates produce one proposal, one evaluation and one alternative. Apply the same admission/deduplication rule to similar replacements. Assert proposal IDs/call counts; do not merely sort the final three values in a test.

#### A1-R2 — P1 — Preserve typed evaluator failures and incomplete evaluation

Files: `src/commerce/products/recommendations.ts`, focused recommendation/adapter tests. Binding contracts: C8 shared budget and C18 fail-closed exact refresh.

**Observed:** the local `evaluate` wrapper converts every evaluator ERROR into null. An evaluator response `{status:'ERROR',code:'DENIED',retryable:false}` becomes `{status:'OK',data:{alternatives:[],truncated:false}}`. The same conversion applies to DEADLINE, THROTTLED and UNAVAILABLE. After earlier candidates succeeded, a later failure can leave apparent complete successful recommendations. `stopped(context)` also returns null, obscuring exhaustion.

**Correct exactly:** return a discriminated evaluation result, preserving typed failure separately from an OK nonqualifying/UNKNOWN evidence outcome. Stop on authorization, cancellation/deadline and provider failures and return the corresponding typed error; do not downgrade them to a complete successful search. Keep the same shared budget object/deadline through search, rule reads and product facts, and issue no provider request13. Check cancellation/deadline before each admitted evaluation and before publishing output. If an intentionally partial search result is returned, it must be explicitly truncated and cannot count as successful complete evidence refresh. Never expand a grant or retry the final refresh automatically.

**Acceptance:** injected DENIED remains DENIED, and DEADLINE/THROTTLED remain typed failures even after an earlier candidate qualified; no subsequent candidate evaluation follows the failure. A controlled real-adapter fixture with a shared12-request counter records at most12 actual provider requests and fails closed on exhaustion. Distinguish an OK `DOES_NOT_QUALIFY` (legitimate no match) from transport/authorization failure.

#### A1-R3 — P2 — Construct only supported same-currency replacement proposals

Files: `src/commerce/products/recommendations.ts`, focused similar-product tests. Binding contracts: C4 explicit proposal quantities and C8 same-currency search/recommendations.

**Observed:** `similar` lacks the known-currency mismatch filter present in `qualifying`. A USD basket produces a EUR replacement alternative, with null monetary totals rather than excluding the mismatch. Separately, `quantity: sourceLine.quantity ?? 1` turns an unknown basket quantity into a concrete replacement quantity1. The actual evaluator marks that proposal UNKNOWN, but the returned alternative still proposes the invented quantity.

**Correct exactly:** exclude known currency mismatches before constructing or evaluating replacements. Missing currency remains unknown and must not be treated as confirmed matching currency. Require a known valid quantity for the selected basket line; when it is missing, do not construct a REPLACE operation with a default. Return no replacement for that line until facts are available, preserving null/unknown facts without inventing them. Remove exactly the selected line, and forward its explicit known quantity unchanged. Preserve separation between similarity reasons and discount qualification.

**Acceptance:** a USD basket plus EUR candidate produces zero replacement alternatives and zero evaluations for that candidate. A source quantity null produces no fabricated proposal/evaluation; source quantity3 produces a REPLACE for the exact line with quantity3 and appropriate totals. No new input field or Shared version is needed.

#### A1-R4 — Complete the local producer contract evidence and examples

Files: task-owned fixtures/tests and recommendation example definitions/templates; update this Completion Report. Do not modify Background, database schemas or production integration to satisfy this item.

The task explicitly assigns the local C18 producer/consumer contract harness to007; the report cannot move the local MCP/renamed-call/tampered-evidence fixture path wholesale to developer-owned validation. Current six tests use a mocked evaluator with constant fabricated evidence hashes and do not demonstrate actual evidence generation, dispatch preservation or exact replay. C18 separates this local responsibility from SYSTEM-TEST-001's real worker integration.

Use the accepted evaluator and definition executor/dispatch ports with controlled provider transport, actual canonical digests, a fixed clock and an arbitrary authored tool name with mapped inputs. Include the requested example tool definitions/templates as executable fixtures (or identify existing exact examples that satisfy this). Record the existing EC01–EC12 matrix with007's relevant producer effects and explicitly identify host-only expectations as consumer-double assertions, not Commerce host code. Demonstrate exact original-call replay, unchanged evidence semantics, changed basket/rule semantics, duplicate/ambiguous alternatives, and the shared provider ceiling. Existing accepted consumer fixtures may be reused; no new exhaustive test program or live services are requested.

Update the requirement-to-fixture matrix with actual commands and expected/observed calls/results. Keep real Shopify, deployed MCP and Background/system integration pending developer-owned validation. These external checks are not prerequisites for completing the local functional corrections above. Return to Review after the scoped implementation/report changes are pushed; do not self-accept or start enabled tasks.


### Original definition review placeholder (historical)

### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.


## Architect readiness reconciliation — 2026-09-21

COMMERCE-016 Attempt2 is architect-accepted at implementation55204ec24b2508c38c064aadfd1dd81bef768e4a; COMMERCE-015 is Complete. Both explicit prerequisites are satisfied. Promoted to Ready on the016 acceptance branch, preserving attempt0 and null executor/claimed_at. Normal preparation owns synchronization and claim; no automatic execution.
