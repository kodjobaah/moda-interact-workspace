---
id: ARCH-002-SYSTEM-TEST-008
architecture_id: ARCH-002
title: Assess production-sized Shopify ingress capacity gate
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: pending
priority: 48
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-SYSTEM-TEST-002
  - ARCH-002-SYSTEM-TEST-006
  - ARCH-002-SYSTEM-TEST-007
  - ARCH-002-SYSTEM-TEST-009
enables:
  - ARCH-002-SYSTEM-TEST-001
created: 2026-09-03
updated: 2026-09-03
---

# Assess Production-Sized Shopify Ingress Capacity Gate

## Current Execution State

This task is **Pending**.

It becomes Ready only after the local observability baseline, deployed Render
test topology and production Blueprint/readiness tasks are architect-accepted:

```text
ARCH-002-SYSTEM-TEST-002
ARCH-002-SYSTEM-TEST-006
ARCH-002-SYSTEM-TEST-007
ARCH-002-SYSTEM-TEST-009
```

## Objective

Produce an explicit evidence-based outcome for the ARCH-002 production Shopify
ingress capacity target:

```text
22,000 Shopify webhook requests/minute
≈ 367 requests/second
```

The task outcome is exactly one of:

```text
PROVEN
```

or:

```text
UNMET
```

`UNMET` is an acceptable completed **assessment** outcome. It means the
architecture must not claim the target has been demonstrated and, while that
capacity target remains an ARCH-002 completion requirement, the architecture
must remain In Progress.

## Important Workload Boundary

The 22,000/minute figure is **raw Shopify event ingress**, not:

```text
22,000 recoveries/minute
22,000 WhatsApp messages/minute
22,000 CommerceAgent calls/minute
22,000 LLM requests/minute
```

The load scenario must preserve the architecture's filtering model and record
background queue behavior separately from ingress acceptance.

## Environment Requirement

Capacity evidence must come from:

- a production-sized pre-cutover environment; or
- production infrastructure before live customer traffic, using safe synthetic
  workload and explicit user/architect approval for that environment.

Do not use the cheap Render test plans as production-capacity evidence.

The system-test runner may define task-owned inputs such as:

```text
ARCH002_CAPACITY_GATEWAY_URL
ARCH002_CAPACITY_SHOPIFY_API_SECRET
ARCH002_CAPACITY_DURATION_SECONDS
```

Secret values must be supplied outside source control.

If no production-sized target environment is available, do not invent one and
do not resize production infrastructure in this task. Complete the assessment
with:

```text
Capacity Gate Outcome: UNMET
Reason: production-sized validation environment/evidence unavailable
```

and record the exact prerequisite needed for a future attempt.

## Load Profile

The target rate is approximately 367 webhook requests/second.

Use synthetic authenticated Shopify webhook payloads and deterministic unique
identifiers so duplicate/idempotency behavior can be interpreted.

The steady-state duration must be long enough to distinguish temporary buffering
from sustainable processing. The architecture source does not define a fixed
latency SLO or a fixed error-rate percentage, so this task must **not invent one**.
Record measured p50/p95/p99 and error outcomes for architect review.

At minimum record:

```text
offered request rate
accepted request rate
HTTP status distribution
p50/p95/p99 acknowledgement latency
queue depth over time
oldest waiting job/event age where observable
background processing throughput
retry/failure amplification
PostgreSQL error/connection behavior
Redis/BullMQ error/connection behavior
resource/instance configuration actually tested
```

Where tenant distribution is configurable, avoid representing a single synthetic
hot tenant as proof of balanced multi-tenant fairness. Record the generated
workload shape.

## Capacity Outcome Rules

### PROVEN

Use `PROVEN` only when measured evidence demonstrates the target ingress rate on
the stated production-sized configuration and the evidence does not show
sustained capacity collapse such as continuously growing queue lag/backlog or
capacity-induced correctness failure.

Do not infer downstream CommerceAgent/WhatsApp capacity from ingress proof.

### UNMET

Use `UNMET` when any of the following applies:

- no production-sized target environment is available;
- the controlled load run cannot be executed safely;
- the measured ingress target is not sustained;
- queue lag/backlog grows without recovery at the target;
- capacity-induced correctness/dependency failures prevent the architecture from
  supporting the target;
- evidence is incomplete or ambiguous.

A failed/unavailable capacity measurement is evidence, not permission for the
system-test agent to alter production plan sizes or autoscaling policy.

## Implementation Guidance for Luna

Keep the task bounded to load generation, measurement and reporting.

Preferred structure when new code is needed:

```text
moda-interact-system-test/src/shopify-ingress-load.js
moda-interact-system-test/scripts/run-arch002-capacity.js
moda-interact-system-test/test/shopify-ingress-load.test.js
```

A package script such as:

```text
validate:arch002-capacity
```

is appropriate.

Use existing approved observability signals rather than creating duplicate Moda
metrics merely for the load test.

Do not add an autoscaling controller.

## Scope

- preflight production-sized environment availability;
- generate bounded synthetic Shopify webhook ingress load;
- measure target-rate acceptance and acknowledgement latency;
- observe queue/backlog/processing/dependency behavior using accepted telemetry;
- record exact tested infrastructure configuration;
- produce `PROVEN` or `UNMET` with evidence.

## Out of Scope

- changing production plan sizes;
- implementing autoscaling;
- modifying gateway/application/background repositories;
- destructive production data operations;
- using live customer payloads;
- extrapolating WhatsApp/LLM capacity from raw Shopify ingress;
- inventing latency/error SLOs absent from the architecture.

## Work Items

- [ ] Confirm SYSTEM-TEST-002/006/007 are Complete before claim.
- [ ] Determine whether a production-sized safe target environment is available.
- [ ] Record the actual service/instance configuration to be tested.
- [ ] Implement/reuse bounded synthetic Shopify ingress load generation.
- [ ] Add focused load-generator correctness tests that do not require production.
- [ ] If environment exists, execute the controlled target-rate run.
- [ ] Record ingress rate/status/latency evidence.
- [ ] Record queue depth/lag/throughput/retry evidence where available.
- [ ] Record PostgreSQL and Redis/BullMQ dependency behavior.
- [ ] Assign exactly one outcome: `PROVEN` or `UNMET`.
- [ ] If UNMET, record the exact missing/failing prerequisite without changing infrastructure.
- [ ] Run repository tests/typecheck/lint for changed system-test code.
- [ ] Return to `review` and stop.

## Acceptance Criteria

- [ ] task does not use cheap test plans as production-capacity proof;
- [ ] raw Shopify ingress is distinguished from recoveries/messages/LLM workload;
- [ ] no latency/error SLO absent from ARCH-002 is invented;
- [ ] measured evidence records actual tested infrastructure configuration;
- [ ] outcome is exactly `PROVEN` or `UNMET`;
- [ ] `PROVEN` is used only for measured production-sized evidence;
- [ ] `UNMET` clearly preserves the architecture blocker rather than disguising it;
- [ ] no production infrastructure is modified by this task;
- [ ] no production customer data is used;
- [ ] repository validation passes for changed system-test code;
- [ ] task returns to `review` and stops.

## Validation

Always run deterministic unit tests for load-generation/rate-control/reporting
logic if code is changed.

The live capacity run is environment-dependent:

- if safely available, run it and capture bounded evidence;
- if unavailable, do not fake/skip-as-pass; report `UNMET` with exact reason.

## Completion Report

### Status

Not Started

### Target Environment

Pending.

### Tested Infrastructure Configuration

Pending.

### Load Profile

Pending.

### Measurements

Pending.

### Capacity Gate Outcome

Pending: must become exactly `PROVEN` or `UNMET`.

### Evidence / Reason

Pending.

### Files Changed

None.

### Validation Results

Not run.

### Deviations

None.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation/evidence.
