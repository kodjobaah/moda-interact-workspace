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
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-049-DATABASE-001", "ARCH-049-ADMIN-001", "ARCH-047-ADMIN-003", "ARCH-047-ADMIN-005"]
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

### R3. Complete the existing Admin IMAGE-header contract

Inspection of the 26 October snapshot shows that the accepted ARCH-047 Admin compiler currently emits **TEXT** headers only; a READY-media picker alone cannot create a sendable IMAGE template. Extend the **existing** ARCH-047 Admin authoring/compiler modules in the Admin repository (do not create a second compiler) so the editor offers one IMAGE-header role (`LOGO`, `SQUARE_LOGO`, `COVER_IMAGE`), displays the verified image, and stores a semantic role binding without embedding the shop-specific media URL. Persist the frozen runtime binding in `WhatsAppTemplateMetaRegistration.parameterBindingsSnapshot` using this proposed version-one extension:

```json
{"schemaVersion":1,"header":[],"headerMediaRole":"LOGO","body":[],"buttons":[]}
```

TEXT-header projections omit `headerMediaRole`; IMAGE headers must contain `HEADER` with `format: "IMAGE"` in the frozen `componentsSnapshot`. The source AST should contain only the corresponding semantic `shopBrandMediaRole`; full production examples/bindings must be fixed before template submission. The Background-004 adapter consumes exactly this field; Admin and Background must test identical frozen-projection digests and reject mismatches. Once content is saved, preserve ARCH-047 create-new-template immutability.

A sample Meta image-header **upload handle** (the `HEADER.example.header_handle` required by the already-implemented ARCH-047 BG003 adapter) is separate from a merchant's send-time READY logo. Never send a shop's source URL as a sample handle. If the approved-authoring path cannot obtain/provide a valid handle, fail closed with `IMAGE_SAMPLE_HANDLE_REQUIRED` and record the provider sample-acquisition gap for architect resolution; do not claim successful IMAGE template creation or invent a client-side Meta token/upload mechanism. No new R2/Meta upload implementation is authorised by this task.

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
- ARCH-047-ADMIN-005

## Enables

- ARCH-049-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] READY processed brand images, not originals, are selectable and correctly previewed.
- [ ] Pending/failed/stale/absent assets cannot be selected for IMAGE headers.
- [ ] Shop-level tenant isolation and accessible modular React boundaries are maintained.
- [ ] Admin merchant-support SQL continues to work after the ShopBrand schema move.
- [ ] The existing AST/compilation module supports the frozen `headerMediaRole` projection and IMAGE-header preview with matching content fingerprints, without a competing compiler or credential-bearing browser code.
- [ ] Meta IMAGE submission remains disabled without a valid server-produced sample handle; no unverified sample is silently substituted.

## Validation

- [ ] Focused React component/controller tests, accessibility and responsive checks.
- [ ] Authenticated Admin server-read/tenant and READY matching tests.
- [ ] Merchant-support raw SQL security/regression tests.
- [ ] Cross-module Admin compiler tests proving IMAGE role persists into the frozen binding and produces the canonical approved-header projection.
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
