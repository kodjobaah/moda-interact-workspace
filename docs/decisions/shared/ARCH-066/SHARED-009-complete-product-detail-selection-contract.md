---
id: ARCH-066-SHARED-009
architecture_id: ARCH-066
title: Complete public product-detail selection contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: codex
claimed_at: 2026-11-08T18:52:11Z
attempt: 1
depends_on: ["ARCH-066-SHARED-005"]
enables: ["ARCH-066-SHARED-010"]
created: 2026-11-08
updated: 2026-11-08
---
# Complete public product-detail selection contract

## Architecture
ARCH-066; docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md and normative ARCH-066-consumer-contract.md sections A–C/E.

## Objective
Make the public model selection contract support the accepted generic product facts presentation.

## Context
Commerce Attempt1 proved immutable Shared5.7.0 omits productDetailSelections and PRODUCT_DETAILS from model-facing exports although verified presentation supports generic facts. User explicitly authorized owning Shared correction and subsequent consumer completion. Preserve accepted release history.

## Scope
Shared schemas, selection verifier/projections, runner response contracts, exports and directly related tests. Preserve public strict schema projection compatibility. No consumer source.

## Out of Scope
Package publication, version change, provider adapters, deployment or message delivery.

## Requirements
Add optional productDetailSelections max3 unique exact productId/variantId pairs and additive PRODUCT_DETAILS disposition to exported model-facing contract. Preserve existing productOptionSelections and PRODUCT_OPTIONS semantics. Both nonempty selections refuse INVALID_SELECTION using canonical verifier; no silent precedence. Align model/runner/public schema projection and inferred types with existing generic verifier/composer. Legacy envelopes remain valid; unknown fields remain rejected. Do not fork schemas or normalize arbitrary facts from model output. Bound identities using existing schemas. No new merchandise enums.

## Work Items
- [ ] Complete public schema, inferred types and exports/projections.
- [ ] Enforce exact-ID cardinality, duplicate and mixed selection refusal.
- [ ] Add legacy and generic selection regression fixtures.

## Interfaces / Contracts
@modainteract/moda-interact-shared/commerce and /commerce/presentation; accepted5.7.0 facts and options contracts. Consumer contract sections A–C/E controls.

## Dependencies
ARCH-066-SHARED-005 (Complete).

## Enables
ARCH-066-SHARED-010 publication; later Commerce001.

## Acceptance Criteria
- [ ] Public JS/declarations accept valid detail selection and PRODUCT_DETAILS.
- [ ] Duplicate/mixed/oversized/wrong identity selection refuses deterministically; legacy options unchanged.
- [ ] Default strict schema projections and runner responses can carry new field without unknown-key widening.
- [ ] Focused regression checks and package validators pass.

## Validation
- [ ] Inspect declared package scripts; run typecheck, build, focused schema/selection/runner/presentation tests and existing commerce entrypoint/presentation validators.
- [ ] Pack public-import smoke proves model-facing selection plus verified facts composition; inspect diff check.

## Stop Condition
Push implementation and task report; set review and stop for architect acceptance. No publication here.

## Implementation Notes
Use canonical launcher isolation and preparation. Exact accepted5.7.0 ancestry must be preserved. No overwrite of immutable version. User authorizes this bounded correction and task/report pushes.

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
Pending
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending
### Follow-up
Separate publication008 after acceptance.
