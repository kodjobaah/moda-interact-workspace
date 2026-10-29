---
id: ARCH-052-BACKGROUND-002
architecture_id: ARCH-052
title: Discover all relevant catalogue candidates with bounded pagination
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-BACKGROUND-001
enables:
- ARCH-052-BACKGROUND-003
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-BACKGROUND-002: Discover all relevant catalogue candidates with bounded pagination

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Build an exhaustive-within-declared-limits and tenant-scoped candidate shortlist for FIXED and AI without treating selection as eligibility.

## Context

`src/services/recovery-offers/recovery-offer-repository.ts` currently filters `isAvailable:true` for both platforms and `recovery-offer-resolver.service.ts` returns CANDIDATE_LIMIT above eight. Woo isAvailable means merchant checkbox; Shopify isAvailable means provider availability.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Refactor the existing recovery-offer candidate repository to distinguish platform/provider active status from merchant-selected authorisation and use sorted bounded keyset pagination.
- For FIXED, consider exactly the frozen selected set; for AI, scan all current provider-identifiable catalogue rows within the configured safe limit, regardless of Woo checkbox flags.
- Apply safe static prefilters against checkout items, currency, provider metadata, lifecycle and supported coupon/discount families; do not claim product category alone proves eligibility.
- Prioritise a bounded independently evaluated shortlist. If complete scanning is impossible, report a typed truncated/oversize outcome rather than silently considering the first eight as the entire catalogue.

## Out of Scope

- No provider calls that prove a customer-specific coupon, no AI model and no outgoing message.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- No full-table scans on common webhook ingress. Only actionable INITIAL recovery paths perform discovery.
- Preserve a 50-ID merchant selection max and separate the catalogue scan ceiling from live verification concurrency/cost ceilings.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Split Shopify/Woo availability filtering and add cursor-based discovery.
- [ ] Implement bounded deterministic shortlist/limit handling.
- [ ] Test many-coupon, wrong-shop, partial-pages and changed-policy states.

## Interfaces / Contracts

- Maintain `RecoveryOfferRepository` and `candidateKind` boundaries in `src/services/recovery-offers/`; adopt a cursor/page result and explicit completeness flag.

## Dependencies

- `ARCH-052-BACKGROUND-001` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-003`

## Acceptance Criteria

- [ ] AI Woo scans unselected active coupons; FIXED never sees unchecked merchant options.
- [ ] More than eight catalogue records does not automatically suppress the entire AI mode.
- [ ] Incomplete or stale catalogue never becomes a false positive eligible offer.

## Validation

- [ ] Focused repository/selection tests and SQL query/index evaluation for large catalogues.
- [ ] Background build/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/recovery-offers/recovery-offer-repository.ts`
- `moda-interact-background/src/services/recovery-offers/recovery-offer-resolver.service.ts`
- `moda-interact-background/src/services/recovery-offers/recovery-offer-providers.ts`

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
