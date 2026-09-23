# ARCH-021 Database Tasks

Architecture:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Assigned Agent:

`moda_database`

Coordinator:

`moda_architect`

## Phase 2 — durable CommerceAgent configuration

Phase 2 database work is intentionally one cohesive task so model catalogue/selections,
prompt-template taxonomy/versioning, prompt lineages/revisions and active pointers are designed
and migrated together.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [DATABASE-001](DATABASE-001-persist-agent-configuration-schema.md) | Persist complete Phase 2 model/prompt/template configuration schema | Ready | ARCH-020-DATABASE-001 |

## Template classification

Prompt-template categories are data-driven platform records, not an enum. A category such as
`Clothing & Fashion` can contain multiple templates; every template belongs to exactly one
category. Platform admins may later create/update display metadata/disable categories through the
Commerce service/UI without a database schema change; the stable category slug/identity is not renamed.

## Execution frontier

The single Phase 2 Database task is immediately executable:

```text
ARCH-021-DATABASE-001   complete Phase 2 CommerceAgent configuration schema
```

After architect acceptance, COMMERCE-007 and COMMERCE-008 may proceed in parallel because their
durable prerequisites will exist. COMMERCE-009 remains gated on architect acceptance of COMMERCE-008
because prompt copy-on-use consumes the template service.
