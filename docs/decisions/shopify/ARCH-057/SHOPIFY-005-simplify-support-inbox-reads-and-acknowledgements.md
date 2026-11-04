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
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
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

Read the mandatory `docs/architecture/ARCH-057/task-contract.md`, including its latest-snapshot provenance, materialisation, original-error logging and validation requirements. **Defined but not materialised.** Canonical destination: `docs/decisions/shopify/ARCH-057/SHOPIFY-005-simplify-support-inbox-reads-and-acknowledgements.md`. No branch, worktree, execution claim, commit, push or passing implementation result is asserted.

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

- [ ] Implement the unread count and two-query inbox projection.
- [ ] Implement bounded atomic acknowledgement and one-ID compatibility adapter.
- [ ] Wire actual framework context and one-batch UI acknowledgement.
- [ ] Combine thread writes and preserve postcommit translation success.
- [ ] Cover every operational failure in the matrix with emitted Shared diagnostics.
- [ ] Register/run focused unit/UI/PostgreSQL checks and record same-fixture call/SQL/write evidence.

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

- [ ] Badge executes one raw SELECT; inbox executes two; existing DTO, locale and system recovery-link semantics are unchanged.
- [ ] Fifty visible unread messages produce one acknowledgement POST and one batch SQL statement, not fifty requests.
- [ ] Mixed foreign/missing/unavailable batches change nothing; all valid already-read batches succeed without row changes; unseen messages remain unread.
- [ ] PostgreSQL overlapping batches preserve first readAt/updatedAt, and concurrent compose transactions increment the thread version exactly once per committed message.
- [ ] Compose uses three data calls without translation/four with translation, excluding transaction statements, with atomic rollback on insertion failure.
- [ ] Queue acquisition/publication failure after commit retains the durable success and logs its original safe evidence.
- [ ] Actual Shared records satisfy every failure-matrix case, redaction/cause checks and sink isolation.
- [ ] No merchant copy/catalogue or independent authorization rule regresses.

## Validation

- [ ] `npm run test:merchant-support:unit` — named cases include batch cardinality/body bounds, cancelled UI effect, one refresh, partial invalid set, already-read success and complete diagnostic matrix.
- [ ] `npm run test:merchant-support:postgres` — own `pgvector/pgvector:pg17`, canonical forward migrations, separate connections and explicit lock barriers; test overlapping batches, rollback, cross-shop isolation, untranslated/system visibility and concurrent compose versions. Missing Docker or skipped cases block validation.
- [ ] `npm run typecheck` and `npm run build`.
- [ ] `npx --no-install eslint app/services/merchant-support app/routes/app/route.jsx app/routes/app/merchant-support/route.jsx tests/unit/merchant-support-service.test.ts tests/unit/merchant-support-route.test.ts tests/unit/merchant-support-observability.test.ts tests/unit/merchant-support-recovery-i18n.test.ts tests/unit/merchant-support-batch-ui.test.tsx tests/integration/merchant-support.postgres.test.ts tests/helpers/merchant-support-postgres.ts`.
- [ ] `git diff --check`.
- [ ] Record starting/final same-fixture repository calls separately from emitted SQL, transaction statements, rows changed and GraphQL calls. Capture actual Shared JSON; a mocked logger call is insufficient. Cleanup only task-owned containers/clients.

## Stop Condition

After all work, acceptance and required validation are complete, set the task to review and return its Completion Report to `moda_architect`. Stop for a missing prerequisite, required schema change or changed support visibility/translation contract. Do not implement enabled tasks, modify indices, merge or mark Complete.

## Implementation Notes

Keep the batching implementation local to the support service. An eligible-row locking CTE plus a count gate provides all-or-nothing eligibility without a second ownership round trip. Ordered row locks avoid reversing lock order for overlapping lists. Distinguish a zero-row UPDATE on an already-read valid batch from a failed eligibility gate. Shared diagnostics are best-effort, business writes are not.

## Completion Report

### Status

Not Started. Defined but not materialised; attempt 0 and no execution claim.

### Files Changed

None. Definition only.

### Work Completed

None.

### Validation Results

Not run. Record exact commands/results, fixture names, actual SQL versus method counts, log-marker/cause/redaction evidence, installed versions, prepared worktree packet, source pins and owned-resource cleanup.

### Deviations

None.

### Assumptions

The canonical launcher verifies the accepted dependency and integrated source before execution.

### Unresolved Issues

Implementation and validation remain outstanding.

### Architectural Concerns

Return changes to ownership, schema, tenant/visibility policy, queue identity or durable-state semantics to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition only; no implementation acceptance.

### Reviewed Files

Definition and latest unchanged support touchpoints.

### Validation Reviewed

Definition inspection only; implementation evidence is outstanding.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

Return the completed task for architect review; do not start downstream work.
