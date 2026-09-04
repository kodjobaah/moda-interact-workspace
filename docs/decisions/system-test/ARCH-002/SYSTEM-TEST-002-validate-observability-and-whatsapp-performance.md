---
id: ARCH-002-SYSTEM-TEST-002
architecture_id: ARCH-002
title: Validate shared observability and WhatsApp worker performance
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: complete
priority: 45
executor: copilot
claimed_at: 2026-09-03T08:46:13Z
attempt: 3
depends_on:
- ARCH-002-SHOPIFY-007
- ARCH-002-BACKGROUND-007
- ARCH-002-BACKGROUND-009
- ARCH-002-MESSAGING-004
- ARCH-002-MESSAGING-005
- ARCH-002-ADMIN-009
- ARCH-002-GATEWAY-006
- ARCH-002-GATEWAY-004
- ARCH-002-SYSTEM-TEST-003
- ARCH-002-SYSTEM-TEST-004
- ARCH-002-SYSTEM-TEST-005
enables:
- ARCH-002-SYSTEM-TEST-008
- ARCH-002-SYSTEM-TEST-001
created: 2026-08-31
updated: 2026-09-03
---

# Validate shared observability and WhatsApp worker performance

## Current Execution State

This task is **Complete** after architect acceptance of attempt 3.

The accepted integrated local validation uses:

```text
ephemeral Redis
+ ephemeral PostgreSQL
+ WhatsApp emulator
+ owning-repository observability tests
+ bounded final JSON evidence report
```

The generated PostgreSQL `DATABASE_URL` is supplied only to the Admin validation
steps. The accepted Prisma contract requires real `prisma:*` span evidence and
does not require literal SQL text attributes.

The current synthetic WhatsApp emulator timing evidence is recorded in the
Completion Report and must not be interpreted as Meta production latency or
production-capacity evidence.

## Objective

Validate the shared observability runtime across the integrated test topology and
establish a measurable WhatsApp/CommerceAgent performance baseline before any
worker split decision.

## Existing implementation to preserve

Attempt 1 already added:

```text
moda-interact-system-test/scripts/run-arch002-observability.js
moda-interact-system-test/src/observability-validation.js
moda-interact-system-test/test/observability-validation.test.js
moda-interact-system-test/package.json
moda-interact-system-test/README.md
```

The existing runner already composes:

```text
Ephemeral Redis
+ WhatsApp emulator
+ Messaging telemetry checks
+ Shopify telemetry checks
+ Background BullMQ checks
+ WhatsApp turn/agent/tool checks
+ worker metrics checks
+ GenAI sampling/metrics checks
+ WhatsApp emulator timing
+ Admin telemetry/bootstrap checks
```

Preserve those checks and their required-output validation unless a concrete
attempt-2 failure proves a correction is necessary within this task's scope.

## Attempt 2 — exact implementation work

### 1. Add the accepted PostgreSQL fixture to the existing runner

In:

```text
moda-interact-system-test/scripts/run-arch002-observability.js
```

import the accepted fixture from:

```text
../src/ephemeral-postgres
```

Use `withEphemeralPostgres(...)` in the existing fixture lifecycle alongside
`withEphemeralRedis(...)` and `withWhatsAppEmulator(...)`.

Do not create a second PostgreSQL lifecycle implementation.

### 2. Pass the generated DATABASE_URL to Admin validation only

Create an Admin environment derived from the existing Redis/test environment and
the accepted PostgreSQL fixture, for example conceptually:

```text
adminEnvironment = {
  ...redisEnvironment,
  ...postgres.environment
}
```

The following existing Admin validation steps must receive the generated
`DATABASE_URL`:

```text
Admin standard HTTP and Prisma telemetry export
Admin correctness during telemetry backend outage
```

Do not use:

```text
a developer-local database
production DATABASE_URL
Render production PostgreSQL
shared CI PostgreSQL
hard-coded localhost:5432
```

The fixture-provided `DATABASE_URL` is authoritative for this local deterministic
scenario.

### 3. Preserve the corrected Admin telemetry contract

The integrated assertion is:

```text
ephemeral PostgreSQL reachable
    -> Admin readiness database operation succeeds
    -> Prisma instrumentation emits prisma:* span evidence
```

Do **not** add or restore any assertion requiring literal `SELECT 1` in
`db.statement`, `db.query.text`, or another third-party SQL-text attribute.

If SQL-text attributes are present, existing owning-repository safety checks may
validate that they do not contain sensitive values.

### 4. Run the complete integrated scenario

Run:

```text
npm run validate:arch002-observability
```

The command must reach the end of the scenario. A required step that exits
non-zero, is skipped, or omits required evidence is a task failure/blocker and
must not be reported as success.

Do not report only the previously passing prefix from attempt 1.

### 5. Preserve measurement interpretation

WhatsApp emulator timings measure Moda-owned local queue/worker/client behavior.
They must not be represented as measured Meta provider latency or Meta production
capacity.

Do not decide to split CommerceAgent solely from emulator timing. Record the
measured evidence so `moda_architect` can make that architectural decision.

## Scope

- integrate the accepted ephemeral PostgreSQL fixture into the existing runner;
- verify HTTP -> BullMQ -> worker trace continuity;
- verify Shopify/Admin/Messaging standard HTTP and Prisma telemetry where applicable;
- verify Background BullMQ, HTTP/tool and GenAI spans;
- verify one trace per WhatsApp conversation turn, not per whole conversation;
- measure queue wait, worker processing, agent invocation, tool and provider HTTP durations;
- verify production sampling configuration does not affect metrics collection;
- verify telemetry backend outage does not affect request/job correctness.

## Out of Scope

- modifying Admin implementation or Admin tests;
- modifying the accepted PostgreSQL fixture except for a genuine fixture defect;
- creating another PostgreSQL lifecycle;
- deciding final production capacity before measured deployed load tests;
- splitting the WhatsApp/CommerceAgent worker without evidence;
- exposing high-cardinality identifiers as metric labels;
- requiring literal SQL text from third-party instrumentation;
- using production infrastructure or credentials.

## Work Items — attempt 2

- [x] Preserve the attempt-1 runner and validation library.
- [x] Import and compose `withEphemeralPostgres` in the existing runner.
- [x] Pass fixture-generated `DATABASE_URL` to both Admin validation steps.
- [x] Keep Redis and WhatsApp fixtures isolated and unchanged unless necessary.
- [x] Keep the corrected Prisma span contract; do not require literal `SELECT 1` telemetry text.
- [x] Run the full integrated observability command to completion.
- [x] Run repository tests, typecheck and lint required by this repository/task.
- [x] Record measured WhatsApp emulator evidence without representing it as Meta production latency.
- [x] Update this Completion Report with attempt-2 files changed and validation results.
- [x] Return this task to `status: review` and stop.

## Acceptance Criteria — must be reconfirmed in attempt 2

- [x] the complete runner uses isolated Redis, PostgreSQL and WhatsApp fixtures;
- [x] the Admin production-bootstrap validation receives the generated PostgreSQL `DATABASE_URL`;
- [x] Admin successful readiness/Prisma telemetry path passes against ephemeral PostgreSQL;
- [x] cross-service trace continuity is proven in the complete run;
- [x] turn-level WhatsApp trace model is proven;
- [x] latency breakdown remains visible for queue/worker/agent/tools/provider HTTP;
- [x] metrics remain available when trace sampling is reduced;
- [x] telemetry backend failure isolation is proven;
- [x] no required validation step is skipped or missing required evidence;
- [x] evidence is sufficient for `moda_architect` to decide whether CommerceAgent needs an independent worker pool;
- [x] repository validation required by the task passes;
- [x] no production credentials or production infrastructure are used.

## Validation

At minimum execute the commands declared by the repository/task, including:

```text
npm run validate:arch002-observability
npm test
npm run typecheck
npm run lint
```

Before Node-related execution, follow the workspace Node/bootstrap policy. Do not
substitute an unsupported Node version if the workspace-required version is
unavailable.

The complete integrated command is the primary task validation. Passing unit
tests alone is not sufficient.

## Attempt 1 historical evidence

Attempt 1 successfully proved the following before stopping at the Admin
boundary:

- Messaging HTTP/BullMQ continuity;
- Shopify webhook/BullMQ continuity;
- Background BullMQ producer-to-worker trace propagation;
- WhatsApp turn/agent/tool span hierarchy;
- one trace per WhatsApp turn;
- worker queue-wait and processing metrics;
- GenAI metrics while tracing was disabled;
- Background client calls to the WhatsApp emulator;
- Admin telemetry backend failure isolation in an earlier complete path.

The final attempt-1 synthetic WhatsApp emulator sample recorded 20 requests with
approximately p50 4.81 ms, p95 6.55 ms and max 45.99 ms. This remains historical
synthetic evidence only and must not be described as Meta production latency.

Attempt 1 stopped because the Admin test then required literal `SELECT 1` SQL
text. `ARCH-002-ADMIN-009` has since corrected that over-specific assertion and
is architect-accepted Complete.

The local PostgreSQL dependency gap discovered during that review was resolved
by architect-accepted `ARCH-002-SYSTEM-TEST-005`.

## Architect Correction Request — attempt 3

`moda_architect` reviewed attempt 2 and accepted the PostgreSQL integration
itself. Preserve that implementation unchanged.

One narrow regression remains before this task can be accepted:

```text
attempt-1 runner
    -> runValidationSteps(...)
    -> console.log(JSON.stringify(report, null, 2))
    -> durable/reviewable step output and timing evidence
```

Attempt 2 removed the final report emission:

```text
console.log(JSON.stringify(report, null, 2));
```

`runValidationSteps(...)` captures each child process's stdout/stderr rather than
streaming it. Without emitting the returned report, a successful integrated run
discards the detailed evidence after process exit. That makes the current
WhatsApp benchmark/timing evidence and per-step validation output unavailable to
architect review and violates the instruction to preserve the valid attempt-1
runner except where the PostgreSQL integration required change.

### Exact correction

In:

```text
moda-interact-system-test/scripts/run-arch002-observability.js
```

preserve all accepted attempt-2 PostgreSQL integration and restore durable
report emission after the complete `runValidationSteps(...)` result is returned.

The expected shape may be the prior implementation:

```js
console.log(JSON.stringify(report, null, 2));
```

or an equivalent bounded deterministic representation that exposes:

- every executed validation step;
- each step exit code;
- missing-evidence results;
- step duration;
- captured required evidence, including the current
  `WHATSAPP_EMULATOR_HTTP` benchmark line.

Do not create a second reporting framework.

### Attempt-3 validation

Run the complete scenario again:

```text
npm run validate:arch002-observability
```

It must:

1. exit `0`;
2. execute every required step;
3. emit the final integrated report;
4. include the current `WHATSAPP_EMULATOR_HTTP` evidence;
5. preserve the generated ephemeral PostgreSQL `DATABASE_URL` for both Admin
   validation steps;
6. retain the corrected Prisma contract without requiring literal SQL text.

Then run:

```text
npm test
npm run typecheck
npm run lint
git diff --check
```

Record the actual current WhatsApp emulator benchmark values (`p50Ms`, `p95Ms`
and `maxMs`) in the Completion Report as synthetic local evidence. Do not
represent them as Meta production latency or capacity.

### Attempt-3 scope boundary

Do not:

- rewrite the runner;
- change the accepted PostgreSQL fixture;
- change Admin;
- restore the rejected literal `SELECT 1` telemetry assertion;
- modify another repository;
- alter the ARCH-002 validation architecture.

After the correction and validation, set this task back to `status: review`,
update the Completion Report, and STOP.

## Completion Report

### Status

Ready for Review

### Files Changed

`moda-interact-system-test/scripts/run-arch002-observability.js` was updated to
compose `withEphemeralPostgres` with the existing Redis and WhatsApp fixtures.
The generated PostgreSQL environment is passed only to the two Admin
validation steps. No Admin code, accepted PostgreSQL fixture code, or
production configuration was changed.

Attempt 3 restored the final bounded JSON report emission after
`runValidationSteps(...)`, preserving per-step exit codes, durations,
missing-evidence results, and captured subprocess output.

### Work Completed

Attempt-1 implementation and attempt-2 PostgreSQL integration are preserved.
Attempt 3 completed the full scenario with durable report output. Admin
readiness and Prisma telemetry validation ran against the generated isolated
database URL. The WhatsApp emulator benchmark exercised 20 local provider HTTP
requests and recorded `p50Ms: 3.89164599999998`,
`p95Ms: 7.51499800000002`, and `maxMs: 66.80090500000001`. These timings are
synthetic local queue/worker/client evidence and are not Meta provider latency
or production capacity measurements.

### Validation Results

Passed:

- `node --check scripts/run-arch002-observability.js`
- `npm run validate:arch002-observability` (complete run, exit 0; all 10
  required boundaries completed without skipped or missing evidence; final JSON
  report emitted and included `WHATSAPP_EMULATOR_HTTP` evidence)
- `npm test` (14 passed, 2 opt-in Docker tests skipped)
- `npm run typecheck`
- `npm run lint`
- `git diff --check` (warning: pre-existing extra blank line at EOF in
  `docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`; no
  task-owned whitespace error)

### Deviations

The two live Docker fixture tests remain opt-in under their existing environment
flags during the repository test suite. The complete integrated scenario did
provision and clean up the ephemeral PostgreSQL fixture. Workspace
`git diff --check` retains the unrelated pre-existing gateway-document warning
listed above.

### Assumptions

All declared dependencies are architect-accepted Complete. The owning-repository
telemetry tests remain the executable boundaries composed by this system test.
The generated fixture URL is authoritative for the local Admin integration.

### Unresolved Issues

None. Any new cross-repository defect discovered after review must be reported
to `moda_architect` rather than modified outside system-test ownership.

### Architectural Concerns

No new concern. The captured local timing evidence supports a later capacity
decision but does not by itself justify an independent CommerceAgent worker
pool. The repository agent did not commit or push.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 is accepted.

Architect review confirmed that:

- the attempt-2 ephemeral PostgreSQL integration remains unchanged;
- the generated fixture `DATABASE_URL` is supplied only to the two Admin
  validation steps;
- the corrected Prisma telemetry contract remains based on real `prisma:*`
  span evidence and does not require literal `SELECT 1` SQL text;
- attempt 3 restores the final bounded JSON report emission from
  `runValidationSteps(...)`;
- the integrated report preserves each executed step, exit code, duration,
  missing-evidence result and captured subprocess evidence;
- the complete scenario reports all 10 required steps successfully;
- the current `WHATSAPP_EMULATOR_HTTP` evidence is retained;
- the recorded p50/p95/max timings are correctly classified as synthetic local
  evidence rather than Meta provider latency or production capacity;
- repository tests, typecheck, lint and task-owned diff checks were reported
  passing;
- no production credentials or production infrastructure were used;
- no unauthorised changes were made outside system-test ownership.

The task is Complete.

`ARCH-002-SYSTEM-TEST-008` remains Pending because its other direct
dependencies, `ARCH-002-SYSTEM-TEST-006` and
`ARCH-002-SYSTEM-TEST-007`, are not yet both architect-accepted Complete.
