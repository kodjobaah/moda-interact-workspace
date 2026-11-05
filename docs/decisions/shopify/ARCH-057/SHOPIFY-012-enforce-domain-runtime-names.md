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
status: complete
priority: 90
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-057-SHOPIFY-011
enables:
- ARCH-057-SYSTEM-TEST-001
created: 2026-11-04
updated: 2026-11-05
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

- [x] Record the development-only/no-legacy-preservation decision and exact replacement map.
- [x] Replace all three runtime hash namespaces and rewrite the specified explanatory comments.
- [x] Add the zero-exception naming gate and new canonical fixed vectors.
- [x] Update affected expectations and verify fresh same-format replay/conflict/rollback behaviour.
- [x] Run focused unit and migrated PostgreSQL regressions and record the final scan inventory.

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

- [x] All three old literals are absent from Shopify runtime code; each new canonical literal is used at its specified builder.
- [x] Final runtime names/comments contain no architecture/task labels; the naming check reports no allowed legacy matches.
- [x] Fixed request-key/fingerprint vectors reflect the new namespaces, actual operation kinds and unchanged input/framing rules.
- [x] Fresh same-format replay returns one operation/receipt and creates no extra grant/purchase; conflicts, tenant checks and rollback remain correct.
- [x] No legacy fallback, dual-read/write, digest alias, backfill, migration or compatibility flag was added.
- [x] Tests/documents retain valid architecture traceability; unrelated encryption, queue, pricing and public DTO contracts are unchanged.
- [x] Required real PostgreSQL cases execute; historical-development-data preservation is not used as a blocker or acceptance requirement.

## Validation

- [x] `npm run lint:runtime-names`
- [x] `npm run test:billing-identity`
- [x] `MODA_DISPOSABLE_INTEGRATION=1 npm test -- tests/integration/billing-activation.postgres.integration.test.ts tests/integration/recovery-credit-purchases.postgres.integration.test.ts`
- [x] `npm run typecheck`
- [x] Focused ESLint on modified/new files and `git diff --check`
- [x] Record the zero-exception final runtime scan, temporary gate-rejection checks, new fixed vectors, fresh replay results and task-owned database cleanup

## Stop Condition

Return review after the naming scan, canonical vectors and fresh replay regressions pass. A changed digest is expected and authorised; do not stop to preserve old development rows or propose a migration for them. Return an architect amendment only for a required unrelated cross-repository/wire/schema change, an undeclared new runtime touchpoint, or a failed required functional validation. Do not start the terminal task or operate on live provider accounts.

## Implementation Notes

The user explicitly prioritised one simple canonical development implementation over historical compatibility. Remove the obsolete architecture-derived values completely from runtime code. Keep future operations deterministic and test their own replay behaviour from fresh state. This task defines the launch baseline; it does not preserve revision 1's exception.

## Completion Report

### Status

Ready for Review — Attempt 1, codex, 2026-11-05. Implementation committed and pushed as `905e8a79ec16f11901375e3fc14931b3f45cbbcd` on `task/ARCH-057-SHOPIFY-012`. No architect acceptance or terminal-task promotion is asserted.

### Prepared Execution / Provenance

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-057-SHOPIFY-012`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-057-SHOPIFY-012`. Both branches `task/ARCH-057-SHOPIFY-012`; both newly created by the launcher. No shared/default checkout or another task worktree was switched or edited.
- Launcher verified SHOPIFY-011 Complete. Both remote-task fast-forwards not needed; both origin/main integrations already current. Parent start `69ff2a6e3e1e6f49e97f32c1f5cfe085470d475a`; implementation start `cf0e8dfd314c92183b07a935dff68c933f445daf`.
- Durable claim `0e562fb1417041178296fd0ef09d34ccc42222f9`, Attempt1, executor codex, `2026-11-05T10:22:20Z`. Parent end is the report-submission commit containing this report; no self-referential SHA is invented. Implementation end `905e8a79ec16f11901375e3fc14931b3f45cbbcd`.
- Recursive submodule sync/update passed in launcher; recorded/working nested Database `bd2d09066a8eb178a56f48fbbf88df637c411059`, unchanged.
- `npm ci` passed; generated Prisma from the pinned Database schema. Actual installation: Shared3.1.0, Prisma client6.19.3, Vitest4.1.11, TypeScript5.9.3. Prescribed workspace bootstrap supplied Node24.19.0/npm11.17.0. No dependency/schema changes.

### Files Changed

16 implementation files, all declared scope:

- `app/services/billing/shopify-billing-operation.service.ts`: exactly the three authorized namespace substitutions.
- Eight specified comment files: webhook normalization utilities; configuration contracts/seal/composition; merchant knowledge R2 configuration; recovery follow-up catalogue/sender and human commands. Responsibility/security/AAD/ordering explanation retained.
- `scripts/check-runtime-names.mjs` (new), `tests/unit/billing-operation-identity-vectors.test.ts` (new), `docs/runtime-naming.md` (new).
- `tests/unit/services/billing/shopify-billing-operation.service.test.ts`; both specified activation/purchase PostgreSQL suites; `package.json`.

### Work Completed

- Replaced `arch027-shopify-operation-key-v1`, `arch027-recurring-v1`, `arch027-topup-v1` directly with the exact canonical names. Each canonical namespace occurs exactly once at its designated builder. The old values are absent from runtime source; no aliases, fallback, encoded strings, compatibility flags, backfill or migration.
- Preserved UTF-8, newline framing, SHA-256, field order and validation; the private key builder remains private. Public enums/signatures, one-time purchase-key format, encryption AAD bytes, queue/pricing/accounting/authorization policy remain unchanged.
- Added a deterministic zero-exception naming gate over241 selected runtime files (234 application source files +7 actual entry/configuration/deployment surfaces) plus production manifest values. Filenames/content and supported architecture/task forms fail with file/line/classification only; no source-line/secret dump. Role/path exclusions preserve test/document traceability, generated/vendor/history/validation artifacts and secret-file boundaries. Symlinks, including parents of literal production-command paths, are not followed. Complete selected-path inventory is in `docs/runtime-naming.md`.
- Added17 new vector/identity cases with independently Python-derived fixed SHA-256 constants, non-ASCII fields and all four real kinds. Service entrypoints expose request keys without exporting the builder. Existing fresh replay case now asserts canonical fixed values. Tests retain field differentiation, cancellation exclusions, provider-reference enrichment/conflict/exclusion and invalid controls.
- Strengthened real PostgreSQL fixtures: repeat initial preparation and concurrent finalization produce one confirmed operation and one25-credit grant; purchase replay creates one receipt/usage/operation and no extra provider observation; changed-quote fingerprint conflict and tenant rejection retain state. Existing lock, cycle-race and rollback assertions preserved.
- Recorded development-only/no-legacy-preservation decision, exact namespace map, ordered field/framing contract, fixed vectors, runtime inventory, gate fixture results, real persistence results and cleanup in the evidence document.

### Validation Results

All required checks passed:

1. `npm run lint:runtime-names` — **241 files + production manifest values,0 violations,0 exceptions**.
2. **16 disposable gate checks passed**: architecture/task spelling forms, all three old literals, filename/config/production-manifest rejection (including actual manifest line), excluded test/document/validation-manifest traceability, external symlink, final clean scope. All fixtures/temporary manifest edits removed/restored.
3. `npm run test:billing-identity` — **41 tests passed,2 files** (17 new +24 existing).
4. `MODA_DISPOSABLE_INTEGRATION=1 npm test -- tests/integration/billing-activation.postgres.integration.test.ts tests/integration/recovery-credit-purchases.postgres.integration.test.ts` — **8 tests passed,2 files**, zero skips in successful run. Two separate fresh task-owned `pgvector/pgvector:pg17` containers, each initialized with canonical `prisma migrate deploy --schema database/prisma/schema.prisma`, real persistence/independent connections/barriers and controlled providers. No db-push/copied schema/mock persistence.
5. `npm run typecheck` — passed.
6. Focused ESLint over all changed/new JS/TS files — passed. Gate lint rerun after its final manifest-line refinement — passed. `git diff --check` — passed. New source/test files remain below300 lines.
7. Shopify toolkit app-pricing reference and official documentation search consulted; required skill-use and once-per-turn feedback commands returned0. No API operation or version changed, so no API schema/code-generation claim.

The first PostgreSQL invocation could not discover Docker from the non-login test process and ran no cases; not counted as a pass. The successful invocation supplied `DOCKER_HOST` from the active Colima context and `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock` only to that process. No host configuration repair/change. Testcontainers stopped both task PostgreSQL containers and its task Ryuk helper; before/after running-container inventories match exactly, preserving three pre-existing containers. No shared Docker pruning or retained task database/volume.

Purchase suite reports364 emitted SQL statements across fixture/assertion/business work; this is not a before/after performance measurement. Synthetic provider call assertions remain in their original cases; no live charge, refund, provider account or merchant data was used. No new server error-handling path was added; accepted error contracts retained.

Local artifacts: `/tmp/arch057-shopify012-{install,prisma,names,unit,postgres,typecheck,lint,gate-lint,shopify-docs}.log`, `/tmp/arch057-shopify012-vectors.json`, `/tmp/arch057-shopify012-gate-fixtures.json`, `/tmp/arch057-shopify012-runtime-inventory.txt`, `/tmp/arch057-shopify012-containers-{before,after}.txt`. Durable map/vectors/inventory/case evidence is committed in `docs/runtime-naming.md`.

### Deviations

None. Changed development hashes are intentional and authorized, not a compatibility failure. No undeclared runtime naming touchpoint required an amendment.

### Assumptions

Fresh task-owned fixture databases establish the canonical launch/development baseline. Old development operation rows are disposable and are neither converted nor accepted through an alternate format. Existing reset/seed workflow remains developer-controlled; no startup deletion is introduced.

### Unresolved Issues

No task-owned implementation/validation blocker. Architect review pending; terminal SYSTEM-TEST-001 remains gated and was not started.

### Architectural Concerns

No cross-repository/schema/wire change, historical identity preservation mechanism, main merge, gitlink, index or downstream task update. The Architect Review below is preserved unchanged.

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

## Architect Dependency Reconciliation — 5 November 2026

SHOPIFY-011 Attempt 2 is architect-accepted and Complete at `aa02676`. Its sole prerequisite is satisfied; promoted to Ready at Attempt 0, executor/claim null. Earlier pending dependency snapshots are historical. Normal launcher preparation is required; no execution is started here.

## Architect Acceptance — Attempt 1, 5 November 2026

**Accepted.** Reviewed implementation `905e8a79ec16f11901375e3fc14931b3f45cbbcd`. No blocking findings identified. Task marked Complete under automatic completion mode; executor/claim cleared and Attempt 1 preserved. Earlier pending review and pre-execution snapshots remain historical.

### Reviewed Source and Conformance

Reviewed the full task diff, zero-exception naming gate, fixed identity vectors, PostgreSQL assertion changes, naming inventory and Completion Report against the development-only/no-legacy-preservation decision. The runtime billing change is exactly the three authorized namespace substitutions. UTF-8/newline framing, SHA-256, field participation/order, input validation and ordinary request-key formats remain unchanged. Public signatures/accounting policy and unrelated encryption AAD are preserved. No old-format reader, alias, dual writer, migration/backfill or startup deletion is added. Naming comments retain domain/security/ordering meaning and the gate avoids secret-source dumps and external symlink traversal. Fresh replay/conflict/tenant/accounting assertions remain substantive.

### Independent Validation and Limits

Executed with the prescribed Node 24.19.0 bootstrap in the dedicated implementation worktree:

- `npm run lint:runtime-names`: passed, 241 selected runtime files plus production manifest values, zero violations/exceptions.
- `npm run test:billing-identity`: **41/41 tests passed**, two files, zero skips.
- Implementation comparison whitespace check passed; no review source edits retained.

Local independent log `/tmp/shopify012-review.log` is not a committed artifact. Reviewed reported **8 PostgreSQL tests across two suites**, **16 disposable naming-gate checks**, typecheck and scoped lint, including the disclosed initial Docker-discovery failure and later successful owned PG17 run/cleanup. Those gates were not independently rerun by this architect review. Repository-call/SQL counts are not treated as production performance measurements. No live charge/refund or provider-account operation is claimed.

### Isolation and Downstream

Reviewed prepared worktree/dependency/synchronization evidence: parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-057-SHOPIFY-012`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-057-SHOPIFY-012`, matching task branches. No implementation, schema, dependency, gitlink or main branch is modified by this review.

SYSTEM-TEST-001's sole explicit prerequisite, SHOPIFY-012, is now Complete; the transitive Shopify implementation chain is accepted. Promoted to Ready, unclaimed, at Attempt 0. No system test is launched here. Developer-owned integration/manual validation and terminal proof remain separate; ARCH-057 is not marked Implemented.

The developer explicitly authorized task/dependency updates, commit and push on 5 November 2026.
