---
id: ARCH-020-COMMERCE-001
architecture_id: ARCH-020
title: Establish the Next.js service and nested database submodule
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-020-BACKGROUND-001
  - ARCH-020-COMMERCE-002
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Establish the Next.js service and nested database submodule

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Provide a reproducible Next.js application foundation in the new Commerce repository.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

**Readiness:** repository provisioning was verified on 2026-09-20. The private `https://github.com/kodjobaah/moda-interact-commerce.git` repository is registered as the workspace submodule at main commit `01c550c3e3f55dd23a4ecc9514c846bb88cf2067`. The architect promotes this task to Ready with no attempt claimed. See the completed provisioning checkpoint in the implementation handoff. Next.js and the nested database submodule remain this task’s deliverables.

## Scope

New repository app shell, package/toolchain config, .gitmodules database pin, Prisma generation, health/readiness and local development documentation.

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

- [ ] After the handoff setup checkpoint registers the remote submodule and owner, scaffold the Node-runtime Next.js App Router application without business features.
- [ ] Add database/ as a Git submodule of https://github.com/kodjobaah/moda-interact-database.git pinned to an integrated revision; never copy the schema.
- [ ] Provide explicit dev/build/start/typecheck/lint/test and prisma:generate commands; recursively initialise database before client generation in clean builds.
- [ ] Establish server-only connection handling and separate liveness/readiness routes with no secret disclosure; do not run migrations on application startup.
- [ ] Choose and record a tested MCP SDK/Next.js adapter/client compatibility set with a bounded local round trip; no production endpoint or authentication bypass.

- [ ] Provide a reusable pending-action/form pattern for the Studio shell so later screens can use a synchronous guard, native disabled controls and accessible busy/error states. No application-wide network lock.

## Interfaces / Contracts

Proposed private /api/mcp; actual SDK/protocol versions documented here and consumed by BACKGROUND-001.

### Implementation guidance

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C5, C9, C10**. These are required acceptance inputs, not optional examples.

Deliver Next App Router Node service, nested database pin, scripts dev/build/start/typecheck/lint/test/prisma:generate, docs/runtime-compatibility.md and a local MCP protocol fixture. Lock exact tested server/client/adapter versions and record Node/Next/React versions. Fixture route must be test-only and absent from the production route tree. Provide /health/live and /health/ready exactly as C10.

### Required evidence

Fresh recursive clone fixture validates generated Prisma and production build/start/health. Compatibility fixture covers initialize, resource read, prompt retrieval and tools/call for the C5 stateless profile. UI shell test only needs its pending-action example; no paid preview test before preview exists.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies


None.

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-BACKGROUND-001
- ARCH-020-COMMERCE-002
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] A fresh recursive clone and canonical execution worktree can generate Prisma and build the service using the database pin.
- [ ] No browser bundle contains server credentials; health routes disclose no credentials or tenant records.
- [ ] Actual build/start/port/health contracts are documented for Gateway; no Vercel hosting assumption is introduced.

- [ ] A local example/test of the shared UI pattern dispatches once under same-tick double activation and permits an intentional retry after a known failure.

## Validation

- [ ] Run the new declared typecheck/lint/build and focused local health/adapter smoke checks.
- [ ] Check git submodule status --recursive and clean-clone/build instructions; record nested database SHA and git diff --check.

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

None blocking task preparation; repository provisioning is complete. Application implementation and nested database registration remain outstanding task work.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-COMMERCE-001. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
