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
DATABASE-001 ---------------------------> publication persistence / Background grants
SHARED-001 (contracts + runner + publication) ---> shared contracts/runner publication
provisioning -> COMMERCE-001 -> COMMERCE-002
COMMERCE-002 + SHARED-001 -> COMMERCE-011 (Shopify discovery/schema services)
COMMERCE-002 + DATABASE-001 + SHARED-001 -> COMMERCE-003 (interface-based publication)
COMMERCE-003 -> COMMERCE-004 -> COMMERCE-005 -> COMMERCE-006 -> COMMERCE-007
COMMERCE-002 + DATABASE-001 + SHARED-001 -> COMMERCE-008 start
COMMERCE-003/004/005/006/007/008/011 -> COMMERCE-013 (real integration)
COMMERCE-008/007 + SHARED-001 -> COMMERCE-009 (U14 tests/conversations)
COMMERCE-004/007/009 -> COMMERCE-010 (observability)
SHARED-001 + DATABASE-001 + COMMERCE-001 + ARCH-016-BACKGROUND-003 -> BACKGROUND-001
BACKGROUND-001 + C18 agreed contract -> BACKGROUND-002 (independent consumer)
SHARED-001 + ARCH-016-SHOPIFY-002 -> SHOPIFY-001
COMMERCE-002/008/011 + BACKGROUND-001 -> GATEWAY-001
GATEWAY-001 + COMMERCE-010 + BACKGROUND-002 -> GATEWAY-002
all implementation tasks -> SYSTEM-TEST-001 (manual terminal gate)
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

2026-09-21 C18 frontier: BACKGROUND-002 promoted Ready, unclaimed, after accepted
BACKGROUND-001. COMMERCE-007 retains its own evaluator prerequisite but no longer
blocks the consumer. SYSTEM-TEST-001 owns EC01–EC12 real-service pairing.

## COMMERCE-008 Attempt 2 — Changes Requested — 2026-09-21

COMMERCE-008 is **Ready, Attempt 2 retained**, claim cleared, not accepted.
Reviewed `6c4ecbc` / report `10fc0ae6` (PR3/171). Typed unavailable/not-found states
and shell improvements are retained. Remaining blockers are canonical port/data
mismatches, incomplete connected authoring/release workflows, unsafe unknown-outcome
retry, and exact-revision/navigation behavior. Latest task review records R1–R4.
C17 still allows fixture component acceptance; real adapters and readiness timing
failures are not the blocker. No new claim, downstream promotion, implementation
edit or main integration. Other task states remain unchanged.
