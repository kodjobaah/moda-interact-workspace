---
id: ARCH-002-SYSTEM-TEST-004
architecture_id: ARCH-002
title: Add WhatsApp Cloud API emulator test infrastructure
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: ready
priority: 31
executor: null
claimed_at: null
attempt: 0
depends_on: []
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

- [ ] inspect system-test Node/runtime/orchestration;
- [ ] add exact `@whatsapp-cloudapi/emulator@5.0.1`;
- [ ] isolate Node 24 requirement if necessary;
- [ ] implement start/readiness/stop lifecycle;
- [ ] use dynamic ports;
- [ ] expose base URL and synthetic provider configuration;
- [ ] implement bounded local webhook receiver/fixture support;
- [ ] prove outbound message API handling;
- [ ] prove inbound signed webhook handling;
- [ ] prove duplicate webhook generation;
- [ ] prove status webhook generation;
- [ ] inspect current Moda outbound base-URL configurability;
- [ ] document integrated-test wiring contract;
- [ ] document that real-provider smoke testing remains separate.

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

- [ ] system tests can start/stop their own emulator instance;
- [ ] no fixed developer port is required;
- [ ] outbound API messages can be sent to the emulator;
- [ ] inbound messages can be simulated;
- [ ] signed webhooks can exercise the real signature boundary;
- [ ] duplicate deliveries can be generated deterministically;
- [ ] status webhooks can be generated;
- [ ] no production Meta credential is required;
- [ ] Node 24 requirement does not silently change unrelated service runtimes;
- [ ] outbound Moda base-URL injection capability is confirmed, or the task is
      returned Blocked with concrete evidence;
- [ ] emulator use is documented as test-only, not proof of Meta production
      compatibility/capacity;
- [ ] implementation changes are ready for developer commit/push;
- [ ] repository agent does not commit or push.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The emulator supports only its documented WhatsApp Cloud API subset. Integrated
tests must not infer support for provider routes the emulator does not
implement.

### Unresolved Issues

Current outbound WhatsApp client base-URL configurability must be confirmed by
source inspection during this task.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Pending
