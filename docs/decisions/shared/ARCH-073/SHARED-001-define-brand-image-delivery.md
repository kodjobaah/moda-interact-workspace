---
id: ARCH-073-SHARED-001
architecture_id: ARCH-073
title: Define additive prepared brand-image conversation delivery contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 15
executor: codex
claimed_at: 2026-11-12T19:11:58Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Define additive prepared brand-image conversation delivery contracts

## Architecture

ARCH-073; docs/architecture/ARCH-073-tenant-recovery-shop-headers.md; coordinator moda_architect.

## Objective

Define additive prepared brand-image conversation delivery contracts.

## Context

User explicitly requests a shop logo where WhatsApp supports it. Existing canonical product-image plans cannot represent a brand image honestly; preserve product identity and the completed text baseline.

## Scope

Pure additive canonical brand-image schema/type/plan/digest and installed public exports under commerce/presentation. Preserve existing ConversationDeliveryPlan TEXT/IMAGE and product-image contracts unchanged. Candidate patch version 5.13.7, verify current package before selecting; if conflict return version gap. No network/runtime orchestration.

## Out of Scope

Other tasks, source main merges/deployment, live sends, hardcoded merchant assets, fake product IDs, extra unsolicited messages, HTML image markup, database schema/new namespace/credential changes. No production permission mutation inside implementation.

## Requirements

Explicit BRAND_IMAGE or equivalent distinct discriminant with genuine brand provenance: exact shop identity, domain/role, current source generation/fingerprint, ready content digest/key/public URL/media facts sufficient for Background freshness validation. Never product IDs. Strict bounded safe HTTPS/auth/port/control and canonical media identity checks; reuse established Shared media/hash primitives. Pure contract does not grant authorization or trust arbitrary URLs. Additive union export may combine legacy product plans with brand variant; do not silently widen old product schema. Full body retained, image caption max1024 Unicode codepoints; invalid/missing media means host-controlled full text fallback, never truncated checkout URL. Public browser-safe exports cannot import Node-only runtime. Background current READY/tenant checks remain mandatory. Keep schema generation/version compatibility and old consumers tests. No new media fetch/transform or separate branding message.

## Work Items

- [x] Implement only the bounded capability and document compatibility/rollout.
- [x] Add meaningful prior-behavior red and regression/concurrency/security coverage.
- [x] Complete required validation and mirrored task report/push.

## Interfaces / Contracts

Published @modainteract/moda-interact-shared/commerce/presentation for reusable media schemas/digests; Background owns live provider access, tenant/domain/READY evidence and lifecycle.

## Dependencies

None

## Enables

Dependent tasks only after architect acceptance.

## Acceptance Criteria

- [x] Required bounded behavior works without hardcoded identity or broader permissions.
- [x] Tenant/domain, immutable state, authorization and concurrent-update boundaries remain enforced.
- [x] Existing unrelated media/frozen content is preserved; no secret/private proof committed.
- [x] Canonical dedicated mirrored worktree/synchronization/recursive submodule evidence recorded.

## Validation

- [x] Contract tests reject fake product provenance, unsafe/tampered/cross-shape data, bounds and overlong captions; legacy schemas/digests unchanged.
- [x] Full package tests/types/build/declarations, immutable packed installed JS/types/public export smoke and exact artifact hashes.
- [x] Diff/secret hygiene and canonical isolated mirrored execution/report evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete, submit review report and STOP. Do not merge/deploy or begin enabled work.

## Implementation Notes

You are not alone. Preserve others' changes. Use prepared canonical packet. Root owns final merges/deployment; architect owns acceptance. Read historical code as evidence, not permission to restore unrelated behavior or stale API assumptions.

## Completion Report

### Status

Ready for Review — ARCH-073-SHARED-001, attempt1, executor codex.

### Files Changed

Shared `src/commerce/presentation/brand-image.ts` and tests; presentation barrel; README; package/package-lock5.13.7; installed-export and browser-isolation validation scripts. Implementation commits b96c946 and bf155d69e3dcb692a0566e725e8b03441a2530bd pushed on task/ARCH-073-SHARED-001. PR https://github.com/kodjobaah/moda-interact-shared/pull/81.

### Work Completed

Added strict `ConversationBrandImageOriginSchema` with SHOP_BRAND identity (shop/domain/role/current generation and sha256-prefixed source fingerprint), `ConversationPreparedBrandImageSchema` with READY derivative media facts, distinct BRAND_IMAGE plan and additive `ConversationMediaDeliveryPlanSchema`/digest. Product identifiers are never invented; legacy TEXT/IMAGE/product schemas and digest implementation are untouched. Reused canonical hash/date/stable-JSON primitives and existing brand R2 namespace. Exact key/public-origin/content/mime consistency, HTTPS/auth/port/control/raw-normalization checks, bounded timestamp/dimensions/bytes and caption validation are enforced.

Pure builder accepts an existing legacy plan plus explicit host-current provenance/origin. It preserves product IMAGE priority; stale/foreign/malformed/missing media or >1024 Unicode-codepoint captions retain the complete original TEXT body, including checkout URL. It never fetches/transforms media, sends an extra message, authorizes an arbitrary URL or claims durable READY state from self-declared fields. Background must supply and revalidate authoritative current tenant/domain/source/READY evidence before freeze/dispatch. API shape was coordinated with Background and architect; existing adapter can expose already-present source/ready facts in its separate task.

### Validation Results

- Owned regressions demonstrate legacy product schema cannot represent branding, while separate brand plan works without fake product identity. Initial focused run exposed an accepted raw-URL normalization edge case; the new contract now checks raw strings directly. Corrected focused legacy/new tests12/12 passed, with additional all-role/digest tests included in final full suite.
- Final `npm run typecheck`, `npm test`:764 total,761 passed,3 skipped,0 failures. Coverage includes role/domain/shop/generation/fingerprint mismatches, unsafe URL/auth/port/control/query/hash, missing/unknown/cross-shape fields, key/content/digest tampering, bounded media/timestamp, all3 existing roles and JPEG/PNG, complete Unicode caption fallback, product priority and legacy hash equivalence.
- `npm run build` ESM+DTS passed. Exact immutable tarball installed via `node scripts/validate-commerce-outreach.mjs /tmp/modainteract-moda-interact-shared-5.13.7.tgz`: JS/schema/helper/type/public-export targets passed. `npm run validate:conversation-product-image-node`: browser bundle/VM and absence of Node/sharp/AWS/host-runtime imports passed without provider I/O. `npm run validate:commerce-entrypoints` passed.
- Diff/secret hygiene and clean implementation tree passed. No customer/private operational proof, credential, source URL or hardcoded merchant asset committed. No network/provider/DB mutation by source contract.

Exact final artifact: `/tmp/modainteract-moda-interact-shared-5.13.7.tgz`,521753 bytes.
SHA256 `7d1e115255e2f431d4ad302121edbd34ed81a87fa5b50c466379bb3900d3a623`.
SHA1 `96aee05484aa47941e99ced02d99856dbc76a2fd`.
Integrity `sha512-h4qRwx18E58kCzTxdtlmtmMuYfCdofEWDh27dBa2z8E8FqdpU6CY6r6adaYfO96mx2QeV8gxQp0LIGoxiVX+JA==`.
No publication performed; candidate awaits accepted source, developer merge and explicit user public-release approval in separate task.

Physical worktree isolation (prepared packet): canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-073-SHARED-001`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-073-SHARED-001`; both task/ARCH-073-SHARED-001. No shared/default checkout switched/mutated or other task worktree reused. Launcher parent and implementation remote-task FF not-needed, origin/main already-current; recursive submodule sync/update passed, entries none. Prepared claim3279dbcdf7cb7283efa21ab34e4f4ae7649ff04f; implementation base11c47feac3a823a586e5f597583c7eb0359b99ca. No duplicate preparation.

### Deviations

None. Timestamp bound was added before final packaging to ensure every new transport field is bounded; legacy date schemas remain unchanged.

### Assumptions

Host-selected normalized stored domain, current generation/fingerprint and READY media evidence remain authoritative. Shape and digest alone do not grant authorization, attest current network safety or prove current READY state.

### Unresolved Issues

No Shared source blocker. Publication, Background rich READY projection/AI/HUMAN freeze/dispatch adoption and genuine production logo/fallback proof are separate tasks. No application behavior/deployment claim is made here.

### Architectural Concerns

Existing Background adapter currently omits rich provenance from its public return; all required values exist in its durable source/ready slots. Narrow adapter projection/freshness validation belongs to Background004, not Shared. No new schema, namespace, permission or infrastructure introduced.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual source review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
