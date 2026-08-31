# ARCH-002 Shared Structured Logging Amendment

## Decision

ARCH-002 standardises generic application structured logging through:

```text
@modainteract/moda-interact-shared/logging
```

Implementation owner:

```text
ARCH-002-SHARED-002
moda_shared
```

## Reason

Structured logging is required by multiple runtime services and is not a
Shopify-specific concern.

A generic logger duplicated separately by app/background/messaging/admin would
create drift in:

```text
JSON shape
identity
levels
redaction
error serialisation
size bounds
failure isolation
```

The shared repository already owns code genuinely reused across services.

## Boundary

Shared owns:

```text
generic logger API
generic JSON envelope
generic redaction/sanitisation
generic failure isolation
generic sink abstraction
```

Service repositories own:

```text
semantic event names
which safe fields are operationally useful
service environment resolution
provider/domain-specific business meaning
service-specific OpenTelemetry metrics/spans
```

Gateway/infrastructure owns:

```text
central log collection
backend/transport
retention
dashboards/alerts
deployment wiring
```

## Logging Is Not OpenTelemetry

The shared logger must not automatically generate metrics or spans.

Service-specific OTel implementations remain owner-specific because metric
cardinality and span lifecycle differ from diagnostic logs.

## Sequencing

```text
ARCH-002-SHARED-002
Implement reusable structured logging
        |
        v
moda_architect review
        |
        v
SHARED-002 Complete
        |
        v
ARCH-002-SHOPIFY-003 resumes
        |
        +--> remove local generic logger
        +--> consume shared ./logging
        +--> retain Shopify-specific OTel locally
        |
        v
moda_architect review
```

`ARCH-002-SHOPIFY-003` is Blocked until `SHARED-002` is architect-accepted.

Other runtime agents should consult:

```text
docs/observability/shared-logging.md
```

before implementing new generic structured logging.

## Production Package Boundary

SHARED-002 implements/validates the additive package API.

Package publication/exact-version adoption remains coordinated through the
existing ARCH-002 shared-package/consumer distribution work.

A service must not claim production readiness using a published shared version
that does not actually contain the `./logging` export.
