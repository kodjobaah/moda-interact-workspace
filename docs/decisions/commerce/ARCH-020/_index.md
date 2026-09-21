# ARCH-020 commerce tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_commerce. Repository: moda-interact-commerce. Coordinator: moda_architect.

COMMERCE-001 is architect-accepted Complete at Attempt 3 (`d7c1c65`). The descendant-process cleanup correction passed focused functional validation; prior real Docker PostgreSQL/Redis readiness evidence is retained. COMMERCE-002 is architect-accepted Complete at Attempt 2 (`fb3362e`): development HTTP mutations and revoked-session recovery are corrected. Live Google OAuth remains developer-owned deployment validation. Downstream source consumption awaits developer integration or explicit accepted-commit approval; no task is promoted or launched. COMMERCE-001 remains accepted and integrated. Other task rows retain this branch snapshot; canonical task worktrees remain authoritative.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-COMMERCE-001](COMMERCE-001-establish-the-next-js-service-and-nested-database-submodule.md) | Establish the Next.js service and nested database submodule | complete | — |
| [ARCH-020-COMMERCE-002](COMMERCE-002-authenticate-team-access-to-commerceagent-studio.md) | Authenticate team access to CommerceAgent Studio | complete | ARCH-020-COMMERCE-001 |
| [ARCH-020-COMMERCE-003](COMMERCE-003-implement-draft-and-release-publication-lifecycle.md) | Implement draft and release publication lifecycle | complete | ARCH-020-COMMERCE-002, ARCH-020-DATABASE-001, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-004](COMMERCE-004-serve-authorised-mcp-capability-bundles.md) | Authenticate MCP requests and resolve immutable grants | complete | ARCH-020-COMMERCE-003, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-005](COMMERCE-005-implement-basket-and-product-discovery-tools.md) | Execute validated public Shopify queries | complete | ARCH-020-COMMERCE-001, ARCH-020-COMMERCE-011, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-006](COMMERCE-006-evaluate-permitted-shopify-discount-rules.md) | Read merchant discount policy and normalise Shopify rules | complete | ARCH-020-COMMERCE-001, ARCH-020-DATABASE-001, ARCH-020-SHARED-001, ARCH-016-BACKGROUND-001, ARCH-016-DATABASE-001 |
| [ARCH-020-COMMERCE-007](COMMERCE-007-recommend-qualifying-and-similar-products.md) | Recommend qualifying and similar products | complete | ARCH-020-COMMERCE-016, ARCH-020-COMMERCE-015 |
| [ARCH-020-COMMERCE-008](COMMERCE-008-build-capability-authoring-and-release-screens.md) | Build capability authoring and release screens | complete | ARCH-020-COMMERCE-002, ARCH-020-DATABASE-001, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-009](COMMERCE-009-preview-capabilities-in-an-isolated-conversation-sandbox.md) | Implement isolated preview lifecycle and execution service | complete | ARCH-020-COMMERCE-002, ARCH-020-SHARED-001, ARCH-020-COMMERCE-001 |
| [ARCH-020-COMMERCE-010](COMMERCE-010-instrument-capability-operations-and-preview-isolation.md) | Instrument capability operations and preview isolation | complete | ARCH-020-COMMERCE-004, ARCH-020-COMMERCE-007, ARCH-020-COMMERCE-009 |
| [ARCH-020-COMMERCE-011](COMMERCE-011-provide-integrated-shopify-discovery-and-schema-validation.md) | Provide integrated Shopify discovery and schema validation | complete | ARCH-020-COMMERCE-002, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-012](COMMERCE-012-add-frequency-based-tool-result-caching.md) | Frequency-based tool-result caching; final implementation feature, readiness checkpoint outstanding | pending | All other ARCH-020 implementation tasks |
| [ARCH-020-COMMERCE-013](COMMERCE-013-integrate-publication-and-studio-with-real-commerce-services.md) | Integrate Commerce backend runtime and publication services | complete | ARCH-020-COMMERCE-003, ARCH-020-COMMERCE-004, ARCH-020-COMMERCE-005, ARCH-020-COMMERCE-006, ARCH-020-COMMERCE-007, ARCH-020-COMMERCE-011, ARCH-020-COMMERCE-014, ARCH-020-COMMERCE-015, ARCH-020-COMMERCE-016 |
| [ARCH-020-COMMERCE-014](COMMERCE-014-execute-and-render-pinned-tool-definitions.md) | Execute and render pinned tool definitions | complete | ARCH-020-COMMERCE-004, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-015](COMMERCE-015-provide-trusted-basket-and-product-policy-adapters.md) | Provide trusted basket and product policy adapters | complete | ARCH-020-COMMERCE-001, ARCH-020-DATABASE-001, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-016](COMMERCE-016-evaluate-normalised-discount-rules-and-produce-evidence.md) | Evaluate normalised discount rules and produce evidence | complete | ARCH-020-COMMERCE-006, ARCH-020-COMMERCE-015, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-017](COMMERCE-017-build-the-u14-preview-frontend.md) | Build the U14 preview frontend | complete | ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-002, ARCH-020-SHARED-001 |
| [ARCH-020-COMMERCE-018](COMMERCE-018-integrate-studio-pages-with-production-services.md) | Integrate Studio pages with production services | ready | ARCH-020-COMMERCE-013, ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-002, ARCH-020-COMMERCE-011 |
| [ARCH-020-COMMERCE-019](COMMERCE-019-integrate-preview-bundles-and-u14-service-flow.md) | Integrate preview bundles and the U14 service flow | ready | ARCH-020-COMMERCE-013, ARCH-020-COMMERCE-009, ARCH-020-COMMERCE-017, ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-002, ARCH-020-COMMERCE-034 |
| [ARCH-020-COMMERCE-020](COMMERCE-020-implement-external-connection-management-service.md) | Implement external connection lifecycle and command kernel | ready | ARCH-020-DATABASE-003, ARCH-020-SHARED-002, ARCH-020-COMMERCE-002 |
| [ARCH-020-COMMERCE-021](COMMERCE-021-execute-read-only-external-http-tools.md) | Execute read-only external HTTP tools | ready | ARCH-020-SHARED-002, ARCH-020-COMMERCE-014 |
| [ARCH-020-COMMERCE-022](COMMERCE-022-build-connections-pages-u15-u16.md) | Build Connections pages U15 and U16 | ready | ARCH-020-SHARED-002, ARCH-020-COMMERCE-002, ARCH-020-COMMERCE-008 |
| [ARCH-020-COMMERCE-023](COMMERCE-023-build-external-tool-authoring-and-filter-editor.md) | Build external tool authoring and response-filter editor | ready | ARCH-020-SHARED-002, ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-017 |
| [ARCH-020-COMMERCE-025](COMMERCE-025-implement-bounded-response-filtering-and-projection.md) | Implement bounded response filtering and projection | ready | ARCH-020-SHARED-002 |
| [ARCH-020-COMMERCE-024](COMMERCE-024-integrate-external-tools-connections-and-studio.md) | Wire accepted external API components into production factories | pending | ARCH-020-COMMERCE-020, ARCH-020-COMMERCE-021, ARCH-020-COMMERCE-022, ARCH-020-COMMERCE-023, ARCH-020-COMMERCE-025, ARCH-020-COMMERCE-013, ARCH-020-COMMERCE-018, ARCH-020-COMMERCE-019, ARCH-020-COMMERCE-026, ARCH-020-COMMERCE-027, ARCH-020-COMMERCE-028, ARCH-020-COMMERCE-030, ARCH-020-COMMERCE-031, ARCH-020-COMMERCE-032 |
| [ARCH-020-COMMERCE-026](COMMERCE-026-implement-isolated-javascript-response-processing.md) | Implement validated code-processing adapter over proven runtime | ready | ARCH-020-SHARED-002, ARCH-020-COMMERCE-029 |
| [ARCH-020-COMMERCE-027](COMMERCE-027-build-code-editor-and-raw-response-preview.md) | Build code editor and raw-response preview | ready | ARCH-020-SHARED-002, ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-017 |
| [ARCH-020-COMMERCE-028](COMMERCE-028-implement-scoped-external-api-credentials.md) | Implement scoped external API credentials | pending | ARCH-020-COMMERCE-020, ARCH-020-DATABASE-003, ARCH-020-SHARED-002 |
| [ARCH-020-COMMERCE-029](COMMERCE-029-prove-and-package-bounded-code-runtime.md) | Prove and package bounded code runtime | complete (Accepted, Attempt 4) | ARCH-020-COMMERCE-001 |
| [ARCH-020-COMMERCE-030](COMMERCE-030-implement-external-tool-publication-validation.md) | Implement external tool publication validation | pending | ARCH-020-SHARED-002, ARCH-020-COMMERCE-003, ARCH-020-COMMERCE-021, ARCH-020-COMMERCE-025, ARCH-020-COMMERCE-026 |
| [ARCH-020-COMMERCE-031](COMMERCE-031-implement-external-response-preview-backend.md) | Implement external response preview backend | pending | ARCH-020-COMMERCE-019, ARCH-020-COMMERCE-009, ARCH-020-SHARED-002, ARCH-020-COMMERCE-025, ARCH-020-COMMERCE-026, ARCH-020-COMMERCE-030 |
| [ARCH-020-COMMERCE-032](COMMERCE-032-implement-external-tool-availability.md) | Implement external tool availability | pending | ARCH-020-COMMERCE-013, ARCH-020-COMMERCE-028, ARCH-020-SHARED-002 |
| [ARCH-020-COMMERCE-034](COMMERCE-034-correct-u14-tool-entry-conversation-source-gating.md) | Correct U14 tool-entry conversation source gating | complete | ARCH-020-COMMERCE-017, ARCH-020-COMMERCE-009 |

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

## COMMERCE-006 Attempt 3 architect review — 2026-09-21

Changes Requested; Ready, Attempt3 retained, claim clear; not accepted.
Verified de532c6/ec088f27. A2 NONE, fraction conversion and zero-value fixes pass;
both documents now pass pinned Admin2026-07 schema validation. Nineteen submitted
reader tests pass; four added cases fail. A3-R1 corrects nested first:1000 runtime
limits with an explicit bounded partial-target profile. A3-R2 requires typed
cancellation, pre-dispatch checks and rejection of late successful data.
See the canonical COMMERCE-006 task for precise code locations and expected effects.
No live validation gate, dependent promotion, new claim, implementation change,
main integration or gitlink update. Parent overlay published before preparation.


## COMMERCE-006 Attempt 4 accepted — 2026-09-21

Current decision: Complete, architect accepted; Attempt4 retained, claim clear.
Implementation1c124f4 / report70c3cf24. A3-R1 bounded nested5-item query profile
and A3-R2 typed cancellation/late-result guards accepted. Independent reader/auth
27/27 pass; prior architect harness23/23 pass, including all4 prior failures.
Live Shopify/provider assembly and unproven semantics remain explicitly separate;
unknown facts must stay unknown.006 prerequisite is satisfied, but016 still awaits
015;012/013/system-test retain other unfinished dependencies. No downstream
promotion, implementation changes, main integration or gitlink update. See the
canonical task's latest Accepted review for validation limits and integration order.


## COMMERCE-004 Attempt 2 architect review — 2026-09-21

Changes Requested; Ready, Attempt2 retained, claim clear; not accepted.
Reviewed5ef60bd/5d54102b. Submitted12 tests pass; four added tests fail:
last-write association bounds, missing pinned definition, malformed JSON503,
and ignored-abort executor holding the response past deadline. A2-R1–R3 define
original-association/tool-revocation resolution, protocol/aggregate bounds and
bounded execution waiting. Retain actual prompt and true-handler interoperability
improvements. See canonical task for precise files and acceptance effects.
No promotion, new claim, main integration or gitlink update; live validation
remains separate from component corrections.

## COMMERCE-004 Attempt 3 accepted — 2026-09-21

COMMERCE-004 is **Accepted / Complete, Attempt 3 retained**, claim cleared.
Reviewed implementation `0411babc` and parent report `b272d1a9` against remote heads.
Original-association minima, required pinned records/current revocation, SDK
transport/protocol bounds and bounded executor waiting resolve A2-R1–A2-R3.
Independent validation passed18 focused MCP tests and all four prior failure
reproductions; diff checks passed. Submitted typecheck/lint/build passed; reported
full-suite infrastructure failures remain separate from component acceptance.
Live Background assertions, Redis, production adapter/provider and deployment
validation remain developer/integration-owned. COMMERCE-014 is promoted Ready,
Attempt0 with no claim, because004/SHARED-001 are Complete. Other dependants retain
their unresolved gates;012 is still the final implementation checkpoint.
No implementation changes, main integration or gitlink update. Architecture is not
yet Implemented. This supersedes older004 state wording and retains review history.
## COMMERCE-009 Attempt 4 accepted — 2026-09-21

Complete, architect accepted; Attempt4 retained, claim clear. Reviewed5d4dcd3 /
ef556b4c. Expired-owner execution fence verified in memory/Redis and all dispatch
boundaries. Independent37/37 focused tests pass, including actual isolated Lua;
prior architect expiry/replacement reproduction1/1 passes with0 stale model calls.
Prior accepted prompt/history/language/replay/bounded-state corrections retained.
009 is satisfied;012/013/system-test retain other unfinished prerequisites, and
017 has no009 dependency. No promotion or automatic execution. Live deployment
and013 assembly remain separate. No main integration or gitlink update.
## COMMERCE-008 Attempt 5 review — 2026-09-21

COMMERCE-008 is **Ready, Attempt 5 retained**, claim cleared, not accepted.
Reviewed implementation `558432f` and report `0b2e03bb`; remote heads matched and
worktrees were clean. A4-R2/R3 are accepted; all three previous reproductions and
25 focused tests passed independently. One remaining A5-R1 failure: adding a
nested field beneath an existing aliased product creates an unbound second root
outside the retained resultPath. The canonical task review contains exact AST
merge/validation instructions. Local U14 handoff passes; real preview integration
and live validation remain separately owned and are not blockers. No dependent
promotion or main integration. This supersedes older COMMERCE-008 state wording.

## COMMERCE-008 Attempt 6 accepted — 2026-09-21

COMMERCE-008 is **Accepted / Complete, Attempt 6 retained**, claim cleared.
Reviewed implementation `8ba5e42` and report `7f8e194` against remote task heads.
The final alias correction preserves the existing field's arguments/result path,
rejects ambiguous edits and denies unbound duplicate roots. Independent validation:
24 focused tests and all four previous architect reproductions passed; diff checks
passed. Submitted typecheck/lint/build passed; the reported208-pass/one unrelated
Redis timeout does not block this component acceptance. Live OAuth/providers,
production composition and actual U14 execution remain separate integration work.
COMMERCE-017 is promoted Ready, Attempt0, no claim, because008/002/SHARED-001 are
accepted Complete.009 is not a prerequisite for017's contract-fixture frontend.
Other downstream tasks remain gated by their own unresolved prerequisites;012 is
still the final implementation checkpoint. No implementation changes, main merge,
main push or gitlink update. Architecture is not yet Implemented. This supersedes
older008 state wording while retaining historical reviews.

## COMMERCE-014 Attempt 1 accepted — 2026-09-21

COMMERCE-014 is **Accepted / Complete, Attempt 1 retained**, claim cleared.
Reviewed implementation `232cbdd` and report `6dc01a40` against remote task heads.
Exact-version definition dispatch, Shared mappings/output validation, trusted-context
separation and bounded one-pass rendering satisfy the owned component contract.
Independent11 focused tests and diff checks passed. Lint/typecheck/build and wider
suite results remain submitted evidence.013 owns real adapter registration and
integrated policy/query execution; live infrastructure/evidence validation remains
separate. No dependent promotion, new claim, implementation edit, main integration
or gitlink update.012 remains the final implementation checkpoint; architecture is
not yet Implemented. Older014 readiness wording is historical.
## COMMERCE-016 Attempt 1 architect review — 2026-09-21

Changes Requested; Ready, Attempt 1 retained, claim cleared; not accepted.
Reviewed implementation `bfbd7839` and report `f96b41df` against remote task heads.
Independent submitted contract suites passed50/50; three isolated functional
reproductions fail: unknown current basket variant facts still qualify, a LINE
rounding cap understates100% savings, and mixed-currency proposal amounts produce
a false known subtotal failure. R1–R3 give explicit evaluator corrections and
expected outputs in the task report. Pure arithmetic/Shared evidence and shared
budget boundaries are retained. No implementation edits, next claim, main merge,
gitlink update or dependent promotion.007 remains gated by016;013 and012 retain
their remaining gates. Live provider composition remains separate integration work.
Older readiness wording is historical; architecture is not yet Implemented.


## COMMERCE-016 Attempt 2 accepted — 2026-09-21

Complete, architect accepted; Attempt2 retained, claim clear. Reviewed55204ec /
dc9edf85. Current-fact checks, consistent LINE/TOTAL savings caps and comparable
currency minimum precedence accepted. Independent evaluator15/15 and previous
architect regressions3/3 pass.007 promoted to Ready because015/016 are Complete;
attempt0/claim unchanged, no execution.012/013/system-test retain other unmet
prerequisites. Live integration and reader baseline limitation remain separate.
No implementation changes, main integration or gitlink update.

## COMMERCE-005 Attempt 2 architect review — 2026-09-21

Changes Requested; Ready, Attempt2 retained, claim clear; not accepted.
Reviewed2761e6b/e4fc15cd. Seven submitted tests pass; two task-owned review cases
fail: populated list selection validation and blocked stream cancellation.
A2-R1–R3 give exact recursion fix, active body cleanup and C14 UNAVAILABLE mapping
for provider-version fallback. Retain variable validation/HTTP envelope/deadline
race improvements. No scope expansion, promotion, new claim, main merge or gitlink
change. See task for exact acceptance effects; live provider validation is separate.


## COMMERCE-005 Attempt 3 architect review — 2026-09-21

Changes Requested; Ready, Attempt3 retained, claim clear; not accepted.
Reviewed6b2c410/4b681aa1. List recursion and provider-version/redirect fixes verified.
Eleven submitted tests pass; two cleanup cases fail: awaited rejected-body cancel
exceeds deadline and pending AsyncIterable read is not interrupted. A3-R1 gives
bounded cleanup and a minimal ReadableStream/Uint8Array-only contract correction.
No new scope, downstream promotion, claim, main merge or gitlink update. See task
for exact effects; live provider and baseline validation remain separate.

## COMMERCE-005 Attempt 4 accepted — 2026-09-21

COMMERCE-005 is **Accepted / Complete, Attempt 4 retained**, claim cleared.
Reviewed implementation `f099659` and report `e5662be5` against remote heads.
A3-R1 is resolved: rejected/late body cleanup no longer delays typed responses;
cleanup rejections are observed; only Uint8Array/ReadableStream bodies are supported,
and unsupported iterators are rejected without consumption. Existing stream and
query corrections remain. Independent13 focused tests and the prior pending-cleanup
reproduction passed; diff checks passed. Typecheck/lint/build and full272/275 are
submitted evidence; baseline failures do not block this component acceptance.
013 owns real transport composition; live Shopify/provider validation remains
pending. No dependent promotion, new claim, main integration or gitlink update.
012 remains the final implementation checkpoint; architecture is not yet Implemented.
This supersedes older005 current-state wording while preserving review history.

2026-09-21 integration split: C20 supersedes combined 013 ownership. 013 owns
backend integration; 018 and 019 independently own Studio and preview integration
and can run concurrently after their explicit prerequisites complete.

## COMMERCE-017 Attempt 4 architect review — 2026-09-21

COMMERCE-017 is **Changes Requested / Ready, Attempt 4 retained**, executor and
claimed_at null; not accepted. Reviewed implementation `8b902a6` and report
`c44ebd71`, matching remote task heads. Independent UI/client tests passed 17/17
and all 8 previous reproductions passed. Four current functional reproductions
failed: Start after Reset is blocked, changing a handoff source still dispatches
the original tool, Conversation Back chooses an unrelated tool, and a valid
nullable integer null cannot execute. Task A4-R1–R3 provide exact correction
steps and expected effects. Preserve the verified previous fixes and the existing
authenticated source-read boundary. Browser identity/live-provider evidence remains
pending separately. No dependent promotion, new claim, implementation change,
main integration or gitlink update. This supersedes earlier COMMERCE-017 current-state
wording only; other task decisions remain unchanged. Architecture is not yet
Implemented; COMMERCE-012 remains the final implementation checkpoint.

## COMMERCE-017 Attempt 5 architect review — 2026-09-21

COMMERCE-017 is **Changes Requested / Ready, Attempt 5 retained**, executor and
claimed_at null; not accepted. Reviewed implementation `bdb753c` and report
`482a0964`, matching remote task heads. Independent UI/client tests passed 20/20
and all 12 prior architect reproductions passed. Two remaining source-flow tests
failed: an unsaved handoff cannot start with a populated saved-release list,
and the tool source can change while its original POST is pending. A5-R1 records
exact corrections, guards and expected payload/call effects, completing A4-R2.
Preserve the verified prior fixes. Authenticated browser identity and live-provider
validation remain pending separately. No dependent promotion, new claim,
implementation change, main integration or gitlink update. This supersedes older
COMMERCE-017 current-state wording only; other task decisions remain unchanged.
Architecture is not yet Implemented; COMMERCE-012 remains the final checkpoint.


## COMMERCE-017 Attempt 6 architect review — 2026-09-21

Changes Requested; **Ready**, Attempt6 retained, executor/claimed_at null; not accepted.
Implementation `5aea0c4` and report `2d30a0aa` match remote heads. Independent22 UI/client
checks and both Attempt5 regressions pass. One remaining source-lock case fails:
uncertain conversation creation from tool A allows visible source B while replay
retains A. Latest task A6-R1 supplies the exact shared lock predicate, event guard
and regression expectations. Prior fixes are retained; browser identity remains
an explicit separate validation prerequisite. No dependent promotion, new claim,
implementation edit, main merge or gitlink change. Reclaim after this review
overlay is published; older decisions are historical.

## COMMERCE-017 Attempt 7 accepted — 2026-09-21

COMMERCE-017 is **Accepted / Complete, Attempt 7 retained**, executor and claimed_at
null. Reviewed implementation `c6da2f2` and report `e6c16617` against remote heads.
A6-R1 is resolved: both tool selectors consult the live synchronous source lock,
pending/uncertain creation retains its original source and payload, and same-ID
reconciliation/reset follow the existing lifecycle. Independent 23 UI/client tests,
the exact outstanding reproduction and all 14 earlier architect reproductions pass;
diff checks pass. Submitted 60 preview tests/typecheck/lint/build remain reported
evidence. This accepts the fixture-validated U14 component; authenticated browser
validation awaits local Studio identity and COMMERCE-019 owns real U14 integration.
COMMERCE-019 still awaits COMMERCE-013; other deployment/final/system gates remain.
No dependent promotion, new claim, implementation change, main integration or
gitlink update. This supersedes earlier COMMERCE-017 current-state wording while preserving
review history and other task decisions. Architecture remains not yet Implemented;
COMMERCE-012 is the final implementation checkpoint.

## COMMERCE-007 Attempt 5 architect review — 2026-09-21

COMMERCE-007 is **Changes Requested / Ready, Attempt 5 retained**, claims cleared.
Reviewed implementation `caf5d38` and report `40ed0a4`, matching remote task heads.
Independent 11 focused tests and seven runtime reproductions pass. A4-R1.1 is
resolved: one execution makes 12 actual provider requests and rejects reservation 13
with typed ERROR. The remaining A5-R1 is confined to the C18 harness/report:
replace the two partial consumer helpers with one measured async replay path,
validate every selected item's provenance/proposal/semantics, and correct claims.
Diagnostics show the new helper accepts truncation and rejects valid fresh digests.
No new production defect is alleged. No dependent promotion, new claim,
implementation change, main integration or gitlink update. Live deployed/worker/
Shopify validation remains with its assigned owner. This supersedes older COMMERCE-007
current-state wording only; other decisions and history remain unchanged.
Architecture is not yet Implemented.

## COMMERCE-007 Attempt 6 architect review — 2026-09-21

COMMERCE-007 is **Changes Requested / Ready, Attempt 6 retained**, claims cleared.
Reviewed implementation `21e150f` and report `73981c7b`, matching remote heads.
Independent 11 focused tests and seven runtime reproductions pass; the 12-request
budget proof remains valid. The unified replay now handles all selected proposals,
truncation and valid fresh digests. A6-R1 identifies two remaining harness issues:
refresh receives no original-call tuple, and expired original evidence can be
rescued by a fresh response. Exact callback/provenance and expiry corrections are
recorded in the task; no production recommendation defect or code change is requested.
No dependent promotion, new claim, main integration or gitlink update. Live service
validation remains with its assigned owner. This supersedes older COMMERCE-007 current-state
wording only; other decisions remain unchanged. Architecture is not yet Implemented.

## COMMERCE-007 Attempt 7 accepted — 2026-09-21

COMMERCE-007 is **Accepted / Complete, Attempt 7 retained**, claims cleared.
Reviewed implementation `e08b896` and report `bb3e977` against remote heads.
A6-R1 is resolved: refresh receives the original name/revision/arguments and invalid
or expired original evidence is rejected before refresh. Independent 11 focused
tests, seven runtime reproductions and both augmented contract tests pass; the
12-request provider budget and reservation 13 rejection remain verified. Diff checks
pass. Submitted full 334/335 and typecheck/lint/build remain reported evidence;
live MCP/Background/Shopify proof remains with integration/system owners.
COMMERCE-010 and COMMERCE-013 are promoted **Ready, Attempt 0**, claims null:
all their explicit prerequisites are accepted Complete. Preparation owns source
synchronization and claims; neither task is launched. COMMERCE-018/019 still await
COMMERCE-013; final/deployment/system gates remain. No implementation change,
main integration or gitlink update. This supersedes older COMMERCE-007 current-state wording;
other task decisions remain unchanged. Architecture is not yet Implemented and
COMMERCE-012 remains the final implementation checkpoint.


### COMMERCE-010 Attempt 1 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 1; executor/claim null.** Reviewed implementation
`7a88d72` and parent report `41d662e2`. A1-R1–R4 in the canonical task's Architect
Review specify actual MCP terminal events/counts, single and correctly classified
stage outcomes, provider correlation/preview-purpose propagation, and accurate
service-level isolation/refresh evidence. Existing focused suites: 23 passed;
two independent functional reproductions failed (duplicate execution and premature
discovery success). Baseline repository-wide failures do not drive this decision.
COMMERCE-010 is not accepted; no dependent is promoted. Hosted validation remains
developer-owned; the final manual system-test gate is unchanged.


### COMMERCE-010 Attempt 2 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 2; executor/claim null.** Reviewed `3343c95`
and report `ad8e2de2`. A2-R1–R4 in the canonical task give explicit corrections
for terminal MCP classification/counting, render-stage outcomes, evaluator
preview/environment/trace propagation, and truthful refresh/isolation evidence.
The submitted focused suite passed 106 tests; three independent functional
assertions failed. Existing fixes are retained. C18 final evidence refresh remains
Background-owned, distinct from evaluator eligibility; an external signal gap
must be handed off honestly, not replaced by an evaluator metric. No acceptance
or downstream promotion. Redis baseline and hosted arrival are not review blockers;
the developer-owned final manual system-test gate remains unchanged.


### COMMERCE-010 Attempt 3 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 3; executor/claim null.** Reviewed `a51eb69`
and report `27429e6b`. One correction remains: A3-R1 preserves a completed tool's
DENIED outcome when the JSON-RPC envelope succeeds. The submitted focused suites
passed 71 tests; prior architect reproductions passed 3/3, while the new denial
precedence check failed. Other A2 corrections are resolved. No acceptance or
downstream promotion. External C18 refresh signal/hosted arrival remain explicit
integration/developer handoffs; baseline failures are not review blockers.


## COMMERCE-010 Attempt 4 architect acceptance — 2026-09-21

**Accepted; Complete**, Attempt4 retained, executor/claimed_at null. Reviewed
implementation `e8b43e4` and report `09e678e` against remote task heads. The completed
DENIED tool outcome survives its valid JSON-RPC envelope; protocol classification
and one terminal request event remain intact. Independent focused72/72 and prior
architect regressions4/4 pass; diff check passes. Hosted arrival, preview exclusion
from production alerts and Background-owned refresh-signal integration remain
explicit external validation, not claimed complete.

No dependent promotion: GATEWAY-002 still awaits GATEWAY-001; COMMERCE-012 and
SYSTEM-TEST-001 still have incomplete infrastructure/composition dependencies.
No automatic task launch, implementation/main change or service gitlink update.
Architecture remains in progress; latest task YAML/review supersedes historical
Changes Requested summaries.


### COMMERCE-013 Attempt 3 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 3; executor/claim null.** Reviewed `1dd5211`
and report `1961d586`. A3-R1–R5 specify real provider rule facts/scopes, eligible
resolve manifests and shared lease/limits, durable cross-transaction CAS time,
complete saved-selection/inspection results, and real adapter mutation rehearsals.
Focused tests: 59 passed; six prior reproductions pass; two remaining contract
checks fail (repeated CAS time and empty draft selection). The reported Prisma
1/1 test is a no-op smoke check, not race/rollback evidence. No acceptance or
downstream promotion; COMMERCE-018/019 stay Pending. Disposable infrastructure
execution remains developer-owned; lack of Docker authorization is not the blocker.


### COMMERCE-013 Attempt 4 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 4; executor/claim null.** Reviewed `d42f8e9`
and report `b71c7874`. A4-R1–R4 specify canonical initial resolution/tool filtering,
actual provider rule facts and bounded reads, real inspection/saved-binding
contracts, and genuine contentious adapter race/rollback assertions. Focused
suite: 59 passed; all eight prior reproductions pass; new no-grant production
resolve check fails. No acceptance or downstream promotion; COMMERCE-018/019
remain Pending. The submitted database 2/2 evidence covers its actual scenarios,
not the missing publication/pointer contention/post-write rollback cases.
Infrastructure execution remains developer-owned; Docker authorization is not
the blocker. Preserve the final manual system-test gate.

### COMMERCE-013 Attempt 5 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 5; executor/claim null.** Reviewed implementation
`3ab8679` and submitted report `8bdc05d0`. The task report's A5-R1–R4 require:
correct schema-valid Shopify discount reads and established normalization semantics;
bounded product-response streaming; explicit saved-tool draft preview support;
and inspection using the backend's validated deployment environment.
Initial no-grant resolution and prior adapter regressions pass. Focused integration:
59/59; previous architect checks: 9/9; expanded facade harness: 8 passed, 2 failed
(saved DRAFT rejection and TEST inspection querying DEVELOPMENT).
Actual contention/post-write rollback scenarios now exist; submitted PostgreSQL
evidence was reviewed, while disposable infrastructure/migration validation remains
pending. No implementation change, main merge, acceptance or downstream promotion.
COMMERCE-018/019 remain Pending; final manual system-test gate remains.

### COMMERCE-013 Attempt 6 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 6 retained; executor/claim null.** Reviewed
implementation `812e97e` and report `36a9a603`. A5-R2 bounded product streaming
and A5-R4 configured inspection environment are resolved; standalone draft
preview and the pinned Admin schema check pass. A6-R1 requires the supported
production discount path (all rules still have unknown restrictions/null
semantics); A6-R2 requires independent publication validation for every
capability binding, including revisions also explicitly selected as drafts.
Exact changes and focused acceptance examples are in the task's Architect Review.
Focused integration: 59/59 passed. Architect harness: 11 passed, 1 failed,
reproducing the unpublished-binding bypass. Submitted PostgreSQL 2/2 evidence
reviewed; developer-owned infrastructure/migration validation remains pending.
No acceptance, implementation change, main merge, gitlink update or downstream
promotion. COMMERCE-018/019 remain Pending; final manual system-test gate remains.

### COMMERCE-013 Attempt 7 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 7 retained; executor/claim null.** Reviewed
implementation `0fab9dc` and report `3dc1fbf7`. A6-R2 binding correction passes.
A7-R1 requires correcting six pinned Shopify schema errors in the production
customer/segment selections; A7-R2 requires substantiating the native-basic
calculation profile and demonstrating the supported production path. Explicit
corrections and bounded verification examples are in the task Architect Review.
Focused integration: 60/60. Architect harness: 11 passed, 1 failed (production
Admin document validation). PostgreSQL report remains one passing smoke and one
failed rehearsal; no new storage regression is established, and developer-owned
isolated infrastructure validation remains pending. No acceptance, implementation
change, main merge, gitlink update or downstream promotion. COMMERCE-018/019
remain Pending; final manual system-test gate remains.

### COMMERCE-013 Attempt 8 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 8 retained; executor/claim null.** Reviewed
implementation `13805d2` and report `de6b2829`. A7-R1 production Shopify schema
correction passes. A8-R1 corrects whole-basket minimum assumptions for targeted
discounts; A8-R2 separates provider-supported calculation semantics from a fixture
of assumed rounding constants. Exact correction examples and evidence boundaries
are in the task Architect Review. Focused integration: 61/61; architect checks:
12/12. PostgreSQL remains one passing scenario and one timeout, not completed
rollback evidence or a demonstrated new regression. Developer-owned infrastructure
validation remains pending. No acceptance, implementation change, main merge,
gitlink update or downstream promotion; COMMERCE-018/019 remain Pending.

### COMMERCE-013 Attempt 9 accepted — 2026-09-21

**Accepted / Complete, Attempt 9 retained; executor/claim null.** Reviewed
implementation `4d52977` and report `650d53bc`. Targeted minima use eligible lines;
unproven monetary semantics fail closed. Native-basic fixed/percentage monetary
qualification remains UNSUPPORTED pending independent provider evidence and an
explicit reviewed enabling change. Acceptance does not assert live discount
qualification; Studio/preview must preserve this limitation. Earlier review demands
for guessed/unsupported positive monetary profiles are superseded by this disposition.
Focused integration: 61/61; architect regressions: 12/12. PostgreSQL remains one
passing scenario and one timeout; developer-owned adapter validation remains pending.
013 introduces no migration; database owners retain fresh/upgrade evidence ownership.
COMMERCE-018/019 are **Ready, Attempt 0, claims null** after checking their explicit
prerequisites. No automatic launch, main merge, implementation edit or gitlink update.
Other deployment/cache/system gates retain their dependencies and manual validation.

## COMMERCE-029 Attempt 4 architect acceptance — 2026-09-21

**Accepted / Complete, Attempt 4 retained; executor/claim null.** Reviewed
implementation `f22e2d6` and report `4069f60c`. Compile validation now uses the
QuickJS compile-only path and does not execute valid top-level side effects; the
real supervisor proof observes execution start, returns `DEADLINE`, awaits worker
termination and recovers for a following transform. Attempt 3's output-isolation
and packaged-runtime corrections are preserved. Submitted focused proof: 10/10;
package/smoke, 64 MiB WASM ceiling, lint, typecheck, build and diff checks pass.

No dependent is promoted by this acceptance alone: COMMERCE-026 still awaits
SHARED-002, which remains Ready rather than Complete. GATEWAY-003, COMMERCE-012
and system validation retain their remaining dependency gates. No automatic task
launch, implementation/main merge or service gitlink update.

## SHARED-002 Attempt 5 acceptance frontier — 2026-09-21

`ARCH-020-SHARED-002` is Accepted / Complete at Attempt 5. With the Shared C21
contract/publication prerequisite satisfied, `COMMERCE-020`, `021`, `022`, `023`,
`026` and `027` are Ready at Attempt 0; `COMMERCE-025` remains Ready at Attempt 0.
No task is claimed or launched by this reconciliation. `COMMERCE-028`, `030`, `031`,
`032`, `024`, `GATEWAY-003`, `COMMERCE-012` and the system-test tasks retain their
remaining dependency gates.


## COMMERCE-034 Attempt 1 acceptance reconciliation — 2026-09-22

COMMERCE-034 is **Accepted / Complete, Attempt 1**, executor and claimed_at null.
The accepted U14 correction requires authored release/draft sources for Conversation
preview and preserves tool-only handoff for Tool test. COMMERCE-019 now records
COMMERCE-034 as an accepted prerequisite and remains **Ready** because all listed
prerequisites are Complete. No downstream task was launched by this reconciliation.
