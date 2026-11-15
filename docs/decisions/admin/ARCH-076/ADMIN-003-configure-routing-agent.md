---
id: ARCH-076-ADMIN-003
architecture_id: ARCH-076
title: Configure the independent routing agent
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: [ARCH-076-BACKGROUND-004]
created: 2026-11-15
updated: 2026-11-15
---

# Configure the independent routing agent

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Manage routing-agent attributes through existing platform configuration.

## Context

15 November user-selected design retains five explicit sender entities plus the R15 evidence amendment. Sender attribution and conversation-credit renewal are independent streams. The user has authorized implementation of this reviewed design. Preserve prepared claims; execute only through the owning task launcher and accepted dependency frontier.

## Scope

Register recovery.routingAgent with Admin editor, validated references, CAS/audit, preview and focused component/PostgreSQL checks.

## Out of Scope

Other repository implementation, live settings, production migration and activation. Sender tasks must not implement allowance renewal; allowance tasks must not implement sender allocation. The SYSTEM-TEST task is deferred at the user's request.

## Requirements

- [x] Publish routing revisions in the existing PLATFORM prompt lineage with sourceContextJson purpose RECOVERY_ROUTING, using existing revision/hash/auth/CAS/audit machinery without ordinary autoactivation.
- [x] Configure only recovery.routingAgent.promptRevisionId; leave normal CommerceAgentConfiguration activePromptRevisionId/promptEditVersion unchanged. Reject routing-tagged revisions in normal Commerce activation and require the tag/PUBLISHED/platform scope on router activation.

- [x] Use existing PlatformConfiguration versioned JSON; no new agent table or mutation of ordinary CommerceAgentConfiguration pointers.
- [x] Validate enabled/model binding/published platform prompt revision/threshold/budgets/retries/history and candidate limits/decision lifetime/template audience; no hardcoded business defaults.
- [x] Reuse existing model catalogue provider parameters/reasoning and protected credential resolver; prohibit credentials in JSON/browser/logs.
- [x] Before shop proof require platform-available model and neutral context; optional verified-shop inheritance resolves only actual proven shop.
- [x] Save complete valid config; missing/invalid config disables semantic selection and uses neutral clarification, never arbitrary model defaults.
- [x] Snapshot config version, model editVersion and prompt ID/hash per request; validate JSON references at save and use (they are not DB foreign keys).

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

- [x] Publish routing revisions in the existing PLATFORM prompt lineage with sourceContextJson purpose RECOVERY_ROUTING, using existing revision/hash/auth/CAS/audit machinery without ordinary autoactivation.
- [x] Configure only recovery.routingAgent.promptRevisionId; leave normal CommerceAgentConfiguration activePromptRevisionId/promptEditVersion unchanged. Reject routing-tagged revisions in normal Commerce activation and require the tag/PUBLISHED/platform scope on router activation.

- [x] Use existing PlatformConfiguration versioned JSON; no new agent table or mutation of ordinary CommerceAgentConfiguration pointers.
- [x] Validate enabled/model binding/published platform prompt revision/threshold/budgets/retries/history and candidate limits/decision lifetime/template audience; no hardcoded business defaults.
- [x] Reuse existing model catalogue provider parameters/reasoning and protected credential resolver; prohibit credentials in JSON/browser/logs.
- [x] Before shop proof require platform-available model and neutral context; optional verified-shop inheritance resolves only actual proven shop.
- [x] Save complete valid config; missing/invalid config disables semantic selection and uses neutral clarification, never arbitrary model defaults.
- [x] Snapshot config version, model editVersion and prompt ID/hash per request; validate JSON references at save and use (they are not DB foreign keys).

## Validation

- [x] Test routing draft/publish/configure leaves normal effective model/prompt and pointer versions unchanged; reject tagged normal activation and untagged/draft/foreign router activation; concurrent normal/router publication preserves both references.

- [x] Admin unit/component tests for full editor, authorization, CAS, invalid scope/model/prompt and secret exclusion.
- [x] Disposable PostgreSQL save/audit/conflicting update tests and preserved normal commerce agent settings.

Inspect the repository package.json before selecting actual commands. Required disposable PostgreSQL checks are task-local repository checks, not execution of the deferred system-test task. No live customer/provider calls belong to these checks.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set review, return the Completion Report and STOP. Do not execute another task or deploy.

## Implementation Notes

Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Completion Report

### Status

Ready for Review — ARCH-076-ADMIN-003, attempt 1, codex.

### Files Changed

- Platform Configuration registry/service/repository/mutation and protected page/actions.
- New routing-agent contract, reference validation, dedicated prompt publication and purpose discriminator.
- New routing fields/editor/preview; normal Agent Instructions routing-revision exclusion.
- Task-local PostgreSQL runner, policy/component/integration tests and normal-agent source-contract regression assertion.
- `docs/arch076-routing-agent-policy.md`; task-scoped package scripts.

### Work Completed

- Complete deployment-scoped `recovery.routingAgent` JSON with explicit enabled state, fixed-platform or verified-shop-only model binding, exact prompt revision, neutral audience, confidence, budgets, retries, input/history/candidate limits, decision TTL and retention. No business defaults or reset.
- Existing model catalogue retains provider parameters/reasoning; no copied credential material. Fixed models require enabled PLATFORM availability. Inherited binding has no fabricated pre-proof shop/model.
- Save-time references are checked inside existing serializable policy CAS/audit transaction. Prompt purpose, scope, published state and SHA-256 are required; normal active pointer reuse is refused. Strict unknown fields include prototype-named JSON keys. Invalid historical routing JSON is suppressed before browser display.
- Dedicated immutable routing instructions use existing PLATFORM lineage and existing audit, locked latest-revision CAS, `sourceContext={purpose:"RECOVERY_ROUTING",schemaVersion:1}`. Publication does not save/enable policy and never writes normal Commerce configuration. Normal editor history, draft seeds, update/publish/activation exclude routing-tagged revisions.
- Protected SUPER_ADMIN editor provides explicit blank controls, separate prompt publication/review, no-send preview, field errors and stale-write refresh. Existing normal model/prompt pointers remain unchanged.
- Background-owned per-request snapshots and use-time validation are documented handoff requirements: config version, model editVersion and exact prompt ID/hash. They are not implemented in Admin or replaced by inference.

### Validation Results

All final checks passed on combined source including accepted ADMIN002 main `5558daadddfdc4a420e300cfb348a2b2eb109812`.

- `node scripts/test-unit.mjs tests/unit/arch076-routing-agent.test.ts tests/unit/arch076-routing-agent-components.test.tsx tests/unit/arch043-platform-configuration-contracts.test.ts tests/unit/arch043-platform-configuration-components.test.tsx tests/unit/agent-instructions.test.ts tests/unit/agent-instruction-actions.test.ts tests/unit/arch076-router-template.test.tsx tests/unit/arch047-template-wrappers-components.test.tsx`: 47/47 passed.
- `node scripts/test-arch076-routing-agent-postgres.mjs`: 3/3 passed. Runner created a private loopback disposable pgvector/PostgreSQL17 database, applied existing recorded migrations and removed its container. Tests cover dedicated routing publication/hash/audit/CAS; normal editor fallback without an active pointer; concurrent policy CAS/audit; environment isolation; forbidden prompt/model/scope/privilege references with no writes; normal Commerce settings preservation.
- `npm run lint`: passed, zero errors; existing database/eslint.config.mjs anonymous-default-export warning only.
- `npm run build`: passed, production route output generated; existing BullMQ dynamic import/optional Valkey warnings only.
- `npx tsc --noEmit`: passed. `git diff --check`: passed.
- Earlier validation exposed host ENOSPC and Docker WAL I/O failure; root recovered generated build/cache space and restarted Colima. Final checks passed after recovery. Earlier fixture omissions (deployment environment and forbidden immutable-audit cleanup) were corrected before the passing PostgreSQL run.
- No external database, customer, Meta/model call, live configuration, package publication, deployment or deferred SYSTEM-TEST execution.

### Execution and VCS Evidence

Prepared launcher packet `/tmp/arch076-admin003-prepared.json` supplied canonical topology; no claim/startup redo.

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Dedicated parent: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-076-ADMIN-003`; implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-076-ADMIN-003`.
- Both branches: `task/ARCH-076-ADMIN-003`. Shared checkouts not switched/mutated; no other task worktree reused.
- Packet parent/implementation remote task fast-forward: not-needed; origin/main incorporated: already-current. Prepared claim `52ea62404f4e0a518feb78809d2e364ba96533a6` preserved.
- Packet recursive submodule sync/update passed; database recorded pin `2e14f8668346dfc135aa12f8d1fbc94e05c12ce7`, unchanged.
- Parent origin/main merged after approved definition amendment (through `85d28ddfa`); implementation merged accepted ADMIN002 main before combined regression checks.
- Implementation commits `92251ca` and `b625fdb` (plus merge of accepted main); pushed task branch. Implementation PR: https://github.com/kodjobaah/moda-interact-admin/pull/103. No main merge/push or parent submodule gitlink staged by this agent.

### Post-review Merge Evidence

Root reports bounded root and independent architect acceptance. Root merged Admin PR103 to actual implementation main `e4e4b0a2b5400f5cb7a49014dae17f3822eb1cd2`. This repository agent fetched the actual merge and verified that its Git tree and tested task HEAD `b625fdb82523481983773f390572bc34a8010a28` both equal `acbe7cfd5f8eba0e942a4637f987d499cb1a4af7`; the implementation-versus-merged-main diff is empty. The passing final validations above therefore cover the merged implementation tree without redundant reruns.

Parent task branch incorporated current `origin/main` before this evidence update. Root/moda_architect retains authority for the durable Accepted review, automatic completion/active-claim clearing and final Admin submodule pin. This agent leaves task status `review` and does not edit Architect Review, main or gitlinks.

### Deviations

Parent-approved dedicated purpose-tagged routing publication was formalized in the task/architecture amendment before review. Uses actual Prisma JSON field `sourceContext`; no new table or Shared release.

### Assumptions

Runtime validation/snapshotting and protected credential resolution belong to BACKGROUND-004; Admin owns authoring and save-time validation. Neutral ROUTER template publication remains ADMIN002.

### Unresolved Issues

None in this task's bounded implementation. Runtime rollout remains coordinator-owned and must verify test before production.

### Architectural Concerns

None. Routing and allowance renewal remain separate.

## Architect Review

### Review Status

Accepted — root and independent moda_architect review, 15 November 2026

### Review Notes

Accepted complete Admin-owned implementation: strict complete policy, serializable reference/CAS validation, independent routing publication and normal-agent isolation. All mandatory checks passed on the exact source tree merged to Admin main e4e4b0a2b5400f5cb7a49014dae17f3822eb1cd2. Automatic completion clears active claim fields; attempt 1 and its historical claim evidence are preserved.

### Reviewed Files

PR103 contract, prompt publisher/references, policy repository/mutation/service, normal Agent Instructions isolation, protected actions/editor, tests and task evidence.

### Validation Reviewed

47 focused checks, 3 disposable PostgreSQL checks, lint, typecheck, production build and identical tested/merged Git trees, as recorded above.

### Architecture Conformance

Conforms within Admin ownership. Routing remains separate from allowance renewal and no Shared release is required.

### Follow-up

Before live routing activation, complete the owning Commerce Studio guard against routing-tagged revisions being selected as normal Commerce prompts. Runtime per-request snapshots and use-time validation remain BACKGROUND-004. SYSTEM-TEST remains user-deferred.


### 15 November definition amendment

This is a new independently scoped definition, not implementation evidence. No runtime source or migration has been implemented. User has authorized implementation; runtime acceptance and rollout verification remain pending.
