---
id: ARCH-048-WOOCOMMERCE-003
architecture_id: ARCH-048
title: Harden checkout-linked Woo paid and cancellation event coverage
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 26
executor: developer
claimed_at: '2026-10-27T11:04:41Z'
attempt: 3
depends_on:
- ARCH-035-WOOCOMMERCE-008
- ARCH-035-API-019
enables:
- ARCH-048-BACKGROUND-003
- ARCH-048-SYSTEM-TEST-001
created: '2026-10-23'
updated: '2026-10-27'
---

# ARCH-048-WOOCOMMERCE-003 — Harden checkout-linked Woo paid and cancellation event coverage

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Attempt 1 was returned to `ready` after an unpaid COD order emitted `ORDER_PAID` at placement. Attempt 2 corrected the payment-evidence predicate and reconciled the integration tests with the modular runner. The real WordPress/Woo HPOS COD and delivery-retry scenarios passed on 27 October 2026; the developer reports that implementation revision `6818b8a` was committed and pushed on `task/ARCH-048-WOOCOMMERCE-003`. This is a **review submission**, not architect acceptance or developer completion. The uploaded task file did not contain an Attempt 2 launcher claim/synchronisation packet; that workflow evidence still requires verification.

After the Attempt 2 workflow review returned the task to `ready`, the canonical developer-create flow claimed Attempt 3 on 27 October 2026. Its route, dependencies, task worktrees and synchronization are recorded in the Attempt 3 claim below. No implementation changes were made as part of claim preparation.

## Objective

Ensure every confirmed checkout-linked order placement, paid transition and cancellation observed by the plugin is reliably published using existing event kinds.

## Context

`OrderLifecycleCapture` attaches `_moda_checkout_key` and currently observes order-processed, `woocommerce_payment_complete` and status change (cancellation) hooks. Some gateways can transition to a paid Woo order state without exercising the specific payment-complete hook. A missed event remains possible even after bounded Action Scheduler retries.

## Scope

- Audit HPOS-compatible status transitions and cover confirmed paid statuses through appropriate WooCommerce-supported hooks without inventing payment when merely placed/on-hold/failed.
- Keep exact `_moda_checkout_key` correlation for Classic and Blocks; no phone/email order matching and no new order identifiers.
- Retain distinct `ORDER_PLACED`, `ORDER_PAID` and `ORDER_CANCELLED` kinds, stable eventId and deduplicated Action Scheduler retry payloads.
- Avoid silently losing known terminal events on transport exhaustion: provide bounded non-PII failure evidence and safe retry/replay handling within existing publisher facilities.
- Handle duplicate payment callbacks, cancellation repeats, and changed status after cancellation without falsely reversing an observed paid outcome.

## Out of Scope

- No new provider status-polling endpoint, local guest-session verification, new Woo database table, unbounded retry loop, new API route or third-party customer-data exposure.

## Requirements

- Do not equate order placement with payment. A placed unpaid order suppresses abandoned-checkout reminders by default, pending any separately approved unpaid-order policy.
- Use existing outbound event contract and Woo order metadata; idempotency and at-least-once transport assumptions remain explicit.
- Exhausted retries are visible operational failures, not evidence that Moda learned the paid outcome.

## Work Items

- [x] Implement paid-state status-transition coverage using Woo order APIs and PHP lifecycle fixtures without treating unpaid COD placement as paid; validate the unpaid COD guard in real WordPress/HPOS guest and customer flows.
- [x] Extend fixture coverage for HPOS-compatible Woo APIs, Classic/Blocks linkage and gateway placed→paid→cancelled/failed/refunded branches.
- [x] Test duplicate callbacks, bounded retry exhaustion and explicit replay retaining the original event ID and checkout correlation.

## Interfaces / Contracts

- Existing `ORDER_PLACED`, `ORDER_PAID`, `ORDER_CANCELLED` payload shape and POST `/v1/woocommerce/activity`; consumer is ARCH-048-BACKGROUND-002.
- The source of truth for payment is the Woo order lifecycle, but Moda is aware only of authenticated events successfully delivered.

## Dependencies

- `ARCH-035-WOOCOMMERCE-008`
- `ARCH-035-API-019`

## Enables

- `ARCH-048-BACKGROUND-003`
- `ARCH-048-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Confirmed paid or cancelled Woo status transitions with `_moda_checkout_key` produce the existing bounded event; a gateway status-only paid transition requires a transaction reference (PHP fixtures and WordPress/HPOS integration).
- [x] No unproven `ORDER_PAID` signal, duplicate terminal action, unscoped order linkage or merchant WordPress checkout-reading route is emitted (real guest/customer COD-before-payment, confirmed-payment, cancellation, duplicate and replay scenarios passed).
- [x] Bounded retry exhaustion produces explicit Action Scheduler failure and privacy-safe diagnostics rather than being counted as successful delivery (fixture-verified).

## Validation

- [x] `npm run test:php`: **190 tests, 1,434 assertions, 0 failures** in the developer's 26 October Attempt 2 log; this preceded the final checkout-test-only commit, and PHPUnit was not rerun in this review environment (missing PHP extensions).
- [x] `WP_ENV_PORT=8899 npm run test:integration:wordpress`: **passed** on 27 October against the `ARCH-048-WOOCOMMERCE-003` plugin, including guest/customer COD unpaid guards, confirmed paid transitions, transaction-backed status-only payment, cancellation, replay, 503 retries, HPOS, and successful environment cleanup.
- [x] `npm run build`: passed in the developer's 26 October Attempt 2 log, including strict 20-locale verification; webpack reported non-fatal performance warnings.
- [x] `composer lint`: passed in the developer's 26 October Attempt 2 log. PHP syntax checks also passed against the uploaded final snapshot. A final implementation-branch `git diff --check` after `6818b8a` was not separately shown.
- [x] `node --test tests/integration/*.test.mjs tests/integration/scenarios/*.test.mjs tests/i18n/*.test.mjs`: **65/65 passed** against the supplied final snapshot in the review-preparation environment, including 8/8 checkout Action Scheduler tests.
- [ ] `npm run test:js`: no complete rerun supplied after the final implementation commit; the earlier run had **456 passed, 1 failed** in unrelated `tests/js/recovery-human-conversation.test.js` (ARCH-040; `never sends twice on pending click; ambiguous retry reuses the same key`). Record as an unrelated previously reproduced failure, not as a passing suite.

## Stop Condition

After only this task's work, criteria and required validation, complete the Completion Report with the launcher-resolved dedicated parent and implementation worktree paths, isolation, start-of-attempt synchronisation and repository revision evidence. Change to `review`, return to `moda_architect` and **STOP**. Do not start dependent work. Superseded tasks must not be claimed.

## Implementation Notes

- Do not promise detection of a completely lost event; ARCH-048 explicitly acknowledges that limitation without provider lookup.

- Use `/moda-task` preparation with the real developer workspace before code execution. Do not treat the snapshot as a Git branch; do not edit any `docs/decisions/**/_index.md` during this architecture session. Validate actual repository scripts rather than guessing commands. Respect assigned repository and task-document ownership.

## Completion Report

### Status

**In Progress — Developer Attempt 3.** Attempt 2 was returned for missing canonical claim/preparation evidence. The developer-create flow has now claimed Attempt 3, synchronized both canonical task worktrees, verified both dependencies complete, and published this claim on the parent task branch. The existing implementation remains at published commit `6818b8a`; no feature changes have been made during preparation.

### Files Changed

Implementation repository `moda-interact-woocommerce`, over Attempt 1 and Attempt 2:

- `includes/Checkout/CheckoutActivityPublisher.php` — Attempt 1 delivery exhaustion/replay handling (unchanged by the latest test-only commit).
- `includes/Checkout/OrderLifecycleCapture.php` — payment-evidence predicate corrected in Attempt 2.
- `tests/OrderLifecycleCaptureTest.php` — COD, confirmed-payment, transaction-backed transitions and duplicate-event fixtures.
- `tests/integration/scenarios/order-wordpress.mjs` — modular real WordPress/HPOS order lifecycle regression.
- `tests/integration/scenarios/checkout-wordpress.mjs` — event-specific Action Scheduler checkout delivery/retry assertions.
- `tests/integration/scenarios/checkout-actions.test.mjs` — deterministic action selection and 503 event-identity tests.

Attempt 1 used the former `tests/integration/order-wordpress.mjs` path before the modular integration-test reorganisation. The final snapshot uses the `tests/integration/scenarios/` structure. Commit history reported by the developer: `30360d3` (Attempt 1), `0af46df` (Attempt 2 payment correction) and `6818b8a` (final two-file checkout retry test change).

Parent workspace: **this task definition and Completion Report only**. No architecture index, parent architecture, application code or implementation gitlink is modified by the review-documentation patch.

### Work Completed

- Retained the WooCommerce paid-status and `woocommerce_payment_complete` observers while requiring evidence beyond the paid-labelled order status: a payment-complete callback or a non-empty gateway transaction reference, together with the paid-state checks. COD `processing` and status-derived `date_paid` alone do not constitute payment.
- Preserved exact `_moda_checkout_key` correlation, the existing `ORDER_PLACED`, `ORDER_PAID` and `ORDER_CANCELLED` contract, event identity and callback deduplication. No new Woo customer lookup or merchant-side API route was added.
- Retained bounded retry exhaustion, diagnostic failure visibility, installation-bound replay and the original event ID in replay/retry payloads.
- Added real WordPress/HPOS regression coverage for unpaid guest/customer COD orders, later confirmed payment, transaction-backed status-only gateways, cancellation, replay and HTTP 503 handling.
- Reconciled tests with the modular scenario layout and removed nondeterministic generic Action Scheduler batch selection from the checkout retry assertion: the test runs the **selected persisted action ID** and verifies that the exact outage event received HTTP 503 and its attempt-2 retry retained the original event identity.
- Developer committed/pushed the final two-file correction as `6818b8a` to `origin/task/ARCH-048-WOOCOMMERCE-003`, moving the remote branch from `0af46df` to `6818b8a` (developer-supplied Git output).

### Validation Results

- **Developer PHPUnit (26 October, Attempt 2):** `npm run test:php` passed **190 tests, 1,434 assertions**. This predates the final two-file integration-test commit; no production PHP files changed in that final commit, based on the developer's commit summary. A fresh PHPUnit rerun is not claimed.
- **Developer build/lint (26 October, Attempt 2):** `npm run build` and `composer lint` passed; build reported warnings about bundle size, not build errors.
- **Developer real WordPress integration (27 October):** `WP_ENV_PORT=8899 npm run test:integration:wordpress` completed on the WOOCOMMERCE-003 worktree. The runner explicitly reported `ARCH-048 Order guest` and `ARCH-048 Order customer` COD/unpaid, confirmed-payment, status-only gateway, cancellation, replay, 503 and HPOS **PASS**. Guest/customer checkout 503/retry scenarios also passed, and the disposable WordPress environment stopped cleanly. This resolves the Attempt 1 COD failure and subsequent nondeterministic checkout retry assertion seen in earlier logs.
- **Snapshot Node verification (27 October, review preparation):** `node --test tests/integration/*.test.mjs tests/integration/scenarios/*.test.mjs tests/i18n/*.test.mjs` passed **65/65**; the focused checkout Action Scheduler tests passed **8/8**. JavaScript syntax and changed PHP-file syntax checks passed against the uploaded snapshot.
- **PHPUnit review-environment limit:** `php vendor/bin/phpunit` was unavailable in this container because `dom`, `mbstring` and `xmlwriter` extensions are missing. This is not recorded as a code failure; rely on the developer-run PHPUnit log above.
- **Full JS limitation:** the earlier `npm run test:js` run had **456 passing and one separately reproduced ARCH-040 failure** in `recovery-human-conversation.test.js`. No final full-suite rerun is evidenced; the Node integration/i18n subset is passing. No unrelated ARCH-040 code was changed here.
- **Git publication:** user-provided terminal output confirms implementation commit `6818b8a` and push `0af46df..6818b8a` to the implementation task branch. The snapshot is a Git-metadata-free archive; remote commit integrity and the final implementation-branch diff must be inspected by the authorised reviewer.
- **Worktree evidence:** the historical Attempt 1 ownership amendment below documents the dedicated parent/implementation worktrees and initial synchronisation. The supplied current task file remained `ready` at `attempt: 1`, so an Attempt 2 launcher claim, `claimed_at` time, start-of-attempt synchronisation and preparation packet **cannot be verified from this archive**. This retrospective report does not invent that evidence. The reviewing developer/architect should reconcile the actual task-workflow record before accepting.
- **Beyond task scope:** no external commerce/API/background end-to-end system test or production delivery trace is claimed.

### Deviations

- The developer applied external patch deliverables under the developer-execution workflow rather than an assigned repository agent writing all code directly. `assigned_agent: moda_woocommerce`, `execution_mode: developer` and `completion_mode: developer` are preserved.
- The integration tests moved from the legacy flat paths to `tests/integration/scenarios/` during branch reconciliation; the final test correction is scoped to the modular layout.
- The uploaded parent task definition does not show the Attempt 2 claim transition. Recording `attempt: 2` and `status: review` in this review-submission patch reconciles the reported completed work for review; it does **not** establish that `/moda_developer_create` ran or supply its launcher packet.

### Assumptions

- The developer's terminal output correctly identifies `6818b8a` as the final pushed implementation commit; this report has not fetched GitHub or inspected remote Git history independently.
- The uploaded `(5)` workspace archive represents the post-correction implementation source used for snapshot Node/syntax checks; the independent WordPress run is evidenced by the separately supplied terminal log.
- The existing `/v1/woocommerce/activity` contract remains unchanged. A gateway supplying neither a payment-complete callback nor a transaction reference cannot safely be classified as confirmed-paid from status alone.

### Unresolved Issues

- **Review workflow evidence:** verify the canonical Attempt 2 `/moda_developer_create` claim and both worktrees' start-of-attempt synchronisation/physical isolation evidence, or explicitly record the workflow non-conformance and its remediation. Do not fabricate a `claimed_at` timestamp.
- **Validation limitation:** the full JS suite's previously reproduced ARCH-040 failure remains outside this task; no final full-suite rerun was supplied. The final implementation-branch diff check and remote commit content should be verified during review.
- No reproduced task-scoped functional blocker remains in the supplied final real WordPress/HPOS integration output.

### Architectural Concerns

- A payment that provides neither Woo's explicit completion callback nor a durable gateway transaction reference will not produce `ORDER_PAID` solely because the order has a paid-labelled status. This is deliberate false-positive prevention, and any uncovered gateway semantics require separate architecture review.
- Bounded delivery retries and explicit replay do not recover an event that was never captured or enqueued. Operational replay remains an internal facility; caller authorisation should be assessed during integrated validation.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.

## Developer Execution Ownership Amendment (Attempt 1)

- Invocation: `/moda_developer_create ARCH-048-WOOCOMMERCE-003` explicitly requested developer execution. `assigned_agent: moda_woocommerce` is unchanged; execution and completion modes are now `developer`.
- Claim: `status: in_progress`, `executor: developer`, `claimed_at: 2026-10-26T14:25:27Z`, `attempt: 1`.
- Dependency verification: `ARCH-035-WOOCOMMERCE-008` and `ARCH-035-API-019` both resolved `complete` before claim.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-WOOCOMMERCE-003`, branch `task/ARCH-048-WOOCOMMERCE-003`, clean at start revision `2624d6445e6d642568d521d18f3e277ea629950e`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-WOOCOMMERCE-003`, branch `task/ARCH-048-WOOCOMMERCE-003`, clean at start revision `fe0c9de7446082e276b589fc58756ea1ac9fb03a`.
- Synchronization: fetched `origin --prune` in both task worktrees. No remote task branch existed at preparation; both task branches start at current `origin/main`, which is an ancestor of each worktree HEAD. At preparation, no implementation changes had been made in this attempt.

## Developer Self-Review - Changes Requested (Attempt 1)

- Review result: Changes Requested. Attempt 1 does not satisfy the no-unproven-payment acceptance criterion.
- Blocking evidence: `npm run test:integration:wordpress` ran in the isolated disposable WordPress/Woo environment and failed at the guest-order assertion in `tests/integration/order-wordpress.mjs:40`: one `ORDER_PAID` existed immediately after checkout placement using the `cod` payment method; expected zero. The harness stopped/cleaned the disposable environment after failure.
- Required correction: adjust Woo payment evidence so status alone plus `is_paid()` cannot turn an unpaid COD placement into `ORDER_PAID`, while still detecting confirmed gateway paid-status transitions that omit `woocommerce_payment_complete`. Add/retain an integration assertion for COD placement producing only `ORDER_PLACED`, and a later genuinely confirmed paid transition producing one `ORDER_PAID`.
- Required validation: rerun `npm run test:php`, `npm run test:integration:wordpress`, `npm run build`, `composer lint`, `git diff --check`, and the task-scoped JS integration checks. The existing full `npm run test:js` failure is ARCH-040 and was reproduced in isolation; report it, but do not modify unrelated code absent a task-scoped cause.
- Other validation: PHP suite 187/187 passed; build, Composer PHP lint, and implementation diff whitespace check passed. The full JS suite reported 456 passed and one unrelated ARCH-040 failure. No implementation changes were made during this review.
- State transition: `review` -> `ready`; `executor: null`, `claimed_at: null`, `attempt: 1` unchanged. The next `/moda_developer_create ARCH-048-WOOCOMMERCE-003` claim must increment to Attempt 2.

## Developer Attempt 2 Review Submission Evidence (2026-10-27)

- **Submission state:** This is a retrospective documentation handoff from the supplied parent task snapshot (`status: ready`, `attempt: 1`) to an Attempt 2 review submission (`status: review`, `attempt: 2`, `executor: null`, `claimed_at: null`). It must not be represented as proof that an Attempt 2 launcher claim or start-of-attempt synchronisation occurred.
- **Implementation:** `moda-interact-woocommerce` branch `task/ARCH-048-WOOCOMMERCE-003`; developer reports `0af46df` followed by `6818b8a`, and published push `0af46df..6818b8a`. No integration into `main` is claimed.
- **Physical task paths:** the existing Attempt 1 ownership amendment records the dedicated parent and implementation worktree paths. Their continued use and fresh Attempt 2 synchronisation must be independently verified, not inferred from the archive name or a clean Git status.
- **Functional evidence:** 27 October WordPress/HPOS guest and customer COD false-paid regression plus confirmed-payment/status-only/cancellation/replay/503 checks passed; checkout Action Scheduler retry check passed in the same WOOCOMMERCE-003 runner.
- **Validation caveats:** PHP suite 190/190 and build/lint were evidenced earlier in Attempt 2; snapshot Node tests 65/65 passed; full JS rerun and Attempt 2 launcher claim packet were not supplied. Retain the separate ARCH-040 failure in review context.
- **Review authority:** the `## Architect Review` section remains unchanged. `completion_mode: developer` requires a durable passing review followed by the developer's explicit `/moda_developer_update ARCH-048-WOOCOMMERCE-003 complete` decision. Downstream tasks must not be marked newly Ready from this submission alone.

## Developer Self-Review - Changes Requested (Attempt 2, 2026-10-27)

- Outcome: **changes requested** because Attempt 2 was submitted without a verifiable canonical `/moda_developer_create` claim and start-of-attempt synchronization/preparation packet. The task report itself identifies this as unverified, and reachable parent task history contains no Attempt 2 claim record. Do not treat the review-submission commit or implementation commits as a substitute for the claim.
- Implementation assessment: implementation branch `task/ARCH-048-WOOCOMMERCE-003` is clean and published at `6818b8a`, equal to `origin/task/ARCH-048-WOOCOMMERCE-003`; `git diff --check origin/main...HEAD` passes. The reported WordPress/HPOS integration evidence covers the Attempt 1 COD defect and checkout retry correction. No task-scoped functional defect is established by this review.
- Required correction: use `/moda_developer_create ARCH-048-WOOCOMMERCE-003` to claim the next canonical attempt. Record the launcher-resolved parent and implementation paths, dependency check, synchronized branch heads, clean-state evidence, recursive submodule state if applicable, and claim commit on the parent task branch. Then rerun the task-scoped validation required by the task, including PHP tests if the environment supports them; retain the unrelated ARCH-040 JavaScript failure as a separately identified existing failure rather than claiming the full suite passes.
- Transition: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 2`. Attempt 2 is preserved; the next valid developer claim increments exactly once to Attempt 3. No task branch was merged to `main`.

## Developer Execution Claim (Attempt 3)

- Claim: `status: in_progress`, `executor: developer`, `claimed_at: 2026-10-27T11:04:41Z`, `attempt: 3`; `assigned_agent: moda_woocommerce` and `completion_mode: developer` are unchanged.
- Canonical route: `python3 scripts/start-agent-task.py ARCH-048-WOOCOMMERCE-003 --route-only --json` resolved workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`, repository `moda-interact-woocommerce`, task branch `task/ARCH-048-WOOCOMMERCE-003`, parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-WOOCOMMERCE-003`, and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-WOOCOMMERCE-003`.
- Dependencies checked before claim: `ARCH-035-WOOCOMMERCE-008` and `ARCH-035-API-019` are both `complete` in the canonical task records.
- Parent synchronization: fetched `origin --prune`; the clean task branch was at `b079ae4f2479caca3abaee8351f10990d91febab`, equal to `origin/task/ARCH-048-WOOCOMMERCE-003`. Current `origin/main` was `293ef582e731c4c578815985e9a12f0d93b64bcf` and was not an ancestor, so it was merged into the task branch without conflicts. The synchronized parent HEAD is `f9326880f2e92848e4f346885f58ffa7952dc676`; `origin/main` is now an ancestor. No task branch was merged into `main`.
- Implementation synchronization: fetched `origin --prune`; implementation HEAD `6818b8a62fd8ce2f558ce6e554569ef5174aeddf` equals `origin/task/ARCH-048-WOOCOMMERCE-003`. `origin/main` is `4f2d0db19931e14127a8399b3e4629ede3d2e280` and is already an ancestor; no merge was needed. The worktree was clean before the claim.
- Physical isolation: both canonical directories were registered to the task branch in their respective repositories and clean before preparation; neither shared/default checkout was used for implementation. `git submodule status --recursive` returned no entries for the WooCommerce implementation repository.
- Attempt 3 begins with the existing implementation at `6818b8a`; no source or test changes were made during claim preparation. The task is handed back for implementation and the task-scoped validation listed above.
