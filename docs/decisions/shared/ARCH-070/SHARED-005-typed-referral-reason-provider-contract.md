---
id: ARCH-070-SHARED-005
architecture_id: ARCH-070
title: Make referral reason provider nullability and forced guidance explicit
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
depends_on:
  - ARCH-070-SHARED-004
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Make referral reason provider nullability and forced guidance explicit

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Make referral reason provider nullability and forced guidance explicit within existing strict final-envelope and bounded execution guarantees.

## Context

Fresh production version7 entered selection repair but failed final schema at referralReason invalid_value. Exact raw invalid value is unknown and must not be assumed. User explicitly authorized correcting referralReason, testing, commit/push/merge and fresh production recommendation/footer verification. All previous eight accepted tasks remain valid; architecture stays In Progress.

## Scope

Shared finalResponse provider JSON schema and common forced-finalization instructions; strict referralReason validation regressions, public export smoke and approved5.13.5 metadata.

## Out of Scope

Unknown-value normalization, schema weakening, missing-field dropping, extra repair/queue loops, automatic selections, provider/model switching, credentials, unrelated refactors, production replay and unsolicited Meta sends.

## Requirements

Explicitly represent nullable string type for provider referralReason JSON schema. Common forced guidance must distinguish ANSWER uses JSON null from REFER_TO_STORE uses an allowed pinned reason, preserving required-referral constraints. Keep exact strict runtime validator, mandatory fields and existing single correction/step/deadline/token budgets. Never normalize unknown strings, drop invalid fields, guess historical raw value or add another retry loop. If diagnostics are needed, emit only bounded ABSENT/NULL/recognized-enum/other-STRING/OTHER shape classification through existing shared logger; no raw value/private prose. Preserve previously accepted selection, shipping-evidence, chronology and security behavior.

## Work Items

- [x] Establish owned source/release behavior and preserve relevant regression evidence.
- [x] Complete only the bounded owned correction or exact artifact release.
- [x] Record required validation, exact hashes/heads and return review.

## Interfaces / Contracts

Shared owns canonical finalResponse provider schema, validator and bounded runner. Background consumes published @modainteract/moda-interact-shared package and retains tenant/host/evidence/delivery policy. No new wire/schema version or mandatory-referral change authorized.

## Dependencies

ARCH-070-SHARED-004. Publication additionally requires developer implementation merge; consumer starts only after actual public artifact integrity acceptance.

## Enables

Next ARCH-070 publication/consumer gate, then root/developer fresh production verification.

## Acceptance Criteria

- [x] Requirements and required validation pass without weakening strict validation or bounded execution.
- [x] No private prompts/prose, raw invalid values, customer data or secrets in diagnostics/probes.
- [x] No unrelated files or implementation-owner boundary violation.
- [x] Launcher mirrored physical isolation, synchronization and recursive submodule evidence recorded.

## Validation

- [x] Deterministic provider-schema/forced-guidance and strict final validation red-green tests including JSON null vs literal string, invalid reason, allowed referral and mandatory-referral behavior; full Shared suite, types/build/installed immutable JS+DTS/public exports. Before publication require a wholly synthetic real-provider conformance probe using current anonymous pinned schema and final actual public built client; synthetic products/history only, no customer/private prompts or Meta sends. Root may supply that proof; report its limits separately from production.
- [x] Diff scope/hygiene and secret validation.

## Stop Condition

When owned work and required validation are complete, set review, report and STOP. No follow-on task, merge/deploy or publication outside explicit task scope.

## Implementation Notes

You are not alone; preserve others' changes. Use canonical prepared packet paths and matching mirrored branch. Read actual package scripts; do not rerun accepted implementation validation in publication. Existing shared structured logger only if diagnostics needed. Exact historical invalid referral value remains unconfirmed.

## Completion Report

### Status

Ready for Review — implementation `7b5c4a6` pushed on `task/ARCH-070-SHARED-005`; PR https://github.com/kodjobaah/moda-interact-shared/pull/79. No merge or package publication performed.

### Files Changed

- `src/commerce/response.ts`: explicit nullable-string provider referralReason type, unchanged canonical enum, JSON-null description and typed ANSWER/REFER_TO_STORE branches.
- `src/commerce/runner/graph/nodes/invoke-model.ts`: one private common forced-envelope instruction applied to both schema and selection correction branches; allowed reasons derived from existing canonical enum.
- `src/commerce/response-contracts.test.ts`, `src/commerce/runner/runner.test.ts`, `src/commerce/runner/selection-semantics.test.ts`: provider schema, strict valid/invalid set, both correction paths, mandatory referrals, actual JSON-null answer, allowed referrals and malformed/missing terminal reason tests.
- `scripts/validate-commerce-entrypoints.mjs`, `scripts/validate-commerce-outreach.mjs`: installed public provider-schema JS/DTS coverage.
- `package.json`, `package-lock.json`: approved 5.13.5 metadata only; dependencies unchanged.

### Work Completed

Recorded four failing regressions before implementation: missing explicit provider type and missing common JSON-null guidance on two schema-correction platforms plus selection correction. Implemented explicit provider guidance without changing the strict runtime validator, allowed reason values, required fields, normal answer/referral semantics or existing single correction flag/budget.

All forced corrections now restate every required envelope field, ANSWER uses JSON null, and REFER_TO_STORE uses a canonical allowed reason with empty details/evidence. Unknown values are never normalized, coerced, omitted or substituted. Invalid/omitted referralReason after the one correction remains terminal FINAL_SCHEMA_INVALID. Mandatory tool-referral decisions remain enforced; no extra provider read, model loop, queue retry or automatic selection.

Prepared launcher/isolation evidence:

- Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-070-SHARED-005`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-070-SHARED-005`; both branch `task/ARCH-070-SHARED-005`.
- Shared/default checkouts switched/mutated: no; another task worktree reused: no.
- Parent/implementation remote task branch fast-forwards not needed; both origin/main already current.
- Recursive submodule sync/update passed; no entries.
- Claim `be4973f7f83bbeecd7913ac7ce31c5d29a7e532c`; implementation base `6cf830f9e5ba9692acd33032af0e6a2c8b5929d3`; prepared Shared004 Complete dependency gate passed.

### Validation Results

- Red regressions: four deterministic failures before provider typing/common guidance correction.
- Focused provider-schema and runner suites: 112 passed, 0 failed.
- `npm run typecheck`: passed.
- `npm test`: 746 total; 743 passed, 0 failed, 3 expected integration skips.
- `npm run build`: ESM and declarations passed.
- Installed immutable package public JS and strict-null DTS validation passed using `node scripts/validate-commerce-outreach.mjs /tmp/modainteract-moda-interact-shared-5.13.5.tgz`.
- `npm run validate:commerce-entrypoints` and `npm run validate:commerce-presentation`: passed, including browser-like presentation imports.
- `git diff --check`, changed-file scope and secret hygiene passed; synthetic test values only, no raw historical invalid value, private prose/customer data or new diagnostics.
- Candidate `/tmp/modainteract-moda-interact-shared-5.13.5.tgz`; SHA256 `71118ab02b14ffb36659a8cc6ba5caa91055bb8f3da48a23b3c731c7366ba6ed`; SHA1 `9fa4b1d97da4a68e801d4c5cc7abfa43bd57e862`; integrity `sha512-ZMkZwnNBWAL+gX8FAV2fcj51KsTqyKJstsyaFDJVYic5T/BR5LsiGArYvZmYAV18APh5Av6mM+eUeLlivQ3LrA==`.
- Required coordinator-supplied synthetic real-provider conformance passed using `/tmp/moda-recovery-setup/probe-synthetic-referral-correction.mjs`: final frozen public candidate OpenRouter client/schema and actual candidate invoke/validate correction nodes via TSX; one real model call returned ANSWER with actual JSON-null referralReason, version 1 and two exact observed synthetic products, no shipping placeholder; candidate strict final validation passed. No customer/private context, commerce provider reads, DB writes or WhatsApp sends. This proves provider conformance on that synthetic request, not a production answer or historical raw-value reproduction.

### Deviations

None. Existing validated dependency installation reused through an ignored node_modules symlink. No runtime source changes after the successful final checks/build/probe; immutable pack used --ignore-scripts without rebuilding.

### Assumptions

Historical exact invalid referralReason remains unknown. Synthetic malformed examples are regression cases, not inferred historical values. Strict fail-closed behavior remains required if a future model output violates the contract.

### Unresolved Issues

Separate accepted-artifact publication, public downloadable integrity, Background dependency adoption/deployment and fresh production verification remain pending owner tasks. No production success claim made here.

### Architectural Concerns

None within approved scope; all previous selection, shipping-evidence, chronology, security and budget behavior remains validated.

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Notes

Reviewed actual final7b5c4a6158e81104ddcfe222de74028bbc584897 and durable report9dad087a0. Provider root referralReason explicitly nullable string with unchanged canonical enum; ANSWER branch JSON-null const and referral branch string enum. One common private forced-envelope instruction applies to both existing correction paths. Strict validator, mandatory referral decisions, required fields and correction/step/deadline budgets unchanged. No normalization or extra retry. Historical invalid raw value is not inferred.

### Reviewed Files

response.ts, invoke-model.ts, provider contract and runner/selection regressions, installed public validators and package metadata; nine-file scope confirmed.

### Validation Reviewed

Four prior-code red regressions;112 focused/743 full pass3 expected skips; types, ESM+DTS build, installed immutable public JS/DTS and browser/Node exports. Independently hashed candidate SHA25671118ab02b14ffb36659a8cc6ba5caa91055bb8f3da48a23b3c731c7366ba6ed. Coordinator's final frozen-built-client and actual correction-node synthetic real-provider probe passed strict JSON-null ANSWER, version1 and two exact observed synthetic products. Probe used no customer context/provider commerce reads/DB writes/Meta sends and is not production proof. Physical preparation/isolation/sync evidence and diff hygiene verified.

### Architecture Conformance

Conforms to strict canonical provider contract guidance, Shared-first publication and bounded fail-closed execution. Existing semantic/chronology/shipping/security behavior retained. No private payload diagnostics or cross-owner edits.

### Follow-up

Developer may merge PR79. Shared006 Ready for sole exact accepted5.13.5 publication after merge, actual public downloaded hashes required before Background005. No repeated implementation validation in publication. Genuine production recommendations/footer proof remains pending.
