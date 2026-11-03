# WooCommerce API database review — working record

**Review date:** 2 November 2026; earlier increments retain their original review dates.
**Status:** Static endpoint review complete — revision 13, all 61 endpoints covered. See the separate final consolidated report; this is not implementation acceptance.
**Increment policy:** Review five further endpoints at a time, following the user's request.
**Coverage:** E01–E61; zero original method/path combinations remain. 59 business routes and 2 health routes.
**Source:** `moda-interact-workspace(20261101-205935).zip`
**Archive SHA-256:** `ee42bb83ee441ba9018779e760967a5bf87edcbc429eecc58699f1419863861b`
**Primary repository:** `moda-interact-api`
**Evidence files:** `woocommerce-api-database-review-01-source-evidence.txt` (E01), `woocommerce-api-database-review-02-source-evidence.txt` (E02–E06), `woocommerce-api-database-review-03-source-evidence.txt` (E07–E11), `woocommerce-api-database-review-04-source-evidence.txt` (E12–E16), `woocommerce-api-database-review-05-source-evidence.txt` (E17–E21), `woocommerce-api-database-review-06-source-evidence.txt` (E22–E26), and `woocommerce-api-database-review-07-source-evidence.txt` (E27–E31). Increment-08 evidence: `woocommerce-api-database-review-08-source-evidence.txt` (E32–E36); revision-08 manifest: `woocommerce-api-database-review-08-source-manifest.json`. The review-only compaction model and result are included. Revision-07 manifest: `woocommerce-api-database-review-07-source-manifest.json`; available earlier manifests are retained in the ZIP. Review-only pagination/digest models and their results are included. Earlier increment entries are historical records; their original per-increment progress and next-batch statements are not the current total or next scope.

Increment-09 evidence: `woocommerce-api-database-review-09-source-evidence.txt` (E37–E41); manifest: `woocommerce-api-database-review-09-source-manifest.json`. The new order-equivalence model and result are included; earlier model files remain historical evidence.

Increment-10 evidence: `woocommerce-api-database-review-10-source-evidence.txt` (E42–E46); manifest: `woocommerce-api-database-review-10-source-manifest.json`. The review-only catalogue model and result are included. Earlier next-increment and progress statements remain historical.

Increment-11 evidence: `woocommerce-api-database-review-11-source-evidence.txt` (E47–E51); manifest: `woocommerce-api-database-review-11-source-manifest.json`. The review-only coupon-selection model and result are included. Earlier per-increment progress and next-scope statements remain historical.

Increment-12 evidence: `woocommerce-api-database-review-12-source-evidence.txt` (E52–E56); manifest: `woocommerce-api-database-review-12-source-manifest.json`. The review-only recurring-blocker predicate model and result are included. Earlier per-increment progress and next-scope statements are historical.

Increment-13 evidence: `woocommerce-api-database-review-13-source-evidence.txt` (E57–E61); manifest: `woocommerce-api-database-review-13-source-manifest.json`. Isolated readiness helper script/results and final endpoint inventory accompany the final package. Earlier progress statements remain historical.

## Final report contract

The consolidated report will bring together the endpoint inventory, per-path database operations, transaction boundaries and justification, redundant/over-fetching queries, concurrency and idempotency requirements, relevant constraints/indexes, original-error preservation, prioritised recommendations, implementation ownership, and validation evidence. Findings will distinguish inspected source behaviour, proposed changes, measured runtime results, and unresolved questions. The report will include retained behaviour as well as recommended changes. It will not equate Prisma model calls with SQL statements or infer latency improvements from source counts.

No repository source, schema, task, architecture or `_index.md` file was modified in this review. No task was created, reopened, materialised or accepted. No branch, commit, push or application patch was produced.

## Entry E01 — POST /v1/woocommerce/installations/connect

### Scope and evidence

The route accepts `siteUrl`, `attemptId`, and `bootstrapSecret`. It uses the site-control challenge rather than the installation bearer authenticator used by the separate GET probe. Successful creation returns 201; reconnect returns 200. [S1, original lines 42–61 and 126–174]

Inspected the route, connection service, Free-plan preparation/activation helpers, relevant Prisma models and installation migration, architecture requirement, and unit/integration test sources. API's nested database schema and the root database repository schema have identical SHA-256 in this snapshot: `45df5e44bdc1e7e29495e391a1754477f0df362c667d648f4b6893b6541f5c0d`.

### Current flow

1. Validate body and canonicalise site URL.
2. Read installation identity/version and selected related Shop fields.
3. Verify live site control over the network, outside the merchant transaction.
4. Generate a credential; persist its digest, not the raw credential.
5. For a new or not-yet-onboarded Shop, prepare global Free-plan configuration outside the merchant transaction.
6. Enter a Serializable transaction with a 15,000 ms timeout. New installation: create Shop, activate Free subscription/lifetime counter/onboarding, create installation. Reconnect: re-read/check Shop, invoke activation helper, rotate credential with a version-conditional update, restore an UNINSTALLED Shop if necessary, then read installation response fields again.
7. Commit before returning the connection result.

`runTransaction` allows two total attempts for P2034 or the activation-specific retry error. It does not repeat site proof or global preparation. The original observed credential version remains the compare-and-set baseline. [S2, lines 57–202; S3, lines 70–159]

### Source-derived operation counts

These count explicit Prisma model-method calls along a successful, non-retried path. `$transaction` control, BEGIN/COMMIT/isolation setup, relation-query expansion, nested writes, database triggers, and provider network work are not counted. They are not measured SQL round trips.

| Path and assumptions | Outside merchant transaction | Inside merchant transaction | Total |
|---|---:|---:|---:|
| Already-onboarded ACTIVE reconnect | 1 | 4 | 5 |
| Already-onboarded UNINSTALLED reconnect | 1 | 5 | 6 |
| First connection; valid operational Free plan already exists and catalogue is marked materialised | 4 | 11 | 15 |

First-connection outside operations: installation lookup; catalogue+features lookup; first-grant policy lookup; operational plan lookup. Inside operations: Shop create; activation Shop lookup; Subscription lookup; catalogue invariant lookup; operational-plan invariant lookup; lifetime-counter lookup; first-grant-policy lookup; Subscription upsert; lifetime-counter create; onboarding update; installation create.

The first-connection total becomes 16 when an existing operational plan needs its catalogue marker updated. With initial operational-plan creation it is 17 without merchant-knowledge validation, or 18 when that validation also queries active purpose/format pairs, assuming success without a uniqueness race or transaction retry. These are derived counts, not a performance benchmark. [S2, S3, S4]

### Transaction assessment — retain

A transaction is justified: new Shop, installation, active Free subscription, lifetime allocation and onboarding must commit together. Reconnection must not partially rotate credentials, restore installation lifecycle, or alter initial entitlements. This agrees with ARCH-027's existing requirement. [S7, lines 363–401]

The atomic unit is merchant activation. Global operational Free-plan preparation is intentionally independent and can remain committed if the later merchant transaction fails. The source contains an integration scenario for that distinction. [S4, lines 13–15, 98–133; S8, lines 585 onward]

Retain site proof outside the transaction, the transactional Shop revalidation, credential-version compare-and-set, no-second-grant rule, paid-subscription preservation, unique constraints, bounded retries, and transaction-local catalogue/policy checks. Do not lower isolation as a side effect of read consolidation. No new Redis/outbox, external service or schema change is justified by the current findings.

### Findings register

#### E01-F01 — Duplicate Shop read within reconnect transaction

**Classification:** Confirmed duplicate model lookup; recommended optimisation.
**Priority:** Medium.
**Evidence:** `src/woocommerce/installation/connection-service.ts:123–132` [S2] and `src/woocommerce/billing/initial-free-activation.service.ts:75–80` [S3].

The connection service reads Shop identity/status/platform; activation immediately reads the same Shop for onboarding state. There is no intervening write. Load onboarding state with the first transaction-local Shop read and pass that authoritative transaction-local result to activation, or skip activation for an already-onboarded Shop using that result. Never substitute the pre-proof `observed.shop` object. Keep the post-proof transactional revalidation.

Expected source-level change on already-onboarded reconnect: one fewer model call. Reuse of the new Shop create result may also remove its immediate activation re-read, but that is a secondary candidate requiring explicit helper contracts and tests.

#### E01-F02 — Installation read after guarded credential update

**Classification:** Confirmed update-then-read pattern; recommended optimisation.
**Priority:** Medium.
**Evidence:** `src/woocommerce/installation/connection-service.ts:134–161` [S2].

`updateMany` checks installation ID, Shop ID and the observed credential version. After requiring exactly one affected row, the service issues `findUniqueOrThrow` for ID, Shop ID and new version. Prefer a guarded update returning those fields, with exactly one returned row required. Keep the same predicate and conflict semantics; do not make it an unconditional update.

The snapshot pins Prisma 6.19.3. The official Prisma v6 API reference documents `updateManyAndReturn` for PostgreSQL from 6.2.0. This is a compatible design candidate, not an implemented or runtime-verified change. Verify generated client types and emitted SQL before acceptance.

Combined target with F01: already-onboarded ACTIVE reconnect 5 -> 3 model calls; UNINSTALLED reconnect 6 -> 4. This is not a claim of 40% lower latency or SQL cost.

#### E01-F03 — Eager feature graph on operational-plan reuse

**Classification:** Confirmed over-fetching; lower-priority optimisation candidate.
**Priority:** Low pending measurement.
**Evidence:** `src/woocommerce/billing/free-plan-preparation.service.ts:50–95, 98–118, 144–175` [S4].

Preparation always fetches catalogue feature mappings and complete related Feature records before checking whether a valid operational plan already exists. That reuse path only validates the operational plan and optionally marks the catalogue as materialised; it does not consume the feature graph. Prefer a narrow initial catalogue projection and lazy feature loading only for operational-plan materialisation. The cold path may gain a model call; the benefit is avoiding unnecessary relation work on the reuse path. Measure SQL and payload before claiming round-trip savings. The initial installation lookup also selects Shop status/platform/Shopify ID that the later transactional read, not the initial projection, supplies to the decision.

#### E01-F04 — Original handled Prisma failures are lost

**Classification:** Confirmed diagnostic gap.
**Priority:** Medium; preserve original-error requirement.
**Evidence:** `src/woocommerce/installation/connection-service.ts:34–38, 172–199` [S2], activation counter catch at `initial-free-activation.service.ts:138–153` [S3], and route `routes.ts:62–95` [S1].

P2002 and exhausted P2034 failures are converted to a new generic `WooConnectionConflictError` without a cause. The route returns 409 for that class without logging it. Counter uniqueness failures are similarly wrapped in `RetryFreeActivationTransactionError` without retaining the cause. Unexpected errors do have logging, so logging is not wholly absent.

Preserve original exceptions through typed wrapping and emit bounded semantic diagnostics through `@modainteract/moda-interact-shared/logging`, with code/message and safe relevant metadata, redacting secrets. Differentiate expected CAS/uniqueness losers from exhausted or unexpected failures. Keep safe public response bodies. Avoid noisy duplicate logs for every recoverable attempt; define deliberate levels and a terminal log where needed. Do not label every possible P2002 constraint violation as a proven expected connection race without checking the constraint/context.

#### E01-F05 — Full first-activation acceptance needs migrated-schema coverage

**Classification:** Validation coverage gap in the dedicated connection harness, not proof of a production defect.
**Priority:** Required before accepting optimisations.
**Evidence:** installation runner `scripts/test-woocommerce-installation-postgres.mjs:36–67` [S9]; immutable identity guard [S6]; consent runner [S11] and consent reconnect test [S10].

The dedicated connection suite uses disposable pg17+pgvector with `prisma db push`, rather than migration deployment. The installation migration contains a trigger and CHECK constraints absent from the Prisma model representation. Another migrated-schema consent suite does exercise real reconnect, so it would be inaccurate to say there is no migrated integration coverage at all. However, that does not establish migrated-schema coverage for all first-activation, billing and race branches in the dedicated connection suite.

Run first activation and reconnect acceptance on the canonical migrated schema, with fixtures satisfying the canonical catalogue constraints. Do not merely replace `db push` with `migrate deploy` and assume existing minimalist fixtures remain valid.

### Validation evidence and remaining work

Existing source tests cover first activation, rollback on invalid Free configuration or missing policy, preservation of lifetime quantities and paid state, conflicting initial subscription shells, concurrent first connects, concurrent reconnect CAS, suspended-Shop rejection, global plan materialisation races, and separation of global preparation from merchant rollback. Route tests cover logging of unexpected Prisma errors, but that is not the same as retaining handled conflict causes. [S8, S12–S14 and the complete inspected test sources]

No tests were executed in this review environment: `moda-interact-api/node_modules` is absent; Docker and psql commands are unavailable. No latency, SQL count, lock-wait, pool-pressure, or capacity measurement was made.

Before accepting changes, require focused tests with the real activation helper (not only its stub), transaction-local Shop reuse, unchanged pre-proof CAS baseline under retries, returned-row cardinality checks, rollback after a late failure, preservation of paid state and all grant quantities, no feature-graph load on operational-plan reuse, retained/redacted original errors, and actual per-path SQL counts on a migrated disposable database. Record retry and rejected-request paths separately from successful paths. Reuse approved instrumentation rather than introducing a competing logger or duplicate generic telemetry.

`attemptId` is used for challenge proof but is not persisted as an idempotency receipt by this service. Concurrent attempts sharing the observed version are guarded; a later successful reconnect can rotate again. Treat lost-response/sequential-retry semantics as a contract question for the plugin/handshake review, not as a proven defect or a reason to add a speculative receipt table. [S2, S15]

### Provisional endpoint decision

**Retain the transaction. Consolidate the duplicate Shop read and installation update/read first. Preserve all concurrency/entitlement checks. Address diagnostic cause preservation and require migrated-schema validation.** Implementation ownership is `moda_api`; no new database schema task is currently justified.

## External technical cross-checks (not evidence of application behaviour)

Prisma v6 API reference, checked 1 November 2026: `https://www.prisma.io/docs/orm/v6/reference/prisma-client-reference` — returning bulk updates supported from 6.2.0 for PostgreSQL.

Prisma v6 transactions reference: `https://www.prisma.io/docs/orm/v6/prisma-client/queries/transactions` — transaction boundaries, Serializable isolation and P2034 retries.

PostgreSQL 17 transaction isolation reference: `https://www.postgresql.org/docs/17/transaction-iso.html` — isolation/snapshot semantics. Serializable is not a promise of a fresh wall-clock read before every statement.


---

# Increment 02 — five more endpoints (E02–E06)

**Review date:** 1 November 2026.
**Review scope:** The five endpoints below; not the entire remaining API.
**Progress:** Six endpoint method/path combinations reviewed, including E01. Fifty-five remain from the earlier 61-route inventory.
**Status:** Static architectural findings and proposed changes, not implementation acceptance.
**Evidence:** `woocommerce-api-database-review-02-source-evidence.txt` (B02-S01–B02-S35). Original line numbers are preserved in that companion. E01 references S1–S15 continue to refer to the separate increment-01 evidence file.

## Increment summary

| Entry | Endpoint | Current database-client work on a successful path | Transaction decision |
|---|---|---|---|
| E02 | GET `/v1/woocommerce/installation` | 1 authentication model call | No explicit transaction needed |
| E03 | POST `/v1/woocommerce/activity` | 1 authentication model call; no business-state PostgreSQL writes | Keep queue acceptance outside any PostgreSQL transaction |
| E04 | POST `/v1/woocommerce/whatsapp-consent` | 5 calls on duplicate; 8 on existing recipient; 10 on new recipient | Retain atomic consent/evidence transaction |
| E05 | GET `/v1/woocommerce/customer-recovery-selection` | 5 calls, including recipient advisory lock and locking phone query | Retain the short authorization boundary initially; remove recipient write-style locking only after explicit snapshot-read contract and tests |
| E06 | POST `/v1/woocommerce/customer-recovery-selection` | 6 calls on mutation; 5 on duplicate | Retain locked read/check/write transaction |

**Counting convention:** These totals count one Prisma model method or one `$queryRaw`/`$executeRaw` call as one explicit database-client operation. Each total includes the initial bearer-authentication lookup. They exclude transaction initiation, isolation configuration, commit/rollback, trigger-internal SQL, relation-loading expansion, retries and Redis work. They are not measured SQL statements or round trips. The authentication model call includes a Shop relation. Historical measured SQL counts are presented separately below.

No code, migrations, task state, branch, worktree, commit or `_index.md` was changed by this increment. No benchmark or runtime test was run. This is a bounded source review, not a performance certification or a declaration that every race is proven safe.

## E02 — GET /v1/woocommerce/installation

### Current flow and operations

The route calls `WooInstallationAuthenticator.authenticate()` and returns only the principal. The authenticator rejects malformed/missing/duplicate credential headers before accessing PostgreSQL. Structurally valid credentials cause one `WooCommerceInstallation.findUnique` selecting installation identity, canonical URL, status, credential digest/version, revocation time and the related Shop's status/platform/Shopify identity. It compares the digest and rejects inactive/revoked or incompatible installations. There is no successful-authentication last-seen write. [B02-S01:21–75; B02-S02:101–118]

Successful request: **1 model call, 0 writes, 0 explicit transactions**. Missing/malformed credentials: **0 database calls**. A validly formatted but wrong credential normally requires the lookup before rejection. This describes source branches, not measured SQL.

### Assessment

Retain this read-only implementation. The endpoint reports authentication at the time of the lookup; it does not promise that credentials will remain valid for later requests. An explicit transaction would not provide a useful durable authorization guarantee once the response has left the server. Later privileged operations must authenticate independently and, when their transaction requires it, recheck the principal under locks.

No duplicate model call or unnecessary write was found in the successful probe path. Do not add an unbounded credential cache or a write on every probe solely for this review. Authentication is a repeated cost across routes, but its necessity is not disproved by its frequency.

### Validation and decision

Existing unit source covers correct principal derivation, invalid/duplicate headers, wrong/revoked/incompatible credentials and the route's safe success/error bodies. Unexpected probe errors retain message, stack and cause in logging. [B02-S19; B02-S20; B02-S02:109–114]

**Decision:** Retain. No new schema or application change justified for this endpoint in this increment. Actual SQL and relation-loading cost remain unmeasured in this review.

## E03 — POST /v1/woocommerce/activity

### Current flow

Authenticate installation → parse the bounded activity body → route CHECKOUT_UPDATED to the checkout publisher or order lifecycle events to the order publisher → verify queue acceptance/retained payload → return 202. The authenticated Shop ID, not a client-supplied Shop ID, is attached to the job. Parsing and phone normalization do not query PostgreSQL. [B02-S03:25–44; B02-S07; B02-S08:112–138,193–218; B02-S32–S33]

**Database:** 1 authentication model call, no business-state PostgreSQL writes, no explicit PostgreSQL transaction.

**Queue-client work:** For a fresh event the producer performs `getJob → add → getJob`; for an already retained ID it performs one `getJob`. These are queue-client method counts, not counts of underlying Redis commands. The post-add read verifies the stored digest because another request may have won the add for the same ID. A changed payload under a retained ID is rejected. [B02-S04:44–67; B02-S05]

### Transaction decision

Do not introduce a PostgreSQL transaction merely around enqueueing. This endpoint does not have a business-state database update to commit together with the event. Its acceptance boundary is the existing queue publication/retained-job check, not a PostgreSQL receipt. A PostgreSQL transaction would not make a Redis write rollback atomically with it.

Do not remove the post-add read as a superficially redundant lookup. Any proposed alternative must demonstrate equivalent concurrent payload-conflict detection. Retained BullMQ identity is not a permanent idempotency ledger: once a job is removed, the same ID can be added again. Consumer idempotency is consequently a separate boundary; it was not re-certified in this five-endpoint increment. [B02-S04:36–67; technical reference T3]

### E03-F01 — Diagnostic classification loses the actual failing dependency

**Classification:** Confirmed source-level diagnostic defect.
**Priority:** High for operability, not a demonstrated data-corruption defect.
**Owner:** moda_api.

The catch-all encompasses both the PostgreSQL-backed authenticator and queue operations, yet labels any unexpected exception `woocommerce.activity.queue.unavailable` / `enqueue_failed`. Therefore an authentication database exception is reported as a queue problem. The `boundedError()` helper creates a new generic error with only the original name, replacing message/stack/cause. [B02-S03:11–15,28–38,58–62]

The connection-readiness wrapper also discards a `connect()` rejection and uses a generic timeout/end error; the Redis error listener is empty. A logging change only at the HTTP boundary cannot recover an error already discarded there. [B02-S06:24–32,39–59]

**Recommendation:** Preserve the original exception/cause through the connection and route boundaries; identify the failing stage accurately; use the existing shared logger and its redaction facilities. Preserve safe generic HTTP bodies, bounded logging and no accidental credential/customer-payload disclosure. Do not log raw Redis URLs or SQL parameters. Do not introduce a competing service-local logger.

The current unit test deliberately asserts the generic replacement message, so correction requires changing that expectation while retaining the secret-redaction assertions. Add separate failures for authentication database outage, initial Redis connection failure and publication failure. [B02-S21:129–146]

### Validation and decision

Real-Redis integration source covers HTTP publication, retained deduplication, tenant separation and unavailable Redis. Its authentication database is stubbed; that suite is not proof of real PostgreSQL authentication-plus-Redis behaviour or credential-rotation races. [B02-S22:23–33,40–123]

**Decision:** Keep the thin database path and queue boundary. Correct diagnostics. No new schema, outbox or receipt table is justified by this endpoint review alone.

## E04 — POST /v1/woocommerce/whatsapp-consent

### Current flow and database operations

The HTTP route authenticates and parses a v2 event, then acknowledges only after the service transaction commits. The service normalizes the canonical recipient and calculates a digest before the transaction. Inside ReadCommitted with a 10-second timeout it:

1. Revalidates and share-locks Shop and installation with one joined query.
2. Takes an advisory lock for `(shop,eventId)`.
3. Takes an advisory lock for `(shop,canonicalPhone)`.
4. Looks up evidence by `(shopId,eventId)`; matching digest returns the original acknowledgement, changed digest conflicts.
5. On a new event, checks freshness and locks up to two active matching CustomerPhone rows to detect ambiguity.
6. Creates Customer plus CustomerPhone if no phone exists.
7. Updates consent state and appends matching immutable evidence.
8. Commits before returning.

[B02-S09:19–28; B02-S10:102–172]

| Path | Authentication | Raw calls inside transaction | Explicit total | Explicit business writes |
|---|---:|---:|---:|---:|
| Identical retained consent event | 1 | 4 | 5 | 0 |
| New event, existing active recipient | 1 | 7 | 8 | 2 |
| New event, no recipient yet | 1 | 9 | 10 | 4 |

The four new-recipient writes are Customer insert, CustomerPhone insert, consent update and evidence insert. They are not four duplicates. No billing/feature lookup, recovery creation, message or queue publication occurs in this service. Passive consent remains separate from sending eligibility. [B02-S10:79–98,139–169]

### Transaction decision — retain

Current CustomerPhone permission and matching immutable evidence must commit together. New-recipient creation must roll back with them if evidence insertion fails. The migration enforces this with evidence validation and a deferred commit guard. Keep both application checks and database integrity enforcement. Apparent overlap between them is not sufficient reason to remove either. [B02-S18:243–331]

The post-authentication locked installation recheck is not a redundant repeat of bearer authentication: it validates the principal's observed credential version and active Shop/installation for the write's transaction. Keep this boundary. [B02-S01:38–75; B02-S10:23–44]

### E04-F01 — Duplicate acknowledgements wait for an unnecessary recipient lock

**Classification:** Confirmed lock-before-duplicate path; optimisation candidate, not yet implemented.
**Priority:** Medium.
**Owner:** moda_api.

The duplicate branch uses only the installation gate, event identity, payload digest and recorded evidence. It does not consult current phone state, but the recipient advisory lock has already been acquired. [B02-S10:111–129]

**Proposed order:** Keep the transactional installation gate → acquire event lock → read/validate evidence → return identical duplicate immediately. Only when no event exists should the code acquire the recipient lock, evaluate the new event's freshness, locate/mutate the phone and insert evidence. Keep event-before-recipient ordering on writes and perform freshness checks after any relevant lock wait.

This preserves the distinction between acknowledging an accepted historical fact and accepting a new consent action. Retrying an accepted GRANT after a later REVOKE or STOP must acknowledge the original event without restoring current consent or removing suppression. Keep digest conflict rejection, event serialization, first-recipient safety, and original revision/sequence in the duplicate result.

**Source-level target:** duplicate path 5 → 4 explicit database-client calls including auth. Fresh/existing-recipient write paths remain 10/8. No latency or throughput improvement has been measured.

Required tests: simultaneous identical events; conflicting payload under one event ID; duplicate after later REVOKE/STOP; duplicate while the recipient lock is held by another transaction; no evidence present under a held recipient lock must still wait before mutation; first-insertion races; unchanged freshness/order handling; revoked/rotated installation rejection. Test locking with deterministic barriers, not arbitrary sleeps.

### E04-F02 — Handled conflict wrappers discard original Prisma errors

**Classification:** Confirmed source-level cause-preservation gap for the handled branches.
**Priority:** Medium.
**Owner:** moda_api.

The catch converts P2002/P2034 to `WooConsentHttpError(409, consent_write_conflict)` without attaching the original error. The route logs that wrapper; it cannot recover the discarded original message/cause. Other unexpected errors are logged directly, so original-error logging is not wholly absent. [B02-S10:173–176; B02-S11:37–40; B02-S09:29–48]

Retain original errors and safe metadata through typed wrapping. Separately test real raw-SQL failures: Prisma documents a P2010 raw-query error path, so do not assume `$executeRaw` uniqueness/deadlock/trigger failures are all classified by P2002/P2034. The precise mapping in pinned Prisma 6.19.3 must be captured on the migrated database before choosing retry or HTTP classification. This is an unvalidated error-classification question, not a claim that a production race has been reproduced. [T4]

Do not automatically retry logical stale-action, changed-payload, ambiguous-phone or revoked-credential failures. Any transient database retry policy must be bounded and reuse the original request identity, not manufacture a fresh consent action.

### Schema/index observations

Evidence lookup has the unique `(shopId,eventId)` index. Phone lookup already has canonical and raw-phone lookup indexes; its `LIMIT 2` is deliberate ambiguity detection, not an accidental extra row. Do not replace it with arbitrary `findFirst` or global phone uniqueness. The same canonical number may belong to different merchants. Any new index requires actual plan/volume evidence. [B02-S16:305–309; B02-S17:2202–2205; B02-S10:54–76]

The application-level call counts omit trigger-internal reads, foreign-key checks and deferred validation. Query logging alone does not describe all server work. Preserve the canonical migrated-schema test runner rather than using `db push`. [B02-S18; B02-S27:45–61]

### Historical performance evidence — attributed, not rerun

The uploaded ARCH-046-API-007 task records a 24 October 2026 comparison at implementation head `b1ccf7842d1a6d732d900676d6e8c4250977b707`. Its v2 service-only sample reported:

| Scenario | Recorded client-observed SQL statements | Recorded transaction-client elapsed time |
|---|---:|---:|
| Fresh GRANT | 12 | 52.04 ms |
| Existing GRANT | 10 | 25.88 ms |
| REVOKE | 10 | 26.92 ms |
| Duplicate retry | 7 | 16.63 ms |

These figures come from the historical task report, not measurements made in this increment. The harness measures the client `$transaction` call, including transaction setup/round trips/commit, and excludes HTTP authentication/setup. They are single local observations, not p95, capacity, server-only latency or a baseline for the proposed new optimisation. The earlier comparison explicitly reports timings that did not improve in every scenario. [B02-S28:206–231; B02-S26:17–31,96–127]

### Validation and decision

Existing test source covers passivity without subscription, immutable evidence, exact evidence-tuple retrieval, tenant/recipient boundaries, replay, temporal ordering, concurrent decisions, real reconnect, STOP preservation and rollback of both existing/new recipients after evidence failure. [B02-S24–S25]

**Decision:** Retain ReadCommitted, write locks, atomicity and database guards. Optimise the duplicate-only branch and preserve original handled errors. No schema change proposed.

## E05 — GET /v1/woocommerce/customer-recovery-selection

### Current flow and operations

Authenticate → require WordPress admin attestation → parse canonical phone → begin ReadCommitted transaction → share-lock/read Shop → share-lock/read installation → acquire recipient advisory lock → select active matching CustomerPhone rows `FOR UPDATE` → format status. [B02-S12:18–30; B02-S13:24–49,84–89; B02-S15:14–39; B02-S35]

**Total:** 1 authentication model call + 4 raw calls = **5 explicit database-client operations**, with no business-state update. The response carries `noContactRevision`; POST requires it as its expected revision. The actual code uses **ReadCommitted**, not Serializable.

### E05-F01 — Read-only status uses the mutation's recipient locking path

**Classification:** Confirmed strong-lock use; optimisation candidate subject to read-consistency contract.
**Priority:** Medium; likely more important for contention than the one-call saving.
**Owner:** moda_api.

`read()` calls the same advisory-lock and `FOR UPDATE` phone-lookup path as mutation. Requests for the same recipient therefore serialize despite returning only status. Ordinary PostgreSQL snapshot reads do not need row-update locks; `FOR UPDATE` blocks conflicting writers/lockers. [B02-S13:24–49,84–89; T1–T2]

**Proposed narrow change:** Keep the existing short transaction and Shop/installation authorization recheck initially. Split the phone read from the mutation lookup. For GET, remove the recipient advisory lock and use an ordinary SELECT without `FOR UPDATE`, preserving tenant scope, active-phone filtering, canonical match and `LIMIT 2` ambiguity detection. Return the revision observed in that result.

This explicitly changes the read semantics to a committed statement snapshot, not a promise to wait for every concurrent recipient mutation to finish. A result can be superseded before the browser uses it, as is already possible after the current transaction releases its locks. POST must continue to re-read and check the supplied revision under mutation locks. A concurrent STOP or consent revocation must still win according to the write rules; GET's `phoneEligibleForRecovery` is never permission to bypass final send admission.

**Source-level target:** 5 → 4 calls including auth. Removing `FOR UPDATE` changes lock behaviour but does not itself remove a query. Further query consolidation is separate.

Validation must show two GETs do not serialize on the recipient lock; a GET can read the last committed phone version during an uncommitted writer; stale POSTs reject; changed/ambiguous phones still fail safely; and installation rotation/revocation cannot bypass the retained gate. The retained Shop share lock can still block the production STOP writer's Shop update lock. This proposal is not a claim of wholly non-blocking status reads.

### E05-F02 — Installation gate is a possible consolidation, not a useless recheck

The support-owned helper uses two statements for Shop and installation, whereas the consent service already uses a joined locked recheck. This is a potential additional one-call saving for selection GET and POST, but the two current reads are not duplicates: they validate different records. [B02-S15:14–39; B02-S10:25–43]

Do not change the shared helper globally during a five-endpoint review. An API-local bounded change must preserve lock ordering with reconnect/revocation/STOP, suspended-Shop errors, credential checks and tenant identity. A SQL JOIN's textual table order alone is not proof of equivalent lock acquisition. The conservative recommendation and 5→4 target above do not depend on this consolidation.

### Validation and decision

Existing selection integration tests cover GET output, ambiguity, tenant boundaries, changed phone, rotated/stale principal and revoked credentials. They do not establish the proposed non-locking read contract. [B02-S23:96–175]

**Decision:** Candidate to remove recipient write-style locks; retain transactional authorization until separately proven replaceable. No schema change required by this proposal.

## E06 — POST /v1/woocommerce/customer-recovery-selection

### Current flow and operations

Authenticate → require admin attestation → validate action/revision → start ReadCommitted → share-lock/read Shop and installation → advisory-lock recipient → lock active matching CustomerPhone → compare expected revision and policy → either return duplicate or update no-contact state/revision → return response from the locked state without another SELECT. [B02-S12:23–38; B02-S13:92–148]

A successful transition makes **6 explicit database-client calls** including auth; a duplicate makes **5**, with no UPDATE. The lone UPDATE is preceded by a revision/policy decision under a row lock. The expected revision is checked in service code; it is not currently an SQL `WHERE revision = expected` predicate. Do not remove the row lock while treating the existing UPDATE as a standalone compare-and-set statement.

### Transaction decision — retain

The fact that the path makes only one explicit business UPDATE does not make its transaction unnecessary. The transaction keeps the installation valid and the phone's read/check/write coherent. Re-enable requires current Woo GRANTED consent, merchant-owned suppression, and no authoritative CUSTOMER_STOP. The revision prevents a stale merchant command from overwriting a newer suppression choice. Identical immediate replay is a no-write result. [B02-S13:99–147; B02-S18:191–212]

Keep the recipient lock/row lock on mutations. Do not replace this with an unlocked read followed by an unconditional update. There is already no read-after-write to remove: the response uses the updated in-memory representation of the locked row. Do not add a second SELECT just for confirmation.

### E06-F01 — Original handled conflicts are lost here too

**Classification:** Confirmed cause-preservation gap in P2002/P2034 wrappers.
**Priority:** Medium.
**Owner:** moda_api.

`selection_write_conflict` is created without the original error. Preserve its cause and meaningful safe diagnostics while keeping client responses bounded. Apply the raw-query failure-mapping validation described for E04; do not indiscriminately retry stale revisions or reload the latest revision to force an originally stale command through. [B02-S13:149–152; B02-S14:39–42; B02-S12:45–61]

### Accepted boundary, not a newly invented defect

`RECORD_CUSTOMER_STOP` requires an opaque external evidence reference, but the current schema does not persist it. The existing API-005 accepted review explicitly records this as an intentional schema boundary: the API sets durable STOP and neither logs nor stores that external reference. Do not reopen this as an unexplained endpoint bug or add an evidence table under a query-optimisation change. [B02-S14:14–21,57–75; B02-S29:275–279]

### Validation and decision

Existing migrated tests cover suppress/re-enable, duplicate/stale commands, missing consent, STOP precedence, recipient/merchant separation and simultaneous merchant mutations. The same-number-across-merchants test is important and must remain. [B02-S23:96–199]

**Decision:** Retain the write transaction and no-reread result path; fix diagnostic cause retention. The shared two-query installation gate remains an optional later consolidation, not a reason to weaken authorization.

## Cross-cutting observation B02-X01 — Actual STOP coordination must be tested

The selection service comment says its recipient advisory lock is the same as customer STOP. The uploaded production Background STOP writer uses a different advisory-lock scheme: a SHA-derived signed bigint keyed by canonical number, then sorted Shop `FOR UPDATE` locks. The API uses a two-int advisory key based on shop plus `phone:<canonical>`. [B02-S13:24–28; B02-S30:10–27; B02-S31:28–53]

**This is not evidence that STOP protection is broken.** The API's retained Shop `FOR SHARE` conflicts with the Background writer's Shop `FOR UPDATE`, and the phone update/trigger also protects state. The important implication is that API recipient advisory locks alone are not the production cross-service coordination contract. Do not remove Shop locks on the assumption that both services use one recipient lock.

The inspected consent race test simulates STOP using the API-style advisory key and a direct SQL update; it is not an invocation of `writeLocalStop`. Keep it, but require a focused cross-service race against the real writer before accepting any change to shared Shop/recipient locking. This observation is bounded to the inspected tests; it does not assert that no other system test exists anywhere in the workspace. [B02-S24:137–165]

The read optimisation retains Shop locks, so it does not require a cross-repository lock-key redesign. No speculative Shared primitive or Background implementation task is created by this observation.

## Increment recommendations and validation order

| Finding | Proposed action | Classification | Priority |
|---|---|---|---|
| E03-F01 | Preserve original DB/Redis errors; classify failure stage; update diagnostic tests | Confirmed diagnostic defect | High (operability) |
| E04-F01 | Look up idempotent evidence before taking recipient lock | Proposed targeted optimisation | Medium |
| E04-F02 / E06-F01 | Preserve conflict causes; verify raw-SQL error shape on Prisma 6.19.3 | Confirmed wrapping gap; error mapping unvalidated | Medium |
| E05-F01 | Give GET a snapshot phone-read path without recipient advisory/FOR UPDATE locks | Proposed lock optimisation | Medium |
| E05-F02 | Consider consolidating transaction-local installation gate, with equivalent ordering/errors | Conditional consolidation | Lower, pending cross-endpoint review |
| B02-X01 | Correct lock explanation and validate actual STOP writer coordination | Confirmed documentation/test-boundary observation | Required for lock-boundary changes |

The first two query/lock changes are independent and bounded; neither justifies lowering isolation for mutation, adding billing lookups, weakening tenant isolation, removing append-only evidence, or adding a new datastore.

### Runtime validation status

**Not executed in this increment.** The snapshot API has no installed `node_modules`; Docker is unavailable. The available Node executable is v22.16.0 while the API declares 24.19.0. No packages or alternative Node versions were installed, and no test was reported as passed on the basis of historical task claims. No PostgreSQL/Redis containers were started, so none require cleanup.

Source evidence: all files reproduced in the increment-02 companion were byte-compared against the uploaded archive. API nested database schema and root database schema retain matching SHA-256 `45df5e44bdc1e7e29495e391a1754477f0df362c667d648f4b6893b6541f5c0d`.

Existing repository commands for the relevant validation are:

```bash
npm run test:arch035-woo-activity:unit
npm run test:arch035-woo-activity:redis
npm run test:arch046-woo-consent:unit
npm run test:arch046-woo-selection:unit
npm run test:arch046-woo-consent:postgres
```

The last runner already executes both consent and recovery-selection PostgreSQL tests using `prisma migrate deploy`; do not run its selection alias as a redundant second integration pass solely because both names exist. Run these in the canonical prepared API worktree after approved source changes, with focused new assertions for diagnostics, duplicate/read lock contention, rollback, actual STOP coordination and emitted-query counts. The benchmark's legacy v1 comparison is historical context, not the right performance baseline for a future change to current v2; compare current-v2 versus patched-v2 under identical migrated fixtures.

Do not add parallel generic telemetry: reuse approved query/transaction instrumentation and the shared logger, keeping raw credentials, recipient values, SQL parameters and customer payloads out of exported diagnostics. Record caller-visible outcome, transaction/client elapsed time and lock wait separately, and do not claim load capacity from a single local scenario.

### Review frontier

Reviewed: E01 connect; E02 installation probe; E03 activity; E04 consent; E05 selection GET; E06 selection POST.
Remaining from the original inventory: **55 endpoints**.
Next proposed bounded group: shop-brand POST, recovery-restore resolve POST, read-authorizations POST, read-authorization GET and read-authorization DELETE. No next-group review or implementation is claimed in this increment.

## External technical cross-checks for increment 02

These sources verify database/library semantics, not application behaviour. Checked 1 November 2026.

- **T1 — PostgreSQL 17 Explicit Locking:** `https://www.postgresql.org/docs/17/explicit-locking.html` — row-lock conflicts, transaction lock lifetime and consistent lock acquisition.
- **T2 — PostgreSQL Transaction Isolation:** `https://www.postgresql.org/docs/17/transaction-iso.html` — ordinary Read Committed SELECT is a committed statement snapshot; a read does not reserve that state for later commands.
- **T3 — BullMQ Job IDs:** `https://docs.bullmq.io/guide/jobs/job-ids` — duplicate IDs are scoped to retained jobs in a queue; removal permits re-addition.
- **T4 — Prisma Error Reference:** `https://www.prisma.io/docs/orm/v6/reference/error-reference` — P2010 raw-query failure and P2034 transaction conflict/deadlock categories. This version-six reference does not by itself prove exact failure mapping for the pinned runtime; integration verification remains required.

## Artifact revision history

- r01: E01 installation connection review.
- r02: Retains E01 verbatim apart from document-level status/evidence metadata; adds five endpoint reviews, source-count tables, historical measurement attribution, lock/error findings and validation boundaries. No application patch or acceptance is implied.


---

# Increment 03 — five more endpoints (E07–E11)

**Review date:** 1 November 2026.
**Scope:** ShopBrand, restore resolution, and the start/status/local-revoke REST-read-authorisation endpoints. Callback and return handlers were inspected only where needed to understand these flows; their endpoint reviews remain for the next increment.
**Progress:** 11 of the original 61 method/path combinations reviewed; 50 remain.
**Status:** Static source findings, source-derived failure scenarios and recommendations. No implementation acceptance, runtime reproduction or measured performance result is claimed.
**Evidence:** `woocommerce-api-database-review-03-source-evidence.txt`, references B03-S01–B03-S36, with original source line numbers and per-file SHA-256. The accompanying JSON manifest records byte-for-byte verification against the original uploaded ZIP.

## Increment summary

The highest-priority issue is local read-grant revocation, not query count. The service updates old pending attempts after reconnect, but the canonical attempt trigger rejects their old credential versions; this can abort the entire revoke transaction. The revoke operation also lacks transaction-local validation of the request's credential version. Both are source-supported correctness risks needing deterministic migrated-PostgreSQL regression tests.

| Entry | Method and path | Successful explicit database-client calls, including authentication | Transaction assessment |
|---|---|---|---|
| E07 | POST `/v1/woocommerce/shop-brand` | 7 first creation; 5 later update; 4 duplicate/stale acknowledgement | Retain ReadCommitted transaction and existing coordination; remove first-creation reread |
| E08 | POST `/v1/woocommerce/recovery-restore/resolve` | 4 eligible; 2 early-ineligible | Retain read-only flow and deliberate post-offer eligibility recheck |
| E09 | POST `/v1/woocommerce/read-authorizations` | 3 with database-backed security configuration; 2 with injected/static config | One guarded insert is atomic; no blanket transaction solely to reduce calls |
| E10 | GET `/v1/woocommerce/read-authorization` | 2 current ACTIVE grant; 3 fallback/latest-attempt path | Retain non-locking status projection; inspect fallback index access |
| E11 | DELETE `/v1/woocommerce/read-authorization` | 3 on a successful non-retried path | Retain Serializable two-write atomicity; correct generation/lifecycle handling |

Counts include explicit `$queryRaw`/`$executeRaw` lock operations and model methods. They exclude `$transaction` setup, BEGIN/COMMIT/isolation commands, relation expansion, trigger-internal SQL, retries and provider work. A bulk update can touch many rows and fire many triggers despite being one client call. No latency reduction is inferred from these counts. Relevant sources: B03-S01–S14.

## E07 — POST /v1/woocommerce/shop-brand

### Current flow and why the transaction is justified

HTTP authentication precedes bounded request parsing. The service rejects invalid/far-future `observedAt`, then opens a ReadCommitted transaction with a 10,000 ms timeout. Inside it the service locks and validates Shop (`FOR UPDATE`), locks and validates installation (`FOR SHARE`), locks/creates ShopBrand, compares source observations and updates the brand/media state. The route acknowledges only after the transaction completes. There is no image download, R2 upload or queue publication in this transaction. [B03-S01:42–60,124–202; B03-S02:19–29]

The existing-row path is a real read/compare/merge/write operation. Media source generations, timestamps and the worker-owned ready/work state share a JSONB object. Preserve the ShopBrand row lock so a worker's completed role is not overwritten by a snapshot merger using stale JSON. Preserve the separate installation revalidation; the earlier bearer check does not establish its state through commit. The Shop lock presently also serialises first insertions for a shop. Do not weaken this lock protocol as a side effect of a small reread optimisation. [B03-S01:100–138,150–202; B03-S15:201–248]

### Counts and decision table

| Path | Authentication | Shop + installation locks | Brand work | Total |
|---|---:|---:|---:|---:|
| First snapshot, no ShopBrand row | 1 | 2 | SELECT + create + SELECT + UPDATE = 4 | 7 |
| Existing brand, newer snapshot | 1 | 2 | SELECT + UPDATE = 2 | 5 |
| Duplicate or older observation | 1 | 2 | SELECT = 1 | 4 |

### E07-F01 — Create result discarded before an immediate reread

**Classification:** Confirmed source-level redundant result-fetch pattern; proposed optimisation. **Priority:** Medium. **Owner:** moda_api.

`lockOrCreateBrand()` first SELECTs the row; when absent, it calls `tx.shopBrand.create({ data: { shopId } })`, discards the result and calls the lock SELECT again. Instead, return the created row with an explicit projection matching `BrandRow`. The transaction already owns its insertion and retains the Shop coordination lock. Preserve the initial existing-row lock, defaults, application-generated ID and unique shop relationship. [B03-S01:124–138; B03-S12:195–219]

Target: **7 -> 6 explicit calls on first creation only**. Existing-row and duplicate paths remain 5 and 4. PostgreSQL's RETURNING mechanism supports obtaining inserted values without an extra SELECT; inspect the generated Prisma SQL and selected shape when implementing. [External cross-check X03-1]

The unit-test create stub currently returns no object; it must return a realistic created row when this change is made. This is a test-double update, not a reason to retain production rereads. [B03-S16:24–36]

### Retained writes and non-findings

A later observation with identical image source identity still advances `observedAt`/refresh metadata, while retaining the generation and ready/work data. Removing that write solely because the URL is unchanged would change ordering: an older conflicting observation could later appear current. Exact duplicate/older observations already return without an UPDATE. Event ID is not the deduplication contract; same timestamp plus different source/presentation data is rejected. [B03-S01:102–120,154–198]

The route retains original exception name/message/stack/cause for unexpected failures; this is not the generic-error replacement defect seen in authorisation start. Prisma-specific code/meta are not explicitly projected there; safe structured code retention can be aligned with the platform logging policy without logging complete query parameters. [B03-S02:30–49; B03-S32]

### Validation

Existing unit and full-migration PostgreSQL tests cover source generations, duplicate/stale observations, equal-timestamp conflicts, metadata-only changes/removal, HTTP tenant/status authentication and simulated worker concurrency. Before accepting F01, add exact first-create call-budget assertions, rollback after a late write failure and simultaneous first-create requests from an empty state, while retaining the worker/newer-observation scenario. [B03-S15; B03-S16; B03-S22:48–56]

**Decision:** Retain the transaction and ordering semantics; eliminate only the reread of the just-created row in the first change.

## E08 — POST /v1/woocommerce/recovery-restore/resolve

### Current flow and counts

The route authenticates, rejects query parameters and validates the v1 request. A joined raw SELECT reads runtime lifetime configuration, the requested shop-scoped latest-generation recovery, Shop/installation eligibility and conversation ID. Unsupported or ineligible snapshots stop here. Eligible requests read the confirmed sequence-one offer/message relation, then repeat the joined recovery/config read and revalidate before building the v1 response from the final snapshot. [B03-S04:45–118; B03-S05:23–83; B03-S06:21–36]

Successful path: authentication (1) + initial recovery/config read (1) + confirmed-offer model call (1) + final recovery/config read (1) = **4** explicit calls. An early denial costs **2**. A later denial or offer failure has already incurred additional work. Neither service writes durable state. The current offer-reader implementation is database-only; no MCP/provider request is performed here. [B03-S09:87–90]

### Transaction assessment — do not remove the final read

The two recovery queries look identical but serve different times in the request. The final read catches completion/cancellation/expiry, newer generation, installation rotation/revocation and changed recovery lifetime after offer loading; it also ensures conversation identity is unchanged. The actual API-003 task explicitly requires this recheck, and a unit test simulates completion between reads. [B03-S04:64–73,121–157; B03-S17:196–217; B03-S27:44–49]

Retain the current no-write flow and recheck. A long RepeatableRead transaction would retain an earlier snapshot rather than automatically strengthen the fresh-state check. Any future single-statement projection must deliberately redefine and test the consistency point; it is not a mechanical deletion of duplicate SQL. The response is still a point-in-time authorisation, not a reservation preventing all later changes at the merchant site. [External cross-check X03-2]

### E08-F01 — Dedicated PostgreSQL suite uses a reduced schema

**Classification:** Confirmed validation boundary, not proof that resolver SQL is wrong. **Priority:** Required for any query/schema optimisation. **Owner:** moda_api (integrated validation owner where needed).

The runner does not deploy all migrations. The integration test creates simplified tables itself, adds one targeted real migration to remove the old lifetime CHECK, and exercises the real resolver/offer reader against those tables. This is useful SQL-behaviour coverage, but it is not full canonical-schema acceptance or representative query-plan evidence. [B03-S23:35–40; B03-S19:76–148]

Add a full-migration fixture path for schema/index/query-plan work and the relevant concurrent state-change cases. Keep the targeted lifetime migration rehearsal as useful separate coverage. Do not label historical task acceptance or these test sources as a test run in this review.

### E08-F02 — Safe redaction also removes diagnostic codes

**Classification:** Confirmed diagnostic information loss. **Priority:** Medium. **Owner:** moda_api.

`safeErrorDetails()` retains a bounded/redacted name and message with redaction/truncation flags, which is useful; it is not wholly generic substitution. However it drops original structured code, relevant metadata and cause. Its broad uppercase/digit-token regex would also redact a code such as `P2010` from message text. [B03-S06:55–74]

Preserve an allowlisted original Prisma/driver code and safe cause/response details as structured fields, alongside the redacted source message, through the existing Shared logger. Do not relax token, URL, coupon, email or phone redaction. Add tests for both retained safe diagnostics and absence of injected secrets. The present test checks the latter and retention of a harmless message prefix, not structured database code preservation. [B03-S18:127–146; B03-S32:299–354]

### E08-F03 — Two duplicate index pairs surfaced in this read path

**Classification:** Confirmed duplicate key definitions in the snapshot; schema optimisation candidate pending deployed-catalogue validation. **Priority:** Medium/lower than revoke correctness. **Owner:** moda_database.

The canonical Prisma model and migration history declare both a unique and a non-unique B-tree index over exactly the same keys:

| Table | Keys | Unique index to retain | Non-unique duplicate candidate |
|---|---|---|---|
| commerce.CheckoutRecovery | shopId, checkoutToken, generation | CheckoutRecovery_shopId_checkoutToken_generation_key | CheckoutRecovery_shopId_checkoutToken_generation_idx |
| whatsapp.Conversation | checkoutRecoveryId | Conversation_checkoutRecoveryId_key | Conversation_checkoutRecoveryId_idx |

[B03-S12:390–391,550–551; B03-S30:184–187; B03-S31:906,921]

The unique indexes already provide a lookup index as well as integrity. Before removing anything, compare actual definitions/validity/dependencies/statistics in a disposable migrated database and deployed catalogue, and check broader workloads. Preserve all uniqueness and the distinct active-generation partial index. Make any approved removal through a new canonical Database migration and Prisma schema reconciliation; never delete or rewrite the old migrations or mutate API's nested schema independently. No space or write-performance savings were measured. [External cross-check X03-3]

**Decision:** Retain both recovery reads for their specified freshness semantics; address diagnostics/test coverage and carry duplicate-index cleanup as a bounded Database candidate.

## E09 — POST /v1/woocommerce/read-authorizations

### Current flow and transaction decision

After authentication the service loads current security configuration, creates a random callback bearer and its digest, inserts one ten-minute PENDING attempt bound to installation/shop/credential version, then returns the provider authorisation URL. The insert returns ID/expiry directly: there is no read-after-create. The endpoint does not contact WooCommerce and does not mint the outgoing grant; that is the callback's separate work. [B03-S07:55–98; B03-S08:69–89]

With the database-backed composition, `operationConfig()` calls the uncached PlatformConfiguration reader once. Thus the normal count is **3** (auth + security config + attempt insert), not 2. The injected/static configuration variant used by several tests costs **2**. Do not silently cache or replace current security configuration just to remove a read. [B03-S09:55–68; B03-S10:99–120; B03-S11:27–48]

A single INSERT plus its triggers is an atomic statement. The canonical attempt trigger rechecks installation/shop binding, Woo platform, active installation, credential version and expiry and acquires share locks. No extra transaction wrapper is justified merely by the number of writes. Trigger-internal queries are real work, even though they are excluded from explicit client-call counts. [B03-S13:127–181; External cross-check X03-4]

### E09-F01 — Every insert error becomes a misleading 409

**Classification:** Confirmed error-cause/classification defect. **Priority:** High for operability. **Owner:** moda_api.

The create promise ends with `.catch(() => { throw new WooReadAuthorizationError(409, "shop_unavailable"); })`. This discards the original exception and classifies all insert failures, including a database outage or unexpected constraint failure, as merchant unavailability. The route logs this replacement, so it cannot recover the original cause. [B03-S07:32–40,72–81; B03-S08:212–232]

Retain original cause and safe code/message/details. Map known identity/generation guards deliberately; let dependency/unexpected errors use the agreed server-error contract instead of fabricating a business conflict. If public status codes change, update the API-owned OpenAPI and plugin-facing expectations. No complete bearer URL, token digest, encrypted configuration or database connection string belongs in logs. [B03-S32; B03-S34:16–38]

### E09-F02 — Trigger revalidation does not cover current Shop status

**Classification:** Confirmed predicate gap; source-supported race requiring explicit lifecycle policy/test. **Priority:** Medium. **Owner:** moda_api, with moda_database only if the canonical guard changes.

HTTP authentication verifies Shop ACTIVE and the Woo-only identity. The attempt trigger's joined recheck selects Shop platform, but not Shop status or `shopifyShopId`, and does not compare those fields. Therefore do not describe it as a complete revalidation of the original authenticated principal. A Shop can be suspended after bearer authentication but before the insert; the trigger as written does not reject that condition. [B03-S03:38–65; B03-S13:159–174]

This is not a demonstrated cross-tenant credential disclosure or successful provider grant. Specify whether start must remain authorised through commit, then enforce the required current lifecycle predicates atomically and test a paused-authentication/suspension interleaving. This may require a small transaction-local gate or an owner-approved trigger change; an unrelated transaction wrapper alone adds no predicate. Cross-check callback's stronger commit contract during its next endpoint review. [B03-S26:64–65,100]

### Retention and duplicate starts

Each explicit start creates a fresh one-use attempt. There is no request-idempotency key here, and expiry does not physically delete a row. That alone is not a defect: returning an earlier bearer would require its recoverable value or a different start contract. Do not add speculative attempt reuse. Track attempt retention/cleanup separately from revocation; deleting an attempt referenced by a grant can have cascading consequences under the model. [B03-S07:61–98; B03-S12:2227–2255]

**Decision:** Keep the narrow guarded-insert design and current configuration source; fix error mapping and explicitly validate the lifecycle-recheck requirement.

## E10 — GET /v1/woocommerce/read-authorization

### Current flow and counts

After bearer authentication, status reads only grant shopId, credential snapshot and status. A current ACTIVE grant returns CONNECTED immediately. Otherwise it fetches the latest attempt for the installation/shop ordered by descending attemptSequence, then derives PENDING, REAUTHORIZATION_REQUIRED or NOT_CONNECTED and the provider-revocation flag. No credentials/ciphertext are selected and no state is written. [B03-S07:127–151]

Counts: **2** with current ACTIVE grant; **3** for the fallback. The second model read is not a duplicate: it provides attempt state not present in the grant.

### Transaction assessment

No row-update locks or Serializable transaction are justified for a display-only status projection. The two-step fallback is not a single snapshot and may observe a callback between reads. Status must never be reused as authorisation for an actual provider read; the provider-connection reader independently checks current installation/grant generation and state. [B03-S35:74–100]

If a one-snapshot status contract is required, a bounded joined/lateral projection is a candidate and could reduce fallback from 3 to 2 calls including auth. Preserve CONNECTED precedence and all tenant/version checks. Do not first add an exclusive lock or claim a read response stays valid after being sent. [External cross-check X03-2]

### E10-F01 — Latest-attempt access pattern has no matching composite index

**Classification:** Confirmed query/index mismatch; performance impact unmeasured. **Priority:** Low/medium depending on retained attempt volume and polling frequency. **Owner:** moda_database after query-plan evidence.

The fallback filters installationId + shopId and orders attemptSequence DESC LIMIT 1. Existing attempt indexes cover tokenDigest, globally unique attemptSequence, installationId/status/expiresAt, and createdAt. None combines tenant/installation equality with sequence ordering. Existing indexes can still be usable; do not claim a proven full scan. [B03-S07:140–144; B03-S12:2232–2245; B03-S13:55–62]

Compare EXPLAIN (ANALYZE, BUFFERS) for the generated SQL on representative multi-tenant/high-history fixtures with a candidate `(installationId, shopId, attemptSequence)` B-tree (backward scan for descending order), or the smaller `(installationId, attemptSequence)` where the established immutable installation-to-shop binding justifies it. Measure before choosing. Do not use a PENDING-only index as a semantics-preserving replacement: this query deliberately selects the latest attempt regardless of status before classifying it. [External cross-check X03-5]

**Decision:** Retain the non-locking fast path; validate an ordered fallback index before schema work. Query consolidation is optional, not required for correctness by the inspected display contract.

## E11 — DELETE /v1/woocommerce/read-authorization

### Current flow and why the transaction is necessary

After bearer auth, `revoke()` opens a Serializable transaction with a 6,000 ms timeout and at most three attempts for Prisma P2034. It marks unexpired PENDING attempts FAILED/locally_revoked, then marks the ACTIVE grant REVOKED. Both predicates use installation/shop, not the request's credential version. It returns only after commit and performs no provider deletion. [B03-S07:154–175,290–300]

There are **3** explicit database-client calls on a successful non-retried path, including authentication. There is no preliminary grant read or redundant read-after-write. Keep the transaction: disabling pending callbacks and revoking the selected local grant must not partially commit. Keep provider-side key deletion distinct; the API explicitly reports `providerRevocationRequired: true`. [B03-S33:24–28; B03-S34:50–58]

### E11-F01 — Stale pending attempts can abort revocation after reconnect

**Classification:** Source-supported deterministic failure scenario from current service and canonical trigger; not runtime-reproduced in this review. **Priority:** High. **Primary owner:** moda_api; involve moda_database only if transition policy changes.

Reconnection increments installation credentialVersion but does not cancel prior pending REST-read attempts. The revoke update selects all unexpired PENDING attempts for installation/shop, including earlier generations. The attempt BEFORE UPDATE trigger checks every affected row's credentialVersionSnapshot against the current installation, even when the transition is PENDING -> FAILED. A stale row therefore raises a guard exception. [B03-S14:123–161; B03-S07:159–168; B03-S13:136–171]

Reproduction contract for the required test:

1. At credential version 1, create attempt A and leave it PENDING and unexpired.
2. Reconnect to credential version 2.
3. Create attempt B and complete its callback, establishing a current ACTIVE version-2 grant.
4. Call revoke with the valid version-2 principal before A expires.
5. The current update includes A; the trigger rejects A's old snapshot. The transaction aborts before successful grant revocation, leaving the current grant ACTIVE.

The route does not falsely return success; an unhandled trigger error takes the server-error path. The defect is failure to revoke, not partial commit. PostgreSQL trigger exceptions execute within and abort their triggering transaction. [B03-S08:225–232; External cross-check X03-4]

Preferred narrow direction: after transaction-local authorisation, cancel the pending attempts belonging to the current credential generation—the ones capable of successfully minting a current grant. Treat older generations as permanently unusable and keep their eventual cleanup separate. Current callback and provider-reader checks already reject old generations. Update any wording promising all historical PENDING rows become FAILED, or obtain a deliberate Database-owned invalidation transition if that durable lifecycle change is required. Never remove the generation trigger or swallow its exception and proceed outside the transaction. [B03-S07:208–215; B03-S35:96–100; B03-S34:57]

### E11-F02 — Authenticated credential version is not revalidated inside revoke

**Classification:** Source-supported same-merchant stale-authorisation race. **Priority:** High. **Owner:** moda_api.

Unlike consent/brand mutations, revoke does not re-read/lock the current installation against the supplied principal inside its transaction. The attempt update uses each row's own version, not principal.credentialVersion. The grant trigger's non-replacement ACTIVE -> REVOKED branch returns before the installation/version check. [B03-S07:154–173; B03-S13:224–260]

A request authenticated with v1 can pause, a reconnect can create v2 and a new ACTIVE v2 outgoing grant, then the delayed old revoke can target that current grant using only the unchanged installation/shop IDs. Serializable isolation does not validate a credential value that is absent from the transaction's predicates; the earlier HTTP lookup is outside this transaction. [B03-S03:70–75; B03-S07:160–171; External cross-check X03-2]

Add one explicit, transaction-local current-principal gate with a defined lock order compatible with reconnect and callback. Validate Shop/installation state, identity and credential version. Preserve denial under retries: never silently substitute the new credential version for the old request. This may intentionally **increase** the explicit call count; correctness takes priority over the smallest number. Scope grant revocation so a current authenticated merchant can still revoke an unusable old stored grant rather than being blocked by its old snapshot.

### E11-F03 — Expiry while waiting is a cancellation edge case

**Classification:** Source-supported expiry-boundary risk; concurrency reproduction pending. **Priority:** Include in the correction's acceptance tests.

The service captures application `now` before updateMany and filters expiresAt > now. The trigger checks its own `clock_timestamp()` on every update, including FAILED cancellation. A selected row can expire during lock wait or statement execution, causing the whole revoke transaction to fail even with a current generation. This is distinct from F01. [B03-S07:158–167; B03-S13:147–149]

Test near-expiry and lock-wait interleavings. Do not claim merely replacing the timestamp with database time solves all lock-wait cases. Any solution must preserve callback expiry enforcement and grant/cancellation atomicity. A deliberate terminal-invalidation trigger policy, or a safely bounded retry of the entire authorised operation with a refreshed cancellation selection, needs owning-agent design and tests; no schema change is assumed or made here.

### Validation required before acceptance

Existing migrated-PostgreSQL tests cover ordinary callback/storage/replay/local revoke, newer-grant ordering and a stale callback after reconnect. They do not exercise F01's old-pending + new-active + revoke sequence in the inspected dedicated suite, nor F02's paused authentication followed by a new grant. The suite also uses a stub verifier; it is not a live-provider test. [B03-S20:44–46,56–117; B03-S24:43–46]

Required focused additions: F01 sequence; paused auth/reconnect/re-authorise/revoke; callback-versus-revoke in both orders; current pending attempt cancellation; duplicate revoke with no active grant; injected failure on the second write proving rollback of the first; near-expiry lock waits; bounded retry exhaustion with original diagnostics; suspended/revoked installation at the mutation gate. Use full migrations and deterministic barriers, not sleeps as proof of ordering. Keep all tests tenant-scoped and include two shops.

**Decision:** Retain Serializable atomicity. Fix revocation generation/lifecycle coordination before spending effort shaving its existing three calls.

## Prioritised register for this increment

| Finding | Action | Priority | Ownership |
|---|---|---|---|
| E11-F01 / F02 | Correct old-attempt revocation and stale-principal mutation | High correctness | API; Database consulted if transition guards change |
| E11-F03 | Reproduce/handle expiry during cancellation | Required in revoke correction | API + Database as needed |
| E09-F01 | Preserve original insert error and distinguish failure classes | High operability | API |
| E07-F01 | Return just-created brand fields, remove reread | Medium optimisation | API |
| E08-F02 | Retain safe original diagnostic code/cause with redaction | Medium operability | API |
| E09-F02 | Resolve/test current Shop-state gate through start commit | Medium correctness clarification | API; Database if guard changes |
| E08-F01 | Full-migration restore validation before query/schema optimisation | Validation gate | API |
| E08-F03 | Validate/remove duplicate non-unique indexes, retaining unique indexes | Measured schema follow-up | Database |
| E10-F01 | Measure latest-attempt ordered index candidate | Lower, evidence-dependent | Database |

No Shared contract, queue, Gateway infrastructure or new service is justified by these findings alone. Cross-repository source was read only to establish ownership and durable contracts. No task status is changed by this audit, including tasks already marked Complete in the snapshot. Source-supported new findings are not retroactive claims that historical tests failed.

## Runtime validation and provenance

No application tests, PostgreSQL integration suite, benchmark or EXPLAIN was executed in this increment. The available Node executable is v22.16.0; API package.json declares 24.19.0. API node_modules, Docker, psql and Git metadata are absent. No package installation, alternate Node selection, container launch, branch, commit or push was attempted. There are no new containers to clean up. [B03-S25 plus environment inspection]

All 36 source files in the new companion were byte-compared with the original ZIP. API nested database schema matches root Database schema with SHA-256 `45df5e44bdc1e7e29495e391a1754477f0df362c667d648f4b6893b6541f5c0d`. The archive SHA-256 remains `ee42bb83ee441ba9018779e760967a5bf87edcbc429eecc58699f1419863861b`.

Existing focused commands, to run in the correctly prepared API worktree/environment, are:

```bash
npm run test:arch049-shop-brand:unit
npm run test:arch049-shop-brand:postgres
npm run test:arch053-recovery-restore:postgres
npm run test:arch026-woo-rest-read:postgres
```

The general `npm test` script also includes the restore and REST-read unit suites. Running the current dedicated restore PostgreSQL command still has the reduced-schema limitation above; it is not made a full-migration test merely by invoking it. No tests are represented as passed here.

Only standalone report/evidence artifacts were generated. Application code, canonical schema/migrations, architecture/task files and all `_index.md` files remain unchanged. This is not an accepted implementation patch, so no patch/apply/commit/push instructions are fabricated.

## External technical cross-checks — not evidence of application behaviour

X03-1 — PostgreSQL 17, Returning Data from Modified Rows: `https://www.postgresql.org/docs/17/dml-returning.html`. INSERT/UPDATE RETURNING can replace a separate result-fetch query.

X03-2 — PostgreSQL 17, Transaction Isolation: `https://www.postgresql.org/docs/17/transaction-iso.html`. Statement versus transaction snapshots and Serializable guarantees; isolation does not add missing application predicates.

X03-3 — PostgreSQL 17, Unique Indexes: `https://www.postgresql.org/docs/17/indexes-unique.html`. Unique indexes provide lookup structures; an equivalent additional index is unnecessary for those same keys.

X03-4 — PostgreSQL 17, Overview of Trigger Behavior: `https://www.postgresql.org/docs/17/trigger-definition.html`. Triggers execute in the triggering transaction; exceptions abort its effects.

X03-5 — PostgreSQL 17, Indexes and ORDER BY and Multicolumn Indexes: `https://www.postgresql.org/docs/17/indexes-ordering.html` and `https://www.postgresql.org/docs/17/indexes-multicolumn.html`. Ordered LIMIT access, equality prefixes and backwards B-tree scanning; actual plans must still be measured.

These primary-documentation checks were made during this increment. They support technical interpretation, not a claim about deployed behaviour or completed testing.

## Next increment

Keep the five-endpoint cadence. The next natural group is the REST-read callback, REST-read browser return, merchant bootstrap, store-context update and store-category options. They remain unreviewed endpoints despite selective helper inspection above. Cumulative progress remains **11 reviewed / 50 remaining** from the original 61-route inventory.


---

# Increment 04 — callback, return and merchant read/context endpoints (E12–E16)

**Review date:** 1 November 2026.
**Progress:** Sixteen endpoint method/path combinations reviewed; 45 remain from the original 61-route inventory. This is the same inventory denominator used in earlier increments, not a newly expanded scope.
**Assessment:** Static source review. No application tests, live Woo requests, PostgreSQL measurements or reproduction of the interleavings below were executed.
**Evidence:** `woocommerce-api-database-review-04-source-evidence.txt`, B04-S01–B04-S52; its manifest records original-file hashes and excerpt ranges. Paths in the endpoint analyses are relative to `moda-interact-api/`, except paths beginning `docs/`.

## Batch summary and counting convention

| Entry | Method/path | Successful source-level database-client calls | Decision |
|---|---|---:|---|
| E12 | POST `/v1/woocommerce/read-authorizations/callback/:token` | 5 fresh with DB-backed security config; 4 with static config; 2 already-committed replay | Retain Serializable transaction; correct concurrent replay and lifecycle validation |
| E13 | GET `/v1/woocommerce/read-authorizations/return` | 0 invalid/missing attempt ID; 1 locale lookup; 2 when a signed-locale attempt also resolves DB-backed config | No transaction; keep informational/read-only boundary |
| E14 | GET `/v1/merchant/bootstrap` | 2, including installation authentication | Retain narrow read; no gratuitous transaction or write |
| E15 | PUT `/v1/merchant/store-context` | 2, including installation authentication | Keep single conditional Shop mutation; consider avoiding identical writes only if worthwhile |
| E16 | GET `/v1/merchant/store-categories` | 6, including installation authentication | Consolidate identity reads cautiously; establish one coherent profile/configuration snapshot |

The callback path segment is a secret bearer token, not a database attempt ID. The earlier inventory used the display placeholder `:id`; this is the same route, not an extra endpoint. `payload.user_id` carries the opaque attempt ID. Browser return is not installation-authenticated. Callback uses the bearer digest lookup rather than the reusable installation authenticator. [B04-S01:177–196; S02:52–58]

Counts are explicit Prisma model-method or raw-query calls. They exclude transaction-control commands, nested relation-query expansion, trigger-internal SELECTs/locks, connection management, and retries. Five client calls do not imply five SQL statements. In particular, the callback guards do additional database work and take share locks inside its apparently small transaction. The security configuration branch intentionally queries current environment-scoped configuration rather than using a process cache. [S01:55–58; S07:55–68; S08:99–120; S09:27–48; S26:127–281]

## E12 — POST /v1/woocommerce/read-authorizations/callback/:token

### Observed flow

The HTTP route checks token shape and a bounded, exact read-only credential payload. The service canonicalises/decodes the token, looks up its digest and checks `payload.user_id`. If the attempt already succeeded, it looks up the grant still associated with that attempt and acknowledges without re-verification or any update. Otherwise it requires PENDING, an unexpired attempt, matching installation generation, an active installation, and an active Woo Shop. [S01:177–215; S02:52–63, 101–137]

It then performs a bounded provider verification call, resolves the encryption configuration and seals credentials **before** entering the database transaction. The transaction consumes exactly one pending attempt, reads the selected grant's sequence and rotation version, and creates or rotates that grant. It is Serializable with a 6-second transaction timeout and at most three total transaction attempts for recognised P2034 failures. The provider call is not repeated by that transaction retry loop. [S01:217–300; S03:41–64]

The route returns HTTP 200 after the service commits. Its comment and route test explicitly record the native callback's HTTP-200 requirement. This review does not independently certify live WooCommerce delivery/key-deletion behaviour. [S02:58–63; S31:99–114]

### Transaction decision: retain

Attempt consumption and grant creation/rotation are one atomic security outcome. The migration binds consumption to the transaction ID and uses a deferred constraint trigger to require the matching committed grant. The grant guard enforces scope, installation generation and monotonic replacement. A single-use attempt cannot be consumed in one committed transaction and minted into a new grant in another. These guards are not redundant substitutes for ordinary foreign keys. [S26:125–281]

The existing-grant read supplies both the stale-attempt check and the required rotation version. It is not a gratuitous post-write reread. An unconditional upsert is not an equivalent replacement. No supported call-count reduction is proposed for this endpoint's normal commit path. Keep the provider request outside the transaction; do not hold database locks during Woo network verification. [S01:249–279]

### E12-F01 — Concurrent duplicate acknowledgement can differ from sequential replay

**Classification:** Source-supported interleaving; not reproduced here.
**Priority:** High for callback correctness.
**Owner:** moda_api.

The idempotent-success branch executes only before provider verification. The transaction retry callback closes over the original PENDING attempt. A zero-row consume becomes `authorization_conflict`; it never checks whether an identical request just completed the same attempt successfully. [S01:197–204, 240–255, 290–298]

A possible schedule is:

1. Requests A and B both read the same attempt as PENDING and both pass provider verification.
2. A consumes the attempt, creates its selected grant and commits.
3. B reaches its consume after A committed, or restarts after a serialization conflict.
4. B's PENDING update affects zero rows and returns a 409 conflict, while a later ordinary replay would take the success branch and return 200.

This does not establish a duplicate grant or a rollback of A: the transaction/guards still protect durable state. It does establish a mismatch in acknowledgement handling for an overlapping retry. The source's explicit 200 callback contract makes this worth resolving rather than treating the loser as an unimportant error. The checked PostgreSQL test covers sequential replay and replay after local revocation; it does not coordinate two overlapping callback invocations. [S29:56–117; S31:99–114]

Recommended correction: make the retried transaction decision or a bounded post-rollback resolution aware of a concurrently committed matching attempt/grant. Acknowledge only the verified durable replay outcome; never turn every conflict or database error into 200. Preserve rejection of superseded attempts and preserve the existing rule that a replay after local revocation does not reactivate a grant. Do not move the external verifier inside the transaction to accomplish this. Define the callback payload/replay acknowledgement policy explicitly, rather than silently changing the existing sequential-replay contract.

Required validation: barrier-controlled simultaneous identical callbacks, a callback arriving while A commits, an injected P2034 followed by durable replay, different-attempt rotation, no second rotation, stale generation, revoked-grant replay, missing/superseded selected grant, and exact HTTP status behaviour through the route.

### E12-F02 — Shop suspension during provider verification is not checked at commit

**Classification:** Confirmed missing field in durable guards; source-supported race, not reproduced.
**Priority:** High for lifecycle conformance.
**Owner:** moda_api; moda_database if the canonical trigger is strengthened. Related to E09-F02 and the revocation review, not an unrelated architecture.

The service checks `installation.shop.status === ACTIVE` in its initial read, before its provider request. Both attempt and grant guards later select installation credentialVersion/status and Shop platform, but **not Shop status**. Although those queries lock the Shop, a lock does not supply the missing status test. [S01:208–219; S26:159–170, 254–265]

If the Shop is suspended after the initial read but before the callback's transaction starts, the inspected transaction predicates/guards do not reject the new grant on that basis. The task's stated acceptance requirement is an active tenant for grant creation. [S47:64–70, 100–103]

Recommended correction: validate active Shop and current installation/generation at the durable mutation boundary, coordinated with reconnect/revoke and the existing lock order. Strengthening the canonical guarded query may avoid another application round trip; adding a transaction-local gate is also possible but must not introduce inconsistent lock ordering. Do not remove the existing version, scope, expiry or same-transaction constraints.

Impact qualification: the separate provider-connection reader checks Shop status before using a grant. This is a grant-lifecycle inconsistency, not evidence that a suspended Shop can currently perform an authenticated provider read. [S06:74–100]

Required validation: suspend while the verifier is paused, then release verification; assert no new successful attempt/grant commits. Also cover suspension after an appropriate transactional gate, reconnect during verification, installation revocation, rollback, and compatibility with E11 corrections.

### E12-F03 — The callback discards provider/database causes and conflates transaction failures

**Classification:** Confirmed error-preservation/classification gap.
**Priority:** Medium, required alongside lifecycle corrections.
**Owner:** moda_api.

Provider verifier errors are replaced with a new `WooReadAuthorizationError` without a cause. Unrecognised verifier exceptions are similarly replaced. The transaction catch converts all non-domain errors, including exhausted P2034 and unexpected database faults, into a generic 409 `authorization_conflict`. Route logging contains the wrapper, not the lost original exception. The lower-level verifier also substitutes reason-only errors for some DNS/socket/response failures. [S01:220–227, 282–285; S02:212–232; S03:85–94, 164 onward]

Retain safe public reason codes, but preserve the original error/cause plus allowlisted database/provider status/code metadata using the approved shared logging boundary. Classify recognised race/guard failures separately from dependency or unexpected persistence failures. Never log callback bearer URLs, consumer keys/secrets, Basic/OAuth headers or raw provider bodies. Do not create a competing generic logger. Configuration/encryption errors outside the transaction catch already propagate to the generic route failure branch; the gap is not a claim that every exception in this route is swallowed.

### Current validation evidence

The dedicated rest-read runner applies migrations, which is appropriate for these guards. Its three authorization integration scenarios cover ordinary commit/ciphertext, sequential replay, local revocation, newer attempt replacement, and a version change before callback entry. The verifier is stubbed in those database tests. The historical task reports four passing authorization/provider cases together; that is previous recorded evidence, not a new run or proof of the new race scenarios. [S29; S40; S47:136–154]

## E13 — GET /v1/woocommerce/read-authorizations/return

### Observed flow and transaction decision

This is an informational browser return, not grant authorisation. A missing or syntactically invalid `user_id` returns English without a database query. A valid ID triggers one narrow attempt → installation → Shop lookup for locale and tenant binding. When both a requested presentation locale and a proof are supplied, the service resolves security configuration and verifies the locale proof against the attempt and Shop. With database-backed configuration that is one additional model call. [S01:101–124; S04:57–84]

The renderer chooses approved/cancelled informational wording from `success`; it does not consume an attempt, update a grant or treat the browser as proof of approval. A lookup failure is logged and falls back to an English page. [S02:31–50; S05:4–5, 26–29, 106–114]

**No transaction or lock is justified for language presentation.** Keep the response available when locale lookup fails. Do not add a grant-status query to this page merely to display a language, and do not convert this browser path into a callback or status writer. The attempt lookup is necessary for the currently defined signed-locale binding and persisted-Shop fallback; the browser parameters alone are untrusted.

### E13-F01 — Reject obviously malformed locale proofs before loading secret configuration

**Classification:** Confirmed avoidable configuration lookup on malformed-input branch; optional optimisation.
**Priority:** Low.
**Owner:** moda_api.

`returnLocale` resolves configuration before calling `verifyWooReturnLocale`; that verifier then rejects unsupported locale, excessive proof length, malformed version/parts and invalid encodings before decrypting. A valid attempt with a nonempty but obviously malformed proof therefore still queries `commerce.connectionKeys` in DB-backed mode. [S01:119–121; S04:65–75; S09:35–39]

A small preflight using the same authoritative parser can reject structurally impossible proofs before requesting secret configuration. Do not duplicate cryptographic parsing rules or accept unverified locale values. Keep full authentication for syntactically plausible proofs and preserve the Shop-locale fallback. Savings apply only to this malformed-proof branch: 2 → 1 explicit calls with DB-backed config, not to normal valid-proof requests.

No caching, new table, schema change or broad key-management redesign is justified. The current English fallback on a configuration lookup failure is tested route behaviour; this review does not silently replace it with a different contract. [S31:157 onward; S32:34–88]

## E14 — GET /v1/merchant/bootstrap

### Observed flow

Installation authentication performs one model lookup and returns a minimal principal. The bootstrap service then makes one tenant-scoped Shop query, selecting identity/lifecycle fields, the four provider-neutral international-context fields, and bounded active/pending category identities. It checks Shop and profile-reference integrity, constructs the response, validates its schema and returns it. An absent profile remains absent; there is no lazy profile, billing, subscription or credit creation. [S10:21–75; S11:17–89; S12:25–53]

**Total: two explicit model calls, no business writes and no explicit transaction.** The second query is not a duplicate authentication query: the principal does not contain the response's context and category information. Some identity fields overlap deliberately for integrity validation; that alone does not justify returning extra sensitive/mutable business data from the reusable authenticator.

### Decision: retain

No proven redundant lookup or write was found in this endpoint. Do not widen every authenticated request's shared principal to avoid one bootstrap query, cache merchant state without a validity contract, or add a transaction simply because related records are selected. There is no client-side N+1 loop in this service, but nested Prisma relations must not be described as a guaranteed one-statement SQL JOIN. [S11:18–44; S27:1–6]

The response is a read model, not a durable permission to issue a later write. Preserve independent authentication/mutation gates on subsequent endpoints. A stricter coherent-snapshot requirement for nested bootstrap relations would require an explicit concurrency test and measured SQL inspection; it is not inferred from a single Prisma call.

The dedicated tests verify the explicit projection, empty-profile behaviour, malformed reference rejection and lack of side effects. They do not establish a runtime performance result. Their PostgreSQL runner has the migration limitation recorded under B04-V01. [S34; S35; S41:54–76]

## E15 — PUT /v1/merchant/store-context

### Observed flow and transaction decision

After authentication and request validation, one `shop.updateMany` conditionally writes four fields. The predicate includes Shop identity/domain/platform/status and a related installation match on ID, Shop, canonical URL, current credential version, ACTIVE state and null revokedAt. Zero matched rows produces a typed conflict. No read-before-write, result reread, billing operation, provider call or interactive transaction is present. [S14:18–46; S15:30–58]

**Total: two explicit model calls.** Keep this single conditional mutation rather than replacing it with a separate authorisation SELECT followed by an unconditional UPDATE. The task explicitly calls for one atomic Shop snapshot update and says a redundant interactive transaction is unnecessary. [S45:67–85]

The database operation is not transactionless: it still has the database/Prisma operation's own atomicity. The recommendation is not to add an application-owned multi-statement transaction without a new invariant requiring it.

### E15-F01 — Identical context PUTs still issue a matching UPDATE

**Classification:** Confirmed repeated-write pattern; potential cost reduction, not a semantic-idempotency failure.
**Priority:** Low/medium pending request frequency and duplicate-rate measurement.
**Owner:** moda_api.

Every accepted request issues the same update, regardless of whether all four values already match. The unit test explicitly calls the service twice and verifies identical operation objects. The integration test also repeats the PUT and deliberately excludes `updatedAt` when checking non-context field preservation. Shop declares `updatedAt @updatedAt`. [S14:19–45; S36:1–34; S37:31–40; S27:2144–2145]

The existing contract requires semantic idempotence—no second Shop/installation/billing/category creation—not zero SQL writes. Thus the implementation meets that stated aspect; avoiding identical writes would be an optimisation, not a correction to the business contract. [S45:83, 119–124]

Do not insert a preliminary SELECT on every PUT simply to avoid some updates. If duplicate frequency warrants a change, prefer an atomic operation that distinguishes **updated**, **authorised and already equal**, and **invalid/stale principal**, with null-safe comparisons. Both updated and already-equal must retain the successful 204 response. Merely adding a value-difference predicate and keeping `count !== 1` as an error would incorrectly turn legitimate identical requests into 409s. Equally, interpreting every zero-row result as success would weaken authorisation.

This recommendation is about writes avoided, not fewer model calls. Retain current behaviour unless the write saving is worth any added implementation/query complexity. Measure actual SQL, rows updated, duplicate ratio and `updatedAt` behaviour before asserting a saving. Continue to clear fields on explicit nulls and never manufacture a second caller-supplied tenant identity.

### Concurrency and diagnostic qualification

The current integration test proves stale-version and revoked-state rejection when those changes complete **before** the update is invoked. It does not pause a real update behind a lock while reconnect/revoke changes installation state. A relation predicate is not evidence of a lock on the related installation for the full duration. Do not overstate the source comment's through-commit guarantee without testing the emitted SQL and interleavings. This is a validation question, not a reproduced bypass. [S37:54–61; S14:26–37]

Unexpected persistence errors propagate unchanged through the service and the route logs original name/message/stack/cause. This is better than the callback's exception replacement and should be retained; no generic diagnostic rewrite is proposed here. [S15:41–58; S36:58–63]

## E16 — GET /v1/merchant/store-categories

### Observed flow and costs

After one installation-authentication lookup, the service rechecks Shop and installation through two separate queries started in parallel. Once valid, it reads the selectable catalogue plus the Shop profile and active environment-specific configuration. The profile and active-configuration reads themselves run independently in `Promise.all`. [S18:15–49; S21:15–51]

The service's five model calls are: Shop, installation, category catalogue, Shop profile, and active SHOP configuration. Including authentication gives **six**. Parallelism does not eliminate database calls. The unit test explicitly asserts five service calls, including for an empty profile. [S38:20–65]

The catalogue fetches at most 101 candidate categories and 51 mappings per category to detect its 100/50 limits, sorts choices deterministically, limits translations to selected fallbacks, and filters out invalid/default-template combinations. Profile mapping IDs come from prompt provenance; prompt text is not returned in the wire response. Preserve these bounds and integrity checks. [S20:5–72; S21:52–84; S22:4–23]

### E16-F01 — Profile and active mapping provenance can be assembled from different commits

**Classification:** Source-supported mixed-snapshot risk; not reproduced here.
**Priority:** Medium correctness issue.
**Owner:** moda_api.

`readStoreCategoryProfile` combines a `commerceShopProfile.findUnique` result with a separate `commerceAgentConfiguration.findMany` result without a shared snapshot. The actual category writer updates active prompt configuration and profile category/generation in one Serializable transaction. The writer is examined here only to establish the read-side consistency boundary; POST category selection is still a future endpoint review. [S21:15–51, 67–79; S24:70–125; S25:98–110]

Possible schedule:

1. The GET's profile query observes active category A and generation 5.
2. Category publication atomically commits category B, generation 6 and B's active revision.
3. The GET's configuration query observes B's revision/provenance.
4. The assembled response reports category A/generation 5 but computes active mapping IDs from B. `selectedMappingIds` returns an empty list on category mismatch. If the update stays within category A but changes mappings, the response can instead pair old generation 5 with new mappings.

This is not a partial writer commit or cross-tenant leak. It is a potentially incoherent read response assembled from two legitimate committed views. The current provenance validation does not make those independent reads atomic. [S22:5–12]

Recommendation: obtain the correlated profile/configuration/provenance using one actual SQL statement, or a narrowly scoped read-only RepeatableRead snapshot covering all queries used to assemble that projection. A plain default ReadCommitted transaction is not sufficient to guarantee a common snapshot. Do not add `FOR UPDATE`, recipient locks or serialise all merchant GETs. A single Prisma method with nested relations must be verified as a single SQL statement before using it as the snapshot guarantee.

Trade-off: a read-only snapshot adds transaction/pool duration and serial execution on one connection; combining queries can increase SQL/projection complexity. Pick the smallest tested solution. It is reasonable for an available global catalogue and the tenant profile to be separately current display snapshots if that is the documented contract, but the profile category/generation and its selected mapping provenance should describe one coherent state. Catalogue eligibility is revalidated on mutation; the GET is not a permission token.

Required validation: coordinate a real publication between reads for different-category and same-category mapping changes; include no-profile → first selection, pending → active transition, environment isolation, and a larger bounded catalogue. Assert coherent old or coherent new data, not a mixture. Existing static-fixture tests do not cover this interleaving. [S38:80–115; S39:55–76]

### E16-F02 — Separate Shop and installation rechecks can be consolidated

**Classification:** Confirmed two-query validation shape; conditional optimisation.
**Priority:** Medium/low after snapshot correctness.
**Owner:** moda_api.

Use one tenant-bound identity projection for the service-level revalidation instead of two independent model reads, preserving every existing ID, domain, platform, Shop-status, installation-status, version and revokedAt check. Do not delete the revalidation merely because authentication already happened. Preserve the guarantee that failed identity validation stops catalogue/profile fetching. [S18:17–41; S38:102–108]

Source-level target is six → five client calls, if the consolidation is implemented as one model/raw call. A nested Prisma projection might still emit multiple SQL statements; actual SQL savings and consistency must be measured. Do not promise lower latency simply from this count or expand the shared authenticator to always fetch category business data.

### E16-F03 — Full prompt text is fetched for a boolean eligibility check

**Classification:** Confirmed internal over-fetching candidate; not a prompt disclosure.
**Priority:** Low pending payload/query evidence.
**Owner:** moda_api; no new schema justified yet.

The catalogue loads `defaultTemplate.promptText` but only uses `promptText.trim()` to determine nonempty eligibility. The wire response returns selected template metadata, not the text. This may transfer unnecessary large text across the database/application boundary, even with bounded category row counts. [S20:24–26, 50–52, 66–71]

If measurements show a meaningful cost, return an equivalent eligibility projection or use a correctly constrained query. Preserve the exact current whitespace semantics: replacing JavaScript trim with `promptText != ''`, or a database trim with different character handling, would change which templates are selectable. Avoid adding a second per-category query or N+1 fetches; do not materialise/cache a second source of template eligibility without a demonstrated need.

## B04-V01 — Validation coverage and environment

**Confirmed harness difference:** the REST-read authorization runner deploys migrations, while the dedicated bootstrap, store-context and category-read suites are invoked by the installation runner after `prisma db push`. The separate migration-backed cross-domain runner covers recovery policy and billing webhook receipts, not these three merchant suites. [S40:43 onward; S41:54–76; S42:13–16]

The international-context migration contains a country-code CHECK not represented solely by Prisma string length, and the authorization migration contains essential runtime triggers. Tests on db-push-created tables are useful but not equivalent to full migrated-schema evidence. Extend relevant acceptance to a disposable migration-backed pg17+pgvector database; adapt fixtures to canonical constraints rather than weakening migrations. [S26; S28]

Current environment verification: Node is available at v22.16.0; API package declares Node 24.19.0, Prisma 6.19.3 and Shared 3.1.0. Installed API node_modules, Docker and psql are unavailable. No toolchain was installed/replaced, no database/container was started, and no runtime suite was claimed as executed. The snapshot has no .git metadata for this extracted review; no developer branch/worktree/SHA or submodule pin is invented. Source identity is the archive and per-file hashes. [S43]

Validation completed in this increment is source inspection, route/helper/migration cross-checking, actual current-environment availability checks, and byte-for-byte verification of all 52 evidence sources against the uploaded archive. There are no new measured SQL counts, latency distributions, pool/lock metrics, benchmark results, query plans or live-provider observations.

### Focused acceptance requirements for future implementation

| Area | Required evidence before accepting a correction |
|---|---|
| Callback replay | Overlapping identical callbacks, transaction retry, selected-grant identity, superseded attempt, revoked replay, no second rotation, exact HTTP 200 acknowledgement only for an accepted durable outcome |
| Callback lifecycle | Shop suspension during paused provider verification; reconnect/revoke at the boundary; rollback leaves attempt/grant consistent; compatible lock order |
| Callback diagnostics | Original provider/database errors retained and classified, with bearer/keys/headers/body redaction; no blanket successful acknowledgement on an infrastructure error |
| Return page | Valid proof still verified; malformed proof avoids optional config work; missing/invalid ID no query; fallback and no-writes preserved |
| Bootstrap | Same bounded response and empty-profile handling; unchanged database state; canonical migrated schema; no assertion that one model call equals one SQL |
| Store context | Equal/non-equal/null-clearing paths, no-op versus stale distinction, conflicting credentials, real lock-wait/reconnect interleavings, timestamp semantics and measured duplicate/write rate |
| Category read | Coherent profile/configuration across publication, same-category mapping update, empty/pending profiles, environment/tenant isolation, bounds, whitespace eligibility, SQL/query/pool measurements |

Use only actual repository-declared scripts and focused test files after dependencies and a disposable runtime are available. The existing `npm run test:arch026-woo-rest-read:postgres` covers authorization through the migrated runner. The three merchant suites currently run via `scripts/test-woocommerce-installation-postgres.mjs`; do not call that migrated coverage. A migration-backed extension is a proposed validation change, not a command that already exists for these suites.

## Priority and ownership summary

| Priority | Findings | Proposed treatment |
|---|---|---|
| High | E12-F01, E12-F02, alongside earlier E11 findings | Correct callback acknowledgement/lifecycle behaviour with deterministic races before performance work |
| Medium | E16-F01; E12-F03 | Fix coherent read semantics and preserve actual diagnostic causes |
| Conditional optimisation | E16-F02, E15-F01 | Consolidate identity lookup; avoid identical context updates only with correct outcome distinction and measurable benefit |
| Low | E13-F01, E16-F03 | Avoid malformed-proof config loading and unnecessary prompt-text transfer if worthwhile |
| Retain | E14 and the stated correct portions of other endpoints | No mandatory refactor simply to lower a call count |

These are review recommendations, not accepted implementation tasks. API owns service/query/HTTP corrections. Database owns any canonical trigger or schema/index change. No new Gateway, Background, queue, outbox, caching service or infrastructure mechanism is justified by this batch. Do not opportunistically change the category mutation endpoint before its own review. No architecture/task statuses or `_index.md` files were edited.

## External technical cross-checks — distinct from application evidence

Only primary PostgreSQL/Prisma documentation was consulted to check database mechanics; it is not evidence that application tests passed or that a proposed race has been reproduced.

- PostgreSQL 17, Transaction Isolation (`https://www.postgresql.org/docs/17/transaction-iso.html`): ReadCommitted statement snapshots versus RepeatableRead consistency; transactions do not supply omitted business predicates.
- PostgreSQL 17, UPDATE (`https://www.postgresql.org/docs/17/sql-update.html`): matching unchanged rows count as updated; conditional updates need an explicit no-change outcome contract.
- Prisma ORM v6, Transactions (`https://www.prisma.io/docs/orm/v6/prisma-client/queries/transactions`): P2034 retry handling and per-transaction connection/parallelism constraints.
- Prisma ORM v6, Query optimization (`https://www.prisma.io/docs/orm/v6/prisma-client/queries/query-optimization-performance`): a Prisma relation read and its underlying SQL statement count are not synonymous.

The snapshot's actual Prisma version remains 6.19.3. No recommendation depends on adopting a newer major version or treating contemporary documentation defaults as automatically enabled in this schema.

## Next increment boundary

Continue from the original inventory with POST `/v1/merchant/store-category`, GET/PUT `/v1/merchant/feature-preferences`, and GET/PUT `/v1/merchant/recovery-policy` (five endpoints). The related category writer was inspected in this increment solely as evidence for E16; it is not marked reviewed.

---

# Increment 05 — five more endpoints (E17–E21)

**Review date:** 1 November 2026.
**Scope:** Category selection, feature preferences GET/PUT, recovery policy GET/PUT.
**Progress:** 21 endpoint method/path combinations reviewed; 40 remain from the original 61-route inventory.
**Status:** Static source review and proposed corrections/optimisations, not implementation acceptance.
**Evidence:** `woocommerce-api-database-review-05-source-evidence.txt`, identifiers B05-S01–B05-S47; original file line numbers follow the vertical bar. Its manifest verifies every included source against the exact uploaded ZIP.

## Executive assessment

Retain all five transaction boundaries in this batch. The category mutation publishes related durable state atomically; the two settings GETs deliberately use Repeatable Read without row-update locks; settings PUTs use Shop-scoped mutation coordination and revision checks. None should be made nontransactional simply to lower a count. There are specific avoidable queries on category publication, excessive projection breadth in settings reads, linear write cost in bulk feature changes, and a confirmed timing-attribution defect. Original handled database errors are also lost at three service catch boundaries despite downstream logging.

No new database schema/index, queue/outbox, distributed cache or infrastructure is justified by these findings. These recommendations are not implemented. Potential global-catalogue interleavings are explicitly labelled validation/consistency questions, not reproduced privilege violations.

## Scope and contract authority

E17 follows the existing `ARCH-026-API-006` category/prompt publication contract. Feature preferences follow accepted `ARCH-035-API-014`, not superseded `ARCH-035-API-003`. The latter's historical 100-ID specification must not be treated as the current limit or revived as a corrective task. The current runtime/OpenAPI allow 1,000 distinct changes, also subject to the 65,536-byte request limit. The current feature task's separate paid-plan fixture was explicitly waived; this review does not reopen that waiver. [B05-S21; B05-S22:35–45, 185–216; B05-S23:202–222; B05-S24:1–21, 197; B05-S10:2–5, 53–70; B05-S40]

Recovery policy uses the accepted ARCH-035 policy boundary extended by ARCH-050-API-001 to schemaVersion 2 and top-level `notifyOnInitialRecoveryOutreach`. The older task's version-1 shape is historical, not the current wire contract. Admin override does not control the merchant notification toggle. [B05-S25:50–73; B05-S26; B05-S14:62–75; B05-S15]

## Call-count method

Counts are explicit Prisma model-method calls plus explicit raw-query lock/read calls on successful non-retried paths, including the one authentication lookup. Exclude `$transaction` BEGIN/COMMIT/isolation setup, trigger-internal operations, relation expansion, nested implementation statements, retries, test fixture operations and provider work. They are not measured SQL counts, round trips, duration or capacity. A bulk operation can affect many rows while counting as one client call.

| Entry | Endpoint/path | Source-derived client calls | Transaction |
|---|---|---:|---|
| E17 | POST `/v1/merchant/store-category`: new profile + new lineage | 16 | Serializable, 15-second service timeout |
| E17 | Same endpoint: existing profile/lineage, create a new revision | 14 | Same |
| E17 | Same endpoint: existing profile/lineage, publish referenced pending draft | 13 | Same |
| E18 | GET `/v1/merchant/feature-preferences` | 6 | Repeatable Read, no explicit row-update locks |
| E19 | PUT `/v1/merchant/feature-preferences`: current-revision no-op | 6 | Read Committed, Shop UPDATE + installation SHARE locks |
| E19 | Same endpoint: m actually changed preferences, m > 0 | 9 + m | Same |
| E20 | GET `/v1/merchant/recovery-policy` | 5 | Repeatable Read, no explicit row-update locks |
| E21 | PUT `/v1/merchant/recovery-policy`: create/update | 6 | Interactive transaction with isolation inherited from DB configuration |
| E21 | Same endpoint: identical replay/default no-op | 5 | Same |

E21 does not explicitly set isolation. The API Prisma constructor also supplies no global transaction isolation override. PostgreSQL's documented default is Read Committed, but the deployed database configuration was not inspected; do not record that deployed isolation as measured fact. [B05-S14:99–122; B05-S37:12–17; external semantics T1/T2 below]

## Entry E17 — POST /v1/merchant/store-category

### Current flow and transaction decision

Authenticate -> read catalogue/template/mappings and render outside the transaction -> Serializable transaction -> lock/revalidate Shop and installation -> read subscription eligibility -> load/create profile and check expected generation -> re-read category/template/mapping versions/hash -> resolve/create SHOP prompt lineage -> resolve selected-environment configuration -> publish pending draft or insert next revision -> switch configuration -> guarded profile update/increment generation -> commit. No external network call is made inside the transaction. [B05-S01; B05-S03:32–129; B05-S04:32–132; B05-S05:12–111; B05-S06:30–47]

Retain the transaction, Shop/installation lock ordering, active-subscription gate, expected generation, existing prompt/configuration integrity checks and final affected-row count. Profile, published prompt and selected-environment pointer must agree, while Free entitlements and installation credentials remain unchanged. Re-reading the template after preparation is not a redundant duplicate: it compares the prepared source version/hash and mapping facts against the transaction snapshot. Do not claim that this makes every referenced row latest in wall-clock time at commit. [B05-S21:39–70; B05-S03:95–117; B05-S04:94–132]

The returned representation is constructed from the accepted mutation and known revision ID; there is no final profile reread to remove. A new POST with a current generation can publish a new revision even for the same category; a stale-generation retry conflicts rather than silently reapplying. Do not import recovery-policy replay rules into category publication.

### Count derivation

Outside transaction: authentication + prepared catalogue = 2. Existing profile/no pending draft inside: Shop lock, installation lock, subscription read, profile read, source recheck, lineage read, configuration read, draft-existence read, latest-revision read, revision insert, configuration create/update, profile CAS = 12. Total 14. New profile and new lineage add one create each, total 16. Publishing an existing referenced draft uses draft read + guarded update in place of the three revision-discovery/creation calls, total 13. [B05-S03–S05]

### E17-F01 — Fresh lineage still performs two empty revision-history queries

**Classification:** Confirmed avoidable source-path lookups; optimisation candidate.
**Priority:** Medium.
**Evidence:** B05-S05:20–30, 69–95.

When no lineage exists, this transaction creates it, then asks whether it has an existing draft and what its highest revision number is. No earlier statement in this branch created a revision. Carry an explicit `lineageCreated` fact and use revision number 1 directly for that newly created lineage. Retain both history checks for pre-existing lineages, including a pre-existing lineage with no revisions. Retain configuration integrity checks and migration-defined constraints.

Expected successful first-publication count: 16 -> 14 client calls. This is not a latency percentage. Validate against the fully migrated schema and test fresh lineage, existing empty lineage, existing draft, existing published history, parallel selection and late rollback before accepting.

### E17-F02 — Referenced draft read can be folded into the conditional publication

**Classification:** Confirmed read/check/conditional-write pattern; optimisation candidate.
**Priority:** Medium/low depending on frequency of this branch.
**Evidence:** B05-S05:47–67.

The draft lookup supplies its ID, promptId and status, all already expressible using `pendingRevisionId`, the resolved lineage ID and DRAFT in the guarded update predicate. A direct conditional update can preserve the exactly-one affected-row test and the same conflict result without a separate read. Keep the publication fields, content hash/provenance, editVersion increment and all database guards. Missing, foreign-lineage or already-published drafts must still fail and roll back the rest of the transaction.

Expected existing-profile/pending-draft path: 13 -> 12 calls. Do not apply this as an unconditional update or accept zero matches.

### E17-F03 — Dedicated category integration runner omits migration-only safeguards

**Classification:** Confirmed validation-harness limitation, not evidence of a runtime category defect.
**Priority:** Required before accepting mutation changes.
**Evidence:** B05-S33:54–79; B05-S19:103–116; B05-S20:28–42.

The selection suite is run after `prisma db push`. Migration-defined SHOP lineage and environment/SHOP configuration partial unique indexes and guards are not established by that harness merely because the Prisma model exists. Run the focused selection acceptance against canonical migrated pg17+pgvector, with fixtures satisfying the actual guards. Do not weaken migrations to make lightweight fixtures pass.

Existing sources test first publication/replacement, billing and credential preservation, one winner for parallel generation commands, stale credentials, inactive subscription, foreign mappings and template edit before transaction entry. They do not establish the new fresh-lineage/draft optimisation behaviour or every catalogue change after revalidation. [B05-S27:110–221; B05-S41]

### Endpoint disposition

Retain atomic publication. Implement only the proven branch-specific query reductions with canonical-schema evidence. Service error wrapping is covered by B05-X02 below. No schema change is currently proposed.

## Entry E18 — GET /v1/merchant/feature-preferences

### Current flow and necessary reads

Authenticate -> Repeatable Read transaction -> Shop identity read -> installation identity/version read -> active Subscription/plan/mappings with related Feature records -> active Feature catalogue + ShopFeaturePreference rows -> Shared `selectCapabilities` -> revision hash and exact DTO. The read path has no FOR UPDATE/SHARE clauses, preference writes or default-row creation. [B05-S09:18–106, 134–138]

One authentication + two identity + three entitlement/preference model calls = six. The Promise.all around the last two queries does not establish SQL-level parallelism within a Prisma transaction; it still uses one transaction connection. [B05-S09:64–67; external T2]

### Transaction decision — retain snapshot semantics

The revision depends on Subscription, BillingPlan, mappings, Feature fields and preference timestamps. The multi-read representation needs a stable view. Retain Repeatable Read unless replacing the whole consistency unit with an actually single-statement equivalent. Merely combining a few projections or removing `$transaction` does not preserve that guarantee. The current transaction does not use mutation-style row locks. [B05-S09:84–90, 134–138; external T1]

### E18-F01 — Full-row include graph retrieves unused fields

**Classification:** Confirmed over-fetching; bounded projection optimisation.
**Priority:** Medium/low, benefit unmeasured.
**Evidence:** B05-S09:53–106; B05-S18:871–894, 1416–1444, 1489–1537, 1540–1579.

`include` loads full Subscription, BillingPlan, BillingPlanFeature and related Feature scalar records. A separate query also loads full active Feature records. The service does not need subscription provider/reconciliation fields, billing pricing/credit-pack fields, mapping `configuration` JSON, or full nested Feature descriptions. Preferences need only featureId, enabled and updatedAt.

Use explicit projections retaining every fingerprint and Shared-selector input:
- Subscription: id/status/planId; plan: id/active/updatedAt.
- Plan mappings: featureId/enabled; related Feature: active/updatedAt.
- Active catalogue: id/key/displayName/description/active/activationMode/systemRequired/updatedAt, with existing ordering.
- Preferences: featureId/enabled/updatedAt, with existing ordering.

Do not drop inactive/disabled mapping facts simply because the response lists active features: the current fingerprint includes them. Do not remove feature timestamps or catalogue text from the revision without a separately agreed contract change. This is reduced data transfer, not a claimed reduction in model calls.

### E18-F02 — Consolidate the two read-only identity queries

**Classification:** Source-supported consolidation candidate.
**Priority:** Medium, subject to benefit and tests.
**Evidence:** B05-S09:19–49.

A joined identity projection inside the same Repeatable Read transaction can validate Shop/platform/domain/status, installation/shop binding/version/status/revocation in one raw query instead of two. Preserve every failure predicate and principal scope; do not reuse the earlier authentication object as proof that later transaction validation is unnecessary.

Potential GET count: 6 -> 5. Do not add locks to the GET or mechanically apply an equivalent join to writes without lock-order review. This is API-owned persistence code, not a candidate to move Prisma queries into Shared.

### Endpoint disposition

Retain read transaction and Shared-owned activation semantics. Prefer narrow projections and measured identity-query consolidation. No additional index is established as necessary by this review; relevant identity, shop preference and plan-feature keys already have indexes/uniqueness in the schema. No EXPLAIN was run.

## Entry E19 — PUT /v1/merchant/feature-preferences

### Current flow and write count

Read Committed transaction -> Shop FOR UPDATE -> installation FOR SHARE -> complete entitlement/preference load -> compare expected fingerprint -> reject every requested noneditable/unknown feature -> filter truly changed values -> if none return current -> sequential upsert per changed feature -> complete load again -> commit. [B05-S09:141–175]

Retain the transaction: multiple changes must be atomic and the loaded revision/editability decision coordinated against other same-Shop writers. Even a no-op must pass the revision and editability gates. Stale empty changes also conflict. These semantics are intentionally stricter than recovery-policy identical replay. [B05-S09:147–158; B05-S28:58–88; B05-S30:57–72]

Before writes: auth 1 + identity 2 + load 3 = 6. For m > 0: add m upserts and three reload calls, yielding 9+m. One changed feature therefore gives 10 calls; 10 changed features gives 19; the contract can permit 1,000 changes subject to body size and eligibility. These are formula examples, not measured merchant cardinalities or claims of deployed 1,000-feature usage. [B05-S10:2–5, 53–70; B05-S40; B05-S09:159–168]

### E19-F01 — Sequential per-feature writes produce linear query work

**Classification:** Confirmed per-item persistence pattern; conditional scalability optimisation.
**Priority:** Medium if batch-size measurements justify it.
**Evidence:** B05-S09:156–168; B05-S18:1521–1537.

For larger changesets, consider bounded set-based persistence rather than one upsert for every feature. Preserve distinct IDs, exactly the already-authorised changed set, tenant ownership, existing row IDs/createdAt, updatedAt/fingerprint semantics, and all-or-nothing rollback. Prisma-managed IDs/timestamps must not be silently omitted if raw SQL is chosen. Do not save ineligible feature flags to reduce validation cost.

`Promise.all` on the same transaction client is not a database-parallelism fix. Nor should merely increasing the transaction timeout substitute for measuring work. The API constructor and this transaction wrapper do not set a timeout override; Prisma v6 documents the standard interactive timeout. No timeout failure was reproduced here. [B05-S09:112–121; B05-S37; external T2]

No fixed batched-call target is promised before selecting and validating an implementation. With no changes, the current six-call path already avoids the upserts and second load.

### E19-F02 — The second complete load is not safely deletable without an entitlement-consistency decision

**Classification:** Source-supported optimisation constraint and missing adversarial validation, not a confirmed privilege bypass.
**Priority:** Required before changing reload/isolation behaviour.
**Evidence:** B05-S09:52–106, 144–168; B05-S38:71–118; B05-S39; B05-S28:75–96.

The second load retrieves actual preference timestamps for the response fingerprint and recomputes effective/required/eligible state using Shared. It is not just an unused read after a write. Reusing returned upserts could replace some work only with a clearly defined entitlement snapshot and complete revision reconstruction.

The Shop lock serialises cooperating merchant writes, but global Admin Feature and plan-feature mutations do not acquire that merchant's Shop lock. This PUT is Read Committed: both its pre-write and post-write multi-query loads can observe intervening global changes. Existing tests change plan mapping between requests and race two merchant commands; they do not pause an Admin update between the individual entitlement reads or between eligibility validation and mutation.

Example to test, not a reproduced incident: a feature is editable during pre-write load, the global catalogue deactivates it, then a merchant preference is persisted and the final response hides the inactive feature. Persisting a dormant preference is not automatically a privilege violation; the effective capability selector still applies current facts. The exact acceptance contract under global drift must be decided and tested rather than silently strengthened or weakened as a query optimisation.

Define a coherent authoritative entitlement view and explicit conflict/ordering behaviour for concurrent global edits. Do not claim that switching to Repeatable Read alone guarantees latest wall-clock eligibility at commit; equally, do not lock every tenant or every Feature globally as a blanket solution. Preserve the accepted one-winner merchant CAS invariant.

### E19-F03 — Timing fields overwrite the initial load on changed PUTs

**Classification:** Confirmed observability defect in phase attribution.
**Priority:** Medium, before using phase logs as optimisation evidence.
**Evidence:** B05-S09:146, 168; B05-S12:22–52; B05-S11:94–104; B05-S30:106–114.

The same phase names (`subscriptionLookupMs`, `featuresLookupMs`, `preferencesLookupMs`, projection/validation phases) are used in both loads. `timeFeaturePhase` and `timeFeatureSync` assign `timings[phase] = elapsed`, not accumulation. A successful changed PUT therefore reports the later load under those fields, replacing the initial load's durations. TransactionWorkMs/transactionMs still include both. This is missing attribution, not loss of total execution time.

Extend the existing diagnostic convention with separate before/after-load phases or documented totals plus invocation counts. Keep the shared logger, existing error propagation and bounded fields; no new generic telemetry framework. Add a deterministic test proving both loads' work is represented. Existing tests only establish that upsert and transaction timing fields exist, not that two loads are accounted for.

The latency note says some database reads overlap. JavaScript timing windows can overlap when calls queue on the same connection; this is not proof of simultaneous SQL execution. Update that interpretation alongside any phase correction, and do not sum nested/overlapping wall-clock timers as SQL execution time. [B05-S13; external T2]

### Endpoint disposition

Retain atomic revision-checked mutation and current no-op denial semantics. Correct timing attribution and handled-error cause preservation first, then use measurements to choose narrow/batched optimisations. Do not remove the final load based on query count alone.

## Entry E20 — GET /v1/merchant/recovery-policy

### Current flow and transaction decision

Authenticate -> Repeatable Read transaction -> Shop read -> installation/version read -> ShopSettings read -> ShopRecoveryPolicyOverride read -> Shared policy validation -> schemaVersion 2 representation. Total five calls. No business writes or explicit row locks. Missing settings uses existing fallback defaults (30 minutes, NONE, no follow-up), revision UNCONFIGURED and notification OFF without inserting a row. [B05-S14:17–96; B05-S17:5–14]

Retain the snapshot: the response combines stored merchant policy and override state. The override is selected as active only when no expiry or expiry after the supplied evaluation time. The response does not grant future sending authority; overrides can expire after the read, and outbound workflows must evaluate their own current policy.

The notification Boolean remains outside the override projection. Existing historical FIXED/AI modes are reported honestly without exposing a provider discount ID; the separate PUT rejects unsupported stored modes. Do not simplify GET by silently replacing such modes with NONE. [B05-S14:45–75; B05-S31:165–191]

### E20-F01 — Narrow policy/override projections and optionally combine identity reads

**Classification:** Confirmed unused scalar retrieval; safe-design consolidation candidate.
**Priority:** Low/medium, benefit unmeasured.
**Evidence:** B05-S14:17–42, 45–75, 91–96; B05-S18:39–60, 148–167.

Both `findUnique` calls fetch full scalar records. Retain only settings updatedAt + policy fields + merchant notification flag, and override expiresAt + policy fields. The stored fixedShopifyDiscountId remains needed internally for validity checks even though it must not enter the DTO. Unused override reason/admin attribution/createdAt and unrelated settings fields need not be retrieved.

A single joined read-only identity query, preserving all principal checks inside the Repeatable Read transaction, can separately reduce 5 -> 4 calls. Narrowing columns alone does not change the count. No need to create an override cache or to drop current override reads.

### Endpoint disposition

Retain coherent, no-write reads, default behaviour and override precedence. Optimise projection breadth first; combine identity reads only with equivalent authorization/failure tests. No new schema change identified.

## Entry E21 — PUT /v1/merchant/recovery-policy

### Current flow and transaction decision

Authenticate -> interactive transaction -> Shop FOR UPDATE -> installation FOR SHARE -> current settings -> reject unsafe historical offer mode -> identical-value short circuit -> expectedRevision check for a real change -> monotonic timestamp -> create/update returns settings -> read override -> project current merchant/effective policy -> commit. [B05-S14:99–128]

Retain this transaction even though there is at most one explicit settings write. It protects the read/check/write against competing merchant commands and installation changes, and the post-write policy projection is inside the rollback boundary. Isolation is not specified by this service, so deployed isolation remains configuration-dependent.

Source-derived calls: authentication 1 + identity locks 2 + settings lookup 1 + settings write 1 + override lookup 1 = 6. An identical replay skips the write and has 5. A stale nonidentical update rejects after the settings read (4 calls including authentication) without a write or override lookup. [B05-S14:101–121]

### Behaviour worth retaining — no speculative rewrite

The service already uses the record returned by create/update; there is no immediate settings reread to eliminate. Identical policy/notification values are detected before revision comparison, making a lost-response replay read-only even with its old revision. The source test explicitly replays the original UNCONFIGURED command after the first save. A notification-only change still advances the revision; absent settings plus exact defaults remain UNCONFIGURED without creating a row. [B05-S14:78–84, 108–120; B05-S29:41–66, 98–104; B05-S31:112–147, 203–209]

Do not standardise this to feature-preference semantics: those require a matching revision even for no-op. Both are source-defined contracts and have distinct tests.

A real update sets updatedAt to at least current updatedAt + 1 millisecond and writes only approved policy/notification fields. It does not write the admin override or another ShopSettings field. The override lookup after save is necessary to return effective policy; it is not a duplicate settings lookup. A single blind upsert would discard current offer validation, replay distinction and revision protection.

### E21-F01 — Handled conflict wrapping loses the original Prisma error

**Classification:** Confirmed diagnostic gap; grouped with B05-X02.
**Priority:** Medium.
**Evidence:** B05-S14:123–126; B05-S15:38–47; B05-S16:55–63, 73–87.

P2002/P2034 are wrapped as a new `RecoveryPolicyConflictError` without the original cause. The route logs that new wrapper. Unexpected exceptions retain their original Error and sanitized 500; logging failure is deliberately isolated. Do not describe all route errors as swallowed or change the successful/409/500 contract merely to preserve causes.

### Endpoint disposition

No mandatory call-count reduction is established for the write path. Retain current return-value reuse, replay behaviour, revision advancement, override query and locks. Narrow projections can be shared with E20; handled-error preservation is the direct corrective recommendation. Do not remove the transaction because only one settings row is updated.

## B05-X02 — Preserve original handled database exceptions across all three write services

E17 catches P2002/P2034 and throws `categoryConflict()` without cause [B05-S03:126–129; B05-S08]. E19 does the same with `FeaturePreferencesConflictError` [B05-S09:170–174; B05-S10:36–39]. E21 does the same with `RecoveryPolicyConflictError` [B05-S14:123–128; B05-S15:38–41]. Their route loggers cannot recover discarded provider details; an errorCause property in a downstream logger is not sufficient.

Keep typed bounded public conflicts, but preserve the original code/message/cause and safe relevant metadata through the domain error boundary. Use the existing `@modainteract/moda-interact-shared/logging` integration and redaction. Do not log prompt text, credentials, complete request bodies, raw query parameters or unnecessary merchant data. Expected validation/CAS errors without an underlying exception need no fabricated cause. Do not invent generic failure explanations in place of the actual Prisma exception.

These services do not automatically retry those failures. Do not add blind retries that re-read a new revision and force a stale command through; any retry must retain the original expected revision/generation and respect the endpoint's defined result contract. Test injected P2002/P2034 through the service and route together, not only a route stub that throws an already-wrapped error. No new generic logger or cross-service persistence helper is proposed.

## Validation, existing evidence and limits

| Area | Existing inspected evidence | Required extension for the proposed change |
|---|---|---|
| Category selection | First/replacement, concurrent generation winner, rollback on template drift, unchanged billing/credentials; dedicated runner uses db push | Canonical migrations; fresh vs existing lineage; pending-draft conditional update; missing/foreign/published draft; rollback; explicit call assertions and actual SQL measurements |
| Feature GET | Eligibility flags, hash changes, no writes, invalid principal/plan; migration-backed runner | Stable multi-table snapshot during global edits; narrowed projection preserves byte-for-byte response/revision; joined identity checks; actual SQL/row-transfer measurements |
| Feature PUT | One-winner merchant race, no-op/current revision, stale requests, mapping drift between requests, system-required denial; migration-backed runner | Late failure in multiple changes rolls back all; realistic/boundary changeset load; coordinated global edit between reads; correct before/after timing; conflict cause preservation |
| Policy GET/PUT | Defaults, notification-only edits, identical replay, one-winner stale race, admin override/expiry, stale credential; migration-backed cross-domain runner | Narrow projection and joined GET identity equivalence; error-cause route/service test; overlap with override changes; preserved no-op/default/timestamp behaviour |

The feature runner generates Prisma and deploys migrations before running its dedicated suite. The cross-domain policy runner also generates Prisma and deploys migrations. They must not be mislabelled db-push tests merely because category selection uses the older installation harness. [B05-S34:35–42; B05-S35:13–16, 54–66; B05-S33:54–79]

Historical task evidence: ARCH-035-API-014 records accepted feature tests and an explicit paid-plan-fixture waiver on 17 October 2026; ARCH-050-API-001 records accepted version-2 policy tests/migrations on 27 October 2026. Those are source-reported historical results, not newly executed tests in this review and not proof of the new recommendations. The waiver remains intact. [B05-S22:185–216; B05-S26]

Current environment verified during this increment: Node v22.16.0 is available; API declares Node 24.19.0, Prisma 6.19.3 and Shared 3.1.0. API node_modules, Docker and psql are absent. No dependency/toolchain installation, runtime test, provider exercise, container or PostgreSQL benchmark was attempted. No EXPLAIN, lock-wait measurement, SQL statement count, pool metric or capacity result was produced. [B05-S36; current environment commands]

Completed verification: actual route/service/helper/test/migration/task inspection, safe archive extraction, SHA-256 verification of the uploaded archive, and byte-for-byte checks of all 47 evidence source files. The extracted review copy was not modified. Source identity is the uploaded archive and per-file checksums, not an invented developer branch, worktree or commit.

## Priority and ownership

| Priority | Finding | Recommendation |
|---|---|---|
| Medium | E19-F03; B05-X02/E21-F01 | Correct timing attribution and preserve original handled database errors before relying on diagnostics |
| Bounded optimisation | E17-F01/F02 | Remove two history reads only for a newly created lineage; fold referenced-draft check into guarded update |
| Measurement-led | E18-F01/F02; E20-F01 | Narrow projections; combine read-only identity queries without changing snapshot/authorization semantics |
| Conditional performance work | E19-F01/F02 | Measure actual change counts and transaction cost; choose bounded batching and coherent entitlement contract, not blind reread removal |
| Acceptance prerequisite | E17-F03 | Canonical migration-backed category mutation coverage |
| Retain | E18/E20 snapshot reads; E21 mutation flow; E17 publication transaction | Avoid refactoring correct behaviour solely to lower a headline query count |

API owns query/service/test/diagnostic changes. Database owns canonical migrations if a later validated proposal genuinely needs one; no schema change is requested now. Admin code was read only to establish independent global catalogue writers; no Admin implementation task is created. Shared retains capability selection and generic logging, not application Prisma orchestration. No new infrastructure or system-test task is materialised during this assessment.

No application source, schema, architecture, task metadata, `_index.md`, branch, commit or push was changed. The report and evidence are external review artifacts. No accepted patch is issued until there is an implementation or an explicitly requested architecture/task amendment to review.

## External technical cross-checks — distinct from application evidence

Only primary documentation was consulted for database mechanics. All application behaviour and recommendations above are grounded in the uploaded source; external references do not imply runtime validation.

T1 — PostgreSQL 17, Transaction Isolation (`https://www.postgresql.org/docs/17/transaction-iso.html`), checked 1 November 2026: Repeatable Read uses a stable transaction snapshot; Read Committed can see intervening commits between statements. This is why existing read snapshots should not simply be deleted, and why a transaction name alone does not establish a latest-at-commit business contract.

T2 — Prisma ORM v6, Transactions (`https://www.prisma.io/docs/orm/v6/prisma-client/queries/transactions`), checked 1 November 2026: interactive transaction work shares one connection, Promise.all does not make its SQL run in parallel, options can inherit database isolation, and the documented standard interactive timeout is five seconds. These clarify mechanics; no runtime timeout, duration or deployed isolation was measured.

## Next increment boundary

Continue with GET and PUT `/v1/merchant/ai-response-delay`, GET `/v1/merchant/recoveries`, GET `/v1/merchant/recoveries/:id`, and GET `/v1/merchant/recoveries/:id/messages` (five endpoints). They are not marked reviewed by the current batch.

---

# Increment 06 — AI reply delay and recovery reads (E22–E26)

**Review date:** 1 November 2026.
**Progress:** 26 of the original 61 endpoint method/path combinations reviewed; 35 remain.
**Status:** Source-based architectural assessment and proposals; not implementation acceptance.
**Evidence:** `woocommerce-api-database-review-06-source-evidence.txt` (B06-S01–B06-S44), with original source line numbers, and `woocommerce-api-database-review-06-source-manifest.json`.
**Source verification:** All 44 included files were compared byte-for-byte with the original uploaded ZIP. No application source, schema, task, architecture document, `_index.md`, branch or worktree was changed.

## Summary and count convention

The clearest avoidable-work finding is in message pagination: a 51-row lookahead is fetched but not used to avoid two complete outside-page counts. The same endpoint also loads summary-only basket/customer/outreach data for every message page. The recovery-list count is different: its exact value is part of the approved page-number contract and should remain, except that a zero result makes the subsequent page query unnecessary. AI-delay settings have narrow-projection opportunities, while the PUT already avoids same-value writes and write-then-read behaviour.

Counts below are explicit Prisma model-method and raw SQL invocation counts in the inspected successful, non-retried route. Each authenticated request contributes one authenticator model call. Counts exclude transaction-control statements, nested relation-query expansion, database-trigger work, retries and HTTP logging. They are not measured SQL statements, network round trips, rows examined or latency estimates.

| Entry | Endpoint | Current explicit calls including authentication | Transaction recommendation |
|---|---|---:|---|
| E22 | GET `/v1/merchant/ai-response-delay` | 4, with or without a settings row | Retain the existing non-locking Repeatable Read snapshot while consolidating reads |
| E23 | PUT `/v1/merchant/ai-response-delay` | 5 actual change/create; 4 valid no-op or revision conflict | Retain mutation transaction and current lock order |
| E24 | GET `/v1/merchant/recoveries` | 5, including current zero-result path | Retain exact-count/page snapshot; skip page fetch when total is zero |
| E25 | GET `/v1/merchant/recoveries/:id` | 5 without verified-inbound query; 6 when conversation and initial sentAt require it | Retain coherent summary snapshot and domain evidence queries |
| E26 | GET `/v1/merchant/recoveries/:id/messages` | 8 nonempty page; 5 empty existing conversation; 4 no conversation | Retain snapshot; use lookahead/bounded existence and a narrow ownership projection |

An absent or foreign recovery returns not-found after four calls including authentication. Route-rejected malformed requests are separate paths and are not included in successful-path counts. Proposed call reductions in different findings must not be added together without specifying the combined implementation; narrowing a projection alone does not reduce a model call.

## E22 — GET /v1/merchant/ai-response-delay

### Current behaviour

The route authenticates the installation, rejects GET bodies and query overrides, and calls a Repeatable Read transaction. Two raw SELECTs validate Shop and installation identity, platform, status, canonical site URL, credential version and revocation. A `shopSettings.findUnique` then loads the settings row. The response uses only `updatedAt` and `aiResponseDelayMinutes`. Missing settings yields `{schemaVersion:1,revision:"UNCONFIGURED",aiResponseDelayMinutes:0}` without any write. [B06-S01:21–75; B06-S03:31–84; B06-S04:23–37]

Neither identity SELECT takes an explicit row lock on GET. The `onboardingCompleted` field is used only by the PUT first-create branch. The implementation imports the published Shared AI-delay contract; this review does not propose duplicating it. Values remain whole numbers 0–30 inclusive and default zero. [B06-S03:31–84, 103–115; B06-S05:1–6, 35–46; B06-S25]

### Transaction assessment — retain for the existing multi-query design

The transaction keeps the revalidated identity and settings in one database snapshot. Do not remove it merely because the method is GET, or replace it with locking reads. A future single actual SQL statement could supply its own statement snapshot, but that would be a separate demonstrated design, not a reason to delete the present transaction before restructuring the reads.

This is snapshot validation, not a promise that credentials remain valid indefinitely after the response. Authentication before the transaction and revalidation inside it are distinct boundaries. [B06-S03:79–84; technical cross-check T06-01]

### E22-F01 — Full settings record fetched for two response fields

**Classification:** Confirmed over-fetching. **Priority:** Low/medium depending on request volume. **Owner:** moda_api.

`findUnique` has no `select`, while `response()` uses only `updatedAt` and `aiResponseDelayMinutes`. The schema also contains unrelated recovery policy, follow-up, notification, language, country, timezone and legacy plan fields. [B06-S03:62–84; B06-S23:39–60]

Use a narrow projection and an explicitly narrowed local type. Apply the corresponding return projection to PUT `create`/`update` where appropriate. Preserve null-as-unconfigured, range/integer integrity checks and the exact timestamp revision. This reduces data retrieval; it does not reduce the count of model calls.

### E22-F02 — Consolidate two read-only identity queries without removing checks

**Classification:** Query consolidation candidate. **Priority:** Medium, shared with recovery read paths. **Owner:** moda_api.

A tenant-bound joined Shop/installation read could replace the two raw SELECTs while preserving every existing identity and lifecycle comparison and remaining inside the snapshot. Current GET count 4 -> proposed 3 calls. Do not broaden the global authenticator with endpoint-specific business data or weaken any comparison. Use an API-local helper only if its contract fits the callers; database authorization belongs in API, not a cross-service Shared primitive. [B06-S03:31–59]

Do not mechanically apply the same rewrite to PUT: it currently acquires Shop `FOR UPDATE` before installation `FOR SHARE`, and lock acquisition order is part of the concurrency design.

### Acceptance validation

Cover missing settings without creation, 0/7/30, malformed persisted values, narrow projection shape, stale/revoked/foreign installation, unchanged GET response and no explicit row locks. If identity queries are joined, verify actual SQL and that the joined query cannot silently convert an identity mismatch into a default response. [B06-S27; B06-S28]

## E23 — PUT /v1/merchant/ai-response-delay

### Current behaviour and transaction assessment

Inside a transaction, Shop is locked `FOR UPDATE`, installation is rechecked under `FOR SHARE`, and settings are read. The service requires `expectedRevision` equality BEFORE checking for equal values. A current-revision identical value returns without a write. A real change updates only the delay and `updatedAt`; a first create establishes the existing policy defaults. Timestamp advancement uses the greater of application now or current timestamp + 1 ms. The `create`/`update` result is returned without a settings reread. [B06-S03:87–118]

Retain the transaction and lock order. This is a coordinated read/revision-check/write operation even though it has at most one explicit settings write. The isolation level is not explicitly set in `update()`; it inherits database configuration, which was not inspected in a deployment. Do not call it Serializable or assert its deployed default from this source alone.

The revision is the shared ShopSettings `updatedAt`, not a new per-delay version. Existing policy fields must remain untouched on an update, and a stale same-value PUT still returns conflict. The source explicitly tests that route behaviour. Do not substitute the recovery-policy endpoint's more permissive identical-replay rule. An unconfigured request for zero with `UNCONFIGURED` remains a no-write default response. [B06-S03:91–117; B06-S27:78–168; B06-S28:33–78]

### E23-F01 — Handled Prisma conflict wrapper drops the original cause

**Classification:** Confirmed diagnostic gap. **Priority:** Medium / diagnostic contract requirement. **Owner:** moda_api.

`P2002` and `P2034` become `new AiResponseDelayConflictError()` with no cause. The domain error constructor cannot accept one. Although route logging includes the Error and cause fields, those fields cannot reconstruct the discarded Prisma exception. [B06-S03:119–123; B06-S05:17–20; B06-S04:59–72]

Preserve the original Prisma Error through wrapping and record safe code/message/metadata/cause through `@modainteract/moda-interact-shared/logging`, with redaction. Keep the public 409 contract. Do not silently retry a stale command against a newly loaded revision. Unexpected exceptions already propagate; this finding is specifically about handled conflict translation. [B06-S44]

### E23-F02 — Dedicated migrated suite is not called by the aggregate integration script

**Classification:** Confirmed command-wiring gap, not absence of tests. **Priority:** Required to make future aggregate validation representative. **Owner:** moda_api.

`scripts/test-arch054-ai-response-delay-postgres.mjs` generates the API client, deploys migrations and runs the dedicated PostgreSQL suite. The current package `test:integration` command does not invoke it, directly or through the inspected runners. Normal `npm test` selects unit tests; it does not replace the dedicated PostgreSQL runner. [B06-S38:38–45; B06-S37:8–41]

The task specifically requires the standalone runner and records earlier passing validation. Therefore it would be wrong to claim the feature has never been integration-tested, or that this review invalidates the accepted task. The recommendation is to make future validation include that existing suite, not to introduce duplicate test infrastructure. [B06-S40, Validation and Attempt 2/3 evidence]

### Retained efficiencies and validation

Keep current-value no-op suppression, monotonic revision, narrow writes, returned write result, first-create defaults and separate AI-versus-recovery delay semantics. Unit and PostgreSQL sources cover values, tenant checks, revoked installations, concurrent same-revision writes and unrelated policy preservation. Add conflict-cause assertions; exercise concurrent recovery-policy/AI-delay updates under their shared row/revision protocol rather than inventing a second revision column. No schema change is currently justified. [B06-S27; B06-S28]

## E24 — GET /v1/merchant/recoveries

### Current behaviour

Within one Repeatable Read transaction, the service loads Shop and installation, validates them, derives the store-local date window, counts exact matching recoveries and fetches the requested page. It clamps the requested page to the real last page and orders by `(detectedAt DESC, id DESC)`. Customer name/email are projected narrowly; a mismatched customer Shop fails closed. Search predicates themselves also carry the authenticated Shop. [B06-S07:6–45, 48–128]

The parser bounds page numbers to 1–9999, page size to 10/20/25/50, date ranges to 366 days and search length. The default date range is the last 30 local dates including today. [B06-S09:26–31, 77–118]

The source count is authentication + two identity queries + exact count + page = five calls. `Promise.all` around identity queries does not mean the transaction obtains parallel database connections. No timing or network round-trip improvement has been measured. [B06-S07:79–112; technical cross-check T06-04]

### Transaction assessment — retain exact count/page snapshot

The task explicitly requires one repeatable-read snapshot for identity, exact filtered count and rows; it also explicitly permits offset-page movement between separate requests. Do not remove the transaction, approximate `total`, drop the count, or silently migrate v1 to cursor-only paging. [B06-S41:58–80; T06-01]

### E24-F01 — Zero count still followed by page fetch

**Classification:** Confirmed unnecessary query on the empty-result branch. **Priority:** Medium. **Owner:** moda_api.

After `total === 0`, the code still issues `findMany` with identical filtering inside the same stable snapshot. Returning the normal empty response immediately is sufficient: `items=[]`, `total=0`, `totalPages=1`, `page=1`, and both navigation flags false, with all normalized filter and timezone fields preserved. Proposed empty-result count 5 -> 4. Nonempty results still need the count and page query. [B06-S07:100–128]

The existing empty search test expects a page query to inspect its predicate. Update that structural assertion deliberately; do not delete tenant/filter tests for nonempty paths. Add a spy that fails if `findMany` is invoked after zero count. [B06-S29:93–107, 127–131]

### E24-F02 — Identity-query consolidation is possible; exact result costs still need measurement

The same read-only Shop/installation consolidation described in E22-F02 could reduce the normal list count from 5 to 4. Keep the Shop timezone in the combined projection and keep all authorization checks inside the snapshot. Narrowing only a Prisma projection does not automatically prove one SQL statement. [B06-S07:81–98]

Existing indexes already cover `(shopId, detectedAt, id)` and `(shopId, status, detectedAt, id)`; they are present in both schema and migration. Do not prescribe a duplicate paging index. Search uses per-word case-insensitive contains predicates on customer firstName/lastName/email, so exact count and searched pages deserve representative query-plan measurement. [B06-S07:48–69; B06-S23:390–397; B06-S24]

Deep offset is a capacity risk rather than a proven current bottleneck. At the largest accepted page and size, the arithmetic offset can reach 499,900 when enough matching records exist; the actual page is clamped to available totals. PostgreSQL documents that skipped offset rows still have to be computed. Measure empty, common, large-history, multiple-status and multiword-search paths with EXPLAIN/BUFFERS and SQL tracing. Do not add a search index, change search semantics or introduce caching based solely on source inspection. [B06-S09:85–110; B06-S07:104–110; T06-02]

### Validation qualification

The inspected repository contains focused mock-backed list/query/route tests. No dedicated list-service PostgreSQL integration file was found in the uploaded API test tree; the task's historical review explicitly says that database execution was not verified at that retrospective review. This is not proof that nobody has ever manually tested the endpoint. Before accepting query changes, add/run migrated-PostgreSQL scenarios for count/page consistency during inserts/status changes, zero-count short-circuit, dates/DST, search, tenant-corrupt relationships and page clamping. [B06-S29; B06-S30; B06-S41:169–186]

## E25 — GET /v1/merchant/recoveries/:id

### Current behaviour and counts

`withOwned()` starts Repeatable Read, revalidates Shop and installation, and loads the recovery by both recovery ID and Shop ID. It validates the customer tenant and conversation recovery/shop/customer links. A conversation whose direct Shop ID is null remains permissible only under the existing recovery-based linkage checks; do not convert that supported shape into an unconditional rejection. [B06-S12:51–96; B06-S36:39–43]

The summary loads the saved basket, milestones, customer projection, conversation control state and only outreach sequences 1/2. It independently reads the Shop's human-messaging restriction. When a conversation exists and initial outreach has `sentAt`, it queries the most recent qualifying customer inbound. No live WooCommerce, R2 or provider operation occurs in this path. [B06-S12:16–35, 99–131; B06-S16:19–51; B06-S17]

Counts: authentication 1 + identity 2 + owned recovery 1 + restriction 1 = 5; the conditional inbound query makes 6. Missing/foreign recovery returns before restriction/inbound work at 4. These counts exclude relation-query expansion.

### Transaction and domain-read assessment — retain

The restriction, control state, outreach-use state, basket and verified-inbound projection are different facts needed by the response. I found no proven redundant domain query on the successful summary path.

In particular, do not replace the inbound query with `Conversation.lastInboundAt`. The existing helper requires INBOUND + CUSTOMER + non-null provider message ID, with createdAt between initial send and the captured current time, and deterministic newest-first ordering. The source calls this verified inbound evidence; this review does not add or infer a broader cryptographic-verification guarantee beyond those predicates. [B06-S21:31–45]

The UI projection is not send admission. Missing restriction is represented as ACTIVE; unknown status never grants permission. Actual POST admission remains separate, and the GET does not reserve or authorize a later send. [B06-S16:19–51]

### E25-F01 — Optional shared identity consolidation, not removal of evidence reads

**Classification:** Query-consolidation candidate only. **Priority:** Lower than E26's unnecessary history work. **Owner:** moda_api.

Combining the two identity queries could remove one explicit call if all checks and snapshot semantics are retained. The restriction and inbound reads must not be removed merely to reach a smaller count. Fetching a narrow related restriction as part of an existing query is another possible design, but generated SQL and semantics would need inspection; no additional call-saving target is asserted for it. [B06-S12:58–106]

No new schema/index is justified by this summary review. The message ordering index already exists. A selective index for heavily filtered inbound history would require plan and workload evidence rather than a speculative migration. [B06-S23:727–729; B06-S24]

### Validation evidence

The migrated human-send runner includes an enriched detail PostgreSQL test covering saved basket/precision, actual verified-versus-unverified inbound examples, recovery-linked nullable Shop identity, tenant absence and current moderation reads. The test creates only three messages; it is not a large-history pagination benchmark. Unit projections cover absent initial outreach/conversation and restriction defaults. Require concurrent control/restriction/moderation changes to preserve a coherent request snapshot before altering the read boundaries. [B06-S33; B06-S36:39–104; B06-S39:55–66]

## E26 — GET /v1/merchant/recoveries/:id/messages

### Current behaviour and counts

The route independently authenticates the request and validates its resource-bound navigation cursor. Cursor scope is a navigation binding, not a substitute for authorization. `withOwned()` then repeats the same identity and recovery ownership checks as the summary endpoint in a fresh Repeatable Read transaction. [B06-S15:26–85; B06-S20:49–66; B06-S12:134–149]

For an existing conversation, the page reader fetches 51 rows using the `(createdAt,id)` keyset, returns 50 in chronological order and issues three further calls: one page-scoped moderation query and two complete counts on either side of the returned page. It uses the count values only as `> 0`. [B06-S13:84–125]

Nonempty page: authentication 1 + identity 2 + owned recovery 1 + message fetch 1 + moderation 1 + two counts 2 = 8. Empty conversation page returns after the fetch at 5. No conversation returns at 4. Malformed cursor validation is before the business transaction; keep it there.

### E26-F01 — Unused lookahead and exact counts for Boolean navigation

**Classification:** Confirmed avoidable database work. **Priority:** Highest query-efficiency priority in this increment, not a measured bottleneck. **Owner:** moda_api.

The 51st fetched row is sliced away without deriving a navigation flag. Both counts determine only whether at least one older/newer row exists; the API never returns their numeric totals.

Proposed behaviour, inside the same snapshot:

| Navigation | Infer from the page fetch | Additional navigation lookup |
|---|---|---|
| `first` | No previous page; 51st row means next page | None |
| `latest` | No next page; 51st row means previous page | None |
| `next` | 51st row means another next page | Bounded existence of a row before the first returned row |
| `previous` | 51st row means another previous page | Bounded existence of a row after the last returned row |

Use the same lexicographic predicates, timestamps, ID ordering, conversation scope and returned-page boundary. The opposite-direction query must remain for arbitrary, stale or deleted-row cursor boundaries; do not infer that the cursor row still exists. Preserve the current empty-page response. An EXISTS or ID-only first-match query expresses the Boolean requirement without counting every qualifying row; actual performance still requires query plans. [B06-S13:43–47, 92–124; T06-03]

Proposed nonempty first/latest count: 8 -> 6. Proposed nonempty next/previous count: 8 -> 7, with the remaining exact count replaced by bounded existence. These figures do NOT include the optional identity-query consolidation elsewhere. The empty/no-conversation counts remain unchanged.

A review-only in-memory comparison was executed: 123,488 cases over 208 datasets agreed between current count-based row/navigation semantics and the proposed lookahead/existence rules. Cases covered all four directions, zero and 49/50/51/52 page edges, tied timestamps, sparse/deleted data and boundaries absent from the data or outside its extent. The script and JSON result are included. This is NOT execution of the TypeScript application, Prisma, PostgreSQL, SQL collation, concurrent database writes, moderation or cursor serialization; it is not a benchmark or acceptance result.

### E26-F02 — Summary-only data loaded for every message page

**Classification:** Confirmed unnecessary data/relation retrieval. **Priority:** Medium. **Owner:** moda_api.

`messages()` shares the full `recoverySelect` with summary. It therefore retrieves `lineItems`, prices, currency, milestones, customer names/email, conversation control fields and outreach attempts even though message paging does not use them. [B06-S12:16–35, 83–95, 134–148]

Define a narrow ownership projection for this endpoint: recovery ID, Shop ID, customer ID, customer Shop ID where needed for current integrity checks, and conversation ID plus recovery/shop/customer bindings. Retain all existing fail-closed relationship checks, including corrupt customer relationships and supported nullable conversation Shop IDs. Drop summary-only fields and the outreach relation from the messages path. Do not remove authorization or try to cache it across browser page requests.

This is a data-volume/relation-work optimisation, not an asserted reduction in top-level model calls. The reduction in actual SQL statements depends on emitted relation loading. The related-recoveries endpoint also uses `withOwned`, but it is outside this increment and is not marked reviewed here.

### Moderation lookup — retain, and do not turn it into N+1

There is already one query for the exact returned page IDs, not one query per message. It binds Shop, conversation and message; only considers suitable text/completed audio transcripts; matches input kind and SHA-256 of the current persisted content; and chooses the latest applicable assessment. Unknown/missing decisions default to pending rather than allow. [B06-S14:14–49; B06-S22; B06-S34]

Retain those predicates and the common snapshot with the message-content query. Removing the content digest or reading moderation outside the snapshot could detach the displayed assessment from the displayed content. Page-bounded IDs limit the subject set, not necessarily the number of historical assessment rows examined; measure actual plans before adding indexes.

### E26-F03 — Pagination acceptance needs real multi-page PostgreSQL coverage

**Classification:** Validation coverage gap for the proposed changes. **Priority:** Required before acceptance. **Owner:** moda_api; cross-service tests only if broader behaviour changes.

Existing unit tests emulate ordering/filtering over 105 rows and verify forward/backward traversal and tied timestamps, while the migrated enriched-detail test exercises only a three-message page. Neither the in-memory review check nor those mocks establish PostgreSQL collation, actual SQL counts, concurrent content/moderation changes, or large-history query plans. [B06-S31:22–97; B06-S36:45–89]

Before acceptance, run the same page navigation cases on canonical migrated PostgreSQL, including 0/1/49/50/51/105 messages, equal timestamps, deleted boundaries, forged-but-well-formed resource-scoped navigation positions, concurrent inserts between requests and moderation/content mutation around the two reads. Within each request require a coherent snapshot; across requests do not claim a frozen global conversation history. Require no exact history count on message pages, page-scoped moderation, unchanged secret projection and preserved tenant checks.

## Cross-cutting diagnostics and indexes

The recovery-list and detail routes preserve original error name, message, stack and cause in their unexpected-error logs; they do NOT have the same generic replacement behaviour as the AI-delay conflict wrapper. However, they project those fields manually and omit the original Error object and structured Prisma `code`/`meta`. A bounded shared-logger error representation could preserve the full useful SDK diagnostic shape without logging requests, message content, credentials or unredacted raw SQL parameters. Do not describe existing logging as absent. [B06-S08:57–75; B06-S20:80–98; B06-S44]

The relevant list and transcript indexes already exist in the schema and ARCH-019 migration. There is also an older `(conversationId,createdAt)` index alongside the deterministic `(conversationId,createdAt,id)` index. This is an overlapping-prefix index review candidate, not proof that the smaller index should be dropped: actual plans, index sizes and other writers/readers must be considered. No index or schema change is included or required solely by the current recommendations. [B06-S23:390–397, 727–729; B06-S24]

## Priorities, ownership and stop boundary

| Priority | Recommendation | Expected evidence before acceptance |
|---|---|---|
| 1 | E26 navigation lookahead/existence and narrow message ownership projection | Migrated multi-page tests, unchanged cursors/content checks, actual SQL/plan comparison |
| 2 | E23 original-cause preservation and aggregate-suite inclusion | Injected handled Prisma error retains safe diagnostics; dedicated suite remains callable and included |
| 3 | E24 zero-result short-circuit | No page query after zero count; exact response/tenant/date semantics unchanged |
| 4 | Read-only identity consolidation and delay-field projection | One actual joined identity read where intended, complete checks and snapshot preserved |
| 5 | Representative deep-list/search and history/moderation measurements | Measured plans/rows/buffers/timing; no speculative index or cache |

All proposed code/test changes are owned by `moda_api`. Any later evidence-backed index change belongs to `moda_database`. Existing PostgreSQL infrastructure and shared logging are sufficient for these recommendations; no new gateway, queue, worker or telemetry transport is justified. No task was created, reopened, accepted, materialised or pushed in this increment. This remains a review record for the final consolidated report.

## Validation performed, not performed, and reproducibility

**Performed here:** Source inspection; exact archive/file verification of 44 included source files; checksum comparison of root and API nested Prisma schemas (both `45df5e44bdc1e7e29495e391a1754477f0df362c667d648f4b6893b6541f5c0d`); source-derived per-branch call counting; the explicitly limited Python pagination model comparison (PASS, 123,488 cases). Source bytes and the report are packaged with manifests; no application source edits were made.

**Not performed here:** Application unit/integration tests, PostgreSQL migration execution, Prisma query logging, EXPLAIN, live concurrency reproduction, latency/throughput/pool measurements, lint, typecheck or build. `node_modules` is absent; Docker and psql commands are unavailable. Available Node is v22.16.0 versus declared 24.19.0. No alternate Node installation/bootstrap selection was performed.

**Existing validation entrypoints inspected:**

- `node scripts/test-arch054-ai-response-delay-postgres.mjs` deploys migrations and executes the delay service PostgreSQL test.
- `node scripts/test-arch040-woo-human-send-postgres.mjs` deploys the validated canonical migration chain and includes `tests/integration/merchant/recoveries/detail/enriched-detail.postgres.test.ts`.
- Normal `npm test` uses the repository's unit-test glob. The current aggregate `test:integration` omits the dedicated ARCH-054 runner.

These are repository-declared/existing commands, not claims they ran here. The accepted ARCH-054 task's historical pass records remain historical evidence, not fresh execution by this review. [B06-S37–B06-S40]

## External technical cross-checks (not application-source evidence)

Checked 1 November 2026. The uploaded source remains authoritative for application behaviour. These references are used only to check database/framework semantics behind the explicitly marked proposals:

- **T06-01:** PostgreSQL 17 transaction isolation, `https://www.postgresql.org/docs/17/transaction-iso.html` — Repeatable Read uses a stable transaction snapshot across successive reads, unlike per-statement Read Committed snapshots.
- **T06-02:** PostgreSQL 17 LIMIT/OFFSET, `https://www.postgresql.org/docs/17/queries-limit.html` — skipped offset rows still need computation; stable pagination needs deterministic ordering.
- **T06-03:** PostgreSQL 17 EXISTS, `https://www.postgresql.org/docs/17/functions-subquery.html` — an existence test need only establish one result rather than compute an exact count.
- **T06-04:** Prisma ORM v6 transactions, `https://www.prisma.io/docs/orm/v6/prisma-client/queries/transactions` — an interactive transaction uses one connection; Promise.all does not make its database statements execute in parallel.

## Next increment — not yet reviewed in this record

E27 GET `/v1/merchant/recoveries/:id/related`; E28 GET `/v1/merchant/recovery-summary`; E29 POST `/v1/merchant/conversations/:id/messages`; E30 GET `/v1/merchant/conversations/:id/send-commands/:commandId`; E31 GET `/v1/merchant/conversations/:id/follow-up-templates`.

The related-page helper was encountered while tracing messages, but it is not counted as a sixth reviewed endpoint in this increment.

---

# Increment 07 — five more endpoints (E27–E31)

**Review date:** 2 November 2026.
**Source baseline:** the same 1 November 2026 uploaded workspace archive; no new source snapshot supplied.
**Coverage after this increment:** 31 of the original 61 method/path combinations; 30 remain.
**Status:** source inspection and proposed corrections/optimisations; not implementation acceptance or a performance benchmark.
**Evidence:** `woocommerce-api-database-review-07-source-evidence.txt`, entries B07-S01–B07-S58, plus its source manifest. Original source line numbers are preserved. Earlier increments remain historical records, including their then-current progress and next-scope statements.

## Executive assessment

The most important new finding is a moderation-subject mismatch in the command-status GET: it hashes `textBody`, while the accepted prepared-content migration and Background writer bind HUMAN_TEXT moderation to `preparedTextBody`. A rendered wrapper that changes the text causes a valid assessment to be excluded by the status query. This is a source-confirmed query/contract mismatch with a concrete conditional consequence, not a reproduced production incident and not proof that Background bypasses moderation.

A second correctness issue concerns idempotency scope: the public command key is shop-scoped, but the follow-up admission copies it unchanged into globally unique `RecoveryOutreachAttempt.initiationKey`. Independent shops choosing the same permitted retry key can conflict. Background dispatch/cancellation explicitly compare these two fields, so an API-only prefix change would break consumers.

The follow-up catalogue also uses the root Prisma client for a configuration read while an interactive transaction is open. This creates an additional connection dependency and a different snapshot boundary. Its broad catch turns dependency failures into empty choices. The production configuration wrapper DOES already log original causes before rethrowing: do not misreport this as universal absence of logging.

Optimisation opportunities are narrower: use the related-page lookahead instead of full navigation counts; avoid summary-only fields on related-page reads; return the sequence-two identifier from its conditional claim; and stop selecting command bodies that the status mapper does not use. No blanket transaction removal is justified.

## Operation-count convention and batch table

Count explicit Prisma model-method calls and raw queries/statements on successful, non-retried branches, including HTTP installation authentication. Transaction setup/commit, implicit relation expansion, trigger queries and connection acquisition are excluded. A global-client configuration lookup inside the callback is counted separately from transaction-client calls. These are not measured SQL counts, round trips, timings or capacity claims.

| Entry | Route | Source-level calls | Transaction decision |
|---|---|---:|---|
| E27 | GET `/v1/merchant/recoveries/:id/related` | 7 nonempty page; 5 empty related page; 4 missing customer or owned recovery absent | Retain Repeatable Read ownership/page snapshot |
| E28 | GET `/v1/merchant/recovery-summary` | 5 | Currently no transaction; no writes. Consider one coherent narrow SQL projection rather than adding locks |
| E29 | POST `/v1/merchant/conversations/:id/messages` | 11 new HUMAN_TEXT; 16 new follow-up with DB-backed sender configuration (15 with a static sender); 5 replay | Retain Read Committed admission/claim/command transaction |
| E30 | GET `/v1/merchant/conversations/:id/send-commands/:commandId` | 6 for existing command; 5 if owned conversation exists but command does not | Retain Repeatable Read command/assessment snapshot; assess installation share lock separately |
| E31 | GET `/v1/merchant/conversations/:id/follow-up-templates` | 12 full path with DB-backed sender configuration (11 static); 4 when control/recovery status rejects immediately | Retain snapshot; make configuration participation explicit; assess installation share lock |

E27 absent recovery returns 404 at the route; no customer returns a valid empty related list. E29 replay returns the current original command with 200, not a new command. E31 can return an empty list at many earlier eligibility gates; 12 is the complete catalogue path, not every request.

## E27 — Related recoveries

### Current behaviour and invariants

`MerchantRecoveryDetailService.related` uses the same `withOwned` Repeatable Read transaction as summary and message reads. It revalidates Shop and installation, loads the owned recovery, checks customer/conversation bindings, and returns empty immediately if there is no durable customer ID. Otherwise it pages recoveries by exact `(shopId, customerId)` and excludes the selected recovery. Identity is NOT guessed using phone, name or email. [B07-S05:51–96, 151–165; B07-S55:55–62]

The page is newest-first by `(detectedAt, id)`, bounded to five returned rows. The query fetches six. A previous-page query reads the opposite direction then reverses the display. Every nonempty page then counts all newer and older rows only to produce navigation cursors. No exact total is returned. [B07-S06:128–177]

Retain the snapshot, scoped cursor validation and integrity gates. The existing `(shopId, customerId, detectedAt, id)` index matches the query family; it is present in both schema and migration, so another equivalent index is not justified. [B07-S24:390–397; B07-S25; B07-S07:48–85]

### E27-F01 — Unused sixth row plus two exact navigation counts

**Classification:** Confirmed redundant count work; proposed optimisation.
**Priority:** Medium, pending query-plan evidence.
**Owner:** moda_api.

Use lookahead to decide the cursor in the fetched direction. The initial page cannot have a newer page. For a next or previous request, use one bounded existence query for the opposite direction rather than counting the complete matching set.

| Navigation | Previous/newer flag | Next/older flag | Proposed nonempty endpoint calls |
|---|---|---|---:|
| First | false | sixth row exists | 5, down from 7 |
| Next | bounded newer-row existence | sixth row exists | 6, down from 7 |
| Previous | sixth row exists | bounded older-row existence | 6, down from 7 |

Do not assume a supplied boundary row still exists. Preserve empty-page behaviour (both cursors null), timestamp/ID comparisons, tenant/customer predicates, exclusion of the anchor recovery, and cursor format. This proposal excludes any separate identity-read consolidation.

**Limited model check performed:** `woocommerce-api-database-review-07-model-checks.py` compared current count-based rows/navigation with the proposed logic across 972 synthetic datasets and **162,324 cases**, with zero mismatches. It covers tied timestamps, sparse/deleted histories, missing and out-of-range boundaries. It does not execute TypeScript, Prisma, SQL, tenant checks, database collation or concurrent transactions.

**Required validation:** migrated PostgreSQL multi-page related histories; tie boundaries; deleted boundary rows; correct first/next/previous flags; no customer; foreign or inconsistent associations; scope-bound invalid cursors; no history count on the initial page; bounded opposite existence on subsequent pages; actual SQL and index plans.

### E27-F02 — Shared ownership loader fetches summary-only data

**Classification:** Confirmed over-fetching; proposed narrow projection.
**Priority:** Medium.
**Owner:** moda_api.

`related` only needs ownership and the durable customer identity, yet `withOwned` uses a projection containing line-item JSON, prices, milestones, customer names/email, conversation-control fields and initial/follow-up outreach data. [B07-S05:16–35, 83–95, 151–164]

Create a page-specific ownership projection, retaining the recovery's Shop/customer identity and every current customer/conversation integrity comparison. Conversation binding remains checked even though a conversation is not required to display related recoveries. Do not silently change invalid association handling by dropping the relation entirely. Remove only fields not used for either authorization/integrity or the response. This may reduce relation SQL and transferred payload; no measured SQL or byte saving is claimed.

**Tests inspected:** `pages.test.ts:99–115` models 12 related recoveries; its minimal query evaluator only models ordering/boundaries, not complete tenant filtering. `read.service.test.ts` covers missing customers and integrity checks. The enriched-detail PostgreSQL suite has summary/message coverage, not a full related-history pagination proof. [B07-S31; B07-S32; B07-S42]

**Decision:** retain snapshot and exact customer identity; eliminate navigation counts and narrow ownership retrieval.

## E28 — Effective recovery-policy summary

### Current behaviour

Despite its name, this route is not a recovery-count, revenue or history aggregation. It returns effective recovery delay, offer mode, follow-up settings and the selected source (`MERCHANT`/`ADMIN_OVERRIDE`). [B07-S09:16–23, 70–89; B07-S48]

After authentication it launches four independent root-client reads with `Promise.all`: Shop, installation, merchant settings and override. Identity is checked after those reads. It chooses the entire unexpired override when present, otherwise merchant settings, otherwise the existing unconfigured defaults; it validates that chosen policy through the published Shared parser and does not expose the discount identifier. Disabled follow-up has a null delay. It creates no defaults and performs no network/provider call. [B07-S09:37–89]

There is no `$transaction` in the service's database port. Do not incorrectly describe these parallel reads as one Repeatable Read snapshot or as one SQL query.

### E28-F01 — Four narrow reads can be consolidated without adding write locks

**Classification:** Confirmed multiple lookups; optional query/snapshot consolidation.
**Priority:** Low to medium, dependent on polling volume.
**Owner:** moda_api.

The current projections are already narrow. Unlike earlier services, fetching full scalar records is not the issue. A conservative first step is a joined Shop/installation identity projection, reducing 5 to 4 client calls including authentication. Do not simply trust the pre-service principal.

A larger but still bounded design candidate is one parameterized SELECT over the authenticated installation and Shop with optional settings/override joins. That would make identity and both policy candidates one statement snapshot and could reduce the source-level total to 2 calls including authentication. Verify actual SQL; a nested ORM call is not automatically one statement. Preserve all existing identity gates, row-absence semantics, chosen-policy validation, default values, expiry comparison and error handling.

No current transaction must be removed. If separate reads remain and a coherent snapshot is explicitly required, a short read-only Repeatable Read transaction is an alternative, not a write-locking requirement. Current independent observations mean no common cross-table snapshot is guaranteed. Because the implementation selects a whole policy row rather than merging arbitrary fields from merchant and override, this review does NOT assert an internally mixed policy or a proven security exploit. Its role is informational, not a send permit.

Do not introduce cache staleness, lazy creation of settings or an analytics table. Avoid sequentially reading the override first solely to skip merchant settings without measuring the latency trade-off.

**Validation:** retain defaults, current and expired overrides (including boundary), stale/foreign installation checks and no-write behaviour. Test a controlled policy/identity transition if snapshot semantics change. Existing unit tests cover these static branches; the migrated discount-offer suite calls the real summary before/after merchant saves and asserts retained Admin precedence, but does not prove interleaved snapshot behaviour. [B07-S33; B07-S43:80–81, 160–161; B07-S46:43–46]

**Decision:** no unnecessary transaction exists here; consider consolidating the reads, not broadening the endpoint.

## E29 — Durably admit a human message or follow-up

### Current behaviour and exact counts

The route is a command producer, not a WhatsApp sender. API code never calls Meta/OpenAI, publishes Redis, sends a message or charges a recovery credit in this flow. Background owns moderation, final eligibility, dispatch and credit outcomes; the accepted architecture names a PostgreSQL command poller rather than an additional HUMAN-send BullMQ producer. [B07-S56:63–105; B07-S11:72–75, 182–192]

The Read Committed transaction follows Shop lock -> installation share lock -> owned conversation/recovery locks -> shop-scoped replay lookup. A matching existing command is returned before checking changing control mode, restrictions, window or entitlement: retry does not reopen it or claim another follow-up. Identity and conversation ownership are still checked. [B07-S11:18–61, 93–118]

For a new command it checks HUMAN control/revision, merchant restriction, active recovery, recovery-send entitlement, sent initial outreach and recipient reachability. It queries actual provider-identified CUSTOMER inbound after initial outreach, not just `Conversation.lastInboundAt`. For HUMAN_TEXT the service window must be open. For a template it must be closed, the persisted follow-up due time must be due, and an approved catalogue choice must match. [B07-S11:107–150; B07-S15]

A template command additionally inserts sequence two if absent, locks/validates it, claims it conditionally and creates the command referencing that exact attempt, all in one transaction. Do not create sequence three or a second conversation/ledger. [B07-S11:151–192]

| Step | HUMAN_TEXT | Template (DB-backed sender) | Replay |
|---|---:|---:|---:|
| HTTP authentication | 1 | 1 | 1 |
| Transaction Shop/installation validation | 2 | 2 | 2 |
| Owned conversation/recovery | 1 | 1 | 1 |
| Prior command by shop/key | 1 | 1 | 1 |
| Restriction | 1 | 1 | 0 |
| Subscription/entitlement projection | 1 | 1 | 0 |
| Initial outreach lock/read | 1 | 1 | 0 |
| Recipient reachability | 1 | 1 | 0 |
| Verified inbound | 1 | 1 | 0 |
| Sender config via root client | 0 | 1 | 0 |
| Catalogue query via transaction | 0 | 1 | 0 |
| Ensure sequence two exists | 0 | 1 | 0 |
| Lock/read sequence two | 0 | 1 | 0 |
| Conditional sequence-two claim | 0 | 1 | 0 |
| Command create | 1 | 1 | 0 |
| **Total** | **11** | **16** | **5** |

With a static sender stub, template total is 15. The sender lookup is awaited inside the callback but is NOT made on `tx`: see E31-F01. The transaction is necessary even for the one-write text branch because authorization/control and mutable policy reads are coordinated; the Shop lock also fences the absent restriction-row case. Do not trade away this coordination for a smaller count.

### E29-F01 — Shop-scoped idempotency copied into a globally unique claim key

**Classification:** Confirmed scope mismatch; conditional failure inferred directly from schema and writes, not reproduced against PostgreSQL.
**Priority:** High correctness.
**Owners:** architecture coordination, at least moda_api and moda_background; assess Database/Shared and every other producer before selecting a fix.

Commands are unique on `(shopId, idempotencyKey)`, and the request accepts a bounded opaque string (not a mandated globally unique UUID). The template admission assigns `initiationKey: input.idempotencyKey`, while `RecoveryOutreachAttempt.initiationKey` has a global unique index. [B07-S16:8–10, 62–80; B07-S11:98–105, 170–174; B07-S24:439, 633; B07-S26:62, 174]

If shop A has an existing claimed follow-up with key `send-1`, shop B can validly use the same public key for its own conversation. Its command replay lookup finds no A command because it is tenant-scoped. Its follow-up claim nevertheless collides with the global initiation-key index and rolls back. The catch can report `idempotency_conflict` despite there being no conflicting command in B's namespace. This is interference/availability, not disclosure of A's command or proof of incorrect billing.

An API-only prefix/hash is unsafe: Background final admission, replay and cancellation explicitly require `attempt.initiationKey === command.idempotencyKey` or its SQL equivalent. [B07-S53:129–138; B07-S52:494–512; B07-S54:72–80, 148–157]

Define a coherent internal claim identity separate from the public shop-scoped retry key, or deliberately revise the database uniqueness/ownership contract after checking all consumers. Preserve same-shop replay/conflict behaviour, the single recovery sequence-two slot, immutable historical command references, cancellation/reclaim safety, provider-unknown protection and billing idempotency. Do not drop a global constraint or change one producer without coordinating readers/writers.

**Required tests:** two shops with the same request key both independently succeed; same shop same payload replays; same shop changed payload conflicts; opposing automated/human claims remain one winner; cancellation/reclaim and dispatched/unknown claims retain their guards. Current test keys are generated UUIDs, so existing success/race tests do not exercise this cross-shop collision.

### E29-F02 — Sequence-two claim can return its identifier instead of a separate read

**Classification:** Conditional query-consolidation proposal.
**Priority:** Medium, after correctness fixes.
**Owner:** moda_api.

Retain the insert-if-absent, then consider replacing `SELECT ... FOR UPDATE` plus `updateMany` with a single conditional `UPDATE ... RETURNING id` that matches recovery/sequence and every existing pending/unclaimed/no-outbound guard. Require exactly one returned row. The write itself must acquire the claim lock, and the same transaction must still create the linked command. Preserve trigger checks, including rejection of previously sent attempts, and map denials deliberately. PostgreSQL RETURNING supplies the changed row without a separate result lookup. [B07-S11:153–190; B07-S29:54–56; technical T07-01]

Source-level template target is **16 -> 15** with DB configuration, or **15 -> 14** with static sender. Human text and replay counts are unchanged. Do not replace this with an unconditional upsert or reset an already-used claim.

**Required validation:** pre-existing unclaimed sequence two; absent sequence two; simultaneous human/automation claims; zero affected rows; trigger rejection; rollback when command creation fails; historical cancellation/reclaim. Measure emitted SQL and locking before acceptance.

### E29-F03 — Replay and create fetch complete command bodies/state unnecessarily

`findUnique` for replay has no `select`, and command `create` returns a full record. The response only needs identity, kind, state and expected control revision; replay additionally needs payload hash and binding comparisons. Prepared wrapper evidence, text, lease/provider fields and template parameters are not returned or used by this branch. Prefer explicit projections for replay validation and `commandReply`. Do not remove payload comparison. This reduces data retrieval, not explicit call count. [B07-S11:64–69, 98–105, 182–191; B07-S24:594–637]

### E29-F04 — Handled failures lose original Prisma evidence

`P2002` and `P2034` become a new `SendHttpError(409,"idempotency_conflict")` with no cause. Preserve original code/message/safe metadata through the domain error and logger; do not claim every unique violation is a genuine same-shop replay conflict. The global key collision above demonstrates why the constraint/context matters. Unexpected errors already propagate; this is a specific handled-error gap. [B07-S11:193–199; B07-S16:45–48; B07-S17:72–89]

**Decision:** retain transaction and final-dispatch separation. Prioritise claim identity and error fidelity; then consolidate conditional claim and narrow returned fields.

## E30 — Poll send-command status

### Current behaviour

Inside Repeatable Read, the service revalidates Shop/installation, checks owned recovery conversation, reads the command by command ID plus Shop/conversation, and queries the latest matching moderation assessment. It projects bounded state, timestamps, message ID and safe error/reason fields. Missing command is 404, not another tenant's command. No command is mutated. [B07-S12:23–70]

Retain a coherent command/assessment snapshot, tenant predicates, input-kind/digest matching, deterministic assessment order and safe reason mapping. A moderation assessment is not redundant merely because the command row also contains state/failure data.

### E30-F01 — HUMAN_TEXT digest targets original intent, not prepared moderated content

**Classification:** Confirmed source contract mismatch; not yet a migrated-runtime reproduction.
**Priority:** High correctness.
**Owner:** moda_api; validate against canonical Database/Background behaviour without weakening their guards.

Status SQL hashes `c.textBody` for HUMAN_TEXT. The current migration's `arch040_moderation_subject_guard` instead reads `cmd.preparedTextBody`, requires prepared content to exist and checks its SHA-256. Background freezes rendered/passthrough content, verifies that moderation reads those same bytes, and moderates that content. [B07-S12:39–55; B07-S30:175–200; B07-S51:58–115; B07-S52:227–257]

Example: accepted text is `Hello`; prepared customer-visible body is `Example Shop: Hello`. A durable assessment with the prepared-body digest cannot match status SQL's original-body digest. The assessment query returns no row; the status mapper reports `moderation_pending` (and loses the associated moderation reason) even for an ALLOW/BLOCK/REVIEW_REQUIRED decision on the prepared body. Command state or safe failure fields may separately expose some terminal outcome; do not claim the entire command is invariably shown as unsent or that blocked content is dispatched.

Fix HUMAN_TEXT assessment matching to use the exact persisted prepared body. Do not use a raw-body fallback when preparation is absent; absence remains pending/unassessed. Keep the existing canonical template-input function for template commands: the migration explicitly leaves that branch unchanged. Do not remove digest matching or select the newest unrelated assessment. [B07-S30:186–200]

The existing migrated API test freezes **passthrough** content equal to `textBody`, so it cannot reveal the mismatch. It tests a BLOCK only after making both digests identical. [B07-S38:129–165]

**Required validation:** real migrated database, prepared text different from original, all moderation decisions, no prepared content, passthrough, wrong digest/tenant/input kind, canonical template branch, and status changing across separate polls. The review model only illustrates the two SHA-256 expressions; it does not insert assessments or execute HTTP.

### E30-F02 — Body/template columns selected but unused by mapper

The command query selects `textBody`, `templateName`, `templateLanguageCode` and `templateParameters`. The mapper does not consume them: SQL independently computes the digest from the persisted command row. Narrow the first query rather than unnecessarily sending content to application memory, or consider a coherent single SQL command-plus-assessment projection after F01. The conservative projection-only change does not reduce six client calls. Do not implement both alternatives redundantly. [B07-S12:30–54, 63–67]

### E30-F03 — Read helper still share-locks installation

`requireCurrentWooShop(..., false)` removes the Shop write lock but always appends `FOR SHARE` to the installation query. The owned conversation read is non-locking. Thus this status GET is read-only but not free of row locks. [B07-S11:21–39; B07-S12:27–29]

Treat this as a lock-removal candidate only after confirming the authorization contract. A snapshot status response is not dispatch authority; later reads authenticate again. If snapshot-at-read eligibility is sufficient, separate the non-locking GET identity path from the mutation fence while preserving Repeatable Read validation. If credential validity must instead be pinned through the read, document that reason and retain the lock. Removing FOR SHARE alone does not reduce calls. Test reconnect/revocation waits and expected failures before changing it. [Technical T07-03]

**Decision:** fix moderation content identity first. Retain digest/tenant protections and snapshot; narrow returned data; assess rather than blindly delete the installation lock.

## E31 — List eligible follow-up templates

### Current behaviour

This is a read-only preview, not dispatch permission. In Repeatable Read it validates principal/owned recovery conversation, requires HUMAN mode/actionable recovery, checks restrictions and recovery entitlement, reads sent initial outreach/due time, checks reachability and actual inbound evidence, and rejects an already used/claimed sequence-two slot. It then resolves sender WABA and the catalogue. [B07-S13:12–60]

The catalogue uses one bounded joined query across variant, Meta registration, locale and definition. It reads up to 301 rows to detect the 300-row cap, rejects ambiguous purpose/language slots and visible-name collisions, validates publication/review, linked provider identity, approval, freshness and drift, then returns at most 30 `(name, language)` choices. This snapshot deliberately advertises only NO_OFFER because no verified checkout-specific positive-offer reader is supplied. Do not infer missing coupon support is a database-performance bug. [B07-S14:13–15, 38–94, 105–132; B07-S57:49–69]

There are no provider API calls and no write/upsert. Do not create follow-up claims from GET or treat cached/listed choices as authorisation for POST. Both POST and Background revalidate independently.

### E31-F01 — Configuration read escapes the open transaction

**Classification:** Confirmed connection/snapshot boundary; pool-exhaustion risk is an inference, not observed runtime evidence.
**Priority:** High reliability investigation.
**Owners:** moda_api platform-configuration and merchant-service boundaries.

`readEligibleFollowUpChoices(tx,...)` calls `sender.readMessagingSenderWabaId()` with no transaction argument. Production composition captures `input.prisma.platformConfiguration.findUnique` on the root client; `src/index.ts` supplies the same Prisma client to the config reader and merchant services. The query is awaited while the caller transaction is open. [B07-S14:97–105; B07-S20:8–30; B07-S02:21–30; B07-S04:73–77]

This is not a nested SQL transaction and not an HTTP provider call. It is a separate pooled database query that is outside the interactive transaction's connection/snapshot. For E29 it runs while mutation locks are held; for E31 while the installation share lock and Repeatable Read snapshot are open.

An inferred failure mode is a one-connection pool: the transaction retains the only connection, while its callback waits for a root-client query that needs one. Under concurrent unrelated shops the same pattern can consume a larger pool. Timeouts may break the wait, so do not label it a proven permanent deadlock. The deployed pool size, wait times and saturation threshold are unknown. Prisma documents that only calls through the transaction client are in that interactive transaction. [Technical T07-02]

Prefer a transaction-aware read port for the existing configuration service, preserving its unseal mechanism, secret redaction, environment binding, purpose-scoped result and error logging. A deliberately resolved pre-transaction snapshot is another architecture option, but requires an explicit freshness/revalidation contract and must not eagerly read sender config for text sends or replays that currently do not need it. Do not solve by adding a secret cache, duplicating decryption, exposing the full secret, or merely increasing pool size.

This change concerns connection ownership and lock duration, not eliminating the necessary configuration lookup. The full-path count remains 12 until other independent query consolidation is adopted.

**Required validation:** real composition/config reader with small pool and concurrent requests; clean unavailable/decryption outcomes; snapshot changes in sender WABA; no provider/network calls; transaction-bounded reads; continued fail-closed choice validation. Existing PostgreSQL fixtures inject a constant `senderReader`, so they do not exercise this production connection pattern. [B07-S41:50; B07-S40:52–53]

### E31-F02 — All sender failures become empty catalogue results

`catch { return []; }` conflates deliberately unavailable sender configuration, malformed/unseal failures, database unavailability and arbitrary unexpected exceptions. GET can return 200 with no choices; POST can reject a valid chosen template as `template_not_allowed`. A pool/transaction failure may also later surface separately; do not claim every timeout necessarily produces 200. [B07-S14:100–104; B07-S11:148–150]

**Important diagnostic qualification:** the production configuration wrapper already logs typed/unexpected errors with original causes and rethrows. The underlying repository preserves database errors in `ApiPlatformConfigurationError.cause`. Therefore it is false to say the original database error is always unlogged or destroyed here. The problem is that the catalogue catches and suppresses its outcome, obscuring dependency failure versus a legitimate empty business result; custom injected readers need not have that logging. [B07-S20:33–57; B07-S22:33–42; B07-S23:19–27]

Define any intentional disabled/unavailable preview outcome explicitly. Propagate unexpected storage/unseal failures through an appropriate safe error outcome instead of returning indistinguishable absence. Preserve current fail-closed no-send behaviour, original diagnostic causes and bounded/redacted public bodies. Any new public status/reason requires contract/OpenAPI review; do not silently change the schema in a performance patch.

### E31-F03 — Installation read lock shared with status

The same helper described in E30-F03 retains installation FOR SHARE even for `write=false`. Keep preview snapshot semantics, but evaluate whether pinning installation validity during the entire potentially expensive catalogue/configuration read is required. No call-count saving is implied by removing that lock. Do not weaken E29's mutation lock order as a side effect. [B07-S11:21–39; B07-S13:22–24]

### Catalogue safety checks are not redundant joins

Do not push a generic LIMIT 30 ahead of collision/overflow detection, replace LEFT JOINs with inner joins that hide invalid assignments, select only superficially approved registration rows, or fetch one template per locale in a loop. Those changes can change ambiguity/fail-closed semantics or introduce N+1 queries. `variantId` is selected but not directly used by the public mapper; trimming this one scalar is minor compared with the confirmed connection/error issues. No speculative index is required by the inspected bounded query. [B07-S14:63–94, 105–132; B07-S35:28–58]

**Decision:** retain read-only preview checks and bounded registered-template query. Address the escaped configuration read and failure classification before speculative query-count reduction.

## Cross-endpoint priorities and ownership

| Priority | Finding | Reason | Ownership |
|---|---|---|---|
| High | E30-F01 | Status does not match canonical prepared-content moderation | API correction; canonical Database/Background compatibility tests |
| High | E29-F01 | Tenant-scoped public key can collide in global claim identity | Architect-coordinated producer/consumer/schema decision; API and Background at minimum |
| High investigation | E31-F01 / F02 | Extra connection while locks are held; dependency failure reported as no choice | API configuration and merchant services; preserve Shared security/logging |
| Medium | E27-F01 / F02 | Unnecessary exact counts and summary data on a paginated read | API |
| Medium | E29-F02 / F04 | Conditional claim result reuse; original conflict evidence | API |
| Lower | E28-F01 / E29-F03 / E30-F02 | Read consolidation/projection narrowing | API; measure workloads |
| Contract-dependent | E30-F03 / E31-F03 | Read-only installation share locks | API; concurrency validation before removal |

No new infrastructure, outbox, queue, database index or schema migration is approved by this record. E29-F01 may require Database and Shared work depending on the chosen identity contract; the report deliberately does not prescribe an isolated API patch. No accepted task has been reopened or silently reclassified by this static review.

## Validation performed and limitations

**Performed:** inspected route composition, services, constraints/migrations, Background prepared-content/dispatch/cancellation consumers, unit/integration tests and their runners; derived the explicit call tables; verified all 58 evidence source files byte-for-byte against the uploaded ZIP; ran the dependency-free related-pagination and digest-expression models; checked package contents/checksums.

**Not performed:** application TypeScript/unit tests, Prisma-generated-client checks, PostgreSQL execution, migrations, query plans, connection-pool stress tests, concurrent HTTP/provider scenarios or latency/throughput benchmarks. `moda-interact-api/node_modules` is absent; Docker and psql are unavailable; available Node is v22.16.0 while the snapshot declares 24.19.0. No substitute Node version or dependencies were installed and no live service was contacted.

`node scripts/test-arch040-woo-human-send-postgres.mjs` is the existing harness. It discovers/validates the accepted canonical schema, deploys migrations and runs the command, follow-up-policy, catalogue and enriched-detail suites. It is included by the repository's aggregate integration script. Existing task records report historical passes; those are not new execution by this review. [B07-S44:9–25, 55–66; B07-S45; B07-S47; B07-S57]

The suite already covers many admission/window/race/replay and safe catalogue behaviours. Its sender stub and passthrough moderation fixture leave the newly identified full-composition pool and wrapped-body status cases untested. Related pagination additionally needs real database multi-page coverage rather than only the minimal boundary model.

The code comments saying the pinned schema predates ARCH-047 are not proof of current archive state. The root and API nested schema files are byte-identical in this uploaded snapshot (SHA-256 `45df5e44bdc1e7e29495e391a1754477f0df362c667d648f4b6893b6541f5c0d`). The report follows inspected migrations and composition rather than extrapolating from that historical comment.

## External technical cross-checks — not application evidence

Checked 2 November 2026. The uploaded source is the basis for application findings; the following official references only validate database/framework semantics used in proposals:

- **T07-01:** PostgreSQL 17 RETURNING, `https://www.postgresql.org/docs/17/dml-returning.html` and UPDATE, `https://www.postgresql.org/docs/17/sql-update.html` — conditional updates can return modified-row fields without a separate result query.
- **T07-02:** Prisma ORM v6 interactive transactions, `https://www.prisma.io/docs/orm/v6/prisma-client/queries/transactions` — transaction-client calls use that transaction; long-held transactions and extra work deserve caution. This review uses the v6 documentation appropriate to the pinned client, not current unrelated ORM APIs.
- **T07-03:** PostgreSQL 17 explicit locking, `https://www.postgresql.org/docs/17/explicit-locking.html` — FOR SHARE conflicts with updates; a read-only endpoint can still hold row locks.
- **T07-04:** PostgreSQL 17 transaction isolation, `https://www.postgresql.org/docs/17/transaction-iso.html` — independent reads are not a common transaction snapshot; Repeatable Read preserves one snapshot across reads.
- **T07-05:** PostgreSQL 17 EXISTS, `https://www.postgresql.org/docs/17/functions-subquery.html` — an existence check needs only establish one matching row rather than compute the full count.

## Next increment — not yet reviewed in this record

E32 POST `/v1/merchant/conversations/:id/control`; E33 GET `/v1/merchant/merchant-knowledge`; E34 POST `/v1/merchant/merchant-knowledge/sources`; E35 PATCH `/v1/merchant/merchant-knowledge/sources/:id`; E36 DELETE `/v1/merchant/merchant-knowledge/sources/:id`.

No repository source, database schema, architecture/task status or `docs/decisions/**/_index.md` was edited. No application patch, branch, commit, push or task materialisation was produced.

---

# Increment 08 — conversation control and Merchant Knowledge sources (E32–E36)

**Review date:** 2 November 2026.
**Coverage after this increment:** 36 of the original 61 endpoint method/path combinations; 25 remain.
**Scope:** Conversation control POST; Merchant Knowledge GET; web-source create, patch and delete. Refresh, ordering and uploaded-file commands are not counted as reviewed in this increment, even where common helpers were inspected.
**Status:** Static source findings, proposed changes and one explicitly limited review-only position model. No implementation or architect acceptance.
**Evidence:** `woocommerce-api-database-review-08-source-evidence.txt`, identifiers B08-S01–B08-S40, with original line numbers. `woocommerce-api-database-review-08-source-manifest.json` verifies reproduced files against the exact uploaded archive. Relevant sections, not every line of every reproduced file, were inspected.

## Summary and counting conventions

The highest-priority correctness finding is the separation between the Shop lock used by API knowledge commands and the source-row lock used by Background generation advancement. PATCH and DELETE check generation in application code, but their later mutation predicates do not include it. Retain transaction atomicity while addressing that gap. The clearest performance opportunities are redundant locked-identity rereads, an unused writer-side preference lookup, the active-revision aggregate/fetch pair and unconditional all-source position rewrites.

Counts below are explicit Prisma model-method calls plus raw SQL/lock calls on a successful non-retried path. They include HTTP authentication where indicated, but exclude `$transaction` control, BEGIN/COMMIT/isolation statements, relation-query expansion, constraint/trigger/FK work and retry amplification. These are not SQL statements, network round trips, rows modified, measured latency or capacity. [B08-S01–S03, S19–S21, S27]

For the knowledge command rows, `R` is the full first-page post-commit read projection **without another HTTP authentication call**. Under a stable valid entitlement, an active MERCHANT_OPT_IN feature, at least one allowed source type, and database-backed upload configuration:

- `R = 10` for an empty source page;
- `R = 11` for a nonempty page with no ACTIVE revision;
- `R = 12` for a nonempty page with at least one ACTIVE revision.

An absent/static upload-configuration reader removes one call from R. Other entitlement/feature states can skip further calls; these are conditional examples, not universal totals. A later GET page also counts preceding eligible sources. Writes can race with the later best-effort response and therefore change its branch. [B08-S02:38–75,102–115,129–213]

| Entry | Method/path | Current explicit calls | Decision |
|---|---|---|---|
| E32 | POST `/v1/merchant/conversations/:id/control` | 7 changed to HUMAN; 6 changed to AI; 5 current-revision HUMAN no-op; 4 AI no-op | Retain transaction, locks, revision checks and audit; preserve handled causes |
| E33 | GET `/v1/merchant/merchant-knowledge` | 13 first page / 14 later page when ACTIVE evidence is found; 12 / 13 if page nonempty but no ACTIVE evidence; 11 empty first page | Preserve explicit best-effort/no-transaction design; consolidate ACTIVE lookup |
| E34 | POST `/v1/merchant/merchant-knowledge/sources` | `1 authentication + 11 transaction + R`; exact duplicate `1 + 9 + R` | Keep source/revision atomicity and post-commit boundary; reduce common guard work |
| E35 | PATCH `/v1/merchant/merchant-knowledge/sources/:id` | `1 + 8 + R` no-op; `1 + 9 + R` metadata; `1 + 10 + R` URL change | Strengthen generation predicate; retain no-op/metadata semantics |
| E36 | DELETE `/v1/merchant/merchant-knowledge/sources/:id` | `1 + (9 + 2n) + R`, with n surviving sources | Strengthen generation predicate; compact only necessary positions, preferably in bounded batches |

Example: an initial fresh create, with its only revision still PENDING, makes 23 calls under these assumptions (1 + 11 + 11). A changed metadata patch whose response contains ACTIVE evidence makes 22 (1 + 9 + 12). Deleting one of 100 sources while the response still has ACTIVE evidence makes 220 calls (1 + 9 + 198 + 12); 198 are survivor position updates. These are source-derived examples, not traffic observations. Shared currently allows 1–100 entitled knowledge sources; the create helper separately refuses new rows when total retained sources reaches 1,000. Do not confuse an eligible-source limit with a claim that all retained rows remain eligible. [B08-S03:79–88,106–174; S39:45–55]

## E32 — POST /v1/merchant/conversations/:id/control

### Current flow and retained transaction

The Read Committed transaction locks Shop FOR UPDATE, rechecks/share-locks installation, then locks the recovery-linked Conversation FOR UPDATE and its CheckoutRecovery FOR SHARE. Ownership comes from CheckoutRecovery.shopId; nullable Conversation.shopId is not an alternative authorization source. It validates the expected control revision before same-mode handling. HUMAN targets additionally read ShopHumanMessagingRestriction, including an already-HUMAN no-op; explicit Resume AI does not run that restriction lookup. [B08-S01:33–89]

A real transition conditionally changes mode/revision/time, clears pending AI/processing state, advances lastProcessedVersion to the locked inboundVersion, and inserts exactly one ConversationControlEvent. It computes the response from the validated transition without another SELECT. No message, follow-up, credit mutation, queue action or external call occurs here. [B08-S01:90–114; S38:62–93]

**Retain the transaction and current locks.** The canonical migration requires matching, contiguous audit history and forbids no-op revision/time changes. Shop locking is meaningful coordination with the absent-restriction-row case, not a gratuitous extra lookup. The existing PostgreSQL test explicitly holds that Shop lock while inserting the first suspension and verifies takeover waits and then fails; it also tests inbound-row contention, stale revisions, no-op audit counts and rotated/revoked credentials. [B08-S18:184–248; S17:118–184,195–273]

Do not skip the restriction lookup merely because a HUMAN request is same-mode: the current suspended same-mode request is intentionally rejected. Do not allow stale same-mode retries. Preserve monotonic timestamps, maximum revision handling and invalidation of pending AI work. No mandatory query-count reduction is established for this endpoint.

### E32-F01 — Handled persistence conflicts lose their original causes

**Classification:** Confirmed diagnostic gap. **Priority:** Medium. **Owner:** moda_api.

P2002/P2034 are replaced by ConversationControlConflictError without carrying the original exception. The route records error/cause fields but the original cause is already absent. Preserve the actual Prisma code/message and safely bounded metadata through typed wrapping and the existing shared logger. Keep the public conflict contract; do not automatically replay a command against a newer revision. [B08-S01:115–120; S07:52–59; S33:298–349]

### Validation

Keep and rerun the migrated PostgreSQL control suite, including Shop-before-conversation coordination, foreign/standalone rejection, nullable direct Shop identity, immutable/contiguous audit, same-mode no-op versus stale conflict, suspension/resume and credential races. Add distinctive original-error/redaction assertions for the handled-conflict branch. The dedicated runner deploys actual migrations and is registered in aggregate integration validation. These are inspected test sources, not results from this review. [B08-S17; S26:38–49; S23:18,27]

## E33 — GET /v1/merchant/merchant-knowledge

### Current contract — deliberately best-effort, without a read transaction

Unlike several earlier reviewed GETs, this service explicitly promises a best-effort multi-query projection without connection pinning. Its unit fake throws if `$transaction` is invoked. Do not silently impose Repeatable Read merely for uniformity with other endpoints. Writers independently validate entitlement and mutation authority. [B08-S02:118–121; S16:76–80,109,211]

It reads upload policy, current principal, plan mapping and opt-in state, total source count, allowed catalogue, a page of at most 100 rows plus lookahead, plan-eligible count, preceding eligible count on later pages, and ACTIVE evidence for the returned source IDs. Latest and ACTIVE revisions are deliberately distinct: an older ACTIVE revision can remain available while a newer revision is PENDING or FAILED. A disabled preference or missing plan must not hide configured source history. All-source, type-eligible and preceding-eligible counts have different meanings and are not interchangeable. [B08-S02:129–213; S10:99–141; S11:5–6; S32:5–31]

The public projection strips sensitive URL query/fragment data and storage locations and allowlists failure codes. Do not fetch normalized content/embeddings to optimise this metadata view, drop tenant binding, or replace ACTIVE with latest generation. Existing queries are already bounded/narrow in these areas. [B08-S10:15–55,99–141]

### E33-F01 — ACTIVE generation aggregate is unnecessary under the canonical index

**Classification:** Confirmed redundant aggregate/fetch pattern under migrated schema. **Priority:** Medium. **Owner:** moda_api; Database validates existing constraint, no new schema required.

`readActiveRevisions()` first groups ACTIVE revisions by source and obtains max(generation), then fetches those source/generation combinations. The migration already has a UNIQUE partial index on sourceId WHERE status='ACTIVE', so a source cannot have multiple committed ACTIVE rows. Query the returned page's source IDs and ACTIVE status once, selecting only the existing public fields. [B08-S02:102–115; S12:221–228]

A partial unique index enforces uniqueness among rows satisfying its predicate; it is not merely a performance hint. This is a technical cross-check, not additional application evidence. [EXT08-2]

Expected reduction: one explicit call when an ACTIVE row exists (GET first page 13 -> 12, later page 14 -> 13; post-command R 12 -> 11). Nonempty/no-ACTIVE remains one revision query; empty pages remain zero. The direct query also avoids the specific gap in which an ACTIVE generation changes between the aggregate and its follow-up fetch, without promising a transactionally frozen full response.

Use the migrated-schema suite because this partial unique index is not represented as a Prisma @@unique declaration. Do not compensate for a missing migration by keeping max(generation) and silently tolerating multiple ACTIVE rows. Preserve at most one ACTIVE result per source, exact page IDs, tenant-derived scope, old-active/new-pending history and redacted projections. [B08-S22:4234–4264; S29:58–96]

### E33-F02 — Read exceptions are reclassified without their original error

**Classification:** Confirmed diagnostic gap. **Priority:** Medium. **Owner:** moda_api.

Unknown database/provider exceptions become a new MerchantKnowledgeReadError(503, merchant_knowledge_unavailable) without a cause. The safe response should remain unavailable rather than falsely unentitled, but source/count/revision errors need their original diagnostic details retained internally. The route already logs safe contextual fields; preserve the source exception through the wrapper instead of inventing a competing logger. Some platform-configuration failures are logged at their owning layer before wrapping, so do not claim all upstream logging is absent. [B08-S02:214–218; S06:54–73; S28:40–56; S33]

### Other bounded candidates and validation

The two identity lookups can potentially be joined with all original checks/default-language retrieval preserved; measure actual SQL rather than count a nested projection as automatically one statement. This is optional after the direct ACTIVE-query correction. Do not indiscriminately remove the three source counts: they feed different visible fields and allowance ranking.

Existing unit tests cover 105-row pagination, explicit no-transaction behaviour and safe projections. The migrated read fixture covers two same-Shop sources, foreign-Shop exclusion, older ACTIVE/newer FAILED, upload metadata, feature-off and plan-loss states, invalid config and credential rotation. It does not validate concurrent active promotion between the two old queries or large-history query plans. [B08-S16:84–114,151–234; S29]

## Shared command guard findings affecting E34–E36

### E34-F01 — Lock results discard identity fields, then reread both rows

**Classification:** Confirmed redundant reads. **Priority:** Medium. **Owner:** moda_api.

`lockedEntitlement()` first SELECTs only Shop.id FOR UPDATE and installation.id FOR SHARE. It then invokes `assertWooPrincipal()`, which issues two more queries for fields from those same locked rows. Extend the two lock queries to return the required fields and validate those returned rows, including defaultLanguageTag. Keep Shop first, installation second, the existing lock modes and all status/platform/domain/version/revocation checks. Never substitute the pre-transaction principal's assumed current state. [B08-S03:15–33; S02:15–34]

This removes two transaction-local model calls per successful command without removing a lock or authorization check. It does not authorise merging these lock queries in a way that changes lock ordering.

### E34-F02 — Writer reads merchant activation preference but does not use it

**Classification:** Confirmed unnecessary writer-side preference read under the current contract. **Priority:** Medium. **Owner:** moda_api.

`readEntitlement()` reads subscription, feature and ShopFeaturePreference. The writer destructures only configuration; activation preference is deliberately not a mutation gate because an entitled merchant can configure sources while the preference is off. Avoid the preference lookup in the command-only eligibility path while sharing the actual plan/mapping validation. Retain the lookup in GET and its post-action response because merchantEnabled/processingEligible are visible fields. Do not weaken plan/source-type/limit enforcement or conflate opt-in with entitlement. [B08-S02:38–75; S03:34–36; S09:41–45,83–85; S32:45–46]

With F01 and F02, the common command guard decreases from seven calls to four: two lock/identity queries and subscription plus feature reads. CREATE's transaction target becomes 11 -> 8 calls, with duplicate create 9 -> 6. PATCH/DELETE inherit the three-call saving, but their final targets also depend on the generation correction below. No claimed latency percentage.

### E34-F03 — All-source revision retrieval should be narrowed by operation, not blindly removed

**Classification:** Confirmed broad peer-data read; optimisation candidate pending plans/size measurements. **Priority:** Low/medium. **Owner:** moda_api.

The common `sources()` query fetches names, languages, positions, generations, type relationships and latest revision URL/status for every Shop-owned source. CREATE uses content equality for retry detection, so its existing lookup has a real purpose. PATCH needs target details and the ordered eligible-source membership; DELETE needs target type/generation and survivor ordering but not every peer's latest revision URL. A targeted projection/rank query can avoid loading peer revision graphs. Do not replace it with one revision query per peer, lose dormant-source ordering or assume one Prisma relation query is one SQL statement. The current findMany has no take; the create-only 1,000-row guard is not a database-wide bound on every historical/imported collection. [B08-S03:39–60,106–174]

## E34 — POST /v1/merchant/merchant-knowledge/sources

### Current flow and transaction — retain

The 12-second-timeout Read Committed transaction obtains locked entitlement, validates the purpose/WEB_PAGE pair, resolves language, reads the Shop's sources and checks exact content equality. A duplicate returns the existing source ID and created=false before allocating another source. A new create enforces eligible-source capacity and the retained-row safety guard, allocates a position, inserts the source at generation 1 and inserts its PENDING CREATE revision. [B08-S03:95–124]

These two writes must commit together. The durable revision is the asynchronous handoff: Background reconciliation scans PENDING work, checks current generation/activation/entitlement and enqueues the existing shared contract. The API performs no HTTP fetch, R2 operation or Redis publication inside the transaction. Preserve this architecture instead of inventing an outbox table or synchronous queue requirement. [B08-S03:65–70; S30:45–86; S31:147–190; S09:100–105]

Exact duplicate create is intentionally checked before the capacity denial, but after live entitlement/pair checks. Preserve that order so retrying an already-created source at capacity does not allocate or erroneously demand another slot. Keep URL admission/SSRF boundary and tenant source identity unchanged. [B08-S03:108–121; S04:36–70]

Primary improvements are shared findings F01/F02 and later peer-projection narrowing. The response refresh described next is outside the transaction and is already required by the task/OpenAPI; do not delete it as an unexplained duplicate call.

## Cross-cutting command/response finding — C08-F01

### A committed mutation can be followed by a failed HTTP response

**Classification:** Confirmed boundary; failure/interleaving consequence is source-derived, not runtime reproduced. **Priority:** Medium/high for explicit retry handling. **Owner:** moda_api, with architecture approval for any wire-contract change.

All three commands await `transact()` and then call the full first-page `readService.read()` on the root client. Upload configuration is read there too. If configuration, source projection or another read fails after commit, the route returns a failure even though the source mutation is durable. A rotation between commit and projection can similarly invalidate the response recheck. [B08-S03:102–104,123–124,144–145,173–174; S02:134–146,214–218; S05:62–95; S19:88–93]

This is not a partial database commit, nor a nested root-client query while a writer connection is held. The response is explicitly documented as a projection **after commit**. [B08-S32:344–351; S09:70–71]

Consequences differ by operation: an unchanged exact create retry is deduplicated; a committed URL change advances generation so retrying the old expectedGeneration conflicts; a committed delete leaves the source absent and the retry returns 404. Metadata/no-op requests have their own semantics. Do not tell clients a response error proves rollback, or silently change these responses into success without durable evidence.

Add deterministic post-commit read-failure tests and stage-aware logs recording commit outcome separately from response projection. Retain source ID/correlation internally where safe. Any decision to return durable acknowledgement separately from refresh requires an explicit API/client contract amendment; do not introduce a receipt table or move the full configuration-backed view into the write transaction automatically. No source/URL/credential leakage in diagnostics.

Because command `response()` calls the reader directly, not the GET route, it does not run GET authentication again and does not currently pass the reader's phase-timing collector or emit its route's read-success event. The command route records overall duration. Measure write duration and response-projection duration separately using the existing shared logging/timing mechanism before attributing total latency to transaction work. [B08-S03:102–104; S02:129–146; S05:67–68; S06:43–51]

## E35 — PATCH /v1/merchant/merchant-knowledge/sources/:id

### Current flow and behaviours to retain

After locked entitlement and the source collection read, it requires an owned WEB_PAGE, checks expectedGeneration and top-of-allowance eligibility, then compares effective name/language/URL with current values. An identical request does not write. Metadata-only edits write the source without creating another ingestion generation; URL changes increment currentGeneration and append a PENDING URL_CHANGE revision in the same transaction. Older ACTIVE history is retained. [B08-S03:126–145; S15:53–67]

Preserve the transaction: URL/generation/revision changes must not partially commit. Preserve generation-before-no-op checking; do not turn generation into a new metadata-revision contract as an incidental refactor. Concurrent metadata edits that do not change generation are a distinct last-writer policy, not covered by a generation token.

### E35-F01 — Generation is checked before, but not on, the actual source write

**Classification:** Source-supported cross-writer concurrency risk. **Priority:** High. **Owner:** moda_api; validate against the real Background writer; no schema change currently justified.

The API's `checkGeneration()` reads the earlier source projection, but the later update's WHERE contains only the source ID. The Shop lock serializes cooperating API writers, not every writer of currentGeneration. Background's entitlement reconciliation has a different path: it locks MerchantKnowledgeSource FOR UPDATE, checks current eligibility and content-limit change, conditionally increments currentGeneration and creates an ENTITLEMENT_CHANGE revision. That path does not acquire the API's Shop lock. [B08-S03:15–25,62–64,128–143; S13:138–162,197–284; S31:124–190]

A possible interleaving is API reads/checks generation g; Background commits g+1 while the API still holds Shop; API metadata update by ID then succeeds against g+1 without checking the supplied g again. The mismatch is at the durable mutation predicate, not tenant binding. [Source-derived inference from the above code.]

Use a tenant-bound conditional mutation that includes expected currentGeneration and requires one affected row, or introduce a correctly ordered source-row lock and revalidate the freshly locked row. PostgreSQL re-evaluates an UPDATE/DELETE WHERE condition on the updated row after a conflicting writer commits; a generation condition must actually be present to obtain that protection. [EXT08-1]

For URL changes, retain the returned/validated next generation and atomic revision insert. A racing increment currently tends to collide with the unique source/generation revision key and roll back; do not describe that as silent committed URL-history corruption. Metadata-only mutations lack that extra revision uniqueness backstop. [B08-S03:140–143; S12:215]

The existing integration suite tests stale generation already present before the call and concurrent API refreshes, but does not interleave this Background replacement between the API read and write. Add barrier-controlled tests with the actual generation writer for metadata update, URL change, rollback and no-op behavior. [B08-S15:53–79]

## E36 — DELETE /v1/merchant/merchant-knowledge/sources/:id

### Current flow and atomicity — retain

The service performs the same locked entitlement/source checks, validates expectedGeneration and source eligibility, deletes the source, and compacts every surviving source's position before commit. The source FK cascades to revisions, and revision deletion cascades to chunks; the single explicit delete call is not a measure of rows deleted or the total database cost. No remote-object deletion runs in this WEB_PAGE transaction. [B08-S03:163–174; S12:215–219,249–250]

Keep the source deletion, history deletion and deterministic survivor order atomic. A rollback during compaction must restore the deleted source and its history as well as positions. Preserve current authorization and dormant-source rules; changing who can delete an ineligible source is a policy change outside this review.

### E36-F01 — DELETE shares the cross-writer generation gap

**Classification:** Source-supported stale-delete risk; not reproduced. **Priority:** High. **Owner:** moda_api.

After checking expectedGeneration in memory, the delete predicate is only `{id}`. The same Background interleaving described in E35-F01 can advance the source before DELETE obtains its row lock. The stale delete can then remove the newer source and its newly committed revision. [B08-S03:167–170; S13:197–284; S12:215–219]

Use a tenant/generation-bound delete with exactly-one result (and rollback on zero) or locked source revalidation. Do not treat every zero result as a successful replay or silently delete a newer generation. Add the real concurrent Background-generation test and retained foreign/missing/generation response tests. The request format already supplies expectedGeneration, and OpenAPI already describes generation mismatch as a conflict. [B08-S04:58–64,80–82; S32:362–366]

### E36-F02 — Compaction updates every survivor twice, even unchanged rows

**Classification:** Confirmed write amplification. **Priority:** Medium/high for larger collections. **Owner:** moda_api; validate existing Database constraints, no speculative new index.

`compact()` stages each survivor at 1,000,000,000 + index with an individual update, then writes each final position using another individual updateMany. Therefore n survivors cost 2n additional model calls, even when deleting the last source leaves every remaining position already correct. Each ordinary Prisma update also involves the model's updatedAt behaviour; changing to raw SQL requires an explicit compatible timestamp/fencing decision. [B08-S03:79–88,170–172; S22:4210–4227]

Example: remove the final source from a contiguous eligible collection of 100; the existing code issues 198 unnecessary survivor-position updates. Remove the first and all 99 survivors genuinely need new positions, but per-row round trips can still be batched. The mutation transaction's configured timeout is 12 seconds; no timeout was observed or predicted from this count alone. [B08-S03:95–96]

**Recommended sequence:** compute deterministic final positions from the full surviving order, identify only rows whose positions change, and skip all compaction writes when none change. When moves exist, use bounded set-based staging/finalisation or an equivalent reviewed method; validate affected identities/cardinality and preserve Shop coordination, nonnegative positions, integer bounds and unique (shopId, position).

Do not blindly replace this with one UPDATE position=position-1 or negative temporary positions. The nonnegative CHECK and immediate unique constraint explain why staging exists; PostgreSQL checks non-deferrable uniqueness immediately, so removing the two-phase safety argument is not a valid optimisation. [B08-S12:165,175; EXT08-3]

**Model evidence:** `woocommerce-api-database-review-08-compaction-check.py` compared all-row two-pass compaction against changed-only two-pass compaction in 21,807 cases with no mismatches. It checked final positions, unique/nonnegative positions after every simulated row update, contiguous/gapped positions, deletion boundaries and larger examples. It did not execute SQL, Prisma, database locks, timestamps, Background interaction or a batched implementation. The SQL batching suggestion remains unimplemented and unvalidated.

Existing command PostgreSQL tests compact only a tiny collection. Add migrated tests for first/middle/last deletion, gapped order, unchanged-prefix timestamps, staging rollback, survivor identity/cardinality, more retained dormant rows, queued worker/source deletion races, source revision/chunk cascades and realistic statement/lock-duration counts. [B08-S15:80–94]

## Shared handled-error finding for E34–E36

The command transaction helper converts P2002/P2034 into a new generic conflict with no cause. Unexpected errors are rethrown, so not all failures are swallowed; the handled branch nevertheless hides the actual constraint/conflict diagnosis. This is material to distinguishing a concurrent generation conflict from a programming/constraint error in a future compaction rewrite. Preserve the original error through safe domain wrapping and the existing route logger; emit explicit commit-versus-projection stage for C08-F01. Never replace provider or Prisma wording with a guessed explanation. [B08-S03:95–100; S04:22–28; S05:70–95; S33:298–349]

## Validation, priorities, ownership and next scope

### Verified during this increment

- Read actual source, request/response contracts, relevant migrations, unit/integration tests, Background generation/reconciliation/activation paths and published-Shared source version identity in the supplied snapshot.
- Derived path-specific model/raw-query counts with post-commit projection work separated from write transactions.
- Ran only the pure-Python compaction model: 21,807 cases, zero mismatches; limitations are recorded above and in its JSON result.
- Verified all 40 reproduced evidence source files byte-for-byte against the uploaded archive and recorded SHA-256 values. The archive SHA-256 matches the prior review baseline.

### Not executed

No application test, Node test runner, PostgreSQL test, migration deployment, EXPLAIN, emitted-SQL query count, latency/lock/pool benchmark or concurrency reproduction was run. Current environment: Node v22.16.0 versus repository requirement 24.19.0; API node_modules absent; Docker and psql commands absent. No environment/toolchain installation or substituted production database was attempted. [B08-S23:6–9]

### Existing validation to extend, not replace

Both the control and knowledge PostgreSQL runners deploy the actual canonical migrations and are registered in package.json's aggregate integration command. Existing suites provide useful concurrency, tenant isolation, durable pending revision, opt-in-off configuration, history and ordering coverage. Historical task Completion Reports record older successful runs, but these are not results of this review. Their fixtures do not establish the new Background-generation race, post-commit read failure, large compaction cost or ACTIVE-query optimization. [B08-S25:35–44; S26:39–49; S23:18,22,27; S15–S17,S29]

### Proposed correction ordering

1. Correct PATCH/DELETE generation fencing against the real Background writer; retain atomic revision/delete/order changes.
2. Define and test committed-command versus failed-response-refresh behaviour, including operation-specific retries and safe stage diagnostics.
3. Reduce command guard 7 -> 4 calls without removing locks or entitlement; preserve original errors.
4. Replace ACTIVE aggregate/fetch with one page-bounded query under the existing partial unique index.
5. Avoid unchanged-position updates, then validate bounded batching; measure realistic database work and lock duration.
6. Consider operation-specific peer projections and joined read-only identity validation only when their SQL/bytes benefit is established.

Most implementation belongs to moda_api. Background involvement is primarily the real-writer concurrency test/contract validation; do not casually change another service's locking. Database ownership remains with moda_database for any actual schema change, but none is currently justified by these optimisations. No new infrastructure/Gateway task, Shared publication, index, outbox, queue or service is required solely by the current evidence. Any command-response contract amendment requires explicit architecture and Woo client coordination. No task status was changed or accepted.

**Next five endpoints:** POST source refresh; PUT source order; POST upload intents; POST upload finalise; PATCH uploaded-source metadata. Upload reprocess remains for a subsequent increment.

## External technical cross-checks — not evidence of application behaviour

- **EXT08-1:** PostgreSQL 17, Transaction Isolation, Read Committed, checked 2 November 2026: `https://www.postgresql.org/docs/17/transaction-iso.html` — UPDATE/DELETE re-evaluation after a concurrent row change; application WHERE must include the condition to protect.
- **EXT08-2:** PostgreSQL 17, Partial Indexes, checked 2 November 2026: `https://www.postgresql.org/docs/17/indexes-partial.html` — a partial unique index enforces uniqueness for qualifying rows.
- **EXT08-3:** PostgreSQL 17, SET CONSTRAINTS, checked 2 November 2026: `https://www.postgresql.org/docs/17/sql-set-constraints.html` — immediate non-deferrable uniqueness and nonnegative CHECK considerations for ordered-position updates.

The uploaded source establishes the current code, task contracts and migrations. These external references explain database semantics only; the proposed interleavings and improvements are explicitly architectural inferences, not claims of runtime reproduction.

---

# Increment 09 — refresh, order and uploaded-file admission (E37–E41)

**Review date:** 2 November 2026.
**Coverage:** E37–E41; 41 of the original 61 method/path combinations reviewed; 20 remain.
**Status:** Source-based architectural assessment, not implementation acceptance. No application source or task state was changed.
**Evidence:** `woocommerce-api-database-review-09-source-evidence.txt`, references B09-S01–B09-S40; original file line numbers follow each pipe. The manifest verifies all 40 files byte-for-byte against the original uploaded archive.
**Review-only model:** `woocommerce-api-database-review-09-order-check.py` and its JSON result; 23,650 logical order cases, not application or database tests.

## Executive assessment

The highest-priority issue is finalisation/cleanup coordination. Finalisation reads a pending asset without locking that asset, checks expiry, then eventually updates it by ID alone. Background cleanup locks the asset, tombstones expired unreferenced uploads and deletes their R2 object after committing. A finalisation transaction that passes its last expiry check just before expiry can be overtaken by cleanup, then overwrite DELETED with AVAILABLE and create a revision for an object cleanup is deleting. This is a source-supported concurrency scenario, not a runtime reproduction. The API's Shop lock does not exclude that asset-scoped Background writer. [B09-S05:200–247; B09-S17:83–147]

Two additional lifecycle issues deserve explicit corrections: finalisation replay selects an arbitrary revision by uploadedAssetId despite legitimate reuse by reprocessing; and the intent's documented changed-metadata conflict rule does not bind purposeKey. Finalisation also re-reads accepted MIME types after R2 verification but fails to apply the MIME-membership check in its committing branch. These are not reasons to remove the post-network checks or put R2 inside a database transaction. [B09-S05:125–149, 170–217, 264–297; B09-S34:140–161, 235–267; B09-S35]

The most direct efficiency opportunities are changed-row-only reordering, using narrow order projections, preserving the three-call common web-command reduction identified in increment 08, bounding existing-upload eligibility selection, and avoiding identical metadata writes. Upload identity validation already returns the fields needed from its lock queries and its entitlement helper already avoids the unused preference query; do not apply the web helper diagnosis to it indiscriminately. [B09-S01:15–36, 79–88, 176–184; B09-S05:17–83, 253–261]

## Operation-count convention and summary

Counts are explicit Prisma model calls and raw-query calls on successful, non-retried paths, including HTTP installation authentication. They exclude transaction-control statements, relation-query expansion, database-trigger/foreign-key work, provider calls, internal SDK operations and retries. They do not measure SQL statements, network round trips, row visits, lock waits or latency.

`R` means the ordinary full first-page knowledge response after a web command commits, without another HTTP-authentication call. With valid entitlement, at least one allowed pair, an active feature, and database-backed upload policy, R is 10 for an empty page, 11 for a nonempty page without ACTIVE evidence, or 12 with ACTIVE evidence. Other entitlement/configuration branches differ. This is the unchanged source count, not the count after proposed prior-increment improvements. [B09-S04:129–218]

| Entry | Endpoint | Current explicit calls | Transaction decision |
|---|---|---|---|
| E37 | POST `/v1/merchant/merchant-knowledge/sources/:id/refresh` | 1 + 10 + R when appending; 1 + 8 + R when current work is PENDING/PROCESSING | Retain generation + revision atomicity |
| E38 | PUT `/v1/merchant/merchant-knowledge/order` | 1 + 8 + 2n + R when rewriting n sources; 1 + 8 + R when already compacted and identical | Retain whole-list atomicity and merchant coordination |
| E39 | POST `/v1/merchant/merchant-knowledge/upload-intents` | 9 new; 7 valid pending replay | Retain count/insert/identity coordination; sign after commit |
| E40 | POST `/v1/merchant/merchant-knowledge/upload-finalize` | 16 new source; 17 replacement; 8 already-AVAILABLE replay; 12 when another finaliser wins during verification | Retain short phases around external verification; fix final asset-state coordination |
| E41 | PATCH `/v1/merchant/merchant-knowledge/uploads/:id` | 8, including identical metadata | Retain authenticated coordinated write; no R2/configuration dependency required |

E39/E40 include one production PlatformConfiguration lookup. Injected static configuration removes that one call. No full knowledge-response refresh is performed by E39–E41. E41 does not call the upload configuration reader. [B09-S05:96–261; B09-S07:53–64; B09-S12:59–74, 95–98; B09-S13:27–48]

### Count derivation

**E37:** 7-call lockedEntitlement (two lock queries, two repeated identity reads, subscription, feature, preference) + one source collection read = 8. An actual refresh adds source update and revision insert = 10. HTTP authentication and R occur outside that transaction. [B09-S01:15–47, 147–161; B09-S04:15–75]

**E38:** the same 7 + 1 preliminary work, followed by two updates per configured source when order/positions are not already correct. Empty/already dense same-order input skips writes, but not validation or R. [B09-S01:79–88, 176–184]

**E39:** authentication + configuration + transaction of Shop lock/read, installation lock/read, subscription, allowed pair, existing asset lookup, live-intent count, asset insert = 9. Replay omits count and insert = 7. [B09-S05:117–162]

**E40:** authentication + configuration + five preliminary calls (Shop, installation, asset, entitlement, pair). New-source commit has nine calls (Shop, installation, entitlement, asset, pair, source collection, source create, asset update, revision create). Replacement adds a separate target-source lookup. Already-AVAILABLE preliminary replay adds one revision lookup to the five preliminary calls and avoids R2/final transaction. A concurrent-winner replay incurs five preliminary + five commit-phase calls, plus authentication/configuration. [B09-S05:165–250]

**E41:** authentication + Shop + installation + entitlement + source collection + target source + pair + source update = 8. No extra revision, post-write settings read, R2 access, configuration read or full knowledge projection. [B09-S05:253–261]

## Entry E37 — POST /v1/merchant/merchant-knowledge/sources/:id/refresh

### Current behaviour and retained invariants

The Read Committed web-command transaction has a 12-second timeout. It validates/locks the current merchant, checks entitlement, reads the configured source collection, requires an owned WEB_PAGE/REMOTE_URL source, checks the supplied expectedGeneration, verifies its eligible position and requires a current URL. If the latest revision is PENDING or PROCESSING, it does not create additional work. Otherwise it advances the generation and inserts a PENDING REFRESH revision for that URL. Background's existing revision reconciler supplies asynchronous handoff; the API does not fetch the URL or publish to Redis here. [B09-S01:15–70, 95–104, 147–161; B09-S20:45–86]

Keep the transaction: generation and revision must roll back together. Retain older ACTIVE history. Keep expectedGeneration validation BEFORE the pending-work no-op. A request with the latest generation while work is pending is a no-op; replaying the original request after it successfully advanced the generation is stale and conflicts. The existing concurrent-refresh test expects one success and one 409, not two successful acknowledgements. Do not change these semantics as a query optimisation. [B09-S24:59–79]

### E37-F01 — Put expected generation in the mutation predicate

**Classification:** Source-confirmed stale predicate; recommended hardening of the cross-writer contract, not evidence of a duplicate committed generation.
**Priority:** Medium; same coordination family as E35/E36.
**Owner:** moda_api; validate with actual Background generation writer.

The source generation is checked in memory, but the UPDATE is `where: { id }` followed by an increment. Background entitlement reconciliation locks the source row, not the API's Shop row, and may advance generation with its own revision. Reprocessing of uploaded sources is not directly part of this web route, but the Background source-generation mechanism is shared. [B09-S01:152–159; B09-S19:197–284]

Require a tenant-bound conditional update using the observed/expected generation and exactly one changed row, or lock and revalidate the source in a compatible order. Do not use a guessed new expected generation to force a stale request through. A Read Committed UPDATE re-evaluates its WHERE predicate after a conflicting updater commits; a generation condition must be in that predicate to provide this gate. [External cross-check: PostgreSQL 17 transaction isolation]

There is an important safety distinction from the previous metadata-only PATCH finding: REFRESH also inserts `(sourceId, observedGeneration + 1)`, and the canonical unique source/generation constraint normally rejects a stale collision, rolling back the whole transaction. Do not claim both generations silently commit. Make the conflict intentional at the mutation boundary and preserve diagnostics rather than relying solely on a later uniqueness exception. [B09-S16:184–219]

Required tests: actual Background generation advance between API source read and update; exactly one durable generation/revision; late revision failure rollback; pending/processing no-op at matching generation; old-generation retry remains 409; previous ACTIVE history retained; paused or revoked merchant rejected.

### E37-F02 — Reuse the common web-command savings without removing admission evidence

**Classification:** Confirmed repeated identity/preference reads in existing helper; carried forward from E34, not a second independent defect.
**Priority:** Medium efficiency.
**Owner:** moda_api.

Return identity fields from the two lock queries instead of issuing two more identity reads, and use writer entitlement data without the unused merchant preference read. Preserve all Shop-first locking, authorization and plan/configuration validation. This removes three transaction calls: append path 10 -> 7; pending no-op 8 -> 5. The full knowledge refresh still needs its preference lookup. Do not count that as removed. [B09-S01:15–36; B09-S04:15–75]

The source collection currently fetches latest revision details for every source although refresh uses URL/status for only the selected one. Narrowing peers is a secondary projection candidate; maintain complete eligible-rank determination and do not introduce an N+1 query pattern. Do not remove the selected URL/status evidence.

The post-commit response risk and original-error wrapping from increment 08 remain: R can fail after a successful commit; handled P2002/P2034 errors are replaced without cause before route logging. No mutation was made in this review. [B09-S01:95–104, 160–161; B09-S03]

## Entry E38 — PUT /v1/merchant/merchant-knowledge/order

### Current behaviour and retained invariants

The service validates a complete, duplicate-free array of at most 1,000 IDs. Within the same Shop-coordinated Read Committed transaction it requires exact membership of all configured sources, including dormant and uploaded sources; partial/subset orders and foreign IDs conflict. If IDs AND compact zero-based positions already match, it returns without writing. Otherwise all rows move into a disjoint positive staging range before final positions are assigned. [B09-S02:84–88; B09-S01:79–88, 176–184]

Keep the transaction and full membership validation. Position changes affect eligible rank and must not be partially committed. Source generation and revision history are not changed by this command. The request contains no order revision/expected generation; serialised ordering commands therefore do not have an optimistic-concurrency guarantee against another complete reorder. Do not add such a contract silently during optimisation.

### E38-F01 — Two writes per source, including stationary sources

**Classification:** Confirmed write amplification; optimisation candidate.
**Priority:** Medium.
**Owner:** moda_api.

A swap of two neighbouring rows in an otherwise compacted 100-row collection currently executes 200 position updates. Only two rows need to move. Compute target positions and stage/update just the m rows whose actual position differs from target, reducing 2n updates to 2m under the existing two-phase approach. Preserve the full initial no-op and compact gaps even when the ID order is unchanged. [B09-S01:79–88, 180–182]

Retain the nonnegative position constraint, unique (shopId, position), disjoint staging range, int32 safety, tenant predicates, exact affected-row checks, complete rollback and an explicit decision about untouched-row updatedAt semantics. Do not stage at negative positions or use a blind shift/CASE update that has not been tested against immediate uniqueness. Source-provided constraints are in B09-S16:153–175.

A bounded set-based implementation is a later option; moving existing calls into Promise.all inside an interactive transaction is not evidence of SQL parallelism. One connection executes the transaction's statements. [External cross-check: Prisma v6 transactions]

**Review-only validation:** the new model compared full versus changed-row-only two-phase updates for 23,650 permutations/layout cases and one explicit 100-source swap. It found zero final-order/incremental-uniqueness/nonnegative-int32 mismatches. The 100-source swap used 200 vs 4 simulated updates. This is NOT TypeScript, Prisma, PostgreSQL, timestamp, lock, concurrent-writer or performance validation.

Before acceptance, use migrated PostgreSQL tests with mixed WEB_PAGE/CSV/XLSX and dormant sources, gaps, empty/full no-ops, one swap, reverse order, duplicate/foreign/missing IDs, concurrent source creation/deletion, a mid-staging failure and rollback. Assert no new ingestion generation/revision. Existing integrated ordering coverage is a two-source swap and foreign-member rejection. [B09-S24:80–94]

### E38-F02 — Ordering loads unused source and revision data

**Classification:** Confirmed over-fetching.
**Priority:** Medium/low after correctness.
**Owner:** moda_api.

The shared source query retrieves names, language, generation, purpose/format relations and latest URL/status. Ordering only uses ID and position after entitlement is established. Use a dedicated narrow collection projection; do not constrain it to currently eligible sources because dormant entries are part of the complete order. [B09-S01:39–47, 176–184]

Together with the existing three-call common-helper saving, a changed order can target `1 + 5 + 2m + R` instead of `1 + 8 + 2n + R`. This is a source-level target, not an implemented query plan. R is still a fresh post-commit projection; the same failure/retry distinction as E34–E37 applies.

## Entry E39 — POST /v1/merchant/merchant-knowledge/upload-intents

### Current behaviour and retained invariants

One purpose-scoped configuration snapshot is fetched before the transaction. The transaction locks/revalidates Shop and installation, reads a narrow entitlement projection and the active allowed pair, validates MIME, then checks the deterministic asset identity. That identity hashes Shop ID plus retry UUID. Unlike E29's follow-up claim issue, two Shops using the same UUID do not intentionally share the same identity. [B09-S05:17–64, 96–151; B09-S06:69–103]

An identical live PENDING_UPLOAD intent returns its existing object key and expiry without another count or insert. New requests count live pending intents and enforce `max(3, maxKnowledgeSources * 3)` under Shop coordination before insertion. Signing happens after commit; the signed capability cannot outlive the durable expiry. The persisted object key is reused verbatim even after a canonical hostname change and for already-supported legacy layouts. Do not regenerate keys or reset TTL on replay. [B09-S05:127–162; B09-S23:82–111]

Keep the transaction: concurrent new intents must not both pass a limit against the same pre-insert count. Keep signing outside the transaction. A signing failure intentionally leaves a bounded pending intent that can be retried with the same UUID/metadata; it is not a partially committed source revision. This behaviour is explicitly documented. [B09-S34:140–161]

Intent does not reserve a source slot. Finalisation enforces actual eligible-source capacity; the integration test deliberately allows another intent at capacity and rejects the later new-source finalisation. Do not turn the live-intent limiter into a source-slot reservation as a side effect of this review. [B09-S23:162–178]

### E39-F01 — purposeKey is not bound to the immutable retry metadata

**Classification:** Confirmed mismatch between documented changed-metadata conflict rule and persistence; conditional reproducer requires two allowed purposes for the same format.
**Priority:** Medium correctness/contract.
**Owner:** moda_api; moda_database if durable schema support is required.

The request and OpenAPI include purposeKey and state that changed retry metadata conflicts. Existing-asset comparison checks dataFormatId, filename, MIME, size, hash, Shop, status and key, but not purpose. The asset model has no purpose or complete request-fingerprint field. [B09-S05:125–149; B09-S06:69–82; B09-S15:4186–4208; B09-S34:157–176]

If both `(purpose A, CSV)` and `(purpose B, CSV)` are currently allowed, replaying the same UUID/file metadata with B resolves the same dataFormatId and satisfies all existing comparisons. It returns the same pending intent instead of a changed-metadata conflict. This is not a proven entitlement bypass: both pairs must pass current validation. It is a replay-contract gap.

Preserve the Shop + idempotency-key identity. Do not add purpose to the asset-ID hash to silently create a second intent for the same key. Either persist/check canonical intent metadata (including purpose) or explicitly approve and publish a purpose-neutral contract. The current documented contract supports the first direction; storage details need a bounded Database-owned decision. Do not alter schema in this analysis. Test two allowed purposes on one format, same key/same purpose, changed MIME/hash/size/name/format, same UUID across Shops and expired replay.

### E39-F02 — Live-intent count needs representative plan evidence, not deletion

**Classification:** Index/access-path candidate, not a demonstrated slow query.
**Priority:** Low pending measurements.
**Owner:** moda_api query evidence; moda_database only if justified.

The query filters by shopId, PENDING_UPLOAD status and uploadExpiresAt > now. The existing relevant index is `(shopId, status, createdAt)`, not an expiry-ordered index. The existing index still has usable equality-prefix filtering. Cleanup already tombstones expired intents; do not claim perpetual live-intent accumulation. [B09-S05:139–142; B09-S16:148–151; B09-S17:40–49, 108–120]

Measure EXPLAIN/row visits for representative live and expired-backlog histories, including cleanup delays and write cost. Only then evaluate `(shopId, status, uploadExpiresAt)` or an appropriate pending-only alternative and whether it replaces/adds to existing indexes. Do not add an equivalent duplicate, create a moving-time index predicate, remove the cap or remove merchant coordination to save a query. [External cross-check: PostgreSQL multicolumn indexes]

The upload identity helper already returns validation fields in its lock queries; entitlement already avoids a merchant preference read. E34/E37's three-call web-helper fix does not apply here. [B09-S05:17–49]

## Entry E40 — POST /v1/merchant/merchant-knowledge/upload-finalize

### Current behaviour and retained boundaries

The service obtains one configuration/R2 snapshot before database work. A preliminary transaction locks/revalidates identity, reads the Shop-owned intent, verifies expected size/hash/MIME and source-format identity, checks current entitlement/pair, and returns the original result for AVAILABLE assets. Otherwise the intent must still be pending and unexpired. [B09-S05:165–192]

That transaction ends before external verification: HEAD checks metadata, then a bounded GET stream recomputes byte count and SHA-256. A second, short Read Committed transaction revalidates identity, entitlement, asset state, allowed pair, capacity or owned replacement-source eligibility, then creates/updates the source, marks the asset AVAILABLE and inserts the PENDING revision. Final transaction timeout is 10 seconds. Preliminary/intent/edit transactions do not explicitly set isolation and inherit the configured setting; deployment values were not inspected. [B09-S05:193–250; B09-S08:57–88]

Retain the final atomic write and the network separation. Do not hold a transaction open across R2 verification, replace bounded GET hashing with HEAD-only evidence or treat pre-network eligibility as authoritative after the network call. Asset/source/revision writes must roll back together. No queue publication is needed; accepted means durable PENDING work, not completed ingestion. [B09-S34:235–246; B09-S36:40–43, 102–105]

The preliminary phase is read-only despite taking the same exclusive Shop lock used by writers. That is a future contention candidate, not the first correction: relaxing preliminary locks must preserve current authorization/expiry rejection and rely on a proven final authority gate. Its locks never reserve the asset across R2 because the transaction has already ended. Do not report them as protecting against all finalisation races.

### E40-F01 — Finalisation can overwrite cleanup's tombstone

**Classification:** Source-supported cross-service concurrency hazard, not runtime reproduced.
**Priority:** High; potential accepted revision referencing an object being deleted.
**Owner:** moda_api correction with moda_background lock/lifecycle compatibility review and integrated validation.

The committing transaction reads the asset without an asset-row lock, checks status/expiry, then later updates `where: { id: asset.id }` to AVAILABLE. The Shop lock does not coordinate with Background cleanup, which locks the asset directly, verifies no referencing revisions, tombstones an expired pending asset, commits, and then deletes the persisted object key from R2. [B09-S05:201–247; B09-S17:83–147; B09-S18:54–56]

Possible schedule:

1. R2 verification succeeds; the final transaction reads PENDING_UPLOAD and passes its last expiry check just before expiry.
2. Before asset UPDATE/revision INSERT, the clock passes expiry. Cleanup locks that asset, sees no committed referencing revision and marks it DELETED, then commits.
3. Cleanup is entitled to delete the R2 object and no longer holds a database transaction.
4. API's unconditional ID-only update changes DELETED back to AVAILABLE and creates a PENDING revision. Cleanup's deletion can occur before or after that commit.

The available-fields CHECK and foreign key do not prohibit that resurrection. The revision FK proves asset-row existence, not object availability or a legal lifecycle transition. The uploaded migrations contain no additional asset-transition trigger. [B09-S16:121–151, 184–224]

Fix the final asset state/expiry gate under the same row-level coordination that cleanup uses, or use an atomic status/expiry/tenant/metadata-conditioned claim whose affected row is held until the referencing revision commits. Revalidate time after waiting; define precise expiry-at-admission behaviour. If cleanup wins, reject without creating a source/revision and never restore DELETED. If finalisation wins, cleanup must observe the reference/current state after waiting and skip deletion. Keep any state change and source/revision writes in the same transaction so failure rolls them all back.

A naked idempotent update is insufficient. In Read Committed, the WHERE predicate can be re-evaluated against a concurrent updater's committed row, but `id = ...` still matches a tombstone. Row locking/conditional transitions, consistent lock ordering and tests are required. [External cross-check: PostgreSQL transaction isolation and explicit locking]

Existing cleanup tests cover a reference added after candidate enumeration BEFORE cleanup's locked check. That is useful but not the inverse API-read -> cleanup-tombstone -> API-write interleaving. Existing API upload tests use a simulated object store and do not run the real cleanup writer concurrently. [B09-S22:208–240; B09-S23]

Required migrated tests: barrier immediately after API final status/expiry read; advance controlled time; run real cleanup with a controlled R2-delete stub; resume API. Require no AVAILABLE resurrection or accepted reference to a deleted object. Also test API-wins, rollback after claiming/late revision failure, expired-before-final-read, parallel finalisers, replacement-source generation writer, deletion failure/retry and consistent lock order. No new external store or long-lived network transaction is justified.

### E40-F02 — AVAILABLE replay is not tied to the original intake revision

**Classification:** Confirmed ambiguous query under a supported one-to-many relation; possible unstable replay result, not observed nondeterministic output.
**Priority:** Medium/high idempotency.
**Owner:** moda_api; Database only if durable uniqueness for original intake needs strengthening.

Both AVAILABLE branches use `findFirst({ where: { uploadedAssetId: asset.id } })` without ordering or intake provenance filtering. Yet REPROCESS and ENTITLEMENT_CHANGE legitimately create later revisions pointing to the same uploaded asset. The schema has a non-unique uploadedAssetId index and unique (sourceId, generation), not one revision per asset. [B09-S05:181–187, 206–212, 274–297; B09-S19:251–280; B09-S16:215–228]

The published contract promises the same source/revision on repeated finalisation. A lookup that permits either the CREATE/FILE_REPLACE revision or a later REPROCESS revision does not enforce that promise. Existing tests repeat finalisation before later processing and primarily compare sourceId; they do not replay after multiple asset-linked revisions while asserting original revisionId AND generation. [B09-S34:239–267; B09-S35:upload sequence step 4; B09-S23:124–142, 165–170]

Select/record the original intake result deterministically. Existing CREATE/FILE_REPLACE provenance may support a precise lookup with explicit zero/multiple-match handling; verify the invariant before deciding whether an explicit receipt relation or partial uniqueness is needed. Do not return the newest reprocess generation, pick an arbitrary row or make uploadedAssetId globally unique across all revisions, which would break reprocessing. Preserve same-Shop/source/purpose checks and the no-R2/no-write path for a completed replay.

Required tests: original new-file finalise -> repeated reprocess/entitlement revisions -> finalise replay returns exact original identity/generation; same for FILE_REPLACE; changed supplied target source rejects; multiple intake evidence fails closed; two concurrent finalisers; no duplicate source/revision.

### E40-F03 — Re-read MIME policy is not enforced in the commit phase

**Classification:** Confirmed validation asymmetry; source-supported policy-change interleaving.
**Priority:** Medium correctness.
**Owner:** moda_api.

The preliminary phase requires current pair.contentTypes to contain request.contentType. After R2 verification, allowedPair is called again and returns the current MIME list, but the pending commit branch checks only dataFormatId. If Admin removes that MIME while verification is in progress, the commit can still accept it. [B09-S05:51–64, 178–180, 214–217]

Apply the MIME membership test to the re-read commit-phase pair, alongside the existing format and identity checks. This need not add a database call: the necessary current data is already retrieved. Test policy removal during the injected verify pause, pair/format deactivation, entitlement revocation and rollback. This is not a hash bypass: expected bytes are still verified. It is a mismatch between current admission policy and what is committed.

The operation intentionally uses one R2/max-upload configuration snapshot per upload operation. Do not conflate this specific omitted check on already-reread catalogue data with a requirement to re-fetch every global configuration value or perform R2 twice. Concurrent policy changes after the final query remain subject to the chosen database consistency contract; a new global configuration lock is not proposed here.

### E40-F04 — Replacement generation should be guarded, not silently strengthened at the HTTP layer

**Classification:** Related mutation-predicate hardening; uniqueness currently supplies rollback protection.
**Priority:** Medium, alongside E37/E35 coordination work.
**Owner:** moda_api.

The replacement path computes currentGeneration + 1 from eligibleSource and assigns it by source ID alone. Background's source-generation writer and the upload reprocess path do not rely on this Shop lock. A tenant-bound expected-observed-generation condition or appropriately ordered source lock would express the internal concurrency contract directly. The following unique revision insert usually prevents a stale committed generation collision; do not label this as proven silent corruption. [B09-S05:221–247, 284–297; B09-S19:197–284]

Unlike web refresh, the public finalize payload has no expectedGeneration. Do not introduce a new required client field as an optimisation. Preserve existing public contract while guarding the transaction's observed source generation and testing cross-writer contention/rollback.

The successful final asset query also fetches a complete asset row while using a smaller subset; narrowing is lower priority than the guarded state transition and must retain every immutable-metadata, expiry and tenant field needed by the new gate.

## Entry E41 — PATCH /v1/merchant/merchant-knowledge/uploads/:id

### Current behaviour and transaction assessment

The route accepts exactly name and languageTag. It does not accept expectedGeneration. It locks/revalidates Shop and installation, reads entitlement, enumerates all sources to find eligible rank, reads the selected source again, validates its active allowed UPLOAD pair, then writes metadata by source ID. The response is a small `{ schemaVersion, sourceId, updated: true }` acknowledgement. No new revision/generation, R2 access, configuration read or full response refresh occurs. [B09-S06:97–100; B09-S05:67–83, 253–261; B09-S34:290–312]

Retain the coordinated authorization/eligibility/write transaction; replacing it with an unconditional update would discard the policy gate. The current last-serialized-merchant-write behaviour is different from a supplied-generation web PATCH. Do not call absence of expectedGeneration a bug or silently add it. Preserve metadata-only semantics and merchant-off configuration support.

### E41-F01 — Existing-source eligibility reads every source, then rereads the target

**Classification:** Confirmed unbounded collection + target lookup; bounded-query optimisation candidate.
**Priority:** Medium.
**Owner:** moda_api.

eligibleSources loads the entire Shop's source ordering and type metadata. eligibleSource filters the first configured maxKnowledgeSources allowed entries in memory, then fetches target identity/generation/type data separately. This is not an exact duplicate query: the first projection lacks fields needed by the second. [B09-S05:67–83]

For EXISTING-source operations, query the first K currently eligible sources directly using the same Shop, active-purpose/format, allowed-pair filters and stable position/ID ordering; return the fields needed for target validation and locate the target inside that bounded result. Keep WEB_PAGE and other eligible source types in ranking; filtering the list to uploads first would incorrectly promote later uploads into capacity. The target itself must still be an UPLOAD source. [B09-S39:45–68; B09-S05:72–83]

One coherent bounded projection can replace the collection + target pair, reducing metadata edit 8 -> 7 calls and replacement finalisation 17 -> 16, before other corrective work. Those are isolated candidate savings, not a promised final corrected-path count. Compare SQL and relation costs, not just client calls.

Do NOT reuse this bounded reader for NEW-source position allocation: creation must consider the maximum position across ALL configured sources, including dormant entries, to avoid collisions. Keep creation's source-count and position semantics distinct. The full-list reorder endpoint also has a different membership contract.

### E41-F02 — Identical metadata still writes

**Classification:** Confirmed unnecessary-write candidate, not an idempotency-contract failure.
**Priority:** Low/medium depending on duplicate frequency.
**Owner:** moda_api.

The service always issues UPDATE. Include current name/languageTag in the necessary owned-source projection and skip it when both already match, after the same identity, entitlement/rank and pair checks. Return the same public acknowledgement. No extra read is needed. The source declares updatedAt @updatedAt, so agree whether identical requests should stop touching that timestamp and test worker consumers accordingly. [B09-S05:253–260; B09-S15:4210–4232]

With both bounded eligibility and no-op suppression, changed metadata can target 7 calls; identical metadata 6, compared with 8 today. No generation, ingestion revision, R2 check or post-write reread should be added.

Required tests: unchanged metadata does not write; name/language changes update only those fields and normal timestamp; unsupported/WEB_PAGE/foreign/dormant/out-of-capacity targets fail; WEB_PAGE entries before an uploaded source still consume eligible rank; source type deactivation and membership changes; concurrent metadata writers; prior generation semantics remain unchanged.

## Cross-cutting diagnostics: upload routes already retain the original error

Do not carry the web-command wrapper diagnosis over to uploads. Although normaliseUploadError maps recognised Prisma errors to a safe conflict response, upload.routes logs the original caught error's name/message/stack/cause and Prisma code BEFORE sending that mapped response. Configuration/R2 wrappers use unavailable(error), retaining their causes. The route therefore still has the original Prisma exception. [B09-S07:65–84; B09-S05:100–111, 301–309; B09-S06:12–23; B09-S08:55, 85–88]

A route regression explicitly verifies the original P2028 diagnostic, and other tests verify redaction of the signed capability and secret-like values through the real shared logger. Keep purpose-scoped configuration, shared logging/redaction and numeric timing phases rather than introducing a competing logger. [B09-S28:143–179, 197–216; B09-S40]

In contrast, the web refresh/order common helper throws a new conflict and loses the Prisma error before its route sees it. The prior cause-preservation recommendation still applies there. [B09-S01:95–100]

Intent/finalise configuration is read before starting transactions; there is no demonstrated version of E31's root-client configuration query inside a held upload transaction. Metadata edit does not acquire R2 configuration at all. Preserve those existing boundaries. [B09-S05:96–118, 165–168, 253–261]

## Validation reviewed, performed and required

**Inspected existing coverage:**

- Web-source migrated suite covers same-Shop parallel create deduplication, stale web generation, pending refresh no-op, parallel refresh winner/409, old ACTIVE history, source quota, tenant scoping and two-row ordering. [B09-S24]
- Upload migrated suite uses real PostgreSQL migrations and sealed database-backed configuration, with injected R2 transport. It covers CSV/XLSX, replay before later processing, immutable object keys across hostname changes/legacy keys, changed file metadata, wrong-Shop/digest rejection, replacement/reprocess, source quota, expiry, revoked installation and revision-insert rollback. It does not exercise live R2. [B09-S23]
- R2 unit tests inspect real signer behaviour and simulated response streams. Timing tests distinguish configuration, preliminary transaction, external verification and commit. These are test SOURCE findings, not newly executed test results. [B09-S25–B09-S28]
- Background cleanup integrated suite covers reference-after-candidate-selection, expired/orphan tombstones and retryable object deletion. It does not call the Woo finaliser in the hazardous opposite interleaving. [B09-S22]
- Both API web-command and upload PostgreSQL runners deploy migrations and are registered in npm run test:integration. No duplicate test harness is proposed. [B09-S31–B09-S33]

**Performed in this review:**

1. Read exact mounted snapshot files and inspect relevant API, schema, migrations, tests, documentation, configuration and Background consumers.
2. Verify 40 selected text files byte-for-byte against their original archive members; produce SHA-256 manifest and line-numbered evidence.
3. Confirm original archive SHA-256 `ee42bb83ee441ba9018779e760967a5bf87edcbc429eecc58699f1419863861b`.
4. Run the review-only ordering model: 23,650 cases, zero logical mismatches; 8,957 cases reduced simulated writes. Separate 100-row adjacent swap: 200 -> 4 writes.
5. Check local execution prerequisites: node v22.16.0 is available; API declares Node 24.19.0; API node_modules is absent; docker and psql commands are not available.

**Not performed:** application/TypeScript tests, Prisma client generation, dependency installation, schema deployment, PostgreSQL queries, real concurrency reproduction, EXPLAIN, pool stress, live R2 operations, latency/capacity measurements or production observations. No claim of runtime acceptance, measured query reduction or a production incident is made.

**Focused acceptance additions, using existing suites:**

- Shared-asset cleanup versus final commit, both winner orderings, controlled time, rollback and external deletion retry.
- Same upload UUID with changed purpose where both purpose/format pairs are allowed; unchanged replay and cross-Shop independence.
- Completed finalise replay after multiple reprocess/entitlement generations; exact original revisionId/generation, not merely matching sourceId.
- Accepted MIME removed during object verification; fail closed without partial asset/source/revision state.
- Real Background generation update between web refresh read/mutation and uploaded replacement read/mutation.
- Mixed/dormant full ordering, gaps, partial permutations, changed-row-only updates, injected mid-staging failure, no-op timestamps and maximum-size workload.
- Bounded first-K eligibility with web rows included in ranking, no-op upload metadata, no unsolicited new revision/generation.
- Post-commit web refresh/order projection failure with commit outcome logged separately; original exceptions and redacted signed-capability diagnostics retained.
- Actual per-path SQL/query plans/lock duration/affected rows on the fully migrated schema, including cold/new, retry, empty, rejection and concurrent cases. Use existing instrumentation and timing phases rather than a new generic telemetry subsystem.

## Priority, ownership and execution boundaries

| Priority | Recommendation | Owners / coordination |
|---|---|---|
| High | E40-F01 final asset gate coordinated with cleanup | API implementation; Background lifecycle/lock review and integrated regression; Database only if invariant strengthening is required |
| Medium/high | E40-F02 stable original-intake replay identity | API; Database only if provenance uniqueness cannot be guaranteed without schema support |
| Medium | E39-F01 durable purpose binding matching published retry contract | API + bounded Database-owned storage decision |
| Medium | E40-F03 reapply current MIME policy after R2 | API; no new query required |
| Medium | E37-F01 / E40-F04 mutation-bound generation checks | API, validated against actual Background writer |
| Medium | E38 moving-row-only ordering and narrow projection | API; migrated constraint/rollback tests |
| Medium | E41 bounded existing-source eligibility / shared web-helper savings | API; preserve distinct new-source allocation and read projection |
| Low/measurement-led | E39 expiry-count index; E41 no-op timestamp suppression; preliminary finalise lock reduction | Query/behaviour measurements first; Database owns any index change |

No new infrastructure service, queue, external store, mandatory schema migration, task definition or API breaking change has been approved in this increment. Potential purpose/intake storage changes require an explicit design decision. Existing runtime mechanisms are inspected rather than replaced. No task is accepted/reopened and no branch/worktree/commit/push is claimed.

## External technical cross-checks (not evidence of Moda runtime behaviour)

Checked 2 November 2026, primary documentation only:

- PostgreSQL 17 transaction isolation: `https://www.postgresql.org/docs/17/transaction-iso.html` — statement snapshots, re-evaluation of a conditional mutation after a concurrent updater, and limits of Read Committed.
- PostgreSQL 17 explicit locking: `https://www.postgresql.org/docs/17/explicit-locking.html` — row-lock coordination and lifetime, including consistent lock ordering.
- PostgreSQL 17 multicolumn indexes: `https://www.postgresql.org/docs/17/indexes-multicolumn.html` — equality prefixes, range fields and why index candidates require workload evidence.
- Prisma v6 transactions: `https://www.prisma.io/docs/orm/v6/prisma-client/queries/transactions` — atomic rollback, short interactive transactions, same-connection execution and avoiding network work inside transactions.

These checks support general reasoning only. Application findings come from the uploaded snapshot; race schedules are explicitly inferred; measurements remain unavailable.

## Next increment

E42 POST `/v1/merchant/merchant-knowledge/uploads/:id/reprocess`; E43 GET `/v1/merchant/promotions`; E44 PUT `/v1/merchant/promotions/selection`; E45 GET `/v1/merchant/discount-catalogue`; E46 GET `/v1/merchant/discount-offers`.

**Current progress: 41 reviewed; 20 remaining. No source/schema/task/index changes.**

---

# Increment 10 — five further endpoints (E42–E46)

**Review date:** 2 November 2026.
**Coverage:** E42 uploaded-source reprocessing; E43 promotion reads; E44 promotion selection; E45 discount catalogue; E46 discount-offer settings reads.
**Current progress:** 46 method/path combinations reviewed; 15 remain from the original 61-route inventory.
**Classification:** Static source assessment, explicit-call accounting, proposed optimisations and unresolved concurrency/contract questions. No implementation acceptance, PostgreSQL execution or measured performance claim.
**Evidence:** `woocommerce-api-database-review-10-source-evidence.txt`, identifiers B10-S01 onward, and `woocommerce-api-database-review-10-source-manifest.json`. The source file paths and original line ranges below identify the primary evidence. `woocommerce-api-database-review-10-catalogue-model.py/.json` contain a limited review-only model, not repository tests.

## Scope and measurement discipline

The two promotion endpoints concern Moda promotional recovery credits, not Woo coupon redemption. The discount catalogue concerns observed Woo coupon codes, while discount-offer settings preserve the merchant's selected IDs even when the catalogue is unavailable. These boundaries are explicitly documented in ARCH-035-API-021 and ARCH-036-API-004; they must not be merged as a performance shortcut.

Counts include one installation-authentication model call where the route uses the authenticator. A call is an explicit Prisma model method or raw-query invocation, not a SQL statement, returned-row count or network round trip. Transaction control, nested relation expansion, SQL triggers, retries, driver/pool operations and asynchronous workers are excluded. A single ORM call may emit several statements; narrower projections or nested upsert results can change that expansion. Costs are successful-path source deductions, not measurements.

| Entry | Endpoint | Explicit calls | Transaction and principal boundary |
|---|---|---:|---|
| E42 | POST `/v1/merchant/merchant-knowledge/uploads/:id/reprocess` | 10 | Authentication + 7 preflight reads, then a 2-write transaction; isolation not explicitly selected |
| E43 | GET `/v1/merchant/promotions` | 9 | Repeatable Read; no explicit row locks on the read helper path |
| E44 | PUT `/v1/merchant/promotions/selection` | 10 actual selection; 6 accepted identical replay | Serializable, 12 s transaction timeout; at most 3 transaction attempts for P2002/P2034 |
| E45 | GET `/v1/merchant/discount-catalogue` | `5 + b`, ordinarily 6 | Repeatable Read; `b >= 1` coupon batches of up to 100 rows, not one query per returned coupon |
| E46 | GET `/v1/merchant/discount-offers` | 7 | Repeatable Read; saved settings readable without a CURRENT catalogue |

E45's incomplete/missing catalogue rejection occurs after 4 calls including authentication, before coupon batches/settings lookup. Rejected/early-return paths elsewhere can cost less than the successful paths above. No unverified latency percentage is derived from these numbers.

## E42 — Reprocess an uploaded knowledge source

### Current flow and retained behaviour

`src/merchant/merchant-knowledge/upload.service.ts:264–296` revalidates Shop/installation using `assertWooPrincipal`, reads current entitlement, resolves eligible source membership and target details, checks the permitted upload pair, and reads the revision at the observed source generation together with its uploaded asset. The asset must belong to the Shop, be AVAILABLE, and match the source data format. The next generation is checked for safe-integer and PostgreSQL integer limits.

The transaction then performs a conditional source update and creates exactly one PENDING REPROCESS revision. Its predicate includes source ID, Shop ID, observed currentGeneration, purposeId and dataFormatId. Exactly one updated row is required. The returned revision ID comes from the create result; there is no post-write read or full knowledge-page refresh.

Call ledger: HTTP authentication 1; Shop/installation revalidation 2; subscription/entitlement 1; eligible-source enumeration plus selected source 2; allowed pair 1; current revision/asset 1; guarded update 1; revision create 1 = 10. No R2 configuration query, HEAD/GET, byte rehash, external call or Redis publication occurs in this operation. It reuses the verified persisted asset. Background reconciliation separately checks current generation and eligibility before queuing work (`moda-interact-background/src/services/merchant-knowledge-reconciliation.service.ts:45–85`); ACCEPTED is not proof that processing has been queued or completed.

**Retain the two-write atomic unit and the conditional generation update.** This is materially stronger than the ID-only web PATCH/DELETE examined in increment 08. Preserve rollback on revision insertion failure, supported merchant-off configuration, asset ownership checks, and the bounded response. Do not add another write/reread or provider call merely to make the implementation resemble finalisation.

The source deliberately performs validation outside the transaction. The dedicated unit suite explicitly asserts that shape, tests competing readers observing the same generation, rollback and preflight rejection of a revoked installation (`tests/unit/merchant/merchant-knowledge/upload-reprocess.test.ts:110–149`). These are inspected test definitions, not results rerun here.

### E42-F01 — Reuse the bounded existing-source eligibility optimisation

**Classification:** Confirmed unbounded enumeration followed by target lookup; optimisation candidate shared with E41-F01. **Priority:** Medium, after semantic tests. **Owner:** API.

`upload.service.ts:67–83` fetches all configured sources, computes the eligible prefix in memory and separately reads the target's fields. For existing-source operations, one bounded first-K eligible-source query can carry the fields needed to identify and validate the target. Preserve exact allowed purpose/format activity, position/ID ordering and merchant capacity semantics. Eligible WEB sources must still occupy positions in the ranked set; do not filter to UPLOAD before applying the limit. The current helper does not check purpose/data-format pair association until target `allowedPair`; do not silently introduce a different ranking definition.

Isolated source-level target: 10 -> 9 calls, with the transaction remaining 2 writes. Do not apply a K-row bound to new-source position allocation. Identity-query consolidation is a separate optional candidate and is not included in this target.

### E42-F02 — The OpenAPI response list omits the implemented concurrency conflict

**Classification:** Confirmed response-contract documentation gap. **Priority:** Medium. **Owner:** API.

The conditional source update throws `KnowledgeUploadError(409, "knowledge_upload_conflict")` on a stale observed generation (`upload.service.ts:287–291`; `upload-contract.ts:22`). The normal upload route returns that status; the concurrency unit test expects 409. But the reprocess operation's OpenAPI lists only 200/400/401/403/503 (`openapi/merchant-knowledge-v1.yaml:313–327`). Document 409 and its retry/conflict meaning; preserve the guard rather than hiding conflict as success. No new request body or expectedGeneration field is approved by this finding.

### E42-C01 — Generation coordination is not commit-time authentication or request deduplication

**Classification:** Source-supported boundary requiring a deliberate contract/validation decision, not a claimed exploit or accepted-task failure.

All eligibility and installation reads precede the two-write transaction; the predicate does not include current installation status/version or current plan/source-rank eligibility. A credential rotation, suspension or entitlement/order change that does not change source generation can occur after preflight without being detected by that generation predicate. Existing tests reject a connection already revoked when preflight runs; they do not establish a commit-time revocation guarantee.

Respect the intentionally short transaction in the current test/implementation. Add a controlled interleaving test and decide whether an admitted preflight may finish or whether a coordinated current-principal recheck is required. If a stronger contract is chosen, design its locking/mutation fence and update the two-write test explicitly; do not silently claim the current CAS supplies that guarantee. The pending revision is not external data access or proof of ingestion, and Background has independent generation/eligibility checks.

The HTTP request is bodyless and has no idempotency key. A subsequent successful call can observe the new generation and append another REPROCESS revision even while it is PENDING. Same-observation concurrency protection is therefore not sequential request deduplication. This follows from `upload.service.ts:274–295`, which selects no revision status and always advances a successfully observed generation. The OpenAPI explicitly defines append semantics. Do not silently copy web-refresh's pending no-op or invent a receipt table. Test/document lost-response retries before promising idempotent reprocessing; superseded pending generations may be skipped by the reconciler rather than all being processed.

Original unexpected Prisma diagnostics are logged from the caught exception by `upload.routes.ts:65–84`; retain that working behaviour rather than classifying this endpoint with promotion selection's cause-loss problem.

## E43 — Read promotional recovery-credit offers, selection and history

### Current flow and transaction decision

`src/merchant/promotions/service.ts:13–17` establishes Repeatable Read. `context.ts:27–81` revalidates Shop, installation and an ACTIVE/TRIALING subscription with an active matching plan. `read.ts:27–102` reads selected grant/campaign state, counts eligible campaigns and tenant grant history, then fetches independently paginated six-row offer and history pages.

Ledger: authentication 1 + identity/subscription 3 + current selection 1 + counts 2 + page queries 2 = 9. The selected grant's authoritative balance and campaign data contribute to the revision; it is not safe to infer selection from whichever offers happen to be on the current page. Translation fallback, scoped GLOBAL/PLAN/SHOP eligibility, retained historical grants, latest REOPENED evidence and corruption checks remain required.

**Retain the snapshot and exact counts.** The task/OpenAPI promise totalEntries, totalPages, clamped page numbers and fixed six-row pages, not cursor-only approximate paging (`docs/decisions/api/ARCH-035/API-021-expose-woo-promotional-recovery-credits.md:52–65`). Snapshot isolation is relevant to consistent count/page/credit state. One instant `now` is captured per read; do not introduce independently evaluated expiry moments for each page.

### E43-F01 — Skip page fetches whose exact count is zero

**Classification:** Confirmed unnecessary empty-page queries. **Priority:** Medium. **Owner:** API.

`read.ts:40–88` unconditionally fetches both pages after their counts. Within the same Repeatable Read snapshot, a zero count for the unchanged filter establishes an empty corresponding page. Return an empty collection for that side without issuing findMany; keep pagination normalization, locale handling, current selection, and the other page unchanged.

Isolated targets: both nonempty 9 unchanged; one empty 9 -> 8; both empty 9 -> 7. Keep both count operations because exact totals are published. Do not mistake no current offers for no historical grants or no selected pointer. The selected state can be closed/expired/exhausted while history still exists.

The migrated integration test covers multiple scopes, pagination/clamping, translations, balances/history and tenant boundaries. Add explicit query assertions for both empty, each empty independently and empty offers with historical selection. Test a concurrent campaign/grant change from another connection to retain count/page consistency; do not infer statement counts from a fake's method count alone.

### E43-F02 — Read-only Shop/installation consolidation is optional

`context.ts:30–62` performs two narrow identity reads; a single tenant-bound joined read can preserve every lifecycle/platform/domain/version/revocation check. It can reduce one additional model call on read paths without row locks. The separate subscription/plan gate remains necessary. This is independent of empty-page short-circuiting; no combined performance percentage is asserted. Do not mechanically rewrite the mutation helper's Shop-first locks.

The existing migration/schema already index campaign status/window/targets and grant shop/creation history (`schema.prisma:1904–1908, 1971–1974`; baseline migration indexes at 1059–1086). No new index is justified without actual plans/cardinality. A missing final ID column in an ordering index is not by itself proof of a bad plan.

## E44 — Select a promotional recovery-credit campaign

### Current behaviour and invariants

`src/merchant/promotions/service.ts:20–100` uses a Serializable transaction with a 12,000 ms timeout, retrying P2002/P2034 up to three total transaction attempts. The request's original expectedRevision is retained across attempts. Shop is locked FOR UPDATE and installation FOR SHARE; current subscription/plan and selected grant/campaign are reread within each attempt.

It validates campaign status, time window, target and positive quantity. A matching, still-unexpired selection may acknowledge a stale original revision without writing, but still must pass current campaign eligibility. Different campaigns cannot bypass a still-unexpired selection. In the current semantics, exhaustion/closure does not itself unlock that selection before expiry; keep the established rule rather than treating an exhausted balance as permission to switch.

A true selection finds-or-creates the existing `(campaignId, shopId)` grant with an empty update branch, validates remaining balance/exhaustion, updates selection bookkeeping, upserts the one-per-Shop selection and rereads its response projection. It does not consume recovery credit, call a provider or publish a queue event. Existing quantity/reserved/committed counters are not reset on reselection.

Ledger: authentication 1 + identity/subscription 3 + current selection 1 + requested campaign 1 + grant upsert 1 + grant bookkeeping update 1 + selection upsert 1 + final selection read 1 = 10. Identical accepted replay stops at 6 without writes. Retries amplify transaction calls, but do not rerun HTTP authentication.

**Retain the transaction, grant uniqueness, balance checks, tenant-bound foreign key, lock expiry semantics and retries.** The final response must use persisted selection version/timestamp and authoritative balance, not guessed increments or client counters. Migrated tests cover no-second-grant/no-second-selectionCount replay, preservation of reserved/committed state, two independent competing selectors and tenant isolation (`tests/integration/merchant/promotions/service.postgres.test.ts:111–172`).

### E44-F01 — Reuse returned writes instead of a separate final selection lookup, only if emitted SQL improves

**Classification:** Confirmed discarded write results followed by read; conditional optimisation candidate. **Priority:** Medium/measurement-led. **Owner:** API.

`service.ts:71–90` discards grant-update and selection-upsert results before `readPromotionSelection`. The response's canonical shape could be returned from the selection upsert using the same narrow projection, or composed from the actual returned grant and selection records plus the already-validated campaign projection from this same transaction. The latter needs display name/translations added to the existing requested-campaign projection and must reuse, not redefine, the canonical response/fingerprint rules.

Source-level candidate: 10 -> 9 model calls for a true selection, with replay unchanged. However, adding nested relation reads to a Prisma upsert can change whether native database upsert is used and the generated query plan. A lower method count is not sufficient acceptance evidence. Compare SQL and runtime before choosing an implementation; retain the existing code if the fused shape is not cheaper. Do not remove the initial selection or requested campaign eligibility read merely to meet a numeric target. Do not merge grant creation/bookkeeping in a way that resets quantities, double-counts selection, loses firstSelectedAt, or grants credits on an exhausted rollback branch.

### E44-F02 — Exhausted retries erase the original Prisma diagnostic

**Classification:** Confirmed diagnostic gap. **Priority:** Medium. **Owner:** API.

After the last P2002/P2034 attempt, `service.ts:92–100` throws a fresh PromotionDomainError without cause. The route logs error/cause fields (`promotions/routes.ts:47–63`), but cannot recover the original database exception. Preserve the original exception, safe code/constraint metadata and retry context, while retaining safe public errors and sensitive-data redaction. Keep bounded retry semantics and don't turn a stale different selection into an unconditional success. Unexpected exceptions outside these cases currently propagate; don't describe logging as universally absent.

## E45 — Browse the current observed Woo coupon catalogue

### Current behaviour and snapshot

`discount-offers/service.ts:80–121` uses Repeatable Read, revalidates Shop/installation and requires a catalogue with CURRENT status, a successful scan timestamp, and no active sync token/start marker. It filters by Shop, both Woo identity prefixes, CODE method, observed current generation, present/not-removed status and non-null code, plus optional search.

It retrieves 100-row ID-keyset batches and applies `deliverableCode` until it has limit+1 usable rows or reaches the end. The display limit is 1–50, default 25 (`contract.ts:41–55`). A separate settings timestamp supplies the informational revision. No provider request, R2 read, write or catalogue-status mutation occurs here.

Ledger: authentication 1 + Shop/installation 2 + catalogue 1 + coupon batches b + settings timestamp 1 = 5+b. Even an empty current catalogue runs one batch. Missing/incomplete catalogue returns 503 after the first four calls; it must not become a successful empty list.

Retain the application-level transport-safety filter while legacy malformed codes can still pass SQL. The migrated test creates 105 unsafe legacy rows before usable rows and checks all-page traversal without unsafe-code leakage (`tests/integration/merchant/discount-offers/offer-settings-and-catalogue.test.ts:145–181`). Retain complete codes rather than truncating; expired, exhausted, zero-amount or unfamiliar provider types are not reasons to remove a technically usable observed coupon. Woo owns redemption eligibility. These are explicit ARCH-036-API-004 requirements, not optimisation opportunities.

### E45-F01 — Fixed 100-row batches over-fetch clean small pages; smaller batches trade payload for more calls

**Classification:** Confirmed transfer pattern; benchmark-dependent candidate. **Priority:** Low until measured. **Owner:** API.

A clean first page at default limit 25 requires 26 usable rows for lookahead, but requests 100. At limit 1, it requests 100 to identify two usable rows. This is not an extra query in the common clean case, but excess result materialisation/transfer.

An exploratory policy is first batch limit+1 and subsequent fallback batches 100. It preserves the exact client cursor (last displayed item, never the final scanned or extra lookahead row), filtering and hasMore semantics. Do not set all retries to a tiny batch size or drop the continuation loop.

The review-only boolean-deliverability model ran 43,865 cases with zero item/cursor/hasMore mismatches. It also demonstrates the trade-off:

| Synthetic ordered input, limit 25 | Current fixed-100 | Exploratory first-26 then-100 |
|---|---|---|
| 1,000 usable rows | 1 query, 100 fetched rows | 1 query, 26 fetched rows |
| 10 unusable then 990 usable | 1 query, 100 fetched rows | 2 queries, 126 fetched rows |

The candidate had extra queries in 9,578 model cases and fetched more rows in 507; these are counts over a deliberately constructed test set, not workload frequencies. No unconditional adoption is recommended. Measure SQL duration, transfer volume and pool time for clean and legacy-invalid distributions first. The model excludes JavaScript/Unicode safety predicates, actual database collation, Prisma, authorization, snapshots and concurrency.

### E45-F02 — The comment's 5,000-coupon bound is not a universal capacity limit

**Classification:** Confirmed assumption drift with variable-query-cost implication. **Priority:** Medium for capacity evidence, not proof of current slowness. **Owners:** API review with Background configuration context.

`service.ts:100–101` refers to a 5,000-coupon worker bound. The actual page reader uses 100 rows per provider page and accepts configured maxPages from 1 to 200; its default is 50 (`moda-interact-background/src/providers/woo-coupon-pages.ts:10–35`, `src/services/woo-coupon-sync-config.ts:14–23`, `woo-coupon-reader.service.ts:14–16`). Thus 5,000 corresponds to the default; the supported reader can accept 20,000 at maxPages=200. The deployed value is unknown. The API's loop itself has no total-batch cap.

With all matched rows failing application safety filtering, 5,000 rows require 51 batches including the final empty batch; 20,000 require 201. The endpoint totals would be 56 and 206 explicit calls respectively. These are pathological source/model bounds, not typical production traffic. The normalizer marks new undeliverable codes UNDELIVERABLE/null and the SQL excludes them (`moda-interact-background/src/providers/woo-coupon-normalization.ts:107–108, 152–165`); the cases are chiefly relevant to legacy/corrupt-but-SQL-matching data and adversarial test fixtures.

Correct capacity assumptions and test longer matched-invalid prefixes. Do not silently truncate at 5,000, weaken code safety, report false hasMore, or simply enlarge timeouts. A predicate pushdown or data-invariant cleanup requires exact safety equivalence, migrated tests and explicit ownership. Consider a `(shopId, lastSeenSyncGeneration, id)`-led access path only after EXPLAIN with representative current/old generations and search; existing Shop-prefixed indexes already support other queries, and this review has no plan evidence for an additional migration.

### E45-F03 — Catalogue metadata can use a narrow projection

`currentCatalogue` loads every catalogue scalar. This path needs status, lastSuccessfulSyncAt, activeSyncToken, syncStartedAt, syncGeneration and updatedAt; it does not need error history or sync-request timestamps. Keep all readiness predicates. The coupon row and settings timestamp projections are already narrow. Optional joined read-only Shop/installation validation removes one client call, independently of b, without adding locks or caching.

## E46 — Read saved discount-offer preferences and effective mode

### Current contract and retained behaviour

`discount-offers/service.ts:124–131, 189–199` uses Repeatable Read, revalidates identity, reads optional catalogue metadata, settings, saved selected Woo IDs and an Admin override. It performs no writes or provider requests and does not call currentCatalogue.

Saved selection retrieval deliberately does not require the observed generation, commercial eligibility, current provider status or coupon code. It reads merchant-owned `isAvailable` flags, keeps Woo/Shop identity constraints, orders by ID, and takes 51 to detect more than the supported 50 selected records. Do not replace this with the browsing filter, remove the overflow sentinel, or silently return the first 50.

Missing/SYNC_REQUIRED/SYNCING/ERROR/UNAVAILABLE catalogue state does not make the stored merchant preference unreadable. A read revision contains catalogue status/generation/update time and settings timestamp, but is informational, not a PUT precondition. Merchant mode/IDs and effective mode/Admin override are distinct; the response does not fabricate effective selected IDs or expose an internal fixed coupon anchor.

**Retain Repeatable Read, non-locking reads and independent saved-preference access.** The migrated suite explicitly checks missing/failed catalogues, unchanged saved rows and a read during an uncommitted Background catalogue update (`tests/integration/merchant/discount-offers/offer-settings-and-catalogue.test.ts:12–86, 189–275`). ARCH-036-API-004 is the authoritative correction that established this boundary. Do not reintroduce the readiness dependency in a shared helper.

### E46-F01 — Three metadata projections are wider than necessary

**Classification:** Confirmed over-fetching. **Priority:** Low/medium. **Owner:** API.

The GET loads whole catalogue, settings and override rows. Its actual projection needs:

| Record | Fields consumed by this read |
|---|---|
| Catalogue | status, syncGeneration, updatedAt |
| ShopSettings | recoveryOfferMode, updatedAt |
| ShopRecoveryPolicyOverride | recoveryOfferMode, expiresAt |
| Selected Woo coupons | id; already narrow |

Narrow the GET/projection reads without stripping fields needed by separately owned write checks in the later Save review. Keep the raw absence/default handling, override expiry and revision token exact. Savings concern result size, not the seven-call total.

### E46-F02 — Optional identity consolidation; no evidence to remove domain reads

Combining the two existing read-only identity queries can reduce 7 -> 6 calls while retaining all Shop/installation/platform/domain/version/revocation conditions inside the snapshot. The settings, selected-ID, catalogue-revision and override reads each supply distinct response evidence. Do not omit catalogue metadata because its readiness is optional, or infer selected IDs solely from the fixed anchor.

### Shared discount-route diagnostic exception

`discount-offers/routes.ts:75–94` logs domain errors and unexpected failures, but directly maps uncaught Prisma P2002/P2034 to 409 without logging the original exception. These are not demonstrated common GET failures, and ordinary unexpected database errors already have diagnostics. If that mapping remains, add bounded original-error reporting on that branch rather than declaring the read services entirely unlogged. PUT's separate cause-wrapping behaviour is reserved for E47.

## Validation, ownership and limits

The uploaded promotion, discount-offer and knowledge-upload PostgreSQL scripts all deploy canonical migrations and are included in `package.json`'s integration aggregation. Existing suites cover real promotion concurrency on separate clients, preserved balances, coupon pagination beyond one invalid batch, saved settings during an uncommitted Background update, and upload lifecycle. The focused reprocess concurrency/rollback tests are mock-backed; the migrated upload lifecycle exercises reprocessing sequentially. No test runs from those histories are claimed as performed here.

This increment actually performed:

- Source/migration/task/OpenAPI inspection; Background page-bound and knowledge-reconciliation tracing.
- Source-derived successful-path counts, with retry, relation-query and row-cardinality exclusions.
- Byte-for-byte evidence verification against the exact uploaded archive and a read-only archive-tree verification; 46 evidence files and 9,453 archive files were checked; hashes are recorded in the manifest.
- The review-only catalogue model (43,865 equivalent response cases, with explicit transfer/query trade-offs).
- Primary technical documentation checks for PostgreSQL 17 snapshots and Prisma v6 transaction/upsert return behaviour; these do not establish application runtime outcomes.

No application tests, migration execution, PostgreSQL queries, EXPLAIN plans, live provider traffic, pool stress or latency benchmark was run. In this environment API node_modules, Docker and psql are absent. Available Node is v22.16.0; the repository declares 24.19.0. No runtime was installed or silently substituted. No library/package change, source edit, branch/worktree materialisation, commit, push, task-state edit or `_index.md` change was made.

| Priority | Next implementation/validation decision | Ownership |
|---|---|---|
| Medium | E42 response contract includes implemented 409; test/document sequential retries and preflight-vs-commit gate | API; explicit architecture/client agreement for changed semantics |
| Medium | E43 empty-page short-circuiting | API; migrated snapshot/query assertions |
| Medium | E44 retain original exhausted-retry diagnostic | API/shared logger usage, no new generic logger |
| Medium / measured | E44 final response from write results without increasing emitted SQL | API; concurrency/balance regression and SQL evidence |
| Medium | E45 variable scan-cost/config-bound evidence | API + Background configuration context; no silent truncation |
| Medium / shared bounded optimisation | E42/E41 existing-source eligibility and GET identity consolidation | API; preserve exact rank/auth checks |
| Low / measured | E45 smaller first batch, index candidate; E46 narrow metadata projections | API; Database only for a subsequently justified index |

No new infrastructure, queue, schema migration, secret cache or global refactor is approved. Reuse existing test harnesses, Shared logger and ownership boundaries. An implementation task would be separately defined only after the relevant design is agreed.

## External technical cross-checks — separate from source findings

Checked 2 November 2026, primary documentation only:

- PostgreSQL 17 transaction isolation: `https://www.postgresql.org/docs/17/transaction-iso.html` — stable Repeatable Read snapshots and conditional mutation/concurrent updater behaviour.
- Prisma v6 transactions: `https://www.prisma.io/docs/orm/v6/prisma-client/queries/transactions` — atomic rollback, retry scope and same-connection transaction execution.
- Prisma v6 client reference: `https://www.prisma.io/docs/orm/v6/reference/prisma-client-reference` — returned fields/selects on writes and conditions for native database upserts; nested reads can alter execution.

No generic documentation was used to replace source-specific contracts. The proposed query changes and race schedules remain recommendations/inferences until repository validation establishes them.

## Next increment

E47 PUT `/v1/merchant/discount-offers`; E48 GET `/v1/merchant/usage-history`; E49 GET `/v1/merchant/support/messages`; E50 POST `/v1/merchant/support/messages`; E51 POST `/v1/merchant/support/messages/:id/read`.

**Current progress: 46 reviewed; 15 remaining. No source/schema/task/index changes.**

---

# Increment 11 — five more endpoints (E47–E51)

**Review date:** 2 November 2026.
**Scope:** Discount-offer PUT, usage history, Support history, Support composition, and Support mark-read.
**Progress:** 51 of the original 61 method/path combinations reviewed; 10 remain.
**Status:** Static architectural assessment and recommendations, not implementation acceptance or a performance benchmark.
**Evidence:** `woocommerce-api-database-review-11-source-evidence.txt`, `woocommerce-api-database-review-11-source-manifest.json`; original repository paths and line numbers are preserved. Previous findings and progress statements remain historical records.

## Summary and counting method

The main opportunities are avoiding unnecessary coupon flag writes, combining usage totals, reusing previously loaded period data, and consolidating Support thread writes. A Support read-model consistency question must not be confused with a durable-state corruption finding. The existing mark-read race reread has a purpose and should not be removed without replacement.

All counts include the HTTP installation-authentication lookup. Count an explicit Prisma model method or raw database call once; exclude transaction-control commands, relation-query expansion, trigger/foreign-key work, Redis calls, retries, and logging. These are source-derived client-call counts, not measured SQL statements, affected rows, network round trips, or latency.

| Entry | Endpoint | Current successful path | Transaction assessment |
|---|---|---|---|
| E47 | PUT `/v1/merchant/discount-offers` | Existing settings: 13 changed nonempty selection; 11 changed empty selection; 10/9 identical nonempty/empty. Creating settings adds one call to the changed path: 14/12. | Retain Shop-coordinated atomic selection/mode/anchor update; isolation is not explicitly set by this method. |
| E48 | GET `/v1/merchant/usage-history` | Free-current available view: `7 + E`; paid-current available view: `8 + E`; past available view: `9 + C + A + E`. See definitions below. | Retain Repeatable Read and bounded evidence resolution. |
| E49 | GET `/v1/merchant/support/messages` | 5, including empty/out-of-range pages. | Read Committed, with Shop and installation SHARE locks; not a single support-data snapshot. |
| E50 | POST `/v1/merchant/support/messages` | 7 new without translation; 8 new with translation; 4 matching replay. | Retain atomic message/thread/PENDING-translation persistence. Redis dispatch stays after commit. |
| E51 | POST `/v1/merchant/support/messages/:id/read` | 5 fresh mark; 4 existing mark; 6 when another marker wins between initial read and conditional update. | Retain coordinated principal check, conditional write, and original winning timestamp. |

Usage-count terms: `C=1` when the current implementation queries a linked current paid period, even for `view=past`, otherwise zero. `A=1` for a supplied valid past-period cursor, which causes a separate anchor validation; otherwise zero. Past available views include one closed-period page query and one selected-period query, whether selected explicitly or by default. `E` is the evidence-resolution work for the returned usage page; it varies with event kinds, correction parents, reservation-derived outreach links, direct source references, and response version. It is zero on an empty usage page. Unavailable/no-selected-period branches return before the three usage queries and the evidence helpers.

Examples: a Free-current v1 page of ordinary directly linked recovery debits uses 9 calls (base 7, one reservation lookup, one recovery lookup); v2 adds one allocation reservation lookup, for 10. The equivalent paid-current v2 case uses 11. Corrections and outreach-attempt references add conditional queries. These examples are not universal bounds and are not SQL counts.

## E47 — PUT /v1/merchant/discount-offers

### Inspected behaviour and retained contract

`src/merchant/discount-offers/service.ts:134–180` serializes merchant Saves by locking the Shop, rechecks the installation, reads optional catalogue/settings, validates every requested Woo coupon ID against the authenticated Shop, reads the existing selected set, and either acknowledges an identical existing setting or writes the complete requested selection, mode and deterministic FIXED compatibility anchor. `projection():189–199` then rereads settings and selected IDs and fetches the Admin override. The method sets a 12,000 ms timeout but does not explicitly choose isolation. Deployed database isolation was not inspected.

Retain the transaction: selected coupon flags, mode and the real same-Shop FK anchor must not commit independently. Retain the 50-ID limit, duplicate-ID validation, full-set last-writer-wins semantics, deterministic sorted-ID anchor for FIXED, and anchor clearing for NONE/AI. Preserve unrelated settings and Admin override precedence.

A Save does not require a CURRENT catalogue or provider-valid coupon, and the read revision is informational rather than a Save precondition. The submitted set can retain dormant selections under NONE. Those are approved contracts, not missing validation to add during an optimisation. See `contract.ts:23–38,58–65` and workspace `docs/decisions/api/ARCH-036/API-002-read-and-save-woo-recovery-discount-selection.md` (Scope/Requirements). Some older catalogue text in that task predates the later relaxed catalogue policy; it is not used to override the inspected implementation or API-004 amendment.

A request for default NONE/empty without any settings row currently creates a settings row; it is not the same branch as the existing-settings identical no-op. Do not silently change that behaviour.

### E47-F01 — Avoid clear-and-reset writes for retained selections

**Classification:** Confirmed redundant row assignments on genuine changed requests; optimisation candidate.
**Priority:** Medium. **Owner:** moda_api.
**Evidence:** `service.ts:154–174`; Background `src/services/woo-coupon-catalogue.service.ts:211–229`.

Every changed request clears every currently selected Woo row, then sets every submitted row true. A mode-only change with an identical 50-coupon set performs 100 coupon-row assignments even though the final flags are unchanged. Replacing one of 50 selected coupons likewise assigns 100 rows, where only two flags differ. These are source-level affected-row examples, not measured database physical writes.

Calculate removed and added ID sets using the already-loaded current/desired lists. Update only removed IDs to false and added IDs to true; omit empty updates. Preserve tenant and Woo identity predicates and exact affected-row expectations. Do not weaken the preceding validation of ALL requested IDs merely because some IDs remain selected. The invariant that only this merchant mutation owns Woo `isAvailable` is explicit; the inspected Background updater preserves it.

This generally reduces rows modified, not necessarily calls: a replacement still needs two bulk updates. Mode-only changes can avoid both coupon-update calls. Keep the Shop serialization, settings write, full response validation and the final selected-set read during the first optimisation, rather than simultaneously removing all revalidation. Test rollback, overlapping Saves, provider updates, missing/deleted selected rows, same-shop scope, and all modes. Assess whether untouched coupon `updatedAt` values should intentionally remain unchanged.

**Review-only check:** `woocommerce-api-database-review-11-selection-model.py` compared baseline and difference-based flag results across 4,096 set transitions; zero mismatches. It models flag-set equivalence only, not SQL, locks, triggers, timestamps, authorization, row-count checks or performance. The fifty-coupon examples produce 100→2 and 100→0 simulated assignments.

### E47-F02 — Reuse settings result and already-locked onboarding state

**Classification:** Confirmed repeated lookup; bounded optimisation candidate.
**Priority:** Medium. **Owner:** moda_api.
**Evidence:** `service.ts:17–23,142,157–160,169–179,189–199`.

Settings are read before decision-making and again by the response projection; create/update results are discarded. Pass the original settings on the identical branch or the actual returned create/update projection on the changed branch. Keep the returned persisted `updatedAt` used by `offerRevision`, rather than reconstructing it from an assumed clock. Retain the selected-set and Admin override reads initially. This removes one model call on all successful save paths.

When settings are absent, the code rereads Shop solely for `onboardingCompleted`. Return that field from the first locked Shop query and reuse it, removing a further call on first settings creation. Do not reuse an unprotected pre-authentication observation.

Isolated targets: existing-settings nonempty changed 13→12; first settings nonempty changed 14→12 with both result-reuse changes. Existing identical nonempty 10→9. These targets do not include the variable benefit of F01, do not reduce override freshness checking, and do not claim equivalent SQL counts without inspecting emitted queries.

The broader narrow projections identified in E46 still apply. Avoid a speculative all-in-one helper rewrite spanning every merchant API.

### E47-F03 — Handled constraint/serialization failures lose the original cause

**Classification:** Confirmed diagnostic gap. **Priority:** Medium. **Owner:** moda_api.
**Evidence:** `service.ts:181–185`; `routes.ts:75–94`; `contract.ts:8–13`.

The service maps P2002/P2034/P2003 to a fresh `DiscountOffersError(409,'offers_conflict')` without cause. Preserve the original error through domain wrapping and Shared logging with bounded safe code/constraint metadata. A generic conflict response is not a substitute for knowing whether the actual failure was uniqueness, FK integrity, or serialization. Unexpected failures already reach the route's logging path. Do not auto-retry against changed merchant state or introduce a catalogue-generation precondition.

### Validation and decision

The three migrated-PostgreSQL discount test files cover overlapping full-set Saves, a Background-style scan/save race, same-Shop/foreign selections, removed/provider-ineligible saved selections, stable no-op behaviour, mode/anchor integrity and Admin precedence. The concurrent scan fixture models the accepted provider-owned field updates; it is not a claim that the live Background service was run here. `scripts/test-arch036-discount-offers-postgres.mjs:43–46` deploys migrations and is in the aggregate integration command.

**Decision:** retain atomic merchant selection. Prioritise set-difference writes and settings/Shop result reuse, preserve all identity/constraint checks, and correct error-cause loss. No new schema is justified.

## E48 — GET /v1/merchant/usage-history

### Inspected behaviour and retained contract

`history.service.ts:85–188` uses Repeatable Read. It validates Shop, installation and subscription, resolves current/closed entitlement periods, reads a bounded usage page plus exact count and signed quantity sum, then resolves recovery lineage and optional v2 charge allocation. `periods.ts` supplies bounded 25-period keyset navigation and separately validates the signed cursor anchor still exists with its same Shop/status/sort key. The installation's 32-byte credential digest is used to sign/verify period cursors; it is not an unused sensitive field to drop (`history.service.ts:91–106,122–125`).

Retain Free-lifetime behaviour with no fabricated bill ID, explicit unavailable paid-current behaviour, real CLOSED history after cancellation, late signed corrections belonging to the original period, tenant/provider filters, numeric precision checks, deterministic ordering, page limits, strict default-v1 shape, and optional v2 allocation evidence. Totals describe the ENTIRE filtered event set, not merely the returned page. Database lookup failures must continue propagating to the Shared logger rather than becoming fabricated unattributed rows. See `history.service.ts:21–79,109–188`, `contract.ts`, `sources.ts`, `attribution.ts`, and the API-022 scope amendment.

### E48-F01 — Combine count and sum into one aggregate

**Classification:** Confirmed same-filter duplicated aggregate work; recommended bounded optimisation.
**Priority:** Medium. **Owner:** moda_api.
**Evidence:** `history.service.ts:156–176`.

`usageEvent.count({where})` and `usageEvent.aggregate({where,_sum:{quantity:true}})` use exactly the same filter. Request `_count: {_all:true}` and `_sum:{quantity:true}` in the same aggregate and keep the separate ordered page query. This removes one client call on every available view, including a selected period with no events. Keep safe-integer count validation and existing Decimal/null/signed quantity conversion. Never calculate totalQuantity by summing the page, and never make negative corrections positive.

Prisma v6 documentation confirms aggregate requests can include a count and other aggregate outputs; this is a compatibility cross-check, not execution evidence. Verify generated client types and actual SQL during implementation. A zero total could later justify skipping the page query when computed first, but do not conflate that additional ordering choice with the one-call consolidation.

### E48-F02 — Avoid rereading period data and irrelevant current periods

**Classification:** Confirmed redundant branches. **Priority:** Medium. **Owner:** moda_api.
**Evidence:** `history.service.ts:116–144`; `periods.ts:5–8,19–62`.

1. For past-history requests on a paid subscription with a billingPeriodId, the implementation loads the linked CURRENT period even though the past-period helper and selected CLOSED-period logic do not use that result. Gate that lookup to current view. Keep initial principal/subscription integrity validation.
2. The period-page query already fetches the full `periodSelect`. For default historical selection, the service throws away the internal row, takes the projected first ID, and fetches the same row again. Retain a typed internal page-row result and reuse its first row, leaving the public period-page DTO unchanged. Explicit `periodId` can also reuse a matching loaded page row, but must still query and validate when not in the page. Do not silently fall back from an invalid requested period.

Together with F01, a past default-selected view with a linked current paid period can avoid three calls. Without that current-period branch, default past selection can avoid two. All savings are conditional and additive only when those branches actually occur.

Do not remove the cursor anchor-existence query as a superficially similar read. Its contract requires more than a valid HMAC: the anchor must still belong to the Shop's CLOSED history with the same sort key. Keep rotation/tampering rejection and deterministic previous/next navigation.

### E48-F03 — v2 duplicates evidence loading, but the predicates differ

**Classification:** Consolidation candidate requiring correctness design, not a trivial duplicate-delete.
**Priority:** Lower than F01/F02. **Owner:** moda_api.
**Evidence:** `sources.ts:45–65,73–127,148–162`; `attribution.ts:63–120`.

The recovery-link resolver loads correction parents and committed reservations. v2 allocation then loads parents and reservations again. A bounded page-scoped evidence bundle could share reads. However, the source resolver filters to original RECOVERY_CONVERSATION parents and committed debit rows, whereas allocation must inspect compensation references and contradictory combinations as well. Direct legacy recovery/conversation/message references and reservation-derived outreach sources also have distinct trust checks.

A merged loader must preserve each consumer's original filters, parent-chain rejection, foreign/missing/conflicting evidence handling, purchased-counter-plus-lot semantics, and v1's existing behaviour without loading v2-only fields unnecessarily. Do not infer charge category from current subscription, free-text sourceType or a plausible period. Retain ambiguity rejection, tenant checks and genuine-query-failure propagation. No fixed call target is asserted until such a loader is designed and validated.

An additional optional fast path is skipping charge-reservation reads when a v2 page contains no recovery metric needing allocation; current code queries once for any nonempty page. That is not required for the first correction and must preserve all non-recovery enum outcomes.

### Validation and decision

The migrated usage suite covers Free/current/past, purchased/promotional pools, signed late corrections, cancelled subscription history, period keyset paging, cross-Shop/tampered/rotated cursors and v2 evidence. Unit suites independently cover source-key parsing, recovery linking, attribution and failure propagation. Existing tests are evidence of scenarios in source, not new passes in this review.

**Decision:** retain Repeatable Read and exact accounting evidence. Combine aggregates and reuse period rows first. Treat evidence-loader consolidation as a separate bounded follow-up, not a reason to weaken the two attribution contracts.

## E49 — GET /v1/merchant/support/messages

### Inspected behaviour and retained contract

`support/read.service.ts:26–76` runs in Read Committed after Shop/installation SHARE-lock revalidation. It retrieves an ascending bounded page, then returns total visible and unread counts from ONE filtered aggregate. There is no count-per-category or count-per-message round trip. It performs five calls including authentication regardless of empty/out-of-range output.

Merchant messages are visible under the existing state rule; ADMINISTRATIVE/SYSTEM messages require AVAILABLE. Translation availability affects body projection: missing required translation must not leak the original body. Recovery links require the exact system code/version and same-Shop joined recovery. Pagination returns the requested page rather than clamping to the last page. An empty inbox does not create a thread. Suspended Shops may read and mark appropriate messages; they may not compose. Revoked/uninstalled credentials remain denied. Preserve all of these rules (`read.service.ts:12–17,29–75`; `routes.ts:25–49`; `installation.ts:14–39`).

### E49-F01 — Page and counts are not one snapshot despite the transaction

**Classification:** Source-supported read-model consistency risk/contract decision, not a proven data-corruption incident.
**Priority:** Medium. **Owner:** moda_api.
**Evidence:** `read.service.ts:29–59,76`; `installation.ts:19–33`; `commands.service.ts:97–125`.

The two support-data statements run under Read Committed. GET and mark-read both take compatible SHARE locks on Shop and installation. A page can therefore read `readAt=null`, another request can commit mark-read, and the later count can report zero unread. The locks pin principal eligibility; they do not lock all Support messages. Background initial-outreach notices also write Support rows without acquiring this API Shop lock (`moda-interact-background/src/services/checkout-recovery/recovery-initial-outreach-support-notice.service.ts:215–253`).

This is an inferred interleaving, not a reproduced runtime race. The task does not explicitly promise one snapshot across page/count, so record the observed consistency and decide whether a coherent response is required rather than declaring an existing accepted feature invalid merely for using Read Committed.

If coherent page/count/unread is required, prefer one parameterised support-data statement (page plus aggregate, including an empty page) or a deliberately tested Repeatable Read read transaction. One statement could reduce five calls to four; changing isolation alone does not reduce calls. Preserve existing principal locks initially and test rotation/suspension behaviour and serialization/error handling. Do not apply Repeatable Read globally to mark-read: its loser reread currently relies on a later Read Committed view of the winner.

Do not add mutation-strength locks across all Support history to make pagination consistent. No unconditional snapshot/isolation rewrite is accepted in this increment.

### E49-F02 — Translation LATERAL latest-row search is unnecessary under uniqueness

**Classification:** Confirmed redundant latest-row mechanism; planner-level optimisation candidate.
**Priority:** Low pending plans. **Owner:** moda_api.
**Evidence:** `read.service.ts:40–44`; `schema.prisma:3149–3174`; baseline migration line 1201.

The LATERAL subquery filters by `(messageId,targetLanguageTag)`, orders by createdAt and takes one AVAILABLE row. A canonical unique index already permits at most one row for that pair. A LEFT JOIN using the same pair and AVAILABLE predicate is sufficient. Preserve no-translation behaviour and the outer body-visibility logic; do not replace it with an INNER JOIN or admit another target language. This does not reduce database-client call count and may already be optimized adequately by PostgreSQL; compare actual plans before claiming savings.

The history index `(threadId,createdAt)` already exists. The extra ID ordering, count cost and deep offsets are measurement subjects; no speculative replacement index or cursor-contract change is required here.

### Decision

**Retain visibility, read-only behaviour and restricted lifecycle access. Establish the desired page/count consistency, then assess a single-statement projection and simpler translation join.** There is no basis to remove the combined exact/unread count, expose untranslated content, or create lazy thread state.

## E50 — POST /v1/merchant/support/messages

### Inspected behaviour and retained contract

`commands.service.ts:26–94` uses Read Committed, Shop-first exclusive coordination and installation SHARE revalidation. The request's actionId becomes a SHA-256 sourceKey over Shop ID, a delimiter and action ID. Its database-wide unique sourceKey therefore preserves shop-scoped replay rather than making unrelated merchants collide on a raw action string.

A matching body/kind returns the original message/translation IDs with no writes; changed-body key reuse conflicts. A new message creates/reuses its thread, inserts MERCHANT/AVAILABLE text, advances thread metadata and merchantMessageVersion exactly once, and optionally inserts a MERCHANT_TO_ADMIN/PENDING translation. The endpoint uses the Shop's configured language and existing Shared translation rules. No billing, customer WhatsApp send, or provider translation call is added.

Retain the transaction: message, thread state and pending translation must commit together. Dispatch occurs only AFTER commit and only for a newly created translation; an outage is deliberately a warning and does not turn the committed message into failure. The actual Background reconciler scans due PENDING/no-batch translations and repairs deterministic jobs (`translation-reconciliation.service.ts:89–104`), so the queue call is a hint rather than the only durable handoff. That source evidence does not attest deployed scheduler health or establish an end-to-end outage test was executed.

### E50-F01 — Thread upsert and thread bookkeeping update can be combined

**Classification:** Confirmed repeated write to the same row; bounded optimisation candidate.
**Priority:** Medium. **Owner:** moda_api.
**Evidence:** `commands.service.ts:48–69`; baseline thread schema and unique shopId index.

The first SQL upserts the thread and changes only updatedAt on conflict. After the message insert, a second SQL changes lastMessageAt, lastMerchantMessageAt, merchantMessageVersion, needsAdminResponse and updatedAt on that same thread.

Populate those fields on the insert path and atomically increment the existing version in ON CONFLICT DO UPDATE, returning the thread ID as today. The message and optional translation remain in the same transaction, so a later failure rolls back the earlier thread bookkeeping. Preserve assignments/admin ownership fields, timestamp policy, exactly-once version increment, and the replay check before all writes. Do not introduce a thread read-before-write race or reset the version to 1 on conflict.

Targets: new no-translation message 7→6 calls; new translated message 8→7; matching replay remains 4. Validate concurrent same/different action IDs, cross-Shop identical actions, conflicts, and rollback after message/translation failure. Admin reply concurrency also uses thread version bookkeeping and must remain correct; see `moda-interact-admin/src/lib/admin/merchant-support.ts:599–658` for thread locking and response-through-version logic. No cross-repository source change is requested merely to validate that invariant.

### E50-F02 — Queue error-event listener discards the original error

**Classification:** Confirmed diagnostic gap in a separate path, not universal missing enqueue logging.
**Priority:** Medium. **Owner:** moda_api.
**Evidence:** `translation-queue.ts:17–35`; `commands.service.ts:83–91`.

The service already logs an actual rejected `enqueue()` error with message/stack/cause. However, the Queue's `error` event handler is empty. An emitted connection error need not be the same error that later appears as a generic timeout or a rejected add operation; the emitted original is discarded here.

Route asynchronous queue errors through the shared logger with safe original details and bounded/deduplicated reporting, never log the Redis URL or message text. Preserve post-commit failure isolation and reconciliation. Do not make successful database persistence depend on Redis availability, or treat best-effort dispatch as a missing database transaction.

### Validation and decision

The migrated Support test submits five concurrent identical actions, verifies one message/version/translation and one dispatch, checks changed-body conflict and cross-Shop isolation, and proves an injected enqueue failure leaves PENDING state committed. It does not drive the real Redis dispatcher and Background recovery end-to-end. Add thread-upsert rollback and cross-writer tests before accepting F01, and error-event tests before accepting F02.

**Decision:** retain durable idempotent composition and translation recovery; combine the thread writes and preserve asynchronous error diagnostics.

## E51 — POST /v1/merchant/support/messages/:id/read

### Inspected behaviour and retained contract

`commands.service.ts:97–125` revalidates a principal under Shop/installation SHARE locks and allows the supported suspended-Shop state. It reads only same-Shop AVAILABLE ADMINISTRATIVE/SYSTEM messages; missing, foreign, merchant-authored, processing and failed messages return not-found.

If readAt already exists, it returns it without touching timestamps. Otherwise it performs a tenant-revalidated conditional UPDATE with `readAt IS NULL`, kind/state predicates and `RETURNING readAt`. If another marker wins, a second scoped SELECT returns the winner's timestamp.

### E51-F01 — The loser reread is necessary; update-first is a trade-off

**Classification:** Retain-current-path assessment plus optional workload-dependent alternative.
**Priority:** Low. **Owner:** moda_api.
**Evidence:** `commands.service.ts:100–124`; integration test `service.postgres.test.ts:108–123`.

The final reread is not the same as blindly rereading every update result. It runs only when the conditional update changes no row after the initial read. Removing it can turn a valid concurrent duplicate into an error or return an invented new timestamp.

An update-first version could perform the existing conditional UPDATE/RETURNING immediately, and only then fetch the eligible record if no row changed. It saves one call on the first successful mark but costs one on already-read replay (and missing/ineligible IDs):

| Path | Current | Update-first candidate |
|---|---:|---:|
| First mark | 5 | 4 |
| Already read | 4 | 5 |
| Concurrent loser needing a fresh read | 6 | 5 |
| Missing/foreign/ineligible | 4 | 5 |

This is not an unconditional optimisation. Choose only after measuring normal-versus-replay frequency and validating two-connection races. Retain exactly the same tenant, state, kind and lifecycle gates in both statements. Do not use an unconditional `UPDATE readAt=COALESCE(readAt,NOW())` as a shortcut: it would execute updates on replays and can touch updatedAt despite the current no-write replay contract.

Keep the transaction/installation pinning for now and the Read Committed winner-observation behaviour. Do not claim a broad transaction removal is safe solely because there is only one business UPDATE. The existing tests prove sequential replay timestamp stability, but do not orchestrate two marks reading null before either updates; add that case.

### Decision

**Retain the current correctness behaviour.** No mandatory source change is justified just to lower a best-case number. Benchmark update-first only if first marks dominate enough to offset slower replays.

## Cross-cutting validation, ownership and evidence

**Executed this increment:** source and contract inspection; inspection of actual Background translation recovery and coupon ownership; source-derived counts; complete evidence-file verification against the uploaded ZIP; review-only coupon-set model. Source archive SHA-256 remains `ee42bb83ee441ba9018779e760967a5bf87edcbc429eecc58699f1419863861b`.

**Not executed:** TypeScript unit/integration suites, Prisma generation, migrations, PostgreSQL statements, concurrent database races, EXPLAIN plans, Redis/provider operations, capacity tests, or latency benchmarks. The inspected environment has Node v22.16.0 while API declares 24.19.0; `node_modules`, Docker and psql are unavailable. No Node selection/install workaround was used and no containers were started.

All three relevant runners deploy canonical migrations and appear in the aggregate integration script: `test-arch036-discount-offers-postgres.mjs`, `test-arch035-usage-history-postgres.mjs`, and `test-arch035-woo-support-postgres.mjs`. Existing checked-in test cases and historical task reports are not newly executed validation.

No new table, index, migration, external service, task, branch, worktree, commit, push, acceptance decision or application patch is created by this review. Primary proposed implementation ownership is moda_api. Any later actual index/schema change would need moda_database ownership and its own measured justification. Keep `docs/decisions/**/_index.md` unchanged pending requested reconciliation. Future application/task patches retain the unique filename plus identical-patch ZIP and exact applicability/staging/commit/push protocol.

### External technical cross-checks (not evidence of application behaviour)

Checked 2 November 2026:

- PostgreSQL 17 transaction isolation: `https://www.postgresql.org/docs/17/transaction-iso.html` — statement snapshots, winner observation under Read Committed, and Repeatable Read differences.
- PostgreSQL 17 explicit locking: `https://www.postgresql.org/docs/17/explicit-locking.html` — SHARE lock compatibility and conflict with updating the pinned row.
- Prisma ORM v6 aggregation: `https://www.prisma.io/docs/orm/v6/prisma-client/queries/aggregation-grouping-summarizing` — combined count/aggregate request compatibility.

These are documentation checks only. Repository behaviour and contracts are derived from the uploaded snapshot. Proposed savings are architectural inferences, not runtime measurements.

### Next increment

E52–E56: GET `/v1/billing`; GET `/v1/billing/plans`; POST `/v1/billing/subscription`; DELETE `/v1/billing/subscription`; POST `/v1/billing/subscription/switch`. The final five from the original inventory are credit-purchase GET/POST, the Woo billing webhook, and the two health routes. Inventory reconciliation and the final consolidated report remain outstanding.

---

# Increment 12 — billing presentation and recurring commands (E52–E56)

**Review date:** 2 November 2026.
**Coverage after this increment:** 56 of the original 61 method/path combinations; five remain.
**Source:** the unchanged 1 November workspace archive identified in the header.
**Status:** static source assessment and proposed changes, not implementation or architect acceptance.
**Evidence:** `woocommerce-api-database-review-12-source-evidence.txt`; original line numbers are preserved. All paths below are relative to `moda-interact-api/` unless explicitly identified as workspace paths.
**Supplemental validation:** review-only blocking-predicate model; not SQL/application/concurrency validation.

## Summary and counting rules

| Entry | Endpoint | Current explicit database-client calls on the stated path | Transaction decision |
|---|---|---:|---|
| E52 | GET `/v1/billing` | 9 ordinary Free; 10 ordinary paid with cancellation-history check; conditional formula below | Retain Repeatable Read and staged integrity checks |
| E53 | GET `/v1/billing/plans` | 3 | Retain Repeatable Read; narrow translation rows |
| E54 | POST `/v1/billing/subscription` | 15 warm successful creation; 8 matching replay | Retain durable intent / provider / guarded outcome separation |
| E55 | DELETE `/v1/billing/subscription` | 11 successful cancellation; 7 matching replay | Retain coordination and deferred entitlement projection |
| E56 | POST `/v1/billing/subscription/switch` | 14 warm successful switch; 8 matching replay | Retain same-contract switch and target materialisation |

Counts include one installation-authentication model call. Recurring command counts additionally include one current sealed platform-configuration lookup as wired by `src/composition/billing.ts:26–30`. Injecting a static provider client removes that one call. Presentation reads do not fetch Woo provider credentials or make provider requests.

“Warm” means the target operational BillingPlan already exists, is valid, and the catalogue's `materializedAt` is non-null. These are successful non-retried paths. Excluded: BEGIN/COMMIT/isolation setup, implicit relation loading or nested-write expansion, trigger-internal queries, provider I/O, and retry amplification. These counts are not SQL statement/round-trip/latency measurements.

E52 formula: authentication 1 + Shop 1 + core 6 + current catalogue C + pending-operation target O + durable pending target D + confirmed-cancellation check K = **8 + C + O + D + K**. Each conditional is 0 or 1. The ordinary initialized Free case has C=1 and O=D=K=0. An ordinary paid case with a provider reference and `cancelAtPeriodEnd=false` additionally has K=1. Early validation failures stop before later calls and are not included in the table.

Recurring fresh intent counts: create 9, cancel 7, switch 10. Successful outcome counts: create 4 (advisory lock + collision check + CAS update + reread), cancel/switch 2 (CAS update + reread). Replays use 6 intent calls for create/switch and 5 for cancel, then no outcome transaction or provider write. These produce the table totals after authentication/configuration. Provider-error paths generally use the two-call failure outcome, not the create success collision path.

For create/switch, marking an existing unmarked catalogue adds one call. New operational materialisation adds two calls relative to the warm path (create plus marker), and another if merchant-knowledge source-pair configuration must be validated. Therefore successful cold create is 17 or 18; cold switch 16 or 17 under those assumptions. A one-time materialisation-uniqueness retry repeats the applicable intent work and is excluded from these totals. See `recurring-intent.ts:66–215`, `initial-free-activation.service.ts:175–230, 278–326`, and `recurring-outcome.ts:80–150`.

## E52 — GET /v1/billing

### Current behaviour and retained boundaries

`BillingPresentationReadService` executes the complete read on one Repeatable Read transaction client (`billing-read.service.ts:18–22`). Shop validation precedes six tenant-scoped core reads: Subscription/period/plan, lifetime/purchased counters, promotional selection, bounded unresolved recurring operations, latest purchase, and bounded unresolved requested purchases (`billing-snapshot.reader.ts:19–156`).

Conditional current/pending catalogue lookups and a confirmed-cancellation lookup follow staged validation (`billing-read.service.ts:31–67`). The projection keeps Free lifetime, paid included allowance, purchased and promotional balances separate. Scheduled cancellation is not immediate loss of prepaid entitlement; a confirmed provider DELETE can need presentation while authenticated lifecycle evidence is still catching up. These facts must not be replaced by a generic sum, by provider live reads, or by an implicit mutation.

**Retain the snapshot.** The migrated integration test deliberately pauses after the Shop read, commits a counter change on another connection, and expects the original counter version from the remaining read (`tests/integration/billing/presentation/billing-read.postgres.test.ts:208–250`). This source test was inspected, not rerun here.

The latest purchase and unresolved requested purchases are not interchangeable. An older pending purchase can block its own bundle while a newer completed purchase is the latest historical purchase. The `take:101` overflow check, bounded conflicting-operation checks, original validation order, no browser exposure of provider IDs/handles, and no write-on-read behaviour remain requirements (`billing-projection.ts:35–68`, `billing-purchase.projection.ts:13–55`). Promise.all within the transaction is not evidence of SQL parallelism or permission to use the root client.

### E52-F01 — Reuse a proven identical pending catalogue target

**Classification:** conditional duplicate lookup; bounded optimisation candidate. **Priority:** low/medium. **Owner:** moda_api.

When both an unresolved operation target and a durable pending operational plan exist, the service reads the former by MerchantPricingPlan ID and the latter by operational `shopifyPlanHandle` (`billing-read.service.ts:50–58`). If they represent the same catalogue row, the second query repeats the projection.

Include `shopifyPlanHandle` in the first narrow target result and reuse it only when it exactly matches the durable pending plan's handle. Otherwise retain the lookup and mismatch/missing-row validation. Operational BillingPlan IDs and MerchantPricingPlan IDs are different identities; do not compare them as though they were interchangeable. Preserve error precedence and common-snapshot semantics.

This removes **one call only on the matching dual-evidence path**. It does not reduce ordinary Free/paid reads. Tests must cover matching targets, mismatched handles/IDs, missing catalogue rows, invalid pending-plan relations, and the existing bounded integrity failures. No broad global cache or additional schema is justified.

### Endpoint decision

Retain the multi-query snapshot and distinct capacity/evidence reads. Pursue only proven same-transaction target reuse; no mandatory blanket consolidation of the six core reads is established.

## E53 — GET /v1/billing/plans

### Current behaviour and retained boundaries

Authentication is followed by a Repeatable Read transaction with one Shop projection and one active MerchantPricingPlan collection query (`plan-catalogue-read.service.ts:44–108`). The collection is bounded at 101 plans and 101 highlights per plan to detect overflow. It validates exactly one zero-priced Free plan, compatible paid plan shape and ordering, and chooses **one complete locale for the entire selectable catalogue**.

Candidate order is requested locale, its base, Shop default locale, its base, and English, deduplicated (`plan-catalogue-read.service.ts:225–246`). The response must not mix language fallbacks per plan or highlight. Currency compatibility is a snapshot/source rule, not newly researched provider guidance. Tests cover language fallback, incompatible paid pricing, missing/duplicate Free plans and incomplete localisation (`tests/unit/billing/presentation/plan-catalogue-read.service.test.ts:53–127`).

**Retain the snapshot, no-provider dependency, bounds and fail-closed completeness checks.** This is three explicit calls, not proof of three SQL statements because relations can expand.

### E53-F01 — Fetch only candidate-locale translations

**Classification:** over-fetching; projection optimisation. **Priority:** medium if catalogue size/transfer cost warrants it. **Owner:** moda_api.

Both plan translations and each highlight's translations are fetched without a locale filter (`plan-catalogue-read.service.ts:97–105`). Only the candidate locales can contribute to the response. After reading Shop, compute that existing candidate list before the catalogue query and constrain both translation relations to those candidates, retaining all candidates together.

The canonical migrations restrict persisted plan/highlight locales to the enumerated canonical set and enforce unique parent/locale identity (`20260915090000_arch014_merchant_pricing_catalogue/migration.sql:63,76–78`; `20260915170000_arch014_merchant_pricing_plan_highlights/migration.sql:31–40`). For valid canonical data, an exact `locale in candidates` filter can avoid fetching the other languages. An English-only candidate set can fetch one translation per plan/highlight rather than the whole retained locale set. This is a data-volume proposal; **the explicit call count remains 3**.

Preserve the existing canonicalisation/duplicate handling for the supported persisted domain, candidate ordering, complete-catalogue fallback, no mixed locales, Free-plan validation, paid-plan exclusions and 101-row overflow sentinels. Do not select only the first candidate before proving all plans/highlights are complete. Do not filter incompatible plans before overflow validation merely as an incidental rewrite: that changes observable validation/diagnostic behaviour. No locale migration is proposed.

Require migrated-schema tests for full English, exact regional language, base/default/English fallback, incomplete highlight translation, no common complete language, supported canonical locale identities, and unchanged output with fewer returned translation rows. Record actual relation SQL/data volume before claiming network-round-trip savings.

### Endpoint decision

Retain the three-call architecture; narrow translation relations rather than introducing caching, provider lookups or an N+1 per-plan translation fetch.

## Recurring-command architecture shared by E54–E56

The three routes reuse `RecurringSubscriptionCommandService`. Each resolves current sealed credentials before any intent transaction, persists or replays a shop-scoped BillingOperation, calls the provider only for a new intent after commit, and commits a guarded result afterwards (`recurring-subscription-command.service.ts:59–94`, `composition/billing.ts:26–30`). A successful create/switch returns AWAITING_CONFIRMATION, not paid entitlement. Cancellation acceptance confirms the provider command, not the end of prepaid coverage. HTTP routes return 202 for AWAITING_CONFIRMATION and 200 for CONFIRMED (`commands/routes.ts:104–157`).

The intent transaction explicitly uses Read Committed and locks Shop before Subscription. The target operational BillingPlan is materialised before external I/O, but the command does not activate it on the current Subscription, create a billing period or allocate included credits. ARCH-027-API-003 explicitly separates this from verified lifecycle reconciliation. Do not merge the intent and outcome into one network-holding transaction, remove the durable intent, or retry an ambiguous external POST/DELETE.

### C12-F01 — Commit-time installation generation is not revalidated

**Classification:** source-supported admission-boundary gap / required contract clarification; not a reproduced production incident. **Priority:** high before optimising mutation admission. **Owner:** moda_api, with architecture decision and integration tests.

HTTP authentication returns `installationId` and `credentialVersion` (`auth/woo-installation/authenticator.ts:38–75`). The recurring intent transaction rechecks Shop and Subscription but never queries WooCommerceInstallation or compares those principal fields (`recurring-intent.ts:66–105`). The BillingOperation insertion guard checks one-time-purchase identity, not installation status/version (`20261008110000_arch027_woocommerce_billing_persistence/migration.sql:336–359`).

Consequently, a request can authenticate under version 1, pause, allow a reconnect to rotate to version 2, then begin an otherwise eligible new recurring intent under the retained same-Shop principal. The Shop can remain ACTIVE with the same domain. Reconnect's installation rotation is at `installation/connection-service.ts:134–147`.

The original task explicitly requires the installed authenticator and current Shop checks but does not spell out a stronger linearization contract for in-flight credentials. Therefore this review distinguishes observed behaviour from the proposed stricter rule; it does not claim the task promised something it did not say.

Recommended mutation policy: validate and coordinate installation/shop binding, ACTIVE/unrevoked state, and the authenticated credential version within the intent transaction, at the durable admission point. Define behaviour for replays separately. The provider call must remain after commit; credentials changing after an already-admitted intent is a different boundary, not a reason to keep a lock over HTTP or discard valid provider outcome evidence. Determine lock ordering with reconnect, subscription writers and materialisation; test actual integration rather than simply inserting a query into an arbitrary position.

Tests should pause after real HTTP authentication, rotate/revoke the installation, resume each new create/cancel/switch command, and require the approved rejection with zero new intent/provider calls. Existing recurring PostgreSQL fixtures synthesise principal fields and do not create/revalidate an installation (`recurring-subscription-command.postgres.test.ts:23–24,51–85`); they remain useful for billing semantics but do not prove this boundary.

Any necessary additional query is a correctness cost. The performance-only targets below must not be read as a promise of the final net count after stronger admission checks.

### C12-F02 — Reuse the locked Shop result; do not remove Subscription coordination

**Classification:** confirmed duplicate lookup. **Priority:** medium. **Owner:** moda_api.

The transaction selects only Shop ID FOR UPDATE and immediately issues `shop.findUnique` for validation (`recurring-intent.ts:66–77`). Return the same required Shop fields from the locked query and validate that result. This removes one call on fresh and replay paths while preserving Shop-first locking and failure precedence.

Subscription likewise has a lock then a read, but its read includes related operational-plan facts. Consolidating it requires care not to broaden locks to shared/global plan rows or change null/missing-plan validation; do not count it as an automatic second saving. Replay currently also takes Subscription coordination before the same-key lookup. Moving replay earlier changes a deliberately tested lock/validation contract; leave it unchanged in this increment.

### C12-F03 — Full operation history is loaded to answer a blocking predicate

**Classification:** unbounded historical read under locks. **Priority:** medium/high for growing histories. **Owner:** moda_api.

For new requests, `billingOperation.findMany` loads all recurring operations for the Shop, ordered by time and ID, then uses two `.some()` checks (`recurring-intent.ts:106–134`). The data is needed only to establish whether an unresolved operation exists or a relevant CONFIRMED cancellation blocks the new request. Ordering is not consumed.

Use one bounded `findFirst` or EXISTS query over the exact combined blocking predicate. Preserve all three unresolved states; ignore unrelated ONE_TIME_CHARGE rows; preserve the provider-reference qualification; preserve the current `cancelAtPeriodEnd`/missing-reference branches and the explicit ordinary-Free-create exception after terminal cancellation. Do not use the latest N operations as a heuristic: an old unresolved operation can still block.

The existing `BillingOperation(shopId,state,createdAt)` and provider-reference indexes are evidence to inspect, not a reason to add another index without EXPLAIN. The client-call count remains one for this check; savings concern returned history, sorting and work while locks are held, not proven latency.

The review-only Python model compares the original pair of predicates with one bounded existence predicate across **189,252 cases**, with no mismatches. It covers 0/1/2 historical rows, recurring and unrelated operation kinds, states, reference matching, cancellation flags and the terminal-Free-reset context. It does not execute source TypeScript, SQL, Prisma, indexes, locks or providers. The abstract terminal context is not validation of Subscription data parsing.

### C12-F04 — Successful CAS outcome can return the updated row

**Classification:** update/read pair with a necessary race branch. **Priority:** medium. **Owner:** moda_api.

Outcome persistence executes a conditional `updateMany` and immediately reads the same BillingOperation when one row changed (`recurring-outcome.ts:97–121,137–148`). Replace the successful branch with a guarded returning update and the projection needed by the response/error mapper. Prisma 6.19.3 is pinned; official Prisma v6 documentation supports PostgreSQL `updateManyAndReturn` from 6.2.0. Verify actual generated client/SQL in the target environment.

**Keep the reread when zero rows change.** That path retrieves a newer webhook/outcome state and is intentionally tested (`tests/unit/billing/commands/recurring-outcome.test.ts:150–173,213–245`). Do not infer success from provider evidence after losing CAS, overwrite newer states, change the late-failure public mapping, or make the update unconditional. Keep provider-reference advisory lock/collision detection on create and same-contract verification on switch.

Outcome-only targets: successful ordinary create 4 -> 3 calls; successful cancel/switch 2 -> 1. Zero-row paths retain their update attempt and reread. If only one atomic statement remains in a successful non-create branch, transaction-wrapper necessity may be assessed separately; do not mechanically eliminate the enclosing transaction while changing race behaviour.

### C12-F05 — Provider and handled persistence errors lose original diagnostics

**Classification:** confirmed diagnostic loss. **Priority:** medium/high for uncertain billing outcomes. **Owner:** moda_api.

`woo-billing-client.ts:60–100` catches transport/read/parse failures without retaining their cause, and maps non-2xx status classes to generic codes without retaining the actual status or bounded provider message. `RecurringBillingCommandError` has no cause parameter. `recurring-outcome.ts:69–77,196–199` maps the error into a durable safe code and a new public domain error; original provider diagnostics are lost. Materialisation/uniqueness wrapping also loses its cause (`recurring-intent.ts:216–229`, `initial-free-activation.service.ts:227–229`).

Keep safe durable/public codes and uncertain-outcome semantics, but preserve original exception/cause, status, and bounded redacted provider response details for the shared logger. Never log Basic authorization, decrypted secrets, complete response/request bodies, sensitive confirmation URLs or return capabilities. Logging failure must not change a committed billing outcome. Do not retry provider writes merely to obtain better diagnostics.

Qualification: the platform-configuration reader already logs original configuration failures before rethrowing (`platform-configuration/composition.ts:40–56`). The service's preflight catch loses downstream correlation but does not establish that all configuration errors are silent. Improve original-error propagation without introducing another generic logger.

### C12-F06 — Provider configuration remains a prerequisite even for replay

**Classification:** observed availability/query trade-off, not an automatic optimisation. **Priority:** contract decision only. **Owner:** moda_api/architect.

Provider resolution precedes replay lookup (`recurring-subscription-command.service.ts:59–67`), so a matching replay still reads/decrypts current credentials and fails if those are unavailable, although it performs no provider write. The configuration task and unit test explicitly require **new** commands with unavailable credentials to create no intent and not even begin a persistence transaction (`tests/unit/woocommerce/billing/woo-billing-resolution.test.ts:8–29`; workspace `ARCH-043/API-004-woo-billing-credential-reader.md`).

Do not move resolution after persisting a new INITIATING operation just to save the replay lookup. Supporting durable replay during credential outage would require a deliberate replay-first/read-only path plus in-transaction revalidation for new requests and unchanged fail-before-intent behaviour. That could add reads on new paths. No such redesign or cache is proposed here.

## E54 — POST /v1/billing/subscription

### Current path and decision

Free-to-paid create requires the existing ACTIVE local Free subscription, null provider reference and null billing period. It validates the paid catalogue, resolves/materialises the operational plan inside the intent transaction, and snapshots the exact minor-unit quote and request fingerprint. After commit it calls provider create; confirmation records AWAITING_CONFIRMATION and a validated redirect. No current Subscription/billing-period/counter mutation occurs (`recurring-intent.ts:139–160,181–214`, orchestrator `78–94`).

Keep the unique `(shopId,requestKey)` idempotency scope, conflict on changed operation/target/quote, provider-write-once intent behaviour, no automatic provider retry, and the reference advisory lock plus cross-Shop collision lookup in the outcome transaction. Safe public HTTP acceptance is not paid-plan activation. The official provider's current external behaviour was not researched as part of this source review; provider semantics here are the source/task contract.

### E54-F01 — Eager feature graph on a warm materialisation path

**Classification:** over-fetching. **Priority:** low/medium pending measurement. **Owner:** moda_api.

The target catalogue always includes full feature mappings and related Feature rows (`recurring-intent.ts:143–146`). When an operational BillingPlan already exists, the resolver checks active/kind, optionally marks materialisation, and returns without consuming that graph (`initial-free-activation.service.ts:180–190`).

Start with required scalar catalogue data and load the feature/configuration projection only when materialisation is actually needed, or at minimum narrow the currently included relations to consumed fields. Cold-path lazy loading may add a query. Preserve pre-provider operational materialisation, merchant-knowledge validation, unique plan creation and one full-intent retry on the resolver's uniqueness race. Do not move materialisation after provider confirmation or let catalogue changes alter already-selected entitlement facts.

### Endpoint target and validation

Current warm success 15 calls; returning the locked Shop and successful outcome can produce an isolated performance-only target of **13** before any new installation admission query. Matching replay 8 -> 7 from Shop result reuse alone. Do not sum speculative translation, cold-path or replay-order changes into these figures.

Require migrated tests for first materialisation, warm reuse, mark-only path, concurrent cross-Shop materialisation, same-key replay, changed quote, different-key concurrency, provider collision, ambiguous transport, and original-error/redaction behaviour. Existing suites cover many of these but not new installation fencing or measured query/data-volume reductions.

## E55 — DELETE /v1/billing/subscription

### Current path and decision

Cancellation is allowed for a provider-backed paid ACTIVE/TRIALING/FROZEN subscription that has not already scheduled cancellation. It persists a CANCEL intent containing the provider reference but no target quote/plan, commits, calls provider DELETE, then commits CONFIRMED (`recurring-intent.ts:173–179,198–214`; orchestrator `69–75`). The paid subscription, current period and counters remain unchanged until verified lifecycle reconciliation. CONFIRMED means command acceptance, not loss of prepaid entitlement.

Matching cancellation replay uses the original operation/reference and never issues another DELETE. The confirmed-cancellation conflict guard is therefore **not unnecessary history**: it bridges the interval before the durable subscription reflects provider lifecycle evidence. Retain FROZEN cancellation eligibility; switch has narrower eligibility.

Common findings C12-F01–F06 apply. Warm/materialisation distinctions do not apply to cancel. Its current success costs 11 calls; locked-Shop/result-returning improvements alone target **9**. Replay 7 -> 6 through Shop result reuse. The race reread, unknown-outcome blocking and existing public error mapping remain mandatory.

Tests must include the pre-projection CONFIRMED window, cancelled-versus-terminal-Free transitions, already-confirmed replay, FROZEN cancellation, stale installation admission, provider success followed by outcome-persistence failure, and late provider outcomes that must not overwrite newer state.

## E56 — POST /v1/billing/subscription/switch

### Current path and decision

Switch requires an ACTIVE/TRIALING paid subscription with a provider reference and no scheduled cancellation. It checks the current catalogue identity by operational handle to reject selecting the same catalogue plan, resolves/materialises the new operational target, records the immutable quote/reference and commits. The provider switch targets that existing contract, and returned identity must match before an AWAITING_CONFIRMATION outcome is accepted (`recurring-intent.ts:161–183`; orchestrator `87–94`; `recurring-outcome.ts:41–50`).

The current-catalogue lookup is not redundant with the target lookup: operational and merchant-catalogue IDs differ, and missing/mismatched mappings are explicit integrity failures. Replacing it with a comparison between IDs from different tables would be wrong. Do not switch by creating a second provider contract, perform local proration, activate the plan on the command result, or treat a Free target as a normal paid switch.

E54-F01's feature-graph improvement applies to this target too, as do all common findings. Current warm success 14; locked-Shop/result-returning candidates target **12** before admission-policy additions. Matching replay 8 -> 7 from Shop reuse alone. Preserve the latest-catalogue quote check on replay: the existing unit and migrated tests require `idempotency_conflict` when the target quote has changed. Replacing it with the stored quote to eliminate that read would alter the accepted contract (`tests/unit/billing/commands/recurring-intent.test.ts:236–247`; `tests/integration/billing/commands/recurring-subscription-command.postgres.test.ts:198–205`).

Tests must cover same-plan rejection, mapping corruption, warm/cold materialisation, target quote changes, scheduled cancellation, provider-contract mismatch, replay, unknown outcomes, and new credential-admission rules. No new schema or provider integration is required for the query candidates alone.

## Validation, limitations and ownership

The existing `scripts/test-arch041-billing-postgres.mjs` creates disposable pg17+pgvector, generates the client, applies canonical migrations and runs billing presentation, recurring commands, credit commands and outcome-race suites (lines 13–19,34–75). It is registered in aggregate `test:integration` (`package.json:18`). No second test framework or live provider account is required to add the proposed deterministic tests.

Existing source evidence includes the presentation snapshot interleaving test, same/different-key recurring serialization, same-contract switching, cancellation preserving projection, concurrent operational plan materialisation, cross-Shop provider-reference collisions and CAS-loss tests. Historical task Completion Reports are not new execution evidence here.

Performed this increment: source/architecture/schema/test inspection; precise branch counting; archive/source byte verification; official technical cross-checks; and the limited 189,252-case blocking-predicate model. Not performed: npm install, TypeScript/application tests, PostgreSQL execution, migration execution, query plans, provider calls, stress tests or latency benchmarks. The available Node is v22.16.0 while API engines require 24.19.0; API node_modules, Docker and psql are absent. No live database or deployment was accessed. No branch/worktree was materialised, no task was claimed/accepted, no source/schema/_index.md was edited and no patch was produced.

All proposed local query/projection/error changes belong to moda_api. Stronger admission semantics require an explicit architectural decision and integrated reconnect/revocation tests; schema/index changes are not assumed. Correctness may add a necessary query. Infrastructure changes are not justified by this static batch; existing instrumentation should measure statements/rows/lock waits rather than introducing duplicate generic telemetry.

### External technical cross-checks — not application evidence

Checked on 2 November 2026:

- `https://www.prisma.io/docs/orm/v6/reference/prisma-client-reference` — PostgreSQL updateManyAndReturn from 6.2.0; candidate for guarded returning writes in pinned 6.19.3.
- `https://www.postgresql.org/docs/17/functions-subquery.html` — EXISTS expresses presence and can stop after finding a qualifying row.
- `https://www.postgresql.org/docs/17/transaction-iso.html` — Repeatable Read snapshot semantics and statement-level consistency distinctions.
- `https://www.prisma.io/docs/orm/v6/prisma-client/queries/transactions` — transaction-bound operations and external-I/O/connection considerations.

These support database-mechanism proposals only. They do not establish the application's emitted SQL, deployed configuration, provider behaviour, performance, or test results.

### Next increment

E57–E61: recovery-credit-purchase history GET, recovery-credit-purchase POST, Woo billing webhook POST, health liveness GET and health readiness GET. After that last endpoint batch, reconcile the original inventory against actual route registrations and produce the separately consolidated final report, retaining evidence/confidence labels and prioritised implementation/validation work.


---

# Increment 13 — final five endpoints (E57–E61)

**Review date:** 2 November 2026.
**Status:** Static endpoint coverage complete: 61 method/path combinations, including 59 business routes and two health routes. This is not implementation acceptance, production certification or measured performance validation.
**Source:** The same 1 November 2026 workspace ZIP used throughout.
**Evidence:** `woocommerce-api-database-review-13-source-evidence.txt`; original source line numbers appear after `|`. The source manifest maps every excerpt to its archive byte hash.
**Counting:** Explicit model and raw-query invocations, including HTTP authentication where used and database-backed configuration where noted. Excludes transaction control, nested/relation SQL expansion, triggers, provider calls and retries. Failed INSERT attempts count as client calls. Counts are not measured SQL statements or round trips.

## Final-increment summary

| Entry | Method/path | Explicit client calls on identified paths | Decision |
|---|---|---|---|
| E57 | GET `/v1/billing/recovery-credit-purchases` | 4, including an empty result | Retain Repeatable Read and exact count; skip empty-page fetch |
| E58 | POST `/v1/billing/recovery-credit-purchases` | 16 fresh successful provider outcome; 8 matching replay; 14 ordinary provider-rejection/unknown-outcome path | Retain atomic intent and guarded outcome; address principal boundary and repeated results |
| E59 | POST `/v1/billing/webhooks/woocommerce` | 2 fresh; 3 exact duplicate, with database-backed secret resolution | Retain receipt-only acceptance; duplicate read is justified |
| E60 | GET `/health/live` | 0 | Retain dependency-independent liveness |
| E61 | GET `/health/ready` | 1 attempted probe per request | Retain minimal query; bound outstanding work beyond the response deadline |

E58/E59 counts each include one configuration read in production composition. A static/injected configuration removes that call. E59 uses HMAC authentication, not installation bearer authentication. Health routes have neither installation authentication nor configuration reads per request.

## E57 — GET /v1/billing/recovery-credit-purchases

### Current implementation and transaction

The route authenticates the installed merchant. `WooPurchaseHistoryReadService.read()` then uses Repeatable Read for the Shop eligibility check, exact tenant/provider/status-filtered count, clamped page calculation and ordered purchase page. Ordering is `createdAt DESC, id DESC`; page sizes are 5, 10 or 20. The ALL filter removes only the status condition, not Shop or provider scope. [API `src/billing/purchase-history/service.ts:13–50`; `contract.ts:1–9`; `routes.ts:8–82`.]

The page projection loads the originating operation/bundle label, plan name, balances, provider valuation evidence and up to eleven Woo refund records. Eleven is an overflow sentinel: more than ten fails the projection; it is not an arbitrary extra record that should be removed. The response uses both the latest refund and a completed refund within the bounded collection. It suppresses arbitrary operator notes, provider contract IDs and sensitive internal payloads. The historical lot does not require a current paid subscription. WITHDRAWN amounts are shown as held, not available, and a previous refund attempt continues to suppress another attempt even after rejection. [API `projection.ts:5–40, 66–108`; `tests/unit/billing/purchase-history/service.test.ts:46–112`.]

**Retain the transaction and exact count.** Count, page, balances and bounded refund evidence are one read model. Do not infer counts from page length, gate historical purchases on current subscription, add provider refund calls or collapse latest/completed refund evidence into a single arbitrary row. Refund navigation remains WooCommerce Orders under the source contract; this API is read-only. The task's existing acceptance explicitly excludes live Woo payment/refund operational certification. [Workspace `docs/decisions/api/ARCH-027/API-006-expose-woocommerce-purchase-history-and-refund-actions.md:397–450`.]

### E57-F01 — Skip the page query when the same-snapshot count is zero

**Classification:** Confirmed unnecessary empty-result query. **Priority:** Low-risk efficiency candidate. **Owner:** moda_api.

`count()` at line 30 is followed unconditionally by `findMany()` at lines 33–39. Within this Repeatable Read snapshot, zero matching rows establish an empty page. Return the normal empty response with `total=0`, `totalPages=1`, `page=1`, the requested page size/filter and unchanged refund navigation. This reduces the empty-result path from **4 to 3 client calls**, including authentication. Nonempty paths retain both count and page lookup. [API `service.ts:25–49`.]

Required validation: empty results for ALL and each supported status, out-of-range page clamping, tenant/provider isolation, no relation/page lookup after zero count, and snapshot consistency during concurrent purchase/refund changes. Do not change the historical zero-balance or refund-attempt policy.

### E57-F02 — Migrated-schema read coverage is not established by the dedicated suite

**Classification:** Validation gap, not a demonstrated read defect. **Priority:** Before acceptance of query changes. **Owner:** moda_api validation.

The snapshot contains focused mock-backed purchase-history service, route, schema and OpenAPI tests. No dedicated purchase-history PostgreSQL test is present in the inspected integration tree or declared billing runner. The billing runner does contain migrated-schema purchase-command/outcome suites; those are not execution of this read projection. The task records developer validation of unit/typecheck/lint and explicitly withholds provider operational signoff. [API `tests/unit/billing/purchase-history/*`; `scripts/test-arch041-billing-postgres.mjs:13–19`; task API-006 review section.]

Extend the existing migrated billing harness with this read service and real refund/purchase relations. Add overflow, historical-lot, concurrent balance/refund and identical timestamp/ID order fixtures. Query-plan/index work remains conditional on representative measurements; existing purchase indexes already include Shop/status/time prefixes, so do not claim a full scan or add a speculative duplicate.

## E58 — POST /v1/billing/recovery-credit-purchases

### Current implementation and counted branches

Provider credentials are resolved before persistence. A Read Committed intent transaction locks Shop then Subscription, validates their current state, checks the shop-scoped request key, validates the current catalogue/bundle, checks for an unresolved purchase of that same bundle, and inserts a REQUESTED purchase plus INITIATING operation. The purchase captures the approved credit quantity but starts with `currentAmount=0` and `reservedAmount=0`. Free purchases legitimately have no recurring provider contract or billing period; paid purchases require a current OPEN period. [API `src/billing/commands/recovery-credit-purchase-command.service.ts:49–80`; `recovery-credit-intent.ts:37–223`.]

The provider charge occurs only after the intent commits. Successful provider evidence is stored in a second transaction with a provider-reference advisory lock, cross-Shop collision check and conditional transition from INITIATING to AWAITING_CONFIRMATION. Unknown outcomes remain durable and block blind retries; accepted provider initiation does not activate credits. Verified Background reconciliation owns activation. [API `recovery-credit-outcome.ts:32–114`; Background `src/services/woocommerce-billing/charge-receipt-processor.ts` and `charge-purchase-transition.ts`; task ARCH-027-API-004.]

Fresh-success count: authentication 1 + production credentials 1 + intent 10 + success outcome 4 = **16**. Intent calls are Shop lock/read (2), Subscription lock/read (2), request lookup (1), current catalogue (1), bundle (1), pending same-bundle check (1), purchase insert (1), operation insert (1). Matching replay uses six intent calls and no provider/outcome call, giving **8** with authentication/configuration. An ordinary rejection/unknown outcome uses two outcome calls, giving **14**; distinct error/collision branches are not conflated with this path.

**Retain the intent/provider/outcome separation and both atomic persistence boundaries.** The pending-bundle query is already a bounded `findFirst`, not the unbounded recurring-operation history pattern. CONFIRMED operations linked to a still-REQUESTED purchase can correctly remain blocking until verified activation. Preserve same-bundle blocking with independent other bundles, new lots after resolution, paid period snapshots, scheduled-cancellation eligibility, exact currency/minor-unit quoting and cross-Shop provider-reference coordination. Replay deliberately revalidates the selected bundle's current price/currency fingerprint: do not delete that query as redundant. [API `recovery-credit-intent.ts:80–89, 129–174, 235–259`; migrated tests at `recovery-credit-purchase-command.postgres.test.ts:171–659`.]

### E58-F01 — Installed-credential generation is not rechecked inside admission

**Classification:** Same authorization-boundary question as C12-F01, source-supported, not runtime reproduced. **Priority:** Resolve before mutation optimisations. **Owner:** moda_api with architect agreement on admission semantics.

The transaction validates Shop/domain/status but does not query `WooCommerceInstallation` or compare `principal.installationId` and `principal.credentialVersion`. A request authenticated before reconnect can therefore pass these later checks after rotation, provided Shop/subscription remain eligible. The BillingOperation insert guard does not supply an installed-credential generation check. [API `recovery-credit-intent.ts:37–95`; `src/auth/woo-installation/authenticator.ts:21–75`; `src/woocommerce/installation/connection-service.ts:134–147`; canonical ARCH-027 billing migration.]

The historical task requires installed authentication and current Shop checks, but does not expressly settle this in-flight rotation boundary. Record an explicit decision rather than relabelling a previously accepted contract as a proven security incident. Recommended policy: current installation binding/version/lifecycle must be validated and coordinated in the intent transaction before a new payment intent is admitted. Preserve Shop-first lock compatibility. A change after admission must not discard already-valid provider outcome evidence.

Validation: pause after real HTTP authentication, rotate/revoke before transaction admission, and assert no new REQUESTED purchase, operation or provider call from that stale request. Also test a rotation after accepted intent to ensure outcome recording remains safe. Existing fixtures inject principals; they do not prove the real authentication-to-admission race.

### E58-F02 — Reuse the locked Shop projection

**Classification:** Confirmed repeated lookup. **Priority:** Bounded optimisation. **Owner:** moda_api.

The first raw query locks only Shop ID, then `findUnique()` reads identity/platform/status/onboarding. Return those fields from the lock query and validate that locked result. Keep all checks and lock order. Save **one call** on fresh/replay paths. The Subscription read includes related plan/period integrity evidence; do not remove it without an explicit equivalent projection. [API `recovery-credit-intent.ts:38–78`.]

### E58-F03 — Return the successful guarded outcome update; keep the loser reread

**Classification:** Confirmed update/result-reread pattern. **Priority:** Bounded optimisation. **Owner:** moda_api.

Successful charge confirmation performs `updateMany()` then `requiredOperation()`. Use a conditional returning update for the winning branch and return its actual row. Preserve the read when no row changes: a verified receipt or other writer may have advanced durable state, and that newer state must win over the delayed HTTP/provider result. Apply equivalent care to failure updates. Keep provider-reference lock/collision checks and null/reference/confirmation predicates. [API `recovery-credit-outcome.ts:59–113`.]

Pinned Prisma 6.19.3 can be evaluated for PostgreSQL `updateManyAndReturn`; its v6 reference documents support from 6.2.0. Generated types, emitted SQL and race tests remain required. The isolated combined performance target is **16 -> 14 fresh-success** and **8 -> 7 replay** using F02/F03. Stronger installed-principal validation may add work; these are not promised net corrected-endpoint totals.

### E58-F04 — Narrow purchase-create output and retain original errors

**Classification:** Confirmed over-fetching and diagnostic gap. **Priority:** Medium for diagnostics; small for projection. **Owner:** moda_api.

`recoveryCreditPurchase.create()` returns the full purchase, but the caller consumes only `purchase.id`; use a narrow returned projection without skipping any write. The intent wrapper drops the original P2002 cause; provider transport/read/parse failures also lose their actual exception/response details through the shared Woo billing client's synthetic safe errors. Preserve original, redacted diagnostics while retaining safe public/durable error codes and no blind retry of uncertain writes. Configuration errors are already logged by the configuration layer; do not claim that all failures are unlogged. [API `recovery-credit-intent.ts:175–227`; `recovery-credit-outcome.ts:32–55`; `src/woocommerce/billing/woo-billing-client.ts:60–100`; configuration composition.]

Existing migrated suites cover Free and paid purchases, atomic rollback, exact replay, changed quotes, same-bundle concurrency, uncertain outcomes, later durable outcomes and provider-reference collisions. They are source-inspected, not rerun here. Extend rather than replace them.

## E59 — POST /v1/billing/webhooks/woocommerce

### Durable acceptance is already minimal

The route reads bounded exact bytes (maximum 262,144), validates content headers, obtains a fresh signing-secret snapshot, verifies the signature, validates the supported topic and minimum provider contract shape, then commits one unprocessed receipt before returning 204. It does not use merchant bearer authentication, resolve a Shop, apply payment/credit changes, call the provider or publish to Redis. [API `src/woocommerce/billing/webhooks/woo-billing-webhook-route.ts:9–76`; `webhook-payload.ts:36–65`.]

`persist()` calculates SHA-256 over the exact raw bytes and INSERTs with `select: { id: true }`. The durable uniqueness contract is `(topic, payloadSha256)`. An exact matching P2002 is followed by a lookup of receipt ID and provider contract ID; the latter is checked before duplicate acknowledgement. Other uniqueness errors and insert/read failures are not silently acknowledged. The wrapper retains original insert/read causes. [API `webhook-receipt.service.ts:20–65`; schema `WooCommerceBillingWebhookReceipt`.]

Production cost is **2 calls for a fresh receipt** (configuration + INSERT), **3 for an exact duplicate** (configuration + failed INSERT + lookup). A missing signature is rejected before the configuration lookup; a syntactically supplied but invalid signature may require that lookup. No explicit multi-statement application transaction is needed for a fresh single insert. This is not a claim that the INSERT has no implicit database transaction.

### E59-R01 — Retain the duplicate integrity read and receipt-only handoff

**Classification:** Retain, no mandatory query change. **Owner if future optimisation:** moda_api.

The duplicate read is not an unnecessary reread after every INSERT. It runs only after the specific uniqueness conflict and proves the acknowledgement's existing receipt identity. Replacing it with a preliminary SELECT adds work to every new delivery and does not remove concurrency handling. A no-op upsert merely to return an existing ID can introduce duplicate-path writes; an `ON CONFLICT DO NOTHING` shortcut must not assume it returns the pre-existing row. No replacement is justified without duplicate-rate measurements and full concurrency semantics.

Do not canonicalise JSON before hashing, deduplicate solely by provider contract ID, reset processed receipts on duplicate delivery, require a pre-existing BillingOperation, or add a second queue/outbox transport. The existing task explicitly makes this table the durable API-to-Background handoff. Background claims unprocessed rows directly; differing raw bytes or topics can create distinct receipts whose business effects must remain idempotent downstream. This review does not certify all Background billing effects. [Task ARCH-027-API-005: durable acceptance and out-of-scope sections; Background `charge-receipt-processor.ts:36–102`, subscription receipt processor.]

The migrated receipt test launches eight simultaneous identical persists and expects one inserted receipt and seven duplicates. It also checks a changed raw body and topic create separate receipts, with no Shop or BillingOperation required. The cross-domain runner uses `prisma migrate deploy` and is in the aggregate integration command. These are inspected tests, not fresh execution. [API `tests/integration/woocommerce/billing/webhooks/webhook-receipt.service.postgres.test.ts:24–64`; `scripts/test-arch041-cross-domain-postgres.mjs`; package scripts.]

## E60 — GET /health/live

The handler immediately returns `200 {status:"ok"}` with no database, installed authentication, secret lookup, transaction, provider or queue dependency. Keep it that way. The unit test injects an unavailable database and verifies zero probe calls. This route proves process HTTP responsiveness, not PostgreSQL readiness or full feature health. [API `src/server.ts:55–60`; `tests/unit/http/server.test.ts:52–66`; ARCH-026-API-001 health contract.]

**Decision:** Retain. No redundant database work exists. Adding SELECT 1 here would make liveness dependent on a condition already owned by readiness.

## E61 — GET /health/ready

### Current implementation

Each request starts a `database.probe()` promise. That adapter executes one parameter-free `SELECT 1` using the same Prisma client as business routes. Success returns 200; failure or the configured 2,000 ms wrapper deadline returns a bounded 503. Immediate database failures are logged with original error fields. There is no business-table query, multi-statement transaction, provider/Redis probe or secret configuration read. [API `src/server.ts:36–79`; `src/database.ts:11–26`; `src/runtime-config.ts:21,73`.]

Keep PostgreSQL-only readiness under the existing service contract. This response does not certify migrations, every required table, Redis, billing credentials or provider availability. Adding all those dependencies would be an architectural change, not a query optimisation.

### E61-F01 — The response deadline does not bound outstanding probe work

**Classification:** Confirmed promise-level behaviour; pool/resource consequence is an unmeasured operational risk. **Priority:** Reliability before scale claims. **Owner:** moda_api; involve moda_gateway only if approved deployment/connection settings must change.

`probeWithinDeadline()` rejects its wrapper after the timer, but has no cancellation signal, single-flight state or concurrency bound for the underlying probe. New requests start more probes even while prior ones remain pending. The source proves lack of cancellation/coalescing; it does not prove that the actual database query or driver will hang indefinitely, because driver/pool/server limits may independently apply. The deployed settings were not inspected.

A review-only harness copied this function body and removed only its TypeScript annotations. Twenty held fake probes at a 5 ms test deadline produced twenty timeout results while all twenty underlying promises remained pending. Releasing the fakes then reduced active probes to zero. This is isolated helper execution, not an HTTP, Prisma, PostgreSQL, connection-pool or performance test. The existing HTTP unit test proves timely 503 with one never-settling fake, but does not assert a bound on accumulated probes. [API `tests/unit/http/server.test.ts:89–100`; included readiness script/result and source-hash link.]

Recommendation: retain the simple query and response contract, but define a bounded underlying database acquisition/execution budget plus bounded in-flight admission/coalescing. A single shared in-flight probe can prevent a burst from creating an unbounded number of concurrent requests; failed/hung work must not poison future readiness indefinitely. Do not reset the guard at the HTTP deadline while the actual probe is still outstanding, cache an old successful result as proof of current readiness, or disconnect the application's shared Prisma client per failed probe. Expose original eventual failure details safely without replacing them solely with the wrapper timeout. Use existing logger/observability rather than a new generic telemetry layer.

Required validation: repeated concurrent HTTP checks while pool acquisition is blocked, database unavailable, query execution delayed and then restored; prove response deadlines, bounded outstanding work, recovery, stable liveness and no application-pool teardown. Measure effective driver/server timeout behaviour before asserting any bound on connections or production throughput.

## Final-increment validation and evidence

Inspected API purchase-history unit suites, migrated charge/outcome and webhook receipt suites, health HTTP tests, architecture/task requirements, canonical schema/migrations, production composition and Background receipt-consumption boundaries. No application test, migration, PostgreSQL query plan, provider call or live concurrency test was run. The only executable behavioural check was the isolated readiness helper described above.

Current environment: Node v22.16.0 versus repository declaration 24.19.0; no API node_modules; Docker and psql commands unavailable. No package installation, source patch, task status, architecture document, `_index.md`, branch, commit or push was performed. Reviewed historical completion reports remain historical evidence, not new test results.

The final-increment evidence contains **83 source files** checked byte-for-byte against the original ZIP. All **9,451 extracted regular files** match the archive. Two archived editor-lock symlink entries were intentionally not extracted; earlier reports' 9,453 count includes those two non-directory archive entries. This is a counting clarification, not source drift. Archive SHA-256 remains `ee42bb83ee441ba9018779e760967a5bf87edcbc429eecc58699f1419863861b`.

The final route inventory maps E01–E61 to actual handler families and their production composition. It contains 61 unique method/path pairs: 13 Woo platform, 38 merchant, 8 billing and 2 health. Dynamic parameter values are not extra routes; callback `:token` is the same route initially labelled `:id`. Validation is static registration inspection, not an HTTP smoke test. No original endpoint remains without a review entry.

## External mechanism checks (not application/provider evidence)

Checked 2 November 2026: PostgreSQL 17 transaction isolation (`https://www.postgresql.org/docs/17/transaction-iso.html`), INSERT/RETURNING (`https://www.postgresql.org/docs/17/sql-insert.html`, `https://www.postgresql.org/docs/17/dml-returning.html`), and Prisma v6 client reference (`https://www.prisma.io/docs/orm/v6/reference/prisma-client-reference`). These support only database mechanism proposals. No current Woo provider behaviour, production deployment, payment/refund certification or performance was independently verified.

## Completion boundary

**All 61 endpoint static reviews are complete.** The companion final report consolidates priorities, transaction decisions, optimisation candidates, implementation ownership and required validation. Findings remain proposals or source-supported hazards until implemented and validated; final architectural acceptance of the application is not granted by this review. No further endpoint batch remains.
