---
id: ARCH-026-API-002
architecture_id: ARCH-026
title: Establish WooCommerce installation connection and authentication
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-API-001
  - ARCH-026-DATABASE-001
enables:
  - ARCH-026-WOOCOMMERCE-003
  - ARCH-026-API-003
created: 2026-10-02
updated: 2026-10-03
---

# Establish WooCommerce installation connection and authentication

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Implement the secure hosted-API boundary that allows one installed Moda Interact WooCommerce plugin to:

1. prove control of its canonical WordPress/WooCommerce site without already possessing a Moda credential;
2. create or reconnect the corresponding Woo-backed Moda `Shop` and `woocommerce.WooCommerceInstallation`;
3. receive one new long-lived installation credential whose raw value is returned once and never persisted by Moda; and
4. use that credential on subsequent API requests to resolve one authenticated Woo installation principal and authoritative `shopId`.

The bounded runtime is:

```text
WordPress/PHP plugin
    |
    | POST /v1/woocommerce/installations/connect
    | siteUrl + attemptId + ephemeral bootstrapSecret
    v
moda-interact-api
    |
    +-- canonicalise site URL
    +-- issue one random challenge
    +-- environment-gated site-control callback to the installed plugin
    +-- verify HMAC site-control proof
    |
    v
PostgreSQL transaction / compare-and-swap
    |
    +-- first connection -> create Woo Shop + installation
    `-- reconnect       -> rotate installation credential
    |
    v
return raw installation credential once
    |
    | subsequent request
    | X-Moda-Installation-Id + Authorization: Bearer <credential>
    v
WooInstallationAuthenticator
    |
    v
{ installationId, shopId, credentialVersion, canonicalSiteUrl }
```

This task establishes installation connection/authentication only. It MUST NOT implement merchant feature queries, onboarding UI/state, billing, recovery, commerce-event ingestion, Redis/BullMQ publication or Gateway deployment.

## Context

`ARCH-026-API-001` establishes the backend-only Node/TypeScript API runtime and canonical Prisma/database dependency.

`ARCH-026-DATABASE-001` establishes:

```text
commerce.Shop.platform = SHOPIFY | WOOCOMMERCE

woocommerce.WooCommerceInstallation
    id
    shopId
    canonicalSiteUrl
    status = ACTIVE | REVOKED
    credentialDigest
    credentialVersion
    credentialIssuedAt
    revokedAt
```

DATABASE-001 deliberately stores no raw installation secret and leaves secret generation, hashing, constant-time comparison, canonical-site normalization, reconnection/rotation and HTTP authentication to this API task.

The Woo plugin executes on merchant-controlled infrastructure. An unauthenticated caller claiming a merchant site therefore cannot be allowed to create/claim that merchant's Moda Shop merely by supplying the URL. API-002 must prove live control of the installed plugin before issuing a Moda credential. Production verification remains public-HTTPS-only. ARCH-026 also permits one explicit local-development mode so a developer can exercise the same challenge/credential flow against a local WordPress/WooCommerce site without paying for or operating a public WordPress host.

The proof mechanism is an ephemeral bootstrap challenge. The raw bootstrap secret exists only for one connection attempt and is never durable Moda state.

`WooCommerceInstallationStatus` is installation/authentication state only. This task MUST NOT encode merchant onboarding, plan activation, billing attention or subscription state into that enum or installation row. Existing Shopify `shopify.ShopSettings.onboardingCompleted` is not reused by Woo here, and no Woo-specific duplicate onboarding flag is created.

ARCH-026 remains pre-production for WooCommerce, so the external connection contract may be introduced directly as v1 without a legacy compatibility adapter.

## Scope

Modify only `moda-interact-api` implementation/test/documentation files required for this connection/authentication capability plus the repository's nested `database/` gitlink required to consume the accepted DATABASE-001 schema.

Expected implementation areas are conceptually:

```text
src/
  woocommerce/
    installation/
      connection-service.ts
      site-url.ts
      site-verifier.ts
      credential.ts
      authenticator.ts
      routes.ts
      types.ts
openapi/
  woocommerce-installation-v1.yaml
tests/
  ... focused connection/authentication tests
```

The exact repository-local filenames may differ when a clearer bounded structure exists.

### Canonical database dependency

Before implementing API-002, update the API repository's nested:

```text
database/
```

gitlink to the architect-accepted `moda-interact-database` `main` commit containing `ARCH-026-DATABASE-001`.

Generate Prisma from that pinned schema.

Do not copy/redeclare the Woo installation model locally and do not modify schema/migrations in this task.

### External HTTP contract ownership

The plugin is PHP and cannot import the TypeScript Shared package. The public Woo installation HTTP contract is therefore owned by `moda-interact-api` and MUST be documented in a version-controlled OpenAPI 3.1 document:

```text
openapi/woocommerce-installation-v1.yaml
```

The OpenAPI contract and runtime validators must agree for every route/body/response defined by this task.

Do not create a duplicate structurally similar contract in `moda-interact-shared` merely to support the PHP client.

### Connection verification mode

Support exactly two server-side verification modes:

```text
public
local-development
```

Use one explicit runtime setting, for example:

```text
MODA_WOOCOMMERCE_CONNECTION_MODE=public|local-development
```

Requirements:

- default to `public` when the setting is absent;
- `local-development` is an explicit developer opt-in, never inferred from the submitted hostname, request headers or browser input;
- startup/configuration MUST fail closed if `local-development` is selected while `NODE_ENV=production`;
- the production Render/Gateway topology continues to run with `NODE_ENV=production`, so the local-development verifier cannot be enabled accidentally in production;
- both modes use the same request schema, bootstrap-secret lifecycle, challenge nonce/HMAC proof, credential issuance/rotation, database transaction/CAS rules and secret-redaction requirements;
- the mode changes only which callback network identities/schemes may be verified and how TLS is applied to that callback transport.

The selected mode is server configuration, not part of the external connect request and not a merchant-editable field.

### Connection route

Expose:

```text
POST /v1/woocommerce/installations/connect
```

This route intentionally does not require a pre-existing Moda installation credential.

It accepts exactly the bounded logical request:

```json
{
  "siteUrl": "https://merchant.example/optional-wordpress-base",
  "attemptId": "<UUID>",
  "bootstrapSecret": "<base64url encoding of exactly 32 random bytes>"
}
```

Additional unknown request fields MUST be rejected.

Request limits:

```text
Content-Type: application/json
maximum encoded request body: 8 KiB
siteUrl: <= 512 UTF-8 bytes
attemptId: UUID
bootstrapSecret: base64url, exactly 32 decoded bytes
```

The API MUST NOT log, persist, meter or return the bootstrap secret.

### Canonical Woo site URL

Canonicalize `siteUrl` before any DNS/network/database action.

The accepted `public` production shape is:

```text
scheme:       https only
credentials:  forbidden
hostname:     DNS hostname only; IP literals forbidden
port:         default HTTPS only (no explicit non-443 port)
query:        forbidden
fragment:     forbidden
path:         allowed for WordPress subdirectory installations
```

When and only when `local-development` mode is explicitly enabled, a callback site may instead use a local development identity:

```text
scheme:       http or https
credentials:  forbidden
hostname:     localhost, *.local, or a loopback/private/link-local IP/DNS target
port:         explicit local-development ports permitted
query:        forbidden
fragment:     forbidden
path:         allowed for WordPress subdirectory installations
```

A public/global target encountered while `local-development` mode is enabled still uses the normal production/public HTTPS policy; local-development mode MUST NOT turn arbitrary public HTTP origins into accepted targets.

Canonicalization must:

- use URL parsing rather than string concatenation;
- lower-case/normalize the hostname through the URL implementation;
- remove a trailing slash from a non-root WordPress base path;
- represent root as the origin without a trailing `/`;
- reject an empty/invalid hostname;
- reject a canonical result exceeding 512 UTF-8 bytes.

Examples:

```text
https://Example.COM/            -> https://example.com
https://Example.COM/store/      -> https://example.com/store
https://example.com/store?q=1   -> rejected
http://example.com              -> rejected
https://127.0.0.1               -> rejected
https://user:pass@example.com   -> rejected

local-development only:
http://woocommerce-sandbox.local/ -> http://woocommerce-sandbox.local
http://127.0.0.1:8080/             -> http://127.0.0.1:8080
```

The canonical URL is the authoritative Woo site identity stored in `woocommerce.WooCommerceInstallation.canonicalSiteUrl`.

For a newly created Woo tenant, set:

```text
commerce.Shop.platform      = WOOCOMMERCE
commerce.Shop.shopifyShopId = NULL
commerce.Shop.domain        = canonicalSiteUrl
commerce.Shop.status        = ACTIVE
```

Do not create `shopify.ShopSettings`, billing/subscription state, Merchant Knowledge state or any other provider/business record as part of connection.

### Site-control challenge contract

For every valid connection attempt, generate a cryptographically random 32-byte challenge nonce and encode it as base64url.

The API MUST call exactly:

```text
GET <canonicalSiteUrl>/wp-json/moda-interact/v1/connection/challenge
    ?attempt_id=<attemptId>
    &nonce=<challengeNonce>
```

where the path is appended to the canonical WordPress base path without allowing the request body to choose another callback origin/path.

Expected response:

```json
{
  "attemptId": "<same UUID>",
  "nonce": "<same challenge nonce>",
  "proof": "<base64url HMAC-SHA256>"
}
```

Additional response fields MUST be rejected.

The proof input is the exact UTF-8 byte sequence:

```text
moda-interact-connect-v1\n<attemptId>\n<nonce>\n<canonicalSiteUrl>
```

and the HMAC key is the decoded 32-byte `bootstrapSecret` supplied in the original connect request.

The API computes the expected HMAC-SHA256 locally and compares the decoded proof using constant-time comparison.

A response with the wrong attempt ID, nonce, proof, media type or schema is rejected with zero database mutation.

### Environment-gated challenge transport

The site-control callback is an outbound request to user-supplied network identity and MUST be treated as an SSRF boundary.

In `public` mode, before connection:

- resolve the canonical hostname through a bounded DNS resolver;
- reject zero answers;
- reject literal/non-DNS hosts before resolution;
- reject the entire result if any resolved IPv4/IPv6 address is loopback, private, link-local, multicast, documentation/special-use, carrier-grade/NAT/shared, unspecified, non-global or IPv4-mapped to a denied IPv4 address;
- select/pin one validated public/global address for the request;
- preserve the original hostname for TLS SNI and certificate validation.

In `local-development` mode, the verifier may additionally accept only explicitly local targets: `localhost`, `.local` hostnames, or DNS/IP identities resolving exclusively to loopback/private/link-local addresses. It MUST still resolve and pin the actual callback peer; a mixed local/public answer set is rejected rather than broadening the trust boundary. Public/global targets continue to use the `public` HTTPS policy even while local-development mode is enabled.

During connection in both modes:

- connect only to the pinned approved address;
- verify the connected peer address still matches an approved resolved address;
- do not use environment/system HTTP proxies;
- do not send cookies or Moda credentials;
- do not follow redirects;
- permit only one GET;
- use a total challenge deadline <= 5 seconds;
- accept only a JSON response body <= 4 KiB after decoding;
- reject unsupported compression/media types/invalid UTF-8/NUL content;
- terminate/abort the response stream promptly on deadline/body-limit failure;
- for HTTPS callbacks, preserve the original hostname for TLS SNI/certificate validation;
- plain HTTP is permitted only for an approved local target while explicit `local-development` mode is active.

Do not merely perform a preflight DNS check followed by an ordinary unpinned `fetch`, because that re-opens DNS rebinding between validation and connection.

Reuse an architecture-approved generic transport only if the required pinning/TLS/peer-verification guarantees are actually available in the API dependency graph. Do not import another service's repository-local implementation by path and do not create a new cross-repository shared framework solely for this task.

### Installation credential

After successful site proof, generate a cryptographically random 32-byte installation credential and expose it to the caller as base64url.

Persist only:

```text
SHA-256(raw installation credential bytes)
```

as the exact 32-byte `credentialDigest` required by DATABASE-001.

Never persist the raw credential in PostgreSQL, logs, traces, audit metadata, error objects or test snapshots.

The successful response is bounded to:

```json
{
  "installationId": "<WooCommerceInstallation.id>",
  "shopId": "<Shop.id>",
  "canonicalSiteUrl": "https://merchant.example",
  "credential": "<raw base64url credential returned once>",
  "credentialVersion": 1,
  "connection": "CREATED"
}
```

or for an existing installation:

```json
{
  "installationId": "<same WooCommerceInstallation.id>",
  "shopId": "<same Shop.id>",
  "canonicalSiteUrl": "https://merchant.example",
  "credential": "<new raw base64url credential returned once>",
  "credentialVersion": "<previous + 1>",
  "connection": "RECONNECTED"
}
```

The exact HTTP status may distinguish create/reconnect, but the OpenAPI document and implementation/tests must agree.

### First connection transaction

Only after successful site proof may the API create durable state.

The first connection MUST atomically create:

```text
commerce.Shop
woocommerce.WooCommerceInstallation
```

with the same `shopId` relation.

If `canonicalSiteUrl` or the derived `Shop.domain` becomes concurrently claimed, the losing operation must return a bounded conflict and MUST NOT create a second Shop/installation.

No raw secret may survive a failed transaction.

### Reconnect / credential rotation

A successfully verified connection request for an existing `canonicalSiteUrl` MUST reconnect to the existing tenant rather than create another Shop.

Reconnect MUST:

- preserve `Shop.id`;
- preserve `WooCommerceInstallation.id`;
- preserve all merchant/business state;
- never create/reset `shopify.ShopSettings.onboardingCompleted`;
- never reset onboarding, subscription, billing or entitlement state;
- generate a new raw installation credential;
- replace `credentialDigest`;
- increment `credentialVersion` by exactly one;
- set `credentialIssuedAt = now()`;
- set installation `status = ACTIVE`;
- clear `revokedAt`;
- if Shop status is `UNINSTALLED`, restore it to `ACTIVE` and clear uninstall/reinstall timestamps;
- if Shop status is `SUSPENDED`, reject reconnection and leave all state unchanged.

Credential rotation MUST use a compare-and-swap condition against the credential version observed before the challenge. If another connection attempt changed the installation during site verification, the losing request returns a bounded conflict rather than rotating the credential again and silently invalidating the winner's returned secret.

For a first-time race, rely on the DATABASE-001 unique constraints and convert the losing unique-conflict outcome to the same bounded concurrent-connection response.

### Site URL changes

Changing an already-associated Woo Shop from one canonical site URL to another is OUT OF SCOPE.

A caller cannot identify an existing installation by installation ID during this unauthenticated bootstrap route and ask to move it to another site URL.

Do not silently merge two site URLs or move an installation between Shops.

### Steady-state installation authentication

Create one reusable API-owned authentication boundary for subsequent Woo routes.

The canonical HTTP credentials are:

```text
X-Moda-Installation-Id: <WooCommerceInstallation.id>
Authorization: Bearer <raw installation credential>
```

Authentication MUST:

1. parse both headers strictly and reject malformed/duplicate credentials;
2. load the installation by `id` with its Shop in one bounded query;
3. require installation `status = ACTIVE` and `revokedAt IS NULL`;
4. require Shop `platform = WOOCOMMERCE` and `shopifyShopId IS NULL`;
5. require Shop `status = ACTIVE` for normal authenticated use;
6. decode the presented base64url credential to exactly 32 bytes;
7. SHA-256 the raw presented bytes;
8. compare the 32-byte digest with `credentialDigest` using constant-time comparison;
9. return an internal principal only after all checks pass.

Internal principal shape:

```ts
{
  installationId: string;
  shopId: string;
  canonicalSiteUrl: string;
  credentialVersion: number;
}
```

Do not trust a caller-supplied shop ID, domain/site URL, platform or credential version.

Externally, missing installation, revoked installation, wrong secret and incompatible Shop state MUST all use the same generic unauthenticated response so the API does not become an installation-enumeration oracle.

### Authentication probe

Expose one authenticated non-business endpoint solely to prove the principal boundary:

```text
GET /v1/woocommerce/installation
```

It MUST use the reusable authenticator and return only:

```json
{
  "installationId": "...",
  "shopId": "...",
  "canonicalSiteUrl": "...",
  "credentialVersion": 1
}
```

It must not return credential digests, raw credentials, billing state, customer data, merchant configuration or other application data.

This route exists as a security/contract probe for WOO-003 and may remain as a bounded connection-status primitive.

### CORS/browser boundary

These routes are server-to-server PHP-plugin APIs.

Do not enable permissive browser CORS for them and do not expose installation credentials to browser JavaScript.

The future React UI calls the local WordPress REST layer; PHP owns the remote Moda credential.

### Logging / sensitive data

Use the canonical Shared structured logger.

Never log:

- `bootstrapSecret`;
- installation credential;
- `credentialDigest`;
- Authorization header;
- challenge proof;
- complete request/response bodies.

Connection/authentication logs may contain bounded identifiers only after they are known, such as `installationId`, `shopId`, outcome/reason and duration.

Before durable identity exists, use a bounded one-way fingerprint of the canonical site URL rather than logging the full URL if diagnostic correlation is needed.

Authentication failure logs MUST NOT echo presented credentials.

## Out of Scope

- WordPress/PHP implementation of the challenge endpoint.
- WordPress storage of Moda installation credentials.
- Woo Admin React UI.
- Merchant onboarding state or provider-neutral onboarding migration.
- `shopify.ShopSettings` changes.
- Billing/subscriptions.
- Feature/entitlement queries.
- Recovery configuration or recovery reads.
- Merchant Knowledge.
- Product/coupon/discount APIs.
- CommerceAgent.
- WhatsApp.
- Cart/checkout/order event ingestion.
- Redis/BullMQ.
- Background changes.
- Installation revocation/uninstall endpoint.
- Changing an installation to a new canonical site URL.
- Multiple Woo installations for one Shop.
- Multiple Shops for one canonical Woo site URL.
- Gateway/Render public routing.
- Hosted merchant HTML/React UI.
- API keys embedded in the WordPress/browser bundle.
- A generic identity/authentication framework for non-Woo providers.

## Requirements

### R1 — Proof before durable mutation

No Shop/installation/credential database mutation may occur until the site-control challenge has succeeded.

### R2 — Production/public verification remains strict

In `public` mode, connection proof must never permit the API to connect to loopback, private, link-local, metadata/special-use or otherwise non-global addresses, including mixed DNS answer sets and IPv4-mapped IPv6 forms. HTTPS with normal hostname/certificate verification remains mandatory.

### R3 — Local development is explicit and fail-closed

Local HTTP/private/loopback/`.local` verification is permitted only when the server-side connection mode is explicitly `local-development`. That mode cannot start under `NODE_ENV=production` and cannot be selected by the connect request/browser.

### R4 — Address pinning and peer validation survive both modes

The actual callback socket must be pinned to an approved resolved address with connected-peer validation and no redirects. HTTPS callbacks preserve the original hostname for SNI/certificate verification; local-development HTTP only removes TLS from an explicitly local target, not challenge proof or network pinning.

### R5 — Ephemeral bootstrap secret

The bootstrap secret is a one-attempt proof key only. It is never durable Moda state and never becomes the long-lived installation credential.

### R6 — Raw installation credential returned once

The API persists only the SHA-256 digest. Successful connect/reconnect returns the newly generated raw credential once; no later endpoint can retrieve it.

### R7 — Reconnect reuses the same tenant

A verified reconnect for the same canonical site URL must retain the same Shop and installation IDs and rotate only installation credential/lifecycle fields defined by this task.

### R8 — Concurrent connection safety

Two overlapping valid connection attempts cannot leave two Shops/installations for one site or cause a successful caller's newly returned credential to be silently invalidated by a racing rotation.

### R9 — Onboarding/billing separation

Connection/reconnection must not mark onboarding complete, create/reset Shopify settings, activate a billing plan, create subscription state or otherwise encode account/billing lifecycle into `WooCommerceInstallationStatus`.

### R10 — Constant-time credential verification

Steady-state authentication hashes the presented high-entropy raw secret and compares fixed-length digests using a timing-safe comparison primitive.

### R11 — Tenant identity is server-resolved

Authenticated routes derive `shopId` exclusively from the installation row. Caller-supplied tenant identity is never trusted.

### R12 — Enumeration-resistant authentication failure

Missing ID, revoked installation, invalid credential and incompatible tenant state return the same public authentication failure shape.

### R13 — PHP-consumable versioned contract

OpenAPI v1 documents the exact connection, challenge and authentication-probe contracts for the later Woo plugin task.

## Work Items

- [ ] Update the API repository's `database/` gitlink to the accepted DATABASE-001 commit and regenerate Prisma.
- [ ] Add strict canonical Woo site URL parsing/normalisation for public mode plus the explicitly gated local-development variant.
- [ ] Add bounded connect request/response runtime validators.
- [ ] Implement the cryptographic challenge nonce/HMAC proof contract.
- [ ] Implement environment-gated challenge transport: strict public/global HTTPS validation plus explicit local-development local-target allowance while retaining DNS/address pinning, peer checking, limits, no redirects and HMAC proof.
- [ ] Implement first-connection Shop + WooCommerceInstallation transaction.
- [ ] Implement reconnect credential rotation with credential-version compare-and-swap/concurrency handling.
- [ ] Generate 32-byte installation credentials and persist only their 32-byte SHA-256 digests.
- [ ] Implement the reusable Woo installation authenticator.
- [ ] Add the authenticated `GET /v1/woocommerce/installation` probe.
- [ ] Add the OpenAPI 3.1 installation v1 contract.
- [ ] Add bounded structured logging with secret/body redaction requirements.
- [ ] Add focused unit/security/integration tests, including controlled public TLS/DNS verification and local-development HTTP/private-target fixtures.
- [ ] Document local connection/authentication testing against a local WordPress/WooCommerce fixture without requiring public/paid WordPress hosting.

## Interfaces / Contracts

### Contract owner

`ARCH-026-API-002`

### Public API owner

`moda-interact-api`

### Consumer

Future `ARCH-026-WOOCOMMERCE-003` PHP plugin implementation.

### Portable contract

`openapi/woocommerce-installation-v1.yaml`

### Connect

```text
POST /v1/woocommerce/installations/connect
```

Request:

```json
{
  "siteUrl": "https://merchant.example",
  "attemptId": "UUID",
  "bootstrapSecret": "base64url(32 bytes)"
}
```

### Challenge callback required from future plugin task

```text
GET <canonicalSiteUrl>/wp-json/moda-interact/v1/connection/challenge
    ?attempt_id=<UUID>
    &nonce=<base64url(32 bytes)>
```

Proof canonical message:

```text
moda-interact-connect-v1\n<attemptId>\n<nonce>\n<canonicalSiteUrl>
```

Proof algorithm:

```text
HMAC-SHA256(key = decoded bootstrapSecret, message = canonical message)
```

### Steady-state authentication

```text
X-Moda-Installation-Id: <installation ID>
Authorization: Bearer <base64url raw installation credential>
```

### Authenticated probe

```text
GET /v1/woocommerce/installation
```

### Database contract owner

`ARCH-026-DATABASE-001`

Models consumed:

```text
commerce.Shop
woocommerce.WooCommerceInstallation
```

Do not duplicate them in the API repository.

## Dependencies

- `ARCH-026-API-001`
- `ARCH-026-DATABASE-001`

Both tasks must be `complete` and architect-accepted before API-002 becomes Ready.

API-002 must consume the accepted DATABASE-001 database gitlink rather than an in-review task commit.

## Enables

- `ARCH-026-WOOCOMMERCE-003`
- `ARCH-026-API-003`

WOO-003 may then implement the PHP-side bootstrap-secret lifecycle, public challenge callback, local WordPress REST façade and secure storage/use of the returned installation credential.

API-003 may add the first real DB-backed merchant read/write capability behind the authenticated installation principal.

## Acceptance Criteria

- [ ] API-002 uses the accepted DATABASE-001 Prisma schema through the pinned `database/` submodule.
- [ ] `POST /v1/woocommerce/installations/connect` rejects invalid/oversized/unknown-field request bodies before DNS/network/database action.
- [ ] `public` mode canonical site validation enforces HTTPS, DNS hostname, default HTTPS port, no credentials/query/fragment and deterministic WordPress base-path normalization.
- [ ] `public` mode rejects literal IPs and private/loopback/link-local/special-use/non-global IPv4/IPv6 answers, including mixed public/private sets.
- [ ] `local-development` mode is disabled by default and startup/configuration fails if it is requested under `NODE_ENV=production`.
- [ ] Explicit `local-development` mode accepts a local HTTP fixture such as `http://woocommerce-sandbox.local` and a loopback/private local target while continuing to reject arbitrary public HTTP targets.
- [ ] The challenge socket is pinned to an approved resolved address in both modes; HTTPS callbacks validate the original hostname via TLS.
- [ ] Connected-peer mismatch is rejected.
- [ ] Redirects are not followed.
- [ ] Challenge deadline, response-body and media-type/UTF-8 limits are enforced.
- [ ] Wrong challenge attempt ID, nonce or HMAC proof causes zero durable mutation.
- [ ] Bootstrap secret never appears in durable state or captured logs.
- [ ] Successful first connection atomically creates exactly one Woo Shop and installation.
- [ ] New Woo Shop has `platform = WOOCOMMERCE`, `shopifyShopId = NULL`, `domain = canonicalSiteUrl` and active installation state.
- [ ] First connection creates no Shopify `ShopSettings` and no billing/subscription/onboarding state.
- [ ] Successful reconnect for the same canonical URL preserves Shop/installation IDs and all unrelated merchant state.
- [ ] Reconnect rotates the raw credential, increments `credentialVersion` exactly once and persists only the new 32-byte SHA-256 digest.
- [ ] Reconnect does not reset onboarding/billing/entitlement state.
- [ ] Suspended Shop reconnection is rejected without mutation.
- [ ] Concurrent create/reconnect attempts cannot create duplicate tenants or silently invalidate a winning request's credential.
- [ ] The long-lived credential is exactly 32 random bytes before base64url encoding.
- [ ] `WooInstallationAuthenticator` derives `shopId` only from the installation row and uses constant-time digest comparison.
- [ ] Missing, revoked, wrong-secret and incompatible-Shop authentication failures have one generic public response shape.
- [ ] `GET /v1/woocommerce/installation` succeeds only with valid installation credentials and returns no secrets/business data.
- [ ] No permissive CORS/browser credential exposure is introduced.
- [ ] OpenAPI 3.1 matches runtime validators and response/error shapes.
- [ ] No billing, recovery, event-ingress, Redis/BullMQ or Background functionality is introduced.

## Validation

Run the API repository's declared validation commands and record exact commands/results.

Required validation categories:

- [ ] clean dependency install from lockfile;
- [ ] Prisma generation from the accepted DATABASE-001 gitlink;
- [ ] typecheck;
- [ ] lint;
- [ ] focused unit tests for public/local-development URL canonicalization, mode gating and credential encoding/digest/constant-time comparison;
- [ ] focused challenge HMAC contract tests with fixed vectors;
- [ ] controlled transport tests for public HTTPS success, private IPv4/IPv6 rejection in public mode, IPv4-mapped rejection, mixed answers, peer mismatch, certificate/SNI behavior, redirect rejection, deadline and body limits;
- [ ] controlled local-development transport tests for HTTP `.local` and loopback/private success, explicit-port handling, peer pinning, public-HTTP rejection and production-mode fail-closed behavior;
- [ ] request parser/body-limit/unknown-field tests proving invalid requests perform zero network/database work;
- [ ] disposable PostgreSQL integration test for first connection;
- [ ] disposable PostgreSQL integration test for reconnect/credential rotation;
- [ ] concurrent first-connect test;
- [ ] concurrent reconnect/CAS test;
- [ ] suspended-Shop reconnect rejection test;
- [ ] authentication probe tests for valid, missing ID, malformed secret, wrong secret, revoked installation and incompatible Shop state;
- [ ] test proving raw/bootstrap credentials do not appear in structured logs;
- [ ] OpenAPI/runtime-contract consistency test;
- [ ] production build;
- [ ] `git diff --check`;
- [ ] clean repository/worktree evidence required by the task protocol.

Do not satisfy the SSRF acceptance contract only with mocked `fetch`. At least one controlled TLS/socket fixture must prove that the actual transport pins the resolved address while retaining the original hostname for TLS verification and checks the connected peer.

No live/public merchant WooCommerce store is required for API-002 validation. The accepted development path may use a local WordPress/WooCommerce fixture; WOO-003 proves the PHP integration and terminal system validation proves the deployed public-mode policy separately.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
        ->
set status: review
        ->
return control to moda_architect
        ->
STOP
```

Do not begin WOO-003 or API-003.

## Implementation Notes

Keep this security boundary narrow and explicit rather than creating a generic OAuth/API-key framework.

Use Node cryptographic primitives for CSPRNG, SHA-256, HMAC-SHA256 and timing-safe comparison.

The installation credential is intentionally high entropy; a fast SHA-256 digest is appropriate for lookup verification because it is not a human password. Do not replace it with plaintext storage. Do not expose `credentialDigest` outside the authentication implementation.

Do not persist the ephemeral bootstrap secret merely to simplify the proof flow. Site verification occurs within the bounded connect request lifecycle before the database transaction.

Do not perform outbound challenge I/O inside the Prisma transaction.

Do not trust a successful TLS connection alone as site-control proof; the exact HMAC challenge response is required.

Do not trust site URL as authentication after connection. All subsequent Woo merchant API calls use installation ID + credential and resolve the Shop server-side.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- API-001 provides the accepted backend-only HTTP/database runtime.
- DATABASE-001 provides the accepted cross-schema Woo installation model and constraints.
- The later Woo plugin task will generate/store the ephemeral bootstrap secret in WordPress server-side state and implement the exact public challenge callback defined here.
- The later Woo plugin task will store the returned long-lived installation credential server-side and never expose it to React/browser code.

### Unresolved Issues

None within this task's bounded v1 connection/authentication contract.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
