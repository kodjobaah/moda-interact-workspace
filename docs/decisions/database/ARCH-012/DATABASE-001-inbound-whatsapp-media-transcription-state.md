---
id: ARCH-012-DATABASE-001
architecture_id: ARCH-012
title: Persist inbound WhatsApp media and transcription lifecycle state
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 12
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-007-DATABASE-006
enables:
- ARCH-012-BACKGROUND-001
- ARCH-012-BACKGROUND-002
created: 2026-09-14
updated: 2026-09-16
---

# ARCH-012-DATABASE-001

## Objective
Extend durable `whatsapp.ConversationMessage` state so inbound text, voice-note media provenance and asynchronous transcription can be represented truthfully without storing raw audio bytes.

## Current-state constraint
`ConversationMessage.content` alone is insufficient because the current worker collapses non-text inbound messages to an empty string. ARCH-012 needs a durable two-phase voice lifecycle: reserve/dedupe the provider message first, then finalize the transcript before it becomes an ordinary conversation turn.

## Authorized implementation surface

```text
prisma/schema.prisma
prisma/migrations/<timestamp>_arch012_inbound_whatsapp_media/*
docs/generated/prisma-erd.puml              # regenerated artifact
scripts/validate-arch012-whatsapp-media-schema.mjs   # new bounded validator
package.json                                 # only if adding validator script is consistent with repository convention
```

Do not edit application repositories.

## 2026-09-16 migration baseline
The current database snapshot contains later ARCH-014/015 migrations through `20260916083000_arch015_refund_correction_evidence`. Create the ARCH-012 migration **after the current canonical latest migration** using the repository's normal timestamp naming; do not backdate it to the original 2026-09-14 overlay date and do not edit/reorder existing migrations.

The existing `ConversationMessage` model itself is unchanged on the fields ARCH-012 extends, so the schema design below remains valid.

## Exact schema additions
Add enums in the `whatsapp` schema:

```text
MessageContentType
  TEXT
  AUDIO
  UNSUPPORTED

MessageTranscriptionStatus
  NOT_REQUIRED
  PENDING
  COMPLETED
  REJECTED
  FAILED
```

Extend `ConversationMessage` with:

```text
contentType              MessageContentType        @default(TEXT)
providerMediaId          String?
providerMediaMimeType    String?
providerMediaSha256      String?
mediaDurationMs          Int?
transcriptionStatus      MessageTranscriptionStatus @default(NOT_REQUIRED)
transcriptionProvider    String?
transcriptionModel       String?
transcriptionFailureCode String?
transcriptionCompletedAt DateTime?
```

Field semantics:

- `content` remains the canonical text presented to CommerceAgent/history after an audio message is successfully transcribed;
- raw audio bytes and provider download URLs MUST NOT be persisted;
- `providerMediaId` is provider media identity only, not a local storage pointer;
- text/unsupported messages normally use `NOT_REQUIRED`;
- audio reservation begins `PENDING`;
- successful transcript -> `COMPLETED`;
- duration/policy/media rejection -> `REJECTED`;
- terminal provider/transcription failure -> `FAILED`;
- `mediaDurationMs` must never be negative;
- `transcriptionFailureCode`, provider and model are bounded operational metadata; do not store arbitrary provider error prose.

Add a migration-level check for non-negative `mediaDurationMs` if PostgreSQL/Prisma migration conventions permit it without introducing an unsupported Prisma representation. If not, enforce via validator/application and document the limitation rather than inventing raw database mechanisms outside repository convention.

## Required validator assertions
The new schema validator must prove:

- both enums and exact members exist;
- every field above exists on `ConversationMessage` with the required nullability/defaults;
- no raw audio/blob/URL persistence column is introduced;
- `providerMessageId` remains unique;
- existing conversation ordering/coalescing fields remain unchanged.

## Non-goals

- sender/WABA configuration persistence;
- merchant WhatsApp accounts;
- template component catalogue redesign;
- recovery lifecycle fields;
- audio object storage.

## Acceptance Criteria

- [x] one inbound provider message can be durably reserved before transcription through existing unique `providerMessageId` semantics;
- [x] voice provenance/transcription lifecycle can be represented without fake empty-text semantics;
- [x] raw audio is not stored in PostgreSQL;
- [x] existing text conversations remain backward-compatible through defaults;
- [x] migration and ERD are generated normally.

## Validation
From `moda-interact-database/`:

```text
npm run prisma:validate
npm run prisma:generate
npm run test:first-production-baseline
node scripts/validate-arch012-whatsapp-media-schema.mjs
npm run erd:puml
git diff --check
```

If local PostgreSQL is unavailable, do not fabricate migration-application evidence. Record the exact environment blocker while still producing/validating the migration artifact to the extent repository tooling permits.

## Stop conditions
STOP if this task would require changing recovery/billing schema, storing audio binaries, or creating a merchant-owned WhatsApp account model.

## Completion protocol
Return only DATABASE-001 to `review`; do not start dependent Background work.

## Completion Report

### Status
Ready for architect review.

### Physical worktree isolation

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-012-DATABASE-001`
- Parent branch: `task/ARCH-012-DATABASE-001`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-012-DATABASE-001`
- Implementation branch: `task/ARCH-012-DATABASE-001`
- Shared implementation checkout switched or mutated: no
- Another task worktree reused: no

### Launcher evidence

- Claim commit: `ec2bec60bb18ae7a2019fa09343d498d817de6bb`
- Attempt: `2`
- Dependency gate: passed (`ARCH-007-DATABASE-006` complete)
- Parent origin/main incorporated: already-current
- Implementation origin/main incorporated: already-current
- Recursive submodule sync/update: passed; no submodule entries

### Files changed

- `prisma/schema.prisma`
- `prisma/migrations/20260916100000_arch012_inbound_whatsapp_media_transcription_state/migration.sql`
- `scripts/validate-arch012-whatsapp-media-schema.mjs`
- `docs/generated/prisma-erd.puml`

### Implementation

- Added `MessageContentType` and `MessageTranscriptionStatus` in the `whatsapp` schema.
- Added durable media provenance and transcription lifecycle fields with backward-compatible defaults for existing text messages.
- Added a PostgreSQL check constraint preventing negative media duration.
- Preserved unique `providerMessageId` deduplication and existing conversation ordering/coalescing fields.
- Added structural validation proving exact enum members, field types/defaults, no raw audio or URL persistence fields, and append-only migration safety.
- Regenerated the PlantUML ERD.

### Validation Results

- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- `npm run test:first-production-baseline`: passed.
- `node scripts/validate-arch012-whatsapp-media-schema.mjs`: passed.
- `npm run erd:puml`: passed.
- `git diff --check`: passed.
- Implementation commit: `655ff35` (pushed).
- No application repositories, recovery/billing schema, raw audio bytes, provider URLs, or merchant account models were changed.

### Rework Attempt 2

- The latest Architect Review section contains `Not reviewed`/`TBD` and no
  `Changes Requested` items; no source correction was identified for this
  attempt.
- Revalidated the existing implementation from the prepared implementation
  worktree; all task-required validation passed.
- The task remains bounded to DATABASE-001 and is returned to `review` without
  starting dependent Background work.

## Architect Review

### Review Status
Not reviewed.

### Review Notes
TBD.
