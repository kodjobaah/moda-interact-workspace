---
id: ARCH-007-GATEWAY-001
architecture_id: ARCH-007
title: Deploy independently scalable billing worker in Render blueprints
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: complete
priority: 140
executor: null
claimed_at: null
attempt: 1
depends_on: 
  - ARCH-007-BACKGROUND-008
enables: 
  - ARCH-007-SYSTEM-TEST-002
  - ARCH-007-SYSTEM-TEST-003
created: 2026-09-07
updated: 2026-09-08
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

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

Implementation commit `2821832` on `task/ARCH-007-GATEWAY-001`:

- `render.test.yaml`
- `render.production.yaml`
- `tests/validate-render-blueprints.sh`
- `tests/validate-render-blueprints-negative.sh`
- `docs/render-topology.md`

### Work Completed

- Added `moda-billing-worker-test` and `moda-billing-worker-production` as
  private Render worker services using the accepted Background repository and
  exact `npm run start:billing-worker` command.
- Configured one conservative initial instance per environment while preserving
  independent horizontal scaling.
- Attached each billing worker to the common observability/environment group,
  the existing Shopify Partner/App configuration group and the corresponding
  environment-specific PostgreSQL connection.
- Kept the billing worker Redis-independent and without public domains or web
  health-check exposure.
- Documented `npm run readiness:billing-worker`, PostgreSQL-only readiness and
  deployment ordering in `docs/render-topology.md`.
- Extended positive Blueprint validation and added billing-specific negative
  fixtures.

### Validation Results

Passed:

- `bash tests/validate-render-blueprints.sh`
- `bash tests/validate-render-blueprints-negative.sh`
- `bash tests/validate-observability-config.sh`
- `git diff --check`

The Gateway repository has no `package.json`, so no npm typecheck/lint/build
command applies. Render deployment-time connectivity/credential/capacity
validation remains deployment/system-test evidence.

### Deviations

The existing test Blueprint convention uses Render-managed `sync: false`
secrets; no secret values are committed.

### Assumptions

- The existing `0.5c-512mb` worker plan and one initial instance are the
  conservative starting topology.
- Background owns the canonical `moda-billing-worker` telemetry service identity
  and PostgreSQL-only readiness behavior.

### Unresolved Issues

Render deployment-time schema, credentials, connectivity and measured capacity
remain to be validated in the appropriate deployment/system-test stage.

### Architectural Concerns

None introduced.

## Architect Review

### Review Status

Accepted

### Review Notes

#### Attempt 1 — Accepted

Attempt 1 is architect-accepted Complete.

The implementation satisfies the GATEWAY-001 deployment contract:

1. `moda-billing-worker-test` and `moda-billing-worker-production` are private
   Render `worker` services, not public web services.
2. Both use the accepted Background repository and exact
   `npm run start:billing-worker` command.
3. Each starts at one conservative instance and remains independently scalable.
4. Each receives the common environment/observability group, the existing
   Shopify Partner/App configuration group, and the environment-specific
   PostgreSQL connection.
5. Neither billing worker receives the Redis group.
6. The topology documentation records
   `npm run readiness:billing-worker` and PostgreSQL-only readiness without
   inventing a live Shopify provider readiness dependency.
7. Positive validation covers worker type, runtime, repository, command,
   private exposure, initial scale, exact environment-group attachments and
   environment-specific database wiring.
8. Negative fixtures cover invalid billing command and missing Shopify
   Partner/App group, while the exact attachment checks also reject accidental
   Redis or unrelated group attachment.
9. Test and production remain distinguishable through their environment-specific
   groups and database resources, with no committed secret values.

The architect reran the supplied Gateway validation scripts from the uploaded
repository and all passed.

The accepted Background-008 contract was cross-checked: the package exposes
`start:billing-worker` / `readiness:billing-worker`, and billing readiness
requires PostgreSQL only.

No further implementation changes are required for
`ARCH-007-GATEWAY-001`.

### Reviewed Files

Implementation represented by Gateway commit `2821832` and the supplied
workspace archive:

- `moda-interact-gateway/render.test.yaml`
- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/tests/validate-render-blueprints.sh`
- `moda-interact-gateway/tests/validate-render-blueprints-negative.sh`
- `moda-interact-gateway/tests/validate-observability-config.sh`
- `moda-interact-gateway/docs/render-topology.md`

Parent report evidence was independently verified at workspace commit
`31c84e5bea7715c6705519a6aba91a0d67adbf58`.

### Validation Reviewed

- Render Blueprint validation: passed.
- Negative Blueprint fixtures: passed.
- Observability validation: passed.
- Completion Report `git diff --check`: passed.
- Render deployment-time credentials/connectivity/platform validation remains
  system/deployment evidence and is not an implementation acceptance blocker.

### Architecture Conformance

Accepted. The billing worker is independently deployable, private,
PostgreSQL-recoverable, Redis-independent and aligned with the accepted
Background-008 runtime contract.

### Follow-up

`ARCH-007-GATEWAY-001` is Complete.

`ARCH-007-SYSTEM-TEST-002` and `ARCH-007-SYSTEM-TEST-003` now have
GATEWAY-001 as a satisfied dependency, but both remain Pending /
manual-terminal-gated. Do not auto-start or auto-promote either system-test task.

Developer/user retains ownership of merging/pushing implementation `main` and
integrating the parent workspace state.
