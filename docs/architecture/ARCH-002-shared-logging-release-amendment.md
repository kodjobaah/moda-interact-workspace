# ARCH-002 Shared Logging Release Amendment

## Decision

The Shopify observability task must not resume immediately after the reusable
logger implementation is accepted.

The public npm boundary must first be completed by:

```text
ARCH-002-SHARED-003
Document and publish shared logging package release
```

## Sequence

```text
ARCH-002-SHARED-002
Implement reusable logger
        |
        v
Architect accepts
        |
        v
ARCH-002-SHARED-003
README + version + pack + publish + registry verification
        |
        v
Architect accepts
        |
        v
ARCH-002-SHOPIFY-003
Resume using exact published package version
```

## Reason

A workspace-local `./logging` export does not prove the production npm artifact
contains that export.

SHARED-003 therefore validates the exact artifact consumers will install.

## Version

If the package remains `0.1.0`, the additive logging export is released as the
next minor version:

```text
0.2.0
```

If the package version has already moved, the agent must stop and report the
observed state rather than guessing.

## Public documentation

The npm README must document both:

```text
cross-service Shopify contracts
shared structured logging
```

and clearly separate structured logs from service-specific OpenTelemetry.
