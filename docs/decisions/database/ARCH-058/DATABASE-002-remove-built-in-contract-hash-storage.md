---
id: ARCH-058-DATABASE-002
architecture_id: ARCH-058
title: Migrate persisted built-in grants to no-hash 2.0.0 identity
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 36
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-058-DATABASE-001
  - ARCH-058-SHARED-005
enables:
  - ARCH-058-MCP-002
  - ARCH-058-SYSTEM-TEST-001
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-058-DATABASE-002: Migrate persisted built-in grants to no-hash 2.0.0 identity

## Architecture

Architecture ID: `ARCH-058`.

Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`.

Contract owners: `ARCH-058-SHARED-003` (identity shape) and `ARCH-058-SHARED-005` (final built-in definition version `2.0.0`).

Coordinator: `moda_architect`.

DATABASE-001 remains accepted historical implementation. Do not edit its applied migration. This task supplies the required forward correction after Shared changes the canonical built-in grant identity to `kind/toolName/definitionVersion` and bumps both discount built-ins to final `definitionVersion: "2.0.0"`.

## Objective

Add one forward PostgreSQL migration that converts any existing ARCH-058 built-in grant entries from legacy four-field hashed `1.0.0` objects to the final strict three-field no-hash `2.0.0` name/version shape and updates the installed grant validator accordingly, while preserving every published-tool grant, grant owner/release invariant and grant immutability rule.

## Context

`20261104120000_reference_taxonomy_and_core_product_discovery` replaced `commerce.arch020_grant_tools(jsonb)` so a built-in entry required exactly `kind`, `toolName`, `definitionVersion`, `contractHash`. SHARED-003 removes that field from the canonical contract, and SHARED-005 changes the accepted discount-offer timestamp semantics and therefore bumps both built-ins to `2.0.0`. Because `CommerceConversationGrant.grantedTools` is JSONB and protected by an immutable-update trigger, the transition requires an explicit forward migration; editing the accepted migration is prohibited.

ARCH-058 is pre-production, so no dual old/new shape is supported after this migration. Existing development rows are deterministically rewritten in place during migration.

## Scope

Create exactly one new migration directory:

```text
prisma/migrations/20261104162500_arch058_remove_builtin_contract_hash/migration.sql
```

Update only the existing ARCH-058 Database validation fixtures/scripts necessary to validate the corrected final state:

- `scripts/fixtures/reference-taxonomy-fixtures.mjs`
- `scripts/validate-reference-taxonomy-schema.mjs`
- `scripts/test-reference-taxonomy-postgres.mjs`

`package.json` may be changed only if an additional command is strictly necessary; prefer the existing `test:reference-taxonomy-schema`, `test:reference-taxonomy:postgres:fresh` and `test:reference-taxonomy:postgres:upgrade` scripts.

## Out of Scope

- Editing `20261104120000_reference_taxonomy_and_core_product_discovery` or any earlier migration.
- Prisma model changes: `grantedTools` remains JSONB and taxonomy models are unchanged.
- Changing published-tool grant shape/provenance, release/capability rows or feature policy.
- Deleting grants/conversations merely to avoid the conversion.
- Supporting both hashed and non-hashed built-in entries after the migration.
- Shared/MCP/Commerce/Background implementation.

## Requirements

The migration must be transactional and use the existing database objects rather than introduce parallel validators.

1. Begin a transaction and execute `LOCK TABLE commerce."CommerceConversationGrant" IN ACCESS EXCLUSIVE MODE` before changing the helper or trigger. This serializes inserts/updates and the migration-owned rewrite for the short pre-production transition.
2. Temporarily drop only the existing `arch020_grant_immutable` **BEFORE UPDATE** trigger required to permit the migration-owned row rewrite. Do not drop or alter the underlying `commerce.arch020_immutable()` function.
3. Keep the installed `arch020_grant_bounds` CHECK constraint in place. It already calls `commerce.arch020_grant_tools()` by name; replacing that function changes the validation used for the transformed rows without a constraint drop/recreate or table-wide constraint rewrite.
4. `CREATE OR REPLACE FUNCTION commerce.arch020_grant_tools(v jsonb)` with the same ownership/security/search-path/bounds behavior except that a built-in object must have **exactly**:

   ```text
   kind
   toolName
   definitionVersion
   ```

   `kind` must equal `BUILT_IN`, name must be one of the two canonical discount names, and version must equal `2.0.0`. Any `contractHash`, extra field, fabricated published identity, unknown name/version, duplicate name, cross-branch name collision, >32 entries or oversized JSON remains invalid. Published entries retain their existing exact five-field shape and provenance checks.
5. Rewrite existing `CommerceConversationGrant.grantedTools` rows in place, preserving JSON array order and every non-built-in entry semantically unchanged, by removing `contractHash` from objects whose `kind == "BUILT_IN"` **and** replacing their canonical legacy `definitionVersion: "1.0.0"` with `"2.0.0"`. Abort rather than rewrite an unknown built-in name/version. Use `jsonb_array_elements(... ) WITH ORDINALITY` and an ordered `jsonb_agg` or an equivalent deterministic transformation. Do not change selected capability keys, release IDs, runner versions or timestamps.
6. After the rewrite, assert that no built-in entry contains `contractHash` and every row passes the corrected `commerce.arch020_grant_tools` function. Abort the migration if the postcondition fails.
7. Recreate `arch020_grant_immutable` with its existing semantics exactly: `BEFORE UPDATE ON commerce."CommerceConversationGrant" FOR EACH ROW EXECUTE FUNCTION commerce.arch020_immutable()`. Do not add DELETE immutability that does not exist in the accepted baseline.
8. `commerce.arch021_conversation_grant_guard()` continues to call `commerce.arch020_grant_tools`; do not replace it unless the implementation proves the body itself must change. Its release-union, shop/recovery/inbound and published-tool checks remain unchanged.
9. Preserve installed function owners/ACLs. `CREATE OR REPLACE` keeps the helper identity/privileges stable.
10. Do not change the Prisma schema because no relational column/model changes.

## Work Items

- [x] Add the single forward migration with the exact transition above.
- [x] Update structural fixture expectations to the strict three-field built-in shape.
- [x] Add an upgrade fixture that creates a valid legacy hashed `1.0.0` built-in grant after DATABASE-001 but before DATABASE-002, then proves the migration removes the hash and changes only the built-in definition version to `2.0.0`.
- [x] Update fresh final-state fixtures to require `2.0.0`, reject legacy `1.0.0`, and reject `contractHash` as an extra built-in key.
- [x] Preserve published-grant and all existing owner/release/immutability failure fixtures.
- [x] Run schema, fresh PostgreSQL and upgrade PostgreSQL validation.

## Interfaces / Contracts

Final persisted built-in grant entry:

```json
{
  "kind": "BUILT_IN",
  "toolName": "commerce_get_discount_options",
  "definitionVersion": "2.0.0"
}
```

or the corresponding `commerce_get_discount_details` name.

No hash/fingerprint field remains in persisted built-in identity.

## Dependencies

- `ARCH-058-DATABASE-001`
- `ARCH-058-SHARED-005`

## Enables

- `ARCH-058-MCP-002`
- `ARCH-058-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] A fresh migration chain ends with the corrected three-field built-in validator.
- [x] An upgrade from the accepted DATABASE-001 state converts existing valid hashed `1.0.0` built-in entries to corrected no-hash `2.0.0` three-field objects without deleting the grant.
- [x] Published grant entries and their exact release-derived union are unchanged by conversion.
- [x] `contractHash` is rejected as an extra built-in key after migration, and legacy built-in `definitionVersion: "1.0.0"` is rejected.
- [x] Unknown kind/name/version, fabricated published keys, duplicates/collisions, oversized/count-overflow and existing shop/recovery/inbound/release failures remain rejected.
- [x] The existing grant **update** immutability trigger is restored exactly after migration; no new DELETE trigger is introduced.
- [x] An injected failure inside a disposable copy of the migration transaction rolls back the function replacement, row rewrite and trigger drop, leaving the pre-migration state intact.
- [x] Re-running the normal migration deploy reports no pending application and performs no second rewrite.
- [x] No earlier migration or Prisma model was edited.

## Validation

Use the existing disposable PostgreSQL 17/pgvector harness and the repository-declared scripts:

```bash
npm run validate
npm run prisma:generate
npm run test:reference-taxonomy-schema
npm run test:reference-taxonomy:postgres:fresh
npm run test:reference-taxonomy:postgres:upgrade
git diff --check
```

The upgrade test must explicitly capture a grant before DATABASE-002 and compare it afterwards, proving that the only built-in changes are removal of `contractHash` and `definitionVersion: "1.0.0" -> "2.0.0"`. The fresh and upgrade paths must exercise the real `CommerceConversationGrant` CHECK/insert guard, not only the helper function.

## Stop Condition

After all Work Items, Acceptance Criteria and Validation pass, set status to `review`, complete the report, return to `moda_architect` and STOP. Do not modify consumer submodule gitlinks, Shared source or MCP code.

## Implementation Notes

Do not use `db push`, migration reset/squash/resolve, manual row deletion or trigger disablement outside this migration. The temporary trigger removal, function replacement and row transformation must live inside the new transaction so failure rolls back the entire transition.

## Completion Report

### Status

Ready for Review

### Files Changed

- `prisma/migrations/20261104162500_arch058_remove_builtin_contract_hash/migration.sql`
- `scripts/fixtures/reference-taxonomy-fixtures.mjs`
- `scripts/validate-reference-taxonomy-schema.mjs`
- `scripts/test-reference-taxonomy-postgres.mjs`

### Work Completed

- Added the single transactional forward migration. It takes the required ACCESS EXCLUSIVE lock, rejects unrecognized legacy built-in shapes before changing guards, drops only the update immutability trigger, replaces the existing helper with the exact three-field `2.0.0` validator, rewrites built-ins in array order, asserts postconditions, and restores the existing BEFORE UPDATE trigger semantics. The existing CHECK, guard trigger/function, function ownership/ACLs, and Prisma models remain unchanged.
- Changed final-state fixtures to strict no-hash built-ins and added a legacy hashed `1.0.0` upgrade grant. The PostgreSQL upgrade test compares the complete saved grant, proving only built-in `contractHash` and `definitionVersion` changed while the published grant and all other row values remained the same.
- Added injected-transaction-failure verification for the helper, row, trigger, CHECK, and migration-history rollback. Fresh and upgrade paths both exercise actual grant table CHECK/insert behavior and verify repeat deploy is a no-op.

### Validation Results

- `npm run validate` — passed; Prisma schema valid.
- `npm run prisma:generate` — passed; Prisma Client 6.19.3 generated.
- `npm run test:reference-taxonomy-schema` — passed.
- `npm run test:reference-taxonomy:postgres:fresh` — passed on disposable `pgvector/pgvector:pg17` / PostgreSQL 17.11, including strict built-in rejection, existing grant failure cases, guard/immutability checks, and second-deploy no-op.
- `npm run test:reference-taxonomy:postgres:upgrade` — passed on disposable `pgvector/pgvector:pg17` / PostgreSQL 17.11, including legacy grant conversion, published-entry preservation, injected failure rollback, existing grant failure cases, and second-deploy no-op.
- `git diff --check` — passed.
- Implementation commit `93225ee` was pushed to `origin/task/ARCH-058-DATABASE-002`.
- Launcher preparation evidence: parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-DATABASE-002` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-DATABASE-002`, both on `task/ARCH-058-DATABASE-002`; prepared bases `dc5da17151c43cb4117e5a14df82373a0d932e08` and `395675f909d604f0bff83ffb3d7d5586f0bdd39b`; claim `bcaa64d77dc01edc5cf05e668116e960216509aa` pushed; no submodules; DATABASE-001 and SHARED-005 dependency gate passed; main incorporated.

### Deviations

- The pre-existing PostgreSQL runner's conflict scenarios specifically exercised the predecessor product-discovery migration. The runner now targets DATABASE-002, so those unrelated predecessor-migration probes were removed from this invocation; the required built-in/published grant shape, release, owner, recovery, inbound-version, bounds, and immutability failure cases remain enabled and passed.

### Assumptions

DATABASE-001 remains the installed predecessor and SHARED-005 has been accepted before this task starts.

### Unresolved Issues

None for the assigned migration scope.

### Architectural Concerns

None. The predecessor product-discovery conflict probes noted under Deviations are separate from this migration's grant validation and were not claimed as passing.

## Architect Review

**Accepted — Attempt 1, 2026-11-04.** Reviewed implementation `93225ee`. No blocking findings identified. Task marked Complete under automatic completion mode; Attempt 1 preserved and claim cleared.

Reviewed the forward migration and all fixture/runner/structural-validator changes. The migration locks the grant table before changing guards, preserves the existing CHECK and insert guard, validates legacy identities, transforms built-ins in array order to strict three-field 2.0.0 identities, asserts postconditions and restores the existing update-only immutability trigger inside the same transaction. Published grants, function identity/security/ACLs, prior migrations and Prisma models are preserved.

Independent validation: `npm run test:reference-taxonomy-schema` passed; implementation comparison whitespace check passed. Reviewed reported fresh and upgrade PostgreSQL success and test assertions for complete-row conversion equality, published-entry preservation, injected rollback, strict rejection cases and repeat-deploy no-op. Docker, Prisma validation and generation were not independently rerun by this review. Local structural log: `/tmp/arch058-database002-review-schema.log`. Removed predecessor-specific conflict probes are disclosed in the report and are not counted as executed coverage for this migration.

Reviewed prepared dedicated worktree evidence: parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-DATABASE-002`, implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-DATABASE-002`, matching task branches. No implementation, schema, gitlink or main branch is modified by this review.

SHARED-006 acceptance and its immutable Shared 5.0.0 receipt are reconciled from parent commit `fcda684c6`. MCP-001, DATABASE-002 and SHARED-006 are now Complete; MCP-002 is Ready with its existing Attempt 1 preserved and no claim. Its WIP remains intact; normal launcher preparation claims the next attempt. SYSTEM-TEST-001 and other downstream work retain remaining prerequisites and are not executed here. Integrated compatibility remains to be validated, including the known optional Commerce projection issue.

The developer explicitly authorized acceptance, downstream reconciliation, commit and push on 2026-11-04. ARCH-058 is not marked implemented.

## Architect Dependency Reconciliation (2026-11-04)

SHARED-005 Attempt 1 is architect-accepted and Complete at `070975e`. All explicit prerequisites are Complete. Promoted to Ready with executor/claim empty and Attempt 0 preserved; no execution is started. The known optional Commerce projection issue recorded in SHARED-005 remains a consumer-validation coordination item, not a passing integration claim.
