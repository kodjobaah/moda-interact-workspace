---
id: ARCH-050
title: Opt-in initial recovery outreach notifications with merchant Support deep links
status: in_progress
coordinator: moda_architect
created: 2026-10-26
updated: 2026-10-27
---

# ARCH-050 — Initial recovery outreach notifications in merchant Support

## Status

**In Progress.** The task definition has been materialised on the mirrored `task/ARCH-050-DATABASE-001` branches. `ARCH-050-DATABASE-001` is architect-accepted and Complete; five direct implementation tasks are now Ready. The architecture originated from the 2026-10-26 uploaded workspace snapshot and portable definition. Domain task indexes remain intentionally deferred until the architecture session is explicitly closed.

## Problem

A merchant may want to be alerted when Moda's automated CommerceAgent begins a WhatsApp checkout-recovery conversation. Shopify and WooCommerce already expose recovery details and a merchant Support inbox, but initial outbound recovery success does not create a Support message with a link into the matching conversation. Merchants currently have to find the recovery themselves.

## Goals

1. Add a per-shop merchant-controlled opt-in, default OFF: **Notify me when initial recovery outreach starts**.
2. After an **automated, sequence-1** WhatsApp recovery message has durable confirmed `SENT`, `DELIVERED`, or `READ` evidence, create **at most one** `SYSTEM` message in that merchant's existing `MerchantSupportThread` if the opt-in is enabled at first successful finalisation.
3. Provide a local **View conversation** action to the exact shop-scoped recovery details/conversation section on Shopify and WooCommerce; support both platforms without putting a WordPress URL or a Shopify URL in PostgreSQL.
4. Make notification admission transactionally consistent with the initial attempt's first successful finalisation; retries, concurrent workers, replay, settings toggles and follow-up sends must not create duplicates or late notifications.
5. Reuse the current Support inbox, recovery/outbound attempt lineage, shared logging, shop authentication, internationalisation and database; do not create a separate notifications system.
6. Cover success, suppression, tenancy, retry, preference concurrency and browser navigation in repository and integrated system tests.

## Non-Goals

- Email, SMS, Meta/WhatsApp notices to the merchant, browser push notifications, or external inbox products.
- A new conversation, support thread per recovery, staff account, merchant assignment, new admin console or notification delivery queue.
- Customer message copy or phone/basket contents in the Support alert; opening Recovery Detail remains the location for private customer data.
- Notification for manual human-authored outreach, customer replies, sequence-2 follow-up or scheduling alone.
- Changes to recovery credit accounting, message caps, consent/STOP enforcement, provider templates, or the WooCommerce production-outbound gate.
- Replacing existing ARCH-048 Woo checkout/order reconciliation, ARCH-046 final send admission or human handover.

## Current Architecture (inspected snapshot)

- `moda-interact-database/prisma/schema.prisma`: `ShopSettings` is a one-per-shop settings row, shared in practice by both platforms; `CheckoutRecovery` owns `outreachAttempts` and a recovery conversation; `RecoveryOutreachAttempt` has unique `(checkoutRecoveryId, sequence)` and `outboundMessageId`; Support uses `MerchantSupportThread` (unique `shopId`) and `MerchantSupportMessage` with unique nullable `sourceKey`, `systemCode`, `systemVersion`, `readAt` and `state`.
- `moda-interact-background/src/services/checkout-recovery/recovery-outreach-finalization.service.ts` finalises Shopify confirmed first sends through `markWaitingAfterConfirmedSend`, a recovery status update, and optional follow-up scheduling. Woo uses a separate finaliser in `src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts`; it must not inherit Shopify sequence-2 scheduling.
- `moda-interact-background/src/services/checkout-recovery/recovery-consent-merchant-notice.service.ts` already demonstrates concurrency-safe deduplicated insertion into existing Support threads using `createMany(skipDuplicates)` and `sourceKey`. Do not duplicate its generic Support infrastructure or introduce a competing logger.
- Shopify: `app/services/recovery-policy/recovery-policy.server.ts`, `app/components/settings/SettingsForm.tsx`, `app/routes/app/settings-save/route.ts` own the existing merchant policy; `app/services/merchant-support/merchant-support.service.ts`, `system-message-actions.ts` and `app/routes/app/merchant-support/route.jsx` own Support rendering; `/app/recoveries/:id` and `app/routes/app/recovery-detail/` own protected recovery conversation history.
- Hosted Woo API: `src/merchant/recovery-policy/contract.ts`/`service.ts` implement a strictly validated response and revision-checked writes; `src/merchant/support/contract.ts`/`read.service.ts` implement strict Support page shapes, tenant reads and message metadata.
- Woo plugin: `src/recovery-policy-client.js`, `src/recovery-settings/`, `src/support/support-contract.js`, `src/support/support-message-card.js`, and `src/recoveries/detail/detail-navigation.js`. `recoveryDetailHref()` already safely builds a local `admin.php?page=moda-interact-recoveries&recoveryId=<id>` target. The Woo JS API validators reject unrecognised response fields.
- The Woo initial outreach service (`src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`) currently allows outbound only for an injected test flag under `NODE_ENV=test`. This new architecture must not bypass that rollout gate; live Woo notices are conditional on separate production-outbound readiness.

## Proposed Architecture and decisions

### Merchant preference

Add `ShopSettings.notifyOnInitialRecoveryOutreach Boolean @default(false)` in the existing `shopify` Prisma schema. This setting is **per merchant**, not subject to the `ShopRecoveryPolicyOverride` discount/delay override; Woo consumes it through the existing authenticated hosted Recovery Policy API. Missing settings rows are treated as OFF; never auto-enable a shop. Settings updates retain revision/optimistic conflict protection. A merchant can enable/disable the setting without altering recovery delays, offers or follow-ups.

### Durable notification target

Add nullable `MerchantSupportMessage.checkoutRecoveryId` and a Prisma relationship to `CheckoutRecovery` with `onDelete: SetNull`, plus an index for lookups/cleanup. Other historical Support messages keep `NULL`. The existing thread's `shopId` is the notification tenant: the writer MUST prove `attempt.checkoutRecovery.shopId = MerchantSupportThread.shopId`; the read endpoints must recheck relationship ownership before emitting an action ID. No untrusted URLs are stored in the message.

### Trigger and atomicity

The trigger is **the first successful transactional finalisation of an automated INITIAL (`sequence=1`) send**, based on the durable outbound message's matching conversation, identity, provider-admitted `SENT|DELIVERED|READ` state and non-null `sentAt`; NOT queue dispatch, model generation, a bare send invocation, or provider-request acceptance without confirmed persisted send evidence. Existing credit commit stays owned by the billing service and is not re-created.

A Background-owned reusable service performs the **first attempt-state transition and optional Support insertion in one PostgreSQL transaction**. The transaction verifies matching shop/recovery/attempt/message lineage; it reads the opt-in at that first finalisation and records the one-time decision by the *fact of the first transition*. `false` means no notification, and a later retry after a merchant enables the option must not retroactively create one. `true` means the transactional transition inserts exactly one available, unread Support message; if it fails, the transaction rolls back and the worker retries (no silent swallow). A previously finalised attempt may be validated/replayed idempotently but MUST NOT create a fresh Support message after the first transition. Concurrent workers must safely create/find the single Support thread and dedupe with the existing unique `sourceKey`.

Canonical notification: `kind=SYSTEM`, `state=AVAILABLE`, `systemCode=RECOVERY_INITIAL_OUTREACH_SENT`, `systemVersion="1"`, `sourceKey=recovery-initial-outreach:v1:<outreachAttemptId>`, `checkoutRecoveryId=<id>`, bounded generic body, source language `en-GB`, no customer PII. Use the existing Support message translation/localisation conventions for merchant-facing text and translate/localise the action label in each UI. `lastMessageAt` updates without setting `needsAdminResponse` or incrementing `merchantMessageVersion` (this is not a ticket to internal support). Neither a new charge nor a merchant WhatsApp message is created.

Both automatic Shopify and Woo finalisers call the same Background primitive after durable send confirmation; the Woo adapter keeps its existing no-follow-up behaviour and never enables outbound in production. Existing HUMAN send flow and sequence-2 paths keep their current attempt-transition method; they never call the notice primitive.

### Action and route contract

Both merchant Support reads include `checkoutRecoveryId: string|null` (only if `SYSTEM`, code/version match and the recovery has `shopId` matching the authenticated Support thread). The UI creates the URL locally using its first-party route builder and a stable `#recovery-conversation` anchor. Missing, stale or cross-tenant IDs produce no action; any direct URL requires the destination recovery's existing independent server-side tenant and entitlement checks. There are no absolute, merchant-supplied or provider-supplied URLs.

For WooCommerce, the API is the **single HTTP contract owner**. Extend its strict Support history DTO to `schemaVersion:2` with required `checkoutRecoveryId` on every item (compose/read receipts remain v1), and its strict Recovery Policy DTO to `schemaVersion:2` with a **top-level** `notifyOnInitialRecoveryOutreach` Boolean in GET/PUT (unchanged `merchant/effective` four-field shapes); release matching WordPress browser validators/proxies together. These are hosted external application contracts, not new inter-service BullMQ payloads; the Woo extension cannot import Node-only `@modainteract/moda-interact-shared` APIs. Do not introduce Shared package work without a genuinely reusable runtime contract needed by multiple Node services. Shopify's internal loader is not a versioned external API.


## Explicit Implementation Contract (Attempt 2)

### Prisma model and migration fields

- `ShopSettings.notifyOnInitialRecoveryOutreach Boolean @default(false)` in `@@schema("shopify")`; **do not** add field to `ShopRecoveryPolicyOverride`.
- `MerchantSupportMessage.checkoutRecoveryId String?` with `checkoutRecovery CheckoutRecovery? @relation("RecoverySupportNotificationTarget", fields: [checkoutRecoveryId], references: [id], onDelete: SetNull)` and `@@index([checkoutRecoveryId])` in `@@schema("support")`.
- `CheckoutRecovery.merchantSupportMessages MerchantSupportMessage[] @relation("RecoverySupportNotificationTarget")` in `@@schema("commerce")`.
- One additive migration: Boolean `NOT NULL DEFAULT false`, nullable cross-schema FK to commerce recovery `ON DELETE SET NULL`, index. Existing `MerchantSupportMessage.systemVersion` is a **String?**; notification value MUST be literal `"1"`.

### Background-owned atomic port

Create `recovery-initial-outreach-support-notice.contracts.ts` + `.service.ts` under `moda-interact-background/src/services/checkout-recovery/` with:

```ts
type ConfirmedInitialRecoveryOutreachInput = {
  shopId: string;
  checkoutRecoveryId: string;
  outreachAttemptId: string;
  outboundMessageId: string;
  sentAt: Date;
  followUpDueAt: Date | null;
};
type InitialOutreachNoticeResult =
  | { outcome: "created"; outreachAttemptId: string }
  | { outcome: "disabled"; outreachAttemptId: string }
  | { outcome: "replayed"; outreachAttemptId: string };
interface ConfirmedInitialOutreachFinalizer {
  finalizeConfirmedInitial(input: ConfirmedInitialRecoveryOutreachInput): Promise<InitialOutreachNoticeResult>;
}
```

The port verifies **persisted** attempt/recovery/outbound ownership, trigger INITIAL, sequence 1, automated message `direction OUTBOUND`, `senderType AUTOMATION`, status `SENT|DELIVERED|READ` and `sentAt`, then locks the attempt and takes the first finalisation decision in one DB transaction. It does not require `initiatedBy=AUTOMATION`, because existing ordinary attempt creation leaves that value nullable; it rejects explicit `HUMAN` and relies on persisted outbound sender type. The port owns optional Support insertion and replay invariants. Shopify BACKGROUND-002 and Woo BACKGROUND-003 call it independently, retaining their original billing and checkout status orchestration. Human and sequence-2 paths retain the existing attempt service.

### Merchant API shapes and action contract

- **Hosted Woo recovery policy v2:** top-level `notifyOnInitialRecoveryOutreach:boolean` in successful GET/PUT response and required PUT request, **not** in `merchant`/`effective`. Keep original merchant/effective four-field recovery-policy values, revision locking and installation principal.
- **Hosted Woo Support history v2 only:** every `items[]` element has `checkoutRecoveryId:string|null`; Support compose/read receipt schemas remain v1. PHP (`includes/Api/SupportResponseValidator.php`) and JS (`src/support/support-contract.js`) validators must match. Hosted SQL projects linked recovery ID only for authorised same-shop recognised available SYSTEM notice.
- **Shopify internal history:** same `checkoutRecoveryId:string|null` shape, no hosted version negotiation; action gated by `canAccessMerchantSurface(state,"RECOVERY_HISTORY")` and destination's existing `requireRecoveryHistory`.
- **Navigation:** Shopify `/app/recoveries/${encodeURIComponent(id)}#recovery-conversation`, WordPress `recoveryDetailHref(id) + "#recovery-conversation"`. The reference is a validated ID, **not** an external URL or an authorization grant.

### Exact implementation file boundaries

| Task | Primary created/modified files |
|---|---|
| DATABASE-001 | `moda-interact-database/prisma/schema.prisma`, `prisma/migrations/<timestamp>_arch050_.../migration.sql`, PostgreSQL schema test |
| BACKGROUND-001 | New `checkout-recovery/recovery-initial-outreach-support-notice.contracts.ts` and `.service.ts`, unit and PostgreSQL integration tests |
| BACKGROUND-002 | `checkout-recovery/recovery-outreach-finalization.service.ts` and focused tests; Shopify initial sequence only |
| BACKGROUND-003 | `woocommerce-recovery/woo-recovery-outreach.adapters.ts` and focused tests; Woo initial sequence only |
| SHOPIFY-001 | `recovery-policy.server.ts`, `settings-save/route.ts`, `recovery-settings/RecoverySettingsView.tsx`, 20 locale keys/tests |
| SHOPIFY-002 | `merchant-support.service.ts`, `system-message-actions.ts`, `merchant-support/route.jsx`, `recovery-conversation-thread.tsx`, locales/tests |
| API-001 | `src/merchant/recovery-policy/{contract,service,routes}.ts`, unit/PostgreSQL tests |
| API-002 | `src/merchant/support/{contract,read.service,routes}.ts`, unit/PostgreSQL tests |
| WOOCOMMERCE-001 | PHP `RecoveryPolicyResponseValidator.php`, JS `recovery-policy-client.js`, `recovery-behaviour-{fields,validation,panel}.js`, relevant proxy/tests |
| WOOCOMMERCE-002 | PHP `SupportResponseValidator.php`, JS `support-contract.js`, `support-message-card.js`, `detail-navigation.js`, `conversation-panel.js`, tests |
| SYSTEM-TEST-001/002 | `moda-interact-system-test/catalogue/scenarios.json`, separated `src/harness/recovery/` fixtures/executors, harness tests and evidence |

Each file path is relative to its owning implementation repository, not to the `docs` folder. Task files contain the exact interfaces, validations, negative cases and stopping points; this table is a navigation aid and does not supersede them.

## Request / Event Flow

```text
Merchant recovery setting (Shopify UI or WooCommerce UI -> hosted API)
           |                        |
           +------------+-----------+
                        v
               ShopSettings (Postgres)
                        |
  existing Shopify / Woo checkout and order processing
                        v
     Background: confirmed automated initial outreach
           |  durable provider status SENT/DELIVERED/READ
           v
  first-send finalisation + preference read + optional
  MerchantSupportMessage insert (SAME DB TRANSACTION)
           |
           v
       one Support thread / shop
           |
         +-------------------------------+
         |                               |
         v                               v
 Shopify Support read               Woo hosted Support read
 tenant guarded                     installation+shop guarded
         |                               |
         v                               v
 local /app/recoveries/:id          local WordPress admin.php?page=...
        #recovery-conversation            &recoveryId=...#recovery-conversation
         |                               |
         +-------------------------------+
                         v
     authenticated, tenant-scoped recovery conversation
```

## Repository Responsibilities and Implementation Tasks

| Task | Owner | Status | Depends on |
|---|---|---|---|
| ARCH-050-DATABASE-001 | moda_database | Complete | None |
| ARCH-050-BACKGROUND-001 | moda_background | Ready | ARCH-050-DATABASE-001 |
| ARCH-050-BACKGROUND-002 | moda_background | Pending | ARCH-050-BACKGROUND-001 |
| ARCH-050-BACKGROUND-003 | moda_background | Pending | ARCH-050-BACKGROUND-001; ARCH-048-BACKGROUND-005 (Complete) |
| ARCH-050-SHOPIFY-001 | moda_app | Ready | ARCH-050-DATABASE-001 |
| ARCH-050-SHOPIFY-002 | moda_app | Ready | ARCH-050-DATABASE-001 |
| ARCH-050-API-001 | moda_api | Ready | ARCH-050-DATABASE-001 |
| ARCH-050-API-002 | moda_api | Complete | ARCH-050-DATABASE-001 |
| ARCH-050-WOOCOMMERCE-001 | moda_woocommerce | Pending | ARCH-050-API-001 |
| ARCH-050-WOOCOMMERCE-002 | moda_woocommerce | Ready | ARCH-050-API-002 |
| ARCH-050-SYSTEM-TEST-001 | moda_system_test | Pending | ARCH-050-BACKGROUND-002; ARCH-050-SHOPIFY-001; ARCH-050-SHOPIFY-002 |
| ARCH-050-SYSTEM-TEST-002 | moda_system_test | Pending | ARCH-050-BACKGROUND-003; ARCH-050-API-001; ARCH-050-API-002; ARCH-050-WOOCOMMERCE-001; ARCH-050-WOOCOMMERCE-002; ARCH-048-WOOCOMMERCE-002/003 |

Task status derives from canonical task metadata and verified prerequisites, not from this planning table. Complete prerequisite tasks do not need to be re-opened. The two terminal system-test tasks allow Shopify testing independently of the Woo plugin work; no implementation task depends on either system test. The developer may validate manually before invoking Ready system-test tasks.

## Data, Transactions, Ordering and Idempotency

- Existing PostgreSQL `ShopSettings` is the durable preference source; existing Support `sourceKey` uniqueness is the one-notification-per-attempt fence. The sequence-1 attempt's uniqueness remains the sole recovery-generation/sequence identity. Use its ID, not a checkout token or phone, as notification source identity.
- A shop cannot create an action to another shop's recovery. Writer and readers verify ownership; the destination read independently authorises.
- The first finalisation transaction is the one-time preference sampling point. It atomically moves the initial attempt into its confirmed durable state and inserts/omits the Support message. Retries validate already-sent lineage but never change the original preference decision; turning ON later is not backfill. Turning OFF after finalisation does not delete existing notifications.
- Use a narrow transaction, no network/Redis/Meta/LLM call inside it. Billing finalisation remains outside the transaction through existing idempotent calls; a failed Support transaction does not undo an already-authoritative external provider send or charge. Retry through existing durable provider admission/idempotency without resending or charging twice.
- Treat dead/stale recovery FK as `NULL` and omit action. Keep Support's existing pagination/unread semantics and authorisation.
- Record first-outreach Support notice creation / disabled / replay / failure with safe bounded correlation fields, via the platform Shared logger. Persistence exceptions always propagate for retry; logging failure never changes a committed result. The explicit policy and task-specific contracts below are mandatory.

### Structured logging and exception contract (Attempt 3)

- **Node owners:** Background, hosted API and Shopify server-side code must use the existing approved `@modainteract/moda-interact-shared/logging` export and `docs/observability/shared-logging.md`. Reuse existing process/service loggers and injection points; do not introduce generic JSON loggers, ad hoc `console.*`, direct unstructured `JSON.stringify`, or a new observability transport. Set service/process identity through existing runtime configuration (`moda-recovery-worker`, `moda-interact-api`, `moda-interact` as applicable); never let individual feature modules override canonical environment identity.
- **Authoritative Background event names:** `recovery.initial_outreach_support_notice.created`, `.disabled`, `.replayed` (info) and `.failed` (error). Use a stable result/outcome plus safe identifiers only after validation: `shopId`, `checkoutRecoveryId`, `outreachAttemptId`, `outboundMessageId`, `platform` (when available) and a bounded `errorCategory`; for unexpected exceptions pass `{ error }` to the Shared logger's bounded Error serializer. Do not log customer name, phone, email, checkout contents, message text, provider bodies, credentials, raw HTTP payloads or SQL parameters. Treat expected OFF/replay outcomes as successes, **not** errors.
- **Caught operational exceptions are never silent.** In the shared Background transaction owner: catch outside the transaction, emit the failure event with safe correlation/error context, then `throw error` unchanged. In Shopify/Woo Background integration: preserve existing admission, billing, compensation and BullMQ retry semantics; if a callsite catches an error, log it with a platform-specific stage/context and rethrow the **same** exception. Do not return `disabled`, `replayed`, `null`, an empty page or apparent success for database/persistence/authorisation failures. Do not mark the original provider send failed, issue another send, or charge again solely due to a notification-write exception.
- **Failure isolation exception:** A logging sink/serialisation exception alone may be suppressed in a narrowly scoped, documented log-safe adapter: it must never mask the original business exception or break a successfully committed transaction. This is the *only* allowed intentionally ignored exception for the new Background logic. Do not log from inside the interactive Prisma transaction.
- **HTTP/API boundaries:** Keep existing approved `StructuredLogger` in route options and established error/status mapping. Log unexpected server/database failures using `.error` with a sanitized Error and operation, warn for handled conflict/integrity where appropriate; keep authorization/validation responses safe. No fake success, dropped rejection or generic fallbacks on infrastructure failure. Shopify server routes use the same Shared logger.
- **WooCommerce boundary:** Node Shared logging is **not** a PHP or browser dependency. PHP continues the existing WordPress/WooCommerce logger/`WP_Error` conventions for caught operational failures with redacted metadata; browser controllers must surface failures in their existing error states rather than silently discarding promises. Pure invalid-link/invalid-input outcomes are expected results, not unexpected exceptions.
- **Tests:** Inject a recording/failing logger into the Background unit tests. Verify each outcome event, failure event including bounded non-sensitive context, original exception identity on rejection, rollback and retry, and sink failure isolation. API/Shopify and Woo tests should exercise their owning catch/response/error-state boundaries. Integrated system tests confirm failed notification persistence is observable and never misreported as success, without requiring a new Grafana/OTLP service.

## Security and Privacy

- Shopify must use `authenticate.admin`, the existing Support shop guard, the recovery detail guard and route-access rules; an action shown in Support cannot bypass Recovery Detail restrictions.
- Woo browser must use WordPress/Woo authentication and nonce, PHP proxy/installation credential, hosted shop-scoped Support and recovery reads; never expose hosted credentials or open a merchant-controlled public endpoint for Background.
- Host/API and merchant UIs only expose a validated relative recovery reference. Resist forged cross-shop references, malformed IDs and open redirects. No arbitrary URL is accepted or stored.
- Consent, local STOP, WhatsApp service window, human takeover and moderated message handling remain unchanged.

## Failure handling and scale

- Only genuinely confirmed first sends enter the notification action path; Shopify raw webhook volume does not fan out into notifications. No additional external calls, queues or worker deployables required. One indexed settings lookup, the existing attempt transition, single Support-thread find/create and at most one Support-message insert per actionable confirmed initial send.
- Persistent failure of the notification transaction causes worker retry and must be surfaced to the existing structured logs/worker failure visibility; do not claim success or silently discard. Provider dedupe/credit fences ensure replay is not another send.
- A large shop's Support thread retains the existing paginated read; this feature adds at most one system message per eligible automated initial attempt and no per-checkout hot-path read before a confirmed send.

## Deployment / Rollout

**Pre-production definition** for this architecture; do not infer that existing merchant installations can automatically accept a breaking API DTO change. Schema migration first, then Background/Shopify and hosted API, then a corresponding Woo plugin build with version-2 policy/Support parsers; no production promise until the actual deployment plan is agreed. Existing historical Support rows retain nullable `checkoutRecoveryId`; default OFF prevents an immediate notification burst. The Woo production outbound gate remains OFF independently of this feature; production Woo messages/notices require separate rollout acceptance of the ARCH-048/046 safety path. The system-test task may use a controlled test-mode guarded sender; must not modify production gates to manufacture a pass.

## Validation

- Prisma schema/migration test; database FK deletion and query-index tests; shared writer concurrency/idempotency/rollback/integration tests; Shopify and Woo save/read DTO validation, revision conflict and negative tenancy tests; browser deep-link navigation and focus tests; end-to-end system tests for Shopify and Woo using supported test fixtures.
- Include consent/STOP, failed/blocked/provider-uncertain, initial confirmed, delivered-before-finalisation, replay after opt-in toggles, sequence-2 follow-up, human send, orphaned recovery and cross-tenant forged IDs.
- System testing is terminal and must not gate implementation tasks. No OpenTelemetry transport changes or new Gateway/Shared publication task is justified by this feature.

## Open Questions / Decisions for developer acceptance

1. Trigger definition is **durable confirmed send** (SENT or later), not confirmed device delivery; this matches current first-outreach finalisation semantics.
2. A changed preference takes effect on the first future initial-send finalisation. An earlier attempt that was already finalised does not produce a late notification on replay.
3. Existing Support inbox is the only merchant notification channel for v1. No browser live push; existing unread/pagination behaviour is retained.

## Change History

- 2026-10-27 — Accepted ARCH-050-DATABASE-001; promoted its five eligible direct dependants to Ready.

- 2026-10-26 — Attempt 3: made shared structured logging, explicit exception reporting/rethrow, log-sink isolation and test expectations normative across Background, hosted API and merchant surfaces; no new runtime service or schema change.

- 2026-10-26 — Attempt 2: replaced generic task descriptions with concrete Prisma declarations, service port, file ownership, strict hosted API v2 shapes and test contracts. Corrected `systemVersion` to string `"1"` and documented Shopify notification-only save idempotency.

- 2026-10-26: Initial external portable task definitions and cross-platform architecture based on supplied snapshot; no source changes or index updates.
