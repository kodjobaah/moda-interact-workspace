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
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-11-04T05:06:11Z
attempt: 1
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

Mandatory execution, diagnostic, provenance and validation contract: `docs/architecture/ARCH-057/task-contract.md`. This is a **portable definition, defined but not materialised**. It has no execution claim, branch, worktree, commit or accepted implementation. Its dependency is not Complete, so its status is Pending.

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

- [ ] Consume the accepted request context and extract the unchanged two-row milestone command.
- [ ] Replace the incorrect/split row locks with the chosen order across the named participants.
- [ ] Share strict provider parsing and implement bounded original-error diagnostics.
- [ ] Thread truthful retry classification and cover every matrix fallback.
- [ ] Remove only the duplicate operation confirmation and unchanged period update.
- [ ] Add focused unit/log fixtures and required migrated PostgreSQL evidence.

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

- [ ] Initial Paid activation succeeds against the canonical migrated schema, with one exact period, included counter and lifetime counter.
- [ ] Every named lifecycle transaction locks Shop, settings, then Subscription before its authoritative reread; no `shopify.Shop` reference or late reacquisition remains.
- [ ] Controlled concurrent milestone/activation and same-token activation preserve bounded completion, one grant and stale-token fencing.
- [ ] Malformed success evidence leaves prior subscription/provider/cycle fields unchanged; explicit valid null and valid missing-cycle responses retain accepted behavior.
- [ ] Each failure-matrix case has an actual Shared output assertion preserving safe original message/code/cause where supplied, without injected secrets/PII or duplicate upstream bodies.
- [ ] Database activation failure is never stored/logged as an assumed Partner outage.
- [ ] Exact billing-period replay performs no period update; missing-counter repair still works; hosted confirmation occurs once.
- [ ] Onboarding remains monotonic, category publication remains after billing commit, and notification best-effort policy is unchanged and explicitly documented.
- [ ] No schema, package, public DTO, locale, queue identity or existing billing hash-preimage changes occurred.

## Validation

Run from the prepared `moda-interact` implementation worktree, following the mandatory contract's Node bootstrap and provenance rules.

- [ ] `npm run prisma:generate`
- [ ] `npm test -- tests/unit/services/shopify-billing.provider.test.ts tests/unit/services/billing/provider-diagnostics.test.ts tests/unit/services/billing/subscription-activation.service.test.ts tests/unit/services/billing/subscription-sync.service.test.ts tests/unit/services/billing/hosted-plan-change.service.test.ts tests/unit/services/billing/billing-period-projection.test.ts tests/unit/services/billing/shopify-billing-operation.service.test.ts tests/unit/services/billing/subscription-ended-notification.service.test.ts tests/unit/services/billing-reconciliation.service.test.ts tests/unit/services/billing.service.test.ts tests/unit/routes/billing-callback.test.ts tests/unit/routes/onboarding-resume.test.ts`
- [ ] `MODA_DISPOSABLE_INTEGRATION=1 npm test -- tests/integration/billing-activation.postgres.integration.test.ts`
- [ ] `npm run typecheck`
- [ ] `npm run build`
- [ ] `npx --no-install eslint app/services/billing app/routes/app/billing/callback/route.tsx app/routes/app/onboarding/resume/route.ts tests/unit/services/billing/provider-diagnostics.test.ts tests/integration/billing-activation.postgres.integration.test.ts tests/helpers/billing-postgres.ts tests/fixtures/billing-activation.ts` and focused ESLint of the changed existing tests.
- [ ] `git diff --check`

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

Not Started. Defined but not materialised.

### Files Changed

None. Definition only.

### Work Completed

None.

### Validation Results

Not run. Record actual commands/results, exact source and dependency provenance, PG cases/SQL, emitted Shared-log assertions, warnings and task-owned cleanup.

### Deviations

None.

### Assumptions

The launcher verifies the dependency's accepted integrated source before claim; fixture providers do not contact live Shopify.

### Unresolved Issues

Implementation and required validation remain outstanding. Notice durability and the Background category hook remain explicitly deferred.

### Architectural Concerns

Return changes to ownership, lifecycle policy, schema, error contracts, lock participants or persisted/provider identity to the architect.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition only; no implementation acceptance.

### Reviewed Files

Task definition and the named latest-snapshot touchpoints.

### Validation Reviewed

Definition checks only. Implementation evidence remains outstanding.

### Architecture Conformance

To be assessed against the implemented behavior, source, lock/race evidence and diagnostic output.

### Follow-up

Return for review; do not start enabled work automatically.
