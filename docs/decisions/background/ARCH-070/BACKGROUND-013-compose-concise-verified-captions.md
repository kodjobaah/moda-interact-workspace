---
id: ARCH-070-BACKGROUND-013
architecture_id: ARCH-070
title: Keep verified recovery captions concise
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-15T01:20:37Z
attempt: 1
depends_on:
  - ARCH-070-BACKGROUND-011
enables: []
created: 2026-11-15
updated: 2026-11-15
---

# Keep verified recovery captions concise

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; moda_architect.

## Objective

Keep verified product captions conservatively concise while preserving complete trusted footer and presentation provenance.

## Context

Actual production captions885 and516codepoints both fall below1024 technicallimit yet client may fold them. Existing verified compaction triggers only above1024, so it cannot meet user brevity request. Root authorizes conservative app caption budget around400, not a guaranteed WhatsApp display threshold. Task012 independently fixes old question contamination.

## Scope

Application-owned concise verified single/multi-product presentation and actual common-footer budget measurement; new brief helper/copy/tests plus narrow composition integration. No history-loader edits.

## Out of Scope

Shared release/rendering machinery, provider/model/token changes, arbitrary model/human/policy prose truncation, URL shortening/cutting, unsafe product/evidence inference, savedtemplate edits, live calls/mainmerge.

## Requirements

Use conservative application target<=400 Unicode codepoints for actual caption body plus EXACT authored footer, and<=8 nonempty lines, including website and canonicalcheckout lines. Count actual resolved savedcommonfooter, not placeholder URL assumptions. This is a brevity target, not a guarantee against client Read more; do not claim control of client UI.

Apply deterministic concise candidates for verified product replies even when original caption fits1024 but exceeds this target. Single-product factual detail may omit optional verbose descriptions in explicitly brief mode, retaining whole verified title/currentprice/currency and relevant stock/option facts without inventing unavailable facts. Multi-product candidates retain whole verified entries, select largest complete bounded prefix and clear localized ask-for-more invitation, never arbitrary prose slicing or inference from old history. Product IDs/variants come only from already independently verified selected presentation; retainedpairs, imagefirstpair, verifiedproof/digest, receipt/context updates and finalpermit MUST exactly match the actually shown subset. Original source response digest stays frozen for replay matching. All mandatory discount/shipping limitation/STOP/checkout policy wording remains preserved.

Do not truncate ordinary policy/nonproduct/human answers merely tohitbudget or remove meaningful exceptions/mandatory text. Existing concise guidance may request at mosttwo focused sentences in ordinary model answers, but renderer must not delete arbitrary prose. If trustedfooter alone or one whole valid entry cannot fit400/8lines, preserve safe complete existingfallback behavior (including fullTEXT when needed), report target-notmet ratherthan cutfooter/title/URL/facts or falselypromise nofold. Existing1024 technicalsafety still applies where compositeprepared. No Sharedchange or independentlayout authority.

Own new shortcaption helper/copy/tests and composition.ts only narrow imports/candidate invocation. Root task012 owns history/RECOVERY_INSTRUCTIONS; coordinate no concurrent edits to that file. Final sync accepted012 before integration and rerun only affected checks if imports/compositionchanged; no code copying from sibling source. Preserve fallback011/consent/control/lease/window/idempotency/UNKNOWN/usage/receipt/finalpermit guards. Root owns savedtemplate/provider/live verification.

## Work Items

- [ ] Add bounded whole-entry verified brief candidates and actual footer measurement.
- [ ] Integrate conservative400/8line target without arbitrary prose truncation.
- [ ] Prove exact retainedpair/proof/image/context consistency and safe nonfit behavior.
- [ ] Return immutable source/report.

## Interfaces / Contracts

Existing published Shared6.1 verified presentation/renderer contracts; Background owns brevity policy. Reuse existing compact-product-presentation/presentation receipt/proof mechanisms without duplicate cross-service codecs.

## Dependencies

ARCH-070-BACKGROUND-011 Complete; independently executable from012. Final merged-source synchronization with012 required before integrated acceptance, not a blocking implementation dependency.

## Enables

Root source merge/deploy and genuine brief latest-question reply verification; client folding remains external behavior.

## Acceptance Criteria

- [ ] Representative verified single/list captions fit400codepoints/8nonemptylines including exactwebsite+checkoutfooter.
- [ ] Wholeentry/URL/facts/proof IDs retained consistently; no arbitrary model/human/policy truncation.
- [ ] Footer-only/longtitle/mandatorylimitation nonfit keeps complete safe fallback withoutfalse guarantee.
- [ ] No extra model calls, safety or delivery lifecycle regression.

## Validation

- [ ] Unicode/emoji/longfooter/twoURL/stock/discount/shipping/option/single/list/longtitle/nonproduct/human tests.
- [ ] Actualsavedcommon frame measurement and exactretainedpairs/proof/image/context/receipt tests.
- [ ] Actual disposable lifecycle onebubble/oneusage/UNKNOWN/currentpermit no-send guards ifchanged.
- [ ] Declaredtypes/build/scopedlint/exactCI; synchronize012 beforefinal affectedchecks.

## Stop Condition

After defined checks/report setReview and STOP. No provider/model/send calls or mainmerge bytaskagent.

## Implementation Notes

Normal dedicated mirrored worktree launcher, no implementationworktree at definition. Not alone: task012 owns history/instructions; this task owns briefhelper and narrowcomposition. Each task owner commits only own branch; merge accepted predecessor source explicitly when needed, preserveothers.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

400codepoints/8nonemptylines is conservative apppolicy, not guaranteed clientthreshold.

### Unresolved Issues

None before scoped execution.

### Architectural Concerns

Mandatory fullfooter and provenance win over brevitytarget.

## Architect Review

### Review Status

Pending

### Review Notes

DefinedReady for independentappcomposition.

### Reviewed Files

Existing compact-product-presentation.ts1024 target and composition seam.

### Validation Reviewed

Root productioncaption885/516 evidence; no implementationvalidationyet.

### Architecture Conformance

Backgroundpolicy only, no Sharedorproviderchange.

### Follow-up

Execute via normal launcher; root integratedcanarylater.
