---
id: ARCH-049-ADMIN-002
architecture_id: ARCH-049
title: Use READY ShopBrand R2 media in ARCH-047 template authoring
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-049-DATABASE-001", "ARCH-049-ADMIN-001", "ARCH-047-ADMIN-003"]
enables: ["ARCH-049-SYSTEM-TEST-001"]
created: 2026-10-25
updated: 2026-10-25
---

# Use READY ShopBrand R2 media in ARCH-047 template authoring

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`. **Portable task definition, not materialised in a developer Git worktree.**

## Objective

Integrate per-role verified ShopBrand media previews into the existing ARCH-047 Admin template editor, without re-implementing image processing, AST compilation or storing original merchant URLs as sendable image headers.

## Context

ARCH-047 Admin-003 already provides the template editor and English AST. ADMIN-001 provides bucket/public-origin configuration. This task adds a self-contained READY media selector and preserves existing merchant-support queries when `ShopBrand` moves to commerce.

## Scope

- Implement presentation-only `ShopBrandMediaRolePicker`, `ShopBrandMediaPreview`, `ShopBrandMediaReadinessMessage` and a dedicated controller/data hook in the existing template-editor component hierarchy.
- Add authenticated Admin server reads for matching shop/role `commerce.ShopBrand.whatsAppMedia` and validate READY generation and configured custom HTTPS origin before display.
- Provide an explicit IMAGE-header role selection `LOGO`, `SQUARE_LOGO`, `COVER_IMAGE` and show genuine processed media previews and safe missing/failed/pending UI.
- Update existing `moda-interact-admin/src/lib/admin/merchant-support.ts` raw SQL paths and related focused tests from `shopify."ShopBrand"` to `commerce."ShopBrand"`, coordinating migration rollout.

## Out of Scope

- New Meta API creation, template rewriting, independent AST compiler, image byte transformation, writing source image URLs, changing ARCH-047 runtime sending or Gateway settings.

## Requirements

### R1. Component boundaries

`ShopBrandMediaRolePicker` owns radio/role choice; `ShopBrandMediaPreview` displays a verified image and format/dimensions, `ShopBrandMediaReadinessMessage` explains MISSING/PENDING/PROCESSING/FAILED. `useShopBrandMediaRole` (or focused existing controller extension) handles requests/selection; page components stay thin. Server service owns authenticated reads and tenant scoping. No single large TSX file, no R2 SDK in React/browser code.

### R2. READY only

Read `ShopBrand.whatsAppMedia.roles[role]`; only present as selectable IMAGE header when `work.status=READY`, `ready.sourceGeneration=source.generation`, `ready.sourceFingerprint=source.fingerprint`, output is JPEG/PNG below 5 MiB and the R2 object key is trusted. Construct a public URL from configured origin and immutable key; do not render/send `logoUrl`/`squareLogoUrl`/`coverImageUrl` as image headers. Distinguish image-header role binding from existing text tokens such as `shopBrand.brandName` or literal logo URL. Never expose R2 credentials in UI or JSON response.

### R3. Template contract handoff

The Admin authoring AST should persist only a semantic image role reference for an image-header template (e.g. `{"header":{"type":"IMAGE","shopBrandMediaRole":"LOGO"}}`), not a shop-specific image URL. Provide exactly that typed binding to the existing ADMIN-003/005 authoring and compilation path; if their prepared-runtime format lacks this field, report a bounded ARCH-047 contract gap to architect instead of implementing a competing compiler. Meta submission sample image is a separate approved authoring input handled in ARCH-047, not each merchant's runtime logo.

### R4. Existing query compatibility

Update all `shopify."ShopBrand"` raw references in `merchant-support.ts` to `commerce."ShopBrand"` with relevant security/tenant tests. Do not deploy a consumer using the new schema before DATABASE-001 migration, or deploy the migration while a required live consumer still uses the old table path; coordinate one compatible rollout window. Prisma client regeneration follows repository conventions.

### R5. Tests

Component/controller tests for all three roles, READY versus stale generation, missing media, tenant isolation and mobile screen responsiveness. Verify screen-reader labels and keyboard selection. No media fetch/conversion is performed by the editor.

## Work Items

- [ ] Add components/hook/server reader without a monolithic editor.
- [ ] Update Admin merchant-support raw SQL schema references/tests.
- [ ] Add preview and tenant/readiness tests with seeded ShopBrand fixtures.
- [ ] Document Admin/Database/ARCH-047 handoff and constraints.

## Interfaces / Contracts

Consumes `commerce.ShopBrand`, accepted `shopBrand.publicMedia`, and the existing ARCH-047 template AST/editor. Produces selected semantic `shopBrandMediaRole` for IMAGE header—not a raw original URL. Does not own R2 processing.

## Dependencies

- ARCH-049-DATABASE-001
- ARCH-049-ADMIN-001
- ARCH-047-ADMIN-003

## Enables

- ARCH-049-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] READY processed brand images, not originals, are selectable and correctly previewed.
- [ ] Pending/failed/stale/absent assets cannot be selected for IMAGE headers.
- [ ] Shop-level tenant isolation and accessible modular React boundaries are maintained.
- [ ] Admin merchant-support SQL continues to work after the ShopBrand schema move.
- [ ] No new AST compiler, media resizing or secret-bearing frontend code.

## Validation

- [ ] Focused React component/controller tests, accessibility and responsive checks.
- [ ] Authenticated Admin server-read/tenant and READY matching tests.
- [ ] Merchant-support raw SQL security/regression tests.
- [ ] Relevant Admin unit tests, lint/typecheck and `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

Separate existing ShopBrand **text** placeholders from actual image-header asset references in the UI: using a logo URL as a text hyperlink is not proof it is sendable media.

## Completion Report

### Status

Not Started — defined but not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the explicit architecture/task contract.

### Unresolved Issues

None; live environment availability is a validation prerequisite and must be reported if missing.

### Architectural Concerns

None reported.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.
