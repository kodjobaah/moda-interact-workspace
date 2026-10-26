---
id: ARCH-047-BACKGROUND-006
architecture_id: ARCH-047
title: Integrate offer decisions and prepared templates into automated recovery
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 35
executor: developer
claimed_at: null
attempt: 2
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

- [x] Modify only relevant automated recovery call sites (`checkout-recovery/recovery-initiation.service.ts`, `checkout-recovery/recovery-outreach-follow-up-processor.service.ts`, narrowly required outbound admission/final fence adapters) to delegate to BG004 and BG001 modules.
- [x] Implement **one narrow shared final-send template assignment/registration recheck adapter** at the established final admission point for both automated and later human sequence-two consumers. Do not create a parallel send pipeline.
- [x] Keep all recovery state, scheduling, reachability, billing and provider-delivery orchestration owned by their existing services; new code is orchestration glue and injection ports.
- [x] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [x] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

- [x] Wire the WooCommerce automated initial path (`woo-recovery-outreach.adapters.ts`) as well as Shopify initial and scheduled follow-up through the same modules, without duplicating offer or template-selection rules.
- [x] Replace legacy template selector/category verifier imports and per-send Meta GET branches in migrated production call sites; update the matching tests and record any still-live imports explicitly for BG007.
- [x] Run both default-unavailable Shopify/Woo eligibility tests and injected independently verified positive-offer tests; report the actual external provider-evidence gap without claiming it implemented.

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

- [x] Initial and automated follow-up forwards a prepared ShopBrand text binding, trusted checkout CTA button parameter and optional READY image-header payload **without** rewriting/dropping a component; unavailable prepared media/URL produces no send or charge. Existing text-only paths remain compatible.

- [x] Initial NONE/FIXED/AI and sequence-two follow-up select expected six-purpose variants and preserve correct language; mapping of body and dynamic URL/button parameters tested with provider mock.
- [x] Provider category preflight no longer called; no normal-send Meta metadata GET; missing/revoked/drifted/disabled/ambiguous assignment fails closed.
- [x] Simulate consent/STOP/recipient/assignment change between preparation and final permit; additionally simulate a previously APPROVED registration receiving PAUSED, BG003 storing UNKNOWN and Meta GET failing. The new disposable-PostgreSQL permit tests prove `TEMPLATE_PROVIDER_STATUS_UNRESOLVED`, no provider dispatch or committed charge, both lock acquisition orders, stale reconciliation rejection and stale APPROVED replay rejection. Existing unit coverage retains the independent consent/STOP/assignment and later-verification requirements.
- [x] Tests for order completion, duplicate initial and sequence-two jobs, response before follow-up and max-two outreach limit.
- [x] Re-run existing recovery-initiation/follow-up/fence/credit compensation tests, PostgreSQL admission race where available, build and `git diff --check`.
- [x] No source/template authoring, shopper checkout mutation, Meta edit-existing-template call, externally authored Meta template adoption, or bypass of existing WhatsApp final-send safeguards is introduced.
- [x] Task implementation is modular, separately testable, and stays within `moda-interact-background/`; externally owned gaps are reported, not silently implemented.

- [x] Source-level regression shows **none** of the Shopify initial, scheduled follow-up or Woo automated initial paths still import/call `whatsappTemplateSelectorService` or `metaWhatsAppTemplateCategoryService`; no branch reaches `purpose: "checkout-recovery"` or an ordinary-send Meta category GET. Existing Woo readiness, billing, consent and send-fence tests still pass.
- [x] Without a checkout-specific provider eligibility adapter, FIXED and AI modes safely resolve to `NO_OFFER`; no code/automatic-offer wording, discount code, credit charge on failed admission, or falsely successful eligibility is produced. Verified-provider fixture covers CODE and AUTOMATIC selection without basket mutation.
- [x] Outdated tests/mocks and dead branches owned by this task are removed or rewritten; any live legacy module dependency retained for BG007 is listed by exact file and consumer in the Completion Report.

## Validation

- [x] Run the focused new tests and relevant existing regression suites identified above; record exact executable commands and outcomes.
- [x] Run the repository-declared build/typecheck (for this snapshot: `npm run build`) and focused ESLint where applicable; do not assume every repository has identical scripts.
- [ ] `git diff --check`, inspect changed-file scope and capture task-isolated start-of-attempt and mirrored-branch evidence. (Git checks and worktree paths verified; launcher sync/submodule evidence is not in the supplied log.)
- [x] When integration depends on a real PostgreSQL/BullMQ service, run the repository's declared integration harness or record the missing environment explicitly; do not claim an unrun test passed.

## Stop Condition

After finishing Work Items, Acceptance Criteria and Validation, fill the Completion Report, change task status to `review`, return both the implementation and parent task-branch evidence to `moda_architect`, and **STOP**. Do not start any enabled/adjacent task or update `docs/decisions/**/_index.md`.

## Implementation Notes

Keep `RecoveryInitiationService` and follow-up processor thin: call the owned modules and preserve their result IDs. Test narrow adapter through injection. Do not delete legacy selector until all callers have migrated; any legacy compatibility cleanup must be bounded and verified.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-006`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.



## Completion Report

### Status

Ready for Review — **Attempt 2 correction submitted**. The previously blocking, real-PostgreSQL final-send permit/revocation tests now pass (four tests in two files), and the test-only correction is published at implementation commit `7a2bac9` after the original `6066b6f`. No architect acceptance or developer completion is claimed. **Evidence caveat:** the supplied Attempt 2 materials do not include a launcher preparation/claim packet or `claimed_at` timestamp; the latter remains `null` rather than being invented, and the dedicated worktree/branch evidence must be verified by the reviewer.

### Files Changed

**Implementation (`moda-interact-background/`): 25 files, 980 insertions and 242 deletions.**

- `src/integration/whatsapp/types.ts`
- `src/services/checkout-recovery/recovery-initiation.service.ts`
- `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts`
- `src/services/conversation-moderation/automated-template-input.ts`
- `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`
- `src/services/outbound-whatsapp-admission/outbound-whatsapp-admission.types.ts`
- `src/services/recovery-conversation/outbound-send-fence.service.ts`
- `src/services/recovery-template-integration/automated-recovery-template.service.ts` (new)
- `src/services/recovery-template-integration/final-template-registration.service.ts` (new)
- `src/services/recovery-template-integration/prepared-template-send.ts` (new)
- `src/services/whatsapp.service.ts`
- `src/services/woocommerce-recovery/woo-guarded-initial-sender.service.ts`
- `src/services/woocommerce-recovery/woo-initial-send-fence.service.ts`
- `src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts`
- `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`
- `tests/integration/conversation-moderation.integration.test.ts`
- `tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`
- `tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts`
- `tests/unit/services/outbound-whatsapp-admission.service.test.ts`
- `tests/unit/services/recovery-template-integration/automated-recovery-template.service.test.ts` (new)
- `tests/unit/services/recovery-template-integration/final-template-registration.service.test.ts` (new)
- `tests/unit/services/recovery-template-integration/prepared-template-send.test.ts` (new)
- `tests/unit/services/woocommerce-recovery/woo-guarded-initial-sender.service.test.ts`
- `tests/unit/services/woocommerce-recovery/woo-initial-delivery.service.test.ts`
- `tests/unit/services/woocommerce-recovery/woo-initial-send-fence.service.test.ts`

**Attempt 2 correction (`7a2bac9`, test-only): three new integration files, 426 insertions; no production source changes.**

- `tests/integration/arch047-final-template-status-admission.integration.test.ts`
- `tests/integration/arch047-final-template-permit-races.integration.test.ts`
- `tests/integration/fixtures/arch047-final-template-permit.fixture.ts`

No architecture index, migration, Shared package, or other repository-owned source file was changed by the implementation commit. The Attempt 2 correction also changes no architecture index, migration, Shared package, or other repository-owned implementation file.

### Work Completed

- Wired Shopify initial outreach, Shopify scheduled sequence-two follow-up, and Woo automated initial outreach through the existing BG004 offer resolver and BG001 frozen-template preparer, using a single `AutomatedRecoveryTemplateService` coordinator.
- Forwarded the prepared template's ordered text/header/image/dynamic-URL-button parameters into the existing WhatsApp sender. Kept existing moderation, recovery billing, credit reservation/compensation, consent/STOP, reachability and worker delivery boundaries in their owning services.
- Introduced `checkFinalTemplateRegistration` as a shared **database-only** registration identity/status/age check, invoked inside the existing Shopify recovery and Woo final SQL permit transactions. Checks include tenant/variant/registration/definition/locale identity, local enablement/publication, sender WABA, reconciled Meta APPROVED state, no drift or unresolved disabling observation, and a 60-minute maximum verification age. No Meta HTTP or Redis I/O was added inside these SQL transactions.
- Removed `whatsappTemplateSelectorService` and `metaWhatsAppTemplateCategoryService` from the migrated automated send call sites. No automated `purpose: "checkout-recovery"` selector branch remains in the inspected snapshot.
- Returned typed no-send outcomes for unprepared/unavailable templates and unsafe historical follow-ups. Default unavailable per-checkout discount verification continues to resolve to `NO_OFFER`; independently verified positive-code and automatic-discount behaviour is tested through injected fixtures, not misrepresented as a live provider implementation.
- Added focused unit, send-path regression, and moderation integration coverage. New caught operational exceptions are logged with bounded fields using `@modainteract/moda-interact-shared/logging` and rethrown rather than silently acknowledged.
- **Attempt 2:** Added disposable PostgreSQL fixture/tests that run the actual BG003 observation transaction and BG006 Woo final SQL permit. Confirmed a durable PAUSED/UNKNOWN pending observation survives Meta GET failure and denies delivery; verified real `FOR SHARE`/writer lock ordering in both directions, a subsequent distinct permit denial, stale APPROVED CAS reconciliation rejection, and the greater-than-60-minute stale-verification fence. The denial test also invokes the existing `OutboundMessageDeliveryService` to assert no Meta template dispatch and no committed recovery credit; expected operational exceptions remain logged by their existing shared-logger paths, with no new exception swallowing.

### Validation Results

**Supplied development-terminal evidence: `typescript(20261026-074508)`, 2026-10-26 07:42–07:44 local time.**

- `npm test -- tests/unit/services/recovery-template-integration/ tests/unit/services/checkout-recovery/ tests/unit/services/woocommerce-recovery/woo-guarded-initial-sender.service.test.ts tests/unit/services/woocommerce-recovery/woo-initial-delivery.service.test.ts tests/unit/services/woocommerce-recovery/woo-initial-send-fence.service.test.ts tests/unit/services/outbound-whatsapp-admission.service.test.ts` — PASS: **22 files, 259 tests**.
- `npm run test:arch040-recovery-conversation` — PASS: **9 files, 71 tests**.
- `npm run test:integration -- tests/integration/conversation-moderation.integration.test.ts` — PASS: **1 file, 10 tests**, exercising the repository's integration runner. This is **not** a dedicated real-PostgreSQL integration test of the newly added final-registration SQL projection.
- `npm run build` — PASS: Prisma Client v6.19.3 generated; TypeScript compiler exited without reported errors.
- `npx eslint src/services/recovery-template-integration/ src/services/checkout-recovery/recovery-initiation.service.ts src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts src/services/outbound-whatsapp-admission/ src/services/woocommerce-recovery/woo-guarded-initial-sender.service.ts src/services/woocommerce-recovery/woo-initial-send-fence.service.ts src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts src/services/woocommerce-recovery/woo-recovery-outreach.service.ts tests/unit/services/recovery-template-integration/` — exited without reported diagnostics.
- `git diff --check` — no whitespace errors reported; initial patch application showed no reported errors.
- `git commit -m "feat(ARCH-047-BACKGROUND-006): integrate approved recovery templates"` — created implementation commit `6066b6f` (25 files changed).
- `git push -u origin task/ARCH-047-BACKGROUND-006` — PASS; remote task branch created, upstream changed to `origin/task/ARCH-047-BACKGROUND-006`.

**Attempt 2 development-terminal evidence: `typescript(20261026-090607)`, 2026-10-26 09:03–09:05 local time.**

- `npm run test:integration -- tests/integration/arch047-final-template-status-admission.integration.test.ts tests/integration/arch047-final-template-permit-races.integration.test.ts` — **PASS: 2 PostgreSQL test files, 4/4 tests**. Demonstrates BG003 PAUSED observation with `UNKNOWN`/pending durable fence after mocked Meta GET 503, real final-permit denial without provider dispatch or committed credit, both row-lock/transaction orderings, stale prior APPROVED reconciliation rejection, and verification older than 60 minutes.
- `npm run build` — **PASS**: Prisma Client v6.19.3 generation and TypeScript compilation.
- `npx eslint tests/integration/arch047-final-template-status-admission.integration.test.ts tests/integration/arch047-final-template-permit-races.integration.test.ts tests/integration/fixtures/arch047-final-template-permit.fixture.ts` — exited with **no reported diagnostics**.
- `git apply --check --whitespace=error-all` and `git apply --whitespace=error-all` — no patch-application error reported in the terminal session; `git diff --check` produced no reported diagnostics.
- `git commit -m "feat(background)"` — created test-only implementation commit **`7a2bac9`** (3 files, 426 insertions); `git push` — **PASS** (`6066b6f..7a2bac9` to `origin/task/ARCH-047-BACKGROUND-006`). This generic commit message is retained as evidence, not reworded to an unexecuted task-specific command.
- The prior Attempt 1 regression, unit, moderation and review rechecks remain historical evidence; these broader suites were **not** rerun in the supplied Attempt 2 terminal session.

**Dedicated worktree evidence from the terminal log/archive:**

- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-BACKGROUND-006`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-BACKGROUND-006`.
- Implementation branch: `task/ARCH-047-BACKGROUND-006`; parent task branch and parent content are shown by the supplied worktree snapshot and claim metadata, but a parent `git branch --show-current` log was not provided.
- The snapshot was generated by overlaying the implementation worktree into the dedicated parent worktree, as stated in the terminal output.
- **Not supplied:** the original launcher-resolved preparation packet, Git-common-dir root proof, start-of-attempt fetch/fast-forward/synchronization records for *both* worktrees, or recursive submodule materialisation/status results. The architect must request/verify these; the existence of matching worktree paths does not replace this evidence.
- **Attempt 2 evidence:** the new log shows implementation branch `task/ARCH-047-BACKGROUND-006`, a successful remote push at `7a2bac9`, and the workspace compressor naming the same dedicated parent and implementation worktrees. It does **not** show an Attempt 2 `/moda_developer_create` claim, a `claimed_at` value, the parent branch synchronization, or the recursive submodule preparation packet. The task metadata records the second implementation iteration, but must not be read as proof that the canonical preparation protocol was executed.

### Deviations

- No unrelated source, schema, infrastructure, BG007 human-sender, architecture-index or cross-repository implementation was attempted.
- **Attempt 1 gap closed in Attempt 2:** the added disposable-PostgreSQL tests now exercise the actual Meta status observation + final SQL permit transaction and deterministic registration-lock ordering. No production code changes were required. The suite focuses on the PAUSED/UNKNOWN registration race; the existing unit regressions cover consent/STOP and other final-admission denials.
- **Workflow evidence gap:** no fresh Attempt 2 launcher/claim or beginning-of-attempt synchronization packet is included. Task isolation is supported by the named dedicated paths, not proved to the full launcher policy standard; the combined isolation/launcher Validation checkbox stays unchecked for the reviewer.
- The historic portable-definition note above describes the definition's origin; this report records the actual materialised development attempt and implementation commit.

### Assumptions

- BG001/BG004 accepted runtime interfaces and the currently materialised Prisma schema are the canonical inputs. No new Shared template contract is added.
- Approved Meta registration and frozen compiled bindings are independently maintained by their existing Admin/BG003 owners; this task reads their durable state and does not author or mutate templates.
- Sender media readiness is proven by the BG001 preparer and the supported existing provider parameter shape; a missing/invalid READY input remains a no-send outcome.

### Unresolved Issues

- **Discount eligibility:** default Shopify and Woo per-checkout provider-rule evaluators remain unavailable; FIXED and AI requests safely use `NO_OFFER` when no independently verified checkout evidence is supplied. A separately owned evaluator is needed before live positive offers can be claimed. BG006 has not implemented that provider capability.
- **Human BG007 migration:** `src/services/recovery-conversation/human-command-dispatcher.service.ts` still imports `metaWhatsAppTemplateCategoryService` (from `src/services/whatsapp-template-category.service.ts`). This is the remaining live consumer and must be handled by ARCH-047-BACKGROUND-007; selector and category modules were not prematurely deleted.
- **Review proof:** Attempt 2 now includes passing PostgreSQL final-template admission/race results. Neither the original nor fresh Attempt 2 launcher preparation/claim packet, start synchronization/recursive-submodule proof or a trustworthy `claimed_at` value appears in the supplied evidence. The reviewer must verify or request correction for this process requirement before accepting; no historical synchronization is inferred from currently correct worktree paths.

### Architectural Concerns

- The new final-send DB fence is a narrow SQL-only reuse point for BG007, not an independent provider delivery pipeline. Attempt 2 PostgreSQL tests demonstrate the BG003 PAUSED/UNKNOWN ordering and stale reconciliation denial; the architect still owns formal assessment of provider observation/source semantics and any broader Admin revocation integration.
- Deferred provider eligibility is a cross-repository capability gap. Do not replace it with optimistic catalogue-based discount matching or an unverified checkout mutation.
- `ARCH-047-BACKGROUND-007` remains pending until BG006 is architect accepted **and** explicitly completed (developer completion mode); a review submission does not unblock dependants.

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

- Date: 2026-10-26.
- Change: The developer explicitly invoked `/moda_developer_create ARCH-047-BACKGROUND-006` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_background`, coordinator, repository, task scope, acceptance criteria, validation requirements, dependency gate, Ready eligibility, and attempt 0. This amendment does not itself claim an implementation attempt.

## Developer Self-Review - Changes Requested

*Historical Attempt 1 review, retained unchanged below. The new Attempt 2 review submission and evidence are documented in the Completion Report above; this section is not the decision on Attempt 2.*

### Review Decision

Attempt 1 is not accepted for developer completion. The production adapter locks and re-reads the exact template registration inside the existing final permit transaction, and focused unit tests cover approved, unavailable, UNKNOWN/PAUSED, pending observation, drift, null/old/future reconciliation timestamps, and SQL error propagation. BG003's separate PostgreSQL integration covers the durable UNKNOWN/pending fence after a PAUSED observation and failed Meta GET. However, the evidence does not exercise those components together against PostgreSQL at the authoritative final-send permit boundary, so the critical ordering/locking behavior remains unverified at the database level.

### Validation Reviewed

- **PASS** — `npx vitest run tests/unit/services/recovery-template-integration/final-template-registration.service.test.ts tests/unit/services/recovery-template-integration/automated-recovery-template.service.test.ts tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts tests/unit/services/outbound-whatsapp-admission.service.test.ts`: 97 tests across 5 files.
- **PASS** — `npm run test:integration -- tests/integration/arch047-recovery-template-preparation.integration.test.ts`: 1 PostgreSQL integration test passed. This verifies prepared-template lookup/provenance, not the final registration permit race.
- The submitted report's build, focused ESLint, broader regression and moderation integration results are retained as supplied evidence; they were not rerun for this review.
- Current Git inspection: implementation branch `task/ARCH-047-BACKGROUND-006` is clean and matches `origin/task/ARCH-047-BACKGROUND-006` at `6066b6f`; `origin/main` is an ancestor. Parent branch is clean and published at `38d34ac`. Recursive database submodule is initialized at `3f1f50b91c9e93ff9647a3d1d7f6fd46b9b888b9`. The original launcher packet is not present in the submitted report, so current state is not misrepresented as historical launcher output.

### Required Correction

- Add and run a disposable-PostgreSQL integration test that seeds an approved/enabled assigned registration and exercises the actual BG006 final permit transaction. Coordinate a BG003 status-observation transaction for PAUSED that durably sets `providerStatus = UNKNOWN` and leaves a `RECONCILIATION_PENDING` event when mocked Meta GET fails. Prove the final permit denies with `TEMPLATE_PROVIDER_STATUS_UNRESOLVED` and makes no provider dispatch or charge; also cover the concurrency ordering so either a permit that acquired the authoritative lock first completes according to the defined ordering, or a committed revocation fences the next permit. Include stale greater-than-60-minute reconciliation denial in a database-backed permit fixture. Do not move Meta/network I/O into SQL transactions or alter BG003 ownership.

### State Transition

Returned to `ready`, with `executor: null`, `claimed_at: null`, and Attempt 1 unchanged. The next canonical `/moda_developer_create ARCH-047-BACKGROUND-006` claim will create Attempt 2 and provide fresh launcher synchronization/submodule evidence. No implementation source was modified during this review.
