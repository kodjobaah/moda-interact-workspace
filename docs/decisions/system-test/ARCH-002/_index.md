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
| SYSTEM-TEST-002 | Validate shared observability and WhatsApp worker performance | Ready | SHOPIFY-007, BACKGROUND-007, BACKGROUND-009, MESSAGING-004, MESSAGING-005, ADMIN-009, GATEWAY-006, GATEWAY-004, SYSTEM-TEST-003, SYSTEM-TEST-004 |


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
| SYSTEM-TEST-003 | Add isolated ephemeral Redis test infrastructure | Complete | - |
| SYSTEM-TEST-004 | Add WhatsApp Cloud API emulator test infrastructure | Complete | BACKGROUND-010 |

`SYSTEM-TEST-003` is Complete. `SYSTEM-TEST-004` is temporarily Blocked by the concrete Background consumer capability identified during its required preflight.

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



## SYSTEM-TEST-003 architect acceptance

`ARCH-002-SYSTEM-TEST-003` is architect-accepted Complete.

The system-test harness now owns isolated ephemeral Redis lifecycle:

```text
per-run Redis container
dynamic host port
bounded readiness
outage/restart support
clean-state recreation
cleanup
```

Its direct dependency edges for `SYSTEM-TEST-001` and `SYSTEM-TEST-002` are
satisfied.

`SYSTEM-TEST-004` remains Ready and is still a direct prerequisite of both
integrated system-test tasks.

`SYSTEM-TEST-001` additionally remains blocked by `ADMIN-004`.

No downstream task is automatically promoted.


## SYSTEM-TEST-004 blocker resolution

The required consumer preflight found:

```text
moda-interact-background/src/services/whatsapp.service.ts
  -> hard-coded https://graph.facebook.com/v25.0
  -> no injectable outbound API base URL
```

The block is accepted as valid.

The architect creates:

```text
ARCH-002-BACKGROUND-010
  Make outbound WhatsApp API base URL configurable
  status: Ready
```

`SYSTEM-TEST-004` now has:

```text
depends_on:
  - ARCH-002-BACKGROUND-010
```

and remains Blocked until that task is architect-accepted Complete.

After acceptance, `moda_architect` may transition:

```text
SYSTEM-TEST-004
  blocked -> ready
```

The current system-test agent must not continue the blocked attempt.


## SYSTEM-TEST-004 blocker cleared

`ARCH-002-BACKGROUND-010` is architect-accepted Complete.

The outbound client can now be directed at the test-owned emulator through:

```text
WHATSAPP_API_BASE_URL
```

Therefore:

```text
SYSTEM-TEST-004
  blocked -> ready
```

The previous claim is cleared. The next claim must increment the task attempt.

`SYSTEM-TEST-001` and `SYSTEM-TEST-002` remain Pending until their complete
explicit dependency lists are satisfied.


## SYSTEM-TEST-004 architect acceptance

`ARCH-002-SYSTEM-TEST-004` is architect-accepted Complete.

The system-test harness now owns a reusable Node-24 WhatsApp Cloud API emulator
fixture with:

```text
dynamic lifecycle
signed inbound webhooks
duplicate delivery
outbound/status handling
synthetic Background client configuration
cleanup after success/failure
```

The direct dependency edges for `SYSTEM-TEST-001` and `SYSTEM-TEST-002` are
satisfied.

All explicit direct dependencies of `SYSTEM-TEST-002` are now Complete, so:

```text
SYSTEM-TEST-002
  pending -> ready
```

`SYSTEM-TEST-001` remains Pending because `ADMIN-004` is still incomplete.

No downstream task is automatically claimed.
