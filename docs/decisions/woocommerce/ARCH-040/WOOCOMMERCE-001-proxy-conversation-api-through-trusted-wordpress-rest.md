---
id: ARCH-040-WOOCOMMERCE-001
architecture_id: ARCH-040
title: Implement complete WooCommerce Recovery Detail human conversation feature
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 40
executor: developer
claimed_at: 2026-10-21T17:54:56Z
attempt: 1
depends_on:
  - ARCH-040-API-002
  - ARCH-040-API-003
  - ARCH-040-API-004
  - ARCH-040-API-005
  - ARCH-040-BACKGROUND-002
  - ARCH-035-API-013
  - ARCH-035-WOOCOMMERCE-013
  - ARCH-040-DATABASE-005
  - ARCH-040-BACKGROUND-006
enables:
  - ARCH-040-SYSTEM-TEST-003
created: 2026-10-14
updated: 2026-10-23
---

# ARCH-040-WOOCOMMERCE-001 — Complete WooCommerce Recovery Detail human conversation feature

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Execution record:** Developer-owned Attempt 1. The WooCommerce implementation is committed and published at `2e037c6da30e4035a6ddd683d9eab725d8ce9576` on `origin/task/ARCH-040-WOOCOMMERCE-001`. Parent worktree claim and Attempt 1 metadata are preserved; formal review and explicit developer completion have not yet occurred. This task consolidates former `ARCH-040-WOOCOMMERCE-001`, `-002` and `-003` into **one feature implementation**.

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

### Semantic moderation: WordPress facade and existing Recovery Detail

Do not invoke OpenAI in PHP or React. The existing WordPress REST facade passes through the Woo-only hosted API's safe moderation status/reason and verifies nonce/capability and connected installation as usual. Within the same existing Recovery Detail layout show CUSTOMER flagged/review notice, HUMAN `Checking message...`, blocked/no-send/revise notice, review-required and retryable-unavailable states. Keep source text and sender identity in the original transcript and distinguish moderation from provider delivery. Reuse all 20 merchant translations; no extra Woo-specific moderation queue, database model, API-key or merchant role. Preserve ASCII desktop/mobile layouts already present in WOOCOMMERCE-001.

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

- [x] Extend existing Woo PHP recovery-detail read facade and client for the enriched basket/conversation/restriction response.
- [x] Add existing-installation-authenticated WordPress REST proxies for control, send and command-status, using allowlisted request/response fields and typed errors.
- [x] Extend the current recovery-detail components/controller with saved basket, conversation attribution, AI/HUMAN controls, responsive desktop/narrow layout and twenty-locale WordPress strings.
- [x] Add HUMAN open-window text composer, accepted/queued/provider status, idempotency, stale revision and merchant suspension states.
- [ ] Add the closed-window approved recovery-follow-up template selector from a server-authorised template/due-time read contract. The current hosted Recovery Detail response does not supply a selectable approved variant list or effective eligibility time; no WordPress-side template inference is permitted.
- [x] Record exact changed files, implemented flows, remaining limitations and handoff notes in the Completion Report. **Do not make developer test execution part of these Work Items.**

## Interfaces / Contracts

- Read: Woo browser -> authenticated WordPress REST recovery detail -> existing hosted `GET /v1/merchant/recoveries/:recoveryId`, paginated `/messages` and `/related` enriched by `ARCH-040-API-002`.
- Commands: Woo browser -> WordPress REST nonce/capability gate -> hosted `ARCH-040-API-003` control and `ARCH-040-API-004` send/command-status operations, using the connected installation's credential and recovery-derived conversation ID.
- Delivery: `MerchantConversationSendCommand` in PostgreSQL -> shared `ARCH-040-BACKGROUND-001/002` policy/consumer -> existing WhatsApp transport/receipts. No new Conversation or synchronous provider call from Woo HTTP.

## Dependencies

- ARCH-040-API-002
- ARCH-040-API-003
- ARCH-040-API-004
- ARCH-040-API-005
- ARCH-040-BACKGROUND-002
- ARCH-035-API-013
- ARCH-035-WOOCOMMERCE-013


- ARCH-040-DATABASE-005

- ARCH-040-BACKGROUND-006
## Enables

- ARCH-040-SYSTEM-TEST-003

### Customer-window and configured follow-up parity

The existing Recovery Detail composer must show HUMAN free-text availability only within 24 hours of latest verified inbound CUSTOMER WhatsApp message. Outside that rolling window (or if never replied), it may offer **one** approved recovery follow-up template only when the recovery's effective configured follow-up due time has arrived and sequence 2 remains unused. No hardcoded 24-hour wait from initial outreach, new timer, direct provider call or settings reinterpretation in WordPress. The hosted Woo API's API-005 correction and Background-008 final admission are authoritative; display only safe server-projected status. This feature still has **no Shopify dependency**. Developer-run integrated validation is separate from implementation acceptance.

## Acceptance Criteria — feature implementation only

- [x] WooCommerce displays only server-authorised moderation outcomes through its existing API/REST facade with no browser-side moderation or cross-store leakage.

- [x] The existing Woo Recovery Detail (not a new inbox) renders a genuine saved checkout basket, recovery context and the original mixed-author conversation on desktop and narrow screens, matching the ASCII layouts.
- [x] WordPress-to-hosted API read/control/send/status paths exist with existing WP permission/nonce and connected-installation credential boundaries; browser secrets and cross-shop access are excluded.
- [ ] Merchant Take Over / Resume AI, in-window HUMAN free-text, eligible closed-window template, single recovery follow-up credit and durable idempotent command/status UI are implemented using the approved hosted/Background authorities.

**Outstanding feature criterion:** Take Over / Resume AI, HUMAN text and durable send status are implemented. The approved closed-window template selector remains unavailable until the hosted API publishes an authoritative eligible template/options and configured due-time projection. The one-follow-up and charging rules remain Background-owned. This unchecked criterion must be resolved or explicitly amended by `moda_architect` before the task can be declared feature-complete.
- [x] The UI correctly represents AI, HUMAN, closed-window, follow-up-used, suspended, rejected, queued and provider-confirmed status states; no duplicate conversation or independent WhatsApp delivery path is added.
- [x] Existing navigation, modular code organisation and all twenty WordPress-admin locale paths are accommodated by the implementation.

**Validation is not an Acceptance Criterion.** These criteria describe delivered behaviour/code; the developer owns later validation and may report defects for correction. Do not add PHPUnit/Jest/Vitest/LocalWP execution or screenshots as unchecked acceptance items for this task.

## Validation

**Developer-owned only — not a task acceptance gate.** Developer-provided PHP/JS/WP REST security, local build/ZIP, responsive and locale checks are informational evidence, not an implementation acceptance gate. **LocalWP installation, manual browser certification and full hosted/WhatsApp provider-flow checks belong to `ARCH-040-SYSTEM-TEST-003`**, not this WooCommerce implementation task. The implementing agent may describe suitable checks or review evidence already available but must not require the developer's validation run before submitting the feature for architect review. The later independent `ARCH-040-SYSTEM-TEST-003` remains an architecture certification task; it is not a dependency or an acceptance criterion of this Woo implementation task.

Suggested developer checks (informational, not checkbox/gate): WordPress capability/nonce denial; active vs disconnected installation; other-shop conversation rejection; mixed sender history and basket; takeover/revision conflicts; open-window free-text; closed-window eligible/used follow-up; queued vs provider receipt; suspended/abusive merchant states; 20 admin locales; responsive layout; local build/ZIP and ordinary diff hygiene. Live LocalWP installation, actual Meta delivery and cross-service end-to-end behaviour are covered by `ARCH-040-SYSTEM-TEST-003`.

## Implementation Notes

Keep one complete, vertically testable feature rather than three independent code deliveries. Implement underlying REST calls and UI states together; do not silently invoke an unimplemented API or duplicate Background policy. Preserve existing WordPress > WooCommerce > Moda Interact navigation and ARCH-035 code. No separate Shopify dependencies. Record any missing hosted API or Background capability as an architectural blocker, not a Woo-local workaround.

## Stop Condition

Once the implementation Work Items and **feature-only** Acceptance Criteria are met, complete the report, set `status: review` and return to `moda_architect`; STOP. **Do not wait for or require the developer to perform validation before moving this implementation task to review or for its code-level architect acceptance.** Developer validation is a separate handoff activity. Do not begin `SYSTEM-TEST-003` or subsequent tasks automatically.

## Completion Report

### Status

**Implementation published — ready for developer self-review of the implemented portion.** Developer Attempt 1 was claimed on 2026-10-21 at 17:54:56 UTC. The task remains `in_progress` until the authorised developer review workflow updates it; `attempt: 1`, `executor: developer`, and `claimed_at` are intentionally preserved. **Not architect-accepted and not Complete.**

Implementation: [`2e037c6da30e4035a6ddd683d9eab725d8ce9576`](https://github.com/kodjobaah/moda-interact-woocommerce/commit/2e037c6da30e4035a6ddd683d9eab725d8ce9576), pushed to `origin/task/ARCH-040-WOOCOMMERCE-001` on 2026-10-23. The final local status showed that task branch up to date with its remote, and only an unrelated untracked `typescript` terminal recording remained.

### Files Changed

The implementation commit contains **60 source, test and source-translation paths** in `moda-interact-woocommerce`:

- `includes/Api/ConversationCommandContracts.php`
- `includes/Api/ModaApiClient.php`
- `includes/Api/RecoveryDetailResponseValidator.php`
- `includes/Rest/RecoveryConversationCommandController.php`
- `includes/Runtime.php`
- `languages/moda-interact-cs_CZ.po`
- `languages/moda-interact-da_DK.po`
- `languages/moda-interact-de_DE.po`
- `languages/moda-interact-es_ES.po`
- `languages/moda-interact-fi.po`
- `languages/moda-interact-fr_FR.po`
- `languages/moda-interact-it_IT.po`
- `languages/moda-interact-ja.po`
- `languages/moda-interact-ko_KR.po`
- `languages/moda-interact-nb_NO.po`
- `languages/moda-interact-nl_NL.po`
- `languages/moda-interact-pl_PL.po`
- `languages/moda-interact-pt_BR.po`
- `languages/moda-interact-pt_PT.po`
- `languages/moda-interact-sv_SE.po`
- `languages/moda-interact-th.po`
- `languages/moda-interact-tr_TR.po`
- `languages/moda-interact-zh_CN.po`
- `languages/moda-interact-zh_TW.po`
- `languages/moda-interact.pot`
- `src/recoveries/detail/api/recovery-detail-contract.js`
- `src/recoveries/detail/connected-recovery-detail-screen.js`
- `src/recoveries/detail/context/checkout-basket.js`
- `src/recoveries/detail/context/checkout-context-panel.js`
- `src/recoveries/detail/context/recovery-milestones.js`
- `src/recoveries/detail/context/related-recoveries.js`
- `src/recoveries/detail/conversation/conversation-message.js`
- `src/recoveries/detail/conversation/conversation-panel.js`
- `src/recoveries/detail/human/conversation-command-client.js`
- `src/recoveries/detail/human/conversation-command-contract.js`
- `src/recoveries/detail/human/human-command-status.js`
- `src/recoveries/detail/human/human-conversation-controller.js`
- `src/recoveries/detail/human/human-conversation-controls.js`
- `src/recoveries/detail/human/human-mode-controls.js`
- `src/recoveries/detail/human/human-reply-composer.js`
- `src/recoveries/detail/human/use-human-conversation.js`
- `src/recoveries/detail/recovery-detail-controller.js`
- `src/recoveries/detail/recovery-detail-header.js`
- `src/recoveries/detail/recovery-detail-presentation.js`
- `src/recoveries/detail/recovery-detail-screen.js`
- `src/recoveries/detail/styles/_recovery-conversation.scss`
- `src/recoveries/detail/styles/_recovery-detail.scss`
- `tests/RecoveryConversationCommandControllerTest.php`
- `tests/RecoveryDetailControllerTest.php`
- `tests/i18n/locale-batch-010.test.mjs`
- `tests/i18n/locale-batch-011.test.mjs`
- `tests/i18n/locale-batch-012.test.mjs`
- `tests/i18n/locale-batch-013.test.mjs`
- `tests/i18n/release-assets.test.mjs`
- `tests/i18n/release-source.test.mjs`
- `tests/js/recovery-detail-integration.test.js`
- `tests/js/recovery-detail-shell.test.js`
- `tests/js/recovery-detail-shopify-visual-parity.test.js`
- `tests/js/recovery-human-conversation.test.js`
- `tests/js/recovery-human-ui-parity.test.js`

Generated `.mo` and locale-specific JavaScript translation `.json` assets were not included; only `.po` sources and the `.pot` template were committed.

### Work Completed

- Extended the existing Recovery Detail PHP read validator and `ModaApiClient` with saved checkout basket, conversation-control, provider status and human-messaging restriction fields.
- Added a WordPress REST command facade for revision-aware Take Over/Resume AI, HUMAN message admission and durable command-status lookup; reused the existing admin capability, nonce and installation-authenticated hosted API boundary without client-side provider credentials or a separate messaging pipeline.
- Built a modular HUMAN command controller, client/contract parser, hook, mode controls, reply composer and command-status display; provided stable idempotency on uncertain sends, duplicate-click prevention, retry/status refresh feedback and latest-message refresh without representing queue acceptance as delivery.
- Added saved basket details, separately presented **Checkout basket**, **Recovery activity** and **Related recoveries** cards, date-separated transcript, status attribution, and responsive Shopify-aligned layout. Corrected fixture-style customer-name presentation and control-row button alignment without changing business policy.
- Reconciled developer-reported UI parity/test/lint issues within Attempt 1. Kept WordPress i18n support across all 20 merchant locales, with 553 catalogue messages including English and 19 translated packs.
- Applied fail-closed handling for missing approved follow-up template options: do not invent template names, due-time eligibility, a second send path, or any credit rule in WordPress.

### Validation Results

Developer-performed validation, provided for review evidence **without becoming an implementation acceptance gate**:

- `npm run test:js`: **457/457 JavaScript unit tests** passed, with **53/53 JavaScript integration/i18n tests** passed in the same reported validation round.
- `npm run test:php`: **181/181 PHPUnit tests**, **1,357 assertions** passed in the earlier post-correction run.
- `npm run test:i18n`: **28/28** localisation checks passed; `npm run i18n:verify:20`: strict catalogue verification passed for **553 messages** / 19 translated packs plus English.
- `npm run lint:js`: **0 errors**, **6 pre-existing warnings** in `tests/js/billing-screen.test.js` concerning `@wordpress/no-global-active-element`.
- `npm run build`: passed. Reported non-fatal webpack bundle/entrypoint size warnings (approximately 298 KiB `index.js`, 448 KiB combined entrypoint).
- `git diff --check` passed during validation; `git diff --cached --check` emitted no issues before the final 60-file commit.
- Commit/push evidence in terminal log confirms remote `task/ARCH-040-WOOCOMMERCE-001` advanced to `2e037c6`; implementation branch then reported up-to-date with origin.
- Dedicated launcher/start-of-attempt synchronization packet and host environment details must be verified from the canonical launcher/task evidence; the supplied terminal recording establishes the branch, commit and push, **not** every preparation invariant.
- LocalWP deployment, live browser flow and hosted/Meta integration verification are intentionally deferred to `ARCH-040-SYSTEM-TEST-003`.

### Deviations

- The implementation includes iterative Shopify visual-parity improvements and corresponding localisation/test adjustments within the existing Recovery Detail feature; no new cross-repository runtime service was created.
- The specified **server-approved closed-window recovery follow-up template selector is not implemented**, because the accessible hosted Recovery Detail contract does not expose authoritative approved template choices or the effective configured due-time eligibility. The UI fails closed. This is an architectural dependency gap, **not** a completed acceptance criterion.

### Assumptions

- The Woo plugin must not infer provider-approved templates, customer consent, entitlement/sequence-2 eligibility or follow-up billing from local state. These remain server/Background-authoritative.
- Shopify parity refers to layout, labels and safe user-facing states, not a requirement to substitute Shopify values, tenant identities, currency or timezone for WooCommerce data.

### Unresolved Issues

- `moda_architect` must determine an owning hosted API read-contract task or explicitly amend the feature acceptance contract for the closed-window follow-up selector. No Woo-local workaround or unconditional template send is authorised.
- Hosted message-history reads may not include **command-only failed attempts** without a persisted conversation message. Status polling is available and truthful; full Shopify-style historical "Not sent" bubbles would require an approved server-side read projection, not invented client records.
- A previously observed `messaging.sender` platform-configuration `MISSING` error in the test environment prevented a send from proceeding. This concerns deployment configuration rather than a WooCommerce UI fix and requires environment verification in the applicable system test.
- Live LocalWP / actual hosted command and WhatsApp delivery testing has not been claimed as completed and is owned by `ARCH-040-SYSTEM-TEST-003`.

### Architectural Concerns

- **Blocking for full feature acceptance:** the server-authorised approved template list and configured due-time projection are missing from the current Woo Recovery Detail read contract. Preserve the original feature criterion until the architect resolves this dependency or authorises an explicit scope amendment.
- Do not regress the existing 24-hour customer-service window, HUMAN/AI control, single sequence-2 follow-up, Moderation fail-closed behaviour or durable idempotent command state to simulate a complete template UI.
- Do not treat this Completion Report as an architect acceptance decision or explicit developer completion.

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

## Dependency Frontier Reconciliation — 2026-10-21

ARCH-040-API-002 is complete. All explicit dependencies of this task are now Complete: ARCH-040-API-002, ARCH-040-API-003, ARCH-040-API-004, ARCH-040-API-005, ARCH-040-BACKGROUND-002, ARCH-035-API-013, ARCH-035-WOOCOMMERCE-013, ARCH-040-DATABASE-005, and ARCH-040-BACKGROUND-006. This normal agent/automatic implementation task is therefore `ready`; ownership is unchanged, with `executor: null`, `claimed_at: null`, and `attempt: 0`. This records eligibility only and does not claim or create an implementation worktree.

## Developer Takeover Amendment — 2026-10-21

The developer explicitly invoked `/moda_developer_create ARCH-040-WOOCOMMERCE-001` for this ready agent-owned task. Execution ownership is transferred to the developer and completion requires an explicit developer decision after architect review. The logical repository owner remains `moda_woocommerce`; task scope, dependencies, acceptance criteria and validation boundaries are unchanged.
