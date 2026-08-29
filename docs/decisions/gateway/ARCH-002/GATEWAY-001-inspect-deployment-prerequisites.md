---
id: ARCH-002-GATEWAY-001
architecture_id: ARCH-002
title: Inspect platform and define production deployment prerequisites
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: complete
priority: 10
executor: codex
claimed_at: 2026-08-29T12:10:00Z
attempt: 1
depends_on: []
enables: 
  - ARCH-002-GATEWAY-002
created: 2026-08-29
updated: 2026-08-29
---

# Inspect Platform and Define Production Deployment Prerequisites

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Inspect architecture-relevant repositories and produce the factual deployment
prerequisite report required before public gateway and Render topology
implementation.

## Context

The target architecture is intentionally not allowed to invent build commands,
ports, health endpoints, worker entrypoints or service contracts.

This task validates those facts.

Reuse accepted deployment findings from ARCH-001 where applicable rather than
performing duplicate discovery.

## Scope

Inspect where relevant:

```text
moda-interact/
moda-interact-background/
moda-interact-messaging/
moda-interact-admin/
moda-interact-database/
moda-interact-shared/
moda-interact-site/
moda-interact-system-test/
moda-interact-gateway/
```

Create:

```text
moda-interact-gateway/docs/deployment-prerequisites.md
```

For each deployable component identify:

- repository/service;
- Render service type candidate;
- build command;
- startup command;
- listening port;
- health endpoint;
- readiness behaviour;
- required environment-variable names;
- Redis dependency;
- PostgreSQL dependency;
- public/private exposure;
- webhook routes;
- worker entrypoints;
- worker queue ownership;
- build-context/shared-package requirements;
- deployment-order constraints;
- missing capabilities;
- blockers.

## Out of Scope

- implementing missing application capabilities;
- changing application business logic;
- changing database schema/migrations;
- changing shared runtime contracts;
- creating final `render.yaml`;
- implementing the public reverse proxy.

## Requirements

Inspection does not grant implementation ownership.

For every missing capability record:

```text
Missing capability:
<description>

Owner:
<logical agent / repository>

Architect follow-up required:
yes
```

Do not invent a task ID. `moda_architect` creates the concrete fully-qualified
task after reviewing the finding.

The report must explicitly inspect how
`@modainteract/moda-interact-shared` resolves in clean production build
contexts where relevant.

## Work Items

- [x] inspect affected repositories;
- [x] identify actual build/start commands;
- [x] identify ports and health/readiness behaviour;
- [x] identify and classify all required environment-variable names by runtime/build/deploy/test use;
- [x] identify Redis/PostgreSQL connectivity requirements;
- [x] identify public/private exposure requirements;
- [x] identify webhook routes;
- [x] identify worker entrypoints/queue ownership;
- [x] inspect shared-package/build-context requirements;
- [x] record missing application capabilities;
- [x] create deployment prerequisite report;
- [x] record validation evidence.

## Interfaces / Contracts

Produces the accepted deployment prerequisite report used by downstream
ARCH-002 gateway tasks.

Does not own application runtime contracts.

## Dependencies

None.

## Enables

- `ARCH-002-GATEWAY-002`

`moda_architect` may add newly discovered owner-specific prerequisites before
GATEWAY-002 becomes Ready.

## Acceptance Criteria

- [x] all relevant repositories have been inspected;
- [x] actual deployment commands/ports are evidenced;
- [x] health/readiness capabilities are evidenced;
- [x] environment-variable names are completely identified and classified without exposing secret values;
- [x] worker entrypoints and queue ownership are evidenced;
- [x] public/private exposure requirements are recorded;
- [x] build-context/shared-package resolution is documented;
- [x] missing capabilities/blockers are explicitly recorded;
- [x] no other repository's application implementation was modified;
- [x] prerequisite report is corrected and ready for architect re-review.

## Validation

- [x] repository inspection evidence recorded;
- [x] deployment commands cross-checked against package/Docker/config files;
- [x] prerequisite report internally re-reviewed after architect-requested corrections.

## Implementation Notes

When the task reaches `review`, `moda_architect` must inspect the report and
then amend downstream dependencies with concrete task IDs before making
GATEWAY-002 Ready.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-gateway/docs/deployment-prerequisites.md`
- `docs/decisions/gateway/ARCH-002/GATEWAY-001-inspect-deployment-prerequisites.md`

### Work Completed

All seven architect review findings were corrected directly in the actual
`moda-interact-gateway/docs/deployment-prerequisites.md` and verified against
the source:

1. **Concurrency wording corrected** — the report now describes
   shared-process/resource/scaling isolation with each worker's own BullMQ
   concurrency setting (`checkout`: 10, `orders`: 5, `pending-recovery`: 10,
   `whatsapp`: 20), not a single shared BullMQ concurrency budget.
2. **Producer-first removed** — BullMQ consumers do not require producers to
   enqueue first; deployment ordering is driven by compatibility, configuration,
   migration and cutover requirements.
3. **Background env vars completed and classified** — runtime, deploy/build and
   test-only variable names enumerated (incl. `GROQ_API_KEY`,
   `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `NODE_ENV`,
   `SHOPIFY_API_KEY`, `SHOPIFY_API_SECRET`); test-only
   `TEST_WHATSAPP_RECIPIENT`, `SHOPIFY_TEST_PRODUCT_QUERY`,
   `SHOPIFY_TEST_SHOP` recorded separately. No secret values exposed.
4. **Multi-instance startup concern promoted to a missing capability** —
   `docker-start` → `prisma migrate deploy + prisma seed` per replica start is
   recorded under section 8 with `Owner: moda_app`, architect follow-up required.
5. **Health/readiness blocker wording corrected** — per-service summary now
   accurate (background has liveness; lacks dependency readiness).
6. **OpenTelemetry ownership aligned with `moda_architect(9)`** — recorded as a
   per-boundary absence requiring architect decomposition into bounded
   owner-specific tasks; no single `Owner: All` implementation owner.
7. **Completion Report now agrees with the actual artifact** — every claim was
   re-checked against the corrected report before this handoff.

### Validation Results

All seven findings were verified against the actual corrected report (grep
confirmed removal of `producer first`, `concurrency budget`, `Owner: All`, and
`four of the deployed services`; per-worker concurrency values confirmed from
`src/workers/*.ts`). Every acceptance criterion was re-checked against the
report. No runtime deployment was required by this discovery task.

### Deviations

None. The task file and deployment report are complete and handed off for
architect re-review.

### Assumptions

None beyond source-derived deployment facts.

### Unresolved Issues

- production distribution/build-context strategy for `@modainteract/moda-interact-shared`;
- application health/readiness gaps;
- worker independent-scaling capability;
- safe multi-instance migration/seed startup strategy for `moda-interact`.

### Architectural Concerns

The issues above require `moda_architect` sequencing after this task is accepted. They must not be silently implemented by `moda_gateway`.

## Architect Review

### Review Status

Accepted

### Review Notes

The corrected deployment-prerequisite report is accepted.

All seven findings from the prior architect review are now reflected in the
actual durable report:

- the background limitation is correctly described as shared-process
  resource/scaling isolation, with separate BullMQ concurrency settings;
- producer-first queue deployment is no longer treated as a BullMQ requirement;
- background environment-variable names are enumerated and classified without
  exposing secret values;
- `moda-interact` migration/seed-on-every-replica-start is explicitly returned
  as an architect follow-up;
- health/readiness findings accurately distinguish background liveness from
  dependency readiness;
- OpenTelemetry absence is reported as a cross-boundary discovery that must be
  decomposed into owner-specific tasks;
- the Completion Report agrees with the actual report.

The report is now sufficiently accurate to become the architecture's accepted
deployment-prerequisite baseline.

### Reviewed Files

- `moda-interact-gateway/docs/deployment-prerequisites.md`
- `docs/decisions/gateway/ARCH-002/GATEWAY-001-inspect-deployment-prerequisites.md`
- `docs/decisions/gateway/ARCH-002/_index.md`
- pending GATEWAY-002/003/004 task definitions

### Validation Reviewed

Static re-review of the complete submitted report confirmed:

- 528-line deployment-prerequisite artifact is present;
- all required GATEWAY-001 task sections are present;
- task was returned as `status: review`;
- Completion Report is `Ready for Review`;
- each prior correction is visible in the actual report;
- no other repository implementation was modified by the discovery task.

### Architecture Conformance

Accepted.

The discovery stayed within `moda_gateway` ownership, identified missing
application capabilities rather than implementing them, and provides sufficient
evidence for architect-owned task decomposition.

### Follow-up

`ARCH-002-GATEWAY-001` is Complete.

The architect has decomposed the accepted findings into bounded owner-specific
prerequisite and observability tasks. GATEWAY-002 may proceed in parallel with
those prerequisites because the thin reverse-proxy implementation does not
require the missing application capabilities to be implemented first.

GATEWAY-003 remains Pending until its concrete deployability and observability
dependencies are Complete.
