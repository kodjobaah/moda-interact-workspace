---
id: ARCH-020-COMMERCE-008
architecture_id: ARCH-020
title: Build capability authoring and release screens
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 120
executor: null
claimed_at: null
attempt: 5
depends_on:
  - ARCH-020-COMMERCE-002
  - ARCH-020-DATABASE-001
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-017
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-013
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
created: 2026-09-20
updated: 2026-09-21
---

# Build capability authoring and release screens

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Build the complete internal Studio authoring workspace, including every page and traversal U01–U13, with existing Admin feature ownership, reusable tools and integrated Shopify discovery.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

U01–U13 pages/dialogs/navigation, roles, query/schema editor, exact tool association, release review and read-only merchant inspection. U14 conversation/test execution belongs to COMMERCE-009; links into it are part of this task.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

### Duplicate-action protection

Every state-changing or costly UI action in this task must prevent duplicate
activation, including mouse double-click, double-tap, Enter/Space repetition and
form-submit plus button-click combinations. Acquire a synchronous submission
guard before awaiting work (a render-delayed disabled state alone is insufficient),
and route all activation paths through the same submit handler. Disable the
trigger and conflicting controls immediately, show a meaningful pending label,
and expose accessible busy/status feedback. Do not lock unrelated navigation.

Keep the guard until the operation has definitively completed, failed or been
cancelled. A client timeout is an unknown outcome: reconcile the original
operation before allowing a retry, rather than silently creating a second one.
On a known failure, restore controls and preserve input for an intentional retry.
Ignore stale completions so an earlier request cannot reset a newer request's
pending state. Debounce alone is not sufficient for mutations or paid previews.
Server authorisation and duplicate protection are required independently of the
browser controls; inspect direct duplicate requests as well as UI behaviour.

## Work Items

### Parallel implementation and integration ownership

Architect promotion on 2026-09-21: Ready, unclaimed. Implement Studio against
C17 agreed ports and deterministic fixtures. This task may be accepted independently
when its owned component, typed interfaces and fixture acceptance tests pass.
ARCH-020-COMMERCE-013 owns real provider adapters, composition and integrated
acceptance; do not wait for or implement that task here.

For this task, all requirements below to consume pending services or exercise a
complete service flow mean contract-fixture execution. This explicitly supersedes
earlier accepted-service/full-integration wording for those pending dependencies.
Retain every field, page, role, failure and side-effect expectation. Do not weaken
them to snapshots or static mockups. Production composition must fail unavailable
until013 installs real adapters; fixtures are test-harness-only, never a runtime
fallback. Already accepted auth/Shared/database dependencies remain real inputs.
Record the port signatures and mapping in the C17 contract document. Integration
checks are assigned explicitly to013, not reported as passed by this task.

- [x] Implement C7.1 U01 Google-only sign-in, development redirect to U03, and persistent Development — SUPER_ADMIN badge across U03–U14 shell. Reuse COMMERCE-002 guards/session state; no client bypass toggle. Verify A11 and preserve same-tick submission guards.

- [x] Implement exact C16 U10/U11 response authoring panels and N13 traversal embedded below, including instructions/schema/example editors, local draft retention, roles, validation and separate creation/activation. Cover R05/R09/R10.

- [x] Implement each page and dialog below with the exact route, entry points, fields, actions, destination, Back/Cancel behaviour and empty/loading/error states. No placeholder links or inferred pages.
- [x] Use C17 typed fixture ports for the pending COMMERCE-003/011/005/006/007 adapters. U07 provides documentation and schema-driven authoring with full-definition validation; real adapters remain COMMERCE-013-owned.
- [x] Implement all mutations with shared immediate submission guards, explicit desired values, stale-response protection, server replay/CAS and input-preserving errors. UI cannot create Admin features or edit merchant entitlements.

### Global layout and navigation

Authenticated shell: left navigation in this order **Features**, **Tools**,
**Explore Shopify**, **Test conversations**, **Releases**, **Merchants**. These
link to U03/U05/U07/U14/U10/U12. Show Studio title, current administrator role,
active release number (or No active release), and Sign out. Sign out returns to
U01 through NextAuth. Mobile uses a labelled menu with the same items/order;
selection closes it and moves focus to the page heading. Active item is announced.
No sidebar link for the internal Capabilities index: U08 is reachable from the
Features page's **Platform configurations** link. No feature-creation button.

GET / redirects to /features. Unauthenticated access to any business page goes
to /sign-in with an allowlisted same-origin return path. Successful sign-in returns
to that page, or /features. No external return URL, arbitrary URL or recursive
sign-in destination. Direct links enforce authorization and ownership, not only
sidebar access. Missing entities are404; revoked/inactive administrators go to
/access-denied without revealing business data. Auth expiry preserves unsaved
input only in current-page memory; never browser localStorage/sessionStorage.
Explain when reauthentication requires re-entering unsaved input.

Back links use the specified parent/list, preserving validated filter/cursor
query state. Browser Back follows history. Unsaved form navigation prompts
**Stay** or **Discard unsaved changes**; discard affects local edits only, never
deletes saved drafts. Cancel closes the current dialog and returns focus to its
trigger. Published records are read-only; changes start a new draft. Every page
has skeleton loading, empty, retryable error, forbidden and not-found states as
applicable. List filters reset cursor; pagination is25/default,100/max. Screen
readers get a heading and status/error announcement. No raw secret or customer
transcript is shown.

### Page register

| ID | Route | Entry points | Main content | Back/exit |
|---|---|---|---|---|
| U01 | /sign-in | Unauthenticated route, Sign out | Google sign-in; pending/error feedback | Successful auth to validated return path or U03 |
| U02 | /access-denied | Valid login without current staff permission | Access denied and Sign out | Sign out to U01; no business navigation |
| U03 | /features | Root redirect, sidebar | Admin feature catalogue, availability and Commerce configuration status | Sidebar; Platform configurations to U08 |
| U04 | /features/[id] | U03 feature row/Configure behaviour | Read-only feature metadata and all linked configurations | Back to Features U03 |
| U05 | /tools | Sidebar, tool editor Back | Searchable reusable tool library | Sidebar |
| U06 | /tools/[id] | U05 tool row, New tool, feature association link | Tool metadata, revision editor/history, usage by features | Back to Tools U05, or validated return context U09 |
| U07 | /explore | Sidebar or Browse Shopify from U06 | Documentation search, schema browser, examples and query builder | Sidebar or Return to tool U06 |
| U08 | /capabilities | U03 Platform configurations | BASE/RECOVERY_POLICY configurations | Back to Features U03 |
| U09 | /capabilities/[id] | U04 configuration row/create, U08 row | Behaviour prompt, settings, exact tool revision associations, history | Feature U04 for FEATURE; U08 otherwise |
| U10 | /releases | Sidebar, release-stage completion | Active release and immutable release history; Create release | Sidebar |
| U11 | /releases/[id] | U10 row, completed Create release | Members, exact revisions, response contract, diff, activation/rollback | Back to Releases U10 |
| U12 | /shops | Merchants sidebar | Read-only merchant search/list | Sidebar |
| U13 | /shops/[id] | U12 row | Eligibility breakdown and tool list for a new conversation | Back to Merchants U12 |
| U14 | /preview | Sidebar, Test from U06/U09/U11/U13 | Synthetic tool test and isolated conversation sandbox | Validated source page, or Features U03 |

No unlisted product pages or workflow routes are required. Creation, association,
publication and confirmations below are dialogs on these pages. /api/auth/*,
/api/studio/*, static assets and private health/MCP routes are transport routes,
not Studio pages. Query selection of revisionId must belong to its route entity;
mismatches are404, never silently switch to another entity or latest revision.

### U03–U04: existing features and Configure behaviour

U03 rows: display name, key, activation mode, Admin active/inactive, Commerce
status and Configure behaviour. Read all Admin Feature rows; filter by name/key,
active state and configuration status. Sort displayName,id. A new arbitrary
Admin key appears after refetch without a deployment. Show **Not configured**
when no CommerceCapability references it; **Draft only** when configurations
exist but none is in the active release; **Live** when at least one is in the
active release. Add **Unpublished changes** when a draft differs from its live
revision, and **Disabled configuration** separately. No active release is not Live.
Multiple linked configurations are enumerated on U04; a Live badge does not hide
another unpublished/disabled configuration.

U04 shows feature metadata read-only and **Manage feature in Admin**, linking to
the configured ADMIN_ORIGIN /billing?view=plans&section=features&featureId=<id>.
Use a normal navigation link; no session token forwarding. Missing ADMIN_ORIGIN
shows explanatory text instead of an invented URL. Studio cannot create/edit
Feature, plan membership or ShopFeaturePreference. Not configured is informational:
non-conversation billing features are still valid features.

**Add behaviour** opens a dialog for capability key, display name and description;
feature binding is fixed to this Feature.id. Create calls createCapability then
opens U09. Saving this metadata creates no draft/release. If the key exists,
show a field error and retain input; no silent association with an existing row.
U04 configuration rows show display name, enabled state, latest draft/published
revision and active-release membership; Open goes to U09. Back from U09 returns
here. No feature-name whitelist and no automatically selected development tool.

### U05–U06: tool library and editor

U05 rows: display name, immutable MCP name, enabled state, latest published
version, draft count and feature usage count. Search name/displayName, filter
has-draft/published/disabled, sort displayName,id. Empty state offers **New tool**.
ADMIN can create/edit/test; only SUPER_ADMIN sees publish/enable/disable controls.
Direct server requests enforce the same roles.

**New tool** opens a dialog with display name, immutable MCP name and optional
staff description. createTool succeeds -> U06 metadata view with **Create draft**.
If entered from U09, preserve returnCapabilityId after validating that record;
never take an arbitrary return URL. Creating a tool does not attach it to a feature.

U06 has Metadata, Definition and History tabs. Metadata edits staff display name
and description; tool name is read-only. **Disable tool** (SUPER_ADMIN) confirms
explicit desired value=false and reason; pending guard then setToolEnabled. Show
that every associated feature is affected, including calls in existing grants.
Enable is an explicit true operation; it cannot add new versions to old grants.

Definition selects a draft or published revision by ID; default newest draft,
otherwise newest published, otherwise Create draft. **Create draft** selects an
optional published source from this tool and proposed SemVer (first1.0.0);
without a source the C14 structural draft defaults are used. The action calls
createToolDraft, and stays U06 on the returned revision. An incomplete draft may
save if structural C14 bounds hold; it cannot publish. No hard-coded tool choices.

Definition editor has these steps, with persistent progress and Back/Next inside
U06 (no extra routes):

1. **Purpose**: agent-facing description/when to use, proposed definition version.
2. **Inputs**: field name, description, supported type, required/optional and
   bounds; Add field and Remove field. Generated strict input schema is viewable.
3. **Retrieve information**: select Public Shopify query or Recovery/discount
   operation. Query: Browse Shopify -> U07; field selection, named query, variables
   and resultPath are editable here too. Advanced GraphQL view stays within C14.
   Policy operation: select documented adapter/version and its argument mappings.
4. **Map inputs**: each variable/argument has Agent input or Fixed value choice;
   choose compatible declared input or type-valid literal. Required missing and
   incompatible mappings show errors. Domain/credentials are never editable.
5. **Response**: select Text or List; select schema-derived result/list path;
   insert allowed field chips; edit unavailable text and empty text for lists.
   Show output schema and synthetic facts beside rendered text. No calculations
   or unsupported token expressions. The agent still composes the final answer.
6. **Review and test**: show exact agent descriptor and server-only execution
   definition in separate read-only panels, validation errors and test results.
   **Test** goes U14 with tool revision and return context. **Save draft** stays
   U06 with returned editVersion. **Publish tool version** opens the SUPER_ADMIN
   confirmation described below.

Save is available in every step; incomplete structural-valid drafts are labelled
Not ready to publish. No autosave. Step changes retain in-memory edits; entering
U07/U14 requires saving first or explicitly discarding edits. Previous test and
validation results become stale immediately after any semantic edit; show that
state and do not present an old result as validation of the new draft.

Publishing tool version: show changed fields, reused-feature impact, validation
result, version and reason. It calls publishToolRevision and stays U06 on the
immutable version. It does NOT update existing feature associations or activate
a release. If returnCapabilityId exists, offer **Attach this version** -> U09's
association dialog preselected; attachment still requires explicit draft save.
History rows open exact revisions and compare with another version of this tool;
never mutate/delete published versions. Usage rows link to U04/U09.

### U07: Explore Shopify inside Studio

Two tabs: **Documentation** and **Schema and query builder**. Show supported API
surface and pinned2026-07 version; distinguish other documented Shopify APIs from
what this executor can run. Default to the public Storefront query surface.

Documentation: search input/button -> in-page results with title, excerpt and
source attribution. Select result -> in-page document panel, Back to results
preserves query. Links to relevant schema fields open the schema tab. Source links
are optional references, never a required step outside Studio. Display search
failure inline with Retry; retain query, current draft and available schema view.

Schema: search types/fields, select permitted root, expand nested fields and
arguments, show descriptions, type/nullability, examples, token requirements and
execution restrictions. Token-required or disallowed fields remain explanatory
but cannot be added to an executable selection. Variables require mappings;
connection counts are fixed bounded literals. Field selections build a named
GraphQL document and derived result choices without requiring typed GraphQL.
Advanced editor uses the same structural validator; errors select the offending
field/line. A valid schema does not imply real inventory or discount eligibility.

**Validate** stays U07 with field errors or Valid for this schema. **Use in tool**
requires an existing U06 draft context, displays an execution-change diff and
returns the proposed document/mappings/resultPath to U06 for explicit Save draft.
Without a draft context it opens New tool, then Create draft before applying the
selection. Losing create/draft responses reconcile original operation IDs; do
not create a second tool. Cancel returns U06 without applying proposed changes.
U07 never publishes, invokes a live merchant tool, or calls the live MCP endpoint.

### U08–U09: platform configurations and feature behaviour

U08 lists only BASE/RECOVERY_POLICY configurations. conversation_core is the
platform grounding/referral prompt with no mandatory product tools. Existing
recovery-policy discount behaviour is distinct from creating a paid feature.
Open row -> U09. No create BASE/RECOVERY_POLICY from this page; explicit seed
operations create reserved rows. BASE identity remains immutable.

U09 shows ownership/binding, enabled state, active revision, draft/published
revision picker. For no draft, **Create draft** clones a selected published
revision or asks for a nonblank initial prompt to start a prompt-only draft
with no tool bindings. Editor fields: prompt text,
maxSearchResults and maxRecommendations within C4 bounds, associated tools table.
**Add tool** opens a searchable picker of published enabled tools and exact
versions; draft-only versions cannot be selected. **Create tool** opens U06 flow
with validated return context. **Change version** shows definition diff and
requires selection; **Remove** removes only the local draft binding. These
changes commit only on Save draft (one updateDraft/editVersion/audit). Unsaved
changes remain subject to the global navigation guard.

Show a warning when the chosen tool is shared by other configurations; replacing
this binding changes only this draft. Publish capability revision validates all
bindings and freezes prompt/settings/associations; it does not activate a release.
Its success offers **Create release** -> U10 with that revision preselected.
**Test behaviour** -> U14 after save. SUPER_ADMIN enable/disable has explicit value,
reason and confirmation. Back goes U04 for FEATURE and U08 for platform bindings.

### U10–U11: releases, activation and rollback

U10 shows active release, compatible release history, created actor/time and
Open action. **Create release** opens a member-selection dialog, prefilled from
the active release and any explicitly selected newly published revision. Select
one published revision per capability; require conversation_core, positions
0..n-1, max32 members, compatible contract/runner and no conflicting revisions
of shared tools. Display diff from active release and identify each conflict;
never silently choose newest. Cancel creates nothing. Confirm reason and
createRelease -> U11 with the resulting immutable release. No implicit activation.

U11 tabs Overview, Changes and Versions show exact capability/tool revisions,
shared tool reuse, compatibility, inclusion and relevant audit metadata. Links
open exact U09/U06 revisions. **Activate** (SUPER_ADMIN) shows current pointer,
expected version, target release and new-conversation impact. Confirm invokes
activateRelease; success stays U11 with Active badge. Pointer conflict keeps
selection, refetches and requires a new deliberate confirmation. Rollback is
choosing a previous compatible release from U10, opening U11 and confirming
**Rollback to this release** with reason; same CAS/replay rules, no rewriting
history. Existing conversations retain their original versions. A missing schema
or executor prevents activation with its exact reason.


### Response contract authoring (C16; U10 composer and U11 detail)

U11 adds a **Response contract** tab beside Overview, Changes and Versions. Show
release ID, contract version/hash, read-only fixed delivery fields with descriptions,
published instructions, details schema and example validator. **Edit as new release**
opens the U10 Create release dialog using this exact release's members and definition,
not the current active release. Published rows are never edited in place.

U10 Create release dialog has **Members**, **Response contract**, **Review** steps.
Response contract step shows locked envelope fields and editable Instructions plus
Details JSON Schema editor, built-in empty baseline/example, inline supported-keyword
reference and limits from C16. No external toolkit is needed. Example final response
editor and **Validate** show JSON Pointer field errors; invalid definition blocks
Review/Test/Create. Every edit clears prior validation/test success. Fresh creation
copies the active definition or uses C16 baseline if no active release exists.

**Test conversation** passes the local draft definition and selected published
members to U14. Keep the unsaved composer in a tab-local authenticated layout provider that
survives U10 -> U14 -> Back navigation. Store a synthetic handoff ID, selected
revision IDs, draft response definition, validation hash, reason and allowlisted
return route; never put the definition in a URL or browser storage. U14 copies
and validates this state as authenticated preview input; Back restores the exact
composer. Refresh, sign-out or loss of authorization clears it and displays
**Draft unavailable—return to Releases** with a U10 link. Late validation results
apply only to the same content hash. U14 freezes the definition at
Start and displays separate Reply and Structured details panels. Reset permits a
new definition; no automatic publication. No customer data in browser storage.

Review displays member and response-definition diffs, validation state, reason and
new-conversation-only effect. SUPER_ADMIN **Create release** invokes the existing
replay-safe createRelease with the full definition, then opens new U11 Response
contract tab. Activate remains a separate confirmation. ADMIN sees Validate/Test
but disabled Create with role explanation. Cancel/close/back with dirty edits asks
Discard or Keep editing; discard writes nothing. Failed validation/publish retains
inputs; unknown outcomes reconcile the same operation ID. Immediate synchronous
submit guards, disabled conflicting controls and accessible pending/error states
apply to Validate/Test/Create; late validation cannot approve changed input.

Traversal case N13: U11 Response contract -> Edit as new release -> U10 Response
contract -> edit -> Validate -> U14 Test -> Back -> Review -> Create -> new U11 ->
Activate. Check cancellation, role denial, invalid schema, duplicate activation and
existing-conversation pinning at terminal system validation. COMMERCE-008 tests
the U14 handoff/return with a preview stub; COMMERCE-009 tests the real U14 round
trip. COMMERCE-008 acceptance does not require COMMERCE-009. This C16 extension supersedes the original approved
prototype's release panels; other U01–U14 routes and traversals remain unchanged.

Publication stages are tool version -> capability revision -> release -> active
pointer. Each has its own stable operation ID and confirmation. Failure at a
later stage preserves earlier published records and provides a link to resume.
A timeout is Unknown outcome: reconcile that stage before offering another write.

### U12–U13: merchant inspection

U12 search by shop ID/domain, sort domain,id, shows shop label/domain and Open.
No phone-number or customer-history search. U13 shows actual plan, active release,
and rows separating Feature.active, enabled plan mapping, activation mode,
merchant preference, effective feature eligibility and published Commerce binding.
Show explicit exclusion reasons, not a single ambiguous Enabled switch.

**Agent tool list · new conversation** uses the production pure selection resolver
with authoritative read-only facts. Display deduplicated names, exact versions,
source feature/configuration and execution availability. Feature names link to
U04, configuration names to U09 and tool versions to exact U06 revisions. It does not create a
grant or call Shopify. No active release/unavailable policy facts produce a clear
unavailable result, never guessed eligibility. No preference or plan edit control.
No retained customer transcript or existing-grant browser in v1.

Below the list, show **How CommerceAgent receives this list** with three steps:
Background identifies the shop/recovery/conversation; Commerce resolves or reuses
its original grant; the agent requests tools/list under authenticated context.
Each tool row has **Agent descriptor**: expands in place to its exact MCP name,
description and inputSchema (read-only), with Close collapsing back to the row.
Never display execution definitions, service tokens or credential values here.
Show **New-conversation preview** beside the list; do not imply that existing
conversations use today's release. Empty selection shows **No remote tools
available** and the specific exclusion reasons. The global U05 library has a
**Inspect a merchant's tool list** link to U12; it is not the merchant-filtered list.


**Test this configuration** -> U14 with copied feature flags/release selection
as synthetic input (no customer/shop credential). Label that tests use fixtures,
not the merchant's live inventory. Back returns U13.


## Interfaces / Contracts

Visual baseline: [approved Studio prototype](../../../architecture/ARCH-020-studio-approved-prototype.html). Implement its exact U01–U13 page hierarchy and the embedded requirements; use Page & flow map to open the matching screen. The sample prototype does not replace server-side contracts or required states.

COMMERCE-003 protected services; immutable revision and release metadata.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C7, C9, C14, C15**. These are required acceptance inputs, not optional examples.

Implement the complete C15/U01–U13 routes against COMMERCE-003 operations. Show immutable published/draft distinctions, field validation and CAS conflicts; initial publish is a resumable sequence of explicit operations, not an unimplemented atomic composite. Enable/disable uses explicit desired value.

### Required evidence

Component/browser fixtures assert role-visible controls and direct server denials, same-tick click/Enter effects, timeout replay with same operationId, stale-response suppression, keyboard focus, narrow layout and conflict input preservation. This UI task does not own production multi-turn runner tests.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-COMMERCE-002
- ARCH-020-DATABASE-001
- ARCH-020-SHARED-001

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-017
- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-013
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001

## Acceptance Criteria

- [x] Demonstrate the assigned C16 response-contract cases with named fixtures and actual outcomes; reference the exact published definition/hash or synthetic preview definition used.

- [x] U05 clearly identifies the global library; U12 -> U13 displays the merchant-specific new-conversation tool list. Each Agent descriptor expansion exactly matches the corresponding tools/list descriptor produced by the shared resolver for the same fixture grant, with no execution/credential fields.

- [x] U01–U13 match the page register and each page's actions/destinations below; direct links and browser Back work, missing IDs are404 and denied roles leak no data.
- [x] N01–N09 and N12 in the embedded validation matrix pass. Desktop/narrow and keyboard flows have focus/status evidence. All U14 entry links pass validated source/revision context; U14 implementation is completed by COMMERCE-009.
- [x] Complete U03 -> U04 -> U09 -> U06 -> U07 -> U06 -> U09 -> U10 -> U11 authoring/publishing flow for an arbitrary Admin feature and new query tool without leaving Studio or registering its name in code.
- [x] Shared tool reuse, exact version choice, dirty navigation, per-stage publication recovery and merchant exclusion reasons are visible; no published record or existing conversation is silently upgraded.
- [x] Search/docs failure preserves drafts and local schema editing; missing required schema/executor blocks publish/activation. Advanced JSON/GraphQL views are optional, never the sole authoring interface.

## Validation

### Mandatory navigation and acceptance matrix

All cases must be browser fixtures with expected destinations and side effects;
run mouse and keyboard paths, direct deep links, mobile navigation and denied roles.
COMMERCE-008 owns N01–N09, N12 and the composer/handoff portion of N13;
COMMERCE-009 owns N10–N11 and the real U14 round trip in N13; COMMERCE-011
owns discovery service contract fixtures consumed by N04. Shared checks are reused.

| Case | Traversal | Required result |
|---|---|---|
| N01 | Deep link U06 -> U01 -> Google success -> U06; revoked user -> U02 | Safe return path and current role checks, no data before authorization |
| N02 | U03 arbitrary Admin feature -> U04 -> Add behaviour -> U09 -> Back U04 | One configuration references existing Feature.id; no Feature/plan/preference writes |
| N03 | U05 New tool -> U06 Create draft -> six steps -> Save -> History -> exact revision | One tool/draft/save per deliberate action; no implicit publication |
| N04 | U06 Browse Shopify -> U07 search -> document -> schema builder -> Validate -> Use -> U06 Save | Complete inside Studio; invalid mapping/field blocks validation, failure retains input |
| N05 | U06 publish -> U09 attach exact version -> Save -> publish | Shared tool remains reusable; original feature revisions do not change |
| N06 | U09 Create release -> U10 dialog -> U11 -> Activate | Distinct replay-safe stages; active pointer changes once after confirmation |
| N07 | U10 previous release -> U11 Rollback | Only pointer changes; existing grants and published rows unchanged |
| N08 | U12 -> U13 -> feature/tool link -> Back | Dynamic eligibility and exact versions; no live grant or provider execution |
| N09 | Any dirty editor -> Back/Sidebar/Cancel -> Stay or Discard | Correct destination/focus, saved drafts retained, no accidental writes |
| N10 | U06/U09/U13 Test -> U14 fixture run -> Return | Correct source context, no live credentials/shop writes; results visibly synthetic |
| N11 | U14 start -> Send -> duplicate Send -> Cancel/timeout -> reconcile -> reset | One run, frozen preview grant, budgets enforced, no hidden retry |
| N12 | Save/publish/activate/disable/attach/create double-click, tap or Enter | One intended persisted effect, immediate busy state; unknown outcomes reconcile |
| N13 | U11 Response contract -> clone U10 -> validate -> U14 -> return -> create U11 -> activate | C16 validation, immutable release, roles; stubbed preview handoff here, real preview in009 and production pinning in SYSTEM-TEST-001 |

Each page is inspected at desktop and narrow viewport with keyboard focus,
loading/empty/error states. Tool/template/feature editing does not require an IDE,
manual external documentation search, JSON or typed GraphQL; advanced views are
optional. No broad assertion that this checklist alone proves factual AI safety:
C8 evidence and end-to-end adversarial cases remain required separately.

- [x] Run focused browser/component/action tests and the declared type/lint checks; retain the 24 route screenshots and add a reproducible populated component browser harness. Test form+button duplication, known failure, unknown timeout and stale completion.
- [x] Assert mutation counts, canonical command payloads and resulting records, not only button disabled appearance. List exact commands/results in the Completion Report.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; the actual repository must be provisioned before execution preparation.

## Completion Report

### Status

Ready for Review.

### Correction Checklist

- [x] **Attempt 3 R1 implemented:** `src/studio/contracts.ts`, the fixture and `docs/studio-service-contract.md` now carry C7/C14/C15/C16/C17 canonical data: separate metadata/draft/pointer CAS values, complete immutable tool definitions, complete capability drafts, exact ordered release members, `response.v1`, documentation traversal, full-definition validation, opaque CUID-shaped operations and explicit ADMIN/SUPER_ADMIN behavior.
- [x] **Attempt 3 R2 implemented:** `StudioWorkspace` now connects feature creation, complete tool definitions, U06/U07 handoff, dynamic published-tool association, capability prompt/settings publication, exact release member/response composition, distinct confirmed activation/rollback and navigation to returned opaque IDs. Production entrypoints render this common component boundary rather than successful reads as JSON. A test-only Vite harness renders populated components without adding a public fixture route.
- [x] **Attempt 3 R3 implemented:** unknown outcomes and thrown requests retain the original operation ID/input, lock all new writes and expose `Check original operation`; same-ID replay reconciles before unlocking. Stale CAS is distinct and retains input. Completion and validation tokens suppress stale responses independently.
- [x] **Attempt 3 R4 implemented:** exact requested revisions determine immutable/read-only versus draft editing. Merchant descriptors carry canonical `toolId`; no revision-ID parsing remains. Dirty navigation performs the intended destination after Discard, restores trigger focus on Stay and protects U06-to-U07 navigation.

### Files Changed

Implementation commit `00c40087ddb17ab996febc39fe04a949976feb59` updates the C17 contracts/fixture, common production workspace boundary, U06–U11 editors and composer handoffs, exact route context, dirty navigation, response preview handoff, focused tests, canonical contract documentation and the populated browser harness under `tests/browser-evidence/`. The prior 24 desktop/narrow route screenshots remain under `artifacts/ARCH-020-COMMERCE-008/screenshots/`.

### Work Completed

Production pages resolve 404 ownership through protected server reads and render the shared interactive component boundary with a fail-closed client adapter; no production module imports the fixture. The fixture now models canonical records and command payloads, success/empty/forbidden/unavailable/stale/unknown states, conflicting replay, stable operation replay, effect counts and returned opaque IDs. The components implement role-aware feature behaviour, full tool definition, documentation/schema traversal, dynamic exact revision association, capability prompt/settings, response-contract/release composition, separate publication and active-pointer changes, merchant descriptor inspection and a tab-local U10/U14 handoff.

### Requirement-to-Fixture Evidence

| Cases | Fixture result and asserted side effects |
|---|---|
| N02 / N12 | Add behaviour is submitted twice in one tick; fixture records `createCapability=1`, preserves the arbitrary `feat_01ARBITRARY` binding and navigation uses the returned `cap_*` ID. |
| N03 / N12 | New tool records one `createTool`, zero implicit revisions/publications and navigation uses the returned opaque `tool_*` ID. Service replay with one operation ID yields one persisted effect; conflicting reuse returns `CONFLICTING_REPLAY`. |
| N04 | Component traversal opens U06 -> U07, searches documentation, opens the in-page document, selects schema fields, validates the complete definition and returns to the exact arbitrary tool/revision context. |
| N05 | Capability editor loads published versions from `listTools`, never a seeded option; ADMIN cannot publish. Direct service evidence preserves full prompt/configuration/contract/tool bindings through publication. |
| N06 / N07 | Release composer selects exact published revisions/positions and validates/sends the complete response contract. Create is separate from confirmed activate/rollback with `expectedActiveReleaseVersion`. |
| N08 | Canonical descriptors contain explicit `toolId`, `toolRevisionId`, SemVer and public schema. Links never split or infer IDs and no execution/credential field is exposed. |
| N09 | Stale CAS retains tool definition input. Stay restores focus and Discard navigates the exact `/shops/shop_01LINEN` destination. U06-to-U07 applies the same save/discard boundary. |
| N12 | Unknown command leaves zero persisted effects, blocks new writes and same-ID reconciliation records exactly one effect/input when certainty is restored. |
| N13 composer handoff | Context retains exact members, response contract, validation hash, reason and return path across U10 -> U14 -> Back. Preview execution remains COMMERCE-009-owned. |

The exact C16 runtime response evaluation remains COMMERCE-009-owned. This task supplies the response-contract preview handoff and immutable release mechanics required by its assigned half of N13.

### Validation Results

- Focused Studio validation: `npm test -- tests/studio-services.test.ts tests/studio-workspace.test.tsx` — **2 files / 14 tests passed**.
- `npm run typecheck` — **passed**.
- `npm run lint` — **passed**.
- `npm run build` — **passed**, including Prisma Client generation, TypeScript and all U03–U13 routes.
- Populated browser rehearsal — the isolated `tests/browser-evidence/` Vite harness rendered the full arbitrary-ID draft tool definition editor and the release member/response-contract composer; accessibility state and visual output were inspected. It is not an application route and cannot ship as a fixture fallback.
- Prior screenshot inspection — **24 nonblank images**, 12 desktop at 1440x1000 and 12 narrow at 500x844, retained as authenticated shell/fail-closed route evidence.
- `git diff --check` — **passed**.
- Full `npm test` — **16 files / 85 tests passed**.

### Deviations

Real database, discovery, publication and selection adapters remain COMMERCE-013-owned. Production displays the explicit unavailable state until that composition is installed. Fixture-populated views exist only in component tests and the separate browser harness.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

No live Google OAuth, Shopify provider, merchant credential, customer data or production mutation was used. COMMERCE-009 owns actual U14 execution; COMMERCE-013 owns protected real adapter composition and integrated acceptance.

### Architectural Concerns

None. The prior full-suite readiness timing failures did not reproduce; all 85 tests passed together in Attempt 3.

### Git / VCS

Implementation commit `00c40087ddb17ab996febc39fe04a949976feb59` is pushed to `origin/task/ARCH-020-COMMERCE-008`. The parent/report branch contains this Attempt 3 review submission. Nested database submodule remains `5abfd87f57038bae515aaa09ec7c8db62adcfb98`. No main branch, parent service gitlink, Architect Review, architecture/index file or other task was changed.

### Attempt 4 Resubmission — 2026-09-21

**Status: Review.** Implementation `04c0838` is pushed to `origin/task/ARCH-020-COMMERCE-008`. This attempt implements A3-R1 through A3-R4 without changing the accepted Shared/database contracts or the COMMERCE-013 provider boundary.

- **A3-R1:** Studio contracts now alias the accepted Shared full/draft definition and response-contract types. Successful fixtures are parsed by `CommerceToolDefinitionSchema`, use the retained 64-character schema hash, a named `ProductDetails($handle: String!)` query, exact handle mapping/result path and canonical scalar response template. Discovery preserves the complete definition. Tool JSON editors retain raw invalid/intermediate text and parse only on explicit save/navigation actions.
- **A3-R2:** capability editing uses a detached full binding array with explicit add, replace and remove controls. Saves submit every unaffected exact revision. Shared `ToolBindingsSchema` enforces unique tool identities and the maximum of 32 without truncation; zero bindings remains valid.
- **A3-R3:** discovery and release validation are tied to the current canonical input hash and request token. Every semantic edit invalidates the prior result; synchronous guards suppress duplicate validation. Preview/create require the exact current validated members and response contract. Command completion clears dirty state only when no newer content revision exists; unknown reconciliation retains the originally admitted closure/input.
- **A3-R4:** production navigation uses App Router `push` beneath the persistent root provider. Shell, list and revision links share the pending-destination guard; unknown operations cannot be discarded. Editors are keyed by explicit revision identity and reads suppress stale completion. The isolated harness now has a functioning history adapter. Connected tests cover U06 -> U07 -> U06 and U10 -> U14 -> Back with exact IDs and authored content retained.

Permanent regressions assert canonical Shared parsing and invalid neighbours; raw JSON retention; two-binding prompt-only preservation; 32-binding/duplicate limits; stale deferred validation and a valid second run; duplicate validation suppression; a newer edit during pending save; exact connected handoff navigation; and the common navigation guard.

Validation:

- `npx tsc --noEmit --incremental false` — passed.
- `npm run lint` — passed.
- `npm test -- tests/studio-services.test.ts tests/studio-workspace.test.tsx tests/studio-shell.test.tsx` — 3 files / 22 tests passed.
- `npm run build` — passed, including Prisma generation, TypeScript and all Studio routes.
- browser evidence build — 184 modules compiled; the served isolated harness was exercised through U06 -> U07, schema selection, validation and return to exact `tool_01GLOBAL` / `toolrev_EVIDENCEDRAFT`; the returned named query retained `$handle`, its mapping and response template.
- `git diff --check` — passed before commit.
- `npm test` — 115/117 passed. The two unrelated `tests/readiness-docker.test.ts` descendant-handshake cases timed out before their helper wrote its readiness file; both reproduced when that file ran alone. All 22 Studio/task regressions pass, and the production build passes. No readiness implementation was changed in this task.

No live Google OAuth, Shopify provider, merchant credential, customer data or production mutation was used. COMMERCE-009 still owns preview execution and COMMERCE-013 still owns real service composition. No main branch or Architect Review content was changed.

### Attempt 5 Resubmission — 2026-09-21

**Status: Ready for Review.** Implementation commit
`558432f2f26890b3e7e44f64abd6ec27c4a50685` is pushed to
`origin/task/ARCH-020-COMMERCE-008`. This attempt addresses every mandatory
Attempt 4 correction without changing Shared, Database, COMMERCE-013 or the
Architect Review.

#### Correction checklist

- [x] **A4-R1 — full query structure:** `StudioWorkspace` now parses and
  structure-merges selected schema paths into the existing GraphQL AST. It
  preserves existing operation names, aliases, arguments, variables, nesting,
  result semantics and unrelated selections instead of rebuilding a hard-coded
  ProductDetails query. The deterministic schema fixture includes the nested
  `product.priceRange.minVariantPrice.amount` path and validates parsed field
  paths plus the required product handle mapping; an unsupported sibling is
  rejected and does not enable Use in tool.
- [x] **A4-R2 — record identity reset:** tool and capability editors are keyed
  by record ID plus resolved selected revision ID, including default draft
  selection. Route-identity load gating prevents stale page/detail data from
  rendering during transitions. A same-mounted two-record fixture asserts
  heading, description, target revision ID and edit version belong to record two.
- [x] **A4-R3 — admitted replay revision:** unknown commands retain the original
  operation ID, closure/input and admitted content revision through
  reconciliation. A newer edit remains dirty after the original operation
  succeeds; the fixture asserts the discard guard remains available.

#### Files changed

- `components/studio-workspace.tsx`
- `src/studio/testing/in-memory-studio-services.ts`
- `tests/studio-services.test.ts`
- `tests/studio-workspace.test.tsx`

#### Requirement-to-fixture matrix

| Correction / case | Fixture and asserted side effects | Result |
|---|---|---|
| A4-R1 nested discovery | `preserves nested query structure and mappings during discovery` selects `product.priceRange.minVariantPrice.amount`, validates, returns U07 -> U06, and asserts the nested query, preserved handle mapping and result path. | Pass |
| A4-R1 invalid sibling | `supports documentation, schema browse and full-definition validation` submits `unknownField` under the nested path and asserts `UNKNOWN_FIELD`, `valid: false`. | Pass |
| A4-R2 identity switch | `resets editor state when a mounted detail changes to another record` switches from `tool_01GLOBAL/toolrev_FIRST` to `tool_02SECOND/toolrev_SECOND`, asserts `SECOND CONTENT`, then asserts `updateToolDraft.toolRevisionId=toolrev_SECOND`. | Pass |
| A4-R3 unknown replay | `keeps newer editor content dirty after unknown save reconciliation` saves in timeout mode, edits newer text, reconciles the same operation ID, and asserts one effect plus the dirty discard dialog and newer input. | Pass |
| Duplicate protection / replay | Existing connected suite asserts double form submission creates one capability; service fixture asserts same-ID replay creates one effect and conflicting command reuse returns `CONFLICTING_REPLAY`. | Pass |

#### Validation results

- `npm test -- --run tests/studio-services.test.ts tests/studio-shell.test.tsx tests/studio-workspace.test.tsx` — **3 files / 25 tests passed**.
- `npm run lint` — **passed**.
- `npm run typecheck` — **passed** (`next typegen` and `tsc --noEmit`).
- `npm run build` — **passed**, including Prisma Client generation and all
  Studio routes U03–U13.
- `git diff --check` — **passed**.
- `npm test` — **24 files / 194 passed / 1 failed**. The remaining failure is
  the Redis-gated `tests/discovery-limits.test.ts` 30-second timeout. The two
  previously documented `tests/readiness-docker.test.ts` descendant
  signal-handler timing cases passed in this current run. No readiness or
  discovery-limits implementation was changed here; all 25 Commerce-008
  focused tests pass.

#### Worktree and dependency evidence

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-008`, branch `task/ARCH-020-COMMERCE-008`, clean after commit and pushed at `558432f2f26890b3e7e44f64abd6ec27c4a50685`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-008`, same mirrored branch, claimed Attempt 5 from parent claim `bcdcf12452681b91ab6d7e85aeaa02a7096b0ad8`.
- The implementation worktree consumed the existing declared `graphql@16.11.0`
  dependency; `npm install --ignore-scripts` restored missing prepared-worktree
  modules without changing package metadata. Nested Database remains at its
  recorded submodule revision; no schema or migration was changed.

#### Developer-owned live validation

Live Google OAuth, Shopify discovery/provider calls, merchant credentials,
production database/adapters, deployment/readiness infrastructure and the real
U14 preview round trip remain explicitly developer-owned or COMMERCE-009/
COMMERCE-013 scope. This attempt reports deterministic fixtures only and makes
no live-provider or deployment claim.

## Architect Review

### Changes Requested — Attempt 5 — 2026-09-21

**Current decision: Ready, Attempt 5 retained, executor/claimed_at null; not accepted.** Reviewed implementation `558432f2f26890b3e7e44f64abd6ec27c4a50685` and report `0b2e03bbaf5461eea1081e977260997335342977`, with clean dedicated worktrees and matching remote task heads. This supersedes earlier current-state wording. No implementation edit, next claim, dependent promotion or main integration.

**A4-R2 and A4-R3 are accepted.** Record/revision keying and route loading separation fix the reproduced cross-record state leak; admittedRevision is retained through replay and preserves newer dirty content. The original unaliased nested-query reproduction also passes. All three previous review reproductions passed independently, and the current focused Studio suite passed **25/25**. Preserve these fixes. The sole remaining blocker is the alias case of the already-required A4-R1 query semantics below.

#### A5-R1 — P1 — Merge selected fields into the intended aliased field

In components/studio-workspace.tsx, addPath deliberately excludes every field with an alias (`!selection.alias`). Given this existing definition:

```graphql
query ProductDetails($handle: String!) {
  selected: product(handle: $handle) { title }
}
```

with resultPath `selected`, selecting `product.priceRange.minVariantPrice.amount` creates two root selections: the original aliased product plus a new unaliased `product { priceRange { minVariantPrice { amount } } }`. The added field has lost the required original handle argument and is outside the retained resultPath. A component reproduction observed two roots where one was expected. The fixture validator checks the first product's argument and accepts the unbound second branch, so it does not protect this flow.

**Explicit correction instructions:**

1. Resolve schema paths against the intended existing AST field by schema field name while preserving its response alias, arguments and directives. For the unambiguous single-product example, extend `selected: product(handle: $handle)`; do not add another root. Preserve operationName, variable definitions/mappings and resultPath `selected`.
2. If multiple existing fields share that schema name but have different aliases/arguments, require a selected AST/response-path identity or reject the ambiguous edit with an actionable message. Do not merge into an arbitrary first field or invent an argument-free duplicate.
3. Make fixture query validation check every relevant field occurrence rather than only the first product root. The malformed duplicate/unbound branch must not be presented as valid or enable Use in tool. Keep the validation boundary injectable; no live provider composition or Shared/011 change is required.
4. Add a focused connected component regression starting from the aliased query above. Select the nested path, validate and return to U06; assert exactly one product root with alias `selected`, its original handle argument/mapping, nested selected field and unchanged resultPath. Include a denied ambiguous/unbound case. Retain the three passing previous regressions.

This finishes the existing alias/argument/result-semantics requirement; no general GraphQL editor expansion or exhaustive coverage is requested.

#### Validation and remaining scope

Independent prior reproductions: **3/3 passed** (`/tmp/c008-a4-review/acceptance.config.mjs`, 14 unrelated original cases skipped). Independent current Studio suite: **25/25 passed**. The additional alias component check in `/tmp/c008-a4-review/alias.test.tsx` **failed** with two root fields instead of one. Implementation diff whitespace check passed. Submitted typecheck/lint/build success and 194-pass/one Redis timeout full-suite result remain reported evidence, not independently rerun in full. No Redis/live Shopify call or new browser screenshot was made by this review.

The local U10 -> U14 -> Back component handoff is covered by the passing focused suite. The report's pending real U14 round trip refers to actual preview execution/provider integration owned by COMMERCE-009/013/developer validation; it is not a new008 acceptance blocker. Live OAuth, production adapters and deployment validation remain separate. The Redis-gated timeout is not this decision's blocker.

Correct only A5-R1 and resubmit the same branch pair with actual validation results. No dependent task is promoted; normal preparation owns the next attempt claim.

### Changes Requested — Attempt 4 — 2026-09-21

**Current decision: Ready, Attempt 4 retained, executor/claimed_at null; not accepted.** Reviewed implementation `04c0838a996136894d1bc00cf917fdd74b9548af` (Commerce PR3) and report `4f8c6180ccf5f35508e1d41d93c8e2fcea8bbd2a` (Workspace PR171). Dedicated worktrees clean and remote branch heads matched. This supersedes historical current-state wording. No implementation edit, next claim, dependent promotion or main integration.

Retain canonical Shared type/schema use, editable raw JSON, detached multi-binding state, content-bound release validation, persistent App Router composer provider and working connected simple handoffs. The submitted component tests including binding preservation, stale-validation rejection and ordinary in-flight save handling pass independently. The three remaining failures below concern original A3-R1/R3/R4 behavior, not exhaustive coverage or COMMERCE-013 production composition.

#### A4-R1 — P1 — Preserve the full query structure in discovery

`components/studio-workspace.tsx`, Discovery proposed definition: the builder still takes only each path's last segment and reconstructs a hard-coded product(handle:$handle) query. It overwrites resultPath and the handle mapping and cannot preserve nesting, aliases, other root arguments or variable semantics. Reproduction: select `product.priceRange.minVariantPrice.amount`; validation receives `query ProductDetails($handle: String!) { product(handle: $handle) { amount } }`, losing both nested containers. The injected fixture validator accepts the Shared envelope without compiling the query, so this broken definition can be described as valid.

Replace last-segment concatenation with structure-aware query construction, preferably the typed injected query-building/validation boundary already requested in A3-R1. Carry the complete source definition, field paths, argument mappings and selected result semantics. Preserve existing variables/aliases/nesting unless the user explicitly changes them; do not unconditionally replace execution with the ProductDetails example. Provide editable mappings/arguments needed by the supported workflow. Use the authoritative schema identity for success fixtures rather than treating a repeated-character hash plus envelope parsing as semantic validation. Fixture validation must reject invalid field paths/required arguments and verify the actual query/definition contract. No change to Shared/011 or installation of real013 adapters is requested.

Regression: exercise the nested selection above and assert its exact nested query plus mappings/resultPath through U06 -> U07 -> U06; an invalid sibling must not unlock Use in tool. Retain the working simple ProductDetails flow and raw JSON editing.

#### A4-R2 — P1 — Reset editor state on actual record identity changes

Detail keys ToolEditor/CapabilityEditor only by revisionId or the constant `latest-draft`. When a preserved workspace switches between two record detail IDs without explicit revision query parameters, the key is unchanged and useState retains the old record's data. Reproduction: first tool draft description FIRST CONTENT, second tool draft description SECOND CONTENT; after rerender/navigation the heading is Second tool but the Description still reads FIRST CONTENT. A subsequent save uses the second selected revision ID with the first tool's definition. The browser harness key={path} hides this state-retention path; production's workspace wrapper does not apply that key.

Key/reset the editor using both record ID and the resolved selected revision ID (including default draft selection), after the dirty-departure guard. Apply the same rule to capability editors. Cancel/invalidate obsolete loads when route identity changes and avoid showing editable previous detail under a new route. Test a same-mounted-workspace transition between two distinct records without revision parameters: heading, input values, saved target ID and expectedEditVersion must all belong to the second record. Also retain explicit revision navigation behavior. Do not rely on a harness-only remount to satisfy production semantics.

#### A4-R3 — P1 — Retain the originally admitted content revision during replay

StudioWorkspace.attempt captures submittedRevision afresh on every invocation. An unknown operation stores its original run closure but not the original content revision. During reconciliation, the newly captured revision equals the current newer edits, so success clears dirty even though the replay saved the older input.

Exact reproduction: edit description to admitted content; Save returns unknown; edit to newer unsaved content; Check original operation returns OK for the old write; Back no longer opens the discard guard. The newer text is falsely marked saved and can be lost. This is distinct from the ordinary deferred-success case covered by the new submitted test.

Store the admitted content revision/hash alongside operationId, original immutable input/run and onSuccess when the command is first dispatched. Reuse that original revision across every reconciliation. Clear dirty only when current editor content matches the originally admitted content. Alternatively disable all conflicting editing for the entire pending/unknown operation lifetime. Do not allocate a new operation ID or overwrite admitted payload on replay. Add the exact regression, asserting same ID/input, preserved newer text and a dirty guard after replay success. Retain the existing unknown-write lock and ordinary in-flight save regression.

#### Validation and resubmission

Independent component harness `/tmp/c008-a4-review/review.test.tsx` imports the actual committed components: **14 submitted component tests passed; 2 additional review tests failed** (nested query construction and record-switch state). A separate `/tmp/c008-a4-review/replay.test.tsx` reproduced the **third failure**, lost dirty state after unknown-operation replay. Exact triggers/results are recorded above. The temporary esbuild/oxc configuration warning is harmless harness output. Implementation diff whitespace check passed. Submitted 22 focused, typecheck/lint/build and browser traversal are acknowledged as reported evidence; no new independent browser screenshots or full-suite run were performed.

The reported 115/117 full-suite result and separately reproduced readiness helper timing failures remain documented; readiness files are unchanged by this correction and are not the reason for Changes Requested. Live integration remains developer-owned/COMMERCE-013 scope. Fix A4-R1–A4-R3 on the existing branch pair, run focused behavioral regressions and required checks, and resubmit accurate evidence. No broad coverage expansion, production provider wiring, main merge or dependent execution is requested.

### Changes Requested — Attempt 3 — 2026-09-21

**Current decision: Ready, Attempt 3 retained, executor/claimed_at cleared; not accepted.** Reviewed implementation `00c40087ddb17ab996febc39fe04a949976feb59` (Commerce PR3) and report `826f871ef2da60c77f9145bdc8a1ea932eb485f8` (Workspace PR171). Dedicated worktrees clean and remote task heads match. This supersedes historical current-state wording. No implementation edits, new claim, dependent promotion or main integration.

Preserve progress: common interactive production boundary with unavailable adapter, explicit revision IDs/tool ownership, server-provided role use, same-operation reconciliation, selected release members and response fields. C17 still permits component/fixture acceptance; real013 provider composition is not requested here.

Independently reran submitted Studio tests: **14/14 passed**. Temporary component harness `/tmp/c008-a3-review/workspace-review.test.tsx` imports actual committed components and extends submitted fixtures. Initial run:9 original component tests passed and2 review cases failed. Final focused run with a valid second published tool and a Shared-schema case: **3 review tests failed,9 unselected originals skipped**. Failures: prompt-only save drops the second binding; stale validation enables changed release content; fixture-declared valid definition fails accepted Shared validation. The harmless temporary esbuild/oxc option warning is not a product failure. Full85/type/lint/build are submitted passing evidence; implementation diff check independently passed. No live/provider calls or new browser screenshots were made in this review.

#### A3-R1 — P1 — Use canonical definitions and contract-faithful query authoring

Files: `src/studio/contracts.ts`, `components/studio-workspace.tsx` emptyDefinition/ToolEditor/Discovery, `src/studio/testing/in-memory-studio-services.ts`, and contract/component tests. The port still redefines accepted ToolDefinition/ResponseContract as broad records. Both the fixture published definition and new draft use `schemaHash:'schema-2026-07'` and `responseTemplate:{template:...}`, which fail Shared publication validation. Fixture validateToolDefinition merely checks that the document includes `{` and reports valid. This masks the broken authoring flow rather than proving C17 compatibility.

Alias/import accepted Shared draft/full definition and response-contract types; preserve intentionally invalid draft JSON as editor text, not as a fake published definition. A success fixture must pass CommerceToolDefinitionSchema and the relevant accepted contract. Use the retained authoritative schema hash and canonical response template (e.g. `{kind:'text',text:'{{result.title}}',unavailable:'Product data is unavailable.'}` for a matching selected output). Keep explicit invalid/unavailable fixtures separate. Do not change Shared or011 implementation to accommodate invalid UI payloads.

Discovery currently synthesizes `query <name> { product { <last path segments> } }`, discarding required product arguments, variable declarations, nesting and original result semantics; the editor cannot configure variables, execution kind or policy arguments. Preserve/build the full named definition through typed schema selection and argument/mapping input, including aliases/nesting/variables/resultPath. Use an injected query-building/validation boundary with contract-faithful fixtures where needed;013 owns concrete adapter wiring, not reconstructing user inputs missing from008. On return to U06, carry the complete validated definition and mark it dirty until explicitly saved. Verify an exact ProductDetails definition with mapped handle and valid scalar template, as well as invalid neighbors; a brace check is not validation.

Tool input/response JSON textareas parse on every keystroke and discard invalid intermediate text. Keep raw text state for editing, parse/validate on explicit actions and show field errors without replacing input. Add a user-typing test that clears and enters JSON incrementally, saves the intended complete definition, and reports invalid JSON without losing it.

#### A3-R2 — P1 — Preserve all capability tool bindings

File: `components/studio-workspace.tsx` CapabilityEditor. It initializes only `selected.toolBindings[0]` and always submits either `[binding]` or `[]`. A prompt-only save silently removes every other existing binding. Reproduction uses two actual published tool records/revision IDs: outgoing updateDraft contains only the first. This violates the exact full-binding requirement even when no association was edited.

Replace singleton state with a detached array initialized from the selected revision. Provide explicit add/remove/replace selection per tool; preserve every unaffected binding, validate unique tool IDs and exact published revisions, and support the canonical maximum32. Never infer removal from a single-select UI. A base capability may have zero tools. Save the complete array. Tests: load2 and32 bindings, edit only the prompt, assert outgoing array unchanged; replace one revision, remove one explicitly, and add one arbitrary published tool with exact expected payload. Reject duplicate tool identity without losing input. Preserve SUPER_ADMIN publication controls and independent server authorization.

#### A3-R3 — P1 — Tie validation and pending writes to current content

File: `components/studio-workspace.tsx` ReleaseComposer validation state/handlers and command success handling. The async validate closure compares its captured responseContract to itself; instructions/schema/member changes do not increment validationToken. A pending old validation resolves valid after an edit and enables Create immutable release/Test conversation for content that was never validated. This failure is independently reproduced.

Increment a revision/token synchronously on EVERY relevant edit and invalidate a structured validation record. Retain `{token,canonicalInputHash,result}` rather than testing a display string's startsWith('Valid'). Compare completion against a ref containing the CURRENT token/hash. Only allow create/preview when that exact current contract (and any membership inputs covered by validation) has a successful result. Show pending state and acquire a synchronous guard before the validation await; duplicate activations issue one request. Invalid/failed results leave controls locked and preserve authored text. Discovery validation must use the same current-content discipline; provider failures must not leave an earlier valid result enabled.

While a write is pending, either disable all conflicting editable fields or retain a content revision so completion cannot clear dirty state for edits made after dispatch. Unknown-outcome same-ID replay must retain its original admitted input. Tests: deferred success followed by instructions edit, schema edit and membership change cannot unlock new content; a second validation for current content can; double activation issues one validation; edit during save cannot falsely mark newer text saved. No extra publication/recovery attempts on reconciliation.

#### A3-R4 — P1 — Make actual navigation preserve handoffs and protect dirty edits

Files: `components/studio-workspace.tsx`, `components/studio-composer-context.tsx`, `components/dirty-navigation-guard.tsx`, shell/revision links and the browser harness. Default navigate uses window.location.assign, but composer state exists only in React useState. U06 sets context then reloads /explore, losing the originating draft; release -> preview similarly loses members/response state. Existing component tests inject navigate spies and rerender the same provider, concealing the failure. `tests/browser-evidence/main.tsx` sets navigate to a no-op, so the populated screenshot harness cannot establish page-to-page traversal.

Use the App Router client navigation mechanism with a persistent root provider, or a deliberately scoped/persisted handoff restored across reloads; do not rely on a state update immediately before document replacement. Keep record/revision/return destination exact. Provide a functioning isolated harness navigation adapter that actually changes the page/route and retains the same state semantics as production; no public fixture route or production fallback. Exercise actual U06 -> U07 -> U06 and U10 -> U14 -> Back, asserting selected IDs and complete unsaved authored content survive.

DirtyNavigationGuard still protects only its own Back/Browse buttons. Sidebar and revision-history Links bypass it, list tool/release editors have no guard, and ReleaseComposer Cancel closes immediately. Route all specified departures through a common pending-destination guard, with Stay preserving input/focus and Discard continuing to the exact destination. Do not replace this with arbitrary history.back. Protect unknown operation context from being silently abandoned. On same-page revision/record navigation, key or reset ToolEditor/CapabilityEditor to the explicitly selected identity after the guard; current useState initialization alone can retain the previous revision's fields. Suppress stale read completions after navigation.

Tests: dirty sidebar departure, revision change, list-editor departure and composer Cancel all show the guard; Stay/Discard and focus/destination are asserted. Switch between two distinct draft revisions without full reload and verify fields/CAS IDs correspond to the selected revision. Browser evidence must exercise real navigation, not only static populated screens or unavailable production routes.

### Attempt 3 resubmission gate

Implement A3-R1–R4 on the same mirrored branches; these finish the previous four corrections, not new provider scope. Promote the three reproduced regressions to permanent tests, add connected navigation/authoring cases above, and run focused/full local checks plus type/lint/build/diff. Update the report with actual command payloads, preserved content and effect counts; distinguish static screenshot evidence from exercised traversal. Preserve prepared isolation/dependency evidence. Commit/push then return to Review. This parent overlay is published before handoff; no main merge or dependent execution is authorized by the review.


### Changes Requested — Attempt 2 — 2026-09-21

**Not accepted; Ready, Attempt 2 retained**, executor/claimed_at null. Reviewed
implementation `6c4ecbc853c8ecb517e42fe17d2b67edf4fd0233` (PR3) and report
`10fc0ae6fe7fb02ad1934e95950d05b2b3309f07` (PR171); both worktrees clean and
published PR heads verified. No new claim, implementation edit, main integration
or downstream promotion. C17 still permits fixture-based component completion;
real provider composition is not the blocker.

Useful progress: typed read result states, production unavailable composition,
Next notFound mapping, dynamic shell release availability and labelled mobile
navigation replace several original placeholders. Test fixtures stay out of the
production service factory. Preserve this work.

#### R1 — P1: make the ports carry the canonical authoring data

`src/studio/contracts.ts` has C7 method names but incompatible/incomplete payloads.
ToolRevision.version is numeric; one expectedVersion substitutes for the distinct
expectedEditVersion/expectedUpdatedAt CAS fields. updateToolDraft carries only
schemaFields/query rather than the full accepted definition. Capability drafts
cannot carry promptTemplate/configuration/contractVersion. createRelease carries
capability IDs, not exact published revision members/positions, and contains no
C16 responseContract. Discovery has no documentation search/document operations
or authoritative definition-validation contract. A real013 adapter cannot recover
authored values the UI never supplies.

Correction: align ports and docs/studio-service-contract.md with C7/C14/C15/C16/C17
canonical inputs/results, preserving separate definition SemVer, immutable
revision identity and edit CAS. Use the required operation ID shape. Carry full
response instructions/schema/examples and exact release members; keep008's C16
composer and read-only response tab here.009 owns runtime preview execution, not
response authoring. Add role-aware UI inputs; currently StudioWorkspace has no
principal/permission input and exposes release actions irrespective of role.
Keep server authorization independent through the eventual protected adapters.

#### R2 — P1: finish the connected authoring workflows

`components/studio-workspace.tsx` still cannot perform the claimed flow:

- Discovery shows field checkboxes but no documentation traversal. Use in tool
  editor links to /tools, dropping the originating tool/revision and built query.
- ToolDetail only offers a query textarea/save/create-draft; no input/response
  authoring steps or publish control. Save hard-codes schemaFields=['product.title'].
- CapabilityDetail asks staff to type a revision ID and defaults to fixture-specific
  tool-products-r1; no prompt/settings editor or publish action exists.
- ReleaseComposer always sends capabilityIds:[] and has no member/response-contract
  composer. ReleaseDetail labels rollback only on the currently ACTIVE release;
  the target is therefore that same active release, not the selected previous one.
  There is no actual confirmation despite sending reason='Confirmed activation'.

Correction: implement the existing task's editable fields and selection dialogs,
carry validated source/revision context and the query payload through U06/U07,
navigate to returned records after creation, publish exact revisions and compose
real release members/response contracts before separate confirmed activation or
rollback. Use arbitrary IDs, never seeded tool names. Demonstrate a connected
feature -> behaviour -> new tool -> discovery -> exact association -> release
flow with injected services and actual command payloads.

ProductionStudioPage currently renders every successful read using JSON.stringify;
StudioWorkspace is not referenced by any page. Provide the common component/view
boundary so013 installs adapters/minimal composition rather than reimplementing
the authored screens. Absent real adapters must still render unavailable; no
fixture runtime fallback is requested.

#### R3 — P1: preserve operation identity and lock on unknown outcomes

`StudioWorkspace.once` clears pendingRef for every returned failure, including the
fixture's 'Unknown outcome. Reconcile before retrying.' Every form submission then
creates a fresh random operationId. Thus after an uncertain create, the next
submit can create another operation instead of reconciling the first. The port
union collapses unknown/CAS/ordinary unavailability into a message, and there is
no reconciliation operation. A thrown promise also skips pending cleanup entirely.
Discovery validation has no same-tick or stale-response guard.

Correction: represent unknown versus definitive outcomes explicitly; retain the
original operation ID/input and reconcile/replay that operation before permitting
a new write. Preserve input on known failure, recover controls on thrown failures
according to outcome certainty, and suppress stale completions. Share guarded
submission across mouse/keyboard paths; control validation results independently
from new editor state. This is a missing behavior, not an exhaustive test request.

#### R4 — P2: honor exact revisions and navigation destinations

getTool validates revision ownership but returns all revisions; ToolDetail ignores
the selected revision and always chooses the first DRAFT. A link to a published
revision can therefore show/edit an unrelated draft. ShopInspector derives toolId
by splitting toolRevisionId on '-r', which only works for fixture IDs. Pass canonical
toolId separately and render the explicitly selected revision read-only or editable
according to its own status.

DirtyNavigationGuard only handles its own Back button; Discard closes the dialog
without performing navigation. Sidebar/editor links bypass it, and list editors
have no guard. Preserve the intended destination and implement Stay/Discard across
the specified navigation paths, including focus return. Do not rely on arbitrary
history.back for specified parent/context links.

#### Validation reviewed and resubmission

Reviewed all changed components/ports/fixture behavior and the desktop tool-detail
screenshot. The 24 images and reported route200 rehearsals document unavailable
shell states, not populated authoring workflows. Retain them as that evidence;
provide populated component/browser views for the corrected flow. The submitted
12 focused tests and successful typecheck/lint/build are recorded; full79/81 and
isolated readiness10/10 remain accurately distinguished. Readiness failures are
not the acceptance blocker. git diff --check passes.

An attempted isolated unknown-outcome component harness in /tmp failed to load
under jsdom/Vitest before executing any test; no independent component-test pass
or reproduced mutation count is claimed. R3 follows directly from the inspected
unconditional unlock and new-ID generation. No implementation files were changed.

Correct R1–R4 on the existing task branch. Prior R1/R2/R3 dispositions in the report
must reflect these remaining behaviors; method names and isolated fixture calls
do not establish the complete traversal. Preserve historical architect reviews,
update actual evidence, validate and push both branches. No new live OAuth/provider
run or other owner's implementation is requested. C17 ownership remains unchanged.

### Changes Requested — Attempt 1 — 2026-09-21

**Not accepted; Ready for correction.** Preserve Attempt 1, executor/claimed_at null. Reviewed implementation `865e16cc474ad9560bc3e948f7447a382195686e` and report `a6df81c13741d2f36cca4f47564d0f3f0e085629` in the launcher-resolved dedicated worktrees. Both were clean and remote heads matched. No new claim, implementation edit, main integration or downstream promotion.

The authenticated shell, ordered links, development badge and root redirect are useful progress. This submission is a route scaffold, not the component implementation required by C17. The latest parallel-delivery amendment explicitly retains every field, action, role, failure and side-effect requirement and says not to weaken them to static mockups. Real provider wiring remains COMMERCE-013-owned; missing component behavior belongs here and is not blocked on COMMERCE-011 acceptance.

#### R1 — P1: implement the authoring component and typed service ports

`components/studio-screen.tsx:14–28` supplies a generic empty section; the tools/capabilities list pages only render it. U07 explicitly says discovery will appear later. U03 has no catalogue read, filters or rows. There is no `src/studio/` implementation or `docs/studio-service-contract.md`, no StudioServices injection boundary, and no new authoring actions/forms/dialogs in the submitted change.

As a result a staff member cannot add behaviour to an arbitrary existing feature, create/edit/save/publish a reusable tool, select schema fields and build a query, attach an exact tool revision, edit capability prompts/settings, compose a response contract, create/activate/rollback a release, or inspect a merchant's resolved tool descriptors. These are the task's primary functions; routes displaying explanatory prose cannot perform N02–N08 or N13.

Correction: implement the C17 `StudioServices` ports and canonical-field mapping first; build the specified U03–U13 components against those ports. Inject populated/empty/error fixtures only through tests. Production with absent adapters must show an explicit unavailable state, never load fixtures or pretend the database is empty. Keep publication, discovery and resolver implementations with their owners; COMMERCE-013 supplies real adapters later. Complete the existing page-specific forms, roles, validation, exact revision choice, mutation guards, CAS/replay and input-preserving failures. Reusing PendingActionForm is appropriate, but existing auth uses do not implement authoring actions.

Acceptance evidence should demonstrate the core feature -> behaviour -> tool -> schema query -> exact association -> release flow and merchant inspection with injected service results and recorded command effects. Focus on functioning workflows and their failure behavior, not a larger test count.

#### R2 — P2: resolve detail records and distinguish missing, unavailable and denied states

`components/studio-screen.tsx:31–35` always renders Record unavailable, regardless of id, and never performs a read or calls notFound. Every feature/tool/capability/release/shop detail page passes arbitrary route text directly to this component. Valid IDs can never open, invalid IDs receive a normal page instead of the required 404, and revision ownership is not checked.

Correction: use authenticated typed detail reads, resolve validated revision and return contexts, render actual records, and map not-found to Next's 404 boundary. Preserve distinct unavailable and forbidden states. Do not mask a provider outage or denied read as a missing record. Demonstrate a valid deep link, an unknown ID and a foreign revision ID using injected ports; navigation must preserve the specified source context.

#### R3 — P2: implement truthful shell state and required navigation behavior

`components/studio-shell.tsx` always says No active release; `app/features/page.tsx` labels static empty content Live data. These claims do not derive from a read model. On narrow screens the CSS turns navigation into a horizontal link strip, with no labelled open/close menu or selection-to-heading focus behavior. There is no dirty-editor Stay/Discard navigation because editors are absent.

Correction: supply active release/availability through the shell read model, distinguish unavailable from genuinely empty data, remove false Live data claims, and implement the specified mobile menu and focus handling. Include dirty navigation and dialog focus return as the editors are built. Keep the existing auth guard and development badge behavior.

#### Evidence and resubmission

Reviewed all 16 changed files and the current C17/task split. The reported 69 passing tests and build/typecheck/lint establish the scaffold builds; the five focused tests are pre-existing auth source checks, not Studio workflow evidence. No test files changed in this submission. No redundant full-suite rerun was needed to confirm the missing implementation.

Local component/browser fixture validation, keyboard/narrow behavior and screenshot evidence remain COMMERCE-008-owned under the explicit task amendment. They were not reassigned to the developer or013. Live Google OAuth and real service/provider integration remain separate and are not new acceptance blockers here. Correct the report's delegation of local UI evidence. Provide the task's requirement-to-fixture mapping with actual behavior/results and prepared worktree synchronization evidence on resubmission.

Retain useful shell work, implement the owned component scope on the same task branch, validate, and push both branches. COMMERCE-009 owns actual U14 execution; this task owns valid entry/return context only. No other owner implementation or live deployment is requested. C17 dependencies remain 002/DATABASE-001/SHARED-001; do not restore the superseded pending-service dependency chain.

### Historical definition review

### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.

### Google-only and local development UI amendment

C7.1 governs U01/U02 and the authenticated shell: Continue with Google is the only
hosted sign-in choice. A server-resolved development SUPER_ADMIN bypass redirects
U01 to U03 and shows Development — SUPER_ADMIN across U03–U14. No UI bypass
selector or extra provider. Protected page/API/action guards remain server-owned.
