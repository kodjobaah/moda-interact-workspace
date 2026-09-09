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
status: pending
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
updated: 2026-09-09
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
