---
id: ARCH-046-BACKGROUND-005
architecture_id: ARCH-046
title: Extract shared recovery consent merchant notification service
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-BACKGROUND-002
enables:
  - ARCH-046-BACKGROUND-002
created: 2026-10-24
updated: 2026-10-24
---

# Extract shared recovery consent merchant notification service

## Architecture

- Architecture: `ARCH-046`.
- Parent: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`.
- Coordinator: `moda_architect`.
- Implementation owner: `moda_background` in `moda-interact-background`.
- Lifecycle: proposed portable definition. This review package does **not** claim task materialisation, execution, commits, or remote worktree access; the actual parent task metadata is authoritative after materialisation.
- Rollout: **pre-production**. The developer explicitly waived compatibility with old development Support notice bodies and `sourceKey` formats. No migration, backfill, dual-read/write, compatibility alias, or deletion of existing Support data is authorised.

## Objective

Replace Shopify's existing recovery-consent Support notice writer with **one Background-local, platform-neutral, independently testable notifier**. It must generate useful, truthful merchant-facing messages, use a single deterministic idempotency identity and transactional Support persistence implementation, and be usable by both Shopify and the subsequent WooCommerce adapter.

**Stop boundary:** this task **migrates Shopify** to the new notifier and **contract-tests a synthetic Woo caller**. `ARCH-046-BACKGROUND-002` subsequently implements the real Woo admission callback, denial mapping and shop-scoped context lookup. This task must not implement Woo workers, admission policy or actual Woo call-site wiring.

## Context

Verified against the 2026-10-24 14:14 snapshot:

- `src/services/checkout-recovery/recovery-consent-notice.service.ts` owns `RecoveryConsentNoticeService.publish`. It upserts a `MerchantSupportThread`, writes a deduplicated `SYSTEM` message with `createMany({ skipDuplicates: true })`, and updates `lastMessageAt` only on insertion. Its body, system code and key format are Shopify-specific, and its displayed checkout digest is not actionable merchant context.
- `src/services/checkout-recovery/recovery-consent-admission.service.ts` calls that writer from `evaluateFirst`, `evaluateReentry` and `notifyMissingRecipient`. Its Shopify-native consent reader, local STOP exclusion and `SHOPIFY_RECOVERY_CONSENT_RETRY_REQUIRED` exception must remain intact.
- `src/services/checkout-recovery/recovery-initiation.service.ts` already has `RecoveryCheckoutSeed` containing customer first/last name, email, checkout total/currency, line items and last observed activity. This task may pass those **already accepted** fields to the Shopify admission adapter without introducing provider/database lookups to the shared notifier.
- `MerchantSupportThread.shopId` is unique; `MerchantSupportMessage.sourceKey` is globally unique. Existing fields include `kind`, `state`, `originalBody`, `sourceLanguageTag`, `systemCode`, `systemVersion`, `availableAt` and `threadId`. No migration is required.
- `WooRecoveryAdmissionService` (ARCH-048-BACKGROUND-003) exposes an **awaited** `onDeniedAdmission({ shopId, checkoutToken, reason })`. The future Woo adapter filters the denial reason and enriches shop-scoped details before calling the canonical notifier.

## Scope

1. Define the exact Background-local contract and pure helpers specified below; do not publish it through `moda-interact-shared` or use `Port` in new interface names.
2. Implement one canonical formatter, source-key generator, and transaction-backed `RecoveryConsentMerchantNoticeService` implementing `RecoveryConsentMerchantNotifier`.
3. Replace the old Shopify notice writer and migrate every current Shopify admission caller to the new interface, forwarding already available customer/checkout context when verified.
4. Preserve all existing Shopify consent, STOP, pre-first-INSERT, `DETECTED` re-entry, recipient validation and bounded-retry decisions. Only notice formatting, identity and persistence ownership change.
5. Test the canonical service for both `SHOPIFY` and `WOOCOMMERCE` using a **synthetic Woo caller**. Do not implement the real Woo callback; hand that contract to `ARCH-046-BACKGROUND-002`.
6. Use the approved Shared structured logger with safe event metadata. Never turn a business/DB failure into a successful or duplicate result; preserve genuine provider-unavailability retry behaviour.

### Exact source-file ownership

All paths below are **relative to `moda-interact-background/`**:

| Path | Required change |
|---|---|
| `src/services/checkout-recovery/recovery-consent-merchant-notice.contracts.ts` | Export the exact input/result/interface types, constants and approved enums below. No I/O. |
| `src/services/checkout-recovery/recovery-consent-merchant-notice.formatter.ts` | Pure validation/sanitisation, fixed message copy and deterministic line formatter; export a formatter used by the service and tests. |
| `src/services/checkout-recovery/recovery-consent-merchant-notice.service.ts` | Only active Support persistence writer for this notice family; canonical sourceKey, injected DB/clock/logger, transaction and structured outcomes. |
| `src/services/checkout-recovery/recovery-consent-admission.service.ts` | Thin **Shopify** reason/operation adapter; depend on `RecoveryConsentMerchantNotifier`; no SQL/formatting/hash. |
| `src/services/checkout-recovery/recovery-initiation.service.ts` | Only the minimal forwarding of verified `RecoveryCheckoutSeed` context into the existing Shopify admission methods; no new provider or database queries and no changed consent decisions. |
| `src/services/checkout-recovery/recovery-consent-notice.service.ts` | Remove after all production imports and tests move; do not leave an active legacy writer/alias. |
| `tests/unit/services/checkout-recovery/recovery-consent-merchant-notice.formatter.test.ts` | Exact text, input bounds, control-character safety and omission tests. |
| `tests/unit/services/checkout-recovery/recovery-consent-merchant-notice.service.test.ts` | Identity vectors, injection, transaction, duplicates, tenancy, errors, synthetic Woo test. |
| `tests/unit/services/checkout-recovery/recovery-consent-admission.service.test.ts` | Extend Shopify reason/operation mapping, STOP and retry regression tests. |
| `tests/integration/recovery-consent-merchant-notice.integration.test.ts` | PostgreSQL uniqueness/concurrency/rollback tests using the repository's existing test database harness. |

The implementor may adjust a test import/fixture directly required by the above rename; any materially wider change is an architectural scope deviation to report, **not** self-authorised refactoring. No edits to WooCommerce, Shopify UI, API, Prisma schema, unrelated Support writers, or `docs/decisions/**/_index.md`.

## Out of Scope

- Implementing Woo's real `onDeniedAdmission` callback, Woo customer lookup, checkout capture, worker wiring, outgoing WhatsApp, template selection, billing, or new recovery creation.
- Any new Support table, queue, migration, shared package export, third-party notification system, translation pipeline or merchant UI.
- Editing/reopening accepted `ARCH-045-BACKGROUND-002`, modifying STOP's separate merchant notification, or replacing provider-native consent policies.
- Legacy notice compatibility, backfill or destructive cleanup of existing development messages.
- Creating a shared generic logger, swallowing unexpected exceptions, or introducing an additional active Support notice writer.

## Requirements

### R1. Eligibility and decision mapping (mandatory exhaustive table)

The **shared notifier does not decide eligibility**. Its callers apply the following mapping. “Notify” is an awaited call; any error from it rejects the invoking operation.

**Existing Shopify adapter, implemented in this task:**

| Existing admission/consent outcome | Normalised reason | Action | Operation |
|---|---|---|---|
| Missing `customerId`, Shopify customer ID or exact recipient during `evaluateFirst` | `RECIPIENT_UNVERIFIED` | Notify, then return `false` | `CREATE_FIRST_RECOVERY` |
| Missing customer/recipient in `evaluateReentry` | `RECIPIENT_UNVERIFIED` | Notify, then return `false` | `SEND_INITIAL_RECOVERY` |
| `notifyMissingRecipient` after a recovery row exists | `RECIPIENT_UNVERIFIED` | Notify | `SEND_INITIAL_RECOVERY` |
| `NOT_AUTHORISED` / `NATIVE_CONSENT_NOT_GRANTED` | `NO_VERIFIED_OPT_IN` | Notify, return `false` | Current caller's operation |
| `AMBIGUOUS` (for example multiple active recipients) | `RECIPIENT_AMBIGUOUS` | Notify, return `false` | Current caller's operation |
| Any other non-STOP `NOT_AUTHORISED` identity/recipient mismatch | `RECIPIENT_UNVERIFIED` | Notify, return `false` | Current caller's operation |
| `UNAVAILABLE` | `VERIFICATION_UNAVAILABLE` | Notify, **then throw existing** `SHOPIFY_RECOVERY_CONSENT_RETRY_REQUIRED` | Current caller's operation |
| `NOT_AUTHORISED` / `LOCAL_NO_CONTACT` | — | **Skip**; existing STOP notice owner handles this | Both |
| `ALLOWED` | — | **Skip**; permit existing recovery processing | Both |

Do not map `AMBIGUOUS` to `RECIPIENT_UNVERIFIED` or `UNAVAILABLE` to `NO_VERIFIED_OPT_IN`. The existing `evaluateFirst`/`evaluateReentry` signatures may gain an **optional** `noticeContext` field; existing callers/test fixtures must remain valid. `evaluateFirst` is creation-stage; `evaluateReentry` and `notifyMissingRecipient` are send/re-entry-stage; no caller guesses the operation from recovery status inside the shared notifier.

**Future Woo adapter (`ARCH-046-BACKGROUND-002`; contract tests only here):**

| `WooAdmissionDenialReason` | Normalised reason | Action |
|---|---|---|
| `CONSENT_NOT_GRANTED` | `NO_VERIFIED_OPT_IN` | Notify |
| `CONSENT_AMBIGUOUS` | `RECIPIENT_AMBIGUOUS` | Notify |
| `RECIPIENT_MISSING`, `RECIPIENT_INVALID`, `RECIPIENT_IDENTITY_MISMATCH`, `CONSENT_RECIPIENT_UNVERIFIED` | `RECIPIENT_UNVERIFIED` | Notify |
| `CONSENT_NO_CONTACT` | — | Skip; existing STOP notice owner |
| `CONSENT_CHANGED` | — | Skip; re-evaluate/handle via existing admission semantics; do not imply refusal |
| `INVALID_CANDIDATE`, `SHOP_NOT_ELIGIBLE`, `INSTALLATION_INACTIVE`, `BASKET_EMPTY`, `BASKET_INVALID` | — | Skip; not consent denial |
| `deferred` / `CONSENT_UNAVAILABLE` | — | No denied callback; preserve existing bounded retry/defer behaviour |

Do not convert recipient/policy/technical denials into notifier decisions; the future Woo adapter owns that mapping and must not duplicate SQL, hashing or formatting.

### R2. Message operations, exact copy and ordering

The persisted `originalBody` is **plain text with LF (`\n`) newlines**, with these lines in this exact order (omit only optional field lines when absent):

```text
Checkout recovery could not proceed
Platform: <Shopify|WooCommerce>
Customer: <customerName>                           [optional]
Email: <customerEmail>                              [optional]
Checkout total: <CURRENCY> <amountDecimal>          [optional]
Items: <itemCount>                                  [optional]
Last recorded activity: <YYYY-MM-DD HH:mm UTC>       [optional]
Checkout reference: <merchantVisibleReference>      [optional]
Customer / checkout details: Not available from the recorded checkout. [only when ALL optional fields absent]
Reason: <fixed reason copy>
Outcome: <fixed operation copy>
```

**Reason copy** (exact, without quotation marks):

| Reason | `Reason:` value |
|---|---|
| `NO_VERIFIED_OPT_IN` | `Verified WhatsApp marketing permission is not available for this customer.` |
| `RECIPIENT_UNVERIFIED` | `Moda could not verify the exact customer and WhatsApp recipient for this checkout.` |
| `RECIPIENT_AMBIGUOUS` | `Moda could not identify one unambiguous WhatsApp recipient for this checkout.` |
| `VERIFICATION_UNAVAILABLE` | `WhatsApp consent verification was temporarily unavailable. The customer's preference is unknown, not refused.` |

**Operation copy** (exact, without quotation marks):

| Operation | `Outcome:` value |
|---|---|
| `CREATE_FIRST_RECOVERY` | `No checkout recovery was created, and no WhatsApp recovery message was sent.` |
| `SEND_INITIAL_RECOVERY` | `The initial WhatsApp recovery message was not sent at this check. An existing recovery may remain.` |

Do **not** claim that credits were refunded, never charged, or consumed: billing is not an input to this notifier. Do not mention an external retry promise or customer consent refusal. This notice is a **Merchant Support SYSTEM** message, not a customer/WhatsApp notification. Do not insert URLs or render HTML/Markdown.

### R3. Exact types and public method

Implement these exports from `recovery-consent-merchant-notice.contracts.ts` without renaming or adding required fields:

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
  lastActivityAt?: string;
  merchantVisibleReference?: string;
}>;

export type RecoveryConsentNoticeInput = Readonly<{
  shopId: string;
  platform: RecoveryConsentNoticePlatform;
  checkoutToken: string; // INTERNAL ONLY: never render or log
  reason: RecoveryConsentNoticeReason;
  blockedOperation: RecoveryConsentBlockedOperation;
  context?: RecoveryConsentCheckoutContext;
}>;

export type RecoveryConsentNoticeResult = "created" | "duplicate";
export interface RecoveryConsentMerchantNotifier {
  notify(input: RecoveryConsentNoticeInput): Promise<RecoveryConsentNoticeResult>;
}
```

`RecoveryConsentMerchantNoticeService` must implement the interface. The notifier accepts an injectable transaction-capable Prisma client, `now: () => Date` clock, and approved `StructuredLogger`. The formatter is pure and testable without Prisma, environment variables or network calls. All callers `await notify`.

### R4. Input validation, optional context and privacy

**Required input:** reject (throw) missing/blank `shopId` or `checkoutToken`, strings longer than 128/1024 characters respectively, an unknown enum value, invalid `blockedOperation`, or an invalid `now()` date. Use safe error messages naming the field, never its value. Do not silently turn such contract failures into `duplicate` or a normal consent denial.

**Optional context:** the platform-specific adapter validates ownership of the source checkout/customer before constructing it. The common formatter performs these exact presentational checks; invalid optional fields are **omitted**, not fabricated and not allowed to block a valid consent notice:

- `customerName`: Unicode plain text; trim, collapse whitespace, remove C0/C1, CR/LF/tab, bidi-control and line-separator characters; max 120 Unicode code points. Omit if empty.
- `customerEmail`: trim; max 254 characters; require exactly one `@`, no whitespace/control/angle bracket and nonblank local/domain parts. Preserve existing case; omit if malformed. Never log it.
- `checkoutTotal`: include **only when both** fields exist; `currency` must be uppercase three ASCII letters (`^[A-Z]{3}$`); `amountDecimal` must match `^(0|[1-9][0-9]{0,11})(\.[0-9]{1,3})?$`. Display the supplied decimal exactly; no rounding, conversion or guessed currency. Omit both if invalid.
- `itemCount`: safe integer in `[0, 100000]`; count **units**, not line-item rows, only when the platform adapter has an accepted complete list. Never infer `0` from missing or truncated items.
- `lastActivityAt`: a valid ISO-8601 timestamp with `Z` or an explicit numeric offset; parse and render UTC as `YYYY-MM-DD HH:mm UTC`. Label **recorded** activity, not independently verified live activity. Omit if invalid.
- `merchantVisibleReference`: explicit adapter-verified, non-secret admin-visible checkout/order reference, maximum 80 characters, matching `^[A-Za-z0-9#][A-Za-z0-9 ._#/-]{0,79}$`. Omit an untrusted URL, raw/session/cart/checkout token, token-equal string, digest, or an unverified merchant reference. **Never derive this from `checkoutToken`.**

Use plain text only. No HTML or Markdown interpolation, no uncontrolled newlines, URLs, raw phone numbers, provider credentials or token leakage. `originalBody` must be at most **2048 UTF-8 bytes**, including heading/reason/outcome; field limits must make the budget enforceable without truncating fixed reason/outcome copy. The `sourceKey` and logs contain no raw checkout/customer values.

**Shopify context forwarding is required when already available:** In `RecoveryInitiationService`, compute optional `noticeContext` from the *accepted* `RecoveryCheckoutSeed`: combined first/last name, customer email, total/currency pair, complete line-item unit count where known, and `lastExternalActivityAt ?? detectedAt`. Forward that context through existing `evaluateFirst`, `evaluateReentry` and `notifyMissingRecipient` paths. Do not perform new Shopify calls or customer database lookups solely for notice enrichment. If an input is missing or not verifiably complete, omit that line. A genuine source-provided non-secret merchant admin reference may be forwarded; do not use `checkoutUrl`, `cartToken` or opaque checkout tokens as the displayed reference.

**Woo context forwarding is NOT implemented here.** BG-002 will fetch/enrich only already accepted shop-scoped checkout/customer data and use this identical contract. Its three-field `WooDeniedAdmission` callback is not modified in this extraction task.

### R5. Canonical deduplication identity (pre-production contract)

Generate the following exact key. **Unlike the earlier proposed draft, `blockedOperation` IS part of the identity** because a denied creation and a subsequently denied initial send are distinct merchant-visible events:

```ts
const payload = JSON.stringify([
  "recovery-consent", 1,
  input.platform, input.shopId, input.checkoutToken,
  input.blockedOperation, input.reason,
]);
const sourceKey = "recovery-consent:v1:" +
  createHash("sha256").update(payload, "utf8").digest("hex");
```

Fixed test vectors (`shopId=shop-test-1`, `checkoutToken=checkout-secret-123`, platform `SHOPIFY`, reason `NO_VERIFIED_OPT_IN`):

- `CREATE_FIRST_RECOVERY` → `recovery-consent:v1:67180b364e0e55cce3bea52d4f50774594447b6be4c6ff3cd9146d9b2c19f94c`
- `SEND_INITIAL_RECOVERY` → `recovery-consent:v1:eb189d63ca39d5d678e4b3c4a3a03632770d4738ded39cded501bc1b8b8dc89a`

Keys differ for platform, shop, checkout, operation or reason, but not for changes to optional display context or retry timestamp. First committed notice is immutable; replays and parallel calls must not rewrite its body. **No** recognition, backfill or dual-write of old Shopify `shopify-recovery-consent:v1` keys is required. Never delete old Support messages as part of the task.

### R6. One atomic Support transaction

The only side effect of `notify` is a SYSTEM Support notice and its thread metadata. Implement exactly this observable behaviour:

1. Validate required input, normalise optional presentation context, generate sourceKey and body **before** opening the transaction.
2. Inside a single PostgreSQL `$transaction`, `merchantSupportThread.upsert({ where: { shopId }, create: { shopId }, update: {} })`.
3. `merchantSupportMessage.createMany({ skipDuplicates: true, data: [one message] })`, with `threadId` from that thread; fields: `kind=SYSTEM`, `state=AVAILABLE`, `systemCode="RECOVERY_CONSENT_ADMISSION"`, `systemVersion="1"`, `sourceLanguageTag="en-GB"`, `availableAt=now()` and `originalBody` from R2.
4. If `count===1`, update `MerchantSupportThread.lastMessageAt` to the insertion timestamp **without regressing an existing later timestamp** (conditional write or database `GREATEST` as appropriate); return `"created"` only after commit.
5. If `count===0`, query `merchantSupportMessage.findUnique({ where: { sourceKey } })` **in the same transaction**. Return `"duplicate"` only when a row really exists, is in this shop's `threadId`, has the same `SYSTEM` kind and canonical `systemCode/systemVersion`; otherwise throw an invariant error. Do not update `lastMessageAt` on duplicate.
6. If `count` is anything else or a DB/transaction operation throws, propagate the failure. The transaction must roll back all its writes, including thread metadata, on failure.

No Redis, provider HTTP, translation request, event publishing, WhatsApp/billing operation or logger sink call inside this transaction. The global `sourceKey` unique constraint is the idempotency authority, not process-memory locks. Races across workers/processes must pass PostgreSQL-backed tests.

### R7. Structured logging and failure semantics

Reuse the approved `@modainteract/moda-interact-shared/logging` (`StructuredLogger`/existing process logger). Emit semantic events `recovery.consent_notice.created`, `.duplicate`, and `.failed` **outside** the transaction. Safe fields only: `shopId`, `platform`, `reasonCode`, `blockedOperation`, result, and optionally a **hash-only** checkout correlation suffix; for errors include a bounded error **type/category**, not error messages or stack traces containing personal data. Never log notice bodies, raw checkout IDs, name, email, phone, tokens, API credentials, total checkout payloads or source payload.

`notify` must not catch an unexpected error and return `duplicate`/success/denial; if caught for safe diagnostics, rethrow the original error. The existing Shopify `UNAVAILABLE` outcome is not a notifier exception: after a successful notice, its admission adapter must still throw the established retry sentinel. An actual notifier/Prisma failure rejects the admission operation as such. The approved shared logger is responsible for sink-failure isolation; a logging sink outage must not change a committed business result or roll it back.

## Work Items

- [ ] Inspect the actual Shopify notice writer, admission service, its `RecoveryInitiationService` call sites, focused tests, Support schema and `docs/observability/shared-logging.md`; record any discrepancy before editing.
- [ ] Create the **three** specified contract/formatter/service files with the exact exported names, R2 fixed text, R4 validators and R5 test vectors.
- [ ] Implement R6 transactional Support persistence once; verify duplicate by querying `sourceKey`, tenant ownership and canonical system metadata.
- [ ] Migrate Shopify's first-admission, re-entry and missing-recipient paths; forward existing safe checkout context and preserve original consent/STOP/retry semantics.
- [ ] Retire the old Shopify-only writer; prove no application import or worker uses it and no duplicate writer remains.
- [ ] Add required pure/unit tests, synthetic Woo contract test and PostgreSQL concurrency/rollback integration tests; run focused Shopify regressions.
- [ ] Verify the exact scope and logging redaction, fill in the Completion Report and validation evidence, change the task to `review`, and stop for architect review.

## Interfaces / Contracts

The **complete normative contract** is Requirements **R1–R7**, including types, sourceKey recipe, exact templates, field bounds, transactions and error semantics. These sections are implementation requirements, not examples or suggestions. `RecoveryConsentMerchantNotifier` is local to Background; it must not be redefined in `ARCH-046-BACKGROUND-002`.

Implementation must be dependency-injected/testable: `RecoveryConsentMerchantNoticeService` owns the formatter and a transaction-capable Prisma client, an injectable clock and the approved logger. Shopify's constructor accepts `RecoveryConsentMerchantNotifier` (not the concrete writer). BG-002 will consume the same published-from-Background TypeScript interface and provide Woo-specific mapping/context without cloning implementation.

The notifier's only return values are the two declared success results. “Skip notification”, provider “defer”, “deny admission” and “retry later” are **caller** outcomes, never forged notifier return values. Changing input fields, enum semantics, deduplication identity or message wording requires architect approval before dependent Woo implementation.

## Dependencies

- `ARCH-045-BACKGROUND-002` — Complete; accepted Shopify pre-insert consent notice implementation being extracted. No ARCH-048 orchestration dependency is required for this platform-neutral extraction.

## Enables

- `ARCH-046-BACKGROUND-002` — real Woo denial callback, exhaustive reason mapping, checkout-context adapter and consumption of this accepted notifier. It must not introduce another writer.

## Acceptance Criteria

- [ ] One active common notifier/formatter/writer exists; Shopify imports its typed interface; a synthetic Woo caller uses the same class. No old writer or runtime import remains.
- [ ] Shopify reason decision table R1 is matched exactly for first admission, existing `DETECTED` re-entry and missing recipient; confirmed local STOP and verified grant yield **zero** new consent notice; UNAVAILABLE produces one truthful notice then retains the existing retry error.
- [ ] Merchant bodies match exact R2 line order and reason/operation wording, include accepted Shopify name/email/amount/item/activity fields when present, and omit missing or unsafe fields. A Woo synthetic input produces the same format apart from platform label. No hash-only body.
- [ ] Required invalid inputs throw safely; optional malformed/untrusted data are omitted. Unicode/control/newline injection and the 2048-byte body cap are tested. Raw checkout/phone/session tokens and untrusted URLs do not appear in body, `sourceKey` or logs.
- [ ] SHA-256 fixed vectors from R5 match exactly. Same identity (even under parallel calls) produces one message; different shop/platform/checkout/reason/**operation** produces separate messages; display-context changes do not rewrite an existing message.
- [ ] PostgreSQL-backed integration tests prove `createMany.count===0` is verified before returning duplicate, `lastMessageAt` changes only on insertion and does not regress under concurrent inserts, and thread/message work rolls back together on fault.
- [ ] Failed Prisma call, sourceKey lookup failure, transaction update failure, invalid required input or formatter invariant propagates. Shared logger sink failure does not prevent or undo an otherwise successful notice.
- [ ] On denied first admission, Shopify still creates no `CheckoutRecovery`, outbound attempt, WhatsApp message, conversation or credit. `DETECTED` retries retain stored-only permission checks and normal billing gates; no provider polling is added.
- [ ] Pre-production contract is adopted without legacy migration/backfill, without deleting old development Support data, and without changes to other services, workers, apps or schema.
- [ ] Required launcher/worktree isolation, start-of-attempt synchronisation, test commands/results and code-file list appear in the Completion Report.

## Validation

- [ ] `vitest run tests/unit/services/checkout-recovery/recovery-consent-merchant-notice.formatter.test.ts tests/unit/services/checkout-recovery/recovery-consent-merchant-notice.service.test.ts tests/unit/services/checkout-recovery/recovery-consent-admission.service.test.ts` from `moda-interact-background/` (adjust only if the actual package runner has changed, and record the change).
- [ ] PostgreSQL integration via the repository's existing `scripts/test-integration.mjs tests/integration/recovery-consent-merchant-notice.integration.test.ts`, including two parallel clients, tenant isolation, duplicate verification and rollback. Never run destructive tests on production data.
- [ ] Focused existing Shopify initial-admission/materialisation, capacity resume and `DETECTED` reentry unit tests; record exact file list and result, not a general “tests passed” claim.
- [ ] Repository-declared TypeScript compilation/typecheck (`npm run build` where applicable) and lint of changed files; no invented `typecheck` script, and no unrelated baseline repairs.
- [ ] `git diff --check`, plus explicit search showing zero active imports of `recovery-consent-notice.service.ts` and no personal/customer data in emitted log fixtures.
- [ ] Test safe failure propagation with Prisma exceptions and logger sink outage separately; include exact observed retry/suppression outcomes.

## Stop Condition

Once all task work items, acceptance criteria and required validation are complete, the implementing agent fills in its Completion Report, changes its assigned task to `review`, returns the implementation branch and parent task branch evidence to `moda_architect`, and **STOPS**. It must not wire the real Woo adapter or execute subsequent tasks.

## Implementation Notes

- Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the `/moda-task` prepared-launch packet. Parent workspace and implementation repository must use separate launcher-resolved dedicated worktrees on matching `task/ARCH-046-BACKGROUND-005` branches; record isolation, start-of-attempt synchronisation and recursive submodule evidence. Do not derive paths from another task worktree.
- Do not implement a new generic logger; import the approved Shared logging API. Keep errors visible and retries working; never swallow exceptions to “avoid notification noise”.
- Follow existing Merchant Support authorisation/translation conventions; the notifier does **not** start a translation job or modify Shopify/WooCommerce UI. This is a merchant-facing Support message, not customer-facing marketing outreach.
- Use one scoped service, one pure formatter and one canonical interface, not a catch-all orchestration module. Helpers for sanitisation/sourceKey may be private to those files; do not introduce extra generic mechanisms.
- Pre-production means old notice formats need no compatibility, **not** that existing merchant Support rows can be deleted. Any new cross-repository requirement discovered during implementation must be returned to the architect.
- Do **not** modify `docs/decisions/**/_index.md` until the architectural session is explicitly complete.

## Completion Report

### Status

Not Started — proposed task definition; implementation work not claimed in this review package.

### Files Changed

None yet.

### Work Completed

Not started.

### Validation Results

Not executed (documentation proposal only).

### Deviations

None.

### Assumptions

Previously sent development notices need no backward compatibility; existing Support database data is not to be deleted.

### Unresolved Issues

None identified in this definition. Scope discrepancies found during implementation must be reported rather than decided independently.

### Architectural Concerns

None recorded at task-definition time.

## Architect Review

### Review Status

Pending.

### Review Notes

Await implementation code, focused tests, worktree evidence and Completion Report. Verify every R1–R7 requirement against actual source and a PostgreSQL-backed duplicate/rollback test.

### Reviewed Files

Not yet reviewed.

### Validation Reviewed

Not yet reviewed.

### Architecture Conformance

Pending.

### Follow-up

After acceptance, evaluate `ARCH-046-BACKGROUND-002`'s remaining dependencies and architect execution gate. Do not automatically activate Woo outbound or BG-005 orchestration solely because this extraction is complete.
