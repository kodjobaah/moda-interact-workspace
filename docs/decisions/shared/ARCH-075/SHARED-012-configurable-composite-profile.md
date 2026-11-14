---
id: ARCH-075-SHARED-012
architecture_id: ARCH-075
title: Render trusted composite images from bounded runtime profiles
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-SHARED-011
enables:
  - ARCH-075-SHARED-013
  - ARCH-075-ADMIN-009
created: 2026-11-14
updated: 2026-11-14
---

# Render trusted composite images from bounded runtime profiles

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Accept a trusted immutable bounded layout profile so supported visual-value changes require configuration revisions rather than Shared publication.

## Context

User explicitly requests the architecture correction before merge/deployment. Published5.13.11 remains immutable. Existing approved visual order is logo/shop details/literal divider, optional product, actual answer+one checkout footer caption. The existing fixed-V1 implementation is preserved for replay, not silently rewritten.

## Scope

Additive browser-safe profile/provenance/output/plan schemas and hash helpers; Node configurable renderer/preparer; opt-in carrier reader delegating all legacy V1 branches exactly. Existing reusable rendering/safe fetch/R2/probe mechanics and bounded image proof remain owned here. No publication in this task.

## Out of Scope

Admin UI/database/environment selection, arbitrary CSS/drawlists/scripts/font URLs, native Meta template changes, live sends/configuration, consumer implementation or publication.

## Requirements

- Shared receives explicit trusted profile snapshot; it never chooses active policy, reads DB/env or owns visual defaults. Admin owns runtime values/revision; Background owns selection/freeze/final authority.
- Profile schemaVersion1 with fixed supported fontId DEJAVU_SANS_2_37 and named fields: canvasWidth,headerOnlyHeight,withProductHeight; logoLeft,logoTop,logoWidth,logoHeight; textLeft,textTop,textWidth,textHeight,fontSize,textLineSpacingPt; productLeft,productTop,productWidth,productHeight. No arbitrary objects of operations.
- Technical bounds: canvasWidth640..1600, headerOnlyHeight160..640, withProductHeight400..1840, logo width/height32..320, textWidth128..1600,textHeight32..640, productWidth128..1600,productHeight128..1200,fontSize24..96. Integers only. Coordinates nonnegative and <=1840; logo/text rectangles fit header; textLineSpacingPt0 or fontSize..2*fontSize; productTop>=headerOnlyHeight and product rectangle fits product canvas; withProductHeight>headerOnlyHeight; both outputs<=2000000pixels. Do NOT require logo-left-of-text or any visual placement order; supported bounded profiles may put logo above/centered with text below. Nonoverlap/readability belongs to owning Admin policy where appropriate. These are safety bounds, not visual defaults. Output dimensions derive from supplied profile and optional product, never fixed1125/300/900 literals in the new contract.
- Preserve literal header incl authored divider exactly once, contained uncropped original logo/product, fixed escaped text/fixedDPI72/white/JPEG/leftalignment/no-autofit semantics. Unsupported glyph/overflow/deadline returns existing typed fallback outcome; no silent truncation/replacement.
- Add explicit opt-in V2 provenance/plan/prepared output with full validated profile snapshot+canonical digest and source/runtime/font/output/caption/logical-body proofs. Separate content-addressed v2 namespace. Old V1 schemas/parsers/digests/render outputs remain unchanged; new reader delegates old branches byte-for-byte; old .11 rejects V2 safely.
- Reuse existing immutable upload/probe/AbortSignal/one original media deadline. No duplicate generic crypto/fetch/R2 mechanism. Runtime/font identity binds profile and actual library environment, no cross-platform byte-identity claim. Preserve old manifest/V1 hash computation; V2 resource identity covers the same bundled font/license/cmap without embedded size/geometry, separately bound to the full profile digest.
- Default-looking profile fixture is consumer-owned test input reproducing accepted visual geometry. Prove two materially different valid profiles (left logo, then top/centered logo with text below plus different font size/spacing/product gap) render correctly through the SAME installed package WITHOUT changing package code, and immutable profile tamper cannot pass trusted validation.
- No secrets/shop assets/customer URLs in public fixtures/package. Root alone merges/publishes/live tests.

## Work Items

- [ ] Add strict profile/provenance/parser/carrier APIs and legacy compatibility vectors.
- [ ] Add parameter-driven Node renderer/preparer using existing mechanics.
- [ ] Validate two profile revisions, actual packed runtime/fontless Alpine output and safety failures.
- [ ] Push mirrored implementation/report and stop for review.

## Interfaces / Contracts

New additive V2 APIs under existing commerce/presentation and Node subpaths. Profile snapshot/hash must be independently supplied by host authority, not self-attested by stored plan. Existing .11 APIs remain unchanged. Document exact exports for Admin009 and BG014 correction before consumers execute.

## Dependencies

ARCH-075-SHARED-011 Complete and integrated before launcher execution.

## Enables

Shared013 release-only preparation/publication; Admin009 bounded existing-policy editor; BG014 next-attempt adoption after accepted contract. Public release requires separate explicit exact-archive approval.

## Acceptance Criteria

- [ ] Runtime profile changes within bounds alter rendering without Shared code/version changes.
- [ ] V1 replay bytes/digests remain compatible and V2 trusted source/profile/output/caption binding fails closed.
- [ ] Actual renderer respects approved semantic order, no private pixels and complete text fallback.
- [ ] Required checks and canonical isolation evidence recorded; no publication/live mutation.

## Validation

- [ ] Focused profile bounds/dimensions/hash/tamper/legacy/transport vectors including left and top/centered arrangements.
- [ ] Actual two-profile rendering including bundled font/overflow/timeout/R2/probe; packed fontless Alpine and browser-safe imports.
- [ ] Declared full tests/type/build and package asset/secret/diff checks appropriate to changed code; no invented lint script.

## Stop Condition

After required scope/checks, push both task branches, set review, return Completion Report and STOP. No enabled-task work/publication/main merge.

## Implementation Notes

Normal launcher dedicated sibling worktrees. You are not alone; preserve all others. Keep reusable mechanics in Shared and product/active-policy authority in owners. Return missing contract gaps before widening.

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

Root owns integration, publication approval and rollout.

### Unresolved Issues

Dependency integration pending.

### Architectural Concerns

Return concrete gaps before widening.

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

No architecture/live completion claim.
