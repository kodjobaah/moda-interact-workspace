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
