---
id: ARCH-020-COMMERCE-004
architecture_id: ARCH-020
title: Serve authorised MCP capability bundles
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-003
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-005
  - ARCH-020-COMMERCE-010
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Serve authorised MCP capability bundles

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Expose published prompts, resources and tools with request-scoped tenant and turn authorisation.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

/api/mcp transport, service-assertion verification, manifest/prompt registry, policy adapters and scoped dispatch.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

- [ ] Serve C16 responseContract/hash in the C5 manifest from the selected/pinned release; reject incompatible definitions, never select latest for an existing grant. Cover R07/R12.

- [ ] Implement the C5 Exact available-tool discovery sequence: trusted shop/recovery/conversation/turn claims, first resolve then immutable grant persistence, execute-purpose tools/list with empty params, and tools/call bound to that original grant. shopId alone is not a grant selector.

- [ ] Resolve capability toolBindings through immutable CommerceToolRevision records and dispatch the C14 execution union. Dedupe identical shared versions; enforce enabled tool plus any still-eligible ORIGINAL provenance capability; never use newly added associations as authority.
- [ ] Query execution is injected from COMMERCE-005; this transport task proves authorization/dispatch using shared-contract fixtures before real provider integration. No hard-coded business tool names. Zero remote tools produces an empty tools/list, not failure.

- [ ] Implement the generic database-definition executor and safe response renderer in C14. tools/list exposes only name/description/inputSchema for the merchant grant. tools/call loads that pinned definition, validates/map arguments, executes the approved operation and returns data plus renderedText. Credentials/merchant identity are injected server-side.

- [ ] Implement authenticated Streamable HTTP with the COMMERCE-001 compatibility set and the canonical shared schemas.
- [ ] Validate service assertion issuer/audience/algorithm/expiry/purpose/key ID; accept only the Background live-turn principal, resolve durable Conversation -> CheckoutRecovery -> Shop ownership and current lifecycle, rejecting conversations without a recovery and mismatched recovery claims. Reject browser/admin sessions and other service identities even on the private network.
- [ ] Resolve effective features, offer policy and immutable release pin; serve commerce.capabilities, prompts/get and tools/list explicitly. Resolve-purpose assertions can only select a published manifest; tool/prompt execution uses execute-purpose assertions checked against the durable pin.
- [ ] Check current permissions and registry binding on every tool dispatch, including direct calls to undiscovered tools.
- [ ] Disable personalised response caching and process-global tenant registry mutation; enforce body/result bounds, approved origins and typed errors.

- [ ] Bind all tools/list, prompts/get and tools/call operations to CommerceConversationGrant. First resolve establishes one grant candidate; after a grant exists return that original bundle and never reselect from current release/features. Enforce exact tool name/version membership server-side as well as current permissions. No alternate endpoint, rediscovery, version substitution or reconnect may expand access.

## Interfaces / Contracts

SHARED-001 canonical manifests/turn claims; established staff sessions are not MCP credentials.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C0, C1, C4, C5**. These are required acceptance inputs, not optional examples.

Deliver /api/mcp with fixed method/purpose matrix, assertion verifier, request-scoped capability resolver and exact-version dispatcher. Local registered fixture handlers exercise transport before real Shopify handlers exist. Return only granted original tool versions still permitted now. No preview session can call this endpoint.

### Required evidence

Test the complete purpose/method matrix, malformed JWT alg/kid/exp/environment, crossed recovery/customer scope, stale processing version, body limits, unexpected Origin, two shops/two server instances, and direct unlisted tools. Test database ownership separately from shared schema parsing.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-COMMERCE-003
- ARCH-020-SHARED-001

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-012

- ARCH-020-COMMERCE-005
- ARCH-020-COMMERCE-010
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Demonstrate the assigned C16 response-contract cases with named fixtures and actual outcomes; reference the exact published definition/hash or synthetic preview definition used.

- [ ] Two conversations for one shop with different pinned releases retain different original lists; a second shop cannot select those grants. tools/list contains exact descriptors only, omits revoked tools, rejects caller-supplied shopId parameters and never expands after publication.

- [ ] Shared tool appears once in tools/list; revoking one of two originally eligible associations retains access through the other, revoking both denies, and adding a third cannot revive an ungranted revision.
- [ ] Arbitrary valid new names dispatch through execution.kind without redeploying Background; missing concrete executor fails UNAVAILABLE.

- [ ] Two simultaneous shops/replicas cannot share prompts, credentials or tool permissions; cross-tenant, expired, wrong-purpose and forged claims fail.
- [ ] Worker credentials never read drafts; revoked capabilities cannot execute even with a previously pinned release.
- [ ] There is no browser-facing live MCP proxy; preview uses local fixture adapters and cannot obtain Background signing credentials.
- [ ] A new compatible published prompt is visible to a new conversation without service/worker redeployment while every existing conversation retains its original grant.

- [ ] Enabling a feature or publishing a new tool after the first turn cannot expose it to the same conversation. Direct calls to it fail even with valid Background identity. Restart/retry/another replica preserves the original allowlist; revocation only restricts it.

## Validation

- [ ] Test renamed/new tool discovery with no per-tool code registration, eligible/ineligible feature mappings, pinned old definitions after publication, operation-level discount permission, one-pass rendering, missing/null/empty results and expression/prototype injection.

- [ ] Add focused multi-turn grant and unanswerable-question fixtures for the scoped acceptance criteria; assert granted tool IDs/versions and referral output, not just prompt text.
- [ ] Run local MCP client/server tests for discovery, explicit prompt retrieval, tool schemas and typed failures.
- [ ] Exercise simultaneous tenants, no-cache headers, revocation, process restart/replica independence and malformed/auth failures with synthetic keys.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; the actual repository must be provisioned before execution preparation.

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

Commerce remote repository/submodule provisioning remains outstanding; role/route definitions exist in this review packet.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-COMMERCE-004. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
