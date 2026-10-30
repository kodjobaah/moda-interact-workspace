---
id: ARCH-048-BACKGROUND-010
architecture_id: ARCH-048
title: Route WhatsApp replies safely across Woo recovery generations
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 42
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-048-BACKGROUND-007
enables:
  - ARCH-048-BACKGROUND-011
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-048-BACKGROUND-010 — Route WhatsApp replies safely across Woo recovery generations

## Architecture

Architecture ID: `ARCH-048`.

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`.

Coordinator: `moda_architect`. Originally defined from the 2026-10-29 source snapshot, then materialised on the parent task branch before execution. On 2026-10-30 the launcher verified BG007 Complete, prepared dedicated parent and implementation worktrees, and claimed Attempt 1.

## Objective

Distinguish the **current eligible Woo recovery conversation** from an older historical generation so customers' inbound messages never revive a closed recovery or become ambiguously associated merely because several generations have sent messages.

## Context

Current `RecoveryRoutingService.resolveInboundMessage()` (`src/services/recovery-routing.service.ts`) counts distinct outbound recovery conversations for an unreferenced number **across all shops and statuses**; once two generations have sent an initial, it can return `MULTIPLE_RECOVERIES` for the same customer and checkout. Explicit `contextMessageId` already refers to a particular historical conversation. `processRoutedInboundMessage()` currently records activity on any resolved recovery and queues an AI turn. This needs generation-aware routing, not a second WhatsApp conversation table.

## Scope

**Permitted Background implementation files:**

- `src/services/recovery-routing.service.ts` — owner of revised `RecoveryRoute` local result and recipient/shop/recovery candidate selection.
- `src/services/whatsapp-inbound-processing.service.ts` — narrowly consume `route.mode` and persist historical inbound without enqueuing obsolete recovery automation or advancing the old checkout generation.
- `src/workers/whatsapp.worker.ts` and `src/services/routing-guidance.service.ts` — **only** if a focused test proves a required change for the revised route result; no generic pipeline refactor.
- `tests/unit/services/recovery-routing.service.test.ts`, focused `whatsapp-inbound-processing`/worker tests, and a PostgreSQL-backed multi-generation routing integration test if the unit fixtures cannot demonstrate SQL query behaviour.

Read, but **do not edit**, `src/services/whatsapp-conversation-routing.service.ts` unless the architectural review proves this separate general-purpose route is used for the target inbound path; escalate before broadening scope. Do not change Woo checkout capture, candidate/admission/outreach, database schema, Meta ingress schema, Shared/Shopify or billing.

## Out of Scope

No new messaging webhook, merchant settings or WhatsApp template, no automatic sending from old generations, no migration, no reentry cap/cooldown, no changes to the CommerceAgent prompt. This is routing/persistence only.

## Requirements

1. **Keep the existing global safeguards.** First verify the canonical Meta provider account and phone-number identity, resolve sender phone using the accepted normalization contract, and preserve existing priority STOP/no-contact, inbound abuse admission, moderation, provider-message deduplication and merchant shop execution checks. Never infer a shop from a checkout key or phone alone. A reused number shared by multiple shops/customers must remain ambiguous unless the original message context proves ownership.
2. **Explicit reply (`contextMessageId`) wins:** find the specific outbound `ConversationMessage` by provider ID; prove direction `OUTBOUND`, provider confirmation, recipient identity and conversation/recovery ownership. Route that reply to **that exact conversation even when its recovery is now `CANCELLED`/historical**; never silently switch an explicit reply from generation N to generation N+1. Invalid/foreign/unsent context returns existing `INVALID_REFERENCE` guidance. Existing previously stored inbound duplicates must remain pinned to their original conversation.
3. **Unreferenced text (no context and no existing stored inbound):** query the distinct eligible **current** recovery conversations for the authenticated sender, considering status `MESSAGE_SENT`/`ENGAGED`, their shop/customer identity and confirmed outbound message. Within one shop+checkout lineage, multiple historical generations do not cause ambiguity; the newest generation is the eligible candidate. If exactly one eligible conversation remains **across all shops**, route there. If several truly distinct eligible shop/checkout owners remain, return `MULTIPLE_RECOVERIES` (do **not** pick the most recent globally). If no eligible current conversation exists, return `NO_RECOVERY` guidance, not an arbitrary historical route.
4. **Historical replies are stored, not resumed.** Extend local `RecoveryRoute` resolved case with required `mode: "active" | "historical"`. `historical` applies when explicit context or a previously stored inbound message points to a non-continuing/closed recovery. `processRoutedInboundMessage` must preserve the original conversation and provider-message identity (including text/audio/unsupported content where supported), but must **not** call `checkoutRecoveryService.recordExternalActivity()` for that closed recovery, enqueue a CommerceAgent/AI turn, initiate recovery outreach, or promote it back to `ENGAGED`. A safe guidance or human-support handling path may be used only if an existing approved mechanism permits it; do not fabricate a new automated send.
5. **Current replies** preserve existing message persistence, turn ownership, abuse/moderation and AI/human control behaviour; do not change established Shopify current-recovery routing semantics. If a Woo generation is `DETECTED` but has not sent any provider-confirmed outbound, it is **not** an unreferenced-inbound conversation candidate.
6. **Concurrency:** an unreferenced reply processed while generation N is being closed cannot be assigned to N on stale status if N+1 is current. Re-read or fence the selected recovery's latest status/generation at the point of resolution and before scheduling an automated turn. If an unambiguous owner cannot be established under the race, use guidance/fail closed instead of guessing. Duplicate inbound processing remains idempotent and cannot enqueue two turns.
7. **No historical automation bypass:** any terminal conversation message still handled for audit must pass the existing outbound admission policy for human/support messages. Do not permit a closed-generation recovery to create offers, follow-ups, initial outreach, AI recovery turns or a second message via routing.
8. Use Shared structured logging for routing decisions and failures, with bounded shop/recovery/conversation ID, mode/reason; do not log raw recipient number, message contents or tokens. Log unexpected errors and rethrow so the existing inbound retry/dead-letter path can act.

## Work Items

- [x] Add and consume `RecoveryRoute.mode` with verified current/historical classification.
- [x] Implement Woo lineage-aware unreferenced selection without relaxing cross-shop ambiguity.
- [x] Preserve exact outbound-context routing to old conversations and dedup of repeated provider messages.
- [x] Prevent activity stamps and AI/automation work for historical routes across content types.
- [x] Test active, historical, mixed-shop, concurrency, STOP and Shopify regression scenarios.

## Interfaces / Contracts

- **Input:** existing `WhatsAppInboundEvent` and stored `ConversationMessage.providerMessageId`/`contextMessageId`; no new Meta wire fields.
- **Local result:** `RecoveryRoute` resolved `{kind:"resolved", conversationId, checkoutRecoveryId, shopId, mode:"active"|"historical"}`; preserve existing `guidance` reasons and `ignored`. This is **local to Background**, not a Shared contract.
- **DB:** existing `Conversation`, `ConversationMessage`, `CheckoutRecovery(generation,status)`, `Customer`, `CustomerPhone`; no new table. Confirmed outbound evidence is required for unreferenced routing.
- **Consumers:** `processRoutedInboundMessage()` and existing authorized turn-processing path; STOP must remain before routing.

## Dependencies

- `ARCH-048-BACKGROUND-007` — accepted Complete; establishes documented generation/resumption semantics.

## Enables

- `ARCH-048-BACKGROUND-011` — final integration regression checks.

## Acceptance Criteria

- [x] Generation 1 closed and generation 2 with confirmed outbound: unreferenced response routes to **generation 2** when it is the sole eligible owner, not `MULTIPLE_RECOVERIES`.
- [x] Explicit reply to generation 1's earlier provider message remains stored on generation 1's historical conversation and causes **no recovery automation** for generation 1.
- [x] Two different eligible shops/checkouts sharing the phone remain ambiguous; no silent most-recent cross-shop selection.
- [x] Forged/unsent provider context, unregistered sender or mismatched phone cannot link to any generation.
- [x] STOP still takes priority; current conversation AI/human ownership, inbound moderation and dedup are preserved.
- [x] Closure/reentry race does not revive old recovery, misroute, duplicate inbound or enqueue an obsolete AI turn.
- [x] Existing Shopify routing unit tests remain passing.

## Validation

- [x] `npx vitest run tests/unit/services/recovery-routing.service.test.ts` and focused new inbound-processing/worker tests.
- [x] PostgreSQL-backed multi-generation routing test using the existing `node scripts/test-integration.mjs` runner if needed; include both same-checkout and cross-shop candidate SQL behaviour.
- [x] `npm run build`, focused lint as available, `git diff --check`; record exact command/results and any known baseline.

## Stop Condition

When routing and historical-message protection are validated, record the Completion Report, set `status: review`, return to `moda_architect` and **STOP**. Do not begin BG011 or implement checkout/admission/outreach logic here.

## Implementation Notes

Use exact launcher-prepared dedicated parent/implementation worktrees, with physical-isolation, synchronization, submodule and branch evidence. Avoid a broad WhatsApp service rewrite; keep changes bounded to the recovery inbound path that is actually invoked. Existing consent/STOP and provider-aware sends are separate security boundaries; never weaken them for convenience. If an unrelated routing path is in fact the active consumer, report concrete callsites to the architect before editing it.

## Completion Report

### Status

Attempt 1 implementation and validation are complete and both mirrored task branches are published. The Shopify routing finding recorded below was corrected in implementation commit `4be9ab3365390e93bdec2fab31dd3e87a5203cf4`; this review requests one remaining bounded-logging correction. The task returns to `ready` at Attempt 1.

### Files Changed

- `src/services/recovery-routing.service.ts`
- `src/services/whatsapp-inbound-processing.service.ts`
- `tests/unit/services/recovery-routing.service.test.ts`
- `tests/unit/services/whatsapp-inbound-processing.service.test.ts`
- `tests/unit/workers/whatsapp.worker.test.ts`
- `tests/integration/woo-recovery-inbound-routing.integration.test.ts`

### Work Completed

`RecoveryRoute` now distinguishes active from historical conversations. Unreferenced replies consider only provider-confirmed outbound conversations whose recovery is `MESSAGE_SENT` or `ENGAGED`, select the newest generation within each `(shopId, checkoutToken)` lineage, and remain ambiguous when more than one eligible shop/checkout owner matches. The latest generation and status are rechecked before turn scheduling.

Follow-up for the 2026-10-30 P1 review finding: generation/status candidate filtering and the latest-generation recheck now apply only to WooCommerce shops. Shopify unreferenced routing retains the prior all-status, all-generation candidate set, including ambiguity from an older terminal generation. Added unit coverage for Shopify route classification and a PostgreSQL regression proving an older cancelled Shopify recovery still produces `MULTIPLE_RECOVERIES`; the existing Woo integration fixtures now explicitly declare `WOOCOMMERCE` so they exercise the intended platform branch.

Explicit replies continue to the exact outbound conversation after it closes. Previously stored inbound message IDs stay pinned to their persisted conversation. Historical text and unsupported content are inserted idempotently without changing pending-turn state; historical audio is reserved on its original conversation without transcription, fallback sends or turn scheduling. Closed/superseded routes do not stamp checkout activity or enqueue AI work. STOP, abuse admission, shop eligibility and the existing active Shopify path remain in place. Routing decisions use Shared structured logging with a bounded digest of the provider message ID.

Implementation commits: `753c17184347215dd309e2f9bb74dc09e4820676` (`feat(background): route replies across Woo recovery generations`) and `4be9ab3` (`fix(background): scope generation routing to Woo`), local branch `task/ARCH-048-BACKGROUND-010`.

### Validation Results

- After the review correction, focused routing, inbound-processing and WhatsApp worker unit tests: 62 passed across 3 files.
- The focused routing suite contains 23 tests, including the Shopify route-classification regression.
- PostgreSQL multi-generation routing integration tests via `node scripts/test-integration.mjs tests/integration/woo-recovery-inbound-routing.integration.test.ts`: 3 passed. The tests use Colima's disposable PostgreSQL and verify Woo latest-generation routing, historical context routing, cross-shop ambiguity, suppression when the latest generation has not sent, and Shopify ambiguity across an older cancelled generation.
- Focused ESLint on `src/services/recovery-routing.service.ts`, `tests/unit/services/recovery-routing.service.test.ts` and `tests/integration/woo-recovery-inbound-routing.integration.test.ts`: passed.
- After the review correction, `npm run build`: Prisma generation and TypeScript build passed.
- `npm run build`: Prisma generation and TypeScript build passed.
- Focused ESLint on all 6 changed files: passed.
- `git diff --check`: passed.

### Deviations

No implementation or contract changes outside the task scope. Historical inbound persistence intentionally does not update the conversation turn version, preventing an already queued turn from consuming a closed-generation reply.

### Assumptions

The launcher preparation packet is authoritative for worktree, synchronization, dependency-gate, submodule and claim evidence. PostgreSQL recovery rows and their generation/status are the durable authority for current inbound ownership.

### Unresolved Issues

The current implementation review requests replacing raw exception objects in the two new failure logs with bounded, non-sensitive error metadata and adding a regression test proving phone/message sentinels are absent from logs. The implementation and parent task branches are published; no code correction for this finding is included yet.

### Git / VCS Evidence

Task branch: `task/ARCH-048-BACKGROUND-010`.

Physical worktree isolation:

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-BACKGROUND-010` / `task/ARCH-048-BACKGROUND-010`
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-BACKGROUND-010` / `task/ARCH-048-BACKGROUND-010`
- Both worktrees were newly created for this task; no other task worktree was reused.
- The shared workspace and implementation source checkouts were not switched. The task worktree reused the implementation checkout's ignored `node_modules` through a local symlink; Prisma client generation updated only that ignored dependency output, and no tracked source files changed. No submodule gitlink was staged.

Start-of-attempt synchronization:

- Parent task branch fast-forward: not needed; `origin/main` incorporated: already current.
- Implementation task branch fast-forward: not needed; `origin/main` incorporated: already current.
- Recursive submodule sync and update: passed; `database` at `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`.
- Launcher claim: Attempt 1 by `codex`, parent claim commit `baa21314da7f71e2437f953d53fcd9e36aad2768`, pushed successfully.

Implementation repository: task branch `task/ARCH-048-BACKGROUND-010`, HEAD `4be9ab3365390e93bdec2fab31dd3e87a5203cf4`, published to `origin/task/ARCH-048-BACKGROUND-010`.

Parent workspace: task report is published on `task/ARCH-048-BACKGROUND-010` at `6da58fe8e41248d2e99f8809edb9174a7a873953` before this review update. No submodule gitlink is staged.

Neither task branch has been merged to `main`.

### Architectural Concerns

No new concerns. The architecture's existing event-only completeness limitation remains unchanged.

## Architect Review — Earlier Shopify Finding

### Review Status

Changes Requested — the first implementation review found a Shopify routing compatibility regression. This finding is resolved by the later platform-scoped correction in `4be9ab3365390e93bdec2fab31dd3e87a5203cf4` and its added tests.

### Review Notes

- **P1 — Preserve existing Shopify unreferenced-routing semantics.** In `src/services/recovery-routing.service.ts:132-138`, the status and latest-generation predicates are applied to candidates across all platforms. This changes Shopify behavior as well as Woo behavior: a phone that previously remained ambiguous because it had historical outbound recovery conversations can now resolve to one remaining current candidate. That can associate an unreferenced reply with the wrong Shopify checkout. The task limits generation-aware selection to Woo and explicitly requires existing Shopify current-recovery routing semantics to remain unchanged.
- Scope the new status/generation selection to Woo recoveries and retain the pre-change candidate rules for Shopify. Add regression coverage that proves both Woo latest-generation routing and Shopify ambiguity/current-routing behavior.

### Reviewed Files

- `src/services/recovery-routing.service.ts` — candidate selection and route recheck.
- `src/services/whatsapp-inbound-processing.service.ts` — historical persistence, activity recording and turn enqueue paths.
- `tests/unit/services/recovery-routing.service.test.ts` — routing query and route classification coverage.
- `tests/integration/woo-recovery-inbound-routing.integration.test.ts` — PostgreSQL Woo generation routing scenarios.
- `docs/decisions/background/ARCH-048/BACKGROUND-010-route-inbound-messages-across-woo-recovery-generations.md` — scope, requirements and reported validation.

### Validation Reviewed

At the time of that review, the report recorded 61 focused unit tests and 2 PostgreSQL routing integration tests. The later Attempt 1 correction report records 62 focused unit tests and 3 PostgreSQL integration tests, including Shopify regression coverage; these results were reviewed as submitted and were not independently rerun.

### Architecture Conformance

Partial. Historical routing, persistence and concurrency safeguards appear aligned with the stated requirements. Shopify compatibility is not satisfied until candidate selection is platform-scoped and regression-tested.

### Follow-up

Correct platform-specific candidate selection, add and run focused Shopify regression coverage alongside the Woo routing tests, then update this review section with the resulting evidence. Do not mark the task accepted until that finding is resolved.


## Architect Review — Attempt 1 (Changes Requested)

### Decision

Changes Requested. The earlier Shopify routing compatibility finding is resolved: the current SQL applies status/latest-generation filtering only to WooCommerce, and the report records a Shopify regression test for older cancelled generations. One bounded-logging issue remains.

### Finding

- **P2 — Do not log raw exception objects.** `RecoveryRoutingService.resolveInboundMessage()` and `processRoutedInboundMessage()` pass caught exceptions directly as `error` fields to the Shared logger. Database/provider exceptions may include query values, recipient numbers, message text or provider data. This conflicts with the task's bounded, non-sensitive logging requirement. Log a fixed error code and bounded error class (or similarly safe metadata) while rethrowing the original exception unchanged. Add a regression test with sensitive sentinel values proving neither log contains the raw number/message or exception text.

### Reviewed Files

- `src/services/recovery-routing.service.ts` — Woo-only generation filtering, Shopify legacy candidate behavior, and routing error logging.
- `src/services/whatsapp-inbound-processing.service.ts` — historical persistence/turn suppression and processing error logging.
- `tests/unit/services/recovery-routing.service.test.ts`
- `tests/unit/services/whatsapp-inbound-processing.service.test.ts`
- `tests/integration/woo-recovery-inbound-routing.integration.test.ts`
- Completion Report and worktree/publication evidence in this task record.

### Validation Reviewed

Attempt 1 correction evidence records 62 focused unit tests across 3 files and 3 PostgreSQL integration tests passing, including Woo generation selection and Shopify historical ambiguity. Focused ESLint, build and `git diff --check` passed. No tests were rerun during this architect review.

### Architecture Conformance

The Woo generation selection is platform-scoped and the reported Shopify regression is covered. Historical explicit/stored-context handling and automation suppression align with the task contract. Acceptance remains withheld until the two failure logs are bounded and a privacy regression test passes.

### Required Follow-up

Sanitize the routing and processing failure log fields, preserve exception propagation, and add the sensitive-sentinel regression coverage. Keep Attempt 1 unchanged; no source or test correction for this finding is included in this review update.
