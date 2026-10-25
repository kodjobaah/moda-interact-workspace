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
status: review
priority: 35
executor: developer
claimed_at: 2026-10-25T14:03:34Z
attempt: 1
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

**Review handoff (25 October 2026): Developer-executed Attempt 1 submitted for architectural review.** The current parent task records a developer claim at `2026-10-25T14:03:34Z` (`/moda_developer_create`), and the user demonstrated the dedicated parent task directory on branch `task/ARCH-046-BACKGROUND-002`, tracking its origin branch. The Woo adapter and two new tests were committed and pushed in `moda-interact-background` as `9b94c6d`; focused unit tests (42/42), real PostgreSQL integration tests (5/5), and TypeScript typecheck passed. The user has not supplied the launcher preparation packet or direct Git worktree mapping/start-of-attempt synchronization and recursive submodule evidence. Record those as unverified for the reviewer. The task remains subject to architectural review and the explicit developer completion decision; no acceptance or completion is claimed.

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

- [x] Read the merged BG005 contracts/formatter/service, BG003 `onDeniedAdmission` seam, BG001 candidate store and existing merchant Support convention.
- [x] Implement the Woo-only adapter/factory and bounded provenance-checked optional checkout context resolver without altering accepted common formatter/writer.
- [x] Implement exhaustive R1 mapping, strict R2 inputs and awaited notifier delegation.
- [x] Add focused unit tests with injected notifier/candidate/lookup fakes, plus integration coverage with a real shop-scoped Support thread where a test DB is available.
- [x] Validate exception propagation, shared structured logs and zero extra side effects; leave workers for ARCH-048-BG005.

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

- [x] One awaited shared-notifier invocation per qualifying R1 denial; STOP, technical deferral and all excluded reasons create **no** consent notice.
- [x] Correct `WOOCOMMERCE`/`CREATE_FIRST_RECOVERY`/reason inputs; two identical denied events create at most one Support SYSTEM message using the **accepted** canonical source key.
- [x] Correct, shop-provenanced optional contact, basket currency/total, item count and activity fields where available; missing snapshot leaves readable, truthful notice, not an opaque checkout hash or fabricated customer.
- [x] Failures in candidate lookup, notification persistence or injected notifier reject and remain retryable; unexpected exceptions are not silently consumed.
- [x] No duplicate writer, no source-key compatibility shim, no new recovery, attempt, send, bill or worker edit; Shopify notifier regression tests stay green.

## Validation

- [x] Unit matrix for every R1 reason, absent candidate, wrong-shop candidate, invalid optional data, deduplication, and first-committed body.
- [x] Focused Support/merchant-notice integration with two concurrent matching Woo denial callbacks and shop isolation, where test DB is configured.
- [x] Fault-injection tests for Redis/DB/notifier exceptions and shared logger sink failure isolation; run repository-declared typecheck and focused unit/integration scripts relevant to modified files.
- [x] `git diff --check` after patch application and `git diff --cached --check` before commit; Completion Report records exact changed files and supplied validation results.
**Review-provenance item (unverified):** The launcher's paired-worktree mapping, start-of-attempt synchronization and recursive submodule preparation packet were not supplied. The parent branch and developer claim are recorded in the uploaded task snapshot; the updated parent task report still needs to be committed and pushed. This is disclosed for architectural review, not represented as an executed validation.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation, set task to `review`, complete the Completion Report with launcher-resolved dedicated parent/implementation worktrees, physical isolation, start-of-attempt sync and task-branch evidence, return to `moda_architect` and **STOP**. Do not begin ARCH-046-BG004 or ARCH-048-BG005.

## Implementation Notes

Only the Woo adapter and its focused tests are implementation-owned here. The accepted notifier and admission service are read-only dependencies. If the available accepted candidate API cannot provide a requested optional field, omit that field rather than inventing a persistence table or widening the BG003 callback without architect review. Use the canonical launcher and the repository's actual scripts; do not modify `docs/decisions/**/_index.md` during this session.

## Completion Report

### Status

**Ready for Architectural Review — developer-executed Attempt 1, implementation committed and pushed on 25 October 2026.** The current parent task shows an active developer claim and the developer supplied implementation validation and publication evidence. The reviewer should inspect the actual commit and any outstanding launcher/synchronization evidence. There is no accepted architect implementation review or explicit developer completion decision yet.

### Files Changed

Implementation repository: `moda-interact-background`, commit `9b94c6d` (`feat(arch-046-background-002)`), branch `task/ARCH-046-BACKGROUND-002`, confirmed pushed to `origin/task/ARCH-046-BACKGROUND-002`.

All three implementation paths were **added** (585 insertions total):

- `src/services/woocommerce-recovery/woo-recovery-consent-notice.adapter.ts`
- `tests/unit/services/woocommerce-recovery/woo-recovery-consent-notice.adapter.test.ts`
- `tests/integration/woo-recovery-consent-notice.integration.test.ts`

No accepted shared service/formatter, admission service, worker composition, schema or `_index.md` source files are included in that implementation commit.

### Work Completed

- Implemented `createWooRecoveryConsentDeniedAdmissionNotifier`, an injectable, awaited callback compatible with `WooRecoveryAdmissionDependencies.onDeniedAdmission`.
- Implemented explicit exhaustive mapping of the 13 existing `WooAdmissionDenialReason` variants: six qualifying cases map to the canonical shared notice reasons; STOP/no-contact, consent-changed and other non-consent denial cases are excluded. Unknown future reasons fail visibly.
- Reused `RecoveryConsentMerchantNotifier.notify` with `platform: WOOCOMMERCE` and `blockedOperation: CREATE_FIRST_RECOVERY`; no new merchant Support writer, formatter, source-key scheme or database table was introduced.
- Looked up optional context through the injected accepted Woo candidate reader using `(shopId, checkoutToken)`; validated source, tenant, checkout, event and activity evidence before projection. Omitted an unverified contact, missing/invalid basket attributes and a merchant-visible reference that the candidate contract does not supply.
- Used the shared structured logger with bounded diagnostic fields. Candidate-store, notifier/persistence, malformed-input and unexpected-notifier-outcome failures propagate; a logger sink failure cannot convert a failed operation into success.
- Added 27 Woo adapter unit tests and two Woo PostgreSQL integration tests; ran the existing shared merchant-notice unit and database integration suites as regressions. BullMQ worker wiring remains assigned to `ARCH-048-BACKGROUND-005`.

### Validation Results

Evidence: developer-supplied terminal records `typescript(20261025-145026)`, `typescript(20261025-145457)` and `typescript(20261025-150215)`.

- **PASS — focused units:** `npm test -- tests/unit/services/woocommerce-recovery/woo-recovery-consent-notice.adapter.test.ts tests/unit/services/checkout-recovery/recovery-consent-merchant-notice.service.test.ts tests/unit/services/checkout-recovery/recovery-consent-merchant-notice.formatter.test.ts` — **3 files, 42/42 tests** (Woo adapter 27, shared service 8, formatter 7).
- **PASS — real PostgreSQL integration:** `npm run test:integration -- tests/integration/woo-recovery-consent-notice.integration.test.ts tests/integration/recovery-consent-merchant-notice.integration.test.ts` — **2 files, 5/5 tests** (Woo 2, shared notifier 3). The same five integration tests passed again in a separate run. Coverage includes concurrent duplicate callbacks, shop isolation, immutable first-committed body and transactional write failure/retry.
- **PASS — typecheck:** `npx tsc --noEmit && echo "TypeScript typecheck PASS"` printed `TypeScript typecheck PASS`.
- **PASS — patch and staged diff checks:** `git apply --check --whitespace=error-all`, `git apply --whitespace=error-all`, `git diff --check`, and `git diff --cached --check` completed without reported errors before commit.
- **PASS — implementation version control:** commit `9b94c6d` created with exactly three new files; `git push -u origin task/ARCH-046-BACKGROUND-002` succeeded against `moda-interact-background.git`.
- **RECORDED — developer claim:** current parent task YAML has `execution_mode: developer`, `completion_mode: developer`, `executor: developer`, `claimed_at: 2026-10-25T14:03:34Z`, `attempt: 1`, and an explicit Execution Ownership Amendment for `/moda_developer_create`.
- **RECORDED — dedicated task locations/branches:** earlier terminal records show the implementation task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-046-BACKGROUND-002` on the correct task branch; the latest developer command shows the parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-046-BACKGROUND-002` on `task/ARCH-046-BACKGROUND-002`, clean and tracking `origin/task/ARCH-046-BACKGROUND-002`. The ZIP contains that currently claimed parent task file.
- **NOT VERIFIED — preparation/isolation provenance:** the screenshots/logs do not provide the launcher-resolved Git-common-dir/mapping, start-of-attempt fetch/merge synchronization, or recursive implementation submodule status. Existence of plausible paths alone does not prove full preparation-policy compliance; the reviewer may request this evidence.
- **PENDING — parent review-report publication:** the existing parent claim is recorded in the supplied task worktree; this rebased review-report patch has not yet been committed/pushed to the parent branch.
- **NOT RUN / NOT SHOWN:** broad repository test suite, separate Shopify consumer end-to-end suite and cross-repository system tests. The accepted shared notifier's unit and PostgreSQL regression tests **did** pass; ARCH-046 system tests remain separate.

### Deviations

The task's developer ownership amendment and claim were already materialised in the supplied parent worktree; `execution_mode: developer` and `completion_mode: developer` must be preserved. The implementation was applied from the supplied patch, tested, committed and pushed manually within the matching implementation task branch. The available logs do not independently verify all launcher preparation/synchronization steps; these are disclosed rather than treated as passed. No implementation-scope deviations were identified in the three-file commit.

### Assumptions

- The **latest uploaded parent worktree snapshot** (not the earlier unclaimed snapshot) is the source for this review-report patch. It already contains the developer claim, Attempt 1, and the execution-ownership amendment; the separately uploaded terminal record confirms implementation commit `9b94c6d`.
- The task's four prerequisites were recorded Complete when execution was prepared, but current remote dependency metadata and the actual launcher preparation packet were not independently checked here.
- Existing `RecoveryConsentMerchantNoticeService` is the accepted canonical implementation from ARCH-046-BACKGROUND-005; ARCH-048-BACKGROUND-005 remains responsible for binding the adapter to runtime admission workers.

### Unresolved Issues

- Obtain the launcher-resolved Git worktree mapping, start-of-attempt synchronization, and recursive submodule preparation evidence if the reviewer requests it. The developer claim itself **is recorded** in the parent task; dedicated directory names/branches are visible, but not sufficient alone to prove full physical isolation and preparation.
- Commit and push this updated task file on the **already-claimed parent** workspace `task/ARCH-046-BACKGROUND-002` branch, without staging the `moda-interact-background` submodule pointer. Retain implementation commit `9b94c6d` on its separate branch; do not merge either branch for submission.
- Broad Shopify consumer and integrated system-test results are not provided; the existing shared notifier regression tests passed, and integration with the worker remains intentionally assigned to ARCH-048-BACKGROUND-005.

### Architectural Concerns

No new cross-repository contract, database schema, send or charging behaviour is introduced by the adapter. The candidate store's accepted payload does not provide a vetted merchant-facing checkout reference, so that optional field is omitted. The existing `## Architect Review` section below is a **pre-implementation readiness review** and is deliberately unchanged; only the authorized reviewer can assess acceptance. With `completion_mode: developer`, an accepted review still requires an explicit developer completion decision before downstream dependencies become Complete.

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
