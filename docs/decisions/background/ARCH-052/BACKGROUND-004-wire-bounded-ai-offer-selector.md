---
id: ARCH-052-BACKGROUND-004
architecture_id: ARCH-052
title: Connect approved AI recommendation to verified offer shortlist
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-BACKGROUND-003
enables:
- ARCH-052-BACKGROUND-008
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-BACKGROUND-004: Connect approved AI recommendation to verified offer shortlist

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Let AI select one offer ID from a bounded, independently verified and merchant-authorised shortlist, with no capability to invent or apply a discount.

## Context

The `ReadOnlyOfferRecommender` interface exists, but `RecoveryOfferResolver` is constructed with `ai:null`, so AI_BEST_APPLICABLE resolves AI_UNAVAILABLE.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Implement a read-only AI adapter reusing existing approved shared model/runtime configuration (no new LLM client framework).
- Supply only safe structured context: verified IDs, savings, kind, currency and bounded non-sensitive checkout item/category summary; never send raw customer contact or checkout URL.
- Enforce model output schema as exactly one candidate ID, cost/token/time budgets, retry/circuit behaviour and positive server-side membership check against verified shortlist.
- Wire the production instance for INITIAL outreach only; no AI call in NONE/FIXED; if AI fails or makes an invalid choice, record bounded diagnostic and select NO_OFFER unless architecture explicitly agrees a deterministic fallback.

## Out of Scope

- No eligibility verdict from AI, cart/coupon mutation, new conversation turn, merchant-facing AI template edits or usage billing changes.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- All candidates must be independently verified immediately before shortlist presentation; AI cannot expand allowed candidate universe.
- AI/model exceptions are logged/rethrown or converted into documented typed controlled failure; no silent swallow.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Build prompt-free structured offer recommender using approved model adapter.
- [ ] Wire into recovery offer resolver production composition.
- [ ] Test valid ID, hallucinated ID, model unavailable/timeouts and zero LLM in NONE/FIXED.

## Interfaces / Contracts

- Existing `ReadOnlyOfferRecommender.recommend` in `src/services/recovery-offers/recovery-offer.types.ts`; published shared model runner where compatible.

## Dependencies

- `ARCH-052-BACKGROUND-003` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-008`

## Acceptance Criteria

- [ ] AI can pick only a verified candidate or yield NO_OFFER.
- [ ] No AI-selected invalid code or discount value reaches a WhatsApp parameter.

## Validation

- [ ] Deterministic mocked-model unit and integration tests for budget, PII absence and provider failure.
- [ ] Background build/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/recovery-offers/ (new AI adapter)`
- `moda-interact-background/src/services/recovery-offers/recovery-offer-resolver.service.ts`
- `moda-interact-background/tests/unit/services/recovery-offers/`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

## Completion Report

### Status

Not Started — portable definition, no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Execution will verify its current workspace, source state, dependency versions and test harness.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.


## Architect Review

### Review Status

Pending.

### Review Notes

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
