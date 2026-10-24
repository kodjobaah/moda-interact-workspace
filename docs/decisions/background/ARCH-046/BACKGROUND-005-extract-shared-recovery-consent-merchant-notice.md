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
claimed_at: 2026-10-24T17:18:52Z
attempt: 1
depends_on:
  - ARCH-045-BACKGROUND-002
enables:
  - ARCH-046-BACKGROUND-002
created: 2026-10-24
updated: 2026-10-24
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

- [ ] **Single writer:** exactly one reusable Support writer for this recovery-consent notice family, consumed by Shopify now and callable by Woo through the same public TypeScript interface.
- [ ] **Tenant safety:** all persisted messages belong to the `MerchantSupportThread` for the validated input `shopId`; the caller may attach customer context only after resolving it for that exact shop and checkout. No cross-shop lookup, context fallback or deduplication collision.
- [ ] **Pre-production identity:** one deterministic canonical `sourceKey` for new notices, independent of old `shopify-recovery-consent:v1` keys. There is no legacy migration/backfill/dual-write requirement.
- [ ] **Truthful outcome:** support both refusal to **create the first recovery** and a blocked **initial-send re-entry** without falsely claiming that no recovery row exists. Do not notify for customer STOP through this service; `ARCH-045-BACKGROUND-005` owns that notice.
- [ ] **Readable body:** use short labelled plain-text lines. Include customer name/email, checkout total/currency, item count, last received activity and safe merchant-visible reference **only if individually available, validated and permitted**. Missing fields are omitted; do not invent names, totals, dates, order numbers, links or customer identifiers.
- [ ] **Content safety:** never put raw checkout tokens, phone numbers, credentials or an untrusted URL into `sourceKey` or logs. Do not place them in the notice body; a merchant-visible reference must be a vetted non-secret identifier, not a session/cart token. Escape/control/remove line breaks in individual context fields; cap field and overall body lengths. Do not render untrusted HTML or Markdown links.
- [ ] **Consent reasons:** distinguish confirmed absent marketing opt-in, unverified identity, ambiguous identity, and technical verification unavailability. The latter is **unknown**, not refusal, and must preserve the caller's bounded retry policy.
- [ ] **No new side effects:** `notify()` may only insert a Support SYSTEM notice and update its thread metadata. Never create `CheckoutRecovery`, attempt, reservation, outbound job or WhatsApp send.
- [ ] **Errors:** the service awaits the database transaction and propagates unexpected business errors after safe structured diagnostics; callers must not silently swallow these errors. Shared logger sink failures must not break correct business processing. `duplicate` is only returned for an actual sourceKey uniqueness conflict handled by the existing `skipDuplicates` pattern.

## Work Items

- [ ] Read the complete accepted Shopify task/implementation and its focused unit tests, plus `docs/observability/shared-logging.md`, before changing the source.
- [ ] Define the canonical contract and its validation/bounds; document exactly which fields are caller-supplied optional context.
- [ ] Implement the shared formatter and new deterministic `sourceKey` construction. No old Shopify id/hash compatibility or migration.
- [ ] Extract one transactional Support persistence implementation (`thread.upsert` → `message.createMany(skipDuplicates)` → conditional `thread.update`) with injected DB, clock and shared logger for tests.
- [ ] Migrate Shopify `RecoveryConsentAdmissionService` to `RecoveryConsentMerchantNotifier.notify`, retaining confirmed no-opt-in, missing identity, STOP skip, technical unavailability/retry, first admission and DETECTED re-entry semantics.
- [ ] Remove/repoint old direct writer usage, avoiding a second active implementation; verify no remaining runtime consumers of the old type/path.
- [ ] Add unit and integration tests for both platform values, reason mapping, readable optional context, idempotency, tenant isolation, concurrency, rollback, safe logging and exception propagation.
- [ ] Fill in the Completion Report, mark only verified checkboxes, set task to `review`, and stop for architect review.

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

- [ ] Exactly one active common writer and formatter exists; Shopify and a synthetic Woo adapter call the **identical** `notify` implementation and create equivalent `SYSTEM` Support messages.
- [ ] Fresh Shopify denial still creates **no** recovery, attempt, outbound message, conversation or credit; confirmed STOP still avoids a duplicate missing-consent notice; a verified Shopify grant produces no notice.
- [ ] Both platform values produce different keys for the same checkout/reason; different shops, checkouts or reasons also yield distinct keys; duplicate/retried/concurrent calls for the same identity insert at most one message.
- [ ] The persisted sourceKey/body and structured logs never contain raw checkout token, telephone number, provider credentials, untrusted URLs or injected control characters. Safe optional merchant-facing identifying details are present where supplied, omitted where absent.
- [ ] A technical-unavailable notice never asserts customer refusal. A `SEND_INITIAL_RECOVERY` notice never asserts that the recovery record was not created. No bogus data enrichment or full customer lookup in the shared service.
- [ ] A failed message insert, thread update, transaction or formatting dependency never turns into a benign `duplicate`/`denied` result; unexpected **business** exceptions propagate to the caller. A shared logger sink outage is isolated and does not roll back successful business processing.
- [ ] All new notices use the approved **new** canonical key/code. No code path attempts legacy `shopify-recovery-consent:v1` recognition, compatibility backfill or migration. Existing development rows are not deleted or rewritten by this task.
- [ ] No production runtime worker wiring, Woo admission service implementation, extra persistence or cross-repo code is changed.

## Validation

- [ ] Focused unit tests: formatter and field bounds; platform-specific truthfulness; Shopify adapter decision mapping, local STOP exclusion and unavailable-provider retry; simulated Woo invocation; sourceKey determinism and collision isolation.
- [ ] Concurrency and persistence tests: replay and parallel duplicate calls, one `lastMessageAt` update on insert, no update on duplicate, transaction rollback on insert/update failure, retry visibility after failed transaction.
- [ ] Fault injection: DB timeout/Prisma errors, notifier dependency failure and unexpected reason/context; assert business errors are diagnosed safely and rethrown (never silently swallowed). Simulate a shared logging sink failure separately and verify normal notice processing continues.
- [ ] Focused existing Shopify consent-admission and notice regression tests pass, including the initial pre-INSERT and DETECTED re-entry flows; no changed consent policy. Use exact repository package scripts/runner after inspecting `package.json`.
- [ ] Run the repository's relevant TypeScript typecheck/lint and `git diff --check`; report baseline failures with precise evidence, never pass off unrelated preexisting failures as successful task validation.
- [ ] Inspect test logs for leaked checkout/customer information and verify no unexpected duplicate active writer remains.

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

In Progress — Attempt 1 claimed by developer at 2026-10-24T17:18:52Z. Attempt 0 review history is preserved below.

### Files Changed

None yet.

### Work Completed

Not started.

### Validation Results

Not executed.

### Deviations

None.

### Assumptions

Pre-production Shopify and Woo merchant consent notices may adopt one canonical identity without legacy support.

### Unresolved Issues

None identified in the task definition; report discovered implementation gaps rather than expanding scope.

### Architectural Concerns

None identified at definition time.

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
