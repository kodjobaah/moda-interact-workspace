---
id: ARCH-045-BACKGROUND-004
architecture_id: ARCH-045
title: Guard scheduled and merchant post-window recovery follow-ups
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 35
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-045-BACKGROUND-001
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-005
enables:
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-23
---
# Guard scheduled and merchant post-window recovery follow-ups

## Developer Ownership Amendment

On 2026-10-23, `/moda_developer_create ARCH-045-BACKGROUND-004` was invoked
while this task was ready and agent-owned. This is an explicit developer
takeover. `execution_mode` and `completion_mode` are now `developer`;
`assigned_agent: moda_background`, repository ownership, dependencies, scope
and acceptance criteria are unchanged. The launcher claimed developer Attempt 1 at `2026-10-23T13:20:29Z`;
this ownership amendment remains part of the task history.

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** materialised and published on parent branch `task/ARCH-045-BACKGROUND-004` during ARCH-045 dependency-frontier reconciliation after BACKGROUND-001, BACKGROUND-002 and BACKGROUND-005 were verified complete. Its dependencies were verified complete and developer Attempt 2 completed the required evidence-reconciliation cycle; the implementation commit is published and validation is recorded below.

## Objective

Apply the final shared Background consent guard to **all business-initiated WhatsApp recovery sends**, especially scheduled follow-ups, merchant post-window templates and first-send reentries, while also enforcing a Customer STOP hard prohibition across **all** outbound WhatsApp sends, including otherwise legitimate in-window service replies.

## Context

`BACKGROUND-002` owns the pre-creation and initial reentry admission seam; `BACKGROUND-001` owns the current CustomerPhone snapshot policy; live Shopify verification belongs to each new-checkout admission in BACKGROUND-002, not every subsequent send. Scheduled sequence-two follow-ups and ARCH-040 human post-window templates use distinct existing dispatch/credit paths and must converge at a safe **final outbound permit**.

## Scope

- Integrate one reusable injected consent decision into scheduled no-response follow-ups, merchant-initiated post-24-hour recovery templates and all business-initiated first-send reentries. Inspect the existing recovery and ARCH-040 human-command dispatch paths rather than duplicating business/Meta logic.
- For subsequent recovery messages, call only `ShopifyWhatsAppConsentService.evaluateStoredRecipient()` (database-backed, **no Shopify GraphQL request**). At the final short database fence verify the exact `CustomerPhone` `GRANTED` state, recipient, current consent revision, no-contact revision and existing checkout/attempt/control predicates. Local revoked/STOP, merchant suppression or unavailable database state denies sending.
- Keep existing `WhatsAppRecipientReachability` temporary delivery suppression separate from positive consent; do **not** require a newly invented permanent recipient STOP fence, source epoch or privacy-erasure table.
- Refuse or compensate denied sends without a Meta call, committed credit or permanently consumed sequence-two attempt. Preserve first-send billing compensation, single sequence-two claim ownership and existing HUMAN/AI control ordering; never issue a second recovery message because of duplicate final checking.
- Classify legitimate customer-initiated **in-window** human/free-form replies separately for Meta template/service-window purposes, but **block delivery if an applicable `CUSTOMER_STOP` exists**. Never interpret a service-window exemption as permission to contact a stopped recipient; apply the STOP predicate at the shared final outbound boundary to automated, human, queued and retrying messages.
- Treat **all business-initiated abandoned-cart/basket reminders** (first contact, automated reminder, sequence-two follow-up and merchant post-window recovery template) as **Marketing**. Verify the selected approved Meta template's actual Marketing category using trusted provider/template approval information; `WhatsAppTemplateVariant.purpose = checkout-recovery` and `status = APPROVED` alone are not evidence of Meta category in the inspected schema. Reject unknown, Utility or Authentication classifications without send/credit; if the existing template catalogue cannot supply trustworthy category evidence, report the precise ownership/contract gap to `moda_architect` rather than changing DATABASE-002 or silently passing the check.
- Document the unavoidable time gap between stored-state fence, SQL commit and Meta dispatch; use short revision checks and existing compensation rather than claiming cross-system atomicity. Shopify is queried anew at each **new checkout**, not before every follow-up.

## Out of Scope

- No new billing/attempt tables, sequence-two slots, customer contact mode, Shopify cookie/CMP work, generic Meta sender-wide consent rule or new recovery scheduler.

## Requirements

- [x] Every proactive follow-up, post-window template and first-send reentry has a consent check before reservation and a safe final pre-provider permit; **every** outbound path also checks the authoritative CustomerPhone STOP flag, including in-window AI/HUMAN replies. No independent fallback can bypass STOP.
- [x] The final consent check uses **stored CustomerPhone** only; no Shopify API call occurs on follow-up/re-entry dispatch, and no Redis/network I/O is introduced inside the short SQL fence.
- [x] Denial or source outage before dispatch produces no provider call, committed charge or lost unique sequence-two attempt; historical attempts retain existing semantics; valid in-window service replies remain distinct from Marketing but are suppressed when STOP is active.

## Work Items

- [x] Identify the concrete scheduled, manual post-window, initial reentry and outbound fence entry points and inject BACKGROUND-001's shared policy.
- [x] Inject the database-only stored recipient decision and revision/no-contact predicates into the existing final send-fence boundary, without a Shopify preflight for follow-ups.
- [x] Add cross-path denial, stored-read-to-fence local revocation, billing compensation, sequence-two contention and permitted service-window reply tests.

## Interfaces / Contracts

Consumes `ARCH-045-BACKGROUND-001` policy, `ARCH-045-BACKGROUND-002` initial admission integration and `ARCH-045-BACKGROUND-005` durable CustomerPhone STOP, plus existing ARCH-040 outbound-send-fence, conversation control and recovery credit interfaces. No Shared queue addition.

## Dependencies

- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-005`

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Neither scheduled nor merchant-initiated post-window WhatsApp recovery may send after stored withdrawal, local STOP, merchant suppression, recipient change or database failure; no per-follow-up Shopify verification occurs.
- [x] First-send retries/resumptions and both sequence-two paths use the final permit, preserving the one allowed follow-up and billing/idempotency guarantees.
- [x] Shopify is **not called** during follow-up dispatch; a credit/attempt is not irreversibly consumed when stored consent or Meta Marketing-template eligibility is denied. In-window service replies retain non-Marketing rules but cannot bypass customer STOP.
- [x] No provider HTTP/Redis in SQL transaction, source epoch, erasure fence or reachability consent schema is introduced.

## Validation

- [x] Focused `recovery-outreach-follow-up-processor`, human post-window command dispatcher/evaluator, first-send capacity/suppression reentry and outbound-send-fence tests, including local revocation between stored read and SQL fence and assertion of zero Shopify GraphQL calls for follow-ups.
- [x] Concurrent human/automation sequence-two claim and compensation tests, in-window HUMAN_TEXT permitted-without-STOP and blocked-with-STOP tests, repository-declared checks and `git diff --check`.
- [x] Approved Marketing versus Utility/Authentication/unverifiable template category tests for automated first/follow-up and merchant recovery templates; no attempt/charge/provider call on invalid category. Verify actual template metadata source, or report an explicit blocker when the catalogue only exposes purpose/status.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Audit the implementation state of concurrent ARCH-040 tasks before editing their owned paths. If the canonical worktree has diverged from the snapshot, update against current accepted API rather than overwriting its human command work. Avoid changing human-text messages into marketing sends; STOP blocks all outbound types without changing their message-category classification.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

Ready for Review — Attempt 2 was claimed by the developer at 2026-10-23T16:00:26Z and completed the required evidence reconciliation. Attempt 1 review history is preserved below; explicit developer completion remains pending.

### Files Changed

`moda-interact-background` — commit [`5e3cecda856eaa2d12d589d6e838ff16911a46f3`](https://github.com/kodjobaah/moda-interact-background/commit/5e3cecda856eaa2d12d589d6e838ff16911a46f3), pushed to `origin/task/ARCH-045-BACKGROUND-004`: **21 files (777 insertions, 69 deletions)**.

- `src/services/checkout-recovery/recovery-initiation.service.ts`
- `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts`
- `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`
- `src/services/recovery-conversation/human-command-dispatcher.service.ts`
- `src/services/recovery-conversation/outbound-send-fence.service.ts`
- `src/services/recovery-conversation/recovery-follow-up-policy.service.ts`
- `src/services/recovery-conversation/recovery-runtime-eligibility.service.ts`
- `src/services/recovery-conversation/recovery-stored-consent.service.ts (new)`
- `src/services/whatsapp-template-category.service.ts (new)`
- `src/services/whatsapp-template-selector.service.ts`
- `tests/integration/conversation-moderation.integration.test.ts`
- `tests/integration/fixtures/recovery-human-dispatch.fixture.ts`
- `tests/integration/recovery-human-dispatch.integration.test.ts`
- `tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts`
- `tests/unit/services/outbound-whatsapp-admission.service.test.ts`
- `tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts`
- `tests/unit/services/recovery-conversation/human-synchronous-rejection.test.ts`
- `tests/unit/services/recovery-conversation/recovery-conversation-services.test.ts`
- `tests/unit/services/recovery-conversation/recovery-stored-consent.test.ts (new)`
- `tests/unit/services/whatsapp-template-category.service.test.ts (new)`
- `tests/unit/services/whatsapp-template-selector.service.test.ts`

No Prisma migrations, Shared contracts, Shopify application source, parent architecture document or `docs/decisions/**/_index.md` files are included in the implementation commit.

### Work Completed

- Integrated stored-only Shopify recovery consent preflight into scheduled sequence-two follow-ups and merchant post-window recovery templates, with no per-follow-up Shopify GraphQL refresh.
- Added `RecoveryStoredConsentService`: binds a canonical recipient, CustomerPhone row and consent/no-contact revisions to a pre-provider snapshot; revalidates that snapshot at the existing Shop-locked SQL dispatch fence. Consent withdrawal, STOP, changed recipient, ambiguous phone record and unavailable state fail closed.
- Preserved a separate WooCommerce policy boundary: do not invent Shopify-native permission for WooCommerce recovery activity. Existing outbound STOP checks remain applicable.
- Added `MetaWhatsAppTemplateCategoryService` to check actual approved Marketing category against Meta template metadata using an exact provider account/name/language/optional ID match. Missing, unapproved, ambiguous, non-Marketing or unavailable metadata denies proactive delivery; network I/O is outside SQL.
- Guarded first-send reentry, scheduled follow-up dispatch, and merchant-initiated post-window templates through the final permit, without changing in-window HUMAN_TEXT Marketing classification or relaxing its STOP prohibition.
- Added bounded pre-provider denial compensation for eligible provisional automated sequence-two claims; maintained the existing single-claim rule, durable provider-admission boundary and billing/idempotency semantics.
- Added/updated focused unit and PostgreSQL integration fixtures for stored-read-to-final-fence revocation, category verification, STOP, merchant suppression, concurrent follow-up claims, compensation and provider-permit ownership.
- Corrected the `exactOptionalPropertyTypes` `executionScope` handling during incremental validation without changing consent/STOP policy.

### Validation Results

- Focused ARCH-045 consent, template-category, follow-up and outbound-admission unit checks: **PASS, 36/36** (Attempt 2 terminal log).
- `npx vitest run tests/unit/runtime/observability-startup.test.ts --reporter=verbose`: **PASS, 10/10** after a single parallel-suite timeout. No observability implementation changed.
- `npm run test:unit -- --maxWorkers=2`: **PASS, 256/256 files, 2,596/2,596 tests** (23 October 2026 terminal log).
- `npm run test:integration -- tests/integration/general-outbound-stop-fence.integration.test.ts tests/integration/recovery-follow-up-claim-races.integration.test.ts tests/integration/recovery-human-dispatch.integration.test.ts`: **PASS, 3/3 suites, 33/33 tests**, using the disposable PostgreSQL integration harness (23 October 2026 terminal log). Earlier Docker startup and direct `spawn prisma ENOENT` issues were resolved by running through the declared npm script; these are not current application-test failures.
- `npm run lint`: **PASS**, ESLint completed without reported errors (same post-integration terminal log).
- `npm run build`: **PASS**, Prisma Client 6.19.3 generation and TypeScript compilation completed (same post-integration terminal log).
- `git diff --check` and `git diff --cached --check`: **PASS**, no whitespace errors reported before the implementation commit.
- `git commit -m "feat(ARCH-045-BACKGROUND-004): enforce final WhatsApp consent and STOP fence"`: **PASS**, commit `5e3cecd`; `git push origin task/ARCH-045-BACKGROUND-004`: **PASS**, branch published. Independent GitHub inspection confirms the full commit hash and 21 changed files.
- **Not claimed:** whole PostgreSQL integration catalogue, real Shopify GraphQL/provider-call interoperability, or live Meta delivery/template API acceptance. Tests used the specified repository fixtures and mock provider where appropriate. Further cross-service/live verification belongs to the architectural system-test gate.

### Deviations

No architecture scope or database schema deviation identified. Existing ARCH-040 integration fixtures were adjusted only to represent the already-required billing reservation, lease-clock and Marketing provider-permit contracts. The initial unit suite had one unrelated 5-second observability subprocess timeout; its focused and reduced-parallelism reruns passed.

### Assumptions

- ARCH-045-BACKGROUND-002 remains owner of fresh Shopify-native checks on each new checkout; BACKGROUND-004 performs stored CustomerPhone checks for subsequent sends.
- Local CUSTOMER_STOP remains authoritative even after a later Shopify `GRANTED` observation. A 24-hour customer-service window does not override STOP.
- Meta's verified Marketing-template category is required for abandoned-cart proactive outreach. Failed metadata verification is a denial, not proof of permission.
- Shopify, PostgreSQL and Meta cannot form one atomic transaction; the final short SQL fence reduces the race window but cannot guarantee atomicity with external dispatch.

### Unresolved Issues

- The implementation branch currently tracks `origin/task/ARCH-045-BACKGROUND-004` and matches the published Attempt 2 synchronization merge; no rebasing or merge to `main` is required.

### Architectural Concerns

- The Meta template category lookup is external, fail-closed and performed outside the SQL transaction. A successful stored-state fence cannot make the later Meta dispatch atomic; maintain compensation, monitoring and end-to-end system tests.
- No schema change or cross-repository consumer migration was required. Acceptance of the cross-path behaviour and live provider compatibility belongs to `moda_architect` and the terminal system-test programme.

### Git / VCS

Task branch: `task/ARCH-045-BACKGROUND-004`

Physical worktree isolation, from the Attempt 2 launcher packet:
- Canonical primary workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-045-BACKGROUND-004`.
- Parent branch: `task/ARCH-045-BACKGROUND-004`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-BACKGROUND-004`.
- Implementation branch: `task/ARCH-045-BACKGROUND-004`.
- Shared workspace checkout switched/mutated for task work: no.
- Shared implementation checkout switched/mutated for task work: no.
- Another task worktree reused: no.

Start-of-attempt synchronization, from the Attempt 2 launcher packet:
- Parent remote task branch fast-forward: `not-needed`.
- Parent `origin/main` incorporated: `already-current`.
- Implementation remote task branch fast-forward: `not-needed`.
- Implementation `origin/main` incorporated: `already-current`.
- Implementation recursive submodule preparation: `sync_recursive=passed`, `update_init_recursive=passed`, status `ready`, recursive `true`.
- Database submodule: initialized at `2e009298612133aace095db5d57245a5b01e773a`.

Implementation repository:
- Repository: `moda-interact-background`.
- Commit: `e33215009dbd4ee74170afdfdb3b9de39e8891b9` (Attempt 2 synchronization merge; original implementation commit `5e3cecda856eaa2d12d589d6e838ff16911a46f3` remains its first parent).
- Published remote: `origin/task/ARCH-045-BACKGROUND-004` — **yes**.

Parent workspace:
- Task file: `docs/decisions/background/ARCH-045/BACKGROUND-004-gate-proactive-recovery-follow-ups-by-consent.md`.
- Baseline parent claim commit: `543dd0551b8d070f5b5f18a93dacb9ddc2b52cf7`.
- Parent claim commit: `55c6bba43968c1c704c0ec1ebd0e5cfcd4a5a9ad`, pushed by the canonical launcher.
- Implementation submodule gitlink staged by this documentation patch: **no**.

Merged to implementation main: **no evidence / not claimed**.
Merged to workspace main: **no evidence / not claimed**.

## Architect Review

### Review Status

Accepted — Attempt 2 reviewed on 2026-10-23. Attempt 1's evidence corrections are satisfied by the canonical Attempt 2 launcher packet.

### Review Notes

The implementation branch is clean and published. The canonical packet records the isolated parent and implementation worktrees, `origin/main` synchronization, recursive submodule preparation, dependency gate, and durable Attempt 2 claim. No new production implementation changes were made during this evidence-reconciliation attempt.

### Reviewed Files

Implementation diff in `moda-interact-background` at commit `e33215009dbd4ee74170afdfdb3b9de39e8891b9`, plus the canonical Attempt 2 launcher packet and task-owned VCS/lifecycle evidence.

### Validation Reviewed

Recorded focused unit/integration, repository unit, build, lint and diff-check results from the implementation attempt. No additional implementation validation was required because Attempt 2 made no production implementation changes and the task Stop Condition excludes rerunning implementation validation for this publication/evidence cycle.

### Architecture Conformance

No production-scope deviation was identified. The implementation remains within the task's ownership and architecture boundaries.

### Follow-up

Because `completion_mode: developer`, explicit developer completion remains pending; this review transitions the task to `status: review`, not `complete`.

## Developer Self-Review - Changes Requested - Attempt 1 (2026-10-23)

The implementation behavior and focused validation evidence are substantially complete, and the implementation commit is published. Review cannot be accepted yet because the task record explicitly requires start-of-attempt launcher evidence and currently states that the canonical parent/implementation worktree preparation, mainline synchronization, recursive submodule preparation, and physical isolation were not captured. The current route output and present-day Git state do not substitute for that historical launcher packet, and no architect-approved evidence amendment is recorded.

Required corrections before the next review:

- Add the original canonical `/moda_developer_create ARCH-045-BACKGROUND-004` launcher packet, or obtain and record an explicit architect-approved evidence amendment covering parent and implementation worktree paths, remote/main synchronization, recursive submodule preparation, and isolation.
- Reconcile the Git/VCS section with the actual implementation branch state: `task/ARCH-045-BACKGROUND-004` currently matches `origin/task/ARCH-045-BACKGROUND-004` at `5e3cecda856eaa2d12d589d6e838ff16911a46f3`; the report's statement that it still tracks `origin/main` is stale.
- Re-submit the same Attempt 1 for review after the evidence corrections. Do not create Attempt 2 solely for this review failure.

The implementation worktree has no tracked changes and the untracked `typescript` entry is a local terminal-log artifact; it was not included in the implementation commit. No production code change is requested by this review. Transitioned to `status: ready`, `executor: null`, `claimed_at: null`, preserving `attempt: 1`. No merge to `main` was performed or requested.

## Developer Self-Review - Accepted - Attempt 2 (2026-10-23)

Attempt 2 completed the requested evidence reconciliation. The canonical launcher packet records the authoritative workspace root, dedicated parent and implementation worktrees, task branches, `origin/main` synchronization, recursive submodule synchronization and initialization, dependency-gate success, and the durable developer claim commit. The implementation branch is clean and published at `e33215009dbd4ee74170afdfdb3b9de39e8891b9`; it contains the existing implementation commit plus the required `origin/main` synchronization merge and no new production implementation changes.

The recorded focused unit/integration, repository unit, build, lint and diff-check validation remains applicable to the unchanged implementation. All Work Items and Acceptance Criteria remain complete, and no production-scope deviation or unresolved implementation failure is known. Because `completion_mode: developer`, this accepted review leaves `status: review`, clears `executor` and `claimed_at`, and preserves `attempt: 2`; explicit completion remains pending. No merge to `main` was performed or required.
