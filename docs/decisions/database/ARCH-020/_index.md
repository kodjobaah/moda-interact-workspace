# ARCH-020 database tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_database. Repository: moda-interact-database. Coordinator: moda_architect.

Individual task YAML is authoritative. DATABASE-001 Attempt 2 is Accepted / Complete; R1 and R2 are closed. Its claim is cleared. Other prerequisites keep downstream tasks pending.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-DATABASE-001](DATABASE-001-persist-capability-releases-and-turn-revision-pins.md) | Persist capability releases and conversation tool grants | complete | ARCH-016-DATABASE-001 |


## New-scope coordination: phone-country language provenance

BACKGROUND-001 amendment A1 requires honest phone-country provenance (C6.2). Shared owns the new wire source/validators and publication; Database owns the persisted PHONE_COUNTRY enum addition. Current accepted contracts lack this value. Architect must materialise separate new-scope owner work and dependency gates before expanded Background execution; do not reopen or relabel accepted SHARED-001/DATABASE-001 as defective. No implementation is assigned or claimed by this coordination note.
