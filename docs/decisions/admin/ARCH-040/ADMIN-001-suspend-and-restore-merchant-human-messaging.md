---
id: ARCH-040-ADMIN-001
architecture_id: ARCH-040
title: Suspend and restore merchant human messaging from Moda Admin
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-040-DATABASE-001
  - ARCH-040-DATABASE-005
enables:
  - ARCH-040-SYSTEM-TEST-001
created: 2026-10-16
updated: 2026-10-21
---

# ARCH-040-ADMIN-001 — Suspend and restore merchant human messaging from Moda Admin

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. Developer Attempt 1 received Changes Requested; Attempt 2 resolved the finding and passed review. The developer explicitly completed the task on 2026-10-21. Implementation commit `d875e5cccb2144da2b40058861f81eb4b7665908` is published on the task branch.

## Objective

Provide restricted platform-administrator control to suspend/restore human-originated messaging for a single merchant, with a mandatory reason and audit.

## Context

The existing tenant directory and `updateTenantAction` already expose broad shop status controls. Add a distinct human messaging section to the selected tenant, not another tenant suspension button and not merchant Recovery Settings.

## Scope

- Extend existing Moda Admin selected-tenant detail with current human-messaging restriction, suspend/restore action and history.
- Implement server-side authenticated privileged mutations with CSRF/protected-action pattern, strong shop validation, optimistic revision checking and transactional state/audit writes.
- Show a focused inline error/success experience, no duplicate submissions, preserve selected tenant page context.

## Out of Scope

- Do not change existing AI/automation entitlement or full-shop `Shop.status` rules; this is a platform-controlled HUMAN-only restriction.
- No merchant-facing toggle to restore a suspension, no per-employee permission system, no new Conversation or duplicated follow-up credit.
- Do not add new ARCH-040 Shared package publication, Shopify-to-Woo/API dependencies or `docs/decisions/**/_index.md` files.
- No speculative new service, queue platform or third-party AI moderation provider.

## Requirements

### Reviewable moderation incidents (DATABASE-005)

On the existing selected-merchant Admin human-messaging section, show a bounded/paginated shop-scoped read-only incident list: time, subject (`CUSTOMER`, `HUMAN`, `AGENT`, `AUTOMATION`), decision, category names, status and reviewed indicator, with restricted access. Do not display content or raw scores in the default list and do not expose internal notes via merchant endpoints. Admin acknowledgment/review annotation uses the DATABASE-005 audit metadata and existing authenticated platform-admin mutation patterns; it cannot silently turn a BLOCK into send permission. Suspending/restoring HUMAN messaging remains an explicit privileged action with mandatory reason, **never** an automatic effect of one model flag. Preserve existing Admin suspension ASCII controls.

### Roles and mutations

- Reuse `requirePlatformAdminMutation`, `runProtectedTenantAction`, the existing platform-admin principal and tenant-detail load patterns. Limit suspend/restore to `SUPER_ADMIN` unless the existing canonical role policy expressly grants another role; **do not invent merchant staff roles**.
- `SUSPEND` requires `shopId`, `expectedRevision`, a bounded machine `reasonCode` (for example SPAM, HARASSMENT, THREATS, POLICY_ABUSE, OTHER), and a non-empty internal `reasonNote` (1–1000 characters). `RESTORE` also requires a meaningful bounded reason. Verify the requested shop exists and that the admin principal has the approved role on **the server**.
- Persist one current restriction plus an audit event in a single transaction using DATABASE-001 monotonic CAS semantics. Unknown/stale revisions and already-in-target-state submissions receive explicit safe feedback. Mutation MUST NOT update `Shop.status`, `ShopFeaturePreference`, `Conversation.controlMode` or automation settings.
- Do not display the full sensitive internal reason note to merchants or include it in client-consumable recovery API responses. Protect against long strings, unsafe redirects and CSRF; log admin actions via existing structured security audit conventions.

### Admin acceptance layout

```text
Moda Admin > Merchants > Selected Store
+----------------------------------------------------+
| HUMAN MESSAGING                                    |
| Status: ACTIVE / SUSPENDED       Revision: 3        |
| [Suspend Human Messaging] / [Restore Access]       |
| Reason category: [Spam                  v]          |
| Internal reason (required): [................]      |
| [Confirm]                [Cancel]                  |
+----------------------------------------------------+
| HISTORY                                            |
| Time / Action / Reason / Platform admin            |
+----------------------------------------------------+
```

Show loading, invalid reason, stale version, already suspended/restored, concurrent update and persistence failure states; disable double clicks. The control does **not** turn off CommerceAgent or recovery automation.

### Cross-platform suspension invariant

Admin suspension is one shop-scoped persisted flag/revision, not a Shopify/WooCommerce setting, entitlement or per-user assignment. Both server-side merchant producers must reject new HUMAN actions when suspended; the same BG001/BG002 provider-admission fence must reject even previously accepted commands when suspension commits first. The platform-agnostic dispatcher must never ignore suspension because of command origin. Resume AI and reading existing recovery history remain permitted. Store restricted admin notes only in privileged Admin views and record a stable restriction revision for concurrency; do not add any platform-specific scheduling or separate shop UI permission system.


## Work Items

- [x] Add restriction status and paginated/reason-safe history to the existing selected-tenant server read.
- [x] Build a separate suspend/restore action with privileged server authorization, expected revision and mandatory reason.
- [x] Use DATABASE-001 transaction/audit without touching general tenant status or recovery automation.
- [x] Implement admin UI with clear confirmation, conflict recovery and disabled duplicate submit.
- [x] Add authorization, persistence, conflict and UI tests including Shopify and Woo shop records.

## Interfaces / Contracts

Consumes `ShopHumanMessagingRestriction` and event from DATABASE-001. It is an internal platform-admin feature; no new public hosted API, no merchant editable preference and no new Shared contract.

## Dependencies

- ARCH-040-DATABASE-001


- ARCH-040-DATABASE-005
## Enables

- ARCH-040-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Privileged Admin can see redacted, shop-scoped moderation incidents and explicitly review them without automatic suspension or exposing raw customer content in the default list.

- [x] Only authorized platform admins can suspend or restore; ordinary merchant users cannot.
- [x] Every transition is audited with reason and platform admin; failed/repeated actions do not fabricate history.
- [x] Suspended merchants retain recoveries/transcripts and automated AI operation; only HUMAN feature is blocked.
- [x] The selected-merchant Admin UI shows current state/history without introducing separate admin application.

## Validation

- [x] Admin server action security/negative authorization tests (Attempt 2: 4/4 security tests passed, including SUPER_ADMIN-only reason-note visibility and incident redaction).
- [x] CAS/audit disposable PostgreSQL tests (Attempt 2: 1/1 passed; Shopify/Woo restrictions, revision conflicts, audit rollback, moderation review, and persisted reason-note projection).
- [x] Admin contracts, component security checks and production build/typecheck (Attempt 2: 4/4 contract + 4/4 security; `npx tsc --noEmit` and `npm run build` passed).
- [x] `npm run lint` and `git diff --check` (Attempt 2: 0 lint errors, 1 unrelated database ESLint warning; whitespace check passed).

**Completion decision:** The developer explicitly invoked `/moda_developer_update ARCH-040-ADMIN-001 complete` after the durable Accepted Attempt 2 review. Task-owned implementation and parent report changes are committed and published. No branch was merged to `main`. `ARCH-040-SYSTEM-TEST-001` remains `pending` because `ARCH-040-BACKGROUND-008` is still pending; its manual execution gate remains in force.

## Stop Condition

After defined work, acceptance criteria and required validation are complete, record Completion Report, set task to review, return control to moda_architect and STOP. Do not begin another task.

## Implementation Notes

Reuse existing platform-admin tenant page and audit helpers; do not silently add new roles. Inspect current component conventions and localisation before implementing. Use the canonical task preparation/worktree protocol. Check actual repository scripts before running tests; use the published shared logger for structured telemetry without message contents or credentials. No `_index.md` updates until the user explicitly confirms architectural-session completion.

## Completion Report

### Status

Complete — developer Attempt 2 was accepted and explicitly completed on 2026-10-21. The published correction `d875e5cccb2144da2b40058861f81eb4b7665908` adds the reason note to SUPER_ADMIN-only restriction history with redaction regression coverage. Focused unit/security (8/8), disposable PostgreSQL (1/1), TypeScript, lint, production build and whitespace checks passed. Metadata is `complete`, `executor: null`, `claimed_at: null`, `attempt: 2`. Attempt 1's Changes Requested review is retained as history.

### Files Changed

In the Admin implementation repository (from the task-scoped implementation and corrections):

- `package.json`
- `scripts/test-arch040-admin-human-messaging-postgres.mjs`
- `src/app/(protected)/page.tsx`
- `src/app/actions/tenant-human-messaging.ts`
- `src/components/admin/human-messaging-controls.tsx`
- `src/components/admin/tenant-administration.tsx`
- `src/components/admin/tenant-detail-panel.tsx`
- `src/components/admin/tenant-human-messaging.tsx`
- `src/components/admin/tenant-table.tsx`
- `src/lib/admin/human-messaging-contract.ts`
- `src/lib/admin/human-messaging-mutations.ts`
- `src/lib/admin/human-messaging.ts`
- `tests/integration/arch040-human-messaging.postgres.test.ts`
- `tests/security/admin-human-messaging.test.mjs`
- `tests/unit/arch040-human-messaging-contract.test.ts`

Attempt 2 correction commit `d875e5cccb2144da2b40058861f81eb4b7665908` modifies only:

- `src/components/admin/tenant-human-messaging.tsx`
- `src/lib/admin/human-messaging-contract.ts`
- `src/lib/admin/human-messaging.ts`
- `tests/integration/arch040-human-messaging.postgres.test.ts`
- `tests/security/admin-human-messaging.test.mjs`

### Work Completed

- Added selected-merchant HUMAN messaging suspension/restoration controls separate from general Shop status, with mandatory reason/category, revision validation, confirmation, and duplicate-submit protection.
- Reused protected Admin actions and SUPER_ADMIN authorization; applied transactional Shop-row locking and revision-checked restriction/audit transitions.
- Added shop-scoped paginated moderation incident projection with bounded non-content metadata and one-time attributed review that does not change the moderation decision.
- Kept AI/automation and existing merchant recovery surfaces outside the restriction mutation scope.
- Corrected the restriction action literal typing and replaced an invalid audit fixture with a transaction-injected audit-write failure. Narrowed the Prisma-extended fixture type at the test boundary; no production migration or business workflow change in these corrections.
- Resolved Attempt 1 Changes Requested: the privileged restriction-event reader selects persisted `reasonNote`, the selected-merchant SUPER_ADMIN history renders it as text, and focused security/PostgreSQL regressions verify that the ordinary moderation incident projection continues to omit message content, raw scores and internal notes. No merchant or recovery API was changed.

### Validation Results

**Attempt 1 baseline — previously validated on 2026-10-21** in the dedicated Admin implementation worktree:

- `npm run test:arch040-admin-human-messaging:unit`: **PASS**, 4/4 contract tests plus 3/3 security tests.
- `npm run test:arch040-admin-human-messaging:postgres`: **PASS**, 1/1 isolated disposable PostgreSQL integration test, including Shopify/Woo restriction transitions, revision conflicts, audit rollback and moderation-review behavior.
- `npx tsc --noEmit`: **PASS**, exit 0; no TypeScript errors reported.
- `npm run lint`: **PASS**, 0 errors; 1 unrelated `import/no-anonymous-default-export` warning in `database/eslint.config.mjs`.
- `npm run build`: **PASS**, exit 0; Next.js production build and TypeScript checking succeeded. Existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` compilation warnings were non-blocking.
- `git diff --check`: **PASS**, no whitespace errors reported.
- Implementation worktree status after validation/build: clean, branch `task/ARCH-040-ADMIN-001`, tracking the published implementation branch.
- **Attempt 1 implementation publication:** verified commit `d4558e8f9d45e8893741a8f2569935f5eca8089d` on `origin/task/ARCH-040-ADMIN-001`.

**Attempt 2 reason-note correction — validation log `typescript(20261021-164428)` (2026-10-21):**

- `npm run test:arch040-admin-human-messaging:unit`: **PASS**, 4/4 contract and 4/4 security tests; includes `restriction history includes privileged notes while incidents stay content-free`.
- `npm run test:arch040-admin-human-messaging:postgres`: **PASS**, 1/1 disposable PostgreSQL integration test with persisted privileged-history reason-note and redacted-incident assertions.
- `npx tsc --noEmit`: **PASS**, no TypeScript error reported.
- `npm run lint`: **PASS**, 0 errors; 1 unrelated `import/no-anonymous-default-export` warning in `database/eslint.config.mjs`.
- `npm run build`: **PASS**, Next.js production build and TypeScript checking completed; existing BullMQ and optional Valkey warnings remained non-blocking.
- `git diff --check`: **PASS**, no whitespace errors reported.
- **Published correction:** commit `d875e5cccb2144da2b40058861f81eb4b7665908` (`fix(ARCH-040-ADMIN-001): show restriction notes in privileged history`) verified on `origin/task/ARCH-040-ADMIN-001`.
- **Workflow evidence:** The supplied parent task snapshot shows a valid claimed Attempt 2 with synchronized task worktrees. The corrected implementation is published. The most recent post-validation implementation `git status` was not separately supplied, so no new clean-worktree claim is made here.

### Deviations

None from the feature architecture. Attempt 1 corrections addressed types and fixtures; Attempt 2 changes only the privileged Admin reason-note history DTO/query/UI and focused regression tests. No database migration, merchant API, recovery API or other repository was changed.

### Assumptions

- DATABASE-001 and DATABASE-005 are the accepted restriction/audit and moderation persistence dependencies.
- Submitted unit/security/PostgreSQL evidence and the latest clean-worktree command refer to the same dedicated implementation checkout. The full launcher preparation packet is not reproduced in the supplied log.

### Unresolved Issues

No known implementation issue remains from the reviewed scope. `ARCH-040-SYSTEM-TEST-001` remains pending because `ARCH-040-BACKGROUND-008` is pending; no downstream task was claimed or started.

### Architectural Concerns

No new cross-service contract, database migration, queue, merchant role or AI/automation restriction was introduced. Formal integration behavior remains subject to the existing ARCH-040 system-test tasks.

## Architect Review

### Review Status
Accepted — Attempt 2

### Review Notes
The Attempt 1 finding is resolved. At `d875e5cccb2144da2b40058861f81eb4b7665908`, the SUPER_ADMIN-only restriction-event projection selects `reasonNote` and the selected-merchant Admin history renders it. Security regression coverage verifies the note is excluded from moderation incident projection/UI alongside message content and scores; PostgreSQL integration verifies the persisted history note. No merchant or recovery API was changed. Attempt 2 passed required focused validation. Since `completion_mode: developer`, this Accepted review does not complete the task.

### Reviewed Files
`src/app/actions/tenant-human-messaging.ts`; `src/lib/admin/human-messaging-mutations.ts`; `src/lib/admin/human-messaging.ts`; `src/lib/admin/human-messaging-contract.ts`; `src/components/admin/tenant-human-messaging.tsx`; `src/components/admin/human-messaging-controls.tsx`; `src/app/(protected)/page.tsx`; focused unit/security/PostgreSQL tests; `database/prisma/schema.prisma`. The Attempt 2 correction diff was reviewed against `d4558e8f9d45e8893741a8f2569935f5eca8089d`.

### Validation Reviewed
Attempt 2 validation independently confirmed: `npm run test:arch040-admin-human-messaging:unit` PASS (4 contract + 4 security); `npm run test:arch040-admin-human-messaging:postgres` PASS (1/1 disposable PostgreSQL); `npx tsc --noEmit` PASS (exit 0); `npm run lint` PASS (exit 0, 0 errors and 1 unrelated `database/eslint.config.mjs` warning); `npm run build` PASS (exit 0; existing optional BullMQ/Valkey warnings); `git diff --check` PASS (exit 0). Implementation commit `d875e5cccb2144da2b40058861f81eb4b7665908` is published and the implementation worktree is clean. Both dependencies resolve `complete`; both canonical worktrees are correctly registered and synchronized.

### Architecture Conformance
Conforms to the task scope. The reason note remains limited to privileged Admin restriction history; moderation incidents remain content/score/note-redacted. No cross-platform or unrelated implementation changes were found in the correction.

### Follow-up
No further ADMIN-001 work is required. `ARCH-040-SYSTEM-TEST-001` remains dependency-blocked on `ARCH-040-BACKGROUND-008`; it is not started by this completion. Do not merge either task branch to `main`.

### Developer Self-Review - Changes Requested

- Attempt: 1 (preserved).
- Review date: 2026-10-21.
- Implementation revision reviewed: `d4558e8f9d45e8893741a8f2569935f5eca8089d`, published and synchronized on `origin/task/ARCH-040-ADMIN-001`.
- Dependency state: `ARCH-040-DATABASE-001` and `ARCH-040-DATABASE-005` both resolve `complete`.
- Validation: focused unit/security 7/7, disposable PostgreSQL 1/1, TypeScript exit 0, lint 0 errors, production build exit 0, and diff check exit 0.
- Required correction: expose the stored internal `reasonNote` in the SUPER_ADMIN-only selected-merchant restriction history, without exposing it in merchant/recovery APIs; add targeted regression coverage and rerun validation.
- Task transition: Attempt 1 returned to `ready` with claim cleared; `completion_mode: developer` retained. This was not an Accepted review or completion decision.

### Developer Attempt 2 Claim

- Claim date: 2026-10-21T16:52:17Z.
- Executor: `developer`; attempt incremented from 1 to 2.
- Parent task worktree was synchronized by merging current `origin/main` into `task/ARCH-040-ADMIN-001`; no conflicts. Implementation task branch already contained current `origin/main` and was synchronized with its remote.
- Both declared dependencies resolve `complete`.
- Implementation correction commit `d875e5cccb2144da2b40058861f81eb4b7665908` is published on `origin/task/ARCH-040-ADMIN-001` and passed Attempt 2 validation/review.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-040-ADMIN-001`.
- Task branch: `task/ARCH-040-ADMIN-001` in both repositories. Completion mode remains `developer`.
- Attempt 2 validation passed: focused unit/security, disposable PostgreSQL, TypeScript, lint, production build, and whitespace checks. The Accepted review and `review` transition are recorded above.

### Developer Self-Review Passed — Attempt 2

- Review date: 2026-10-21.
- Reviewed implementation: `d875e5cccb2144da2b40058861f81eb4b7665908`, published and synchronized on `origin/task/ARCH-040-ADMIN-001`.
- Prior Changes Requested item: resolved; privileged restriction history now includes the internal note, while moderation incidents and merchant/recovery surfaces remain redacted.
- Validation passed: focused unit/security 8/8; disposable PostgreSQL 1/1; TypeScript exit 0; lint exit 0 with one unrelated warning; production build exit 0 with existing optional dependency warnings; diff check exit 0.
- Dependencies: `ARCH-040-DATABASE-001` and `ARCH-040-DATABASE-005` resolve `complete`.
- Review transition: `review`, `executor: null`, `claimed_at: null`, `attempt: 2`; `completion_mode: developer` retained.

### Developer Completion Decision

- Decision date: 2026-10-21.
- The developer explicitly invoked `/moda_developer_update ARCH-040-ADMIN-001 complete` after the durable Accepted Attempt 2 review.
- Accepted attempt: 2 (unchanged); task status set to `complete`; executor and claim cleared.
- Implementation correction `d875e5cccb2144da2b40058861f81eb4b7665908` and parent task report are published on their mirrored `task/ARCH-040-ADMIN-001` branches.
- Dependency frontier checked: `ARCH-040-DATABASE-001`, `ARCH-040-DATABASE-005`, `ARCH-040-BACKGROUND-002`, `ARCH-040-BACKGROUND-006`, and `ARCH-040-BACKGROUND-007` are complete; `ARCH-040-BACKGROUND-008` is pending. Therefore `ARCH-040-SYSTEM-TEST-001` remains pending and was not started.

## Execution Ownership Amendment

Developer execution was explicitly requested for this task. The task remains
assigned to `moda_admin`; execution ownership is changed from the automatic
agent path to the developer path for this attempt.

- Previous execution mode: `agent`
- Previous completion mode: `automatic`
- New execution mode: `developer`
- New completion mode: `developer`
- Amendment date: 2026-10-21
