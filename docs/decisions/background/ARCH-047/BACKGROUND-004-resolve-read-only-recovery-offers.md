---
id: ARCH-047-BACKGROUND-004
architecture_id: ARCH-047
title: Implement read-only recovery offer resolution module
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 25
executor: developer
claimed_at: 2026-10-26T03:02:29Z
attempt: 1
depends_on: []
enables:
  - ARCH-047-BACKGROUND-006
  - ARCH-047-BACKGROUND-007
created: 2026-10-24
updated: 2026-10-26
---

# Implement read-only recovery offer resolution module

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

This is a **portable task definition** prepared from the 24 October 2026 workspace snapshot and consolidated DB001 Attempt 7 contract. It is not a repository implementation, task claim or evidence of a created worktree/branch. No new ARCH-047 Shared package is assumed. The parent architecture and `BACKGROUND-001` require reconciliation to the final Admin-owned AST/compilation and DB-backed keyed-segment translation decisions before dependent work is promoted.

## Objective

Compute a verified NO_OFFER, CODE_OFFER or AUTOMATIC_OFFER decision from merchant recovery policy and current read-only checkout/discount evidence.

## Context

ARCH-047 permits only immutable, Moda Admin-authored template definitions. Admin validates and compiles the AST and persists already-prepared transport/runtime data. Background handles independently testable execution modules and **never re-parses the Admin authoring AST**. The DB001 schema provides translation runs/items/batches, compiled Meta registrations, publication targets and wrapper pointers. Messaging delivers Meta template status observations through the existing BullMQ path; Background persists/assesses them. Existing outbound admission remains authoritative.

## Scope

- Add `src/services/recovery-offers/` with a small `RecoveryOfferResolver` facade, policy strategies for NONE/FIXED/AI_BEST_APPLICABLE, read-only discount/checkout provider adapters and deterministic eligibility verification.
- Reuse `RecoveryPolicyService`, existing Shopify discount/eligibility tools, Woo coupon catalogue/normalisation, and Commerce's approved read-only discount capabilities where actually available. Keep customer-specific offer evaluation on the **actionable recovery path**, not the raw webhook hot path.
- Return an immutable, typed offer-decision value for `BACKGROUND-001`/integrations; preserve existing policy snapshot meanings unless deliberately changed by a separate owning task.

## Out of Scope

- No Meta template selection, AST processing, template translation, parameter rendering, checkout or basket writes, discount creation/application, AI cart tools or changing tenant-owned checkout state.
- No unrelated Woo coupon grant/discount dispatcher refactor, no `ARCH-047-DATABASE-001` schema expansion merely for offer ranking, no merchant UI changes and no independent outbound admission/billing.

## Requirements

**R1 — Pure decision boundary.** Given verified `shopId`, checkout/recovery identifier, stage, policy snapshot, checkout currency/contents and candidate discounts, return `{kind:'NO_OFFER'}` or a `CODE_OFFER` / `AUTOMATIC_OFFER` with provider-verified identifier, display description, parameters, evidence source/time and applicable constraints. This value is **Background-local**, not a new published Shared type.

**R2 — NONE and FIXED.** NONE performs no AI/discount eligibility operations. FIXED restricts candidates to the merchant-authorised set; one selection is validated, multiple eligible options follow a **deterministic documented rule** (e.g. verified maximum checkout savings, with stable tie-breaking), not an LLM call. Do not treat a Woo compatibility/anchor discount ID as proof of a final selected coupon. Handle Shopify/Woo differences explicitly; do not invent provider-level automatic-discount support.

**R3 — AI mode.** Only `AI_BEST_APPLICABLE` may invoke a bounded, approved read-only AI recommendation using verified candidate evidence. Return only a candidate the application independently validates against current provider rules and checkout; never trust invented codes, prices or eligibility asserted by the LLM. Do not route through an artificial customer message or create a conversation turn solely to select an offer. If required trustworthy provider evaluation is unavailable, return `NO_OFFER` and report a bounded capability gap to the architect.

**R4 — Failure and follow-up.** Expired/missing/ambiguous offers, provider outages, stale checkout, wrong currency/shop, invalid coupon eligibility or inconclusive AI produce `NO_OFFER` or a typed controlled failure rather than customer-facing promises. For sequence two, prefer the previously promised offer only if currently valid; any replacement requires explicit agreed policy; never advertise conflicting offers.

**R5 — Security and cost.** Strictly read-only provider calls; do not add/remove basket items, update quantities, apply coupons, change discounts or place orders. Enforce per-tenant checkout scope, timeouts/rate limits and bounded AI costs. Observe decisions with non-sensitive identifiers, not coupon/customer secrets.

## Work Items

- [ ] Add `src/services/recovery-offers/` with a small `RecoveryOfferResolver` facade, policy strategies for NONE/FIXED/AI_BEST_APPLICABLE, read-only discount/checkout provider adapters and deterministic eligibility verification.
- [ ] Reuse `RecoveryPolicyService`, existing Shopify discount/eligibility tools, Woo coupon catalogue/normalisation, and Commerce's approved read-only discount capabilities where actually available. Keep customer-specific offer evaluation on the **actionable recovery path**, not the raw webhook hot path.
- [ ] Return an immutable, typed offer-decision value for `BACKGROUND-001`/integrations; preserve existing policy snapshot meanings unless deliberately changed by a separate owning task.
- [ ] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [ ] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

## Interfaces / Contracts

**Background-local port:** `resolveRecoveryOffer(input: {shopId, checkoutRecoveryId, stage, policy, now}): Promise<RecoveryOfferDecision>`. The decision is not a Meta payload; `BACKGROUND-001` maps a **verified** decision and stage to its template purpose. Read-only Commerce tools and provider adapters are dependencies to inspect, not authority to implement cross-repository changes here.

**Existing providers**: `src/services/recovery-policy.service.ts`, Shopify discount evaluator, `woo-coupon-reader.service.ts`/catalogue. If a capability needs a new cross-repo read tool, return the dependency gap for a Commerce/API-owned task.

## Dependencies

None — the module can be developed in isolation from new ARCH-047 schema; still requires the architect to reconcile the parent architecture before execution.

**Important:** Tasks are not Ready merely because their files exist. Confirm each dependency has `status: complete` (not only Passing tests / Accepted review) before claiming. DB001 is developer-owned and may remain in progress pending explicit completion. Dependencies outside this task must be resolved by their owners; do not implement across repositories.

## Enables

- `ARCH-047-BACKGROUND-006`
- `ARCH-047-BACKGROUND-007`


## Acceptance Criteria

- [ ] Unit scenarios for NONE (zero LLM calls), valid/expired FIXED, one/multiple candidates, deterministic ranking/tie, wrong-shop/currency restrictions and no verified offer.
- [ ] AI suggests valid, ineligible and fabricated offers; only verified offers can be returned; model/provider timeout never promises an offer.
- [ ] Shopify/Woo fixtures including code and automatic discount differences; Woo multiple-selected-coupons anchor must not incorrectly imply chosen coupon.
- [ ] Retry/stale-checkout and sequence-two offer consistency tests; assert no cart/checkout/discount mutation API invoked.
- [ ] Focused tests/build/typecheck and `git diff --check`; record unsupported provider evaluation as an architectural gap, not fabricated eligibility.
- [ ] No source/template authoring, shopper checkout mutation, Meta edit-existing-template call, externally authored Meta template adoption, or bypass of existing WhatsApp final-send safeguards is introduced.
- [ ] Task implementation is modular, separately testable, and stays within `moda-interact-background/`; externally owned gaps are reported, not silently implemented.

## Validation

- [ ] Run the focused new tests and relevant existing regression suites identified above; record exact executable commands and outcomes.
- [ ] Run the repository-declared build/typecheck (for this snapshot: `npm run build`) and focused ESLint where applicable; do not assume every repository has identical scripts.
- [ ] `git diff --check`, inspect changed-file scope and capture task-isolated start-of-attempt and mirrored-branch evidence.
- [ ] When integration depends on a real PostgreSQL/BullMQ service, run the repository's declared integration harness or record the missing environment explicitly; do not claim an unrun test passed.

## Stop Condition

After finishing Work Items, Acceptance Criteria and Validation, fill the Completion Report, change task status to `review`, return both the implementation and parent task-branch evidence to `moda_architect`, and **STOP**. Do not start any enabled/adjacent task or update `docs/decisions/**/_index.md`.

## Implementation Notes

Use strategy injection for provider-specific eligibility rather than branching through one oversized service. Existing read-only policies remain authoritative; do not change `RecoveryPolicyService` semantics in this task unless its existing public contract explicitly permits the needed read-only snapshot.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-004`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.



## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-26T03:02:29Z. Attempt 0 review history is preserved below.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run; implementation validation remains outstanding.

### Deviations

None recorded.

### Assumptions

The DB001 Attempt 7 model names and fields are authoritative design inputs, not proof of an accepted/applied production migration. Reinspect current implementation on claim.

### Unresolved Issues

The parent ARCH-047 architecture and `BACKGROUND-001` still require final reconciliation with the Admin-owned AST/compilation and no-new-Shared-template-package decision before work begins.

### Architectural Concerns

No additional cross-repository issues identified at definition time; return any new gap to the architect.

## Architect Review

### Review Status

Pending — implementation not submitted.

### Review Notes

Not reviewed.

### Reviewed Files

None yet.

### Validation Reviewed

None yet.

### Architecture Conformance

To be assessed against the reconciled ARCH-047 parent architecture and current repository code.

### Follow-up

Architect to reconcile the parent task graph and obsolete Admin/Shared references before promoting these tasks to Ready.

## Execution Ownership Amendment

- Date: 2026-10-26
- Change: The developer explicitly invoked `/moda_developer_create` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_background`, coordinator, repository, task scope, acceptance criteria, validation requirements and current Ready eligibility.
- Claim state: This amendment does not claim an implementation attempt; the canonical launcher records the claim after dependency and worktree preparation.
