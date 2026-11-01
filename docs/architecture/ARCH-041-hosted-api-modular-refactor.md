---
id: ARCH-041
title: Hosted API modular refactor with behavioural parity
status: in_progress
coordinator: moda_architect
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041: Hosted API modular refactor with behavioural parity

## Status

**In Progress — Revision 6 (2026-10-16), post-extraction reconciliation.** The `moda-interact-workspace-ARCH-041-API-013(1).zip` snapshot records API-001–API-012 and API-014 Complete, with API-013 `in_progress` (developer execution), and SYSTEM-TEST-001 still Pending. The primary structural refactor is present; additional cleanup patches and full validation remain outstanding. Canonical individual task YAML governs status. The ZIP does not establish live worktree/remote state. No `_index.md` is modified.

## Problem

Historical baseline (before ARCH-041): the hosted Node.js `moda-interact-api` had coherent merchant, billing and WooCommerce feature directories, but concentrated responsibilities. Between the 2026-10-15 23:26:53 and 2026-10-16 00:01:47 snapshots, 77 production TypeScript modules were unchanged. The following sizes and layout describe that **pre-refactor problem**, not the present implementation:

- `src/woocommerce/installation/routes.ts` (~665 lines) handles Woo connection/probe **and** merchant bootstrap/context and billing HTTP handlers/delegation.
- `src/index.ts` constructs services and providers and wires the umbrella router.
- `src/billing/presentation/billing-read.service.ts` (~733 lines) combines repeatable-read snapshots, integrity rules and response projections.
- `src/billing/commands/recurring-subscription-command.service.ts` (~566 lines) and `recovery-credit-purchase-command.service.ts` (~532 lines) combine transactional intent, external provider calls and guarded outcomes.

**Existing work to retain:** ARCH-036-API-004 has introduced a deliberate `tests/` convention for discount offers: three unit tests in `tests/unit/merchant/discount-offers/` and three PostgreSQL suites in `tests/integration/merchant/discount-offers/`, with `tests/README.md`, adjusted TypeScript/test scripts and a disposable PostgreSQL runner. The task is `complete` at Attempt 2 in the latest snapshot. This is sound groundwork; it does not mean production routing or authentication has yet been refactored.

The initiative is a **structural maintainability** refactor, not a request to fix speculative billing or authentication defects.

## Goals

1. Establish a reusable executable parity baseline, including explicit authentication/authorization denial behaviour, **without runtime modifications**.
2. Preserve **feature-first production source** (`merchant/`, `billing/`, `woocommerce/`) with each route owned by the feature it serves.
3. Adopt the accepted **test-type-first, feature-second** convention: unit tests in `tests/unit/<domain>/<feature>/`, PostgreSQL integration tests in `tests/integration/<domain>/<feature>/`; the developer-requested final cleanup has relocated all legacy colocated tests out of `src/`.
4. Extract bounded HTTP domain handlers from Woo installation routing, retaining precise path/method/handler ordering.
5. Keep one explicit Node HTTP dispatch boundary and a thin startup composition root; construct services once and inject dependencies.
6. Separate billing snapshot reads from deterministic response projection without weakening the single `RepeatableRead` transaction.
7. Separate each billing command's transactional intent from provider invocation and guarded outcome reconciliation, retaining independence between recurring and recovery-credit policy.
8. Establish `src/auth/woo-installation/` as the single shared API-facing installation identity owner, preserving existing credential, revocation and tenant checks; do not merge the distinct security protocols.
9. Establish `src/http/route-handler.ts` as a minimal Node HTTP dispatch interface, then share further API-local HTTP mechanics **only when semantically identical**; retain all published v1 response/error/header semantics.
10. Keep tasks small, one repository and logical agent per task; retain canonical worktree, task and architect-review governance.

## Non-Goals

- No changes to v1 endpoint paths, HTTP methods, authentication semantics, wire contracts, status/error codes, strict payload parsing or logging semantics.
- No change to existing installation credential format, bearer validation, WordPress admin permissions, signed provider webhooks, REST-read callback capabilities, credential rotation/revocation policy or billing command authorization. Unresolved policy questions require **separate architectural agreement**, not incidental refactoring.
- No new authentication protocols, generic JWT/global authentication middleware, altered credential-rotation policy or extra per-request DB check. The existing `WooInstallationAuthenticator` is **relocated without behaviour change** to `src/auth/woo-installation/` by a dedicated task after the other affected source streams are accepted.
- No generic test-helper framework or change to the system-test repository's independent conventions. The original non-goal of avoiding a bulk test migration was explicitly superseded by the user's 2026-10-16 request to separate **all** remaining colocated tests; test assertions and behaviour are preserved.
- No switch from Node `node:http`, generic cross-domain controllers/services/repositories hierarchy, database schema/migration, Shared package publication, queue/Background change or new Gateway infrastructure.
- No WooCommerce plugin changes (including separate WordPress REST nonce/capability consistency work), Shopify UI feature work, new REST endpoints or unrelated clean-up.
- No task materialisation, branch creation, code implementation, review acceptance or `_index.md` edits merely from issuing this portable design packet.

## Current Architecture

**Inspected source:** `moda-interact-workspace-ARCH-041-API-013(1).zip`, before the follow-up cleanup patches. API-001–012 and API-014 are Complete in the snapshot's task YAML. API-013 is in progress and is **not accepted**.

```text
src/index.ts
  -> src/composition/{merchant,billing,woocommerce,routes}.ts
  -> src/server.ts (health, ordered HTTP dispatch, lifecycle)
     -> Woo REST-read callback (if enabled), signed billing webhook
     -> 9 merchant feature-owned handlers
     -> 3 billing feature-owned handlers
     -> Woo installation connection and probe

src/auth/woo-installation/    canonical bearer identity
src/woocommerce/installation/site-proof.ts    distinct site-control HMAC
src/http/{route-handler,body,headers,response}.ts    small Node-only HTTP mechanics

billing/presentation/billing-read.service.ts
  -> ONE RepeatableRead transaction -> snapshot reader -> pure projections
billing/commands/*-command.service.ts
  -> intent transaction -> provider call -> guarded outcome transaction

tests/unit/                  unit, HTTP, contract, real-composition tests
tests/integration/           17 PostgreSQL suites, organised by domain
src/                         production TypeScript only: no *.test.ts files
```

The subsequent bounded cleanup removes obsolete Woo installation constant re-exports and duplicate route-handler interfaces, adopts identical no-store response helpers, registers all 17 PostgreSQL suites in the standard integration chain, and adds a real-factory HTTP route-registration regression. The intentionally private Woo product-read port is **retained**, not treated as proven dead code.

`npm test` discovers `tests/unit/**/*.test.ts` only. `npm run typecheck` covers `src/` and `tests/`; `npm run build` compiles runtime source only. `npm run test:integration` executes distinct disposable database runners, with migration-backed validation for billing, provider outcomes, recovery policy, webhook receipts, Woo REST-read and discount offers. The installation runner's `prisma db push` checks **are not** billing-integrity proof. Results must be recorded from actual execution; this documentation does not claim a PostgreSQL run.

## Proposed Architecture

### Feature-first runtime layout; test-type-first validation layout

This was the **target responsibility map**. Actual implemented filenames and ownership supersede illustrative placeholders below; no empty placeholder files are required.

```text
moda-interact-api/
├── src/
│   ├── index.ts                               # process entrypoint/startup
│   ├── server.ts                              # node:http, health, dispatch, lifecycle
│   ├── database.ts
│   ├── runtime-config.ts
│   ├── composition/                           # implemented startup wiring only
│   │   ├── merchant.ts                        # feature handler/service assembly
│   │   ├── billing.ts                         # billing clients/handlers
│   │   ├── woocommerce.ts                     # Woo connection, callbacks, webhook
│   │   └── routes.ts                          # explicit ordered route composition
│   ├── http/                                  # implemented API-local HTTP boundary
│   │   ├── route-handler.ts                   # minimal shared handle(...) contract
│   │   ├── body.ts                            # bounded stream/strict body helper
│   │   ├── headers.ts                         # raw-header cardinality
│   │   └── response.ts                        # shared exact no-store JSON writer
│   ├── auth/                                  # canonical Woo bearer installation identity
│   │   └── woo-installation/
│   │       ├── principal.ts                   # canonical Woo installation shop principal
│   │       ├── authenticator.ts               # moved unchanged validation behaviour
│   │       ├── credential.ts                  # existing Woo installation credential codec
│   ├── merchant/
│   │   ├── bootstrap/routes.ts                # merchant-owned GET handler
│   │   ├── store-context/routes.ts            # merchant-owned PUT handler
│   │   ├── store-categories/                  # existing feature implementation
│   │   ├── recovery-summary/
│   │   ├── recovery-policy/
│   │   ├── recoveries/                        # accepted ARCH-040 extensions retained
│   │   └── discount-offers/
│   ├── billing/
│   │   ├── presentation/
│   │   │   ├── routes.ts                      # both GET billing and plans
│   │   │   ├── billing-read.service.ts        # existing public facade
│   │   │   ├── billing-snapshot.reader.ts      # NEW, ONE RepeatableRead transaction
│   │   │   └── billing-projection.ts          # NEW pure projection
│   │   ├── commands/
│   │   │   ├── routes.ts                      # POST/DELETE subscriptions and POST credit purchases
│   │   │   ├── recurring-subscription-command.service.ts
│   │   │   ├── recurring-intent.ts             # NEW transactional intent
│   │   │   ├── recurring-outcome.ts            # NEW guarded outcome
│   │   │   ├── recovery-credit-purchase-command.service.ts
│   │   │   ├── recovery-credit-intent.ts       # NEW transactional intent
│   │   │   └── recovery-credit-outcome.ts      # NEW guarded outcome
│   │   └── purchase-history/                  # existing GET purchase handler
│   └── woocommerce/
│       ├── installation/
│       │   ├── routes.ts                      # NARROWED to connect/probe
│       │   ├── connection-service.ts
│       │   ├── site-verifier.ts
│       │   └── site-proof.ts                  # Woo connect HMAC site proof, extracted by API-014
│       ├── rest-read/                         # existing callback/grant boundaries
│       └── billing/                           # existing provider and signed webhooks
├── tests/
│   ├── README.md                              # canonical test-type-first convention
│   ├── unit/
│   │   ├── http/                              # dispatch/body/header/response tests
│   │   ├── composition/                       # real route-registration checks
│   │   ├── auth/woo-installation/             # negative bearer/tenant/rotation parity tests
│   │   ├── merchant/{bootstrap,store-context,discount-offers}/
│   │   └── billing/{presentation,commands}/
│   ├── integration/
│   │   ├── auth/woo-installation/              # only for actual persisted/auth races
│   │   ├── merchant/discount-offers/          # EXISTING
│   │   └── billing/{presentation,commands}/   # migration-backed persistence evidence
│   └── helpers/                              # only demonstrably shared fixtures
├── scripts/                                  # includes API-001 migration-backed billing PG runner
├── openapi/                                  # existing unchanged v1 contracts
├── database/                                 # canonical Prisma submodule
└── package.json
```

The tree is illustrative: feature folders may contain additional accepted source files, and exact extracted filenames may vary if the actual mainline dictates. **`src/auth/woo-installation/` and `src/http/route-handler.ts` are explicit ARCH-041 targets** (API-014 and API-012 respectively), not placeholders. Move existing bearer authentication and generic credential primitives without changing values, protocols, DB predicates or request semantics. The current `credential.ts` also contains Woo connection-specific `createSiteProof`/`verifySiteProof`: API-014 moves those functions to `woocommerce/installation/site-proof.ts`, preserving the exact HMAC input and comparison. `installation-state.ts` and additional HTTP helpers are optional only when backed by real extracted responsibilities. The existing `tests/unit/auth/` location is retained for targeted negative/security tests.

### Request dependency direction

```text
index.ts (process startup)
    |
    v
composition/{merchant,billing,woocommerce,routes}.ts
    |                              |
    v                              v
server.ts (health + dispatch) --> src/http/route-handler.ts interface
                                      |
                              ordered feature-owned routes
                                      |
                           route-specific authentication/validation
                                      |
                              injected feature services
                                      |
                         +------------+------------+
                         v                         v
                    Prisma DB                  Woo provider
```

- Composition depends on features; features do not depend on `composition/`, `index.ts` or `server.ts`.
- Routes enforce the established security boundary for their own endpoint and receive injected services; no global bearer policy for connect, callbacks or webhook. Authenticated merchant/billing routes import the Woo installation authenticator and principal from `src/auth/woo-installation/` after API-014; Woo connection establishment retains ownership of issuance/reconnection and site verification.
- Feature services do not import `node:http` or write responses. Prisma remains inside services/snapshot/intent/outcome modules; there is no mandatory generic repository layer.
- Billing provider calls stay outside PostgreSQL transactions and are not moved to generic HTTP helpers.
- Continue using published Shared security/logging primitives; do not create local generic cryptographic or logging implementations. API-014 keeps the existing Woo site-control HMAC policy in `woocommerce/installation/`; the API-wide auth boundary must never depend on that Woo feature.

### Method-specific route ownership

| Request | Target route owner | Security |
|---|---|---|
| `GET /health/live`, `GET /health/ready` | `server.ts` | Deliberately public health checks |
| `POST /v1/woocommerce/installations/connect`, `GET /v1/woocommerce/installation` | `woocommerce/installation/routes.ts` | Site-ownership challenge for connect; current installation bearer for probe |
| Woo REST-read authorization callback/grant routes | existing `woocommerce/rest-read/` | Existing one-time capability and callback validation; **not** generic installation middleware |
| Woo billing webhook | existing `woocommerce/billing/webhooks/` | Existing HMAC-signed webhook verification |
| `GET /v1/merchant/bootstrap` | `merchant/bootstrap/routes.ts` | Existing Woo installation bearer principal |
| `PUT /v1/merchant/store-context` | `merchant/store-context/routes.ts` | Existing Woo installation bearer principal and current service guard |
| Recoveries, policies, categories and discounts | existing `merchant/<feature>/` | Existing Woo installation principal, per-route authorization |
| `GET /v1/billing`, `GET /v1/billing/plans` | `billing/presentation/` routes | Existing Woo installation bearer principal |
| `GET /v1/billing/recovery-credit-purchases` | existing `billing/purchase-history/routes.ts` | Existing Woo installation bearer principal |
| `POST /v1/billing/recovery-credit-purchases` | `billing/commands/recovery-credit.routes.ts` | Existing Woo installation bearer principal + idempotency/command validation |
| Subscription POST/switch/DELETE endpoints | `billing/commands/subscription.routes.ts` | Existing Woo installation bearer principal + command validation |

The **GET/POST path overlap** for purchases is intentional; handlers must dispatch by both method and path, returning `false` if they do not own the request. Preserve Woo REST-read callback precedence ahead of generic installation routing and existing safe 404/failure handling. API-008 must compare the API-001 route inventory with **all subsequently accepted ARCH-026/035/036/040 routes** and add missing characterization before relocating handlers; API-012 must verify the same accepted inventory against final composition (including auth and wrong-method behaviour).

### Billing internals remain independent

- Presentation: `BillingPresentationReadService.read(principal, now)` -> one `RepeatableRead` snapshot reader -> deterministic projection/validation, preserving all v1 response fields and errors.
- Recurring commands: shop/subscription-locked intent transaction -> provider create/switch/cancel **outside transaction** -> guarded persisted provider outcome.
- Credit purchases: purchase-specific locked intent transaction -> Woo provider charge **outside transaction** -> credit-specific guarded outcome.
- Do **not** replace recurring and credit commands with a generic workflow engine or alter persisted state, fingerprint/lock rules or provider retry semantics.

## Request / Event Flow

- Health endpoints stay separate from tenant auth: `/health/live` is independent of PostgreSQL and `/health/ready` uses the same deadline/503 semantics.
- Connect retains its challenge/site-verification contract; installation probe, merchant and billing operations retain the existing authenticated principal (`installationId`, `shopId`, `canonicalSiteUrl`, `credentialVersion`) from `WooInstallationAuthenticator`. API-014 moves this implementation from `woocommerce/installation/` to `auth/woo-installation/` **without changing its query, digest, raw-header matching or principal fields**. The resolved shop is authoritative.
- Woo signed billing webhooks and REST-read callback/capability flows are separate trust boundaries. A global middleware must not misclassify them.
- Unknown paths or wrong methods retain the bounded `404`. First-match routing and the credit-purchase GET/POST collision are characterized in API-001 before extraction.
- Billing commands retain idempotency keys, strict JSON/header limits, durable replay, provider failure and outcome handling. Billing reads retain bounded, tenant-scoped transactional snapshot semantics.
- The WordPress plugin's per-controller capability/nonce differences and the exact in-flight credential-rotation authorization policy are **not** being changed by ARCH-041; capture the current API behaviour and refer policy changes to a separate explicit architecture/task.

## Repository Responsibilities

| Repository | Responsibility | Change required? |
|---|---|---|
| `moda-interact-api` / `moda_api` | HTTP route extraction, billing internals, service wiring, local tests | **Yes** |
| `moda-interact-system-test` / `moda_system_test` | Final black-box API behavioural parity, negative security and provider/database proof | **Yes, terminal validation only** |
| `moda-interact-database` | Canonical Prisma schema and migrations | No |
| `moda-interact-shared` | Existing published logging/contracts/crypto | No |
| `moda-interact-gateway` | Render/gateway topology | No |
| `moda-interact-woocommerce`, Shopify, Background, Messaging, Commerce | Existing producers/consumers and async workflows | No |

If inspection in an implementation task establishes a genuine new cross-repository contract or Shared primitive gap, stop that affected task and return to `moda_architect` rather than duplicating a generic implementation.

## Data Model

Unchanged. PostgreSQL remains the durable source of truth, with existing billing operation, subscription, purchase, entitlement, shop and Woo installation records. No schema/index/migration, persistence state, lock-key, uniqueness or lifecycle changes are authorised.

## Contracts

Unchanged: documented current v1 API route paths, HTTP methods, authentication, strict bodies/headers, JSON responses, response status/error codes, `Cache-Control`, bounded metadata, provider error codes, OpenAPI examples and existing live/readiness contracts. API-specific HTTP DTOs remain owned by API; cross-service reusable primitives remain owned by published Shared. No new cross-repo wire contract, producer or consumer is introduced.

## Consistency and Transactions

- `BillingPresentationReadService.read` retains a **single `RepeatableRead` read transaction** and the same integrity checks; do not move later dependent reads outside its snapshot.
- Recurring and credit-purchase command intent retains shop/subscription row locking, tenant checks, existing replay fingerprint and `ReadCommitted` transactional boundaries; no network calls inside transactions.
- Provider state recording retains guarded compare-and-set from `INITIATING`, idempotent replay, provider-reference collision rules, outcome-unknown versus definitive rejection semantics, and advisory transaction locking where currently used.
- No additional durable writes or implicit state transitions in read handlers.

## Ordering

Explicit first-match HTTP route ordering must preserve `/health/*`, Woo REST-read callbacks, signed billing webhook callbacks and method-specific merchant/billing handlers. There is no new event ordering mechanism or background processing.

## Failure Handling

Preserve observable current failure modes and bounded bodies: unauthorized, malformed/oversized JSON, provider unavailable, operation conflict, unknown provider outcome, suspected provider-reference collision, database integrity violations and 404. Do not turn uncertain provider outcomes into retries that could double-charge; do not introduce fallback authentication or leak SQL/provider exceptions. Logs remain Shared structured logs and redacted.

## Scalability

The initiative is not a throughput redesign. Avoid adding extra database round-trips, longer transactions or per-request service composition. The established hosted API synchronous merchant workload is distinct from Shopify event ingress (~20,000 events/minute design reference), Background queue throughput and CommerceAgent turns. Existing bounded queries and concurrency invariants remain in force. Validate any observed performance regression as an unplanned change.

## Security

**Installation bearer principal:** `src/woocommerce/installation/authenticator.ts` currently validates a single installation ID header, Bearer secret, stored SHA-256 digest, credential version, active installation and active Woo shop. Merchant/billing endpoints consume the same `WooInstallationPrincipal`; do not reinterpret user-supplied shop IDs as authority. Preserve constant-time comparison, revocation/rotation decisions and deterministic errors.

**Distinct trust boundaries:** connect uses Woo site-control proof; signed billing webhooks use HMAC verification; REST-read authorization/callbacks use their existing one-time capability and client-credential checks; live/ready are intentionally public. Composition must register their existing per-route guards, not install generic authentication. Recheck that a rejected/missing/duplicate/rotated/revoked installation credential cannot reach a business command or provider call, and that webhook/callback signatures fail closed.

**Policy questions deferred:** WooCommerce WordPress-admin REST permissions are owned by `moda_woocommerce`, not this API-only initiative. A new uniform policy for credentials rotated while a paid command is in-flight would be a behavioural/security change; the existing command/service transaction guards remain unchanged unless separately accepted. Never make security changes as a side effect of moving files.

No secret, Authorization header, sensitive provider payload or unhashed credential is logged or exposed to browser code. No generic JWT/security framework is introduced. The **location** of the existing Woo installation authenticator and principal changes in API-014; its authentication **policy and runtime behaviour do not**.

## Observability

Reuse `@modainteract/moda-interact-shared/logging` and current semantic event names, bounded redacted fields, operation IDs and durations. Do not duplicate generic HTTP telemetry already available from approved framework/instrumentation or introduce a new service-local generic logger. No Gateway/OTLP infrastructure changes are justified by the structural refactor.

## Rollout / Migration

Classification: **structural compatibility rollout** (preserve production compatibility regardless of environment). Deploy one internally reviewed API implementation at a time and verify stable v1 contracts. No database or Shared publication gate; no consumer redeployment is required solely by a code extraction. Roll back by reverting the API implementation commit(s), with no data reversal or queue drain. If testing finds behaviour divergence, fix the same task before acceptance rather than hiding it behind a new feature.

## Existing-work coordination

**Architectural sequencing decision (2026-10-16):** complete the ARCH-041 hosted API refactor before initiating further unrelated API feature work. The **2026-10-16 11:42 snapshot** shows ARCH-041-API-001 through API-007 Complete. API-008 now depends only on completed ARCH-041-API-001, not on ARCH-026/035/036/040 feature tasks.

Preserve every endpoint actually served by the execution baseline, including already-integrated functionality from other initiatives. Source presence does **not** convert an unfinished feature task into Complete; its canonical status and review remain separate. Do not implement pending feature specifications inside route-extraction tasks. Coordinate concurrent changes to shared route/composition files rather than starting conflicting feature work.

**Scope of this revision:** only ARCH-041 architecture and task documents are modified. ARCH-026/035/040 task metadata remains untouched. Consequently this patch expresses a **sequencing policy**, not an enforced launcher hold on those outside tasks; the developer/coordinator must refrain from starting them until ARCH-041 integrated validation and explicitly coordinate their resumption. No non-system-test task gains a system-test dependency.

## Decisions / Tasks

**The original API-001–013 IDs and API-014 authentication extraction remain unchanged.** `src/auth/woo-installation/` is the planned shared identity owner, `src/http/route-handler.ts` is mandatory in API-012, and additional HTTP helpers remain evidence-based in API-013. The authentication task follows the billing and route extractions, without waiting for unrelated feature implementations.

The snapshot records task definitions and statuses but does not prove live task worktrees or branch materialisation. `Ready` is YAML dependency eligibility, not an execution claim. Re-gate the canonical workspace before execution.

| Task | Owner | Status | Depends on |
|---|---|---|---|
| ARCH-041-API-001 HTTP/contract characterisation | moda_api | Complete | — |
| ARCH-041-API-002 Extract billing snapshot reads | moda_api | Complete | API-001 |
| ARCH-041-API-003 Extract billing response projection | moda_api | Complete | API-002 |
| ARCH-041-API-004 Extract recurring intent transaction | moda_api | Complete | API-001 |
| ARCH-041-API-005 Extract recurring provider outcome | moda_api | Complete | API-004 |
| ARCH-041-API-006 Extract credit-purchase intent transaction | moda_api | Complete | API-001 |
| ARCH-041-API-007 Extract credit-purchase provider outcome | moda_api | Complete | API-006 |
| ARCH-041-API-008 Extract billing read HTTP handlers | moda_api | Complete | API-001 |
| ARCH-041-API-009 Extract billing command HTTP handlers | moda_api | Complete | API-008 |
| ARCH-041-API-010 Extract merchant bootstrap HTTP handler | moda_api | Complete | API-009 |
| ARCH-041-API-011 Extract merchant store-context HTTP handler | moda_api | Complete | API-010 |
| ARCH-041-API-014 Relocate Woo installation authentication boundary | moda_api | Complete | API-003, API-005, API-007, API-011 |
| ARCH-041-API-012 Unnest registration and composition | moda_api | Complete | API-014 |
| ARCH-041-API-013 Deduplicate API-local HTTP mechanics | moda_api | In Progress | API-012 |
| ARCH-041-SYSTEM-TEST-001 Black-box API parity | moda_system_test | Pending | API-003, API-005, API-007, API-013, API-014 |

### Dependency graph

```text
API-001 [COMPLETE]
  +-- API-002 -> API-003 [COMPLETE]
  +-- API-004 -> API-005 [COMPLETE]
  +-- API-006 -> API-007 [COMPLETE]
  +-- API-008 -> API-009 -> API-010 -> API-011 [COMPLETE]
                                    |
                     API-003/005/007/011
                                    v
                             API-014 [COMPLETE]
                                    |
                             API-012 [COMPLETE]
                                    |
                             API-013 [IN PROGRESS]
                                    |
                             SYSTEM-TEST-001 [PENDING]
```

API-013 still requires developer validation, architect review and explicit developer completion before SYSTEM-TEST-001 is Ready. No implementation task depends on the system test; no external feature task is modified by this refactor-first decision.

## System Validation

The independent `moda-interact-system-test` terminal task runs after **all** ARCH-041 implementation prerequisites (including API-014 authentication relocation) are architect-accepted, with a developer manual-validation checkpoint permitted beforehand. It does not relocate system-test code into API `tests/` or become a dependency of implementation tasks.

### Test organisation (accepted ARCH-036 convention)

- **New unit/characterization tests:** `tests/unit/<domain>/<feature>/*.test.ts` (for example `tests/unit/http/route-dispatch.test.ts`, `tests/unit/billing/commands/recurring-intent.test.ts`). Unit/auth/route tests should use injected fakes and should not require a live external Woo provider.
- **New PostgreSQL integration tests:** `tests/integration/<domain>/<feature>/*.test.ts`, including `tests/integration/auth/woo-installation/` for persisted authentication or concurrency tests; never put database-dependent tests under `tests/unit/`.
- **Migration-backed billing proof:** API-001 owns a **small reusable** `scripts/test-arch041-billing-postgres.mjs` harness for the existing billing-read, recurring and recovery-credit PostgreSQL suites and newly accepted billing integration suites. Follow the disposable PostgreSQL and `prisma migrate deploy` pattern already used by `scripts/test-woocommerce-rest-read-authorization-postgres.mjs`; do **not** use `prisma db push` from the installation runner to assert migration-defined constraints/triggers. The harness must supply `DATABASE_URL` and `WOO_INSTALLATION_TEST_DATABASE_URL`, run focused suites against an invocation-owned instance, and guarantee teardown. Billing API-002–007 reuse this one runner (including API-003 where applicable); they do not each build another harness or create dependencies among independent billing tracks.
- **Required evidence:** Tests involving persisted billing integrity, locks, replay, collisions or concurrent outcomes must execute on migration-backed PostgreSQL. An unavailable Docker/PostgreSQL environment is recorded as **not run / blocked**, never as a pass or as proof from mocks or `db push`.
- **Test relocation:** the developer subsequently authorised migration of all remaining legacy colocated tests. No `*.test.ts` files remain in `src/`; all unit/contract tests are under `tests/unit/` and all 17 PostgreSQL tests under `tests/integration/`.
- **Discovery/build contracts:** `npm test` runs `tests/unit/**/*.test.ts`; `npm run typecheck` covers `src/` and `tests/`; `npm run build` compiles production source only. Integration suites remain separate from `npm test` and are explicitly registered with the disposable PostgreSQL runners.
- **Follow-up coverage:** the standard `npm run test:integration` chain now registers all 17 suites, including the provider-outcome collision tests, discount-offers suites, recovery-policy and webhook-receipt validation. Full migration-backed execution remains to be evidenced by the developer.
- **Evidence:** Each API task validates the focused existing and new suites, `npm test`, typecheck/lint/build and appropriate disposable PostgreSQL checks. Do not report an unavailable Docker/PG run as passed. Preserve clean isolated task worktree, recursive submodule and `git diff --check` evidence.

Final system tests must prove route/method precedence, intact negative authorization, bounded failure envelopes, tenant separation, existing billing response/currency semantics, replay/idempotency and signed/callback boundaries, using controlled fixtures.

## Open Questions

No open design question blocks the **behaviour-preserving** task plan. Explicitly excluded security-policy follow-ups (WordPress nonce/capability consistency and in-flight paid-command authorization after credential rotation) require a different, agreed architecture if pursued. Before each route extraction and final composition, characterize all routes actually served by the baseline; do not create pending ARCH-040 endpoints as part of this refactor. Performance capacity remains unmeasured; do not claim a throughput improvement from code extraction.

## Change History

- 2026-10-16 (initial): Defined ARCH-041 as a behaviour-preserving hosted API structural refactor; 13 API tasks and one terminal system-test task, no `_index.md` edits.
- 2026-10-16 (revision 2): Reconciled against `moda-interact-workspace(20261016-000147).zip`. Adopted test-type/feature directories established by complete `ARCH-036-API-004`, retained legacy `src` tests, clarified endpoint-specific authentication boundaries and no forced `src/auth/` move, updated test placement/validation across API-001–013, and identified which external route-extraction prerequisites remain open. No runtime code, task IDs, dependency links, task status or Git worktrees changed.
- 2026-10-16 (revision 3): Made `src/auth/woo-installation/` and `src/http/route-handler.ts` explicit target modules; added API-014 as a separate, bounded identity-ownership relocation after route and billing streams; revised API-012/API-013 composition and HTTP responsibilities and terminal validation. No `_index.md`, runtime source or external auth policy changed.
- 2026-10-16 (revision 4): Clarified integration/auth test placement, added one shared migration-backed billing validation runner to API-001, required actual migration-backed PostgreSQL evidence for billing extraction, specified Woo site-proof ownership in API-014, required refreshed characterization for newly accepted feature routes, and repaired API-014 enables metadata. Preserved all task IDs, dependency links, statuses, runtime behaviour and `_index.md` exclusions.

- 2026-10-16 (revision 5): Adopted refactor-first sequencing against the 11:42 full workspace snapshot. API-001–007 are Complete; API-008 becomes Ready with only API-001 as prerequisite. Later ARCH-041 route/composition/auth tasks preserve all already-served endpoints without waiting for unrelated feature tasks. No external initiative files, `_index.md` or runtime source changed.

- 2026-10-16 (revision 6): Reconciled with the API-013 snapshot: API-001–012 and API-014 Complete, API-013 in progress, SYSTEM-TEST pending. Recorded user-directed relocation of remaining co-located tests, final actual module ownership, and bounded legacy/runner/composition cleanup. No completion or runtime-test results are inferred; no `_index.md` changed.
