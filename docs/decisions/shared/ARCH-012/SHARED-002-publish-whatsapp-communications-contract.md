---
id: ARCH-012-SHARED-002
architecture_id: ARCH-012
title: Publish the accepted ARCH-012 WhatsApp inbound contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: automatic
status: pending
priority: 11
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-012-SHARED-001
- ARCH-011-SHARED-002
enables:
- ARCH-012-MESSAGING-001
- ARCH-012-BACKGROUND-001
created: 2026-09-14
updated: 2026-09-14
---

# ARCH-012-SHARED-002

## Objective
Publish the accepted ARCH-012 `./whatsapp` contract so Messaging and Background consume one immutable package release rather than copying types locally.

## Version sequencing
The current snapshot has Shared source version `0.11.0`, while ARCH-011-SHARED-002 is already defined to own the next publication step. This task therefore deliberately depends on ARCH-011-SHARED-002 to avoid two architecture initiatives racing for the same npm version.

At execution:

1. re-read `package.json` and `npm view @modainteract/moda-interact-shared dist-tags.latest`;
2. if ARCH-011-SHARED-002 completed according to its current definition and both local/current `latest` are `0.12.0`, target exactly `0.13.0`;
3. if that premise is false, STOP for `moda_architect` version reconciliation; do not choose a substitute version independently.

## Authorized changes
Only publication/version metadata:

```text
package.json
package-lock.json
```

No `src/**` edits.

## Required export verification
The packed `./whatsapp` entrypoint must expose the exact accepted SHARED-001 runtime/declaration names and all existing package entrypoints must remain present.

## Publication sequence

```text
npm pack --dry-run --json
npm view @modainteract/moda-interact-shared@0.13.0 version
npm publish
npm view @modainteract/moda-interact-shared@0.13.0 version dist.tarball dist.shasum
npm view @modainteract/moda-interact-shared dist-tags.latest
```

If the target version already exists before publication, STOP.

Do not rerun source validation against a different commit than the architect-accepted SHARED-001 implementation. If the source commit changed after acceptance, STOP for architect review.

## Acceptance Criteria

- [ ] exact accepted SHARED-001 source is published once;
- [ ] `./whatsapp` is present in runtime and declarations;
- [ ] npm `latest` resolves to the published target;
- [ ] no implementation source changed in this task.

## Completion protocol
After publication evidence is recorded: update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

### Status
Not started.

### Published Version
TBD.

### Validation Results
TBD.

## Architect Review

### Review Status
Not reviewed.

### Review Notes
TBD.
