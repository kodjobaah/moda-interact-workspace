---
id: ARCH-075-ADMIN-011
architecture_id: ARCH-075
title: Author website in saved common caption footer
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-14T14:06:20Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Author website in saved common caption footer

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Author website in saved common caption footer.

## Context

User requests compact one-bubble AI product lists and website in clickable caption footer instead of image header. Published6 reader currently hardcodes website/header and checkout placement business policy; correct ownership once, saved template remains source of truth. No live source/activation changes by agents.

## Scope

Move common-frame business validation into Admin owning app; Shared only structural parser/hash machinery. Require trusted shop.name/site and checkout identity counts and allowed variables; support saved header Shop/name/divider and checkout.available conditional containing website followed by canonical checkout URL last. Retain static footer empty if smallest existing app contract; do not add unsupported variables. Audit every requireCommonLayout/readSaved/eligibility/clone/translation/frozen-review/Meta projection/common activation path. Exact source/prepared/locale/profile hashes and locale equality preserved, no silent old source rewriting. Existing native projection can consume conditional website tokens; test provider preview matches submitted body. App admission remains failclosed for untrusted/duplicate/missing bindings. Preserve reviewed immutable audit reads. No live template edits, registrations or activation.

## Out of Scope

Unrelated refactors, arbitrary user-programmable layouts, new database/infrastructure, main merges/live operations. Preserve all others work.

## Requirements

Move common-frame business validation into Admin owning app; Shared only structural parser/hash machinery. Require trusted shop.name/site and checkout identity counts and allowed variables; support saved header Shop/name/divider and checkout.available conditional containing website followed by canonical checkout URL last. Retain static footer empty if smallest existing app contract; do not add unsupported variables. Audit every requireCommonLayout/readSaved/eligibility/clone/translation/frozen-review/Meta projection/common activation path. Exact source/prepared/locale/profile hashes and locale equality preserved, no silent old source rewriting. Existing native projection can consume conditional website tokens; test provider preview matches submitted body. App admission remains failclosed for untrusted/duplicate/missing bindings. Preserve reviewed immutable audit reads. No live template edits, registrations or activation.

## Work Items

- [x] Implement only defined owning capability.
- [x] Add meaningful affected behavior regressions.
- [ ] Record exact source and required checks.

## Interfaces / Contracts

Shared owns technical structure/hash/render safety; applications own trusted bindings/placement/operational authority. Existing Shared6 published source immutable. No duplicated shared codec.

## Dependencies

ARCH-075-SHARED-015

## Enables

None; dependent promotions architect-owned.

## Acceptance Criteria

- [ ] Defined capability and owning-policy boundaries satisfied.
- [ ] Hash/identity/tenant/receipt/permit and mandatory content integrity retained.
- [ ] Required checks and exact immutable reports complete; no live/merge actions.

## Validation

Focused authoring/preview/translation/common activation tests, persisted meaningful common workflow if changed, types/scopedlint/build/browser graph/exact remote check. Local exact accepted Shared pack consumer tests may run before publication; final registry lock/npmci/remote gates required after actual publication.

## Stop Condition

After required work/checks publish matching source and parent report, set review and STOP. Do not continue dependent work.

## Implementation Notes

Normal moda-task canonical sibling isolation/claim required. You are not alone; do not revert others. Pending consumer tasks may perform preparatory source work only after explicit architect Ready amendment; final acceptance requires accepted published dependency. No unpublished sibling imports or fabricated registry lock.

## Preparatory execution and final release gate

Root authorizes concurrent owning source preparation using unchanged public reader signature. No unpublished sibling imports or fabricated registry lock. Shared014 must be accepted and its exact tested pack used for affected consumer validation before requesting publication approval. Final review/acceptance requires actual approved Shared015 publication, real registry dependency/lock/npmci and exact remote checks. Task Ready permits source preparation, not readiness/deployment claims. Desired saved frame puts website inside existing checkout.available conditional before canonical checkout URL; staticfooter empty can stay app policy. No generic checkout contextual-rule widening needed.

## Completion Report

### Status

In Progress — concrete tested source checkpoint. Final accepted artifact and actual approved registry release adoption remain mandatory before review; no readiness/live claim.

### Files Changed

- `authoring/common-layout-policy.ts`, `common-layout.ts`, `validation.ts`, `preview.ts`: Admin trusted-binding/placement admission around the existing Shared technical reader/projection.
- Existing `wrapper-structure-editor.tsx` and `common-layout-selector.tsx`: discoverable dynamic website/checkout footer, no ignored static footer.
- New footer-policy/preview/UI regression suite, affected authoring/compilation/wrapper fixtures and existing disposable common-layout PostgreSQL workflow.

### Work Completed

Source `ae8033f914f3f88237f570a0d3ed51679ce9b255` pushed, draft Admin PR [100](https://github.com/kodjobaah/moda-interact-admin/pull/100). One app-owned policy enforces exactly one trusted shop.name in header, one shop.websiteUrl in header or checkout conditional, response-only body, semantically empty static footer, one checkout.available conditional and one canonical checkout.url alone on its final line. AI-only productImage is rejected for common references. Existing reviewed header website remains valid without rewriting or compatibility adapters; new authoring places it in the clickable caption footer.

`requireCommonLayout` invokes the policy after Shared structural/hash parsing, so readSaved/assertSaved, selectors, native Meta projection, reconstruction and activation inherit it. SHARED compiler/save/review/eligibility and direct common preview also invoke the same policy. Frozen audit verification preserves exact saved bytes; new admission remains strict. Existing source/prepared/profile hashing and locale identity equality are unchanged. Static footer content is not silently omitted: meaningful content is refused with a footer issue; the editor retains its correction path. Empty static footer uses the complete conditional tokens in native BODY and AI/human caption.

UI labels Website and checkout footer / Dynamic footer show where both links belong; a deliberate Add button inserts trusted website then final checkout URL. Existing nonempty static content remains editable for correction. Generic AI/HUMAN branded wrapper tests retain their broader supported fields and audit/CAS/authorization assertions; actual SHARED tests use valid common frames rather than obsolete generic SHARED fixtures.

### Validation Results

- Actual published 6.0.0 RED reproduces the Shared reader rejecting the new conditional-website reference. Accepted Shared014 source `20aa60f0e9feb4c14ca909b7d7a68771e2b37bcf` archive SHA256 `6618d7c97e99c1e75ab67240ba940a5a5eade2a37a5661de000f25c5ade3a97a` hash-verified and installed no-save/no-lock; all **161 installed files** byte-match. Committed package/lock remain unchanged; this is not a registry-readiness claim.
- Common/native/activation/translation/profile focused run: **57 passed**. New footer policy, UI and affected authoring-component run after UX changes: **14 passed**. Additional affected authoring/wrapper admission regressions: **51 passed**. Counts are separate runs with overlap, not an aggregate unique total.
- New cases cover trusted binding counts/allowed placement, exact invalid prepared-reference rejection after rehash, six native scenario BODY/preview parity, AI/human caption ordering, translated variable relocation rejection, source/prepared/profile hashes, immutable read and unchanged old valid header bytes. Actual UI Add button preserves other content and saves correct bindings; nonempty static footer remains visible for correction.
- Existing disposable PostgreSQL runner: **2 passed**, including real old-header-to-new-footer clone, queued translations and all 20 locale reviews, selector/reference equality, coordinated activation and original/audit preservation. Disposable container removed; no hosted database used.
- Exact Shared015 **6.0.1 candidate** SHA256 `fd7b4a70d2a54da175556739074acdb5ee4487dc9c7e9c68a656717de3137aa2` independently compared with accepted 014: all **160 nonmetadata files identical**, only package version changed. No-save/no-lock installed candidate **161 files byte-identical**; affected footer/UI **5/5** and typecheck passed. No unchanged build/PostgreSQL/broad suite repeated for metadata only. This is an unpublished candidate proof, not publication or actual-registry readiness.
- Final types/scoped lint and production build after the dynamic-footer UX change passed (terminal build exit 0). Production browser graph across 71 JS files has no Node renderer/font-loader/frozen-verifier markers. Draft exact source ae8033f Vercel SUCCESS at 2026-11-14T14:28:22Z and Preview Comments SUCCESS at 14:28:23Z; this does not replace the final actual-registry adoption gate. No unaffected full-suite or PostgreSQL repeats.

### Deviations

None

### Assumptions

Root owns accepted dependency publication, main integration and normal saved-template/provider replacement/activation. No live edits, provider calls, database schema changes or independent configuration authority. Shared technical reader signature is unchanged; no sibling source imports or fabricated registry lock.

### Unresolved Issues

Accepted Shared014 artifact identity and exact Shared015 candidate proof are complete. Actual separately approved Shared015 publication and real registry dependency/lock/clean npm-ci adoption are mandatory before Ready for Review. Local UX build and draft exact-head checks passed; final actual-registry installation and exact-head checks still required.

### Architectural Concerns

Moving the website changes native BODY/binding order, so normal immutable native replacement/provider approval remains required; geometry-only comparisons from the preceding task do not imply this text-placement change is provider-byte-identical. No bypass is added. Static common footer remains semantically empty under app policy; the existing checkout.available footer carries both links without widening generic checkout-context grammar.

Isolation: primary root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-ADMIN-011`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-ADMIN-011`; both `task/ARCH-075-ADMIN-011`. Launcher verified main/task synchronization and recursive Database at `2e14f8668346dfc135aa12f8d1fbc94e05c12ce7`; implementation base `907fa32726565ddd0c80bf07273ef6af7418949d`. Attempt1 durable claim `9ce081670c9f400d9ffc3a84882c85caaa36cf4e` pushed. No shared/default or other task source changed.

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
