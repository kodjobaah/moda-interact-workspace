---
id: ARCH-035-SYSTEM-TEST-005
architecture_id: ARCH-035
title: Certify end-to-end Woo merchant Support parity
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 91
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-020
  - ARCH-035-WOOCOMMERCE-016
enables: []
created: 2026-10-21
updated: 2026-10-21
---

# ARCH-035-SYSTEM-TEST-005: Certify end-to-end Woo merchant Support parity

## Architecture

Architecture ID: `ARCH-035`. Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`. Coordinator: `moda_architect`.

**Lifecycle:** Portable task definition from the developer-supplied 2026-10-21 workspace ZIP. Defined but **not materialised**, claimed, committed, pushed or accepted in the developer's workspace. The developer's canonical task launcher must establish physical parent and implementation worktrees and synchronize branches before execution.

## Objective

Independently validate the integrated Woo Support read, merchant send, Moda admin reply, mark-read and ARCH-046 SYSTEM notice display using real tenant-scoped API/database behaviour.

## Context

ARCH-035-SYSTEM-TEST-001 validates UI parity and cannot by itself certify functioning backend Support. This is a separate terminal functional validation after API-020 and WOOCOMMERCE-016 are architect-accepted. Shopify remains the behavioural reference.

## Scope

- Use the existing modular black-box system-test executors/fixtures/assertions/data and real hosted API/Postgres/WordPress test fixture boundaries.
- Test merchant Support thread creation, merchant send, admin reply appearing, translations, original/display toggle, SYSTEM notice, unread/mark-read and pagination.
- Test tenant isolation, denied/revoked installations, retry/idempotency, duplicate concurrent sends, queue-unavailable behaviour and Shopify regression evidence.

## Out of Scope

- No Support implementation changes; no Woo recovery/WhatsApp provider workflow activation.
- Do not claim manual LocalWP execution by repository agent; developer may supply separate LocalWP evidence.

## Requirements

- Run only after API-020 and WOOCOMMERCE-016 are Complete and architect-accepted; developer may perform manual checks before invocation.
- Exercise real permission boundaries and committed database records; do not treat fixture-only UI success as integrated certification.
- Keep system-test task terminal: no implementation task may depend on SYSTEM-TEST-005.

## Work Items

- [ ] [ ] Execute real Woo merchant round-trip Support case and verify stored message/translation state.
- [ ] [ ] Inject Moda admin reply plus consent SYSTEM notice and verify same-thread visibility/read state.
- [ ] [ ] Verify denial/race/duplicate/translation-queue failure cases with observability evidence.
- [ ] [ ] Produce reproducible test evidence and report any missing provider/manual checkpoints.

## Interfaces / Contracts

- Existing API-020 and WOOCOMMERCE-016 contracts; existing shared `support.MerchantSupportThread/Message` schema.

## Dependencies

- `ARCH-035-API-020` (must be architect-accepted Complete)
- `ARCH-035-WOOCOMMERCE-016` (must be architect-accepted Complete)

## Enables

None

## Acceptance Criteria

- [ ] Woo merchant-to-Moda and Moda-to-merchant two-way thread works with existing Admin Support system and tenant isolation.
- [ ] Mark-read/pagination/translation and ARCH-046 consent notice same-thread behaviour verified with real stored data.
- [ ] Retry/concurrency do not duplicate messages or billing usage; disabled/revoked/unauthorised attempts fail closed.
- [ ] Any lack of manual evidence or external runtime is explicitly reported; no invented pass.

## Validation

- [ ] Run reproducible integrated tests and `git diff --check`; preserve paths for DB/HTTP/WordPress assertions.
- [ ] Inspect supported 20-locale plugin build/translation evidence; report developer-only LocalWP evidence separately.

## Stop Condition

After all required Work Items, Acceptance Criteria and task-specific Validation are satisfied, update the task Completion Report and `status: review`, return to `moda_architect` and STOP. Do not perform dependent tasks, create new task implementation worktrees, merge or push main, or change `docs/decisions/**/_index.md`.

## Implementation Notes

This is a terminal integration acceptance task separate from ARCH-035-SYSTEM-TEST-001 (UI-only) and ARCH-046-SYSTEM-TEST-002 (blocked consent/recovery engine).

Start with `scripts/start-agent-task.py --prepare` through the normal `/moda-task` path. The prepared packet proves canonical parent/implementation worktree identity, synchronization and submodule state; record that packet in the Completion Report. Re-read the latest task and architect review before claiming. Use actual repository scripts. The architect in this externally supplied ZIP session has not created any Git branches or worktrees.

## Completion Report

### Status

Not Started — portable task definition only.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Inspect current canonical developer workspace when materialising; this source ZIP may lag task branches.

### Unresolved Issues

None identified at definition time.

### Architectural Concerns

None identified at definition time.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

Definition approved for handoff; no implementation has been accepted.
