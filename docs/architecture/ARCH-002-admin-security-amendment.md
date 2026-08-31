# ARCH-002 Amendment — Platform Admin Security Decomposition

Date: 2026-08-31

## Decision

The previous `ARCH-002-ADMIN-003` task combined identity-provider integration,
session handling, application-wide authorisation, mutation protection, audit
logging, deployment configuration and security regression testing.

That scope is replaced by a bounded security chain.

## Identity and credential model

Human platform administrators authenticate through Google using Auth.js.

Moda does **not** store administrator passwords or Google credentials in the
application database.

PostgreSQL stores only the Moda authorisation record:

```text
PlatformAdmin
    id
    provider
    providerSubject
    email
    displayName
    role
    active
    lastLoginAt
    createdAt
    updatedAt
```

Google proves identity. Moda decides whether that identity is an authorised
platform administrator.

The first login for a pre-provisioned active email may bind the stable Google
subject to that `PlatformAdmin` record. Subsequent logins must match the bound
provider subject.

## Sessions

Use Auth.js JWT sessions so Moda does not require Auth.js account/session tables.
The session lifetime should be bounded to a normal administrator work period
(reference implementation: eight hours).

Every privileged request must still resolve the current `PlatformAdmin` record
and require `active=true`; a stale session must not by itself preserve access
after an administrator is disabled.

## Development authentication bypass

Local development and focused tests may bypass authentication only under this
exact invariant:

```text
resolved deployment environment == development
AND
NODE_ENV != production
```

The canonical deployment variable is:

```text
DEPLOYMENT_ENVIRONMENT_NAME
```

Resolution falls back to `NODE_ENV` when the explicit value is absent.

Consequences:

```text
development -> login is skipped and a synthetic local SUPER_ADMIN principal is used
test        -> authentication required by default
production  -> authentication required
```

A test process may explicitly set:

```text
DEPLOYMENT_ENVIRONMENT_NAME=development
```

to exercise non-authenticated feature tests.

If a production Node process is configured with deployment environment
`development`, the application must fail closed rather than bypassing auth.

No generic `DISABLE_AUTH=true` or equivalent production-capable bypass is
permitted.

## Public and protected boundaries

Unauthenticated operational endpoints required by Render/gateway health checks
remain outside the platform-admin page boundary and must expose no privileged
data:

```text
/api/auth/*        Auth.js protocol endpoint
/login             login page
/health            liveness, when implemented
/ready             readiness, when implemented
/api/health/*      existing bounded health endpoint(s)
```

All administrative UI/data pages belong under a protected server layout.
Server actions and privileged API handlers must additionally enforce
authorisation themselves because page/layout protection is not a mutation
security boundary.

## Deployment secrets

Test and production use separate values for:

```text
AUTH_SECRET
AUTH_GOOGLE_ID
AUTH_GOOGLE_SECRET
AUTH_URL
```

No admin email/password is stored as a deployment secret merely to implement
login.

`AUTH_URL` is environment-specific, e.g. test Admin host versus
`https://admin.modainteract.com` in production.

## Task chain

```text
ARCH-002-DATABASE-001  Add PlatformAdmin registry
ARCH-002-ADMIN-003     Google/Auth.js + session + development bypass
ARCH-002-ADMIN-005     Protect privileged pages and server reads
ARCH-002-ADMIN-006     Protect mutations and privileged route handlers
ARCH-002-ADMIN-007     Add bounded security/audit logging
ARCH-002-ADMIN-008     Final security regression/deployment gate
```

`ARCH-002-ADMIN-004` (Grafana presentation) and production Admin host exposure
must depend on the final `ADMIN-008` gate, not merely the authentication
foundation.
