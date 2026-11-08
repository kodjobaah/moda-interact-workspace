---
id: ARCH-066-SHARED-011
architecture_id: ARCH-066
title: Correct frozen outreach brand binding compatibility
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-SHARED-010"]
enables: ["ARCH-066-SHARED-012"]
created: 2026-11-08
updated: 2026-11-08
---
# Correct frozen outreach brand binding compatibility

## Architecture
ARCH-066; docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md and ARCH-066-initial-outreach-contract.md. Coordinator moda_architect.

## Objective
Preserve the existing supported frozen initial-template brand binding semantics through the published Shared outreach renderer.
## Context
BACKGROUND002 adoption exposed a required compatibility gap in immutable5.8.0: SemanticKeySchema allows shopBrand.logoAltText/logoWidth/logoHeight/squareLogoAltText, but PreparedVariableResolver.resolve has no corresponding cases and always refuses valid values. Background's existing RecoveryVariableResolver supports saved text/dimensions, mandatory-brand refusal, and authorized ready media URLs in body parameters. Generic shop.name fallback must not silently satisfy mandatory shopBrand.brandName.
## Scope
Shared outreach strict render input/data projection, resolver/bindings and focused compatibility fixtures only. Inspect actual5.8.0 exports/source and Background read-only evidence; do not import Background. Add the smallest bounded explicit data inputs for saved brand text/dimensions and ready same-shop media by role needed to preserve existing semantics. Shared retains deterministic semantic-key/cap validation/rendering, hosts retain database/media resolution and tenant authorization. Do not accept arbitrary callbacks, raw customer records, unvalidated dictionaries or original image URLs.
## Out of Scope
Standalone production identity,007/008/MCP002 resurrection, provider calls/media generation, producer/consumer edits, package publication, deployment, main integration and unrelated evaluator redesign.
## Requirements
Preserve all existing supported semantic keys and exact caps, required-vs-fallback distinction, positive safe bounded dimensions, prepared body/header/button fields and binding fingerprints. Missing/wrong-type/unsafe mandatory brand values fail closed; same-shop READY R2 media only, no original URL fallback. Valid body media bindings must work without an IMAGE header. Legacy ordinary shop.name/category inputs and no-brand templates retain behavior; no merchandise-specific keys. Preserve evaluator contracts, public009 product-details correction and all existing exports. Inspect invalid-URL validation throwing observed during Background fixtures; if directly reproduced in public renderer/schema, return typed INVALID_REQUEST instead of throwing for malformed input, with focused regression; do not widen trust.
## Work Items
- [ ] Reproduce valid alt/dimension/body-media incompatibility and mandatory-brand distinction using exact published5.8.0 entrypoint.
- [ ] Define minimal strict optional prepared brand/media data with explicit host/Shared boundaries and preserve prior no-brand input compatibility.
- [ ] Implement deterministic supported bindings and fail-closed validation; no service-local imports or side effects.
- [ ] Add positive/negative compatibility goldens and exact full text/parameter/provenance checks.
## Interfaces / Contracts
@modainteract/moda-interact-shared/commerce/outreach; InitialOutreachRenderInputSchema, renderInitialOutreachPreview, existing frozen SemanticKeySchema and strict ready-media contract. Extend documented data contract explicitly; do not pretend existing5.8 supports new inputs.
## Dependencies
ARCH-066-SHARED-010 Complete, immutable5.8.0 source/exports. No dependency on blocked Background or terminal system tests.
## Enables
ARCH-066-SHARED-012; consumer correction remains on original BACKGROUND002 after corrected publication.
## Acceptance Criteria
- [ ] Valid saved logoAltText, squareLogoAltText, logoWidth/logoHeight bindings render exact expected parameters in INITIAL without copying Background algorithms.
- [ ] Mandatory saved brandName cannot be satisfied by generic shop.name fallback; missing/invalid values refuse.
- [ ] Authorized READY same-shop logo/square/cover URL body bindings preserve valid behavior; missing/wrong-shop/wrong-role/raw-original media refuses.
- [ ] Existing nonbrand inputs, image/TEXT fallback, approved registration/binding integrity, provider parameter encoding and full-body bounds remain compatible.
- [ ] Public runtime and declaration imports include corrected strict inputs; malformed input never weakens validation or leaks secrets.
## Validation
- [ ] Focused outreach renderer/schema compatibility tests, including positive existing Background binding cases and negative tenant/type/value cases.
- [ ] Existing outreach evaluator/render regressions, typecheck and production build per repository scripts.
- [ ] Package public JS/declaration import smoke; record exact commands/results. No live calls.
## Implementation Notes
Exact initial evidence: Shared src/commerce/outreach/variables.ts switch afterbrandName/3URLs falls through; template-contracts.ts includes the4unimplemented fields. Background src/services/recovery-template-preparation/recovery-template-brand.ts supports saved type/cap semantics. Reuse approved Shared logger only if logging changes. If more contract work is required, return precise gap rather than expand scope. Use canonical launcher dedicated worktrees when execution is explicitly invoked; definition only now.
## Completion Report
### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
Not run; definition only.
### Deviations
None
### Assumptions
Hosts supply authorized saved data; Shared verifies deterministic structure/caps and tenant/media binding.
### Unresolved Issues
Published5.8.0 cannot preserve named valid bindings; BACKGROUND002 cannot be Accepted until corrected artifact is available and its same-task checks pass.
### Architectural Concerns
No standalone scope or live send authorization follows from rendering.
## Architect Review
### Review Status
Pending
### Review Notes
Definition authored after actual local/remote/canonical ID scan;011/012 unused, existing007–010 identities/claims preserved.
### Reviewed Files
Shared outreach variables/template contracts and Background brand/preparer tests read-only.
### Validation Reviewed
Repository implementation validation pending.
### Architecture Conformance
Bounded Shared-owned compatibility correction, separate publication and consumer adoption.
### Follow-up
Stop after review submission. Do not publish or implement consumers.
