# ARCH-020 task-definition review — 2026-09-20

Scope: all 20 original tasks, parent architecture, handoff, domain indexes and
related Shared/Background/merchant/database source. Definitions only on local
main under the user's exception; no task claim, application implementation,
commit/push, deployment or live provider call performed.

## Earlier review record (superseded where amended below)

The following records the earlier 20-task/seven-table draft. The current scope
and validation are in the final reconciliation section below.

## Findings resolved

| Gap | Resolution / owner |
|---|---|
| Generic task instructions allowed incompatible wire implementations | C4 exact tool/manifest/final/evidence contracts; task-specific guidance in all 20 existing tasks |
| Inbound metadata potentially duplicated/redefined | Inspected Shared whatsapp.ts/tests and billing.ts status schema; C0 preserves inbound v1/status v2 unchanged |
| Candidate routing and unowned clarification delivery were still open | C2 exact distinct-recovery query; C3 lightweight Redis guard, existing abuse limits and no merchant attribution; no new DB prerequisite |
| No persisted sender/recipient evidence; timestamp-only current fragments | Deferred: single-number routing reuses existing message/customer links and batching; prior-history repair needs no migration |
| Initial/follow-up outreach could be mistaken for separate conversations | C13 reuses ARCH-016 attempts1/2, one Conversation, distinct provider IDs, credit boundaries and engagement suppression |
| Compatibility evidence was required without a prerequisite | BACKGROUND-001 now depends on COMMERCE-001's real SDK/profile fixture |
| Compound publishing conflicted with one audit id per operation | C7 explicit operations and resumable create/publish/activate flow; exact replay/CAS rules |
| Unspecified registry binding allowed discount tools outside policy | C1 fixed reserved-tool ownership and conditional permission on similarity evidence |
| UI/preview tests copied into unrelated backend/foundation tasks | Scoped tests to each deliverable; retained double-activation requirements on actual UI actions |
| Preview conversation identity conflated with a run; budgets unspecified | C9 separate IDs, fixed fixture grant, cross-replica claim/budgets/cancel/uncertainty |
| Database grant JSON bounds ambiguous | DATABASE-001 explicitly separates selected keys8192 bytes and tools32768 bytes |
| Free-form infrastructure/telemetry expectations | C10 exact routes/env/health/build contract; C11 actual-signal inventory and alert thresholds |
| Claim that schemas prove tenancy/LLM grounding | Separate pure shape tests, service ownership enforcement and adversarial model evaluation; no universal hallucination guarantee |

## Review status

Definitions cover 20 tasks: 2 Ready, 17 Pending, 1 Blocked. The user chose
lightweight single-number scope; unclaimed DATABASE-002 was removed. DATABASE-001's
seven Commerce tables remain unchanged. Existing accepted ARCH-016 behaviour remains a prerequisite, not rewritten
under another architecture. All execution fields remain unclaimed.

External execution inputs remain: actual new repository/submodule provisioning,
Studio hostname and credentials; exact tested SDK dependencies selected/recorded
by foundation; official Shopify schema/scope evidence and closed unsupported
fallbacks in discount implementation. These are assigned deliverables/setup
inputs, not permission for an executor to guess deployed values or widen scope.

## Validation evidence

- Packet validator: 20 tasks, full section/frontmatter schema, dependency reciprocity
  and acyclic graph, accepted external prerequisite metadata, 20 route resolutions,
  terminal system-test dependency set, Markdown links, TOML parsing and launcher
  syntax passed.
- Scoped documentation whitespace/link checks passed. Runtime verification of
  proposed changes remains in the assigned implementation tasks.
- Shared inbound contract: `node --import tsx --test src/whatsapp.test.ts` passed
  all 6 tests after the workspace-owned Node bootstrap (ENV-NODE-001). Contextual/
  contextless text, audio, unsupported types, bounds/version checks, forbidden
  business fields and union narrowing all passed. No Shared source/publication changed.

Shared-channel clarification: Moda owns the initial WhatsApp number for all merchants. C2 and Background/system-test tasks explicitly cover separate shop Customer records sharing one phone and count recovery candidates across merchants before selecting a shop. Additional-number design is outside current scope.

Lightweight amendment: no durable clarification table or per-message version field. C3 specifies Redis SET NX EX 86400 before sending, retaining the marker on uncertainty; Redis loss/expiry and crash-before-send are explicitly accepted limitations.

Database-tool amendment: C14 stores complete tool definitions in each published
capability revision, replacing tool-reference-only metadata. The seven-table
layout remains. Existing capability feature bindings select tools; each tool has
its schema, approved operation mapping and response template. Studio creation,
publication and preview plus Shared/Commerce/Background/system-test requirements
now enforce definition-version pinning and structured-plus-rendered results.
New definitions over installed operations require publication, not deployment.

Tool-definition amendment validation: all20 task schemas/routes/dependencies and
Markdown file links passed; the embedded product-search example parses as JSON,
contains the exact six definition keys and validates decimal-string prices such
as30.00. Whitespace checks include untracked documents. No application runtime or
new database implementation was executed by this documentation amendment.

## Studio authoring reconciliation — current review packet

The packet now has 19 unclaimed tasks: 3 Ready, 16 Pending, 0 Blocked. Added
COMMERCE-011 for core Shopify discovery/schema/compiler services. Admin continues
to own Feature creation. Nine database tables support independent reusable tools,
exact capability bindings and original grant provenance. C14 permits new public
Shopify queries without named-handler deployments; policy helpers retain discount
and recovery authority. Development examples are not a production feature list.

COMMERCE-008 embeds every U01–U13 page, dialog, entry/destination, Back/Cancel,
role, field and publication transition; COMMERCE-009 embeds U14. N01–N12 define
navigation and side-effect acceptance. Discovery services precede publication
and execution; the complete editor depends on those implemented services; gateway
depends on final route/discovery contracts. Reciprocal metadata, all indexes and
the terminal dependency set are reconciled. No task is claimed or implemented.

### Reconciliation validation evidence

- Packet validation passed for all19 tasks: exact task sections/frontmatter,
  unclaimed metadata, reciprocal acyclic dependencies, external prerequisite
  records, complete terminal dependency set, launcher routes and Markdown links.
- UI consistency validation passed:14 unique page routes,12 navigation cases,
  exact embedding of U01–U13 in COMMERCE-008 and U14 in COMMERCE-009.
- Nine database model specifications counted; C14 example parsed as JSON with
  exact definition keys. Its schema hash remains explicitly an implementation
  artifact input; no live GraphQL validation is claimed here.
- Scoped whitespace checks passed; Commerce TOML parses and generated agent mirror
  synchronization check passed. No application tests, migrations, provider calls,
  commits, pushes or task executions were performed by this reconciliation.

## Repository readiness correction — 2026-09-20

The earlier provisioning blocker is resolved: the private Commerce repository and
workspace submodule now exist at the verified initial main commit recorded in the
implementation handoff. COMMERCE-001 is Ready, unclaimed at attempt 0. Historical
review counts above describe earlier drafts; current counts are 3 Ready and
16 Pending across 19 tasks. Next.js and nested database setup remain task work.

Shared consolidation: one SHARED-001 now includes all contracts, runner and publication requirements. The current 19-task graph passes schema, reciprocal dependency, cycle, terminal-gate, route and link validation.


## Remaining-task determinism review — 2026-09-20

Reviewed the remaining ARCH-020 definitions with separate read-only runtime and
Studio reviews. This is a definition amendment, not implementation acceptance or
a task claim. Completed tasks and the active COMMERCE-011 implementation are not
reopened. Concurrent BACKGROUND-001 acceptance/integration edits are excluded.

| Finding | Binding correction / owner |
|---|---|
| Arbitrary tool names made a hard-coded final evaluator impossible | C4 exact-call evidence provenance/replay; COMMERCE-004/006/007 and BACKGROUND-002, without a new Shared/DB contract |
| Preview dependency cycle hidden inside acceptance | COMMERCE-008 owns composer plus stubbed handoff;009 owns real U14; SYSTEM-TEST owns production pinning |
| Unsaved composer lost on route navigation | UI design and008 specify tab-local authenticated layout state and exact loss/return behaviour |
| Preview APIs and concurrent different-run semantics missing | C9.1 exact routes, bodies, owner checks, replay, busy, cancellation and history rules;009/Gateway consume them |
| Superseded language/preference tests and fixed-prompt ownership | C6.1 aligned to C6.2 and C16;009 and SYSTEM-TEST use final expectations |
| Ranking, multiple capability limits and provider retries ambiguous | C8 deterministic normalization/order/effective minima/shared request counter |
| Grant persistence and credential boundaries ambiguous |004 read/verifies Background-owned grant;005 public query never loads privileged credentials |
| Publication acceptance implied later executors |003 fixture registry acceptance, production executor availability remains mandatory |
| Deployment/alert handoffs not exact | AUTH_URL, readiness semantics, messaging transcription names, metric denominators and threshold boundaries |
| Stale provisioning blockers | Removed from pending Commerce tasks; foundation already supplies repository provisioning |

COMMERCE-011 is already being implemented: its historical unresolved-issues boilerplate
still mentions provisioning, but the accepted COMMERCE-001 setup supersedes that
line. No additional provisioning gate or new implementation requirement is imposed
on its active attempt by this review.

COMMERCE-012 intentionally remains an initial backlog definition. Its existing
Before promotion to Ready checklist must first resolve policy persistence, API,
U06/U14 controls, limits and any owner-specific prerequisites. It is not executable
merely because other tasks finish. Do not invent a migration or reopen accepted
Shared/Database tasks to bypass that checkpoint.

Validation for this amendment is documentation-only: dependency reciprocity and
cycle checks, owned UI embedding, local Markdown links, unchanged lifecycle fields
and scoped whitespace. Application and live-provider evidence belongs to the
implementation tasks; none is claimed by this review.


## Parallel start amendment — 2026-09-21

At the user's request, publication003 and Studio008 can start and complete their
components against C17 typed ports/fixtures. Both are Ready, attempt0, unclaimed.
A separate013 owns real service adapters and I01–I08 integrated acceptance.013
waits for003/004/005/006/007/008/011;009/GATEWAY-001/012/SYSTEM-TEST-001 wait for013.
Start/enable metadata and indexes are reciprocal. No launcher changes, task claims
or application implementation.011 active implementation remains untouched.


## Independent evidence-contract amendment — 2026-09-21

C18 plus the canonical JSON seed specifies requests, Shared output schemas, exact
extraction/provenance/replay/comparison, failure/admission decisions and EC01–EC12.
BACKGROUND-002 is Ready against accepted001;007 remains independently sequenced
on006. Removed reciprocal dependency; terminal system test owns real pairing.
No Shared publication, migration, implementation or task claim is introduced.

Validation: reciprocal acyclic21-task graph, unchanged claims/attempts, local links
and whitespace passed. BACKGROUND-002 prerequisite001 is Complete. Original and
refreshed JSON seed replies passed the current Shared source Zod schemas under
workspace Node24.19.0; both SHA-256 digests and frozen-clock freshness bounds passed.
This validates contract examples, not the future producer/consumer implementation.


## Smaller-scope task amendment — 2026-09-21

Rewrote unattempted004/005/006/009 as single-scope tasks and added014–017.
C19 names owner directories, typed boundary inputs/results, rule normalization,
provider budgets, fixture cases and integration owners. Original task bodies were
replaced instead of accumulating scope overrides. U14 exact page specification
is embedded in017;009 now owns lifecycle only.012 and SYSTEM-TEST explicitly wait
for all four new tasks. Active attempts retain implementation scope/claim fields;
only reciprocal enables metadata is reconciled where required.

Validation:25-task reciprocal dependency graph is acyclic; all prerequisites for
newly Ready006/009/015 are Complete. All eight narrowed/new task bodies retain
required sections, claims/attempts are unchanged and U14's embedded page text
matches the binding UI design.012 and terminal system testing include014–017.
Local Markdown links and scoped whitespace checks passed. These are definition
checks only, not application/provider test results. Frontend017 owns no backend
implementation;013 owns saved-bundle loading and actual preview/frontend pairing.


## Integration-task decomposition — 2026-09-21

Replaced unclaimed013's combined scope with backend integration and created018
Studio /019 preview integration. C20 supplies inspected source exports, exact
payload/error translations, facade contract, isolated seed, file boundaries and
I01–I09 ownership. Explicitly assigned the discovered enable/disable timestamp-CAS
compatibility gap to013; consumers may not discard it.018 and019 have no mutual
edge and can run concurrently. No application code or task claim was changed.

Validation: all 27 ARCH-020 tasks form a reciprocal, acyclic dependency graph.
018/019 have no mutual dependency, both require 013, and caching/deployment/system
testing require both. Claims and attempts are unchanged. Both new tasks resolve
through the launcher in read-only route mode as Pending, attempt 0 and unclaimed.
Local links and scoped whitespace checks passed. Former I01–I09 checks are mapped
to B/S/P owners in C20. These are task-definition checks, not application tests.

## External API and generic response processing — 2026-09-21

Created12 narrowly owned extension tasks under C21, preserving existing base task
implementation scopes/claims. C21 specifies connection tables, immutable endpoint
revisions, encrypted credential scope, strict external execution/processing schema,
HTTP controls, visual operations, isolated JavaScript, raw UTF-8 formats, U15/U16 and
U06/U14 traversal, sample/output-schema validation and real-call failure behavior.
Database003 and Shared002 can start independently; UI and backend stay separate;024
owns actual assembly.012 explicitly bypasses external caching and waits for extension
implementation; overall system test waits for the separate manual external gate.

Validation: all39 ARCH-020 tasks form a reciprocal acyclic graph; metadata/body
dependency lists match. All12 new task IDs resolve through launcher read-only routing;
DATABASE-003/SHARED-002 are Ready with Complete prerequisites, others Pending.
Existing status/attempt/claim fields are unchanged. Required task sections, local
links and scoped whitespace pass. No task claimed and no application/security test
execution or deployed sandbox claimed by this documentation amendment.
