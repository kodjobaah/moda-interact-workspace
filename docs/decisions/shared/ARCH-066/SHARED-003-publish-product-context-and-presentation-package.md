---
id: ARCH-066-SHARED-003
architecture_id: ARCH-066
title: Publish product context and presentation package
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-SHARED-004", "ARCH-066-SHARED-001", "ARCH-066-SHARED-002"]
enables: ["ARCH-066-BACKGROUND-002", "ARCH-066-MCP-001", "ARCH-066-BACKGROUND-001", "ARCH-066-COMMERCE-001"]
created: 2026-11-08
updated: 2026-11-08
---
# Publish product context and presentation package

## Objective and read first
Implement only the owned work below. Read `docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md` first: its numbered contract decisions are normative and must not be redesigned by the implementor.

## Scope
Release metadata/lockfile and immutable npm publication only, from the accepted implementation of SHARED-001 and SHARED-002. Baseline checkouts differ (local Shared metadata 5.4.0, current consumers 5.5.0); do not publish stale local code or overwrite an existing version.

## Exact release rule
Use minor version 5.6.0 if absent from registry; if occupied by identical accepted artifact reuse it, otherwise choose first unused 5.6.N patch in ascending order and record exact version/integrity in architecture release handoff. No floating ^ or latest consumer pin. This is a backwards-compatible addition, not response.v2 or commerce.v2.

## Acceptance / validation
- [ ] Verify accepted source commits, clean npm pack file list, browser-safe presentation export, /commerce and /commerce/runner declarations, old import compatibility and hash of published tarball.
- [ ] Install exact downloadable artifact into an isolated smoke project; import context schemas/reducer, runner and composer from public exports. Record npm dist.integrity and version for all dependent tasks.
- [ ] Do not republish mutable version, add consumer source forks, or change features while publishing. Source validation evidence comes from prerequisites; package/import smoke is mandatory.

## Execution boundary
Definition only. Do not claim or implement until explicit dependency tasks are Complete. Use the canonical launcher-resolved parent and implementation task worktrees; execution_mode and completion_mode are developer. Do not change unrelated work or another repository. Record exact Shared package version/integrity, database migration and provider schema artifact used. No production customer messages, Meta registrations or live mutations are authorized by this task.

## Completion Report
Status: Not started. Attempt: 0. Implementation commit: none. Validation evidence: none. Remaining work: all unchecked acceptance criteria. Document isolated worktree, package, test and deployment evidence when implemented; do not mark Complete merely from source inspection.

Publication must include the SHARED-004 `./commerce/outreach` export and its Zod contracts; smoke-test the installed export before releasing.
