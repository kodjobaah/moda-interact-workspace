---
id: ARCH-075-BACKGROUND-010
architecture_id: ARCH-075
title: Consolidate branded answers with separate product media
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-SHARED-006
  - ARCH-075-BACKGROUND-009
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Consolidate branded answers with separate product media

## Architecture

ARCH075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Deliver a complete branded main answer with one checkout footer, keeping verified product images separate.

## Context

Actual AI common reply emitted empty logo/header/footer then answer/footer, creating adjacent dividers. Existing strict common preparation/frozen guards enforce that old decomposition. Shared005/006 add only HEADER-only order; this consumer must use published package and preserve legacy frozen plans. Root user authorizes correction; BG009 urgent default-human freeze remains independent prerequisite.

## Scope

Background common composition/preparation/frozen exact decomposition and published Shared version pin; directly related default AI/human and PG delivery tests.

## Out of Scope

Shared implementation/publication, saved common source mutation, Meta template AST/provider registration, schema/DB changes, new engine, arbitrary text stripping, live sends or main merge.

## Requirements

- When full authored common body (shop header+answer+checkout footer) fits1024 Unicode code points and verified logo available, emit one HEADER BRAND_IMAGE whose caption is the full body. No extra ANSWER part. If verified product selected, follow with PRODUCT IMAGE with trusted footer-only caption; do not reuse product as logo or silently drop product.
- Without available/valid logo, or full body exceeds1024, use a single complete TEXT main (4096existing bound), retaining shop details, answer and single footer. With product: HEADER TEXT fullbody then PRODUCT footer-only (existing order); without product: existing ANSWER TEXT fullbody. Logo omitted only due availability/caption constraint; never truncate answer, inject literal copy, strip authored divider heuristically or keep empty header+footer message.
- Every physical part retains trusted checkout URL final line. Preserve full logical body/common reference/hash/evidence unchanged; complete authored answer occurs exactly once. New short singleHEADER and HEADER(fullbody)+PRODUCT(footeronly) have exact guard decomposition, not substring/prose heuristics.
- Preserve old frozen valid HEADER+ANSWER/HEADER+PRODUCT/HEADER+PRODUCT+ANSWER decompositions and their bytes/digests across restart/retry. Only newly prepared plans choose consolidated layout. No arbitrary alternate-body acceptance: exact source receipt/canonical body/plan digest/media tenant/provenance constraints remain.
- Preserve dispatch permits, one logical billing charge, moderation, human control/lease/CAS, per-part idempotency/provider ambiguity behavior. Product image unavailable follows existing verified fallback policy; no foreign image or footer.
- Use accepted published Shared006 version (root verifies registry). No sibling source, copied validator or local expanded Sharedschema. Return any actual contract gap before expanding.
- Production rollout compatible: root deploys new consumer then verifies old workers stopped/drained before new HEADER-only preparation/live requests. Existing frozen retries remain valid. Root alone runs genuine new human/AI/product tests and verifies provider delivery.

## Work Items

- [ ] Inspect current source and capture awkward old decomposition regression.
- [ ] Adopt published accepted Shared package and exact new composition/guard decomposition with legacy read preservation.
- [ ] Prove short/long/logo/product boundaries, AI/human and real PG firstfreeze/retry/ordering/idempotency negatives.
- [ ] Publish source/report and return review.

## Interfaces / Contracts

Published Shared RecoveryMultipartDeliveryPlan v1 additive HEADER-only; existing common reference/finalURL/media receipts and Background frozen source guard.

## Dependencies

ARCH-075-SHARED-006 accepted publication and ARCH-075-BACKGROUND-009 accepted/integrated before execution.

## Enables

Root rollout/drain and actual new human/AI/product delivery verification, no automatic follow-on.

## Acceptance Criteria

- [ ] Short verified logo reply is one complete caption; selected product remains separate footer-only.
- [ ] Over1024/noLogo uses complete TEXT main without adjacent empty framing; no answer/product loss or truncation.
- [ ] Old frozen plans remain readable, new exact guards reject tamper/foreign/duplicate content, physical footers and logical billing/idempotency unchanged.
- [ ] Required tests/checks/isolation/publication evidence pass; no live mutation.

## Validation

- [ ] Focused RED/GREEN AI/human defaultcomposition tests:1024/1025Unicode,4096limit,logo present/absent/invalid,product present/absent/unavailable,exact footer/no duplicated middle.
- [ ] Frozen legacy/new shape digest/read vectors plus tamper/media/tenant/control/moderation/lease/dispatch negatives.
- [ ] Disposable PG new root/ordered parts/retry/concurrency/one logical usage/no duplicate provider sends.
- [ ] Relevant declared full tests/build/type/scoped lint and known unchanged baseline disclosure; exact dependency/registry pin,diff/privacy and launcher isolation/synchronization evidence.

## Stop Condition

Set review and publish exact source/report; no self-accept/main merge/live send or further capability.

## Implementation Notes

Normal launcher dedicated mirrored worktrees; you are not alone, preserve others/primary. Root owns merges/drain/live. Never modify approved common source to hide transport issue.

## Completion Report

#

## Status

Not Started

#

## Files Changed

None

#

## Work Completed

None

#

## Validation Results

Not run

#

## Deviations

None

#

## Assumptions

Root controls rollout and publication authorization.

#

## Unresolved Issues

Publication/consumer/live proof separate.

#

## Architectural Concerns

Production old readers reject HEADER-only; root drain gate and legacy frozen read compatibility are mandatory.

## Architect Review

#

## Review Status

Pending

#

## Review Notes

None

#

## Reviewed Files

None

#

## Validation Reviewed

None

#

## Architecture Conformance

Pending

#

## Follow-up

No implicit publication or architecture completion.

