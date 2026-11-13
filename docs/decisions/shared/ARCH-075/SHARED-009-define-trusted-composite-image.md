---
id: ARCH-075-SHARED-009
architecture_id: ARCH-075
title: Define trusted composite recovery image contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-SHARED-006
enables: 
  - ARCH-075-SHARED-010
created: 2026-11-13
updated: 2026-11-13
---

# Define trusted composite recovery image contract

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Define one additive trusted composite image carrier that binds rendered shop branding and optional verified product to the real answer/footer caption.

## Context

User approved single bubble: original logo and product remain separate assets; a deterministic derived bitmap shows logo beside shop details, divider then optional product, while answer and one canonical checkout footer stay real caption text. Supersedes unexecuted two-bubble SHARED007/008/BG013. Native template changes remain excluded.

## Scope

Browser-safe composite provenance/prepared-image/plan schema and digest exports plus direct contract tests. Existing runtime primitives are reused; no image renderer implementation in this task.

## Out of Scope

Renderer/fonts/network/R2 execution, package version/publication, service consumer, native template AST/registration, schema/database or new generic framework.

## Requirements

- Add distinct COMPOSITE_IMAGE kind to the appropriate media carrier; do not pretend output is logo BRAND_IMAGE or product IMAGE. Keep existing TEXT/IMAGE/BRAND_IMAGE/frozen multipart bytes/digests and validators unchanged.
- Provenance binds exact trusted LOGO/SQUARE_LOGO source origin/generation/fingerprint plus actual input byte hash, optional verified product shop/platform/product/variant+actual byte hash, same tenant, canonical rendered header text/common reference hash, layout/renderer/font asset identity, strict output dimensions/MIME/size/SHA and trusted publicOrigin/objectKey/publicUrl identity. Product absence is explicit, supporting no-product AI/HUMAN.
- Caption is complete answer+canonical footer, <=1024 Unicode codepoints; no truncation/global URL count. Full logical header+answer+footer remains separately authoritative for moderation/history/receipt. Host must cryptographically bind exact caption/bitmap header to original canonical boundaries before send, not infer equivalence from text inclusion.
- New composite key namespace binds tenant hash/render identity/output hash; output URL equals exact trusted origin/key and key suffix matches content SHA. No model URLs or secret/customer/checkout/answer content in reusable bitmap/cache identity. Define fixed bounded geometry/layout version in coordination with Node renderer; existing1125x600 output assumptions must not silently validate taller composite bytes.
- Browser export contains no Node/Sharp/Prisma/config reads. Runtime authorization remains Background-owned, current source provenance reattested before send. No fields/roles/version changes elsewhere unless concrete compatibility need is returned.
- Demonstrate current5.13.10 rejects new kind; new reader accepts exact old plans. No writer activation/publication. Malformed/mixed-tenant/forged origin/hash/key/caption/control/oversize cases fail closed.

## Work Items

- [ ] Define minimal distinct provenance and plan schema/digest.
- [ ] Prove optional-product, same-tenant and exact source/output identities.
- [ ] Preserve legacy contract/digest and browser safety; publish source/report.

## Interfaces / Contracts

Published commerce/presentation media plan exports and existing brand/product provenance schemas. New composite is additive schemaVersion1 carrier; no new multipart role needed unless proven.

## Dependencies

ARCH-075-SHARED-006 Complete and published5.13.10. Root released resource hold after BG012 final checks; this Ready task may prepare normally. No implementation worktree was created at definition time.

## Enables

ARCH-075-SHARED-010 only after source acceptance/integration.

## Acceptance Criteria

- [ ] Distinct composite with trusted same-tenant dual/optional-product provenance and exact public output identity.
- [ ] Caption/logical-body separation explicit; no unsafe URL/string inference or source relabel.
- [ ] Legacy vectors/digests unchanged; browser-safe packed exports and negative guards pass.

## Validation

- [ ] Focused schema/digest RED/GREEN optional-product, forgery/control/Unicode/caption/tenant/output cases.
- [ ] Declared relevant/full tests/type/build/available scoped lint and packed/browser safety checks.
- [ ] Diff/privacy, exact isolated source/report and compatibility evidence.

## Stop Condition

Publish exact mirrored source/report, set review and return architect. No main merge, live mutation, enabled consumer or npm publication without release-specific authorization.

## Implementation Notes

Normal launcher dedicated sibling worktrees. You are not alone; preserve others and primary. Original approved mock is schematic only: small contained logo alongside shop details, divider, product beneath. Root owns operational/visual review and integration; no live sends.

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

Root owns final integration and live authorization.

### Unresolved Issues

Publication and consumer/live proof remain gated.

### Architectural Concerns

Return gaps before widening.

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

No architectural/live completion claim.
