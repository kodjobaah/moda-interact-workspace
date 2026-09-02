---
id: ARCH-002-ADMIN-007
architecture_id: ARCH-002
title: Add bounded platform-admin security audit logging
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: pending
priority: 28
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-ADMIN-005
  - ARCH-002-ADMIN-006
  - ARCH-002-SHARED-005
enables:
  - ARCH-002-ADMIN-008
created: 2026-08-31
updated: 2026-08-31
---

# Add Bounded Platform-Admin Security Audit Logging

## Objective

Record security-relevant administrator outcomes using the accepted shared logger
without logging credentials, session material or sensitive request payloads.

## Shared logging boundary

Consume exact accepted shared logging package version:

```text
@modainteract/moda-interact-shared@0.3.0
```

Application code imports the lightweight logging facade. Do not recreate the
shared redaction, OTel Logs provider or Loki transport.

## Required event classes

Examples:

```text
admin.auth.login_allowed
admin.auth.login_denied
admin.auth.logout
admin.auth.development_bypass
admin.authorization.denied
admin.tenant.update_succeeded
admin.tenant.update_failed
```

Use stable bounded event names.

Allowed body fields may include bounded operational identifiers such as:

```text
adminId
role
action
resourceType
resourceId
outcome
reasonCode
```

Do not log:

```text
passwords
OAuth codes/tokens
AUTH_SECRET
cookies
Authorization headers
raw JWT/session tokens
full request/response bodies
Google profile payloads
```

Do not promote `adminId`, tenant/resource IDs or other high-cardinality values to
Loki labels or metric dimensions.

## Development bypass audit

Development bypass events must clearly identify that the request used the
synthetic development principal, but must not create a production-capable auth
switch.

## Acceptance criteria

- [ ] security outcomes are logged with bounded event names;
- [ ] successful privileged mutation has an audit event;
- [ ] denied authorization has an audit event where operationally useful;
- [ ] no session/token/cookie/OAuth credential material is emitted;
- [ ] high-cardinality IDs remain body fields, not labels;
- [ ] logger/export failure does not change authorization/business correctness;
- [ ] no duplicate local generic logging implementation is introduced.

- [ ] repository changes are committed/pushed and commit hash is recorded.

## Reference implementation

See `ADMIN-007-reference/src/lib/auth/audit.ts`.

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
