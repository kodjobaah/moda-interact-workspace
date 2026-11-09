---
id: ARCH-066-COMMERCE-003
architecture_id: ARCH-066
title: Remove template and sender validation from Studio outreach preview
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-SHARED-016"]
enables: []
created: 2026-11-09
updated: 2026-11-09
---
# Remove template and sender validation from Studio outreach preview

## Objective
Remove template/WABA validation from Studio initial-outreach preview. Use the existing selected template content/bindings directly with Shared's preview-only renderer. This separate correction owns removal of the SENDER_UNAVAILABLE stub and template/sender prerequisites; COMMERCE002 retains all remaining unfinished host/evaluator/lifecycle work. Never mark002 Complete merely because this correction passes.

## Exact touch points
`package.json`/lock: exact016 artifact/integrity. `lib/preview/initial-outreach-runtime.ts`: remove unconditional sender-unavailable refusal; no sender-identity read/decryption. `src/commerce/preview/initial-outreach/{contracts,presentation,service,ports}.ts`: renderer dependency uses renderStudioInitialOutreachPreview; add NEW `template-reader.ts` for existing template content. `lib/preview/initial-outreach-http.ts` and existing collection/status/cancel routes: preserve selected-shop authorization and request schema. `src/studio/test-conversations/initial-outreach-preview-panel.tsx`: show source template/locale and final text; label “Template validation not evaluated. No message sent.” Existing initial-outreach service/UI fixtures and NEW `tests/arch066-initial-outreach-template-reader.test.ts`. Resolve actual existing configuration reader symbol by inspection and record path; no parallel configuration store. No Admin/Background/Shared source edits.

## Source selection and data mapping
Use existing selected-shop assigned initial template and existing locale-resolution precedence already implemented by Background's configuration reader, read-only; document actual reader/query path before editing. Filter for selected shop and evaluated initial purpose (no offer/code/automatic). Do not filter on Meta approval/status, registration submission state, enabled registration, configured sender/WABA, drift/category/hash/fingerprint. Use configured template assignment and stored locale component/binding snapshot; missing stored content returns typed configuration TEMPLATE_UNAVAILABLE, never fabricate components. Preserve established locale precedence; ties at the same precedence refuse AMBIGUOUS_TEMPLATE rather than choose an arbitrary row. Do not infer sender from assignment. Map existing definition/locale IDs, languageTag, componentsSnapshot and parameterBindingsSnapshot into Shared StudioOutreachTemplateSchema. No extra Meta lookup/revalidation/register/send. Current shop authorization and approved ready media access remain host data boundaries; these are not template approval checks.

## Runtime correction boundary
Delete imports/calls/readers for messaging.sender, messaging.senderIdentity, sender projection version checks and production selectRecoveryAssignment/renderInitialOutreachPreview from this preview path. Wire presentation to public renderStudioInitialOutreachPreview with actual stored template/facts, existing saved-brand data and ready media. No dummy WABA, approved status, hash or registration creation. Use production-independent template result type and NOT_EVALUATED marker. Keep same-origin/SUPER_ADMIN/tenant/checkout checks, live product evaluator, cancellation/budget/storage checks and no-side-effect rules. Missing template/content/variables yields precise refusal, not generic sender-unavailable. If genuine evaluator host integration is still unavailable, expose that specific configuration failure and retain002 incomplete; injected simulation never becomes default live service.

## Required tests/review
Prove preview with stored template works without messaging.sender/projection and with mocked non-approved/stale-hash metadata: metadata must not enter renderer input or gate result. Assert zero sender-secret, sender-projection, Meta/registration/send accesses. Missing components and unresolved placeholders refuse precisely; cross-shop selection remains rejected before I/O. Compare parameters/full body to016 and Background's identical valid-content golden; preserve both-platform checkout live reads and no mutation spies. Run existing `tests/arch066-initial-outreach-preview.test.ts`, `tests/arch066-initial-outreach-store.test.ts`, `tests/arch066-initial-outreach-ui.test.tsx` plus new reader tests via Vitest, production typecheck and changed-file ESLint. Report actual remaining002 gaps explicitly.

## Coordination handoff
At review, architect removes SHARED014 and ADMIN001 sender prerequisites from COMMERCE002 and records this correction's accepted source/artifact;013/014/Admin001 are unnecessary for Studio and their historical reports are preserved. Do not execute those tasks or claim they are completed. Existing Background production renderer/send validation stays unchanged. This task does not depend on blocked002 (avoids cycle); reuse its published partial source via normal main/task integration only, record exact baseline and preserve its work. Keep task Pending until016 Complete and partial002 source available on canonical implementation baseline; no cherry-pick selected unreviewed files silently.

## Execution and completion boundary
Definition only. Preserve unrelated work; you are not alone in the codebase. Use canonical launcher task worktrees and mirrored task branches. Record exact source, commands/results and package integrity; submit for review, stop and retain developer completion authority. No main merge/push, deployment, real customer send, Meta call, database mutation in a hosted environment or follow-on task execution is authorized. No acceptance from tests against injected simulation alone.

## Completion Report
Not started. No implementation or validation performed.
