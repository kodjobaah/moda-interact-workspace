---
id: ARCH-075-BACKGROUND-006
architecture_id: ARCH-075
title: Constrain keyed translation provider output schema
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 5
executor: codex
claimed_at: 2026-11-13T09:44:29Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-005
  - ARCH-075-SHARED-004
enables:
  - ARCH-075-SYSTEM-TEST-001
created: 2026-11-13
updated: 2026-11-13
---

# Constrain keyed translation provider output schema

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Constrain keyed translation provider output schema.

## Context

Actual provider output was syntactically valid JSON but echoed input-only protectedTokens in result segments; strict ResultSchema correctly rejected it. Existing Responses batch request is prompt-only without text.format. Prevent shape drift at provider generation rather than stripping fields or weakening ingestion.

## Scope

Background-owned providers/translation.provider.ts keyed-segments-v1 Responses batch payload and directly related strict result schema exposure/JSON-schema derivation plus provider/codec regression tests. Reuse existing ResultSchema as the owning contract; no competing generic parser or new cross-service contract.

## Out of Scope

Shared release/schema/DB migration, model/provider switch, loosening ResultSchema or marker/key/hash checks, stripping echoed metadata, manual candidate changes, automatic extra retries, live provider calls/translation retries/deployment by agent, unrelated translation refactors.

## Requirements

Only keyed-segments-v1 requests use official Responses text.format strict JSON Schema, root schemaVersion1/segments and segment objects key/text only, additionalProperties:false at each object and required fields. Keep exact existing runtime bounds/strict parser/marker+key identity checks, including rejection of extra metadata. Derive/reuse same local result schema where SDK supports it; if provider JSON-schema subset cannot express some local bound, preserve stricter local validation and document limit rather than silently weaken it. Batch endpoint/correlation/idempotency/status/error handling unchanged; non-keyed translation request behavior unchanged. Verify exact configured model and installed SDK support using official docs; no unsupported fallback or model substitution. Root handles normal UI retry after accepted deployment. No production output/customer text in fixtures/logs; synthetic reproduction only.

## Work Items

- [x] Reproduce missing provider output contract and extra-field refusal with synthetic fixture.
- [x] Add strict keyed provider schema using supported installed SDK/model contract.
- [x] Complete focused/regression/exact-head validation, mirrored report and stop.

## Interfaces / Contracts

Existing local keyed translation ResultSchema and Responses Batch /v1/responses request. Official OpenAI guide https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses establishes strict text.format/json_schema and Batch support; exact selected model/SDK compatibility must be verified. No new Shared version.

## Dependencies

ARCH-075-BACKGROUND-005; ARCH-075-SHARED-004

## Enables

ARCH-075-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Actual prepared Batch JSONL keyed request carries strict exact result JSON schema; generic translation remains unchanged.
- [x] Extra protectedTokens/context/unknown fields still fail ingestion; marker/key/hash/truncation/refusal/error boundaries stay strict.
- [x] Official model/SDK evidence, canonical isolation and passing exact checks reported, no live mutation.

## Validation

- [x] Red/green actual provider JSONL payload/schema tests; valid strict output and echoed metadata rejection through actual codec/worker; existing translation provider regressions.
- [x] Declared relevant focused tests, typecheck/scoped lint and exact-head full CI; no unnecessary persistence/schema tests.
- [x] Diff/privacy hygiene and no dependency/model/provider change or real request.

## Stop Condition

After scope and required checks complete, set review, submit mirrored Completion Report and STOP. No dependent implementation or live action.

## Implementation Notes

You are not alone; preserve other changes. Canonical prepared packet owns startup/claim. Existing accepted tasks must not be rewritten. Root owns merges and live verification.

## Completion Report

### Status

Ready for Review. Implementation and validation complete; awaiting moda_architect review.

### Files Changed

Implementation commit `6bf2da70f935aaaa287454904bbf9387157ff153` on `task/ARCH-075-BACKGROUND-006`; draft PR https://github.com/kodjobaah/moda-interact-background/pull/217:

- `src/providers/translation.provider.ts`: derive one strict format with official SDK `zodTextFormat(ResultSchema, "keyed_translation_segments_v1")`; attach only to keyed-segments-v1 Responses request bodies.
- `src/services/template-translation/segment-codec.ts`: export the unchanged authoritative local ResultSchema; no parser/marker/key/hash logic changed.
- `tests/unit/providers/translation.provider.test.ts`: inspect actual uploaded mixed Batch JSONL; schema appears only on keyed requests and exact correlation/model/endpoint stay intact.
- `tests/unit/services/template-translation/provider-contract.test.ts`: actual JSONL request schema shape, required fields, strict objects, schemaVersion and all existing numeric bounds; ordinary request remains format-free.
- `tests/unit/services/template-translation/segment-codec.test.ts`: extra protectedTokens/context/unknown fields still reject; same strict local key/text/count/version bounds.
- `tests/unit/services/template-translation/strict-result-ingestion.test.ts`: actual provider JSONL decoding through codec and worker lifecycle ingestion, using synthetic mocked transport/repository only.

### Work Completed

Reproduced the missing output contract in actual request builder and uploaded JSONL (two red payload tests). Existing strict codec correctly rejects echoed input metadata. Added provider-side constrained generation from that same local ResultSchema, using the installed official SDK instead of a competing schema/parser. Root object permits only schemaVersion=1 and segments; segment objects permit only key/text. Both objects forbid additional properties and require every field. Existing key length 1..256, text length 1..8192 and segment count 1..64 bounds are emitted unchanged. No local bound was dropped; current base model supports the schema subset. Marker occurrence identity, exact segment membership/order reconstruction, source/output hashes and local validation remain necessary and unchanged.

Ordinary translation request JSON remains unchanged. Batch endpoint, correlation/custom IDs, upload flow, idempotency, status/error handling and token limits are unchanged. No provider/model/dependency/schema/Shared release or retry-policy change. No metadata stripping, candidate editing, provider requests, live database writes, retries, deployment or merge by this agent. Retained output evidence was inspected structurally only; no provider/customer text copied into source, tests or diagnostics.

### Official Model and SDK Evidence

- Bounded read-only affected-run database metadata confirmed by recovery_consent_format: provider `openai`, configured/request providerModelId `gpt-4.1-mini`, modelConfigurationVersion 2. The retained response resolves to exact snapshot `gpt-4.1-mini-2025-04-14`. Lifecycle passes batch.providerModelId verbatim and batches copy run.providerModelId; this implementation never substitutes the model.
- [Official GPT-4.1 mini model page](https://developers.openai.com/api/docs/models/gpt-4.1-mini), directly fetched: documents Responses endpoint, Batch, Structured Outputs support and the alias/snapshot family including the observed snapshot.
- [Official Structured Outputs Responses guide](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses), directly fetched: documents strict text.format/json_schema, Batch support and `zodTextFormat` from `openai/helpers/zod`. Required fields and additionalProperties:false match the generated schema. The listed string/array bound exclusions apply to fine-tuned models; the observed base model is not fine-tuned.
- Clean installed versions read directly from package manifests: OpenAI 7.15.0, Zod 4.6.5. Installed `openai/src/helpers/zod.ts` exports zodTextFormat, detects Zod v4, converts with z4.toJSONSchema and toStrictJsonSchema, and emits strict:true/type:json_schema. Focused tests exercise the installed helper on the actual owning schema with all bounds preserved.
- Official documentation and local SDK verification required no API credentials or provider calls. No unsupported fallback was introduced.

### Validation Results

- Red: `npx vitest run tests/unit/providers/translation.provider.test.ts tests/unit/services/template-translation` before source correction: 2 payload/schema failures, 37 passes. Both actual builder and actual uploaded keyed JSONL omitted text.format; extra-metadata rejection tests already passed.
- Green: same command with added direct worker ingestion/bounds regressions: 5 files / 50 tests passed. Proves valid strict restoration, input-only protectedTokens/context/unknown refusal, strict bounds/version, truncation/refusal/provider-error behavior and unchanged key/marker drift rejection. Synthetic data and mocked provider transport/repository only.
- `npm run prisma:generate` and `npx tsc --noEmit`: passed.
- `npx eslint src/providers/translation.provider.ts src/services/template-translation/segment-codec.ts tests/unit/providers/translation.provider.test.ts tests/unit/services/template-translation`: passed.
- `git diff --check`: passed; only six assigned implementation files. No dependency/lockfile/database/runtime-policy changes or real output/customer text.
- Exact-head full CI passed (384 files / 4,213 tests, Prisma generation and TypeScript): push run https://github.com/kodjobaah/moda-interact-background/actions/runs/43405101447 and PR run https://github.com/kodjobaah/moda-interact-background/actions/runs/43405196810 at `6bf2da70f935aaaa287454904bbf9387157ff153`.
- Self-review: source diff only adds owning-schema export and keyed-only SDK format; runtime parser, model selection, hash/marker/key checks, submission semantics and ordinary provider flow are unchanged. No persistence behavior changed, so no additional PostgreSQL test was required by task scope.

### Physical Isolation and Launcher Evidence

Prepared packet `/tmp/moda-arch075-background006-prepare.json` supplied the following evidence; preparation/claim was not repeated:

- Canonical workspace root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-BACKGROUND-006`, reused; branch `task/ARCH-075-BACKGROUND-006`.
- Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-BACKGROUND-006`, launcher-created; same mirrored task branch.
- Shared workspace/implementation checkout switched or mutated for task work: no. Another task worktree reused: no.
- Parent and implementation remote-task fast-forward: not-needed; both origin/main incorporations: already-current.
- Recursive submodule sync/update: passed; database at recorded `a9b6ab852a8245dfd14447808aac288a23b113d0`, unchanged.
- Dependency gate passed; durable claim `6a0fdfdb8d93610af85153477aa5aed7a7d60738`, attempt 1, executor codex.
- A read-only git diff process stalled on fsmonitor; only that identified process was terminated. Subsequent Git commands used a per-command core.fsmonitor=false override. No persistent Git configuration/environment changes.

### Deviations

None. Latest Architect Review is Pending; no Changes Requested corrections exist and this agent makes no architect decision.

### Assumptions

Root retains the approved configured model and performs the normal UI retry only after acceptance/deployment. Provider-side schema enforcement complements the unchanged stricter semantic ingestion guards.

### Unresolved Issues

None. Both exact-head CI runs passed and exact configured model metadata was confirmed read-only. No live retry or provider verification was performed by this agent.

### Architectural Concerns

None requiring cross-owner changes. No bound/schema-subset gap was found for the observed non-fine-tuned model.

## Architect Review

### Review Status

Pending

### Review Notes

Pending exact source review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
