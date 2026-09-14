---
id: ARCH-012-SYSTEM-TEST-001
architecture_id: ARCH-012
title: Validate bidirectional WhatsApp text, reply correlation, links and template media
task_kind: system_test
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-012-MESSAGING-001
- ARCH-012-BACKGROUND-001
- ARCH-012-BACKGROUND-003
- ARCH-012-GATEWAY-001
enables: []
created: 2026-09-14
updated: 2026-09-14
---

# ARCH-012-SYSTEM-TEST-001

## Objective
Prove the integrated non-voice ARCH-012 communications path against realistic Meta-shaped traffic and the existing WhatsApp emulator. This task validates communications only; it must not test or redefine when a Shopify recovery should be scheduled.

## Required scenarios

### Inbound explicit reply

```text
existing outbound ConversationMessage with provider wamid
  -> Meta-shaped inbound text with context.id = that wamid
  -> Messaging Shared event
  -> BullMQ
  -> Background exact Conversation resolution
  -> inbound ConversationMessage.inReplyToProviderId persisted
  -> ordered existing turn path
```

Assert a more-recent unrelated conversation cannot steal an explicit reply.

### Inbound contextless reply
Prove:

- one actionable conversation -> routed;
- same-owner multiple recoveries -> existing clarification behaviour;
- cross-tenant candidates -> unresolved/no CommerceAgent;
- no context field is invented by Messaging.

### Outbound text/link
Drive Background outbound transport and assert emulator receives:

- exact text;
- Shopify HTTPS URL unchanged;
- `preview_url` when requested;
- correct Moda sender phone-number ID path;
- returned provider wamid persisted/status-tracked.

### Outbound approved template media/action
Assert serialized template can contain:

- body parameters;
- dynamic image header link;
- dynamic URL-button parameter;
- exact provider template name and provider language code;
- WABA identity is used for template selection while phone-number ID is used for send endpoint.

### Duplicate/failure safety

- duplicate inbound providerMessageId -> one logical inbound message;
- duplicate status webhook -> idempotent lifecycle;
- provider failure -> bounded failure state, no fabricated success;
- malformed/unsupported inbound type -> never becomes empty text agent turn.

## Test ownership / fixtures
Extend the existing WhatsApp Cloud API emulator rather than creating a second emulator. Add only fixtures/capabilities needed to inspect the new request fields and realistic inbound webhook generation.

Use test database/Redis configuration according to existing system-test conventions. Do not call live Meta.

## Out of scope

- Groq/live transcription;
- voice-note media bytes (SYSTEM-TEST-002);
- Shopify abandonment timers/follow-up scheduling;
- merchant Meta onboarding;
- human escalation.

## Acceptance Criteria

- [ ] both reply modes work end to end;
- [ ] cross-tenant contextless ambiguity fails closed;
- [ ] outbound links/template media/URL actions serialize correctly;
- [ ] WABA and phone-number identities remain distinct across integration;
- [ ] duplicate and provider-status behaviour remains idempotent.

## Validation
Run the focused ARCH-012 system scenarios plus the repository-declared full test suite and:

```text
git diff --check
```

If the task targets the deployed Render test environment, record exact service revision/environment evidence using existing system-test deployment conventions; do not silently substitute local-only evidence for a required deployed gate.

## Stop conditions
STOP if any dependency is not architect-accepted/integrated or if the emulator cannot represent a required Meta field without changing application behaviour.

## Completion protocol
Return SYSTEM-TEST-001 to `review`; STOP.

## Completion Report

### Status
Not started.

### Validation Results
TBD.

## Architect Review

### Review Status
Not reviewed.

### Review Notes
TBD.
