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

# Separate Database Setup from Shopify Replica Startup

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Make `moda-interact` safe for horizontally scaled deployment by separating
build, migration, seed and normal web-process startup.

The resulting commands must be usable by both the test and production
Blueprints.

## Context

Discovery confirmed the existing Docker startup sequence could run:

```text
prisma migrate deploy
prisma seed
application start
```

for every replica start.

That is not an acceptable normal restart/scaling contract.

ARCH-002 requires:

```text
build
  ->
pre-deploy migration
  ->
replica start
```

with seeding remaining explicit/controlled.

## Scope

- provide a production web start command that starts only the web runtime;
- expose a migration-only command suitable for Render `preDeployCommand`;
- keep seed as an explicit controlled initialization command;
- ensure normal service restart/scale-out does not run migration or seed;
- update deployment documentation/scripts accordingly;
- keep commands environment-neutral so the same application artifact can be
  deployed to test and production.

## Out of Scope

- modifying Render Blueprint files;
- changing migration contents;
- changing seed business data;
- choosing whether production should contain seed data;
- gateway implementation;
- database schema redesign.

## Requirements

Normal replica startup must not execute migration.

Normal replica startup must not execute seed.

Migration execution must be independently callable and must use the environment's
configured `DATABASE_URL`.

Seed must be independently callable and must never execute automatically on an
ordinary service restart, horizontal scale-out or rolling deploy.

The commands used by GATEWAY-003 must work for both:

```text
render.test.yaml
render.production.yaml
```

Test and production must use their own database configuration.

Do not hard-code a test or production database URL.

Existing local development workflows may retain explicit setup helpers if they
are clearly separate from production deployment commands.

The application command contract must make these four phases distinguishable:

```text
build
migrate
seed
start
```

## Work Items

- [ ] separate web startup from setup/migration/seed;
- [ ] expose migration-only command;
- [ ] expose/document explicit seed command;
- [ ] ensure normal Docker/Render start launches only the web runtime;
- [ ] add command-level tests or deterministic verification;
- [ ] update deployment documentation;
- [ ] verify replica restart/scale-out command does not execute migration/seed.

## Interfaces / Contracts

Provides commands consumed by:

```text
ARCH-002-GATEWAY-003
```

GATEWAY-003 owns the environment-specific `preDeployCommand` wiring.

The intended infrastructure sequence is:

```text
build
  ->
preDeployCommand: migration-only
  ->
startCommand/dockerCommand: web runtime only
```

Seed is never part of that automatic sequence.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

None.

## Acceptance Criteria

- [ ] normal service startup performs no migration;
- [ ] normal service startup performs no seed;
- [ ] migration command is independently executable;
- [ ] seed command is independently executable;
- [ ] existing application starts successfully;
- [ ] commands do not hard-code an environment/database;
- [ ] test and production can use the same command contract;
- [ ] production deployment documentation clearly distinguishes build, migrate,
      seed and start.

## Validation

- [ ] relevant tests;
- [ ] typecheck;
- [ ] production build;
- [ ] command-level verification;
- [ ] prove normal start does not invoke migration;
- [ ] prove normal start does not invoke seed.

## Implementation Notes

ARCH-002 intends Render `preDeployCommand` for migration on paid application
services. GATEWAY-003 owns that infrastructure wiring.

If a chosen test service plan does not support a required deployment feature,
return that infrastructure constraint to `moda_architect` rather than changing
the application command semantics.

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
