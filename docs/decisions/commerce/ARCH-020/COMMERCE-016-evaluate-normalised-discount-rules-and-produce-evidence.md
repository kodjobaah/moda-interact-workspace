---
id: ARCH-020-COMMERCE-016
architecture_id: ARCH-020
title: Evaluate normalised discount rules and produce evidence
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 105
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-006
  - ARCH-020-COMMERCE-015
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-007
  - ARCH-020-COMMERCE-013
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-21
updated: 2026-09-21
---

# Evaluate normalised discount rules and produce evidence

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own deterministic eligibility/savings evaluation and discounts.evaluate adapter using006 normalized rules and015 basket/product facts.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own deterministic eligibility/savings evaluation and discounts.evaluate adapter using006 normalized rules and015 basket/product facts.

## Out of Scope

Other C19 owners' modules; new Shared wire versions or database schema; live
deployment/provider calls; unrelated refactors; cart/order writes or WhatsApp sends.
Do not implement missing dependencies or substitute production fixtures to finish.

## Requirements

Use accepted auth/Shared/database source, canonical types and C19 ports. Preserve
others' changes. Exact business names remain database-authored. Fixtures are injected
only by tests; production missing adapters fail closed. Each case below has an
expected side effect, not just a screenshot/typecheck. C19 assigns final wiring.

## Work Items

- [x] Implement the pure C19 evaluator with injected now and exact decimal/currency metadata; no network/DB access inside arithmetic.
- [x] Apply C8 condition precedence, startsAt<=now<endsAt, native supported rule scope, minimum bases/allocation/rounding only where006 evidence proves semantics.
- [x] Implement discounts.evaluate orchestration: re-read current policy/rule, load exact basket/proposal facts, enforce NONE/FIXED and caller ownership, and share request budget across adapters.
- [x] Generate C4/C18 Evidence/digest/fingerprints/lifetime for exact proposal; UNKNOWN/UNSUPPORTED/unresolved never qualifies. No checkout guarantee or mutation.
- [x] Export evaluator for007 and operation adapter for013 registration. Accept rule-reader/product fixtures plus actual pure evaluator tests;013 verifies real reader/provider composition.

## Interfaces / Contracts

Own `src/commerce/discounts/evaluator/`.006 owns DiscountRuleSnapshot/provider semantics;015 owns basket/current facts;007 owns recommendations.013 owns their real registration/composition.


## Dependencies

- ARCH-020-COMMERCE-006
- ARCH-020-COMMERCE-015
- ARCH-020-SHARED-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-007
- ARCH-020-COMMERCE-013
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [x] V01: percentage/fixed rule matrix includes quantity/subtotal boundaries, product/variant/collection scope and exact decimal rounding/allocation; expected money is explicitly calculated in fixtures.
- [x] V02: time/disabled/failure -> nonqualification precedes unsupported/missing facts; unknown semantics and customer/usage restrictions never qualify.
- [x] V03: wrong currency, absent variants, partial memberships and stale/changed rules fail closed; exact proposal operation order and fingerprints are preserved.
- [x] V04: canonical C18 seed parses; producer evidence lifetime/digest, renamed evaluator, NONE/FIXED and revoked policy cases have zero unauthorized reads.
- [x] V05: re-evaluation of changed basket/rule produces changed semantic evidence; provider ceiling includes all nested reads; pure arithmetic makes zero I/O calls.

## Validation

Implement the named cases above as focused tests. Record case -> fixture -> command
-> expected/actual effects in the Completion Report. Check shared contract examples
where applicable; include malformed and denied inputs with zero side effects.
Run focused tests while developing, then typecheck/lint/build once before submission;
repeat broader checks only for new failures or changed concerns. Use actual repository
commands and record them. Local browser/component evidence is task-owned where a UI
is in scope. Follow agent-validation/live-validation policies; separate pending
required developer database/container evidence and never claim fixture tests prove
live service behavior. No minimum screenshot/test count substitutes for coverage.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; consume the accepted COMMERCE-001 foundation.

## Completion Report

### Status

Ready for Review.

### Files Changed

- Implementation commit `bfbd7839503b60e88b17da49f258c84c4e506c76`:
  - `src/commerce/discounts/evaluator/types.ts`
  - `src/commerce/discounts/evaluator/evaluator.ts`
  - `src/commerce/discounts/evaluator/adapter.ts`
  - `src/commerce/discounts/evaluator/index.ts`
  - `tests/discount-evaluator.test.ts`

### Work Completed

- Added the pure `evaluateDiscount` C19 function. It accepts only validated basket,
  proposal, normalized rule, current variant facts, identities and an injected UTC
  time; it performs no database, network or clock lookup.
- Implemented exact decimal arithmetic with `BigInt`, canonical currency minor-unit
  metadata, HALF_UP/HALF_EVEN/DOWN rounding, LINE/TOTAL rounding points and
  ACROSS_ELIGIBLE_LINES/PER_ELIGIBLE_ITEM allocation.
- Applied the C8 precedence chain: disabled/not-started/expired and every provable
  target/proposal/minimum failure return DOES_NOT_QUALIFY before unsupported rule
  semantics; unsupported precedes incomplete rule, currency and membership facts.
- Evaluated ALL/PRODUCT/VARIANT/COLLECTION targets, basket/eligible quantity and
  subtotal minima, ordered ADD/REPLACE proposals, current availability and exact
  currency. Missing variants, partial collection membership and contradictions fail
  closed without a qualifying result.
- Produced Shared `CommerceEvidence` with the original proposal order, basket/rule
  fingerprints, positive lifetime capped at60 seconds and offer expiry, and a
  lowercase SHA-256 digest over canonical C4 JSON excluding `evidenceId`.
- Added the immutable `discounts.evaluate` version1.0.0 adapter for013. It validates
  Shared input, re-reads the authorized current rule first, then basket and product
  facts with the same context/budget, propagates typed failures and performs no later
  reads after DENIED/NONE/wrong-FIXED/revoked or malformed input.

### Validation Results

Agent-executed:

- `npm test -- tests/discount-evaluator.test.ts tests/discount-reader.test.ts tests/products-policy.test.ts`:
  PASS,3 files /50 tests.
- `npm run lint`: PASS, zero warnings/errors.
- `npm run typecheck`: PASS.
- `npm run build`: PASS; Prisma client generation and Next.js production build completed.
- `git diff --check`: PASS.
- `npm test`:253 passed,4 failed outside the changed evaluator/reader/product paths.
  Existing infrastructure-sensitive failures were two descendant-process timing cases
  in `readiness-docker.test.ts`, the live Shopify developer-MCP request timeout in
  `discovery-process.test.ts`, and the configured Redis discovery-limit timeout in
  `discovery-limits.test.ts`. The focused evaluator dependency matrix passed.

Case/effect matrix:

- V01: percentage10 over USD100 produced savings10.00/result90.00; fixed5 produced
  5.00/95.00; exact/below subtotal and quantity bounds, all target kinds, USD/JPY,
  half-up/even/down and per-item allocation assert exact money and outcomes.
- V02: exact start qualifies, exact end/disabled/minimum/target failure does not;
  known failure wins over an unsupported family, while unsupported wins over unknown
  customer/current facts. No unresolved result qualifies.
- V03: wrong currencies, missing variants, unavailable proposal variants and partial
  collections fail closed; ADD/REPLACE order is unchanged in evidence and basket/rule
  changes produce distinct evidence IDs.
- V04: the canonical C18 seed parses and its published digest recomputes exactly;
  generated evidence validates against Shared, has a60-second ceiling, and the exact
  `discounts.evaluate` operation is exported. Malformed and three denied policy cases
  perform zero basket/product reads.
- V05: adapter fixtures prove one shared budget object across rule, basket and nested
  product ports; the accepted015 suite proves its12-request nested ceiling. The pure
  function has value-only inputs and no I/O dependency. Typed deadline/provider
  failures stop without fallback or later reads.

Developer/integration validation remains for013's production composition with real
006/015 readers and provider configuration. No live Shopify, database mutation,
cart/order write, model or WhatsApp operation was run or claimed.

### Deviations

None.

### Assumptions

- Existing basket snapshot prices are evaluated as the exact C18 basket snapshot;
  current015 facts establish variant identity, availability, proposal price/currency
  and collection membership. Evidence remains a snapshot claim, never a checkout guarantee.
- Accepted database submodule revision: `5abfd87f57038bae515aaa09ec7c8db62adcfb98`.

### Unresolved Issues

Production adapter assembly and live provider evidence remain owned by013 and the
terminal system test. The four broader-suite infrastructure failures above are not
caused by or located in this task's changed paths.

### Architectural Concerns

None newly reported.

### Git / VCS

- Task branch: `task/ARCH-020-COMMERCE-016` in both repositories.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-016`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-016`.
- Shared workspace/implementation checkout switched or mutated: no. Another task
  worktree reused: no.
- Start synchronization: parent and implementation remote task fast-forward not
  needed; both already contained current `origin/main` at launcher preparation.
- Recursive submodule sync/update: passed. Database pin:
  `5abfd87f57038bae515aaa09ec7c8db62adcfb98`.
- Implementation commit `bfbd7839503b60e88b17da49f258c84c4e506c76` pushed to
  `origin/task/ARCH-020-COMMERCE-016`.
- No main merge/push, force push, parent gitlink update or unrelated parent file edit.

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


### Architect readiness promotion — 2026-09-21

Ready, unclaimed, attempt0. Prerequisites006 (accepted Attempt4, implementation
1c124f4b53a494425735a8064ac20a2e2000914e),015 (accepted Attempt3, implementation
511e14ad25fb5f34882102e324b246a601ca9053) and SHARED-001 are Complete in main.
006's accidentally blank task ID is restored without changing its acceptance.
No implementation scope change, task claim or automatic execution. Launcher must
consume accepted prerequisite source through normal preparation/synchronization.
