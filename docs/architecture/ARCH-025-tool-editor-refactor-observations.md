# ARCH-025 ToolEditor refactor observations and follow-up issues

## Purpose

This document records source behaviours and possible follow-up issues discovered while decomposing `moda-interact-commerce/src/studio/tools/tool-editor.tsx` for ARCH-025.

It is **not** an implementation contract to change these behaviours during COMMERCE-006..010. The structural refactor must preserve them unless a separate architecture/task explicitly authorises behavioural correction. Where a behaviour is merely unusual rather than demonstrably wrong, it is labelled accordingly.

Reviewed baseline:

```text
src/studio/tools/tool-editor.tsx
916 lines
SHA-256 c91ff89cb47d5e9afd50dec2b0aeb24e59c57dfc37e2013e6511f87d15be54fa
```

## Observed behaviours to preserve during ARCH-025

### O1 — Cancel does not reset every local authoring field

`cancelPersistedChanges()` restores the selected saved definition, raw JSON/editor buffers, persisted authoring state and editVersion; clears parse/validation/publish messages and most execution-kind validation flags; clears dirty state; increments `editorGeneration`; and calls `onAuthoringSessionSaved`.

It does **not** explicitly reset `resultTemplateValid` or the current persisted authoring tab (`externalSection`). A cancel performed from Review therefore leaves the selected tab unchanged until the user navigates. This is current behaviour and must not be normalised in COMMERCE-006..010.

Potential follow-up: decide whether Cancel should restore a canonical section and force Result Template validity to be recomputed.

### O2 — Cancel consumes the authoring-session callback despite performing no save

Cancel calls `onAuthoringSessionSaved?.()` even though no `updateToolDraft` mutation occurs. In current composition that callback is used to consume/clear the restored authoring-session handoff.

Potential follow-up: rename or split the callback to reflect “authoring session consumed” rather than “saved” semantics.

### O3 — Save convergence differs by execution kind

Policy save explicitly restores the returned candidate, resets common authoring state, clears parse/validation messages and dirty state, updates returned editVersion, increments `editorGeneration`, and consumes the authoring session. Shopify Admin save restores returned state/editVersion, clears dirty/admin validation, increments `editorGeneration`, and consumes the authoring session.

External save restores returned candidate/buffers/editVersion and conditionally preserves authoritative validation when returned definition equals the submitted definition, but does not explicitly increment `editorGeneration` or call `onAuthoringSessionSaved`; global dirty clearing may instead occur through the Studio `runCommand` content-revision success fence.

Potential follow-up: decide whether all persisted execution kinds should have one explicit saved-revision convergence contract. Do not change this in the move-only refactor.

### O4 — External and Shopify Admin publication can rely on server-side current-Test rejection

Policy publication includes `isCurrentTestPassed(...)` in its client publish gate. External publication currently gates on role/dirty/definition validation/authoritative validation/reason but not current Test. Shopify Admin publication gates on role/dirty/request/result-contract/mapping validation but not current Test. After a save resets common Test state, their UI can therefore reach a publish attempt that the server rejects with `LIVE_TEST_REQUIRED`. Existing External/Admin regression coverage demonstrates this server-authoritative rejection path.

Potential follow-up: decide whether all persisted Tool kinds should expose a consistent client-side current-Test publication gate. Server enforcement must remain authoritative regardless.

### O5 — Publication reason semantics differ by execution kind

Policy and External require a trimmed user-provided publication reason between 1 and 1000 characters. Shopify Admin currently publishes with the fixed reason `Reviewed Shopify Admin GraphQL definition` and does not expose the same reason input in its Review action.

Potential follow-up: decide whether audit reason UX/policy should be uniform across persisted Tool kinds.

### O6 — Returned-save identity verification is asymmetric

Policy save verifies the returned revision ID, canonical Tool name and immutable operation/operationVersion binding before adopting returned state. External save uses canonical saved-definition equality to decide whether authoritative validation can be retained, but does not perform the same explicit returned revision/binding identity rejection. Shopify Admin save adopts the returned definition/editVersion without an equivalent explicit identity check.

Potential follow-up: consider one common returned-revision identity/fence contract after the structural refactor.

### O7 — Review validation identity is narrower than the full set of raw editor buffers

The shared Review identity is built from selected revision ID, editVersion, `definition`, `inputSchemaText` and `responseTemplateText`. Raw local buffers such as `externalAdvancedText`, `externalSchemaText`, `adminResultPathText` and `adminLiteralText` are not independently part of that identity. Current child flows generally propagate authoritative changes into definition/revision state, and existing tests protect important stale-validation cases.

Potential follow-up: audit whether every invalid/raw-buffer edit that can affect an authoritative Review candidate is guaranteed to alter the current identity or otherwise prevent validation acceptance. Do not broaden the identity during extraction without dedicated behavioural tests.

### O8 — Review identity generation uses a render-time state update

`ToolEditor` currently calls `setReviewIdentityState(...)` during render when the canonical identity changes, incrementing a monotonic generation used to distinguish A→B→A. The pattern is unusual React state management but is bounded by the key comparison and existing regression coverage.

Potential follow-up: after extraction, consider a clearer generation primitive only if A→B→A semantics and duplicate in-flight fencing are proven unchanged.

### O9 — No-port External fallback does not advance the common Request revision for raw Input Schema edits

When an authorised External HTTP port is available, Input Schema edits explicitly call `recordPersistedAuthoringRevision("request")`. In the no-port fallback Request panel, the raw Input Schema edit marks dirty and invalidates External validation but does not explicitly advance the common Request revision. Live Test is unavailable in that state, which limits the practical effect.

Potential follow-up: decide whether revision semantics should be consistent even while provider authoring is unavailable.

### O10 — Shopify Admin mapping-only edits intentionally keep the derived result contract fresh

The current branch stales `adminResultContractFresh` for document, operationName, apiVersion, schemaHash or resultPath changes, but not for variable/literal mapping-only changes. Dedicated regression coverage asserts this behaviour.

This is an **intentional protected contract**, not a defect candidate for ARCH-025.

### O11 — The defensive generic DRAFT editor bypasses the persisted six-step/Test model

Execution kinds other than Policy/External/Shopify Admin fall through to a simple generic definition editor with direct save/publish controls. It does not use the same persisted six-step/Test/Review gate model. This appears to be a defensive compatibility path rather than a fourth supported authoring workflow.

Potential follow-up: if another execution kind becomes authorable, define it explicitly instead of expanding this fallback opportunistically.

### O12 — Authoring-session overlays are gated inconsistently across fields

The selected definition base uses `authoringSession.definition` only when the session is `mode === "existing"` and its tool/revision identity matches the selected revision. In contrast, the raw Input Schema / Result Template / Admin result-path / literal buffers currently read from the supplied session whenever values are present; the active persisted section checks `mode === "existing"` but not tool/revision identity; and Result Template authoring metadata is applied whenever supplied. Current `ToolAuthoringScreen` composition is expected to pass the relevant session, so this normally converges correctly.

Potential follow-up: decide whether ToolEditor should independently validate one consistent authoring-session identity before applying every overlay. ARCH-025 preserves the current behaviour.

## Follow-up handling

No issue above is automatically a bug. After COMMERCE-010 is accepted, `moda_architect` may create separate bounded correction tasks for behaviours the developer chooses to change. Any such task should have its own behavioural acceptance criteria and tests rather than being folded into the structural extraction.
