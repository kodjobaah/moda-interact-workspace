---
id: ARCH-076-DATABASE-001
architecture_id: ARCH-076
title: Persist explicit sender ownership and routing evidence
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-15T19:56:51Z
attempt: 2
depends_on: []
enables: [ARCH-076-BACKGROUND-001, ARCH-076-ADMIN-001]
created: 2026-11-13
updated: 2026-11-15
---

# Persist explicit sender ownership and routing evidence

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Persist sender ownership and unresolved originals with five durable records.

## Context

15 November user-selected design retains five explicit sender entities plus the R15 evidence amendment. Sender attribution and conversation-credit renewal are independent streams. The user has authorized implementation of this reviewed design. Preserve prepared claims; execute only through the owning task launcher and accepted dependency frontier.

## Scope

Prisma, one forward sender migration, constraints/indexes, scoped ERD and disposable PostgreSQL tests; see exact fields in parent architecture.

## Out of Scope

Other repository implementation, live settings, production migration and activation. Sender tasks must not implement allowance renewal; allowance tasks must not implement sender allocation. The SYSTEM-TEST task is deferred at the user's request.

## Requirements

- [x] Support the parent explicit R15 two-stage star relation: Q2 shop choice and Q3 basket choice both parent Q1 substantive original; Q3 names exact basket prompt Q2, whose parent is Q1. Prompt may be Q1 or its explicitly identified direct child, not necessarily original itself.

- [x] Follow the parent R15 evidence privacy amendment: routingDecision contains only message IDs, clause offsets/hashes and structural evidence, no exact clause plaintext. Preserve exact wording through pending inputJson then atomic existing ConversationMessage association.
- [x] Freeze input/candidate/config/parent scope; permit only explicit destructive terminal value→NULL scrub and real FK SET NULL cleanup, never rebind or payload resurrection. Terminal scrub removes ephemeral customer/candidate/prompt payloads without deleting authentic owned Conversation history.

- [x] Add nullable routingDecision JSONB separately from configurationSnapshot, with structural schema-version/object validation and write-once decision evidence. Preserve the parent R15 original/current inbound, confirmed prompt, candidate fingerprint, exact clause/moderation, policy/template and owner/control bindings. Application owns role/evidence business validation; SQL guards prevent replacement of frozen evidence and terminal-resolution rebinding.

- [x] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [x] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [x] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [x] Enforce immutable recipient/sender identity and assignment-per-Conversation; protect original request candidate snapshots and terminal resolutions.
- [x] Preserve current ordered-delivery sender/status evidence; use database baseline 2e14f866 with all 80 predecessor migrations through 20261113111320_arch075_meta_app_operation_state; sender target 20261113120000_whatsapp_sender_pool remains available.
- [x] Preserve prepared attempt 1 metadata; resume only in its canonical prepared implementation worktree.

## Work Items

- [x] Inspect the exact latest accepted repository pin and existing owning mechanisms.
- [x] Implement only this task's scope and requirements.
- [x] Complete the focused checks below and record exact commands and evidence.
- [x] Return the isolated implementation branch and parent Completion Report for review.

## Interfaces / Contracts

The parent architecture's Explicit sender storage, Independent allowance storage and Configurable routing sections are authoritative. Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Dependencies

None

## Enables

Recalculate from dependent task metadata after architect acceptance; no implicit implementation handoff.

## Acceptance Criteria

- [x] Frozen routingDecision cannot be replaced during retry or terminal replay; invalid structural shape is rejected without imposing model confidence business policy in SQL or Shared.

- [x] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [x] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [x] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [x] Enforce immutable recipient/sender identity and assignment-per-Conversation; protect original request candidate snapshots and terminal resolutions.
- [x] Preserve current ordered-delivery sender/status evidence; use database baseline 2e14f866 with all 80 predecessor migrations through 20261113111320_arch075_meta_app_operation_state; sender target 20261113120000_whatsapp_sender_pool remains available.
- [x] Preserve prepared attempt 1 metadata; resume only in its canonical prepared implementation worktree.

## Validation

- [x] Positive Q1 unknown-shop→Q2 shop selection and basket prompt→Q3 exact basket selection→Q1 resolution/admission flow; reject foreign original/prompt/thread/route scope and missing confirmation, with replay/concurrency tests. No extra table/column or recursive/newest prompt lookup.

- [x] Verify exact clause survives association/retry through authentic message IDs and offsets/hash; routingDecision contains no customer plaintext. Test frozen payload replacement rejection, terminal destructive scrub, FK cleanup and resurrection/rebinding rejection.

- [x] Disposable PostgreSQL checks cover NULL initial decision, one valid freeze, attempted replacement, wrong schema shape, terminal replay and preservation of configurationSnapshot as a distinct record.

- [x] Prisma validate/generate and scoped ERD render against actual declared commands.
- [x] Fresh and full-history upgrade replay preserve existing rows, ordered delivery parts, Meta operation state and old-writer nullable fields.
- [x] Real PostgreSQL constraint, immutability, duplicate inbound, concurrent recipient allocation/release and deletion cases.

Inspect the repository package.json before selecting actual commands. Required disposable PostgreSQL checks are task-local repository checks, not execution of the deferred system-test task. No live customer/provider calls belong to these checks.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set review, return the Completion Report and STOP. Do not execute another task or deploy.

## Implementation Notes

Replace obsolete fixed SQL counts with exact reviewed five-table objects. Generate final SQL from the user-authorized field contract; do not copy historical five-table SQL.

## Completion Report

### Status

Ready for Review — prepared attempt 1 resumed without re-claiming or incrementing. This agent performed no hosted migration, service activation, system-test execution or main merge. The coordinator subsequently merged the accepted implementation source as recorded below.

### Files Changed

Implementation repository only:

- `prisma/schema.prisma`: five sender/routing models, inverse relations, two nullable root dispatch sender fields; unchanged one-Conversation-per-checkout uniqueness.
- `prisma/migrations/20261113120000_whatsapp_sender_pool/migration.sql`: additive tables, 9 FKs, 14 CHECKs, 16 explicit indexes, 8 functions and 11 triggers. Parent/assignment/resolution FKs use reviewed deferred deletion semantics.
- `scripts/test-arch076-sender-pool-postgres.mjs` and package script: invocation-owned PostgreSQL authoring/deployment, preservation, ownership, freeze, concurrency, resolution and deletion validation.
- `docs/architecture/arch076-sender-pool.md`, scoped `docs/generated/arch076-sender-pool.puml/.png`, and scoped additions to `docs/generated/prisma-erd.puml`.

Parent write: this task file only. No parent submodule gitlink staged.

### Work Completed

- Implemented immutable verified sender identity, recipient/sender thread generations, shop routes and lifetime recovery Conversation assignments. Assignment creation locks Conversation then CheckoutRecovery, while deferred reverse-owner checks prevent concurrent parent edits from invalidating ownership.
- Preserved separate bound-shop and admitted-prompt scope. A neutral prompt remains neutral after shop binding; physical shop deletion scrubs pending private input without rebinding historical scope.
- Added structural schema-versioned, write-once routing decisions and explicit immutable resolution witnesses. A frozen Q1 CLARIFY is preserved while a later child authorizes resolution; direct usable classifications may self-resolve, but CLARIFY cannot. Explicit prompt lookup supports original → shop prompt holder → basket selection, with no newest/reverse/recursive inference.
- Protected raw input/candidate/moderation/configuration snapshots from replacement, permitted destructive terminal cleanup, excluded plaintext clause fields from decision evidence, preserved exact prompt receipts, and prevented terminal owner/resolver rebinding.
- Preserved existing ordered physical delivery/status proofs and nullable old-writer message inserts. No credit/allowance fields, counter resets, fake funding or additional Conversation were added.

### Validation Results

Final tested implementation commit: `87fbe59edfc6aa80607f2dfdc409e9f1e5ed3dda`; tree `ec1a255c3501e239d9173671d5ced7a43f8b4089`.

- `npm run lint` — PASS, exit 0.
- `npm run test:arch076-sender-pool:postgres` — PASS, exit 0, **226 assertions**, actual Prisma migrate dev `--create-only --skip-generate` against disposable local PostgreSQL, then migrate deploy on fresh and seeded upgrade databases. All 80 predecessors replayed; 81 migrations through this target, re-deploy no-op.
- Upgrade fingerprints preserved Shop, CheckoutRecovery, Conversation, CustomerPhone/consent, UsageEvent, UsageReservation, ConversationMessage, ConversationDeliveryPart, ConversationDeliveryStatusReceipt and MetaTemplateAppOperationState rows.
- Positive and negative SQL cases covered frozen decisions, original/current identities, private-clause exclusion, neutral prompt scope, cross-thread/shop/parent/assignment rejection, parent/resolver cohort retention, physical owner deletion, immutable generation/assignment/dispatch proofs, concurrent owner mutation versus assignment insert, serialized recipient allocation, sibling release/admission, duplicate/restarted admission, SELECT_ONLY, SELECT_AND_QUESTION, independent NEW_QUESTION, distinct competing selection children, CLARIFY self-resolution rejection, and two-stage shop/basket prompts with forged root/thread/scope/receipt rejection.
- `npm run validate` — PASS, exit 0.
- `npm run prisma:generate` — PASS, Prisma Client 6.19.3, exit 0.
- `npm run erd:puml` — PASS; retained only task-scoped new entities/relations and new message columns in the tracked aggregate ERD to avoid unrelated snapshot churn. `plantuml -tpng docs/generated/arch076-sender-pool.puml` — PASS; rendered PNG visually inspected.
- `git diff --check` — PASS; final implementation worktree clean.

Final invocation-owned PostgreSQL container `moda-arch076-sender-73bc8629-2bde-49be-88e7-30fbd1ad1930` and its volumes/temporary migration files were removed by the runner. Earlier interrupted containers were removed; no unrelated container or hosted DB was targeted.

Resolved iteration failures: non-login shell initially lacked Docker; login shell plus canonical Node bootstrap resolved it. Workspace ENOSPC/containerd I/O failure interrupted one run; root coordinated disk/Docker recovery before the final successful replay. An expanded-fixture helper ordering ReferenceError and lint `no-unsafe-finally` were corrected and rerun. Cleanup now preserves the primary failure. `npm ci --ignore-scripts` reported 8 dependency audit findings; dependency versions/lockfile were not changed by this task.

### Git / VCS

- Mirrored branch: `task/ARCH-076-DATABASE-001` in both repositories.
- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-076-DATABASE-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-076-DATABASE-001`.
- Shared workspace/shared implementation checkout switched or mutated for implementation: no. Another task worktree reused: no.
- Prepared packet: parent remote task fast-forward not-needed; origin/main incorporated yes; implementation remote task fast-forward not-needed; origin/main already-current at `2e14f8668346dfc135aa12f8d1fbc94e05c12ce7`.
- Recursive submodule sync/update passed in launcher; no nested implementation submodules.
- Original durable claim remains `5c0bc8cbe931abe52716492a9ccb150abcf5fe71`, attempt 1, executor codex, claimed_at 2026-11-15T11:46:23Z. Parent resumed current governance by merging origin/main into this same task branch, most recently `2628b87dfc6e1877bf6eb853bc7c7308366195e8`.
- Source commit/tree above pushed to `origin/task/ARCH-076-DATABASE-001`; source PR [Database #79](https://github.com/kodjobaah/moda-interact-database/pull/79).
- Coordinator merged source PR #79 to actual Database main `a7c204618c6b0ad83952a7b661482cfd03acf899`. A read-only fetch verified its tree `ec1a255c3501e239d9173671d5ced7a43f8b4089` exactly matches the tested source tree; no additional schema/code changes were introduced by integration.
- Parent task/report is published on the same mirrored branch; historical governance PR #1059 is already merged, and the new report PR URL is provided in the coordinator handoff; initial review-report publication commit `b9c07371e1d0fe4c93f50f40bb038ec2771ca4ba` is pushed; final source-integration evidence publication SHA is recorded in the coordinator handoff.
- Implementation main merged by this agent: no. Parent main merged by this agent: no. Unmerged implementation gitlink staged: no. Coordinator owns acceptance, final main integration and accepted DB consumer pin.

### Deviations

No runtime scope expansion. Added selective partial indexes for historical scope cleanup and parent/resolver/selected-pointer retention/deletion queries, avoiding full retained-turn scans. The sibling release/admission fixture deliberately retains another live assignment; it is not represented as the actual allocation service's last-member generation-closure race, which belongs to BACKGROUND-001.

### Assumptions

Background owns consent, window, contacted/eligible candidates, moderation, confidence, configuration and provider admission. SQL supplies durable structural identity/ownership/freeze constraints, not model confidence business policy. Allowance renewal remains independent DATABASE-002/BACKGROUND-005 work.

### Unresolved Issues

None blocking this bounded database task. Hosted rollout and architecture-level system tests are not claimed; SYSTEM-TEST-001 remains deferred at the user's request.

### Architectural Concerns

No new concern. Reviewed privacy, parent-retention, immutable resolution witness, ownership concurrency and multi-stage prompt amendments are incorporated.

## Architect Review

### Review Status

Accepted — root review, 15 November 2026.

### Review Notes

Accepted exact tested implementation; see final root acceptance evidence below.

### Reviewed Files

Prisma schema, sender migration and integrity triggers, PostgreSQL runner, package scripts, architecture notes and scoped ERD.

### Validation Reviewed

226 fresh/seeded-upgrade PostgreSQL assertions, lint, Prisma validate/client generation, scoped ERD and exact merged-tree equality.

### Architecture Conformance

Five explicit routing entities; same original Conversation retained; no allowance funding rules or Shared changes.

### Follow-up

ADMIN001 and BACKGROUND001 are Ready. Actual allocation-service last-member race belongs BACKGROUND001. Hosted rollout and SYSTEM-TEST remain deferred.

## Reconciliation provenance — 15 November 2026

Reconciled from the later local sender-pool revision formerly labelled ARCH-069. The completed chronological-input architecture and its ARCH-069 task identities are unchanged. ARCH-076 was already reserved for the earlier sender-pool proposal; this revision updates that proposal in place, retaining its Git history. These are definition changes, not implementation or deployment evidence. All execution remains Pending until compatibility review and dependency promotion.

## Current-main definition review — 15 November 2026

Architect read-only compatibility review against Database `2e14f866` found no conflicting Prisma anchor, table, foreign-key target or prescribed SQL name. The predecessor has 80 migration SQL files ending at `20261113111320_arch075_meta_app_operation_state`; the prescribed unused `20261113120000_whatsapp_sender_pool` target is the 81st through that migration. Upgrade fixtures replay all 80 predecessors and preserve the existing `ConversationDeliveryPart`, `ConversationDeliveryStatusReceipt` and Meta operation-state tables/rows in addition to the ordinary seeded ownership, consent, billing and message rows. Expected source counts are 138 Prisma models and 108 tracked PUML entities before this task.

The SQL contract remains five new tables, eight foreign keys, thirteen CHECKs, nine explicit indexes (six partial) and one identity trigger/function. Required fresh/upgrade/concurrency validation belongs to the Database implementation attempt; this read-only definition review is not evidence those tests passed.

DATABASE-001 is independently Ready: it supplies sender-pool storage only. The same-Conversation renewed-credit amendment belongs to separate DATABASE-002 and BACKGROUND-005 definitions and does not authorize adding allowance fields or billing policy here. No downstream task is promoted by this definition review. No implementation worktree, claim, schema migration or live mutation has been performed by the architect.

### 15 November definition amendment

Historical fixed SQL must be regenerated for the restored five-entity contract plus R15 evidence; hardcoded router policy remains superseded. Historical claim/review evidence above is retained as history, not approval of the replacement implementation. No runtime source or migration has been implemented. User has authorized implementation; runtime acceptance and rollout verification remain pending.

Prepared claim evidence: parent task claim commit `5c0bc8cbe`, attempt 1, executor codex, claimed_at 2026-11-15T11:46:23Z. Dedicated implementation worktree remains untouched at Database main 2e14f866. The earlier user-review pause is lifted; resume this exact prepared attempt without erasing its claim or incrementing a new attempt.

Restored exact storage contract: use parent Explicit sender storage field table, FK/delete actions and indexes for all five entities; preserve R15 routingDecision separate from configurationSnapshot and immutable candidate/original/prompt scope. Prior SQL block/counts in historical review are not current migration instructions. No new claim; prepared attempt1 resumes under the user authorization.

Parent relationship correction: parentProviderMessageId FK NO ACTION DEFERRABLE INITIALLY DEFERRED; allow NULL→ID once after classification (row must exist before model I/O), then no clear/rebind. Retention deletes eligible parent/dependent cohorts or full thread cascade; selected Conversation associates only atomically with frozen routingDecision. Validate deferred parent deletion protection, bind-once concurrency and cohort deletion. This supersedes generic parent FK SET NULL cleanup wording.

R15 positive resolution lifecycle correction: classifier routingDecision and later original-request resolution are separate. Add nullable resolutionInboundProviderMessageId TEXT self-FK NO ACTION DEFERRABLE INITIALLY DEFERRED (no global UNIQUE). Q1 frozen CLARIFY stays unchanged; confirmed prompt + Q2 frozen exact-parent SELECT_ONLY/SELECT_AND_QUESTION permits Q1's initial selectedConversationId+witness=Q2 bind atomically with original admission and terminal scrub. Direct NEW_QUESTION may use self witness and leaves older pending originals alone. Bound witness is immutable; a preexisting CLARIFY decision must not block valid first resolution. Validate same-thread/route original/prompt/candidate and current owner/control/moderation under lock. Required positive PostgreSQL original→CLARIFY→confirmed prompt→child selection→original admission case, plus simultaneous selections/replay/crash, forged witness, separate new question, exact additional clause and retention-cohort deletion. Do not rewrite classifier decisions or infer resolver by reverse-child lookup.

The parent R15 explicit two-stage shop then basket clarification section is authoritative. Preserve Q1/Q2 CLARIFY decisions; Q3 exact role decision and Q1 resolution witness provide later admission evidence. Prior wording requiring promptTurnId equal originalTurnId is superseded by the direct-child star contract.

### Root acceptance and automatic completion — 15 November 2026

Accepted source PR79 at actual Database main a7c204618c6b0ad83952a7b661482cfd03acf899; merged tree ec1a255c3501e239d9173671d5ced7a43f8b4089 is identical to tested87fbe59. Root reviewed schema, sender/owner integrity, explicit original/prompt/resolution relationships and final evidence. Final226 disposable PostgreSQL assertions pass across fresh and seeded full-history upgrade, plus lint, Prisma validation/client generation and scoped ERD. Checks include the two-stage Q1/Q2/Q3 star relationship and forged-scope rejection. The sibling release/admission check does not replace BACKGROUND-001 actual last-member allocation service race. Automatic completion retains attempt1 and claim history, clears activeclaim fields, and promotes only explicit dependent tasks. No hosted migration, activation or SYSTEM-TEST performed.

## Developer Override — explicit reopen, 15 November 2026

User decision: **“Reopen DATABASE-001 for this correction.”** Root received this explicit decision before this lifecycle edit. Reopen preserves the Accepted attempt-1 review, report, source and claim history above. Current status is Ready, executor/claimed_at remain null and attempt remains 1; only the next prepared execution claim increments to attempt 2. Execution remains agent-owned with automatic architect completion. This is a bounded correction of the existing R15 integrity contract, not permission to recreate sender storage or edit old migration history.

### Correction objective and ownership

The existing ARCH040 moderation subject trigger requires a CUSTOMER_MESSAGE assessment digest to equal the complete authentic ConversationMessage content. R15 SELECT_AND_QUESTION preserves that full inbound text for merchant history while independently moderating its exact genuine question clause. Add one forward migration to authorize only that proven clause subject. No new table, column, Shared API, plaintext decision field or general digest bypass. Consume latest accepted Database main including D002; preserve all existing sender/allowance constraints.

### Required integrity contract

- Preserve the existing full-content digest path unchanged for ordinary customer text/transcripts and all AGENT/AUTOMATION/HUMAN subjects. An unmatched alternative must still fail closed.
- The narrow alternative applies only CUSTOMER_MESSAGE/TEXT, or CUSTOMER_MESSAGE/TRANSCRIPT with the verified audio proof below, on the actual authentic inbound CUSTOMER message. Require an immutable RESOLVED RoutingTurn with SELECT_AND_QUESTION, actual current provider ID and associatedMessages.currentMessageId matching this exact message, selectedConversationId matching its real Conversation/shop, and resolutionInboundProviderMessageId equal to the current routing inbound identity.
- Require the referenced original root to be the explicitly bound parent, same thread and selected owner, resolved by this same current witness. Validate the exact confirmed prompt relationship: prompt is original root or its explicitly bound direct child, confirmed provider receipt matches decision, and frozen route/prompt scope agrees with selected owner. Do not infer a parent or prompt from newest/reverse traversal. Preserve direct NEW_QUESTION/SELECT_ONLY/CLARIFY rejection for clause digests.
- Require current authentic full text moderation ALLOW proof under its exact full digest and current policy before accepting the independently assessed clause. Keep original-Q1 assessment proof and application moderation lifecycle intact. A failed or absent full-current assessment cannot be laundered by a clause ALLOW.
- Validate frozen clause start/end as bounded integer **JavaScript UTF-16 code-unit offsets** against actual immutable full message content. Reject negative/reversed/out-of-bounds offsets and split-surrogate boundaries. Hash precisely the corresponding UTF-8 encoding of the JavaScript slice; Postgres code-point substring is not equivalent when astral characters precede the clause. Both decision clause.sha256 and NEW.contentSha256 must equal that exact slice digest. Never store clause plaintext in routingDecision or retain scrubbed customer payloads there.
- Retain same-owner/actor/input checks, assessment lease/lifecycle guards, prepared decision immutability and terminal payload scrub. Use existing rows/evidence only. No timestamps fabricated or policy decisions moved into structural Shared validation.

### Attempt-2 work and acceptance checks

- [x] Add an additive, safely ordered forward migration replacing only the owning moderation digest guard behavior; do not modify already deployed ARCH040/D001/D002 migration bytes.
- [x] Positive actual transaction: Q1 original → confirmed clarification → authentic Q3 SELECT_AND_QUESTION full text, frozen decision/resolution association, full-current ALLOW plus independently moderated exact clause, all same owner. Verify persisted full text and two distinct exact digest assessments; Q1 remains separately proven.
- [x] Positive two-stage Q1/Q2/Q3 star, ASCII and emoji/astral-prefix UTF-16 offsets, fresh database and upgrade from full current accepted migration history.
- [x] Negative wrong message/provider ID/Conversation/shop/thread/parent/resolution witness/prompt receipt/route scope; mutable or unconfirmed decision; wrong role; missing/disallowed full-current moderation; forged hash, malformed/noninteger/out-of-range/split-surrogate offsets; unverified transcript/AGENT/AUTOMATION/HUMAN alternatives; foreign assessment and replay/tamper. No blanket exception.
- [x] Existing moderation subject/lifecycle regressions and sender evidence/privacy invariants continue passing. Run task-local disposable PostgreSQL checks, owning schema/client validation and required repository lint/build checks; inspect actual package scripts. SYSTEM-TEST remains explicitly deferred.
- [x] Record new migration identity/checksum, exact tested source, physical prepared attempt-2 isolation/synchronization and complete test evidence. Return Review and stop; no hosted migration or live activation.

BG004 may continue its independent implementation under its existing active claim, but clause-path acceptance/rollout is held until this correction is architect-accepted and its migration is present in the tested environment. Completed downstream tasks retain their historical acceptance; they are not silently reopened. No new unrelated task is introduced.

### Verified voice clause clarification — attempt 2, 15 November 2026

Voice is already part of R15; the user's general exact verified question-clause correction includes this case. Extend the same narrow alternative to TRANSCRIPT only when the authentic message is inbound CUSTOMER, contentType AUDIO and transcriptionStatus COMPLETED. Require actual full transcript content and immutable authenticated provider-message/media identity to match the verified transcript/source hash and operation/configuration provenance supplied before classification; reject missing, altered or unverified transcript evidence. Keep full-current canonical TRANSCRIPT ALLOW under its full-content hash as prerequisite, followed by an independent canonical clause TRANSCRIPT assessment with the exact UTF-16 slice hash. Apply the same resolved owner/original/prompt/witness checks as TEXT. Test verified voice SELECT_AND_QUESTION (including astral-prefix offsets), wrong media/source/full transcript hash, incomplete/failed transcription, foreign provenance, missing full-current ALLOW and ordinary unverified transcript refusal. Existing non-routing TRANSCRIPT full-content validation remains unchanged.

Background reuses the existing configured speech/download/validation primitives under the durable RoutingTurn lease before a Conversation is selected. Immutable inputJson retains the authenticated raw audio event. Existing single-fill moderationJson temporarily holds verified full transcript, exact source/media digest, immutable speech operation/configuration provenance and full-current moderation proof before classification. Later immutable routingDecision may retain bounded **nonplaintext** assessment metadata (IDs, hashes, model, categories/outcomes and configuration revisions) for full/clause proof; never transcript or clause plaintext. Final same-owner admission creates the real AUDIO/COMPLETED message and canonical full-current plus clause assessment rows atomically; JSON is evidence, never a replacement moderation store. Terminal scrub removes ephemeral transcript/proof payloads while preserving required nonplaintext decision evidence. No fake Conversation, new table/column, Shared release, invented speech defaults or credit debit. Exact provider billing is not claimed once-only if an unknown speech operation must be retried.

This clarification preserves the active prepared attempt-2 claim and report. Database and Background owners must agree the precise existing JSON proof shape before freezing the SQL guard; no broad AUDIO/TRANSCRIPT digest exemption is authorized.

Because moderationJson is scrubbed at terminal association, the immutable routingDecision must retain the bounded **nonplaintext transcript attestation** required to validate later canonical assessment lifecycle operations: authentic provider/media identity and source digests, exact full-transcript hash, speech operation/configuration revision proof and full-current assessment ID/hash with inputKind TRANSCRIPT. Match this attestation to the actual AUDIO/COMPLETED message, full content and canonical assessment. Do not depend on scrubbed plaintext to authorize later updates, and do not retain transcript/clause text in this attestation.

## Attempt-2 Completion Report — R15 clause moderation correction

### Status

Ready for Review. The accepted attempt-1 implementation and Architect Review above remain unchanged history. This prepared attempt implements only the explicitly reopened moderation correction.

### Correction checklist and implementation

- **Implemented — additive owning guard correction:** `prisma/migrations/20261115201000_arch076_r15_clause_moderation/migration.sql` preserves ordinary full-content validation and adds only the exact CUSTOMER_MESSAGE TEXT/verified TRANSCRIPT R15 alternative. No deployed migration bytes, Prisma model, table, column or index changed; ERD remains unchanged.
- **Implemented — authoritative resolved evidence:** exact current provider/message identity, self resolver witness, original root/parent, confirmed original-or-direct-child prompt receipt, same thread/route/Conversation/shop and frozen role are required. Canonical original and full-current ALLOW assessments under the same policy/model precede the independent clause assessment. Historical proof does not depend on active assignment, control revision, window or scrubbed payloads.
- **Implemented — exact UTF-16 and authentic history:** the slice helper rejects malformed bounds and split surrogate pairs, hashes the exact UTF-8 encoding without normalization, and leaves the complete authentic customer text/transcript untouched. Clause and full-current canonical assessment rows remain distinct.
- **Implemented — verified voice and privacy:** initial decision freeze binds bounded nonplaintext audioCurrent/audioOriginal attestations to single-fill verified speech metadata, exact raw media/provider identity and transcript hash. Raw-source SHA-256 is independently recomputed using the versioned `whatsapp.arch076_r15_audio_source_sha256(inputJson)` SQL recipe; Background reads that same helper, with no Shared canonicalJson fallback. Final AUDIO/COMPLETED records must match retained media/transcription identity and full content after terminal scrub. Exact nested metadata allowlists reject plaintext; transcript proof must be a nonblank JSON string using the JavaScript trim whitespace set.
- **Implemented — direct voice integration:** self audioOriginal is permitted only with actual NULL parent, NEW_QUESTION/CLARIFY, NULL original IDs, exact current provider and equal nonempty associated message IDs. Positive both-role freezes and invalid self-selection/self-ID shortcut cases pass; selection-parent clause authorization is unchanged.
- **Implemented — review corrections:** consistent forgery of both metadata and frozen attestation is tested (source/transcript hash and nested plaintext), alongside missing/numeric/ASCII-blank/Unicode-blank transcript proof. The prior equality-only source-hash gap and NULL/NULL or numeric transcript-proof gaps are closed.

### Final source and validation

Final tested source: `4372d0a06c905a27fcfd1a14a38e17f907ae9bfb`; source PR [Database #80](https://github.com/kodjobaah/moda-interact-database/pull/80).

Migration SHA-256: `4498000f9882c8a5404fe4d8e8b87359baa1b0f6724e3b8192fb193ae622fb68`.

- `npm run test:arch076-r15-clause:postgres` — PASS, **684 assertions**, complete fresh 83-migration deploy, seeded upgrade from all 82 accepted predecessors and no-op redeploy. Historical messages/usage/reservations/delivery evidence preserved. Tests cover exact one/two-stage routing, authentic full message plus independent canonical clause moderation, text and verified current/original voice, astral/combining/CRLF Unicode slicing, malformed/foreign role/identity/prompt/hash/offset proof, missing/disallowed full-current proof, voice source/media/provenance tampering and historical reads after release.
- `npm run test:arch040-moderation:postgres:fresh` — PASS against the complete **83-migration chain**, including ordinary text/transcript/template actor/digest/tenant validation, idempotency, immutable bindings, lease/token-CAS completion, terminal outcomes and attributed review.
- `npm run lint`, `npm run validate`, `npm run prisma:generate`, `git diff --check` — PASS. This repository declares no build script; schema/client checks are its owning validation.
- All task-local PostgreSQL instances were invocation-owned local Docker fixtures. No hosted database, customer/provider call, live setting, SYSTEM-TEST task or main merge was performed.

### Prepared execution and publication

Prepared packet `/tmp/arch076-database001-attempt2-prepared.json` supplied the exact canonical workspace and reused physical D001 worktrees. Parent: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-076-DATABASE-001`; implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-076-DATABASE-001`; both branches `task/ARCH-076-DATABASE-001`. Launcher incorporated origin/main in both, with no remote task fast-forward needed, source baseline `0a965c549b4916085acd8a806d5ecf376eda0e47`, recursive submodule synchronization passed (none). Durable prepared attempt-2 claim `a70dd7f10cafd67327fd5ce1f656d630db3f72ec`, executor codex, claimed_at `2026-11-15T19:56:51Z`; no re-claim or startup redo. Architect voice clarification was preserved on the same parent task branch.

Source and this parent task report are committed/pushed on the mirrored branches. No shared checkout switch, other task write or unmerged gitlink staging. Root owns source acceptance/main merge, final parent gitlink and rollout.

### Rollout and unresolved issues

No unresolved implementation issue. Apply the accepted forward Database migration before corrected Background voice/clause admission uses its helper/guard. Background owns actual protected speech/configuration verification and full-current-before-clause admission; SQL retains structural authoritative proof and existing moderation lifecycle. Sender routing and credit renewal remain separate. Production activation and deferred SYSTEM-TEST execution are not claimed.
