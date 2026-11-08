---
id: ARCH-066-SHARED-007
architecture_id: ARCH-066
title: define canonical standalone turn identity
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ['ARCH-066-SHARED-005']
enables: ['ARCH-066-SHARED-008']
created: 2026-11-08
updated: 2026-11-08
---
# Define canonical standalone turn identity

## Architecture
ARCH-066; docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md and consumer-contract C/D. Coordinator moda_architect.

## Objective
Represent a true standalone conversational turn without a fabricated checkout recovery ID.

## Context
BACKGROUND001 proved published5.7 CommerceTurnIdentitySchema.checkoutRecoveryId required, live-budget recoveryId required and routing/worker/context helper recovery-only. Existing Conversation already has canonical standalone shop/customer relations. Never fabricate a recovery ID or waive consent to satisfy task. Preserve prior accepted history.

## Scope
Existing CommerceTurnIdentitySchema and canonical assertions/grant/runner turn contracts plus tests. Introduce explicit canonical conversation ownership scope with backward-compatible recovery parsing: recovery scope requires real checkoutRecoveryId; standalone scope forbids it and requires existing shopId/conversationId and existing actor/version identity. Preserve all existing expiry/replay/tenant/grant binding fields; canonical signatures/hashes cover scope and identity, no local alternative hash. No entitlement/consent permission is granted by standalone identity. Runner must not infer checkout facts or make recovery-only actions available absent recovery. Publish browser-safe schemas/types/validators once; no service source imports. Document exact consumer migration and fail-closed old/new behavior before implementation.

## Out of Scope
New schema/customer mapping, arbitrary entitlement policy, fake checkout/recovery facts, provider sends, live deployment, main merge or automatic follow-on work.

## Requirements
Real recovery unchanged, explicit standalone valid, fake/ambiguous/mixed identities reject; assertion/grant scope/tenant/replay tampering fails. Required schemas/types/runner call paths accept canonical standalone without recovery facts.

## Work Items
- [ ] Existing CommerceTurnIdentitySchema and canonical assertions/grant/runner turn contracts plus tests. Introduce explicit canonical conversation ownership scope with backward-compatible recovery parsing: recovery scope requires real checkoutRecoveryId; standalone scope forbids it and requires existing shopId/conversationId and existing actor/version identity. Preserve all existing expiry/replay/tenant/grant binding fields; canonical signatures/hashes cover scope and identity, no local alternative hash. No entitlement/consent permission is granted by standalone identity. Runner must not infer checkout facts or make recovery-only actions available absent recovery. Publish browser-safe schemas/types/validators once; no service source imports. Document exact consumer migration and fail-closed old/new behavior before implementation.

## Interfaces / Contracts
Canonical published Shared turn/assertion/grant identity; existing Conversation/Shop/customer ownership. Host/service policy remains owning runtime responsibility.

## Dependencies
- ARCH-066-SHARED-005

## Enables
- ARCH-066-SHARED-008

## Acceptance Criteria
- [ ] Real recovery unchanged, explicit standalone valid, fake/ambiguous/mixed identities reject; assertion/grant scope/tenant/replay tampering fails. Required schemas/types/runner call paths accept canonical standalone without recovery facts.

## Validation
- [ ] Focused recovery compatibility/standalone missing/mixed/forged/replay vectors, declared typecheck/build. No publication/service integration.

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
