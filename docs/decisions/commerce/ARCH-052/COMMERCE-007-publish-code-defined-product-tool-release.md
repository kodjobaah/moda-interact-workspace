---
id: ARCH-052-COMMERCE-007
architecture_id: ARCH-052
title: Publish reviewed code-defined product tools to the TEST Commerce release
task_kind: publication
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-COMMERCE-006
- ARCH-052-MCP-003
enables:
- ARCH-052-BACKGROUND-007
- ARCH-052-BACKGROUND-010
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-COMMERCE-007: Publish reviewed code-defined product tools to the TEST Commerce release

## Architecture

Architecture ID: `ARCH-052`. Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Defined but not materialised**; no Git branch or worktree created.

## Objective

Activate the already accepted canonical product-search and exact-item capability revisions in the existing TEST release; this is publication, not implementation.

## Context

The existing Commerce publication lifecycle validates executable registration. Waiting for accepted MCP-003 prevents publishing tool descriptors whose provider handler does not exist. The developer performs this release gate explicitly.

## Scope

- Confirm COMMERCE-006 and MCP-003 task YAMLs are `complete` and architect-accepted. Invoke the exact approved code-defined bootstrap command from COMMERCE-006 as a privileged, auditable TEST operation. It creates or verifies the canonical drafts, publishes tool revisions with the existing lifecycle, appends them without removing other capabilities, activates the new immutable TEST release by CAS and records release/feature/tool revision IDs.
- Verify the published product descriptors appear in MCP `tools/list` under an authorised recovery attempt and that `tools/call` reaches both accepted provider handlers for Shopify and Woo test fixtures. Verify active release pointer, pinned descriptor hashes and repeated invocation no-op. No manual Studio edits or source implementation changes.
- Never publish directly to production under this task; production rollout remains an independently authorised operational action after tests.

## Out of Scope

No additional database table/column/migration, migration backfill, alternate provider proxy, customer-facing product database/cache, secret-bearing logs, unrelated architecture or other repository implementation.

## Requirements

- This is **task_kind: publication**, `execution_mode: developer`, `completion_mode: developer`; exact COMMERCE-006 and MCP-003 YAML prerequisites must be architect-accepted `complete`. Do not claim if either is unfinished.
- Perform only the existing authorised TEST Commerce release/bootstrap operation for previously accepted code-defined product tool identities. Do not edit product/discount source, add new behavior, rerun source tests/lint/typecheck/build or perform a production release.
- Existing immutable release feature/entitlement and MCP published-tool pin semantics remain enforced; idempotent reruns must not create duplicate release or tool revision.
- Record exact release version, tool definition hashes, activated TEST release ID, permissions/audit evidence and repeat invocation outcome. Any required source fix returns to the owning implementation task/architect.
- Read agent/task worktree isolation policy and record dedicated launcher-prepared development worktree and reconciliation, use bounded shared logger without logging secret tokens.

## Work Items

- [ ] Confirm COMMERCE-006 and MCP-003 are Complete with accepted Architect Reviews and the intended TEST release target.
- [ ] Invoke COMMERCE-006's already reviewed code-defined bootstrap and approved Commerce publication command; record the exact immutable release/definition IDs.
- [ ] Verify TEST release activates both `commerce_search_products` and `commerce_get_product`, and MCP lists/calls their existing accepted handlers for each supported platform.
- [ ] Repeat publication to prove no-op/idempotence and verify no unauthorized release members were changed.
- [ ] Inspect only publication metadata and release records; do not rerun unit/integration tests, lint, typecheck or build. Record developer completion decision separately.

## Interfaces / Contracts

Existing Commerce `publishToolRevision`, `createSuccessorRelease`, `activateRelease` and `ensureMerchantKnowledgeBootstrap` pattern, new canonical `ensureInitialOutreachProductBootstrap` exported by COMMERCE-006. Product definition versions independent from policy operation version.

## Dependencies

- `ARCH-052-COMMERCE-006` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-MCP-003` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-BACKGROUND-007`
- `ARCH-052-BACKGROUND-010`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Exact reviewed version and release identifiers are recorded.
- [ ] Both tools callable through MCP under an authorised attempt; no manual authoring or duplicate release on rerun.
- [ ] No code change other than permitted publication/release metadata.

## Validation

- [ ] Exact accepted implementation prerequisites and authorised TEST release identity.
- [ ] Publication invocation success, active release pointer and both version-pinned product descriptors at the intended target; repeat is idempotent.
- [ ] Verify absence of implementation-source changes and run only `git diff --check` for release metadata. **Do not rerun accepted implementation tests, lint, typecheck or build.**

## Stop Condition

Once Work Items, acceptance criteria and validation are met, set task status to `review`, complete its report, return to `moda_architect` and **STOP**. Do not mark it Complete, publish another task, merge branches or push `main`.

## Implementation Notes

Expected workspace-relative owned source paths (confirm paths exist in checked-out worktree before editing):

- `moda-interact-commerce/src/commerce/bootstrap/initial-outreach-products.ts` (invoke, not edit)
- `moda-interact-commerce/src/commerce/integration/backend.ts` (existing lifecycle plumbing; no source changes)

## Completion Report

### Status

Not Started — portable definition; no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Confirm execution baseline in dedicated task worktree.

### Unresolved Issues

None established.

### Architectural Concerns

Return material contract/security/proof gaps to `moda_architect` without inventing a workaround.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation accepted.

### Reviewed Files

Task definition and uploaded 29 October 2026 snapshot only.

### Validation Reviewed

No implementation tests yet.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through canonical task launcher only after dependencies are Complete.
