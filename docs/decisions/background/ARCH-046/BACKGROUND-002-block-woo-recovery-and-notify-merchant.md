---
id: ARCH-046-BACKGROUND-002
architecture_id: ARCH-046
title: Integrate Woo first-recovery consent denial with shared merchant notices
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-BACKGROUND-001
  - ARCH-045-BACKGROUND-005
  - ARCH-048-BACKGROUND-003
  - ARCH-046-BACKGROUND-005
enables:
  - ARCH-046-BACKGROUND-004
  - ARCH-048-BACKGROUND-005
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-25
---

# Integrate Woo first-recovery consent denial with shared merchant notices

## Architecture

Architecture ID: `ARCH-046`.

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`.

Coordinator: `moda_architect`.

**Execution frontier (25 October 2026 snapshot): Ready.** All four YAML dependencies are recorded Complete. `WooRecoveryAdmissionService` has an awaited `onDeniedAdmission` callback. The merged Background code contains `RecoveryConsentMerchantNoticeService` and the Shopify consumer imports it. This task has **not** been claimed or implemented. The `/moda-task` launcher must recheck status, dependencies, branch/worktree isolation and start-of-attempt synchronization before execution.

## Objective

Implement **only** a WooCommerce-specific adapter for the approved first-recovery admission-denial callback that sends appropriate, shop-scoped merchant Support SYSTEM notices through the **already accepted** shared `RecoveryConsentMerchantNotifier`. Do not create a new notifier, change the admission business rules or wire BullMQ workers here.

## Context

`ARCH-048-BACKGROUND-003` already checks current recipient, consent, STOP, installation, basket and observed order state **before inserting** the first `CheckoutRecovery`. Its `WooRecoveryAdmissionService` awaits `onDeniedAdmission({ shopId, checkoutToken, reason })` when the result is `denied`. `ARCH-046-BACKGROUND-005` is Complete and its runtime files are present in this snapshot:

- `src/services/checkout-recovery/recovery-consent-merchant-notice.contracts.ts`
- `src/services/checkout-recovery/recovery-consent-merchant-notice.formatter.ts`
- `src/services/checkout-recovery/recovery-consent-merchant-notice.service.ts`

`ARCH-048-BACKGROUND-005` owns actual worker/dependency composition. No guest-session lookup, Woo provider HTTP read or consent-triggered queue is authorised.

## Scope

- Add one independently testable Woo adapter/factory under `src/services/woocommerce-recovery/` (for example `woo-recovery-consent-notice.adapter.ts`). Export a callable compatible with `WooRecoveryAdmissionDependencies["onDeniedAdmission"]`; inject `RecoveryConsentMerchantNotifier`, a strictly shop+checkout-scoped accepted-checkout-context reader and the existing shared structured logger. An explicit dependency-injection factory is preferable to modifying the accepted BG003 service constructor.
- Map Woo denial reason codes **exactly** using the decision table in Requirements. Invoke and `await` the existing notifier only for included cases. Never invoke a separate SQL writer, thread creator, hash function or formatter.
- Project available verified checkout context from the last **successfully accepted** Woo candidate/event, when still accessible. Consult candidate storage by `(shopId, checkoutToken)` and verify returned source and identity before projecting. If no matching accepted snapshot is present (e.g. job already completed/removed), omit optional fields; do not search other shops, reconstruct a cart, query the merchant WordPress site, or infer a matching customer from phone equality.
- Supply `context.customerName` (from accepted `contact.firstName`/`lastName`), `customerEmail`, `{amountDecimal,currency}` total, `itemCount` (sum validated item quantities), `lastActivityAt` and a vetted merchant-visible reference **only when those individual facts have appropriate matching provenance**. If recipient/customer identity is unverified or ambiguous, do not describe unverified checkout contact as an authenticated customer. Missing/oversized basket `items` means `itemCount` is absent, **not zero**. The shared formatter owns all sanitisation, final omission rules and exact wording.
- Keep consent admission and STOP decisions in the accepted BG003/BG001 code. BG002 only observes a completed denial and writes an appropriate merchant notice. Technical dependency errors propagate to the caller/BullMQ; they are not converted to consent-denial notices or success.

## Out of Scope

- No rewrites of accepted `WooRecoveryAdmissionService`, `RecoveryConsentMerchantNoticeService`, its formatter or `sourceKey` implementation; no duplicate Support thread/persistence or notification queue.
- No changes to initial outreach, Meta/template category validation, credit charging, final provider permit, follow-ups or merchant-post-window messaging. `ARCH-046-BACKGROUND-004` owns the final initial-send fence; `ARCH-048-BACKGROUND-005` owns composition.
- No new database table, Woo REST/guest-session reader, consent wakeup/poller, 72-hour consent deadline, automatic recovery after later opt-in or `docs/decisions/**/_index.md` update.

## Requirements

### R1 — Exhaustive Woo denial-notice mapping

| `WooAdmissionDenialReason` | Shared reason | Notify? |
|---|---|---|
| `CONSENT_NOT_GRANTED` | `NO_VERIFIED_OPT_IN` | Yes |
| `CONSENT_AMBIGUOUS` | `RECIPIENT_AMBIGUOUS` | Yes |
| `RECIPIENT_MISSING` | `RECIPIENT_UNVERIFIED` | Yes |
| `RECIPIENT_INVALID` | `RECIPIENT_UNVERIFIED` | Yes |
| `RECIPIENT_IDENTITY_MISMATCH` | `RECIPIENT_UNVERIFIED` | Yes |
| `CONSENT_RECIPIENT_UNVERIFIED` | `RECIPIENT_UNVERIFIED` | Yes |
| `CONSENT_NO_CONTACT` | — | No: existing STOP/no-contact notification owns this |
| `CONSENT_CHANGED` | — | No: normal reconciliation/retry, not proof of refusal |
| `INVALID_CANDIDATE`, `SHOP_NOT_ELIGIBLE`, `INSTALLATION_INACTIVE`, `BASKET_EMPTY`, `BASKET_INVALID` | — | No |

These are the **actual** denial reason variants in the accepted BG003 source. A `deferred`, `already-exists`, `superseded` or `created` result never invokes this denial adapter. Unexpected/future reason variants fail visibly during exhaustive mapping review; do not silently reinterpret them as missing consent.

### R2 — Exact existing shared notifier contract

```ts
import type {
  RecoveryConsentMerchantNotifier,
  RecoveryConsentNoticeInput,
} from "../checkout-recovery/recovery-consent-merchant-notice.contracts.js";
import type {
  WooDeniedAdmission,
} from "./woo-recovery-admission.service.js";

// Illustrative adapter boundary; BG005 injects the actual callback.
type WooDeniedAdmissionNotifier =
  (denial: WooDeniedAdmission) => Promise<void>;

// For an included reason:
const input: RecoveryConsentNoticeInput = {
  shopId: denial.shopId,
  platform: "WOOCOMMERCE",
  checkoutToken: denial.checkoutToken,
  reason: mappedReason,
  blockedOperation: "CREATE_FIRST_RECOVERY",
  ...(context ? { context } : {}),
};
await notifier.notify(input);
```

Use the accepted **pre-production canonical deduplication contract as implemented**: `sourceKey` is keyed on `platform`, `shopId`, `checkoutToken` and `reason` (plus the fixed namespace/version); it **does not include** `blockedOperation`. `blockedOperation` selects truthful body wording for the first committed notice. Do not create operation-sensitive keys or change the completed shared service in this task. The notifier returns `created | duplicate` and verifies genuine duplicates internally.

### R3 — Safety, logging and errors

- Verify exact tenant/checkout identity before optional context projection; no raw checkoutKey, phone number, session token, personal data or full basket in logs or a deduplication key. No raw untrusted checkout URLs in merchant notices.
- Merchant Support must show the useful fields that are actually available from the accepted snapshot; omit individual absent/unverified fields instead of inventing them. Only the shared notifier formats and persists the message.
- Use the existing `@modainteract/moda-interact-shared/logging` process logger with bounded `shopId`, code and outcome. Do not introduce generic local logging. Await notification; never use `.catch(() => {})`, catch→success, fire-and-forget or false `deferred` for PostgreSQL/Redis/formatter errors. Unknown failures are logged safely and rethrown.
- No first recovery row, attempt, outbound or credit may be created **as a consequence of a denied admission**. The adapter itself has no authority to create any of them.

## Work Items

- [ ] Read the merged BG005 contracts/formatter/service, BG003 `onDeniedAdmission` seam, BG001 candidate store and existing merchant Support convention.
- [ ] Implement the Woo-only adapter/factory and bounded provenance-checked optional checkout context resolver without altering accepted common formatter/writer.
- [ ] Implement exhaustive R1 mapping, strict R2 inputs and awaited notifier delegation.
- [ ] Add focused unit tests with injected notifier/candidate/lookup fakes, plus integration coverage with a real shop-scoped Support thread where a test DB is available.
- [ ] Validate exception propagation, shared structured logs and zero extra side effects; leave workers for ARCH-048-BG005.

## Interfaces / Contracts

**Consumes:** `WooDeniedAdmission` and `WooRecoveryAdmissionDependencies.onDeniedAdmission` from `ARCH-048-BACKGROUND-003`; `WooCandidateManager`/accepted Woo candidate snapshot from `ARCH-048-BACKGROUND-001`/BG006; `RecoveryConsentMerchantNotifier`, `RecoveryConsentNoticeInput` and formatter from completed `ARCH-046-BACKGROUND-005`; exact recipient consent and local STOP services from `ARCH-046-BACKGROUND-001`/`ARCH-045-BACKGROUND-005` are policy dependencies, not new calls by the adapter.

**Produces:** an injectable, awaited `WooDeniedAdmissionNotifier`. `ARCH-048-BACKGROUND-005` supplies it to the BG003 admission composition; no BullMQ worker changes here.

## Dependencies

- `ARCH-046-BACKGROUND-001`
- `ARCH-045-BACKGROUND-005`
- `ARCH-048-BACKGROUND-003`
- `ARCH-046-BACKGROUND-005`

All were Complete in the uploaded 2026-10-25 13:36 snapshot.

## Enables

- `ARCH-046-BACKGROUND-004`
- `ARCH-048-BACKGROUND-005`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] One awaited shared-notifier invocation per qualifying R1 denial; STOP, technical deferral and all excluded reasons create **no** consent notice.
- [ ] Correct `WOOCOMMERCE`/`CREATE_FIRST_RECOVERY`/reason inputs; two identical denied events create at most one Support SYSTEM message using the **accepted** canonical source key.
- [ ] Correct, shop-provenanced optional contact, basket currency/total, item count and activity fields where available; missing snapshot leaves readable, truthful notice, not an opaque checkout hash or fabricated customer.
- [ ] Failures in candidate lookup, notification persistence or injected notifier reject and remain retryable; unexpected exceptions are not silently consumed.
- [ ] No duplicate writer, no source-key compatibility shim, no new recovery, attempt, send, bill or worker edit; Shopify notifier regression tests stay green.

## Validation

- [ ] Unit matrix for every R1 reason, absent candidate, wrong-shop candidate, invalid optional data, deduplication, and first-committed body.
- [ ] Focused Support/merchant-notice integration with two concurrent matching Woo denial callbacks and shop isolation, where test DB is configured.
- [ ] Fault-injection tests for Redis/DB/notifier exceptions and shared logger sink failure isolation; run repository-declared typecheck and focused unit/integration scripts relevant to modified files.
- [ ] `git diff --check`; Completion Report records tests, exact touched files, worktree isolation and any unavailable validation.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation, set task to `review`, complete the Completion Report with launcher-resolved dedicated parent/implementation worktrees, physical isolation, start-of-attempt sync and task-branch evidence, return to `moda_architect` and **STOP**. Do not begin ARCH-046-BG004 or ARCH-048-BG005.

## Implementation Notes

Only the Woo adapter and its focused tests are implementation-owned here. The accepted notifier and admission service are read-only dependencies. If the available accepted candidate API cannot provide a requested optional field, omit that field rather than inventing a persistence table or widening the BG003 callback without architect review. Use the canonical launcher and the repository's actual scripts; do not modify `docs/decisions/**/_index.md` during this session.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task definition only.

### Deviations

None.

### Assumptions

This review uses the 25 October 13:36 snapshot; check the actual task worktree and dependency versions on claim.

### Unresolved Issues

None known that blocks definition eligibility. The event-only Woo design cannot detect events never delivered to Moda.

### Architectural Concerns

Report interface or tenant-provenance gaps to the architect; do not bypass source validation.

## Architect Review

### Review Status

Pending.

### Review Notes

Architect has verified the four prerequisites and accepted BG003 callback are present in the supplied snapshot; this is a readiness decision, **not** acceptance of BG002 implementation.

### Reviewed Files

BG003 admission service, merged BG005 notifier contract/service/formatter, Woo pending candidate contract and BG002 task definition.

### Validation Reviewed

Static code/task inspection only; no BG002 runtime tests yet.

### Architecture Conformance

Defined scope and contracts conform to ARCH-046/048 consent and service-ownership boundaries; implementation is pending.

### Follow-up

ARCH-046-BG004 becomes eligible once this task is accepted Complete.

## Execution Ownership Amendment

- Date: 2026-10-25
- Change: The developer explicitly invoked `/moda_developer_create` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_background`, coordinator, dependencies, task scope, and acceptance criteria.
- Claim state: This amendment does not claim an implementation attempt; the canonical launcher records the claim after dependency and worktree preparation.
