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
status: review
priority: 20
executor: null
claimed_at: null
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
- [x] Complete public schema, inferred types and exports/projections.
- [x] Enforce exact-ID cardinality, duplicate and mixed selection refusal.
- [x] Add legacy and generic selection regression fixtures.

## Interfaces / Contracts
@modainteract/moda-interact-shared/commerce and /commerce/presentation; accepted5.7.0 facts and options contracts. Consumer contract sections A–C/E controls.

## Dependencies
ARCH-066-SHARED-005 (Complete).

## Enables
ARCH-066-SHARED-010 publication; later Commerce001.

## Acceptance Criteria
- [x] Public JS/declarations accept valid detail selection and PRODUCT_DETAILS.
- [x] Duplicate/mixed/oversized/wrong identity selection refuses deterministically; legacy options unchanged.
- [x] Default strict schema projections and runner responses can carry new field without unknown-key widening.
- [x] Focused regression checks and package validators pass.

## Validation
- [x] Inspect declared package scripts; run typecheck, build, focused schema/selection/runner/presentation tests and existing commerce entrypoint/presentation validators.
- [x] Pack public-import smoke proves model-facing selection plus verified facts composition; inspect diff check.

## Stop Condition
Push implementation and task report; set review and stop for architect acceptance. No publication here.

## Implementation Notes
Use canonical launcher isolation and preparation. Exact accepted5.7.0 ancestry must be preserved. No overwrite of immutable version. User authorizes this bounded correction and task/report pushes.

## Completion Report
### Status
Ready for Review — Attempt1. No publication or version change.
### Files Changed
src/commerce/schemas.ts; src/commerce/selection.ts; src/commerce/answer-presentation-selection.test.ts; scripts/validate-commerce-entrypoints.mjs.
### Work Completed
Added PRODUCT_DETAILS to public response disposition and optional strict productDetailSelections (max3 exact bounded identities, duplicate pairs rejected). Existing option selection semantics unchanged. Public inferred types and wildcard exports include new field and verifyCommerceAnswerPresentationSelection. The pure canonical verifier rejects both nonempty option/detail selections as INVALID_SELECTION; callers must use it before fresh host verification. Schema remains plain strictObject with shape projection compatibility. Host grants/currentness/budgets remain consumer-owned, not granted by model selection. Existing verifyCommerceProductFacts and composer remain canonical generic facts path.
### Validation Results
Declared scripts inspected. Typecheck passed; initial 95 focused schema/response/selection/runner/presentation checks passed; added JSON authoring projection regression passed (4 selection tests total). Production ESM/declaration build and commerce entrypoint/presentation Node/browser validators passed. npm pack --ignore-scripts and extracted-package public entrypoint smoke passed using locked dependency linkage; local tarball is validation only, not immutable published5.7.0. JSON projection uses z.toJSONSchema io output/unrepresentable any (Commerce projector engine), verifies strict identity fields/maxItems/enum, no arbitrary fields. Test type narrowing corrected before final typecheck. No lint script declared; not represented as passed. Diff check passed.
### Deviations
None. Canonical verifier owns mixed-selection refusal because schema shape consumers require composable strict fields; runtime uniqueness remains in detail array schema and canonical verifier. JSON schema cannot express custom uniqueness of pairs: hosts must invoke verifier, never rely on generated JSON alone.
### Assumptions
Additive consumer adoption only after separate immutable publication; old envelopes remain valid. No rollout compatibility or delivery approval inferred.
### Unresolved Issues
None in bounded correction. Separate publication010 remains required before Commerce integration.
### Architectural Concerns
None. No consumer schemas forked.
### Git / VCS
Task branch task/ARCH-066-SHARED-009. Canonical workspace /Users/kwadwoadomafriyie/project/moda-interact-workspace; parent /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-066-SHARED-009; implementation /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-066-SHARED-009. Both matching branches; shared workspace/implementation switched or mutated for task work: no; another task worktree reused: no. Launcher preparation dependency gate passed SHARED005 Complete; parent reused/implementation created; both remote FF not-needed and main already-current. Recursive sync/update passed, submodules ready with no entries. Claim80e43ec54e8fa004fa7f4c9b820ded834b4acc73 pushed Attempt1 codex. Implementation16e3b35; report exact SHA in task branch history; pushed to matching origin/task refs. No gitlink staged, main merged/pushed, or immutable release overwritten.

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
