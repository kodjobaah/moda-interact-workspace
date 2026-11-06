---
id: ARCH-061-SHARED-001
architecture_id: ARCH-061
title: implement coordinated shopify token provider
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 50
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables: ["ARCH-061-SHARED-002"]
created: 2026-11-05
updated: 2026-11-06
---
# Implement coordinated shopify token provider

## Architecture
ARCH-061; docs/architecture/ARCH-061-shopify-offline-token-refresh-coordination.md. Coordinator moda_architect.

## Objective
Implement coordinated shopify token provider using the published injected-client Shared runtime.

## Context
Background bespoke refresh currently reads/refreshes/writes unlocked; App SDK refreshes before storage write. Consumers use the same persisted rotating offline credential.

## Scope
Task-owned moda-interact-shared changes and focused validation only. Cross-repository paths below are read-only baseline evidence unless owned by this task.

| Existing file | Symbol/surface | Required change |
|---|---|---|
| moda-interact-shared/package.json | exports | Add Node-only factory export and structural injected Prisma contract; no service dependency. |
| moda-interact-background/src/services/shopify-session.service.ts | getShopifyAccessToken baseline (read-only reference) | Extract mechanics design without copying global Prisma/config policy; fix unbounded fetch, expiry checks and raw error-body leakage. |


## Out of Scope
Central token service, agent tools, sibling imports, credential UI, schema changes, node_modules patches, automatic execution, claims or main merges.

## Requirements
The entire parent architecture runtime/bounds/SDK/lifecycle/ambiguity matrix is normative. Factory accepts each service's local Prisma client at composition. Lock before read/decision/remote refresh; write-only locking is insufficient. No exactly-once remote guarantee across crash. Use the binding revision public-wrapper/ALS/lifecycle gate architecture; do not choose a different synchronization mechanism.

## Work Items
- [ ] Implement the normative transaction/fetch/validation/error contract with consumer-owned Prisma injection.
- [ ] Implement fixed revision-2 row/advisory lock order, public SDK lifecycle interface and provider-supported ambiguous-outcome recovery.
- [ ] Add unit and disposable PostgreSQL concurrency tests using two independent Prisma clients.

## Interfaces / Contracts
Shared Node-only factory and structural transaction interface/error categories defined by SHARED-001 and published by SHARED-002. Consumers inject local client/config/fetch and translate errors. No sibling source imports; no browser exports or raw token DTOs. App owns all SDK/lifecycle mutation entrypoints.

## Dependencies
None

## Enables
- ARCH-061-SHARED-002

## Acceptance Criteria
- [ ] Implement the normative transaction/fetch/validation/error contract with consumer-owned Prisma injection.
- [ ] Implement fixed revision-2 row/advisory lock order, public SDK lifecycle interface and provider-supported ambiguous-outcome recovery.
- [ ] Add unit and disposable PostgreSQL concurrency tests using two independent Prisma clients.
- [ ] Relevant parent matrix rows pass; no uncoordinated bypass, stale pair overwrite or secret emission.

## Validation
- [ ] Inspect package.json and run declared focused unit/integration tests for task-owned matrix rows, including disposable PostgreSQL separate-client races; record exact commands. Run declared typecheck/build appropriate to deployable changes.
- [ ] Record boundary/gap evidence honestly; never infer SDK coordination from helper-only tests.

## Stop Condition
Submit completed report for authorized review and STOP after scoped criteria/validation. Explicit developer completion required. Do not start enabled tasks; system validation is terminal/manually invoked.

## Revision 2 — binding implementation contract (2026-11-05)
This section supersedes earlier proposed APIs, feasibility gates, recovery assumptions and cutover text. All decisions below are architecture decisions, not implementation choices. Existing task metadata/history remains intact.

### Exact package/API and files to create
Shared creates `src/shopify/offline-token-provider.ts`, `src/shopify/offline-token-provider.test.ts`, `src/shopify/offline-token-provider.postgres.test.ts`, `src/shopify/oauth-configuration.ts` and `src/shopify/index.ts`; publish export `@modainteract/moda-interact-shared/shopify/node`. These paths are NEW, not claims of existing code. Export createShopifyOfflineTokenProvider, ShopifyOfflineTokenError, readShopifyOAuthConfiguration and the types below. Package entrypoint is Node-only and never re-exported from browser-safe root.

Factory input: `{prisma: ShopifyOfflineDatabase, readOAuth: () => Promise<{apiKey:string;apiSecret:string}>, fetch: typeof fetch, now?:()=>number}`. Factory returns `{withSdkInstallationSessionLock<T>(integrationDomain:string, work:(context:SdkInstallationSessionContext)=>Promise<T>):Promise<T>, getAccessToken(shopId:string, options?:{signal?:AbortSignal}):Promise<string>, getSession(shopId:string, options?:{signal?:AbortSignal}):Promise<OfflineCredentialSnapshot>, withSessionLock<T>(shopId:string, work:(context:LockedSessionContext)=>Promise<T>, options?:{signal?:AbortSignal}):Promise<T>}`. Snapshot is server-only `{id:string;shopId:string;shop:string;accessToken:string;scope:string|null;expires:Date|null;refreshTokenExpires:Date|null}`; never includes refreshToken. getAccessToken delegates to getSession. Context is `{transaction:ShopifyOfflineTransaction;shopId:string;shop:string;sessionId:string;signal:AbortSignal}`. This is not an authorization API: consumers resolve trusted tenant/shop first. Callback may perform ONLY session authentication/token acquisition/lifecycle persistence, never a route handler or unrelated commerce operation.

Structural interfaces: `ShopifyOfflineDatabase.$transaction<T>(work:(tx:ShopifyOfflineTransaction)=>Promise<T>, options:{maxWait:number;timeout:number;isolationLevel:'ReadCommitted'}):Promise<T>`. Transaction requires `$queryRawUnsafe<T>(sql:string,...values:unknown[]):Promise<T>`, `$executeRawUnsafe(sql:string,...values:unknown[]):Promise<number>`, and `session` delegate methods findUnique, findMany, create, update, upsert, delete, deleteMany, updateMany supporting the existing Session scalar shape; method args are narrow exported structural object types, not imported generated Prisma types. Any SDK session serialization delegates use this tx, never a second global-client transaction. Shared tests compile adapters against independently generated service clients. No Shared Prisma client instance or @prisma/client runtime dependency.

### Exact lock order
Within the configured transaction execute SET LOCAL lock_timeout='5s' and statement_timeout='18s'; parameterized SELECT pg_advisory_xact_lock(hashtextextended($1,0)) with the stored integration-domain gate, then parameterized SELECT "id" FROM "shopify"."Session" WHERE "id"=$1 FOR UPDATE with actual persisted row ID. Keep all timing/recovery guarantees. Acquire gate then existing lifecycle Shop locks where needed then actual Session row; never choose an arbitrary row. Selected-shop resolution and mapping are fixed in the selected-shop section below.

### Fixed budgets, wire validation and retry taxonomy
Transaction maxWait 5000ms; timeout 20000ms; per refresh network plus streamed body total 8000ms; callback/request work deadline 15000ms. Abort at first caller cancellation/deadline. Fetch POST `https://${shop}/admin/oauth/access_token`, redirect:error, no automatic retries, x-www-form-urlencoded client_id/client_secret/grant_type=refresh_token/refresh_token. Limit response to 16384 bytes while streaming before JSON parse, require successful status and object; token strings nonempty <=4096 chars with no CR/LF/NUL or surrounding whitespace. expires_in and refresh_token_expires_in must be safe integers >0, within 86400 and 7776000 seconds respectively, and access lifetime >300 seconds plus 20-second transaction margin. Validate optional scope string <=4096 chars/control-free; absent scope preserves stored scope, present scope replaces it. Compute expiries from request-start timestamp (conservative), check Date range, then update accessToken/expires/refreshToken/refreshTokenExpires/scope in ONE tx update. Return snapshot/token only after commit.

ShopifyOfflineTokenError exports fixed codes SESSION_MISSING, SESSION_IDENTITY_CONFLICT, INVALID_SESSION, REFRESH_TOKEN_EXPIRED, OAUTH_CONFIG_UNAVAILABLE, LOCK_TIMEOUT, CANCELLED, DEADLINE, REFRESH_REJECTED, REFRESH_RESPONSE_INVALID, REFRESH_OUTCOME_UNKNOWN, PERSISTENCE_UNAVAILABLE. No Error cause/raw payload in public error. Never log secret/token/provider body/SQL. Retryable flag true only lock timeout/deadline/persistence/unknown; caller cancellation and invalid input/rejected credentials false. No automatic retry inside call. Lock wait/HTTP failure before request dispatch is distinct from uncertain dispatch; 4xx rejection maps REFRESH_REJECTED, malformed success or post-dispatch network/body failure maps REFRESH_OUTCOME_UNKNOWN; DB failure after remote success likewise unknown. Transient pre-dispatch DB failure maps PERSISTENCE_UNAVAILABLE.

### Resolved provider recovery decision
Official Shopify August 28, 2026 change retains previously used refresh token until its replacement is used, at most 30 days from first use and within original 90-day lifetime: https://shopify.dev/changelog/posts/more-resilient-refreshes-for-expiring-offline-access-tokens . It explicitly supports lost-response/storage-failure recovery. On unknown outcome return bounded unavailable, release/rollback transaction and DO NOT return uncommitted access token. Next independent request reacquires locks, rereads durable pair, uses newest stored refresh token, and may make ONE fresh bounded refresh attempt with that persisted token if still unexpired. This is documented provider recovery, not blind concurrent retry. If provider rejects it, fail REFRESH_REJECTED and require existing reinstall/reauthorization; never keep an older in-memory token. No exactly-once remote guarantee on crash/save failure. No new durable marker/schema is needed for this provider-supported recovery path. Tests distinguish single normal refresh from permitted extra recovery request after injected ambiguity.

### SDK integration decision — public wrappers plus transaction-bound storage
There is no installed SDK pre-refresh hook. Do NOT invent one, mutate internal strategies, disable expiring offline tokens or patch node_modules. App creates `app/services/shopify-offline-coordination.server.ts` and `.test.ts`, plus `app/services/shopify-session-storage.server.ts` and `.test.ts`. Use Node AsyncLocalStorage to bind LockedSessionContext to custom implementation of PUBLIC Shopify SessionStorage interface. Keep SDK Session serialization compatibility by using its public Session class/Prisma adapter conversion behavior; no private method invocation. Its loadSession/storeSession/deleteSession/deleteSessions/findSessionsByShop execute against the bound transaction when offline; direct offline writes without context throw COORDINATION_REQUIRED. Online-only rows retain normal existing storage behavior but cannot overwrite offline IDs.

Wrap PUBLIC shopify.authenticate.admin, authenticate.webhook and unauthenticated.admin BEFORE SDK invocation in withSessionLock. Wrapper scope ends after SDK authentication/context acquisition or redirect Response, before returned admin client operations or React Router route work. SDK token exchange/refresh and storeSession then share the same held gate/row tx. SDK may refresh internally and that is permitted only in this scope. Expose default shopify object as a facade with these wrapped fields; exported authenticate/unauthenticated/sessionStorage reference facade, never raw underlying SDK. Other auth methods remain delegated but storage refuses any offline access without binding; add an explicit wrapper when an actually used method requires it rather than silently bypassing enforcement.

For admin requests choose lock hint from Bearer session token JWT dest (decoded ONLY to select lock, NOT treated authenticated), then id_token/session URL token dest, then query shop. SDK still verifies JWT/HMAC/audience before auth success. For webhook use X-Shopify-Shop-Domain; for unauthenticated.admin use supplied domain. Use existing SDK/install acceptance rules; do not add domain syntax checks. Custom storage asserts every offline load/store row.shop AND actual stored session ID match bound context before returning any row; SDK actual decoded dest mismatch therefore fails at initial load before token exchange. No offline ID or hint means no offline credential/storage/token endpoint operation is allowed; SDK readless login/redirect path may execute with no context, and storage/transport enforce refusal if it tries offline token work. Invalid token payload is never authorization. Tests deliberately mismatch hint/verified dest and demand no OAuth call/write. Install authenticity stays SDK owned.

Install official `setAbstractFetchFunc` exported from `@shopify/shopify-api/runtime` ONCE after adapters/node import and before shopifyApp creation. Runtime declaration exports this function in installed package. Delegate to captured native fetch (not abstractFetch recursion). For OAuth token endpoint require ALS context and same stored integration domain, combine caller/context 8000ms deadline, redirect:error and 16384-byte body bound, sanitize logs; use bounded reconstructed Response so SDK JSON parsing cannot exceed deadline. Other SDK requests get caller 15000ms context bound when in auth transaction; do not globally alter external route requests or log bodies. Transaction timeout alone is NOT network cancellation. Preserve SDK HTTP diagnostics redaction and httpRequests:false. SDK retrying token exchange after client errors must use the same wrapper/context and deadline; returned client retry handler that later needs offline write must re-enter wrapper from public authenticate.admin, otherwise storage rejects before exchange.

App SDK redirects: a thrown Response after a successful token store must COMMIT session transaction then rethrow Response outside it. Ordinary errors roll back. Capture callback Response as a tagged return value so transaction commits intentionally; 4xx/5xx failure Response without successful validated persistence must roll back. Do not commit arbitrary error effects. Compare provider request/save state in scoped context; tests cover OAuth redirect success versus failure rollback. No callback escapes transaction-bound Prisma/ALS into later route execution.

### OAuth configuration exact adapter decision
App retains createDefaultShopifyPlatformConfigurationService().requireShopifyOAuthCredentials in app/services/platform-configuration/composition.server.ts. Background retains platformConsumerConfiguration.read('shopify.oauth') in src/services/platform-configuration/consumers.ts. Commerce existing src/platform-configuration/runtime.ts/service.ts does NOT yet expose shopify.oauth; MCP has no platform OAuth reader. Add NEW Commerce `src/platform-configuration/shopify-oauth.ts` and MCP `src/runtime/shopify-oauth.ts`; these use Shared readShopifyOAuthConfiguration with each local Prisma platformConfiguration delegate, trusted deployment environment and MODA_CONFIG_UNSEAL_KEY parsed via existing Shared credentials/node. Do not copy App/Background source or pass OAuth keys via tool requests.

Shared readShopifyOAuthConfiguration input `{prisma:{platformConfiguration:{findUnique(args):Promise<Row|null>}};environment:string;unsealKeyring:CredentialKeyring}` reads exact environment_key [environment,'shopify.oauth']; validates stored environment/key/version and sealed envelope with existing Shared decryptCredential/parseCredentialKeyring. Freeze AAD UTF-8 JSON.stringify(['moda-platform-config-v1',environment,'shopify.oauth',version,1]) exactly as existing App seal.server.ts and Background service.ts. Decode existing `{apiKey,apiSecret}` payload shape, nonempty bounded strings, no plaintext/env fallback, no disabled/missing row fallback. Reuse existing platform sealed format, do not invent envelope. Add known existing-format compatibility vectors for App/Background readers; Shared tests use actual stored envelope fixtures. This new reusable reader is scoped to Shopify OAuth, not an unsolicited platform config rewrite.


### Task-owned exact file changes and read-only inventory
NEW paths below are to be created RELATIVE TO THIS TASK REPOSITORY. Existing fully qualified paths are verified. Cross-repository evidence is read-only.

| Path | Exact existing/new surface | Required edit |
|---|---|---|
| NEW src/shopify/offline-token-provider.ts | createShopifyOfflineTokenProvider/getSession/getAccessToken/withSessionLock | Implement exact binding revision API, lifecycle advisory+Session row lock, bounded fetch and error taxonomy. |
| NEW src/shopify/oauth-configuration.ts | readShopifyOAuthConfiguration | Implement injected local platformConfiguration read with frozen existing AAD/sealed decoder and safe OAuth DTO. |
| NEW src/shopify/index.ts | package entrypoint | Export Node-only runtime/types; no browser root export. |
| moda-interact-shared/package.json | exports/build config | Add ./shopify/node export; include new files in declared build. |
| NEW src/shopify/offline-token-provider.test.ts | unit fixtures | Test selected-shop ownership, expiry/skew, response bounds, scope preservation, every error code and secret canaries. |
| NEW src/shopify/offline-token-provider.postgres.test.ts | PostgreSQL fixture | Two separate clients barrier-race, absent-row lifecycle ordering, rollback/commit ambiguity, no deadlock and different-shop progress. |
| NEW src/shopify/oauth-configuration.test.ts | known-format vector | App/Background-compatible sealed payload + disabled/missing/wrong env/key/version/AAD rejection. |

### Task-specific deterministic assertions
- [ ] Two clients released by same barrier: provider refresh request count=1, both receive committed access token, final refresh pair matches returned fixture.
- [ ] Timeout while one lock held: second returns LOCK_TIMEOUT <=5s+250ms; releasing holder lets later call succeed.
- [ ] Unknown remote success/save rollback: first returns REFRESH_OUTCOME_UNKNOWN without token; next call rereads old durable pair and uses documented recovery, success commits whole pair.
- [ ] Scope omitted/present remains/persists exactly; expired refresh token ->0 HTTP; unknown shop/wrong provider/foreign session ->0 HTTP.

Create the new focused test paths listed in this exact command where absent; preserve existing test files. Required focused command: `npx tsx --test src/shopify/offline-token-provider.test.ts src/shopify/oauth-configuration.test.ts`. Also run `npx tsx --test src/shopify/offline-token-provider.postgres.test.ts` against disposable PostgreSQL, `npm run typecheck` and `npm run build`.

## Implementation Notes
No execution started. Use launcher isolated/synchronized task worktrees when requested. Use the installed SDK surfaces and official recovery policy identified in revision 2. Node recovery uses workspace bootstrap. No new schema or alternative lock primitive is authorized. Publication is release mechanics only.

## Completion Report

### Status

Submitted for architect review — Attempt 2. The review-requested source corrections and required Shared validation are complete. The task remains in `review`; explicit developer completion is pending a durable passing review and a separate developer decision.

### Files Changed

The implementation contains eight task-owned files; Attempt 2 corrects two of those files across the two commits:

- Initial implementation `66b59a295de835a66930aa57c1c98ef424ccbfb4`: Node entrypoint exports; injected offline-token provider and unit/PostgreSQL tests; sealed OAuth configuration reader/tests; disposable PostgreSQL and generated-client contract runners.
- Attempt 2 correction `f399a84`: `src/shopify/offline-token-provider.ts` and `src/shopify/offline-token-provider.test.ts`.

The existing package export map and build entry already exposed the Node-only `./shopify/node` subpath at baseline `e9f5968`; no package or browser-safe Shopify entrypoint change was needed. No dependency/version, database schema, or consumer repository changes were made.

### Work Completed

Implemented the Shared injected-client Shopify offline token provider, structural Prisma contract, Node-only exports, and OAuth configuration reader using the existing sealed configuration format.

Addressed both Attempt 1 findings:

1. Once Shopify returns a successful status, malformed JSON, invalid token/lifetime fields, invalid dates, and streamed body overflow now map to retryable `REFRESH_OUTCOME_UNKNOWN`. No uncommitted credentials are returned or persisted; the next independent request can use the documented persisted-token recovery path.
2. `getSession` and `withSessionLock` now establish one 15-second operation deadline and check cancellation before the initial selected-Shop lookup. The lookup, transaction, lock work, and callback share that deadline; it is not reset after resolution. Regressions cover a stalled initial lookup and a pre-aborted caller that must not issue the lookup.

### Validation Results

All required validations passed on the correction:

- `npx tsx --test src/shopify/offline-token-provider.test.ts src/shopify/oauth-configuration.test.ts` — 18 passed, 0 failed.
- `npm run typecheck -- --pretty false` — passed.
- `npm run build` — passed (ESM and declaration builds).
- `node scripts/test-arch061-shopify-token-postgres.mjs` — 1 passed using two independent Prisma clients; verified one normal refresh for the race, bounded lock wait, different-shop progress, rollback after injected save failure, and next-request recovery. Disposable container `arch061-shared-e9c5e224-201a-4aad-bf0e-6a8384d41045` was removed by the runner.
- `TMPDIR=/private/tmp node scripts/test-arch061-shopify-prisma-contracts.mjs` — passed for Background and Commerce generated Prisma adapters.
- `git diff --check` — passed.

### Deviations / Assistance

No agent assistance or consumer changes were used. The task definition names `src/shopify/index.ts` and the `./shopify/node` export as new surfaces; inspection of the task branch baseline confirmed the package export and build entry already existed, so the implementation added the runtime API through the existing Node entrypoint and preserved the browser-safe Shopify entrypoint.

### Git / VCS

Task branch: `task/ARCH-061-SHARED-001`.

Physical worktree isolation:

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-061-SHARED-001` / `task/ARCH-061-SHARED-001`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-061-SHARED-001` / `task/ARCH-061-SHARED-001`.
- Shared workspace checkout switched for task work: no. Shared implementation checkout switched for task work: no. Another task worktree reused: no.
- Recursive implementation submodule sync and update-init: passed; no recursive entries were present.

Start-of-attempt synchronization from the Attempt 2 preparation packet:

- Parent remote task branch fast-forward: not needed; parent `origin/main` incorporated: already current.
- Implementation remote task branch fast-forward: not needed; implementation `origin/main` incorporated: already current.

Implementation repository: `moda-interact-shared`; correction commit `f399a84` pushed to `origin/task/ARCH-061-SHARED-001`. Implementation worktree is clean after publication.
Parent workspace task file: `docs/decisions/shared/ARCH-061/SHARED-001-implement-coordinated-shopify-token-provider.md`; report submission commit `fc07d3190` was pushed to `origin/task/ARCH-061-SHARED-001`. No submodule gitlink is staged. Neither task branch is merged to `main`.

### Unresolved Issues

None within the Shared implementation scope. App SDK lifecycle coordination and production consumer wiring belong to their separately assigned ARCH-061 tasks; this Shared validation does not claim those consumer behaviors. ARCH-061-SHARED-002 remains gated pending completion of this task.

### Architectural Concerns

Preserve revision 2 boundaries: consumers inject their local Prisma clients; no shared Prisma runtime or schema change; use selected Shop identity, stored integration domain and actual Session row ID; keep SDK/lifecycle mutation under the App-owned public-wrapper boundary; do not infer consumer rollout readiness from Shared tests.

## Architect Review
### Review Status
Pending
### Review Notes
Definition only.
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending implementation.
### Follow-up
None

### Architecture definition review — 2026-11-05 revision 2
Definition reviewed against installed SDK control flow and current repository reads/writes. Public authenticate/unauthenticated wrapper + ALS storage and runtime setAbstractFetchFunc are the selected integration; no fictional SDK hook. Session row plus stable per-shop lifecycle advisory gate is selected for demonstrated deletion/recreation. Provider lost-response recovery is grounded in official Shopify August 28, 2026 policy. No implementation reviewed and no lifecycle status changed.

### Selected-shop identity and existing integration rules
The caller supplies selected `commerce.Shop.id`, never a host/domain: `getAccessToken(shopId:string, options?:{signal?:AbortSignal}):Promise<string>`, `getSession(shopId:string, options?:{signal?:AbortSignal}):Promise<OfflineCredentialSnapshot>`, `withSessionLock<T>(shopId:string, work:(context:LockedSessionContext)=>Promise<T>, options?:{signal?:AbortSignal}):Promise<T>`. Context includes trusted `shopId`, stored `shop` integration domain and actual `sessionId`. Snapshot includes `shopId` plus existing session fields. Add structural `shop.findUnique({where:{id:string},select:{id:true;platform:true;status:true;domain:true}})` to transaction interface. Shared loads selected Shop server-side, requires existing active SHOPIFY identity, then reads its stored offline Session through existing installation mapping (`Session.shop` matches the trusted Shopify integration domain). It verifies row ownership against that selected shop and rejects missing/ambiguous/foreign session. No new schema field or alias map is introduced. Current schema stores Shopify integration domain on Shop.domain and Session.shop; use that existing relationship, not a primary storefront/custom domain from a browser. Use actual persisted Session.id for row lock/update; SDK owns new-auth session ID creation. Do not derive or mandate an offline_<domain> ID, rekey legacy rows or invent ID normalization.

No new domain regex, normalization or myshopify.com acceptance rule is added. Shopify installation/SDK validation continues to own accepted integration domains. Once trusted mapping resolves, the refresh URL host is the stored Session.shop; do not accept a host in provider options or tool inputs. Unknown shop -> SESSION_MISSING, non-SHOPIFY/inactive shop -> INVALID_SESSION, missing/ambiguous/foreign offline mapping -> SESSION_IDENTITY_CONFLICT or SESSION_MISSING as applicable, before OAuth I/O. Existing consumer tenant authorization remains required before this helper; knowing a Shop ID alone is not authorization.

All existing-shop service and SDK paths use gate parameter `moda:shopify-offline:v1:${storedIntegrationDomain}` then lock actual stored Session.id. Resolve selected Shop, stored domain and session association again under the gate; if association changed, fail rather than switching shop/host under the old gate. No custom domain alias remapping is added. Row select SQL remains parameterized WHERE id=$1 using actual row id.

SDK install/bootstrap has no Shop ID yet: provide separately named `withSdkInstallationSessionLock<T>(integrationDomain:string, work:(context:LockedSessionContext)=>Promise<T>)` ONLY to App composition, not consumer getAccessToken/getSession callers. SDK's existing validation/installation rules establish the integration domain and still verify request authenticity. Existing-shop App requests resolve that stored integration to its Shop first and use selected-shop path; genuinely new SDK auth uses bootstrap gate with same domain identity, while SDK owns generated Session.id. There is no new domain acceptance check or invented alias table. Unverified request hints select only candidate gate as previously specified and never authorize; the SDK storage adapter checks actual row.shop against the bound SDK integration context before returning/persisting any credential. Binding a session ID happens from actual stored row or successful SDK-generated Session, not string concatenation. After bootstrap creates Shop, future consumers use the existing stored relationship and same gate. Lifecycle deletion/reinstall takes same stored integration-domain gate before existing locks.

### Exact adapter changes for selected Shop ID
Background helper becomes `getShopifyAccessToken(shopId:string, options?:{signal?:AbortSignal})`; existing provider callbacks accepting shopDomain resolve through their existing authorized Shop object/query and pass its id. Do not pass domain as ID or infer a different tenant. Where a domain-only runtime callback remains, the service adapter resolves an active SHOPIFY Shop by the existing stored integration domain within its current authorized execution context, requires one matching Shop and forwards id; absence/ambiguity fails closed. No Shared domain lookup overload.

Commerce createStudioLocalProviderExecution uses call.turn.shopId after existing authorized shop/domain admission; local-policy-providers uses context.shopId for merchantKnowledge and policy execution. Its discount provider domain-only list callback resolves the matching owned active Shopify Shop from its existing local Prisma/context then calls getSession(shop.id); retain scope and permission checks. MCP runtime provider reader accepts trusted selected shop identity from resolved connection context (thread shopId to read rather than extracting it from arbitrary request domain); retain stored domain equality check as consistency validation, not new validation policy. Metadata-only status readers retain selected-shop filtering and no refresh, use actual persisted IDs and existing mapping rather than new hardcoded canonical ID predicates.

### Replacement identity acceptance assertions
Replace invalid-domain/regex/canonical-format fixtures with: unknown selected Shop ID -> no OAuth; wrong provider -> no OAuth; inactive selected Shop -> no OAuth; foreign Session.shop or mismatched selected-shop association -> denial/no OAuth; multiple offline rows -> explicit conflict, no arbitrary selection; existing legitimate stored SDK Session.id -> preserved/used for lock and update; bootstrap SDK-generated ID -> accepted only in authentic SDK flow; custom storefront/browser host cannot choose refresh origin; two services and App resolving same stored integration acquire same gate. Existing Shopify domain acceptance tests remain unchanged.

Bootstrap context type is `SdkInstallationSessionContext={transaction:ShopifyOfflineTransaction;shopId:null;shop:string;sessionId:string|null;signal:AbortSignal}` until existing Shop/session association is established by SDK install. Consumer LockedSessionContext always has non-null selected Shop ID and actual existing Session ID. Bootstrap is App-only and never a domain overload of getAccessToken/getSession.


## Developer Self-Review - Changes Requested — Attempt 1 (2026-11-06)

### Decision

**Review fails.** Reconciled the current uncommitted implementation against binding revision 2. Return to Ready, executor/claimed_at null, Attempt 1 unchanged; developer execution/completion modes preserved. No next claim or completion is created. Preserve all WIP; this review changes only the parent task record.

### Corrections required

1. **P2 — Classify ambiguous successful refresh responses as retryable unknown outcomes.** `src/shopify/offline-token-provider.ts:352-369` propagates REFRESH_RESPONSE_INVALID for oversized/malformed/invalid successful responses. That code is non-retryable, despite a successful remote response possibly having rotated credentials. The binding taxonomy explicitly assigns malformed success and post-dispatch body failures to REFRESH_OUTCOME_UNKNOWN. Preserve rollback/no-token-return, emit only bounded safe errors and allow the documented next independent request recovery. Update existing tests currently asserting REFRESH_RESPONSE_INVALID for these post-dispatch cases, including malformed JSON, invalid lifetime/token fields and oversized bodies; verify no write/uncommitted token and retryable true.
2. **P2 — Include initial selected-shop resolution in cancellation/deadline handling.** `getSession` and `withSessionLock` await `resolveShop` before `runLocked` creates/checks the operation deadline. A stalled initial database lookup is therefore unbounded, and a pre-aborted caller still performs/waits for that lookup. Establish the call budget and cancellation check at the public selected-shop entrypoint, cover initial resolution and transaction/callback with the same budget, preserve transaction rollback/no late work, and test a stalled initial lookup plus already-aborted caller. Do not reset the operation budget after resolution.
3. **Finish the semantic completion/validation report.** It still says Files Changed/Work Completed None and Validation Definition only, while seven task-owned files exist as WIP. Record the actual implementation and assistance, prepared worktree/synchronization evidence, exact unit/typecheck/build and required disposable PostgreSQL results, including separate-client lock/race/recovery proof and cleanup. The new PostgreSQL test/helper source alone is not passing execution evidence. Report NOT_RUN if absent; no Docker/integration execution is authorized by this review.

### Implementation and verification inspected

Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-061-SHARED-001`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-061-SHARED-001`, matching task branches. Implementation baseline HEAD `e9f59680693db13efd73a04b512970245ff9b4f5`. WIP: modified `src/shopify/node.ts`; new offline-token-provider source/unit/PostgreSQL tests, OAuth configuration source/tests and disposable runner script. No task-owned implementation commit/publication exists yet; no WIP is discarded or falsely labelled published.

Inspected provider lock/identity/refresh/error/deadline logic, the OAuth sealed-reader adapter and PostgreSQL runner/test source. Independently ran the required two-file unit set via installed tsx: **17 tests passed**, zero failed/skipped, exit 0; local evidence `/tmp/arch061-shared-review.log`. Passing tests currently encode the erroneous response classification and do not replace the missing initial-lookup bounds or database evidence. No typecheck/build/PostgreSQL/live provider run is claimed by this review. Consumer SDK/ALS integration remains separately owned and is not inferred from Shared helper tests.

### Follow-up

Reclaim through the normal developer workflow, preserve this Attempt 1 history and current WIP, correct both source issues, reconcile the report and provide required evidence before resubmission. Explicit developer completion remains unavailable until a passing review is durable. SHARED-002 stays gated on this task's completion; no downstream promotion, package publication, main merge, schema change or consumer edit is performed.


## Developer Self-Review - Changes Requested — Attempt 1 Recheck (2026-11-06)

The developer invoked the reconciliation skill again while the task remained Ready/unclaimed. No new claim or attempt is manufactured. **Changes Requested remains in effect.** Implementation is now committed and pushed at `66b59a295de835a66930aa57c1c98ef424ccbfb4`; the earlier WIP/publication description is historical.

Source verification confirms both open findings: `getSession` and `withSessionLock` await `resolveShop` before `runLocked` constructs the deadline; malformed successful bodies and invalid successful payload fields still throw REFRESH_RESPONSE_INVALID, bypassing the unknown-outcome mapping through CallbackFailure. Commit publication and added test helpers do not fix those behaviors. Apply the exact previous corrections and regressions, then provide the final semantic report and actual required validation results.

No tests or Docker runs were repeated; no new passing evidence is claimed. The initial completion report has been reconciled to describe the committed partial implementation rather than None/Definition only. Status Ready, executor/claimed_at null, Attempt 1 preserved; developer execution/completion modes unchanged. SHARED-002 remains gated. No source alteration, downstream promotion, release or merge is performed by this recheck.


## Developer Self-Review Passed / Accepted — Attempt 2 (2026-11-06)

**Review passed; no actionable findings remain from the requested corrections.** Reviewed implementation `f399a84b592da1a3855e2a6561567a788ea3fcfa`, matching its published task ref. Status Review; executor/claimed_at null; Attempt 2 unchanged. Execution/completion modes remain developer/developer. Explicit developer completion remains pending; this review does not complete the task or unblock SHARED-002.

### Correction and evidence reconciliation

Malformed successful JSON, invalid returned token/lifetime/date fields and streamed overflow now produce retryable REFRESH_OUTCOME_UNKNOWN, with no returned uncommitted credential. Public getSession/withSessionLock create and check one operation deadline before initial selected-Shop resolution, race that lookup against cancellation/deadline and pass the same budget through lock/transaction/callback. The updated unit regressions cover malformed success, stalled initial lookup and pre-aborted caller. The completion report now describes the actual source, publication, isolation and required validation instead of definition-only placeholders.

Independently ran `node --import tsx --test src/shopify/offline-token-provider.test.ts src/shopify/oauth-configuration.test.ts` using workspace Node 24.19.0: **18 passed, 0 failed/skipped**, exit 0. Local evidence `/tmp/arch061-shared-attempt2-review.log`. Independently checked correction whitespace and source/remote equality. Inspected the provider correction, focused tests and generated-client structural runner.

Reviewed the submitted report of passing typecheck/build, generated Background/Commerce client compilation and disposable PostgreSQL proof (1 passed, two independent clients, lock contention/different-shop progress/rollback recovery and owned-container cleanup). Those checks were not independently rerun by this review; no live Shopify request or consumer SDK integration is certified by the Shared test evidence. Earlier failed dispositions are historical and superseded for the corrected source.

The canonical dedicated parent/implementation worktrees were clean at review. Attempt 2 preparation/claim/synchronization, unchanged consumer boundary and implementation/report commits are recorded in the Completion Report. No new claim, implementation edit, package publication, dependency promotion, main merge or deployment occurs. The durable parent review is committed/pushed separately on the matching task branch. The developer retains explicit completion and final integration authority.
