# Shopify application: database and architectural review

**Snapshot:** `moda-interact-workspace(20261103-235702).zip`

**Architect brief:** `moda_architect(20261103-235630).toml`

**Review revision:** 01

**Status:** assessment and evidence; no implementation or task acceptance

## Executive assessment

The application has useful architectural boundaries already: merchant routes call local services, generic webhook ingress performs one application-level Shop lookup before queue publication, recovery readers use bounded queries, and sensitive mutations retain transaction, tenant, revision and idempotency checks. The database snapshot and its canonical database repository are also consistent.

The clearest avoidable cost is in merchant request composition. Shop resolution combines authentication-adjacent identity lookup, remote profile retrieval and local provisioning checks. Parent loaders, child loaders and independently written services repeatedly invoke overlapping readers. That produces unnecessary database and provider work even when the shop has not changed.

A few functional defects deserve attention before performance refactoring:

1. Initial paid activation locks `shopify.Shop`, although the supplied schema defines `commerce.Shop`. Fixing the relation alone also exposes a source-reachable lock-order inversion.
2. A malformed successful provider response can be interpreted as authoritative absence of a subscription and clear the current local projection.
3. Eligible refund admission performs provider HTTP and root-client database reads while a Serializable transaction is open.
4. A duplicate uninstall during pending reinstall can delete the replacement offline session even though the Shop lifecycle fence correctly preserves the reinstall marker.
5. Repository webhook configuration does not match all implemented handlers or its existing consent test.
6. Privacy request and erasure handlers have existing functionality gaps; those require a separate retention/fulfilment decision, not a query-count cleanup.

The smallest useful direction is to share narrow trusted context within one request, make presentation projection pure, remove reads whose outputs are unused, batch bounded acknowledgements, and keep external observations outside write transactions. No new service, process-wide tenant cache, generic repository framework or ingress outbox is justified by this review.

### Evidence and priorities

| Finding | Priority | Evidence |
|---|---|---|
| F01: wrong initial paid lock relation; related lock order | Correctness first | Source/schema contradiction and emitted-SQL probe; concurrent deadlock is a source-derived risk, not reproduced |
| F02: malformed provider body becomes no contract | Correctness first | Unchanged-source probe plus concrete caller trace |
| F03: refund crosses transaction boundary | Correctness first | Unchanged-source probe records root DB/provider work during transaction |
| F04: duplicate uninstall deletes replacement session | Correctness first | Actual route/service/token-reader control flow with mocked boundaries |
| F05: webhook configuration drift | Correctness first | Parsed files and existing-test-equivalent assertion |
| F06–F14: repeated reads, writes and refresh work | Simplification next | Static branch ledgers; resolver and purchase-history counts additionally probed |
| F15: queue pre-reads and incomplete deadline | Reliability next | Static trace and stalled-pre-read source probe |
| F16: suppressed or misclassified operational failures | Cross-cutting correction | Source trace |
| F17: privacy handlers and restrictive deletion graph | Separate functional scope | Source/schema trace; no legal or compliance conclusion |
| F18: category lifecycle check during commit | Confirm policy and race | Static candidate, conditional on active-at-commit requirement |

## 1. Scope, baseline and counting rules

The primary target is `moda-interact`. The review traced all 45 registered route modules and their relevant Shop, billing, support, recovery, settings, knowledge, promotion, usage and webhook services. Canonical schema/migrations, relevant Background consumers, existing tests and accepted architecture decisions were used to check ownership and avoid reopening intentional behaviour. This is not a full implementation audit of the Background or API repositories.

The lexical inventory scanned 188 application source files. It found 376 candidate persistence calls: 182 reads, 105 writes, 45 raw operations and 44 transaction wrappers. Those are search candidates, not a runtime workload, an AST-complete inventory, or a sum of queries executed by any request. The report's branch counts come from tracing actual call paths.

The nested and canonical Prisma schema files are byte-identical. All 72 migration-directory files (71 SQL migrations and migration_lock.toml) are also byte-identical, with no extra file on either side. Of 62 literal qualified relation references in raw SQL, the inventory identified one relation absent from the supplied schema: the initial paid activation reference to `shopify.Shop`.

**Source baseline:**

| Item | Value |
|---|---|
| Uploaded ZIP SHA-256 | `6890c8d7cfbc68d9814920ef154d0d18b4aca7af8e1e6cc9dd9a95ff04239c6e` |
| Architect TOML SHA-256 | `1b5548a98a9c899a9f44e442d86df2e2510b0827ecd2fa742a829b07d00dec3e` |
| Canonical/nested schema SHA-256 | `5c68e467f392cafe2e6b5be730b81e000a3590e31567135c4037791bcfe11052` |
| Locked Prisma / client | 6.19.3 |
| Locked React Router | 7.18.2 |
| Locked Shopify app React Router integration | 1.2.1 |
| Locked Shopify Prisma session storage | 9.0.1 |
| Locked BullMQ | 6.3.1 |
| Locked Vitest | 4.1.11 |
| Source-probe runtime | Node 24.22.1 |

These versions describe the supplied lockfile, not the latest packages or a verified deployed environment. The app resolves Shared 3.1.0 while the Background package declares 3.0.0. That difference alone does not prove an incompatibility or justify a package upgrade.

Throughout this report, a **data call** means an explicit repository invocation of a Prisma model method or a raw query/execute method. Counts exclude SDK authentication/session storage, transaction BEGIN/COMMIT/SET, relation expansion into additional SQL, retries, database triggers/cascades and later framework revalidation unless expressly stated. Provider credential reads are included where verified. Counts are not latency, physical scans or measured SQL statement totals.

Unless qualified, a merchant count assumes an established, unchanged, ACTIVE shop with existing settings/subscription rows and a successful stated branch. A full-page count includes the parent and child only when both loaders execute; it is not a claim that every navigation reruns both. Source line references target the uploaded snapshot. Abbreviated paths refer to the named area of moda-interact; canonical database and architecture-decision paths are identified separately.

The reference workload of 20,000 inbound Shopify events per minute in the architect brief is a planning assumption. This review does not establish capacity at that rate.

## 2. Current ownership and request shape

| Boundary | Current responsibility | Architectural judgement |
|---|---|---|
| Shopify SDK authentication | Verify admin/webhook requests and supply authenticated Shopify context/session | Preserve at every independently callable endpoint; internal SDK query cost remains unmeasured |
| `ShopService.resolveShopifyShop` | Remote profile read, local identity lookup, optional profile update/provisioning, subscription/settings existence | Too much repeated work for routine read composition |
| Merchant loaders/read services | Access projection, page data and presentation | Share immutable request facts; keep standalone resource guards |
| Billing mutation services | Current provider evidence, local subscription/cycle checks, accounting transitions and idempotency | Preserve fresh admission and atomicity; shorten transaction duration |
| Generic webhook ingress | Authentication, metadata validation, Shop admission, normalization and BullMQ publication | Already lean on business DB work |
| Background consumers | Re-read state at later execution time and perform asynchronous work | These reads are across a process/time boundary, not automatic duplicates |
| Canonical database repository | Schema and migrations | Verified aligned with app's nested copy |

A normal established-Shop resolution executes one Shopify Admin GraphQL request, one Shop read, one Subscription existence read and one ShopSettings read. The parent app loader then adds a full support reader and another subscription projection. Its baseline is therefore **seven data calls and one resolver GraphQL request**. A child loader that resolves the shop independently starts another three-call/one-GraphQL sequence.

Evidence: `moda-interact/app/services/shop/shop.service.ts:48–168`; `moda-interact/app/routes/app/route.jsx:17–58`; route nesting in `moda-interact/app/routes.ts:26–59`. The unchanged-source resolver probe reproduces three reads for one unchanged shop and six reads/two GraphQL requests for two concurrent resolutions.

[React Router loaders can run independently and in parallel](https://reactrouter.com/how-to/middleware). A parent loader is therefore not a safe sole access-control gate for a child or resource endpoint. Request context/middleware can supply shared trusted facts, but every endpoint must retain its required authorization. The exact integration must be verified against the installed 7.18.2 configuration; do not assume current documentation is a drop-in patch.

## 3. Correctness findings

### F01. Initial paid activation locks the wrong relation

`moda-interact/app/services/billing/subscription-locks.ts:21–30` emits:

```sql
SELECT "id" FROM "shopify"."Shop" WHERE "id" = $1 FOR UPDATE
```

The canonical Shop model is `commerce.Shop`, defined in `moda-interact-database/prisma/schema.prisma:2075–2152` and the first production baseline migration. No shipped migration defines a compatibility `shopify.Shop` table or view. ShopSettings really is in `shopify`; a blanket schema replacement would be wrong.

The affected branch is synchronous **initial paid activation with a matching selection token**. `subscription-sync.service.ts:199–240` reaches `SubscriptionActivationService.finalizeInitialPaidActivation`, whose line 220 executes this lock. Against the supplied canonical schema this branch cannot acquire the intended row lock.

The callback catches the error without preserving its diagnostic at `app/routes/app/billing/callback/route.tsx:205–210` and schedules Background reconciliation at lines 250–263. The supported impact is failed synchronous finalization and dependence on reconciliation, not permanent failure of every paid operation.

Two unit tests explicitly expect the wrong relation: `tests/unit/services/billing/subscription-activation.service.test.ts:386` and `tests/unit/services/billing.service.test.ts:723`. Mock expectations have preserved the defect instead of validating the actual database relation.

**Smallest correction:** use the canonical Shop relation, update the misleading expectations, and validate initial paid activation against migrated PostgreSQL.

**Lock-order companion:** correct the order in the same change. Callback milestone persistence locks Shop then ShopSettings (`callback/route.tsx:32–49`); paid synchronization locks ShopSettings, Subscription, then Shop (`subscription-sync.service.ts:199–239`). After correcting the table name, two callbacks can form a cycle:

1. A has committed its milestone and pending token, then waits for provider verification.
2. B holds Shop while recording its milestone and has not yet updated ShopSettings or replaced A's token.
3. A locks ShopSettings and Subscription, verifies its still-current token, then waits for B's Shop.
4. B waits for A's ShopSettings.

This is a source-derived potential deadlock; no PostgreSQL concurrency test was executed. Establish one order across participating writers and test this interleaving. Preserve the locks rather than deleting them.

### F02. Missing provider evidence is treated as confirmed absence

`moda-interact/app/services/billing/providers/shopify-billing.provider.ts:161–176` reads `result.data?.activeSubscription` and returns `null` for a falsy result. The source probe confirms that HTTP 200 with `{}` becomes `null`. Missing `data` or a missing field follows the same logic. Explicit GraphQL errors and unsuccessful HTTP statuses throw; a literal JSON `null` body also throws. The defect is the missing/malformed evidence accepted by this specific fallback.

`subscription-sync.service.ts:70–157` interprets that return value as authoritative no-contract evidence. It clears current plan/provider/billing-period references and dates, records `NO_CONTRACT` and may notify the merchant that the subscription ended. Historical ledger rows are not deleted.

A concrete reachable caller exists for an already active free subscription: `subscription-activation.service.ts:96–107` returns `VERIFIED_REPLAY` with no token when the current ACTIVE/TRIALING plan matches. The callback then synchronizes without the initial-selection token guard. A successful first verification followed by a malformed second response can clear that active projection. Some initial-token branches are protected; this is not a claim that every established paid callback behaves the same way.

**Smallest correction:** distinguish explicit, schema-valid provider `null` from absent or malformed fields. Fail malformed responses before replacing local state; retain the original safe provider diagnostic and cause. The lifecycle provider already demonstrates a stricter malformed-response check. Use one local parsing contract, not a new provider framework.

This is a demonstrated input-handling condition, not an observed Shopify production incident.

### F03. Refund admission holds a transaction during provider I/O

`moda-interact/app/services/billing/recovery-credit-purchase-management.service.ts:623–833` opens a Serializable transaction. On an eligible refundable ACTIVE purchase it calls `isCurrentProviderContext` at line 738. That helper uses the **root** database client for Shop and Subscription reads and invokes the provider at lines 908–920. The provider also reads its credential before HTTP.

The unchanged-source probe records root Shop, root Subscription, credential and provider fetch operations while the transaction is open, followed by transaction-bound counter reads and conditional refund/purchase/counter writes.

This extends transaction duration by provider response time, can consume an additional pool connection, and assembles local eligibility from different snapshots. Existing CAS and accounting predicates still matter. Duplicate cash refunds or incorrect cash movement were not established.

**Smallest correction:** collect provider evidence before the write transaction. Within a short transaction, read current local Shop/subscription/purchase/counter facts through the transaction client and match the captured provider identity and cycle to those facts. Keep tenant/provider predicates, request identity, refundable-amount checks, purchase/counter CAS and bounded Serializable retries. A failed provider preflight must leave no refund hold.

### F04. Duplicate uninstall can delete reinstall credentials

`moda-interact/app/routes/webhooks/app/uninstalled/route.jsx:31–44` calls `markUninstalled` and then deletes every session for the domain if SDK authentication returned a session.

`app/services/shop/shop.service.ts:441–480` correctly fences its lifecycle update with `uninstalledAt: null`. However, it returns no transition result and session cleanup is outside that fence. During pending reinstall, an old uninstall retry can affect zero Shop rows, preserve the fresh reinstall marker, and still delete the new offline session.

The probe executes the actual route, service, lifecycle helper and Background token-reader source with in-memory boundaries. It observes HTTP 200, the pending marker retained, the replacement session removed, and the real token reader failing with “No offline Shopify session found”.

Background reinstall reconciliation itself uses the Partner API and does not require that offline session. It may restore ACTIVE while subsequent token-dependent work fails. That distinction prevents overstating the failure.

**Smallest correction:** one fenced lifecycle operation should own the session-cleanup outcome and preserve replacement credentials during pending reinstall. Define rollback/retry behaviour if cleanup fails. Test duplicate and concurrent uninstall/reinstall at the route, service and Session boundary.

Accepted `ARCH-010-SHOPIFY-006` already protects the reinstall marker and rejects a second uninstall-identity scheme. Do not add event-time heuristics or an unrelated lifecycle identity to repair this gap.

### F05. Webhook declarations and implemented handlers disagree

`moda-interact/shopify.app.moda-interact.toml:12–40` omits the following implemented topics:

- `app/uninstalled`;
- `customers_whats_app_marketing_consent/update`;
- `discounts/create`, `discounts/update`, `discounts/delete`, `discounts/redeemcode_added` and `discounts/redeemcode_removed`.

The existing `tests/unit/webhooks/shopify-whatsapp-consent-config.test.js:6–16` expects the consent topic in that file. Running the equivalent assertion against the snapshot returns false. The full Vitest suite was not executed.

The default `shopify.app.toml` represents a different application identity and uses API version 2026-10; the named configuration and server use 2026-07. No app-level API registration call was found: `registerWebhooks` is exported but not invoked, and the configured app has no corresponding registration hook.

**Smallest correction:** identify the intended deployable configuration per environment and align its subscriptions, scopes and API version with the implemented handlers and accepted requirements. Do not blindly merge application identities. The snapshot proves repository drift; deployed subscription state remains unknown.

## 4. Avoidable merchant and billing work

### F06. Shop resolution repeatedly combines identity, profile sync and provisioning

The three-read/one-GraphQL sequence in `shop/shop.service.ts:48–168` runs even for unchanged established shops. Profile changes add a transaction and two updates; first provisioning adds required upserts. Profile updates are conditional, so this is not an “every read writes” defect.

Parent and child loaders independently resolve the same authenticated shop. Two concurrent resolutions in the probe perform six data reads and two GraphQL requests; there is no shared request promise.

**Smallest correction:** first reuse one authenticated resolution within a server request and pass narrow trusted facts to read services. Next separate routine tenant lookup from first-time provisioning and deliberate profile refresh. If remote metadata is removed from routine reads, define when locale/profile changes are refreshed; do not silently make metadata stale.

No process-global cache is needed. An SDK Session read is not equivalent to the application's Shop lifecycle check. Any request cache must be scoped to the authenticated request and tenant, never just an untrusted URL or submitted shop ID.

### F07. The support badge over-reads; acknowledgements multiply whole requests

The parent asks `readMerchantSupportMessages({ pageSize: 1 })` for an unread badge (`routes/app/route.jsx:41–54`). That reader executes a translated message-page SELECT, a total COUNT and an unread COUNT in a transaction (`services/merchant-support/merchant-support.service.ts:212–303`). The parent uses only the unread count.

A dedicated badge count removes **two SELECTs per parent execution** without changing message visibility.

The support UI then loops over visible unread message IDs and POSTs each sequentially (`routes/app/merchant-support/route.jsx:157–190`). Each request performs resolver three reads, an ownership SELECT, an UPDATE and one resolver GraphQL request. The default 25 unread messages cause **125 data calls and 25 GraphQL requests**; 50 unread messages cause **250 and 50**, excluding page loads, SDK authentication and subsequent revalidation.

`merchant-support.service.ts:305–330` also updates an already-read message's `updatedAt`. **Smallest correction:** submit the bounded set of rendered IDs together, cap it at the current 50-message limit, validate tenant/message visibility in the database predicate, update only unread rows and preserve the first read timestamp. Valid already-read IDs must remain idempotent successes; zero affected rows must not by itself mean a message is unowned. Do not implement an unbounded “mark everything read” operation or mark unseen messages.

Composition also upserts a thread and later updates it again. Fold only fields that can be assigned atomically without losing the message/thread ordering semantics.

### F08. Billing presentation composes overlapping snapshots

The healthy billing-options branch, with an active current cycle and no pending provider plan, performs **17 data calls after Shop resolution**:

| Component | Calls |
|---|---:|
| Access subscription projection | 1 |
| Live commercial context: Shop, provider credential, plan | 3 |
| Recovery capacity | 5 |
| Merchant billing state | 8 |
| Total after resolver | 17 |

The route therefore costs 20 calls including its resolver, or 27 when the seven-call app parent also executes. The branch makes one Partner request, separately from resolver GraphQL requests.

Repeated work includes three subscription reads, repeated reads of the same counters and Shop, and two catalogue reads when the live/local handles match. `merchant-billing-read.service.ts:104–107` additionally computes lifetime `usageEvent.aggregate`; the returned `usageQuantity` at line 324 has no production consumer in the inspected call graph.

**Smallest correction:** construct one request-local billing read snapshot, fetch required counters together, and derive capacity and presentation as pure projections. Remove the unused aggregate. If live and local provider handles differ, preserve the distinction rather than incorrectly reusing a catalogue row. Lifetime, purchased, promotional and paid-period balances must remain separate concepts even when fetched together.

The billing-select GET loads full capacity just to determine whether the subscription is FROZEN. A narrow status projection can answer that question.

The purchase POST repeats route prevalidation before entering a service that already owns validation. An existing receipt replay therefore reaches provider work before the service's one-read replay. Keep authentication/tenant authorization at the route; let the mutation service own its idempotent outcome and admission. Do not delete the two provider observations and catalogue rereads deliberately used for a **new** purchase's lifecycle revalidation.

Evidence: `routes/app/billing/options/route.tsx`; `routes/app/billing/select/route.jsx`; `services/billing/merchant-billing-read.service.ts`; `recovery-credit-purchase-request.service.ts`; `merchant-recovery-capacity-read.service.ts`; and `tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts:197–255`.

### F09. Purchase history has a bounded page but N+1 provider verification

`recovery-credit-purchase-management.service.ts:385–417` maps eligible ACTIVE purchase rows through the same current-provider helper. Each qualifying row repeats Shop, Subscription and credential reads plus a Partner request for the same shop.

The unchanged-source probe confirms:

| Eligible rows N | Service data calls | Partner requests |
|---:|---:|---:|
| 1 | 5 | 1 |
| 5 | 17 | 5 |
| 20 | 62 | 20 |

The service formula is `2 + 3N`: count/page reads plus three reads per qualifying row. The route adds one access-subscription read and resolver three reads, producing `6 + 3N`. Including the parent produces `13 + 3N`: 28 calls for five rows and 73 for twenty. An out-of-range page clamp adds a page reread. The route also makes a development-store Admin GraphQL request.

**Smallest correction:** load current provider/shop/subscription context once when any row needs it, then project each row's eligibility without further I/O. Service cost becomes five data calls and one Partner request, before further reuse of authenticated facts. At twenty qualifying rows that removes 57 data calls and 19 Partner requests. This is method-count arithmetic, not a measured response-time improvement.

Keep separate fresh verification when the merchant actually requests a refund.

The nested refund relation is unbounded even though the outer purchase page is bounded. The UI needs latest and latest-completed refund information. Retrieve those precise summaries; an arbitrary `take: 2` can hide an older completed refund and change behaviour.


### F10. Recovery detail reloads the same large ownership projection

`moda-interact/app/services/recoveries/recovery-detail.server.ts:37–75` builds an owned-recovery projection containing basket, customer, control, restrictions, outreach, inbound message, latest command and moderation information. Detail, messages and related readers each invoke it; the composed detail loader calls all three.

On the qualifying nonempty branch this means seven section/data SELECTs, including three copies of that large ownership projection, before counting the access guard. The child costs 11 calls, or 18 with the parent. A successful eligible follow-up catalogue branch adds four more reads; earlier empty/unavailable branches add fewer.

**Smallest correction:** resolve ownership once for the composed page and pass a trusted narrow context to its internal readers. Keep an independently authenticated, tenant-scoped ownership read for standalone message/related resources. The caller must not be able to supply this trusted context from request JSON.

Transcript page/edge queries and the empty-list existence lookup serve different pagination/UI purposes. Do not delete them merely because they are additional queries.

### F11. Settings and knowledge repeatedly load presentation context

The qualifying settings page performs 21 child calls, or 28 with its parent: settings access five, category/profile three, knowledge eight, feature preferences two and recovery policy three. ShopSettings, Subscription and Shop language are repeatedly loaded by these independently composed readers.

`moda-interact/app/services/feature-preferences/access.server.ts:11–36` returns a full settings row. All eight knowledge action routes discard that settings return. Source/upload mutation services correctly perform fresh, locked admission checks; upload-failure is telemetry-only and performs no business mutation after the guard.

**Smallest correction:** share one request-local settings/read projection and split the minimal mutation access guard from page presentation loading. Keep current entitlement, exact source/asset ownership, count/type validation, revision CAS and Shop/source locks inside mutations.

Smaller removals are directly supported by source:

- `services/merchant-knowledge/upload.server.ts:154` reads activation during upload intent and discards it. Remove that unused one/two-read call without changing the deliberately supported ability to configure sources while the feature is OFF.
- The same file validates a required language at lines 236–242, then rereads Shop language at line 343 as an unreachable fallback for the new-source branch.
- `merchant-knowledge.server.ts:496–512` rewrites every position even when the requested order already matches. Compare order first. Retain the Shop lock, exact tenant ID-set validation and two-phase conflict-safe movement under the unique `(shopId, position)` constraint.
- `services/recoveries/recovery-human-commands.server.ts:47–63` already obtains Shop status under its lock, then rereads it. Carry the locked value into the local check; keep fresh subscription, restriction, recipient and template checks.

Knowledge's source list includes dormant sources after a plan downgrade. Capping it at the **current** plan allowance would hide configured data. Any future pagination must preserve management of dormant sources; this is not an excuse to erase the list's existing semantics.

### F12. Several nominally idempotent paths still perform repeat writes

Three narrow changes can reduce writes without weakening safety:

| Path | Current behaviour | Minimal correction |
|---|---|---|
| Recovery-policy no-op | `services/recovery-policy/recovery-policy.server.ts:157–172` clears selected discounts, sets requested selections, then checks no-op | Compare complete desired/current state under the existing lock/revision boundary first; update only added/removed selections |
| Confirmed hosted paid plan change | `shopify-billing-operation.service.ts:321–339` calls a CONFIRMED `ensureOperation` that already confirms at 677–678, then confirms again; each confirmation updates and rereads | Retain one guarded confirmation and its result |
| Exact current billing-period projection | `billing-period-projection.ts:215–230` computes `repaired: false` but still updates the unchanged period | Skip identical period UPDATE; retain conflicts and missing-counter repair |

The existing `tests/unit/recovery-policy-save.test.ts:93–106` explicitly expects two discount updates in its no-op case. That test needs a changed behavioural expectation alongside the eventual fix. Provider selection ownership, concurrent sync and revision rejection remain required.

These are stronger optimization candidates than deleting rereads that protect a transaction against an actual concurrent writer.

### F13. Knowledge adds redundant action revalidation; polling needs stable bounds

`moda-interact/app/components/settings/MerchantKnowledgeSection.tsx:64–67` explicitly revalidates whenever any fetcher contains successful data. [React Router's v7 API](https://api.reactrouter.com/v7/functions/react-router.useRevalidator.html) states that action submissions already revalidate page data. For these fetcher actions, the extra effect is redundant.

The effect depends on whole fetcher/revalidator objects and does not consume success by operation identity. The following processing interval also depends on the whole revalidator object (`69–81`). Persistent success data plus changing hook identities could cause repeated refreshes or reset the nominal deadline.

**Qualification:** an infinite refresh loop or a reset deadline was not reproduced with the exact 7.18.2 mounted router. The existing component test mocks fetcher data to undefined and cannot establish real post-success behaviour. Do not report a confirmed production refresh storm.

**Smallest correction:** remove the extra fetcher-success revalidation, use a stable processing deadline and prevent overlapping polls. Preserve the separate upload form's one-time refresh at `MerchantKnowledgeUploadForm.tsx:239` because its finalization uses plain `fetch`.

If remaining processing polls are still expensive, consider a narrow status reader rather than rerunning the entire settings projection. First measure the need; do not introduce another endpoint solely on speculation.

The recovery command panel similarly polls every four seconds while pending (`routes/app/recovery-detail/human-conversation-panel.tsx:107–117`). At a sustained pending state, 15 interval ticks per minute each run a five-call resource and one resolver GraphQL request: 75 data calls and 15 GraphQL requests, plus its immediate poll. This is conditional arithmetic, not an observed request rate. A cheaper authenticated resolver helps every such resource without weakening command admission.

### F14. Promotions and usage have smaller composition improvements

`moda-interact/app/routes/app/promotions/route.tsx:22–52` invokes three readers that each load the same Shop/subscription context (`services/promotions/promotion.service.ts:163–178,224,266,334`). Authorized loading costs eight reads after the resolver, or 18 with resolver and parent. Share that context within the request.

The reader fetches all matching active/date/tenant/plan campaigns, filters missing requested-locale translations in memory, and the route then slices six items. The status, date and scope predicates already run in the database (`promotion.service.ts:227–237`); translation filtering occurs at lines 255–257. Bound retrieval around the actual translated set; applying an arbitrary `take` before that filter can return too few or the wrong offers.

Usage history performs count and sum with the same filter (`services/usage/history.server.ts:212–231`). One aggregate containing `_count` and `_sum` can replace the pair.

Keep usage's tenant/period admission, bounded 25-period keyset list, bounded usage page and one combined source-resolution query. Source resolution is already not an application-level per-row query.

A promotion concurrency integration test expects both same-campaign selections to succeed, while current service logic rejects an already-active selection. This is static test/implementation drift, not an executed failure. Decide the intended behaviour before changing either the transaction guard or its expectation.

## 5. Ingress, failures and lifecycle completeness

### F15. Generic ingress is lean; Redis publication has avoidable probes and incomplete deadlines

`moda-interact/app/services/webhooks/shopify-webhook-ingress.service.ts:134–155` performs one application-level Shop lookup for a valid supported event and no database writes. The row supplies current lifecycle admission and trusted tenant identity; it is not redundant with an SDK Session lookup.

Select only the used `id`, `domain` and `status` fields. Truly unsupported topics can be ignored before this read: they are classified early but currently checked only at lines 247–264. That saves a read for unsupported events, not for the normal subscribed stream.

Unknown/inactive shops are logged as `QUARANTINED` and ACKed without a durable replay record. Clarify the outcome name or policy. A new quarantine table is not automatically required, and this review does not authorize changing admission policy.

Queue work is separate from SQL. Fresh checkout/cart/order publication does `getJob(currentId)`, `getJob(legacyId)` and then `add` (`shopify-webhook-queue.server.ts:215–250`). The 3.5-second helper timeout wraps only `add`. The source probe leaves the first `getJob` unresolved: no timer is armed and `add` is never reached. Discount's pre-read also sits outside its deadline; consent times pre-read and add separately, allowing roughly seven seconds across the two waits before other request work.

[BullMQ custom job IDs](https://docs.bullmq.io/guide/jobs/job-ids) already provide atomic duplicate prevention for an existing job in a queue. The preliminary reads are not the concurrency guarantee. A simpler normal path is deterministic ID plus bounded `add` with correct inserted/already-present semantics.

**Guardrails:** inspect live legacy-job rollout/drain state before removing a compatibility lookup. Use one overall publication/request deadline. [Shopify's documented full webhook response deadline](https://shopify.dev/docs/apps/build/webhooks/verify-deliveries) is five seconds; a 3.5-second timeout on only the final operation does not satisfy that end-to-end budget by itself.

Completed jobs removed with `removeOnComplete` no longer provide the queue's dedupe record. Background already has order terminal-state/CAS, activity timestamp and consent-observation guards. This review has not demonstrated duplicate charging or delivery after job removal. Preserve and test those guards; do not add a per-delivery database outbox solely to reduce redundant work.

Lifecycle services have a different profile. Uninstall/scope handling reads by domain, locks, then rereads. The **post-lock** state is necessary. A targeted lock query that resolves the domain and returns required fields could consolidate calls; simply deleting the reread would introduce a race.

Discount unavailability currently uses two updates to preserve the first `unavailableAt` while correcting `isAvailable` (`shopify-discount-lifecycle.service.ts:70–98`). At minimum filter already-false rows from the first update. Do not discard the first-timestamp semantics to reduce two calls to one.

### F16. Several fallback paths suppress the cause or change its meaning

The existing Shared logger should remain the diagnostic boundary. Keep merchant-safe responses while preserving the original Error/cause and bounded safe provider details.

Concrete examples:

| Boundary | Current loss or misclassification | Needed behaviour |
|---|---|---|
| Billing callback | Catches at `callback/route.tsx:159,208` discard errors; a database failure can be recorded as `PARTNER_API_ERROR` | Log/classify original DB versus provider failure |
| Provider HTTP | `shopify-billing.provider.ts:155–158,398–399` keeps status but drops other safe failure context | Preserve available safe response/request diagnostic and cause without credentials |
| Webhook publication | Wrappers drop cause; ingress catches and returns 503 with only a reason code | One shared structured error retaining original Redis/provider failure; keep retry response |
| Discount webhook success | Returns before the common ENQUEUED/DUPLICATE outcome log | Route success through the same final outcome recording |
| Knowledge entitlement | Reader returns retryable `unavailable` after a DB error; mutators map every non-entitled result to 403 `DENIED` | Distinguish unavailable from actual plan denial |
| Upload HEAD | Every R2 error becomes `UPLOAD_OBJECT_NOT_FOUND` | Distinguish genuine missing object from service/transport/credential failure |
| Recovery and billing read fallbacks | Safe UI state returned without original server diagnostic | Keep safe display and add bounded diagnostic at the owning boundary |

Evidence includes `webhooks/shopify-webhook-queue.server.ts:246–249,474–477,514–517`; `shopify-webhook-ingress.service.ts:236–264,401–431`; `shopify-webhook-observability.server.ts:117–143`; `merchant-knowledge-entitlement.server.ts:50–58`; `merchant-knowledge.server.ts:360–361`; `upload.server.ts:268–272`; and recovery loaders' catch blocks.

This does not imply every catch is wrong. Expected validation rejection, health dependency probes and isolated logging failures have legitimate fallback semantics. Do not log raw webhook bodies, customer messages, tokens or secrets.

Subscription-ended notification has a separate durability question. Sync commits `NO_CONTRACT` before notifying. `subscription-ended-notification.service.ts:61–72` suppresses persistence/dispatch failures except a special identity error. A later no-contract sync does not retry because the previous state is already `NO_CONTRACT` (`subscription-sync.service.ts:112–155`). Existing tests intentionally permit best-effort notification.

At minimum preserve diagnostic evidence. If the notice is a required durable function, use the existing support pending-message/retry lifecycle with the transition, then publish after commit. That is a product/architecture decision; it does not justify another generic outbox system by default.

### F17. Existing privacy handlers need explicit fulfilment and retention scope

These findings concern implemented functionality and database relationships. They are not a legal assessment.

`moda-interact/app/routes/webhooks/customers/data-request/route.jsx:32–48` only looks up Shop, logs PROCESSED and returns 200. No export, durable request or actionable fulfilment record exists in that handler. Removing its lookup would reduce cost without delivering the function implied by the handler.

`customers/redact/route.jsx:33–103` clears four Customer fields and closes active phone intervals, but retains phone/canonical phone values and historical message/recovery data. There is no rehydration fence against later background customer refresh. Its exact numeric-string lookup can miss an existing GID alias accepted by Background; new Background-created customers generally use numeric IDs, so this is a legacy/alias case, not a claim that all current rows use GIDs. Large numeric IDs may also have lost precision before the parsed value is converted to String.

`ARCH-045-SHOPIFY-003` and `004` already describe privacy work as outside the consent scope and are superseded. Do not reopen those tasks or silently assign erasure/export to consent work.

Shop erasure adds an atomicity problem. `webhooks/shop/redact/route.jsx:33–40` deletes Sessions and then Shop in separate operations. The actual schema has direct restrictive Shop relations, including PromotionalCreditGrant (`schema.prisma:1949–1953`), WhatsAppTemplatePublicationTarget (`2733`), CommerceAuditEvent (`3507`) and CommerceStudioMerchantAccess (`3572`). One such retained dependent row can reject Shop deletion after session removal has committed.

**Needed decision:** define which data is erased, retained or de-identified, who owns fulfilment, how retries work and how rehydration is prevented. Implement against the full current relation graph with an atomic or durable resumable boundary. Do not turn every foreign key into CASCADE. Validate a populated shop with grants and publication targets, not just an empty fixture.

### F18. Category selection may need a lifecycle check under its existing lock

The category route verifies ACTIVE before preparation (`moda-interact/app/routes/app/store-profile/category/route.ts:10–22`). The service later selects only ID while locking the Shop row and neither checks status nor verifies that a row was returned (`services/store-profile/store-category-selection.server.ts:183–197`). A lifecycle transition can occur between route preflight and that lock.

If category changes must require ACTIVE **at commit**, check that state through the existing locked Shop row. This is a conditional policy/race finding, not a reproduced database race. Keep rendering outside locks, current template/mapping checks under lock, expected-generation CAS and selection-time draft provenance.

Do not conflate this with onboarding milestone ordering. `ARCH-017-SHOPIFY-002` deliberately separates the onboarding milestone from later billing outcomes. `ARCH-023-SHOPIFY-003` R8/R9 preserves that separation and requires category activation after subscription commit. Existing callback tests intentionally retain the milestone before preparation and allow confirmed unmapped/catalogue-error outcomes.

A `NO_PENDING` or `SUBSCRIPTION_NOT_ACTIVE` category result combined with a later resume short-circuit is worth lifecycle policy coverage. It does not authorize moving the milestone after category activation. The missing Background activation hook is already acknowledged cross-repository work in ARCH-023, not a newly discovered task to recreate.


## 6. Route and mutation ledger

These ledgers make future changes reviewable. They are branch-specific source counts, not production measurements. `S = 3` for the unchanged-Shop resolver, `P = 7` for the matched parent, `G = 4` for recovery access and `K = 5` for settings access. Each S also makes one Admin GraphQL request. Authentication SDK work is additional and unmeasured.

### Pages and read resources

| Route or branch | Child/resource data calls | Parent + child when both run | Important condition |
|---|---:|---:|---|
| Ordinary active home | 12 | 19 | Current plan handle, valid overview range |
| Onboarding home | 8 | 15 | Also taxonomy-suggestion GraphQL |
| Legacy home usage redirect | 5 / 6 | 12 / 13 | Extra call only for valid explicit bill lookup |
| Recovery list | 5 / 6 | 12 / 13 | Nonempty / empty result |
| Recovery detail | 11 | 18 | Customer/conversation present, both sections nonempty |
| Detail with eligible follow-up catalogue | 15 | 22 | Successful candidate catalogue |
| Standalone messages or related section | 7 / 6 / 5 | — | Nonempty / empty / no conversation or customer |
| Command status resource | 5 | — | Status projection after recovery access |
| Pending recoveries resource | 4 | — | Further work is Redis, not Prisma |
| Recovery settings | 21 | 28 | Active opt-in knowledge feature and at least one source |
| Compatibility features redirect | 0 | Parent may execute | No own business read |
| Merchant support | 7 | 14 | Bounded page, default 25/max 50 |
| Promotions | 11 | 18 | Authorized shop |
| Billing options | 20 | 27 | Active current cycle, no pending provider plan |
| Billing status | 4 | — | One subscription read after resolver |
| Billing select | 9 | — | Capacity's full healthy branch |
| Purchase history | `6 + 3N` | `13 + 3N` | N qualifying ACTIVE rows; clamp adds one read |
| Usage with selected period | 10 | 17 | Nonempty source IDs |
| Usage with no selected period | 6 | 13 | No event page/source projection |
| Reinstall loader | 4 | — | Mutation/reconciliation branch differs |
| Authentication callback/catchall | SDK cost + S where resolved | — | Reinstall/provisioning adds branch work |
| Liveness | 0 | — | No dependency probe |
| Readiness | 1 direct pg SELECT | — | Plus Redis PING, not Prisma |
| Public/privacy static pages; public telemetry probe | 0 | — | No business DB work |

Settings subtracts one call when there are no knowledge sources, and another activation-preference call when the opt-in feature is absent/inactive. Failed, denied, first-install, profile-change, stale-revision and retry branches have different counts. Onboarding resume is intentionally branch-dependent: an already-complete milestone can return after S; other branches perform projection/sync/category work.

Primary route evidence is enumerated in `route-inventory.csv`. Service-level candidate calls are in `database-call-inventory.csv`. These inventories support navigation; the call graph and stated branch assumptions determine the totals.

### Mutations, excluding subsequent page revalidation

| Action or branch | Data calls including its access guard | Additional work or qualification |
|---|---:|---|
| Mark one owned support message read | 5 | One resolver GraphQL |
| Compose support message | 7 / 8 | No translation / translation; queue hint after commit |
| Recovery control to HUMAN / AI | 12 / 9 | Different outbound admission requirements |
| Human command idempotent replay | 8 | Keep replay identity and scoped lookup |
| New permitted human text | 15 | Successful open-window branch |
| New eligible follow-up | 21 / 22 | Existing / newly created sequence-two attempt |
| Recovery policy no-op | 10 / 11 | Empty / nonempty selected IDs; includes two avoidable updates |
| Recovery policy changed | 11 / 12 | Same selected-ID distinction |
| Feature preferences unchanged / n changed | 8 / `10 + n` | Current entitlement and output refresh |
| AI delay unchanged / changed | 7 / 8 | Already skips identical update |
| Category pending selection | 12 / 15 | Existing profile/lineage / initial missing rows |
| Active category reselection | 14 / 15 | Existing draft / create draft |
| New promotion selection | 10 | First successful attempt; retries additional |
| New fixed-price credit purchase | 27 | 20 reads + 3 writes + raw lock after S; three Partner requests |
| Existing purchase receipt replay through current route | 13 | One avoidable pre-service Partner request |
| Eligible refund request | 12 | Partner work inside current transaction; development-store GraphQL also |
| Reactivate held credit | 9 | Positive held balance; first successful attempt |

High mutation counts are not automatically waste. Human command admission and payment accounting deliberately perform current checks after acquiring locks.

### Knowledge actions

Each current action begins with K=5. These branches assume an available active opt-in feature and no retry/failure. Provider/R2 requests and postcommit queue hints are excluded from data-call counts.

| Action or branch | Calls including K |
|---|---:|
| Create web source | 14 |
| Edit web source, unchanged / changed URL | 15 / 16 |
| Edit uploaded source | 13 |
| Refresh web source | 15 |
| Reorder N sources | `9 + N` |
| Delete leaving N sources | `11 + N` |
| Upload intent | 13 |
| Finalize new / replacement uploaded source | 18 / 19 |
| Reprocess uploaded source | 17 |
| Upload-failure telemetry | 5 |

Sources: `services/merchant-knowledge/merchant-knowledge.server.ts:343–512` and `upload.server.ts:126–481`. The ledger intentionally exposes both the discarded access-row read and the distinct locked admission inside the service.

### Webhooks

These counts exclude `authenticate.webhook` and its SDK session work.

| Handler or branch | Explicit application data calls |
|---|---:|
| Generic invalid/conflicting delivery metadata | 0 |
| Generic supported active-shop event | 1 Shop read; no DB writes |
| Generic unknown/inactive or unsupported topic | 1 Shop read |
| Uninstall known Shop | 7, plus session deletion if SDK supplied a session |
| Uninstall unknown Shop | 1, plus conditional session deletion |
| Scopes update, known eligible Shop, SDK session present | 6 |
| Scopes update, missing discount permission, SDK session present | 8 |
| Scopes update, otherwise ineligible with permission | 5 with SDK session, 4 without |
| Scopes update, unknown Shop | 1 |
| Customer redact, found customer | 4 |
| Customer redact, no ID / unknown Shop / unknown customer | 0 / 1 / 2 |
| Customer data request | 1 |
| Shop redact | 2; cascade/restrict work is not included |

A missing SDK session removes its conditional Session update. A known-shop scope update with no usable offline session follows the unavailable branch and costs seven calls. Those conditional branches should not be collapsed into a single universal number.

## 7. Simplification boundaries to preserve

The target design can remain inside the current services:

1. **Authenticate once per independently callable request.** Resolve one trusted local tenant context and reuse it for composition. Do not rely on a parent loader to protect standalone endpoints.
2. **Separate reads from provisioning and mutation.** Read-only page projection should consume explicit inputs. First-install repair, profile refresh and lifecycle transitions should have deliberate owners.
3. **Share immutable facts only within their validity boundary.** Request-local subscription/counter/catalogue data can serve several views. A later mutation or Background job must still read current authoritative state.
4. **Keep write transactions short and decisive.** Perform provider/R2 observation outside; compare current local identity/version/cycle inside; commit accounting and durable intent atomically; publish after commit where that is the established contract.
5. **Bound repeated UI work.** Batch visible support IDs, poll only while needed, preserve stable deadlines and request narrow status only when the remaining cost warrants it.
6. **Keep one error model at the owning boundary.** Distinguish denied, absent, malformed and temporarily unavailable; retain safe original diagnostics through the existing Shared logger.

Specific good properties must survive:

- Subscription projection getters each perform one read and do not automatically reconcile or mutate. Billing service construction is inert.
- There is one module-level Prisma client rather than a new client per request. Startup credential bootstrap is not a per-request duplicate.
- Recovery overview uses database aggregation plus a five-row preview in one RepeatableRead snapshot. Lists use tenant-scoped keyset pagination and bounded queries.
- Existing recovery/message composite indexes cover the principal tenant/time/key patterns. Do not add duplicate indexes from call counts without representative actual query plans.
- Recovery commands retain Shop-before-Conversation lock order, revision CAS, tenant-scoped idempotency, current subscription/restriction/recipient/window/template checks and atomic sequence-two claims. The current claim already uses an internal UUID; do not reopen the superseded client-key collision defect.
- Knowledge writes retain active-Shop and scoped source/asset locks, durable revisions, current type/count/entitlement checks, external HEAD before SQL and current asset/expiry validation inside. Postcommit queue publication and pending-revision reconciliation are intentional.
- Category rendering stays outside locks; template/mapping freshness, expected selection generation and selection-time draft provenance stay inside their existing protocol.
- Generic webhook ingress stays a normalizer/publisher, with no synchronous checkout materialization, billing reservation or AI work. Its direct BullMQ acceptance is an accepted boundary.
- Consent refresh hints do not become consent authority. Background still validates and observes current state.
- SDK session access, tenant lifecycle admission and later Background validation solve different problems. Similar IDs do not make those reads interchangeable.

## 8. Verification performed and reproducible evidence

The evidence scripts execute the **unchanged source** with synthetic imports/in-memory DB, authentication, queue and network boundaries. They are review instruments, not replacements for the repository's test suite.

### Completed checks

| Check | Result and limit |
|---|---|
| Schema/migration comparison | Canonical and nested schema plus 72 migration-directory files match |
| Raw relation inventory | Initial paid `shopify.Shop` reference absent from supplied schema; other inventoried literal relations resolve |
| Resolver source probe | 3 reads/1 GraphQL for unchanged shop; 6/2 for two concurrent calls; conditional profile writes |
| Resolver diagnostic probe | If an errors-only GraphQL body reaches this service, its provider marker is lost in a generic error without cause; real SDK handling remains unmeasured |
| Lock source probe | Actual paid SQL names `shopify.Shop`; free lock schemas correctly identify ShopSettings and Subscription |
| Billing source probe | Purchase-history formula at 1/5/20 rows; eligible fixture outcomes; refund root/provider work during transaction; malformed successful provider body becomes null |
| Webhook source probe | Duplicate uninstall removes replacement Session while preserving marker; consent config expectation false; stalled getJob has no active timeout |
| Evidence-package replay | All three probes reproduce recorded JSON; lexical inventories reproduce against the same snapshot |
| Source integrity | Review package contains documentation, inventory and probes; no runtime/schema/task-index changes are part of the intended patch |

The snapshot has no Git history and no installed app `node_modules`. No packages were installed. No real PostgreSQL, Redis, Shopify SDK/provider, R2, integration suite, complete Vitest suite, browser runtime or load benchmark was executed. Existing test code was inspected; a test's presence is not a passed test.

Environment metadata such as Node version, Git presence and dependency-directory presence may differ when these scripts run in the developer's checkout. Compare source hashes and substantive observations; do not demand whole-file identity for environment metadata across different machines.

### Reproduce from the parent workspace root

The scripts do not change application source. The Python inventory writes only to the explicitly supplied output directory below.

```sh
command -v node >/dev/null 2>&1 || source scripts/bootstrap-node.sh

REVIEW_DIR=docs/architecture/reviews/shopify-database-20261103-235702-r01
REVIEW_OUTPUT=$(mktemp -d)

node --experimental-vm-modules --no-warnings \
  "$REVIEW_DIR/probe-shop-resolver-and-locks.mjs" . \
  > "$REVIEW_OUTPUT/resolver-and-locks.results.json"

node --experimental-vm-modules --no-warnings \
  "$REVIEW_DIR/probe-billing.mjs" . \
  > "$REVIEW_OUTPUT/billing.results.json"

node --experimental-vm-modules --no-warnings \
  "$REVIEW_DIR/probe-webhooks.mjs" . \
  > "$REVIEW_OUTPUT/webhooks.results.json"

python3 "$REVIEW_DIR/audit-source.py" . "$REVIEW_OUTPUT/inventory"
```

The recorded runtime is Node 24.22.1. The probes need Node's built-in TypeScript stripping and VM-module support. They intentionally avoid installing app dependencies or calling real services. Each contains assertions and fails if its targeted observation changes.

### Targeted verification needed with implementation

| Change area | Necessary check |
|---|---|
| Paid activation/schema/order | Migrated PostgreSQL initial-paid callback; concurrent callback lock interleaving; correct free path retained |
| Provider parser | Missing data/field, malformed values and explicit null; malformed input makes no subscription-state write |
| Refund | Provider preflight failure leaves no hold; lifecycle/cycle changes before transaction reject safely; concurrent CAS accounting |
| Uninstall/reinstall | Route+service+Session duplicate/concurrent cases; cleanup failure and retry; fresh credential retained |
| Request composition | Count actual SQL and provider calls for representative authenticated routes; preserve independent resource authorization |
| Support batching | Owned/foreign/already-read/unseen IDs, bounded batch, first timestamp and idempotence |
| Read/no-op changes | One badge query; one detail owner projection; zero discount writes on true no-op; unchanged order produces no position writes |
| Knowledge UI | Exact-version mounted router after successful action; stable deadline and no overlapping polls; plain-fetch upload refresh retained |
| Webhook queue | Deadline includes stalled pre-read/add; duplicate and legacy transitions; retry after ambiguous acceptance and completed-job replay |
| Privacy | Retention/fulfilment contract first; then populated restrictive graph, partial failure/retry and rehydration cases |

The existing PostgreSQL recovery query-plan suite is useful: `tests/integration/recovery-detail-query-plans.test.ts` uses real query builders and checks bounded arms/index behaviour behind its explicit environment gate. Run it when changing those queries; it was not run here.

## 9. Suggested review sequence

This is a sequence of architectural decisions and focused changes, **not newly authored implementation tasks**.

1. Correct the paid activation relation and agree its coherent lock order; reject malformed provider evidence; move refund observation outside its transaction.
2. Align uninstall cleanup with the existing lifecycle fence and reconcile environment-specific webhook declarations.
3. Take the simplest broad merchant wins: dedicated support badge count, bounded acknowledgement batch, one purchase-history context, removal of unused billing aggregate and true no-op writes.
4. Consolidate request-local Shop/subscription/settings context and read projections. Measure actual SQL/provider calls before setting final budgets; keep independent endpoint guards.
5. Remove redundant revalidation and stabilize polling; simplify queue pre-reads/deadlines only after resolving compatibility rollout requirements.
6. Scope privacy fulfilment/retention separately and clarify whether subscription-ended notices require durability. Do not disguise product/lifecycle decisions as performance refactoring.

No `_index.md`, task state, acceptance record, schema, runtime source or submodule pointer is changed by this assessment. No developer branch, worktree, commit SHA, push, deployment or production measurement is claimed. The supplied task acceptance commands are the delivery model; this revision is an architectural assessment with reproducible evidence, not acceptance of an implementation attempt.

## 10. Package contents and external references

The patch adds this one directory:

`docs/architecture/reviews/shopify-database-20261103-235702-r01/`

It contains the review, three Node probes, one Python inventory script, their three recorded probe results, three CSV inventories and the source baseline JSON. The separate ZIP contains the identical standalone patch. A standalone copy of this report accompanies the patch for direct reading.

External primary references inform framework/provider semantics only; source findings and versions are anchored to the supplied snapshot:

- [React Router middleware and independent loaders](https://reactrouter.com/how-to/middleware): why shared context must retain independently callable route authorization. Current docs are not proof of exact installed hook identities.
- [React Router v7 useRevalidator](https://api.reactrouter.com/v7/functions/react-router.useRevalidator.html): action submissions already trigger revalidation.
- [BullMQ custom job IDs](https://docs.bullmq.io/guide/jobs/job-ids): uniqueness for existing jobs and loss of that deduplication record after job removal.
- [Shopify webhook delivery requirements](https://shopify.dev/docs/apps/build/webhooks/verify-deliveries): verification, duplicate delivery and full response deadline.
- [Shopify webhook subscriptions](https://shopify.dev/docs/apps/build/webhooks/subscribe): app configuration as a subscription declaration mechanism; deployed configuration must be verified separately.
