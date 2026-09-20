---
id: ARCH-020-BACKGROUND-002
architecture_id: ARCH-020
title: Preserve turn safeguards and validate offer replies
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 160
executor: copilot
claimed_at: 2026-09-20T23:41:29Z
attempt: 2
depends_on:
  - ARCH-020-BACKGROUND-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-002
created: 2026-09-20
updated: 2026-09-20
---

# Preserve turn safeguards and validate offer replies

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Keep MCP-backed replies within existing conversation, permission and outbound safety boundaries.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Background turn processor/result validation, live permission recheck and offer-evidence integration tests.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

### Independent implementation contract

Binding **C18** in the implementation contracts is the single producer/consumer
specification, including the linked JSON seed and EC01–EC12 matrix.
Consumer: implement the C18 strict extractor, immutable call provenance, exact
refresh comparison and delivery decision. Use a contract-faithful MCP double;
COMMERCE-007 implementation is not a prerequisite. Existing BACKGROUND-001 and
its accepted Shared version remain prerequisites. Do not implement Commerce
ranking/evaluation. Component acceptance uses EC01–EC12 with call/send/usage/state
assertions; actual service pairing is SYSTEM-TEST-001-owned.


- [ ] Treat generic public query data as ordinary facts, never signed/validated discount Evidence. Current offer-policy verification still uses exact originally granted policy helpers; absence of suitable evidence causes referral.

- [ ] Keep final answer composition in CommerceAgent: a tool rendered template is not an instruction to send immediately. Validate structured facts/offer evidence and normal admission before WhatsApp delivery.

- [ ] Preserve C13 no-response follow-up suppression and credit semantics. Test reply-to-initial before follow-up, reply-to-initial after follow-up, reply-to-follow-up, ordinary single-recovery reply, duplicate audio engagement repair, and engagement racing final send recheck. No new recovery credit/attempt for continuation, no sequence3 or grant reset.

- [ ] Recheck current shop/capability permission and discount evidence before an offer reply is sent; pinning must not bypass revocation.
- [ ] Preserve per-conversation ordering, stale-version suppression, language mutation guards, outbound reservations and exactly the existing delivery ownership.
- [ ] Prevent cross-turn or expired/tampered offer evidence from supporting a customer claim; distinguish known-rule qualification from checkout guarantees.
- [ ] Exercise MCP timeout/throttle/cancellation and lease-loss paths without duplicate sends or leaked reservations.
- [ ] Provide host semantic telemetry for release/evidence outcomes using existing tracing/logging infrastructure.

- [ ] Handle REFER_TO_STORE as the single normal admitted reply, localised to the resolved language. Render its verified contact/store URL from trusted server context; otherwise say to contact the store directly. Do not trust model-supplied contact details, assert human notification, open a ticket or send an additional fallback message. Preserve current stale-turn/admission checks for referrals.

## Interfaces / Contracts

Existing ARCH-007/010/005 safeguards and the binding C18 producer/consumer contract. Do not redesign general billing policy.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C2, C3, C4, C6, C11**. Also apply **C13** for outreach/continuation semantics. These are required acceptance inputs, not optional examples.

Own final-delivery admission, evidence refresh, status handling and worker failure regression coverage. Preserve the existing unknown-message provider-status path for unpersisted guidance; no guidance receipt table/status handler or merchant usage. For normal replies recheck processing version/lease and current permissions immediately before send; revalidation failure replaces the proposed answer with one admitted referral.

### Deterministic review clarification

Implement the C4 Exact-call evidence refresh contract and its named fixtures.
Business MCP names remain arbitrary. Background captures/replays actual calls;
Commerce policy adapters return bounded structured evidence. No hard-coded
evaluator discovery, extra grant, new Shared field or new database table. Apply
C18 host call/deadline budgets; C8 internal provider counters and ranking remain
Commerce-owned and are represented by contract fixtures here.

### Required evidence

Add controllable barriers for new-message-during-model, lease loss, revocation-before-send, unknown provider acceptance and duplicate job delivery. Verify no stale language write or double reservation; actual send status uncertainty is not treated as safe automatic retry. History inclusion is tested in BACKGROUND-001; do not substitute prompt snapshots.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-BACKGROUND-001

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-012

- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-002

## Acceptance Criteria

- [ ] An authored template/query cannot authorize a discount by imitating evidence fields or a reserved helper name; normal factual product queries remain usable.

- [ ] A newer customer message or lost lease suppresses the older result without a WhatsApp send or stale language update.
- [ ] Disabling a feature/shop or changing an offer before delivery prevents an invalid offer reply.
- [ ] MCP failures and retries do not double-charge, double-send, bypass abuse limits or start an unbounded fallback loop.

- [ ] Unknown answers and unusable originally granted tools produce a factual bounded store referral without extra WhatsApp sends, fabricated contacts or unsupported offers. Revoked tools cannot be replaced by newly enabled ones.

## Validation

- [ ] Injection/unsupported claims in renderedText cannot replace verified contacts or evidence; multiple tool results still produce one normal admitted final response.

- [ ] Add focused multi-turn grant and unanswerable-question fixtures for the scoped acceptance criteria; assert granted tool IDs/versions and referral output, not just prompt text.
- [ ] Run focused turn/admission/evidence Vitest regressions with deterministic concurrent-turn and revoked-policy fixtures.
- [ ] Run declared build and git diff --check; provide any long integration command separately for developer execution.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; its real repository must be provisioned before execution preparation.

## Completion Report

### Status

Ready for Review.

### Files Changed

- Added Background-owned turn-local evidence provenance and exact-call refresh in `src/commerce/evidence.ts`.
- Wired `src/commerce/host.ts` to record trusted structured evidence only through an injected policy extractor and fail closed to one normal trusted referral when evidence cannot be refreshed.
- Preserved existing conversation admission, processing-version, lease, language, reservation, send, retry, and unknown-provider-status ownership.
- Added deterministic fixtures for renamed evaluators, literal/mapped inputs, recommendation evidence without a separate evaluator, changed results, missing provenance, revoked producers, duplicate references, exhausted budget, and lease rechecks.

### Work Completed

None; task definition only.

### Validation Results

- `npx vitest run tests/integration/commerce/host.test.ts tests/unit/commerce/evidence.test.ts tests/unit/services/conversation-turn-processor.service.test.ts` passed: 3 files, 73 tests.
- `npm run build` passed, including `prisma:generate` and TypeScript compilation.
- `npm run prisma:validate` passed.
- `npx tsc --noEmit` passed.
- `git diff --check` passed.

Requirement-to-fixture matrix:

| Requirement | Fixture | Expected side effects | Result |
| --- | --- | --- | --- |
| C16/C4 trusted offer evidence | `replays renamed evaluators with literal mapped arguments...` | One exact replay; rendered text is ignored; no untrusted contact/evidence authority | Passed |
| C4 recommendation evidence without separate evaluator | `deduplicates duplicate evidence references and recommendation evidence...` | Duplicate evidence IDs share one replay; no extra call | Passed |
| Missing provenance | `fails closed for missing provenance` | No replay and no positive offer claim | Passed |
| Revocation before send | `fails closed when the evidence producer is revoked` | Denied replay produces no send-authorizing evidence | Passed |
| Changed recommendation | `rejects changed recommendations...` | Refresh fails closed; exhausted budget causes zero replay | Passed |
| Lease/stale-turn protection | `rechecks the lease before and after replay` plus existing host/turn fixtures | Current-turn assertion occurs before and after refresh; stale result is not delivered or persisted | Passed |
| Duplicate/retry/send/reservation safeguards | Existing `conversation-turn-processor.service.test.ts` stale, duplicate, reservation, retry and provider-uncertainty cases | At most one normal admitted send; stale language/reservation cleanup preserved | Passed |

### Deviations

The Commerce policy adapter remains injected and contract-owned outside this repository; production pairing is intentionally not implemented here. The fixture extractor is deterministic and does not claim live Shopify or Commerce provider validity.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. The published shared runner already performs turn-local evidence extraction/budget reservation; Background owns immutable provenance, exact replay, current permission/lease rechecks, and delivery fail-closed handling.

### Unresolved Issues

Live Commerce producer/consumer pairing, live provider discount semantics, and deployment validation remain developer-owned SYSTEM-TEST/Gateway work.

### Architectural Concerns

No new architectural concern. The injected extractor is the explicit boundary for the Commerce-owned policy adapter; Background does not implement Commerce ranking, GraphQL execution, discount mutation, or a duplicate catalogue.

### Git / VCS

Expected execution branch: task/ARCH-020-BACKGROUND-002. Attempt: 1. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-BACKGROUND-002`, branch `task/ARCH-020-BACKGROUND-002`, published implementation commit `a7ccac5`. Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-BACKGROUND-002`, branch `task/ARCH-020-BACKGROUND-002`, published parent report commit `7d682c2a` (this final bookkeeping update follows on the same mirrored branch). Database submodule was not modified. No parent service gitlink or main integration was performed.

## Architect Review

### Changes Requested — Attempt 1 — 2026-09-21

**Not accepted; Ready for corrections**, Attempt 1 preserved, executor/claimed_at cleared. Reviewed implementation a7ccac57f26ca672fcdf51d6b01800ccbfcd43f0 and report ffcc04618d05cd59123387aabc38223ddda1f622; both remote heads verified and worktrees clean. C18 component acceptance remains independent of live Commerce/provider pairing; the following are consumer-owned requirements, not new producer dependencies.

#### R1 — P1: implement and wire the strict Background-owned extractor

Locations: `src/commerce/evidence.ts`, `src/commerce/host.ts` and `src/agents/commerce.agent.ts`. C18 explicitly assigns extraction to Background. Currently HostDependencies.extractEvidence is optional, no default extractor exists, and the production caller supplies none. Consequently normal policy calls register no evidence. Injecting an arbitrary extractor is not implementation of the fixed consumer contract; the tests extract data directly and never exercise a real recommendation envelope.

Add/export a strict extractor in evidence.ts using the accepted Shared CommerceEvidenceSchema and CommerceToolOutputs recommendation schema. Accept only a validated root evaluator or validated alternatives[*].evidence; null is no evidence. Reject malformed/truncated recommendation results as unusable, preserving that failure distinction rather than treating them as a legitimate empty success. C14 public-query wrappers, renderedText, nested values/product descriptions and arbitrary evidence-shaped JSON register zero IDs. Wire this extractor as the actual host default and Shared runner extractor; tests may inject controlled transports/results but must not supply a permissive evidence parser. No business tool-name switch, new endpoint or new Shared field.

Tests: EC01/EC03/EC07/EC12 through executeCommerceHost with the production extractor and a contract-faithful MCP double. Valid root and recommendation results register; two alternatives/two final IDs from one producer replay once; truncated or counterfeit results cannot authorize an offer. A zero-evidence factual answer still follows ordinary admission. Assert send/reservation counts, not just registry booleans.

#### R2 — P1: validate digests, immutable provenance and original/fresh evidence eligibility

Locations: TurnEvidenceRegistry.record/refresh in evidence.ts. record overwrites an existing evidenceId unconditionally. Neither record nor refresh recomputes the digest. refresh tests only the fresh expiry, allowing an expired original to be rescued, and does not require nonnull amounts or no unresolved conditions. Comparable equality alone is not the C18 matching algorithm.

Confirmed isolated reproductions: (a) an evidenceId of 64 literal c characters is accepted; (b) the same correctly hashed evidence recorded under arguments `{search:'one'}` then `{search:'two'}` overwrites without rejection; (c) original expires at 00:00:30, now is 00:00:31, refreshed evaluatedAt 00:00:30/expiresAt 00:01:00: refresh returns true. Case (c) recomputes both digests correctly. All must reject; an expired original should cause zero refresh requests.

Implement this order: Shared structural validation -> SHA-256 of canonical complete evidence excluding evidenceId -> current turn/grant/release match -> original eligibility/freshness -> immutable provenance insertion. Duplicate identical provenance may deduplicate; conflicting reuse must invalidate/refuse that ID and never replace its first authority silently. Store and replay detached snapshots of `{name,toolRevisionId,arguments,evidence}` from actual authenticated returns. Do not expose mutable internal arguments to adapters.

Before refresh, require each original ID to be trusted and unexpired at the frozen decision clock. Group by exact name/revision/canonical arguments; check remaining budget before any request. Validate every refreshed result/digest and require `evaluatedAt <= now < expiresAt`, positive lifetime <=60 seconds and applicable offer expiry. For each original, first find exactly one result by offerId plus canonical proposal, THEN compare full turn/grant/release and C18 semantic fields. A duplicate match must reject even if only one duplicate has matching savings. Require qualifying outcome, nonnull currency/savings/total and empty unresolvedConditions for a positive claim. Compare money as exact decimal values without floating point and preserve proposal operation order. Do not drop recommendation-level truncated state.

Permanent tests: EC04 changes each field independently with a newly computed hash and sufficient budget; EC05 missing/duplicate/empty/truncated; EC06 original/fresh expiry boundaries, future date, invalid digest, null money/unresolved conditions; EC10 conflicting provenance/cross-turn/unknown ID/budget. Use the canonical C18 JSON seed, not placeholder fingerprints as evidence IDs. The current changed-recommendation test exhausts budget first, so it does not test changed semantics; split it into one-refreshed-call changed-result rejection and zero-call exhausted-budget cases.

#### R3 — P1: distinguish refresh referral failures from stale/cancel suppression

Locations: evidence.refresh, the post-run refresh block in host.ts, and host/turn integration tests. Current refresh returns false for EVERY non-OK result, including STALE_TURN, causing the host to construct a referral when C18 requires no delivery. Conversely, transport exceptions and malformed refreshed evidence throw out of refresh into executeCommerceHost's generic unavailable error instead of producing the required single admitted referral for non-stale failures.

Use an explicit refresh outcome or typed error distinction: accepted / refer / suppress. STALE_TURN, local version/lease loss and cancellation suppress all send and language mutation. DENIED, NOT_FOUND, UNAVAILABLE, THROTTLED, INVALID_INPUT, INCOMPATIBLE_VERSION, ordinary refresh deadline, HTTP401/403, malformed result and transport failure produce one trusted admitted referral only if admission remains valid. No automatic refresh retry even with retryable=true. Preserve the smaller of remaining turn time and10-second call deadline; zero remaining call/time budget makes zero requests. Recheck normal admission after the refresh outcome before delivery; do not add another reservation/credit/send or switch tools/grants.

Tests: EC08/EC09 table-test each structured code and HTTP/transport/parse failure through the host/processor, asserting exact replay count (never a retry), normal referral count <=1 and no positive offer. EC11 use controllable barriers for new inbound, lease loss and cancellation while replay is pending; assert zero send, zero stale language update and existing reservation cleanup only. Use the real default extractor/host path introduced in R1; registry-only tests cannot prove delivery behavior.

#### Validation and deterministic resubmission

Independent temporary harness `/tmp/bg002-review/evidence-review.test.ts`: **6 existing evidence tests passed; 3 added review tests failed** for digest, conflicting provenance and expired-original resurrection. A temporary helper syntax error was corrected before the final run; it is not implementation evidence. No implementation was edited or live service contacted. Submitted 73-test/build/Prisma results remain reported evidence, not proof of the uncovered EC cases.

Implement R1–R3 in the listed modules and add the full EC01–EC12 consumer matrix in `tests/unit/commerce/evidence.test.ts`, `tests/integration/commerce/host.test.ts` and processor integration fixtures as appropriate. For each EC ID report replay/send/reservation/language-write counts and expected/actual outcome; tests must not let exhausted budget or invalid hashes mask unrelated checks. Add bounded evidence-outcome telemetry using existing infrastructure with no transcript/tool arguments or customer/evidence payload logging. Preserve C13/outbound uncertainty regressions. Rerun focused evidence/host/processor tests, build, Prisma validation and diff check. Replace stale Work Completed text and record prepared worktree/dependency pin evidence. Live pairing stays terminal-system-test-owned and explicitly unrun; do not wait for COMMERCE-007 implementation to complete these fixed contract checks.

Commit/push corrections and the report on the same mirrored branches, then return to Review. This parent overlay is published before preparation; no new attempt or downstream promotion is made by the review.

### Historical definition review


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


### Architect readiness amendment — 2026-09-21

Ready, unclaimed, attempt0. Accepted BACKGROUND-001 is the start prerequisite;
C18 fixes the interface. COMMERCE-007 is removed as a code/start dependency.
Component acceptance uses contract fixtures; terminal SYSTEM-TEST-001 owns real
producer/consumer integration. No task is launched or implementation accepted here.
