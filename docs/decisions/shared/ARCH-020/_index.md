# ARCH-020 shared tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_shared. Repository: moda-interact-shared. Coordinator: moda_architect.

Individual task YAML is authoritative. Attempt 2 is architect-accepted Complete on 2026-09-20, with no active claim. Verified package 0.13.1 is the accepted consumer artifact; it supersedes 0.13.0. Shared implementation and publication are combined in SHARED-001; completion requires a verified registry version containing both exports.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-SHARED-001](SHARED-001-define-commerce-capability-and-evidence-contracts.md) | Implement and publish commerce contracts and reusable runner | complete (Accepted, Attempt 2) | ARCH-016-SHARED-001 |
| [ARCH-020-SHARED-002](SHARED-002-publish-external-http-and-response-processing-contracts.md) | Publish external HTTP and response-processing contracts | ready | ARCH-020-SHARED-001 |
