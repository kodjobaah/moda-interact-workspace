---
id: ARCH-011-SHARED-002
architecture_id: ARCH-011
title: Publish accepted ARCH-011 Shared billing contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: automatic
status: pending
priority: 12
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-011-SHARED-001
enables:
- ARCH-011-BACKGROUND-002
- ARCH-011-SHOPIFY-001
- ARCH-011-ADMIN-001
created: 2026-09-14
updated: 2026-09-14
---
# ARCH-011-SHARED-002

## Preconditions
SHARED-001 must be Complete/Accepted. Current snapshot package version is `0.11.0`; at execution re-read `package.json` and npm `latest`. If both still equal 0.11.0, target is **0.12.0**. If either differs, STOP for architect version reconciliation; do not choose another version yourself.

## Authorized changes
Only `package.json` and `package-lock.json` version metadata. No `src/**` edits.

## Required export verification
Packed `./billing` declarations/runtime must contain exactly the ARCH-011 names from SHARED-001, including both constants, both schemas, and four functions. Existing ARCH-010 billing exports must remain.

## Publication sequence
```text
npm test                 # do not rerun if architect acceptance evidence already records same commit; otherwise STOP for architect instruction
npm run typecheck        # same rule
npm run build            # same rule
npm pack --dry-run --json
npm view @modainteract/moda-interact-shared@0.12.0 version
npm publish
npm view @modainteract/moda-interact-shared@0.12.0 version dist.tarball dist.shasum
npm view @modainteract/moda-interact-shared dist-tags.latest
```
If target exists before publish, STOP. Publish once only.

## Completion protocol

After all Work Items, Acceptance Criteria and Validation pass: update the Completion Report, set task status to `review`, clear the active claim according to the normal launcher protocol, return control to `moda_architect`, and **STOP**. Do not start an enabled/follow-on task.
