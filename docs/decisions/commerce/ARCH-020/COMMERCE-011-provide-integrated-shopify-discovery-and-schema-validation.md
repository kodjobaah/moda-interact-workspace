---
id: ARCH-020-COMMERCE-011
architecture_id: ARCH-020
title: Provide integrated Shopify discovery and schema validation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 85
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-002
  - ARCH-020-SHARED-003
enables:
  - ARCH-020-COMMERCE-005
  - ARCH-020-COMMERCE-003
  - ARCH-020-COMMERCE-008
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
created: 2026-09-20
updated: 2026-09-20
---

# Provide integrated Shopify discovery and schema validation

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Provide all Shopify discovery, schema browsing, explanatory content and query validation needed by Studio authoring without sending staff to an external IDE.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

C15 developer-resource adapter, pinned Shopify schema artifact, authenticated discovery services, structured field/mapping validation and local fixtures. COMMERCE-008 owns the actual U07 page; this task owns its backend and schema compiler contract.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

- [ ] Implement C15 typed discovery operations, using a pinned @shopify/dev-mcp supervised stdio child and only its verified documentation/schema/validation capabilities. Capture actual upstream initialize/list/call fixtures and map them to the stable Studio API; no arbitrary proxy.
- [ ] Deliver the official Storefront2026-07 schema artifact, SHA-256, provenance, version support and distribution evidence. Provide paginated typed fields/arguments/constraints and inline explanations, including unavailable/token-required fields. Fixture strings must not stand in for the actual schema.
- [ ] Implement deterministic schema selection -> named GraphQL query compilation, variable mapping validation, response-path derivation and C14 AST/root/bounds checks. No business feature names in compiler dispatch.
- [ ] Implement POST discovery/search, POST discovery/document, GET discovery/schema and POST discovery/validate exactly as C15; authentication, limits, timeout, response bounds and redaction included.
- [ ] Keep local schema/compiler validation operational on docs-search failure; show typed errors for the UI, retain accepted schema artifacts across deployments, and block unsupported schema versions. No provider/store credentials in the child environment or submitted search text.
- [ ] Document child startup/health/restart/shutdown in docs/shopify-discovery-runtime.md; pass only explicit nonsecret environment needed for documentation connectivity. Bound pending calls and reap child on service shutdown. No extra network listener or Shopify CLI execution.
- [ ] Supply U07/N04 service fixtures for docs search -> document -> field selection -> query validation -> apply-to-draft payload, including no external navigation requirement. Authoring services create no live grant, Shopify write, billing preference or release.

## Interfaces / Contracts

Visual page ownership: Service owner for exact U07 /explore, implemented by COMMERCE-008. Supply both Documentation and Schema and query builder tabs; do not add a separate UI or require external navigation. [Approved prototype](../../../architecture/ARCH-020-studio-approved-prototype.html).

Binding [C14/C15 contracts](../../../architecture/ARCH-020-implementation-contracts.md) and [Studio page specification](../../../architecture/ARCH-020-studio-ui-design.md), U07/N04. Shared exports strict provider-neutral descriptor/query-validation schemas; this task owns actual Shopify schema metadata and upstream tool adaptation. COMMERCE-003 publication consumes the injected validator; COMMERCE-005 runtime consumes its schema/compiler artifacts. Return field-level validation errors, not upstream stack traces or secrets.

### Required evidence

Record actual pinned dependency/tool schemas, artifact hash/version/provenance, denied upstream capabilities, resource limits, offline-local validation and child environment isolation. The compatibility fixture must exercise the real pinned upstream process locally; deterministic mocks alone do not satisfy that compatibility evidence.

## Dependencies

- ARCH-020-COMMERCE-002
- ARCH-020-SHARED-003

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-005
- ARCH-020-COMMERCE-003
- ARCH-020-COMMERCE-008
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001

## Acceptance Criteria

- [ ] Staff-facing service operations provide complete supported-field guidance, source excerpts and schema-generated query definitions; no handwritten per-feature operation registry is needed.
- [ ] Invalid/unknown fields, forbidden roots/mutations/directives, excessive nesting/list bounds, missing variables and wrong schema hashes are rejected before execution/publication.
- [ ] Remote docs unavailability preserves local schema browsing/validation; missing authoritative schema fails closed. No automatic API version upgrade.
- [ ] Anonymous/revoked/other-service callers are denied; requests cannot invoke shell/CLI/store tools, pass credentials or fetch arbitrary URLs.
- [ ] Accepted artifacts support the U07 traversal N04 and C14 product-description example, including its real schemaHash. No production credential or live Shopify store is needed for local discovery validation.

## Validation

- [ ] Test the complete service traversal plus timeouts, upstream schema changes, invalid tool names, URL/domain injection, oversized responses, rate/concurrency limits and absent Redis.
- [ ] Assert logs exclude query content/secrets and child environment excludes DB/Background/Shopify/preview credentials.
- [ ] Run fixture tests, declared type/lint checks and the pinned-process compatibility fixture. Record exact versions/hashes/commands; actual runtime tests happen during implementation, not task authoring.
- [ ] Record a requirement-to-fixture matrix for C14/C15 and U07/N04; keep developer-owned deployed validation separate.

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

Commerce remote repository/submodule provisioning remains outstanding; role/route definitions exist in this review packet.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-COMMERCE-011. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
