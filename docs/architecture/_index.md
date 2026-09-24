# Architecture index

> **State synchronization:** ARCH-001..007 rows retain the 2026-09-08 rollup; ARCH-008..009 retain the 2026-09-12 rollup; ARCH-010 is synchronized 2026-09-13. Current task state is generated in
> [`WORKSPACE-CURRENT-TASK-STATE.md`](WORKSPACE-CURRENT-TASK-STATE.md).
> Individual task YAML remains authoritative. Historical review/amendment documents
> preserve the state that existed when they were written and should not be used as
> the current execution frontier.

| Architecture | Current task state | Primary architecture |
|---|---|---|
| ARCH-001 | complete 9, ready 1 | [Shopify checkout recovery webhook processing](ARCH-001-shopify-checkout-recovery-webhook-processing.md) |
| ARCH-002 | complete 61, pending 3, ready 2, superseded 5 | [Render production gateway and infrastructure](ARCH-002-render-production-gateway-infrastructure.md) |
| ARCH-003 | blocked 1, complete 23, pending 1, review 1, superseded 1 | [Admin operational UI](ARCH-003-admin-operational-ui.md) |
| ARCH-004 | complete 6, ready 1 | [Cart activity recovery rescheduling](ARCH-004-cart-activity-recovery-rescheduling.md) |
| ARCH-005 | complete 17, pending 2, ready 1, superseded 2 | [Global internationalisation and WhatsApp markets](ARCH-005-global-internationalisation-whatsapp-markets.md) |
| ARCH-006 | complete 21, pending 3, review 3, superseded 2 | [Merchant communications and support inbox](ARCH-006-merchant-communications-support-inbox.md) |
| ARCH-007 | complete 21, pending 13, ready 5 | [Shopify billing, usage and WhatsApp cost control](ARCH-007-shopify-billing-usage-cost-control.md) |
| ARCH-008 | complete 7, ready 1, superseded 1 | [Shopify App Pricing conformance](ARCH-008-shopify-app-pricing-conformance.md) |
| ARCH-009 | complete 5, pending 2, ready 2 | [Merchant billing lifecycle, cancellations and refunds](ARCH-009-merchant-billing-lifecycle-cancellations-refunds.md) |
| ARCH-010 | complete 40, pending 34, ready 4, superseded 8 | [Merchant lifecycle state transitions and behavioural access](ARCH-010-merchant-lifecycle-state-transitions.md) · [First-production baseline](ARCH-010-first-production-baseline.md) |
| ARCH-011 | pending 9, ready 3 | [Pro-rated same-cycle subscription upgrades](ARCH-011-pro-rated-same-cycle-subscription-upgrades.md) |
| ARCH-012 | pending 7, ready 3 | [Moda-managed WhatsApp communications](ARCH-012-moda-managed-whatsapp-communications.md) |
| ARCH-013 | complete 2 | [Merchant application routing, navigation and lifecycle coherence](ARCH-013-merchant-application-routing-navigation.md) |

## Current execution highlights

- `ARCH-010`: first-production baseline consolidation is current. Ready frontier: `BACKGROUND-008`, `BACKGROUND-009`, `ADMIN-004`, `ADMIN-008`. `DATABASE-014` and `ADMIN-010` are architect-accepted Complete; superseded tasks remain history only.
- `ARCH-010` system-test tasks remain terminal/manual-gated and never block implementation startup.
- For architectures other than ARCH-010, use [`WORKSPACE-CURRENT-TASK-STATE.md`](WORKSPACE-CURRENT-TASK-STATE.md) plus individual task YAML rather than relying on an old highlight bullet.

- `ARCH-012`: agreed Moda-managed WhatsApp communications. Ready frontier: `SHARED-001`, `DATABASE-001`, `BACKGROUND-003`. Exact task YAML and `ARCH-012-implementation-handoff.md` are authoritative.

- `ARCH-013`: implemented. `SHOPIFY-001` is Complete / Attempt 2 Accepted and `SHOPIFY-002` is Complete / Attempt 1 Accepted. ARCH-013 has no Ready task; the routing-coherence gate before later billing-v1.1 work is satisfied.

## Historical architecture material

Files named `*-review-*`, `*-amendment.md`, overview documents, and old overlay/patch artifacts may intentionally preserve earlier decisions or task frontiers. Use the current-state rollup and task YAML for execution eligibility.

## ARCH-019 — merchant recovery experience (2026-09-20)

Current frontier: all ARCH-019 implementation tasks are architect-accepted/Complete: DATABASE-001 and SHOPIFY-001/003/006 at Attempt 1, SHOPIFY-002 at Attempt 3, SHOPIFY-004/005 at Attempt 2. SHOPIFY-006 accepted `39054cec`. SYSTEM-TEST-001 Ready at Attempt 0, explicitly developer-invoked after manual validation; not started. Architecture remains In Progress pending terminal integrated validation and final architect acceptance. Accepted dependency records are reconciled into SYSTEM-TEST-001; readiness does not authorize execution, deployment or unmerged dependency consumption.

[Architecture](ARCH-019-merchant-recovery-experience.md) · [Implementation handoff](ARCH-019-implementation-handoff.md)

## ARCH-020 — CommerceAgent Studio and MCP capabilities (2026-09-20)

COMMERCE-001 is architect-accepted Complete at Attempt 3 (`d7c1c65`). The descendant-process cleanup correction passed focused functional validation; prior real Docker PostgreSQL/Redis readiness evidence is retained. COMMERCE-002 is architect-accepted Complete at Attempt 2 (`fb3362e`): development HTTP mutations and revoked-session recovery are corrected. Live Google OAuth remains developer-owned deployment validation. Downstream source consumption awaits developer integration or explicit accepted-commit approval; no task is promoted or launched. COMMERCE-001 remains accepted and integrated. Other task rows retain this branch snapshot; canonical task worktrees remain authoritative.

The Commerce repository and nested database are provisioned; live MCP remains private and staff UI routing remains Gateway-owned. This task review does not complete ARCH-020.

[Architecture](ARCH-020-commerce-agent-studio-mcp-capabilities.md) ·
[Implementation handoff](ARCH-020-implementation-handoff.md)

## Shopify merchant preferences acceptance — 2026-09-20

SHOPIFY-001 is architect-accepted Complete at Attempt 1 (`4693bba`, report
`c5016d73`). Merchant eligibility, explicit idempotent saves and guarded form
behavior conform; architect reran 18 passing focused checks and reviewed six
passing PostgreSQL tests plus build/browser evidence. Existing repository-wide
typecheck/lint limitations remain documented. SYSTEM-TEST-001 remains Pending
until all its implementation dependencies are accepted, then explicitly
user-invoked; no task is launched. Developer integration remains separate.

Historical pre-acceptance snapshot: 19 tasks, 4 Complete, 1 Ready, 14 Pending; superseded for BACKGROUND-001 by the Attempt 3 acceptance below.
Other canonical task worktrees remain authoritative for concurrent progress;
this review does not overwrite their state. Prior readiness records are historical.

## BACKGROUND-001 Attempt 3 architect acceptance — 2026-09-20

ARCH-020-BACKGROUND-001 is **Accepted / Complete, Attempt 3**, implementation
`4e42056`, report `7a3cf35d`. R1/R2 are resolved: persisted inbound ordering
replaces completion-time comparisons, and finishing an earlier reply does not
discard valid pending audio. Architect independently reran **133 passing tests**
and reviewed the submitted passing build and local real-SDK compatibility evidence.
The existing configurable OpenAI adapter and A1/A2 amendments are accepted.
Live audio-quality and PostgreSQL concurrency checks remain explicitly not run;
no deployed integration or acoustic-quality result is asserted.

This is the current decision and supersedes earlier BACKGROUND-001 Ready/Review
and Changes Requested notes. Other task states remain unchanged. BACKGROUND-002,
GATEWAY-001, COMMERCE-012 and SYSTEM-TEST-001 retain remaining dependency gates;
no dependent task is promoted or launched. Developer integration remains separate,
and ARCH-020 is not complete. See the task's latest Architect Review for limits.

## BACKGROUND-002 Attempt 4 — Accepted — 2026-09-21

ARCH-020-BACKGROUND-002 is **Accepted / Complete, Attempt 4**, claim cleared.
Reviewed implementation `8b2f983` and report `47345f39`; architect independently
reran **114 passing focused tests**, correcting the reported combined total110.
Evidence/provenance refresh, trusted referrals and cancellation/admission guards
conform to the component contract. Latest task review distinguishes registry,
local MCP transport and injected processor evidence from unrun integrated/live
pairing. No further coverage-only correction is required for this acceptance.
Gateway002, Commerce012 and terminal system tests retain other dependencies;
no dependent is promoted or launched. Developer integration remains separate;
ARCH-020 is not complete. Earlier BACKGROUND-002 review statuses are historical.

## COMMERCE-011 Attempt 8 review — 2026-09-21

COMMERCE-011 is **Ready, Attempt 8 retained**, claim cleared, not accepted.
Reviewed implementation `ae6acb4` and report `409b14a`; clean dedicated worktrees
and matching remote heads verified. All three Attempt 7 reproductions now pass;
R7-2 Redis cleanup is accepted. The sole remaining correction is R8-1: preserve
interleaved text/element order during document extraction (inline code currently
scrambles instructions). Independent focused validation: 19 passed; isolated
checks: 3 passed, 1 failed. See the latest canonical task Architect Review for
reproduction and correction scope. No dependent promotion or main integration.
Live validation remains developer-owned and is not an acceptance blocker.
This note supersedes previous COMMERCE-011 current-state wording.

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
## COMMERCE-006 Attempt 2 review — 2026-09-21

COMMERCE-006 is **Ready, Attempt 2 retained**, claim cleared, not accepted.
Reviewed implementation `724875d` and report `2000bccb`; dedicated worktrees clean
and remote heads matched. Working AI/FIXED, completeness, budget and pagination
improvements are retained. Corrections remain for NONE read denial, exact
fraction-to-percentage conversion, executable list/ID query documents and positive
canonical fixed amounts. Independent checks: 16 submitted reader tests passed;
five functional reproductions failed. See the latest task Architect Review.
Live Shopify remains developer-owned and is not the blocker. No dependent
promotion or main integration. This supersedes prior COMMERCE-006 current-state
wording; the narrowed C19 reader-only scope remains authoritative.

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

## COMMERCE-017 Attempt 3 architect review — 2026-09-21

COMMERCE-017 is **Changes Requested / Ready, Attempt 3 retained**, executor and
claimed_at cleared; not accepted. Reviewed implementation `64847e64` and parent
report `f3644a64` against their remote task heads. Independent UI/client tests
passed 12/12 and all four previous reproductions now pass. Four new reproductions
fail: second-run cancellation remains locked, empty catalogue permits a tool POST,
malformed HTTP failures discard uncertainty, and nullable input types bypass
validation. Direct-entry saved-source selection also remains unimplemented.
The task's A3-R1–R4 specify exact files, corrections and expected request effects;
preserve the verified prior fixes. Authenticated browser evidence remains pending
local Studio identity; source-selection implementation is still task-owned.
No new claim, dependent promotion, implementation change, main integration or
gitlink update. This overlay supersedes older COMMERCE-017 current-state wording only;
other task decisions and historical reports remain unchanged. Architecture is
not yet Implemented; COMMERCE-012 remains the final implementation checkpoint.

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

### DATABASE-003 Attempt 1 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 1 retained; executor/claim null.** Reviewed
implementation `a96dfd7` and report `cee29108`. The generated ERD whitespace
correction and expanded static validator coverage are preserved. PostgreSQL
fresh/upgrade migration and runtime checks remain unrun and are directly owned
by this migration task. No acceptance, implementation change, main merge, gitlink
update or downstream promotion. COMMERCE-020/028 remain gated on their actual
dependencies; no automatic launch.
### ARCH-020 COMMERCE-029 Attempt 4 accepted — 2026-09-21

COMMERCE-029 is **Accepted / Complete, Attempt 4** (`f22e2d6`; report `4069f60c`).
The C21 bounded QuickJS kernel now has accepted compile-only, supervisor-termination,
cleanup/recovery, packaged artifact and fixed-memory evidence. COMMERCE-026 remains
Pending because SHARED-002 is not yet Complete; no downstream task is launched and
ARCH-020 remains In Progress.
### COMMERCE-018 Attempt 1 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 1 retained; executor/claim null.** Reviewed
implementation `d074205` and parent report `686abc47`. Production Studio composition
is present, but six bounded functional corrections remain: mutation Server Actions
need the canonical Origin guard; capability publication currently sends a strict-schema
extra field; documentation search paths are double-prefixed on document fetch; release
read models do not carry the current environment pointer CAS/member-order semantics;
response validation ignores the supplied example; and U13 omits positive eligibility.
The exact correction contract is recorded in COMMERCE-018 Architect Review. Submitted
focused tests (3), typecheck, lint, build and diff hygiene pass, but do not establish
these flows. No exhaustive retest is requested and no downstream task is promoted or
launched.

## ARCH-020 SHARED-002 Attempt 5 accepted — 2026-09-21

SHARED-002 is Accepted / Complete at Attempt 5 (`95bab1d`, Shared `0.14.2`). The
direct C21 component frontier `COMMERCE-020/021/022/023/025/026/027` is Ready;
remaining extension/integration/gateway/system-test tasks stay dependency-gated.

## COMMERCE-022 pre-claim implementation review — 2026-09-21

**Changes Requested; Ready, Attempt 0 retained; executor/claim null.** Reviewed
submitted implementation `dd0164b` and parent reports `330a355` / `b74842df`.
The U15/U16 visual skeleton and Shared `0.14.2` usage are preserved, but C21 X05/XN01
is not yet satisfied: server routes pass a function-valued fixture port into a Client
Component, mutation ports bypass the canonical result/unknown-replay contract,
search/cursor return state and dirty/unknown navigation are not preserved, PER_SHOP
credentials use a free-form shop ID instead of authorized shop search/status rows,
and Overview conflates selected with latest revision. The task was implemented before
a successful launcher claim, so no Attempt 1 is invented retroactively. The next
successful `/moda-task ARCH-020-COMMERCE-022` claim creates Attempt 1 from the
already-pushed implementation branch and executes exact A0-R1–A0-R5 in the task
Architect Review. No downstream promotion or automatic launch.
### COMMERCE-020 Attempt 1 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 1 retained; executor/claim null.** Reviewed
implementation `5229b033` and parent report `29a6ffb1`. Preserve the lifecycle/CAS,
immutable-revision and transaction/audit direction. Four bounded C21 contract defects
remain: Commerce still pins Shared `0.13.1` and locally duplicates/mismatches the
accepted `0.14.2` connection contracts; the reusable command kernel omits credential
actions and an actual same-connection `FOR UPDATE` lock; development bypass does not
materialize/verify its reserved PlatformAdmin row before FK-backed writes; and lifecycle
request validation/default-port normalization is not strict (`:443` is retained and
invalid bounds may reach/clamp at Prisma). The task Architect Review contains exact
A1-R1..A1-R4 source, behavior and focused-proof instructions. No exhaustive retest,
downstream promotion or automatic launch.
## ARCH-020 COMMERCE-019 Attempt 3 readiness reconciliation — 2026-09-22

COMMERCE-019 is **Ready, Attempt 2 retained**, claim null. Architect-accepted
COMMERCE-033 (OpenAI/Groq preview model transport/config) and COMMERCE-034 (U14
Conversation source gating) resolve the two Attempt-2 blockers. All explicit 019
dependencies are Complete; the next `/moda-task ARCH-020-COMMERCE-019` claim becomes
Attempt 3.

The prepared Commerce worktree must contain the accepted 033/034 implementation after
normal synchronization. If either producer is absent, 019 returns `blocked` without
reimplementation until developer integration or explicit exact dependency-commit
consumption makes the accepted producer source available. No downstream task is
started by this reconciliation.

### ARCH-020 COMMERCE-021 Attempt 1 review — 2026-09-21

COMMERCE-021 is **Changes Requested / Ready, Attempt 1** (`b19f9d7`; report
`5abdd61a`). Preserve its fixed-origin TLS/socket and Shared 0.14.2 integration;
Attempt 2 closes production DNS/address classification, absolute stage deadline and
abort cleanup, raw JSON safety/depth and explicit dispatcher exhaustiveness. The C21
CANCELLED contradiction is reconciled to nonretryable `DEADLINE` at the
CommerceToolResult boundary; runner-level cancellation remains separate. No dependent
promotion or automatic launch.


### ARCH-020 COMMERCE-021 Attempt 3 accepted — 2026-09-22

COMMERCE-021 is **Accepted / Complete, Attempt 3**. The final corrections terminate
rejected provider bodies and preserve nonretryable external `DEADLINE` semantics
through the definition dispatcher. Existing production DNS/TLS pinning, bounded
transport and raw-JSON safety remain accepted. No dependant is newly Ready from this
acceptance alone.


## ARCH-020 COMMERCE-019 Attempt 4 acceptance — 2026-09-22

`ARCH-020-COMMERCE-019` is **Complete / Accepted, Attempt 4**. Production preview composition now consumes the accepted COMMERCE-033 preview configuration/provider transport and COMMERCE-034 U14 source-gating contracts: enabled MODEL mode injects the dedicated OpenAI/Groq preview adapter, disabled preview leaves FIXTURE provider-free, and tool-only U14 entry cannot fabricate Conversation capability state. Redis-frozen preview snapshots and replica/restart semantics from the earlier accepted corrections remain intact. No downstream task becomes Ready solely from this acceptance; GATEWAY-001 still waits on COMMERCE-018, COMMERCE-031 still waits on COMMERCE-025/030, and later integration/system gates retain their broader dependency sets.

## COMMERCE-035 Attempt 4 architect acceptance — 2026-09-22

**Accepted / Complete, Attempt 4** (`9a0120b`; parent report `b357be28`).

The C20 isolated integration fixture boundary has now executed successfully against
real task-owned disposable PostgreSQL and Redis targets. The guarded reset and
focused fixture proof passed, closing the remaining F02/F03/F05/F06 infrastructure
and relational-proof gates. Repository-wide typecheck/lint/build remain blocked only
by previously documented unrelated Shared/external-response/Connections diagnostics;
no COMMERCE-035-owned file is implicated and `git diff --check` passes.

The C20 producer gate is therefore satisfied. This acceptance does not automatically
launch a consumer and does not rewrite newer COMMERCE-018/019 task branches from the
older COMMERCE-035 parent snapshot. Reconcile each current consumer branch after this
acceptance is integrated.
## COMMERCE-020 Attempt 2 architect acceptance — 2026-09-22

**Accepted / Complete, Attempt 2** (`d2b7154`; parent report `a6d09e32`). The C21
connection-lifecycle producer now uses exact Shared `0.14.2` DTOs/results, implements
the six-action reusable command kernel, authorizes before replay, materializes the
development PlatformAdmin inside the transaction, acquires a parameterized
same-connection PostgreSQL `FOR UPDATE` lock, keeps mutation/audit atomic, validates
bounded lifecycle inputs and stores canonical HTTPS origins. Credential persistence,
resolution and encryption remain COMMERCE-028 ownership; HTTP remains COMMERCE-021.

`COMMERCE-028` is now **Ready** because its other declared prerequisites
`DATABASE-003` and `SHARED-002` are Complete. It is not automatically launched.
`COMMERCE-024`, `GATEWAY-003`, `COMMERCE-012` and system-test work remain gated by
their other authoritative dependencies.

## COMMERCE-030 Attempt 3 architect acceptance — 2026-09-22

**Accepted / Complete, Attempt 3** (`d15d3f5`).

The C21 external publication/sample validator now shares the lifecycle's canonical
`toolHashInput(definition)` identity and admits synthetic samples/publication from
persisted non-secret connection revision state (`enabled`, `revisionPresent`,
`scope`, `authMode`, `authHeader`) without requiring live merchant credentials.
Active-staff receipt semantics, strict 24-hour TTL, sample MIME/schema validation,
production renderer reuse and later real-provider runtime validation remain intact.

`ARCH-020-COMMERCE-031` is **Review, Attempt 5**, with implementation `abb02d9`
and executor/claimed_at null. Architect review is required before downstream
promotion. COMMERCE-024 and COMMERCE-012 remain Pending behind their other
authoritative prerequisites.
## COMMERCE-018 Attempt 7 architect review — 2026-09-22

**Changes Requested / Ready, Attempt 7 retained.**

The real C20 infrastructure gate is now closed: disposable PostgreSQL/Redis health,
fixture reset, 4/4 real Studio integration scenarios, 9/9 focused adapter tests and
container cleanup all pass. The production Studio adapter remains accepted in
substance.

The remaining COMMERCE-018 task-owned requirement is C20 I01 / S01: the real suite
must perform one full authoring traversal through production `StudioServices`
(create tool/draft/publish, create capability/draft/publish, create release,
activate, rollback) rather than only operating on COMMERCE-035's pre-seeded
published graph. Attempt 8 is limited to that deterministic proof plus explicit
saved-draft preservation during the intentional discovery outage unless the real
flow exposes a bounded 018-owned defect. No downstream task is promoted.
## COMMERCE-037 Attempt 1 architect acceptance — 2026-09-22

**Accepted / Complete, Attempt 1** (`021dcf7`; parent report `15d9588b`).

The read-only credential availability boundary is normalized so `shopId` means
trusted merchant identity. Immutable revision scope now selects the credential row:
PLATFORM uses the null-scope row; PER_SHOP uses only that merchant's row. Credential
status/mutation/resolution retain their existing nullable credential-scope semantics.
No decryption, mutation or fallback is added to availability.

COMMERCE-032 remains Ready and explicitly records COMMERCE-037 as a prerequisite.
No downstream task is launched automatically.
## COMMERCE-032 Attempt 2 architect acceptance — 2026-09-22

**Accepted / Complete, Attempt 2** (`b8d8ccd`; parent report `99f4b90c`).

The read-only external availability consumer is now proven against the accepted
COMMERCE-037 producer semantics: trusted merchant identity is passed unchanged into
`checkConnectionAvailability`, PLATFORM credentials are selected at null scope by
the producer, and PER_SHOP isolation remains merchant-specific. Existing resolver
behavior preserves original grant pinning, exact tool/revision/capability identity,
explicit current exclusions and typed lookup outage without provider calls, secret
access, grant writes or cross-call caching.

No downstream task becomes Ready solely from this acceptance. COMMERCE-024 and
COMMERCE-012 remain behind their other authoritative dependencies.

## COMMERCE-031 Attempt 1 architect review — 2026-09-22

**Changes Requested / Ready, Attempt 1 retained.**

The first external-preview slice correctly reuses COMMERCE-025/026 processors,
COMMERCE-030 receipt validation and the existing preview result store, but does not
yet satisfy PR01-PR03. Same-operation replay is currently recognized only after
external quota/receipt validation, tool-test cancel is absent, caller-supplied
definition remains authoritative, and conversation external fixtures are frozen in
state but ignored during conversation tool execution. Attempt 2 is bounded to those
producer-owned corrections and their named focused evidence.

COMMERCE-024 and COMMERCE-012 remain gated; no downstream task is launched.

## COMMERCE-031 Attempt 2 implementation checkpoint — 2026-09-22

**Ready, Attempt 2 retained; claim cleared.**

The external-preview lifecycle corrections requested after Attempt 1 are now present
in source and accepted in substance: saved definitions are server-owned/frozen,
preview replay is claimed before quota/receipt/processor work, tool tests support
cancel/expiry on the same run identity, conversation fixture bodies are aggregate
bounded and frozen, and synthetic external conversation calls have an injected
runner path.

The remaining COMMERCE-031 gate is named PR01-PR03 proof plus durable mirrored
handoff. The next launcher claim is Attempt 3 and must not broaden into new preview
architecture or downstream integration. COMMERCE-024/012 remain gated.

## COMMERCE-031 Attempt 3 architect review — 2026-09-22

**Changes Requested / Ready, Attempt 3 retained.**

The external-preview implementation is substantially conformant: saved definitions
are server-owned/frozen, replay claims precede business side effects, tool tests
support same-ID cancel/expiry state, and conversation external definitions/fixtures
are frozen with a synthetic runner hook. Attempt 3 also adds successful visual and
JavaScript sample paths.

Remaining work is bounded to: normalize parameterized sample MIME before comparison;
prove the external-preview replay/quota/cancel/expiry contract against the actual
Redis preview store; exercise frozen conversation external fixtures through the
synthetic runner with zero live provider/credential calls; and reconcile the
unchecked Work Items/PR criteria only after that evidence exists.

COMMERCE-024 and COMMERCE-012 remain gated. No downstream task is launched.

## COMMERCE-031 Attempt 4 architect review — 2026-09-22

**Changes Requested / Ready, Attempt 4 retained.**

The external-preview lifecycle implementation remains substantially correct and the
new foreign fixture rejection is valid. Acceptance is still blocked by three
task-owned items: normalize parameterized sample MIME before the saved allowlist
comparison; prove replay/quota/cancel/expiry through the actual Redis preview store;
and exercise the successful frozen conversation external-fixture path with explicit
zero live provider/credential execution.

Attempt 5 is bounded to those corrections/evidence and Completion Report
reconciliation. COMMERCE-024/012 remain gated and no downstream task is launched.

## COMMERCE-031 Attempt 5 architect acceptance — 2026-09-22

**Accepted / Complete, Attempt 5** (`abb02d9`; parent report `5f334581`).

The external response preview backend now satisfies PR01-PR03: actual visual and
JavaScript processors run through the accepted preview/receipt lifecycle; saved
definitions are server-owned and frozen; replay claims precede quota/receipt/processor
side effects; Redis-backed cross-instance replay, conflict, cancellation, expiry and
different-new-run quota behavior are proven; MIME parameters are normalized; and
conversation external fixtures execute through the frozen synthetic path without
normal live tool execution. Invalid foreign/non-external fixtures and malformed or
oversize response samples fail closed.

`ARCH-020-COMMERCE-024` is now **Ready** because every declared dependency is
Complete. It is not automatically launched. COMMERCE-012 and system-test work retain
their remaining integration/gateway gates.

<!-- Preserved task-branch record. -->
## COMMERCE-024 Attempt 1 blocked / COMMERCE-038 created — 2026-09-22

COMMERCE-024 is **Blocked, Attempt 1 retained**.

The submitted implementation correctly refused to represent the missing XN04
composition as successful, but review identified two distinct causes.

First, its implementation base is stale relative to accepted COMMERCE-019
implementation `8850b55`: the accepted preview adapters are absent and the production
runtime still uses `unavailableLoader`. That accepted implementation must be
developer-integrated into the canonical Commerce implementation base before 024 is
reclaimed.

Second, accepted COMMERCE-031 does not export the reusable
`PreviewExternalFixtureRunner` required to inject frozen external synthetic fixtures
into production Conversation preview without copying 031 processing logic.
`ARCH-020-COMMERCE-038` is created **Ready, Attempt 0** to export only that producer
seam.

024's current changes under connection command/lifecycle producer files are outside
its composition ownership and must not be carried forward after resynchronization.
Final composition remains 024-owned after both unblock conditions are satisfied.

No downstream task is launched; COMMERCE-012 and SYSTEM-TEST-002 remain gated.

## COMMERCE-024 unblock reconciliation — 2026-09-22

**Ready, Attempt 1 retained; claim cleared.**

The two blockers recorded by COMMERCE-024 Attempt-1 review are now resolved in the
canonical Commerce implementation base.

Developer verification on main
`4e01e20ea3f94e6125b8017340d869d5198db6d0` proves accepted COMMERCE-019
implementation `8850b55` is an ancestor, the production preview adapters/runtime are
present and `unavailableLoader` is absent. Accepted COMMERCE-038 implementation
`16972af` is also an ancestor and `createExternalFixtureRunner` is present.

COMMERCE-024 may therefore be reclaimed. The next launcher claim creates Attempt 2
exactly once and is limited to the previously defined composition-only contract.
COMMERCE-012 and SYSTEM-TEST-002 remain gated until 024 is accepted Complete.

A local untracked `typescript` artifact was present in the developer main worktree;
it is not part of the accepted source and should be moved/removed before launch rather
than committed.
<!-- Preserved mainline record. -->
## GATEWAY-001 Attempt 4 architect acceptance — 2026-09-22

ARCH-020-GATEWAY-001 is **Complete / Accepted, Attempt 4** (`478923a`; parent
report `cb41f7c`). The Render/private-MCP/public-Studio topology and final hosted
smoke contract are accepted. Real deployment/DNS/TLS/OAuth/assertion smoke remains
a developer validation checkpoint, not an unfinished implementation dependency.

Because their remaining prerequisites are already Complete, GATEWAY-003 (priority
175) and GATEWAY-002 (priority 190) are now **Ready, Attempt 0, claim clear**.
Neither is started automatically. COMMERCE-012 and system-test work retain their
additional dependency gates.

## COMMERCE-038 Attempt 1 architect acceptance — 2026-09-22

**Accepted / Complete, Attempt 1** (`16972af`; parent report `f107b817`).

The reusable external synthetic fixture-processing seam required by final production
composition is now available from the accepted COMMERCE-031 producer. It shares the
same visual/JavaScript processing kernel as tool-test execution and introduces no
quota, receipt, provider, credential or preview-state side effects.

COMMERCE-024 remains blocked on its separate implementation-base condition: accepted
COMMERCE-019 source `8850b55` is still not present in the Commerce source reviewed in
this task. Once that source is developer-integrated, a fresh synchronized 024 snapshot
can be returned to `moda_architect` for Blocked -> Ready reconciliation.

No downstream task is launched automatically.


## ARCH-020 Grafana ownership decision — 2026-09-22

GATEWAY-002 is Superseded at Attempt 2. Custom Commerce dashboards and alerts are
developer-managed in Grafana Cloud; repository-owned telemetry emissions and existing
OTLP/Loki transport remain unchanged. No implementation or system-test task depends on
GATEWAY-002 after this reconciliation.

## COMMERCE-024 Attempt 2 architect review — 2026-09-22

**Changes Requested / Ready, Attempt 2 retained; claim cleared.**

The former producer blockers are resolved: accepted COMMERCE-019 preview composition,
COMMERCE-036 connection compatibility handling and COMMERCE-038 reusable fixture
processing are present in the synchronized source.

Attempt 2 successfully wires the external preview service/fixture runner into the
accepted preview runtime direction, but final composition is not yet complete. The
COMMERCE-030 identity adapter incorrectly treats saved DRAFT revisions as an empty
definition hash/disabled revision; EXTERNAL_HTTP publication is fail-open if the
external publication validator is absent; the submitted XN04 proof constructs an
isolated in-memory PreviewService instead of traversing production composition; and
WI01's publish -> release -> grant -> assembled MCP execution path is still unproven.

Attempt 3 is bounded to those 024-owned corrections/evidence. Accepted connection and
external producers must remain unchanged. COMMERCE-012 and SYSTEM-TEST-002 remain
gated.

## COMMERCE-024 Attempt 3 architect review — 2026-09-22

**Changes Requested / Ready, Attempt 3 retained; claim cleared.**

The saved-DRAFT identity and fail-closed external publication binding are now accepted
in substance. The remaining gate is final production composition evidence only.

XN04 currently installs a prebuilt in-memory PreviewService rather than proving
`productionService()` plus the real U14 POST/GET route identity. WI01 currently
constructs manifest/grant state in test code, overrides assertion verification and
calls the executor directly rather than persisting publication/release/grant state and
calling the assembled `backend.mcp` JSON-RPC `tools/call` endpoint.

Attempt 4 is bounded to those two proofs and report reconciliation. Accepted producer
implementations remain unchanged. COMMERCE-012 and SYSTEM-TEST-002 remain gated.

## COMMERCE-024 Attempt 4 architect review — 2026-09-22

**Changes Requested / Ready, Attempt 4 retained; claim cleared.**

The merge-conflict resolution preserving both EXTERNAL_HTTP and POLICY_OPERATION
availability is accepted in substance. The already-accepted DRAFT identity and
fail-closed publication fixes also remain intact.

The outstanding gate is unchanged: XN04 must traverse the Redis-backed production
preview runtime through the actual U14 POST/GET routes, and WI01 must persist the
real publication/release/grant lifecycle and invoke a signed assembled
`backend.mcp` JSON-RPC `tools/call`. The current 4/4 wiring suite still uses the
in-memory/direct-executor substitutes rejected in Attempt 3.

Attempt 5 is bounded to those proofs and report reconciliation. COMMERCE-012 and
SYSTEM-TEST-002 remain gated.

## COMMERCE-024 Attempt 5 infrastructure unblock — 2026-09-22

**Ready, Attempt 5 retained; claim cleared.**

Missing `COMMERCE_TEST_DATABASE_URL`, `COMMERCE_TEST_REDIS_URL` and
`COMMERCE_C20_REDIS_NAMESPACE` no longer block the final COMMERCE-024 integration
proof. They are optional complete-set overrides. Attempt 6 must create its own
task-owned disposable PostgreSQL/Redis targets when absent.

The self-provisioning runner must reuse the accepted local-Docker safety pattern from
`moda-interact-commerce/scripts/readiness-docker.mjs`: local Unix-socket context,
pinned PostgreSQL/Redis images, loopback-only random ports, tmpfs, generated
credentials, task ownership labels, safe C20 database/Redis namespace naming, schema
preparation only against the disposable database, signal-aware cleanup and a final
zero-owned-resource check.

The outstanding XN04 production preview POST/GET proof and WI01 persisted
publication/release/grant + signed `backend.mcp tools/call` proof remain the
acceptance gate. COMMERCE-012 and SYSTEM-TEST-002 remain gated.

## COMMERCE-024 Attempt 6 architect closeout — 2026-09-22

**Accepted / Complete, Attempt 6.**

The production external API tool composition is accepted as functionally complete
from source and focused integration review. The accepted preview/runtime, external
fixture, credential, HTTP, processor, publication and availability producers are
bound without duplicating their business algorithms. Saved-DRAFT identity and
fail-closed EXTERNAL_HTTP publication behavior are preserved.

The architecture no longer requires COMMERCE-024 to introduce substantial
test-oriented factoring solely to automate the entire persisted WI01 lifecycle.
That full connection -> receipt -> publication -> release -> persisted grant ->
signed MCP `tools/call` proof is transferred to the already-defined manual
SYSTEM-TEST-002 cross-service validation task.

This closeout does not claim that the manual end-to-end flow has already passed.
Defects found during manual validation are routed to the concrete owner identified by
the first failing stage.

COMMERCE-012 and SYSTEM-TEST-002 remain Pending in this snapshot because GATEWAY-003
is not Complete.

## ARCH-021 — CommerceAgent configuration and live Studio authoring (2026-09-23)

Agreed architecture. Model selection and the editable CommerceAgent behavioural prompt
are platform/shop configuration with independent shop-override -> platform-default
fallback. Features/releases do not own prompts or models. Platform admins author
application-wide and shop-specific prompts; later merchant access reuses the shop-scoped
prompt boundary. Production conversation grants and Studio preview sessions freeze the
resolved model/prompt identities without making them release-owned.

Phase 1's six Commerce-only tasks for real Connections composition, server-validated
`shopId` context, production external connection selection and JavaScript response-panel
installation are architect-accepted Complete.

Phase 2 is architect-accepted Complete across its Database and Commerce tasks, including
the bounded COMMERCE-015 prompt-template revision-history read contract and the accepted Agent
Configuration, prompt-template and platform-prompt authoring surfaces. Shop override CAS uses
immutable row-generation tokens plus edit versions so clear/recreate cannot ABA-match stale
mutations.

Phase 3 is materialised for complete Tool authoring without live provider execution.
COMMERCE-016 is architect-accepted Complete: Commerce now owns the canonical persisted Tool
definition while Shared remains pinned at exact 0.14.2. The independent current Ready frontier is
COMMERCE-017 (bounded request JavaScript), COMMERCE-018 (Shopify Admin GraphQL compiler),
COMMERCE-019 (common authoring validation/publication gate), and COMMERCE-020 (Tool authoring
domain extraction).

[Architecture](ARCH-021-commerce-agent-configuration-live-studio-authoring.md)
