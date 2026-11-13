---
id: ARCH-075-ADMIN-007
architecture_id: ARCH-075
title: Compile provider-valid common Meta body boundaries
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 5
executor: codex
claimed_at: 2026-11-13T18:01:39Z
attempt: 1
depends_on:
  - ARCH-075-ADMIN-001
  - ARCH-075-ADMIN-005
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Compile provider-valid common Meta body boundaries

## Architecture

ARCH-075; `docs/architecture/ARCH-075-ordered-recovery-message-layout.md`; coordinator moda_architect.

## Objective

Reject Meta-invalid leading/trailing BODY parameters while compiling the existing common shop frame and reviewed localized opt-out into provider-valid replacement templates.

## Context

Root read-only production evidence:120 reviewed registrations failed template_create HTTP400/code100/subcode2388299, no approvals/provider IDs. Root verified the official Meta error-code page (`https://developers.facebook.com/documentation/business-messaging/whatsapp/support/error-codes`) states2388299 forbids leading/trailing parameters. Saved private official row receipt is `official-meta-2388299-rule.txt`. Actual commonMetaBody currently concatenates header, scenario body plus static draft.footer, then common checkout conditional. The current common header begins shop.name and conditional must end checkout.url, producing exactly the forbidden provider BODY boundaries. Shared intentionally preserves the final checkout URL contract for ordered AI/human rendering; no Shared release is required for this provider projection correction.

## Scope

Admin-owned pure authoring validation/compiler/common-layout projection, directly related compilation/read/preview/confirmation safety and regression tests. Reuse reviewed localized source text, existing compiler/hash/binding mechanisms and current published Shared contract. Inspect impacted frozen-source verification callsites before changes.

## Out of Scope

Shared/BG/Database/runtime edits or releases; rewriting existing immutable sources/locales/submissions/registrations; live clone/review/submit/retry/activation; blanket120 retries; credentials/providers/branding image selection; Meta product-image headers; new framework or sender-pool work.

## Requirements

- For NEW common-layout Meta compilation, project common header -> scenario body -> common checkout conditional -> existing reviewed static draft.footer opt-out. No untranslated injected English, bare punctuation, invisible padding, inferred URL content, dropped opt-out or duplicated checkout binding. The dynamic checkout link remains the footer link; the localized opt-out is its final provider-safe text tail. Product images remain separate; logo header media role remains shop brand only.
- A new immutable common header may be authored by root with meaningful reviewed localized fixed prefix before shop.name (for example localized Shop:/Website: labels). Do not silently mutate that common source, generate translations or patch the saved hash in this task. Invalid old common headers must be reported with actionable field validation, not prefixed ad hoc at transport time.
- Validate the FINAL projected Meta BODY, including common frame, and ordinary noncommon Meta BODY: after ignoring whitespace, it must not begin/end with a parameter. Require meaningful fixed boundary text; whitespace, punctuation-only or formatting tricks must not satisfy the rule. Do not reject a variable safely surrounded by real text. Keep translated Unicode letters valid. Avoid inventing an unsupported universal variable-ratio rule.
- Reuse one pure final projection/validation path without compiler-validation recursion. Authoring preview, reviewed confirmation and actual submitted prepared components must agree, with same order, examples, sequential binding positions and content hash. Enforce existing1024characters/10parameters on final BODY; fail without truncation or content removal.
- Preserve AST schemaVersion1 and existing binding names. Existing frozen legacy noncommon and submitted common snapshots remain immutable; no recompile-and-rewrite migration. Inspect compilation/reads.ts, translations/source-snapshot.ts and meta/snapshot.ts: new compilation may produce a fresh hash, but old submissions must not silently acquire new content. New sources/locales must be cloned/reviewed/submitted under new immutable identity/hash. If preserving existing read/clone paths needs a contract/version change beyond Admin scope, return concrete evidence before expanding.
- All20 supported locales and all six scenario variants must be exercised with actual reviewed localized static opt-out fixtures and a provider-safe new common header. Preserve trusted common reference/website/name/checkout, media role, example and immutable hash checks. Legacy no-common valid output should remain unchanged.
- Root owns operational canary-first rollout: after source acceptance/deployment, clone/review one corrected English source and common header; inspect exact projected BODY, then submit one canary. Only successful provider response/real approval permits expansion; preserve failed120 history, do not reset it. Activation and actual Eugene Meta/AI/human ordered logo/details/product/footer proof remain later operational gates.

### Narrow historical verification clarification

Saved reads and approved publication currently recompile authoring to establish immutable hash identity. Permit one server-only verifier for exact stored source/prepared hashes against only the known old/current deterministic projection, returning stored bytes unchanged. This is historical verification only: never expose a caller-controlled bypass, accept arbitrary prepared content, rewrite frozen hashes or use legacy mode for saving/new compilation. Existing approved read/publication/display/clone may retain exact old snapshot. New compilation/reconstruction, new submission and every technical retry/re-registration admission must strictly validate final stored BODY. Invalid old translation/recompile requires clone/corrected source, not silent regeneration. Add tamper/wronghash/old-invalid-newsubmit-and-retry negatives plus old-approved-read preservation. Report any genuinely cross-owner retry gap before extending implementation.

## Work Items

- [x] Inspect final projection and immutable read/preview/submission paths; capture current boundary failure regression.
- [x] Implement bounded projection reorder and actionable final BODY validation without changing Shared or saved records.
- [x] Prove all20 locales/six scenarios plus frozen legacy/preview/hash/binding regressions.
- [x] Run required validation and publish exact matching source/report for independent review.

## Interfaces / Contracts

Existing published `@modainteract/moda-interact-shared/commerce/presentation` common layout reference/finalURL contract unchanged. Admin owns provider projection and prepared content hashing; Background consumes frozen prepared components/bindings. No contract/version release is authorized.

## Dependencies

ARCH-075-ADMIN-001 and ARCH-075-ADMIN-005 are architect-accepted Complete.

## Enables

Root-owned corrected immutable source review, canary registration and later verified operational activation; no implicit task execution.

## Acceptance Criteria

- [x] Current leading/trailing common BODY failure captured before fix; corrected new projection has fixed localized boundaries, one checkout binding and preserved opt-out.
- [x] Common and ordinary invalid boundary input fails before submission; valid Unicode/static-boundary input passes.
- [x] Preview/confirmation/actual components, examples/bindings/hashes match; final size bounds and immutable legacy behavior are preserved.
- [x] Required checks pass; no live/source-contract scope mutation, complete preparation/report evidence recorded.

## Validation

- [x] Focused compiler/common/noncommon boundary tests including current failure RED/GREEN; whitespace/punctuation/empty-tail/Unicode/parameter-order/size negatives.
- [x] All20 supported locale ×six scenario projections and exact preview/prepared consistency; immutable source/hash/submission/legacy compatibility regressions.
- [x] Declared Admin full unit/security checks, typecheck/lint/production build; run build-dependent tests after build where necessary. Inspect actual package scripts, no repeated green heavy checks without change.
- [x] Exact source diff/privacy and parent/implementation isolation/synchronization evidence. Remote exact-head checks before root merge.

## Stop Condition

After scoped validation and exact mirrored source/report publication, set review and return to moda_architect. No self-acceptance, merge, deployment, live submissions or follow-on work.

## Implementation Notes

Use normal launcher-prepared dedicated matching parent/implementation worktrees and durable claim. You are not alone: preserve all newer main behavior and primary originals. Return a concrete ownership/contract gap before expanding. Root owns merges and all live provider operations. Do not claim provider acceptance from local compiler checks.

## Completion Report

### Status

Ready for Review. Exact implementation `69fa0a258fc426c6007d02193d7c86659824daf7`, pushed on `task/ARCH-075-ADMIN-007`; PR96 https://github.com/kodjobaah/moda-interact-admin/pull/96 . Exact-head Vercel deployment and Preview Comments checks succeeded. Root owns acceptance, merges, deployment and all live provider actions.

### Files Changed

27 task-owned files:12 production modules covering common projection, strict authoring/final BODY validation, deterministic preparation, server frozen verification, saved detail/review, translation snapshot integrity, Meta admission/retry and existing-approved publication reads; three existing PostgreSQL runner/launcher files; one static reviewed opt-out fixture and existing Meta test helper; one activation PostgreSQL fixture; nine directly related unit suites. No package, Shared, Background, Database or runtime sender changes.

### Work Completed

- Confirmed provider cause from root evidence: template-create HTTP400/code100/subcode2388299. The official [Meta error-code reference](https://developers.facebook.com/documentation/business-messaging/whatsapp/support/error-codes) prohibits BODY parameters at the start/end. Captured two RED regressions before correction: old common order ended in checkout parameter, and ordinary boundary parameters were accepted.
- New common Meta projection is header -> unchanged scenario body -> common checkout conditional -> exact reviewed localized static opt-out. Native Meta FOOTER stays empty in common mode. No content is removed, translated, truncated or padded. Existing Shared final-URL layout and product/logo roles remain unchanged.
- One pure positional projection feeds validation/compiler/previews, examples, sequential semantic bindings and prepared hashes. Strict final BODY checks enforce1024characters/10parameters, meaningful Unicode fixed text before/after parameters, and exactly one common BODY checkout binding. Whitespace, punctuation, numeric padding and default-ignorable/invisible-letter fillers cannot satisfy the boundary rule. No variable-ratio rule was introduced.
- Default new authoring/reconstruction, submission-plan admission and every Admin technical retry use strict checks. Invalid saved common projection cannot start new translations under the old identity: Clone as New is required. Existing no-common valid output and historical optional empty TEXT-header binding compatibility remain intact.
- Server-only frozen verification accepts only exact stored hashes matching known current/old deterministic common order or the known omitted-empty TEXT-header binding shape. It returns stored bytes unchanged, never saves a legacy projection or exposes a request bypass. Saved English/translated review, detail and existing approved publication preserve immutable history; new submission/retry remains blocked for invalid historical BODY. IMAGE sample/URL injection and missing-header guards remain enforced.
- Actual authoring-hook tests prove the valid path uses compiled preview, while Clone as New retains an invalid historical draft/body/footer and becomes valid only after explicit selection of a corrected common reference. No initializer/reset workaround or immutable source mutation.
- Reused the existing native-ESM publication test runner for the old authoring/compilation PostgreSQL launchers, correcting their pre-test import-condition failures. Disposable-only/localhost checks, migrations and cleanup are unchanged. Activation fixture now supplies its explicit test environment and static opt-out; transactional/CAS/audit/cohort assertions remain intact.

### Validation Results

Canonical bootstrap: Node24.19.0/npm11.17.0. No remaining application/test failures; no live writes or provider requests.

- Full declared unit baseline:826/826 passed. Two later authoring-hook proof tests initially exposed test-harness path/type inference, corrected using the established explicit repository-root adapter and a typed test export. Final affected suite (`node scripts/test-unit.mjs tests/unit/arch075-meta-body-boundaries.test.ts tests/unit/arch049-admin-media-compiler.test.ts`):20/20 passed, including both new proofs, Unicode/padding/size/duplicate-binding, historical/tamper/hash/clone/admission and media trust negatives. Coordinator accepted broad826 plus final affected20 as adequate; no redundant broad repetition after these test-only additions.
- All20 locales ×six scenarios exercised using120 actual reviewed static opt-out fixtures. Exact preview/prepared/confirmation components, examples, ordering, semantic positions, hashes and unchanged input bytes verified.
- Additional protected read-only preflight used all120 actual reviewed scenario/locale ASTs plus the actual new common English source/snapshot and strict reconstruction of19 real translated outputs:120/120 passed; maximum595 BODY characters and7 parameters. Exact localized opt-out and single checkout binding preserved. Only aggregate results and sanitized static opt-out strings are published; root retains protected input/output receipts.
- Six declared isolated PostgreSQL suites passed15 tests: authoring2, translations2, compilation3, Meta4, common-layout2, common-activation2. Each used its own disposable pgvector PostgreSQL container and migration history, then cleanup; no external/hosted database override.
- Declared security/observability suite:331 passed,0 failed,3 build-dependent tests initially skipped. After production build the real production-server preload/export/failure-isolation suite passed3/3,0 skipped.
- Exact-source `npx tsc --noEmit` and `npm run build`: passed after the test-only type declaration correction; Next16.3.3 webpack production compilation/typecheck/prerender completed. Full ESLint passed with0errors and the unchanged nested Database anonymous-default-export warning. Optional BullMQ Valkey build warnings remain warnings; no dependency change.
- Exact final build import graph: frozen-verifier diagnostic markers in4 server outputs and0 static/client JavaScript outputs. Browser authoring compiler/hook never imports the historical verifier; Node digest remains on saved server paths.
- Exact head remote: Vercel SUCCESS and Vercel Preview Comments SUCCESS. Repository declares no GitHub Actions workflows. `git diff --check`, explicit27-file staging whitelist, clean source worktree, static-fixture privacy scan and unchanged nested Database reference passed.

### Preparation / Isolation Evidence

Normal `/moda-task` preparation succeeded: Attempt1/codex, dependencies passed, durable parent claim `ab2730b03b9d3287439bf7c94d944223c3fb7ccb`. Canonical primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-ADMIN-007`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-ADMIN-007`. Matching mirrored task branch. Launcher fetched/synchronized both repositories, incorporated current main and initialized/verified recursive submodules. Implementation base `48269c3507ed0196240f10f1aa626a2fa41330b8`; unchanged nested Database `2e14f8668346dfc135aa12f8d1fbc94e05c12ce7`. Historical-verification clarification reread from canonical parent task. No primary/shared checkout was switched or modified; no private export, provider/shop identity, credential, generated bundle or operational receipt was staged.

### Deviations

Bounded existing test-runner reuse was needed for two old declared PostgreSQL commands that failed before tests under import-only Shared exports/global CJS conditions. Two directly related activation fixture assumptions were corrected. No runtime/framework, provider policy, dependency or validation-contract expansion.

### Assumptions

Root's actual provider error and official-rule evidence are authoritative. New meaningful localized common labels and replacement source reviews remain operator-authored immutable content. This task compiles/verifies them; it does not create/translate/activate them in a hosted environment.

### Unresolved Issues

Local/remote source checks do not establish real Meta acceptance. Root must deploy this source, clone/review corrected immutable replacements, inspect exact projected content and submit one canary before expansion. Preserve failed history; no blanket retry. Real approvals, coordinated activation and genuine Meta/AI/human/logo/product/footer delivery proof remain operational gates.

### Architectural Concerns

No cross-owner/schema/version gap. Existing Shared contract and frozen historical content remain unchanged. No provider acceptance or ARCH075 completion claim is made.

## Architect Review

### Review Status

Accepted

### Review Notes

Independently reviewed exact published source `69fa0a258fc426c6007d02193d7c86659824daf7` and immutable report `2136b663e49001b51eb7130f02ace8075af04f73`. Confirmed common projection now retains authored localized opt-out after checkout; final common/noncommon BODY boundaries and limits are checked before new compilation/submission/technical retry. Exact frozen history remains readable and cannot bypass new admission. No findings.

### Reviewed Files

All production projection/validation/frozen server verifier and callers; saved review/detail, publishing, translation and Meta plan/retry paths; actual hook/120matrix/historical/media negative tests; existing ESM PostgreSQL runner/launcher reuse and activation fixture. Reviewed normal launcher isolation/synchronization/recursive nested Database proof and unchanged primary source.

### Validation Reviewed

Two current-failure RED regressions then passing120locale/scenario projection matrix; actual protected120reviewed AST preflight passed (maximum595characters/7parameters). Broad826unit plus finalaffected20, security331 plus postbuild3, all15tests across six disposable PG suites passed. Exact typecheck/build, lint0errors, diff/privacy and Vercel/Preview checks passed. Actual build graph has0client/4server historical-verifier markers. Reviewed explicit test-only additions/targeted final validation sequence; no redundant heavy rerun.

### Architecture Conformance

Conforms to Admin-only provider projection ownership and existing Shared immutable finalURL/common reference. One positional projector preserves preview/examples/bindings/hash identity; meaningful Unicode boundaries reject punctuation/default-ignorable padding. Frozen compatibility is server-only exact known projection/hash verification returning unchanged bytes, not authoring authority; strict new plan/retry and translation-clone gates remain. IMAGE sample trust and logo/product separation preserved. No schema, dependency, Shared release, Background change or hosted mutation.

### Follow-up

Root integrates source then accepted parent/gitlink and verifies deployment. Clone/review corrected immutable content and submit one English canary before expanding; retain failed120 history. Real Meta approval, coordinated common activation and genuine Eugene Meta/AI/human logo/details/product/checkout proof remain required. ARCH075 remains In Progress; source acceptance is not provider/live acceptance.

## Developer Integration

Admin PR96 merged to main as `8d5acec9813dbd11d610dd4121d1353a21dacd26` after architect acceptance and successful local/remote checks. Canonical workspace Admin gitlink follows that merge. Production deployment, corrected replacement registration and live delivery remain root-owned operational gates; this integration does not claim their completion.
