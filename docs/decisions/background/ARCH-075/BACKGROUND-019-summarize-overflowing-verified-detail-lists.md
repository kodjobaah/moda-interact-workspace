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
status: in_progress
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

- [ ] Add strictly eligible multi-product detail summary branch.
- [ ] Preserve complete verified fields/proof/pairs and exact footer budget.
- [ ] Add unit/actualservice/disposable lifecycle regressions.
- [ ] Record exactsource/isolation/check evidence.

## Interfaces / Contracts

Existing Shared6.0.1 verifiedfacts/renderer/receipt machinery unchanged; app owns list presentation policy. Existing immutable saved template owns caption footer/header.

## Dependencies

ARCH-075-BACKGROUND-015 Complete/integrated.

## Enables

Root genuine productlist/logo/clickablewebsite/checkout verification after combined source integration.

## Acceptance Criteria

- [ ] At least2 originally selected longdescription facts can yield honest brief fitting composite with exactretained proof.
- [ ] Single-originalproduct complete detail behavior unchanged; no-fit fallback intact.
- [ ] Actual savedwebsite+checkout/STOP caption<=1024 with one providerimage/rootbilling, no omittedpair metadata.
- [ ] Replay/UNKNOWN/currentpolicy/tenant/control guards unchanged.

## Validation

- [ ] Focused Unicode/locales/longdescriptions/singleproduct/no-fit/nonproduct/HUMAN/referral/proof tests.
- [ ] Actualservice/disposablePG oneimage/oneusage/retainedproof/context/UNKNOWN and bothfooterURLs.
- [ ] Types/build/scopedlint/exactCI/diffprivacy, no unrelated broadlocal repeats.

## Stop Condition

After required work/checks push source+matchingreport, review and STOP. Root owns merges/live.

## Implementation Notes

Normal moda-task dedicatedsiblings/claim. You are not alone; BG008 touches categoryguidance/hostserialization, do not edit those or revertothers. No fakeprovider credentials/private actualsource fixtures.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

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
