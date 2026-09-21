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
| [ARCH-020-COMMERCE-011](COMMERCE-011-provide-integrated-shopify-discovery-and-schema-validation.md) | Provide integrated Shopify discovery and schema validation | ready | ARCH-020-COMMERCE-002, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-012](COMMERCE-012-add-frequency-based-tool-result-caching.md) | Frequency-based tool-result caching; final implementation feature, readiness checkpoint outstanding | pending | All other ARCH-020 implementation tasks |
| [ARCH-020-COMMERCE-013](COMMERCE-013-integrate-publication-and-studio-with-real-commerce-services.md) | Connect real services and verify integrated U01–U13 flows | pending | ARCH-020-COMMERCE-003, ARCH-020-COMMERCE-004, ARCH-020-COMMERCE-005, ARCH-020-COMMERCE-006, ARCH-020-COMMERCE-007, ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-011 |

2026-09-21: COMMERCE-003/008 promoted Ready for C17 interface-based parallel work.
Component acceptance uses C17 fixtures;013 separately owns real integration. This
supersedes earlier no-promotion wording for these two tasks only.011 active task
worktree status remains authoritative. No task was claimed by this amendment.

## COMMERCE-011 Attempt 3 — Changes Requested — 2026-09-21

COMMERCE-011 is **Ready, Attempt 3 retained**, claim cleared, not accepted.
Reviewed implementation `c616560` and report `78325853`. Prior four compiler
reproductions pass and R4's rolling-history/readiness/error-handling defects are
corrected in source. Three additional invalid GraphQL definitions still return
valid:true (unquoted String value, duplicate argument, conflicting alias).
R1 remains incomplete; R3 still returns a search excerpt as a document and retains
failed startup promises without owned shutdown. See the latest task Architect
Review. Verified artifact is retained; no new live validation requirement, claim,
dependent promotion, implementation edit or main integration. Other task states
and C17 ownership remain unchanged.

## COMMERCE-011 Attempt 4 — document-provider resolution — 2026-09-21

COMMERCE-011 is **Ready, Attempt 4 retained**, claim cleared, not yet accepted.
Reviewed `f363ac4` / report `05311f5b`; eight independent compiler checks pass.
The pinned MCP document-fetch gap is valid and is resolved architecturally by
**C15.1**: retain MCP search, add a bounded credential-free server adapter for
exact official shopify.dev/docs document retrieval. The in-Studio API/workflow is
preserved. Always-unavailable document retrieval is not task completion.
Implement the amendment on the same task branch, then resubmit. Prior review
history accidentally removed by the report has been restored. The reported full
suite remains95/96; the unrelated timing failure is not asserted resolved.
No new claim, downstream promotion, implementation edit or main integration.

## COMMERCE-011 Attempt 5 — Changes Requested — 2026-09-21

COMMERCE-011 is **Ready, Attempt 5 retained**, claim cleared, not accepted.
Reviewed `fba9482` / report `0e91e5dd`. C15.1 was already present before the claim,
but the approved official-document adapter remains unimplemented. A new admission
cleanup regression leaves Redis clients open on rate denial; one isolated test
reproduced zero close calls. Latest task review records R5-1/R5-2 and the exact
next steps. Preserve prior compiler/artifact fixes and submitted local Redis
evidence. Reported readiness baseline failures are not the review blocker.
No new claim, downstream promotion, implementation edit or main integration.


## COMMERCE-011 Attempt 6 review — 2026-09-21

Current decision: Ready, Attempt6 retained, claim clear; Changes Requested.
Reviewed7bfa26d /08caea2d. Document adapter and outer Redis cleanup are present,
but six controlled architect checks fail: nondefault port/encoded separator,
third redirect, missing title/article, valid larger source HTML, operation-error
preservation. R6-1–R6-3 give exact file/algorithm/test corrections in the task.
32 focused tests report passing; real Redis60/61 was not exercised with URL unset.
Retain prior compiler/artifact/pinned-process fixes. Real Redis unavailability is
not this review blocker. No downstream promotion, claim, main merge or gitlink edit.
