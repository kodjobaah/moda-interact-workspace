# ARCH-012 Implementation Handoff — consolidated deterministic communications contracts

Date: 2026-09-16
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

```text
A. Explicit native WhatsApp reply
   message.context.id -> exact prior outbound providerMessageId -> Conversation

B. Ordinary contextless message
   contextMessageId = null -> Background durable resolution
```

Messaging never infers shop/conversation ownership. Customer phone is a communications endpoint, not a tenant key.

## Consolidation decision — 2026-09-16

Two artificial task boundaries are removed:

```text
SHARED-001 + SHARED-002 -> SHARED-001
BACKGROUND-001 + BACKGROUND-002 -> BACKGROUND-001
```

Rationale:

- the Shared contract is not usable downstream until the package is published, so one `moda_shared` task owns implementation, validation and publication;
- voice-note processing is one content branch of Background's inbound routing/persistence pipeline, so routing and transcription are implemented/reviewed together.

`ARCH-012-SHARED-002` and `ARCH-012-BACKGROUND-002` are now `superseded` and must never be launched.

## Database freeze

`ARCH-012-DATABASE-001` has already started in the developer workspace. This consolidation does **not** rewrite that task, its metadata, its attempt number, its status, its migration contract or any database implementation file.

Merged BACKGROUND-001 depends on the live/accepted DATABASE-001 result. If database review exposes an incompatibility, return it to `moda_architect`; do not mutate DATABASE-001 through this handoff.

## 2026-09-16 compatibility baseline

Preserve later accepted runtime work:

```text
ARCH-010-BACKGROUND-013
  -> shop execution eligibility and outbound suppression

ARCH-014-BACKGROUND-004
  -> runtime-configured WhatsApp abuse-admission limits

ARCH-014-BACKGROUND-005
  -> runtime-configured fleet-wide BullMQ concurrency, including whatsappQueueGlobalConcurrency
```

ARCH-012 must extend these implementations rather than restore older static behaviour. Do not replace `createWhatsappWorker()`, remove dynamic concurrency binding, bypass `shopExecutionEligibilityService`, or reintroduce static abuse/concurrency constants.

## Luna execution rule

Every active ARCH-012 task is an exact implementation contract. The repository agent MUST:

1. use launcher-prepared parent + implementation task worktrees;
2. record prepared execution packet evidence;
3. read the exact task before editing;
4. edit only authorised surfaces;
5. preserve accepted behaviours outside the stated change;
6. run focused tests plus repository-declared validation;
7. use baseline IDs only for unchanged pre-existing failures;
8. return the task to `review` and STOP.

The repository agent MUST NOT:

```text
invent a second queue
move DB/Shopify/STT/CommerceAgent work into Messaging webhook lifecycle
copy the Shared inbound schema locally after publication
make customerPhone a tenant identity
choose the latest merchant on cross-tenant ambiguity
turn unsupported/audio input into empty text
translate voice to English before CommerceAgent
persist raw audio or signed provider media URLs
conflate WABA ID and phone-number ID
build a sender pool or merchant WABA model
implement recovery timing/business decisions
execute SHARED-002 or BACKGROUND-002
start a dependent task after returning current task to review
```

If a named file/symbol/capability is absent or an architectural decision is missing, STOP and return evidence to `moda_architect`.

## Task graph

```text
ARCH-012-SHARED-001
        (accepted Attempt 1; published `0.12.0`)
            -> ARCH-012-MESSAGING-001
            -> ARCH-012-BACKGROUND-001

# Shared release-line reconciliation:
ARCH-012-SHARED-001 -> ARCH-011-SHARED-001 -> ARCH-011-SHARED-002 (`0.13.0`)

ARCH-012-DATABASE-001
        -> ARCH-012-BACKGROUND-001

ARCH-012-BACKGROUND-003
        -> ARCH-012-BACKGROUND-001
        -> ARCH-012-GATEWAY-001

MESSAGING-001 + BACKGROUND-001 + BACKGROUND-003 + GATEWAY-001
        -> SYSTEM-TEST-001
        -> SYSTEM-TEST-002
```

## Current execution frontier after consolidation

```text
ARCH-012-DATABASE-001      Complete — architect accepted Attempt 2; implementation `655ff35`
ARCH-012-SHARED-001        Complete — architect accepted Attempt 1; published `0.12.0`
ARCH-012-MESSAGING-001     Complete — architect accepted Attempt 1; implementation `2267f26` + `424e09d`
ARCH-012-BACKGROUND-003    Complete — architect accepted Attempt 1; implementation `bb01a66`
ARCH-012-BACKGROUND-001    Ready — SHARED-001, DATABASE-001 and BACKGROUND-003 are accepted Complete
ARCH-012-GATEWAY-001       Ready — BACKGROUND-003 is accepted Complete
ARCH-012-SYSTEM-TEST-001   Pending — BACKGROUND-001 and GATEWAY-001 are not Complete
ARCH-012-SYSTEM-TEST-002   Pending — BACKGROUND-001 and GATEWAY-001 are not Complete
```

Never downgrade a task that has already advanced in the live workspace merely because this handoff shows the snapshot-era state.

## Exact active task contracts

### `ARCH-012-SHARED-001`

Owner: `moda_shared`. Accepted Attempt 1. The strict Shared v1 inbound text/audio/unsupported contract is published as `@modainteract/moda-interact-shared@0.12.0`. The post-review release-line reconciliation makes this accepted release the baseline that ARCH-011 Shared work must preserve.

### `ARCH-012-DATABASE-001`

Owner: `moda_database`. **Live task; untouched by this consolidation patch.** Adds durable media/transcription lifecycle needed by Background.

### `ARCH-012-MESSAGING-001`

Owner: `moda_messaging`. Accepted Attempt 1 (`2267f26`, `424e09d`). Maps realistic Meta webhook payloads into the published Shared event, including `message.context.id` and audio media identity, validates before queue publication and keeps DB/media/STT/business work out of the ACK path.

### `ARCH-012-BACKGROUND-001`

Owner: `moda_background`. Complete inbound pipeline: consume Shared event, both reply modes, text/unsupported persistence, audio reservation, Meta media retrieval, <=120-second validation, provider-neutral STT + Groq adapter, multilingual transcript preservation and exactly-once turn completion.

### `ARCH-012-BACKGROUND-003`

Owner: `moda_background`. Separate WABA and sender phone identity, one Moda sender v1, outbound text/link preview plus approved template image/URL-button transport while preserving ARCH-010 outbound execution gates.

### `ARCH-012-GATEWAY-001`

Owner: `moda_gateway`. Adds WABA identity to existing worker configuration. No new service/topology.

### `ARCH-012-SYSTEM-TEST-001`

Owner: `moda_system_test`. Integrated deterministic text/reply/contextless/link/template-media/status/idempotency validation.

### `ARCH-012-SYSTEM-TEST-002`

Owner: `moda_system_test`. Integrated deterministic voice media/download/duration/STT/retry/privacy validation.

## Superseded task records

```text
ARCH-012-SHARED-002      superseded by ARCH-012-SHARED-001
ARCH-012-BACKGROUND-002  superseded by ARCH-012-BACKGROUND-001
```

Keep the files for history; never prepare them.

## Overlay/materialisation note

This patch changes canonical task/documentation definitions only. It does not claim branches, worktrees, commits or pushes. Normal `/moda-task <TASK_ID>` preparation remains authoritative.
