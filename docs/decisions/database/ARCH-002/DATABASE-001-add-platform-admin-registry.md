---
id: ARCH-002-DATABASE-001
architecture_id: ARCH-002
title: Add platform-admin identity registry
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
status: complete
priority: 25
executor: github-copilot
claimed_at: 2026-09-02T12:30:00Z
attempt: 1
depends_on: []
enables:
  - ARCH-002-ADMIN-003
created: 2026-08-31
updated: 2026-09-02
---

# Add Platform-Admin Identity Registry

## Objective

Add the minimal durable Moda authorisation record required to identify, enable,
disable and role platform administrators without storing administrator
passwords or OAuth credentials.

## Scope

- add `PlatformAdminRole`;
- add `PlatformAdmin` in the existing `public` PostgreSQL schema;
- add a migration;
- retain a stable provider identity binding;
- allow an admin to be pre-provisioned by normalised email before first OAuth
  login;
- regenerate/validate Prisma and ERD artifacts according to database repository
  conventions.

## Required model

The architecture requires the equivalent of:

```prisma
enum PlatformAdminRole {
  ADMIN
  SUPER_ADMIN

  @@schema("public")
}

model PlatformAdmin {
  id              String            @id @default(cuid())
  provider        String            @default("google")
  providerSubject String?
  email           String            @unique
  displayName     String?
  role            PlatformAdminRole @default(ADMIN)
  active          Boolean           @default(true)
  lastLoginAt     DateTime?
  createdAt       DateTime          @default(now())
  updatedAt       DateTime          @updatedAt

  @@unique([provider, providerSubject])
  @@index([active, role])
  @@schema("public")
}
```

The owning database agent may make a Prisma-equivalent adjustment if required by
actual Prisma/PostgreSQL validation, but must preserve the semantics.

## Security requirements

Do not add:

```text
password
passwordHash
Google access token
Google refresh token
OAuth client secret
session cookie/token
```

The stable `providerSubject` is bound by the Admin application after verified
Google authentication. Pre-provisioning uses email + role only.

## Acceptance criteria

- [x] schema validates;
- [x] migration is deterministic and deployable;
- [x] active/role/provider identity fields exist;
- [x] email is unique;
- [x] provider subject can be initially null and later bound;
- [x] no password/token/credential storage is introduced;
- [x] ERD/schema documentation is updated where required;
- [x] implementation changes are ready for developer commit/push; repository agent does not commit or push.

## Validation

- [x] Prisma format/validate;
- [x] migration SQL review;
- [x] Prisma generate where repository convention requires it;
- [x] clean migration validation according to the repository baseline;
- [x] secret/credential field review.

## Reference Implementation

See:

```text
docs/decisions/database/ARCH-002/DATABASE-001-reference/
```

The reference is architect-supplied guidance, not a substitute for validation.

## Completion Report

### Status

Accepted / Complete

### Files Changed

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260902123000_add_platform_admin_registry/migration.sql`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `moda-interact-database/docs/generated/erd.png`
- `docs/decisions/database/ARCH-002/DATABASE-001-add-platform-admin-registry.md`

### Work Completed

- Added `PlatformAdminRole` with `ADMIN` and `SUPER_ADMIN` values in the
  existing `public` PostgreSQL schema.
- Added the `PlatformAdmin` registry with provider identity, nullable
  `providerSubject`, unique email, role, active state, login timestamp and
  created/updated timestamps.
- Added unique provider/provider-subject and active/role indexes while allowing
  pre-provisioned records to bind a provider subject after verified login.
- Added and reviewed a deterministic deployable migration without password,
  token, OAuth credential or session storage fields.
- Regenerated the Prisma ERD PlantUML and PNG artifacts.
- Repository agent did not commit or push.

### Validation Results

- `npx prisma format --schema prisma/schema.prisma`: passed.
- `npm run validate`: passed; Prisma schema is valid.
- `npx prisma generate --schema prisma/schema.prisma`: passed with Prisma
  Client 6.19.3.
- `npm run erd`: passed; PlantUML and PNG artifacts regenerated.
- `DATABASE_URL="postgresql://postgres:postgres@localhost:5432/moda_interact"
  npm run migrate:deploy`: passed; the new migration applied successfully to
  local PostgreSQL.
- The same local `npm run status`: passed; database schema is up to date.
- Scoped secret/credential review of the new model and migration: passed.
- `git diff --check`: passed.

### Git / VCS

Developer publication completed.

```text
repository: moda-interact-database
branch: main
commit: 9a286b7
subject: feat(database): added admin tables
remote: origin/main
working tree: clean
```

The repository agent did not commit or push; publication was performed by the
developer after architect acceptance.

### Deviations

None.

Architect review confirmed the submitted repository `package.json` already uses:

```text
prisma generate --schema prisma/schema.prisma
```

The earlier Completion Report statement that `prisma:generate` pointed to
`database/prisma/schema.prisma` was stale/inaccurate and is superseded by this
review record.

### Assumptions

Local migration validation used the repository-standard localhost development
database only; hosted deployment safety still depends on the normal
`prisma migrate deploy` rollout process.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted / Complete

### Review Notes

`ARCH-002-DATABASE-001` is architect-accepted.

The submitted Prisma model preserves the required platform-admin identity and
authorisation semantics:

```text
PlatformAdmin
  provider
  providerSubject?
  email
  displayName?
  role
  active
  lastLoginAt?
  createdAt
  updatedAt
```

The implementation introduces no administrator password, password hash, OAuth
access/refresh token, OAuth client secret, or session credential storage.

The nullable `providerSubject` together with the composite
`provider/providerSubject` unique constraint permits pre-provisioning before
first verified Google login while enforcing uniqueness after a provider subject
is bound.

The schema and generated migration match the architect reference semantics.

The generated ERD includes both `PlatformAdminRole` and `PlatformAdmin`.

### Reviewed Files

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260902123000_add_platform_admin_registry/migration.sql`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `moda-interact-database/docs/generated/erd.png`
- `moda-interact-database/package.json`
- `docs/decisions/database/ARCH-002/DATABASE-001-add-platform-admin-registry.md`
- `docs/decisions/database/ARCH-002/DATABASE-001-reference/files/database/platform-admin-schema.prisma`
- `docs/decisions/database/ARCH-002/DATABASE-001-reference/files/database/migration.sql`

### Validation Reviewed

The implementing agent reports successful:

```text
npx prisma format --schema prisma/schema.prisma
npm run validate
npx prisma generate --schema prisma/schema.prisma
npm run erd
npm run migrate:deploy
npm run status
git diff --check
```

Architect review independently confirmed:

- the submitted schema matches the required model semantics;
- the migration SQL matches the required schema;
- the ERD PlantUML contains `PlatformAdminRole` and `PlatformAdmin`;
- the generated ERD PNG is present and valid;
- the submitted `package.json` uses the correct `prisma/schema.prisma` path;
- no prohibited credential fields were introduced by this task.

### Architecture Conformance

Accepted.

The durable registry is suitable for consumption by `ARCH-002-ADMIN-003`.

### Follow-up

`ARCH-002-DATABASE-001` is Complete.

The publication gate for `ARCH-002-ADMIN-003` is satisfied.

Accepted database target:

```text
9a286b7 feat(database): added admin tables
```

`ADMIN-003` may update the Admin repository's nested database submodule to this
exact published commit and is promoted to Ready by `moda_architect`.

The repository agent must not perform the commit/push itself.
