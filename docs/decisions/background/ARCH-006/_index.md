# ARCH-006 Background Tasks

Architecture: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Assigned Agent: `moda_background`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| BACKGROUND-001 | Implement the OpenAI Batch translation provider adapter | Complete | DATABASE-002, SHARED-002 |
| BACKGROUND-002 | Implement versioned merchant system notifications | Superseded | — |
| BACKGROUND-003 | Extend queue telemetry to merchant-communications | Superseded | — |
| BACKGROUND-004 | Assemble pending translations into durable logical batches | Complete | BACKGROUND-001, SHARED-004 |
| BACKGROUND-005 | Submit each logical translation Batch to OpenAI at most once | Complete | BACKGROUND-004 |
| BACKGROUND-006 | Poll OpenAI batches in minutes and apply translation results idempotently | Complete | BACKGROUND-005 |
| BACKGROUND-007 | Add self-healing translation reconciliation and worker runtime | Complete | BACKGROUND-006 |
| BACKGROUND-008 | Adopt disposable integration-test infrastructure in Background | Complete | BACKGROUND-004, SHARED-006 |
| BACKGROUND-009 | Correct PostgreSQL enum parameter bindings in translation lifecycle | **Review — Attempt 1** | BACKGROUND-005, BACKGROUND-006, BACKGROUND-007, BACKGROUND-008 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
The individual task file YAML metadata is authoritative.

Architect state: BACKGROUND-004, BACKGROUND-005, BACKGROUND-006, BACKGROUND-007 and BACKGROUND-008 are architect-accepted Complete. Repository agents must execute one task per invocation, return only their owned task to `review`, and STOP.

Architect coordination on 2026-09-06: BACKGROUND-007 Attempt 3 is independently accepted after replacing the final unbounded continuation aggregate with an indexed bounded existence probe. GATEWAY-001, ADMIN-002, ADMIN-004 and SHOPIFY-003 may now move to Ready where their complete dependency sets are satisfied. System-test tasks remain terminal/manual-gated and are not auto-started.


Architect coordination on 2026-09-07: live manual translation validation exposed
PostgreSQL SQLSTATE `42804` in `TranslationBatchSubmitService.persistFailure()` because
a Prisma-bound JavaScript `text` status was written directly to
`support."MerchantTranslationBatchStatus"`. Independent source/schema inspection found
the same defect class in five dynamic enum-bound writes across submit, poll, results
and reconciliation. `BACKGROUND-009` is Ready to correct exactly those five bindings
and add generated-SQL plus disposable PostgreSQL regression coverage.

The previously accepted BACKGROUND-005/006/007 designs remain authoritative. This is a
post-acceptance runtime correction, not a redesign.

ARCH-006 system tests remain terminal/manual-gated and must not be invoked until
BACKGROUND-009 is architect-accepted Complete.
