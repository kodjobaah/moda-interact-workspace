---
id: ARCH-020-COMMERCE-009
architecture_id: ARCH-020
title: Preview capabilities in an isolated conversation sandbox
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 130
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-007
  - ARCH-020-SHARED-001
  - ARCH-020-COMMERCE-013
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-010
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Preview capabilities in an isolated conversation sandbox

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Let staff exercise draft behaviour with the production runner contract and isolated fixtures.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Studio preview UI/server route, synthetic fixture adapters, explicit bounded model preview and ephemeral result trace.

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

- [ ] Reuse C7.1 auth helpers for all preview routes/actions in both Google and development modes. Development SUPER_ADMIN remains subject to preview quotas, isolation and mutation guards; it grants no live MCP access.

- [ ] Implement C16 U14 draft response preview handoff, frozen synthetic definition, Reply/Structured details views and return-to-composer flow. Validate R01–R05/R08/R10/R11 without production access.

- [ ] Apply C6.1 as amended by final C6.2 in U14 Conversation mode using synthetic recovery status, nullable completedAt, languageTag/languageSource and customer-message fixtures. Supply equivalent fixed host recovery instructions to the same Shared runner; do not expose them as editable capability prompts. Select fixtures before Start conversation; use a scripted later-turn state change for P05 without replacing the frozen grant.

### U14: tool tests and conversation traversal (COMMERCE-009)

Landing has **Tool test** and **Conversation** modes. Source context preselects
saved draft/revision/release; direct navigation requires explicit selection.

Tool test: choose saved tool revision, synthetic scenario (success, empty, missing
fact, provider failure), enter schema-driven input, Run -> same page with mapped
variables/arguments, structured facts, rendered text and validation/failure codes.
No live Shopify request. Editing test input invalidates visible success until
rerun. Return to tool links to U06; code/schema edits occur there.

Conversation: choose saved behaviour revisions or release, synthetic feature flags
and fixture basket. **Start conversation** freezes synthetic prompt/tool grant;
then show chat with message input, Send, Cancel run, Reset conversation, trace and
remaining limits. Default Fixture mode is deterministic. Explicit Model mode uses
separate preview credentials and C9 quotas; controls explain unavailable config
or exhausted budget. No production model credentials/customer transcripts.

Send creates one previewRunId before dispatch, disables duplicate sends, preserves
input on known failure and shows Running/Completed/Failed/Cancelled/Unknown.
Trace lists discovered tools, chosen tool/input, structured output and final answer.
Cancel requests cancellation of that same run and waits for confirmed status;
unknown state is reconciled before another run. C9 max20 turns,32k history,24h
retention and model budgets apply. Reset confirms abandoning synthetic state and
creates a new preview conversation; never replaces a live grant. Changing selected
release/tools/flags requires reset confirmation; an ongoing preview does not gain
new tools. Back returns the originating page, or U03 when entered from sidebar.



- [ ] Preview unpublished database-defined tools through the same definition interpreter/renderer with fixture operation adapters. Freeze all schemas, mappings, operations and templates in the preview conversation grant; edits require a new preview conversation.

- [ ] Use the same ./commerce/runner version as Background with synthetic basket/shop/customer fixtures and authorised draft bundle loading.
- [ ] Provide deterministic model/tool fixtures by default and an explicit model-backed preview with separate credentials and per-staff budget.
- [ ] Display rendered prompt, available tools, trace, reply, evidence and revision/runner identity without exposing credentials.
- [ ] Enforce preview purpose at the server; fixtures cannot invoke production provider writes, WhatsApp delivery or billable recovery admission.
- [ ] Store only bounded audit metadata/hash/version; keep synthetic preview transcript ephemeral and prevent production-message ingestion.

- [ ] Guard Run preview, rerun and cancel. Issue one previewRunId for each intentional run and reuse it on transport retries. Use existing platform Redis with an atomic claim keyed by environment, authenticated admin ID and previewRunId (24-hour deduplication lifetime, longer than the bounded run deadline); store payload hash and bounded status/result. Only the claim winner invokes the model or reserves preview budget. Matching duplicates return existing running/completed/failed/unknown status; changed payload conflicts. A crashed/unknown run is not automatically relaunched. Cancellation marks the original run and retains its claim; a new intentional rerun receives a new ID. No in-memory-only cross-replica guard.

- [ ] Pin one fixture grant for the whole preview conversation. Add fixtures where a later question needs an ungranted tool or unverified store policy; preview must refer to the store. Publishing/editing during the preview does not expand its tools; an explicit new preview conversation gets a new grant.

## Interfaces / Contracts

Visual page ownership: Implement exact U14 /preview with Tool test and Conversation modes. Use the approved U14 screen and embedded traversal, including return links to U06/U09/U11/U13. [Approved prototype](../../../architecture/ARCH-020-studio-approved-prototype.html).

Shared runner and canonical manifest schemas; fixture adapters match production tool result schemas.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C4, C6, C9**. These are required acceptance inputs, not optional examples.

Implement preview conversation state separate from previewRunId. Deliver Redis atomic claim/budget/status/cancel operations and a bounded synthetic fixture catalogue. Default fixture mode uses no live keys. Paid preview uses explicit separate model config; no real message ingestion, credentials or live Shopify/MCP provider access.

### Deterministic review clarification

Implement C9.1 route/body/status/ownership contracts and all cross-replica
creation, run, cancel and busy-conversation fixtures. Consume the U10 authenticated
layout handoff specified in COMMERCE-008 and the UI design; test real N13 return
without losing edits. P06/P07 use the final C6.2 shop-initialized/detected-language
rule, with no customer-explicit-preference feature. Speech scenarios inject a
persisted synthetic transcript; preview never transcribes audio or sends WhatsApp.

### Required evidence

Cross-instance tests count one budget/model start per run ID, changed-payload conflicts, cancellation flag propagation, crash unknown outcome, expired in-flight slot without dedupe deletion, per-admin/hour/global bounds and preserved synthetic grant across turns. Publishing/editing requires a new preview conversation to alter prompts/tools.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-COMMERCE-013

- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-007
- ARCH-020-SHARED-001

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-012

- ARCH-020-COMMERCE-010
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Demonstrate the assigned C16 response-contract cases with named fixtures and actual outcomes; reference the exact published definition/hash or synthetic preview definition used.

- [ ] Provide named C6.1 P01–P12 preview scenarios and deterministic assertions for context, grant and final-output handling; list expected natural-language outcomes separately. No live records, production credentials or WhatsApp sends.

- [ ] U14 Tool test and Conversation modes follow the exact entry/return routes, frozen selection, send/cancel/reconcile/reset states specified above. N10/N11 pass with U06/U09/U11/U13 source contexts and sidebar entry; no dead-end navigation.
- [ ] New query tools use the same C14 validator/projector/template renderer against fixtures, and independently published/shared revisions remain pinned for a preview conversation.

- [ ] Draft instructions can be tested without publication and are unreachable using production worker credentials.
- [ ] An identical scripted fixture produces the same contract/selection/tool sequence in Studio and Background harnesses.
- [ ] Cancellation, repeated preview requests and budgets cannot create unbounded model spend or production side effects.

- [ ] Concurrent direct requests with the same previewRunId invoke the model and reserve budget at most once within the 24-hour deduplication window, including retries, cancellation and requests to different instances. The UI cannot accidentally start another paid run after timeout; a new run requires a deliberate rerun action.

- [ ] Multi-turn preview proves identical tool boundaries and grounded referral behaviour to the production runner; no extra model call is started merely to acquire another tool.

## Validation

- [ ] Run the exact C14 example and malicious/missing-field variants with fixture data. Preview/live interpreter parity must cover data and renderedText; no production provider connection or additional paid call is introduced by rendering.

- [ ] Add focused multi-turn grant and unanswerable-question fixtures for the scoped acceptance criteria; assert granted tool IDs/versions and referral output, not just prompt text.
- [ ] Test same-tick mouse double-click, repeated keyboard/form submission, delayed success, known error/cancel and timeout with unknown outcome; assert one operation, visible pending state, preserved input and a deliberate successful retry. For server mutations/previews also send concurrent duplicate requests directly and verify persisted effects/provider invocation counts.
- [ ] Run deterministic preview/runner parity, role, draft isolation, budget and cancellation tests.
- [ ] Inspect local preview flows with fixture data. Any live model test is explicitly invoked and its model/version recorded separately.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; the actual repository must be provisioned before execution preparation.

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

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. No additional provisioning prerequisite is introduced.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-COMMERCE-009. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
