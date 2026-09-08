---
id: ARCH-007-GATEWAY-001
architecture_id: ARCH-007
title: Deploy independently scalable billing worker in Render blueprints
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: pending
priority: 140
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-007-BACKGROUND-008
enables: 
  - ARCH-007-SYSTEM-TEST-002
  - ARCH-007-SYSTEM-TEST-003
created: 2026-09-07
updated: 2026-09-07
---

# ARCH-007-GATEWAY-001: Deploy independently scalable billing worker in Render blueprints

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Add the accepted billing worker entrypoint to architecture-managed Render test/production topology with correct database/Shopify/observability environment wiring, readiness and conservative initial scaling.

## Context

Billing publication/reconciliation must not run inside recovery/messaging workers by accident. Background-008 provides a dedicated entrypoint; Gateway owns deployable topology.

## Scope

`render.test.yaml`, `render.production.yaml`, topology docs/validation scripts as required. Use actual Background package scripts/entrypoint; do not invent commands.

## Out of Scope

- Changing Background source.
- Creating Shopify credentials/secrets in source control.
- Deploying system tests.

## Requirements

- Inspect accepted Background-008 `package.json`/entrypoint/readiness scripts and use those exact commands.
- Declare `moda-billing-worker-test` and `moda-billing-worker-production` (or naming consistent with existing topology) as background worker services with no public exposure.
- Wire PostgreSQL and required Shopify Partner/App Events configuration using existing Blueprint secret placeholders/environment-group conventions. Never commit secret values.
- Wire OpenTelemetry identity `service.name=moda-billing-worker`, existing namespace and environment-specific resource attributes consistent with other worker services.
- Configure readiness using accepted Background readiness command/pattern. Do not make readiness depend on a live App Events call.
- Use conservative single-instance/low initial scale unless existing Blueprint autoscaling convention and measured architecture justify more; independent horizontal scaling must remain possible.
- Update render topology/deployment docs and validation scripts to include billing worker.

## Work Items

- [ ] Inspect current test/production worker declarations.
- [ ] Add billing worker to both blueprints.
- [ ] Add env/secret placeholders and OTel identity.
- [ ] Update topology docs/blueprint validators.
- [ ] Run existing gateway blueprint/observability validation.

## Interfaces / Contracts

Deployable:

```text
moda-billing-worker-{test|production}
source: moda-interact-background
start: accepted `npm run start:billing-worker`
readiness: accepted `npm run readiness:billing-worker`
```

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-SYSTEM-TEST-002
- ARCH-007-SYSTEM-TEST-003

## Acceptance Criteria

- [ ] Billing worker is private/background and independently scalable.
- [ ] Commands match accepted Background implementation.
- [ ] No secret values committed.
- [ ] Test and production telemetry remain distinguishable.
- [ ] Blueprint validators and gateway tests pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Do not run `git commit` or `git push`.


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
