# ARCH-020 commerce tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_commerce. Repository: moda-interact-commerce. Coordinator: moda_architect.

Definitions are on local main for review by explicit developer request. Individual task YAML is authoritative; no task is claimed or launched. Commerce repository/submodule provisioning is complete; COMMERCE-001 is Ready and remains unclaimed. See the implementation handoff for verified evidence.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-COMMERCE-001](COMMERCE-001-establish-the-next-js-service-and-nested-database-submodule.md) | Establish the Next.js service and nested database submodule | ready | — |
| [ARCH-020-COMMERCE-002](COMMERCE-002-authenticate-team-access-to-commerceagent-studio.md) | Authenticate team access to CommerceAgent Studio | pending | ARCH-020-COMMERCE-001 |
| [ARCH-020-COMMERCE-003](COMMERCE-003-implement-draft-and-release-publication-lifecycle.md) | Implement draft and release publication lifecycle | pending | ARCH-020-COMMERCE-002, ARCH-020-DATABASE-001, ARCH-020-SHARED-003, ARCH-020-COMMERCE-011 |
| [ARCH-020-COMMERCE-004](COMMERCE-004-serve-authorised-mcp-capability-bundles.md) | Serve authorised MCP capability bundles | pending | ARCH-020-COMMERCE-003, ARCH-020-SHARED-003 |
| [ARCH-020-COMMERCE-005](COMMERCE-005-implement-basket-and-product-discovery-tools.md) | Implement basket and product discovery tools | pending | ARCH-020-COMMERCE-004, ARCH-020-COMMERCE-011 |
| [ARCH-020-COMMERCE-006](COMMERCE-006-evaluate-permitted-shopify-discount-rules.md) | Evaluate permitted Shopify discount rules | pending | ARCH-020-COMMERCE-005, ARCH-016-BACKGROUND-001, ARCH-016-DATABASE-001 |
| [ARCH-020-COMMERCE-007](COMMERCE-007-recommend-qualifying-and-similar-products.md) | Recommend qualifying and similar products | pending | ARCH-020-COMMERCE-006 |
| [ARCH-020-COMMERCE-008](COMMERCE-008-build-capability-authoring-and-release-screens.md) | Build capability authoring and release screens | pending | ARCH-020-COMMERCE-003, ARCH-020-COMMERCE-005, ARCH-020-COMMERCE-006, ARCH-020-COMMERCE-007, ARCH-020-COMMERCE-011 |
| [ARCH-020-COMMERCE-009](COMMERCE-009-preview-capabilities-in-an-isolated-conversation-sandbox.md) | Preview capabilities in an isolated conversation sandbox | pending | ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-007, ARCH-020-SHARED-003 |
| [ARCH-020-COMMERCE-010](COMMERCE-010-instrument-capability-operations-and-preview-isolation.md) | Instrument capability operations and preview isolation | pending | ARCH-020-COMMERCE-004, ARCH-020-COMMERCE-007, ARCH-020-COMMERCE-009 |
| [ARCH-020-COMMERCE-011](COMMERCE-011-provide-integrated-shopify-discovery-and-schema-validation.md) | Provide integrated Shopify discovery and schema validation | pending | ARCH-020-COMMERCE-002, ARCH-020-SHARED-003 |
