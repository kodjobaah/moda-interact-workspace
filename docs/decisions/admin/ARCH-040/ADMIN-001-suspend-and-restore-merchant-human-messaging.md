---
id: ARCH-040-ADMIN-001
architecture_id: ARCH-040
title: Suspend and restore merchant human messaging from Moda Admin
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-DATABASE-001
  - ARCH-040-DATABASE-005
enables:
  - ARCH-040-SYSTEM-TEST-001
created: 2026-10-16
updated: 2026-10-18
---

# ARCH-040-ADMIN-001 — Suspend and restore merchant human messaging from Moda Admin

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. Portable task definition; no branch, worktree, commit, push or implementation is claimed.

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

- [ ] Add restriction status and paginated/reason-safe history to the existing selected-tenant server read.
- [ ] Build a separate suspend/restore action with privileged server authorization, expected revision and mandatory reason.
- [ ] Use DATABASE-001 transaction/audit without touching general tenant status or recovery automation.
- [ ] Implement admin UI with clear confirmation, conflict recovery and disabled duplicate submit.
- [ ] Add authorization, persistence, conflict and UI tests including Shopify and Woo shop records.

## Interfaces / Contracts

Consumes `ShopHumanMessagingRestriction` and event from DATABASE-001. It is an internal platform-admin feature; no new public hosted API, no merchant editable preference and no new Shared contract.

## Dependencies

- ARCH-040-DATABASE-001


- ARCH-040-DATABASE-005
## Enables

- ARCH-040-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Privileged Admin can see redacted, shop-scoped moderation incidents and explicitly review them without automatic suspension or exposing raw customer content in the default list.

- [ ] Only authorized platform admins can suspend or restore; ordinary merchant users cannot.
- [ ] Every transition is audited with reason and platform admin; failed/repeated actions do not fabricate history.
- [ ] Suspended merchants retain recoveries/transcripts and automated AI operation; only HUMAN feature is blocked.
- [ ] The selected-merchant Admin UI shows current state/history without introducing separate admin application.

## Validation

- [ ] Admin server action authentication/CSRF/negative authorization tests
- [ ] CAS/audit PostgreSQL tests
- [ ] Admin component and production build/typecheck
- [ ] git diff --check and task worktree evidence

## Stop Condition

After defined work, acceptance criteria and required validation are complete, record Completion Report, set task to review, return control to moda_architect and STOP. Do not begin another task.

## Implementation Notes

Reuse existing platform-admin tenant page and audit helpers; do not silently add new roles. Inspect current component conventions and localisation before implementing. Use the canonical task preparation/worktree protocol. Check actual repository scripts before running tests; use the published shared logger for structured telemetry without message contents or credentials. No `_index.md` updates until the user explicitly confirms architectural-session completion.

## Completion Report

### Status
Not Started

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
The initiative is proposed; work has not begun.

### Unresolved Issues
None recorded.

### Architectural Concerns
None recorded.

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
