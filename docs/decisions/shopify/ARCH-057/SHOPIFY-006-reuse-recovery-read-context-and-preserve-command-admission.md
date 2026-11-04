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

# ARCH-057-SHOPIFY-006: Reuse recovery read context while preserving command admission

## Architecture

Architecture ID: `ARCH-057`. Architecture document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`. Coordinator: `moda_architect`.

Mandatory execution/logging/validation contract: `docs/architecture/ARCH-057/task-contract.md`. Materialised through the prepared launcher for Attempt 1. Canonical task: `docs/decisions/shopify/ARCH-057/SHOPIFY-006-reuse-recovery-read-context-and-preserve-command-admission.md`.

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
| `app/services/platform-configuration/contracts.server.ts` | Add an optional standard Error cause to the existing typed configuration error/helper while preserving existing constructor/helper callers, wrapper name, key, code and message |
| `app/services/platform-configuration/repository.server.ts` | Retain the original database exception as the cause of the existing DATABASE_UNAVAILABLE wrapper; preserve all query, validation and failure classifications |
| `tests/unit/platform-configuration/service.test.ts` | Assert original database cause identity and the existing configuration classifications/fallback contracts |
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

### Architect scope clarification — configuration database cause, 2026-11-04

R3 includes the original database failure underlying sender-configuration reads. Inspection found that `readPlatformConfiguration` currently catches and discards that exception before creating `ShopifyPlatformConfigurationError` with `DATABASE_UNAVAILABLE`. The three scope additions above authorize only preserving the exception through the standard server-only Error cause mechanism and verifying it through the existing tests. Existing callers that supply no cause remain compatible. Preserve the wrapper classification and public safe responses, and let the existing Shared logging projection serialize/redact the cause at the recovery boundary. Retain the actual safe Prisma/provider code on that cause. The already scoped recovery semantic adapter may select the original cause for diagnostic emission only when the supplied error is the existing ShopifyPlatformConfigurationError classified DATABASE_UNAVAILABLE and has a cause. This prevents the wrapper classification from hiding the actual database code in the Shared output. Preserve the typed wrapper for propagation and HTTP/business classification. Use Shared serialization/redaction without adding a generic serializer or recursively unwrapping arbitrary errors. Verify the actual catalogue-to-sender-to-repository path, original cause identity and emitted safe database code in the existing recovery observability test. Do not add raw configuration values, credentials, request payloads or diagnostics to merchant DTOs.

`app/services/recoveries/recovery-follow-up-sender.server.ts` remains a read-only consumer for this clarification. Its current non-MISSING error path already rethrows the typed error, while only MISSING permits the established environment fallback. Prove cause preservation through that existing path using the already scoped sender test and real Shared capture-output test. Do not change sender eligibility, fallback policy, seal/keyring behavior, database access or configuration validation. This amendment changes implementation scope only and leaves review pending.

## Work Items

- [x] Add one-owner detail factory and narrow independent resource ownership.
- [x] Wire loader composition and actual framework context without serializing server context.
- [x] Reuse the locked Shop row and trusted read-only Shop snapshot at the specified catalogue callers.
- [x] Preserve all paging/command/admission invariants and add complete recovery diagnostic ownership.
- [x] Add/update focused tests, register scripts and record actual query evidence.

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

- [x] Normal detail composition performs one full owner query/five raw data SELECTs, with unchanged messages/related/detail output.
- [x] Standalone resources remain independently authorized and use one narrow tenant ownership read; foreign/missing resources and cursor scopes retain behavior.
- [x] Actual PostgreSQL query-plan cases retain bounded UNION arms and indexed keyset access; no application-loop per-row query is introduced.
- [x] The mutation reuses only its own locked Shop and retains all current admission/replay/follow-up checks and durable identities.
- [x] The advisory catalogue and transactional catalogue use their distinct authoritative Shop sources; missing optional snapshot still performs the existing fallback read.
- [x] Every listed operational failure emits original safe message/code/cause through real Shared logging, without internal details in merchant DTOs.
- [x] Existing recovery copy/locales, safe error states, independent section rendering and command response/status behavior remain unchanged.

## Validation

- [x] `npm run test:recovery-readers:unit` — include one-owner count, no-conversation/no-customer/empty cases, malformed/foreign cursor cases, context spoof rejection, locked INACTIVE status denial, replay and missing-publication denial, and every failure-matrix case.
- [x] `npm run test:recovery-readers:postgres` — existing own `pgvector/pgvector:pg17` with canonical migrations; execute composition with real SQL, separate-tenant/inconsistent legacy links, first/next/previous/latest pages and command-only attempts. Record actual EXPLAIN output; skipped/container-unavailable is blocked, not passed.
- [x] `npm test -- tests/unit/arch040-shopify-command-status.test.tsx tests/unit/arch040-shopify-layout.test.tsx tests/unit/arch047-shopify-follow-up-ui.test.tsx` — presentation/status/advisory-choice regression, no runtime loop claim from mocked hooks.
- [x] `npm run typecheck` and `npm run build`.
- [x] `npx --no-install eslint app/services/recoveries/recovery-detail.server.ts app/services/recoveries/recovery-human-commands.server.ts app/services/recoveries/recovery-follow-up-catalogue.server.ts app/services/recoveries/recovery-observability.server.ts app/routes/app/recovery-detail/loader.server.ts app/routes/app/recovery-detail/command-http.server.ts app/routes/app/recovery-detail/state.ts app/routes/app/recoveries/loader.server.ts app/routes/app/home/overview.server.ts tests/unit/recovery-read-context.test.ts tests/unit/recovery-reader-observability.test.ts tests/unit/recovery-detail-readers.test.ts tests/unit/recovery-detail-route.test.ts tests/unit/recovery-list-route.test.ts tests/unit/recovery-overview.test.ts tests/unit/recovery-cohort-readers.test.ts tests/unit/arch040-shopify-command.test.ts tests/unit/arch040-shopify-http.test.ts tests/unit/arch047-shopify-follow-up-catalogue.test.ts tests/unit/arch047-shopify-follow-up-sender.test.ts tests/fixtures/arch047-shopify-follow-up.ts tests/integration/recovery-detail-query-plans.test.ts`.
- [x] `npm test -- tests/unit/platform-configuration/service.test.ts` and scoped ESLint for the three newly allowed files. Verify original DB cause identity, unchanged wrapper classification and MISSING-only sender fallback, plus real Shared output containing the harmless source marker/actual code and excluding injected sensitive spans.
- [x] `git diff --check`; record same-fixture before/after method calls, raw SQL and outcomes separately from transaction statements and provider work. Capture actual Shared JSON and cleanup.

## Stop Condition

When all required work and validation are complete, set review and return to `moda_architect`. Stop if removing a read would change tenant/command/publication authority, require schema changes or change provider/Background contracts. Do not weaken a failing predicate to meet a call budget or start follow-on tasks.

## Implementation Notes

The reader factory is a small same-module composition mechanism, not a new repository framework. Current row locks and transaction reads are safety boundaries, not generic duplication. A raw ownership query is replaced by a narrower one only on independently authenticated resources; it is removed only where the composed page already holds the trusted result. Preserve intentional RepeatableRead aggregation and message edge queries.

## Completion Report

### Status

Attempt 1 implemented, validated and submitted for independent architect review. Status: review; no acceptance or completion decision is asserted. Implementation commit: `99f00a1` on `task/ARCH-057-SHOPIFY-006`.

### Files Changed

Nineteen implementation files, all within the original scope or the architect's 2026-11-04 cause-preservation amendment:

- Detail service/loader: pure detail projection, one full-owner factory, navigation-only bound section readers, narrow independently guarded section ownership, existing DTOs and edge queries.
- Human-command service/current catalogue: private transaction-locked Shop snapshot, retained fresh subscription checks, trusted advisory Shop snapshot and independent fallback. Existing fourth-argument sender injection remains supported for existing server test callers; production uses the explicit trusted Shop object.
- Recovery semantic adapter, list/overview/detail/command HTTP boundaries: original safe diagnostics, section/recovery identity, retry-conflict warning and unchanged responses. Invalid app-URL diagnostics use the actual parser error and internal configuration origin without logging its input.
- Approved platform-configuration contracts/repository: optional standard ErrorOptions cause, unchanged typed wrapper name/key/code/message and MISSING-only fallback. The recovery adapter selects only the original cause of the named DATABASE_UNAVAILABLE wrapper for diagnostic emission; it does not unwrap arbitrary errors. Sender implementation remains read-only.
- Exact package scripts; existing unit/route/command/sender/configuration fixtures and PostgreSQL query-plan suite; three new declared files. New file sizes: adapter 18 lines, context tests 89 lines, emitted-output tests 125 lines.

### Work Completed

All work items and acceptance criteria are satisfied by implementation and the validation below, subject to independent architect review.

The composed detail loader resolves full ownership once and serializes only its existing detail DTO. Standalone resources still authenticate independently, parse navigation before querying ownership, and retain same-shop customer and same-shop/legacy-null RECOVERY conversation predicates. Message UNION arms, limits, tuple ordering, command-only exclusion and edge queries remain intact.

Mutation admission reuses only its current transaction's locked Shop. Replay order, fresh plan/features, restriction/window/reachability, publication eligibility, sequence-two claim, private UUID/public retry identity and existing transaction/HTTP behavior remain intact. Advisory request context is never mutation authority. The non-ACTIVE lock denial uses the canonical SUSPENDED enum; the schema has no INACTIVE enum value.

The existing framework context continues through every selected guard. Each selected fallback/command boundary owns its diagnostic. Actual sender configuration failures now preserve the original exception across the existing typed boundary, with real Shared serialization/redaction and sink isolation. No provider/Redis/R2 work was introduced inside admission.

### Validation Results

Final amended-source checks passed:

- `npm run test:recovery-readers:unit`: **289 tests across 11 files**, none skipped. The existing optional cohort SQL case was enabled against an additional task-owned disposable PostgreSQL database; it is separate from the canonical migrated detail suite.
- `npm run test:recovery-readers:postgres`: **8 tests**, all executed on PostgreSQL 17.11 using `pgvector/pgvector:pg17` and the canonical forward migration sequence. Covered identical composed DTOs, foreign/missing resources, inconsistent customer/conversation links, legacy-null conversation links, first/next/previous/latest pagination, bounded/indexed EXPLAIN plans and command-only attempts. Later changes concerned asynchronous rejection semantics and configuration cause propagation, with no SQL changes.
- Required command-status/layout/follow-up presentation regressions: **85 tests**.
- Amendment validation `npm test -- tests/unit/platform-configuration/service.test.ts`: **8 tests**, including original cause identity and unchanged wrapper contract. Existing sender tests also prove MISSING-only fallback and retained original DB cause.
- Required original lint scope plus all three amendment files; typecheck; production build; `git diff --check`: passed. Existing client chunk-size warning remains non-fatal.
- Full emitted-output failure matrix covers owner/message/related/template/list/existence/overview failures, actual page/edge failures, command/control/status errors, P2002/P2034 warnings, original URL-parser errors, context/control-flow denials and throwing sinks. Real catalogue → sender → configuration repository coverage verifies unchanged empty advisory templates/HTTP success and actual safe database evidence.

Same-fixture evidence:

| Operation | Starting implementation | Final implementation | Evidence and outcome |
|---|---|---|---|
| Detail + messages + related | 3 public reader calls, 7 raw SELECTs, 3 full owner projections | 1 factory + 2 bound section calls, 5 raw SELECTs, 1 full owner projection | Starting commit executed in a temporary baseline probe on the same canonical migrated fixture; 50 messages/5 related rows; final DTO equality; no transaction-control statements or provider calls |
| New text admission | 1 ORM Shop read plus 1 Shop lock | 0 ORM Shop reads plus 1 Shop lock | Same deterministic fixture and source-baseline command implementation; fresh subscription read remains 1; durable ACCEPTED outcome |
| New follow-up admission | 2 ORM Shop reads plus 1 Shop lock | 0 ORM Shop reads plus 1 Shop lock | Same fixture; subscription remains 1, publication and sequence-two checks retained; durable ACCEPTED outcome |

Command counts are mocked repository-method evidence, not emitted SQL or latency measurements. The separate real PostgreSQL composition case records seven compatibility-reader SELECTs versus five composed SELECTs and identical output. Each of the four message-page EXPLAIN cases retains the indexed ConversationMessage keyset scan and three LIMIT 51 clauses (two UNION sources and outer page). Full actual EXPLAIN JSON is retained in the PostgreSQL log.

Representative fields from captured actual Shared output:

```json
{"operation":"read_detail","stage":"read_detail","origin":"database","shopId":"shop-1","identities":{"recoveryId":"owned-recovery"},"error":{"name":"Error","message":"original recovery marker [REDACTED] [REDACTED]"},"causeChain":[{"name":"Error","message":"original cause [REDACTED]"}],"databaseCode":"P2010","redactionApplied":true,"truncated":false}
```

Logs under `/tmp/arch057-shopify006-`: `amended-unit.log`, `postgres.log`, `ui.log`, `amended-config.log`, `amended-lint.log`, `amended-types.log`, `amended-build.log`, `baseline-command.log`, `baseline-postgres.log`. Baseline probes selected one proof case each; their filtered/skipped cases are not counted as completed suites. Temporary baseline source/test edits were restored and removed.

Earlier evidence is retained: the first focused run had the existing optional cohort DB case skipped before its disposable fixture was enabled; three new test type errors were corrected. The real sender-configuration probe failed twice before the approved amendment (`config-before.log`), proving the discarded cause; both cases pass in the final 289-test suite. No earlier failed/skipped run is presented as passing evidence.

Resource cleanup awaited only owned container/client shutdowns, including the baseline and optional cohort containers. No shared Docker pruning, live Shopify request, persistent migration/import or provider send was performed.

### Source and Prepared Launcher Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-057-SHOPIFY-006`; implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-057-SHOPIFY-006`; both branches `task/ARCH-057-SHOPIFY-006`.
- Both dedicated worktrees created by the launcher; shared/default checkouts were not switched or mutated; no previous task worktree reused.
- Starting parent `df683a2f5c78e2314b5ffa84989567ebaf8531f1`; implementation `de5650e73df91e4d52bbcb4131dd80d1c7a7d339`. Attempt 1 claim `745c6cd62326d264dcbc0f3d6ec2bba1f53bde26`, executor codex, claimed `2026-11-04T20:04:52Z`, committed/pushed by launcher after prerequisite SHOPIFY-001 passed.
- Parent and implementation remote task fast-forward: not needed; origin/main already current in both, as recorded by preparation. No preparation/claim was repeated.
- Recursive submodule sync/update passed. Recorded and final working Database pin: `8e74634ff92be9900f693c0c449ffce888e7d617`. Database/schema/gitlinks unchanged.
- Node 24.19.0, npm 11.17.0, Prisma client 6.19.3, Vitest 4.1.11, installed Shared 3.1.0; pinned installation through npm ci. No dependency upgrade or lockfile change.

### Deviations

Only the architect-authored 2026-11-04 scope amendment documented in R3 and the scope table. No business policy, sender behavior, schema, locale, command identity, route topology or provider/Background contract changed.

### Assumptions

Request-context Shop is advisory; the current transaction's locked Shop and fresh subscription/catalogue remain admission authority. Source-level method counts are distinguished from real SQL; no throughput/latency claim is made.

### Unresolved Issues

No known implementation/validation gap within the amended scope. Independent architect review remains outstanding. No downstream task was started or promoted.

### Architectural Concerns

The scoped discarded-cause issue was returned to moda_architect and resolved under its written amendment. No further cross-repository, schema or authority change was needed. Domain index, frontier, main branches and parent implementation gitlink remain outside this implementation handoff.

## Architect Review

### Review Status

**Accepted — Attempt 1, 2026-11-04.** No blocking findings identified in implementation `99f00a1`. Task is `complete` under automatic completion mode; executor and claim cleared, Attempt 1 preserved. Acceptance relies on inspected source, independently executed focused tests, and the submitted PostgreSQL/build/typecheck/lint evidence with the limits below.

### Reviewed Source and Conformance

Reviewed the task requirements and scope amendment; composed detail reader and narrow standalone ownership checks; loader/section routing; locked Shop reuse and current follow-up catalogue admission; command HTTP outcomes; configuration cause preservation; recovery diagnostics and their actual Shared output tests.

The composed reader retains server-resolved identity and serializes only the existing detail DTO. Standalone readers retain tenant predicates and navigation validation. Command admission uses the current transaction's locked Shop, preserves subscription/restriction/window/publication checks and replay semantics, and does not use the advisory request Shop for mutations. Typed configuration failures preserve their original database cause; recovery diagnostics retain safe source wording/code/cause and isolate sink failures. No blocking defect was found within the reviewed scope.

### Independent Validation and Limits

- Executed `npm run test:recovery-readers:unit` from the dedicated implementation worktree using Node 24.19.0: **11 files passed, 288 tests passed, 1 optional database case skipped (289 total)**. The skip is not counted as a pass. Local log: `/tmp/arch057-shopify006-review-unit.log` (not a committed artifact).
- Observed actual Shared JSON with original safe error/cause, redaction applied, and database code P2010; the focused suite covers source boundaries, conflict warning levels, configuration-cause propagation and throwing sinks.
- Implementation comparison whitespace check passed.
- Reviewed submitted evidence of **289/289 focused tests** with the optional cohort database enabled separately, **8 canonical PostgreSQL/query-plan tests**, **85 presentation regressions**, **8 configuration tests**, build, typecheck and scoped lint. These were not independently rerun except for the focused command above. PostgreSQL evidence includes same-fixture DTO equality and reduction from seven raw SELECTs/three full owner projections to five SELECTs/one full owner projection; no throughput claim is inferred.
- Reviewed worktree/preparation evidence in the Completion Report. Parent review worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-057-SHOPIFY-006`; implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-057-SHOPIFY-006`, both on `task/ARCH-057-SHOPIFY-006`.

### Follow-up and Publication

No implementation correction required by this review. SHOPIFY-011 retains its other prerequisites and is not promoted or executed here. Integrated architecture validation remains with the terminal system-test task. This acceptance does not mark ARCH-057 implemented.

The developer authorized committing and pushing this review on 2026-11-04. Only parent documentation is published; no implementation code, database schema or gitlink is changed, and no task branch is merged into main.
