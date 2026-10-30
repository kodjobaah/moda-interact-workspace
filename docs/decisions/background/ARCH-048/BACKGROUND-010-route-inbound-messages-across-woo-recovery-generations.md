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
status: in_progress
priority: 42
executor: codex
claimed_at: 2026-10-30T09:46:34Z
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

Implementation and validation are complete locally. Task remains `in_progress` while implementation-branch publication awaits authorization for the configured remote. The Architect Review section remains pending and unmodified.

### Files Changed

- `src/services/recovery-routing.service.ts`
- `src/services/whatsapp-inbound-processing.service.ts`
- `tests/unit/services/recovery-routing.service.test.ts`
- `tests/unit/services/whatsapp-inbound-processing.service.test.ts`
- `tests/unit/workers/whatsapp.worker.test.ts`
- `tests/integration/woo-recovery-inbound-routing.integration.test.ts`

### Work Completed

`RecoveryRoute` now distinguishes active from historical conversations. Unreferenced replies consider only provider-confirmed outbound conversations whose recovery is `MESSAGE_SENT` or `ENGAGED`, select the newest generation within each `(shopId, checkoutToken)` lineage, and remain ambiguous when more than one eligible shop/checkout owner matches. The latest generation and status are rechecked before turn scheduling.

Explicit replies continue to the exact outbound conversation after it closes. Previously stored inbound message IDs stay pinned to their persisted conversation. Historical text and unsupported content are inserted idempotently without changing pending-turn state; historical audio is reserved on its original conversation without transcription, fallback sends or turn scheduling. Closed/superseded routes do not stamp checkout activity or enqueue AI work. STOP, abuse admission, shop eligibility and the existing active Shopify path remain in place. Routing decisions use Shared structured logging with a bounded digest of the provider message ID.

Implementation commit: `753c17184347215dd309e2f9bb74dc09e4820676` (`feat(background): route replies across Woo recovery generations`), local branch `task/ARCH-048-BACKGROUND-010`.

### Validation Results

- Focused routing, inbound-processing and WhatsApp worker unit tests: 61 passed across 3 files.
- PostgreSQL multi-generation routing integration tests via `node scripts/test-integration.mjs tests/integration/woo-recovery-inbound-routing.integration.test.ts`: 2 passed. The test uses Colima's disposable PostgreSQL and verifies latest-generation routing, historical context routing, cross-shop ambiguity and suppression when the latest generation has not sent.
- `npm run build`: Prisma generation and TypeScript build passed.
- Focused ESLint on all 6 changed files: passed.
- `git diff --check`: passed.

### Deviations

No implementation or contract changes outside the task scope. Historical inbound persistence intentionally does not update the conversation turn version, preventing an already queued turn from consuming a closed-generation reply.

### Assumptions

The launcher preparation packet is authoritative for worktree, synchronization, dependency-gate, submodule and claim evidence. PostgreSQL recovery rows and their generation/status are the durable authority for current inbound ownership.

### Unresolved Issues

The implementation branch has not been published. Its configured origin is `https://github.com/kodjobaah/moda-interact-background.git`; the task parent origin is `https://github.com/kodjobaah/moda-interact-workspace.git`. The implementation commit remains local pending authorization. No publish attempt or workaround was made in this task. The parent report update is being committed locally; task status therefore remains `in_progress`.

### Git / VCS Evidence

Task branch: `task/ARCH-048-BACKGROUND-010`.

Physical worktree isolation:

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-BACKGROUND-010` / `task/ARCH-048-BACKGROUND-010`
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-BACKGROUND-010` / `task/ARCH-048-BACKGROUND-010`
- Both worktrees were newly created for this task; no other task worktree was reused.
- Shared workspace and implementation source checkouts were not switched or mutated for task implementation; no submodule gitlink was staged.

Start-of-attempt synchronization:

- Parent task branch fast-forward: not needed; `origin/main` incorporated: already current.
- Implementation task branch fast-forward: not needed; `origin/main` incorporated: already current.
- Recursive submodule sync and update: passed; `database` at `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`.
- Launcher claim: Attempt 1 by `codex`, parent claim commit `baa21314da7f71e2437f953d53fcd9e36aad2768`, pushed successfully.

Implementation repository: commit `753c17184347215dd309e2f9bb74dc09e4820676`; origin `https://github.com/kodjobaah/moda-interact-background.git`; task branch push pending authorization.

Parent workspace: this task file is updated on `task/ARCH-048-BACKGROUND-010`; origin `https://github.com/kodjobaah/moda-interact-workspace.git`; report commit is local and not pushed. No submodule gitlink is staged.

Neither task branch has been merged to `main`.

### Architectural Concerns

No new concerns. The architecture's existing event-only completeness limitation remains unchanged.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
