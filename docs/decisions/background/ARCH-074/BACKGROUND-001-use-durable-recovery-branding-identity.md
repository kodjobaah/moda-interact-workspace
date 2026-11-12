---
id: ARCH-074-BACKGROUND-001
architecture_id: ARCH-074
title: Use durable recovery identity for prepared branded replies
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Use durable recovery identity for prepared branded replies

## Architecture

ARCH-074; docs/architecture/ARCH-074-recovery-branding-billing-scope.md; coordinator moda_architect.

## Objective

Deliver legitimate recovery-linked branded AI replies independently of billing executionScope while safely finalizing deterministic pre-provider suppression.

## Context

Normal/free contract admission returns general billing scope even for a linked recovery. Delivery's new BRAND_IMAGE scope guard confuses billing with durable recovery identity, then returns before placeholder cleanup. Processor ignores suppression result and reports a send. Existing durable recovery/current-control/final fence can supply the correct authority.

## Scope

Owning Background prepared text/conversation delivery and narrowly related notice preparation gates if they use the same incorrect billing proxy; existing AiTurnOwnershipService/checkAutomatedTurn integration; affected processor result/outcome handling; regression tests/docs. Inspect current exact source first. Root owns merge/deploy/live verification.

## Out of Scope

Billing/usage/entitlement policy changes, generic lifecycle refactor, tenant fallback inference, dropping branding on valid recovery solely to evade proof, source/media policy relaxation, schema/Shared/npm/infrastructure changes, unrelated tests/features, production writes/requeue/reset/replay or extra WhatsApp sends.

## Requirements

Keep normal/free billing classification unchanged. Use current AiTurnOwnershipService durable Conversation→CheckoutRecovery identity, exact expected shop, AI mode/revision and original inbound/control/message receipt to authorize a new recovery BRAND_IMAGE even when billing executionScope is general. Never substitute billing scope for relationship authority, or recapture newer ownership to legitimize stale work. General/unbound, missing/mismatched recovery and wrong tenant/control/version remain refused. Existing final Shop/consent/header/source/current READY/policy-row/idempotency fences are unchanged.

Deterministic pre-provider invalid prepared-plan/identity refusal must use existing conditional failPrepared cleanup so no empty PENDING phantom remains. Cleanup must never overwrite a permit, provider message, actual duplicate/admitted or uncertain outcome. Do not convert ambiguous provider attempts to retry or falsely claim cleanup success. Preserve provider-boundary safety flags unless a concrete tested correction is needed. Actual result is consumed at the affected AI caller: suppressed outcome cannot log agent-response-sent; turn completion/cleanup follows existing version-scoped rules and preserves newer input/control. No broad new retry policy.

Use shared logger for semantic outcomes; do not add generic telemetry or private payload logs. You are not alone: preserve others' work and only modify assigned owning modules. Return genuine cross-owner/contract gaps rather than unsafe workaround.

## Work Items

- [ ] Reproduce normal-contract recovery branded suppression against original code.
- [ ] Correct durable recovery eligibility with existing tenant/control/final fences.
- [ ] Finalize deterministic pre-provider refusal and truthful caller outcome without touching committed/unknown sends.
- [ ] Validate focused/integration/CI and publish mirrored report, then stop.

## Interfaces / Contracts

Existing Background admission/billing result, AiTurnOwnershipService/checkAutomatedTurn, OutboundSendFence, conditional failPrepared and published Shared5.13.7 media contract. No new wire/schema/authority contract.

## Dependencies

None. Current implementation main includes accepted ARCH-073.

## Enables

Developer source merge/deployment and fresh genuine customer verification.

## Acceptance Criteria

- [ ] Normal/free contract with general billing scope and real same-tenant recovery can send exactly one branded AI image with exact full header/footer caption.
- [ ] Generic/unbound/wrong-tenant/stale-control/inbound/lease/media/policy cases remain refused with no provider call.
- [ ] Deterministic pre-provider suppression leaves no phantom pending placeholder or false sent outcome; duplicate/admitted/uncertain states unchanged.
- [ ] Billing/usage semantics and all existing receipt/final-permit checks remain intact.
- [ ] Canonical mirrored worktree/synchronization/recursive proof recorded; no private payload/source scope expansion.

## Validation

- [ ] Meaningful prior-code red for normal/free contract actual recovery billing-general BRAND_IMAGE path.
- [ ] Actual processor/admission policy→prepared branded delivery→final fence→mock provider regression with real PostgreSQL recovery state; Free/normal contract semantics exercised, not manually changing billing policy.
- [ ] General/unbound and tenant/control/version negatives; pre-provider failPrepared leaves finalized row, already-admitted/duplicate/provider-uncertain preservation; caller outcome truthful.
- [ ] Relevant existing billing/admission/processor/media regressions and actual PostgreSQL identity/cleanup checks.
- [ ] Task-owned lint/typecheck/declared build and exact final-head full CI; inspect actual package scripts first.
- [ ] Diff/privacy hygiene, synthetic/mocked providers, no production mutation/live sends during task validation.

## Stop Condition

After required work and validation complete, set review, submit Completion Report and STOP. Do not merge/deploy, retry production message or begin adjacent work.

## Implementation Notes

No broad billing-scope rename needed. Existing ownership read is durable linkage, not a model assertion. Existing conditional cleanup protects admitted messages. Source/turn completion must remain version-scoped. Preserve user changes and use the canonical prepared packet.

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

Existing approved media/source evidence remains valid; no new provider configuration is required.

### Unresolved Issues

None currently; return concrete gaps.

### Architectural Concerns

No authorization or provider-outcome safety weakening is permitted.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual source review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
