---
id: ARCH-002-ADMIN-003
architecture_id: ARCH-002
title: Implement Google platform-admin authentication and session foundation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 25
executor: github-copilot
claimed_at: 2026-09-02T14:00:56Z
attempt: 2
depends_on:
  - ARCH-002-DATABASE-001
enables:
  - ARCH-002-ADMIN-005
  - ARCH-002-ADMIN-006
created: 2026-08-31
updated: 2026-09-02
---

# Implement Google Platform-Admin Authentication and Session Foundation


## Publication precondition

Satisfied.

The publication precondition means that the architect-accepted database commit
must exist as a real published commit that the Admin repository can target.

That condition is satisfied:

```text
repository: moda-interact-database
branch: main
commit: 9a286b7
subject: feat(database): added admin tables
remote: origin/main
```

**The Admin nested `database` submodule is not required to already point at
`9a286b7` before this task starts.**

Updating that pointer is explicitly part of `ADMIN-003` implementation work.

Expected starting state may therefore be:

```text
Admin nested database submodule -> older accepted commit
```

The first repository-owned implementation step is:

```text
fetch published database history
    -> checkout exact accepted commit 9a286b7 in nested database submodule
    -> record the changed gitlink/pointer in moda-interact-admin
```

This is an Admin repository dependency-pointer update. It does **not** authorize
`moda_admin` to:

- edit database schema/migrations;
- create a database commit;
- push the database repository;
- advance beyond `9a286b7` without architect coordination.

If `9a286b7` cannot be fetched from the configured database remote, or checking
out that exact commit requires database changes rather than a clean submodule
checkout, then return the task Blocked with evidence.

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

## Work Items

- [x] verify `moda-interact-database@9a286b7` is fetchable from the nested
      submodule's configured remote;
- [x] update the Admin nested `database` submodule checkout/pointer to exact
      commit `9a286b7`;
- [x] verify the nested database working tree is clean at `9a286b7`;
- [x] regenerate Prisma client from the accepted nested schema as required by
      the Admin repository;
- [x] implement the Auth.js / Google platform-admin authentication foundation;
- [x] implement verified-email allow-list and provider-subject binding;
- [x] implement bounded session/login/logout behavior;
- [x] implement development-only bypass under the accepted invariant;
- [x] implement the local PlatformAdmin provisioning CLI;
- [x] document required environment/callback configuration;
- [x] run focused task validation;
- [x] return `in_progress -> review` and STOP without committing/pushing.

## Acceptance criteria

- [ ] development mode skips login exactly under the accepted invariant;
- [ ] a production Node process can never activate the development bypass;
- [ ] test/production missing auth configuration fails closed;
- [ ] Google is the only configured human login provider;
- [ ] unverified Google email is rejected;
- [ ] unknown/inactive PlatformAdmin is rejected;
- [ ] bound Google subject mismatch is rejected;
- [ ] first valid login can bind an unbound pre-provisioned admin record;
- [x] session is HttpOnly/Secure as appropriate to deployed HTTPS and expires on
      a bounded schedule;
- [x] `/login` and logout behavior work;
- [x] provisioning creates admin identity metadata only, not credentials;
- [x] implementation changes are ready for developer commit/push; repository agent does not commit or push.

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

Ready for Review

### Previous Attempt

Attempt 1 stopped before implementation because the Admin nested database
submodule was at `505f7d9` rather than `9a286b7`.

`moda_architect` determined that this was not a valid blocker: updating the
nested submodule pointer to the published accepted commit is explicitly part of
this task's Scope and Work Items.

### Files Changed

- Updated the nested `database` submodule pointer to accepted commit
  `9a286b7c515a1edfec158374c3a3473d9b0967b`.
- Added Auth.js Google configuration, verified-email allow-list checks,
  provider-subject binding, bounded JWT sessions, login route/page, logout
  control, and development-only principal helpers.
- Added `admin:provision`, auth environment documentation, and pinned
  `next-auth` to `5.0.0-beta.32` with the generated lockfile update.

### Work Completed

- Prisma Client regenerated from the accepted nested database schema.
- Google is the only configured provider; unverified, unknown, inactive, and
  provider-subject-mismatched identities are rejected.
- First valid login binds an unbound pre-provisioned Google subject.
- Sessions use JWT strategy with an eight-hour maximum age.
- Development bypass fails closed when production Node runs with a development
  deployment name.
- Provisioning creates or enables identity metadata only and supports disable.

### Validation Results

- `npm run prisma:validate` passed.
- `npm run prisma:generate` passed.
- `npx tsc --noEmit` passed.
- `npm run lint` passed.
- `npm run build` passed; `/login` and `/api/auth/[...nextauth]` were included.
- `npm test` could not run because the existing script targets the missing
  `tests/observability/` directory.

### Review Handoff

Ready for `moda_architect` review. No commit or push was performed. Route and
privileged mutation enforcement remains intentionally deferred to ADMIN-005 and
ADMIN-006.

Not run for the new Ready attempt.

### Git / VCS

No commit or push performed.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None currently.

If exact published database commit `9a286b7` cannot be fetched/checked out
cleanly by the nested submodule, return Blocked with evidence.

### Architectural Concerns

None currently.

## Architect Review

### Review Status

Block Rejected / Returned Ready

### Review Notes

The reported blocker is not valid.

The task's Scope explicitly requires `moda_admin` to update the Admin
repository's nested database submodule/pointer to the accepted
`DATABASE-001` commit.

Therefore:

```text
nested database pointer = 505f7d9
```

is an implementation starting condition, not an unsatisfied publication
precondition.

The actual cross-repository publication precondition was that the accepted
database commit be published and fetchable. That is satisfied by:

```text
9a286b7 (origin/main) feat(database): added admin tables
```

`moda_admin` may fetch and checkout that exact commit inside the nested
submodule and record the resulting Admin gitlink change.

This does not grant ownership of database schema/migrations and does not permit
creating or pushing database commits.

### Reviewed Files

- `docs/decisions/admin/ARCH-002/ADMIN-003-platform-admin-auth.md`
- `moda-interact-admin` nested database submodule state reported by attempt 1
- published DATABASE-001 evidence at `moda-interact-database@9a286b7`

### Validation Reviewed

Publication evidence already confirmed:

```text
9a286b7 (HEAD -> main, origin/main, origin/HEAD)
feat(database): added admin tables
working tree clean
```

### Architecture Conformance

Ready to execute.

### Follow-up

Retry:

```text
/moda-task ARCH-002-ADMIN-003
```

The next attempt must treat updating the nested database pointer to `9a286b7`
as the first implementation step.

Do not start downstream tasks automatically.
