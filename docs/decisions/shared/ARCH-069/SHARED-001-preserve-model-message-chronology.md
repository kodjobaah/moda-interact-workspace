---
id: ARCH-069-SHARED-001
architecture_id: ARCH-069
title: Preserve chronological model conversation inputs
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-069-SHARED-002
created: 2026-11-12
updated: 2026-11-12
---

# Preserve chronological model conversation inputs

## Architecture

ARCH-069 — `docs/architecture/ARCH-069-chronological-commerce-model-inputs.md`; coordinator moda_architect.

## Objective

Correct the Shared OpenRouter model message order while preserving its existing contracts and validation.

## Context

Production's snowboard turn returned an internal-looking indicator. The model serializer independently places current context before prior history. This task addresses only its bounded owning outcome; the exact indicator cause requires evidence and must not be asserted merely from a passing structural test.

## Scope

Repository: `moda-interact-shared`.

- Move current-context message after validated older history and before current-turn tool results.
- Add deterministic role/order/content regressions with older history ending in an assistant failure/indicator and a fresh product question.
- Retain malformed-history rejection, tool-result ownership validation, budgets, cancellation and provider error semantics.
- Prepare version 5.13.2 metadata and a validated package artifact; do not publish.

## Out of Scope

Moderation/STOP changes, sentinel blocklists, provider/model switching, schema or queue changes, credential edits, production message replay, unrelated dependency changes and another repository's implementation.

## Requirements

- Move current-context message after validated older history and before current-turn tool results.
- Add deterministic role/order/content regressions with older history ending in an assistant failure/indicator and a fresh product question.
- Retain malformed-history rejection, tool-result ownership validation, budgets, cancellation and provider error semantics.
- Prepare version 5.13.2 metadata and a validated package artifact; do not publish.

## Work Items

- [x] Move current-context message after validated older history and before current-turn tool results.
- [x] Add deterministic role/order/content regressions with older history ending in an assistant failure/indicator and a fresh product question.
- [x] Retain malformed-history rejection, tool-result ownership validation, budgets, cancellation and provider error semantics.
- [x] Prepare version 5.13.2 metadata and a validated package artifact; do not publish.

## Interfaces / Contracts

Existing Shared ModelRequest/ModelStep and `@modainteract/moda-interact-shared/commerce/model/node`; no wire schema changes. Background remains host/lifecycle owner. Shared implementation owner: ARCH-069-SHARED-001.

## Dependencies

None

## Enables

- ARCH-069-SHARED-002

## Acceptance Criteria

- [x] Move current-context message after validated older history and before current-turn tool results.
- [x] Add deterministic role/order/content regressions with older history ending in an assistant failure/indicator and a fresh product question.
- [x] Retain malformed-history rejection, tool-result ownership validation, budgets, cancellation and provider error semantics.
- [x] Prepare version 5.13.2 metadata and a validated package artifact; do not publish.

## Validation

- [x] Inspect declared package scripts and run focused model adapter regressions.
- [x] Run the existing full Shared suite, typecheck and build required by the repository.
- [x] Run packed-export/import smoke validation; record exact artifact hash and version.
- [x] Where the coordinator supplies a protected failed-context request, record paired old/new no-send probe evidence without committing private payloads; distinguish causality from structural correctness.

## Stop Condition

After the scoped work, acceptance criteria and required validation pass, complete this task's report, set review, publish both mirrored task branches, return to moda_architect and STOP. Do not begin dependent work, merge main or send a production message.

## Implementation Notes

Use launcher-resolved physical parent and implementation task worktrees for the entire attempt. Preserve unrelated changes. All no-send/live diagnostic artifacts must be protected and excluded from Git; no credentials or private customer prompt payloads in reports. Publication task validation is release mechanics only.

## Completion Report

### Status

Ready for Review — implementation commit `8fefac2` pushed on `task/ARCH-069-SHARED-001`; PR https://github.com/kodjobaah/moda-interact-shared/pull/76. No merge or npm publication performed.

### Files Changed

- `src/commerce/model/openrouter-model-client.internal.ts`: System instructions, validated older history, current context, then current-turn tool results.
- `src/commerce/model/openrouter-model-client.test.ts`: update existing order-dependent checks; add current-question/older-assistant-indicator regressions with and without tool results and empty-history regression.
- `package.json`, `package-lock.json`: prepare 5.13.2 metadata; dependencies unchanged.

### Work Completed

Preserved existing ModelRequest/ModelStep contracts, trusted-data framing, history validation, tool-result validation, provider errors, budget and cancellation semantics. Existing natural-text compatibility remains unchanged. No control-token blocklist, provider switch or credential edits.

Physical worktree isolation (launcher evidence):

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-069-SHARED-001`; branch `task/ARCH-069-SHARED-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-069-SHARED-001`; branch `task/ARCH-069-SHARED-001`.
- Shared/default checkouts switched/mutated: no. Another task worktree reused: no.
- Parent and implementation remote task branch fast-forwards: not needed; both origin/main already current at preparation.
- Recursive implementation submodule sync/update passed; no entries.
- Prepared claim `bf404c4a6669a587c553a1d122f8a7b1d34e8c0e`; implementation base `6efe96fa6ba9b17436f8a24a955ccd882e3bcc6b`.

### Validation Results

- Focused adapter suite: 19 passed, 0 failed.
- `npm run typecheck`: passed.
- `npm test`: 717 total; 714 passed, 0 failed, 3 expected integration skips.
- `npm run build`: ESM and declaration build passed.
- `node scripts/validate-commerce-outreach.mjs /tmp/modainteract-moda-interact-shared-5.13.2.tgz`: installed immutable tarball smoke passed; all public export targets present.
- `node scripts/validate-arch024-model-entrypoints.mjs`: browser-safe and Node model exports import without credentials.
- `npm run validate:commerce-entrypoints`: passed.
- `git diff --check`: passed.
- Candidate artifact: `/tmp/modainteract-moda-interact-shared-5.13.2.tgz`; SHA256 `4288d94e9edb2c79ad90b3138d8e88c62b247edd1f2d10e389d4c14c05be3c2e`; npm SHA1 `fb876e81e539a6fe8a3521072b7c8d870c52a389`.
- Coordinator-supplied no-send paired provider evidence using anonymized production-shaped request: previous ordering ended with older assistant and produced unrelated prose with no tools; corrected ordering requested the expected product tool. Exact reported indicator was not deterministically reproduced.
- Coordinator additionally probed the actual built public `OpenRouterModelClient` export from this candidate: expected `commerce_get_product` request, correct synthetic product/variant identities, 251 output tokens, `tool_calls` finish reason, no indicator. Protected diagnostic scripts/payloads remain outside Git.

### Deviations

None. Runtime dependencies reused through an ignored node_modules symlink to the existing validated Shared dependency installation; no dependency or lock resolution changes.

### Assumptions

Existing request schemas and pinned-release contracts remain unchanged. Artifact publication belongs to ARCH-069-SHARED-002 after acceptance.

### Unresolved Issues

Exact indicator causality and production answer verification remain coordinator-owned evidence gates. Passing structural and anonymized provider probes do not prove a deterministic marker-specific cause or a deployed production fix.

### Architectural Concerns

Natural-text finalization is an intentional existing canonical runner behavior and remains schema-validated. A mandatory structured finalization or semantic grounded-answer policy would require separate scope; this chronology task does not silently change it.

## Architect Review

### Review Status

Accepted — Attempt 1, 2026-11-12. Automatic completion authority applied.

### Review Notes

Inspected exact implementation `8fefac2a267a4adc6547d8d4f703dd0c234b2539` against base `6efe96fa6ba9b17436f8a24a955ccd882e3bcc6b`, not only the report. Runtime change is the bounded relocation of the current-context HumanMessage after the unchanged validated history loop. System instructions remain first, current-turn tool results remain last, and data-only trust framing/content/role validation remain unchanged. Package and lock metadata move to 5.13.2 without dependency resolution changes. The chronology regression covers history ending in an assistant indicator and a fresh current product question, with/without current-turn tool results; empty history remains valid.

Both canonical physical worktrees, matching task branch identities, initial synchronization, recursive-submodule readiness and durable launcher claim are recorded and conform. No shared/default implementation checkout was used.

### Reviewed Files

- `src/commerce/model/openrouter-model-client.internal.ts`
- `src/commerce/model/openrouter-model-client.test.ts`
- `package.json`, `package-lock.json`
- This task Completion Report and prepared execution packet `/tmp/moda-arch069-shared-prepare.json`.

### Validation Reviewed

Focused 19/19; full 717 total, 714 passed, three expected integration skips; typecheck, ESM/declarations build, immutable installed-tarball smoke, model and Commerce public-entrypoint smoke all passed. Inspected exact source diff and clean implementation worktree; `git diff --check` passed. Independently verified package metadata5.13.2 and SHA256 `4288d94e9edb2c79ad90b3138d8e88c62b247edd1f2d10e389d4c14c05be3c2e` for `/tmp/modainteract-moda-interact-shared-5.13.2.tgz`. Coordinator's anonymized paired-provider probes select the expected product tool after correction, including the actual built public export. No raw private prompt or credential was committed. No GitHub check is configured for this PR; accepted local checks are the implementation evidence.

### Architecture Conformance

Conforms to ARCH-069 scope, Shared ownership and unchanged ModelRequest/ModelStep contracts. No schema, queue, retry, consent, authorization, infrastructure or delivery change. Exact marker-specific causality remains qualified; the deterministic structural defect and corrected current-turn tool behavior are established, while actual production customer answer verification is still pending.

### Follow-up

ARCH-069-SHARED-002 is Ready to publish only the exact accepted5.13.2 artifact after developer integration. No implementation tests/builds are to be rerun as publication validation. Background remains Pending until publication is accepted Complete. The developer retains all implementation/parent main integration and deployment authority.
