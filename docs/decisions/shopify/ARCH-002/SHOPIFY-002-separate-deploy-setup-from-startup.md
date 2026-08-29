---
id: ARCH-002-SHOPIFY-002
architecture_id: ARCH-002
title: Separate database setup from Shopify replica startup
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-002-GATEWAY-001
enables: []
created: 2026-08-29
updated: 2026-08-29
---

# Separate database setup from Shopify replica startup

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Make `moda-interact` safe for horizontal replica startup by separating migration/seed operations from normal application process startup.

## Context

Discovery confirmed `docker-start -> setup -> prisma migrate deploy + prisma seed -> start`, so every replica start can run migration and seed work.

## Scope

- provide an application start command that starts only the web runtime;
- expose a separate migration command suitable for Render pre-deploy execution;
- keep seed as an explicit controlled initialization command;
- update repository deployment documentation/scripts accordingly.

## Out of Scope

- modifying Render Blueprint;
- changing migration contents;
- changing seed business data;
- gateway implementation.

## Requirements

Normal replica startup must not run database seed.

Migration execution must be callable independently from application startup.

Seed must not execute automatically on ordinary production replica restart.

Existing local development workflows may retain explicit setup helpers if clearly separated from production startup.

## Work Items

- [ ] separate web startup from setup;
- [ ] expose migration-only command;
- [ ] expose/document explicit seed command;
- [ ] update tests/docs as applicable;
- [ ] verify replica start does not execute migration/seed.

## Interfaces / Contracts

Provides startup and migration commands consumed by `ARCH-002-GATEWAY-003` Render Blueprint configuration.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

None.

## Acceptance Criteria

- [ ] normal service startup performs no seed;
- [ ] migration command is independently executable;
- [ ] seed is independently executable;
- [ ] existing application starts successfully;
- [ ] production deployment documentation clearly distinguishes build, migrate, seed and start.

## Validation

- [ ] relevant tests;
- [ ] typecheck;
- [ ] production build;
- [ ] command-level verification.

## Implementation Notes

ARCH-002 intends Render `preDeployCommand` for migration. GATEWAY-003 owns that infrastructure wiring.

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

None.

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
