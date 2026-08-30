# ARCH-002 — System Test Task Index

## Initiative

Render Test & Production Gateway & Infrastructure

## Owner

```yaml
architecture_id: ARCH-002
domain: system-test
assigned_agent: moda_system_test
repository: moda-interact-system-test
```

## Task

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| SYSTEM-TEST-001 | Validate integrated test and production-ready topology | Pending | GATEWAY-004 |

## Unblocking rule

`SYSTEM-TEST-001` remains Pending until `ARCH-002-GATEWAY-004` is
architect-accepted Complete.

GATEWAY-004 is the final infrastructure validation gate and is expected to be
Complete only after the required application, build, observability and topology
prerequisites have been accepted.

System validation runs functional/integration scenarios primarily against the
isolated **test** environment.

The cheap test environment is not evidence that production sustains the
approximately 22,000-Shopify-webhooks-per-minute capacity target.

Measured production-sized capacity evidence is required before ARCH-002 may make
that production-capacity claim.

`moda_system_test` may run/observe the platform but must not modify another
agent's implementation merely to make a failing scenario pass.

The individual task file is authoritative for task state.
