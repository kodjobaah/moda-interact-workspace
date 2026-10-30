---
id: ARCH-052-ADMIN-002
architecture_id: ARCH-052
title: Author approved optional checkout and alternative-product IMAGE headers
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 35
executor: copilot
claimed_at: 2026-10-30T13:00:29Z
attempt: 2
depends_on:
- ARCH-052-SHARED-003
- ARCH-049-ADMIN-002
enables:
- ARCH-052-BACKGROUND-008
- ARCH-052-BACKGROUND-012
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: 2026-10-30
---

# ARCH-052-ADMIN-002: Author approved optional checkout and alternative-product IMAGE headers

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Freeze optional checkout/alternative-product IMAGE template identities and submit their immutable registration intents without a sample handle; the Background Meta provider adapter supplies a trusted sample only at provider creation. No product-image table or new ShopBrand role.

## Context

ARCH-049 ADMIN002 already adds frozen ShopBrand media roles to Meta template authoring. A checkout product IMAGE role is distinct and optional; Meta approval applies to the exact header family. Source inspection confirms `meta/snapshot.ts` currently rejects frozen IMAGE registration before it is queued, while `moda-interact-background/src/services/meta-template-management/` alone calls Meta Graph. ADMIN-002 therefore owns authoring and durable registration intent, not provider sample upload. Background-012 owns the separate provider-only sample enrichment.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Use Shared-002 `CHECKOUT_PRODUCT` media role and Shared-008 exact MCP product images; author separate immutable IMAGE and text-only fallback variants for `promotionTarget:CHECKOUT` and `promotionTarget:ALTERNATIVE_PRODUCT` where approved, under existing INITIAL purposes.
- Author the semantic `CHECKOUT_PRODUCT` binding for the exact checkout product or Background-010-selected alternative product/variant; Background-007 alone enforces shop/product/variant binding at send preparation. Never accept an arbitrary AI-selected image URL. Preserve ARCH-049 media origin validation and frozen Meta header digests; reject header type/role changes after approval.
- Preserve and test the immutable IMAGE/TEXT variants, role/promotion-target invariants, translation integrity and exact approved TEXT fallback selection. Send-time image availability/product mismatch/revocation belongs solely to BACKGROUND-007.
- Correct Admin frozen registration planning and `READY_TO_SUBMIT` confirmation to allow an IMAGE header **without any sample handle** in the immutable AST, fingerprint or database snapshot. It must never accept a client-supplied URL or handle. Provider-only Meta handle enrichment is assigned to BACKGROUND-012.

## Out of Scope

- No actual Shopify/Woo photo download, R2 processing, Meta sample-media upload, Graph API creation or live send. No Admin-owned runtime image proof, `VERIFIED_PROVIDER_IMAGE` object, proof TTL or persisted verification evidence. Actual provider approval is not an Admin task completion gate; it is an integrated/deployment gate after BACKGROUND-012.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Admin defines and freezes the semantic IMAGE role and separately approved TEXT fallback identity. **There is no five-minute media-proof contract or `VERIFIED_PROVIDER_IMAGE` dependency.** Admin neither fetches live product media nor validates its send-time freshness.
- Freeze `components`, role binding, promotion target, locale and digest **without** `example.header_handle`. Change `frozenLocaleSnapshot()` and associated planning tests so an IMAGE locale can be confirmed as `READY_TO_SUBMIT` without a sample: no `IMAGE_SAMPLE_HANDLE_REQUIRED` at the Admin intent boundary. Reject malformed, injected or untrusted IMAGE examples. The provider-create boundary in Background must still fail closed without a valid Meta-issued sample handle. Preserve TEXT registration and approval behaviour unchanged.
- The canonical sample URL is `https://www.modainteract.com/assets/whatsup-sample.jpeg`, but it is **not** saved in the authoring AST, trusted input from a merchant, or written to a registration snapshot. Background-012 owns that fixed-URL fetch, validation, Meta upload and outbound-only handle insertion. ADMIN-002 is independently reviewable before BACKGROUND-012 is Complete.
- Background-007 must resolve the exact current-shop product/variant via authenticated MCP during each send-preparation attempt. Only its **Background-local** validated `READY` result can accompany an independently approved IMAGE template. If the media is missing, unsafe, unavailable, mismatched, or its source has changed/revoked, use the separately approved TEXT template for the same purpose and promotion target or return typed no-send. Retries re-resolve; never mutate approved template components.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

## Work Items

- [x] Implement new header role UI/validation and preview.
- [x] Reuse and regression-test the existing paired variant fallback publication/eligibility contract.
- [x] Correct `meta/snapshot.ts` frozen IMAGE registration planning: accepted semantic IMAGE role without an example handle produces an unchanged immutable digest and `READY_TO_SUBMIT` intent. Any client-supplied sample URL/handle fails closed.
- [x] Add deterministic Admin tests for the IMAGE registration plan across locales, identical-plan replay and frozen hash/role drift; confirm existing TEXT behaviour and no provider call from Admin. The Background provider upload and real Meta approval are tested separately by BACKGROUND-012 and terminal system tests.

## Interfaces / Contracts

Existing ARCH-049 media conventions and published Shared-002 `CHECKOUT_PRODUCT` + `promotionTarget` bindings remain authoritative. Admin produces a frozen `MetaLocaleSnapshot` / `MetaSubmissionPlan` with `HEADER.format = IMAGE` and **no** `HEADER.example.header_handle`; its normal transaction persists a `READY_TO_SUBMIT` `WhatsAppTemplateMetaRegistration` for the current approved WABA. `submittedContentHash` and role/locale checks remain stable. Background-012 consumes the frozen registration, adds a *provider-request-only* Meta-issued sample handle and POSTs through the existing adapter. No new Shared or Prisma contract; never persist the handle or modify the approved content digest. Background-007 separately owns authenticated MCP image reads and its local `READY` / `UNAVAILABLE` send-time result. No timed proof.

## Dependencies

- `ARCH-052-SHARED-003` — must be Complete and architect-accepted before this task starts.
- `ARCH-049-ADMIN-002` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-BACKGROUND-008`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`
- `ARCH-052-BACKGROUND-012`

## Acceptance Criteria

- [x] IMAGE header with product role compiles, reviews and queues the correct immutable registration intent only through Admin; no Graph template creation or IMAGE approval is falsely asserted by the Admin task.
- [x] Admin freezes distinct IMAGE and TEXT template identities for each purpose/promotion target; stored IMAGE examples omit sample handles and external URLs, while content hashes/role validations, replay and translations remain sound.
- [x] All existing Admin TEXT approval/publication/fallback behaviour remains intact. BACKGROUND-007 alone enforces runtime `READY` image, safe TEXT fallback or typed no-send. BACKGROUND-012 is independently gated on accepted Admin frozen IMAGE intents.

## Validation

- [x] Admin authoring/preview, IMAGE-without-sample frozen fingerprint, replay/translation and publication-planning regression suites (Meta provider network mocked).
- [x] Admin typecheck, relevant focused unit tests, changed-file lint, build and `git diff --check`; distinguish known baseline failures from regressions.
- [x] Assert no Admin-side fetch/Meta upload and no raw sample handle/URL in frozen snapshots or logs.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/media/`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/publishing/`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/meta/snapshot.ts` (remove **intent-time** requirement; keep immutable media-role/hash validation)
- `moda-interact-admin/src/lib/admin/whatsapp-templates/meta/submission.ts` (confirm existing durable intent flow without provider I/O)
- `moda-interact-admin/tests/unit/`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

## Completion Report

### Attempt 1 (Historical)

**Historical status: Blocked at Attempt 1; superseded by the clarified Attempt 2 ownership contract below.** The report and validation record below describe the original attempt and are retained as history. Its conclusions that Admin registration must remain blocked on a provider sample handle and that Admin acceptance depended on Background runtime proof are no longer applicable: Admin owns the immutable, handle-free registration intent; Background-012 owns provider sample upload and Background-007 owns runtime image match/fallback.

### Files Changed

- `moda-interact-admin/package.json`
- `moda-interact-admin/src/components/admin/whatsapp-templates/authoring/template-authoring-workspace.tsx`
- `moda-interact-admin/src/components/admin/whatsapp-templates/authoring/template-content-editor.tsx`
- `moda-interact-admin/src/components/admin/whatsapp-templates/media/shop-brand-media-header-section.tsx`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/types.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/validation.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/meta/contracts.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/meta/snapshot.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/publishing/source.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/publishing/types.ts`
- `moda-interact-admin/tests/unit/arch047-template-meta-snapshots.test.ts`
- `moda-interact-admin/tests/unit/arch047-template-publication-pure.test.ts`
- `moda-interact-admin/tests/unit/arch049-admin-media-compiler.test.ts`
- `moda-interact-admin/tests/unit/arch049-admin-media-components.test.tsx`
- `moda-interact-admin/tests/unit/arch049-admin-media-projection-vectors.test.ts`

### Work Completed

Added the Shared `CHECKOUT_PRODUCT` role to the Admin authoring AST and validation, with explicit offer-target requirements. Added a distinct product-image authoring option that is not backed by ShopBrand sample assets or arbitrary URLs. Preserved immutable role/digest behavior and added locale role-drift checks to Meta submission planning and publication translation validation. Confirmed and tested that existing publication selection chooses the exact approved TEXT variant for the same purpose/target rather than mutating or selecting the IMAGE variant. No product-image resolver or Meta sample-media workaround was introduced.

### Validation Results

Launcher packet: prepared execution for attempt 1; claim commit `0bd17e5461d5301a608fcd096cd1f9bbfa198a95`; dependency gate passed for `ARCH-052-SHARED-003` and `ARCH-049-ADMIN-002`; database submodule initialized at `f16d5fc955b1fa1215177cc89fb6fd326bfa65c`.

- `npm run test:arch049-admin-media:unit`: passed, 26 unit tests and 1 SQL test.
- `npm run test:arch047-admin-authoring:unit`: passed, 33 tests.
- `npm run test:arch047-admin-compilation:unit`: passed, 14 tests.
- `npm run test:arch047-admin-publication:unit`: passed, 22 tests.
- `npm run test:arch047-admin-translations:unit`: passed, 16 tests.
- `npm run test:arch047-admin-meta:unit`: passed, 14 snapshot/service tests and 1 UI test.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed; emitted non-fatal existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings.
- `git diff --check`: passed.
- `npm run test:unit`: 555/572 passed; 17 failed. Failures include unrelated commerce-policy mock harness dependency mismatches, CJS/ESM interop and top-level-await loader errors; the focused authoring/publication/translation/media/Meta scripts above pass.
- `npm run lint`: blocked by an existing `react-hooks/set-state-in-effect` error in unchanged `src/components/admin/whatsapp-templates/media/use-shop-brand-media-role.ts:26`; focused lint on changed source had no errors.

### Attempt 1 Deviations (Historical)

The requested `VERIFIED_PROVIDER_IMAGE` five-minute proof/resolver and exact selected product/variant/source-revocation checks were not implemented in Admin or Background. Those are not Admin requirements under the clarified contract: Background-007 owns runtime enforcement. Attempt 1 also failed to create the Admin-owned handle-free registration intent and incorrectly treated the provider sample producer as an Admin prerequisite. No live messaging or product-media fetch was performed.

### Assumptions

Shared 2.6.0's exported `RecoveryTemplateHeaderMediaRole` is authoritative for CHECKOUT_PRODUCT. The existing publication identity selector supports distinct IMAGE/TEXT variants keyed by promotion target and header format. The prepared launcher supplied canonical worktrees and dependency evidence, which were used without repeating startup discovery or claim operations.

### Attempt 1 Unresolved Issues (Historical; corrected by Attempt 2)

1. Background-007 owns runtime product/variant matching, source-change handling, and TEXT fallback/no-send; this is a downstream task, not a blocker to Admin review.
2. Background-012 owns the trusted IMAGE sample upload-handle producer; the provider POST remains fail-closed until that task is complete. It is not a prerequisite to Admin review.
3. The Attempt 1 broad `npm run test:unit` and full lint findings remain historical observations only. Attempt 2 ran the focused required suites, changed-source lint, typecheck, production build and diff checks successfully.

### Attempt 1 Architectural Concerns (Historical)

The prior request to block Admin review on Background proof and sample-upload work is superseded by the Attempt 2 Architect Review contract. Background ownership remains recorded above; no Admin-local architectural blocker remains.

### Attempt 2 Completion Report

#### Status

Ready for Review. Admin now freezes and confirms handle-free IMAGE registration intents. No provider upload, Graph POST, live approval, product-media source resolution or runtime proof was implemented. The Background provider POST remains fail-closed until BACKGROUND-012 supplies its trusted sample handle; BACKGROUND-007 retains runtime image matching and fallback ownership.

#### Files Changed

- `moda-interact-admin/src/lib/admin/whatsapp-templates/meta/snapshot.ts`
- `moda-interact-admin/tests/unit/arch049-admin-media-compiler.test.ts`
- `moda-interact-admin/tests/unit/arch047-template-meta-snapshots.test.ts`
- `moda-interact-admin/tests/unit/arch047-template-meta-service.test.ts`

#### Architect Review Corrections

1. Implemented: handle-free semantic IMAGE snapshots now remain immutable `READY_TO_SUBMIT` intents; caller-injected IMAGE sample handles and URLs are rejected. Verified by IMAGE snapshot and confirmation tests.
2. Implemented: committed authoring, preview, translations, explicit promotion targets and TEXT behavior remain intact. Verified by focused authoring, compilation, translation, publication, Meta and media suites.
3. Implemented: no upload, provider POST, live approval, Shopify/Woo source resolution or timed proof was added. Meta confirmation tests verify durable Admin intent creation and replay without provider events/calls.

#### Validation Results

- `npm run test:arch049-admin-media:unit`: passed, 27 unit tests and 1 SQL test.
- `npm run test:arch047-admin-meta:unit`: passed, 16 snapshot/service tests and 1 UI test.
- `npm run test:arch047-admin-authoring:unit`: passed, 33 tests.
- `npm run test:arch047-admin-compilation:unit`: passed, 14 tests.
- `npm run test:arch047-admin-publication:unit`: passed, 22 tests.
- `npm run test:arch047-admin-translations:unit`: passed, 16 tests.
- `npx tsc --noEmit`: passed.
- `npx eslint src/lib/admin/whatsapp-templates/meta/snapshot.ts`: passed. Test files are ignored by the repository ESLint configuration.
- `npm run build`: passed. Existing non-fatal BullMQ dynamic-dependency and optional `@valkey/valkey-glide` resolution warnings remain.
- `git diff --check`: passed.

#### Deviations and Unresolved Issues

No Admin-owned deviation or blocker remains. Provider-side sample attachment/Meta creation is explicitly owned by BACKGROUND-012, and send-time image resolution/fallback is explicitly owned by BACKGROUND-007. No live Meta approval, provider call or send-time behavior is claimed by this report.

#### Assumptions

The existing Meta registration transaction is the durable `READY_TO_SUBMIT` intent boundary. Its frozen projection contains compiler-authored IMAGE components and semantic role bindings only; provider-only handle enrichment remains outside Admin. The prepared launcher established attempt 2 and the dependency gate, so no startup discovery, synchronization or claim was repeated.

#### Git Evidence

- Parent claim commit: `55f555bfbbe5fe3a06d6b486bd2fedf9568fa709`.
- Implementation starting commit: `8432eac90ffd50d078d82155655f2193f2040df3`.
- Implementation commit: `76809d5005c62fec8fdf1c1707310df69991badc`.
- Parent review-report commit: this task-file commit.

### Current Task Status

Ready for architect review; task status is `review`.

### Review Finding Follow-up

Updated the Admin IMAGE guidance to state that Admin queues a handle-free registration intent and Background supplies the provider sample handle during Meta submission. The product-image selector now attributes exact product/variant resolution at send time to Background, without implying a timed proof requirement. Updated the component assertion to guard the Background-owned guidance.

- Implementation commit `efb18cb` (`fix(admin): clarify image header submission guidance`) is pushed on `task/ARCH-052-ADMIN-002`.
- `npm run test:arch049-admin-media:unit`: passed, 27 unit tests and 1 SQL test.
- `npx eslint src/components/admin/whatsapp-templates/authoring/template-review-summary.tsx src/components/admin/whatsapp-templates/media/shop-brand-media-header-section.tsx`: passed.
- `git diff --check`: passed; implementation-worktree search found no remaining obsolete sample-handle or timed-proof guidance in the Admin WhatsApp template components.


## Architect Review
### Review Status

Changes Requested.

### Review Notes

30 October 2026, **Attempt 2 architectural unblock**. The developer removed the arbitrary five-minute `VERIFIED_PROVIDER_IMAGE` contract (Attempt 1 correction). The agent's earlier Attempt 1 Completion Report above is preserved verbatim as historical evidence, not a continuing requirement. The source inspection confirms the Admin `frozenLocaleSnapshot()` currently throws `IMAGE_SAMPLE_HANDLE_REQUIRED` for every IMAGE registration, while **Background** owns the actual Meta Graph registration adapter. This is an ownership/specification problem, not a missing Admin media processor.

**Rework contract for ADMIN-002:**

1. Change Admin frozen locale and `makeMetaSubmissionPlan()` handling so an IMAGE semantic binding with no sample handle is valid as an immutable `READY_TO_SUBMIT` registration intent. Do not fabricate handles, inject a fixed URL into Admin metadata, or weaken role/fingerprint/locale validation. If a caller attempts to inject an untrusted `header_handle` or URL into the frozen projection, reject it.
2. Retain the existing committed authoring, preview, translation, explicit promotion-target and independently approved TEXT fallback work. Add focused tests for IMAGE intent planning/confirmation, digest stability, replays and role drift; TEXT behaviour must not regress.
3. Do **not** implement provider image upload, Graph POST, live Meta approval, Shopify/Woo source resolution, or a five-minute proof. The fixed image source and Meta upload are the bounded `ARCH-052-BACKGROUND-012` task. Runtime image match/fallback remains `ARCH-052-BACKGROUND-007`, downstream of ADMIN-002.
4. Reclaim **this same task** on its dedicated mirrored worktrees using the canonical launcher and prior claim evidence; retain `attempt: 1` until the next claim increments it. Correct the Completion Report and return `status: review` only when the Admin-specific criteria pass. There is no need to reimplement already committed authoring code.

`status: ready`, `executor: null` and `claimed_at: null` restore reclaimability. ADMIN-002 depends only on two already-Complete tasks; BACKGROUND-012 must **not** become a reverse dependency on ADMIN-002. Keep Background provider POST fail-closed until its own sample-producer task passes.

### Reviewed Files

- `moda-interact-admin/src/lib/admin/whatsapp-templates/meta/snapshot.ts` — currently rejects frozen IMAGE registration without sample handle.
- `moda-interact-admin/src/lib/admin/whatsapp-templates/meta/submission.ts` — confirms durable intent inside a database transaction, no provider network.
- `moda-interact-background/src/services/meta-template-management/meta-graph.adapter.ts` and `service.ts` — own Meta Graph creation; provider requires a handle on final IMAGE POST.
- `moda-interact-background/src/services/meta-template-management/contracts.ts` — current provider image validation.
- ARCH-052 Background-007 task and preserved Attempt 1 Completion Report.

### Validation Reviewed

Architectural/documentation review only. Earlier focused Admin tests were agent-reported in Attempt 1; no new source changes, Meta upload, provider approval, or live send have been executed by this review. The next Admin attempt must run the specified source validations.

### Architecture Conformance

Admin owns frozen authoring and intent; Background owns provider sample attachment and send-time product images. Frozen hashes and tenant/WABA/role approval remain authoritative; only a Meta-issued handle may reach the final provider POST. No new Shared/database proof or storage, no arbitrary time window, no new messaging pipeline.

### Follow-up

Run `/moda-task ARCH-052-ADMIN-002` for Attempt 2 through the canonical launcher, review its submitted implementation and accept it independently. Then `ARCH-052-BACKGROUND-012` becomes eligible to implement the fixed-URL Meta sample producer. Terminal Shopify/Woo system testing checks actual Meta approval and product-image send gating.
