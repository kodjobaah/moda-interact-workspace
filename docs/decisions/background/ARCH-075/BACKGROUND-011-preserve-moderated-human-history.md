---
id: ARCH-075-BACKGROUND-011
architecture_id: ARCH-075
title: Preserve moderated delivered human replies in resumed AI history
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 5
executor: codex
claimed_at: 2026-11-13T21:33:11Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-010
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Preserve moderated delivered human replies in resumed AI history

## Architecture

ARCH075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Include eligible delivered merchant replies after AI handback using the same canonical prepared-body moderation identity as human dispatch.

## Context

Actual latest21:11 delivered/read human common root378chars has exact immutable ALLOW for preparedTextBody, while raw command83chars differs. moderation-assessment effectiveText uses preparedTextBody; moderation-history allowedHistoryCandidates compares raw textBody and drops this delivered human reply. Root owner read-only evidence confirms mismatch; no reset or new message is required to establish source defect. Videographer search/referral is separate and causal details unproven.

## Scope

Background moderation history eligibility and directly affected commerce/history default-dispatch regressions; reuse existing authoritative effectiveText/prepared evidence identity.

## Out of Scope

Product search/referral redesign, modelprompt/roles broadchange, Shared/API/DB schema, livewrites/replays/reset, relaxing moderation/modelpolicy/tenant/contentguards.

## Requirements

- Compare HUMAN_TEXT moderation ALLOW against exact authoritative prepared body used by dispatch (or unchanged legitimate legacy raw body when no prepared identity exists), not blindly rawcommandtext. Use existing trusted effective-text/immutable evidence semantics, no arbitrary fallback from malformed explicit preparation.
- Prove candidate message belongs to exact shop/conversation/outbound command identity and content matches authorized delivered canonicalbody. Wrongtenant/conversation/message, tamperedbody, missing/blocked/stalepolicy/model evidence, unsent/cancelled command or invalidpreparedreceipt must not gain eligibility. Preserve any established legacy rawbody path only when its own exact validcontent assessment matches.
- Use bounded batched queries, no per-message external/DBnetwork calls or broadened history scan. Existing20message/32000bound, chronology/dedup/currentturn and merchant-authored untrusted-history rolelabel stay unchanged. Never elevate merchanttext into system/agent instruction.
- Real default human dispatch→moderation→delivered root→loadCommerceHistory→AIresume regression must show the actual message appears once under merchantuntrustedlabel. Include rawtext/body mismatch from commonheader/footer, restart/replay and relevant wrongcontent/tenant/assessment negatives. No fabricatedALLOW forwrongcontent to forcepass.
- Existing sharedlogging only if diagnosis changes necessary; no fullcustomertext/credentials inlogs. Rootalone deploys/livehandbacktest; ownerusesdisposablePG/Redis/loopbackprovider only.

- Inspect the existing CUSTOMER ingress/control-HUMAN moderation capture path before claiming complete handback awareness. A real customer message received during HUMAN mode currently has no ALLOW and remains correctly excluded. Do not admit unmoderated content, fabricate evidence, or alter model roles. Report the precise owning capture-path gap and a bounded follow-up contract if fixing it introduces a separate mechanism; this task does not claim both sides of the exchange are restored solely by the merchant hash correction.

## Work Items

- [x] Capture raw-vs-prepared history mismatch RED using authoritative actualdefaulthumanpreparation.
- [x] Correct bounded content-specific eligibility withfailclosedidentitychecks and existinglegacycompatibility.
- [x] Prove unit+realPG dispatch/history/resume andnegativeguards; runrelevantchecks.
- [x] Inspect CUSTOMER-during-HUMAN capture and report whether existing safe moderation is retained; document a separate bounded follow-up if required.
- [x] Publish exactsource/mirroredreport thenreturnreview.

## Interfaces / Contracts

Existing Background HistoryCandidate, MerchantConversationSendCommand and immutable moderationassessment/prepared evidence. No crossservice/schema contract change expected.

## Dependencies

ARCH-075-BACKGROUND-010 Complete/integrated before execution.

## Enables

Root genuine human→AIhandback history verification. No implicitfurtherimplementation.

## Acceptance Criteria

- [x] Deliveredpreparedhuman commonreply included once afterresume with exactALLOWidentity anduntrustedmerchantrolelabel.
- [x] Tamper/foreign/missing/blocked/stalemodelpolicy/unsent invalidcasesremainexcluded/failclosed.
- [x] Legacyvalidhistory/chronology/bounds/dedup preserved andnofullpayloadlogging.
- [x] Customer-during-HUMAN capture gap is traced to actual source and explicitly dispositioned; unmoderated rows remain excluded and no unsupported both-sides awareness claim is made.
- [x] Unit+actualPG/defaultdispatch andrequiredbuild/scopedlint/fullrelevantchecks pass, isolatedsource/reportpublished.

## Validation

- [x] RED/GREEN historymoderation unitvectors preparedvsraw,legacy,tamper/foreign/assessment/lifecycle negatives andboundedqueryassertions.
- [x] ActualdisposablePG defaultdispatcher→realmoderation/delivery→history→resume inclusion, replayonce/rolelabels andguardnegatives;nohostedDBfallback.
- [x] Relevantdeclaredfulltests/build/type/scopedlint with exactunchangedbaseline disclosure;diff/privacy andnormalcanonicalworktreeevidence.

## Stop Condition

Setreview/publishexactsource+reportandreturnarchitect;nomerge/deploy/liveops orproductreferralwork.

## Implementation Notes

Normal launcher dedicated mirrored worktrees. Youarenotalonepreservecurrentmain/others/primary. Rootprovidesprivateevidence; do notduplicate/printpayloads. Returnactualnewcontractgap beforewidening.

## Completion Report

### Status

Ready for Review. Implementation `01702b7ccf86c195f16ba6eee6a21248e1524c30` committed and pushed on mirrored `task/ARCH-075-BACKGROUND-011`. No main merge, live write, replay or send by executor.

### Files Changed

- `src/services/conversation-moderation/moderation-history.ts`: two existing bounded batches now fetch canonical preparation and exact linked command/root/conversation/recovery identity. HUMAN requires SENT command, sent eligible HUMAN root, exact candidate/root/canonical body, valid immutable preparation and current-model/current-policy ALLOW. Explicit malformed or partial preparation cannot fall back to raw text. Genuine legacy raw path requires all prepared fields absent and its own exact content assessment.
- `src/services/recovery-conversation/human-prepared-command.service.ts`: export/reuse the pure immutable prepared-body reader from dispatch; existing common receipt/application-key checks retained, legacy RENDERED key checked with the same existing final-permit algorithm. No active-slot requirement for historical delivered content.
- New `tests/unit/services/conversation-moderation/moderation-history.test.ts`: prepared/raw mismatch, legacy compatibility, eleven identity/content/assessment/lifecycle refusals and two bounded query assertions.
- `tests/integration/arch075-common-layout.integration.test.ts`: actual default HUMAN dispatcher, real SQL moderation service with deterministic classifier, loopback WhatsApp send, AI handback and actual loadCommerceHistory show the complete prepared reply once with user-role untrusted merchant label; repeated read/replay unchanged.
- `tests/integration/conversation-moderation.integration.test.ts`: old raw-input assertion corrected to the actual persisted prepared body moderated by dispatch; BLOCK/no-send assertions unchanged.

### Work Completed

Corrected the demonstrated delivered merchant history gap without relaxing moderation, tenant or delivery identity. Existing history chronology, deduplication, current turn selection, prior20/32000 Unicode bounds and merchant role label remain unchanged. No per-message DB/provider calls were added to history: preparation validation is pure and query count remains two batched calls. HUMAN cannot bypass command identity using an unrelated generic message ALLOW.

### Customer During HUMAN — Explicit Disposition

Separate gap confirmed; not implemented in this task. `whatsapp-inbound-processing.service.ts:290–299` persists text then returns before enqueue when control is HUMAN; audio completion uses the same branch at145–151. Current `ModerationTurnGate.moderatePending` is invoked only by the AI turn processor (`conversation-turn-processor.service.ts:375` after control/claim checks). Therefore customer messages received during HUMAN mode can lack immutable ALLOW and remain correctly excluded. This merchant correction does not claim both sides of handback are restored.

Bounded follow-up contract returned to architect and materialised separately as Pending BG012: before the next genuine AI invocation, reuse existing moderation service/turn gate to classify exactly the same visible prior20 plus existing current-turn candidates, dedup IDs, persisted TEXT or COMPLETED AUDIO only, current model/policy/content/tenant; cached assessments and leases remain idempotent. Historical BLOCK/REVIEW remain excluded; historical retry must not alter current-turn allowed/suppressed semantics or cause AI/provider sends during HUMAN. No arbitrary whole-history scan or fabricated assessment.

### Validation Results

- Unit baseline RED against exact unchanged 1b71a7d history reader:2fail/11pass; GREEN focused17tests/2files.
- Actual default-dispatch PG baseline RED: real canonical prepared moderation and delivered root followed by AI resume yields0 merchant entries instead of1 with old reader;1failure/36name-filter skips,7.19s. Source restored identically before final validation.
- Final real disposable PostgreSQL/Redis run:2suites47tests PASS,0skip,66.97s (`arch075-common-layout`, `conversation-moderation`). Includes actual default runtime, immutable moderation, history resume/replay, existing BLOCK/current-model/policy and delivery guards. No hosted database fallback.
- Declared full `vitest run`:392files PASS/1 existing configured skipped;4328tests PASS/10 existing configured skipped,260.84s. Skips are existing environment gates, not substitutes for actual PG.
- Build PASS: Prisma6.19.3 generation, both TypeScript compilers, sample artifact packaging. Scoped ESLint5changed files and diff check PASS.
- Known full-lint baseline remains the four unchanged unused-variable errors documented with exact HEAD proof in BG010: candidate-index.store.ts:9 readRecoveryExecutionPolicy; recovery-offer-resolver.service.ts:23–25 MAX_CANDIDATES/VERIFICATION_TIMEOUT_MS/AI_TIMEOUT_MS. Both files unchanged against1b71a7d; no full-lint-green claim or unrelated cleanup.
- Initial PG run: common-layout suite passed37; moderation suite had one obsolete raw-input expectation and one first-pull Aimock timeout. The expectation now asserts exact persisted prepared body. Pinned image `ghcr.io/copilotkit/aimock:1.45.1` was explicitly cached (digest fc4b72a999544c6c7e475da756932d3384d315da99e66695e5a60d6a2798ec0b); complete final PG run passed. No production code changed after full/build validation; only this relevant PG assertion was corrected, then scoped lint and complete PG rerun passed.
- Local evidence: `local-backups/arch075-live-20261113/bg011-{red,focused,postgres-red,postgres-final,full-tests,build,lint-final,aimock-pull}.log`. Real private production evidence was not committed or printed as payload.

### Isolation / Publication Evidence

Normal prepared launcher: dependency BG010 Complete; dedicated parent and implementation worktrees on `task/ARCH-075-BACKGROUND-011`; canonical primary workspace; parent03464d6f4 and implementation1b71a7d3582f6f946939ac669a9308f1a0c66b01 synchronized; recursive database6f42b71112efe7ac63654d55f41cd74ca569b1ae exact ready. Attempt1codex claimed2026-11-13T21:33:11Z, pushed claim39251e4f00ded41de38a52367bc8b490d527c30c. Implementation clean after push. No parent gitlink, other task/index, Shared, schema or primary checkout edits.

### Deviations / Assumptions

No feature scope deviation. Existing current moderation operation is supplied by the disposable fixture, not production configuration, while actual persisted source and assessments are used. Root owns independent review, merge, deployment and real history/handback verification.

### Unresolved Issues / Architectural Concerns

BG012 customer moderation backfill remains separate and Pending. Product referral/search cause remains unproven and was not changed. No live verification or architect acceptance claimed by executor.

## Architect Review

### Review Status

Accepted

### Review Notes

Independently inspected exact implementation 01702b7ccf86c195f16ba6eee6a21248e1524c30 and mirrored report a43d7eb4c7518f50a49ff1d82ce0bf5f6b0cee20. No findings. Canonical prepared-body validation is reused rather than accepting raw text or arbitrary assessment evidence. Historical HUMAN eligibility requires exact linked SENT command/root, tenant/conversation, authorized body and current ALLOW. Explicit malformed preparation cannot fall back. The legacy rendered application-key check matches established final-permit semantics. Candidate role, bounds and chronology are unchanged.

The PG assertion correction was reviewed against actual dispatcher/canonical moderation source: assessment already receives persisted preparedTextBody; the test still requires BLOCK and zero outbound/provider/billing admission. This corrects expected transport input without weakening policy.

### Reviewed Files

- src/services/conversation-moderation/moderation-history.ts
- src/services/recovery-conversation/human-prepared-command.service.ts
- tests/unit/services/conversation-moderation/moderation-history.test.ts
- tests/integration/arch075-common-layout.integration.test.ts
- tests/integration/conversation-moderation.integration.test.ts
- Existing human dispatcher, moderation canonical source and Commerce history/control path.

### Validation Reviewed

Actual default-dispatch PG baseline RED and final two disposable suites 47 PASS/0 skips; focused17; full4328 PASS with10 existing configured skips; build/both TypeScript compilers, changed-file lint and diff checks. Four unchanged unrelated full-lint baseline findings are disclosed, not represented as green. Prepared launcher isolation/synchronization/recursive database evidence and clean mirrored publication reviewed. No unnecessary heavy rerun.

### Architecture Conformance

Conforms to bounded Background ownership and existing immutable moderation/security contracts. No Shared/schema/infrastructure/telemetry changes, provider mutations or live data rewrites. Task completion is source acceptance, not live architectural completion.

### Follow-up

BG012 remains Pending until actual source/parent integration, then may be promoted for bounded CUSTOMER handback moderation. Root owns merges, rollout and genuine both-sides context proof. ARCH-075 remains In Progress; unrelated product-referral cause is unproven and unchanged.
