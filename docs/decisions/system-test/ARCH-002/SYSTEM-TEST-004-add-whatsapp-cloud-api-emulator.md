---
id: ARCH-002-SYSTEM-TEST-004
architecture_id: ARCH-002
title: Add WhatsApp Cloud API emulator test infrastructure
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: complete
priority: 31
executor: copilot
claimed_at: 2026-09-02T22:47:12Z
attempt: 2
depends_on:
  - ARCH-002-BACKGROUND-010
enables:
  - ARCH-002-SYSTEM-TEST-001
  - ARCH-002-SYSTEM-TEST-002
created: 2026-09-02
updated: 2026-09-02
---

# Add WhatsApp Cloud API Emulator Test Infrastructure

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Provide a reusable WhatsApp Cloud API emulator fixture for architecture-level
integration/system testing.

The fixture must let Moda tests exercise both directions of the provider
boundary without sending messages to real WhatsApp users:

```text
Moda outbound WhatsApp API call
    -> emulator

emulator signed inbound/status webhook
    -> gateway/messaging test target
```

The emulator is a test dependency only. It does not replace final real-provider
smoke testing or prove Meta production capacity.

## Selected Emulator

Use the architect-approved current package:

```text
@whatsapp-cloudapi/emulator@5.0.1
```

Pin the package exactly in the system-test harness unless a later architect
decision changes the version.

The selected version requires Node.js 24 or later.

Do not upgrade unrelated Moda service runtimes merely to satisfy the emulator.

If `moda-interact-system-test` is not already on a compatible Node runtime,
isolate the emulator in a Node 24 test runner/helper/container rather than
silently changing production service runtime contracts.

## Required Emulator Capabilities

The reusable fixture must support:

- start;
- readiness;
- stop/cleanup;
- dynamic port selection;
- synthetic business phone-number ID;
- synthetic verify token;
- synthetic app secret;
- configurable webhook callback URL;
- `X-Hub-Signature-256` webhook generation;
- inbound text-message simulation;
- outbound message API requests;
- message status webhooks;
- configurable duplicate webhook delivery;
- bounded request timeout;
- test-controlled logging.

No production Meta credential is required.

## System-Test Connection Contract

The fixture must expose a stable test contract equivalent to:

```text
WHATSAPP_EMULATOR_BASE_URL
WHATSAPP_TEST_PHONE_NUMBER_ID
WHATSAPP_TEST_VERIFY_TOKEN
WHATSAPP_TEST_APP_SECRET
```

Exact environment names may follow existing repository conventions, but must be
documented.

The integrated tests must be able to configure:

```text
Moda outbound WhatsApp client
    -> emulator base URL

emulator webhook callback
    -> gateway / messaging webhook endpoint
```

Do not hardcode a developer machine port.

## Consumer Capability Preflight

Before completing this task, inspect the current Moda outbound WhatsApp client
configuration to determine whether tests can override the Cloud API base URL.

Inspection does not grant ownership to modify another repository.

If the current Messaging/Background implementation cannot point outbound
WhatsApp API calls at an injected emulator base URL:

1. record the exact hard-coded/non-configurable call site;
2. do not patch that repository from `moda_system_test`;
3. return this task `blocked` with the concrete missing capability;
4. allow `moda_architect` to create the required task for the owning agent.

Do not create a test-only network interception hack to bypass an application
configuration gap.

## Functional Fixture Validation

Before this task is Complete, validate the emulator fixture itself with a
bounded local callback/receiver where necessary.

At minimum prove:

### Outbound

```text
test client
    -> POST /v{version}/{phoneNumberId}/messages
    -> emulator accepts the outbound message
    -> emulated message ID/status observed
```

No real WhatsApp user receives the message.

### Inbound signed webhook

```text
POST /simulate/incoming/text
    -> emulator
    -> callback receives WhatsApp-format webhook
    -> X-Hub-Signature-256 present and verifiable
```

### Duplicate delivery

Configure duplicate delivery and prove the callback receives the configured
number of repeated deliveries.

The later integrated system tests own proving Moda's deduplication/business
outcome.

### Status webhook

Prove an outbound message can generate the expected emulator status webhook
shape needed by Moda tests.

## Security Requirements

Use synthetic test values only.

Never reuse:

```text
production Meta access token
production app secret
production verify token
real customer phone number
```

The emulator app secret exists only to prove the same signature-verification
boundary used by the application.

Provider-specific verification remains in `moda_messaging`; the system-test
fixture must not bypass it.

## Out of Scope

- sending real WhatsApp messages;
- proving full Meta Graph API compatibility;
- proving Meta production throughput/capacity;
- changing WhatsApp business logic;
- changing provider signature semantics;
- modifying Messaging/Background code from this task;
- implementing all `SYSTEM-TEST-001/002` scenarios.

## Work Items

- [x] inspect system-test Node/runtime/orchestration;
- [x] add exact `@whatsapp-cloudapi/emulator@5.0.1`;
- [x] isolate Node 24 requirement if necessary;
- [x] implement start/readiness/stop lifecycle;
- [x] use dynamic ports;
- [x] expose base URL and synthetic provider configuration;
- [x] implement bounded local webhook receiver/fixture support;
- [x] prove outbound message API handling;
- [x] prove inbound signed webhook handling;
- [x] prove duplicate webhook generation;
- [x] prove status webhook generation;
- [x] inspect current Moda outbound base-URL configurability;
- [x] document integrated-test wiring contract;
- [x] document that real-provider smoke testing remains separate.

## Validation

Run the repository's normal:

```text
tests
typecheck
lint
```

where available.

Add focused tests that prove:

```text
emulator lifecycle
dynamic port allocation
outbound message acceptance
signed inbound webhook
duplicate delivery
status webhook
cleanup after failure/success
```

## Acceptance Criteria

- [x] system tests can start/stop their own emulator instance;
- [x] no fixed developer port is required;
- [x] outbound API messages can be sent to the emulator;
- [x] inbound messages can be simulated;
- [x] signed webhooks can exercise the real signature boundary;
- [x] duplicate deliveries can be generated deterministically;
- [x] status webhooks can be generated;
- [x] no production Meta credential is required;
- [x] Node 24 requirement does not silently change unrelated service runtimes;
- [x] outbound Moda base-URL injection capability is confirmed, or the task is
      returned Blocked with concrete evidence;
- [x] emulator use is documented as test-only, not proof of Meta production
      compatibility/capacity;
- [x] implementation changes are ready for developer commit/push;
- [x] repository agent does not commit or push.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-system-test/package.json`
- `moda-interact-system-test/package-lock.json`
- `moda-interact-system-test/src/whatsapp-emulator.js`
- `moda-interact-system-test/test/whatsapp-emulator.test.js`
- `moda-interact-system-test/README.md`

### Work Completed

Consumer preflight confirmed that `moda-interact-background/src/services/whatsapp.service.ts`
now accepts `WHATSAPP_API_BASE_URL` with the unchanged production default:

```text
https://graph.facebook.com/v25.0
```

The fixture uses the exact `@whatsapp-cloudapi/emulator@5.0.1` dependency with
Node 24, binds the emulator to port 0, exposes the assigned port and synthetic
environment contract, and wraps bounded outbound requests plus inbound text
simulation. Its documented `WHATSAPP_API_BASE_URL` includes `/v25.0` so the
actual Background client reaches the emulator’s supported route.

Focused tests prove outbound acceptance and generated status webhooks, signed
inbound webhooks, configured duplicate delivery, dynamic port isolation, direct
synthetic Background environment wiring, and cleanup. No production credentials
or external provider requests are used.

### Validation Results

Node runtime: `v24.19.0`.

`npm test`: 9 total, 8 passed, 0 failed, 1 skipped (the existing opt-in live
Docker Redis test; `RUN_LIVE_REDIS_TEST=1` is required).

`npm run typecheck`: passed.

`npm run lint`: passed.

Focused emulator tests: 4 passed, 0 failed, 0 skipped. They cover lifecycle
and dynamic port allocation, outbound acceptance/status webhook, signed inbound
webhook, duplicate delivery, direct Background environment keys
(`WHATSAPP_API_BASE_URL`, `WHATSAPP_PHONE_NUMBER_ID`, and
`WHATSAPP_ACCESS_TOKEN`), and cleanup.

Cleanup-success evidence: `withWhatsAppEmulator` callback-success test confirms
the fixture's port is released after the callback returns.

Cleanup-failure evidence: callback-failure test confirms the fixture is cleaned
up in `finally` while the synthetic callback error is preserved.

### Deviations

The emulator package delays configured duplicate deliveries randomly, so the
focused duplicate test uses a bounded 12-second observation window. This is
within the package behavior and does not change application timeout settings.

### Assumptions

The emulator supports only its documented WhatsApp Cloud API subset. Integrated
tests must not infer support for provider routes the emulator does not
implement.

### Unresolved Issues

No unresolved implementation issue remains. Integrated system scenarios and
Moda webhook deduplication/business outcomes remain owned by SYSTEM-TEST-001
and SYSTEM-TEST-002.

### Architectural Concerns

The missing outbound base-URL injection is an ownership boundary issue. No
test-only interception or cross-repository patch was added.

## Architect Review

### Review Status

Accepted / Complete

### Review Notes

`ARCH-002-SYSTEM-TEST-004` is architect-accepted.

The second execution attempt resolves the runtime and lifecycle gaps identified
during the previous architect review.

### Emulator Dependency / Runtime Reviewed

The system-test harness pins exactly:

```text
@whatsapp-cloudapi/emulator@5.0.1
```

Both:

```text
package.json
package-lock.json
```

declare the system-test runtime contract:

```text
node >=24
```

The pinned emulator package itself also declares:

```text
node >=24
```

This requirement applies only to `moda-interact-system-test`; no Moda
production-service Node runtime is changed.

### Fixture Contract Reviewed

The accepted fixture provides:

```text
start
bounded readiness
stop / cleanup
dynamic port allocation
synthetic phone-number ID
synthetic verify token
synthetic app secret
synthetic access token
configurable webhook callback
signed X-Hub-Signature-256 webhooks
inbound text simulation
outbound message API handling
status webhook generation
duplicate webhook delivery
bounded HTTP requests
test-controlled logging
```

The Background client can consume the fixture directly through:

```text
WHATSAPP_API_BASE_URL
WHATSAPP_PHONE_NUMBER_ID
WHATSAPP_ACCESS_TOKEN
```

The fixture additionally retains its stable test-oriented identity variables:

```text
WHATSAPP_EMULATOR_BASE_URL
WHATSAPP_TEST_PHONE_NUMBER_ID
WHATSAPP_TEST_VERIFY_TOKEN
WHATSAPP_TEST_APP_SECRET
WHATSAPP_TEST_ACCESS_TOKEN
```

All values are synthetic test data.

### Provider Boundary Reviewed

The fixture exposes:

```text
WHATSAPP_API_BASE_URL
  -> http://127.0.0.1:<dynamic-port>/v25.0
```

which is compatible with the architect-accepted `BACKGROUND-010` outbound
client seam.

Therefore the real Background outbound URL becomes:

```text
http://127.0.0.1:<dynamic-port>/v25.0/<phoneNumberId>/messages
```

during integrated system testing without HTTP interception or cross-repository
patching.

Production remains unchanged:

```text
https://graph.facebook.com/v25.0/<phoneNumberId>/messages
```

when the override is absent.

### Lifecycle / Cleanup Reviewed

The reusable helper:

```text
withWhatsAppEmulator(options, callback)
```

owns:

```text
start
  -> callback
  -> finally cleanup
```

Focused executable tests prove cleanup after:

```text
callback success
callback failure/rejection
```

and preserve the original callback error on failure.

### Functional Validation Reviewed

The submitted focused tests cover:

```text
dynamic lifecycle / port allocation
outbound message acceptance
generated status webhook
signed inbound webhook
signature verification
configured duplicate delivery
direct Background environment wiring
cleanup after callback success
cleanup after callback failure
```

No real WhatsApp user or production Meta credential is used.

### Validation Evidence Reviewed

The repository-agent Completion Report records:

```text
Node runtime
  v24.19.0

npm test
  9 total
  8 passed
  0 failed
  1 skipped
```

The skipped test is the existing opt-in live Docker Redis test and is unrelated
to the WhatsApp emulator.

Focused emulator suite:

```text
4 passed
0 failed
0 skipped
```

Additional validation:

```text
npm run typecheck
  PASS

npm run lint
  PASS
```

### Independent Architect Inspection

The architect independently confirmed from the submitted bundle:

```text
package.json engines.node = >=24
package-lock root engines.node = >=24
emulator package version = 5.0.1
emulator package engines.node = >=24
withWhatsAppEmulator finally-cleanup implementation present
success cleanup test present
failure cleanup test present
direct Background environment variables present
no production Meta credential present
```

The architect review runtime is Node 22, so the Node-24-only emulator dependency
was not independently executed here. The source/lockfile inspection and the
repository-agent Node 24 execution evidence are sufficient for this bounded
fixture task.

### Architecture Conformance

Accepted.

The emulator remains:

```text
test infrastructure only
```

and is not treated as proof of:

```text
full Meta API compatibility
real-provider behavior
Meta production throughput
Meta production capacity
```

No application business behavior was moved into the fixture.

### Git / Publication

The repository agent stopped at Review and did not commit or push.

Accepted system-test changes are ready for developer commit/push.

### Downstream Coordination

`ARCH-002-SYSTEM-TEST-004` is Complete.

This satisfies its direct dependency edges for:

```text
ARCH-002-SYSTEM-TEST-001
ARCH-002-SYSTEM-TEST-002
```

`SYSTEM-TEST-002` now has all explicit direct dependencies architect-accepted
Complete and is promoted:

```text
pending -> ready
```

`SYSTEM-TEST-001` remains Pending because its explicit direct dependency:

```text
ARCH-002-ADMIN-004
```

is not yet Complete.

No downstream task is automatically claimed or started.
