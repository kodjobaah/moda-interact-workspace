# Runtime, inventory and evidence impact

## Exact comparison

The baseline is `moda-interact-workspace(20261102-112817).zip`, SHA-256 `ee42bb83ee441ba9018779e760967a5bf87edcbc429eecc58699f1419863861b`. The updated input is `moda-interact-workspace(20261103-212722).zip`, SHA-256 `f8194947c3564a8f9ea8942d9462ec83716aecc17fc1626d7d846af68c044024`. Comparisons use archive regular-file contents, so documents added by the earlier review are not counted as source changes.

The archive comparison finds 146 added, 315 modified and four removed regular files. Background `src/` contains seven added and 22 modified files, with no removals. The new review is a standalone addition because the prior review directory is absent from the updated archive. It does not require the previous review patch to have been applied.

| Source metric | Previous | Updated | Change |
| --- | ---: | ---: | ---: |
| TypeScript source files | 481 | 488 | +7 |
| TypeScript source lines | 70,139 | 71,324 | +1,185 |
| Worker modules | 25 | 25 | 0 |
| Files containing direct database client sites | 198 | 201 | +3 |
| ORM read sites | 433 | 438 | +5 |
| ORM write sites | 358 | 359 | +1 |
| Raw SQL query/execute sites | 236 | 238 | +2 |
| Explicit transaction-boundary sites | 162 | 162 | 0 |
| Total direct sites, including transaction boundaries | 1,189 | 1,197 | +8 |
| Separately indexed SQL-wrapper invocations | 59 | 59 | 0 |

The same bounded lexical scanner was used for both inputs. These are source locations, not queries per job, executed SQL statements, active production paths or performance measurements. SQL-function internals, relation expansion and Shared package implementation are outside this index. The scanner is not a TypeScript parser or type checker. The 109 excluded non-database candidates are unchanged. Wrapper calls must not be added to their underlying raw implementation sites to estimate database load.

The net eight additional sites arise from four file-level changes:

| File under `moda-interact-background/src/` | Change in direct sites |
| --- | --- |
| `services/conversation-ai-delay/pending-turn-repair.ts` | One new raw SELECT site. |
| `services/conversation-ai-delay/pending-turn-repository.ts` | One read, two mutually exclusive write sites, one raw locking-read site. |
| `services/inbound-whatsapp-audio.service.ts` | Two former inline write sites removed as pending-turn handling moves into the shared helper. |
| `services/recovery-template-integration/initial-no-offer-fallback.service.ts` | Four read sites and one write site. |

Unchanged site counts elsewhere do not mean unchanged behaviour. Existing call arguments, conditions and helper execution paths changed in several services. In particular, helper extraction changes branch execution budgets even where the caller's syntactic count stays the same.

## Schema, migrations and dependencies

Canonical Database and Background's nested Database schema remain byte-identical: 130 models, 191,864 bytes, SHA-256 `5c68e467f392cafe2e6b5be730b81e000a3590e31567135c4037791bcfe11052`. All 72 regular files under their respective migration trees are byte-identical. The schema adds nullable `MerchantConversationSendCommand.followUpClaimKey` and `MerchantKnowledgeUploadedAsset.intentPurposeKey` fields. The three added migrations establish Woo REST-read lifecycle changes, persisted human follow-up claim identity, and original upload-intake uniqueness. This equality verifies snapshot contents; it does not prove deployed migration state or a real submodule pin.

Background's `package-lock.json` is unchanged. Its declared resolved Prisma/client 6.19.3, Shared 3.0.0 and BullMQ 6.3.6 versions remain the baseline facts. No parent, Background or Database Git metadata, installed Background dependencies, or generated Prisma client is available in the archive extraction.

## R1 remains applicable: lease uncertainty and callback overlap

`src/runtime/background-runtime-lease.ts` and `dynamic-leased-scheduler.ts` are byte-identical to the previous input. The renewal timer still uses `.then(success).finally(cleanup)` without a rejection handler at `background-runtime-lease.ts:91`. A resolved false sets `leaseLost`, but a rejected heartbeat does not. Cleanup may clear the retained promise before the callback finishes, so the eventual `await heartbeatInFlight` does not reliably observe an earlier rejected renewal.

Detected ownership loss still does not stop the callback. The dynamic scheduler checks only the skipped result at `dynamic-leased-scheduler.ts:37`; the completed result's `leaseLost` is not acted on. The old owner can therefore continue work after takeover. This remains a static scheduler coordination/error-handling gap, not a reproduced duplicate-send or accounting incident. Domain claims, version predicates and provider fences still matter independently.

The next validation should inject both a rejected renewal and a resolved false while work is blocked, permit another owner to acquire, then inspect the original callback's next effect. A cancellation decision cannot undo a committed effect; retain durable domain ownership checks.

## R2 remains applicable and gains a new recurring scan

Runtime configuration, queue concurrency reconciliation and their lease implementation are unchanged. The approximately `12 × P` periodic configuration reads per minute for `P` worker processes remain cadence arithmetic that excludes query duration and explicit `getFresh()` calls. `current()` remains an in-memory snapshot read. Queue-concurrency reconciliation still has a zero inter-cycle lease cadence and may repeat across staggered replicas. These are measurement candidates; no general cache or central scheduler redesign follows from the static counts alone.

The messaging entrypoint now starts `startProductionPendingTurnRepair(whatsappQueue)` at `src/entrypoints/messaging.ts:21` and registers its closer at line 36. The service schedules a pass 30 seconds after startup and 30 seconds after each preceding pass completes. It prevents overlap within one process and waits for an active pass during shutdown. It does not take the Background runtime lease; ARCH-054 explicitly chooses independent replica discovery, deterministic queue job identities and the processor's database claim predicates.

`services/conversation-ai-delay/pending-turn-repair.ts:189` performs a narrow SELECT of five fields, ordered by `(pendingAiNotBeforeAt, id)`, with pages of 100 and at most 1,000 candidate rows per pass. The cursor persists across passes and wraps after reaching the end. The existing `20261031170000_arch054_merchant_ai_response_delay/migration.sql:12` provides a normal two-column index matching that order. It is not a newly added index and is not partial.

An empty pass performs one SELECT. A pass performs at most ten SELECTs, including any final empty page within the 1,000-candidate ceiling. Each selected candidate also performs Redis/BullMQ job lookup and potentially state lookup, retry or add; these are not PostgreSQL calls. The service uses `runtimeConfig.current()` once per pass, so that access adds no database read.

For `M` messaging processes and negligible pass duration, this adds approximately `2 × M` empty-poll SELECT executions per minute, or up to `20 × M` page SELECT executions per minute when each pass reaches the maximum pages. Processing duration reduces that cadence. These expressions are not a capacity guarantee: a bounded returned page does not bound examined rows or query time, and there is no measured query plan.

The query includes future deadlines so missing delayed jobs can be reconstructed with a nonnegative delay. Already waiting, delayed or active jobs are left intact. Due failed jobs can be retried using the same job identity with attempts reset; competing retry transitions are checked. Replica duplication of discovery work is expected by this architecture and is not evidence of duplicate sends.

Measure the selector under many HUMAN, revision-mismatched or actively leased rows, sustained arrivals, retained failed jobs and several messaging replicas. Preserve the fixed deadline, cross-pass cursor, deterministic ID and execution-time claim/final-send guards when optimising it. Repeatedly resetting an exhausted job's attempts needs an operational policy and error visibility; it is not, by itself, proof of incorrect delivery.

## R3 remains applicable: preserve original diagnostic errors

`services/platform-configuration/service.ts` and `errors.ts` are unchanged. The operation-time `readBundle` remains a narrow uncached key lookup; its catch at line 131 still substitutes `DB_UNAVAILABLE` without retaining the original cause. Readiness still substitutes a generic probe error. The unchanged Woo initial-send SQL fence logs a synthetic `PERSISTENCE_FAILURE` while rethrowing the original. Changes elsewhere to structured error logging do not repair these particular sites.

All six existing production observability preloads remain present. The review therefore continues to recommend using Shared instrumentation and preserving original redacted errors, rather than adding a second generic Prisma telemetry layer.

## Validation boundary

This reassessment inspects source, tests, migrations, archive differences and inventory results. It does not execute the application, integration suites, PostgreSQL, Redis or providers. The new tests supply inspectable coverage intentions and assertions, not results produced in this session. Historical task reports contain their own accepted validation claims, which remain historical claims.

The declared `moda-interact-database/scripts/validate-arch055-database-contracts.mjs` gate requires its recorded historical Git commit `7c377282aa5819b3008b7d7f3018f44f4161523e`, ancestor verification and an installed Prisma binary. Those prerequisites are absent. Creating an artificial Git baseline would not establish this gate; it is not done. The delivery's temporary Git repository is used only for patch construction and applicability/whitespace validation and must not be confused with implementation history.

The patch adds only review and evidence files. Applicability, content equality and whitespace checks are artifact-integrity checks; they do not establish runtime correctness or task acceptance.
