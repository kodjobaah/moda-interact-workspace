---
id: ARCH-021
title: CommerceAgent configuration and live Studio authoring
status: agreed
coordinator: moda_architect
created: 2026-09-23
updated: 2026-09-23
---

# ARCH-021: CommerceAgent configuration and live Studio authoring

## Status

Agreed — Phase 0 contract accepted; Phase 1 architect-accepted Complete; Phase 2 task set defined; ARCH-021-DATABASE-001 is Ready.

This initiative defines the target product contract before implementation tasks are
materialised. It supersedes the ARCH-020 assumption that feature/capability revisions
own behavioural prompts and that the normal human-facing Studio preview is primarily
fixture-driven. ARCH-020's accepted immutable tool/release/grant/MCP, external
connection, credential, bounded-code and response-processing work remains reusable.

## Problem

Commerce Studio is intended to become the authoring environment for the real
CommerceAgent behaviour that Moda staff, and later merchants, will configure before
that behaviour is used by customers.

The current implementation has two ownership rules that do not match that product:

1. `CommerceCapabilityRevision.promptTemplate` makes behavioural prompts
   feature/capability-specific. When several features are selected, Background loads
   one prompt per capability and the Shared runner concatenates them. A single agent
   therefore has multiple independently-authored behavioural prompts with no clear
   shop-level ownership.
2. Model selection is deployment configuration rather than agent/shop configuration:
   Background reads `GROQ_COMMERCE_MODEL`, while Commerce preview reads
   `COMMERCE_PREVIEW_MODEL`. Studio testing therefore does not establish which model
   the shop's production CommerceAgent will use.

The target product instead requires one effective CommerceAgent prompt and one
effective CommerceAgent model for a shop. Features determine capabilities, tools and
feature configuration; they do not select a model or contribute separate behavioural
prompts.

## Goals

- Make CommerceAgent model selection platform/shop configuration, independent of
  features and releases.
- Make the editable CommerceAgent behavioural prompt platform/shop configuration,
  independent of features and releases.
- Allow Moda platform administrators to author application-wide prompt revisions and
  shop-specific prompt revisions in Commerce Studio.
- Allow a shop-specific model override selected from a Moda-controlled model
  catalogue.
- Use independent fallback for model and prompt:
  - shop override when defined;
  - otherwise platform default.
- Ensure exactly one configurable behavioural prompt is supplied to the runner for a
  turn, regardless of how many features are selected.
- Preserve immutable code-owned runner/protocol instructions separately from the
  configurable behavioural prompt.
- Freeze the resolved model and prompt revision when a production conversation grant
  or Studio preview conversation begins, without making model/prompt release-owned.
- Keep feature/capability ownership focused on feature settings and exact tool
  bindings.
- Establish contracts that can later permit merchants to author their own
  shop-specific prompts without giving them control over platform defaults.
- Establish the configuration foundation required by later ARCH-021 phases for live
  tool testing and production-equivalent multi-turn Studio preview.

## Non-Goals

Phase 0 does not implement:

- database migrations;
- Studio UI changes;
- provider calls;
- live tool testing;
- merchant authentication/authorisation;
- model-catalogue management UI;
- production Background changes;
- removal of synthetic fixtures from automated tests;
- changes to external connection/credential encryption or read-only HTTP policy.

Phase 0 defines the contract those later phases must implement.

## Current Architecture

### Prompt ownership

`CommerceCapabilityRevision` currently stores `promptTemplate`. Commerce manifest
capabilities each expose a `promptName`. Background iterates selected manifest
capabilities and loads each prompt through MCP. The Shared runner requires one prompt
per capability and concatenates all capability prompt texts into the model
instructions.

This is no longer the intended ownership model.

### Model ownership

Background currently selects the CommerceAgent model using
`GROQ_COMMERCE_MODEL`. Commerce preview independently selects its configured model
using `COMMERCE_PREVIEW_MODEL`/preview-provider configuration.

There is no durable shop-level model selection shared by Studio and Background.

### Release ownership

`CommerceRelease` currently owns the immutable capability composition and response
contract. `CommerceConversationGrant` pins the release, selected capability keys and
exact granted tools for a conversation.

That release/grant machinery remains useful, but model and prompt are not properties
of a feature or release.

## Core Ownership Decisions

### D1 — model ownership is platform/shop configuration

A CommerceAgent model is resolved for a shop using this precedence:

```text
shop model override
    ??
platform default model
```

There is one effective model for the agent. Selecting Feature A, Feature B or both
must not alter model selection.

A shop override and the platform default both reference entries in a Moda-controlled
model catalogue. API keys/provider credentials are runtime secrets and are never part
of the catalogue record sent to the browser.

### D2 — prompt ownership is platform/shop configuration

A CommerceAgent configurable behavioural prompt is resolved using this precedence:

```text
shop active prompt revision
    ??
platform active prompt revision
```

There is exactly one effective configurable behavioural prompt for the agent. A
shop-specific prompt **replaces** the platform-configurable prompt for that shop; the
two are not concatenated.

Platform administrators must be able to author and publish both:

- the application-wide/platform prompt lineage;
- a shop-specific prompt lineage for any shop.

A later merchant-facing Studio may grant a merchant permission to author/publish only
their own shop prompt lineage. The durable scope is the shop, not the administrator
who happened to author the revision.

### D3 — runner invariants remain code-owned

The configurable prompt does not replace security/protocol invariants implemented by
the Shared runner or Background host.

The effective model instructions are conceptually:

```text
immutable Shared runner/platform invariants
+ immutable response-contract instructions
+ bounded host instructions where architecture-approved
+ exactly one effective configurable CommerceAgent behavioural prompt
```

Platform/shop prompt authors cannot remove the runner's invariant safety, contract,
authorisation or evidence requirements.

### D4 — features/capabilities do not own prompts or models

A feature/capability revision owns only feature-specific material such as:

- feature configuration;
- exact tool-revision bindings;
- immutable revision/publication identity.

It must not own:

- model selection;
- behavioural prompt text;
- another feature-specific model instruction block.

`CommerceCapabilityRevision.promptTemplate` and capability-level `promptName` are
legacy ARCH-020 concepts to be removed by later implementation phases.

### D5 — releases do not own prompts or models

`CommerceRelease` remains the immutable deployable capability/tool/response-contract
composition. Model and prompt are resolved independently from platform/shop agent
configuration.

A release therefore does **not** gain `modelId` or `promptRevisionId` as ownership
fields.

### D6 — conversations freeze resolved configuration

Ownership and snapshotting are different concepts.

When a production conversation first obtains a `CommerceConversationGrant`, Commerce
resolves the shop's current effective model and prompt and the grant pins their exact
immutable identities. An existing conversation therefore does not silently switch
model or prompt when an administrator changes shop/platform defaults.

Likewise, when a Studio preview conversation starts, it resolves and freezes the
current effective model and prompt for the selected shop. Editing a prompt/model
requires starting/resetting a preview to observe the new configuration.

New conversations use the newest effective configuration.

This snapshotting does not make the release the owner of either setting.

### D7 — prompt templates are authoring inputs, not runtime configuration

Commerce Studio may provide reusable **application-wide prompt templates** maintained by
platform administrators. A template is not itself an active CommerceAgent prompt and is
not associated with a feature or model.

Using a template means:

```text
published template revision
        |
        v
copy exact text into a new prompt draft
        |
        +--> record sourceTemplateRevisionId for provenance
```

The resulting prompt draft/revision is independent. Publishing a newer template revision,
editing the template or disabling it must not mutate any platform/shop prompt previously
created from it. Active prompt pointers always reference published **prompt revisions**,
never template revisions.

Phase 2 supports platform-wide templates only. Merchant/shop-owned reusable template
libraries are deferred to the merchant-access phase unless later product requirements make
them necessary.

### D8 — prompt templates use a data-driven category/classification taxonomy

Each reusable prompt template belongs to one platform-managed category/classification.
Categories are durable data, not a code/Prisma enum. A category such as:

```text
Clothing & Fashion
```

may contain multiple prompt templates. New categories, category renames and category
disablement must not require an application/schema release. Category identity is stable;
disabling a category affects normal new authoring selection but does not delete existing
templates/revisions or invalidate prompt provenance.

The Phase 2 template library must support listing/filtering/grouping templates by category.
Merchant-owned categories/templates remain deferred with merchant access.

### D9 — Studio refactoring is incremental and domain-driven

Phase 2 must not turn `StudioWorkspace` into the owner of model, prompt, category or template
editor state. The new Agent Configuration surface gets a dedicated domain screen/module and
`StudioWorkspace` remains shell/navigation/orchestration for that surface.

This is **not** a wholesale Studio rewrite. Only code touched by the Phase 2 Agent
Configuration surface is extracted. Tools, Releases, Explore and other unrelated Studio
domains remain in place until their own phase requires change.

## Resolution Semantics

Model and prompt fallback are independent.

Examples:

| Shop model | Shop prompt | Effective model | Effective prompt |
|---|---|---|---|
| none | none | platform model | platform prompt |
| override | none | shop model | platform prompt |
| none | override | platform model | shop prompt |
| override | override | shop model | shop prompt |

Fallback occurs only when an override is absent.

If an explicit shop model override references a disabled/unavailable catalogue entry,
the runtime must fail closed with a configuration error rather than silently using a
different platform model. A broken explicit configuration must not masquerade as an
inherited configuration.

Published prompt revisions are immutable. A valid active prompt pointer therefore
cannot change the contents of an already-pinned revision.

A platform default model and a platform active prompt are mandatory for an
environment before CommerceAgent execution is considered configured.

## Environment Scope

Active platform defaults and shop overrides are environment-scoped. Development/test
configuration must not mutate production behaviour.

Conceptually:

```text
(environment, PLATFORM) -> default model
(environment, PLATFORM) -> active prompt revision
(environment, SHOP, shopId) -> optional model override
(environment, SHOP, shopId) -> optional active prompt override
```

Prompt revision content and immutable model catalogue identity may be reused across
environments, but active pointers/selections are environment-specific.

## Data Model

Exact Prisma names are deferred to the database task, but the architecture requires
the following durable concepts.

### Model catalogue

A platform-owned immutable/selectable catalogue entry containing at minimum:

```text
id
provider                 # e.g. OPENAI | GROQ
providerModelId
human display name
enabled/selectable state
created/updated audit metadata
```

Provider credentials are not stored in the catalogue.

A catalogue entry's provider/model identity must not be mutated after it has been
used by a frozen conversation. Changes that represent a different provider model use
a new catalogue entry; an old entry may be disabled for new selections.

### Model selection

Environment-scoped active selections:

```text
platform default model selection   # mandatory
shop model override                # optional per shop
```

The shop override is removable, returning that shop to inheritance.

### Prompt-template categories and immutable template revisions

Platform administrators may maintain data-driven application-wide prompt-template categories.
Each category has a stable identity/slug plus display metadata and can contain multiple
template identities. Every template belongs to exactly one category. Categories may be
enabled/disabled without deleting historical templates/revisions.

Within a category, platform administrators may maintain reusable template identities with
versioned draft/published revisions. Published template revision content is immutable.
Templates may be enabled/disabled for new selection without deleting historical revisions.

When a prompt draft is created from a template, the exact template revision content is
copied and the resulting prompt revision may retain `sourceTemplateRevisionId` as audit
provenance. There is no live inheritance/linkage after the copy.

### Prompt lineage and immutable revisions

There is one logical CommerceAgent behavioural-prompt lineage for platform scope and
one optional lineage per shop. Each lineage supports drafts/history and immutable
published revisions.

An environment-scoped active pointer selects:

```text
platform active prompt revision    # mandatory
shop active prompt revision        # optional per shop
```

A shop pointer is removable, returning that shop to platform inheritance.

### Conversation grant snapshot

`CommerceConversationGrant` must eventually pin at least:

```text
modelCatalogueEntryId
promptRevisionId
```

in addition to its existing release/capability/tool snapshot.

The grant records the exact resolved values, not only whether they came from platform
or shop scope. Source scope may also be retained for audit/presentation but is not a
substitute for the immutable IDs.

### Preview snapshot

A Studio preview conversation must freeze the equivalent effective configuration:

```text
selected shop
modelCatalogueEntryId
promptRevisionId / immutable prompt text snapshot
selected feature/capability revisions
exact tool revisions
```

Preview state remains isolated from customer WhatsApp conversation rows.

## Contracts

### Shared Commerce grant

The Shared `CommerceConversationGrant` contract will be extended in a later phase to
pin model and prompt identities.

### Commerce manifest

The manifest will move from per-capability prompt identity to one top-level resolved
agent prompt identity. Conceptually:

```text
manifest.agentConfiguration.modelId
manifest.agentConfiguration.promptRevisionId
manifest.agentConfiguration.promptName
```

Capability entries will no longer contain `promptName`.

When MCP resolves a manifest without an existing grant, it uses the current effective
shop configuration. When an existing grant is supplied, MCP must reproduce the
model/prompt identities pinned by that grant rather than re-resolving new defaults.

### Shared runner

`runCommerceTurn` will consume exactly one configurable behavioural prompt instead of
requiring one prompt per capability. Its immutable platform/protocol instructions
remain internal to the runner.

### Background

Background will stop treating `GROQ_COMMERCE_MODEL` as CommerceAgent behavioural
configuration. After grant resolution it will obtain the pinned model catalogue entry
and instantiate the provider adapter for that exact model.

Background will fetch one pinned agent prompt through MCP rather than iterating one
prompt per capability.

This keeps Background's behavioural change bounded: grant/manifest resolution remains
the source of Commerce configuration, and the existing conversation history and
`runCommerceTurn` flow remain in place.

## Studio Authoring Contract

Commerce Studio will eventually expose a dedicated Agent Configuration surface
separate from Features.

### Platform defaults

Platform administrators can:

- view/edit/publish the platform CommerceAgent prompt;
- create/rename/enable/disable prompt-template categories/classifications;
- create/version/disable multiple reusable application-wide prompt templates within each category;
- filter/group templates by category when creating a platform or shop prompt draft;
- create a platform or shop prompt draft by copying one exact published template revision;
- select the platform default model from enabled Moda catalogue entries;
- see the currently active prompt/model and their revision/identity.

### Shop overrides

After selecting a shop, platform administrators can independently:

- view the effective prompt and whether its source is PLATFORM or SHOP;
- create/edit/publish a shop-specific prompt;
- remove the shop prompt override to inherit the platform prompt;
- view the effective model and whether its source is PLATFORM or SHOP;
- select a shop-specific model from the Moda catalogue;
- remove the shop model override to inherit the platform model.

Feature authoring no longer contains a Behaviour Prompt field.

### Future merchant access

The shop-scoped prompt architecture is deliberately reusable for merchant access.
A later merchant authorisation phase may allow a merchant to manage only the prompt
lineage for their own shop. Merchants never gain permission to edit the platform
prompt or platform model catalogue/default.

Whether merchants may choose their own shop model override is an entitlement/policy
decision for the later merchant-access phase; the underlying shop-scope model
selection supports it without changing runtime ownership.

## Preview Configuration Contract

Starting a Studio conversation preview requires a selected shop. The preview resolves
that shop's effective model and prompt at start and shows their source/identity to the
user.

The preview then freezes those values together with the selected features/tools.
Subsequent turns use the same model, prompt and conversation history. A reset/new
preview is required to test newly-published prompt/model changes.

Later live-preview phases will replace normal human-facing fixture execution with
real read-only Shopify/external tool execution. Synthetic fixtures remain valid for
deterministic automated tests.

## Consistency and Transactions

Publishing a prompt revision and changing an active pointer are separate durable
operations. Active pointers/selections use optimistic concurrency/CAS semantics
consistent with existing Studio mutation patterns.

A grant is created from one resolved configuration snapshot. The model and prompt IDs
must be written atomically with the rest of the grant so a conversation cannot be
created with a partially mixed configuration.

## Failure Handling

- Missing mandatory platform model: fail closed as configuration unavailable.
- Missing mandatory platform prompt: fail closed as configuration unavailable.
- Missing shop override: inherit platform value.
- Explicit shop model override referencing an unavailable/disabled model: fail closed;
  do not silently inherit.
- Invalid/missing pinned prompt revision: fail closed.
- Provider failure remains a runtime provider failure and does not cause model
  fallback to another catalogue entry during the same conversation.

## Security

- Model provider credentials remain server-side secrets.
- Prompt/model selection APIs remain authenticated and authorised.
- Shop overrides are tenant-scoped durable configuration.
- Merchant-facing access later must enforce exact shop ownership and must never permit
  editing platform defaults.
- Configurable prompt text cannot override runner-enforced authorisation, evidence,
  tool or response-contract checks.

## Rollout / Migration

ARCH-021 is classified as **PRE-PRODUCTION / BREAKING ROLLOUT** for this capability.
The Commerce Studio/agent configuration is still under active development and no
production customer compatibility requirement has been established for the
capability-level prompt contract.

Later tasks may therefore remove `CommerceCapabilityRevision.promptTemplate` and
capability `promptName` directly rather than carrying permanent compatibility
adapters. Implementation sequencing must nevertheless keep each intermediate branch
buildable and testable.

Existing fixture infrastructure remains test-only infrastructure and is not removed
merely because the human-facing preview becomes live.

## Phase Plan

### Phase 0 — architecture contract

This document.

Exit criteria:

- prompt/model ownership and fallback are agreed;
- feature/release boundaries are explicit;
- conversation/preview snapshot semantics are explicit;
- platform vs shop authoring responsibilities are explicit;
- later repository tasks can be written without relying on ARCH-020's per-feature
  prompt or hard-coded preview/Background model assumptions.

### Phase 1 — real Studio service wiring and shop execution context

Replace fixture-backed production Studio composition and establish the selected-shop
execution context. Phase 1 is deliberately Commerce-only: it reuses accepted ARCH-020
connection, credential, Studio, shop-inspection, code-response and preview producers and
introduces no new Database/Shared/Background contract.

Phase 1 establishes these invariants:

1. `/connections` and `/connections/[id]` use the real connection lifecycle and
   credential services; fixture ports remain test-only. They also consume the existing
   ARCH-020 U06 `returnTo` handoff as validated internal Studio navigation context, while
   preserving the independent U15 `search`/`cursor`/`enabled` return state.
2. Studio has one explicit selected-shop context identified by `shopId` URL/navigation
   state and resolved server-side from the persisted Commerce shop.
3. The selected-shop context reports offline Shopify-session availability without ever
   exposing the access token. Absence of an offline session is explicit; the Studio does
   not silently select another shop.
4. U06 external Tool authoring lists/binds real persisted immutable connection revisions.
   Synthetic response samples remain temporary deterministic authoring/test inputs until
   Phase 4; they are no longer the source of production connection metadata.
5. The accepted bounded JavaScript response panel is actually installed in production
   Tool authoring. Its Phase 1 sample execution remains synthetic/server-side; live
   provider execution remains Phase 4.
6. Phase 1 performs no model/prompt persistence, no feature-prompt migration and no
   Background behaviour change.

The platform-admin selected-shop representation for Phase 1 is:

```text
/tools?...&shopId=<Commerce Shop.id>
/connections?...&shopId=<Commerce Shop.id>
/preview?...&shopId=<Commerce Shop.id>
...
```

The URL carries only the shop id. Domain/label/plan/offline-session availability are
resolved from the server. Selection is navigation context, not durable business state. A
later merchant-facing Studio may derive the shop from merchant authentication while
reusing the same server-validated downstream shop context.

Phase 1 tasks:

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-021-COMMERCE-001 | moda_commerce | Complete | ARCH-020-COMMERCE-020, ARCH-020-COMMERCE-024, ARCH-020-COMMERCE-028 |
| ARCH-021-COMMERCE-002 | moda_commerce | Complete | ARCH-021-COMMERCE-001, ARCH-020-COMMERCE-022 |
| ARCH-021-COMMERCE-003 | moda_commerce | Complete | ARCH-020-COMMERCE-013, ARCH-020-COMMERCE-018 |
| ARCH-021-COMMERCE-004 | moda_commerce | Complete | ARCH-021-COMMERCE-003 |
| ARCH-021-COMMERCE-005 | moda_commerce | Complete | ARCH-021-COMMERCE-001, ARCH-021-COMMERCE-004, ARCH-020-COMMERCE-023 |
| ARCH-021-COMMERCE-006 | moda_commerce | Complete | ARCH-021-COMMERCE-005, ARCH-020-COMMERCE-026, ARCH-020-COMMERCE-027, ARCH-020-COMMERCE-031 |

Current executable frontier:

```text
None — Phase 1 implementation set is architect-accepted Complete.
```

COMMERCE-001 through COMMERCE-006 are Complete. Attempt 4 closes the final U06
saved-vs-unsaved/publication-integrity gap by preventing JavaScript saves and enclosing
full-draft saves from bypassing invalid visible execution-definition JSON buffers. The
Phase 1 exit criteria below are satisfied. Phase 2 is now materialised as the bounded task set defined below; `ARCH-021-DATABASE-001` is the initial executable frontier.

Phase 1 exit criteria:

- production Connections routes contain no fixture-port composition;
- production U06 connection selection uses persisted connection revisions;
- production JavaScript response authoring is composed instead of showing the
  unavailable placeholder;
- selected shop is explicit, server-validated and preserved across Studio navigation;
- offline Shopify-session availability is known without exposing the token;
- no live provider call has been introduced prematurely;
- deterministic fixtures remain available for automated tests;
- all six Phase 1 tasks are architect-accepted Complete.

### Phase 2 — model catalogue and platform/shop agent configuration

Phase 2 persists and authors CommerceAgent model/prompt configuration without yet changing
preview, manifest, grant, Shared runner or Background execution. It also introduces a
category-organised application-wide prompt-template library as copy-on-use authoring input.

Phase 2 invariants:

1. Model catalogue identity is platform-owned and contains no provider credentials.
2. Platform model default and shop model override are environment-scoped and independently
   mutable from prompt configuration.
3. There is one platform behavioural-prompt lineage and at most one lineage per shop.
4. Published prompt revisions are immutable; active pointers are environment-scoped.
5. Prompt-template categories are data-driven platform records, not enums. One category may
   contain multiple templates and every template belongs to exactly one category.
6. Platform admins may maintain reusable application-wide prompt templates with immutable
   published revisions. `Use template` copies text into a prompt draft and records provenance;
   category/template changes never mutate the copied prompt.
7. Effective model and prompt are resolved independently as shop override -> platform
   default and expose their source as `SHOP` or `PLATFORM`.
8. A missing override inherits. A broken explicit override fails closed and does not silently
   inherit.
9. Phase 2 introduces a dedicated Agent Configuration domain screen/module. New model/prompt/
   category/template editor state must not be accumulated inside `StudioWorkspace`; unrelated
   Studio domains are not rewritten merely for file-size reduction.
10. Phase 2 does not remove the legacy ARCH-020 capability prompt yet because the current
    preview/runtime still consumes it. Runtime migration occurs in later phases.
11. No Phase 2 task performs OpenAI/Groq execution or live Shopify/external tool execution.
12. No Shared/Background contract is published in Phase 2; the exact frozen cross-service
    grant/manifest shape is deferred until runtime integration.

Phase 2 tasks:

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-021-DATABASE-001 | moda_database | Ready | ARCH-020-DATABASE-001 |
| ARCH-021-COMMERCE-007 | moda_commerce | Pending | ARCH-021-DATABASE-001, ARCH-020-COMMERCE-002 |
| ARCH-021-COMMERCE-008 | moda_commerce | Pending | ARCH-021-DATABASE-001, ARCH-020-COMMERCE-002 |
| ARCH-021-COMMERCE-009 | moda_commerce | Pending | ARCH-021-DATABASE-001, ARCH-021-COMMERCE-008, ARCH-020-COMMERCE-002 |
| ARCH-021-COMMERCE-010 | moda_commerce | Pending | ARCH-021-COMMERCE-007, ARCH-021-COMMERCE-009 |
| ARCH-021-COMMERCE-011 | moda_commerce | Pending | ARCH-021-COMMERCE-006, ARCH-021-COMMERCE-007, ARCH-021-COMMERCE-008, ARCH-021-COMMERCE-009, ARCH-021-COMMERCE-010 |
| ARCH-021-COMMERCE-012 | moda_commerce | Pending | ARCH-021-COMMERCE-004, ARCH-021-COMMERCE-010, ARCH-021-COMMERCE-011 |

The initial Phase 2 execution frontier is one cohesive Database task:

```text
ARCH-021-DATABASE-001   complete Phase 2 CommerceAgent configuration schema
```

It introduces model catalogue/selections, template categories/templates/revisions, prompt
lineages/revisions and active prompt pointers in one coherent migration. After architect
acceptance, COMMERCE-007, COMMERCE-008 and COMMERCE-009 can proceed against the same accepted
schema. Phase 1 is already architect-accepted Complete, so the remaining gates are only the
explicit Phase 2 dependencies above.

Phase 2 exit criteria:

- durable model catalogue exists with no provider credentials;
- environment-scoped platform/shop model selections exist with independent CAS;
- data-driven prompt-template categories/classifications exist and each can contain multiple
  reusable templates;
- reusable application-wide prompt templates and immutable revisions exist;
- one platform and at most one per-shop prompt lineage exist with immutable published
  revisions and optional copy-on-use template provenance;
- environment-scoped platform/shop prompt pointers exist with independent CAS;
- Commerce resolves effective model/prompt independently and reports source;
- explicit broken overrides fail closed;
- production Studio exposes platform and selected-shop Agent Configuration backed by real
  services, including category-organised template browsing and template-based prompt drafts;
- Agent Configuration domain state/actions live outside `StudioWorkspace`, while unrelated
  Studio domains are not opportunistically refactored;
- legacy capability prompt/runtime behaviour remains untouched;
- no live provider/model/tool call is introduced;
- all Phase 2 tasks are architect-accepted Complete.

### Phase 3 — complete tool authoring

Finish real Shopify/external execution definitions and direct/visual/JavaScript
request/response authoring.

### Phase 4 — live single-tool testing

Execute real read-only Shopify/external calls for the selected shop.

### Phase 5 — feature/tool agent composition

Compose feature configuration and exact tool revisions without feature-owned prompts.

### Phase 6 — production-equivalent multi-turn Studio preview

Use the selected shop's frozen effective model/prompt plus real tools and retained
preview conversation history.

### Phase 7 — Background parity

Make production grants pin the effective model/prompt and make Background execute the
same configuration tested in Studio.

### Phase 8 — merchant-scoped Studio access

Allow authorised merchants to manage their own shop-scoped configuration, beginning
with shop prompts, without access to platform defaults.

### Phase 9 — integrated validation and legacy preview cutover

Prove the complete live authoring-to-production flow and remove obsolete human-facing
fixture/per-capability-prompt behaviour while retaining deterministic test fixtures.

## Decisions / Tasks

Phase 1 is materialised as six Commerce tasks under `docs/decisions/commerce/ARCH-021/`.
Phase 2 is materialised across:

```text
docs/decisions/database/ARCH-021/
docs/decisions/commerce/ARCH-021/
```

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-021-COMMERCE-001 | moda_commerce | Complete | ARCH-020-COMMERCE-020, ARCH-020-COMMERCE-024, ARCH-020-COMMERCE-028 |
| ARCH-021-COMMERCE-002 | moda_commerce | Complete | ARCH-021-COMMERCE-001, ARCH-020-COMMERCE-022 |
| ARCH-021-COMMERCE-003 | moda_commerce | Complete | ARCH-020-COMMERCE-013, ARCH-020-COMMERCE-018 |
| ARCH-021-COMMERCE-004 | moda_commerce | Complete | ARCH-021-COMMERCE-003 |
| ARCH-021-COMMERCE-005 | moda_commerce | Complete | ARCH-021-COMMERCE-001, ARCH-021-COMMERCE-004, ARCH-020-COMMERCE-023 |
| ARCH-021-COMMERCE-006 | moda_commerce | Complete | ARCH-021-COMMERCE-005, ARCH-020-COMMERCE-026, ARCH-020-COMMERCE-027, ARCH-020-COMMERCE-031 |
| ARCH-021-DATABASE-001 | moda_database | Ready | ARCH-020-DATABASE-001 |
| ARCH-021-COMMERCE-007 | moda_commerce | Pending | ARCH-021-DATABASE-001, ARCH-020-COMMERCE-002 |
| ARCH-021-COMMERCE-008 | moda_commerce | Pending | ARCH-021-DATABASE-001, ARCH-020-COMMERCE-002 |
| ARCH-021-COMMERCE-009 | moda_commerce | Pending | ARCH-021-DATABASE-001, ARCH-021-COMMERCE-008, ARCH-020-COMMERCE-002 |
| ARCH-021-COMMERCE-010 | moda_commerce | Pending | ARCH-021-COMMERCE-007, ARCH-021-COMMERCE-009 |
| ARCH-021-COMMERCE-011 | moda_commerce | Pending | ARCH-021-COMMERCE-006, ARCH-021-COMMERCE-007, ARCH-021-COMMERCE-008, ARCH-021-COMMERCE-009, ARCH-021-COMMERCE-010 |
| ARCH-021-COMMERCE-012 | moda_commerce | Pending | ARCH-021-COMMERCE-004, ARCH-021-COMMERCE-010, ARCH-021-COMMERCE-011 |

Later runtime phases are intentionally not decomposed yet. Expected later owners still include:

- `moda_database` for conversation/preview frozen model/prompt fields;
- `moda_shared` for grant/manifest/runner contract changes;
- `moda_commerce` for live Tool tests, MCP resolution and preview;
- `moda_background` for pinned model/prompt consumption;
- `moda_system_test` only after the required implementation dependencies are Complete.

No implementation task may depend on a system-test task.

## Open Questions

The following are deliberately deferred beyond the Phase 0 ownership contract:

- which exact OpenAI/Groq models Moda initially exposes in the catalogue;
- whether merchants may select shop model overrides or only edit prompts;
- whether merchants later receive shop-owned reusable prompt-template libraries;
- catalogue entitlement/tier restrictions;
- retention period for old prompt revisions;
- whether preview conversation state remains Redis TTL state or gains durable preview
  tables when merchant access is introduced.

None of these changes the core rule: one effective model and one effective
configurable behavioural prompt are resolved per shop with platform fallback and are
independent of features.

## Change History

### 2026-09-23 — Phase 2 task set defined

- Combined all Phase 2 Database schema work into one cohesive `ARCH-021-DATABASE-001` migration/task covering model catalogue/selections, prompt-template categories/templates/revisions, prompt lineages/revisions and active pointers.
- Added a data-driven prompt-template category/classification taxonomy: every template belongs to one category and a category such as `Clothing & Fashion` may contain multiple templates without code/schema enum changes.
- Kept prompt templates as copy-on-use authoring assets independent of models/features and retained immutable template/prompt revision semantics.
- Defined Commerce services for model lifecycle, category/template lifecycle, prompt lifecycle and effective configuration resolution.
- Defined separate platform and selected-shop Agent Configuration UI tasks and made incremental `StudioWorkspace` decomposition an explicit Phase 2 requirement: Agent Configuration gets its own domain module while unrelated Studio domains remain untouched.
- Kept Shared grant/manifest/runner changes, Background execution and all live provider/tool execution out of Phase 2.
- Phase 1 is already architect-accepted Complete; `ARCH-021-DATABASE-001` is the sole initial Phase 2 Ready frontier.

### 2026-09-23 — COMMERCE-006 Attempt 4 accepted; Phase 1 complete

- Accepted implementation `39824714febb6198645a5f4e151f8acc33bb8c70` with submitted parent report `ad00499156b587bf10513033e719b5a4f5030113`.
- Confirmed the JavaScript save composition now preflights both visible `ExternalHttpEditor` execution-definition buffers (`advanced` and `schemaText`) before persistence, so invalid buffered JSON cannot be bypassed or falsely marked clean.
- Confirmed the enclosing full-draft save also respects execution-definition validity, while the previously accepted CAS/edit-version, complete top-level candidate persistence and JavaScript validation/publication handoff remain intact.
- Accepted the submitted functionality-focused evidence: 13 U06 tests, 105 focused response/preview tests, targeted ESLint and `git diff --check` passed; the documented repository typecheck baseline remains non-blocking.
- Marked COMMERCE-006 Complete. COMMERCE-001 through COMMERCE-006 now satisfy the Phase 1 exit criteria; Phase 1 is complete and Phase 2 remains intentionally unmaterialised.

### 2026-09-23 — COMMERCE-006 Attempt 3 changes requested

- Confirmed implementation `5991dde` / parent report `2b37c7b` correctly persists the current top-level Input JSON Schema and Response template with JavaScript saves, preserves the authoritative edit-version sequence, and retains the accepted JavaScript validation/publication handoff.
- Confirmed invalid top-level sibling JSON performs no write and retains the shared navigation/publication guard; submitted focused validation reports 12 U06 tests, 104 focused composition/preview tests and 76 response/preview integration tests passing.
- Identified one remaining functional saved-vs-unsaved gap in the same U06 boundary: invalid `ExternalHttpEditor` Advanced response-processing or Response-shape JSON is buffered locally outside `definition`, so JavaScript Save can persist the previous execution value and clear the shared dirty guard while the invalid value remains visibly displayed.
- Returned COMMERCE-006 to Ready at `attempt: 3`; Phase 1 remains In Progress and Phase 2 remains unmaterialised.

### 2026-09-23 — COMMERCE-006 Attempt 2 changes requested

- Confirmed implementation `14c4c3e` / parent report `f031e16` resolves the Attempt 1 CAS continuity defect and connects completed current JavaScript sample proof to the canonical U06 SUPER_ADMIN publication gate.
- Confirmed the accepted server-only QuickJS/external-preview, cancellation/reconciliation and no-provider-network/credential boundaries remain intact; submitted functionality-focused suites report 103/103 passing.
- Identified one remaining functional saved-vs-unsaved identity defect: the JavaScript panel save unconditionally clears shared U06 dirty state even when independently buffered Input JSON Schema or Response template edits remain unpersisted.
- Returned COMMERCE-006 to Ready at `attempt: 2`; Phase 1 remains In Progress and Phase 2 remains unmaterialised.

### 2026-09-23 — COMMERCE-006 Attempt 1 changes requested

- Accepted in substance the production JavaScript response-panel composition, server-only QuickJS validation/execution boundary, synthetic external-preview wiring and preserved visual/JavaScript discard guard at implementation `8d5ee07` / parent report `d3acb90`.
- Identified a functional CAS continuity defect: JavaScript save, full Tool save and publication continue to use the original selected revision edit version after a successful mutation increments the authoritative version.
- Identified a functional publication-handoff gap: JavaScript validation/sample success remains internal to the code panel and cannot make the canonical U06 publication gate current.
- Returned COMMERCE-006 to Ready at `attempt: 1`; Phase 1 remains In Progress and Phase 2 remains unmaterialised.

### 2026-09-23 — COMMERCE-005 Attempt 2 accepted

- Accepted production U06 persisted connection/revision authoring at implementation `9033069` with parent report `1131be5` after the merged U15/U16 route correction.
- Confirmed Tool -> Connections -> Tool navigation preserves the exact Tool revision, selected `shopId`, validated internal `returnTo`, and independent Connections list/detail state with one production route client.
- Confirmed synthetic sample processing remains test/authoring-only and no live provider call or credential decryption was introduced.
- Marked COMMERCE-005 Complete and promoted COMMERCE-006 to Ready; COMMERCE-006 is the sole remaining Phase 1 implementation task.

### 2026-09-23 — COMMERCE-002 Attempt 2 accepted

- Accepted the production U15/U16 `ConnectionPort` composition and completed the existing ARCH-020 U06 `returnTo` consumer handoff.
- Confirmed validated internal return destinations propagate through U15/U16 while preserving independent `search`/`cursor`/`enabled` list state and Studio navigation blockers.
- Marked COMMERCE-002 Complete. COMMERCE-004 is the remaining Ready Phase 1 frontier; COMMERCE-005 stays Pending on COMMERCE-004.
- Recorded a non-blocking route-prop type-annotation cleanup for `returnTo`; no additional implementation attempt is required for the functionality-focused acceptance.

### 2026-09-23 — COMMERCE-002 Attempt 1 changes requested

- Confirmed the production U15/U16 wrapper now uses the accepted COMMERCE-001 server-backed `ConnectionPort` and no longer composes fixtures.
- Identified an ARCH-020 navigation-contract gap: COMMERCE-023 emits `returnTo` from U06, but U15/U16 never implemented the consumer required for XN02 return-to-source behaviour.
- Corrected COMMERCE-002 to own validated internal `returnTo` parsing, U15/U16 propagation, guarded return-to-origin navigation and focused regression proof.
- Returned COMMERCE-002 to Ready at `attempt: 1`; COMMERCE-004 remains independently Ready.
### 2026-09-23 — COMMERCE-004 accepted

- Accepted the Studio-wide selected-shop URL/navigation context at implementation `b67177d` after Attempt 2.
- Confirmed `/connections/[id]` restores the server-validated selected shop on refresh/direct entry while retaining Connections list state.
- Confirmed an exact valid shop outside the bounded discovery list remains represented in the selector by durable-id merge/deduplication.
- Promoted ARCH-021-COMMERCE-005 to Ready.

### 2026-09-23 — COMMERCE-001 accepted

- Accepted the production Connections server boundary at implementation `03ffcd0` after Attempt 2.
- Confirmed lifecycle `enabled` filtering is applied in the database query before cursor pagination and preserves adapter forwarding semantics.
- Confirmed production U15/U16 route composition remains fixture-backed until COMMERCE-002 installs the accepted production port.
- Promoted ARCH-021-COMMERCE-002 to Ready.
### 2026-09-23 — COMMERCE-003 accepted

- Accepted the server-validated Studio shop execution context at implementation `ce8c8bc`.
- Confirmed persisted shop identity/domain/plan resolution and offline-session availability without Session/access-token disclosure.
- Promoted ARCH-021-COMMERCE-004 to Ready.

### 2026-09-23 — Phase 1 task set defined

- Accepted the Phase 0 ownership contract and moved ARCH-021 to Agreed.
- Defined six Commerce-only Phase 1 tasks.
- Made production Connections wiring and server-validated shop context independent
  Ready workstreams.
- Chose explicit `shopId` URL/navigation state for platform-admin Studio selection;
  selection is not durable business state.
- Kept synthetic response samples temporarily for deterministic authoring/tests while
  requiring real connection metadata and production JavaScript panel composition.
- Kept live provider execution, model/prompt persistence and Background changes outside
  Phase 1.

### 2026-09-23 — Phase 0 created

- Established platform/shop ownership for model and prompt.
- Removed model/prompt ownership from features and releases.
- Defined independent shop-override/platform-fallback semantics.
- Defined one configurable runtime prompt rather than one prompt per feature.
- Defined conversation/preview freezing of resolved immutable identities.
- Defined platform-admin authoring of both application-wide and shop-specific prompts
  and the future merchant shop-prompt boundary.
