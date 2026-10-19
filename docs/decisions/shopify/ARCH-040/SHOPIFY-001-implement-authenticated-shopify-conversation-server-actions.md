---
id: ARCH-040-SHOPIFY-001
architecture_id: ARCH-040
title: Implement complete Shopify Recovery Detail human conversation feature
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 40
executor: developer
claimed_at: 2026-10-18T22:36:19Z
attempt: 2
depends_on:
  - ARCH-040-DATABASE-001
  - ARCH-040-BACKGROUND-002
  - ARCH-040-DATABASE-005
  - ARCH-040-BACKGROUND-006
enables:
  - ARCH-040-SYSTEM-TEST-002
created: 2026-10-14
updated: 2026-10-18
---

# ARCH-040-SHOPIFY-001 — Complete Shopify Recovery Detail human conversation feature

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. This is a single complete Shopify feature: the former SHOPIFY-001 server reads, SHOPIFY-002 basket/layout and SHOPIFY-003 control/composer have all been incorporated here. The task was materialised and promoted to Ready before developer execution preparation.

### Developer Ownership Amendment

On 2026-10-18, `/moda_developer_create ARCH-040-SHOPIFY-001` was invoked for developer execution. Logical ownership remains assigned to `moda_app`; `execution_mode` and `completion_mode` are now `developer`. Task scope, dependencies, and acceptance criteria are unchanged. The canonical launcher will synchronize both task worktrees, revalidate dependencies and recursive submodules, and durably claim Attempt 1 before implementation begins.

## Objective

Extend the **existing Shopify Recoveries -> Recovery Detail** screen as one merchant-usable feature. Display the persisted checkout basket beside the existing single WhatsApp conversation and recovery context; allow authenticated merchant Take Over / Resume AI and permitted HUMAN text/template replies, with durable send status and platform abuse restrictions. Do not create an independent customer-conversations page or a new WhatsApp delivery mechanism.

## Context

The inspected 2026-10-17 Shopify snapshot already has:

- `app/routes.ts` defining `app/recoveries/:recoveryId`, plus `/messages` and `/related` resource routes.
- `app/routes/app/recovery-detail/route.tsx` composing the current loader and `RecoveryDetail` component.
- `app/routes/app/recovery-detail/loader.server.ts` using `requireRecoveryHistory`, then the scoped `readRecoveryDetail`, `readRecoveryMessages`, and `readRelatedRecoveries` readers.
- `app/services/recoveries/recovery-detail.server.ts` with shop-scoped bounded message/related reads; `CheckoutRecovery.lineItems` exists but is **not yet part of the detail projection**.
- `app/routes/app/recovery-detail/RecoveryDetail.tsx` rendering sender attribution, link-safe text, audio transcription, provider status, message pagination, recovery milestones, and related recoveries.
- `app/routes/app/recovery-detail/state.ts`, `messages.ts`, `related.ts`, and `RecoveryDetail.css` supporting current navigation and layout.
- The database's unique recovery conversation, `ConversationMessage.senderType` including `HUMAN`, and one sequence-2 `RecoveryOutreachAttempt`. Consolidated DATABASE-001 and Background-001/002 add the ownership, command and final-send rules.

Avoid a second inbox, a second conversation, client-owned permissions, a new Shopify-to-Woo API bridge or duplicate Background services. This one task replaces the three-task read/UI/write handoff, not the existing internal separation of server logic and modular UI components.

## Scope

1. Enrich the existing authenticated recovery-detail loader/service with saved basket, control mode/revision, service-window advisory, follow-up status and public human-messaging restriction state.
2. Build the responsive recovery detail layout with the existing transcript as the main panel, basket and recovery context adjacent/stacked, all using the actual saved recovery data.
3. Add Shopify server-side, shop-scoped Take Over / Resume AI (compare-and-set, audit) and durable HUMAN send/command-status operations for recovery-linked conversations only.
4. Add actual Take Over/Resume UI, open-window free-text reply, closed-window approved recovery-follow-up template when eligible, command status display and suspended-state behaviour.
5. Preserve current recovery list, route, embedded admin session, pagination, related recoveries and existing translations; keep the implementation modular even though delivery is one feature.

## Out of Scope

- No `/app/conversations` navigation item, separate inbox, generic standalone human messaging, duplicate transcript or separate conversation identity.
- No new store staff accounts, assignment workflow, granular per-conversation permissions or Shopify-to-`moda-interact-api` authentication bridge.
- No live Shopify cart lookup on page open, invented line-item prices, images, discounts, taxes, shipping, unread counts or new checkout snapshot schema.
- No synchronous WhatsApp provider send or recovery billing/credit settlement from the browser or Shopify HTTP action. Background owns final dispatch, status and charging.
- No new human-only follow-up attempt/scheduler or quota. Reuse sequence 2, approved template restrictions and shared recovery-credit identity.
- No changes to `docs/decisions/**/_index.md`, cross-repository code or unrelated recovery settings.

## Requirements

### Semantic moderation: one existing Recovery Detail UI

Read DATABASE-005 moderation decisions through Shopify's existing authenticated server loader/actions (no Woo API). On the single existing transcript show a restrained warning for flagged CUSTOMER text, while preserving the record and sender attribution; never present it as an unsafe AI prompt. For HUMAN composer: after accepted command show `Checking message...` until status changes; show `Message not sent — please revise it` for BLOCK, a review notice for REVIEW_REQUIRED, and retryable dependency notice for temporary moderation failure. Distinguish these from queued/SENT/DELIVERED/READ/FAILED provider states and from merchant suspension. Keep Take Over/Resume AI controls available subject to existing rules; never allow UI-only override of moderation or display raw scores. Use established localisation; no new Conversations nav page or direct OpenAI browser call. Preserve the existing canonical desktop/mobile wireframes and explicitly implement the additional message-state examples; no extra route or UI required.

### 1. Exact existing code surfaces to extend

| Existing source | Required changes |
|---|---|
| `app/services/recoveries/recovery-detail.server.ts` | Extend `readRecoveryDetail`/scoped DTO with bounded safe `CheckoutRecovery.lineItems`, currency/value, `Conversation.id`/mode/revision, last authenticated customer inbound/window advisory, sequence-2 follow-up and public shop restriction. Keep `readRecoveryMessages` and `readRelatedRecoveries` pagination unchanged. |
| `app/routes/app/recovery-detail/loader.server.ts` | Use the existing `requireRecoveryHistory` shop/session boundary and current detail identity. Forward the new projection; preserve 404, section errors, embed context, list filters and message cursors. `RECOVERY_HISTORY` is read access, **not sufficient by itself to authorise sending**. |
| `app/routes/app/recovery-detail/state.ts` | Extend only existing `DetailData`/DTO-derived types, with no parallel generic conversation DTO or duplicate client store. |
| `app/routes/app/recovery-detail/route.tsx` | Continue rendering current route; integrate action/fetcher state via small separated modules rather than turning this file into a large controller. |
| `app/routes/app/recovery-detail/RecoveryDetail.tsx`, `.css` | Compose modular basket, conversation control, transcript and composer components; maintain existing `MessageText`, sender labels, receipts, transcription and related-recovery behaviour. |
| `app/routes.ts` | If needed register **only recovery-scoped Shopify resource actions** for takeover/resume, human send and command status under the existing `/app/recoveries/:recoveryId` flow. Preserve current detail, `/messages` and `/related` endpoints. |
| `app/routes/app/recovery-detail/messages.ts`, `related.ts` | Preserve existing reader and cursor semantics; change only if a concrete integration issue requires it. |
| `app/routes/app/recoveries/recovery-list-state` and merchant i18n utilities | Reuse existing return navigation, filters, embed state and merchant locale/time zone; add translations using current i18n patterns. |

Recommended small modules, following actual repository conventions, include `checkout-basket.tsx`, `conversation-control.tsx`, `human-message-composer.tsx`, `follow-up-template-selector.tsx`, `conversation-commands.server.ts` and a command-status controller/hook. These are **illustrative module boundaries**, not required new directories or additional task IDs. Do not grow an already substantial `RecoveryDetail.tsx` into a monolith.

### 2. Authenticated data projections — specific contract

1. Use the existing Shopify admin session and the resolved trusted internal `shopId` on **every** reader/action. Authorise recovery via `CheckoutRecovery.shopId` and recover its `Conversation.id` server-side; `Conversation.shopId` can be nullable and a browser-supplied shopId is never authoritative. Foreign/missing recovery or conversation cannot be read, mutated or used to create a command.
2. Extend the existing detail shape (names may follow repository conventions) with `basket: { items, currency, recoveryTotal, unavailableReason? }` and `conversation: { id, controlMode, controlRevision, lastInboundAt?, windowExpiresAt?, followUp: { used, initiatedBy? }, humanMessagingStatus } | null`. Do not leak internal Admin suspension notes, credentials, payment tokens, or private customer details.
3. Map `CheckoutRecovery.lineItems` as a **snapshot**, after inspecting the actual persisted checkout-event writer and JSON keys. Project only supported title/name, variant, quantity, safe image URL and persisted unit/line price; use decimal-safe currency formatting and label the saved recovery total. Do not infer line prices from a recovery total, convert money with unsafe floats or silently fetch a current Shopify price.
4. If basket JSON is absent/malformed/partial, show an honest partial/unavailable display without hiding transcript, control state, or recovery milestones. A missing conversation keeps recovery/basket readable; it must not create a new Conversation as a read side effect.
5. Preserve existing paginated `CUSTOMER`, `AGENT`, `AUTOMATION`, `HUMAN` messages, audio transcript states, safe HTTP(S) linkification, receipt statuses and related recoveries. Never infer unread counts from timestamps. Do not auto-scroll away from history the merchant is reading.
6. Service-window time is based on the most recent **verified customer inbound** WhatsApp message; its UI value is advisory. Final action/Background validation remains authoritative and must account for expiry while the page is open.

### 3. Server-side control and HUMAN send operations

1. **Take Over** is allowed from an AI-controlled recovery conversation regardless of the 24-hour WhatsApp window, unless shop HUMAN messaging is suspended or another existing shop/feature/terminal-state policy blocks it. Authenticate session; validate recovery ownership and the current restriction; CAS `controlMode/controlRevision` and append the DB-owned immutable transition event in the same transaction. Accept the current `expectedControlRevision`; on stale revision return a typed conflict and current authoritative state.
2. **Resume AI** is allowed from HUMAN mode even if human messaging is suspended; commit an incremented revision and audit event. Do not infer an automatic release from customer inbound, a timer or a message author. If an AI provider send was already irreversibly submitted before takeover, inform the UI it cannot be recalled. Any subsequently admitted AI sends must pass Background ownership fencing.
3. HUMAN reply submission must check the existing shop's actual messaging entitlement/feature policy, session/tenant ownership, `HUMAN` control mode, supplied control revision, shop HUMAN restriction, recipient availability/suppression, content type and eligibility. A `RECOVERY_HISTORY` read grant must not become an implicit send grant. Recheck relevant state transactionally, use the accepted DATABASE-001 command constraints, and record the intent with stable shop-scoped idempotency; conflicting payload reuse of one key is rejected.
4. When the verified customer service window is **open**, permit bounded validated free-text HUMAN replies. When **closed**, reject free text. Permit only an eligible, server-allowlisted, provider-approved recovery follow-up template and claim the same existing `RecoveryOutreachAttempt` **sequence 2**, never a parallel human sequence, independent billing ledger, or arbitrary template ID. Existing scheduled no-response follow-up behaviour remains unchanged except that it must honour HUMAN ownership; the allowed human-initiated follow-up competes for the same sequence-2 claim/credit.
5. A successful HTTP command response means `ACCEPTED`/queued intent, **not** Meta `SENT`. Neither action nor loader makes a provider network call, settles billing, or publishes a second Redis job. Background-002 consumes the durable PostgreSQL command; reuse Background's final send fence, WhatsApp transport, provider status and compensation mechanisms.
6. Provide a **recovery-scoped command-status read** that resolves the command under the same authenticated shop and conversation, returning only safe canonical statuses, `commandId` and typed failure/retry information. Do not allow arbitrary command IDs from another shop or standalone conversation. Preserve idempotent replies to a repeated identical submission even across page reloads.
7. Reject and display suspended merchant, abuse-screened, rate-limited, invalid template, closed window, already-used follow-up, stale revision, unavailable recipient, terminal recovery, duplicate/conflicting idempotency and provider unknown/failure states. Restriction is checked at command acceptance and again by Background before final provider dispatch; server permissions must remain effective if a browser forges a request.

### 4. Responsive recovery detail and state management

- Conversation occupies the **larger desktop column**. The right column shows the **checkout basket** above recovery status, milestones, follow-up availability and related recoveries. No new route/menu and no second read-only transcript.
- Narrow embedded Shopify Admin width: basket and recovery context stack/collapse **above** the conversation; composer remains reachable without horizontal scrolling. No invented sticky-footer rules that interfere with Shopify embedding.
- Preserve the Recoveries back-link list filters, embed context, selected recovery and message cursor/pagination. Manual refresh remains available; refresh transcript/status without unexpectedly losing the merchant's draft, resetting selection or scrolling to an unrelated message.
- Loading, missing conversation, malformed basket, empty history, failed section, terminal recovery, suspended shop and transient provider status all get distinct localised/accessibility-aware feedback; never show a fake successful send.
- UI keeps a stable per-intent idempotency key, disables duplicate Take Over/Resume/Send presses, and discards stale asynchronous results. On a `409` revision conflict, reload actual mode/eligibility before repeating an operation; do not optimistically change persisted ownership.
- Messages display ACCEPTED/QUEUED separately from SENT/DELIVERED/READ/FAILED/UNKNOWN, according to actual command/provider evidence. Poll the selected in-flight command at a bounded cadence and stop when no longer needed.
- In `AI` mode, display **Take Over** and a disabled/absent human composer. In `HUMAN` mode, display **Resume AI** and an open-window composer or an eligible closed-window template. Customer reply opens a new window but **does not** automatically change HUMAN back to AI.
- When HUMAN messaging is platform-suspended, basket and transcript stay readable; disable Take Over, free text and templates; keep **Resume AI** available. Do not surface private administrator reason/notes. Never auto-resume AI.
- Reuse Shopify merchant UI localisation and safe input/focus patterns (e.g. accessible buttons, keyboard operations and status announcements); do not invent an independent translation system.

### 5. Canonical desktop ASCII wireframe — complete feature

```text
+-------------------------------------------------------------------------------+
| < Back to Recoveries                                                         |
| Customer: Sarah Jones          Recovery: ENGAGED        Saved value: GBP 124.99 |
+----------------------------------------------+--------------------------------+
| CUSTOMER CONVERSATION                        | CHECKOUT BASKET                |
| AI in control                [Take Over]      | Basket snapshot (at recovery) |
| Window: open until <customer inbound +24h>    |                                |
|----------------------------------------------| Product A  Blue / Large        |
| CommerceAgent                        10:20    | Qty 2             GBP 59.98   |
|  [Can I help you with your checkout?]         | Product B  Black               |
|                                              | Qty 1             GBP 65.01   |
| Customer                             10:25    |--------------------------------|
|  [Can you help with delivery?]                | Saved recovery total GBP124.99|
|                                              +--------------------------------+
| Merchant                             10:28    | RECOVERY CONTEXT               |
|                        [Yes, let me check.]   | Status / milestones            |
|                                              | Initial / follow-up state      |
| [Previous] [Latest] [Next] [Refresh]          | Related recoveries             |
|----------------------------------------------|                                |
| Human reply composer / template when eligible        |                                |
+----------------------------------------------+--------------------------------+
* Take Over and Resume AI are live actions in consolidated SHOPIFY-001.
```

The original SHOPIFY-002 desktop layout is retained here; the Take Over button and conditional composer are now **real actions in this same task**, not inert placeholders. Example names, products and amounts are fictitious wireframe content and must never be hardcoded into implementation.

### 6. Canonical narrow-screen ASCII wireframe

```text
+--------------------------------------+
| < Recoveries       Sarah Jones       |
| Recovery: ENGAGED     GBP 124.99     |
|--------------------------------------|
| [Checkout basket v]                  |
|  Product A  Qty 2 ...                 |
|  Saved recovery total ...            |
|--------------------------------------|
| [Recovery context v]                 |
|--------------------------------------|
| Conversation       [AI / HUMAN]      |
| [Take Over]                         |
|                                      |
| CommerceAgent: Can I help?           |
| Customer: Can you help?              |
| Merchant: Yes, of course.            |
|                                      |
| [Previous] [Latest] [Refresh]        |
| Composer appears when HUMAN mode permits sending          |
+--------------------------------------+
```

All modes use this same Recovery Detail route; the basket and recovery context can collapse, but the transcript and composer remain usable.

### 7. AI, HUMAN and closed-window ASCII interaction states

```text
AI in control (any service-window state)       HUMAN + open window
+----------------------------------------+    +--------------------------------------+
| Conversation  [AI]         [Take Over] |    | Conversation [HUMAN] [Resume AI]   |
| Agent/customer transcript ...          |    | Agent/customer/human messages ...   |
|----------------------------------------|    |--------------------------------------|
| CommerceAgent is managing replies.     |    | [Type your reply ..............]    |
| Take over to reply.                    |    |                             [Send]  |
+----------------------------------------+    +--------------------------------------+

HUMAN + closed window + follow-up available   HUMAN + closed + already used
+----------------------------------------+    +--------------------------------------+
| Conversation [HUMAN]       [Resume AI]  |    | Conversation [HUMAN] [Resume AI]    |
| 24-hour customer window closed.        |    | Window closed. Follow-up used.     |
| [Approved recovery template       v]  |    | Await customer message to resume    |
| One remaining follow-up; 1 credit      |    | permitted free-form replying.       |
|                  [Send Follow-up]      |    | (no composer / no send button)       |
+----------------------------------------+    +--------------------------------------+
```

Only show the closed-window template if the current recovery/sequence-2 attempt is genuinely eligible. A customer reply opens another 24-hour service window but does not reset the one follow-up allowance or switch HUMAN back to AI. Initial recovery and eligible follow-up credit semantics remain Background-owned.

### 8. Suspended human messaging ASCII interaction state

```text
+---------------------------------------------------------------+
| Customer / Recovery       [HUMAN]           [Resume AI]       |
| Conversation history / Checkout basket remain visible        |
+---------------------------------------------------------------+
| HUMAN MESSAGING UNAVAILABLE                                   |
| This store's human replies are currently disabled by Moda.   |
| [Reply composer disabled]                                     |
+---------------------------------------------------------------+
```

Existing basket, messages and recovery details remain available; HUMAN composer and Take Over are **server-blocked**. Resume AI stays available for an already HUMAN-controlled conversation. Show a safe, localised restriction message.

### Platform-specific Shopify boundary — shared Background after commit

The Shopify server owns only existing Shopify admin-session validation, recovery-scoped Prisma reads, the accepted HUMAN/AI control CAS, the same durable HUMAN command/follow-up claim transaction as Woo API-004, and the Recovery Detail UI. It must **not** publish a BullMQ merchant-send job, call Meta directly, run a Shopify-only dispatcher or configure a Shopify-specific delivery queue. Successful command acceptance means a PostgreSQL record exists; BG002's single shared DB poller consumes it irrespective of origin. Inbound WhatsApp and automatic recovery follow-up BullMQ paths are unchanged. Confirm actual existing plan/feature human-send entitlement instead of borrowing `RECOVERY_HISTORY`, and keep terminal recovery sends ineligible under shared recovery policy. Preserve all ASCII layouts and developer-owned post-delivery validation, which is not a feature acceptance criterion.


## Work Items

- [ ] Extend existing Shopify shop-scoped recovery detail read/loader and typed projection with persisted basket, mode/revision, 24-hour advisory, follow-up and public HUMAN restriction data.
- [ ] Extract/reuse modular Recovery Detail UI pieces and render the desktop/narrow basket/transcript/recovery context, preserving existing navigation, pagination, audio, safe links, sender labels and delivery receipts.
- [ ] Implement authenticated recovery-scoped Take Over / Resume AI server actions with CAS, immutable transition audit, entitlement and suspension enforcement.
- [ ] Implement shop/recovery-scoped HUMAN text and approved-template send command acceptance plus command status using stable idempotency and the canonical DATABASE-001 schema; no direct WhatsApp send.
- [ ] Implement the complete conversation controls and composer states shown in the ASCII diagrams, including expired window, used follow-up, suspended state, queued/provider status, stale revision and safe double-click handling.
- [ ] Integrate current merchant locale, recovery navigation and accessible responsive styling; keep server command code, UI presentation and controller hooks separated.
- [ ] Record changed source files, the actual implemented endpoints and components, remaining limitations and developer-validation handoff evidence in Completion Report. **Do not make developer-run validation a Work Item.**

## Interfaces / Contracts

- **Reads:** Shopify authenticated `/app/recoveries/:recoveryId` loader -> `readRecoveryDetail` + existing paginated `/messages`, `/related` -> Prisma `CheckoutRecovery`/`Conversation`/`ConversationMessage`/`RecoveryOutreachAttempt`/shop HUMAN restriction. No hosted Woo API.
- **Mutations:** Shopify server-only recovery-scoped control/send/status actions -> CAS mode/revision, audit and durable `MerchantConversationSendCommand`; shop/recovery ownership always rechecked; no browser database credential or provider key.
- **Delivery:** Database accepted HUMAN command -> accepted `ARCH-040-BACKGROUND-001/002` services and existing WhatsApp sender -> canonical `ConversationMessage`, outreach sequence-2/credit and provider status. Shopify never creates a second thread, independently bills a follow-up, or sends to Meta.
- **Renderer:** Existing `RecoveryDetail.tsx`/messages/related components -> new small presentation/control/composer modules using the same recovery detail DTO and sender semantics.

## Dependencies

- ARCH-040-DATABASE-001
- ARCH-040-BACKGROUND-002

No WooCommerce, hosted Woo API, Gateway, new Shared-package or other Shopify task dependency.


- ARCH-040-DATABASE-005

- ARCH-040-BACKGROUND-006
## Enables

- ARCH-040-SYSTEM-TEST-002

## Acceptance Criteria — feature implementation only

- [ ] Shopify Recovery Detail presents moderation pending/blocked/review states while preserving its existing basket, transcript, AI/HUMAN controls and server-only moderation decisions.

- [ ] The **existing** Shopify Recoveries -> Recovery Detail route renders the actual saved basket, recovery context and unchanged single WhatsApp transcript at wide/narrow sizes matching these ASCII layouts; no `/app/conversations` route or second Conversation row is created.
- [ ] The authenticated server readers/actions are implemented with strict `CheckoutRecovery.shopId` scoping, actual shop messaging entitlements, monotonic mode CAS/audit and safe missing/foreign recovery handling; Shopify never accesses Woo-hosted API for ARCH-040.
- [ ] Merchant Take Over/Resume AI, open-window free text, eligible closed-window recovery template and single sequence-2 follow-up are implemented using canonical database intents and Background admission, without a duplicate provider sender or charging path.
- [ ] The UI expresses AI/HUMAN, queued/provider status, expiry, already-used follow-up, revision conflicts, suspension and abuse rejection honestly; it does not allow double-submit or treat command ACCEPTED as SENT.
- [ ] Existing recovery list navigation, filters, related/milestone/message pagination, safe links, audio/transcription, localisation and modular component boundaries are preserved; suspended shops can still read history and Resume AI.

**Developer validation is separate and is NOT an acceptance criterion for this Shopify implementation task.** The above acceptance criteria describe the feature/code delivered for architect review. Browser/manual tests, screenshots, full provider integration and other developer-run validation are not required before the task is handed to the architect. Findings from subsequent developer verification may require a correction attempt.

## Validation

**Developer-owned, not a task acceptance gate.** The developer will perform any Shopify authenticated route tests, component/browser checks, responsive/i18n reviews, production build, typecheck, lint, disposable PostgreSQL/provider tests, and manual embedded-app verification after delivery. The implementing agent records suitable suggested checks and any existing evidence, but must **not** wait for developer validation to submit an otherwise complete implementation. Later `ARCH-040-SYSTEM-TEST-002` is an independent architecture-level certification task, not a prerequisite for this implementation task's acceptance.

Suggested developer checks (informational): denied other-shop recovery/command, null Conversation, malformed basket, mixed sender pagination, AI Take Over / HUMAN Resume, stale revision, expiry while drafting, approved/used template, duplicate idempotency key, queued vs provider receipt, suspended shop with readable history, responsive layouts against both ASCII diagrams, refresh/back navigation, localised status messages, and clean diff/build artifacts.

## Implementation Notes

Deliver this as **one complete, end-to-end Shopify feature**, not separate server-read, read-only UI and send-control tasks. Reuse the existing read-side/UI before layering the control and composer in the same implementation. Preserve session authorization and no-new-inbox rule. Avoid 400+ line catch-all components; keep source files/components independently reviewable. If a genuine DATABASE-001 or BACKGROUND-002 contract gap exists, return it to `moda_architect`, do not duplicate the missing mechanism locally.

## Stop Condition

When all implementation Work Items and **feature-only** Acceptance Criteria are met, complete the report, set status `review`, return to `moda_architect` and STOP. **Do not wait for the developer to run validation before review/architect code acceptance.** Do not automatically begin SYSTEM-TEST-002 or work belonging to another repository.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-18T22:36:19Z. Attempt 1 review history is preserved below.

### Files Changed
None.

### Work Completed
None.

### Validation Results
No Shopify feature validation was run because no implementation changes are present. The canonical implementation worktree is clean at `7303c04` (`origin/main`); no `origin/task/ARCH-040-SHOPIFY-001` implementation branch or task-specific commit exists. The lint fix previously recorded in conversation belongs to ARCH-035-WOOCOMMERCE-004 and is not evidence for this task.

### Deviations
None.

### Assumptions
Schema and common Background runtime are accepted before this task starts; implementation follows actual Shopify route and merchant-auth conventions.

### Unresolved Issues
None recorded.

### Architectural Concerns
Return new cross-service, persistence, admission or policy gaps to `moda_architect`.

## Architect Review

### Review Status
Pending

### Review Notes
Not reviewed.

### Reviewed Files
None.

### Validation Reviewed
Developer-owned validation not required for task-level code acceptance.

### Architecture Conformance
Pending.

### Follow-up
None.

## Dependency Frontier Promotion — 2026-10-18

- Eligibility: promoted from `pending` to `ready` at Attempt 0; no implementation claim or worktree preparation is implied.
- Satisfied dependencies: `ARCH-040-DATABASE-001`, `ARCH-040-BACKGROUND-002`, `ARCH-040-DATABASE-005`, and `ARCH-040-BACKGROUND-006` are all `complete` according to canonical launcher routes.
- Execution remains governed by the normal `/moda-task ARCH-040-SHOPIFY-001` launcher and assigned owner `moda_app`; this promotion does not start the task.

## Developer Self-Review - Changes Requested (Attempt 1, 2026-10-18)

The review does not pass. No Shopify implementation was delivered in Attempt 1: the canonical implementation worktree is clean at `7303c04` (`origin/main`), and no task-specific implementation branch or commit is published. All implementation Work Items and feature Acceptance Criteria remain incomplete. The reported lint fix was made for a different WooCommerce task.

Required corrections for the next developer attempt:

- Implement the authenticated, strictly shop-scoped recovery-detail projection for saved basket snapshots, conversation ownership/revision, verified-inbound service-window advisory, sequence-2 follow-up state, public HUMAN restriction and moderation decisions. Preserve safe partial/unavailable behavior and existing message/related pagination.
- Deliver the responsive basket/transcript/recovery-context layout and localized AI/HUMAN controls on the existing Recovery Detail route, preserving sender attribution, audio/transcription, safe links, receipts, filters, embed context and history navigation.
- Implement recovery-scoped Take Over/Resume AI actions with transactional revision CAS and audit, plus authorized HUMAN text/approved-template command acceptance and recovery-scoped status reads using canonical durable command/idempotency contracts. Do not add a provider sender, queue or charging path.
- Implement and test the required window, sequence-2 eligibility, suspension, moderation, stale-revision, duplicate-submit, provider-status and terminal/unavailable states; ensure server authorization remains authoritative and the UI never equates ACCEPTED with SENT.
- Record actual implementation files/endpoints, focused validation results, remaining limitations and developer-validation handoff evidence in the Completion Report. Leave every feature checkbox unchecked until its behavior is implemented and evidenced.

Attempt 1 remains recorded. The task is returned to `ready` with `executor: null` and `claimed_at: null`; the next developer-create claim may increment the attempt exactly once.
