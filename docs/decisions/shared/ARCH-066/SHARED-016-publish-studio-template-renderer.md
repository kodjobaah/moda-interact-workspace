---
id: ARCH-066-SHARED-016
architecture_id: ARCH-066
title: Publish preview-only template renderer
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: review
priority: 20
executor: codex
claimed_at: 2026-11-09T02:09:32Z
attempt: 1
depends_on: ["ARCH-066-SHARED-015"]
enables: ["ARCH-066-COMMERCE-003"]
created: 2026-11-09
updated: 2026-11-09
---
# Publish preview-only template renderer

## Scope and touch points
Release-only package metadata/package lock and existing publication mechanism. Require accepted and explicitly Complete015; preserve exact accepted source and production exports. Select first unused5.x minor version above all published5.x versions, patch0; record registry check/version before publication, never overwrite an artifact. Publish only through existing package mechanism; record source commit, exact version, dist.integrity and downloaded tarball SHA256. Verify public new preview schemas/renderer/types and retained production exports using installed artifact. No consumer edits, new source fixes or live calls. Return a discovered source defect to015; do not repair during release. This task does not depend on sender013/014/Admin001. Acceptance: immutable artifact downloadable, hashes match, exact accepted source preserved beyond release metadata, public import smoke passes. No implementation test reruns as substitute for accepted015 evidence.

## Execution and completion boundary
Definition only. Preserve unrelated work; you are not alone in the codebase. Use canonical launcher task worktrees and mirrored task branches. Record exact source, commands/results and package integrity; submit for review, stop and retain developer completion authority. No main merge/push, deployment, real customer send, Meta call, database mutation in a hosted environment or follow-on task execution is authorized. No acceptance from tests against injected simulation alone.

## Completion Report
Ready for Review — immutable5.10.0 published and downloaded hash verification passed. Final installed downloaded-artifact public runtime/declaration smoke passed exit0.

Source/release metadata: implementation `80bb605f9c6fd026e82b1dd207a1de2874d221b6` pushed on task/ARCH-066-SHARED-016. Prepared baseline56a8130f2f17d805734b40e6220b6011190798f8 source/scripts/tsup exactly match accepted015a19519e460516cfbc95dbe817bae9598e2b4ac6d (including exact accepted009carry869f830 and accepted011 brand/media). Only package.json.version and two matching package-lock version entries changed, three lines5.7.0→5.10.0; no source/runtime/test/export-map edits.

Registry full versions query (not latest tag) showed highest published5.x5.9.0 and5.10.0 unused; selected first next minor5.10.0 exactly. Receipt `/private/tmp/arch066-shared016-versions.json`. Accepted015 local archive SHA256205523f32ba787fa9edb871caae5b0f75e204e8ef3cfb7991b686110535e0ecd verified before restoring all140distfiles. Packed5.10.0 dist byte-matches every accepted015distfile; no implementation tests/lint/typecheck/build reruns. Dependency install and pack scripts disabled; existing validated artifact reused without required build lifecycle.

Concrete reviewed/published archive `/private/tmp/modainteract-moda-interact-shared-5.10.0.tgz`,447293bytes/145files; SHA256`711fe20dfe54f6516e67eab0f6616e7799d4f9d567c93d90819e4eb974f4ac2d`; npm integrity`sha512-cdXKp0YLPg/yFN5acZNpdZbDfzFqY1MV45rFHh1+Q1e8Wf3VFuR1Ylgr8icorCj9h8pE3CTFTheUuxCEMKCfFw==`; shasum`1bfff37342cf701b7811ad2648279984e6b49b0e`. Pack receipt `/private/tmp/arch066-shared016-pack.json`. `npm version 5.10.0 --no-git-tag-version --ignore-scripts`, `npm pack --ignore-scripts --json --pack-destination /private/tmp`, and installed local-archive public runtime/declaration smoke passed. No new feature validation executed.

Publication authority was the user's explicit implementation of this publication task and its deterministic version rule, applied only after concrete archive/source parity and installed smoke evidence. Exact archive published using `npm publish /private/tmp/modainteract-moda-interact-shared-5.10.0.tgz --access public --ignore-scripts --registry https://registry.npmjs.org/`; automatic review allowed, process exited0 with +package@5.10.0, no retries/republish/version overwrite. Log `/private/tmp/arch066-shared016-publish.log`. First exact metadata read2026-11-09T02:12:55Z HTTP404 during processing, second cache-fresh metadata read02:13:44Z remained404. At2026-11-09T02:14:44Z exact metadata and registry-returned tarball became available; downloaded447293bytes SHA256 matches reviewed artifact and independently computed SHA512 matches registry dist.integrity. No retry publication. Evidence `/private/tmp/arch066-shared016-registry.json`, `/private/tmp/arch066-shared016-registry-verified.txt`, `/private/tmp/arch066-shared016-downloaded.tgz`. Registry tarball `https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-5.10.0.tgz`.

`node scripts/validate-commerce-outreach.mjs /private/tmp/arch066-shared016-downloaded.tgz` passed exit0 after immutable download. Installed downloaded-artifact smoke includes Studio3schemas/3types/renderer, existing production renderer, existing purposeFor/selectSendableOutreachOffer/SendableOutreachOffer, Component/FrozenBindings schemas and exact production/Studio text/parameter parity. Static packed declarations retain productDetailSelections and verifyCommerceAnswerPresentationSelection plus accepted brand/media exports. Downloaded smoke log `/private/tmp/arch066-shared016-downloaded-public.log`; local counterpart `/private/tmp/arch066-shared016-local-public.log`. Existing old5.9dist preserved byte-for-byte beyond015 accepted additions. No sender projection dependency or invented registration. Background002 residual72failures remain unwaived; no consumer execution or live action.

Prepared isolation evidence: canonical root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-066-SHARED-016`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-066-SHARED-016`; both task/ARCH-066-SHARED-016. Parent reused baselineb441a3e31072f8b82ba93f480f2976a948ba6c88; implementation created baseline56a8130f2f17d805734b40e6220b6011190798f8. Both remote FF not-needed/main already-current; recursive sync/update passed, no entries, ready. Launcher claimAttempt1codex2026-11-09T02:09:32Z fe7e7895b51c694234d461009ea7713a387ed635 durably pushed; dependency015Complete gate passed. Startup/claim not repeated. Shared/reference checkouts not switched/mutated; no another-task worktree reused. No main merge/push/gitlink, consumer, activation or follow-on changes. Developer completion retained; Architect Review untouched.


## Code-level amendment — 2026-11-09

### Exact release delta and verification
Only package.json.version and the matching package-lock.json root/package version entries may change. Use `npm version "$selected_version" --no-git-tag-version --ignore-scripts` after verifying the recorded accepted015 source and unused registry version. `selected_version` is the first unused next minor above highest published5.x; never select latest tag alone. Do not edit source to make packing pass. Use existing approved repository publication command/registry settings and required packaging lifecycle.

Downloaded installed artifact must export these exact names from `@modainteract/moda-interact-shared/commerce/outreach`:
```typescript
import {
  StudioOutreachTemplateSchema,
  StudioInitialOutreachRenderInputSchema,
  StudioInitialOutreachRenderResultSchema,
  renderStudioInitialOutreachPreview,
  renderInitialOutreachPreview,
  type StudioOutreachTemplate,
  type StudioInitialOutreachRenderInput,
  type StudioInitialOutreachRenderResult,
} from '@modainteract/moda-interact-shared/commerce/outreach';
```
Run runtime/declaration import smoke against the downloaded artifact using existing scripts, record exact version/integrity/tarball SHA256. Production renderer export must remain present. Report diff proving release metadata-only changes. No consumer edits or source correction during016; no invented fixed future version or republish. Public code import above is the required contract, not a request to re-run implementation test suites during publication.


## Mandatory shared-component ownership and reuse — 2026-11-09

This section controls earlier ambiguous wording. Shared means implementation in the published `@modainteract/moda-interact-shared` package, consumed through its public entrypoints. A helper placed only in Commerce or duplicated between services does not meet this requirement.

| Responsibility | Sole implementation owner | Consumers |
|---|---|---|
| Preview template/input/result Zod schemas and inferred types | Shared outreach/template-contracts.ts, public outreach exports | Commerce; Shared tests |
| Placeholder-to-parameter construction | Shared outreach/bindings.ts prepareStoredComponents | Both Shared production and Studio renderer entrypoints |
| Header/body/footer text substitution and length handling | Shared outreach/component-render.ts renderStoredComponentText | Both Shared renderer entrypoints |
| Variable/brand/media resolution | Existing Shared PreparedVariableResolver | Both Shared renderer entrypoints |
| Offer presentation classification and INITIAL purpose mapping | Existing Shared selectSendableOutreachOffer and purposeFor | Both Shared renderer paths; Commerce host selecting frozen content |
| Production registration/approval/hash/sender validation | Existing Shared production entrypoint and Background sending pipeline | Production only; never Studio renderer |
| Database query, selected-shop authorisation, credentials, preview lifecycle/storage and UI | Commerce | Studio only; these are host adapters, not Shared business logic |

### Exact public API addition in SHARED-015

Add to `src/commerce/outreach/index.ts`:
```typescript
export { selectSendableOutreachOffer } from './sendable-offer.js';
export type { SendableOutreachOffer } from './sendable-offer.js';
export { purposeFor } from './selection.js';
```
These export the existing implementations; do not create wrappers, a second classifier or a copied purpose switch. Preserve the exact existing function signatures and inferred return type. Verify SendableOutreachOffer is the existing exported type; if declaration emission requires an existing referenced type, expose that type additively without changing its shape.

COMMERCE-003 imports those helpers from the public outreach entrypoint and uses:
```typescript
const sendable = selectSendableOutreachOffer(evaluation.offerDecision);
const purpose = purposeFor('INITIAL', sendable.presentation);
```
It must not implement its own no-offer/code/automatic mapping. Shared owns reusable semantic decisions; Commerce freezes/selects existing database content using the resolved purpose. The Commerce presentation adapter delegates once and contains no substitution, brand resolution, template approval, hash validation or message-length algorithm.

### Required proof before acceptance

1. Inspect real call sites: production prepareFrozenComponents and renderInitialOutreachPreview delegate to the same Shared prepareStoredComponents/renderStoredComponentText used by renderStudioInitialOutreachPreview. No parallel replacement bodies remain.
2. Shared tests exercise both entrypoints using identical content/variables and assert exact parameters/full text. Production validation still refuses invalid production metadata; Studio does not consume that metadata.
3. Commerce tests invoke the actual installed published renderer and purpose helpers; do not mock them in the parity acceptance test. Mock only host I/O, clocks and external provider/model boundaries. Assert no service-local rendering/classification algorithm or cross-repository source/internal-dist import.
4. SHARED-016 installed-artifact JS/declaration smoke includes the new purpose/classification exports as well as the Studio schemas/renderer. Record the exact accepted package version/integrity in Commerce's report.
5. Review removes replaced duplicate code and verifies old production golden bytes remain unchanged. Merely naming a file “shared” or passing tests against copied helper code is insufficient.

No new standalone service, database table, sender projection or UI component in Shared is introduced. Existing Background consumers use the same common code through their existing production renderer; no Background package change is part of these tasks.


## Architect publication readiness — 2026-11-09
Sole prerequisite SHARED015 explicitly CompleteAcceptedAttempt1, sourcea19519e460516cfbc95dbe817bae9598e2b4ac6d/review7dbfa0ca6c596ffcd1dea62d0b4ca2cecc6cfa1d clean/published. Ready unchangedAttempt0/unclaimed. Reuse retained validated dist and pack/source provenance recorded in015; publication-only metadata and archive/registry checks, no implementation test/lint/typecheck/build revalidation. No publication or implementation worktree created by readiness reconciliation.
