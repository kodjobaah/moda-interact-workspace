---
id: ARCH-057-SHOPIFY-008
architecture_id: ARCH-057
title: Simplify merchant knowledge processing and bounded refresh
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 50
executor: codex
claimed_at: 2026-11-04T20:55:21Z
attempt: 1
depends_on:
- ARCH-057-SHOPIFY-001
- ARCH-057-SHOPIFY-007
enables:
- ARCH-057-SHOPIFY-011
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-057-SHOPIFY-008: Simplify merchant knowledge processing and bounded refresh

## Architecture

Architecture ID: `ARCH-057`. Architecture document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`. Coordinator: `moda_architect`.

Mandatory execution/logging/validation contract: `docs/architecture/ARCH-057/task-contract.md`. Materialised in the canonical parent and implementation worktrees on `task/ARCH-057-SHOPIFY-008`; Attempt 1 was claimed by the launcher. The Completion Report records implementation/validation evidence; architect acceptance is not asserted.

## Objective

Use the existing settings read facts for Merchant Knowledge presentation, remove unused reads and per-row reorder writes, distinguish operational unavailability from policy denial, and make knowledge refresh follow the installed router's action lifecycle with a fixed polling deadline.

## Context

Review F11/F13 identifies repeated settings/entitlement/language/preference reads, unused upload-intent activation and finalization language reads, per-row reorder writes, and an explicit success effect duplicating router revalidation. An exact-version infinite refresh loop was not established by the audit. This task removes the redundant effect and proves the resulting behavior with the actual installed router rather than declaring a speculative production incident.

Operational errors currently lose information in entitlement fallbacks, R2 HEAD classification, queue publication and the upload adapter's errorType-only output. The user requires all such handled failures to retain original safe source evidence through Shared logging.

## Scope

Paths are relative to `moda-interact`.

### Production edit map

| Existing path | Required edit |
|---|---|
| `app/services/merchant-knowledge/merchant-knowledge.server.ts` | Consume the supplied settings read context; share pure entitlement/activation facts; remove unused read paths; implement two-statement ordered rewrite; re-export the moved error class for compatibility |
| `app/services/merchant-knowledge/merchant-knowledge-entitlement.server.ts` | Extract pure entitlement projection; retain unavailable with actual cause rather than turning it into denied; own diagnostics for converted failures |
| `app/services/merchant-knowledge/upload.server.ts` | Remove unused activation/default-language reads, distinguish real storage404 from operational failure, preserve causes and durable finalization/queue semantics |
| `app/services/merchant-knowledge/r2-client.server.ts` | Own R2/AWS SDK source diagnostics with safe original evidence; preserve actual thrown exception; add trusted shop correlation at construction |
| `app/services/merchant-knowledge/merchant-knowledge-queue.server.ts` | Log actual acquisition/close/add errors while retaining best-effort false and durable pending revisions |
| `app/services/merchant-knowledge/merchant-knowledge-observability.server.ts` | Extend the existing thin Shared semantic adapter; retain original safe messages/codes/causes/provider details, not only errorType |
| `app/routes/app/recovery-settings/route.tsx` | Pass the SHOPIFY-007 `SettingsReadContext` to knowledge loading; no duplicate scalar/relation projection |
| `app/routes/app/merchant-knowledge/source/route.ts` | Pass framework context to `settingsMutationAccess`; preserve create/edit/edit-upload forms and use common knowledge HTTP error mapping |
| `app/routes/app/merchant-knowledge/reorder/route.ts` | Same guard/error integration; retain existing 131072-character sourceIds bound and exact-set validation |
| `app/routes/app/merchant-knowledge/refresh/route.ts` | Same guard/error integration; preserve durable generation/queue behavior |
| `app/routes/app/merchant-knowledge/delete/route.ts` | Same guard/error integration; preserve tenant ownership and deletion semantics |
| `app/routes/app/merchant-knowledge/reprocess/route.ts` | Same guard/error integration; preserve immutable uploaded-asset reuse |
| `app/routes/app/merchant-knowledge/upload-intent/route.ts` | Same guard/error integration; preserve signed upload contract and input bounds |
| `app/routes/app/merchant-knowledge/upload-finalize/route.ts` | Same guard/error integration; return operational503 versus genuine missing-object400 correctly |
| `app/routes/app/merchant-knowledge/upload-failure/route.ts` | Use the minimal guard; retain telemetry-only behavior and truthful client-reported origin |
| `app/components/settings/MerchantKnowledgeSection.tsx` | Remove fetcher-success revalidation; implement the fixed polling episode; distinguish unavailable from plan denial using existing localized common.unavailable text |
| `app/components/settings/MerchantKnowledgeUploadForm.tsx` | Preserve its one explicit plain-fetch finalization refresh; update typed handling for unavailable without exposing source error text |
| `tests/fixtures/settings-preview/main.tsx` | Keep fixture DTOs in sync with the added entitlement-state discriminant only |
| `package.json` | Add the exact three scripts below; no dependency/router upgrade |

New production files:

- `app/services/merchant-knowledge/merchant-knowledge-error.server.ts`: the one domain error class with optional cause/retryable metadata. Existing `merchant-knowledge.server.ts` re-exports the same class so imports and instanceof identity remain compatible.
- `app/services/merchant-knowledge/merchant-knowledge-http.server.ts`: one local HTTP mapping for known business/unavailable outcomes and the action-owned unexpected-error diagnostic. It is not a generic error framework.

Existing tests to update only for these contracts:

- `tests/unit/merchant-knowledge-actions.test.ts`, `merchant-knowledge-read-model.test.ts`, `merchant-knowledge-entitlement.test.ts`, `merchant-knowledge-upload.test.ts`, `merchant-knowledge-observability.test.ts`, `merchant-knowledge-queue.test.ts`, `merchant-knowledge-section.test.tsx`, `merchant-knowledge-upload-form.test.tsx` under `tests/unit/`.
- `tests/integration/merchant-knowledge-source-lifecycle.integration.test.ts` and `tests/integration/merchant-knowledge-upload.integration.test.ts` retain current durable/source/asset cases; add no copied schema or old migration edits.

New test/helper files, each below 300 lines:

- `tests/unit/merchant-knowledge-read-context.test.ts`
- `tests/unit/merchant-knowledge-ordering.test.ts`
- `tests/unit/merchant-knowledge-r2-diagnostics.test.ts`
- `tests/integration/merchant-knowledge-router.test.tsx`
- `tests/helpers/merchant-knowledge-router-fixtures.tsx`
- `tests/integration/merchant-knowledge-ordering.postgres.test.ts`
- `tests/integration/merchant-knowledge-finalization.postgres.test.ts`
- `tests/helpers/merchant-knowledge-postgres.ts`

## Out of Scope

No new knowledge-status endpoint, new polling service, cross-request cache, source-count truncation to the current plan allowance, global plan include, Background ingestion/reconciliation change, R2 key/signing identity change, queue/job identity change, finalize replay redesign, schema/migration/index, new dependency or unapproved locale copy. Do not remove fresh locked source/asset/entitlement checks. Do not treat a queue hint as the durable work record.

## Requirements

### R1 — reuse presentation facts; keep admission fresh

1. All eight production actions accept `{request,context}` and call SHOPIFY-007's `settingsMutationAccess(request,context)`. For an established tenant with valid prerequisites they no longer fetch unused ShopSettings. Retain SHOPIFY-001's authenticated missing-prerequisite bootstrap/repair outside this guard-only zero-read budget. Upload-failure remains telemetry-only after its guard, with no source/asset lookup added solely for logging.
2. Extend `loadMerchantKnowledge(shopId, database, readContext?)` with the exact optional server context below. When supplied, require matching shopId and use its scalar subscription, plan/mappings, preference list and default language. Use a pure entitlement projection shared with the existing transaction loader. Do not reread Subscription, Shop language or a preference already represented by that context.
3. If the loaded plan contains the merchant_knowledge Feature mapping, derive activation from that Feature's current active/activationMode metadata and the context preference list. If the mapping is absent, perform one Feature lookup by key to retain the existing display of merchantEnabled independently of plan entitlement, still using the supplied preference list. An inactive/missing feature remains disabled. Do not infer absence of the global Feature from absence of a plan mapping.
4. Keep current catalogue/source/latest-revision/active-revision loading, ordering, source status and dormant reasons for determinate entitlement. All configured sources, including downgraded/over-limit/type-dormant sources, remain visible; do not apply current-plan take limits to that management list. Current source order still determines plan-eligible slots.
5. Existing standalone loaders and mutation services continue to load fresh entitlement facts from their provided transaction/database. Read contexts are never passed into writes. Every source/upload mutation retains ACTIVE Shop lock, exact same-Shop source/asset locks, current plan/type/count admission, generation checks and durable revision creation.
6. Remove `readMerchantKnowledgeActivation` from upload-intent creation: its return is unused and configuring/uploading sources while featureOFF remains allowed. On new-source finalization, use the already required and validated languageTag directly; remove only the unreachable Shop default-language fallback read. Keep actual fallback behavior for APIs where language is optional.

### R2 — bounded operations for ordering

7. Reorder reads the current tenant IDs and positions in `(position,id)` order under the existing ACTIVE Shop lock. Validate the exact submitted ID set before writes. If requested IDs already have that order and positions are contiguous zero-based, return success with zero ordering UPDATEs and unchanged updatedAt. An empty list for a shop with no sources is a successful no-op.
8. For a changed order, preserve two-phase collision safety under the immediate unique `(shopId,position)` constraint. Before either write, verify every existing position is a nonnegative integer, compute `offset = maxPosition + 1`, and require `maxPosition + offset <= 2147483647` and the final largest ordinal minus one to fit the same PostgreSQL signed-int range. The first UPDATE adds that offset to every tenant position, so the temporary range is disjoint from both existing and final ranges. Invalid persisted range produces a typed CONFLICT and original internal diagnostic, not integer wraparound. Then perform one parameterized UPDATE FROM `unnest(text[]) WITH ORDINALITY`, assigning ordinal minus one for the exact submitted IDs and matching shopId; set updatedAt to one operation timestamp in this final UPDATE only. Use one bound array, not N individual UPDATEs or a dynamically concatenated ID list. Verify both affected counts against the validated tenant set; rollback on mismatch.
9. Deletion retains its owned-source lock/delete and obtains remaining ordered IDs/positions. It calls the same rewrite primitive only if remaining positions need compaction. Deleting the last item does not rewrite unaffected rows. All ordering writes occur in the same Shop-locked transaction; preserve rollback and exact ID-set semantics under concurrent reorder/delete/create operations.
10. Do not change idempotency of refresh/reprocess: an explicit accepted refresh still produces its intended new generation. No timestamp-only no-op behavior is invented for those commands.

### R3 — router-managed actions and a fixed processing episode

11. Delete the fetcher-success effect at the current MerchantKnowledgeSection lines64–67. The actual installed router owns fetcher action revalidation. Do not replace it with another unconditional success effect or fetcher-data reset mechanism.
12. A continuous `hasProcessingSources` episode starts when the value changes false→true and lasts at most60,000ms. Store its start/deadline in a ref; changes to fetcher/revalidator object identity, loader data, loading/idle state or ordinary rerenders do not restart the episode. A later false→true episode gets a new deadline. No new endpoint is introduced.
13. During the episode, check every4,000ms. Revalidate only when the document is visible, the current revalidator state is idle and the deadline has not expired. Read the current revalidator through a ref so an interval does not capture stale state. Prevent overlapping reloads. Hidden time counts toward the same deadline. Stop timers at deadline, when processing ends, and on unmount; visibility changes after expiry do not restart polling. Preserve one explicit refresh after successful upload finalization because that path uses plain fetch.
14. Prove action and polling behavior using a mounted `createMemoryRouter`/`RouterProvider` with the installed lockfile router (currently7.18.2) and actual `useFetcher`/`useRevalidator`. Control only route loader/action data and external upload HTTP fixtures. Do not mock those hooks. Fake time and visibility are permitted; report installed version. One successful action produces its router-managed reload without an extra loop; a slow loader prevents overlap; deadline remains fixed through many loader/fetcher state transitions. Do not claim this test reproduces a previously observed production loop.

### R4 — unavailable is different from denied

15. Keep `MerchantKnowledgeEntitlement` as entitled/denied/unavailable and retain an internal original `cause` for unavailable results. Database failure is unavailable/retryable; invalid persisted feature configuration is unavailable/nonretryable with its actual parse cause. Only genuine missing/inactive/unentitled plan policy is denied. A pure projection never fabricates an upstream error.
16. Mutations convert unavailable entitlement/config/storage/unknown operational failures into HTTP503 `{ok:false,error:'UNAVAILABLE',retryable:boolean}`. Set retryable true for database availability failures, transport/timeouts, HTTP429 and HTTP5xx; false for malformed configuration, credentials/authorization failures, other non-not-found HTTP4xx, and unclassified internal failures. Existing invalid400, denied403 and conflict409 responses remain. `MerchantKnowledgeError` preserves the original cause when wrapping; the HTTP mapper never emits that cause/message to the browser. Do not catch all exceptions as DENIED or generic success.
17. Add `entitlementState: 'entitled' | 'denied' | 'unavailable'` to the knowledge read DTO while retaining existing fields. On unavailable, show the existing translated `common.unavailable` text and disable mutation controls; do not show the plan-denial text or mark retained sources NO_CURRENT_PLAN from uncertainty. Existing configured source rows remain available for read-only display when their reads succeeded. When an earlier mandatory settings-context read itself fails, propagate its already logged operational failure; do not fabricate a partial authorized settings page.
18. A genuine R2 HEAD not-found is recognized from actual SDK HTTP404 or a genuine service exception named NotFound/NoSuchKey and remains UPLOAD_OBJECT_NOT_FOUND/400. Network/timeouts,429,5xx, credential403 and malformed configuration are UNAVAILABLE/503 with the exact retryability mapping in R4.16. HEAD remains outside the SQL transaction. Existing status/expiry predicate under asset lock remains mandatory; repeated successful finalization retains the existing conflict behavior rather than introducing a replay contract.
19. Once finalization commits, an activation-read or queue acquisition/publication failure is logged but must not turn the successful durable source/asset/revision outcome into an HTTP failure. Preserve `queued:false` and pending reconciliation. No storage or Redis call occurs inside the write transaction.

### R5 — source-owned diagnostics

Apply the common error contract through the existing knowledge semantic adapter and Shared `createLogger`/`sanitizeLogFields`. The adapter supplies explicit safe original error/code/causeChain (maximum4), actual provider metadata and redaction/truncation flags. No generic serializer, log registry, competing sink or copied redactor. Preserve actual thrown cause/exception identity where not deliberately wrapping a typed domain result.

| Failure/injection | Source owner | Required emitted evidence and business result |
|---|---|---|
| Entitlement DB query rejects | Entitlement loader | Original safe DB marker/code/cause, origin database; unavailable/retryable, never denied |
| Persisted feature configuration fails parsing | Entitlement projection boundary | Original safe parse cause, origin internal; unavailable/nonretryable, no invented provider fields |
| Knowledge source/revision/catalogue read or mutation DB failure not converted below | Read-model boundary or HTTP action mapper respectively | Original DB message/code/cause once; safe error/503, transaction rollback preserved |
| R2 signPut or HEAD SDK/service/transport exception | `r2-client.server.ts` via existing knowledge semantic adapter | Actual safe name/message/cause, status/code/request ID/details when supplied; preserve original thrown exception |
| R2 actual404 versus503/429/403/transport | Same R2 source owner; upload maps without re-logging source body | Correct400 missing-object versus503 unavailable; no asset/source writes before HEAD success |
| Sealed configuration fails during upload or display limit load | Owning knowledge caller if not already logged by its source adapter | Actual safe config cause; upload503 or display maxUploadBytes0 as applicable; never log envelope/keyring/credentials |
| P2025 converted by upload normalizeError | Conversion boundary | Actual safe DB cause/code retained before current typed denial; no loss caused by constructing a fresh code-only Error |
| Postcommit activation read fails | Finalization continuation | Original DB failure once, warn; successful committed result with queuedfalse |
| Queue creation/old queue close/add fails | Knowledge queue helper | Original safe Redis/BullMQ error/cause once, warn; false and durable pending revision |
| Optional queue absent | Queue helper when dispatch requested | Truthful internal unavailable classification, no fabricated SDK/provider message |
| Browser upload-failure telemetry | Existing telemetry route | Explicit client-reported stage/status/code; never pretend to possess the provider's original server response or accept arbitrary raw error text |
| Validation, expected conflict/denial | Typed control flow | Preserve400/403/409; no fabricated upstream error |
| Throwing Shared sink | Shared isolation | Same HTTP status, rollback, finalized rows, queued result and retry decision |

R2 diagnostics remove credentials, signed URLs, object keys, raw request/response bodies and echoed PII before Shared emission. Retain safe original provider wording/details; redact only unsafe portions, or explicitly mark an inseparable unsafe portion `[REDACTED]`. Keep no-error/malformed-success cases free of fabricated providerError. Pass trusted shopId into R2 client construction; do not perform another DB read for correlation. Browser replies never contain provider diagnostics.

## Work Items

- [x] Migrate all knowledge actions to the minimal context-aware guard.
- [x] Reuse settings read facts and preserve dormant source/activation semantics.
- [x] Remove the two unused upload reads and implement zero-write no-op/two-statement order changes.
- [x] Add cause-preserving unavailable/error mapping and complete the diagnostic matrix.
- [x] Remove duplicate success revalidation and implement the fixed visibility/idle/deadline polling episode.
- [x] Add exact mounted-router and migrated PostgreSQL proofs; register scripts and report emitted-log/query evidence.

## Interfaces / Contracts

Consumes `ARCH-057-SHOPIFY-001` context and `ARCH-057-SHOPIFY-007`'s exact `settingsMutationAccess`/`SettingsReadContext`/`loadSettingsReadContext`. Do not change those contracts in this task.

```ts
loadMerchantKnowledge(
  shopId: string,
  database?: Database,
  readContext?: SettingsReadContext,
): Promise<ExistingKnowledgeDto & {
  entitlementState: "entitled" | "denied" | "unavailable";
}>;

class MerchantKnowledgeError extends Error {
  readonly code: string;
  readonly retryable?: boolean;
  constructor(code: string, options?: { cause?: unknown; retryable?: boolean });
}

merchantKnowledgeActionFailure(
  error: unknown,
  context: { operation: string; shopId: string; sourceId?: string; assetId?: string },
): Response;
```

The pure entitlement projection accepts the current scalar Subscription and plan/Feature facts and returns the existing discriminated result with internal unavailable cause. The fresh transaction loader calls that same pure projection. The action mapper owns previously unhandled operational failures; already source-owned unavailable/storage/queue diagnostics are not emitted again. Known typed outcomes preserve existing error names and statuses except the explicitly selected UNAVAILABLE503 distinction.

Keep existing upload intent fields, signed PUT headers/expiry, R2 key, finalize fields, source/revision models, queue payload/job ID and all success replies unchanged. `ExistingKnowledgeDto` denotes the current inferred read DTO, not a Shared wire schema. The new entitlement discriminant stays in the local merchant presentation contract. Reuse the existing `common.unavailable` translation in every locale; no new English-only message or catalogue key.

Add exact package scripts:

```json
{
  "test:merchant-knowledge:unit": "vitest run tests/unit/merchant-knowledge-actions.test.ts tests/unit/merchant-knowledge-read-model.test.ts tests/unit/merchant-knowledge-entitlement.test.ts tests/unit/merchant-knowledge-upload.test.ts tests/unit/merchant-knowledge-observability.test.ts tests/unit/merchant-knowledge-queue.test.ts tests/unit/merchant-knowledge-section.test.tsx tests/unit/merchant-knowledge-upload-form.test.tsx tests/unit/merchant-knowledge-read-context.test.ts tests/unit/merchant-knowledge-ordering.test.ts tests/unit/merchant-knowledge-r2-diagnostics.test.ts",
  "test:merchant-knowledge:router": "vitest run tests/integration/merchant-knowledge-router.test.tsx",
  "test:merchant-knowledge:postgres": "MODA_DISPOSABLE_INTEGRATION=1 vitest run tests/integration/merchant-knowledge-source-lifecycle.integration.test.ts tests/integration/merchant-knowledge-upload.integration.test.ts tests/integration/merchant-knowledge-ordering.postgres.test.ts tests/integration/merchant-knowledge-finalization.postgres.test.ts"
}
```

## Dependencies

- ARCH-057-SHOPIFY-001
- ARCH-057-SHOPIFY-007

## Enables

- ARCH-057-SHOPIFY-011

## Acceptance Criteria

- [x] All eight actions perform no guard-only settings read for established valid tenants while retaining authenticated prerequisite repair; GET presentation reuses supplied scalar/plan/preference facts and retains global-feature fallback where necessary.
- [x] OFF configuration and dormant/over-limit source management remain intact; indeterminate availability never masquerades as plan denial.
- [x] Upload intent performs no activation read; validated-language finalization performs no default-language fallback read.
- [x] Identical dense reorder has zero ordering writes; changed order has two SQL writes regardless of source count; delete compaction preserves unique contiguous positions and rollback.
- [x] The actual pinned mounted router proves one automatic action refresh, no success-effect loop, no overlapping polls and a fixed60-second deadline across revalidation/visibility transitions. Plain-fetch upload still refreshes once.
- [x] Database/provider unavailability maps to safe503 rather than403/400 misclassification; real missing object remains400, with original cause and safe provider evidence logged once.
- [x] Concurrent source/order/finalize tests run on canonical migrated PG17 and preserve exact ownership, count limits, unique positions, one successful finalization and durable pending work after queue failure.
- [x] Every failure-matrix row passes actual Shared JSON marker/code/cause/redaction/sink assertions, without source/provider/credential leakage to merchant DTOs.
- [x] No new endpoint, schema, global cache, dependency, queue identity, user-facing English-only text or architecture-ID runtime name is introduced.

## Validation

- [x] `npm run test:merchant-knowledge:unit` — include null/denied/unavailable entitlement, active/inactive/missing global Feature fallback, downgraded sources, no-op versus changed ordering, integer-range failure, unused-read absence, storage404/403/429/503/transport, postcommit continuation and complete diagnostic matrix.
- [x] `npm run test:merchant-knowledge:router` — mounted actual installed `createMemoryRouter`/`RouterProvider` and hooks; record installed/locked version. Test all five fetcher operations, automatic revalidation, failed action, successful plain-fetch finalize, pending→active, repeated revalidations through60s, slow loader overlap, hidden/visible transitions, unmount and a later new episode. Do not mock useFetcher/useRevalidator or treat a hook stub as runtime proof.
- [x] `npm run test:merchant-knowledge:postgres` — all own `pgvector/pgvector:pg17`, canonical migrations. New ordering suite proves overlapping reorder/reorder and both delete/reorder lock orders using separate connections/barriers, exact-set conflict and unchanged rows on no-op. New finalization suite proves two simultaneous finalizations of one asset have one committed source/revision, inactive-shop/count-limit denial leaves no partial rows, and postcommit activation/queue failure retains durable pending work. Provider/storage/queue boundaries are controlled fixtures, not live services. Missing Docker or skipped tests block validation.
- [x] `npm test -- tests/unit/merchant-knowledge-url-validation.test.ts tests/unit/recovery-settings-i18n.test.ts` — URL restrictions and all existing locale keys remain valid.
- [x] `npm run typecheck` and `npm run build`.
- [x] `npx --no-install eslint app/services/merchant-knowledge app/routes/app/merchant-knowledge app/routes/app/recovery-settings/route.tsx app/components/settings/MerchantKnowledgeSection.tsx app/components/settings/MerchantKnowledgeUploadForm.tsx tests/unit/merchant-knowledge-actions.test.ts tests/unit/merchant-knowledge-read-model.test.ts tests/unit/merchant-knowledge-entitlement.test.ts tests/unit/merchant-knowledge-upload.test.ts tests/unit/merchant-knowledge-observability.test.ts tests/unit/merchant-knowledge-queue.test.ts tests/unit/merchant-knowledge-section.test.tsx tests/unit/merchant-knowledge-upload-form.test.tsx tests/unit/merchant-knowledge-read-context.test.ts tests/unit/merchant-knowledge-ordering.test.ts tests/unit/merchant-knowledge-r2-diagnostics.test.ts tests/integration/merchant-knowledge-router.test.tsx tests/integration/merchant-knowledge-source-lifecycle.integration.test.ts tests/integration/merchant-knowledge-upload.integration.test.ts tests/integration/merchant-knowledge-ordering.postgres.test.ts tests/integration/merchant-knowledge-finalization.postgres.test.ts tests/helpers/merchant-knowledge-router-fixtures.tsx tests/helpers/merchant-knowledge-postgres.ts tests/fixtures/settings-preview/main.tsx`.
- [x] `git diff --check`; report same-fixture source method calls, emitted SQL/affected rows, router loader/action/poll counts and actual Shared records separately. Preserve safe original cause markers, no invented upstream fields, and owned-container/client/timer cleanup.

## Stop Condition

After all acceptance and mandatory validation pass, set review, complete the report and return to `moda_architect`. Stop on incompatible accepted context, missing Shared capability, actual installed-router mismatch requiring a version change, required schema change or different durable identity/processing semantics. Do not weaken tests, bypass tenant/lock checks or start downstream tasks.

## Implementation Notes

The read projection and transaction admission serve different purposes. Keep the latter fresh. A source list after plan downgrade is management data, not merely a list of currently usable sources. A pending revision is the durable work record; Redis is a postcommit hint. Two-phase order movement is required because unique positions are immediate, so replacing it with a direct swap is incorrect even inside a transaction. Timer stability is verified with actual router state, not guessed hook object identities.

## Completion Report

### Status

Ready for Review — Attempt 1. Implementation and required validation pass. Implementation `e41537919e2a639de4f036582555b79f29c521c6` is committed and pushed on `task/ARCH-057-SHOPIFY-008`. No architect acceptance decision is made here.

### Work Completed and Files Changed

- Added the one cause-preserving domain error module with compatibility re-export and the local common HTTP mapper. All eight knowledge actions use `settingsMutationAccess(request, context)`; existing form/tenant bounds remain. Typed invalid/denied/conflict outcomes retain 400/403/409; operational failures become bounded UNAVAILABLE503 with evidence-based retryability and no internal message in browser responses.
- Settings GET supplies its accepted read context to knowledge loading. Pure entitlement projection is shared with fresh transaction admission; supplied Shop/Subscription/plan/features/preferences avoid duplicate reads. A missing plan mapping triggers only the necessary global Feature lookup, without rereading preferences. Inactive/missing global Feature remains disabled. All configured sources remain visible after downgrade and during unavailability; uncertainty does not become NO_CURRENT_PLAN. The DTO adds entitlementState. The settings preview fixture has no knowledge DTO to amend and remains unchanged.
- Upload intent drops its unused activation read; finalization uses its already validated language without the unreachable default-language query. HEAD stays before SQL. Actual HTTP404/genuine service not-found differs from 403/429/503/transport; nonretryable configuration and unknown internal failures remain distinct. Original causes survive typed wrapping, including P2025 normalization. Successful committed finalization retains queued:false and pending revisions after activation/queue failure.
- Ordering validates the exact tenant set under the existing ACTIVE Shop lock. Dense identical/empty order returns with zero ordering writes. Changed order uses a checked maxPosition+1 disjoint offset and one bound text-array unnest/ordinality assignment, verifies both row counts, and sets one operation timestamp only in the final statement. Deletion reuses compaction only when needed. Generation/asset/source locks, current entitlement admission and explicit refresh/reprocess generation behavior remain fresh.
- MerchantKnowledgeSection drops its redundant fetcher-success effect. A ref-owned sixty-second episode with four-second ticks checks current visibility/revalidator idle state and prevents overlap. Rerenders and reloads do not extend its deadline; end/unmount cleans timers and later false-to-true starts a new episode. Actual installed React Router tests use real hooks. Plain-fetch upload keeps its one explicit refresh. Unavailable data uses existing common.unavailable copy and disables mutation controls while retaining readable source rows.
- The existing knowledge semantic adapter uses Shared createLogger/sanitizeLogFields and the existing safe boundary helper. It supplies bounded original cause/code/status/request evidence, distinguishes real Prisma/driver codes from domain source codes, masks known R2 secrets/object identity and protects native JSON-parser excerpts without mutating the thrown SDK exception. Queue constructor/old-close/add failures retain false and warn; optional absence has truthful internal classification. No generic serializer, sink or log registry is introduced.
- Added the three exact package scripts; fixed a missing comma already present between starting scripts so package.json could parse. No package/dependency/router version changed. Updated existing knowledge tests and added the declared context/order/R2/router/PostgreSQL helpers/suites; all new files are below 300 lines. Existing lifecycle integration has focused fixture/assertion edits only. No schema, locale, key/signing/job identity, Background, context-contract or other implementation repository changed.

### Validation and Evidence

- Locked `npm ci` and pinned-schema Prisma generation passed. Initial tests ran before generation finished and failed to import the client; those results are superseded by generated-client runs and are not counted as acceptance evidence.
- Final exact unit script: **81 passed**, eleven files, zero failures/skips; includes diagnostic classification and cause-preserving P2025 normalization. Real Shared assertions cover original message/cause/native codes, source code versus database code, R2 status/request IDs, privacy sentinels, malformed parser excerpts, source ownership and throwing sinks.
- Actual mounted router suite: **10 passed**, zero skips, with real createMemoryRouter/RouterProvider/useFetcher/useRevalidator. Five successful fetcher operations each cause exactly one automatic loader reload; failure does not add a success loop. Tests cover plain-fetch finalize, pending-to-active, repeated reloads, sixty-second hidden-time-inclusive deadline, later episode, slow loader overlap, unmount and unavailable read-only presentation. This does not claim an observed production loop was reproduced.
- URL/localization preservation: **7 passed**, zero skips.
- Final `npm run typecheck`, `npm run build`, required scoped ESLint and `git diff --check` passed. Existing build chunk-size advisory is unchanged. No final gate was skipped.
- The developer explicitly authorized `npm run test:merchant-knowledge:postgres`. Initial serial migrated PG17 run: **19 passed, 2 failed**, no skips. One existing malformed-configuration assertion expected DENIED rather than required nonretryable UNAVAILABLE. One pre-existing feature-preference setup transaction exceeded the fixture client's default five seconds (6,475ms), producing P2028. Corrected the assertion and increased only that suite's test-client transaction allowance to thirty seconds, leaving production transaction limits unchanged. Final serial rerun: **4 files, 21 passed, zero failed/skipped** using `npm run test:merchant-knowledge:postgres -- --maxWorkers=1 --no-file-parallelism --testTimeout=60000 --hookTimeout=240000`. Logs retain both initial failures rather than presenting them as passing evidence. Runner-only deadlines/serialization accommodate the local host; package scripts and production transaction limits remain unchanged.
- New ordering tests measured two actual UPDATE statements with affected counts [3,3] and two transaction controls for three sources. No-op equality/timestamps, exact-set conflict, rollback after a genuine P2010, and separate-connection Shop-lock barriers are asserted. Finalization suite uses separate clients/barriers for one-asset competition, lifecycle/count denial and durable postcommit pending work. All cases passed on canonical forward migrations in owned pgvector/pgvector:pg17 fixtures. Awaited teardown removed task-owned clients/containers; mounted-router tests clean roots/routers/timers. No unrelated resource was removed.

Same-fixture baseline comparison used the exact starting source `062777ceae29695314d6c7210bd88bdd11252153` and identical three-source inputs; temporary source/harness were removed. Unchanged order: before four ordering writes/six source methods, after zero writes/two source methods. Changed order: before four writes/six methods, after two writes/four methods. Counts exclude the separately controlled entitlement port and transaction statements, with zero provider calls. These are repository-call measurements, not emitted SQL or latency/capacity claims. Actual PostgreSQL counts/affected rows and mounted-router loader/action counts are recorded separately.

Final evidence logs: `/tmp/shopify008-unit-all-final.log` (81), `...-router-complete.log` (10), `...-postgres-final.log` (21), `...-preservation.log` (7), `...-types-final.log`, `...-build-final.log`, `...-lint-final.log`, `...-before-after.log` and `...-upload-final.log` (16-case subset, not additional passes). `/tmp/shopify008-postgres-initial.log` retains the 19-pass/two-failure run. Earlier install/generation/fixture/type/lint errors remain in initial logs. No live R2, Redis, Shopify or embedding call was used; external boundaries are controlled fixtures. All disposable clients/containers/timers are task-owned and cleaned by their harnesses.

### Provenance and Isolation

Launcher packet: dependency gate passed for SHOPIFY-001/007; canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-057-SHOPIFY-008`, prepared start `311086f7d5196e486e39a406890f2b25712f397e`. Implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-057-SHOPIFY-008`, start `062777ceae29695314d6c7210bd88bdd11252153`. Both newly created, both `task/ARCH-057-SHOPIFY-008`; both remote task fast-forwards not-needed and origin/main already current. Recursive submodule sync/update/init/verification passed; recorded/working Database pin `8e74634ff92be9900f693c0c449ffce888e7d617` unchanged.

Durable claim `b5f61f8de2fdfc9a0a8fb904727e41015fdc6d9f`, pushed at `2026-11-04T20:55:21Z`, Attempt 1, executor codex. Workspace bootstrap selected Node24.19.0/npm11.17.0. Installed Shared3.1.0, Prisma/client6.19.3, React Router7.18.2 and Vitest4.1.11 match the lockfile. No manual runtime or dependency upgrade. No shared/default checkout switched/edited, no other task worktree reused, no main merge or parent gitlink update. Final implementation `e41537919e2a639de4f036582555b79f29c521c6` is pushed to `origin/task/ARCH-057-SHOPIFY-008`; implementation checkout is clean. This report is submitted on the matching parent task branch with no gitlink staging. Its parent publication receipt is recorded after push below.

Parent publication receipt: report commit `df4a4f8d0647e0a9abdb655106b51be35d8a75b9` was pushed to `origin/task/ARCH-057-SHOPIFY-008`. This follow-up records that receipt only; no implementation or lifecycle change.

### Deviations, Assumptions and Unresolved Issues

No business-policy, schema or source/job identity deviation. Starting package syntax repair and fixture-only timeout correction are described above. Request presentation is never mutation authority. Test providers/queues are synthetic and migrations apply only to owned disposable PG17. All required validation passes; no unresolved implementation issue is identified in scope. No downstream task is started; acceptance remains with the architect.

### Architectural Concerns

None requiring a cross-repository amendment has been identified.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition only; no implementation accepted.

### Reviewed Files

Definition and latest unchanged knowledge/settings touchpoints.

### Validation Reviewed

Definition inspection only; actual implementation evidence outstanding.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

Return for architect review; do not execute enabled work.

## Architect Dependency Reconciliation (2026-11-04)

SHOPIFY-007 Attempt 1 is accepted and Complete at `e1533e4658e7e69eeb33e7efd6516211f0bcbe2e`; SHOPIFY-001 is also Complete. Both declared prerequisites are satisfied. This task is ready, unclaimed, at Attempt 0. Normal launcher preparation and source-integration gates remain required. No implementation is started by this promotion.
