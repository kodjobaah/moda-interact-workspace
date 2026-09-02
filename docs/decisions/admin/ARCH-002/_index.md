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
| ADMIN-001 | Add admin service health and readiness | Ready | GATEWAY-001 |
| ADMIN-002 | Add OpenTelemetry to admin runtime | Superseded | Replaced by ADMIN-009/010 |
| ADMIN-003 | Implement Google platform-admin authentication and session foundation | Ready | DATABASE-001 |
| ADMIN-005 | Protect privileged admin pages and server reads | Pending | ADMIN-003 |
| ADMIN-006 | Protect admin mutations and privileged route handlers | Pending | ADMIN-003 |
| ADMIN-007 | Add bounded platform-admin security audit logging | Pending | ADMIN-005, ADMIN-006, SHARED-005 |
| ADMIN-008 | Validate platform-admin security and deployment contract | Complete | ADMIN-003, ADMIN-005, ADMIN-006, ADMIN-007 |
| ADMIN-004 | Add secure private Grafana Cloud observability access | Pending | ADMIN-008, GATEWAY-006 |
| ADMIN-009 | Adopt shared observability runtime in admin process | Complete | GATEWAY-001, SHARED-010 |
| ADMIN-010 | Add bounded admin request operational metrics | Superseded | Duplicate standard HTTP telemetry; reuse framework/OpenTelemetry signal |

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
