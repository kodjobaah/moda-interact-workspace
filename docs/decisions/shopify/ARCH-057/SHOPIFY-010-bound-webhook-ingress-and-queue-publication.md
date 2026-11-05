---
id: ARCH-057-SHOPIFY-010
architecture_id: ARCH-057
title: Bound Shopify webhook publication and remove redundant queue probes
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 70
executor: codex
claimed_at: 2026-11-05T00:12:20Z
attempt: 1
depends_on:
- ARCH-057-SHOPIFY-009
enables:
- ARCH-057-SHOPIFY-011
created: 2026-11-04
updated: 2026-11-05
---

# ARCH-057-SHOPIFY-010: Bound Shopify webhook publication and remove redundant queue probes

## Architecture

Architecture ID: `ARCH-057`.

Architecture document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`.

Coordinator: `moda_architect`.

Mandatory execution, diagnostic and naming contract: `docs/architecture/ARCH-057/task-contract.md`.

**Materialised task definition; Ready and unclaimed.** ARCH-057-SHOPIFY-009 Attempt 2 is architect-accepted and Complete at implementation `f0cf26877a9e3f7503c0f9a956b02ede3eff2571`; its acceptance satisfies this task's sole prerequisite. Normal launcher preparation and claiming are required before execution. No implementation, deployment or passing runtime test is asserted for this task.

## Objective

Make each supported authenticated webhook perform one useful tenant lookup and one deterministic BullMQ add under one publication deadline, with truthful acknowledgement and original safe diagnostics when publication fails.

## Context

Generic ingress currently reads the full Shop even for unsupported topics. Checkout/cart/order publication first reads the current job ID and then a legacy ID; those reads occur outside the 3.5-second add timeout. Discount has the same unbounded pre-read. Consent has separate read/add budgets. These existence checks cannot provide atomic deduplication, which already belongs to BullMQ's custom job ID.

Publication wrappers drop original causes; the ingress consumes typed failures and returns 503 without an error record carrying that evidence. Discount success returns before the final semantic outcome. Unknown/inactive Shop deliveries are acknowledged and discarded but labelled `QUARANTINED`, although no durable quarantine exists.

The chosen design keeps the direct queue acceptance boundary, existing Shared payloads and current deterministic IDs. It removes speculative per-delivery existence probes and uses one local accepted outcome, because BullMQ add does not reliably distinguish a new job from an existing ID without additional observation. This task does not claim exactly-once business effects or a durable receipt.

## Scope

Paths are relative to `moda-interact`.

### Existing files to modify

| Path | Selected responsibility |
|---|---|
| `app/services/webhooks/shopify-webhook-ingress.service.ts` | Classify unsupported topics before the Shop read; select only id/domain/status; explicit success/error outcomes for every supported branch; preserve original publication diagnostics |
| `app/services/webhooks/shopify-webhook-queue.server.ts` | One add and one total publication deadline per call; retain current ID bytes and queue contracts; preserve cause/code/stage; own safe queue-emitter diagnostics |
| `app/services/webhooks/shopify-webhook-observability.server.ts` | Extend the SHOPIFY-009 domain adapter for publication and connection-event failures; no competing logger/serializer |
| `app/services/webhooks/shopify-webhook-observation.ts` | Keep the narrow semantic observation contract; document accepted/discarded outcomes truthfully without carrying error/payload objects into metric dimensions |
| `app/services/otel/shopify-webhook-telemetry.server.ts` | Recognize the selected accepted/discarded outcome names; retain metric/span names and bounded attributes |
| `app/routes/webhooks/root/route.jsx` | Reconcile the documented failure owner if needed; retain authentication, exact consent raw-body handling, response and framework propagation |
| `tests/unit/webhooks/shopify-webhook-queue.server.test.js` | New single-add/accepted contract and unchanged deterministic ID/queue/payload options |
| `tests/unit/webhooks/shopify-webhook-ingress.service.test.js` | Route/topic/query-count/typed failure/success cases |
| `tests/unit/webhooks/webhooks-route.test.js` | Independent HMAC boundary, auth denial and unexpected failure propagation |
| `tests/unit/otel/shopify-webhook-ingress-traceid.test.js`, `tests/unit/otel/shopify-webhook-telemetry.test.js` | Trace preservation and new truthful accepted-outcome classification |
| `tests/integration/shopify-webhook-queue-telemetry.test.ts` | Reuse the task-owned disposable Redis helper, preserve actual producer/worker trace continuity and unchanged business payload |
| `package.json` | Add the two exact test commands below; no dependency/version change |

### New files

| Path | Purpose |
|---|---|
| `tests/unit/webhooks/shopify-webhook-deadline.test.ts` | Deterministic fake-clock cases for the one budget, completion cleanup and late resolution/rejection |
| `tests/unit/webhooks/shopify-webhook-failure-logging.test.ts` | Real Shared output, original message/cause/code, privacy and sink-isolation cases |
| `tests/integration/shopify-webhook-publication.redis.integration.test.ts` | Real BullMQ concurrent duplicate, tenant separation, retained-ID and late-add/retry evidence |
| `tests/helpers/shopify-webhook-redis.ts` | Bounded disposable Redis process/container ownership and separate control connection; no inherited service URL |
| `tests/helpers/shopify-webhook-fixtures.ts` | Small canonical Shared-validated synthetic fixtures for the six publishers |
| `docs/shopify-webhook-publication.md` | Query/add budget, outcomes, legacy-probe retirement boundary, delivery guarantees and run evidence |

Each new test/helper file remains below 300 lines. The declared `tests/helpers/shopify-webhook-redis.ts` helper uses existing `bullmq`, `ioredis` and Node tooling. It starts an isolated task-owned `redis:7.4.2-alpine` Docker container bound to a random loopback port, matching the existing system-test image. Use this helper from both named Redis suites. Do not point these tests at a caller-supplied production/shared `REDIS_URL` or import another implementation repository's internals.

## Out of Scope

No PostgreSQL receipt/outbox, quarantine table, Redis cache, extra queue, new delivery/event identity, cross-request tenant cache, schema/index change or Shared publication. No changes to checkout/cart/order/discount/consent payload schemas, ordering keys, queue/job names, downstream admission, recovery timing, consumer retries or accounting/idempotency.

No customer data export/erasure policy or compliance-handler rewrite. No generic HTTP timeout framework, global error registry, additional HTTP metric/span, retrying provider request from the webhook route or guarantee that a timed-out Redis command was cancelled.

Do not change `removeOnComplete`, `removeOnFail`, attempts or backoff to manufacture deduplication retention. No blanket queue purge, production deployment or automatic migration/replay of legacy work is authorised.

## Requirements

### A. Keep authentication and one necessary tenant read

1. Authenticate through the existing SDK before trusting topic/domain/delivery metadata. Preserve raw-body cloning only for the consent topic and the exact large numeric customer-ID normalization; never replace it with ordinary rounded JSON number handling. Do not accept a tenant ID from a payload or request query.
2. Validate metadata as today. Then classify commerce, discount and consent topics before touching the database. A genuinely unsupported authenticated topic returns the existing successful ignore response with zero Shop reads and no Redis operation. Invalid metadata still produces the existing 400 behavior; bypassing metadata checks because a topic is unsupported is not selected.
3. Supported topics perform exactly one repository Shop lookup with `select: {id: true, domain: true, status: true}`. Retain this authoritative internal tenant/lifecycle lookup; it is not redundant with the SDK's Session storage read. Count SDK-internal persistence separately and do not claim a one-SQL-statement HTTP request.
4. Unknown and inactive Shops remain acknowledged without publication. Rename their diagnostic outcomes to `IGNORED_UNKNOWN_SHOP` and `IGNORED_INACTIVE_SHOP`. State explicitly in the documentation that these deliveries are discarded and have no automatic replay. Do not call them durably quarantined and do not introduce persistence to justify the old name.
5. Preserve the existing normalizers, Shared validation, version rules, event envelopes, ordering keys, trace propagation and international context. Invalid supported payloads keep their current bounded rejection behavior and never publish. Errors in internal normalization/schema construction propagate to the named logged owner; do not convert unexpected exceptions into successful ignores.
6. Every successful supported publication, including each discount topic, emits exactly one final queue-acceptance observation and returns 200 only after the add resolves within the deadline. Remove the discount branch's early return that skips that observation. No DB writes, transaction, provider call or customer lookup are added to generic ingress.

### B. Use the current deterministic identity and one add

7. All six exported publishers call `queue.add` directly with the existing current deterministic ID. Remove `findExistingJobId`, all per-delivery `getJob` pre-reads and the regex that interprets arbitrary error messages as duplicates. A real failed add remains a failure.
8. Preserve these exact existing ID constructions for the same input values:

| Publisher | Current deterministic ID |
|---|---|
| checkout created, checkout updated, cart activity | `createTenantReadableJobId(shopId, createShopifyWebhookJobId(shopId, deliveryId))` |
| order completed | `createTenantReadableJobId(shopId, createShopifyOrderJobId(shopId, orderId))` |
| discount sync | Shared `createShopifyDiscountSyncJobId(event)` |
| WhatsApp consent sync | Shared `createShopifyWhatsAppConsentSyncJobId(event)` |

The existing `shopId--digest` prefix remains unchanged; renaming a local variable away from `legacyJobId` does not change hash input, framing or stored IDs. Queue names, job names and payload versions remain owned by the installed Shared `3.1.0` contract.
9. The local publication result becomes `{queue, jobId, outcome: "accepted"}`. Both a newly added job and BullMQ acceptance of an existing retained ID have that result. Ingress logs `QUEUE_ACCEPTED`. Do not report `DUPLICATE` or claim the job was newly created without evidence. Keep event identity/queue result out of customer responses.
10. Preserve default job options: three attempts, exponential 1,000 ms backoff, `removeOnComplete: true`, `removeOnFail: false`. A replay after auto-removal can create another job and remains an at-least-once delivery. Existing Background durable/monotonic business guards own repeat effects; this task cannot claim new exactly-once behavior.

### C. One deadline includes every publication operation

11. Start one 3,500 ms publication budget at the exported publisher boundary, before lazy queue acquisition/connection readiness and add. Use one small reused local deadline helper that receives the operation, arms the deadline before invoking it and clears its timer on completion/failure. No sequential fresh read/add timeout, unbounded awaited readiness call or outside-budget duplicate probe remains.
12. The deadline is a publication budget, not a claim that authentication and PostgreSQL always fit within Shopify's complete HTTP deadline. Record publication elapsed time separately if needed; do not describe the existing ingress `ackMs` as a measured total-network SLA.
13. Missing connection configuration, queue acquisition/constructor failure, add rejection and deadline expiry all reject through `ShopifyWebhookPublicationError` with the existing bounded Moda code. Extend the Error using optional original `cause`, known stage and already-available queue/job context. Preserve the original safe source message and any actual driver code for the owning diagnostic. A generated timeout/configuration failure has internal origin; do not fabricate a Redis-supplied cause or status.
14. A timeout means the HTTP attempt is not acknowledged as accepted and generic ingress returns 503. A late add can still succeed. Attach completion/rejection handling so no unhandled rejection appears after timeout; do not remove the possible late job or invent cancellation. A subsequent retry uses exactly the same deterministic ID. Real Redis evidence must demonstrate this late-add/retry case with one retained job.
15. Keep Redis work outside every database transaction. Queue construction uses the existing Shared BullMQ telemetry adapter. Attach bounded queue `error` listeners where the producer owns the emitter so connection failures cannot become unhandled events. Use the semantic adapter for errors without an active request; no second telemetry/logging transport or query solely for decoration.

### D. Retire development-era existence probes explicitly

16. Historical `ARCH-004-SHOPIFY-001` and `ARCH-003-BACKGROUND-001` record legacy/new ID compatibility. Read them; do not silently pretend that contract never existed. The selected pre-production target retires only the producer's legacy ID *lookups* and retains all current ID bytes. Existing Background candidate ID compatibility is a different boundary and remains unchanged.
17. Record the release boundary in `docs/shopify-webhook-publication.md`: intended test/staging instances stop the old producer, allow relevant old ingress jobs to complete using the existing consumers, and verify no legacy-format job remains in the affected ingress queues before enabling the simplified producer. Do not add a permanent runtime compatibility flag or preserve two getJob calls indefinitely. Do not delete durable rows, pending-recovery candidates, retained failed jobs or other service work to pass a check.
18. The archive is not proof of current deployed traffic. If a real target has production/live legacy jobs or a rollback requirement that needs the old producer's existence behavior, return that concrete deployment fact to `moda_architect` for a bounded transition decision before rollout. Source implementation and disposable tests must not assert that live drain occurred. No live queue mutation is part of this task.
19. The latest ARCH-056 Background tasks change initial-recovery continuation/persistence, not these ingress payloads or queue names. Do not add a dependency on or modify those tasks. If integrated consumer evidence differs from the unchanged Shared contract, stop with the exact incompatibility rather than inventing producer/consumer adapters.

### E. Log the failure that actually occurred

20. Generic ingress owns publication failures that it converts to 503. It calls the existing domain failure adapter with the original safe exception/cause, actual code/stage, trusted topic/delivery/shop and known queue/job identity, then emits its one final failure outcome. This error record plus semantic outcome is not permission to log the full exception at every caller. Keep the known Shop ID after lookup; do not discard it in the publication catch or query it again for logging.
21. Unexpected DB/internal errors propagate through the generic route's existing failure adapter and are rethrown unchanged. Authentication errors remain owned by the authentication adapter. Lifecycle/scopes and best-effort activation callers remain responsible for their own propagated publication errors under SHOPIFY-009. Document these owners so a queue wrapper is not a second full request error logger.
22. Reuse Shared `createLogger`/`sanitizeLogFields` and the existing environment resolver. Error name/message, safe actual driver code and explicit cause/causeChain (at most four known entries) must reach real emitted JSON. Preserve original exception/cause propagation; safe logging may redact or bound text, with flags, but cannot replace all diagnostic detail with `QUEUE_ADD_FAILED` or an error type.
23. Never log Redis URLs, passwords, API/session tokens, webhook bodies, consent customer identifiers, customer PII, GraphQL data or arbitrary response bodies. Remove sensitive spans in the domain adapter before Shared defense-in-depth sanitization. Expected invalid metadata/payload is bounded rejection control flow, not a fabricated operational/provider failure. Throwing log sinks must not alter status, retries, queue data or propagation.

## Work Items

- [ ] Integrate SHOPIFY-009 observability changes and inspect all six current publishers/callers.
- [ ] Move unsupported-topic admission before the Shop lookup and use the exact required select.
- [ ] Replace pre-reads/message-regex duplicate detection with one current-ID add and accepted result.
- [ ] Apply one overall publication deadline and preserve causes/context across all failure branches.
- [ ] Make success/discard/failure outcomes truthful, including discount success and typed 503 handling.
- [ ] Cover original emitted diagnostics, queue error events, privacy and throwing sinks.
- [ ] Execute real Redis duplicate/tenant/late-add/retry/telemetry cases and record the actual evidence class.
- [ ] Document retirement of legacy producer probes and the explicit rollout evidence boundary.

## Interfaces / Contracts

The six existing exported publisher names and `{event}` input contracts stay unchanged. The repository-local result and error contract is:

```ts
type ShopifyWebhookPublicationResult = {
  queue: ShopifyWebhookQueueName;
  jobId: string;
  outcome: "accepted";
};

// Keep the existing error class and codes; add optional known context/cause.
type ShopifyWebhookPublicationCode =
  | "REDIS_UNAVAILABLE"
  | "PUBLICATION_TIMEOUT"
  | "QUEUE_ADD_FAILED";
```

Use domain names for any helper/type/event. The publication error preserves `cause` and a fixed stage such as `configuration`, `queue_acquisition`, `add` or `deadline`. Do not export a second generic error framework. Extend the existing observability adapter with one thin queue-emitter event function only if needed; it takes queue/stage/error, not raw connection configuration.

Accepted generic ingress outcomes become `QUEUE_ACCEPTED`, `IGNORED`, `IGNORED_UNKNOWN_SHOP` and `IGNORED_INACTIVE_SHOP`; existing rejection/failure codes remain. Update the local telemetry accepted-outcome set and assertions accordingly. Metric/tracer/span names and payload contracts do not change. Record this local observation change in the document so dashboards do not mistake `QUEUE_ACCEPTED` for a count of newly created jobs.

Package additions:

```json
{
  "test:shopify-webhooks": "vitest run tests/unit/webhooks tests/unit/otel/shopify-webhook-ingress-traceid.test.js tests/unit/otel/shopify-webhook-telemetry.test.js",
  "test:shopify-webhooks:redis": "MODA_SHOPIFY_WEBHOOK_REDIS=1 vitest run tests/integration/shopify-webhook-publication.redis.integration.test.ts tests/integration/shopify-webhook-queue-telemetry.test.ts"
}
```

The Redis helper starts and stops only its own isolated container, discovers the random loopback port, waits for actual readiness and closes all clients/Workers/Queues even on failure. Use a separate control connection for `CLIENT PAUSE`/`CLIENT UNPAUSE` or an equivalent deterministic owned transport barrier; no arbitrary sleep is concurrency proof. Container/Redis unavailability makes the mandatory suite blocked, not skipped/pass. Never flush a supplied host Redis.

## Dependencies

- `ARCH-057-SHOPIFY-009` — accepted/integrated lifecycle configuration and webhook diagnostic adapter. This prevents conflicting edits to the common observability file and confirms the supported subscription set.

## Enables

- ARCH-057-SHOPIFY-011

## Acceptance Criteria

- [ ] Valid unsupported topics use zero DB/Redis operations; supported topics use one narrow authoritative Shop lookup without generic-ingress writes.
- [ ] Every supported active publication uses exactly one Queue.add and zero per-delivery getJob calls, with unchanged current deterministic IDs and Shared payload/job contracts.
- [ ] One 3,500 ms budget covers queue acquisition/readiness/add; no separate unbounded or restarted publication phase exists.
- [ ] Success is reported only after add resolves; all six publishers use the truthful accepted result and discount successes emit their final outcome.
- [ ] Unknown/inactive deliveries are explicitly discarded/ignored, with no durable quarantine or replay claim.
- [ ] Timeout/connection/add failures return 503 at generic ingress and preserve original safe error/cause/code and known tenant/job context in emitted Shared records.
- [ ] Late completion/rejection creates no unhandled promise rejection and retry retains the deterministic ID; no possible late job is removed.
- [ ] Concurrent duplicate publication and tenant separation are proved with real BullMQ/Redis; completed-job replay limits are documented honestly.
- [ ] Queue options, normalizers, consent integer/version handling, trace propagation and downstream wire contracts remain unchanged.
- [ ] Legacy producer-probe retirement has a precise pre-production/drain boundary; no live compatibility/drain state is fabricated and no indefinite lookup bridge is added.
- [ ] Raw emitted-record sentinel and throwing-sink tests pass without changing business behavior.

### Required cases, log owners and outcomes

| Case / injection | Owning diagnostic / evidence | Required result |
|---|---|---|
| Unauthenticated HMAC request | Existing auth adapter; original safe SDK error when an Error exists, actual denial status otherwise | SDK denial unchanged; zero ingress DB/queue calls |
| Valid unsupported topic | One `IGNORED` outcome | HTTP 200; zero Shop lookups and zero Redis calls |
| Missing/malformed metadata, invalid cart/checkout/consent ID/API version | Existing bounded rejection outcome, no invented upstream error | Current 400/no-publication behavior; exact consent integer preserved |
| Unknown Shop; inactive Shop | Distinct ignored outcome, no quarantine claim | HTTP 200; one narrow Shop read, no queue work |
| Shop lookup rejection with original marker/code/cause | Generic route failure adapter, `database` origin | Original exception propagated; no queue work |
| Each of six successful publishers; every discount topic | One final `QUEUE_ACCEPTED` observation with queue/job/trusted Shop | HTTP 200 after add; one add, zero getJob |
| Queue configuration/acquisition failure | Ingress failure owner with truthful internal/acquisition stage | Typed 503; no original cause fabricated if none exists |
| Add rejection containing a unique harmless driver marker, code and nested cause | Ingress failure owner preserves safe source marker/code/explicit causes | Typed 503, same deterministic identity on retry |
| Hanging readiness/add; clock reaches 3,500 ms | Ingress owner logs generated deadline with known identity and no invented Redis message | One budget expires, 503; no second budget |
| Add resolves or rejects after deadline | Promise settlement observed, no duplicate final HTTP outcome or unhandled rejection | Original 503 remains; retry uses same ID; no cancellation/removal claim |
| Concurrent same-ID adds while job retained; same delivery in another tenant | Real Redis job/accepted-count evidence | One retained job for first tenant, a distinct job for the second; all successful adds say accepted |
| Successful job is auto-removed then delivery is replayed | Real Redis completion/replay evidence | Replay may create a new job; no exactly-once claim |
| Queue emits error without an active HTTP call | Queue semantic adapter, safe original message/code/cause and queue | No unhandled emitter crash; no credential URL in log |
| Sensitive sentinels in message/cause plus throwing Shared sink | Actual Shared JSON before harness redaction; bounded cause limit checked | Safe marker retained, secrets/PII absent; HTTP/queue behavior unchanged |
| Actual producer/Worker telemetry enabled and disabled | Existing real Redis telemetry suite | Business payload/identity unchanged; trace continuity only when enabled |

For source-level counts, keep SDK authentication/storage outside the repository-call total. Queue telemetry/internal Redis protocol operations are not equated with Queue.add invocation counts. Real Redis tests inspect actual stored jobs; fake timers prove deadline control flow separately. Neither proves live Shopify delivery nor end-to-end consumer idempotency.

## Validation

- [ ] `npm run test:shopify-webhooks`
- [ ] `npm run test:shopify-webhooks:redis` — actual disposable Redis/BullMQ, all required opt-in cases execute rather than skip
- [ ] `npm run typecheck` and `npm run build`
- [ ] Focused ESLint on changed/new source and tests; `git diff --check`
- [ ] Same-fixture before/after repository Shop/Queue.add/getJob invocation evidence, actual Redis stored-job assertions and unchanged deterministic ID vectors
- [ ] Real Shared emitted-log fault/privacy/sink assertions; correct failure ownership for generic ingress, lifecycle callers and queue events
- [ ] Review source compatibility note against the current deployment facts available to the executor; explicitly label live drain/deployment as not performed when unavailable
- [ ] Record source/package provenance, Redis/container version, fixture IDs, command results and cleanup

## Stop Condition

After all defined work and mandatory evidence pass, set this task to review, complete its report and return to `moda_architect`. Do not begin SHOPIFY-011 or deploy the app. Stop if a changed Shared/consumer contract, a real live legacy queue requirement, an unsafe diagnostic extraction, missing real Redis validation or a needed durable delivery mechanism would require different architecture. Do not hide that issue with an outbox, cache, compatibility flag or second queue.

## Implementation Notes

BullMQ custom IDs provide atomic suppression while the job is retained. A successful add is sufficient durable queue acceptance for the existing direct-ingress contract; probing existence first is neither necessary for concurrency nor a substitute for retained business idempotency. The new outcome intentionally avoids an unverifiable duplicate/new distinction.

Legacy ingress ID lookups are not the Background pending-candidate compatibility logic. Preserve the latter. `docs/architecture/ARCH-010-first-production-baseline.md` records the historical pre-production boundary, but its existence does not prove a current deployment is empty; the actual rollout facts remain explicit.

Official behavior references for executor verification: [BullMQ job IDs](https://docs.bullmq.io/guide/jobs/job-ids), [auto-removal](https://docs.bullmq.io/guide/queues/auto-removal-of-jobs), and [Shopify HTTPS delivery handling](https://shopify.dev/docs/apps/build/webhooks/verify-deliveries). Installed locked code and real disposable tests are the implementation evidence. This task does not install tooling or contact production services as part of definition.

## Completion Report

### Status

Not Started. Defined but not materialised; no execution claim or worktree is asserted.

### Files Changed

None. Definition only.

### Work Completed

None.

### Validation Results

Not run. Record exact commands, actual source/build/Shared/BullMQ/Redis versions, case outcomes, call versus protocol evidence, emitted records, legacy-boundary assessment and task-owned resource cleanup.

### Deviations

None.

### Assumptions

The launcher verifies current dependency status and integrated source. No assertion about deployed subscriptions, legacy queue contents or production rollout is made from the archive.

### Unresolved Issues

Implementation and mandatory validation remain outstanding. Live release/drain evidence remains a separate deployment responsibility.

### Architectural Concerns

Return ownership, schema, wire identity, consumer compatibility, durable acceptance or logging-contract changes to the architect.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition only; no implementation accepted.

### Reviewed Files

Definition and latest snapshot producer/ingress/consumer-contract touchpoints only.

### Validation Reviewed

Definition/source inspection only; implementation evidence is outstanding.

### Architecture Conformance

To be assessed after implementation against the parent decision, common contract and unchanged Shared wire contracts.

### Follow-up

Return the completed task for architect review; do not begin enabled work.
