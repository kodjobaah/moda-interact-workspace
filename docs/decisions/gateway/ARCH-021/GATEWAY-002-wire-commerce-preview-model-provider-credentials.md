---
id: ARCH-021-GATEWAY-002
architecture_id: ARCH-021
title: Wire Commerce Preview selected-model provider credentials
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 104
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-106
  - ARCH-021-COMMERCE-109
enables:
  - ARCH-021-SYSTEM-TEST-004
created: 2026-09-29
updated: 2026-09-29
---

# Wire Commerce Preview selected-model provider credentials

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Update the canonical Render Blueprint/runtime documentation so the Commerce service can execute the frozen selected-shop OPENAI or GROQ model chosen by COMMERCE-106 using Commerce-owned server-only credentials, and remove obsolete fixed Preview provider/model/API-key wiring.

## Context

Before Phase 6, Commerce Preview uses a single environment-wide tuple:

```text
COMMERCE_PREVIEW_PROVIDER
COMMERCE_PREVIEW_MODEL
COMMERCE_PREVIEW_API_KEY
```

That cannot execute arbitrary effective Model catalogue selections because model/provider are now database-owned Agent Configuration facts. COMMERCE-106 changes the Commerce runtime contract to:

```text
COMMERCE_PREVIEW_ENABLED             kill switch
COMMERCE_OPENAI_API_KEY              server-only provider credential
COMMERCE_GROQ_API_KEY                server-only provider credential
```

The selected provider/model ID comes from the frozen effective configuration, not from Render environment values. COMMERCE-109 removes the old Commerce-code dependency before this deployment wiring task runs.

## Scope

Primary Gateway-owned files:

```text
render.test.yaml
render.production.yaml
tests/validate-render-blueprints.sh
tests/validate-render-blueprints-negative.sh
docs/commerce-deployment.md
docs/render-topology.md or existing relevant deployment docs
```

Inspect actual Blueprint structure before editing; preserve established secret/config-group conventions where compatible with this explicit contract.

## Out of Scope

- Commerce application code.
- Model catalogue/database changes.
- Prompt configuration.
- Background/WhatsApp model credentials.
- Reusing another service's provider credential by undocumented coupling.
- Enabling production Preview if it is currently disabled.
- Deploying automatically.

## Requirements

### R1 — add Commerce-owned provider credentials

Declare on the Commerce service in both test and production:

```text
COMMERCE_OPENAI_API_KEY
COMMERCE_GROQ_API_KEY
```

Both are external secret inputs:

```yaml
sync: false
```

Do not commit values/placeholders that could be mistaken for real credentials.

The credentials must be independently configurable per environment.

### R2 — retain Preview kill-switch policy exactly

Keep:

```text
COMMERCE_PREVIEW_ENABLED
```

with the current architecture-approved environment policy unless another accepted task explicitly changed it.

Current expected policy at task definition time:

```text
test       true
production false
```

Do not enable production Preview merely because provider credentials exist.

### R3 — remove obsolete fixed Preview configuration

Remove from Commerce service Blueprint config, validators and deployment docs:

```text
COMMERCE_PREVIEW_PROVIDER
COMMERCE_PREVIEW_MODEL
COMMERCE_PREVIEW_API_KEY
```

Do not introduce renamed equivalents that again make provider/model an environment-owned selection.

Provider/model selection is frozen from the database Agent Configuration; only provider credentials are environment secrets.

### R4 — do not attach unrelated service config groups wholesale

The Gateway currently has provider credentials/config groups for other workloads. Do not solve Commerce wiring by attaching unrelated `ai`, translation, WhatsApp or other service groups if doing so would also grant unrelated environment variables/secrets.

Prefer explicit Commerce-owned service secret declarations unless an existing group contains **exactly** the intended Commerce contract.

No secret sharing between deployables should be introduced accidentally.

### R5 — positive Blueprint validation

Update validation to assert in test and production:

```text
Commerce has COMMERCE_OPENAI_API_KEY sync:false
Commerce has COMMERCE_GROQ_API_KEY sync:false
Commerce has COMMERCE_PREVIEW_ENABLED with expected environment policy
Commerce does not have COMMERCE_PREVIEW_PROVIDER
Commerce does not have COMMERCE_PREVIEW_MODEL
Commerce does not have COMMERCE_PREVIEW_API_KEY
provider secret values are not committed
```

Preserve all unrelated existing Blueprint validation.

### R6 — negative mutation validation

Add negative cases that fail validation when at least:

```text
one required Commerce provider credential is missing
Commerce provider credential is made non-secret/synchronized improperly
obsolete COMMERCE_PREVIEW_PROVIDER returns
obsolete COMMERCE_PREVIEW_MODEL returns
obsolete COMMERCE_PREVIEW_API_KEY returns
production COMMERCE_PREVIEW_ENABLED is changed from false without architecture change
```

Do not weaken unrelated negative cases.

### R7 — deployment documentation

Document that:

```text
Model provider/model ID = frozen selected-shop Agent Configuration
API credential = matching Commerce server secret
no provider fallback
missing selected-provider credential = Preview unavailable
Preview-enabled flag remains an independent kill switch
```

Document secret provisioning names only, never values.

## Work Items

- [ ] Add `COMMERCE_OPENAI_API_KEY` and `COMMERCE_GROQ_API_KEY` as Commerce service `sync:false` inputs in test/production.
- [ ] Preserve the existing `COMMERCE_PREVIEW_ENABLED` environment policy.
- [ ] Remove `COMMERCE_PREVIEW_PROVIDER`, `COMMERCE_PREVIEW_MODEL`, `COMMERCE_PREVIEW_API_KEY` from canonical Blueprints.
- [ ] Update Gateway positive validation for exact presence/absence/secret rules.
- [ ] Add negative mutations for missing/miswired new secrets and reintroduced old config.
- [ ] Update deployment/topology documentation.

## Interfaces / Contracts

Consumes the Commerce runtime configuration contract accepted in:

```text
ARCH-021-COMMERCE-106
ARCH-021-COMMERCE-109
```

Produces deployment wiring only. No application contract is redefined here.

## Dependencies

- ARCH-021-COMMERCE-106
- ARCH-021-COMMERCE-109

## Enables

- ARCH-021-SYSTEM-TEST-004

## Acceptance Criteria

- [ ] Test/production Commerce services declare both new provider credentials as `sync:false` secrets.
- [ ] Test keeps Preview enabled and production keeps Preview disabled per current policy.
- [ ] Old fixed Preview provider/model/API-key variables are absent from canonical Blueprints/docs/validators except intentional negative fixtures/history.
- [ ] No unrelated service secret group is attached merely to obtain provider credentials.
- [ ] Positive Blueprint validation proves exact wiring.
- [ ] Negative validation rejects missing/misconfigured new secrets and old-variable reintroduction.
- [ ] Documentation states database configuration chooses provider/model and environment supplies only matching provider credential.
- [ ] No secret value is committed.

## Validation

- [ ] `bash tests/validate-render-blueprints.sh`
- [ ] `bash tests/validate-render-blueprints-negative.sh`
- [ ] repository-declared YAML/config validation
- [ ] source search for old/new Preview credential names
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin SYSTEM-TEST-004.

## Implementation Notes

This task intentionally separates **configuration selection** from **credential wiring**. Render must not become the source of truth for which model a shop uses.

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
