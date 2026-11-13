---
id: ARCH-075-SHARED-001
architecture_id: ARCH-075
title: Define bounded ordered recovery multipart contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: codex
claimed_at: 2026-11-13T00:40:48Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Define bounded ordered recovery multipart contracts

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect. Read all frozen contract constants and lifecycle decisions before implementation.

## Objective

Define bounded ordered recovery multipart contracts.

## Context

User requests logo/shop details before a distinct product image and checkout footer. Existing single-provider-id response cannot safely loop multiple sends. This task owns one bounded prerequisite capability; preserve completed prior behavior.

## Scope

Additive browser-safe ordered schema/type/digest reusing current perpart schemas, pure composition/order helper only if needed, exported entrypoint, package metadata candidate5.13.8 and packed artifact tests.

## Out of Scope

Other repositories/tasks, source main merges/deployment, production sends/replays/resets, billing/usage/cap changes, provider credentials/permissions, unsupported exactly-once assumptions, unbounded fanout/retries, unrelated refactors. Return actual cross-owner gaps.

## Requirements

Exact frozen shape/constants from architecture: max3, roles HEADER/PRODUCT/ANSWER and schemaVersion1 kindRECOVERY_MULTIPART parts[{role,plan}]. Existing media validators unchanged. Enforce permitted role/plan/order combinations and no duplicate roles; HEADER thenPRODUCT with optionalANSWER, HEADER+ANSWER, or singleANSWER TEXT fallback. Each physical part carries complete exact trusted checkout footer; builder accepts trusted URL explicitly and validates no truncation, all body/caption bounds. Keep product pair/brand provenance honest; no fake IDs or mixing roles. Preserve legacy exports/digests exactly. Host authorization/current evidence stays outside Shared. Candidate5.13.8 only if current version free; source builds exact immutable consumable tarball, no publication in this task.

### Explicit pure helper contract

Export a pure validated builder/check that accepts the host's trusted checkout URL explicitly alongside ordered parts, validates that every physical part ends with the exact safe trusted checkout footer/URL, and returns the canonical ordered plan or bounded validation failure. No extraction of authority from model/body JSON. The schema alone cannot authenticate a supplied URL; host original recovery receipt remains authority. Digest binds full role/order/part payload bytes. Count caption1024 Unicode codepoints with astral/emoji cases, preserve complete author text and existing text4096 contract; reject impossible size rather than truncate. Two-part HEADER+PRODUCT-with-answer and three-part HEADER+PRODUCT+ANSWER fixtures must both pass, malformed footer/order/fanout must fail. No provider calls or state logic.

## Work Items

- [x] Implement only assigned capability and document compatibility.
- [x] Complete meaningful required checks and regression/negative evidence.
- [x] Publish mirrored branch/report and return review, then stop.

## Interfaces / Contracts

Use canonical ARCH075 frozen decisions. Shared owns ordered schema/digest and existing perpart media exports; Database owns durable child/status identity; Background owns provider/current authorization and logical aggregation. Never duplicate validators or fabricate product/provider identity.

## Dependencies

None

## Enables

Only dependent tasks after architect acceptance; never begin them implicitly.

## Acceptance Criteria

- [x] Assigned bounded capability and frozen contract behavior satisfied.
- [x] Legacy reads/records remain compatible; no unauthorized cross-owner/billing/security change.
- [x] Durable/contract identity and fault cases satisfy required checks without silent fallback.
- [x] Canonical dedicated mirrored worktree, synchronization and recursive evidence recorded; no private proof committed.

## Validation

- [x] Roles/order/maxpart/footer/Unicode bounds/tampered source/duplicate and long-answer2vs3part golden cases; legacy contracts/digest fixtures unchanged.
- [x] Full package tests/types/ESM+DTS, exact packed installed public JS/types/browser exports and immutable artifact hash.
- [x] Diff/privacy hygiene and report actual results, no production sends or secrets.

## Stop Condition

After required work and validation, set review, submit Completion Report and STOP. No main merge/deploy or enabled task execution.

## Implementation Notes

You are not alone. Preserve others' edits and canonical prepared isolation. Root owns final merges/deployment. Architecture constants resolve inter-agent assumptions; report genuine gaps before expanding scope.

## Completion Report

### Status

Ready for Review. Source committed and pushed at `708c3500e7e66c0894d57e6d2041e7fac1c47190`, [Shared PR82](https://github.com/kodjobaah/moda-interact-shared/pull/82). Candidate5.13.8 is packed and tested, not published. No source or parent main merge performed.

### Files Changed

- `src/commerce/presentation/recovery-multipart.ts`: additive max3 ordered manifest, role-discriminated per-part type/schema, explicit host-trusted checkout-footer builder/parser and stable digest; current media validators are reused unchanged.
- `src/commerce/presentation/recovery-multipart.test.ts`:9 targeted cases for two-/three-part layouts, complete authored bytes, missing-logo/no-product/fallback shapes, role/order/fanout failures, genuine image identity, exact trusted footer, Unicode/legacy text bounds, tampering and digest compatibility.
- `src/commerce/presentation/index.ts`: public presentation entrypoint exports.
- `scripts/validate-recovery-multipart.mjs`: installs the exact packed tarball in a disposable external consumer and checks Node ESM exports, public TypeScript roles/types and browser-safe bundled behavior.
- `package.json`, `package-lock.json`: candidate5.13.8 metadata and artifact-validation script; no dependency changes.
- `README.md`: additive compatibility, ordering/footer contract and host-authorization/state ownership.

### Work Completed

Manifest shape is `schemaVersion:1`, `kind:RECOVERY_MULTIPART`, `parts:[{role,plan}]`. The only valid orders are ANSWER, HEADER→ANSWER, HEADER→PRODUCT and HEADER→PRODUCT→ANSWER. HEADER accepts TEXT or verified LOGO/SQUARE_LOGO BRAND_IMAGE; PRODUCT accepts existing genuine product IMAGE; ANSWER accepts TEXT. COVER_IMAGE cannot masquerade as a logo. Available brand/product identities must agree on shop.

The builder and parser take the host-trusted checkout URL explicitly and require it as every part's exact own final line. They do not extract authority from body/model JSON or strip authored content. Per-part existing media validators retain caption1024 Unicode-codepoint bounds and existing text4096 contract; impossible sizes fail rather than truncate. The digest binds full roles/order/media/body bytes. The plan contains only physical parts; Background retains the original logical root text, source/current receipts, one billing reservation and independent delivery state. Legacy single-plan schemas/helpers/digests remain unchanged.

### Validation Results

All final checks ran against unchanged source `708c3500e7e66c0894d57e6d2041e7fac1c47190`:

- `npm test`:773 total,770 passed,3 existing declared skips,0 failures;75.07s. Final focused new-contract run9/9 passed; combined new and existing brand/product media run22/22 passed before role-type narrowing.
- `npm run typecheck`:passed. `npm run build`:passed ESM and DTS (DTS89.31s under host load).
- `npm pack --ignore-scripts --pack-destination /tmp/moda-arch075-shared-artifacts --json`:packed the already validated exact-head build. Artifact `modainteract-moda-interact-shared-5.13.8.tgz`, SHA256 `ea2186662e130f66c05fbfda9147618ec6ce61fa9b73b3516edb88611455a464`.
- `npm run validate:recovery-multipart -- <exact tarball>`:passed installed Node ESM, direct public TypeScript consumption/invalid-role compile check and browser bundle/runtime isolation. Installed metadata reports5.13.8 and the same artifact hash.
- `npm run validate:commerce-presentation` and `npm run validate:conversation-product-image-node`:passed existing public Node/browser entrypoints without provider I/O.
- Diff/whitespace and task scope checks passed. The repository has no configured `.github/workflows` CI; no absent check is represented as a CI success. Root/architect agreed exact-head local evidence and the immutable installed artifact are the validation contract instead of inventing an unrelated workflow.
- Public npm version5.13.8 availability was checked before versioning (E404). No package publication was attempted; release task must recheck availability and obtain exact public-publication approval.

Prepared launcher proof from `/tmp/moda-arch075-shared001-prepare.json`:

- Canonical primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Dedicated parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-SHARED-001`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-SHARED-001`; both `task/ARCH-075-SHARED-001`.
- Launcher parent and implementation remote-task fast-forward not needed; origin/main already current in both. Implementation base `46834ef32a945606c92feade5924564ce325b326`; parent pre-claim `4acffc3599e958fae4dec3b36fac5cc43f295424`; durable claim `869431dd297e0f1be9fcc432eeb67fe0d198a24c`.
- Recursive submodule sync/update passed; no submodules in this implementation repository. No shared/default checkout was switched or used for implementation, no earlier task worktree reused, no repeated claim or startup discovery.
- Architect coordination commits on the parent task branch were preserved; only this assigned task file is changed for report submission. Implementation Node environment used canonical workspace bootstrap. No environment/permission workaround or source test weakening occurred.

### Deviations

No functional scope deviation. No CI workflow exists in this repository; exact-head full local and packed-consumer evidence is recorded explicitly rather than adding unrelated CI infrastructure.

### Assumptions

The host supplies the original trusted recovery checkout URL and durable current authority. Schema validity or a digest does not authorize a provider send, identify an active tenant, establish consent, or prove current media/sender state.

### Unresolved Issues

Publication belongs to ARCH-075-SHARED-002 after architect acceptance and explicit approval of the immutable public artifact. Background state/composition, database migration, terminal system validation and production verification remain their assigned tasks. No production send or migration was performed here.

### Architectural Concerns

Keep the parts-only contract distinct from root logical billing/content and existing legacy single-message formats. Host must use its original trusted footer/current receipts, preserve per-part verified provenance and durable sequencing/unknown-outcome fences. No Shared state machine/provider/database orchestration was added.

## Architect Review

### Review Status

Accepted

### Review Notes

Independent actual implementation and test review accepted exact source `708c3500e7e66c0894d57e6d2041e7fac1c47190`. Strict additive max-three role/order contract, explicit trusted final-line footer checks, Unicode caption limits, brand/product shop consistency and stable digest reuse conform. The canonical prepared packet and report establish dedicated mirrored isolation and synchronization. No implementation changes requested.

### Reviewed Files

`src/commerce/presentation/recovery-multipart.ts`, its regression tests, public index exports, installed-artifact validator, package metadata and README.

### Validation Reviewed

Exact-head full tests:770 passed/3 declared skips; typecheck, ESM/DTS build, installed public JS/types/browser isolation and existing presentation/product-image entrypoint checks passed. Root independently verified immutable artifact SHA256 `ea2186662e130f66c05fbfda9147618ec6ce61fa9b73b3516edb88611455a464`. Existing absence of repository CI is explicitly recorded, not represented as a CI pass.

### Architecture Conformance

Conforms to ARCH-075 source scope, Shared ownership, legacy single-plan compatibility and host-owned durable authorization/provider lifecycle. Schema/digest do not grant sending authority. Production integration remains pending.

### Follow-up

ARCH-075-SHARED-002 becomes Ready. Execution additionally requires root source merge and explicit public-release approval for the accepted5.13.8 artifact. No rebuild, repack or repeated source validation during publication. Background remains dependency-gated.
