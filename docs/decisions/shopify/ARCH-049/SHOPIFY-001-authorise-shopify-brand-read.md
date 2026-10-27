---
id: ARCH-049-SHOPIFY-001
architecture_id: ARCH-049
title: Authorise Shopify read_brand scope without implementing synchronisation
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: ["ARCH-049-BACKGROUND-003"]
created: 2026-10-25
updated: 2026-10-27
---

# Authorise Shopify read_brand scope without implementing synchronisation

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`.

## Execution Ownership Amendment

On 2026-10-27, `/moda_developer_create ARCH-049-SHOPIFY-001` was invoked as an explicit developer takeover. Execution and completion authority are now `developer`; logical ownership remains `assigned_agent: moda_app` and `repository: moda-interact`.

## Objective

Add and validate the Shopify Admin brand-read permission required by the Background-owned Shopify ShopBrand synchroniser. No brand fetch or ShopBrand persistence belongs in this task.

## Context

The uploaded Shopify app scope string contains `write_products,write_metaobjects,write_metaobject_definitions` but not `read_brand`. Shopify Admin GraphQL `shop.brand`/BrandingBrand requires `read_brand`. The earlier full Shopify ingestion task is superseded in scope by Background-003.

## Scope

- Add `read_brand` to the app `access_scopes.scopes` in the canonical `moda-interact/shopify.app.toml` while preserving every existing scope.
- Verify any applicable production app configuration variant and existing `app/scopes_update`/reauthorisation flow; document how already installed shops regain the grant.
- Add focused config tests/evidence proving the declared scope is present and brand read is unavailable without it.

## Out of Scope

- Shopify provider brand GraphQL queries and polling, modifications to Background, ShopBrand database writes, brand-image processing, changing unrelated Shopify scopes or webhook contracts.

## Requirements

### R1. Exact scope change

Existing scope list in the supplied snapshot is:

```toml
scopes = "write_products,write_metaobjects,write_metaobject_definitions"
```

Add `read_brand` exactly once, retain all existing scopes and the current `app/scopes_update` registration. Confirm the deployed configuration is the one being edited; do not assume that a development-only TOML file controls a different production app.

### R2. Permission/reauthorisation

A live already-installed merchant may need Shopify's permitted authorisation refresh after scope changes. Provide the normal Shopify re-authorisation path and test missing-scope reporting. Do not silently attempt brand reads with a token that lacks scope.

### R3. Stop boundary

This task is **configuration/authentication only**. `BACKGROUND-003` owns all brand API retrieval and ShopBrand source persistence.

## Work Items

- [ ] Update only relevant Shopify app config/auth tests.
- [ ] Document the re-authorisation procedure for existing installations.
- [ ] Record applicable deployment config and scope evidence.

## Interfaces / Contracts

Produces the `read_brand` permission for the existing authenticated Shopify GraphQL client. It does not create any new HTTP/queue contract or write brand records.

## Dependencies

None.

## Enables

- ARCH-049-BACKGROUND-003

## Acceptance Criteria

- [ ] `read_brand` is present without dropping prior scopes; existing app configuration remains valid.
- [ ] Installed-shop permission refresh and missing-scope behaviour are explicitly documented/tested.
- [ ] No Shopify brand sync implementation added.

## Validation

- [ ] Config parse/validation and focused scope test using existing scripts.
- [ ] Inspect installed app auth/scope-update tests; run affected tests.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

No additional assumptions are authorised.

## Completion Report

### Status

Not Started — defined but not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the explicit architecture/task contract.

### Unresolved Issues

None; live environment availability is a validation prerequisite and must be reported if missing.

### Architectural Concerns

None reported.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.
