---
id: ARCH-075-ADMIN-002
architecture_id: ARCH-075
title: Coordinate approved common-layout activation
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-13T04:17:42Z
attempt: 1
depends_on:
  - ARCH-075-ADMIN-001
  - ARCH-075-BACKGROUND-002
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Coordinate approved common-layout activation

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Coordinate approved common-layout activation.

## Context

The user explicitly requires all Meta templates, AI replies and HUMAN messages to share one shop header and checkout footer, with product images separate. Existing Admin-owned SHARED wrapper definition/slot is the common immutable content authority; family-specific body/offer/opt-out content stays intact. No duplicate hardcoded frame builders.

## Scope

Existing Admin approved-source/publication preview, SHARED wrapper activation/CAS/audit and registered replacement readiness. Source capability only; no live provider publication or activation.

## Out of Scope

Other repositories, new database tables/settings, provider permissions, live registrations/activation, source merges, unapproved publication, changing billing/cap semantics, arbitrary source refactors, automatic mutation of approved templates. Background engine001 uses accepted published5.13.9 compatible readers and remains producer-disabled.

## Requirements

Use existing publication operation/target snapshots, SHARED slot version CAS and audit in bounded serializable transactions; no new setting/table. Preview exact affected active Meta stage/offer/locale/shop slots and selected common revision. Every required replacement must have provider APPROVED/content-equivalent registration and matching canonical commonRef; stale/missing locale, approval, source, active-pointer or current slot mismatch refuses activation. Do not claim cross-shop atomicity from existing per-shop operations/global SHARED slot. Before implementing, return any actual inability to coordinate global common pointer with target assignments safely. Required behavior is one reviewed common revision across newly sent Meta/AI/HUMAN, not silent mixed versions.

Source/approval workflows must keep existing Meta snapshots immutable, clone/register/review replacements; live provider submission/activation remains root-owned after concrete review. Background consumer must be deployed before selecting new projections. Existing approved outreach outside customer window remains a template send only, no new product freeform tail. Runtime mismatches fail closed before provider. Preserve compatible legacy frozen messages. Test concurrent Admin/slot/provider drift, all-or-no-switch per intended transaction boundary, idempotent replay and audit. Stop with explicit architectural gap if broader schema/contract change is necessary.

### Bounded global activation contract

Inspection found existing operations publish one definition in per-shop transactions while the SHARED pointer is global. Sequential reuse is insufficient. Use one strict Admin-local versioned coordinator snapshot in existing publication operation JSON, discriminated as `schemaVersion: 2`, `kind: COMMON_RECOVERY_ACTIVATION`. It binds the exact common reference, expected SHARED pointer/version, complete cohort fingerprint, per-definition immutable source/registration identities and reviewed shop/assignment digests, actor/reason and override acknowledgement. The coordinator may reference the common definition through the existing definition FK if schema-compatible. Existing per-definition operation/target audit records may be committed COMPLETE in the same transaction with coordinator linkage; do not duplicate the complete manifest per child or misrepresent existing counters. Ordinary v1 progress/advance must never process the v2 coordinator. Exact operation-key replay is idempotent; changed actor/fingerprint/intent refuses.

Conservative implementation bounds: at most six reviewed scenario definitions, 50 shops, 1,000 replacement locale targets and independently 1,000 currently selectable affected variants; canonical snapshot at most 1 MiB. Enumerate with limit-plus-one and refuse overflow before mutation. These are safety bounds, not measured throughput. Cover the complete globally affected selectable cohort, including exact unchanged assignments where applicable; no arbitrary subset under a global pointer. Larger cohorts require a returned architecture gap rather than partial activation.

Commit all assignments, operation/target outcomes, SHARED CAS/lifecycle and audits in one serializable transaction, with existing 30-second timeout and 10-second maximum lock wait. No network, page commits or silent automatic reconfirmation. On conflict/timeout roll back everything and require appropriate reviewed retry. Acquire one shared activation/publication advisory fence before protected reads, use consistent lock order and actual row/version checks, and include every relevant ordinary writer or equivalent proven database conflict. An advisory lock alone does not protect an uncooperative writer; root's writer audit and concurrent real-PostgreSQL tests must demonstrate coverage.

The reviewed cohort deliberately overapproximates present eligibility: include every existing enabled and APPROVED recovery variant across all WABAs and every Shop lifecycle status, including unlinked legacy variants that can become ambiguity blockers. Restricting to ACTIVE shops/current sender would permit future shop reactivation or sender rotation to expose a mixed legacy frame. Inactive shops remain inactive and no new offer eligibility is granted. Foreign-WABA, unsupported or unlinked replacement identity, incomplete mapping and bounds overflow refuse the entire operation; do not silently exclude or disable unreviewed rows. Lock/re-read affected Shop rows and exact variants/registration readiness. Privacy deletion/cascade and Background provider-status changes must serialize or cause stale/serialization refusal; no new cross-repository lock writer is needed where no assignment/pointer writer exists. Test inactive-shop and alternate-sender legacy inclusion explicitly.

Preserve historical AI/HUMAN slots. Accepted Background common mode selects a valid active common SHARED source before legacy audience overrides; show that precedence rather than deleting the older slots. Activation still requires both-environment producer rollout and drain evidence. No live action is authorized by this task.

### Explicit English Meta source review

Existing translation review excludes English, but Background requires REVIEWED for every Meta locale. Coordinated confirmation must explicitly include review of the exact English Meta compiled content/hash and APPROVED provider registration. Only for META_RECOVERY English SOURCE_SAVED, perform a conditional SOURCE_SAVED-to-REVIEWED lifecycle update with authenticated reviewer/time and existing REVIEW_WHATSAPP_TEMPLATE_LOCALE audit inside the same activation transaction. Leave AST, source/content hashes and registration unchanged. Already REVIEWED is unchanged; unexpected statuses refuse, never normalize provider readiness. Common WRAPPER English SOURCE_SAVED remains its separate canonical lifecycle. Test explicit confirmation, unchanged hashes and rollback of English review on a later cohort conflict.

Once common mode is active, ordinary assignment/publication of a stamped META_RECOVERY definition must require every Meta locale REVIEWED, including English. Otherwise refuse with explicit review/coordination guidance; generic publication must not silently perform English review. Preapproval submission/compilation may retain English SOURCE_SAVED, and legacy pre-common publication is unchanged. Test the ordinary assignment rejection independently of coordinated activation.

### Existing source catalogue gate

When common-layout mode is activated, new publication/submission of unstamped legacy saved/queued definitions must refuse with a clone-with-common-layout action. Do not retrofit current common content during an HTTP send, mutate old snapshots or silently publish duplicate versions. Active replacement cohort is reviewed from real supported scenario inventory, not merely two existing NO_OFFER definitions. Root reviews copy and coverage before external registration. Existing legacy records stay readable/cloneable and historical sends unchanged.

### Explicit live registration environment constraint

User authorizes recovery template registration in PRODUCTION Meta account only. Root then copies the approved immutable catalogue/registration metadata and referenced common source coherently to test for the same provider assets. Never initiate duplicate external registration from test. Keep local source/reference/locale identities and provider WABA/content/approval proof consistent; no fabricated approval or source-hash rewrite. Actual callback/status environment routing must be verified before claiming live ordered test processing: copied provider metadata alone does not prove delivery callbacks reach the test database. Root owns every live registration/copy/activation action after concrete review.

## Work Items

- [x] Complete assigned bounded capability only.
- [x] Prove compatibility and meaningful negative/failure behavior.
- [x] Submit mirrored branch/report and stop.

## Interfaces / Contracts

Common content authority: selected immutable Admin SHARED wrapper revision and locale projection. Shared owns canonical semantic key/wrapper validation; Admin owns authoring/compiler/reference/activation; Background owns tenant-derived values, frozen rendering, sending and current fences. Existing template registration hashes remain authority for provider components.

## Dependencies

ARCH-075-ADMIN-001, ARCH-075-BACKGROUND-002

## Enables

Only explicitly promoted dependent tasks after acceptance.

## Acceptance Criteria

- [x] One common content source is used without duplicated formatting or unauthorized semantic widening.
- [x] Old stored projections/registrations remain readable and immutable; new fields do not grant tenant/provider authority.
- [x] Assigned validation and isolated mirrored synchronization evidence are complete.

## Validation

- [x] Actual PostgreSQL coordinated activation, stale source/slot/approval/locale and concurrent conflict/replay tests.
- [x] Declared relevant tests/types/lint/build and exact-head CI; no live registration mutation.

## Stop Condition

After required work and validation, submit review and STOP. No enabled-task execution, merge, live mutation or unapproved public release.

## Implementation Notes

You are not alone; preserve other changes. Canonical prepared packet is startup/isolation authority. Report actual cross-owner gaps rather than inventing a setting/schema or weakening strict validation.

## Completion Report

### Status

Ready for architect review. Implementation committed and pushed; local validation and exact-head supplementary checks complete. Source capability only. No live registration, activation, template copying, deployment, provider request or browser-origin workaround was performed.

### Files Changed

- `common-activation/{contracts,preview,gates,service}.ts`: versioned coordinator contract, bounded complete-cohort preview, source/workflow gates and one transaction.
- Protected common-activation page, server actions and review panel; wrapper navigation and dynamic coverage precedence.
- Existing publication assignment/confirmation, Meta submission/technical retry and wrapper activation adopt the common advisory fence and source gates.
- Publication binding validator admits canonical `shop.websiteUrl` without widening unknown keys.
- Focused unit and disposable PostgreSQL activation fixtures, native ESM test runner entry and package scripts. Existing wrapper/Meta mocks gain explicit advisory-lock collaborators while retaining every existing authorization, collision and audit assertion.

Exact owned-path inventory: `/tmp/admin002-owned-files.json` (22 files).

### Work Completed

One global SHARED pointer cannot be safely changed through existing independently committed per-shop publication pages. Returned that concrete gap before implementation. Architect approved a bounded coordinator using existing PublicationOperation JSON (`schemaVersion:2`, `kind:COMMON_RECOVERY_ACTIVATION`), with per-definition child operations and ordinary locale targets committed COMPLETE in the same transaction. No new database table, enum, setting or per-shop pointer was introduced. V1 publication readers refuse v2 records; the specialized coordinator verifies exact request/actor/fingerprint on replay.

Bounds are six replacement definitions, 50 shops, 1,000 replacement locale targets, 1,000 existing enabled+APPROVED variants, and 1 MiB snapshot. These are refusal bounds, not measured capacity guarantees. The transaction uses Serializable, maxWait10s/timeout30s, without provider I/O, page commits or blind retry. Row-lock reads are bounded, including at most 1,000 old plus 1,000 replacement registrations. Global advisory lock precedes ordinary assignment/SHARED publication reads. Exact row/version checks remain authoritative for external status and privacy changes.

The preview conservatively includes enabled+APPROVED assignments across ALL shop statuses and WABAs, including unlinked ambiguity blockers. Excluding inactive shops or previous senders would let later reactivation/rotation expose mixed frames. Foreign/unlinked/unsupported or incomplete cohorts refuse; no arbitrary subset, silent disable, new offer eligibility or invented assignment. Target and personalized-greeting semantics must match exactly. Old and proposed media roles are explicitly reviewed. All 20 canonical common references, source/locale hashes, approved content-equivalent registrations, recent provider reconciliation, pending observations, current assignment facts and SHARED version are re-read before any changes.

Empty exact Meta cohorts are supported: the reviewed SHARED pointer can change for recovery AI/HUMAN without creating Meta assignments or offers. Existing AI/HUMAN audience pointers remain historical; the accepted Background common-recovery path takes precedence. Admin coverage now reflects that precedence.

Architect-approved English Meta lifecycle correction is explicit: confirmation reviews the exact English content/hash and APPROVED provider registration; the same transaction CASes only META_RECOVERY English SOURCE_SAVED to REVIEWED, adds authenticated reviewer/time and the existing review audit. JSON, source/content hashes and registration snapshots remain unchanged. Already REVIEWED is retained; unexpected statuses refuse. Common WRAPPER English SOURCE_SAVED remains unchanged. Ordinary common-mode assignment also requires every Meta locale REVIEWED; it cannot silently normalize English. Submission/preapproval staging remains allowed with SOURCE_SAVED English.

Unstamped saved/queued definitions refuse new submission/publication in common mode with clone-with-common-layout guidance. Generic SHARED activation cannot introduce or replace a common revision outside coordinated activation, including a retired current common source. Historical definitions/registrations remain readable and cloneable; no send-time retrofit or provider approval fabrication.

### Validation Results

- Native ESM full unit suite: 788/788 PASS.
- Focused activation + existing wrapper/Meta suites: 14/14 PASS.
- Final TypeScript: PASS (`npx tsc --noEmit`).
- Disposable PostgreSQL: 2/2 PASS. Real transactions cover late-audit rollback (including English review), concurrent confirmation, stale source/locale/approval/assignment refusal, provider pending observations, inactive/foreign cohorts, replay/collision, generic workflow gates and empty-cohort pointer-only activation.
- Scoped new-file lint: PASS. Declared full lint: PASS (zero errors; one existing nested Database default-export warning).
- Security/observability: `npm test` passed 331 with three initially skipped build-dependent observability tests; after successful build, those three passed 3/3 with zero skips. All 334 distinct checks passed.
- Production build (`npm run build`): PASS.
- `git diff --check`: PASS.
- No GitHub Actions workflow is configured. Exact-head Preview Comments and supplementary Vercel checks: PASS (root verified on source `98c86f334cbc04edbad5f27895e2722c8d86b9d8`).
- Browser visual verification: not performed; no screenshot or visual-pass claim. Live Admin origin remained explicitly denied and was not accessed by another origin/API/CLI workaround.

All checks run with sanitized environments and localhost dummy URLs or a uniquely named disposable PostgreSQL database. A synthetic AUTH_SECRET supplies test-only policy signing; no live database or credentials used.

### Deviations

The initial focused suites exposed new mandatory advisory-lock collaborators missing from old fake transactions. Added explicit lock SQL assertions and absent SHARED state; no production bypass or weakened existing assertion.

The initial PostgreSQL fixture reused a synthetic provider ID between original and replacement definitions, correctly violating `(wabaId,providerTemplateId)` uniqueness. Changed synthetic identity to derive from definition and locale. The dependent empty-cohort version assertion remained unchanged. Final rerun results are reported separately above.

Child runtime could not write the canonical sibling worktree. Authored exact file payloads in `/tmp/admin002-files`; root mechanically applied them only in the canonical worktree and executed validation. No alternate checkout, source-main mutation or escalation workaround was used.

### Assumptions

Live activation requires root to verify accepted compatible Background producer is Live and predecessor instances drained in both environments. The explicit Admin confirmation records that operational assertion; source code cannot independently prove fleet state. Provider approval and copied metadata alone cannot prove correct webhook environment routing.

### Unresolved Issues

Live production registration, coherent test catalogue copying, callback routing, compatible-producer rollout/drain, reviewed activation and genuine ordered-message proof remain root-owned operational work. This task performs none of them. Provider template eligibility, including final dynamic parameter constraints, remains subject to real Meta approval; local compile success is not approval.

### Architectural Concerns

Outside-writer audit found no runtime Variant/ActiveSlot writer outside Admin. Shopify privacy Shop deletion cascades variants; lock/recheck affected Shop rows. Background updates registration readiness, so row locks/current reconciliation and pending observations are included. No external application advisory-lock change was required. Broader-than-bounded cohorts refuse rather than claim cross-shop atomicity from old per-shop operations.

### Physical Worktree Isolation

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-ADMIN-002`, branch `task/ARCH-075-ADMIN-002`.
- Implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-ADMIN-002`, same task branch.
- Prepared packet `/tmp/moda-arch075-admin002-prepare.json`: prepared_execution true, claim attempt1 codex, commit `1bcb1b09770c67255e53742deccc86568cb5a6f6`.
- Parent remote-task fast-forward not-needed; origin/main incorporated yes; recorded prepared head `4ddc361f33a52a4c8876d78fcdf392190862b6a3`.
- Implementation remote-task fast-forward not-needed; origin/main already-current; base `73831bb661731bc6d7dd478475ea7acad1ffc4dd`.
- Recursive submodule sync/update passed; Database `5329d5390d346042895219663f3a040ea54ae168`.
- Shared/default checkout switched or mutated: no. Other task worktree reused: no. Startup/claim repeated: no.

### Source Checkpoint

- Source commit: `98c86f334cbc04edbad5f27895e2722c8d86b9d8` (pushed; implementation worktree clean).
- Draft source PR: https://github.com/kodjobaah/moda-interact-admin/pull/90.
- Parent completion report commit: recorded by final submission.
- Root owns merges; no main merge or force-push by this agent.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual source review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
