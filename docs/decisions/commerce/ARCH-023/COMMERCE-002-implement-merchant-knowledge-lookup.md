---
id: ARCH-023-COMMERCE-002
architecture_id: ARCH-023
title: Implement Merchant Knowledge lookup
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 31
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-DATABASE-003
  - ARCH-023-SHARED-004
enables:
  - ARCH-023-GATEWAY-001
  - ARCH-023-SYSTEM-TEST-002
created: 2026-09-27
updated: 2026-09-27
---

# Implement Merchant Knowledge lookup

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Add the feature-bound Merchant Knowledge runtime lookup operation that embeds the agent query with the platform embedding model and performs exact pgvector ranking only inside the authenticated shop's currently entitled knowledge scope.

## Context

One global `merchant_knowledge` Commerce capability is authored/published through normal Studio operations. Merchant entries are data for that capability, not capabilities themselves. Any active capability in the same turn may benefit from lookup results, but knowledge never expands authority.

## Scope

- Add the closed policy/tool operation `merchantKnowledge.lookup` (or architecture-equivalent canonical operation) to the Commerce runtime/authoring registry.
- Accept only bounded agent-controlled query/purpose filters; never accept `shopId` or language from the LLM.
- Resolve trusted shop, current `merchant_knowledge` feature configuration/eligibility, first-N entry positions, and shop default language with English fallback.
- Select active source revision for the resolved shop language, generate query embedding using the same `EMBEDDING_*` model/version configuration as Background, and fail closed on provenance mismatch.
- Execute parameterized exact pgvector distance over the small relationally filtered candidate set; return bounded top matches as untrusted tool data.
- Add capability-local instructions/description clarifying factual-reference-only semantics without granting actions.

## Out of Scope

- Creating/publishing the capability/release automatically.
- URL ingestion.
- Redis vector search.
- Customer-language-driven source selection.

## Requirements

- Tenant id comes only from authenticated runtime context.
- Feature/plan/preference eligibility is re-evaluated server-side before lookup.
- Entries beyond `maxKnowledgeEntries` are excluded by deterministic position before semantic ranking.
- Purpose narrows retrieval but grants no authority.
- Only chunks whose active revision embedding provenance matches current `EMBEDDING_PROVIDER/MODEL/DIMENSIONS/INDEX_VERSION` are comparable.
- Query/result sizes and top-K are bounded.
- Tool result is context data, never appended as trusted instructions.

## Work Items

- [ ] Add policy operation/registry and authorization adapter.
- [ ] Add embedding provider adapter/config validation.
- [ ] Implement relational filtering + exact pgvector query and bounded result shaping.
- [ ] Add cross-shop/plan-downgrade/language-fallback/provenance/prompt-injection/multilingual semantic tests.

## Interfaces / Contracts

Consumes ARCH-023-DATABASE-001/003 and ARCH-023-SHARED-002/003 via published Shared package. Deployment env wiring is ARCH-023-GATEWAY-001.

## Dependencies

- ARCH-023-DATABASE-001
- ARCH-023-DATABASE-003
- ARCH-023-SHARED-004

## Enables

- ARCH-023-GATEWAY-001
- ARCH-023-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Cross-shop data cannot be retrieved even with malicious query text.
- [ ] Downgraded excess entries are excluded without deletion.
- [ ] French shop knowledge can answer an English customer query through multilingual embeddings while response language remains independently resolved.
- [ ] Knowledge text cannot grant an ungranted action/tool.

## Validation

- [ ] Focused policy/registry/authorization/pgvector tests.
- [ ] Embedding adapter/config tests.
- [ ] Production runtime integration tests with real PostgreSQL pgvector where repository convention permits.
- [ ] Lint/typecheck/build as declared.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

None

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

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending.

### Follow-up

None
