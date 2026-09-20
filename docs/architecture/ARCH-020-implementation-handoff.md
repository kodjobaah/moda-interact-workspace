# ARCH-020 implementation handoff

Canonical architecture: [CommerceAgent Studio and merchant-configured MCP capabilities](ARCH-020-commerce-agent-studio-mcp-capabilities.md).

## Initial review packet and definition frontier

The developer requested task definitions on local workspace `main` for review.
This is an explicit exception to task-definition materialisation only. No task
is claimed, no application implementation has started, and no remote repository,
submodule, deployment or task worktree is claimed to exist because of this packet.

The packet defines 19 tasks: **3 Ready, 16 Pending, 0 Blocked**. Ready means
dependency-eligible; this review request does not launch execution.

- Ready: `ARCH-020-DATABASE-001`, `ARCH-020-SHARED-001` (accepted ARCH-016 task
  metadata is present in this checkout; verify actual source availability at launch).
- Ready: `ARCH-020-COMMERCE-001`, following the verified repository provisioning below.
- Pending: the remaining 16 tasks, including the terminal system test.

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
COMMERCE-002/011 + DATABASE-001 + SHARED-001 -> COMMERCE-003 (publication)
COMMERCE-003 -> COMMERCE-004 -> COMMERCE-005 -> COMMERCE-006 -> COMMERCE-007
COMMERCE-003/005/006/007/011 -> COMMERCE-008 (U01–U13 full authoring UI)
COMMERCE-008/007 + SHARED-001 -> COMMERCE-009 (U14 tests/conversations)
COMMERCE-004/007/009 -> COMMERCE-010 (observability)
SHARED-001 + DATABASE-001 + COMMERCE-001 + ARCH-016-BACKGROUND-003 -> BACKGROUND-001
BACKGROUND-001 + COMMERCE-007 -> BACKGROUND-002
SHARED-001 + ARCH-016-SHOPIFY-002 -> SHOPIFY-001
COMMERCE-002/008/011 + BACKGROUND-001 -> GATEWAY-001
GATEWAY-001 + COMMERCE-010 + BACKGROUND-002 -> GATEWAY-002
all 20 nonterminal tasks -> SYSTEM-TEST-001 (manual terminal gate)
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
Commerce repository/default-branch provisioning is complete and COMMERCE-001 is Ready.
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
package version. Current frontier: 19 tasks, 3 Ready, 16 Pending, 0 Blocked.
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
