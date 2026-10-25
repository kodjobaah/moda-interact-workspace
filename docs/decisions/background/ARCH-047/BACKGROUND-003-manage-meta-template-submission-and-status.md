---
id: ARCH-047-BACKGROUND-003
architecture_id: ARCH-047
title: Implement Meta template submission and reconciliation module
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: blocked
priority: 25
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-047-DATABASE-001
enables: []
created: 2026-10-24
updated: 2026-10-25
---

# Implement Meta template submission and reconciliation module

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

This task was originally defined from the 24 October 2026 workspace snapshot and consolidated DB001 Attempt 7 contract. It was materialised and claimed for developer execution in canonical task worktrees after verifying DB001 completion and synchronising with the workspace mainline. Attempt 1 implemented the module and is now blocked at the agreed Messaging queue-contract boundary; see the Completion Report. No new ARCH-047 Shared package is assumed. Preserve the cross-repository stop condition until the architect decides whether to narrow this task or separately define queue integration.

## Objective

Submit Admin-compiled Meta template payloads, consume queued authenticated Meta status observations and reconcile provider identities/drift without adopting external templates.

## Context

ARCH-047 permits only immutable, Moda Admin-authored template definitions. Admin validates and compiles the AST and persists already-prepared transport/runtime data. Background handles independently testable execution modules and **never re-parses the Admin authoring AST**. The DB001 schema provides translation runs/items/batches, compiled Meta registrations, publication targets and wrapper pointers. Messaging delivers Meta template status observations through the existing BullMQ path; Background persists/assesses them. Existing outbound admission remains authoritative.

## Scope

- Implement `src/services/meta-template-management/` with focused submission orchestrator, server-only Meta Graph API adapter, reconciliation reader, webhook-status consumer, Prisma repository and module-local ports. Wire `whatsapp-events` worker dispatch through a thin job-name handler when the Messaging producer contract is available.
- Consume frozen `WhatsAppTemplateMetaRegistration` rows and append `WhatsAppTemplateMetaEvent` receipts. Background maintains current `providerStatus`, provider ID and drift observations, **not** authoring ASTs, translation content, shop assignments or publication permissions.
- Reuse existing sender/WABA credential resolution, Meta API error/retry conventions, BullMQ worker orchestration and structured logging.

## Out of Scope

- No `POST /{TEMPLATE_ID}` editing, template import/adoption, Admin AST parsing or compiling, customer messaging, merchant publication or Meta webhook signature verification.
- No PostgreSQL connection added to Messaging; no changes to DB001 schema; no generic new Shared AST/event package solely for this module. A previously unsupported new cross-repository queue format must be referred to the architect rather than duplicated independently.

## Requirements

**R1 — Create-only provider operation.** The registration already contains an Admin-compiled `componentsSnapshot`, `parameterBindingsSnapshot`, unique new provider template name, language, WABA and `submittedContentHash`. Check operator-confirmed submission state and snapshot/digest association transactionally, but **do not compile or author** Meta components. Use Meta template **create** API only and record bounded request/response evidence; never call Meta edit-existing-template API. Protect credential material.

**R2 — Uncertain outcomes and retries.** Mark intent before external I/O; after timeouts/unknown responses reconcile by configured WABA + template name + language/provider ID before retry. When Meta has accepted the request, persist that identity without a duplicate POST. Deduplicate attempts/events through stable `eventIdentity` and application CAS. Never perform Meta network I/O inside a SQL transaction.

**R3 — Queue boundary.** Messaging authenticates webhook ingress and publishes a bounded Meta `message_template_status_update` observation onto the **existing** `whatsapp-events` BullMQ queue. The Background worker distinguishes its job name from `message-received`, `message-status` and `process-conversation-turn`; no attempt to feed status events through `NormalizedWhatsAppInboundMessageSchema`. Reuse the provider-defined fields and established queue envelope where possible. The detailed wire shape must be agreed with `ARCH-047-MESSAGING-001` and documented once; if existing contracts cannot represent it safely, report that limited cross-repository dependency to the architect **before implementing competing local schemas**.

**R4 — Reconciliation and drift.** Match only registrations that originate from Moda definitions. Persist provider event history with optional nullable registrationId for unknown external notifications; **never create a definition, locale, registration or assignment from those notifications**. Handle duplicates, out-of-order/stale statuses and missed webhooks through current Meta reads for the known identity. Store `lastObservedContentHash`, `lastObservedCategory`, `lastReconciledAt`, `driftDetectedAt` using the canonical frozen submission comparison; a status webhook is not proof that content still matches.

**R5 — Runtime safety.** Provider `APPROVED`, `PAUSED`, `DISABLED`, `REJECTED` and drift observations update provider state only; neither activate a shop variant nor clear STOP/consent suppression. A later APPROVED event cannot silently enable an assignment previously disabled by Admin. Provide explicit failure/unknown status outputs for consuming Background selector. Reconciliation may use Meta GET, ordinary WhatsApp sends may **not**.

**R5a — Admin-authored image-header sample.** If the frozen `componentsSnapshot` describes a true Meta `IMAGE` header (not a body text token containing `shopBrand.logoUrl`), verify it has the required Meta-compatible **submission sample/media handle** and supported component structure supplied through the authorised Admin/media preparation path. This module may use its server-only Meta adapter for the required provider sample-media submission operation, but must not fetch original ShopBrand URLs, resize images, upload to R2, invent sample handles, change the template category, or silently mutate an immutable compiled snapshot. Return a typed submission-blocked result when a valid sample/handle is unavailable. The merchant's READY runtime R2 image is a separate value resolved at send time by BG001, not the one sample permanently sent to every shop.

**R6 — Reliability.** Bounded retry/backoff, error taxonomy and observability, no secrets or full raw payloads in logs. Reuse existing queues/workers rather than deploying an unrelated ingress service.

## Work Items

- [ ] Implement `src/services/meta-template-management/` with focused submission orchestrator, server-only Meta Graph API adapter, reconciliation reader, webhook-status consumer, Prisma repository and module-local ports. Wire `whatsapp-events` worker dispatch through a thin job-name handler when the Messaging producer contract is available.
- [x] Consume frozen `WhatsAppTemplateMetaRegistration` rows and append `WhatsAppTemplateMetaEvent` receipts. Background maintains current `providerStatus`, provider ID and drift observations, **not** authoring ASTs, translation content, shop assignments or publication permissions.
- [ ] Reuse existing sender/WABA credential resolution, Meta API error/retry conventions, BullMQ worker orchestration and structured logging.
- [x] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [ ] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

## Interfaces / Contracts

**Consumes DB001** `WhatsAppTemplateMetaRegistration`, `WhatsAppTemplateMetaEvent` and immutable compiled JSON fields. **Produces/consumes** Meta's WABA template-management API via server-only client; authenticated input from the agreed Messaging producer via `whatsapp-events`. Only this module interprets provider status and writes Meta registration current-state projections.

**Ports:** `submitPreparedRegistration(registrationId)`, `processTemplateStatusObservation(job)`, `reconcileRegistration(registrationId)`. Use locally documented typed inputs at module boundary, not a duplicate authoring AST. Do not introduce a new Shared publication dependency.

## Dependencies

- `ARCH-047-DATABASE-001`


**Important:** Tasks are not Ready merely because their files exist. Confirm each dependency has `status: complete` (not only Passing tests / Accepted review) before claiming. DB001 was confirmed `complete` for Attempt 1. Dependencies outside this task must be resolved by their owners; do not implement across repositories.

## Enables

None in this nine-task Background set.

## Acceptance Criteria

- [ ] Unit tests show Meta POST receives the stored compiled payload **unchanged** and refuses any Meta edit endpoint, external template adoption or unpublished intent.
- [x] Image-header submissions use a valid authorised sample/media handle; a missing, invalid or external-original-URL sample is blocked before provider creation. Text-only templates continue unchanged. Submission never performs ShopBrand ingestion/R2 preprocessing.
- [ ] Duplicate submission, provider timeout + GET reconciliation, provider rejection, rate limiting and WABA mismatch tests; no double POST after confirmed creation.
- [ ] Authenticated queue observation tests, wrong job name/version, duplicate and reordered APPROVED/PAUSED/DISABLED, unmatched external template and provider-content drift.
- [x] PostgreSQL integration exercises unique event identities, registration status transitions and append-only event evidence; no automatic shop activation.
- [ ] Existing inbound/message-status queue processing and final-send admission regressions pass; focused unit/build/typecheck and `git diff --check`. End-to-end Meta webhook receipt belongs to Messaging/System Test.
- [x] No source/template authoring, shopper checkout mutation, Meta edit-existing-template call, externally authored Meta template adoption, or bypass of existing WhatsApp final-send safeguards is introduced.
- [x] Task implementation is modular, separately testable, and stays within `moda-interact-background/`; externally owned gaps are reported, not silently implemented.

## Validation

- [ ] Run the focused new tests and relevant existing regression suites identified above; record exact executable commands and outcomes.
- [x] Run the repository-declared build/typecheck (for this snapshot: `npm run build`) and focused ESLint where applicable; do not assume every repository has identical scripts.
- [ ] `git diff --check`, inspect changed-file scope and capture task-isolated start-of-attempt and mirrored-branch evidence.
- [x] When integration depends on a real PostgreSQL/BullMQ service, run the repository's declared integration harness or record the missing environment explicitly; do not claim an unrun test passed.

## Stop Condition

After finishing Work Items, Acceptance Criteria and Validation, fill the Completion Report, change task status to `review`, return both the implementation and parent task-branch evidence to `moda_architect`, and **STOP**. Do not start any enabled/adjacent task or update `docs/decisions/**/_index.md`.

## Implementation Notes

Meta template webhooks are WABA events and must reach the configured Meta app callback. `ARCH-047-MESSAGING-001` will own ingress enablement and publication; Background must **not** take over its callback route. Narrowly document queue job correlation and producer/consumer expectations without creating a second general WhatsApp event transport.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-003`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.

**Architectural concern:** If queue transport requires a new, genuinely cross-repository canonical contract unavailable in the installed Shared version, stop that slice and return the dependency gap to `moda_architect` instead of inventing a local duplicate.

## Completion Report

### Status

Blocked — developer Attempt 1, initially claimed `2026-10-25T19:11:32Z`. The bounded Meta submission/reconciliation module has been implemented and committed, but the full BG003 task cannot yet satisfy the queued-status-job and final-send regression criteria. Returning the cross-repository boundary to `moda_architect` for a scoped decision; not claiming Accepted/Complete.

### Files Changed

Implementation repository (`moda-interact-background/`, commit `568eed8`):

- `src/services/meta-template-management/contracts.ts`
- `src/services/meta-template-management/index.ts`
- `src/services/meta-template-management/meta-graph.adapter.ts`
- `src/services/meta-template-management/repository.ts`
- `src/services/meta-template-management/service.ts`
- `tests/unit/services/meta-template-management/meta-management.test.ts`
- `tests/integration/arch047-meta-template-management.integration.test.ts`

No parent architecture file, `_index.md`, existing WhatsApp worker, Messaging repository, or database schema was changed by this implementation commit.

### Work Completed

- Implemented module-local create-only Meta submission, frozen compiled-component transport, private server-side WABA credential use, image-header sample validation and provider-name collision blocking.
- Persisted a claim and POST intent before provider I/O; handled unknown create outcomes without blindly reposting; exposed reconciliation and bounded due-processing ports.
- Added Prisma-backed append-only Meta event evidence, event identity deduplication, provider projection and drift detection; no automatic merchant/shop activation or external-template adoption.
- Added injectable authenticated status-observation processing with repeat/reorder handling. This is **not** the production `whatsapp-events` queue decoder/handler.
- Used `@modainteract/moda-interact-shared/logging` and preserved/propagated unexpected errors; logging and compensation-error behavior are covered in focused unit tests.
- Implemented 16 new unit tests and one disposable-PostgreSQL integration scenario with multiple database assertions.
- Developer terminal evidence records a successful implementation commit and push: `568eed8` (`feat(arch-047-background-003)`) to `origin/task/ARCH-047-BACKGROUND-003`. The recording does **not** establish a later parent task-branch push or architect acceptance.

### Validation Results

Evidence: uploaded terminal recording `typescript(20261025-192158)` and the matching code snapshot `moda-interact-workspace-ARCH-047-BACKGROUND-003.zip`.

| Check | Command / evidence | Outcome |
|---|---|---|
| Dependencies | `npm ci`; `npm run prisma:generate` | Completed; npm reported 20 audit advisories (8 moderate, 12 high), not investigated in this task |
| Build/typecheck | `npm run build` (`prisma:generate` followed by `tsc`) | Passed; no TypeScript errors reported |
| Focused lint | `npx eslint src/services/meta-template-management tests/unit/services/meta-template-management` | No ESLint diagnostics reported in captured run |
| Unit + existing status/worker regression | `npx vitest run tests/unit/services/meta-template-management/meta-management.test.ts tests/unit/workers/whatsapp.worker.test.ts tests/unit/services/whatsapp-provider-status.service.test.ts` | **69/69 passed in 3 test files** (16 new, 53 existing) |
| Disposable PostgreSQL integration | `npm run test:integration -- tests/integration/arch047-meta-template-management.integration.test.ts` | **1/1 passed**, real Prisma persistence, concurrent claims, duplicate observation, reconciliation, stale CAS and no variant activation |
| Local diff check | `git diff --check` appears in terminal during patch application | No whitespace diagnostic shown; final post-commit diff check is not independently recorded |
| Branch publication | `git commit` and `git push -u origin task/ARCH-047-BACKGROUND-003` | Background implementation commit `568eed8` pushed |
| Final outbound-admission regression | Not present in captured commands | **Not run/verified** |
| Template-status BullMQ producer/consumer integration | No agreed ARCH-047 Messaging producer/job contract in supplied snapshot | **Not implemented/tested** |
| Real Meta webhook end-to-end | Separate Messaging/system-test boundary | **Not run** |

The existing database integration test is a **single combined scenario**, not a comprehensive matrix of independent database tests. It runs against the disposable test database (`TEST_DATABASE_URL`, `MODA_DISPOSABLE_INTEGRATION=1`); it does not exercise a BullMQ template-status job because that producer/consumer contract is absent.

### Deviations

- Did not wire a `message_template_status_update` job into `whatsapp-events`, or implement wrong-job-name/version rejection: the agreed Messaging producer and canonical cross-repository queue format are absent from this snapshot. A guessed local envelope would violate the task's explicit queue-contract stop condition.
- Implemented module-owned due-processing entrypoint only; no production scheduling caller or independent new queue was added.
- Did not run the existing final-send admission regression suite, so that acceptance condition is left unchecked.
- An initial patch-application command failed because the downloaded patch was not yet at the named local path; a subsequent application and the committed implementation are visible in the recording. The failed command is not counted as successful validation.

### Assumptions

- `ARCH-047-DATABASE-001` was `complete` at claim time per the canonical task record. The tested Prisma schema provides the expected registration/event tables.
- Admin owns preparation of immutable compiled components and authorised image sample handles; Background neither recompiles the AST nor ingests original merchant images.
- Messaging owns verification and publication of future Meta template-status events. Background accepts only validated/authenticated observation data at its current module-level port.

### Unresolved Issues

1. `ARCH-047-MESSAGING-001` is **planned but not defined** in the uploaded architecture. Agree and materialise its authenticated template-status BullMQ payload/job contract; then assign the correct owner to wire the existing Background `whatsapp-events` dispatcher and cover wrong name/version rejection.
2. Architect to decide whether this BG003 task should remain blocked pending that integration or be explicitly **narrowed** to the now-validated module, with a separate dependent queue-integration task. Do not silently treat the present module as a wired consumer.
3. Run and record the applicable outbound-admission/final-send regression suite before full BG003 acceptance. No passing result is claimed from the current terminal log.
4. Inspect task-isolated start-of-attempt synchronisation evidence and both published mirrored task branches during review. The task preparation metadata documents worktree paths and initial synchronisation; the terminal recording independently confirms the implementation worktree and background push only.

### Architectural Concerns

The missing Messaging queue contract is a cross-repository interface gap. No new private schema or unapproved Shared package should be created inside Background. Do not infer readiness for production Meta webhook processing, background polling or customer sends from the module-only tests. There is no evidence of changing the consent, STOP or final outbound-admission safeguards.

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

- Date: 2026-10-25.
- Change: The developer explicitly invoked `/moda_developer_create` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_background`, coordinator, repository, dependency, task scope, acceptance criteria and validation requirements.
- Dependency check: `ARCH-047-DATABASE-001` is `complete` in its canonical task record.
- Claim: Attempt 1 is claimed by `developer` at `2026-10-25T19:11:32Z` after canonical worktree preparation and synchronization.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-BACKGROUND-003`, branch `task/ARCH-047-BACKGROUND-003`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-BACKGROUND-003`, branch `task/ARCH-047-BACKGROUND-003`, created from current Background `origin/main` because no BACKGROUND-003 task branch existed locally or remotely.
- The parent task branch was merged with current workspace `origin/main`; it is intentionally ahead of its previously published task-branch tip and will be published with this claim. No implementation changes were made during preparation. No branch was merged into `main`.
