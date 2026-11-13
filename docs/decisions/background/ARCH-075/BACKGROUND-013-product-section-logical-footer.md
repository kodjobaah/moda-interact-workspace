---
id: ARCH-075-BACKGROUND-013
architecture_id: ARCH-075
title: Place product before answer with one logical checkout footer
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-BACKGROUND-012
  - ARCH-075-SHARED-008
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Place product before answer with one logical checkout footer

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Render in-session AI/HUMAN recovery replies as branding, product section, answer and one canonical checkout footer per logical group.

## Context

User clarified separate product section means product photo before answer, and footer once per logical reply. Current consolidated main then photo reverses this desired order. Native outreach remains unchanged pending the separate native-format decision. BG012 must finish first; no implementation begins under current resource hold.

## Scope

Background common multipart composition, exact preparation/frozen validation and directly related tests, using accepted published Shared group-footer parser. Existing canonical logical body/receipts/authorization remain authoritative.

## Out of Scope

Native Meta template changes or extra freeform messages outside the session window; new roles/wirefields/schema; asset collage generation; empty-caption IMAGE contract; Admin authoring redesign; provider/billing/moderation weakening; live operations.

## Requirements

- Every NEW logical group has the authored shop logo/details/header divider first, selected verified product photo next, answer next and exact canonical checkout footer appended once last. Preserve authored content byte-for-byte; no global trusted-URL count, stripping, truncation or divider heuristics. Authored answer may already contain checkout URL; that is distinct from appended footer.
- Product caption fits existing1024-codepoint limit: HEADER branding only (verified logo when available, otherwise existing text); PRODUCT photo with full answer+canonical footer caption. Long product caption: HEADER branding; PRODUCT photo caption the existing verified product title; ANSWER full answer+footer. No invented marketing or lost image. Existing max3 parts/allowed roles suffice.
- Without a selected product: fitting complete branded main remains one HEADER; long content uses HEADER branding then ANSWER full answer+footer. If even authored header cannot fit logo caption, retain text header fallback; never truncate. Existing canonical body/size/control/security refusal remains.
- Reader accepts old frozen every-part-footer and new final-footer groups exactly, with unchanged receipt/application-key identity and media-origin/tenant checks. Require exact canonical decomposition and one appended footer boundary in host, not pure string heuristics. Existing frozen plans replay unchanged regardless of writer flag.
- Reader-first compatibility: reuse exact-true RECOVERY_BRANDED_MAIN_REPLY_ENABLED with no new env mechanism. ROOT MUST set FALSE in BOTH environments BEFORE this source main merge can deploy, verify safe OFF startup, then deploy new readers with legacy writer. Root verifies every actual old reader drained, then enables TRUE. If this operational precondition cannot be proven, STOP integration; do not silently reuse live TRUE against old readers. Preserve flag safe boolean evidence and legacy OFF byte behavior. No queue clearing or quota reset.
- Keep default human dispatch, AI flow, root/part delivery ordering, consent, moderation, control races, billing once/logical reply, UNKNOWN no resend, quote routing and repairs intact. Common logical moderation covers complete authored body independent of physical footer projection.
- Native initial/followup uses existing approved one-media-header template only. Do not send freeform product parts outside the customer window or claim one native card supports two independent images. Client Read-more behavior is uncontrolled; no visibility guarantee.
- No new generic telemetry. Root owns merges/deploy/actual Meta delivery and verifies exact physical order/footer boundaries after drain.

## Work Items

- [ ] Capture desired order/footer-placement RED using actual canonical authored receipts.
- [ ] Adopt exact accepted published Shared release and implement reader-compatible projection.
- [ ] Prove short/long/product/no-image fallbacks, authored embedded URL, legacy replay and exact guards.
- [ ] Run actual PG default HUMAN+AI ordering/control/billing/receipt regressions and required checks.
- [ ] Publish exact source/report with mandatory root OFF-before-merge gate.

## Interfaces / Contracts

Existing published RecoveryMultipartDeliveryPlan schemaVersion1/roles and canonical common receipt. SHARED-008 publication is authoritative; no sibling source/imports or local duplicate parser.

## Dependencies

ARCH-075-BACKGROUND-012 and ARCH-075-SHARED-008 must be Complete/Accepted and actually integrated/published before preparation. Pending; no implementation worktree or claim yet.

## Enables

Root guarded reader-first deployment and genuine in-session AI/HUMAN product-section proof. Native decisions and accurate Admin preview remain separately bounded.

## Acceptance Criteria

- [ ] New group exact header→product→answer→single appended canonical footer order, preserving authored repeated URL content.
- [ ] Short/long/no-product/no-logo fallback retains full content and verified image without new fields/roles.
- [ ] Legacy frozen plans, moderation/control/tenant/receipt/delivery/replay/billing guards remain compatible.
- [ ] Actual PG plus relevant full tests/build/scopedlint pass; no native outside-window freeform extension.
- [ ] Root OFF-before-source-merge and drain-before-TRUE gate explicitly recorded; no premature rollout claim.

## Validation

- [ ] RED/GREEN decomposition vectors including authored URL in answer, footer suffix, long Unicode captions and exact legacy manifests.
- [ ] Actual disposable PG/Redis/default human and AI ordered parts, delivery gates/replay/billing once/control races, negative authority/media/receipt cases.
- [ ] Relevant declared full tests/build/type/scopedlint, exact unchanged baseline disclosure, browser-safe published dependency and diff/privacy/isolation evidence.

## Stop Condition

Set review and publish exact mirrored source/report. No main merge, configuration toggle or live send. Root confirms OFF-before-merge precondition before final integration.

## Implementation Notes

Normal launcher dedicated sibling worktrees; you are not alone, preserve others. No new gateway env declaration is needed. Existing authored common footer final-token contract remains unchanged; transport grouping must not introduce a new universal URL-last rule beyond the current canonical receipt.

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

Root owns operational gate and native preference.

### Unresolved Issues

Shared publication, BG012 and live proof pending.

### Architectural Concerns

Return unexpected receipt/contract gaps.

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

No native or overall live completion claim.


## Supersession (user-approved composite design)

User explicitly selected a single-bubble composite image with original logo/product assets retained separately. The two-bubble group-footer approach is superseded without implementation, claim or publication. Preserve this definition as history. New composite contract/provenance/renderer tasks require separate bounded design; no automatic successor execution.
