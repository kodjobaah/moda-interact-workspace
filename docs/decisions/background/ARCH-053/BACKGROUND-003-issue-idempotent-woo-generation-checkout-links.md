---
id: ARCH-053-BACKGROUND-003
architecture_id: ARCH-053
title: Issue immutable, safe generation-specific Woo resume URLs
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 50
executor: codex
claimed_at: 2026-10-30T16:57:06Z
attempt: 2
depends_on:
- ARCH-053-BACKGROUND-002
- ARCH-048-BACKGROUND-011
enables:
- ARCH-053-SYSTEM-TEST-001
- ARCH-053-SYSTEM-TEST-002
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-053-BACKGROUND-003 — Issue immutable, safe generation-specific Woo resume URLs

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. Materialised in the parent workspace and dependency-ready. Implementation execution has not started; no implementation branch or producer deployment is claimed.

## Objective

Issue immutable, safe generation-specific Woo resume URLs. One bounded outcome in `moda-interact-background` owned by `moda_background`.

## Context

The inspected snapshot is dated 2026-10-30 07:59. ARCH-052 owns dynamic discount discovery and is not a checkout-URL implementation domain. ARCH-048-BACKGROUND-007..011 task files are present, but none has been accepted Complete in this snapshot (007 Ready, 008–011 Pending). This task is **Pending** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

- Modify `src/services/woocommerce-recovery/woo-recovery-admission.service.ts` only for transactional URL creation and `woo-recovery-admission-evidence.ts` or a narrowly owned `woo-recovery-link-issuer.ts` helper; update Woo Background admission/outreach/template regression tests. Consume generation-aware admission already accepted under ARCH-048-BACKGROUND-011; do not reimplement the new generation lifecycle.
- For a **supported, fully persisted** `wooRestoreSnapshot`, resolve active `WooCommerceInstallation.canonicalSiteUrl` from the authoritative shop. Validate HTTPS/public site and hostname equality with `Shop.domain` (support home subpath). Generate 32 cryptographically random bytes to base64url 43-character token and construct `<canonicalSiteUrl>/?moda_interact_resume=1&r=<new-recovery-id>&t=<token>`; insert row with `CheckoutRecovery.checkoutUrl` atomically as part of the existing recovery admission transaction (create row, then update URL within same tx, if generated recovery ID required).
- For a shop and installation that pass the existing admission/consent gates, missing/unsupported snapshot, invalid canonical site or host mismatch permits the otherwise eligible recovery to be admitted with `checkoutUrl:null` and a bounded omission reason. Never fall back to bare `wc_get_checkout_url()` or product-ID `/checkout-link/`; use the established no-link fallback or no-send when a template requires a URL. **A revoked/inactive installation is not a link-omission case: deny recovery admission completely, create no new `CheckoutRecovery` row, URL or status history, and never weaken the existing eligibility/consent gates.**
- Do not regenerate token/URL for duplicate delivery, already-created generation or resend/retry: return existing immutable link; one unique URL per recovery ID/generation. Confirm existing `checkout.url` templating and `trustedHttpsUrl` host gate still accepts the verified URL, and that Meta preparation/redaction does not emit token in logs. Do not activate Woo production sends.

## Out of Scope

No schema migration, Woo WordPress endpoint, API resolver, discount discovery or modification to ARCH-048-BACKGROUND-011 generation orchestration.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- Issuance does not depend on ARCH-052 discount discovery, private Woo provider call, WP transient or extra HMAC key. No network/Redis inside admission transaction; entropy failure is retryable and must not admit a partial row with a phantom URL.
- A new generation receives a different URL and fresh snapshot; the old link remains stored historically but API resolver refuses it immediately once old generation is terminal/superseded. New arrivals can send their independently eligible initial outreach under ARCH-048. **Installation status is authoritative:** revoked/inactive at preflight yields `INSTALLATION_INACTIVE`; revocation after preflight but before the insertion transaction commits is rejected by `confirmCurrentWooConsent()` as `CONSENT_CHANGED`. Neither path may insert a new recovery, issue a link, or create admission history. If an installation is revoked *after* a previously valid admission, preserve historical data, but subsequent link resolution/outreach must fail closed at their owning boundaries.
- Ensure 7-day checkout freshness for URL resolution is consistent with existing Background template freshness. Historical confirmed billing/sends are never altered by link creation.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the launcher preparation evidence. Use the **dedicated, synchronized parent and implementation task worktrees**; do not operate from a shared checkout or claim a branch was pushed without evidence. Implement only the owning repository and assigned task metadata. No unrelated refactors, migrations, agent handoffs or remote pushes to `main`.
- Read the ARCH-053 parent architecture and all dependency tasks before claiming Ready. Any missing contract or incorrect owner is a blocking architect question; do not invent a local parallel schema or silently change another agent's task. System-test tasks must remain terminal.
- Never swallow unexpected errors: Node uses `@modainteract/moda-interact-shared/logging`; PHP uses the existing safe plugin diagnostics (not a competing generic Node logger). Report bounded event codes, ids and outcomes, propagate retryable failures to their owning boundary, omit tokens, full URLs, coupon codes and customer personal data from logs.
- The plugin cannot access PostgreSQL/Redis. The API cannot mutate merchant WordPress cart sessions. Background cannot directly call an unverified merchant endpoint to mint URLs. Do not enable Woo production WhatsApp sending, relax final consent/STOP/order gates, or add cross-generation outreach caps/cooldowns.

## Work Items

- [x] Generate bounded deterministic URL **format** with random per-generation token and canonical site URL.
- [x] Write exactly one URL in generation admission transaction, safe retry and uniqueness conflict handling.
- [x] Test supported/unrestorable, subpath, host mismatch, generation 1→2, duplicate admission, token uniqueness, template bind and zero token logging.

## Interfaces / Contracts

Recovery DB: `CheckoutRecovery.checkoutUrl String?` (existing) and new `wooRestoreSnapshot`. URL params are `moda_interact_resume=1&r=<recoveryId>&t=<43-char-token>`, matching API-002 and WOOCOMMERCE-002. No raw coupon/product/identity data in URL. Confirm every consumer uses stored URL rather than generating another from `wc_get_checkout_url()`.

## Dependencies

- `ARCH-053-BACKGROUND-002` (must be architect-accepted Complete)
- `ARCH-048-BACKGROUND-011` (must be architect-accepted Complete)

## Enables

- `ARCH-053-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Confirm by focused regression tests that a previously revoked installation is denied before admission and a revocation detected by the transaction consent fence is also denied; neither case creates a recovery, URL update or admission history. No runtime code changes are requested if the existing safety gate passes.
- [x] Generate bounded deterministic URL **format** with random per-generation token and canonical site URL.
- [x] Write exactly one URL in generation admission transaction, safe retry and uniqueness conflict handling.
- [x] Test supported/unrestorable, subpath, host mismatch, generation 1→2, duplicate admission, token uniqueness, template bind and zero token logging.
- [x] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [x] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [x] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [ ] Add/run focused revoked-installation regression tests (preflight `INSTALLATION_INACTIVE` and transaction-fence `CONSENT_CHANGED`); verify zero inserts, URL updates and history writes, and no logged bearer token.
- [x] Background admission transaction and URL issuer unit tests, mature job retry and two generation integration
- [x] Template binding/host validation and secret-redaction regression tests
- [x] Package build/typecheck, changed-file lint and `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

**Architect decision (2026-10-30, after Attempt 1):** The earlier scope phrase grouping revoked installations with invalid URL configuration was contradictory. **Do not implement a separate persistence path for revoked installations.** The existing active-installation and transactional consent fences take precedence over URL omission. The implementation described in the Attempt 1 Completion Report is architecturally correct on this point. Reclaim this *same* task as Attempt 2, keep implementation commit `6b6b254` as the code baseline, add only the narrowly scoped regression coverage in the latest Architect Review, rerun task-required validation, update the Completion Report and return `status: review`. Do not redesign the URL, create a new task, modify another repository, activate Woo outbound sending or start enabled system-test tasks.

Dependencies `ARCH-053-BACKGROUND-002` and `ARCH-048-BACKGROUND-011` are Complete in this submitted worktree snapshot, subject to rechecking in the launcher on reclaim. Older historical snapshot descriptions in this task are superseded by the recorded accepted dependency state.

## Completion Report

### Status

Blocked — architect decision required on revoked-installation omission semantics

### Files Changed

Implementation branch `task/ARCH-053-BACKGROUND-003`, commit `6b6b254`:

- `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-admission.service.ts`
- `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-admission-evidence.ts`
- `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-link-issuer.ts`
- `moda-interact-background/tests/unit/services/woocommerce-recovery/woo-recovery-admission.service.test.ts`
- `moda-interact-background/tests/unit/services/woocommerce-recovery/woo-recovery-link-issuer.test.ts`
- `moda-interact-background/tests/unit/services/conversation-wrappers/woo-checkout-link.test.ts`
- `moda-interact-background/tests/integration/woo-recovery-admission.integration.test.ts`
- This task's checklists and Completion Report only.

### Work Completed

Supported snapshots now receive a URL of the form `https://<verified-merchant-host>/<home-subpath>/?moda_interact_resume=1&r=<recovery-id>&t=<43-character-token>`. The token is generated from 32 cryptographically random bytes only after the admission transaction has ruled out an existing generation. The recovery row is created and its URL is written in the same transaction; an update or history failure rolls the transaction back. Duplicate and stale deliveries return the existing recovery without rotating its URL.

Absent/unsupported restore snapshots and invalid or mismatched merchant site settings create a recovery with `checkoutUrl: null` and a bounded omission reason in admission history. Existing consent, STOP, order, candidate watermark and installation eligibility gates remain in place. The existing conversation wrapper binds the URL only when it remains HTTPS on the merchant host and within its seven-day checkout freshness window.

The disposable PostgreSQL/Redis integration test verifies a persisted generation-1 URL survives replay unchanged and a resumed generation 2 receives a distinct URL and its own restoration snapshot. No external HTTP or Redis operation was added inside the transaction.

Implementation commit `6b6b254` was pushed to `origin/task/ARCH-053-BACKGROUND-003`.

Launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-053-BACKGROUND-003` on `task/ARCH-053-BACKGROUND-003`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-053-BACKGROUND-003` on the same task branch. Neither shared checkout nor another task worktree was switched or mutated. Parent remote task branch fast-forwarded `not-needed`, parent `origin/main` incorporated `already-current`; implementation remote task branch fast-forwarded `not-needed`, implementation `origin/main` incorporated `already-current`. Recursive submodule sync/update passed; `database` remained at `af77c594ecbfc78c26d01c0021a090830884bbff`.

### Validation Results

- Focused unit suites: 3 files, 52 tests passed (issuer safety, admission/idempotency and template binding).
- Disposable Postgres/Redis integration suites: 2 files, 8 tests passed, including URL persistence, retry stability and generation 1→2 separation.
- Changed-file ESLint: passed.
- `npm run build` (Prisma Client generation 6.19.3 and TypeScript compilation): passed.
- `git diff --check`: passed.
- Admission logs contain neither URL host nor bearer token. Candidate/watermark and order evidence reads remain outside the transaction.

### Deviations

The launcher marked this execution `rework.required: true` with `previous_attempt: 0`, while the complete task's Architect Review remains Pending with no correction request. No rework checklist was present; the implementation follows the task's scope and acceptance criteria. The Architect Review section was not changed.

### Assumptions

The launcher dependency gate established BACKGROUND-002 and ARCH-048-BACKGROUND-011 as Complete. Their contracts permit storing the URL in the existing `checkoutUrl` field and reusing the admitted generation's immutable restore snapshot.

### Unresolved Issues

The task asks to admit a recovery with `checkoutUrl: null` and an omission reason when the installation is revoked. Current admission rejects inactive/revoked installations before the admission transaction, and the consent fence also rejects a revocation that occurs before commit. Creating a row in that state would require weakening the existing installation/consent gates. The task is blocked pending moda_architect direction on whether the existing safety gate takes precedence or this task should define a separate safe persistence path.

### Architectural Concerns

The revoked-installation requirement conflicts with the current admission invariant that only active installations with current consent can be admitted. No gate was relaxed.

## Architect Review

### Review Status

Changes Requested — architectural blocker resolved; focused validation-only correction, then resubmit the same task for acceptance.

### Review Notes

Attempt 1 reviewed on 2026-10-30. The task's original instruction to admit a revoked installation with `checkoutUrl:null` was incorrect and conflicts with the pre-existing admission/consent invariants. **Architect decision: deny admission entirely for an inactive or revoked Woo installation; do not create a recovery, URL or admission history.** Missing/unsupported restoration data and unsafe canonical-site configuration are URL-omission cases only for an otherwise eligible active installation. No code change or separate revoked-installation persistence mechanism is authorised.

The submitted implementation already performs an early `INSTALLATION_INACTIVE` denial and rechecks `installationStatus === ACTIVE` and `revokedAt === null` in `confirmCurrentWooConsent()` within the PostgreSQL transaction, returning `CONSENT_CHANGED` on a failed fence. Reviewed URL creation inside the transaction, opaque 32-byte token generation, canonical-host checks, immutable reuse after retry, generation isolation, and safe omission reasons. No material architectural redesign was identified. The sole request is specific regression evidence for both revocation timings; it may require a focused test addition, not production code churn.

### Reviewed Files

- `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-admission.service.ts`
- `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-admission-evidence.ts`
- `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-link-issuer.ts`
- `moda-interact-background/tests/unit/services/woocommerce-recovery/woo-recovery-admission.service.test.ts`
- `moda-interact-background/tests/unit/services/woocommerce-recovery/woo-recovery-link-issuer.test.ts`
- `moda-interact-background/tests/integration/woo-recovery-admission.integration.test.ts`
- Attempt 1 Completion Report and the ARCH-053 parent architecture.

### Validation Reviewed

The supplied Completion Report records 52 focused unit and eight disposable PostgreSQL/Redis integration tests passed, plus ESLint, build and `git diff --check`. The checked-in tests in the uploaded snapshot cover preflight revocation, transaction-fenced STOP, URL/idempotency and generations. These reported commands were **not independently rerun** during this architect review. An explicit revocation-during-transaction regression scenario is still required before final acceptance.

### Architecture Conformance

The inspected runtime behaviour conforms to the corrected ARCH-053 safety policy, the ARCH-048 generation lifecycle and existing tenant/consent guards. Link omission does not override installation admission eligibility. No new persistence path, endpoint, Shared contract or schema migration is required for this decision.

### Follow-up — authoritative Attempt 2 correction contract

1. Keep the already-pushed Attempt 1 implementation as the baseline; **do not change production source solely to manufacture another commit**.
2. In `tests/unit/services/woocommerce-recovery/woo-recovery-admission.service.test.ts`, ensure a revoked/inactive installation rejected at the initial lookup produces exactly `denied/INSTALLATION_INACTIVE`; assert **zero** recovery creates, URL updates and admission-history writes. Strengthen an existing test rather than duplicate it.
3. In that same test file, add a transaction-fence case with preflight installation ACTIVE, but a mocked locked consent row with `installationStatus: REVOKED` or non-null `revokedAt`; expect exactly `denied/CONSENT_CHANGED` and **zero** recovery creates, URL updates and admission-history writes. Keep the test narrowly scoped; use existing `permittedFence`/`setFence` helpers.
4. Run the focused admission/link issuer/template unit tests, the existing disposable PostgreSQL/Redis admission integration suite, repository build, changed-file lint and `git diff --check`. Record actual commands/results; if environmental validation is impossible, report it rather than claim a pass.
5. Update the agent-owned checkboxes/Completion Report, set task `status: review`, return the same task for architect acceptance and STOP. Do not modify Architect Review, parent architecture, `_index.md`, ARCH-052 or unrelated code.
