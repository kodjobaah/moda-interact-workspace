---
id: ARCH-070-SHARED-003
architecture_id: ARCH-070
title: Align bounded selection repair with canonical semantic validity
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-12T13:47:59Z
attempt: 1
depends_on:
  - ARCH-070-SHARED-002
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Align bounded selection repair with canonical semantic validity

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Align bounded selection repair with canonical semantic validity within existing verified and bounded execution contracts.

## Context

Provider-free reproductions prove schema-valid missing-version/nonempty-list can skip runner repair but host drops the list; truthy null/null shipping without disposition similarly skips repair but host discards it. Fresh production version6 exact raw final shape is unavailable, so historical exact cause is not claimed. Existing accepted null-URL/footer/terminal fixes remain valid.

## Scope

Shared product-selection normalization/semantic validity helper, existing graph-node/invoke repair constraint, public commerce export, directly related tests and approved5.13.4 metadata.

## Out of Scope

Unrelated refactors, provider/model changes, fabricated selections or automatic product choice, new queue retry loop, broader schema/infra/credential/consent changes, live customer sends or resetting processed input.

## Requirements

Own reusable normalized selection parsing once in Shared and use it in runner repair eligibility. Missing recommendation version/list pair, malformed selections or null shipping placeholder without a meaningful disposition must not bypass existing selection repair. Preserve valid paired product IDs and disposition/shipping semantics; preserve bounded existing retry, step/token/tool budgets, cancellation and empty-search behavior. Do not infer version/IDs, auto-select products or create a second repair/queue loop. Preserve Background existing valid-disposition recovery and refusal semantics; export normalization/eligibility helpers so consumer uses identical mechanics. Test provider-free malformed-pair and null-shipping reproductions, corrected model turn with valid fields, bounded exhaustion, valid selections, empty search, ordinary factual answer and publication type/export compatibility.

Compatibility clarification: structural schemas intentionally permit independent optional version/list fields and .extend consumers; do not globally refine that Zod contract. Preserve canonical host semantics for null/null shipping WITH a recognized disposition and partial valid-disposition recovery. In generic runner pinned contracts that do not expose the canonical version/list pair, preserve existing strictly pinned field behavior; never invent unsupported version requirements. Production canonical pair must use normalized semantic validity.

Runtime evidence clarification: static valid STANDARD plus null/null shipping remains a normalized valid selection, but is not by itself sufficient to bypass product selection repair. Qualify shipping bypass and provider forced-schema shipping alternatives with matching successful authorized current-turn shipping observations; product search alone never qualifies. Preserve legitimately observed shipping-only policy answers and exact product/variant matching. Add positive observed-shipping and negative unobserved/mismatched/failed/stale shipping regressions. Keep generic pinned-contract compatibility and existing one-repair/budget limits.

Shipping evidence precision: expose one canonical pure recognized shipping-result/selection-identity qualifier for runner and Background fresh-result reuse, with expected provider where known. A truthy limitation is not proof: reject provider/identity mismatch, invalid or unrelated result. For null/null policy selection, preserve a matching NOT_REQUESTED identity and truthful policy-unavailable limitation. When product observations require selection, disposition-only SHIPPING_INFORMATION_UNVERIFIED bypass and forced-schema alternative also require matching qualified shipping evidence. Shipping-only paths with no product observation retain existing normal behavior. No new provider reads or loops.

## Work Items

- [x] Reproduce both semantic gaps deterministically against prior implementation.
- [x] Implement only owned canonical semantic correction/adoption.
- [x] Prove compatibility and bounded failure behavior; report exact validation.

## Interfaces / Contracts

Shared owns canonical semantic normalization and repair eligibility; public package @modainteract/moda-interact-shared/commerce. Background consumes published helper and retains tenant/provider/evidence policy. Existing schemas, normal answer contract and budgets remain compatible.

## Dependencies

ARCH-070-SHARED-002. Publication additionally requires developer merge of accepted implementation.

## Enables

Next publication/consumer task in ARCH-070, then developer production verification.

## Acceptance Criteria

- [x] Requirements hold, including unchanged security and bounded failure behavior.
- [x] Canonical reusable mechanics are not duplicated across Shared/Background.
- [x] No private prose, prompts or secret payloads added to diagnostics.
- [x] Prepared mirrored worktree, start-sync and recursive submodule evidence recorded.

## Validation

- [x] Focused parser/runner red-green regressions and bounded-budget cases, full Shared suite, types/build and installed immutable package JS+DTS/public exports; record exact candidate hashes.
- [x] Exact changed-file scope and diff/secret hygiene.

## Stop Condition

Complete owned work and required validation, set review, return report and STOP. Do not merge, deploy or begin another task.

## Implementation Notes

You are not alone in the codebase. Preserve others' changes. Use the prepared dedicated mirrored worktrees and task branch. Verify actual package scripts before running checks. Existing structured semantic logs suffice; do not introduce competing logging or repeated provider work as a diagnostic mechanism.

## Completion Report

### Status

Ready for Review — implementation `8390849` pushed on `task/ARCH-070-SHARED-003`; PR https://github.com/kodjobaah/moda-interact-shared/pull/78. No merge or package publication performed.

### Files Changed

- `src/commerce/recommendation-selection.ts`: canonical normalized host selection parser and exported semantic eligibility, canonical-contract detection, matching shipping DTO/provider/identity qualifier and authorized current-turn shipping selection extraction.
- `src/commerce/index.ts`: public commerce helper/type exports.
- `src/commerce/runner/graph/nodes/validate-final-response.ts`: use accepted semantic selections for the existing single bounded correction.
- `src/commerce/runner/product-selection.ts`: require supported canonical version/list pairs; shipping alternatives constrained to observed identities, including optional null/null selection on a generic-policy disposition branch. Custom pinned contracts retain existing behavior.
- `src/commerce/runner/graph/nodes/invoke-model.ts`: pass current authorized observations/provider to constraint construction and align initial/correction guidance. Same forced finalResponse, tools, budgets and existing repair flag.
- `src/commerce/recommendation-selection.test.ts`, `src/commerce/runner/selection-semantics.test.ts`: deterministic semantic, parser, current-turn identity/provider, forced-schema, normalization, compatibility, corrected model turn, empty search, cancellation and bounded-budget regressions.
- `scripts/validate-commerce-entrypoints.mjs`, `scripts/validate-commerce-outreach.mjs`: installed public JS/DTS helper coverage.
- `package.json`, `package-lock.json`: approved 5.13.4 metadata only; dependencies unchanged.

### Work Completed

Provider-free read-only reproduction proved both semantic gaps against the prior implementation: nonempty recommendations without version and shipping null/null without disposition were accepted without correction while Background discarded the unusable selection. Two new runner regressions failed before the correction.

Own canonical mechanics now preserve valid partial disposition recovery, normalized empty optional lists, paired recommendations and static recognized-disposition null/null shipping. Runtime shipping alternatives only qualify against matching successful authorized current-turn canonical shipping results, including expected provider when known. Product-search results, failed/malformed/mismatched shipping and historical prose cannot qualify. Matching NOT_REQUESTED null/null policy with unavailable policy remains a truthful limitation. Disposition-only SHIPPING_INFORMATION_UNVERIFIED requires matching generic policy evidence when observed products require a selection.

Existing structural optional-field schemas and .extend consumers are unchanged. Generic/custom contracts without both canonical version/list properties keep existing pinned behavior and are never assigned an unsupported version field. No inferred version/IDs, automatic product choice, extra provider calls, second repair or queue loop. Background adoption/delegation remains its separate repository task.

Prepared launcher/isolation evidence:

- Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-070-SHARED-003`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-070-SHARED-003`; both branch `task/ARCH-070-SHARED-003`.
- Shared/default checkouts switched/mutated: no; another task worktree reused: no.
- Parent and implementation remote task branch fast-forwards not needed; both origin/main already current.
- Recursive submodule sync/update passed; no entries.
- Claim `992f57acf8151f0cb46d99197326a473e2c63fe4`; implementation base `72203015aa7daec41ed4aa76d13c11d7309b10a4`; prepared dependency gate Shared002 Complete.

### Validation Results

- Red regressions: 2 failures before guard correction, both accepted-before/repair-required cases.
- Final focused parser/runner/structural-contract suite: 154 passed, 0 failed.
- `npm run typecheck`: passed.
- Final `npm test`: 739 total; 736 passed, 0 failed, 3 expected integration skips.
- Final `npm run build`: ESM and declarations passed.
- Installed immutable tarball JS and strict-null public declaration/import smoke: passed using `node scripts/validate-commerce-outreach.mjs /tmp/modainteract-moda-interact-shared-5.13.4.tgz`.
- `npm run validate:commerce-entrypoints` and `npm run validate:commerce-presentation`: passed, including browser-like presentation import.
- `git diff --check`, changed-file scope and secret hygiene: passed. Synthetic identities only; no private prompts/prose, customer payloads or new diagnostics.
- Final candidate `/tmp/modainteract-moda-interact-shared-5.13.4.tgz`; SHA256 `fcf2cc8d78c327b85a6de777541ea5ba53b659079234e790aec3d0fd97b47693`; SHA1 `32453dd53debf4024899b607632a38046a292c08`; integrity `sha512-EXNoSmbmB3E+hK1bNArMr5dsfZSQ2gHTV4/EoSj8coSCdHepdLfPD9aN2YTEOgYZ9Rwi6mNa9OT/ZBlqCDdJjg==`.
- Coordinator supplied separate provider-conformance evidence using entirely synthetic context/products: one 327-token forced finalResponse with version 1 and two observed product recommendations, no shipping placeholder. This is not asserted as exact historical production reproduction or a full source-wiring test; actual source wiring is covered by deterministic runner tests.

### Deviations

Architect-approved runtime evidence clarification added during this attempt and read in full. A final reviewed generic-policy optional-shipping identity constraint required rerunning affected final checks. Test-only tuple/union narrowing annotations were corrected; final checks and artifact all use the same frozen runtime source. Existing validated dependencies reused through an ignored node_modules symlink; dependency resolution unchanged.

### Assumptions

Authorized current-turn observation provenance is maintained by the existing runner tool-execution boundary. The pure qualifier does not replace host tenant, ownership, deadline, fresh-read or provider authorization fences and does not invent a new timestamp TTL. Background must reuse it for fresh-result identity/provider verification after publication.

### Unresolved Issues

Exact historical production version6 final raw shape remains unavailable; deterministic semantic gaps are proven but historical exact causality is not claimed. Separate accepted artifact publication, downloadable registry integrity and Background adoption/deployment verification remain pending owner tasks.

### Architectural Concerns

None within this approved correction. Canonical parser/qualifier are ready for Background delegation after published dependency adoption; no cross-repository edits performed here.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
