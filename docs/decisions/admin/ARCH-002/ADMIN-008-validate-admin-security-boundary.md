---
id: ARCH-002-ADMIN-008
architecture_id: ARCH-002
title: Validate platform-admin security and deployment contract
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: pending
priority: 29
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-ADMIN-003
  - ARCH-002-ADMIN-005
  - ARCH-002-ADMIN-006
  - ARCH-002-ADMIN-007
enables:
  - ARCH-002-GATEWAY-007
  - ARCH-002-GATEWAY-003
  - ARCH-002-ADMIN-004
created: 2026-08-31
updated: 2026-08-31
---

# Validate Platform-Admin Security and Deployment Contract

## Objective

Act as the final Admin application security gate before public Admin host routing
or live internal Grafana presentation is enabled.

This task primarily validates and closes gaps; it must not redesign the accepted
authentication model unless evidence requires architect review.

## Required security matrix

Validate at minimum:

```text
1. NODE_ENV=development, deployment=development
   -> auth/login bypassed
   -> synthetic development SUPER_ADMIN works

2. NODE_ENV=test, deployment=development
   -> explicit development bypass works for focused tests

3. NODE_ENV=test, deployment=test
   -> authentication required
   -> missing auth config fails closed

4. NODE_ENV=production, deployment=production
   -> authentication required
   -> missing auth config fails closed

5. NODE_ENV=production, deployment=development
   -> application fails closed
   -> never bypasses

6. valid Google + active bound/unbound PlatformAdmin
   -> allowed according to binding rules

7. valid Google + unknown/inactive admin
   -> denied

8. provider-subject mismatch
   -> denied

9. direct server-action invocation without admin
   -> denied before mutation

10. /health, /ready and bounded /api/health/*
    -> remain usable by infrastructure without exposing admin data
```

## Deployment contract

Document non-secret environment names for gateway/Render topology:

```text
DEPLOYMENT_ENVIRONMENT_NAME
AUTH_URL
AUTH_GOOGLE_ID
```

Secret environment names:

```text
AUTH_SECRET
AUTH_GOOGLE_SECRET
DATABASE_URL
```

Values remain environment-specific and are never committed.

Production Google callback:

```text
https://admin.modainteract.com/api/auth/callback/google
```

The test environment must have its own Admin host/OAuth callback and its own
secret values.

## Validation

- [ ] repository test suite;
- [ ] lint/typecheck as applicable;
- [ ] production build;
- [ ] security matrix above;
- [ ] cookie attributes/expiry review;
- [ ] no credential/session logging review;
- [ ] environment isolation review;
- [ ] direct server-action/API rejection tests;
- [ ] admin database disable/revocation behavior;
- [ ] Google callback/host documentation review;
- [ ] `git status --short` and commit/push evidence.

## Acceptance criteria

- [ ] all security matrix cases pass;
- [ ] no production-capable authentication bypass exists;
- [ ] every current privileged UI/read/mutation boundary is protected;
- [ ] admin deactivation takes effect even while a browser holds an otherwise
      valid session;
- [ ] no admin password is stored by Moda;
- [ ] required Render/Google configuration contract is documented;
- [ ] task can safely enable `GATEWAY-007`, `GATEWAY-003` and `ADMIN-004`.

- [ ] repository changes are committed/pushed and commit hash is recorded.

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
