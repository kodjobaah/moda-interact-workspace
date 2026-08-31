---
id: ARCH-002-BACKGROUND-007
architecture_id: ARCH-002
title: Add bounded background worker operational metrics
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 32
executor: codex
claimed_at: 2026-08-31 17:34:49+00:00
attempt: 1
depends_on:
- ARCH-002-BACKGROUND-006
enables:
- ARCH-002-GATEWAY-006
- ARCH-002-SYSTEM-TEST-002
created: 2026-08-31
updated: '2026-08-31'
---

# Add bounded background worker operational metrics

## Objective

Add service-owned low-cardinality operational metrics needed to determine
whether the three worker deployments are keeping up with their workloads.

## Scope

Instrument bounded signals for the existing worker/job set, including where
meaningful:

- processed job throughput;
- success/failure outcome;
- processing duration;
- retry/attempt outcome;
- processing age / queue-lag signal available from existing BullMQ job metadata.

Create instruments once at module/process scope.

Use only architecture-controlled bounded dimensions such as logical worker,
queue/job kind and outcome.

## Out of Scope

- BullMQ trace-context wiring;
- GenAI/CommerceAgent metrics;
- tenant/shop/customer/job IDs as metric dimensions;
- new queue scans merely to manufacture queue-depth metrics;
- autoscaling controller logic;
- Grafana dashboards/alerts;
- provider/exporter setup.

## Acceptance Criteria

- [x] job throughput/outcome/duration is observable with bounded dimensions;
- [x] retry/attempt behaviour is observable where available without new business semantics;
- [x] processing-age/lag is emitted from bounded existing metadata where practical;
- [x] no job/customer/shop/checkout/message identifiers are metric labels;
- [x] instruments are module/process singletons rather than per-job constructs;
- [x] metric recording failure cannot fail a business job.

## Validation

- [x] focused metric tests;
- [x] cardinality fuzz/review;
- [x] sensitive-data review/test;
- [x] failure-isolation test;
- [x] affected repository tests;
- [x] typecheck;
- [x] production build.

## Stop Condition

After bounded worker metrics are complete and validated, set this task to
`review`, complete the Completion Report, return to `moda_architect`, and STOP.

Do not begin gateway or system-test work.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/package.json`
- `moda-interact-background/package-lock.json`
- `moda-interact-background/src/observability/worker-metrics.ts`
- `moda-interact-background/src/workers/checkout.worker.ts`
- `moda-interact-background/src/workers/orders.worker.ts`
- `moda-interact-background/src/workers/pending-recovery-candidate.worker.ts`
- `moda-interact-background/src/workers/whatsapp.worker.ts`
- `moda-interact-background/tests/unit/observability/worker-metrics.test.ts`
- `moda-interact-background/tests/unit/runtime/bullmq-telemetry.test.ts`
- `docs/decisions/background/ARCH-002/BACKGROUND-007-add-bounded-worker-operational-metrics.md`

### Work Completed

- Added module-scope OpenTelemetry counter and histograms for job processing
	operations, processor duration and creation-to-processing age.
- Wrapped all four existing Worker processors without changing their queue/job
	names, payloads, concurrency, retry behavior, return values or thrown errors.
- Added fixed worker, queue, job-kind, outcome and initial/retry dimensions;
	unknown job names collapse to the bounded `unknown` value.
- Disabled BullMQ's generic Worker metrics because BullMQ labels those metrics
	with raw job names and creates instruments during state transitions; native
	BullMQ tracing remains enabled on every Worker and Queue boundary.
- Added a direct production dependency on `@opentelemetry/api`; provider,
	exporter and lifecycle ownership remains in the shared runtime.
- Added focused singleton, outcome, retry, age, cardinality, sensitive-data and
	metric-failure-isolation coverage.

### Validation Results

- `npm test -- --run tests/unit/observability/worker-metrics.test.ts tests/unit/runtime/bullmq-telemetry.test.ts tests/unit/runtime/worker-process.test.ts`:
	passed, 3 files and 15 tests.
- Cardinality/sensitive-data fuzz coverage passed for 50 arbitrary customer-like
	job names and payload/identifier values; every unknown name emitted only
	`bullmq.job.name=unknown`, and no supplied value reached metric attributes.
- Failure-isolation coverage passed with counter and both histogram recorders
	throwing; successful return identity and original business-error identity
	were preserved.
- `scripts/workspace-doctor.sh --quick`: 7 checks passed; one known warning for
	`moda-interact/.npmrc` `shamefully-hoist` configuration outside this task.
- `./node_modules/.bin/tsc --noEmit`: passed.
- `npm run build`: passed, including Prisma Client generation and TypeScript
	compilation.
- `npm test`: 14 files passed, 1 failed, 2 skipped; 85 tests passed, 1 failed,
	4 skipped. The sole failure remains the architect-accepted unrelated
	`recovery-routing.service.test.ts` mock omission for
	`prisma.customerPhone.findMany`; no operational metric test failed.
- Source review found exactly one meter, one counter, two histograms and five
	bounded attribute keys. No job/customer/shop/checkout/message identifiers,
	payload fields, error details, trace values or GenAI metrics are recorded.
- VS Code diagnostics were clean for all changed production and test files.

### Deviations

None.

### Assumptions

- Processing age is defined as BullMQ job `timestamp` to the current
	`processedOn` value. It intentionally includes scheduled delay, retry backoff
	and prior waiting time and is not described as pure ready-queue latency.
- `attemptsStarted > 1` or `attemptsMade > 0` identifies a retry attempt without
	predicting whether BullMQ will schedule another attempt after a failure.

### Unresolved Issues

- The existing recovery-routing unit-test mock still lacks
	`prisma.customerPhone.findMany`, leaving the unrelated full suite one test
	short of green. This is unchanged from accepted BACKGROUND-006 evidence.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted by `moda_architect` on 2026-08-31.

The implementation conforms to the granular BACKGROUND-007 boundary:

- one module-scope meter creates exactly one operations counter and two
  histograms for processor duration and creation-to-processing age;
- all four existing Worker processors are wrapped without changing queue names,
  job names, payloads, concurrency, retries, return values or business errors;
- metric dimensions are restricted to five bounded keys:
  `moda.worker.name`, `bullmq.queue.name`, `bullmq.job.name`,
  `moda.worker.outcome` and `moda.worker.attempt`;
- worker and queue values come from the fixed architecture-owned worker set;
- known job names are explicitly allow-listed and arbitrary names collapse to
  the bounded `unknown` value;
- outcome is restricted to `success|failure` and attempt classification to
  `initial|retry`;
- processing age is derived from existing BullMQ `timestamp`/`processedOn`
  metadata and does not introduce queue scans or additional state lookups;
- job/customer/shop/checkout/message identifiers, payload values, error details
  and trace values are excluded from metric attributes;
- each metric recorder is independently failure-isolated so telemetry cannot
  replace a successful result or original business error;
- BullMQ tracing remains enabled, while BullMQ generic metrics are disabled on
  these Workers in favour of the bounded service-owned metric vocabulary;
- no GenAI/CommerceAgent spans or GenAI metrics were introduced.

Moving `@opentelemetry/api` from development-only to a production dependency is
appropriate because the new production `worker-metrics.ts` module imports that
API directly.

The Completion Report records the focused operational-metric/runtime suite as
15/15 passing, including cardinality fuzzing across 50 arbitrary job names,
sensitive-data exclusion and recorder-failure isolation. TypeScript typecheck
and production build passed.

The full repository suite still contains the previously known unrelated
`recovery-routing.service.test.ts` Prisma mock omission. No worker-operational
metric test failed.

`ARCH-002-BACKGROUND-007` is architecturally Complete.

`ARCH-002-BACKGROUND-008` remains independently Ready.
`ARCH-002-BACKGROUND-009` remains Pending until BACKGROUND-008 is
architect-reviewed Complete.
