---
id: ARCH-002-GATEWAY-005
architecture_id: ARCH-002
title: Enable workspace-root production build context
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: ready
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-002-GATEWAY-001
enables: []
created: 2026-08-29
updated: 2026-08-29
---

# Enable workspace-root production build context

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Make `moda-interact` and `moda-interact-background` clean production builds consume `moda-interact-shared` from the workspace checkout without publishing the package to a registry.

## Context

ARCH-002 selects workspace-superproject build context. Render can clone Git submodules and supports repository-root Docker build context for monorepo services.

## Scope

This task explicitly authorises `moda_gateway` to modify infrastructure build files:

- `moda-interact/Dockerfile`;
- `moda-interact-background/Dockerfile`;
- relevant `.dockerignore` files;
- gateway deployment/build documentation.

Configure clean builds so the sibling `moda-interact-shared` package is present,
built as required and resolvable by the existing `file:../moda-interact-shared`
dependency when the Docker build context is the workspace root.

## Out of Scope

- publishing `moda-interact-shared` to npm/GitHub Packages;
- modifying shared runtime contracts;
- application business logic;
- Render service topology itself.

## Requirements

The resulting images must contain only required runtime artifacts.

Do not copy `.git`, local secrets, node_modules or unrelated repository content into final runtime layers.

A clean build from workspace root must be reproducible.

If this strategy proves technically incompatible with npm/package-lock behaviour, return the task Blocked with evidence rather than silently switching to registry publication.

## Work Items

- [ ] update app Docker build for workspace-root context;
- [ ] update background Docker build for workspace-root context;
- [ ] build shared package at the correct stage;
- [ ] add/update dockerignore rules;
- [ ] run clean app image build;
- [ ] run clean background image build;
- [ ] document required `dockerContext`/`dockerfilePath` settings.

## Interfaces / Contracts

Consumes the existing canonical package dependency; produces Docker/build inputs for GATEWAY-003.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

None.

## Acceptance Criteria

- [ ] clean app Docker build succeeds from workspace root;
- [ ] clean background Docker build succeeds from workspace root;
- [ ] both consume the canonical shared build;
- [ ] no registry publication is required;
- [ ] no secrets/unnecessary repos are copied into runtime images;
- [ ] business source behaviour is unchanged.

## Validation

- [ ] Docker build app;
- [ ] Docker build background;
- [ ] image/runtime smoke checks;
- [ ] secret/build-context review.

## Implementation Notes

The canonical Blueprint later declares `dockerContext: .` and service-specific `dockerfilePath` from the superproject repository.

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
