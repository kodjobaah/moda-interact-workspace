---
id: ARCH-040-SHOPIFY-005
architecture_id: ARCH-040
title: Reconcile verified customer service-window and merchant follow-up eligibility
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-SHOPIFY-001
  - ARCH-040-API-004
enables:
  - ARCH-040-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# ARCH-040-SHOPIFY-005 — Verified customer service-window parity

## Architecture

- Initiative: `ARCH-040`.
- Parent: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`.
- Logical owner: `moda_app` (`moda-interact`); coordinator: `moda_architect`.
- **Defined but not materialised.** This portable task definition does not claim a branch, worktree, commit, push or execution attempt.
- **Blocked on one architecture policy decision:** the minimum delay for an explicit HUMAN follow-up template when there is **no verified CUSTOMER inbound**. The relevant choices and recommended resolution are recorded in the parent architecture's 2026-10-20 reconciliation note. The coordinator/developer must approve and record that decision, then promote this task to `ready`, **before execution claims or runtime edits**. Task agents must not silently choose a different policy.

## Objective

Make the existing authenticated Shopify Recovery Detail's HUMAN text/template admission and advisory window state consistently derive from verified CUSTOMER inbound WhatsApp events, with the same explicitly approved no-reply follow-up timing policy as the Woo hosted API and Background's final admission fences.

## Context

The merged Shopify implementation in the attached **2026-10-20 16:02** workspace has two concretely verified differences from Woo API-004:

1. `moda-interact/app/services/recoveries/recovery-human-commands.server.ts`, around lines 187–191, reads the latest `ConversationMessage` with `direction=INBOUND` and `senderType=CUSTOMER` but does **not** require a non-null `providerMessageId`, does **not** constrain `createdAt` to the interval from sequence-1 `sentAt` through the server's current time, and does not check the sequence-1 sent timestamp before admitting HUMAN free text. A pre-initial, future-dated or unverified row could therefore open a false free-text window.
2. The Shopify template branch around lines 194–197 rejects a template while this inferred window is open but accepts it **immediately** without a customer reply once sequence 1 has `sentAt`. Woo API-004 uses `merchantFollowUpWindowClosed(initialSentAt, latestVerifiedInbound, now)`, requiring at least 24 hours after initial outreach if no verified reply exists. This is a **product-policy discrepancy**; the WhatsApp customer-service window from verified customer inbound does not by itself establish an initial-outreach waiting period.
3. `moda-interact/app/services/recoveries/recovery-detail.server.ts`, around lines 41–49 and 84–90, projects the advisory `lastInboundAt`/`windowExpiresAt` from the same unchecked inbound rows and computes `followUp.eligible` from the unused sequence-two slot without the corresponding merchant follow-up timing gate. The UI can therefore display eligibility inconsistent with authoritative send acceptance.

Existing Woo reference: `moda-interact-api/src/merchant/conversations/messages/eligibility.ts` (`latestVerifiedCustomerInbound`, `windowOpen`, `merchantFollowUpWindowClosed`) and `.../admission.service.ts` (around lines 110–129). ARCH-040 invariant #5 and the parent concurrency section require a **verified CUSTOMER inbound** for the free-text service window. Woo's 24-hour no-reply minimum is an existing implementation, not yet separately approved as universal platform policy.

## Scope

- After the policy gate is closed, correct Shopify server-side HUMAN `HUMAN_TEXT` and `RECOVERY_FOLLOW_UP_TEMPLATE` eligibility in `app/services/recoveries/recovery-human-commands.server.ts`.
- Use only the latest verified inbound in the same recovery conversation: `direction=INBOUND`, `senderType=CUSTOMER`, non-null `providerMessageId`, and `createdAt >= sequence-1 sentAt` and `createdAt <= captured server now`. Preserve descending `(createdAt, id)` ordering. Do not rely on `Conversation.lastInboundAt` or an arbitrary outbound timestamp to open a customer window.
- Require sequence-1 `sentAt` before either category of HUMAN send may be accepted. Derive the text window as `[lastVerifiedInbound, lastVerifiedInbound + 24h)`; if no verified inbound, text is not permitted.
- Apply **the explicitly approved** no-verified-inbound merchant-template delay consistently with Woo API-004. **Recommended policy for approval:** an explicit merchant template may be eligible at or after `initialSentAt + 24h` when there is no verified inbound, or at or after `lastVerifiedInbound + 24h` when a later verified inbound closed the window; always subject to all existing recovery, sequence-two, template, restriction and recipient conditions. This minimum wait is a Moda merchant-contact policy, not a claim that WhatsApp's template transport prohibits earlier templates.
- Align the existing `readRecoveryDetail` advisory projection with the same verified source and the selected template eligibility policy; preserve existing DTO fields and avoid an extra UI/backend feature. The UI remains advisory and must not replace atomic server admission or Background's final provider checks.
- Add focused deterministic Shopify tests for the same boundary cases, plus a source-level parity comparison with the accepted Woo eligibility implementation.
- Preserve the existing authenticated Shopify shop/recovery scope and one-command/one-sequence-two-claim transaction.

## Out of Scope

- No edits to Woo API, WooCommerce plugin, Background workers, Prisma schema/migrations, Meta sender, billing, credits, moderation or shop restrictions. If policy approval requires a Woo or Background behavior change, return that dependency to `moda_architect` for a separate owner task; do **not** edit another repository.
- No change to the scheduled AUTOMATION `NO_RESPONSE_FOLLOW_UP` cadence/suppression. The deliberate HUMAN post-window template remains distinct from automated no-response recovery.
- No second conversation, additional sequence-two row, new queue/transport, new database entitlement, generic cross-service policy package, new merchant page or navigation, or speculative provider-timestamp infrastructure.
- No `docs/decisions/**/_index.md` edits until the user closes the architecture session.

## Requirements

1. Capture one server `now` for admission, exclude future-dated inbound and ignore pre-initial records, unverified provider-message records, OUTBOUND rows, and non-CUSTOMER sender types. No untrusted row may extend/reopen the HUMAN free-text 24-hour window.
2. For last valid inbound at `T`, free text is eligible only while `T <= now < T + 24h`. At exactly `T + 24h`, free text is closed. The next valid customer inbound may open a new window without changing HUMAN control mode or restoring a used sequence-two attempt.
3. No valid verified inbound means no HUMAN free text. Template eligibility in this case follows the **recorded policy decision**; under the recommended option it is unavailable until `initialSentAt + 24h` inclusive. When a valid inbound exists, a proactive template is prohibited while the resulting customer window is open.
4. An absent/unsent initial outreach fails closed for both send kinds. Retain all existing terminal-recovery, active entitlement, recipient reachability, shop restriction, approved template, current control revision and one-sequence-two-claim fences.
5. Do not change replay semantics: a matching idempotency-key retry returns its prior command **before** reevaluating the current window, without new claims/sends/credits; a conflicting replay still fails.
6. Keep the Shopify read projection's `lastInboundAt`, `windowExpiresAt` and `followUp.eligible` consistent with the same input trust rules and accepted merchant follow-up timing. No unavailable template should become an enabled UI action solely because sequence two is unused. At submit time the server makes the final determination.
7. The Shopify boundary remains provider-free: atomically create only durable commands and sequence-two claims; all moderation, provider dispatch, compensation and usage remain in Background.
8. Use existing safe response codes (`service_window_closed`, `follow_up_unavailable`, etc.), existing merchant UI patterns and shared structured logging. Do not log customer message bodies or credentials.

### Required policy decision and behavioral matrix

`V` = newest **verified** customer inbound in `[initialSentAt, now]`; `S` = initial sequence-1 `sentAt`; `W` = 24 hours. All rows assume otherwise-valid HUMAN control, entitlement, recipient, approved template and unclaimed sequence two.

| Input and server time | HUMAN_TEXT | HUMAN template (recommended policy) |
|---|---|---|
| `V` exists, `V <= now < V + W` | Allow | Deny: customer window still open |
| `V` exists, `now = V + W` | Deny | Allow |
| No `V`, `now < S + W` | Deny | Deny; **policy gate** |
| No `V`, `now >= S + W` | Deny | Allow, once only; **policy gate** |
| Unverified/pre-initial/future CUSTOMER records only | Same as no `V` | Same as no `V` |
| No `S`, or terminal/unsupported state | Deny | Deny |
| Matching previously admitted idempotency replay | Return prior command without re-admitting | Return prior command without re-claiming |

The **recommended** no-`V` rule shown above is not automatically approved by this task's creation. Architect/developer acceptance of the policy must be recorded in the parent architecture and task review, and the task must be moved from `blocked` to `ready` before coding begins. If a different product-policy resolution is chosen, amend this matrix and identify the affected API/Background owner before implementation.

## Work Items

- [ ] Coordinator records the agreed no-verified-inbound template waiting period in ARCH-040 and explicitly unblocks the task.
- [ ] Inspect current merged Shopify admission, detail DTO/read projection, existing Shopify test fixtures, Woo API-004 eligibility, and Background final-admission fence.
- [ ] Implement provider-verified, recovery-bounded CUSTOMER inbound selection using a captured server clock; make text/template admit decisions use that source.
- [ ] Implement the agreed no-reply template timing with inclusive/exclusive 24-hour boundaries; preserve all existing claim/idempotency/authorization fences.
- [ ] Reconcile the advisory read projection and existing composer availability; keep send authorization server-side.
- [ ] Add focused unit and, where available, PostgreSQL-backed regression tests for all matrix cases, including false/future/preinitial inbound, expiry boundaries, no initial `sentAt`, replay after expiry, and one sequence-two winner.
- [ ] Report Woo/Background policy parity, any unresolved cross-repository change, and validation evidence in the task Completion Report.

## Interfaces / Contracts

- Shopify server: `admitRecoveryHumanSend(shopId, recoveryId, input, db)` in `app/services/recoveries/recovery-human-commands.server.ts`.
- Shopify read: `readRecoveryDetail(...)` in `app/services/recoveries/recovery-detail.server.ts`, with existing `conversation.lastInboundAt`, `conversation.windowExpiresAt` and `conversation.followUp.eligible` fields.
- Existing persisted inputs: `ConversationMessage` (verified CUSTOMER/INBOUND provider event), `RecoveryOutreachAttempt` sequences 1 and 2, `MerchantConversationSendCommand`. No migration, new field or new cross-service wire format.
- Existing behavioral reference: `moda-interact-api/src/merchant/conversations/messages/eligibility.ts` and `admission.service.ts` as implemented under `ARCH-040-API-004`. **This reference does not authorize a Shopify agent to change API source.**
- Background retains provider permit, final service-window check, outbound send, moderation, credit reservation/release and compensation.

## Dependencies

- `ARCH-040-SHOPIFY-001` — Complete in supplied 2026-10-20 snapshot.
- `ARCH-040-API-004` — Complete in supplied 2026-10-20 snapshot; reference policy only, not a code dependency.
- **Policy gate:** explicit architect/developer determination of the no-customer-reply HUMAN template minimum waiting period, recorded before changing task status from `blocked` to `ready`.

## Enables

- `ARCH-040-SYSTEM-TEST-002` — independent terminal Shopify E2E certification after this correction and other prerequisites become Complete.

## Acceptance Criteria

- [ ] The parent architecture and task explicitly state the approved no-reply HUMAN template eligibility rule, and observed Shopify/Woo behavior conforms to it or separately-owned correction tasks are recorded.
- [ ] Only `providerMessageId != null` CUSTOMER/INBOUND messages in `[initialSentAt, now]` determine the latest customer window; a forged/unverified, old or future row cannot admit free text or falsely delay a template.
- [ ] Inclusive/exclusive boundary tests at exact 24 hours pass for free text, proactive templates, and no customer reply according to the approved policy.
- [ ] Read-side Recovery Detail guidance uses the same verification rule; when the follow-up is not yet eligible, the page does not offer an actionable template even when sequence two remains unused.
- [ ] Existing idempotent replay, ownership/tenant isolation, control mode/revision, terminal state, template authorization and sequence-two single-winner invariants are unchanged and tested.
- [ ] No additional credit, second command, second follow-up, Meta request or Redis queue is created by merely checking eligibility. Scheduled AUTOMATION no-response policy remains unchanged.
- [ ] Source-level differences with Woo and Background are documented with either verified parity or a concrete cross-repository blocker returned to the architect; no undocumented inconsistent production rules remain.

## Validation

- [ ] Focused `npm run test -- tests/unit/arch040-shopify-command.test.ts tests/unit/recovery-detail-readers.test.ts` (or equivalent current repository test paths); record exact counts and failures.
- [ ] Existing recovery-detail route/panel focused tests where window/display logic is affected.
- [ ] PostgreSQL-backed real query test for the verified inbound and read projection, if the repository's existing integration harness supports it; if unavailable, record precisely what could not be proven.
- [ ] `npm run typecheck`.
- [ ] `npm run lint`.
- [ ] `npm run build`.
- [ ] `git diff --check` and no `_index.md` or unrelated files changed.

## Stop Condition

When all approved Work Items, Acceptance Criteria and required Validation pass, update the Completion Report, set the task to `review`, return to `moda_architect`, and **STOP**. Do not start the terminal SYSTEM-TEST task or any cross-repository correction without a new assignment.

## Implementation Notes

- Reuse the existing Shopify modules and established Prisma patterns; avoid introducing generic abstractions solely for two local call sites.
- Capture a single `now` per transaction instead of repeatedly comparing to changing `Date.now()` values. Use deterministic test clocks and exact edge timestamps; no sleeps/timers in unit tests.
- Keep the existing ordered lock chain (Shop -> Conversation -> sequence-two) and the idempotency lookup before new eligibility checks.
- `providerMessageId != null` is the *current validated-message criterion used by Woo API-004*; do not invent another verification field or an additional provider lookup without architectural justification.
- Keep service-window advisory separate from command acceptance; the window can expire while a merchant views the screen. Background final admission remains a separate safety fence.
- If the approved cross-platform no-reply rule differs from Woo's current `merchantFollowUpWindowClosed`, **do not** silently copy or alter Woo; request an explicit API-owned follow-up task.

## Completion Report

### Status

Not Started — blocked on policy decision; no implementation claim or validation has occurred.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task is not yet executable.

### Deviations

None.

### Assumptions

The merged 2026-10-20 snapshot is the current inspected Shopify implementation baseline. Revalidate at task claim time.

### Unresolved Issues

Approval of the no-verified-inbound merchant-template waiting period.

### Architectural Concerns

Cross-platform policy must remain consistent with Woo API-004 and Background final send admission; any change outside Shopify is a separate task.

## Architect Review

### Review Status

Pending.

### Review Notes

The source mismatch has been identified. This portable task is **defined but not materialised**; not an approved implementation, accepted review, branch or worktree.

### Reviewed Files

- `moda-interact/app/services/recoveries/recovery-human-commands.server.ts`
- `moda-interact/app/services/recoveries/recovery-detail.server.ts`
- `moda-interact-api/src/merchant/conversations/messages/eligibility.ts`
- `moda-interact-api/src/merchant/conversations/messages/admission.service.ts`
- ARCH-040 parent architecture and existing Shopify/hosted API task definitions.

### Validation Reviewed

Static source comparison from the supplied 2026-10-20 snapshot; no implementation tests executed for this new task.

### Architecture Conformance

Scope is Shopify-owned, with a deliberately blocked cross-platform policy gate.

### Follow-up

Approve/record the no-reply merchant-template timing policy and explicitly promote SHOPIFY-005 to Ready before implementation begins. After accepted implementation, rerun SYSTEM-TEST-002 with negative verified-inbound and 24-hour boundary cases.
