---
id: ARCH-006-SHARED-001
architecture_id: ARCH-006
title: Define merchant communications contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-005-SHARED-001
  - ARCH-006-DATABASE-001
enables:
  - ARCH-006-SHARED-002
created: 2026-09-05
updated: 2026-09-05
---

# Define merchant communications contracts

## Luna execution guidance

Inspect architect-accepted ARCH-005 shared language primitives first and reuse them. Do not create another language-tag validator.

Inspect current shared BullMQ queue/job conventions before adding ARCH-006 contracts.

## Required values

```text
MerchantSupportMessageKind:
  ADMINISTRATIVE
  SYSTEM
  MERCHANT

MerchantSupportMessageState:
  PROCESSING
  AVAILABLE
  FAILED

MerchantMessageTranslationStatus:
  PENDING
  COMPLETE
  FAILED

MerchantSystemNotificationCode:
  SUBSCRIPTION_ENDED
```

Shared values must align with database enums.

## Queue contract

```text
queueName: merchant-communications
jobName: translate-message
jobName: reconcile-message-translations
```

Do not reuse `whatsapp-events`.

## Translate job payload

Strict equivalent:

```ts
{
  messageId: string;
  targetLanguageTag: CanonicalLanguageTag;
}
```

Do not include message body.

## Deterministic job ID

Provide/reuse collision-safe helper from `messageId + canonical targetLanguageTag`.

Do not include source body in ID.

## System notification

Only live code:

```text
SUBSCRIPTION_ENDED
version 1
```

Do not add speculative future codes as active enum values.

## Acceptance

- values align with DB;
- queue/jobs canonical;
- strict minimal payload;
- ARCH-005 BCP-47 validation reused;
- collision-safe job ID;
- only SUBSCRIPTION_ENDED live;
- existing shared contracts unaffected;
- tests cover invalid language, malformed IDs, strict extras;
- tests/typecheck/build/diff pass.

## Completion Report

### Status

Not started.

## Architect Review

### Review Status

Pending
