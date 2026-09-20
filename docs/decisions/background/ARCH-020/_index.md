# ARCH-020 background tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_background. Repository: moda-interact-background. Coordinator: moda_architect.

Definitions are on local main for review by explicit developer request. Individual task YAML is authoritative; no task is claimed or launched. Commerce submodule provisioning remains a prerequisite; the owner and route are defined in this packet.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-BACKGROUND-001](BACKGROUND-001-integrate-the-generic-mcp-commerceagent-host.md) | Integrate the generic MCP CommerceAgent host | pending | ARCH-016-BACKGROUND-003, ARCH-020-SHARED-001, ARCH-020-DATABASE-001, ARCH-020-COMMERCE-001 |
| [ARCH-020-BACKGROUND-002](BACKGROUND-002-preserve-turn-safeguards-and-validate-offer-replies.md) | Preserve turn safeguards and validate offer replies | pending | ARCH-020-BACKGROUND-001, ARCH-020-COMMERCE-007 |
