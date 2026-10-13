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
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-026-API-007"]
enables: ["ARCH-036-API-002", "ARCH-036-ADMIN-001", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-13
---
# ARCH-036-BACKGROUND-001 — Schedule and reconcile WooCommerce coupon catalogues

## Architecture

- Parent: `ARCH-036` — `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`; implementation owner: `moda_background`, repository `moda-interact-background`.
- **Defined but not materialised in the developer's workspace.** Do not interpret this patch as a task claim, worktree creation, implementation, test run, commit or push.
- This definition supersedes the earlier **per-shop recurring-scheduler** suggestion. There is **one global recurring dispatcher**, with independent **one-off shop jobs** and per-shop catalogue claims. The design must not create 10,000 BullMQ Job Schedulers for 10,000 shops.

## Objective

Automatically discover connected WooCommerce shops, register each in the existing discount-catalogue table regardless of whether a Woo read grant exists, dispatch bounded batches of shops due for refresh through **one global BullMQ schedule**, and safely synchronise complete, paginated, read-only WooCommerce coupon catalogues into existing PostgreSQL rows while preserving merchant checkbox selections.

## Context

The four in-session ARCH-036 implementation tasks concern Woo coupon synchronisation, API configuration, Woo merchant UI and internal Admin visibility. CommerceAgent, outbound recovery, coupon redemption and Shopify behaviour are **out of scope**.

Inspected snapshot evidence:

- `moda-interact-database/prisma/schema.prisma` already defines `Shop` (including `platform`, `status`), `WooCommerceInstallation`, `WooCommerceRestReadGrant`, `ShopifyDiscountCatalogue` and `ShopifyDiscount`. `ShopifyDiscountCatalogue.shopId` is unique; the catalogue has `status`, `syncGeneration`, `activeSyncToken`, `syncRequestedAt`, `syncStartedAt`, `lastSuccessfulSyncAt`, `lastErrorAt`, `lastErrorCode` and `unavailableAt`.
- `moda-interact-background/src/entrypoints/recovery.ts` starts the existing recovery workers, Shopify discount sync worker and scheduler/telemetry. `src/workers/shopify-discount-sync.worker.ts` illustrates a BullMQ worker; `src/services/shopify-discount-catalogue.service.ts` illustrates per-shop row locking and generation/fencing, **but must not be reused without removing its Shopify-specific availability writes/eligibility logic**.
- `src/runtime/dynamic-leased-scheduler.ts` + `src/runtime/background-runtime-lease.ts` use PostgreSQL `BackgroundRuntimeLeaseName`; the enum has **no Woo coupon dispatcher member**. Adding one requires a database migration and an updated lease cadence mapping. **Do not do so in this task.** Use one uniquely identified BullMQ v6 Job Scheduler instead, with bounded dispatch and independent PostgreSQL shop claims.
- API-owned credential format is implemented in `moda-interact-api/src/woocommerce/rest-read/envelope.ts`. API's read-only provider transport/security precedent is in `.../rest-read/credential-verifier.ts`; implementation must not import private API source at runtime.
- `moda-interact-api/src/woocommerce/installation/connection-service.ts` creates a Woo `Shop` and `WooCommerceInstallation` but does **not** currently create a `ShopifyDiscountCatalogue` row. Background must therefore idempotently **bootstrap missing catalogue rows** from Woo installations on its dispatcher scan. This is eventual registration after installation, not a claim that the API installation transaction already creates the row. Missing read permission is **never** a reason to omit that row.

## Scope

Only `moda-interact-background` runtime, tests and local configuration/documentation required for this bounded capability:

1. One globally identified BullMQ coupon dispatcher (proposed tick: 60 seconds), shared across all worker replicas.
2. Bounded PostgreSQL discovery/bootstrap and due-shop dispatch (proposed maximum 500 jobs per tick); one transient BullMQ job per due shop; **no recurring schedule per shop**.
3. Shop-scoped claim/timeout/retry/fencing using existing catalogue fields.
4. Worker-time Woo installation/grant verification and API-007-compatible AES-GCM decryption.
5. SSRF-safe, authenticated `GET /wp-json/wc/v3/coupons` with complete bounded pagination, normalisation and fenced reconciliation of Woo rows only.
6. Focused validation and operational signals demonstrating fair dispatch, recovery, tenant isolation and preservation of merchant selections.

## Out of Scope

- No Prisma migration, new table/column/enum/index, Shared package/contract, API proxy, Woo PHP hook or webhook, plugin-side coupon uploader, per-shop recurring Job Scheduler, new process/deployment or new generic queue framework.
- No changes to Shopify's existing discount service or meaning of `ShopifyDiscount.isAvailable` on Shopify shops.
- No merchant checkbox writes, `ShopSettings` offer-mode writes, CommerceAgent/tool changes, recovery scheduling/outreach, coupon proof at send time, coupon creation/modification/deletion at WooCommerce, customer eligibility promises or redemption.
- Do not modify another repository or introduce new key storage/authentication mechanisms to solve a missing API-007 prerequisite; report architectural gaps to `moda_architect`.

## Requirements

### A. One dispatcher, installation discovery and scheduling

1. **Single logical schedule:** introduce one BullMQ v6 Job Scheduler with a stable ID such as `woo-coupon-dispatch-v1` and a bounded `dispatch-woo-coupon-sync` payload (no merchant IDs or credentials in the recurring job). Register/upsert it idempotently on recovery-worker startup. A deployment with 1 or N Background replicas must still have one recurring schedule and must never spin up one timer or recurring scheduler per shop. Ensure registration and graceful queue/worker shutdown are compatible with `src/entrypoints/recovery.ts` and existing readiness flow.
2. **Cadence:** *proposed initial configuration* is a 60-second dispatcher tick and a 30-minute target refresh interval per shop. These are two different clocks: **every minute dispatch many due shops**, not one shop every 30 minutes. The refresh interval is a target, not a guarantee under provider outages or insufficient fleet capacity. Keep bounds configurable through validated Background runtime/environment settings without altering `BackgroundRuntimeConfig` columns or its PostgreSQL enum. Defaults must be safe; do not add unsupported admin controls.
3. **Discovery/bootstrap:** in bounded keyset pages, read `Shop` joined with `WooCommerceInstallation`; find genuinely connected `platform=WOOCOMMERCE` shops, with active installation/Shop. `INSERT ... ON CONFLICT DO NOTHING` / Prisma `upsert` a `ShopifyDiscountCatalogue` row when absent, initially `SYNC_REQUIRED` with `lastSuccessfulSyncAt=NULL`; **do not filter discovery by grant**. Do not touch Shopify catalogue rows. Treat inactive/disconnected shops as not dispatchable but preserve their historical catalogue/selection records. Newly connected shops are discovered on the next tick without needing a new Woo plugin/API write.
4. **Due selection:** scan catalogue/installation identities using bounded pages and indexed keyset (`shopId`), avoiding a full unbounded result or an N+1 query. Eligible cases: never successfully synced; CURRENT but refresh interval elapsed (with deterministic per-shop spreading/jitter); ERROR/UNAVAILABLE after retry cooldown; stale queued/SYNCING claims eligible for recovery. Do not requeue every minute only because `lastSuccessfulSyncAt` is NULL. Check current Shop/installation eligibility here for waste avoidance, **but check grant only inside the shop worker** so granting read access later needs no new registration event.
5. **Fairness and scale:** rotate the catalogue scan cursor or otherwise ensure that a sustained backlog cannot indefinitely starve shops after the first batch. Limit each cycle by a configured dispatch budget (proposed 500), database page size and total runtime. Record scanned/due/claimed/enqueued/skipped counts, oldest due age and backlog. At 10,000 shops and a 30-minute desired refresh interval, the system needs **at least 10,000 / 1,800 = 5.56 successfully completed shop scans per second**, not merely enqueue throughput. Size worker concurrency and network budgets from measured latency and rate limits; no claim that 500 queued jobs/minute guarantees completion.
6. **Dispatch race and Redis failure:** atomically claim each due catalogue row using its current `status`, `syncRequestedAt`, `syncStartedAt` and relevant timestamps (compare-and-set/row lock), **commit the short PostgreSQL operation before BullMQ publication**, then enqueue with a deterministic bounded `jobId` derived from shop and that claim's timestamp/identity. Do not hold a DB transaction while publishing to Redis. If publication fails or the process dies between claim and enqueue, a bounded dispatch timeout makes the row due again; a repeated dispatcher must not leave it stranded. Replayed one-off jobs must be harmless. Do not use BullMQ deduplication as the only protection against same-shop concurrent processing.
7. **Dispatcher failover:** losing Redis's recurring schedule must be recoverable by idempotent setup on next process start; if runtime health/reconciliation already detects missing schedulers, reuse it. Do not conflate scheduler ownership with shop-specific database fencing. If an existing maintenance component can provide the single global tick without new migration, document and prove that equivalence rather than implementing duplicate timers.

### B. Queue job and per-shop worker

8. Use one local Background queue, e.g. `woo-coupon-sync`, with two bounded job shapes: a global `dispatch-woo-coupon-sync` and a shop job `sync-woo-coupons` whose **only business identifier is the internal `shopId`** (optionally a bounded dispatch-claim token). Parse/validate payloads at the worker boundary. Retries/backoff and retention must be bounded; successful jobs must not permanently block future dispatch IDs. Reject malformed payloads. Avoid logging provider URLs, consumer keys/secrets or raw responses.
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

- [ ] Add the one-off Woo coupon queue/typed payload parser and single global recurring BullMQ dispatcher schedule; wire to recovery process startup/shutdown, readiness and queue telemetry.
- [ ] Implement bounded installation-to-catalogue bootstrap, due-shop scanning with fairness, atomic dispatch claims, enqueuing and publication-loss recovery without requiring grant at registration.
- [ ] Implement worker-time current grant resolver/AES-GCM envelope parity, safe canonical Woo origin and transport, plus pagination with strict complete-scan evidence and bounds.
- [ ] Implement token/generation-fenced shop reconciliation and conservative verified-missing handling, preserving all Woo merchant selection flags and Shopify behaviour.
- [ ] Add unit/transport/PostgreSQL/queue tests including 10,000-shop dispatcher simulation and document operational configuration and production-safe credential handling.

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
| `src/runtime/woo-coupon-sync-config.ts` | Validate bounded cadence, batch, concurrency, timeout, pagination and keyring configuration; reuse existing environment/crypto helpers rather than add DB columns. |
| `src/entrypoints/recovery.ts` *(modify)* | Register one global Job Scheduler and one shop-worker pool; add queue metrics and close/stop hooks. |
| `tests/unit/services/woo-coupon-*.test.ts` and `tests/unit/workers/woo-coupon-*.test.ts` *(new)* | Dispatch fairness, grant, pagination, mapping, worker/lock/retry tests split by responsibility. |
| `tests/integration/woo-coupon-sync.integration.test.ts` *(new)* | Disposable PostgreSQL + Redis claims, generation fencing, cross-shop isolation, completion/retry recovery. |

Paths are proposed repository-relative implementation boundaries, not already existing files. Adapt test filenames only to match established repository conventions; do not collapse the implementation into a monolithic service. Local queue job shapes remain internal to Background; **no cross-service Shared package publication** is required.

### Provider request contract

- Canonical origin: `WooCommerceInstallation.canonicalSiteUrl` (and its approved base path), *never* a client-supplied origin in a queue message.
- Endpoint: `GET /wp-json/wc/v3/coupons`; query: `page=<1-based integer>&per_page=100&orderby=id&order=asc` (add only verified required fixed parameters).
- Auth: Woo read-only consumer key/secret from current API-007 grant; HTTPS Basic header; no secret query arguments; preserve the existing explicitly approved local-development auth mode.
- Pagination evidence: `X-WP-Total`, `X-WP-TotalPages`, per-page array, sorted unique positive IDs, response/header consistency and entire-scan reconciliation.
- Producer/consumer: Background dispatcher → Background BullMQ worker → Background provider/reconcile services. Queue payload contains only bounded internal identifiers.
- Reference for the API-owned wire/envelope definitions: `moda-interact-api/src/woocommerce/rest-read/{envelope,credential-verifier}.ts` in the supplied snapshot; these are **reference implementations, not package imports**.

## Dependencies

- `ARCH-026-API-007` — requires architect-accepted ACTIVE read-grant persistence, canonical Woo installation identity and the API-owned AEAD envelope/keyring. Background must fail closed if the prerequisite is not satisfied.

## Enables

- `ARCH-036-API-002`
- `ARCH-036-ADMIN-001`
- `ARCH-036-SYSTEM-TEST-001` (terminal, after all four in-session implementations are Complete).

## Acceptance Criteria

- [ ] Every connected Woo shop is eventually registered in `ShopifyDiscountCatalogue` by the global discovery path **even without a read grant**, and every later eligible job independently rechecks permission; grant changes require no per-shop scheduler registration.
- [ ] Exactly one logical recurring BullMQ dispatch schedule exists for any number of Background replicas/shops. A dispatch tick can enqueue multiple due shop jobs, uses bounded queries/batches and cannot starve overdue shops or keep requeueing missing-grant shops each minute.
- [ ] For a simulated 10,000-shop population, demonstrate the 30-minute throughput requirement (5.56 completed scans/second) as a **capacity calculation and instrumented load-test scenario**, report measured throughput/latency and scale/concurrency headroom; do not claim production 30-minute freshness without evidence.
- [ ] A worker securely constructs and authenticates Woo coupons GET requests and fetches all bounded pages. Zero coupons is accepted only with complete consistent evidence. Missing pages, changed totals/duplicates/oversize/timeout never become CURRENT or mark coupons deleted.
- [ ] Provider reads use the **actual** encrypted API-007 read grant and shop/version/AAD/keyring parity; unauthorised, revoked, rotated, cross-shop, SSRF/redirect or stale-grant attempts fail closed without leaking keys.
- [ ] Per-shop claims prevent concurrent writes; crashed owners can be replaced, and stale tokens cannot overwrite newer generations. Redis dispatch loss or duplicate delivery does not strand or duplicate a shop indefinitely.
- [ ] Woo row updates preserve `isAvailable` on every existing row; new rows default `false`; expiry/removal changes provider eligibility only. Shopify provider availability and code paths are unchanged. Referenced historical rows are retained.
- [ ] Shop A outage cannot block Shop B, no cross-tenant coupon can be attached to another Shop, and no API/Shared/Shopify/CommerceAgent/recovery code, database schema or migration is changed.

## Validation

- [ ] Unit tests: due/cooldown/fairness, bootstrap without grant, grant granted after initial skip, queue dedupe/dispatch publication gap and repeat scheduler registration across replicas.
- [ ] Provider tests: exact authenticated query and page construction, totals/headers, 0/1/100/101/200+ coupons, missing/duplicate/out-of-order pages, concurrent provider edits, limits, retry/429, wrong auth, redirects, DNS/peer/TLS protections and key/AAD parity with API-produced fixture.
- [ ] Disposable PostgreSQL + Redis integration: two Woo shops and a Shopify shop, 10,000-shop due enumeration simulation, initial/recurring sync, competing worker claims, expired claim takeover, stale writer fencing, selection preservation, missing-row confirmation and Redis publication failure/recovery.
- [ ] Run actual declared Background checks according to `moda-interact-background/package.json`: focused `npm test` / `npm run test:integration` where relevant; `npm run build` (includes Prisma generate); any repository-provided changed-file lint/type validation. No fabricated `npm run typecheck` or `npm run lint` scripts if missing. `git diff --check` required.
- [ ] Record tested worker concurrency, average/p95 shop scan latency, achieved completed shops/s, backlog age and whether the proposed 30-minute target was met in the test environment. Distinguish measured results from assumptions and identify any infrastructure/index bottleneck without silently adding a database migration.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, fill the Completion Report, return the task at `status: review` and **STOP**. Do not begin dependent API/Woo/Admin work or any superseded task. For `execution_mode: developer`, final completion remains the developer's explicit action after review.

## Implementation Notes

- **Source-of-truth split:** PostgreSQL stores each shop's catalogue, freshness and fenced claim; Redis/BullMQ carries work and one global recurring dispatcher. Neither a Redis-only lease nor a per-shop BullMQ schedule is the durable source of business state.
- **No migration exception:** this task does *not* add `WOO_COUPON_SYNC_DISPATCH` to the PostgreSQL `BackgroundRuntimeLeaseName` enum. If approved operational evidence later requires PostgreSQL global leasing or a due-time index, stop and raise a separately approved schema/task change; do not silently expand BACKGROUND-001.
- **Registration vs permission:** Background bootstrap creates the catalogue row based on installation presence; the worker alone checks current read grant on each attempt. A missing grant results in a non-terminal skip/cooldown, not permanent exclusion.
- **Eligibility vs merchant selection:** any coupon may be visible in the catalogue even if not selectable. `isAvailable` is reserved for Woo merchant checkbox persistence by `API-002` and may be `true` even when provider status later makes the coupon ineligible. Never reinterpret Shopify rows this way.
- **Security:** do not use a generic HTTP client that automatically follows redirects or embeds Basic credentials in URLs; test actual DNS-pin and TLS-peer behaviour. A healthy LocalWP test cannot stand in for required production-safe transport evidence.
- **Task isolation:** agent/developer execution must use launcher-resolved dedicated worktrees in the real workspace and record start-of-attempt synchronisation/submodule evidence. Do not claim a branch, commit or push based on this portable snapshot.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task remains unclaimed.

### Deviations

None.

### Assumptions

The developer will supply a runnable canonical workspace; observed deployment throughput and transport connectivity are not yet measured.

### Unresolved Issues

None blocking task definition. Cadence/batch/page caps are **initial proposed defaults** and must be capacity-tested; their final production settings are not inferred from the snapshot.

### Architectural Concerns

If the actual deployment needs database due indexes, a PostgreSQL global lease enum update, cross-service encryption contract publication or gateway/environment changes, return the gap to `moda_architect` before editing another repository.

## Architect Review

### Review Status

Pending.

### Review Notes

Attempt 8: detailed planning definition only; no code, migration, task status transition or branch changes. Preserves the four-task, Woo-only session boundary.

### Reviewed Files

Architectural task and inspected snapshot implementation cited above.

### Validation Reviewed

Task-document patch application only; no implementation validation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

After task materialisation and dependency acceptance, use developer task execution; review implementation evidence before any completion.
