---
id: ARCH-020-BACKGROUND-001
architecture_id: ARCH-020
title: Integrate the generic MCP CommerceAgent host
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 150
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-016-BACKGROUND-003
  - ARCH-020-SHARED-001
  - ARCH-020-DATABASE-001
  - ARCH-020-COMMERCE-001
enables:
  - ARCH-020-BACKGROUND-002
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
created: 2026-09-20
updated: 2026-09-20
---

# Integrate the generic MCP CommerceAgent host

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Replace hard-coded feature prompts and local product tools with the published MCP capability path.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Background agent adapter, MCP client/auth, context normalisation, shared runner integration and conversation grant pinning.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

- [ ] Pass the pinned C16 response definition to Shared and consume only the stable finalResponse envelope; never interpret/send custom details. Cover R02/R07/R08/R12 and grant/hash persistence across turns.

- [ ] Implement C6.1 host-owned recovery instructions and freshly loaded, serialized recovery/customer/language context. Apply the explicit status matrix including COMPLETED with null completedAt; replace unrestricted product-help wording with original-grant-only assistance. Keep the pinned prompt release separate from fresh recovery state; use C2 history rather than an authoritative summary.

- [ ] Implement the C5 Exact available-tool discovery sequence: trusted shop/recovery/conversation/turn claims, first resolve then immutable grant persistence, execute-purpose tools/list with empty params, and tools/call bound to that original grant. shopId alone is not a grant selector.

- [ ] Consume C14 exact reusable tool/revision identities and original capabilityKeys provenance without copying query execution into Background. Manifest may contain arbitrary new names or no remote tools; retain existing conversation grant through reconnects.

- [ ] Discover feature-selected tools and schemas dynamically from MCP; invoke by discovered name with the existing pinned grant. Do not download/execute database operations or response templates in Background.

- [ ] Search phone-matched recoveries across all merchants on the receiving Moda sender before counting distinct recoveries. Two shop-scoped customers with the same phone and one recovery each require identification; never pick the first customer, infer a merchant from Moda providerAccountId or process the message for both shops. V1 reuses the single Moda sender and requires no merchant WABA/number setup.

- [ ] Preserve C13 outbound categories: initial/follow-up attempts each retain their own provider ID and outboundMessageId but share one recovery Conversation. Replies to either template or a later agent message route to that same recovery; repeated outreach counts once. Do not create a grant until the first admitted CommerceAgent turn.

- [ ] Enforce the parent "WhatsApp reply correlation decision" before recovery engagement, grant creation or MCP/model execution. Validate referenced outbound message ownership against the incoming customer and configured provider sender; never resolve ambiguity by recency or prior channel binding. For messages without a reference, automatically route exactly one distinct recovery found for the customer/sender; do not request identification in that case.
- [ ] For unreferenced messages with zero or multiple candidate recoveries, do not invoke CommerceAgent, create standalone conversations, or mutate a guessed recovery. Exactly one candidate follows the normal recovery conversation path and original tool grant. Use the fully specified C3 lightweight Redis clarification guard; never attach guidance to a guessed merchant.

- [ ] Consume the exact published shared version; adapt the real whatsapp.worker.ts runAgent entry path to the shared runner.
- [ ] After existing admission, resolve/persist one immutable tool grant per conversation and load manifest/prompts/tools explicitly. First resolution uses resolve-only credentials; persist with unique-key concurrency handling, then use execute credentials bound to the winning pin. All subsequent inbound versions and retries reuse the grant.
- [ ] Sign short-lived turn assertions with fixed audience/purpose; keep credentials/tenant identity outside model-controlled tool arguments.
- [ ] Require a real checkoutRecoveryId in every wire turn context and verify Conversation -> CheckoutRecovery -> Shop ownership before MCP/model work. Reject missing/sentinel recovery IDs; no standalone or direct-shop fallback. Adapt MCP schemas/results without a feature-specific worker switch.
- [ ] Propagate deadline/cancellation and bounded errors through the existing reservation/lease retry lifecycle; remove forced final-after-search and legacy local tool fallback.

- [ ] Before the first model invocation create or load one immutable grant per Conversation.id after admission; later inbound versions always reuse it. Supply trusted verified store contact/canonical Shop.domain separately from model arguments, and pass grantId/current turn identity to MCP. Never delete/recreate a grant for capability expansion.

## Interfaces / Contracts

Read the binding schema contract in docs/decisions/database/ARCH-020/DATABASE-001-persist-capability-releases-and-turn-revision-pins.md. Its exact field names/types, enum values, JSON shapes/bounds, immutable release membership and selectedCapabilityKeys/grantedTools conversation grants are the persistence contract; do not invent alternative representations. Shared APIs serialize dates as ISO strings and map database environment enums to lower case.

Shared ./commerce and ./commerce/runner. Consume accepted database schema via Background database submodule; server fixtures allow independent implementation.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C0, C1, C2, C3, C4, C5, C6**. Also apply **C13** for outreach/continuation semantics. These are required acceptance inputs, not optional examples.

Own routing service, conversation/audio persistence, generic MCP host and narrow platform routing-reply service. Reuse existing message/provider IDs, recovery/customer links and shared inbound/status parsers unchanged. Add no WhatsApp schema fields. Preserve batching and assemble prior same-conversation history using existing records. Remove standalone/clarify-basket agent branches.

### Required evidence

Unit/integration fixtures cover valid reference delayed1h/10h, no-reference0/1/2 distinct recoveries, duplicate outreach for one recovery, terminal recovery ambiguity, invalid explicit reference without fallback, existing stored-message ownership, voice routing before download, prior-question follow-up and unchanged batching/stale-turn safeguards. Routing guidance tests assert exact fixed text, no merchant usage/grant, one Redis SET NX winner per event within 24h, existing abuse limits, Redis-error suppression, and retained guard after failed/ambiguous sends.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-016-BACKGROUND-003
- ARCH-020-SHARED-001
- ARCH-020-DATABASE-001
- ARCH-020-COMMERCE-001

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-BACKGROUND-002
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001

## Acceptance Criteria

- [ ] Demonstrate the assigned C16 response-contract cases with named fixtures and actual outcomes; reference the exact published definition/hash or synthetic preview definition used.

- [ ] Verify C6.1 P01–P12 through host integration fixtures, including fresh status on later turns, explicit-language precedence, validated detection persistence and no delivery from invalid/stale final results.

- [ ] Two conversations for one shop with different pinned releases retain different original lists; a second shop cannot select those grants. tools/list contains exact descriptors only, omits revoked tools, rejects caller-supplied shopId parameters and never expands after publication.

- [ ] Newly published query tool works for new grants without a Background build, while a retained grant cannot discover it; no fixed conversation_core/product_search admission dependency remains beyond legitimate current feature entitlement checks.

- [ ] Valid explicit replies resume only their referenced recovery and original grant, including replies delayed by one or ten hours with intervening outreach to other recoveries.
- [ ] Unreferenced messages with exactly one recovery route without clarification. Unreferenced zero/multiple-candidate, unknown-reference, wrong-customer, wrong-provider and missing-recovery cases cannot invoke CommerceAgent or access merchant tools. Replying to an unowned clarification cannot manufacture a recovery link.

- [ ] New conversations consume compatible tool/prompt revisions without redeploying Background; all turns/retries of existing conversations reuse their original exact tool grant and prompt release.
- [ ] Unknown contract/runner versions, MCP outage and invalid results fail explicitly; no hard-coded discount fallback is used.
- [ ] Existing language handling, admission ordering and structured final-response semantics remain intact with the generic runner.

- [ ] Two turns of the same conversation use the same grant despite a new release/feature or worker restart. Concurrent first turns select one winning grant; a different eligible new conversation may receive the new release.

## Validation

- [ ] Publish a newly named supported tool without Background deployment, use it for an eligible new conversation, and prove an existing conversation cannot list/call the new name or template version.

- [ ] Add focused multi-turn grant and unanswerable-question fixtures for the scoped acceptance criteria; assert granted tool IDs/versions and referral output, not just prompt text.
- [ ] Run focused Vitest tests with a local mock MCP server for discovery, prompt retrieval, tool calls, tenant headers, release pin races and deadlines.
- [ ] Run declared npm run build and git diff --check; do not assume lint/typecheck scripts exist.
- [ ] Record the client/server compatibility set established by Commerce foundation before acceptance; mocks alone cannot prove cross-SDK interoperability.

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

Expected execution branch: task/ARCH-020-BACKGROUND-001. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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


## Dependency readiness — 2026-09-20

All listed prerequisites are architect-accepted Complete following SHARED-001 Attempt 2 acceptance. Consume exact published Shared 0.13.1 (commerce and commerce/runner exports). Ready is eligibility only: no claim or execution is made by this review. Normal preparation must synchronize the canonical task worktrees and verify dependency source availability; do not silently use an older database/service revision.
