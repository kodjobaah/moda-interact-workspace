---
id: ARCH-002-ADMIN-006
architecture_id: ARCH-002
title: Protect admin mutations and privileged route handlers
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: pending
priority: 27
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-ADMIN-003
enables:
  - ARCH-002-ADMIN-007
created: 2026-08-31
updated: 2026-08-31
---

# Protect Admin Mutations and Privileged Route Handlers

## Objective

Enforce platform-admin authorisation at mutation/API boundaries themselves.
Page/layout protection is defence in depth and must not be treated as sufficient
mutation security.

## Current repository targets

At minimum, the current action:

```text
src/app/actions/tenant.ts::updateTenantAction
```

must call the server-side platform-admin mutation guard before validating or
mutating tenant state.

Inventory route handlers and future actions. Existing health endpoints are not
privileged mutation APIs and should remain bounded/public for infrastructure.

## Scope

- implement/use `requirePlatformAdminMutation()`;
- guard `updateTenantAction` before Prisma writes;
- inventory other server actions/route handlers;
- guard every privileged read/write API discovered;
- use 401/403 semantics appropriate to direct API handlers;
- preserve development bypass only under the accepted development invariant;
- prove forged/direct action requests cannot bypass page protection.

## Acceptance criteria

- [ ] anonymous direct invocation cannot update tenant status/settings;
- [ ] authenticated non-admin/inactive identity cannot update tenant state;
- [ ] active platform admin can perform existing mutations;
- [ ] dev bypass works for focused local/feature testing;
- [ ] `DEPLOYMENT_ENVIRONMENT_NAME=test|production` never bypasses;
- [ ] every privileged route handler discovered is independently guarded;
- [ ] health/auth protocol endpoints are not incorrectly converted into
      privileged admin endpoints;
- [ ] existing transaction/business validation remains unchanged.

- [ ] repository changes are committed/pushed and commit hash is recorded.

## Reference implementation

See `ADMIN-006-reference` for the current `updateTenantAction` guard placement.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Git / VCS

Not recorded yet.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None recorded yet.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
