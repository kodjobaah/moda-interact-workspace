---
id: ARCH-066-SHARED-008
architecture_id: ARCH-066
title: publish standalone turn identity
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: superseded
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ['ARCH-066-SHARED-007']
enables: ['ARCH-066-MCP-002']
created: 2026-11-08
updated: 2026-11-08
---
# Publish standalone turn identity

## Architecture
ARCH-066; docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md and consumer-contract C/D. Coordinator moda_architect.

## Objective
Publish accepted standalone turn identity contract as an exact immutable package.

## Context
BACKGROUND001 proved published5.7 CommerceTurnIdentitySchema.checkoutRecoveryId required, live-budget recoveryId required and routing/worker/context helper recovery-only. Existing Conversation already has canonical standalone shop/customer relations. Never fabricate a recovery ID or waive consent to satisfy task. Preserve prior accepted history.

## Scope
Release metadata and exact registry artifact only. Select approved available compatible version after accepted implementation; reuse byte-identical accepted artifacts, scripts-disabled exact pack/publish and downloadable integrity/export checks. No runtime source changes or implementation validation reruns.

## Out of Scope
New schema/customer mapping, arbitrary entitlement policy, fake checkout/recovery facts, provider sends, live deployment, main merge or automatic follow-on work.

## Requirements
Accepted Complete prerequisite, exact downloadable artifact and canonical standalone/recovery exports verified, metadata-only diff.

## Work Items
- [ ] Release metadata and exact registry artifact only. Select approved available compatible version after accepted implementation; reuse byte-identical accepted artifacts, scripts-disabled exact pack/publish and downloadable integrity/export checks. No runtime source changes or implementation validation reruns.

## Interfaces / Contracts
Canonical published Shared turn/assertion/grant identity; existing Conversation/Shop/customer ownership. Host/service policy remains owning runtime responsibility.

## Dependencies
- ARCH-066-SHARED-007

## Enables
- ARCH-066-MCP-002

## Acceptance Criteria
- [ ] Accepted Complete prerequisite, exact downloadable artifact and canonical standalone/recovery exports verified, metadata-only diff.

## Validation
- [ ] Release mechanics only; no tests/lint/typecheck/build reruns.

## Stop Condition
Publish source/report and submit review, then STOP. Explicit developer completion required; no enabled task auto-start.

## Implementation Notes
Exact evidence in BACKGROUND001 blocked report. Background same task later adapts loader/router/budget using existing canonical customer/shop, language/consent/general-admission and send fences; no fake recovery. Return actual incompatible contract/policy to architect rather than choose a fallback grant.

## Completion Report
### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
Definition only.
### Deviations
None
### Assumptions
Existing persisted standalone ownership relations retained.
### Unresolved Issues
Original standalone admission gap above.
### Architectural Concerns
Identity is never evidence or permission.

## Architect Review
### Review Status
Pending
### Review Notes
Source-level prerequisite gap documented, no execution.
### Reviewed Files
Shared5.7 turn type; Background live-budget/router/worker/context helper.
### Validation Reviewed
No execution claimed.
### Architecture Conformance
Shared-first identity then publication/MCP before Background adoption.
### Follow-up
None

## Scope Withdrawal — 2026-11-08
Developer explicitly selected checkout-led production scope and withdrew standalone identity/admission chain. Superseded at unchanged Attempt0, no claim or implementation. SHARED008 publication expressly prohibited; no npm publish/version selection. MCP002 no longer a dependency for recovery-linked Background acceptance. Historical definition retained only; no source rollback or alteration of immutable published artifacts.
