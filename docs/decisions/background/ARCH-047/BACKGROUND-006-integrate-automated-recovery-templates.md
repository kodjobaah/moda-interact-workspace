---
id: ARCH-047-BACKGROUND-006
architecture_id: ARCH-047
title: Integrate offer decisions and prepared templates into automated recovery
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-047-BACKGROUND-001
  - ARCH-047-BACKGROUND-004
enables:
  - ARCH-047-BACKGROUND-007
created: 2026-10-24
updated: 2026-10-26
---

# Integrate offer decisions and prepared templates into automated recovery

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

This is a **portable task definition** prepared from the 24 October 2026 workspace snapshot and consolidated DB001 Attempt 7 contract. It is not a repository implementation, task claim or evidence of a created worktree/branch. No new ARCH-047 Shared package is assumed. The parent architecture and `BACKGROUND-001` require reconciliation to the final Admin-owned AST/compilation and DB-backed keyed-segment translation decisions before dependent work is promoted.

## Objective

Wire the offer resolver and reusable template preparer into initial and scheduled follow-up sends while preserving one authoritative final outbound admission path.

## Context

ARCH-047 permits only immutable, Moda Admin-authored template definitions. Admin validates and compiles the AST and persists already-prepared transport/runtime data. Background handles independently testable execution modules and **never re-parses the Admin authoring AST**. The DB001 schema provides translation runs/items/batches, compiled Meta registrations, publication targets and wrapper pointers. Messaging delivers Meta template status observations through the existing BullMQ path; Background persists/assesses them. Existing outbound admission remains authoritative.

## Scope

- Replace the legacy template-selection/category-check calls in `checkout-recovery/recovery-initiation.service.ts`, `checkout-recovery/recovery-outreach-follow-up-processor.service.ts` **and** the WooCommerce automated-initial adapter `woocommerce-recovery/woo-recovery-outreach.adapters.ts` with calls to BG004/BG001. Preserve each caller's checkout eligibility, recovery sequence and provider-fence ownership; do not create separate Shopify and Woo template-selection algorithms.
- Migrate the affected outbound delivery/admission adapter from live Meta-category verification to the existing DB-backed, fail-closed BG006 final-registration fence; remove outdated category verifier injection only after all production callers have migrated.
- Implement **one narrow shared final-send template assignment/registration recheck adapter** at the established final admission point for both automated and later human sequence-two consumers. Do not create a parallel send pipeline.
- Keep all recovery state, scheduling, reachability, billing and provider-delivery orchestration owned by their existing services; new code is orchestration glue and injection ports.

## Out of Scope

- Do not reimplement the offer resolver, selector, AST compiler, Meta registration management, translation, wrapper rendering or human in-window send.
- Do not reopen completed ARCH-045/046 consent/STOP tasks, bypass purchased-credit reservations or implement unrelated retry/scheduling refactors.

## Requirements

**R1 — Eligible action ordering.** Retain current checkout/recovery and consent/STOP/reachability guards. Only after an initial/sequence-two message is eligible and needed, resolve one verified offer using BG004; then request BG001 preparation with `INITIAL` or `FOLLOW_UP`, verified offer outcome, intended shop/WABA/language/recipient and checkout evidence. No LLM call on irrelevant inbound checkout events.

**R2 — Selected template.** Use prepared approved/published Moda-authored assignment and per-language frozen Meta parameter bindings; default to a No Offer template only on a validated `NO_OFFER` decision, never on an unavailable/ineligible sender slot. Do not perform provider template-metadata GET on normal sends. Preserve the initial shop-default and subsequent conversation-language semantics unless explicitly changed in task scope.

**R3 — Final recheck, including provider observation fence.** Reverify the exact shop/variant/registration, local approved/enabled status, current provider revocation/drift state, sender WABA and recipient association as late as existing final permit/transaction permits. **The existing registration MUST be re-read at the authoritative final-send admission boundary, not trusted from BG001 preparation.** Permit provider-dependent template delivery only when `providerStatus === "APPROVED"`, `driftDetectedAt == null`, `lastReconciledAt != null` and the successful reconciliation is no older than **60 minutes**, with no outstanding unresolved potentially disabling Meta observation (`providerStatus: UNKNOWN` or `STATUS_RECONCILIATION_PENDING`). An authenticated PAUSED/DISABLED/REJECTED event committed by BG003 must make subsequent final-send checks fail even if Meta GET has timed out. Deny with a typed `TEMPLATE_PROVIDER_STATUS_UNRESOLVED`/`TEMPLATE_PROVIDER_STATUS_STALE` outcome; preserve consent/STOP, moderation, send limits and credit reservation/compensation. Never activate/deactivate a shop assignment in this adapter. No external Meta/Redis operation inside a SQL transaction; no stale prepared payload can bypass changed publication/STOP/consent state.

**R3a — Prepared ShopBrand and CTA component pass-through.** BG001 owns resolving the ShopBrand text references and any separately typed READY image-header/checkout-button bindings. BG006 must forward **all prepared provider components unchanged** (ordered text/header parameters, validated `imageHeader.link` when supplied, and the one compiled dynamic URL-button suffix/parameter) through the existing WhatsApp send adapter; it must not read `ShopBrand`, rebuild compiled URLs, resize or fetch media, recalculate variable positions or silently drop media/button values. When the preparer returns an unavailable result (including `MEDIA_NOT_READY`, optional brand field missing or invalid checkout URL), do not invoke the provider or reserve/settle outreach charges. Media support cannot be activated until the separately owned R2-normalisation readiness contract and the existing sender's supported parameter shape have been proven.

**R4 — Recovery invariants. Preserve sequence-one idempotency, one permitted sequence-two follow-up, order-completion/checkout-change suppression, last inbound response ordering, consent and authoritative STOP, independent moderation, entitlement and credit reservation/settlement/compensation. Failed preparation/admission yields a controlled no-send result without wrongly consuming credits.

**R5 — Shared adapter ownership.** BG006 owns the narrow final template eligibility adapter/fence changes; BG007 **calls the same adapter** and must not implement a second copy. Existing Meta provider send mechanics remain unchanged except passing prepared body/button/header parameters.

**R6 — Record unresolved discount-evidence capability accurately.** The completed BG004 resolver has read-only provider-evaluation ports, but its default Shopify and Woo implementations currently return `outcome: "unavailable"`. `NONE` is a fully supported No Offer case; `FIXED` and `AI_BEST_APPLICABLE` must not be labelled as successfully advertising a verified discount unless a checkout-specific provider evaluator supplies the existing `CheckoutRuleEvidence` contract. Where the provider capability is absent, retain BG004's typed `NO_OFFER` result, prepare only an eligible No Offer variant, do not call Meta with a coupon promise, and emit a bounded, non-sensitive capability-gap signal. BG006 does **not** implement Shopify/Woo discount evaluation or turn catalogue listing into eligibility evidence. Document this unresolved capability in the Completion Report and return it to the architect for a separately owned read-only capability task; no checkout/cart mutation is permitted.

**R7 — Legacy path retirement is part of implementation, not optional cleanup.** Remove legacy `whatsappTemplateSelectorService` and `metaWhatsAppTemplateCategoryService.verify()` usage from **all automated Shopify and Woo initial/follow-up call sites** after the BG001/BG004 equivalent is wired and exercised. Replace corresponding stale mocks, fixtures and tests that expect `purpose: "checkout-recovery"`, `verifiedCategory` or per-send Meta template-category GET. Do not delete the selector/category modules yet if BG007's human path or other real production consumers still use them: identify remaining imports in the Completion Report for BG007 to retire. No compatibility fallback to legacy unlinked `WhatsAppTemplateVariant` rows is permitted in the migrated production flow.

## Work Items

- [ ] Modify only relevant automated recovery call sites (`checkout-recovery/recovery-initiation.service.ts`, `checkout-recovery/recovery-outreach-follow-up-processor.service.ts`, narrowly required outbound admission/final fence adapters) to delegate to BG004 and BG001 modules.
- [ ] Implement **one narrow shared final-send template assignment/registration recheck adapter** at the established final admission point for both automated and later human sequence-two consumers. Do not create a parallel send pipeline.
- [ ] Keep all recovery state, scheduling, reachability, billing and provider-delivery orchestration owned by their existing services; new code is orchestration glue and injection ports.
- [ ] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [ ] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

- [ ] Wire the WooCommerce automated initial path (`woo-recovery-outreach.adapters.ts`) as well as Shopify initial and scheduled follow-up through the same modules, without duplicating offer or template-selection rules.
- [ ] Replace legacy template selector/category verifier imports and per-send Meta GET branches in migrated production call sites; update the matching tests and record any still-live imports explicitly for BG007.
- [ ] Run both default-unavailable Shopify/Woo eligibility tests and injected independently verified positive-offer tests; report the actual external provider-evidence gap without claiming it implemented.

## Interfaces / Contracts

**Consumes** BG004 `RecoveryOfferDecision`, BG001 `PreparedRecoveryTemplate` with immutable assignment identity, existing recovery/credit/final-send ports. This task owns only integration and the shared late-check adapter. Do not make a new Shared package contract for Background-local interfaces.

**Key paths to inspect:** `recovery-initiation.service.ts`, `recovery-outreach-follow-up-processor.service.ts`, `outbound-whatsapp-admission/outbound-message-delivery.service.ts`, `recovery-conversation/outbound-send-fence.service.ts`. Resolve actual call graph before modifying.

## Dependencies

- `ARCH-047-BACKGROUND-001`
- `ARCH-047-BACKGROUND-004`


**Important:** Tasks are not Ready merely because their files exist. Confirm each dependency has `status: complete` (not only Passing tests / Accepted review) before claiming. DB001 is developer-owned and may remain in progress pending explicit completion. Dependencies outside this task must be resolved by their owners; do not implement across repositories.

## Enables

- `ARCH-047-BACKGROUND-007`


## Acceptance Criteria

- [ ] Initial and automated follow-up forwards a prepared ShopBrand text binding, trusted checkout CTA button parameter and optional READY image-header payload **without** rewriting/dropping a component; unavailable prepared media/URL produces no send or charge. Existing text-only paths remain compatible.

- [ ] Initial NONE/FIXED/AI and sequence-two follow-up select expected six-purpose variants and preserve correct language; mapping of body and dynamic URL/button parameters tested with provider mock.
- [ ] Provider category preflight no longer called; no normal-send Meta metadata GET; missing/revoked/drifted/disabled/ambiguous assignment fails closed.
- [ ] Simulate consent/STOP/recipient/assignment change between preparation and final permit; additionally simulate a previously APPROVED registration receiving PAUSED, BG003 storing UNKNOWN and Meta GET timing out. Final admission refuses all new sends without charge; later verified APPROVED restores only provider eligibility, not an Admin-disabled assignment. Stale `lastReconciledAt` over 60 minutes also denies without send.
- [ ] Tests for order completion, duplicate initial and sequence-two jobs, response before follow-up and max-two outreach limit.
- [ ] Re-run existing recovery-initiation/follow-up/fence/credit compensation tests, PostgreSQL admission race where available, build and `git diff --check`.
- [ ] No source/template authoring, shopper checkout mutation, Meta edit-existing-template call, externally authored Meta template adoption, or bypass of existing WhatsApp final-send safeguards is introduced.
- [ ] Task implementation is modular, separately testable, and stays within `moda-interact-background/`; externally owned gaps are reported, not silently implemented.

- [ ] Source-level regression shows **none** of the Shopify initial, scheduled follow-up or Woo automated initial paths still import/call `whatsappTemplateSelectorService` or `metaWhatsAppTemplateCategoryService`; no branch reaches `purpose: "checkout-recovery"` or an ordinary-send Meta category GET. Existing Woo readiness, billing, consent and send-fence tests still pass.
- [ ] Without a checkout-specific provider eligibility adapter, FIXED and AI modes safely resolve to `NO_OFFER`; no code/automatic-offer wording, discount code, credit charge on failed admission, or falsely successful eligibility is produced. Verified-provider fixture covers CODE and AUTOMATIC selection without basket mutation.
- [ ] Outdated tests/mocks and dead branches owned by this task are removed or rewritten; any live legacy module dependency retained for BG007 is listed by exact file and consumer in the Completion Report.

## Validation

- [ ] Run the focused new tests and relevant existing regression suites identified above; record exact executable commands and outcomes.
- [ ] Run the repository-declared build/typecheck (for this snapshot: `npm run build`) and focused ESLint where applicable; do not assume every repository has identical scripts.
- [ ] `git diff --check`, inspect changed-file scope and capture task-isolated start-of-attempt and mirrored-branch evidence.
- [ ] When integration depends on a real PostgreSQL/BullMQ service, run the repository's declared integration harness or record the missing environment explicitly; do not claim an unrun test passed.

## Stop Condition

After finishing Work Items, Acceptance Criteria and Validation, fill the Completion Report, change task status to `review`, return both the implementation and parent task-branch evidence to `moda_architect`, and **STOP**. Do not start any enabled/adjacent task or update `docs/decisions/**/_index.md`.

## Implementation Notes

Keep `RecoveryInitiationService` and follow-up processor thin: call the owned modules and preserve their result IDs. Test narrow adapter through injection. Do not delete legacy selector until all callers have migrated; any legacy compatibility cleanup must be bounded and verified.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-006`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.



## Completion Report

### Status

Not Started — task definition only; no implementation was executed or validated in this artifact.

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
