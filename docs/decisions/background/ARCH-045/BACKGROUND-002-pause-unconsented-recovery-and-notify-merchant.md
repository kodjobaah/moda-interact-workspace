---
id: ARCH-045-BACKGROUND-002
architecture_id: ARCH-045
title: Skip unconsented Shopify recovery creation and notify merchant
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-045-BACKGROUND-001
  - ARCH-045-BACKGROUND-005
enables:
  - ARCH-045-BACKGROUND-004
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-23
---
# Skip unconsented Shopify recovery creation and notify merchant

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** materialised on parent branch `task/ARCH-045-BACKGROUND-002`, developer-claimed as Attempt 1, and returned to `ready` after self-review. Implementation commit [`8a2e56c`](https://github.com/kodjobaah/moda-interact-background/commit/8a2e56c0aa881d8155daa714864a682406a26f34) is published on the mirrored implementation task branch. The original launcher preparation/synchronisation packet was not found in the current-session transcript.

## Objective

During **ordinary Shopify checkout reconciliation**, reject unconsented first recoveries **before the first `CheckoutRecovery` INSERT** and publish one truthful checkout-keyed merchant Support notice without sending WhatsApp or charging a recovery credit.

## Context

`BACKGROUND-001` supplies Shopify-native current consent and an injectable policy. `recovery-initiation.service.ts` currently creates a recovery before some later admission checks; the policy must move to a pre-create seam. `BACKGROUND-004` will own the last pre-provider sending fence shared by all proactive paths.

## Scope
- Integrate `ShopifyWhatsAppConsentService.evaluateRecipient()` at mature pending-candidate/**each distinct new Shopify checkout** reconciliation before creating a first `CheckoutRecovery`, reserving credits or sending. Obtain a fresh Shopify `readCurrent()` observation for that checkout, project its native decision to CustomerPhone, and retain existing paid/abandoned checkout, exact recipient, entitlement and idempotency gates. Duplicate deliveries of the same checkout must not produce redundant recovery or billing work.
- On confirmed no opt-in, unknown/revoked consent, ambiguous recipient or local customer STOP/merchant suppression: no first recovery row, attempt, charge or provider send. A new Shopify `SUBSCRIBED` observation updates the native `CustomerPhone` decision but **never** clears STOP; BACKGROUND-005 already owns the merchant notice for STOP, so do not issue a misleading duplicate consent-missing notice. Keep Shopify temporary provider/API verification outages as a **distinct fail-closed technical outcome** under the existing bounded retry rules.
- Reuse existing `MerchantSupportMessage(kind=SYSTEM)` and a bounded deterministic `sourceKey` derived from shop, **hashed** checkout identity and reason. Show one checkout/reason notice without leaking phone/checkout tokens; never claim the customer refused consent when Shopify was unavailable or identity could not be resolved. No separate Support table.
- Apply the same initial-admission policy to first-send re-entry through existing `DETECTED` recoveries, capacity resume, recipient suppression and initial-send retries. Historical pre-existing recoveries may retain their rows, but no new send/credit is permitted after withdrawal or no-contact. `BACKGROUND-004` supplies the shared **final** dispatch guard.
- A later consent grant updates CustomerPhone only. Reconsideration requires an independently occurring **normal** checkout event/reconciliation; the pending-candidate index is not retained merely to wait for consent.
- An approved **Marketing-category** abandoned-basket template is required for first proactive recovery outreach; neither a generic utility/transactional template nor phone collection alone can authorise the send. BACKGROUND-004 owns common template-category and final-dispatch checks; the initial recovery cannot bypass that path.


## Out of Scope
- No consent-blocked recovery status/enum, 72-hour consent clock, consent-specific queue/sweeper, Shopify merchant consent-collector configuration, customer opt-in WhatsApp request, privacy-erasure fence or recipient-reachability schema change.
- Do not implement the final scheduled/post-window send fence owned by BACKGROUND-004 or webhook-consent synchronisation owned by BACKGROUND-003.


## Requirements
- [x] The first recovery must **not** exist when current exact customer/phone consent is unverified or denied; use no `DETECTED` consent-wait row.
- [x] All initial admission and first-send retry/reentry paths use the same injected consent/no-contact policy; a native `GRANTED` alongside local `CUSTOMER_STOP` is denied. Preserve existing billing/reservation/compensation rules.
- [x] Merchant notices distinguish confirmed no opt-in from identity ambiguity and transient Shopify verification failure, without falsely asserting customer refusal.
- [x] Missing consent is not a reason to retain or periodically poll an abandoned checkout; only ordinary future reconciliation may attempt again.
- [x] Each new Shopify checkout's initial recovery decision freshly verifies native WhatsApp marketing consent and persists the result to CustomerPhone. Later sends from an already-created recovery read stored permission and do not make another Shopify consent API call.


## Work Items
- [x] Move the first consent check before `RecoveryInitiationService` persists its first recovery; wire the existing candidate and direct initiation paths.
- [x] Reuse that policy for capacity/suppression and legacy `DETECTED` first-send reentries, delegating final pre-provider fencing to BACKGROUND-004.
- [x] Implement idempotent checkout-keyed Support notices with distinct bounded denial/failure reasons.
- [ ] Test duplicate candidates, no new recovery/charge on denial, technical failure retry, real later checkout event and no-event inactivity.


## Interfaces / Contracts

Consumes BACKGROUND-001 current CustomerPhone + Shopify authority and existing normal checkout candidate/initiation, Support and billing contracts. Depends on BACKGROUND-005's durable customer STOP semantics; **no second permanent no-contact representation** is created in `WhatsAppRecipientReachability`.

## Dependencies
- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-005`


## Enables
- `ARCH-045-BACKGROUND-004`
- `ARCH-045-SYSTEM-TEST-001`


## Acceptance Criteria
- [x] Initial negative/unknown/unavailable permission creates no new CheckoutRecovery, outbound message, recovery attempt or billable charge; duplicates produce at most one notice per checkout/reason.
- [x] Direct initiation, pending candidate maturation, capacity resume, suppression retry and old `DETECTED` first sends cannot bypass latest phone consent/STOP, including a Shopify grant recorded after STOP. Existing rows are not rewritten merely to model missing consent.
- [x] The first recovery Marketing template cannot be sent using a Utility classification or an unverified template category; no provider send or credit on a category/consent denial.
- [ ] A grant alone causes no recovery/candidate job; a later legitimate reconciliation may create the first recovery only if the checkout still qualifies.
- [x] API outage, missing identity and confirmed absent opt-in produce appropriately distinct operational/merchant outcomes.


## Validation
- [x] Focused candidate/materialisation, direct initiation, capacity/suppression reentry, Support deduplication, billing/Meta zero-send and unavailable-provider tests; assert no new recovery on initial denial.
- [ ] Real next checkout event versus no event, paid-order race, changed recipient, duplicate jobs, customer STOP/merchant suppression and `git diff --check`.
- [x] Marketing-template availability/classification tests, one provider consent verification per new checkout (not per follow-up), missing-consent merchant notice and Shopify read outage distinction.


## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Prefer a small consent admission/merchant notice service injected into the existing initiation method. Use Shared logging; do not expand a large orchestration module with generic logging/transport logic. Existing Support inbox copy is delivered by the app, not via Meta WhatsApp.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

Changes Requested — Attempt 1 was claimed by developer at `2026-10-23T10:41:40Z` and returned to `ready` after self-review. The implementation and supplementary regression tests are committed and pushed, and the latest focused tests, unit suite, lint and build passed. **The task remains `ready`, `attempt: 1`, `executor: null`; no Attempt 2 claim or architect acceptance is represented by this report.** The missing original launcher preparation packet still requires reconciliation or an architect-approved amendment.

### Files Changed

Implementation repository: `moda-interact-background`, branch `task/ARCH-045-BACKGROUND-002`, commit `8a2e56c0aa881d8155daa714864a682406a26f34` (19 files, 784 insertions, 47 deletions; pushed to `origin/task/ARCH-045-BACKGROUND-002`).

Production code:
- `src/services/checkout-recovery.service.ts`
- `src/services/checkout-recovery/recovery-capacity-resume-processor.service.ts`
- `src/services/checkout-recovery/recovery-consent-admission.service.ts` (new)
- `src/services/checkout-recovery/recovery-consent-notice.service.ts` (new)
- `src/services/checkout-recovery/recovery-initiation.service.ts`
- `src/services/checkout-recovery/recovery-materialization.service.ts`
- `src/services/checkout-recovery/recovery-recipient-resolver.service.ts`
- `src/services/checkout-recovery/recovery-shopify-customer.service.ts` (new)
- `src/services/whatsapp-template-selector.service.ts`


Tests/test support:
- `tests/unit/services/checkout-recovery.capacity-resume.test.ts`
- `tests/unit/services/checkout-recovery/recovery-consent-admission.service.test.ts` (new)
- `tests/unit/services/checkout-recovery/recovery-consent-notice.service.test.ts` (new)
- `tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`
- `tests/unit/services/checkout-recovery/recovery-recipient-resolver.service.test.ts`
- `tests/unit/services/checkout-recovery/recovery-shopify-customer.service.test.ts` (new)
- `tests/unit/services/checkout-refresh.test.ts`
- `tests/unit/services/matured-candidate.materialization.test.ts`
- `tests/unit/services/outbound-whatsapp-admission/outbound-admission.test-support.ts`
- `tests/unit/workers/pending-recovery-candidate.worker.test.ts`

Supplementary regression commit: `efd6721d945a4498f8510c3a5ae4e079abeee6cc`, published on `origin/task/ARCH-045-BACKGROUND-002` after `8a2e56c` (test-only; three files):
- `tests/unit/services/checkout-recovery/recovery-consent-checkout-reconciliation.test.ts` (new)
- `tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts` (additional regression assertions)
- `tests/unit/services/shopify-whatsapp-consent.service.test.ts` (merchant opt-out regression)

No schema/migrations, Shared package, Shopify application, or `docs/decisions/**/_index.md` files were changed by either implementation or regression commit.

### Work Completed
- Added a focused consent admission service: fresh Shopify-native recipient eligibility check before the first recovery INSERT, stored consent checks for existing `DETECTED` recovery reentry, and a distinct retryable Shopify verification-outage outcome.
- Retained local CUSTOMER_STOP as an authoritative no-contact denial even when Shopify's current native state is granted, without creating a second reachability prohibition or misleading STOP notice.
- Added exact-linked Shopify customer resolution for recovery admission instead of converting phone matches into Shopify customer identities; canonical phone formatting does not remove STOP.
- Added transactional, checkout/reason-deduplicated Support SYSTEM notices with a bounded hashed checkout reference and separate reasons for absent opt-in, unresolved identity and provider unavailability.
- Routed normal maturation/direct initiation and capacity-resume first sends through admission checks, with suppression and billing protections; rechecks stored consent before provider admission and releases reserved credit on a newly detected block.
- Rejected first-send template selections whose Marketing category is unverified; final cross-path dispatch fencing remains delegated to `ARCH-045-BACKGROUND-004`.
- Adjusted focused test fixtures across incremental correction patches and committed the consolidated implementation as one repository commit.
- Added the Changes Requested regression tests: grant without checkout activity does not schedule recovery, a later genuine ordinary checkout event may retry admission, completed/paid checkouts remain blocked, duplicate matured candidates stay idempotent, changed recipients require independent consent, and STOP/merchant no-contact defeats subsequent grants on first-send reentry. These are deterministic unit tests with injected dependencies, not live Shopify/Meta integration.


### Validation Results
- `npx vitest run tests/unit/workers/pending-recovery-candidate.worker.test.ts` — **PASS, 2/2 tests** (23 October 2026 terminal log).
- `npm run test:unit` — **PASS, 250/250 test files and 2,514/2,514 tests** (same terminal log).
- `npm run lint` — **PASS**, ESLint completed without reported errors (same terminal log).
- `npm run build` — **PASS**, Prisma Client 6.19.3 generated and TypeScript compiler completed without reported errors (same terminal log).
- `git diff --check` — **PASS**, no whitespace errors reported before staging.
- `git commit -m "feat(background)"` — **PASS**, `8a2e56c`, 19 changed files.
- `git push -u origin task/ARCH-045-BACKGROUND-002` — **PASS**, new remote task branch published and tracking established.
- Latest terminal log (23 October 2026), `npx vitest run tests/unit/services/checkout-recovery/recovery-consent-checkout-reconciliation.test.ts tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts tests/unit/services/shopify-whatsapp-consent.service.test.ts` — **PASS, 3/3 files, 49/49 tests**.
- Latest terminal log, `npm run test:unit` — **PASS, 251/251 files, 2,522/2,522 tests**.
- Latest terminal log, `npm run lint` — **PASS**, ESLint completed without reported errors.
- Latest terminal log, `npm run build` — **PASS**, Prisma Client 6.19.3 generated and TypeScript compilation finished without reported errors.
- Latest terminal log, `git diff --check` — **PASS**, no whitespace errors reported.
- GitHub implementation branch verification — **PASS**, `efd6721d945a4498f8510c3a5ae4e079abeee6cc` published, one commit ahead of `8a2e56c`, with exactly the three regression test files in that commit.
- **Review boundary:** focused/unit tests pass; no claim of real Shopify consent webhooks, actual Meta sends, PostgreSQL system tests or historical launcher packet validation.
- Physical implementation worktree evidenced by terminal `pwd`/commands: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-BACKGROUND-002`, branch `task/ARCH-045-BACKGROUND-002`.
- Parent mirrored task branch was read directly from the repository. **The original launcher-prepared execution packet was not found in the current-session transcript.** A correct branch and passing tests are not substitutes for that packet.
- **Not executed / not evidenced:** live Shopify consent API, actual Meta provider or PostgreSQL end-to-end system tests. The later ordinary checkout-event versus no-event sequence is now covered by passing injected-dependency unit tests; this is not live integration evidence.


### Deviations

None in repository ownership or consent policy. The original task's historical portable-definition text was stale after the developer takeover and is corrected in the current task metadata/report. Test-fixture corrections across incremental patch iterations were consolidated into commit `8a2e56c`.

### Assumptions
- Native Shopify consent remains independent from the permanent local CUSTOMER_STOP prohibition.
- No consent-specific queue/poller or fixed 72-hour hold is introduced; a later grant alone does not restart outreach.
- Unit tests establish deterministic service behaviour; provider/system integration requires separate verification and is not inferred from the unit suite.


### Unresolved Issues
- **Review evidence:** attach or recover the actual `/moda_developer_create` launcher preparation packet showing both canonical parent/implementation task worktrees, start-of-attempt sync and recursive-submodule evidence. Do not recreate historical evidence or claim synchronization from `git branch` alone.
- **Regression coverage now evidenced:** the grant-only versus later ordinary checkout event, paid-order race, duplicate candidate, changed recipient, STOP and merchant opt-out tests are implemented in `efd6721` and pass in the latest focused (49/49) and full unit (2,522/2,522) runs. Their live provider/system behaviour remains separately unverified.
- No live Shopify, Meta or PostgreSQL integration execution is evidenced in the submitted unit-validation log. Record the separate integration/system-test ownership rather than asserting this validation passed.


### Architectural Concerns
- The current template catalogue exposes approval but not a trusted Meta Marketing category. The implementation deliberately fails closed for unverified category; actual proactive recovery sends will remain blocked until the architecture-owned category validation is available. `ARCH-045-BACKGROUND-004` owns the common final pre-provider fence; this task does not claim to implement it.
- The normal checkout admission flow has unit coverage, but the separate terminal system-test programme remains responsible for real cross-repository provider/billing outcomes. No cross-repository changes were made.


## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.

## Developer Self-Review - Changes Requested (Attempt 1)

- Implementation commit `8a2e56c0aa881d8155daa714864a682406a26f34` is clean and published on `origin/task/ARCH-045-BACKGROUND-002`. Before this review, the parent report was clean and synchronized at `e3d2abc72aab45b19ceb82235cde20cc695c6272`. `git diff --check origin/main...HEAD` passes for the implementation branch.
- The recorded focused test, full unit suite (2,514 tests), lint and build passed. Existing focused consent tests cover denial, local STOP, identity ambiguity, Shopify verification outage, stored permission on reentry and a verified grant.
- Correction 1: add and run a regression proving a consent grant alone creates no recovery/candidate job, while a separate later ordinary checkout event may create the first recovery only when that checkout remains eligible. Assert the no-event case creates no recovery, attempt, charge or send and that there is no consent-triggered scan/retry.
- Correction 2: add/run the remaining task-listed admission scenarios with durable assertions: paid-order race, duplicate candidate jobs for one checkout, changed current recipient, and STOP/merchant suppression across first-send reentry. Record exact focused test commands/results and update the corresponding unchecked Work Items, Acceptance Criteria and Validation only after they pass.
- Correction 3: provide the original launcher prepared-execution packet for Attempt 1 showing canonical parent/implementation worktrees, start-of-attempt synchronization and recursive-submodule result. The packet was not found in the current-session transcript; do not rerun preparation solely to recreate historical evidence. If it cannot be recovered, obtain an architect-approved amendment to the evidence requirement.
- State transition: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1`. No Attempt 2 was created and completion was not accepted.

## Developer Takeover

On 2026-10-23, `/moda_developer_create ARCH-045-BACKGROUND-002` was invoked while this task was ready and agent-owned. This is an explicit developer takeover. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_background`, repository ownership, dependencies, scope and acceptance criteria are unchanged. The canonical launcher prepared and claimed Attempt 1; its original prepared-execution packet was not found in the current-session transcript.
