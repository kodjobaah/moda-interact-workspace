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
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
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

Mandatory execution/logging/validation contract: `docs/architecture/ARCH-057/task-contract.md`. **Defined but not materialised.** Canonical destination: `docs/decisions/shopify/ARCH-057/SHOPIFY-008-simplify-merchant-knowledge-processing-and-refresh.md`.

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

- [ ] Migrate all knowledge actions to the minimal context-aware guard.
- [ ] Reuse settings read facts and preserve dormant source/activation semantics.
- [ ] Remove the two unused upload reads and implement zero-write no-op/two-statement order changes.
- [ ] Add cause-preserving unavailable/error mapping and complete the diagnostic matrix.
- [ ] Remove duplicate success revalidation and implement the fixed visibility/idle/deadline polling episode.
- [ ] Add exact mounted-router and migrated PostgreSQL proofs; register scripts and report emitted-log/query evidence.

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

- [ ] All eight actions perform no guard-only settings read for established valid tenants while retaining authenticated prerequisite repair; GET presentation reuses supplied scalar/plan/preference facts and retains global-feature fallback where necessary.
- [ ] OFF configuration and dormant/over-limit source management remain intact; indeterminate availability never masquerades as plan denial.
- [ ] Upload intent performs no activation read; validated-language finalization performs no default-language fallback read.
- [ ] Identical dense reorder has zero ordering writes; changed order has two SQL writes regardless of source count; delete compaction preserves unique contiguous positions and rollback.
- [ ] The actual pinned mounted router proves one automatic action refresh, no success-effect loop, no overlapping polls and a fixed60-second deadline across revalidation/visibility transitions. Plain-fetch upload still refreshes once.
- [ ] Database/provider unavailability maps to safe503 rather than403/400 misclassification; real missing object remains400, with original cause and safe provider evidence logged once.
- [ ] Concurrent source/order/finalize tests run on canonical migrated PG17 and preserve exact ownership, count limits, unique positions, one successful finalization and durable pending work after queue failure.
- [ ] Every failure-matrix row passes actual Shared JSON marker/code/cause/redaction/sink assertions, without source/provider/credential leakage to merchant DTOs.
- [ ] No new endpoint, schema, global cache, dependency, queue identity, user-facing English-only text or architecture-ID runtime name is introduced.

## Validation

- [ ] `npm run test:merchant-knowledge:unit` — include null/denied/unavailable entitlement, active/inactive/missing global Feature fallback, downgraded sources, no-op versus changed ordering, integer-range failure, unused-read absence, storage404/403/429/503/transport, postcommit continuation and complete diagnostic matrix.
- [ ] `npm run test:merchant-knowledge:router` — mounted actual installed `createMemoryRouter`/`RouterProvider` and hooks; record installed/locked version. Test all five fetcher operations, automatic revalidation, failed action, successful plain-fetch finalize, pending→active, repeated revalidations through60s, slow loader overlap, hidden/visible transitions, unmount and a later new episode. Do not mock useFetcher/useRevalidator or treat a hook stub as runtime proof.
- [ ] `npm run test:merchant-knowledge:postgres` — all own `pgvector/pgvector:pg17`, canonical migrations. New ordering suite proves overlapping reorder/reorder and both delete/reorder lock orders using separate connections/barriers, exact-set conflict and unchanged rows on no-op. New finalization suite proves two simultaneous finalizations of one asset have one committed source/revision, inactive-shop/count-limit denial leaves no partial rows, and postcommit activation/queue failure retains durable pending work. Provider/storage/queue boundaries are controlled fixtures, not live services. Missing Docker or skipped tests block validation.
- [ ] `npm test -- tests/unit/merchant-knowledge-url-validation.test.ts tests/unit/recovery-settings-i18n.test.ts` — URL restrictions and all existing locale keys remain valid.
- [ ] `npm run typecheck` and `npm run build`.
- [ ] `npx --no-install eslint app/services/merchant-knowledge app/routes/app/merchant-knowledge app/routes/app/recovery-settings/route.tsx app/components/settings/MerchantKnowledgeSection.tsx app/components/settings/MerchantKnowledgeUploadForm.tsx tests/unit/merchant-knowledge-actions.test.ts tests/unit/merchant-knowledge-read-model.test.ts tests/unit/merchant-knowledge-entitlement.test.ts tests/unit/merchant-knowledge-upload.test.ts tests/unit/merchant-knowledge-observability.test.ts tests/unit/merchant-knowledge-queue.test.ts tests/unit/merchant-knowledge-section.test.tsx tests/unit/merchant-knowledge-upload-form.test.tsx tests/unit/merchant-knowledge-read-context.test.ts tests/unit/merchant-knowledge-ordering.test.ts tests/unit/merchant-knowledge-r2-diagnostics.test.ts tests/integration/merchant-knowledge-router.test.tsx tests/integration/merchant-knowledge-source-lifecycle.integration.test.ts tests/integration/merchant-knowledge-upload.integration.test.ts tests/integration/merchant-knowledge-ordering.postgres.test.ts tests/integration/merchant-knowledge-finalization.postgres.test.ts tests/helpers/merchant-knowledge-router-fixtures.tsx tests/helpers/merchant-knowledge-postgres.ts tests/fixtures/settings-preview/main.tsx`.
- [ ] `git diff --check`; report same-fixture source method calls, emitted SQL/affected rows, router loader/action/poll counts and actual Shared records separately. Preserve safe original cause markers, no invented upstream fields, and owned-container/client/timer cleanup.

## Stop Condition

After all acceptance and mandatory validation pass, set review, complete the report and return to `moda_architect`. Stop on incompatible accepted context, missing Shared capability, actual installed-router mismatch requiring a version change, required schema change or different durable identity/processing semantics. Do not weaken tests, bypass tenant/lock checks or start downstream tasks.

## Implementation Notes

The read projection and transaction admission serve different purposes. Keep the latter fresh. A source list after plan downgrade is management data, not merely a list of currently usable sources. A pending revision is the durable work record; Redis is a postcommit hint. Two-phase order movement is required because unique positions are immediate, so replacing it with a direct swap is incorrect even inside a transaction. Timer stability is verified with actual router state, not guessed hook object identities.

## Completion Report

### Status

Not Started. Defined but not materialised; attempt 0, no claim/worktree/publication asserted.

### Files Changed

None. Definition only.

### Work Completed

None.

### Validation Results

Not run. Record exact scripts/cases, actual router and Shared versions, prepared worktree/source/Database pins, barrier/row/SQL evidence, source error/code/cause/redaction assertions, timer behavior and task-owned cleanup. Skipped checks remain outstanding.

### Deviations

None.

### Assumptions

Both dependencies are accepted and the launcher verifies current integrated source before execution.

### Unresolved Issues

Implementation and all required validation are outstanding.

### Architectural Concerns

Return ownership, schema, provider/queue identity, tenant policy, transaction or cross-repository changes to the architect.

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
