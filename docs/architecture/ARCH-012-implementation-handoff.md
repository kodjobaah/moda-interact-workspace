# ARCH-012 Implementation Handoff — deterministic communications contracts

Date: 2026-09-14
Coordinator: `moda_architect`
Architecture: [`ARCH-012-moda-managed-whatsapp-communications.md`](ARCH-012-moda-managed-whatsapp-communications.md)

## Binding boundary

ARCH-012 owns only:

```text
Meta/WhatsApp -> moda-interact-messaging -> Shared event -> BullMQ -> moda-interact-background

moda-interact-background -> Moda-owned WhatsApp transport -> Meta/WhatsApp
```

Do **not** implement Shopify abandonment/reconciliation, 48-hour reminder scheduling, order completion, recovery expiry, billing/credits or merchant Meta onboarding in an ARCH-012 task.

## Binding product rules

```text
merchant Meta/WABA setup:                 none
Moda sender ownership:                    central Moda infrastructure
active Moda sender count in v1:           exactly one
sender-pool/load-balancing implementation: prohibited in ARCH-012
inbound text:                              supported
inbound voice note:                        supported <= 120 seconds
exactly 120 seconds:                       accepted
>120 seconds:                              reject before transcription
outbound generated voice:                  out of scope
raw audio durable retention:               prohibited by default
speech translation to English:             prohibited
human-agent/live escalation:               out of scope
recovery/follow-up timing:                  out of scope
```

## Reply modes

Both are first-class and must be preserved:

```text
A. Explicit native WhatsApp reply
   message.context.id -> exact prior outbound providerMessageId -> Conversation

B. Ordinary contextless message
   contextMessageId = null -> Background durable resolution
```

Messaging never infers shop/conversation ownership. Customer phone is a communications endpoint, not a tenant key.

## Luna execution rule

Every individual ARCH-012 task is an exact implementation contract.

The repository agent MUST:

1. use launcher-prepared parent + implementation task worktrees;
2. record the prepared execution packet evidence in the Completion Report;
3. read the exact task before editing;
4. edit only the authorised repository/surface unless the task explicitly permits another file;
5. preserve accepted ARCH-005/007 behaviours outside the stated change;
6. run the task's focused tests plus repository-declared validation;
7. use documented baseline IDs only for unchanged pre-existing conditions;
8. return the task to `review` and STOP.

The repository agent MUST NOT:

```text
invent a second queue
move DB/Shopify/STT/CommerceAgent work into Messaging webhook lifecycle
copy the Shared inbound schema locally after publication
choose an npm version not authorized by SHARED-002
make customerPhone a tenant identity
choose the latest merchant on cross-tenant ambiguity
turn unsupported/audio input into empty text
translate voice to English before CommerceAgent
persist raw audio or signed provider media URLs
conflate WABA ID and phone-number ID
build a sender pool or merchant WABA model
implement recovery timing/business decisions
start a dependent task after returning current task to review
```

If a required named file/symbol/capability is absent, or implementation requires a product/architecture decision not written in the task, **STOP and return evidence to `moda_architect`**. Do not infer an alternative design.

## Task graph

```text
SHARED-001 (Ready)
    -> SHARED-002 (Pending; also waits for ARCH-011-SHARED-002)
        -> MESSAGING-001
        -> BACKGROUND-001

DATABASE-001 (Ready)
        -> BACKGROUND-001
            -> BACKGROUND-002

BACKGROUND-003 (Ready)
        -> BACKGROUND-002
        -> GATEWAY-001

MESSAGING-001 + BACKGROUND-001 + BACKGROUND-003 + GATEWAY-001
        -> SYSTEM-TEST-001

MESSAGING-001 + BACKGROUND-002 + BACKGROUND-003 + GATEWAY-001
        -> SYSTEM-TEST-002
```

## Initial Ready frontier

These may be prepared independently after the overlay is applied/materialised:

```text
ARCH-012-SHARED-001
ARCH-012-DATABASE-001
ARCH-012-BACKGROUND-003
```

Do not start Pending tasks manually. Their dependencies must be architect-accepted Complete and normal task gating must promote them.

## Exact task contracts

### `ARCH-012-SHARED-001`

Owner: `moda_shared`.

Creates strict Shared v1 inbound event with text/audio/unsupported union and preserves:

```text
providerAccountId
providerPhoneNumberId
providerMessageId
customerPhone
contextMessageId
occurredAt
content
```

No tenant/business fields. No publication in this task.

### `ARCH-012-SHARED-002`

Owner: `moda_shared`, developer execution mode.

Publication metadata only. Serializes after `ARCH-011-SHARED-002`; expected `0.13.0` only if local/npm premise is exactly as written in the task. Otherwise STOP for architect reconciliation.

### `ARCH-012-DATABASE-001`

Owner: `moda_database`.

Adds exact `ConversationMessage` content/media/transcription lifecycle. Does not store raw audio or media URL. Existing providerMessageId uniqueness remains dedupe authority.

### `ARCH-012-MESSAGING-001`

Owner: `moda_messaging`.

Maps realistic Meta webhook payload to the Shared event, including `message.context.id` and `message.audio.id`. No DB, Shopify, media GET, STT or CommerceAgent work before webhook ACK.

### `ARCH-012-BACKGROUND-001`

Owner: `moda_background`.

Consumes Shared package, removes authoritative local inbound event, implements/preserves exact-vs-contextless routing and prevents audio/unsupported content becoming empty text.

### `ARCH-012-BACKGROUND-002`

Owner: `moda_background`.

Implements route-first two-phase audio reservation/completion, Meta media retrieval, <=120s validation, provider-neutral STT + Groq adapter, multilingual transcript preservation, deterministic terminal fallbacks, no raw-audio retention.

### `ARCH-012-BACKGROUND-003`

Owner: `moda_background`.

Separates WABA ID from phone-number sender ID, retains one sender v1, and provides outbound text/link preview plus approved-template image/URL-button transport. No sender-pool DB.

### `ARCH-012-GATEWAY-001`

Owner: `moda_gateway`.

Adds WABA identity to existing test/production messaging worker configuration. No new service, route or network topology.

### `ARCH-012-SYSTEM-TEST-001`

Owner: `moda_system_test`.

Integrated deterministic text/reply/contextless/link/template-media/status/idempotency validation with existing WhatsApp emulator. No live Meta.

### `ARCH-012-SYSTEM-TEST-002`

Owner: `moda_system_test`.

Integrated deterministic voice media/download/duration/STT/retry/privacy validation using emulator/fake provider boundaries. No live Groq required for normal acceptance suite.

## Repository sequencing

Tasks in the same repository are deliberately serialized:

```text
Shared:      SHARED-001 -> SHARED-002
Background:  BACKGROUND-001 -> BACKGROUND-002
```

`BACKGROUND-003` is an independent initial outbound track and may execute before BACKGROUND-001.

Do not start the next same-repository task until predecessor dependencies are architect-accepted Complete.

## System-test gate

System-test tasks are terminal/manual invocation gates. No non-system-test task depends on them.

After all implementation/infrastructure dependencies for a system-test task are Complete, the developer may manually validate the integrated environment before launching the Ready system-test task.

## Overlay/materialisation note

This overlay places canonical task definitions in the workspace documentation tree. It does **not** claim that task branches/worktrees/commits have been created or pushed.

Normal `/moda-task <TASK_ID>` preparation remains authoritative for task execution/materialisation and worktree isolation.
