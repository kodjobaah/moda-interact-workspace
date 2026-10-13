---
id: ARCH-038-ADMIN-001
architecture_id: ARCH-038
title: Manage Platform LIVE CommerceAgent budgets
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-038-DATABASE-001
enables:
  - ARCH-038-SYSTEM-TEST-001
created: 2026-10-13
updated: 2026-10-13
---
# Manage Platform LIVE CommerceAgent budgets

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_admin`
- Repository: `moda-interact-admin`

## Objective

Expose centrally audited LIVE CommerceAgent Platform deadline/output-token defaults in System Controls → Platform Policy.

## Context

The existing Platform Policy page edits billing/recovery safeguards. CommerceAgent execution controls belong in a clearly separated section backed by `CommerceModelPolicy` filtered to `context=LIVE` and `scope=PLATFORM`.

## Scope

- Add a distinct **CommerceAgent Execution Policy** section within System Controls → Platform Policy (not mixed with billing controls); show selected environment, required LIVE defaults, edit/schema versions and visible provenance.
- Build a reusable **schema-driven Admin budget-policy editor** for ADMIN-001/002/003 using an allowlisted `budgetSchemaVersion=1` descriptor for `deadlineMs` and `outputTokens`, with labels, units, descriptions, parsing, inline errors and optional scope-dependent Override/Inherit controls. Do not render arbitrary JSON keys as inputs.
- Display deadline in milliseconds alongside a readable seconds equivalent, and explain that `outputTokens` is per model invocation.
- Implement SUPER_ADMIN-only server reads and version-checked writes using DATABASE-001 schema.
- Record mandatory audit reason, actor and changed values in same durable mutation; expose a scope/environment-filtered **Policy History** view of existing `CommerceAuditEvent` records (timestamp, actor, reason and before/after values) with pagination/empty state.
- Handle missing defaults, stale edits, field-level validation errors and double-submit safely; present explicit conflict/reload recovery and disable the save action in flight.

## Out of Scope

- Do not add LIVE budgets to PlatformBillingPolicy or change its validation rules.
- Do not expose these controls to merchants or edit Preview budgets.

## Requirements

- Deadline means total turn milliseconds, tokens means per model call; both required positive safe integers.
- Server validates operational feasibility against documented Background execution envelope; unresolved envelope limitations must be raised rather than silently clipped.
- Required default persists as complete JSONB `budget` and is shown with provenance, budget schema version and edit version. Unknown schema versions/keys fail closed; neither required Platform field can be set to Inherit. Future JSON keys are editable only after the versioned descriptor and runtime support are updated.

## Work Items

- [ ] Add Admin read/mutation path using accepted database schema.
- [ ] Implement shared Admin field descriptors and reusable form/editor; integrate required Platform inputs, descriptions, effective source and in-flight protection in the existing Platform Policy page.
- [ ] Add paginated, scoped Commerce policy audit-history read/presentation using existing `CommerceAuditEvent`.
- [ ] Add authentication, scoped history, schema allowlist, audit, CAS/conflict reload, double-submit and field-validation regression tests.

## Interfaces / Contracts

Consumes ARCH-038-DATABASE-001 `CommerceModelPolicy` (`context=LIVE`, `scope=PLATFORM`, `budgetSchemaVersion=1`) Platform row and existing CommerceAuditEvent. Exposes repository-local reusable Admin editor/field descriptors for ARCH-038-ADMIN-002 and ADMIN-003; does not introduce a new cross-service contract or modify Shared/merchant-facing applications.

## Dependencies

- `ARCH-038-DATABASE-001`

## Enables

- `ARCH-038-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Only authorised SUPER_ADMIN can save; audit is transactional.
- [ ] Invalid/stale inputs render actionable errors without partial writes.
- [ ] Changing Platform default does not mutate Plan, Merchant or Preview overrides.
- [ ] Required numeric fields, descriptions, units and effective source display clearly; no raw JSON editing or unsupported keys.
- [ ] Scoped Policy History shows actor, time, reason and old/new changed budget fields without exposing other merchants; concurrent save shows a recoverable conflict.
- [ ] Reusable editor is available to downstream Admin Plan and Merchant tasks without duplicate field schemas.

## Validation

- [ ] Focused admin action and component tests
- [ ] Relevant typecheck/lint/build scripts
- [ ] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-ADMIN-001` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation

### Follow-up

None
