# WooCommerce hosted API
# Database architecture review — final report

**Moda Interact · 2 November 2026 · Revision 1**

**Review outcome:** Static analysis complete across **61 HTTP method/path combinations**: 59 business routes and two health routes. This is a decision report, not acceptance of implementation changes or certification of production performance.

**Baseline:** `moda-interact-workspace(20261101-205935).zip`, dated 1 November 2026.
**Archive SHA-256:** `ee42bb83ee441ba9018779e760967a5bf87edcbc429eecc58699f1419863861b`.
**Primary owner:** `moda_api`; Database, Background and Shared ownership applies where contracts or persistence rules cross repositories.

## 1. Executive decision

**Keep the current PostgreSQL + Prisma architecture. Correct the identified consistency and lifecycle gaps first, then remove bounded, demonstrably redundant work. Do not launch a blanket transaction-removal or caching refactor.**

The review found useful existing safeguards worth preserving: atomic activation, consent/evidence commits, version-checked merchant commands, consistent read snapshots, durable payment intents before provider I/O, receipt-based webhook acceptance, asynchronous reconciliation, tenant-scoped evidence and no-write replay branches. The source does not justify replacing these mechanisms merely to lower a call counter.

The highest-priority work is concentrated in a small number of cross-writer or cross-service boundaries: prepared-message moderation identity, follow-up claim-key uniqueness, installation-generation admission/revocation, knowledge source-generation writes, and upload cleanup versus finalisation. Most of those findings are source-supported interleavings or contract mismatches, not incidents reproduced in this environment. [Review entries E11–E12, E29–E31, E35–E40, C12-F01 and E58-F01; evidence companions 03, 04, 07, 08, 09, 12 and 13.]

Efficiency work should then focus on avoidable writes and over-fetching, not just method-call totals: knowledge ordering/deletion, coupon-selection differences, repeated locked-row reads, count-only navigation, duplicated aggregates, warm plan feature graphs and excessive relation projections. Some improvements save calls; others save rows transferred or modified. Their latency benefit is unmeasured. [E01, E07, E17–E19, E24–E27, E33–E38, E43–E48, E50 and E54–E58.]

**No application code, schema, architecture/task status or `_index.md` file was changed. No branch, commit, push, task acceptance or production migration is implied.** The final package contains the report, a complete endpoint ledger, original-line source evidence, manifests, route inventory and review-only model results. No application patch was produced because this phase was analysis, not implementation.

## 2. Scope, counting and confidence

The scope is the hosted `moda-interact-api` service, including its Woo-specific, merchant, billing and health routes. The WordPress plugin, Shopify application, Database and Background repositories were consulted only where required to understand these boundaries. This is not a full independent audit of all Background financial workflows or the merchant plugin.

| Route family | Method/path combinations | Coverage |
|---|---:|---|
| Woo platform/install/consent/restore/authorisation | 13 | Reviewed |
| Merchant configuration, conversation, knowledge, reporting and Support | 38 | Reviewed |
| Billing reads, commands and webhook | 8 | Reviewed |
| Liveness and readiness | 2 | Reviewed |
| **Total** | **61** | **No original route remains unreviewed** |

The original inventory's callback placeholder `:id` is represented as `:token` in the final inventory because the implementation consumes a secret bearer token there. It is the same route, not an additional endpoint. Path parameter values do not count as separate routes. Registration reconciliation was static source inspection, not execution of 61 HTTP requests. [Final endpoint inventory JSON; increment-13 route/composition evidence.]

### Evidence categories

**Confirmed source finding** means the query, predicate, projection or error wrapping is visible in the uploaded snapshot. It does not automatically establish production frequency or impact.

**Source-supported risk** means the inspected writers and guards permit an interleaving or contract mismatch. A deterministic integration test is still required to reproduce and then prove the correction.

**Optimisation candidate** means a smaller data-access pattern is proposed with explicit invariants and validation. None of the candidates has been deployed or benchmarked here.

**Review-only execution** means a small model or copied helper was run outside the application. These checks support particular equivalence/resource observations; they do not validate Prisma SQL, migrations, locks, pool behaviour or provider integration.

**Historical validation** means evidence recorded in an existing task/completion report. It remains historical and is not reported as a fresh run. The cumulative ledger retains each increment's qualifications.

### What the call counts mean

Counts in the ledger are explicit Prisma model-method or raw-query invocations along named branches. They include authentication and database-backed configuration when stated. They exclude BEGIN/COMMIT/isolation statements, nested/relation query expansion, trigger-internal SQL, retries and external provider/Redis work. A bulk update may change many rows despite counting as one call. A relation projection may execute more than one SQL statement.

Do not add all endpoint counts to estimate platform load. Real cost depends on route mix, replay/no-op frequency, tenant concentration, pagination depth, changed-row cardinality, relation loading, lock waits and provider/configuration paths. Woo workload and deployed pool settings were not measured. The architect's reference Shopify event volume is not evidence of Woo HTTP demand.

## 3. Prioritised correctness and reliability work

The order below is an architectural recommendation derived from the completed review. It is not a set of newly materialised tasks or a reclassification of existing task acceptance. Related fixes must still be bounded by repository ownership.

### 3.1 Prepared-message moderation identity — E30-F01

**Finding:** Send-command status hashes the original merchant text; canonical persistence and Background moderation use the prepared customer-visible body. When preparation changes the text, the status lookup can miss the applicable assessment and show moderation pending. The current test's passthrough preparation conceals the mismatch.

**Decision:** Use persisted prepared content for HUMAN_TEXT assessment matching. Missing preparation remains pending; do not fall back to unmoderated original text. Keep template hashing, tenant scope, input kind and content-digest safeguards. This finding does not demonstrate that Background sends unmoderated content.

**Owner and proof:** moda_api, with Background/schema contract review. A migrated test must use deliberately different original/prepared bodies and cover allowed, blocked, review-required, retryable, missing and wrong-digest cases. [E30; evidence 07: API status service, prepared-content migration and Background prepared-command/dispatcher sources.]

### 3.2 Follow-up retry key versus global claim identity — E29-F01

**Finding:** Public command retry keys are unique per Shop, but the same value is copied into globally unique `RecoveryOutreachAttempt.initiationKey`. Independent merchants choosing the same permitted key can conflict. Background consumers compare these fields, so an API-only prefix is not a safe isolated change.

**Decision:** Agree one internal claim identity that preserves public shop-scoped retry semantics and all cancellation/dispatch comparisons. Do not weaken the one-follow-up slot, uncertain-send or billing invariants.

**Owner and proof:** Coordinated API/Background/Database review; Shared only if a reusable cross-service contract is required. Test identical keys across two merchants, same-Shop replay, cancellation/reclaim and uncertain outcomes. [E29; evidence 07.]

### 3.3 Read-authorisation revocation and callback lifecycle — E11–E12

**Finding:** Revocation can target an old-generation pending attempt that its trigger refuses to update, aborting a valid newer-generation revoke. An older authenticated revoke request also lacks a transaction-local version check before targeting a newer grant. Callback replay treats some overlapping duplicates differently from committed replays, and commit-time guards do not enforce Shop status after provider verification.

**Decision:** Retain atomic attempt/grant transitions. Correct generation-scoped cancellation and current-principal admission, explicitly coordinate lifecycle checks and recognise only a genuinely completed matching replay as success. Do not swallow failed revocations or reactivate a revoked grant on replay.

**Owner and proof:** moda_api with Database guard review. Run reconnect, pending old attempt, new grant, stale revoke, expired lock-wait attempt, simultaneous callbacks, suspension-during-verification and post-revoke replay schedules on the migrated schema. [E11–E12; evidence 03–04.]

### 3.4 Knowledge-source generation against Background writers — E35–E37

**Finding:** Web PATCH/DELETE check generation in memory but later write by source ID only. The Shop lock does not coordinate with Background's source-row generation writer. Stale metadata can be applied or a newer source generation deleted. Refresh/URL-change paths have an additional unique revision-insert rollback guard; their risk is not identical to a silent metadata overwrite.

**Decision:** Put tenant and expected generation in the actual mutation predicate with exact affected-row validation, or lock/revalidate the source in an agreed order. Preserve metadata-only versus ingestion changes and current replay rules.

**Owner and proof:** moda_api with Background compatibility validation. Pause the API between read and mutation and execute the actual Background entitlement-generation writer. Test PATCH, DELETE, refresh, URL change and rollback. [E35–E37; evidence 08–09.]

### 3.5 Upload finalisation versus cleanup, and replay identity — E39–E40

**Finding:** The finaliser can read pending asset state and later overwrite cleanup's DELETED status using an ID-only update. It can then attach a revision to an object that cleanup is deleting. Completed-finalisation replay finds an arbitrary revision referencing the asset, although legitimate reprocessing creates several such revisions. Intent retry does not bind purpose, and final policy reread omits a MIME-membership check it has already fetched.

**Decision:** Coordinate the asset transition with cleanup through a fresh locked or conditional state/expiry/metadata check held through revision insertion. Resolve the original intake result deterministically. Bind the complete intended retry metadata and apply the freshly read MIME rule. Keep R2 HEAD/GET verification outside the transaction.

**Owner and proof:** API/Background lifecycle review; Database involvement only for agreed durable metadata/constraint changes. Test both cleanup-wins and finalisation-wins schedules, expiry while waiting, rollback, replay after REPROCESS/ENTITLEMENT_CHANGE, changed purpose and MIME policy changes during verification. [E39–E40; evidence 09.]

### 3.6 Current installed credentials at billing admission — C12-F01 and E58-F01

**Finding:** Recurring commands and credit purchases authenticate installation version before admission, but their intent transaction rechecks Shop/subscription rather than installation version. A rotation between those phases is not detected. Historical tasks do not explicitly settle that in-flight boundary, so this is an architectural decision supported by source—not a reproduced breach.

**Recommended policy:** Revalidate binding, version, active status and revocation when admitting a new durable financial intent. Keep provider I/O outside the transaction; a credential change after admission must not discard valid provider outcome evidence.

**Owner and proof:** moda_api. Use real authentication, pause, reconnect/revoke, and resume each command. Also verify post-admission rotation does not erase durable provider outcomes. Additional correct authorization work is not a performance regression to avoid. [E54–E56, E58; evidence 12–13.]

### 3.7 Configuration reads inside a transaction through the root client — E31-F01

**Finding:** Follow-up catalogue code receives a transaction client but obtains sender configuration through a reader that captured the root Prisma client. That query may need another pool connection while the transaction holds its connection and, on POST, mutation locks. The resulting small-pool stall is an inference; deployment pool behaviour was not measured.

**Decision:** Make the existing reader transaction-aware or deliberately resolve configuration before the transaction with an explicit freshness contract. Avoid adding configuration reads to text/replay branches. Unexpected configuration failures must not silently become a normal empty catalogue. Preserve existing configuration-layer original-error logging and fail-closed send behaviour.

**Owner and proof:** moda_api; test actual production composition with constrained pool capacity and configuration failures, not a constant stub. Do not substitute a new secret cache, duplicate cryptography or a larger pool for connection ownership. [E31; evidence 07.]

### 3.8 Coherent read models and deliberate exceptions — E16, E19, E49

**Finding:** Category profile and active configuration can come from different commits. Support page and unread count can differ under Read Committed. Feature PUT's initial eligibility and final projection need an explicit concurrent Admin-change test before reloads are removed.

**Decision:** Use one statement or a justified snapshot for correlated read models. Do not automatically apply Repeatable Read to every endpoint: knowledge reads explicitly use a best-effort projection, restoration deliberately performs a later eligibility reread, and several mutation/no-op contracts differ.

**Owner and proof:** moda_api. Controlled writer barriers must prove an old coherent or new coherent result where required; retain explicitly approved best-effort semantics elsewhere. [E08, E16, E19, E33, E49; evidence 03–05, 08, 11.]

### 3.9 Readiness bounds actual work, not only the response — E61-F01

**Finding:** A two-second wrapper deadline returns 503 but does not cancel/coalesce its underlying probe. The copied-helper test left 20 of 20 fake probes outstanding after all wrapper timeouts. Actual Prisma/driver/server limits and pool impact remain unmeasured.

**Decision:** Keep SELECT 1 and independent liveness. Define bounded acquisition/execution and in-flight admission, without caching stale success, indefinitely poisoning recovery or disconnecting the shared client per check.

**Owner and proof:** moda_api; gateway involvement only for approved infrastructure settings. Test bursts, blocked pool acquisition, outage and recovery with real PostgreSQL; prove outstanding work remains bounded. [E61; evidence 13 and isolated readiness result.]

### 3.10 Diagnostic integrity and validation wiring — cross-cutting

Several domain wrappers discard original Prisma/provider causes; a service-level logger cannot reconstruct them. Activity can label a database authentication error as a queue error. Feature PUT overwrites initial lookup timing fields during its final reload. Some integration runners use `db push` rather than canonical migrations; the existing AI-delay migrated suite is missing from the aggregate command.

**Decision:** Preserve original message/code/cause and safe response details through the shared logger, distinguish expected races from unexpected constraint/infrastructure failures, and keep public errors bounded. Do not add duplicate generic observability. Correct timing labels before using those fields as optimisation evidence. Add focused cases to existing migrated harnesses rather than claiming mock assertions prove locking. [E01, E03–E04, E06, E08–E09, E12, E19, E23, E29, E32–E38, E44, E47, E50, C12-F05, E58; evidence by entry.]

## 4. Transaction decisions to preserve

| Boundary | Recommended treatment | Representative entries |
|---|---|---|
| Multiple durable records form one outcome | Retain atomic transaction; narrow work inside it | Activation; consent/evidence; category publication; command/claim; source/revision; purchase/operation |
| Read/check/write protected by revision, authorization or policy | Retain coordinated mutation even with one final UPDATE | Selection, response delay, recovery policy, conversation control, metadata changes |
| Several reads form a consistent presentation snapshot | Retain snapshot or prove one-statement equivalent | Billing, exact pagination, effective settings, usage history |
| Deliberately later eligibility revalidation | Retain later read; do not freeze an earlier snapshot as a shortcut | Recovery restoration |
| Explicit best-effort read model | Do not silently change to a long transaction | Merchant knowledge GET |
| Single conditional snapshot write | No additional interactive transaction merely because it writes | Store context |
| Single durable webhook receipt | No extra application transaction/outbox/queue for acceptance | Billing webhook |
| External provider/R2 work | Keep outside database transactions; revalidate where needed afterwards | Billing commands, installation proof, upload finalisation |
| Process liveness / database connectivity | Zero calls for liveness; one bounded connectivity probe for readiness | Health endpoints |

Lock ownership matters independently of isolation. A Shop lock does not automatically coordinate a Background writer that only locks a source or asset; two different advisory-key schemes are not the same lock. Serializable isolation does not invent a missing credential predicate. Conversely, an apparently repeated read may deliberately enforce a later-state check or recover the winner of a conditional-update race. [E04–E08, E11, E35–E40, E51, E54–E58; technical mechanism references in section 9.]

Do not weaken consent/STOP authority, tenant isolation, prepared-content moderation, billing balances, provider outcome ambiguity, unique generation/claim constraints or immutable evidence to lower query counts.

## 5. High-value bounded efficiency candidates

These are independent examples. Do not add their savings across branches or assume a percentage latency improvement.

| Candidate and condition | Existing source-level work | Candidate target | Preserve |
|---|---|---|---|
| E01 already-onboarded active reconnect | 5 client calls | 3 | Transaction-local revalidation and observed-version CAS |
| E07 first brand creation | 7 calls | 6 | Merge/ordering and worker coordination |
| E17 first category publication | 16 calls | 14 | Atomic profile/prompt/configuration publication |
| E26 nonempty first/latest message page | 8 calls | 6 | Ownership, stable order and moderation digest |
| E27 nonempty first related page | 7 calls | 5 | Exact Shop/customer relation |
| E33 first knowledge page with ACTIVE evidence | 13 calls | 12 | ACTIVE versus latest-generation distinction |
| E34 web-source common writer checks | 7 helper calls | 4 | Return locked authoritative fields; plan validation |
| E38 swap two positions among 100 sources | 200 position writes | 4 | Membership, uniqueness, staging and rollback |
| E47 replace one of 50 selected coupons | 100 row assignments | 2 | Full-set validation, anchor and tenant scoping |
| E48 count plus quantity total | 2 aggregate calls | 1 | Signed quantities, exact totals and overflow checks |
| E50 new Support message, no translation | 7 calls | 6 | Message/thread atomicity and version semantics |
| E57 empty purchase-history result | 4 calls | 3 | Exact zero count and unchanged empty response |
| E58 new purchase with successful provider outcome | 16 calls | 14, before any stronger auth cost | Locked Shop validation and newer-outcome winner reread |

Other worthwhile reductions are projection-only: candidate plan translations, settings fields, metadata-only ownership loaders, warm catalogue feature graphs and write-return fields. These reduce bytes/row materialisation, not necessarily SQL count. Batching a collection of writes is useful only if row ownership, revision, timestamp, ordering and retry semantics survive.

Some candidates have explicit trade-offs. An update-first mark-read improves first-use but worsens already-read replay calls. Smaller initial coupon batches save clean-page transfer but can add round trips for invalid prefixes. Lazy materialisation data improves warm paths but may add a cold-path query. Native versus emulated upsert can reverse an apparent model-call saving. Measure actual branch frequencies and SQL before choosing. [E19, E41, E44–E45, E51, E54; detailed ledger.]

## 6. Index and capacity decisions

**No blanket index migration is justified by this static review.** Preserve proven unique/partial indexes and inspect actual deployed definitions before proposing removal. Two source-declared duplicate lookup structures were recorded for CheckoutRecovery generation and Conversation recovery identity; their removal remains conditional on dependencies and workload plans. [Increment 03 shared index finding.]

Measure targeted candidates: latest REST-read attempt by installation/Shop and sequence; expired/live upload-intent counts; purchase-history status/ALL ordering; coupon filtering/batching; deep offset and case-insensitive recovery searches. Existing indexes already cover several important prefixes. Do not describe a query as a full-table scan without a plan. [E10, E24, E39, E45, E57.]

The coupon reader's 5,000-coupon comment represents the default scan setting, not the maximum configurable bound. Pathological legacy-invalid prefixes can produce many application batches; that is a capacity assumption to correct, not evidence of typical traffic or permission to truncate results. [E45-F02.]

The largest static write amplification is in collection rewrites, not necessarily the endpoint with the most scalar lookups. Prioritise rows changed, lock duration, pooled connection occupancy, table/JSON bytes and retry amplification alongside SQL statement count. Actual latency, sustained Woo throughput and database sizing remain unknown.

## 7. Final batch decisions (E57–E61)

### E57 — Purchase history

**Retain:** Four-call authenticated Repeatable Read path; exact count/page semantics; narrow bounded refund evidence; historical-lot independence from current subscription; one-attempt refund suppression; Woo Orders navigation; no refund mutation/provider call.

**Change candidate:** After zero count, skip `findMany()` and return the normal empty page: four calls become three. Keep the eleven-refund overflow sentinel and both latest/completed-refund meanings. Add dedicated migrated read-service coverage; existing focused tests are mock-backed, while migrated command suites are not proof of this read projection. [Evidence 13: purchase-history service, projection, tests, billing runner and API-006 task.]

### E58 — Credit-purchase creation

**Retain:** Resolve credentials before creating financial intent; lock Shop then Subscription; preserve current quote fingerprint on replay; one REQUESTED purchase plus one INITIATING operation commit together; provider call outside transactions; guarded outcome; zero usable credits until verified reconciliation; distinct Free and paid-period requirements.

**Correct/decide:** Current installation generation at admission; original provider/Prisma diagnostics. **Optimise:** return validation fields from Shop lock, return the successful conditional outcome directly, and select only purchase ID from its create result. Keep the zero-row outcome reread because newer durable evidence wins. The observed ordinary path is 16 calls with database-backed credentials, matching replay eight; proposed isolated savings must not conceal any added authorization work. [Evidence 13: credit-intent, purchase-command, outcome, client and migrated tests.]

### E59 — Billing webhook

**Retain unchanged:** Exact bounded-byte signature verification; topic/raw-body-digest deduplication; durable unprocessed receipt before 204; narrow INSERT return; duplicate-only integrity lookup; original failure causes; no installed merchant auth, Shop lookup, provider call, business transition or Redis handoff.

Production database-backed secret resolution yields two calls for fresh acceptance and three for a duplicate. The duplicate read is necessary evidence, not a fresh-path reread. No extra application transaction or outbox is justified. Raw-body whitespace and topic differences intentionally remain different receipt identities; downstream business idempotency is separate. The existing migrated test exercises eight simultaneous identical inserts. [Evidence 13: webhook route, receipt, canonical schema, migrated test and API-005 task.]

### E60 — Liveness

**Retain unchanged:** Zero database calls. It proves process HTTP responsiveness even during PostgreSQL failure. Do not add a connectivity query, secret lookup or business-table check. [Evidence 13: server lines 55–60; health unit test lines 52–66.]

### E61 — Readiness

**Retain:** One parameter-free SELECT 1, PostgreSQL-only scope, safe 200/503 responses and a two-second HTTP deadline. **Correct:** define bounded underlying acquisition/execution and in-flight work. The isolated copied-helper result proves timeout does not cancel/coalesce its fake probes; it does not prove a production connection leak. Add real HTTP/pool outage-and-recovery tests. [Evidence 13: server lines 36–79, database adapter, runtime config and helper/result.]

## 8. Validation and implementation sequence

### Evidence actually available

The review used the exact snapshot and its canonical schema/migrations, route composition, tests, tasks and selected cross-service consumers. Increment 13 includes 83 source files with byte hashes. All 9,451 extracted regular files match the ZIP. Two archived editor-lock symlinks were deliberately excluded from extraction; historical 9,453 counts include those archive entries. The original archive hash is unchanged.

The source declares Node 24.19.0, Prisma 6.19.3 and Shared 3.1.0. This environment has Node 22.16.0, no installed API dependencies, and no Docker or psql commands. **No application unit/integration suite, PostgreSQL migration/query plan, provider call or production benchmark was executed for the final review.** Existing task reports and source tests are not substituted for those executions.

Review-only checks retained in the package include pagination, ordering/compaction, selection, recurring-blocker and catalogue equivalence models, plus the final copied readiness helper. Their results are scoped to their specific predicates or data structures. They are not proof of runtime transactions, indexes, moderation, collation or provider correctness.

### Acceptance requirements before implementation approval

Use the repository's declared Node/toolchain and existing disposable PostgreSQL 17 + pgvector runners. Test against canonical migrations, not only `db push`, wherever constraints/triggers/partial indexes matter. Do not copy unrelated validation commands into every bounded task.

For each selected change, record baseline and changed SQL traces on the same fixtures, including success, identical replay, no-op, stale revision, conflict and error paths. Capture actual statements and affected rows, transaction duration, pool wait, lock wait and p50/p95/p99 latency under a stated workload. Use existing framework/Prisma instrumentation rather than a competing generic telemetry layer. Do not extrapolate an all-endpoint capacity figure from static call counts.

Concurrency proof needs two or more database connections with barriers around the exact read/write gap. Use actual competing writers where the hazard crosses services. Validate complete rollback after late failures, original errors with redaction, and recovery after queue/provider/configuration outages. Read-only endpoints must remain free of writes; final-send/consent/payment gates must remain authoritative.

### Suggested sequencing

**First: correctness contracts and regression fixtures.** Resolve installed-principal admission policy, claim identity and original upload-result identity; reproduce and fix moderation/content, source generation, cleanup and revocation hazards. Define owners before changing schema or Shared contracts.

**Second: diagnostic and bounded-query changes.** Preserve causes, fix timing attribution, narrow projections, reuse locked/write-return rows, skip zero-result fetches, combine equivalent aggregates and bounded existence checks. Keep each outcome independently reviewable.

**Third: measured write/plan improvements.** Stage only changed ordering rows, update only coupon differences, choose batch sizes from evidence, inspect candidate indexes and pool/readiness limits. Do not add infrastructure merely because the platform may grow.

**Finally: cross-service validation and rollout review.** Database/Shared changes, if any, precede their consumers; system-test tasks remain terminal validators, not dependencies for unfinished implementation. Record actual deployment order and rollback constraints for the chosen changes. Provider sandbox/payment/refund certification remains a separate outstanding requirement where the source tasks say so.

### Ownership and delivery

API owns route/service queries, error handling, projections and local tests. Database owns schema, constraints, migrations and indexes. Background owns generation/cleanup/dispatch/receipt-consumption behaviour. Shared owns genuinely reusable cross-service contracts/mechanics. Gateway is involved only when an agreed solution changes deployment or infrastructure settings.

No new ARCH ID or task was invented in this report. When implementation is authorised, define bounded canonical task files, explicit commands, file scope, dependencies and stop conditions. In an external snapshot-only session, such tasks are **defined but not materialised** until the developer's launcher prepares the real worktrees.

For any later actual change delivery, retain the user's protocol: unique task/attempt patch name; identical patch inside its ZIP; applicability check using `git apply --check --whitespace=error-all`; exact repository/worktree navigation and staging/commit/push commands; no `docs/decisions/**/_index.md` reconciliation without explicit approval. Do not mark a proposed correction Accepted merely because it appears in this report.

## 9. Source map and external checks

The authoritative review basis is the uploaded code and architect role, not external recommendations. The cumulative ledger `woocommerce-api-database-review-working-notes-r13.md` contains all endpoint findings, branch counts, priorities, preserved behaviours and per-increment validation limits. Evidence files `01` through `13` reproduce inspected source with original line numbers and source hashes; manifests make them traceable to the ZIP. The final inventory JSON maps each route below to its source handler family.

Technical mechanism checks were limited to PostgreSQL 17 isolation/RETURNING/INSERT and Prisma v6 aggregate/returning-update/transaction behaviour, as referenced in individual increments. They do not verify current Woo service behaviour or production configuration. Final cross-checks, 2 November 2026: PostgreSQL 17 transaction isolation, INSERT and returning modified rows; Prisma ORM v6 client reference. The exact links are retained in the cumulative ledger for reproducibility.

Previous review statements are retained as historical evidence; the final summary does not silently upgrade a candidate or model into measured validation. Where a stronger consistency/authorization contract is unresolved, the report labels the decision explicitly.

## 10. Complete endpoint decision register

Each row links conceptually to its stable E-number in the cumulative ledger. The evidence companion for the row's increment contains original source references. Transaction mode and all branch-specific counts remain in that ledger to avoid presenting one misleading count for a multi-path endpoint.

### Woo platform

| Review | Method and route | Decision |
|---|---|---|
| E01 | POST `/v1/woocommerce/installations/connect` | Retain activation transaction; consolidate transaction-local Shop and credential-result reads. |
| E02 | GET `/v1/woocommerce/installation` | Retain one authentication lookup; no write or explicit transaction needed. |
| E03 | POST `/v1/woocommerce/activity` | Retain queue acceptance; preserve and correctly classify database/Redis errors. |
| E04 | POST `/v1/woocommerce/whatsapp-consent` | Retain consent/evidence atomicity; acknowledge duplicate before recipient locking. |
| E05 | GET `/v1/woocommerce/customer-recovery-selection` | Assess snapshot read without recipient write-style locks; preserve transactional principal check. |
| E06 | POST `/v1/woocommerce/customer-recovery-selection` | Retain revision/STOP coordination and transaction; preserve original errors. |
| E07 | POST `/v1/woocommerce/shop-brand` | Retain merge/ordering locks; reuse newly created brand result. |
| E08 | POST `/v1/woocommerce/recovery-restore/resolve` | Retain later eligibility reread; require full-schema validation and useful diagnostics. |
| E09 | POST `/v1/woocommerce/read-authorizations` | Retain guarded pending insert; fix error classification and clarify Shop lifecycle gate. |
| E10 | GET `/v1/woocommerce/read-authorization` | Retain non-locking status read; measure latest-attempt index candidate. |
| E11 | DELETE `/v1/woocommerce/read-authorization` | Correct stale-generation cancellation and current-principal gating; retain atomic revoke. |
| E12 | POST `/v1/woocommerce/read-authorizations/callback/:token` | Retain attempt/grant atomicity; fix overlapping replay and commit-time Shop lifecycle check. |
| E13 | GET `/v1/woocommerce/read-authorizations/return` | Retain informational read; preflight impossible locale proofs before secret lookup. |

### Merchant configuration and recovery reads

| Review | Method and route | Decision |
|---|---|---|
| E14 | GET `/v1/merchant/bootstrap` | Retain narrow business projection; no mandatory query refactor established. |
| E15 | PUT `/v1/merchant/store-context` | Retain conditional write; assess no-op suppression without losing stale-principal conflicts. |
| E16 | GET `/v1/merchant/store-categories` | Make profile/configuration projection coherent; narrow prompt text and identity queries. |
| E17 | POST `/v1/merchant/store-category` | Retain atomic publication; remove new-lineage history reads and pending-draft pre-read. |
| E18 | GET `/v1/merchant/feature-preferences` | Retain consistent snapshot; narrow entitlement projections and consolidate identity reads. |
| E19 | PUT `/v1/merchant/feature-preferences` | Retain revision/entitlement checks; fix timing overwrite; assess batched changed-row persistence. |
| E20 | GET `/v1/merchant/recovery-policy` | Retain settings/override snapshot; narrow fields. |
| E21 | PUT `/v1/merchant/recovery-policy` | Retain existing result reuse and no-write replay semantics. |
| E22 | GET `/v1/merchant/ai-response-delay` | Retain snapshot; select delay/revision only and consolidate read identity. |
| E23 | PUT `/v1/merchant/ai-response-delay` | Retain ordered locks and no-op; preserve error causes and include existing suite in aggregate tests. |
| E24 | GET `/v1/merchant/recoveries` | Retain exact count/page snapshot; skip page fetch after zero count; measure deep paging/search. |
| E25 | GET `/v1/merchant/recoveries/:id` | Retain actual inbound/eligibility evidence; do not substitute summary timestamps. |
| E26 | GET `/v1/merchant/recoveries/:id/messages` | Use lookahead and bounded existence; narrow ownership load; retain moderation matching. |
| E27 | GET `/v1/merchant/recoveries/:id/related` | Use lookahead and bounded existence; retain exact Shop/customer identity. |
| E28 | GET `/v1/merchant/recovery-summary` | Consolidate narrow identity/policy reads; decide snapshot contract. |

### Conversation and knowledge

| Review | Method and route | Decision |
|---|---|---|
| E29 | POST `/v1/merchant/conversations/:id/messages` | Correct public retry-key/internal claim uniqueness mismatch; retain durable atomic admission. |
| E30 | GET `/v1/merchant/conversations/:id/send-commands/:commandId` | Match moderation against prepared outgoing text; narrow fields; review read lock contract. |
| E31 | GET `/v1/merchant/conversations/:id/follow-up-templates` | Fix root-client configuration query within transaction and failure-to-empty classification. |
| E32 | POST `/v1/merchant/conversations/:id/control` | Retain conversation/audit atomicity, Shop coordination and revision semantics. |
| E33 | GET `/v1/merchant/merchant-knowledge` | Preserve explicit best-effort read; direct ACTIVE-revision query instead of aggregate/fetch. |
| E34 | POST `/v1/merchant/merchant-knowledge/sources` | Retain source/revision atomicity; return locked principal fields and skip unused preference lookup. |
| E35 | PATCH `/v1/merchant/merchant-knowledge/sources/:id` | Guard actual mutation by tenant/generation against Background writer. |
| E36 | DELETE `/v1/merchant/merchant-knowledge/sources/:id` | Guard actual delete by generation; compact only surviving rows whose positions change. |
| E37 | POST `/v1/merchant/merchant-knowledge/sources/:id/refresh` | Retain generation/revision atomicity; strengthen UPDATE predicate and common-helper reuse. |
| E38 | PUT `/v1/merchant/merchant-knowledge/order` | Retain full membership/atomic order; stage only changed rows and use ID/position projection. |
| E39 | POST `/v1/merchant/merchant-knowledge/upload-intents` | Bind purpose to retry metadata; preserve immutable asset identity and bounded live-intent admission. |
| E40 | POST `/v1/merchant/merchant-knowledge/upload-finalize` | Coordinate cleanup and final asset state; bind replay to original intake; recheck MIME policy. |
| E41 | PATCH `/v1/merchant/merchant-knowledge/uploads/:id` | Bound eligible-prefix reads and skip identical metadata; retain metadata-only contract. |
| E42 | POST `/v1/merchant/merchant-knowledge/uploads/:id/reprocess` | Retain guarded two-write transaction; bound eligibility and document 409/preflight boundary. |

### Promotions, discounts, reporting and Support

| Review | Method and route | Decision |
|---|---|---|
| E43 | GET `/v1/merchant/promotions` | Retain exact counts and snapshot; skip zero-count pages. |
| E44 | PUT `/v1/merchant/promotions/selection` | Retain grant balances/selection atomicity; assess returned-row reuse with emitted-SQL evidence. |
| E45 | GET `/v1/merchant/discount-catalogue` | Preserve safety and complete pagination; measure variable batch cost and correct assumed scan bound. |
| E46 | GET `/v1/merchant/discount-offers` | Keep settings readable independently of catalogue readiness; narrow fields. |
| E47 | PUT `/v1/merchant/discount-offers` | Persist selection differences only; reuse settings and locked onboarding state. |
| E48 | GET `/v1/merchant/usage-history` | Retain accounting snapshot; combine count/sum and reuse period rows; preserve evidence semantics. |
| E49 | GET `/v1/merchant/support/messages` | Decide page/unread snapshot contract; simplify unique translation join. |
| E50 | POST `/v1/merchant/support/messages` | Combine thread bookkeeping writes; retain durable translation repair and original queue errors. |
| E51 | POST `/v1/merchant/support/messages/:id/read` | Retain conditional mark and concurrent-winner reread; update-first is workload-dependent. |

### Billing and health

| Review | Method and route | Decision |
|---|---|---|
| E52 | GET `/v1/billing` | Retain capacity/operation snapshot; reuse proven identical pending catalogue target. |
| E53 | GET `/v1/billing/plans` | Retain whole-catalogue locale fallback; retrieve candidate translations only. |
| E54 | POST `/v1/billing/subscription` | Retain intent/provider/outcome separation; strengthen admitted principal; bound operation-history check. |
| E55 | DELETE `/v1/billing/subscription` | Retain deferred lifecycle effects; reuse locked rows and guarded write results. |
| E56 | POST `/v1/billing/subscription/switch` | Retain exact replay quote and same-provider-contract checks; narrow warm materialisation reads. |
| E57 | GET `/v1/billing/recovery-credit-purchases` | Retain exact history/refund snapshot; skip page read after zero count; add migrated read tests. |
| E58 | POST `/v1/billing/recovery-credit-purchases` | Retain REQUESTED purchase plus intent atomicity; strengthen principal gate and reuse write results. |
| E59 | POST `/v1/billing/webhooks/woocommerce` | Retain durable receipt acceptance, exact raw digest and duplicate integrity lookup; no extra outbox. |
| E60 | GET `/health/live` | Retain zero-database dependency and bounded process-only response. |
| E61 | GET `/health/ready` | Retain SELECT 1 and safe response; bound underlying probe work, not just response deadline. |

## Final conclusion

**The endpoint analysis is complete. The implementation work is not claimed complete.** Preserve the architecture's useful atomicity and evidence boundaries, correct the prioritised cross-writer inconsistencies, and then validate the bounded efficiency changes against the real migrated database. The report supplies a reviewable plan and traceable source findings; it does not claim measured speedups, production-scale capacity, provider certification or approval of unimplemented patches.
