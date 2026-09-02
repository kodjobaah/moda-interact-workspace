---
id: ARCH-002-ADMIN-008
architecture_id: ARCH-002
title: Validate platform-admin security and deployment contract
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 29
executor: copilot
claimed_at: 2026-09-02T18:00:00Z
attempt: 4
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
updated: 2026-09-02
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

- [x] repository test suite;
- [x] lint/typecheck as applicable;
- [x] production build;
- [x] security matrix above;
- [x] cookie attributes/expiry review;
- [x] no credential/session logging review;
- [x] environment isolation review;
- [x] direct server-action/API rejection tests;
- [x] admin database disable/revocation behavior;
- [x] Google callback/host documentation review;
- [x] `git status --short` review; commit/push is developer-owned.

## Acceptance criteria

- [x] all security matrix cases pass;
- [x] no production-capable authentication bypass exists;
- [x] every current privileged UI/read/mutation boundary is protected;
- [x] admin deactivation takes effect even while a browser holds an otherwise
      valid session;
- [x] no admin password is stored by Moda;
- [x] required Render/Google configuration contract is documented;
- [x] task can safely enable `GATEWAY-007`, `GATEWAY-003` and `ADMIN-004`.

- [x] implementation/validation changes are ready for developer commit/push; repository agent does not commit or push.

## Architect changes requested — attempt 2

Attempt 1's implementation changes are retained.

The remaining gap is executable final-gate security evidence.

`ADMIN-008` is the final Admin application security/deployment gate. Source
inspection is useful evidence, but it is not sufficient for matrix cases that
this task explicitly exists to prove before enabling public Admin routing and
live observability presentation.

Attempt 2 must add or extend a focused validation harness that proves, at
minimum:

```text
environment matrix
  NODE_ENV=development + deployment=development -> bypass allowed
  NODE_ENV=test        + deployment=development -> explicit test bypass allowed
  NODE_ENV=test        + deployment=test        -> auth required / missing config fails closed
  NODE_ENV=production  + deployment=production  -> auth required / missing config fails closed
  NODE_ENV=production  + deployment=development -> hard fail closed / no bypass

identity matrix
  active bound PlatformAdmin             -> allowed
  active unbound PlatformAdmin           -> first valid subject binding allowed
  unknown PlatformAdmin                  -> denied
  inactive PlatformAdmin                 -> denied
  provider-subject mismatch              -> denied

revocation
  valid existing session/JWT
      -> PlatformAdmin becomes inactive
      -> next privileged principal resolution is denied

direct mutation boundary
  no valid admin principal
      -> updateTenantAction rejected
      -> rejection occurs before FormData consumption / Prisma mutation

public infrastructure routes
  /health
  /ready
  bounded /api/health/*
      -> remain unauthenticated
      -> expose bounded health data only

session/cookie contract
  eight-hour session bound
  hosted HTTPS cookie security attributes reviewed/proved
  no production-capable bypass

deployment/OAuth contract
  production callback is admin.modainteract.com
  test host/callback is distinct
  secret and non-secret environment names remain isolated
```

A bounded test seam/mock/fixture is acceptable where live Google OAuth is not
appropriate. The harness must validate the accepted security model rather than
redesign it.

If a small testability seam is required, keep it local to the accepted
`ADMIN-003/005/006/007` design and record it in the Completion Report.

After implementing the focused validation, rerun:

```text
TypeScript
lint
Prisma validation
repository tests
production build
focused ADMIN-008 security validation
```

Then transition:

```text
in_progress -> review
```

and STOP without committing or pushing.

## Architect changes requested — attempt 3

Attempt 2 materially improved the validation harness and its implementation
changes are retained.

The remaining gap is narrow: several final-gate checks still validate a
parallel/pure representation or source ordering rather than executing the
accepted production security path.

Attempt 3 must close the following four items.

### 1. Existing-session revocation must execute principal resolution

Required evidence:

```text
valid hosted session/JWT identity
  -> PlatformAdmin load returns active + matching subject
  -> privileged principal resolution succeeds

same session/JWT identity
  -> PlatformAdmin load now returns inactive
  -> privileged principal resolution is denied
```

A small injectable/testable resolver seam is acceptable, but the seam must be
the same code path used by `getPlatformAdminPrincipal()` rather than a separate
test-only policy implementation.

### 2. Direct mutation rejection must be executable

Required evidence:

```text
updateTenantAction(...)
  -> no authorized principal
  -> PlatformAdminUnauthorizedError (or equivalent denial)
  -> FormData fields are not consumed
  -> Prisma transaction/mutation is not invoked
```

A bounded dependency-injection/module-mock seam is acceptable. A textual
`indexOf()`/regex ordering assertion alone is not sufficient for this final
gate.

### 3. Google unbound/bound identity tests must exercise the real sign-in
authorization path

The current test executes `canBindPlatformAdmin(...)`, but `auth.ts` does not
use that helper for its actual first-binding transaction.

Required evidence must cover the production authorization/binding behavior:

```text
active + already bound + matching subject -> allowed
active + unbound -> single subject binding succeeds -> allowed
active + unbound -> competing/raced binding resolves to same subject -> allowed
unknown -> denied
inactive -> denied
bound + mismatched subject -> denied
```

A small extracted authorization function with injected PlatformAdmin
persistence is acceptable if `auth.ts` calls that same function.

Do not create a parallel function used only by tests.

### 4. Hosted cookie/session contract must be closed explicitly

The current report says:

```text
Auth.js v5 JWT defaults provide HttpOnly cookies and Secure cookies ...
```

as an assumption while the task's cookie validation remains unchecked.

Close this by either:

- executable/configuration evidence against the actual accepted Auth.js
  configuration/dependency behavior; or
- an explicit hosted cookie configuration owned by the application, with
  focused tests proving the required security attributes.

Do not duplicate Auth.js session implementation.

The eight-hour `maxAge` remains required.

### Validation

After these focused changes, rerun:

```text
focused ADMIN-008 security suite
full repository tests
TypeScript
lint
Prisma validation
production build
```

Then check every validation/acceptance box that is actually proved, transition
`in_progress -> review`, and STOP without committing or pushing.

## Architect changes requested — attempt 4

Attempt 3 closes the mutation-boundary and hosted cookie/session gaps.

Only **two executable-evidence gaps remain**. Do not broaden this task.

### 1. Execute revocation through the production principal resolver seam

The current security suite does not call:

```text
resolvePlatformAdminPrincipal(...)
```

despite the attempt-3 Completion Report saying that a resolver fixture proves
active-to-inactive revocation.

Add a focused test that executes the exported resolver used by
`getPlatformAdminPrincipal()`:

```text
same session identity:
  email = admin@example.com
  providerSubject = google-1

first resolver call:
  findByEmail -> active=true, provider=google, providerSubject=google-1
  -> principal returned

second resolver call using the same session identity:
  findByEmail -> active=false, provider=google, providerSubject=google-1
  -> null / denied
```

The test must call `resolvePlatformAdminPrincipal()` itself, not only
`isAuthorizedPlatformAdmin()`.

Because development bypass would short-circuit the resolver, run this fixture
under a hosted/test environment with the minimum synthetic auth configuration
needed for `assertPlatformAdminAuthConfiguration()` to pass.

### 2. Execute the real first-binding race persistence behavior

`auth.ts` now correctly calls `authorizeGoogleProfile()`, but its production
`bindSubject` persistence behavior is still an inline closure:

```text
updateMany(... providerSubject: null ...)
  -> count === 1 => allowed

otherwise:
  findUnique(...)
  -> active + google + providerSubject === same subject => allowed
```

The current `"raced"` test injects:

```text
bindSubject: async () => true
```

so it does not execute that production race logic.

Extract only the production subject-binding persistence operation into a small
function/seam that:

```text
bind succeeds directly                  -> true
bind loses race; reread same subject    -> true
bind loses race; reread different subj  -> false
bind loses race; reread inactive        -> false
```

`auth.ts` must call that same extracted function. The focused test must execute
that function with injected persistence operations or an equivalent bounded
test seam.

Do not introduce a second authentication policy or redesign Auth.js.

### Already accepted from attempt 3

Do not reopen these unless your changes break them:

```text
environment fail-closed/bypass matrix
direct mutation guard-before-FormData/mutation
explicit hosted cookie/session contract
public bounded health/readiness routes
audit-field restrictions
Google verified/unknown/inactive/mismatch policy
deployment/OAuth documentation
```

### Validation

After the two focused fixes, run:

```text
node --test tests/security/*.test.mjs
npm test
npm exec tsc -- --noEmit
npm run lint
npm run prisma:validate
npm run build
```

Then update the Completion Report with the exact test names/results, transition
`in_progress -> review`, and STOP without committing or pushing.

## Completion Report

### Status

Ready for Review. Attempt 4 closes the two architect-requested executable
validation gaps; architect acceptance is still required.

### Files Changed

- `src/auth.ts`, `src/lib/auth/platform-admin.ts`, and
  `src/lib/auth/security-policy.ts`: carry and revalidate the Google provider
  subject on every privileged request, with injected production-path seams for
  authorization, subject binding persistence, and principal resolution.
- `tsconfig.json`: allows explicit TypeScript imports required by the direct
  resolver fixture.
- `src/lib/auth/tenant-action.ts` and `src/app/actions/tenant.ts`: route the
  tenant mutation through a guard-before-FormData/mutation wrapper.
- `src/lib/auth/security-policy.ts`: local authorization/revocation policy seam.
- `src/app/health/route.ts` and `src/app/ready/route.ts`: bounded public
  infrastructure endpoints.
- `README.md`: separate test/production OAuth hosts, callbacks, and
  environment-secret documentation.
- `package.json` and `tests/security/admin-security-boundary.test.mjs`:
  focused final-gate validation harness, including executable binding, race,
  revocation, mutation, and cookie-contract coverage.

### Work Completed

- Added executable environment coverage for development bypass, explicit test
  bypass, hosted missing-auth fail-closed behavior, and production configured
  with a development deployment identity.
- Added executable identity coverage for active bound, active unbound binding,
  raced unbound binding, unknown, inactive, subject mismatch, and
  post-revocation states through the real authorization and principal resolver
  seams used by production.
- Added executable direct mutation denial coverage proving the guard rejects
  before FormData access or Prisma mutation.
- Extracted the production first-binding persistence operation and tested direct
  success, same-subject race resolution, different-subject race denial, and
  inactive race denial.
- Executed the exported principal resolver twice with the same hosted session
  identity, proving active access followed by denial after deactivation.
- Explicitly configured and tested the hosted session cookie contract:
  HttpOnly, SameSite=Lax, hosted Secure, root path, and eight-hour maxAge.
- Verified privileged mutation guard ordering, five privileged read guards,
  session lifetime, public bounded routes, OAuth callback separation, and audit
  field restrictions.

### Validation Results

- `node --test tests/security/*.test.mjs`: 9 passed.
- `npm exec tsc -- --noEmit`: passed.
- `npm run lint`: passed.
- `npm run prisma:validate`: passed.
- `npm test`: 19 passed.
- `npm run build`: passed; routes include `/health`, `/ready`, and bounded
  `/api/health/database`.
- `git status --short`: reviewed; no commit or push performed.

The production build emitted the existing multiple-lockfile workspace-root
warning; compilation, type checking, page generation, and route output all
completed successfully.

### Deviations

- Live Google OAuth and a deployed database are not exercised in this local
  harness; injected persistence fixtures execute the same extracted production
  authorization path, and the resolver fixture exercises active-to-inactive
  revocation with the same session identity.
- The stale task criterion requiring repository-agent commit/push is not
  followed; workspace policy assigns publication to the developer.

### Assumptions

- Hosted cookie security is explicitly owned by the application configuration;
  no Auth.js cookie-default assumption remains.

### Unresolved Issues

None for the Admin implementation. Authenticated live OAuth/database fixtures
remain a future integration-harness improvement.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted / Complete

### Review Notes

`ARCH-002-ADMIN-008` is architect-accepted after attempt 4.

The final Admin security gate now has executable evidence for the complete
accepted boundary rather than relying on source-order inspection alone.

The two remaining attempt-4 gaps are closed through production-consumed seams.

#### Existing-session revocation

The focused security suite imports and executes:

```text
resolvePlatformAdminPrincipal(...)
```

using the same resolver consumed by `getPlatformAdminPrincipal()`.

The test holds the same session identity constant while changing the persisted
administrator state:

```text
active=true
  -> principal returned

same session identity
active=false
  -> null / denied
```

This proves that an otherwise valid browser session does not preserve
privileged access after the `PlatformAdmin` record is disabled.

#### Google provider-subject binding race

The production sign-in path is now:

```text
Auth.js signIn
  -> authorizeGoogleProfile(...)
  -> bindPlatformAdminSubject(...)
```

and `bindPlatformAdminSubject()` owns the persistence race semantics consumed by
`src/auth.ts`.

The focused suite executes the same function and proves:

```text
direct conditional bind succeeds             -> allowed
conditional bind loses race
  + reread same subject                       -> allowed
  + reread different subject                  -> denied
  + reread inactive admin                     -> denied
```

This is a bounded testability seam over the accepted production behavior, not a
parallel authentication policy.

### Previously Accepted Final-Gate Evidence

Architect review also retains the accepted attempt-2/3 evidence for:

```text
development/test/production bypass and fail-closed matrix
verified Google profile requirement
active bound/unbound administrator policy
unknown/inactive administrator denial
provider-subject mismatch denial
direct mutation guard before FormData/Prisma access
public bounded /health, /ready and /api/health/* routes
eight-hour JWT/session lifetime
HttpOnly session cookie
SameSite=Lax
Secure cookie in hosted test/production
root cookie path
bounded security-audit fields
test/production OAuth host and callback isolation
```

### Reviewed Files

Architect inspected the actual attempt-4 implementation, including:

```text
src/auth.ts
src/lib/auth/environment.ts
src/lib/auth/platform-admin.ts
src/lib/auth/security-policy.ts
src/lib/auth/tenant-action.ts
src/app/actions/tenant.ts
tests/security/admin-security-boundary.test.mjs
package.json
tsconfig.json
README.md
docs/decisions/admin/ARCH-002/ADMIN-008-validate-admin-security-boundary.md
```

### Validation Reviewed

The agent reports the following successful attempt-4 validation:

```text
focused ADMIN-008 security suite   9 PASS
full repository tests             19 PASS
TypeScript                        PASS
ESLint                            PASS
Prisma validation                 PASS
production build                  PASS
```

Architect source review independently verified that the two attempt-4 tests
invoke the production-consumed resolver/binding seams described above.

The existing multiple-lockfile Next.js workspace-root warning is not an
`ADMIN-008` security failure; the reported production build completed
successfully.

### Architecture Conformance

Accepted.

No password, OAuth credential or session secret is moved into Moda's
`PlatformAdmin` data model.

Authentication remains Google-backed and allow-list based. Current
administrator state is re-read for privileged access, so disabling an
administrator revokes subsequent privileged requests without waiting for the
eight-hour JWT to expire.

The testability seams do not create a second authorization implementation.

### Git / Publication

The repository agent correctly stopped at Review and did not commit or push.

Implementation changes are ready for developer commit/push.

The developer/user remains the owner of repository and parent-workspace
publication.

### Downstream Coordination

`ARCH-002-ADMIN-008` is Complete.

This acceptance satisfies the Admin-security dependency for:

```text
ARCH-002-GATEWAY-007
ARCH-002-GATEWAY-003
ARCH-002-ADMIN-004
```

It does **not** automatically change those tasks to Ready or start them.

`moda_architect` must re-evaluate each task's complete set of direct
dependencies after the accepted Admin changes are committed/pushed.

