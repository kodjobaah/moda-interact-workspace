---
id: ARCH-070-COMMERCE-001
architecture_id: ARCH-070
title: Adopt compatible OpenRouter preview transport
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-15T00:07:00Z
attempt: 1
depends_on:
  - ARCH-070-SHARED-008
enables: []
created: 2026-11-14
updated: 2026-11-15
---

# Adopt compatible OpenRouter preview transport

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; moda_architect.

## Objective

Adopt the accepted published Shared transport so Commerce preview remains compatible with correctly nested provider routing configuration.

## Context

Preview model-runtime imports OpenRouterModelClient and forwards saved catalogue configuration. Trial015 demonstrated unconditional parallel_tool_calls:false filters all DeepSeek endpoints with require_parameters:true; removing only that hint restores routing. Global catalogue nesting before all consumers adopt the corrected SDK would break preview. Selection efficacy is separate and remains unproved.

## Scope

Exact Shared dependency and real registry lock adoption; focused preview factory/SDK HTTP transport regression; independently reviewable source/report. Expected release6.1.0 is provisional until approved publication; use only actual accepted version from Shared008.

## Out of Scope

Native protocol opt-in, terminal application selection policy, model/catalogue/credential changes, privacy relaxation, Shared mechanics duplication, DB migrations, live calls, settings writes, deployments or main merges.

## Requirements

Use published Shared SDK without local transport copies or sibling imports. Preserve preview credential resolution, tenant isolation, pinned model/configuration, cancellation, budgets, error mapping and logging redaction. Default HTTP omits unsupported parallel_tool_calls; nested provider preferences reach wire unchanged. Preserve strict schemas, tool choices and token limit. No parallel execution authority is inferred from hint omission. Root owns saved configuration mutation only after corrected Background AND Commerce deployments and old-consumer drain.

## Work Items

- [x] Adopt exact approved public Shared version and normal lock.
- [x] Add focused preview/actual SDK HTTP compatibility regression.
- [x] Validate and return immutable source/report.

## Interfaces / Contracts

Shared007 owns reusable transport; Shared008 owns accepted publication. Consume @modainteract/moda-interact-shared/commerce/model/node. Existing preview factory remains application-owned.

## Dependencies

ARCH-070-SHARED-008 must be Complete before normal execution. No fake lock or premature claim.

## Enables

Safe root-owned global saved routing configuration correction after both consumers deploy.

## Acceptance Criteria

- [x] Exact registry dependency installed and lock verified.
- [x] Actual SDK wire omits parallel_tool_calls and preserves nested routing, tool schemas/choice and max_tokens.
- [x] Preview authorization, credential privacy, cancellation and error boundaries unchanged.
- [x] No live/configuration/source ownership violations.

## Validation

- [x] Clean npm ci and installed registry identity.
- [x] Focused model-runtime/preview tests and actual HTTP loopback with no live credentials.
- [x] Declared typecheck/build and scoped lint; exact remote checks if configured.

## Stop Condition

After required checks, set Review, complete report and STOP. No live model calls, settings writes or main merges.

## Implementation Notes

Use normal launcher dedicated mirrored worktrees. Not alone: preserve others changes. Inspect package scripts and local instructions; do not repeat unrelated broad tests. Final deployment must precede root catalogue nesting.

## Completion Report

### Status

Ready for Review. Exact source `5901420c41f6a9a60fdef283e55cd8829c815dd8`, https://github.com/kodjobaah/moda-interact-commerce/pull/196. Published6.1.0 dependency and focused preview transport adoption complete. No native opt-in, runtime business-code, model/configuration, database or live changes.

### Files Changed

- package.json and package-lock.json: exact public Shared5.13.0→6.1.0; one manifest/four lock lines only.
- tests/preview-openrouter-transport.test.ts: actual installed SDK through default preview factory and local127.0.0.1 HTTP server; automatic/named choices, exact schemas/strict, nested routing, absent unsupported parallel hint,2048 tokens, original request unchanged.
- tests/arch066-initial-outreach-host.test.ts: authorized duplicate type import removal, existing recovery-policy mock completion, unnecessary any removal, synthetic approved registration raw observation hash vs authored submitted hash separation, diagnostic assertion message.
- tests/arch066-initial-outreach-lifecycle.test.ts, tests/arch066-initial-outreach-media.test.ts, tests/arch066-initial-outreach-preview.test.ts, tests/arch066-initial-outreach-refusals.test.ts: required existing readBudgetDefaults fixture mocks; lifecycle unused import removal.

### Work Completed

Adopted real registry URL and SRI through normal npm install; clean npm ci then all163 installed package files byte-matched the approved302b91f5 archive (977151B). Integrity `sha512-h4bQaLuufY4u2CF4X6oS/7BbRWvNnfVN8cFJvL/xrhcmS4lqnob2qAgSTm/r5q3NqEIUWxuPw9FpypndQT+qiA==`. No sibling source imports/local transport copies or fabricated lock. Preview credential resolution, current snapshot configuration, cancellation/error mapping and staff/tenant boundaries retain existing runtime code. All required full typecheck diagnostics were corrected in authorized fixtures without skips, relaxed assertions, null observation hashes or production changes.

### Validation Results

- Normal registry install and `npm ci --registry=https://registry.npmjs.org`: PASS. Approved archive SHA256302b91f5ad24353ac3052c1e8c5d456b3c90d072d64665edff579eb56eb249d5/SRI/version6.1.0 and163/163 installed members PASS.
- Focused preview commands: `npm test -- tests/preview-openrouter-transport.test.ts tests/preview-openrouter-runtime.test.ts tests/arch067-model-context.test.ts tests/preview-service.test.ts tests/preview-integration.test.ts tests/preview-routes.test.ts`; five suites56PASS initially, routes import initially lacked fresh generated Prisma enum. Declared `npm run prisma:generate` PASS; exact routes rerun7PASS. Combined63 unique tests/six files PASS, not one all-green original invocation.
- Authorized five ARCH066 fixture suites: initial44 tests yielded40PASS/4FAIL (missing existing policy mock caused503). Mock completion exposed three synthetic production parity PROVIDER_DRIFT failures; diagnostic confirmed wrong observed hash domain. Corrected nonnull raw components-only hash while authored submitted hash remains locale.contentHash; final exact host rerun5/5PASS. Retained39 other unique passing cases →44 unique outreach cases PASS. No assertion/guard weakening. Total focused107 unique cases across11 files; traces retained under /tmp/arch070-commerce001-*.log.
- Final `npm run typecheck`: PASS exit0 after fixture corrections; no baseline waiver. Initial ten errors (duplicate import and missing required budget mocks) disclosed and resolved. Final log /tmp/arch070-commerce001-types-green.log.
- `npm run typecheck:build`: PASS. `npm run build`: PASS exit0, Next webpack/types/prerender complete; existing Nunjucks dynamic-dependency warning. Later changes confined to test files excluded by tsconfig.build.json, no production/dependency byte changes after build.
- Scoped ESLint over new transport test and all five corrected outreach files: PASS exit0/zero output, /tmp/arch070-commerce001-lint-green.log. Initial inherited any error/unused import warning corrected, not waived.
- `git diff --check`: PASS. Exact head PR196 statusCheckRollup empty; GitHub check-runs/statuses total0. No hosted check success claimed when none configured.
- Install warnings: existing peer/deprecation/allow-scripts notices and npm audit36 vulnerabilities (18moderate/17high/1critical). Lock diff changes only Shared pin/URL/SRI; no audit remediation or unrelated dependency upgrade authorized/performed.
- No live model/provider/DB/Redis service, Meta or Render calls. Local Redis test fixtures use owned Unix sockets with suite cleanup; wire uses synthetic credentials and local HTTP only.

### Deviations

Authorized scope extensions9792391c0/bcc48f9a9 and subsequent root/architect instruction repaired exact five existing test fixtures to make full checks green. No runtime behavior changes beyond consuming the published SDK correction. Initial bootstrap lacked explicit MODA_WORKSPACE_ROOT while outside primary; corrected using exact launcher root and sanctioned bootstrap before Node execution. No manual Node path/version change.

### Assumptions

Root deploys corrected Commerce and both catalogue-consuming Background workers and drains old processes BEFORE nested provider configuration is saved. This task does not perform or certify that rollout.

### Unresolved Issues

None in implementation. Architect acceptance and root source/parent integration/deployment remain; no main merges or live operations by agent.

### Architectural Concerns

Global saved catalogue configuration affects all consumers. Do not apply nesting before all corrected SDK consumers deploy/drain. Transport regression proves serialization compatibility only, not model selection efficacy or WhatsApp delivery.

### Git / VCS

Normal launcher prepared attempt1/codex claim `2aa345e87e82ea15f92d5ec9fc2437faeb0e5a9a` at2026-11-15T00:07:00Z. Canonical primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-070-COMMERCE-001`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-070-COMMERCE-001`; both branches task/ARCH-070-COMMERCE-001. Parent reused, implementation newly created; no shared checkout switched/mutated, no other task worktree reused. Launcher dependency Shared008 Complete verified; parent task FF not needed/originmain alreadycurrent at4d6a1346a; implementation task FF not needed/originmain alreadycurrent at4485f16d19c01afc09496aef280ad109af068825. Recursive submodule sync/init passed, database exact5329d5390d346042895219663f3a040ea54ae168 ready. No database pin edits.

Implementation source5901420c41f6a9a60fdef283e55cd8829c815dd8 committed/pushed origin/task/ARCH-070-COMMERCE-001; parent current task report committed/pushed separately. Parent gitlink not staged. No implementation/workspace main merge, main push, force push, publication or deployment.

## Architect Review

### Review Status

Pending

### Review Notes

Defined; not executable until published dependency accepted.

### Reviewed Files

Existing preview/model-runtime.ts and package scripts inspected read-only.

### Validation Reviewed

None

### Architecture Conformance

Commerce-only dependency adoption; reusable transport remains Shared-owned.

### Follow-up

Promote after Shared008 Complete.

### Actual registry promotion

Shared008 architect Complete accepted683a5fce8. Execute normal launcher now against public6.1.0 exact approved archive302b91f5ad24353ac3052c1e8c5d456b3c90d072d64665edff579eb56eb249d5,977151bytes163members/SRIsha512-h4bQaLuufY4u2CF4X6oS/7BbRWvNnfVN8cFJvL/xrhcmS4lqnob2qAgSTm/r5q3NqEIUWxuPw9FpypndQT+qiA==. Registry receipt independently verified00:03:39Z/versionlatest6.1.0;6.0.1unchanged. Adopt realregistrylock/npmci, no unpublisheddependency. Existing5.13.0→6.1 migration must diagnose actual removedAPI failures; do not add compatibility machinery or broaden policies. All source/runtime ownership boundaries and finalrootdeploy-before-settings requirement unchanged.

### Required full-typecheck test fixture correction (root authorized)

Root explicitly requires full declared typecheck green, not a baseline waiver. Scope includes ONLY five existing ARCH066 test files with actual diagnostics: remove duplicate SubsetSchema imports and supply required local InitialOutreachHost.readBudgetDefaults mock fixtures using the current contract. Preserve requiredport semantics, existing auth/business assertions and production runtime. Do not weaken types/skip tests or add compatibility code. Record exact files/corrections, rerun full declared typecheck and affected tests plus productionbuild/scopedlint. This is a bounded test-maintenance extension; no new runtime capability.

Saved global provider nesting rollout gate: BOTH recovery and messaging workers using the catalogue SDK, AND Commerce preview, must deploy the corrected dependency and drain predecessor processes before root updates configuration through audited normal writer. Apply per affected environment; preserve old catalogue until all consumers confirmed. No settings/deploy bytaskagent.

### Existing ARCH066 fixture completion (root authorized)

Full declared typecheck now passes, but the same touched initial-outreach-host fixture omits the existing currentCommerceRecoveryExecutionPolicy runtime export; actual host constructor therefore fails503 in four cases. Authorize ONLY adding that existing policy mock using DEFAULT_COMMERCE_RECOVERY_EXECUTION_POLICY and the fixture's matching synthetic1000ms/1000token limits. Preserve actual authorization/freeze/referral assertions and production policy. Also remove unnecessary db:any annotation in that same test (existing callsite retains explicit PrismaClient cast) and unused InMemoryPreviewStateStore test import in lifecycle file. No runtime code or assertion weakening. Rerun failing host fixture, affected scopedlint and full typecheck; retain other40passing cases/build evidence. No baseline waiver.

### Synthetic provider observation fixture parity (root authorized)

The same touched host fixture wrongly substitutes authoring content+bindings hash for provider observed components-only hash, yielding truthful PROVIDER_DRIFT. Correct its nonnull lastObservedContentHash to the existing canonical provider-components domain, retaining submittedContentHash=locale.contentHash and all drift/readiness assertions. Existing providerObservationHash sorts keys and excludes example recursively; fixture/helper must respect this exact domain. No null bypass, hash rewriting of runtime records or production comparison changes. Root authorizes minimal obvious fixture-contract/mock/import corrections within the SAME five test files when supported by actual diagnostics and unchanged production contracts; no serial new permission is needed for each such correction. Fulltypecheck/affectedtests/scopedlint/build must pass. Return any actual runtime/ownership gap toarchitect instead of expanding.
