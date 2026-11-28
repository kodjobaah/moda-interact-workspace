---
id: ARCH-076-BACKGROUND-003
architecture_id: ARCH-076
title: Attribute inbound replies and provider statuses to exact sender and ownership evidence
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
depends_on: [ARCH-076-BACKGROUND-002]
enables: [ARCH-076-BACKGROUND-004]
created: 2026-11-13
updated: 2026-11-15
---

# Attribute inbound replies and provider statuses to exact sender and ownership evidence

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Attribute inbound replies and provider statuses to exact sender and ownership evidence.

## Context

15 November user-selected design retains five explicit sender entities plus the R15 evidence amendment. Sender attribution and conversation-credit renewal are independent streams. The user has authorized implementation of this reviewed design. Preserve prepared claims; execute only through the owning task launcher and accepted dependency frontier.

## Scope

Owning Background services and focused unit/provider-fixture/disposable PostgreSQL tests.

## Out of Scope

Other repository implementation, live settings, production migration and activation. Sender tasks must not implement allowance renewal; allowance tasks must not implement sender allocation. The SYSTEM-TEST task is deferred at the user's request.

## Requirements

- [x] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [x] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [x] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [x] Receiving WABA/sender/recipient must match verified assignment; exact quote/replay binds original message and Conversation.
- [x] Confirmed failed initial delivery such as 131049 does not establish contacted ownership; HTTP acceptance alone is insufficient.
- [x] Use sender-specific existing per-part receipt proof for status callbacks; foreign sender evidence has no effect.
- [x] STOP, history and HUMAN control retain existing semantics independent of credit or allowance; ambiguous original is saved outside merchant transcript.

## Work Items

- [x] Inspect the exact latest accepted repository pin and existing owning mechanisms.
- [x] Implement only this task's scope and requirements.
- [x] Complete the focused checks below and record exact commands and evidence.
- [x] Return the isolated implementation branch and parent Completion Report for review.

## Interfaces / Contracts

The parent architecture's Explicit sender storage, Independent allowance storage and Configurable routing sections are authoritative. Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Dependencies

ARCH-076-BACKGROUND-002

## Enables

Recalculate from dependent task metadata after architect acceptance; no implicit implementation handoff.

## Acceptance Criteria

- [x] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [x] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [x] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [x] Receiving WABA/sender/recipient must match verified assignment; exact quote/replay binds original message and Conversation.
- [x] Confirmed failed initial delivery such as 131049 does not establish contacted ownership; HTTP acceptance alone is insufficient.
- [x] Use sender-specific existing per-part receipt proof for status callbacks; foreign sender evidence has no effect.
- [x] STOP, history and HUMAN control retain existing semantics independent of credit or allowance; ambiguous original is saved outside merchant transcript.

## Validation

- [x] Focused unit tests for every requirement, lint/typecheck/build as declared for changed code.
- [x] Disposable PostgreSQL race/replay/restart tests with two recipients, two shops, multiple checkouts and shared sender.
- [x] Provider HTTP fixtures for exact sender, failed initial delivery, unknown result, duplicate/foreign statuses and no network inside transactions.

Inspect the repository package.json before selecting actual commands. Required disposable PostgreSQL checks are task-local repository checks, not execution of the deferred system-test task. No live customer/provider calls belong to these checks.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set review, return the Completion Report and STOP. Do not execute another task or deploy.

## Implementation Notes

Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Completion Report

### Status

Ready for Review. Source [PR242](https://github.com/kodjobaah/moda-interact-background/pull/242), clean source head `f09b1471d5ba1445d6dc2c4396b85b568c962a1b`, is committed and pushed with both exact-head CI workflows passing. Final tested source tree is `43a9f786787f0a4877af02a2b09acb6472e123fe`.

### Files Changed

- `recovery-sender-pool/inbound-authority.ts`, `inbound-writer.ts`, `routing-handoff.ts`: exact immutable ownership, sender-aware quote/replay proof, shared provider-ID serialization, atomic transcript/activity/engagement and scoped pending-original persistence.
- Actual `recovery-routing.service.ts`, `whatsapp-inbound-processing.service.ts`, `conversation.service.ts`, audio reservation/completion, STOP quote validation, scalar provider statuses and production delayed-turn composition.
- Task-local PostgreSQL suite/script, focused unit fixtures, delayed-turn regression cases and `docs/architecture/arch076-inbound-attribution.md`.

### Work Completed

- Resolve known pool sender independently of allocation-enabled state. Match WABA, frozen recipient, exact thread/route generation and immutable assignment. No credits, message allowance or model-capacity candidate filter; exhausted baskets remain candidates.
- Unquoted contacted eligibility requires provider delivery/read proof. HTTP acceptance alone does not establish ownership. An authentic customer quote of an exact accepted SENT root/ACKNOWLEDGED part with stable sender, recipient, provider ID and source proof may establish direct contact for that referenced live input. Its authenticated stamped inbound/quote witness can prove later contact; no provider timestamps are invented. FAILED/UNKNOWN/NULL/foreign evidence does not grant active ownership.
- Shared provider-ID advisory lock composes merchant transcript and RoutingTurn writers. Final owner, lifetime and generation are rechecked before text/audio persistence, engagement and activity changes. Duplicates and historical input do not revive a recovery. Audio existing/P2002 winners verify owner and receiving pair; delayed production turns check ownership before context/model and again at control/provider boundaries.
- Exact confirmed RoutingTurn prompt quotes and compatible outstanding prompts hand off before a single-candidate shortcut. Unknown-shop input remains thread-scoped; verified shop scope is explicit. BG004 owns classification, exact original/prompt linkage, role-aware history before latest/caps and durable neutral prompt execution.
- Pending persistence consumes an explicit validated complete policy snapshot port and saved TTL/retention. Missing policy holds, with no hidden model/business defaults. Current saved policy version is rechecked under share lock. Full BG004 policy wiring and terminal scrub/association are activation gates.

### Validation Results

- Focused four-suite status/conversation/audio/STOP checks: 129 passed, exit 0 (`/tmp/bg003-helper-unit.log`), including foreign/NULL status no-effects and public audio reserve/P2002 owner/sender refusal.
- Router plus delayed-turn suites: 89 passed, exit 0 (`/tmp/bg003-routing-turn-unit.log`).
- `npm run test:arch076-inbound-routing:postgres`: final 24/24 passed, exit 0 (`/tmp/bg003-pg-final24.log`). Covers two shops/recipients, sender drain, release/generation reuse, shared-provider-ID race, routing persistence/replay, real STOP and status integration, multipart ownership, allowance-exhausted candidates, and actual quote-before-callback inbound-to-AI-enqueue pipeline. Discovery failures and superseded/interrupted runs are not counted as final passes.
- Replaced obsolete recipient-only router mocks with explicit ownership/handoff unit seams and real PostgreSQL regressions. The final PostgreSQL cases specifically preserve Woo completed-successor generation exclusion, inactive-shop refusal, historical quote with no Commerce enqueue/activity, and a later valid quote witness surviving an earlier failed witness. No unique constraint was disabled for fixtures.
- Final `npm run lint` and `npm run build`: exit 0 (`/tmp/bg003-final-validation.log`). Declared build runs Prisma generation, `tsc`, `tsc -p tsconfig.provision.json`, and sample packaging; it covers the final witness-iteration runtime source. The only subsequent edit corrected a PostgreSQL fixture. Separate prior `npx tsc --noEmit --pretty false` passed; final exact-head CI will supply the explicit noEmit and broad-unit evidence.
- Final exact clean-head CI passed: [push workflow 43750386225](https://github.com/kodjobaah/moda-interact-background/actions/runs/43750386225) and [PR workflow 43750391288](https://github.com/kodjobaah/moda-interact-background/actions/runs/43750391288). Both execute the repository broad unit/typecheck workflow against source `f09b1471d5ba1445d6dc2c4396b85b568c962a1b`. Identical tested tree was preserved through authorized history cleanup; local checks were not redundantly repeated.

### Deviations

No new Shared contract, schema, model policy, funding path, provider callback configuration or live setting is introduced. BG003 deliberately exposes a fail-closed typed policy/prompt seam; BG004 must provide its validated policy and durable prompt/decision consumer before any pool activation.

### Assumptions

Accepted sender allocation/dispatch and independent allowance renewal are preserved from Background main `cb625e626bebba337c1dda3ce4190bd00f3ad7f1`, with Database `0a965c549b4916085acd8a806d5ecf376eda0e47`. The SYSTEM-TEST task remains deferred. Root owns main merges, final parent pin, test activation and production rollout.

### Unresolved Issues

No implementation issue remains for this bounded task. BG004 policy/prompt wiring remains a rollout gate, not implemented here. Coordinator performed the user-authorized cleanup of only this unmerged source task branch, preserving the exact tested tree. Private verified history bundle `local-backups/arch076-design-review/background003-before-authorized-cleanup.bundle` has mode 0600; coordinator audit `background003-authorized-history-cleanup.json` records the operation. Newly introduced fixtures use reserved fictional numbers. Existing main history and unrelated baseline fixtures were unchanged. No history rewrite or force-push by this agent.

### Launcher Evidence

- Exact primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-076-BACKGROUND-003`, branch `task/ARCH-076-BACKGROUND-003`.
- Source `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-076-BACKGROUND-003`, same task branch. No shared/default checkout switched or another task worktree reused for source edits.
- Prepared attempt1 claim `6abec40415acfd33393fe1ce0dca3cc9220ef982`, executor codex, `2026-11-15T18:03:14Z`, committed/pushed by launcher. Parent main `fa21dddfdb3e84057cfaf4a59e33a885eb894201` and source main `cb625e626bebba337c1dda3ce4190bd00f3ad7f1` already incorporated; no remote task fast-forward needed at creation.
- Recursive submodule sync/update passed in launcher; Database recorded `0a965c549b4916085acd8a806d5ecf376eda0e47`. No startup re-claim or redundant submodule preparation. No parent implementation gitlink staged.

### Architectural Concerns

No source blocker. The explicit BG004 activation boundary remains; coordinator-owned narrow history cleanup is complete with the tested tree preserved.

## Architect Review

### Review Status

Accepted — 15 November 2026. Automatic completion; attempt 1 preserved. Historical codex claim 2026-11-15T18:03:14Z, prepared commit `6abec40415acfd33393fe1ce0dca3cc9220ef982`.

### Review Notes

Independently inspected actual ownership authority, final inbound writer, routing handoff, quote/replay, STOP/status and delayed-turn integration. Earlier SQL alias, pending-clarification single-candidate and router-prompt quote findings were corrected. Exact authenticated SENT/ACKNOWLEDGED quotes can establish contact before delivery callbacks, with actual stamped inbound evidence and one logical AI job; no Meta timestamps are fabricated. Distinct valid witnesses are not hidden by another failed quote. Root merged source PR242 to `61cbc9cd8fc1661e9ca17b774f6d338517cdb58b`, exact tested tree `43a9f786787f0a4877af02a2b09acb6472e123fe` matching clean head `f09b1471d5ba1445d6dc2c4396b85b568c962a1b`. Authorized task-only history cleanup preserves that tree and private evidence; new fixtures use reserved fictional numbers.

### Reviewed Files

Inbound authority/writer/routing-handoff, recovery routing, conversation and audio persistence, contact opt-out and quoted ownership, provider status, inbound processing and production turn composition; actual PostgreSQL and affected unit fixtures.

### Validation Reviewed

24/24 actual PostgreSQL scenarios, focused 129 plus router/delayed-turn 89 unit tests, lint and production build passed. Exact clean-head CI workflows 43750386225 and 43750391288 passed broad units and typecheck. Reviewed full quote-before-callback enqueue/replay, generation reuse, Woo completed successor, inactive shop, historical no-model/no-activity, STOP/foreign status isolation and contact-witness iteration. Prepared physical mirrored worktrees, synchronization and recursive Database evidence are recorded above.

### Architecture Conformance

Conforms to exact sender/recipient/thread/route ownership, immutable provider-ID arbitration, lifetime/generation revalidation, atomic text/audio persistence, historical preservation and allowance-independent candidate selection. Missing routing policy holds through explicit typed port; no model defaults, schema or Shared release introduced. BG004 remains responsible for complete configured routing, R15 decisions and durable neutral prompts before activation.

### Follow-up

Promote only ARCH-076-BACKGROUND-004 to Ready: BG003, ADMIN002, ADMIN003 and COMMERCE001 are Complete. No pool activation, deployment verification or deferred SYSTEM-TEST execution is claimed. Production holds and test-first manual verification remain coordinator-owned.

## Reconciliation provenance — 15 November 2026

Reconciled from the later local sender-pool revision formerly labelled ARCH-069. The completed chronological-input architecture and its ARCH-069 task identities are unchanged. ARCH-076 was already reserved for the earlier sender-pool proposal; this revision updates that proposal in place, retaining its Git history. These are definition changes, not implementation or deployment evidence. All execution remains Pending until compatibility review and dependency promotion.

## Mandatory same-conversation allowance renewal amendment

Historical renewal amendment is superseded for this sender task: allowance work belongs only to independent DATABASE-002/BACKGROUND-005 and does not gate sender routing. Never filter ownership by credit or cap.

### 15 November definition amendment

Historical fixed SQL must be regenerated for the restored five-entity contract plus R15 evidence; hardcoded router policy remains superseded. Historical claim/review evidence above is retained as history, not approval of the replacement implementation. No runtime source or migration has been implemented. User has authorized implementation; runtime acceptance and rollout verification remain pending.

Scope contract: verify exact thread generation and optional route generation before attribution. Unknown shop stays at thread scope; verified shop binds once to same-thread route. Historical quotes/statuses never acquire a newer generation after reuse.

## Existing singleton cutover proof boundary

BG002 must retain the approved non-pooled send-versus-enrollment fence, not merely change recovery transport endpoints. Before a new standalone/non-pooled provider permit, acquire the same transaction advisory membership key as Admin enrollment: `pg_advisory_xact_lock(hashtextextended('whatsapp-pool-membership:' || phoneId::text, 0))`. Under that lock reject the non-pooled permit if any inventory row exists for that exact phone, even allocation-disabled. Freeze the exact dispatchProviderAccountId/dispatchProviderPhoneNumberId pair on the durable root permit and current delivery parts; no network inside the lock. Enrollment collision preflight and permit must serialize on that key. Existing already-admitted/unknown provider work retains exact proof and must not be resent after cutover. Recovery initial/followup/AI/human sends use their existing assignment's sender; non-pooled sends may use only the permitted current credential identity and never bypass enrolled inventory.

BG003 must distinguish newly pooled routing from exact preexisting unassigned singleton evidence. An authentic quoted prior outbound, persisted inbound replay or exact status receipt may resolve its original existing Conversation using immutable recorded root/part sender evidence and matching authenticated WABA/phone/recipient. An old NULL root pair without another exact durable sender/recipient witness remains held; current singleton configuration alone never proves historical identity. Never fabricate sender proof, backfill assignment, bind old history to a new route generation or use recipient-only fallback to select an owner. Closed/expired history remains history and never reopens recovery or bypasses STOP/window/control/cap. Foreign sender statuses/quotes have no effects. This preserves production evidence, not a compatibility path for obsolete new schema formats.

Owner checks: concurrent standalone permit versus first disabled enrollment (either permit wins and enrollment reports protected use, or enrollment wins and permit is refused); inventory disabled still blocks new non-pooled permit; pooled endpoints never fall back to singleton; exact preexisting singleton quote/replay/status succeeds only with matching stable proof, wrong/changed/unknown account proof refuses, no assignment backfill or repeated provider admission. Partial BG001 may hold zero-inventory initial work, but inventory cannot activate until complete pinning/ownership path is test-verified and old consumers/inflight work are drained. Production auto-deploy holds remain.

## Proven preexisting unassigned recovery continuation

The clean-sender cutover may leave an old singleton unenrolled while its legitimate preexisting recovery Conversation continues. Permit only new customer-initiated in-window AI or human free-form replies on that exact unassigned Conversation when durable original sender AND recipient proof exists. This does not authorize proactive followup, new initial outreach, or generic unassigned recovery fallback.

Accepted proof sources are (a) a confirmed prior outbound root with its immutable dispatch sender pair plus the exact sent INITIAL RecoveryOutreachAttempt recipient tied to that root/Conversation, or (b) frozen multipart source recipient plus sender pair and confirmed matching part evidence. Match authenticated quote/replay/current owned human-command scope and the exact Conversation; a mutable customer/Conversation phone, current configuration alone, bare recipient lookup or an old NULL sender pair without another durable witness is insufficient. If proof is missing, changed or conflicting, hold without backfill, migration or guessing.

At each NEW reply permit, take the existing exact-phone non-pooled membership advisory fence, verify no inventory row exists for that phone (even disabled rows forbid this path), and hold current credential row FOR SHARE while checking its WABA/phone against the durable proof. Freeze exact sender pair on the new root/parts and use the proved recipient. Existing consent, STOP, window, moderation, control revision, quota and billing admission checks remain mandatory. Assigned recovery always uses assignment and never this path, even on missing credentials or drained inventory; all new initial recoveries require assignment.

A prior admitted/UNKNOWN provider operation is never retransmitted through this continuation path. Each new customer/human reply has its own existing idempotent message/command identity. Status callbacks and quoted history continue against original exact evidence, never a new route generation. Test successful AI and human continuation with both approved proof forms, NULL/no-witness refusal, changed sender/recipient refusal, inventory-disabled fence, concurrent enrollment versus permit, assigned-recovery refusal, initial/proactive-followup exclusion, and duplicate/unknown replay with no second provider send. This preserves a legitimate old conversation, not an obsolete schema-format adapter.
