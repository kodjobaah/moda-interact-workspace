# Billing, scheduled work and ARCH-055 schema impact — updated snapshot

## Conclusion

**The reviewed ARCH-055 claim-identity change is consistent across new producers, Background command loading/replay, final provider admission, and cancellation/release. No new claim-owner mismatch was found at those boundaries. All seven earlier BS findings remain open at their previous classifications.** Their principal Background implementations and scheduler wiring are byte-identical between snapshots; the new upload identity and uniqueness changes do not repair their separate liveness, cleanup, amplification, billing-lineage or batching concerns.

There is a concrete **snapshot integration gap**: API source now uses both new Prisma fields, but the API nested database schema and migration tree remain the previous versions. Its normal build and typecheck regenerate from that nested schema. This needs reconciliation before treating the archive as a reproducible integrated build. This conclusion concerns the uploaded files, not a deployed database, live application, real Git checkout, or previously recorded task-worktree test run.

## Scope and evidence standard

Snapshot names: `moda-interact-workspace(20261102-112817).zip` and `moda-interact-workspace(20261103-212722).zip`. Source references below are relative to the **updated** root; `BG` means `moda-interact-background`, `DB` means `moda-interact-database`, `API` means `moda-interact-api`, and `SHOPIFY` means `moda-interact`.

This is a static, read-only delta review. Application source, migrations and dependencies are unchanged by this review; the delivery adds review/evidence documentation. No tests, live PostgreSQL/Redis/provider operations, credentials, EXPLAIN plans, timing traces, build or Prisma generation were run. Local Python reads compared bytes, SHA-256 hashes and migration-file sets. Every numeric call count below describes explicit application DB client invocations on the stated branch, excluding transaction BEGIN/COMMIT, DB triggers, implicit ORM relation queries, retries and network work. It is not an executed SQL-statement count.

Substantial updated review: the three ARCH-055 forward migrations and affected schema models; new command ownership through API/Shopify producers, Background command loader/dispatcher/replay/final send fence/cancellation/repair; follow-up billing identity; new database and Background tests; upload intent/finalization's use of the new field and intake index; the ARCH-054 scalar inbound-version addition to the shared send fences. Full AI-delay and pending-turn repair findings appear in the messaging appendix; Woo gate/no-offer findings appear in the checkout appendix. No end-to-end re-proof of unrelated billing, purchased/promotional/refund, translation-provider or catalogue behaviour is claimed.

Read relevant task definitions and review context from ARCH-055 DATABASE-001, BACKGROUND-001, API-004, API-005 and SHOPIFY-001; ARCH-054 BACKGROUND-002; and ARCH-052 BACKGROUND-009. These explain intended boundaries, but source bytes establish the findings. API-004 still has `status: ready`, `attempt: 0` in its task front matter; other reviewed ARCH-055 tasks record completion/reviews. Those records do not prove the supplied source archive is an integrated validated build or that deployment occurred.

## 1. Schema and migration parity

### Exact schema bytes

| Location | Bytes | Models | SHA-256 | Comparison with current canonical DB |
|---|---:|---:|---|---|
| `DB/prisma/schema.prisma` | 191864 | 130 | `5c68e467f392cafe2e6b5be730b81e000a3590e31567135c4037791bcfe11052` | Canonical |
| `BG/database/prisma/schema.prisma` | 191864 | 130 | `5c68e467f392cafe2e6b5be730b81e000a3590e31567135c4037791bcfe11052` | Identical bytes |
| `SHOPIFY/database/prisma/schema.prisma` | 191864 | 130 | `5c68e467f392cafe2e6b5be730b81e000a3590e31567135c4037791bcfe11052` | Identical bytes |
| `moda-interact-admin/database/prisma/schema.prisma` | 191864 | 130 | `5c68e467f392cafe2e6b5be730b81e000a3590e31567135c4037791bcfe11052` | Identical bytes |
| `API/database/prisma/schema.prisma` | 191707 | 130 | `45df5e44bdc1e7e29495e391a1754477f0df362c667d648f4b6893b6541f5c0d` | Still old canonical schema |
| `moda-interact-commerce/database/prisma/schema.prisma` | 191485 | 130 | `9d1041441f53cabbeee9083787ab7b3aff076c744282724b8fc5e2766f184edf` | Earlier pre-existing divergence |
| `moda-interact-mcp/database/prisma/schema.prisma` | 161588 | 117 | `220e0d9e6e7960a3e89264998a776911b5dd442f839ec5618063724d49c32ae2` | Earlier pre-existing divergence |

Current canonical, Background, Shopify and Admin migration trees contain **72 regular files: 71 migration.sql files and migration_lock.toml**. All 72 are byte-identical across those four copies. API has 69 regular files, lacking exactly the three ARCH-055 additions. Commerce has 67, lacking those three plus `20261031110000_arch016_remove_recovery_lifetime_check` and `20261031170000_arch054_merchant_ai_response_delay`. MCP has 53, with 19 canonical files absent. Every migration-tree file shared with canonical has identical bytes; no extra or changed common file was found in those nested trees. Commerce/MCP divergence already existed in the old snapshot and was not introduced by this update.

All **69 previous canonical migration-tree files retain their exact bytes** in the updated canonical tree. The forward additions are:

| Migration | Bytes | SHA-256 |
|---|---:|---|
| `20261102120000_arch055_rest_read_lifecycle/migration.sql` | 3465 | `c129466fdb53190b7f8ce6c2d3a04867c6bacbd55e334c5e0bceeb1b28e4e53b` |
| `20261102121000_arch055_human_follow_up_claim_identity/migration.sql` | 1263 | `e4689790fbba7f606803b2d0370a66ba8b4f57bb3cb0b67b154336f90c2d41fb` |
| `20261102122000_arch055_upload_intake_identity/migration.sql` | 975 | `e9ce08d49576f84a4e1b95c39637c69e97f0f620b4fae608fadf2712fefb6a37` |

### API integration gap and practical consequence

`API/package.json:12,14,19` makes build/typecheck run `prisma:generate`, whose schema argument is `database/prisma/schema.prisma`. This nested file lacks the new fields. Yet:

- `API/src/merchant/conversations/messages/admission.service.ts:186–195` supplies `followUpClaimKey` to the typed Prisma command create.
- `API/src/merchant/merchant-knowledge/upload.service.ts:149–172` reads/compares/writes `intentPurposeKey`; lines 193–197 explicitly select it, with further checks at 207–211 and 244–251.

A client generated from the included API schema does not define these fields. Standard typed build/client validation therefore has a concrete schema/source mismatch. A locally retained client generated from another schema could conceal it, but no such client or successful build is inferred here. The existing ARCH-047 canonical-schema helper is not the normal `prisma:generate` script; it also prioritises API's own schema when its older ARCH-047 conditions are satisfied (`API/scripts/arch047-canonical-schema.mjs:104–131`). It does not resolve this new-field mismatch by itself.

Recommended disposition: reconcile the API's accepted database dependency and regenerate its client using the intended normal build path, then repeat the relevant API integration tests. Do not hand-edit a consumer schema or claim a database migration was deployed based on source presence. API-005's recorded accepted dependency/test evidence refers to its historical worktree; the uploaded nested bytes must be reconciled independently.

## 2. What the migrations change, and what they preserve

### REST authorization failure terminalization

`DB/prisma/migrations/20261102120000_arch055_rest_read_lifecycle/migration.sql:3–11` permits a FAILED attempt's terminal timestamp after expiry while retaining `consumedAt >= createdAt`. The replacement trigger retains identity immutability and single-use checks before its new FAILED branch (22–40). That branch requires a timestamp, records the current transaction ID, and returns before active-installation/current-generation checks. Consequently an already expired or credential-rotated pending attempt can be durably failed without being treated as a successful bearer consumption.

The success path still requires an unexpired timestamp (42–48), active Woo installation and matching credential generation (54–68). The historical lifecycle CHECK still requires FAILED attempts to have nonblank failureCode and consumption transaction ID; the grant guard still requires SUCCEEDED state, matching identity/generation and the same consumption transaction; and the deferred success guard still requires a corresponding grant in the same transaction. See unchanged `20261010120000_arch026_woocommerce_rest_read_grant/migration.sql:41–48,186–209,268–281`.

This is a narrow correctness improvement, not a relaxation permitting failed attempts to mint grants. Failure terminalization now avoids the trigger's installation/shop share-lock query; successful consumption retains it. Application-side query count alone does not capture such trigger work.

### Persisted human follow-up claim identity

The schema change is only nullable `followUpClaimKey String? @db.VarChar(255)` at `DB/prisma/schema.prisma:601`. The migration takes ACCESS EXCLUSIVE on the command table, verifies the expected command trigger is enabled, adds the column, disables **only** that guard for the historical backfill, then reenables it in the same explicit transaction (`20261102121000.../migration.sql:3–33`). Every historical template command gets its own `idempotencyKey`, across all lifecycle states; HUMAN_TEXT remains NULL. It does not read an attempt's current initiation key or rewrite attempt ownership. This matters after a cancelled command's attempt was reclaimed by another command.

The existing globally unique nullable `RecoveryOutreachAttempt.initiationKey` remains (`schema.prisma:439`; original handover migration:52–62). NULL permits an unclaimed attempt; the old CHECK requires a nonblank key, initiator and claimedAt together when claimed. Command public replay uniqueness remains `(shopId,idempotencyKey)` (`schema.prisma:634`). The new `followUpClaimKey` itself is deliberately neither globally unique nor NOT NULL and has no new immutability/blank CHECK; ARCH-055 DATABASE-001 explicitly delegates workflow enforcement to applications rather than adding a policy trigger. It must not be described as database-enforced immutable metadata. No reviewed runtime path edits it after insertion, and Background now rejects missing/blank template values.

The exclusive table lock and full historical UPDATE are one-time migration work, not a recurring query optimization. The migration comments require quiescing relevant producers/consumers. That remains a real rollout prerequisite: a legacy producer allowed to insert template commands after backfill could still insert NULL into this nullable column, and the new consumer would hold those claims. Upgrade ordering and completion cannot be certified from this archive.

### Upload identity and original-intake uniqueness

Nullable `intentPurposeKey VARCHAR(64)` is added at `schema.prisma:4191`, without default/backfill. The third migration locks source revisions, checks for duplicate nonnull uploaded assets with reason CREATE/FILE_REPLACE, aborts with 23505 if any exist, and adds a partial unique index over exactly that predicate (`20261102122000.../migration.sql:3–28`). The index applies regardless of revision status, preventing a second original intake of the same asset even after a failure; REPROCESS, ENTITLEMENT_CHANGE and NULL-asset web revisions remain outside the uniqueness predicate. The preflight and index are in one transaction; no historical deduplication or deletion is attempted.

The partial unique index is migration-owned rather than a blanket Prisma `@@unique([uploadedAssetId])`. A blanket unique would incorrectly reject legitimate reprocessing. No new pending-repair index or object-deletion acknowledgement exists. API's new purpose checks and `originalIntakeReplay` improve command identity: AVAILABLE historical assets may replay through their original intake while new pending finalization requires the persisted purpose (`upload.service.ts:205–211,244–251`). R2 verification remains outside the final transaction (224–228), and finalization locks/revalidates the asset before source/revision writes (230–289). These changes do not alter the Background cleanup predicate or its repeating DELETED work.

## 3. ARCH-055 ownership through the application boundaries

| Boundary | Source evidence | Disposition |
|---|---|---|
| New Woo command admission | `API/src/merchant/conversations/messages/admission.service.ts:98–105,138–153,173–195` | Public replay occurs first. Fresh command UUID becomes both attempt initiationKey and command followUpClaimKey in the same transaction. Public request key remains separate. Runtime integration still needs the API schema correction above. |
| New Shopify command admission | `SHOPIFY/app/services/recoveries/recovery-human-commands.server.ts:183–194,253–274` | Same distinction: replay existing command, generate UUID only for a new command, claim attempt and persist command together. HUMAN_TEXT stores NULL. |
| Claimed command load | `BG/src/services/recovery-conversation/merchant-send-command.service.ts:61–79` | Lease/provider checks precede key validation; missing/blank template key raises typed integrity error before context evaluation. Stored value is carried verbatim; no fallback to request/public key/command ID for historical rows. |
| Dispatcher and restart | `human-command-dispatcher.service.ts:202–228,509–531` | Loads/validates key before evaluator/cancellation, passes exact key to claimSequenceTwo, and on already-claimed replay queries the same persisted owner. Final returned attempt must equal the command's immutable FK. |
| Final provider fence | `outbound-send-fence.service.ts:103–154` | Locked command select includes persisted key. Missing/blank key logs typed error and suppresses; attempt is locked and must be HUMAN/PENDING, match key, and have no outbound/sent evidence. |
| Cancellation/release | `follow-up-claim-cancellation.service.ts:141–175,196–232` | Under Shop → Conversation → Command → Attempt locks, validates exact key and provider evidence. Durable command cancellation precedes credit release; conditional attempt reset retains expected attempt, recovery, sequence, HUMAN owner, key and unsent predicates. |
| Repair | `follow-up-claim-cancellation.service.ts:71–92,101–124` | Bounded LIMIT 25 scan joins the command's attempt FK and persisted owner. Provisional credit release is outside first transaction; second transaction rechecks durable credit/ownership before reset. Missing/blank keys are excluded, deliberately requiring integrity repair rather than an unsafe guessed owner. |

The relevant source satisfies the intended key separation: distinct shops may use the same public request idempotency key while each fresh attempt gets a different internal identity. Historical cancellation cannot borrow a newly reclaimed attempt's identity. The new key does **not** change the billing idempotency namespace: billing remains tied to the shared outreach attempt (`recovery-follow-up-billing.service.ts:79,147–149`). This preserves accounting across cancellation/reclaim but also means BS-05's older reservation-lineage issue is unaffected.

The exception path is deliberately conservative. Dispatcher catches only `FollowUpClaimKeyIntegrityError` and sends it into the terminal cancellation path (`human-command-dispatcher.service.ts:207–212,496–505`). Cancellation records the typed original error, cancels the command under lease, and holds the attempt/credit because ownerMatches is false (`follow-up-claim-cancellation.service.ts:162–175,196–218`). It does not manufacture a replacement key or release a different owner's reservation. This is a diagnostic/manual-integrity-repair state, not a promise of automatic repair by the normal key-matching scan.

### Query costs in the changed flow

- Valid `loadClaimedCommand` uses two explicit reads: command plus recovery context. Invalid lease or missing/blank template key uses one. The new integrity check itself adds no query.
- `claimDueHumanCommands` is a bounded transaction with **1 + N** explicit DB calls for a positive bounded limit with N selected commands (0 ≤ N ≤ 100), comprising one SKIP LOCKED SELECT and N individual UPDATE/RETURNING calls (`merchant-send-command.service.ts:33–57`); an effective zero limit returns with no query. The existing comment describing a single claiming statement is not an accurate invocation count. This loop predates ARCH-055; it is a bounded optimization candidate, not a new correctness regression.
- The successful dispatcher still loads command/context twice: directly at line206 and inside `HumanCommandEvaluationService.evaluateHumanCommand` at line20. Previously these calls occurred in the opposite order. On an allowed path, the delta adds no DB call; early denial costs differ with the reordered short circuit. Those adjacent preflight reads are a potential consolidation candidate, but final locked revalidation must remain.
- A fully valid `lockRecoveryContext` performs four explicit calls: initial joined context, Shop lock, Conversation lock, refreshed joined context (`recovery-conversation.sql.ts:55–67`). The new inboundVersion is added to an existing projection, not fetched separately.
- The normal preclaimed HUMAN follow-up replay reaches the existing `claimSequenceTwo` already-claimed branch after eight explicit calls in that transaction (root, four context/lock calls, window evidence, insert-on-conflict, attempt read), then one outside replay lookup: **nine total** for this named claim/replay portion only (`recovery-follow-up-policy.service.ts:85–144`; dispatcher:522–526). Neither earlier moderation nor billing nor later permit work is included.
- For valid-owner cancellation with an existing attempt, no provider evidence and no reservation/usage, the direct successful `cancelClaimed` path uses **12 explicit calls**: pointer1 + lock/context4 + command1 + attempt1 + provider-evidence1 + billing-inspection2 + cancel1 + reset1. The original claim/billing checks are preserved. If an existing RESERVED credit must be released, source-owned release plus a second transaction adds branch-dependent calls; no blanket count is asserted.
- The ARCH-054 general fence reads inboundVersion in its existing locked Conversation query and can reject a stale input before message work (`general-outbound-send-fence.service.ts:29–38`). Recovery's fence compares the refreshed version before persisting dispatch (`outbound-send-fence.service.ts:228–230`). These scalar guards add no client invocation. Full processor propagation is assessed in the messaging appendix.

These counts are descriptions, not a recommendation to remove safety checks. Consolidate reads only where the same immutable context/decision time is truly shared. Rechecks after moderation, provider preparation, billing admission or lock waits protect against changed state.

## 4. Previous BS findings — every disposition

| Prior finding | Updated disposition | Classification retained | Principal evidence |
|---|---|---|---|
| BS-01 Pending knowledge prefix starvation | **Open; unchanged** | Statically demonstrated liveness gap | `merchant-knowledge-reconciliation.service.ts:45–75`; minute/page100 wiring unchanged |
| BS-02 Repeated DELETED upload cleanup | **Open; unchanged** | Confirmed repeated work and unbounded cycle; scale cost unmeasured | `merchant-knowledge-upload-cleanup.service.ts:40–49,60–157`; no acknowledgement field |
| BS-03 Per-source entitlement amplification | **Open; unchanged** | Confirmed repeated reads/O(S²) transferred ID rows; optimization candidate | `merchant-knowledge-entitlement-reconciliation.service.ts:138–160,197–249`; eligibility:124–180 |
| BS-04 Duplicate paid meter read | **Open; unchanged** | Exact redundant client read in the same transaction | `paid-included-recovery-reservation.service.ts:307–316,348,509–517` |
| BS-05 Ambiguous historical compensation source | **Open; unchanged** | Conditional correctness risk; live occurrence and regression reproduction unproven | `recovery-delivery-compensation/lineage.ts:85–96`; paid revalidation:255–272 |
| BS-06 Global billing reconstruction | **Open; unchanged** | Confirmed unbounded selection/publication; scale impact unmeasured | `billing-subscription-reconciliation/reconciliation-queue.service.ts:45–119`; billing entrypoint:241–245 |
| BS-07 Serial item/catalogue/chunk writes | **Open; unchanged** | Confirmed O(N) transaction calls; optimization candidate | Translation assembly:80–147; catalogue loops; knowledge promotion:414–495 |

### BS-01 — Pending merchant-knowledge repair starvation: unchanged, open liveness gap

`BG/src/services/merchant-knowledge-reconciliation.service.ts:45–57` still always selects the oldest PENDING prefix without a cursor; lines63–75 retain dormant/stale rows without advancing selection. A full prefix of 100 retained ineligible rows still hides a later eligible lost-enqueue revision. Wiring remains page size 100/minute (`src/entrypoints/merchant-knowledge.ts:64–74`), and dormant processing intentionally resets to PENDING (`merchant-knowledge-processing.service.ts:160–173,379–399`). The new original-intake index cannot change scan progress. Keep fair bounded traversal or explicit eligibility-aware revisit as the recommendation; retain durable intent.

### BS-02 — Repeated upload tombstone cleanup: unchanged, open repeated-work/unbounded-cycle finding

`merchant-knowledge-upload-cleanup.service.ts:40–49` still selects every DELETED asset; lines60–157 page until exhaustion; lines84–105 lock/count/reread each historical candidate; successful R2 delete at146–150 still records no durable acknowledgement. New `intentPurposeKey` is unrelated metadata, and the asset schema still has no external-deletion completion field (`DB/prisma/schema.prisma:4187–4209`). For D unreferenced DELETED rows successfully deleted, the old named branch remains D transactions with three DB calls each plus ceil(D/100)+1 page reads and D R2 deletes per full sweep. Preserve reference rechecks and tombstone-before-R2 order; add completion state/fair bounded progress only through a separately authorised change. The bare R2 failure catch still loses original diagnostics.

### BS-03 — Merchant-knowledge repeated shop-wide eligibility: unchanged, open optimization candidate

`merchant-knowledge-entitlement-reconciliation.service.ts:138–160,197–249` and `merchant-knowledge-entitlement.service.ts:124–180` are identical. Per-source source/subscription/rank-list reads still repeat shop-wide state, transferring O(S²) source-ID rows for S otherwise eligible sources. The pending page's up to 301 explicit reads for 100 otherwise eligible current revisions is unaffected. API upload-intake identity prevents duplicate originals; it does not batch this Background reconciliation. Recommend shop-scoped pass context plus narrow locked revalidation; do not remove the latter.

### BS-04 — Duplicate paid-commit meter read: unchanged, open exact redundant-read candidate

`paid-included-recovery-reservation.service.ts:307–316,348,509–517` still reads the same subscription plan meter handle twice in the same paid-commit transaction. The prior branch counts remain: fresh RESERVED→COMMITTED Shopify 9 client operations, Woo 8; already-committed replay 1. The bounded reservation/CAS/Serializable checks remain needed. Reusing the already validated handle is still the narrow candidate; new follow-up claim identity does not alter this transaction.

### BS-05 — Compensation historical reservation ambiguity: unchanged, retain conditional correctness-risk classification

`recovery-delivery-compensation/lineage.ts:85–96` still selects exact logical source OR paid-included prefix/suffix matches, LIMIT2, including RELEASED history and without a shop filter in that lookup (tenant equality is checked afterward). Multiple matching historical/current rows still cause refusal. Paid revalidation still releases and readmits the same outreach attempt if the period/policy changed (`recovery-billing.service.ts:255–272`), so the previously described old-period RELEASED + new-period reservation scenario remains a source-level conditional failure path. No production occurrence or runnable database reproduction is claimed.

The ARCH-055 key is **claim ownership**, not a new reservation/event FK. Follow-up billing deliberately retains the same `recovery-outreach:<attemptId>` source across reclaim (`recovery-follow-up-billing.service.ts:79,147–149`). Its own credit inspection also returns unsafe for more than one reservation (80–102), holding a cancelled claim instead of guessing which source to release. Keep exact consumed-reservation lineage as the design question, with a period-transition regression as the next proof. A new key field, a shop predicate, or picking the first row alone does not resolve historical ambiguity.

### BS-06 — Global billing reconstruction each cycle: unchanged, open unbounded-scan/publication candidate

`billing-subscription-reconciliation/reconciliation-queue.service.ts:45–119` still loads all eligible candidates without take/cursor/due horizon and enqueues individually; `src/entrypoints/billing.ts:241–245` still invokes it each cycle. The separately bounded billing reconciliation path does not bound this reconstruction. Retain repair of DB-commit/Redis-publication gaps, but use bounded sweep progress and a justified horizon if this is later changed. No new migration or claim field affects it; scale impact remains unmeasured.

### BS-07 — Serial per-item writes under locks: unchanged, open optimization candidates

`translation-batch-assembly.service.ts:80–147` retains 2+2N explicit transaction calls for N>0 batch items, excluding model lookup. Shopify/Woo catalogue writers still upsert one observed discount/coupon at a time under their catalogue locks (`shopify-discount-catalogue.service.ts:100–126`; `woo-coupon-catalogue.service.ts:72–121,211–229`). Knowledge promotion still inserts chunks one at a time (`merchant-knowledge-processing.service.ts:414–495`), after embedding outside the transaction. New partial intake uniqueness does not conflict with legitimate REPROCESS/ENTITLEMENT_CHANGE revisions, so there is no reason to drop those histories or split atomic promotion. Measure large batch lock duration before prioritising bulk writes.

ARCH-052's merchant-selection invariant remains: Shopify new-row create sets `isAvailable:false`, update omits it, and disappearance/reinstall changes `unavailableAt` rather than clearing merchant choice (`shopify-discount-catalogue.service.ts:110–112,141–142`; `billing-subscription-reconciliation/reinstall-reconciliation.service.ts:103–105`). Any future bulk change must preserve that distinction and generation-complete publication.

## 5. Preserved invariants and limits

Exact old/new byte comparisons confirmed unchanged principal files for: knowledge pending reconciliation, cleanup, entitlement reconciliation/eligibility/processing; paid and free reservations; recovery billing and terminal compensation; billing reconstruction; translation assembly; Shopify/Woo catalogues and Woo dispatcher; brand-media repository; order-recovery correlation; follow-up policy/billing; billing and merchant-knowledge entrypoints (21 files).

Consequently the earlier invariants remain in the inspected source: Serializable reservation transactions and counter CAS; source-owned idempotent accounting; terminal compensation's message lock and lineage/accounting transaction; Woo dispatch's bounded SKIP LOCKED claim and Redis publication after commit; brand-media keyset bounds and per-shop/brand locks; order status/history atomicity. The earlier order `fromStatus` race concern is not resolved by a claim-key schema field and is assessed in the checkout appendix. Existing retry loops and provider-independent accounting are not candidates for wholesale removal merely to reduce call totals.

A source byte match is strong evidence of unchanged implementation, but not proof of unchanged workload: new API producers, data distribution, claim ordering, retained history and deployment configuration can change frequency. We have no measurements of row volume, pool occupancy, lock wait, queue publication load, retries or p95/p99 duration.

## 6. Tests reviewed versus tests run

**Run here:** no tests, typecheck/build, Prisma generate, migration apply, PostgreSQL/Redis/provider calls or live queries. Only local source reads, textual diffs, exact-byte/hash comparisons and file/model counts were performed. Prerequisite inspection found that the declared ARCH-055 validator requires a historical Git baseline and local Prisma binary that the archive does not provide. No synthetic Git baseline or rewritten validator was created to force that gate to pass.

**Reviewed test intent/assertions (not executions):**

- `BG/tests/unit/services/recovery-conversation/arch055-claim-key.test.ts:36–99`: historical key independent of public idempotency; NULL/blank fails at first read; HUMAN_TEXT NULL remains valid; outbound fence preserves typed diagnostic without exposing key values.
- `BG/tests/unit/services/recovery-conversation/follow-up-claim-cancellation.test.ts:104–240`: cancellation before provisional release, source-owner and durable-release rechecks, expired lease/foreign owner/provider evidence rejection, historical stored key, missing/blank held state, original typed error and idempotent repair. Existing tests were inspected selectively, not represented as a new successful run.
- `BG/tests/integration/arch055-follow-up-identity.integration.test.ts:23–140`: stored historical identity after restart, identical public keys across two shops, a Shop-lock barrier for old-worker cancellation/reclaim, and missing-key cancellation with no provider/credit side effect. Its suite requires TEST_DATABASE_URL, REDIS_URL and an explicit disposable-integration flag (6–7). These conditions were not enabled here.
- `DB/scripts/test-arch055-database-contracts-postgres.mjs:88–128`: nullable/no-default column shape, preserved existing catalogue/guard definitions, FAILED terminalization after expiry/rotation while refusing stale success/failed-grant/identity edits, partial original-intake uniqueness without rejecting reprocess/entitlement/null, historical all-state backfill preserving a cancellation/reclaim pair, injected migration rollback restoring guard/data/column state, and duplicate-intake upgrade refusal without history changes. It is a disposable PostgreSQL harness; its PASS print statements are test source, not evidence that we executed it.
- The ARCH-040 human-prepared validator/test compatibility changes were inspected for purpose and registration; full historical invariant gate execution is not certified.

Recommended follow-through is bounded: first reconcile the API nested schema/client build; then run the source-defined migration upgrade/fresh and cross-platform follow-up identity tests in a disposable harness. To close the older BS correctness/liveness concerns, add/run targeted full-dormant-prefix progress, successive successful tombstone-cleanup, and period-change reservation/compensation cases. Performance decisions need realistic cardinality measurements rather than another syntactic count.
