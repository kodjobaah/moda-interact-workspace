---
id: ARCH-012-BACKGROUND-003
architecture_id: ARCH-012
title: Establish Moda-owned WhatsApp sender identity and outbound transport capabilities
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 13
executor: copilot
claimed_at: 2026-09-16T11:46:29Z
attempt: 1
depends_on:
- ARCH-005-BACKGROUND-003
- ARCH-007-BACKGROUND-004
- ARCH-010-BACKGROUND-013
enables:
- ARCH-012-BACKGROUND-001
- ARCH-012-GATEWAY-001
- ARCH-012-SYSTEM-TEST-001
created: 2026-09-14
updated: 2026-09-16
---

# ARCH-012-BACKGROUND-003

## Objective
Harden the outbound WhatsApp transport as a Moda-owned communications capability. v1 uses one Moda sender, but business callers must no longer encode the assumption that `WHATSAPP_PHONE_NUMBER_ID` is the provider account/WABA identity or that a single sender can never be abstracted later.

## Product invariant
Merchants do **not** provide a WABA, Meta app, access token or WhatsApp phone number. The sender is Moda-owned infrastructure.

ARCH-012 v1 provisions exactly one active production sender; this task creates an abstraction, not a load balancer or sender pool database.

## Current defect to correct
`WhatsAppService.getProviderAccountId()` currently returns `WHATSAPP_PHONE_NUMBER_ID`, while template selection treats that value as `providerAccountId`. WABA/account identity and phone-number sender identity are distinct concepts and must no longer be conflated.

## Authorized implementation surface
Expected files:

```text
src/services/whatsapp.service.ts
src/services/outbound-whatsapp-admission.service.ts
src/integration/whatsapp/types.ts
src/services/whatsapp-template-selector.service.ts     # only identity naming/wiring if required
focused WhatsApp/outbound/template tests
```

No database schema changes.

## 2026-09-16 outbound-admission compatibility requirement
`src/services/outbound-whatsapp-admission.service.ts` now contains accepted ARCH-010 execution gates that were not present in the original ARCH-012 snapshot. Preserve them exactly while extending the transport:

```text
admitted result retains shopId
executionEligibility.evaluate(shopId) is re-run immediately before provider send
NO_CONTRACT -> contract-required
SUBSCRIPTION_FROZEN -> subscription-frozen
denied prepared messages are cleaned up through existing failPrepared behaviour
```

Do not simplify the service back to the older admission-only implementation, and do not bypass eligibility for text, template, link-preview, image-header or URL-button sends. New outbound capabilities must pass through the same accepted admission/provider lifecycle.

## Sender configuration abstraction
Create a bounded resolver/config type equivalent to:

```ts
type ModaWhatsAppSender = {
  providerAccountId: string;      // WABA ID
  providerPhoneNumberId: string;  // Cloud API sender phone-number ID
};
```

Credentials remain encapsulated inside the transport and are not returned to business services.

Read v1 configuration from:

```text
WHATSAPP_BUSINESS_ACCOUNT_ID
WHATSAPP_PHONE_NUMBER_ID
WHATSAPP_ACCESS_TOKEN
WHATSAPP_API_BASE_URL              # existing optional override
```

Exactly one sender is required in v1. Do not invent shop->sender persistence or automatic balancing.

Template selection must receive true `providerAccountId = WHATSAPP_BUSINESS_ACCOUNT_ID`, not the phone-number ID.

## Outbound transport surface
Preserve existing `sendWhatsAppText` and `sendWhatsAppTemplate` behaviours while extending typed capability:

### Text
Support:

```ts
{
  to: string;
  text: string;
  previewUrl?: boolean;
  replyToProviderMessageId?: string;
}
```

Serialize `text.preview_url` only when requested. Ordinary HTTPS hyperlinks in `text.body` remain untouched.

### Template
Support approved template components needed by ARCH-012 communications:

```text
body text parameters               existing behaviour preserved
optional dynamic image header      by HTTPS link
optional dynamic URL button value  explicit button index + bounded text/suffix parameter
```

Use Meta's template component shape; do not synthesize an unapproved template, arbitrary button definition or template approval workflow. The caller supplies the approved template name/language and only runtime parameters allowed by that template.

A static URL already embedded in an approved template requires no runtime URL parameter; do not force one.

### Reply context
Allow an outbound text response to include `context.message_id` when Background intentionally replies to a specific customer message. Do not require it for every ordinary conversation response.

## Sender identity / provider response
All sends:

- use `providerPhoneNumberId` in the Graph `/messages` path;
- preserve returned provider `wamid` exactly;
- use existing bounded provider timeout/error classification;
- never log access tokens, authorization headers or customer message body as generic structured metadata;
- preserve ARCH-007 outbound admission and message accounting; this task must not bypass it.

## Required tests

- missing WABA ID fails configuration with bounded error;
- missing phone-number ID/token fails boundedly;
- template selector receives WABA ID, not phone-number ID;
- text send serializes `preview_url: true` only when requested;
- text body containing Shopify HTTPS URL is preserved;
- optional `context.message_id` serializes correctly;
- template body params remain backward-compatible;
- template image-header link serializes exact approved component form;
- template dynamic URL button parameter serializes exact index/value;
- static-template URL case requires no invented runtime component;
- existing provider message ID/status lifecycle remains intact;
- prepared text/template sends still re-check shop execution eligibility immediately before provider invocation;
- `contract-required` and `subscription-frozen` suppression reasons remain distinct;
- admitted results continue to retain `shopId`;
- no merchant-specific WhatsApp credential input is introduced.

## Non-goals

- multiple active senders in v1;
- sender allocation/balancing;
- merchant Embedded Signup;
- template creation/approval automation;
- outbound generated voice;
- recovery timing/follow-up policy.

## Acceptance Criteria

- [ ] WABA identity and sender phone identity are separate in code;
- [ ] one Moda sender remains simple to operate;
- [ ] outbound text can carry normal hyperlinks/link previews;
- [ ] outbound approved templates can carry image headers and URL-button parameters;
- [ ] accepted outbound admission/provider-status behaviour is preserved.

## Validation
Run focused transport/admission/template tests plus repository-declared full tests/build/typecheck/Prisma validation and:

```text
git diff --check
```

## Stop conditions
STOP if making WABA identity truthful requires a durable sender database/pool, or if existing template rows cannot be interpreted without a data migration. Report the exact blocker; do not silently repurpose another field.

## Completion protocol
Return BACKGROUND-003 to `review`; STOP.

## Completion Report

### Status
Not started.

### Files Changed
TBD.

### Validation Results
TBD.

## Architect Review

### Review Status
Not reviewed.

### Review Notes
TBD.
