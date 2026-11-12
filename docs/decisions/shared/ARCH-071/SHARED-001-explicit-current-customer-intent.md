---
id: ARCH-071-SHARED-001
architecture_id: ARCH-071
title: Preserve explicit current customer utterances as conversation intent
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Preserve explicit current customer utterances as conversation intent

## Architecture

ARCH-071; docs/architecture/ARCH-071-explicit-current-customer-intent.md; coordinator moda_architect.

## Objective

Preserve explicit current customer utterances as conversation intent without granting customer text policy or tenant authority.

## Context

Source inspection proves current customer text is nested only in data-only context whose instructions forbid establishing customer objective, while older user history has ordinary Human roles. A newer named subject was answered using prior product focus. Exact historical model reasoning/input is unavailable; structural contract mismatch is independently confirmed. ARCH070 is complete and remains closed. Root approved the additive typed contract and existing-budget constraints before execution.

## Scope

New canonical current-customer-message schema/helper/public export; optional RunCommerceTurnInput/ModelRequest field; preflight/copy, all-step invocation/repair propagation, direct OpenRouter adapter boundary/order, generic customer-intent instructions and approved5.13.6 metadata.

## Out of Scope

Hardcoded product aliases, fuzzy ID guessing, clearing all prior product references, permission/tenant policy changes, alternate models, automatic product selection, additional repair loops, schema/infra/credentials, private prompt export and production replay.

## Requirements

Use optional currentCustomerMessages: readonly {role:user,content:string}[] with exact role/content-only shape. When present it must be nonempty, every role exactly user and content a string; reject invalid input rather than silently drop/truncate/coerce. JSON-encoded current array must fit32,000 Unicode code points, matching existing Background current budget; no arbitrary20-row or16,000UTF16 lower cap. Existing overall payload byte cap remains. Validate/copy in runner preflight and defend direct adapter invocation before provider calls. Forward on every model step/forced correction. Serialize System -> older history -> data-only context -> dedicated current Human utterances -> current tool-result data. Explicit current customer content establishes present request/objective subject to system policies, never grants permissions, tenant access or tool authority. Older references must not override an explicitly named current subject. Named/typo switch may use an authorized fresh lookup or clarification; no hardcoded alias/fuzzy identifier mapping is implemented. Ambiguity guidance is retained, but a deterministic general semantic resolver is outside this carrier contract. Never extract/promote arbitrary context/history/tool text as current input. Optional absence keeps exact legacy behavior; current opted-in custom invokers must receive and honor the typed field. Preserve chronology, budgets, strict selection/referral, shipping and security behavior.

Contract clarification: each current content string must contain at least one character; reject empty strings without trimming, dropping or fallback. Preserve whitespace and all raw text exactly. This adds no lower row/UTF16 cap; existing aggregate Unicode JSON/overall-byte limits remain.

Identity-resolution clarification: freshly reading a known product proves facts, not that it is the intended new subject. If multiple plausible candidates remain, ask a clarifying question rather than choosing by recency. Preserve candidate references for lookup without treating them as automatic current identity. Exact-name and typo switch probes plus deterministic carrier/authority guards are the required acceptance evidence. Both failed multiple-candidate ambiguity samples remain honestly recorded; they are not labeled passed. Root approved splitting a deterministic ambiguity-resolution/explicit-choice contract into separate unrequested scope, with no additional prompt iteration or restrictive UX in this task.

## Work Items

- [x] Establish owned failing regression and exact caller/contract compatibility.
- [x] Implement only the defined owned outcome or approved exact release.
- [x] Validate required positive/negative boundaries and record exact artifact/heads.

## Interfaces / Contracts

Shared owns optional currentCustomerMessages exact role:user/content array contract and runtime validation. Producer Background attests its server-owned current-message source through existing turn identity/fences; the shape itself is not authentication. Runner forwards to ModelRequest, adapter presents dedicated current Human content; no arbitrary JSON promotion. Public package @modainteract/moda-interact-shared through appropriate commerce/model entrypoints. Legacy absence unchanged.

## Dependencies

None. Publication readiness additionally requires explicit user public-release approval; consumer waits actual canonical downloaded-byte acceptance.

## Enables

Next ARCH071 publication/consumer gate, followed by developer genuine production verification.

## Acceptance Criteria

- [x] Requirements hold, including current-intent objective boundary and unchanged security/budgets.
- [x] No silent truncation/drop/coercion, inferred input or tenant/permission promotion.
- [x] No private customer prose/operational identifiers in committed evidence or diagnostics.
- [x] Canonical mirrored physical isolation, synchronization and recursive submodule evidence recorded.

## Validation

- [x] Deterministic role/order/strictshape/Unicode aggregate/overall-byte budget and no-provider-invalid-input tests; all model/repair propagation; old-absence compatibility; synthetic multi-turn named/typo switch and prompt-injection/tenant authority negatives; record ambiguous-case limitations without claiming a general resolver. Full Shared suite/types/build/installed immutable JS+DTS/public exports. Before publication require wholly synthetic real-provider current-versus-prior-subject probe with frozen built public client/actual runner wiring; no customer/private context, live commerce/DB/Meta mutation. Root may supply proof.
- [x] Scope/diff/secret hygiene.

## Stop Condition

Complete owned work and required validation, report REVIEW and STOP. No next task, merge/deploy or public publication outside explicit task authorization.

## Implementation Notes

You are not alone; preserve others. Use prepared packet paths/branch and actual package scripts. No source edits before prepared claim. For publication, reuse accepted artifact and do not repeat implementation checks. Public docs/probes use synthetic examples and coarse outcomes only.

## Completion Report

### Status

Ready for Review — ARCH-071-SHARED-001, attempt1, executor codex.

### Files Changed

Shared: current-customer-messages schema/helper/tests; runner types/preflight/invoke-model/tests; OpenRouter adapter/tests; commerce exports; README; package metadata5.13.6; installed-export validation script. Implementation commits1fe6e9f and17fcced339c2c9490f064027e3365cf86fa397f4 pushed on task/ARCH-071-SHARED-001. PR: https://github.com/kodjobaah/moda-interact-shared/pull/80.

### Work Completed

Added strict role:user/content-only, nonempty array/content validation with32,000 JSON Unicode codepoint aggregate bound, preserving raw content and the existing131,072-byte combined payload cap. No lower row/UTF16 cap. Preflight copies/freezes current rows and forwards the same snapshot on every model step/correction. Direct adapter separately validates before provider invocation; order is System, older history, data-only context, dedicated current Human messages, then tool data. New current-boundary errors discard private raw validation causes. Optional absence retains legacy instructions/serialization. Opt-in guidance gives new named subjects priority without granting tenant/tool/consent authority. Documented custom-invoker responsibilities and host source provenance.

### Validation Results

- Initial focused adapter/runner regression run:118/118 passed. Final full `npm test`:758 total,755 passed,3 skipped,0 failed. Includes strictshape/empty/unknown-role rejection, exact Unicode bound, >20 rows, >16k text, aggregate byte rejection, frozen snapshot/correction propagation, absence compatibility, private cause chains and safe unauthorized-tool referral with zero tool execution.
- `npm run typecheck`, `npm run build` (ESM+DTS), immutable-tarball `node scripts/validate-commerce-outreach.mjs /tmp/modainteract-moda-interact-shared-5.13.6.tgz`, and `npm run validate:commerce-entrypoints`: passed. Installed smoke proves JS/helper/schema/public exports and strict declaration role typing.
- Coordinator/root supplied wholly synthetic actual-provider proof using final frozen public client and instructions: exact new subject and typo after older product dialogue select the correct known new identity; an additional harder synthetic misspelling also passed. Provider-generated tool calls were not executed. Scripts are local `/tmp/moda-recovery-setup/probe-synthetic-product-switch.mjs` and `probe-synthetic-product-switch-hard-typo.mjs`; no customer payload/private prompt, real commerce API, DB writes or WhatsApp send. Provider-free runner tests prove actual current-field/correction propagation.
- Both original and revised ambiguous unnamed multi-candidate samples selected a candidate without clarification. These are failed samples, not conformance passes. Root/architect explicitly separated generic semantic resolution/explicit-choice UX from this carrier/named-switch task before acceptance; retained generic guidance is empirical model guidance, not a deterministic ambiguity gate.
- Scope/`git diff --check`/committed evidence hygiene passed. No credential or customer-text artifacts committed.

Exact immutable candidate: `/tmp/modainteract-moda-interact-shared-5.13.6.tgz`,517461 bytes.
SHA256 `fbe8e97a3018ddcfbd29f85c4acc4fdab5447681bf94d4bc41695e6f6c44e049`.
SHA1 `606bed12a2d2869f414919d1538202cfd1fab9dc`.
Integrity `sha512-bcc7jKLRQU/c7uzLJxXtQbbILsYfCsBXwpdX4fwtejsPvV0fN98eWr49dqmoC7M+4BucF2CJ84n193qbIAJuew==`.
No public publication performed.

Physical worktree isolation (prepared packet): primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-071-SHARED-001`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-071-SHARED-001`; both branches task/ARCH-071-SHARED-001. No shared/default checkout switched or mutated; no other task worktree reused. Launcher parent/implementation remote-task fast-forward not-needed, origin/main already-current; recursive submodule sync/update passed, entries none. Prepared claim141451498f175a70c21066acec8f64d18001a041; implementation base596eaa455f9b6eb72f316c76c1c7a4657faa1f60. No duplicate preparation.

### Deviations

Root/architect narrowed acceptance after two transparent synthetic ambiguity failures: typed carrier/named-typo switch remains this task, deterministic general ambiguity resolution is separate unrequested scope. No additional prompt iteration, guessed aliases/IDs, new tool loops or restrictive choice UX added.

### Assumptions

Host source/turn fences attest current inbound provenance. Shape itself authenticates nobody; current customer content supplies objective only. Custom invokers must honor the opt-in field semantics.

### Unresolved Issues

General unnamed multi-candidate ambiguity is not solved, as documented above. Exact historical model reasoning remains unavailable. This artifact has not been publicly released, adopted by Background or verified in a genuine production conversation. Separate publication requires explicit user approval and accepted exact artifact.

### Architectural Concerns

No further source change requested. Background producer/adoption and publication remain separate owner/task gates.

## Architect Review

### Review Status

Accepted — Attempt 1, under the recorded evidence-based carrier/named-switch scope decision.

### Review Notes

Reviewed actual17fcced339c2c9490f064027e3365cf86fa397f4 and durable report56563bcee. Strict nonempty role:user/content-only current array, exact32k JSON Unicode budget, existing overall-byte cap and frozen preflight snapshot are implemented without lower row/UTF16 caps. All model/correction steps forward the explicit field; direct adapter defensively validates and orders history/context/current/tools. Optional absence keeps legacy serialization/instructions unchanged. Opt-in current text establishes objective, never tenant/tool/consent/policy authority. Private validation causes are bounded and the meaningful denial test proves safe referral/no unauthorized execution.

### Reviewed Files

current-customer-messages module/tests; public types/export, preflight and invoke propagation; OpenRouter adapter/tests; runner regressions, README compatibility, installed validator and package metadata.

### Validation Reviewed

Initial118 focused and final755 full passes/3 skips; types, ESM+DTS build and immutable installed JS/DTS/public exports. Exact/typo and harder synthetic named-switch actual-provider cases passed on frozen source; no customer data or real commerce calls were used. Both unnamed multiple-candidate ambiguity samples failed and remain explicitly NOT passed. Root approved separating a deterministic semantic resolver/choice UX from this structural carrier fix before acceptance; this is a real bounded scope correction, not a waived claimed pass. Independently hashed517461-byte candidate SHA256fbe8e97a3018ddcfbd29f85c4acc4fdab5447681bf94d4bc41695e6f6c44e049. Prepared physical isolation/sync/submodule evidence and diff scope verified.

### Architecture Conformance

Conforms to additive explicit current-input contract and existing authority/control/budget fences. No arbitrary JSON promotion, alias/ID mapping implementation or extra retry loop. General semantic ambiguity remains a transparent model limitation; historical reasoning and production improvement are not inferred from synthetic checks.

### Follow-up

Developer may merge PR80 exact17fcced. User explicitly approved public5.13.6 release in response to the canonical public npm/latest question; publication002 may be Ready but must wait actual merge and sole exact-artifact execution. Background adoption and genuine production named-switch proof remain separate gates. No further prompt churn or repeated implementation validation required.
