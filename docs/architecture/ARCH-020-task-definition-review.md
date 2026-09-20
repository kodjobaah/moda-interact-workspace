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

The packet now has 21 unclaimed tasks: 3 Ready, 18 Pending, 0 Blocked. Added
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

- Packet validation passed for all21 tasks: exact task sections/frontmatter,
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
18 Pending across 21 tasks. Next.js and nested database setup remain task work.
