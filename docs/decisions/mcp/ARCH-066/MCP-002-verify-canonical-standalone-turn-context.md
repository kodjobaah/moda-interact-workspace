---
id: ARCH-066-MCP-002
architecture_id: ARCH-066
title: verify canonical standalone turn context
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ['ARCH-066-SHARED-008']
enables: ['ARCH-066-BACKGROUND-001']
created: 2026-11-08
updated: 2026-11-08
---
# Verify canonical standalone turn context

## Architecture
ARCH-066; docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md and consumer-contract C/D. Coordinator moda_architect.

## Objective
Authorize standalone conversational calls using canonical persisted Conversation ownership without fabricated recovery identity.

## Context
BACKGROUND001 proved published5.7 CommerceTurnIdentitySchema.checkoutRecoveryId required, live-budget recoveryId required and routing/worker/context helper recovery-only. Existing Conversation already has canonical standalone shop/customer relations. Never fabricate a recovery ID or waive consent to satisfy task. Preserve prior accepted history.

## Scope
Existing private context/assertion admission, execution revalidation, canonical reader and focused tests only. Consume exact published standalone contract. Resolve Conversation.shopId/customer relations for standalone; recovery-linked owner remains CheckoutRecovery.shopId, conflicting dual owners deny. Recheck active shop/customer/consent/plan/provider/grant/purpose/version policy as existing scopes require; identity alone never authorizes. No recovery-only feature or checkout facts in standalone. Preserve private ingress, expiry/replay and call-time revocation. Reject forged/mixed/cross-tenant IDs before provider I/O. No Background sender implementation or live actions.

## Out of Scope
New schema/customer mapping, arbitrary entitlement policy, fake checkout/recovery facts, provider sends, live deployment, main merge or automatic follow-on work.

## Requirements
Real standalone canonical context passes authorized read path, missing/wrong owner/customer/permission denies pre-I/O; recovery compatibility and consent/entitlement gates unchanged.

## Work Items
- [ ] Existing private context/assertion admission, execution revalidation, canonical reader and focused tests only. Consume exact published standalone contract. Resolve Conversation.shopId/customer relations for standalone; recovery-linked owner remains CheckoutRecovery.shopId, conflicting dual owners deny. Recheck active shop/customer/consent/plan/provider/grant/purpose/version policy as existing scopes require; identity alone never authorizes. No recovery-only feature or checkout facts in standalone. Preserve private ingress, expiry/replay and call-time revocation. Reject forged/mixed/cross-tenant IDs before provider I/O. No Background sender implementation or live actions.

## Interfaces / Contracts
Canonical published Shared turn/assertion/grant identity; existing Conversation/Shop/customer ownership. Host/service policy remains owning runtime responsibility.

## Dependencies
- ARCH-066-SHARED-008

## Enables
- ARCH-066-BACKGROUND-001

## Acceptance Criteria
- [ ] Real standalone canonical context passes authorized read path, missing/wrong owner/customer/permission denies pre-I/O; recovery compatibility and consent/entitlement gates unchanged.

## Validation
- [ ] Focused actual private protocol/reader and call-time revocation/identity fixtures, declared typecheck/build/lint. No live provider.

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
