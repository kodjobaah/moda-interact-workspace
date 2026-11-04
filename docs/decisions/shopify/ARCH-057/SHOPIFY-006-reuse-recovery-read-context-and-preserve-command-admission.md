---
id: ARCH-057-SHOPIFY-006
architecture_id: ARCH-057
title: Reuse recovery read context while preserving command admission
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
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

# ARCH-057-SHOPIFY-006: Reuse recovery read context while preserving command admission

## Architecture

Architecture ID: `ARCH-057`. Architecture document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`. Coordinator: `moda_architect`.

Mandatory execution/logging/validation contract: `docs/architecture/ARCH-057/task-contract.md`. **Defined but not materialised.** Canonical destination: `docs/decisions/shopify/ARCH-057/SHOPIFY-006-reuse-recovery-read-context-and-preserve-command-admission.md`.

## Objective

Resolve recovery ownership once for a composed detail page, use narrow independent ownership reads for section resources, reuse an authoritative locked Shop row within human-command admission, and retain actionable diagnostics for recovery read/command failures.

## Context

Review F10 shows three repetitions of the large `ownedRecovery` projection in one detail load. F11 notes that command admission obtains Shop.status under lock and immediately rereads it. Recovery overview/list/detail/template fallbacks and command error classification discard operational evidence. These touchpoints share recovery presentation and command admission; no provider dispatch policy changes are selected.

The same-request context from SHOPIFY-001 is suitable for read presentation only. A fresh locked Shop/subscription/restriction/window/template check remains authoritative for a new command. Source-level call counts are not emitted SQL or performance measurements.

## Scope

All paths are relative to `moda-interact`.

| Existing path | Required edit |
|---|---|
| `app/services/recoveries/recovery-detail.server.ts` | Introduce the composed reader factory, private narrow section readers and independent narrow ownership resolver; preserve existing public readers/DTOs |
| `app/routes/app/recovery-detail/loader.server.ts` | Pass framework context, use one composed reader, preserve independent section states/statuses and template fallback |
| `app/routes/app/recovery-detail/state.ts` | Adjust type-only imports if required by the composed reader, without changing public DTO fields |
| `app/routes/app/recoveries/loader.server.ts` | Pass context to the guard and log operational read failures while preserving existing invalid/empty/never-used/error states |
| `app/routes/app/home/overview.server.ts` | Log overview read failures while retaining its existing safe error state and RepeatableRead reader |
| `app/services/recoveries/recovery-human-commands.server.ts` | Retain the locked Shop row and reuse it in local admission/catalogue checks; no other command state-machine changes |
| `app/services/recoveries/recovery-follow-up-catalogue.server.ts` | Accept the explicit trusted Shop snapshot below; retain independent fallback and every sender/publication/variant predicate |
| `app/routes/app/recovery-detail/command-http.server.ts` | Pass framework context; retain HTTP/origin/body bounds; log actual original operational errors including classified retry conflicts |
| `tests/unit/recovery-detail-readers.test.ts`, `tests/unit/recovery-detail-route.test.ts` | Verify one full owner projection, narrow standalone guards, section failures and unchanged DTOs |
| `tests/unit/recovery-list-route.test.ts`, `tests/unit/recovery-overview.test.ts`, `tests/unit/recovery-cohort-readers.test.ts` | Retain list/overview semantics and assert their diagnostic owners |
| `tests/unit/arch040-shopify-command.test.ts`, `tests/unit/arch040-shopify-http.test.ts`, `tests/unit/arch047-shopify-follow-up-catalogue.test.ts`, `tests/unit/arch047-shopify-follow-up-sender.test.ts` | Preserve admission/replay/CSRF/window/publication/private-claim contracts; assert locked-row reuse |
| `tests/fixtures/arch047-shopify-follow-up.ts` | Add fields returned by the locked Shop query to deterministic fixtures, without changing provider eligibility |
| `tests/integration/recovery-detail-query-plans.test.ts` | Extend actual-query composition/tenant cases; keep existing EXPLAIN and UNION limits |
| `package.json` | Add the exact unit/PostgreSQL scripts below |

New files:

- `app/services/recoveries/recovery-observability.server.ts`: a thin domain event adapter using Shared; no generic error serializer/logger.
- `tests/unit/recovery-reader-observability.test.ts`: emitted Shared output/cause/redaction/sink cases.
- `tests/unit/recovery-read-context.test.ts`: composition and authoritative Shop provenance cases, below 300 lines.

Existing `tests/helpers/recovery-detail-seed.mjs` and `tests/helpers/recovery-detail-pg-utc.mjs` are read-only reusable helpers unless a fixture correction strictly required by a named case is documented. No route topology change is needed: section/control/command/status resources remain top-level in `app/routes.ts`.

## Out of Scope

No provider send, Background worker, moderation, recipient reachability, service-window policy, command identity/idempotency, follow-up offer eligibility, table/index/migration or query-cache redesign. Do not remove message/related edge queries, the empty-list existence lookup, the overview RepeatableRead transaction, current template admission or independent resource guards. Do not change the command polling interval or merchant copy. Existing task identifiers in test filenames remain legitimate test provenance.

## Requirements

### R1 — detail composition and standalone ownership

1. Extract the existing owned-row-to-detail transformation into a pure private projection. Add `createRecoveryDetailReader(identity, database)` with the exact contract below. It executes the existing full `ownedRecovery` SQL once, returns null for unavailable ownership, and otherwise returns the existing detail DTO plus bound section-read methods. The callbacks close over server-resolved identifiers, not request JSON or a client DTO.
2. The detail loader calls that factory once, assigns only `reader.detail` into its public result and uses its bound methods through the existing independent `section` error boundary. It must not spread or serialize the reader/context/authentication object. For the normal branch with a conversation/customer and nonempty messages/related pages, the service composition is five raw SELECTs: owner1, message page1/edges1, related page1/edges1, replacing seven.
3. Keep `readRecoveryDetail`, `readRecoveryMessages` and `readRelatedRecoveries` compatible. Standalone message/related readers parse cursor/window syntax first and independently resolve tenant ownership with a narrow SELECT of recovery ID, customer ID and conversation ID. Retain recovery.shopId, customer same-shop join, RECOVERY conversation type and allowed same-shop/legacy-null conversation linkage. Do not fetch basket/control/outreach/moderation in that narrow resolver.
4. A standalone endpoint always calls `requireRecoveryHistory(request, context)` before its reader. Direct invocation cannot depend on the app parent executing. Invalid/missing/foreign resources retain existing 400/404/503 behavior and must not disclose another shop's record existence.
5. Preserve message ordering, tuple cursors, command-only attempts, linked-command exclusion, two UNION ALL arms each capped at51 and outer51, 50 visible messages, 5 related items and existing edge predicates. The read context is local composition, not a new transaction snapshot or cross-request cache.

### R2 — authoritative Shop reuse

6. Extend the existing Shop FOR UPDATE query in `lockedContext` to return `id,status,platform,defaultLanguageTag`. Retain that row as a private `lockedShop` field. `assertMerchantEnabled` checks its status rather than issuing another Shop findUnique. Retain the fresh transaction subscription/plan-feature read, human restriction, initial outreach, reachability, verified inbound/window and control-revision predicates.
7. Extend `readCurrentFollowUpTemplates` with an optional final `TrustedRecoveryShop` parameter as below. If supplied, verify that its ID equals the authenticated shopId and use its status/platform/language; otherwise keep the existing one Shop read. For the advisory detail page pass `merchant.shop` from SHOPIFY-001. For command admission pass only the current transaction's `lockedShop`. Never pass a cached request Shop into the mutation path.
8. Retain sender configuration, current variant and publication-target reads, no-offer-only policy, ambiguity checks, language preference, WABA/provider identity/hash checks and bounds. The UI list is advisory. The mutation still obtains a current catalogue inside its serializable transaction and Background still checks at dispatch. No provider/Redis/R2 call is introduced inside that transaction.
9. Preserve replay-before-new-admission behavior, payload hashes, public retry key, private UUID follow-up claim, atomic sequence2 claim, command creation, lock order and existing HTTP outcomes. A replay does not allocate a new command/claim. New text and follow-up paths save only the redundant Shop reads specified here.

### R3 — complete recovery diagnostics without changing UI contracts

10. Every production loader/action owned here passes actual framework `context` to SHOPIFY-001's guard. Auth/context failures remain owned by SHOPIFY-001; do not log the same source error again at rethrow-only callers.
11. Use `resolveDeploymentEnvironmentName()` with Shared logging in the new recovery semantic adapter. Retain original safe exception/cause and actual Prisma code rather than only `errorType` or `internal_error`. Do not log message/basket/customer content, recipient, idempotency payload, raw URL/header, sender credentials or template configuration body.
12. Preserve existing Responses/redirects and invalid-query/business-denial behavior. A known P2002/P2034 retains the current 409 `conflict_retry` response but records the actual error at warn; an unexpected failure retains safe 503 and records error. No fabricated command success or automatic unbounded retry.

| Failure/injection | Owner and log fields | Required behavior |
|---|---|---|
| Overview summary/preview DB error | Overview boundary; fixed operation, trusted shopId, original safe error/code/causes | Existing `state:error`; no fake zero totals |
| List page/existence DB error | List loader | Existing error state/filters/embed retained |
| Detail full ownership DB error | Detail loader | One original diagnostic, HTTP503/detail error |
| Message/related page or edge error | Section wrapper with explicit section/identity context | Only affected section errors; standalone503; no swallowed source error |
| Template config/variant/publication read failure | Detail template fallback | Log original failure; retain history and empty advisory templates, never guess a template |
| Command/control/status DB exception, including P2002/P2034 | `handleFailure` via semantic adapter | Original safe message/code/cause once; existing409/503 contract |
| Invalid configured app URL with actual URL-parser cause | Configuration/command boundary | Original internal cause, safe503, no configuration value or header leak |
| Missing app URL, invalid JSON/cursor, foreign ID, permission or origin denial | Existing business/configuration classification | No invented provider error; original internal error only where one exists |
| Throwing Shared sink | Shared isolation | Response, rollback, replay and admission decisions unchanged |

## Work Items

- [ ] Add one-owner detail factory and narrow independent resource ownership.
- [ ] Wire loader composition and actual framework context without serializing server context.
- [ ] Reuse the locked Shop row and trusted read-only Shop snapshot at the specified catalogue callers.
- [ ] Preserve all paging/command/admission invariants and add complete recovery diagnostic ownership.
- [ ] Add/update focused tests, register scripts and record actual query evidence.

## Interfaces / Contracts

Consume `ARCH-057-SHOPIFY-001`: `requireRecoveryHistory(request, context?)` retains existing fields and adds server-only `merchant`. All owned production callers pass `context`; optional fallback is for existing direct tests/helpers only.

New/extended server-only contracts in existing recovery service modules:

```ts
type RecoveryIdentity = { shopId: string; recoveryId: string };
type SectionNavigation = { cursor?: unknown; window?: unknown };

createRecoveryDetailReader(
  identity: RecoveryIdentity,
  database?: RecoveryDetailDatabase,
): Promise<null | {
  detail: NonNullable<Awaited<ReturnType<typeof readRecoveryDetail>>>;
  readMessages(navigation?: SectionNavigation): ReturnType<typeof readRecoveryMessages>;
  readRelated(navigation?: SectionNavigation): ReturnType<typeof readRelatedRecoveries>;
}>;

type TrustedRecoveryShop = Pick<Shop, "id" | "status" | "platform" | "defaultLanguageTag">;
readCurrentFollowUpTemplates(
  shopId: string,
  languageTag: string | null,
  database?: CatalogueDatabase,
  trustedShop?: TrustedRecoveryShop,
): Promise<FollowUpTemplateChoice[]>;
```

Implement the return types with non-recursive named DTO aliases as needed; the factory must not call a public reader that re-resolves ownership. Bound private methods accept only navigation, never replacement tenant/recovery IDs. Existing public DTOs are unchanged.

Add exact package scripts:

```json
{
  "test:recovery-readers:unit": "vitest run tests/unit/recovery-read-context.test.ts tests/unit/recovery-reader-observability.test.ts tests/unit/recovery-detail-readers.test.ts tests/unit/recovery-detail-route.test.ts tests/unit/recovery-list-route.test.ts tests/unit/recovery-overview.test.ts tests/unit/recovery-cohort-readers.test.ts tests/unit/arch040-shopify-command.test.ts tests/unit/arch040-shopify-http.test.ts tests/unit/arch047-shopify-follow-up-catalogue.test.ts tests/unit/arch047-shopify-follow-up-sender.test.ts",
  "test:recovery-readers:postgres": "MODA_RECOVERY_DETAIL_POSTGRES=1 vitest run tests/integration/recovery-detail-query-plans.test.ts"
}
```

## Dependencies

- ARCH-057-SHOPIFY-001

## Enables

- ARCH-057-SHOPIFY-011

## Acceptance Criteria

- [ ] Normal detail composition performs one full owner query/five raw data SELECTs, with unchanged messages/related/detail output.
- [ ] Standalone resources remain independently authorized and use one narrow tenant ownership read; foreign/missing resources and cursor scopes retain behavior.
- [ ] Actual PostgreSQL query-plan cases retain bounded UNION arms and indexed keyset access; no application-loop per-row query is introduced.
- [ ] The mutation reuses only its own locked Shop and retains all current admission/replay/follow-up checks and durable identities.
- [ ] The advisory catalogue and transactional catalogue use their distinct authoritative Shop sources; missing optional snapshot still performs the existing fallback read.
- [ ] Every listed operational failure emits original safe message/code/cause through real Shared logging, without internal details in merchant DTOs.
- [ ] Existing recovery copy/locales, safe error states, independent section rendering and command response/status behavior remain unchanged.

## Validation

- [ ] `npm run test:recovery-readers:unit` — include one-owner count, no-conversation/no-customer/empty cases, malformed/foreign cursor cases, context spoof rejection, locked INACTIVE status denial, replay and missing-publication denial, and every failure-matrix case.
- [ ] `npm run test:recovery-readers:postgres` — existing own `pgvector/pgvector:pg17` with canonical migrations; execute composition with real SQL, separate-tenant/inconsistent legacy links, first/next/previous/latest pages and command-only attempts. Record actual EXPLAIN output; skipped/container-unavailable is blocked, not passed.
- [ ] `npm test -- tests/unit/arch040-shopify-command-status.test.tsx tests/unit/arch040-shopify-layout.test.tsx tests/unit/arch047-shopify-follow-up-ui.test.tsx` — presentation/status/advisory-choice regression, no runtime loop claim from mocked hooks.
- [ ] `npm run typecheck` and `npm run build`.
- [ ] `npx --no-install eslint app/services/recoveries/recovery-detail.server.ts app/services/recoveries/recovery-human-commands.server.ts app/services/recoveries/recovery-follow-up-catalogue.server.ts app/services/recoveries/recovery-observability.server.ts app/routes/app/recovery-detail/loader.server.ts app/routes/app/recovery-detail/command-http.server.ts app/routes/app/recovery-detail/state.ts app/routes/app/recoveries/loader.server.ts app/routes/app/home/overview.server.ts tests/unit/recovery-read-context.test.ts tests/unit/recovery-reader-observability.test.ts tests/unit/recovery-detail-readers.test.ts tests/unit/recovery-detail-route.test.ts tests/unit/recovery-list-route.test.ts tests/unit/recovery-overview.test.ts tests/unit/recovery-cohort-readers.test.ts tests/unit/arch040-shopify-command.test.ts tests/unit/arch040-shopify-http.test.ts tests/unit/arch047-shopify-follow-up-catalogue.test.ts tests/unit/arch047-shopify-follow-up-sender.test.ts tests/fixtures/arch047-shopify-follow-up.ts tests/integration/recovery-detail-query-plans.test.ts`.
- [ ] `git diff --check`; record same-fixture before/after method calls, raw SQL and outcomes separately from transaction statements and provider work. Capture actual Shared JSON and cleanup.

## Stop Condition

When all required work and validation are complete, set review and return to `moda_architect`. Stop if removing a read would change tenant/command/publication authority, require schema changes or change provider/Background contracts. Do not weaken a failing predicate to meet a call budget or start follow-on tasks.

## Implementation Notes

The reader factory is a small same-module composition mechanism, not a new repository framework. Current row locks and transaction reads are safety boundaries, not generic duplication. A raw ownership query is replaced by a narrower one only on independently authenticated resources; it is removed only where the composed page already holds the trusted result. Preserve intentional RepeatableRead aggregation and message edge queries.

## Completion Report

### Status

Not Started. Defined but not materialised; attempt 0, no execution claim.

### Files Changed

None. Definition only.

### Work Completed

None.

### Validation Results

Not run. Record exact commands, required cases, installed packages, prepared worktrees/source pins, actual SQL/plan and Shared-log evidence, failure/outcome preservation and owned-resource cleanup.

### Deviations

None.

### Assumptions

The launcher verifies the accepted prerequisite and actual integrated runtime before claiming execution.

### Unresolved Issues

Implementation and required evidence are outstanding.

### Architectural Concerns

Return ownership, schema, transaction, public DTO, identity, queue or provider changes to the architect.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition only; no implementation accepted.

### Reviewed Files

Definition and latest unchanged recovery touchpoints.

### Validation Reviewed

Definition inspection only; implementation evidence outstanding.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

Return for architect review; do not start enabled work.
