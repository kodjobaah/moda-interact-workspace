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
status: complete
priority: 80
executor: null
claimed_at: null
attempt: 2
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
updated: 2026-11-05
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
| `app/services/merchant-support/merchant-support.service.ts`, `app/services/merchant-knowledge/merchant-knowledge-queue.server.ts` | Attach bounded error listeners to the existing owned producer queues through their semantic adapters |
| `app/services/merchant-support/merchant-support-observability.server.ts`, `app/services/merchant-knowledge/merchant-knowledge-observability.server.ts` | Add narrowly named producer connection-error diagnostic exports as needed, reusing the existing central projection and Shared logger |
| `app/services/billing/providers/shopify-billing-diagnostics.server.ts` | Expose the existing safeText projection for runtime adapter reuse and optionally accept known sensitive values/explicit diagnostic cause in the existing boundary logger; retain one existing projection |
| `tests/unit/merchant-support-service.test.ts`, `tests/unit/merchant-support-observability.test.ts`, `tests/unit/merchant-knowledge-queue.test.ts`, `tests/unit/merchant-knowledge-observability.test.ts`, `tests/unit/services/billing/provider-diagnostics.test.ts` | Existing predecessor queue/emitted-output regression coverage for these narrow changes |
| `app/routes/system/telemetry-probe/route.ts` | Preserve the existing probe request and HTTP/DTO contract while diagnosing network/non-success attempts and projecting target/error safely in logs and response |
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

### Architect scope and installed SDK contract clarification — 2026-11-05

The two producer constructors above currently have no error listener. Authorize a listener for each owned queue instance using the corresponding existing semantic adapter and the actual safe source error/cause/code. Idle connection events have no request-owned diagnostic. Preserve queue identity, data/options, admission, deadlines, retries and best-effort outcomes. Do not add process-level handlers, connection probes, queries for logging or a competing logging transport. Verify the emitted record and unchanged behavior with the existing predecessor queue/observability suites and throwing-sink cases.

The runtime adapter must reuse the existing central safeText and error/cause projection. The existing logBillingBoundaryFailure input may gain only optional diagnosticError (an explicit diagnostic projection of the caught error), sensitiveValues (known strings to remove), and explicit redactionApplied/truncated booleans. Reuse existing safeErrorValue, causeChain and safeText on the selected diagnosticError or original error. Keep original-error ownership/deduplication marking on the original supplied error. These optional inputs support SDK/configuration-parser privacy. Preserve original thrown error/cause identity in application propagation and existing billing behavior when these optional inputs are absent. Any projected diagnostic input must have direct provenance in the actual caught exception. A JSON parser exception may echo plaintext configuration. Preserve the actual SyntaxError as the thrown wrapper cause, while emitting its safely projected name/message/cause with explicit redaction metadata. Omit the sensitive echo rather than copying configuration into logs. Retain safely available source wording and actual diagnostic code. Keep existing bounds and honest redaction/truncation flags. This is a narrow reuse amendment, not authority for another serializer, redaction kernel or generic logger.

Installed Shopify API `LogFunction` is `(severity, msg)` in `dist/ts/lib/base-types.d.ts`. Its `logger/log.mjs` formats message and context before invoking that callback. Requirement 4 therefore means retain supplied severity and the safely projectable supplied formatted text. There is no separate structured context argument to preserve. Wire the supported callback directly. Do not recover guessed structured fields by parsing console output or SDK formatting, and do not emit arbitrary formatted request/session/header/body context. The SDK semantic adapter may omit the entire opaque suffix beginning at the installed formatter delimiter ` | {` and mark redactionApplied. This is one privacy omission of opaque supplied text, not reconstruction of structured fields. Retain the independently safe message prefix and supplied severity through the existing central projection. If the message prefix itself contains opaque request/session/body/JSON content that cannot safely be retained, omit that unsafe content with an explicit privacy-omission classification. Use the existing centralized projection and known sensitive values. If a safely retained source portion cannot be established, omit the unsafe text with an explicit privacy-omission classification and document the concrete SDK capability limitation in the inventory. This explicit privacy omission does not authorize substituting generic labels for safely available source wording. Actual thrown SDK errors retain their original propagation and named diagnostic owner. SDK tests must exercise the installed callback path, source-marker/severity retention for safe messages, sensitive formatted-context omission/redaction and sink isolation. Any operational failure whose required safe evidence remains unavailable is recorded as a blocker before review.

### Architect scope clarification — telemetry probe failure owner, 2026-11-05

The telemetry probe converts fetch exceptions into HTTP 200 NETWORK_ERROR but currently retains only an error-message string and publishes configured target/error text in its information record and response. Authorize the existing runtime semantic adapter to add a narrowly named recordTelemetryProbeFailure export using the existing central projection. Capture the actual caught network error/cause/code before the fallback. For a non-success HTTP response, record the actual numeric status and fixed probe operation/stage as an internally classified failed probe, without inventing a provider exception, message, cause or body. Preserve the existing one-shot fetch, target selection, HTTP 200, no-store, otel/probe nesting, probe keys, status classification and elapsed-time semantics. Keep the normal correlation information record and assign the full technical diagnostic to the named failure owner once.

Response privacy is explicitly within this narrow correction. Preserve target as a string and error as string-or-null, but sanitize their values using the reused central safeText projection and known configured sensitive values. If a safe value cannot be established, use a fixed redacted string. Do not expose target userinfo, signed/query capabilities, credentials, raw configured URL or unsafe exception text in either captured logs or response JSON. Keep the actual target exclusively for the fetch operation. Verify injected credential/signed-target sentinels are absent from both outputs, while the safe source marker/code/cause remains available in the internal failure record. Use the already declared server-error-fallbacks/privacy tests for network, non-success, success and throwing-sink behavior. No new metric/span, remote telemetry setup, authentication policy or bootstrap edit is authorized. observability.mjs remains read-only.

## Work Items

- [x] Inventory and classify all final server failure paths.
- [x] Close the exact remaining entry/bootstrap/configuration/health/pending-work gaps.
- [x] Preserve error causes, truthfully classify failures and retain normal response behaviour.
- [x] Execute source-message, privacy, fallback, event-emitter and sink-isolation cases.
- [x] Record complete coverage and any unresolved prerequisite gap.

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

- [x] Every server inventory row has a valid classification and named diagnostic owner; no unexplained operational swallowing remains.
- [x] Emitted records contain actual safe source messages and available causes/codes/request IDs, including caught fallback and typed-error branches.
- [x] Provider-origin and internally generated failures remain distinguishable; no guessed provider messages.
- [x] SDK/startup/SSR/uncaught handler/dependency/queue-emitter/cleanup cases are covered.
- [x] Raw captured records and evidence contain no injected sensitive sentinel.
- [x] Merchant/browser responses and established status/rollback/retry/best-effort behaviour remain unchanged.
- [x] Throwing-sink tests preserve behaviour; no new logging kernel, query-for-logging or broad catch-and-continue.

## Validation

- [x] `npm run test:server-diagnostics`
- [x] Re-run affected predecessor failure suites only where an owned diagnostic path changed; list exact commands/results
- [x] Run `npm test -- tests/unit/merchant-support-service.test.ts tests/unit/merchant-support-observability.test.ts tests/unit/merchant-knowledge-queue.test.ts tests/unit/merchant-knowledge-observability.test.ts tests/unit/services/billing/provider-diagnostics.test.ts` and scoped ESLint for newly authorized files. Verify idle producer error events, original safe source/cause/code, configuration privacy, optional-input compatibility and throwing-sink behavior.
- [x] `npm run typecheck` and `npm run build` — preserve server-only imports and SDK bootstrap
- [x] Focused ESLint and `git diff --check`
- [x] Coverage inventory references actual emitted JSON records and outcome assertions, not only logger-spy calls

## Stop Condition

Return review only after all rows and mandatory cases are resolved. Any unowned failure path, missing source message, unsafe emission, changed status/transaction semantics or unsupported Shared/SDK capability is a blocker. Do not claim global production observability from local emitted-record tests or change privacy/notification policy.

## Implementation Notes

The user explicitly requires original error messages for pre-production diagnosis. Shared's bounds and safe extraction still apply in development. The goal is complete useful server evidence, not noisy logging of ordinary validation or duplicate full provider records.

## Completion Report

### Status

Ready for Review — Attempt 2, codex, 2026-11-05. Implemented the Attempt 1 P2 correction and published implementation `aa026765831cae76d0acd51f2af86298fcad41ef` on `task/ARCH-057-SHOPIFY-011`. No architect acceptance or downstream promotion is asserted. The prior implementation/report remain in Git at `528ec1c2e53cdd1f00fc8f45141cc77c2d9e5561` / `b736f82fb3163df4a7b029c6a6c56813d54e8740`.

### Prepared Execution / Provenance

- Canonical root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-057-SHOPIFY-011`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-057-SHOPIFY-011`. Both use `task/ARCH-057-SHOPIFY-011`. Shared/default checkouts were not switched or edited; no other task worktree was reused.
- Launcher dependency gate passed: all ten explicit prerequisites Complete. Rework required, previous attempt1. Parent remote task fast-forward not needed, origin/main incorporated; implementation remote task fast-forward not needed, origin/main already current.
- Parent start: `4c6d5f92b2848eec7055c1fa0ce8008172fe8e92`; durable Attempt 2 claim `b5922a0788a1d307665b7b4f0c991336d20c8807`, executor codex, `2026-11-05T10:08:28Z`. Parent end is this report's publication commit (not an invented self-referential SHA).
- Implementation start: `528ec1c2e53cdd1f00fc8f45141cc77c2d9e5561`; end: `aa026765831cae76d0acd51f2af86298fcad41ef`.
- Launcher recursive submodule sync/update passed; nested Database recorded/working pin `bd2d09066a8eb178a56f48fbbf88df637c411059`, unchanged.
- Reused pinned installation from Attempt 1: Shared3.1.0, Prisma6.19.3, Shopify API13.1.0, Shopify React Router1.2.1, React Router7.18.2, BullMQ6.3.1, ioredis6.0.0, pg8.23.0. Prescribed workspace Node bootstrap supplied Node24.19.0/npm11.17.0. Final build generated Prisma from the same pinned Database schema. No dependency or schema change.

### Files Changed

- `app/services/health/health-check.server.ts`: Redis/PostgreSQL source events go directly to the existing semantic diagnostic owner instead of being discarded when a later operation fails.
- `app/services/pending-recovery/pending-recovery-reader.server.ts`: same correction for Redis/BullMQ source events; unavailable projection remains unchanged.
- `tests/unit/server-error-fallbacks.test.ts`:22 added normal/throwing-sink regression cases;196 lines, below300.
- `docs/server-error-coverage.md`: final source anchors rescanned, executed correction matrix and actual emitted JSON evidence added. Inventory remains1,147 source anchors across200 application modules plus read-only preload, with browser/presentation separately classified. Counts are source/propagation anchors, not independent injected incidents.

### Architect Correction Checklist

1. **Implemented — retain distinct source event evidence.** Health Redis, health PostgreSQL and pending Redis/BullMQ listeners emit immediately through their existing source owners. A later generic rejection cannot suppress the original marker/cause/code. No event buffer can overwrite an earlier distinct source error. Regression `retains %s source events before a distinct generic rejection`:8 cases passed (four paths × normal/throwing sink).
2. **Implemented — preserve evidence before timeout.** Existing Redis1500ms and pending2500ms local deadlines remain unchanged. `retains %s source events before the existing local timeout`:6 cases passed. PostgreSQL uses the existing driver deadlines; controlled query timeout `ETIMEDOUT` plus distinct connection source `ECONNREFUSED`:2 cases passed. No new PostgreSQL application timer or driver field is invented.
3. **Implemented — suppress duplicates without losing distinct evidence.** Reuses the existing original-error ownership marker in `logBillingBoundaryFailure`; duplicate delivery and rejection of the same Error instance emit once. PostgreSQL/pending same-instance regression:6 cases passed; existing Redis same-instance regression retained. Different Error objects are not collapsed merely because text matches, since cause/code can differ. No global registry or new serializer/logger.
4. **Implemented — preserve behavior, privacy and evidence.** Added cases capture actual Shared JSON, retain original safe source marker/cause/code, reject sensitive sentinels, assert false/unavailable and cleanup calls, and repeat under a throwing sink. Existing constructor propagation, best-effort/fallback, framework/configuration/SDK and cleanup cases remain passing. Inventory contains actual adjacent source-event and generic-rejection records and names all executed cases/results.

### Validation Results

All required checks passed on this rework:

- `npm run test:server-diagnostics` — **138 tests passed,7 files**, including22 new correction cases. Passing final capture run at10:11 UTC used a temporary sink-copy hook; restored original test bytes afterward. Actual sink JSON was copied before harness assertions/redaction and selected synthetic records are committed in the coverage document.
- `npm test -- tests/unit/merchant-support-service.test.ts tests/unit/merchant-support-observability.test.ts tests/unit/merchant-knowledge-queue.test.ts tests/unit/merchant-knowledge-observability.test.ts tests/unit/services/billing/provider-diagnostics.test.ts tests/unit/services/billing-reconciliation.service.test.ts tests/unit/services/billing/subscription-ended-notification.service.test.ts tests/unit/shopify-taxonomy-suggestion.test.ts tests/unit/routes/onboarding-resume.test.ts` — **73 tests passed,9 files**.
- `npm run typecheck` — passed.
- `npm run build` — passed, final SSR bundle generated; existing non-failing chunk-size advisory remains.
- `./node_modules/.bin/eslint app/services/health/health-check.server.ts app/services/pending-recovery/pending-recovery-reader.server.ts tests/unit/server-error-fallbacks.test.ts` — passed, zero warnings/errors.
- `git diff --check` — passed. Final source inventory rescanned using the installed TypeScript parser.

Local artifacts: `/tmp/arch057-shopify011-attempt2-{tests,predecessors,typecheck,build,lint}.log` and `/tmp/arch057-shopify011-attempt2-emitted.jsonl`. Durable source anchors, case matrix and JSON examples: `docs/server-error-coverage.md`.

No live Redis/PostgreSQL/Shopify/collector operation, new SQL query, concurrency proof or remote delivery/retention claim. Tests use controlled dependency ports and real installed Shared serialization. No task-owned container/database/volume was created. Fake timers/environment/globals were restored, temporary capture edits removed; no Docker pruning. This rework changes only dependency event handling, tests and evidence; no Shopify API/platform operation or SDK configuration was changed.

### Deviations

None beyond the existing architect-authorized scope clarifications from Attempt 1. The P2 correction stays within selected health/pending source and declared tests/evidence.

### Assumptions / Limits

Existing central original-error deduplication remains best effort for frozen errors, as in the accepted predecessor kernel; no new global mechanism. Unchanged predecessor ownership is distinguished from executed local fault cases in the inventory. SDK flattened-text privacy limitations remain documented from Attempt 1; no structured context is reconstructed. Local emitted-record proof is not global production observability proof.

### Unresolved Issues / Architectural Concerns

No remaining task-owned correction or validation blocker. Architect review is pending. No response policy, deadline, cleanup policy, billing/notification durability, schema, transaction, queue admission/retry, main branch, gitlink, index or downstream task was changed. The Architect Review section below is preserved unchanged.

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


## Dependency Reconciliation — Published Acceptance Correction (2026-11-05)

SHOPIFY-004's published task branch contains its architect acceptance at implementation `525194c9598c18f8f736b4d24752bfdf07228720`. Its accepted task record was reconciled from `origin/task/ARCH-057-SHOPIFY-004`; the earlier Review snapshot in this branch was stale. All ten explicit prerequisites, SHOPIFY-001 through SHOPIFY-010, are now Complete. Promoted to Ready, unclaimed, with attempt unchanged at 0. Normal launcher preparation and accepted-source integration checks are required before execution. SHOPIFY-012 and SYSTEM-TEST-001 remain Pending; no downstream implementation is started.

## Architect Review — Attempt 1, 5 November 2026

**Changes Requested.** Reviewed implementation `528ec1c2e53cdd1f00fc8f45141cc77c2d9e5561`. Returned to Ready with executor/claim cleared and Attempt 1 preserved. This supersedes the earlier pending review text; no acceptance or downstream promotion is recorded.

### Finding

**[P2] Distinct connection source errors are discarded when an operation also rejects.** In `app/services/health/health-check.server.ts:80–84`, the error listener saves `observed`, but the finally block emits it only when `failed` is false. The PostgreSQL probe has the same suppression condition. `app/services/pending-recovery/pending-recovery-reader.server.ts:167–171` repeats the pattern for Redis/BullMQ. This assumes the operation's rejection is the same diagnostic as the emitted connection error. If the event contains the actual transport failure/cause/code while the operation rejects with a generic closed-connection error or a local timeout, the original evidence is lost. This violates the task's source-message/cause ownership requirement.

An independent temporary regression invoked the actual Redis health function with a controlled emitter: it emitted an Error containing a synthetic original marker, cause and ECONNREFUSED code, then rejected connect with a distinct `Error("Connection is closed.")`. Readiness remained false, but the actual installed Shared sink captured only the generic closed-connection message, with no original marker, cause or code. The assertion requiring the original marker failed. This is a controlled reproduction, not a claim that a live Redis incident was observed.

Retain distinct source event evidence while suppressing equivalent/duplicate failure reporting. Cover health Redis, health PostgreSQL and pending Redis/BullMQ paths, including event-then-generic-rejection and event-then-timeout where supported. Preserve Boolean/unavailable outcomes, existing deadlines/cleanup, safe redaction and throwing-sink isolation. Do not replace the operation exception, invent provider fields, add process-level handlers or introduce a global deduplication registry. Update the coverage inventory to reflect the executed cases and retain useful source wording/code/cause.

### Independent Validation and Limits

- `npm run test:server-diagnostics`: **116/116 tests passed**, seven files, using the prescribed Node 24.19.0 bootstrap in the dedicated implementation worktree. Local log `/tmp/shopify011-review.log`.
- Additional temporary regression: **failed as described**, one selected test. Local log `/tmp/shopify011-review-probe.log`; the 48 filtered tests are not counted as completed validation. Probe used synthetic data only. Original test file restored byte-for-byte; implementation checkout clean afterward. No probe edit is retained.
- Inspected task requirements/scope amendments and submitted report; runtime/SDK, framework, configuration, health and pending diagnostic changes, central boundary reuse and selected emitted-output tests. Reviewed submitted predecessor/build/typecheck/lint evidence; these gates were not independently rerun in this review.
- No implementation, dependency, schema or gitlink is changed by this review. Parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-057-SHOPIFY-011`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-057-SHOPIFY-011`, matching task branches.

### Handoff

Use normal launcher preparation for the next attempt, correct the finding within this task's existing scope, rerun required diagnostic/predecessor/static checks, publish both task branches and return for review. SHOPIFY-012 and terminal system validation remain gated; neither is promoted or executed. The developer explicitly authorized committing and pushing this review on 5 November 2026.

## Architect Acceptance — Attempt 2, 5 November 2026

**Accepted.** Reviewed correction `aa02676` against prior submission `528ec1c`. No blocking findings remain. Task marked Complete under automatic completion mode; Attempt 2 preserved and executor/claim cleared. Earlier Changes Requested/Ready/pending review text remains historical and is superseded by this acceptance.

### Finding Resolved

Health Redis, health PostgreSQL and pending Redis/BullMQ now emit source events immediately through their existing semantic owners. A later distinct generic rejection or local/driver timeout cannot discard original source wording/cause/code. The existing original-error marker suppresses repeated emission of the same Error instance without a new global registry. The correction preserves existing Boolean/unavailable responses, deadlines and cleanup. Tests cover all four event paths, distinct rejection, local/driver timeout, repeated event/rejection identity, privacy and throwing-sink behavior. The coverage inventory now records these executed cases.

### Independent Validation and Limits

Independently ran `npm run test:server-diagnostics` in the dedicated implementation worktree using the prescribed Node 24.19.0 bootstrap: **138/138 tests passed across seven files**, no skips. This includes the added regression cases for the reproduced Attempt 1 gap. Whitespace check passed; implementation checkout clean. Local independent log `/tmp/shopify011-review-attempt2.log` is not a committed artifact.

Reviewed the submitted **73 predecessor test passes**, typecheck, build and scoped lint results; these were not independently rerun during this review. Source inspection covered the entire correction diff and updated inventory, with the prior broader implementation review retained above. Local emitted-log tests do not establish live Redis behavior, remote collector delivery/retention or global production observability. No Docker/live provider/deployment check is claimed.

### Isolation and Downstream

Reviewed prepared worktree/claim evidence in the report. Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-057-SHOPIFY-011`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-057-SHOPIFY-011`, matching task branches. No implementation, schema, dependency, gitlink or main branch is changed by this review.

SHOPIFY-012's sole explicit prerequisite is now Complete. Promoted to Ready, unclaimed, at Attempt 0. SYSTEM-TEST-001 remains Pending on SHOPIFY-012; no downstream task is executed. ARCH-057 is not marked implemented.

The developer explicitly authorized updating acceptance/dependencies, committing and pushing on 5 November 2026.
