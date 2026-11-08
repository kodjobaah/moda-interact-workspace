---
id: ARCH-066-SHARED-005
architecture_id: ARCH-066
title: Publish the accepted initial outreach contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 50
executor: developer
claimed_at: 2026-11-08T17:59:28Z
attempt: 1
depends_on: ["ARCH-066-SHARED-004", "ARCH-066-SHARED-006"]
enables: ["ARCH-066-MCP-001", "ARCH-066-BACKGROUND-001", "ARCH-066-COMMERCE-001", "ARCH-066-BACKGROUND-002", "ARCH-066-COMMERCE-002"]
created: 2026-11-08
updated: 2026-11-08
---
# Publish the accepted initial outreach contract

## Exact scope
Release package metadata/lockfile and immutable npm artifact from accepted SHARED-004 and SHARED-006 source plus accepted5.6.0 ancestry. Do not amend completed SHARED-003 or overwrite5.6.0. Own Shared repository only. Check registry and all existing5.x releases before choosing version: select5.7.0 if unused and greater than current accepted version; otherwise first unused minor greater than every published5.x minor, patch0. Record chosen exact version as the authoritative outreach pin in this task and architecture before consumer launch; consumers use this recorded pin/integrity, never guess/latest/ranges. No feature implementation during publication.

## Acceptance
- [ ] Accepted004 commit and original001/002 ancestry; clean pack list includes JS/declarations for commerce/outreach plus all prior public exports.
- [ ] Build, validate:commerce-outreach and existing entrypoint/presentation checks pass; install downloaded immutable tarball in isolated project and import four schemas, evaluator, preview alias and renderer.
- [ ] Confirm schema rejection and deterministic fixture evaluate/render from installed package; no private service imports. Existing browser presentation export still works without server globals.
- [ ] Record npm version/dist.integrity, tarball SHA256, source commit, commands and installed-artifact smoke evidence. Publication acceptance requires downloadable artifact verification; do not repeat publish during propagation delay.

## Completion
Ready, Attempt0/unclaimed. No automatic publication or execution authorized by this definition. BACKGROUND-002 and COMMERCE-002 depend explicitly on this gate. No consumer rollout or real messages.

Additional gate: pack/install smoke must include generic description/attribute schemas and verifyCommerceProductFacts/PRODUCT_DETAILS together with outreach. Original5.6.0 public imports/goldens remain compatible. Every pending MCP/Background/Commerce task pins this one recorded artifact after publication.

## Dependency readiness — 2026-11-08

SHARED-004 is explicitly Complete at accepted Attempt 2 (passing review `30278f91b64177eb5070034fe1b2eb7e25c15bca`, accepted source `987a05dd06e79aa465d11fce8a4d4fe8b8d52703`). SHARED-006 is Complete at accepted Attempt 1, source `2bc7f02c16840a41154f2135a26f9ba52c71fad7`, contained in the accepted outreach source. Both explicit dependencies are satisfied. Ready, unclaimed at Attempt 0; no release/version selection or package publication is performed by readiness reconciliation.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-11-08T17:59:28Z. Attempt 0 review history is preserved below.

## Release selection — Attempt 1

Selected exact version: `@modainteract/moda-interact-shared@5.7.0`. Registry inspection on 2026-11-08 listed existing 5.x versions 5.0.0, 5.1.0, 5.2.0, 5.3.0, 5.4.0, 5.5.0 and 5.6.0, with latest 5.6.0; 5.7.0 is unused and greater than the accepted baseline. npm publishing identity is available. This is the selected outreach pin; publication/download verification and integrity recording are still in progress, and consumers remain gated.

Accepted source ancestry verified: outreach/fence/group correction `987a05dd06e79aa465d11fce8a4d4fe8b8d52703`, generic facts `2bc7f02c16840a41154f2135a26f9ba52c71fad7`, original001 `c3f9f07cfcf9ff60817f89d5c3d2aaca2dddfbf7`, original002 `7255db58ee1231e209c75c1466255787426d2e5a`, and 5.6.0 release `14c8412cddb2042878b91a17a0043586254aebd6`. Release baseline `8d79ccfbe4b8e06bb2addc62dd092078908198c6` has no src/ differences from accepted outreach source. No feature implementation is part of this task.
