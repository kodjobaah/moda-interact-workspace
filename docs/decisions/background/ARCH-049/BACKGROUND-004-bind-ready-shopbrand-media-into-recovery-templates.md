---
id: ARCH-049-BACKGROUND-004
architecture_id: ARCH-049
title: Bind verified ShopBrand R2 media into prepared recovery templates
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 35
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-049-DATABASE-001
  - ARCH-049-ADMIN-001
  - ARCH-047-BACKGROUND-001
  - ARCH-047-BACKGROUND-006
enables:
  - ARCH-049-SYSTEM-TEST-001
created: 2026-10-26
updated: 2026-10-31
---

# Bind verified ShopBrand R2 media into prepared recovery templates

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator: `moda_architect`. This is a materialised task in the canonical parent task worktree. It closes an identified integration gap in the completed ARCH-047 runtime without reopening its accepted core tasks.

## Execution Ownership Amendment

On 2026-10-27, `/moda_developer_create ARCH-049-BACKGROUND-004` was invoked
as an explicit developer takeover. Execution and completion authority are now
`developer`; logical ownership remains `assigned_agent: moda_background` and
`repository: moda-interact-background`.

## Objective

Implement the one read-only production adapter from `commerce.ShopBrand.whatsAppMedia` to the existing ARCH-047 `RecoveryTemplatePreparer` READY-image resolver and frozen IMAGE-header binding, without any per-send media downloads or new media tables.

## Context

The 26 October snapshot's ARCH-047 `RecoveryTemplatePreparer` injects `noReadyMedia`, `approvedMediaHosts=[]`, and `imageHeader()` calls a generic `headerImage` role. It cannot resolve the fixed ShopBrand roles `LOGO`, `SQUARE_LOGO`, `COVER_IMAGE`. The Admin compiler currently supports TEXT headers only; `ARCH-049-ADMIN-002` owns the matching authoring/compilation extension, and both tasks use the explicit JSON binding contract below.

The adapter needs the existing schema and Admin public-origin configuration, but not the implementation of BG001 image processing or BG002 processing queues. Use seeded READY role metadata in this task's focused tests; integrated source-to-READY tests remain in SYSTEM-TEST-001. No extra formal BG001/BG002 dependency is justified.

## Scope

- Add a focused `src/services/shop-brand-media-runtime/` repository/reader, READY validator, role-to-URL resolver and injectable adapter. Read by authenticated `shopId` only; use the approved `shopBrand.publicMedia` origin, never a browser-supplied host.
- Update the existing `recovery-template-preparation/recovery-template-brand.ts`, `recovery-template-bindings.ts`, `recovery-template.types.ts`, repository and composition call sites only as necessary to support the three canonical image roles and inject the production READY resolver. Do not duplicate the accepted ARCH-047 selector or author an alternate AST compiler.
- Use existing caller/final-send path from ARCH-047 BG006. The prepared IMAGE `header` must pass unchanged through the existing admission/delivery mechanism; no new bypass or second send path.
- Add focused fixtures and integration checks for all roles, stale media, cross-tenant lookups and absent public-origin configuration.

## Out of Scope

Original-image downloading, resizing, Cloudflare uploads, Shopify/Woo sources, Meta template creation or sample-media upload, pricing/offer resolution, database schema changes, editing already-saved template definitions, merchant-initiated post-window integration (ARCH-047 BG007), changes to any Shared package, and `docs/decisions/**/_index.md`.

## Requirements

### R1. Canonical frozen IMAGE-header binding

Consume the Admin-owned prepared, persisted `WhatsAppTemplateMetaRegistration.parameterBindingsSnapshot` contract:

```json
{"schemaVersion":1,"header":[],"headerMediaRole":"LOGO","body":[],"buttons":[]}
```

`headerMediaRole` is permitted **only** when the corresponding frozen Meta component has `type:"HEADER",format:"IMAGE"`, and its value must be one of `LOGO`, `SQUARE_LOGO`, `COVER_IMAGE`. A TEXT header must not contain this key. Preserve the existing BODY and button binding behaviour. The accepted ARCH-047 content fingerprint must include this new field **consistently with the Admin compiler's frozen projection**; do not recompute a new digest silently or use a different AST interpreter. Missing, unknown, duplicated or mismatched role bindings fail closed, including legacy `headerImage` without a specific media role.

### R2. Tenant-scoped READY media resolution

Read only `ShopBrand` for the authenticated shop, `whatsAppMedia.roles[headerMediaRole]` and the accepted public origin. Return an `R2_DERIVATIVE` URL only when the role is READY, has a current non-null source, the ready generation and fingerprint match its current source, and `objectKey` is exactly `shop-brands/<normalized-current-raw-Shop.domain>/<role-lowercase>/sha256-<contentSha256>.<jpg|png>`. An absolute URL contributes only its parsed hostname; safe bare values, including one-label values, remain readable. Background and Admin use the same path-safe ASCII segment validation, and raw `Shop.domain` remains the claim identity for completion-time rename detection. Verified output must be `image/jpeg` or `image/png` with positive bounded dimensions and size below 5 MiB, and the final HTTPS URL must be beneath the configured media origin. Shop-id and old base64url READY records are stale; an existing readable raw-domain key is canonical. No untrusted `logoUrl`/`squareLogoUrl`/`coverImageUrl`, cross-shop reference, R2 credentials or arbitrary external host may be returned. Source URLs in text bindings must remain distinct from IMAGE-header media parameters; where a text binding intentionally requests a processed image URL, map it to the corresponding validated READY role only.

### R3. Runtime integration

Replace the production `noReadyMedia`/empty-allowlist default injection with a configured trusted adapter. Keep constructor injection for isolated tests. The existing `RecoveryTemplatePreparer` must produce one prepared IMAGE header when a matching READY role exists and a typed `MEDIA_NOT_READY`/`BINDINGS_INVALID` result otherwise. Do not issue a network call to fetch, inspect, resize or HEAD the image at send time. Ensure the prepared template flows through the established consent, STOP, moderation, provider eligibility, credit and late admission checks without dropping/duplicating the header or bypassing the final send permit. The ARCH-047 BG007 merchant dispatcher can consume the same adapter after its independent implementation is accepted; this task does not implement that dispatcher.

### R4. Logging and error behaviour

Use `@modainteract/moda-interact-shared/logging` as already installed. Emit bounded shop/role/reason identifiers; never log a full customer URL, source URL, Meta token or R2 credential. Expected absent/stale media is a typed non-send outcome; unexpected database/configuration errors propagate to the owning retry boundary rather than silently succeeding.

## Work Items

- [x] Implement one shop-scoped READY-media adapter in its own focused module and tests.
- [x] Update the existing ARCH-047 image-header variable binding to require the frozen three-role selection.
- [x] Wire the adapter into production recovery preparation and preserve existing final-send admission.
- [x] Verify text-only templates, bad roles, stale media, multiple shops and immutable fingerprint compatibility.
- [x] Record changed paths, validation and worktree evidence in Completion Report.

## Interfaces / Contracts

Input: `(shopId, role)` and saved `whatsAppMedia` JSONB plus the `shopBrand.publicMedia` configuration. Output: the existing ARCH-047 `ReadyBrandMedia` / `BrandMediaResolver` boundary, adapting its role vocabulary as necessary without introducing a new cross-repository queue or schema. Consumes the **Admin-002 version-one `headerMediaRole` prepared-binding contract**; the compiler and preparer must share explicit cross-repository test vectors even though the AST remains Admin-private. No new database model.

## Dependencies

- `ARCH-049-DATABASE-001` — new `ShopBrand.whatsAppMedia` field and `commerce` schema mapping.
- `ARCH-049-ADMIN-001` — accepted public-media configuration.
- `ARCH-047-BACKGROUND-001` — accepted preparer and media resolver interface.
- `ARCH-047-BACKGROUND-006` — accepted automated recovery send/admission integration.

`ARCH-049-BACKGROUND-001`/`002` are **not** formal dependencies: this task is testable against seeded READY JSON; the terminal system test depends on both pipelines. `ARCH-049-ADMIN-002` is also independently implementable against the documented frozen-binding fixtures; integration verifies interoperability before certification. No ARCH-047 BG007 dependency is needed for automated recovery image headers.

## Enables

- ARCH-049-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Only the configured shop's current READY immutable derivative can become a Meta image header.
- [x] A TEXT-header message remains unchanged; a missing/unsafe image fails closed without using original source URL.
- [x] Admin's accepted frozen binding for each of LOGO/SQUARE_LOGO/COVER_IMAGE produces the exact corresponding runtime image header; content hashes remain compatible.
- [x] The existing late outbound admission receives the unchanged prepared media component without bypassing existing safeguards.
- [x] No R2 upload/fetch, Meta sample submission, schema migration or new generic logger is introduced.

## Validation

- [x] Unit tests covering all three roles, absent/stale generation, cross-tenant asset, unsafe host, invalid key and output MIME/size.
- [x] Fixed Admin projection/fingerprint compatibility vectors (including rejection of mismatch).
- [x] Production composition tests proving READY adapter injection and IMAGE component delivery; automated initial + scheduled follow-up and text-only regression.
- [x] Existing Background typecheck, lint, focused tests and `git diff --check`.

## Stop Condition

On completing all Work Items, Acceptance Criteria and required validation, mark the task `review`, record complete validation and dedicated worktree evidence, return control to `moda_architect`, and STOP. Do not implement enabled tasks or edit `_index.md`.

## Implementation Notes

Read relevant ARCH-047 BG001/BG006 accepted tasks and ARCH-049 DB001/ADMIN002 contracts. Keep adapter/repository/validation/composition files bounded; no catch-all service. Use canonical task launcher-isolated parent/implementation worktrees and documented start synchronisation. No Git merges or push to main; developer performs integration. If an actual sample-media provision/acquisition gap blocks Meta IMAGE approval, report it to the architect instead of inventing a server-side upload mechanism inside this resolver.

## Completion Report

### Status

In Review — Attempt 1 implementation and developer self-review passed; explicit developer completion is pending.

### Developer Takeover and Worktree Evidence

- Parent task worktree:
  `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-049-BACKGROUND-004`
  on `task/ARCH-049-BACKGROUND-004`. It was synchronized with `origin/main`
  before this review; the parent branch is clean and its task branch contains
  current mainline.
- Implementation worktree:
  `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-049-BACKGROUND-004`
  on `task/ARCH-049-BACKGROUND-004`. Commit
  `3d59eabf0d10cc3a6266dcd7f334eac275459293` is pushed to
  `origin/task/ARCH-049-BACKGROUND-004`; the worktree is clean and local HEAD
  matches the remote task branch.
- The implementation task branch merged current `origin/main` into the task
  branch. The conflict in
  `src/services/recovery-template-preparation/recovery-template-preparer.service.ts`
  was resolved while retaining mainline category/language inputs and the
  configured READY-media adapter. No merge to `main` was performed.
- The initial typecheck used stale installed Shared `2.5.1` although the
  manifest pins `2.8.1`. `npm ci` restored the lockfile version; no package
  manifest or lockfile change resulted. No schema or Shared source was changed.
- Attempt 1 remains the only attempt. `moda_background` provided implementation
  assistance at the developer's explicit request; execution/completion ownership
  remains developer. The concurrent WooCommerce task file was not edited.

### Files Changed

The implementation branch changes:

- `docs/arch049-ready-media-binding.md`
- `src/services/recovery-template-preparation/recovery-template-bindings.ts`
- `src/services/recovery-template-preparation/recovery-template-brand.ts`
- `src/services/recovery-template-preparation/recovery-template-preparer.service.ts`
- `src/services/recovery-template-preparation/recovery-template.types.ts`
- `src/services/shop-brand-media-runtime/contracts.ts`
- `src/services/shop-brand-media-runtime/repository.ts`
- `src/services/shop-brand-media-runtime/resolver.ts`
- `tests/fixtures/arch049-admin-media-header-projection.json`
- `tests/integration/arch049-ready-media.integration.test.ts`
- `tests/unit/services/recovery-template-preparation/arch049-frozen-image-binding.test.ts`
- `tests/unit/services/recovery-template-preparation/recovery-template-preparer.test.ts`
- `tests/unit/services/shop-brand-media-runtime/production-composition.test.ts`
- `tests/unit/services/shop-brand-media-runtime/resolver.test.ts`

### Work Completed

Implemented a shop-scoped READY-media adapter that reads `ShopBrand` by the
authenticated `shopId`, obtains the current raw Shop domain and trusted
`shopBrand.publicMedia` origin, and returns only a validated immutable R2
derivative. It checks READY state, current source generation/fingerprint,
canonical domain/role/content-hash object key, output MIME, dimensions, size and
origin. It performs no image network access or upload.

Frozen bindings support only the canonical `LOGO`, `SQUARE_LOGO` and
`COVER_IMAGE` roles on IMAGE headers, verify the Admin-compatible frozen
projection fingerprint, preserve BODY/button behavior and reject legacy or
mismatched image bindings. Production preparation injects an operation-scoped
trusted adapter; existing text-only preparation and outbound delivery/admission
remain in place. Text bindings requesting a brand image URL resolve only the
corresponding validated READY derivative.

### Validation Results

Passed:

- `npm ci` restored the lockfile-pinned Shared `2.8.1` dependency; no package
  manifest or lockfile changes were made.
- `npm run build` — Prisma client generation and TypeScript compilation passed.
- `npm run lint` — passed.
- Focused Vitest suite covering recovery-template preparation, frozen bindings,
  runtime resolver/composition, registration and send paths — 10 files, 75
  tests passed.
- `node scripts/test-integration.mjs tests/integration/arch049-ready-media.integration.test.ts`
  — 1 PostgreSQL integration test passed.
- `git diff --check origin/main...HEAD` in the implementation worktree — passed.
- Implementation task branch is pushed and clean; local HEAD matches the task
  remote.

`npm ci` reported 40 dependency audit findings (27 moderate, 13 high); dependency
remediation was not part of this task and no audit-fix command was run.

### Deviations

The assigned `moda_background` agent resolved the implementation-branch
mainline merge conflict and completed the implementation as explicitly
authorized bounded assistance during developer Attempt 1. No ownership,
attempt-count or task-scope change was made.

### Assumptions

None beyond the explicit architecture/task contract.

### Unresolved Issues

Meta sample-media procurement is an external integration prerequisite for real IMAGE template approval; not part of this runtime adapter.

### Architectural Concerns

No additional concerns identified. Meta sample-media procurement remains an
external prerequisite for real IMAGE template approval. The dependency audit
findings reported by `npm ci` should be handled through the repository's normal
dependency-security workflow, separately from this task.

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

## Dependency Frontier Reconciliation

- Historical note: promoted from `pending` to `ready` on 2026-10-27 after `ARCH-049-DATABASE-001`, `ARCH-049-ADMIN-001`, `ARCH-047-ADMIN-003`, `ARCH-047-ADMIN-005`, and `ARCH-047-BACKGROUND-001` were verified complete. At that time, attempt was 0 and no implementation worktree existed.
- Attempt 1 is now in `review`; execution and completion authority remain
  `developer`, with `executor` and `claimed_at` cleared for the review state.
  Attempt count remains 1. The declared dependencies remain complete; no
  downstream task was started or promoted as part of this review.

## Developer Self-Review

### Decision

Passed. The implementation satisfies the task scope and acceptance criteria;
status is `review` because `completion_mode` is `developer`. Explicit developer
completion remains pending and is not inferred from this review.

### Review Findings

- READY media resolution is tenant-scoped and validates the current source
  generation/fingerprint, canonical object key, trusted origin and verified
  image metadata before returning a URL.
- Frozen role selection is enforced for IMAGE headers and included in the
  Admin-compatible fingerprint projection. TEXT headers, BODY/button bindings
  and existing outbound admission/delivery behavior are covered by regression
  tests.
- No BG004-specific blocker or scope deviation was found. R2 fetch/upload,
  schema changes, Shared source changes and `_index.md` edits were not introduced.

### Validation Reviewed

- Build, lint, 75 focused unit tests, 1 PostgreSQL integration test and
  implementation diff check passed after restoring dependencies with `npm ci`.
- The dependency audit findings from `npm ci` are recorded above; they were not
  remediated in this task.

### Implementation Publication

`3d59eabf0d10cc3a6266dcd7f334eac275459293` is published on
`origin/task/ARCH-049-BACKGROUND-004`. The implementation worktree is clean.
The active developer claim was preserved through Attempt 1 and no branch was
merged to `main`.

### Explicit Completion

Pending developer decision via `/moda_developer_update ARCH-049-BACKGROUND-004 complete`.
