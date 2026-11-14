---
id: ARCH-075-BACKGROUND-019
architecture_id: ARCH-075
title: Fit overflowing multi-product details with verified brief summaries
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
claimed_at: 2026-11-14T16:57:40Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-015
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Fit overflowing multi-product details with verified brief summaries

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Keep originally multi-product verified detail lists within the one-image caption budget using honest brief summaries.

## Context

BG015 preserves complete descriptions, so category detail selections may still overflow and lose logo toTEXT. User authorizes shortening long lists, not arbitrary prose or single-product detail loss. Root confirms multi-product overview policy without newintentcontract.

## Scope

Background compact presentation summary branch/localizedcopy and meaningful provenance/actualsavedcaption regression tests.

## Out of Scope

Single-product detail shortening, arbitrary prose slicing, model selection/Shared/wire/schema/provider changes, live/main operations.

## Requirements

User and root explicitly authorize brief list presentation when ORIGINAL AI PRODUCT_DETAILS selects at least2 verified products AND actual saved-frame answer+mandatory footer exceeds1024codepoints. No category-intent wire or customer/model-prose heuristics. Do not change single-product detail fidelity: one originally selected product keeps complete facts or existingTEXT fallback. In eligible multi-item overflow only, produce an explicitly brief canonical summary from complete verified title/current price/currency/stock/category fields where observed; do not slice descriptions, assert description unavailable, infer quantities/categories or invent facts/links/discounts. Omit optional long narrative intentionally as summary, preserve full independent verified evidence. Include localized brief/ask-more presentation without catalogue availability claim; use supported20locale application copy.

Reuse bounded descending complete selected prefixes and SAME saved common template/footer; require actual caption<=1024 including clickable website once and exact checkoutfooter/STOP content last. First retained image, displayed pairs/presentation metadata/context and filtered proof must align exact retained identities while original full responseDigest replay authority stays unchanged. No source/header/footer surgery or mandatory content truncation. Complete title/facts cannotfit→safe fullTEXT fallback. HUMAN/nonproduct/referral/PRODUCT_OPTIONS/recommendation behavior unchanged unless existing helper defaults already preserve it. Existing control/source/moderation/tenant/policy/receipt/finalpermit/billing/UNKNOWN guards unchanged. No Shared/dependency/model/retry/budget change. Coordinate BG008 selectionguidance independentfiles; sync acceptedmain before finalcheck if it merges.

## Work Items

- [x] Add strictly eligible multi-product detail summary branch.
- [x] Preserve complete verified fields/proof/pairs and exact footer budget.
- [x] Add unit/actualservice/disposable lifecycle regressions.
- [x] Record exactsource/isolation/check evidence.

## Interfaces / Contracts

Existing Shared6.0.1 verifiedfacts/renderer/receipt machinery unchanged; app owns list presentation policy. Existing immutable saved template owns caption footer/header.

## Dependencies

ARCH-075-BACKGROUND-015 Complete/integrated.

## Enables

Root genuine productlist/logo/clickablewebsite/checkout verification after combined source integration.

## Acceptance Criteria

- [x] At least2 originally selected longdescription facts can yield honest brief fitting composite with exactretained proof.
- [x] Single-originalproduct complete detail behavior unchanged; no-fit fallback intact.
- [x] Actual savedwebsite+checkout/STOP caption<=1024 with one providerimage/rootbilling, no omittedpair metadata.
- [x] Replay/UNKNOWN/currentpolicy/tenant/control guards unchanged.

## Validation

- [x] Focused Unicode/locales/longdescriptions/singleproduct/no-fit/nonproduct/HUMAN/referral/proof tests.
- [x] Actualservice/disposablePG oneimage/oneusage/retainedproof/context/UNKNOWN and bothfooterURLs.
- [x] Types/build/scopedlint/exactCI/diffprivacy, no unrelated broadlocal repeats.

## Stop Condition

After required work/checks push source+matchingreport, review and STOP. Root owns merges/live.

## Implementation Notes

Normal moda-task dedicatedsiblings/claim. You are not alone; BG008 touches categoryguidance/hostserialization, do not edit those or revertothers. No fakeprovider credentials/private actualsource fixtures.

## Completion Report

### Status

Ready for Review — exact source and required checks passed; no live or main operations.

### Files Changed

- `src/commerce/brief-product-list.ts`: strictly verified multi-product detail summary candidates and20locale brief/price/category copy; existing Shared money/stock/i18n/schema mechanics reused.
- `compact-product-presentation.ts`: opt-in brief detail candidates before existing full candidates; unchanged filtering/responseDigest/receipt application.
- New brief-product-list unit tests.
- Existing common-layout disposable lifecycle fixture: explicit saved website/STOP/checkout frame and brief normal/UNKNOWN cases; existing cases retain behavior.

### Work Completed

Exact implementation `09298ac0369cfce1c4484bf8265f2b1b8bb18053` pushed, source PR232. Existing caller still limits fitting to overflowing AI ANSWER caption; new summary candidates require PRODUCT_DETAILS with at least two distinct ORIGINAL product IDs. Same-product multi-variant detail rows remain complete, preserving single-product fidelity. No prose/customer-intent heuristics. Before formatting, existing Shared verification proves exact original selected facts against complete fresh independent product proof. Whole titles, observed current money/currency, canonical stock and observed productType are rendered; optional missing price/category omitted without invented values. Long descriptions/options/attributes are intentionally not rendered in the explicitly marked brief list, but remain intact/AVAILABLE in frozen fact/product evidence. No fake unavailable description or fact-status mutation.

Same saved source/footer renderer, existing localized ask-more line, descending full-entry prefixes, exact caption<=1024 codepoints and original responseDigest replay authority remain. Filtered fact/proof/displayed pairs/first image/context align to retained identities; no-fit returns existing completeTEXT fallback. Single-original-product, HUMAN/nonproduct/referral/PRODUCT_OPTIONS/recommendation paths remain unchanged. No dependency, Shared, schema, model, retry, budget, provider, admission/billing or telemetry changes.

Root-required accepted BG008 source main `2bfc7074a7cd2808f65994d301d52649948cf8d5` synchronized into this task via clean fast-forward before final checks; three accepted instruction/host-test files preserved without changes. No ownership collision.

### Validation Results

- Normal prepared launcher: primary `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; dedicated parent `moda-interact-workspace-task-ARCH-075-BACKGROUND-019` and implementation `moda-interact-workspace.worktrees/ARCH-075-BACKGROUND-019`, matching task branches. Initial parent e8ca8fc3771c38605a6b1ce9ee3b881b3eba96a6/source8244752ba6dd987eb8873e216b2fec75011ad0f0; origin task sync not-needed/main already-current both. Recursive database6f42b71112efe7ac63654d55f41cd74ca569b1ae sync/update/statusready. Attempt1/codex16:57:40Z claim37ee2681e673899514ce3fd1fe291cb53d125955 pushed. Dependency BG015 Complete. No primary/other-task edits.
- `npm ci --no-audit --no-fund`: PASS; declared package scripts inspected, package/lock unchanged. Initial focused80/3files and build PASS; after accepted2bfc main synchronization, final production build/types and same affected80/3files PASS. Scoped ESLint all4 changed files/diff/privacy PASS.
- Unit vectors cover20locales, fullnarrative proof preserved, whole title/price/stock/category, missing/duplicate/tampered proof rejection, original single-product and same-product variant preservation, no-fit/Unicode/footer safety, reduced prefix still brief with exact retained proof, and unchanged referral/non-detail/default behavior. Existing actual composition tests cover replay/original responseDigest and HUMAN controls.
- Actual disposable PostgreSQL final4PASS/48 intentionally name-filtered skips,15.33s: normal and UNKNOWN brief plus existing compact normal/UNKNOWN cases. Saved template has website and STOP in conditional before exact final checkout URL; caption<=1024, header bitmap input excludes website, full selected description proof retained; one image, one logical root/normal usage, retained image/context/pairs match, UNKNOWN does not resend and delivery usage stays0 until actual delivered status. No live provider calls.
- Initial two new PG cases failed only reused BG015 assertion requiring fewer than3 retained selections; new brief output correctly fitted all3. Updated ONLY brief-specific assertion to exact3, retaining old compact strict<3 and all proof/context/transport assertions. No runtime/timeout/guard relaxation; final4case rerun passed.
- Exact source CI43619604819 and43619523132 bothSUCCESS at17:12:05Z/17:11:32Z, including typecheck and unit tests. Inspected43619604819 logs397files/4444testsPASS,79.96s. No duplicate broad local run.
- Local logs `/tmp/bg019-focused-initial.log`, `/tmp/bg019-build.log`, `/tmp/bg019-build-final.log`, `/tmp/bg019-focused-final.log`, `/tmp/bg019-lint-final.log`, `/tmp/bg019-postgres-brief.log` (initial fixture failure), `/tmp/bg019-postgres-final.log`. No private live assets/customer/payloads/credentials used. Whole repo lint not repeated for unchanged unrelated baseline; no full-lint-green claim.

### Deviations

None in runtime scope. The initial reused fixture assumed compaction must drop an item; correction explicitly asserts the newly authorized all3-fit behavior without weakening old cases.

### Assumptions

Original distinct product IDs determine list policy, not category/customer intent. Two variants of one product retain complete details. Root owns merges/live deployment and genuine combined verification.

### Unresolved Issues

None within task. Genuine production postdeployment proof remains root-owned and unclaimed.

### Architectural Concerns

None; all new behavior is application-owned presentation, existing reusable mechanics remain published Shared6.0.1.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actualcode

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

Root genuine integratedverification
