---
id: ARCH-056-API-001
architecture_id: ARCH-056
title: Align the API Database dependency with accepted lifecycle contracts
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 3
depends_on:
- ARCH-055-DATABASE-001
- ARCH-055-API-005
enables:
- ARCH-056-SYSTEM-TEST-001
created: '2026-11-03'
updated: 2026-11-04
---

# ARCH-056-API-001: Align the API Database dependency with accepted lifecycle contracts

## Architecture

Architecture: `ARCH-056`. Parent: `docs/architecture/ARCH-056-background-persistence-and-recovery-progress.md`. Coordinator: `moda_architect`.

Definition revision: 4. **Materialised and Complete at Attempt 3.** Attempt 1 was returned for changes; Attempt 2 recorded the non-blocking validation exception and the scoped dependency amendment; Attempt 3 reran the upload PostgreSQL suite successfully and satisfied the existing acceptance criteria. The implementation remains a justified zero diff.

## Objective

Make the API's recorded and materialized Database dependency supply the accepted schema and migrations consumed by the API's normal generated client.

## Context

U1 compares `moda-interact-workspace(20261103-212722).zip` with its canonical Database tree. API's nested schema lacks `MerchantConversationSendCommand.followUpClaimKey` and `MerchantKnowledgeUploadedAsset.intentPurposeKey`, and exactly three ARCH-055 migrations. The API's current source consumes both fields. Its `build` and `typecheck` scripts regenerate from `database/prisma/schema.prisma`. The ARCH-047 helper can select a separate migration source while the human-send harness still generates from the nested path; an override is not this task's correction.

The ZIP cannot reveal whether the real recorded gitlink is old or only its exported materialization was stale. Resolve that distinction before any edit. Existing accepted task history remains intact; this task does not repeat ARCH-055-API-004's workflow changes or ARCH-055-API-009's readiness/aggregate-runner work.

## Scope

One repository: `moda-interact-api`. Paths below are relative to that implementation repository.

| Path | Operation | Boundary |
|---|---|---|
| `database` | Verify/materialize; update this gitlink only if the recorded pin lacks the accepted contract | The only allowed committed implementation change |
| `package.json` | Read only | Use the existing generation, build and focused test scripts; no script/dependency bump |
| `database/prisma/schema.prisma` and `database/prisma/migrations/` | Read only through the verified dependency | Never edit a nested schema or historical migration |
| `scripts/arch047-canonical-schema.mjs` | Read only | Existing predicate is not broadened into a new architecture validator |
| `scripts/test-arch040-woo-human-send-postgres.mjs` | Read only | Verify normal client generation uses the synchronized dependency |
| `src/merchant/conversations/messages/admission.service.ts` | Read only | Verify the accepted claim-key field compiles normally |
| `src/merchant/merchant-knowledge/upload.service.ts` | Read only | Verify the accepted purpose field compiles normally |

No new implementation or test file is required. Record evidence in this task's Completion Report. If the recorded dependency is already correct, accurate rematerialization and validation can produce a zero-diff implementation result; do not manufacture code churn or an implementation commit.

## Out of Scope

No API endpoint/DTO/auth/upload/readiness behavior change, new schema/migration, historical task reopening, arbitrary version upgrade, schema-copy workaround, generated-client commit, Shared publication, production rollout or edits to any `_index.md`. Do not advance the parent workspace gitlink to an unmerged API task commit.

## Requirements

1. Use the launcher-prepared API and matching parent task worktrees. The recorded pin, working dependency HEAD and actual schema/migration bytes must be recorded separately.
2. Choose the accepted merged Database revision from real accessible task/Git evidence. Historical documents name accepted implementation `5907b4572ea9efc2a24c07e4c3bd3e107db4260b` and merged revision `8e74634ff92be9900f693c0c449ffce888e7d617` as tree-equivalent. Those are investigation anchors, not a command to pin an unverified SHA. Verify the relevant commit/tree and integration history in the real checkout.
3. Require both nullable fields with the accepted native types: `followUpClaimKey String? @db.VarChar(255)` and `intentPurposeKey String? @db.VarChar(64)`. Preserve every other schema definition.
4. Require these three existing forward migrations, unchanged: `20261102120000_arch055_rest_read_lifecycle`, `20261102121000_arch055_human_follow_up_claim_identity`, `20261102122000_arch055_upload_intake_identity`. Matching only the model fields is insufficient. All common pre-existing migration bytes remain unchanged.
5. Preserve original public idempotency keys and historical stored claim keys. This task changes dependency coherence, not the producer/consumer contract. Existing pending uploads and the original-intake index retain ARCH-055's accepted behavior.
6. Do not execute the coordinated deployment. Record that ARCH-055's migration/quiescence and compatible Background/both-producer rollout still govern release. This focused task does not establish architecture-wide ARCH-055 completion.

## Work Items

- [x] Inspect recorded gitlink, working dependency HEAD, clean state and accepted merged Database history.
- [x] Rematerialize a correct recorded dependency, or advance only the API-owned gitlink to the verified accepted merged contract.
- [x] Verify the two fields, three migration files and unchanged common migration bytes.
- [x] Rerun normal client generation through the existing typecheck/build path and the focused migration-backed API suites below; apply only the documented ARCH-035 exception.
- [x] Report real provenance, exact commands/results and the committed diff or justified zero-diff outcome.

## Interfaces / Contracts

No new TypeScript/public/Shared interface. The consumed persistence contract is owned by `ARCH-055-DATABASE-001`; the accepted upload consumer is `ARCH-055-API-005`. Both normal commands must still invoke `prisma generate --schema database/prisma/schema.prisma`. Selecting a sibling schema through a test override is not a replacement.

At the reviewed baseline the canonical schema SHA-256 is `5c68e467f392cafe2e6b5be730b81e000a3590e31567135c4037791bcfe11052`; the stale API schema SHA-256 is `45df5e44bdc1e7e29495e391a1754477f0df362c667d648f4b6893b6541f5c0d`. These identify this review's bytes, not a permanent ban on later accepted migrations. If later accepted source is present, establish that lineage and contract explicitly; an unexplained divergence is a stop condition.

## Dependencies

- `ARCH-055-DATABASE-001` — Complete and accepted persistence contract.
- `ARCH-055-API-005` — Complete and accepted purpose/intake consumer.

`ARCH-055-API-004`, `ARCH-055-API-009` and `ARCH-055-SYSTEM-TEST-001` retain their existing scopes/statuses. They are not synthetic gates for this narrow dependency correction. A failure inside their unrelated unfinished behavior must be reported accurately, not fixed opportunistically here or hidden as a successful validation.

## Enables

- `ARCH-056-SYSTEM-TEST-001`, after its other prerequisites are also Complete.

## Acceptance Criteria

- [x] Recorded and working Database revisions have a verified accepted relationship and provide the exact required contract.
- [x] Normal `npm run typecheck` and `npm run build` succeed without an out-of-band generated client.
- [x] The ARCH-026 and ARCH-040 focused migration-backed API suites pass against the synchronized dependency, with no test-only canonical override masking the nested client path. The ARCH-035 upload suite is rerun and its exact result recorded. Its previously observed result (1 passed, 1 failed with Prisma `Transaction not found` in the upload service) is a non-blocking exception for API-001 only if the rerun reproduces that same failure signature; it remains a failure, not a pass, and does not establish upload behavior as correct. Any different or additional failure blocks acceptance.
- [x] Existing fields, migration bytes, public retry identities and historical keys are preserved.
- [x] Only the API `database` gitlink changed, or a zero-diff rematerialization result is truthfully demonstrated.
- [x] Real task/worktree/branch/submodule evidence and disposable-resource cleanup are recorded; deployment is not claimed.

## Validation

From the launcher-resolved implementation worktree, inspect first:

```bash
git status --short
git ls-tree HEAD -- database
git submodule status -- database
git -C database rev-parse HEAD
git -C database status --short
```

If the recorded revision is correct but materialization is stale, use the existing workflow:

```bash
git submodule sync -- database
git submodule update --init --recursive -- database
```

Those commands cannot choose a new pin when the recorded pin itself is old. The latter case requires the verified accepted revision, not a guessed literal supplied by this document.

Required commands after the dependency is coherent and existing locked dependencies are available:

```bash
npm run typecheck
npm run build
npm run test:arch026-woo-rest-read:postgres
npm run test:arch035-knowledge-upload:postgres
npm run test:arch040-human-send:postgres
git diff --check
```

- [x] Inspect the exact command output and migration source; no skipped/no-test result counts as a pass.
- [x] Record recorded/working nested revision, schema hash, missing/changed migration comparison, generated Prisma version, real parent/implementation HEADs and container cleanup.
- [x] Use disposable PostgreSQL 17 + pgvector through the existing runners; no live database, `db push`, destructive schema reset or ad hoc schema source.

These are validation obligations, not results already obtained by the architect. Historical accepted tests do not prove this checkout passes. The ARCH-035 suite must be rerun; only the exact previously recorded failure signature may use the architect-approved API-001 exception. A skipped run, different failure or additional failure does not qualify.

## Implementation Notes

Follow the common execution/logging/evidence contract in the parent architecture. This task needs no new runtime logger. Any runner/database failure must retain its original diagnostic and redacted safe context. The three migrations and their rollout semantics remain owned by ARCH-055; no accepted task or `_index.md` is modified by this definition.

### Stop Condition

Stop and report before changing scope if accepted dependency provenance is unavailable, the real checkout has unexplained schema drift, validation exposes a failure outside the architect-approved exact ARCH-035 exception, or a fix would require another repository/schema/task. Do not substitute an arbitrary current Database revision or weaken any other gate. Once scoped acceptance and validation pass, complete this task's report, publish the normal mirrored task evidence, set `status: review`, return to `moda_architect` and stop. Do not execute the enabled system task.

## Completion Report

This section belongs to the implementing repository agent. No implementation is recorded by this definition.

### Attempt 3 Completion Report

#### Status

Accepted and Complete — Attempt 3. All required validation passed. The implementation is a justified zero diff; no ARCH-035 exception was needed because the required upload suite passed on this rerun.

#### Files Changed

Implementation repository: no files changed. The recorded `database` gitlink was already correct. The implementation worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-056-API-001`, branch `task/ARCH-056-API-001`, HEAD `20108b9e7dc4a66b1e296be53dab289fe5c3680b`; it is clean. The previously published implementation task ref at `2384bac6cea135d5571bd9f771f9431cfb0c7b45` was an ancestor of the current worktree HEAD and was fast-forward-pushed to `origin/task/ARCH-056-API-001` at `20108b9e7dc4a66b1e296be53dab289fe5c3680b`. No implementation commit was manufactured.

Parent workspace: this task file only. The parent worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-056-API-001`, branch `task/ARCH-056-API-001`; its pre-submission HEAD is the launcher claim commit `d31ed6db91daee4f9db9b4281d427b29dbb175db`.

#### Work Completed

The recorded API gitlink and initialized working Database submodule both resolve to `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. The accepted merged Database revision `8e74634ff92be9900f693c0c449ffce888e7d617` has the same tree, `9a91d956274810aeedd168c83b72c50f6d7f29f`; the two commits are separate integration-history commits, and `git diff --exit-code 8e74634ff92be9900f693c0c449ffce888e7d617 -- prisma/schema.prisma prisma/migrations` reports no differences.

The synchronized schema SHA-256 is `5c68e467f392cafe2e6b5be730b81e000a3590e31567135c4037791bcfe11052`. It contains `followUpClaimKey String? @db.VarChar(255)` and `intentPurposeKey String? @db.VarChar(64)`. The three required existing migrations are present and byte-identical to the accepted merged revision: `20261102120000_arch055_rest_read_lifecycle`, `20261102121000_arch055_human_follow_up_claim_identity`, and `20261102122000_arch055_upload_intake_identity`. The full migration directory is also identical to the accepted revision, preserving common pre-existing migration bytes. No API producer/consumer behavior, source, scripts, dependencies, generated client, schema or migration files were changed.

#### Validation Results

- `npm run typecheck`: passed; normal Prisma Client generation used `database/prisma/schema.prisma`.
- `npm run build`: passed; normal Prisma Client generation used `database/prisma/schema.prisma`.
- `npm run test:arch026-woo-rest-read:postgres`: passed, 9 tests; all 71 migrations applied, including the three ARCH-055 migrations.
- `npm run test:arch035-knowledge-upload:postgres`: passed, 2 tests, 0 failures, 0 skipped; all 71 migrations applied. The prior Attempt 2 `Transaction not found` failure did not recur. This result is a pass, not an exception or waiver.
- `npm run test:arch040-human-send:postgres`: passed, 6 tests, 0 failures, 0 skipped; all 71 migrations applied.
- `git diff --check`: passed; implementation worktree remains clean.

All three PostgreSQL runners use disposable `pgvector/pgvector:pg17` containers and remove their started container in `finally`. No cleanup-failure diagnostic appeared. The post-run `docker ps -a --format '{{.Names}}'` check showed no task runner containers; listed containers belonged to unrelated persistent services. Prisma Client version generated by the normal path was `6.19.3`. No test-only schema override, live database, `db push` or destructive reset was used.

No coordinated deployment was run. ARCH-055 migration/quiescence and compatible Background/both-producer rollout requirements still govern release. API-002 was not launched or created, and the enabled system-test task was not started.

#### Deviations

No implementation deviation. The accepted dependency was already correctly recorded and materialized, so the API implementation remains intentionally zero diff.

#### Unresolved Issues

None for this task's acceptance criteria. The Attempt 2 upload failure remains preserved as historical validation evidence; the exact required Attempt 3 rerun passed 2/2 without code changes.

#### Architectural Concerns

No new concern. Deployment and cross-service rollout remain outside this task and follow ARCH-055 coordination.

### Attempt 2 Historical Report

Accepted at Attempt 3. The accepted Database dependency is recorded and materialized correctly, all required migration-backed suites passed, and the implementation is a justified zero diff.

### Files Changed

Implementation repository: no files changed; the recorded `database` gitlink already points to the accepted contract.

Parent workspace: this task file only. Materialization commit: `e5fd2d7836581ddbf95161973cac44020910bbfe`; claim commit: `29d6a92b26003b57e2ebb464219d3d88c3e54bee`.

### Work Completed

The launcher-prepared API worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-056-API-001` on `task/ARCH-056-API-001`, HEAD `2384bac6cea135d5571bd9f771f9431cfb0c7b45`. It is clean; no implementation commit is needed. The recorded gitlink and initialized working `database` submodule are both `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. Accepted Database revision `8e74634ff92be9900f693c0c449ffce888e7d617` has the same tree as that pin (`9a91d956274810aeedd168c83b72c50f6d7f29f8`).

The synchronized schema SHA-256 is `5c68e467f392cafe2e6b5be730b81e000a3590e31567135c4037791bcfe11052`. It contains `followUpClaimKey String? @db.VarChar(255)` and `intentPurposeKey String? @db.VarChar(64)`. The three required migrations are present: `20261102120000_arch055_rest_read_lifecycle`, `20261102121000_arch055_human_follow_up_claim_identity`, and `20261102122000_arch055_upload_intake_identity`. The accepted merge preserves common pre-existing migration bytes. No API producer/consumer behavior or deployment was changed.

Launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-056-API-001`, branch `task/ARCH-056-API-001`; implementation branch `task/ARCH-056-API-001`; parent and implementation `origin/main` were already incorporated; no other task worktree was reused. Recursive submodule sync and update passed, with `database` initialized at the recorded commit. Both disposable PostgreSQL 17 + pgvector runners cleaned up their containers.

### Validation Results

`npm ci`: completed to provide the locked dependencies. It emitted Node/npm engine-version warnings and reported 15 audit findings; no dependency or lockfile changes were made.

- `npm run typecheck`: passed; normal Prisma client generation used `database/prisma/schema.prisma`.
- `npm run build`: passed; normal Prisma client generation used `database/prisma/schema.prisma`.
- `npm run test:arch026-woo-rest-read:postgres`: passed, 9 tests.
- `npm run test:arch035-knowledge-upload:postgres`: failed, 1 passed and 1 failed. The failing upload scenario reported Prisma `Transaction not found` in `src/merchant/merchant-knowledge/upload.service.ts`. API source is read-only in this task, so this was not changed.
- `npm run test:arch040-human-send:postgres`: passed, 6 tests.
- `git diff --check`: passed; implementation worktree clean; no runner containers remained.

The three test commands used the synchronized nested Database dependency, not a test-only schema override. No coordinated deployment was run. ARCH-055 migration/quiescence and compatible Background/both-producer rollout requirements remain in force.

### Deviations

No implementation deviation. The accepted dependency was already materialized, so the API implementation result is intentionally zero diff. One required focused suite remains failing as described above; request architect disposition before treating all acceptance criteria as passed.

### Assumptions

The reviewed snapshot and accepted prerequisite contracts are the definition baseline. Recheck the real current checkout and task state at launch.

### Unresolved Issues

The upload suite's `Transaction not found` failure requires diagnosis by the owning architecture/review process. This task did not alter the read-only API source. Do not treat ARCH-056 API completion as proof of ARCH-055 rollout or architecture-wide completion.

### Architectural Concerns

Return changes to ownership, contracts, schema, transaction boundaries, durable-state semantics, queue behavior, security or another repository to moda_architect before expanding scope.

## Architect Review

This section belongs only to moda_architect. Definition authoring is not implementation acceptance.

### Review Status

**Accepted — Attempt 3 (2026-11-04).** Task status is Complete; the attempt number remains 3. The prior Changes Requested reviews and routing notes below are retained as history and superseded by the Attempt 3 acceptance record at the end of this section.

### Review Notes

The following Attempt 1 findings and Attempt 2 disposition are historical. The upload validation failure was rerun in Attempt 3 and passed 2/2; the zero-diff implementation ref is published at the reported task HEAD.

1. **Historical [P2] validation finding:** `npm run test:arch035-knowledge-upload:postgres` previously failed with `Transaction not found`. Attempt 3 reran it successfully with 2 tests, 0 failures and 0 skips.

2. **Historical [P2] publication finding:** the implementation ref was absent in Attempt 1 and later published as a justified zero-diff task ref. Attempt 3's published implementation ref is `20108b9e7dc4a66b1e296be53dab289fe5c3680b`.

Attempt 1 was returned to Ready; Attempt 2 and its review routing were preserved. Attempt 3 is now accepted and Complete. There is no active claim.

### Reviewed Files

- API implementation worktree at `20108b9e7dc4a66b1e296be53dab289fe5c3680b`; published task ref, justified zero diff.
- Nested Database gitlink and working HEAD `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`; canonical Database commit `8e74634ff92be9900f693c0c449ffce888e7d617` with the matching tree.
- This task report and its Attempt 3 validation evidence.

### Validation Reviewed

Reviewed the reported Attempt 3 validation: typecheck, build, ARCH-026 PostgreSQL 9/9, ARCH-035 upload PostgreSQL 2/2, ARCH-040 human-send PostgreSQL 6/6, and `git diff --check` passed. The three PostgreSQL runners applied all 71 migrations and cleaned up their task-owned containers. Tests were not rerun during architect review.

### Architecture Conformance

The accepted Database pin supplies the required fields and migrations, and the API implementation is a justified zero-diff. The previous upload suite failure was resolved by a passing Attempt 3 rerun. No source-scope expansion, API-002 launch or production deployment occurred.

### Follow-up

`ARCH-056-SYSTEM-TEST-001` remains Pending because its other Background prerequisites are incomplete. No downstream task is promoted by this acceptance.

### Review Disposition — Attempt 2 Routing (2026-11-04)

The required `npm run test:arch035-knowledge-upload:postgres` failure is **not waived**. Its acceptance criterion remains unchecked. The submitted result remains 1 passed and 1 failed with Prisma `Transaction not found`; this architect routing did not rerun tests or assert a cause.

The implementation branch finding is resolved without a source commit: `moda-interact-api` has the published `task/ARCH-056-API-001` ref at `2384bac6cea135d5571bd9f771f9431cfb0c7b45`, matching the reported clean zero-diff task commit. No implementation source or test work was performed in this routing step.

`ARCH-056-API-002` is the bounded API-owned diagnosis/correction task for the failing upload suite. API-001 now depends on API-002 and is `pending`; its Copilot claim is cleared, and attempt 2 is preserved. After API-002 is accepted, API-001 must rerun the three required PostgreSQL suites and satisfy every existing criterion before acceptance. No ARCH-056 system-test task is created or made Ready by this disposition.

This routing supersedes only the earlier Follow-up instruction to address both findings within API-001's task branch: the implementation-ref publication finding is resolved, and the upload source/test diagnosis and correction belongs to API-002. The earlier review notes remain as historical review evidence.

### Architect Review — Scope and Validation Amendment (2026-11-04)

**Disposition:** API-001 is Ready for its next normal attempt. Preserve Attempt 2 and all prior review evidence; there is no active claim. The current task dependency list is limited to `ARCH-055-DATABASE-001` and `ARCH-055-API-005`. The prior API-002 dependency/routing remains historical evidence and is superseded as a gate for API-001. This amendment does not create or authorize launching API-002.

The ARCH-035 upload PostgreSQL suite must still be rerun and its exact result recorded. The previously observed result (1 passed, 1 failed with Prisma `Transaction not found` in the upload service) may be a non-blocking exception for API-001 only if the rerun reproduces that same failure signature. Record it as **failed, non-blocking exception for API-001**, never as passed; it does not establish upload behavior as correct. A skipped run, different failure or additional failure blocks acceptance. All other acceptance criteria remain unchanged.

### Architect Acceptance — Attempt 3 (2026-11-04)

#### Review Notes

Attempt 3 satisfies the task's accepted dependency and validation criteria. The API repository's recorded `database` gitlink and working submodule are both `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. The pinned commit and accepted merged Database commit `8e74634ff92be9900f693c0c449ffce888e7d617` resolve to the same tree, `9a91d956274810aeedd168c83b72c50f6d7f29f`, as confirmed against the canonical Database repository. The required schema fields and three migrations are present. The implementation task ref is published at `20108b9e7dc4a66b1e296be53dab289fe5c3680b`; no artificial implementation commit was added.

#### Validation Reviewed

Reviewed the reported passing typecheck, build, ARCH-026 PostgreSQL 9/9, ARCH-035 upload PostgreSQL 2/2 with zero failures/skips, ARCH-040 human-send PostgreSQL 6/6, and `git diff --check`. The three disposable database runs applied all 71 migrations and cleaned up their task-owned containers. No tests were rerun during architect review.

#### Architecture Conformance

Conforms to the task's dependency-coherence scope. The API-owned pin already supplies the accepted contract, so the justified zero-diff result is correct. No source behavior, generated client, schema, migration, dependency, deployment or unrelated task was changed.

#### Follow-up

`ARCH-056-SYSTEM-TEST-001` remains Pending because its other Background prerequisites are incomplete. API-002 was not launched. No other task is promoted by this acceptance.

#### Accepted Completion Decision

`completion_mode: automatic`; task status is Complete at Attempt 3 with `executor: null` and `claimed_at: null`. The parent acceptance record is the only task-definition change; the implementation branch remains the published zero-diff ref at `20108b9e7dc4a66b1e296be53dab289fe5c3680b`. No merge to main or deployment was performed.
