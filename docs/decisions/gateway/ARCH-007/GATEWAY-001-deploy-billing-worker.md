---
id: ARCH-007-GATEWAY-001
architecture_id: ARCH-007
title: Deploy independently scalable billing worker in Render blueprints
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: in_progress
priority: 140
executor: copilot
claimed_at: 2026-09-08T21:38:27Z
attempt: 1
depends_on: 
  - ARCH-007-BACKGROUND-008
enables: 
  - ARCH-007-SYSTEM-TEST-002
  - ARCH-007-SYSTEM-TEST-003
created: 2026-09-07
updated: 2026-09-08
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

- [x] Inspect current test/production worker declarations.
- [x] Add billing worker to both blueprints.
- [x] Add env/secret placeholders and OTel identity.
- [x] Update topology docs/blueprint validators.
- [x] Run existing gateway blueprint/observability validation.

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

- [x] Billing worker is private/background and independently scalable.
- [x] Commands match accepted Background implementation.
- [x] No secret values committed.
- [x] Test and production telemetry remain distinguishable.
- [x] Blueprint validators and gateway tests pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-GATEWAY-001` branch and the mirrored parent-workspace `task/ARCH-007-GATEWAY-001` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


## Completion Report

### Status

Complete, returned to architect review (Attempt 1)

### Files Changed

- `render.test.yaml`
- `render.production.yaml`
- `tests/validate-render-blueprints.sh`
- `tests/validate-render-blueprints-negative.sh`
- `docs/render-topology.md`

### Work Completed

- Added `moda-billing-worker-test` and `moda-billing-worker-production` as private Docker workers using `npm run start:billing-worker`, one initial instance, and the Background repository.
- Attached each worker to the environment common group, Shopify App/Partner Events group, and environment-specific PostgreSQL connection; no Redis, domains, or worker health check were added.
- Documented `npm run readiness:billing-worker`, PostgreSQL-only dependencies, independent scaling, and deployment ordering.
- Extended positive validation and added billing-specific negative fixtures for the command and Shopify App group contract.

### Validation Results

- `bash tests/validate-render-blueprints.sh` passed for test and production.
- `bash tests/validate-render-blueprints-negative.sh` passed, including billing command and missing Shopify App group cases.
- `bash tests/validate-observability-config.sh` passed.
- `git diff --check` passed.
- Repository has no `package.json`; no npm typecheck/lint/build command applies. Docker/integration validation remains developer-owned per policy and was not launched.

### Deviations

- The existing test Blueprint convention uses Render-managed `sync: false` secrets, so the validator accepts that test form while retaining strict production placeholder checks.

### Assumptions

- Existing `0.5c-512mb` worker plan and one-instance initial count are conservative starting values; independent Render worker scaling remains available.
- Background-008 source owns canonical telemetry identity (`moda-billing-worker`, namespace `moda-interact`); the Blueprint supplies common environment-specific observability configuration.

### Unresolved Issues

- Render deployment-time schema, credentials, connectivity, readiness, and capacity evidence remain to be validated in isolated test/production environments.

### Architectural Concerns

- None introduced. The billing worker has no Redis dependency and readiness does not call Shopify App Events.

## Architect Review

### Review Status

Pending architect review

### Review Notes

None

### Reviewed Files

Implementation commit `2821832` on pushed branch `task/ARCH-007-GATEWAY-001`.

### Validation Reviewed

Static Render Blueprint, negative fixture, observability, and whitespace checks listed above passed. Parent report branch is `task/ARCH-007-GATEWAY-001`; no parent submodule gitlink was staged.

### Architecture Conformance

Conforms to ARCH-007 objective and accepted Background-008 start/readiness contracts.

### Follow-up

Architect/developer to review and merge the implementation branch; system-test tasks remain enabled but were not started.
