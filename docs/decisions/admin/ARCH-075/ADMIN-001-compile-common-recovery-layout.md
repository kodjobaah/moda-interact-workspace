---
id: ARCH-075-ADMIN-001
architecture_id: ARCH-075
title: Compile immutable common recovery layout into replacement templates
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-SHARED-004
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Compile immutable common recovery layout into replacement templates

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Compile immutable common recovery layout into replacement templates.

## Context

The user explicitly requires all Meta templates, AI replies and HUMAN messages to share one shop header and checkout footer, with product images separate. Existing Admin-owned SHARED wrapper definition/slot is the common immutable content authority; family-specific body/offer/opt-out content stays intact. No duplicate hardcoded frame builders.

## Scope

Admin-owned immutable common layout selection/reference, new replacement Meta clone compilation, translation reconstruction and visible cross-family preview only; existing authoring/localeAst JSON, compiler and SHARED wrapper definition/slot. Adopt published Shared website/common-reference contract. Do not activate live pointers or submit registrations in this task.

## Out of Scope

Other repositories, new database tables/settings, provider permissions, live registrations/activation, source merges, unapproved publication, changing billing/cap semantics, arbitrary source refactors, automatic mutation of approved templates. Background engine001 remains on published5.13.8 and producer-disabled.

## Requirements

Select exact saved immutable SHARED wrapper definition+locale and freeze canonical Shared commonRef in NEW Meta authoring.commonLayout JSON; include it in immutable source hashing. Re-read saved definition/locale, verify sourceHash/contentHash/locale/family/audience/status and use public Shared reference parser with existing injected digest. Client-provided projection alone is not authority. No new database table/setting. Common layout is body-only slot with authoritative editable header and checkout conditional/footer; no duplicated hardcoded common frame.

The ONE existing compiler projects saved common header tokens into Meta BODY prefix, preserves authored family-specific body and original opt-out footer text, then appends common checkout conditional as actual final BODY suffix; native Meta FOOTER is empty for new clones. Logo uses genuine verified LOGO/SQUARE IMAGE HEADER; text shop identity is BODY content, not simultaneous native text header. Preserve original authoring body/footer bytes and existing INITIAL contextual Reply validation; compiler validates final projected1024 length, variable count, header/button limits and complete semantic bindings after insertion. Do not truncate, drop opt-out, regex-delete arbitrary inline checkout or fabricate a registration. Existing duplicates require explicit review and clear preview. Impossible/provider-ineligible shape fails with actionable bounded error.

Immutable approved snapshots remain readable/unchanged. Clone revisions rather than mutate published definitions; reconstructed target locales preserve matching localized commonRef and variable bindings. Body translations remain family-specific, common header/footer translations are authored/reviewed once in common revision. Preview should say Common shop header and Common checkout footer, not implementation jargon, and demonstrate custom common text changes across Meta/AI/HUMAN without copy-paste. Default name/site/divider/check-out content is not a second hardcoded builder. Return actual provider/API/schema/activation gaps; no unreviewed template-part transport or outside-window freeform send.

### Reviewed baseline drafts and progress truth

Root reviewed six body-only CHECKOUT baseline drafts in `/tmp/moda-six-recovery-scenarios.md` and `.json` as reviewable inputs, not approved registrations. Validate them through the repository native test runner before any seeding; preserve verified offer.description/offer.code, no fixed percentage/deadline, initial contextual Reply tail and opt-out. Source inventory translation-run/item results may be complete despite legacy definition status TRANSLATION_QUEUED: show actual run/item review/approval/assignment counts, do not rewrite historical status merely to make badges agree. External registration still requires root review of concrete final compiled copy/limits and required20 locales.

### Scenario catalogue coverage

Confirmed supported core matrix: INITIAL/FOLLOW_UP × NO_OFFER/CODE_OFFER/AUTOMATIC_OFFER = six scenarios. CHECKOUT/ALTERNATIVE_PRODUCT are an additional target axis inside existing offered classes, never new discount promises. Inventory actual target eligibility from existing code and definitions. HUMAN outside-window uses existing approved RECOVERY_FOLLOW_UP_TEMPLATE catalogue; in-window HUMAN_TEXT uses the dynamic common frame. AI responses, terminal limits and service outcomes are dynamic content, not invented Meta purposes/HANDOFF enums. Two NO_OFFER published definitions cover two scenarios; duplicate queued NO_OFFER versions add no scenario coverage. Present clear scenario labels distinguishing approved business-initiated initial/follow-up recovery templates (including any supported outside-window HUMAN path) from dynamic AI product answers and HUMAN freeform messages. Prepare reviewable replacement/default seed drafts only for supported scenarios, with the one common layout and family-specific copy. Preserve existing offer eligibility/promises; no invented discount, policy, template family or transport. Missing supported scenario coverage must be explicit, not masked by duplicate queued versions. Preserve historical/queued definitions as immutable/cloneable records; no automatic deletion, retirement, registration or activation. Root reviews concrete copy/coverage before external registration. Golden previews and tests verify labels/coverage and common frame parity.

## Work Items

- [ ] Complete assigned bounded capability only.
- [ ] Prove compatibility and meaningful negative/failure behavior.
- [ ] Submit mirrored branch/report and stop.

## Interfaces / Contracts

Common content authority: selected immutable Admin SHARED wrapper revision and locale projection. Shared owns canonical semantic key/wrapper validation; Admin owns authoring/compiler/reference/activation; Background owns tenant-derived values, frozen rendering, sending and current fences. Existing template registration hashes remain authority for provider components.

## Dependencies

ARCH-075-SHARED-004

## Enables

Only explicitly promoted dependent tasks after acceptance.

## Acceptance Criteria

- [ ] One common content source is used without duplicated formatting or unauthorized semantic widening.
- [ ] Old stored projections/registrations remain readable and immutable; new fields do not grant tenant/provider authority.
- [ ] Assigned validation and isolated mirrored synchronization evidence are complete.

## Validation

- [ ] Golden custom-header/footer projections and Meta/dynamic parity with real public parser/renderer; legacy records unaffected.
- [ ] Clone/translation/source-hash/tamper/stale-ref/locale mismatch and final composed-limit/opt-out preservation regressions.
- [ ] Existing declared relevant tests/types/lint/build plus real PostgreSQL immutable-source fixture where applicable; exact-head CI and privacy checks.

## Stop Condition

After required work and validation, submit review and STOP. No enabled-task execution, merge, live mutation or unapproved public release.

## Implementation Notes

You are not alone; preserve other changes. Canonical prepared packet is startup/isolation authority. Report actual cross-owner gaps rather than inventing a setting/schema or weakening strict validation.

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

None beyond approved contracts.

### Unresolved Issues

None currently; return concrete gaps.

### Architectural Concerns

Preserve one common content authority and immutable prior registrations.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual source review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
