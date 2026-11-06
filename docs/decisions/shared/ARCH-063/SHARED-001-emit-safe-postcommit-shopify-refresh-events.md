---
id: ARCH-063-SHARED-001
architecture_id: ARCH-063
title: emit safe postcommit shopify refresh events
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: review
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: ["ARCH-063-SHARED-002"]
created: 2026-11-06
updated: 2026-11-06
---
# Emit safe postcommit shopify refresh events

## Architecture
ARCH-063; docs/architecture/ARCH-063-refreshable-shopify-status-and-safe-refresh-events.md. Coordinator moda_architect.

## Objective
Emit safe postcommit shopify refresh events using existing automatic coordinated refresh.

## Context
Metadata EXPIRED blocks authoring despite usable refresh; no safe refresh lifecycle events. Parent includes cross-service source audit and selected solution.

## Scope
moda-interact-shared implementation/tests at exact touchpoints below; stale shared checkout is not a deployed observation.

| Existing file | Exact surface | Required change |
|---|---|---|
| moda-interact-shared/src/shopify/offline-token-provider.ts | factory/getSession/runLocked | Add optional safe hook and exact schema/timing/error event contract; do not alter refresh/lock/recovery mechanics. |
| moda-interact-shared/src/shopify/index.ts | Node-only exports | Export event type/code types for consumer adapters; retain browser boundary. |
| moda-interact-shared/src/shopify/offline-token-provider.test.ts | unit fixtures | Assert safe payload, no reuse events, hook isolation and terminal categories. |
| moda-interact-shared/src/shopify/offline-token-provider.postgres.test.ts | commit/concurrency fixtures | Assert success only after actual commit and one normal refresh attempt for independent clients. |


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
- [x] Add optional safe hook and exact schema/timing/error event contract; do not alter refresh/lock/recovery mechanics.
- [x] Export event type/code types for consumer adapters; retain browser boundary.
- [x] Assert safe payload, no reuse events, hook isolation and terminal categories.
- [x] Assert success only after actual commit and one normal refresh attempt for independent clients.

## Interfaces / Contracts
Commerce-local REFRESHABLE DTO/predicate and selector metadata, plus published optional Shared onEvent hook and exact frozen event schema above. Each consumer owns safe logger forwarding; provider/runtime credentials stay server-only. Exact version recorded by SHARED-002 before consumer pins.

## Dependencies
None

## Enables
- ARCH-063-SHARED-002

## Acceptance Criteria
- [x] Committed observer can read new expiry/pair from second client; save/commit failure never emits committed.
- [x] Two clients same expired row ->one started+committed; waiting reuse ->no event.
- [x] Token/body/error canaries absent; throwing/rejecting callback cannot fail business call.

## Validation
- [x] Run focused command `npx tsx --test src/shopify/offline-token-provider.test.ts`; explicitly create additional focused fixture files where required. Shared also runs disposable PostgreSQL offline-token-provider.postgres.test.ts postcommit/concurrency fixtures.
- [x] Run owning declared typecheck/build appropriate to deployable change (Background build; System Test typecheck only); record exact commands. Capture event payloads with secret canaries and test hook failure isolation.

## Stop Condition
Complete defined work/criteria/validation, submit report for authorized review and STOP. Explicit developer completion required. System Test terminal/manually invoked; no enabled work auto-start.

## Implementation Notes
Execution ownership amendment (2026-11-06): the developer explicitly requested `/moda-task ARCH-063-SHARED-001`, authorized agent implementation, and requested moda_architect assistance to resolve preparation. Execution is delegated to moda_shared through the canonical agent launcher; completion_mode remains developer, preserving explicit developer completion authority. No scope, acceptance, dependency or attempt change.

Use launcher-resolved isolated/synchronized task worktrees when execution requested. No implementation from definition. Preserve accepted locking/domain/SDK identities. Task-specific assertions are binding; no architecture selection delegated. Service logger uses published Shared logging, never raw provider/Prisma Error.

## Completion Report
### Status
Ready for Review — architect Accepted; explicit developer completion pending.
### Files Changed
- src/shopify/offline-token-provider.ts
- src/shopify/node.ts
- src/shopify/offline-token-provider.test.ts
- src/shopify/offline-token-provider.postgres.test.ts
### Work Completed
Added optional isolated onEvent hook with exact frozen safe metadata, fresh UUID identity and monotonic bounded duration. Started is emitted immediately before dispatch after eligibility checks; committed only after transaction resolution. Failures emit one safe terminal category, including UNKNOWN for remote acceptance with persistence/commit ambiguity. Existing refresh, lock, credential and caller-error behavior is preserved. Reuse and lock waiters emit no refresh events. Node-only event type export supports independently owned consumer adapters. No service logger, SDK wrapper, publication version or consumer code changed.
### Validation Results
- `npx tsx --test src/shopify/offline-token-provider.test.ts`: PASS 20/20, zero skips, including secret canaries, sync/async hook failures, no-reuse events, cancellation and actual 8-second network timeout.
- `MODA_WORKSPACE_ROOT=<canonical workspace> node scripts/test-arch061-shopify-token-postgres.mjs`: PASS 1/1, zero skips; independent clients, single refresh pair, committed observer reads new credential pair/expiry from second client, save rollback, actual deferred-constraint COMMIT failure, recovery. Disposable container removed successfully. Initial readiness socket message was transient and retried by the existing runner.
- Targeted strengthened event timing test: PASS 1/1 (timing assertions outside isolated callbacks).
- `npm run typecheck`: PASS.
- `npm run build`: PASS ESM and declarations.
- `git diff --check`: PASS.
- Locked `npm ci --ignore-scripts` completed; audit reported 3 existing dependency vulnerabilities (1 low, 2 high); no dependency/lockfile changes made.
### Deviations
Task touchpoint table names index.ts for Node-only exports; actual ./shopify/node entrypoint is src/shopify/node.ts. Export added there, preserving browser-safe index.ts, as confirmed by moda_architect.
### Assumptions
Hook telemetry is process-local and best effort; process death can leave started without terminal. Consumer adapter integration and package publication remain separate tasks.
### Unresolved Issues
None. Initial automatic publication rejection was resolved by explicit developer authorization to push implementation source/tests and the parent task review report to their remote task branches.
### Architectural Concerns
None introduced. Completion mode remains developer; enabled tasks remain gated.
### Git / VCS
Task branch: task/ARCH-063-SHARED-001

Physical worktree isolation:
- canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
- parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-063-SHARED-001
- parent branch: task/ARCH-063-SHARED-001
- implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-063-SHARED-001
- implementation branch: task/ARCH-063-SHARED-001
- shared workspace checkout switched/mutated for task work: no
- shared implementation checkout switched/mutated for task work: no
- another task worktree reused: no

Start-of-attempt synchronization (launcher packet):
- parent remote task branch fast-forwarded: not-needed
- parent origin/main incorporated: already-current
- implementation remote task branch fast-forwarded: not-needed
- implementation origin/main incorporated: already-current
- recursive submodule sync/update: passed; recorded submodules: none; status ready
- Attempt 1 claim commit: 760282f8400c4c02a1353a623110b29202dcad1d; pushed yes

Implementation repository: moda-interact-shared
- commit: 4097eb3662c11bf97989cd1012da914973ec7592
- local branch: task/ARCH-063-SHARED-001
- pushed: yes; remote task branch verified at 4097eb3662c11bf97989cd1012da914973ec7592 after explicit developer publication authorization

Parent workspace:
- task file: docs/decisions/shared/ARCH-063/SHARED-001-emit-safe-postcommit-shopify-refresh-events.md
- report/review commit: see current parent task branch history; initial report 52d7f2d0e57193c2a85f7b74241f3ece9c35d361
- report pushed: yes on matching task branch; final review publication verified after commit
- submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review
### Review Status
Accepted — explicit developer completion pending.
### Review Notes
2026-11-06 moda_architect inspected actual implementation commit 4097eb3662c11bf97989cd1012da914973ec7592 and focused test changes. No implementation corrections identified. Optional observer preserves caller behavior and transaction/lock flow; committed emission follows awaited interactive transaction resolution. Event payload uses an explicit frozen field allowlist, fresh UUID, trusted resolved Shop identity and bounded monotonic duration. Errors/body/credentials are excluded, and synchronous throws/asynchronous rejections are isolated. Existing valid credential reuse and lock waiters do not emit attempts. Cancellation, remote uncertainty and commit failure produce one terminal event after started.

Technical review passes. Developer explicitly authorized publication of source/tests and the task review report after the initial automatic rejection. Accepted implementation remains at review under completion_mode developer; no main integration, package release or dependent execution is authorized by this review.
### Reviewed Files
- src/shopify/offline-token-provider.ts
- src/shopify/node.ts
- src/shopify/offline-token-provider.test.ts
- src/shopify/offline-token-provider.postgres.test.ts
- Current task Completion Report and launcher preparation packet.
### Validation Reviewed
Reviewed evidence: unit 20/20; disposable PostgreSQL 1/1 without skips and successful cleanup; typecheck; ESM/declaration build; diff whitespace check. Inspected assertions for actual deferred-constraint COMMIT failure, independent-client postcommit visibility, concurrency single event pair, secret canaries, hook failure isolation and timing assertions outside swallowed observer callbacks. No redundant validation rerun required.
### Architecture Conformance
Conforms to bounded Shared hook contract and compatible rollout. Node-only export correctly resides in node.ts; browser-safe index retained. Physical worktrees and startup synchronization match canonical launcher packet. Developer completion authority retained. ARCH-063-SHARED-002 remains Pending until this task is published, accepted and explicitly completed by developer.
### Follow-up
Developer completion pending via `/moda_developer_update ARCH-063-SHARED-001 complete`. Preserve completion_mode developer; no enabled task starts implicitly.
