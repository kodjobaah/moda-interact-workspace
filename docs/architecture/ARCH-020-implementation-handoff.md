# ARCH-020 implementation handoff

Canonical architecture: [CommerceAgent Studio and merchant-configured MCP capabilities](ARCH-020-commerce-agent-studio-mcp-capabilities.md).

## Initial review packet and definition frontier

COMMERCE-001 is architect-accepted Complete at Attempt 3 (`d7c1c65`). The descendant-process cleanup correction passed focused functional validation; prior real Docker PostgreSQL/Redis readiness evidence is retained. COMMERCE-002 is architect-accepted Complete at Attempt 2 (`fb3362e`): development HTTP mutations and revoked-session recovery are corrected. Live Google OAuth remains developer-owned deployment validation. Downstream source consumption awaits developer integration or explicit accepted-commit approval; no task is promoted or launched. COMMERCE-001 remains accepted and integrated. Other task rows retain this branch snapshot; canonical task worktrees remain authoritative.

The consolidated packet contains 19 tasks; SHARED-001 owns contracts, runner and publication. The original definition/provisioning records below are historical setup evidence. Ready status elsewhere in this packet does not launch execution.

Confirmed choices: `moda-interact-commerce`, team-only Studio frontend,
`database/` nested submodule of `moda-interact-database`, private Background-only
MCP, administrator UI via Gateway, and pre-production breaking rollout.

## New-owner registration delivered in this packet

- `.codex/agents/moda_commerce.toml`: owner of Commerce only, following the
  existing common task/worktree/validation protocol and explicit service boundaries.
- `.claude/agents/moda_commerce.agent.md`: generated using `scripts/sync_agents.py`.
- `scripts/start-agent-task.py`: COMMERCE maps to `docs/decisions/commerce`,
  `moda_commerce`, and `moda-interact-commerce`.

The host may need to reload agent configuration before it can invoke the newly
defined logical role. A file definition is not a claim that this already-running
session has a new callable agent type. Do not substitute another repository owner
or use a shared checkout to bypass a missing runtime registration.

## Repository provisioning checkpoint

Developer/architect coordination owns this setup before COMMERCE-001 is promoted.
It is recorded explicitly here because a repository task cannot prepare its own
implementation worktree before that repository exists. It is not a system-test
dependency and does not permit implementation on main.

- [x] Created private repository `https://github.com/kodjobaah/moda-interact-commerce.git`
  in the same account as the existing components. GitHub confirms default branch
  `main`; its initial README-only commit is
  `01c550c3e3f55dd23a4ecc9514c846bb88cf2067`.
- [x] Registered `moda-interact-commerce` in workspace `.gitmodules` and pinned
  its gitlink to that initial main commit. No application code is provisioned.
- [x] Reviewed packet is integrated in workspace main (`20e720d3`). This readiness
  correction follows the user's authorization to fix preparation and publish on main.
  Execution must synchronize this correction from main before claiming.
- [x] COMMERCE route resolves the real repository and the configured `moda_commerce`
  role; agent definition synchronization is checked. Runtime host role loading is
  still a launcher concern, not an assertion that application implementation exists.
- [x] Architect promotes COMMERCE-001 from Blocked to Ready on 2026-09-20 and
  reconciles task, domain index, architecture table and workspace rollup. The task
  remains unclaimed at attempt 0. This is provisioning acceptance only.

COMMERCE-001 then adds the **nested** submodule at `database/` from
`https://github.com/kodjobaah/moda-interact-database.git`, provides the application
foundation and proves recursive initialisation/client generation. DATABASE-001
owns subsequent schema changes; consuming tasks update to its accepted integrated
database revision. Never copy the Prisma schema into Commerce.

## Execution sequence

```text
003 publication +004/014 MCP +005/015 products +006/016 discounts +007 recommendations +011 compiler ->013 backend integration
013 +008 Studio +002 auth +011 discovery ->018 Studio integration
013 +009 preview +017 U14 +008 composer +002 auth ->019 preview integration
018 and019 run concurrently; neither depends on the other
013 +018 +019 + existing prerequisites ->GATEWAY-001
all feature/infrastructure tasks ->012 caching ->terminal SYSTEM-TEST-001
```

Individual task YAML contains the exact complete dependency sets. Runtime call
direction does not imply unnecessary implementation dependencies: Background can
implement against shared contracts and local server fixtures while Commerce is
built. Actual client/server compatibility must be verified before acceptance.

Each executor reads the full task/architecture and latest review, uses normal
dedicated mirrored task branches, publishes its task-owned implementation and
Completion Report, then stops at review. The architect accepts implementations,
reconciles current prerequisite records and promotes newly eligible tasks.
Use the actual published shared version. SHARED-001 implements and validates both
exports, publishes them together and verifies a clean registry installation before
completion. It does not begin consumer implementation.

## Private MCP and administrator UI acceptance

GATEWAY-001 owns the canonical `moda-interact-gateway/render.yaml` changes.
Commerce is a private service; Background addresses MCP through the private
network. The public gateway exposes an explicit Studio UI/auth route set and
rejects MCP routes, aliases and normalised route variants. Staff login is checked
inside Next.js as well as at routing boundaries.

Other services may share Render private-network reachability; this is not an
authorisation grant. Only Background has the production signing credential.
Commerce verifies short-lived Background assertions and durable tenant/turn
ownership on every live MCP call. Administrator sessions cannot call live MCP,
and Studio preview uses isolated local fixtures rather than a public MCP proxy.

Required checks include valid Background private access, other-principal denial,
public MCP denial across verbs/path variants, authenticated administrator UI
access, expired/revoked staff denial and no preview-to-production credential path.

## Studio authentication

COMMERCE-002 explicitly uses NextAuth.js (`next-auth`), following the existing
Admin Google OAuth/JWT implementation and reading the same `public.PlatformAdmin`
identities, active status and roles through the canonical database submodule.
No second staff directory or new NextAuth User/Account/Session tables are needed.
Verified email, atomic provider-subject binding and current per-request identity
checks are required. The current proposal uses a separate Studio browser session;
automatic sign-on from Admin is outside the v1 default and must not be assumed from
shared tables. Staff sessions never grant production MCP access.

## Validation and rollout

The architecture is explicitly pre-production and does not require compatibility
with the old hard-coded agent. Database migrations are additive and run once;
preserve durable data. Publish Shared, deploy Commerce and publish a reviewed
initial release, then coordinate the Background/merchant UI switch with affected
conversation workers paused and prepared reservations reconciled. Do not flush
Redis, alter unrelated queues or add legacy compatibility adapters.

Fast local checks belong to repository agents. Long container, load and live
Shopify/Render/WhatsApp/model checks follow the developer validation policies.
Record exact commands and evidence; do not mark unrun validation as passed.
After all implementation dependencies are accepted Complete, the developer can
manually exercise the feature, then explicitly invoke the Ready system test.
No implementation task depends on that terminal system test.

## Review points

Review the proposed initial native-basic discount support boundary, staff role
split and execution ceilings. Those are concrete draft design choices, not
promises that arbitrary Shopify offers can be evaluated. Missing authoritative
eligibility facts produce Unknown/Unsupported, not a checkout guarantee.

## Deterministic database contract and conversation scope

DATABASE-001 now specifies all nine exact tables, columns/types/defaults,
enums, FKs/indexes, SQL guard requirements and named validation artifacts.
Shared, Commerce publication and Background pins must consume that contract.
ARCH-020 accepts only WhatsApp conversations linked to an existing checkout
recovery. Resolve shop ownership through that recovery; reject missing/sentinel
recovery IDs and do not add a standalone conversation path. Existing unrelated
platform records are preserved; no conversation-schema cleanup is authorised.

## UI duplicate-action acceptance

All UI work (COMMERCE-001/002/008/009 and SHOPIFY-001) must include immediate
submission guards, disabled conflicting controls, accessible pending feedback
and deliberate retry after known failures. COMMERCE-003 owns transactional
operation replay using the existing audit ID; preview owns atomic existing-Redis
run deduplication across instances, wired by GATEWAY-001. Direct duplicate
requests must be safe even when browser controls are bypassed. SYSTEM-TEST-001
verifies one business effect/model invocation and recovery after failure.

## Conversation-lifetime grants and grounded referrals

The original per-turn snapshot design is superseded. DATABASE-001's seventh table
is now CommerceConversationGrant, unique by conversationId, with initialInboundVersion
and exact grantedTools. Initialise it before the first admitted CommerceAgent call;
all later messages/retries retain that grant and its prompt release. New releases
or merchant feature additions apply only to newly granted conversations. Current
revocation can restrict the original grant, never add tools. Do not reset/recreate
a grant to bypass this rule.

Questions must be answered using originally granted tools and trusted recovery
facts. If the agent cannot verify an answer, it returns REFER_TO_STORE; Background
renders one localised store referral using verified contact/domain data, with no
invented answer/address or claim of a human handoff. Shared schemas/runner, MCP
server, Background, Studio preview and terminal tests all specify this contract.

## WhatsApp correlation and clarification implementation

[Binding implementation contracts](ARCH-020-implementation-contracts.md) C0–C3
close the earlier routing design gates. Reuse Shared inbound v1/status v2 unchanged.
A validated explicit reply routes to its recovery; one distinct recovery for an
ordinary message routes automatically; multiple/zero candidates receive fixed
platform guidance. No time window, recency or remembered channel selects a basket.

No WhatsApp schema changes are required. The user selected lightweight guidance:
Background claims a 24-hour Redis guard before one fixed-text send, preserving it
on failure. Existing raw-abuse limits apply. Accepted trade-offs are possible
missed guidance after a crash and duplicates after Redis loss/expiry. DATABASE-002
was removed while unclaimed; its proposed batch-version field is deferred.
BACKGROUND-001 still depends on DATABASE-001 for Commerce grants and COMMERCE-001
for SDK compatibility. Existing batching and inbound/status schemas are unchanged.

## Determinism review and execution inputs

All 19 tasks contain explicit contracts/guidance and expected validation evidence.
The companion defines strict tool arguments/results, service assertions, grants,
publication/replay operations, preview budgets, gateway routes and initial alert
thresholds. Per-task implementation helpers may follow repository conventions;
external wire/state/ownership contracts may not vary between implementations.

Remaining external inputs are the Studio hostname and provisioned credentials.
Commerce repository/default-branch provisioning is complete; COMMERCE-001 is architect-accepted Complete at Attempt 3; developer integration precedes downstream source consumption, and the authorized real Docker readiness evidence is retained.
Pin/test actual SDK dependencies in that foundation task;
Shopify schema/scope evidence belongs to COMMERCE-006, with closed unsupported
outcomes when provider facts cannot be established. Do not invent deployed values,
mark unrun live validation passed, or alter scopes outside an explicit owner task.

The review adds deterministic defaults (separate Studio session, platform-owned
identification guidance costs/limits and bounded budgets) for developer review;
none of this document constitutes a production rollout or implementation claim.

C13 preserves initial outreach/follow-up/continuation distinctions and accepted ARCH-016-BACKGROUND-003 behaviour, now an explicit BACKGROUND-001 prerequisite. Each proactive message keeps its own provider ID while both attempts share the same recovery Conversation.

[Task-definition review and validation](ARCH-020-task-definition-review.md).

Shared-channel clarification: Moda owns the initial WhatsApp number for all merchants. C2 and Background/system-test tasks explicitly cover separate shop Customer records sharing one phone and count recovery candidates across merchants before selecting a shop. Additional-number design is outside current scope.

Reusable-tool amendment: nine-table persistence separates CommerceTool and
CommerceToolRevision from capability toolBindings. C14 permits authored public
Shopify queries without per-business-tool handlers; policy helpers retain privileged
checks. C15/COMMERCE-011 provides core in-Studio discovery. COMMERCE-008 contains
all U01–U13 pages/traversals and COMMERCE-009 U14; their prerequisites include the
actual discovery, publication and execution services. No implementation is claimed.

## Response-contract authoring amendment

C16 adds release-owned response instructions and details schemas, U10/U11 authoring
and U14 preview. Shared retains a stable delivery envelope with generic validation;
CommerceRelease gains two fields, no new table. Nine owning tasks carry explicit
implementation/acceptance requirements. Existing dependency edges already place
persistence/contracts before publication/runtime/UI; no new task or readiness
promotion is required. Published definitions are pinned through grant.releaseId.
The original visual prototype predates the C16 release-panel extension; the exact
page specification in the UI design and COMMERCE-008 is authoritative for it.

## Shared task consolidation

By developer request, the unclaimed Shared contracts, runner and publication
definitions are consolidated into ARCH-020-SHARED-001. The two superseded draft
files were removed before execution; their requirements remain in SHARED-001.
One task owns implementation, tests, publication and clean registry installation
evidence. Consumers depend on its architect-accepted Complete state and recorded
package version. Historical snapshot after COMMERCE-001 acceptance: 19 tasks, 1 Complete, 2 Ready, 16 Pending, 0 Blocked. The synchronized current frontier is recorded below. COMMERCE-002 source integration was subsequently verified; it is now Ready, unclaimed at Attempt 0.
No execution was claimed and no package was published by this documentation change.

## Historical DATABASE-001 architect review — Attempt 1 — 2026-09-20

Attempt 1 is **Changes Requested**, task `ready`, attempt 1, claim cleared.
The implementation/report PRs are #33/#165 (0e992c4 / 312e350b). Preserve the
implementation and rehearsal history. Required corrections are the newer C16
CommerceRelease responseContract/responseContractHash persistence and negative
fixtures that currently permit unrelated constraint failures. The full correction
contract is in the task's Architect Review. C16 was incorporated by parent synchronization commit 7fef4689 from canonical
workspace commit a710df26; its semantic consumer requirements remain binding.

Guarded writes require READ COMMITTED or SERIALIZABLE with bounded transaction
retries; REPEATABLE READ is rejected. BACKGROUND-001 and COMMERCE-003 must honor
that database restriction when implementing grants/publication. No dependency is
promoted by this review; SYSTEM-TEST-001 remains terminal and manually invoked.
Other task states in this branch's older definition snapshot are not a fresh
review of their separate execution branches. Integrate latest parent main before
reclaiming this task, preserving its report, review and attempt metadata.

## DATABASE-001 architect acceptance — 2026-09-20

ARCH-020-DATABASE-001 is **Accepted / Complete, Attempt 2**. Implementation
30de940 (tested source a835207) and report 17c9f9ab satisfy R1 C16 response
persistence and R2 rejection-fixture isolation. Reviewed 298 distinct passing
checks per fresh/upgrade rehearsal, including controls; preservation covers
57 existing tables, 41 seeded rows and 217 indexes. Static/Prisma checks passed.
The previous Changes Requested section is historical and superseded.

No downstream promotion: canonical SHARED-001 is in_progress, COMMERCE-001 is
review, and COMMERCE-002/011 remain pending. BACKGROUND-001 and COMMERCE-003 still
have incomplete prerequisites. Terminal SYSTEM-TEST-001 remains pending/manual.
Other task table rows are branch-local snapshots, not fresh acceptance decisions.

Guarded consumers use READ COMMITTED or SERIALIZABLE with bounded whole-transaction
retries; REPEATABLE READ is rejected. Shared/Commerce own semantic response-schema
validation and canonical hash equality; Commerce owns atomic release assembly,
authorization and audit. Merge database PR #33 first, pin its final integrated
database-main commit in the parent, then merge parent PR #165. No main integration
or gitlink update is performed by this acceptance. ARCH-020 is not Implemented.

## Shared Attempt 1 architect review — 2026-09-20

ARCH-020-SHARED-001 returned to Ready with Changes Requested against implementation
34be970 and report f713caed: R1 whole-definition persistence size compatibility;
R2 malformed model-call error classification. Attempt 1 is preserved and the
claim is clear. Package 0.13.0 is published but not architect-accepted; corrections
require a new verified registry version. No downstream task is promoted.
See the canonical Shared task's latest Architect Review for the correction contract.
Parent main synchronization preserves DATABASE-001 Complete at Attempt 2 and
COMMERCE-001 Complete at Attempt 3 alongside this Shared correction contract.
Current branch frontier: 19 tasks, 2 Complete, 1 Ready, 16 Pending, 0 Blocked.
SHARED-001 remains Ready at Attempt 1 with no active claim. No next attempt is
claimed by conflict resolution. Architecture completion/system-test gates remain.


## Shared Attempt 2 acceptance — 2026-09-20

ARCH-020-SHARED-001 is **Accepted / Complete, Attempt 2** against implementation
a83bfc1 and report 595566ca. R1 storage-size compatibility and R2 malformed-model
classification are closed. Independently passed typecheck, 30 focused tests and
clean registry-consumer smoke; reviewed 160-pass/one-skipped full-suite evidence.
Verified registry artifact **@modainteract/moda-interact-shared@0.13.1**, with all
75 installed files matching publication files. Consumer tasks must use 0.13.1.
The earlier Shared correction/frontier record is historical and superseded.

BACKGROUND-001 (moda_background) and SHOPIFY-001 (moda_app) are newly Ready: all
listed dependencies are Complete. No task is claimed or launched. Preparation
must synchronize dedicated worktrees and verify dependency source availability.
Other pending tasks retain their existing gates. Current branch frontier:
**19 tasks, 3 Complete, 2 Ready, 14 Pending, 0 Blocked**. System testing remains
terminal/manual; ARCH-020 is not Implemented. No main merge or gitlink change.


## BACKGROUND-001 review scope amendments — 2026-09-20

BACKGROUND-001 remains **Review, Attempt 1**, with no active claim or acceptance.
User A1/A2 add deterministic shop/phone-country initial language and approved
initial/follow-up template selection, then substantive text/speech language;
and configurable OpenAI spoken-language transcription alongside retained Groq.
These are **scope amendments, not defects against the original task**. See the
canonical task's named A1-L01–L06/A2-V01–V07 cases and binding C6.2/C6.3.
Shared/Database phone-country provenance prerequisites require separate new-scope
materialisation/acceptance; Gateway owns hosted provider/model/secret wiring.
The submitted implementation/report and accepted prerequisite history remain.
No new attempt or downstream task is launched; expanded-scope acceptance pending.

## Caching backlog addition

COMMERCE-012 adds one Pending final implementation task; active scope is now 20
tasks. Its prerequisites are all 18 other nonterminal ARCH-020 tasks; SYSTEM-TEST-001
depends on it. Earlier 19-task counts predate this addition. Before promotion, resolve
its explicit policy persistence/API/UI checkpoint and any owner-specific prerequisite
tasks. No execution or cache enablement is authorized by task authorship alone.

## Simplified language decision — 2026-09-20 (current)

The user withdrew phone-country inference: initialize from shop language, then
respond in clearly detected customer text/speech language. C6.2 and BACKGROUND-001
A1 specify this rule. Earlier phone-country/Review coordination notes are historical
and superseded. Both unclaimed provenance tasks were removed with their dependency
edges. BACKGROUND-001 is Ready, Attempt 1 retained, no active claim; A2 transcription
scope remains. All four retained prerequisites are accepted Complete. Active task
scope returns to 20; no automatic execution or expanded-scope acceptance occurred.


## BACKGROUND-001 Attempt 2 architect review — Changes Requested

Reviewed implementation 399cc2f and report 0ed91909. **Ready, Attempt 2 preserved,
claim cleared**, not accepted. R1 confuses earlier audio completion time with a
new message's sent time; R2 treats completion of the preceding reply as superseding
new audio. Both reproduce as ignored valid messages. The canonical task's latest
Architect Review contains the correction contract and validation expectations.
The original A1/A2 scope amendments are not retroactive defects; these findings
concern the submitted amended implementation. Simplified shop-language scope
remains; no phone-country prerequisites are restored. No downstream promotion or
new attempt is claimed. Older Background review/in-progress/readiness statements
are historical; this is the current decision. Architecture remains unaccepted.

## BACKGROUND-001 user-directed review hold

Current status: Review, Attempt 2, no active claim. User requested no re-preparation or new claim. This supersedes the prior Ready/preparation direction only; R1/R2 remain unresolved against implementation 399cc2f and acceptance remains withheld. No downstream promotion.

## BACKGROUND-001 return to Ready

Latest user instruction restores Ready for reviewed R1/R2 corrections, Attempt 2, executor/claimed_at null. This supersedes the preceding Review hold. Acceptance remains withheld; no preparation, new claim or downstream promotion is performed by this update.

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


## Parallel start frontier — 2026-09-21

003 and008 are Ready, unclaimed, for independent component implementation and
acceptance against C17 ports.011 continues separately. New013 connects real
services after003/004/005/006/007/008/011 are accepted;009 and GATEWAY-001 now wait
for013.012 and terminal system testing also explicitly depend on013. No task is
launched by this amendment. Fixtures never become production service fallbacks.


2026-09-21 C18 frontier: BACKGROUND-002 promoted Ready, unclaimed, after accepted
BACKGROUND-001. COMMERCE-007 retains its own evaluator prerequisite but no longer
blocks the consumer. SYSTEM-TEST-001 owns EC01–EC12 real-service pairing.

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

## Smaller task frontier — 2026-09-21

C19 replaces combined004/005/006/009 scopes and adds014/015/016/017. Every
predecessor task keeps its existing ID/path. No attempted task is split or reset.
Component and assembly evidence owners are explicit; no task is launched here.


## BACKGROUND-002 Attempt 1 — Changes Requested — 2026-09-21

Current state: Ready, Attempt 1, claim cleared; not accepted. Reviewed a7ccac5 /
ffcc0461. R1 wired strict C18 extractor; R2 digest/provenance/freshness/matching;
R3 referral versus stale/cancel suppression. Six submitted evidence tests pass,
three architect regressions fail. Full deterministic EC01–EC12 consumer outcomes
are required; live producer pairing stays terminal-system-test-owned. See the
canonical task's explicit correction steps. No new claim or downstream promotion.


## BACKGROUND-002 Attempt 2 — Changes Requested — 2026-09-21

Current state: Ready, Attempt 2, claim cleared; not accepted. Reviewed implementation
55ac8b2 / report5802e25; 78 focused tests independently pass. Strict extraction and
digest/provenance corrections are present. Remaining A2-R1: unusable final evidence
must produce C18's admitted referral, not INVALID_FINAL; A2-R2: unconditional
post-refresh cancellation/admission checks (ordinary-Error cancellation reproduced
a deliverable referral); A2-R3: complete the canonical EC01–EC12 tests and correct
overstated report mappings/results. See the task's exact code/location instructions.
This is the latest decision; prior review entries are historical. No downstream
promotion or claim; live pairing remains terminal-system-test-owned.


## BACKGROUND-002 Attempt 3 review — 2026-09-21

Current decision: Ready, Attempt 3, claim cleared; Changes Requested for remaining
A2-R3 deterministic validation/report corrections. Reviewed7505ac3 / f409db23.
A2-R1 referral conversion and A2-R2 cancellation/admission code fixes are verified:
84 focused tests and the prior failing host cancellation reproduction now pass.
Canonical two-alternative, independent semantic/error and refresh-pending processor
cases remain required; exact files/cases/counts are in the task review. Live pairing
is terminal-owned and is NOT a prerequisite to component acceptance. Prior review
current-state wording is historical. No downstream promotion, claim or main merge.

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


## COMMERCE-015 Attempt 1 architect review — 2026-09-21

Changes Requested; status Ready, Attempt1 retained, claim clear; not accepted.
Reviewed implementationff386e2 and report42b8c300. Seven submitted tests pass;
five independent cases fail: denied variant read, late cancelled success, skipped
search results, C19 input mismatch, and missing null basket unknown markers.
R1–R5 require schema-shaped Admin requests/normalization, authorization and bounded
cancellation, lossless pagination, exact C19 descriptors, and null/source fixtures.
See canonical COMMERCE-015 task for deterministic locations and acceptance effects.
Prisma baseline and developer-owned live checks are separate from these blockers.
No dependency promotion, implementation edits, new claim, main merge or gitlink change.

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


## COMMERCE-016 readiness reconciliation — 2026-09-21

ARCH-020-COMMERCE-016 is Ready, attempt0, unclaimed. Accepted006/015/SHARED-001
are Complete in main;006's blank frontmatter ID is repaired to its canonical ID.
No task is launched and no other task lifecycle state changes in this update.

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


## Integration task split — 2026-09-21

C20 replaces combined013 with backend013, Studio018 and preview019. Both new
tasks are Pending, unclaimed; they may execute concurrently after013 and their
listed components complete. Exact mappings, file ownership and prior I01–I09
coverage are recorded. No active component implementation is changed or launched.

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

## C21 extension execution sequence — 2026-09-21

Read [C21](ARCH-020-external-api-tools.md) before extension work.

```text
DATABASE-003 (Complete)              SHARED-002 (Complete; 0.14.2 accepted)
        \                            /
         ->020 connection service   +->021 HTTP executor (ports)
                                    +->025 visual processor
                                    +->026 code sandbox
                                    +->022 Connections UI
                                    +->023 visual authoring UI
                                    +->027 code editor UI
020/021/022/023/025/026/027 +013/018/019 ->024 real integration
GATEWAY-001 +020/021/026 ->GATEWAY-003 runtime configuration
024 +GATEWAY-003 +BACKGROUND-002 ->SYSTEM-TEST-002 (manual)
new implementation prerequisites ->012 caching (external tools bypassed)
012 +SYSTEM-TEST-002 +existing dependencies ->SYSTEM-TEST-001 (manual)
```

The new tasks are unclaimed; no implementation/deployment started. Existing active
base scopes and claims stay intact. Database and Shared definitions can begin
independently; backend, processing and UI components use C21 ports independently.

## C21 tightened frontier — 2026-09-21

Section9 of [C21](ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence)
supersedes the earlier extension ownership diagram. No active013 scope/claim changed.

```text
DATABASE-003 +SHARED-002 ->020 connection lifecycle ->028 scoped credentials
COMMERCE-001 ->029 reusable sandbox proof (Complete; Accepted Attempt 4)
029 (Complete) +SHARED-002 ->026 typed code adapter
021 HTTP and025 visual processor remain independent component work
003 +021 +025 +026 +SHARED-002 ->030 publication validation/receipts
019 +009 +025 +026 +030 +SHARED-002 ->031 external preview backend
013 +028 +SHARED-002 ->032 merchant/runtime availability
020/021/022/023/025/026/027/028/030/031/032 +013/018/019 ->024 wiring only
GATEWAY-001 +020/021/026/028/029 ->GATEWAY-003
024 +GATEWAY-003 +BACKGROUND-002 ->SYSTEM-TEST-002 (manual)
all extension implementation ->012 cache bypass ->SYSTEM-TEST-001 (manual)
```

DATABASE-003 and SHARED-002 are Complete. COMMERCE-029 is Complete at accepted
Attempt 4 with the reusable bounded runtime. The direct Shared-gated component
frontier 020/021/022/023/025/026/027 is Ready; later tasks remain gated by their
other declared prerequisites. Each submission maps named acceptance cases to
committed scenarios and actual results.

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

### SHARED-002 Attempt 4 review — 2026-09-21

SHARED-002 is **Changes Requested / Ready, Attempt 4 retained**, executor/claim null. Reviewed `b23a7c1` / `52b14319`. Existing Attempt 1 fixes and `0.14.1` submitted consumer proof are retained. A4-R1 closes the remaining LIST publication wrapper/cardinality hole; A4-R2 restores the root package README/export inventory and publishes the corrected next patch version; A4-R3 makes the Completion Report current-state evidence coherent. No downstream task is promoted or launched until SHARED-002 is accepted Complete.
### DATABASE-003 Attempt 1 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 1 retained; executor/claim null.** Reviewed
implementation `a96dfd7` and report `cee29108`. The generated ERD whitespace
correction and expanded static validator coverage are preserved. PostgreSQL
fresh/upgrade migration and runtime checks remain unrun and are directly owned
by this migration task. No acceptance, implementation change, main merge, gitlink
update or downstream promotion. COMMERCE-020/028 remain gated on their actual
dependencies; no automatic launch.

### DATABASE-003 Attempt 2 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 2 retained; executor/claim null.** Submitted
implementation `df86899` closes the prior timestamp/assertion defects, but the real X02
upgrade rehearsal has now run and fails before the new migration: `seedBaseline()` is
rejected with SQLSTATE `23514`, `ARCH020 definition identity mismatch`. The repository
agent must make the upgrade seed a valid predecessor ARCH-020 state, including a valid
legacy tool definition and the minimum recovery/conversation + `conversation_core`
capability/revision + release membership needed for the preserved grant. Do not weaken
predecessor guards. Recreate the disposable targets and rerun fresh/upgrade; no
downstream task is promoted or launched.

### DATABASE-003 Attempt 3 accepted — 2026-09-21

**Accepted / Complete, Attempt 3 retained; executor/claim null.** Implementation
`bc59bf0`; report `aca2c656`; remote heads verified. The upgrade fixture now forms
a predecessor-valid ARCH-020 graph and both recreated fresh/upgrade PostgreSQL
rehearsals pass. X02 preservation, uniqueness, bounds, RESTRICT FKs,
immutability and rollback are established. DATABASE-003 alone does not unblock
COMMERCE-020/028/012 because their other declared prerequisites remain incomplete;
no automatic launch, main merge or gitlink update.
## COMMERCE-029 Attempt 4 accepted — 2026-09-21

The bounded QuickJS runtime is **Accepted / Complete, Attempt 4** (`f22e2d6`; report
`4069f60c`). Compile-only syntax validation no longer executes top-level guest code,
and the real 2,000 ms supervisor now has committed evidence terminating an active
built-in with `DEADLINE`, awaiting worker cleanup and recovering for the next run.
SB01-SB03 component proof is accepted.

Frontier: SHARED-002 remains Ready, so COMMERCE-026 stays Pending. Nothing else is
promoted or launched by this acceptance; GATEWAY-003 and the final cache/system
gates remain downstream.
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

### COMMERCE-018 Attempt 2 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 2 retained; executor/claim null.** Attempt 2
closes the Origin-boundary source check, strict capability-publish payload, discovery
path handoff and response-example validation, and preserves no-active-release and
descriptor de-duplication. Acceptance is still blocked because mutation release
rereads use the environment-agnostic `release(state,id)` helper (returning the wrong
pointer CAS/status), U13 still substitutes capability IDs for missing feature IDs,
the named suite remains mocked-adapter evidence rather than C20's required
real-application-service integration path, and the C20 producer-SHA/source/export
mapping table is still absent. Exact A2-R1..R4 corrections are recorded in the task's
Architect Review. Submitted 8 focused tests plus typecheck/lint/build/diff hygiene are
retained as passing evidence. No dependent task is promoted or launched.


### COMMERCE-018 Attempt 3 / COMMERCE-033 fixture correction — 2026-09-21

COMMERCE-018 is **Blocked, Attempt 3 retained, claims null** after source-level
acceptance of its environment-aware release rereads and authoritative U13 feature
identity handling. Real C20 integration evidence is blocked by a producer gap: the
accepted COMMERCE-013 backend does not contain the C20 persistent integration
seed/reset boundary.

The architect creates `ARCH-020-COMMERCE-033` as a bounded producer-correction task:
**Ready, Attempt 0, executor/claimed_at null**, depends only on accepted COMMERCE-013.
It has deterministic file ownership, exact exports, TEST target guards, a dedicated
disposable PostgreSQL reset contract, prefix-scoped Redis cleanup, exact fixture graph
and real-infrastructure validation. C20 now names 033 as the fixture owner while the
accepted013 production runtime remains unchanged.

COMMERCE-018 and unclaimed COMMERCE-019 both depend on 033 and are Blocked until it
is Complete. Their existing attempt numbers are preserved; neither is automatically
claimed or launched. COMMERCE-012, GATEWAY and system-test gates remain downstream.

### SHARED-002 Attempt 5 accepted — 2026-09-21

**Accepted / Complete, Attempt 5.** Implementation `95bab1d`; exact published Shared
package `0.14.2`. The direct C21 component frontier is now Ready for
`COMMERCE-020`, `021`, `022`, `023`, `025`, `026` and `027`. Do not rerun
`/moda-task ARCH-020-SHARED-002`; it has no further correction attempt. Use the
normal launcher on an eligible Ready dependant when the developer chooses to start
one. No automatic downstream launch occurs in this acceptance.

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
## COMMERCE-033 Attempt 1 architect review — 2026-09-22

**Changes Requested / Ready, Attempt 1 retained; claim clear.** The provider
transport is materially correct but its strict response parser currently rejects
standard OpenAI/Groq Chat Completions function calls because those calls contain
`id` and `type: "function"` alongside `function`. A1-R1 requires accepting and
validating that standard envelope while continuing to map only function name and
parsed arguments into the existing Shared `ModelStep`. No provider-call ID is
added to the Shared contract. Existing config, fixed endpoints, secret isolation,
one-request/no-retry behavior and token accounting are preserved. COMMERCE-019
remains blocked; no downstream task is promoted or launched.

## COMMERCE-033 Attempt 2 architect acceptance — 2026-09-22

ARCH-020-COMMERCE-033 is **Accepted / Complete, Attempt 2** (`94d31ea`; report
`6e0d5849`). The server-only OpenAI/Groq native-fetch preview transport now accepts
the standard Chat Completions function-tool response envelope (`id`,
`type: "function"`, `function`) while preserving only function name and parsed
arguments in the Shared `ModelStep`. Fixed endpoints, exact request mapping,
provider token accounting, cancellation, response bounds, no-retry/fallback and
secret-isolation behavior remain accepted.

The durable graph is reconciled so COMMERCE-019 explicitly depends on
COMMERCE-033. Because this provider task is Complete and 019's other declared
prerequisites are already Complete, COMMERCE-019 remains **Ready, Attempt 0** with
no active claim. No downstream task is started automatically.

## COMMERCE-021 Attempt 1 review — 2026-09-21

`ARCH-020-COMMERCE-021` is **Changes Requested / Ready, Attempt 1 retained** after
review of `b19f9d7` / report `5abdd61a`. Keep the working fixed-origin TLS/socket,
Shared 0.14.2 and response-processing integration. Attempt 2 is bounded to four
functional corrections: production DNS + maintained address classification,
absolute DNS/connect/body stage deadlines and abort cleanup, raw JSON depth/unsafe-key
rejection, and explicit EXTERNAL_HTTP dispatch exhaustiveness. C21 cancellation is
reconciled to nonretryable `DEADLINE` at the CommerceToolResult boundary because
Shared 0.14.2 has no CANCELLED tool-result member; runner cancellation remains
separate. No downstream task is promoted or launched.


## COMMERCE-021 Attempt 2 review — 2026-09-22

`ARCH-020-COMMERCE-021` is **Changes Requested / Ready, Attempt 2 retained**.
Attempt 3 is narrowly bounded to provider-body termination on post-header rejection
and preserving nonretryable external `DEADLINE` through DefinitionExecutor. Preserve
the completed DNS/classifier, pinned TLS transport, stage deadlines, JSON safety,
explicit dispatch and one-request budget work. No downstream task is promoted or
launched.

## COMMERCE-034 Attempt 1 acceptance reconciliation — 2026-09-22

COMMERCE-034 is **Accepted / Complete, Attempt 1**. The accepted U14 correction
keeps tool-only handoff in Tool test and requires an authored persisted release or
non-empty behaviour/draft source before Conversation preview can start; no synthetic
tool-to-capability fallback is permitted. COMMERCE-019 now records COMMERCE-034 as
an accepted prerequisite and remains **Ready**. No downstream task was launched by
this state reconciliation.
## COMMERCE-026 Attempt 2 architect acceptance — 2026-09-21

ARCH-020-COMMERCE-026 is **Accepted / Complete, Attempt 2** (`4b8e5bc`; report
`170074b3`). The C21 JavaScript response adapter is accepted over the existing
COMMERCE-029 QuickJS runtime and Shared `0.14.2` contracts. It preserves the bounded
server-only processor/compile ports and does not duplicate publication/sample schema
validation owned by COMMERCE-030.

No dependent is newly Ready from this acceptance alone: COMMERCE-030 still awaits
COMMERCE-025, and the later preview/assembly/gateway/system-test frontier retains its
other prerequisites. No downstream task is launched automatically.

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

## COMMERCE-021 Attempt 3 accepted — 2026-09-22

`ARCH-020-COMMERCE-021` is **Accepted / Complete, Attempt 3**. Provider-body cleanup
and nonretryable EXTERNAL_HTTP deadline propagation now close the final review
contract. Preserve the accepted DNS/socket pinning, stage-deadline, JSON-safety and
one-provider-request implementation. COMMERCE-030 still waits on COMMERCE-025; later
composition/gateway/final-checkpoint tasks retain their other dependencies. No
automatic launch.

## COMMERCE-027 Attempt 1 architect review — 2026-09-22

ARCH-020-COMMERCE-027 is **Changes Requested / Ready, Attempt 1**, claim clear.
Submitted implementation `771c1ff` establishes the isolated U17/raw-sample component
boundary but does not yet satisfy C21 X12/XN04. The task's latest Architect Review is
the complete deterministic correction contract covering Shared sample shape, content
hash/stale-result guards, saved-revision run identity, cancel/cooldown/replay behavior,
published/role/publish review rules, CodeMirror 6 local editor requirements, bounded
failure presentation and focused evidence.

No dependency is promoted. COMMERCE-024 and the final COMMERCE-012 checkpoint remain
gated. No downstream task is launched automatically.

## ARCH-020 COMMERCE-019 Attempt 4 acceptance — 2026-09-22

`ARCH-020-COMMERCE-019` is **Complete / Accepted, Attempt 4**. Production preview composition now consumes the accepted COMMERCE-033 preview configuration/provider transport and COMMERCE-034 U14 source-gating contracts: enabled MODEL mode injects the dedicated OpenAI/Groq preview adapter, disabled preview leaves FIXTURE provider-free, and tool-only U14 entry cannot fabricate Conversation capability state. Redis-frozen preview snapshots and replica/restart semantics from the earlier accepted corrections remain intact. No downstream task becomes Ready solely from this acceptance; GATEWAY-001 still waits on COMMERCE-018, COMMERCE-031 still waits on COMMERCE-025/030, and later integration/system gates retain their broader dependency sets.
## COMMERCE-025 Attempt 2 architect acceptance — 2026-09-22

ARCH-020-COMMERCE-025 is **Accepted / Complete, Attempt 2** (`8b281cf`; report
`04f10b0e`). The C21 visual response processor now preserves null/missing-last
ordering in both sort directions with stable ties and is protected by the required
server-only module boundary. Focused tests pass 6/6 and diff validation passes.
Repository-wide lint/typecheck/build remain non-zero only on reported unrelated
baseline diagnostics; the production Next compilation completed before the
unrelated TypeScript phase failed, and no task-owned diagnostic was reported.

Dependency reconciliation promotes **ARCH-020-COMMERCE-030 to Ready, Attempt 0**
because SHARED-002, COMMERCE-003, COMMERCE-021, COMMERCE-025 and COMMERCE-026 are
all Complete. Later preview, assembly, cache, gateway and system-test work retains
its remaining dependencies. No downstream task is started automatically.

## COMMERCE-023 Attempt 2 review — 2026-09-22

`ARCH-020-COMMERCE-023` is **Ready / Changes Requested, Attempt 2**. The explicit U06
external composition direction is retained. Attempt 3 must satisfy the latest task
review A2-R1..A2-R5 before COMMERCE-024 consumes the frontend: valid new external
draft, exact connection/revision return context, complete typed visual/query editor,
canonical stale sample-validation boundary, typed COMMERCE-027 slot and exact frozen
U14 fixture port. No dependant is promoted or auto-started.

## COMMERCE-023 Attempt 3 architect review — 2026-09-22

ARCH-020-COMMERCE-023 is **Changes Requested / Ready, Attempt 3**, claim clear.
Implementation `c71b30e` materially improves the U06 external editor but does not yet
satisfy C21 X06/XN02. The task's latest Architect Review is the complete deterministic
Attempt 4 correction contract: valid starter/return context, complete typed
query/filter/sort and code-slot authoring, editable sample plus current-validation
review/publish state, exact-revision U14 fixture port with no task-owned diagnostics,
and the owned new-tool XN02 path.

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
## COMMERCE-027 Attempt 2 architect review — 2026-09-22

ARCH-020-COMMERCE-027 is **Changes Requested / Ready, Attempt 2**, claim clear.
Attempt 2 correctly implements the Shared `TransformSample` boundary, canonical
browser hash/stale-result guards, returned-saved-revision run dispatch, retained
preview identity, RUNNING cancel/status controls and locally bundled CodeMirror 6.

Acceptance remains gated only by three task-owned corrections recorded
deterministically in the task: reachable SUPER_ADMIN draft publication workflow,
structured MIME/OUTPUT/SCHEMA failure presentation with `expected`, and correct
pre-dispatch save-failure plus serialized read/cancel reconciliation semantics.

COMMERCE-024 and COMMERCE-012 remain gated. No downstream task is launched
automatically.

## COMMERCE-027 Attempt 3 acceptance — 2026-09-22

`ARCH-020-COMMERCE-027` is **Complete / Accepted, Attempt 3**. Consume the exported
`CodeResponsePanel` / `RawResponseSamplePanel` as the accepted C21 frontend boundary;
do not reopen its editor, role, typed-failure or retained-run-identity mechanics during
COMMERCE-024 composition. COMMERCE-024 and the final COMMERCE-012 checkpoint remain
dependency-gated; no task is auto-started.
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

## COMMERCE-018 Attempt 6 autonomous validation unblock — 2026-09-22

`ARCH-020-COMMERCE-018` is **Ready / validation-only, Attempt 6 retained**. No new
Studio source correction is requested before the real C20 proof. Its canonical
fixture dependency is the accepted `ARCH-020-COMMERCE-035`; historical references to
a COMMERCE-033 fixture are superseded because COMMERCE-033 is the preview-model
provider task. Attempt 7 may provision its own task-labelled, loopback-only disposable
PostgreSQL/Redis Docker targets and must run reset + `test:arch020-studio-integration:c20`.
Unchanged unrelated repository baseline diagnostics do not block return to review
after that proof and the focused Studio suite pass. No dependant is auto-started.
## COMMERCE-028 Attempt 1 architect review — 2026-09-22

ARCH-020-COMMERCE-028 is **Changes Requested / Ready, Attempt 1**, claim clear.
Implementation `715da4d` is provisionally conformant at the credential-service source
boundary, but C21 CR02 is not yet proven. The latest task review requires a dedicated
real PostgreSQL credential rehearsal using two independent Prisma clients plus the
accepted COMMERCE-020 command kernel to prove NULL-platform uniqueness, one-effect/
one-audit replay, stale-CAS race, transaction rollback and no plaintext persistence.
The developer must execute that committed scenario before CR02 may be checked.

No dependency is promoted. COMMERCE-032, GATEWAY-003, COMMERCE-024, COMMERCE-012
and terminal system-test work retain their dependencies. No downstream task is
started automatically.

## COMMERCE-028 Attempt 2 architect acceptance — 2026-09-22

ARCH-020-COMMERCE-028 is **Accepted / Complete, Attempt 2** (`7384f81`; report
`f5214dc1`). CR01–CR03 are established, including the dedicated real PostgreSQL
CR02-PG-01..05 rehearsal with two Prisma clients, actual command-kernel replay/CAS,
NULL-platform uniqueness, rollback and no-plaintext persistence.

COMMERCE-032 is **Ready, Attempt 0**. Review separately identified a pre-existing
COMMERCE-020/database contradiction for BEARER revision `authHeader`. C21 now makes
the canonical boundary explicit: BEARER persists `authHeader:null`; runtime
credential resolution derives `Authorization`. The bounded producer correction is
materialized as **ARCH-020-COMMERCE-036 Ready, Attempt 0**, and COMMERCE-024 depends
on it before final production composition. No task is started automatically.
## COMMERCE-030 Attempt 1 architect review rebased — 2026-09-22

ARCH-020-COMMERCE-030 remains **Changes Requested / Ready, Attempt 1**, claim clear.
The current combined snapshot still contains implementation `59f0c34` unchanged; only
unrelated ARCH-020 coordination documentation has advanced since the original review
overlay. The deterministic correction contract in the task is unchanged: tester and
publisher liveness/role enforcement, exact 24-hour fail-closed receipt semantics,
sample-MIME plus production-renderer reuse, bounded schema issues, and complete
PV02/PV03 runtime-revalidation evidence.

No dependency is promoted and no downstream task is launched automatically.

## COMMERCE-030 Attempt 2 review — 2026-09-22

`ARCH-020-COMMERCE-030` is **Ready / Changes Requested, Attempt 2**. Preserve the
completed receipt/liveness/MIME/renderer/runtime-revalidation work. Attempt 3 is
bounded to canonical tool-definition hashing via Shared `toolHashInput` and
credential-independent connection/revision publication admission. COMMERCE-031,
COMMERCE-024 and COMMERCE-012 remain gated; no automatic launch.

## COMMERCE-023 Attempt 4 architect review — 2026-09-22

ARCH-020-COMMERCE-023 is **Changes Requested / Ready, Attempt 4**, claim clear. The
committed implementation advances the external fixture integration, but C21 X06/XN02
is not yet complete. The task's latest Architect Review is the complete deterministic
Attempt 5 correction contract: code-panel/mode-switch wiring; query/literal and
8-filter typed authoring; editable sample and response-shape guidance; exact fallback
return context plus role-aware publication reason/review; and one full new-tool XN02
proof.

COMMERCE-024 and COMMERCE-012 remain gated. No downstream task is started
automatically.

## COMMERCE-023 Attempt 5 architect review — 2026-09-22

ARCH-020-COMMERCE-023 is **Changes Requested / Ready, Attempt 5**, claim clear.
Implementation `c184c58` is close to the C21 X06/XN02 boundary. The latest task review
narrows Attempt 6 to three remaining items: bind U14 and Publish to the persisted saved
revision rather than unsaved local state; make Literal/IN typed authoring exact and
retain invalid IN text; and complete the exact XN02 proof/current Completion Report.

COMMERCE-024 and COMMERCE-012 remain gated. No downstream task is started
automatically.
## COMMERCE-030 Attempt 3 architect acceptance — 2026-09-22

**Accepted / Complete, Attempt 3** (`d15d3f5`).

The C21 external publication/sample validator now shares the lifecycle's canonical
`toolHashInput(definition)` identity and admits synthetic samples/publication from
persisted non-secret connection revision state (`enabled`, `revisionPresent`,
`scope`, `authMode`, `authHeader`) without requiring live merchant credentials.
Active-staff receipt semantics, strict 24-hour TTL, sample MIME/schema validation,
production renderer reuse and later real-provider runtime validation remain intact.

`ARCH-020-COMMERCE-031` is now **Ready** because COMMERCE-019, COMMERCE-009,
SHARED-002, COMMERCE-025, COMMERCE-026 and COMMERCE-030 are Complete. It is not
automatically launched. COMMERCE-024 and COMMERCE-012 remain Pending behind their
other authoritative prerequisites.
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
## COMMERCE-032 Attempt 1 architect review — 2026-09-22

ARCH-020-COMMERCE-032 is **Blocked, Attempt 1**, claim clear. The submitted resolver
preserves original grant tool/revision/provenance and current exclusion identities,
but cannot be accepted against the current COMMERCE-028 availability port: 032 passes
trusted merchant `shopId` for all candidates, while 028 currently requires null for
PLATFORM credential availability and therefore falsely returns `CREDENTIAL_MISSING`.

C21 now makes the intended boundary explicit and
**ARCH-020-COMMERCE-037 is Ready, Attempt 0** to normalize only the producer's
read-only availability shop semantics. COMMERCE-032 depends on 037; after 037 is
accepted it returns Ready for a validation/reconciliation Attempt 2. COMMERCE-024 and
COMMERCE-012 remain gated. No task is started automatically.
## COMMERCE-037 Attempt 1 architect acceptance — 2026-09-22

**Accepted / Complete, Attempt 1** (`021dcf7`; parent report `15d9588b`).

The read-only credential availability boundary is normalized so `shopId` means
trusted merchant identity. Immutable revision scope now selects the credential row:
PLATFORM uses the null-scope row; PER_SHOP uses only that merchant's row. Credential
status/mutation/resolution retain their existing nullable credential-scope semantics.
No decryption, mutation or fallback is added to availability.

COMMERCE-032 remains Ready and explicitly records COMMERCE-037 as a prerequisite.
No downstream task is launched automatically.

## COMMERCE-018 Attempt 8 acceptance — 2026-09-22

`ARCH-020-COMMERCE-018` is **Complete / Accepted, Attempt 8**. Consumers may rely on
the production Studio adapter for the accepted C20 read/write mapping, Origin/role
enforcement, replay/CAS behavior, exact release-member/pointer semantics, response
validation and read-only U13 inspection. The full real authoring traversal now passes
through production services (5/5 C20; 9/9 focused Studio). Optional source revision
fields are omitted rather than hashed as `undefined`.

This acceptance promotes GATEWAY-001 to Ready. COMMERCE-024, COMMERCE-012 and
system-test work remain gated by their other prerequisites; no task is auto-started.
## COMMERCE-022 Attempt 4 acceptance — 2026-09-22

`ARCH-020-COMMERCE-022` is **Complete / Accepted, Attempt 4**. Consumers may treat the
U15/U16 frontend as the accepted Connections producer: Shared result envelopes,
same-operation replay, write-only credential controls, parent-owned navigation guard,
exact revision/shop credential status/CAS context, terminal detail states and preserved
list return state. COMMERCE-024 and COMMERCE-012 remain gated by their other
dependencies; no task is auto-started.
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

## COMMERCE-036 Attempt 1 architect acceptance — 2026-09-22

ARCH-020-COMMERCE-036 is **Accepted / Complete, Attempt 1** (`ccc8c41`; parent
handoff `e0f0265e`). The lifecycle now accepts null/blank or legacy `Authorization`
for BEARER input but canonicalizes persisted/public revision metadata to
`authHeader:null`, preserving the DATABASE-003 CHECK and COMMERCE-028 runtime
derivation of the `Authorization` header.

Focused lifecycle tests pass 11/11 and the disposable-PostgreSQL regression proves
both accepted BEARER input forms persist NULL. COMMERCE-024 retains COMMERCE-036 as a
dependency but remains Pending because other prerequisites are incomplete. No
downstream task is started automatically.

## COMMERCE-023 Attempt 7 review — 2026-09-22

`ARCH-020-COMMERCE-023` is **Ready / Changes Requested, Attempt 7**. Preserve the
current U06/U14 authoring, saved-definition refresh and typed editor work. Attempt 8
must close only A7-R1..A7-R3 from the latest task review before COMMERCE-024 consumes
this frontend. COMMERCE-024 and COMMERCE-012 remain gated; nothing is auto-started.

## COMMERCE-023 Attempt 8 acceptance — 2026-09-22

`ARCH-020-COMMERCE-023` is **Complete / Accepted, Attempt 8**. Consumers may rely on
the accepted U06/U14 external authoring frontend: exact saved-vs-unsaved revision
separation, current-validation publication gating, typed query/projection/filter
editing, scalar-only IN validation/reconciliation, guarded return context, injected
code-panel slot and exact saved-revision fixture execution. COMMERCE-024 readiness
must be reconciled only once all of its producer acceptances coexist in one parent
snapshot.

## GATEWAY-001 Attempt 3 architect review — 2026-09-22

ARCH-020-GATEWAY-001 is **Changes Requested / Ready, Attempt 3**, claim clear.
The Render/HAProxy implementation from `7bd5865` is preserved. Attempt 4 is
documentation/evidence-only: hosted smoke commands must use valid C5/C9.1/C15 bodies,
the required C15 schema apiVersion and concrete matching preview UUIDs rather than
`{}`/placeholder IDs. The later C21 U15/U16 route extension remains assigned to
GATEWAY-003.

No downstream task is promoted or started automatically.
