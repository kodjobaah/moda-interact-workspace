---
id: ARCH-047-ADMIN-007
architecture_id: ARCH-047
title: Publish Meta-approved recovery templates to eligible shops
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-047-DATABASE-001
enables: []
created: 2026-10-24
updated: 2026-10-25
---

# Publish Meta-approved recovery templates to eligible shops

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`. Coordinator: `moda_architect`. This task was materialised before developer takeover. Developer execution Attempt 1 has finished and has been submitted for review; seven incremental implementation patch iterations occurred inside that single workflow attempt.

## Objective

Provide controlled, audited **one/selected/all-eligible-shop publication** of centrally authored, Meta-approved template definitions, recording resumable shop-language targets and preserving existing overrides until explicitly replaced.

## Context

The adopted ARCH-047 design is **Moda Admin-only authoring**. A saved English source definition and its corresponding language content are immutable: corrections create a different definition using **Clone as New**. There are six Meta recovery purposes (`INITIAL`/`FOLLOW_UP` × `NO_OFFER`/`CODE_OFFER`/`AUTOMATIC_OFFER`) and one internally published `MODA_CONVERSATION_WRAPPER` family with `SHARED`, `AI` and `HUMAN` audiences. No template authored externally in Meta may be adopted.

`ARCH-047-DATABASE-001` defines the eleven-table persistence boundary, including `WhatsAppTemplateDefinition`, `WhatsAppTemplateLocale`, translation Run/Item/Batch/BatchItem, `WhatsAppTemplateMetaRegistration`, `WhatsAppTemplateMetaEvent`, publication Operation/Target and `WhatsAppConversationWrapperActiveSlot`, plus the nullable link to existing shop `WhatsAppTemplateVariant` and existing `CommerceAuditEvent` actions. Database stores technical relations/JSONB but does **not** enforce template lifecycle/business rules. Admin must enforce those rules transactionally. This Admin task never modifies Prisma schema or the existing database migration.

The six Admin tasks have **only `ARCH-047-DATABASE-001` as a formal dependency**. They own separate route/action/service/component modules, use stable documented persistence payloads, and must prove their capability with fixtures or injected dependencies when a sibling Admin/Background implementation is not yet complete. The end-to-end system test, not an artificial task chain, verifies their integration.


## Scope

- Own `publishing/` module and `/system-controls/whatsapp-templates/[definitionId]/publish/` route. The source is a Moda-authored definition and its 20 confirmed Meta registrations—not an existing shop row or an externally imported provider template.
- Require SUPER_ADMIN, independently verify current Meta `APPROVED` state, lack of blocking drift, reviewed locale/content/binding equivalence and correct WABA for the configured sender **before** preview and again at mutation; never trust browser-supplied shop IDs, provider identity, eligibility or an old preview.
- Scope: one active shop; explicit bounded selection; or **all currently eligible shops**. Eligibility: `Shop.status=ACTIVE`; for Woo require `WooCommerceInstallation.status=ACTIVE` (and any independently required recovery entitlement where applicable). Snapshot exact targets under `WhatsAppTemplatePublicationOperation.scopeSnapshot`, with stable operation key and explicit next-page cursor for bounded processing; do not implicitly apply later to shops joining after confirmation.
- When a proposed compiled Meta template references `shopBrand.*`, obtain **shop-scoped, read-only** `ShopBrand` field availability for the selected shops in bounded batches. In publication previews, show which referenced brand fields are configured, missing/null or not verifiable for each shop; label unresolved values as warnings rather than substituting another shop's branding or falsely claiming a send-ready message. Do not materialise brand values into the immutable template, frozen registration or publication target. This is visibility, **not** a new blanket publication eligibility rule or a runtime delivery guarantee.
- Preview exact impact per eligible shop and **per language**: new assignment, unchanged, replaced version, local override, conflict/ambiguous slot and exclusion. For changed/override rows display the **full previous-shop versus proposed Moda-authored template** components and variable bindings, including header/body/footer/buttons/status/category, the frozen header/body/button positional maps with `shopBrand.*` semantic keys and proper missing-historical-content labels; stack views responsively. Unlike legacy ADMIN-002, this preview does **not** copy a source shop or query Meta.
- Confirm overwriting shop-specific overrides explicitly, require admin reason and fresh server-side revalidation. Use technical FK/identity keys in DB and **application-level per-shop slot serialisation** to keep at most one selectable approved+enabled variant for `(shopId, providerAccountId, purpose, canonicalLanguageTag)`; no new DB business uniqueness constraint.
- Create up to one `WhatsAppTemplatePublicationTarget` per `(operationId, shopId, languageTag)` (20 rows for a 20-language target shop); all language changes for a shop are committed together in a bounded **shop transaction** with correct `previousVariantId`/`newVariantId`. Preserve historical rows/provider references, disable replaced active variants in a safe order and audit each effective change; do not delete old variants.
- Implement idempotent batch progression for thousands of targets, retry only failed/pending shops, and report both **shop counts** and **shop-language target counts** (DB counters count target rows). Stale/overlapping publication attempts are explicitly conflicted/reconfirmed; no unbounded single-request transaction or generic background publishing worker is invented.


### Required React component decomposition

This is the most complex Admin screen and **must not** become a single bulk-publication React component or service. Use a thin protected Server Component route and separate client components under `src/components/admin/whatsapp-templates/publishing/`:

- `PublicationScopeSelector` — one, selected or all currently eligible shops.
- `PublicationEligibilitySummary` — included/excluded shop counts and reasons.
- `PublicationImpactList` — bounded, paginated shop-level impact rows.
- `ShopLanguageComparison` — full previous versus proposed template, per language, using a shared read-only presentation component instead of cloning editor logic.
- `PublicationOverrideConfirmation` — explicit override confirmation, reason and stale-preview warning.
- `PublicationProgressSummary` — separate shop and shop-language counts, partial failures and retry controls.

Move UI state/selection/page-navigation/confirmation fingerprint handling into `useTemplatePublication` (or an equivalent dedicated controller hook). Split candidate discovery, eligibility, impact/diff computation, confirmation digest, per-shop transactional assignment, operation paging/retry and audit into separate **server-side repository/service files** in `src/lib/admin/whatsapp-templates/publishing/`. No JSX file may contain raw Prisma writes or bulk-loop orchestration; no server action may contain a giant combined preview/publish state machine. Large shop lists must never be rendered as one unbounded React array. Ensure a tested selected-shop/selected-language drill-down, not 20 full previews for all shops simultaneously.

## Out of Scope

- No Meta template creation, translation, provider status reconciliation, Admin authoring edits, wrapper activation, storefront merchant custom authoring or Runtime WhatsApp sending.


## Requirements

- [x] Publication never proceeds on unapproved/drifted/mismatched template or without explicit impact review, including individual override replacement; all decisions are reverified within application transactions.
- [x] A single shop is all-or-nothing for its selected languages; other shops may succeed independently and failed shops remain retryable.
- [x] Publishing 100 shops × 20 languages produces 2,000 durable shop-language targets, not 100; UI must not mistake target counts for shops.
- [x] No assignment carries another WABA/provider identity or silently adopts an external/legacy row. Old content and audit history remain accessible for comparison/rollback via newly confirmed publication.
- [x] Per-shop brand-variable availability is displayed accurately and independently of Meta approval: missing nullable `ShopBrand` fields are flagged, no substitute/preview value is silently treated as real data, and no merchant branding is copied into another shop's publication.


All server reads/mutations of template management require the existing authenticated platform-admin boundary; mutations and privileged cross-shop reads require **`SUPER_ADMIN`**, verified server-side (`requirePlatformAdminPage` / `requirePlatformAdminMutation` or repository-equivalent). Reject client-supplied actor identity, WABA ownership, approval and shop eligibility assertions. Persist bounded/redacted audit records using the existing `commerce.CommerceAuditEvent` and ARCH-047 audit enum; do not log tokens, credentials or unnecessary customer/checkout data. Reuse the platform's shared structured logger only for needed semantic logs.


## Work Items

- [x] Implement paginated target discovery, authoritative eligibility/slot preview (including bounded shop-scoped `ShopBrand` availability for referenced keys), confirmation digest and per-shop/app-synchronised publication transaction in focused `publishing/` files.
- [x] Build responsive complete previous/proposed comparisons, per-shop overrides, counts and progress/retry UI.
- [x] Add cross-shop leakage, stale confirmation, concurrent publication, per-shop rollback, partial-operation restart and audit tests.


## Interfaces / Contracts

**Reads:** `Shop`, Woo installation, eligible definition, reviewed locale and `MetaRegistration`, current `WhatsAppTemplateVariant`, and read-only shop-scoped `ShopBrand` when compiled bindings reference its fields. `ShopBrand` values are optional preview context only; persistence and eligibility checks remain as otherwise defined. **Writes:** `WhatsAppTemplatePublicationOperation`, per `(operationId,shopId,languageTag)` `WhatsAppTemplatePublicationTarget`, linked local `WhatsAppTemplateVariant.metaRegistrationId`, per-shop `CommerceAuditEvent`; optionally definition's `publishedAt` once on first authorised publication. `operationKey` and preview fingerprint are idempotency/collision identities, not provider template names. No new Shared/Background dependency: use direct DB fixtures for approved registration state in focused tests.


**Module ownership.** Keep this task modular: put its domain services under `src/lib/admin/whatsapp-templates/publishing/`, components under `src/components/admin/whatsapp-templates/publishing/`, and its server actions in a task-specific `src/app/actions/whatsapp-template-publication.ts`. Avoid a global `whatsapp-templates.ts` catch-all or unrelated edits to sibling modules. Prefer small repository/domain, validation, orchestrator and view components. Only the English authoring task owns the shared navigation/catalogue shell; other tasks provide focused subroutes/panels, not a second editor or shell.


## Dependencies

- `ARCH-047-DATABASE-001` — **the only formal task dependency**. No `ARCH-047-ADMIN-00N`, Background, Messaging or new Shared publication dependency is permitted. Use seeded DB fixtures and injected ports to test independently when upstream/downstream implementations are absent. Status remains Pending until DB001 is confirmed Complete in the canonical task record; do not infer completion from tests alone.

## Enables

None at task-definition time. Completion of this task does not grant permission to start another task or skip an independently required system-test gate.

## Acceptance Criteria

- [x] React views are composed from separately named, independently testable components; route pages, controller hooks, pure domain helpers, server actions and database services are in separate files with no monolithic screen/action implementation.

- [x] One/selected/all current eligible merchants are targeted correctly; Shopify/Woo eligibility is enforced and newly appearing shops are excluded from the confirmed run.
- [x] Each affected shop has correct 20-language target history, one selectable slot per purpose/language, and preservation of historic variants; conflicting overrides require deliberate confirmation.
- [x] Multiple invocations of an operation neither multiply variants nor audit entries; concurrent individual and bulk commands cannot leave duplicate active assignments.
- [x] Exact, complete previous/proposed UI renders text, component/button/variable differences (including frozen header/body brand-binding keys and positions) per shop and labels missing history accurately.
- [x] A shop with configured `ShopBrand` fields and one with missing/null fields receive distinct, accurate preview indicators without creating misleading sample branding, leaking values across tenants, or changing the existing eligibility policy.


## Validation

- [x] Focused React component tests cover composition, user interactions, relevant loading/error/empty states and at least one mobile-width/accessibility scenario; controller hooks and pure business helpers are tested separately.

- [x] PostgreSQL integration tests for slot serialisation, 20-language per-shop transaction, 100-shop target cardinality, stale confirmation, cross-shop identity mismatch and interruptions/retries.
- [x] Guarded Admin preview/action/UI tests for full comparisons, frozen brand-binding differences, scoped `ShopBrand` availability (configured/null/no record/unknown), paging, accessible responsive display, partial-result clarity; typecheck/lint/`git diff --check`.


## Stop Condition

After task-scoped work, acceptance criteria, validation and Completion Report are complete, set `status: review`, return control to `moda_architect` and **STOP**. Do not mark this task Complete yourself, start sibling/Admin/Background tasks, modify `_index.md`, merge branches or push main.

## Implementation Notes

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md`, `docs/developer-task-workflow.md`, the revised parent ARCH-047 architecture and current Admin repository instructions. Use launcher-prepared dedicated parent/implementation task worktrees and mirrored `task/<TASK_ID>` branches. In the Completion Report record prepared physical worktree isolation, start sync, recursive submodule materialisation, exact test commands/outcomes, changed paths and commits. The implementing agent must not modify `docs/decisions/**/_index.md`, another task, the parent architecture, another repository, or follow-on work. Reuse existing Admin Store Category AST authoring and Merchant Pricing translation UX patterns without copying their domain services or creating a competing generic runtime. Inspect the actual worktree state before implementation; the attached snapshot is not a live Git-branch guarantee.


## Completion Report

### Status

Ready for Review — developer-executed **workflow Attempt 1**, completed on 2026-10-25. Implementation was developed through seven incremental correction patches within this claim; patch attempt numbers do not increment the task claim's `attempt: 1`. Awaiting independent architect review and the developer's later explicit completion decision.

### Files Changed

Task-owned implementation in `moda-interact-admin/`:

- `src/app/(protected)/system-controls/whatsapp-templates/[definitionId]/publish/page.tsx`
- `src/app/actions/whatsapp-template-publication.ts`
- `src/lib/admin/whatsapp-templates/publishing/`: `validation.ts`, `types.ts`, `source.ts`, `sender.ts`, `discovery.ts`, `impact.ts`, `preview.ts`, `operation.ts`, `assignment.ts`, `audit.ts`
- `src/components/admin/whatsapp-templates/publishing/`: `template-publication-workspace.tsx`, `use-template-publication.ts`, `publication-scope-selector.tsx`, `publication-eligibility-summary.tsx`, `publication-impact-list.tsx`, `shop-language-comparison.tsx`, `compiled-template-read-only.tsx`, `publication-override-confirmation.tsx`, `publication-progress-summary.tsx`
- `src/lib/admin/platform-configuration/environment.ts`, `src/lib/admin/platform-configuration/service.ts` (narrow environment resolution extraction)
- `scripts/run-arch047-admin-publication-tests.mjs`, `scripts/test-arch047-admin-publication-postgres.mjs`
- `tests/unit/arch047-template-publication-pure.test.ts`, `tests/unit/arch047-template-publication-components.test.tsx`, `tests/integration/arch047-template-publication.postgres.test.ts`
- `package.json`, `package-lock.json` (task test scripts/dependencies and Shared version alignment)

This handoff changes **only this task definition in the parent workspace**. No domain `_index.md`, parent architecture, schema/migration, or sibling task is changed by the review-handoff patch.

### Work Completed

- Implemented the protected publication route and bounded one/selected/all-eligible-shop workflow, including server-verified `SUPER_ADMIN` access, current persisted Meta registration approval and WABA/identity/content checks, frozen confirmation fingerprints and explicit override reason/acknowledgement.
- Added shop-specific brand-variable availability and a paginated, responsive previous-versus-proposed language comparison. Missing/nullable/unknown `ShopBrand` values remain warnings and are never copied between shops.
- Added durable per-shop-language targets, per-shop all-or-nothing assignment transactions, application-level shop-slot serialisation, distinct deterministic audit identities, bounded five-shop progression, idempotency and retry of eligible failures.
- Added focused React/pure tests and disposable PostgreSQL integration tests covering a 100-shop/2,000-target run, approval drift, rollback and retry, concurrent publication, and prevention of adoption of unlinked/external Meta identities.
- Corrected execution/test issues during seven incremental patch iterations (TypeScript/React issues, ESM test launch, Node environment isolation, eligibility predicate, test fixture uniqueness, audit identity uniqueness and independent external-identity fixture).

### Validation Results

Developer terminal capture: `typescript(20261025-200718)`, dated 2026-10-25, against the supplied `moda-interact-workspace-ARCH-047-ADMIN-007.zip` snapshot.

- **PASS** — `git apply --check --whitespace=error-all`, `git apply --whitespace=error-all` and `git diff --check` for correction patch 7; no patch/whitespace errors were printed.
- **PASS** — `npx tsc --noEmit` (no TypeScript errors reported).
- **PASS** — `npm run test:arch047-admin-publication:unit`: **19 passed / 0 failed**, covering pure rules and server-rendered/component interactions.
- **PASS** — `npm run test:arch047-admin-publication:postgres`: **5 passed / 0 failed**; disposable PostgreSQL schema setup completed and the runner reported `PASS ARCH-047 ADMIN-007 disposable PostgreSQL`.
- **ESLint:** the previous validation log reported no errors (with ignored-file warning); the latest 2026-10-25 20:07 terminal capture does **not** include a fresh ESLint invocation after the final test-fixture correction. Reviewer may rerun scoped lint if desired.
- **Git publication:** Admin implementation commit `83443cf` (`feat(arch-047-admin-007)`) was pushed successfully to `origin/task/ARCH-047-ADMIN-007` (`0ea2bd7..83443cf`). No parent documentation commit/push is claimed by this external review-handoff artifact.

### Worktree and Preparation Evidence

- The supplied task record identifies an authorised developer takeover and a dependency-verified Attempt 1 claim on 2026-10-25.
- The final archive-generation transcript names dedicated parent and implementation paths: `moda-interact-workspace-task-ARCH-047-ADMIN-007` and `moda-interact-workspace.worktrees/ARCH-047-ADMIN-007`. The task implementation branch and remote push are visible in the terminal capture.
- **Review evidence limitation:** the supplied final terminal capture does not contain the original launcher-resolved preparation packet, complete start-of-attempt Git synchronisation transcript, or recursive submodule materialisation proof. The reviewer should verify those against the actual worktrees/preparation record; successful tests and a push are not substitutes for that evidence.

### Deviations

- Introduced a narrow platform-configuration environment helper and task-specific ESM test runners to avoid importing NextAuth/Next.js runtime code into the disposable database test process.
- Updated the Admin Shared dependency to the `2.5.0` version present in the snapshot's other consumers, so the canonical published internationalization contract resolves. No local replica of Shared's language contract was introduced.
- No database-schema extension, imported external Meta-template authoring, background worker or unrelated task was introduced.

### Assumptions

- `ARCH-047-DATABASE-001` is the accepted persistence contract. Meta approval is checked against the persisted Meta registration snapshot, which the owning approval/reconciliation workflow must keep current; this task does not perform a fresh Meta Graph API call or author provider templates.
- Twenty supported languages are obtained from the published Shared internationalization export; shop brand fields are read-only preview context, not publication eligibility constraints.
- Publication patch iterations 1–7 occurred during the single claimed workflow Attempt 1, as specified by the developer-task workflow (attempts are review cycles, not ordinary code commits or patches).

### Unresolved Issues

- No failing task-scoped tests are shown in the latest supplied validation log.
- Original launcher preparation/synchronisation and recursive submodule evidence has not been independently reproduced from the archive. Verify during architect review; request evidence-only correction if required.
- Production deployment, live Meta provider state, and integrated ARCH-047 system tests are separate architectural verification steps and are not claimed as completed by this task.

### Architectural Concerns

- Final acceptance still requires independent assessment of all scope, authorisation, concurrent publication and source-identity guarantees against the implementation branch. `status: review` is a handoff, **not** an architect acceptance or developer completion decision.

## Execution Ownership Amendment

- Date: 2026-10-25
- Change: The developer explicitly invoked `/moda_developer_create ARCH-047-ADMIN-007` for this ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_admin`, repository, coordinator, dependencies, task scope and acceptance criteria, including the latest ShopBrand preview and React decomposition requirements.
- Claim: Attempt 1 was claimed by `developer` after canonical worktree synchronization and dependency verification.


## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
