---
id: ARCH-024
title: CommerceAgent model runtime and Feature-composed Test Conversations
status: agreed
coordinator: moda_architect
created: 2026-10-01
updated: 2026-10-01
---

# ARCH-024: CommerceAgent model runtime and Feature-composed Test Conversations

## Status

Agreed.

ARCH-024 is the successor architecture for the unstarted ARCH-021 Phase-6 Preview/Test Conversation work. It keeps accepted ARCH-021 Studio authoring foundations, consumes frozen ARCH-023 Platform/Shop Instruction semantics, and replaces the unstarted ARCH-021 COMMERCE-105..109 / GATEWAY-002 / SYSTEM-TEST-004 plan with a broader Admin-owned model catalogue, scoped availability, database-backed OpenRouter credentials, LangChain/OpenRouter runtime integration, production Background parity and Feature-composed selected-shop Test Conversations.

Two ARCH-024 implementation tasks have no prerequisites and are the initial Ready frontier:

```text
ARCH-024-DATABASE-001
ARCH-024-COMMERCE-001
```

All other ARCH-024 tasks remain Pending behind their declared dependencies.

Integrated system-test tasks are **deliberately not materialised in this architecture session** because final acceptance overlaps frozen ARCH-023 completion and upcoming architecture work. Any terminal integrated validation will be defined separately against the final combined architecture.

## Problem

The current platform has a useful CommerceAgent configuration and Studio foundation, but the model/runtime and Test Conversation boundaries are inconsistent with the target product model:

1. `CommerceModelCatalogueEntry.provider` is represented through the closed `OPENAI | GROQ` provider enum and corresponding application unions/validation.
2. Commerce Studio currently owns Model Catalogue administration even though model catalogue/availability/credential administration is platform administration.
3. There is no durable distinction between **what model entries exist**, **where those model entries are available**, and **which single model is currently active** for Platform or Shop Agent Configuration.
4. Preview still contains the older human-facing Tool/Release/Fixture composition workflow and environment-selected Preview provider/model/API-key configuration.
5. Human Test Conversations do not yet represent the agreed product flow: selected Shop + selected Features, where selecting one Feature means **all direct Capabilities under that Feature**.
6. Human Test Conversations still have synthetic runtime assumptions such as `preview.myshopify.com` / fixture Tool execution instead of the selected Shop's real server-owned Tool execution context.
7. Production Background CommerceAgent turns still use the older Groq conversational-model path rather than the same effective model rules and OpenRouter runtime intended for Studio testing.
8. Ordinary model-provider credential rotation should not require an application restart or deployment.

ARCH-024 corrects those boundaries without redesigning accepted Feature/Capability/Tool publication mechanics, frozen ARCH-023 instruction semantics or existing Background conversation ordering.

## Goals

- Make Admin the owner of Model Availability, Model Catalogue entries and OpenRouter credential lifecycle.
- Make Commerce Studio **selection-only** for models: one Platform active model and an optional Shop override.
- Preserve `CommerceAgentConfiguration.modelId = null` on a Shop configuration as the explicit "Use Platform model" representation.
- Guarantee exactly one **effective active model** for a Shop when configuration is valid.
- Fail closed when an explicit Shop model override becomes unavailable, disabled or otherwise invalid; do not silently fall back.
- Represent model availability as one global Platform Availability plus zero/one Shop Availability per Shop, with Availability `1 -> many` Catalogue Entries.
- Keep model identity as dynamic `provider + providerModelId` strings and derive the OpenRouter model slug as `provider + '/' + providerModelId`.
- Store model runtime configuration as bounded, extensible, direct OpenRouter-style JSON rather than a closed list of model parameters.
- Store one encrypted OpenRouter credential per `CommerceEnvironment` and permit hot replacement without restarting Commerce or Background.
- Use a thin Shared LangChain `ChatOpenRouter` integration behind the existing Moda Commerce runner model interface; do not introduce a second agent orchestration framework.
- Remove obsolete human-facing Preview composition controls first, then build the replacement Test Conversation flow on a clean surface.
- Compose Test Conversations from selected Feature IDs only; every direct Capability under every selected Feature participates.
- Resolve exact current published Tool revisions and Feature Behaviour at conversation start and retain that authored configuration for the lifetime of the Test Conversation.
- Execute human Test Conversation Tools against the real selected Shop through existing production execution infrastructure.
- Use the same effective active-model rules in Test Conversations and production Background CommerceAgent turns.
- Keep live operational secrets/session material outside the Conversation Configuration Snapshot and resolve current credentials when needed.
- Remove obsolete static Preview provider/model/API-key deployment configuration after consumers no longer require it.

## Non-Goals

ARCH-024 does not introduce:

- merchant-facing model selection;
- merchant-facing Model Catalogue or Model Availability administration;
- a new Shopify application task;
- a new public model-management API;
- a new database, Redis deployment, queue or service;
- a new model-provider-specific credential for every Catalogue Entry;
- a configurable OpenRouter base URL;
- a closed allowlist of every OpenRouter model/request option;
- model fallback lists stored in Catalogue configuration;
- LangGraph adoption or a CommerceAgent orchestration rewrite;
- changes to ARCH-023 Merchant Knowledge embedding-model provenance;
- changes to frozen ARCH-023 Platform/Shop Instruction ownership or trust hierarchy;
- changes to Feature/Capability/Tool publication semantics already accepted under ARCH-021;
- automatic modification/clearing of Agent Configuration when Admin disables or reassigns a selected model;
- system-test task materialisation in this architecture session.

## Rollout Classification

ARCH-024 is a **PRE-PRODUCTION / BREAKING ROLLOUT** for Model Catalogue storage and the human Test Conversation surface.

The platform remains in development. ARCH-024 therefore does not require compatibility/backfill machinery solely to preserve development-only `OPENAI`/`GROQ` catalogue rows or the obsolete human Preview composition controls. The database migration must reach the deterministic target schema and the application tasks must reach the target runtime contract.

Durable state outside the explicitly replaced model-development state is not implicitly disposable. Database and repository tasks must preserve unrelated ARCH-020/021/023 durable data and accepted runtime semantics.

## Current Architecture

### Model Catalogue and Agent Configuration

The current database already provides:

```text
CommerceModelCatalogueEntry
CommerceAgentConfiguration
CommerceAuditEvent
```

Agent Configuration already supports independent Platform and Shop model selection. A Shop configuration with no `modelId` represents inheritance from Platform. This existing selection model is retained by ARCH-024.

The current Catalogue provider identity is constrained by the closed `CommerceModelProvider` enum (`OPENAI | GROQ`) and a global `(provider, providerModelId)` uniqueness rule. Catalogue entries are not currently scoped through Model Availability.

### Commerce Studio

Commerce Studio currently contains both Agent model selection and Model Catalogue administration. ARCH-024 moves Catalogue/Availability/Credential administration to Admin and leaves Commerce Studio responsible only for selecting the one active Platform model or one valid Shop override.

### Human Preview/Test Conversations

The integrated baseline still contains the older Preview model:

```text
Tool test / Conversation test
Tool source
Release source
Saved selection RELEASE / DRAFT
Fixture scenario
FIXTURE / MODEL mode
Preview provider/model/API-key environment tuple
Release-composer Test Conversation handoff
```

The human Test Conversation path therefore exposes implementation/testing concepts rather than the intended product composition.

### Production Background model execution

Production CommerceAgent turns currently retain an older Groq conversational model path. Existing Background ordering, history, admission, LangGraph/workflow structure and WhatsApp speech-transcription use of Groq are separate concerns and are retained.

## Proposed Architecture

### Ownership boundary

```text
ADMIN
  Model Availability
  Model Catalogue Entries
  OpenRouter credential lifecycle
        |
        v
DATABASE
  durable catalogue / availability / encrypted credential state
        |
        +-------------------------+
        |                         |
        v                         v
COMMERCE STUDIO                BACKGROUND
  select one active model        resolve same effective active model
  Feature-composed testing       production CommerceAgent turns
        |                         |
        +------------+------------+
                     v
             SHARED MODEL RUNTIME
             LangChain ChatOpenRouter
                     |
                     v
                  OpenRouter
```

Merchant-facing Shopify application code does not participate in model administration or selection. A merchant experiences whichever effective active model Commerce Studio has configured for that Shop.

### Exactly one effective active model

For each environment, Platform Agent Configuration selects one Platform-available Catalogue Entry.

A Shop Agent Configuration may either:

```text
modelId = null
    -> explicitly inherit the Platform selected model

modelId = <catalogue entry>
    -> explicit Shop override
```

Effective resolution is:

```text
Shop has explicit modelId?
        |
        +-- YES -> validate exact entry is enabled and effectively available
        |           |
        |           +-- valid   -> use Shop-selected entry
        |           +-- invalid -> UNAVAILABLE (no Platform fallback)
        |
        +-- NO  -> validate Platform selection
                    |
                    +-- valid   -> use Platform-selected entry
                    +-- invalid -> UNAVAILABLE
```

Absence means inheritance. A broken explicit selection is a configuration error and fails closed.

### Effective model availability

There is exactly one global Platform Model Availability and at most one Shop Model Availability per Shop.

For Shop `S`:

```text
EffectiveAvailableModels(S)
    = enabled entries in enabled PLATFORM Availability
      UNION
      enabled entries in enabled SHOP Availability where shopId = S
```

Availability determines **what may be selected**. Agent Configuration determines **what has been selected**.

## Data Model

### `CommerceModelAvailabilityScope`

```text
PLATFORM
SHOP
```

This is distinct from prompt/instruction scope.

### `CommerceModelAvailability`

Target durable fields:

```text
id
scope                    PLATFORM | SHOP
shopId                   nullable; required for SHOP, null for PLATFORM
enabled
editVersion
createdByAdminId          nullable for deterministic bootstrap Platform row
updatedByAdminId          nullable for deterministic bootstrap Platform row
createdAt
updatedAt
```

Relations:

```text
Shop?                     ON DELETE/UPDATE RESTRICT
PlatformAdmin? creator    ON DELETE/UPDATE RESTRICT
PlatformAdmin? updater    ON DELETE/UPDATE RESTRICT
entries 1 -> many CommerceModelCatalogueEntry
auditEvents
```

Invariants:

- exactly at most one Platform row (`scope = PLATFORM`, `shopId = NULL`);
- at most one Shop Availability per Shop;
- `PLATFORM <=> shopId IS NULL` and `SHOP <=> shopId IS NOT NULL`;
- `editVersion > 0`;
- `id`, `scope` and `shopId` immutable after insert;
- deletion rejected;
- an Availability may contain zero Catalogue Entries.

The deterministic bootstrap Platform Availability ID is:

```text
arch024-platform-model-availability
```

No Shop Availability is created by migration.

### `CommerceModelCatalogueEntry`

Target fields:

```text
id
availabilityId
provider                   lower-case dynamic string
providerModelId
displayName
description
configurationSchemaVersion
configuration              JSONB OpenRouter-style request options
enabled
editVersion
createdByAdminId
updatedByAdminId
createdAt
updatedAt
```

Identity:

```text
provider + '/' + providerModelId
```

Database uniqueness:

```text
UNIQUE(availabilityId, provider, providerModelId)
```

This deliberately allows the same OpenRouter model identity to exist as independently configured entries in different Availability scopes.

`id`, `provider` and `providerModelId` are immutable. `availabilityId` is mutable so Admin can reassign one existing Catalogue Entry without cloning it. Reassignment or disablement does not rewrite `CommerceAgentConfiguration.modelId`; an invalid explicit selection remains durable and resolves `UNAVAILABLE` until corrected.

The closed Prisma/PostgreSQL `CommerceModelProvider` enum is removed. Canonical providers are validated lower-case strings such as:

```text
openai
groq
anthropic
google
```

### Model configuration JSON

`configurationSchemaVersion = 1` versions the Moda envelope/safety contract; it does not enumerate every OpenRouter option.

Persisted configuration is a direct OpenRouter-style JSON object, for example:

```json
{
  "temperature": 0.2,
  "top_p": 0.9,
  "reasoning": {
    "effort": "high"
  },
  "provider": {
    "allow_fallbacks": true,
    "sort": "latency",
    "data_collection": "deny",
    "require_parameters": true
  }
}
```

The Shared contract bounds JSON size/depth/cardinality and rejects prototype-pollution keys. Unknown non-reserved OpenRouter options remain valid. Stored configuration may not override Moda-owned runtime/security values including model identity, messages, Tools, Tool policy, output-token budget, credentials, headers/base URL, tracing/session/user identity, plugins, web search or modalities.

The `provider` object inside model configuration means **OpenRouter routing preferences**. It is distinct from `CommerceModelCatalogueEntry.provider`, which is the first component of the model slug.

### `CommerceOpenRouterCredential`

Target fields:

```text
id
environment                UNIQUE CommerceEnvironment
ciphertext
nonce                       12 bytes
authTag                     16 bytes
keyId
editVersion
updatedByAdminId
createdAt
updatedAt
```

There is zero or one row per environment. Absence means OpenRouter is not configured for that environment.

Lifecycle:

```text
SET      -> INSERT
REPLACE  -> CAS UPDATE
REMOVE   -> CAS DELETE
```

No Catalogue Entry contains a credential FK. At execution time:

```text
CommerceAgentConfiguration.environment
    -> current CommerceOpenRouterCredential for that environment
```

Normal credential replacement changes database ciphertext only; it does not change Catalogue rows and must not require a service restart.

### Existing `CommerceAgentConfiguration`

ARCH-024 retains the existing environment-scoped Platform/Shop configuration model and `modelId` selection field. It does not add a second active/selected flag to Catalogue Entries.

The durable states remain conceptually:

```text
PLATFORM config: modelId = selected Platform entry
SHOP config:     modelId = explicit override OR null to inherit Platform
```

## Shared Contracts and Model Runtime

### Package ownership

Owner: `moda-interact-shared`

Package:

```text
@modainteract/moda-interact-shared
```

Pure contract entrypoint:

```text
@modainteract/moda-interact-shared/commerce/model
```

Node runtime entrypoint:

```text
@modainteract/moda-interact-shared/commerce/model/node
```

Consumers include Admin, Commerce and Background as appropriate.

### Canonical contracts

Shared owns the versioned validators/types for:

- `CommerceEnvironment`;
- `CommerceModelAvailabilityScope`;
- Availability shape;
- dynamic provider/providerModelId identity;
- Catalogue Entry shape;
- Agent model-selection shape;
- bounded extensible OpenRouter-style model configuration;
- `createOpenRouterModelId`;
- reserved configuration keys.

### Runtime integration

Shared implements a thin Node-only `OpenRouterModelClient` over `@langchain/openrouter` `ChatOpenRouter` that satisfies the existing Moda Commerce runner model dependency (`ModelRequest` -> `ModelStep`).

Architecture boundary:

```text
CommerceAgent / runCommerceTurn
        -> existing Moda model request/result contract
        -> OpenRouterModelClient
        -> LangChain ChatOpenRouter
        -> OpenRouter
```

LangChain/OpenRouter types do not leak into the pure Shared model contracts or the existing runner contracts.

The runtime client:

- always receives the credential explicitly from its consumer;
- never depends on `OPENROUTER_API_KEY` fallback;
- maps known OpenRouter snake_case settings to the reviewed `ChatOpenRouter` API;
- forwards unknown non-reserved options through `modelKwargs`;
- binds only runner-provided Tools;
- keeps Tool choice, parallel Tool policy and output-token bounds runtime-owned;
- propagates `AbortSignal`;
- performs no Shared-owned retry loop;
- redacts provider/credential failure details.

LangGraph is explicitly outside ARCH-024 Shared scope. Existing orchestration remains authoritative.

## Admin Application

### Model Availability

Admin provides:

```text
/commerce-models/availability
```

Authenticated Platform Admins may read. Mutations independently require `SUPER_ADMIN`.

The deterministic Platform Availability is created by the database migration and is inspectable/enableable/disableable but not recreatable, deletable or retargetable. Shop Availability is zero/one per canonical `Shop.id` and is created/managed by Admin.

### Model Catalogue

Admin provides:

```text
/commerce-models/catalogue
```

Admin owns create/edit/enable/disable/reassignment of Catalogue Entries. Provider/providerModelId become immutable after creation. Availability, display metadata and model configuration remain mutable under CAS.

Admin displays all Platform and Shop catalogue entries. Commerce Studio does not administer them.

### OpenRouter credentials

Admin provides credential status plus `SET`, `REPLACE` and `REMOVE` for the current deployment environment. Existing secret plaintext is never returned to the browser.

Encryption uses the existing Commerce credential keyring mechanism and AES-256-GCM envelope. Normal credential replacement is database-only and becomes visible to the next runtime model invocation without restart.

## Commerce Studio

### Preview cleanup first

`ARCH-024-COMMERCE-001` is intentionally the first Commerce task. It removes the obsolete human-facing Tool/Release/Fixture Preview composition controls while retaining referenced low-level run/reconciliation infrastructure required by accepted Tool Authoring/Code Response paths and later ARCH-024 work.

After cleanup, `/preview` is a deliberately minimal selected-shop-aware Test Conversations shell until the replacement tasks are complete.

### Model selection only

Commerce Studio no longer creates/edits Catalogue Entries, Availability or credentials.

Platform Agent Configuration selects one Platform-available active model.

Shop Agent Configuration presents the effective available model set and allows either:

```text
Use Platform model
```

or one explicit available override.

Broken durable selections are surfaced as unavailable and remain correctable; they are not silently cleared.

## Feature-composed Test Conversations

### User intent

The administrator selects:

```text
one validated Studio Shop
one or more Features
```

The administrator does **not** select:

- Capability IDs;
- Tool revisions;
- model/provider/model ID on the Test Conversations screen;
- prompt/instruction revisions;
- credentials.

### Server composition

For the ordered selected Feature IDs, Commerce resolves:

```text
Feature
    -> every direct Capability
    -> each Capability's current PUBLISHED Tool revision
    -> Feature Behaviour once for the Feature
```

There is no per-Capability opt-out. Selected Features with unresolved required Capability/Tool state fail conversation creation rather than silently shrinking the composition.

Feature order is preserved. Capability ordering within each Feature is deterministic.

### Conversation Configuration Snapshot

At Test Conversation start Commerce creates a server-side **Conversation Configuration Snapshot** containing the authored configuration to be tested, including:

```text
selected Shop identity
active model Catalogue Entry identity
provider + providerModelId
validated model configuration
selected Feature identities/order
Feature Behaviour
resolved Capability identities
exact published Tool revision identities
ARCH-023 Platform Instructions
optional ARCH-023 Shop Instructions
```

The snapshot means an already-running Test Conversation does not silently float to later model selection, Feature, Capability, Tool revision or instruction edits. Starting a new Test Conversation resolves current authored configuration again.

The snapshot does **not** contain live operational secrets/session material:

```text
OpenRouter API credential
Shopify access token/offline-session secret
External HTTP connection credential
credential ciphertext/nonce/authTag/keyId material
```

Those are resolved from current server-owned durable state when required.

### Selected-shop Tool execution

Human Test Conversation Tool calls execute the exact Tool revision from the snapshot through existing production execution infrastructure against the validated selected Shop.

```text
SHOPIFY_ADMIN_GRAPHQL
    -> selected Shop current offline session / access token

EXTERNAL_HTTP
    -> current server-owned connection/credential according to connection scope

POLICY_OPERATION
    -> normal policy-operation executor with selected Shop identity
```

The supported human path does not use synthetic `preview.myshopify.com` identity or fixture Shopify results.

### OpenRouter model execution

For each model invocation in a Test Conversation:

```text
snapshot provider/providerModelId/configuration
        +
current environment OpenRouter credential
        -> Shared OpenRouterModelClient
        -> ChatOpenRouter
        -> OpenRouter
```

The active model is stable for the conversation snapshot. The credential is deliberately live. Replacing the credential can affect the next invocation without restarting Commerce or creating a new Test Conversation.

Trusted instruction order remains deterministic and consumes frozen ARCH-023 semantics:

```text
Shared immutable runner kernel
Test Conversation host safety instruction
Platform Instructions
optional Shop Instructions
response-contract instruction
Feature Behaviours
```

Tool results, Merchant Knowledge, External HTTP responses, customer text and provider output never become trusted `hostInstructions`.

## Production Background Runtime

Background production CommerceAgent turns use the same effective model semantics and Shared OpenRouter client.

Per CommerceAgent turn:

1. resolve trusted Shop/environment;
2. resolve one effective active Catalogue Entry using ARCH-024 rules;
3. keep that selected model identity/configuration stable for the turn;
4. resolve/decrypt the current environment OpenRouter credential for model invocation;
5. execute through Shared `OpenRouterModelClient` and the existing Commerce runner/orchestration.

Background does not import private Commerce source. It must implement the same accepted effective-model semantics using the same database schema and Shared contracts.

ARCH-024 does not refactor existing Background LangGraph/workflow orchestration, conversation ordering, history or admission behaviour.

The existing `GROQ_API_KEY` use for WhatsApp speech transcription is independent and remains where currently required. ARCH-024 only replaces the conversational CommerceAgent model path.

## Gateway / Deployment

ARCH-024 introduces no new Render service, worker, route, database or Redis resource.

After Admin, Commerce and Background no longer depend on the obsolete Preview provider tuple, Gateway removes:

```text
COMMERCE_PREVIEW_PROVIDER
COMMERCE_PREVIEW_MODEL
COMMERCE_PREVIEW_API_KEY
```

and does not replace them with a static `OPENROUTER_API_KEY`/`COMMERCE_OPENROUTER_API_KEY` environment secret.

`COMMERCE_PREVIEW_ENABLED` remains the existing Preview/Test Conversation kill switch with the current test/production policy.

### Encryption keyring

Gateway reuses the accepted external-credential keyring infrastructure from `ARCH-020-GATEWAY-003`.

Each environment exposes one shared keyring group containing:

```text
COMMERCE_CONNECTION_KEYS_JSON
```

only to the authorized Admin, Commerce and production CommerceAgent worker boundaries defined by GATEWAY-001.

Credential writers (Admin and Commerce) additionally receive:

```text
COMMERCE_CONNECTION_ACTIVE_KEY_ID
```

The production Background worker is decrypt-only and does not receive the active-key selector.

Normal OpenRouter credential rotation is a database operation. Encryption-keyring rotation remains a rarer infrastructure operation: add the new key while retaining old referenced keys, distribute the complete keyring, then advance the active key for writers.

## Repository Responsibilities

| Repository | Owner | ARCH-024 responsibility |
|---|---|---|
| `moda-interact-database` | `moda_database` | Availability, Catalogue evolution, encrypted OpenRouter credential, constraints/migration/audit persistence |
| `moda-interact-shared` | `moda_shared` | model/availability/configuration contracts, thin Node OpenRouter/LangChain runtime, publication |
| `moda-interact-admin` | `moda_admin` | Availability administration, Catalogue administration, OpenRouter credential lifecycle |
| `moda-interact-commerce` | `moda_commerce` | Preview cleanup, effective model resolution, Studio model selection, Feature-composed Test Conversations, selected-Shop Tool execution, OpenRouter Test Conversation runtime |
| `moda-interact-background` | `moda_background` | production effective model/OpenRouter CommerceAgent runtime |
| `moda-interact-gateway` | `moda_gateway` | keyring/config-group wiring and obsolete static Preview provider configuration removal |
| `moda-interact` | `moda_app` | **No ARCH-024 implementation task required**; merchants do not select/administer models |
| `moda-interact-system-test` | `moda_system_test` | Terminal integrated validation deliberately deferred to a later architecture session |

## Contracts

### Shared model contract

Owner: `moda-interact-shared`

Package: `@modainteract/moda-interact-shared`

Exports:

```text
@modainteract/moda-interact-shared/commerce/model
@modainteract/moda-interact-shared/commerce/model/node
```

Producers/consumers:

- Database/Admin produce values conforming to the pure model contracts.
- Commerce consumes the pure contracts and Node OpenRouter runtime.
- Background consumes the pure contracts and Node OpenRouter runtime.

Runtime validation:

- Zod model/availability/configuration schemas from the pure entrypoint;
- `OpenRouterModelClient` validates configuration again at construction/invocation boundary.

### Admin -> Commerce model availability contract

Admin writes durable Availability/Catalogue state. Commerce reads only the effective set allowed for the selected Shop. The browser is never authoritative for tenant isolation.

### Commerce -> Test Conversation composition contract

Human Test Conversation start supplies selected Shop plus ordered Feature IDs. Server-side Commerce resolves all Capabilities/Tool revisions/Feature Behaviour and active Agent Configuration facts.

### ARCH-023 instruction dependency

ARCH-024 does not redefine Platform/Shop Instructions. `ARCH-023-COMMERCE-003` remains the frozen owning task for additive trusted Platform + optional Shop instruction resolution used by the Test Conversation chain when that dependency is accepted.

## Consistency and Transactions

- Admin Availability, Catalogue and credential mutations use explicit CAS (`editVersion`) and transactional audit writes.
- Catalogue reassignment/disablement does not rewrite existing Agent Configuration selections.
- Effective model resolution is always recomputed against current durable Availability/Catalogue state.
- Conversation Configuration Snapshot is immutable for the running Test Conversation's authored configuration; live operational credentials are not copied into it.
- OpenRouter credential replacement is an atomic durable state change and is observed by subsequent model invocations without process restart.
- ARCH-024 does not introduce a Redis/database dual-write transaction for model administration.

## Ordering

- No global ordering is introduced for model administration.
- CAS protects concurrent Admin edits to Availability, Catalogue and credential rows.
- A Test Conversation retains the composition/model/instruction snapshot established at Start.
- Production Background preserves existing per-conversation ordering; ARCH-024 does not widen serialization scope.

## Failure Handling

Fail closed for:

- no valid Platform active model when inheritance is required;
- explicit Shop model unavailable/disabled/out-of-scope;
- unavailable Model Availability;
- invalid Catalogue configuration;
- missing OpenRouter credential;
- credential decryption/keyring failure;
- selected Feature with unresolved required Capability/Tool state;
- selected Shop missing required Shopify offline session for a Shopify Tool;
- external connection unavailable for a required Tool;
- OpenRouter/model invocation failure.

Do not silently switch model, Shop, Feature, Capability, Tool revision or provider route to conceal broken explicit application configuration.

Provider errors exposed to product code/UI are bounded and redacted. Secrets and raw credential/provider bodies are not emitted.

## Scalability

ARCH-024 does not change the fundamental CommerceAgent workload boundary: capacity is driven by actual concurrent conversations/model turns rather than raw Shopify webhook volume.

Relevant costs are:

- one bounded effective-model lookup at conversation/turn boundaries as specified by the owning task;
- one current OpenRouter credential lookup/decryption for model invocation;
- existing Tool execution/provider costs;
- existing Redis Preview/conversation storage where retained;
- OpenRouter/provider latency and rate limits.

No new high-cardinality model-catalogue scan is permitted on every token/message. Availability/Catalogue queries must use the indexes defined by DATABASE-001.

## Security

- Admin mutations independently require `SUPER_ADMIN` where specified by the Admin tasks.
- Shop model availability/selection is enforced server-side using canonical `Shop.id`; client filtering is not a security boundary.
- Merchants cannot select or administer models.
- Provider/model configuration cannot inject credentials, headers, arbitrary base URLs, messages, Tools, Tool policy or other reserved runtime capabilities.
- OpenRouter credential plaintext is never returned by Admin APIs and is never stored in Test Conversation snapshots.
- Shopify and External Tool credentials remain server-owned and resolved at execution time.
- Existing trusted-instruction hierarchy from ARCH-023 is preserved.
- Runtime data remains zero-authority input and cannot rewrite trusted instructions or grant Tool authority.

## Observability

No new ARCH-024 observability implementation task is created in this session. Existing structured logging/OpenTelemetry boundaries remain authoritative.

ARCH-024 implementation must preserve enough bounded identifiers to diagnose:

```text
environment
shop ID/domain where safe
model Catalogue Entry ID
provider/providerModelId where non-secret
Availability source/provenance
conversation/run ID
Tool identity/revision
operation IDs / edit versions for Admin mutations
```

Never emit:

```text
OpenRouter credential
credential ciphertext/nonce/authTag
Shopify access token
External connection secrets
authorization headers
full sensitive provider/customer payloads
```

Future integrated validation must include secret-redaction and failure-isolation checks.

## Rollout / Migration

ARCH-024 implementation order is dependency-driven rather than a single serial chain.

Initial independent Ready frontier after this coordination patch:

```text
ARCH-024-DATABASE-001
ARCH-024-COMMERCE-001
```

Expected progression:

```text
DATABASE-001
    -> SHARED-001
    -> SHARED-002 publication

COMMERCE-001 ----------------------------------+
                                               |
DATABASE-001 + SHARED-002 + COMMERCE-001       |
    -> COMMERCE-002                            |
                                               |
DATABASE-001 + SHARED-002                      |
    -> ADMIN-001                               |
    -> ADMIN-002 ------------------------------+-> COMMERCE-003
    -> ADMIN-003                                      |
                                                      v
                                                COMMERCE-004
                                                      |
                                                      v
ARCH-023-COMMERCE-003 ------------------------> COMMERCE-005
                                                      |
                                                      v
                                                COMMERCE-006
                                                      |
SHARED-002 + ADMIN-003 ------------------------> COMMERCE-007

DATABASE-001 + SHARED-002 + COMMERCE-002 + ADMIN-003
    -> BACKGROUND-001

ARCH-020-GATEWAY-003
ADMIN-003
COMMERCE-007
BACKGROUND-001
    -> GATEWAY-001
```

Shared consumer repositories use only the exact architect-accepted/published `ARCH-024-SHARED-002` package revision.

Gateway is deliberately last among the runtime cutover tasks so obsolete static Preview inputs are not removed before Commerce/Background/Admin have adopted the database-backed credential/runtime contract.

## Decisions / Tasks

Individual task YAML is authoritative.

| Task | Owner | Status | Depends On |
|---|---|---|---|
| `ARCH-024-DATABASE-001` | `moda_database` | Ready | - |
| `ARCH-024-SHARED-001` | `moda_shared` | Pending | DATABASE-001 |
| `ARCH-024-SHARED-002` | `moda_shared` | Pending | SHARED-001 |
| `ARCH-024-ADMIN-001` | `moda_admin` | Pending | DATABASE-001, SHARED-002 |
| `ARCH-024-ADMIN-002` | `moda_admin` | Pending | DATABASE-001, SHARED-002, ADMIN-001 |
| `ARCH-024-ADMIN-003` | `moda_admin` | Pending | DATABASE-001, SHARED-002, ADMIN-002 |
| `ARCH-024-COMMERCE-001` | `moda_commerce` | Ready | - |
| `ARCH-024-COMMERCE-002` | `moda_commerce` | Pending | DATABASE-001, SHARED-002, COMMERCE-001 |
| `ARCH-024-COMMERCE-003` | `moda_commerce` | Pending | COMMERCE-002, ADMIN-002 |
| `ARCH-024-COMMERCE-004` | `moda_commerce` | Pending | COMMERCE-003 |
| `ARCH-024-COMMERCE-005` | `moda_commerce` | Pending | COMMERCE-004, ARCH-023-COMMERCE-003 |
| `ARCH-024-COMMERCE-006` | `moda_commerce` | Pending | COMMERCE-005 |
| `ARCH-024-COMMERCE-007` | `moda_commerce` | Pending | COMMERCE-006, SHARED-002, ADMIN-003 |
| `ARCH-024-BACKGROUND-001` | `moda_background` | Pending | DATABASE-001, SHARED-002, COMMERCE-002, ADMIN-003 |
| `ARCH-024-GATEWAY-001` | `moda_gateway` | Pending | ARCH-020-GATEWAY-003, ADMIN-003, COMMERCE-007, BACKGROUND-001 |

No ARCH-024 system-test task is materialised in this session. This is an intentional coordination decision due to overlap with frozen ARCH-023 and upcoming architecture work. Any terminal integrated acceptance work will be defined separately against the final combined architecture.

## Superseded ARCH-021 Phase-6 Work

The following unstarted ARCH-021 tasks are superseded and MUST NOT execute:

```text
ARCH-021-COMMERCE-105
ARCH-021-COMMERCE-106
ARCH-021-COMMERCE-107
ARCH-021-COMMERCE-108
ARCH-021-COMMERCE-109
ARCH-021-GATEWAY-002
ARCH-021-SYSTEM-TEST-004
```

Replacement mapping:

| Superseded task | ARCH-024 replacement |
|---|---|
| ARCH-021-COMMERCE-105 | ARCH-024-COMMERCE-004 |
| ARCH-021-COMMERCE-106 | ARCH-024-COMMERCE-002 + ARCH-024-COMMERCE-007 |
| ARCH-021-COMMERCE-107 | ARCH-024-COMMERCE-005 |
| ARCH-021-COMMERCE-108 | ARCH-024-COMMERCE-006 |
| ARCH-021-COMMERCE-109 | ARCH-024-COMMERCE-001 |
| ARCH-021-GATEWAY-002 | ARCH-024-GATEWAY-001 |
| ARCH-021-SYSTEM-TEST-004 | Deferred future integrated system validation; no ARCH-024 system-test task materialised in this session |

Accepted ARCH-021 work through COMMERCE-104/110 remains baseline functionality and is not reopened by ARCH-024.

## System Validation Deferral

The required integrated validation areas are known but task materialisation is deliberately deferred. The later system-test architecture must cover at least:

- Admin visibility of all Catalogue/Availability state versus Shop-effective visibility in Commerce Studio;
- exactly-one-effective-model selection and Platform inheritance;
- tenant isolation for Shop Availability and Shop selection;
- fail-closed broken explicit Shop overrides;
- OpenRouter execution through the selected model/configuration;
- OpenRouter credential replacement taking effect without Commerce/Background restart;
- Feature selection meaning every direct Capability under each selected Feature;
- exact Tool revision / Feature Behaviour / instruction/model snapshot stability within one Test Conversation;
- real selected-Shop Tool execution;
- production Background parity;
- removal of obsolete human Preview controls;
- credential/secret redaction and telemetry failure isolation.

No implementation/publication/Gateway task depends on a system-test task.

## Open Questions

None blocking implementation.

Future architectural sessions may separately evaluate:

- LangGraph orchestration refactoring after the OpenRouter/model boundary is stable;
- the final integrated system-test decomposition across ARCH-023, ARCH-024 and subsequent overlapping work.

Those are not ARCH-024 implementation scope in this session.

## Change History

- **2026-10-01** — ARCH-024 agreed. Consolidated Admin-owned Model Availability/Catalogue/Credential design, dynamic `provider + providerModelId`, extensible OpenRouter-style model configuration, Shared LangChain/OpenRouter runtime, Commerce Studio selection-only ownership, Feature-composed selected-Shop Test Conversations, production Background parity and Gateway cutover. ARCH-021 COMMERCE-105..109 / GATEWAY-002 / SYSTEM-TEST-004 superseded. ARCH-024 system-test task materialisation deliberately deferred.
