---
id: ARCH-076-ADMIN-002
architecture_id: ARCH-076
title: Publish a dedicated tenant-neutral routing template
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 25
executor: codex
claimed_at: 2026-11-15T12:57:28Z
attempt: 1
depends_on: []
enables: [ARCH-076-BACKGROUND-004]
created: 2026-11-15
updated: 2026-11-15
---

# Publish a dedicated tenant-neutral routing template

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinated by `moda_architect`. This task owns the Admin authoring/publication boundary; BACKGROUND-004 owns runtime selection and neutral sending.

## Objective

Allow a platform administrator to author, review and activate an independent neutral ROUTER template for questions whose merchant is not yet proved.

## Context

The live ambiguity message is hard-coded, while ordinary AI/HUMAN/SHARED layouts can require a merchant identity, customer or checkout. Borrowing such a layout before merchant attribution either leaks a tenant or refuses the send. The product owner requires a separate Admin-editable neutral template and the normal shop layout only after a shop is established.

The current database stores `WhatsAppConversationWrapperActiveSlot.audience` as String varchar(24). Admin owns its authoring audience union and publication controls. Shared 6.1.0's prepared projection reader and renderer do not select an audience. Its ordinary `chooseSlot` and `validDefinition` deliberately accept only SHARED/AI/HUMAN: preserve that boundary. This task needs no database migration or Shared release.

## Scope

- Extend Admin-owned authoring audience types, family/audience selector, draft operations, variable palette, examples and read-only/detail/coverage labels with `ROUTER`, displayed as “Router — before a shop is selected”.
- Extend `src/lib/admin/whatsapp-templates/wrappers/{contracts,eligibility,reads,service,repository,preview}.ts` and existing authoring/compilation/publication actions only as needed to persist and activate that exact audience.
- Keep `MODA_CONVERSATION_WRAPPER`, prepared schema version 1, immutable source/locale hashes, review records, active-slot edit-version CAS, authorization and audit mechanisms.
- Reuse the existing translation/review workflow and normal supported locales. No live translation, publication, activation or Meta call occurs during implementation validation.
- Update relevant unit/component and disposable PostgreSQL authoring/publication tests, operator documentation and declared scripts where required.

## Out of Scope

Sender inventory, billing/allowance renewal, merchant identity matching, routing-model decisions, provider dispatch, changes to Shared ordinary audience policy, schema migration, live credentials/settings or Meta registration. No second template engine or hand-built runtime projection format.

## Requirements

1. ROUTER is an Admin application-owned persisted audience. The browser may select it only through authenticated existing template actions. Super-admin mutation/read rules, current environment isolation, review and source immutability stay unchanged.
2. A ROUTER definition uses exactly one `response.body` slot in body. Static neutral header/footer text is allowed. Reject all `variable` nodes in every section, checkout conditionals, `productImage`, `compositeProfile` and composite hashes, and any required customer/shop/checkout binding. Never silently strip unsafe nodes on save, compile, review or activation. No logo or shop masthead is implied by selecting ROUTER.
3. Reuse the existing prepared compiler/hash format: audience remains on the definition, not a new Shared prepared JSON field. Read/preview checks inspect the actual compiled projection as well as authoring input so a tampered persisted payload cannot bypass the neutral rule.
4. Ordinary SHARED/AI/HUMAN authoring, common-layout projection, renderer and publication retain their behavior. ROUTER does not require the SHARED composite profile. Do not label ROUTER as AI or pass it into Shared's ordinary audience selection to obtain acceptance.
5. Fix the Admin publication/reads fallback explicitly: ROUTER selects only its own active slot. No ROUTER→SHARED/AI/HUMAN fallback; ordinary source precedence stays unchanged. Missing ROUTER is visibly “Not configured”. A configured invalid/retired/unreviewed/hash-mismatched ROUTER definition is visibly refused, never shown as absence or replaced with another audience.
6. Use existing locale review/publication eligibility, source hash/content hash, actor identity and edit-version checks. Concurrent activations CAS the same ROUTER slot. Activating ROUTER cannot mutate or deactivate SHARED, AI or HUMAN. Record normal bounded audit provenance.
7. The preview shows platform-neutral static outer copy plus an illustrative routing question. It loads no shop, customer, basket, media or checkout. Explain that merchant-specific text/media appear only after verified shop selection, through that shop's normal AI/SHARED path. The editor must not suggest inserting raw placeholders as a way around restricted variables.
8. Runtime safety remains Background-owned: ADMIN-002 validates allowed structure and publication; BACKGROUND-004 also rechecks the neutral projection and outer static copy against its proved candidate identity scope. This task must not claim arbitrary administrator text can be automatically proven tenant-neutral without runtime checks.

## Work Items

- [x] Add isolated ROUTER authoring, labels, restricted palettes and neutral preview.
- [x] Apply restrictive compiled-projection validation and independent publication/read selection.
- [x] Preserve immutable review/hash/CAS/audit behavior and all ordinary audience regressions.
- [x] Run focused component/unit and disposable PostgreSQL checks plus repository-required lint/type/build checks; publish both task branches and report.

## Interfaces / Contracts

Persist existing `WhatsAppTemplateDefinition.kind='MODA_CONVERSATION_WRAPPER'`, `audience='ROUTER'`; active slot key is exactly `ROUTER`. Reuse existing prepared schema version 1, `readPreparedWrapper` and `renderPreparedWrapper` structural machinery from the published Shared package. The normal Shared `WrapperAudience`, `WrapperSource`, `chooseSlot` and `validDefinition` are not widened.

Background's application-owned selector will read only ROUTER for neutral scope and revalidate the published definition/locale/hash/slot provenance. It will render with no tenant/customer variables, no media and checkout unavailable. No new queue or public API payload is introduced.

## Dependencies

None. The existing wrapper tables and varchar audience field support this task independently of ARCH-076-DATABASE-001; no schema or consumer pin change is required.

## Enables

- ARCH-076-BACKGROUND-004 consumes the independent published ROUTER slot.
- ARCH-076-SYSTEM-TEST-001 remains manual-gated and is not executed in this user-authorized cycle.

## Acceptance Criteria

- [x] A real Admin component/action round trip saves, reviews and activates a valid neutral ROUTER source with immutable prepared hash and independent slot.
- [x] Every variable category, conditional, product/composite media option, raw placeholder and tampered compiled projection is rejected with actionable UI feedback, without silently rewriting source.
- [x] Missing and refused ROUTER are distinct; neither falls back to normal audiences. Normal SHARED/AI/HUMAN selection still works with a ROUTER row present.
- [x] Lower roles, stale source/locale review, retired definition, incorrect hashes, stale edit version and concurrent activations cannot mutate the wrong slot.
- [x] Preview uses no merchant/customer/media query and no remote provider call; labels/documentation accurately describe neutral scope.

## Validation

Inspect the implementation worktree's actual package scripts before running them. Extend the existing template authoring/compilation/wrapper publication unit and component suites. Extend the existing disposable PostgreSQL wrapper-publication harness for ROUTER isolation, actual source→projection→review→slot CAS, concurrent activation and tampering. Run declared relevant lint, typecheck and production build; `git diff --check`. Record exact commands/results, baseline warnings and invocation-owned database cleanup. Do not call production or run the deferred SYSTEM-TEST task.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation pass, set the task to review, commit/push implementation and parent task-report branches, return to `moda_architect` and stop. No main merge, live activation or follow-on task.

## Implementation Notes

Executing prepared attempt 1 on the launcher-resolved mirrored task worktrees. The launcher claimed the task as codex and synchronized both branches; no claim or startup work was repeated. Application policy remains in Admin and the existing prepared compiler/hash/rendering machinery is reused.

## Completion Report

### Status

Ready for Review. Implementation committed and pushed as `4bfefc5d1e20bb41c65a0d0dcce90c8a7e05e3f5`; [Admin PR #102](https://github.com/kodjobaah/moda-interact-admin/pull/102). Neither task branch has been merged by the repository agent.

### Files Changed

- Admin-owned authoring types, validation, registry, draft operations, preview, immutable projection verification and bounded coverage reads under `src/lib/admin/whatsapp-templates/authoring/`.
- Existing compilation preview/read integration in `compilation/{reads,wrapper-compiler}.ts`.
- Wrapper contracts, eligibility, neutral preview and publication reads; new application-owned `wrappers/router-policy.ts` and `wrappers/slot-resolution.ts`.
- Existing authoring/catalogue/detail/review/coverage and wrapper publication components under `src/components/admin/whatsapp-templates/`.
- `tests/unit/arch076-router-template.test.tsx`, existing wrapper component tests, `tests/integration/arch047-template-wrappers.postgres.test.ts`, wrapper PostgreSQL harness and its declared unit script in `package.json`.
- Operator instructions: `docs/testing/arch076-neutral-router-template.md`.

### Work Completed

- Added exact persisted audience `ROUTER` with “Router — before a shop is selected” authoring/publication labels, restricted palette and neutral examples. Audience selection preserves incompatible content for explicit correction; no save/compiler/review/activation silently removes it.
- Reused the existing schema-1 wrapper compiler and immutable source/content digests. Admin admission rejects variables in every section, raw placeholders, conditionals, product/composite media, composite hashes, extra fields and incorrect response-slot placement/count. Frozen review and activation inspect actual prepared payloads as well as authoring.
- Added pure bounded slot resolution: ROUTER only resolves its own pointer; missing and configured-but-refused states remain distinct. Ordinary SHARED/AI/HUMAN precedence is retained and a ROUTER row cannot displace their bounded coverage reads.
- Reused existing SUPER_ADMIN authorization, all-20-locale immutable review gates, serializable edit-version CAS and bounded audit. The real disposable PostgreSQL case drives English save, 19 translation review approvals, ROUTER activation/replacement race, wrong-role refusal, audit and tampered-projection refusal while asserting normal slots are unchanged.
- Preserved Shared's ordinary audience selection and existing published dependency (actual Admin pin is 6.0.1). No Shared source/release, schema change, live configuration, provider send or deferred system-test execution.
- Runtime static-copy identity-scope checks remain BACKGROUND-004-owned; Admin does not claim to prove arbitrary text tenant-neutral.

### Validation Results

- Relevant authoring/compilation/translation/wrapper unit and component aggregate: 91 checks passed during implementation; subsequent final targeted regressions passed, including the additional immutable-review/neutral-preview case.
- Final `npm run test:arch047-admin-wrappers:unit`: **13/13 passed**, including six ROUTER policy/preview/read tests.
- Final `npm run test:arch047-admin-authoring:unit`: **41/41 passed**.
- Compilation/translation/component focused command through `node scripts/test-unit.mjs` (router, wrapper components, authoring components and compilation suites): **33/33 passed**.
- Final `npm run test:arch047-admin-wrappers:postgres`: **4/4 passed**, applying the recorded database migrations to an invocation-owned disposable pgvector/PostgreSQL 17 container. Final cleanup succeeded; no wrapper fixture container remains.
- `npm run lint`: passed, zero errors; existing `database/eslint.config.mjs` anonymous-default-export warning remains. `npx tsc --noEmit`: passed.
- Final `npm run build`: passed completely after Prisma generation, webpack compilation, TypeScript, static-page generation and build tracing. Existing BullMQ dynamic dependency and optional `@valkey/valkey-glide` warnings remain.
- `git diff --check` and staged diff check: passed.
- Resolved validation prerequisites: the old wrapper PostgreSQL runner selected tsx/CommonJS conditions incompatible with existing import-only Shared exports. It now bundles local TypeScript as ESM, matching the existing unit-runner approach. Its old SHARED fixture was also corrected to the current common-layout shape and coordinator-authorized transaction port; no production activation rule was weakened.
- A repeat build and PostgreSQL attempt were interrupted by host ENOSPC/containerd I/O failures. Heavy work was paused; root recovered generated cache space and Docker, including removal of the invocation-owned residual container. The final build and complete PostgreSQL suite were rerun successfully after clearance.

### Git / VCS

- Mirrored branch: `task/ARCH-076-ADMIN-002`.
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-076-ADMIN-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-076-ADMIN-002`.
- Prepared packet `/tmp/arch076-admin002-prepared.json`: created dedicated worktrees, dependency gate passed with no dependencies, remote task FF not-needed and origin/main already-current in both histories. Canonical root was not derived from a previous task worktree.
- Prepared parent/main head: `41d383094b07e4f4d6ad9e0fd34c88bd75170fd7`; implementation start/main: `beb082cd4c6f813de560fd723d951ac84b01ac4a`.
- Durable prepared claim: `f1a415e453bcce4c42b8955d08e2891b18d069f0`, codex attempt 1. Claim/startup work was not repeated.
- Recursive database pin `2e14f8668346dfc135aa12f8d1fbc94e05c12ce7`: initialized at recorded commit, recursive sync/update passed in preparation, unchanged by this task.
- Implementation commit `4bfefc5d1e20bb41c65a0d0dcce90c8a7e05e3f5`, pushed to `origin/task/ARCH-076-ADMIN-002`; Admin PR #102.
- Parent task/report publication: this report's task-branch commit, with exact final SHA supplied in the coordinator handoff. Only this task file is staged; no implementation gitlink is staged.
- Shared/default checkouts switched or mutated for task work: no. Other task worktree reused: no. Main merges/pushes: none.

### Deviations

No architectural deviation. Corrected the obsolete DATABASE-001 dependency body to match the independent, already-authorized empty frontmatter gate. Repaired the relevant existing PostgreSQL harness and stale fixtures so current behavior is actually verified.

### Assumptions

Administrators review authored static router copy and all locale text. Background independently revalidates runtime projection and static outer copy against its routing identity scope. A live ROUTER template must be reviewed and activated through the normal Admin workflow before runtime routing is enabled; this implementation makes no live activation.

### Unresolved Issues

None for this task. ARCH-076-SYSTEM-TEST-001 remains pending and was not executed. Live rollout/activation remains coordinator-owned.

### Architectural Concerns

No Shared release or database migration is required. ADMIN-003 platform-configuration work remains separate and was not edited.

## Architect Review

### Review Status

Accepted — automatic completion, 15 November 2026.

### Review Notes

Root architectural review accepted source commit 4bfefc5d1e20bb41c65a0d0dcce90c8a7e05e3f5 (Admin PR102), merged as actual Admin main 5558daadddfdc4a420e300cfb348a2b2eb109812. Independently fetched the merge and compared Git trees: both e7ade8d406a8ee5549141cfa23675732036089f5; implementation versus merged-main diff is empty. Prepared canonical worktree/attempt1 synchronization and recursive Database pin evidence are recorded above. Preserve executor/claimed_at/attempt as accepted execution history. No live configuration or provider activation was performed.

### Reviewed Files

Actual application-owned wrappers/router-policy.ts and slot-resolution.ts; root accepted authoring/compiler immutable projection guards, neutral preview/palette components, wrapper activation/read integration, ROUTER unit/component cases and disposable PostgreSQL publication case. Existing Shared prepared schema remains unchanged; ordinary slot selection remains independent.

### Validation Reviewed

Completion Report final results: wrapper unit13/13, authoring41/41, focused compilation/components33/33, disposable PostgreSQL4/4; lint, TypeScript, full production build and diff checks passed. Final tests ran after host space/Docker recovery; interrupted earlier attempts do not substitute for those successful final results. Existing documented build warnings are not introduced behavior. No redundant test rerun on the identical accepted merge tree was necessary.

### Architecture Conformance

Conforms to ADMIN002 scope: dedicated ROUTER audience, exactly one response.body, no tenant/checkout variables or media, independent pointer without normal fallback, published immutable locales/hashes/CAS/audit/SUPER_ADMIN authorization. No Shared release or schema change. Runtime static-copy identity leak checks remain Background-owned.

### Follow-up

BG004 remains Pending because BG003 and ADMIN003 are not Complete. This acceptance alone does not promote it. SYSTEM-TEST remains user-deferred. Production/test activation and runtime verification remain root-owned after remaining implementation and test-first rollout requirements.
