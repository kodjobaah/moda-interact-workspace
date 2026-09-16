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
updated: 2026-09-16
---

# ARCH-012-SHARED-002

## Objective
Publish the accepted ARCH-012 `./whatsapp` contract so Messaging and Background consume one immutable package release rather than copying types locally.

## Version sequencing
The exact ARCH-012 npm version is intentionally unresolved in this compatibility revision. The 2026-09-16 snapshot shows that ARCH-015 has advanced the Shared patch publication line, while `ARCH-011-SHARED-002` is still Pending with an older version premise.

This task remains serialized after `ARCH-011-SHARED-002`. **Do not execute SHARED-002 until `moda_architect` has reconciled ARCH-011 publication and amended this task with one exact target version.**

At execution, the developer must:

1. verify the exact architect-written target in this task;
2. re-read local `package.json` and npm `latest`;
3. verify the source commit is the exact architect-accepted SHARED-001 implementation rebased/integrated on all previously accepted Shared source;
4. STOP if any premise differs.

The executor MUST NOT calculate `latest + 1`, choose patch/minor/major semantics, or substitute another available version.

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
Before this task becomes executable, `moda_architect` must replace `<ARCHITECT_AUTHORIZED_VERSION>` below with one exact version after ARCH-011 publication is accepted. A literal placeholder means **STOP; task is not execution-ready**.

```text
npm pack --dry-run --json
npm view @modainteract/moda-interact-shared@<ARCHITECT_AUTHORIZED_VERSION> version
npm publish
npm view @modainteract/moda-interact-shared@<ARCHITECT_AUTHORIZED_VERSION> version dist.tarball dist.shasum
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
