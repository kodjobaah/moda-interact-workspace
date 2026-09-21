# ARCH-020 commerce tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_commerce. Repository: moda-interact-commerce. Coordinator: moda_architect.

COMMERCE-001 is architect-accepted Complete at Attempt 3 (`d7c1c65`). The descendant-process cleanup correction passed focused functional validation; prior real Docker PostgreSQL/Redis readiness evidence is retained. COMMERCE-002 is architect-accepted Complete at Attempt 2 (`fb3362e`): development HTTP mutations and revoked-session recovery are corrected. Live Google OAuth remains developer-owned deployment validation. Downstream source consumption awaits developer integration or explicit accepted-commit approval; no task is promoted or launched. COMMERCE-001 remains accepted and integrated. Other task rows retain this branch snapshot; canonical task worktrees remain authoritative.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-COMMERCE-001](COMMERCE-001-establish-the-next-js-service-and-nested-database-submodule.md) | Establish the Next.js service and nested database submodule | complete | — |
| [ARCH-020-COMMERCE-002](COMMERCE-002-authenticate-team-access-to-commerceagent-studio.md) | Authenticate team access to CommerceAgent Studio | complete | ARCH-020-COMMERCE-001 |
| [ARCH-020-COMMERCE-003](COMMERCE-003-implement-draft-and-release-publication-lifecycle.md) | Implement draft and release publication lifecycle | ready | ARCH-020-COMMERCE-002, ARCH-020-DATABASE-001, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-004](COMMERCE-004-serve-authorised-mcp-capability-bundles.md) | Serve authorised MCP capability bundles | pending | ARCH-020-COMMERCE-003, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-005](COMMERCE-005-implement-basket-and-product-discovery-tools.md) | Implement basket and product discovery tools | pending | ARCH-020-COMMERCE-004, ARCH-020-COMMERCE-011 |
| [ARCH-020-COMMERCE-006](COMMERCE-006-evaluate-permitted-shopify-discount-rules.md) | Evaluate permitted Shopify discount rules | pending | ARCH-020-COMMERCE-005, ARCH-016-BACKGROUND-001, ARCH-016-DATABASE-001 |
| [ARCH-020-COMMERCE-007](COMMERCE-007-recommend-qualifying-and-similar-products.md) | Recommend qualifying and similar products | pending | ARCH-020-COMMERCE-006 |
| [ARCH-020-COMMERCE-008](COMMERCE-008-build-capability-authoring-and-release-screens.md) | Build capability authoring and release screens | ready | ARCH-020-COMMERCE-002, ARCH-020-DATABASE-001, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-009](COMMERCE-009-preview-capabilities-in-an-isolated-conversation-sandbox.md) | Preview capabilities in an isolated conversation sandbox | pending | ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-007, ARCH-020-SHARED-001, ARCH-020-COMMERCE-013 |
| [ARCH-020-COMMERCE-010](COMMERCE-010-instrument-capability-operations-and-preview-isolation.md) | Instrument capability operations and preview isolation | pending | ARCH-020-COMMERCE-004, ARCH-020-COMMERCE-007, ARCH-020-COMMERCE-009 |
| [ARCH-020-COMMERCE-011](COMMERCE-011-provide-integrated-shopify-discovery-and-schema-validation.md) | Provide integrated Shopify discovery and schema validation | pending | ARCH-020-COMMERCE-002, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-012](COMMERCE-012-add-frequency-based-tool-result-caching.md) | Frequency-based tool-result caching; final implementation feature, readiness checkpoint outstanding | pending | All other ARCH-020 implementation tasks |
| [ARCH-020-COMMERCE-013](COMMERCE-013-integrate-publication-and-studio-with-real-commerce-services.md) | Connect real services and verify integrated U01–U13 flows | pending | ARCH-020-COMMERCE-003, ARCH-020-COMMERCE-004, ARCH-020-COMMERCE-005, ARCH-020-COMMERCE-006, ARCH-020-COMMERCE-007, ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-011 |

2026-09-21: COMMERCE-003/008 promoted Ready for C17 interface-based parallel work.
Component acceptance uses C17 fixtures;013 separately owns real integration. This
supersedes earlier no-promotion wording for these two tasks only.011 active task
worktree status remains authoritative. No task was claimed by this amendment.

## COMMERCE-008 Attempt 1 — Changes Requested — 2026-09-21

COMMERCE-008 is **Ready, Attempt 1 retained**, claim cleared, not accepted.
Reviewed implementation `865e16c` and report `a6df81c1`. Authenticated shell and
route scaffolding exist, but C17 StudioServices ports, authoring workflows,
record resolution and required navigation behavior remain unimplemented.
The task's latest Architect Review records R1–R3. Component/fixture behavior and
local browser evidence remain008-owned; real provider composition remains013-owned.
Readiness uses002, DATABASE-001 and SHARED-001, not the superseded service chain.
No new claim, downstream promotion, implementation edit or main integration.
Other canonical task states remain authoritative; ARCH-020 is not complete.

## COMMERCE-008 Attempt 2 — Changes Requested — 2026-09-21

COMMERCE-008 is **Ready, Attempt 2 retained**, claim cleared, not accepted.
Reviewed `6c4ecbc` / report `10fc0ae6` (PR3/171). Typed unavailable/not-found states
and shell improvements are retained. Remaining blockers are canonical port/data
mismatches, incomplete connected authoring/release workflows, unsafe unknown-outcome
retry, and exact-revision/navigation behavior. Latest task review records R1–R4.
C17 still allows fixture component acceptance; real adapters and readiness timing
failures are not the blocker. No new claim, downstream promotion, implementation
edit or main integration. Other task states remain unchanged.
