---
id: ARCH-066-SHARED-016
architecture_id: ARCH-066
title: Publish preview-only template renderer
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-SHARED-015"]
enables: ["ARCH-066-COMMERCE-003"]
created: 2026-11-09
updated: 2026-11-09
---
# Publish preview-only template renderer

## Scope and touch points
Release-only package metadata/package lock and existing publication mechanism. Require accepted and explicitly Complete015; preserve exact accepted source and production exports. Select first unused5.x minor version above all published5.x versions, patch0; record registry check/version before publication, never overwrite an artifact. Publish only through existing package mechanism; record source commit, exact version, dist.integrity and downloaded tarball SHA256. Verify public new preview schemas/renderer/types and retained production exports using installed artifact. No consumer edits, new source fixes or live calls. Return a discovered source defect to015; do not repair during release. This task does not depend on sender013/014/Admin001. Acceptance: immutable artifact downloadable, hashes match, exact accepted source preserved beyond release metadata, public import smoke passes. No implementation test reruns as substitute for accepted015 evidence.

## Execution and completion boundary
Definition only. Preserve unrelated work; you are not alone in the codebase. Use canonical launcher task worktrees and mirrored task branches. Record exact source, commands/results and package integrity; submit for review, stop and retain developer completion authority. No main merge/push, deployment, real customer send, Meta call, database mutation in a hosted environment or follow-on task execution is authorized. No acceptance from tests against injected simulation alone.

## Completion Report
Not started. No implementation or validation performed.
