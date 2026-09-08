---
id: ARCH-005-SYSTEM-TEST-002
architecture_id: ARCH-005
title: Verify multilingual conversation language behaviour
task_kind: verification
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-005-SYSTEM-TEST-001
  - ARCH-005-BACKGROUND-004
enables: []
created: 2026-09-05
updated: 2026-09-06
---

# Verify multilingual conversation language behaviour

## Objective

Prove active WhatsApp conversations can resolve, retain and change language
without telephone/country coupling and without weakening proactive template
rules.

## Required scenarios

### Initial Shopify language

Conversation starts from Shopify-derived language:

```text
languageSource = shopify
```

when no stronger customer preference/detection exists.

### Merchant fallback

No Shopify/customer language:

```text
merchant default
```

is used with:

```text
languageSource = merchant-default
```

### CommerceAgent language upgrade

Customer sends a clear substantive message in another language. The existing
CommerceAgent run returns its customer reply plus bounded detected-language
metadata; there must not be a separate language-detection model call.

With sufficient application-accepted confidence:

```text
languageTag changes
languageSource = detected
```

The same CommerceAgent turn responds in the new language.

### Ambiguous message

Emoji/short URL/numeric/ambiguous message must not cause a language change. The
CommerceAgent structured result may report null/insufficient detection and the
existing durable language remains stable.

### Regional stability

Text-only detection must not invent regional specificity or degrade a more
specific durable locale:

```text
en-GB + detected en -> en-GB
fr-CA + detected fr -> fr-CA
```

A clear different-base-language switch such as `en-GB -> fr` may be accepted.

### Stale-turn protection

If a newer inbound message advances `inboundVersion` while CommerceAgent is
processing an earlier turn, the stale result must neither send its reply nor
mutate durable conversation language.

### Explicit precedence

If an explicit customer preference representation exists by implementation
time, prove it outranks detection.

If no user-facing explicit-preference feature exists, verify the resolver unit/
integration contract rather than inventing UI.

### Phone/country independence

A destination phone associated with one calling country must be able to conduct
the conversation in a different language.

### Commerce facts

Across language changes, verify structured:

```text
price
currency
product/order facts
URLs
```

remain unchanged except presentation formatting.

### Template boundary

A free-form active-conversation language change must not make an unapproved
proactive template variant selectable.

## Acceptance criteria

- [ ] Shopify initial-language path passes.
- [ ] merchant fallback passes.
- [ ] confident CommerceAgent-reported language update passes without a separate detector call.
- [ ] ambiguous message does not flip language.
- [ ] same-base detection preserves a more-specific durable locale.
- [ ] stale agent result cannot mutate language.
- [ ] language source changes correctly.
- [ ] phone/country cannot override resolved language.
- [ ] the same CommerceAgent turn responds in the confidently detected switched language.
- [ ] authoritative commerce facts remain stable.
- [ ] proactive template approval boundary remains intact.
- [ ] evidence avoids raw customer PII.
- [ ] system-test validation/build/diff checks pass.

## Completion Report

### Status

Not started.

## Architect Review

### Review Status

Pending
