---
id: ARCH-051
title: moda-interact-background test-suite stabilisation
status: in_progress
coordinator: moda_architect
created: 2026-10-26
updated: 2026-10-27
---

# ARCH-051: moda-interact-background test-suite stabilisation

## Status

In Progress. The sole Background task is Ready for Attempt 2 after its ARCH-007 scheduling-failure dependency completed.

## Problem

A full `moda-interact-background` validation run found stale installed Shared
package exports, a unit suite with 17 reported failures among 2,996 passes, and
integration results that changed after dependency installation was corrected.
The current evidence does not establish that all failures are Background code
regressions. Package installation, Shared exports, stale test expectations,
pre-existing failures and intermittent subprocess timeouts must be separated
before source changes are selected.

## Goals

- Establish reproducible, same-revision Background unit and integration results
  using the dependencies declared by the repository.
- Classify each observed failure before modifying Background code or tests.
- Correct confirmed Background-owned defects and keep Shared/workspace dependency
  ownership at the appropriate boundary.
- Complete full Background unit and integration validation after any fixes.

## Non-Goals

- Making changes in moda-interact-shared or workspace-level package-install
  configuration from the Background task.
- Broad test cleanup, weakening assertions, changing production behaviour to
  satisfy an unverified expectation, or expanding the established baseline.
- Running or implementing this remediation as part of task authoring.

## Current Architecture and Evidence

The Background repository declares `@modainteract/moda-interact-shared` 2.5.1.
The initial test run resolved a locally installed 2.4.3 package without the
`./identity` and `./whatsapp-template-events` exports. Replacing that ignored
local package with the declared 2.5.1 artifact and supplying the declared
`libphonenumber-js` 1.12.30 dependency produced a passing full integration run
(5 files, 13 tests). This is evidence of an installation/export-resolution
problem, not by itself a Background source defect.

The subsequent full unit result reported 17 failed and 2,996 passed tests across
291 files. Candidate mismatches include an observability-startup assertion for
Shared 2.5.0 while the Background manifest declares 2.5.1, an automated-template
input expectation that omits null `textHeader`/`imageHeader` properties, and
subprocess-timeout and checkout-recovery failures. These remain candidates until
the assigned task reproduces and classifies them against the exact starting
revision and a controlled dependency set. Existing durable baseline
`ARCH025-BACKGROUND-TEST-001` is historical evidence; it must not be overwritten
or assumed to explain every current failure.

## Proposed Architecture

`ARCH-051-BACKGROUND-001` owns baseline reproduction and Background-only
corrections. Dependency installation and Shared package resolution are
diagnosed first. A wrong local install is corrected in the task environment
without adding Background shims or unrelated manifest changes. If the published
Shared package/export is actually defective, the Background agent stops the
affected correction and returns evidence to `moda_architect`; the architect
creates and coordinates a Shared-owned task and any required publication gate,
then updates the Background task dependency before execution resumes.

Only confirmed Background-owned production/test defects may be corrected in the
Background implementation task. Failure identities and reasons are compared
with the existing baseline; intermittent outcomes require repeatable evidence
and are not dismissed or added to the baseline by assertion.

## Repository Responsibilities

- `moda_background` / `moda-interact-background`: reproduce, classify and
  remediate confirmed Background-owned unit/integration failures.
- `moda_shared` / `moda-interact-shared`: owns any actual missing or incorrect
  Shared export implementation and its release.
- `moda_architect`: owns cross-repository task creation, dependencies,
  publication sequencing and any baseline-document update.
- Workspace dependency installation/configuration remains outside Background
  source ownership unless repository evidence proves a Background-owned
  manifest/lock defect.

## Data Model

None. This initiative changes no durable schema or runtime data contract.

## Interfaces / Contracts

No contract changes are authorised by this architecture. The task consumes the
published `@modainteract/moda-interact-shared` package as declared by Background.
If that package is defective, the Shared-owned contract and published export
remain authoritative; no local duplicate is permitted.

## Failure Handling and Rollout

If a required correction is owned by Shared or workspace infrastructure, stop
the affected work and return the exact evidence to `moda_architect`. Do not
silently change imports, add local export shims, or make an unreviewed dependency
upgrade. This is test-suite remediation; no database migration, service rollout,
or production compatibility change is planned. Any discovered production
behaviour change requires a separately reviewed scope decision.

## Scalability, Security, and Observability

No platform capacity, security boundary, or telemetry architecture changes are
intended. The task must preserve existing behavior and avoid exposing secrets or
customer payloads in test diagnostics.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|------|-------|--------|------------|
| ARCH-051-BACKGROUND-001 | moda_background | Ready | ARCH-007-BACKGROUND-012 (Complete) |

Integrated `moda_system_test` validation is not applicable: this initiative
validates an existing repository test suite and does not add a cross-service
runtime capability.

## Open Questions

Failure ownership and the reproducible baseline remain to be determined by the
task. Any Shared-owned dependency gap is returned to `moda_architect` for a
separate task and dependency update.

## Change History

- 2026-10-27 — Promoted the test-suite stabilisation initiative from the conflicting ARCH-050 identity to ARCH-051; recorded the completed ARCH-007 scheduling repair as a satisfied task dependency. Attempt 1 evidence remains in the task record.

- 2026-10-26: Created from the full Background test-run evidence; no test or
  implementation changes were made during task authoring.