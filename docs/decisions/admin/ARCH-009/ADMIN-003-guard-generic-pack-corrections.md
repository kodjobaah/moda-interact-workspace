---
id: ARCH-009-ADMIN-003
architecture_id: ARCH-009
title: Prevent generic billing corrections from bypassing recovery-credit refund lifecycle
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-009-ADMIN-002
  - ARCH-007-ADMIN-004
enables:
  - ARCH-009-SYSTEM-TEST-001
created: 2026-09-09
updated: 2026-11-05
---

# ARCH-009-ADMIN-003

## Objective

Generic ARCH-007 correction must not bypass refund lifecycle.

## Server rule

Reload original UsageEvent from DB.

If durable metric:

```text
RECOVERY_CREDIT_PACK_PURCHASE
```

reject generic correction with stable semantic code:

```text
RECOVERY_CREDIT_PACK_REQUIRES_REFUND_WORKFLOW
```

No negative UsageEvent.

No correction audit.

Show i18n operator message and link to refund workflow when linked purchase
exists.

Browser-supplied metric ignored.

Other supported generic corrections remain unchanged.

## Tests

1. pack correction rejected;
2. no negative event;
3. no false correction audit;
4. ordinary correction still works;
5. forged client metric cannot bypass;
6. refund navigation shown;
7. i18n.

## Stop

Return review and STOP.

## Completion Report

### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
None
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
Pending
### Follow-up
None

## Architect supersession — 2026-11-05

Explicitly authorized by the developer. Superseded; do not claim or implement this legacy definition. Preserve all earlier attempt, implementation and review history; supersession does not accept the old implementation.

Binding replacements: [ARCH-010 lifecycle ownership](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md) removes the local cancellation state machine and assigns subscription cancellation to Shopify. [ARCH-015 Admin refund replacement](../ARCH-015/ADMIN-001-manual-refund-fallback.md) owns the current refund workflow and guarded provider settlement. Remaining Woo-specific support stays in ARCH-027-ADMIN-001.

Safety requirement retained for any future generic billing correction (including ARCH-007-ADMIN-004 if that capability proceeds): reload the durable original UsageEvent server-side; reject recovery-credit purchase corrections through the generic path, create neither negative event nor misleading correction audit, ignore browser-supplied metric claims, and direct the operator to the canonical refund workflow. Include focused tests before acceptance. This is a future capability constraint, not implementation authorization or a new claim. Current Admin event action is retry-only.
