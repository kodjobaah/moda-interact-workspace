---
id: ARCH-005-BACKGROUND-003
architecture_id: ARCH-005
title: Send selected approved WhatsApp template for proactive recovery
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 55
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-005-BACKGROUND-002
enables:
  - ARCH-005-SYSTEM-TEST-001
created: 2026-09-06
updated: 2026-09-06T01:19:34Z
---

# Send selected approved WhatsApp template for proactive recovery

## Architecture

The current proactive recovery path persists an outbound intent and then calls
`WhatsAppService.sendWhatsAppText`. That does not consume the provider-approved
locale variant selected by BACKGROUND-002.

This task closes the runtime gap: proactive recovery must send the selected Meta
template rather than an arbitrary free-form recovery text. Active-conversation
free-form replies remain separate and continue through the existing text-send
path.

## Objective

Integrate the accepted BACKGROUND-002 selection result into the actual proactive
recovery send path, preserving provider approval, deterministic locale choice,
existing message lifecycle/idempotency and bounded provider failures.

## Context

Relevant existing files include:

```text
src/services/checkout-recovery.service.ts
src/services/conversation.message.service.ts
src/services/whatsapp.service.ts
src/integration/whatsapp/types.ts
```

Inspect current code before editing; keep changes bounded to proactive template
sending and its focused tests.

## Scope

- Load/resolve the template using the accepted BACKGROUND-002 boundary.
- Add a provider template-send operation to the existing Background WhatsApp
  integration/service.
- Send explicit provider template name and provider language code; do not derive
  either from canonical locale.
- Preserve `providerMessageId` and existing pending/sent/failed message lifecycle.
- Persist a truthful outbound-history representation for the template send. The current
  English `buildRecoveryMessage(...)` text is not the provider template body and MUST NOT
  be stored as though it were the customer-visible message when a template is sent.
  DATABASE-002 does not currently persist approved localized template body snapshots, so
  this task must use a bounded internal template-send descriptor rather than fabricate
  localized copy.
- Use locale-aware canonical values only for approved template parameters where
  parameters are required.
- Map provider rejection into bounded operational outcomes.
- Ensure unknown market capability (`provider-check-required`) is allowed to reach
  the provider; a real provider rejection is authoritative.

## Out of Scope

- Free-form active-conversation replies.
- New template approval/creation automation.
- AI translation of proactive templates.
- New country allowlists.
- Modifying `moda-interact-messaging`.
- New database schema unless an actual blocking persistence requirement is found;
  if one is found, STOP and return it to the architect rather than creating a local
  migration.

## Requirements

### Provider send

The outbound request must use the provider-template send mode and explicit values
from the selected catalogue row, conceptually:

```text
type = template
template.name = providerTemplateName
template.language.code = providerLanguageCode
```

Do not use `providerTemplateId` in place of the provider template name unless the
actual inspected provider API explicitly requires it.

### Recovery workflow

The proactive recovery send path must no longer bypass template selection by
calling free-form `sendWhatsAppText` for the initial recovery message.

If no approved selectable template exists, do not send ad-hoc translated or
free-form proactive content. Return/record the bounded unavailable outcome defined
by the workflow.

### Persisted outbound history

The proactive template send and the durable `ConversationMessage` history must describe
the same action. Do not call `buildRecoveryMessage(event)` and persist that English
free-form text when the provider request actually sends a selected Meta template.

Until an architecture explicitly adds approved template-body snapshots/parameter metadata
to the catalogue, persist a deterministic bounded descriptor equivalent to:

```text
[WhatsApp template sent; purpose=checkout-recovery; template=<providerTemplateName>; canonicalLanguage=<canonicalLanguageTag>; providerLanguage=<providerLanguageCode>]
```

The exact punctuation may differ, but the persisted content MUST:

- state that an approved WhatsApp template was sent;
- identify the recovery purpose;
- identify the selected provider template name;
- record canonical and provider language identifiers separately;
- NOT claim to be the exact customer-visible localized body;
- NOT contain arbitrary provider rejection prose;
- NOT synthesize/translate customer-visible copy.

This is required because `CheckoutRecoveryService.getAgentContext()` later feeds outbound
`ConversationMessage.content` into the CommerceAgent history. A French template send must
not appear to the agent as an English free-form message that the customer never received.

Do not add a database migration for this Attempt 2 correction. If exact rendered template
body persistence is required, STOP and return that schema requirement to `moda_architect`.

### Market unknown

If BACKGROUND-002 returns a selected template with
`marketCapability = provider-check-required`, attempt the provider template send.
Do not block merely because local capability is unknown.

If the provider rejects the market/template send, map that failure to a bounded
operational reason without persisting arbitrary provider prose as business state.

### Active conversation boundary

Do not replace existing free-form `sendWhatsAppText` calls that are genuinely
inside an active customer conversation. This task only changes proactive recovery
template sending.

## Work Items

- [x] Inspect the accepted BACKGROUND-002 selector contract.
- [x] Extend WhatsApp integration types/service for provider template send.
- [x] Integrate selection into proactive recovery send.
- [x] Preserve existing pending -> sent/failed persistence and provider message id.
- [x] Add bounded provider rejection handling.
- [x] Add focused provider-body and recovery-flow tests.
- [x] Prove active-conversation text sends are unchanged.
- [x] Attempt 2: replace fabricated free-form recovery history with a truthful bounded
  template-send descriptor.
- [x] Attempt 2: add a regression proving a non-English selected template does not persist
  the old English `buildRecoveryMessage(...)` content.
- [x] Attempt 2: rerun focused provider/recovery validation and `git diff --check`.

## Interfaces / Contracts

Consumes the accepted BACKGROUND-002 selection result and existing DATABASE-002
provider template fields. No new cross-service contract is introduced.

## Dependencies

- ARCH-005-BACKGROUND-002.

## Enables

- ARCH-005-SYSTEM-TEST-001.

## Acceptance Criteria

- [x] proactive recovery path consumes BACKGROUND-002 selection.
- [x] proactive recovery does not bypass approval with free-form text.
- [x] provider request uses selected template name and provider language code.
- [x] canonical languageTag is not substituted for provider language code.
- [x] providerMessageId persistence remains intact.
- [x] no-template outcome causes no proactive send.
- [x] unsupported market causes no proactive send.
- [x] provider-check-required is allowed to reach provider send.
- [x] actual provider rejection maps to bounded operational outcome.
- [x] active-conversation free-form replies remain unchanged.
- [x] no AI translation/provider approval bypass exists.
- [x] persisted proactive outbound history truthfully represents a template send rather
  than storing unsent English free-form recovery copy.
- [x] selected non-English template regression proves canonical/provider language metadata
  is persisted without pretending it is the localized provider body.
- [x] focused/full tests, build/typecheck and `git diff --check` pass subject to baseline.

## Validation

Include focused tests that inspect the serialized provider request body and prove:

```text
selected en-GB canonical / en_GB provider -> provider sends en_GB
selected fr-CA canonical with provider-specific code -> exact provider code is preserved
unknown market -> provider call occurs
known unsupported market -> provider call does not occur
no approved template -> provider call does not occur
provider rejection -> bounded failure
active conversation -> existing text-send path unchanged
fr-CA selected template -> pending message stores bounded template descriptor; it does NOT
                           store the English buildRecoveryMessage(...) text
```

Run repository-standard validation and `git diff --check`.

## Implementation Notes

No further implementation correction is required for this task. The old
`buildRecoveryMessage(...)` helper may remain as unused legacy code; it is not
part of the proactive template-send runtime after this task. Do not remove it
inside this accepted task merely for cleanup.

## Completion Report

### Status

Implemented and architect-accepted after Attempt 2.

### Attempt 1 — provider template send

- Added typed `sendWhatsAppTemplate` support with explicit provider template
  name and provider language code, preserving the active-conversation text-send
  method.
- Integrated the accepted BACKGROUND-002 selector into proactive checkout
  recovery using the configured WhatsApp provider account.
- Suppressed provider calls for unavailable templates and unsupported markets;
  allowed `provider-check-required` selections to reach the provider.
- Preserved pending, sent, failed and `providerMessageId` persistence.

Validation recorded by the implementation agent:

- focused provider/recovery tests: 24 passed;
- full suite: 157 passed, 4 skipped, with 3 known unrelated baseline failures;
- build, Prisma validation and `git diff --check`: passed.

### Attempt 2 — truthful outbound history

- Replaced fabricated `buildRecoveryMessage(...)` persistence with a bounded
  template-send descriptor containing purpose, provider template name, canonical
  language and provider language.
- Added a `fr-CA` regression proving the old English recovery copy is neither
  built nor persisted for a selected non-English template.

Validation recorded by the implementation agent:

- focused proactive recovery tests: 17 passed;
- full suite: 161 passed, 4 skipped, with 3 known unrelated baseline failures;
- build, Prisma validation and `git diff --check`: passed.

## Architect Review

### Attempt 1 — Changes Requested

The provider-template send path was correct, but durable outbound history stored
the old English `buildRecoveryMessage(...)` text even when Meta actually sent a
selected non-English approved template. That would have supplied false assistant
history to the CommerceAgent. Attempt 2 was requested to persist a truthful,
bounded template-send descriptor instead.

### Attempt 2 — Accepted

Accepted. Architect inspection of the returned workspace confirmed:

- the proactive path no longer calls `buildRecoveryMessage(...)`;
- `buildRecoveryTemplateDescriptor(...)` records the recovery purpose, selected
  provider template name, canonical language tag and provider language code as
  separate values;
- the descriptor explicitly identifies the action as a WhatsApp template send
  and does not claim to contain the exact localized provider body;
- the `fr-CA` regression proves the unsent English recovery copy is neither built
  nor persisted;
- the selected approved template, `provider-check-required` behaviour, provider
  message-id lifecycle and pending/sent/failed state transitions remain intact;
- active-conversation free-form replies remain outside this proactive template
  path.

The bounded descriptor is intentionally an interim truthful history
representation because DATABASE-002 does not persist approved localized body
snapshots. Exact rendered body persistence would require a separate architecture
decision if it becomes necessary.

`ARCH-005-BACKGROUND-003` is Complete. `ARCH-005-SYSTEM-TEST-001` remains Pending
until all of its other implementation dependencies, including SHOPIFY-001 and
SHOPIFY-002, are Complete and architect-accepted.
