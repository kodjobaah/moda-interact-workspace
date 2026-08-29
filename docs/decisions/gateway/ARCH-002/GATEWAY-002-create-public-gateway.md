---
id: ARCH-002-GATEWAY-002
architecture_id: ARCH-002
title: Create public Moda Interact gateway
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-002-GATEWAY-001
enables: 
  - ARCH-002-GATEWAY-003
created: 2026-08-29
updated: 2026-08-29
---

# Create Public Moda Interact Gateway

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Create the thin public reverse-proxy gateway using only route/upstream
capabilities established by the architect-accepted prerequisite report.

## Context

GATEWAY-001 is Complete.

The thin gateway implementation can proceed independently of the application
health/startup/worker remediation tasks because routing/header/body/error
behaviour can be implemented and tested against controlled upstream fixtures.

Deployment topology remains gated later by GATEWAY-003.

## Scope

Within authorised infrastructure scope create equivalent artifacts for:

- minimal gateway container;
- reverse-proxy configuration;
- environment/config validation;
- routing/header/body/health tests;
- infrastructure documentation.

Expected responsibilities include:

- route matching;
- reverse proxying;
- request/correlation IDs;
- forwarded/provider headers;
- request-size/connection/timeouts;
- access/error logging;
- security headers;
- approved rate limiting;
- health handling;
- private-service routing.

## Out of Scope

- Shopify/recovery/messaging business logic;
- provider signature verification itself;
- database queries/business semantics;
- queue business semantics;
- CommerceAgent/LLM/billing logic;
- implementing missing upstream application capabilities.

## Requirements

Only architect-approved routes may be exposed.

Provider verification remains in owning ingress services.

The gateway must preserve headers and body behaviour required by Shopify and
Meta signature verification.

No secrets may be embedded in image/configuration.

## Work Items

- [ ] implement minimal production gateway image;
- [ ] implement route/upstream configuration;
- [ ] implement environment/config validation;
- [ ] implement health handling;
- [ ] implement routing tests;
- [ ] implement header-forwarding tests;
- [ ] implement webhook-body compatibility tests;
- [ ] implement upstream-error tests;
- [ ] create/update gateway documentation;
- [ ] record validation.

## Interfaces / Contracts

Consumes the architect-accepted GATEWAY-001 deployment prerequisite report and
any concrete prerequisite tasks added by `moda_architect`.

## Dependencies

- `ARCH-002-GATEWAY-001`
- any additional **fully-qualified** task IDs added by `moda_architect` after
  GATEWAY-001 review.

## Enables

- `ARCH-002-GATEWAY-003`

## Acceptance Criteria

- [ ] thin public gateway is implemented;
- [ ] only approved routes are exposed;
- [ ] accepted private-service targets are used;
- [ ] provider-signature headers are preserved;
- [ ] webhook body behaviour remains verification-compatible;
- [ ] gateway health is cheap and testable;
- [ ] upstream failures are predictable;
- [ ] secrets are not embedded;
- [ ] gateway configuration validates;
- [ ] container builds/starts;
- [ ] no application business logic moved into gateway.

## Validation

- [ ] reverse-proxy syntax validation;
- [ ] gateway container build;
- [ ] gateway container startup;
- [ ] gateway test suite;
- [ ] environment/config validation.

## Implementation Notes

The task file's YAML `depends_on` must be amended by `moda_architect` with any
new prerequisite task IDs before this task is moved from Pending to Ready.

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
