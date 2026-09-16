---
id: ARCH-012-SHARED-001
architecture_id: ARCH-012
title: Implement, validate and publish the canonical WhatsApp inbound contract
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
- ARCH-011-SHARED-002
enables:
- ARCH-012-MESSAGING-001
- ARCH-012-BACKGROUND-001
created: 2026-09-14
updated: 2026-09-16
---

# ARCH-012-SHARED-001

## Objective
Implement **and publish** one strict, versioned cross-repository contract for inbound WhatsApp customer messages. This single task replaces the previous split between SHARED-001 implementation and SHARED-002 publication.

The task is complete only when the exact validated source has been published to npm and independently verified as consumable by Messaging and Background.

## Why publication is in this task
The contract has no useful downstream state between “implemented” and “published”: `moda_messaging` and `moda_background` must consume an immutable published Shared release. Keeping implementation and publication in one repository-owned task avoids a second artificial lifecycle boundary.

Publication remains the **last phase** of this task. Do not publish before all source validation and package-content checks pass.

## Architectural boundary
This contract represents **provider-normalized communications data only**. It MUST NOT contain Shopify recovery policy, merchant billing, CommerceAgent decisions, database entities, or recovery scheduling.

Producer after publication: `moda_messaging`.
Consumer after publication: `moda_background`.

## Mandatory dependency and release ordering
This task depends on `ARCH-011-SHARED-002` because both initiatives publish `@modainteract/moda-interact-shared` and must not race the package version line.

Do not prepare/start this task while `ARCH-011-SHARED-002` is not architect-accepted Complete.

At task start:

1. inspect launcher-synchronised canonical `origin/main`;
2. read local `package.json` version;
3. read `npm view @modainteract/moda-interact-shared dist-tags.latest`;
4. verify local source contains every previously architect-accepted Shared capability, including ARCH-015 provider-context work;
5. verify local package version and npm `latest` represent the same accepted baseline before choosing the ARCH-012 publication version.

If the canonical source is behind an already-published accepted Shared release, STOP before editing. Do not reconstruct missing source from npm artifacts.

### Deterministic ARCH-012 version rule
After the preflight succeeds, choose the ARCH-012 version using this exact rule:

```text
baseline = architect-accepted npm/latest version after ARCH-011-SHARED-002
ARCH-012 target = next minor version, patch reset to 0

examples:
0.12.0 -> 0.13.0
0.12.3 -> 0.13.0
0.13.7 -> 0.14.0
```

This rule is architect-authorized. Do not choose a patch bump, major bump, prerelease tag or any other version.

If local source version, ARCH-011 completion evidence and npm `latest` do not describe one coherent baseline, STOP for `moda_architect` reconciliation.

## Authorized implementation surface

```text
src/whatsapp.ts                              # new
src/whatsapp.test.ts                         # new
package.json                                 # ./whatsapp export + final version bump
package-lock.json                            # matching export/version metadata when required
```

Do not edit existing billing/provider-status semantics except for mechanically preserving exports while changing package metadata.

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
- `customerPhone`: trim, non-empty, max 64 characters; no tenant lookup/E.164 ownership inference in Shared;
- `contextMessageId`: nullable; non-null must be bounded/non-empty;
- `occurredAt`: offset-aware ISO datetime;
- text: preserve normalized value; min 1, max 4096 characters after validation trimming;
- audio `mediaId`: required bounded/non-empty;
- audio `mimeType` and `sha256`: nullable bounded strings; do not invent values Meta omitted;
- `voice`: nullable;
- unsupported `providerType`: bounded/non-empty and preserves Meta type label;
- strict unknown-field rejection at every object level;
- no raw webhook payload;
- no `shopId`, `conversationId`, `checkoutRecoveryId`, recovery state or merchant identity field.

## Required source tests
Prove at minimum:

1. contextual text parses;
2. contextless text parses;
3. audio parses with media metadata;
4. audio parses with only required `mediaId` and null optional metadata;
5. unsupported provider type parses through explicit union member;
6. blank/oversized identifiers reject;
7. invalid/non-offset datetime rejects;
8. blank/oversized text rejects;
9. tenant/business/raw-payload unknown fields reject;
10. schemaVersion other than 1 rejects;
11. TypeScript discriminated-union narrowing works for text/audio/unsupported.

## Phase 1 — implementation validation
Before changing the package version or publishing, run repository-declared validation. Minimum expected where declared:

```text
npm test
npm run typecheck
npm run build
npm pack --dry-run --json
git diff --check
```

Inspect the dry-run tarball/manifest and prove `./whatsapp` runtime and declarations are included while every pre-existing public entrypoint remains present.

If any source validation fails because of this task, fix it before publication. Do not publish a known-failing source tree.

## Phase 2 — package version and publication
Only after Phase 1 passes:

1. update `package.json` and lockfile root version to the deterministic target;
2. rerun package/build validation required by repository scripts;
3. verify target does not already exist;
4. publish exactly once;
5. verify registry version/tarball/shasum/latest;
6. install the exact published version into an isolated temporary consumer and prove the `./whatsapp` runtime and declaration surface is usable.

Required sequence (substitute the deterministic target calculated above):

```text
npm pack --dry-run --json
npm view @modainteract/moda-interact-shared@<TARGET> version
# previous command must show target is absent / not already published
npm publish --access public
npm view @modainteract/moda-interact-shared@<TARGET> version dist.tarball dist.shasum
npm view @modainteract/moda-interact-shared dist-tags.latest
```

If the target already exists before publication, STOP. Never republish or silently choose another version.

Do not expose npm credentials/tokens in logs or the Completion Report.

## Non-goals

- provider-status schema changes;
- outbound message contracts;
- voice duration policy;
- transcription provider selection;
- Meta webhook parsing;
- database schema changes;
- Shopify/recovery lifecycle.

## Acceptance Criteria

- [ ] one canonical strict inbound contract exists at `@modainteract/moda-interact-shared/whatsapp`;
- [ ] explicit reply context is preserved but optional;
- [ ] audio uses provider media identity, not raw bytes;
- [ ] unsupported inputs are explicit, not empty text;
- [ ] no tenant/business decision is moved into Shared;
- [ ] all pre-existing Shared exports remain compatible;
- [ ] the exact validated source is published once using the deterministic version rule;
- [ ] npm `latest` points at the published ARCH-012 target;
- [ ] an isolated consumer can import the runtime/declarations.

## Stop conditions
STOP and return to `moda_architect` if:

- ARCH-011-SHARED-002 is not accepted Complete;
- canonical Shared source is behind an already-published accepted release;
- local version / npm latest / ARCH-011 evidence disagree;
- the contract requires changing an accepted billing/provider-status schema;
- additive `./whatsapp` export requires removing an accepted export;
- target version already exists before publication;
- publication credentials/permissions are unavailable.

Do not split publication into a new ARCH-012 task.

## Completion protocol
After implementation, validation, publication and clean-consumer verification all pass: update Completion Report, set `status: review`, clear the claim according to launcher protocol, return to `moda_architect`, and STOP. Do not start Messaging or Background.

## Completion Report

### Status
Not started.

### Published Version
TBD.

### Files Changed
TBD.

### Validation Results
TBD.

## Architect Review

### Review Status
Not reviewed.

### Review Notes
TBD.
