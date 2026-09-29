---
id: ARCH-021-COMMERCE-099
architecture_id: ARCH-021
title: Round-trip and save persisted Policy Operation Tool drafts
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-097
  - ARCH-021-COMMERCE-098
enables:
  - ARCH-021-COMMERCE-100
created: 2026-09-29
updated: 2026-09-29
---
# Round-trip and save persisted Policy Operation Tool drafts

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Integrate the COMMERCE-097 Policy Operation editor and COMMERCE-098 live-Test backend into the canonical persisted-DRAFT authoring-session lifecycle so an existing `POLICY_OPERATION` Tool can be opened, edited in-memory, validated, live-tested, CAS-saved, remounted and restored without changing its fixed operation/version binding.

## Context

COMMERCE-097 supplies the local persisted Policy Operation authoring surfaces. COMMERCE-098 supplies one non-durable production-path live-Test backend. This task connects them to the accepted ARCH-021 persisted authoring-session validation/Test freshness and draft-save lifecycle.

This task is the first task that may durably update an existing Policy Operation DRAFT. It does not create a new Policy Operation Tool identity and does not publish the revision.

## Scope

Primary implementation areas:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring-session.ts or accepted persisted-session equivalent
src/studio/tools/<policy-operation editor components from C097>
src/studio/tools/<policy-operation live-test action from C098>
existing updateToolDraft / Commerce lifecycle boundary
focused persisted-authoring tests
```

## Out of Scope

- New Tool creation for `POLICY_OPERATION`.
- Rebinding `operation` or `operationVersion`.
- Publishing the DRAFT; COMMERCE-100 owns publication/reopen regression.
- Implementing a policy operation.
- ARCH-023 Merchant Knowledge code.
- Changing External HTTP/Shopify Admin Save/Test semantics.
- Creating another authoring session store or Test freshness model.

## Requirements

### R1 — use the canonical persisted authoring session

Policy Operation authoring must consume the same accepted persisted Tool authoring session/validation ledger/Test freshness model used by the other providers.

Do not introduce Policy-specific authoritative copies of:

```text
dirty
validated
testPassed
testedSnapshot
editVersion
current section
```

Provider-specific transient literal-text/display state may be local, but Save/Test readiness comes from the common authoring session.

### R2 — exact candidate assembly

At every Validate/Test/Save boundary, assemble one current `CommerceToolDefinition` containing exactly:

```text
name                   persisted immutable Tool name
definitionVersion      current editor value
description            current editor value
inputSchema             current Request value
execution.kind          POLICY_OPERATION
execution.operation     original persisted operation
execution.operationVersion original persisted operationVersion
execution.arguments     current Request mappings
responseTemplate        current Result Template value
```

No boundary may build a second stale provider-specific candidate from duplicated buffers.

The original operation/version pair captured from the loaded revision is an invariant for the session. If local state attempts to change either value, validation and Save fail closed.

### R3 — deterministic authored-section validation

The common section ledger must represent current validity for:

```text
Tool Definition
Request
Response
Result Template
```

Policy Operation validation responsibilities are:

```text
Tool Definition
  -> normal identity/description/definitionVersion validation

Request
  -> CommerceToolDefinition inputSchema restrictions
  -> C096 descriptor available for exact operation/version
  -> required/optional operation mappings valid against descriptor.argumentsSchema
  -> literals valid and bounded
  -> mapped Tool input properties exist

Response
  -> exact descriptor.resultSchema is available/current; no editable provider response transform

Result Template
  -> existing Result Template validator against descriptor.resultSchema
```

Changing a value owned by an earlier section must stale the appropriate downstream validation/Test checkpoint using the existing authoring-session rules.

### R4 — one Policy Operation Test tab integrated with common Test freshness

Add one reusable Policy Operation Test surface for persisted DRAFTs.

Before invoking COMMERCE-098 require:

```text
Tool Definition current VALID
Request current VALID
Response current VALID
Result Template current VALID
complete current candidate parses
selected shopId present
Test arguments valid JSON object
Test arguments within the common bounded size
```

Do not automatically validate missing/stale sections when Test is pressed. Show the same owning-step style used by accepted provider flows.

Test lifecycle must use the common equivalent of:

```text
NOT_RUN
RUNNING
PASSED
FAILED
STALE
```

with the common authored-section snapshot. Editing any candidate field after a successful Test makes that Test stale.

### R5 — Test displays canonical C098 output

The Policy Operation Test tab sends exactly:

```ts
{
  definition: currentCandidate,
  arguments: parsedTestArguments,
  shopId: selectedShopId,
}
```

to COMMERCE-098.

Show `renderedText` as the primary successful agent-facing result and bounded structured status/diagnostics as secondary information. Do not directly call an adapter from React/Server Action UI code.

### R6 — Save uses the existing CAS draft lifecycle

Save an existing Policy Operation DRAFT only through the canonical `updateToolDraft`/Commerce lifecycle operation with:

```text
toolRevisionId = currently selected DRAFT id
expectedEditVersion = loaded/current CAS editVersion
definition = exact current candidate
```

Use the existing structured operation/audit reason convention.

Save must not:

```text
create a new Tool identity
change operation
change operationVersion
publish the revision
create a release
create a conversation grant
```

### R7 — Save requires the canonical current Test checkpoint

Apply the accepted provider Save/Test gate consistently:

```text
all owned authored sections current VALID
AND
current candidate Test status == PASSED for the exact current snapshot
```

A stale/failed/not-run Test prevents Save and shows an actionable Test-owned message.

Do not invent a weaker Policy Operation Save rule.

### R8 — CAS conflict and unknown outcome preserve user work

On a stale edit-version conflict or unknown mutation outcome:

```text
do not silently replace local candidate
show the existing explicit conflict/refresh recovery path
operation/version remain fixed
no implicit retry that may overwrite another editor
```

Follow the accepted persisted-DRAFT CAS semantics; do not create Policy-specific reconciliation behaviour.

### R9 — remount/return round-trip is exact

After a successful Save and subsequent remount/reselection of the DRAFT, restore exactly:

```text
description
definitionVersion
inputSchema
operation
operationVersion
argument mappings
responseTemplate
editVersion returned by Save
```

No field may fall back to a Shopify/External default simply because the editor remounted.

Opening an existing persisted Policy Operation revision performs no write.

## Work Items

- [ ] Connect Policy Operation local editor state to the common persisted authoring session.
- [ ] Add deterministic section validation/freshness propagation.
- [ ] Integrate one Policy Operation Test tab with COMMERCE-098 and common Test state.
- [ ] Gate Save on current validation plus current successful Test.
- [ ] Save through canonical CAS `updateToolDraft` without changing operation/version.
- [ ] Preserve local work on CAS conflict/unknown outcome using the existing recovery model.
- [ ] Add exact save/remount/round-trip regressions.
- [ ] Add no-write-on-open and no-rebind regressions.

## Interfaces / Contracts

Consumes:

- COMMERCE-097 Policy Operation authoring UI;
- COMMERCE-098 live-Test action;
- canonical persisted authoring-session/Test state;
- canonical Tool DRAFT CAS lifecycle.

Produces no new cross-service contract.

## Dependencies

- `ARCH-021-COMMERCE-097`
- `ARCH-021-COMMERCE-098`

## Enables

- `ARCH-021-COMMERCE-100`

## Acceptance Criteria

- [ ] Existing `POLICY_OPERATION` DRAFT opens with exact persisted operation/version and no write.
- [ ] All editable Policy Operation fields participate in the common validation/Test freshness model.
- [ ] Operation/version cannot be rebound in Studio.
- [ ] Test executes the exact current candidate through COMMERCE-098.
- [ ] Editing after Test makes the checkpoint stale.
- [ ] Save is blocked until all owned sections are current-valid and the exact current candidate has a PASSED Test.
- [ ] Save uses the canonical DRAFT CAS operation and preserves operation/version.
- [ ] CAS conflict/unknown outcome does not silently overwrite local work.
- [ ] Successful Save/remount restores the exact saved Policy Operation candidate and returned editVersion.
- [ ] No new Tool identity, publication, release or grant is created by Save.
- [ ] Existing External HTTP and Shopify Admin Save/Test flows are unchanged.

## Validation

- [ ] Focused persisted Policy Operation editor/round-trip tests.
- [ ] Focused Test freshness/stale-after-edit tests.
- [ ] Focused CAS conflict/unknown-outcome tests.
- [ ] Focused no-rebind/no-write-on-open tests.
- [ ] Existing provider regression packet required by the current Tool editor.
- [ ] Targeted TypeScript diagnostics for changed files.
- [ ] Targeted ESLint for changed files.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin COMMERCE-100.

## Implementation Notes

The fixed operation binding is intentional. Studio is authoring a revision of a Tool that invokes Moda-owned code; Studio is not a backend function IDE and does not own operation registration.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
