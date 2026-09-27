---
id: ARCH-023-BACKGROUND-003
architecture_id: ARCH-023
title: Process Merchant Knowledge sources
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 32
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-DATABASE-003
  - ARCH-023-SHARED-004
enables:
  - ARCH-023-BACKGROUND-004
  - ARCH-023-GATEWAY-001
  - ARCH-023-SYSTEM-TEST-002
created: 2026-09-27
updated: 2026-09-27
---

# Process Merchant Knowledge sources

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Implement the asynchronous Merchant Knowledge worker that safely fetches public pages, normalises/caps/chunks content, generates multilingual embeddings and atomically promotes successful source revisions.

## Context

Background owns ingestion and writes PostgreSQL directly. There is no Background-to-Commerce ingestion call. The worker uses one deployment-configured embedding model shared with Commerce.

## Scope

- Add Merchant Knowledge queue consumer/service and dedicated worker entrypoint/readiness identity.
- Validate process job against authoritative latest revision/shop ownership/current feature configuration.
- Implement SSRF-safe HTTPS fetch with DNS and redirect revalidation, bounded redirects/timeouts/bytes, and only `text/html`/`text/plain`.
- Extract/strip executable markup, normalize text using Shared content-unit rules, truncate safely at `maxContentUnitsPerLocaleSource`, and record truncation.
- Deterministically chunk at architecture target (about 300 units with bounded overlap).
- Generate embeddings using `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`, `EMBEDDING_INDEX_VERSION`, and server-side credential configuration.
- Persist revision content/provenance/chunks/vectors and promote active revision only if it is still the source latest revision.

## Out of Scope

- Commerce runtime lookup.
- Headless browser/JavaScript rendering.
- Scheduled page refresh.
- Redis vector indexing.

## Requirements

- Reject loopback/private/link-local/metadata/non-public destinations for initial URL, DNS answers and every redirect.
- Never send Moda secrets/auth headers to merchant URLs.
- Provider/model/dimension/index version written to revision provenance.
- Stale older job cannot overwrite a newer latest revision.
- Any fetch/extract/embed/persist failure leaves prior active revision unchanged.
- Logs never include page bodies or vectors.

## Work Items

- [ ] Add worker/entrypoint/config validation.
- [ ] Implement safe fetch/extraction/chunk/embed/persist pipeline.
- [ ] Add SSRF/redirect/content-type/size/timeout/truncation/multilingual/stale-job/provider-failure tests.
- [ ] Add readiness/structured domain logging using Shared logger.

## Interfaces / Contracts

Consumes ARCH-023-SHARED-002 process contract and ARCH-023-DATABASE-003 models; deployment wiring is ARCH-023-GATEWAY-001.

## Dependencies

- ARCH-023-DATABASE-001
- ARCH-023-DATABASE-003
- ARCH-023-SHARED-004

## Enables

- ARCH-023-BACKGROUND-004
- ARCH-023-GATEWAY-001
- ARCH-023-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Valid HTML/plain source reaches ACTIVE with complete chunks/vectors.
- [ ] Unsafe URL/redirect never makes a network request to denied target.
- [ ] Embedding failure leaves old active revision usable.
- [ ] A stale revision job cannot promote after a later revision is requested.
- [ ] Stored vector dimensions/version match configured environment.

## Validation

- [ ] Focused unit tests including network-policy fixtures.
- [ ] Database/pgvector integration tests.
- [ ] Worker entrypoint/readiness test.
- [ ] Build/typecheck/lint as declared.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

Use a multilingual embedding model, but do not hard-code its model id in source. Environment configuration is platform-wide.

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
