---
id: ARCH-005-MESSAGING-002
architecture_id: ARCH-005
title: Resolve conversation language and localise CommerceAgent responses
task_kind: implementation
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
status: superseded
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-005-MESSAGING-001
enables:
  - ARCH-005-SYSTEM-TEST-002
created: 2026-09-05
updated: 2026-09-06
---

# Resolve conversation language and localise CommerceAgent responses

## Objective

Allow an active WhatsApp conversation to establish and update its customer
language independently from merchant/country/phone context, and instruct
CommerceAgent to respond in that resolved language.

## Language resolver

Implement an explicit resolver with precedence:

```text
customer-explicit
detected
shopify
merchant-default
platform-default
```

Persist both:

```text
languageTag
languageSource
```

## Detection boundary

Introduce a provider-agnostic detector contract:

```text
detect(message) ->
  languageTag
  confidence
```

Exact model/provider implementation may use the existing agent stack.

Do not persist detector explanations.

## Confidence / stability

Define and test policy preventing language flapping for:

```text
short messages
emoji-only messages
URLs
numbers
ambiguous words
```

A confident clear language change may update the conversation.

A low-confidence detection should leave the current language unchanged.

## Explicit preference

If the product currently has no explicit customer language-preference command,
provide the internal resolver precedence now without inventing a user-facing
command.

Future explicit preference must be able to outrank detection.

## CommerceAgent

Pass the resolved language to CommerceAgent as structured context.

Instruction invariant:

```text
respond in the resolved conversation language unless the customer clearly
changes language and the resolver accepts that change
```

Do not ask the LLM to infer merchant prices, currency, URLs, order state or
policies.

Those remain authoritative structured data.

## Mixed language

Tests must cover a customer who begins in one language and clearly switches to
another.

The system should update only after the resolver accepts the new language.

## WhatsApp active conversation

This task concerns free-form active-conversation responses.

It does not bypass provider template rules for proactive messages.

## Acceptance criteria

- [ ] conversation language resolver follows explicit precedence.
- [ ] language source is persisted.
- [ ] detector is provider-agnostic.
- [ ] confidence policy prevents short-message language flapping.
- [ ] clear language switch is supported.
- [ ] phone/country cannot override explicit/detected language.
- [ ] CommerceAgent receives structured resolved language.
- [ ] free-form response language follows resolved language.
- [ ] authoritative commerce facts remain structured/unchanged.
- [ ] no proactive template approval bypass exists.
- [ ] multilingual focused tests pass.
- [ ] full tests/build/typecheck/diff checks pass subject to baseline.

## Completion Report

### Status

Not started.

## Architect Review

### Review Status

Superseded before execution — ownership correction.

### Reason

Language detection, durable Conversation updates, CommerceAgent structured
context and free-form outbound replies all execute in `moda-interact-background`.
`moda-interact-messaging` only authenticates/normalises inbound Meta webhook
traffic and enqueues it. The task is therefore rehomed to
`ARCH-005-BACKGROUND-004`.
