---
id: ARCH-040-WOOCOMMERCE-001
architecture_id: ARCH-040
title: Implement complete WooCommerce Recovery Detail human conversation feature
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-API-002
  - ARCH-040-API-003
  - ARCH-040-API-004
  - ARCH-040-BACKGROUND-002
  - ARCH-035-API-013
  - ARCH-035-WOOCOMMERCE-013
enables:
  - ARCH-040-SYSTEM-TEST-003
created: 2026-10-14
updated: 2026-10-17
---

# ARCH-040-WOOCOMMERCE-001 — Complete WooCommerce Recovery Detail human conversation feature

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable task definition: no task branch/worktree/commit/push is claimed.** This task consolidates former `ARCH-040-WOOCOMMERCE-001`, `-002` and `-003` into **one feature implementation**.

## Objective

Deliver one coherent WooCommerce merchant feature on the **existing Recoveries > Recovery Detail screen**: show the saved checkout basket alongside the original AI/customer/human WhatsApp transcript; allow Take Over / Resume AI; accept eligible human text and the single recovery follow-up template; and show authoritative send/restriction states. Implement the PHP REST facade, React/controller integration, and UI together in this one task.

**Developer validation is explicitly separate and is NOT a task Acceptance Criterion, a prerequisite to architect implementation review, or a condition for setting this task to `review`/`complete`.** The developer performs validation after implementation delivery at their chosen checkpoint. Keep later `ARCH-040-SYSTEM-TEST-003` as independent architecture certification, not an implementation acceptance gate.

## Context

The October 17 snapshot already contains `includes/Rest/RecoveryDetailController.php`, `includes/Api/ModaApiClient.php`, `src/recoveries/detail/` with read-only transcript, checkout context, recovery milestones, controller/hook, and ARCH-035 Recovery Detail support. WooCommerce PHP alone communicates with the Woo-only hosted API and holds installation credentials. `API-002` enriches the existing read DTO, `API-003` owns control commands, `API-004` owns durable human message admission/status, and `BACKGROUND-002` wires the shared worker runtime. No Shopify code or hosted Shopify authentication is needed.

## Scope

1. **WordPress REST / hosted API integration:** Extend the existing recovery-detail PHP controller and API client to read the enriched basket/control/restriction DTO, preserve paginated messages/related recoveries, and add authenticated control, send and command-status proxies using the agreed hosted API operations.
2. **Recovery Detail presentation:** Extend the existing modular Woo detail components to show saved checkout products, quantities/variants and real optional prices/images, together with existing transcript, recovery milestones, related recoveries and ownership status.
3. **Human interaction:** Add revision-aware Take Over / Resume AI, a HUMAN-only free-text composer while the customer's 24-hour window is open, and an approved recovery follow-up template selector when the window is closed and the shared sequence-2 follow-up is eligible.
4. **Outcomes and restrictions:** Render accepted/queued versus provider-confirmed sent/delivered/read/failed statuses, invalid/stale commands, suspended human messaging, moderation/rate rejection, disconnect, provider errors and safe retry; do not present speculative success.
5. **Existing platform UX:** Preserve WooCommerce > Moda Interact entry then Moda Interact's active Recoveries navigation; use WordPress-native i18n for all 20 supported merchant admin locales, responsive layout, modular components and accessible controls.

## Out of Scope

- No separate Conversations inbox/menu, new customer thread, non-recovery human-chat surface, custom merchant/staff accounts, role assignment, staff-specific conversation permissions or live chat service.
- No direct WordPress/PHP/JS database/Redis/Meta access, browser-held provider/API credentials, Shopify API calls or a second outbound sender/scheduler/credit ledger.
- Do not change hosted API-002/003/004, Background, Database or ARCH-035 implementation inside this Woo task. Report external gaps to `moda_architect`.
- No `docs/decisions/**/_index.md` changes until the architectural session is confirmed complete.
- Developer validation and the terminal system-test run are **not part of the implementation acceptance criteria** for this task.

## Required interface — desktop ASCII

```text
WooCommerce > Moda Interact > Recoveries > Recovery Detail
+--------------------------------------------------------------------------+
| < Back to Recoveries      Sarah Jones            Recovery: ENGAGED       |
+-------------------------------------------+------------------------------+
| CUSTOMER CONVERSATION                     | CHECKOUT BASKET              |
| [HUMAN]                     [Resume AI]   | Saved checkout snapshot      |
| 24-hour service window: OPEN              | Product A / Blue / Large     |
|-------------------------------------------| Qty 2  Price if stored       |
| Agent: Can I help with this checkout?     | Product B / Qty 1            |
| Customer: Please check delivery.          |                             |
| Merchant: Yes, let me check.              | Saved recovery total        |
|                                           +------------------------------+
| [Previous] [Latest] [Refresh]             | RECOVERY CONTEXT             |
|                                           | Milestones / related         |
+-------------------------------------------+------------------------------+
| [ Type your message................................. ]          [Send]   |
+--------------------------------------------------------------------------+
```

## Required interface — narrow screen ASCII

```text
+------------------------------------------+
| < Recoveries / Sarah Jones                |
| [Checkout basket v]                       |
| [Recovery context v]                      |
| Conversation       [HUMAN] [Resume AI]    |
| Agent / Customer / Merchant messages      |
| [Previous] [Latest] [Refresh]             |
|------------------------------------------|
| [Type your reply............]      [Send] |
+------------------------------------------+
```

## Required interaction states — ASCII

```text
AI MODE:              [AI] [Take Over]          Composer disabled
HUMAN + WINDOW OPEN:  [HUMAN] [Resume AI]       [Type reply...] [Send]
HUMAN + WINDOW CLOSED, FOLLOW-UP ELIGIBLE:
  Free-form text unavailable.
  [Approved recovery follow-up template v] [Send Follow-up]
  Notice: consumes one recovery-conversation credit.
HUMAN + FOLLOW-UP USED:
  Window closed; the recovery's one follow-up is already used.
  No further recovery-initiated follow-up can be submitted.
HUMAN + STORE SUSPENDED:
  Conversation and basket remain readable; [Resume AI] available.
  HUMAN MESSAGING UNAVAILABLE / composer and Take Over disabled.
PENDING SEND:
  Accepted / Queued (not 'Sent'); disable duplicate submission.
FAILED / STALE REVISION / ABUSE REJECTED:
  Show authoritative safe error, update control and message state.
```

Sample customer names, products and amounts in diagrams are illustrative, never production fixtures. The layout is a required UX contract, not a mandate to build a separate page.

## Requirements

### WordPress and hosted API boundary

1. Reuse `includes/Rest/RecoveryDetailController.php`, `includes/Api/ModaApiClient.php` and the existing recovery detail route registration. Each browser-to-WordPress read/write requires normal logged-in WordPress `manage_woocommerce` capability and REST nonce. PHP-to-hosted continues using the verified connected installation and server-held Bearer credential. Never accept a browser-supplied `shopId` as authority.
2. Keep the approved authenticated reads `GET /v1/merchant/recoveries/:recoveryId`, its `/messages` and `/related` pages. Forward basket, control mode/revision, customer-service window, follow-up eligibility and public human-messaging ACTIVE/SUSPENDED state from the hosted API. Do not expose internal Admin reasons/notes.
3. Add only the required WordPress REST proxy operations for the existing Woo-only hosted routes: `POST /v1/merchant/conversations/{conversationId}/control` (Take Over/Resume AI), `POST /v1/merchant/conversations/{conversationId}/messages` (human text/approved follow-up template), and `GET /v1/merchant/conversations/{conversationId}/send-commands/{commandId}` (durable command status). Use the conversation ID from the selected recovery detail; preserve expected revision, idempotency key and supported template parameters. Forward allowlisted fields and typed upstream errors/status without leaking secrets.
4. Enforce recovery/shop/installation isolation at the authenticated hosted boundary; the UI cannot create or select arbitrary other-shop or standalone conversations. No browser-to-hosted API/Meta request. Handle disconnected/revoked/rotated installation credentials, invalid IDs, bounded timeouts and no-store response handling.

### Existing Recovery Detail UI

5. Reuse `src/recoveries/detail/recovery-detail-screen.js`, `recovery-detail-controller.js`, `hooks/use-recovery-detail.js`, `api/recovery-detail-client.js`, `conversation/conversation-panel.js`, `context/checkout-context-panel.js` and existing subcomponents. Add small control/composer/template modules as needed; never grow `page.js` into a monolith or create duplicate conversation state.
6. Display the **saved** checkout basket (not live Woo product state) with persisted product title, variant, quantity, optional image/item price, currency and total; show honest placeholders for missing/malformed `lineItems`, missing amounts or absent conversation. Avoid fabricated prices and floating-point transformations that alter displayed currency amounts.
7. Show one paginated transcript with CUSTOMER, AGENT, AUTOMATION and HUMAN attribution, text/transcription and actual provider status. Preserve related recoveries, milestones, browser back/navigation, selected recovery, focus, pagination and manual refresh. Do not invent unread counts or auto-scroll away from what the merchant is reading.
8. Keep conversation primary on desktop and basket/context alongside; stack or collapse on narrow screens. All controls accessible, localised through WordPress i18n in 20 supported admin locales with fallback. Merchant admin UI language must not overwrite store/conversation language.

### Human control, follow-up and abuse

9. Display Take Over whenever an eligible recovery-linked conversation is in AI mode, regardless of WhatsApp 24-hour window; switch mode through hosted API with `expectedControlRevision`. In HUMAN mode show Resume AI. Inbound customer messages do **not** automatically resume AI. Recover gracefully from stale revisions, overlapping clicks and mode conflicts.
10. Only HUMAN mode permits human message submission; open customer service window permits validated free text. When closed, only a server-authorised approved recovery follow-up template is selectable if the **existing shared sequence-2** attempt remains eligible. Never initiate an independent follow-up or charge from WordPress. The normal scheduled no-response policy and shared credit rules remain Background-owned.
11. Suspend controls on shop-level human messaging restriction: keep basket and history readable, disable Take Over, human free text and follow-up template; allow explicit Resume AI. Treat restriction and deterministic abuse/rate-limit rejections as server-enforced outcomes, not merchant-configurable preferences.
12. Implement one stable client idempotency key per send intent; disable double-submission while pending and distinguish accepted/queued from actual provider send/status. Poll command status at a bounded cadence while relevant, stop when inactive, and show safe retry/error states without creating duplicate sends. Never claim provider-delivered status on HTTP command acceptance alone.

### Platform-specific WooCommerce boundary — no scheduling in the plugin

The WordPress plugin owns only WordPress permission/nonce validation, installation-credential forwarding to existing hosted Woo endpoints, and the Recovery Detail UI; hosted API-003/004 perform the canonical PostgreSQL control/command transactions. PHP and React must **not** publish BullMQ jobs, poll the PostgreSQL command table, invoke Meta directly, or implement Woo-only message abuse/follow-up/billing policy. The single BG002 platform-neutral dispatcher processes commands accepted by Woo API or Shopify server identically. WordPress command-status UI polling is for presentation only; it must stop when no longer selected/visible. Preserve existing two-stage WordPress navigation, 20 merchant locales, all desktop/mobile ASCII diagrams and separate developer-owned post-implementation validation.


## Work Items

- [ ] Extend existing Woo PHP recovery-detail read facade and client for the enriched basket/conversation/restriction response.
- [ ] Add existing-installation-authenticated WordPress REST proxies for control, send and command-status, using allowlisted request/response fields and typed errors.
- [ ] Extend the current recovery-detail components/controller with saved basket, conversation attribution, AI/HUMAN controls, responsive desktop/narrow layout and twenty-locale WordPress strings.
- [ ] Add human composer/template eligibility, accepted/queued/provider status, idempotency, stale revision and merchant suspension states.
- [ ] Record exact changed files, implemented flows, remaining limitations and handoff notes in the Completion Report. **Do not make developer test execution part of these Work Items.**

## Interfaces / Contracts

- Read: Woo browser -> authenticated WordPress REST recovery detail -> existing hosted `GET /v1/merchant/recoveries/:recoveryId`, paginated `/messages` and `/related` enriched by `ARCH-040-API-002`.
- Commands: Woo browser -> WordPress REST nonce/capability gate -> hosted `ARCH-040-API-003` control and `ARCH-040-API-004` send/command-status operations, using the connected installation's credential and recovery-derived conversation ID.
- Delivery: `MerchantConversationSendCommand` in PostgreSQL -> shared `ARCH-040-BACKGROUND-001/002` policy/consumer -> existing WhatsApp transport/receipts. No new Conversation or synchronous provider call from Woo HTTP.

## Dependencies

- ARCH-040-API-002
- ARCH-040-API-003
- ARCH-040-API-004
- ARCH-040-BACKGROUND-002
- ARCH-035-API-013
- ARCH-035-WOOCOMMERCE-013

## Enables

- ARCH-040-SYSTEM-TEST-003

## Acceptance Criteria — feature implementation only

- [ ] The existing Woo Recovery Detail (not a new inbox) renders a genuine saved checkout basket, recovery context and the original mixed-author conversation on desktop and narrow screens, matching the ASCII layouts.
- [ ] WordPress-to-hosted API read/control/send/status paths exist with existing WP permission/nonce and connected-installation credential boundaries; browser secrets and cross-shop access are excluded.
- [ ] Merchant Take Over / Resume AI, in-window HUMAN free-text, eligible closed-window template, single recovery follow-up credit and durable idempotent command/status UI are implemented using the approved hosted/Background authorities.
- [ ] The UI correctly represents AI, HUMAN, closed-window, follow-up-used, suspended, rejected, queued and provider-confirmed status states; no duplicate conversation or independent WhatsApp delivery path is added.
- [ ] Existing navigation, modular code organisation and all twenty WordPress-admin locale paths are accommodated by the implementation.

**Validation is not an Acceptance Criterion.** These criteria describe delivered behaviour/code; the developer owns later validation and may report defects for correction. Do not add PHPUnit/Jest/Vitest/LocalWP execution or screenshots as unchecked acceptance items for this task.

## Validation

**Developer-owned only — not a task acceptance gate.** The developer will perform any PHP/JS/WP REST security tests, plugin build/ZIP checks, LocalWP/manual acceptance, responsive/locale checks and full platform/provider-flow validation **after delivery**. The implementing agent may describe suitable checks or review evidence already available but must not require the developer's validation run before submitting the feature for architect review. The later independent `ARCH-040-SYSTEM-TEST-003` remains an architecture certification task; it is not a dependency or an acceptance criterion of this Woo implementation task.

Suggested developer checks (informational, not checkbox/gate): WordPress capability/nonce denial; active vs disconnected installation; other-shop conversation rejection; mixed sender history and basket; takeover/revision conflicts; open-window free-text; closed-window eligible/used follow-up; queued vs provider receipt; suspended/abusive merchant states; 20 admin locales; responsive layout; LocalWP plugin build/install/ZIP; and ordinary diff hygiene.

## Implementation Notes

Keep one complete, vertically testable feature rather than three independent code deliveries. Implement underlying REST calls and UI states together; do not silently invoke an unimplemented API or duplicate Background policy. Preserve existing WordPress > WooCommerce > Moda Interact navigation and ARCH-035 code. No separate Shopify dependencies. Record any missing hosted API or Background capability as an architectural blocker, not a Woo-local workaround.

## Stop Condition

Once the implementation Work Items and **feature-only** Acceptance Criteria are met, complete the report, set `status: review` and return to `moda_architect`; STOP. **Do not wait for or require the developer to perform validation before moving this implementation task to review or for its code-level architect acceptance.** Developer validation is a separate handoff activity. Do not begin `SYSTEM-TEST-003` or subsequent tasks automatically.

## Completion Report

### Status
Not Started

### Files Changed
None.

### Work Completed
None.

### Validation Results
Developer-owned; not yet run and not an implementation acceptance gate.

### Deviations
None.

### Assumptions
The architecture is proposed; task execution requires the normal launcher and verified prerequisites.

### Unresolved Issues
None recorded at definition time.

### Architectural Concerns
Return any missing endpoint/contract or provider policy gap to moda_architect; do not invent a parallel runtime.

## Architect Review

### Review Status
Pending

### Review Notes
Not reviewed.

### Reviewed Files
None.

### Validation Reviewed
Developer-owned follow-up; not required for this task's implementation acceptance.

### Architecture Conformance
Pending.

### Follow-up
None.
