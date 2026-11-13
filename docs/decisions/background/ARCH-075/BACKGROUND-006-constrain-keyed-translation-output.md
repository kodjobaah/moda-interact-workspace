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
status: ready
priority: 5
executor: null
claimed_at: null
attempt: 0
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

- [ ] Reproduce missing provider output contract and extra-field refusal with synthetic fixture.
- [ ] Add strict keyed provider schema using supported installed SDK/model contract.
- [ ] Complete focused/regression/exact-head validation, mirrored report and stop.

## Interfaces / Contracts

Existing local keyed translation ResultSchema and Responses Batch /v1/responses request. Official OpenAI guide https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses establishes strict text.format/json_schema and Batch support; exact selected model/SDK compatibility must be verified. No new Shared version.

## Dependencies

ARCH-075-BACKGROUND-005; ARCH-075-SHARED-004

## Enables

ARCH-075-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Actual prepared Batch JSONL keyed request carries strict exact result JSON schema; generic translation remains unchanged.
- [ ] Extra protectedTokens/context/unknown fields still fail ingestion; marker/key/hash/truncation/refusal/error boundaries stay strict.
- [ ] Official model/SDK evidence, canonical isolation and passing exact checks reported, no live mutation.

## Validation

- [ ] Red/green actual provider JSONL payload/schema tests; valid strict output and echoed metadata rejection through actual codec/worker; existing translation provider regressions.
- [ ] Declared relevant focused tests, typecheck/scoped lint and exact-head full CI; no unnecessary persistence/schema tests.
- [ ] Diff/privacy hygiene and no dependency/model/provider change or real request.

## Stop Condition

After scope and required checks complete, set review, submit mirrored Completion Report and STOP. No dependent implementation or live action.

## Implementation Notes

You are not alone; preserve other changes. Canonical prepared packet owns startup/claim. Existing accepted tasks must not be rewritten. Root owns merges and live verification.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

None beyond supported official provider contract.

### Unresolved Issues

None currently.

### Architectural Concerns

Return actual missing primitive/contract before widening scope.

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
