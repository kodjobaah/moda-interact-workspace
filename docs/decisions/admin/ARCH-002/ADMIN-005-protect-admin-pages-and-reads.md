---
id: ARCH-002-ADMIN-005
architecture_id: ARCH-002
title: Protect privileged admin pages and server reads
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: pending
priority: 26
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

- [ ] protected layout is not the sole security control;
- [ ] privileged page/data functions enforce server-side guards;
- [ ] anonymous test/production request to `/` cannot read admin data;
- [ ] anonymous test/production request to `/observability` cannot read admin
      data;
- [ ] authorised active admin can access both;
- [ ] inactive/non-admin identity cannot access privileged reads;
- [ ] development environment bypass can access pages without login;
- [ ] test environment does not bypass by default;
- [ ] public auth/health endpoints remain reachable as intended;
- [ ] no duplicate Next.js routes are introduced;
- [ ] existing pagination/query behavior is unchanged.

- [ ] repository changes are committed/pushed and commit hash is recorded.

## Reference implementation

See `ADMIN-005-reference` for the protected layout and route-move plan.

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
