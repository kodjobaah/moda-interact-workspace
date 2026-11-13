---
task_id: LOCAL-RECONCILE-DOCUMENTATION-001
repository: moda-interact-documentation
assigned_agent: default
coordinator: moda_architect
status: ready
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

Pending preparation and architect exception review. Main integration and any
deployment/publication remain root-owned and have not occurred under this task.
