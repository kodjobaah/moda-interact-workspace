---
id: ARCH-075-BACKGROUND-015
architecture_id: ARCH-075
title: Bound AI product-list composition to branded caption budget
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
claimed_at: 2026-11-14T14:05:23Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Bound AI product-list composition to branded caption budget

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Bound AI product-list composition to branded caption budget.

## Context

User requests compact one-bubble AI product lists and website in clickable caption footer instead of image header. Published6 reader currently hardcodes website/header and checkout placement business policy; correct ownership once, saved template remains source of truth. No live source/activation changes by agents.

## Scope

Investigate then implement deterministic app-owned bounded product selection/composition for long AI lists, preserving exact verified IDs/facts/discount provenance and rendered mandatory STOP/checkout footer. Budget full caption<=1024 after actual canonical footer; no arbitrary model prose truncation, no human text truncation, no automatic invented selection or weakening model/receipt/permit guards. If no evidence-safe compact form fits, retain fullTEXT fallback. Shared6 renderer unchanged; root owns actual model/customer/live operations. Source profile/saved template remains authority. Concrete strategy below is authorized.

## Out of Scope

Unrelated refactors, arbitrary user-programmable layouts, new database/infrastructure, main merges/live operations. Preserve all others work.

## Requirements

Investigate then implement deterministic app-owned bounded product selection/composition for long AI lists, preserving exact verified IDs/facts/discount provenance and rendered mandatory STOP/checkout footer. Budget full caption<=1024 after actual canonical footer; no arbitrary model prose truncation, no human text truncation, no automatic invented selection or weakening model/receipt/permit guards. If no evidence-safe compact form fits, retain fullTEXT fallback. Shared6 renderer unchanged; root owns actual model/customer/live operations. Source profile/saved template remains authority. Concrete strategy below is authorized.

## Work Items

- [x] Implement only defined owning capability.
- [x] Add meaningful affected behavior regressions.
- [x] Record exact source and required checks.

## Interfaces / Contracts

Shared owns technical structure/hash/render safety; applications own trusted bindings/placement/operational authority. Existing Shared6 published source immutable. No duplicated shared codec.

## Dependencies

None

## Enables

None; dependent promotions architect-owned.

## Acceptance Criteria

- [x] Defined capability and owning-policy boundaries satisfied.
- [x] Hash/identity/tenant/receipt/permit and mandatory content integrity retained.
- [x] Required checks and exact immutable reports complete; no live/merge actions.

## Validation

Focused exact provenance/selection/budget/Unicode/mandatory footer/discount/no-fit/referral/HUMAN preservation tests, actual one provider send/billing root integration, types/build/scopedlint/exact CI. No unrelated broad repeats.

## Stop Condition

After required work/checks publish matching source and parent report, set review and STOP. Do not continue dependent work.

## Implementation Notes

Normal moda-task canonical sibling isolation/claim required. You are not alone; do not revert others. Pending consumer tasks may perform preparatory source work only after explicit architect Ready amendment; final acceptance requires accepted published dependency. No unpublished sibling imports or fabricated registry lock.

## Authorized composition strategy

Only overflowing AI verified-product answers may use compact deterministic presentation. Reuse existing verified-facts renderer and complete descending selected prefixes [n,n-1,...,1], maximum existing selected count3. Re-render each candidate through SAME saved common reference; select largest whose actual answer plus exact canonical authored footer fits1024 codepoints. Add one application-owned localized invitation equivalent to Ask me for more options on EVERY successful compact branch, counted in budget; no catalogue availability promise. This includes all three verified products fitting after replacing original fifteen-item prose. Never truncate arbitrary prose or HUMAN/nonproduct text. Preserve existing mandatory shipping/out-of-scope limitations. If no complete item fits or footer alone exceeds budget, retain fullTEXT fallback.

Filter derived presentation products, displayedPairs and independent proof/digest to EXACT retained selected pairs and original verified facts. These drive first image, displayed receipt and committed product-context update; removed pairs must not leak into presentation metadata. Original responseDigest stays original full host input for replay; derived caption/pairs/proof freeze together under existing application key. Observed knowledge references may remain distinct from displayed selections. Keep discounts/permit/current-source and one logical billing guarantees. Tests must prove exact subset provenance and replay/UNKNOWN no resend. Website move belongs saved-template revision, no runtime string replacement. Existing Shared6 sufficient for this task; independent website reader adoption is BG016.

## Completion Report

### Status

Ready for Review. Implementation, combined focused/PostgreSQL evidence, final committed build/type/scoped lint and both exact CI checks complete.

### Files Changed

- `src/commerce/compact-product-presentation.ts` and `.test.ts`: bounded complete verified-prefix fitting, explicit20locale invitation copy, exact retained pairs/presentation/proof filtering and mandatory-footer/Unicode/no-fit/limitations/discount tests.
- `src/commerce/presentation-receipt.ts`: opt-in descending positive prefixes3→2→1; existing default candidate output remains unchanged.
- `src/services/recovery-multipart/composition.ts`: only overflowing AI ANSWER verified-product composite path selects an actual saved-template-rendered fitting candidate; media preparation receives reduced trusted presentation; original responseDigest remains full host-input digest.
- `tests/unit/services/recovery-multipart/composition.test.ts`: fifteen-item model lead/verified3 compaction, one frozen composite/replay, exact original digest and filtered proof; AI/HUMAN nonproduct full-text preservation.
- `tests/unit/services/conversation-turn-processor/ai-wrapper.cases.ts`: observed omitted knowledge remains distinct from retained presentation metadata reaching final admission.
- `tests/integration/arch075-common-layout.integration.test.ts`: actual disposable PostgreSQL compact normal/UNKNOWN admission, exact retained proof/context, one provider image, one logical charge, no uncertain resend.

### Work Completed

Exact source `9e5a7f50d97aea739ff0851de2e44c739a6189f1` pushed to `task/ARCH-075-BACKGROUND-015`, draft PR https://github.com/kodjobaah/moda-interact-background/pull/227. Only the oversized AI verified-product branch recomposes from the existing Shared verified renderer; no arbitrary prose slicing, invented products/IDs/discount facts, zero-product details or model retries. Each complete prefix is rendered through the SAME immutable saved common reference, and actual answer+exact authored footer+localized invitation must fit1024codepoints. A budgeted invitation appears for every successful compact branch, including original15-item prose with all3 verified selections fitting, per root clarification recorded in task amendmentf90797024. It promises no catalogue availability.

Retained pairs drive displayed presentation metadata, first image and filtered independent verifiedProducts facts/digest. Individual verified facts and their order remain exact. The original full host-input responseDigest remains replay authority; derived canonical body/receipt/proof freeze under the existing application key. Observed knowledge references are not mistaken for displayed items. Media prep remains one call AFTER pure bounded fitting, one physical message/one logical billing reservation; existing lease, source, tenant, moderation, ownership and final-permit guards stay unchanged. Missing fit, overlong complete description/title/footer, nonproduct/referral and HUMAN content retain existing full-text behavior. No Shared/package/DB/model budget/layout placement changes; website adoption remains separately owned BG016.

### Validation Results

- Normal prepared launcher: primary `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; canonical parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-BACKGROUND-015`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-BACKGROUND-015`; mirrored task branches. Attempt1/codex claimed2026-11-14T14:05:23Z, parent claim32f121af347aec6d82b55467b7a329c1b4de035c pushed; synchronized parent87284cecc12c8150742fee70508c4bf16c3055f5/source d0c968e68d38031a9b3e884301573adbcbb08652. No explicit dependencies, recorded database submodule6f42b71112efe7ac63654d55f41cd74ca569b1ae ready. Root amendmentf90797024 read; no relaunch/reclaim or primary/other-task edits.
- Normal `npm ci` PASS; runtime production build PASS after correcting optional productFacts access. Final committed production build/type validation PASS (both declared TypeScript compilations).
- Combined170unique focused cases PASS:91 nonprocessor cases across helper/receipt/context/composition/frozen/budget plus final79 ConversationTurnProcessor cases. Final committed helper10/10PASS after test-only readonly-fixture correction. Initial traces retained: long-description test expected raw trailing whitespace instead of existing Shared canonicalized facts (fixed by immutable canonical snapshot); added Woo omitted-ID fixture used invalid nonnumeric ID (fixed to valid20); final typecheck caught test assignment to readonly verified (fixed to immutable fixture copy). No production guard weakened.
- Disposable actual PostgreSQL lifecycle combined13unique cases PASS: initial11PASS plus2 new compact normal/UNKNOWN cases passed targeted rerun. Original2 new-case failures were test expectation retained<3 while all3 legitimately fit; strengthened only valid synthetic titles to exercise3→2, then both affected cases PASS. Original run is NOT claimed all green. Existing nine HUMAN control/policy/generation/expiry/template/UNKNOWN paths and two ordinary AI paths retained; new compact path verifies filtered proof, exact selected prefix/presentation context, original logical root, one image/one automated charge/one delivery charge; UNKNOWN remains one attempt/no delivery charge/no resend. Command: `node scripts/test-integration.mjs tests/integration/arch075-common-layout.integration.test.ts --testNamePattern 'composite existing lifecycle'`; affected rerun pattern `actual AI composition/admission.*compact`. Only disposable test infrastructure, no managed database/provider calls.
- Scoped ESLint PASS both before and after the final test-only immutable-copy correction. `git diff --check` PASS. Exact known full-lint4 baseline remains untouched: candidate-index.store.ts:9 readRecoveryExecutionPolicy, recovery-offer-resolver.service.ts:23-25 MAX_CANDIDATES/VERIFICATION_TIMEOUT_MS/AI_TIMEOUT_MS; exact starting/current blobs8bff21b8514b4449dd326c1c1dac12a3ba4a8dbf /077bcbb76c018428bd5b64c0c82d2a1903b5c6e4 match prior proven BG006/BG007 baseline. No unrelated full-lint/broad-unit rerun or green claim.
- Exact source CI [43604763426](https://github.com/kodjobaah/moda-interact-background/actions/runs/43604763426) and [43604717962](https://github.com/kodjobaah/moda-interact-background/actions/runs/43604717962): both SUCCESS on9e5a7f50d97aea739ff0851de2e44c739a6189f1. Mirrored parent evidence checkpoint843bf7c1c pushed before this final review-status commit. Relevant private logs under primary `local-backups/arch075-bg015-*`: npm-ci, initial/final build, focused initial/final/corrected, processor-final, helper-final, postgres initial/compact rerun, types and scoped lint. These traces disclose every correction above.
- Diff/privacy review: no live IDs/secrets/customer payloads, provider/model calls, environment changes or arbitrary string truncation. No main merge/live send by this agent; root retains production canary/remaining message allowance.

### Deviations

Only root-authorized invitation clarification: every successful compact path includes the budgeted more-options invitation, even if all verified selections fit after replacing oversized model prose. Initial fixture/type corrections and combined-check receipts disclosed above; no hidden runtime fallback or test waiver.

### Assumptions

Existing published6 is sufficient for this independent task. Source common template/footer is authoritative; website/header policy is not rewritten here. Root coordinates accepted integration, BG016 follow-up and genuine canary.

### Unresolved Issues

If even one complete verified entry or mandatory footer cannot fit, full-text fallback remains intentionally unchanged. This implementation does not promise an image for arbitrarily long descriptions/titles/URLs or unavailable media, and does not trim human/nonproduct content.

### Architectural Concerns

No new queue, provider calls/retries, LLM token budget, generic logging, schema, dependency or application layout source. All business fitting policy remains Background; Shared retains renderer/technical safety. All required committed checks and exact CI are recorded above; no production success claim by this agent.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual code

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
