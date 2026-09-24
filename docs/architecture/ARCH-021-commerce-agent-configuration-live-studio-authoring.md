---
id: ARCH-021
title: CommerceAgent configuration and live Studio authoring
status: agreed
coordinator: moda_architect
created: 2026-09-23
updated: 2026-09-24
---

# ARCH-021: CommerceAgent configuration and live Studio authoring

## Status

Agreed — Phase 1 and Phase 2 are architect-accepted Complete. Phase 3 contract task `ARCH-021-COMMERCE-016` is Complete, but remaining Phase 3 tasks are paused/Blocked while the 2026-09-24 simplification checkpoint reduces Agent Configuration, Studio composition and private-MCP complexity.

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

may contain multiple prompt templates. New categories, category display-name/metadata edits and
category disablement must not require an application/schema release. Category identity/slug is stable;
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

Phase 2 Prisma names are fixed by `ARCH-021-DATABASE-001`; later tasks must consume these exact durable models rather than inventing alternate persistence concepts:

```text
CommerceModelCatalogueEntry
CommercePlatformModelSelection
CommerceShopModelSelection
CommercePromptTemplateCategory
CommercePromptTemplate
CommercePromptTemplateRevision
CommerceAgentPrompt
CommerceAgentPromptRevision
CommercePlatformPromptPointer
CommerceShopPromptPointer
```

The exact fields, indexes, FKs, audit extensions and migration guards are authoritative in `docs/decisions/database/ARCH-021/DATABASE-001-persist-agent-configuration-schema.md`. The architecture requires the following durable semantics.

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

The shop override is removable, returning that shop to inheritance. A persisted shop model override carries an immutable row `generationId` plus `editVersion`; replace/clear CAS uses both so a clear/recreate cycle cannot make a stale request valid again merely because a new row restarts its numeric edit version.

### Prompt-template categories and immutable template revisions

Platform administrators may maintain data-driven application-wide prompt-template categories.
Each category has a stable identity/slug plus display metadata and can contain multiple
template identities. Every template belongs to exactly one category. Categories may be
enabled/disabled without deleting historical templates/revisions.

Within a category, platform administrators may maintain reusable template identities with
versioned draft/published revisions. DRAFT revisions may persist empty prompt text so authors can
start from a blank editor; publication requires non-blank content. Published template revision
content is immutable. Its `contentHash` is SHA-256 of the exact UTF-8 bytes of persisted
`promptText`, with no trimming or line-ending normalisation for hashing. Templates may be
enabled/disabled for new selection without deleting historical revisions.

When a prompt draft is created from a template, the exact template revision content is
copied and the resulting prompt revision may retain `sourceTemplateRevisionId` as audit
provenance. There is no live inheritance/linkage after the copy.

### Prompt lineage and immutable revisions

There is one logical CommerceAgent behavioural-prompt lineage for platform scope and
one optional lineage per shop. Each lineage supports drafts/history and immutable
published revisions. DRAFT prompt revisions may persist empty prompt text; publication
requires non-blank content. Published `contentHash` is SHA-256 of the exact UTF-8 bytes of
persisted `promptText`, with no trimming or line-ending normalisation for hashing.

An environment-scoped active pointer selects:

```text
platform active prompt revision    # mandatory
shop active prompt revision        # optional per shop
```

A shop pointer is removable, returning that shop to platform inheritance. A persisted shop prompt pointer carries an immutable row `generationId` plus `editVersion`; replace/clear CAS compares both so `present -> absent -> present` cannot create an ABA stale-write match.

### Phase 2 command replay and CAS

Privileged model/template/prompt mutations reuse the accepted immutable `CommerceAuditEvent` command-receipt convention rather than creating another operation table:

```text
CommerceAuditEvent.id = operationId
metadata.payloadHash  = canonical actor/action/input hash
metadata.result       = replayable successful result
```

Reusing an operation id with the same actor/action/payload returns the recorded result without reapplying the mutation. Reusing it with different input is a conflicting replay. An exception whose durable outcome is unknown is surfaced through the existing Studio unknown-outcome reconciliation flow.

`editVersion` alone is sufficient only for identities that cannot disappear and be recreated through the supported lifecycle. Shop model selections and shop prompt pointers deliberately represent inheritance by row absence, so existing-row replace/clear operations compare both immutable `generationId` and `editVersion`.

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
8. Effective model and prompt resolution observes one coherent database read snapshot so a
   resolver cannot return a model/prompt combination that never existed together; multi-statement
   resolution therefore uses `REPEATABLE READ` or stronger snapshot semantics rather than ordinary
   `READ COMMITTED`, unless one statement obtains the complete result.
9. A missing override inherits. A broken explicit override fails closed and does not silently
   inherit.
10. Shop model/prompt override rows use immutable `generationId` plus `editVersion` for existing-row
    replace/clear CAS so clear/recreate cannot ABA-match stale mutations.
11. Privileged Phase 2 commands reuse `CommerceAuditEvent` as durable operation receipt with
    `operationId`, canonical payload hash and replayable result; conflicting reuse and unknown
    outcomes follow accepted Studio semantics.
12. DRAFT template/prompt revisions may persist empty content; publication requires non-blank
    content and hashes the exact persisted UTF-8 prompt bytes without trimming/newline normalisation.
13. Phase 2 introduces a dedicated Agent Configuration domain screen/module. New model/prompt/
    category/template editor state must not be accumulated inside `StudioWorkspace`; unrelated
    Studio domains are not rewritten merely for file-size reduction.
14. Phase 2 does not remove the legacy ARCH-020 capability prompt yet because the current
    preview/runtime still consumes it. Runtime migration occurs in later phases.
15. No Phase 2 task performs OpenAI/Groq execution or live Shopify/external tool execution.
16. No Shared/Background contract is published in Phase 2; the exact frozen cross-service
    grant/manifest shape is deferred until runtime integration.

Phase 2 tasks:

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-021-DATABASE-001 | moda_database | Complete | ARCH-020-DATABASE-001 |
| ARCH-021-COMMERCE-007 | moda_commerce | Complete | ARCH-021-DATABASE-001, ARCH-020-COMMERCE-002 |
| ARCH-021-COMMERCE-008 | moda_commerce | Complete | ARCH-021-DATABASE-001, ARCH-020-COMMERCE-002 |
| ARCH-021-COMMERCE-009 | moda_commerce | Complete | ARCH-021-DATABASE-001, ARCH-021-COMMERCE-008, ARCH-020-COMMERCE-002 |
| ARCH-021-COMMERCE-010 | moda_commerce | Complete | ARCH-021-COMMERCE-003, ARCH-021-COMMERCE-007, ARCH-021-COMMERCE-009 |
| ARCH-021-COMMERCE-011 | moda_commerce | Complete | ARCH-021-COMMERCE-006, ARCH-021-COMMERCE-007 |
| ARCH-021-COMMERCE-012 | moda_commerce | Complete | ARCH-021-COMMERCE-004, ARCH-021-COMMERCE-007, ARCH-021-COMMERCE-008, ARCH-021-COMMERCE-009, ARCH-021-COMMERCE-010, ARCH-021-COMMERCE-011 |
| ARCH-021-COMMERCE-013 | moda_commerce | Complete | ARCH-021-COMMERCE-008, ARCH-021-COMMERCE-011, ARCH-021-COMMERCE-015 |
| ARCH-021-COMMERCE-014 | moda_commerce | Complete | ARCH-021-COMMERCE-008, ARCH-021-COMMERCE-009, ARCH-021-COMMERCE-011, ARCH-021-COMMERCE-015 |
| ARCH-021-COMMERCE-015 | moda_commerce | Complete | ARCH-021-COMMERCE-008 |

Phase 2 is architect-accepted Complete. The individual task YAML is authoritative: DATABASE-001 and COMMERCE-007 through COMMERCE-015 are Complete.

```text
Phase 2 frontier: none — implementation set complete
```

Phase 2 exit criteria:

- durable model catalogue exists with no provider credentials;
- environment-scoped platform/shop model selections exist with independent CAS and generation-aware shop-override ABA protection;
- data-driven prompt-template categories/classifications exist and each can contain multiple
  reusable templates;
- reusable application-wide prompt templates and immutable revisions exist;
- one platform and at most one per-shop prompt lineage exist with immutable published
  revisions and optional copy-on-use template provenance;
- environment-scoped platform/shop prompt pointers exist with independent CAS and generation-aware shop-override ABA protection;
- Commerce resolves effective model/prompt independently, reports source and observes one coherent database read snapshot;
- explicit broken overrides fail closed;
- production Studio exposes platform model configuration, category-organised template browsing,
  platform prompt authoring and selected-shop Agent Configuration as independently reviewable
  surfaces backed by real services, including template-based prompt drafts;
- Agent Configuration domain state/actions live outside `StudioWorkspace`, while unrelated
  Studio domains are not opportunistically refactored;
- legacy capability prompt/runtime behaviour remains untouched;
- no live provider/model/tool call is introduced;
- all Phase 2 tasks are architect-accepted Complete.

### Phase 3 — complete tool authoring

Phase 3 completes the immutable Tool authoring contract without making a real Shopify or external provider request. It is a pre-production breaking contract change: there is one canonical `EXTERNAL_HTTP` shape, not an `EXTERNAL_HTTP v2` compatibility layer.

Phase 3 invariants:

1. The persisted Tool `inputSchema` remains the contract presented to the CommerceAgent; the CommerceAgent generates actual argument values per invocation. Phase 3 does not persist invocation values.
2. External HTTP remains generic read-only GET in Phase 3. A Tool pins one immutable connection revision; origin/auth credentials remain server-owned connection state and never enter request JavaScript or browser state.
3. EXTERNAL_HTTP request construction is exactly one of:
   - `DECLARATIVE`: relative path + bounded query mappings + static safe headers;
   - `JAVASCRIPT`: bounded QuickJS `buildRequest({ args })` returning only relative path/query/safe headers.
4. Request JavaScript describes a request; it never calls `fetch`, chooses an origin/method, accesses credentials, reads environment/process/filesystem or performs I/O.
5. EXTERNAL_HTTP response processing is exactly DIRECT, Visual (OBJECT/LIST), or JavaScript `transform(response)`. DIRECT validates selected JSON directly against `resultSchema`.
6. Shopify authoring uses `SHOPIFY_ADMIN_GRAPHQL` pinned to Admin API `2026-07`, not a new Storefront authoring flow. The definition contains the query document, operation name, input-variable mappings, result path/schema and pinned schema hash; it contains no shop/session/token.
7. Authored Shopify Admin documents are query-only. Mutations/subscriptions are rejected before publication/live testing.
8. Commerce validates Shopify Admin drafts locally against a committed schema derived from pinned `@shopify/dev-mcp@1.15.4`. Shopify Dev MCP / AI Toolkit `validate_graphql_codeblocks` is development conformance evidence only; normal Studio validation does not send merchant-authored GraphQL to the toolkit.
9. Existing `SHOPIFY_STOREFRONT_QUERY` runtime support remains transitional while Phase 4 Admin execution is absent, but the Phase 3 Studio does not offer Storefront for new Tool creation.
10. New Phase 3 definitions are authorable/structurally valid but cannot publish until Phase 4 records a successful real live Tool test for the exact saved revision. Synthetic fixtures remain automated-test assets and do not satisfy that publication gate.
11. Phase 3 continues incremental Studio decomposition: the Tools domain is extracted from `StudioWorkspace`; unrelated Studio surfaces are not rewritten.
12. Phase 3 introduces no live provider/model call, no Background change, no database migration and no conversation tool-call-history persistence.

Phase 3 tasks:

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-021-COMMERCE-016 | moda_commerce | Complete | ARCH-020-COMMERCE-021, ARCH-020-COMMERCE-030 |
| ARCH-021-COMMERCE-017 | moda_commerce | Blocked | ARCH-021-COMMERCE-016, ARCH-020-COMMERCE-029, ARCH-020-COMMERCE-026 |
| ARCH-021-COMMERCE-018 | moda_commerce | Blocked | ARCH-021-COMMERCE-016, ARCH-020-COMMERCE-011 |
| ARCH-021-COMMERCE-019 | moda_commerce | Blocked | ARCH-021-COMMERCE-016, ARCH-020-COMMERCE-030 |
| ARCH-021-COMMERCE-020 | moda_commerce | Blocked | ARCH-021-COMMERCE-016, ARCH-021-COMMERCE-005, 006 |
| ARCH-021-COMMERCE-021 | moda_commerce | Blocked | ARCH-021-COMMERCE-019, 020, 023, ARCH-021-COMMERCE-005, 006 |
| ARCH-021-COMMERCE-022 | moda_commerce | Blocked | ARCH-021-COMMERCE-019, 020, 024 |
| ARCH-021-COMMERCE-023 | moda_commerce | Blocked | ARCH-021-COMMERCE-016, 017, 019, ARCH-020-COMMERCE-030 |
| ARCH-021-COMMERCE-024 | moda_commerce | Blocked | ARCH-021-COMMERCE-016, 018, 019 |

Dependency graph:

```text
COMMERCE-016
    |
    +--> COMMERCE-017 ----+----------------> COMMERCE-023 ----+--> COMMERCE-021
    |                     |                                   |
    +--> COMMERCE-018 ----|----------------> COMMERCE-024 ----+--> COMMERCE-022
    |                     |                                   |
    +--> COMMERCE-019 ----+---- common validation/publication +
    |
    +--> COMMERCE-020 -------- Tool UI extraction ------------+

COMMERCE-016 is architect-accepted Complete. COMMERCE-017 through COMMERCE-024 are paused/Blocked by the pre-Phase-3 simplification checkpoint and must not be claimed. `moda_architect` will reconcile/reissue the Phase-3 frontier after the simplification implementation is architect-accepted.
```

Phase 3 exit criteria:

- Commerce owns the accepted request/response/Admin Tool-definition contracts under `src/commerce/tool-definition/`; Shared remains unchanged at 0.14.2;
- Commerce is fully migrated to the canonical EXTERNAL_HTTP request shape with no compatibility parser;
- `buildRequest({args})` uses the same bounded QuickJS runtime and can produce only a safe request descriptor;
- Admin 2026-07 GraphQL drafts are validated locally/query-only with the accepted bounded GraphQL structure (no fragments/directives, <=100 selections, depth <=8, estimated cost <=500, literal `first` <=20) and toolkit conformance evidence;
- common publication policy plus independent External HTTP and Shopify Admin server-side authoring validators are authoritative and perform zero provider I/O;
- new Phase 3 definitions fail publication with `LIVE_TEST_REQUIRED` until Phase 4;
- production Studio authors External HTTP declarative/JS request + DIRECT/Visual/JS response definitions;
- production Studio authors Shopify Admin GraphQL definitions and no longer offers Storefront for new Tool creation;
- Tool-specific state/actions are outside `StudioWorkspace`;
- all Phase 3 tasks are architect-accepted Complete.

### Pre-Phase-3 simplification checkpoint — 2026-09-24

Before expanding Tool authoring further, ARCH-021 reduces implementation complexity while preserving product invariants.

Keep:

- `CommerceModelCatalogueEntry`;
- immutable published `CommerceAgentPromptRevision`;
- first-class `CommercePromptTemplateCategory`;
- immutable Tool/capability/release/grant boundaries;
- server-owned Shopify/external credentials and tenant authorization;
- merchant Studio authorization as a shop-scoped authorization layer on the normal Auth.js identity; initial access provisioning is manual;
- UI reconciliation for genuinely unconfirmed client outcomes.

Collapse/remove:

- separate platform/shop model-selection and prompt-pointer tables into one `CommerceAgentConfiguration`;
- `generationId` ABA machinery by retaining shop configuration rows and clearing nullable override fields;
- template revision persistence into current template `promptText` plus copy-on-use Agent Prompt revisions;
- generic payload-hash/stored-result command replay for ordinary PostgreSQL configuration mutations;
- production Server -> Client function-valued Studio service/port bundles;
- MCP RSA/JWT/key exchange and **all replacement application-layer MCP credentials**. The existing private service link is the MCP caller trust boundary; Commerce continues to authorize shop/turn/grant/release/tool context from PostgreSQL.

Error rule:

```text
known domain/DB error -> explicit typed UI error
lost/untrustworthy client response -> UNCONFIRMED with operationId -> read-only reconcile
reconcile COMMITTED -> reload canonical state
reconcile NOT_COMMITTED -> allow explicit retry with a new operationId
```

Do not catch ordinary failures and silently return success, empty state or generic `unknown`.

Checkpoint tasks:

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-021-DATABASE-002 | moda_database | Complete | DATABASE-001 |
| ARCH-021-COMMERCE-025 | moda_commerce | Ready | DATABASE-002, COMMERCE-007, 009, 010 |
| ARCH-021-COMMERCE-026 | moda_commerce | Ready | DATABASE-002, COMMERCE-008, 015 |
| ARCH-021-COMMERCE-027 | moda_commerce | Ready | DATABASE-002 |
| ARCH-021-COMMERCE-028 | moda_commerce | Pending | COMMERCE-025, 026, 027, 011..014 |
| ARCH-021-COMMERCE-029 | moda_commerce | Pending | COMMERCE-028, COMMERCE-001..006 |
| ARCH-021-COMMERCE-030 | moda_commerce | Complete | ARCH-020-COMMERCE-024 |
| ARCH-021-BACKGROUND-001 | moda_background | Ready | COMMERCE-030 |
| ARCH-021-GATEWAY-001 | moda_gateway | Pending | COMMERCE-030, BACKGROUND-001 |
| ARCH-021-SYSTEM-TEST-001 | moda_system_test | Pending | all checkpoint implementation tasks |

Current checkpoint frontier: `ARCH-021-DATABASE-002` and `ARCH-021-BACKGROUND-001`.

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
| ARCH-021-DATABASE-001 | moda_database | Complete | ARCH-020-DATABASE-001 |
| ARCH-021-COMMERCE-007 | moda_commerce | Complete | ARCH-021-DATABASE-001, ARCH-020-COMMERCE-002 |
| ARCH-021-COMMERCE-008 | moda_commerce | Complete | ARCH-021-DATABASE-001, ARCH-020-COMMERCE-002 |
| ARCH-021-COMMERCE-009 | moda_commerce | Complete | ARCH-021-DATABASE-001, ARCH-021-COMMERCE-008, ARCH-020-COMMERCE-002 |
| ARCH-021-COMMERCE-010 | moda_commerce | Complete | ARCH-021-COMMERCE-003, ARCH-021-COMMERCE-007, ARCH-021-COMMERCE-009 |
| ARCH-021-COMMERCE-011 | moda_commerce | Complete | ARCH-021-COMMERCE-006, ARCH-021-COMMERCE-007 |
| ARCH-021-COMMERCE-012 | moda_commerce | Complete | ARCH-021-COMMERCE-004, ARCH-021-COMMERCE-007, ARCH-021-COMMERCE-008, ARCH-021-COMMERCE-009, ARCH-021-COMMERCE-010, ARCH-021-COMMERCE-011 |
| ARCH-021-COMMERCE-013 | moda_commerce | Complete | ARCH-021-COMMERCE-008, ARCH-021-COMMERCE-011, ARCH-021-COMMERCE-015 |
| ARCH-021-COMMERCE-014 | moda_commerce | Complete | ARCH-021-COMMERCE-008, ARCH-021-COMMERCE-009, ARCH-021-COMMERCE-011, ARCH-021-COMMERCE-015 |
| ARCH-021-COMMERCE-015 | moda_commerce | Complete | ARCH-021-COMMERCE-008 |
| ARCH-021-COMMERCE-016 | moda_commerce | Complete | ARCH-020-COMMERCE-021, ARCH-020-COMMERCE-030 |
| ARCH-021-COMMERCE-017 | moda_commerce | Blocked | ARCH-021-COMMERCE-016, ARCH-020-COMMERCE-029, ARCH-020-COMMERCE-026 |
| ARCH-021-COMMERCE-018 | moda_commerce | Blocked | ARCH-021-COMMERCE-016, ARCH-020-COMMERCE-011 |
| ARCH-021-COMMERCE-019 | moda_commerce | Blocked | ARCH-021-COMMERCE-016, ARCH-020-COMMERCE-030 |
| ARCH-021-COMMERCE-020 | moda_commerce | Blocked | ARCH-021-COMMERCE-016, ARCH-021-COMMERCE-005, ARCH-021-COMMERCE-006 |
| ARCH-021-COMMERCE-021 | moda_commerce | Blocked | ARCH-021-COMMERCE-017, ARCH-021-COMMERCE-019, ARCH-021-COMMERCE-020, ARCH-021-COMMERCE-005, ARCH-021-COMMERCE-006 |
| ARCH-021-COMMERCE-022 | moda_commerce | Blocked | ARCH-021-COMMERCE-018, ARCH-021-COMMERCE-019, ARCH-021-COMMERCE-020, ARCH-020-COMMERCE-011 |

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

### 2026-09-24 — COMMERCE-025 Attempt 3 changes requested

- Reviewed implementation `d1e884c` with parent report `cb0486b3`.
- Confirmed the reduced services now include most Attempt 2 corrections, including active unit suites, shop-correlated shared logging, first-write CAS, retained nullable override rows, real prompt lineage identity and operation-receipt reconciliation.
- Returned COMMERCE-025 to Ready because the effective resolver regressed the mandatory platform-baseline rule, the prompt unit suite remains incomplete, the prompt PostgreSQL test is syntactically invalid, and none of the required npm-based unit/PostgreSQL validation actually executed.
- Attempt 4 must use npm (not pnpm), repair/migrate the task-owned suites, execute both PostgreSQL suites against a disposable DATABASE-002 database, and return to review only after all required validation passes. COMMERCE-028 remains Pending.

### 2026-09-24 — COMMERCE-025 Attempt 2 changes requested

- Reviewed implementation `e5c6ed2` with parent report `edd22c18`.
- Confirmed the reduced DATABASE-002 service implementation now contains most requested semantics: nullable model inheritance reads, deterministic first-write `1 -> 2` CAS creation, real prompt lineage ids, current-template `sourceTemplateId` provenance, parameterized prompt-lineage locking, concurrent operation-receipt reconciliation and the canonical shared logger path.
- Acceptance remains blocked because the required model/prompt/effective suites are still disabled (`21` skipped tests), both PostgreSQL suites still contain dropped Phase-2 fixtures/fields and were not executed, and the database-unavailable event omits already-known shop correlation on shop-scoped failures.
- Returned COMMERCE-025 to Ready at `attempt: 2`; COMMERCE-028 remains Pending.

### 2026-09-24 — COMMERCE-025 Attempt 1 changes requested

- Reviewed implementation `256dbef112ae9f7c7d4301f6603b4ec892972067` with parent report `19e4c3d05ebdd319de2884f4fe4eed4206dfeb5d`.
- Accepted the direction toward direct `CommerceAgentConfiguration` transactions plus read-only audit reconciliation, but identified reduced-contract drift: synthetic generation/template-revision fields remain, nullable cleared overrides cannot be read as inheritance, prompt pointers expose configuration ids as prompt ids, and first configuration writes return `NOT_FOUND` instead of creating the DATABASE-002 row.
- Identified concurrent receipt/draft-allocation gaps: an operation-id unique race can become `INTERNAL_ERROR`, and prompt draft numbering uses unsafe `count + 1` without a per-lineage lock.
- Required Prisma connection/initialization failures to normalize publicly to `DATABASE_UNAVAILABLE` while preserving the original root cause through the canonical `@modainteract/moda-interact-shared/logging` logger using the repository's existing `createLogger` contract; no local logger or secret-bearing fields are permitted.
- Attempt 1 validation is incomplete because the model, prompt and effective suites are disabled with `describe.skip`; Attempt 2 must migrate and activate them plus the reduced PostgreSQL model/prompt suites.
- Returned COMMERCE-025 to Ready at `attempt: 1`; COMMERCE-028 remains Pending.

### 2026-09-24 — DATABASE-002 Attempt 2 accepted

- Accepted implementation `f2629f1` with task report `dde2e33` after the Attempt 1 migration-execution corrections.
- Confirmed migration-local handling of the pre-existing immutable audit and prompt-revision triggers permits deterministic backfill while restoring runtime immutability before migration completion.
- Confirmed the redundant audit actor-admin FK is not recreated and the predecessor FK remains authoritative.
- Accepted executable fail-closed PostgreSQL fresh and seeded-upgrade rehearsals proving exact model/prompt edit-version backfill, template-content/source-template migration, audit operation IDs, prompt-scope and merchant-identity guards, pre/post audit immutability and removal of the five obsolete persistence tables.
- Marked DATABASE-002 Complete and promoted COMMERCE-025, COMMERCE-026 and COMMERCE-027 to Ready. COMMERCE-028 remains Pending on those three Commerce tasks.

### 2026-09-23 — COMMERCE-012 Attempt 3 accepted
### 2026-09-23 - COMMERCE-013 Attempt 5 accepted

- Reviewed implementation `8ebff4ee8e5a8bf21a44be95daf2be75f8475c76` with parent report `174b729ca4a0862c9779e156bb324a14c14944d4` and metadata update `3ac0679561a2efee4dd413bbe5e68b89c692d2e2`.
- Accepted canonical `revisionNumber DESC, id ASC` local revision reconciliation and immediate newest-published revision/id/hash presentation.
- Accepted exact-operation `unknown -> ok` retry reconciliation with the original success reconciler and exact original operation id.
- Accepted the prepared-worktree/synchronization/submodule evidence and focused template UI/production composition validation.
- Marked COMMERCE-013 Complete. COMMERCE-012 remains the sole executable Phase 2 Commerce frontier.

### 2026-09-23 - COMMERCE-014 Attempt 2 accepted

- Marked COMMERCE-012 Complete after direct source review confirmed stale-shop load isolation, dirty prompt mutation protection, durable single-DRAFT resume, publish-success/activation-failure reconciliation and visible effective-resolution error preservation.
- Accepted 11 focused shop UI tests and the 5-file / 27-test combined focused suite plus targeted ESLint, changed-file diagnostics and `git diff --check`.
- Preserved the accepted COMMERCE-007/009 CAS/replay boundaries and server-validated selected-shop contract; COMMERCE-012 has no dependants to promote.
- COMMERCE-013 remains Ready on this branch; its newer separately accepted Attempt 5 state must be preserved when the parallel parent branches are reconciled.

### 2026-09-23 — COMMERCE-012 Attempt 2 changes requested

- Accepted the Attempt 1 corrections for server-validated shop handoff, raw broken-override recovery, durable unactivated shop-lineage discovery, separate lineage/draft operation receipts, returned-revision publication/activation, Composer dirty integration and ADMIN read-only behavior.
- Identified an asynchronous selected-shop isolation race: an older shop load can resolve after a newer selection and repopulate stale model/prompt/draft state under the new shop surface.
- Identified remaining dirty-state independence defects: successful model/prompt controls that reload the surface can silently discard unsaved prompt text, and the UI can create a second DRAFT while one already exists.
- Identified incomplete partial-success recovery: when publication commits but pointer activation loses CAS, the UI keeps the old DRAFT representation instead of reconciling the immutable published revision and current pointer.
- Required preservation of the effective-resolver configuration-error message while raw broken override state remains visible/clearable.
- Returned COMMERCE-012 to Ready at `attempt: 2`; parallel COMMERCE-013/014 coordination state must be preserved from their newer branches during reconciliation.

### 2026-09-23 — COMMERCE-012 Attempt 1 changes requested

- Accepted in substance the dedicated selected-shop Agent Configuration module, independent model control and service-provided model `generationId` + `editVersion` handoff.
- Identified that production composition validates `shopSelection` but still hands the raw query-string `shopId` to the authoring surface; Attempt 2 must consume only the validated selected-shop id.
- Identified fail-closed recovery drift: an effective-resolution failure currently prevents raw model/prompt override state from loading, so a broken explicit override can be hidden and become uncleareable.
- Identified incomplete durable shop prompt authoring: one operation id is reused across lineage+draft commands, unactivated drafts are not discoverable after refresh, shop switches can retain stale lineage/draft state, and the activation button targets the already-active revision instead of the newly published revision.
- Required exact visible-state publication and Studio Composer dirty-navigation protection; ADMIN prompt controls must be genuinely read-only.
- Returned COMMERCE-012 to Ready at `attempt: 1`; COMMERCE-013 and COMMERCE-014 remain independently Ready.

### 2026-09-23 — COMMERCE-010 Attempt 2 accepted

- Accepted mandatory platform-baseline validation before shop overrides, preserving the rule that each environment must have a valid platform model default and platform active prompt even when a shop override exists.
- Accepted independent model/prompt fallback and fail-closed explicit override semantics.
- Confirmed the resolver composes all participating reads in one Prisma `REPEATABLE READ` transaction and the Studio server action short-circuits unavailable selected shops before resolution.
- Reviewed submitted focused validation: 10 resolver tests, touched-file ESLint/diagnostics and `git diff --check` passed; repository-wide TypeScript retains unrelated baseline diagnostics.
- Marked COMMERCE-010 Complete and promoted COMMERCE-012 to Ready. COMMERCE-013 and COMMERCE-014 remain independently Ready.

### 2026-09-23 — COMMERCE-010 Attempt 1 changes requested

- Reviewed the effective model/prompt resolver with snapshot consistency and fail-closed inheritance as the primary focus.
- Accepted in substance the `REPEATABLE READ` transaction boundary, independent shop/platform model and prompt lookup, explicit source provenance, and server-side selected-shop/environment derivation.
- Identified a mandatory-baseline defect: valid shop overrides currently mask missing/disabled/invalid platform defaults because only `shopOverride ?? platformDefault` is validated; ARCH-021 requires a valid platform model default and platform active prompt for the environment even when a shop override exists.
- Required focused coherent-snapshot proof under concurrent configuration mutation and a selected-shop server-action rejection regression, because the submitted unit test only asserts that `RepeatableRead` was requested.
- Returned COMMERCE-010 to Ready at `attempt: 1`; COMMERCE-012 remains Pending while COMMERCE-013/014 remain independently Ready.

### 2026-09-23 — COMMERCE-015 Attempt 2 accepted

- Accepted the bounded revision-history read contract after Attempt 2 supplied the canonical launcher/worktree, synchronization, claim and recursive-submodule evidence requested by the Attempt 1 review.
- Confirmed the five task-owned implementation/test files are unchanged from the substantively conformant Attempt 1 submission; no source churn was introduced for the evidence-only correction.
- Marked COMMERCE-015 Complete and satisfied the added dependency for COMMERCE-013.
- Returned COMMERCE-013 to Ready at `attempt: 1`; its next claim becomes Attempt 2 and must consume `listPromptTemplateRevisions` plus complete the previously recorded template-editor state/dirty-guard/production-composition corrections.

### 2026-09-23 — COMMERCE-011 Attempt 3 accepted

- Reviewed implementation `d2d67dd` with submitted parent report `b90718b`.
- Confirmed Attempt 3 is validation-only relative to Attempt 2: no runtime source changed; the new production-composition and server-action regression files prove the previously requested boundaries.
- Accepted production `/agent-configuration` composition with server-resolved `shopId`, trusted server-derived environment, real COMMERCE-007 action handoff, ADMIN read-only behavior and secret-safe rendering.
- Accepted explicit serializable forbidden, stale-CAS and conflicting-replay server-action outcomes while retaining exact-original-operation reconciliation for `unknown` results.
- Marked COMMERCE-011 Complete. COMMERCE-008 remains the sole Ready Phase 2 Commerce frontier; COMMERCE-012/013/014 retain their remaining service dependencies.

### 2026-09-23 — COMMERCE-009 Attempt 2 accepted

- Reviewed implementation `9ee65b3` with submitted parent report `59ee628e`.
- Accepted the CAS/replay correction: failed CAS/domain transactions now reconcile a matching durable `CommerceAuditEvent` before returning the known error; conflicting operation-id reuse remains `CONFLICTING_REPLAY` and genuinely indeterminate no-receipt outcomes remain `unknown`.
- Accepted explicit SET/CLEAR prompt-pointer audit targets, including clear-time snapshots of the exact prompt/revision/shop/environment being removed.
- Accepted exact published template-revision copy semantics and immutable copy provenance.
- Reviewed focused validation: 16 Vitest tests, 6 PostgreSQL lifecycle/concurrency tests, focused ESLint/TypeScript diagnostics and `git diff --check` passed; repository-wide TypeScript retains unrelated baseline diagnostics.
- Reconciled workflow metadata drift where the executor returned the YAML state as `ready` despite an explicit Ready-for-architect-review Completion Report; no implementation rework was required.
- Marked COMMERCE-009 Complete and promoted COMMERCE-010 and COMMERCE-014 to Ready. COMMERCE-013 remains independently Ready; COMMERCE-012 remains Pending on COMMERCE-010.

### 2026-09-23 — COMMERCE-009 Attempt 1 changes requested

- Reviewed the platform/shop prompt lifecycle service with CAS semantics as the primary focus.
- Accepted the atomic draft/publish and platform/shop pointer write predicates in substance.
- Identified receipt-first replay drift: known `LifecycleError` CAS/domain failures return before checking whether the winning transaction already durably committed the same `operationId`.
- Identified invalid pointer audit-target mapping: SET pointer results expose `promptRevisionId`, not generic `id`, and CLEAR currently loses both prompt targets required by `arch020_audit_targets`.
- Required template copy-on-use to identify one exact published `sourceTemplateRevisionId` rather than accepting template-id-only ambiguous selection.
- Returned COMMERCE-009 to Ready at `attempt: 1`; COMMERCE-010/012/014 remain gated until COMMERCE-009 is Complete.

### 2026-09-23 — COMMERCE-008 Attempt 3 accepted

- Accepted receipt-first reconciliation for known CAS/domain failures after live PostgreSQL proof that identical concurrent CAS-bound commands replay one durable `CommerceAuditEvent` result.
- Accepted per-template concurrent draft numbering after correcting the Prisma row-lock query to use parameterised `Prisma.sql`; live PostgreSQL regression proved two concurrent drafts receive distinct revisions.
- Corrected the PostgreSQL regression fixture to use the accepted prompt-template key grammar; no production schema or validation rule was weakened.
- Marked COMMERCE-008 Complete and promoted COMMERCE-009 to Ready. COMMERCE-013 remains gated on COMMERCE-011; COMMERCE-014 remains gated on COMMERCE-009 and COMMERCE-011.

### 2026-09-23 — COMMERCE-008 Attempt 2 changes requested

- Reviewed implementation `7a90a03` with submitted parent report `6ca2b49b`; accepted the per-template `FOR UPDATE` draft revision allocation and the generic post-failure durable-receipt reconciliation path.
- Identified one remaining same-command replay gap: known CAS/domain errors are returned before receipt reconciliation, so an identical concurrent CAS-bound mutation can return `CAS_CONFLICT` even after the winning transaction durably committed the same operation/result.
- Returned COMMERCE-008 to Ready at `attempt: 2`; Attempt 3 is limited to receipt-first reconciliation of failed concurrent commands plus focused disposable-PostgreSQL proof. COMMERCE-009/013/014 remain gated until COMMERCE-008 is Complete.

### 2026-09-23 — COMMERCE-008 Attempt 1 changes requested

- Reviewed implementation `ddb03c1` with submitted parent report `23d9224`; accepted in substance the data-driven category/template lifecycle, atomic existing-row edit-version CAS, exact UTF-8 publication hashing, immutable published revision boundary, disabled-selection/historical-read semantics, authorization and no-provider-execution boundary.
- Identified a durable operation-receipt concurrency gap: simultaneous identical/conflicting `operationId` calls can race on `CommerceAuditEvent.id`, and the losing/ambiguous outcome is returned as a generic error rather than reconciling the winning receipt or the existing Studio `unknown` result.
- Identified unsafe concurrent draft revision allocation: `count + 1` is not serialised per template, so independent concurrent draft creates can collide on `(templateId, revisionNumber)`.
- Returned COMMERCE-008 to Ready at `attempt: 1`; COMMERCE-009/013/014 remain gated until COMMERCE-008 is Complete. COMMERCE-007 remains independently executable/correctable.
### 2026-09-23 — COMMERCE-007 Attempt 3 accepted

- Reviewed implementation `2f1ed58` with submitted parent report `f6ce4272`.
- Accepted the narrow absent-row CAS correction: platform creation now requires `expectedEditVersion: null`, and shop creation requires both `expectedGenerationId: null` and `expectedEditVersion: null`; stale tokens from cleared/removed state return `CAS_CONFLICT`.
- Preserved the accepted Attempt 2 atomic write-boundary CAS, first-write race handling and durable concurrent `CommerceAuditEvent` receipt reconciliation.
- Treated the intermittent PostgreSQL `unknown` outcome envelope as non-blocking because the contract explicitly permits `unknown` for indeterminate storage/transaction outcomes, the broader concurrency implementation was unchanged in Attempt 3, and its prior submitted run passed 3/3.
- Marked COMMERCE-007 Complete and promoted COMMERCE-011 to Ready. COMMERCE-010 remains Pending on COMMERCE-009; COMMERCE-008 remains independent and its separately reviewed state must be preserved.

### 2026-09-23 — COMMERCE-007 Attempt 2 changes requested

- Reviewed implementation `b79fc72` with submitted parent report `8ae46735`.
- Accepted the Attempt 1 corrections for atomic catalogue/platform/shop CAS, first-write race handling and concurrent durable `CommerceAuditEvent` receipt reconciliation; submitted PostgreSQL concurrency tests passed 3/3.
- Identified one remaining generation/CAS edge: an absent platform/shop selection currently permits stale non-null expected tokens to be reinterpreted as a create. A create is valid only from the explicit absence tokens (`expectedEditVersion: null` for platform; both `expectedGenerationId: null` and `expectedEditVersion: null` for shop).
- Returned COMMERCE-007 to Ready at `attempt: 2`; the next claim becomes Attempt 3. COMMERCE-010/011 remain gated and COMMERCE-008 retains its separately reviewed state.

### 2026-09-23 — COMMERCE-007 Attempt 1 changes requested

- Reviewed implementation `d3252e0` with submitted parent report `bfe2b7b4`.
- Confirmed the bounded model catalogue/platform/shop service, authorization, trusted environment derivation, disabled-pointer preservation, durable audit storage and no-provider-call boundary are substantially present.
- Identified non-atomic read-then-write CAS for catalogue/platform/shop mutations; concurrent callers can both pass the same token and succeed, including first-time `upsert` races that can overwrite a newly-created platform/shop selection instead of returning stale CAS.
- Identified concurrent `operationId` replay drift: Prisma unique-receipt races are mapped to generic conflict before reconciling the winning `CommerceAuditEvent`, so identical concurrent commands do not guarantee replay of the durable result.
- Returned COMMERCE-007 to Ready at `attempt: 1`; COMMERCE-010/011 remain gated. COMMERCE-008 remains independently Ready.

### 2026-09-23 — DATABASE-001 Attempt 3 accepted

- Accepted the exact Phase 2 durable CommerceAgent configuration schema and single migration after the SQLSTATE `55P04` correction retained the audit-target invariant using text comparison rather than uncommitted enum constants.
- Developer live PostgreSQL 15 evidence passed ARCH-021 fresh and upgrade rehearsals with 24/24 behavioral cases in each mode; upgrade preservation passed.
- Predecessor compatibility passed ARCH-020 fresh and upgrade rehearsals with 298/298 behavioral cases in each mode; upgrade preserved 217 predecessor indexes unchanged.
- Rehearsal-only compatibility fixes made during review removed stale assumptions about a pre-existing platform lineage and about ARCH-020 being the final Commerce schema shape; they did not alter the accepted Prisma schema or ARCH-021 migration semantics.
- Marked DATABASE-001 Complete and promoted COMMERCE-007 and COMMERCE-008 to Ready. COMMERCE-009 remains Pending on COMMERCE-008.

### 2026-09-23 — DATABASE-001 Attempt 2 changes requested

- Reviewed implementation `7ab7c27b56468af346df2f1ae92710b094779c7e` with submitted parent report `4c4684521aacaa8e03f1a2eeaa6467132e0e56dd`.
- Confirmed every Attempt 1 fixture/static-validation correction is present: retained-DRAFT and exact-other-shop pointer cases, race-winner independence, catalogue-provider immutability, complete predecessor-index subset preservation, and ARCH-020 historical-action-prefix compatibility.
- Developer live fresh-rehearsal evidence reached `20260923150000_arch021_agent_configuration` and failed with PostgreSQL SQLSTATE `55P04` because newly appended `CommerceAuditAction` values are referenced by `arch020_audit_targets` before the enum-addition transaction commits.
- Required a bounded correction inside the existing single ARCH-021 migration directory: preserve the exact audit-target semantics while avoiding uncommitted enum-literal resolution (prefer `"action"::text` comparisons); do not split the migration or weaken the database invariant.
- Returned DATABASE-001 to Ready at `attempt: 2`. COMMERCE-007 and COMMERCE-008 remain Pending until fresh/upgrade ARCH-021 and predecessor ARCH-020 live rehearsals pass and DATABASE-001 is architect-accepted.

### 2026-09-23 — DATABASE-001 Attempt 1 changes requested

- Reviewed implementation `e8f173be5dc9197bcdf5fdd68f35ce335c2e0174` with submitted parent report `bc043533bec160dffe19fb08f894a6cd1e3f67cf`.
- Confirmed the exact Phase 2 schema/migration surface and ARCH-021 static contract are substantially present.
- Identified deterministic rehearsal-fixture defects: the platform-DRAFT rejection uses an already-published revision, the other-shop rejection uses an exact-same-shop lineage, and the concurrency fixture assumes a particular winner.
- Required the upgrade validator to prove preservation of all predecessor indexes (including existing `CommerceAuditEvent` indexes) by treating the pre-migration index set as a required subset after the additive migration.
- Explicitly authorised the existing ARCH-020 static validator to become extension-aware for appended `CommerceAuditAction` values while continuing to require its historical 17-action prefix/order exactly.
- Returned DATABASE-001 to Ready at `attempt: 1`. Fresh and upgrade rehearsal remain mandatory before acceptance; COMMERCE-007 and COMMERCE-008 remain Pending.

### 2026-09-23 — Phase 2 task set defined

- Combined all Phase 2 Database schema work into one cohesive `ARCH-021-DATABASE-001` migration/task covering model catalogue/selections, prompt-template categories/templates/revisions, prompt lineages/revisions and active pointers.
- Added a data-driven prompt-template category/classification taxonomy: every template belongs to one category and a category such as `Clothing & Fashion` may contain multiple templates without code/schema enum changes.
- Kept prompt templates as copy-on-use authoring assets independent of models/features and retained immutable template/prompt revision semantics.
- Defined Commerce services for model lifecycle, category/template lifecycle, prompt lifecycle and effective configuration resolution.
- Split the former broad platform Agent Configuration UI task into independently reviewable model-shell (`COMMERCE-011`), selected-shop overrides (`COMMERCE-012`), template library (`COMMERCE-013`) and platform prompt authoring (`COMMERCE-014`) tasks while keeping one shared Agent Configuration domain module outside `StudioWorkspace`.
- Added immutable shop-override `generationId` CAS tokens so clear/recreate cannot ABA-match stale model/prompt override mutations.
- Clarified that prompt/template DRAFT revisions may persist empty content, publication requires non-blank content, and published hashes cover exact persisted UTF-8 prompt bytes without normalisation.
- Standardised Phase 2 privileged command replay on the existing immutable `CommerceAuditEvent` operation-receipt convention and clarified coherent resolver reads require one statement or `REPEATABLE READ`/stronger semantics.
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

### 2026-09-23 — Phase 3 task set defined

- Confirmed Phase 2 authoritative task files are Complete and reconciled stale Ready prose in the parent/index.
- Confirmed the full persisted Tool authoring definition is Commerce-only; removed Phase 3 Shared/package-publication work and established `src/commerce/tool-definition/` as the canonical owner while retaining only true cross-service descriptor/result/manifest/runner contracts in Shared 0.14.2.
- Kept generic external HTTP GET-only; request JavaScript is a pure `buildRequest({args})` descriptor builder and cannot perform I/O or select origin/method/credentials.
- Reused pinned Shopify Dev MCP/Admin 2026-07 schema as development validation evidence while keeping normal Studio validation local/offline.
- Deferred all real provider calls and publication proof to Phase 4; Phase 3 new definitions fail closed with LIVE_TEST_REQUIRED.
- Continued incremental Studio decomposition by extracting the Tool domain from StudioWorkspace.
### 2026-09-24 — COMMERCE-030 Attempt 1 changes requested

- Accepted in substance implementation `fd281e0` / submitted parent report `f9ec3a52`: Commerce MCP no longer verifies RS256/JWT caller assertions or requires MCP caller credentials, parses only the bounded private-link context header, derives environment locally and keeps PostgreSQL turn/grant/release/tool authorization in the execution path.
- Submitted focused MCP suite (26 tests), local persisted external-MCP diagnostic, lint and diff checks passed; unrelated repository typecheck and health-origin baseline issues remain non-blocking.
- Returned COMMERCE-030 to Ready for a bounded correction because task-owned config currently logs raw database/Redis endpoint values, known production authorization-domain failures can be collapsed to generic `UNAVAILABLE`, and runtime/env guidance still contains stale RSA/signed-context wording.
- BACKGROUND-001 and GATEWAY-001 remain Pending until the private-MCP simplification dependencies are architect-accepted Complete.

### 2026-09-24 — COMMERCE-030 Attempt 2 accepted

- Accepted implementation `e9c7c85009552463f9447475072e9bbc6f2ff433` with submitted parent report `3ded199e35f3d40ccfa038dba80d46c71c51c835`.
- Confirmed task-owned configuration no longer logs raw database/Redis endpoint values.
- Confirmed known production authorization-domain failures preserve bounded MCP codes while unexpected resolver/storage failures remain fail-closed `UNAVAILABLE`.
- Confirmed Commerce-owned RSA assertion/signed-context configuration and readiness guidance is removed without altering unrelated Studio Auth.js session behavior.
- Confirmed the private MCP remains context-only over the private service link with server-derived environment, local ten-second tool deadline and PostgreSQL shop/turn/grant/release/tool authorization intact.
- Focused MCP suite (26 tests), persisted local external-MCP diagnostic, lint and `git diff --check` passed; repository-wide typecheck/build and one stale route-source assertion remain documented non-blocking baselines.
- Marked COMMERCE-030 Complete and promoted BACKGROUND-001 to Ready. GATEWAY-001 remains Pending until BACKGROUND-001 is Complete.
