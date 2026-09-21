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
