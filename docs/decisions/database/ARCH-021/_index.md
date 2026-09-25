# ARCH-021 Database Tasks

Architecture:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Assigned Agent:

`moda_database`

Coordinator:

`moda_architect`

## Phase 2 — durable CommerceAgent configuration

Phase 2 database work is intentionally one cohesive deterministic task. `DATABASE-001` fixes the exact Prisma model names, fields, FKs, indexes, SQL guards, migration directory, validation scripts and audit actions for model catalogue/selections, prompt-template taxonomy/versioning, prompt lineages/revisions and active pointers. It also fixes generation-aware shop-override CAS identity, blank-DRAFT/non-blank-publication rules and the existing `CommerceAuditEvent` operation-receipt convention consumed by later Commerce services. The implementing agent must not redesign that schema.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [DATABASE-001](DATABASE-001-persist-agent-configuration-schema.md) | Persist complete Phase 2 model/prompt/template configuration schema | Complete | ARCH-020-DATABASE-001 |

## Template classification

Prompt-template categories are data-driven platform records, not an enum. A category such as
`Clothing & Fashion` can contain multiple templates; every template belongs to exactly one
category. Platform admins may later create/update display metadata/disable categories through the
Commerce service/UI without a database schema change; the stable category slug/identity is not renamed.

## Execution frontier

DATABASE-001 Attempt 3 is architect-accepted Complete after successful PostgreSQL 15 fresh/upgrade rehearsals for ARCH-021 and predecessor ARCH-020 compatibility. The single-migration SQLSTATE `55P04` correction is proven, all 24 ARCH-021 behavioral cases pass in both fresh and upgrade modes, and the predecessor ARCH-020 upgrade preserves 217 indexes unchanged while completing all 298 behavioral cases.

The Database domain has no remaining executable Phase 2 task:

```text
ARCH-021-DATABASE-001   Complete
```

COMMERCE-007 and COMMERCE-008 are now independently Ready because their durable prerequisite exists. COMMERCE-009 remains gated on architect acceptance of COMMERCE-008 because prompt copy-on-use consumes the template service.


## Pre-Phase-3 simplification checkpoint — 2026-09-24

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [DATABASE-002](DATABASE-002-collapse-agent-configuration-and-add-merchant-studio-access.md) | Collapse Agent Configuration persistence, retain template categories, add merchant Studio access | Complete | DATABASE-001 |

DATABASE-002 Attempt 2 is architect-accepted Complete. The executable fresh and seeded-upgrade PostgreSQL rehearsals prove the simplified schema, exact Phase-2 backfills, migration-local immutability-trigger handling, final prompt/merchant guards, restored audit immutability and removal of the five obsolete persistence tables.

The Database checkpoint has no remaining executable task. `ARCH-021-COMMERCE-025`, `ARCH-021-COMMERCE-026` and `ARCH-021-COMMERCE-027` are now Ready.
