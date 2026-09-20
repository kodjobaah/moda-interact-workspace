---
id: ARCH-020-SHOPIFY-001
architecture_id: ARCH-020
title: Expose merchant capability feature preferences
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 170
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-SHARED-001
  - ARCH-016-SHOPIFY-002
enables:
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Expose merchant capability feature preferences

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Let merchants select eligible optional features while retaining the existing discount-policy controls.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Embedded merchant feature-selection read/action/UI services and existing recovery-settings integration only.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

### Duplicate-action protection

Every state-changing or costly UI action in this task must prevent duplicate
activation, including mouse double-click, double-tap, Enter/Space repetition and
form-submit plus button-click combinations. Acquire a synchronous submission
guard before awaiting work (a render-delayed disabled state alone is insufficient),
and route all activation paths through the same submit handler. Disable the
trigger and conflicting controls immediately, show a meaningful pending label,
and expose accessible busy/status feedback. Do not lock unrelated navigation.

Keep the guard until the operation has definitively completed, failed or been
cancelled. A client timeout is an unknown outcome: reconcile the original
operation before allowing a retry, rather than silently creating a second one.
On a known failure, restore controls and preserve input for an intentional retry.
Ignore stale completions so an earlier request cannot reset a newer request's
pending state. Debounce alone is not sufficient for mutations or paid previews.
Server authorisation and duplicate protection are required independently of the
browser controls; inspect direct duplicate requests as well as UI behaviour.

## Work Items

- [ ] Load arbitrary Admin-created feature identities and current plan mappings from the database; do not whitelist development seed keys. Creating a Feature alone does not establish plan eligibility. Test a newly created non-seed key through enabled mapping and opt-in, including absent preference. Absence of Commerce configuration must not rewrite a billing feature or its saved preference.

- [ ] Keep merchant UI selecting existing features; tools/templates are team-configured in Studio and selected via the capability's feature binding. Do not expose tool authoring to merchants.

- [ ] Preserve existing merchant followUpEnabled/followUpDelayMinutes controls, max one no-response follow-up, delay validation and credit-warning copy. C13 distinguishes a separately chargeable proactive follow-up from conversational replies; do not introduce another follow-up editor or reset pending schedules from feature saves. Include double-submit tests for this existing settings form.

- [ ] Inspect current feature-selection surfaces and reuse them where present; local source inspection found no ShopFeaturePreference editor to rely on.
- [ ] Present active eligible feature keys with current enabled/effective state and persist authenticated ShopFeaturePreference changes.
- [ ] Use the shared pure selection contract with authoritative plan facts; enforce ownership/eligibility server-side and preserve ALWAYS_ENABLED/system-required policy.
- [ ] Keep NONE/FIXED/AI offer choice in existing Recovery Settings, available to eligible Free and Paid shops; explain its effect on discount assistance.
- [ ] Add locale-complete labels and loading/denied/error states without exposing Studio internals or creating another feature catalogue.

- [ ] Guard preference switches and feature/recovery-settings save actions. Send explicit desired values, never a toggle command; use the existing unique shop/feature preference and transactional upsert/update-if-changed semantics. Duplicate equal-value requests produce no second state transition or secondary effect. Serialize conflicting writes for the same form/resource and ignore stale UI responses.

## Interfaces / Contracts

Existing Feature/plan mappings/ShopFeaturePreference and ARCH-016 recovery policy; shared selection DTOs.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C1, C9**. Also apply **C13** for outreach/continuation semantics. These are required acceptance inputs, not optional examples.

Implement a feature-preferences service/action and embedded page using current Shopify session ownership, never caller-supplied shopId. Display authoritative active eligible mapped features; disallow edits to ALWAYS_ENABLED/systemRequired or inactive/unmapped items. Write explicit desired enabled value with unique shop/feature row. Keep existing recovery-offer form as the only NONE/FIXED/AI editor.

### Required evidence

Use Free/Paid, enabled/disabled mapping, active/inactive feature, missing opt-in, required feature and override fixtures. Test forged shop, same-value concurrent requests and conflicting same-form requests with refetch. Add all labels to existing supported locale files; run declared locale checker or document if none exists.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-SHARED-001
- ARCH-016-SHOPIFY-002

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Unauthorised, inactive, other-shop and plan-ineligible preferences cannot be written through direct actions.
- [ ] Merchant selection drives the initial capability grant for a new conversation; billing/plan prices and existing admin override precedence are unchanged.
- [ ] Discount assistance is not accidentally introduced as a paid-only feature.

- [ ] Double-clicking a switch or Save results in the intended state once, not an immediate reversal, duplicate preference row or repeated secondary action. Direct repeated requests are idempotent; validation/network failure preserves inputs and restores controls for a deliberate retry.

## Validation

- [ ] Feature on/off fixtures alter tools for eligible new conversations; existing grants never gain newly mapped tools. Recovery-policy discount access retains its existing semantics.

- [ ] Test same-tick mouse double-click, repeated keyboard/form submission, delayed success, known error/cancel and timeout with unknown outcome; assert one operation, visible pending state, preserved input and a deliberate successful retry. For server mutations/previews also send concurrent duplicate requests directly and verify persisted effects/provider invocation counts.
- [ ] Run focused merchant action/selection policy tests and declared typecheck/lint/localisation validation.
- [ ] Inspect embedded UI with local fixtures for Free/Paid, opt-in/required, disabled feature and override states.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; its real repository must be provisioned before execution preparation.

## Completion Report

### Status

Not Started.

### Files Changed

None; implementation has not started.

### Work Completed

None; task definition only.

### Validation Results

Not run. At execution, distinguish agent checks from exact developer validation required.

### Deviations

Task definition authored on local main by explicit developer request. Normal execution policy remains unchanged.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

See parent architecture review assumptions; no implementation evidence asserted.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-SHOPIFY-001. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.
