---
id: ARCH-073-BACKGROUND-002
architecture_id: ARCH-073
title: Compose tenant shop headers before immutable recovery sends
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 20
executor: codex
claimed_at: 2026-11-12T19:19:48Z
attempt: 1
depends_on:
  - ARCH-073-BACKGROUND-001
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Compose tenant shop headers before immutable recovery sends

## Architecture

ARCH-073; docs/architecture/ARCH-073-tenant-recovery-shop-headers.md; coordinator moda_architect.

## Objective

Prepare deterministic shop-name and verified-website text headers on eligible recovery messages before immutable send preparation.

## Context

Current main lacks preserved Shopify name acquisition; wrappers cannot render a missing ShopBrand name. User requests generic shop branding, never a hardcoded single-shop patch.

## Scope

Background wrapper/local trusted context/composition, HUMAN dual provenance/frozen replay, eligible notice admission paths and corresponding tests/docs. Prefer existing wrapper contracts; no new Shared variable without returning a concrete gap.

## Out of Scope

Logo/media enablement, read_brand/other permission changes, privileged Brand queries, wholesale historical merge, unrelated token refactor, production DB backfill, schema/new namespace/Shared release, other repositories, live sends or deployment. Return genuine cross-owner gaps.

## Requirements

Header uses exact authorized shop persisted name and verified stored domain, never model text or hardcoded alias. Use verified-domain-only fallback for missing name; do not suppress an otherwise legitimate reply or guess a display name. No logo or extra media sends. Cover eligible AI/HUMAN configured/passthrough and service/limit/audio/oversize notices; approved templates, unbound routing and forbidden sends stay excluded. Preserve configured header content and human-authored bytes; avoid duplicate mandatory header blocks. Compose header and existing divider/checkout footer before freeze/hash/media/moderation/permit, provider body identical. Strict provenance checks both preparation and persisted replay; old frozen bodies byte-identical. Length/caption fallback keeps full safe body or refuses before admission. Preserve tenant/control/inbound/version/lease fences. Document rolling old-reader drain if new evidence cannot old-decode.

### Header contract clarification

Approved text layout is shop name, then verified HTTPS website, then neutral divider and blank line before the existing body/footer. Missing name uses only verified website without guessing or suppressing an otherwise legitimate reply. Safe single-line display names cannot inject controls/markup into identity; retain stored identity without inventing aliases. Validate/canonicalize website from exact authorized stored Shop.domain, never customer/model text. Background-local context/receipt extension is sufficient; no Shared variable enum/release.

Shared presentation brandName currently validates projection identity but does not add a header. Deduplicate only a proven pure-identity configured-wrapper header derived from its typed tokens; never heuristically remove words/URLs from HUMAN authored bytes or body text. Retain custom merchant header prose. Bind optional header identity/receipt digest through fresh application keys, no-wrapper exact transform, HUMAN preparation, persisted evidence and final-permit validation. Evidence-absent old records retain old hashes/bytes. A receipt is not tenant authority; its source is the verified local context. No new logo/media behavior belongs to this task.

## Work Items

- [x] Implement only the bounded capability and document compatibility/rollout.
- [x] Add meaningful prior-behavior red and regression/concurrency/security coverage.
- [x] Complete required validation and mirrored task report/push.

## Interfaces / Contracts

Background-local current authenticated Shopify token and ShopBrand persistence; existing published Shared schemas/logging remain canonical. No new cross-service wire is planned.

## Dependencies

ARCH-073-BACKGROUND-001

## Enables

Developer integration and genuine production verification.

## Acceptance Criteria

- [x] Required bounded behavior works without hardcoded identity or broader permissions.
- [x] Tenant/domain, immutable state, authorization and concurrent-update boundaries remain enforced.
- [x] Existing unrelated media/frozen content is preserved; no secret/private proof committed.
- [x] Canonical dedicated mirrored worktree/synchronization/recursive submodule evidence recorded.

## Validation

- [x] Prior behavior red plus AI/HUMAN configured/unconfigured and all eligible notice header coverage; name/domain freshness/tenant mismatch/missing-name fallback.
- [x] Configured-header preservation/idempotence, human authored exact transform, old frozen replay/tamper and footer coexistence.
- [x] Real PostgreSQL freeze/moderation/final permit/provider body identity and race refusal; limits/caption fallback and security/template exclusions.
- [x] Types, task-owned lint, declared build and exact-head full CI; inspect package scripts first.
- [x] Diff/secret hygiene; synthetic fixtures and mocked providers, no real Meta send or production write.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete, submit review report and STOP. Do not merge/deploy or begin enabled work.

## Implementation Notes

You are not alone. Preserve others' changes. Use prepared canonical packet. Root owns final merges/deployment; architect owns acceptance. Read historical code as evidence, not permission to restore unrelated behavior or stale API assumptions.

## Completion Report

### Status

Ready for Review. Implementation task branch and mirrored parent report branch pushed; awaiting moda_architect review. No merge or deployment performed by this agent.

### Files Changed

- Background-local recovery shop header helper, application-key helper and SQL current-identity verifier.
- Wrapper contracts/context repository/service and AI adapter; HUMAN preparation, persisted evidence and final send fence.
- Outbound admission/delivery and turn-processor receipt forwarding.
- Focused wrapper, HUMAN, notice, turn and image-caption tests; real PostgreSQL header identity/race tests and existing footer exact-body expectation.
- Implementation PR: https://github.com/kodjobaah/moda-interact-background/pull/209
- Final implementation head: `b0216b1e52ce0d2619b84ca2298c31013dbe93a6` on `task/ARCH-073-BACKGROUND-002`.

### Work Completed

Deterministic eligible recovery text begins with the exact safe persisted name, verified HTTPS Shop.domain, neutral divider and blank line before the existing body/footer. Missing/unsafe/over-512 names fall back to verified-domain-only. Unsafe domains omit branding with bounded shared-logger diagnostic; no guessed alias, external lookup or broader permission.

The local receipt is projected only from verified recovery tenant context. It is bound into application keys, retained on replay and HUMAN JSON evidence, passed through known notice/AI admission, and compared to current Shop/ShopBrand under SQL locks before final permit. Header composition precedes media choice, freeze, whole-body moderation and provider dispatch. Pure-identity typed configured headers deduplicate; custom configured prose and original staff bytes remain intact. No schema or Shared contract change.

### Validation Results

- Prior-behavior RED: new header test failed on the original missing prefix; first GREEN then passed.
- Focused wrapper/HUMAN/delivery/turn suite: 11 files / 238 tests passed. Added configured/custom header, immutable replay/receipt loss, second tenant, image caption and long-caption TEXT fallback tests: 44 tests passed. Final C1/RTL/name/domain boundary follow-up: 21 tests passed.
- Real disposable PostgreSQL/Redis: `node scripts/test-integration.mjs tests/integration/arch073-recovery-header.integration.test.ts tests/integration/arch072-recovery-footer.integration.test.ts` passed 7 tests. Covers frozen/persisted/provider body equality and committed name/domain races while waiting for Shop locks, cross-tenant refusal and existing footer/admission identity.
- `npx tsc --noEmit` passed; scoped ESLint passed; declared `npm run build` on combined asset/header tree completed with `BUILD_EXIT=0` (Prisma, worker/provision TypeScript and packaging).
- Exact final-head full CI Type-check + unit tests both SUCCESS: https://github.com/kodjobaah/moda-interact-background/actions/runs/43294814356 and https://github.com/kodjobaah/moda-interact-background/actions/runs/43294804692 at `b0216b1e52ce0d2619b84ca2298c31013dbe93a6`.
- Diff/check and synthetic fixture review clean; providers mocked; no live Meta send, production setting write, secret or provider credential committed.

Physical worktree isolation (launcher packet `/tmp/moda-arch073-bg002-prepare.json`): canonical primary root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-073-BACKGROUND-002`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-073-BACKGROUND-002`; both branch `task/ARCH-073-BACKGROUND-002`. No shared checkout switched, no other task worktree reused. Prepared claim `d4822ca49a7813952d456664f3cb429eb770812d`, codex attempt 1.

Start-of-attempt parent/implementation remote-task fast-forwards not needed; both origin/main already current. Recursive implementation submodule sync/update passed; database initialized at recorded `5329d5390d346042895219663f3a040ea54ae168`. Before final CI, fetched and merged current implementation main `22e39d34e44c2ced066bb35cc242338c2b289dd6` cleanly into the task branch; parent origin/main rechecked already current. No gitlink staged.

### Deviations

Root/architect clarified safe name length to existing Shared 512 bound and preservation of ordinary punctuation; controls/bidi/newlines and actual markup delimiters fall back without truncation. Final narrow control-range regression added after the first combined-head build; exact final-head CI typecheck/full unit pass confirms it.

One extra-shell Node bootstrap attempt failed to resolve the canonical root because that shell omitted the workspace-root environment; no dependency/toolchain mutation occurred. All successful validation used the existing officially bootstrapped Node session. No doctor or unrelated baseline reinvestigation.

### Assumptions

The existing typed-commerce no-wrapper adapter trusts its internal renderer for normalized presentation text. Receipt-loss is strictly detected for actual rendered application keys, plain exact transforms and HUMAN frozen evidence; arbitrary mutation of that trusted internal normalized mock seam is not claimed cryptographically distinguishable from historical output. Actual service emits and forwards the receipt and SQL current-identity checks it. This preserves the approved local boundary without a cross-service/schema redesign.

### Unresolved Issues

None within assigned text-header scope. Root owns final merge/deployment and genuine production verification. Logos remain separate tasks.

### Architectural Concerns

Rollout must drain old messaging workers before generating new HUMAN prepared commands. Old readers cannot validate the new optional receipt/application-key additions and will refuse those preparations. Receipt-absent historical frozen records keep old algorithms and bytes; they are never rebranded or rewritten. New identity mismatch refuses a prepared send rather than rewriting content after moderation. Existing tenant/control/inbound/lease/consent fences remain authoritative.

## Architect Review

### Review Status

Accepted

### Review Notes

Reviewed actual final `b0216b1e52ce0d2619b84ca2298c31013dbe93a6`, complete report `654f3ff3c`, final control-range delta and asset-main integration. Verified per-tenant safe-name/domain header, domain-only fallback, typed configured-prefix dedup, receipt-bound local application/HUMAN replay and current Shop-locked permit check. No findings.

### Reviewed Files

Header helper/application-key/context repository/service, AI adapter, HUMAN preparation/evidence/current validator, processor/admission/delivery receipt forwarding, recovery fence/current identity helper, unit and real PostgreSQL tests.

### Validation Reviewed

Prior-code red, focused238/additional44/final21, disposable PostgreSQL7 frozen/send identity and rename/domain lock races; types/scoped lint/combined build; both exact final-head CI passed. Prepared canonical mirrored isolation/submodule evidence and clean merged asset main are recorded. No duplicate architect run required.

### Architecture Conformance

Conforms to Background-local text header with no schema/Shared change or extra permission. Old receipt-absent records preserve old key/body bytes. Existing trusted normalized typed-commerce renderer seam is explicitly retained, not claimed cryptographically resistant to arbitrary internal mock metadata stripping; actual service forwards proof and final checks. Security, footer, authored bytes and immutable permit preserved.

### Follow-up

Developer merges/deploys and drains old messaging workers before new HUMAN receipt preparation. Verify genuine name/site header/footer delivery. BG004 becomes Ready only with all accepted prerequisites; canonical preparation should incorporate actual merged header main. Logo readiness/fallback remain separately owned.
