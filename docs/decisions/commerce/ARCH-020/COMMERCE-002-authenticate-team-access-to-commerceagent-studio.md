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
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-001
enables:
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

- [ ] Configure NextAuth.js with Google and JWT sessions following Admin (including its current eight-hour maximum unless the architect changes it); supply Studio-specific callback, cookie and server-only secret configuration.
- [ ] Require a verified Google email and non-empty subject, normalise email, and look up the same pre-provisioned active PlatformAdmin row with provider=google. Reject unlisted users, unverified emails and subject mismatch; do not auto-provision staff.
- [ ] Match Admin's atomic first-login subject binding: update only an active Google row whose providerSubject is still null, then reload and accept only the same subject if another login won the race. Preserve display-name and last-login semantics.
- [ ] Carry providerSubject in the NextAuth JWT/session and reload current PlatformAdmin identity/role for each protected request; request-local deduplication is allowed, stale cross-request permission caches are not.
- [ ] Implement ADMIN inspect/edit/preview and SUPER_ADMIN publish/rollback/disable permissions with server-side checks.
- [ ] Recheck active identity and role for protected reads/actions; protect mutation origins/CSRF and fail closed on missing auth configuration.
- [ ] Provide a team-only shell and denied/expired-session states; no merchant account login or shared Admin host cookie trust.

- [ ] Apply the common submission guard to Google sign-in, sign-out and any confirmation/retry controls. Keep sign-in pending through navigation; only a known provider error/cancel resets it. Preserve NextAuth state/CSRF handling and existing atomic account-subject binding.

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

- ARCH-020-COMMERCE-003
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001
- ARCH-020-COMMERCE-011

## Acceptance Criteria

- [ ] Unauthenticated, deactivated and insufficient-role callers cannot access direct protected routes/actions.
- [ ] An active pre-provisioned Admin account with the same verified Google subject can sign into Studio through NextAuth without another account being created; inactive, unlisted, wrong-provider and mismatched-subject accounts are denied.
- [ ] Studio reads the same database identity/role records, creates no duplicate User/Account/Session tables, and never modifies merchant permissions.
- [ ] Deactivation or role change in the shared PlatformAdmin row takes effect on the next protected Studio request even when its JWT has not expired; concurrent first-login binding cannot bind a different subject.
- [ ] Authentication secrets stay server-side and denied operations produce bounded audit/security events.

- [ ] Rapid mouse/keyboard sign-in or sign-out activation initiates one client auth flow; repeated callbacks cannot create extra accounts or change provider-subject binding. Known provider failure/cancel permits a fresh intentional attempt.

## Validation

- [ ] Run local NextAuth callback/guard tests for verified/unverified email, existing/unlisted/inactive users, wrong provider/subject, atomic first-login races, JWT subject propagation, expiry, sign-out, and next-request role/deactivation changes.
- [ ] Test direct protected reads/actions, forged cross-host cookies, CSRF/origin rejection, host cookie isolation and failure on missing hosted auth configuration. Do not enable a hosted development bypass.
- [ ] Run declared typecheck/lint; verify login/denied shell keyboard behaviour locally. Live OAuth validation is developer-owned.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; the actual repository must be provisioned before execution preparation.

## Completion Report

### Status

Not Started.

### Files Changed

None; implementation has not started.

### Work Completed

None; task definition only.

### Validation Results

Not run. At execution, distinguish agent checks from exact developer validation required.

### Deviations

Task definition authored on local main by explicit developer request. Normal execution policy remains unchanged.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Commerce remote repository/submodule provisioning remains outstanding; role/route definitions exist in this review packet. Confirm whether automatic Admin-to-Studio sign-on is required; the current design uses the same account with a separate Studio session.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-COMMERCE-002. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.
