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
status: review
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

- [x] Add bounded whole-entry verified brief candidates and actual footer measurement.
- [x] Integrate conservative400/8line target without arbitrary prose truncation.
- [x] Prove exact retainedpair/proof/image/context consistency and safe nonfit behavior.
- [x] Return immutable source/report.

## Interfaces / Contracts

Existing published Shared6.1 verified presentation/renderer contracts; Background owns brevity policy. Reuse existing compact-product-presentation/presentation receipt/proof mechanisms without duplicate cross-service codecs.

## Dependencies

ARCH-070-BACKGROUND-011 Complete; independently executable from012. Final merged-source synchronization with012 required before integrated acceptance, not a blocking implementation dependency.

## Enables

Root source merge/deploy and genuine brief latest-question reply verification; client folding remains external behavior.

## Acceptance Criteria

- [x] Representative verified single/list captions fit400codepoints/8nonemptylines including exactwebsite+checkoutfooter.
- [x] Wholeentry/URL/facts/proof IDs retained consistently; no arbitrary model/human/policy truncation.
- [x] Footer-only/longtitle/mandatorylimitation nonfit keeps complete safe fallback withoutfalse guarantee.
- [x] No extra model calls, safety or delivery lifecycle regression.

## Validation

- [x] Unicode/emoji/longfooter/twoURL/stock/discount/shipping/option/single/list/longtitle/nonproduct/human tests.
- [x] Actualsavedcommon frame measurement and exactretainedpairs/proof/image/context/receipt tests.
- [x] Actual disposable lifecycle onebubble/oneusage/UNKNOWN/currentpermit no-send guards ifchanged.
- [x] Declaredtypes/build/scopedlint/exactCI; synchronize012 beforefinal affectedchecks.

## Stop Condition

After defined checks/report setReview and STOP. No provider/model/send calls or mainmerge bytaskagent.

## Implementation Notes

Normal dedicated mirrored worktree launcher, no implementationworktree at definition. Not alone: task012 owns history/instructions; this task owns briefhelper and narrowcomposition. Each task owner commits only own branch; merge accepted predecessor source explicitly when needed, preserveothers.

## Completion Report

### Status

Ready for Review. Exact Background `c4e87f9671a6ab984ef7956fb90d4a91cff8346f`, PR238; awaiting independent moda_architect review. No acceptance decision is made by this report.

### Files Changed

- `src/commerce/brief-product-list.ts`: explicit concise detail mode uses whole independently verified title, current formatted price/currency, truthful localized stock and complete selected options. Full description/attributes remain unchanged in the retained proof.
- `src/commerce/compact-product-presentation.ts`: actual 400-Unicode-point/eight-nonempty-line measurement, largest complete target-fitting prefix, truthful target-not-met/hard-limit fallback and exact retained proof/pair filtering. Rich shipping/policy/offer qualifications cannot be rewritten as bare details.
- `src/services/recovery-multipart/composition.ts`: narrow predicate/import change triggers the same trusted fitter below the old 1024-only threshold; existing media, receipt/application, replay and delivery paths remain.
- Embedded brief/compact unit tests, saved-common composition tests and bounded existing disposable common-layout lifecycle modes.

### Work Completed

Caption measurement includes the actual rendered body and exact authored website/STOP/checkout footer, not placeholder URL estimates. Whole verified entries are never sliced. A single explicit brief detail may omit optional verbose narrative while keeping the complete original facts/proof, selected variant options, money/currency and stock. The extra single-product invitation is omitted to minimize wording; lists retain existing localized ask-for-more copy. Twenty application-owned short product-stock labels are provided; precise variant stock/unknown/not-tracked copy reuses the existing renderer catalogue.

Retained pairs, proof, image first pair and presented context remain aligned; original response digest and immutable replay identity remain unchanged. If no whole entry fits the soft target, the smallest complete safe candidate within the existing 1024 technical caption bound may report target-not-met. If none fits, the original complete safe TEXT behavior remains. Mandatory footer/title/URL/policy/discount/shipping content, nonproduct/human/referral responses and provider UNKNOWN semantics are never cut to satisfy a UI target. Client folding is not controlled or guaranteed.

Pre-review identified a rich-detail policy edge: the factual projection can have requiresShipping null/false while the validated envelope retains shippingInformationSelection or an unverified/redirect disposition. Concise rewriting now refuses all such adjuncts, any nonnull policy URL/requiresShipping value, and offer/no-verified-offer requirements, preserving the complete original answer. This is Background policy only; no Shared, dependency, model/provider, schema, saved-template or infrastructure change.

Normal launcher claimed attempt1/codex at parent `87255673d260f2f178c2de6c1955da16aa3105a1`, implementation baseline `68fd52ca98ac6f94df871e2c4478f96460b7ee6e`, recursive Database `6f42b71112efe7ac63654d55f41cd74ca569b1ae`, using dedicated mirrored `task/ARCH-070-BACKGROUND-013` worktrees. Accepted BG012 actual main `79cee094e0e0b7bd0bd6959a5ae46dc72755a93e` was merged normally as `356c266a9ae57146e3b918b5e97ec413d93b8e3a` before final affected checks; no history/instruction/gate source was edited by this task. Final parent origin/main synchronization encountered architecture/index conflicts outside agent authority; coordinator resolved/pushed `40b946f30`, preserving both histories and accepted main gitlink. This agent did not stage a feature gitlink or resolve those protected files.

### Validation Results

- Clean declared `npm ci` and Prisma generation passed with existing published Shared6.1.0; no dependency edits.
- Final exact-head affected tests: **118 passed / three files** (`/tmp/bg013-exact-focused.log`). Includes Unicode/emoji, explicit line bounds, long footer and two URLs, whole title/price/stock/variant options, all twenty locales, exact proof/subset/source immutability, rich shipping/null/false/policy/redirect preservation, nonproduct/human safety, source response digest and frozen replay.
- Disposable PostgreSQL/Redis AI lifecycle: **nine passed / 50 intentional name-filter skips**, 15.44 seconds (`/tmp/bg013-terminal-pg.log`), on the combined accepted BG012 tree. Includes below-1024 concise single, complete lists, immutable proof/context, one bubble/root/usage, UNKNOWN no resend and stale-current-permit refusal. Later shipping-adjunct guard changes only preserve additional original bodies and are covered by actual composition regressions; normal permit/engine code is unchanged.
- Additional requested existing DEFAULT HUMAN consolidated lifecycle on final head: **one passed / 58 intentional name-filter skips**, 6.92 seconds (`/tmp/bg013-exact-human-pg.log`), proving existing freeze/replay/history integration after BG012.
- Final declared `npm run build` (Prisma, TypeScript and provision build), seven-file scoped ESLint and `git diff --check` all passed (`/tmp/bg013-exact-build.log`, `/tmp/bg013-exact-lint.log`).
- Both exact-head remote runs **43664260607** and **43664253381** SUCCESS. Actual declared unit log: **4553 tests / 402 files passed**, 106.94 seconds. Embedded commerce tests are also explicitly covered by the local affected run; no unchanged broad local full-suite repeat.
- Private offline historical receipt, pure saved-template render plus existing verified facts/proof: **516 UTF16 units / 513 Unicode points → 286 Unicode points / six nonempty lines**, target met. Exact footer, checkout once/final, original verified first pair and image/logo receipt unchanged. `/tmp/bg013-offline-counts.json` contains aggregate invariants only. No DB/model/provider/send occurred. This is historical offline evidence, not current stock or genuine production delivery. The canonical product formatter does not strip the actual default selected option, so it was retained rather than introducing a new heuristic.

### Deviations

Initial checks exposed an optional selectedOptions access (fixed), old 1024-only/full-single expectations superseded by the authorized brief policy, canonical variant label/mandatory-line assumptions, and a changed-description fixture whose unchanged proof correctly failed verification. Fixtures now use the same complete refreshed proof and canonical labels; no verification was relaxed. One type-only fixture attempted to assign a readonly top-level verified field; final c4e87f9 uses an immutable derived fixture.

Initial new stale PG assertion expected a resolved suppression/zero usage. The unchanged engine correctly throws MULTIPART_OWNER_STALE, and the normal reservation already records one outbound usage event. The test now asserts that exact refusal, zero provider sends, unchanged reservation accounting and zero delivered usage; no runtime permit, billing, timeout or retry change. All nine lifecycle cases then passed.

### Assumptions

400 points/eight nonempty lines is an application brevity target, not a WhatsApp Read more threshold. URL wrapping, blank-line rendering and client version can still cause folding. Trusted mandatory content wins over brevity; unverified category/nonproduct prose is preserved rather than arbitrarily summarized.

### Unresolved Issues

No implementation blocker. Root owns source/main integration, deployment and any genuine latest-question/caption canary; this task performed no live operations or quota changes.

### Architectural Concerns

No claim that concise composition fixes selection/model failures or guarantees physical Meta delivery/client display. Existing fallback011 and all consent/control/lease/window/UNKNOWN/usage/provenance guards remain authoritative.

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
