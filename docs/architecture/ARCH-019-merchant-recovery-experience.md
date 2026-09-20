---
id: ARCH-019
title: Merchant recovery overview, browsing and conversation experience
status: in_progress
coordinator: moda_architect
created: 2026-09-20
updated: 2026-09-20
---

# ARCH-019: Merchant recovery experience

## Status and agreement

Current frontier: DATABASE-001, SHOPIFY-001 and SHOPIFY-003 accepted/Complete at Attempt 1; SHOPIFY-002 accepted/Complete at Attempt 3. SHOPIFY-004 Ready at Attempt 0. SHOPIFY-005/006 and SYSTEM-TEST-001 remain Pending. Architecture remains In Progress; system validation is terminal and developer-invoked. Accepted dependencies are reconciled into SHOPIFY-004; readiness does not launch implementation or authorize unmerged dependency consumption.

## Problem and inspected current behaviour

The existing journey is usage overview → billing-period detail → customer modal → recovery selector → message table. Billing, recovery performance and shopper conversation history are mixed. Opaque recovery IDs and accounting identifiers dominate detail.

Inspected source: moda-interact/app/routes/app/home/route.jsx, routes/app/usage/route.jsx, routes/app/route.jsx, routes.ts, components/dashboard/{UsageOverview,Dashboard,Stats,RecoveryChart}.jsx, services/shop/merchant-route-access-policy.ts, and the canonical database schema. Baseline inspected app HEAD: 65c8289e9f0e0df29e251723d17171572aacac85; database HEAD: 3518f504a3ba1d600d603905a93371f385952cab. Existing unrelated local changes were not adopted or modified. Executors must re-read current accepted code, including pending-recovery and recovery-settings changes, before implementation.

Home loads all shop recoveries with all messages even for the usage overview. Recovery stats ignore the displayed billing period. Messages sent counts inbound messages too. The recovery chart segments count recoveries while its centre counts customers; pagination is browser-only. Usage history also hydrates all recoveries/message IDs and includes all period usageEvents. Current schema has no shop/date/id recovery index; its shop/admission-reason/status/date index does not match unfiltered browsing. Transcript has conversationId/createdAt but lacks the id tie-breaker.

## Goals and non-goals

Deliver a coherent recovery-first read experience, truthful date-cohort metrics, tenant-safe bounded browsing, a readable transcript, and a clear billing/history/support boundary. Preserve the embedded app shell, localization and lifecycle controls.

No reply composer, human takeover, resend/cancel recovery, new automated messages, credit consumption changes, subscription/refund changes, conversion attribution claims, currency conversion, new Shopify scopes, LLM work, global customer CRM or standalone product/support conversation browser. No inferred product images/items; product data enrichment is outside this release. No new service, queue or infrastructure component.

## Target journey and routes

```text
/app                                Overview after onboarding; existing setup before it
  -> /app/recoveries                 Recovery list
       -> /app/recoveries/:recoveryId  Read-only recovery detail
/app/billing/options                 Existing Billing & recovery capacity
  -> /app/usage                      Usage history (existing URL)
/app/merchant-support                Support (existing inbox)
/app/promotions                      Existing promotion experience
/app/recovery-settings               Existing recovery settings
```

List/detail are independently guarded embedded routes; detail must not inherit an expensive list loader. Additional read-only message resource routes are allowed under the same independent guard if required. No route accepts a browser-supplied shopId as authority. Preserve Shopify boundary headers/authenticated embed context using existing patterns.

Navigation for ACTIVE: Overview, Recoveries, Billing, Promotions, Support, Recovery settings. For NO_CONTRACT/FROZEN/BILLING_ATTENTION: Overview, Recoveries, Billing, Support. For ONBOARDING: Home, Support. For SUPPORT_ONLY/REINSTALLING: only existing Support surface; standalone restoration remains intact. SIGNED_OUT has no app navigation. Use localized labels and retain support unread count. There is no generic Settings route.

Add one RECOVERY_HISTORY surface permitted only for ACTIVE, NO_CONTRACT, FROZEN and BILLING_ATTENTION. Every list/detail/resource loader authenticates, resolves shop/lifecycle and checks that surface before recovery reads. Parent guards are not sufficient. Preserve all other current surface permissions, including ONBOARDING billing denial in current source. ARCH-013 is amended only for these page/navigation/breadcrumb responsibilities; its historical text must not restore permissions changed by accepted ARCH-017 work.

## Overview and metrics

Date inputs are merchant-local calendar dates. Default is the last 30 calendar dates including today. Offer Today, Last 7 days, Last 30 days and custom dates. Display explicit dates and time zone. Convert from inclusive start/end dates to [start-of-start-date, start-of-day-after-end-date) UTC using zone-aware calendar arithmetic, not 24-hour addition. Future end dates or reversed/invalid ranges produce localized validation without running a cohort query. Bound custom ranges to 366 inclusive dates. Use the existing merchantUi time-zone resolution/fallback; do not invent a browser-local zone.

All performance measures refer to distinct recovery records with detectedAt in that cohort and their latest known outcomes; outcomes may change after the range. They are not completion-date sales, every abandoned Shopify checkout, or billing consumption.

| Measure | Definition |
|---|---|
| Recoveries started | Count of cohort CheckoutRecovery records |
| Recovered checkouts | Cohort records currently COMPLETED |
| Recovery rate | Recovered / started; null and em dash when denominator is zero |
| Recovered checkout value | Sum recorded totalPrice for completed cohort rows per known currency; decimal-safe; no cross-currency sum |
| Ongoing in range | DETECTED + MESSAGE_SENT + ENGAGED within cohort |

Unknown totalPrice/currency is not silently zero: report omitted/unknown record count and a localized incomplete-value hint. Zero known completed rows may display no recovered value; unknown-only value displays unavailable. The UI shows currency groups separately and wraps them. The label is checkout value, not verified net revenue or causal uplift. Rates are rounded once for display using existing i18n helpers.

Show five newest cohort recoveries with View all. Ongoing metric opens the same date range plus ongoing filter. Summary metrics do not change with list search/status filters; they remain the full date cohort. Avoid single-category donut charts and invented historical comparisons.

Capacity is current and independent of performance dates; use existing billing capacity projection, source/expiry/reservation rules and availability states. Keep billing setup/restriction actions and current plan flows intact. Pending queue candidates remain a separate bounded section with their existing PENDING_RECOVERIES guard. An empty queue says nothing about overall service health. No new admission or credit-accounting logic belongs here.

## Query contract

Application-local contracts belong to moda-interact, not the shared package: normalizeRecoveryQuery, readRecoveryCohortSummary, readRecoveryPage, readRecoveryDetail, readRecoveryMessages, readRelatedRecoveries (names illustrative; semantics binding). New modules live in app/services/recoveries; producers and consumers are within this repository. Existing schemas/enums remain authoritative; do not duplicate cross-service runtime contracts.

List query uses from/to dates, status=all|ongoing|COMPLETED|EXPIRED|CANCELLED, q and cursor. q is trimmed, maximum 100 characters, case-insensitive substring match against customer firstName, lastName, combined display name or email within the same shop. Treat LIKE wildcard characters literally; always parameterize SQL. Search UI says Search customer. No promise to search opaque checkout tokens. Existing display reference may be used only if safe and durable; fallback label is Checkout · local date/time. Database IDs remain route identifiers, not primary labels.

List defaults to 25 rows, maximum 50, using (detectedAt DESC,id DESC) keyset traversal and one lookahead row. Cursors are opaque, bounded, strictly validated and bound to normalized filters; cursor contents never confer ownership. Include the original ordering keys so a deleted cursor row does not require an unscoped lookup. Prev/Next and refresh are supported without unbounded offset walks. Browsing is a live read: newly changed statuses can alter membership; do not promise a historical snapshot. Date changes/search/filter changes reset pagination.

List DTO: recovery ID, nullable owned customer display info, status, decimal-safe value/currency, detectedAt and safe display label. Do not include message bodies, lineItems, checkoutToken, checkoutUrl or billableActions. No latest-activity column in this release because it is not necessary to the agreed core browse flow. Provide separately bounded related-customer pages, not a customer count over a client-hydrated dataset.

Summary executes SQL aggregates, not findMany of all cohort records. Number of application queries per page must be fixed relative to result count, not N+1. Bounded transfer does not imply constant database cost: aggregation/search still scales with cohort size. The 366-date cap and indexed tenant/date predicates constrain scope. Record query plans; no arbitrary throughput claims. General substring-search indexing is deferred until measured evidence justifies it.

## Detail contract and interaction

Header: customer display name/email fallback or Guest, checkout value, current status, started date/time. Main column: chronological transcript. Side column: known milestones and related recoveries. Mobile: concise summary, transcript, expandable secondary context. No customer modal and no second selection gate.

Own recovery lookup is constrained by shopId and recoveryId. Message queries traverse its owned conversation, not a freely supplied conversationId. Related recoveries are same shop and customerId, exclude current, five per cursor page; absent customer gives no related-customer grouping. Missing/foreign IDs have the same unavailable response shape/status; no foreign metadata leaks.

Messages page at 50 plus lookahead with (createdAt,id) ordering. First window starts with the initial exchange; Previous/Next and Jump to latest provide complete traversal. Latest window is queried descending and displayed ascending; current page boundaries use original key values. No automatic polling, read-receipt mutation or provider call. Explicit refresh revalidates the selected resource, without background writes.

Sender mapping: CUSTOMER → Customer, AGENT → Moda assistant, AUTOMATION → Automated message, HUMAN → Team member; unsupported legacy value → Unknown sender. Do not conflate sender with direction. Inbound records are not assigned outbound delivery receipts. For outbound display recorded PENDING/SENT/DELIVERED/READ/FAILED with available corresponding timestamps; missing/unknown evidence says unavailable, not failed. Show stored time accurately without inventing a provider send time.

TEXT is escaped and direction-aware. AUDIO displays Voice message and the persisted successful transcription if present; pending/rejected/failed transcription receives a truthful localized label. UNSUPPORTED receives a safe placeholder. No provider-media playback/download or providerMediaId exposure. No internal tool messages, prompts, arbitrary metadata, raw provider errors or credentials. Safe links use approved http/https schemes and safe external-link semantics.

Milestones use existing recorded timestamps (detectedAt/messageSentAt/engagedAt/completedAt/expiredAt) and current status; no invented cancellation timestamp. Any statusHistory reasons exposed must be allowlisted merchant explanations, not raw metadata. History beyond these milestones is out of scope. No basket/product rendering from untyped lineItems in this release.

Back to recoveries preserves validated list query/cursor and router scroll state; direct entry defaults to list. Related recovery switching preserves the original return context. Do not accept arbitrary returnTo URLs. Use normal links/Back semantics, not mouse-only row handlers. Conversation is read-only.

## Billing bridge and compatibility

Keep /app/usage and its USAGE authorization as billing usage history, entered from Billing. Breadcrumb becomes Billing → Usage history. Keep current/past period and billId semantics, with explicit unavailable/not-found state for an unknown or foreign billId rather than silently selecting another shop's period. Existing default current/past choice remains when no billId was requested.

Authorized old /app?view=detail&bill=current|past&billId=... redirects to /app/usage with only validated billing parameters and necessary embed context. Before redirect, preserve onboarding/restoring/suspended/signed-out gates. Do not translate a billing period into an apparently equivalent recovery cohort. No redirect loop or /app/billing alias.

Usage pages retain bounded existing usage-event pagination (cap 100), aggregate quantity/count in SQL and retrieve source-recovery display data only for IDs on that page through tenant-constrained batched joins. Period selector pages at 25 plus one lookahead ordered (periodStart DESC,id DESC); retrieve an explicitly selected period by shop/id independently. Remove all-period usageEvents includes and all-recovery/message-ID joins. Source links point to owned recovery detail; missing/deleted/unresolved source remains a safe non-link. No accounting record mutation or quantity reinterpretation.

## State, localization and accessibility

Loading uses structural placeholders and an accessible busy state. Errors name the failed section and provide safe retry without erasing known context. Empty history differs from filtered zero results; Clear filters is available. Missing detail is neutral with Back to recoveries. Screens are usable at 320/390/1024px, with explicit focus, native links/buttons, no colour-only statuses and no nested modal scroll containers. Localize all added text through existing catalogues, preserve ICU parity, merchant-local time/money and RTL message content. No new translation provider calls.

## Data architecture, ownership and consistency

moda_database owns additive read indexes; moda_app owns readers/routes/UI/locales; moda_system_test owns integrated evidence. Canonical database tables and constraints remain unchanged apart from indexes. Queries are read-only and use parameterized/Prisma predicates. Recovery and billing histories remain separate concepts. Use a consistent read snapshot for multi-query cohort summary/preview where necessary; never hold transactions across provider calls. Other page requests represent current state at their own read time.

Required recovery indexes: (shopId,detectedAt,id), (shopId,status,detectedAt,id), (shopId,customerId,detectedAt,id). Required transcript index: (conversationId,createdAt,id). Existing equivalent indexes must be reused; preserve unrelated indexes. No separate database release task is needed: this is schema/index Git publication consumed at the accepted commit, not a published npm package.

No Background, Messaging, Shared, Admin, Site or Gateway implementation is needed: no provider flow, queue contract, route exposure topology or deployable unit changes. Application capability gaps beyond this scope return to architect rather than growing a task silently.

## Security and observability

Every read is tenant-scoped; lifecycle and authentication are server-side. Cursor/filter IDs are untrusted. Retain redaction, safe content rendering and existing framework/shared telemetry. Remove full recovery/message payload debug logging from touched Overview/Usage paths. Do not create duplicate HTTP metrics or route telemetry. Existing error instrumentation is sufficient; bounded query/response evidence belongs to tests and review, not a new production analytics system.

## Rollout and rollback

Classification: compatible additive rollout. No assumption that existing production state can be discarded. Apply the index migration before app release; validate migration locally and let the developer perform deployment under existing tooling. Consume the architect-approved database revision in the app's dedicated task worktree. Integrate accepted app changes in dependency order and deploy the complete experience after SHOPIFY-006 acceptance; intermediate routes need not be advertised or separately deployed.

No queue drain, new secrets, provider configuration, worker release, new service or contract version. Existing /app/usage and old detail entry links remain supported. Rollback is to the previous app release while leaving additive indexes in place; index removal is optional and database-owned after consumer review. Never edit deployed migration history or destroy data. Developer retains merges, main pushes, deployment and final top-level Gitlink integration.

Required terminal system validation follows all accepted implementation tasks and developer manual exercise. Architecture is not Implemented until required evidence and architect review are complete. Long/live validation execution follows workspace policy; Ready does not start it.

## Task plan

| Task | Owner | Status | Depends on |
|---|---|---|---|
| [ARCH-019-DATABASE-001](../decisions/database/ARCH-019/DATABASE-001-index-merchant-recovery-read-paths.md) | moda_database | Complete | None |
| [ARCH-019-SHOPIFY-001](../decisions/shopify/ARCH-019/SHOPIFY-001-bounded-recovery-cohort-readers.md) | moda_app | Complete | ARCH-019-DATABASE-001 |
| [ARCH-019-SHOPIFY-002](../decisions/shopify/ARCH-019/SHOPIFY-002-bounded-recovery-detail-readers.md) | moda_app | Complete | ARCH-019-DATABASE-001 |
| [ARCH-019-SHOPIFY-003](../decisions/shopify/ARCH-019/SHOPIFY-003-recovery-list-page.md) | moda_app | Complete | ARCH-019-SHOPIFY-001 |
| [ARCH-019-SHOPIFY-004](../decisions/shopify/ARCH-019/SHOPIFY-004-recovery-conversation-detail-page.md) | moda_app | Ready | ARCH-019-SHOPIFY-002, ARCH-019-SHOPIFY-003 |
| [ARCH-019-SHOPIFY-005](../decisions/shopify/ARCH-019/SHOPIFY-005-recovery-performance-overview.md) | moda_app | Pending | ARCH-019-SHOPIFY-001, ARCH-019-SHOPIFY-003, ARCH-019-SHOPIFY-004 |
| [ARCH-019-SHOPIFY-006](../decisions/shopify/ARCH-019/SHOPIFY-006-merchant-navigation-and-billing-history.md) | moda_app | Pending | ARCH-019-SHOPIFY-005 |
| [ARCH-019-SYSTEM-TEST-001](../decisions/system-test/ARCH-019/SYSTEM-TEST-001-validate-merchant-recovery-experience.md) | moda_system_test | Pending | ARCH-019-DATABASE-001, ARCH-019-SHOPIFY-001, ARCH-019-SHOPIFY-002, ARCH-019-SHOPIFY-003, ARCH-019-SHOPIFY-004, ARCH-019-SHOPIFY-005, ARCH-019-SHOPIFY-006 |

Current frontier: DATABASE-001, SHOPIFY-001 and SHOPIFY-003 accepted/Complete at Attempt 1; SHOPIFY-002 accepted/Complete at Attempt 3. SHOPIFY-004 Ready at Attempt 0. SHOPIFY-005/006 and SYSTEM-TEST-001 remain Pending. Architecture remains In Progress; system validation is terminal and developer-invoked. Accepted dependencies are reconciled into SHOPIFY-004; readiness does not launch implementation or authorize unmerged dependency consumption.


## Risks and evidence gaps

Case-insensitive substring search and long-range aggregates need measured plans on representative data; no capacity promise is made. Index build locks depend on existing row counts/environment and must be documented by DATABASE-001. Existing source contains unrelated uncommitted UI work; task isolation and synchronization protect it. Unknown/missing message attribution must remain visible rather than guessed. No system capability is claimed deployed by the prototype.

## Change history

- 2026-09-20: agreed product experience translated into eight bounded tasks; added query indexes and bounded billing-history integration after source inspection; current onboarding permissions explicitly retained.

- 2026-09-20: accepted DATABASE-001 after populated PostgreSQL 15.19 evidence; promoted SHOPIFY-001/002 and assigned transcript query-shape validation to SHOPIFY-002.

- 2026-09-20: accepted SHOPIFY-001 at `08af00b` after source review and 27 passing tests including PostgreSQL; promoted SHOPIFY-003. Full typecheck remains blocked by independently verified pre-task syntax debt.

- 2026-09-20: accepted SHOPIFY-003 `37c62cd` after 72 passing tests, source/access/locale review and local browser evidence. No downstream promotion while SHOPIFY-002 awaits acceptance.

- 2026-09-20: accepted SHOPIFY-002 Attempt 3 at `1a60f1e` after fixture correction, 37 unit tests and supplied five-test PostgreSQL evidence; promoted SHOPIFY-004.
