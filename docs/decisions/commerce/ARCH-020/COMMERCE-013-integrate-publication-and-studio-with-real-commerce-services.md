---
id: ARCH-020-COMMERCE-013
architecture_id: ARCH-020
title: Integrate publication and Studio with real Commerce services
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 125
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-003
  - ARCH-020-COMMERCE-004
  - ARCH-020-COMMERCE-005
  - ARCH-020-COMMERCE-006
  - ARCH-020-COMMERCE-007
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-011
enables:
  - ARCH-020-COMMERCE-009
  - ARCH-020-GATEWAY-001
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-21
updated: 2026-09-21
---

# Integrate publication and Studio with real Commerce services

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Connect accepted publication, compiler, executor and Studio components through C17
ports and prove the assembled U01–U13 authoring flow works with real services.

## Context

003 and008 are independently accepted against agreed interfaces and fixtures.
This task supplies the production composition; it is not another UI build or a
substitute for terminal cross-service SYSTEM-TEST-001. Definition authored on main
under the user's exception. No attempt is claimed.

## Scope

Production adapters, route/service composition, installed executor registration,
UI read-model translation and local integrated acceptance in moda-interact-commerce.
Own `src/commerce/integration/` and minimal wiring into003/008 ports/page entries.
Consume actual accepted011 exports. Do not copy or replace the compiler.

## Out of Scope

New business features/pages, Shared publication, database migrations, other service
implementation, live deployment, paid provider calls and WhatsApp delivery. U14
is009-owned;013 tests its composer handoff with the agreed stub, not real preview.

## Requirements

Read C4/C7/C9/C14–C17, the binding Studio UI design and each prerequisite contract
report. Use accepted source in dedicated launcher-resolved worktrees. Preserve
others' edits. New schema/semantic incompatibilities require architect resolution;
never weaken validation or alter an accepted wire contract merely to connect code.

## Work Items

- [ ] Map003 QueryValidationPort to011's actual compiler, including all bounded
  errors, schema identity and timeout/unavailable semantics. Remove no validation.
- [ ] Register only executable005/006/007 adapters and exact operation versions
  in003 publication availability and004 dispatch. Unavailable operations remain
  unavailable; descriptors alone never make tools publishable or callable.
- [ ] Implement008 StudioServices adapters using real003 reads/commands and011
  discovery/schema services, current accepted auth and real executor descriptors.
  Map fields/errors/CAS tokens without changing their defined meaning.
- [ ] Wire every U01–U13 page/read/action to those adapters, with server authorization
  on each request. No fixture flag, fake result or synthetic success in production.
- [ ] Reconcile service exports and routes; preserve C15 exact paths and008 UI.
  Provide docs/commerce-integration.md listing port -> module/export mappings,
  dependency revisions, runtime composition and test commands.
- [ ] Add one integrated suite and execute all I01–I08 below. Real application
  services must run; substitute only external provider/model transport and test
  infrastructure. Component-level fake publication/compiler services cannot pass.

## Interfaces / Contracts

C17 ports and003/008 contract documents are binding. Use current C7 operation IDs,
CAS and audit behavior, C14 definition validation and C16 release response contract.
No newly invented public endpoint or alternate command schema. Source compatibility
is demonstrated by execution, not matching types alone.

## Dependencies

- ARCH-020-COMMERCE-003
- ARCH-020-COMMERCE-004
- ARCH-020-COMMERCE-005
- ARCH-020-COMMERCE-006
- ARCH-020-COMMERCE-007
- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-011

Every prerequisite must be Complete and architect-accepted before execution.

## Enables

- ARCH-020-COMMERCE-009
- ARCH-020-GATEWAY-001
- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] I01: U03 -> U04 -> U09 -> U06 -> U07 -> U06 -> U09 -> U10 -> U11 with
  an arbitrary existing Admin Feature: author, validate, save, publish and activate
  a query through real services. Assert exact revision/member/hash/audit records.
- [ ] I02: invalid field, input mapping and schema version are rejected by the real
  compiler; missing compiler/adapter fails closed; zero publication writes/audits.
- [ ] I03: authenticated MCP resolve/list/call uses that release and005 query
  adapter against controlled provider transport; changed publication cannot alter
  a seeded existing grant. Seed grant as Background-owned; no WhatsApp required.
- [ ] I04:005/006/007 descriptors match installed executors and authoring fields;
  renamed policy tool dispatches correctly; unsupported/missing operation rejects.
- [ ] I05: role revocation, ADMIN publication denial, stale CAS, matching replay,
  changed-payload replay and duplicate clicks have the specified write/audit counts.
- [ ] I06: N01–N09/N12 and N13 composer portion run against real services, including
  dirty Back/Cancel, unknown outcome reconciliation and refresh-loss notice.
- [ ] I07: docs process outage preserves saved draft/schema editing; unavailable
  required schema blocks publication; neither path falls back to synthetic data.
- [ ] I08: production composition contains no fixture adapter. Run production build
  and direct protected endpoint tests; unavailable dependency returns typed failure,
  never mock success. Verify Google/development auth uses the accepted library.

## Validation

Deliver `test:arch020-integration` for bounded local integration fixtures and
`test:arch020-integration:database` for isolated PostgreSQL rehearsal. Run agent-owned
checks under repository policy; provide developer-owned database command, assertions
and actual evidence separately. Required database/I01/I05 evidence must exist before
acceptance, not be claimed from mocked transactions. Record each I01–I08 command,
expected effects, actual result and dependency revisions. No paid live-provider or
production customer data required. Terminal cross-repository testing remains separate.

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

Expected execution branch: task/ARCH-020-COMMERCE-013. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
