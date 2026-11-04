---
id: ARCH-057-SHOPIFY-002
architecture_id: ARCH-057
title: Stabilise subscription activation and provider evidence
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 3
depends_on:
- ARCH-057-SHOPIFY-001
enables:
- ARCH-057-SHOPIFY-003
- ARCH-057-SHOPIFY-004
- ARCH-057-SHOPIFY-011
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-057-SHOPIFY-002: Stabilise subscription activation and provider evidence

## Architecture

Architecture ID: `ARCH-057`.

Architecture document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`.

Coordinator: `moda_architect`.

Mandatory execution, diagnostic, provenance and validation contract: `docs/architecture/ARCH-057/task-contract.md`. This task is materialised in the canonical launcher-resolved parent and implementation worktrees recorded in its Completion Report. Its dependency, ARCH-057-SHOPIFY-001, is Complete.

## Objective

Make the existing Shopify subscription activation boundary preserve trustworthy provider evidence, acquire its lifecycle locks in one consistent order, and avoid duplicate confirmation or unchanged-period writes while preserving current onboarding and billing semantics.

## Context

The Shopify review records the wrong initial-paid lock relation (F01), malformed successful provider evidence becoming NO_CONTRACT (F02), duplicate confirmation/period writes (F12), and suppressed or misclassified activation errors (F16). The reviewed runtime is byte-identical in the 4 November snapshot named in the mandatory contract.

The accepted onboarding milestone is deliberately separate from subscription and Store Category activation. ARCH-017-SHOPIFY-002, ARCH-023-SHOPIFY-003 and ARCH-026-SHOPIFY-001 remain authoritative. This task fixes the implementation boundary; it does not redefine onboarding completion or make category activation atomic with billing.

## Scope

All implementation paths below are relative to `moda-interact`. Modify only the listed responsibilities. The dependency owns the request-context mechanism; consume its accepted implementation without changing that contract.

### Existing files to modify

| Path | Exact responsibility |
|---|---|
| `app/services/billing/subscription-locks.ts` | Replace the split lock sequence with the single ordered lifecycle-lock function specified below; remove the obsolete late paid-Shop lock |
| `app/services/billing/subscription-activation.service.ts` | Use the ordered lock function, preserve selection fencing and atomic period/counter finalization, and accept truthful retry-failure classification |
| `app/services/billing/subscription-sync.service.ts` | Use the same lock order before current-row rereads, preserve projection on provider parsing failure, and report owned internal/database failures |
| `app/services/billing/hosted-plan-change.service.ts` | Use the ordered locks and supplied failure classification; retain the complete verification fence |
| `app/services/billing/providers/shopify-billing.provider.ts` | Validate the response envelope, share one active-subscription parser between both existing provider operations, and emit safe original provider diagnostics |
| `app/services/billing/billing.types.ts` | Add the narrow retry-failure type below; preserve all existing provider and merchant DTO fields |
| `app/services/billing/billing.service.ts` | Thread the narrow failure argument through its existing facade methods; no constructor I/O |
| `app/services/billing/billing-period-projection.ts` | Skip the already-correct BillingPeriod update, retaining conflict detection and missing-counter repair |
| `app/services/billing/shopify-billing-operation.service.ts` | Remove only the second confirmation of an operation already confirmed by `ensureOperation` |
| `app/services/billing/subscription-ended-notification.service.ts` | Log original persistence/translation failures before existing best-effort continuation; preserve current durable and error-propagation semantics |
| `app/services/billing/billing-reconciliation.service.ts` | Preserve original error/cause on its existing enqueue-failure diagnostic; no queue identity/configuration/deadline changes |
| `app/routes/app/billing/callback/route.tsx` | Consume authenticated request context, use the shared milestone function, classify/log each failure at its actual stage, retain redirects and fenced retry scheduling |
| `app/routes/app/onboarding/resume/route.ts` | Consume authenticated request context, use the same milestone function, log reconciliation/activation failures while retaining existing response and activation gates |
| `tests/unit/services/shopify-billing.provider.test.ts` | Strict envelope/parser fixtures for both provider operations |
| `tests/unit/services/billing/subscription-activation.service.test.ts` | Ordered locks, fresh Shop eligibility, stale-token and activation invariants |
| `tests/unit/services/billing/subscription-sync.service.test.ts` | Malformed-response preservation, explicit-null behavior and failure classification |
| `tests/unit/services/billing/hosted-plan-change.service.test.ts` | Fence and classified failure regression |
| `tests/unit/services/billing/billing-period-projection.test.ts` | Exact replay without update; real snapshot/counter repair still writes |
| `tests/unit/services/billing/shopify-billing-operation.service.test.ts` | One guarded confirmation and unchanged conflict/identity behavior |
| `tests/unit/services/billing/subscription-ended-notification.service.test.ts` | Real Shared output for caught best-effort errors, preserving current missing-identity behavior |
| `tests/unit/services/billing-reconciliation.service.test.ts` | Original enqueue exception/cause and logging isolation |
| `tests/unit/services/billing.service.test.ts` | Facade argument changes and removal of the wrong SQL expectation |
| `tests/unit/routes/billing-callback.test.ts` | Full callback branch/failure ownership and milestone ordering |
| `tests/unit/routes/onboarding-resume.test.ts` | Existing response/generation gates and original failure evidence |

### New files

| Path | Purpose |
|---|---|
| `app/services/billing/providers/shopify-billing-diagnostics.server.ts` | Shopify billing-specific failure type, safe provider-error extraction and Shared semantic emission; no generic logger/serializer |
| `app/services/billing/onboarding-milestone.server.ts` | One existing two-row atomic milestone command used by callback and resume, with an injectable Prisma transaction owner |
| `tests/unit/services/billing/provider-diagnostics.test.ts` | Actual Shared JSON output, safe cause/source fields, redaction/truncation and sink-failure assertions |
| `tests/integration/billing-activation.postgres.integration.test.ts` | Migrated PG17 initial activation, replay, rollback and controlled concurrent locking cases |
| `tests/helpers/billing-postgres.ts` | Test-only disposable `pgvector/pgvector:pg17` lifecycle, canonical forward migration deployment, separate clients and cleanup |
| `tests/fixtures/billing-activation.ts` | Minimal valid Free/Paid, settings, policy, period and counter fixtures; no production seed changes |

New test/helper files must each stay below 300 lines. Existing large test files need only the bounded changes above. Do not add a package script or dependency: the exact existing `npm test -- <files>` commands below discover these suites.

## Out of Scope

No schema/migration/index changes, new lifecycle state, Background implementation, provider charge/refund execution, request cache redesign, new queue/outbox, generic provider framework, pricing policy or entitlement change. This activation task leaves billing identity generation unchanged. SHOPIFY-012 subsequently owns the user-authorised development-only namespace replacement and new-format vectors/replay; no old-identity compatibility is required by the overall architecture.

Durable subscription-ended notification retry is explicitly deferred: this task preserves its current best-effort policy and makes failures observable. Privacy/retention policy and the separately acknowledged Background Store Category activation hook are also deferred. Do not create tasks, change old task states or edit `_index.md` files.

## Requirements

### R1. Consume trusted context without turning a read cache into admission

Use `getMerchantRequestContext({ request, context })` from SHOPIFY-001 in callback/resume. Preserve SDK redirects, active-Shop checks and each route's existing authorization. Its `readSubscription()` is a scalar presentation read, not a locked decision. Subscription synchronization and finalization continue to obtain current rows inside their existing transaction.

The shared milestone command remains one transaction that updates `commerce.Shop.onboardingCompleted=true` and then `shopify.ShopSettings.onboardingCompleted=true`, requires exactly one existing row for each, and rolls back both on an invariant failure. It never writes false. Preserve the callback's current verified-selection-before-milestone and milestone-before-prepare sequence. Preserve resume's ACTIVATED/ALREADY_ACTIVE and expected-generation gates. Category activation still happens after the billing transaction commits; its failure never reverses that commit.

### R2. One lifecycle lock order

Replace `lockInitialFreeActivationState` and the late paid-Shop lock with `lockSubscriptionLifecycleRows(transaction, shopId)` in `subscription-locks.ts`. It locks existing rows in this exact order using parameterized SQL:

1. `commerce.Shop` by `id`;
2. `shopify.ShopSettings` by `shopId`;
3. `billing.Subscription` by `shopId`.

Every activation prepare/complete/retry, synchronization and hosted-return/failure transaction that currently calls the initial-Free lock helper calls this function before its authoritative reread. `finalizeInitialPaidActivation` runs only with that already-locked transaction; remove its second Shop lock rather than acquiring Shop after Subscription. The locked Shop row serializes the initial missing-Subscription case. Retain all existing missing-settings, token, tenant, status, plan, meter, cycle and balance predicates.

This order matches the existing Background initial-activation/reinstall boundary, inspected as read-only source, and the milestone's Shop-before-settings writes. Do not edit Background or copy its implementation. If the integrated prerequisite changes a participating writer to an incompatible order, stop for an architect amendment instead of inventing another lock or weakening serialization.

### R3. Explicit absence is the only no-contract response

Both `getActiveSubscription` and `getSubscriptionLifecycleSnapshot` consume one validated active-subscription parser in the existing provider module. Parse input as `unknown`. Reject a non-object/array envelope, missing/non-object `data`, missing own `activeSubscription`, invalid field/container types and invalid non-null timestamps. Only an explicit `data.activeSubscription: null`, with no provider errors, denotes absence. Lifecycle reads additionally retain their events/subject/shop checks.

Preserve the selected GraphQL fields and existing `ProviderSubscription` shape. Require one current flat-rate plan and at most one pending flat-rate plan as today. Preserve legitimate nullable cycle/trial/pending fields and existing missing-cycle discovery/unsupported-Paid-trial behavior; do not require a cycle merely to parse a valid provider response. Downstream plan/meter/allowance/cycle policy remains where it is now. Do not change credential freshness: each actual provider operation still resolves the configured credential.

Missing/malformed success evidence throws a typed billing provider failure before any no-contract persistence. Its diagnostic is internally generated validation evidence, never a fabricated provider message. HTTP, GraphQL, JSON parsing, transport and credential/configuration errors retain their actual original error/cause. A callback whose first verification succeeds but whose subsequent Free replay verification is malformed must leave the prior plan/provider/cycle projection intact.

### R4. Original diagnostics and truthful classification

The new diagnostics module owns only Shopify billing provider semantics. Export a `ShopifyBillingProviderError` that preserves `cause` and identifies `failureKind` (`HTTP`, `GRAPHQL`, `TRANSPORT`, `MALFORMED_RESPONSE`, or `CONFIGURATION`), the actual origin and whether its source diagnostic was already emitted. No global registry or generic error envelope is allowed.

Extract the actual safe provider error code/message/details and request ID before Shared emission. HTTP-200 GraphQL `errors[]` and non-2xx JSON/non-JSON error responses both need source diagnostics. Bound the retained error excerpt to 2 KiB and the extracted GraphQL error list to five entries; set truncation/redaction flags. Never log GraphQL `data`, complete bodies, credentials, signed URLs, customer/payment fields or arbitrary response headers. Unsafe portions become `[REDACTED]`; do not replace a safe originating message with an invented explanation. Let Shared own final serialization, record bounds and sink isolation.

The callback's scheduling functions receive `BillingVerificationFailure = { code: "PARTNER_API_ERROR" | "SUBSCRIPTION_SYNC_FAILED"; occurredAt: Date } | null`. Use `PARTNER_API_ERROR` for actual provider/transport/malformed-provider verification failures; local database/configuration/invariant failures use `SUBSCRIPTION_SYNC_FAILED`. Thread this explicit argument through the two existing facade/scheduling methods, replacing the ambiguous `partnerErrorAt` input. Do not label a missing relation or local Prisma error as a Partner outage. Retain bounded scheduling and current token/fence predicates.

At non-provider boundaries emit the original safe `error`, available cause entries and actual Prisma code through Shared. A rethrow-only caller relies on the documented owner; a fallback cannot silently discard a failure. Do not expose server diagnostics in merchant JSON or introduce new visible copy.

### R5. Remove two definite repeated writes

For a confirmed hosted plan switch, `ensureOperation` already calls `confirmOperation`. Return that result directly from `recordHostedPlanChange`; do not confirm a second time. Keep the one confirmation update/reread, fingerprint checks, provider-reference conflicts and ambiguity checks.

In `ensureMappedCurrentBillingPeriodProjection`, update the existing period only if its already-computed repair predicate is true; otherwise use the existing row. Independently retain missing included-counter creation and all mismatch checks. Unchanged replay must preserve period `updatedAt` and balances. Do not remove synchronization timestamps or legitimate period/counter repair writes.

### Required failure matrix

| Injection / owner | Required diagnostic | Required behavior |
|---|---|---|
| Provider HTTP/GraphQL failure, provider adapter | Original safe upstream marker/code, status/request ID, explicit source origin and redaction/truncation | One source log; propagate typed failure; no no-contract mutation |
| Transport/JSON exception, provider adapter | Actual exception name/message/cause; no invented provider error fields | Preserve cause; no projection clearing |
| Missing/wrong success fields, provider adapter | Internal malformed-response reason and safe field path, without response payload | Throw; valid explicit null still follows existing NO_CONTRACT rules |
| Credential/configuration read failure | Original exception/cause and actual database code when present, truthful origin | No Partner-outage misclassification; no request with missing credentials |
| Activation/fence/period persistence fails, owning service or route fallback | Original Prisma message/code/cause, Shop and operation/stage | Roll back transaction; preserve prior projection; existing retry policy remains bounded |
| Synchronization returns local configuration SYNC_ERROR | Actual local reason/identities, without fabricated upstream exception | Retain current state/result semantics |
| Retry scheduling or milestone persistence fails, route boundary | Original scheduling/milestone failure, distinct from the prior failure | Do not report successful persistence or swallow a failed invariant |
| Category activation fails after commit, callback/resume boundary | Original error/cause and activation stage | Billing commit remains durable; current callback failure/resume gate remains |
| Ended-notice persistence/translation dispatch fails, notification service | Actual source exception/cause and lifecycle identity | Preserve existing best-effort continuation and special missing-identity propagation; no durability claim |
| Reconciliation enqueue fails, existing queue adapter | Actual Redis/queue exception/cause, safe subscription/schedule IDs | Preserve queue-after-commit and existing best-effort outcome |
| Shared sink throws, each owned failure path | Real Shared isolation test | No changed redirect, rollback, retry, projection or notification policy |

## Work Items

- [x] Consume the accepted request context and extract the unchanged two-row milestone command.
- [x] Replace the incorrect/split row locks with the chosen order across the named participants.
- [x] Share strict provider parsing and implement bounded original-error diagnostics.
- [x] Thread truthful retry classification and add focused coverage for provider/local fallback classification.
- [x] Remove only the duplicate operation confirmation and unchanged period update.
- [x] Add focused unit/log fixtures and migrated PostgreSQL evidence.

## Interfaces / Contracts

Consumes SHOPIFY-001's server-only `MerchantRequestContext`, with scalar Shop/Subscription/ShopSettings facts. It does not widen that context or its authorization meaning.

New internal contracts:

```ts
lockSubscriptionLifecycleRows(tx: Prisma.TransactionClient, shopId: string): Promise<void>;

persistShopifyOnboardingMilestone(
  shopId: string,
  database?: Pick<PrismaClient, "$transaction">,
): Promise<void>;

type BillingVerificationFailure = {
  code: "PARTNER_API_ERROR" | "SUBSCRIPTION_SYNC_FAILED";
  occurredAt: Date;
} | null;
```

Provider failure type/extraction is owned here and consumed by SHOPIFY-003/004 for classification and diagnostic ownership. `BillingProvider`, provider/current-plan DTOs, subscription statuses, queue payloads and persisted request/hash identities remain compatible. Tests use the exact installed Shared logger export, not sibling Shared source.

The test helper exports `startBillingPostgresFixture()` returning a migrated database URI, a real Prisma client, a factory for additional real clients and idempotent task-owned cleanup. It always creates its own container; it does not accept a production URL or use `db push`. SHOPIFY-003 reuses it.

## Dependencies

- ARCH-057-SHOPIFY-001 — Complete and architect-accepted before claim; provides the trusted request-context contract and integrated route baseline.

## Enables

- ARCH-057-SHOPIFY-003
- ARCH-057-SHOPIFY-004
- ARCH-057-SHOPIFY-011

## Acceptance Criteria

- [x] Initial Paid activation succeeds against the canonical migrated schema, with one exact period, included counter and lifetime counter.
- [x] Lifecycle locking is asserted in Shop, settings, Subscription order; obsolete late reacquisition and wrong `shopify.Shop` locking were removed.
- [x] Controlled concurrent milestone/activation and same-token activation preserve bounded completion, one period/counter grant and stale-token fencing.
- [x] Malformed Free replay evidence is rejected before projection writes; the callback preserves the prior projection path. Explicit null and missing-cycle provider behavior remain covered.
- [x] Each applicable failure-matrix case has an actual Shared output assertion at its owning boundary, preserving safe original message/code/cause and correlation, excluding injected secrets/PII/raw provider bodies and duplicate source diagnostics, with sink-failure behavior checked at provider, service and route owners.
- [x] Database/local failures classify as `SUBSCRIPTION_SYNC_FAILED`, not as an assumed Partner outage.
- [x] Exact billing-period replay performs no period update; missing-counter repair still works; hosted confirmation occurs once.
- [x] Onboarding remains monotonic, category publication remains after billing commit, and notification best-effort policy is unchanged.
- [x] No schema, package, public DTO, locale, queue identity or existing billing hash-preimage changes occurred.

## Validation

Run from the prepared `moda-interact` implementation worktree, following the mandatory contract's Node bootstrap and provenance rules.

- [x] `npm run prisma:generate`
- [x] `npm test -- tests/unit/services/shopify-billing.provider.test.ts tests/unit/services/billing/provider-diagnostics.test.ts tests/unit/services/billing/subscription-activation.service.test.ts tests/unit/services/billing/subscription-sync.service.test.ts tests/unit/services/billing/hosted-plan-change.service.test.ts tests/unit/services/billing/billing-period-projection.test.ts tests/unit/services/billing/shopify-billing-operation.service.test.ts tests/unit/services/billing/subscription-ended-notification.service.test.ts tests/unit/services/billing-reconciliation.service.test.ts tests/unit/services/billing.service.test.ts tests/unit/routes/billing-callback.test.ts tests/unit/routes/onboarding-resume.test.ts`
- [x] `MODA_DISPOSABLE_INTEGRATION=1 npm test -- tests/integration/billing-activation.postgres.integration.test.ts` (passed with Colima `DOCKER_HOST` and `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock`; 2 tests passed against disposable PG17 after canonical migrations).
- [x] `npm run typecheck`
- [x] `npm run build`
- [x] `npx --no-install eslint app/services/billing app/routes/app/billing/callback/route.tsx app/routes/app/onboarding/resume/route.ts tests/unit/services/billing/provider-diagnostics.test.ts tests/integration/billing-activation.postgres.integration.test.ts tests/helpers/billing-postgres.ts tests/fixtures/billing-activation.ts` and focused ESLint of changed existing tests.
- [x] `git diff --check`

The PostgreSQL suite must execute, not skip: deploy all accepted forward migrations to `pgvector/pgvector:pg17`; use real separate connections and explicit barriers around completed statements/provider responses. Exercise initial Paid activation, duplicate/stale tokens, a milestone transaction concurrent with activation, failed second milestone update rollback, unchanged period replay and missing-counter repair. Capture emitted SQL and affected rows. A provider test port may be synthetic; database locks/results may not be mocked. Do not use sleeps as concurrency proof.

For the reviewed Free replay branch, inject a valid first provider verification and malformed second verification and prove the current persisted contract survives. Retain the existing callback ordering regression. Record one-confirmation/no-period-update counts separately from mandatory locks/transaction-control SQL. Record actual Shared JSON/log-sink assertions and container cleanup in the Completion Report.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation are satisfied, set this task to review, return its Completion Report to `moda_architect` and stop. Do not mark it Complete or start SHOPIFY-003.

Stop for an architect amendment if the accepted context contract is absent, a participating writer requires another repository change, the actual provider response contract needs new fields/API behavior, safe diagnostics require a missing Shared export, a schema/identity change appears necessary, or required PostgreSQL validation cannot execute. Preserve unavailable validation as unchecked/blocked; do not weaken the gate.

## Implementation Notes

This task chooses Shop-first locking because the concurrent milestone and existing Background activation/reinstall writers already use it. A missing Subscription row alone cannot serialize first creation; the existing Shop is the stable scope lock. Extra synchronization solely to reduce a measured method count is not authorized.

Keep provider acquisition outside write transactions. Reuse existing parser code rather than retaining two versions. The new diagnostics file is a thin provider-specific semantic boundary, not a reusable generic error system. Runtime filenames, symbols, environment variables and events use domain names; tests may refer to historical decisions. Notification durability and category/milestone policy remain separate decisions.

## Completion Report

### Status

Ready for Review. Attempt 3 implements all three mandatory corrections from the latest Changes Requested review and reruns the required focused unit, disposable PostgreSQL, lint, typecheck, build and diff validations. No architect acceptance decision is made here.

### Files Changed

Implementation repository files changed in Attempt 3:

- `app/services/billing/providers/shopify-billing-diagnostics.server.ts`
- `app/services/billing/providers/shopify-billing.provider.ts`
- `tests/integration/billing-activation.postgres.integration.test.ts`
- `tests/unit/services/billing/provider-diagnostics.test.ts`
- `tests/unit/services/shopify-billing.provider.test.ts`

No schema, dependency, package, public DTO, locale, queue identity or billing hash-preimage changed. No other implementation repository was modified.

### Work Completed

- **Review finding 1, implemented:** timestamp-aware sanitization now preserves only timestamp characters from a phone-like match and redacts the adjacent phone span. `tests/unit/services/billing/provider-diagnostics.test.ts` captures actual installed Shared JSON and asserts the schedule timestamp remains while `+447700900123` is absent and `redactionApplied` is true. Existing callback schedule timestamp correlation assertions remain covered by the focused route suite.
- **Review finding 2, implemented:** JSON parser failures keep the original native `SyntaxError` as the propagated provider error's `cause`; emitted `causeChain` uses a separate sanitized `SyntaxError` with safe invalid-JSON reason and position/line/column metadata when supplied by the runtime. `tests/unit/services/shopify-billing.provider.test.ts` exercises the real parser and installed Shared console output for short complete and long partial synthetic sentinels, verifies no sentinel excerpt reaches the record, confirms the thrown cause remains a `SyntaxError`, and confirms no provider error fields are fabricated.
- **Review finding 3, implemented:** the PG test service factory accepts a provider port and no longer replaces it. Both same-token services are created with the barrier provider; the test waits for and asserts two arrivals before releasing either request. The independent-client PostgreSQL result assertions still prove one activation, one period, one included counter, one lifetime counter and stale-token rejection. The distinct milestone lock-wait/rollback test is unchanged and remains in the suite.

Failure-matrix evidence, using actual Shared output captured from the installed logger:

| Failure-matrix row | Owning output assertion and behavior evidence |
|---|---|
| Provider HTTP/GraphQL | `tests/unit/services/shopify-billing.provider.test.ts`: HTTP status/request ID/code and GraphQL code/request ID/original message; injected token/email/customer detail absent; one source record. |
| Transport, body-read, JSON and malformed success | `tests/unit/services/shopify-billing.provider.test.ts`: exception/cause or safe malformed reason/path; short and long JSON sentinel bodies are exercised through the real parser and Shared output; the original thrown SyntaxError is preserved while emitted cause text contains no response excerpt; no fabricated provider fields or raw invalid body; malformed success does not enter no-contract persistence. |
| Credential/configuration | `tests/unit/services/shopify-billing.provider.test.ts`: original P2025/cause, truthful database origin, no provider fields or fetch; sink failure preserves typed rejection. |
| Activation, fence, hosted return and period persistence | `tests/unit/routes/billing-callback.test.ts` asserts fence read, hosted-return persistence, activation prepare/finalize, hosted and initial retry persistence, and milestone owner records; `tests/unit/services/billing/subscription-sync.service.test.ts` asserts P2034/cause and transaction rollback for period persistence. Sink failures retain throws and do not advance activation/retry. |
| Local synchronization fallback | `tests/unit/services/billing/subscription-sync.service.test.ts`: local reason and plan correlation without fabricated provider errors; result semantics remain `SYNC_ERROR` under sink failure. |
| Retry scheduling and milestone | `tests/unit/routes/billing-callback.test.ts` covers both retry-persistence boundaries and ensures a prior provider error is not copied into the persistence record; callback and `tests/unit/routes/onboarding-resume.test.ts` assert milestone P2025/cause and no false success. |
| Post-commit category activation | Callback and resume tests assert original error/cause, stage, Shop/generation context, and failure after the subscription activation call; sink failure preserves the route throw/gates. |
| Ended-notice persistence and dispatch | `tests/unit/services/billing/subscription-ended-notification.service.test.ts` asserts separate stage/origin records, lifecycle identity, actual cause/code, redaction, best-effort completion and Shared sink isolation; existing missing-identity propagation remains covered. |
| Reconciliation queue acquisition and add | `tests/unit/services/billing-reconciliation.service.test.ts` asserts distinct stages, original queue error/cause, Shop/subscription/schedule correlation, timestamp retention, redaction and best-effort resolution; sink failure on add does not change queue outcome. |
| Shared sink failure | Actual installed Shared logger console sink throws in provider, sync, callback, resume, ended-notice and reconciliation owner tests; each existing throw, response, rollback, retry or best-effort policy remains intact. |

Attempt 3 correction-to-test map:

| Review correction | Durable regression evidence |
|---|---|
| Phone redaction adjacent to timestamp | `tests/unit/services/billing/provider-diagnostics.test.ts`: real Shared JSON output retains `2026-11-04T06:00:00.000Z`, redacts the adjacent phone, and marks redaction; callback scheduling timestamp assertions remain in `tests/unit/routes/billing-callback.test.ts`. |
| JSON parser excerpt privacy | `tests/unit/services/shopify-billing.provider.test.ts`: actual `getActiveSubscription` parser with short and long sentinels; actual Shared output has a sanitized SyntaxError cause chain and no complete/truncated sentinel; propagated error retains the original SyntaxError cause. |
| Same-token concurrency barrier | `tests/integration/billing-activation.postgres.integration.test.ts`: separate real Prisma clients/services, two barrier arrivals asserted before release, PostgreSQL period/counter/stale-token outcomes verified; separate milestone lock-wait and rollback case retained. |

### Validation Results

- `npm test -- tests/unit/services/shopify-billing.provider.test.ts tests/unit/services/billing/provider-diagnostics.test.ts tests/unit/services/billing/subscription-activation.service.test.ts tests/unit/services/billing/subscription-sync.service.test.ts tests/unit/services/billing/hosted-plan-change.service.test.ts tests/unit/services/billing/billing-period-projection.test.ts tests/unit/services/billing/shopify-billing-operation.service.test.ts tests/unit/services/billing/subscription-ended-notification.service.test.ts tests/unit/services/billing-reconciliation.service.test.ts tests/unit/services/billing.service.test.ts tests/unit/routes/billing-callback.test.ts tests/unit/routes/onboarding-resume.test.ts` — passed, 12 files / 395 tests.
- `DOCKER_HOST="${DOCKER_HOST:-unix://$HOME/.colima/default/docker.sock}" TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock MODA_DISPOSABLE_INTEGRATION=1 npm test -- tests/integration/billing-activation.postgres.integration.test.ts` — executed and passed, 2 tests against disposable PG17 after canonical migrations. The same-token provider barrier recorded two arrivals before release; real PostgreSQL results verified one period/counter grant and stale-token rejection. The separate milestone lock-wait and rollback case passed; fixture cleanup completed.
- `npm run typecheck` — passed.
- `npm run build` — passed and ran `npm run prisma:generate` (Prisma Client 6.19.3). Existing dependency annotation, unresolved browser Prisma import, empty route chunk, and large client chunk warnings were emitted; no build error occurred.
- `npx --no-install eslint app/services/billing/providers/shopify-billing-diagnostics.server.ts app/services/billing/providers/shopify-billing.provider.ts tests/unit/services/billing/provider-diagnostics.test.ts tests/unit/services/shopify-billing.provider.test.ts tests/integration/billing-activation.postgres.integration.test.ts` — passed.
- `git diff --check` — passed.
- Focused owner retests passed, including the final exact 12-file command; actual Shared output, safe causes/codes, redaction, timestamp correlation, deduplication and sink isolation are mapped above.

### Deviations

Colima requires the Docker socket and in-container socket override for the disposable PostgreSQL suite; the required integration executed successfully with those settings. Build emitted existing Zod/Rollup annotation, empty-route-chunk and large-client-chunk warnings but completed successfully. No production scope or dependency was changed.

### Assumptions

The launcher verifies the dependency's accepted integrated source before claim; fixture providers do not contact live Shopify.

### Unresolved Issues

No failure-matrix evidence gap remains identified for this bounded task. Notification durability and the Background category hook remain explicitly deferred by the task. SHOPIFY-003, SHOPIFY-004 and SHOPIFY-011 remain pending architect review and downstream sequencing.

### Physical Worktree and Synchronization Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-057-SHOPIFY-002`, branch `task/ARCH-057-SHOPIFY-002`; prepared synchronized base `e5202616ea84bd44df95c18a576fd72e847cf3b8`; launcher claim commit `ecee03fa921dd3ad6f082600e73cd27c7b40ba8c` is pushed on `origin/task/ARCH-057-SHOPIFY-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-057-SHOPIFY-002`, branch `task/ARCH-057-SHOPIFY-002`; Attempt 3 starting SHA `f26d91209a4c177a8adeb9fd7bf875cb9c7a9577`, implementation commit `8561a870a8a5a407dca8b9da7f6239c69a140c90` pushed to `origin/task/ARCH-057-SHOPIFY-002`.
- Parent and implementation task branches were reused by the prepared launcher; mainline was already incorporated. No branch synchronization, claim or submodule preparation was repeated by this attempt.
- Recursive implementation submodule sync and initialization passed in launcher preparation. The `database` submodule is initialized at the recorded gitlink `8e74634ff92be9900f693c0c449ffce888e7d617`; recursive status was ready and this task did not change the gitlink.
- Shared/default checkouts were not used for implementation, no other task worktree was reused, and no submodule gitlink was changed.

### Architectural Concerns

Return changes to ownership, lifecycle policy, schema, error contracts, lock participants or persisted/provider identity to the architect.

## Architect Review

### Review Status

**Accepted — Attempt 3, 2026-11-04.** All three Attempt 2 findings are resolved. No remaining blocking finding was identified in the scoped review. Under this task's automatic completion mode, status is `complete`, the claim is cleared, and Attempt remains 3. The implementing agent's Completion Report remains its submission evidence; this section is the architect acceptance decision.

### Findings Resolved

1. Timestamp-aware redaction now preserves only timestamp characters within a numeric match and redacts adjacent phone spans. The real Shared regression retains the schedule timestamp, excludes the synthetic phone and asserts the redaction flag. Existing route timestamp-correlation tests pass.
2. The provider retains the original native JSON SyntaxError as the propagated cause while supplying a separate safe diagnostic cause. Logs retain exception type and bounded parser position/reason information without the response excerpt. Short and long invalid-response regressions exercise the real parser and installed Shared output; transport and other original-cause paths remain covered.
3. The PostgreSQL service factory accepts the provider port without overwriting it. Both independent clients reach the shared barrier, the test asserts two arrivals before release, and real persistence assertions establish one activation/period/counter grant plus stale-token rejection. The separate milestone lock-wait and second-write rollback case remains intact.

### Reviewed Source and Validation

- Implementation: `8561a870a8a5a407dca8b9da7f6239c69a140c90`; five-file corrective delta from `f26d91209a4c177a8adeb9fd7bf875cb9c7a9577`. Parent submission: `24b1f81ca50162486ff4e856b97a93c6edc1b057`.
- Independently reran the exact required 12-file unit command: **395/395 passed**, no skips. Log: `/tmp/arch057-shopify002-attempt3-review-units.log`.
- Independently reran the disposable PG17 suite: final isolated run **2/2 passed**, no skips, including same-token concurrency and milestone/rollback. Canonical migrations and the fixture cleanup hook executed. Log: `/tmp/arch057-shopify002-attempt3-review-postgres-rerun.log`.
- Preserve the first review PostgreSQL result: **1 passed, 1 failed**, plus an unhandled teardown error. The milestone case hit an expired interactive transaction while other review checks were running; the same-token case passed. The unchanged suite passed when rerun alone after those checks finished. This does not establish the timeout's root cause. Initial log: `/tmp/arch057-shopify002-attempt3-review-postgres.log`.
- Independent `npm run typecheck`, production build (including Prisma Client 6.19.3 generation), changed-file ESLint and `git diff --check` passed. Logs: `/tmp/arch057-shopify002-attempt3-review-typecheck.log`, `/tmp/arch057-shopify002-attempt3-review-build.log`, `/tmp/arch057-shopify002-attempt3-review-lint.log`. Existing build warnings are not represented as errors.
- The implementation worktree remained clean after review. No implementation, package, schema or gitlink changes were made by the architect. Earlier review evidence is preserved below rather than overwritten.

### Architecture Conformance and Dependencies

The correction preserves provider exception propagation, explicit-null parsing policy, original lifecycle locks/fences, milestone ordering and current notification/retry behavior. The previously reviewed owner-level diagnostic matrix remains covered by the passing focused suites. This acceptance makes no general performance, deadlock-freedom or production-rollout claim.

SHOPIFY-001 is complete. SHOPIFY-003's only prerequisite is now complete, so it is promoted from `pending` to `ready`, unclaimed at Attempt 0. SHOPIFY-004 remains pending on SHOPIFY-003; SHOPIFY-011 retains its remaining incomplete prerequisites. No downstream task was executed or claimed. No `_index.md` or implementation gitlink was changed.

The developer explicitly authorized committing and pushing the acceptance, dependency and architecture handoff updates on the parent task branch on 2026-11-04.

### Previous Review — Attempt 2

### Review Status

Changes Requested — Attempt 2, reviewed 2026-11-04. Returned to `ready`, with `executor` and `claimed_at` cleared; Attempt remains 2. This decision supersedes the submitted Completion Report's review-readiness claim. No architect acceptance or downstream promotion is made.

### Findings

1. **[P2] Timestamp preservation bypasses phone redaction.** In `app/services/billing/providers/shopify-billing-diagnostics.server.ts:94–96`, a numeric match is preserved in full whenever any part overlaps an ISO timestamp. The phone matcher spans spaces and hyphens, so the synthetic message `failed for +447700900123 2026-11-04T06:00:00.000Z` retains the entire phone number in actual installed Shared output, with `redactionApplied: false`. Preserve only timestamp spans and redact adjacent phone text. Add real Shared output coverage for adjacent phone/timestamp values while retaining the schedule-correlation assertion.
2. **[P2] Native JSON parsing errors disclose response text through the cause.** `app/services/billing/providers/shopify-billing.provider.ts:265–278` correctly preserves the original SyntaxError as the thrown error's cause, but the diagnostic emitter also logs its message, including the body excerpt generated by Node. A synthetic HTTP-200 body `SECRETXYZ` appears verbatim in `causeChain[0].message` as `Unexpected token 'S', "SECRETXYZ" is not valid JSON`. The existing longer-body test only checks that the complete marker is absent and misses a truncated excerpt. Keep the original cause on the propagated error, but remove response-derived spans from emitted parse diagnostics; retain safe exception identity and position/reason metadata. Test both short complete-body and long partial-body excerpts using the real parser and real Shared output.
3. **[P2] The same-token concurrency barrier is overwritten before use.** `tests/integration/billing-activation.postgres.integration.test.ts:118–128` installs a two-reader provider barrier, but each subsequent `billingServiceFor(...)` call replaces `provider.getActiveSubscription` with an immediate resolver at line 77. The test can pass as sequential fresh/stale token processing without executing the declared barrier. Construct the clients/services before installing the barrier or inject independent provider ports; assert both calls reach the barrier before release, then verify the existing one-period/counter and stale-token outcomes against real PostgreSQL. Keep the separate milestone lock-wait test intact.

### Validation Reviewed

- Reviewed implementation `f26d91209a4c177a8adeb9fd7bf875cb9c7a9577` and parent submission `8524666ae70a5e29d63b662103293c35466719d3`, including Attempt 2's 12-file delta and the provider/diagnostic/real-PostgreSQL paths relevant to these findings.
- Independently reran the exact required 12-file unit command: **393/393 passed**. Local log: `/tmp/arch057-shopify002-review-units.log`.
- Two additional temporary regression probes using Node 24.19.0 and the installed Shared 3.1.0 logger **both failed**, reproducing findings 1 and 2. Log: `/tmp/arch057-shopify002-review-probes.log`. Only synthetic sentinels were used. The temporary probe was removed and the implementation worktree remains clean.
- Finding 3 is a source-level test setup defect, not a claim of a production locking failure. The reported 2/2 PostgreSQL result is retained as historical execution evidence, but does not establish the overwritten same-token barrier. PostgreSQL, build, typecheck and lint were not independently rerun in this review; their submission results remain as reported above.
- Recorded/working Database pin is `8e74634ff92be9900f693c0c449ffce888e7d617`. No implementation, dependency, schema, package or gitlink changes were retained by this review.

### Follow-up and Dependencies

Correct all three findings within the existing allowlist, rerun the mandatory focused unit and disposable PostgreSQL suites plus the task's applicable gates, and update the evidence map. Recheck the two acceptance criteria only after the privacy probes and controlled same-token case pass. Preserve original exception propagation, current lifecycle/rollback semantics, and safe timestamp correlation.

SHOPIFY-003, SHOPIFY-004 and SHOPIFY-011 were checked and remain `pending`; they are not eligible for promotion because SHOPIFY-002 is not accepted. No downstream task was started. The developer explicitly authorized committing and pushing this review overlay on the parent task branch on 2026-11-04.

### Previous Review — Attempt 1

### Review Status

Changes Requested.

### Review Notes

Attempt 1 is not acceptable yet because one explicit acceptance criterion remains unchecked. The task requires an actual Shared output assertion for every row in the Required failure matrix. `provider-diagnostics.test.ts` currently demonstrates representative provider diagnostics, local Prisma/cause logging, classification and sink isolation, while the Completion Report explicitly confirms that it does not assert every owning boundary. This leaves the diagnostic ownership and privacy contract unverified at the callback/resume, retry scheduling, category-activation fallback, ended-notice and reconciliation-queue boundaries as applicable.

### Reviewed Files

- All implementation paths in `moda-interact` commit `54c021b`.
- `app/services/billing/providers/shopify-billing-diagnostics.server.ts` and `app/services/billing/providers/shopify-billing.provider.ts`.
- Failure owners in the callback/resume routes, activation/sync/hosted-plan services, milestone, ended-notification and reconciliation services.
- `tests/unit/services/billing/provider-diagnostics.test.ts` and relevant provider, route, service and PostgreSQL test suites.
- Attempt 1 Completion Report and recorded validation evidence.

### Validation Reviewed

Reviewed the reported passing evidence: 368 focused unit tests plus a 45-test callback/sync follow-up, 2 PostgreSQL integration tests, Prisma generation, typecheck, build, focused ESLint and diff checks. The report confirms that actual Shared JSON assertions do not yet cover every required matrix row. Tests were not rerun during this review.

### Architecture Conformance

The provider parser, lock order, transaction fences, replay behavior and representative diagnostic paths conform to the reviewed task contracts. Full diagnostic-matrix conformance is not demonstrated because the required per-owner Shared output assertions are incomplete.

### Follow-up

For Attempt 2, complete the unchecked acceptance criterion. Add actual Shared logger JSON output assertions for each Required failure matrix row at its owning boundary, including provider HTTP/GraphQL/transport/malformed response, credential/configuration and local database failures, activation/fence and period persistence, synchronization fallback, retry scheduling and milestone persistence, post-commit category activation, ended-notice persistence/translation, reconciliation enqueue failure, and Shared sink isolation. For each case assert the actual original safe message/cause/code and source/stage/shop/operation correlation required by that row, the truthful origin/classification, absence of injected credentials/PII/raw provider data, and absence of duplicate source diagnostics where one owner already emitted them. Preserve the existing behavior and retry/rollback assertions. If a row is structurally inapplicable to this task's implementation, document the concrete call path and retained owner assertion instead of marking it covered by a generic utility test. Rerun the focused suites that cover the changed tests and update the report with a row-by-row evidence map. Keep SHOPIFY-003, -004 and -011 pending until acceptance.
