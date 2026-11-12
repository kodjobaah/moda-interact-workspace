---
id: ARCH-073-BACKGROUND-002
architecture_id: ARCH-073
title: Compose tenant shop headers before immutable recovery sends
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-073-BACKGROUND-001
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Compose tenant shop headers before immutable recovery sends

## Architecture

ARCH-073; docs/architecture/ARCH-073-tenant-recovery-shop-headers.md; coordinator moda_architect.

## Objective

Prepare deterministic shop-name and verified-website text headers on eligible recovery messages before immutable send preparation.

## Context

Current main lacks preserved Shopify name acquisition; wrappers cannot render a missing ShopBrand name. User requests generic shop branding, never a hardcoded single-shop patch.

## Scope

Background wrapper/local trusted context/composition, HUMAN dual provenance/frozen replay, eligible notice admission paths and corresponding tests/docs. Prefer existing wrapper contracts; no new Shared variable without returning a concrete gap.

## Out of Scope

Logo/media enablement, read_brand/other permission changes, privileged Brand queries, wholesale historical merge, unrelated token refactor, production DB backfill, schema/new namespace/Shared release, other repositories, live sends or deployment. Return genuine cross-owner gaps.

## Requirements

Header uses exact authorized shop persisted name and verified stored domain, never model text or hardcoded alias. Use verified-domain-only fallback for missing name; do not suppress an otherwise legitimate reply or guess a display name. No logo or extra media sends. Cover eligible AI/HUMAN configured/passthrough and service/limit/audio/oversize notices; approved templates, unbound routing and forbidden sends stay excluded. Preserve configured header content and human-authored bytes; avoid duplicate mandatory header blocks. Compose header and existing divider/checkout footer before freeze/hash/media/moderation/permit, provider body identical. Strict provenance checks both preparation and persisted replay; old frozen bodies byte-identical. Length/caption fallback keeps full safe body or refuses before admission. Preserve tenant/control/inbound/version/lease fences. Document rolling old-reader drain if new evidence cannot old-decode.

### Header contract clarification

Approved text layout is shop name, then verified HTTPS website, then neutral divider and blank line before the existing body/footer. Missing name uses only verified website without guessing or suppressing an otherwise legitimate reply. Safe single-line display names cannot inject controls/markup into identity; retain stored identity without inventing aliases. Validate/canonicalize website from exact authorized stored Shop.domain, never customer/model text. Background-local context/receipt extension is sufficient; no Shared variable enum/release.

Shared presentation brandName currently validates projection identity but does not add a header. Deduplicate only a proven pure-identity configured-wrapper header derived from its typed tokens; never heuristically remove words/URLs from HUMAN authored bytes or body text. Retain custom merchant header prose. Bind optional header identity/receipt digest through fresh application keys, no-wrapper exact transform, HUMAN preparation, persisted evidence and final-permit validation. Evidence-absent old records retain old hashes/bytes. A receipt is not tenant authority; its source is the verified local context. No new logo/media behavior belongs to this task.

## Work Items

- [ ] Implement only the bounded capability and document compatibility/rollout.
- [ ] Add meaningful prior-behavior red and regression/concurrency/security coverage.
- [ ] Complete required validation and mirrored task report/push.

## Interfaces / Contracts

Background-local current authenticated Shopify token and ShopBrand persistence; existing published Shared schemas/logging remain canonical. No new cross-service wire is planned.

## Dependencies

ARCH-073-BACKGROUND-001

## Enables

Developer integration and genuine production verification.

## Acceptance Criteria

- [ ] Required bounded behavior works without hardcoded identity or broader permissions.
- [ ] Tenant/domain, immutable state, authorization and concurrent-update boundaries remain enforced.
- [ ] Existing unrelated media/frozen content is preserved; no secret/private proof committed.
- [ ] Canonical dedicated mirrored worktree/synchronization/recursive submodule evidence recorded.

## Validation

- [ ] Prior behavior red plus AI/HUMAN configured/unconfigured and all eligible notice header coverage; name/domain freshness/tenant mismatch/missing-name fallback.
- [ ] Configured-header preservation/idempotence, human authored exact transform, old frozen replay/tamper and footer coexistence.
- [ ] Real PostgreSQL freeze/moderation/final permit/provider body identity and race refusal; limits/caption fallback and security/template exclusions.
- [ ] Types, task-owned lint, declared build and exact-head full CI; inspect package scripts first.
- [ ] Diff/secret hygiene; synthetic fixtures and mocked providers, no real Meta send or production write.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete, submit review report and STOP. Do not merge/deploy or begin enabled work.

## Implementation Notes

You are not alone. Preserve others' changes. Use prepared canonical packet. Root owns final merges/deployment; architect owns acceptance. Read historical code as evidence, not permission to restore unrelated behavior or stale API assumptions.

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

No broader provider grant is available or needed.

### Unresolved Issues

None currently; report new contract gaps.

### Architectural Concerns

No source expansion beyond explicit scope without architect reconciliation.

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
