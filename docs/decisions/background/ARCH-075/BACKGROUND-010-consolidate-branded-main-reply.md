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
status: complete
priority: 5
executor: codex
claimed_at: 2026-11-13T20:29:53Z
attempt: 1
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

Prerequisites integrated: BG009 source cb98d6b75da189a6408f7ccfec96a4368ba9baad/parentabfd2768d946b2a63e0d23d00338b85d7c34c3a2; approved public Shared5.13.10 exactarchive receipt accepted311ce54f4, source232bcb3a3e5a8385aa76fc50f1c59da34f323fb1 and parent3896421ac4b076d980df33895d45fb1021b3a50c. Both dependency tasks Complete. Use exactpublished5.13.10 and reader-first writerOFF gate.

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

### Two-phase reader/writer rollout gate

Common layout is already active; first boot of a new worker must NOT start writing new HEADER-only plans during overlap with old5.13.9 readers. Add one explicit Background-owned environment feature gate `RECOVERY_BRANDED_MAIN_REPLY_ENABLED`, absent/false means existing legacy composition byte-for-byte, only exact literal true enables new writer. Invalid values must never enable it (fail configuration or explicitly remain disabled with bounded diagnosis). Reads accept old/new plans regardless of writer flag. Test default/off/invalid preserve old plan bytes and true selects new layout. Root deploys PhaseA new readers with legacy writer OFF; verifies all old messaging workers stopped/drained with queue state preserved, then sets true and deploys PhaseB. PhaseA/B overlap is safe because every reader supports new order. No platform pause/drop of events, force replay or mutation of frozen jobs. Expose only safe enabled/disabled boolean through the existing worker-start semantic event or equivalent bounded read-only runtime proof, so root can verify PhaseA OFF and PhaseB ON without environment/secret dumps. Reuse shared structured logging; no competing generic logger or telemetry. Gateway002 owns matching Render declaration/operator rollout documentation; no Gateway edits by Background.

## Work Items

- [x] Inspect current source and capture awkward old decomposition regression.
- [x] Adopt published accepted Shared package and exact new composition/guard decomposition with legacy read preservation.
- [x] Prove short/long/logo/product boundaries, AI/human and real PG firstfreeze/retry/ordering/idempotency negatives.
- [x] Publish source/report and return review.

## Interfaces / Contracts

Published Shared RecoveryMultipartDeliveryPlan v1 additive HEADER-only; existing common reference/finalURL/media receipts and Background frozen source guard.

## Dependencies

ARCH-075-SHARED-006 accepted publication and ARCH-075-BACKGROUND-009 accepted/integrated before execution.

## Enables

Root rollout/drain and actual new human/AI/product delivery verification, no automatic follow-on.

## Acceptance Criteria

- [x] Short verified logo reply is one complete caption; selected product remains separate footer-only.
- [x] Over1024/noLogo uses complete TEXT main without adjacent empty framing; no answer/product loss or truncation.
- [x] Old frozen plans remain readable, new exact guards reject tamper/foreign/duplicate content, physical footers and logical billing/idempotency unchanged.
- [x] Required tests/checks/isolation/publication evidence pass; no live mutation.

## Validation

- [x] Focused RED/GREEN AI/human defaultcomposition tests:1024/1025Unicode,4096limit,logo present/absent/invalid,product present/absent/unavailable,exact footer/no duplicated middle.
- [x] Frozen legacy/new shape digest/read vectors plus tamper/media/tenant/control/moderation/lease/dispatch negatives.
- [x] Disposable PG new root/ordered parts/retry/concurrency/one logical usage/no duplicate provider sends.
- [x] Relevant declared full tests/build/type/scoped lint and known unchanged baseline disclosure; exact dependency/registry pin,diff/privacy and launcher isolation/synchronization evidence.

## Stop Condition

Set review and publish exact source/report; no self-accept/main merge/live send or further capability.

## Implementation Notes

Normal launcher dedicated mirrored worktrees; you are not alone, preserve others/primary. Root owns merges/drain/live. Never modify approved common source to hide transport issue.

## Completion Report

### Status

Ready for Review. Source `56148f8e4ba1bd4578162a2564720c5de80aa995` pushed to mirrored `task/ARCH-075-BACKGROUND-010`; no main merge or live operation by executor.

### Files Changed

- `package.json`, `package-lock.json`: exact public Shared5.13.10 pin and registry integrity.
- `src/services/recovery-multipart/{composition,common-decomposition,preparation,frozen}.ts`: gated consolidated writer and one exact additive legacy/new decomposition reader.
- `src/workers/whatsapp.worker.ts`: existing semantic startup event safe boolean.
- Related composition/frozen/worker unit tests and `tests/integration/arch075-common-layout.integration.test.ts`.
- Three existing installed-Shared logger/startup tests: expected installed release updated5.13.9→5.13.10; behavioral/privacy assertions retained.

### Work Completed

Short verified logo main contains complete canonical header, authored answer and footer; verified product remains separate footer-only. Over1024/no valid logo uses complete TEXT main. Logical source/receipt/body stays unchanged. Old plans retain exact bodies/digests and remain readable independent of writer flag. Existing consent/moderation/leases/fences/ordering/ambiguity and one logical usage retained.

`brandedMainReplyEnabled()` enables new writes only for exact `RECOVERY_BRANDED_MAIN_REPLY_ENABLED=true`; absent/false/invalid remains legacy. `whatsapp.worker.started.data.recoveryBrandedMainReplyEnabled` is boolean only. No secrets/environment dumps.

Entrypoint audit: production `src/entrypoints/messaging.ts` alone starts multipart repair plus WhatsApp status/continuation worker and HUMAN dispatcher. Legacy combined `src/index.ts` also starts WhatsApp worker/HUMAN dispatcher and can read/write plans if deployed. No other dedicated entrypoint starts these consumers. Root must inventory every affected instance including any combined process, deploy PhaseA OFF, prove all old readers stopped/drained without changing queued work, then enable PhaseB. No activation performed here.

### Validation Results

- Exact unchanged composition baseline RED:7 failures/5passes,8filtered skips, proving true flag was ignored by old writer. New focused GREEN124tests/8files including AI/HUMAN,1024/1025Unicode,4096TEXT, flag defaults/invalids, old/new reader, safe startup bool. Final full suite includes final additional unavailable-product test.
- Declared full `vitest run`:391files passed/1configured skipped;4315tests passed/10configured skipped,227.56s. No failures. Skips are existing environment-gated suites, not substituted for disposable PG.
- Real disposable PostgreSQL/Redis runner:3suites71PASS/0skip,274.61s, including new enabled AI short/long verified-product cases; separate DEFAULT HUMAN consolidated production adapter root/replay/concurrent claim vector1PASS/36name-filter skips,26.91s. Total72actual PG tests pass. Existing suite also exercises stale control/source, expiry, moderation, tampering and provider ambiguity guards. One logical AI usage, zero HUMAN automated usage and no duplicate sends asserted.
- Build PASS: Prisma6.19.3 generate, both TypeScript compilers and Meta sample packaging. Initial discriminant typing failure fixed using explicit HEADER/ANSWER branches before final build.
- Scoped ESLint all12changed TS/test files PASS; `git diff --check` PASS.
- Full ESLint retains exactly4 unchanged `@typescript-eslint/no-unused-vars` baseline errors: candidate-index.store.ts:9 readRecoveryExecutionPolicy; recovery-offer-resolver.service.ts:23–25 MAX_CANDIDATES/VERIFICATION_TIMEOUT_MS/AI_TIMEOUT_MS. Exact unchanged cb98d6b HEAD source via stdin reproduces all4; current diff empty in both. No full-lint-green claim.
- Initial full test run2failures were obsolete5.13.9 version literals; updated3 release assertions and reran complete final suite successfully. Initial unit fixture issues (empty authored answer / HUMAN with AI-only commerce payload) corrected without relaxing runtime checks.
- Protected local logs `local-backups/arch075-live-20261113/bg010-{red,focused-final,full-final,postgres,postgres-human,build-final,lint-final,full-lint,baseline-candidate,baseline-offer}.log`; no private live fixture committed.

### Isolation / Publication Evidence

Launcher prepared packet `bg010-prepared.json`: canonical primary workspace, exact dedicated parent/implementation paths, mirrored branch; dependency gate passed Shared006/BG009Complete; attempt1codex at2026-11-13T20:29:53Z; pushed claim `e9d4f0f75720bf857b7a7eb2984cb99eca9b9804`. Parent synchronized f08e7c192; implementation synchronized cb98d6b75da189a6408f7ccfec96a4368ba9baad; recursive database6f42b71112efe7ac63654d55f41cd74ca569b1ae exact ready. No sibling/primary edits or unmerged gitlink staged. Shared installed from registry.npmjs.org exact5.13.10 integrity `sha512-PjuTCfTQxb0JIA7LfWIJJjOmmFsjxhB+C+tNdSawUu+uun9VWPEOqn5tRaLeRs55u29JuKmllN2/75kQ1dWs0A==`.

### Deviations

No feature scope deviation. Existing service4096UTF16 input admission remains unchanged; Unicode caption boundaries1024/1025 use supplementary emoji,4096TEXT test uses ASCII. No Shared implementation/publication, migration, Meta registration/source mutation, main merge or live send.

### Assumptions / Unresolved Issues

Root owns independent review, merge, all-reader deployment inventory/drain, flag activation and real production recipient/provider verification. These remain operational follow-through and are not claimed by this report.

### Architectural Concerns

Do not enable writer until every old reader is gone. New readers accept old and new plans regardless of flag; root can safely overlap PhaseA and PhaseB after reader upgrade.

## Architect Review

### Review Status

Accepted

### Review Notes

Independent exact source `56148f8e4ba1bd4578162a2564720c5de80aa995` and report `297e4c278a95e84b9ffee90ac061a8263f633063` reviewed. Complete short branded main caption, separate footer-only product and complete long/noLogo TEXT fallback preserve logical content. One exact legacy/new decomposition reader is shared within Background preparation/frozen guards. No findings.

### Reviewed Files

All production composition/decomposition/preparation/frozen/startup and exact published dependency deltas; relevant default HUMAN/AI unit/PG vectors and version-only assertions. Reviewed launcher isolation/synchronization/recursive evidence and actual entrypoint inventory.

### Validation Reviewed

RED7 baseline failures; focused124 and full4315pass/10existing configured skips;72actual disposablePG tests including defaultHUMAN enabled→OFFreplay/concurrentclaim, AIshort/long/product/ordering/usage and negative guards. Build/scoped12filelint/diff passed; four unrelated full-lint findings reproduced unchangedcb98 baseline. Exact registry5.13.10integrity verified; no redundant rerun. Root must verify exact CI before merge.

### Architecture Conformance

Existing Sharedv1 additive order consumed from published package; no schema/role/source mutation. Exacttrue writer flag defaultsOFF and preserves legacy plans; readers accept old/new independent of flag. Safe existingworkerstartup boolean exposes rollout state without secrets. Fullcaption1024 and TEXT4096 existing constraints retained; no answer/product substitution, truncation or divider heuristics. Tenant/media/receipt/dispatch/control/moderation/idempotency/logicalbilling guards unchanged.

### Follow-up

Root CI/source/parent integration and Gateway002 declaration required. PhaseA compatible readers/legacywriterOFF across all messaging or deployed combined instances; verify oldreaders drained with jobs preserved before PhaseBtrue. Newplans may not reach oldreader. Actual shortlogo/body/footer/product and human/AI delivery proof remains root-owned; ARCH075 stays InProgress.

## Developer Integration

Root verified both GitHub unit-test checks passed for exact reviewed source `56148f8e4ba1bd4578162a2564720c5de80aa995` and merged Background PR221. Actual main merge is `1b71a7d3582f6f946939ac669a9308f1a0c66b01`; the workspace pin records that merge. Shared5.13.10 is already publicly published and verified. Gateway002 and the reader-first PhaseA/PhaseB rollout remain operational follow-through; this integration does not claim live activation or recipient delivery.
