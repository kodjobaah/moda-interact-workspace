---
id: ARCH-020-COMMERCE-005
architecture_id: ARCH-020
title: Implement basket and product discovery tools
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-004
  - ARCH-020-COMMERCE-011
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-006
  - ARCH-020-COMMERCE-013
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Implement basket and product discovery tools

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Provide tenant-safe basket context and current variant-level product discovery over MCP.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Generic public Shopify query execution, schema-bound result projection, trusted recovery basket and existing product policy helpers. No per-business-feature registry or fixed feature catalogue.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

- [ ] Implement C14 generic SHOPIFY_STOREFRONT_QUERY executor using COMMERCE-011's accepted exact schema/AST compiler. Execute fixed published queries against recovery-owned canonical shop host tokenlessly, with typed variables/resultPath and no privileged fallback.
- [ ] Enforce query/depth/list/response/time bounds, API-version response verification, partial-error denial and current grant authority. Return source/schema/version/observedAt plus selected values; never promote public query data into discount Evidence.
- [ ] Keep basket/product policy adapters as reusable helpers and sample imports. Add a previously unregistered product-description query using ordinary publish operations; do not add its name as a code handler.

- [ ] Implement recovery.getBasket and shopify.searchProducts operation adapters for the generic executor, rather than bespoke MCP endpoints. Search supports mapped maximumPrice decimal strings, availableOnly and bounded limits.

- [ ] Require an authorised recovery-linked WhatsApp conversation and load its checkout-recovery basket snapshot. Reject absent/sentinel recovery links; normalise bounded line items and report unknown/stale basket facts without inventing a basket.
- [ ] Read existing installation credentials server-side and verify shop domain; do not own token lifecycle or log provider payloads.
- [ ] Implement bounded current product/variant search with availability, decimal prices, market/currency evidence and safe URLs.
- [ ] Add input/output validation, provider timeouts/throttle errors, scoped pagination and configurable bounded query construction.

## Interfaces / Contracts

Canonical basket/product schemas; existing installation and recovery snapshot fields.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C4, C8**. These are required acceptance inputs, not optional examples.

Implement recovery.getBasket and shopify.searchProducts operation adapters, replacing test fixtures with read-only production adapters; the MCP names come from database definitions. Explicitly map existing CheckoutRecovery.lineItems provider shapes to the canonical basket; fixture every supported shape. Missing/unrecognised data stays unknown, never guessed from prompt text.

### Deterministic review clarification

Installation credentials are available only to privileged POLICY_OPERATION
adapters. SHOPIFY_STOREFRONT_QUERY never loads or forwards installation tokens
and never falls back to a privileged adapter. Assert credential lookup count zero
for public queries, including failures; cover the privileged branch separately.

### Required evidence

Provider fixtures assert static request destinations/query variables, unknown market/price/availability, pagination limits, tampered cursor, cross-shop IDs and provider timeout. Record no mutation request issued.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-COMMERCE-004
- ARCH-020-COMMERCE-011

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-006
- ARCH-020-COMMERCE-013
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] New authored query with a different selection works without code/deployment changes; unknown field/root, mutation, credential/domain input, version fallback, partial errors and oversized response fail before unsafe data use.
- [ ] Query authoring requires no new OAuth scopes or privileged Admin credential; token-required Storefront fields return unavailable with no alternate credential path.

- [ ] Model input cannot select another shop, arbitrary API host or raw GraphQL query; cross-tenant recovery/product references fail.
- [ ] Historical basket state, unknown prices/market and unavailable variants are represented accurately, never promoted to current facts.
- [ ] Both tools work through the MCP dispatcher and perform no basket/order/discount mutation.

## Validation

- [ ] Use the C14 blue-shirt example; assert mapped query/price/availability/limit, verified currency, structured products and exact rendered/empty/unavailable text, with no cross-merchant credential arguments.

- [ ] Run provider-fixture tests for missing/stale basket facts, rejected non-recovery turns, variants, currencies, pagination, errors and tenant isolation.
- [ ] Run declared local type/lint checks and a local MCP tool round trip with mocked Shopify responses.

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

Expected execution branch: task/ARCH-020-COMMERCE-005. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
