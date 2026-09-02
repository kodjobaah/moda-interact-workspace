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
| ADMIN-003 | Implement Google platform-admin authentication and session foundation | Pending | DATABASE-001 |
| ADMIN-005 | Protect privileged admin pages and server reads | Pending | ADMIN-003 |
| ADMIN-006 | Protect admin mutations and privileged route handlers | Pending | ADMIN-003 |
| ADMIN-007 | Add bounded platform-admin security audit logging | Pending | ADMIN-005, ADMIN-006, SHARED-005 |
| ADMIN-008 | Validate platform-admin security and deployment contract | Pending | ADMIN-003, ADMIN-005, ADMIN-006, ADMIN-007 |
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
