---
id: ARCH-057-SHOPIFY-012
architecture_id: ARCH-057
title: Enforce domain runtime names and canonical development billing identities
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-057-SHOPIFY-011
enables:
- ARCH-057-SYSTEM-TEST-001
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-057-SHOPIFY-012: Enforce domain runtime names and canonical development billing identities

## Architecture

Architecture ID: `ARCH-057`. Document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`. Coordinator: `moda_architect`.

Mandatory contract: `docs/architecture/ARCH-057/task-contract.md`. **Defined but not materialised.** Definition revision 2 records the user's explicit development-only/no-legacy-preservation decision of 4 November 2026.

## Objective

Remove architecture/task labels from Shopify production code, including all three billing hash namespaces, and establish one descriptive canonical identity format for development and launch.

## Context

The user confirmed that Moda Interact has not gone live, is still in development, and does not require preservation of the existing architecture-derived billing identities. This supersedes revision 1's three-literal compatibility exception. The selected change replaces the literals directly; old digest values, development operation records and historical replay compatibility are not acceptance requirements.

Deterministic identity and duplicate protection still apply to operations created under the new canonical names. Tests use fresh synthetic records. No old-format lookup, alias, dual-write, backfill, compatibility flag or separate identity-migration task is required.

## Scope

Paths relative to `moda-interact`.

### Existing files to modify

| Path | Exact change |
|---|---|
| `app/services/webhooks/webhook-normalization-utils.ts` | Replace task-ID comment with its normalization responsibility |
| `app/services/platform-configuration/contracts.server.ts` | Replace architecture-ID comment with server-only configuration ownership/security rule |
| `app/services/platform-configuration/seal.server.ts` | Replace ADMIN-002 comment with the actual AAD field/ordering contract; keep that unrelated encryption contract unchanged |
| `app/services/recoveries/recovery-follow-up-catalogue.server.ts` | Replace ADMIN-003 comment with SOURCE_SAVED draft provenance |
| `app/services/platform-configuration/composition.server.ts` | Replace SHOPIFY-002 comment with service composition description |
| `app/services/merchant-knowledge/r2-config.server.ts` | Replace two SHOPIFY-001 references with sealed operation-scoped configuration semantics |
| `app/services/recoveries/recovery-follow-up-sender.server.ts` | Replace architecture reference with configuration/AAD ownership description |
| `app/services/recoveries/recovery-human-commands.server.ts` | State actual Shop→Conversation→command/attempt ordering without DATABASE-001 label |
| `app/services/billing/shopify-billing-operation.service.ts` | Replace exactly the three hash namespace literals using the fixed map below; retain current input validation, field order, framing, algorithms and operation behaviour |
| `tests/unit/services/billing/shopify-billing-operation.service.test.ts` | Update any affected expected keys/fingerprints and prove fresh canonical operation replay through the actual service |
| `tests/integration/billing-activation.postgres.integration.test.ts` | Prerequisite-created suite: use fresh canonical fixtures and assert initial-operation replay still creates one operation/grant |
| `tests/integration/recovery-credit-purchases.postgres.integration.test.ts` | Prerequisite-created suite: use fresh canonical fixtures and assert purchase replay and fingerprint-conflict semantics |
| `package.json` | Add the naming and identity commands below |

Audit final `app/**` source, actual production configuration, entry files and deployment scripts for architecture-labelled runtime filenames, symbols, events, environment/queue/route names and comments. Earlier tasks already require domain names. Return any undeclared predecessor naming defect for its owning correction; do not create a permanent allowlist.

### New files

- `scripts/check-runtime-names.mjs` — deterministic source naming gate, with zero runtime architecture/task-label exceptions.
- `tests/unit/billing-operation-identity-vectors.test.ts` — fixed request-key/fingerprint vectors for the new canonical values, using actual public functions/service entrypoints.
- `docs/runtime-naming.md` — final naming inventory, exact canonical namespace map, development baseline decision and validation evidence.

Each new test/source file remains below 300 lines. Existing prerequisite suites need focused fixture/assertion changes only.

## Out of Scope

No schema/migration/history renaming, task renumbering, unrelated public DTO/API/environment/queue transition or change to pricing/accounting/authorization. No historical-key migration, rekeying/backfill of old records, legacy reader, dual-format writer, alternate version, compatibility feature flag or reset framework. This task does not modify API/Background/Shared or rename ARCH-056 work. Test/document architecture traceability remains allowed.

## Requirements

### R1 — replace the three literals directly

Use this exact canonical map in `shopify-billing-operation.service.ts`:

| Current literal to remove | Sole canonical replacement |
|---|---|
| `arch027-shopify-operation-key-v1` | `shopify-billing-operation-key-v1` |
| `arch027-recurring-v1` | `shopify-billing-recurring-v1` |
| `arch027-topup-v1` | `shopify-billing-topup-v1` |

Replace the actual complete literals in place. Keep UTF-8 encoding, newline framing, SHA-256, field ordering and input/control-character validation. Keep the ordinary `shopify:<kind>:<digest>` request-key format. The already descriptive one-time charge key `shopify:one-time-charge:<purchaseId>` stays as it is; its fingerprint uses the new top-up namespace. Do not expose the private request-key builder merely for testing.

The resulting recurring request digests and recurring/top-up fingerprints intentionally differ from revision 1's baseline. This change is authorised by the user's development-only decision. There is one canonical implementation; do not retain the old strings in runtime aliases, fallback branches, encoded fragments, hidden constants or compatibility lookup paths.

### R2 — use a fresh development baseline

Existing records created with the old namespaces are disposable development fixtures and need not be retained, converted or accepted by the new implementation. Record that fact in `docs/runtime-naming.md`. Required validation starts with fresh task-owned fixture databases, so it cannot accidentally pass by reading an old operation. Development environments can discard/reseed old test billing state through their existing reset/seed workflow; this task does not add automated deletion to application startup or a new data-reset tool.

Do not create an upgrade/backward-compatibility acceptance case, a migration script or a separate task to preserve previous digests. A failing old fixed expectation is updated to the new independently derived expected value. This does not remove normal same-format idempotency, conflict detection, tenant ownership or atomic accounting requirements for newly created operations.

### R3 — prove new-format identity and replay

1. Fixed vectors use the actual enum values `SUBSCRIPTION_CREATE`, `PLAN_SWITCH`, `CANCEL` and `ONE_TIME_CHARGE`. Cover the real exported recurring/top-up fingerprint builders and request keys observed through `ShopifyBillingOperationService` methods.
2. Derive expected hexadecimal values independently from the selected literal, fixed input fields, exact newline framing and UTF-8 bytes, then commit those expected values as constants in the tests. Do not compute the expected value by invoking the implementation under test, and do not freeze the old digests.
3. Include non-ASCII identifiers, invalid control characters, distinct Shop/plan/quote/usage inputs and existing provider-reference inclusion/exclusion semantics. This task changes the namespace only; it does not alter which business fields participate in identity.
4. On a fresh fixture, create an operation using the new names and replay the same request. It returns the same operation/receipt and creates no second operation, credit grant or purchase. A genuinely conflicting fingerprint still produces the existing bounded conflict behaviour. Verify tenant and transaction rollback invariants.
5. Rerun the accepted initial-activation and purchase PostgreSQL suites on canonical migrated PG17 + pgvector. Use real persistence for replay/concurrency cases and the existing controlled provider boundaries. Update only assertions/fixtures needed for the new namespace; preserve their substantive outcome checks.

### R4 — domain naming with no runtime exceptions

1. Runtime filenames, identifiers, classes, exports, events, environment variables and queue/route names describe domain/function. Remove the eight files' explanatory task references while retaining their responsibility/security/ordering explanation.
2. The naming gate scans filename and content in `app/**` plus actual production entry/configuration/deployment files. Recognize forms such as `ARCH-123`, `arch123`, `ARCH_123` and task fragments such as `SHOPIFY-001`, `DATABASE-001` or `ADMIN-002` used in runtime names/comments.
3. Tests, fixtures, generated output, database migration history, documentation and validation-only tooling (including the check itself) are outside the runtime scan. These exclusions are by role/path, not an allowlist for billing literals.
4. Every architecture/task-labelled match in the selected runtime scope fails the check. The three old billing strings have no exception. Output identifies file/line/classification without dumping secret-bearing source lines. Do not follow symlinks outside the repository, inspect secret files or scan node_modules.
5. Prove the gate detects a temporary old-literal/naming fixture in its scanned scope and excludes legitimate task-labelled test/document fixtures, using disposable temporary fixtures that are removed afterward. Do not conceal matches through concatenation, spelling changes or encoding.

## Work Items

- [ ] Record the development-only/no-legacy-preservation decision and exact replacement map.
- [ ] Replace all three runtime hash namespaces and rewrite the specified explanatory comments.
- [ ] Add the zero-exception naming gate and new canonical fixed vectors.
- [ ] Update affected expectations and verify fresh same-format replay/conflict/rollback behaviour.
- [ ] Run focused unit and migrated PostgreSQL regressions and record the final scan inventory.

## Interfaces / Contracts

Package additions:

```json
{
  "lint:runtime-names": "node scripts/check-runtime-names.mjs",
  "test:billing-identity": "vitest run tests/unit/billing-operation-identity-vectors.test.ts tests/unit/services/billing/shopify-billing-operation.service.test.ts"
}
```

Exported production signatures and public operation kinds stay unchanged. The selected three namespace substitutions are the complete intended identity-format change. There is no old-format compatibility interface and no Shared package/schema requirement.

## Dependencies

- ARCH-057-SHOPIFY-011

This transitively follows all ten functional touchpoint tasks. Their existing identity-preservation instructions apply during their own scope; this final task explicitly owns the authorised namespace replacement and its resulting expectations.

## Enables

- ARCH-057-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] All three old literals are absent from Shopify runtime code; each new canonical literal is used at its specified builder.
- [ ] Final runtime names/comments contain no architecture/task labels; the naming check reports no allowed legacy matches.
- [ ] Fixed request-key/fingerprint vectors reflect the new namespaces, actual operation kinds and unchanged input/framing rules.
- [ ] Fresh same-format replay returns one operation/receipt and creates no extra grant/purchase; conflicts, tenant checks and rollback remain correct.
- [ ] No legacy fallback, dual-read/write, digest alias, backfill, migration or compatibility flag was added.
- [ ] Tests/documents retain valid architecture traceability; unrelated encryption, queue, pricing and public DTO contracts are unchanged.
- [ ] Required real PostgreSQL cases execute; historical-development-data preservation is not used as a blocker or acceptance requirement.

## Validation

- [ ] `npm run lint:runtime-names`
- [ ] `npm run test:billing-identity`
- [ ] `MODA_DISPOSABLE_INTEGRATION=1 npm test -- tests/integration/billing-activation.postgres.integration.test.ts tests/integration/recovery-credit-purchases.postgres.integration.test.ts`
- [ ] `npm run typecheck`
- [ ] Focused ESLint on modified/new files and `git diff --check`
- [ ] Record the zero-exception final runtime scan, temporary gate-rejection checks, new fixed vectors, fresh replay results and task-owned database cleanup

## Stop Condition

Return review after the naming scan, canonical vectors and fresh replay regressions pass. A changed digest is expected and authorised; do not stop to preserve old development rows or propose a migration for them. Return an architect amendment only for a required unrelated cross-repository/wire/schema change, an undeclared new runtime touchpoint, or a failed required functional validation. Do not start the terminal task or operate on live provider accounts.

## Implementation Notes

The user explicitly prioritised one simple canonical development implementation over historical compatibility. Remove the obsolete architecture-derived values completely from runtime code. Keep future operations deterministic and test their own replay behaviour from fresh state. This task defines the launch baseline; it does not preserve revision 1's exception.

## Completion Report

### Status

Not Started. Defined but not materialised; no execution claim or worktree is asserted.

### Files Changed

None. Definition only.

### Work Completed

None.

### Validation Results

Not run. Record exact commands, fixture/case results, source/build/installed-package provenance, original diagnostic assertions, SQL/provider counts where required, and task-owned resource cleanup.

### Deviations

None.

### Assumptions

The launcher will verify actual dependency status and the accepted integrated source before claiming this task.

### Unresolved Issues

Implementation and required validation are outstanding.

### Architectural Concerns

Return changed ownership, persisted identity, schema, queue, transaction or external contract requirements to the architect.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition only; no implementation accepted.

### Reviewed Files

Definition and current snapshot touchpoints only.

### Validation Reviewed

Definition checks only. Implementation evidence is outstanding.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

Return the completed task for architect review; do not start enabled tasks.
