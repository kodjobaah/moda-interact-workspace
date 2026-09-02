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
| SYSTEM-TEST-001 | Validate integrated test and production-ready topology | Pending | GATEWAY-004, ADMIN-004, SYSTEM-TEST-003, SYSTEM-TEST-004 |

## Unblocking rule

`SYSTEM-TEST-001` remains Pending until `ARCH-002-GATEWAY-004`,
`ARCH-002-ADMIN-004`, `ARCH-002-SYSTEM-TEST-003` and
`ARCH-002-SYSTEM-TEST-004` are architect-accepted Complete.

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

## Observability Validation Extension

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| SYSTEM-TEST-002 | Validate shared observability and WhatsApp worker performance | Pending | SHOPIFY-007, BACKGROUND-007, BACKGROUND-009, MESSAGING-004, MESSAGING-005, ADMIN-009, GATEWAY-006, GATEWAY-004, SYSTEM-TEST-003, SYSTEM-TEST-004 |


`SYSTEM-TEST-002` also requires `ARCH-002-GATEWAY-004` because it validates the
shared observability runtime across the integrated test topology. Completion of
the telemetry-emitter tasks and GATEWAY-006 alone is not sufficient to promote
it to Ready.


## SYSTEM-TEST-002 dependency-record reconciliation

The individual `SYSTEM-TEST-002` YAML frontmatter is reconciled to match this
index and the task's own Infrastructure gate section.

`ARCH-002-GATEWAY-004` is a direct dependency.

Therefore `SYSTEM-TEST-002` remains Pending even though its telemetry-emitter
and `GATEWAY-006` prerequisites are Complete.


## Isolated Test Dependency Infrastructure

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| SYSTEM-TEST-003 | Add isolated ephemeral Redis test infrastructure | Ready | - |
| SYSTEM-TEST-004 | Add WhatsApp Cloud API emulator test infrastructure | Ready | - |

Both tasks are independently executable now.

They are direct prerequisites for `SYSTEM-TEST-001` and `SYSTEM-TEST-002`.

### Redis decision

System/integration tests own their Redis runtime:

```text
test run
  -> isolated Redis container
  -> dynamic port
  -> clean state
  -> teardown
```

Tests must not silently use developer Redis, shared CI Redis, Redis Cloud or
production Redis.

### WhatsApp decision

Architecture-level functional tests use a test-owned WhatsApp Cloud API emulator
for deterministic inbound/outbound provider-boundary scenarios.

The emulator is a test substitute, not evidence of full Meta provider behavior
or production capacity.

If current Moda outbound WhatsApp code cannot inject an emulator base URL,
`SYSTEM-TEST-004` must return Blocked with the concrete call site. The
system-test agent must not modify the owning application repository.

