# ARCH-002 Direct Loki Shared Logger Amendment

## Decision

Direct Loki delivery is a reusable logging transport and belongs in
`moda-interact-shared`, not in an individual service repository.

The shared logging fan-out becomes:

```text
application
    |
    v
@modainteract/moda-interact-shared/logging
    |
    +--> structured stdout
    +--> OpenTelemetry Logs API
    +--> optional direct Loki
```

## Runtime boundary

The application-facing `./logging` entry remains lightweight.

Winston and `winston-loki` are Node-only implementation details exposed only
through bootstrap APIs in:

```text
@modainteract/moda-interact-shared/logging/node
```

## Infrastructure boundary

The shared library owns **how** to deliver a direct Loki log.

Gateway/deployment infrastructure owns **which endpoint and credentials** are
injected into test/production processes.

## Labels

Only static low-cardinality identity labels are indexed by default:

```text
service_namespace
service_name
environment
```

Dynamic event/customer/job/request identifiers remain in safe structured log
content and never become default Loki stream labels.

## Release sequence

Do not publish SHARED-004 alone.

```text
SHARED-004  accepted
    |
    v
SHARED-006  direct Loki
    |
    v
SHARED-005  one public 0.3.0 release
```
