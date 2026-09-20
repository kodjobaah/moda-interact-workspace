# ARCH-020 shared tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_shared. Repository: moda-interact-shared. Coordinator: moda_architect.

Individual task YAML is authoritative. Attempt 2 is architect-accepted Complete on 2026-09-20, with no active claim. Verified package 0.13.1 is the accepted consumer artifact; it supersedes 0.13.0. Shared implementation and publication are combined in SHARED-001; completion requires a verified registry version containing both exports.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-SHARED-001](SHARED-001-define-commerce-capability-and-evidence-contracts.md) | Implement and publish commerce contracts and reusable runner | complete (Accepted, Attempt 2) | ARCH-016-SHARED-001 |


## New-scope coordination: phone-country language provenance

BACKGROUND-001 amendment A1 requires honest phone-country provenance (C6.2). Shared owns the new wire source/validators and publication; Database owns the persisted PHONE_COUNTRY enum addition. Current accepted contracts lack this value. Architect must materialise separate new-scope owner work and dependency gates before expanded Background execution; do not reopen or relabel accepted SHARED-001/DATABASE-001 as defective. No implementation is assigned or claimed by this coordination note.
