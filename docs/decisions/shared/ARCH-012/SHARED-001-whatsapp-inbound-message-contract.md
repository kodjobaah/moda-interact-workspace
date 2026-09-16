---
id: ARCH-012-SHARED-001
architecture_id: ARCH-012
title: Define the canonical inbound WhatsApp message contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-007-SHARED-004
enables:
- ARCH-012-SHARED-002
created: 2026-09-14
updated: 2026-09-16
---

# ARCH-012-SHARED-001

## Objective
Create one strict, versioned cross-repository contract for inbound WhatsApp customer messages. This replaces the incompatible repository-local `WhatsAppInboundEvent` interfaces currently declared by Messaging and Background.

## Architectural boundary
This contract represents **provider-normalized communications data only**. It MUST NOT contain Shopify recovery policy, merchant billing, CommerceAgent decisions, database entities, or recovery scheduling.

Producer after publication: `moda_messaging`.
Consumer after publication: `moda_background`.

## 2026-09-16 Shared integration preflight
Before editing, inspect canonical task-worktree `origin/main`, local `package.json`, and the accepted Shared task history. The supplied 2026-09-16 snapshot shows downstream consumers on `0.11.2` while the included Shared source checkout still reports `0.11.0` and does not visibly contain the accepted ARCH-015 provider-context helpers.

If launcher-synchronised canonical `origin/main` still has that mismatch, **STOP before editing** and return the exact Shared integration gap to `moda_architect`. Do not reconstruct ARCH-015 source from installed npm packages and do not publish from a source tree that omits previously accepted Shared behaviour.

If canonical `origin/main` is already reconciled, continue normally and preserve all accepted Shared exports. This preflight does not change the ARCH-012 v1 WhatsApp schema below.

## Authorized implementation surface
Prefer a dedicated package entrypoint rather than placing the new contract in billing code:

```text
src/whatsapp.ts                              # new
src/whatsapp.test.ts                         # new
package.json                                 # add ./whatsapp export only
```

`package-lock.json` may change only if the repository tooling requires it after the package export edit. Do not edit existing billing behaviour.

## Exact contract
Export:

```text
WHATSAPP_INBOUND_MESSAGE_SCHEMA_VERSION = 1
WhatsAppInboundContentSchema
NormalizedWhatsAppInboundMessageSchema
parseNormalizedWhatsAppInboundMessage(input)
safeParseNormalizedWhatsAppInboundMessage(input)
```

The canonical event must be a strict object with exactly:

```ts
{
  schemaVersion: 1;
  provider: "whatsapp";
  providerAccountId: string;       // Meta WABA identity, webhook entry.id
  providerPhoneNumberId: string;   // Meta metadata.phone_number_id
  providerMessageId: string;       // inbound Meta message.id
  customerPhone: string;           // inbound Meta message.from
  contextMessageId: string | null; // Meta message.context.id when present
  occurredAt: string;              // offset-aware ISO datetime
  content:
    | { type: "text"; text: string }
    | {
        type: "audio";
        mediaId: string;
        mimeType: string | null;
        sha256: string | null;
        voice: boolean | null;
      }
    | {
        type: "unsupported";
        providerType: string;
      };
}
```

Validation rules:

- all identifiers: trim, non-empty, max 256 characters;
- `customerPhone`: trim, non-empty, max 64 characters; do not perform tenant lookup or E.164 ownership inference in Shared;
- `contextMessageId`: nullable, but a non-null value must be bounded/non-empty;
- `occurredAt`: offset-aware ISO datetime;
- text: trim only for validation; preserve actual normalized text value, min 1, max 4096 characters;
- audio `mediaId`: required bounded/non-empty;
- audio `mimeType` and `sha256`: nullable bounded strings, no format invention if Meta omitted them;
- `voice`: nullable because provider payload availability may vary;
- unsupported `providerType`: bounded/non-empty and preserves the Meta message type label;
- strict unknown-field rejection at every object level;
- no raw webhook payload field;
- no `shopId`, `conversationId`, `checkoutRecoveryId`, recovery state or merchant identity field.

## Required tests
Add focused tests proving:

1. valid contextual text message parses;
2. valid contextless text message parses;
3. valid audio/voice event parses with media metadata;
4. audio event with only required `mediaId` and null optional metadata parses;
5. unsupported provider type parses through the explicit unsupported union member;
6. blank/oversized provider/customer/message identifiers are rejected;
7. invalid/non-offset datetime is rejected;
8. blank/oversized text is rejected;
9. `shopId`, `conversationId`, arbitrary raw payload and other unknown fields are rejected;
10. schemaVersion other than 1 is rejected;
11. exact TypeScript discriminated-union narrowing works for `text`, `audio`, and `unsupported`.

## Non-goals

- provider status schema changes;
- outbound message contracts;
- voice duration policy;
- transcription provider selection;
- Meta webhook parsing;
- database schema changes;
- Shopify/recovery lifecycle.

## Acceptance Criteria

- [ ] Messaging and Background can import the same strict inbound-message type/schema from `@modainteract/moda-interact-shared/whatsapp` after publication.
- [ ] The contract preserves explicit reply context without requiring it.
- [ ] Audio is represented by provider media identity, not raw bytes.
- [ ] Unsupported inbound types are explicit rather than silently collapsed into empty text.
- [ ] No tenant/business decision is moved into Shared.
- [ ] Existing Shared exports remain compatible.

## Validation
From `moda-interact-shared/`:

```text
npm test
npm run typecheck
npm run build
npm pack --dry-run --json
git diff --check
```

Inspect the packed manifest and prove `./whatsapp` runtime and declarations are present.

## Stop conditions
STOP and return to `moda_architect` if implementing the contract requires changing an accepted provider-status/billing schema or if the package cannot expose an additive `./whatsapp` entrypoint without removing an accepted export.

## Completion protocol
After all acceptance/validation passes: update Completion Report, set `status: review`, clear the claim according to launcher protocol, return to `moda_architect`, and STOP. Do not publish the package; SHARED-002 owns publication.

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
