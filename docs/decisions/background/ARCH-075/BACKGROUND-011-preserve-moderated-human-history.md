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
status: ready
priority: 5
executor: null
claimed_at: null
attempt: 0
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

## Work Items

- [ ] Capture raw-vs-prepared history mismatch RED using authoritative actualdefaulthumanpreparation.
- [ ] Correct bounded content-specific eligibility withfailclosedidentitychecks and existinglegacycompatibility.
- [ ] Prove unit+realPG dispatch/history/resume andnegativeguards; runrelevantchecks.
- [ ] Publish exactsource/mirroredreport thenreturnreview.

## Interfaces / Contracts

Existing Background HistoryCandidate, MerchantConversationSendCommand and immutable moderationassessment/prepared evidence. No crossservice/schema contract change expected.

## Dependencies

ARCH-075-BACKGROUND-010 Complete/integrated before execution.

## Enables

Root genuine human→AIhandback history verification. No implicitfurtherimplementation.

## Acceptance Criteria

- [ ] Deliveredpreparedhuman commonreply included once afterresume with exactALLOWidentity anduntrustedmerchantrolelabel.
- [ ] Tamper/foreign/missing/blocked/stalemodelpolicy/unsent invalidcasesremainexcluded/failclosed.
- [ ] Legacyvalidhistory/chronology/bounds/dedup preserved andnofullpayloadlogging.
- [ ] Unit+actualPG/defaultdispatch andrequiredbuild/scopedlint/fullrelevantchecks pass, isolatedsource/reportpublished.

## Validation

- [ ] RED/GREEN historymoderation unitvectors preparedvsraw,legacy,tamper/foreign/assessment/lifecycle negatives andboundedqueryassertions.
- [ ] ActualdisposablePG defaultdispatcher→realmoderation/delivery→history→resume inclusion, replayonce/rolelabels andguardnegatives;nohostedDBfallback.
- [ ] Relevantdeclaredfulltests/build/type/scopedlint with exactunchangedbaseline disclosure;diff/privacy andnormalcanonicalworktreeevidence.

## Stop Condition

Setreview/publishexactsource+reportandreturnarchitect;nomerge/deploy/liveops orproductreferralwork.

## Implementation Notes

Normal launcher dedicated mirrored worktrees. Youarenotalonepreservecurrentmain/others/primary. Rootprovidesprivateevidence; do notduplicate/printpayloads. Returnactualnewcontractgap beforewidening.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

Root owns operational evidence and rollout.

### Unresolved Issues

Live handback/history proof remains required; product referral separate.

### Architectural Concerns

Return gaps before expansion.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

No live acceptance or architecture completion claim.
