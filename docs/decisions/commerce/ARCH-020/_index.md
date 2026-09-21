# ARCH-020 commerce tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_commerce. Repository: moda-interact-commerce. Coordinator: moda_architect.

COMMERCE-001 is architect-accepted Complete at Attempt 3 (`d7c1c65`). The descendant-process cleanup correction passed focused functional validation; prior real Docker PostgreSQL/Redis readiness evidence is retained. COMMERCE-002 is architect-accepted Complete at Attempt 2 (`fb3362e`): development HTTP mutations and revoked-session recovery are corrected. Live Google OAuth remains developer-owned deployment validation. Downstream source consumption awaits developer integration or explicit accepted-commit approval; no task is promoted or launched. COMMERCE-001 remains accepted and integrated. Other task rows retain this branch snapshot; canonical task worktrees remain authoritative.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-COMMERCE-001](COMMERCE-001-establish-the-next-js-service-and-nested-database-submodule.md) | Establish the Next.js service and nested database submodule | complete | — |
| [ARCH-020-COMMERCE-002](COMMERCE-002-authenticate-team-access-to-commerceagent-studio.md) | Authenticate team access to CommerceAgent Studio | complete | ARCH-020-COMMERCE-001 |
| [ARCH-020-COMMERCE-003](COMMERCE-003-implement-draft-and-release-publication-lifecycle.md) | Implement draft and release publication lifecycle | ready | ARCH-020-COMMERCE-002, ARCH-020-DATABASE-001, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-004](COMMERCE-004-serve-authorised-mcp-capability-bundles.md) | Authenticate MCP requests and resolve immutable grants | pending | ARCH-020-COMMERCE-003, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-005](COMMERCE-005-implement-basket-and-product-discovery-tools.md) | Execute validated public Shopify queries | ready | ARCH-020-COMMERCE-001, ARCH-020-COMMERCE-011, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-006](COMMERCE-006-evaluate-permitted-shopify-discount-rules.md) | Read merchant discount policy and normalise Shopify rules | ready | ARCH-020-COMMERCE-001, ARCH-020-DATABASE-001, ARCH-020-SHARED-001, ARCH-016-BACKGROUND-001, ARCH-016-DATABASE-001 |
| [ARCH-020-COMMERCE-007](COMMERCE-007-recommend-qualifying-and-similar-products.md) | Recommend qualifying and similar products | pending | ARCH-020-COMMERCE-016, ARCH-020-COMMERCE-015 |
| [ARCH-020-COMMERCE-008](COMMERCE-008-build-capability-authoring-and-release-screens.md) | Build capability authoring and release screens | ready | ARCH-020-COMMERCE-002, ARCH-020-DATABASE-001, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-009](COMMERCE-009-preview-capabilities-in-an-isolated-conversation-sandbox.md) | Implement isolated preview lifecycle and execution service | ready | ARCH-020-COMMERCE-002, ARCH-020-SHARED-001, ARCH-020-COMMERCE-001 |
| [ARCH-020-COMMERCE-010](COMMERCE-010-instrument-capability-operations-and-preview-isolation.md) | Instrument capability operations and preview isolation | pending | ARCH-020-COMMERCE-004, ARCH-020-COMMERCE-007, ARCH-020-COMMERCE-009 |
| [ARCH-020-COMMERCE-011](COMMERCE-011-provide-integrated-shopify-discovery-and-schema-validation.md) | Provide integrated Shopify discovery and schema validation | complete | ARCH-020-COMMERCE-002, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-012](COMMERCE-012-add-frequency-based-tool-result-caching.md) | Frequency-based tool-result caching; final implementation feature, readiness checkpoint outstanding | pending | All other ARCH-020 implementation tasks |
| [ARCH-020-COMMERCE-013](COMMERCE-013-integrate-publication-and-studio-with-real-commerce-services.md) | Integrate publication and Studio with real Commerce services | pending | ARCH-020-COMMERCE-003, ARCH-020-COMMERCE-004, ARCH-020-COMMERCE-005, ARCH-020-COMMERCE-006, ARCH-020-COMMERCE-007, ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-011, ARCH-020-COMMERCE-014, ARCH-020-COMMERCE-015, ARCH-020-COMMERCE-016, ARCH-020-COMMERCE-009, ARCH-020-COMMERCE-017 |
| [ARCH-020-COMMERCE-014](COMMERCE-014-execute-and-render-pinned-tool-definitions.md) | Execute and render pinned tool definitions | pending | ARCH-020-COMMERCE-004, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-015](COMMERCE-015-provide-trusted-basket-and-product-policy-adapters.md) | Provide trusted basket and product policy adapters | ready | ARCH-020-COMMERCE-001, ARCH-020-DATABASE-001, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-016](COMMERCE-016-evaluate-normalised-discount-rules-and-produce-evidence.md) | Evaluate normalised discount rules and produce evidence | pending | ARCH-020-COMMERCE-006, ARCH-020-COMMERCE-015, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-017](COMMERCE-017-build-the-u14-preview-frontend.md) | Build the U14 preview frontend | pending | ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-002, ARCH-020-SHARED-001 |

2026-09-21: COMMERCE-003/008 promoted Ready for C17 interface-based parallel work.
Component acceptance uses C17 fixtures;013 separately owns real integration. This
supersedes earlier no-promotion wording for these two tasks only.011 active task
worktree status remains authoritative. No task was claimed by this amendment.

2026-09-21 C19 split:004 transport/014 executor,005 queries/015 basket-products,
006 rule reader/016 evaluator,009 backend/017 U14 frontend.013 owns real pairing.
006/009/015 are newly Ready from accepted prerequisites; no task was launched.

## COMMERCE-011 Attempt 9 accepted — 2026-09-21

COMMERCE-011 is **Complete, architect accepted, Attempt 9 retained**, claim cleared.
Reviewed implementation `1176412` and report `ccb35ea3`; clean dedicated worktrees
and matching remote heads verified. R8-1 inline text order is fixed; all four prior
review reproductions and 38 focused checks passed independently. Submitted full
suite remains 117/119 with two existing readiness timing failures in unchanged
code; no green full-suite or live Redis claim is made. Live Redis/OAuth/Shopify/
deployment checks remain developer-owned and pending. COMMERCE-005 is promoted
Ready (001/011/Shared Complete), with no new claim. Other dependants retain current
states because prerequisites remain unresolved. No main merge or gitlink update;
architecture is not Implemented. This supersedes older COMMERCE-011 current-state
wording while preserving historical reviews.
