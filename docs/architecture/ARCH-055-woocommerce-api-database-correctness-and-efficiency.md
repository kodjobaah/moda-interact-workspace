---
id: ARCH-055
title: WooCommerce hosted API database correctness and efficiency
status: proposed
coordinator: moda_architect
created: 2026-11-02
updated: 2026-11-02
---

# ARCH-055: WooCommerce hosted API database correctness and efficiency

## Status

**Proposed implementation initiative; definition revision 2.** The user requested a new initiative after the 61-endpoint review. This revision incorporates the user's API-policy boundary and the explicit ARCH-053-DATABASE-001 definition pattern. It freezes the proposed implementation contract; it does not claim accepted application changes. Thirteen tasks are **defined but not materialised**: nine API functional units, one Database contract set, one Background consumer, one narrowly required Shopify producer, and one terminal system validator.

`ARCH-055` is unused in the uploaded snapshot: all architecture identifiers found in its docs are <= ARCH-054. No current Git remote was inspected. Before materialisation, the real launcher/architect must reject a conflicting live ARCH-055 allocation rather than overwrite it. This is a snapshot-derived allocation, not a reservation in the developer's remote.

The report's findings, candidate counts and runtime-validation limits are retained without substantive changes (trailing whitespace normalised for strict patch application) in `docs/architecture/ARCH-055/review-report.md` and `review-ledger.md`. New decisions below are explicitly **ARCH-055 design choices**, not claims that the report had already selected their exact implementation.

## Problem

The static review completed 59 business method/path combinations and two health routes. It found a small set of cross-writer lifecycle and evidence gaps plus bounded repeated reads, writes and over-fetching. A task per endpoint would duplicate work across shared service files; one all-API task would combine unrelated correctness boundaries and become unreviewable.

The existing PostgreSQL + Prisma + Redis/BullMQ architecture is retained. Most transactions protect legitimate atomic state, revision policies or coherent reads. Source-supported race schedules must be reproduced with real migrated PostgreSQL before the correction is accepted. No production incident, throughput, latency saving or provider certification is inferred from a method-call count.

## Goals

Correct the reported prepared-content, installed-principal, human-claim, source-generation and asset-cleanup boundaries. Reduce proven redundant work within the same functional service changes. Preserve public contracts and deliberate replay/no-op differences. Make original provider/Prisma diagnostics and actual SQL/row evidence reviewable. Cover all 61 endpoints with one primary API owner, including retained behaviour.

## Non-Goals

No 61-task endpoint checklist; no one-task blanket refactor; no new cache, ORM, database, message broker or microservice; no unmeasured index batch; no changes to plan pricing/credits, STOP scope, outreach caps, AI-delay range, checkout lifetime or live payment/refund provider certification. ARCH-052 remains discount/outreach work; ARCH-053 remains restore/URL work. This initiative does not repurpose either. Old tasks and all `_index.md` files remain untouched until explicit final reconciliation.

## Source and evidence

Baseline archive: `moda-interact-workspace(20261101-205935).zip`. SHA-256: `ee42bb83ee441ba9018779e760967a5bf87edcbc429eecc58699f1419863861b`. The report is dated 2 November 2026 against the 1 November snapshot. `source-baseline.json` records source and report hashes; `review-endpoint-inventory.json` preserves the reviewed route inventory.

The review was static plus isolated models; application tests, PostgreSQL plans, provider operations and production capacity were not executed in that phase. This definition package only adds architecture/task documents. No implementation, migration or task acceptance is implied.

Additional narrow implementation inspection found a second human-send producer at `moda-interact/app/services/recoveries/recovery-human-commands.server.ts:254–278`. It uses the same public-key/attempt-key convention as the Woo producer. This is why ARCH-055-SHOPIFY-001 is required for a safe shared-consumer change; it is not a new independent Shopify audit.

## Consolidation and repository responsibilities

Group by functional lifecycle and shared source touchpoints, not by URL or individual query. Each implementation task owns one repository. Source changes, error preservation, focused tests and query evidence stay in that task. The small Schema/Background/Shopify boundaries remain separate because merging them into an API task would violate ownership and obscure rollout dependencies.

API owns nine units: installed lifecycle; consent/recovery ingress; merchant configuration; recovery conversation inbox; knowledge lifecycle; commercial projections; financial command admission; Support; runtime/readiness and final API validation wiring. Database owns the two persisted fields, exact historical backfill, one original-intake unique index and narrowly corrected existing attempt guard/time CHECK. Service owners enforce workflow policy; no new business-policy triggers are selected. Background owns follow-up dispatch/release consumers. Shopify owns its existing producer. System-test owns final cross-service execution. No Shared or Gateway task is justified by the chosen design at definition time.

## Current architecture

HTTP installation authentication yields an authoritative Shop/installation/version principal. Individual services use conditional writes or transactions for durable commands, and several read models intentionally use Repeatable Read. Consent decisions and immutable evidence commit together. Merchant human-send commands and sequence-two claims are durable; Background moderates prepared content, applies final admission and dispatches. Knowledge commands write pending revisions, while Background reconciles generations and uploaded-object cleanup. Billing commits intent before provider I/O and then conditionally persists outcomes. Billing webhooks durably insert raw-digest receipts without Redis. Liveness is database-independent; readiness currently wraps a SQL probe in a response deadline.

These boundaries remain unless an ADR below explicitly says otherwise. Retained observations and exact source references are in the frozen ledger.

## Proposed architecture and contracts

### ADR-01 — Current read-authorisation lifecycle

API transaction-local admission enforces that attempt mint/consume-success and grant mint/rotation require the current ACTIVE Woo Shop and ACTIVE, unrevoked, matching installation generation. Successful consume/grant still commit in the same transaction and preserve monotonic rotation/sequence. Failed terminalisation is not success: a PENDING attempt may become FAILED even after expiry, without granting authority. The only Database correction is the existing attempt function and its consumption-time CHECK so FAILED terminalisation may occur after expiry/rotation while preserving identity/single-use and successful-consumption safeguards. The existing grant function/deferred successful-attempt coupling is unchanged; new Shop-status/revokedAt policy checks are not added to SQL triggers. API revocation validates its current principal and cancels current-generation pending attempts atomically with local grant revocation; unusable old-generation attempts do not block it. Overlapping callbacks acknowledge only a proven matching completed outcome. Replay cannot reactivate a revoked or superseded grant. Provider verification stays outside the committing transaction.

### ADR-02 — Public retry identity is separate from internal claim identity

**New chosen persistence contract:** `MerchantConversationSendCommand.followUpClaimKey String? @db.VarChar(255)`.

For every NEW `RECOVERY_FOLLOW_UP_TEMPLATE` command, both Woo and Shopify preallocate command.id using the existing globally unique Node primitive and persist that exact value as followUpClaimKey. The claimed sequence-two attempt stores the same value in initiationKey. Public `(shopId, idempotencyKey)` and payload hashing remain unchanged. HUMAN_TEXT uses null. Background reads the persisted key for every claim, fence, restart, cancellation, repair and release comparison.

Historical template commands are data-preservingly backfilled with their own old idempotencyKey; their existing immutable attempt keys are **not rewritten**. The service treats this field as immutable; no new database key-policy/immutability trigger is added. API/Shopify admission binds each new key = command.id and its own same-recovery HUMAN attempt atomically; historical rows can keep an older value on update. No unique index is placed on command.followUpClaimKey because historical released owners may share an old request key. The globally unique active attempt key and immutable command/attempt binding remain.

Examples: Shop A and B may both submit `idempotencyKey: "send-1"`; their new command IDs and stored claim keys differ. An older cancelled command retains its old key and cannot release a later owner. This is a Database-owned persisted contract, not a new shared hash/codec or a provider-facing key. No Shared implementation/publication task is necessary.

### ADR-03 — Upload intent and original-intake identity

**New chosen persistence contract:** `MerchantKnowledgeUploadedAsset.intentPurposeKey String? @db.VarChar(64)`, nullable storage with no default or new policy CHECK/trigger. API-005 enforces nonblank canonical purpose, unchanged retry metadata and application immutability. Updated Woo intent creation always persists the canonical requested purpose key and compares it on retry together with the existing format/file/hash/size metadata. The deterministic Shop/request-key asset ID and object key do not change.

Historical unbound pending assets remain null: retries/finalisation cannot silently bind a purpose; reject with the existing safe upload-conflict contract and require a new intent/key. They expire through existing cleanup. Completed assets and revision history remain usable; their replay is accepted only where original-intake evidence proves binding. No inferred backfill, object deletion or storage reset is authorised.

At most one original intake revision may reference an asset: partial uniqueness on uploadedAssetId for CREATE/FILE_REPLACE. REPROCESS and ENTITLEMENT_CHANGE can create further revisions. Completed finalisation replay returns the original intake's source/revision/generation, not the latest arbitrary reference. Duplicate original-intake history blocks the migration for architect review rather than being deleted.

Finalisation takes an asset FOR NO KEY UPDATE lock shared with cleanup's conflicting FOR UPDATE (and compatible with revision FK KEY SHARE), then any replacement-source FOR UPDATE, revalidates pending/expiry/metadata/purpose/MIME after waits, and holds that protection through AVAILABLE + revision insertion. R2 verification remains between transactions. Cleanup-wins means reject without resurrection; finalisation-wins means cleanup sees the durable reference and skips deletion.

### ADR-04 — Current installed principal at new mutation admission

Adopt the report's recommended financial policy: new create/cancel/switch/purchase intents require current installation identity, active/unrevoked state and authenticated version inside the first transaction. ARCH-055-API-001 owns one transaction-only `requireCurrentWooMutationPrincipal(tx, principal)` helper; ARCH-055-API-007 consumes it. The helper locks Shop then installation, validates platform/domain/canonical URL and returns safe transaction-local fields. It is not used for suspended-Shop Support reads, unauthenticated connection proof or provider outcome reconciliation.

Once an intent is committed, later rotation does not erase valid provider outcome evidence. Provider credentials remain resolved before NEW intent persistence; replay availability during configuration outage is not redesigned. Extra correct authorization work is counted separately from efficiency savings.

### ADR-05 — Deliberate read consistency, not blanket transactions

Category GET uses one short RepeatableRead transaction for principal/catalogue/profile/configuration. Support GET keeps its current principal share-lock checks and ReadCommitted transaction, with a single parameterised support-data statement for page plus total/unread including the empty-page aggregate. These are fixed implementation choices, not alternatives for the executor to select. Recovery summary consolidation yields a statement snapshot. Recovery-selection GET is a committed status snapshot with revision, not send permission; remove recipient write-style locks but retain principal/Shop coordination. Mutation/final-send gates still revalidate.

Existing billing/accounting/count-page/settings snapshots remain. Knowledge GET remains explicitly best-effort without one pinned transaction. Restore keeps its deliberately later eligibility read. Feature PUT keeps its existing revision/eligibility logic and final reload; batching/reload removal needs measured equivalence and explicit Admin-change evidence, not an implied new consistency policy. Read-only share-lock changes not explicitly selected are measure/decide items, not default removals.

### ADR-06 — Configuration reads participate in their transaction

ARCH-055-API-004 makes the existing configuration reader accept the supplied transaction's read-only `platformConfiguration` port. The same Shared crypto/keyring, validation, environment and logger code is reused. Follow-up transaction code must not await a root-client query requiring another pool connection. No positive secret cache, duplicate crypto or extra lookup on text/replay branches is introduced. Unexpected configuration failure remains fail-closed but is not silently classified as an ordinary empty catalogue.

### ADR-07 — Bound work without changing business evidence

Use create/update returned rows, exact-one conditional mutations, zero-count short circuits, one count/sum aggregate, lookahead plus bounded existence, candidate locale filters and changed-row differences. Keep conditional-update loser rereads, later eligibility checks, overflow sentinels, current quote/fingerprint checks and immutable accounting/moderation evidence.

Source targets are examples, not aggregate performance claims: first message page 8 -> 6 calls; related first page 7 -> 5; adjacent order swap among 100 sources 200 -> 4 row writes; one-of-50 coupon replacement 100 -> 2 flag assignments. Record actual SQL, bytes/rows and correctness separately. Optional batching, upsert-result reuse, first-batch coupon sizing, store-context no-op suppression, mark-read update-first and index proposals require measurements. Retain current behaviour with recorded evidence where trade-offs do not justify change.

### ADR-08 — Bound actual readiness work

Keep zero-database liveness and parameter-free SELECT 1 readiness with its existing 2,000 ms HTTP deadline. At most one underlying readiness probe per process may remain unresolved; coalesce request observers but never treat an old success as fresh readiness. The underlying acquisition/execution must have a supported, measured finite bound and recover after database recovery. API-009 uses a dedicated readiness-only Prisma6 client with connection_limit=1, pool_timeout=1, connect_timeout=1 and socket_timeout=1 (seconds), preserving all other connection/TLS settings; business client URL is unchanged. Keep the observer deadline at 2000ms and one underlying in-flight promise until actual settlement. Disconnect clients on shutdown, never per-readiness failure. The dedicated client probes connectivity, not spare capacity in the business pool. An unavailable infrastructure capability is a specific architect escalation, not permission to guess deployed settings or add a Gateway task speculatively.

## Request/event flows

```text
New human follow-up:
  authenticate -> replay check -> generate command ID/internal key
  -> transaction(claim sequence two + command including persisted key)
  -> Background(prepared moderation + persisted-key fences + send/release)

Uploaded file:
  immutable intent incl. purpose -> external upload
  -> preliminary check -> external HEAD/GET/hash
  -> transaction(asset lock + fresh eligibility + original intake)
  -> existing Background revision/cleanup workflows

Financial command:
  resolve credentials -> transaction(current principal + intent)
  -> external provider -> transaction(guarded durable outcome)
  -> verified reconciliation; no early credits or paid activation
```

## Consistency, transactions, ordering and failure handling

Preserve existing Shop/installation/Subscription, Shop/Conversation/command/attempt and source/asset coordination where each applies. A Shop lock is not a substitute for a competing worker's source/asset lock. Use deterministic barriers with actual competitors to verify lock ordering and deadlock/serialization handling. Do not globally serialize tenants.

New current-principal helper lock order is Shop FOR UPDATE -> installation FOR SHARE, before the Subscription lock in financial admission. Knowledge finalisation uses Shop/installation -> asset FOR NO KEY UPDATE -> replacement source FOR UPDATE. Revision FK KEY SHARE on an asset remains compatible with NO KEY UPDATE, so a Background source-locked revision writer is not made to wait on an incompatible asset-key lock; test that actual schedule. Cleanup still conflicts on its asset FOR UPDATE; no provider call occurs while either is held. Retrying a serialization conflict reruns authoritative transaction checks without changing a request's original expected revision/quote/identity. Unknown provider outcomes remain unknown; a timeout is not proof that a write did not occur.

Preserve original errors with shared structured logging. Internal codes supplement the actual provider/Prisma exception and safe response metadata, never replace them. Expected races and unexpected infrastructure/constraint failures are distinguished. Logging failure cannot change a committed outcome. No secrets, capabilities, full webhook/customer bodies or connection URLs in logs.

## Data model and schema ownership

ARCH-055-DATABASE-001 owns exactly the two nullable fields, historical claim-key backfill, original-intake partial unique index and one existing attempt-function/time-CHECK correction. No new command-claim policy trigger or upload-purpose immutability/nonblank trigger is created. It specifies three complete forward migration scripts plus exact Prisma/package/test edits. Old migration files are read-only. The historical backfill temporarily disables only the existing command guard under an exclusive table lock within one transaction, re-enabling it before commit; this is required for active CLAIMED rows and is failure-injection tested. No other trigger bypass is authorised. Existing global claim uniqueness, one-ACTIVE revision uniqueness, generation uniqueness, foreign keys, billing and prepared-content constraints remain.

No new indexes are selected for performance in this initiative at definition time. API owners collect plans for latest attempt, intent expiry, history, search and coupon cases. Duplicate-index removal and any new index are explicitly held for architect approval after evidence, rather than being silently bundled into the safety migration.

## Security

Shop-scoped customer/phone identity remains scoped per merchant. STOP remains authoritative with the existing merchant-specific/global routing rules. No private PostgreSQL/Redis credentials reach Woo plugin/browser code. All new persistence fields are internal. Public retry keys are untrusted request metadata, not globally unique ownership evidence. Tenant checks are never removed to meet a target call count.

## Observability and capacity

Use the installed Shared logging and approved Prisma/framework instrumentation. Do not add generic renamed request/SQL metrics or competing redaction. Feature timing phases must identify initial versus final lookup rather than overwrite. Preserve original source errors in every touched family. Conditional post-commit web-knowledge projection failure is logged separately from mutation commit success.

Woo route mix, burst load, live pool settings and production p50/p95/p99 are UNKNOWN. The Shopify 20,000-event/minute planning reference is not a Woo HTTP workload. Every performance experiment states its fixtures, route/branch mix, changed-row cardinality, concurrency, warm-up and sample size. Client-call targets are not production latency targets.

## Validation and acceptance

Each functional task owns its source tests and migrated PostgreSQL regressions. Source-supported risks must have a reproducing before-state/barrier schedule and a passing correction. Existing Docker pg17+pgvector runners are reused; absent capabilities are explicitly implemented in the named owner task. ARCH-055-API-009 owns final package.json integration wiring and includes the previously omitted AI-delay suite. System-test is terminal, after all code/schema/producers/consumer acceptance and optional developer manual validation.

Required evidence includes exact commands, canonical migration hashes, before/after SQL and affected rows, relevant latency/pool/lock measurements, redacted original failures, rollback, fresh/upgrade migration behaviour and disposable resource cleanup. No check may be reported as run merely because a prior task report or review model says it passed. Do not claim live payment/refund certification from emulators.

## Rollout / migration

Classification: **pre-production, coordinated schema-and-code rollout with explicit durable-data preservation**. This uses the user's established pre-release context; it is not permission to reset durable tables, credits, messages, provider outcomes or R2. If the real environment has a production-compatible rolling-deploy requirement, stop and return that changed premise before migration.

1. Inventory and back up the actual database/storage references; run duplicate-intake and claim backfill preflights. Quiesce new human commands from BOTH Woo and Shopify, pause relevant dispatch/cleanup processing and preserve queued/durable work. Do not delete unknown/dispatched commands to make rollout easier.
2. Apply the accepted ARCH-055-DATABASE-001 migrations. Historical claim key backfill retains its original value; immutable attempt keys and provider evidence stay untouched. Existing unbound pending uploads may require a new intent/key; do not silently bind them.
3. Deploy the accepted Background consumer, Shopify producer and Woo producer using the same accepted nested Database pin while the relevant writes remain quiesced. Start no old producer that can create a new template command with a missing claim key. With no new insert guard, producer deployment gating and fail-closed Background checks are mandatory. No live dual-format fallback is necessary because old commands have explicit backfilled keys.
4. Deploy remaining accepted API corrections and readiness/runtime wiring. Resume paused services only after smoke checks for stored claims, current-principal admission, cleanup coordination and pending-revision/receipt recovery pass.
5. Run developer manual validation and then the terminal system suite. Preserve raw evidence and reconcile status only after acceptance.

Rollback: do not deploy an old producer/consumer against the new persisted command-key consumer contract. Roll back the compatible application set together under quiescence, or roll forward; never strip fields/keys from accepted commands or reverse provider/financial evidence. Database changes are forward-only and data-preserving, including the explicitly named existing CHECK/function correction; historical data remains. No automatic destructive down migration is supplied.

## Infrastructure assessment

No new service, queue, provider integration, public route, Render topology, secret store or infrastructure task is presently required. Readiness now specifies a dedicated one-connection client and its exact Prisma6 pool/socket settings within the API, adding at most one physical connection per process; validate deployment capacity before rollout. A real deployment-only gap must be returned for an explicit Gateway amendment. Do not make infrastructure changes without a defined owner.

## Decisions / Tasks

| Task | Owner | Bounded outcome / touchpoint | Initial state | Depends on |
|---|---|---|---|---|
| `ARCH-055-DATABASE-001` | moda_database | Add explicit persistence metadata and narrowly correct existing guards | ready | — |
| `ARCH-055-BACKGROUND-001` | moda_background | Consume the persisted human follow-up claim identity | pending | `ARCH-055-DATABASE-001` |
| `ARCH-055-SHOPIFY-001` | moda_app | Keep the Shopify producer compatible with shared follow-up dispatch | pending | `ARCH-055-BACKGROUND-001` |
| `ARCH-055-API-001` | moda_api | Harden installation and REST-read authorisation lifecycle | pending | `ARCH-055-DATABASE-001` |
| `ARCH-055-API-002` | moda_api | Streamline consent and recovery ingress without weakening STOP | ready | — |
| `ARCH-055-API-003` | moda_api | Consolidate merchant settings and category projections | ready | — |
| `ARCH-055-API-004` | moda_api | Correct recovery inbox and human-send persistence | pending | `ARCH-055-BACKGROUND-001` |
| `ARCH-055-API-005` | moda_api | Correct knowledge-source and upload lifecycle | pending | `ARCH-055-DATABASE-001` |
| `ARCH-055-API-006` | moda_api | Optimise commercial settings and reporting projections | ready | — |
| `ARCH-055-API-007` | moda_api | Harden durable billing-command admission | pending | `ARCH-055-API-001` |
| `ARCH-055-API-008` | moda_api | Consolidate Support-inbox persistence | ready | — |
| `ARCH-055-API-009` | moda_api | Bound readiness and reconcile API validation entrypoints | pending | `ARCH-055-API-001`, `ARCH-055-API-002`, `ARCH-055-API-003`, `ARCH-055-API-004`, `ARCH-055-API-005`, `ARCH-055-API-006`, `ARCH-055-API-007`, `ARCH-055-API-008` |
| `ARCH-055-SYSTEM-TEST-001` | moda_system_test | Validate the accepted database corrections end to end | pending | `ARCH-055-DATABASE-001`, `ARCH-055-BACKGROUND-001`, `ARCH-055-SHOPIFY-001`, `ARCH-055-API-001`, `ARCH-055-API-002`, `ARCH-055-API-003`, `ARCH-055-API-004`, `ARCH-055-API-005`, `ARCH-055-API-006`, `ARCH-055-API-007`, `ARCH-055-API-008`, `ARCH-055-API-009` |

All task IDs in `depends_on` are fully qualified in the task files. ARCH-055-API-001/004/005 need the new persistence contracts; producer tasks wait for the accepted Background consumer; ARCH-055-API-007 waits for the reviewed principal helper. Other functional API units do not wait unnecessarily for those changes. ARCH-055-API-009 waits for the eight functional units to avoid conflicting aggregate-runner rewrites. ARCH-055-SYSTEM-TEST-001 explicitly depends on all twelve implementation tasks; no dependency points from implementation to system test.

Initial independent Ready definitions: ARCH-055-DATABASE-001, ARCH-055-API-002, ARCH-055-API-003, ARCH-055-API-006 and ARCH-055-API-008. The remaining eight are Pending. Ready does not mean claimed or materialised. After a dependency becomes Complete, the architect promotes its eligible dependants; repository agents do not self-promote.

## File ownership and merge hotspots

- ARCH-055-API-001 owns the new current-mutation-principal helper and Free activation/materialisation helper changes. ARCH-055-API-007 consumes them after acceptance.
- ARCH-055-API-004 owns transaction-aware platform-configuration composition; other tasks retain normal root reads outside transactions.
- ARCH-055-API-008 owns Support's installation helper; ARCH-055-API-002 treats it as a read-only dependency and retains its semantics.
- ARCH-055-API-001 creates an installation-only canonical runner; API-003 creates a separate canonical settings runner with bootstrap/context/category fixtures. API-009 redirects the old aggregate db-push harness only after both owners are accepted. Neither early task removes another family's tests.
- ARCH-055-API-006 registers presentation/history cases in the billing runner; ARCH-055-API-007 registers command cases. No task replaces the complete runner from a stale copy.
- Only ARCH-055-DATABASE-001 edits the canonical schema/migrations; consumers update their own accepted nested pins, not schema copies. Source/model evidence must record the resulting pin.
- No implementation task edits parent architecture, other task reports, indexes or parent gitlinks. New task definitions/rollup state are architect-owned.

## Coverage and measure-first decisions

`endpoint-task-map.csv` has exactly 61 rows and one primary API task per route. `finding-task-map.json` maps every stable finding heading extracted from the detailed ledger to its owning task(s). Cross-repository and shared diagnostic findings are governed by the ADRs and family requirements even where the old review did not assign a separate stable finding ID.

Eight routes are retained/regressed as primary decisions (E02, E14, E21, E25, E32, E51, E59, E60); an error-cause or validation correction in their owner task does not require an invented query rewrite. Measure-first candidates are named in the map and tasks. Index DDL and optional read-lock removal are not automatically authorised by this plan.

## Open questions / bounded stop rules

There are no unresolved cross-service contract choices that a repository agent is expected to invent: ADR-01..08 provide them. MEASURE-FIRST items return evidence with baseline behaviour retained; a source change to those alternatives needs an architect scope amendment. Runtime evidence can block a selected implementation, not silently change its contract. Unknown live ARCH-ID collision, production rollout requirements, duplicate original-intake rows, unsupported readiness cancellation/timeouts, undocumented provider error shape, or a proposed new index/Shared primitive must return to the architect as a concrete blocker/amendment, not silently expand scope.

Architecture can become Implemented only when all thirteen tasks are Complete with accepted evidence, rollout constraints are reconciled and final index/navigation reconciliation is explicitly requested. This package deliberately does not change any `_index.md`.

## Change History

- 2026-11-02: Defined ARCH-055 from the completed Woo hosted-API database review. Consolidated 61 reviewed routes into nine API task families plus four repository/validation boundaries. Added the narrowly necessary Shopify producer based on actual shared-dispatch source inspection. Froze data-preserving claim/purpose contracts and admission/readiness policies. No implementation or task acceptance performed.

## Deterministic task-definition contract — revision 2

Read `docs/architecture/ARCH-055/task-definition-contract.md`. Every task now includes an exact file/operation map and named regression outcomes. `deterministic-execution-map.json` inventories those changes; task files remain the canonical execution instruction. New files/scripts are labelled as deliverables, not claims about the baseline. No additional implementation tasks were created; count stays13 and endpoint primary ownership stays61.

The attached ARCH-053-DATABASE-001 example is the style reference, not a scope or historical-acceptance source for this initiative. Its exact insertion/expected SQL, package entries, fresh/upgrade harness, legacy-value preservation, explicit exclusions and forward-only migration discipline are applied here.

All persistence changes use new versioned forward `migration.sql` files. No old migration edits, destructive automatic down steps, schema resets or hidden history repair. If any previous ARCH-055 migration was already applied, stop for a new forward reconciliation plan rather than reuse its name/checksum. This definition revision does not rewrite deployed schema.

- 2026-11-02 revision2: Narrowed Database to storage/structural integrity/existing guard correction; moved new workflow validation explicitly into service tasks; added exact Prisma/SQL/package edits and F/U cases; fixed active-CLAIMED backfill and expired-FAILED CHECK details; selected deterministic category/Support/readiness contracts and isolated canonical test runners. Definition only; no implementation claims.

## Definition revision 3 — acceptance clarification only

The existing API before/after evidence requirement now uses the fixed protocol/profiles in `docs/architecture/ARCH-055/task-definition-contract.md` for API-001 through API-009. API-001 and API-007 pin public mappings for the new current-principal gate; API-003 pins the source-preserving C03 Admin-mapping interleaving. The task files and execution map carry those exact outcomes. No new product policy, implementation task, dependency, source edit, schema field or migration SQL is introduced. All other revision-2 choices, evidence-only restrictions and the forward-only migration contract remain unchanged. Definition revision is not an execution attempt or acceptance.


## Current execution frontier — 3 November 2026

DATABASE-001 is Accepted and Complete at Attempt 2 (`5907b4572ea9efc2a24c07e4c3bd3e107db4260b`). BACKGROUND-001, API-001 and API-005 are now Ready, Attempt 0, unclaimed; SYSTEM-TEST-001 remains Pending on the remaining implementation work. This supersedes their initial-state table entries without changing unrelated task statuses. Database acceptance includes the two narrowly authorized ARCH-040 validator compatibility amendments. Initial definition manifests remain historical; individual canonical task records are authoritative. No production rollout or architecture-wide completion is claimed.
