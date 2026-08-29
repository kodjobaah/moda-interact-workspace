---
id: ARCH-002-GATEWAY-003
architecture_id: ARCH-002
title: Create Render production deployment topology
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-GATEWAY-002
  - ARCH-002-GATEWAY-005
  - ARCH-002-GATEWAY-006
  - ARCH-002-SHOPIFY-001
  - ARCH-002-SHOPIFY-002
  - ARCH-002-MESSAGING-001
  - ARCH-002-ADMIN-001
  - ARCH-002-BACKGROUND-001
  - ARCH-002-BACKGROUND-002
enables: 
  - ARCH-002-GATEWAY-004
created: 2026-08-29
updated: 2026-08-29
---

# Create Render Production Deployment Topology

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Create the version-controlled Render deployment topology using actual
capabilities accepted by the architect, with `moda-interact-gateway/render.yaml`
as the canonical Blueprint source of truth.

## Context

The proposed target is a public gateway with private application HTTP services
and BullMQ-distributed workers.

Actual service/worker decomposition must come from accepted prerequisites.

## Scope

The canonical Render Blueprint for Moda Interact is owned by `moda_gateway` and
must be created or modified at:

```text
moda-interact-gateway/render.yaml
```

This file is inside the `moda-interact-gateway` repository, so no workspace-level
cross-repository write exception is required.

Configure/document where supported:

- public gateway service;
- private Shopify application service;
- private messaging ingress;
- private admin service where deployed;
- actual supported worker services:
  - `moda-shopify-event-worker`;
  - `moda-recovery-worker`;
  - `moda-messaging-worker`;
- HTTP health checks;
- Render private service references;
- PostgreSQL infrastructure wiring;
- external Redis Cloud secret wiring;
- environment-variable declarations;
- deployment order;
- `moda-interact` pre-deploy migration wiring (seed excluded from normal replica startup);
- scaling/capacity classifications;
- cost assumptions.

## Out of Scope

- inventing worker commands;
- adding HTTP load balancers in front of BullMQ workers;
- provisioning Redis Cloud as Render Redis when architecture specifies external
  Redis Cloud;
- application schema/migration implementation;
- committing secret values.

## Requirements

Use Render-native service load balancing for ordinary HTTP services.

Use Redis/BullMQ for worker work distribution.

Planning instance counts must be labelled ASSUMED/ESTIMATED unless measured.

Only actual required environment variables should be declared/documented.

Use the workspace superproject as the source repository for services that need
sibling submodule build inputs. Use the accepted workspace-root Docker context
strategy from GATEWAY-005.

`moda-interact-admin` may use Render's native Node runtime; ARCH-002 does not
require a Dockerfile solely for that service.

OpenTelemetry/OTLP declarations must consume GATEWAY-006's accepted environment
and transport model.

## Work Items

- [ ] create/update `moda-interact-gateway/render.yaml`;
- [ ] configure public gateway;
- [ ] configure accepted private services;
- [ ] configure actual worker services;
- [ ] configure health checks;
- [ ] configure internal service references;
- [ ] wire Redis/PostgreSQL environment names securely;
- [ ] document deployment order;
- [ ] document scaling/cost assumptions;
- [ ] record validation.

## Interfaces / Contracts

Consumes:

- accepted public-gateway implementation;
- accepted deployment-prerequisite report;
- any application prerequisite tasks added by the architect.

## Dependencies

- `ARCH-002-GATEWAY-002`
- `ARCH-002-GATEWAY-005`
- `ARCH-002-GATEWAY-006`
- `ARCH-002-SHOPIFY-001`
- `ARCH-002-SHOPIFY-002`
- `ARCH-002-MESSAGING-001`
- `ARCH-002-ADMIN-001`
- `ARCH-002-BACKGROUND-001`
- `ARCH-002-BACKGROUND-002`

## Enables

- `ARCH-002-GATEWAY-004`

## Acceptance Criteria

- [ ] `moda-interact-gateway/render.yaml` represents accepted topology;
- [ ] public/private exposure matches architecture;
- [ ] worker definitions use real supported entrypoints;
- [ ] no HTTP load balancer fronts BullMQ workers;
- [ ] Redis Cloud remains external where required;
- [ ] PostgreSQL ownership remains with `moda_database`;
- [ ] no secrets are committed;
- [ ] health paths match actual services;
- [ ] environment declarations match actual requirements;
- [ ] deployment order is documented;
- [ ] scaling/cost claims are correctly classified.

## Validation

- [ ] Render Blueprint/config validation where practical;
- [ ] service mapping review;
- [ ] command/port/health cross-check;
- [ ] secret scan/review;
- [ ] topology documentation review.

## Implementation Notes

This task may only use worker/service decomposition actually supported by
accepted application prerequisites.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond those explicitly stated by the task.

### Unresolved Issues

None recorded yet.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
