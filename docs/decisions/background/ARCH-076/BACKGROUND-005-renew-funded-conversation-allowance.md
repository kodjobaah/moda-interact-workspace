---
id: ARCH-076-BACKGROUND-005
architecture_id: ARCH-076
title: Renew the existing conversation allowance
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on: [ARCH-076-DATABASE-002]
enables: []
created: 2026-11-15
updated: 2026-11-15
---

# Renew the existing conversation allowance

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Fund a fresh automated allowance on genuine continuation without changing routing.

## Context

15 November user-selected design retains five explicit sender entities plus the R15 evidence amendment. Sender attribution and conversation-credit renewal are independent streams. The user has authorized implementation of this reviewed design. Preserve prepared claims; execute only through the owning task launcher and accepted dependency frontier.

## Scope

Existing recovery credit admission/settlement/compensation, outbound admission counts and merchant SYSTEM notice; no sender allocation.

## Out of Scope

Other repository implementation, live settings, production migration and activation. Sender tasks must not implement allowance renewal; allowance tasks must not implement sender allocation. The SYSTEM-TEST task is deferred at the user's request.

## Requirements

- [x] At the live normal boundary keep current block ACTIVE and emit advisory merchant SYSTEM notice once; no new credit solely for crossing. Follow the parent ACTIVE-until-renewal protocol.
- [x] Next genuine automated continuation reserves one eligible credit against explicit continuation identity on SAME Conversation/recovery; no fake sequence-two attempt.
- [x] Count automated message UsageEvents by immutable funded block; never reset lifetime counts/history or globally suppress after historical terminal notice.
- [x] Canonical paid/included/promotional/purchased/free paths must preserve exact new source identity; existing admit without outreachAttemptId drops custom paid sourceKey and must be explicitly corrected.
- [x] FOLLOW_UP uses its legitimate exact sequence-two credit once to fund successor block; no second continuation debit, unadmitted followup still cancelled on customer return.
- [x] Activate successor atomically only on exact confirmed opening settlement; mark prior EXHAUSTED for CONTINUATION or CLOSED for genuine FOLLOW_UP. Definitive pre-permit failure cancels/releases; unknown result holds exact proof and bounded repair, no resend.
- [x] Late opening failure compensates block only if no other provider-admitted consumption; otherwise preserve funding and expose incident.
- [x] Zero credits holds same request and existing capacity repair resumes; no auto-purchase, reroute, cap reset, extra Conversation or unfunded model/provider call.
- [x] HUMAN/STOP/clarification/window/closed/expiry paths never consume continuation funding; cap does not change controlMode.

## Work Items

- [x] Inspect the exact latest accepted repository pin and existing owning mechanisms.
- [x] Implement only this task's scope and requirements.
- [x] Complete the focused checks below and record exact commands and evidence.
- [x] Return the isolated implementation branch and parent Completion Report for review.

## Interfaces / Contracts

The parent architecture's Independent allowance storage and lifecycle sections are authoritative. Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Dependencies

ARCH-076-DATABASE-002

## Enables

Recalculate from dependent task metadata after architect acceptance; no implicit implementation handoff.

## Acceptance Criteria

- [x] At the live normal boundary keep current block ACTIVE and emit advisory merchant SYSTEM notice once; no new credit solely for crossing. Follow the parent ACTIVE-until-renewal protocol.
- [x] Next genuine automated continuation reserves one eligible credit against explicit continuation identity on SAME Conversation/recovery; no fake sequence-two attempt.
- [x] Count automated message UsageEvents by immutable funded block; never reset lifetime counts/history or globally suppress after historical terminal notice.
- [x] Canonical paid/included/promotional/purchased/free paths must preserve exact new source identity; existing admit without outreachAttemptId drops custom paid sourceKey and must be explicitly corrected.
- [x] FOLLOW_UP uses its legitimate exact sequence-two credit once to fund successor block; no second continuation debit, unadmitted followup still cancelled on customer return.
- [x] Activate successor atomically only on exact confirmed opening settlement; mark prior EXHAUSTED for CONTINUATION or CLOSED for genuine FOLLOW_UP. Definitive pre-permit failure cancels/releases; unknown result holds exact proof and bounded repair, no resend.
- [x] Late opening failure compensates block only if no other provider-admitted consumption; otherwise preserve funding and expose incident.
- [x] Zero credits holds same request and existing capacity repair resumes; no auto-purchase, reroute, cap reset, extra Conversation or unfunded model/provider call.
- [x] HUMAN/STOP/clarification/window/closed/expiry paths never consume continuation funding; cap does not change controlMode.

## Validation

- [x] Unit and real PostgreSQL races: duplicate inbound, concurrent last slots, renewal once, zero credits/resume, restart and third funded block.
- [x] Provider fixtures: exact opening settlement, definitive failure, timeout unknown, foreign receipt and late failure after subsequent consumption.
- [x] Existing credit-bucket/followup/accounting tests plus declared typecheck/build.

Inspect the repository package.json before selecting actual commands. Required disposable PostgreSQL checks are task-local repository checks, not execution of the deferred system-test task. No live customer/provider calls belong to these checks.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set review, return the Completion Report and STOP. Do not execute another task or deploy.

## Implementation Notes

Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Completion Report

### Status

Ready for Review. Implementation and validation complete; awaiting moda_architect review.

### Files Changed

- `src/services/recovery-allowance/storage.ts` and `renewal.service.ts`: immutable block accounting, canonical funding intent, once-only merchant advisory, final reversible capacity check, exact settlement and bounded independent repair.
- Existing outbound admission, turn processor, send fence, delivery and provider-failure services: pin new automated messages, hold the original turn without unfunded model/provider work, owner-lock compensation, preserve unknown outcomes and retry the same inbound when old capacity reopens.
- Existing recovery billing, follow-up billing/processor and delivery-compensation services: preserve exact paid source identity; use the genuine sequence-two source once, including HUMAN template openers; retain cancellation lineage and protect credits already consumed by other provider-admitted messages.
- `database`: accepted combined Database main `0a965c549b4916085acd8a806d5ecf376eda0e47`, explicitly authorized by coordinator; no schema/migration edits.
- Task-local PostgreSQL suite, focused unit fixture updates, two existing PostgreSQL fixture corrections, package test command and `docs/architecture/arch076-conversation-allowance.md`.

### Work Completed

- Same checkout/Conversation/transcript/lifetime counters remain. Each allowance block snapshots configured hard limit and terminal reserve; normal capacity is their difference. The advisory does not exhaust an ACTIVE block, charge a credit, change control mode or consume an automated slot.
- Next genuine current unprocessed AI continuation creates a durable PENDING intent before canonical credit admission. No-credit work retains the original turn; repair resumes the same intent. Zero ordinary capacity fails before funding intent/reservation.
- Under the existing owner lock immediately before provider permit, reopened old capacity cancels/releases the unadmitted pending source and preserves its immutable prepared row; the original inbound retries with fresh old-block preparation. Once provider-admitted, funding is frozen and unknown outcome never triggers a resend/refund by timeout.
- Exact confirmed opening plus committed source activates the successor and closes/exhausts its predecessor appropriately. Definitive opening failure releases/cancels only its exact source. Eligible late cancellation retains original predecessor and monotonically increasing ordinal; other admitted consumption preserves funding and reports the existing compensation incident.
- Genuine sequence-two templates use their canonical credit once. HUMAN template opener retains HUMAN actor plus one automated opening event; ordinary HUMAN_TEXT has no automated allowance event.
- No sender allocation, routing changes, AI settings, auto-purchase, Shared publication, live changes or SYSTEM-TEST execution.

### Validation Results

- `npm run lint`: passed on final runtime source; `npx eslint tests/integration/arch075-common-layout.integration.test.ts tests/integration/recovery-conversation.services.integration.test.ts`: passed after the only later test-fixture edits.
- `npx tsc --noEmit --pretty false`: passed; `npm run build`: passed (Prisma generation, both TypeScript compilations and sample packaging).
- Focused existing credit-bucket/recovery/admission/turn unit checks: 33 files / 430 tests passed before final cleanup. Exact published final commit `69a5bb3ec28ec70c0388dae67d73b7221634abaf` GitHub CI passed Prisma generation, typecheck and full unit suite: 403 files / 4,562 tests (run `43742863256`; original runtime head `ce844739c2ede6a812eeda76125bbcea9a451cd7` runs also passed).
- Exact disposable PostgreSQL command: `node scripts/test-integration.mjs tests/integration/arch076-allowance-renewal.integration.test.ts tests/integration/arch028-recovery-delivery-compensation.integration.test.ts tests/integration/arch075-common-layout.integration.test.ts tests/integration/recovery-conversation.services.integration.test.ts`. Three suites / 107 tests passed; four existing HUMAN expected-success fixtures lacked required prepared-wrapper/moderation proof. Those fixtures were corrected through real owning service seams, preserving all negative guards.
- Isolated rerun `node scripts/test-integration.mjs tests/integration/recovery-conversation.services.integration.test.ts`: 11/11 passed. Combined relevant coverage is 118/118 after corrections, including allowance 20 races/provider/restart fixtures. No production/test deployment or provider calls were used.
- The allowance cases cover variable limits/reserve zero and normal capacity zero, concurrent final slots/renewal, no-credit resume, crash before funding bind, third funded block, before/after-permit old-slot compensation, unknown opening, exact/foreign receipts, definitive rejection, retained cancelled-lineage retry, late failure with subsequent consumption, genuine HUMAN sequence-two versus ordinary HUMAN text and STOP/HUMAN/clarification/window/terminal exclusions.
- An earlier malformed queued PTY integration command unintentionally selected broad suites and was interrupted; it is not counted as a pass. A later redundant local default-worker full-unit run was stopped after host-load 5-second timing failures in unchanged startup/chronology tests; exact-head hosted full-unit CI passed. Neither interrupted run is represented as successful validation.

### Deviations

None to the accepted application contract. Relevant existing integration success fixtures now establish real funding/preparation proof rather than bypassing the new or already-existing final guards. No test assertions were weakened or skipped.

### Assumptions

Configured policy remains the source of allowance limits; technical leases/repair cadence reuse existing runtime patterns. A provider-unknown opening requires exact durable reconciliation and is never guessed successful or refunded.

### Unresolved Issues

Final published head `69a5bb3ec28ec70c0388dae67d73b7221634abaf` CI run `43742863256` passed Prisma generation, typecheck and the full unit suite. Production remains held; test-first rollout and the separate SYSTEM-TEST task remain coordinator/developer responsibilities.

### Architectural Concerns

No new schema or Shared contract required. Sender allocation remains independent; the later merging dispatch task must preserve both final-permit authorities and revalidate their union.

### VCS / Isolation Evidence

- Canonical root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; prepared parent and implementation worktrees supplied by launcher were reused, never derived from another task.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-076-BACKGROUND-005`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-076-BACKGROUND-005`. Both branches: `task/ARCH-076-BACKGROUND-005`.
- Prepared launcher performed fetch/task-branch synchronization/main incorporation and durable claim `8c11db2a36ee2a12597f6867cd09d83ad2717d48`. Accepted Background main `f6bbcc5fbf247ea9b8df87ad0ba34ade079d9c38` was incorporated before final source validation; parent incorporated current main in `8f35247b6cbedf4df434d52b6185be90f1f5e438`.
- Implementation commit `69a5bb3ec28ec70c0388dae67d73b7221634abaf`, pushed to `origin/task/ARCH-076-BACKGROUND-005`; source PR: https://github.com/kodjobaah/moda-interact-background/pull/241 (ready for review).
- Parent report publication commit `44c01f956` pushed to `origin/task/ARCH-076-BACKGROUND-005`; report PR https://github.com/kodjobaah/moda-interact-workspace/pull/1077. This follow-up evidence-only commit records that prior publication; both histories remain feature branches.
- Shared/default checkouts were not switched or edited. No other task worktree was reused. No parent submodule gitlink staged. Neither task branch merged to main, no main push, no architect acceptance asserted.

## Architect Review

### Review Status

Accepted — 15 November 2026. Automatic completion; attempt 1 preserved. Historical claim: codex, 2026-11-15T14:11:05Z; prepared claim `8c11db2a36ee2a12597f6867cd09d83ad2717d48`.

### Review Notes

Independently inspected the actual renewal/storage, quota admission, exact-source billing, final provider permit, follow-up and compensation changes. Root accepted and merged source PR241 to Background main `0a6bb0ba2ea1042ef79588592a4e39e7bf20ea94`. Its tree exactly equals tested head `69a5bb3ec28ec70c0388dae67d73b7221634abaf`: `15b0db811cdafc8883684de699ec9dfb12d9c4ee`. Final changes after runtime review corrected only two PostgreSQL fixture files through real funding, wrapper and moderation seams without weakening assertions. Canonical prepared isolation and synchronization evidence above satisfies the mirrored task workflow.

### Reviewed Files

Recovery allowance storage/renewal; outbound admission reservation, delivery/provider failure; final send fence; turn processor and pending repair; recovery capacity/billing/follow-up; exact compensation lineage/reconciliation; new allowance PostgreSQL suite and affected existing fixtures.

### Validation Reviewed

Exact-head hosted Prisma/typecheck/full unit CI: 403 files, 4,562 tests. Local lint, changed-fixture lint, TypeScript and production build passed. Required PostgreSQL coverage passed cumulatively: three suites/107 tests plus corrected HUMAN suite/11 tests, 118 relevant tests; not represented as one rerun invocation. Reviewed concurrent last slots and renewal, no-credit restart, variable/zero reserve, exact/foreign receipts, pre/post-permit reopened capacity, unknown outcome, cancelled-lineage retry and late failure after other consumption. Interrupted runs remain explicitly excluded from passing evidence.

### Architecture Conformance

Conforms to independent same-Conversation funding, exact canonical credit identity in all buckets, immutable usage/history and block pins, ACTIVE-until-renewal boundary, once-only merchant advisory, genuine sequence-two credit reuse, HUMAN/STOP/window/clarification exclusions and provider-unknown no-refund/no-resend. Database pin is accepted combined `0a965c549b4916085acd8a806d5ecf376eda0e47`; no schema, Shared release or sender routing changes were introduced.

### Follow-up

No task correction required and no new dependency promotion follows this independent task. BG002 must preserve both sender and allowance permit authorities when integrating accepted main and validate their combined implementation. SYSTEM-TEST remains user-deferred. Source acceptance does not activate inventory or verify test/production deployment.

### 15 November definition amendment

This is a new independently scoped definition, not implementation evidence. No runtime source or migration has been implemented. User has authorized implementation; runtime acceptance and rollout verification remain pending.

## Funded allowance boundary — ACTIVE until renewal admission

This application protocol supersedes earlier wording that marked EXHAUSTED as soon as reserved usage reached a cap. No SQL/schema change is required. The normal-message allowance is the frozen `hardMessageLimit - terminalReservedSlots`; do not hardcode 19/20. Reserved terminal slots are only for genuine permitted terminal notices, never ordinary answers, and no customer terminal notice is forced merely to spend the reserve. Test zero reserve and variable valid limits.

1. Usage reservations count for ordinary admission, so potentially consumed/inflight slots cannot be oversubscribed. Merely reserved usage, HTTP200/provider ID or SENT can later fail and be compensated; none justifies irreversible exhaustion alone. When the live normal cap prevents another ordinary answer, keep the existing block ACTIVE and emit at most one merchant SYSTEM advisory notice keyed by that block. Explain that a further recovery credit may be required if the limit still holds at the next genuine continuation; no debit occurs solely at the boundary.
2. On the next genuine customer automated continuation, create one PENDING successor intent under owner lock before external credit reservation, using the same deterministic block identity and canonical credit paths. No new routing decision, Conversation or reset. An unresolved pending provider outcome gates parallel successors; bounded repair reconciles exact evidence rather than declaring timeout a failure.
3. Immediately BEFORE the final durable provider permit, re-lock/revalidate actual surviving normal usage/reservations, block ownership/control/eligibility and exact funding proof. If compensation freed old capacity, cancel/release the unadmitted pending successor and admit the original customer continuation using the still-ACTIVE old block. Never retag an immutable prepared message pin: if preparation already pinned a successor row, preserve/cancel it and create a fresh logical row for old capacity without a duplicate provider send. No manual-incident hold is the default for an ordinary freed slot.
4. Once that successor's exact provider permit is admitted, its funding choice is frozen. Do not re-evaluate old capacity after permit or rewind this decision because a late old message failure removes an old event. UNKNOWN opening stays PENDING, with exact reservation/permit identity, preventing another successor or automatic resend.
5. On confirmed funded opening settlement, atomically transition predecessor ACTIVE→EXHAUSTED for CONTINUATION (already-EXHAUSTED predecessor is retained on a proved replacement lineage), or predecessor ACTIVE→CLOSED for a genuine FOLLOW_UP, and activate the successor. The followup's exact sequence-two credit funds it once. CONTINUATION eligibility before permit is actual live cap proof, not a requirement that the predecessor already be EXHAUSTED.
6. Definitive opening failure BEFORE activation cancels/releases/refunds the PENDING intent only with exact no-success/compensation proof; predecessor remains ACTIVE. After activation, a late opening failure follows existing exact compensation and the no-other-provider-consumption guard: retain cancelled lineage where cancellation/refund is eligible, retry with a fresh monotonic ordinal and exact source, never reopen an EXHAUSTED predecessor. If other successor messages already consumed its funding, preserve that funding and its evidence as previously required. Old-block late failure compensates only its own exact usage, not the completed successor renewal.

Required owner checks: variable hard/reserve snapshots (including reserve0), provisional reserved/unknown slots versus compensated slots, advisory notice once, compensation before final permit cancels/releases successor and reuses old capacity, compensation after permit cannot rewind funding, unknown opening excludes parallel charge/resend, definitive preactivation opener failure, eligible late opener cancellation plus retained lineage/new ordinal retry, and ineligible late opener refund after other admitted consumption. Check actual provider calls, pins and canonical credit counts, not only block state. Existing service-window/STOP/HUMAN/routing exclusions remain; SYSTEM-TEST stays deferred.
