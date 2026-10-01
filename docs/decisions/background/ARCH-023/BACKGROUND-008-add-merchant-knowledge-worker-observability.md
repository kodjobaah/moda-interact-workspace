---
id: ARCH-023-BACKGROUND-008
architecture_id: ARCH-023
title: Add Merchant Knowledge worker observability bootstrap
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 32
executor: copilot
claimed_at: 2026-10-01T12:34:32Z
attempt: 1
depends_on:
  - ARCH-023-BACKGROUND-005
enables:
  - ARCH-023-GATEWAY-001
created: 2026-10-01
updated: 2026-10-01
---

# Add Merchant Knowledge worker observability bootstrap

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Make the accepted dedicated Merchant Knowledge worker initialize the repository's existing shared worker observability runtime before loading its production entrypoint, without changing Merchant Knowledge business processing or deployment topology.

## Context

`ARCH-023-GATEWAY-001` Attempt 1 stopped at its explicit R17 boundary after inspecting the accepted Background worker start contract:

```text
npm run start:merchant-knowledge-worker
  -> node dist/entrypoints/merchant-knowledge.js
```

The accepted sibling Background workers already preload repository-owned observability profiles before their compiled entrypoints. The Merchant Knowledge worker has no corresponding preload, so deploying the accepted command would omit the normal worker observability bootstrap.

The existing ARCH-002 Background observability architecture is authoritative for the implementation pattern. This task extends that already-adopted pattern to the fourth independently deployable worker identity:

```text
service.name = moda-merchant-knowledge-worker
service.namespace = moda-interact
```

The production Gateway command remains `npm run start:merchant-knowledge-worker`; Gateway must not invent a replacement command or initialize application telemetry itself.

## Scope

Primary authorized files:

```text
package.json
observability/merchant-knowledge.mjs
Dockerfile                                      # only if required to package the new preload
src/entrypoints/merchant-knowledge.ts           # only if existing shutdown/failure cleanup must be wired to the shared runtime
src/runtime/observability.ts                    # only if the existing repository helper requires the new worker profile

tests/unit/runtime/observability-startup.test.ts
tests/unit/runtime/entrypoint-isolation.test.ts
tests/unit/entrypoints/merchant-knowledge.test.ts
```

Modify another existing observability/startup-focused test only when required by the repository's actual decomposition.

## Out of Scope

- Merchant Knowledge acquisition, normalization, chunking, embedding, promotion or entitlement logic.
- Queue/event contract changes.
- Database schema/migration changes.
- New telemetry providers, exporters, samplers, collectors or backends.
- New service-local NodeSDK/provider/exporter stacks.
- Gateway Blueprint/configuration changes.
- Renaming the accepted Gateway-facing package script.
- Changing `moda-merchant-knowledge-worker` to an environment-specific `service.name`.
- Duplicating BullMQ or GenAI instrumentation already owned by existing shared/runtime paths.
- Starting or modifying `ARCH-023-GATEWAY-001`.

## Requirements

### R1 — preserve the accepted production command contract

Keep the externally consumed package-script name exactly:

```text
start:merchant-knowledge-worker
```

Its implementation must preload the Merchant Knowledge observability module before loading:

```text
dist/entrypoints/merchant-knowledge.js
```

Use the same Node preload mechanism already used by the accepted sibling Background worker commands. Gateway must continue to invoke only:

```text
npm run start:merchant-knowledge-worker
```

### R2 — shared observability runtime only

Create one repository-owned Merchant Knowledge preload/profile using:

```text
@modainteract/moda-interact-shared/observability/node
```

with exact logical identity:

```text
service.name = moda-merchant-knowledge-worker
service.namespace = moda-interact
```

Environment identity remains resolved by the shared runtime. Do not encode `test`, `production`, Render service names or another environment suffix into `service.name`.

### R3 — instrumentation profile

Use the existing Background generic worker profile needed by the Merchant Knowledge runtime:

```text
HTTP/fetch/Undici = enabled
Prisma            = enabled
```

Preserve existing BullMQ/queue telemetry ownership. Do not create duplicate BullMQ instrumentation or add GenAI semantic telemetry merely because this worker performs embedding calls.

### R4 — initialization ordering and singleton ownership

The shared runtime must initialize before the compiled Merchant Knowledge worker/Prisma/application modules are loaded.

Repeated initialization in one process must continue to resolve to the shared runtime's singleton ownership rather than creating competing SDK/provider/exporter instances.

### R5 — disabled-runtime and failure isolation

With `OTEL_SDK_DISABLED=true`, the exact production command must remain runnable through the existing readiness/start lifecycle without attempting hosted telemetry export.

Observability initialization/export failure must not become a business-correctness dependency or weaken existing readiness failure behavior.

### R6 — shutdown ownership

Inspect the accepted Merchant Knowledge entrypoint's existing resource/observability shutdown path. Ensure a process that successfully initializes the shared runtime flushes/shuts it down through the same accepted repository lifecycle used by sibling workers after owned worker/scheduler resources drain, including pre-consumer readiness failure where applicable.

Do not refactor unrelated shutdown behavior.

### R7 — production packaging

If the Background production image copies observability preload files explicitly, include `observability/merchant-knowledge.mjs` in the same bounded packaging path. Do not otherwise redesign the Docker image.

### R8 — focused regression

Focused tests must prove at minimum:

1. `start:merchant-knowledge-worker` preloads the Merchant Knowledge observability module before `dist/entrypoints/merchant-knowledge.js`;
2. the exact service identity is `moda-merchant-knowledge-worker`;
3. generic HTTP/fetch/Undici and Prisma instrumentation are requested through the shared runtime;
4. no service-local SDK/provider/exporter implementation is introduced;
5. disabled-runtime startup preserves the existing readiness/failure contract;
6. the production image/package includes the preload when explicit packaging is required;
7. sibling worker start commands/identities remain unchanged.

## Work Items

- [ ] Add the Merchant Knowledge shared-runtime preload/profile.
- [ ] Preload it from the existing `start:merchant-knowledge-worker` command.
- [ ] Wire existing shutdown/failure cleanup only if required by the accepted runtime lifecycle.
- [ ] Package the preload in the production image if the Dockerfile requires explicit inclusion.
- [ ] Add focused startup/identity/disablement/isolation regressions.
- [ ] Run the bounded validation contract.

## Interfaces / Contracts

Consumes the accepted shared observability runtime established by ARCH-002 and the accepted final Merchant Knowledge worker from:

```text
ARCH-023-BACKGROUND-005
```

Produces the Background-owned startup capability required by:

```text
ARCH-023-GATEWAY-001 R17
```

Canonical deployment-facing contract remains:

```text
repo:          moda-interact-background
command:       npm run start:merchant-knowledge-worker
service.name:  moda-merchant-knowledge-worker
```

## Dependencies

- `ARCH-023-BACKGROUND-005`

## Enables

- `ARCH-023-GATEWAY-001`

## Acceptance Criteria

- [ ] Merchant Knowledge production startup initializes shared observability before application/Prisma worker imports.
- [ ] Exact logical service identity is `moda-merchant-knowledge-worker` with `service.namespace=moda-interact`.
- [ ] Existing shared runtime owns providers/exporters/sampling/environment identity.
- [ ] Required generic HTTP/fetch/Undici and Prisma instrumentation is enabled without duplicate BullMQ/GenAI instrumentation.
- [ ] Existing worker business logic, queue contracts, readiness identity and scheduler behavior are unchanged.
- [ ] `OTEL_SDK_DISABLED=true` preserves the existing startup/readiness failure behavior.
- [ ] Shared runtime shutdown is reached through the accepted worker lifecycle where required.
- [ ] Production packaging contains the new preload when explicit packaging is necessary.
- [ ] Sibling worker start commands and service identities remain unchanged.

## Validation

Run only validation relevant to this bounded corrective task:

- [ ] focused observability-startup / entrypoint-isolation / Merchant Knowledge entrypoint tests
- [ ] exact production-command disabled-runtime subprocess probe
- [ ] TypeScript/typecheck or repository equivalent
- [ ] production build
- [ ] changed-file lint/diagnostics
- [ ] `git diff --check`

If the broader repository suite is run and reports unrelated failures, record/classify them without expanding task scope.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, clear the active claim, return to `moda_architect` and STOP.

Do not begin or modify GATEWAY-001.

## Implementation Notes

Follow the already-accepted ARCH-002 Background observability pattern rather than creating a fourth observability architecture. A small worker-specific preload/profile is expected; the shared package remains the provider/exporter/sampler owner.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
