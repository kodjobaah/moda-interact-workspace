---
id: ARCH-046-BACKGROUND-005
architecture_id: ARCH-046
title: Extract shared recovery consent merchant notification service
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 30
executor: developer
claimed_at: 2026-10-25T01:10:01Z
attempt: 2
depends_on:
  - ARCH-045-BACKGROUND-002
enables:
  - ARCH-046-BACKGROUND-002
created: 2026-10-24
updated: 2026-10-25
---

# Extract shared recovery consent merchant notification service

## Architecture

Architecture ID: `ARCH-046`.

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`.

Coordinator: `moda_architect`.

**Lifecycle:** portable architect task definition; **defined but not materialised** in the developer's Git workspace. No implementation branch, worktree, commit or push has been created by this task definition.

**Rollout classification:** **pre-production / breaking change permitted.** The developer confirmed on 2026-10-24 that previously sent development Support notices require **no backward compatibility, old-key recognition, backfill, dual-write or migration**. Use one canonical notice identity for all new Shopify/WooCommerce notices. Do not destroy existing development data or schema as part of this task.

## Objective

Extract the accepted Shopify recovery-consent merchant notice writer into **one platform-neutral Background business service** that Shopify uses immediately and that the pending Woo consent-admission adapter can call without duplicating formatting, deduplication, Support persistence or logging. Keep **consent decisions and checkout-context lookup in platform-specific callers**.

## Context

- `ARCH-045-BACKGROUND-002` is **Complete**. Its current implementation uses `src/services/checkout-recovery/recovery-consent-notice.service.ts` and `recovery-consent-admission.service.ts`. The writer transactionally `upsert`s `MerchantSupportThread`, `createMany(..., skipDuplicates: true)` for a `SYSTEM` message and updates `lastMessageAt` only on insertion. Today its body, `systemCode` and hash recipe are hardcoded for Shopify; it presents an opaque digest instead of useful merchant context.
- `ARCH-048-BACKGROUND-003` already defines `WooRecoveryAdmissionService` with an **awaited** `onDeniedAdmission({ shopId, checkoutToken, reason })` callback. `ARCH-046-BACKGROUND-002` will provide the Woo adapter after this shared service is accepted. That callback is invoked for **all** admission-denial reasons: Woo must filter genuine notice-worthy consent/recipient reasons rather than publish on empty basket, ineligible shop, ordinary terminal state or customer STOP.
- `MerchantSupportThread` is uniquely keyed by `shopId`. `MerchantSupportMessage.sourceKey` is unique and the message has existing `kind`, `state`, `originalBody`, `sourceLanguageTag`, `systemCode`, `systemVersion` and `availableAt` fields. **No new table is needed.** Shopify and Woo merchants already consume these same Support records.
- The shared implementation must **not** invoke Shopify's native consent API, Woo customer consent reader, BullMQ, WhatsApp/Meta, billing or recovery creation.

## Scope

1. Introduce the **Background-local** canonical `RecoveryConsentMerchantNotifier` interface and `RecoveryConsentNoticeInput`/result types (contract below). The concrete class is `RecoveryConsentMerchantNoticeService`. These are not `Port` interfaces and do not require a `moda-interact-shared` publication.
2. Extract the transactional Support notice writer and one plain-text merchant message formatter from `recovery-consent-notice.service.ts`. Use one system code and one deduplication recipe across platforms. Rename/replace the old service as appropriate; **no compatibility wrapper** for its old Shopify key/type is required during development.
3. Migrate **the existing Shopify consumer** in `recovery-consent-admission.service.ts` to the new `notify` contract. Keep Shopify-native permission evaluation, no-contact/STOP suppression, retry semantics and pre-insert denial intact. Its existing native decision mapping becomes a **thin Shopify adapter**. When an existing Shopify checkout-context projection is available at this seam, pass safe bounded context; otherwise omit fields rather than adding provider calls or inventing data.
4. Implement bounded, understandable merchant-facing copy that states the checkout/customer information **available and verified for that shop**, the exact category of block, and the outcome. The hash remains **internal** for deduplication, not the sole content of the merchant notice. Never claim a customer refused consent when identity is ambiguous or verification is unavailable.
5. Add contract tests proving a simulated Woo invocation uses **the same** formatter and persistence behaviour. The actual Woo `onDeniedAdmission` binding and Woo-specific context enrichment belong to `ARCH-046-BACKGROUND-002`, **not this task**.
6. Use the published `@modainteract/moda-interact-shared/logging` implementation already configured in Background, with safe structured events. Database, formatter and domain-dependency failures must **propagate**; never catch an exception and return `duplicate`, `denied`, or success. Shared logger **sink** failures remain isolated from business execution by the approved logging library.

### Source ownership / expected changes

- **Primary owned file (suggested):** `moda-interact-background/src/services/checkout-recovery/recovery-consent-merchant-notice.service.ts` (canonical interface may be colocated here or in an adjacent small domain-local contract module).
- **Replace/retire:** `moda-interact-background/src/services/checkout-recovery/recovery-consent-notice.service.ts`; avoid leaving a second active writer.
- **Shopify adapter:** `moda-interact-background/src/services/checkout-recovery/recovery-consent-admission.service.ts`.
- **Tests:** `tests/unit/services/checkout-recovery/recovery-consent-notice.service.test.ts`, `recovery-consent-admission.service.test.ts`, and a focused integration test for transactional Support persistence/deduplication where the repository's test database is available.
- Changes to the **assigned task definition** and its Completion Report are allowed in the normal task workflow. Do not change Shopify/WooCommerce apps, API, database schema, the Woo admission implementation, or any `docs/decisions/**/_index.md`.

## Out of Scope

- Implementing or wiring `ARCH-046-BACKGROUND-002`'s Woo denial callback, Woo checkout/customer lookup, new BullMQ workers, provider-state verification, WhatsApp sends or credit usage.
- Refactoring unrelated merchant Support notifications, STOP notification writers, translation services, merchant UI or any other architecture initiative.
- New Support tables/columns, migrations, data backfills, compatibility aliases or attempts to match previously sent development notifications.
- New Shared package exports or duplicate generic logger/formatter infrastructure.
- Treating a denied consent decision as a provider/DB exception, or synthesising a notice on every ordinary ineligible checkout.

## Requirements

- [x] **Single writer:** exactly one reusable Support writer for this recovery-consent notice family, consumed by Shopify now and callable by Woo through the same public TypeScript interface.
- [x] **Tenant safety:** all persisted messages belong to the `MerchantSupportThread` for the validated input `shopId`; the caller may attach customer context only after resolving it for that exact shop and checkout. No cross-shop lookup, context fallback or deduplication collision.
- [x] **Pre-production identity:** one deterministic canonical `sourceKey` for new notices, independent of old `shopify-recovery-consent:v1` keys. There is no legacy migration/backfill/dual-write requirement.
- [x] **Truthful outcome:** support both refusal to **create the first recovery** and a blocked **initial-send re-entry** without falsely claiming that no recovery row exists. Do not notify for customer STOP through this service; `ARCH-045-BACKGROUND-005` owns that notice.
- [x] **Readable body:** use short labelled plain-text lines. Include customer name/email, checkout total/currency, item count, last received activity and safe merchant-visible reference **only if individually available, validated and permitted**. Missing fields are omitted; do not invent names, totals, dates, order numbers, links or customer identifiers.
- [x] **Content safety:** never put raw checkout tokens, phone numbers, credentials or an untrusted URL into `sourceKey` or logs. Do not place them in the notice body; a merchant-visible reference must be a vetted non-secret identifier, not a session/cart token. Escape/control/remove line breaks in individual context fields; cap field and overall body lengths. Do not render untrusted HTML or Markdown links.
- [x] **Consent reasons:** distinguish confirmed absent marketing opt-in, unverified identity, ambiguous identity, and technical verification unavailability. The latter is **unknown**, not refusal, and must preserve the caller's bounded retry policy.
- [x] **No new side effects:** `notify()` may only insert a Support SYSTEM notice and update its thread metadata. Never create `CheckoutRecovery`, attempt, reservation, outbound job or WhatsApp send.
- [x] **Errors:** the service awaits the database transaction and propagates unexpected business errors after safe structured diagnostics; callers must not silently swallow these errors. Shared logger sink failures must not break correct business processing. `duplicate` is only returned for an actual sourceKey uniqueness conflict handled by the existing `skipDuplicates` pattern.

## Work Items

- [x] Read the complete accepted Shopify task/implementation and its focused unit tests, plus `docs/observability/shared-logging.md`, before changing the source.
- [x] Define the canonical contract and its validation/bounds; document exactly which fields are caller-supplied optional context.
- [x] Implement the shared formatter and new deterministic `sourceKey` construction. No old Shopify id/hash compatibility or migration.
- [x] Extract one transactional Support persistence implementation (`thread.upsert` → `message.createMany(skipDuplicates)` → conditional `thread.update`) with injected DB, clock and shared logger for tests.
- [x] Migrate Shopify `RecoveryConsentAdmissionService` to `RecoveryConsentMerchantNotifier.notify`, retaining confirmed no-opt-in, missing identity, STOP skip, technical unavailability/retry, first admission and DETECTED re-entry semantics.
- [x] Remove/repoint old direct writer usage, avoiding a second active implementation; verify no remaining runtime consumers of the old type/path.
- [x] Add unit and integration tests for both platform values, reason mapping, readable optional context, idempotency, tenant isolation, concurrency, rollback, safe logging and exception propagation.
- [x] Fill in the Completion Report, mark only verified checkboxes, set task to `review`, and stop for architect review.

## Interfaces / Contracts

**Canonical Background-local contract.** Implement these exact exported names and basic shapes; any required change must be returned to `moda_architect` **before** dependent implementation rather than independently changing Woo/Shopify adapters.

```ts
export type RecoveryConsentNoticePlatform = "SHOPIFY" | "WOOCOMMERCE";

export type RecoveryConsentNoticeReason =
  | "NO_VERIFIED_OPT_IN"
  | "RECIPIENT_UNVERIFIED"
  | "RECIPIENT_AMBIGUOUS"
  | "VERIFICATION_UNAVAILABLE";
export type RecoveryConsentBlockedOperation =
  | "CREATE_FIRST_RECOVERY"
  | "SEND_INITIAL_RECOVERY";

export type RecoveryConsentCheckoutContext = Readonly<{
  customerName?: string;
  customerEmail?: string;
  checkoutTotal?: Readonly<{ amountDecimal: string; currency: string }>;
  itemCount?: number;
  lastActivityAt?: string; // ISO-8601 with offset, label as last received activity
  merchantVisibleReference?: string; // verified non-secret reference only
}>;

export type RecoveryConsentNoticeInput = Readonly<{
  shopId: string;
  platform: RecoveryConsentNoticePlatform;
  checkoutToken: string; // internal only: NEVER display/log as raw text
  reason: RecoveryConsentNoticeReason;
  blockedOperation: RecoveryConsentBlockedOperation;
  context?: RecoveryConsentCheckoutContext;
}>;

export type RecoveryConsentNoticeResult = "created" | "duplicate";
export interface RecoveryConsentMerchantNotifier {
  notify(input: RecoveryConsentNoticeInput): Promise<RecoveryConsentNoticeResult>;
}
```

**Identifier and persistence invariants:**

- Construct `digest = sha256(JSON.stringify(["recovery-consent", 1, platform, shopId, checkoutToken, reason]))` in that **exact element order**, encoded as lowercase hex. Use `sourceKey = "recovery-consent:v1:" + digest`. Each `(platform, shop, checkout, reason)` produces **one** notice. `blockedOperation` is deliberately *not* part of the key, avoiding repeat notices if the same checkout/reason is later observed at another entrypoint. The first successfully committed message remains authoritative and is **not rewritten** on duplicates.
- Use `MerchantSupportMessage.kind = SYSTEM`, `state = AVAILABLE`, `systemCode = "RECOVERY_CONSENT_ADMISSION"`, `systemVersion = "1"`, `sourceLanguageTag = "en-GB"`, `availableAt = now()`, and a bounded plain-text `originalBody`.
- Within **one PostgreSQL transaction**, upsert the thread by `shopId`, insert with `createMany({ skipDuplicates: true })`, and update `lastMessageAt` only if `count === 1`. Return `created` iff `count === 1`; `duplicate` iff `count === 0` for a verified duplicate. Fail/throw on unexpected database or cardinality outcomes. No Redis, network, provider, translation request or logging sink operation inside the transaction.
- Render a single canonical heading (e.g. **Checkout recovery could not proceed**), labelled optional customer/checkout fields, a precise reason and an operation-specific outcome. `CREATE_FIRST_RECOVERY` may say no recovery was created; `SEND_INITIAL_RECOVERY` must say only that initial outreach was not sent/charged. Do not confuse these two states.
- `VERIFICATION_UNAVAILABLE` must explicitly say the customer's preference is **unknown**, not refused. Any retry/defer decision is owned by the adapter/orchestrator, not the notifier.
- Input context is prepared by an authenticated **platform-specific adapter**. The notifier formats/persists it; it does not query Customer, Woo/Shopify providers or checkout sessions. Shopify's native permission evaluation and Woo's stored CustomerPhone consent remain separate.
- Caller-specific mappings: Shopify maps its existing `NATIVE_CONSENT_NOT_GRANTED`, missing/ambiguous recipient and `UNAVAILABLE` outcomes to the normalized reason; a local STOP yields **no** call. Woo BG-002 will map `CONSENT_NOT_GRANTED` → `NO_VERIFIED_OPT_IN`, `CONSENT_AMBIGUOUS` → `RECIPIENT_AMBIGUOUS`, missing/unverified recipient → `RECIPIENT_UNVERIFIED`, and **will not** call this notifier for unrelated order/installation/basket failures or `CONSENT_NO_CONTACT` STOP.

**Dependency injection:** the concrete service must implement `RecoveryConsentMerchantNotifier`; accept an injectable transaction-capable Prisma client, clock and `StructuredLogger` (or approved process child logger) without creating another generic logger. Shopify injects the interface rather than referencing the concrete class. The Woo task consumes the same interface; it must not copy its SQL, sourceKey generation or formatter.

## Dependencies

- `ARCH-045-BACKGROUND-002` — architect/developer-completed Shopify pre-insert consent notice implementation to extract. This task does **not** depend on unfinished Woo recovery orchestration.

## Enables

- `ARCH-046-BACKGROUND-002` — Woo-specific denial mapping, safe context enrichment and hookup to the common notifier.

## Acceptance Criteria

- [x] Exactly one active common writer and formatter exists; Shopify and a synthetic Woo adapter call the **identical** `notify` implementation and create equivalent `SYSTEM` Support messages.
- [x] Fresh Shopify denial still creates **no** recovery, attempt, outbound message, conversation or credit; confirmed STOP still avoids a duplicate missing-consent notice; a verified Shopify grant produces no notice.
- [x] Both platform values produce different keys for the same checkout/reason; different shops, checkouts or reasons also yield distinct keys; duplicate/retried/concurrent calls for the same identity insert at most one message.
- [x] The persisted sourceKey/body and structured logs never contain raw checkout token, telephone number, provider credentials, untrusted URLs or injected control characters. Safe optional merchant-facing identifying details are present where supplied, omitted where absent.
- [x] A technical-unavailable notice never asserts customer refusal. A `SEND_INITIAL_RECOVERY` notice never asserts that the recovery record was not created. No bogus data enrichment or full customer lookup in the shared service.
- [x] A failed message insert, thread update, transaction or formatting dependency never turns into a benign `duplicate`/`denied` result; unexpected **business** exceptions propagate to the caller. A shared logger sink outage is isolated and does not roll back successful business processing.
- [x] All new notices use the approved **new** canonical key/code. No code path attempts legacy `shopify-recovery-consent:v1` recognition, compatibility backfill or migration. Existing development rows are not deleted or rewritten by this task.
- [x] No production runtime worker wiring, Woo admission service implementation, extra persistence or cross-repo code is changed.

## Validation

- [x] Focused unit tests: formatter and field bounds; platform-specific truthfulness; Shopify adapter decision mapping, local STOP exclusion and unavailable-provider retry; simulated Woo invocation; sourceKey determinism and collision isolation.
- [x] Concurrency and persistence tests: replay and parallel duplicate calls, one `lastMessageAt` update on insert, no update on duplicate, transaction rollback on insert/update failure, retry visibility after failed transaction.
- [x] Fault injection: DB timeout/Prisma errors, notifier dependency failure and unexpected reason/context; assert business errors are diagnosed safely and rethrown (never silently swallowed). Simulate a shared logging sink failure separately and verify normal notice processing continues.
- [x] Focused existing Shopify consent-admission and notice regression tests pass, including the initial pre-INSERT and DETECTED re-entry flows; no changed consent policy. Use exact repository package scripts/runner after inspecting `package.json`.
- [x] Run the repository's relevant TypeScript typecheck/lint and `git diff --check`; report baseline failures with precise evidence, never pass off unrelated preexisting failures as successful task validation.
- [x] Inspect test logs for leaked checkout/customer information and verify no unexpected duplicate active writer remains.

## Stop Condition

After completing only the specified extraction, Shopify migration and focused validation, update the task's work-item/validation checkboxes and Completion Report; set `status: review`, return to `moda_architect`, and **STOP**. Do not implement the Woo adapter, run ARCH-048-BG-005 integration, update domain indexes or begin follow-on tasks.

## Implementation Notes

- The canonical task must be materialised in the **launcher-resolved parent** `task/ARCH-046-BACKGROUND-005` worktree; the implementation runs in the separate `moda-interact-background` worktree on its matching `task/ARCH-046-BACKGROUND-005` branch. Use `/moda-task` preparation and record physical worktree isolation, synchronization and submodule evidence. Do not infer worktree location from another task's checkout.
- Keep business logic in one independently testable Background service. Do not put notice formatting, hashing or persistence inside worker callbacks, Shopify consent policy or Woo admission callbacks.
- Prefer a small renderer/helper and single transaction. Reuse Shared logging via `@modainteract/moda-interact-shared/logging`; redact unexpected error diagnostics. No raw event/provider payload logging. Await and propagate failures; only deliberate business denials are normal outcomes.
- The merchant-facing notice is a **Support** message, not a WhatsApp message. Use existing Support translation/rendering functionality. Multiline plain text should be readable in Woo's existing UI; Shopify presentation changes (if desired) belong to its owning app, **not** this extraction.
- **Development reset permitted, destructive operations not authorised:** no legacy notice compatibility code and no migration of old development messages, but never delete existing Support data as a side-effect of this task or its tests outside isolated test fixtures.
- If a genuinely missing cross-repository contract, schema change, or additional product behaviour is found, stop and report the dependency gap to `moda_architect`, rather than broadening this service-extraction task.
- Do **not** modify `docs/decisions/**/_index.md` until the architect session is explicitly complete.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-25T01:10:01Z. Attempt 1 review history is preserved below.

### Files Changed

Implementation repository: `moda-interact-background`.

- `src/services/checkout-recovery/recovery-consent-admission.service.ts` — Shopify adapter.
- `src/services/checkout-recovery/recovery-consent-merchant-notice.contracts.ts` — new local contract.
- `src/services/checkout-recovery/recovery-consent-merchant-notice.formatter.ts` — canonical body and key.
- `src/services/checkout-recovery/recovery-consent-merchant-notice.service.ts` — single Support writer.
- `src/services/checkout-recovery/recovery-consent-notice.service.ts` — removed legacy writer.
- `src/services/checkout-recovery/recovery-initiation.service.ts` — context forwarding.
- `tests/integration/recovery-consent-merchant-notice.integration.test.ts` — new PostgreSQL integration tests.
- `tests/unit/services/checkout-recovery/recovery-consent-admission.service.test.ts`.
- `tests/unit/services/checkout-recovery/recovery-consent-checkout-reconciliation.test.ts`.
- `tests/unit/services/checkout-recovery/recovery-consent-merchant-notice.formatter.test.ts` — new fixture.
- `tests/unit/services/checkout-recovery/recovery-consent-merchant-notice.service.test.ts` — new fixture.
- `tests/unit/services/checkout-recovery/recovery-consent-notice.service.test.ts` — removed old fixture.
- `tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`.

**Post-review correction in implementation commit `8c6f034` (four files):**

- `src/services/checkout-recovery/recovery-consent-merchant-notice.formatter.ts`.
- `tests/unit/services/checkout-recovery/recovery-consent-merchant-notice.formatter.test.ts`.
- `tests/unit/services/checkout-recovery/recovery-consent-merchant-notice.service.test.ts`.
- `tests/integration/recovery-consent-merchant-notice.integration.test.ts`.

### Work Completed

- Added the common `RecoveryConsentMerchantNotifier` contract, formatter and
  canonical `recovery-consent:v1` SHA-256 source-key construction for both platforms.
- Replaced the Shopify-only writer with one transaction-backed, shop-scoped
  Support `SYSTEM` notice implementation; migrated the Shopify admission consumer.
- Preserved distinct `CREATE_FIRST_RECOVERY` versus `SEND_INITIAL_RECOVERY`
  outcomes, explicit consent/recipient reasons and STOP exclusion.
- Added optional, bounded merchant-visible checkout context and safe logging.
- Added unit coverage and disposable PostgreSQL integration coverage, including
  independent concurrent clients, canonical duplicate verification, timestamp
  monotonicity and rollback.
- Corrected the deterministic digest fixture; replaced the racy Support-thread
  `upsert` with `createMany({ skipDuplicates: true })` followed by
  `findUniqueOrThrow` within the existing transaction after the PostgreSQL
  concurrency test exposed a uniqueness race.
- Verified that the integration, build and lint checks completed on the
  implementation task worktree and pushed the corrected implementation branch.
- **Changes Requested correction, published in `8c6f034`:** the canonical
  notice `sourceKey` now hashes exactly the six fields
  `JSON.stringify(["recovery-consent", 1, platform, shopId, checkoutToken, reason])`.
  `blockedOperation` and optional context no longer affect the identity.
  The first committed notice retains its operation-specific body. Unit and real
  PostgreSQL regressions cover both entrypoint orders, concurrent mixed-operation
  requests, duplicate/no-rewrite behavior, reason/shop/platform/checkout
  separation and `lastMessageAt` handling.

### Validation Results

Implementation worktree observed in terminal logs:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-046-BACKGROUND-005`.

- Original seven-file focused unit selection: **92 passed / 1 failed**;
  the single failure was the expected source-key fixture, which was
  subsequently corrected. **The full selection was not rerun** as a unit after
  the final correction. During developer self-review, the current focused
  selection ran 5 files / 56 tests and passed, but its key-vector assertions
  encode the same contract mismatch recorded below.
- Corrected formatter unit test:
  `npm test -- tests/unit/services/checkout-recovery/recovery-consent-merchant-notice.formatter.test.ts`:
  **7/7 passed**.
- Canonical notifier unit test:
  `npx vitest run tests/unit/services/checkout-recovery/recovery-consent-merchant-notice.service.test.ts`:
  **7/7 passed**.
- Disposable PostgreSQL integration test (with local Prisma on `PATH`):
  `PATH="$PWD/node_modules/.bin:$PATH" node scripts/test-integration.mjs tests/integration/recovery-consent-merchant-notice.integration.test.ts`:
  **3/3 passed** on 2026-10-25. Covers independent-client deduplication,
  noncanonical collision rejection and transactional rollback.
- `npm run build` (Prisma generation + TypeScript): **passed**.
- `npm run lint`: **passed**.
- `git diff --check`: **passed** before the correction commit.
- Source commit `abaa394` and follow-up commit `f204911` were pushed;
  successful remote update:
  `abaa394..f204911 task/ARCH-046-BACKGROUND-005 -> task/ARCH-046-BACKGROUND-005`.
- The first attempted plain `git push` failed because the branch tracked
  `origin/main`; explicit `git push -u origin task/ARCH-046-BACKGROUND-005`
  then succeeded. This is not an implementation test failure.
- Terminal output showed an untracked `typescript` log file. It was **not**
  staged or included in commit `f204911`.

**After the operation-independent source-key correction (2026-10-25 log):**

- `npm test -- tests/unit/services/checkout-recovery/recovery-consent-merchant-notice.formatter.test.ts tests/unit/services/checkout-recovery/recovery-consent-merchant-notice.service.test.ts tests/unit/services/checkout-recovery/recovery-consent-admission.service.test.ts`:
  **21/21 passed across 3 files** (formatter 7, notifier 8, admission 6).
- `PATH="$PWD/node_modules/.bin:$PATH" node scripts/test-integration.mjs tests/integration/recovery-consent-merchant-notice.integration.test.ts`:
  **3/3 passed** on disposable real PostgreSQL. The updated first scenario checks
  mixed `CREATE_FIRST_RECOVERY` / `SEND_INITIAL_RECOVERY` operations from two
  Prisma clients deduplicate, preserve the first body, isolate tenants and do
  not regress thread timestamps; the other scenarios cover noncanonical
  collision rejection and transaction rollback.
- `git diff --cached --check`: **passed before commit**, with no error reported.
- Implementation commit `8c6f034` changed the four scoped files and was pushed
  successfully: `f204911..8c6f034` on
  `origin/task/ARCH-046-BACKGROUND-005`.
- Post-push `git status`: **tracked files clean and branch synchronized** with
  `origin/task/ARCH-046-BACKGROUND-005`; the local `typescript` log remained
  untracked and was not included in the correction commit.
- **Not evidenced after `8c6f034`:** the requested checkout-reconciliation unit
  test, complete five-file focused regression set, fresh `npm run build`,
  `npm run lint`, or separate post-correction `git diff --check`. Earlier
  passing results remain historical and are not represented as a fresh rerun.

### Deviations

- **Concurrency-safe thread creation**: the task work item specifies
  `merchantSupportThread.upsert`. Parallel real-PostgreSQL execution showed
  a `P2002` shopId uniqueness race. The implementation instead uses
  `merchantSupportThread.createMany({ skipDuplicates: true })`, then
  `findUniqueOrThrow({ where: { shopId } })` inside the same transaction.
  The architect should confirm that this preserves the required invariant.
- Shopify checkout-item count is omitted where the existing snapshot
  does not prove the item list is complete; no provider call was added.

### Assumptions

- Development-only historical Shopify Support notice keys do not require
  compatibility, migration or rewrite.
- Context enrichment belongs to the verified platform-specific caller.
- The real Woo `onDeniedAdmission` binding remains owned by
  `ARCH-046-BACKGROUND-002`.

### Unresolved Issues

- The Attempt 1 identity violation recorded in Developer Self-Review below is
  corrected in published commit `8c6f034`; that review remains as historical
  Changes Requested evidence, not an accepted review.
- The latest log does not show a canonical Attempt 2 claim. Parent task YAML
  therefore remains `status: ready`, `attempt: 1`, `executor: null`,
  `claimed_at: null`. The developer launcher must claim Attempt 2 before
  preparing a `review` status transition.
- The architect requested a focused checkout-reconciliation unit rerun plus
  build, lint and `git diff --check` after the correction; the latest log does
  not evidence these. The original full seven-file selection was not rerun
  after the fix either.
- Launcher-prepared parent/implementation worktree isolation, attempt-2
  synchronization and recursive submodule preparation evidence have not been
  supplied in this latest log. Capture those in the claimed attempt report.

### Architectural Concerns

- The concurrency-safe thread creation differs from the prescriptive
  `upsert` wording; the service's transactional and tenant-scoped
  behavioral contract is unchanged in the passing focused tests.
- Do not promote `ARCH-046-BACKGROUND-002` before authorised review and
  explicit developer completion of this task.

## Developer Self-Review - Changes Requested

### Outcome

Changes Requested — Attempt 1 does not satisfy the canonical source-key contract. The key currently includes `blockedOperation`, contrary to the identifier invariant, which explicitly excludes it so the same platform/shop/checkout/reason observed at first recovery creation and initial-send re-entry produces one notice.

### Required Corrections

- In `createRecoveryConsentNoticeSourceKey`, hash exactly `JSON.stringify(["recovery-consent", 1, platform, shopId, checkoutToken, reason])` in that order. Do not include `blockedOperation` or context.
- Replace the formatter test's “including blocked operation” vectors with a regression asserting identical source keys for `CREATE_FIRST_RECOVERY` and `SEND_INITIAL_RECOVERY` when platform, shop, checkout token and reason match. Keep assertions that platform/shop/token/reason changes produce distinct keys.
- Preserve operation-specific body copy. Add or retain a persistence-level replay test proving a second call with the same identity but a different `blockedOperation` returns `duplicate`, inserts no second message, and does not rewrite the original body.
- Rerun the focused formatter, notifier, Shopify-admission and checkout-reconciliation unit tests, the disposable PostgreSQL integration test, build, lint and `git diff --check`; record final results on the next attempt.

### Attempt State

Attempt 1 remains the reviewed attempt. The task returns to `ready` with `executor: null` and `claimed_at: null`; no Attempt 2 claim was made by this review.

### Review Evidence

- The final published implementation branch is `f204911db4bc41f9eaf2037ced54364f566831dc` and is clean/synchronized with its remote. The parent task branch is `1a71c1079a2f19a7d8bcddf0dd885a4831cfe052` before this review record update.
- Focused Vitest run completed 5 files / 56 tests successfully; the suite currently asserts operation-dependent hashes, so it cannot validate the task's operation-independent key requirement.
- The source-key implementation and formatter test were inspected directly. Both include/assert `blockedOperation` in the digest, while the task contract explicitly says it is deliberately excluded.
- No implementation files were modified during this review decision.

## Architect Review

### Review Status

Pending.

### Review Notes

Await accepted implementation branch, parent task branch/Completion Report and validation evidence. Review source, contracts, Shopify behaviour, multi-tenant identity and unique-key transaction semantics independently.

### Reviewed Files

Not yet reviewed.

### Validation Reviewed

Not yet reviewed.

### Architecture Conformance

Pending.

### Follow-up

After acceptance, promote `ARCH-046-BACKGROUND-002` if its remaining dependencies and implementation gate are satisfied; do not open the live Woo orchestration gate prematurely.

## Execution Ownership Amendment

- Date: 2026-10-24
- Change: The developer explicitly invoked the developer-create workflow for this ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_background`, coordinator, dependencies, task scope, and acceptance criteria.
- Claim state: This amendment does not claim an implementation attempt; the canonical launcher records the claim after dependency and worktree preparation.
