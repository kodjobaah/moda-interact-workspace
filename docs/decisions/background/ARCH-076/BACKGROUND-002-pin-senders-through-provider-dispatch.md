---
id: ARCH-076-BACKGROUND-002
architecture_id: ARCH-076
title: Carry the immutable assignment through each provider permit
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-11-15T14:58:50Z
attempt: 1
depends_on: [ARCH-076-BACKGROUND-001]
enables: [ARCH-076-BACKGROUND-003]
created: 2026-11-13
updated: 2026-11-15
---

# Carry the immutable assignment through each provider permit

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Carry the immutable assignment through each provider permit.

## Context

15 November user-selected design retains five explicit sender entities plus the R15 evidence amendment. Sender attribution and conversation-credit renewal are independent streams. The user has authorized implementation of this reviewed design. Preserve prepared claims; execute only through the owning task launcher and accepted dependency frontier.

## Scope

Owning Background services and focused unit/provider-fixture/disposable PostgreSQL tests.

## Out of Scope

Other repository implementation, live settings, production migration and activation. Sender tasks must not implement allowance renewal; allowance tasks must not implement sender allocation. The SYSTEM-TEST task is deferred at the user's request.

## Requirements

- [ ] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [ ] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [ ] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [ ] Initial/follow-up/AI/human paths all use pinned sender; ordinary text/image/template transport must not resolve singleton sender again.
- [ ] Recheck sender/WABA/recipient/consent/owner/control/service window immediately before permit; no network in DB transactions.
- [ ] Use existing ordered delivery parts and immutable sender pair for receipts/status; preserve exact credit lineage and admission behavior without renewing allowance.
- [ ] Unknown provider results remain uncertain; never retry send automatically based on timeout.

## Work Items

- [ ] Inspect the exact latest accepted repository pin and existing owning mechanisms.
- [ ] Implement only this task's scope and requirements.
- [ ] Complete the focused checks below and record exact commands and evidence.
- [ ] Return the isolated implementation branch and parent Completion Report for review.

## Interfaces / Contracts

The parent architecture's Explicit sender storage, Independent allowance storage and Configurable routing sections are authoritative. Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Dependencies

ARCH-076-BACKGROUND-001

## Enables

Recalculate from dependent task metadata after architect acceptance; no implicit implementation handoff.

## Acceptance Criteria

- [ ] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [ ] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [ ] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [ ] Initial/follow-up/AI/human paths all use pinned sender; ordinary text/image/template transport must not resolve singleton sender again.
- [ ] Recheck sender/WABA/recipient/consent/owner/control/service window immediately before permit; no network in DB transactions.
- [ ] Use existing ordered delivery parts and immutable sender pair for receipts/status; preserve exact credit lineage and admission behavior without renewing allowance.
- [ ] Unknown provider results remain uncertain; never retry send automatically based on timeout.

## Validation

- [ ] Focused unit tests for every requirement, lint/typecheck/build as declared for changed code.
- [ ] Disposable PostgreSQL race/replay/restart tests with two recipients, two shops, multiple checkouts and shared sender.
- [ ] Provider HTTP fixtures for exact sender, failed initial delivery, unknown result, duplicate/foreign statuses and no network inside transactions.

Inspect the repository package.json before selecting actual commands. Required disposable PostgreSQL checks are task-local repository checks, not execution of the deferred system-test task. No live customer/provider calls belong to these checks.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set review, return the Completion Report and STOP. Do not execute another task or deploy.

## Implementation Notes

Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Completion Report

### Status

Implementation in progress. Source draft PR240: https://github.com/kodjobaah/moda-interact-background/pull/240. Initial source head `24f45ef` is committed/pushed; additional exact-history proof tests and integration of accepted BACKGROUND-005 main remain before review readiness.

### Files Changed

- New `src/services/recovery-sender-pool/dispatch-sender.ts`; sender permit and transport wiring in outbound delivery, recovery final fence, Woo initial fence, general fence, HUMAN dispatcher and multipart fence/engine.
- Scalar provider-status ownership guard and temporary legacy routing-guidance enrollment precheck.
- Focused unit fixtures, `tests/integration/arch076-dispatch-sender.integration.test.ts`, declared PostgreSQL command and source-owned dispatch documentation.

### Work Completed

- Validate/unseal current sender configuration outside SQL; check row/version, immutable assignment, frozen recipient, account membership and owner policy inside final permits. Freeze exact root sender pair and retain ordered-part identity.
- Serialize new standalone permits against disabled/enabled enrollment; preserve narrow proved preexisting unassigned AI/HUMAN continuation without assignment backfill.
- Forward exact sender through text/image/template transports; foreign stamped statuses have no lifecycle, credit or contact effects.

### Validation Results

- Focused delivery: 52 passed; text/image/template snapshot: 18 passed; guidance precheck: 10 passed; scalar status suite passed before additional paired-identity cases.
- Disposable PostgreSQL: 9 cases passed, including actual standalone/Woo permits, replay, disabled enrollment, both membership-lock winners, shared sender/recipient/account checks and credential CAS serialization. Additional explicit AI/HUMAN and historical multipart cases are being validated.
- Full lint and source typecheck passed before the latest proof-test additions. Full unit CI/integrated-main verification and build remain pending. Interrupted/failing discovery runs are not counted as passes.

### Deviations

The old neutral routing-guidance path has a membership/configuration precheck but still only historical Redis admission. This is **not** a complete durable permit or a closed commit-to-provider enrollment race. Pool activation is gated on BACKGROUND-004's persisted RoutingTurn replacement. No fabricated Conversation or external I/O in SQL was introduced.

### Assumptions

Sender routing remains independent of allowance funding. Preserve accepted BACKGROUND-005 funding checks and combined Database `0a965c5` when integrating current main. No Shared release, live mutation, deployment or deferred SYSTEM-TEST execution.

### Unresolved Issues

Final integrated validation/review submission pending; no main merge by this agent.

### Launcher Evidence

- Canonical root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-076-BACKGROUND-002`, `task/ARCH-076-BACKGROUND-002`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-076-BACKGROUND-002`, `task/ARCH-076-BACKGROUND-002`.
- Launcher created both worktrees, incorporated current origin/main, verified recursive submodules and dependency, and committed/pushed claim `ca9404984845ba2b3af2c5cd2426bb4d5fe16c07`, attempt1 at `2026-11-15T14:58:50Z`.
- Source initial head `f6bbcc5fbf247ea9b8df87ad0ba34ade079d9c38`; initial nested Database `a7c204618c6b0ad83952a7b661482cfd03acf899`. No shared/default checkout switch or another task's worktree reuse. No parent implementation gitlink staged.
- Parent origin/main subsequently merged to consume the exact legacy continuation amendment and accepted Admin governance. Architect Review remains untouched.

### Architectural Concerns

None beyond the explicit staged legacy-guidance durability gate above.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Awaiting implementation.

### Follow-up

None.

## Reconciliation provenance — 15 November 2026

Reconciled from the later local sender-pool revision formerly labelled ARCH-069. The completed chronological-input architecture and its ARCH-069 task identities are unchanged. ARCH-076 was already reserved for the earlier sender-pool proposal; this revision updates that proposal in place, retaining its Git history. These are definition changes, not implementation or deployment evidence. All execution remains Pending until compatibility review and dependency promotion.

## Mandatory same-conversation allowance renewal amendment

Historical renewal amendment is superseded for this sender task: allowance work belongs only to independent DATABASE-002/BACKGROUND-005 and does not gate sender routing. Never filter ownership by credit or cap.


### 15 November definition amendment

Historical fixed SQL must be regenerated for the restored five-entity contract plus R15 evidence; hardcoded router policy remains superseded. Historical claim/review evidence above is retained as history, not approval of the replacement implementation. No runtime source or migration has been implemented. User has authorized implementation; runtime acceptance and rollout verification remain pending.


## Existing singleton cutover proof boundary

BG002 must retain the approved non-pooled send-versus-enrollment fence, not merely change recovery transport endpoints. Before a new standalone/non-pooled provider permit, acquire the same transaction advisory membership key as Admin enrollment: `pg_advisory_xact_lock(hashtextextended('whatsapp-pool-membership:' || phoneId::text, 0))`. Under that lock reject the non-pooled permit if any inventory row exists for that exact phone, even allocation-disabled. Freeze the exact dispatchProviderAccountId/dispatchProviderPhoneNumberId pair on the durable root permit and current delivery parts; no network inside the lock. Enrollment collision preflight and permit must serialize on that key. Existing already-admitted/unknown provider work retains exact proof and must not be resent after cutover. Recovery initial/followup/AI/human sends use their existing assignment's sender; non-pooled sends may use only the permitted current credential identity and never bypass enrolled inventory.

BG003 must distinguish newly pooled routing from exact preexisting unassigned singleton evidence. An authentic quoted prior outbound, persisted inbound replay or exact status receipt may resolve its original existing Conversation using immutable recorded root/part sender evidence and matching authenticated WABA/phone/recipient. An old NULL root pair without another exact durable sender/recipient witness remains held; current singleton configuration alone never proves historical identity. Never fabricate sender proof, backfill assignment, bind old history to a new route generation or use recipient-only fallback to select an owner. Closed/expired history remains history and never reopens recovery or bypasses STOP/window/control/cap. Foreign sender statuses/quotes have no effects. This preserves production evidence, not a compatibility path for obsolete new schema formats.

Owner checks: concurrent standalone permit versus first disabled enrollment (either permit wins and enrollment reports protected use, or enrollment wins and permit is refused); inventory disabled still blocks new non-pooled permit; pooled endpoints never fall back to singleton; exact preexisting singleton quote/replay/status succeeds only with matching stable proof, wrong/changed/unknown account proof refuses, no assignment backfill or repeated provider admission. Partial BG001 may hold zero-inventory initial work, but inventory cannot activate until complete pinning/ownership path is test-verified and old consumers/inflight work are drained. Production auto-deploy holds remain.

## Proven preexisting unassigned recovery continuation

The clean-sender cutover may leave an old singleton unenrolled while its legitimate preexisting recovery Conversation continues. Permit only new customer-initiated in-window AI or human free-form replies on that exact unassigned Conversation when durable original sender AND recipient proof exists. This does not authorize proactive followup, new initial outreach, or generic unassigned recovery fallback.

Accepted proof sources are (a) a confirmed prior outbound root with its immutable dispatch sender pair plus the exact sent INITIAL RecoveryOutreachAttempt recipient tied to that root/Conversation, or (b) frozen multipart source recipient plus sender pair and confirmed matching part evidence. Match authenticated quote/replay/current owned human-command scope and the exact Conversation; a mutable customer/Conversation phone, current configuration alone, bare recipient lookup or an old NULL sender pair without another durable witness is insufficient. If proof is missing, changed or conflicting, hold without backfill, migration or guessing.

At each NEW reply permit, take the existing exact-phone non-pooled membership advisory fence, verify no inventory row exists for that phone (even disabled rows forbid this path), and hold current credential row FOR SHARE while checking its WABA/phone against the durable proof. Freeze exact sender pair on the new root/parts and use the proved recipient. Existing consent, STOP, window, moderation, control revision, quota and billing admission checks remain mandatory. Assigned recovery always uses assignment and never this path, even on missing credentials or drained inventory; all new initial recoveries require assignment.

A prior admitted/UNKNOWN provider operation is never retransmitted through this continuation path. Each new customer/human reply has its own existing idempotent message/command identity. Status callbacks and quoted history continue against original exact evidence, never a new route generation. Test successful AI and human continuation with both approved proof forms, NULL/no-witness refusal, changed sender/recipient refusal, inventory-disabled fence, concurrent enrollment versus permit, assigned-recovery refusal, initial/proactive-followup exclusion, and duplicate/unknown replay with no second provider send. This preserves a legitimate old conversation, not an obsolete schema-format adapter.
