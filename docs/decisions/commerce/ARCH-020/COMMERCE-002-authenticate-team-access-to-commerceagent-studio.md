---
id: ARCH-020-COMMERCE-002
architecture_id: ARCH-020
title: Authenticate team access to CommerceAgent Studio
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 60
executor:
claimed_at:
attempt: 2
depends_on:
  - ARCH-020-COMMERCE-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-003
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
  - ARCH-020-COMMERCE-011
created: 2026-09-20
updated: 2026-09-20
---

# Authenticate team access to CommerceAgent Studio

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Authenticate Studio with NextAuth.js using the same Google-backed PlatformAdmin accounts and database tables as Admin, with current server-side authorisation on every protected surface.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

NextAuth.js (`next-auth`) Google login/JWT session integration, existing PlatformAdmin database access through database/, Studio server guards, layout/navigation and security tests. Match the inspected Admin approach; do not substitute another authentication library.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

Read the existing Admin implementation as the reference:

- `moda-interact-admin/src/auth.ts`
- `moda-interact-admin/src/lib/auth/security-policy.ts`
- `moda-interact-admin/src/lib/auth/platform-admin.ts`
- `moda-interact-admin/src/lib/auth/environment.ts`
- `moda-interact-admin/src/lib/auth/development-platform-admin.ts`
- `moda-interact-admin/src/lib/auth/audit.ts`

Use [NextAuth.js](https://next-auth.js.org/) through the `next-auth` package. Admin currently declares `next-auth` 5.0.0-beta.32 and uses App Router handlers; record a compatible version during implementation rather than copying an incompatible Pages Router example or silently downgrading to v4. No Admin source change is authorised by this task.

The shared identity authority is the existing `public.PlatformAdmin` row (`email`, `provider`, `providerSubject`, `active`, `role`) in the same database. Authentication is Google OAuth via NextAuth, not a password lookup against that table. Do not create another staff directory or default NextAuth User/Account/Session tables: follow Admin's JWT-session strategy and existing allowlisted staff provisioning.

Session scope: the current proposed design retains a Studio-specific NextAuth session/cookie and callback. Using the same account/table does not automatically reuse the Admin browser session. Automatic cross-application sign-on is outside the explicit v1 separate-session default; do not claim it is delivered or silently share cookie domains/secrets. If selected, the architect must define the cross-application trust/redirect contract and any Admin/Gateway dependencies before execution.

### Duplicate-action protection

Every state-changing or costly UI action in this task must prevent duplicate
activation, including mouse double-click, double-tap, Enter/Space repetition and
form-submit plus button-click combinations. Acquire a synchronous submission
guard before awaiting work (a render-delayed disabled state alone is insufficient),
and route all activation paths through the same submit handler. Disable the
trigger and conflicting controls immediately, show a meaningful pending label,
and expose accessible busy/status feedback. Do not lock unrelated navigation.

Keep the guard until the operation has definitively completed, failed or been
cancelled. A client timeout is an unknown outcome: reconcile the original
operation before allowing a retry, rather than silently creating a second one.
On a known failure, restore controls and preserve input for an intentional retry.
Ignore stale completions so an earlier request cannot reset a newer request's
pending state. Debounce alone is not sufficient for mutations or paid previews.
Server authorisation and duplicate protection are required independently of the
browser controls; inspect direct duplicate requests as well as UI behaviour.

## Work Items

- [x] Implement binding C7.1 in full: Google-only NextAuth, Admin-compatible development SUPER_ADMIN resolution, transaction-safe reserved development identity, reusable server-only auth entry points and typed route/action/page denial adapters. No application route may invent its own auth or role resolution.

- [x] Configure NextAuth.js with Google and JWT sessions following Admin (including its current eight-hour maximum unless the architect changes it); supply Studio-specific callback, cookie and server-only secret configuration.
- [x] Require a verified Google email and non-empty subject, normalise email, and look up the same pre-provisioned active PlatformAdmin row with provider=google. Reject unlisted users, unverified emails and subject mismatch; do not auto-provision staff.
- [x] Match Admin's atomic first-login subject binding: update only an active Google row whose providerSubject is still null, then reload and accept only the same subject if another login won the race. Preserve display-name and last-login semantics.
- [x] Carry providerSubject in the NextAuth JWT/session and reload current PlatformAdmin identity/role for each protected request; request-local deduplication is allowed, stale cross-request permission caches are not.
- [x] Implement ADMIN inspect/edit/preview and SUPER_ADMIN publish/rollback/disable permissions with server-side checks.
- [x] Recheck active identity and role for protected reads/actions; protect mutation origins/CSRF and fail closed on missing hosted auth configuration; only the explicit C7.1 development environment bypass is exempt.
- [x] Provide a team-only shell and denied/expired-session states; no merchant account login or shared Admin host cookie trust.

- [x] Apply the common submission guard to Google sign-in, sign-out and any confirmation/retry controls. Keep sign-in pending through navigation; only a known provider error/cancel resets it. Preserve NextAuth state/CSRF handling and existing atomic account-subject binding.

## Interfaces / Contracts

Visual page ownership: Authentication service owner only: COMMERCE-008 implements the exact U01 /sign-in and U02 /access-denied screens. Do not build competing auth page layouts. [Approved prototype](../../../architecture/ARCH-020-studio-approved-prototype.html).

Existing public.PlatformAdmin model in the canonical database; NextAuth Google signIn/jwt/session callbacks and App Router auth handlers; Admin verified-email/provider-subject policy. JWT sessions do not require a database adapter or new auth tables. Studio permissions remain ADMIN inspect/edit/preview and SUPER_ADMIN publish/rollback/disable; shared identity does not grant live MCP access.

### Implementation guidance

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C7, C9, C10**. These are required acceptance inputs, not optional examples.

Use Admin src/auth.ts as behaviour reference, not a source import. Studio separate NextAuth session is the v1 default; automatic cross-host SSO requires a later explicit amendment. No DB adapter/new staff tables. Create request-scoped requireStudioAdmin and requireStudioSuperAdmin guards reused by all routes/actions. Distinguish unauthenticated401, inactive/insufficient role403 and UI redirects.

### Required evidence

Add callback/guard fixtures with an existing active PlatformAdmin and a concurrent first-subject bind. Every route family must be exercised directly, including server-action entry points, not only navigation links. UI tests target sign-in/out; do not require previews/publication here.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-COMMERCE-001

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-012

- ARCH-020-COMMERCE-003
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001
- ARCH-020-COMMERCE-011

## Acceptance Criteria

- [x] Pass C7.1 A01–A11 fixtures and provide an entry-point-to-guard matrix covering reads, writes, Server Actions, pages and explicit protocol exceptions. Demonstrate development SUPER_ADMIN, hosted rejection of bypass and reserved audit identity integrity.

- [x] Unauthenticated, deactivated and insufficient-role callers cannot access direct protected routes/actions.
- [x] An active pre-provisioned Admin account with the same verified Google subject can sign into Studio through NextAuth without another account being created; inactive, unlisted, wrong-provider and mismatched-subject accounts are denied.
- [x] Studio reads the same database identity/role records, creates no duplicate User/Account/Session tables, and never modifies merchant permissions.
- [x] Deactivation or role change in the shared PlatformAdmin row takes effect on the next protected Studio request even when its JWT has not expired; concurrent first-login binding cannot bind a different subject.
- [x] Authentication secrets stay server-side and denied operations produce bounded audit/security events.

- [x] Rapid mouse/keyboard sign-in or sign-out activation initiates one client auth flow; repeated callbacks cannot create extra accounts or change provider-subject binding. Known provider failure/cancel permits a fresh intentional attempt.

## Validation

- [x] Run local NextAuth callback/guard tests for verified/unverified email, existing/unlisted/inactive users, wrong provider/subject, atomic first-login races, JWT subject propagation, expiry, sign-out, and next-request role/deactivation changes.
- [x] Test direct protected reads/actions, forged cross-host cookies, CSRF/origin rejection, host cookie isolation and failure on missing hosted auth configuration. Do not enable a hosted development bypass.
- [x] Run declared typecheck/lint; verify login/denied shell keyboard behaviour locally. Live OAuth validation is developer-owned.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; the actual repository must be provisioned before execution preparation.

## Completion Report

### Status

Ready for Review — Attempt 2 implemented by copilot on 2026-09-20. The two Architect Review corrections are implemented and locally validated; live Google OAuth remains developer-owned and no architect acceptance is asserted.

### Correction Checklist — Architect Review Attempt 1

- [x] **R1 — documented local development mutations:** `lib/auth/environment.ts` now permits HTTP only for `localhost`, `127.0.0.1` or `[::1]` under the explicit development environment. Exact Origin comparison and POST enforcement remain unchanged; hosted HTTP, foreign origins and production builds using the development override fail closed. Covered by `tests/auth-environment.test.ts` and `tests/auth-origin.test.ts`.
- [x] **R2 — revoked/expired session recovery:** `clearStudioSessionAction` clears only the Studio NextAuth session after the same-origin POST check and does not require an active PlatformAdmin. The denied shell exposes it through the existing duplicate-action guard; no protected read, write, role or MCP authority is granted. Covered by `tests/auth-entrypoints.test.ts` and `tests/auth-action-button.test.tsx`.

### Files Changed

- `auth.ts`, `types/next-auth.d.ts`, `app/api/auth/[...nextauth]/route.ts`: NextAuth 5.0.0-beta.32 Google-only JWT session, eight-hour maximum, provider-subject propagation and Studio-specific host cookie.
- `lib/auth/*`: server-only environment, current PlatformAdmin resolution, typed failures/adapters, permission matrix, origin policy, shared structured security audit and exact reserved development identity.
- `app/page.tsx`, `app/sign-in/page.tsx`, `app/access-denied/page.tsx`, `components/auth-action-button.tsx`, `app/actions/session.ts`, `app/api/studio/access/route.ts`: protected team shell, minimal auth states, guarded sign-in/sign-out, protected read and privileged mutation entry points.
- `.env.example`, `README.md`, `package.json`, `package-lock.json`: hosted/local configuration contract, separate-session documentation, exact NextAuth dependency and accepted Shared 0.13.1 logging dependency.
- `tests/auth-*.test.{ts,tsx}`: C7.1 A01–A11 policy, entry-point, concurrency, environment, permission, origin and UI fixtures.
- Correction fixtures: development loopback mutation origins, hosted/foreign-origin rejection, revoked-session recovery entry-point isolation and duplicate-activation coverage for session clearing.

### Work Completed

Implemented the C7.1 auth boundary without a database adapter or new auth tables. Hosted login accepts only a verified Google profile matching an active, pre-provisioned `public.PlatformAdmin`; first subject binding uses conditional `updateMany`, reloads after a race and accepts only the winning subject. Existing display names are preserved and current logins refresh `lastLoginAt`.

JWT sessions carry `providerSubject`, while every protected request reloads email, active state, provider, subject and role from the canonical table. ADMIN receives inspect/edit/preview permissions; publish/rollback/enable/disable require SUPER_ADMIN. Page, route and Server Action adapters distinguish 401, 403 and 503 without returning configuration values. Root and sign-in are forced dynamic to prevent build-time/static principal capture.

Development bypass is derived only from the normalized server environment, fails closed for production builds, and yields the exact reserved SUPER_ADMIN. `ensureDevelopmentStudioAdmin` rechecks both environment and principal, inserts with `ON CONFLICT DO NOTHING`, and verifies every reserved field without modifying conflicts. Ordinary reads and startup create no auth row.

Mutations require POST plus the exact configured Origin, including development. NextAuth retains OAuth CSRF/state handling. Sign-out additionally passes through the guarded Server Action. Auth controls acquire a synchronous lock, disable immediately, expose a pending label/status and only unlock on a known start failure. No staff cookie or development principal authorizes MCP; no production MCP route exists.

Entry-point matrix:

| Family | Entry point | Guard | Exception/status behavior |
| --- | --- | --- | --- |
| Page | `/` | `requireStudioAdminPage` | no session -> `/sign-in`; denied/configuration -> `/access-denied` |
| Public auth page | `/sign-in` | `getStudioAdminPrincipal` | authenticated/development -> `/`; otherwise Google control |
| Direct read | `GET /api/studio/access` | `requireStudioAdmin` | typed 401/403/503, private no-store |
| Direct privileged write | `POST /api/studio/access` | exact Origin + `requireStudioSuperAdmin` | ADMIN and forged origins denied |
| Server Action | `signOutStudioAction` | exact Origin + `requireStudioAdmin` | typed denial before NextAuth sign-out |
| Protocol/public | `/api/auth/*`, `/health/live`, `/health/ready` | NextAuth protocol or health contract | explicit exceptions; no Studio session grants MCP access |

Requirement-to-fixture matrix:

| Contract | Fixture | Expected side effect | Result |
| --- | --- | --- | --- |
| A01 | verified allowlisted current Google subject | login timestamp refresh; no account creation | passed |
| A02 | unverified/unlisted/inactive/wrong-provider/wrong-subject | deny; no bind/refresh | passed |
| A03 | explicit development environment | server-resolved SUPER_ADMIN without Google credentials | passed |
| A04 | production build plus development override | configuration failure before principal | passed |
| A05 | test/production/unknown with missing configuration | fail closed as 503 adapter result | passed |
| A06 | request-shaped bypass flags outside development | ignored; no bypass principal | passed |
| A07 | concurrent reserved-row ensure and first-subject bind | one exact row/one subject; conflicts unchanged | passed with injected transaction/persistence fixtures |
| A08 | page/read/write/Server Action matrix and all seven permissions | direct guards; ADMIN cannot publish, SUPER_ADMIN can | passed |
| A09 | mutable role/active persistence behind repeated resolver calls | next request sees role/deactivation change | passed; no module-global principal cache |
| A10 | wrong/missing Origin, development request and absent MCP production route | deny mutation; bypass cannot authorize MCP | passed |
| A11 | sign-in redirect, badge and rapid mouse/keyboard auth controls | one flow, pending state, intentional retry after known failure | passed in DOM tests and local browser inspection |

### Validation Results

Agent-executed validation from the isolated implementation worktree with workspace Node 24.19.0:

```text
npm run prisma:generate
npm test
npm run typecheck
npm run lint
npm run build
git diff --check
```

- Prisma client generation: passed against recorded database submodule `5abfd87f57038bae515aaa09ec7c8db62adcfb98`.
- Focused correction fixtures: **4 files, 20 tests passed**.
- Vitest: **13 files, 69 tests passed**. This includes existing foundation checks, C7.1 auth/policy/UI cases and the two Architect Review corrections.
- Typecheck: passed (`next typegen && tsc --noEmit`).
- Lint: passed (`eslint .`).
- Production build: passed. `/`, `/sign-in`, auth handler, protected access route and health handlers compile; protected root/sign-in are dynamic.
- Diff whitespace check: passed.
- No unrelated baseline failures were observed.
- Local browser fixture: `DEPLOYMENT_ENVIRONMENT_NAME=development COMMERCE_STUDIO_ORIGIN=http://127.0.0.1:4184 npm run dev -- --port 4184`. Verified root shows `Development — SUPER_ADMIN`, `/sign-in` redirects to root without Google credentials, and `/access-denied` exposes its heading and return link. The dev server was stopped and its generated untracked agent files removed.

Developer-owned live validation remains pending because it requires provisioned Google credentials and a real callback host. With `AUTH_SECRET`, `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET`, matching `AUTH_URL`/`COMMERCE_STUDIO_ORIGIN`, `DATABASE_URL` and normal runtime dependencies configured for a non-development environment, run `npm run dev` (or the deployed start contract), sign in with one active provisioned Google account, verify sign-out, verify an unlisted account is denied, then deactivate/change the role of the signed-in PlatformAdmin and confirm the next protected request reflects it. No repository live-OAuth automation script exists; do not report this manual check as passed until the developer supplies evidence.

### Deviations

COMMERCE-008 owns the final U01/U02 prototype. This task supplies intentionally minimal accessible auth states and reusable auth behavior rather than the later visual design. The local browser run used the explicit development principal and made no provider/database call. The reserved-row concurrency proof uses an injected transaction fixture; no local/shared database was mutated.

### Assumptions

Separate Studio sessions remain the v1 default. The existing Shopify `Session` table remains in the canonical schema and is unrelated to NextAuth; no NextAuth User/Account/Session models or adapter were added. Future Studio pages/actions must call the exported server guards at each entry point.

### Unresolved Issues

Live Google OAuth evidence is pending developer execution as described above. No implementation defect or cross-repository blocker is known.

### Architectural Concerns

None. The task consumes exact `next-auth` 5.0.0-beta.32 and accepted Shared 0.13.1; it changes no shared contract or database schema.

### Git / VCS

- Task branch: `task/ARCH-020-COMMERCE-002` in both repositories.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-002`; reused, remote task fast-forward not needed, origin/main incorporated yes.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-002`; created for this task, remote task fast-forward not needed, origin/main already current. No shared/default checkout or another task worktree was switched or reused.
- Recursive submodule sync/update: passed; `database` remained at `5abfd87f57038bae515aaa09ec7c8db62adcfb98` with no pin change.
- Attempt 2 claim commit `6201f93ecf9a3b83c09a1ebfa82c5dbb54ff062f` was already pushed before implementation.
- Attempt 1 implementation head `7f70f33a491dd60861b25b1f820668258ea5a5d2` was corrected by implementation commit `fb3362e2e8df093c6a550bb08f9ee42aa8f778ab`, pushed to `origin/task/ARCH-020-COMMERCE-002`.
- Parent review submission is the commit containing this report, pushed to the matching parent task branch. Only this task file is staged; no Commerce gitlink, Architect Review, index/frontier, architecture document or main branch is changed.
- Merged to implementation main: no. Merged to workspace main: no.

## Architect Review

### Current review — Accepted, Attempt 2 (2026-09-20)

**Accepted. COMMERCE-002 is Complete at Attempt 2.** Reviewed published
implementation `fb3362e2e8df093c6a550bb08f9ee42aa8f778ab` and report
`5b1b4ec58e6aa12acdfc729f4ec20dbbb4948d6f`; both remote task heads verified.
This decision supersedes the historical Attempt 1 Changes Requested below.

R1 is closed: HTTP is admitted only for the configured loopback host under
explicit development, while exact Origin/POST checks remain. Hosted HTTP and
production-build development overrides still fail closed. The documented local
mutation origin no longer produces the previous configuration failure.

R2 is closed: the denied page offers a guarded Clear session control invoking
`clearStudioSessionAction`. That narrow protocol operation retains same-origin
POST protection and delegates cookie clearing/redirect to NextAuth without
requiring an active PlatformAdmin. A revoked or expired session can therefore
return to sign-in. Protected business routes still require current identity and
role; the change grants no staff permission or MCP authority. Final U01/U02 page
layout ownership remains COMMERCE-008.

Architect reran the four focused environment/origin/auth-control/entry-point files:
**20 tests passed**. Inspected the actual environment, Server Action and denied-page
flow rather than treating test count as acceptance. Supplied validation has
**69 passing tests**, typecheck, lint, build and Prisma generation; committed
whitespace checks pass. No further functional blocker found, no broader coverage
expansion requested, and no redundant build/infrastructure run performed.

Database remains `5abfd87f57038bae515aaa09ec7c8db62adcfb98`. Dedicated mirrored
worktrees, prepared claim, publication and clean state are consistent with the
report. No schema, main, gitlink or implementation changes by this review.

Live Google OAuth remains **unrun and developer-owned**: real callback-host and
credential verification is still required before claiming deployed sign-in works.
As C7.1 specifies local injected fixtures and separate live-check recording, this
is retained deployment validation, not a blocker to acceptance of the corrected
repository auth foundation.

Dependency disposition: accepted source is currently on task/ARCH-020-COMMERCE-002;
Commerce origin/main remains `86929b2`. Downstream consumers require developer
integration or explicit accepted-commit consumption before readiness promotion.
COMMERCE-011's task dependencies are satisfied in this branch snapshot, but its
source integration gate remains; COMMERCE-003/012, Gateway and terminal system
validation retain their other dependencies. No downstream task is launched or
promoted here; ARCH-020 is not Implemented.

### Historical Attempt 1 review

### Review Status

**Changes Requested — Attempt 1, 2026-09-20, moda_architect.** Reviewed published
implementation `7f70f33a491dd60861b25b1f820668258ea5a5d2` and report
`eb83eb8abe7f98af83f438639cacb440e30becf6`. Return the same task to Ready with
Attempt 1 retained and executor/claimed_at null. No next attempt or dependent task
is claimed/promoted. These are functional corrections, not a request for exhaustive
coverage or live provider execution.

### R1 — P2: documented local development cannot perform mutations

`lib/auth/environment.ts:32–44,72–78` accepts only HTTPS origins even after
`assertStudioAuthConfiguration` permits explicit development. The documented and
reported local setup uses `COMMERCE_STUDIO_ORIGIN=http://127.0.0.1:4184` with Next
development mode. That setup resolves SUPER_ADMIN but every otherwise-valid
mutation origin check throws configuration/503 before authorization, including
sign-out and future Studio actions. The reported browser read checks do not prove
that development writes work.

Confirmed by transpiling/evaluating the committed environment module with
`NODE_ENV=development`, `DEPLOYMENT_ENVIRONMENT_NAME=development`, and the documented
HTTP origin: `isDevelopmentStudioAuth` returned true, while
`configuredStudioOrigin` threw `503 configuration`.

Correction: support the documented local HTTP loopback origin only under the
explicit, production-build-safe development policy. Preserve exact Origin
comparison, POST enforcement and hosted HTTPS requirements. Verify a matching
local development mutation succeeds and foreign/missing origins remain denied;
hosted HTTP and production plus development override must still fail closed.

### R2 — P2: revoked session has no usable sign-out/account-recovery path

`app/actions/session.ts:16` requires current active-admin authorization before
clearing the session. After the current PlatformAdmin is deactivated or its
provider/subject no longer matches, the action therefore returns 403 and never
calls NextAuth signOut. Meanwhile `app/sign-in/page.tsx:10–12` redirects that same
session to access denied, whose only return link leads back to sign-in. The
visible recovery path loops; a user cannot clear the rejected Studio session and
try another authorized Google identity through this UI.

Correction: provide a minimal accessible way for a rejected/expired Studio
session to clear its own cookie and return to Google sign-in using the NextAuth
protocol or a narrow session-clearing adapter. Preserve same-origin/CSRF handling
and the client submission guard; do not grant denied users any protected read,
write, staff role or MCP authority. Clearing one's own session is a protocol
exception already recognized by C7.1, not a privileged business mutation. Keep
final U01/U02 visual ownership with COMMERCE-008.

Verify the concrete sequence: previously signed-in identity becomes inactive;
protected access is denied; the user clears that session through the offered
control; Google sign-in becomes available again. An expired-session sign-out
should also recover gracefully rather than requiring active-admin authorization.

### Conformance and Validation Reviewed

The core allowlist/Google verified-subject policy, conditional first binding,
current-row permission resolution, separate Studio cookie/JWT, exact development
identity helper and shared security logging otherwise align with the inspected
C7.1/Admin reference. No schema or merchant permission mutation was introduced.

Architect ran the five focused origin/environment/principal/Google-policy/auth-UI
files: **27 tests passed**. The R1 source-module reproduction above independently
failed as described. R2 follows the inspected resolver, action and page control
flow; no real Google account was contacted. Reviewed the supplied 65-test,
typecheck, lint, production-build and local browser evidence. Published heads,
dedicated worktrees, claim and database pin match the report; whitespace checks pass.

After the two source corrections, run targeted functional verification plus the
declared typecheck/lint and update the report with results. Retain unaffected
foundation evidence; no exhaustive coverage expansion or full Docker rerun is
requested. Commit/push the same mirrored branches and return to review.

Live Google OAuth remains explicitly developer-owned and unrun. C7.1 permits
injected local identity fixtures and separately records developer live OAuth
checks; this pending external callback/credential check is not the reason for
Changes Requested. Deployment sign-in must still be verified with real provisioned
configuration before claiming live OAuth works. No provider credentials, deployment
or main integration were used by this review.

## Architect readiness reconciliation — 2026-09-20

Promoted to **Ready**, with Attempt 0, executor null and claimed_at null preserved.
The sole dependency, ARCH-020-COMMERCE-001, is architect-accepted Complete at
Attempt 3. Its accepted implementation `d7c1c65bf382de1538d77ac4dbe65c1d7fcd1276`
is an ancestor of current Commerce origin/main
`86929b2d0fa636f4fe3dd595f1cd85707b0cea9b`, integrated through merge `8303133`.
Both acceptance and prerequisite source availability are now satisfied; the
previous Pending integration gate is cleared.

The canonical parent task branch was synchronized with workspace origin/main
`3be22019` before this update. This is readiness reconciliation only: no claim,
implementation change, new attempt, downstream launch or main merge/push.
The normal `/moda-task ARCH-020-COMMERCE-002` launcher may now prepare the task,
synchronize its implementation worktree and claim Attempt 1. Existing task scope,
NextAuth/PlatformAdmin requirements and later-task dependencies remain unchanged.
