---
id: ARCH-063-SHOPIFY-001
architecture_id: ARCH-063
title: wire sdk refresh events and viable readiness
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-063-SHARED-002"]
enables: ["ARCH-063-SYSTEM-TEST-001"]
created: 2026-11-06
updated: 2026-11-07
---
# Wire sdk refresh events and viable readiness

## Architecture
ARCH-063; docs/architecture/ARCH-063-refreshable-shopify-status-and-safe-refresh-events.md. Coordinator moda_architect.

## Objective
Wire sdk refresh events and viable readiness using existing automatic coordinated refresh.

## Context
Metadata EXPIRED blocks authoring despite usable refresh; no safe refresh lifecycle events. Parent includes cross-service source audit and selected solution.

## Scope
moda-interact implementation/tests at exact touchpoints below; stale shared checkout is not a deployed observation.

| Existing file | Exact surface | Required change |
|---|---|---|
| moda-interact/app/services/shopify-offline-coordination.server.ts | createOfflineProvider/coordinated wrapper | Wire Shared hook to safe service adapter; emit SDK refresh lifecycle from ALS at outer commit, not storeSession. |
| moda-interact/app/services/shopify-session-storage.server.ts | transaction-bound storage | Expose scoped persisted-pair state to outer wrapper without logging tokens or declaring success. |
| moda-interact/app/services/shop/shop.service.ts | offline readiness near128–136 | Require future refresh expiry for expired access; preserve metadata-only admission. |
| moda-interact/app/services/observability/shopify-runtime-observability.server.ts | existing safe observability adapter | Add semantic refresh-event forwarding without raw SDK/provider error/body. |


## Out of Scope
Page-render refresh, manual credential entry, lock/recovery redesign, schema, topology, generic logger/metric framework and automatic task execution.

## Requirements
## Problem and audited behavior
Commerce src/studio/connections/provider-status.ts readProviderMetadata checks valid access then expired access and emits EXPIRED without checking usable refresh credentials. store-integration.tsx and provider-tool-handoff.ts permit AVAILABLE only, so users cannot reach the already automatic execution refresh. Selector components/studio-selected-shop-context.tsx renders an existence-only shopifyOfflineSessionAvailable boolean even for Woo. Existing expired-status tests encode this dead end. App shop.service.ts readiness near128–136 accepts refreshToken presence without refreshTokenExpires, giving the opposite false-positive. Shared offline-token-provider has coordinated refresh mechanics but no refresh events. These are local implementation observations, not deployed-state claims.

Canonical ARCH-061-MCP-001 implementation worktree session-reader.ts calls provider.getSession(shopId) without a premature expiry gate; shared submodule checkout may show old direct reads and is not proof of deployed behavior. Background shopify-session.service.ts delegates Shared getAccessToken; no access-expiry admission gate found. Commerce execution composition/local-policy-providers already call Shared; App SDK wrapper handles token refresh inside transaction scope. Audit fixes below preserve existing accepted locking/identity/recovery rather than reimplementing it.

## Exact functional decision
Add Commerce-local StoreIntegrationStatus REFRESHABLE. Keep EXPIRED for unusable refresh-required credentials, with label "Refresh or reconnection required" so a within-skew access token is not falsely described already expired. Both status and App readiness use the current helper's fixed 320000ms skew, test boundaries at exactly now+320000 and +320001; do not revert to an assumed five-minute constant. For an authorized ACTIVE Shopify shop with exactly one matching offline session, metadata AVAILABLE means nonempty access present with null expiry with no refresh token (the helper-supported nonexpiring state) or expires>now+320000ms. Access inside the helper's actual 320000ms refresh skew, including expired access, with refreshToken present/nonempty and refreshTokenExpires>now is REFRESHABLE. Access requiring refresh without usable refresh is EXPIRED; absent offline/access is MISSING, ambiguous or invalid mapping UNKNOWN/unavailable. Query refresh presence using DB predicates and explicit safe selects; never select/return token or decrypt. No page render/status read/network mutation. Readiness means credentials can be attempted, never live provider health. Display REFRESHABLE as "Ready to refresh automatically" and "Credentials refresh when a tool runs" with existing "Live connection not checked". No user refresh button, credential edit or reinstall requirement for REFRESHABLE.

Allow both AVAILABLE and REFRESHABLE for Shopify tool-authoring link and native tool preselection; Woo retains AVAILABLE and existing grant checks. Use one local isStoreIntegrationUsableForAuthoring predicate in provider-tool-handoff.ts and reuse in StoreIntegration. Test/save/live-test actions MUST independently resolve current selected Shop and execute via Shared getSession/getAccessToken; do not authorize from stale browser status, skip scope checks or refresh on save if existing save is metadata-only. Refresh happens only at actual provider execution. A stale REFRESHABLE hint can fail safely if refresh is revoked; stale AVAILABLE can refresh at execution after expiry. Existing pending async shop-switch results must never reopen another shop's link.

Selector header must show provider-specific metadata state from the same safe classifier: remove existence-only boolean as decision source, replace ShopExecutionContext field with `storeIntegration:{platform:'SHOPIFY'|'WOOCOMMERCE';status:StoreIntegrationStatus}|null` as Commerce-local contract. The production projection reuses readProviderMetadata; injected test fixtures updated. No cross-service wire schema. Unknown/no selection stays explicit; Woo never labelled Shopify session. Header and Connections agree without live checks.

App readiness function must use same logical credential viability: nonexpiring access with no refresh token OR access valid beyond now+320000ms OR access requiring refresh with nonempty refresh and refresh expiry strictly future; missing/expired refresh expiry is false. This remains metadata-only and does not replace actual Shared execution validation. Shared helper invalid-token semantics remain unchanged. MCP/Background direct helper callers require no new optimistic expiry precheck.

## Exact safe refresh-event contract
Shared factory gains optional `onEvent?:(event:ShopifyOfflineRefreshEvent)=>void` hook, exported from ./shopify/node. Hook failure is swallowed synchronously; async return is ignored and rejection suppressed; telemetry never changes return/transaction outcome. Event is frozen plain bounded object `{event:'shopify.offline_refresh.started'|'shopify.offline_refresh.committed'|'shopify.offline_refresh.failed';operationId:string;shopId:string|null;source:'SHARED'|'SDK';durationMs:number;outcome:'STARTED'|'COMMITTED'|'REJECTED'|'UNKNOWN'|'CANCELLED'|'UNAVAILABLE';reasonCode:ShopifyOfflineTokenErrorCode|null}`. No domain, session ID, token, scope, error/cause/body, OAuth client key/secret, endpoint or customer fields. operationId is a fresh UUID per attempted refresh, not caller text; duration monotonic elapsed rounded/clamped 0..60000. shopId derives trusted context; SDK bootstrap uses null until resolved, never a guessed domain as identifier.

For Shared getSession: emit started immediately before actual refresh dispatch after all eligibility checks; emit committed ONLY after interactive transaction commits successfully; emit failed once on rejection, cancellation, timeout, malformed response or persistence/commit ambiguity after start. Unknown after remote acceptance maps UNKNOWN/REFRESH_OUTCOME_UNKNOWN, never committed. Returning existing valid/nonexpiring credential emits no refresh event. Lock waiter rereading committed token emits none. Hook is not a competing logger: each service adapter forwards schema fields to existing @modainteract/moda-interact-shared/logging logger, info started/committed, warn failed. No raw Error attached. Exactly one terminal event per started attempt within a running process; process death can leave started without terminal, do not claim durable/exactly-once telemetry.

SDK-managed refresh/token exchange is not observable solely from Shared getSession. App coordination wrapper tracks bounded OAuth request intent in its existing ALS context: grant_type refresh_token emits same SDK started event; successful SDK credential persistence does not yet emit committed. Emit SDK committed only after outer coordinated transaction commits (including authenticated redirect commit); rejection/rollback/deadline/commit failure emits SDK failed. Token exchange acquisition is a distinct operation and MUST NOT be mislabeled refresh: no refresh event unless grant_type refresh_token. If SDK delegates to Shared refresh, source SHARED owns events and wrapper emits no duplicate. App creates service-owned event adapter reusing same exported event shape; no generic logger fork. Tests cover SDK refresh/store-success/commit-failure and redirect handling.

## Package/dependency and rollout
Shared implementation extends existing API compatibly; publication chooses next available approved semver and records exact version before consumer pins. No forced version guess or unpublished sibling import. Commerce UI correction is independent and Ready now; it uses existing accepted ARCH-060/061/062 contracts, does not wait for log publication. Shared logging implementation is also independently Ready. Consumer event wiring depends on Shared publication. App wiring includes metadata-readiness correction. System Test is terminal on all fixes; manually invoked after optional user exercise. Compatible rollout, no schema/credential/env or Render topology change. Logging absent in old binaries is expected until owning consumer deployed; do not assert deployed observability from local code. No new metric/span framework. Metadata reads and tooling never expose provider secrets.

## Work Items
- [ ] Wire Shared hook to safe service adapter; emit SDK refresh lifecycle from ALS at outer commit, not storeSession.
- [ ] Expose scoped persisted-pair state to outer wrapper without logging tokens or declaring success.
- [ ] Require future refresh expiry for expired access; preserve metadata-only admission.
- [ ] Add semantic refresh-event forwarding without raw SDK/provider error/body.

## Interfaces / Contracts
Commerce-local REFRESHABLE DTO/predicate and selector metadata, plus published optional Shared onEvent hook and exact frozen event schema above. Each consumer owns safe logger forwarding; provider/runtime credentials stay server-only. Exact version recorded by SHARED-002 before consumer pins.

## Dependencies
- ARCH-063-SHARED-002

## Enables
- ARCH-063-SYSTEM-TEST-001

## Acceptance Criteria
- [ ] SDK refresh start then successful store but commit rollback ->failed UNKNOWN only; redirect-success commit ->committed.
- [ ] Token exchange is not refresh; Shared-delegated refresh not double logged.
- [ ] Expired refresh present but expiry past/missing ->readiness false; valid refresh future ->true; zero refresh calls for readiness.

## Validation
- [ ] Run focused command `npx vitest run app/services/shopify-offline-coordination.server.test.ts`; explicitly create additional focused fixture files where required. Shared also runs disposable PostgreSQL offline-token-provider.postgres.test.ts postcommit/concurrency fixtures.
- [ ] Run owning declared typecheck/build appropriate to deployable change (Background build; System Test typecheck only); record exact commands. Capture event payloads with secret canaries and test hook failure isolation.

## Stop Condition
Complete defined work/criteria/validation, submit report for authorized review and STOP. Explicit developer completion required. System Test terminal/manually invoked; no enabled work auto-start.

## Implementation Notes
Execution ownership amendment (2026-11-07): developer explicitly requested agent implementation through `/moda-task ARCH-063-SHOPIFY-001` and authorized synchronization plus checkpoint/commit/push of already-started task-owned implementation, claim and report. Preserve eight uncommitted source files by explicit WIP checkpoint before canonical preparation; delegate to moda_app, completion_mode developer retained. Prior Attempt1 review/corrections binding; no claim/attempt increment here.

Dependency reconciliation (2026-11-06): ARCH-063-SHARED-002 is Accepted and explicitly developer-completed; published package @modainteract/moda-interact-shared@5.3.0 has verified downloadable immutable archive and Node hook exports. Task is Ready at unchanged Attempt 0, unclaimed. No automatic execution.

Use launcher-resolved isolated/synchronized task worktrees when execution requested. No implementation from definition. Preserve accepted locking/domain/SDK identities. Task-specific assertions are binding; no architecture selection delegated. Service logger uses published Shared logging, never raw provider/Prisma Error.

## Completion Report
### Status
Developer Self-Review — Changes Requested (2026-11-07). Attempt1 reviewed, unchanged; claim cleared and task Ready for canonical next attempt. No source edited or published during review.
### Files Changed
Eight uncommitted developer files: app/services/observability/shopify-runtime-observability.server.ts; app/services/shop/shop.service.ts; app/services/shopify-offline-coordination.server.test.ts; app/services/shopify-offline-coordination.server.ts; app/services/shopify-session-storage.server.ts; package.json/package-lock.json; tests/unit/services/shop.service.test.ts.
### Work Completed
Actual draft wires Shared hook/safe logger, tracks SDK refresh dispatch/store state and outer transaction outcomes, and corrects readiness320000ms/future-refresh logic. SDK event lifecycle and bounded intent parsing still need corrections below. No accepted implementation commit exists; HEADf14509f8c4feefe317b3dabb2a582f0dc9f688a2 is baseline and remote task implementation branch lookup returned no ref.
### Validation Results
- `npx vitest run app/services/shopify-offline-coordination.server.test.ts tests/unit/services/shop.service.test.ts`: PASS2 files55/55.
- Read-only actual diff reviewed by moda_architect with moda_app assistance; existing tests do not cover the three concrete gaps below.
- Initial cache write EPERM resolved by authorized test execution; no source changes.
- Broad typecheck/build not repeated because concrete correctness/publication requirements already fail. Required deployment-change validation must be recorded after correction before passing review.
### Deviations
Review-only request; uncommitted developer source left untouched, no unauthorized source commit/push.
### Assumptions
No deployed-state/provider behavior inferred from local unit fixtures.
### Unresolved Issues
Three SDK lifecycle/boundedness corrections plus committed/pushed implementation and final required validation remain before passing review.
### Architectural Concerns
Telemetry must not change refresh deadlines or claim successful remote outcome on ambiguous persistence. Preserve developer execution ownership and exact safe event contract.
### Git / VCS
Canonical workspace /Users/kwadwoadomafriyie/project/moda-interact-workspace; parent /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-063-SHOPIFY-001; implementation /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-063-SHOPIFY-001. Both branches task/ARCH-063-SHOPIFY-001. Parent clean before reconciliation; implementation eight task-owned uncommitted files. Review made no shared checkout/source/gitlink/main changes. No new claim/attempt increment or execution mode conversion. Parent review publication only; implementation not published.

## Architect Review
### Review Status
Pending
### Review Notes
Definition source audit completed; implementation not reviewed. Historical task acceptance preserved.
### Reviewed Files
Task touchpoints above; canonical MCP ARCH-061 reader inspected separately from stale shared checkout.
### Validation Reviewed
Task metadata/dependency/path checks only.
### Architecture Conformance
Single repository ownership; shared release gate explicit; independent Commerce correction not blocked on logging.
### Follow-up
None

## Developer Self-Review — Changes Requested (Attempt1, 2026-11-07)
Actual source reviewed, not inferred from commit messages. Existing focused55 tests pass but omit binding edge cases. Required corrections:

1. **One terminal per started SDK attempt** — shopify-offline-coordination.server.ts:247–255 overwrites binding/sdk closure single sdkRefreshAttempt on every dispatch; lines371–382 emit a terminal only for latest attempt. Track each actual attempt or explicitly terminate/reject a second dispatch safely so every started operationId gets exactly one terminal after correct transaction outcome. Add two-refresh-dispatch fixture in one authenticated callback; assert both operationIds have one terminal and commit failure emits no committed.
2. **Accepted remote outcome with deadline/commit ambiguity is UNKNOWN** — sdkRefreshFailure at lines164–171 checks DEADLINE before tokenOutcome succeeded/unknown, emitting CANCELLED/DEADLINE after remote acceptance. Preserve caller error behavior but map telemetry after accepted/unknown remote refresh to UNKNOWN/REFRESH_OUTCOME_UNKNOWN, never committed. Add accepted-response then outer deadline/rollback test and assert exact terminal code/outcome.
3. **Bound OAuth intent parsing** — isRefreshTokenGrant lines129–143 reads Request.clone().text() without byte/deadline bounds before dispatch. Use bounded abort-aware intent inspection (including string/URLSearchParams limits), do not consume original request, recheck cancellation/deadline before emitting started/network dispatch. Add oversized/never-ending or aborting streaming request fixture; prove bounded settlement, no premature dispatch/start and no secret/body logging.
4. **Durable implementation/validation evidence** — after corrections, run focused tests plus declared appropriate typecheck/build; commit/push reviewed task-owned source on matching implementation branch through developer-authorized publication, then reconcile exact hashes/report. Current eight source files are uncommitted and no remote task implementation ref exists, so passing review cannot be recorded. This review did not authorize/publish developer source.

State transition: in_progress -> Ready, executor/claimed_at null, Attempt1 preserved. Next canonical developer claim increments once via `/moda_developer_create ARCH-063-SHOPIFY-001`; do not convert execution mode or claim within review. No main/live/provider/deployment action performed.
