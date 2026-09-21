# ARCH-020 database tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_database. Repository: moda-interact-database. Coordinator: moda_architect.

Individual task YAML is authoritative. DATABASE-001 Attempt 2 is Accepted / Complete; R1 and R2 are closed. Its claim is cleared. Other prerequisites keep downstream tasks pending.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-DATABASE-001](DATABASE-001-persist-capability-releases-and-turn-revision-pins.md) | Persist capability releases and conversation tool grants | complete | ARCH-016-DATABASE-001 |
| [ARCH-020-DATABASE-003](DATABASE-003-persist-external-api-connections-and-credentials.md) | Persist external API connections and encrypted credentials | ready | ARCH-020-DATABASE-001 |

### DATABASE-003 Attempt 1 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 1 retained; executor/claim null.** Reviewed
implementation `a96dfd7` and report `cee29108`. A1-R1 aligns six Prisma timestamp
fields with the required timestamptz(3) migration; A1-R2 repairs missing updatedAt
fixture values; A1-R3 makes constraint/immutability/rollback assertions specific
and proves existing tool/grant data preservation. Explicit corrections are in the
database task Architect Review. Syntax and Prisma validation pass; offline schema
SQL confirms timestamp drift. Real fresh/upgrade PostgreSQL evidence remains
unrun and is directly owned by this migration task. No acceptance, implementation
change, main merge, gitlink update or downstream promotion. COMMERCE-020/028 remain
gated on their actual dependencies; no automatic launch.
