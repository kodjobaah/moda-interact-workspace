---
id: ARCH-070-SHARED-001
architecture_id: ARCH-070
title: Support absent storefront links for verified product-only recommendations
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
claimed_at: 2026-11-12T12:46:04Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Support absent storefront links for verified product-only recommendations

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Support absent storefront links for verified product-only recommendations without relaxing existing production security or lifecycle guarantees.

## Context

MCP valid catalogue products can have onlineStoreUrl null, but existing Shared recommendation schema/render requires a link. Background must consume a canonical safe contract rather than weaken verification.

## Scope

Shared recommendation presentation schema/render and directly related tests/types; approved5.13.3 package metadata. Publication task scope is only accepted-artifact release mechanics.

## Out of Scope

Background/MCP implementation, basket mutation URL relaxation, fabricated URLs, credentials, unrelated refactors and live customer sends.

## Requirements

Allow null recommendation product URL only in PRODUCT_ONLY scope while retaining verified product identity, price, stock and image fields. Renderer omits the product link when null; never fabricate a URL. Mutation/actionable recommendation scopes still require URL. Nonnull URLs retain HTTPS, no credentials, no unsafe ports, domain and existing security validation. Apply approved patch version5.13.3. Inspect existing exports before adding any reusable runtime helper.

## Work Items

- [x] Establish exact source/fixture cause and preserve a failing regression.
- [x] Implement only the owned correction.
- [x] Validate positive and failure/recovery behavior and report evidence.

## Interfaces / Contracts

Consume published Shared contracts and existing MCP product evidence / durable conversation lifecycle. No new wire or schema contract is authorized. Cross-repository gaps return to architect.

## Dependencies

None.

## Enables

Developer integration and production verification after architect acceptance of both tasks.

## Acceptance Criteria

- [x] Requirements demonstrated with deterministic positive and negative regression tests.
- [x] Existing tenant, domain, message identity and lifecycle guarantees preserved.
- [x] No duplicate delivery, live test send, secret logging or unrelated changes.
- [x] Completion Report records canonical launcher packet, physical isolation, synchronization and recursive submodule evidence.

## Validation

- [x] Focused schema/render tests for null PRODUCT_ONLY link omission, mutation null rejection, unsafe/non-HTTPS/auth/port/offdomain rejection; full Shared suite, typecheck/build, packed installed public exports and immutable artifact hashes.
- [x] Exact changed-file scope and secret hygiene review.

## Stop Condition

Complete owned work and required validation, set review, return report and STOP. Do not merge, deploy or begin another task.

## Implementation Notes

You are not alone in the codebase. Preserve others' changes. Use the prepared dedicated mirrored worktrees and task branch. Verify actual package scripts before running checks. Existing structured semantic logs suffice; do not introduce competing logging or repeated provider work as a diagnostic mechanism.

## Completion Report

### Status

Ready for Review — implementation `bf642ea` pushed on `task/ARCH-070-SHARED-001`; PR https://github.com/kodjobaah/moda-interact-shared/pull/77. No merge or publication performed.

### Files Changed

- `src/commerce/presentation/schemas.ts`: discriminated recommendation scopes permit nullable URL only for PRODUCT_ONLY. Other scopes keep required safe URL; existing same-origin check skips only null.
- `src/commerce/presentation/render.ts`: matching discriminated public type; omit only absent product-link line. Existing title, quantity, prices, terms and formatting remain unchanged.
- `src/commerce/presentation/recommendation-url.test.ts`: source regression, canonical schema-to-preview body, all 20 locales, mixed linked/linkless recommendations, mutation null/undefined rejection, URL security negatives and valid mutation links.
- `scripts/validate-commerce-outreach.mjs`: existing installed-public-package smoke additionally verifies nullable catalogue JS rendering/schema and strict-null declaration safety for actionable scopes.
- `package.json`, `package-lock.json`: approved 5.13.3 metadata only; dependencies unchanged.

### Work Completed

Verified existing strict product URL schema rejected valid linkless catalogue products. Recorded two positive-test failures before implementation; mutation and safety negatives already passed. Implemented only catalogue presentation nullability and link omission. No fabricated URL, new identity source, stock/sale/image relaxation, provider work or customer send.

Physical worktree isolation and prepared launcher evidence:

- Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-070-SHARED-001`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-070-SHARED-001`; both branch `task/ARCH-070-SHARED-001`.
- Shared/default checkouts switched/mutated: no; another task worktree reused: no.
- Parent and implementation remote task branch fast-forwards not needed; both origin/main already current.
- Recursive submodule sync/update passed; no entries.
- Durable claim `861ccee9c6a1ac0a32c296da190f1cdb4216268d`; implementation base `ea82023e831e77cd4c964df9a697ad17a9c1a1fb`.

### Validation Results

- Before fix: new focused file had 2 positive failures (expected string, received null), 3 passing negative checks.
- Focused recommendation/presentation/image tests: 26 passed, 0 failed. Existing 60 multilingual golden recommendation outputs unchanged.
- `npm run typecheck`: passed.
- `npm test`: 722 total; 719 passed, 0 failed, 3 expected integration skips.
- `npm run build`: ESM and declarations passed.
- `node scripts/validate-commerce-outreach.mjs /tmp/modainteract-moda-interact-shared-5.13.3.tgz`: passed against installed exact immutable artifact; all public export targets present, nullable catalogue schema/preview accepted, both null actionable scopes rejected; strict-null declaration fixture rejects null mutation URL.
- `npm run validate:commerce-presentation`: Node and browser-like public imports passed.
- `npm run validate:commerce-entrypoints`: passed.
- Changed-file scope and `git diff --check`: passed; no credentials/private payloads added.
- Exact candidate `/tmp/modainteract-moda-interact-shared-5.13.3.tgz`; SHA256 `34b17b2fd6fd4ec2dc9043ee8d2e6cd5d77c804b3b9c58b0f91f1d25f3175b5e`; npm SHA1 `5d5de64a07a7a820bfff759153df2b6b7c70c9ee`; integrity `sha512-x2vu8tD4Vs9fzIGNLPc/4McxXsz96xiZjLUzaXUEvK2ShuU6RZcWP8N3nxmdc3rP3Qg/5PH+dyhp/9iw82WBWA==`.

### Deviations

Initial added installed smoke fixture had a duplicate schema import; corrected only that fixture and reran packed/export checks. No implementation source, build or full suite repetition after artifact packing. Scripts are excluded from packed files (confirmed zero scripts entries), and exact candidate hash remained unchanged.

### Assumptions

Background remains verified product evidence/lifecycle owner and must adopt the published nullable presentation contract in its separate dependent task. Mutation/actionable scopes remain nonnullable and same-shop verified.

### Unresolved Issues

Separate accepted-artifact publication and public downloadable-byte integrity verification are required before Background adoption. No production behavior or deployment verification claimed here.

### Architectural Concerns

None beyond the expressly approved nullable PRODUCT_ONLY contract extension. Other scopes and existing provider/tenant/message/lifecycle boundaries remain unchanged.

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
