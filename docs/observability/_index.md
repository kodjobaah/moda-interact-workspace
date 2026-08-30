# Moda Interact Observability Conventions

Architecture-owned operational observability documentation.

## Guides

- [Shared structured logging](shared-logging.md)

## Ownership

Application/runtime repositories emit operational signals.

`moda-interact-shared` owns reusable backend-neutral logging primitives.

Service/domain repositories own semantic logging calls and their own
OpenTelemetry instrumentation.

`moda-interact-gateway` owns architecture-approved central collection,
transport/backend wiring and deployment-level observability infrastructure.

Do not expose raw cross-tenant operational logs/metrics/traces as a
tenant-facing analytics API.
