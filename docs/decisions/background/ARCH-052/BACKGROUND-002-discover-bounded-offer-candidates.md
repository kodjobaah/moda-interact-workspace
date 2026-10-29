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

`recovery-offer-repository.ts` filters isAvailable=true regardless of mode; `candidateKind` treats selection as provider eligibility; MAX_CANDIDATES=8 suppresses larger catalogues. That is wrong after isAvailable is standardised as merchant selection.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- In `src/services/recovery-offers/recovery-offer-repository.ts` implement keyset page reader by `(id ASC)` for `shopId`, fixed page size 100, at most 5000 catalogue rows. Require catalogue status CURRENT, latest generation and absence of row.unavailableAt before an offer is a candidate. Page includes `isAvailable` only for merchant selection, never as provider status.
- FIXED reads only the frozen `authorisedDiscountIds` from attempt snapshot (1..50); validate exact same shop and provider identity, and do not add unchecked rows. AI reads ALL current catalogue rows regardless of `isAvailable`, across pages; NONE does zero repository/provider/model reads.
- Replace `candidateKind` `!row.isAvailable` exclusion with provider-specific required liveness checks (`providerStatus`, `unavailableAt`, dates, fixedSelectable and provider snapshot). Stop treating merchant selection as provider fact. Unsupported families are excluded from eligible shortlist; do not invent codes or calculate savings.
- Static prefilter: exclude expired/inactive, wrong platform, non-deliverable code, incompatible currency and provably inapplicable product/variant sets. Product category is optional relevant metadata, never sole eligibility evidence. Maintain stable order by ID; deduplicate with set.
- Use maximum 5000 scanned rows, maximum 50 FIXED selected IDs, maximum 24 live provider verifications per INITIAL attempt and concurrency at most 4. If >5000 rows or incomplete pagination, return `CATALOGUE_INCOMPLETE` NO_OFFER (add reason type); if >24 plausibly eligible AI candidates, mark shortlist partial and still consider only the deterministically first 24, never claim globally optimal savings.
- Remove MAX_CANDIDATES=8 rejection; bounded timeout/partial-result counters use shared logger (count/reason only). Never perform provider calls on raw webhooks; this remains delayed actionable recovery work.
- Add SQL/unit fixtures: 3 selected among 20, 12 selected (no eight cap), 150 unselected AI candidates, 5,001 rows fail closed, stale gen, provider-status invalid, two shops and no duplicate pages.

## Out of Scope

- No provider calls that prove a customer-specific coupon, no AI model and no outgoing message.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- AI is allowed to recommend only among independently verified evaluated candidates; scan-wide completeness != verification of every record.
- No provider calls during transaction, no full-scan in Shopify webhook hot path.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement shop-scoped paginated candidate discovery and provider-status filters.
- [ ] Remove legacy eight-candidate gating and define 5000/50/24/4 budgets.
- [ ] Add large catalogue and mode-isolation tests.

## Interfaces / Contracts

- `RecoveryOfferRepository.readDiscountPage(shopId,afterId,take=100)` plus explicit completeness; `candidateKind(platform,row,now)` excludes provider-ineligible independently of selection.
- `NoOfferReason` extends with `CATALOGUE_INCOMPLETE`; producer and consumer names match.

## Dependencies

- `ARCH-052-BACKGROUND-001` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-003`

## Acceptance Criteria

- [ ] FIXED evaluates only saved-authorised set; AI can evaluate unchecked rows; NONE makes no discount-catalogue, discount-proof or AI calls (the separate optional product-image reader is unaffected).
- [ ] No positive discount for stale, unsupported or unknown-rule candidates.

## Validation

- [ ] Background repository/resolver tests, SQL query plan/index inspection, no schema migration.
- [ ] Background declared typecheck/lint and `git diff --check`.

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
