---
id: ARCH-057-SHOPIFY-011
architecture_id: ARCH-057
title: Complete server diagnostic coverage with original failure messages
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-057-SHOPIFY-001
- ARCH-057-SHOPIFY-002
- ARCH-057-SHOPIFY-003
- ARCH-057-SHOPIFY-004
- ARCH-057-SHOPIFY-005
- ARCH-057-SHOPIFY-006
- ARCH-057-SHOPIFY-007
- ARCH-057-SHOPIFY-008
- ARCH-057-SHOPIFY-009
- ARCH-057-SHOPIFY-010
enables:
- ARCH-057-SHOPIFY-012
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-057-SHOPIFY-011: Complete server diagnostic coverage with original failure messages

## Architecture

Architecture ID: `ARCH-057`. Document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`. Coordinator: `moda_architect`.

Mandatory contract: `docs/architecture/ARCH-057/task-contract.md`. **Defined but not materialised.**

## Objective

Ensure every Shopify server operational failure has a tested Shared-log owner that retains its original safe message, cause and available diagnostic details.

## Context

F16 includes suppressed exceptions, error-type-only logs and operational failures converted into ordinary absence/denial. Earlier touchpoint tasks own their changed errors. This terminal application task closes the remaining entry/bootstrap/configuration/health/pending-work boundaries and reconciles all server catch/error-event paths. It does not redesign their business policy.

## Scope

Paths relative to `moda-interact`.

### Existing files to modify

| Path | Selected change |
|---|---|
| `app/entry.server.jsx` | Shared diagnostics in SSR callbacks; export framework `handleError` for uncaught loader/action failures; preserve statuses/stream abort/rethrow |
| `app/shopify.server.js` | Route SDK logger output and bootstrap exceptions through a safe Shared semantic adapter; keep auth/token/storage settings |
| `app/services/platform-configuration/contracts.server.ts` | Optional actual Error cause on the existing configuration error; same public codes |
| `app/services/platform-configuration/repository.server.ts` | Preserve original Prisma error as cause on DATABASE_UNAVAILABLE |
| `app/services/platform-configuration/seal.server.ts` | Preserve actual decode/unseal cause; never expose sealed/keyring values |
| `app/services/platform-configuration/service.server.ts` | Emit original safe cause/code at the owning failed-read/unseal boundary, including keyring failures |
| `app/services/health/health-check.server.ts` | Log failed dependency attempts/cleanup with original message/code while preserving Boolean response and deadlines |
| `app/services/pending-recovery/pending-recovery-reader.server.ts` | Diagnose Redis/BullMQ read/error-event/cleanup failures; retain bounded unavailable projection |
| `app/services/billing/subscription-ended-notification.service.ts` | Log failed persistence/dispatch by stage; preserve currently accepted best-effort notification semantics |
| `app/services/billing/billing-reconciliation.service.ts` | Verify/correct message/cause logging for failed postcommit scheduling |
| `app/services/discounts/shopify-discount-lifecycle.service.ts` | Replace remaining console-only dispatch diagnostic; preserve committed lifecycle result |
| `app/services/store-profile/shopify-taxonomy-suggestion.server.ts` | Preserve and log actual provider/transport/parser failures before fallback |
| `app/routes/app/onboarding/resume/route.ts` | Log caught activation/category technical failures; retain milestone/redirect semantics |
| `app/services/webhooks/shopify-webhook-observability.server.ts` | Reconcile remaining auth/route failure-message gaps from all six handlers without changing admission |
| `tests/unit/platform-configuration/service.test.ts` | Real emitted error/cause/privacy assertions and unchanged error codes |
| `tests/unit/platform-configuration/shopify-oauth-bootstrap.test.ts` | Missing/revoked/malformed configuration fails closed and logs safe original cause |
| `tests/unit/pending-recovery-reader.test.ts` | Read, emitter and cleanup diagnostics with no status change |
| `tests/unit/health/health-check.server.test.ts` | Probe failure/cause and safe Boolean/timeout behaviour |
| `package.json` | Add the exact diagnostic test command below |

The coverage inventory reads all server routes/services, provider adapters, queue constructors and framework callbacks. Corrections outside this write list are returned to their prior task owner or require an explicit scope amendment; no broad unreviewed app rewrite.

### New files

- `app/services/observability/shopify-runtime-observability.server.ts` — only semantic entry/SSR/startup/SDK failure events using Shared.
- `tests/unit/server-error-boundaries.test.ts` — actual Shared records at framework/SSR/startup surfaces.
- `tests/unit/server-error-fallbacks.test.ts` — remaining best-effort/typed result/cleanup boundaries and cause retention.
- `tests/unit/server-error-privacy.test.ts` — provider/SDK/DB sentinel and throwing-sink assertions.
- `docs/server-error-coverage.md` — complete catch/error-event/uncaught-boundary inventory and case evidence.

## Out of Scope

No competing logging kernel or new log sink, remote Loki access/retention setup, process-level “keep running” uncaught-exception handler, global error de-duplication registry, altered public error DTO, new reconciliation worker, durable notification-policy change or privacy erasure/export implementation. No client telemetry collector or raw provider output in merchant UI.

## Requirements

1. Re-scan the actual final accepted source for `catch`, promise rejection handlers, error events, provider non-success/GraphQL error returns, typed unavailable results, framework callbacks and detached async operations. Inventory **every server path**, including paths without a catch whose error propagates to an owner. Categorize browser-only presentation parsing separately.
2. Each inventory row has exact file/symbol, failure origin, existing outcome, owning emitted event or propagation boundary, required safe message/cause/code fields, associated test/case and result. Classifications are: operational failure logged, propagated to named logged owner, expected business/input control flow, logger/telemetry-internal isolation, or blocker. No unexplained blank/ignored row is permitted.
3. Add framework `handleError` and SSR callback diagnostics through the new **semantic** adapter. Keep original propagation/status/stream behaviour. Recognized redirects and expected 4xx Responses are not operational exceptions. Do not log arbitrary Response bodies or request URL queries.
4. Configure the existing Shopify SDK logging callback using the installed SDK signature. Retain original safe SDK message text, supplied severity and context. Domain-sanitize provider text before Shared; no debug dump of headers/session/request/response. Preserve actual SDK errors where thrown. If installed callback cannot safely expose the required details, return a concrete dependency/contract gap; do not parse console text or install a parallel logger.
5. Configuration wrappers accept/preserve their actual cause. Preserve explicit missing/disabled/invalid-configuration outcomes without fabricated upstream fields. Database/unseal/keyring failure records retain safe actual message and available database code/cause. Bootstrap failure must still prevent serving authenticated traffic.
6. Health probes retain current bounded dependency checks, Boolean HTTP DTO and cleanup. Log the original failed attempt once; a corresponding Redis error event is not an excuse to log nothing or duplicate the same failure. Missing configuration has no fabricated provider error. Failed cleanup is diagnosed without replacing the primary failure.
7. Pending work, subscription-ended notification and reconciliation keep their established degraded/postcommit behaviour, but emit original technical failures and stage/correlation. The notification durability decision remains deferred; do not claim a failed notice will automatically retry.
8. Log full original diagnostic evidence once at its owning boundary. Existing domain adapters own provider extraction; entry handling can add context without duplicating unsafe bodies. Shared serializes Error name/message only. The owner explicitly supplies available safe cause/code fields as the common contract requires; a downstream context record need not repeat the complete diagnostic payload.
9. Every selected technical failure preserves source wording except explicit security redaction/truncation. Expected invalid cursor/form/optional locale parsing is documented control flow, not a mandatory error-level log. All unexpected dependency/read/write/queue/provider failures remain diagnosable, including those converted into success/fallback.
10. Capture actual Shared output before harness redaction. No secret/PII/signed capability appears in it. A throwing Shared sink cannot change the business result or hide a real exception behind another exception.

## Work Items

- [ ] Inventory and classify all final server failure paths.
- [ ] Close the exact remaining entry/bootstrap/configuration/health/pending-work gaps.
- [ ] Preserve error causes, truthfully classify failures and retain normal response behaviour.
- [ ] Execute source-message, privacy, fallback, event-emitter and sink-isolation cases.
- [ ] Record complete coverage and any unresolved prerequisite gap.

## Interfaces / Contracts

New semantic adapter exports only `recordUnhandledRequestFailure`, `recordServerRenderFailure`, `recordShopifyBootstrapFailure` and `recordShopifySdkDiagnostic`. Inputs are explicitly bounded safe fields for those operations, not arbitrary request/session objects. Use Shared `createLogger`/`sanitizeLogFields` and the existing environment resolver; no local generic serializer/redactor.

Existing `ShopifyPlatformConfigurationError` gains only optional original `cause`. Public `key`/`code` and existing API/UI decisions remain unchanged. No new Shared version/schema is required.

Package script:

```json
{
  "test:server-diagnostics": "vitest run tests/unit/server-error-boundaries.test.ts tests/unit/server-error-fallbacks.test.ts tests/unit/server-error-privacy.test.ts tests/unit/platform-configuration/service.test.ts tests/unit/platform-configuration/shopify-oauth-bootstrap.test.ts tests/unit/pending-recovery-reader.test.ts tests/unit/health/health-check.server.test.ts"
}
```

## Dependencies

ARCH-057-SHOPIFY-001 through ARCH-057-SHOPIFY-010, each explicitly listed in frontmatter. They must be accepted/integrated so this task audits the final behaviour.

## Enables

- ARCH-057-SHOPIFY-012

## Acceptance Criteria

- [ ] Every server inventory row has a valid classification and named diagnostic owner; no unexplained operational swallowing remains.
- [ ] Emitted records contain actual safe source messages and available causes/codes/request IDs, including caught fallback and typed-error branches.
- [ ] Provider-origin and internally generated failures remain distinguishable; no guessed provider messages.
- [ ] SDK/startup/SSR/uncaught handler/dependency/queue-emitter/cleanup cases are covered.
- [ ] Raw captured records and evidence contain no injected sensitive sentinel.
- [ ] Merchant/browser responses and established status/rollback/retry/best-effort behaviour remain unchanged.
- [ ] Throwing-sink tests preserve behaviour; no new logging kernel, query-for-logging or broad catch-and-continue.

## Validation

- [ ] `npm run test:server-diagnostics`
- [ ] Re-run affected predecessor failure suites only where an owned diagnostic path changed; list exact commands/results
- [ ] `npm run typecheck` and `npm run build` — preserve server-only imports and SDK bootstrap
- [ ] Focused ESLint and `git diff --check`
- [ ] Coverage inventory references actual emitted JSON records and outcome assertions, not only logger-spy calls

## Stop Condition

Return review only after all rows and mandatory cases are resolved. Any unowned failure path, missing source message, unsafe emission, changed status/transaction semantics or unsupported Shared/SDK capability is a blocker. Do not claim global production observability from local emitted-record tests or change privacy/notification policy.

## Implementation Notes

The user explicitly requires original error messages for pre-production diagnosis. Shared's bounds and safe extraction still apply in development. The goal is complete useful server evidence, not noisy logging of ordinary validation or duplicate full provider records.

## Completion Report

### Status

Not Started. Defined but not materialised; no execution claim or worktree is asserted.

### Files Changed

None. Definition only.

### Work Completed

None.

### Validation Results

Not run. Record exact commands, fixture/case results, source/build/installed-package provenance, original diagnostic assertions, SQL/provider counts where required, and task-owned resource cleanup.

### Deviations

None.

### Assumptions

The launcher will verify actual dependency status and the accepted integrated source before claiming this task.

### Unresolved Issues

Implementation and required validation are outstanding.

### Architectural Concerns

Return changed ownership, persisted identity, schema, queue, transaction or external contract requirements to the architect.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition only; no implementation accepted.

### Reviewed Files

Definition and current snapshot touchpoints only.

### Validation Reviewed

Definition checks only. Implementation evidence is outstanding.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

Return the completed task for architect review; do not start enabled tasks.


## Dependency Reconciliation — 2026-11-04

ARCH-057-SHOPIFY-009 Attempt 2 is architect-accepted and Complete. This task remains Pending: SHOPIFY-010 is Ready but incomplete, and SHOPIFY-004 is still recorded in Review in this branch. No claim or downstream execution is authorized by this update; the normal launcher must check current dependency records and integration before execution.


## Dependency Reconciliation — 2026-11-05

SHOPIFY-010 Attempt 1 is architect-accepted and Complete at `6e8029deb30de8903e937dc092b68f8b304e4dce`. This task remains Pending: SHOPIFY-004 is still recorded in Review in this branch. All other explicit prerequisites are Complete. This note supersedes the earlier frontier note naming SHOPIFY-010 as incomplete; no claim or execution is started.
