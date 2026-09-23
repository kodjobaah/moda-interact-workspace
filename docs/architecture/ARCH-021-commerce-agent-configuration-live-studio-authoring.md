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

Agreed — Phase 0 contract accepted; Phase 1 implementation in progress; COMMERCE-001 accepted Complete.

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
   credential services; fixture ports remain test-only.
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
| ARCH-021-COMMERCE-002 | moda_commerce | Ready | ARCH-021-COMMERCE-001, ARCH-020-COMMERCE-022 |
| ARCH-021-COMMERCE-003 | moda_commerce | Complete | ARCH-020-COMMERCE-013, ARCH-020-COMMERCE-018 |
| ARCH-021-COMMERCE-004 | moda_commerce | Complete | ARCH-021-COMMERCE-003 |
| ARCH-021-COMMERCE-005 | moda_commerce | Ready | ARCH-021-COMMERCE-001, ARCH-021-COMMERCE-004, ARCH-020-COMMERCE-023 |
| ARCH-021-COMMERCE-006 | moda_commerce | Pending | ARCH-021-COMMERCE-005, ARCH-020-COMMERCE-026, ARCH-020-COMMERCE-027, ARCH-020-COMMERCE-031 |

Current executable frontier:

```text
ARCH-021-COMMERCE-002   install the production ConnectionPort into U15/U16 routes
ARCH-021-COMMERCE-005   wire persisted connection revisions into U06 Tool authoring
```

Those tasks are independent and may execute in parallel. No task is automatically
launched merely because it is Ready.

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

Implement model catalogue, model selection, prompt lineage/revisions/pointers and the
Agent Configuration Studio surface.

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

Phase 1 is materialised as six Commerce tasks under:

`docs/decisions/commerce/ARCH-021/`

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-021-COMMERCE-001 | moda_commerce | Complete | ARCH-020-COMMERCE-020, ARCH-020-COMMERCE-024, ARCH-020-COMMERCE-028 |
| ARCH-021-COMMERCE-002 | moda_commerce | Ready | ARCH-021-COMMERCE-001, ARCH-020-COMMERCE-022 |
| ARCH-021-COMMERCE-003 | moda_commerce | Complete | ARCH-020-COMMERCE-013, ARCH-020-COMMERCE-018 |
| ARCH-021-COMMERCE-004 | moda_commerce | Complete | ARCH-021-COMMERCE-003 |
| ARCH-021-COMMERCE-005 | moda_commerce | Ready | ARCH-021-COMMERCE-001, ARCH-021-COMMERCE-004, ARCH-020-COMMERCE-023 |
| ARCH-021-COMMERCE-006 | moda_commerce | Pending | ARCH-021-COMMERCE-005, ARCH-020-COMMERCE-026, ARCH-020-COMMERCE-027, ARCH-020-COMMERCE-031 |

Later phases are intentionally not decomposed yet. Expected later owners still include:

- `moda_database` for durable model/prompt configuration and grant fields;
- `moda_shared` for grant/manifest/runner contract changes;
- `moda_commerce` for Agent Configuration, live Tool tests, MCP resolution and preview;
- `moda_background` for pinned model/prompt consumption;
- `moda_system_test` only after the required implementation dependencies are Complete.

No implementation task may depend on a system-test task.

## Open Questions

The following are deliberately deferred beyond the Phase 0 ownership contract:

- which exact OpenAI/Groq models Moda initially exposes in the catalogue;
- whether merchants may select shop model overrides or only edit prompts;
- catalogue entitlement/tier restrictions;
- retention period for old prompt revisions;
- whether preview conversation state remains Redis TTL state or gains durable preview
  tables when merchant access is introduced.

None of these changes the core rule: one effective model and one effective
configurable behavioural prompt are resolved per shop with platform fallback and are
independent of features.

## Change History

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
