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
status: review
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

This task was originally defined as a portable handoff from the 24 October 2026 workspace snapshot and consolidated DB001 Attempt 7 contract. Attempt 1 implementation and validation evidence is now recorded in the Completion Report. No new ARCH-047 Shared package is assumed. The parent architecture and `BACKGROUND-001` still require architect-owned reconciliation to the final Admin-owned AST/compilation and DB-backed keyed-segment translation decisions before dependent work is promoted.

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

- [x] Add `src/services/recovery-offers/` with a small `RecoveryOfferResolver` facade, policy strategies for NONE/FIXED/AI_BEST_APPLICABLE, read-only discount/checkout provider adapters and deterministic eligibility verification.
- [x] Reuse `RecoveryPolicyService`, existing Shopify discount/eligibility tools, Woo coupon catalogue/normalisation, and Commerce's approved read-only discount capabilities where actually available. Keep customer-specific offer evaluation on the **actionable recovery path**, not the raw webhook hot path.
- [x] Return an immutable, typed offer-decision value for `BACKGROUND-001`/integrations; preserve existing policy snapshot meanings unless deliberately changed by a separate owning task.
- [x] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [x] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

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

- [x] Unit scenarios for NONE (zero LLM calls), valid/expired FIXED, one/multiple candidates, deterministic ranking/tie, wrong-shop/currency restrictions and no verified offer.
- [x] AI suggests valid, ineligible and fabricated offers; only verified offers can be returned; model/provider timeout never promises an offer.
- [x] Shopify/Woo fixtures including code and automatic discount differences; Woo multiple-selected-coupons anchor must not incorrectly imply chosen coupon.
- [x] Retry/stale-checkout and sequence-two offer consistency tests; assert no cart/checkout/discount mutation API invoked.
- [x] Focused tests/build/typecheck and `git diff --check`; record unsupported provider evaluation as an architectural gap, not fabricated eligibility.
- [x] No source/template authoring, shopper checkout mutation, Meta edit-existing-template call, externally authored Meta template adoption, or bypass of existing WhatsApp final-send safeguards is introduced.
- [x] Task implementation is modular, separately testable, and stays within `moda-interact-background/`; externally owned gaps are reported, not silently implemented.

## Validation

- [x] Run the focused new tests and relevant existing regression suites identified above; record exact executable commands and outcomes.
- [x] Run the repository-declared build/typecheck (for this snapshot: `npm run build`) and focused ESLint where applicable; do not assume every repository has identical scripts.
- [x] `git diff --check`, inspect changed-file scope and capture task-isolated start-of-attempt and mirrored-branch evidence.
- [x] When integration depends on a real PostgreSQL/BullMQ service, run the repository's declared integration harness or record the missing environment explicitly; do not claim an unrun test passed.

## Stop Condition

After finishing Work Items, Acceptance Criteria and Validation, fill the Completion Report, change task status to `review`, return both the implementation and parent task-branch evidence to `moda_architect`, and **STOP**. Do not start any enabled/adjacent task or update `docs/decisions/**/_index.md`.

## Implementation Notes

Use strategy injection for provider-specific eligibility rather than branching through one oversized service. Existing read-only policies remain authoritative; do not change `RecoveryPolicyService` semantics in this task unless its existing public contract explicitly permits the needed read-only snapshot.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-004`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.



## Completion Report

### Status

Ready for Review — Attempt 1 (developer-executed). Claimed at `2026-10-26T03:02:29Z`; implementation commit `68063bd` has been pushed to `origin/task/ARCH-047-BACKGROUND-004` in `moda-interact-background`. This is a submission for review, **not** architect acceptance or developer completion.

### Files Changed

Implementation repository (`moda-interact-background/`), 11 new files:

- `src/services/recovery-offers/recovery-offer-resolver.service.ts`
- `src/services/recovery-offers/recovery-offer-evidence.ts`
- `src/services/recovery-offers/recovery-offer-providers.ts`
- `src/services/recovery-offers/recovery-offer-repository.ts`
- `src/services/recovery-offers/recovery-offer-timeout.ts`
- `src/services/recovery-offers/recovery-offer.types.ts`
- `tests/unit/services/recovery-offers/fixtures.ts`
- `tests/unit/services/recovery-offers/recovery-offer-ai.test.ts`
- `tests/unit/services/recovery-offers/recovery-offer-repository.test.ts`
- `tests/unit/services/recovery-offers/recovery-offer-resolver.test.ts`
- `tests/integration/recovery-offer-postgres.integration.test.ts`

Parent-workspace change submitted separately: this canonical task file only. No `docs/decisions/**/_index.md` or parent architecture document is modified in this handoff.

### Work Completed

- Implemented the Background-local read-only `RecoveryOfferResolver` with `NONE`, `FIXED` and `AI_BEST_APPLICABLE` policy strategies. `NONE` performs no provider or AI eligibility calls.
- Added tenant-scoped PostgreSQL shop/recovery/discount catalogue reads, fixed merchant-authorised discount selection, Shopify automatic/code and Woo code-only candidate handling, and deterministic ranking by independently verified savings with stable tie-breaking.
- Added immutable typed offer decisions and evidence validation, including checkout fingerprint, provider discount identity, currency, current redeem code/description, expiry and previously promised offer consistency for sequence two.
- Added injectable read-only eligibility and AI recommendation ports. Only provider-verified candidates can be selected; the AI cannot invent an offer or mutate checkout state. Provider and AI calls have bounded timeouts; candidate count and AI output are bounded.
- Implemented fail-closed `NO_OFFER` results for expected unavailability. Unexpected exceptions are logged through `@modainteract/moda-interact-shared/logging` with bounded, non-sensitive context and rethrown; no silent exception suppression.
- Added focused unit and disposable PostgreSQL integration tests. No outbound sends, billing changes, checkout writes, Meta template modification or additional database migrations were introduced.

### Validation Results

Observed in the uploaded `typescript(20261026-035151)` terminal log on 2026-10-26:

| Command | Observed outcome |
| --- | --- |
| `npm ci` | Completed (603 packages added); reported 20 dependency audit advisories (8 moderate, 12 high). No dependency remediation undertaken as part of this task. |
| `npm run prisma:generate` | Passed; Prisma Client v6.19.3 generated. |
| `npm test -- tests/unit/services/recovery-offers/` | Passed: 3 test files, **21/21** tests. |
| `npm run test:integration -- tests/integration/recovery-offer-postgres.integration.test.ts` | Passed: 1 file, **1/1** PostgreSQL integration test. |
| `npm run build` | Passed: Prisma generation followed by `tsc`; shell returned to prompt with no errors. |
| `npx eslint src/services/recovery-offers/ tests/unit/services/recovery-offers/ tests/integration/recovery-offer-postgres.integration.test.ts` | Invoked in the logged command sequence; no lint errors reported. |
| `git diff --check` and `git diff --cached --check` | Invoked; no whitespace errors reported. |
| `git commit` / `git push -u origin task/ARCH-047-BACKGROUND-004` | Passed: commit `68063bd`, 11 files and 1,112 insertions; remote task branch created and upstream configured. |

The uploaded log does **not** show full repository-wide regression tests or a live provider-eligibility end-to-end test; those are not claimed to have passed. The compiled module was inspected in the uploaded snapshot, but this submission is not an architect acceptance review.

### Physical Isolation and Synchronisation Evidence

The uploaded terminal log and the combined worktree archive corroborate the following **paths**, but they do not contain the original launcher preparation packet:

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-BACKGROUND-004` (shown by the developer's worktree compression command).
- Implementation task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-BACKGROUND-004` (shown by Vitest's execution path and the worktree compression output).
- Implementation branch: `task/ARCH-047-BACKGROUND-004` (verified by terminal output after commit/push).
- Expected parent branch: `task/ARCH-047-BACKGROUND-004` (must be checked in the developer's parent worktree before applying this review patch).
- Canonical primary workspace root and launcher-resolved identity: **not independently established** by the uploaded evidence.
- Start-of-attempt synchronization (both task branches, `origin/main` incorporation), recursive implementation-submodule preparation, and absence of shared/other-task worktree execution: **not independently verifiable** without the launcher packet. Architect/developer reviewer should request that evidence before acceptance.

### Deviations

No out-of-scope source modifications were identified in the 11-file task commit. Provider adapters intentionally default to an unavailable result when no trustworthy live per-checkout eligibility evaluator is supplied; this is the explicit fail-closed behaviour required by R3, rather than an assertion of provider eligibility.

### Assumptions

- The existing merchant recovery policy snapshot remains authoritative; no new published Shared offer contract or schema migration is required.
- Eligible-offer evidence must be confirmed by a trusted read-only checkout-specific evaluator, not inferred from a discount catalogue row or Woo anchor ID.
- The reported test environment's disposable PostgreSQL setup is representative for the focused repository integration scenario; production provider evaluation was not exercised.

### Unresolved Issues

- **Provider capability gap:** the snapshot lacks an approved Background-accessible live per-checkout Shopify/WooCommerce discount eligibility evaluator proving all relevant provider/customer/checkout rules. Injectable adapter ports exist, but positive offers must remain unavailable until the appropriate Commerce/API/provider owner supplies and validates that capability. The architect should decide the owning follow-up task and integration dependency.
- **Review evidence gap:** the original task launcher synchronization/recursive-submodule preparation packet is not included; verify separately before accepting the task under `docs/agent-worktree-isolation-policy.md`.
- `npm ci` surfaced 20 audit advisories. No audit remediation was attempted under this bounded task; separate triage may be needed.

### Architectural Concerns

The resolver is deliberately read-only, uses the shared structured logger, and fails closed without checkout eligibility proof. The remaining live provider evaluation is cross-repository integration work; do not invent eligibility from catalogue rows or silently implement Commerce/API-owned capabilities inside Background. Downstream integration must also preserve final consent/STOP admission, messaging and billing boundaries. `ARCH-047-BACKGROUND-006` and `ARCH-047-BACKGROUND-007` remain subject to architect-controlled task dependencies and must not be started merely because this implementation has been submitted for review.

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
