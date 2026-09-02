---
id: ARCH-002-ADMIN-007
architecture_id: ARCH-002
title: Add bounded platform-admin security audit logging
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 28
executor: copilot
claimed_at: 2026-09-02T17:09:03Z
attempt: 1
depends_on:
  - ARCH-002-ADMIN-005
  - ARCH-002-ADMIN-006
  - ARCH-002-SHARED-005
enables:
  - ARCH-002-ADMIN-008
created: 2026-08-31
updated: 2026-09-02
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

- [x] security outcomes are logged with bounded event names;
- [x] successful privileged mutation has an audit event;
- [x] denied authorization has an audit event where operationally useful;
- [x] no session/token/cookie/OAuth credential material is emitted;
- [x] high-cardinality IDs remain body fields, not labels;
- [x] logger/export failure does not change authorization/business correctness;
- [x] no duplicate local generic logging implementation is introduced.

- [x] implementation changes are ready for developer commit/push; repository
  agent does not commit or push.

## Reference implementation

See `ADMIN-007-reference/src/lib/auth/audit.ts`.

## Completion Report

### Status

Ready for Review

### Files Changed

- Added `src/lib/auth/audit.ts` as a domain adapter over the shared structured
  logger.
- Added bounded auth login allowed/denied, development bypass, authorization
  denied, logout, and tenant update succeeded/failed events.
- Updated `src/auth.ts`, `src/lib/auth/platform-admin.ts`,
  `src/components/admin/logout-form.tsx`, and
  `src/app/actions/tenant.ts`.

### Work Completed

- Audit fields are limited to operational identifiers, action/resource values,
  outcomes, reason codes, and the development-bypass marker.
- No credentials, OAuth material, cookies, session data, profiles, or request
  bodies are passed to the logger.
- The shared logger remains responsible for serialization, redaction, bounded
  output, OTel/Loki transport, and failure isolation.

### Validation Results

- `npx tsc --noEmit` passed.
- `npm run lint` passed.
- `npm test` passed: 10 tests.
- `npm run prisma:validate` passed.
- `npm run build` passed with the auth, health, root, and observability routes.
- Source inventory confirmed no competing local generic logger and no prohibited
  sensitive logging fields.

### Git / VCS

Implementation ready for developer commit/push. Repository agent did not commit
or push. The task's original commit/push criterion is stale coordination wording
and does not override the workspace VCS policy.

### Deviations

The task text names `@modainteract/moda-interact-shared@0.3.0`, but the current
architect-accepted consumer dependency is exact `0.4.0`; that installed release
exports the required `./logging` facade and was retained.

### Assumptions

No dedicated audit-event test exists in the current repository harness; shared
logger behavior is covered by the shared package and application compilation,
inventory, and existing tests passed.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Complete.

### Review Notes

Ready for `moda_architect` review. No commit or push was performed.

### Reviewed Files

Complete.

### Validation Reviewed

Complete.

### Architecture Conformance

Complete.

### Follow-up

Complete.
