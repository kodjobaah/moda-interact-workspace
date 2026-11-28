---
id: ARCH-070-BACKGROUND-012
architecture_id: ARCH-070
title: Bind recovery replies to the latest customer question
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: codex
claimed_at: 2026-11-15T01:19:41Z
attempt: 1
depends_on:
  - ARCH-070-BACKGROUND-011
enables: []
created: 2026-11-15
updated: 2026-11-15
---

# Bind recovery replies to the latest customer question

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; moda_architect.

## Objective

Prevent historical customer questions or assistant replies from becoming the objective or lead of the latest admitted customer turn.

## Context

Actual production01:02 request asks about one named snowboard but reply prepends an older category answer plus separator before details;01:05 same question gives correct verified detail/image. Private evidence current-production-layout-reply-production.json stays protected. This is not proven to be model-only: inspect current pending-window/history assembly and composition before choosing fix. Root explorer latest_question_trace supplies exact findings.

## Scope

Current inbound objective/history/context boundary and app-owned completion focus; deterministic reproduction and actual host/processor tests. No implementation byarchitect.

## Out of Scope

Shared release, model/provider/token changes, deleting customer/audit history, question/product regex heuristics, invented selected IDs, loosening grounding, broad transcript or layout refactor, live calls/main merges.

## Requirements

Inspect latest accepted runtime and exact source path before editing: worker loadConversationTurn passes pendingTurnStartedAt; checkoutRecovery getAgentContext assembles currentmessages/history; host prepareCurrentCustomerMessages and Shared runner receive both. Establish whether an old pending window, duplicated latest/history entries, stale objective or composition lead causes contamination. Reproduce old-category history plus latest standalone detail question with synthetic IDs/text and preserve failing evidence. Do not guess another generic prompt fix.

Anchor objective to the latest server-authoritative admitted customer input identity/version, separating older questions and assistant outputs as lower-trust history. Historical references may resolve an explicit current follow-up, but never automatically request re-answering an old question. Preserve genuine current multi-message batch semantics only when actually bound to admitted version; do not silently discard a pending customer message or invent one. Exact original current content/roles unchanged, no assistant/system promotion. Active input ordering, audio transcription completion and duplicate timestamps need deterministic tie-break/identity tests. If the actual rule needs state beyond existing metadata, return architecture gap before inventing database fields.

Application-owned focus guidance may state answer only current objective and use prior context only for reference; actual request assembly/regression must prove new authority, not text-only prompt assertions. Current-turn observed selection, independent refresh, raw/canonical transport binding, fallback011, control/consent/window/lease/idempotency/usage/finalpermit remain unchanged. No unsupported history-based factual lead may bypass discovery guard. No new model retry/budget. Privacy-safe finite diagnostics only if existing signals insufficient, reuse shared logging; no raw history or IDs in publicfixtures.

Root owns implementation workflow delegation, source/main merges and actual provider/live verification. Normal isolated launcher claim required; canonical primary unrelated work preserved.

## Work Items

- [ ] Establish exact contamination mechanism and regression.
- [ ] Correct app current-question authority/history assembly.
- [ ] Validate latest-only and legitimate follow-up/multi-input cases.
- [ ] Return immutable source/report.

## Interfaces / Contracts

Existing RecoveryAgentContext/currentCustomerMessages/published6.1 runner only. App owns authoritative DB/currentturn selection; no duplicated Shared contract or genericmechanism.

## Dependencies

ARCH-070-BACKGROUND-011 Complete; source base actualBackground68fd52ca98ac6f94df871e2c4478f96460b7ee6e or lateracceptedmain.

## Enables

Independent shorter-caption task013 integration and root genuine latest-question canary.

## Acceptance Criteria

- [ ] Old category question/assistant answer does not prepend to latest standalone product detail reply.
- [ ] Latest exact server-bound input authoritative; follow-up references and valid current multi-input behavior preserved.
- [ ] Raw/model/selection/fallback/control/delivery safety remains unchanged.
- [ ] Concrete mechanism and source evidence documented, not speculative efficacy.

## Validation

- [ ] Context-loader/currentobjective synthetic regression including oldcategory/latestdetail, assistant/history duplicates, timestamp/audio and followup.
- [ ] Actual host/processor request and composition tests with current verified products; no rawhistory canaries.
- [ ] Required actual lifecycle/currentversion no-send guards where changed.
- [ ] Declared types/build/scopedlint/exactremoteCI; no unmotivated broad repeats.

## Stop Condition

After defined checks/report setReview and STOP. No provider/model/send calls or mainmerge bytaskagent.

## Implementation Notes

Normal launcher fresh siblings from primary root. Not alone; task013 owns concise composition; coordinate actual overlapping imports but do not revert others. Root owns realcanary.

## Completion Report

### Status

Review Ready; implementation PR237, final source b8e6f92 (full SHA via Git). Root retains live verification ownership.

### Files Changed

Application history selection/bounding, recovery focus instructions, latest moderation authorization; focused history/current window/checkout-context/moderation tests, actual host request regression and disposable PostgreSQL moderation integration.

### Work Completed

Actual failure: an old categories question persisted since the previous afternoon in pendingTurnStartedAt. A later named-product question was appended to that same current array, so the model answered both. The newest raw server-ordered customer input is now the sole objective. All earlier fragments remain bounded moderated history, including merchant replies; no customer/audit rows deleted or pending timestamps rewritten. Audio uses transcript-ready chronology with createdAt/id ties. The latest raw identity is selected before ALLOW filtering; the gate requires its own ALLOW and retains any classification retry, never authorizing it from an older message. Same-time predecessors enter the bounded historical selection. Prior candidate window remains the existing20 rows ordered by creation/id, then merged/deduplicated/readiness ordered; this is not a global all-history scan.

### Validation Results

- Before fix, new targeted regressions against accepted source produced7 failures/19 passes; exact log preserved privately /tmp/bg012-baseline-regression.log.
- Fixed initial history/moderation28 tests passed; final expanded focused76 tests passed; checkout-context24 tests passed.
- Lifecycle/moderation158 tests passed; actual local HTTP/MCP model-host156 tests passed, including newest-only current request with categories history.
- Actual disposable PostgreSQL13 tests passed, including eight-hour backlog/latest allowed and blocked, stable same-time outbound predecessor, content-specific persisted moderation and zero WhatsApp sends.
- Type check, production build and scoped lint passed; final build after tie query also passed.
- Full hosted initial CI exposed one stale checkout loader mock/query order and old multi-current expectation; updated to assert latest current and first fragment history. Final exact-head CI pending review gate.

### Physical Worktree Isolation and Synchronization

Canonical workspace /Users/kwadwoadomafriyie/project/moda-interact-workspace; launcher parent /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-070-BACKGROUND-012 and implementation /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-070-BACKGROUND-012; both task/ARCH-070-BACKGROUND-012. Parent reused, implementation newly created. Parent and implementation origin/main already current at claim; no remote task fast-forward needed. Claim9920931cdfe11cc68b192f60dccffe4dcf9b3771, attempt1 codex. Implementation base68fd52ca98ac6f94df871e2c4478f96460b7ee6e; recursive database6f42b71112efe7ac63654d55f41cd74ca569b1ae synced/initialized. No shared/default checkout switched or mutated, no other task worktree reused.

### Deviations

None. No Shared publication, model/provider/token change, live send or quota reset.

### Unresolved Issues

Root must await exact final CI and architect acceptance before authorized merge; live final canary after012+013 deployed. Existing test conversation has exhausted19 normal automated messages plus one terminal message, so root must use a genuine fresh authorized test checkout or request a scoped policy decision rather than reset usage.

## Architect Review

### Review Status

Accepted

### Review Notes

Defined Ready based on accepted011 and observed production defect; implementation must prove mechanism.

### Reviewed Files

Existing worker current-window loader and host currentCustomerMessages seam read.

### Validation Reviewed

None

### Architecture Conformance

Background application authority; no Shared business policy.

### Follow-up

Root normal execution path.

### Superseding latest-only and moderation authority contract

Root normal launcher claim9920931cdfe11cc68b192f60dccffe4dcf9b3771 established canonical implementation base68fd; active attempt continues. Actual oldcategory inbound17:25 Nov14 and newdetail01:02 Nov15 remain within stale pending boundary7h36 apart. No time-threshold heuristic is needed: ONLY final server-ordered raw customer row is current objective. Every preceding current-burst row is preserved intact as moderated lower-trust priorcontext together with intervening human history, chronological merge/dedup/bounds20messages/32000characters. This supersedes earlier multi-current-objective permission; genuine earlier fragments may resolve pronouns/continuations, never become independently reanswered objectives. No pending state mutation or deleted history.

Root owns context boundary/history helper, RECOVERY_INSTRUCTIONS latest-only/concise guidance, moderation-turn-gate and tests. Existing moderation gate ANY-pending-allowed is insufficient: classify allpending rows forhistory as before and retry on any not-ready classification, but authorization MUST follow the latest raw candidate only. A blocked/unsupported latest cannot resurrect older allowed content as objective or trigger basketfallback from that older approval. Preserve raw source identity/order; no selecting latest ALLOWED row. Use one shared APPLICATION helper for deterministic effective timestamp/audio readiness vs createdAt plus stable identity tie-break, consistently in objective partition and moderation. Prior-window boundary must include intervening human history based on effective latest-ready chronology. Test audio-created-earlier/completes-later and tiedtimestamps explicitly; no Sharedcontract or databasefield invented.

Tests must prove older allowed+latestblocked/unsupported NOagent/fallback/send, any unreadyclassification retainsretry, oldcategory+newdetail sends only newdetail, earlierburstcontext preserved forpronouns, historicalassistant notobjective, exact current raw input unchanged and stale/control/lease protections retained. Application guidance may request atmosttwo focused sentences for currentobjective; task013 separately owns deterministic400captionpolicy, no overlapping sourcefile edits. Root implements012; specialist owns013newhelpers/composition. Each branch independently commits/tests, finalsource synchronization coordinated.

### Independent exact-source review checkpoint

Reviewed exactb8e6f9281c8693baf0e840e94955451afa7f1c99 PR237/report98c861bb6. No source finding remains: objective selects final raw server-ready candidate before contentALLOW, preceding pending rows preserved as moderated bounded history, latest blocked/unsupported cannot resurrect earlier allowed input, any pending retry remains retry. App effective-ready timestamp/createdAt/id comparator used consistently; optionalanchor includes equal-effective sent predecessor. Historical DB candidate limit remains existing20 creation/id before readinessmerge, not universal allhistory scan. No time heuristic/state mutation/Sharedchange.

Reviewed synthetic baseline7fail/19pass against correction28pass and expanded76focus/24checkout/158lifecycle/156host/PG13/typesbuildlint evidence; original stale checkoutrefresh multi-objective mock corrected only to assert earlierhistory/latestcurrent. Normal claim992/dedicated mirroredisolation/recursiveDB evidence retained. Actualsource worktree clean. Both exact remote runs43663406439/43663402091 are still running at this checkpoint, so review remains Pending; no acceptance/completion until terminalgreen. Root post012+013 deployment genuinecanary remains separate, no usage reset permitted.

### Final independent acceptance

Accepted exactb8e6f9281c8693baf0e840e94955451afa7f1c99 PR237/report98c861bb6. Prior exactsource review9d1d3883c retained, no sourcefinding. Independently verified both exacthead CI43663406439/43663402091 completedSUCCESS (4550tests/402files rootlogreceipt), finaltypes/build/lint0 andPG13 reviewed. Baseline targeted regression7fail confirms mechanism; correction latest-only objective/moderation and chronology tests pass. Original firstCI stale checkoutfixture failure preserved and fixed without runtimeguard change.

Normal launcher claim992/canonical mirrored isolation/synchronization/recursiveDB evidence reviewed. No customerhistory deletion, unsafecontextpromotion, firstallowed fallback or timeheuristic; earlier pending/human context preserved in bounded history, stable latest readiness identity authoritative. No Shared/provider/budget changes. Complete implementation only; root012+013 deployment/drain/genuinecanary remains outstanding, no production efficacy claim. Root owns source/parentmerge/liveoperations; no merge byarchitect.

### Actual source integration receipt

Root merged PR237 acceptedb8e6f92 to actualBackground79cee094e0e0b7bd0bd6959a5ae46dc72755a93e; tree equality independently verified. Parent1057gitlink records actualmergedmain; root owns recordmerge/deployment/genuinecanary, no liveoperation byarchitect.
