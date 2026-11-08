---
id: ARCH-066-SHARED-010
architecture_id: ARCH-066
title: Publish accepted product-detail selection correction
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-SHARED-005", "ARCH-066-SHARED-009"]
enables: ["ARCH-066-COMMERCE-001"]
created: 2026-11-08
updated: 2026-11-08
---
# Publish accepted product-detail selection correction

## Architecture
ARCH-066; canonical architecture and ARCH-066-consumer-contract.md A–C/E.

## Objective
Publish one immutable accepted Shared correction artifact for Commerce.

## Context
User explicitly authorizes moda_shared to resolve the missing public contract and unblock Commerce. Publication follows architect acceptance of009; never overwrite5.7.0.

## Scope
Release metadata/lockfile and approved package publication only. Preserve accepted009 source exactly; if main has not integrated009, repository owner may carry its exact accepted commit into this isolated publication branch without source edits. No integration into main.

## Out of Scope
Implementation changes, repeated implementation validation, consumer source, deployment or activation.

## Requirements
Prerequisites must be Complete. Inspect registry versions; select5.8.0 if unused and greater than all published5.x versions, otherwise first unused minor above every published5.x minor, patch0. Never republish existing versions. Use existing approved release mechanism. Record exact version/dist.integrity/tarball SHA256/source commit. Download/install artifact in isolation and verify public detail selection/PRODUCT_DETAILS/verifier/facts/outreach imports and legacy option schemas. Consumer pin comes only from this accepted record, not ranges/latest. If release reveals source defect return to architect.

## Work Items
- [ ] Verify accepted source/prerequisites.
- [ ] Apply version and publish immutable artifact.
- [ ] Verify registry metadata and downloaded public artifact.

## Interfaces / Contracts
Published @modainteract/moda-interact-shared /commerce /commerce/presentation and existing outreach entrypoint; accepted009 correction plus005 ancestry.

## Dependencies
ARCH-066-SHARED-005 and ARCH-066-SHARED-009.

## Enables
ARCH-066-COMMERCE-001.

## Acceptance Criteria
- [ ] Exact approved version is downloadable and integrity matches.
- [ ] Public artifact supports corrected model-facing selection and preserved existing exports.
- [ ] No implementation change or consumer activation occurred.

## Validation
- [ ] Prerequisite acceptance/source verification.
- [ ] Publication command and exact registry/download/install public-import smoke.
- [ ] Release-only diff review; no repeated tests/lint/typecheck/build as validation.

## Stop Condition
Push release metadata/report, set review, stop for architect acceptance; do not start consumer.

## Implementation Notes
Existing release lifecycle packaging may build required distributables; do not rerun implementation validation. No main merge/push. Release is explicitly authorized by current user request to resolve Shared blocker.

## Completion Report
### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
Pending
### Deviations
None
### Assumptions
None
### Unresolved Issues
None
### Architectural Concerns
None

## Architect Review
### Review Status
Pending
### Review Notes
Pending
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending
### Follow-up
Consumer pin amendment after accepted artifact.

## Accepted source handoff
009 Complete at accepted Attempt1; implementation16e3b357c982975820cdeafd036bf63a6cefae36. Release must carry this exact accepted source; source edits are prohibited.
