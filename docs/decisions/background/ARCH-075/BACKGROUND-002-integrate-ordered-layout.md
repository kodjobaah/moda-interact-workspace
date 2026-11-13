---
id: ARCH-075-BACKGROUND-002
architecture_id: ARCH-075
title: Compose and integrate ordered recovery logo and product replies
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-BACKGROUND-001
  - ARCH-075-SHARED-004
  - ARCH-075-ADMIN-001
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Compose and integrate ordered recovery logo and product replies

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect. Read all frozen contract constants and lifecycle decisions before implementation.

## Objective

Compose and integrate ordered recovery logo and product replies.

## Context

User requests logo/shop details before a distinct product image and checkout footer. Existing single-provider-id response cannot safely loop multiple sends. This task owns one bounded prerequisite capability; preserve completed prior behavior.

## Scope

Server-known header/footer composition for AI/HUMAN/eligible notices, wrapper/provenance preparation and processor/dispatcher integration with accepted engine, end-to-end tests/docs.

## Out of Scope

Other repositories/tasks, source main merges/deployment, production sends/replays/resets, billing/usage/cap changes, provider credentials/permissions, unsupported exactly-once assumptions, unbounded fanout/retries, unrelated refactors. Return actual cross-owner gaps.

## Requirements

Build canonical2/3part layout and singleTEXT fallback; eachpart exactcheckoutfooter. Preserve author middle bytes via known receipts/boundaries, never heuristic regex stripping. Actual verified first selected product pair/image only; brandheaderfromcurrentREADYlogo, no cover substitute. Header/detail image precedes separate product; answer fits productcaption then2parts, otherwise finalANSWER third. Missinglogo verifiedtextheader/fullanswer and missingproduct image safeTEXT; no suppressing otherwise legitimate response. Freeze original body/manifest/moderation/authority before firstsend; no postpermit edits/ownership recapture. AIoriginalversion, HUMANcommand/control/lease with newinboundpolicy unchanged, STOP/security/templates oldexact compatibility. One logical reservation/usage/cap, max3physical, no new merchantUIfeature. Handle returned partial/unknown truthfully and preserve inter-response conversation order.

### Common content authority amendment

Consume published5.13.9 commonRef/website binding and Admin001 immutable common revision, not a new hardcoded header/footer builder. Existing RecoveryShopHeaderReceiptv1 helpers enforce a fixed prefix and must remain legacy-only. Introduce additive local receiptv2 (existing JSON only) binding canonical commonRef, actual rendered header/footer and trusted split boundaries from the existing renderer, tenant/name/website/checkout facts and original source/control; final current-slot/source/locale/policy checks preserve original evidence. Frozen v1 replay stays byte-exact, no automatic upgrade. Eliminate fixed common prefix decoration for newly framed replies; audience/family-specific content remains body only. Custom common header/footer edits must visibly match Meta/AI/HUMAN goldens, proving one editable source rather than equal default strings. No regex stripping arbitrary authored HUMAN bytes. Update multipart frozen parser/derivation to recognize new receipt only after strict validation, preserve old plan/digest semantics.

Background website resolvers derive canonical saved tenant domain with existing HTTPS/origin policy. Meta registration preparation validates frozen commonRef against selected common revision; no mutation/recompile of provider snapshots at send. New Meta outreach still uses approved native template transport outside window, never freeform product tail. Product photos remain separate only under valid transport/window and frozen part provenance. Runtime consumer deployment precedes Admin002 activation; return any global-slot/per-shop assignment race gap.

### Logical admission and staged producer rules

Reuse the accepted engine reader/frozen source/part helpers and published validator; do not invent a second lifecycle, content renderer or receipt decoder. Use deterministic HUMAN root identity from commandId. Existing HUMAN Redis anti-spam/rate admission remains ONCE per logical command, not once per part; preserve original billing/usage/cap policy. No separate Meta HTTP rate limiter exists to reuse, so do not claim or invent one; transport is bounded by max3 parts and existing provider behavior. Initial HUMAN claim duration must cover its immutable logical delivery deadline using the existing bounded claim API (up to300seconds); do not extend/reacquire admitted authority after freeze. Existing default60seconds is shorter than default120second group deadline and is insufficient for initial prepermit waiting.

Production generation remains off until root verifies accepted compatible-engine Live and old-reader drain in BOTH test/production. Source can be implemented once dependencies are accepted, but producer merge/deployment activation is root-gated on that runtime evidence. Preserve actual AGENT/HUMAN sender semantics; do not retag AUTOMATION marketing/notices to bypass their existing final policy. If any eligible notice truly uses an unsupported actor, return the concrete gap rather than widen transport authorization.

## Work Items

- [ ] Implement only assigned capability and document compatibility.
- [ ] Complete meaningful required checks and regression/negative evidence.
- [ ] Publish mirrored branch/report and return review, then stop.

## Interfaces / Contracts

Use canonical ARCH075 frozen decisions. Shared owns ordered schema/digest and existing perpart media exports; Database owns durable child/status identity; Background owns provider/current authorization and logical aggregation. Never duplicate validators or fabricate product/provider identity.

## Dependencies

ARCH-075-BACKGROUND-001
ARCH-075-SHARED-004
ARCH-075-ADMIN-001

## Enables

Only dependent tasks after architect acceptance; never begin them implicitly.

## Acceptance Criteria

- [ ] Assigned bounded capability and frozen contract behavior satisfied.
- [ ] Legacy reads/records remain compatible; no unauthorized cross-owner/billing/security change.
- [ ] Durable/contract identity and fault cases satisfy required checks without silent fallback.
- [ ] Canonical dedicated mirrored worktree, synchronization and recursive evidence recorded; no private proof committed.

## Validation

- [ ] Actual AI Free/normal admission→full composition→engine→mockMeta2/3 ordered calls; HUMAN/no-product/notices + missingmedia/longcaption/author bytes and everyfooter.
- [ ] Real PG original receipts/moderation/fullmanifest/partial/unknown/takeover/restart plus existing single-send/caption read-model tests.
- [ ] Types/scoped lint/build/exact-head CI and no real production sends.
- [ ] Diff/privacy hygiene and report actual results, no production sends or secrets.

## Stop Condition

After required work and validation, set review, submit Completion Report and STOP. No main merge/deploy or enabled task execution.

## Implementation Notes

Accepted compatible engine merged at `02e624478fbaf4f4d2c755bfa88e86d4a1a4154c`; launcher implementation must incorporate that main source. Admin001 accepted source merged `73831bb661731bc6d7dd478475ea7acad1ffc4dd`, public Shared5.13.9 actual bytes verified. Root retains producer merge/deployment gate until engine Live/healthy and predecessor drain proof in BOTH environments; implementation may proceed in isolation while that operational proof is pending.

You are not alone. Preserve others' edits and canonical prepared isolation. Root owns final merges/deployment. Architecture constants resolve inter-agent assumptions; report genuine gaps before expanding scope.

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

None beyond canonical contracts.

### Unresolved Issues

None currently; report concrete gaps.

### Architectural Concerns

No weakening of tenant, immutable outcome or uncertain-provider safety.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
