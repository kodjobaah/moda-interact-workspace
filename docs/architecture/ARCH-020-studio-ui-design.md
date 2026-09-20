# ARCH-020: Binding Studio pages and navigation

This is a required implementation specification for COMMERCE-008/009/011, not
an illustrative mock-up. Each task includes its owned page/action checklist and
acceptance cases. C7/C9/C14/C15 in the [contracts](ARCH-020-implementation-contracts.md)
supply backend behaviour, execution bounds and authorization. All UI labels below
are required English defaults; layout/styling can follow the application system.

## Approved visual reference and ownership

[Approved clickable prototype](ARCH-020-studio-approved-prototype.html) provides
the visual reference for the exact U01–U14 pages below. Open Studio screens or
Page & flow map and select the matching page ID; list/detail pages are different
screens, not interchangeable examples. Its sample rows and simulated actions are
not live data or a substitute for the contracts. Required fields, real mutation
semantics and state handling below take precedence over simplified prototype
controls. Preserve the approved sidebar order, page hierarchy and editor steps.

COMMERCE-002 implements authentication services; COMMERCE-008 owns U01/U02 visual
pages and all U03–U13 pages. COMMERCE-009 owns U14. COMMERCE-011 supplies U07
services, not another separate discovery page. GATEWAY-001 exposes these same
routes and never creates alternative UI pages. Their task instructions identify
these exact screen IDs and required acceptance tests.

## Global layout and navigation

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

## Page register

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
| U11 | /releases/[id] | U10 row, completed Create release | Members, exact revisions, diff, activation/rollback | Back to Releases U10 |
| U12 | /shops | Merchants sidebar | Read-only merchant search/list | Sidebar |
| U13 | /shops/[id] | U12 row | Eligibility breakdown and tool list for a new conversation | Back to Merchants U12 |
| U14 | /preview | Sidebar, Test from U06/U09/U11/U13 | Synthetic tool test and isolated conversation sandbox | Validated source page, or Features U03 |

No unlisted product pages or workflow routes are required. Creation, association,
publication and confirmations below are dialogs on these pages. /api/auth/*,
/api/studio/*, static assets and private health/MCP routes are transport routes,
not Studio pages. Query selection of revisionId must belong to its route entity;
mismatches are404, never silently switch to another entity or latest revision.

## U03–U04: existing features and Configure behaviour

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

## U05–U06: tool library and editor

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

## U07: Explore Shopify inside Studio

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

## U08–U09: platform configurations and feature behaviour

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

## U10–U11: releases, activation and rollback

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

Publication stages are tool version -> capability revision -> release -> active
pointer. Each has its own stable operation ID and confirmation. Failure at a
later stage preserves earlier published records and provides a link to resume.
A timeout is Unknown outcome: reconcile that stage before offering another write.

## U12–U13: merchant inspection

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

## U14: tool tests and conversation traversal (COMMERCE-009)

Landing has **Tool test** and **Conversation** modes. Source context preselects
saved draft/revision/release; direct navigation requires explicit selection.

Tool test: choose saved tool revision, synthetic scenario (success, empty, missing
fact, provider failure), enter schema-driven input, Run -> same page with mapped
variables/arguments, structured facts, rendered text and validation/failure codes.
No live Shopify request. Editing test input invalidates visible success until
rerun. Return to tool links to U06; code/schema edits occur there.

Conversation: choose saved behaviour revisions or release, synthetic feature flags
and fixture basket. **Start conversation** freezes synthetic prompt/tool grant;
then show chat with message input, Send, Cancel run, Reset conversation, trace and
remaining limits. Default Fixture mode is deterministic. Explicit Model mode uses
separate preview credentials and C9 quotas; controls explain unavailable config
or exhausted budget. No production model credentials/customer transcripts.

Send creates one previewRunId before dispatch, disables duplicate sends, preserves
input on known failure and shows Running/Completed/Failed/Cancelled/Unknown.
Trace lists discovered tools, chosen tool/input, structured output and final answer.
Cancel requests cancellation of that same run and waits for confirmed status;
unknown state is reconciled before another run. C9 max20 turns,32k history,24h
retention and model budgets apply. Reset confirms abandoning synthetic state and
creates a new preview conversation; never replaces a live grant. Changing selected
release/tools/flags requires reset confirmation; an ongoing preview does not gain
new tools. Back returns the originating page, or U03 when entered from sidebar.

## Mandatory navigation and acceptance matrix

All cases must be browser fixtures with expected destinations and side effects;
run mouse and keyboard paths, direct deep links, mobile navigation and denied roles.
COMMERCE-008 owns N01–N09 and N12; COMMERCE-009 owns N10–N11 with U14; COMMERCE-011
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

Each page is inspected at desktop and narrow viewport with keyboard focus,
loading/empty/error states. Tool/template/feature editing does not require an IDE,
manual external documentation search, JSON or typed GraphQL; advanced views are
optional. No broad assertion that this checklist alone proves factual AI safety:
C8 evidence and end-to-end adversarial cases remain required separately.
