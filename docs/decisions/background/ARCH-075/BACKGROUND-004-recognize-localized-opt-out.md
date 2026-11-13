---
id: ARCH-075-BACKGROUND-004
architecture_id: ARCH-075
title: Recognize explicit published localized opt-out commands
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
depends_on:
  - ARCH-075-BACKGROUND-003
  - ARCH-075-SHARED-004
enables:
  - ARCH-075-SYSTEM-TEST-001
created: 2026-11-13
updated: 2026-11-13
---

# Recognize explicit published localized opt-out commands

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Recognize explicit published localized opt-out commands.

## Context

Actual reviewed translated opt-out copy instructs STOPP (Norwegian/Swedish) and DUR (Turkish), while existing exact command matcher accepts only STOP/UNSUBSCRIBE. No live locale approval or send should promise an unrecognized opt-out command. This is a bounded consent correction, not language inference.

## Scope

Existing whatsapp-contact-opt-out/phone.ts explicit command matcher and directly related opt-out routing/priority/fence regression tests. Add only exact STOPP and DUR to existing STOP/UNSUBSCRIBE semantics, preserving case-insensitive matching, existing trim and optional single dot/exclamation punctuation.

## Out of Scope

Substring or NLP matching, additional unreviewed aliases, changing consent priority/shop scope, Shared release/schema, template translation edits, live sends/DB writes/replays/resets, source merges or unrelated refactors.

## Requirements

Text-only whole-command recognition: STOP, UNSUBSCRIBE, STOPP, DUR, existing trim/case and optional single . or !. No sentences/prefix/suffix/substrings/extra punctuation or nontext intent. Route recognized localized commands through the exact existing durable opt-out/tenant resolution and priority path before ordinary conversation/AI handling. Existing quoted/standalone merchant scope, STOP persistence-before-notice, duplicate behavior, no-contact and final send/continuation fences remain unchanged. Use synthetic data; do not change provider/customer state.

## Work Items

- [ ] Reproduce exact localized command omission before correction.
- [ ] Extend only explicit matcher and meaningful consent priority/scope/fence regressions.
- [ ] Complete declared validation, mirrored report and stop.

## Interfaces / Contracts

Existing Background-local explicit WhatsApp opt-out command and durable consent pipeline. Published inbound schemas unchanged. No new shared parser is required for this single owning runtime policy.

## Dependencies

ARCH-075-BACKGROUND-003; ARCH-075-SHARED-004

## Enables

ARCH-075-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Exact STOPP/DUR variants follow existing recognized-command behavior; sentences/substrings/malformed variants/nontext refuse.
- [ ] Existing durable consent priority, merchant scope, duplicate and final-send/continuation suppression remain proven.
- [ ] Canonical physical isolation/sync and exact validation evidence reported; no live mutation.

## Validation

- [ ] Red/green exact matcher cases and negative boundaries; existing opt-out routing/priority and relevant send-fence/continuation regressions.
- [ ] Declared relevant focused tests, scoped lint/typecheck and exact-head full CI; additional persistence tests only where actual changed path needs them.
- [ ] Diff/privacy hygiene, no dependency/runtime-policy expansion or live requests.

## Stop Condition

After scope and required checks complete, set review, submit mirrored Completion Report and STOP. No dependent implementation or live action.

## Implementation Notes

You are not alone; preserve all other work. Canonical packet owns startup/isolation/claim. Root owns source merges and live locale approval. Return any newly discovered translated opt-out commands before expanding this exact allowlist.
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

Existing explicit-command policy otherwise unchanged.

### Unresolved Issues

None currently.

### Architectural Concerns

Return actual cross-owner gaps.

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
