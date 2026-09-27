---
id: ARCH-021-COMMERCE-067
architecture_id: ARCH-021
title: Separate Agent contract and Result Template validation boundaries
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 74
executor: copilot
claimed_at: 2026-09-27T15:45:11Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-063
enables:
  - ARCH-021-COMMERCE-068
created: 2026-09-27
updated: 2026-09-27
---

# Separate Agent contract and Result Template validation boundaries

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Refactor the authoring validation backend so Agent Contract validation owns only the model call-side contract (`definitionVersion`, description and input schema), while Result Template validation owns `responseTemplate` compatibility with the Tool result contract, without weakening final publication validation or breaking the currently integrated UI before COMMERCE-068 lands.

## Context

COMMERCE-056 correctly validated the fields then exposed in Agent Contract, including `responseTemplate`. The architecture has since refined the ownership boundary: `responseTemplate` belongs to a dedicated Result Template tab because it formats post-execution Tool data, while Agent Contract describes how the model decides to call the Tool and what arguments it may provide.

COMMERCE-063 has introduced the canonical result-template validation boundary. This task separates backend responsibilities while retaining a temporary compatibility adapter for the currently integrated Agent Contract UI until COMMERCE-068 switches consumers.

## Scope

Expected implementation areas include:

```text
src/commerce/tool-authoring/agent-contract-validation.ts
src/commerce/tool-authoring/result-template-validation.ts or COMMERCE-063 module
src/commerce/tool-authoring/contracts.ts
src/studio/tools/agent-contract-validation-server-actions.ts
src/commerce/tool-definition/publication.ts
focused validation tests
```

## Out of Scope

- React Agent Contract changes; COMMERCE-068 owns them.
- Result Template React UI; COMMERCE-066 owns it.
- Request/Response changes.
- Provider I/O.
- Database writes.
- New publication rules unrelated to the ownership split.

## Requirements

### R1 — define the Agent call-side validation contract

Add/reuse a named validator whose semantic input is only:

```text
definitionVersion
description
inputSchema
```

It validates the existing SemVer, description, bounded input-schema and forbidden authority/credential rules from COMMERCE-056.

It MUST NOT require output/result-schema context.

### R2 — Result Template validation remains separate

`responseTemplate` + current output contract must be validated through COMMERCE-063's Result Template boundary.

Do not duplicate token/path compatibility logic back into Agent validation.

### R3 — preserve final publication completeness

Final Tool definition/publication validation must still require both:

```text
valid Agent call-side contract
valid Result Template against canonical output contract
```

The ownership split must not make publication less strict.

### R4 — temporary compatibility for current UI

Until COMMERCE-068 changes the React consumer, retain a bounded compatibility action/helper if required so the current integrated Agent Contract tab continues to function and existing tests remain green.

The compatibility adapter may compose the two canonical validators, but it must not become the new canonical ownership boundary.

Document/deprecate the compatibility path clearly in code/tests.

### R5 — deterministic issue ownership

Agent issues use Agent-local paths such as:

```text
/definitionVersion
/description
/inputSchema/...
```

Result Template issues remain under `/responseTemplate/...` and are produced by the Result Template validator.

### R6 — zero side effects

Both validation boundaries remain non-mutating and perform no provider calls, credential reads, Tool writes, audit writes or publication receipt writes.

## Work Items

- [ ] Extract/rename the canonical Agent call-side validator.
- [ ] Remove result/output-schema dependency from that canonical Agent validator.
- [ ] Route responseTemplate compatibility through COMMERCE-063 only.
- [ ] Preserve final publication validation of both boundaries.
- [ ] Add a temporary compatibility adapter only if required by the pre-C068 UI.
- [ ] Update focused validation tests and issue-path assertions.

## Interfaces / Contracts

Consumes COMMERCE-063 Result Template validation.

Produces two independent Commerce-internal authoring validation boundaries:

```text
Agent call-side contract validation
Result Template validation
```

No persistent or Shared contract changes.

## Dependencies

- `ARCH-021-COMMERCE-063`

## Enables

- `ARCH-021-COMMERCE-068`

## Acceptance Criteria

- [ ] Canonical Agent validation no longer needs `responseTemplate` or output schema.
- [ ] Canonical Result Template validation is the only authoring owner of template/output compatibility.
- [ ] Publication still rejects invalid Agent or Result Template contracts.
- [ ] Existing UI remains buildable/testable before COMMERCE-068 through a bounded compatibility path if necessary.
- [ ] Agent issues never masquerade as Result Template issues and vice versa.
- [ ] Validation remains zero-provider-I/O and zero-persistence.

## Validation

- [ ] focused Agent validation tests
- [ ] focused Result Template validation tests
- [ ] publication validation tests
- [ ] current AgentContractTab integration regression tests
- [ ] targeted lint
- [ ] changed-file TypeScript diagnostics
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-068.

## Implementation Notes

This task is an ownership refactor, not a relaxation. Keep COMMERCE-056's accepted Agent validation behavior for the three remaining Agent fields.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending review.

### Follow-up

None.
