---
id: ARCH-035
title: WooCommerce merchant Admin UI parity with Shopify
status: in_progress
coordinator: moda_architect
created: 2026-10-11
updated: 2026-10-20
---

# ARCH-035: WooCommerce merchant Admin UI parity with Shopify

## 20 October 2026 — Woo checkout/order **capture-only** architectural amendment

**Authoritative scope for reopened ingestion tasks; overrides older superseded checkout/recovery designs below.** The Woo lifecycle work is limited to taking checkout and order events from a connected Woo store, authenticating them in the hosted API, accepting them in existing Redis/BullMQ infrastructure, and validating them in isolated Woo-specific Background consumers. It must **not** initiate customer recoveries, update `CheckoutRecovery`, perform Shopify GraphQL checkout lookup, send WhatsApp, record consent evidence, manage merchant allowlists, bill usage, or execute offers. Those features remain outside this implementation and are not prerequisites.

**No new database tables/migrations or new Shared implementation are authorised.** `ARCH-035-DATABASE-001`, `SHARED-001`, `DATABASE-002`, `BACKGROUND-003` and `SYSTEM-TEST-003` remain superseded, as do previously superseded Woo offer tasks. Shopify's current model uses BullMQ events and writes `CheckoutRecovery` only when recovery becomes actionable; do not manufacture recovery rows to archive Woo events. API-008 owns a strict `woo.activity.v1` OpenAPI contract, with PHP plugin and Background adapters matching that contract. If a genuinely missing Shared cross-service mechanism is discovered, stop and refer that dependency to the architect rather than duplicate cryptographic/validation libraries.

### Reopened capture tasks and ownership

| Task | Responsibility | Initial status | Dependencies |
|---|---|---|---|
| `ARCH-035-API-008` | Authenticated Woo `CHECKOUT_UPDATED` API, queue producer and contract | Ready | None |
| `ARCH-035-WOOCOMMERCE-007` | Guest/authenticated Classic + Blocks checkout capture and bounded retry | Pending | API-008 |
| `ARCH-035-API-019` | Add placed/paid/cancelled order variants on same API endpoint, order queue producer | Pending | API-008 |
| `ARCH-035-WOOCOMMERCE-008` | Authoritative Woo order hooks with checkout-to-order key and publisher reuse | Pending | API-019, WOOCOMMERCE-007 |
| `ARCH-035-BACKGROUND-001` | Woo checkout queue consumer, validate and observe capture only | Pending | API-008, WOOCOMMERCE-007 |
| `ARCH-035-BACKGROUND-002` | Woo order queue consumer, validate and observe capture only | Pending | API-019, WOOCOMMERCE-008 |
| `ARCH-035-SYSTEM-TEST-002` | Terminal capture-only integration certification | Pending | All six implementation tasks above |

**API endpoint:** single `POST /v1/woocommerce/activity`, authenticated with the existing active Woo installation credentials. The API owns the exact bounded `woo.activity.v1` schema and current installation-derived Shop identity; the client never chooses `shopId`. Queue acceptance is the durable HTTP acknowledgement point. API-008 creates the Woo checkout producer and API-019 adds the Woo order producer, both using existing Redis/BullMQ infrastructure but **not** Shopify queues. The two Woo workers must not compete for jobs on the same queue, or feed the existing Shopify recovery services. The same `eventId` is retained on retries of one source event; true new updates have new IDs. Redis job retention bounds deduplication; this architecture does not claim permanent event receipts or permanent order fencing.

**Checkout identity:** The Woo plugin emits a stable, merchant-scoped checkout key on updates and preserves it in HPOS-compatible order metadata. Order events distinguish `ORDER_PLACED`, `ORDER_PAID` and `ORDER_CANCELLED` and include their authoritative Woo order ID. No phone/email-based correlation and no inferred payment success from placement. If the API is unavailable, the Woo plugin must not block shopper checkout/order actions; reuse existing retry facilities (Woo Action Scheduler where needed), no custom WordPress queues/tables.

**Capture-only consequence:** Successful completion of a Woo Background job is an observation, not a durable business-state record. Completed jobs can expire under BullMQ retention and may not be replayable after this phase. The later Woo recovery/checkout-state-reader integration requires a separate, explicit architectural decision; do not activate the Shopify maturity/materialisation or order-completion side effects in this amendment. Existing Shopify recovery processing must remain unchanged.

**Integration gate:** API queues/producers and Woo-specific consumers must be deployed before Woo event publishing is enabled; ensure no undeliverable jobs accumulate during rollout. Test real Classic/Blocks/HPOS inputs, retries, order-first and checkout-first arrival, shop isolation, queue failure, and absence of recovery/WhatsApp/credit side effects. `SYSTEM-TEST-002` is terminal and depends only on the six required implementation tasks; it no longer depends on Recoveries list/analytics. Existing `SYSTEM-TEST-001` and `SYSTEM-TEST-004` keep their independent UI/Knowledge validation scopes. Do not modify any `docs/decisions/**/_index.md` during this architecture session.

**Baseline:** Reconciled against the complete `moda-interact-workspace(20261020-075304).zip` attachment. `ARCH-040-DATABASE-006` is present in that snapshot; no database changes are requested by this amendment. Task definitions are portable and unclaimed; verify current canonical task branches and dependency status before launcher materialisation.

---

## 17 October 2026 — browser-direct Woo Merchant Knowledge uploads (approved amendment)

**Current design supersedes the 16 October PHP-mediated file transfer only; it does not reopen `ARCH-035-API-017`.** In `moda-interact-workspace(20261017-114953).zip`, API-014, API-015, API-016 and API-017 are each recorded `complete` in their task YAML. API-017 already implements shop-bound presigned `PUT` intents, `uploadUrl`, `requiredHeaders` (`Content-Type`, `If-None-Match: *`, `x-amz-meta-sha256`), bounded expiry and verified size/type/SHA-256 finalisation. That completed implementation and its historical acceptance remain unchanged.

**New gap and owner:** `ARCH-035-API-018` is a new, independently reviewable API task for browser-direct compatibility, no-store/credential-safe handoff, signed-header/redirect/URL guarantees, accurate OpenAPI/browser integration evidence and any *proven* minimal correction; it does **not** repeat API-017 lifecycle implementation. `ARCH-035-GATEWAY-001` owns the operational R2 CORS policy and approved Woo site-origin enrolment. CORS is not authentication: signed object-scoped URL and tenant-bound API intent/finalise remain the authority. There is no wildcard-origin grant or automatic trust of arbitrary `Origin` values.

**Canonical file flow:** privileged Woo React requests metadata-only intent through same-origin WordPress (`WOOCOMMERCE-014`) → authenticated Moda API returns a short-lived presigned R2 `PUT` URL and exact required headers → WordPress returns only that bounded capability to the authenticated administrator without caching/logging → React (`WOOCOMMERCE-015`) hashes/validates and sends the **binary directly to the approved R2 S3 endpoint** without Woo installation secrets → React requests metadata-only finalisation through WordPress → API-017 verifies the R2 object and durably records source/revision → existing Background reconciliation processes eligible pending revisions. WordPress PHP never accepts, buffers or proxies the CSV/XLSX bytes. Fail closed on missing CORS enrolment, failed preflight, expired signature, invalid header, wrong hash, aborted upload, provider failure, site URL change or rotated installation credentials. No client-asserted success before server finalisation.

**18 October configuration reconciliation:** `ARCH-043-API-001/002` are accepted Complete and now supply the canonical sealed PostgreSQL `merchant.knowledge.r2` policy/credentials to the API upload and knowledge-read consumers on demand. Deployment environment retains only root unseal inputs; there is no legacy R2 credential fallback. API-018 must use this existing reader, update stale PHP-only browser upload contract documentation, and verify config-change behaviour across intent and finalisation. Its prerequisites are API-017 **and** ARCH-043-API-002; neither completed task is reopened.

**Task frontier (snapshot evidence, not remote branch state):** API-018 `ready` (depends on accepted API-017 and ARCH-043-API-002); GATEWAY-001 `pending` (depends on API-018); WOOCOMMERCE-014 `pending` (new dependency on API-018); WOOCOMMERCE-015 remains `pending` (depends additionally on Gateway and completion of W004); SYSTEM-TEST-004 remains `pending` with all required implementation and Gateway dependencies. All required status promotion must be rechecked in the canonical developer workspace; uploaded ZIP cannot prove branches/claims. `moda_system_test` may use LocalWP for integrated system certification; the LocalWP prohibition applies to WooCommerce repository implementation agents, while developer manual validation is a separate checkpoint.

**Rollout:** API-018 accepted and deployed → approved R2 CORS/origin policy provisioned and verified → WooCommerce metadata broker/browser uploader enabled → developer manual validation → terminal system-test certification. Existing API-017, Shopify keys/paths, database schema, Background semantics, installation credential boundaries and unrelated UI remain unchanged. Do not update `docs/decisions/**/_index.md` during this architectural session.

## 16 October 2026 — 22:56 repository-structure reconciliation

The uploaded `moda-interact-workspace(20261016-225609).zip` implements the ARCH-041 hosted API modular refactor. **The seven Merchant Knowledge extension tasks remain architecturally valid, but their handoffs must target the current feature-first source boundaries.** Each task below has a structure-specific Implementation Notes addendum. This note changes no task ID, owner, `depends_on`, `status`, `attempt`, or previously superseded definition.

- Hosted merchant endpoints are assembled in `moda-interact-api/src/composition/merchant.ts` and passed through `src/composition/routes.ts`; production code belongs under `src/merchant/<feature>/`, with Woo installation authentication in `src/auth/woo-installation/` and bounded shared HTTP primitives under `src/http/`. **Do not** add merchant operations to the narrowed `src/woocommerce/installation/routes.ts` or write another startup router in `src/index.ts`.
- The API validation layout is `tests/unit/merchant/<feature>/`, `tests/integration/merchant/<feature>/`, with explicit disposable PostgreSQL runners registered in the `test:integration` script. OpenAPI specifications reside in `moda-interact-api/openapi/`. API-014..017 own feature-preference/knowledge contracts and must use the installed published Shared primitives as applicable.
- The API does not yet configure R2 or contain a Merchant Knowledge queue publisher. API-017 owns any bounded upload-only R2 configuration and must identify genuine deployment/secret wiring gaps for `moda_gateway`; neither missing R2 nor Redis should disable unrelated merchant reads. Existing Background Merchant Knowledge reconciliation reads durable `PENDING` revisions and enqueues processing. API-016/017 must ensure durable, eligible pending work is discoverable instead of requiring a new direct BullMQ producer or external call within a transaction.
- WordPress continues to register its PHP facades in `moda-interact-woocommerce/includes/Runtime.php`, `includes/Rest/`, and `includes/Api/`. WOO-014 extends those boundaries; WOO-015 owns React connections under `src/recovery-settings/`. W003's production feature client currently returns unavailable; W004's Merchant Knowledge UI source is **absent in this snapshot**, notwithstanding earlier portable patch work. W004 is recorded `ready` (not `complete`) in the latest task YAML, so WOO-015 is gated on accepting/materialising W004 and including its source in the implementation baseline.
- This is a **documentation-only review** of an uploaded code snapshot, not a branch, commit, task claim, integration test, or final acceptance decision. Do not modify any `docs/decisions/**/_index.md` until the developer ends the architecture session.

## 16 October 2026 — approved functional Merchant Knowledge parity extension

**Decision (developer approved, 16 October 2026):** The developer has explicitly extended the ARCH-035 scope beyond its earlier UI-only boundary **only for WooCommerce merchant feature preferences and Merchant Knowledge management**. This section supersedes older UI-only/non-API exclusions **for these bounded capabilities only**. The superseded `ARCH-035-API-003`, `API-004`, and `API-005` historical task definitions remain superseded; do not reopen or reclaim them. Other exclusions (checkout/order ingestion, recovery business execution, coupon offers, billing changes, Meta/WhatsApp, and Promotions) remain in force. ARCH-036 continues to own discount/coupon functionality, and proposed ARCH-042 owns promotion-credit parity.

**Evidence and limitation:** Inspected from `moda-interact-workspace(20261016-175534).zip` and `moda-interact-workspace-api(8).zip`, plus the W004 UI patch evidence supplied in this session. In the snapshot, `WOOCOMMERCE-003` is Complete, `WOOCOMMERCE-004` is Ready with an accepted UI-only definition (its newer patch attempts are not yet present in this base ZIP), and the Woo feature-preferences client explicitly returns `FEATURES_UNAVAILABLE`. The API has authenticated Woo merchant route infrastructure but no live Merchant Knowledge/feature-preference routes. Shopify already contains Merchant Knowledge services and API operations; Background contains Merchant Knowledge entitlement reconciliation. Source existence is not a runtime certification. No new local Git branch, worktree, commit, publication or developer-side merge has been created by this portable patch.

### Approved behaviour and boundaries

- Reuse canonical Shop-scoped `Feature`, `BillingPlanFeature`, `ShopFeaturePreference`, `MerchantKnowledge*` and existing R2/revision/Background processing data. **No new tables, migrations or duplicate knowledge catalogue.**
- Optional `merchant_knowledge` preference controls runtime ingestion/retrieval, **not** whether plan-entitled merchants may configure or retain sources. Disable preserves sources. Read projects real feature and entitlement/capacity state, not simulated zeroes.
- Source actions: list, add HTTPS web page, edit, refresh, reorder, delete, upload CSV/XLSX via signed intent and verified finalisation, replace/reprocess where already supported. Distinguish durable revision creation, queued/processing/active/failed lifecycle and merchant-disabled/dormant eligibility. Existing source IDs and histories remain Shop-scoped.
- `moda-interact-api` owns authenticated hosted merchant APIs; `moda-interact-woocommerce` owns privileged WordPress REST mediation (`manage_woocommerce`, nonce, connected installation credential and site-identity gates), React controller/state and 20-locale UI. Browser never accesses hosted Moda credentials, PostgreSQL or Redis.
- Preserve independent WordPress administrator UI language, shop language and source language tag. Reuse published `@modainteract/moda-interact-shared` validation and merchant-knowledge schemas where compatible; expose strict versioned HTTP/OpenAPI schemas, not copied ad hoc DTO variants in multiple Node repositories.
- **Shopify upload reuse caveat:** Shopify's `upload.server.ts` validates a `*.myshopify.com` upload domain. That exact domain parser is not usable for arbitrary Woo installations. Hosted API must derive a stable Woo storage identity from the authenticated canonical Shop/installation, not a client-controlled domain or unsafe string. Preserve Shopify's existing key scheme and R2 objects. Proposed Woo scheme: `merchant-knowledge/<environment>/woocommerce/<validated-shop-id>/<asset-uuid>/source.<csv|xlsx>`. Validate worker compatibility before adoption; do not expose credentials or allow arbitrary object-key choice.
- **Current Woo file transport choice (17 October amendment):** React obtains upload intent/finalise metadata through authenticated WordPress PHP, performs the presigned bounded `PUT` directly to R2 with exact signed headers and no installation credentials, then finalises through WordPress. PHP handles **no uploaded file bytes**. Approved exact-origin R2 CORS configuration is required; no wildcard trust. Preserve client hash/type/size checks, terminal server-side verification, abort/error handling, expiry/idempotency and no network operations in database transactions.
- Reuse existing Background source-revision queue and entitlement reconciliation. Confirm how disabled sources are resumed when enabled, with real Postgres/queue proof. If a concrete cross-repository deficiency is found, stop the affected task and return a bounded correction to `moda_architect`; do not silently patch Background from API/Woo tasks.
- Existing Moda API ingress topology remains sufficient. Browser-direct R2 introduces a **concrete Gateway-owned CORS/origin-enrolment requirement** (`ARCH-035-GATEWAY-001`). Only hosted Node services use `@modainteract/moda-interact-shared/logging`; the Woo plugin/browser do not. No signed URLs, credentials or file payloads in logs; reuse approved OTel instrumentation.

### Proposed versioned HTTP boundary (owned by moda_api)

| Endpoint | Role | Task |
|---|---|---|
| `GET/PUT /v1/merchant/feature-preferences` | Read effective/required/optional feature state, compare-and-set changed preference | API-014 |
| `GET /v1/merchant/merchant-knowledge` | Real entitlement, allowed formats, language tags, sources/revisions/capacity | API-015 |
| `POST /v1/merchant/merchant-knowledge/sources`, `PATCH/DELETE /.../sources/{id}`, `POST /.../sources/{id}/refresh`, `PUT /.../order` | Shop-scoped source lifecycle and ordering | API-016 |
| `POST /v1/merchant/merchant-knowledge/upload-intents`, `POST /.../upload-finalize`, `PATCH /.../uploads/{sourceId}`, `POST /.../uploads/{sourceId}/reprocess` | Accepted signed/verified upload lifecycle (unchanged); browser-facing contract review in API-018 | API-017 Complete, API-018 new |

API-014 establishes the versioned feature-pref DTO with `expectedRevision` and bounded `changes` (not the W003 fixture's `preferences` request without mediation). API-015 defines the canonical knowledge read DTO. API-016/017 publish matching strict OpenAPI request/response/error schemas; Woo adapters validate and map them, rather than define competing business authority. All APIs derive `shopId` exclusively from the Woo installation principal, verify `Shop.platform === WOOCOMMERCE`, use bounded input/error projection, fail closed on revoked/rotated grants, and never trust browser-submitted shop/plan/entitlement identity.

### Task and dependency graph (newly defined, not materialised)

```text
API-014 (feature pref read/write) -----+-------------------------------+
                                      |                               |
API-015 (knowledge read) ---+---------+                               |
                            |         |                               |
                            v         |                               |
           API-016 (web lifecycle)    |                               |
           API-017 (upload lifecycle) |                               |
                            |         |                               |
                            +---------+-------------------------------+
                                      |
                                      v
                           WOOCOMMERCE-014 (PHP proxy)
                                      |
                                      v
  WOOCOMMERCE-003 (Complete) ----> WOOCOMMERCE-015 (live W003/W004)
  WOOCOMMERCE-004 (UI foundation) ->   |
                                      v
                          SYSTEM-TEST-004 (terminal)
```

New task identifiers (all docs under `docs/decisions/<domain>/ARCH-035/`):

| Task | Assigned Agent | Initial status | Depends on |
|---|---|---|---|
| ARCH-035-API-014 | moda_api | Ready | None |
| ARCH-035-API-015 | moda_api | Ready | None |
| ARCH-035-API-016 | moda_api | Pending | API-015 |
| ARCH-035-API-017 | moda_api | Pending | API-015 |
| ARCH-035-WOOCOMMERCE-014 | moda_woocommerce | Pending | API-014, API-015, API-016, API-017 |
| ARCH-035-WOOCOMMERCE-015 | moda_woocommerce | Pending | WOOCOMMERCE-003, WOOCOMMERCE-004, WOOCOMMERCE-014 |
| ARCH-035-SYSTEM-TEST-004 | moda_system_test | Pending | API-014, API-015, API-016, API-017, WOOCOMMERCE-015 |

**Current 17 October dependency frontier (supersedes the earlier task-creation graph above):**

```text
API-017 (Complete) -> API-018 (Ready, browser-contract review) --+--> WOO-014 (Pending, WP metadata broker)
                                                                 |
                                                                 +--> GATEWAY-001 (Pending, CORS)
                                                                                      |
WOO-003 (Complete) ----+                                                            |
WOO-004 (acceptance pending) ---+                                                     v
WOO-014 (after API-018) --------+----------------------------------------------> WOO-015 (Pending)
                                                                                      |
API-014/015/016/017 (Complete) --- API-018 --- GATEWAY-001 --- WOO-015 --------------> SYSTEM-TEST-004
```

`SYSTEM-TEST-001` remains the original terminal UI parity task and is not a prerequisite for application implementation or SYSTEM-TEST-004. The developer may validate the completed feature manually before invoking ready system testing. This extension **does not** make the unresolved `WOOCOMMERCE-004` UI-only implementation Complete, change its attempt, or modify any existing `_index.md`.

**Rollout classification:** No production compatibility waiver is granted for the existing Shopify system. Add Woo API routes and verification without breaking existing Shopify readers/writers, migrations, R2 object keys or Background jobs; deploy API before the Woo plugin update; allow incomplete/aborted uploads to expire or be cleaned up; protect rollback by preserving durable rows and historical grants. Check cross-provider tests before enabling Woo writes.

**Architecture status:** In Progress, not Implemented. Acceptance requires the new implementation tasks, developer manual validation, SYSTEM-TEST-004 and the original relevant terminal parity tests to be completed or explicitly declared not applicable.

## Status and revision context

**UI-led revision, 11 October 2026; source-reconciled 16 October 2026.** The developer narrowed ARCH-035 to the WooCommerce merchant interface and requested ASCII page designs. After approving the Recoveries shell, the developer authorised **bounded read-only APIs for page data**. On 12 October, the developer also authorised **API-002**, a narrowly scoped write endpoint for merchant recovery delay and follow-up settings, without reopening recovery processing or provider offers. This replaces the earlier UI-plus-checkout/order-recovery lifecycle architecture. No implementation task is accepted; no parent or implementation task branch was created/pushed by this portable-document handoff. Do not update any `docs/decisions/**/_index.md` files until the developer explicitly confirms final reconciliation.

## 16 October 2026 — source-based reconciliation

This reconciliation uses the `moda-interact-workspace(20261016-105855).zip` snapshot as implementation evidence, **not** a history of completed task worktrees, commits or test runs. The original UI-only/supersession scope remains in force. No runtime code, `docs/decisions/**/_index.md`, task attempt counters or original Completion Reports were changed by this review.

- **Retrospectively architect accepted and marked Complete (6):** `API-002`, `WOOCOMMERCE-002`, `WOOCOMMERCE-009`, `WOOCOMMERCE-011`, `WOOCOMMERCE-012`, `WOOCOMMERCE-013`. The code implements these scoped capabilities. This is not an assertion of historical launcher/worktree evidence or of LocalWP/system-test certification.
- **Developer-authorised retrospective completion (2):** `API-009`, then `API-013`. Both were architect-accepted on 16 October and have `completion_mode: developer`. The 19 October completion patch records the developer's requested source-evidence closure in dependency order; historical execution and full runtime validation remain unverified and are not represented as passed.
- **Newly Ready (4):** `WOOCOMMERCE-001` Support, `WOOCOMMERCE-003` feature preferences, `WOOCOMMERCE-005` Promotions, `WOOCOMMERCE-006` Usage History. All their recorded prerequisites are now Complete.
- **Still Pending (3):** `WOOCOMMERCE-004` Merchant Knowledge (after `WOOCOMMERCE-003`); `WOOCOMMERCE-010` recovery analytics Overview (after `WOOCOMMERCE-006` and `WOOCOMMERCE-013`); terminal `SYSTEM-TEST-001` (after all ten required Woo UI tasks). The existing Overview still shows account/store/category data rather than the specified recovery performance, capacity, recent and pending sections.
- **Superseded (20):** unchanged. In particular the checkout/order capture, Background lifecycle and provider offer processing remain outside ARCH-035 and must not be revived by this reconciliation.

**Verification from this session:** Woo `npm run test:i18n` passed 28 tests; `npm run i18n:verify:20` passed for 332 source strings, 19 translation packs / 20 canonical locales; relevant PHP navigation and REST files passed `php -l`. JavaScript and TypeScript runtime test suites, LocalWP interactions, ZIP/build commands, disposable PostgreSQL validation, worktree isolation and original task Completion Reports were not independently executed or available in this supplied archive. The final UI parity system test is not complete, so the initiative remains **In Progress**, not Implemented.

**Navigation clarification:** the approved two-stage experience is intentional: `WooCommerce > Moda Interact` as an entry point, then the native `Moda Interact` top-level menu with nested merchant pages. This is not an accidental duplicate menu; the code suppresses the legacy in-page tabs when using the native merchant routes.

## Problem and inspected starting state

The inspected `moda-interact-workspace(20261011-192347).zip` has a native WordPress plugin with working connected Overview, Billing and Recovery Settings/Store Category surfaces. `moda-interact-woocommerce/includes/Admin/NativeNavigation.php` still uses `register_planned` for Recoveries, Promotions and Support; its `src/native-admin/page-surface.js` and `src/page/connected-workspace.js` handle only Overview/Billing/Recovery Settings. Woo Usage History and Recoveries detail are not current UI surfaces. Shopify has merchant Support, Promotions, Recoveries list/detail, Usage History, a richer Overview, and Recovery Settings with policy, feature preferences and Merchant Knowledge sections.

## Goal

Make WooCommerce **page structure, navigation, information hierarchy, validation/feedback and merchant interactions** match the current Shopify merchant-facing experience as closely as WordPress Admin permits. Keep WordPress-native navigation and presentation rather than shipping Shopify-specific authentication or Polaris server components. All UI plans must be grounded in the actual Shopify source, not invented features, copy, backend data or status labels.

## Explicit non-goals and boundary

- No PostgreSQL schema or table additions, migrations, Database/Shared contract implementations or new queue events.
- No Woo checkout/order capture, lineage, recovery materialisation, provider-status reconciliation, new Background jobs, WhatsApp changes or new checkout recovery engine.
- No Woo coupon validation/selection/provenance, discount issuance, new billing/refund business behaviour or price/plan changes.
- No checkout capture, new private gateway/Render configuration or externally published contracts. Approved exceptions to the UI-only implementation boundary: bounded read-only API-009 and API-013, and API-002 read/write operations **solely for the existing merchant-owned recovery-start and no-response follow-up policy fields**. This does not authorise other writes, discount selection, provider recovery logic or new tables.
- No attempt to change the actual Shopify page behaviour. Shopify is read-only reference.
- No production fake data, fake success, made-up recovery revenue, credentials in browser storage or direct browser-to-hosted-API calls.

## Architecture and ownership

- **`moda-interact-woocommerce` (`moda_woocommerce`):** sole implementation repository for this UI initiative. Existing WordPress navigation, React components/hooks/controllers, CSS, native gettext and approved plugin REST client/proxy integration are in scope. No new hosted service routes or provider domain algorithms.
- **`moda-interact` (`moda_app`):** read-only Shopify UX reference.
- **`moda-interact-api` (`moda_api`):** bounded authenticated merchant UI data endpoints when individually authorised: read-only API-009 and API-013, and read/write API-002 for existing merchant recovery delay and follow-up policy only. No billing, ingress or recovery-processing changes.
- **`moda-interact-database`, `moda-interact-background`, `moda-interact-shared`, `moda-interact-gateway`:** no ARCH-035 implementation tasks.
- **`moda-interact-system-test` (`moda_system_test`):** one terminal UI parity/certification task, after all implementation tasks are accepted.
- **`moda_architect`:** cross-page design, task scope/dependencies, review, UI parity and documentation reconciliation.

### Existing service functionality versus UI parity

A page can be drawn and tested without creating backend operations. A missing approved data/action API **does not authorise a Woo repository agent to implement or invent that API**. The UI may use a test-only fixture and a strictly local presentation adapter for design and component tests, but merchant-facing production must show an honest unavailable/disabled state for unsupported operations. No missing real data is represented as zero, a successful send, a successful save, a selected promotion, recovered revenue or an active AI capability.

If the developer later wants full real-end-to-end merchant feature parity, the missing hosted API/checkout/order/offer capabilities require separately scoped architecture and implementation, not hidden scope expansion in ARCH-035.

## 12 October 2026 — Shared discount-catalogue implementation boundary

Following merchant approval, the shared Shopify/WooCommerce coupon catalogue, provider-aware discount sync, multi-coupon persistence and send-time proof are **separately owned by ARCH-036**, not by the ARCH-035 UI-only initiative. ARCH-035-WOOCOMMERCE-011 remains a local read-only coupon preview until the separately accepted ARCH-036 hosted selection/proof tasks make customer-facing offers safe. **No new discount tables** are approved; reuse the physical Shopify discount catalogue tables. No ARCH-035 backend tasks are reactivated by this cross-link.

## 12 October 2026 — Native coupon catalogue preview (bounded UI exception)

The developer authorised a staged *Specific WooCommerce Coupon* experience. Stage 1, `ARCH-035-WOOCOMMERCE-011`, is limited to merchant-facing discovery of **local Woo coupon records** with a privileged WordPress GET, bounded pagination, search, responsive layout and explicit preview-only state. It does **not** activate the earlier superseded coupon eligibility/selection/database/background tasks; it does not add a hosted read grant or new cross-service contract. The Recovery Behaviour PUT remains delay/follow-up-only with the existing offer unchanged. Coupons are not offered to customers and the preview radio choice is not persisted. Durable selection and send-time verification require a separately agreed provider-capability architecture. This narrow local catalogue UI exception supersedes the earlier blanket coupon UI exclusion only for this Stage 1.

## Shopify-to-Woo source map

| Shopify reference | Native Woo target | Task |
|---|---|---|
| `app/routes/app/merchant-support/route.jsx` | Support submenu: message thread/composer | WOOCOMMERCE-001 |
| `app/routes/app/recovery-settings/RecoverySettingsView.tsx` | Recovery Settings: effective policy + behaviour sections | WOOCOMMERCE-002 |
| `app/components/settings/FeaturePreferences.tsx` | Feature controls **within Recovery Settings** | WOOCOMMERCE-003 |
| `app/components/settings/MerchantKnowledgeSection.tsx` | Merchant Knowledge **within Recovery Settings** | WOOCOMMERCE-004 |
| `app/routes/app/promotions/route.tsx` | Promotions credits submenu | WOOCOMMERCE-005 |
| `app/components/dashboard/UsageEvents.tsx` | Usage History linked from merchant surfaces | WOOCOMMERCE-006 |
| `app/routes/app/recoveries/RecoveryList.tsx` | Recoveries list/filter/pagination submenu | WOOCOMMERCE-009 |
| `app/routes/app/recovery-detail/RecoveryDetail.tsx` | Recoveries detail with message history | WOOCOMMERCE-013 |
| `app/components/dashboard/RecoveryOverview.tsx` + `PendingRecoveries.jsx` | Richer Woo Overview | WOOCOMMERCE-010 |
| Shopify merchant navigation layout | WordPress Admin surface registry/breadcrumbs/links | WOOCOMMERCE-012 |

Existing Woo Billing and Store Category/connection screens are preserved and included in UI regression comparison; no speculative redesign task is assigned to already implemented capabilities. New gaps discovered in comparison return to the architect for bounded follow-up.

## UI structure / ASCII design contract

Every new or revised Woo UI task includes a source-derived `## ASCII Page Design` section. It specifies the **page shell, positioning, major cards, controls, actions, navigation and relevant loading/empty/error/disabled states**. Fixed-width ASCII is a reviewable layout contract, not pixel-level CSS and **not permission to invent domain data or functionality**. Keep each section with its Shopify analogue: Feature Preferences and Merchant Knowledge are sections of Recovery Settings; Promotions are recovery-credit promotions, not provider coupons.

```text
WordPress Admin
  Moda Interact
    Overview ------------------ Recovery performance / capacity / pending
    Recoveries --------------- Filtered list -> Recovery detail
    Billing ------------------ Existing Billing + link to Usage History
    Promotions --------------- Promotional recovery credits
    Support ------------------ Merchant support inbox
    Recovery settings -------- Effective policy / controls
                                   |-- Feature preferences
                                   |-- Store category
                                   +-- Merchant Knowledge
```

A Woo UI task must split presentation, controller/state, data client and integration rather than introduce monolithic page.js or oversized component files. Prefer modules near 200 lines; no new production catch-all above 300 lines.

## Security, localisation, failure handling

- Use `manage_woocommerce`, WordPress REST nonce/capability and existing connected installation/credential rotation guards for any approved network operation.
- No direct browser-to-hosted Moda API, tenant-supplied shop identity, leaked secret/token or storing sensitive support/recovery data in browser persistence.
- WordPress administrator UI locale with site-language fallback, full parity across all 20 supported merchant UI locales; preserve saved store/customer-conversation languages.
- Accessible labels, keyboard/focus order, narrow viewport, translated/original message display and no duplicate submits or stale asynchronous results after disconnect.
- Use only explicitly approved read/write actions; all unavailable write/read capabilities have explicit merchant-facing disabled/failed states and test fixtures remain test-only.
- No new telemetry, new gateway resources or cross-service version publication is justified by UI-only scope. Existing failure/logging and security mechanisms remain in place.

## Rollout / verification

Current planned UI work is pre-production; no database migration is authorised. The relevant approved API endpoint must be available before its separate WooCommerce proxy/React integration is enabled. Existing WordPress ZIP build/install/upgrade and 20-language compilation remain required. The certification task validates **UI parity**, not Woo checkout/recovery lifecycle, provider offers or end-to-end payment/refund workflows. Do not claim real feature certification from component fixtures.

For each UI implementation task, the repository agent runs the declared automated JS/PHP tests, `npm run test:i18n`, `npm run i18n:verify:20`, `npm run build`, `npm run plugin-zip`, and `git diff --check` as applicable. **LocalWP startup, installation/connection, interactive merchant-admin checks, viewport/keyboard review and LocalWP screenshots are exclusively developer-owned manual validation.** Repository agents and `moda_system_test` must not be assigned to run or inspect a live LocalWP session; they may use repeatable automated WordPress fixtures/browser tests and review evidence that the developer voluntarily supplies. Developer LocalWP validation is a separate checkpoint, not a required Work Item or Validation check for an agent task to enter `review` or be architect-accepted. The developer may perform it after implementation acceptance and before invoking Ready terminal system tests. Record missing manual evidence as `developer validation pending`, not as a failed agent test or proof of successful manual validation.

## Reconciled active task plan — 16 October 2026

| Task | Owner | Implementation status | Dependencies | Next action |
|---|---|---|---|---|
| `API-002` | moda_api | Complete | — | No further ARCH-035 implementation required |
| `API-009` | moda_api | Complete (retrospective developer closure) | — | Preserve source-based review evidence |
| `API-013` | moda_api | Complete (retrospective developer closure) | API-009 | Preserve source-based review evidence |
| `WOOCOMMERCE-012` | moda_woocommerce | Complete | — | Preserve native two-stage navigation |
| `WOOCOMMERCE-002` | moda_woocommerce | Complete | — | Recovery policy stage delivered |
| `WOOCOMMERCE-001` | moda_woocommerce | Ready | WOOCOMMERCE-012 | Build Support UI |
| `WOOCOMMERCE-003` | moda_woocommerce | Ready | WOOCOMMERCE-002 | Build feature controls |
| `WOOCOMMERCE-004` | moda_woocommerce | Pending | WOOCOMMERCE-003 | Build Merchant Knowledge UI after 003 |
| `WOOCOMMERCE-005` | moda_woocommerce | Ready | WOOCOMMERCE-012 | Build Promotions credits UI |
| `WOOCOMMERCE-006` | moda_woocommerce | Ready | WOOCOMMERCE-012 | Build Usage History UI |
| `WOOCOMMERCE-009` | moda_woocommerce | Complete | WOOCOMMERCE-012 | Recoveries list delivered |
| `WOOCOMMERCE-013` | moda_woocommerce | Complete | WOOCOMMERCE-009 | Recovery detail delivered |
| `WOOCOMMERCE-010` | moda_woocommerce | Pending | WOOCOMMERCE-006, WOOCOMMERCE-013 | Build recovery analytics Overview after 006 |
| `WOOCOMMERCE-011` | moda_woocommerce | Complete | — | Local coupon preview only; do not assert send-time offer |
| `SYSTEM-TEST-001` | moda_system_test | Pending | All ten required merchant UI tasks | Certify when UI tasks Complete |

Individual task YAML frontmatter remains authoritative. These states are reconciled against the available source; historical developer-mode task materialisation and developer completion are not invented. Existing superseded tasks remain superseded. Do not update domain `_index.md` until the developer explicitly closes this architecture reconciliation session.

## Superseded definitions (not executable)

The original ARCH-035 plan also contained 23 non-UI task definitions; **API-009 and API-002 are now explicitly re-scoped and reactivated**, leaving 21 superseded task definitions. These are retained for history with `status: superseded`, not silently deleted or reassigned:

- API-001, API-003..008 and API-010..012 (10): other hosted merchant APIs, Woo activity and coupon interfaces. API-009 is an active list-read task and API-002 is the narrowly approved recovery-policy read/write task.
- DATABASE-001..002 (2): checkout activity / Woo offer persistence.
- BACKGROUND-001..003 (3): checkout/order/recovery processing and offers.
- SHARED-001 (1): Woo commerce activity contract.
- WOOCOMMERCE-007, -008, -011 (3): checkout/order event producers and coupon selection.
- SYSTEM-TEST-002 and -003 (2): backend checkout/order/offer certification.

Superseded task IDs must not be repurposed for unrelated UI changes. Their former dependencies are absent from all active tasks. This does **not** certify that the underlying functionality is implemented or unnecessary for eventual functional parity.

## Dependency graph

```text
WOOCOMMERCE-012 (navigation) ----+----> 001 Support
                                 +----> 005 Promotions
                                 +----> 006 Usage History -----+
                                 +----> 009 Recoveries list    |
                                             |                 |
                                             v                 |
                                         013 Detail ------------+--> 010 Overview

API-002 (policy read/write) ---> WOOCOMMERCE-002 (policy Stage 3 integration)
                                            |
                                            v
    003 Feature controls
          |
          v
    004 Merchant Knowledge

API-009 (existing-data list read) ---> Woo Recoveries list integration
    |
    v
API-013 (detail/messages/related reads) ---> future Woo Recovery Detail integration

All ten Woo UI tasks ---------------------------> SYSTEM-TEST-001
```

The ordering minimizes file conflicts while leaving independent surfaces parallel. A task becomes Ready only when its actual declared dependencies are architect-accepted `complete`.

## Open issues to report, not implement in ARCH-035

- Which requested merchant read/mutation operations are actually exposed through existing approved Woo PHP plugin / hosted API calls. The current plugin does not expose the full set of Shopify-equivalent data/actions.
- Whether the existing Woo Overview can retrieve authoritative recovery performance, pending recoveries and currency values without new hosted API support. Until verified show unavailable instead of fake zero.
- Whether server-side support message send/read and Knowledge/Promotions/feature writes exist as approved public Woo endpoints. Until verified disable actions and report integration gaps.

## Architecture change history

- **2026-10-11 original:** mixed Woo merchant UI and checkout/order/offer recovery lifecycle, 32 task definitions.
- **2026-10-11 UI-only scope decision:** user limited work to merchant UI and required ASCII page designs. Backend tasks superseded; 10 bounded Woo UI tasks (two new task IDs) and one terminal UI test; no `_index.md` changed.

- **2026-10-11 staged Recoveries agreement:** developer approved responsive UI shell, authorised API-009 as existing-data read only with server-side page/pageSize/total/totalPages and date/customer/status filters. Reopened/re-scoped API-009; no new tables, Background work or `_index.md` changes. Stage 3 remains a separate future integration task.

- **2026-10-12 detail read approval:** developer requested Stage 2 after the responsive Recovery Detail shell. Added API-013 as a bounded Woo Shop-authenticated read-only detail/messaging/related endpoint with independent cursor pagination. No database, Background, Shopify or `_index.md` work.

- **2026-10-12 Recovery Behaviour API exception:** developer approved API-002 after reviewing the Woo Recovery Settings preview. Read/PUT are restricted to existing `ShopSettings` delay/follow-up columns; `ShopRecoveryPolicyOverride` is read-only, no Woo coupon selection, no migrations, and the saved/effective policy are returned separately with revision protection. WOOCOMMERCE-002 remains a separate Stage 3 integration.

## 2026-10-19 Developer-authorised API closure

The developer has requested a documentation patch closing API-009 followed by API-013 under the previously accepted source-based reconciliation. This does not certify unrun checks or the overall architecture.
