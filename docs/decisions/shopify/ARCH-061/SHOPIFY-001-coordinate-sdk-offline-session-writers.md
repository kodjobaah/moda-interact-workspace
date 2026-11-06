---
id: ARCH-061-SHOPIFY-001
architecture_id: ARCH-061
title: coordinate sdk offline session writers
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 50
executor: null
claimed_at: null
attempt: 2
depends_on: ["ARCH-061-SHARED-002"]
enables: ["ARCH-061-BACKGROUND-001", "ARCH-061-COMMERCE-001", "ARCH-061-MCP-001", "ARCH-061-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-06
---
# Coordinate sdk offline session writers

## Architecture
ARCH-061; docs/architecture/ARCH-061-shopify-offline-token-refresh-coordination.md. Coordinator moda_architect.

## Objective
Coordinate sdk offline session writers using the published injected-client Shared runtime.

## Context
Background bespoke refresh currently reads/refreshes/writes unlocked; App SDK refreshes before storage write. Consumers use the same persisted rotating offline credential.

## Scope
Task-owned moda-interact changes and focused validation only. Cross-repository paths below are read-only baseline evidence unless owned by this task.

| Existing file | Symbol/surface | Required change |
|---|---|---|
| moda-interact/app/shopify.server.js | shopifyApp configuration and sessionStorage | Compose factory with App Prisma and existing OAuth configuration; establish supported pre-read SDK boundary. |
| moda-interact/app/routes/webhooks/app/uninstalled/route.jsx | uninstall route | Enforce same lifecycle lock order/current-install checks and no stale resurrection. |
| moda-interact/tests/helpers/shopify-lifecycle-postgres.ts | independent Prisma/session storage fixtures | Add SDK-vs-shared concurrency and install/uninstall race tests. |


## Out of Scope
Central token service, agent tools, sibling imports, credential UI, schema changes, node_modules patches, automatic execution, claims or main merges.

## Requirements
The entire parent architecture runtime/bounds/SDK/lifecycle/ambiguity matrix is normative. Factory accepts each service's local Prisma client at composition. Lock before read/decision/remote refresh; write-only locking is insufficient. No exactly-once remote guarantee across crash. Use the binding revision public-wrapper/ALS/lifecycle gate architecture; do not choose a different synchronization mechanism.

## Work Items
- [x] Inventory every SDK/custom offline writer and prove supported coordinated read-through-refresh scope. Storage-write-only adapter is forbidden.
- [x] Implement App lifecycle ordering with the fixed advisory gate then row-lock order and canonical identity checks from revision 2.
- [x] Prove SDK/Background-style client simultaneous refresh yields one normal remote call; stale store cannot overwrite new pair.

## Interfaces / Contracts
Shared Node-only factory and structural transaction interface/error categories defined by SHARED-001 and published by SHARED-002. Consumers inject local client/config/fetch and translate errors. No sibling source imports; no browser exports or raw token DTOs. App owns all SDK/lifecycle mutation entrypoints.

## Dependencies
- ARCH-061-SHARED-002

## Enables
- ARCH-061-BACKGROUND-001
- ARCH-061-COMMERCE-001
- ARCH-061-MCP-001
- ARCH-061-SYSTEM-TEST-001

## Acceptance Criteria
- [x] Inventory every SDK/custom offline writer and prove supported coordinated read-through-refresh scope. Storage-write-only adapter is forbidden.
- [x] Implement App lifecycle ordering with the fixed advisory gate then row-lock order and canonical identity checks from revision 2.
- [x] Prove SDK/Background-style client simultaneous refresh yields one normal remote call; stale store cannot overwrite new pair.
- [x] Relevant parent matrix rows pass; no uncoordinated bypass, stale pair overwrite or secret emission.

## Validation
- [x] Inspect package.json and run declared focused unit/integration tests for task-owned matrix rows, including disposable PostgreSQL separate-client races; record exact commands. Run declared typecheck/build appropriate to deployable changes.
- [x] Record boundary/gap evidence honestly; never infer SDK coordination from helper-only tests.

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
| moda-interact/app/shopify.server.js | shopifyApp and exported facade | Install runtime bounded transport and ALS storage; wrap public auth entrypoints before SDK invocation; no raw default SDK escape. |
| NEW app/services/shopify-offline-coordination.server.ts | withCoordinatedShopifyAuthentication | Own wrapper hint/domain enforcement, public auth invocation, Response commit handling and context cleanup; do not wrap route handlers. |
| NEW app/services/shopify-session-storage.server.ts | CoordinatedShopifySessionStorage | Implement public storage interface; bound offline reads/writes to current tx; online-only default adapter remains separate. |
| moda-interact/app/services/platform-configuration/composition.server.ts | createDefaultShopifyPlatformConfigurationService | Reuse existing OAuth read; no duplicate secrets/config source. |
| moda-interact/app/services/shop/shop.service.ts | offline credential readiness read near126; deletion near668 | Metadata readiness stays read-only; lifecycle teardown enters same gate BEFORE existing transaction/Shop locks, reuse tx instead of nested tx. |
| moda-interact/app/routes/webhooks/app/uninstalled/route.jsx | uninstall webhook | Authentication wrapper completes first; teardown then independently enters gate; preserve existing current-install checks. |
| moda-interact/app/routes/webhooks/shop/redact/route.jsx | session.deleteMany | Acquire gate before redact transaction/deletes; delete all shop sessions only after existing verified webhook admission. |
| moda-interact/app/routes/webhooks/app/scopes-update/route.jsx | session.updateMany/findFirst | Acquire gate before scope transaction, update scope under selected stored row lock without writing credential pair; online rows preserve prior behavior. |
| moda-interact/app/services/discounts/shopify-discount-lifecycle.service.ts | offline scope read near146 | Metadata scope check under existing business tx remains no-refresh; avoid nested lock inversion and never reuse it as access-token source. |
| moda-interact/app/services/shop/merchant-request-context.server.ts | authenticate.admin caller | Use coordinated export; assert no raw SDK import escape. |
| moda-interact/app/routes/auth/catchall/route.jsx | authenticate.admin caller | Use coordinated export, preserve authenticated redirect behavior. |
| moda-interact/tests/helpers/shopify-lifecycle-postgres.ts | two storage/client fixtures | Bind two App+Shared clients to real tx; prove install/delete/recreate ordering. |

### Task-specific deterministic assertions
- [ ] Pause two authenticators before SDK load; release both; one acquisition/refresh occurs, second sees committed row; stale store rejected outside ALS.
- [ ] Valid SDK session token whose dest differs from lock hint: storage rejects before OAuth network.
- [ ] SDK successful exchange then redirect commits once and rethrows Response outside tx; SDK error/failed exchange rolls back.
- [ ] Uninstall/delete and reinstall/exchange barriers: operations order on same gate; no transaction leaks/online row corruption.
- [ ] Raw default SDK authenticate/sessionStorage escape test fails import-policy assertion.

Create the new focused test paths listed in this exact command where absent; preserve existing test files. Required focused command: `npx vitest run tests/unit/shopify-offline-coordination.test.ts tests/integration/shopify-offline-coordination.test.ts`. Run declared `npm run build`; App/Commerce/MCP additionally `npm run typecheck`; System Test uses `npm run typecheck` only.

## Implementation Notes
No execution started. Use launcher isolated/synchronized task worktrees when requested. Use the installed SDK surfaces and official recovery policy identified in revision 2. Node recovery uses workspace bootstrap. No new schema or alternative lock primitive is authorized. Publication is release mechanics only.

## Completion Report

### Status

Review — Attempt 2 submitted for architect review on 2026-11-06. Attempt 1 review history is preserved below.

### Files Changed
`package.json`, `package-lock.json`; `app/shopify.server.js`; new `app/services/shopify-offline-coordination.server.ts` and `app/services/shopify-session-storage.server.ts` with their focused tests; `app/services/shop/shop.service.ts`; `app/services/observability/shopify-runtime-observability.server.ts`; `app/routes/webhooks/app/scopes-update/route.jsx`; `app/routes/webhooks/shop/redact/route.jsx`; `tests/helpers/shopify-lifecycle-postgres.ts`; new `tests/unit/shopify-offline-coordination.test.ts` and `tests/integration/shopify-offline-coordination.test.ts`; updated `tests/unit/routes/scopes-update.test.jsx`, `tests/unit/services/shop.service.test.ts`, and `tests/unit/server-error-privacy.test.ts`.
### Work Completed
- Upgraded App to the published `@modainteract/moda-interact-shared` 5.2.0 Node export and composed its provider with the App Prisma client and the existing App OAuth configuration service.
- Replaced raw SDK session storage exposure with a public `SessionStorage` adapter. Offline reads/writes use the authentication transaction binding; direct writes are denied. For an existing row, storage tracks its current credential fingerprint and accepts a replacement pair only when the bounded OAuth response in that same binding supplied it; each successful write advances the accepted fingerprint, rejecting stale stores. Shop and actual persisted Session ID checks remain mandatory. The SDK facade wraps public admin, webhook and unauthenticated-admin entrypoints and exports no raw authentication or storage escape.
- Installed the SDK public abstract-fetch adapter. OAuth refresh traffic requires the bound stored integration host and POST method, rejects redirects, limits streamed response size to 16 KiB, applies an 8-second network budget, and maps rejected versus ambiguous post-dispatch failures to fixed Shared error categories. Other SDK transport and callback work is bounded to 15 seconds. SDK diagnostic messages are wholly omitted during coordinated authentication.
- Applied the same Shared domain advisory gate before the existing Shop lifecycle lock and actual Session row lock where applicable. Uninstall, scopes-update, and shop-redact persistence reuse the gate-bound transaction. Scope/readiness checks remain metadata-only and do not refresh tokens.
- Audited production paths: raw SDK `authenticate.admin`, `authenticate.webhook`, and `unauthenticated.admin` invocation exists only inside the facade wrappers; offline Session write/delete paths are the coordinated storage adapter and the gated uninstall/scopes/redaction lifecycle transactions. The default SDK storage/auth object is not exported.
- Added App unit assertions for redirect commit versus failure rollback, mismatched Session identity, missing binding, stale Session rejection (including an older credential pair after a successful replacement in the same binding), safe error categories, transport bounds, and raw SDK export policy. The PostgreSQL regressions now install through `sdk.authenticate.admin`, read the SDK-generated persisted Session ID, expire that row, and invoke the installed public `sdk.unauthenticated.admin` refresh. They prove the newly constructed SDK Session atomically commits both tokens while an independent Shared client waits on the same gate, and preserve the SDK-refresh/uninstall/reinstall ordering test.
### Validation Results
- `npm run typecheck` — passed after the Attempt 2 correction.
- `npm run build` — passed after the Attempt 2 correction. Vite emitted dependency annotation, external Prisma browser-entry, and large client-chunk warnings; no build errors.
- Required focused command `npx vitest run tests/unit/shopify-offline-coordination.test.ts tests/integration/shopify-offline-coordination.test.ts` — 11 passed; the two PostgreSQL cases are flag-gated and skipped in this unflagged invocation.
- Disposable PostgreSQL command `DOCKER_HOST=unix:///Users/kwadwoadomafriyie/.colima/default/docker.sock TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock MODA_SHOPIFY_LIFECYCLE_POSTGRES=1 npx vitest run tests/integration/shopify-offline-coordination.test.ts` — 2 passed. Both cases use real SDK auth/refresh and separate Prisma clients; Testcontainers stopped the owned fixture container after the run.
- Additional focused coordination/session-storage test command — 14 passed across 3 files.
- Additional focused command covering coordination/storage service tests, privacy diagnostics, ShopService, and scopes-update route — 82 passed; 2 flag-gated PostgreSQL cases skipped.
- `git diff --check` — passed.
### Deviations
Attempt 2 replaces the identity-only guard with a credential-pair provenance protocol tied to the actual bounded OAuth response and transaction binding, as required by the review. The first PostgreSQL run exposed a test helper trying to enumerate offline Sessions outside a binding; it now reads the SDK-generated persisted ID through the independent observer client. The corrected PostgreSQL run passed using the Colima endpoint and socket override shown above.
### Assumptions
Same canonical PostgreSQL database; exact identity, lifecycle lock, SDK wrappers and provider recovery are fixed by binding revision 2. No schema changes or service-side OAuth configuration changes were made.
### Unresolved Issues
None identified in the scoped implementation or validation. Attempt 2 is awaiting architect review; `completion_mode: developer` is preserved and explicit developer completion remains pending.
### Architectural Concerns
Architect review remains pending. No architect review decision has been made by the developer implementation.

## Developer Self-Review
### Review Status
Passed — Attempt 2 self-review. The Attempt 1 P1 is corrected and the report reconciled against every Work Item and Acceptance Criterion. Attempt 2 implementation/report are published for architect review. `completion_mode: developer` is preserved; explicit developer completion remains pending. No architect acceptance decision has been made by this agent.
### Reviewed Files
All files listed under Completion Report → Files Changed, including the coordinated SessionStorage, Shopify facade/transport, lifecycle routes and services, and focused test fixtures.
### Validation Reviewed
`npm run typecheck`; `npm run build`; required focused Vitest command (11 passed, 2 PostgreSQL tests skipped in unflagged mode); focused coordination/session-storage service tests (14 passed); disposable PostgreSQL independent-client real SDK refresh and uninstall/reinstall race tests (2 passed); `git diff --check`.
### Self-Review Findings
The credential provenance guard now admits the replacement Session constructed by the installed SDK only when its shop/Session identity is bound and its credential pair came from the bounded OAuth response in that transaction. The accepted credential fingerprint advances after each successful store, so an older pair cannot overwrite the committed replacement. Real PostgreSQL SDK refresh, Shared-client serialization, stale-store, and uninstall/reinstall checks pass. The only raw SDK public auth calls are invoked inside the facade wrappers; the facade exports wrapped auth functions and coordinated storage.
### Decision
Submit Attempt 2 for `moda_architect` review. Do not mark complete until the developer explicitly requests completion after architect review.

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

## Developer Self-Review — Attempt 2

### Review Outcome
Passed. The architect's Attempt 1 P1 is addressed. Attempt 2 has been submitted for architect review; the task remains developer-controlled and is not complete.

### Finding-to-Evidence Reconciliation
- Fresh SDK Session rejected by identity-only provenance: replaced with same-binding OAuth response credential provenance plus bound shop/actual Session ID checks; the current persisted credential fingerprint advances on write.
- Stale credential overwrite: unit coverage rejects the earlier pair after a fresh pair is stored in the same binding; the PostgreSQL integration also rejects a stale Session from a later binding.
- Actual SDK compatibility: PostgreSQL tests perform public `sdk.authenticate.admin` bootstrap, obtain the ID from the Session row actually persisted by the SDK, expire it, and run public `sdk.unauthenticated.admin` refresh through the composed real storage adapter. Authentication succeeds and both access and refresh tokens are persisted.
- Concurrency/lifecycle: a separate Shared Prisma client waits on the same advisory gate while the actual SDK refresh is held; the refresh issues one request and Shared observes its committed token. The second PostgreSQL case retains SDK refresh, uninstall, and actual SDK reinstall ordering.
- Foreign and unbound writes remain denied by the existing focused assertions.

### Decision
Submit Attempt 2 to `moda_architect`. Preserve Attempt 1 review history and `completion_mode: developer`; wait for architect review and an explicit developer completion request before marking complete.


## Developer Self-Review - Changes Requested — Attempt 1 (2026-11-06)

**Review fails: actual installed SDK refresh Sessions are rejected by the storage guard.** Status Ready, executor/claimed_at null, Attempt 1 unchanged; developer execution/completion modes preserved. Earlier implementer self-review does not establish acceptance against this finding.

### P1 — Support freshly constructed SDK refresh/exchange Sessions safely

`app/services/shopify-session-storage.server.ts:165-166` requires `binding.loadedOfflineSessions.has(session)` for every existing-row update. The installed Shopify React Router helper `helpers/ensure-offline-token-is-not-expired.mjs` calls `api.auth.refreshToken`, obtains its returned Session and passes it to `storeSession`. The installed Shopify API `auth/oauth/refresh-token.mjs` constructs that result through `createSession`, whose public implementation returns `new Session`. It is therefore a different object from the one returned by storage.loadSession, even for the same legitimate shop/session identity while the coordination gate is held. The WeakSet test rejects the normal SDK refresh and token-exchange path with SESSION_IDENTITY_CONFLICT after possible remote rotation; authentication cannot reliably persist the new pair.

Replace JavaScript object-identity provenance with a safe coordinated protocol that permits a newly constructed Session from an actual scoped SDK refresh/exchange while still rejecting a stale store and mismatched shop/actual session ID. Preserve existing public SDK wrappers, transaction-bound storage, same gate/row authority and no uncoordinated writes. Do not weaken identity checks merely to make the write succeed.

### Required actual SDK regression

Exercise the installed public SDK authentication/refresh flow with controlled fetch and real SessionStorage composition. Verify the newly constructed refreshed Session is accepted under its correct binding, both tokens commit atomically, authentication succeeds, and stale/foreign/unbound stores remain denied. Extend the separate-client PostgreSQL race to include that actual SDK call, preserving exactly one normal remote refresh and uninstall/reinstall ordering. The current PostgreSQL callback at `tests/integration/shopify-offline-coordination.test.ts:85-91` manually loads a Session, changes its properties through installRefresh and stores that same object; it cannot expose this compatibility failure and must not be labelled proof of the installed SDK refresh path.

### Review evidence

Reviewed implementation `39d2f917a074173eec99214a9d71689952d58dfc`, the facade/transport/wrapper, storage guard and test sources, and the installed SDK refresh/token-exchange/createSession implementations. Independently ran `vitest run tests/unit/shopify-offline-coordination.test.ts`: **10 passed**, exit 0; local log `/tmp/arch061-shopify-review.log`. The green unit callbacks do not replace actual SDK coverage. Submitted typecheck/build, 82-test extra set and two PostgreSQL cases were reviewed as reported evidence, not independently rerun. No Docker/live Shopify run was performed.

Preserve the published implementation/report and dedicated worktrees. Reclaim through the normal developer workflow, implement the safe correction, add actual SDK regression/race evidence and resubmit. No implementation edit, new claim, attempt increment, package change, main merge, deployment or downstream promotion occurs in this review. Explicit completion remains unavailable until a passing review is durable.


## Developer Self-Review Passed / Accepted — Attempt 2 (2026-11-06)

**Review passed; the prior P1 SDK Session compatibility finding is resolved.** Reviewed implementation `17fb986a8f0635ea771327261d84b548d06d36cb`, matching its pushed task branch. Status Review, executor/claimed_at null, Attempt 2 unchanged. Developer execution/completion modes are preserved; explicit `/moda_developer_update ARCH-061-SHOPIFY-001 complete` remains required. No downstream dependency is promoted by review alone.

### Correction review

The storage guard no longer depends on the JavaScript identity of a loaded Session. It captures the current persisted credential-pair fingerprint under the binding and records replacement pair fingerprints from the bounded same-host OAuth response. A newly constructed SDK Session may persist the corresponding replacement; shop and actual Session ID checks remain mandatory, the stored fingerprint must still match current scoped state, and successful writes advance state and clear pending provenance. Stale/unbound/foreign stores remain denied. The correction changes four files, retaining the public wrapper/ALS/transaction boundary.

Inspected the revised separate-client PostgreSQL regression source: it installs through public `sdk.authenticate.admin`, observes the actual generated Session ID, expires the stored row and refreshes through public `sdk.unauthenticated.admin`. It asserts the SDK returns a newly constructed Session, atomically commits the pair and serializes the independent Shared read. The second case covers actual SDK refresh, concurrent uninstall and SDK reinstall exchange under the domain gate. This replaces the earlier hand-mutated callback evidence rather than relabelling it as real SDK execution.

### Validation and limits

Independently ran the focused unit/coordination/storage three-file set: **14 tests passed**, exit 0; local evidence `/tmp/arch061-shopify-attempt2-review.log`. Independently checked correction whitespace and implementation task-ref equality. Inspected the actual SDK callsites used by the new integration tests and the source changes.

Reviewed submitted Attempt 2 typecheck/build, additional lifecycle/privacy regression results and the recorded **two passing PostgreSQL cases** using separate clients with owned Testcontainers cleanup. Those checks and Docker execution were not independently repeated by this review. No live Shopify/provider or consumer rollout proof is implied. Source retains no raw SDK auth/storage escape and the earlier broad implementation review remains applicable outside the corrected provenance path.

Canonical dedicated worktree/branch, preparation/claim, publication and validation evidence are recorded in the Completion Report. Implementation/parent worktrees were clean before this review update. Only the parent task record is published here; no source change, attempt/claim creation, gitlink/main merge, package publication, deployment or downstream execution occurs. Explicit developer completion and terminal cross-service proof remain separately gated.
