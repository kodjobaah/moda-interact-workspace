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
status: in_progress
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

- [ ] Adopt exact approved public Shared version and normal lock.
- [ ] Add focused preview/actual SDK HTTP compatibility regression.
- [ ] Validate and return immutable source/report.

## Interfaces / Contracts

Shared007 owns reusable transport; Shared008 owns accepted publication. Consume @modainteract/moda-interact-shared/commerce/model/node. Existing preview factory remains application-owned.

## Dependencies

ARCH-070-SHARED-008 must be Complete before normal execution. No fake lock or premature claim.

## Enables

Safe root-owned global saved routing configuration correction after both consumers deploy.

## Acceptance Criteria

- [ ] Exact registry dependency installed and lock verified.
- [ ] Actual SDK wire omits parallel_tool_calls and preserves nested routing, tool schemas/choice and max_tokens.
- [ ] Preview authorization, credential privacy, cancellation and error boundaries unchanged.
- [ ] No live/configuration/source ownership violations.

## Validation

- [ ] Clean npm ci and installed registry identity.
- [ ] Focused model-runtime/preview tests and actual HTTP loopback with no live credentials.
- [ ] Declared typecheck/build and scoped lint; exact remote checks if configured.

## Stop Condition

After required checks, set Review, complete report and STOP. No live model calls, settings writes or main merges.

## Implementation Notes

Use normal launcher dedicated mirrored worktrees. Not alone: preserve others changes. Inspect package scripts and local instructions; do not repeat unrelated broad tests. Final deployment must precede root catalogue nesting.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

Publication dependency pending.

### Architectural Concerns

Global catalogue configuration affects all consumers; coordinate rollout.

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
