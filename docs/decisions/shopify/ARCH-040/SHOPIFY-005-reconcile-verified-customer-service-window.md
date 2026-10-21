---
id: ARCH-040-SHOPIFY-005
architecture_id: ARCH-040
title: Reconcile verified customer service-window and configured recovery follow-up
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 30
executor: developer
claimed_at: 2026-10-21T15:11:56Z
attempt: 1
depends_on:
  - ARCH-040-SHOPIFY-001
enables:
  - ARCH-040-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-21
---

# ARCH-040-SHOPIFY-005 — Verified service window and configured follow-up

## Architecture

- Parent: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`.
- Owner: `moda_app` in `moda-interact`; coordinator: `moda_architect`.
- Originally supplied as a portable definition; the live task is materialized in the workspace. `ARCH-040-SHOPIFY-001` was verified `complete` through the canonical launcher before this claim.
- **Policy approved 2026-10-20:** verified customer inbound opens a rolling 24-hour free-text window. When that window is closed (or there has been no reply), only the existing **configured recovery follow-up** may be initiated through an approved template, provided it is enabled, due, otherwise eligible and the single sequence-2 attempt remains available. **There is no additional fixed 24-hour wait after initial outreach.**

## Objective

Correct the existing Shopify Recovery Detail command admission and read-side guidance to enforce the above policy using verified persisted inbound evidence and the recovery's existing effective follow-up configuration. Do not duplicate the WooCommerce API or Background implementation.

## Context / exact existing integration points

- `moda-interact/app/services/recoveries/recovery-human-commands.server.ts`: `admitRecoveryHumanSend()` currently picks customer inbound rows without a non-null `providerMessageId`, without a bounded `[initial.sentAt, now]` interval, and permits a merchant template as soon as initial outreach was sent.
- `moda-interact/app/services/recoveries/recovery-detail.server.ts`: `readRecoveryDetail()` derives `lastInboundAt`, `windowExpiresAt` and `followUp.eligible` from an unchecked inbound selection and an unused sequence-2 attempt.
- Existing persisted configuration/evidence: `ShopSettings.followUpEnabled`, `ShopSettings.followUpDelayMinutes`, applicable `ShopRecoveryPolicyOverride`, and the resolved, durable `RecoveryOutreachAttempt` sequence-1 `followUpDueAt`. **Use the already-resolved recovery policy/due time as the recovery-specific authority.** An absent due time means do not invent a new follow-up time; fail closed and report any missing upstream scheduling evidence.
- Woo API-004 is an **existing behaviour reference only**, not a dependency or a code-edit target. Its `initialSentAt + 24h` merchant-template requirement contradicts the agreed setting-based rule and is owned by API-005.

## Scope

1. In `admitRecoveryHumanSend()` capture one server `now` per transaction, under the existing shop/recovery/conversation locks and with idempotent replay lookup **before** new eligibility checks.
2. Select the newest `ConversationMessage` with the same recovery conversation, `direction=INBOUND`, `senderType=CUSTOMER`, `providerMessageId IS NOT NULL` and `initial.sentAt <= createdAt <= now`, ordered `createdAt DESC, id DESC`. No other row can open a HUMAN text window.
3. For `HUMAN_TEXT`, allow only when that verified latest inbound exists and `inbound.createdAt <= now < inbound.createdAt + 24h`. At exact expiry the window is closed. Customer replies reset this window, not the ownership mode or sequence-two allowance.
4. For `RECOVERY_FOLLOW_UP_TEMPLATE`, require the initial outreach to have been sent, the text window to be closed, **the effective recovery follow-up to be enabled and already due** using the established persisted sequence-1 `followUpDueAt <= now`, and the one sequence-2 attempt to be unclaimed and otherwise eligible. No hardcoded `initial.sentAt + 24h` gate. If settings disabled/unscheduled, due time absent or future, deny.
5. Preserve current control mode/revision, shop isolation, terminal recovery, active entitlement, provider-approved template/recipient checks, moderation, restriction and recovery claim/idempotency paths. No direct Meta/Redis calls, new scheduler or billing logic.
6. Make `readRecoveryDetail()` return advisory `lastInboundAt` and `windowExpiresAt` from the same verified inbound rules; `followUp.eligible` must additionally respect configured due time, closed customer window, initial sent state, sequence-2 availability and existing bounded eligibility inputs. Advisory UI state is never an authorisation token.
7. Keep `/app/recoveries/:recoveryId` and the existing basket/transcript/takeover/composer. Reuse existing UI and safe reason codes; do not add a Conversations page or duplicate component hierarchy.
8. **Architect-approved, one-file baseline correction (2026-10-21):** in `app/services/platform-configuration/seal.server.ts`, normalise an unseal/decryption failure to the existing typed `"UNSEAL_FAILED"` code without appending an underlying exception message. This is an expressly authorised, bounded Shopify-owned typecheck and error-redaction fix, not a platform-configuration refactor.

## Out of Scope

- No change to the scheduled AUTOMATION `NO_RESPONSE_FOLLOW_UP`: it still runs at the **existing configured due time** through BullMQ only when the customer has not engaged, and is suppressed after a customer reply.
- No WooCommerce API, Background, database, provider, credits or schema edits in a Shopify task. API-005 and BACKGROUND-008 own their respective corrections.
- No new rolling 24-hour follow-up timer, no mandatory 24-hour delay from initial recovery, no extra attempts or separate conversation.
- No `docs/decisions/**/_index.md` modification.
- The Shopify task must not advance the `database` submodule into unrelated schema/migration work. Restoring the task branch gitlink to the `origin/main` pin `caee3df` is a scope correction only, not authorisation to edit database source.
- Other platform-configuration changes remain out of scope; the sole approved exception is the `seal.server.ts` `UNSEAL_FAILED` error-code correction described in Scope.

## Exact eligibility matrix

`S` = persisted sequence-1 `sentAt`; `D` = persisted effective `followUpDueAt` (`null` when unavailable/disabled); `V` = latest verified customer inbound in `[S, now]`; `W` = 24 hours. All cases also require Human mode and current revision, eligible shop/recovery/recipient, an approved template and an unused sequence 2.

| Case | HUMAN_TEXT | HUMAN follow-up template |
|---|---|---|
| No `S` | Deny | Deny |
| Verified `V`, `now < V + W` | Allow | Deny (window open) |
| Verified `V`, `now = V + W`, `D <= now` | Deny | Allow |
| Verified `V`, window closed, `D > now` or `D = null` | Deny | Deny (not configured/due) |
| No `V`, `D <= now` | Deny | Allow; **no invented 24h wait from S** |
| No `V`, `D > now` or `D = null` | Deny | Deny |
| Only unverified, future or pre-`S` inbound | Treat as no `V` | Apply configured due and other safeguards |
| Sequence 2 already claimed, sent or provider-uncertain | Applicable text window only | Deny regardless of settings |
| Exact idempotency replay of an accepted command | Return same command | Return same command without another claim |

**Example:** follow-up enabled with effective delay 60 minutes and persisted `D=S+60min`, with no verified customer reply: the single approved template may become eligible at `D`, rather than `S+24h`. A delay of 48 hours remains 48 hours. If the customer has replied, Human free text follows their rolling 24-hour window; the configured follow-up is never automatically sent solely because that window expires.

## Work Items

- [x] Inspect accepted Shopify admission/read code and persisted effective recovery-policy/due-time source; verify why/when `followUpDueAt` is populated and how disabled settings appear.
- [x] Implement verified-inbound selection with a single captured `now` and exact 24-hour boundaries.
- [x] Implement setting/due-based HUMAN template admission, preserving existing transaction and idempotency order.
- [x] Align the Recovery Detail read-side window/follow-up advisory with server eligibility; preserve established DTO and UI.
- [x] Add focused deterministic fixtures for the full matrix and settings enabled/disabled/shorter/longer delays.
- [x] Record Woo API and Background ownership gaps as separate implementation dependencies; do not edit those repositories.
- [x] Apply the expressly approved `seal.server.ts` error-code correction without exposing underlying decryption errors; validate with its focused unit tests, typecheck and lint.
- [x] Restore the unrelated `database` gitlink from `807af33` to the original Shopify baseline `caee3df`, then validate and publish the corrective implementation commit. No database code, migration or script edits.

## Interfaces / Contracts

- Existing Shopify server: `admitRecoveryHumanSend(shopId, recoveryId, input, db)` and `readRecoveryDetail(...)`.
- Canonical persisted inputs: sequence-1 `sentAt/followUpDueAt`, sequence-2 `RecoveryOutreachAttempt`, verified `ConversationMessage`, immutable merchant command. No new schema or shared library.
- Independent parity owners: `ARCH-040-API-005` for Woo command admission, `ARCH-040-BACKGROUND-008` for final common runtime admission. **SHOPIFY-005 depends on neither.**

## Dependencies

- ARCH-040-SHOPIFY-001 (Complete in supplied snapshot).

## Enables

- ARCH-040-SYSTEM-TEST-002.

## Acceptance Criteria

- [x] Verified latest CUSTOMER inbound alone determines the rolling 24-hour HUMAN free-text window, including exact expiry and renewed inbound.
- [x] HUMAN approved follow-up is governed by the existing effective recovery configuration and persisted due time, not by a new 24-hour post-initial delay; disabled, missing and not-yet-due cases fail closed.
- [x] The same sequence-2 attempt and credit identity are retained. No second conversation or new scheduling mechanism is introduced.
- [x] Recovery Detail advisory uses the same trusted inbound and due-time evidence; server commands remain authoritative.
- [x] Existing authenticated tenant scope, idempotent replay, control mode/revision, moderation and restrictions remain intact; no Woo/Background changes are made in this task.

## Validation

- [x] Focused tests for `recovery-human-commands.server.ts` and recovery-detail reader, covering exact boundaries, configured 15m/60m/48h examples, disabled/null due, pre-initial/future/unverified inbound, control and replay.
- [x] Typecheck, lint, build and `git diff --check` using actual declared scripts; capture results in Completion Report. Developer's later integrated/browser validation remains separate from implementation acceptance.

## Stop Condition

Once the defined work and functional acceptance criteria are implemented, report the actual validation performed, set status to `review`, return to moda_architect and STOP. Do not implement cross-repository corrections or run terminal system tests.

## Implementation Notes

Use the existing authenticated Shopify server transactions. Do not re-resolve an arbitrary new due time from mutable UI settings when the initial outreach has a persisted effective due-time snapshot. If upstream persistence is missing for an enabled recovery, report the concrete gap; never infer a default and accidentally send early. Do not log message bodies or credentials.

## Completion Report

### Status
Developer Attempt 1 implementation is complete and submitted for architect review; canonical lifecycle remains **in progress** until review reconciliation, with the original claim and attempt unchanged. Recovery implementation `3b6e7739165cb752ce01930570e0f85ca223e79f`, approved sealing correction `b5d5080ebab219f2eecc3e0c233f53930369085b`, and gitlink-only scope correction `ad61f2e627e5e75bc60707620a068812b199a01c` are published on `task/ARCH-040-SHOPIFY-005`. The implementation worktree is clean at `ad61f2e`; local and remote heads match, and the `database` gitlink is restored to `caee3df61dbb38c8319ebcd3cfaf68522743245e`. No database source changes were made. No Complete transition or downstream promotion is requested.

### Files Changed
- Published recovery implementation `3b6e773`: `app/services/recoveries/recovery-detail.server.ts`, `recovery-human-commands.server.ts`, `recovery-service-window.ts`, and focused `tests/unit/arch040-shopify-command.test.ts`, `arch040-shopify-service-window.test.ts`, `recovery-detail-readers.test.ts`.
- Published one-file baseline fix `b5d5080`: `app/services/platform-configuration/seal.server.ts` (normalised `UNSEAL_FAILED` without underlying exception text).
- Gitlink-only scope correction `ad61f2e` restores the nested `database` pointer from `807af3393f992c8a19bc9ef278d7e7e05f41799d` to baseline `caee3df61dbb38c8319ebcd3cfaf68522743245e`; no nested database files changed.

### Work Completed
- Implemented the ARCH-040 Shopify verified-inbound and configured-follow-up admission/read-policy changes and deterministic service-window fixtures in the published task branch (final task-wide architecture review pending).
- Corrected the existing Shopify sealed-configuration error path to call `configurationFailure(input.key, "UNSEAL_FAILED")` without concatenating provider exception text, under the narrowly approved scope exception.
- Published `ad61f2e627e5e75bc60707620a068812b199a01c`, a forward, gitlink-only correction restoring the original database baseline; implementation head and remote match, and the worktree is clean.

### Validation Results
- `npm test -- tests/unit/arch040-shopify-command.test.ts tests/unit/recovery-detail-readers.test.ts tests/unit/arch040-shopify-service-window.test.ts` — **PASS, 86/86** across three files after the due-time fixture correction (earlier supplied terminal evidence).
- `npm test -- tests/unit/platform-configuration/service.test.ts` — **PASS, 7/7** on 2026-10-21 following the sealed-configuration baseline correction.
- At corrected head `ad61f2e`, `npm test -- tests/unit/arch040-shopify-command.test.ts tests/unit/recovery-detail-readers.test.ts tests/unit/arch040-shopify-service-window.test.ts tests/unit/platform-configuration/service.test.ts` — **PASS, 93/93** across four files.
- At corrected head `ad61f2e`, `npm run typecheck` (`react-router typegen && tsc --noEmit`) — **PASS**, completed without reported errors.
- At corrected head `ad61f2e`, `npm run lint` (`eslint --ignore-path .gitignore --cache --cache-location ./node_modules/.cache/eslint .`) — **PASS**, completed without reported errors.
- At corrected head `ad61f2e`, `npm run build` — **PASS**; Prisma Client regenerated from the restored `database/prisma/schema.prisma`. Build emitted bundler notices for dependency annotations/Prisma browser resolution/empty route chunks and a large chunk, but no build errors.
- At corrected head `ad61f2e`, `git diff --check origin/main...HEAD` and `git diff --check` — **PASS**, no whitespace errors.
- Final implementation worktree is clean; `HEAD` equals `origin/task/ARCH-040-SHOPIFY-005` at `ad61f2e627e5e75bc60707620a068812b199a01c`; nested `database` checkout and gitlink both resolve to `caee3df61dbb38c8319ebcd3cfaf68522743245e`.

### Deviations
- **Explicitly approved 2026-10-21:** the pre-existing, same-repository `seal.server.ts` concatenated an exception message onto the closed `ShopifyConfigurationErrorCode`, failing TypeScript and risking disclosure of underlying decryption diagnostics. The one-file replacement emits only `UNSEAL_FAILED`; no additional platform-configuration behaviour is authorised.
- **Corrected scope deviation:** the nested database pointer was restored to the approved `caee3df` baseline in forward commit `ad61f2e`; the earlier `3b6e773` history remains unchanged, and no database source or migration was modified.

### Assumptions
`followUpDueAt` is the recovery's existing resolved scheduled due time; verify its actual producer in the current implementation before coding.

### Unresolved Issues
No outstanding 24-hour post-initial policy decision: setting-based follow-up timing is approved.
The `seal.server.ts` correction remains within its approved bounded scope. The gitlink restoration and corrected-head validation are complete. Full architect review remains pending; do not increment the claim or attempt solely for review reconciliation.

### Architectural Concerns
Any unavailable policy snapshot/producer is returned to moda_architect rather than worked around by inventing a new delay.

## Architect Review

### Review Status
Pending.

### Review Notes
Policy recorded; task-wide implementation is not yet architect-accepted. **Scope exception approved on 2026-10-21:** the one-file `app/services/platform-configuration/seal.server.ts` catch-path correction emits only the typed `UNSEAL_FAILED` code without exposing decryption error text; this was published at `b5d5080`. **Database pin review:** the diff from `caee3df` to `807af33` is exclusively an unrelated operational-incident diagnostics migration and support scripts. The recovery policy depends on the existing `caee3df` baseline, not that extra commit. Restore the gitlink in a forward task commit before final review. This record does not approve the full implementation or advance dependencies.

### Reviewed Files
Existing Shopify admission/read, ARCH-040 architecture, Woo API eligibility and Background policy files.

### Validation Reviewed
Static snapshot inspection and developer-provided 2026-10-21 focused Shopify test results (86/86), sealed-configuration tests (7/7), consolidated rerun (93/93) at `b5d5080`, and typecheck/lint/whitespace evidence. Git commit comparison confirms the unrelated `807af33` pin contents. Full implementation review and corrected-head validation remain Pending.

### Architecture Conformance
Pending implementation.

### Follow-up
1. Restore the Shopify `database` gitlink from `807af33` to `caee3df` using a new commit on the existing task branch, without rewriting `3b6e773` or `b5d5080`.
2. Regenerate Prisma Client against the restored database submodule and rerun the four focused test files, repository typecheck, and Git whitespace check. Run lint/build if required by the current task validation contract; record commands and exact outcomes.
3. Update the Completion Report with the new commit SHA and validated, clean implementation head; return through the existing developer review path. Keep `status: in_progress`, `attempt: 1`, and the current claim until review reconciliation; do not mark Complete or promote SYSTEM-TEST-002.

### Developer Response — 2026-10-21
All three follow-ups are complete at implementation head `ad61f2e627e5e75bc60707620a068812b199a01c`: the gitlink points to `caee3df`, Prisma Client was regenerated, the four focused test files passed 93/93, typecheck/lint/build passed, and both whitespace checks passed. The implementation worktree is clean and matches the remote task branch. Developer Attempt 1 remains active and the canonical task status remains `in_progress` pending architect review; no completion or downstream system-test transition is made here.

## Developer Execution Ownership Amendment

The developer explicitly invoked `/moda_developer_create ARCH-040-SHOPIFY-005` for this agent-owned, ready task. `assigned_agent: moda_app` remains the logical repository owner; execution and completion ownership are transferred to the developer for this task cycle.

- Previous execution mode: `agent`
- Previous completion mode: `automatic`
- New execution mode: `developer`
- New completion mode: `developer`
- Amendment date: 2026-10-21

## Developer Claim — Attempt 1

**Claimed — 2026-10-21T15:11:56Z.** The task transitioned from `ready`, attempt 0, null executor to `in_progress`, attempt 1, `executor: developer`. No portable task definition was materialized during this invocation; the canonical task definition was already present in the workspace. The canonical parent and implementation worktrees were created from their respective current `origin/main` commits because neither a local nor remote task branch existed.

- Dependency gate: `ARCH-040-SHOPIFY-001` resolves `complete` through the canonical launcher.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-040-SHOPIFY-005`, branch `task/ARCH-040-SHOPIFY-005`, based on `origin/main` at `1f9b27407820dde5e709b19c9b5c3b90a5838f95` before this claim commit.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-040-SHOPIFY-005`, branch `task/ARCH-040-SHOPIFY-005`, based on `origin/main` at `e69a4bc4ae44f5c8251071cf0268308bb0510982`.
- Both worktrees were clean at preparation and contain their current `origin/main`. The implementation package scripts were verified: `npm run test`, `npm run typecheck`, `npm run lint`, and `npm run build`.
- Implementation and validation have not been performed by this create workflow. No Woo API, Background, database, provider, credit, schema, or index files are in scope.
