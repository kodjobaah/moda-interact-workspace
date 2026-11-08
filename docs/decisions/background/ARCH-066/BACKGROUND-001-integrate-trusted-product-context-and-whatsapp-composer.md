---
id: ARCH-066-BACKGROUND-001
architecture_id: ARCH-066
title: Integrate product context and the shared WhatsApp composer
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: in_progress
priority: 50
executor: codex
claimed_at: 2026-11-08T19:46:00Z
attempt: 2
depends_on: ["ARCH-066-DATABASE-001", "ARCH-066-SHARED-005", "ARCH-066-MCP-001", "ARCH-066-SHARED-010"]
enables: ["ARCH-066-BACKGROUND-002", "ARCH-066-SYSTEM-TEST-001"]
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

### Status

Blocked — Attempt 1 implementation published; standalone host execution cannot satisfy the normative contract with the published required recovery identity. Unaffected recovery-linked context, fresh facts and shared composition work is implemented and validated. Awaiting moda_architect disposition; no acceptance or completion decision made by moda_background.

### Implementation and artifacts

- Implementation commit: `4664ea89daad920a2704dc9f0db11a201910a939`, pushed to `moda-interact-background` branch `task/ARCH-066-BACKGROUND-001`.
- Exact Shared package: `@modainteract/moda-interact-shared@5.7.0`; lock integrity `sha512-2/Ew2Blo83eY/LKthULJh84kHoJfq701e3RCpjPEQNXYnSai6IEQO08n4QNct1QzwWGyNxf9M2lokLlCHKyoXg==`. Canonical provider output, product reference and presentation schemas are imported from this immutable artifact; no local substitute schema or package edits.
- Database submodule pinned to accepted `b7f58d5a93e41d54b2fd92a5d483aec4c2c5b595`. Migration `20261108173000_arch066_conversation_product_context/migration.sql` SHA256 `3e99659d71c8e1d5933a95ad933a10bffea03bd25395795cc8de704f27ff686a`.
- `product-context-repository.ts`: canonical recovery/standalone owner validation, exact Conversation row lock, inbound version fencing, canonical equal-version idempotency without TTL extension, revision CAS, competing-insert conflict, UTF8 and PostgreSQL storage bounds, expiry and safe cache-failure logging.
- `host.ts`, `presentation.ts`, agent types and observation timestamp: typed reference context is separate from moderated history, passed to Shared runner; fresh exact authorized product reads share runner usage/deadline, feed canonical fact verifiers and return strict presentation/update metadata. Factual details bypass purchase/discount/URL recommendation authority. Canonical owner conflict and unsupported standalone fail before model/provider work.
- Recommendation and wrapper pure modules delegate to Shared. Wrapper service owns the single Shared composer invocation inside existing applicationKey/replay handling; persisted replay skips recomposition/context writes. Processor writes references only after successful composition and repeats control/inbound fences before existing moderated delivery. HUMAN/manual, outbox/billing and initial template paths retain their boundaries.

### Validation

- `npm run build`: passed (Prisma client generation, both TypeScript projects and existing template packaging).
- `npm run test:commerce-host`: final 73/73 passed, using actual Shared runner and loopback MCP. New cases prove canonical-owner rejection, standalone fail-closed, fresh product detail reads, no recommendation/discount authority and no required purchase URL for factual answers.
- `npm run test:commerce-recommendations`: 20 files / 201 passed, including recommendations/shipping/discount, host diagnostics, MCP/evidence and existing initial-outreach regressions. Old fixture provider IDs were made canonical; forged-input assertion now checks the published runner's safe referral and zero provider I/O rather than obsolete fatal-input behavior.
- `vitest run src/commerce/presentation.test.ts`: final 10/10 passed; canonical selection validation, exact pair authorization/freshness, refusal priority, ambiguity/mixed selection rejection, missing-fact limitation and Shared composer golden/boundary fixtures. Migrated render/shipping regression plus helper: 15 passed.
- `node scripts/test-arch066-product-context-postgres.mjs` (exposed as `npm run test:arch066-product-context:postgres`): disposable PostgreSQL fixture 6/6 passed. Exact accepted migration applied only to isolated fixture parent-key tables; actual observed row-lock wait and inbound-version race, concurrent insertion, canonical equality/unchanged expiry, CAS, ownership, malformed/expired/oversize data and technical failures exercised. Fixture container removed; no shared/live database migration.
- Wrapper + processor + HUMAN focused suite: 6 files / 110 passed. Final affected adapter/processor assertions: 76 passed, including immutable provenance, replay/no update, refused composition/no write, STALE/CONFLICT suppression, SKIPPED behavior and post-write inbound fence suppression.
- `vitest run tests/unit/services/conversation-moderation tests/unit/services/recovery-billing.service.test.ts tests/unit/services/recovery-billing tests/unit/services/conversation-turn-processor.service.test.ts`: 16 files / 204 passed.
- `npm run lint`: fails with exactly one existing error in untouched `src/providers/shopify-whatsapp-consent.provider.ts:151` (`no-control-regex`). File diff against launcher implementation baseline `7c162e5b28cedc7c185421b55db6dc4bdd6c3013` is empty. No corresponding baseline ID exists in `docs/development-baseline.md`; this is reported as an observed existing failure, not claimed as a documented exemption. ESLint across all changed source/test/script scopes passed. `git diff --check` passed.

### Unresolved standalone prerequisite

Published Shared5.7.0 `dist/response-DFDEw4K0.d.ts:65–72` requires `CommerceTurnIdentitySchema.checkoutRecoveryId` as a string; runner/MCP assertion identity therefore cannot express a truly standalone conversation. Background `src/commerce/live-budget.ts:9,78–83` likewise requires recoveryId; `whatsapp-conversation-routing.service.ts:175–176` returns CONTEXT_REQUIRED without recovery; `whatsapp.worker.ts:256–298` derives ownership/recipient from recovery and requires it; `recovery-agent-context.service.ts:108` named standalone helper still loads a supplied recovery. Existing canonical Conversation shop/customer relations do not resolve this cross-service identity/admission contract. No fabricated recovery IDs, customer facts or new recipient/consent policy were introduced. Required correction: architect-owned additive standalone Shared identity/assertion contract and release, MCP authorization consumption, then bounded Background admission/budget/context integration. Standalone execution acceptance remains unmet; no main merge, deployment, live provider/model call, customer/Meta send or follow-on execution.

### Prepared execution provenance

Launcher packet `/private/tmp/arch066-background001-prepared.json`: primary root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-066-BACKGROUND-001` reused; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-066-BACKGROUND-001` created. Mirrored branch `task/ARCH-066-BACKGROUND-001`; parent baseline `678d0cdc5380e78a87c5b05148138a2f6f3d756b`, implementation baseline `7c162e5b28cedc7c185421b55db6dc4bdd6c3013`. Both startup fast-forwards not-needed/main already-current; recursive submodule sync/update passed at database `039778a4a472db7d09e6b077bb8c8d7c82a58129`. Dependency gate all Complete. Claim `4dfeb84d02baca22436da26a5c278cd82bb19cf5`, executor codex at `2026-11-08T18:29:15Z`; Attempt1 unchanged, active claim cleared on blocked return. Source and assigned report only published; parent implementation gitlink not staged.

## Release / Dependency Handoff - 2026-11-08
SHARED-003 accepted Attempt1 explicitly Complete. Pin @modainteract/moda-interact-shared exactly5.6.0; dist.integrity sha512-tDuW+C8MdteWMJWwmuFI2cTAugMejOJwTk0KkemBMwpN/lL92WPI8CX/A5dDa2nhG0RYiIeHSR490WPCrTz42w==. Downloadable archive and isolated public-import/browser checks verified in release record. Remain Pending until other explicit dependencies Complete. No claim or execution performed.

## Current additive-release gate (supersedes earlier consumer pin)
Pending scope now includes generic descriptions/attributes and therefore depends on SHARED-005, not the original5.6.0 release. Pin exactly the version/integrity recorded by SHARED-005 after acceptance. Earlier5.6.0 handoff is historical and must not satisfy this amended task. No attempt/claim started; MCP readiness returns to Pending until new prerequisite is Complete. Implement [consumer contract](../../../architecture/ARCH-066-consumer-contract.md) as normative.

## Deterministic implementation checklist
- [ ] Apply consumer contract C/D in order. product-context-repository.ts implements exact read/write signatures and lock/CAS/idempotency algorithm; fixtures cover recovery-linked identity, missing-recovery rejection, expiry, same-version conflict and out-of-order turns.
- [ ] host.ts passes context/platform into runner and passes successful context metadata to presentation.ts. Presentation helper validates both old/new selection details, performs counted fresh exact reads, builds published presentation schema and never trusts model-supplied facts.
- [ ] Existing wrapper service/service.ts and compose-ai-outbound.ts remain the one persisted AI composition boundary. Pass envelope+verified projection through existing pipeline; call Shared composer once inside wrapper application handling, preserving applicationKey/replay. Remove only migrated pure duplicates; keep MANUAL semantics and historical records.
- [ ] Read brand from Shop.brand.brandName; locale from existing committed conversation policy; trusted checkout variables remain production host-owned. No title/domain-derived brand or new fallback contact.
- [ ] Persist context only after presentation success, before handing final body to existing delivery orchestration, using dedicated short transaction. DB SKIPPED log does not create additional send or override send fence. Assert current version again at existing delivery gate.
- [ ] Add tests src/commerce/product-context-repository.test.ts and presentation.test.ts using disposable Postgres for actual row-lock/CAS race (in-memory mocks insufficient for lock claim), plus host/wrapper integration tests proving no double-wrap, final-body moderation and same-version replay. Record migration commit/hash, artifact integrity and exact commands.

## Release dependency reconciliation — 2026-11-08

SHARED-005 is Complete at accepted Attempt1, with accepted immutable `@modainteract/moda-interact-shared@5.7.0` and integrity `sha512-2/Ew2Blo83eY/LKthULJh84kHoJfq701e3RCpjPEQNXYnSai6IEQO08n4QNct1QzwWGyNxf9M2lokLlCHKyoXg==` (source `09e249c5717c8866996624f8855a7d649dfd2c43`). Use this exact artifact and canonical consumer contract; never guess/latest/ranges. Remaining explicit blockers: None; every explicit prerequisite is Complete. Status Ready, unchanged Attempt0/unclaimed. No implementation, deployment or task claim is started by reconciliation.

## Execution Ownership Amendment — 2026-11-08
Developer explicitly requested `/moda-task ARCH-066-BACKGROUND-001` agent implementation and authorized sync plus claim/source/review publication. Canonical explicit dependencies all Complete, Ready Attempt0/unclaimed; implementation worktree absent, no existing source edits to checkpoint. Delegate to moda_background through canonical preparation; completion_mode developer retained and exact consumer contract unchanged. No live/customer/Meta/main/follow-on execution.

## Architect Review — Attempt1 (2026-11-08)
### Review Status
Blocked — canonical standalone identity/private admission prerequisite missing; not Accepted.
### Review Notes
Inspected published partial source4664ea89daad920a2704dc9f0db11a201910a939 and reportdce85f846776d413afdf47b1c726369493152f80. Valid cache/verified presentation/shared-composer integration retained; no fake recovery or unsafe fallback. Actual standalone conversational execution cannot satisfy normative C1 under published5.7: CommerceTurnIdentitySchema.checkoutRecoveryId required string; live-budget.ts input/output recoveryId required; whatsapp-conversation-routing.service.ts:175–176 denies non-recovery CONTEXT_REQUIRED; whatsapp.worker.ts:256–298 derives tenant/recipient/context solely from recovery and requires it; recovery-agent-context.service.ts:108+ named standalone helper still loads recovery. Existing canonical Conversation.shop/customer relations alone do not supply a valid Shared turn/assertion/budget contract. Acceptance remains incomplete, no integrated runtime completion claimed.
### Reviewed Files
product-context-repository.ts and actual PostgreSQL fixture; presentation.ts and golden/delegate tests; host/history and wrapper/processor composition paths; package/DB pin; precise Shared/worker/router/budget/helper evidence. Read normative consumer C/D and actual production code.
### Validation Reviewed
Actual disposable PostgreSQL6/6 including observed pg_stat_activity row-lock wait/inbound advancement, competing inserts, canonical equality/no TTL extension, revision CAS, ownership/expiry/bounds passed. Host73/73, recommendations201, presentation10, wrapper110/final76, moderation/billing/processor204 passed. Build (Prisma/both TypeScript projects/template artifact) and changed-scope lint passed. Full lint fails one untouched baseline-identical src/providers/shopify-whatsapp-consent.provider.ts:151 no-control-regex; not silently fixed or claimed passed. Real Shared runner/loopback fresh-facts verification uses2reads without discount/purchaseURL gating. Unit evidence does not prove absent standalone pipeline.
### Architecture Conformance
Partial code preserves canonical owner/version lock/CAS, Shared validation/UTF8+SQL storage bounds, post-composition context timing/send recheck, single durable wrapper application/replay/moderation, fresh counted facts and existing send/billing/consent fences. Shared pure duplicates delegated; no copied generic logger/validator. Exact5.7 artifact and accepted cache migration pin recorded. No live provider/model/customer/Meta/main/activation/schema edits.
### Follow-up
New architect definitions SHARED007 Ready (canonical standalone identity/admission scope), SHARED008 Pending publication, MCP002 Pending private standalone verification. Background remains Blocked on published contract/private ingress gates, same Attempt1/history/branches retained, claim cleared. After gates Complete, reclaim same task to adopt corrected package and implement existing canonical standalone loader/router/general budget/context path with explicit owner/customer/consent fixtures; never fabricate recovery/checkout facts. No follow-on implementation launched. System Tests remain terminal/manual-gated.

## Checkout-led scope amendment — 2026-11-08

This amendment supersedes earlier standalone-production-conversation requirements, including consumer contract C1 and the standalone prerequisite reported by BACKGROUND-001. It preserves historical reports, attempts and acceptance evidence; it does not accept, complete, reclaim or start any task.

- Every production conversation in this scope originates from a real abandoned checkout/CheckoutRecovery. Initial outreach uses that checkout; subsequent CommerceAgent turns retain the same recovery identity even when discussing other products. No independent customer-start conversation, new admission/recipient/consent policy or fabricated recovery ID is required.
- Background resolves the current conversation's real CheckoutRecovery and its shop/customer through existing routing. Missing recovery or conflicting tenant/owner fails closed before model/provider I/O under existing admission rules. Preserve current consent/window/billing/outbox fences. Conversation.shopId, when populated, must agree with recovery ownership; it is not an alternate admission route.
- Studio conversational preview remains an isolated, explicitly synthetic test using its existing preview identity. Do not persist a fake production recovery/customer, weaken live MCP authorization, or add a production standalone route to accommodate preview. Initial-outreach testing remains COMMERCE-002: select an existing same-shop checkout recovery and verify its items using live product reads. Synthetic conversational preview must not claim production admission was evaluated.
- Retain generic product references, fresh authorized fact verification, shared WhatsApp composition, budgets, wrapper provenance, storage fencing and parity requirements. These apply to any merchant goods. No new table/schema is needed for standalone admission. Keep the existing ARCH-066 reference-context table and its recovery-linked owner checks.
- SHARED-007/008 and MCP-002 standalone support is withdrawn from the required acceptance/dependency path for this checkout-led scope. Any existing work is subject to review for removal of unused standalone-only identity/admission branches; do not remove existing supported recovery behaviour or rewrite immutable published artifacts. This does not withdraw SHARED-009/010's independent productDetailSelections/PRODUCT_DETAILS compatibility correction and immutable publication. Consumers must wait for that accepted correction when using those fields; do not locally fork Shared schemas.

### Mandatory review corrections

Review BACKGROUND-001 and COMMERCE-001 against this amendment before acceptance. Inspect the actual implementation and require corrections on their same task branches: remove newly introduced standalone-only routing/budget/authorization code that has no checkout-led or isolated-preview caller; retain real recovery ownership rejection; confirm product-context persistence and verified WhatsApp body composition; prove missing recovery is rejected and a later product question retains the original recovery. For Commerce also prove synthetic preview stays isolated, real-checkout outreach preview remains separate, and no fabricated production records or weakened grants were added. Preserve and re-run relevant existing tests after corrections; report exact files, package pin/integrity, call order and final body evidence. A historical standalone blocker alone is no longer grounds to reject recovery-linked behaviour. Other genuine blockers, unfinished acceptance work and manual system-test gates remain in force. Do not declare acceptance from partial provider tests.

## Architect Checkout-Led Unblocking — 2026-11-08
Developer explicitly withdrew standalone production objective and superseded SHARED007/008/MCP002. Authorized task-owned checkout-led amendment above adopted unchanged. Standalone missing-recovery behavior is now required fail-closed, not an architectural blocker. Remove withdrawn standalone prerequisites from acceptance/dependency path; retain independent product-detail correction SHARED010 (canonical Complete), no guessing package pin or source schema fork. Ready at prior Attempt1, claim remains null; historical blocked report preserved, no new claim/source edits/acceptance/completion.

Next authorized same-task review/rework must inspect actual code for unused standalone-only routing/budget/auth branches and remove only those with no checkout-led/isolated-preview caller, preserve real recovery owner/consent/send fences, verify product references/fresh facts/composer/replay/CAS and later product question retaining original recovery, exact accepted product-detail artifact pin and relevant tests. Full-lint baseline issue and any genuine unfinished integration requirement remain honestly recorded; scope withdrawal alone is not passing acceptance. No Shared008 publication, main/live/customer/follow-on execution.
