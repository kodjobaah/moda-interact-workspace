---
id: ARCH-002-DATABASE-001
architecture_id: ARCH-002
title: Add platform-admin identity registry
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-002-ADMIN-003
created: 2026-08-31
updated: 2026-08-31
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

- [ ] schema validates;
- [ ] migration is deterministic and deployable;
- [ ] active/role/provider identity fields exist;
- [ ] email is unique;
- [ ] provider subject can be initially null and later bound;
- [ ] no password/token/credential storage is introduced;
- [ ] ERD/schema documentation is updated where required;
- [ ] repository changes are committed/pushed and commit hash is recorded.

## Validation

- [ ] Prisma format/validate;
- [ ] migration SQL review;
- [ ] Prisma generate where repository convention requires it;
- [ ] clean migration validation according to the repository baseline;
- [ ] secret/credential field review.

## Reference Implementation

See:

```text
docs/decisions/database/ARCH-002/DATABASE-001-reference/
```

The reference is architect-supplied guidance, not a substitute for validation.

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
