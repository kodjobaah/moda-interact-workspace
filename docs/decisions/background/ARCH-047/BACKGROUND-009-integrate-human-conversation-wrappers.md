---
id: ARCH-047-BACKGROUND-009
architecture_id: ARCH-047
title: Integrate prepared wrappers into human conversation replies
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-047-BACKGROUND-005
  - ARCH-040-DATABASE-007
enables: []
created: 2026-10-24
updated: 2026-10-26
---

# Integrate prepared wrappers into human conversation replies

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

This is a **portable task definition** prepared from the 24 October 2026 workspace snapshot and consolidated DB001 Attempt 7 contract. It is not a repository implementation, task claim or evidence of a created worktree/branch. No new ARCH-047 Shared package is assumed. The parent architecture and `BACKGROUND-001` require reconciliation to the final Admin-owned AST/compilation and DB-backed keyed-segment translation decisions before dependent work is promoted.

## Objective

Apply BG005 to merchant-authored in-window HUMAN_TEXT commands using an **immutable, once-prepared customer-visible body**. Preserve the accepted raw text as merchant intent, but make the frozen **wrapped** body the one moderated, persisted in `ConversationMessage.content`, and sent to WhatsApp. Do not re-render on retries or bypass the post-window BG007 route.

## Context

ARCH-047 permits only immutable, Moda Admin-authored template definitions. Admin validates and compiles the AST and persists already-prepared transport/runtime data. Background handles independently testable execution modules and **never re-parses the Admin authoring AST**. The DB001 schema provides translation runs/items/batches, compiled Meta registrations, publication targets and wrapper pointers. Messaging delivers Meta template status observations through the existing BullMQ path; Background persists/assesses them. Existing outbound admission remains authoritative.

## Scope

- Wire BG005 only into the existing **in-window free-text** branch of the merchant human command path (`recovery-conversation/human-command-dispatcher.service.ts`, related command/message record) after authorisation and before final content moderation.
- Preserve exactly the merchant-authored response inside prepared SHARED/HUMAN wrapper and store/send the same complete customer-visible content. Use existing tenant, recovery, human-takeover and provider send code.

## Out of Scope

- No post-window Meta follow-up branch work (BG007), no new Quick Reply/canned response authoring, no UI redesign, no staff roles or per-conversation assignment, no AST compilation, template Meta status work or checkout mutations.
- No relaxed moderation or customer-service-window checks because a template wrapper is internally published.

## Requirements

**ARCHITECT DECISION — durable prepared-content prerequisite (2026-10-26; satisfied).** At the time of the original decision, the existing implementation worktree contained only a preparation seam, so it was not safe to connect directly to WhatsApp while `MerchantConversationSendCommand.textBody` remained the SQL-validated moderation/send source. `ARCH-040-DATABASE-007` is now Complete and adds nullable `preparedTextBody`, `preparedWrapperEvidence` and `preparedAt`, extends the set-once command guard, and makes `HUMAN_COMMAND`/`TEXT` moderation use the frozen body. Both explicit BG009 dependencies are Complete. The historical Attempt 1 readiness and first-action instructions below are superseded: the canonical Attempt 2 claim is recorded at the end of this report, and the Background `database/` submodule is synchronized to Database `origin/main` at `7cd7e955c8ede2ce76631ee40c655daba91bfdd6`, followed by successful Prisma generation and build.

**R0 — Exact durable preparation and full-message admission.** Under the current `HUMAN_TEXT` command lease, before any HUMAN moderation assessment, call the existing BG005 wrapper through `HumanWrapperPreparationService` (or an equivalent small module). `not-applicable` must be limited to the separate post-window command kind. `prepared` freezes its exact body plus the BG005 wrapper definition/locale/audience/slot-edit-version/applicationKey and body digest. `passthrough` freezes the original text with explicit no-wrapper evidence. `refused` or unexpected errors **never** send raw text as a fallback. Atomically freeze the body, provenance and timestamp with a conditional DB `UPDATE ... WHERE state='CLAIMED' AND leaseToken=:token AND leaseExpiresAt>statement_timestamp() AND providerDispatchKey IS NULL AND preparedTextBody IS NULL RETURNING ...`. A stale lease or zero-row update must fail/re-read, never overwrite. If already frozen, reuse the identical bytes and provenance without calling the renderer again. Do not change `textBody` or `payloadSha256`.

**R0a — Moderation/final-send identity.** Modify `ModerationAssessmentService`'s HUMAN_COMMAND/HUMAN_TEXT canonical reader to return only persisted `preparedTextBody` and fail closed if it is absent. Ensure moderation `effectiveText`, the INSERT guard digest, `requireCurrentAllowance`, final SQL admission and the persisted outbound `ConversationMessage.content` all use precisely the frozen prepared UTF-8 body. Immediately before the provider permit, re-check current wrapper slot/definition validity against frozen evidence and refuse if the selected wrapper has changed or been retired; a changed slot must not trigger an in-place re-render. At final send, use the **committed admitted `ConversationMessage.content`** (or an exactly equivalent frozen read backed by that message) rather than `command.textBody`. If the committed content or moderation digest cannot be proven identical, do not call Meta. After a provider permit, preserve existing UNKNOWN/reconciliation rules; no second send/retry may be authorised by a mismatch.

**R0b — Strict isolation.** All changes above apply only to `HUMAN_TEXT` inside the verified open customer-service window. Post-window `RECOVERY_FOLLOW_UP_TEMPLATE` retains the existing TEMPLATE_PARAMETERS moderation input, BG007 preparation, sequence-2 credit and Meta template send. The wrapper has no authority to relax consent, STOP, HUMAN control, tenant ownership, the window or billing. Keep logs free of raw message content and checkout URLs.

**R1 — Intent and content.** For a human-authored ordinary response within the valid rolling WhatsApp 24-hour service window, resolve SHARED/HUMAN wrapper through BG005 and insert the submitted merchant text unchanged. Checkout URL and shop name come from read-only verified conversation context; never use a customer-supplied arbitrary URL as the trusted basket URL.

**R2 — Final message consistency.** Moderate the complete **frozen `preparedTextBody`** (including header/footer) independently. The SQL guard must validate SHA-256 of that body; `OutboundSendFenceService` must insert that body as `ConversationMessage.content`, and the provider request must send the exact admitted content. Do not moderate only `command.textBody` and then append unmoderated material. Preserve the original merchant text and accepted-request idempotency unchanged. Merchant previews in Shopify/Woo should use identical prepared-wrapper semantics under their separate owning tasks; do not create UI from Background.

**R3 — Admission invariants.** Reuse current merchant authentication, tenant scoping, HUMAN control, the 24-hour window, consent/STOP, support moderation, provider compensation/idempotency and billing policy. Existing merchant-authored replies within the window are not subjected to AI-exchange caps. No additional paid follow-up is created by wrapper rendering.

**R4 — Retry/error.** `preparedTextBody` and evidence are immutable after first freeze. Worker restarts, deferred moderation, lease reclaims and replay reuse those exact bytes even if Admin activates a different wrapper. If checkout context, prepared projection or length is invalid, refuse rather than silently sending raw text; only explicit `NOT_CONFIGURED` permits frozen passthrough through the **same** moderation/admission path. A stale/outdated wrapper at final admission suppresses sending; do not silently rewrite a frozen message.

**R5 — Separation.** Post-window commands must continue to the Meta recovery-template path (BG007), never use a free-form conversation wrapper in place of an approved template.

**R6 — One human in-window path; no obsolete bypass.** Replace any separate in-window direct raw-text dispatch that would evade BG005 and full-message moderation, while retaining a no-wrapper case through the *same* final admission path. Remove dead local wrapper/formatting helpers and superseded tests after a reference audit, not by deleting the original human-control, service-window or moderation protections. BG007 separately owns the post-window template branch; both tasks touch `human-command-dispatcher.service.ts`, so require explicit final-branch reconciliation before acceptance.

## Work Items

- [x] Before any Background source edits, update the canonical `database/` submodule to the developer-merged Database `main` containing accepted `ARCH-040-DATABASE-007`, regenerate the Prisma client, and validate the generated schema; retain BG009's existing preparation-only files and attempt history. Do not point the submodule at an unmerged Database task-branch commit.
- [x] Add a focused lease-protected prepared-content repository/seam; freeze full text and bounded wrapper evidence atomically once, read frozen content on replay, no direct `textBody` rewrite.
- [x] Make HUMAN_TEXT moderation canonical/effective text use `preparedTextBody`; preserve TEMPLATE_PARAMETERS behaviour for BG007.
- [x] Make `OutboundSendFenceService` persist `preparedTextBody` as the admitted `ConversationMessage.content` and bind approval to the exact digest/current policy; deliver the committed admitted message bytes through the existing provider path.
- [x] Recheck frozen wrapper activation before admission, and fail closed if stale; no re-render or second permit after admission.
- [x] Remove only obsolete HUMAN_TEXT raw-send/formatting branches after an import/reference audit; preserve BG007 post-window logic and all ARCH-040 security/follow-up safeguards.
- [x] Add focused PostgreSQL integration, lease/replay, moderation denial, no-wrapper, wrapper-change and provider-text equality tests; run required repository validation and record it in Completion Report. The formerly missing raw-digest and crash/reclaim/eligibility cases now pass as part of the 28/28 integration run; formal review workflow remains outstanding.

- [x] Wire BG005 only into the existing **in-window free-text** branch of the merchant human command path (`recovery-conversation/human-command-dispatcher.service.ts`, related command/message record) after authorisation and before final content moderation.
- [x] Preserve exactly the merchant-authored response inside prepared SHARED/HUMAN wrapper and store/send the same complete customer-visible content. Use existing tenant, recovery, human-takeover and provider send code.
- [x] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [ ] Complete all required repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report. The two named PostgreSQL gaps are closed; the final post-correction branch/worktree checks, remote push and next claim remain to be reconciled before formal review submission.

## Interfaces / Contracts

**New mandatory dependency:** `ARCH-040-DATABASE-007` — nullable, set-once `MerchantConversationSendCommand.preparedTextBody`, `preparedWrapperEvidence`, `preparedAt`; database HUMAN_COMMAND/TEXT digest against `SHA256(UTF8(preparedTextBody))`. The new fields and guard are authored in Database, not here.

**BG009 application-owned prepared evidence:** JSONB includes `schemaVersion:1`, either `outcome:'RENDERED'` with `wrapperDefinitionId`, `localeId`, `audience`, `slotEditVersion`, `applicationKey`, `bodySha256`, or `outcome:'PASSTHROUGH'` with `reason:'NOT_CONFIGURED'` and `bodySha256`. No customer text or full AST is duplicated in evidence; Database does not enforce its semantic fields.

**Execution equality:** `command.textBody` = original intent; `command.preparedTextBody` = complete moderated text; `ConversationModerationAssessment.contentSha256` = SHA-256 of the prepared body; `ConversationMessage.content` = approved prepared body; the actual `sendWhatsAppText` payload = committed message content. Require equality under tests. The post-window template path remains keyed to `arch040_moderation_template_input_v1` and Meta approved template parameters.

**Consumes** BG005 wrapper `renderConversationResponse(source:'HUMAN')`, existing `MerchantSendCommandService`, `HumanCommandDispatcherService` and moderation/admission services. No Shared AST. UI preview endpoints remain owned by Shopify/Woo/API; this task exposes only its established prepared render result to the existing command path.

## Dependencies

- `ARCH-047-BACKGROUND-005` (Complete)
- `ARCH-040-DATABASE-007` (Complete; its merged Database `main` schema/client must be synchronized before Background source edits)


**Important:** Tasks are not Ready merely because their files exist. Confirm each dependency has `status: complete` (not only Passing tests / Accepted review) before claiming. DB001 is developer-owned and may remain in progress pending explicit completion. Dependencies outside this task must be resolved by their owners; do not implement across repositories.

## Enables

None in this nine-task Background set.

## Acceptance Criteria

- [x] Database prerequisite complete; original `textBody`/`payloadSha256` unchanged by wrapping, prepared body and evidence frozen atomically once under current claim.
- [x] Complete wrapped body (or explicit no-wrapper passthrough) is identical across HUMAN_TEXT moderation input/digest, final-admission `ConversationMessage.content` and actual provider-send text; wrapper-only forbidden content is moderated before any provider permit.
- [ ] SQL rejects raw-body moderation digest when it differs from the frozen body; stale/absent prepared body, invalid lease, replay mutation and current wrapper change cannot reach provider dispatch.
- [ ] Concurrent claim, retry after worker crash, change of published wrapper, `STOP`/control/window loss and existing UNKNOWN/provider compensation covered by actual PostgreSQL-integrated tests.
- [ ] `RECOVERY_FOLLOW_UP_TEMPLATE` retains original template-parameter moderation, BG007 sequence-two and billing semantics; no new human free-text route is reachable after window close.
- [ ] Only orphaned raw HUMAN_TEXT branches/tests are removed; existing final admission security invariants and BG007 integration remain intact.

- [ ] Human in-window reply retains verbatim merchant text with deterministic wrapper; HUMAN override/SHARED fallback and valid checkout URL tested.
- [x] Wrapper-only forbidden content blocked by full-message moderation; durable message/provider payload equality verified.
- [ ] 24-hour expiry prevents unapproved free text; post-window sequence two untouched; STOP, consent, tenant scope and HUMAN ownership preserved.
- [ ] Retry/replay, template activation change and double-wrap refusal; no AI cap applied to eligible merchant text.
- [x] Existing human command/compensation regressions plus focused integration/build and `git diff --check`; the complete moderation unit suite has one unrelated failure documented below.
- [ ] No source/template authoring, shopper checkout mutation, Meta edit-existing-template call, externally authored Meta template adoption, or bypass of existing WhatsApp final-send safeguards is introduced.
- [ ] Task implementation is modular, separately testable, and stays within `moda-interact-background/`; externally owned gaps are reported, not silently implemented.

- [ ] Old human raw-text bypass/duplicated formatting path is absent; unwrapped fallback (if no wrapper is published) uses the same full-message moderation and final-send logic. BG007's post-window processing remains isolated and compatible.

## Validation

- [x] Fresh/upgrade PostgreSQL schema guard evidence is supplied by accepted `ARCH-040-DATABASE-007`; BG009 PostgreSQL integration passed for frozen preparation, moderation INSERT digest, final-send message content and provider-send equality. The previously missing negative INSERT of the original raw-body digest is now covered in `arch047-human-prepared-reclaim.integration.test.ts` (passing in the 28/28 run).
- [ ] Regression tests: valid wrapper, passthrough, missing/invalid wrapper refusal, wrapper-only moderation denial, malformed evidence, blocked moderation, concurrent/reclaimed claims, retry/restart, stale wrapper activation, window/STOP/control loss, and BG007 template command untouched.
- [ ] Audit all production callers of `command.textBody` and remove/redirect the obsolete HUMAN_TEXT sender path; inspect no stale direct sender remains before review.
- [x] Run the focused new tests and relevant existing regression suites identified above; exact executable commands and outcomes are recorded in the current developer update below.
- [x] Run the repository-declared build/typecheck (for this snapshot: `npm run build`) and focused ESLint where applicable; do not assume every repository has identical scripts.
- [x] `git diff --check`, inspect changed-file scope and capture task-isolated start-of-attempt and mirrored-branch evidence.
- [x] When integration depends on a real PostgreSQL/BullMQ service, run the repository's declared integration harness or record the missing environment explicitly; do not claim an unrun test passed.

## Stop Condition

After finishing Work Items, Acceptance Criteria and Validation, fill the Completion Report, change task status to `review`, return both the implementation and parent task-branch evidence to `moda_architect`, and **STOP**. Do not start any enabled/adjacent task or update `docs/decisions/**/_index.md`.

## Implementation Notes

Keep merchant-facing display parity explicit in handoff to Shopify/Woo tasks, but do not modify those repositories. A preview must never be the security authority at send time: Background re-resolves current wrapper and session eligibility.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-009`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.



## Completion Report

### Status

**Correction evidence ready for formal handoff; task remains `ready` at Attempt 2.** The two PostgreSQL acceptance cases identified by the Attempt 2 developer self-review now pass (5 integration files, 28/28 tests). The additional tests were committed locally as `7b135b1` **after** the task returned to `ready`, but the supplied terminal recording does not show a push or a canonical Attempt 3 claim. This evidence update does not change `status`, `attempt`, `executor`, `claimed_at`, or the previous Architect Review. Claim/publication reconciliation and authorised movement to `review` are still required; developer completion has not been decided.

**Prior Attempt 2 self-review (historical):** Implementation commit `ab55ed9a9d9de3aaf6791933db2574ed49a86f36` was pushed to `origin/task/ARCH-047-BACKGROUND-009` before the formal Attempt 2 claim and remains explicitly disclosed. The review returned the task to `ready` for two missing PostgreSQL proofs; that history is preserved below.

**Historical Attempt 1 status (superseded as implementation progress, retained for audit):**

**Ready for developer Attempt 2 — dependency frontier reconciled 2026-10-26.** The original Attempt 1 claim at `2026-10-26T07:24:51Z` and its preparation-only source remain historical evidence; task YAML is now `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1`. Both explicit dependencies (`ARCH-047-BACKGROUND-005` and `ARCH-040-DATABASE-007`) resolve Complete. The next developer claim increments to Attempt 2. Its first required action is to synchronize `database/` to Database `main` after the developer merges DATABASE-007 there, regenerate Prisma Client, and validate before editing Background source. This readiness transition is not implementation acceptance or a new claim.

### Files Changed

**Additional acceptance-test correction committed locally at `7b135b1` (remote push not evidenced):**

- `moda-interact-background/tests/integration/arch047-human-prepared-reclaim.integration.test.ts` — new: PostgreSQL raw-digest rejection; crash/lease reclaim with STOP and HUMAN-control-loss cases.
- `moda-interact-background/tests/integration/fixtures/recovery-human-dispatch.fixture.ts` — updated: recipient fixture option needed for the STOP scenario.

The terminal records `2 files changed, 190 insertions(+), 2 deletions(-)` for this local commit. It records an untracked `typescript` terminal capture; that file is not part of the implementation commit.

**Attempt 2 implementation, from developer `git status` and commit `ab55ed9`:**

- `moda-interact-background/database/` — synchronized canonical Database submodule (accepted prepared-command fields are present in the uploaded schema).
- `moda-interact-background/src/services/conversation-moderation/moderation-assessment.service.ts`
- `moda-interact-background/src/services/recovery-conversation/human-command-dispatcher.service.ts`
- `moda-interact-background/src/services/recovery-conversation/human-prepared-command.service.ts` (new)
- `moda-interact-background/src/services/recovery-conversation/human-wrapper-preparation.service.ts` (new)
- `moda-interact-background/src/services/recovery-conversation/outbound-send-fence.service.ts`
- `moda-interact-background/tests/integration/arch047-human-prepared-send.integration.test.ts` (new)
- `moda-interact-background/tests/integration/fixtures/recovery-human-dispatch.fixture.ts`
- `moda-interact-background/tests/integration/recovery-human-dispatch.integration.test.ts`
- `moda-interact-background/tests/integration/recovery-human-provider-recovery.integration.test.ts`
- `moda-interact-background/tests/unit/services/recovery-conversation/human-prepared-command.test.ts` (new)
- `moda-interact-background/tests/unit/services/recovery-conversation/human-synchronous-rejection.test.ts`
- `moda-interact-background/tests/unit/services/recovery-conversation/human-wrapper-preparation.test.ts` (new)

The uploaded archive is an overlay of parent and implementation worktrees. These paths are the implementation-repository changes reported at commit time, not a claim that the parent task file or implementation `main` was pushed. No `_index.md` files are changed by this review-evidence patch.

**Historical Attempt 1 file list:**

Preparation-only source present in the supplied BG009 implementation worktree:

- `moda-interact-background/src/services/recovery-conversation/human-wrapper-preparation.service.ts` (new).
- `moda-interact-background/tests/unit/services/recovery-conversation/human-wrapper-preparation.test.ts` (new; execution not evidenced).

This handoff patch changes only `docs/decisions/background/ARCH-047/BACKGROUND-009-integrate-human-conversation-wrappers.md`. The uploaded archive does not establish whether the implementation files have been committed or pushed.

### Work Completed

**Post-self-review correction evidence (local commit `7b135b1`):**

- Added an actual PostgreSQL `ConversationModerationAssessment` INSERT rejection test for a raw merchant-text SHA-256 digest when a different full wrapped `preparedTextBody` has been frozen; the same scenario verifies that the correct frozen-body digest is accepted.
- Added real PostgreSQL lease expiry and a different worker's reclaim. The frozen body, wrapper evidence and preparation timestamp are verified unchanged, a second render is refused, and the old lease cannot be used.
- Verified a committed local STOP **or** HUMAN-control revision loss after reclaim blocks final admission and prevents both free-text and template provider calls while preserving the original frozen evidence.
- These are tests and a fixture update only; no production send/moderation code was changed by commit `7b135b1`.

**Attempt 2:**

- Reused the accepted `ARCH-040-DATABASE-007` schema (`preparedTextBody`, `preparedWrapperEvidence`, `preparedAt`) via the canonical Background database submodule; Prisma Client generation succeeds.
- Added lease-fenced, set-once PostgreSQL prepared-content freezing, immutable wrapper provenance/body digest and frozen replay. Original merchant intent (`textBody` and accepted payload identity) remains separate.
- Connected BG005 preparation only to HUMAN_TEXT in-window dispatch, with an explicit `NOT_CONFIGURED` passthrough using the same moderation/admission path; no raw fallback after refusal.
- Switched HUMAN_COMMAND/TEXT moderation canonical content, final SQL admission, `ConversationMessage.content` and provider text to the frozen complete body. Stale wrapper assignment suppresses the final send without re-rendering.
- Preserved the distinct BG007 post-window template branch and existing control/window, billing, unknown-provider and compensation mechanisms.
- Added/updated unit and real PostgreSQL integration fixtures. The latest correction records sender-preflight and provider-dispatch exceptions through `@modainteract/moda-interact-shared/logging` using bounded metadata; expected uncertain outcomes stay in durable reconciliation instead of blindly retrying WhatsApp.

**Historical Attempt 1 work (preparation only):**

- Added a preparation-only seam over BG005's `renderConversationResponse(source: 'HUMAN')`, using the accepted command ID as stable rendering identity and the original merchant text as input.
- The preparer distinguishes rendered, explicitly unconfigured passthrough, refusal, and non-applicable post-window commands. It does **not** grant moderation approval or provider-send permission.
- Added unit-test source for identity and exact merchant text, passthrough/refusal behaviour, exclusion of the post-window command kind, and shared-logger exception propagation. The tests have **not** been shown to execute in the supplied terminal log.
- Deliberately **did not** connect prepared text to `HumanCommandDispatcherService`, the moderation assessment service, `OutboundSendFenceService`, or the WhatsApp provider. These would currently disagree on the authoritative content.

### Validation Results

**Post-self-review correction recording `typescript(20261026-204952)` (26 October 2026):**

- `npm run test:integration -- tests/integration/arch047-human-prepared-reclaim.integration.test.ts tests/integration/arch047-human-prepared-send.integration.test.ts tests/integration/recovery-human-dispatch.integration.test.ts tests/integration/conversation-moderation.integration.test.ts tests/integration/recovery-human-provider-recovery.integration.test.ts` — **PASS, 5/5 files, 28/28 tests** against the repository's disposable PostgreSQL integration runner. Three tests in `arch047-human-prepared-reclaim.integration.test.ts` directly close the two explicit acceptance-evidence gaps from the prior self-review. The 28-test total includes the existing regression tests; it is not 28 additional tests.
- `npm run build` — **PASS**, generating Prisma Client 6.19.3 and compiling TypeScript without a reported error.
- The focused `npx eslint tests/integration/arch047-human-prepared-reclaim.integration.test.ts tests/integration/fixtures/recovery-human-dispatch.fixture.ts` command appears in the terminal sequence with no reported diagnostics; the recording does not separately print an ESLint exit code. An earlier focused ESLint run over the prior implementation was independently recorded as passing.
- The terminal shows local commit **`7b135b1`** (`feat(background-009)`, 2 test/fixture files) and `git status` showing the branch **one commit ahead** of `origin/task/ARCH-047-BACKGROUND-009`. **No successful `git push` of `7b135b1` is evidenced** by this recording. The `typescript` capture remained untracked and must not be included in the code commit.
- This latest log does **not** separately show `git diff --check`; the earlier implementation report records `git diff --check origin/main...HEAD` passing before `7b135b1`. Whitespace of this documentation-only patch has been verified separately. The developer must capture final post-correction Git/worktree evidence when formally submitting.

**Attempt 2 developer terminal recording `typescript(20261026-154602)` (26 October 2026):**

- `npm run test:integration -- tests/integration/arch047-human-prepared-send.integration.test.ts tests/integration/recovery-human-dispatch.integration.test.ts tests/integration/conversation-moderation.integration.test.ts tests/integration/recovery-human-provider-recovery.integration.test.ts` — **PASS, 4/4 files, 25/25 tests**, using the repository's disposable integration runner. Covers durable frozen-body moderation and delivery, passthrough, wrapper-only moderation BLOCK, changed-slot suppression, command concurrency, customer-window expiry and provider UNKNOWN/compensation regressions.
- `npx eslint src/services/recovery-conversation/human-prepared-command.service.ts src/services/recovery-conversation/human-command-dispatcher.service.ts src/services/recovery-conversation/outbound-send-fence.service.ts src/services/conversation-moderation/moderation-assessment.service.ts tests/integration/fixtures/recovery-human-dispatch.fixture.ts tests/integration/recovery-human-dispatch.integration.test.ts tests/integration/recovery-human-provider-recovery.integration.test.ts tests/integration/arch047-human-prepared-send.integration.test.ts` — completed without errors in the recording.
- `npm run build` — **PASS** (`prisma generate` version 6.19.3 and TypeScript compilation without errors).
- Developer `git add database src tests`, commit **`ab55ed9`** (`feat(arch-047-background-009)`), and push to **`origin/task/ARCH-047-BACKGROUND-009`** — recorded successful. The `typescript` terminal recording remained untracked and was not included in the `git add database src tests` command.
- Workspace compressor reported a separate parent task worktree and implementation task worktree. That diagnostic is not a substitute for canonical launcher start-of-attempt synchronization/physical isolation evidence.

**Not evidenced by the historical implementation terminal recording:** a fresh standalone focused unit-test run, implementation `git diff --check`, durable Attempt 2 claim, parent report branch publication, or a final call-site/negative-test matrix audit. The current developer update below addresses the checks that can be established and records remaining coverage gaps without treating unrun cases as passing.

**Current developer update validation (2026-10-26):**

- `npm run test:integration -- tests/integration/arch047-human-prepared-send.integration.test.ts tests/integration/recovery-human-dispatch.integration.test.ts tests/integration/conversation-moderation.integration.test.ts tests/integration/recovery-human-provider-recovery.integration.test.ts` — **PASS, 4/4 files, 25/25 tests**.
- `npx vitest run tests/unit/services/recovery-conversation/human-prepared-command.test.ts tests/unit/services/recovery-conversation/human-wrapper-preparation.test.ts tests/unit/services/recovery-conversation/human-synchronous-rejection.test.ts` — **PASS, 3/3 files, 17/17 tests**.
- `npm run test:arch040-background-runtime:postgres` — **PASS, 2/2 files, 9/9 tests**, including dispatcher replica concurrency, HUMAN_TEXT window expiry, and follow-up claim races.
- `npm run test:arch040-recovery-conversation` — **PASS, 11/11 files, 81/81 tests**.
- `npm run test:arch040-moderation:postgres` — **PASS, 1/1 file, 10/10 tests**.
- `npm run test:integration -- tests/integration/recovery-human-follow-up-billing.integration.test.ts tests/integration/recovery-human-follow-up-cancellation-races.integration.test.ts tests/integration/recovery-follow-up-purchased-release.integration.test.ts tests/integration/recovery-human-provider-status.integration.test.ts` — **PASS, 4/4 files, 15/15 tests**, covering BG007 follow-up billing, cancellation, purchase release, and provider-status recovery.
- `npx vitest run tests/unit/services/conversation-moderation -t "HUMAN|human|template input|prepared"` — **PASS, 1 test; 32 tests skipped by filter**.
- Focused `npx eslint` over all 11 changed production/integration/unit files — **PASS**, no diagnostics.
- `npm run build` — **PASS**, Prisma Client 6.19.3 generation and TypeScript compilation.
- `git diff --check origin/main...HEAD` — **PASS**. Implementation worktree is clean at `ab55ed9a9d9de3aaf6791933db2574ed49a86f36`, equal to `origin/task/ARCH-047-BACKGROUND-009`; Database submodule is clean at `7cd7e955c8ede2ce76631ee40c655daba91bfdd6`, equal to Database `origin/main`.
- `npm run test:arch040-moderation` — **FAIL, 1 failed / 32 passed**. `tests/unit/services/conversation-moderation/automated-template-input.test.ts` expects serialization without `imageHeader: null` and `textHeader: null`, while the unchanged serializer now emits both. Neither file is changed by BG009; the focused moderation unit filter and PostgreSQL moderation suite pass. This out-of-scope failure was not modified.
- Production call-site audit: remaining `command.textBody` use in `human-command-evaluation.service.ts` is policy screening, not a provider sender. HUMAN_TEXT provider delivery uses the committed `permit.messageContent`; RECOVERY_FOLLOW_UP_TEMPLATE remains on the separate `sendWhatsAppTemplate` branch. The Database migration requires frozen HUMAN_TEXT content and validates the moderation digest against `preparedTextBody`.

The two explicitly identified PostgreSQL acceptance-evidence gaps from the Attempt 2 self-review are now **closed by the 28/28 integration run**: raw-body-digest rejection and lease-reclaimed frozen-body reuse under STOP/HUMAN-control loss. The final review submission still requires a canonical next-attempt developer claim, confirmation that local commit `7b135b1` is pushed, and reconciliation of the remaining compound acceptance checklist and worktree evidence. The historical unrelated automated-template serialization unit failure remains disclosed; no out-of-scope serializer change was made.

**Historical Attempt 1 validation (retained):**

The uploaded `typescript(20261026-072937)` terminal recording shows:

- `npm run prisma:generate` — completed successfully (Prisma Client 6.19.3 generated).
- `git apply --check --whitespace=error-all` for the preparation patch — no error reported.
- `git apply --whitespace=error-all` — no error reported.
- `git diff --check` — no error reported.
- The archive was created by the task-worktree compressor using separate reported parent and implementation paths. This is **not** a substitute for launcher-resolved start-of-attempt synchronisation/branch evidence.

**Not evidenced or claimed passed:** focused Vitest, build/typecheck after the preparation patch, ESLint, PostgreSQL integration, moderation/final-send/provider equality, or an implementation commit/push. All corresponding task Validation and Acceptance Criteria remain unchecked.

### Deviations

**Post-self-review correction:** The two missing PostgreSQL proofs were supplied by tests committed locally as `7b135b1` after the task had already been returned to `ready`. No new claim is evidenced, and there is no push confirmation in the supplied log. This ordering must be disclosed in the next developer claim/Completion Report rather than presented as work performed under a claim already active. The unrelated automated-template serialization unit failure is still outside BG009 scope.

**Attempt 2 history:** No deliberate departure from the approved prepared-content architecture is reported. Commit `ab55ed9` predates the formal Attempt 2 claim and remains explicitly disclosed. At that time the task was returned to `ready` for the two previously unproven PostgreSQL cases (now covered by the correction above).

**Historical Attempt 1:** **Intentional preparation-only implementation.** The task's in-window dispatcher/moderation/final-send integration remains incomplete, because the currently installed durable command and moderation constraints do not permit the prepared wrapped body to become the canonical moderated and sent content. No insecure workaround or parallel raw-text send path was introduced.

### Assumptions

- Post-self-review correction evidence is sourced from the uploaded BG009 snapshot and terminal log dated 2026-10-26. Its 28/28 tests are observed; an updated remote tip, new developer claim and current fully clean task worktree are **not** established by that recording.
- Attempt 2 source and build use the accepted Database-main prepared-content schema; the implementation gitlink is verified at `7cd7e955c8ede2ce76631ee40c655daba91bfdd6`, equal to Database `origin/main`.
- The formal developer claim is durable in the parent task record. This update reconciles the claim and validation but does not accept completion or alter implementation source.

**Historical Attempt 1 assumptions:**

- The provided 26 October worktree snapshot is the inspected development baseline; schema and migration files in this archive do not by themselves prove deployment state.
- `ARCH-047-BACKGROUND-005` is recorded `complete` in the uploaded task definitions.
- The existing ARCH-040 tenant/control/window/STOP/final-send/moderation guards remain mandatory; BG007 retains the separately owned post-window Meta-template path.

### Unresolved Issues

**Current review-submission prerequisites (after PostgreSQL correction):**

- **Resolved:** The PostgreSQL raw-text moderation-digest rejection and crash/reclaim plus STOP/HUMAN-control-loss cases now pass in the 28/28 integration run. These are not outstanding implementation changes.
- **Not yet evidenced:** push of correction commit `7b135b1` to `origin/task/ARCH-047-BACKGROUND-009` and a properly claimed next developer attempt. The terminal showed one local commit ahead of origin. Reconcile these facts through the canonical developer workflow; do not invent a claim or change `status` to `review` from this evidence patch.
- **Final review:** Confirm worktree isolation/synchronization and `git diff --check` after the new commit, review any remaining composite acceptance/validation criteria, and record actual final branch/parent task commits. Previous BG007 post-window tests passed (15/15) and no BG007 production source was changed in the correction.
- **Unrelated failure:** The full moderation unit suite's unchanged automated-template serializer expectation differs from emitted nullable header fields. It remains documented as out-of-scope; do not fix it inside BG009 without evidence of a regression caused by this task.

**Historical Attempt 1 concerns (resolved by Database-007 and implemented in Attempt 2):**

**Historical Attempt 1 action plan, superseded by the Attempt 2 claim and implementation.** The immutable raw accepted command, canonical moderation identity, final-admission message construction, and provider send were required BG009 implementation work under R1/R2/R3/R6. The durable prepared-content contract is implemented and accepted by DATABASE-007.

- Before any Background source edit, DATABASE-007 must be available through the developer-merged Database `main`; then update the canonical `database/` submodule, regenerate Prisma Client, and validate the generated schema. Direct mutation of accepted `MerchantConversationSendCommand.textBody`, an unmoderated append, and in-memory/Redis-only prepared content remain unacceptable.
- BG007 also changes `human-command-dispatcher.service.ts`. Reconcile its final branch before BG009 acceptance; do not modify BG007's post-window flow within this task.
- Following the decision and prerequisite implementation, run the required unit, database integration, compensation/retry, and full-message/payload equality validations; capture branch/worktree/synchronisation evidence before formal review.

### Architectural Concerns

**Post-self-review update:** The PostgreSQL digest and lease-reclaim safety gaps are now demonstrated in the latest integration tests without modifying production send policy. No new architectural contract is requested. The remaining review concerns are formal claim/branch publication, final BG007 coexistence verification, and honest documentation of the unrelated full-moderation-unit failure.

**Attempt 2 history:** The previously escalated prepared-content architecture dependency was accepted as `ARCH-040-DATABASE-007` and implemented in the current BG009 source. The earlier review required the two now-closed PostgreSQL proof cases. Its developer-execution chronology remains part of the record.

**Historical Attempt 1 blocker (preserved for context, not a new decision request):**

**Evidence in the supplied repository:**

1. `database/prisma/migrations/20261017214500_arch040_remove_outreach_sequence_policy/migration.sql` enforces immutable accepted-command identity/payload, including `textBody`, through `whatsapp.arch040_command_guard()`.
2. `src/services/conversation-moderation/moderation-assessment.service.ts` resolves a HUMAN_TEXT command's canonical moderation content from `command.textBody`, and rejects a supplied `effectiveText` that differs (`moderation_content_identity_mismatch`).
3. `database/prisma/migrations/20261018092000_arch040_moderation_template_content_digest/migration.sql` enforces the HUMAN_COMMAND/TEXT moderation digest against the same command text in `whatsapp.arch040_moderation_subject_guard()`.
4. `src/services/recovery-conversation/outbound-send-fence.service.ts` constructs the admitted HUMAN_TEXT `ConversationMessage` from `command.textBody`; `src/services/recovery-conversation/human-command-dispatcher.service.ts` also sends `command.textBody` to WhatsApp. A prepared wrapper currently has no durable, authoritative pre-moderation handoff to either step.

**Architect decision requested:** Choose and document an architecture-owned contract (for example, an immutable, set-once prepared body plus provenance/digest on the command, **or an equivalent durable one-to-one prepared-message record**) satisfying all of the following:

- Preserve the original accepted merchant text, request payload identity, idempotency key, tenant/conversation/command relationship and audit history unchanged.
- Atomically freeze the complete customer-visible body and selected wrapper provenance under a valid command claim **before** moderation; retry/restart/replay must reuse that frozen body rather than re-render under a changed assignment.
- Make the frozen full body the canonical HUMAN_TEXT moderation subject, including database digest validation and existing ALLOW/BLOCK/REVIEW_REQUIRED, model/policy-version and fail-closed requirements. Do not reclassify HUMAN text as AGENT/AUTOMATION to bypass the guard.
- Bind final admission to the exact moderated digest, current tenant/HUMAN control/24-hour window/STOP/consent and wrapper-publication policy, then persist `ConversationMessage.content` from that same frozen body. The provider-send payload must equal the durably admitted message. Decide explicitly what happens when the wrapper assignment changes after freezing but before admission (suppress/reprepare under a safe revision contract, never silently change admitted text).
- Preserve one-way provider permits, existing UNKNOWN/compensation/idempotency handling, and the separate BG007 post-window template/billing behaviour.
- Require PostgreSQL integration coverage for uniqueness, concurrent leases, restart/replay, mid-flight control or wrapper changes, wrapper-only moderation denial, stale moderation, and exact moderated/persisted/provider-text equality. Preserve structured error reporting through `@modainteract/moda-interact-shared/logging` without swallowing unexpected failures.

**Ownership and sequencing decision requested:** `moda_architect` to approve a `moda_database` prerequisite and any necessary cross-repository contracts, update the ARCH-047 execution graph/task dependencies, and then return BG009 to its existing developer execution path for the bounded Background wiring/tests. If the architect selects a different design, explicitly revise BG009's acceptance criteria and track the remaining full-content moderation/final-send obligation. Until that decision, **do not treat the preparation-only patch as BG009 acceptance evidence**.

## Architect Review

### Review Status

**Historical Attempt 1 review — blocked on architectural dependency (2026-10-26).** Developer Attempt 1 preparation was not accepted as a completed BG009 integration. The dependency has since been completed and Attempt 2 was claimed; the subsequent Attempt 2 self-review below returns this task to Ready for corrections.

### Review Notes

The inspected 26 October BG009 worktree shows a correct preparation-only `HumanWrapperPreparationService`, but `whatsapp.arch040_command_guard()` freezes the original `textBody`, and `whatsapp.arch040_moderation_subject_guard()` hashes that raw body. `PostgresModerationAssessmentService`, `OutboundSendFenceService` and `HumanCommandDispatcherService` consequently moderate, admit, persist and transmit `command.textBody`. Wiring a wrapped body only at the provider would break moderation-content identity; overwriting `textBody` would break accepted-command idempotency. Preserve the existing work and **do not** add an unsafe bypass.

**Historical Attempt 1 follow-up, superseded:** synchronize the canonical `database/` submodule after DATABASE-007 reaches Database `main`, then claim Attempt 2 and implement frozen prepared-body moderation/admission/provider equality while reconciling BG007's shared dispatcher without moving its post-window scope into BG009. The synchronization and implementation are now evidenced in the Attempt 2 claim and validation records above.


### Reviewed Files

- `moda-interact-background/src/services/recovery-conversation/human-wrapper-preparation.service.ts`
- `moda-interact-background/src/services/recovery-conversation/human-command-dispatcher.service.ts`
- `moda-interact-background/src/services/recovery-conversation/outbound-send-fence.service.ts`
- `moda-interact-background/src/services/conversation-moderation/moderation-assessment.service.ts`
- `moda-interact-background/database/prisma/schema.prisma`
- `moda-interact-background/database/prisma/migrations/20261017214500_arch040_remove_outreach_sequence_policy/migration.sql`
- `moda-interact-background/database/prisma/migrations/20261018092000_arch040_moderation_template_content_digest/migration.sql`

### Validation Reviewed

Inspected developer's recorded `prisma:generate`, patch-apply and whitespace evidence. Focused BG009 tests, build, database integration and provider equality are **not yet proven**.

### Architecture Conformance

Preparation module respects source/owner boundaries, but full delivery architecture cannot conform until the durable HUMAN_TEXT moderation subject and admitted/provider text agree. Preserve ARCH-040 consent, STOP, claim/window/billing/UNKNOWN rules.

### Follow-up

Execute `ARCH-040-DATABASE-007`, accept its schema/migration and tests, sync `database/` in BG009 implementation, then explicitly re-gate/reclaim BG009 as developer Attempt 2. Review BG007 shared dispatcher changes before final BG009 acceptance; downstream ARCH-047 system tests must assert original/approved/persisted/provider equality. No `_index.md` modification before architecture-session closure.

## Execution Ownership Amendment

- Date: 2026-10-26.
- Change: The developer explicitly invoked `/moda_developer_create ARCH-047-BACKGROUND-009` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_background`, coordinator, repository, task scope, acceptance criteria, validation requirements, and attempt history. Attempt 1 remains the prior developer attempt; this dependency-frontier reconciliation retains `attempt: 1` and does not claim Attempt 2. The existing BG007 shared-dispatcher reconciliation requirement remains unchanged.

## Historical Dependency Frontier Reconciliation (2026-10-26)

- `ARCH-047-BACKGROUND-005`: Complete.
- `ARCH-040-DATABASE-007`: Complete; implementation commit `12102f0b611973b1436f4c0d4ec33f3e15fa9a78` is published on its task branch. The Database implementation has not been merged to `main`.
- Transition: `blocked` to `ready`; `attempt: 1` preserved, `executor: null`, `claimed_at: null`. The next claim is Attempt 2.
- First Attempt 2 action: after DATABASE-007 is merged to Database `main`, synchronize the Background `database/` submodule to that merged commit, regenerate Prisma Client, and validate. Do not point the submodule at the unmerged Database task branch.
- No implementation source, submodule gitlink, `main` branch, or unrelated task record was changed by this frontier update.

## Developer Execution Claim (Attempt 2)

- Claim: `status: in_progress`, `executor: developer`, `claimed_at: 2026-10-26T19:37:18Z`, `attempt: 2`; `assigned_agent: moda_background` is unchanged.
- Dependency verification immediately before claim: `ARCH-047-BACKGROUND-005` and `ARCH-040-DATABASE-007` both resolved `complete`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-BACKGROUND-009`, branch `task/ARCH-047-BACKGROUND-009`, clean at `ba938dba3971cb6425c406887b9b9f4d9f98aeb8`; current `origin/main` `2624d6445e6d642568d521d18f3e277ea629950e` is an ancestor.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-BACKGROUND-009`, branch `task/ARCH-047-BACKGROUND-009`, clean at `ab55ed9a9d9de3aaf6791933db2574ed49a86f36`, equal to `origin/task/ARCH-047-BACKGROUND-009`; current `origin/main` `6cce2b18f288d4cabc6f7dcea3ef251acbb15323` is an ancestor.
- Database prerequisite: implementation `database/` submodule is clean at `7cd7e955c8ede2ce76631ee40c655daba91bfdd6`, equal to Database `origin/main`.
- Synchronization: fetched `origin --prune` in both canonical task worktrees; both were clean and task branches matched their remotes before the claim. No merge was required.
- Pre-existing implementation disclosure: commit `ab55ed9` and its source/test changes were already present and pushed before this canonical Attempt 2 claim. Claim preparation made no implementation edits; the report and remaining required validation must be reconciled against that actual history during this attempt.

## Developer Self-Review - Changes Requested (Attempt 2)

- Outcome: **changes requested**. The implementation branch is committed, pushed, clean, builds, and passes the focused prepared-send and BG007 regression suites. The explicit acceptance matrix is incomplete because the PostgreSQL raw-body-digest rejection and combined prepared-body crash/reclaim plus control-loss cases are not directly tested.
- Transition: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 2`. This returns Attempt 2 for corrections and does not create Attempt 3. The next developer claim increments the attempt once.
- Required corrections: add and run the two PostgreSQL cases listed under Attempt 2 changes requested; preserve BG007's post-window template branch; record exact results and re-run focused validation.
- Parent task/report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-BACKGROUND-009`, branch `task/ARCH-047-BACKGROUND-009`; this task-report transition is committed and pushed with the update. Implementation worktree remains `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-BACKGROUND-009`, branch `task/ARCH-047-BACKGROUND-009`, clean at `ab55ed9a9d9de3aaf6791933db2574ed49a86f36`.

**Subsequent correction evidence (26 October 2026; not a claim or new review decision):** Local implementation commit `7b135b1` adds the exact negative digest and crashed-lease/STOP/HUMAN-control-loss PostgreSQL tests; 5/5 integration files, 28/28 tests, build and focused ESLint completed without reported errors. The terminal shows the implementation branch one commit ahead of origin and does not show a push. Preserve `status: ready`, `attempt: 2` and the historical Changes Requested outcome until `/moda_developer_create` and `/moda_developer_update` reconcile the next attempt and submit it for review.
