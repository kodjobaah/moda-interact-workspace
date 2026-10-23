---
id: ARCH-040-BACKGROUND-008
architecture_id: ARCH-040
title: Enforce verified customer window and configured follow-up at final dispatch
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-040-BACKGROUND-002
  - ARCH-040-BACKGROUND-006
  - ARCH-040-BACKGROUND-007
enables:
  - ARCH-040-SYSTEM-TEST-001
  - ARCH-040-SYSTEM-TEST-002
  - ARCH-040-SYSTEM-TEST-003
created: 2026-10-20
updated: 2026-10-23
---

# ARCH-040-BACKGROUND-008 — Platform-neutral eligibility at provider dispatch

## Architecture

ARCH-040 parent: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`; `moda_background` owns `moda-interact-background`. The task was claimed as Attempt 1 by the canonical launcher on 2026-10-23 and explicitly taken over for developer execution. **No dependency on Shopify, WooCommerce or hosted Woo API.** BG007 is a prerequisite because it modifies the same sequence-2 claim/release lifecycle.

## Objective

Ensure recovery-linked Human and AI outbound messaging obeys the **latest verified CUSTOMER inbound 24-hour free-text window** and the **existing configured recovery follow-up time** at the final provider admission boundary, irrespective of the merchant's e-commerce platform. Preserve the existing BullMQ queues and one PostgreSQL human-command dispatcher.

## Confirmed current code surfaces

| Existing file | Exact change |
|---|---|
| `src/services/recovery-conversation/recovery-conversation.sql.ts` | Add a recovery-bounded, provider-verified customer inbound and persisted initial-outreach/due-time query usable under existing transaction locks. Do not treat `Conversation.lastInboundAt` as sufficient authorisation evidence. |
| `src/services/recovery-conversation/recovery-follow-up-policy.service.ts` | Make `checkServiceWindow`, `validateHumanFollowUp` and `claimSequenceTwo` use verified inbound for window checks; HUMAN template claims also check the established `followUpDueAt`. Preserve existing sequence-2 claim identity and BG007 release semantics. |
| `src/services/recovery-conversation/outbound-send-fence.service.ts` | In the short PostgreSQL final-permit transaction, recheck actual inbound window for HUMAN_TEXT/AI free text and configured-due/closed-window/single-claim eligibility for HUMAN follow-up templates. No provider/Redis/OpenAI call in transaction. |
| `src/services/recovery-conversation/human-command-dispatcher.service.ts` and `human-command-evaluation.service.ts` | Use the shared policy rather than a separate platform-specific timer. Cancel/reconcile safely if command becomes ineligible before permit. |
| `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts` | Retain configured delayed BullMQ jobs and no-response suppression after engagement; do not schedule on 24-hour expiry or add a second follow-up. |

## Requirements

1. **Authoritative evidence.** A recovery conversation's latest service-window opener is the newest row with `direction=INBOUND`, `senderType=CUSTOMER`, non-null `providerMessageId`, `initial.sequence1.sentAt <= createdAt <= capturedNow`, ordered `createdAt DESC,id DESC`. Query inside the existing final-admission transaction with Shop -> Conversation -> command/attempt row-lock ordering. Unsupported/unverified, pre-initial or future rows never open the window. Leave non-recovery flows unchanged.
2. **Free-text window.** With verified inbound at `V`, HUMAN or AGENT free text may be admitted only for `V <= now < V+24h`, subject to normal conversation ownership and content checks. At exactly `V+24h`, deny. Without verified inbound, deny. Queued commands whose window expires before dispatch must be suppressed despite earlier API acceptance.
3. **Configured follow-up.** Deliberate HUMAN `RECOVERY_FOLLOW_UP_TEMPLATE` requires sent sequence 1, no open verified customer window, `initial.followUpDueAt != null && initial.followUpDueAt <= now`, an available sequence-2 claim and approved recipient/template/entitlement. Null means disabled/not scheduled: fail closed. **Never impose an additional `initialSentAt+24h` fixed wait.** Do not re-compute due time from mutable settings; use the effective policy/due-time snapshot recorded for the recovery.
4. **Scheduled no response.** The existing BullMQ sequence-2 job remains governed by `followUpDueAt` and the no-response rule. If a verified customer responded since initial outreach, scheduled AUTOMATION remains suppressed even after their 24-hour window later expires. No automatic new job on expiry. A merchant may deliberately initiate the single follow-up after prior engagement only when it is due, window closed and unclaimed.
5. **Final fencing and cancellation.** Retain current mode/revision, tenant isolation, human suspension, abuse/moderation approval for exact content, recipient suppression, recovery entitlement, provider permit and billing checks. Preserve BG007's conditional pre-provider cancellation/release ordering. No release, resend or double credit for provider-`UNKNOWN` or already admitted sends.
6. **Platform neutrality.** No `SHOPIFY`/`WOOCOMMERCE` branch, new producer API, queue, cron, worker, database table, generic package or duplicate WhatsApp sender. Both platforms commit identical commands; Background owns the common policy.
7. **Failure safety.** Missing initial `sentAt`, `followUpDueAt` or verified inbound denies the corresponding send; never guess a clock value or enable a template without configured evidence. If the configured due-time producer is missing for eligible recoveries, return a concrete gap to architect rather than silently invent another scheduler.

## Exact decision matrix

`S` = initial sent; `D` = effective persisted follow-up due (null if disabled); `V` = verified latest CUSTOMER inbound since `S`; `W` = 24h. All columns remain subject to normal recovery, ownership, recipient, provider and moderation gates.

| State | HUMAN/AI free text | Human follow-up template | Scheduled no-response |
|---|---|---|---|
| `V` within W | Eligible in current appropriate mode | Deny: window open | Suppressed: engaged |
| `V` expired, `D <= now` | Deny | Eligible if sequence 2 free | Suppressed: engaged |
| No `V`, `D <= now` | Deny | Eligible if sequence 2 free, even before `S+24h` | Eligible at scheduled due if unengaged |
| No `V`, `D > now` or null | Deny | Deny | Not due/disabled |
| Unverified/pre-initial/future inbound only | Deny | Treat as no `V` | Preserve the existing no-response engagement check; do not loosen it |
| Missing `S`, terminal, already-used sequence 2 | Deny | Deny | Deny |

Do not infer that a static approved Meta recovery template becomes free-text because the customer window is open; template eligibility is separate from free-text admission.

## Work Items

- [x] Inspect accepted BG007 code and current outbound/follow-up/dispatch call sites before implementation.
- [x] Add one shared provider-verified inbound plus persisted effective follow-up due selector; reuse the existing short PostgreSQL final-admission transaction.
- [x] Update HUMAN/AI free-text checks and HUMAN template claim/fence checks to consume the same evidence.
- [x] Preserve existing delayed BullMQ no-response and merchant DB-poller registration unmodified.
- [x] Add transaction/worker tests for expiry at exact 24h, new inbound, 15m/60m/48h configured delays, no reply, disabled/null/future due, unverified/pre-initial/future rows, queued crossing expiry, two contenders, takeover and provider-unknown safety.
- [x] Record evidence of configured due-time producer and safe BG007 cancellation/release; report any upstream gap without implementing outside scope.

## Interfaces / Contracts

Existing Prisma `ConversationMessage`, sequence-1/2 `RecoveryOutreachAttempt`, `RecoveryFollowUpPolicyService`, `OutboundSendFenceService`, Human dispatcher, existing billing and provider transport. No new table or external API. `followUpDueAt` is **configured follow-up timing evidence**, not a WhatsApp service-window opener.

## Dependencies

- ARCH-040-BACKGROUND-002 — Complete in supplied snapshot.
- ARCH-040-BACKGROUND-006 — Complete in supplied snapshot.
- ARCH-040-BACKGROUND-007 — Ready in supplied snapshot; must be accepted Complete first.

## Enables

- ARCH-040-SYSTEM-TEST-001.
- ARCH-040-SYSTEM-TEST-002.
- ARCH-040-SYSTEM-TEST-003.

## Acceptance Criteria

- [x] Final permit never authorises recovery free text without recent verified CUSTOMER inbound; exact 24-hour expiry and replay/retry behaviour are correct.
- [x] HUMAN recovery follow-up is controlled by configured due time and closed verified window, not a newly invented 24-hour delay from initial outreach.
- [x] Scheduled no-response timing and engaged-customer suppression remain unchanged; service-window expiry alone produces no job.
- [x] Existing one-thread/one-sequence-2/one-credit, BG007 safe release, moderation, ownership and provider-uncertain protections remain intact.
- [x] No new queue, scheduler, database migration or platform-specific code.

## Validation

- [x] Focused unit, PostgreSQL and existing worker integration tests with deterministic clocks and mocked Meta; run actual declared typecheck/build/lint and `git diff --check`. Record results; developer/system-test certification remains separate.

## Implementation Notes

Avoid calling a remote provider inside the DB transaction. Keep shared logger redaction. If current worker prepares a message before the 24-hour cutoff but final permit occurs afterward, **the final permit must deny**; an already irreversible permit cannot be recalled. No changes to BG007's accepted task definition.

## Stop Condition

Implement only the defined changes, report actual results, set `review`, return to moda_architect and STOP.

## Completion Report

### Status
Ready for Review — developer-executed Attempt 1, claimed by the canonical launcher at `2026-10-23T12:34:09Z`. The four delivery-patch iterations (Attempts 1–4) are corrections within this **single claimed task attempt**; the task frontmatter `attempt: 1` is unchanged. Awaiting architectural review and subsequent explicit developer completion.

### Files Changed
Implementation repository: `kodjobaah/moda-interact-background`, branch `task/ARCH-040-BACKGROUND-008`, commit `f8962121c3f825f0129ccb99247cf6f9348c3442` (pushed 2026-10-23):

- `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`
- `src/services/recovery-conversation/human-command-dispatcher.service.ts`
- `src/services/recovery-conversation/human-command-evaluation.service.ts`
- `src/services/recovery-conversation/outbound-send-fence.service.ts`
- `src/services/recovery-conversation/recovery-conversation.sql.ts`
- `src/services/recovery-conversation/recovery-follow-up-policy.service.ts`
- `tests/integration/fixtures/arch040-ai-turn.fixture.ts`
- `tests/integration/fixtures/arch040-window.fixture.ts` (new)
- `tests/integration/fixtures/recovery-human-dispatch.fixture.ts`
- `tests/integration/recovery-conversation.services.integration.test.ts`
- `tests/integration/recovery-human-dispatch.integration.test.ts`
- `tests/integration/recovery-verified-window-and-due.integration.test.ts` (new)
- `tests/unit/services/recovery-conversation/recovery-verified-window.test.ts` (new)

The implementation commit changes 13 files (641 insertions, 54 deletions). No schema/migration, Shared package, new queue/cron, Shopify/WooCommerce branch or domain `_index.md` change is included.

### Work Completed
- Inspected the accepted BG007 release/final-permit model and the outbound, dispatcher, eligibility and delayed follow-up call sites. The existing configured-delay producer in `recovery-outreach-finalization.service.ts` persists `followUpDueAt` from the effective follow-up policy when sequence 1 is finalised.
- Added a recovery-scoped selector for provider-verified CUSTOMER inbound messages from sequence-1 sent time through captured now, using the existing PostgreSQL admission boundary; unverified, pre-initial and future inbound messages do not open the customer window.
- Updated HUMAN and AGENT free-text preflight and final admission to require the latest verified customer reply within the strict 24-hour window (denied at exactly expiry); recheck after transaction locking so stale queued commands cannot gain an irreversible provider permit.
- Enforced persisted `followUpDueAt` and closed verified window on intentional HUMAN template follow-up claims and final dispatch. Preserve the configured due-time semantics (including 15-minute, 60-minute and 48-hour examples), null/disabled fail-closed behaviour, one sequence-2 claim and scheduled no-response engagement suppression; no invented 24-hour wait or expiry-driven job.
- Preserved accepted BG007 cancellation/release, provider UNKNOWN/admitted safety, moderation, tenant/recipient controls and one-credit accounting. Kept the existing BullMQ follow-up scheduler and merchant polling architecture unchanged.
- Added verified-window/due-time unit and PostgreSQL integration coverage; corrected fixture revision/timestamp, initial-outreach and reserved-credit setup, receipt compensation lineage, and one nondeterministic stale-lease test ordering. These latter corrections changed tests only, not the production window policy.

### Validation Results
- **PASS:** `npm run test -- tests/unit/services/recovery-conversation/recovery-verified-window.test.ts tests/unit/services/recovery-conversation/recovery-conversation-services.test.ts` — **25/25 tests**, 2 files (focused unit run after Attempt 1).
- **PASS:** `npm run test:integration -- tests/integration/recovery-human-dispatch.integration.test.ts --maxWorkers=1` — **28/28 tests** in the isolated final lease/dispatch regression run.
- **PASS:** `npm run test:integration -- tests/integration/recovery-verified-window-and-due.integration.test.ts tests/integration/recovery-conversation.services.integration.test.ts tests/integration/recovery-human-dispatch.integration.test.ts tests/integration/recovery-follow-up-claim-races.integration.test.ts tests/integration/recovery-follow-up-purchased-release.integration.test.ts --maxWorkers=1` — **64/64 tests**, 5 files on disposable PostgreSQL after the fourth correction.
- **PASS:** `npm run build` — Prisma Client generation and TypeScript compilation succeeded in the final validation run.
- **PASS:** `npm run lint` (`eslint .`) — latest supplied terminal output shows completion with no lint diagnostics.
- **PASS:** `git diff --check` and `git diff --cached --check` produced no errors before the commit; commit `f8962121c3f825f0129ccb99247cf6f9348c3442` and explicit push to `origin task/ARCH-040-BACKGROUND-008` succeeded.
- **Not run:** the entire repository unit/integration suite or integrated platform system-test certification; the task's focused validation was completed. Earlier Attempts 1–3 had fixture/lineage/test-race failures, resolved and retested successfully in Attempt 4.

Launcher/worktree evidence preserved from this task's Developer Takeover:

- Parent task claim commit: `85c80122ba13677476d258b922e25743e04488c7`, with mirrored branch `task/ARCH-040-BACKGROUND-008`; canonical launch claimed Attempt 1 at `2026-10-23T12:34:09Z`.
- Dedicated implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-040-BACKGROUND-008`, on `task/ARCH-040-BACKGROUND-008`.
- Launcher recorded recursive submodule synchronization and nested database pin `2e009298612133aace095db5d57245a5b01e773a`.
- The latest implementation worktree `git status` had only an untracked local `typescript` terminal-log file, which was **not** included in the 13-file commit. No tracked changes were pending after commit.
- The original launcher packet's full Git common-dir/parent worktree physical isolation details were not independently reproduced in the supplied validation logs; the architect can verify them against the launcher evidence before final acceptance.

### Deviations
No production-scope or ownership deviation. Integration fixtures required bounded corrections over four delivery-patch iterations: matching ARCH040 control revision/time constraints; real reservation usage/lineage for ARCH028 receipt compensation; and deterministic ordering for a stale lease test that previously raced `FOR UPDATE SKIP LOCKED` under parallel transactions. The final production policy code was unchanged after Attempt 1.

### Assumptions
- Provider-verified inbound messages with persisted `providerMessageId` are the service-window evidence for recovery-linked free text; `Conversation.lastInboundAt` alone is not authoritative.
- The existing sequence-1 effective `followUpDueAt` snapshot and BG007 final-permit/cancellation fencing remain authoritative. The new implementation does not recompute due time from mutable settings or release credits after uncertain/provider-admitted sends.

### Unresolved Issues
No unresolved failures in the focused unit, PostgreSQL integration, build or lint validation. Independent integrated platform system tests remain outside this repository task. The reviewer should inspect the original launcher packet if additional Git common-dir isolation evidence is required.

### Architectural Concerns
No new database/Shared contract, external API, platform-specific branch or scheduled worker is required. The reviewer should confirm that original BG007 cancellation/release and sender-mode gating still conform to ARCH-040 across production consumers, rather than treating passing isolated tests as system-test certification.

## Architect Review

### Review Status
Pending.

### Review Notes
Not reviewed.

### Reviewed Files
October 20 Background service policy/SQL/final fence and recovery follow-up processor.

### Validation Reviewed
Static source only.

### Architecture Conformance
Pending implementation.

### Follow-up
None.

## Developer Takeover

On 2026-10-23, `/moda_developer_create ARCH-040-BACKGROUND-008` was invoked while this task was ready and agent-owned. The canonical launcher claimed Attempt 1 at `2026-10-23T12:34:09Z`, committed the parent claim as `85c80122ba13677476d258b922e25743e04488c7`, and created the implementation worktree at `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-040-BACKGROUND-008` on `task/ARCH-040-BACKGROUND-008`. Recursive submodule synchronization passed; the `database` submodule is initialized at `2e009298612133aace095db5d57245a5b01e773a`.

This is an explicit developer takeover. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_background`, repository ownership, dependencies, scope and acceptance criteria are unchanged.
