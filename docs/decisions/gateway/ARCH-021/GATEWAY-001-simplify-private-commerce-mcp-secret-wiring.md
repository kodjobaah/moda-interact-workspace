---
id: ARCH-021-GATEWAY-001
architecture_id: ARCH-021
title: Remove Commerce MCP assertion-key wiring and preserve private link
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-09-24T16:00:02Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-030
  - ARCH-021-BACKGROUND-001
enables:
  - ARCH-021-SYSTEM-TEST-001
created: 2026-09-24
updated: 2026-09-24
---

# Remove Commerce MCP assertion-key wiring and preserve private link

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Preserve the existing private Commerce MCP topology and public denial while deleting all RSA/JWT assertion-key environment wiring. Add **no replacement MCP token or secret**.

## Context

ARCH-020 already routes Background to the Commerce internal service address and denies public `/api/mcp` routes. COMMERCE-030/BACKGROUND-001 remove application-layer MCP authentication; private network placement is therefore the only caller trust boundary and PostgreSQL remains the business-authorization boundary.

## Scope

Primary files:

```text
render.production.yaml
render.test.yaml
docs/commerce-deployment.md
docs/gateway.md
tests/validate-render-blueprints.sh
tests/validate-render-blueprints-negative.sh
```

## Out of Scope

- Application code.
- Making MCP public.
- Adding a shared token/API key/mTLS/key pair.
- Automatic deployment.

## Requirements

### R1. Preserve exact private topology

Keep `COMMERCE_MCP_URL` attached only to the Background messaging worker and pointing to Commerce's internal/private service address `/api/mcp`.

Keep the existing public gateway denial for `/api/mcp`, aliases, encoded separators, dot segments and trailing/path variants.

### R2. Remove all MCP authentication secret/key wiring

Remove from production/test Blueprint, docs and validators:

```text
COMMERCE_ASSERTION_PUBLIC_KEYS
COMMERCE_ASSERTION_PRIVATE_KEY
COMMERCE_ASSERTION_KEY_ID
COMMERCE_MCP_SERVICE_TOKEN
```

Do not add any replacement MCP secret/key/token environment variable.

### R3. Commerce service remains private for MCP

The Blueprint/gateway contract must continue to make `/api/mcp` reachable through the Commerce internal service address only. Staff/public Studio routes may remain exposed through the existing approved public routing; that must not expose `/api/mcp`.

### R4. Deployment runbook

Replace JWT/token examples with context-only private requests. Runbook must demonstrate:

```text
private service address + valid DB-backed context -> protocol response
private service address + malformed/stale context -> explicit denial/error
public /api/mcp -> denied before Commerce MCP execution
```

No secret generation/distribution/rotation step remains.

### R5. Blueprint tests

Positive validation asserts:

```text
COMMERCE_MCP_URL exists only where already authorised (Background messaging worker)
old assertion key env vars absent
no replacement MCP credential env var added
public MCP denial remains
```

Negative validation must fail when public MCP exposure is introduced or old key variables return.

## Work Items

- [ ] Remove assertion-key env declarations from production/test Blueprints.
- [ ] Add no replacement secret.
- [ ] Update gateway/commerce deployment docs.
- [ ] Update positive/negative Blueprint validators.

## Interfaces / Contracts

Consumes COMMERCE-030/BACKGROUND-001 context-only private MCP contract.

## Dependencies

- ARCH-021-COMMERCE-030
- ARCH-021-BACKGROUND-001

## Enables

- ARCH-021-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] `/api/mcp` remains private-only.
- [ ] No RSA/JWT assertion env remains.
- [ ] No bearer/API/shared secret replacement is introduced.
- [ ] `COMMERCE_MCP_URL` still uses the internal Commerce service address.
- [ ] Public MCP denial remains validated.

## Validation

- [ ] `bash tests/validate-render-blueprints.sh`
- [ ] `bash tests/validate-render-blueprints-negative.sh`
- [ ] repository-declared YAML/config validation
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

Do not introduce a replacement credential merely because the old key variables are removed. The agreed trust boundary is the private service link.

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
