---
id: ARCH-052-SHARED-002
architecture_id: ARCH-052
title: Define cross-service checkout summary and product-header binding contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-052-SHARED-003
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHARED-002: Define cross-service checkout summary and product-header binding contract

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Own the new semantic WhatsApp initial-outreach binding names and product-media role once, as the shared contract consumed by Admin and Background.

## Context

ARCH-047 Admin and Background currently hold parallel semantic-variable allowlists. `shop.categoryName` already exists. ARCH-049 defines three ShopBrand IMAGE header roles with immutable compiled hashes; checkout product media is a fourth distinct role, not a ShopBrand role.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Add a browser-safe `@modainteract/moda-interact-shared/recovery-template-bindings` published subpath with the `checkout.itemsSummary` text variable and `CHECKOUT_PRODUCT` IMAGE header role, plus accepted existing recovery-body variables and ARCH-049 image-header roles.
- Define typed body-versus-header eligibility, purpose/offer-kind constraints, length/sanitisation limits, locale-neutral description output and exact versioned `parameterBindingsSnapshot.headerMediaRole` semantics.
- Keep Admin English AST compilation and its immutable digest algorithm Admin-owned. Shared defines keys/roles/validation and cross-repository fingerprint fixtures, not a second AST compiler.
- Add fixtures for all six INITIAL/FOLLOW_UP × offer-kind purposes; missing category, no item title, no available media, and valid/invalid product header roles.

## Out of Scope

- No changes to category source/translation, media R2 processing, template compilation, Meta API or Background send implementation.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Product images are optional and must never be substituted into a ShopBrand role; IMAGE header role is frozen in the immutable provider-approved projection.
- No arbitrary text/URL injection into Meta template, no dynamic footer and no new unapproved variable names.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Define shared schemas/exports and fixtures.
- [ ] Document compatible Admin/Background compiler/runtime semantic constraints.
- [ ] Run contract fixtures and cross-runtime-safe import tests.

## Interfaces / Contracts

- Export `RecoveryTemplateSemanticVariableSchema`, `RecoveryTemplateHeaderMediaRoleSchema` and representative frozen-binding vectors from a new Shared subpath.
- Text key: `checkout.itemsSummary` (body only); IMAGE role: `CHECKOUT_PRODUCT`; existing `shop.categoryName` remains store category, not product category.

## Dependencies

None.

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [ ] Admin and Background can validate exactly the same key/role fixtures.
- [ ] Existing ARCH-047/049 frozen bindings remain valid; unknown dynamic keys and ambiguous image roles fail closed.

## Validation

- [ ] Shared unit/contract tests, package build/typecheck, browser-safe entrypoint test.
- [ ] `git diff --check` and API export shape checks.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-shared/src/recovery-template-bindings.ts (new)`
- `moda-interact-shared/src/recovery-template-bindings.test.ts (new)`
- `moda-interact-shared/package.json`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

## Completion Report

### Status

Not Started — portable definition, no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Execution will verify its current workspace, source state, dependency versions and test harness.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.


## Architect Review

### Review Status

Pending.

### Review Notes

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
