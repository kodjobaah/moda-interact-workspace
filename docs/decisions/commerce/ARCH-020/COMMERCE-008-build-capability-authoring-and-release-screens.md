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
status: pending
priority: 120
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-003
  - ARCH-020-COMMERCE-005
  - ARCH-020-COMMERCE-006
  - ARCH-020-COMMERCE-007
  - ARCH-020-COMMERCE-011
enables:
  - ARCH-020-COMMERCE-009
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
created: 2026-09-20
updated: 2026-09-20
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

- [ ] Implement exact C16 U10/U11 response authoring panels and N13 traversal embedded below, including instructions/schema/example editors, local draft retention, roles, validation and separate creation/activation. Cover R05/R09/R10.

- [ ] Implement each page and dialog below with the exact route, entry points, fields, actions, destination, Back/Cancel behaviour and empty/loading/error states. No placeholder links or inferred pages.
- [ ] Use COMMERCE-003 persisted operations, COMMERCE-011 discovery/compiler services and accepted COMMERCE-005/006/007 executor descriptors. U07 provides schema-driven authoring and inline help; typing GraphQL or visiting an external IDE is not required.
- [ ] Implement all mutations with shared immediate submission guards, explicit desired values, stale-response protection, server replay/CAS and input-preserving errors. UI cannot create Admin features or edit merchant entitlements.

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
members to U14. Keep the unsaved composer only in this browser tab's memory; Back
returns to it, refresh loses it with a clear notice. U14 freezes the definition at
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
existing-conversation pinning. This C16 extension supersedes the original approved
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

- ARCH-020-COMMERCE-003
- ARCH-020-COMMERCE-005
- ARCH-020-COMMERCE-006
- ARCH-020-COMMERCE-007
- ARCH-020-COMMERCE-011

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-009
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001

## Acceptance Criteria

- [ ] Demonstrate the assigned C16 response-contract cases with named fixtures and actual outcomes; reference the exact published definition/hash or synthetic preview definition used.

- [ ] U05 clearly identifies the global library; U12 -> U13 displays the merchant-specific new-conversation tool list. Each Agent descriptor expansion exactly matches the corresponding tools/list descriptor produced by the shared resolver for the same fixture grant, with no execution/credential fields.

- [ ] U01–U13 match the page register and each page's actions/destinations below; direct links and browser Back work, missing IDs are404 and denied roles leak no data.
- [ ] N01–N09 and N12 in the embedded validation matrix pass. Desktop/narrow and keyboard flows have focus/status evidence. All U14 entry links pass validated source/revision context; U14 implementation is completed by COMMERCE-009.
- [ ] Complete U03 -> U04 -> U09 -> U06 -> U07 -> U06 -> U09 -> U10 -> U11 authoring/publishing flow for an arbitrary Admin feature and new query tool without leaving Studio or registering its name in code.
- [ ] Shared tool reuse, exact version choice, dirty navigation, per-stage publication recovery and merchant exclusion reasons are visible; no published record or existing conversation is silently upgraded.
- [ ] Search/docs failure preserves drafts and local schema editing; missing required schema/executor blocks publish/activation. Advanced JSON/GraphQL views are optional, never the sole authoring interface.

## Validation

### Mandatory navigation and acceptance matrix

All cases must be browser fixtures with expected destinations and side effects;
run mouse and keyboard paths, direct deep links, mobile navigation and denied roles.
COMMERCE-008 owns N01–N09, N12 and N13; COMMERCE-009 owns N10–N11 with U14; COMMERCE-011
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
| N13 | U11 Response contract -> clone U10 -> validate -> U14 -> return -> create U11 -> activate | C16 definition validation, immutable release, role checks, original-conversation pinning |

Each page is inspected at desktop and narrow viewport with keyboard focus,
loading/empty/error states. Tool/template/feature editing does not require an IDE,
manual external documentation search, JSON or typed GraphQL; advanced views are
optional. No broad assertion that this checklist alone proves factual AI safety:
C8 evidence and end-to-end adversarial cases remain required separately.

- [ ] Run focused browser/component/action tests and the declared type/lint checks; attach screenshots for every page in normal and narrow layouts. Test form+button Enter/click duplication, known failure, unknown timeout and stale completion.
- [ ] Assert mutation counts and resulting records, not only button disabled appearance. List exact commands/results in the Completion Report. No application runtime check is claimed during architecture authoring.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; the actual repository must be provisioned before execution preparation.

## Completion Report

### Status

Not Started.

### Files Changed

None; implementation has not started.

### Work Completed

None; task definition only.

### Validation Results

Not run. At execution, distinguish agent checks from exact developer validation required.

### Deviations

Task definition authored on local main by explicit developer request. Normal execution policy remains unchanged.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Commerce remote repository/submodule provisioning remains outstanding; role/route definitions exist in this review packet.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-COMMERCE-008. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

## Architect Review

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
