---
id: ARCH-021-SYSTEM-TEST-001
architecture_id: ARCH-021
title: Validate simplified Studio configuration and private MCP
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-DATABASE-002
  - ARCH-021-COMMERCE-025
  - ARCH-021-COMMERCE-026
  - ARCH-021-COMMERCE-027
  - ARCH-021-COMMERCE-028
  - ARCH-021-COMMERCE-029
  - ARCH-021-COMMERCE-030
  - ARCH-021-BACKGROUND-001
  - ARCH-021-GATEWAY-001
enables: []
created: 2026-09-24
updated: 2026-09-24
---

# Validate simplified Studio configuration and private MCP

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Validate the integrated pre-Phase-3 simplification: reduced Agent Configuration persistence, visible/reconcilable Studio failures, unified Auth.js platform/merchant authorization, serializable production Studio boundaries, and private-link MCP with no application-layer authentication credential.

## Context

This is the terminal validation task for the simplification checkpoint. It does not implement missing application behavior. Defects must be routed to the owning Database/Commerce/Background/Gateway task.

## Scope

Add/update ARCH-021 system-test scenarios/fixtures/scripts required to exercise the accepted implementations.

## Out of Scope

- Fixing repository-owned defects inside system-test.
- Phase-3 Tool authoring implementation.
- Merchant self-service onboarding.
- Live provider/model testing unrelated to the checkpoint.

## Requirements

### R1. Agent Configuration inheritance matrix

Prove all four combinations against real persisted state:

```text
platform model + platform prompt
shop model override + platform prompt
platform model + shop prompt override
shop model override + shop prompt override
```

Clear overrides by setting nullable fields back to inheritance; verify configuration row remains and independent model/prompt edit versions behave correctly.

### R2. Template simplification

Prove category -> multiple templates, current `promptText` editing, template-copy into Agent Prompt DRAFT, and later template edits do not mutate the copied prompt draft/revision.

### R3. Error visibility and reconciliation

Prove:

```text
known DB unavailable -> visible DATABASE_UNAVAILABLE (not success/empty/unknown)
lost client response after committed mutation -> UI UNCONFIRMED -> reconcile COMMITTED -> canonical reload
lost client response before commit -> UI UNCONFIRMED -> reconcile NOT_COMMITTED -> retry enabled with new operationId
unexpected server error -> visible INTERNAL_ERROR with correlation/operation context
```

No scenario may pass by swallowing an exception.

### R4. Auth.js authorization

Prove:

```text
PlatformAdmin precedence when identity also has merchant access
manually provisioned merchant first Google login binds providerSubject exactly once
same merchant identity can have access rows for multiple shops
merchant is denied for a shop without access
VIEWER cannot mutate
EDITOR can perform allowed shop edits but not platform operations
MERCHANT ADMIN remains shop-scoped
```

No second authentication/session system is used.

### R5. Serializable Studio boundary

Production build/runtime proof must show no Server -> Client function-valued `StudioServices`, ConnectionPort, ExternalHttpUiPort or Agent Configuration action bundle is required by the normal Studio path.

### R6. Private MCP without application credential

Prove the integrated private request contains:

```text
X-Moda-Commerce-Context
JSON-RPC body
```

and contains no:

```text
Authorization Bearer MCP credential
JWT
RSA keys
COMMERCE_MCP_SERVICE_TOKEN
```

A valid private request with authoritative DB state succeeds.

Malformed context is rejected explicitly.

Well-formed context that does not match authoritative shop/conversation/inbound/grant/release state is rejected by Commerce DB authorization.

Public `/api/mcp` remains inaccessible through Gateway.

### R7. No key/token residue

Cross-repository search must find no runtime/deployment requirement for:

```text
COMMERCE_ASSERTION_PUBLIC_KEYS
COMMERCE_ASSERTION_PRIVATE_KEY
COMMERCE_ASSERTION_KEY_ID
COMMERCE_MCP_SERVICE_TOKEN
```

Historical docs may mention removed names only when clearly labelled historical; active runtime/deployment docs must not.

## Work Items

- [ ] Add reduced configuration inheritance scenarios.
- [ ] Add template-copy independence scenario.
- [ ] Add error/reconciliation scenarios.
- [ ] Add platform/merchant Auth.js authorization scenarios.
- [ ] Add serializable Studio boundary validation.
- [ ] Add context-only private MCP scenario/public denial proof.
- [ ] Add cross-repository obsolete-auth residue check.

## Interfaces / Contracts

Consumes only architect-accepted implementation dependencies listed below.

## Dependencies

- ARCH-021-DATABASE-002
- ARCH-021-COMMERCE-025
- ARCH-021-COMMERCE-026
- ARCH-021-COMMERCE-027
- ARCH-021-COMMERCE-028
- ARCH-021-COMMERCE-029
- ARCH-021-COMMERCE-030
- ARCH-021-BACKGROUND-001
- ARCH-021-GATEWAY-001

## Enables

None

## Acceptance Criteria

- [ ] R1-R7 pass.
- [ ] No application-layer MCP credential remains.
- [ ] No swallowed Studio mutation error remains in tested flows.
- [ ] No system-test task modifies implementation repositories.

## Validation

- [ ] task-specific integrated test command documented by implementation
- [ ] system-test repository lint/typecheck/build required by repository
- [ ] cross-repository residue scan
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin or modify paused Phase-3 implementation tasks.

## Implementation Notes

This task validates the checkpoint only. A failure is routed to the repository that owns the failing boundary.

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

Pending

### Follow-up

None
