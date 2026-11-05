---
id: ARCH-057-SHOPIFY-005
architecture_id: ARCH-057
title: Simplify support inbox reads and bounded acknowledgements
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-057-SHOPIFY-001
enables:
- ARCH-057-SHOPIFY-011
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-057-SHOPIFY-005: Simplify support inbox reads and bounded acknowledgements

## Architecture

Architecture ID: `ARCH-057`. Architecture document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`. Coordinator: `moda_architect`.

Read the mandatory `docs/architecture/ARCH-057/task-contract.md`, including its latest-snapshot provenance, materialisation, original-error logging and validation requirements. Materialised in the canonical task worktrees on `task/ARCH-057-SHOPIFY-005`; Attempt 1 was claimed by the launcher. The Completion Report records implementation and validation evidence; Attempt 1 was independently accepted on 2026-11-04.

## Objective

Serve the support badge and inbox with only their required reads, acknowledge one bounded rendered page in one atomic database operation, and preserve durable support-message success when translation publication fails.

## Context

Review F07 identifies three support SELECTs for the parent's unread badge, three SELECTs for the inbox, and one complete authenticated POST per unread visible message. The old acknowledgement service also rewrites already-read rows. Message composition performs a thread upsert and a second thread update in the same transaction. These operations share the support inbox lifecycle and belong in one independently reviewable change.

This task consumes SHOPIFY-001's authenticated request context. Its read cache is GET/HEAD only; actions obtain fresh local Shop state. Neither the context nor batching replaces the support lifecycle/tenant predicate.

## Scope

Paths are relative to `moda-interact`. The edit map is exhaustive for production changes.

| Existing path | Required edit |
|---|---|
| `app/services/merchant-support/merchant-support.service.ts` | Add the narrow count and batch-acknowledgement APIs; combine inbox aggregates; combine thread writes; catch queue acquisition and publication failures after commit |
| `app/services/merchant-support/merchant-support-observability.server.ts` | Extend existing Shared-based semantic diagnostics for badge/list/acknowledgement/compose/queue failures, with original safe errors and causes |
| `app/routes/app/route.jsx` | Replace only the full support-page call with the new unread-count API; preserve SHOPIFY-001 middleware/context and all navigation fields |
| `app/routes/app/merchant-support/route.jsx` | Pass framework context, consume `getMerchantRequestContext`, keep independent `assertSupportShop`, accept the bounded batch intent, and issue one batch request from the visible-page effect |
| `tests/unit/merchant-support-service.test.ts` | Assert read/write budgets and unchanged projection/translation/version behaviour |
| `tests/unit/merchant-support-route.test.ts` | Assert request shape, batch validation, already-read success, one explicit refresh and independent support authorization |
| `tests/unit/merchant-support-observability.test.ts` | Assert actual Shared output and failure isolation |
| `tests/unit/merchant-support-recovery-i18n.test.ts` | Retain localized system-message actions and translated-message visibility |
| `package.json` | Add exactly the two scripts below; no dependency changes |

New files:

- `tests/integration/merchant-support.postgres.test.ts`: migrated PostgreSQL ownership, concurrent batch and thread-version proofs.
- `tests/helpers/merchant-support-postgres.ts`: task-local PG17 container/migration/fixture setup, separate clients and cleanup; no generic test framework.
- `tests/unit/merchant-support-batch-ui.test.tsx`: mounted React support-page effect with controlled HTTP responses and the existing router test boundary; verify request/refresh behaviour rather than pixel changes.

Keep each new test/helper file below 300 lines. Do not modify Shared or copied Database files.

## Out of Scope

No new support message kind, translated copy, queue identity, source-key/idempotency redesign for composition, unread-count cache, thread-wide mark-read action, new API service, schema/index migration, support offset-pagination redesign, or Admin/Background implementation. Do not change the current support availability policy for suspended/reinstalling shops. No architecture/task IDs in new runtime names.

## Requirements

### R1 — precise reads

1. Add `readMerchantSupportUnreadCount` as one parameterized raw SELECT using the existing tenant join and exact unread predicate: ADMINISTRATIVE or SYSTEM, AVAILABLE, `readAt IS NULL`. It returns a number and never selects message bodies, translations, related recoveries or total-page counts. The app parent uses that number directly.
2. Retain the existing inbox page query, ordering, LIMIT/OFFSET, translations, system-action linkage and DTO. Replace its two separate count SELECTs with one SELECT containing total visible COUNT and unread filtered COUNT. Keep the existing read transaction; the normal inbox service now makes two raw SELECT calls. No claim of RepeatableRead consistency is added.
3. Use SHOPIFY-001's cached scalar subscription only for the support page's existing read policy. Preserve active-only filtering where the old `getSubscription` returned null. Never return `merchant`, authentication, session or admin objects in loader JSON.

### R2 — one bounded, atomic acknowledgement

4. Add the service/API contracts specified below. The new HTTP intent is `read-batch`. It accepts exactly one `messageIds` form field containing a JSON array of 1–50 unique, nonempty string IDs, each at most 191 characters, plus exactly one `intent` field. Reject extra/duplicate fields, malformed JSON, duplicate IDs and oversized lists with HTTP 400 and `{marked:false}`. Read at most 65,536 body bytes before form parsing for this route; oversized bodies receive 413 and `{marked:false,errorCode:'SEND_FAILED'}`, allowing either caller to retain its existing failure presentation even when the intent could not be parsed. Preserve the existing compose grapheme/body validation within this explicit byte bound; do not invent a new merchant-facing error key.
5. Preserve legacy `intent=read&messageId=...` as a one-ID adapter returning the existing `{marked:boolean}` shape. There is no new route and no client-supplied Shop ID.
6. Implement one parameterized raw SQL statement inside the service transaction. A locking eligible-row CTE joins MerchantSupportMessage to MerchantSupportThread, constrains `shopId`, submitted IDs, kind and AVAILABLE state, and locks eligible message rows in ascending ID order. A count gate permits UPDATE only when every submitted ID is eligible. Update only rows whose `readAt IS NULL`, setting `readAt` and `updatedAt` once. Return `{marked:true}` for an entirely valid set, including a set that was already read. For any missing, foreign, merchant-authored or unavailable ID, return `{marked:false}` with no changes to any submitted row. Do not return matching IDs/counts that disclose foreign existence.
7. Only the submitted rendered IDs can change. IDs from another page remain untouched. Concurrent overlapping batches retain the first read timestamp and do not rewrite already-read `updatedAt`. Do not infer ownership from affected-row count alone.
8. `markUnreadMessages` sends one `read-batch` request for the visible IDs, no per-ID loop. On `marked:true`, refresh once unless cancelled/unmounted; on false/non-OK or transport failure, stop without acknowledging unseen messages. The compose fetcher continues to use router-managed action revalidation; do not add a compose success revalidation effect.

### R3 — atomic composition and durable postcommit handling

9. Fold thread `lastMessageAt`, `lastMerchantMessageAt`, `merchantMessageVersion` and `needsAdminResponse` into the existing INSERT ON CONFLICT. New thread version is 1; an existing thread increments its current version by 1. Insert the message and optional translation in the same transaction afterward. Delete the later thread UPDATE. A failed message/translation insert rolls back every thread change; concurrent successful messages increment the version exactly once each.
10. Keep the language read and translation decision inside the composition transaction. Keep translation publication after commit and retain the existing deterministic translation job ID/payload. Move queue acquisition/replacement/close into the best-effort catch boundary as well as `queue.add`. A queue failure after commit must log the original failure and preserve the successful message response plus durable PENDING translation. It must not cause the merchant to retry an already-committed compose operation because of Redis alone.

### R4 — diagnostic ownership

Apply the common mandatory server-error contract. Reuse the existing support semantic adapter; Shared remains the only serializer/sink/redactor. Pass original safe Error plus explicit available code/cause chain of at most four entries. Preserve thrown cause; do not log message bodies, translations, customer details or Redis URL. No database read is permitted solely to enrich a log.

| Failure/injection | Owning diagnostic | Required outcome |
|---|---|---|
| Badge SELECT or inbox page/aggregate SELECT rejects with a Prisma/driver marker and cause | Support reader; operation distinguishes badge/page/aggregate | One Shared error with original safe message/code/cause; propagate original error; no fabricated zero badge or empty inbox |
| Batch transaction/SQL fails | Batch service | Original database failure once; rollback; HTTP error remains operational, not `{marked:true}` |
| Compose transaction/insert fails | Support action's existing send-failure boundary | Original error/code/cause once; existing bounded `SEND_FAILED` response; no partial thread/message/translation |
| Queue creation/old-queue close/add rejects after commit | Existing translation-dispatch diagnostic, warn | Original error/cause once, durable success unchanged |
| Missing optional queue configuration | Internal unavailable classification only if dispatch was needed | No invented provider error; translation remains PENDING |
| Invalid payload, foreign/unavailable ID, already-read valid ID | Expected control flow | Preserve defined HTTP/marked outcomes; no fabricated operational error |
| Throwing Shared sink | Shared isolation | Database result, rollback and response unchanged |

## Work Items

- [x] Implement the unread count and two-query inbox projection.
- [x] Implement bounded atomic acknowledgement and one-ID compatibility adapter.
- [x] Wire actual framework context and one-batch UI acknowledgement.
- [x] Combine thread writes and preserve postcommit translation success.
- [x] Cover every operational failure in the matrix with emitted Shared diagnostics.
- [x] Register/run focused unit/UI/PostgreSQL checks and record same-fixture call/SQL/write evidence.

## Interfaces / Contracts

Contract owner for authentication/read caching: `ARCH-057-SHOPIFY-001`, `app/services/shop/merchant-request-context.server.ts`. Consume its exact `getMerchantRequestContext({request,context})` API; do not change it here.

New support exports, using the existing injectable database type extended with `$queryRaw` where required:

```ts
readMerchantSupportUnreadCount(input: {
  shopId: string;
  database?: DatabaseClient;
}): Promise<number>;

markMerchantSupportMessagesRead(input: {
  shopId: string;
  messageIds: readonly string[];
  database?: DatabaseClient;
}): Promise<{ marked: boolean }>;
```

`markMerchantSupportMessageRead` remains an adapter returning `Promise<boolean>`. Server validation also applies when the batch service is called directly. Public batch reply is only `{marked:boolean}`. No new schema/Shared/queue contract.

Add exact package scripts:

```json
{
  "test:merchant-support:unit": "vitest run tests/unit/merchant-support-service.test.ts tests/unit/merchant-support-route.test.ts tests/unit/merchant-support-observability.test.ts tests/unit/merchant-support-recovery-i18n.test.ts tests/unit/merchant-support-batch-ui.test.tsx",
  "test:merchant-support:postgres": "MODA_DISPOSABLE_INTEGRATION=1 vitest run tests/integration/merchant-support.postgres.test.ts"
}
```

## Dependencies

- ARCH-057-SHOPIFY-001

## Enables

- ARCH-057-SHOPIFY-011

## Acceptance Criteria

- [x] Badge executes one raw SELECT; inbox executes two; existing DTO, locale and system recovery-link semantics are unchanged.
- [x] Fifty visible unread messages produce one acknowledgement POST and one batch SQL statement, not fifty requests.
- [x] Mixed foreign/missing/unavailable batches change nothing; all valid already-read batches succeed without row changes; unseen messages remain unread.
- [x] PostgreSQL overlapping batches preserve first readAt/updatedAt, and concurrent compose transactions increment the thread version exactly once per committed message.
- [x] Compose uses three data calls without translation/four with translation, excluding transaction statements, with atomic rollback on insertion failure.
- [x] Queue acquisition/publication failure after commit retains the durable success and logs its original safe evidence.
- [x] Actual Shared records satisfy every failure-matrix case, redaction/cause checks and sink isolation.
- [x] No merchant copy/catalogue or independent authorization rule regresses.

## Validation

- [x] `npm run test:merchant-support:unit` — named cases include batch cardinality/body bounds, cancelled UI effect, one refresh, partial invalid set, already-read success and complete diagnostic matrix.
- [x] `npm run test:merchant-support:postgres` — own `pgvector/pgvector:pg17`, canonical forward migrations, separate connections and explicit lock barriers; test overlapping batches, rollback, cross-shop isolation, untranslated/system visibility and concurrent compose versions. Missing Docker or skipped cases block validation.
- [x] `npm run typecheck` and `npm run build`.
- [x] `npx --no-install eslint app/services/merchant-support app/routes/app/route.jsx app/routes/app/merchant-support/route.jsx tests/unit/merchant-support-service.test.ts tests/unit/merchant-support-route.test.ts tests/unit/merchant-support-observability.test.ts tests/unit/merchant-support-recovery-i18n.test.ts tests/unit/merchant-support-batch-ui.test.tsx tests/integration/merchant-support.postgres.test.ts tests/helpers/merchant-support-postgres.ts`.
- [x] `git diff --check`.
- [x] Record starting/final same-fixture repository calls separately from emitted SQL, transaction statements, rows changed and GraphQL calls. Capture actual Shared JSON; a mocked logger call is insufficient. Cleanup only task-owned containers/clients.

## Stop Condition

After all work, acceptance and required validation are complete, set the task to review and return its Completion Report to `moda_architect`. Stop for a missing prerequisite, required schema change or changed support visibility/translation contract. Do not implement enabled tasks, modify indices, merge or mark Complete.

## Implementation Notes

Keep the batching implementation local to the support service. An eligible-row locking CTE plus a count gate provides all-or-nothing eligibility without a second ownership round trip. Ordered row locks avoid reversing lock order for overlapping lists. Distinguish a zero-row UPDATE on an already-read valid batch from a failed eligibility gate. Shared diagnostics are best-effort, business writes are not.

## Completion Report

### Status

Ready for Review — Attempt 1. Implementation and required validation pass and are published. No architect acceptance decision is made here.

### Files Changed and Work Completed

- Support service: one parameterized unread-count SELECT; two-query inbox with combined total/unread aggregate; one ordered locking eligible-row CTE and count-gated batch UPDATE; legacy one-ID adapter. Direct-service and route validation enforce 1–50 unique nonempty IDs of at most 191 characters. Already-read rows retain both timestamps; a mixed invalid set changes nothing.
- Parent route consumes the scalar unread count. Support loader/action consume the existing request context and retain independent support authorization, active-only subscription policy and bounded merchant JSON. The action reads at most 65,536 bytes before form parsing and rejects extra/duplicate batch fields. The visible-page effect sends one JSON-array batch and refreshes once only after an uncancelled successful response. Compose keeps router-managed revalidation.
- Composition folds thread timestamps, needsAdminResponse and version into the upsert, followed by message/optional translation insertion in the same transaction. New version is 1; each subsequent successful compose increments once. Queue acquisition, replacement/close and publication all occur inside the postcommit best-effort boundary. Failed replacement cannot cache a closed queue. Missing configuration logs an internal unavailable diagnostic only when dispatch is required; durable PENDING translation and successful message response survive.
- Existing support semantic diagnostics delegate to the existing sanitized Shared boundary adapter for original safe error/code/causes; no generic logger or serializer is added. Stage distinguishes badge/page/aggregate/ack/compose/dispatch. Real Shared output tests cover source privacy, cause identity, status preservation and throwing sinks.
- Added only the two specified package scripts. Added task-local PG17 helper, PostgreSQL suite and mounted UI suite (all below 300 lines). Existing support tests updated; localized recovery action catalogue test is unchanged.
- Test-only compatibility adjustment: `tests/integration/merchant-request-context-router.test.ts` mocks the new unread-count port and the already-migrated Home presentation port. Real parent/child/middleware regression passes. Production edit scope remains exactly the four declared support/route files and package scripts; no prerequisite context implementation was changed.

### Validation Results

- `npm ci` and `npm run prisma:generate`: passed using locked dependencies and the pinned Database schema; no dependency/lockfile change. Existing npm allow-scripts notices were retained without changing approvals.
- `npm run test:merchant-support:unit`: **79 passed**, five files, no skips. Mounted UI tests use actual React Router loader/revalidation behavior, fifty rendered IDs, one POST/refresh, false/non-OK/transport failures and unmount cancellation. Unit/service/actual-Shared tests cover bounded payloads, tenant policy, one-ID compatibility, read budgets, original diagnostic evidence and queue constructor/close/add failure.
- `npm run test:merchant-support:postgres`: **4 passed**, no skips, owned `pgvector/pgvector:pg17`, canonical forward migrations, separate clients, explicit row-lock wait observation and compose barriers. Mixed foreign/missing/merchant/unavailable batches leave valid rows untouched. Already-read retries preserve timestamps; unseen rows remain unread. Overlap waits on the held row and retains the first readAt/updatedAt. Concurrent composes produce one version increment per message. Failures after actual message/translation inserts roll back thread and child rows. Postcommit queue failure retains durable PENDING translation. Final helper cleanup completed.
- `npm run test:merchant-request:router`: **9 passed**, no skips, real parent/child loaders and existing request-context/middleware with controlled external ports.
- `npm run build`: passed; existing large client-chunk warning remains.
- Required scoped ESLint command, focused router-fixture lint and final UI-fixture lint: passed. `npm run typecheck` passed after correcting the UI mock’s type annotation; this correction does not alter executed behavior.
- `git diff --check`: passed. Initial mounted UI setup, lint and mock typing failures were corrected; their earlier logs are retained, not counted as passing validation.

Same-fixture repository-call comparison ran the exact accepted starting service `de5650e73df91e4d52bbcb4131dd80d1c7a7d339` and current service with identical empty inbox/English compose inputs: inbox **3 -> 2** data calls, English compose **4 -> 3**, zero provider calls. The temporary baseline source/test were removed. Translation adds one insert (current four data calls), confirmed by service assertions. Badge now uses one raw SELECT; batch fifty-ID unit fixture uses one SQL invocation and one POST in mounted UI. These are method/request counts, not latency or physical-SQL claims.

Actual PostgreSQL SQL was counted separately: badge one SELECT; inbox two SELECTs plus BEGIN/COMMIT, returning four visible rows/three unread in the fixture. Final integration emitted **106 SQL statements including all setup, races, writes and assertion reads**; this total is not a per-operation budget. Batch executes one CTE statement plus transaction control; ownership denials change zero rows, successful submitted rows alone change, and already-read timestamps are compared byte-for-byte by returned row equality. No Shopify GraphQL or embedding call occurs in these support service fixtures. No throughput/capacity claim is inferred.

Actual Shared sink assertions inspect serialized records for original database marker, P2010 and original cause, and absence of injected email/token/Redis URL. Constructor, old-queue close and add failures are exercised through composition, not just direct mocked logger calls. The original thrown errors/cause identities remain intact. Sink failures preserve service rejection, rollback/marked outcome and durable postcommit success.

Evidence logs: `/tmp/arch057-shopify005-unit-router-final.log`, `...-postgres-final.log`, `...-router.log`, `...-build-final.log`, `...-lint-verified.log`, `...-before-after.log`; final passing type evidence is `/tmp/arch057-shopify005-types-final.log` and `/tmp/arch057-shopify005-ui-lint-typed.log`. All provider/queue fixtures are synthetic; no persistent migration/import, live Shopify request or external publication occurred.

### Provenance, Isolation and VCS

Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-057-SHOPIFY-005`, start `d7d9052aaa1565b52704228f8c204733f7ac414e`. Implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-057-SHOPIFY-005`, start `de5650e73df91e4d52bbcb4131dd80d1c7a7d339`. Both newly created by launcher, on `task/ARCH-057-SHOPIFY-005`. Remote task fast-forwards not needed; origin/main already current in both. Dependency gate passed for SHOPIFY-001. Recursive submodule sync/update/verification passed; recorded/working Database pin `8e74634ff92be9900f693c0c449ffce888e7d617` unchanged.

Durable Attempt 1 claim `8ee777b7a2c97e10add3bbd26ca71fb537c4822f`, pushed at `2026-11-04T16:19:52Z`, executor codex. Node 24.19.0/npm 11.17.0 via prescribed bootstrap, Prisma 6.19.3, installed Shared 3.1.0. Existing Colima endpoint/socket override used for the bounded single-container fixture, without host configuration changes or shared-resource cleanup. No shared/default checkout switched or edited, no other task worktree reused, no main merge, schema edit, identity/queue payload change or parent gitlink update. Implementation commits `793299f` and final `bc02d1095ed81daf601ca48d73e7958abdcb2768` are pushed to `origin/task/ARCH-057-SHOPIFY-005`. Both implementation and parent task branches use the matching task name. This task-only report is committed/pushed on the parent branch at submission; the parent gitlink is not staged.

### Deviations and Unresolved Issues

No business-policy, schema, locale, support visibility/translation or queue-identity change. One existing router test fixture was aligned as described above to verify the changed parent caller and current Home API; it adds no production scope. No unresolved implementation or validation issue remains in the bounded scope. Independent architect review remains pending. No downstream task was started.

### Architectural Concerns

None identified requiring a schema or cross-repository amendment. Request reads remain observations rather than mutation authority; architect review is still required.

## Architect Review

### Review Status

Accepted — Attempt 1, 2026-11-04. Completion mode is automatic: task is complete and the developer claim is cleared.

### Review Notes

No actionable correctness or regression finding identified after independent source and test review. Badge and inbox reads meet the one/two SELECT budgets. The tenant-scoped batch statement locks eligible IDs in deterministic order, gates the entire update on eligibility, and preserves the first read timestamp. Request bounds and field/cardinality checks, legacy single-ID compatibility, mounted UI batching/cancellation, compose rollback/version increments, and postcommit queue failure isolation conform to the task.

The existing request-context router test adjustment is accepted as a compatibility fixture update for the changed parent caller; it does not widen production behavior. No schema, policy, locale, provider operation, translation payload or deterministic queue identity change was introduced.

### Reviewed Files

Reviewed all 12 changed files in implementation commit `bc02d1095ed81daf601ca48d73e7958abdcb2768` against starting commit `de5650e73df91e4d52bbcb4131dd80d1c7a7d339`: support route and parent route, support service and observability adapter, package scripts, PostgreSQL helper/suite, request-context router fixture, and support service/route/observability/mounted UI unit suites. Reviewed the existing Shared diagnostic boundary and task/architecture contract as context. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-057-SHOPIFY-005`.

### Validation Reviewed

Independent reruns passed:

- Focused support unit/UI suite: 79 tests across five files, including real Shared output and throwing-sink checks.
- Disposable migrated PostgreSQL 17 suite: all four tests executed; no skipped suite. Captured inbox evidence: two SELECTs, two transaction-control statements and four visible rows. Full suite emitted 106 SQL statements including fixtures. Covered tenant/visibility rejection, already-read no-op, lock overlap/first timestamps, rollback and concurrent compose versions. Only suite-owned resources were cleaned up.
- Request-context router integration fixture: nine tests.
- Typecheck, production build, required support lint scope and changed router fixture lint.
- Implementation diff whitespace check and clean implementation worktree.

Review logs are local `/tmp/arch057-shopify005-review-{units,postgres,typecheck,build,lint,required-lint,router}.log`. The production build retains its existing client chunk-size warning; it completed successfully. No live Shopify call was needed or made for this support database/UI review. Full platform certification remains owned by the terminal system-test task.

### Architecture Conformance

Accepted within the bounded Shopify support lifecycle. Existing authentication, active subscription filtering, message visibility, translation rendering, transaction atomicity and durable compose success are preserved. Shared logging remains the serializer/sink owner; the support adapter adds semantic stage context without introducing a new logging implementation.

### Follow-up

SHOPIFY-011 remains pending on its other explicit prerequisites. No downstream task was started. Acceptance and lifecycle reconciliation are local review edits; they have not been committed or pushed.
