---
id: ARCH-052-COMMERCE-007
architecture_id: ARCH-052
title: Execute reviewed Commerce system-product-tool sync in TEST
task_kind: publication
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
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
updated: '2026-10-31'
---

# ARCH-052-COMMERCE-007: Execute reviewed Commerce system-product-tool sync in TEST

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`.

**Defined but not materialised.** This is a developer-executed, developer-completed **publication** task. It does not implement or change the synchronisation script.

## Objective

Apply the architect-accepted `COMMERCE-006` **environment synchronisation script** to the existing TEST Commerce release, after the accepted MCP provider handlers exist; record auditable publication and repeat-run evidence. No manual Commerce Studio authoring.

## Context

- `COMMERCE-006` implements the reusable source-controlled product descriptors and `npm run commerce:sync-tools` command with a read-only plan and explicit apply mode.
- `MCP-003` implements direct Shopify GraphQL and WooCommerce REST product search/lookup. Its acceptance is a prerequisite for activating descriptors that advertise those operations.
- The existing Commerce immutable release and capability feature-gating behaviour must remain authoritative. `product_search` is the existing Feature; both `commerce_search_products` and `commerce_get_product` are code-defined tool/capability identities.

## Scope

- Confirm `ARCH-052-COMMERCE-006` and `ARCH-052-MCP-003` are each `status: complete` with `Architect Review: Accepted` in their actual task definitions, and the accepted script version is installed in the dedicated developer worktree.
- Verify the configured TEST database target and its environment identity **before** running the script; use the operationally authorised `COMMERCE_SYSTEM_TOOL_ACTOR_EMAIL` resolving to an active `SUPER_ADMIN`. Obtain these values through approved private environment configuration; never copy secrets into the task or logs.
- Execute the approved read-only plan, inspect changes to the two product tools and preservation of unrelated active release members, then execute the reviewed `--apply` command **only against TEST**.
- Verify the TEST `CommerceReleasePointer` points to a release containing **exactly one active pin for each** product capability and the appropriate published definition version and hash. Confirm unrelated capabilities, existing response contract and Feature snapshots are unchanged.
- Execute the script's `--dry-run` again followed by an identical `--apply` invocation. Both should report `UNCHANGED`; no new tool draft, tool revision, capability, release, audit record or pointer mutation may be created.
- Record the exact command, definition versions/hashes, active release ID, product tool revision and capability IDs, old release ID, operator identity, environment and output status. A source change or unsupported release conflict returns to `moda_architect`; do not fix it inside this task.

## Out of Scope

- No source code, NPM dependency, schema, config or tool definition edits; no production/staging/development rollout; no new feature creation, merchant entitlement change, manual Commerce Studio authoring or alteration of unrelated release entries.
- No re-running the already accepted implementation's unit/integration tests, typecheck, lint, build or provider product-read tests. `MCP tools/call` provider execution is end-to-end/system-test scope, not this publication task's validation requirement.
- No creation of scheduled deployment automation or silent Commerce startup publication.

## Requirements

- Preserve `task_kind: publication`, `execution_mode: developer`, `completion_mode: developer`. Never claim the task until both prerequisites are architect-accepted `complete`.
- Use only the accepted code-defined source of truth and the existing audited Commerce lifecycle to publish/activate. `--dry-run` must not modify any persistent record; `--apply` must preserve unrelated Commerce release membership and use existing CAS.
- Require exact target `TEST` (not a general `--environment` value chosen by the operator) for this task. Refuse to execute if `DEPLOYMENT_ENVIRONMENT_NAME` or the configured database target is inconsistent with TEST.
- Never print database credentials, product URLs, customer data, Shopify/WooCommerce tokens or raw provider data. Persist operational evidence in the Completion Report with bounded metadata.
- The developer, not the repository agent, decides final completion after an accepted review. This task only publishes the previously accepted implementation.

## Work Items

- [x] Read and verify the accepted COMMERCE-006 and MCP-003 task definitions, implementation commits and required physical-isolation evidence.
- [x] Verify the TEST target, authorised actor and checked-out version of the accepted `commerce:sync-tools` command.
- [x] Run the dry-run command; inspect intended product-tool changes and unrelated-member preservation.
- [x] Run the apply command once; capture audited release/pointer/revision/capability evidence.
- [x] Rerun dry-run and apply to prove no-op/idempotence without additional durable mutations.
- [x] Record publication evidence and leave task for the required developer completion decision. Do not enter another implementation task.

## Interfaces / Contracts

Use the **exact command** built and accepted by COMMERCE-006; these are the required TEST invocations:

```bash
npm run commerce:sync-tools -- --environment=test --dry-run
npm run commerce:sync-tools -- --environment=test --apply
npm run commerce:sync-tools -- --environment=test --dry-run
npm run commerce:sync-tools -- --environment=test --apply
```

Expected published identities:

```typescript
const expected = [
  {
    name: "commerce_search_products",
    capabilityKey: "commerce_search_products",
    featureKey: "product_search",
    definitionVersion: "1.0.0",
    operation: "products.search",
    operationVersion: "1.0.0",
  },
  {
    name: "commerce_get_product",
    capabilityKey: "commerce_get_product",
    featureKey: "product_search",
    definitionVersion: "1.0.0",
    operation: "products.get",
    operationVersion: "1.0.0",
  },
] as const;
```

The actual published revision identifiers and content hashes come from the script receipt and TEST release records. Do not invent them. Use the existing `CommerceReleasePointer` and `CommerceRelease` read models for publication confirmation. Neither raw MCP `tools/call` execution nor provider API requests are part of this publication gate.

## Dependencies

- `ARCH-052-COMMERCE-006` — accepted complete synchronisation script and canonical definitions.
- `ARCH-052-MCP-003` — accepted complete Shopify/WooCommerce product tool handlers, so advertised tools have a supported implementation.

## Enables

- `ARCH-052-BACKGROUND-007`
- `ARCH-052-BACKGROUND-010`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] TEST only, with an explicitly authorised actor and verified target environment.
- [ ] Plan and actual publication contain only the two accepted product-tool identities and preserve unrelated Commerce release state.
- [ ] The exact accepted product definition versions/hashes and TEST active-release pointer are recorded.
- [ ] The second identical apply returns `UNCHANGED` without any new durable writes.
- [ ] No implementation source or environment outside TEST was changed.

## Validation

- [ ] Prerequisites are `complete` and `Architect Review: Accepted` before publication begins.
- [ ] Dry-run/apply receipts and TEST release read-model state confirm the required published tool pins and preservation of other members.
- [ ] Repeated invocation proves no new audit, draft, revision, capability, release or pointer writes.
- [ ] Confirm no implementation-source changes. `git diff --check` applies only if release-specific metadata was legitimately changed. **Do not rerun implementation tests, lint, typecheck or builds.**

## Implementation Notes

This task **invokes only** the previously accepted `moda-interact-commerce/scripts/sync-system-commerce-tools.mjs` through `npm run commerce:sync-tools`; the source-control locations listed in COMMERCE-006 are not to be edited here. No additional publication script or manual Studio process may be introduced.

Keep `COMMERCE-007` as a separate release gate from `COMMERCE-006` implementation. Production deployment requires a separate explicit operational decision after ARCH-052 system validation and is not authorised by this task.

## Stop Condition

After recording the authorised TEST publication outcome and developer Completion Report, return control for architectural review and explicit developer completion. **STOP.** Do not implement new code, merge or push `main`, or start dependent/system-test tasks.

## Completion Report

### Status

Not Started — portable publication definition, no execution claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

A verified TEST target and eligible release actor will be available when the developer invokes this task.

### Unresolved Issues

None established.

### Architectural Concerns

Return missing release or publication capability to `moda_architect` without adding implementation behaviour to this release-only task.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no TEST publication executed.

### Reviewed Files

Task definition and attached 29 October 2026 workspace snapshot.

### Validation Reviewed

No publication commands executed.

### Architecture Conformance

Pending authorised publication and review.

### Follow-up

After accepted review, developer completion explicitly marks the release gate `complete` and unlocks its dependants.
