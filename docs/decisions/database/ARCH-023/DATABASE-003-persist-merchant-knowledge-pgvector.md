---
id: ARCH-023-DATABASE-003
architecture_id: ARCH-023
title: Persist Merchant Knowledge and pgvector chunks
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 12
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-023-SHOPIFY-003
  - ARCH-023-BACKGROUND-003
  - ARCH-023-COMMERCE-002
  - ARCH-023-GATEWAY-001
  - ARCH-023-SYSTEM-TEST-002
created: 2026-09-27
updated: 2026-09-27
---

# Persist Merchant Knowledge and pgvector chunks

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Add the durable shop-scoped Merchant Knowledge entry/source/revision/chunk model and pgvector storage required for asynchronous ingestion and exact per-shop semantic retrieval.

## Context

PostgreSQL is the durable source of truth. The developer has verified pgvector support in the target installation. Redis remains queue/reconciliation infrastructure and is not the v1 vector database.

## Scope

- Create/ensure the pgvector extension in the canonical migration.
- Add Merchant Knowledge purpose and revision-status enums.
- Add `MerchantKnowledgeEntry`, `MerchantKnowledgeSource`, `MerchantKnowledgeSourceRevision`, and `MerchantKnowledgeChunk`.
- Persist both latest-requested and active revision identity on each locale source so stale workers cannot promote old revisions.
- Store extracted content/content units/fetch metadata/embedding provenance on revisions and chunk text/content units/vector data on chunks.
- Add tenant/retrieval indexes for shop, position, purpose, source locale, revision status and active/latest identities.

## Out of Scope

- HNSW/IVFFlat indexes.
- Redis vector storage.
- URL fetching, embeddings or query execution.
- Plan entitlement configuration.

## Requirements

- Entry position is unique within a shop and positive/deterministic.
- One source exists per `(entryId, languageTag)`.
- Revision number is unique per source.
- Chunk ordinal is unique per revision.
- A source has nullable `latestRevisionId` and `activeRevisionId`; they may differ while refresh/replacement is processing.
- The vector column supports the configured embedding dimensions without forcing a database catalogue of embedding models.
- Revision provenance records `embeddingProvider`, `embeddingModel`, `embeddingDimensions`, and `embeddingIndexVersion`.
- Shop deletion cascades through all Merchant Knowledge rows.
- No approximate global vector index is created in v1.

## Work Items

- [ ] Update Prisma schema and migration including `CREATE EXTENSION IF NOT EXISTS vector`.
- [ ] Add fresh/upgrade schema validation and pgvector smoke fixture.
- [ ] Add relation/uniqueness/index/active-vs-latest fixtures.

## Interfaces / Contracts

Consumed by Shopify configuration, Background ingestion/reconciliation and Commerce lookup. `ARCH-023-SHARED-002` owns purpose/config/job/content-unit contracts.

## Dependencies

None

## Enables

- ARCH-023-SHOPIFY-003
- ARCH-023-BACKGROUND-003
- ARCH-023-COMMERCE-002
- ARCH-023-GATEWAY-001
- ARCH-023-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] pgvector storage and exact distance query work in database validation.
- [ ] Two locale sources may belong to one logical entry without consuming extra entry rows.
- [ ] Creating a new latest revision does not change active revision.
- [ ] Stale revision promotion can be detected using durable latest identity.
- [ ] Shop cascade removes entries, sources, revisions and chunks.

## Validation

- [ ] Prisma validation/generation.
- [ ] Fresh migration validation including vector extension.
- [ ] Upgrade migration validation.
- [ ] Focused pgvector/relation fixtures and `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

If Prisma models the vector field as an unsupported native type, use repository-standard migration/raw-SQL validation rather than inventing a second vector store.

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
