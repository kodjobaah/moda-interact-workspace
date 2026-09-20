---
id: ARCH-020-COMMERCE-003
architecture_id: ARCH-020
title: Implement draft and release publication lifecycle
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-002
  - ARCH-020-DATABASE-001
  - ARCH-020-SHARED-001
  - ARCH-020-COMMERCE-011
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-004
  - ARCH-020-COMMERCE-008
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Implement draft and release publication lifecycle

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Persist and atomically publish immutable capability releases with an auditable rollback path.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Commerce persistence services and protected server actions for draft/publish/history/rollback/disable.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

### Duplicate-action protection

Every state-changing or costly UI action in this task must prevent duplicate
activation, including mouse double-click, double-tap, Enter/Space repetition and
form-submit plus button-click combinations. Acquire a synchronous submission
guard before awaiting work (a render-delayed disabled state alone is insufficient),
and route all activation paths through the same submit handler. Disable the
trigger and conflicting controls immediately, show a meaningful pending label,
and expose accessible busy/status feedback. Do not lock unrelated navigation.

Keep the guard until the operation has definitively completed, failed or been
cancelled. A client timeout is an unknown outcome: reconcile the original
operation before allowing a retry, rather than silently creating a second one.
On a known failure, restore controls and preserve input for an intentional retry.
Ignore stale completions so an earlier request cannot reset a newer request's
pending state. Debounce alone is not sufficient for mutations or paid previews.
Server authorisation and duplicate protection are required independently of the
browser controls; inspect direct duplicate requests as well as UI behaviour.

## Work Items

- [ ] Reuse C7.1 guards for every publication operation and validation endpoint; ensureDevelopmentStudioAdmin inside the same FK-backed audit/publication transaction when the server-resolved principal is development bypass. Verify A07/A08/A10; no copied auth policy.

- [ ] Implement C16 createRelease definition/hash persistence, replay binding and authenticated /api/studio/response-contract/validate; baseline seed, immutable clone semantics, role enforcement and R01–R06/R09.

- [ ] Implement independent createTool/updateTool/createToolDraft/updateToolDraft/publishToolRevision/setToolEnabled with C7 replay/CAS/audit. Capability drafts store exact toolBindings; no copied definitions. Shared tools can be reused; no implicit latest revision.
- [ ] Consume the accepted COMMERCE-011 local schema/compiler validator for query publication; validate installed policy operation descriptors through an injected registry interface. Until concrete adapters exist, test policy operations using explicit fixtures and reject unavailable adapters at runtime, never claim they are installed.
- [ ] Release creation rejects conflicting shared-tool revisions, deduplicates identical ones and preserves full original grant provenance. Base conversation_core can contain no tools. Publication never modifies Admin Feature/plan/preference records.

- [ ] Read the existing Admin-owned Feature catalogue by database identity for Studio configuration. Do not create or mutate Feature records, plan mappings or ShopFeaturePreference from Studio. A missing Commerce configuration must not change billing eligibility. Validate an arbitrary newly created feature key rather than seed-name whitelists.

- [ ] Create/save/publish independent tool definitions and exact capability toolBindings using existing replay/CAS/audit. Validate definition-version changes and available operationVersion; hash schemas/mappings/templates. Seed reviewed example definitions through existing explicit seed command.

- [ ] Implement capability bindings, optimistic draft edits and bounded schema validation using the canonical shared package.
- [ ] Validate database definitions, executor-operation availability and runner compatibility and create complete immutable release membership, then activate its pointer in a separate explicit atomic operation.
- [ ] Append actor/reason/hash audit evidence in the same transaction; implement compatible rollback and emergency disable.
- [ ] Enforce the DATABASE-001 publishing responsibilities: atomic 1–32-member release creation with contiguous positions and base capability, no later member insertion, CAS writes, canonical content hashing and actor/audit transactions.
- [ ] Provide paginated read models for Studio and an idempotent explicit initial-release seeding command; never seed by wiping tables.
- [ ] Consume the accepted database revision through the nested submodule; document the exact pin.

- [ ] Make create/save/publish/activate/rollback/enable/disable mutations replay-safe. Each logical operation carries one opaque operationId reused on retries and a canonical payload hash. Use CommerceAuditEvent.id as the unique operation key inside the same transaction as business writes; store payloadHash and bounded result IDs in metadata. Check current authorisation first. A committed matching actor/action/hash replay returns the original result; mismatched reuse conflicts. Concurrent duplicates must roll back losing writes and resolve the winning audit record, producing no extra revision/release/audit. Keep CAS checks for distinct conflicting edits. Set enabled to an explicit value, never blind toggle.

## Interfaces / Contracts

Read the binding schema contract in docs/decisions/database/ARCH-020/DATABASE-001-persist-capability-releases-and-turn-revision-pins.md. Its exact field names/types, enum values, JSON shapes/bounds, immutable release membership and selectedCapabilityKeys/grantedTools conversation grants are the persistence contract; do not invent alternative representations. Shared APIs serialize dates as ISO strings and map database environment enums to lower case.

Database revision/release model and ./commerce schemas. Reuse canonical policy state read-only.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C1, C4, C7**. These are required acceptance inputs, not optional examples.

Deliver publication domain services, strict action schemas, transactional audit/replay and explicit seed CLI. Build typed read-only executor-operation descriptors as the publication registry; operations may be added by COMMERCE-005/006/007, but descriptors alone must not claim operation availability. Publish database tool definitions only when their query executor/schema or policy-operation versions have executable implementations in the deployed build. Synthetic registry fixtures permit this task to be tested before later implementations.

### Deterministic review clarification

Synthetic executable registry adapters are dependency-isolated test fixtures,
never production registrations. This task proves publication validation and
transactions with those fixtures; COMMERCE-005/006/007 provide real executors and
SYSTEM-TEST-001 proves the deployed author/publish/invoke flow. Do not add a
circular dependency on those later tasks or advertise unimplemented operations.
Provide the isolated PostgreSQL rehearsal command and expected assertions; report
agent fixture results separately from developer-owned database rehearsal evidence
under C12. An unexecuted rehearsal must remain explicitly pending.

### Required evidence

Use two-transaction local storage fixtures and an isolated PostgreSQL rehearsal for duplicate operation IDs, mismatched reuse, revision allocation, CAS pointer conflicts, rollback and failed partial publication. This backend task tests direct requests; COMMERCE-008 owns mouse/keyboard tests.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-COMMERCE-002
- ARCH-020-DATABASE-001
- ARCH-020-SHARED-001
- ARCH-020-COMMERCE-011

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-012

- ARCH-020-COMMERCE-004
- ARCH-020-COMMERCE-008
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Demonstrate the assigned C16 response-contract cases with named fixtures and actual outcomes; reference the exact published definition/hash or synthetic preview definition used.

- [ ] Two features can reuse one published tool; editing/publishing a new tool version changes neither feature binding until explicitly updated. A release with conflicting tool versions is rejected atomically.
- [ ] Publish a new static Shopify query within the pinned schema without registering a business operation or deploying a service; changed query/schema/template requires a new tool version.

- [ ] Concurrent publish/edit operations cannot overwrite each other or expose partial releases.
- [ ] Published revisions are immutable; rollback preserves history; invalid definitions or unavailable executor operation versions cannot be published.
- [ ] Every release mutation is server-authorised and audited; no merchant feature, discount or billing settings are overwritten.

- [ ] Concurrent identical mutation requests yield one committed business change and one operation audit record. Matching retries recover the original result; altered payload/actor reuse is rejected. A timeout after commit cannot create another revision/release on retry.

## Validation

- [ ] Publishing a new definition over an installed operation succeeds without a service deployment; changed definition with unchanged version, unsupported operation, bad mapping/template and duplicate release tool names fail atomically.

- [ ] Run focused local transactional/optimistic-concurrency tests with deterministic storage fixtures.
- [ ] Provide a developer-owned PostgreSQL rehearsal command for atomic pointer/audit and rollback evidence; run declared local type/lint checks.

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

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. No additional provisioning prerequisite is introduced.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-COMMERCE-003. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
