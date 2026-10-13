---
id: ARCH-036-BACKGROUND-001
architecture_id: ARCH-036
title: "Schedule and reconcile WooCommerce coupon catalogues by Background pull"
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on: ["ARCH-026-API-007", "ARCH-036-DATABASE-003"]
enables: ["ARCH-036-API-002", "ARCH-036-ADMIN-001", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-13
---
# ARCH-036-BACKGROUND-001 — Schedule and reconcile WooCommerce coupon catalogues

## Architecture

- Parent: `ARCH-036` — `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`; implementation owner: `moda_background`, repository `moda-interact-background`.
- Materialised on the canonical parent task branch. This developer reopen is not an execution claim; the declared dependencies must be complete before an implementation attempt can be prepared.
- This definition supersedes the earlier **per-shop recurring-scheduler** and **global BullMQ Job Scheduler** proposals. It reuses **one PostgreSQL global runtime lease** (`WOO_COUPON_SYNC_DISPATCH`) through the existing `startDynamicLeasedScheduler()` / `BackgroundRuntimeLeaseService`, with independent one-off shop jobs and per-shop catalogue fencing. The design must not create recurring BullMQ Job Schedulers per shop or for global dispatch.

## Objective

Automatically discover connected WooCommerce shops, register each in the existing discount-catalogue table regardless of whether a Woo read grant exists, dispatch bounded batches of shops due for refresh under **one existing-style PostgreSQL global lease**, and safely synchronise complete, paginated, read-only WooCommerce coupon catalogues into existing PostgreSQL rows while preserving merchant checkbox selections.

## Context

The five in-session ARCH-036 implementation tasks consist of the prerequisite `DATABASE-003` lease-enum migration plus Woo coupon synchronisation, API configuration, Woo merchant UI and internal Admin visibility. CommerceAgent, outbound recovery, coupon redemption and Shopify behaviour are **out of scope**.

Inspected snapshot evidence:

- `moda-interact-database/prisma/schema.prisma` already defines `Shop` (including `platform`, `status`), `WooCommerceInstallation`, `WooCommerceRestReadGrant`, `ShopifyDiscountCatalogue` and `ShopifyDiscount`. `ShopifyDiscountCatalogue.shopId` is unique; the catalogue has `status`, `syncGeneration`, `activeSyncToken`, `syncRequestedAt`, `syncStartedAt`, `lastSuccessfulSyncAt`, `lastErrorAt`, `lastErrorCode` and `unavailableAt`.
- `moda-interact-background/src/entrypoints/recovery.ts` starts the existing recovery workers, Shopify discount sync worker and scheduler/telemetry. `src/workers/shopify-discount-sync.worker.ts` illustrates a BullMQ worker; `src/services/shopify-discount-catalogue.service.ts` illustrates per-shop row locking and generation/fencing, **but must not be reused without removing its Shopify-specific availability writes/eligibility logic**.
- `src/runtime/dynamic-leased-scheduler.ts` and `src/runtime/background-runtime-lease.ts` implement the approved fleet-wide scheduler using `BackgroundRuntimeLease` (`ownerToken`, `generation`, `leaseUntil`, `lastFinishedAt`, heartbeat/release). `DATABASE-003` adds the missing `BackgroundRuntimeLeaseName.WOO_COUPON_SYNC_DISPATCH` enum member. Background must add the corresponding 60-second branch to the existing `CASE` cadence mapping in `tryAcquire()` and register `startDynamicLeasedScheduler()` in the recovery entrypoint. There is no BullMQ recurring dispatcher job. `BackgroundRuntimeConfig` needs no new column.
- API-owned credential format is implemented in `moda-interact-api/src/woocommerce/rest-read/envelope.ts`. API's read-only provider transport/security precedent is in `.../rest-read/credential-verifier.ts`; implementation must not import private API source at runtime.
- `moda-interact-api/src/woocommerce/installation/connection-service.ts` creates a Woo `Shop` and `WooCommerceInstallation` but does **not** currently create a `ShopifyDiscountCatalogue` row. Background must therefore idempotently **bootstrap missing catalogue rows** from Woo installations on its dispatcher scan. This is eventual registration after installation, not a claim that the API installation transaction already creates the row. Missing read permission is **never** a reason to omit that row.

## Scope

Only `moda-interact-background` runtime, tests and local configuration/documentation required for this bounded capability:

1. One globally leased PostgreSQL coupon dispatcher using the existing dynamic scheduler and the `WOO_COUPON_SYNC_DISPATCH` enum member from `DATABASE-003` (proposed 60-second cadence).
2. Bounded PostgreSQL discovery/bootstrap and due-shop dispatch (proposed maximum 500 jobs per tick); one transient BullMQ job per due shop; **no recurring schedule per shop**.
3. Shop-scoped claim/timeout/retry/fencing using existing catalogue fields.
4. Worker-time Woo installation/grant verification and API-007-compatible AES-GCM decryption.
5. SSRF-safe, authenticated `GET /wp-json/wc/v3/coupons` with complete bounded pagination, normalisation and fenced reconciliation of Woo rows only.
6. Focused validation and operational signals demonstrating fair dispatch, recovery, tenant isolation and preservation of merchant selections.

## Out of Scope

- No Prisma schema/migration edits **in Background** (the single approved lease-enum migration belongs to `DATABASE-003`), new catalogue table/column/index, Shared package/contract, API proxy, Woo PHP hook or webhook, plugin-side coupon uploader, BullMQ recurring Job Scheduler, new process/deployment or new generic queue framework.
- No changes to Shopify's existing discount service or meaning of `ShopifyDiscount.isAvailable` on Shopify shops.
- No merchant checkbox writes, `ShopSettings` offer-mode writes, CommerceAgent/tool changes, recovery scheduling/outreach, coupon proof at send time, coupon creation/modification/deletion at WooCommerce, customer eligibility promises or redemption.
- Do not modify another repository or introduce new key storage/authentication mechanisms to solve a missing API-007 prerequisite; report architectural gaps to `moda_architect`.

## Requirements

### A. One dispatcher, installation discovery and scheduling

1. **Single global PostgreSQL lease:** use the existing `startDynamicLeasedScheduler({ config: backgroundRuntimeConfigService, lease: backgroundRuntimeLeaseService, leaseName: "WOO_COUPON_SYNC_DISPATCH", intervalMs: 60_000, runImmediately: true, run, onError })` pattern in `src/entrypoints/recovery.ts`. Each Background replica may maintain its existing local timer, but `BackgroundRuntimeLease.name` is the **same single enum value** across every replica, so only the successful holder dispatches per cycle. Reuse the existing owner-token/generation, 120-second lease, 30-second heartbeat and release/last-finished flow; do not create another lease table, Redis global lock, per-shop periodic scheduler or BullMQ Job Scheduler. Ensure graceful stop and readiness/telemetry parity with adjacent Background schedulers. `DATABASE-003` must be migrated and the Prisma client regenerated before runtime registration.
2. **Cadence and lease SQL:** add `WHEN 'WOO_COUPON_SYNC_DISPATCH'::"BackgroundRuntimeLeaseName" THEN 60` to `src/runtime/background-runtime-lease.ts` inside the existing `runtime_config` `CASE` used by `tryAcquire()`. This **must** match `intervalMs: 60_000` at scheduler registration. The persisted cadence is enforced from `BackgroundRuntimeLease.lastFinishedAt` following each completed cycle; local wakeups can be skipped, and completion-relative cadence plus scheduling/queue lag means a precise wall-clock tick is **not guaranteed**. The 30-minute per-shop refresh remains a separate target, not one global dispatch every 30 minutes. Fix the global lease cadence at 60 seconds for this task; keep batch size (proposed 500), per-shop refresh, cooldown, worker concurrency and provider limits configurable through validated Background settings without adding `BackgroundRuntimeConfig` columns or admin controls. If a variable global cadence is later required, it needs an explicitly agreed SQL/runtime-config change; do not configure a local interval inconsistent with the database `CASE`.
3. **Discovery/bootstrap:** in bounded keyset pages, read `Shop` joined with `WooCommerceInstallation`; find genuinely connected `platform=WOOCOMMERCE` shops, with active installation/Shop. `INSERT ... ON CONFLICT DO NOTHING` / Prisma `upsert` a `ShopifyDiscountCatalogue` row when absent, initially `SYNC_REQUIRED` with `lastSuccessfulSyncAt=NULL`; **do not filter discovery by grant**. Do not touch Shopify catalogue rows. Treat inactive/disconnected shops as not dispatchable but preserve their historical catalogue/selection records. Newly connected shops are discovered on the next tick without needing a new Woo plugin/API write.
4. **Due selection:** scan catalogue/installation identities using bounded pages and indexed keyset (`shopId`), avoiding a full unbounded result or an N+1 query. Eligible cases: never successfully synced; CURRENT but refresh interval elapsed (with deterministic per-shop spreading/jitter); ERROR/UNAVAILABLE after retry cooldown; stale queued/SYNCING claims eligible for recovery. Do not requeue every minute only because `lastSuccessfulSyncAt` is NULL. Check current Shop/installation eligibility here for waste avoidance, **but check grant only inside the shop worker** so granting read access later needs no new registration event.
5. **Fairness and scale:** rotate the catalogue scan cursor or otherwise ensure that a sustained backlog cannot indefinitely starve shops after the first batch. Limit each cycle by a configured dispatch budget (proposed 500), database page size and total runtime. Record scanned/due/claimed/enqueued/skipped counts, oldest due age and backlog. The number of shops used in planning discussions is illustrative, not an acceptance benchmark. Size worker concurrency and network budgets based on operational needs and available evidence; do not claim a production refresh-time guarantee from enqueue counts alone.
6. **Dispatch race and Redis failure:** the global lease serialises dispatch cycles across healthy replicas but does **not** replace per-shop claims or make PostgreSQL and Redis atomic. Claim due catalogue rows using current `status`, `syncRequestedAt`, `syncStartedAt` and relevant timestamps (compare-and-set/row lock), **commit the short PostgreSQL operation before BullMQ publication**, then enqueue a **one-off** deterministic bounded `jobId` derived from shop and that claim's timestamp/identity. Do not hold a DB transaction while publishing to Redis. If publication fails, the dispatcher crashes between claim and enqueue, or a job is lost, a bounded dispatch timeout makes the row due again; replayed jobs are harmless. Do not use the global lease or BullMQ job deduplication as the only protection against same-shop concurrent processing.
7. **Dispatcher failover and lease loss:** on process crash, heartbeats cease; after `leaseUntil` expires another replica may acquire the same enum-name lease with a higher generation. The existing `runWithLease()` reports `leaseLost` but does not automatically interrupt an in-flight callback. The dispatcher must stop further dispatch on shutdown/ownership loss where it can observe it, bound cycle duration to be comfortably less than lease duration where practical, and rely on atomic shop claims/idempotent jobs to prevent stale overlapping dispatcher callbacks from causing duplicate shop work. A failed callback still releases its valid lease and records `lastFinishedAt`; the next eligible cycle follows database cadence. Test two replicas, healthy exclusivity, heartbeat, expiry/takeover, callback failure, and stale owner overlap. Queue workers remain independent after the dispatcher lease is released.

### B. Queue job and per-shop worker

8. Use one local Background BullMQ queue, e.g. `woo-coupon-sync`, for **one-off** `sync-woo-coupons` jobs only; the **only business identifier** is internal `shopId` (optionally a bounded dispatch-claim token). The PostgreSQL-leased dispatcher callback calls the dispatch service directly; it does **not** publish a recurring dispatcher job. Parse/validate payloads at the worker boundary. Retries/backoff and retention must be bounded; successful jobs must not permanently block future dispatch IDs. Reject malformed payloads. Avoid logging provider URLs, consumer keys/secrets or raw responses.
9. Use shared workers with configurable concurrency; individual shop calls execute in parallel, limited globally and (where justified) by per-store/provider rate limits. Do not attach a worker/process to each shop. Ensure a blocked or slow merchant cannot monopolise the entire worker fleet; apply request deadlines, capped per-job duration and fair queue/backoff.
10. On each shop job: load `Shop` -> `WooCommerceInstallation` -> `WooCommerceRestReadGrant` **at execution time** (not just when the dispatcher ran). Require active Woo Shop and installation, matching `shopId`, verified canonical origin, non-revoked, current credential version, ACTIVE grant, exact `authorizedScope='read'` and matching installation/authorisation attempt. If grant is missing/revoked/unusable, **skip without contacting WooCommerce**, record `UNAVAILABLE` with a bounded reason (for example `WOO_READ_GRANT_MISSING`) and attempt/cooldown metadata; preserve successful timestamp, existing coupons and selections. The next scheduled attempt checks again so permission granted later automatically unblocks sync. Transient network failures are `ERROR` rather than proof of revocation. Recheck current grant/installation before committing provider observations.
11. Acquire a **single shop's** catalogue lock and new `syncGeneration`/`activeSyncToken` before network I/O; enforce one live claimant per shop. A second job skips an unexpired existing claim. Store `SYNCING`/`syncStartedAt` atomically. On stale takeover, increment generation and replace token only after an explicit, bounded expiry. On final commit/error, compare the token **and generation** to prevent an older worker changing state after takeover. Never hold a database lock/transaction while fetching Woo pages. A provider failure must clear only the matching current claim, not a successor's claim.

### C. Exact WooCommerce request and paginated fetch

12. Resolve `WooCommerceInstallation.canonicalSiteUrl` using the approved API canonicalisation rules. Construct the request **from trusted components**, not a merchant-supplied URL/path. Preserve an approved canonical subdirectory/base path if supported by the verified site; append only the fixed Woo REST path. Public deployments require HTTPS, valid TLS hostname/certificate, DNS-resolved public destinations, peer pinning/validation and **no redirect following**. Apply the same safety model as the API's `WooReadCredentialVerifier`; a naive `fetch(new URL(merchantUrl))` without DNS/peer protections is unacceptable. LocalWP/non-public HTTP is permitted only in the existing explicit local-development mode using the approved request signing protocol, not Basic credentials over plaintext. Avoid duplicate generic SSRF/security frameworks where existing reusable primitives can be adopted safely.
13. **GET request example (illustrative, secrets intentionally omitted):**

    ```http
    GET /wp-json/wc/v3/coupons?page=1&per_page=100&orderby=id&order=asc HTTP/1.1
    Host: merchant.example
    Accept: application/json
    Authorization: Basic <base64(consumerKey:consumerSecret)>
    ```

    Only use HTTP Basic over verified HTTPS. In code, use `URL` + `searchParams.set` with fixed `page`, `per_page`, `orderby=id`, `order=asc` values, not string-concatenated user input. **Never** put `consumer_key` or `consumer_secret` in query parameters, logs or queue jobs. Set `Accept: application/json`, controlled `Accept-Encoding` and bounded body processing. No `POST`, `PUT`, `DELETE` or arbitrary Woo REST endpoints in this task.
14. Obtain the Woo credential from `WooCommerceRestReadGrant` (`credentialCiphertext`, `credentialNonce`, `credentialAuthTag`, `encryptionKeyId`, `authorizationAttemptId`, `credentialVersionSnapshot`). The API's actual AES-256-GCM AAD is UTF-8 JSON array `['moda-woo-rest-read-v1', shopId, installationId, authorizationAttemptId, credentialVersionSnapshot]`; its plaintext is JSON array `[consumerKey, consumerSecret]`. Use the API-owned keyring configuration contract (`MODA_WOO_REST_READ_KEYRING` key IDs/base64url, configured privately for Background) and an audited Background AES-GCM primitive **only if it can decrypt this exact envelope without imposing a different format**. Prove API-sealed → Background-opened parity and rejection for wrong key/AAD/shop/installation/attempt/version. Do not invent a plaintext fallback or import private API code across repository boundaries. Clear/bound in-memory secrets where practical.
15. **Pagination sequence:** start at `page=1`, `per_page=100` (Woo's documented maximum), `orderby=id`, `order=asc`. Read and strictly parse `X-WP-Total` and `X-WP-TotalPages` from the first response; both must be bounded non-negative integers and consistent with returned count. For `p=2..totalPages`, independently construct the same approved URL with `page=p`, perform one GET, and enforce per-page size, sorted monotonic unique positive numeric coupon IDs, stable page-count/total evidence, valid JSON arrays and response content-type. Never blindly follow an untrusted `Link` URL. Distinguish a **verified empty list** (`X-WP-Total: 0`, zero coupons on page 1, provider-consistent page count) from a missing page or failed request. Reject missing, contradictory or unstable pagination evidence and retry the **entire scan**; do not mark the catalogue CURRENT on a partial scan.
16. Bound the total number of pages/coupons, per-response bytes, total scan bytes, DNS/connection/response time, total scan deadline and transport retry count. Suggested initial safety limits: 100 items/page, at most 200 pages (20,000 coupons/shop), 10 seconds/request and 120 seconds/scan; these are **proposals requiring measurement** and must fail closed with a reason when exceeded, not silently truncate a catalogue. Use bounded exponential backoff with jitter for 429/5xx/timeouts and honour safe `Retry-After` values. Treat 401/403 as possible expired/insufficient credentials, not as an empty catalogue. Never perform a network request inside a PostgreSQL transaction.
17. **Concurrent Woo edits during page-number scans:** `orderby=id` stabilises ordering but does **not** provide a provider snapshot. Check repeated total/page evidence, ID uniqueness and expected total across the assembled result; if changes make the scan inconsistent, fail/retry. To avoid false deletion on an otherwise apparently complete scan during a concurrent update, require **two consecutive verified complete generations missing the same previously observed ID** before marking a coupon removed (use `lastSeenSyncGeneration`; no new state table). A later reappearing coupon updates its existing row. A missing page or any failed generation never counts as a confirmation.

### D. Existing PostgreSQL models and writes

18. **Tables read:** `commerce.Shop` (internal shop ID, `platform=WOOCOMMERCE`, `status`, domain), `woocommerce.WooCommerceInstallation` (shopId, installation ID, canonicalSiteUrl, status, revocation, credentialVersion), `woocommerce.WooCommerceRestReadGrant` (grant state, authorised scope, encrypted fields, attempt/version/rotation), `shopify.ShopifyDiscountCatalogue` (per-shop sync status/claim), and existing `shopify.ShopifyDiscount` (previous rows, generation and selection). Read `WooCommerceRestReadAttempt` only if needed to prove the authorised attempt is still current; do not change attempts. Read no Shopify session/scope/subscription records to determine Woo read permission.
19. **Tables written:** `shopify.ShopifyDiscountCatalogue` and `shopify.ShopifyDiscount` **for Woo shops only**. Bootstrap catalogue rows, dispatch/worker claims, committed current generation, success/error status and existing provider row projections. This Background task does **not** write merchant `ShopSettings`, `ShopRecoveryPolicyOverride`, `WooCommerceRestReadGrant`, installation credentials, billing state or Shopify rows.
20. **Stable coupon identity:** write `ShopifyDiscount.shopifyDiscountNodeId = 'woo:coupon:' + positiveWooCouponId` and unique `(shopId, shopifyDiscountNodeId)`. Use existing required fields: `providerType` from `discount_type`, `method=CODE`, `title`/`singleRedeemCode` from real `code`, `summary` from bounded description, `providerStatus`, `fixedSelectable`, dates (`startsAt`/`endsAt`), `providerSnapshot` and generation/timestamps. Convert `amount` as a bounded **decimal string**, never floating-point currency math; preserve supported limits/restrictions in a bounded allowlisted JSON projection (e.g. individual use, limits/count, permitted products/categories, minimum/maximum amounts, expiry, free shipping). Do **not** persist unneeded personal data such as raw `used_by` or customer emails or raw provider payloads. Unknown/unsupported coupon types or ambiguous time/eligibility semantics must be kept provider-visible but `fixedSelectable=false` (fail closed), not silently declared usable.
21. **Selection isolation:** `ShopifyDiscount.isAvailable` means **merchant checkbox selection for Woo only**. New Woo coupon rows start `false`. On Woo upserts, **omit `isAvailable` from updates** and do not clear it for expired/removed/unavailable coupons. Provider eligibility lives in `providerStatus`, `fixedSelectable`, `endsAt`, `unavailableAt` and current catalogue state. Preserve existing discount IDs/rows referenced by settings/audit/history; do not delete. Shopify's `isAvailable` remains provider availability and Shopify synchronisation is unchanged.
22. **Commit only complete generations:** after successful validation and a current-grant recheck, atomically upsert all bounded observed Woo records, set lastSeen generation/current metadata and mark catalogue CURRENT/`lastSuccessfulSyncAt` while verifying the live fencing token. Rows absent from a **confirmed** provider scan become unavailable only after the safe missing-generation rule in item 17; do not treat provider timeout, incomplete pages, missing grant or stale token as deletion. A true verified zero-coupon store is allowed to become CURRENT with no observed coupon rows and the same conservative missing-row treatment.
23. **Failure semantics:** no grant → `UNAVAILABLE` plus bounded reason; invalid/mismatched ciphertext/config → `UNAVAILABLE` or explicit blocked operational failure, no fallback; timeouts/429/5xx/bad pages → `ERROR` and retry cooldown; stale fencing token → `superseded` without writes. Preserve `lastSuccessfulSyncAt` and existing selected flags in all failure paths. On revocation/installation inactivity, cancel provider reads for that attempt, preserve history and let future eligible scans recover after access is restored.

### E. Operations and protection

24. Use `@modainteract/moda-interact-shared/logging` for new structured events, e.g. `woo.coupon_dispatch.cycle`, `woo.coupon_sync.started`, `.skipped`, `.completed`, `.failed`; log bounded shop IDs, job IDs, generation, counts, duration and error **codes**, not raw error objects, URLs with tokens, Authorization headers, keyring material, coupon/customer payloads or credentials. Reuse existing BullMQ/OpenTelemetry metrics where they already express generic worker throughput/lag; add only genuinely domain-specific counters if a documented observability gap exists.
25. Operators must be able to distinguish never synced, waiting for permission, current, overdue, queued, in progress, failed, and stale/recoverable without false success claims. Document configured tick, per-shop interval, dispatch cap, worker concurrency, page limit, retry/cooldown, backlog/oldest age and deployment secret wiring. Logs/telemetry failures must never fail business state transitions. Ensure queue and scheduler resources are closed via the existing readiness/shutdown contract.

## Work Items

- [ ] Consume `DATABASE-003`'s generated Prisma `BackgroundRuntimeLeaseName.WOO_COUPON_SYNC_DISPATCH`; add the 60-second SQL cadence branch in `src/runtime/background-runtime-lease.ts` and register the existing `startDynamicLeasedScheduler()` in recovery startup/shutdown, with lease loss/error tests.
- [ ] Add the one-off Woo coupon queue, typed shop-job parser and worker; wire readiness and queue telemetry. **Do not register BullMQ recurring jobs.**
- [ ] Implement bounded installation-to-catalogue bootstrap, due-shop scanning with fairness, atomic dispatch claims, enqueuing and publication-loss recovery without requiring grant at registration.
- [ ] Implement worker-time current grant resolver/AES-GCM envelope parity, safe canonical Woo origin and transport, plus pagination with strict complete-scan evidence and bounds.
- [ ] Implement token/generation-fenced shop reconciliation and conservative verified-missing handling, preserving all Woo merchant selection flags and Shopify behaviour.
- [ ] Add focused unit/transport/PostgreSQL/queue tests for bounded due-shop batches, backlog fairness and failure recovery; document operational configuration and production-safe credential handling. A fixed 10,000-shop simulation or throughput benchmark is not required.

## Interfaces / Contracts

### Proposed files in `moda-interact-background` (create only where absent)

| Path | Ownership / intended implementation |
|---|---|
| `src/services/woo-coupon-dispatcher.service.ts` | Discover installation rows; bootstrap missing catalogue rows; scan due shops fairly; transactionally claim and enqueue bounded per-shop jobs; recover publication gaps. |
| `src/services/woo-coupon-sync.service.ts` | Shop claim/generation/fencing, grant checks, full-scan orchestration, transactional reconcile and error transitions. |
| `src/services/woo-coupon-grant.service.ts` | Read current Shop/installation/grant; validate active scope/version/identity; reconstruct API-007 AAD/decrypt and safely recheck rotation. |
| `src/providers/woo-coupon.provider.ts` | Canonical Woo REST GET builder, DNS/TLS/redirect/SSRF-safe transport, Basic-over-HTTPS or approved local-only auth, bounded full pagination. |
| `src/services/woo-coupon-normalization.service.ts` | Validate and normalise provider coupon records into the existing discount columns and allowlisted JSON snapshot; conservative supported-rule flags. |
| `src/workers/woo-coupon-sync.worker.ts` | Parse bounded dispatcher/shop job payloads, invoke the owning service, apply bounded retries/backoff, structured outcome logging. |
| `src/runtime/woo-coupon-sync-config.ts` | Validate bounded batch, **per-shop refresh** interval, concurrency, timeout, pagination and keyring configuration; the **global lease cadence is fixed at 60 seconds** and not configured independently of its SQL `CASE`. |
| `src/runtime/background-runtime-lease.ts` *(modify)* | Add `WOO_COUPON_SYNC_DISPATCH` -> 60-second cadence to the existing `tryAcquire()` SQL `CASE`; no new lease mechanism. |
| `src/runtime/dynamic-leased-scheduler.ts` *(reuse)* | Keep existing lease/heartbeat/timer/stop implementation; modify only if a demonstrated reusable correctness defect requires an explicitly reviewed correction. |
| `src/entrypoints/recovery.ts` *(modify)* | Register the global dynamic **PostgreSQL-leased** scheduler, wire its dispatcher callback and one-off shop-worker pool; add queue metrics and stop hooks. No BullMQ Job Scheduler. |
| `tests/unit/runtime/woo-coupon-dispatch-lease.test.ts` *(new; path adaptable)* | Verify the lease enum, 60-second SQL cadence mapping, multi-replica mutual exclusion, callback failure and stale takeover using existing service test conventions. |
| `tests/unit/services/woo-coupon-*.test.ts` and `tests/unit/workers/woo-coupon-*.test.ts` *(new)* | Dispatch fairness, grant, pagination, mapping, worker/lock/retry tests split by responsibility. |
| `tests/integration/woo-coupon-sync.integration.test.ts` *(new)* | Disposable PostgreSQL + Redis claims, generation fencing, cross-shop isolation, completion/retry recovery. |

Paths are proposed repository-relative implementation boundaries, not already existing files. Adapt test filenames only to match established repository conventions; do not collapse the implementation into a monolithic service. Local queue job shapes remain internal to Background; **no cross-service Shared package publication** is required.

### Provider request contract

- Canonical origin: `WooCommerceInstallation.canonicalSiteUrl` (and its approved base path), *never* a client-supplied origin in a queue message.
- Endpoint: `GET /wp-json/wc/v3/coupons`; query: `page=<1-based integer>&per_page=100&orderby=id&order=asc` (add only verified required fixed parameters).
- Auth: Woo read-only consumer key/secret from current API-007 grant; HTTPS Basic header; no secret query arguments; preserve the existing explicitly approved local-development auth mode.
- Pagination evidence: `X-WP-Total`, `X-WP-TotalPages`, per-page array, sorted unique positive IDs, response/header consistency and entire-scan reconciliation.
- Database lease owner: `DATABASE-003` adds the Prisma/PostgreSQL enum value; Background adds the SQL cadence and starts the existing leased scheduler. Lease type: `BackgroundRuntimeLeaseName.WOO_COUPON_SYNC_DISPATCH` (via generated `@prisma/client`).
- Producer/consumer: PostgreSQL-leased Background dispatcher callback → one-off Background BullMQ shop worker → Background provider/reconcile services. Queue payload contains only bounded internal identifiers.
- Reference for the API-owned wire/envelope definitions: `moda-interact-api/src/woocommerce/rest-read/{envelope,credential-verifier}.ts` in the supplied snapshot; these are **reference implementations, not package imports**.

## Dependencies

- `ARCH-026-API-007` — requires architect-accepted ACTIVE read-grant persistence, canonical Woo installation identity and the API-owned AEAD envelope/keyring. Background must fail closed if the prerequisite is not satisfied.
- `ARCH-036-DATABASE-003` — supplies the architect-accepted enum migration, generated Prisma lease name and a verified upgrade/fresh-database rehearsal before Background can register the global lease.

## Enables

- `ARCH-036-API-002`
- `ARCH-036-ADMIN-001`
- `ARCH-036-SYSTEM-TEST-001` (terminal, after all five in-session implementations are Complete).

## Acceptance Criteria

- [ ] Every connected Woo shop is eventually registered in `ShopifyDiscountCatalogue` by the global discovery path **even without a read grant**, and every later eligible job independently rechecks permission; grant changes require no per-shop scheduler registration.
- [ ] Exactly one **valid PostgreSQL lease holder** for `WOO_COUPON_SYNC_DISPATCH` dispatches on a given global cycle across Background replicas; there are **zero BullMQ recurring dispatcher schedules**. Dispatch can enqueue multiple due shop jobs, uses bounded queries/batches and cannot starve overdue shops or keep requeueing missing-grant shops each minute.
- [ ] The existing `BackgroundRuntimeLeaseService` SQL maps `WOO_COUPON_SYNC_DISPATCH` to 60 seconds, its local scheduler interval matches, and last-finished cadence, heartbeat/expiry/takeover and old-generation loss are exercised without creating another lease implementation.
- [ ] Demonstrate bounded discovery and due-shop dispatch, including fairness when more shops are due than fit in one batch. A 10,000-shop simulation, 5.56-scans/second benchmark and instrumented capacity proof are **not** acceptance criteria. Do not assert a measured production freshness guarantee without supporting evidence.
- [ ] A worker securely constructs and authenticates Woo coupons GET requests and fetches all bounded pages. Zero coupons is accepted only with complete consistent evidence. Missing pages, changed totals/duplicates/oversize/timeout never become CURRENT or mark coupons deleted.
- [ ] Provider reads use the **actual** encrypted API-007 read grant and shop/version/AAD/keyring parity; unauthorised, revoked, rotated, cross-shop, SSRF/redirect or stale-grant attempts fail closed without leaking keys.
- [ ] Per-shop claims prevent concurrent writes; crashed owners can be replaced, and stale tokens cannot overwrite newer generations. Redis dispatch loss or duplicate delivery does not strand or duplicate a shop indefinitely.
- [ ] Woo row updates preserve `isAvailable` on every existing row; new rows default `false`; expiry/removal changes provider eligibility only. Shopify provider availability and code paths are unchanged. Referenced historical rows are retained.
- [ ] Shop A outage cannot block Shop B, no cross-tenant coupon can be attached to another Shop, and Background modifies no API/Shared/Shopify/CommerceAgent/recovery code, Prisma schema or migration; the **only** approved ARCH-036 schema change is the `DATABASE-003` enum addition.

## Validation

- [ ] Unit tests: due/cooldown/fairness, bootstrap without grant, grant granted after initial skip, queue dedupe/dispatch publication gap, SQL lease cadence mapping, multi-replica exclusive lease acquisition, 120-second expiry/30-second heartbeat, last-finished gating, callback failure and stale-owner overlap.
- [ ] Provider tests: exact authenticated query and page construction, totals/headers, 0/1/100/101/200+ coupons, missing/duplicate/out-of-order pages, concurrent provider edits, limits, retry/429, wrong auth, redirects, DNS/peer/TLS protections and key/AAD parity with API-produced fixture.
- [ ] Disposable PostgreSQL + Redis integration (with `DATABASE-003` migration deployed): two competing dispatcher instances using one `BackgroundRuntimeLease` row, two Woo shops and a Shopify shop, bounded multi-batch due enumeration and starvation-prevention checks, initial/recurring sync, competing worker claims, expired claim takeover, stale writer fencing, selection preservation, missing-row confirmation and Redis publication failure/recovery.
- [ ] Run actual declared Background checks according to `moda-interact-background/package.json`: focused `npm test` / `npm run test:integration` where relevant; `npm run build` (includes Prisma generate); any repository-provided changed-file lint/type validation. No fabricated `npm run typecheck` or `npm run lint` scripts if missing. `git diff --check` required.
- [ ] Record the validated dispatch batch limit, refresh interval, retry cooldown, worker concurrency and page/deadline limits. Demonstrate bounded batches and fair re-selection from a backlog; do not require throughput, p95 latency or a fixed shop-count capacity benchmark. Do not claim production freshness or capacity as measured unless separately tested.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, fill the Completion Report, return the task at `status: review` and **STOP**. Do not begin dependent API/Woo/Admin work or any superseded task. For `execution_mode: developer`, final completion remains the developer's explicit action after review.

## Implementation Notes

- **Source-of-truth split:** PostgreSQL owns the **single global dispatcher lease** (`BackgroundRuntimeLease`), each shop's catalogue, freshness and fenced claim. Redis/BullMQ carries **one-off shop work only**. Neither a Redis-only lease nor a recurring BullMQ schedule is the source of global dispatcher ownership or business state.
- **Migration ownership:** `ARCH-036-DATABASE-003` is the sole owner of adding `WOO_COUPON_SYNC_DISPATCH` to Prisma/PostgreSQL. BACKGROUND-001 depends on its **accepted, applied** migration and owns only `background-runtime-lease.ts`'s enum-specific SQL cadence plus `recovery.ts` registration. No catalogue columns, due-time index, `BackgroundRuntimeConfig` fields, migrations or new tables are approved. If capacity evidence later requires extra indexes, raise a separately reviewed database task.
- **Registration vs permission:** Background bootstrap creates the catalogue row based on installation presence; the worker alone checks current read grant on each attempt. A missing grant results in a non-terminal skip/cooldown, not permanent exclusion.
- **Eligibility vs merchant selection:** any coupon may be visible in the catalogue even if not selectable. `isAvailable` is reserved for Woo merchant checkbox persistence by `API-002` and may be `true` even when provider status later makes the coupon ineligible. Never reinterpret Shopify rows this way.
- **Security:** do not use a generic HTTP client that automatically follows redirects or embeds Basic credentials in URLs; test actual DNS-pin and TLS-peer behaviour. A healthy LocalWP test cannot stand in for required production-safe transport evidence.
- **Task isolation:** agent/developer execution must use launcher-resolved dedicated worktrees in the real workspace and record start-of-attempt synchronisation/submodule evidence. Do not claim a branch, commit or push based on this portable snapshot.

## Completion Report

### Status

Changes Requested after developer self-review of attempt 2.

### Attempt 2 Preparation

- Claim: developer attempt 2, recorded at `2026-10-13T20:34:04Z`; the prior attempt remains recorded as Changes Requested.
- Dependencies: `ARCH-026-API-007` and `ARCH-036-DATABASE-003` both resolve as `complete`.
- Physical worktree isolation: canonical workspace root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-036-BACKGROUND-001` on `task/ARCH-036-BACKGROUND-001`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-BACKGROUND-001` on `task/ARCH-036-BACKGROUND-001`. The shared workspace and shared implementation checkouts were not switched or modified for task work; no other task worktree was reused.
- Start-of-attempt synchronization: parent remote task branch fast-forward was not needed; parent `origin/main` was already incorporated. Implementation remote task branch fast-forward was not needed; implementation `origin/main` was already incorporated. Both task branches were clean and aligned with their published upstreams before claim.
- Recursive implementation submodules were initialized and verified at their recorded gitlinks; the `database` submodule is clean at `33b42ece85b042230863a1c04d05d7d4383800a2`.
- The implementation task branch already contains published correction commit `c36bc5691b6fbf5eccba26bcb6e9b670e960adbd`; its corrections and validation evidence will be reviewed during this attempt. No implementation files were changed by this claim.

### Files Changed

Implementation task branch commit `f51cb9a` changes:

- `database` (submodule pointer)
- `package.json`
- `src/entrypoints/recovery.ts`
- `src/observability/queue-performance.ts`
- `src/providers/woo-coupon-local-oauth.ts`
- `src/providers/woo-coupon-pages.ts`
- `src/runtime/background-runtime-lease.ts`
- `src/security/aes-gcm-credential.ts`
- `src/services/woo-coupon-dispatcher.service.ts`
- `src/services/woo-coupon-grant.service.ts`
- `src/services/woo-coupon-reader.service.ts`
- `src/workers/woo-coupon-sync.worker.ts`
- `tests/integration/woo-coupon-dispatch-worker.integration.test.ts`
- `tests/unit/observability/queue-performance.test.ts`
- `tests/unit/providers/woo-coupon-pages.test.ts`
- `tests/unit/providers/woo-coupon-transport.test.ts`
- `tests/unit/runtime/background-runtime-lease.test.ts`
- `tests/unit/runtime/recovery-entrypoint.woo-coupons.test.ts`
- `tests/unit/security/aes-gcm-credential.test.ts`
- `tests/unit/services/woo-coupon-dispatcher.service.test.ts`
- `tests/unit/services/woo-coupon-grant.service.test.ts`
- `tests/unit/workers/woo-coupon-sync.worker.test.ts`

### Work Completed

Attempt 1 adds a PostgreSQL-leased recovery dispatcher, a one-off BullMQ coupon worker, grant decryption/revalidation, bounded Woo coupon-page transport and normalization, fenced catalogue writes, and focused unit/integration coverage. The source commit is `f51cb9a`; it is one commit ahead of the implementation task remote and is not published. No merge to `main` occurred.

### Validation Results

Passed focused Woo coupon unit tests: 6 files, 30 tests, 0 failures.

`npm run build` generated Prisma Client but TypeScript failed at `src/entrypoints/recovery.ts` because `"WOO_COUPON_SYNC_DISPATCH"` is not a member of the generated `BackgroundRuntimeLeaseName` enum. At build time the nested `database` checkout was `b9cb77a74c5fffa250dc65ed34de23113738d8e8`. Commit `f51cb9a` records database gitlink `8936f3b76a5e7f988c477032397de55de2b369de`, while its `origin/main` base records `b9cb77a74c5fffa250dc65ed34de23113738d8e8`. After the integration run, the nested checkout is `main` at `33b42ec` and remains modified relative to the task commit. Do not stage or publish this Background-owned gitlink change as-is. The task must consume the accepted DATABASE-003 enum revision without authoring a Background schema/migration change.

`npm run test:arch036-woo-coupon-dispatch:postgres` exercised dispatch, worker execution and the initial coupon write, then failed in test cleanup because the same generated Prisma enum rejects `WOO_COUPON_SYNC_DISPATCH`. Therefore this integration run is not a pass. Full `npm test` and `npm run test:integration` were not run. `git diff --check` on the task record passed before this review update.

The source review found that `WooCouponCatalogueService` immediately marks every previously observed coupon absent from one successful scan as `REMOVED`. The task requires two consecutive verified complete generations missing that coupon before removal. The committed test suite has no multi-generation missing-coupon proof, 10,000-shop capacity simulation/throughput measurement, or task-specific competing-dispatcher/lease-expiry/stale-owner integration proof. Those acceptance items remain unverified.

### Deviations

The implementation commit changes the `database` submodule pointer outside this task's schema ownership. The build and integration both used a generated client missing the required lease enum. The nested checkout is now on its `main` branch and differs from the gitlink recorded by `f51cb9a`; preserve that state until the developer resolves it under the dependency workflow. The implementation commit has not been pushed to the implementation task remote. No source history was rewritten.

### Assumptions

The developer will supply a runnable canonical workspace; observed deployment throughput and transport connectivity are not yet measured.

### Unresolved Issues

Build and the dispatch PostgreSQL integration are blocked by the missing generated Prisma enum. Coupon removal does not meet the two-consecutive-complete-scan safety rule. Required scale and lease failover evidence is missing. The implementation task branch has an unpublished commit and a modified `database` submodule checkout on `main` at `33b42ec`.

### Architectural Concerns

If the actual deployment needs due-time indexes, additional database lease fields, cross-service encryption contract publication or gateway/environment changes, return the gap to `moda_architect` before editing another repository. The required enum value is already owned by `DATABASE-003`.

## Architect Review

### Review Status

Pending.

### Review Notes

Attempt 9: replace global BullMQ Job Scheduler with the existing PostgreSQL global lease; depend on new `DATABASE-003` enum-only migration. Documentation definition only; no implementation or claim. The in-session plan now has five implementation tasks (including DATABASE-003), with CommerceAgent/recovery/Shopify behaviour excluded.

### Reviewed Files

Architectural task and inspected snapshot implementation cited above.

### Validation Reviewed

Task-document patch application only; no schema migration or Background implementation validation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Address the Developer Self-Review corrections below in the next claimed attempt. Do not begin dependent API/Admin work or merge either task branch to `main`.

### Developer Override — Reopened (2026-10-13)

- Previous accepted attempt: none. The task has not been claimed; preserve `attempt: 0` without incrementing.
- Reason: the developer explicitly requests reopening this task. This records the requested workflow override and does not assert that its prerequisites are satisfied or authorize implementation to begin.
- Reopen is not a claim. Preserve `execution_mode: developer` and `completion_mode: developer`; `executor` and `claimed_at` remain null.
- Dependency gate remains outstanding: `ARCH-026-API-007` is `pending` and `ARCH-036-DATABASE-003` is `ready`, not complete. Do not claim an attempt until both declared dependencies are complete and the task is made eligible by dependency-frontier reconciliation.
- Downstream frontier checked: `ARCH-036-API-002`, `ARCH-036-ADMIN-001` and `ARCH-036-SYSTEM-TEST-001` remain `pending`; no downstream status changes are required.

## Developer Self-Review — Changes Requested

### Result

Attempt 1 does not pass review. Task returned to `ready`; `attempt` remains 1, and `executor` / `claimed_at` are cleared. Do not create attempt 2 until a new `/moda_developer_create ARCH-036-BACKGROUND-001` claim.

### Corrections Required

1. Resolve the nested `database` revision through the accepted ARCH-036-DATABASE-003 dependency so Prisma generation exposes `BackgroundRuntimeLeaseName.WOO_COUPON_SYNC_DISPATCH`. Keep Background from authoring schema/migration changes and do not publish a stale or unrelated `database` gitlink. Rerun `npm run build` and the dispatch PostgreSQL integration; both must pass, including fixture cleanup.
2. Change catalogue reconciliation so one verified complete scan missing an existing coupon does not mark it removed. Require two consecutive verified complete generations missing the same coupon, preserve its merchant `isAvailable` selection and history during the first absence, and add PostgreSQL coverage for first absence, second confirmed absence, failed/partial scans and reappearance.
3. Add and run the required 10,000-shop due-dispatch simulation. Record achieved completed scans/second, average and p95 scan latency, backlog/oldest due age, configured concurrency and headroom against 5.56 completed scans/second; do not claim a 30-minute freshness target without measured evidence. Ensure dispatcher discovery/due scanning demonstrates bounded pagination and backlog fairness.
4. Add and run task-specific PostgreSQL/Redis evidence for two competing dispatchers, global lease exclusivity, heartbeat/expiry takeover, callback failure/stale owner, per-shop claim fencing and publication-loss recovery. Add API-007-sealed credential compatibility and wrong-key/AAD/tenant/version rejection evidence, and document the actual validated refresh/cooldown/page/worker settings and secret wiring.

### Validation Reviewed

Focused unit tests passed (30/30). Build failed on the generated Prisma enum; the PostgreSQL dispatch integration reached successful worker reconciliation but failed during cleanup on that same missing enum. These failures and unrun acceptance evidence prevent a passing review.

## Architect Review — Scope Clarification (2026-10-13)

### Review Status

Changes Requested — Attempt 1 remains `ready` with `attempt: 1`, `executor: null` and `claimed_at: null`. No new attempt has been claimed or completed by this documentation update.

### Superseding correction contract

The developer clarified that **10,000 shops was an illustrative capacity example, not an ARCH-036-BACKGROUND-001 acceptance requirement**. This decision expressly **supersedes Correction 3** in the historical `Developer Self-Review — Changes Requested` above, including its 10,000-shop simulation, 5.56 completed scans/second threshold, p95 latency measurement and headroom evidence. The earlier review is retained unchanged as the record of what was requested at the time; it is not the active contract on this point.

The next claimed attempt must still prove, using bounded deterministic fixtures, that due-shop discovery is paginated, the dispatcher enqueues only a configured bounded batch, and shops beyond the first batch are not starved. Production-scale load testing is optional follow-up work and must not block this task. The 30-minute per-shop refresh remains an initial configuration target, not a certified production SLA.

**Corrections 1, 2 and 4 remain fully required and unchanged:** resolve and verify the accepted Database submodule/Prisma enum, implement two-consecutive-complete-scan confirmation before marking coupons `REMOVED`, and prove multi-instance lease exclusivity, failover/stale-owner safety, per-shop fencing, publication-loss recovery and API-007 credential compatibility. Existing scope, dependency and validation requirements unrelated to the large-population benchmark remain in force.

### Follow-up

Reclaim Attempt 2 only through `/moda_developer_create ARCH-036-BACKGROUND-001`. Preserve the unpublished implementation and modified database checkout until their exact provenance and gitlink are reconciled. The task remains subject to its existing `completion_mode: developer` review and explicit completion decision.

## Developer Self-Review - Changes Requested

### Result

Attempt 2 does not pass review. The task returns to `ready`; `attempt` remains 2, and `executor` / `claimed_at` are cleared. Do not increment the attempt in this review update. A later `/moda_developer_create ARCH-036-BACKGROUND-001` claim starts attempt 3.

### Implementation Reviewed

The implementation task branch is published and clean at `c36bc5691b6fbf5eccba26bcb6e9b670e960adbd`. This correction commit updates `src/services/woo-coupon-catalogue.service.ts`, `tests/integration/woo-coupon-catalogue-reconciliation.integration.test.ts`, `tests/integration/woo-coupon-dispatch-worker.integration.test.ts`, and `tests/unit/services/woo-coupon-catalogue.service.test.ts`. It adds confirmed two-successful-scan removal behavior, keeps merchant selection/history on first absence, and expands lease/publication recovery coverage. The `database` submodule is clean at the branch's recorded `33b42ece85b042230863a1c04d05d7d4383800a2` revision, which contains the DATABASE-003 enum; Background does not author a migration.

### Validation Results

- Passed `npm run build`; Prisma Client generation used the pinned DATABASE-003 schema and TypeScript compilation succeeded.
- Passed the focused Woo unit suites: 10 files, 73 tests.
- Passed `npm run test:arch036-woo-coupon-catalogue:postgres`: 1 file, 3 tests.
- Passed `npm run test:arch036-woo-coupon-dispatch:postgres`: 1 file, 3 tests, including competing global lease acquisition, heartbeat, expiry/takeover, callback failure, dispatch reservation overlap and Redis publication recovery.
- Passed `git diff --check`; the implementation branch is clean and synchronized with its published task branch.
- Full `npm test` and `npm run test:integration` were not run.

### Corrections Required

1. Add validated configuration for the currently hard-coded dispatcher batch (`500`), refresh (`30` minutes), request/retry cooldowns (`5`, `30` and `15` minutes), provider page limit (`50`) and request/body bounds. Worker concurrency (`WOO_COUPON_SYNC_WORKER_CONCURRENCY`) and the API-007 keyring already have validation; retain those protections. Keep the global lease at the fixed 60-second cadence and do not add Prisma columns or migrations. Document the actual validated settings, operational meanings, keyring/secret wiring and limits.
2. Emit structured dispatcher-cycle operational signals using the shared logger/metrics: discovered/scanned, due, reserved, published, skipped, backlog and oldest-due age. Current `WooCouponDispatchResult` reports only catalogues created, shops reserved and jobs published; recovery `onError` emits a generic `console.error`, and generic BullMQ queue telemetry does not expose catalogue due backlog. Add focused tests proving safe bounded fields and that telemetry failure cannot fail dispatch.
3. Add a deterministic bounded-backlog PostgreSQL test with more due shops than the configured batch. Assert each cycle stays within budget and shops beyond the first batch are eventually selected without starvation; also cover bounded discovery/bootstrap across batches. The prior scope clarification explicitly removes the 10,000-shop benchmark and throughput target, so do not reintroduce that load test as a gate.
4. Replace/augment the locally self-sealed grant test with a stable fixture produced by the API-007 sealing implementation. Prove Background opens that fixture and rejects wrong key/key ID, each AAD identity/version component (shop, installation, attempt, credential version), mismatched tenant/scope and grant rotation. Current tests construct ciphertext locally and cover wrong-attempt AAD plus revocation, but do not prove producer-to-consumer fixture parity or the required rejection matrix.
5. Add a PostgreSQL stale-shop-owner takeover test: expire an existing `SYNCING` claim, allow a successor generation/token to reconcile, then release the old reader and prove it cannot alter the successor's rows or catalogue state. Current PostgreSQL tests cover concurrent live claims and global lease takeover; stale per-shop fencing is only simulated by the unit-test transaction fake.

### Review Decision

The DATABASE-003 enum/build blocker and the one-scan removal defect are resolved and validated in attempt 2. Remaining required operational, fairness, credential-parity and persisted per-shop fencing evidence prevents acceptance. No implementation files were changed during this review, and no task branch was merged to `main`.
