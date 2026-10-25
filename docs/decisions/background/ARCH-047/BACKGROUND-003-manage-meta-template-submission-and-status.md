---
id: ARCH-047-BACKGROUND-003
architecture_id: ARCH-047
title: Implement Meta template submission and reconciliation module
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
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

This is a **portable task definition** prepared from the 24 October 2026 workspace snapshot and consolidated DB001 Attempt 7 contract. It is not a repository implementation, task claim or evidence of a created worktree/branch. No new ARCH-047 Shared package is assumed. The parent architecture and `BACKGROUND-001` require reconciliation to the final Admin-owned AST/compilation and DB-backed keyed-segment translation decisions before dependent work is promoted.

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

**R6 — Reliability.** Bounded retry/backoff, error taxonomy and observability, no secrets or full raw payloads in logs. Reuse existing queues/workers rather than deploying an unrelated ingress service.

## Work Items

- [ ] Implement `src/services/meta-template-management/` with focused submission orchestrator, server-only Meta Graph API adapter, reconciliation reader, webhook-status consumer, Prisma repository and module-local ports. Wire `whatsapp-events` worker dispatch through a thin job-name handler when the Messaging producer contract is available.
- [ ] Consume frozen `WhatsAppTemplateMetaRegistration` rows and append `WhatsAppTemplateMetaEvent` receipts. Background maintains current `providerStatus`, provider ID and drift observations, **not** authoring ASTs, translation content, shop assignments or publication permissions.
- [ ] Reuse existing sender/WABA credential resolution, Meta API error/retry conventions, BullMQ worker orchestration and structured logging.
- [ ] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [ ] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

## Interfaces / Contracts

**Consumes DB001** `WhatsAppTemplateMetaRegistration`, `WhatsAppTemplateMetaEvent` and immutable compiled JSON fields. **Produces/consumes** Meta's WABA template-management API via server-only client; authenticated input from the agreed Messaging producer via `whatsapp-events`. Only this module interprets provider status and writes Meta registration current-state projections.

**Ports:** `submitPreparedRegistration(registrationId)`, `processTemplateStatusObservation(job)`, `reconcileRegistration(registrationId)`. Use locally documented typed inputs at module boundary, not a duplicate authoring AST. Do not introduce a new Shared publication dependency.

## Dependencies

- `ARCH-047-DATABASE-001`


**Important:** Tasks are not Ready merely because their files exist. Confirm each dependency has `status: complete` (not only Passing tests / Accepted review) before claiming. DB001 is developer-owned and may remain in progress pending explicit completion. Dependencies outside this task must be resolved by their owners; do not implement across repositories.

## Enables

None in this nine-task Background set.

## Acceptance Criteria

- [ ] Unit tests show Meta POST receives the stored compiled payload **unchanged** and refuses any Meta edit endpoint, external template adoption or unpublished intent.
- [ ] Duplicate submission, provider timeout + GET reconciliation, provider rejection, rate limiting and WABA mismatch tests; no double POST after confirmed creation.
- [ ] Authenticated queue observation tests, wrong job name/version, duplicate and reordered APPROVED/PAUSED/DISABLED, unmatched external template and provider-content drift.
- [ ] PostgreSQL integration exercises unique event identities, registration status transitions and append-only event evidence; no automatic shop activation.
- [ ] Existing inbound/message-status queue processing and final-send admission regressions pass; focused unit/build/typecheck and `git diff --check`. End-to-end Meta webhook receipt belongs to Messaging/System Test.
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

Meta template webhooks are WABA events and must reach the configured Meta app callback. `ARCH-047-MESSAGING-001` will own ingress enablement and publication; Background must **not** take over its callback route. Narrowly document queue job correlation and producer/consumer expectations without creating a second general WhatsApp event transport.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-003`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.

**Architectural concern:** If queue transport requires a new, genuinely cross-repository canonical contract unavailable in the installed Shared version, stop that slice and return the dependency gap to `moda_architect` instead of inventing a local duplicate.

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

If queue transport requires a new, genuinely cross-repository canonical contract unavailable in the installed Shared version, stop that slice and return the dependency gap to `moda_architect` instead of inventing a local duplicate.

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
