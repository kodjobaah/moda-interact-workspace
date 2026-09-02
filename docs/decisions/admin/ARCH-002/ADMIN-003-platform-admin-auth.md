---
id: ARCH-002-ADMIN-003
architecture_id: ARCH-002
title: Implement Google platform-admin authentication and session foundation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: pending
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-DATABASE-001
enables:
  - ARCH-002-ADMIN-005
  - ARCH-002-ADMIN-006
created: 2026-08-31
updated: 2026-08-31
---

# Implement Google Platform-Admin Authentication and Session Foundation

## Objective

Implement the human platform-admin identity/session foundation using Google
OAuth through Auth.js and the accepted `PlatformAdmin` registry.

This task establishes identity and session mechanics. Application-wide page and
mutation coverage are separate tasks.

## Authentication decision

```text
Google OAuth
    -> Auth.js
    -> verified Google identity
    -> PlatformAdmin allow-list
    -> secure bounded session
```

Moda does not store administrator passwords.

Use Auth.js without its database adapter/account/session schema. The reference
implementation uses a bounded JWT session and keeps Moda authorisation in the
existing Prisma database through `PlatformAdmin`.

Pin the exact compatible `next-auth` package version selected during
implementation; do not leave an unbounded authentication dependency range.

## Development bypass

Authentication/login must be skipped only when:

```text
DEPLOYMENT_ENVIRONMENT_NAME=development
AND
NODE_ENV != production
```

When `DEPLOYMENT_ENVIRONMENT_NAME` is absent, resolve the local environment from
`NODE_ENV`.

Required behavior:

```text
npm run dev
    -> development bypass
    -> no Google login required
    -> synthetic local SUPER_ADMIN principal

NODE_ENV=test + DEPLOYMENT_ENVIRONMENT_NAME=development
    -> development bypass may be used by focused feature tests

DEPLOYMENT_ENVIRONMENT_NAME=test
    -> real authentication required

DEPLOYMENT_ENVIRONMENT_NAME=production
    -> real authentication required

NODE_ENV=production + DEPLOYMENT_ENVIRONMENT_NAME=development
    -> fail closed
```

Do not add a generic `DISABLE_AUTH`, `SKIP_AUTH` or equivalent switch that can
be enabled in production.

## Scope

- update the Admin repository's database submodule/pointer to the accepted
  `DATABASE-001` commit;
- add Auth.js Google authentication;
- add `/api/auth/[...nextauth]`;
- add branded `/login` page;
- add logout behavior;
- implement secure bounded session behavior;
- require Google verified email;
- allow only active pre-provisioned `PlatformAdmin` identities;
- bind `providerSubject` on the first valid login and require the same subject
  on later logins;
- add a local provisioning CLI for creating/enabling the first `PlatformAdmin`
  record by normalised email/role;
- implement the development-only bypass helper and synthetic local principal;
- document environment names and Google callback URLs.

## Out of scope

- protecting every Admin page/data read (`ADMIN-005`);
- protecting server actions/privileged API handlers (`ADMIN-006`);
- final security audit logging (`ADMIN-007`);
- final cross-boundary security regression gate (`ADMIN-008`);
- gateway host routing;
- Grafana embedding;
- storing administrator passwords.

## Required runtime configuration

For `test` and `production`:

```text
AUTH_SECRET
AUTH_GOOGLE_ID
AUTH_GOOGLE_SECRET
AUTH_URL
DEPLOYMENT_ENVIRONMENT_NAME
```

`AUTH_URL` is environment-specific.

Production callback:

```text
https://admin.modainteract.com/api/auth/callback/google
```

The test callback uses the test Admin hostname.

No secret value is committed.

## Acceptance criteria

- [ ] development mode skips login exactly under the accepted invariant;
- [ ] a production Node process can never activate the development bypass;
- [ ] test/production missing auth configuration fails closed;
- [ ] Google is the only configured human login provider;
- [ ] unverified Google email is rejected;
- [ ] unknown/inactive PlatformAdmin is rejected;
- [ ] bound Google subject mismatch is rejected;
- [ ] first valid login can bind an unbound pre-provisioned admin record;
- [ ] session is HttpOnly/Secure as appropriate to deployed HTTPS and expires on
      a bounded schedule;
- [ ] `/login` and logout behavior work;
- [ ] provisioning creates admin identity metadata only, not credentials;
- [ ] package/schema/submodule changes are committed and pushed.

## Reference implementation

See:

```text
docs/decisions/admin/ARCH-002/ADMIN-003-reference/
```

It is based on the current Next.js 16 Admin repository and provides the auth
module, environment gate, login page, auth handler, logout component and
provisioning script.

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
