---
task_id: LOCAL-RECONCILE-DOCUMENTATION-001
repository: moda-interact-documentation
assigned_agent: default
coordinator: moda_architect
status: in_progress
execution_mode: agent
completion_mode: agent
executor: default
attempt: 1
claimed_at: 2026-11-13T15:07:43.867649+00:00
updated: 2026-11-13
---

# Preserve local video production functionality

## Explicit execution exception

The user requested review, preservation, testing and integration of remaining
local functionality across the workspace. Root explicitly assigned this bounded
Documentation task because the canonical launcher has no Documentation route.
This task does not add or change routes, agents, architecture task schemas or
the launcher. It uses the normal dedicated parent and implementation worktree
topology, mirrored `task/LOCAL-RECONCILE-DOCUMENTATION-001` branches, source/report
publication and independent architect review. Root retains all main-branch
integration authority. The exception is limited to task preparation/claim
mechanics for this repository, not isolation, review, VCS or publication rules.

Before implementation, the architect reviews this exception and the bounded
scope. The executor records that review, then creates the dedicated source
worktree and records its clean synchronized baseline. The primary checkout is
read-only source material and must remain unchanged.

## Preservation and audit

Root completed and verified all-repository Git bundles, staged/unstaged binary
patches and nonignored untracked-file archives before source preparation:

`/Users/kwadwoadomafriyie/project/moda-local-reconciliation-backup-20261113T145749Z`

Documentation's primary checkout and freshly fetched `origin/main` both resolve
to `9405661b6835216b1d5586ca7492fe7e1d66f89a`. The local video profile edits and
four JSON source inputs are absent from main. Existing narration and storyboard
tests/code already read the untracked JSON paths, so these are required inputs,
not generated recordings. All original local files remain preserved.

## Owned source scope

- `README.md`
- `automation/README.md`
- `automation/src/video/merchant-demo-voiceover.ts`
- `automation/src/video/merchant-demo.ts`
- `automation/src/video/merchant-onboarding-voiceover.ts`
- `automation/src/video/merchant-onboarding.ts`
- `automation/src/video/video-quality.ts`
- `automation/tests/video-quality.test.ts`
- Narrow `automation/src/capture/runner.ts` optional-timeout call-site correction and directly related unit test, as authorized below.
- `videos/merchant-demo/storyboard.en.json`
- `videos/merchant-demo/voiceover.en.json`
- `videos/merchant-onboarding/storyboard.en.json`
- `videos/merchant-onboarding/voiceover.en.json`

Port the reviewed local functionality selectively onto current main, preserving
existing safety controls. Correct defects directly exposed by these changes
within the owned video profile/pipeline/tests. Do not publish raw captures,
identity-bearing files, model files, media exports, `commands/splice.sh`,
`hey.py`, shell transcripts or unrelated local tools.

## Required behavior

The intended capture profile uses a 1600×900 CSS viewport, DPR 2.4 and a
3840×2160 recording surface. Intermediate trimming and final composition retain
UI text fidelity, narration timing and captions. Both merchant walkthrough and
onboarding paths use a shared, validated profile. Checked-in English storyboards
and voiceovers make existing plan/narration configuration loading reproducible.

Do not weaken privacy redaction, safe-scene selection, explicit onboarding
mutation consent, source-integrity checks, required healthy Free-plan outcome,
locale bounds, output overwrite controls or deterministic scene ordering.

## Validation

- Run the existing Documentation typecheck, unit suite and capture plan command.
- Validate all four source JSON inputs against the existing loaders and tests.
- Perform a small offline Playwright/FFmpeg recording/render verification of
  actual output resolution and the quality-profile path; avoid a constant-only
  assertion masquerading as video validation.
- No network/store/customer/browser-session calls, real onboarding mutation,
  production recording, model download or external publishing.
- Check source diff/format and ensure only owned source files are staged.
- Record any unavailable tool or baseline failure precisely; no invented pass.

## Completion report

### Attempt 1 — In Progress

Physical worktree isolation:

- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-LOCAL-RECONCILE-DOCUMENTATION-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/LOCAL-RECONCILE-DOCUMENTATION-001`.
- Both branches: `task/LOCAL-RECONCILE-DOCUMENTATION-001`.
- Shared/default checkouts switched or mutated for source work: no.
- Another task worktree reused: no.

Start-of-attempt synchronization:

- Primary root derived from its Git common-directory/worktree identity.
- Both task branches newly created from their own freshly fetched `origin/main`.
- Parent remote task branch fast-forward: already current.
- Parent mainline merge: already current (`a879371dd606a8daa8364ce09146a1a82d6a136e`).
- Documentation baseline: `9405661b6835216b1d5586ca7492fe7e1d66f89a`.
- Source task worktree clean before claim: yes.
- Recursive source submodule sync/update/status: passed, no nested submodules.
- Mechanical claim delegated by root under the explicit route exception.

Implementation, validation, publication and final review are pending. No
implementation gitlink is staged. Main integration and external publication are
root-owned and have not occurred under this task.

## Architect review

### Preparation exception — Accepted

The architect reviewed exact parent record `44abadabe` and accepted the bounded
non-ARCH Documentation route exception before source implementation. The
acceptance requires the normal isolated mirrored branches, claim metadata,
source whitelist, meaningful offline video proof, privacy/mutation controls,
source/report publication and independent final review. No new launcher route,
agent or architecture framework is authorized. Final implementation review is
pending.


## Architect scope refinement — 2026-11-13

The required full validation exposed four pre-existing exactOptionalPropertyTypes failures in the capture runner passing timeout:undefined to the locked Playwright API. The user's explicit test/fix instruction and this coordinator authorize a bounded correction at those four existing calls: omit the timeout option when undefined while preserving every explicit numeric value (including zero) and the established default behavior. Prove unchanged-main baseline first and add direct meaningful option forwarding tests; no scene selection, credential, privacy, capture mutation or time-limit redesign. This is part of restoring the existing documentation pipeline validation, not permission for unrelated capture refactoring.
