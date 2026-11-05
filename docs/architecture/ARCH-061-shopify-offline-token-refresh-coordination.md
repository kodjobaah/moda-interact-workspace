---
id: ARCH-061
title: Shopify offline token refresh coordination
status: agreed
coordinator: moda_architect
created: 2026-11-05
updated: 2026-11-05
---
# Shopify offline token refresh coordination

## Normative shared runtime contract
Publish a Node-only Shared factory (new API, proposed name createShopifyOfflineTokenProvider) accepting the composing service's own Prisma client through a narrow structural transaction interface, injected bounded fetch/clock, cancellation and a server-only OAuth configuration resolver. It returns getAccessToken(shop) and coordinated mutation/lifecycle primitives needed by App. No Shared-owned Prisma singleton, sibling repository imports, central HTTP/token service, model tool or agent capability. Application configuration supplies OAuth identity; never accept client-provided credentials or arbitrary refresh origin. Normalize and validate the canonical myshopify.com domain before constructing Shopify OAuth URL.

getAccessToken owns the ENTIRE interactive transaction: locate canonical offline identity, SELECT FOR UPDATE the shopify.Session row, reread all access/refresh expiry and token values under lock, return existing token if valid, otherwise refresh once only when eligible and save the validated access/refresh pair and both expiry timestamps atomically in that transaction. Never do an unlocked read-to-decide-refresh followed by write-only locking. Nonexpiring offline tokens remain supported. Use a common documented five-minute refresh skew compatible with installed SDK; inject clock for deterministic tests. Reject online sessions, malformed/duplicate canonical identities, expired/missing refresh tokens and invalid date arithmetic. Bound token lengths, response bytes and positive finite expiry durations; return only after commit. Do not retain process-wide token caches across rotation.

Primary concurrency mechanism is the Session row lock. Canonical identity is offline_<canonical-domain> as verified against the installed Shopify session-ID helper during implementation, not findFirst ordered by expiry. Existing unexpected duplicate/noncanonical offline rows must fail with an explicit diagnostic and a separately reviewed reconciliation decision; never silently choose a different token. Cross-process transactions serialize on the SAME database and canonical row. No promise across independently replicated databases.

A row lock cannot lock an absent row: install/uninstall can delete/recreate that ID while a stale SDK callback holds old material. App must establish an explicit lifecycle ordering contract before acceptance. Prefer a narrow existing stable Shop row lock acquired before Session row lock by ALL participating callers, if the canonical shop lifecycle guarantees that row exists; verify that guarantee. If absent-install bootstrap cannot use it, STOP and return the exact gap for an architect-approved lifecycle primitive rather than inventing an advisory-lock framework, adding schema or claiming serialization. Never resurrect a deleted offline session from stale refresh results. Lock order, shop-generation/current-install verification, install creation, rotation and uninstall deletion must be consistent across writers. Session row locking alone is sufficient only after absence/recreation and all-writer ordering are proved safe.

## Bounds, errors and unavoidable ambiguity
Set explicit finite lock-wait, transaction maxWait/timeout, refresh network/body deadline and abort propagation. Defaults must satisfy network/body deadline < transaction budget with commit margin; do not hold transaction through unrelated provider calls. Refresh is the deliberate bounded exception to the usual no-network-in-transaction preference because rotation must serialize. Validate status/content and fields before any token update. Reject expired refreshTokenExpires before provider I/O. Roll back malformed/failing calls; no partial token pair save. Logs/errors contain fixed reason codes and bounded status only, never token values, OAuth body, secret, raw provider response or Prisma error.

PostgreSQL and Shopify cannot commit atomically. A timeout/reset after request acceptance, process death after remote rotation, or DB save/commit failure can leave rotated credentials ambiguous. Do NOT promise exactly-once remote refresh under crash, blindly retry the old refresh token, or return an unsaved new token. Classify this as REFRESH_OUTCOME_UNKNOWN, reread durable state in a NEW coordinated transaction, and return an already committed currently-valid pair only when identity/generation is still current. Otherwise fail unavailable and use Shopify's documented supported recovery/reauthorization rules, verified during implementation; do not assume token replay/grace/reuse. Do not invent a durable recovery flag without Database ownership. Preserve an expired durable access state so subsequent attempts cannot treat it as valid; prohibit automatic refresh retries for unknown outcomes within the request. Across process restart, documented provider recovery limits must be explicit; if reliable prevention/recovery needs durable extra state, stop for a Database task. Invalid refresh credentials require existing reinstall/reauthorization flow; never configure credentials in Studio.

## SDK writer requirement and feasibility gate
Installed App code uses PrismaSessionStorage(prisma) and expiringOfflineAccessTokens:true. Installed SDK authenticate/admin/authenticate.mjs loads session BEFORE strategy; helpers/ensure-offline-token-is-not-expired.mjs refreshes through api.auth.refreshToken THEN calls storeSession. A storage adapter locking storeSession alone is TOO LATE. App task must prove an officially supported composition hook/wrapper enclosing earliest read, expiry decision, remote refresh and persistence in the same coordinator. Inventory authenticate.admin, unauthenticated/admin, auth callback/token exchange, SDK request retries, afterAuth writes, scope changes and uninstall paths. Use official installed SDK extension points and preserve SDK online/session-token validation. No node_modules edits or undocumented monkey patch. If SDK cannot expose the required boundary, stop App task and return a concrete supported integration alternative for architectural approval; downstream adoption stays gated. Never declare coordination complete from passing a custom helper test while SDK can still refresh independently.

## Producer/consumer and ownership
Shared owns reusable rotation/transaction mechanics and error categories under a published Node-only package subpath; App, Background, Commerce and MCP each instantiate once with THEIR local Prisma client and existing OAuth configuration source. Shared must not import @prisma/client from a sibling service or force a single generated Prisma version. Consumer adapters preserve service auth/tenant selection, translate bounded errors and propagate deadlines. App owns installation lifecycle and every SDK writer. Background preserves domain call sites. Commerce uses the provider for execution; metadata-only Connections status never triggers refresh/decryption/network and only represents availability, not live health. MCP uses it in its offline-session reader, preserving scope validation and typed failures. Provider credentials remain server-side fetched integration state, never entered in Studio.

## Deterministic acceptance matrix
| Trigger | Required result |
|---|---|
| Two distinct Prisma clients/processes race on same expired row | One normal successful remote refresh; waiter rereads committed pair under lock and sends no second refresh |
| Different shops | Independent locks; no global serialization |
| Valid/nonexpiring access | No refresh, unchanged credential pair |
| Expired refresh token or missing pair | No provider call; explicit unavailable/reauth state |
| Malformed response/non-2xx/body overflow | No partial writes; bounded safe errors |
| Lock wait or fetch timeout/caller abort | Finite termination, rollback, released lock; classify possible remote acceptance as unknown |
| Remote success then injected save/commit failure | Never return uncommitted token; unknown-outcome classification and documented recovery |
| Stale SDK preloaded session races service refresh | SDK cannot refresh outside pre-read lock; cannot overwrite newly rotated pair |
| Install/uninstall/reinstall race | No stale token/session resurrection; agreed lifecycle generation/order enforced |
| OAuth client config missing or bad shop origin | Fail before network; no secret diagnostics |
| Credential canaries in response/errors | Absent from logs/client DTO/HTML/test reports |
| Commerce status render | Zero token refresh/provider network; execution obtains current token via shared runtime |

## Deployment and scope
PRODUCTION / COMPATIBLE ROLLOUT. Existing rotating tokens may exist. Shared implementation -> publication -> App all-writer coordination acceptance -> independent Background/Commerce/MCP adoption -> terminal System Test. App can be accepted only with proven SDK/lifecycle boundary. During actual coordinated cutover pause/drain token-using work and App auth writers using an explicitly validated operational procedure; no procedure is asserted verified by these definitions. Deploy compatible binaries/config, verify writer inventory, then resume. Old uncoordinated processes cannot remain active alongside new coordination. No queue deletion. Rollback must preserve current rotated pair and all-writer locking; do not simply restore an uncoordinated binary against rotating state. No schema/infrastructure/secret duplication planned; newly discovered lifecycle/recovery persistence needs return to architect. Existing generic logging reused; no new metrics framework.

## Tasks
| Task | Owner | Status | Dependencies |
|---|---|---|---|
| ARCH-061-SHARED-001 | shared | Ready | - |
| ARCH-061-SHARED-002 | shared | Pending | ARCH-061-SHARED-001 |
| ARCH-061-SHOPIFY-001 | shopify | Pending | ARCH-061-SHARED-002 |
| ARCH-061-BACKGROUND-001 | background | Pending | ARCH-061-SHARED-002, ARCH-061-SHOPIFY-001 |
| ARCH-061-COMMERCE-001 | commerce | Pending | ARCH-061-SHARED-002, ARCH-061-SHOPIFY-001 |
| ARCH-061-MCP-001 | mcp | Pending | ARCH-061-SHARED-002, ARCH-061-SHOPIFY-001 |
| ARCH-061-SYSTEM-TEST-001 | system-test | Pending | ARCH-061-SHARED-002, ARCH-061-SHOPIFY-001, ARCH-061-BACKGROUND-001, ARCH-061-COMMERCE-001, ARCH-061-MCP-001 |

## Open implementation gates
SDK supported pre-read extension feasibility, stable absent-session install ordering and documented provider ambiguous-outcome recovery must be proven, not assumed. Return gaps before adoption.
