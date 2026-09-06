---
id: ARCH-005-SHOPIFY-002
architecture_id: ARCH-005
title: Introduce merchant UI locale and standards-aware formatting
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-005-SHARED-002
  - ARCH-005-DATABASE-001
enables:
  - ARCH-005-SYSTEM-TEST-001
created: 2026-09-05
updated: 2026-09-05T19:38:00Z
---

# Introduce merchant UI locale and standards-aware formatting

## Objective

Create the merchant-app internationalisation foundation without coupling
merchant UI language to customer conversation language.

## Merchant locale

Resolve merchant UI locale independently from customer context.

Use existing Shopify/app locale context where authoritative, otherwise merchant
default/platform fallback.

Persist/configure the merchant default through the schema introduced by
DATABASE-001.

## Translation framework

Introduce a repository-appropriate translation catalogue abstraction.

Requirements:

```text
stable message keys
locale catalogues
fallback catalogue
interpolation
plural-aware messages where needed
```

Do not scatter:

```ts
if (locale === ...)
```

through React components.

Initial catalogue coverage may focus on the merchant surfaces touched by
ARCH-005 and shared layout/navigation primitives.

The architecture must allow more translations without code branching.

## Formatting

Centralise helpers for:

```text
money
date/time
number
percentage
relative/short dates where used
```

Use:

```text
Intl.NumberFormat
Intl.DateTimeFormat
Intl.PluralRules
```

or equivalent.

Currency comes from the relevant commerce object.

Do not infer currency from locale.

## Time zone

Display merchant operational timestamps using merchant timezone where the UI
already presents local operational time.

Authoritative stored values remain UTC.

Do not silently reinterpret UTC database instants.

## Direction

Internationalised components/helpers must not force LTR assumptions.

Use `dir=auto` or a locale-direction helper where appropriate for text
containers touched by this task.

A complete RTL redesign is out of scope.

## Pending recoveries

Ensure the ARCH-004/ARCH-003 pending-recovery timestamp formatting uses the new
shared merchant locale/timezone formatter without changing its scheduling
semantics.

## Customer independence

Tests must prove changing merchant UI locale does not change:

```text
Conversation.languageTag
WhatsApp template language
checkout currency
```

## Acceptance criteria

- [ ] merchant UI locale resolver exists.
- [ ] translation catalogue abstraction exists.
- [ ] no country switch is used for UI language.
- [ ] money formatter requires explicit currency.
- [ ] dates use locale/timezone-aware formatter.
- [ ] stored UTC values remain unchanged.
- [ ] internationalised components do not assume LTR.
- [ ] pending-recovery UI adopts shared formatting.
- [ ] merchant locale cannot overwrite customer conversation language.
- [ ] representative locale component/route tests pass.
- [ ] full tests/build/lint/diff checks pass subject to baseline.

## Completion Report

### Status

Not started.

## Architect Review

### Review Status

Pending
