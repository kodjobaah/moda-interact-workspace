---
id: ARCH-066-BACKGROUND-001
architecture_id: ARCH-066
title: Integrate product context and the shared WhatsApp composer
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-DATABASE-001", "ARCH-066-SHARED-003", "ARCH-066-MCP-001"]
enables: ["ARCH-066-SYSTEM-TEST-001"]
created: 2026-11-08
updated: 2026-11-08
---
# Integrate product context and the shared WhatsApp composer

## Objective and read first
Implement only the owned work below. Read `docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md` first: its numbered contract decisions are normative and must not be redesigned by the implementor.

## Touch points
`package.json`/lockfile and database submodule; `src/commerce/{host,history,recovery-instructions,referral}.ts`; `src/commerce/recommendations/{observations,render,messages,candidates,shipping,disposition}.ts`; `src/services/conversation-wrappers/{service,render,selection,projection,contracts,compose-ai-outbound}.ts`; `src/services/conversation-turn-processor.service.ts`; existing scoped host/wrapper integration tests. NEW `src/commerce/product-context-repository.ts` and `src/commerce/presentation.ts`.

## Exact work
- Read/write context row by tenant+conversation using decision 6. Load only unexpired valid Shared payload; invalid payload logged and ignored. Pass only reference context to runner. Once successful current-turn product results arrive, merge through Shared reducer; commit update with decision 6 version fencing. Failed/cancelled/stale turns never overwrite newer context. First version starts without a row; no historical text parsing/backfill.
- `history.ts` keeps moderated text and separate typed context; do not embed product IDs by modifying customer-visible replies. Product detail calls revalidate current provider state for sizes/prices/offers. Ambiguous references prompt clarification, not guessed IDs. Inputs absent from prior context may be resolved by fresh search as usual.
- Preserve existing host offer verification, current product re-fetch, availability/URL purchase-readiness gates, shipping trust, budget, language and moderation. Produce host-verified projection for shared composer; model details are requests, never render facts. Options must match refreshed exact parent/variant result before rendering.
- Replace local pure recommendation/wrapper implementations with imports/delegates to Shared presentation; delete unused duplicate pure code only after call sites/tests move. Keep Prisma slot/context readers, tenant admission, prepared wrapper hash validation, replay/applicationKey generation, moderation, outbox, billing and sender in Background. The existing wrapper service invokes the shared pure selection/render primitives; it still owns persisted delivery evidence.
- Support plain factual size answer without forcing product purchase proposal or discount when unrelated. Never auto-select a variant from just 'yes'. Use host-known saved brand name; default we/our, not a domain-derived name.
- Render outcome/refusal and context log events use IDs/codes/counts only. No raw customer text, tool bodies or model reasoning. Initial outreach Meta registration/approved template remains unchanged; this task affects conversational reply composition only.

## Acceptance / validation
- [ ] Conversation: discover three shirts -> yes -> sizes uses verified IDs or asks which shirt; listed sizes exactly provider values; no stale price evidence reuse.
- [ ] Deleted product -> corrective search -> useful ANSWER possible; DENIED still referral; no size data -> truthful limitation; no unauthorized recommendation.
- [ ] DB CAS race, stale inbound turn, duplicate delivery and wrapper replay tests pass. Golden composer fixtures match Studio fixture inputs byte-for-byte.
- [ ] Existing commerce-host suite, recommendation/shipping/discount, wrapper/moderation/outbox/billing tests plus typecheck/lint pass. No real WhatsApp sends.

## Execution boundary
Definition only. Do not claim or implement until explicit dependency tasks are Complete. Use the canonical launcher-resolved parent and implementation task worktrees; execution_mode and completion_mode are developer. Do not change unrelated work or another repository. Record exact Shared package version/integrity, database migration and provider schema artifact used. No production customer messages, Meta registrations or live mutations are authorized by this task.

## Completion Report
Status: Not started. Attempt: 0. Implementation commit: none. Validation evidence: none. Remaining work: all unchecked acceptance criteria. Document isolated worktree, package, test and deployment evidence when implemented; do not mark Complete merely from source inspection.

## Release / Dependency Handoff - 2026-11-08
SHARED-003 accepted Attempt1 explicitly Complete. Pin @modainteract/moda-interact-shared exactly5.6.0; dist.integrity sha512-tDuW+C8MdteWMJWwmuFI2cTAugMejOJwTk0KkemBMwpN/lL92WPI8CX/A5dDa2nhG0RYiIeHSR490WPCrTz42w==. Downloadable archive and isolated public-import/browser checks verified in release record. Remain Pending until other explicit dependencies Complete. No claim or execution performed.
