---
id: ARCH-002-MESSAGING-004
architecture_id: ARCH-002
title: Add bounded Meta ingress semantic telemetry
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 31
executor: codex
claimed_at: 2026-08-31 16:12:14+00:00
attempt: 1
depends_on:
- ARCH-002-MESSAGING-003
enables:
- ARCH-002-GATEWAY-006
- ARCH-002-SYSTEM-TEST-002
created: 2026-08-31
updated: '2026-08-31'
---

# Add bounded Meta ingress semantic telemetry

## Objective

Add messaging-owned bounded acceptance, failure and latency telemetry for the
Meta/WhatsApp HTTP ingress path using the global providers installed by the
shared runtime.

## Scope

- add service-semantic spans/metrics for ingress acceptance, failure and latency;
- create instruments once at module/process scope;
- use only bounded architecture-controlled metric dimensions;
- preserve webhook correctness when telemetry recording/export fails;
- exclude tokens, message content, full payloads and customer identifiers.

## Out of Scope

- NodeSDK/provider/exporter/sampler setup;
- BullMQ Queue telemetry;
- background worker/CommerceAgent telemetry;
- gateway/backend configuration;
- business behaviour changes.

## Acceptance Criteria

- [x] ingress acceptance/failure/latency is operationally observable;
- [x] metric dimensions are bounded;
- [x] prohibited message/customer/credential data is absent;
- [x] telemetry failure does not fail otherwise valid webhook handling;
- [x] no generic runtime plumbing is introduced locally.

## Validation

- [x] focused semantic telemetry tests;
- [x] failure-isolation test;
- [x] sensitive-data review/test;
- [x] metric-cardinality review/test;
- [x] affected repository tests;
- [x] repository-defined typecheck;
- [x] production build.

## Stop Condition

After semantic ingress telemetry is complete and validated, set this task to
`review`, write the Completion Report, return to `moda_architect`, and STOP.

Do not begin MESSAGING-005 or gateway work.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-messaging/app/lib/observability/whatsapp-ingress-telemetry.ts`
- `moda-interact-messaging/app/routes/whatsapp.tsx`
- `moda-interact-messaging/tests/whatsapp-ingress-telemetry.test.mjs`
- `moda-interact-messaging/package.json`
- `moda-interact-messaging/package-lock.json`
- `docs/decisions/messaging/ARCH-002/MESSAGING-004-add-ingress-semantic-telemetry.md`

### Work Completed

- Added module-scope messaging-owned tracer, request counter, and latency
	histogram using the global OpenTelemetry API providers installed by the
	accepted shared runtime.
- Recorded accepted, rejected, and failed POST ingress outcomes across the
	existing method, signature, JSON, processing, and success paths without
	changing response or queue behavior.
- Restricted all span and metric attributes to closed outcome, reason, and HTTP
	status-code vocabularies.
- Kept message content, full payloads, customer/phone identifiers, provider
	message IDs, credentials, tokens, and authorization data out of telemetry.
- Wrapped semantic recording in failure isolation so tracer, counter, or
	histogram failures cannot escape into webhook handling.
- Added direct runtime declarations for `@opentelemetry/api` and the compatible
	Zod contract required by the shared runtime consumer.

### Validation Results

- `node --test tests/whatsapp-ingress-telemetry.test.mjs` passed: 4 tests.
	Coverage includes acceptance/latency, rejected/failed outcomes, exact
	attribute allowlisting, closed cardinality sets, sensitive-data exclusion,
	and independent tracer/counter/histogram failure isolation.
- `npm test` passed: 7 tests, 0 failures.
- `npm run typecheck` passed (`react-router typegen && tsc`).
- `npm run build` passed for both React Router client and server bundles.
- Changed-file editor diagnostics reported no errors and `git diff --check`
	passed.
- Static ownership review found no local NodeSDK, tracer/meter provider, OTLP
	exporter, span processor, sampler, or BullMQ telemetry wiring.
- Sensitive-data scan found no message, payload, customer, phone, credential,
	token, secret, or authorization input in the semantic telemetry module. Its
	only `message` property is a bounded span-status value derived from the closed
	reason vocabulary.
- Initial `workspace-doctor.sh --quick` reported `DEP-ZOD-001` because messaging
	consumed the shared runtime without a direct Zod declaration. After adding
	compatible `zod@^4.5.4`, the doctor passed 7 checks with only the documented
	unrelated `NPM-CONFIG-001` warning and one local-development informational
	condition.
- Dependency installation reported zero vulnerabilities and repeated the
	existing transitive allow-scripts advisory for `fsevents`,
	`msgpackr-extract`, and `protobufjs`.

### Deviations

Added the direct compatible Zod runtime declaration required by baseline
`DEP-ZOD-001` after the task's dependency-state validation exposed the missing
consumer contract.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted by `moda_architect` on 2026-08-31.

The implementation conforms to the granular MESSAGING-004 boundary:

- messaging-owned tracer, request counter and latency histogram are created once
  at module scope through the global OpenTelemetry API providers installed by
  the shared runtime;
- semantic observations cover accepted, rejected and failed POST ingress paths
  without changing the existing webhook response or queue-processing behaviour;
- metric/span dimensions are restricted to the closed
  `outcome`, `reason` and `status_code` vocabularies defined by the module;
- message content, raw payloads, customer/phone identifiers, provider message
  identifiers, credentials, tokens and authorization data are not passed into
  the semantic telemetry helper;
- semantic telemetry recording is best-effort and cannot escape into otherwise
  valid webhook handling;
- no local NodeSDK, provider, exporter, sampler or BullMQ telemetry mechanism was
  introduced;
- no MESSAGING-005 implementation was started.

The Completion Report records focused semantic telemetry, cardinality,
sensitive-data and failure-isolation tests as passing, together with the
repository test suite, typecheck and production build.

The direct `@opentelemetry/api` dependency is appropriate because this
repository now imports that API directly. The added compatible Zod declaration
is accepted as a narrowly documented dependency-state correction discovered by
the required workspace dependency validation; it does not expand the runtime
behaviour owned by MESSAGING-004.

`ARCH-002-MESSAGING-004` is architecturally Complete.

`ARCH-002-MESSAGING-005` remains independently Ready.
