---
id: ARCH-045-BACKGROUND-005
architecture_id: ARCH-045
title: Record inbound WhatsApp opt-outs and enforce no-contact precedence
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 22
executor: developer
claimed_at: 2026-10-23T00:02:02Z
attempt: 2
depends_on:
  - ARCH-045-DATABASE-002
enables:
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-004
  - ARCH-046-BACKGROUND-002
  - ARCH-046-BACKGROUND-004
  - ARCH-045-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
  - ARCH-046-SYSTEM-TEST-001
created: '2026-10-21'
updated: 2026-10-23
---
# Record inbound WhatsApp opt-outs and enforce no-contact precedence

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-045-BACKGROUND-005`, taking over execution and completion authority from the prior `execution_mode: agent`, `completion_mode: automatic` definition. Execution/completion modes are now `developer`/`developer`; logical ownership remains `assigned_agent: moda_background`, and task scope, dependencies, acceptance criteria and validation requirements are unchanged.

## Objective

Record explicit WhatsApp customer STOP/unsubscribe requests **by canonical phone** before ordinary routing can ignore them: a STOP quoting a reliably resolved merchant outbound message blocks that phone at the identified merchant, while a **standalone STOP blocks that phone at every merchant where it is currently registered**. Record the STOP **only in Moda** and notify each affected merchant through the existing Support SYSTEM messages. No Shopify unsubscribe mutation, Shopify `write_customers` scope or new consent table/reachability changes.

## Context

`whatsapp.worker.ts` may route/ignore a message before a consent opt-out is interpreted. The normalised inbound message is not guaranteed to carry `shopId`; the same phone can occur at multiple merchants. Current `CustomerPhone` provides durable customer no-contact state, while the existing `WhatsAppRecipientReachability` concerns provider delivery failures, not consent.

## Scope

- After authenticated inbound admission, detect explicit deterministic STOP/UNSUBSCRIBE **before** moderation rejection, ignored/guidance/AI/human routing or any other normal message disposition can discard it. Preserve moderation logging where applicable, but it must not prevent a valid opt-out from taking effect. Do not substitute LLM classification for explicit commands.
- Read the authenticated inbound sender as a canonical WhatsApp number. If `contextMessageId` references a **reliably resolved original merchant outbound message**, identify that message's shop and block **all active CustomerPhone records for that canonical number within that shop**. If the inbound STOP has **no quoted outbound message**, do not infer a shop from the latest conversation: block **every active matching CustomerPhone across all currently registered merchants**, including both Shopify and WooCommerce. If a quoted reference exists but cannot be resolved reliably, use the same number-wide STOP rather than guessing one shop. Cross-merchant matching is permitted **only for this negative STOP operation**, never for positive consent.
- Use the existing authenticated inbound event identity for idempotency and persist STOP/no-contact on **each affected active CustomerPhone** in a short database transaction. Do not add event-ID columns to CustomerPhone. Duplicates must not redate/revise a previous STOP or leave partial merchant subsets. Once set, the `CUSTOMER_STOP` reason and no-contact state are never cleared by a Shopify read/webhook (even a newer `SUBSCRIBED`), Woo checkout consent grant or merchant re-enable. Only a future separately authorised, verified **customer-requested Moda STOP removal** could change this; no such automatic flow is added here.
- After local STOP is committed, publish one **idempotent `MerchantSupportMessage(kind=SYSTEM)` per affected merchant**, correlated to shop and an opaque canonical-phone STOP identity without exposing raw phone numbers in logs or source keys. Distinguish an explicit quoted shop-specific STOP from a standalone number-wide STOP. Prefer committing per-merchant Support notices with the STOP state in the same PostgreSQL transaction when the existing Support writer supports this; otherwise use its existing idempotent `sourceKey` and bounded inbound retry/reconciliation for partial notice failures. Report a concrete delivery guarantee gap instead of inventing another queue or table. A duplicate inbound webhook must not redate STOP or create another merchant notice. No calls to Shopify or WooCommerce provider APIs are made for STOP.
- If no active CustomerPhone exists for the canonical sender, report the unmatched STOP without falsely claiming durable future suppression. This v1 rule covers **registered numbers**, not unknown future merchants; do not invent a global suppression table. A nonexistent/invalid phone must not mutate unrelated records.
- Preserve existing ARCH-040 handover/moderation and distinct service-window classification, but the local STOP **blocks every subsequent outbound WhatsApp message** to the targeted shop/phone, including in-window human/AI replies, queued sends and retries; no outbound STOP acknowledgement is sent to the customer.

## Out of Scope

- No new customer/session/erasure table, recipient-reachability consent columns, consent-specific queue or global WhatsApp policy rewrite. No new Shopify merchant opt-out UI (SHOPIFY-005 is superseded), Woo merchant preference UI/API or customer STOP-removal interface.

## Requirements

- [x] Quoted STOP applies to the identified merchant's phone records; **standalone or unresolvable-quote STOP** blocks every active matching phone across all registered merchants, before ordinary routing/ignored-message logic. Existing CustomerPhone no-contact state blocks **all** outbound sends to affected shops/phones, including service-window replies.
- [x] Cross-merchant updates occur **only** for standalone/unresolved-quote STOP and are scoped by the canonical sender phone; no positive consent, Customer merge or unrelated number is changed. Missing matching phones are explicitly reported, not marked suppressed.
- [x] Moderation and human handover retain their distinct rules, but no in-window reply or human message bypasses an active STOP.
- [x] An active STOP is an independent local prohibition that cannot be overridden by Shopify consent reads/webhooks, new checkouts, Woo checkbox grants or a merchant preference toggle. No Shopify mutation or remote retry is executed.
- [x] Each affected merchant receives one idempotent Moda Support SYSTEM notice; a partial Support-notice failure is retried without clearing STOP or notifying a different merchant.

## Work Items

- [x] Implement a small deterministic opt-out detector at the existing authenticated inbound worker boundary, ahead of any moderation or routing disposition that could drop STOP; test even an otherwise rejected inbound message still opts out.
- [x] Implement explicit quoted-message-to-shop resolution and number-wide fallback; update the correct merchant-scoped or cross-merchant set of current CustomerPhone records atomically/idempotently before ignored/guidance routing.
- [x] Create idempotent per-merchant Support SYSTEM notices after the STOP update, with partial-delivery retry and no raw phone PII in logs/source keys. Add quoted, standalone, unresolved quote, multi-customer same-shop, multi-shop, duplicate, Shopify `SUBSCRIBED` after STOP, Woo grant/merchant re-enable and concurrent send-fence tests. No Shopify or Woo outbound consent mutation.

## Interfaces / Contracts

Consumes `ARCH-045-DATABASE-002` CustomerPhone local no-contact fields, existing Meta-normalised inbound provider message/conversation mapping and the reusable consent policy read by ARCH-045-BACKGROUND-001/004 and ARCH-046-BACKGROUND-001/004. No new cross-service event schema or recipient-reachability consent table. A standalone STOP deliberately has **all registered merchants** as its target; no guessed recent-conversation shop. Quoted STOP uses validated outbound-message correlation. BACKGROUND-001 only reads Shopify consent; no Shopify write, new Shared queue or global no-contact table.

**Follow-up database contract:** General outbound dispatch admission consumes the forward migration identified as `ARCH-045-DATABASE-004`, which replaces `whatsapp.arch040_message_dispatch_guard()` to allow admission without requiring `checkoutRecoveryId IS NOT NULL`. The developer confirms architect approval of this change; the independently verified published database revision is `2e009298612133aace095db5d57245a5b01e773a` on `moda-interact-database/main`. Existing control-mode, control-revision, dispatch identity and immutability safeguards remain applicable. The database migration must be integrated before deploying the corresponding Background general-send fence. No new database columns, tables or Shared queue contract are introduced.

## Dependencies

- `ARCH-045-DATABASE-002`

## Enables

- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-004`
- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-004`
- `ARCH-045-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`
- `ARCH-046-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] An authenticated STOP updates the **correct set of active canonical-phone records**, with one effective stop per targeted record despite duplicate delivery; each affected merchant receives a deduplicated Support notice and no later Shopify consent response removes the local blocks.
- [x] A standalone STOP for a shared number blocks all currently registered shops without disabling any different number. An explicitly referenced merchant STOP leaves other shops untouched. An unresolvable quote follows the number-wide rule and an unmatched sender yields no invented durable suppression.
- [x] STOP is not lost to ignored/guidance routing and suppresses **all** outbound WhatsApp messages to the affected phone/shop, including in-window customer-service replies.

## Validation

- [x] Focused `whatsapp.worker` tests for quoted shop-specific STOP, standalone cross-merchant STOP, unresolvable quote fallback, duplicate provider IDs, multi-merchant and same-shop duplicate numbers, no registered phone, local STOP vs later Shopify consent/merchant re-enable; no PII in logs.
- [x] ARCH-040 moderation/human-control regression tests, Background send policy denial after STOP and `git diff --check`.
- [x] Realistic integration tests prove `SUBSCRIBED` before/after STOP and consent-sync webhook replay cannot clear STOP; merchant Support notices are exactly once per affected merchant; partial notice failures resume; no Shopify unsubscribe mutation or `write_customers` dependency exists.

## Stop Condition

After defined Work Items, Acceptance Criteria and required Validation, record dedicated parent/implementation task worktree and start-of-attempt synchronisation evidence, set `status: review`, submit Completion Report to `moda_architect`, and STOP. No dependent task may start before architect acceptance.

## Implementation Notes

Use the architect-approved consent model: no initial CheckoutRecovery without verified current permission, no arbitrary consent timeout, and consent changes do not trigger checkout reconciliation. Follow the current `/moda-task` launcher and exact published Shared/Database contracts. Preserve `docs/decisions/**/_index.md` until architecture session completion is confirmed. Use Shared structured logging on Node; bounded WordPress-safe diagnostics in PHP. Any missing cross-repository capability returns to architect rather than being implemented outside repository ownership.

## Completion Report

### Status
**Post-review correction committed and published; workflow re-claim pending.** The parent task still records `status: ready`, `attempt: 1`, `executor: null` and `claimed_at: null` following the prior Changes Requested review. The developer must use the normal task-claim workflow for Attempt 2 before changing the task to `review`; this report does **not** invent a new claim. The implementation correction is published at `7361af562ca448c97b730ea881be979e0755cfca`. Architect acceptance and explicit developer completion remain pending. The historical Attempt 1 evidence below is preserved.

### Developer Claim — Attempt 1

- Claimed at `2026-10-22T19:39:55+01:00`; executor is `developer` and `attempt: 1`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-045-BACKGROUND-005`, branch `task/ARCH-045-BACKGROUND-005`, created from current `origin/main` because no task branch or worktree registration existed.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-BACKGROUND-005`, branch `task/ARCH-045-BACKGROUND-005`, created from current implementation `origin/main` because no task branch or worktree registration existed.
- Both new worktrees are clean, correctly mapped, and contain their current `origin/main` tips. Explicit dependency `ARCH-045-DATABASE-002` resolves `complete`.
- The implementation worktree's `database` submodule was initialized at the recorded gitlink `e0ab833d2e2395e3ed3cfe4aee6d07c716173e44`; the parent pointer was not changed. The shared primary workspace and implementation reference checkout have unrelated dirty changes; neither was modified.

### Files Changed

The implementation commit changes 18 Background files (11 production, 7 test files):

- `src/services/outbound-whatsapp-admission.service.ts`
- `src/services/outbound-whatsapp-admission/outbound-delivery-errors.ts`
- `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`
- `src/services/recovery-conversation/outbound-send-fence.service.ts`
- `src/services/routing-guidance.service.ts`
- `src/services/whatsapp-contact-opt-out.service.ts`
- `src/services/whatsapp-contact-opt-out/local-no-contact.ts`
- `src/services/whatsapp-contact-opt-out/phone.ts`
- `src/services/whatsapp-contact-opt-out/quoted-outbound.ts`
- `src/services/whatsapp-contact-opt-out/stop-writer.ts`
- `src/services/whatsapp-inbound-processing.service.ts`
- `tests/integration/whatsapp-contact-opt-out.integration.test.ts`
- `tests/unit/services/outbound-whatsapp-admission/outbound-admission.test-support.ts`
- `tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts`
- `tests/unit/services/recovery-conversation/recovery-conversation-services.test.ts`
- `tests/unit/services/routing-guidance.service.test.ts`
- `tests/unit/services/whatsapp-contact-opt-out.service.test.ts`
- `tests/unit/workers/whatsapp.worker.test.ts`

**Post-review correction** (`7361af562ca448c97b730ea881be979e0755cfca`) changed exactly six Background-owned paths (one database gitlink, two production source files and three test files):

- `database` — advanced the nested database gitlink from `e0ab833d2e2395e3ed3cfe4aee6d07c716173e44` to architect-approved migration revision `2e009298612133aace095db5d57245a5b01e773a` (approval as confirmed by the developer).
- `src/services/outbound-whatsapp-admission/general-outbound-send-fence.service.ts`
- `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`
- `tests/integration/general-outbound-stop-fence.integration.test.ts`
- `tests/integration/whatsapp-contact-opt-out.integration.test.ts`
- `tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts`

No database migration source was edited from Background, and the untracked `typescript` terminal capture was excluded from the commit.

### Work Completed

- Added explicit text STOP/UNSUBSCRIBE detection at the authenticated WhatsApp inbound worker boundary, before raw-abuse rejection and ordinary routing. Validates the configured WhatsApp sender identity and canonical phone; unmatched/invalid numbers do not mutate customer records.
- Resolves quoted outbound provider messages to a verified merchant; a standalone or unresolved/mismatched quote falls back to all currently registered merchants for that canonical number. Includes multiple active CustomerPhone records per shop and across Shopify/WooCommerce shops.
- Persists durable `CUSTOMER_STOP` in the existing CustomerPhone no-contact projection, preserving existing Shopify consent evidence and prohibiting later grants or merchant re-enable from clearing STOP. Duplicate inbound delivery does not increment revisions or redate STOP.
- Publishes idempotent merchant-scoped Support SYSTEM notices after STOP persistence. Retries partial Support failures through the existing inbound job retry path, with no raw phone numbers in notice source keys or structured logs. Does not send an outbound STOP acknowledgement or mutate Shopify/WooCommerce provider consent.
- Added local no-contact checks for recovery HUMAN/AGENT/AUTOMATION send permits, other prepared WhatsApp sends, and direct routing guidance; preserves the existing moderation/handover and service-window rules.
- Corrected one TypeScript interface omission (`AdmissionDatabase.$queryRawUnsafe`) and test-only fixture isolation/eligibility issues discovered in the first validation run. No additional production STOP business logic was needed for those corrections.
- Production files modified/added by the original implementation were all under the 300-line limit (largest at that time: `outbound-message-delivery.service.ts`, 296 lines).
- **Post-review correction:** replaced general text/template no-contact preflight-only admission with a Shop-serialized final dispatch admission that follows the STOP writer's Shop-first lock order. A STOP committed before general admission prevents provider invocation; an admission committed first may already be in flight and is not retroactively withdrawn.
- Prevented already-admitted messages from being re-prepared with modified content, added a final persisted-content consistency check, and preserved idempotent rejection of duplicate dispatch attempts without incorrectly releasing reserved usage.
- Fixed test dependency injection, used distinct valid phone fixtures across concurrently executed PostgreSQL suites, and corrected Prisma's nullable dispatch-filter shape. These changes preserve standalone STOP's intended all-registered-merchants scope.
- Integrated the architect-approved forward database migration using the database submodule revision `2e009298612133aace095db5d57245a5b01e773a`; no database code or migration was changed in this Background task.

### Validation Results

Local Background implementation worktree, 2026-10-22 (terminal captures `typescript(20261022-184950)`, `typescript(20261022-185907)`, `typescript(20261022-190503)`):

- [x] `npm run build` — Prisma Client generation and TypeScript compilation passed following the interface correction.
- [x] Focused `npx vitest run` across the five requested STOP/outbound/worker test files — **65/65 passed**, after the worker mock and send-fence fixtures were corrected.
- [x] `npm run test:integration -- tests/integration/whatsapp-contact-opt-out.integration.test.ts` — **3/3 PostgreSQL tests passed**. Covered multi-shop Shopify/Woo STOP, duplicate/revision stability, newer Shopify SUBSCRIBED resync without clearing STOP, verified quoted-scope versus unresolved quote, Support notice uniqueness and resumption after partial publication.
- [x] `npm run test:arch040-moderation` — **33/33 passed** in the initial run, after the new STOP implementation was applied.
- [x] `npm run test:arch040-recovery-conversation` — **36/36 passed** after correcting the HUMAN/AGENT test fixtures.
- [x] Targeted `npx eslint` of the corrected admission/service/test files — passed with no reported errors.
- [x] `git diff --check` — passed (no whitespace errors reported).
- [x] Git staging/commit/push: `git add src tests` staged the 18 task files; the untracked `typescript` terminal recording was not committed. `git commit -m "feat(background)"` created `e85efca`; `git push` advanced `origin/task/ARCH-045-BACKGROUND-005` from `6279d89` to `e85efca` successfully.

The first validation run exposed one TypeScript interface error and five test failures (three focused unit tests and two ARCH-040 recovery tests); the incremental validation correction fixed them. The subsequent runs have no remaining reported test failures. Test totals overlap by suite and are not an assertion that every test belongs to a distinct test case.

**Post-review correction validation** (local implementation worktree, terminal captures `typescript(20261022-234349)` and `typescript(20261022-234605)`):

- [x] `npx vitest run tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts` — **23/23 passed** after the final Prisma filter correction.
- [x] `npm run test:integration -- tests/integration/general-outbound-stop-fence.integration.test.ts tests/integration/whatsapp-contact-opt-out.integration.test.ts` — **6/6 passed together** in disposable PostgreSQL. Validated STOP-first text/template admission denial, send-first ordering, duplicate admission and isolated quoted/standalone STOP fixtures.
- [x] `npm run test:arch040-recovery-conversation` — **38/38 passed** on the corrected code.
- [x] `npm run test:arch040-moderation` — **33/33 passed** on the corrected code.
- [x] `npm run build` — passed after the Prisma filter fix.
- [x] `npm run lint` — passed after the Prisma filter fix.
- [x] `git diff --check` and `git diff --cached --check` — no whitespace errors reported.
- [x] `git commit`/`git push` — committed and pushed `7361af562ca448c97b730ea881be979e0755cfca` to `origin/task/ARCH-045-BACKGROUND-005` with six paths (including the approved database gitlink), as shown in `typescript(20261022-234933)`.

These results prove the tested **general conversation text/template** fence; they do not establish transactional STOP serialization for the separate platform-level `sendRoutingGuidance()` path. Earlier failed test runs are superseded by the specified passing reruns, not erased from historical evidence.

### Git and Worktree Submission Evidence

- **Implementation repository:** `moda-interact-background`, dedicated worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-BACKGROUND-005`, branch `task/ARCH-045-BACKGROUND-005`.
- **Published implementation commit:** `e85efcaa678b7b480cca28e18759c3fbbcdf51c0` (`feat(background)`); the push output and remote task ref confirm publication. The displayed terminal log does not include a post-push local/remote `git rev-list` parity check; no such check is claimed.
- **Parent task workspace and claim:** see preserved `### Developer Claim — Attempt 1` above. The accepted `ARCH-045-DATABASE-002` gitlink at claim was `e0ab833d2e2395e3ed3cfe4aee6d07c716173e44`. These are launcher/claim facts, not newly inferred branch operations.
- **Post-review implementation commit:** `7361af562ca448c97b730ea881be979e0755cfca` (`fix(ARCH-045-BACKGROUND-005): serialize general WhatsApp sends with STOP`), published on `origin/task/ARCH-045-BACKGROUND-005`. The commit includes the database submodule gitlink at `2e009298612133aace095db5d57245a5b01e773a`.
- **Forward-migration approval and publication:** the developer reports the `ARCH-045-DATABASE-004` migration as architect-approved; GitHub confirms `2e009298612133aace095db5d57245a5b01e773a` is on `moda-interact-database/main`. No separate DATABASE-004 task acceptance record was supplied with this evidence.
- **Physical isolation:** prior claim's parent and implementation worktree evidence is preserved above. The latest terminal capture confirms execution in `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-BACKGROUND-005`, on `task/ARCH-045-BACKGROUND-005`, and a clean nested `database` checkout at the published revision. **No formal Attempt 2 claim/synchronisation packet has been recorded in the parent task** as of this report update.
- **Parent task definition:** this documentation-only patch targets the existing parent task branch. No parent review-submission commit/push is claimed until the developer applies and publishes it.

### Deviations

None from the agreed feature scope. The service uses existing bounded inbound retries and Support `sourceKey` idempotency rather than adding a queue, outbox or database table. The first validation correction changed an interface declaration and unit-test fixtures only.

### Assumptions

- The accepted `ARCH-045-DATABASE-002` `CustomerPhone` no-contact migration remains the canonical persistence contract; a later Shopify consent refresh may update the provider consent projection but not clear `CUSTOMER_STOP`.
- Regression tests exercise the Shopify resynchronisation operation consumed by consent-sync webhook handling; they do not claim an end-to-end delivery of an actual Shopify webhook through the not-yet-integrated ARCH-045-BACKGROUND-003 route.

### Unresolved Issues

No failing checks remain in the reported focused unit, PostgreSQL, ARCH-040 regression, build or lint reruns. Two matters still require explicit workflow/architect disposition: (1) the parent task must be formally reclaimed for developer Attempt 2 (it is still `ready`, Attempt 1); (2) `sendRoutingGuidance()` uses a separate platform-level outbound path with a local STOP preflight but no demonstrated Shop-serialized final admission. Do not claim every possible outbound path is race-safe until this boundary is addressed or explicitly excluded by the architect.

### Architectural Concerns

- Support notices are written **after** the committed STOP. A transient failure is retried idempotently by the bounded inbound job retry mechanism, as tested. If all retries are exhausted without another delivery/replay, notification is not guaranteed to recover automatically; STOP remains durable. This is the notification-delivery guarantee limitation anticipated by the task and does not permit outbound messaging.
- A provider send already admitted before STOP commits cannot be retracted, even if Meta submission completes afterward. For tested general text/template sends, STOP-first admission ordering is now enforced by the shared Shop lock.
- `sendRoutingGuidance()` remains a distinct platform-level send path; its no-contact preflight does not establish the same atomic send-versus-STOP linearisation as the new general conversation fence. This remains a bounded architect review question, not an assertion that the implementation has passed a routing-guidance race test.
- The Background patch consumes the published forward database migration; deployment must ensure `2e009298612133aace095db5d57245a5b01e773a` (or an accepted successor containing that migration) is deployed before the general-send fence is enabled.

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

**2026-10-22 architect coordination:** Promoted `pending -> ready` because all declared dependencies in the supplied snapshot are `complete`. Task remains unclaimed (`executor: null`, `claimed_at: null`, `attempt: 0`). This eligibility change does not materialise a branch/worktree or start implementation.

## Developer Self-Review - Changes Requested

### Finding
General prepared text and template sends call `hasLocalNoContact()` as a preflight read in `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`, but that check is not serialized with the STOP writer's Shop-row lock. A STOP can therefore commit after the general send's no-contact read and before provider dispatch. Recovery-linked sends have `OutboundSendFenceService.admitFinalSend()` for atomic admission; non-recovery sends do not. The current general-send check is not sufficient evidence that a STOP which wins the ordering blocks the subsequent provider send.

### Required Correction
Add a final no-contact admission fence for general prepared text and template sends that uses the same Shop-first serialization order as STOP. Define the admission linearization point clearly: a send whose provider admission wins before STOP may already be in flight, but if STOP obtains and commits under the shared fence first, no provider call may follow. Cover both text and template paths with a deterministic concurrency test that pauses a general send at the final admission boundary, commits STOP, then proves the provider is not called. Retain a converse ordering assertion if needed to establish the intended in-flight behavior. Rerun the focused unit slice, STOP PostgreSQL integration, ARCH-040 moderation and recovery suites, build, lint and diff checks.

### Review Validation
The independent review rerun passed: focused STOP/send/worker unit tests (65/65), STOP PostgreSQL integration (3/3), ARCH-040 moderation (33/33), ARCH-040 recovery conversation (36/36), build, targeted ESLint and committed implementation diff check. These checks do not cover the concurrency gap above; implementation changes and their deterministic regression test are required before resubmission.

### Lifecycle
Returned to `ready`; `executor` and `claimed_at` cleared. Attempt remains 1. No implementation changes, branch creation, or developer completion decision were made during review.
