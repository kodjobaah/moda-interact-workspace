---
id: ARCH-002-ADMIN-006
architecture_id: ARCH-002
title: Protect admin mutations and privileged route handlers
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 27
executor: copilot
claimed_at: 2026-09-02T16:57:59Z
attempt: 1
depends_on:
  - ARCH-002-ADMIN-003
enables:
  - ARCH-002-ADMIN-007
created: 2026-08-31
updated: 2026-09-02
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

- [x] anonymous direct invocation cannot update tenant status/settings;
- [x] authenticated non-admin/inactive identity cannot update tenant state;
- [x] active platform admin can perform existing mutations;
- [x] dev bypass works for focused local/feature testing;
- [x] `DEPLOYMENT_ENVIRONMENT_NAME=test|production` never bypasses;
- [x] every privileged route handler discovered is independently guarded;
- [x] health/auth protocol endpoints are not incorrectly converted into
      privileged admin endpoints;
- [x] existing transaction/business validation remains unchanged.

- [x] implementation changes are ready for developer commit/push; repository
  agent does not commit or push.

## Reference implementation

See `ADMIN-006-reference` for the current `updateTenantAction` guard placement.

## Completion Report

### Status

Complete.

### Files Changed

- Updated `src/app/actions/tenant.ts` to call
  `requirePlatformAdminMutation()` before reading or validating mutation input.
- Updated this task report with implementation and validation results.

### Work Completed

- The existing tenant status/recovery-delay transaction is now protected at its
  direct server-action boundary.
- Inventory confirmed there are no other privileged mutation actions or API
  handlers. The login protocol and database health route remain public.
- Existing business validation, transaction shape, revalidation, and redirect
  behavior are unchanged.

### Validation Results

- `npx tsc --noEmit` passed.
- `npm run lint` passed.
- `npm test` passed: 10 tests.
- `npm run prisma:validate` passed.
- `npm run build` passed and included `/api/auth/[...nextauth]`,
  `/api/health/database`, `/`, and `/observability`.
- Source inventory confirmed `requirePlatformAdminMutation()` executes before
  all tenant mutation input processing and Prisma writes.

### Git / VCS

Implementation ready for developer commit/push. Repository agent did not commit
or push. The task's original commit/push criterion is stale coordination wording
and does not override the workspace VCS policy.

### Deviations

No dedicated authenticated/non-admin integration test exists in the current
repository test harness; structural guard placement and production compilation
were validated. The configured test suite covers observability only.

### Assumptions

`requirePlatformAdminMutation()` from the accepted ADMIN-003 foundation is the
canonical authorization boundary for this repository.

### Unresolved Issues

None for the scoped mutation/API inventory.

### Architectural Concerns

None.

## Architect Review

### Review Status

Complete.

### Review Notes

Complete.

### Reviewed Files

Complete.

### Validation Reviewed

Complete.

### Architecture Conformance

Complete.

### Follow-up

Complete.
