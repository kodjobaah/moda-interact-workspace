# ARCH-002 Admin Tasks

Architecture:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Security amendment:

`docs/architecture/ARCH-002-admin-security-amendment.md`

Grafana Cloud Free presentation amendment:

`docs/architecture/ARCH-002-grafana-cloud-free-access-amendment.md`

Assigned Agent:

`moda_admin`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| ADMIN-001 | Add admin service health and readiness | Complete | GATEWAY-001 |
| ADMIN-002 | Add OpenTelemetry to admin runtime | Superseded | Replaced by ADMIN-009/010 |
| ADMIN-003 | Implement Google platform-admin authentication and session foundation | Complete | DATABASE-001 |
| ADMIN-005 | Protect privileged admin pages and server reads | Complete | ADMIN-003 |
| ADMIN-006 | Protect admin mutations and privileged route handlers | Complete | ADMIN-003 |
| ADMIN-007 | Add bounded platform-admin security audit logging | Complete | ADMIN-005, ADMIN-006, SHARED-005 |
| ADMIN-008 | Validate platform-admin security and deployment contract | Complete | ADMIN-003, ADMIN-005, ADMIN-006, ADMIN-007 |
| ADMIN-004 | Add secure private Grafana Cloud observability access | Complete | ADMIN-008, GATEWAY-006 |
| ADMIN-009 | Adopt shared observability runtime in admin process | Complete | GATEWAY-001, SHARED-010 |
| ADMIN-010 | Add bounded admin request operational metrics | Superseded | Duplicate standard HTTP telemetry; reuse framework/OpenTelemetry signal |
| ADMIN-011 | Add protected Redis Shopify queue monitor to Tenant Directory | Complete | ADMIN-005 |

Security and presentation chain:

```text
DATABASE-001
    -> ADMIN-003
        -> ADMIN-005 -----+
        -> ADMIN-006 -----+-> ADMIN-007 -> ADMIN-008
                                            |
                                            +-> GATEWAY-007 / GATEWAY-003
                                            +-> ADMIN-004 -> SYSTEM-TEST-001
```

`ADMIN-004` uses private external Grafana Cloud navigation under the current
Grafana Cloud Free architecture. It does not require iframe embedding or a
Grafana authentication proxy.

Development auth bypass is permitted only for deployment environment
`development` when `NODE_ENV` is not `production`.

The individual task file is authoritative for task state.

## Shared Observability Amendment

`ADMIN-009` consumes the shared Node observability runtime from `SHARED-010`.
Admin-owned semantic telemetry remains owned by `moda_admin`.

The parent ARCH-002 telemetry ownership boundary treats architecture-approved
framework/OpenTelemetry-generated telemetry as trusted third-party operational
telemetry. ADMIN-009 must not fail merely because those third-party spans contain
framework-defined URL/query attributes, and must not add a repository-local
sanitizer or patch to rewrite them.

`ADMIN-010` is Superseded. ADMIN-009 already enables architecture-approved
Next.js/OpenTelemetry HTTP instrumentation through the shared runtime. Generic
request count/duration/status telemetry must be reused from that standard
instrumentation rather than recreated as Moda-owned metrics.


`ADMIN-003` publication gate is satisfied by:

```text
moda-interact-database@9a286b7
```

`ADMIN-003` is Ready and must pin the Admin nested database submodule to this
exact accepted commit before implementation/build validation.


## ADMIN-003 blocker resolution

The attempt-1 block was rejected by `moda_architect`.

The nested database submodule being behind `9a286b7` is expected task input.
`ADMIN-003` owns updating the Admin gitlink to exact published commit `9a286b7`.

`ADMIN-003` is Ready.


## ADMIN-008 attempt 2

Attempt 1's implementation direction is retained, but executable final-gate
security evidence is incomplete.

`ARCH-002-ADMIN-008` is Ready for attempt 2.

Required focused evidence includes:

```text
environment fail-closed/bypass matrix
identity allow/deny/binding matrix
active-session revocation
direct mutation rejection before write
public health/readiness behavior
session/cookie contract
deployment/OAuth isolation
```

`GATEWAY-007`, `GATEWAY-003`, and `ADMIN-004` remain gated.


## ADMIN-008 attempt 3

Attempt 2 improved the focused validation harness but four final-gate items
remain unproved through the actual production security paths:

```text
existing-session revocation through privileged principal resolution
direct mutation rejection before FormData/Prisma access
actual Google first-binding persistence path
hosted cookie security attributes
```

`ARCH-002-ADMIN-008` is Ready for attempt 3.

`GATEWAY-007`, `GATEWAY-003`, and `ADMIN-004` remain gated.


## ADMIN-008 attempt 4

Attempt 3 closed the direct-mutation and hosted-cookie/session gaps.

Two final executable checks remain:

```text
resolvePlatformAdminPrincipal() active -> inactive revocation
production Google subject-binding updateMany/reread race behavior
```

`ARCH-002-ADMIN-008` is Ready for attempt 4.

`GATEWAY-007`, `GATEWAY-003`, and `ADMIN-004` remain gated.


## ADMIN-008 architect acceptance

`ARCH-002-ADMIN-008` is architect-accepted Complete after attempt 4.

Final executable evidence now covers the production-consumed principal resolver
and provider-subject binding race in addition to the previously accepted
security matrix.

This acceptance satisfies the Admin-security dependency for:

```text
GATEWAY-007
GATEWAY-003
ADMIN-004
```

No downstream task is automatically promoted or started. The architect must
re-evaluate each task's full direct dependency set after developer publication.


## Post-ADMIN-008 dependency re-evaluation

`ARCH-002-ADMIN-008` is architect-accepted Complete.

Consequences:

```text
ADMIN-004  Pending -> Ready
GATEWAY-007 dependency edge satisfied
GATEWAY-003 ADMIN-008 dependency edge satisfied
```

The Admin index has also been reconciled to the authoritative individual task
states for `ADMIN-003`, `ADMIN-005`, `ADMIN-006`, and `ADMIN-007`.

No task is started automatically.


## ADMIN-001 architect acceptance

`ARCH-002-ADMIN-001` is architect-accepted Complete.

Accepted operational endpoints:

```text
GET /health
  -> dependency-free liveness

GET /ready
  -> bounded PostgreSQL `SELECT 1` readiness
```

The behavioral correction was independently re-run by the architect:

```text
5 focused tests passed
0 failed
```

This satisfies the task's direct `GATEWAY-003` dependency edge.


## ADMIN-004 architect acceptance

`ARCH-002-ADMIN-004` is architect-accepted Complete.

Accepted behaviour:

```text
platform-admin authorisation
  -> Admin /observability
  -> validated private Grafana Cloud navigation
  -> Grafana Cloud authentication/authorisation
```

No iframe, anonymous/public dashboard, browser-visible Grafana credential, or
Grafana authentication proxy was introduced. Missing/invalid Grafana URL
configuration remains a bounded page-level condition.

This satisfies the Admin presentation dependency for:

```text
ARCH-002-SYSTEM-TEST-001
```

No downstream task is automatically claimed.


## ADMIN-009 post-acceptance validation correction

`ARCH-002-SYSTEM-TEST-002` exposed an over-specific assertion in the accepted
ADMIN-009 bootstrap test: it requires literal `SELECT 1` SQL text even though
ARCH-002/SHARED-008 require Prisma span emission, not SQL-text attribute
presence.

The same task is reopened under the architect Changes Requested path:

```text
ARCH-002-ADMIN-009
  complete -> ready (Changes Requested reissue)

ARCH-002-SYSTEM-TEST-002
  ready -> blocked
```

The correction is validation-only unless `moda_admin` proves a genuine Prisma
instrumentation defect. `GATEWAY-006` remains Complete because its OTLP/runtime
wiring contract is unchanged.

The launcher-compatible reissue state is `ready` with the prior executor/claim
cleared. `Architect Review: Changes Requested` remains in the task. The next
`/moda-task ARCH-002-ADMIN-009` claim increments the task attempt to 2.

## ADMIN-009 attempt 2 architect acceptance

`ARCH-002-ADMIN-009` is architect-accepted Complete after the narrow validation-contract correction.

The production shared-observability preload remains unchanged. The focused bootstrap test proves Prisma instrumentation from emitted `prisma:*` spans and no longer requires third-party instrumentation to expose literal `SELECT 1` SQL text. Optional SQL attributes remain subject to sensitive-value validation when present.

This satisfies the ADMIN-009 dependency edge for `ARCH-002-SYSTEM-TEST-002`. That system-test task remains Blocked only because `ARCH-002-SYSTEM-TEST-005` is still not Complete.


## ADMIN-011 initial Redis queue monitor handoff

`ARCH-002-ADMIN-011` was initially made Ready as a bounded Admin-only diagnostic
task for the current Render checkout-event investigation. Attempt 1 has since
been reviewed; the current authoritative state is recorded in the correction
section below.

It adds a protected read-only Redis/BullMQ queue monitor to the Tenant Directory
for the two existing Shopify event queues:

```text
checkout-events
  checkout-created
  checkout-updated

order-events
  order-completed
```

The refresh interval is browser-local UI state and must not create a database
change. The task may consume server-side `REDIS_URL` but must not modify the
Gateway/Render Blueprints, workers, producers, shared contracts or queue
retention semantics. Missing Redis configuration must degrade the monitor only,
not the existing Admin page.

Because successful Shopify jobs currently use `removeOnComplete: true`, this
monitor is recent/current queue evidence rather than durable processing history.
A bounded latest BullMQ event-stream timestamp/type is included so recent Redis
queue activity remains visible even when completed jobs are removed.

## ADMIN-011 Attempt 1 architect review correction

`ARCH-002-ADMIN-011` was reviewed with Architect Review status
`Changes Requested`. The previous execution claim is no longer active, so
`moda_architect` has reset the stranded correction handoff to `Ready` for a new
repository-agent claim. The next successful claim is Attempt 2.

The correction remains within the original Admin-only scope:

```text
fix first-use refresh default so absent localStorage -> 5 seconds
preserve explicitly saved Paused (0) and other valid choices
add focused refresh-initialisation coverage
remove duplicated stale Completion Report template sections
rerun task validation and return the same task to review
```

No database, gateway, Shopify, background, messaging, shared-contract or Render
Blueprint change is authorised by this correction.


## ADMIN-011 architect acceptance

`ARCH-002-ADMIN-011` is architect-accepted Complete after Attempt 2.

The accepted correction restores the required first-use 5-second refresh default
while preserving explicit Paused and other saved interval choices. The protected
read-only Redis/BullMQ monitor remains confined to `moda-interact-admin`.

Manual Render `REDIS_URL` configuration is developer-owned deployment setup and
does not reopen this implementation task.
