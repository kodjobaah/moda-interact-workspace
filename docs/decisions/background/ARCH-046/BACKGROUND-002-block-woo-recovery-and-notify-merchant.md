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
status: complete
priority: 35
executor: null
claimed_at: null
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

**Developer completion (25 October 2026): Attempt 1 passed self-review and was explicitly accepted by the developer.** Implementation commit `9b94c6d` and parent task/report commits are published on their mirrored task branches; focused unit tests (42/42), real PostgreSQL integration tests (5/5), and TypeScript typecheck passed. The historical start-of-attempt preparation packet remains unavailable, as documented below; current worktree mapping and implementation synchronization/submodule evidence were verified at review. No branch was merged to `main`.

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
**Review-provenance caveat:** The historical start-of-attempt launcher mapping/synchronization/submodule preparation packet was not supplied. Current dedicated worktree mapping, clean task-branch publication, implementation synchronization and exact database gitlink were verified during review. This caveat was assessed and accepted as non-blocking for this bounded adapter task.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation, set task to `review`, complete the Completion Report with launcher-resolved dedicated parent/implementation worktrees, physical isolation, start-of-attempt sync and task-branch evidence, return to `moda_architect` and **STOP**. Do not begin ARCH-046-BG004 or ARCH-048-BG005.

## Implementation Notes

Only the Woo adapter and its focused tests are implementation-owned here. The accepted notifier and admission service are read-only dependencies. If the available accepted candidate API cannot provide a requested optional field, omit that field rather than inventing a persistence table or widening the BG003 callback without architect review. Use the canonical launcher and the repository's actual scripts; do not modify `docs/decisions/**/_index.md` during this session.

## Completion Report

### Status

**Completed — developer-executed Attempt 1, explicitly accepted on 25 October 2026.** The developer claim at `2026-10-25T14:03:34Z` is historical and cleared. Implementation and validation evidence are published; the historical start-of-attempt preparation-packet gap is disclosed and was accepted as non-blocking. No merge to `main` was performed.

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
- **PASS — independent review rerun (25 October 2026):** from the canonical implementation task worktree, the focused unit selection passed **3 files / 42 tests**, the focused real PostgreSQL integration selection passed **2 files / 5 tests**, and `npx tsc --noEmit` passed.
- **PASS — patch and staged diff checks:** `git apply --check --whitespace=error-all`, `git apply --whitespace=error-all`, `git diff --check`, and `git diff --cached --check` completed without reported errors before commit.
- **PASS — implementation version control:** commit `9b94c6d` created with exactly three new files; `git push -u origin task/ARCH-046-BACKGROUND-002` succeeded against `moda-interact-background.git`.
- **RECORDED — developer claim:** Attempt 1 was claimed at `2026-10-25T14:03:34Z`; parent task claim commit `1674be4b4` records it. The claim is cleared on review submission (`executor: null`, `claimed_at: null`).
- **VERIFIED — dedicated worktrees at review:** parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-046-BACKGROUND-002` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-046-BACKGROUND-002` are the canonical launcher-resolved paths, registered in Git on `task/ARCH-046-BACKGROUND-002`, clean and tracking their matching origin task branches. Parent review-report HEAD was `506b4ae2bb83b54ecca640059830a8de9b2ab9a6`; implementation HEAD is `9b94c6d38703fe725a351a94b6b8e62110d65be8`.
- **VERIFIED — implementation sync/submodule at review:** implementation HEAD contains `origin/main` at `2e0425c89eee086241b15a39a63894247e498629`; recursive submodule status shows nested `database` at exact gitlink `3f1f50b91c9e93ff9647a3d1d7f6fd46b9b888b9`.
- **NOT VERIFIED — start-of-attempt packet:** the historical launcher Git-common-dir/mapping and fetch/merge/submodule preparation packet was not supplied. At review, current parent `origin/main` (`bba20335696ac988901ccf50eb24e6a3e45ee4fc`) is not an ancestor of the parent task branch. No synchronization merge was performed during this review; reviewer may request the original preparation evidence or separately authorize synchronization.
- **PASS — parent review-report publication:** the parent review report is committed and pushed at `506b4ae2bb83b54ecca640059830a8de9b2ab9a6`, tracking `origin/task/ARCH-046-BACKGROUND-002`.
- **NOT RUN / NOT SHOWN:** broad repository test suite, separate Shopify consumer end-to-end suite and cross-repository system tests. The accepted shared notifier's unit and PostgreSQL regression tests **did** pass; ARCH-046 system tests remain separate.

### Deviations

The task's developer ownership amendment and claim were already materialised in the supplied parent worktree; `execution_mode: developer` and `completion_mode: developer` must be preserved. The implementation was applied from the supplied patch, tested, committed and pushed manually within the matching implementation task branch. The available logs do not independently verify all launcher preparation/synchronization steps; these are disclosed rather than treated as passed. No implementation-scope deviations were identified in the three-file commit.

### Assumptions

- The **latest parent task worktree** is the source for this completion decision. It contains the accepted Attempt 1 review, cleared claim and published review-report commit `506b4ae2`; the implementation task branch contains commit `9b94c6d`.
- The task's four prerequisites were independently resolved as `complete` through the canonical launcher during this review. That current state does not reconstruct the missing historical start-of-attempt preparation packet.
- Existing `RecoveryConsentMerchantNoticeService` is the accepted canonical implementation from ARCH-046-BACKGROUND-005; ARCH-048-BACKGROUND-005 remains responsible for binding the adapter to runtime admission workers.

### Unresolved Issues

- The original start-of-attempt preparation packet remains unavailable; this was accepted as a non-blocking provenance caveat after current worktree and implementation synchronization evidence were verified.
- Broad Shopify consumer and integrated system-test results are not provided; these are outside BG002's adapter scope. Worker integration remains assigned to ARCH-048-BACKGROUND-005.

### Architectural Concerns

No new cross-repository contract, database schema, send or charging behaviour is introduced by the adapter. The candidate store's accepted payload does not provide a vetted merchant-facing checkout reference, so that optional field is omitted. The existing `## Architect Review` section below is a **pre-implementation readiness review** and is deliberately unchanged; the explicit developer completion decision below records final acceptance under `completion_mode: developer`.

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

## Developer Self-Review Passed (Attempt 1)

### Outcome

Attempt 1 passes developer self-review against the scoped Woo first-recovery
denial adapter requirements. The adapter exhaustively maps the current BG003
denial reasons, delegates qualifying notices to the accepted shared notifier,
projects only tenant/checkout-verified candidate context, and propagates lookup
and persistence failures. Focused units, real PostgreSQL integration tests and
TypeScript typecheck passed, including independent review reruns.

### Deviation and Evidence Gap

No implementation-scope deviation was identified. The historical start-of-attempt
launcher preparation packet was not supplied. At review, both dedicated task
worktrees are registered and clean, implementation is synchronized with
`origin/main` and its nested database gitlink is exact, but the parent task branch
does not contain the latest `origin/main` observed during review. This is disclosed
for architect review; no mainline or cross-task merge was performed.

### Completion Boundary

The task was submitted to `moda_architect` with `status: review`. The developer
now explicitly accepts Attempt 1 and sets `status: complete`; `executor` and
`claimed_at` remain null and the attempt number is unchanged.

## Developer Completion Decision (Attempt 1)

On 25 October 2026, the developer explicitly invoked
`/moda_developer_update ARCH-046-BACKGROUND-002 complete` and accepted the
durable passing self-review. All required Work Items, Acceptance Criteria and
focused validations are complete, and the implementation task branch is
committed and pushed. The historical launcher preparation-packet gap remains
disclosed and was accepted as non-blocking; no merge to `main` was required or
performed.

### Dependency Frontier

- `ARCH-046-BACKGROUND-004` is promoted from `pending` to `ready` at Attempt 0:
  its declared dependencies are complete after this decision. Its canonical
  parent task record is published at commit `0a891f3c`; no attempt was claimed
  or started.
- `ARCH-048-BACKGROUND-005` remains `pending`: it still depends on BG004, which
  is ready but not complete.
- `ARCH-046-SYSTEM-TEST-002` remains `blocked` and terminal/manual-gated because
  other declared implementation prerequisites remain incomplete. It was not
  started or promoted solely by this completion.
