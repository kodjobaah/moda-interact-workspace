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
status: ready
priority: 110
executor: null
claimed_at: null
attempt: 1
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
- `src/commerce/products/index.ts`
- `src/commerce/products/recommendations.ts`
- `tests/recommendations.test.ts`

### Work Completed

Implemented the qualifying and similar-product policy operations, deterministic ranking, bounded evaluator processing, currency-safe totals, unavailable-variant filtering, and exact C4 evidence provenance checks. Existing recovery and public product-search operations remain available.

#### Correction checklist

- No separate Architect Review `Changes Requested` items were present; the latest review remained `Pending` with no implementation submitted.
- C18 shared recommendation outputs and operation descriptors: implemented and wired.
- C4 exact-call evidence identity for offer, turn, current basket fingerprint, and exact proposal: implemented.
- C8 deterministic ranking, max-three output, currency/extra-spend disclosure, and evaluator bound: implemented.
- Qualifying/similar separation and unavailable/cross-currency filtering: implemented.

### Validation Results

Focused: `npm test -- --run tests/recommendations.test.ts` -> 6 passed, 0 failed.
Typecheck: `npm run typecheck` -> passed.
Lint: `npm run lint` -> passed with 0 warnings/errors.
Build: `npm run build` -> passed; Prisma client generation and Next.js production build completed.
Full tests: `npm test` -> 36 test files, 306 passed and 1 failed. The unrelated baseline failure is `tests/discovery-limits.test.ts`, which timed out after 30 seconds in the Redis-backed sequential discovery-limit test; no recommendation tests failed.
Whitespace: `git diff --check` -> passed.

#### Requirement-to-fixture matrix

| Requirement | Fixture/check | Expected side effect | Result |
|---|---|---|---|
| Same inputs produce ordered max-three results | ranking/cap test | stable order and truncation | passed |
| No match or unsupported qualification | nonqualifying-evidence test | empty alternatives, no invented savings | passed |
| Missing attributes and unavailable variant | similarity fixture | exclude unknown type/unavailable product | passed |
| Higher-spend proposal disclosure | ranking fixture | disclose exact extra spend and resulting total | passed |
| Wrong currency | currency-bound fixture | skip known EUR candidate for USD basket | passed |
| Provider/evaluator ceiling | 11-candidate fixture | evaluate at most 10 and mark truncated | passed |
| Changed basket/turn/proposal evidence | provenance fixtures | reject stale or mismatched evidence | passed |
| Similarity versus qualification separation | similarity fixture | no qualifying label without separate evidence | passed |

### Deviations

The full-suite Redis-backed discovery timeout remains unrelated to the changed files and recommendation path. No live MCP, deployment, or system-test validation was launched.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Developer-owned live/system validation remains pending, including the local MCP sequence and tampered-evidence integration path required by the task validation section.

### Architectural Concerns

None newly reported.

### Git / VCS

Task branch: `task/ARCH-020-COMMERCE-007`, attempt 1; claim cleared for review.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-007`, branch `task/ARCH-020-COMMERCE-007`, claim revision `98b876779783fdc49127d182aa73295ea6d8c8bd`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-007`, branch `task/ARCH-020-COMMERCE-007`, final commit `6821a49` (`feat(commerce): recommend qualifying and similar products`), pushed to `origin/task/ARCH-020-COMMERCE-007`.
- Recursive database submodule evidence: `5abfd87f57038bae515aaa09ec7c8db62adcfb98` (`database`, `heads/main`).
- No parent service gitlink, main branch integration, or other repository changes were performed.

## Architect Review

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
