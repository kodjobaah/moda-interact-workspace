---
id: ARCH-049-ADMIN-002
architecture_id: ARCH-049
title: Use READY ShopBrand R2 media in ARCH-047 template authoring
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-049-DATABASE-001", "ARCH-049-ADMIN-001", "ARCH-047-ADMIN-003", "ARCH-047-ADMIN-005"]
enables: ["ARCH-049-SYSTEM-TEST-001"]
created: 2026-10-25
updated: 2026-10-27
---

# Use READY ShopBrand R2 media in ARCH-047 template authoring

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`. This task is materialised on its canonical parent task branch and prepared for developer Attempt 1.

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

- [x] Add components/hook/server reader without a monolithic editor.
- [x] Update Admin merchant-support raw SQL schema references/tests.
- [x] Add preview and tenant/readiness tests with seeded ShopBrand fixtures.
- [x] Document Admin/Database/ARCH-047 handoff and constraints.

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

- [x] READY processed brand images, not originals, are selectable and correctly previewed.
- [x] Pending/failed/stale/absent assets cannot be selected for IMAGE headers.
- [x] Shop-level tenant isolation and accessible modular React boundaries are maintained.
- [x] Admin merchant-support SQL continues to work after the ShopBrand schema move.
- [x] The existing AST/compilation module supports the frozen `headerMediaRole` projection and IMAGE-header preview with matching content fingerprints, without a competing compiler or credential-bearing browser code.
- [x] Meta IMAGE submission remains disabled without a valid server-produced sample handle; no unverified sample is silently substituted.

## Validation

- [x] Focused React component/controller tests, accessibility and responsive checks.
- [x] Authenticated Admin server-read/tenant and READY matching tests.
- [x] Merchant-support raw SQL security/regression tests.
- [x] Cross-module Admin compiler tests proving IMAGE role persists into the frozen binding and produces the canonical approved-header projection.
- [x] Relevant Admin unit tests, lint/typecheck and `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

Separate existing ShopBrand **text** placeholders from actual image-header asset references in the UI: using a logo URL as a text hyperlink is not proof it is sendable media.

## Completion Report

### Status

**Complete — Developer Attempt 1 (2026-10-27).** The developer explicitly invoked `/moda_developer_update ARCH-049-ADMIN-002 complete` after the durable passing Attempt 1 self-review. Implementation is committed and pushed to the Admin task branch. The implementation's separately labelled Attempt 2 patch corrected a TypeScript test narrowing issue within this same developer claim; no new task claim or increment to `attempt` occurred. No separate architect-specific file review is claimed.

### Files Changed

In `moda-interact-admin` (**35 task-owned implementation files**, all verified to match the corrected Attempt 2 patch):

- `package.json`
- `docs/testing/arch049-admin-002-media-authoring-handoff.md`
- `scripts/test-arch049-admin-media-postgres.mjs`
- `src/app/actions/shop-brand-media-preview.ts`
- `src/components/admin/whatsapp-templates/authoring/template-authoring-workspace.tsx`
- `src/components/admin/whatsapp-templates/authoring/template-content-editor.tsx`
- `src/components/admin/whatsapp-templates/authoring/template-read-only-preview.tsx`
- `src/components/admin/whatsapp-templates/authoring/template-review-summary.tsx`
- `src/components/admin/whatsapp-templates/media/shop-brand-media-header-section.tsx`
- `src/components/admin/whatsapp-templates/media/shop-brand-media-preview.tsx`
- `src/components/admin/whatsapp-templates/media/shop-brand-media-readiness-message.tsx`
- `src/components/admin/whatsapp-templates/media/shop-brand-media-role-picker.tsx`
- `src/components/admin/whatsapp-templates/media/use-shop-brand-media-role.ts`
- `src/lib/admin/merchant-support.ts`
- `src/lib/admin/whatsapp-templates/authoring/compiler.ts`
- `src/lib/admin/whatsapp-templates/authoring/preview.ts`
- `src/lib/admin/whatsapp-templates/authoring/service.ts`
- `src/lib/admin/whatsapp-templates/authoring/super-admin.ts`
- `src/lib/admin/whatsapp-templates/authoring/types.ts`
- `src/lib/admin/whatsapp-templates/authoring/validation.ts`
- `src/lib/admin/whatsapp-templates/media/reader.ts`
- `src/lib/admin/whatsapp-templates/media/readiness.ts`
- `src/lib/admin/whatsapp-templates/meta/contracts.ts`
- `src/lib/admin/whatsapp-templates/meta/snapshot.ts`
- `src/lib/admin/whatsapp-templates/publishing/types.ts`
- `src/lib/admin/whatsapp-templates/publishing/validation.ts`
- `tests/fixtures/arch049-admin-media-header-projection.json`
- `tests/integration/arch049-admin-media.postgres.test.ts`
- `tests/security/admin-merchant-support.test.mjs`
- `tests/security/arch049-admin-media-sql.test.mjs`
- `tests/unit/arch049-admin-media-compiler.test.ts`
- `tests/unit/arch049-admin-media-components.test.tsx`
- `tests/unit/arch049-admin-media-projection-vectors.test.ts`
- `tests/unit/arch049-admin-media-reader.test.ts`
- `tests/unit/arch049-admin-media-readiness.test.ts`

The untracked `typescript` shell recording shown in the developer's Git status is **not** an implementation deliverable and is not part of the implementation commit. The parent task-worktree review update changes **only this task definition**, not the implementation submodule gitlink or shared architecture indexes.

### Work Completed

- Added modular `ShopBrandMediaRolePicker`, `ShopBrandMediaPreview`, `ShopBrandMediaReadinessMessage`, `ShopBrandMediaHeaderSection`, and `useShopBrandMediaRole` for the existing ARCH-047 authoring UI; introduced a reference-shop preview without saving the preview shop or merchant source URL in a template.
- Added authenticated, `SUPER_ADMIN`-restricted Admin media reads for an **exact `shopId`**, from the migrated `commerce.ShopBrand.whatsAppMedia`, using the validated `shopBrand.publicMedia` HTTPS origin. Browser projection contains safe readiness statuses and verified JPEG/PNG derivative metadata only, not raw JSON/source URLs/R2 credentials.
- Refused READY selection for missing, pending, processing, failed, stale-generation, mismatched fingerprint, tampered shop/role/digest object keys, malformed dimensions/content metadata, or unsafe origins. Only verified immutable processed derivatives are previewed.
- Extended the **existing** ARCH-047 Meta authoring AST/compiler/preview/translation and immutable registration snapshot to support a semantic `shopBrandMediaRole` (`LOGO`, `SQUARE_LOGO`, `COVER_IMAGE`), an IMAGE `HEADER`, and schema-versioned frozen `headerMediaRole` bindings/content hashes; retained text-header semantics and create-new-template immutability.
- Confirmed the Meta sample IMAGE upload-handle requirement remains **fail-closed** with `IMAGE_SAMPLE_HANDLE_REQUIRED`. No provider handle, raw merchant URL, R2 upload, client-side Meta credentials, or new compiler was invented.
- Updated the three merchant-support SQL ShopBrand joins from `shopify."ShopBrand"` to `commerce."ShopBrand"`; added focused SQL regression/security coverage.
- Added server-reader, readiness, React component/accessible markup, compiler, immutable projection-vector, and disposable PostgreSQL tests, plus a handoff document addressing the Database/Admin rollout, Background-004 binding contract, and outstanding provider sample-handle acquisition boundary.

### Validation Results

Evidence: developer terminal recordings `typescript(20261027-131801)` (after initial database-submodule repair) and `typescript(20261027-133829)` (after correcting the compiler-vector test), plus the uploaded combined task-worktree archive `moda-interact-workspace-ARCH-049-ADMIN-002.zip`.

| Check / command | Result / evidence |
| --- | --- |
| `npm run prisma:generate` / `npm run prisma:validate` | **PASS** after the Database submodule was initialised; Prisma v6.19.3 client generated and schema valid. Earlier missing-submodule failures are superseded by this passing run. |
| `npm run test:arch049-admin-media:unit` | **PASS**, 18 tests (readiness/tenant/role/component/compiler/frozen projection) plus 1 merchant-support SQL security test, **19/19**. Repeated successfully after the TypeScript correction. |
| `npm run test:arch049-admin-media:postgres` | **PASS**, disposable PostgreSQL migration/schema integration, two shop-scoped media rows, cross-shop key rejection, and `commerce."ShopBrand"` query. Runner reports `PASS ARCH-049 ADMIN-002 disposable PostgreSQL`. |
| `npm run test:arch047-admin-authoring:unit` | **PASS**, 28/28 existing authoring regressions. |
| `npm run test:arch047-admin-meta:unit` | **PASS**, 12 Meta unit tests plus 1 UI test, **13/13**. |
| `npx tsc --noEmit` | **PASS** in the later `133829` log; previous `TS2339` in the projection-vector test was corrected by narrowing the compiler family. |
| `npm run build` | **PASS** (Next.js 16.3.3); webpack compilation, TypeScript and page optimisation finish successfully. Non-fatal BullMQ critical-dependency and optional `@valkey/valkey-glide` resolution warnings remain. |
| `npm run lint` | **PASS with 0 errors, 1 warning** in the Database submodule's `eslint.config.mjs` (anonymous default export); not changed by this task. |
| `git diff --check` | No whitespace errors reported in the terminal validation sequence. |
| Review snapshot vs corrected patch | **PASS** in this review-submission preparation: 35/35 task implementation files match the corrected Attempt 2 patch byte-for-byte. |
| Fresh developer-update rerun (27 October) | **PASS**: media/security 19/19, disposable PostgreSQL 1/1, ARCH-047 authoring 28/28, ARCH-047 Meta 13/13, `npx tsc --noEmit`, and `npm run build`; `npm run lint` had 0 errors and the same one Database-submodule warning. `git show --check HEAD` passed. |

The React tests validate native labelled radio controls, disabled non-READY states, alt text and responsive Tailwind breakpoint markup. **Real-browser keyboard/screen-reader interaction and mobile viewport layout were not recorded as manually tested**; the handoff recommends this for final integration review, and static rendering is not misrepresented as a browser smoke test.

### Deviations

No unapproved in-scope behaviour changes identified. The failed early Prisma/typecheck commands preceded the developer's Database-submodule initialisation and test correction; the subsequent successful commands are recorded above. The repository's existing BullMQ and Database ESLint warnings were not fixed or concealed. No new R2/Meta upload producer was implemented, as prohibited by this task.

### Assumptions

- The supplied terminal logs are execution evidence from the canonical Admin implementation worktree; this ZIP contains overlaid source files but not independently verifiable Git remote state or the complete prepared launcher packet.
- The PostgreSQL test uses its separate disposable test database; no live migration, deployment or Meta submission is claimed.
- A semantic IMAGE-header role is not tied to the reference-shop preview image. Background must revalidate the actual destination shop's derivative when it implements its send-time adapter.

### Unresolved Issues

- **Meta provider IMAGE sample handle:** valid IMAGE header creation/submission to Meta remains unavailable until a separately authorised trusted server-produced handle exists. This task deliberately fails closed and records the gap for architect ownership; do not present IMAGE templates as already registered or sendable.
- **Rollout coordination:** deploy `ARCH-049-DATABASE-001` schema migration and this Admin consumer only in a safe coordinated compatibility window. Do not deploy Admin against a missing `commerce."ShopBrand"` or move the table while required old-schema consumers remain live.
- **System integration:** browser responsive/accessibility smoke checks and Background-004 consumption of the frozen projection-vector fixture remain follow-on validation, not falsely claimed completed here.
- **Parent Git publication:** the canonical parent task record was published at `8266a921415b41b3036025ee065dcae62e292822` before this self-review update; this self-review update must be committed and pushed on the same parent task branch.

### Architectural Concerns

The immutable Admin `headerMediaRole` projection must agree exactly with Background-004 at send time, including content-hash/binding checks and absence of merchant original URLs. Refer to `docs/testing/arch049-admin-002-media-authoring-handoff.md` and `tests/fixtures/arch049-admin-media-header-projection.json`. The missing trusted Meta sample-handle producer is an explicit architect-level capability gap, not an excuse to bypass registration requirements in Admin.

### Git / Worktree Evidence

- `execution_mode: developer`; `completion_mode: developer`; logical owner `moda_admin`; claimed at `2026-10-27T12:55:06Z`, attempt **1**. Task dependencies were marked complete in the supplied parent definition at claim time.
- Canonical dedicated parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-049-ADMIN-002`.
- Canonical dedicated Admin implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-049-ADMIN-002`.
- Task branch in both repositories: `task/ARCH-049-ADMIN-002`. Parent source claims canonical synchronisation from parent `origin/main` and Admin task branch creation from Admin `origin/main`; the updated terminal log shows the Admin commands executed in the named dedicated implementation worktree.
- Admin implementation commit: **`75fc8ee`** (abbreviated SHA exactly as reported by `git commit`); subject `feat(arch-049-admin-002)`; **35 files changed**.
- Admin branch publication: `git push -u origin task/ARCH-049-ADMIN-002` **succeeded**, creating `origin/task/ARCH-049-ADMIN-002` as shown in the terminal log.
- The Admin working tree subsequently had only untracked `typescript` (terminal recording); it was not staged in the commit.
- Parent task/report branch before this self-review update: `8266a921415b41b3036025ee065dcae62e292822`, equal to `origin/task/ARCH-049-ADMIN-002`. The parent worktree was clean before this review edit; do not claim this new self-review record is published until its commit/push is verified.

## Architect Review

### Review Status

No separate architect-specific review supplied. Completion records the developer's explicit authority after the durable passing self-review; no architect review notes are implied.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

Coordinate the DATABASE-001 migration and Admin consumer rollout; complete browser accessibility/mobile smoke validation and Background-004 interoperability before end-to-end certification. The Meta sample-handle gap remains subject to architect resolution.

## Developer Self-Review Passed (Attempt 1, 2026-10-27)

- Outcome: **passed**. All task Work Items, Acceptance Criteria and validation checks are complete in the published Admin implementation branch. No known required task criterion is incomplete.
- Source review: the media reader exposes only exact-shop safe projections and accepts READY media only when source generation/fingerprint, content type, size, dimensions, digest, immutable shop/role key and HTTPS origin validate. The existing authoring compiler emits semantic IMAGE role bindings without a merchant URL; frozen projection vectors pin the digest and role identity. Submission remains fail-closed without a trusted Meta sample handle.
- Fresh validation in the canonical Admin implementation worktree: media/compiler/accessibility/security tests **19/19**; disposable PostgreSQL integration **1/1**; ARCH-047 authoring regressions **28/28**; ARCH-047 Meta regressions **13/13**; `npx tsc --noEmit` passed; `npm run build` passed with existing non-fatal BullMQ/optional Valkey warnings; `npm run lint` passed with 0 errors and one unchanged Database-submodule warning; `git show --check HEAD` passed.
- Implementation publication and isolation: canonical Admin worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-049-ADMIN-002`, branch `task/ARCH-049-ADMIN-002`, is at `75fc8ee924f128f1245a0ad78ba70d7ec8cea99f`, equal to `origin/task/ARCH-049-ADMIN-002`. Only the previously disclosed untracked `typescript` terminal recording remains; it is not task deliverable and was not staged. Canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-049-ADMIN-002` is registered on the matching task branch, clean before this edit, at `8266a921415b41b3036025ee065dcae62e292822` equal to its remote task ref.
- All four declared dependencies were verified `complete`. `origin/main` is an ancestor of the Admin implementation task branch. No merge or push to `main` was performed.
- Remaining limitations are disclosed, not misrepresented as passed: live browser keyboard/screen-reader/mobile smoke tests were not performed; the Meta sample-handle producer remains an architect-owned gap; rollout must coordinate with DATABASE-001; Background-004 interoperability remains follow-on integration validation.
- Transition: retain `status: review`, `executor: null`, `claimed_at: null`, and `attempt: 1`. Since `completion_mode: developer`, explicit developer completion is pending. No downstream task was started or promoted.

## Developer Completion Decision (Attempt 1, 2026-10-27)

- Decision: the developer explicitly invoked `/moda_developer_update ARCH-049-ADMIN-002 complete` after the durable passing Attempt 1 self-review.
- Accepted attempt: Attempt 1; `attempt` remains 1. The task is `status: complete`, `executor: null`, and `claimed_at: null`.
- Implementation publication: `moda-interact-admin` task branch `task/ARCH-049-ADMIN-002` remains clean with respect to tracked files and published at `75fc8ee924f128f1245a0ad78ba70d7ec8cea99f`. The disclosed untracked `typescript` terminal recording was not staged or changed.
- Parent publication: this completion record is to be committed and pushed on parent `task/ARCH-049-ADMIN-002`.
- Dependency frontier: `ARCH-049-SYSTEM-TEST-001` remains pending because its other explicit dependencies are incomplete; it remains manual-gated and is not promoted by this completion alone.
- Integration: no task branch was merged to `main`.

## Dependency Frontier Reconciliation

- Promoted from `pending` to `ready` on 2026-10-27 after `ARCH-049-DATABASE-001`, `ARCH-049-ADMIN-001`, `ARCH-047-ADMIN-003`, and `ARCH-047-ADMIN-005` were verified complete.
- At promotion, Attempt remained 0 with no executor or claim timestamp; no implementation attempt or implementation worktree had yet been created.

## Execution Ownership Amendment and Claim

- On 2026-10-27, `/moda_developer_create ARCH-049-ADMIN-002` explicitly took over the ready agent-owned task for developer execution. `assigned_agent: moda_admin` is unchanged; `execution_mode` and `completion_mode` are now `developer`.
- Developer Attempt 1 was claimed at `2026-10-27T12:55:06Z` after verifying all four declared dependencies were complete and synchronizing both canonical task worktrees.
- Parent task branch `task/ARCH-049-ADMIN-002` merged current parent `origin/main`; implementation branch `task/ARCH-049-ADMIN-002` was created from current Admin `origin/main`. Both task worktrees were clean before the claim.
