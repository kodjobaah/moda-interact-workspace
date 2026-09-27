---
id: ARCH-023-SHARED-003
architecture_id: ARCH-023
title: Harden Commerce runner instruction trust
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 12
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-023-SHARED-004
created: 2026-09-27
updated: 2026-09-27
---

# Harden Commerce runner instruction trust

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Strengthen the code-owned Commerce runner security kernel and trusted-instruction composition contract so untrusted context remains non-authoritative across languages.

## Context

The runner already places immutable platform instructions before host/capability instructions and states that tools/context are not instructions. ARCH-023 makes this trust boundary explicit for merchant knowledge and requires it to hold regardless of language or apparent role labels inside retrieved text.

## Scope

- Refine immutable runner security instructions only where needed to make origin-based trust and permission non-expansion explicit.
- Preserve the host-instruction input as trusted platform/shop configuration composed after the immutable kernel and before capability prompts.
- Add regression tests proving multilingual/mixed-language context cannot alter grant/tool availability or instruction ordering.

## Out of Scope

- Platform/shop prompt database resolution.
- Capability prompt authoring.
- Prompt-injection phrase detection/classification.
- Changing tool authorization semantics.

## Requirements

- Trust is based on source/origin, not language or strings such as SYSTEM/developer.
- No customer, merchant knowledge, catalogue or tool-result content can expand permissions.
- Immutable kernel stays first; trusted host instructions stay ahead of capability prompts.
- Security kernel is one canonical code-owned definition, not 20 translated policy copies.

## Work Items

- [ ] Update runner instructions/composition only as necessary.
- [ ] Add instruction-order and multilingual untrusted-context regressions.

## Interfaces / Contracts

Consumed by Commerce/Background through the published Shared runner. Published package gate: ARCH-023-SHARED-004.

## Dependencies

None

## Enables

- ARCH-023-SHARED-004

## Acceptance Criteria

- [ ] Existing tool/grant authorization tests remain green.
- [ ] Host/capability ordering remains deterministic.
- [ ] Multilingual untrusted content has no path to change tool set or runtime authorization.

## Validation

- [ ] Focused runner tests.
- [ ] Shared package tests/build/typecheck as declared.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

None

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

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

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending.

### Follow-up

None
