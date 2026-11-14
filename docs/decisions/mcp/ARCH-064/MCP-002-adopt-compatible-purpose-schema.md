---
id: ARCH-064-MCP-002
architecture_id: ARCH-064
title: Adopt accepted database schema required by pinned purpose reader
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: codex
claimed_at: 2026-11-14T04:58:14Z
attempt: 1
depends_on:
  - ARCH-064-MCP-001
  - ARCH-064-DATABASE-001
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Adopt accepted database schema required by pinned purpose reader

## Architecture

ARCH-064; docs/architecture/ARCH-064-published-initial-outreach-profile.md; moda_architect.

## Objective

Make the already-implemented typed pinned-purpose reader build and run against its compatible accepted canonical database schema.

## Context

User reports Render build failure src/capabilities/prisma-reader.ts24: purposeMembers missing from generated CommerceReleaseFeatureSelect. Read-only explorer and source inspection confirm MCP main ebbdc07 selects the correct accepted relation but nested Database pinbd2d090 predates it; canonical accepted Database2e14f8668346dfc135aa12f8d1fbc94e05c12ce7 contains purposeMembers and CommerceReleasePurposeCapability. This is dependency drift, not permission to remove scope authorization.

## Scope

MCP-owned nested database gitlink adoption of compatible accepted canonical commit2e14f8668346dfc135aa12f8d1fbc94e05c12ce7; generated-client build/type validation and meaningful existing pinned-purpose reader/auth/runtime tests. Minimal direct test/fixture correction only if genuine gap exposed.

## Out of Scope

Database schema/migration/seed edits, any live DDL/data/provider/Render/Admin operation, Shared release/adoption, removing purposeMembers selection, authorization weakening, unrelated refactor/dependency cleanup or main merge.

## Requirements

- Normal launcher dedicated parent/implementation worktrees and mirrored task branch; preserve all primary untracked files, especially session_export.json/private local data. Do not read/publish sensitive ad-hoc exports or copy them into task source. Primary unrelated staged ARCH069 parent file must remain untouched.
- Reproduce the generated-client/schema mismatch on exact old pin via bounded build/type evidence where practical, then adopt exact accepted Database2e14f8668346dfc135aa12f8d1fbc94e05c12ce7 as nested gitlink, no source migration edits. If current origin main already fixed, report evidence instead of duplicate change.
- Preserve releaseInclude satisfies Prisma.CommerceReleaseInclude, actual immutable Feature.purposeMembers relation and same-release projection. Do not replace typed selection with any/casts/omission or query draft memberships. Existing shop/platform/current release/plan/preference/purpose/capability/revision authority remains fail-closed.
- Fresh normal npm install/client generation must resolve accepted schema and compile purposeMembers. Do not commit generated client/node_modules/dist, inferred Prisma types or copied schema. No database/runtime credentials in logs/report.
- Meaningful runtime validation should exercise actual generated Prisma reader against disposable accepted schema, including pinned purpose subset and denied wrong-release/tenant/permission cases through existing integration harness. Prefer existing coverage; no contrived test merely mirroring gitlink hash.
- Use repository-declared scripts/task validation; inspect actual package.json. Fix only directly related test/fixture mismatch if exposed; report unrelated baseline failures honestly and return wider issues rather than broad cleanup. No new deployment topology/telemetry/publication mechanism.
- Commit/push exact implementation and parent report with ready PR links and remote CI/check evidence. Root owns final source/main and parent actualgitlink merges; no live operations by agent.

## Work Items

- [x] Verify bounded old generated-client failure and accepted dependency relation.
- [x] Adopt exact compatible accepted database gitlink without changing authorization/source semantics.
- [x] Run declared build/types/lint/unit and meaningful disposable pinned-purpose runtime checks.
- [x] Push exact source/report/PR/check evidence and stop for review.

## Interfaces / Contracts

Existing ARCH064 canonical database purpose membership model and MCP trusted-purpose/current release contract. Existing Shared5.12.5 remains unchanged; no new package release needed. Database adoption consumes accepted source, not a new migration task.

## Dependencies

ARCH-064-MCP-001 and ARCH-064-DATABASE-001 Complete. Exact current accepted canonical Database2e14f8668346dfc135aa12f8d1fbc94e05c12ce7 is root-supplied and already integrated in parent; no new DDL permission.

## Enables

Root source/parent integration and separately owned deployment verification. No application task depends on a system-test task.

## Acceptance Criteria

- [x] Clean generated Prisma/client build/types recognize purposeMembers and immutable same-release membership.
- [x] Pinned-purpose subset and tenant/release/auth fail-closed behavior preserved in meaningful runtime tests.
- [x] Changes bounded to nested pin and necessary direct validation; no Shared/schema/auth weakening.
- [x] Mirrored clean isolated commits/reports/PRs/remote checks ready for root; primary private files preserved.

## Validation

- [x] Build the exact production MCP Dockerfile on accepted pin (actual Node24.19bookworm path), with no sensitive env/buildargs; reuse existing lifecycle runner if it builds the same file, avoid duplicate heavy build. Root explicitly requires this actual failing build path, not host TypeScript alone.

- [x] Bounded old-pin failure and new generated-schema/build proof.
- [x] Declared npm run build,typecheck,lint,test:unit and typecheck:integration where relevant to actual runtime harness.
- [x] Existing disposable PostgreSQL integration runner covering real purpose reader and denial cases (no hosted DB); report exact executed subset/flags and skips.
- [x] Diff/privacy/no-generated-file scan, canonical preparation/isolation/synchronization and final remote CI review.

## Stop Condition

When required checks pass, push both task branches, set review and return Completion Report; STOP. Do not merge main, deploy or begin adjacent capabilities.

## Implementation Notes

You are not alone; preserve all other work. Existing reader relation is correct; update dependency rather than weakening query. No new observability or Gateway task identified because build/schema dependency only, no runtime topology change.

## Completion Report

### Status

Review-ready. Implementation and all required local checks published; architect acceptance has not been made.

### Files Changed

- MCP `database` gitlink: bd2d09066a8eb178a56f48fbbf88df637c411059 → accepted 2e14f8668346dfc135aa12f8d1fbc94e05c12ce7.
- MCP `tests/integration/purpose-reader.integration.test.ts`: real generated Prisma reader/registry coverage of immutable purpose subset versus differing draft membership; wrong release, tenant, missing profile, out-of-subset capability and revoked recovery entitlement stop before adapter execution.
- This task file only in the parent repository.

### Work Completed

Preserved typed `releaseInclude satisfies Prisma.CommerceReleaseInclude`, nested immutable `features.purposeMembers` selection and same-release projection unchanged. No production TypeScript, Shared version, schema/migration/seed or authorization change. New test obeys the existing ARCH021 feature configuration/snapshot guard.

Implementation commits: 5809b8d5c39eb2ebff3da816cab80e5bbd934210 and fixture correction 8dd4a0854367d84a5c31f6710915def70dfdd5ee (remote head). Draft source PR: https://github.com/kodjobaah/moda-interact-mcp/pull/23. Draft parent report PR: https://github.com/kodjobaah/moda-interact-workspace/pull/1038.

Physical worktree isolation:

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-064-MCP-002
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-064-MCP-002
parent and implementation branches: task/ARCH-064-MCP-002
shared workspace/implementation checkout switched or mutated for task work: no
another task worktree reused: no
parent remote task branch fast-forwarded: not-needed
parent origin/main incorporated: already-current
implementation remote task branch fast-forwarded: not-needed
implementation origin/main incorporated: already-current
launcher recursive submodule sync/update: passed
launcher database pin: bd2d09066a8eb178a56f48fbbf88df637c411059
launcher claim: Attempt1, codex, 2026-11-14T04:58:14Z
claim pushed: 82077a6c5878547180864410b99b4d5681cedc99
```

Primary private exports were not read or copied; primary untracked files were not modified; all task implementation writes stayed inside the supplied worktree. Unrelated staged parent work was untouched. The task-local parent branch incorporated root amendment 51d1f2745 without editing other task/architecture surfaces.

### Validation Results

- Old pin: `npm ci --ignore-scripts`, then `npm run build` generated Prisma6.19.3 and reproduced TS2353 at prisma-reader.ts24: `purposeMembers` missing from CommerceReleaseFeatureSelect.
- Accepted pin: fresh normal `npm ci` passed; `npm run build` and `npm run typecheck` passed with explicit Prisma generation against accepted schema. npm reported existing audit/lifecycle-script policy warnings; no dependency cleanup performed.
- `npm run lint` passed, including final corrected fixture.
- `npm run test:unit`: final 475 passed, 0 failed, 0 skipped. Initial run 473/475 failed only because ignored canonical Shopify schema artifact was absent. `npm run schema:install:shopify -- /Users/kwadwoadomafriyie/project/moda-interact-workspace/moda-interact-commerce/lib/discovery/artifacts/admin-2026-07.json` installed the existing artifact with enforced SHA256 2b507dc1f74c6157e0eb98500db0f3c3e238d69eaf0d98fd7657ac7ed3f6900b; full rerun passed. Artifact remains ignored/uncommitted.
- `npm run typecheck:integration` passed after correcting exactOptionalPropertyTypes in new test's omitted profile fixture; final disposable runner repeated and passed this check.
- `npm run test:integration:docker` (no subset flags): final 37 tests, 36 passed, 0 failed, 1 skipped (`opt-in live Shopify test`; MODA_MCP_LIVE_SHOPIFY not enabled). Actual generated reader purpose test passed. Entire accepted migration chain applied only to disposable loopback PostgreSQL. Final project moda-mcp-it-8ebc4ab260d6 and its volume/network were cleaned. First run exposed new fixture omission: PostgreSQL23514 `ARCH021 release Feature snapshot must match current or historical behaviour prompt` at release-feature insert. Added matching configuration and reran full suite successfully; no guard weakening.
- `npm run test:production:docker:lifecycle -- --build`: production Docker `npm run build` passed (Prisma generation + tsc,58.2s); cold build timed out at900000ms during migrate-image unpack/export after runtime image completion. Both built tags passed image inspection: runtime sha256:8e05b8d8d65234218cde0d7932e75f83ea2417d51f91dad3d80fea5c1115852c; migrate sha256:68f70760cefef1ae584febe7a148840f76dfb0490bd88fba8d7dc1c94f9f62d0. Harness cleanup completed in2s; no labelled lifecycle containers or compose/buildx process remained. Root explicitly authorized one normal image-reuse lifecycle rerun; `npm run test:production:docker:lifecycle` passed (exit0) using those exact built images: liveness200, readiness503 on dependency loss while liveness stays200, readiness200 after PostgreSQL restart, SIGTERM graceful exit0 with expected shutdown logs; disposable stack cleanup completed2s. Original timeout limits retained; no prune, rebuild or timeout inflation. Same Dockerfile targets runtime/smoke, Node24.19.0-bookworm-slim base digest sha256:a9f5f7c91a432850b2a8a7797adf5eadb6c733ceed61167806cee7ea7fbc29df. Dockerfile SHA256 c70986317bb8d56afdfbc7758f21899c615560b34ad9ae7bc71447561fd92123. No sensitive build args/env supplied. Production build context unchanged between5809b8d and8dd4a08; correction only touches ignored tests.
- `git diff --check` passed; implementation worktree and database submodule clean; local/remote source head match. Source diff is exactly the gitlink plus test; no generated files, credentials, copied schema or production-source changes.
- GitHub exact source head8dd4a0854367d84a5c31f6710915def70dfdd5ee: check-runs total_count0; combined status pending,total_count0,statuses[]. Repository has no tracked workflow. This is absence of remote checks, not a CI pass.

### Deviations

Added focused runtime integration coverage because existing purpose coverage used mocked reader records. No scope expansion beyond direct validation. Full unit and integration reruns addressed actual missing artifact/test-fixture evidence.

### Assumptions

Root owns final source/parent integration and all deployment operations. No agent hosted database/provider/Admin/Render operation was performed.

### Unresolved Issues

No unresolved source/runtime failures. Remote CI is unconfigured (0 reported checks/statuses); no remote CI pass is claimed. Root owns all acceptance/merge/deployment decisions.

### Architectural Concerns

Only new runtime scalar read requirement is commerce.CommerceReleasePurposeCapability(releaseId,purposeFeatureId,capabilityId,position), added by 20261106192000_arch064_purpose_capability_membership. Existing reader follows immutable release-feature membership, not draft CommercePurposeCapability. Composite release/feature and release/capability FKs and immutable trigger remain intact.

Old→accepted pin also includes migrations 20261106023000_remove_order_support,20261108173000_arch066_conversation_product_context,20261109210000_arch068_conversation_delivery_plan,20261111090000_arch038_initial_outreach_tool_call_budget,20261113004310_arch075_ordered_delivery_parts,20261113111320_arch075_meta_app_operation_state. Shared exact delta with root: order-support retirement deletes bounded feature mappings/configuration and feature; ARCH038 updates missing PLATFORM/LIVE tool-call budgets; others add schema. MCP Docker build/start and Gateway TEST/PROD MCP service blocks do not run migrations.

Root supplied external read-only evidence (not independently queried by this agent): at04:57:36/04:59:35–38 both TEST/PRODUCTION required purpose columns, enabled immutable trigger, RESTRICT composite FKs, and all seven canonical finished/non-rolled-back migration checksums matched. Root retains private mcp-purpose-schema-readiness-{test,production}.json and mcp-purpose-migration-readiness-{test,production}.json receipts. No new hosted DDL required per root evidence.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted exact source8dd4a0854367d84a5c31f6710915def70dfdd5ee (MCP PR23) and immutable parent report821c89c1ae1d86bcfbe4396c473fe75b9e5b44e9 (workspace PR1038). Actual source diff inspected: only nested accepted Database2e14f866 gitlink and meaningful generated-reader/execution-registry integration test. Correct typed purposeMembers reader and authorization source remain unchanged; no casts, omission, draft-query fallback or Shared release. Canonical launcher isolated worktrees/synchronization/recursive submodule claim82077a6c reviewed; parent actual origin/main already current. No findings.

Exact old-pin generated Prisma build reproduced TS2353 and accepted-pin host/actual production Docker compilation passes. Root external read-only TEST/PROD prerequisite evidence confirms required columns, immutable trigger/RESTRICT FKs and all7finished migration checksums. MCP build/start/Blueprint do not replay migrations; no live DDL needed by this change. Primary private/untracked files and unrelated staged ARCH069 work preserved.

### Reviewed Files

Actual database gitlink delta; generated-reader integration test including differing draft membership, immutable subset, denied wrongrelease/tenant/missing-profile/outsubset/revocation before adapter; existing reader/registry authority; package scripts/Dockerfile and final validation/report.

### Validation Reviewed

Fresh npm-ci,build/type/lint/integrationtype PASS;475unit PASS; actual disposable integration36PASS/1explicit opt-inliveShopify skip. Exact Node24.19bookworm Docker production build/Prisma+tsc PASS; initial cold export exceeded original900s bound, exact completed images inspected, owncleanup and one root-authorized normal verified-image lifecycle run PASS (live200/dependencyready503/recovery200/gracefulSIGTERM0), no timeout/prune/guard waiver. Source-context equivalence across test-only correction reviewed. No configured GitHub checks(status/count0), not a claimed CI pass. Scoped diff/privacy/generated-file checks PASS. No further broad reruns needed.

### Architecture Conformance

Bounded accepted-schema dependency correction conforms to ARCH064 purpose membership and repository ownership; no runtime auth semantics changed. Source accepted for root integration; production deployment/runtime health remains root-owned verification. This acceptance does not mark overall ARCH064 implemented.

### Follow-up

Root merges implementation first then actual merged main gitlink into parent task, then merges parent. Root verifies Render test/production new commit/build/readiness replaces failed build/predecessor. No new migration/publication/agent live operation. Preserve diagnostic/cold-export traces and opt-in skip disclosure.

## Developer Integration

Root merged source PR23 exact reviewed8dd4a0854367d84a5c31f6710915def70dfdd5ee into MCP actualmainf317ddf249066133ac89a807106998c6cf98b6e4 at2026-11-14T05:28:12Z. Architect independently fetched actual main and verified reviewed source is an ancestor and its complete source tree is byte-identical to mergedmain. At root's explicit request this parent feature branch pins only moda-interact-mcp to that actual merged SHA; no implementation checkout or primary/unrelated staged files changed. Parent origin/main was already current. Root owns final parent PR1038 merge and deployment/live verification; this commit is reviewable feature-branch integration only.
