---
id: ARCH-057-SHOPIFY-009
architecture_id: ARCH-057
title: Preserve Shopify sessions across uninstall retries and reinstall admission
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 65
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-057-SHOPIFY-001
enables:
- ARCH-057-SHOPIFY-010
- ARCH-057-SHOPIFY-011
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-057-SHOPIFY-009: Preserve Shopify sessions across uninstall retries and reinstall admission

## Architecture

Architecture ID: `ARCH-057`.

Architecture document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`.

Coordinator: `moda_architect`.

Mandatory execution, diagnostic and naming contract: `docs/architecture/ARCH-057/task-contract.md`.

**Defined but not materialised.** This is the canonical portable definition for `docs/decisions/shopify/ARCH-057/SHOPIFY-009-preserve-session-lifecycle-and-webhook-configuration.md`. It uses the latest supplied `moda-interact-workspace(20261104-005051).zip`; no branch, worktree, claim or passing implementation is asserted. Dependency status must be verified by the launcher before execution.

## Objective

Make the authenticated install lifecycle one coherent persistence boundary: a real uninstall commits its credential cleanup atomically; duplicate uninstall preserves replacement credentials; reinstall admission verifies durable credentials after the existing Shop lock; the intended app configuration delivers the lifecycle and supported webhook topics to their existing routes.

## Context

The reviewed uninstall route commits `ShopService.markUninstalled()` and then separately deletes all Sessions when the SDK supplied a session. A duplicate delivery during `reinstallPendingAt` therefore deletes the new offline session even though the guarded Shop mutation does nothing. Separating the commits also makes failed cleanup non-atomic.

The existing `PrismaSessionStorage` writes are outside that lifecycle transaction. Moving deletion alone does not prove that a previously authenticated request still has durable credentials when it begins reconciliation. The selected completion is a locked durable-session check in the two existing reinstall admission methods, followed by the existing login path when authentication must be renewed. This task does not wrap or replace SDK storage.

Preserve the accepted `ARCH-010-SHOPIFY-006` uninstall fence and stopped-reinstall semantics and the `ARCH-016-SHOPIFY-001` common Shop lock, durable offline-scope eligibility and first-unavailable timestamps. The named app configuration is missing uninstall, consent and discount subscriptions already supported by this repository. Its app identity differs from the default template configuration; they must not be merged or silently retargeted.

## Scope

Paths are relative to `moda-interact`.

### Existing files to modify

| Path | Selected responsibility |
|---|---|
| `app/services/shop/shop.service.ts` | Transaction-owned uninstall cleanup; typed uninstall/reinstall outcomes; lock and durable credential admission in `beginReinstallReconciliation` and `retryReinstallReconciliation`; preserve SHOPIFY-001 resolver/context work |
| `app/routes/webhooks/app/uninstalled/route.jsx` | Remove route-owned Session deletion; consume the service result and log the committed semantic outcome |
| `app/routes/webhooks/app/scopes-update/route.jsx` | Keep Shop-before-Session lock ordering; tolerate an authenticated session removed by a committed uninstall without recreating it; retain durable offline-scope eligibility |
| `app/routes/auth/catchall/route.jsx` | Handle typed reinstall outcomes and authenticated-domain login redirection; enqueue only a returned committed schedule |
| `app/routes/app/reinstalling/route.jsx` | Handle typed explicit-retry outcomes and authenticated-domain login redirection while preserving the standalone shell and stopped state |
| `app/services/discounts/shopify-discount-lifecycle.service.ts` | Preserve the common lock and invalidation semantics; avoid updating discounts already unavailable when only their availability Boolean is unchanged; own safe original errors from best-effort activation publication |
| `app/services/webhooks/shopify-webhook-observability.server.ts` | Safe original failure/cause/code fields for lifecycle routes, authentication and lifecycle service diagnostics; retain Shared logging and existing metric ownership |
| `shopify.app.moda-interact.toml` | Add the seven missing topic declarations to the existing intended app identity; retain its API version, scopes and compliance subscriptions |
| `shopify.app.toml` | At most a comment identifying the separate template app; retain its distinct identity, URLs, version and topic/scope contents |
| `scripts/shopify.mjs`, `scripts/shopify-dev.mjs`, `scripts/shopify-dev-cloud.mjs` | Make the existing dev child commands explicitly select `--config moda-interact`; no process-management rewrite |
| `tests/unit/services/shop.service.test.ts` | Uninstall/reinstall transition, credential, return-type and retry cases |
| `tests/unit/services/shopify-discount-lifecycle.service.test.ts` | Invalidation timestamp/no-op predicates, postcommit publication and emitted diagnostics |
| `tests/unit/routes/scopes-update.test.jsx` | Lock-before-Session, missing-session race, persisted offline scope and after-commit publication |
| `tests/unit/routes/auth-catchall.test.ts`, `tests/unit/routes/reinstalling-route.test.ts` | Typed schedule/no-change/login outcomes and trusted domain handling |
| `tests/unit/webhooks/shopify-whatsapp-consent-config.test.js`, `tests/unit/webhooks/shopify-brand-scope-config.test.ts` | Retain the existing consent/version and distinct-app scope constraints |
| `package.json` | Add the exact test commands below; select the named config in the existing `dev` and `deploy` commands; no dependency/version change |

### New files

| Path | Purpose |
|---|---|
| `tests/unit/routes/uninstalled.test.jsx` | Actual route delegation, duplicate/session-less success and failure ownership |
| `tests/unit/webhooks/shopify-lifecycle-errors.test.ts` | Real Shared emitted-record, original cause/code, privacy and throwing-sink tests |
| `tests/unit/webhooks/shopify-webhook-config.test.ts` | Complete topic/URI/config-identity and dev/deploy selection checks |
| `tests/integration/shopify-session-lifecycle.postgres.test.ts` | Migrated real PostgreSQL rollback, duplicate retry and tenant-isolation cases |
| `tests/integration/shopify-session-lifecycle-races.postgres.test.ts` | Independent-connection uninstall, SDK persistence, reinstall and scopes races |
| `tests/helpers/shopify-lifecycle-postgres.ts` | Small task-owned PG17 container, forward migration, synthetic fixture and explicit barrier helpers |
| `docs/shopify-webhook-configuration.md` | Exact configuration identity/topic map, explicit launch commands and non-deployment evidence |

Test files/helpers remain below 300 lines each. The helper uses the existing Testcontainers and Prisma dependencies; it is not a second general integration framework. Unit/module injection may bind the actual service to disposable clients; add no production injection endpoint or SDK-storage proxy.

## Out of Scope

No schema/index/trigger, advisory lock, new uninstall identity, provider event-time ordering heuristic, session cache, replacement Session adapter, new queue, receipt/outbox or credential migration. No direct `UNINSTALLED -> ACTIVE` restoration, new background reconciliation policy, billing/credit/history reset or automatic restart of a stopped reinstall attempt.

No privacy data export/erasure implementation or blanket cascade change. Review F17 remains an explicit deferred architecture decision: data ownership, retained accounting/audit history, numeric/GID alias handling, rehydration prevention, acknowledgement/retry and external-object handling require an agreed policy before tasks alter the three compliance handlers. The configuration keeps those handlers subscribed without representing their business implementation as complete.

No Shopify app deployment, remote subscription mutation, app-identity merge, additional permission request or API version upgrade. The source task specifies and validates the intended configuration; deployment evidence is a separate release responsibility.

## Requirements

### A. Commit uninstall and cleanup together

1. `markUninstalled(domain, uninstalledAt)` remains the single lifecycle owner. Normalize the authenticated domain, resolve its Shop ID, acquire the existing `commerce.Shop FOR UPDATE` lock and reread authoritative lifecycle state. A pre-lock identity lookup is not an eligibility read.
2. Retain exactly the accepted guarded transition: `where: {id, uninstalledAt: null}` sets `status: UNINSTALLED`, the first `uninstalledAt` and `reinstallPendingAt: null`. Only the transaction that changes one row may delete Sessions for that canonical Shop domain. Session cleanup is independent of whether the webhook SDK returned a `session` object.
3. Run the guarded mutation, `transaction.session.deleteMany({where: {shop: canonicalDomain}})` and catalogue invalidation inside the same database transaction. Deletion or invalidation failure rolls back the Shop transition and all other writes; a retry can win the original guard and finish cleanup. Never catch the failed delete and acknowledge success.
4. If `uninstalledAt` is already non-null, perform no Shop lifecycle mutation and no Session deletion. Preserve the pending reinstall marker and every replacement session, including a new offline session written before the marker exists. Retain the existing idempotent catalogue invalidation using the persisted first uninstall time. Missing Shop returns the typed no-Shop outcome without deleting unrelated/orphan credentials or inventing a Shop.
5. Keep existing non-null per-discount `unavailableAt` values unchanged. Narrow the availability update to `isAvailable: true`; retain the separate `unavailableAt: null` update so rows already false but lacking a timestamp still acquire one. Do not collapse these into an update that overwrites history.
6. Emit final success only after commit. The route no longer imports the database for Session deletion. A successful first transition and an already-applied delivery have distinguishable domain outcomes; neither reads credentials solely for logging.

### B. Admit reinstall from durable post-lock credentials

7. Both reinstall methods acquire the same Shop row lock before authoritative lifecycle/subscription/session reads and before marker/schedule writes. Preserve the ordering `Shop -> related lifecycle rows`; do not lock Subscription/Session first or reuse request-cached state as mutation authority. No Shopify/Partner/Redis request occurs inside the transaction.
8. Use one private, reused durable offline-session eligibility reader in `shop.service.ts`. Select by the authoritative Shop domain and `isOnline: false`, retaining the current token owner's ordering `expires: desc`. Its minimum usable predicate matches the current Background `getShopifyAccessToken` decision: the row has a nonempty access token and the token is non-expiring, unexpired at the supplied `now`, or has a nonempty refresh token. Do not require `read_discounts` for billing reinstall, select an online token, refresh a token in this transaction, log tokens or claim remote token validity. Expired/unrefreshable or missing credentials require authentication. This is a local availability gate, not proof that Shopify will accept the token.
9. Check that predicate before creating/rescheduling a pending marker or returning a schedule to republish. An authenticated SDK object whose persisted Session was removed by the just-committed uninstall yields `AUTHENTICATION_REQUIRED`: no new/changed marker, no schedule write and no queue publication. A subsequent successful login/session persistence can enter the ordinary begin path.
10. Keep the accepted state machine: ordinary begin reuses an existing live marker/schedule unchanged; an existing stopped marker with no schedule returns `NO_CHANGE` and is not restarted; only explicit Retry can replace that stopped marker and create a new schedule. Active/Suspended/missing/non-eligible Shops retain no-op/access behavior. Retain the guarded comparisons as defensive mutation admission even though participating methods share the Shop lock.
11. Handle `AUTHENTICATION_REQUIRED` in auth catchall and the retry action by redirecting through the existing `/auth/login` route, adding `shop` with `URLSearchParams` from the authenticated SDK session domain. Never use a submitted/query/body tenant value or a token in the redirect. Preserve Shopify boundary headers and embedded authentication handling. The existing login loader passes the request to SDK `login`; verify its installed query-shop behavior instead of introducing an alternate OAuth flow.
12. The SDK storage implementation remains unchanged. The real database race evidence must cover both orders: `storeSession -> uninstall commit -> begin` returns authentication-required without a marker/schedule; `uninstall commit -> storeSession -> begin` produces one pending schedule and retains the new offline session. Also place persistence between the uninstall transaction's Shop transition and Session delete. That removed credential must be detected by the post-lock begin check. Once the original uninstall is committed, delayed duplicate deliveries must preserve a new session both before and after `reinstallPendingAt` exists.

### C. Preserve scope-driven lifecycle ordering

13. Keep the existing Shop lock before any Session scope write. Update only the authenticated session ID belonging to the authenticated canonical domain; use `updateMany` so zero rows after a concurrent committed uninstall is an expected missing-session result, not P2025-driven infinite retries. Do not recreate a missing session from the webhook payload.
14. Reread persisted offline scope after the Session update. Payload scope or an online Session alone cannot authorize sync. Missing offline/read-discounts scope invalidates the catalogue; inactive or otherwise ineligible Shops cannot request a sync. Eligible scope updates commit `SYNC_REQUIRED` before publishing the existing Shared discount job. A postcommit publication failure remains retryable with the original cause logged; never publish inside the transaction.

### D. Select and validate the intended app configuration

15. Treat `shopify.app.moda-interact.toml` as the selected application configuration for this task's dev/deploy entrypoints. Keep its current client ID, `app-test.modainteract.com` URLs, scopes and webhook API `2026-07`. Retain the distinct default template config; no inference is made about either deployed subscription set.
16. The named config must have exactly these existing endpoint mappings, without duplicate topic declarations:

| Endpoint | Topics |
|---|---|
| `/webhooks` | `orders/create`, `carts/create`, `carts/update`, `checkouts/create`, `checkouts/update`, `customers_whats_app_marketing_consent/update`, `discounts/create`, `discounts/update`, `discounts/delete`, `discounts/redeemcode_added`, `discounts/redeemcode_removed` |
| `/webhooks/app/uninstalled` | `app/uninstalled` |
| `/webhooks/app/scopes_update` | `app/scopes_update` |
| `/webhooks/customers/data_request` | compliance `customers/data_request` |
| `/webhooks/customers/redact` | compliance `customers/redact` |
| `/webhooks/shop/redact` | compliance `shop/redact` |

17. Preserve `read_customers`, `read_discounts`, `read_brand` and the other existing named-app scopes; request no new write scope. Match the existing runtime/consent `2026-07` contract. Use TOML-managed subscriptions, not a second per-shop after-auth registration mechanism.
18. Existing `dev`/`deploy` and the three custom dev child commands explicitly pass `--config moda-interact`. Document how the separate default app is intentionally selected by an operator. Tests inspect arguments without starting ngrok/cloudflared or deploying an app. Running local tests or configuration validation must not create/release a Shopify app version.

### E. Own the original failure diagnostic

19. Reuse `shopify-webhook-observability.server.ts` and Shared `createLogger`/`sanitizeLogFields`. Extend the route failure adapter with optional fixed `operation`/`stage`/`origin` and actual safe error/cause/causeChain/databaseCode fields; preserve existing event names where meaningful. Add a thin `recordShopifyLifecycleFailure` entry only for the service-owned reinstall/best-effort boundaries. No new generic serializer/redactor or duplicate generic HTTP metric/span.
20. A wrapper retains the original exception as `cause`; Shared receives available safe causes explicitly, to the common maximum of four entries. Preserve original safe wording and actual codes; redact credential/connection-string/PII spans before emission. Untrusted authentication headers, webhook bodies, SDK Session objects and token/refresh fields never appear in emitted records.

## Work Items

- [ ] Integrate against accepted SHOPIFY-001 and preserve its context/resolver interfaces.
- [ ] Move first-transition Session cleanup into the uninstall transaction and return typed outcomes.
- [ ] Add the locked offline-session reinstall admission check and typed caller handling.
- [ ] Preserve scope/session/catalogue ordering, missing-session behavior and first timestamps.
- [ ] Correct named topic declarations and explicit configuration selection.
- [ ] Implement the lifecycle diagnostic matrix and real emitted-record privacy/isolation assertions.
- [ ] Execute migrated PostgreSQL rollback and actual SDK persistence races with independent connections.
- [ ] Record exact commands, source/package provenance, database calls/SQL and result evidence.

## Interfaces / Contracts

The new local result types live in `shop.service.ts`; callers switch explicitly on `kind`:

```ts
type ShopifyUninstallResult =
  | { kind: "SHOP_NOT_FOUND" }
  | { kind: "UNINSTALLED"; shopId: string; deletedSessionCount: number }
  | { kind: "ALREADY_UNINSTALLED"; shopId: string };

type ReinstallSchedule = {
  shopId: string;
  subscriptionId: string;
  reinstallPendingAt: Date;
  expectedNextReconcileAt: Date;
};

type ReinstallAdmissionResult =
  | { kind: "SCHEDULED"; schedule: ReinstallSchedule }
  | { kind: "AUTHENTICATION_REQUIRED" }
  | { kind: "NO_CHANGE" };
```

Keep the existing method arguments `(domain, uninstalledAt)` and `(shopId, now?)`; change only their documented return types. `enqueueBillingSubscriptionReconcileBestEffort` still receives the existing unchanged schedule object. No Shared schema/version or Background consumer change is required. SHOPIFY-001's server-only merchant context supplies authenticated identity in its migrated callers; webhooks continue independent SDK HMAC authentication.

Package script values:

```json
{
  "dev": "shopify app dev --config moda-interact",
  "deploy": "shopify app deploy --config moda-interact",
  "test:shopify-lifecycle": "vitest run tests/unit/routes/uninstalled.test.jsx tests/unit/routes/scopes-update.test.jsx tests/unit/routes/auth-catchall.test.ts tests/unit/routes/reinstalling-route.test.ts tests/unit/services/shop.service.test.ts tests/unit/services/shopify-discount-lifecycle.service.test.ts tests/unit/webhooks/shopify-lifecycle-errors.test.ts tests/unit/webhooks/shopify-webhook-config.test.ts tests/unit/webhooks/shopify-whatsapp-consent-config.test.js tests/unit/webhooks/shopify-brand-scope-config.test.ts",
  "test:shopify-lifecycle:postgres": "MODA_SHOPIFY_LIFECYCLE_POSTGRES=1 vitest run tests/integration/shopify-session-lifecycle.postgres.test.ts tests/integration/shopify-session-lifecycle-races.postgres.test.ts"
}
```

The integration helper starts only its disposable `pgvector/pgvector:pg17`, deploys the canonical forward migrations, creates separate clients and injects those clients at existing module boundaries. Use the actual installed `PrismaSessionStorage` to persist synthetic SDK Sessions; the SDK must not be replaced by a handwritten `upsert` in the concurrency proof. Store only synthetic credentials. Explicit barriers may intercept calls around real SQL, but may not substitute the SQL/lock implementation.

## Dependencies

- `ARCH-057-SHOPIFY-001` — accepted/integrated request context and ShopService baseline. This dependency also prevents concurrent edits to the resolver and auth/reinstall callers.

Accepted historical contracts from ARCH-010/016/045/049 are preservation requirements, not invitations to edit their task files. The launcher checks their actual current integrated state.

## Enables

- ARCH-057-SHOPIFY-010
- ARCH-057-SHOPIFY-011

## Acceptance Criteria

- [ ] Only a winning genuine uninstall transition deletes Sessions; Shop/session/catalogue mutations commit or roll back together.
- [ ] A duplicate during reinstall, including persistence-before-marker, retains replacement credentials, the first uninstall time and the marker.
- [ ] Cleanup failure leaves the first transition eligible for a correct retry; a committed duplicate does not repeat credential deletion.
- [ ] Reinstall admission obtains the common Shop lock and checks current durable usable offline credentials before creating/rescheduling/republishing a schedule.
- [ ] Removed credentials cause authenticated-domain login redirection without a new marker or queue work; successful subsequent persistence can begin normally.
- [ ] Stopped attempts remain stopped until explicit Retry; concurrent begins/retries produce one durable authority and no direct activation.
- [ ] Scope updates never recreate a deleted Session, use only persisted offline scope and publish only after commit.
- [ ] Catalogue invalidation preserves non-null historical timestamps and avoids unchanged availability writes.
- [ ] Named config contains the exact topic/URI matrix and the correct version/scopes; distinct app identities remain distinct and launch commands select the named app explicitly.
- [ ] Original safe operational messages/codes/causes appear in real Shared records; secrets/PII do not; logger failure does not change business outcomes.
- [ ] Real PG17+pgvector evidence covers all required races; no mock-only result is presented as database or SDK integration proof.

### Required cases and diagnostic ownership

| Case / injection | Owner and required emitted evidence | Outcome to preserve |
|---|---|---|
| SDK HMAC/auth throws a harmless Error marker with cause | Existing auth adapter: original safe message/cause, `sdk_exception`, fixed route; no untrusted headers | Original exception/SDK status propagated; no DB/queue work |
| Expected SDK 401 Response | Auth adapter records actual status and control-flow classification, never arbitrary Response body | SDK denial unchanged |
| Uninstall lookup/lock/guard/Session delete/catalogue write fails | Uninstall route adapter: actual error/code/cause and failed stage, trusted Shop/domain where already known | Transaction rollback; failure remains retryable; no success log |
| Duplicate uninstall with absent SDK session and replacement persisted offline session | Semantic committed outcome, no fabricated error | HTTP success; new credentials and marker preserved |
| Begin/retry DB lookup/lock/session/schedule write fails | `recordShopifyLifecycleFailure`: actual message/code/cause and method stage | Rethrow; no partial marker/schedule, no enqueue |
| Begin/retry finds missing/expired-unrefreshable offline session | Bounded `AUTHENTICATION_REQUIRED` outcome, not a fabricated provider failure | No writes/enqueue; login via authenticated domain |
| Scopes handler's authenticated Session was deleted before its lock | Bounded missing-session outcome; no fabricated P2025 | No recreation; unavailable catalogue/no publication when offline grant absent |
| Scope persistence or catalogue write fails | Scope route adapter: original message/code/cause | Rollback and retryable failure |
| Scope publication fails after commit | Scope route adapter: original queue cause plus committed stage | Committed sync intent retained; HTTP failure permits retry |
| Activation discount publication fails after commit | Existing best-effort helper owns original queue failure through Shared | Already committed subscription/lifecycle result stays successful |
| Sensitive sentinels in source error and a throwing Shared sink | Actual emitted JSON checked before harness redaction; original harmless markers retained, sensitive spans absent | Same rollback/redirect/HTTP/no-op behavior |

Real database cases include two tenants; simultaneous duplicate uninstall; rollback injected after the real Session delete; simultaneous begin/retry with explicit barriers; both SDK persistence orders and persistence inside the first-uninstall transaction window; duplicate arrival before/after new marker; and scopes/uninstall orderings. Check actual persisted rows and returned schedule, not only call order.

## Validation

- [ ] `npm run test:shopify-lifecycle`
- [ ] `npm run test:shopify-lifecycle:postgres` — canonical migrations, real SDK storage, independent PostgreSQL connections and explicit barriers; required opt-in cases execute, not skip
- [ ] `shopify app config validate --config moda-interact` with the already available host CLI; validate only, do not deploy or install a repository dependency
- [ ] `npm run typecheck` and `npm run build`
- [ ] Focused ESLint on changed/new implementation and test files; `git diff --check`
- [ ] Same-fixture before/after repository calls, affected rows and emitted SQL recorded separately; preserve necessary post-lock reads and explain the new credential-admission read
- [ ] Raw Shared records, source/package provenance, two-app configuration map and task-owned container cleanup recorded

If a required tool/SDK/container/validation is unavailable, record blocked/not run and return the precise prerequisite. Do not treat skipped tests as passing or run destructive commands against an inherited DATABASE_URL.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation pass, set this task to review, complete its report and return to `moda_architect`. Do not start SHOPIFY-010. Stop for a changed canonical schema/SDK contract, an unmodelled credential race outside the specified admission solution, an app-identity ambiguity, a need to alter Background restoration, or a required diagnostic that cannot safely preserve its source evidence. Do not solve those issues with an SDK wrapper, event timestamp heuristic or new durable identity without a scoped architect amendment.

## Implementation Notes

The linearization point for beginning reinstall is the post-lock durable credential observation, not the earlier authenticated object. A genuine uninstall may legitimately invalidate a session persisted before its cleanup; the caller must then authenticate again instead of scheduling work against vanished credentials. A duplicate whose first uninstall has already committed is a different case and must never delete replacement credentials.

The guard intentionally does not distinguish a very late old uninstall from a genuinely new uninstall after Background has completed restoration and cleared `uninstalledAt`. That is the accepted lifecycle contract, not a new event-identity promise. This task adds no heuristic to change it.

Official references for executor verification: [Shopify login behavior](https://shopify.dev/docs/api/shopify-app-react-router/latest/entrypoints/shopifyapp), [app configuration selection](https://shopify.dev/docs/apps/build/cli-for-apps/manage-app-config-files), and [webhook subscriptions](https://shopify.dev/docs/apps/build/webhooks/subscribe). Installed pinned packages and repository contracts decide implementation details; online examples are not proof of installed behavior. Use the repository's Shopify AI Toolkit guidance for platform work in the execution host.

## Completion Report

### Status

Not Started. Defined but not materialised; no execution claim or worktree is asserted.

### Files Changed

None. Definition only.

### Work Completed

None.

### Validation Results

Not run. Record exact commands, actual source/build/installed SDK and Shared versions, canonical migration provenance, case outcomes, emitted-log evidence, before/after persistence calls versus SQL, and task-owned resource cleanup.

### Deviations

None.

### Assumptions

The launcher verifies current dependency status and integrated source. The named app is the explicit target of the selected local commands; no deployed subscription state has been inspected.

### Unresolved Issues

Implementation and mandatory validation remain outstanding. Privacy policy/erasure scope remains separately deferred as specified above.

### Architectural Concerns

Return ownership, schema, durable identity, SDK storage, queue or cross-repository changes to the architect; do not silently widen this task.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition only; no implementation accepted.

### Reviewed Files

Definition and latest snapshot touchpoints only.

### Validation Reviewed

Definition/source inspection only; implementation evidence is outstanding.

### Architecture Conformance

To be assessed after implementation against the parent decision, common contract and accepted lifecycle fence.

### Follow-up

Return the completed task for architect review; do not begin enabled work.
