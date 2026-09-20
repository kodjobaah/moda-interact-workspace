---
id: ARCH-020-SYSTEM-TEST-001
architecture_id: ARCH-020
title: Validate merchant-configured MCP conversations end to end
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 200
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-012
  - ARCH-020-BACKGROUND-001
  - ARCH-020-BACKGROUND-002
  - ARCH-020-COMMERCE-001
  - ARCH-020-COMMERCE-002
  - ARCH-020-COMMERCE-003
  - ARCH-020-COMMERCE-004
  - ARCH-020-COMMERCE-005
  - ARCH-020-COMMERCE-006
  - ARCH-020-COMMERCE-007
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-009
  - ARCH-020-COMMERCE-010
  - ARCH-020-COMMERCE-011
  - ARCH-020-DATABASE-001
  - ARCH-020-GATEWAY-001
  - ARCH-020-GATEWAY-002
  - ARCH-020-SHARED-001
  - ARCH-020-SHOPIFY-001
enables: []
created: 2026-09-20
updated: 2026-09-20
---

# Validate merchant-configured MCP conversations end to end

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Independently validate the complete Studio-to-merchant-to-conversation capability lifecycle.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

System-test fixture services, test data, architecture scenarios and evidence reporting.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

- [ ] Verify all C16 R01–R12 cases and N13 traversal, including release-only schema change without worker/Shared deployment, old/new conversation pinning, immutable publication and stable delivery-envelope behaviour.

- [ ] Validate C6.1 fixed platform versus editable capability prompt boundaries across Background and Studio preview. Cover the exact recovery status/language matrix with equivalent synthetic inputs; distinguish fresh turn context from pinned prompts/tools.

- [ ] Execute the UI navigation matrix N01–N12 against integrated services and the new COMMERCE-011 dependency. Include direct links, Back/Cancel, auth expiry, double activation, docs outage, draft conflict and publication-stage recovery.
- [ ] Create an arbitrary non-seed Feature through existing Admin, include it in a plan, configure/publish a new schema-authored query tool in Studio and opt in through merchant UI. Confirm a new routed recovery conversation uses it without deployment of Commerce/Background/merchant UI between authoring and invocation.
- [ ] Reuse one exact tool version in two feature configurations, publish a changed version, and prove old grants retain original query/template/provenance. Conflicting versions in one release reject; revoking original associations never gains authority from a new association.

- [ ] Add the C14 end-to-end demonstration: staff creates a database-defined tool with schema/operation/template, publishes it, merchant feature gates discovery, agent invokes it, and a later definition version cannot change an existing conversation.

- [ ] Use one Moda providerAccountId/providerPhoneNumberId shared by two merchants and two separate Customer rows with the same customerPhone. With one recovery per shop, unreferenced input produces one platform clarification and zero agent calls; an explicit reply selects only its owning shop. With one total recovery it routes automatically. Do not introduce multi-number routing fixtures; the existing provider identifiers identify only the one configured Moda channel.

- [ ] Exercise C13 initial sequence1 -> optional sequence2 in one Conversation with two distinct outbound provider IDs. Reply to each and to an intervening agent message; verify one routing candidate, retained context provenance, suppressed unsent follow-up after engagement and unchanged existing credit accounting. Test two recovery generations, no sequence3, no tool-grant reset and preserved existing provider IDs on both template paths.

- [ ] Validate reply correlation with two shops and multiple recoveries sharing a customer phone: valid references at one-hour/ten-hour delays select the original recovery, not later outreach; no-reference messages with exactly one distinct recovery route automatically without identification guidance and reuse its original grant when present; no-reference messages with zero/multiple candidates, unknown references and customer/provider ownership mismatches never invoke the model/MCP or create grants/standalone conversations. Repeated outreach for one recovery must count as one candidate. Include unreferenced follow-ups and replies to the identification instruction. Verify approved clarification delivery deduplication, rate limits and cost attribution against C3 (best-effort Redis guard, no database persistence).

- [ ] Provide isolated repeatable fixtures for two shops, staff roles, feature preferences, revisions, baskets and supported/unsupported discounts.
- [ ] Validate draft/edit/preview/publish/rollback and conversation-wide grants and retry stability across different service instances.
- [ ] Validate MCP discovery/prompts/tools with the actual selected client/server versions and shared runner parity.
- [ ] Exercise qualifying/nonqualifying/similar-product flows, NONE/FIXED/AI modes, currencies, stale facts and unsupported rules.
- [ ] Reject conversations without a checkout recovery, sentinel recovery IDs and mismatched recovery/shop/conversation links before model/MCP work. Exercise tenant/auth/revocation, prompt/data injection, stale turns, duplicate jobs, deadlines, outage recovery and outbound accounting.
- [ ] Validate recursive database build pins, gateway exposure, trace propagation, environment separation and absence of secret/payload leakage.
- [ ] Provide bounded representative conversation-load scenarios with measured tool calls, database cost, latency and queue lag; label capacity assumptions.

- [ ] Exercise rapid mouse/touch/keyboard and direct concurrent duplicate requests for sign-in, draft save, publishing, rollback, feature preferences and model-backed preview; verify busy/retry behaviour, one committed state change/audit and one preview budget/model invocation across replicas.

- [ ] Validate at least two turns under the same conversation grant while publishing a new release/enabling a tool between them. Verify the old conversation cannot list/call it, the original exact version remains enforced across replicas/retries, and a new conversation can receive the new grant. Test unanswerable questions, unsupported facts, revocation, tool failure and invented contact injection.

## Interfaces / Contracts

All ARCH-020 contracts and accepted implementations. External/live validation uses explicitly isolated test identities, not real customer messaging.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C0 through C13**. Also apply **C13** for outreach/continuation semantics. These are required acceptance inputs, not optional examples.

Deliver scripts/run-arch020-commerce.js and package script test:arch020-commerce for isolated end-to-end runs, plus test:arch020-commerce:static for agent-owned fixture/config checks. Runner must reject non-isolated targets and report implementation/DB/shared revisions. Build scenarios against real integrated services with fixture provider/model transports, not mocks replacing the services under test.

### Required evidence

Required scenario groups: routing0/1/2 and sender ownership; normal/voice history; Redis clarification guard concurrency/TTL/failure and no merchant attribution; staff roles/CSRF/duplicate actions; publish/replay/rollback; multi-turn original grants; unsupported/unknown discounts and referrals; evidence changes; private/public MCP; preview isolation/budget; telemetry redaction; migration preservation. Add bounded load profile20 concurrent conversations across2 shops for5min, record lag/p95/calls/rows and failures without claiming production capacity. Full/container/load/live runs remain developer-owned.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-COMMERCE-012

- ARCH-020-BACKGROUND-001
- ARCH-020-BACKGROUND-002
- ARCH-020-COMMERCE-001
- ARCH-020-COMMERCE-002
- ARCH-020-COMMERCE-003
- ARCH-020-COMMERCE-004
- ARCH-020-COMMERCE-005
- ARCH-020-COMMERCE-006
- ARCH-020-COMMERCE-007
- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-009
- ARCH-020-COMMERCE-010
- ARCH-020-COMMERCE-011
- ARCH-020-DATABASE-001
- ARCH-020-GATEWAY-001
- ARCH-020-GATEWAY-002
- ARCH-020-SHARED-001
- ARCH-020-SHOPIFY-001

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables


None.

## Acceptance Criteria

- [ ] Validate accepted COMMERCE-012 caching end to end: threshold/expiry, cross-shop isolation, revoked grants, Redis fallback and mandatory fresh offer evaluation.

- [ ] Cover C7.1 A01–A11 with injected Google/development identities and direct endpoint/action requests; verify hosted bypass rejection, local SUPER_ADMIN audit writes and no bypass-to-live-MCP access.

- [ ] Demonstrate the assigned C16 response-contract cases with named fixtures and actual outcomes; reference the exact published definition/hash or synthetic preview definition used.

- [ ] Record C6.1 P01–P12 outcomes, including unsupported-question store referral, status transition without grant expansion and identical structural rules in live-host fixtures and preview. Distinguish scripted fixture evidence from any developer-invoked live-model evaluation.

- [ ] End-to-end navigation and unknown-feature/query acceptance cases pass with explicit side-effect evidence and versions; no manual DB edit, handler addition or feature-name whitelist is needed to complete authoring.
- [ ] Live provider evidence is separate from synthetic preview evidence; public-query success is not claimed from a mocked response alone.

- [ ] All non-system implementation/publication/infrastructure tasks are Complete/Accepted before execution; developer manually invokes this terminal task.
- [ ] Changing an enabled capability prompt affects a newly granted conversation without redeploying workers, while drafts and revoked tools remain unavailable.
- [ ] No cross-shop access, invented discount guarantee, unauthorised basket mutation, duplicate delivery or admission bypass occurs in required fixtures.
- [ ] All required operational and rollout evidence is recorded against exact revisions; unresolved blocking failures prevent architectural completion.

- [ ] Duplicate UI activation or replayed requests cannot create duplicate drafts/releases/preference transitions or extra preview model cost; failure/cancel recovery permits intentional retries without replaying completed operations.

- [ ] Existing conversations never acquire additional tools. Unanswerable factual questions result in one localised store referral with only verified contact details and no unsupported claim or purported human handoff.

## Validation

- [ ] Assert no service restart/deployment between publications, no code registration for the new tool name, exact structured/rendered results, old-definition retention, feature denial, duplicate-action protection and unsupported operation rejection.

- [ ] Add focused multi-turn grant and unanswerable-question fixtures for the scoped acceptance criteria; assert granted tool IDs/versions and referral output, not just prompt text.
- [ ] Run agent-owned syntax/fixture/contract checks and document exact reproducible local system-suite commands.
- [ ] The developer owns multi-container system/load runs and any deployed Shopify/Render/WhatsApp/model validation unless explicitly authorised for the exact run; record command, revisions, result and exit code.
- [ ] Accept clear developer validation evidence without rerunning merely because the agent did not launch it.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; its real repository must be provisioned before execution preparation.

## Completion Report

### Status

Not Started.

### Files Changed

None; implementation has not started.

### Work Completed

None; task definition only.

### Validation Results

Not run. At execution, distinguish agent checks from exact developer validation required.

### Deviations

Task definition authored on local main by explicit developer request. Normal execution policy remains unchanged.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

See parent architecture review assumptions; no implementation evidence asserted.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-SYSTEM-TEST-001. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
