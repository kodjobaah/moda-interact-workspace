---
id: ARCH-040-API-005
architecture_id: ARCH-040
title: Align Woo merchant follow-up admission to configured recovery policy
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-040-API-004
enables:
  - ARCH-040-WOOCOMMERCE-001
  - ARCH-040-SYSTEM-TEST-003
created: 2026-10-20
updated: 2026-10-21
---

# ARCH-040-API-005 — Woo configured follow-up eligibility correction

## Architecture

ARCH-040 parent: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Owner `moda_api` / `moda-interact-api`. The parent task is materialised on `task/ARCH-040-API-005` and was claimed for developer execution (Attempt 1). Implementation commit `143fe2678d130a2c33d48de60775e1992ac6dfb2` is published on the implementation task branch; the parent report is being submitted for developer review.

## Objective

Remove the independent hardcoded 24-hour delay from the accepted WooCommerce HUMAN follow-up template admission. Use **verified inbound only for the rolling free-text service window** and the **existing effective recovery follow-up setting and persisted due time** for post-window merchant template eligibility.

## Current source and defect

- `src/merchant/conversations/messages/eligibility.ts`: `latestVerifiedCustomerInbound()` and `windowOpen()` correctly define the verified 24-hour window. Retain these semantics. `merchantFollowUpWindowClosed(initialSentAt,inbound,now)` currently applies `now >= max(initialSentAt,inbound)+24h` even with no reply; this incorrectly introduces a fixed wait irrespective of Recovery Settings.
- `src/merchant/conversations/messages/admission.service.ts`: `MerchantConversationMessageAdmissionService.admit()` uses that helper for `RECOVERY_FOLLOW_UP_TEMPLATE` and atomically claims the one existing sequence-2 attempt.
- Prisma already includes `RecoveryOutreachAttempt.followUpDueAt` on sequence 1; the effective recovery policy is reflected in its persisted due time. Existing ShopSettings/ShopRecoveryPolicyOverride are the inputs to policy resolution, not a new independent timer.
- API-004 is Complete. **Do not reopen or rewrite that task file**. Implement this correction only in API-005.

## Scope

1. Keep the current Woo installation credentials, current shop/recovery isolation, idempotent replay before eligibility, HUMAN mode/revision, recipient/approved-template, suspension, entitlement and sequence-two lock/claim rules.
2. Continue selecting newest **provider-verified** CUSTOMER/INBOUND row between sequence-1 `sentAt` and one captured server `now`, ordered `(createdAt DESC,id DESC)`. No outbound, pre-initial, future or unverified row can open a window.
3. `HUMAN_TEXT`: allow only while the latest verified CUSTOMER inbound's `[at,at+24h)` window is open. At exact expiry deny.
4. `RECOVERY_FOLLOW_UP_TEMPLATE`: allow only when the window is **closed** (including no customer reply), the initial attempt was sent, the existing **configured** follow-up is enabled/scheduled/due as evidenced by `sequence1.followUpDueAt != null && followUpDueAt <= now`, and sequence 2 is unclaimed and otherwise eligible. **Remove `initialSentAt+24h` or `lastInboundAt+24h` as independent follow-up delay gates.** The latter is only a window-closed boundary.
5. If follow-up is disabled, absent or not yet due, deny with existing stable typed failure (`follow_up_unavailable` or an established equivalent); do not schedule a new job or compute a default due time. Respect frozen effective recovery-policy evidence rather than an ad hoc live setting read.
6. Preserve scheduled AUTOMATION no-response timing and engagement suppression, billing and command acceptance. Do not modify Shopify, Background or WP plugin in this task.
7. Add focused unit and PostgreSQL tests for verified/unverified and exact 24h boundaries, absent initial, absent/future due, enabled short and long configured delays, previously engaged customer, one sequence-two winner, idempotent replay and tenant isolation.

## Out of Scope

No new follow-up queue, schema, template catalogue, sender, credit or separate conversation. No recovery settings UI changes; no cross-repository implementation; no `_index.md` updates.

## Decision table

`S` = initial sent, `D` = effective persisted due (null if disabled/unscheduled), `V` = verified inbound.

| Scenario | HUMAN_TEXT | HUMAN template |
|---|---|---|
| `V` is within latest 24 hours | Eligible | Denied: window open |
| `V` expired, `D <= now` | Denied | Eligible if sequence 2 free |
| `V` expired, `D > now` or null | Denied | Denied |
| No `V`, `D <= now` | Denied | Eligible even if `now < S+24h` |
| No `V`, `D > now` or null | Denied | Denied |
| Missing unsent `S` or terminal recovery | Denied | Denied |

The existing approved Meta template requirement and all other policy gates apply to every eligible template row. A customer reply **does not schedule** a new follow-up; scheduled no-response jobs remain suppressed after engagement.

## Work Items

- [x] Inspect accepted Woo API-004 admission flow and Background's existing sequence-1 `followUpDueAt` producer; the persisted effective-policy due time exists and no new delay resolver is needed.
- [x] Replace the obsolete independent 24-hour waiting condition with persisted due-time and verified-window checks.
- [x] Preserve existing transaction locks, replay-before-eligibility ordering and provider-verified CUSTOMER inbound reader.
- [x] Add unit and disposable PostgreSQL tests for the decision table, tenant isolation, replay and one sequence-two claimant.
- [x] Verify the effective due-time producer is present; no missing-producer dependency gap or fallback delay was introduced.

## Interfaces / Contracts

Existing `POST /v1/merchant/conversations/{conversationId}/messages`; existing `HumanSendInput`, `SendHttpError`, `RecoveryOutreachAttempt` and Woo principal. No new HTTP route or Shared contract. API-002 owns the independent read projection; WooCommerce-001 consumes the already-authenticated API boundary.

## Dependencies

- ARCH-040-API-004 (Complete in supplied snapshot).

## Enables

- ARCH-040-WOOCOMMERCE-001.
- ARCH-040-SYSTEM-TEST-003.

## Acceptance Criteria

- [x] Woo free text is eligible only from provider-verified CUSTOMER inbound within the latest rolling 24-hour window; exact expiry is excluded (unit and PostgreSQL integration).
- [x] HUMAN follow-up template requires a closed service window and due, non-null persisted `followUpDueAt`; no independent initial-send-plus-24-hour gate (short/long delay and boundary tests).
- [x] Disabled, missing or future-due follow-ups do not create a merchant command or sequence-two claim; API does not admit or consume recovery credits (PostgreSQL checks).
- [x] Woo installation/tenant ownership, approved template, idempotent replay, existing moderation boundary and single sequence-two claimant are retained (API-004/API-005 integration suites).
- [x] Only the API repository's admission/eligibility code, tests and test harness changed; no Shopify/Background runtime, schema migration or infrastructure added.

## Validation

- [x] Focused API unit/contract: `node --import tsx --test tests/unit/merchant/conversations/messages/contract.test.ts` — 5/5 passed (final 2026-10-21 run).
- [x] Disposable PostgreSQL: `npm run test:arch040-human-send:postgres` — API-005 and API-004 admission suites 2/2 passed; Prisma applied 58 migrations using database submodule HEAD `807af33`.
- [x] `npm run typecheck` (Prisma Client v6.19.3, `tsc --noEmit`), `npm run lint`, `npm run build` — passed on final run.
- [x] `git diff --check` — no whitespace errors reported, confirmed again in supplied Git output.
- [x] Reconcile the validated database gitlink (`aa3fd02` -> `807af33`) and publish implementation commit `143fe2678d130a2c33d48de60775e1992ac6dfb2` on `origin/task/ARCH-040-API-005`; parent task report records the source and validation evidence.

## Implementation Notes

Do not repurpose `latestVerifiedCustomerInbound` as a follow-up timer. `followUpDueAt` is the recovery snapshot; validate how it is written by the existing recovery scheduling flow. Keep one captured `now` per admission transaction; provider sending and billing remain Background-owned.

## Stop Condition

After scoped implementation and functional acceptance criteria are complete, record the Completion Report, set status `review`, return to moda_architect and STOP.

## Completion Report

### Status

Review — developer Attempt 1 implementation and required validation passed. Implementation commit is published and the database gitlink used for validation is recorded as `807af3393f992c8a19bc9ef278d7e7e05f41799d`. A passing review is recorded below; explicit developer completion is pending.

### Files Changed

Implementation repository, published commit `143fe2678d130a2c33d48de60775e1992ac6dfb2` on `task/ARCH-040-API-005`:

- `src/merchant/conversations/messages/eligibility.ts`
- `src/merchant/conversations/messages/admission.service.ts`
- `tests/unit/merchant/conversations/messages/contract.test.ts`
- `tests/integration/merchant/conversations/messages.follow-up-policy.postgres.test.ts` (new, untracked)
- `scripts/test-arch040-woo-human-send-postgres.mjs`
- `database` submodule gitlink is pinned to `807af3393f992c8a19bc9ef278d7e7e05f41799d` so the 58-migration validation baseline is reproducible.

## Execution Ownership Amendment

Developer execution was explicitly requested for this task. The task remains
assigned to `moda_api`; execution ownership is changed from the automatic agent
path to the developer path for this attempt.

- Previous execution mode: `agent`
- Previous completion mode: `automatic`
- New execution mode: `developer`
- New completion mode: `developer`
- Amendment date: 2026-10-20

### Work Completed

- `RECOVERY_FOLLOW_UP_TEMPLATE` admission now requires the customer service window to be closed and sequence one's persisted `followUpDueAt` to be non-null and due. Removed the independent 24-hour wait following initial outreach.
- Retained `HUMAN_TEXT` provider-verified customer-inbound window `[inbound, inbound + 24h)` and exact-expiry behavior; no extra live settings read or follow-up scheduler.
- Kept the API-004 Woo principal, tenant checks, approved-template checks, idempotency/replay ordering, existing transaction locks and sequence-two claim semantics.
- Extended the existing disposable PostgreSQL harness to run a dedicated API-005 scenario alongside API-004; added unit assertions for persisted due-time eligibility and PostgreSQL cases for short/long delays, unscheduled/not-due attempts, verified/unverified replies, exact expiry, single-claim contention, replay and cross-shop isolation.

### Validation Results

Final successful run from `typescript(20261021-110607)` (21 October 2026, after dependency install and switching the database submodule to `807af33`):

- `node --import tsx --test tests/unit/merchant/conversations/messages/contract.test.ts`: **PASS 5/5**.
- `npm run test:arch040-human-send:postgres`: **PASS 2/2** (API-005 follow-up due/window suite and API-004 durable admission suite); disposable database successfully applied **58 migrations**.
- `npm run typecheck`: **PASS** (`prisma generate` v6.19.3; TypeScript completed without diagnostics).
- `npm run lint`: **PASS** (`eslint . --max-warnings=0`).
- `npm run build`: **PASS** (Prisma Client generation and TypeScript build).
- `git diff --check`: **PASS**, no whitespace errors in the log or follow-up terminal output.
- Earlier attempts to run tests/typecheck initially failed because dependencies were absent (`tsx`, `prisma`, `eslint`) and the API database submodule was behind; these were environment/baseline issues resolved for the final run by `npm ci` and selecting database HEAD `807af33`.
- `npm ci` reported Node `24.21.0` versus repository-pinned `24.19.0` and **three high-severity npm audit findings**. No dependency changes or audit remediation were undertaken within API-005.
- After validation, implementation commit `143fe2678d130a2c33d48de60775e1992ac6dfb2` was confirmed equal to `origin/task/ARCH-040-API-005`; implementation worktree is clean and contains current `origin/main`.

### Deviations

- No new runtime behavior outside the approved API-005 scope. A newer database submodule checkout was used to run integration tests/typecheck; whether to record that gitlink in the API task branch remains an explicit integration decision.

### Assumptions

The effective follow-up due is already persisted on sequence one by Background's recovery-outreach finalization flow; API reads that snapshot without introducing a second delay or policy resolver. Validation reflects the local database submodule revision `807af33`.

### Unresolved Issues

- None. Implementation publication, the validated database pin, and the focused validation were verified against the canonical task worktree.

### Architectural Concerns

No Shopify/Background source, schema migration, queue, billing, or new infrastructure was modified for this correction. Provider delivery and usage accounting remain Background-owned. Do not enable dependent tasks until the configured developer review/completion lifecycle is satisfied.

## Architect Review

### Review Status
Developer Self-Review Passed/Accepted — 2026-10-21. Explicit developer completion was requested and is recorded separately after this durable review transition.

### Review Notes
The configured follow-up due-time correction is implemented within API ownership. The decision table and integration coverage exercise verified inbound windows, configured due timestamps, replay, tenant isolation and single sequence-two admission.

### Reviewed Files
`src/merchant/conversations/messages/eligibility.ts`, `src/merchant/conversations/messages/admission.service.ts`, focused unit/PostgreSQL tests, harness, and database gitlink at implementation commit `143fe2678d130a2c33d48de60775e1992ac6dfb2`.

### Validation Reviewed
Focused unit suite 5/5; disposable PostgreSQL API-004/API-005 suites 2/2 with 58 migrations; typecheck, lint, build, and `git diff --check` passed on the published implementation branch. The database gitlink matches the tested revision `807af3393f992c8a19bc9ef278d7e7e05f41799d`.

### Architecture Conformance
Accepted. No independent delay, fallback scheduler, schema or cross-repository runtime change was introduced. Existing transaction locks, replay ordering, tenant checks, moderation boundary and sequence-two claim were retained.

### Follow-up
No remaining API-005 work item or acceptance criterion is incomplete. Downstream tasks remain governed by their explicit dependency sets and system-test manual gate.

## Developer Self-Review Passed/Accepted — Attempt 1

The current attempt satisfies the scoped Work Items and Acceptance Criteria. The configured follow-up is admitted only after the service window closes and the persisted sequence-one `followUpDueAt` is non-null and due; free-text eligibility still uses the latest provider-verified customer inbound window with exact expiry excluded. The existing tenant, replay, moderation, locking and sequence-two ownership constraints remain intact.

Validation passed on published implementation commit `143fe2678d130a2c33d48de60775e1992ac6dfb2`: focused unit tests 5/5, disposable PostgreSQL suites 2/2 (58 migrations; database submodule `807af3393f992c8a19bc9ef278d7e7e05f41799d`), typecheck, lint, build, and diff check. Parent branch synchronization merged current `origin/main` into `task/ARCH-040-API-005`; implementation branch is clean and pushed. No required API-005 criteria remain incomplete.

Review accepted. Because `completion_mode: developer`, this passing review alone does not complete the task; explicit developer completion is pending.
