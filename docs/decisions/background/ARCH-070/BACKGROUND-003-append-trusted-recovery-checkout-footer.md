---
id: ARCH-070-BACKGROUND-003
architecture_id: ARCH-070
title: Append trusted recovery checkout links to eligible AI replies
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Append trusted recovery checkout links to eligible AI replies

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Deterministically include the verified recovery checkout link once in every eligible checkout-initiated AI response.

## Context

The user explicitly requires checkout links on subsequent replies. Published AI wrapper body may contain only response.body, so the model or wrapper definition cannot guarantee this. Existing wrapper context verifies conversation/recovery tenant/customer, status/lifetime and trusted HTTPS shop domain, exposing checkoutAvailable and checkout.url.

## Scope

Conversation wrapper service composition, dedicated recovery footer helper, compose-ai-outbound provenance adapter and directly related tests. Inspect actual paths before implementation. No host.ts or conversation-turn-processor edits (owned by other tasks).

## Out of Scope

Templates, credentials, model prompting, consent/STOP/moderation policy changes, unrelated Shared primitives, schema or infrastructure, duplicate sends or old-message replay.

## Requirements

Reuse existing trusted recovery context. For eligible AI recovery replies, append a deterministic checkout footer once across plain text, details, recommendations, wrapped and image-caption responses. Use existing localized checkout label/renderer if available; never fabricate a URL or accept model-supplied checkout links. Include footer before media/text limits, final moderation/control gates and delivery hashes. Preserve strict raw/provenance semantics with an explicit narrow trusted augmentation if required. Prevent repeated footer duplication. Missing/expired/wrong-tenant/unsafe recovery context remains fail-closed. Nonrecovery and STOP/consent/blocked/security responses must not accidentally reengage a checkout. Preserve privacy and deterministic retries. Return concrete Shared/contract gaps before implementing outside scope.

## Work Items

- [ ] Establish exact source/fixture cause and preserve a failing regression.
- [ ] Implement only the owned correction.
- [ ] Validate positive and failure/recovery behavior and report evidence.

## Interfaces / Contracts

Consume published Shared contracts and existing MCP product evidence / durable conversation lifecycle. No new wire or schema contract is authorized. Cross-repository gaps return to architect.

## Dependencies

None. Disjoint wrapper assembly can execute independently of host recommendation and processor retry tasks.

## Enables

Developer integration and production verification after architect acceptance of both tasks.

## Acceptance Criteria

- [ ] Requirements demonstrated with deterministic positive and negative regression tests.
- [ ] Existing tenant, domain, message identity and lifecycle guarantees preserved.
- [ ] No duplicate delivery, live test send, secret logging or unrelated changes.
- [ ] Completion Report records canonical launcher packet, physical isolation, synchronization and recursive submodule evidence.

## Validation

- [ ] Regression across plain/details/recommendation/wrapped/image caption paths; exactly one trusted URL footer.
- [ ] Negative nonrecovery, expired/mismatched recovery, unsafe URL, STOP/blocked/control paths.
- [ ] Provenance, length/media fallback, final control/moderation and deterministic delivery-hash tests.
- [ ] Relevant existing wrapper/compose tests, typecheck, lint, required repository CI and diff hygiene.

## Stop Condition

Complete owned work and required validation, set review, return report and STOP. Do not merge, deploy or begin another task.

## Implementation Notes

You are not alone in the codebase. Preserve others' changes. Use the prepared dedicated mirrored worktrees and task branch. Verify actual package scripts before running checks. Existing structured semantic logs suffice; do not introduce competing logging or repeated provider work as a diagnostic mechanism.

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

Existing runtime evidence needs corroboration in source and fixtures.

### Unresolved Issues

None known beyond investigation.

### Architectural Concerns

Return contract or schema gaps before implementing outside scope.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
