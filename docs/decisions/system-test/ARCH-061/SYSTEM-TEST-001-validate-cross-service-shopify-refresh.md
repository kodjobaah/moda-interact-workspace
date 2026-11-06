---
id: ARCH-061-SYSTEM-TEST-001
architecture_id: ARCH-061
title: validate cross service shopify refresh
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-061-SHARED-002", "ARCH-061-SHOPIFY-001", "ARCH-061-BACKGROUND-001", "ARCH-061-COMMERCE-001", "ARCH-061-MCP-001"]
enables: []
created: 2026-11-05
updated: 2026-11-06
---
# Validate cross service shopify refresh

## Architecture
ARCH-061; docs/architecture/ARCH-061-shopify-offline-token-refresh-coordination.md. Coordinator moda_architect.

## Objective
Validate cross service shopify refresh using the published injected-client Shared runtime.

## Context
Background bespoke refresh currently reads/refreshes/writes unlocked; App SDK refreshes before storage write. Consumers use the same persisted rotating offline credential.

## Scope
Task-owned moda-interact-system-test changes and focused validation only. Cross-repository paths below are read-only baseline evidence unless owned by this task.

| Existing file | Symbol/surface | Required change |
|---|---|---|
| moda-interact-system-test/package.json | declared harness scripts | Add focused scenario via established harness after implementation acceptance. |


## Out of Scope
Central token service, agent tools, sibling imports, credential UI, schema changes, node_modules patches, automatic execution, claims or main merges.

## Requirements
The entire parent architecture runtime/bounds/SDK/lifecycle/ambiguity matrix is normative. Factory accepts each service's local Prisma client at composition. Lock before read/decision/remote refresh; write-only locking is insufficient. No exactly-once remote guarantee across crash. Use the binding revision public-wrapper/ALS/lifecycle gate architecture; do not choose a different synchronization mechanism.

## Work Items
- [ ] Create scripts/arch061-verify-cutover.mjs and test/harness/arch061-cutover.test.js implementing the binding architecture manifest checks; test missing/stale/remaining-old-replica rejection.
- [ ] Exercise actual App SDK and each consumer composition with separate clients/processes against disposable PostgreSQL/provider mock.
- [ ] Cover every normative matrix row, install/uninstall ordering, ambiguous save failure and safe recovery evidence.
- [ ] Verify all active writer paths coordinated, secret canaries absent and Commerce status never refreshes.

## Interfaces / Contracts
Shared Node-only factory and structural transaction interface/error categories defined by SHARED-001 and published by SHARED-002. Consumers inject local client/config/fetch and translate errors. No sibling source imports; no browser exports or raw token DTOs. App owns all SDK/lifecycle mutation entrypoints.

## Dependencies
- ARCH-061-SHARED-002
- ARCH-061-SHOPIFY-001
- ARCH-061-BACKGROUND-001
- ARCH-061-COMMERCE-001
- ARCH-061-MCP-001

## Enables
None

## Acceptance Criteria
- [ ] Exercise actual App SDK and each consumer composition with separate clients/processes against disposable PostgreSQL/provider mock.
- [ ] Cover every normative matrix row, install/uninstall ordering, ambiguous save failure and safe recovery evidence.
- [ ] Verify all active writer paths coordinated, secret canaries absent and Commerce status never refreshes.
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
| NEW test/arch061-shopify-refresh.test.js | cross-process integration scenario | Launch separate actual service compositions and App SDK facade against same disposable DB + barrier-controlled OAuth server; test normative matrix. |
| moda-interact-system-test/package.json | test/typecheck scripts | Run new scenario via node --test; retain existing scripts. |
| NEW test/fixtures/arch061-shopify-refresh.js | fixtures | Seed canonical online/offline, duplicate, expired-refresh, wrong-shop and install lifecycle fixtures; no real provider credentials. |

### Task-specific deterministic assertions
- [ ] Spawn App SDK and Background/Commerce/MCP at barrier on same expired selected stored row: count1 normal provider refresh, all use same committed pair.
- [ ] Inject remote success+save failure then recover with persisted refresh per official provider behavior; permit second remote recovery call, assert no exactly-once crash claim.
- [ ] Install/uninstall/reinstall+scope update order and metadata-only Commerce count0 assertions pass.

Create the new focused test paths listed in this exact command where absent; preserve existing test files. Required focused command: `node --test test/arch061-shopify-refresh.test.js`. Run declared `npm run build`; App/Commerce/MCP additionally `npm run typecheck`; System Test uses `npm run typecheck` only.

## Implementation Notes
No execution started. Use launcher isolated/synchronized task worktrees when requested. Use the installed SDK surfaces and official recovery policy identified in revision 2. Node recovery uses workspace bootstrap. No new schema or alternative lock primitive is authorized. Publication is release mechanics only.

## Completion Report
### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
Definition only.
### Deviations
None
### Assumptions
Same canonical PostgreSQL database; exact identity, lifecycle lock, SDK wrappers and provider recovery are fixed by binding revision 2.
### Unresolved Issues
None blocking architecture definition. Revision-1 feasibility questions are superseded by binding revision 2 decisions.
### Architectural Concerns
Implement binding revision 2 exactly; report actual incompatibility with evidence instead of selecting alternate architecture.

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

## Dependency Reconciliation — 6 November 2026

ARCH-061-MCP-001 Attempt 1 is explicitly developer-completed following passing
scoped review `7f61bde93`, implementation `c9ca303`. SHARED-002 and SHOPIFY-001
are also Complete. BACKGROUND-001 and COMMERCE-001 remain Ready, not Complete,
in current canonical task records and fetched origin/main; this task therefore
remains Pending with attempt 0, executor/claimed_at null. MCP is no longer an
incomplete prerequisite. Terminal/manual invocation and operator cutover gates
are unchanged; no claim or execution is authorized by this reconciliation.
