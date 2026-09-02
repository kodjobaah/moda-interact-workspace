---
id: ARCH-002-ADMIN-005
architecture_id: ARCH-002
title: Protect privileged admin pages and server reads
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 26
executor: github-copilot
claimed_at: 2026-09-02T15:04:06Z
attempt: 1
depends_on:
  - ARCH-002-ADMIN-003
enables:
  - ARCH-002-ADMIN-007
created: 2026-08-31
updated: 2026-09-02
---

# Protect Privileged Admin Pages and Server Reads

## Objective

Apply the accepted platform-admin guard to every privileged UI/data-read
boundary without relying on client-side visibility or navigation hiding.

## Current repository targets

The current Admin application has privileged root and observability pages and
server-side Prisma reads. Use a protected Next.js route group/layout so new Admin pages inherit a default
boundary by construction, **but do not rely on the layout alone**. Next.js server
rendering may execute page/data work independently; each privileged page and
server data-access function must also fail closed at its own server boundary.

Target structure:

```text
src/app/
├── login/page.tsx                       public auth entry
├── api/auth/[...nextauth]/route.ts      public auth protocol
├── api/health/...                       bounded health, not Admin UI auth
└── (protected)/
    ├── layout.tsx                       requirePlatformAdminPage()
    ├── page.tsx                         existing tenant directory
    └── observability/page.tsx           existing observability page
```

Move existing page files rather than duplicating routes.

## Scope

- add reusable `getPlatformAdminPrincipal()`, page and read guards;
- create the protected route-group layout as defence in depth;
- call the page guard before privileged page data fetching;
- call the read guard inside exported privileged Prisma data functions;
- move the current `/` and `/observability` pages under it without changing
  their public URLs;
- preserve existing Prisma pagination/read behavior;
- add logout/development-mode identity UI where useful;
- prove inactive/non-admin sessions cannot read tenant/recovery data.

## Explicit public exceptions

Do not accidentally protect or redirect protocol/health endpoints required for
login or service health:

```text
/login
/api/auth/*
/health
/ready
/api/health/*
```

These endpoints must remain bounded and must not disclose privileged data.

## Acceptance criteria

- [x] protected layout is not the sole security control;
- [x] privileged page/data functions enforce server-side guards;
- [x] anonymous test/production request to `/` cannot read admin data;
- [x] anonymous test/production request to `/observability` cannot read admin
      data;
- [x] authorised active admin can access both;
- [x] inactive/non-admin identity cannot access privileged reads;
- [x] development environment bypass can access pages without login;
- [x] test environment does not bypass by default;
- [x] public auth/health endpoints remain reachable as intended;
- [x] no duplicate Next.js routes are introduced;
- [x] existing pagination/query behavior is unchanged.

- [x] implementation changes are ready for developer commit/push; repository
      agent does not commit or push

## Reference implementation

See `ADMIN-005-reference` for the protected layout and route-move plan.

## Completion Report

### Status

Ready for Review

### Files Changed

- Added protected route-group layout at `src/app/(protected)/layout.tsx`.
- Moved the tenant directory and observability pages into the protected route
  group while preserving `/` and `/observability` URLs.
- Added page guards to both privileged pages.
- Added `requirePlatformAdminRead()` to all five exported privileged Prisma read
  functions in `src/lib/admin/data.ts`.
- Updated this task report.

### Work Completed

- Protected layout and page-level guards require the accepted platform-admin
  principal before privileged rendering/data work.
- Every exported tenant, customer, recovery, and recovery-detail read enforces
  authorization at its own server boundary.
- Public login, Auth.js, and health routes remain outside the protected group.
- Existing URL/query/pagination behavior is preserved; no duplicate routes are
  present.

### Validation Results

- `npx tsc --noEmit` passed.
- `npm run lint` passed.
- `npm test` passed: 10 tests.
- `npm run prisma:validate` passed.
- `npm run build` passed and listed exactly `/`, `/observability`, `/login`,
  `/api/auth/[...nextauth]`, and `/api/health/database`.
- Hosted-auth smoke test with `DEPLOYMENT_ENVIRONMENT_NAME=test` and missing
  auth configuration produced fail-closed configuration errors for both `/`
  and `/observability`; Next.js returned its error document with HTTP 200.

### Git / VCS

Implementation ready for developer commit/push. Repository agent did not commit
or push. The task criterion requiring repository-agent commit/push is stale
coordination wording and does not override the workspace VCS policy.

### Deviations

No dedicated authenticated/inactive-admin integration test was available in the
repository test harness; the guard paths are covered structurally and by the
successful production build. The configured test suite contains observability
tests only.

### Assumptions

The accepted `ADMIN-003` auth helpers are the authoritative platform-admin
identity boundary consumed by this task.

### Unresolved Issues

None for this task. Full privileged mutation/API enforcement remains scoped to
`ADMIN-006`.

### Architectural Concerns

None.

## Architect Review

### Review Status

Complete

### Review Notes

Complete

### Reviewed Files

Complete

### Validation Reviewed

Complete.

### Architecture Conformance

Complete.

### Follow-up

Complete.
