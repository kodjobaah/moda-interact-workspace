---
id: ARCH-045-SHARED-002
architecture_id: ARCH-045
title: Publish Shopify WhatsApp consent-update contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 21
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-SHARED-001
enables:
  - ARCH-045-SHOPIFY-001
  - ARCH-045-BACKGROUND-003
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-20
---
# Publish Shopify WhatsApp consent-update contract

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Make the architect-accepted Shopify WhatsApp consent event contract available as a published Shared package version before downstream consumers adopt it.

## Context

Shared publication must be a release gate separated from implementation; Shopify and Background cannot depend on unpublished sibling source.

## Scope

- Verify SHARED-001 is `complete` with Accepted architect review.
- Select/apply approved package version and publication metadata, publish using repository-defined release command.
- Record registry/version availability and exact package version for consumer tasks.

## Out of Scope

- No runtime behaviour, schema redesign, unit-test reruns, TypeScript refactoring or consumer code changes.

## Requirements

- [ ] Only accepted implementation is published.
- [ ] No unexpected source changes apart from approved release metadata.

## Work Items

- [ ] Confirm accepted SHA/version and publication prerequisites.
- [ ] Publish and verify exact registry package/version.
- [ ] Record the distribution evidence.

## Interfaces / Contracts

Publishes `@modainteract/moda-interact-shared` entrypoints from SHARED-001. Consumers use the published version, not a local worktree path.

## Dependencies

- `ARCH-045-SHARED-001`

## Enables

- `ARCH-045-SHOPIFY-001`
- `ARCH-045-BACKGROUND-003`
- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Exact approved version is visible at target package registry.
- [ ] All publication evidence recorded; no implementation change is mixed into publication.

## Validation

- [ ] Check package version, release command exit status, registry visibility and source diff only; do **not** rerun code validation from SHARED-001.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

If an implementation correction becomes necessary, stop publication and refer it to moda_architect.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

Not Started — external portable definition, not materialised.

### Files Changed

None — not implemented.

### Work Completed

None.

### Validation Results

Not run; the supplied snapshot is not the developer's task worktree.

### Deviations

None.

### Assumptions

Use the 2026-10-20 snapshot for orientation; revalidate active code/configuration when the task is materially claimed. ARCH-045's provisional 72-hour consent-wait deadline is the exact v1 task contract unless the developer and architect amend it before implementation.

### Unresolved Issues

None recorded at definition time; report any discovered cross-repository dependency rather than implementing outside ownership.

### Architectural Concerns

None recorded at definition time.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
