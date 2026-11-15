---
id: ARCH-076-ADMIN-003
architecture_id: ARCH-076
title: Configure the independent routing agent
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 40
executor: codex
claimed_at: 2026-11-15T13:00:12Z
attempt: 1
depends_on: []
enables: [ARCH-076-BACKGROUND-004]
created: 2026-11-15
updated: 2026-11-15
---

# Configure the independent routing agent

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Manage routing-agent attributes through existing platform configuration.

## Context

15 November user-selected design retains five explicit sender entities plus the R15 evidence amendment. Sender attribution and conversation-credit renewal are independent streams. The user has authorized implementation of this reviewed design. Preserve prepared claims; execute only through the owning task launcher and accepted dependency frontier.

## Scope

Register recovery.routingAgent with Admin editor, validated references, CAS/audit, preview and focused component/PostgreSQL checks.

## Out of Scope

Other repository implementation, live settings, production migration and activation. Sender tasks must not implement allowance renewal; allowance tasks must not implement sender allocation. The SYSTEM-TEST task is deferred at the user's request.

## Requirements

- [ ] Use existing PlatformConfiguration versioned JSON; no new agent table or mutation of ordinary CommerceAgentConfiguration pointers.
- [ ] Validate enabled/model binding/published platform prompt revision/threshold/budgets/retries/history and candidate limits/decision lifetime/template audience; no hardcoded business defaults.
- [ ] Reuse existing model catalogue provider parameters/reasoning and protected credential resolver; prohibit credentials in JSON/browser/logs.
- [ ] Before shop proof require platform-available model and neutral context; optional verified-shop inheritance resolves only actual proven shop.
- [ ] Save complete valid config; missing/invalid config disables semantic selection and uses neutral clarification, never arbitrary model defaults.
- [ ] Snapshot config version, model editVersion and prompt ID/hash per request; validate JSON references at save and use (they are not DB foreign keys).

## Work Items

- [ ] Inspect the exact latest accepted repository pin and existing owning mechanisms.
- [ ] Implement only this task's scope and requirements.
- [ ] Complete the focused checks below and record exact commands and evidence.
- [ ] Return the isolated implementation branch and parent Completion Report for review.

## Interfaces / Contracts

The parent architecture's Explicit sender storage, Independent allowance storage and Configurable routing sections are authoritative. Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Dependencies

None

## Enables

Recalculate from dependent task metadata after architect acceptance; no implicit implementation handoff.

## Acceptance Criteria

- [ ] Use existing PlatformConfiguration versioned JSON; no new agent table or mutation of ordinary CommerceAgentConfiguration pointers.
- [ ] Validate enabled/model binding/published platform prompt revision/threshold/budgets/retries/history and candidate limits/decision lifetime/template audience; no hardcoded business defaults.
- [ ] Reuse existing model catalogue provider parameters/reasoning and protected credential resolver; prohibit credentials in JSON/browser/logs.
- [ ] Before shop proof require platform-available model and neutral context; optional verified-shop inheritance resolves only actual proven shop.
- [ ] Save complete valid config; missing/invalid config disables semantic selection and uses neutral clarification, never arbitrary model defaults.
- [ ] Snapshot config version, model editVersion and prompt ID/hash per request; validate JSON references at save and use (they are not DB foreign keys).

## Validation

- [ ] Admin unit/component tests for full editor, authorization, CAS, invalid scope/model/prompt and secret exclusion.
- [ ] Disposable PostgreSQL save/audit/conflicting update tests and preserved normal commerce agent settings.

Inspect the repository package.json before selecting actual commands. Required disposable PostgreSQL checks are task-local repository checks, not execution of the deferred system-test task. No live customer/provider calls belong to these checks.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set review, return the Completion Report and STOP. Do not execute another task or deploy.

## Implementation Notes

Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

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

None

### Unresolved Issues

Use owning task launcher at the accepted dependency frontier.

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Definition only; implementation not started.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation review.

### Follow-up

None


### 15 November definition amendment

This is a new independently scoped definition, not implementation evidence. No runtime source or migration has been implemented. User has authorized implementation; runtime acceptance and rollout verification remain pending.
