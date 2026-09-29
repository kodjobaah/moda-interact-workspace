---
id: ARCH-021-COMMERCE-083
architecture_id: ARCH-021
title: Integrate Shopify Admin Test and show the populated Result Template
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 75
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-078
  - ARCH-021-COMMERCE-079
  - ARCH-021-COMMERCE-081
  - ARCH-021-COMMERCE-082
  - ARCH-021-COMMERCE-085
enables:
  - ARCH-021-SYSTEM-TEST-002
created: 2026-09-28
updated: 2026-09-28
---

# Integrate Shopify Admin Test and show the populated Result Template

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Integrate the already-implemented COMMERCE-082 Shopify Admin live-Test backend into the canonical new/persisted authoring-session Test-freshness model, replace the Shopify Test placeholder with one reusable Test surface, show the server-rendered populated Result Template as the primary result, and require a current successful Shopify Test before Create/Save may persist the current Shopify candidate.

## Context

COMMERCE-082 is Complete and supplies the canonical non-durable Shopify Admin live-Test backend. It validates the complete candidate, resolves the selected shop server-side, reuses the production Admin execution port/result normalization, validates the current Result Template, and returns server-rendered agent text without creating publication proof or durable Tool state.

COMMERCE-078 owns the central authored-section validation ledger and common Test freshness model. COMMERCE-079 applies the same model to persisted DRAFTs. COMMERCE-081 establishes the provider-aware Save/Test integration pattern for External HTTP. This task applies the same accepted pattern to Shopify Admin; it must preserve External behaviour and must not introduce a second Test-readiness authority.

The current uploaded snapshot's parent task record marks COMMERCE-082 Complete/Accepted, but the uploaded `moda-interact-commerce` checkout does not contain the C082 implementation files named in that Completion Report. This is an integration-state discrepancy, not permission to recreate C082. See R1.

## Scope

Primary implementation areas:

```text
src/studio/tools/new-tool-editor.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/shopify-admin-test-tab.tsx      # one new reusable component
src/studio/tools/shopify-admin-live-test-server-actions.ts  # consume C082 implementation
src/studio/tools/<C078 authoring-session module>           # consume; do not create competing store
```

Focused tests:

```text
tests/shopify-admin-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
tests/shopify-admin-live-test-action.test.ts
```

## Out of Scope

- Reimplementing or changing COMMERCE-082 backend execution semantics.
- Creating a second Shopify live-Test Server Action, GraphQL transport or result contract.
- Changing C078 validation/Test state semantics or creating a competing Test store.
- Changing C079 persisted CAS/persistence-dirty semantics.
- External Test UI or External Save gate; COMMERCE-081 owns them.
- Publication proof or `LIVE_TEST_REQUIRED` publication-gate changes.
- Automatic persistence after Test.
- GraphQL Request authoring or Response/result-contract derivation changes.
- Rendering/interpolating Result Template tokens in React.

## Requirements

### R1 — verify the accepted C082 implementation is physically present; do not recreate it

Before making any source change, verify that the implementation repository available to this task contains the accepted COMMERCE-082 capabilities from its Completion Report, including semantic equivalents of:

```text
src/commerce/tool-authoring/shopify-admin-live-test.ts
src/studio/tools/shopify-admin-live-test-server-actions.ts
Shopify Admin live-Test input/result types
ADMIN-authorized Test Server Action
CommerceBackend Admin execution-port exposure
```

If the parent task metadata says COMMERCE-082 is Complete but those accepted capabilities are not present in the implementation branch/worktree used for C083:

```text
DO NOT implement them again.
DO NOT copy C082 from its task document.
DO NOT create a substitute action/transport.
```

Instead:

```text
set C083 status to blocked
record the missing integrated C082 implementation as the blocker
return control to moda_architect
STOP
```

The developer must integrate/update the implementation repository to the accepted C082 commit before C083 continues.

### R2 — consume the canonical C078/C079 Test state and the provider-aware C081 Save pattern

Use the accepted C078/C079 authoring-session Test checkpoint with these semantics:

```ts
type AuthoringTestStatus =
  | "NOT_RUN"
  | "RUNNING"
  | "PASSED"
  | "FAILED"
  | "STALE";

type AuthoringTestSnapshot = {
  toolDefinitionRevision: number;
  requestRevision: number;
  responseRevision: number;
  resultTemplateRevision: number;
};

type AuthoringTestState = {
  status: AuthoringTestStatus;
  testedSnapshot: AuthoringTestSnapshot | null;
};
```

Consume the actual accepted exports/operations equivalent to:

```text
currentAuthoringSnapshot(session)
isCurrentTestPassed(session)
mark Test RUNNING for submitted snapshot
mark Test PASSED for submitted snapshot
mark Test FAILED for submitted snapshot
mark Test STALE / clear testedSnapshot
```

Do not create a Shopify-specific authoritative `testPassed`, `dirty`, `validated` or Test snapshot store.

Provider-specific display result/diagnostics may be local to `ShopifyAdminTestTab`, but Review/Save readiness must use only the common authoring Test checkpoint.

If those common capabilities are missing despite dependencies being Complete, STOP and report a dependency defect instead of duplicating them.

### R3 — one reusable `ShopifyAdminTestTab` for new and persisted authoring

Create exactly one reusable component:

```text
ShopifyAdminTestTab
```

(or mechanically equivalent single shared component) and use it for both:

```text
new Shopify Admin Tool
persisted Shopify Admin DRAFT
```

Do not implement two provider-Test components with separate freshness/run/result logic.

The parent editor supplies the assembled candidate, common Test/session operations, selected shop, Test arguments and disabled/locked state. The component owns only provider-specific transient Test input/result presentation.

### R4 — Test consumes the exact current assembled candidate

Immediately before running Test, obtain the same complete definition that Review/Create/Save would persist.

The Shopify definition must contain exactly the current values for:

```text
Tool Definition:
  name
  definitionVersion
  description

Request:
  inputSchema
  execution.apiVersion
  execution.schemaHash
  execution.document
  execution.operationName
  execution.variables

Response:
  execution.resultPath
  execution.resultSchema / compiler-derived current result contract fields

Result Template:
  responseTemplate
```

Do not construct a second partial candidate inside `ShopifyAdminTestTab` from stale duplicated buffers when the authoring session already exposes the current assembled definition.

Pass to the accepted C082 Server Action exactly:

```ts
{
  definition: CommerceToolDefinition;
  arguments: Record<string, unknown>;
  shopId: string;
}
```

The browser must never supply:

```text
shop domain
Shopify access token
offline-session credential
Authorization header
```

### R5 — exact local prerequisites before provider Test

Do not invoke the C082 Server Action unless all four authored sections are current VALID according to the common validation ledger:

```text
Tool Definition  current VALID
Request          current VALID
Response         current VALID
Result Template  current VALID
```

Also require:

```text
complete assembled Shopify definition parses through the canonical Tool definition boundary
selected shopId is a non-empty string
Test arguments are valid JSON
Test arguments are a JSON object
Test arguments serialized input is <= 64 KiB
```

Do **not** automatically run missing validations from Test.

Show exactly these owning-step messages for authored prerequisites:

```text
Tool Definition invalid/stale -> "Return to Tool Definition and validate the current values."
Request invalid/stale         -> "Return to Request and validate the current values."
Response invalid/stale        -> "Return to Response and validate the current values."
Result Template invalid/stale -> "Return to Result Template and validate the current values."
shopId absent                 -> "Select a Studio shop before running Test."
```

Invalid Test arguments remain on Test with the bounded local JSON error.

No message may refer the user to Agent Contract.

### R6 — exact common Test lifecycle and stale-response protection

Immediately before the C082 backend call:

1. Obtain the exact assembled current Shopify definition.
2. Capture:

```ts
const submittedSnapshot = currentAuthoringSnapshot(session);
```

3. Capture one provider-local run identity from exactly:

```text
submittedSnapshot
Test arguments text
selected shopId
```

4. Mark the common session Test state `RUNNING` for `submittedSnapshot`.
5. Invoke the accepted C082 live-Test Server Action exactly once.

The Test is PASSED only when all of the following are true:

```text
Server Action result.kind === "ok"
candidateValidation.status === "passed"
shopResolution.status === "passed"
providerRequest.status === "passed"
resultValidation.status === "passed"
resultRendering.status === "passed"
renderedText is a string
```

If the submitted authoring snapshot and provider-local run identity still match current state, set:

```text
common Test status = PASSED
common testedSnapshot = submittedSnapshot
```

If the Server Action returns an error or any required C082 stage is not `passed`, and the submitted identity is still current, set:

```text
common Test status = FAILED
common testedSnapshot = submittedSnapshot
```

If any authored section, Test arguments or selected shop changes while the request is in flight, the response is stale and must not modify readiness for the current candidate:

```text
common Test status = STALE
common testedSnapshot = null
ignore/discard the late result for current-candidate readiness
```

Use a monotonically increasing run sequence or equivalent existing deterministic stale-response mechanism. Run N must never overwrite run N+1.

### R7 — deterministic Shopify Test staleness

C078/C079 own staleness caused by authored-section edits. Do not duplicate those revision rules in `ShopifyAdminTestTab`.

Shopify Test must additionally mark the common Test STALE and clear its displayed provider result whenever either changes:

```text
Test arguments text
selected shopId
```

Tab navigation alone must not stale the Test.

Use the common stale state exactly:

```text
status = STALE
testedSnapshot = null
```

Test arguments/shop are transient Test context only. Changing them must not mark a persisted DRAFT persistence-dirty.

### R8 — primary output is the exact server-rendered agent result

On a successful Test, render this section before normalized values or stage diagnostics:

```tsx
<section aria-label="Result shown to agent">
  <h4>Result shown to agent</h4>
  <pre>{renderedText}</pre>
</section>
```

The displayed text must equal the C082 server-returned `renderedText` exactly. React must not parse, interpolate or rerender the authored Result Template.

After the primary result, display only safe secondary diagnostics returned by C082:

```text
candidateValidation stage
shopResolution stage
providerRequest stage
resultValidation stage
resultRendering stage
processedResult / normalized values
```

Do not expose raw access tokens, Authorization headers, offline-session records, unbounded GraphQL responses or credential material.

### R9 — Shopify Create/Save requires a current PASSED Test

Preserve the External provider gate already implemented by COMMERCE-081.

For a new Shopify Tool:

```ts
canCreateShopify =
  existingC078NewToolSaveEligibility &&
  isCurrentTestPassed(session);
```

For a persisted Shopify DRAFT:

```ts
canSaveShopifyDraft =
  existingC079PersistedSaveEligibility &&
  isCurrentTestPassed(session);
```

Do not replace the existing C078/C079 eligibility predicates. Add the current Test requirement.

The exact Test consequences are:

```text
NOT_RUN -> Create/Save disabled
RUNNING -> Create/Save disabled
FAILED  -> Create/Save disabled
STALE   -> Create/Save disabled
PASSED for an older snapshot -> Create/Save disabled
PASSED for current snapshot -> Test requirement satisfied
```

Review remains accessible in every state. Do not enforce sequential Next/Previous wizard navigation.

After this task, both supported provider kinds must therefore require a current successful Test before persistence:

```text
EXTERNAL_HTTP         -> C081 current Test gate
SHOPIFY_ADMIN_GRAPHQL -> C083 current Test gate
```

### R10 — Test remains non-durable and separate from publication proof

Running Shopify Test, changing Test arguments/shop, displaying diagnostics, marking Test PASSED/FAILED/STALE or navigating Test/Review performs zero:

```text
createToolWithInitialDraft
updateToolDraft
Tool/ToolRevision write
audit write
operation-receipt write
publication-proof write
```

A successful authoring Test does not satisfy or alter the existing publication `LIVE_TEST_REQUIRED` gate. Exact-saved-revision publication proof remains separately owned.

For persisted DRAFTs, Test-only state changes must not set persistence-dirty.

### R11 — preserve existing authoring flows

The Shopify Test integration must not regress:

```text
Request -> Explore Shopify -> Use in tool -> Request round-trip
Request validation/mapping state
Response resultPath/result-contract derivation
Result Template validation
read-only derived Agent Contract in Review
new Tool single atomic Create/Save boundary
persisted one-CAS Save boundary
Cancel semantics
```

Do not auto-save after Explore, Response derivation, template validation or Test.


### R7 — drive the C078 common Test checkpoint for new Tools

For the new-Tool Shopify Admin flow, C083 MUST consume the C078 common Test freshness model rather than create a second canonical pass/freshness checkpoint.

On Test start capture the exact C078 `currentAuthoringSnapshot(session)` and transition the common session Test state to `RUNNING`.

On C082 success complete the checkpoint with `PASSED`; on C082 failure complete it with `FAILED`.

If any Tool Definition, Request, Response or Result Template revision changed while C082 was running, the completion must become:

```text
status = STALE
testedSnapshot = null
```

and the provider result must not mark the current candidate passed.

The reusable Shopify Admin Test component may retain bounded provider-specific result/stage diagnostics separately. Those payloads must not be copied into the C078 common `test` state.

Use `isCurrentTestPassed(session)` for new-Tool current-pass decisions. Persisted-DRAFT Test freshness remains governed by the persisted authoring state model introduced by C079; do not force the new-Tool session object into persisted DRAFTs.

## Work Items

- [ ] Verify accepted C082 source capability is physically present; block instead of recreating it if integration is missing.
- [ ] Add exactly one reusable `ShopifyAdminTestTab` for new and persisted Shopify authoring.
- [ ] Consume C078/C079 common Test state; do not create a Shopify-specific authoritative Test store.
- [ ] Pass the exact assembled current Shopify definition + arguments + shopId to the accepted C082 action.
- [ ] Gate Test execution on current VALID Tool Definition, Request, Response and Result Template.
- [ ] Capture the current authoring snapshot and provider-local run identity before each backend invocation.
- [ ] Drive common RUNNING/PASSED/FAILED/STALE transitions exactly as specified.
- [ ] Stale Test on Test-argument or selected-shop changes without changing persisted-draft dirtiness.
- [ ] Preserve concurrent-run/stale-response protection.
- [ ] Render `Result shown to agent` first from C082 `renderedText`.
- [ ] Keep only safe C082 stages/normalized values as secondary diagnostics.
- [ ] Add current Test PASSED to new Shopify Create eligibility.
- [ ] Add current Test PASSED to persisted Shopify Save eligibility without changing C079 persistence/CAS rules.
- [ ] Preserve the External current-Test Save gate from C081 unchanged.
- [ ] Prove Test remains non-durable and does not satisfy publication proof.
- [ ] Add all required new/persisted Shopify regressions.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-078
  authored-section validation ledger
  common AuthoringTestState / snapshot semantics
  new-Tool assembled candidate and Save eligibility

ARCH-021-COMMERCE-079
  persisted authoring-session parity
  persisted assembled candidate
  persistence-dirty/CAS Save eligibility

ARCH-021-COMMERCE-081
  provider-aware current-Test Save-gating pattern
  preserved External provider behaviour

ARCH-021-COMMERCE-082
  accepted Shopify Admin live-Test domain service
  accepted ADMIN-authorized Server Action
  ShopifyAdmin live-Test input/result contract
  server-produced renderedText
```

No new database, Shared, queue or cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-078
- ARCH-021-COMMERCE-079
- ARCH-021-COMMERCE-081
- ARCH-021-COMMERCE-082
- ARCH-021-COMMERCE-085

## Enables

- ARCH-021-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] The task blocks rather than recreating C082 if the accepted C082 implementation is not physically present in its implementation worktree.
- [ ] Exactly one reusable Shopify Admin Test component serves new and persisted Shopify authoring.
- [ ] No second authoritative Shopify Test/dirty/validated state exists outside the common authoring session.
- [ ] Test cannot invoke C082 while any authored section is not current VALID.
- [ ] Test sends the exact current assembled Shopify definition, arguments and server-resolved-shop identifier input; browser supplies no domain/token.
- [ ] Test start captures the current section-revision snapshot and marks common Test RUNNING.
- [ ] Only a response with every C082 stage passed and server `renderedText` present may mark current Test PASSED.
- [ ] Backend/action failure marks the matching current Test FAILED.
- [ ] Authoring/Test-context changes during an in-flight call prevent the late response from changing current readiness.
- [ ] Authored section edits stale Test through C078/C079; argument/shop changes additionally stale Test locally/common-state without setting persistence-dirty.
- [ ] Successful Test displays exact server `renderedText` first under `Result shown to agent`.
- [ ] Safe normalized result/stages remain secondary and credential-safe.
- [ ] New Shopify Create requires all existing C078 gates plus a current PASSED Test.
- [ ] Persisted Shopify Save requires all existing C079 gates plus a current PASSED Test.
- [ ] Existing External Save/Test gating from C081 is unchanged.
- [ ] Review is navigable while Test is NOT_RUN/RUNNING/FAILED/STALE.
- [ ] Test performs zero Tool/draft/audit/receipt/publication-proof mutation and does not satisfy `LIVE_TEST_REQUIRED` publication proof.
- [ ] Existing Explore/Request/Response/Result Template/Review/Cancel/CAS behaviour remains intact.

## Validation

- [ ] `npx vitest run tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/shopify-admin-live-test-action.test.ts`
- [ ] New Tool: all four sections current VALID + Shopify Test NOT_RUN -> Create disabled.
- [ ] New Tool: current successful Shopify Test -> Create enabled when all other C078 gates pass.
- [ ] New Tool: edit Request after PASS -> common Test STALE -> Create disabled.
- [ ] New Tool: edit Result Template after PASS -> common Test STALE -> Create disabled.
- [ ] New Tool: change selected shop or Test arguments after PASS -> common Test STALE -> Create disabled.
- [ ] Persisted DRAFT: C079 persistence-dirty/current-valid + Test NOT_RUN -> Save disabled.
- [ ] Persisted DRAFT: same state + current PASS -> Save enabled.
- [ ] Persisted DRAFT: changing only Test arguments/shop does not set persistence-dirty but stales Test/Save eligibility.
- [ ] Start run at snapshot N, edit Response before completion, resolve old successful response -> Test remains STALE and Create/Save remains disabled.
- [ ] Start run N, then run N+1; late N response cannot overwrite N+1 result/checkpoint.
- [ ] Backend `kind: ok` with any failed C082 stage -> common Test FAILED, never PASSED.
- [ ] Missing selected shop performs zero C082 action call and shows the exact local message.
- [ ] Invalid/stale prerequisite messages point only to Tool Definition, Request, Response or Result Template.
- [ ] Successful output renders `Result shown to agent` before diagnostics and equals server `renderedText` exactly.
- [ ] Browser Test input contains no shop domain/access token/credential fields.
- [ ] Focused zero-write assertion proves Test invokes no create/save/publication mutation.
- [ ] Existing External C081 Save/Test regressions remain green.
- [ ] Targeted ESLint for changed files.
- [ ] Changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation.
- [ ] `git diff --check`.

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin system-test or adjacent work.

## Implementation Notes

Do not infer Shopify rendering or result-envelope semantics in React. C082 is the sole server authority for provider execution, normalized result and rendered agent output.

The C083 dependency on C081 is an intentional coordination dependency: both tasks affect provider-aware authoring/Test Save gating in shared new/persisted editors. C083 must build on the accepted External gate rather than editing the same shared decision concurrently.

The C083 dependency on C079 is also intentional: persisted Shopify Test integration must target the accepted persisted authoring-session/persistence-dirty model rather than inventing temporary persisted-state semantics.

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
