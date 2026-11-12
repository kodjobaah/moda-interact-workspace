---
id: ARCH-070-BACKGROUND-004
architecture_id: ARCH-070
title: Adopt canonical selection semantics and bounded shape diagnostics
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
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

# Adopt canonical selection semantics and bounded shape diagnostics

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Adopt canonical selection semantics and bounded shape diagnostics within existing verified and bounded execution contracts.

## Context

Provider-free reproductions prove schema-valid missing-version/nonempty-list can skip runner repair but host drops the list; truthy null/null shipping without disposition similarly skips repair but host discards it. Fresh production version6 exact raw final shape is unavailable, so historical exact cause is not claimed. Existing accepted null-URL/footer/terminal fixes remain valid.

## Scope

Exact published5.13.4 dependency/lock and existing recommendations/disposition.ts normalization consumer, host shape-only diagnostic and directly related host/selection tests.

## Out of Scope

Unrelated refactors, provider/model changes, fabricated selections or automatic product choice, new queue retry loop, broader schema/infra/credential/consent changes, live customer sends or resetting processed input.

## Requirements

Replace duplicate local semantic parser mechanics with published Shared helper, preserving host domain policy and exact normalized behavior. Add bounded shape-only diagnostics needed to distinguish pair presence/count/type/disposition/shipping eligibility, never reply prose/private prompts, tokens/credentials or full payload. Use existing shared structured logger, no generic logger or duplicate framework telemetry. Keep host fail-closed verified selection/evidence checks; no inferred version/IDs, product auto-selection, new retries, schema or credentials. Exercise malformed pair and null-shipping prior bypass through actual published bounded runner repair, valid corrected selection and refusal on exhaustion. Preserve all accepted nullURL/footer/terminal fixes on final current main.

Runtime evidence clarification: missing-product-selection guard must test actual verified shipping presentation/evidence, not a truthy model shippingInformationSelection object. Valid static STANDARD plus null/null selection alone cannot authorize unsupported prose after product searches. Preserve genuinely verified shipping-only answers and strict domain/identity checks. Test unobserved, failed/mismatched shipping versus positive authorized observation; no additional retry loop.

Shipping evidence precision: selectShippingPresentation may return a truthy limitation for provider/identity mismatch, so object presence alone is insufficient. Use the published canonical shipping-result/selection qualifier on fresh output with known expected platform before allowing shipping evidence to satisfy the missing-product-selection guard. Preserve matched null/null policy-unavailable truthful limitations and no-product-observation shipping-only flow. Reject provider/product/variant mismatch and malformed/unrelated result. Share qualifier mechanics; do not duplicate local parsing or add calls/loops.

## Work Items

- [x] Reproduce both semantic gaps deterministically against prior implementation.
- [x] Implement only owned canonical semantic correction/adoption.
- [x] Prove compatibility and bounded failure behavior; report exact validation.

## Interfaces / Contracts

Shared owns canonical semantic normalization and repair eligibility; public package @modainteract/moda-interact-shared/commerce. Background consumes published helper and retains tenant/provider/evidence policy. Existing schemas, normal answer contract and budgets remain compatible.

## Dependencies

ARCH-070-SHARED-004. Publication additionally requires developer merge of accepted implementation.

## Enables

Next publication/consumer task in ARCH-070, then developer production verification.

## Acceptance Criteria

- [x] Requirements hold, including unchanged security and bounded failure behavior.
- [x] Canonical reusable mechanics are not duplicated across Shared/Background.
- [x] No private prose, prompts or secret payloads added to diagnostics.
- [x] Prepared mirrored worktree, start-sync and recursive submodule evidence recorded.

## Validation

- [x] Clean public exact artifact install/hash, semantic compatibility vectors and actual local host/runner tests, no provider/Meta sends, changed-file lint/types and final combined full CI. Existing untouched main lint baseline remains documented; no unrelated cleanup.
- [x] Exact changed-file scope and diff/secret hygiene.

## Stop Condition

Complete owned work and required validation, set review, return report and STOP. Do not merge, deploy or begin another task.

## Implementation Notes

You are not alone in the codebase. Preserve others' changes. Use the prepared dedicated mirrored worktrees and task branch. Verify actual package scripts before running checks. Existing structured semantic logs suffice; do not introduce competing logging or repeated provider work as a diagnostic mechanism.

## Completion Report

### Status

Ready for Review. Implementation and validation evidence committed/pushed; awaiting moda_architect review.

### Files Changed

- `package.json` / `package-lock.json`: exact public Shared 5.13.4 adoption, canonical registry integrity.
- `src/commerce/recommendations/disposition.ts`: re-export exact canonical Shared parser; derive local compatibility type from its return instead of duplicating normalization.
- `src/commerce/host.ts`: original/fresh shipping observation qualification with expected provider and exact selected identity; bounded selection shape diagnostics; actual verified shipping guard and evidence-backed generic policy intent.
- `tests/integration/commerce/host-suites/selection-semantics.ts`, host composition entry point: actual published runner/host tests, forced single correction and exhaustion, shipping compatibility/security and diagnostic privacy.
- Canonical adapter unit vectors and three existing package-version consumer assertions.

### Work Completed

Prior provider-free 5.13.3 proof reproduced schema-valid missing recommendation version/list pair accepted by runner but discarded by host, and unobserved shipping placeholders bypassing repair. Historical raw production version6 response remains unavailable; its exact shape is not claimed.

Consumed exact published 5.13.4 canonical semantics and existing one-correction runner. Background has no new correction/retry loop and does not infer versions, product identifiers or recommendations. Host qualifies both original authorized current-turn and fresh shipping DTO using Shared helper plus known platform, before treating presentation as evidence. Provider/product/variant mismatch cannot qualify a truthy limitation. Disposition-only generic policy intent is derived only from recognized SHIPPING_INFORMATION_UNVERIFIED plus a qualified current-turn generic null/null observation, followed by existing budgeted fresh verification. Matched NOT_REQUESTED null/null unavailable-policy limitations and no-product shipping flow remain compatible. A fallback product cannot authorize unverified shipping disposition.

Diagnostics use the existing Shared structured logger and existing commerce.response.composition event. Emitted structural states are bounded enums/counts/booleans; arbitrary key names, reply prose, prompts, identifiers and full payloads are excluded from shape diagnostics. Strict scalar type checks prevent array/string-coercion leakage. No custom generic telemetry, provider writes, Meta sends, queue changes or production replay.

### Validation Results

- Fresh public npm cache `/tmp/moda-arch070-bg004-public-cache`: exact canonical5.13.4 tarball GET HTTP200/cache miss; installation succeeded. Public artifact dependency gate independently verified511919 bytes/SHA256fcf2cc8d78c327b85a6de777541ea5ba53b659079234e790aec3d0fd97b47693. Lock preserves npm canonical registry URL/integrity sha512-EXNoSmbmB3E+hK1bNArMr5dsfZSQ2gHTV4/EoSj8coSCdHepdLfPD9aN2YTEOgYZ9Rwi6mNa9OT/ZBlqCDdJjg==.
- Prior-host red shipping regression: 4 failed /1 passed, proving old truthy shipping bypass and fallback-present gap. Source restored unconditionally; no other files reverted.
- Actual published runner→host: final immutable-head full host suite106/106 passed. Missing-version and unobserved shipping correction forced exactly one finalResponse-only retry; corrected exact observed products accepted; exhaustion refused with no repeated provider reads.
- 62 focused tests across15 files passed serially: canonical parser identity/vectors, recommendations, installed model boundary, observability package/version and recovery notice consumers.
- Final `tsc6 --noEmit`: passed. First concurrent typecheck raced initial Prisma generation; rerun after generation passed. No source workaround for generated artifacts.
- Changed-file ESLint passed; existing untouched main four-unused-declaration lint baseline remains unchanged and excluded from task cleanup.
- `git diff --check` passed; scoped diff and secret/prose hygiene checked.
- Unit/host commands explicitly use loopback port1 DATABASE_URL/REDIS_URL and test deployment environment; host uses local MCP/model fixture and fake DB. No live services used.
- Implementation a80afe5c8ef95a15bfe5e0486eaf79e3ae12aa9c, PR https://github.com/kodjobaah/moda-interact-background/pull/203. Both required final-head full CI runs passed3,985 tests/368 files, including clean dependency install/Prisma generation/typecheck: https://github.com/kodjobaah/moda-interact-background/actions/runs/43239779043 and https://github.com/kodjobaah/moda-interact-background/actions/runs/43239799745. No further source changes.

### Physical Isolation / Preparation Evidence

Authoritative packet `/tmp/moda-arch070-bg004-prepare.json`, ARCH-070-BACKGROUND-004, attempt1 codex; claim e00e9bc749c61b9fcb9d42f965ad524a0c212df6 committed/pushed by launcher. Workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-070-BACKGROUND-004`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-070-BACKGROUND-004`; both branches `task/ARCH-070-BACKGROUND-004`. Shared/default workspace or implementation checkouts switched/mutated: no. Another task worktree reused: no.

Start synchronization: parent and implementation remote-task fast-forward not needed; both origin/main already current. Implementation base244304adea723bcc18854e4f1bffcc25571d3346 includes all accepted recommendation/footer/terminal fixes. Recursive sync/update passed; database submodule5329d5390d346042895219663f3a040ea54ae168 initialized at recorded commit. Parent submodule gitlink not staged.

### Deviations / Assumptions / Unresolved Issues

No scope deviation. No schema migration, provider/model change, new calls/loops or inferred selection. Actual host integration verifies unchanged database interaction shape using fixture; no PostgreSQL contract changed. Production genuine-question verification and merge/deployment remain root/developer-owned after architect review. Historical exact raw production failure cause remains unconfirmed.

### Architectural Concerns

None newly discovered; implementation stops at review and does not claim architect acceptance or production success.

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Notes

Reviewed actual final a80afe5c8ef95a15bfe5e0486eaf79e3ae12aa9c and durable report1c8622d75. Exact public Shared5.13.4 pinned, local parser delegates published canonical mechanics. Host requires matching authorized current-turn and existing budgeted fresh shipping DTO provider/identity qualification; raw truthy selection or rendered mismatch limitation cannot bypass missing product selections. Generic disposition-only null/null intent requires matched observation, and fallback product does not authorize unverified shipping claims. Legitimate matched policy-unavailable limitations and no-product shipping remain compatible. Shape diagnostics use finite enums/booleans/capped counts without arbitrary coercion, prose or full payload. No new provider reads/loops or IDs/version inferred.

### Reviewed Files

commerce/host.ts; recommendations/disposition.ts; package/lock; actual published runner-host selection suite/registration, parser vectors and three pinned-version consumer assertions.

### Validation Reviewed

Actual prior-host red4fail/1pass; final host106/106 and62 focused; types/scoped lint/diff hygiene; exact public-cache install/integrity. Independently verified both final-head CI successes3,985 tests/368 files. Four untouched pre-existing full-lint unused declarations remain documented; no unrelated cleanup. Prepared mirrored worktree/start-sync/recursive database evidence verified. No live providers or database used in fixtures.

### Architecture Conformance

Conforms to Shared-first canonical runtime mechanics and tenant/provider/evidence boundaries. Existing null-URL/footer/terminal fixes preserved on current244304ad base. No schema, infrastructure, credentials, consent or queue changes. Historical version6 exact raw shape and successful production outcome remain unconfirmed.

### Follow-up

Developer may merge PR203 exacta80afe5 and deploy. Verify genuinely new customer question after final code Live, grounded recommendations, trusted footer, Meta acceptance and durable delivery. Do not reset/replay version6. Final parent gitlinks and architecture completion remain developer/coordinator-owned.
