---
id: ARCH-045-SHARED-002
architecture_id: ARCH-045
title: Publish Shopify consent-sync and canonical identity contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 21
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-045-SHARED-001
enables:
  - ARCH-045-SHOPIFY-001
  - ARCH-045-BACKGROUND-003
  - ARCH-045-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
  - ARCH-045-BACKGROUND-001
  - ARCH-046-BACKGROUND-001
  - ARCH-046-API-001
created: 2026-10-20
updated: 2026-10-22
---
# Publish Shopify consent-sync and canonical identity contracts

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** materialised through `/moda_developer_create ARCH-045-SHARED-002` and claimed as developer Attempt 1 (`claimed_at: 2026-10-22T09:49:18Z`). Publication of version `2.5.0`, accepted-source provenance, implementation branch/tag publication, and preparation evidence are reconciled below. The task is explicitly complete; architect review remains a separate governance record.

## Objective

Publish the review-accepted and completed combined **consent-sync event and canonical identity helpers** in one Shared package release, without changing runtime behaviour. A consent-sync job is not a checkout-recovery wakeup.

## Context

Shared publication must be a release gate separated from implementation; Shopify and Background cannot depend on unpublished sibling source.

## Scope

- Verify the combined SHARED-001 task is `complete` following the Accepted review and explicit completion decision required by its configured `completion_mode`. For this developer-owned prerequisite, an Accepted Developer Self-Review and Developer Completion Decision satisfy this dependency; a separate Architect Review record may remain Pending.
- Select/apply approved package version and publication metadata, publish using repository-defined release command.
- Record registry/version availability and exact package version for consumer tasks.

- Publish the **single accepted `ARCH-045-SHARED-001` implementation**, including both minimal Shopify sync schema and canonical exact-recipient/Shopify customer ID helpers. Pin the resulting version in each Node consumer; publication remains release-only, without rerunning implementation tests.

## Out of Scope

- No runtime behaviour, schema redesign, unit-test reruns, TypeScript refactoring or consumer code changes.

## Requirements

- [x] Only accepted implementation is published.
- [x] No unexpected source changes apart from approved release metadata.

## Work Items

- [x] Confirm accepted SHA/version and publication prerequisites.
- [x] Publish and verify exact registry package/version (`@modainteract/moda-interact-shared@2.5.0`).
- [x] Record the distribution evidence for `2.5.0` in the Completion Report.

- [x] Verify the `2.5.0` release package contains the consent-sync and identity outputs, and record `./shopify`, `./identity` and `./identity/fixtures` package exports. The accepted-source/release-tag provenance is checked separately before acceptance.

## Interfaces / Contracts

Publishes `@modainteract/moda-interact-shared` consent-sync **and** canonical identity exports from the combined SHARED-001. No new queue/recovery scheduler. Consumers must use the published version, not unpublished sibling source.

## Dependencies

- `ARCH-045-SHARED-001`

## Enables

- `ARCH-045-SHOPIFY-001`
- `ARCH-045-BACKGROUND-003`
- `ARCH-045-SYSTEM-TEST-001`
- `ARCH-045-SHOPIFY-003`
- `ARCH-045-SHOPIFY-004`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`
- `ARCH-045-BACKGROUND-001`
- `ARCH-046-BACKGROUND-001`
- `ARCH-046-API-001`

## Acceptance Criteria

- [x] Exact published version `2.5.0` is visible at the npm registry (`latest: 2.5.0` on the recorded check).
- [x] Verify that the release commit/tag for `2.5.0` matches the accepted SHARED-001 implementation (by ancestry or source equivalence) plus permitted release metadata.
- [x] All publication evidence recorded; no implementation change is mixed into publication.

- [x] The `2.5.0` release tarball lists the `identity` and `shopify` JavaScript/declaration entrypoints and portable JSON fixtures, with package exports for `./identity`, `./shopify`, and `./identity/fixtures`; the exact version is registry-visible. Downstream consumer installation/adoption is separately owned and is not claimed here.

## Validation

- [x] Check package version, release command exit status, registry visibility and source diff only; do **not** rerun code validation from SHARED-001.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

If an implementation correction becomes necessary, stop publication and refer it to moda_architect.

**Architect publication-dependency clarification (2026-10-22):** `ARCH-045-SHARED-001` is `complete` after a durable Accepted Developer Self-Review (Attempt 2) and explicit `/moda_developer_update ARCH-045-SHARED-001 complete` decision. The configured developer completion workflow satisfies SHARED-002's implementation prerequisite even though SHARED-001's separate `## Architect Review` remains Pending. This clarification does not waive verification of the selected release version, accepted-source provenance, launcher preparation evidence, or publication-only scope. Shopify, Background, and WooCommerce consumer integration remains within their respective dependent tasks.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

Complete — developer Attempt 1 reconciled, passed, and explicitly completed. Release `@modainteract/moda-interact-shared@2.5.0` was published and verified in the npm registry.

### Files Changed

- Release commit `777c2dd` (`v2.5.0`) changes only `package.json` and `package-lock.json` from accepted implementation commit `12f6ff5`; both refs are published on `task/ARCH-045-SHARED-002` and tag `v2.5.0`.
- This task-definition report is updated for publication evidence only. No implementation-source change is claimed.

### Work Completed

- Confirmed prerequisite `ARCH-045-SHARED-001` is `complete` (Attempt 2 Accepted Developer Self-Review and explicit developer completion) and records accepted implementation commit `12f6ff59583ad630e12e77ac6b0ae2f69e3a2cae`. Git comparison confirms release commit `777c2dd` is that accepted source plus version metadata only.
- Selected `2.5.0` with `npm version minor`, starting from installed package version `2.4.2`; release acceptance remains subject to the configured developer review workflow.
- Published `@modainteract/moda-interact-shared@2.5.0` to `https://registry.npmjs.org/` with tag `latest`; the successful `npm publish` and subsequent successful `npm view` are in the supplied terminal transcript.
- Confirmed package output includes `dist/shopify/index.js` and `.d.ts`, `dist/identity/index.js` and `.d.ts`, and `fixtures/identity-v1.json`. The supplied `package.json` exports `./shopify`, `./identity` and `./identity/fixtures`.
- Recorded registry tarball filename `modainteract-moda-interact-shared-2.5.0.tgz`, SHA-1 `47a33fe499d63f7b4f0f5e921497419b1e9f7105`, 112 files, and unpacked size approximately 1.1 MB.

### Validation Results

| Evidence | Result |
|---|---|
| `npm version` / `npm version minor` | **PASS** — version advanced from `2.4.2` to `2.5.0`. |
| First `npm publish` | **FAIL** — automatic `prepack` build could not find `tsup` (`exit 127`). No successful release claimed from this attempt. |
| `npm ci` | **PASS** — 211 packages installed; npm reported one low and one high vulnerability and install-script approval warnings. |
| Second `npm publish` | **PASS** — the repository `prepack` lifecycle automatically ran a successful `tsup` ESM/declaration build; npm returned `+ @modainteract/moda-interact-shared@2.5.0`. |
| Registry verification | First `npm view` returned **E404** during processing; the repeated `npm view @modainteract/moda-interact-shared@2.5.0` **PASS**, showing `latest: 2.5.0`, tarball URL, and matching SHA-1. |
| Tarball/package-shape evidence | **PASS (manifest/output inspection)** — the npm release file list and supplied `package.json` show Shopify and identity exports and portable fixture JSON. No downstream consumer installation was run or required here. |
| Release commit/tag, source diff, `git diff --check` | **PASS** — `777c2dd`/`v2.5.0` differs from accepted `12f6ff5` only in `package.json` and `package-lock.json` version metadata; diff check passed. |
| `/moda_developer_create` `--prepare` synchronization/recursive-submodule packet | **PASS** — Attempt 1 packet recorded parent `d4492fa1`, implementation `93dc666e`, recursive submodule readiness, dependency gate, and claim commit `9c45e6d5`. |

Source: developer terminal capture `Pasted text(20261022-095355).txt` and the supplied `moda-interact-workspace-ARCH-045-SHARED-002.zip` snapshot. Publication commands are not to be rerun merely to obtain documentation evidence.

### Deviations

- The initial `npm publish` failed because `tsup` was not installed. The developer then ran `npm ci` and retried publication successfully; no runtime implementation changes are evidenced by the supplied transcript.
- The successful `npm publish` automatically ran the package's `prepack` build. That is an npm lifecycle side effect, **not** a separate test/lint/typecheck run requested by this release task. Because the architect publication policy excludes rerunning implementation builds, this side effect is recorded for review rather than silently described as publication-only validation.
- `npm ci` reported two dependency vulnerabilities and install-script approval warnings. No `npm audit fix`, dependency upgrade or unrelated package change is authorised by this publication task.

### Assumptions

- For this developer-executed publication, the accepted Attempt 2 developer self-review and explicit `complete` state of SHARED-001 satisfy the task dependency; this is distinct from the still-Pending separate Architect Review entry in that predecessor's task record.
- The successful registry response demonstrates `2.5.0` distribution, but not, by itself, the precise Git source commit/tag or absence of non-release modifications. Consumer imports and lockfile pinning are separate repository-owned work.
- ARCH-045 does not impose a consent-expiry window; current Shopify consent and checkout eligibility remain separate.

### Unresolved Issues

1. Log dependency-audit warnings as release observations; handling any newly required security correction belongs to an authorised owning implementation task, not opportunistic work in this publication task.

### Architectural Concerns

The published package exposes the single Shared consent-sync and identity contracts. No Shopify, Background, WooCommerce or API adoption is claimed by this release task. Downstream tasks must import the exact published version and retain consent/recovery side-effect boundaries.

## Developer Takeover Amendment — 2026-10-22

The developer explicitly invoked `/moda_developer_create ARCH-045-SHARED-002` for this agent-owned publication task. The task is transferred to developer execution with developer-controlled completion while preserving the assigned agent `moda_shared`, repository ownership, publication-only scope, dependency, acceptance criteria and validation requirements. The canonical launcher will record the Attempt 1 claim after this amendment is published.

### Developer Self-Review - Passed/Accepted (Attempt 1)

- Attempt reviewed: 1. The published package `@modainteract/moda-interact-shared@2.5.0` is visible from npm with the recorded tarball and checksum.
- Release commit `777c2dd`, tag `v2.5.0`, and remote task branch `task/ARCH-045-SHARED-002` are published. The release differs from accepted SHARED-001 commit `12f6ff5` only in permitted `package.json` and `package-lock.json` version metadata.
- The launcher preparation packet records the canonical parent and implementation worktrees, dependency gate, recursive submodule readiness, and durable Attempt 1 claim. Both current task worktrees are clean and branch parity is `0 0`.
- No implementation validation was rerun; publication-only package/version, registry, provenance, and source-diff checks passed. The initial missing-`tsup` publish attempt, npm audit warnings, and install-script warnings remain recorded as release observations.
- State before explicit completion: `status: review`, `executor: null`, `claimed_at: null`, `attempt: 1`.

### Developer Completion Decision (Attempt 1)

- The developer explicitly invoked `/moda_developer_update ARCH-045-SHARED-002 complete` after the durable Attempt 1 Passed/Accepted review.
- All Work Items, Acceptance Criteria, and publication-only Validation gates are checked. Release commit `777c2dd` and tag `v2.5.0` are published; the parent task report is committed and pushed.
- No merge to `main` was required or performed. Downstream consumer adoption remains owned by the enabled dependent tasks.
- State transition: `status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1`.

## Architect Review

### Review Status

Developer self-review Accepted; task Complete — Attempt 1. No independent architect code-diff re-review was performed in this coordination pass.

### Review Notes

**Coordination reconciliation — 2026-10-22 (documentation only):** The canonical task YAML is `complete` at Attempt 1; its later developer Passed/Accepted self-review and explicit completion decision are the latest recorded outcome. Historical Architect Review status before this reconciliation: "Pending — no implementation reviewed.". All prior findings and validation notes below are preserved as historical evidence; no tests were rerun, Git remote state was not rechecked, and this is not a new independent implementation acceptance.

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
