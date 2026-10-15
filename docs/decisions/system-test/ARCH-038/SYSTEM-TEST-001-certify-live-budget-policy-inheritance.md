---
id: ARCH-038-SYSTEM-TEST-001
architecture_id: ARCH-038
title: Certify LIVE execution budget precedence and runtime
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-038-DATABASE-001
  - ARCH-038-ADMIN-001
  - ARCH-038-ADMIN-002
  - ARCH-038-ADMIN-003
  - ARCH-038-BACKGROUND-001
enables: []
created: 2026-10-13
updated: 2026-10-14
---
# Certify LIVE execution budget precedence and runtime

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_system_test`
- Repository: `moda-interact-system-test`

## Objective

Independently certify Admin-controlled LIVE Platform/Price Plan/Merchant limits through real Background CommerceAgent admission and Shared execution.

## Context

LIVE policy is cross-repository and must be verified after implementation acceptance and the developer manual checkpoint, rather than used to gate implementation.

## Scope

- Use disposable seeded shops, subscriptions, pricing plans and `CommerceModelPolicy` (`LIVE`) rows; exercise different effective deadline/token sources.
- Verify SUPER_ADMIN-only writes and no merchant-facing mutation; test cross-tenant isolation.
- Black-box test the Admin Platform Policy, Merchant Pricing Plan builder and Tenant Directory editors: field labels/units/help, independent Override/Inherit controls, effective-source display and scoped history; verify single-flight submission and reloadable conflicts.
- Run Background black-box execution or the closest available integrated contract harness, covering worker/deadline behaviour and **per-execution** LIVE policy resolution (not a retry-wide snapshot). Preserve separate PREVIEW Test Conversation snapshot certification in SYSTEM-TEST-002.
- Verify production SDK HTTP request orchestration against local AI Mock with dummy credentials, strict loopback routing and no paid AI-provider calls.
- Capture evidence, exact commands, fixture IDs, failures and cleanup.

## Out of Scope

- Do not modify production business implementation while testing.
- No dependency from implementation tasks back to this task.

## Requirements

- Validate independent sparse JSON-key precedence, rejected explicit null/unknown JSON schema versions, scope-owner checks and missing/current/inactive/pending subscription cases.
- Verify that plan changes and concurrent admin edits do not alter a **running** LIVE invocation, but a later execution (including retry of the same inbound identity) resolves current policy values. Do not require persisted LIVE retry snapshots.
- Verify no silent deadline cap/lease mismatch; require corrected owning implementation if failing.

## Work Items

- [ ] Prepare disposable fixtures and integrated harness.
- [ ] Execute precedence, authorisation, isolation, deadline and create/edit/retry policy-refresh matrix.
- [ ] Exercise request ordering, model ID, token limits, tool definitions and tool-result forwarding through the real Shared runner/OpenRouter SDK against local AI Mock with fail-closed provider egress.
- [ ] Record and review reproducible evidence.

## Interfaces / Contracts

Terminal architecture certification of DATABASE-001 + ADMIN-001/002/003 + BACKGROUND-001.

## Dependencies

- `ARCH-038-DATABASE-001`
- `ARCH-038-ADMIN-001`
- `ARCH-038-ADMIN-002`
- `ARCH-038-ADMIN-003`
- `ARCH-038-BACKGROUND-001`

## Enables

None

## Acceptance Criteria

- [ ] All mandated LIVE cases pass with reproducible evidence.
- [ ] No cross-tenant budget leakage; no unauthorised merchant edits.
- [ ] Effective value and provenance agree between policy, runtime and logs; each LIVE invocation retains its own values, while later retries may use edited policy.
- [ ] All automated model requests go to the loopback AI Mock server (dummy credentials); no paid provider access or fallback is possible.
- [ ] Admin Platform/Plan/Merchant forms show correct per-field values, sources, versioned validation and scope-filtered audit history; duplicate submit/conflict recovery does not create duplicate mutations.

## Validation

- [ ] Integrated PostgreSQL/Background LIVE policy matrix with disposable launcher-forced `DEPLOYMENT_ENVIRONMENT_NAME=test` and matching TEST policy rows
- [ ] Auth/isolation/plan-change and in-flight-versus-retry-current-policy regression
- [ ] Local AI Mock + real OpenRouter SDK HTTP request-orchestration and blocked-external-provider verification
- [ ] Artifact and evidence audit
- [ ] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-SYSTEM-TEST-001` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

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
