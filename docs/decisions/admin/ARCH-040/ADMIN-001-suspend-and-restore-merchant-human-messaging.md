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
status: in_progress
priority: 40
executor: developer
claimed_at: 2026-10-21T14:52:21Z
attempt: 1
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

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. Developer Attempt 1 is claimed in the dedicated task worktree; validation is recorded below and the Admin implementation is published on `origin/task/ARCH-040-ADMIN-001` at `d4558e8f9d45e8893741a8f2569935f5eca8089d`. Formal review remains pending.

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

- [x] Admin server action security/negative authorization tests (3/3 passed; protected action and SUPER_ADMIN boundaries verified in focused checks).
- [x] CAS/audit disposable PostgreSQL tests (1/1 passed; Shopify and Woo restrictions, revision conflicts, rollback and moderation review).
- [x] Admin contracts, component security checks and production build/typecheck (4/4 contract and 3/3 security tests passed; `npx tsc --noEmit` and `npm run build` passed).
- [x] `npm run lint` and `git diff --check` (0 lint errors, 1 pre-existing database-config warning; whitespace clean); dedicated task branch and clean local worktree confirmed.

**Submission gate:** The implementation commit `d4558e8f9d45e8893741a8f2569935f5eca8089d` is published and matches `origin/task/ARCH-040-ADMIN-001`; the developer may invoke `/moda_developer_update ARCH-040-ADMIN-001` for the required review. Do not mark Complete before a durable Accepted review and explicit developer completion decision.

## Stop Condition

After defined work, acceptance criteria and required validation are complete, record Completion Report, set task to review, return control to moda_architect and STOP. Do not begin another task.

## Implementation Notes

Reuse existing platform-admin tenant page and audit helpers; do not silently add new roles. Inspect current component conventions and localisation before implementing. Use the canonical task preparation/worktree protocol. Check actual repository scripts before running tests; use the published shared logger for structured telemetry without message contents or credentials. No `_index.md` updates until the user explicitly confirms architectural-session completion.

## Completion Report

### Status

In Progress — developer Attempt 1 implementation and validation are complete, and implementation commit `d4558e8f9d45e8893741a8f2569935f5eca8089d` is published on `origin/task/ARCH-040-ADMIN-001`. The local implementation worktree is clean and tracking that remote branch. Ready for the canonical developer review workflow; no Accepted review has yet been recorded.

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

### Work Completed

- Added selected-merchant HUMAN messaging suspension/restoration controls separate from general Shop status, with mandatory reason/category, revision validation, confirmation, and duplicate-submit protection.
- Reused protected Admin actions and SUPER_ADMIN authorization; applied transactional Shop-row locking and revision-checked restriction/audit transitions.
- Added shop-scoped paginated moderation incident projection with bounded non-content metadata and one-time attributed review that does not change the moderation decision.
- Kept AI/automation and existing merchant recovery surfaces outside the restriction mutation scope.
- Corrected the restriction action literal typing and replaced an invalid audit fixture with a transaction-injected audit-write failure. Narrowed the Prisma-extended fixture type at the test boundary; no production migration or business workflow change in these corrections.

### Validation Results

Validated on 2026-10-21 in the dedicated Admin implementation worktree:

- `npm run test:arch040-admin-human-messaging:unit`: **PASS**, 4/4 contract tests plus 3/3 security tests.
- `npm run test:arch040-admin-human-messaging:postgres`: **PASS**, 1/1 disposable PostgreSQL integration test, including Shopify/Woo restriction transitions, revision conflicts, audit rollback and moderation-review behavior.
- `npx tsc --noEmit`: **PASS**, no TypeScript errors reported.
- `npm run lint`: **PASS**, 0 errors; 1 unrelated `import/no-anonymous-default-export` warning in `database/eslint.config.mjs`.
- `npm run build`: **PASS**, Next.js production build and TypeScript checking succeeded. Existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` compilation warnings were non-blocking.
- `git diff --check`: **PASS**, no whitespace errors reported.
- Latest developer terminal evidence: `git status --short` returned no entries and `git branch --show-current` returned `task/ARCH-040-ADMIN-001`. Source output identifies a dedicated `moda-interact-workspace.worktrees/ARCH-040-ADMIN-001` execution path.
- **Remote implementation commit SHA/upstream verification:** **PASS**. `git log -1 --oneline` reports `d4558e8` (`feat(admin)`); `git push -u origin task/ARCH-040-ADMIN-001` succeeded; `git ls-remote --heads origin task/ARCH-040-ADMIN-001` reports `d4558e8f9d45e8893741a8f2569935f5eca8089d`. GitHub branch/ref inspection confirms the same published commit.

### Deviations

None from the feature architecture. Corrections after the first local run were limited to type validation and PostgreSQL test fixtures; no database schema or other repository was changed.

### Assumptions

- DATABASE-001 and DATABASE-005 are the accepted restriction/audit and moderation persistence dependencies.
- Submitted unit/security/PostgreSQL evidence and the latest clean-worktree command refer to the same dedicated implementation checkout. The full launcher preparation packet is not reproduced in the supplied log.

### Unresolved Issues

No known failing functional validation or outstanding publication requirement. The formal `/moda_developer_update ARCH-040-ADMIN-001` review and subsequent explicit developer completion decision remain outstanding; the current task status is still `in_progress`.

### Architectural Concerns

No new cross-service contract, database migration, queue, merchant role or AI/automation restriction was introduced. Formal integration behavior remains subject to the existing ARCH-040 system-test tasks.

## Architect Review

### Review Status
Pending

### Review Notes
None.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending.

### Follow-up
None.

## Execution Ownership Amendment

Developer execution was explicitly requested for this task. The task remains
assigned to `moda_admin`; execution ownership is changed from the automatic
agent path to the developer path for this attempt.

- Previous execution mode: `agent`
- Previous completion mode: `automatic`
- New execution mode: `developer`
- New completion mode: `developer`
- Amendment date: 2026-10-21
