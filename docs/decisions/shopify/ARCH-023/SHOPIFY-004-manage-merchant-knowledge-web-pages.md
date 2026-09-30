---
id: ARCH-023-SHOPIFY-004
architecture_id: ARCH-023
title: Manage Merchant Knowledge web-page sources
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 51
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-SHOPIFY-001
  - ARCH-023-SHARED-002
enables:
  - ARCH-023-SHOPIFY-005
created: 2026-09-29
updated: 2026-09-30
---

# Manage Merchant Knowledge web-page sources

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Implement the merchant-facing Merchant Knowledge management lifecycle for `WEB_PAGE` sources on the existing Recovery Settings page.

The server must enforce the shop's **current materialised** Merchant Knowledge plan configuration on every mutation, persist versioned PENDING source revisions before queue publication, and rely on Background's durable PENDING reconciliation if enqueue fails.

This task also establishes generic source ordering/status read models reused by SHOPIFY-005 for CSV/XLSX.

## Scope

Primary authorized implementation surface:

```text
app/services/merchant-knowledge/merchant-knowledge-entitlement.server.ts
app/services/merchant-knowledge/merchant-knowledge.server.ts
app/services/merchant-knowledge/merchant-knowledge-queue.server.ts

app/routes/app/recovery-settings/route.tsx
app/routes/app/recovery-settings/RecoverySettingsView.tsx
app/components/settings/MerchantKnowledgeSection.tsx

app/routes/app/merchant-knowledge/source/route.ts
app/routes/app/merchant-knowledge/reorder/route.ts
app/routes/app/merchant-knowledge/refresh/route.ts
app/routes/app/merchant-knowledge/delete/route.ts

tests/unit/merchant-knowledge-entitlement.test.ts
tests/unit/merchant-knowledge-actions.test.ts
tests/unit/merchant-knowledge-section.test.tsx
tests/integration/merchant-knowledge-source-lifecycle.integration.test.ts
```

Use localization keys established by SHOPIFY-002 when available on merged main; do not create another key naming convention.

## Out of Scope

- R2 signed uploads and CSV/XLSX (SHOPIFY-005).
- URL fetching.
- SSRF network validation beyond public-HTTPS syntax.
- extraction/chunking/embedding.
- Commerce Tool/capability creation.
- automatic scheduled refresh.
- source-type entitlement from pending future plans.
- deleting dormant/excess sources automatically.

## Requirements

### R1 — one authoritative current-plan entitlement resolver

Implement:

```ts
loadCurrentMerchantKnowledgeEntitlement(shopId)
```

Use:

```text
Subscription.status IN (ACTIVE, TRIALING)
Subscription.planId/current plan only
BillingPlan.active = true
BillingPlanFeature.enabled = true
Feature.key = merchant_knowledge
Feature.active = true
```

Parse:

```text
BillingPlanFeature.configuration
```

with Shared `MerchantKnowledgeFeatureConfigurationSchema`.

Ignore:

```text
pendingPlanId
pendingShopifyPlanHandle
pendingEffectiveAt
ShopFeaturePreference
```

No qualifying current mapping -> entitlement unavailable.

Malformed C2 -> fail closed with configuration error; do not substitute defaults.

### R2 — load active global source-type catalogue

Load active:

```text
MerchantKnowledgePurpose
MerchantKnowledgeDataFormat
MerchantKnowledgePurposeDataFormat
```

and intersect it with current `allowedSourceTypes`.

Purpose selector options are only purposes with at least one entitled format.

Data Format options for a selected purpose are the exact active/intersection formats.

No plan display name/handle/kind conditional is allowed.

### R3 — source entitlement/read model

Load all persisted shop sources ordered:

```text
position ASC, id ASC
```

For each source calculate:

```text
globallySupported
sourceTypeAllowed
allowedOrdinal among only globally-supported + allowedSourceTypes sources
withinSourceAllowance = allowedOrdinal < maxKnowledgeSources
currentlyEntitled = all above
```

A disallowed source type does not consume an active slot.

Expose:

```ts
{
  id,
  name,
  purposeKey,
  dataFormatKey,
  languageTag,
  position,
  configuredLocator,
  currentlyEntitled,
  dormantReason: null | "SOURCE_TYPE" | "SOURCE_COUNT" | "NO_CURRENT_PLAN",
  currentGeneration,
  currentRevisionStatus,
  activeRevision: {
    contentUnits,
    truncated,
    completedAt,
    requestedUrl
  } | null
}
```

For WEB_PAGE `configuredLocator` comes from the revision at `currentGeneration`, not necessarily the ACTIVE predecessor.

Do not expose normalized content/chunks/vectors.

### R4 — public HTTPS syntax validator

At Shopify mutation boundary require:

```text
raw length <= 2048
new URL(input) succeeds
protocol === "https:"
username === ""
password === ""
```

Persist canonical:

```text
url.toString()
```

Do not perform DNS/network SSRF checks here; Background owns them.

### R5 — create WEB_PAGE source transaction

Input:

```text
name
purposeKey
dataFormatKey = WEB_PAGE
languageTag
url
```

Validation:

```text
name trimmed 1..160
languageTag parses Shared ModaSupportedLanguageTag
purpose/data format exact current entitled pair
data format inputKind = REMOTE_URL
```

Transaction:

1. lock Shop row;
2. re-resolve current entitlement and active pair catalogue inside transaction;
3. count only currently allowed source rows after source-type filtering;
4. require count `< maxKnowledgeSources`;
5. allocate:
   ```text
   position = max(existing source.position) + 1
   ```
   or `0` when none;
6. create source:
   ```text
   currentGeneration = 1
   ```
7. create exactly one revision:
   ```text
   generation = 1
   reason = CREATE
   requestedUrl = canonical URL
   uploadedAssetId = null
   status = PENDING
   requestedAt = now
   ```
8. commit;
9. enqueue C4 best effort using exact Shared deterministic job id.

Queue failure must leave the durable PENDING revision unchanged.

### R6 — edit WEB_PAGE metadata/URL

Existing source immutable fields after creation:

```text
purposeId
dataFormatId
```

Editable metadata:

```text
name
languageTag
```

URL is configured locator and may change.

Transaction locks source and validates shop ownership/current entitlement.

If canonical URL unchanged:

```text
update name/language only
no new revision
```

If URL changed:

1. increment `currentGeneration` exactly once;
2. update name/language;
3. insert:
   ```text
   reason = URL_CHANGE
   status = PENDING
   requestedUrl = new canonical URL
   generation = new currentGeneration
   ```
4. keep prior ACTIVE revision/chunks unchanged;
5. commit;
6. enqueue best effort.

### R7 — Refresh

Refresh input:

```text
sourceId
```

Require owned source, WEB_PAGE and currently entitled.

Load revision whose:

```text
generation = source.currentGeneration
```

Require `requestedUrl != null`.

Transaction increments generation and creates one:

```text
reason = REFRESH
status = PENDING
requestedUrl = exact current-generation requestedUrl
```

Prior ACTIVE remains unchanged until Background succeeds.

Commit then enqueue best effort.

### R8 — delete source

Delete only an owned source.

Transaction:

1. lock Shop/source ordering scope;
2. delete source (database cascades its revisions/chunks);
3. compact remaining shop source positions to exact:
   ```text
   0..N-1
   ```
   preserving prior `(position ASC,id ASC)` order.

Use a collision-safe two-phase position update because `(shopId,position)` is unique.

No other source's generation changes.

WEB_PAGE delete has no R2 cleanup concern.

### R9 — reorder all persisted sources

Input:

```text
orderedSourceIds: string[]
```

Require exact set equality with all current persisted source ids for that shop:

```text
no missing
no extra
no duplicate
```

Transaction locks Shop ordering scope and rewrites positions to:

```text
0..N-1
```

using collision-safe temporary positions.

Reordering is allowed for dormant/excess sources because their persisted order determines future first-N entitlement.

No revision is created by reorder.

### R10 — queue publication helper

Create one helper:

```ts
enqueueMerchantKnowledgeRevisionBestEffort({
  shopId,
  sourceRevisionId,
  generation,
  requestedAt
})
```

It uses exactly:

```text
MERCHANT_KNOWLEDGE_QUEUE_NAME
MERCHANT_KNOWLEDGE_PROCESS_JOB_NAME
MerchantKnowledgeProcessSourceRevisionJobSchema
createMerchantKnowledgeProcessJobId
```

and the repository's existing Redis/BullMQ connection convention.

Do not create a separate reconciliation request. Background scans durable PENDING rows.

Do not throw after commit solely because enqueue failed; emit bounded diagnostic.

### R11 — Recovery Settings UI

Add `Merchant Knowledge` section after Store Profile and before existing recovery-specific settings.

Show:

```text
configured currently-allowed count / maxKnowledgeSources
maxContentUnitsPerSource
source list in position order
current entitlement/dormancy
purpose localized label
data format localized label
language
WEB_PAGE URL
current revision status
active content-unit usage / max
truncated indicator
last processed timestamp
```

Actions for WEB_PAGE:

```text
Add
Edit
Refresh
Delete
Move up/down (or equivalent deterministic reorder)
```

The Add/Edit form builds Purpose/Data Format selectors from R2 intersection data.

In this task only `WEB_PAGE` is actionable. CSV/XLSX pairs may be shown as "Upload support pending" until SHOPIFY-005 lands, or hidden from the Add form while preserving server catalogue data.

### R12 — source language default

New-source language defaults to:

```text
resolveModaConfigurationLocale(ShopSettings.defaultLanguageTag)
```

Merchant may select any of the exact 20 Shared supported tags.

Customer conversation language does not affect this form.

### R13 — concurrency

Create/reorder/delete operations lock the Shop source-ordering scope.

Concurrent creates must not both allocate the same slot or exceed `maxKnowledgeSources`.

Concurrent source revision operations lock the source and increment `currentGeneration` exactly once per committed new revision.

### R14 — tests

Prove:

```text
pending future plan ignored
no current active/trialing plan -> unavailable
C2 malformed -> fail closed
disallowed pair rejected
inactive global pair rejected
source-type filtering precedes maxKnowledgeSources
concurrent creates cannot exceed limit
second URL for same purpose allowed when slots permit
purpose/dataFormat immutable after create
name/language edit without URL change creates no revision
URL change creates URL_CHANGE while old ACTIVE remains
Refresh uses current configured URL and creates REFRESH
enqueue failure leaves PENDING
delete compacts positions
reorder exact-set/CAS concurrency behavior
dormant/excess source retained
no ShopFeaturePreference consulted
no extracted content/vector returned to UI
```

## Work Items

- [ ] Implement current entitlement/catalogue resolver.
- [ ] Implement source read model.
- [ ] Implement WEB_PAGE create/edit/refresh/delete/reorder transactions.
- [ ] Implement deterministic queue publication helper.
- [ ] Add Merchant Knowledge Recovery Settings UI.
- [ ] Add source-language default/selector.
- [ ] Add focused unit/integration/component tests.

## Interfaces / Contracts

Consumes:

```text
BillingPlanFeature.configuration from SHOPIFY-001 materialisation
Shared C1-C4
ARCH-023 database models
```

Produces C4 jobs for Background.

## Dependencies

- `ARCH-023-SHOPIFY-001`
- `ARCH-023-SHARED-002`

Resolved Shared release for this task: `@modainteract/moda-interact-shared@1.0.1`. Do not substitute a range, `latest`, workspace link or later release without architect reconciliation.

## Enables

- `ARCH-023-SHOPIFY-005`

## Acceptance Criteria

- [ ] Every mutation re-checks current materialised entitlement.
- [ ] Source-type filtering happens before active source-count limit.
- [ ] WEB_PAGE lifecycle is fully revisioned and queue-loss safe.
- [ ] Existing ACTIVE content remains while replacement/refresh is pending.
- [ ] Dormant/excess sources are retained.
- [ ] UI lives on existing Recovery Settings page.
- [ ] No Background/Commerce execution is implemented.

## Validation

- [ ] focused entitlement/action tests
- [ ] DB concurrency integration tests
- [ ] Recovery Settings component/route tests
- [ ] `npm run typecheck`
- [ ] `npm run lint`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP. Do not begin SHOPIFY-005.

## Completion Report

### Status
Not Started
### Files Changed
None.
### Work Completed
None.
### Validation Results
None.
### Deviations
None.
### Assumptions
None.
### Unresolved Issues
None.
### Architectural Concerns
None.

## Architect Review

### Review Status
Pending
### Review Notes
Pending.
### Reviewed Files
Pending.
### Validation Reviewed
Pending.
### Architecture Conformance
Pending.
### Follow-up
Pending.
