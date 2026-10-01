---
id: ARCH-023-COMMERCE-004
architecture_id: ARCH-023
title: Enforce Merchant Knowledge merchant activation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 62
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-023-COMMERCE-002
  - ARCH-023-ADMIN-004
enables: []
created: 2026-09-30
updated: 2026-10-01
---

# Enforce Merchant Knowledge merchant activation

## Objective

Enforce request-time Merchant Knowledge merchant activation after the accepted COMMERCE-002 bootstrap and ADMIN-004 product-policy reconciliation.

COMMERCE-002 is already accepted with the exact `MERCHANT_OPT_IN` bootstrap prerequisite. This task therefore owns only the remaining runtime correction: extend `merchantKnowledge.lookup` operation-level authority so an enabled `ShopFeaturePreference` is required independently of capability association.

Canonical invariant:

```text
retrievable = planEntitled && merchantEnabled
```

## Scope

Expected bounded surface:

```text
src/commerce/merchant-knowledge/entitlement.ts
merchantKnowledge.lookup operation tests
existing generic capability-selection integration only where needed for defence in depth
```

Do not modify or redesign the accepted COMMERCE-002 Tool/Capability/release bootstrap. Do not redesign pgvector retrieval.

## Requirements

### R1 — preserve accepted COMMERCE-002 bootstrap

COMMERCE-002 is Complete / Accepted Attempt 4 with the exact fixed Feature prerequisite:

```text
key = merchant_knowledge
active = true
activationMode = MERCHANT_OPT_IN
systemRequired = false
```

This task MUST NOT reopen, duplicate or replace that bootstrap guard and MUST NOT add any `ShopFeaturePreference` write to bootstrap.

### R2 — operation-level merchant activation authority

Extend current Merchant Knowledge entitlement resolution to require the exact current Feature preference:

```text
ShopFeaturePreference.shopId = trusted shopId
ShopFeaturePreference.featureId = merchant_knowledge Feature id
enabled = true
```

Missing/false preference -> `DENIED`, `retryable=false`, before query embedding or vector lookup.

Continue to ignore browser/model-supplied shop identity and pending future plans.

### R3 — defence in depth independent of capability grant

Even if the same Tool revision is granted through another eligible Capability, `merchantKnowledge.lookup` must still deny when Merchant Knowledge is OFF.

The generic Commerce capability selector may also remove the feature-bound capability because `MERCHANT_OPT_IN` is OFF; operation-level re-check remains mandatory.

### R4 — OFF is non-destructive

Commerce performs no source/revision mutation when disabled. Re-enabling immediately makes retained eligible ACTIVE chunks retrievable again, subject to current plan/source/provenance rules.

### R5 — tests

Prove:

```text
plan entitled + missing preference -> DENIED before embedding/vector query
plan entitled + false preference -> DENIED
plan entitled + true preference -> existing lookup path unchanged
Tool granted through another Capability cannot bypass preference gate
re-enable makes retained ACTIVE knowledge retrievable without re-ingestion
no ShopFeaturePreference row is created by Commerce
```

## Dependencies

- `ARCH-023-COMMERCE-002`
- `ARCH-023-ADMIN-004`

## Acceptance Criteria

- [x] Accepted COMMERCE-002 bootstrap remains unchanged and preference-neutral.
- [x] Lookup independently requires explicit merchant activation.
- [x] Disabled Merchant Knowledge cannot cause embedding or pgvector retrieval.
- [x] Re-enable reuses retained ACTIVE knowledge.

## Validation

- [x] focused Merchant Knowledge entitlement/operation tests
- [x] live PostgreSQL/pgvector proof where existing COMMERCE-001 test contract requires it
- [x] `npm run typecheck`
- [x] targeted lint/diagnostics
- [x] `npm run build`
- [x] `git diff --check`

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP.

## Completion Report

### Status
Ready for Review — Attempt 2
### Files Changed
`src/commerce/merchant-knowledge/entitlement.ts`, `src/commerce/merchant-knowledge/operation.ts`, `tests/merchant-knowledge-entitlement.test.ts`, `tests/merchant-knowledge-policy.test.ts`, and `tests/merchant-knowledge-bootstrap.test.ts`.
### Work Completed
Merchant Knowledge entitlement now resolves the active plan's current `merchant_knowledge` Feature ID and requires `ShopFeaturePreference` for the authenticated turn's shop and that Feature ID. Missing or disabled preferences return non-retryable `DENIED`; preference database failures map to retryable `UNAVAILABLE`. The operation performs this check before testing embedding configuration, so an opted-out shop causes no embedding, source query, or vector lookup. Tests cover missing/false/true preferences, exact composite-key lookup, preference lookup failure, another-capability context, OFF-to-ON retrieval of retained ACTIVE knowledge, and the bootstrap's lack of preference mutations. The accepted bootstrap implementation was not changed.
### Validation Results
Prepared launcher evidence (2026-10-01T08:27:30Z):

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-COMMERCE-004
parent branch: task/ARCH-023-COMMERCE-004
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-COMMERCE-004
implementation branch: task/ARCH-023-COMMERCE-004
shared workspace checkout switched/mutated for task work: no
shared implementation checkout switched/mutated for task work: no
another task worktree reused: no
parent remote task branch fast-forwarded: not-needed
parent origin/main incorporated: yes; synchronized head 93bb4f80ac05eb8090eeea4aad10f8d8d597f905
implementation remote task branch fast-forwarded: not-needed
implementation origin/main incorporated: already-current; synchronized head efee1b366f325c4d8b8c7c350950558699fcdff8
git submodule sync --recursive: passed
git submodule update --init --recursive: passed
database submodule: 6a8602e67d2308189af81ee0091e5189f1ffd71a (initialized, recursive)
claim: Attempt 1, copilot, committed and pushed as bd0fce1089b0325e33dbba52bb4d72a2ab57c88a
implementation commit: ea88b43cbdf676ee9963b88a7bbae5a6676a66ec (pushed to task/ARCH-023-COMMERCE-004)
```

Focused entitlement/policy/bootstrap tests: 3 files passed, 27 tests passed. Extended Merchant Knowledge tests (entitlement, policy, bootstrap, bootstrap startup, retrieval and contract): 6 files passed, 36 tests passed. Targeted ESLint on all five changed files passed with no output. `npm run typecheck` passed. `npm run build` passed, including manual/runtime package smoke checks, Prisma generation and Next.js production compilation; it emitted the existing Nunjucks dynamic-dependency warning. `git diff --check` passed.

The adjacent `tests/merchant-knowledge-embedding.test.ts` was also tried; one existing config-contract test fails because its `readConfig(base)` fixture omits the required `COMMERCE_BOOTSTRAP_ADMIN_EMAIL`. Architect confirmed this is unrelated and does not need correction.
### Deviations
Attempt 1 did not run the live PostgreSQL/pgvector proof because no disposable database target was configured. Attempt 2 supplied a task-local disposable Docker environment and completed the required proof; no deployment database was used. The unrelated embedding-config fixture failure remains unchanged.
### Assumptions
The current active plan Feature relation is the source of truth for the `merchant_knowledge` Feature ID; `ShopFeaturePreference` absence is equivalent to opted out, consistent with the model's `enabled` default and opt-in activation mode.
### Unresolved Issues
Architect attribution is requested for the adjacent embedding-config test fixture failure and the unavailable disposable PostgreSQL/pgvector target.
### Architectural Concerns
None. The check remains operation-level and independent of the eligible Capability set; bootstrap and pgvector retrieval design are unchanged.

### Attempt 2 Validation Correction
No production-source changes were made. Added `tests/merchant-knowledge-activation-postgres.test.ts`, which invokes `createMerchantKnowledgeLookupAdapter()` against the real migrated schema and exercises missing preference, explicit disabled preference, and enabling that same preference. The test asserts the missing row remains absent after denial, neither OFF call invokes embedding, retained source/revision/chunk snapshots remain unchanged, and the enabled call returns the existing matching-provenance ACTIVE chunk without replacing retained knowledge. Trusted turn context contains only `another-capability`.

Added `scripts/run-merchant-knowledge-activation-postgres.mjs` and the `test:arch023-merchant-knowledge-activation:postgres` package script. The runner rejects checkouts containing dotenv files and non-local Docker contexts, uses image `pgvector/pgvector:pg17`, an ephemeral IPv4 loopback port, a uniquely named `commerce_arch023_activation_test_*` database, and a tmpfs PostgreSQL data directory. It passed all 22 repository Prisma migrations before launching the test with `DATABASE_URL` and `COMMERCE_TEST_DATABASE_URL` set to the same disposable target. Teardown removed the owned container and verified that no container with this invocation's label remained.

Live proof result: **passed**, 1 test. Docker server: `29.5.2`. The successful run used database `commerce_arch023_activation_test_bc9f2dd2ca63` at `127.0.0.1:32793`; these were ephemeral and have been removed. The initial harness run correctly cleaned up its container but exposed an erroneous test guard that rejected the required identical URLs; that guard was corrected before the passing run.

Focused affected Merchant Knowledge tests: 4 files passed, 32 tests passed, 2 live-only tests skipped because those tests require the guarded runner environment. The wider `tests/merchant-knowledge-*.test.ts` run had 44 passing tests and 3 live-only skips, with one known unrelated failure in `tests/merchant-knowledge-embedding.test.ts` because its configuration fixture omits required `COMMERCE_BOOTSTRAP_ADMIN_EMAIL`. Architect confirmed that failure is outside this task; it was not changed.

`npm run typecheck`, targeted ESLint for the new test and runner, Pylance diagnostics for the new files, `node --check` for the runner, and `git diff --check` passed.

Implementation/test commit `72e232a` (`test(commerce): prove merchant knowledge activation in postgres`) was pushed to `task/ARCH-023-COMMERCE-004`. Parent report commit `2fd5519d` records this Attempt 2 evidence. The Attempt 2 parent claim is `b732b9ea`; parent synchronization incorporated `origin/main` at `c047c4feff6e1754b0d06e823a013fd14de0d61b` after resolving the architecture-document merge in favor of upstream's newer history. The recursive database submodule was initialized at `6a8602e67d2308189af81ee0091e5189f1ffd71a`. The implementation worktree is clean after the pushed test commit. Task status is returned to `review`, with executor and claim timestamp cleared, for `moda_architect`.

## Architect Review

### Attempt 2 Review Status

Accepted — Attempt 2

### Attempt 2 Review Notes

Attempt 2 closes the only outstanding finding from Attempt 1. No production-source
change was required. The submitted PostgreSQL/pgvector regression exercises the
production `createMerchantKnowledgeLookupAdapter()` authority path against the real
migrated schema and proves the final request-time invariant:

```text
retrievable = planEntitled && merchantEnabled
```

The live proof demonstrates that a missing `ShopFeaturePreference` and an explicit
`enabled=false` preference both return non-retryable `DENIED` before query embedding or
pgvector retrieval, preserve the retained Merchant Knowledge source/revision/chunk
state exactly, and do not cause Commerce to create a preference row. Updating the same
preference to `enabled=true` immediately retrieves the already-retained matching ACTIVE
chunk through the production retrieval path without re-ingestion or replacement.

The reviewed production implementation remains the conformant Attempt 1 source:
current ACTIVE/TRIALING plan entitlement is resolved first; the exact current
`merchant_knowledge` Feature id is used for the shop/Feature preference lookup;
preference-read failure maps to retryable `UNAVAILABLE`; missing/false preference fails
closed; and trusted `turn.shopId`, not model/browser input, remains the tenant authority.
The accepted COMMERCE-002 bootstrap remains preference-neutral.

### Attempt 2 Reviewed Files

- `src/commerce/merchant-knowledge/entitlement.ts`
- `src/commerce/merchant-knowledge/operation.ts`
- `tests/merchant-knowledge-activation-postgres.test.ts`
- `scripts/run-merchant-knowledge-activation-postgres.mjs`
- `package.json`
- `docs/decisions/commerce/ARCH-023/COMMERCE-004-enforce-merchant-knowledge-activation.md`

### Attempt 2 Validation Reviewed

The submitted evidence records:

```text
disposable pgvector PostgreSQL activation proof        PASS — 1 live test
focused affected Merchant Knowledge suite              PASS — 32 tests
live-only tests outside guarded runner                 SKIP — 2
npm run typecheck                                      PASS
targeted ESLint                                        PASS
changed-file diagnostics                               PASS
runner node --check                                    PASS
git diff --check                                       PASS
```

The runner uses `pgvector/pgvector:pg17`, an invocation-owned container, an ephemeral
IPv4 loopback port, a uniquely named disposable test database, a tmpfs PostgreSQL data
directory, and applies all 22 repository Prisma migrations before executing the proof.
`DATABASE_URL` and `COMMERCE_TEST_DATABASE_URL` are both constrained to that disposable
target for the child process. Teardown removes the owned container and verifies zero
owned containers remain.

The broader Merchant Knowledge glob still contains the previously attributed
`merchant-knowledge-embedding.test.ts` configuration-fixture failure because that fixture
omits required `COMMERCE_BOOTSTRAP_ADMIN_EMAIL`. It is outside the COMMERCE-004 changed
surface and does not overturn the focused/live evidence.

### Attempt 2 Architecture Conformance

Accepted. Request-time Merchant Knowledge retrieval now independently requires both
current plan entitlement and explicit merchant activation. OFF is fail-closed and
non-destructive, another eligible Capability cannot bypass the operation-level gate,
Commerce performs no preference mutation, and re-enable reuses retained ACTIVE
knowledge. The COMMERCE-002 bootstrap, schema/migrations, generic capability-selection
contract, embedding implementation and pgvector retrieval SQL remain outside this task
and unchanged.

### Attempt 2 Dependency Reconciliation

`ARCH-023-COMMERCE-004` is **Complete / Accepted Attempt 2** under
`completion_mode: automatic`. It declares no `enables` tasks. `ARCH-023-SYSTEM-TEST-002`
remains Pending because its other implementation/infrastructure prerequisites are not
yet Complete.

#### Historical Attempt 1 — Changes Requested

### Review Status
Changes Requested

### Review Notes
Attempt 1 production behavior is architecture-conformant on the reviewed Merchant Knowledge activation paths. The operation resolves current ACTIVE/TRIALING plan entitlement, obtains the exact current `merchant_knowledge` Feature id, requires an explicit enabled `ShopFeaturePreference` for the authenticated shop, denies missing/false preference before embedding/source/vector work, maps preference-read failures to bounded retryable `UNAVAILABLE`, and leaves the accepted COMMERCE-002 bootstrap preference-neutral. No production-source correction is requested at this review stage.

Acceptance is withheld because the task's required live PostgreSQL/pgvector validation remains unchecked. The accepted COMMERCE-001 live proof calls `retrieveMerchantKnowledge()` directly and therefore does not exercise the new COMMERCE-004 operation-level preference gate. The focused mocked test proves call ordering but does not prove the changed authority path against the real migrated billing/commerce schema.

The adjacent embedding-config fixture failure is unrelated to COMMERCE-004 and does not need correction in this task.

### Reviewed Files
- `src/commerce/merchant-knowledge/entitlement.ts`
- `src/commerce/merchant-knowledge/operation.ts`
- `src/commerce/merchant-knowledge/retrieval.ts`
- `tests/merchant-knowledge-entitlement.test.ts`
- `tests/merchant-knowledge-policy.test.ts`
- `tests/merchant-knowledge-policy-postgres.test.ts`
- `tests/merchant-knowledge-bootstrap.test.ts`
- `docs/decisions/commerce/ARCH-023/COMMERCE-004-enforce-merchant-knowledge-activation.md`

### Validation Reviewed
- submitted focused entitlement/policy/bootstrap suite: 27 tests passed
- submitted extended Merchant Knowledge suite: 36 tests passed
- submitted targeted ESLint: passed
- submitted `npm run typecheck`: passed
- submitted `npm run build`: passed with the recorded existing Nunjucks warning
- submitted `git diff --check`: passed
- live PostgreSQL/pgvector operation-level activation proof: **required and outstanding**

### Architecture Conformance
Conformant except for the outstanding required live validation. The implementation preserves `retrievable = planEntitled && merchantEnabled`, derives `shopId` only from trusted turn context, performs no preference mutation, preserves OFF as non-destructive, and does not modify the accepted bootstrap or retrieval SQL.

### Follow-up
Return the **same task** through its normal `/moda-task ARCH-023-COMMERCE-004` path for Attempt 2. Attempt 2 is a validation correction, not a production redesign.

Required Attempt 2 contract:

1. Preserve the current production implementation unless the live proof exposes a real defect. Do not modify the COMMERCE-002 bootstrap, schema/migrations, generic capability selection, embedding implementation or pgvector retrieval SQL merely to manufacture a new implementation commit.
2. Add a real migrated-PostgreSQL/pgvector regression for the production `createMerchantKnowledgeLookupAdapter()` path. Prefer extending `tests/merchant-knowledge-policy-postgres.test.ts` or adding one adjacent task-owned PostgreSQL test; do not replace the accepted COMMERCE-001 retrieval proof.
3. The live fixture must use the real ARCH-023 schema and create one authenticated shop with:
   - an ACTIVE or TRIALING current Subscription;
   - an enabled `BillingPlanFeature` mapping to the active `merchant_knowledge` Feature with valid C2 configuration;
   - one retained currently eligible source with an ACTIVE revision and at least one matching-provenance pgvector chunk.
4. Exercise this exact transition through the production adapter with a deterministic local embed stub and trusted turn context whose eligible capability set may contain a non-Merchant-Knowledge capability:

```text
no ShopFeaturePreference row
    -> DENIED
    -> embed not called
    -> retained source/revision/chunk unchanged
    -> preference row count remains zero

explicit preference enabled=false
    -> DENIED
    -> embed not called
    -> retained knowledge unchanged

update the same preference to enabled=true
    -> same adapter call returns OK
    -> production pgvector retrieval returns the already-retained ACTIVE chunk
    -> no re-ingestion/revision/chunk replacement is required
```

5. The test must prove Commerce itself did not create the missing preference: after the first denied call, the shop/Feature preference count remains zero. The fixture may then explicitly create the false row and explicitly update it to true as test setup.
6. Use a task-local disposable Docker PostgreSQL environment with `pgvector/pgvector:pg17`, an ephemeral IPv4 loopback port, a disposable database name containing `test`, and a temporary data filesystem/volume. Apply the repository's real Prisma migrations before the test. `DATABASE_URL` and `COMMERCE_TEST_DATABASE_URL` for the migration/test process must both point at that disposable database. Never use the configured/deployment database.
7. The Docker proof must clean up the task-owned container/volume after success or failure and verify that no owned test container remains. If Docker/Colima is temporarily unavailable, return the task blocked with the exact environment failure; do not substitute the remote database.
8. Run the new live proof, rerun the focused Merchant Knowledge suites affected by the added test, `npm run typecheck`, targeted changed-file ESLint/diagnostics and `git diff --check`. A full unrelated suite rerun is not required solely for this validation correction.
9. Record exact Docker image, migration result, live test result, teardown evidence, implementation/test commit, parent report commit, canonical worktree synchronization and any source changes in the Completion Report.
10. Set the task to `review`, clear `executor`/`claimed_at`, preserve the historical Attempt 1 Architect Review, return to `moda_architect` and STOP. Do not begin any follow-on task.

No production change is requested unless the required live proof exposes one.
