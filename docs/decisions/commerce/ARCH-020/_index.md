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
| [ARCH-020-COMMERCE-015](COMMERCE-015-provide-trusted-basket-and-product-policy-adapters.md) | Provide trusted basket and product policy adapters | complete | ARCH-020-COMMERCE-001, ARCH-020-DATABASE-001, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-016](COMMERCE-016-evaluate-normalised-discount-rules-and-produce-evidence.md) | Evaluate normalised discount rules and produce evidence | pending | ARCH-020-COMMERCE-006, ARCH-020-COMMERCE-015, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-017](COMMERCE-017-build-the-u14-preview-frontend.md) | Build the U14 preview frontend | pending | ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-002, ARCH-020-SHARED-001 |

2026-09-21: COMMERCE-003/008 promoted Ready for C17 interface-based parallel work.
Component acceptance uses C17 fixtures;013 separately owns real integration. This
supersedes earlier no-promotion wording for these two tasks only.011 active task
worktree status remains authoritative. No task was claimed by this amendment.


## COMMERCE-003 Attempt 1 review — 2026-09-21

Current decision: Ready for Changes Requested, Attempt 1, claim cleared; not
accepted. Reviewed 211b4a3 / 19441950. R1 Shared schemas/canonical hashes;
R2 immutable ownership/unique release members; R3 complete C17 ports and lifecycle
component with transactional fixtures; R4 pagination skipping rows. Eight original
fixture tests passed and four architect regressions failed. Exact correction
instructions/tests are in the task. C17 fixture acceptance remains permitted;
013 production composition and developer PostgreSQL rehearsal remain separate.
No new claim, downstream promotion, main integration or gitlink update.


## COMMERCE-003 Attempt 2 review — 2026-09-21

Current decision: Ready, Attempt 2, claim cleared; Changes Requested, not accepted.
Reviewed d5d7f56 / 6f4359a3. The17 submitted focused tests pass independently;
three added architect regressions fail (ADMIN draft status injection, scalar
configuration publication, incompatible release activation). Exact A2-R1–R4
corrections cover strict command/persistence validation, runtime compatibility,
canonical Feature/selection ports and executable transaction rehearsal evidence.
Preserve the working Shared hashes, ownership/membership and cursor fixes.
See the task for file-level algorithms/tests. This supersedes previous current-state
wording. C17 component acceptance remains permitted;013 composition and developer
PostgreSQL execution remain separate. No promotion, claim, main merge or gitlink edit.


## COMMERCE-003 Attempt 3 review — 2026-09-21

Current decision: Ready, Attempt3 retained, claim cleared; Changes Requested for
the remaining rehearsal deliverable. Reviewed ebe612bb /3d58f69f. Strict inputs,
compatibility and Feature/storage corrections are present;26 focused tests,
shell syntax and diff checks independently pass. A3-R1 documents immutable-row
cleanup failure, arbitrary SQL-error masking, replay assertion and worker-teardown
corrections. Preserve passing component code. PostgreSQL execution remains
explicitly developer-owned/unrun;013 composition remains separate. This is the
latest decision. No downstream promotion, new claim, main merge or gitlink edit.

## COMMERCE-003 Attempt 4 accepted — 2026-09-21

COMMERCE-003 is **Complete, architect accepted, Attempt 4 retained**, claim cleared.
Reviewed implementation `12df0104` and report `4b86771f`. The isolated rehearsal
now fails closed on unexpected SQL/cleanup errors, identifies its injected
rollback case, checks audit-backed replay and reaps owned workers. Independently
passed 26 lifecycle tests, shell syntax, four mock harness scenarios and diff
checks. Live disposable PostgreSQL execution remains explicitly developer-owned
and unrun; COMMERCE-013 owns real adapter/integration composition. No main merge
or gitlink update. COMMERCE-004 is promoted Ready (003 and SHARED-001 Complete),
without claiming an attempt. Other dependent tasks retain their current states;
012/013/system-test still have unresolved prerequisites. This acceptance supersedes
older COMMERCE-003 current-state wording; architecture is not yet Implemented.
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

## COMMERCE-015 Attempt 2 review — 2026-09-21

COMMERCE-015 is **Ready, Attempt 2 retained**, claim cleared, not accepted.
Reviewed implementation `8793bc2` and report `b791e1c`; clean isolated worktrees
and matching remote heads verified. Working registry/auth/null-line improvements
are retained. Remaining corrections: terminal-page continuation, nullable facts
nodes, historical snapshot currency provenance, and async recovery/nested-provider
failure handling. Independent checks: 9 submitted tests passed, 5 functional
reproductions failed. See the latest task Architect Review for exact instructions.
Reported unrelated baseline failures and pending live validation are not the
review blockers. No dependent promotion, main merge or gitlink change. This note
supersedes earlier COMMERCE-015 current-state wording.

## COMMERCE-015 Attempt 3 accepted — 2026-09-21

COMMERCE-015 is **Complete, architect accepted, Attempt 3 retained**, claim cleared.
Reviewed implementation `511e14ad` and report `a8c9a9e3`; clean dedicated worktrees
and matching remote heads verified. All five previous functional failures are
resolved: terminal-page continuation, nullable nodes, snapshot currency provenance,
post-authorization cancellation and nested provider error propagation. Independent
checks passed: 14 previous harness cases (including all five reproductions), plus
13 current focused tests and diff check. Submitted full-suite Redis timeout remains
separate; live Shopify/integration validation is still developer-owned and pending.
No dependent promotion:016 still needs006,007 needs016, and012/013/system-test have
other prerequisites. No main merge/gitlink change; architecture is not Implemented.
This acceptance supersedes all older COMMERCE-015 current-state wording.
