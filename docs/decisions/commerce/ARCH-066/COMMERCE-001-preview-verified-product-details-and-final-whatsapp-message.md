---
id: ARCH-066-COMMERCE-001
architecture_id: ARCH-066
title: Preview verified product context and final WhatsApp message
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-066-SHARED-010", "ARCH-066-MCP-001"]
enables: ["ARCH-066-COMMERCE-002", "ARCH-066-SYSTEM-TEST-001"]
created: 2026-11-08
updated: 2026-11-08
---
# Preview verified product context and final WhatsApp message

## Objective and read first
Implement only the owned work below. Read `docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md` first: its numbered contract decisions are normative and must not be redesigned by the implementor.

## Touch points
`package.json`/lockfile; `src/commerce/preview/{types,service,tool-activity,product-discovery-instructions}.ts`; `src/commerce/preview/product-reads/{shopify-core,ports,registrations}.ts`; `src/commerce/integration/preview/{adapters,runtime}.ts`; Studio `src/studio/test-conversations/{contracts,client,conversation-panel,test-conversation-view-types,test-conversations-screen}.tsx/ts` as existing file extensions dictate; existing preview Redis store/finalization and wrapper database readers; NEW `src/commerce/preview/{product-context,presentation}.ts` and `src/commerce/integration/preview/whatsapp-wrapper-reader.ts`.

## Exact work
- Mirror MCP provider field mapping and validation using the exact published Shared schemas (not imported MCP source). Adopt public context reducer and pure composer, no Background cross-repository imports.
- Extend Redis conversation payload with optional typed productContext defaulting empty for old snapshots. Merge only successful validated observations and commit atomically with terminal conversation history under existing run fencing. Preserve separate-record storage caps/TTL/purge and activity accounting; no new global mutable cache. References never bypass current grant/provider checks.
- Select live current deployment AI wrapper via read-only existing DB slot/locale definitions using the same Shared pure selection logic as Background. Compose synthetic preview wrapper context using selected tenant's saved brand/language and fixture customer firstName 'Test customer'; no checkout URL by default, checkoutAvailable false. A synthetic context is explicitly labelled Preview context in UI. Checkout-specific preview is outside this task; no customer/outreach records are created.
- Validate prepared projection/contentHash exactly as production before composing. Pin wrapper definition/locale/hash/edit version with each run result; no active slot -> explicit unwrapped preview; configured-invalid -> show refusal. Never read another environment via browser parameters.
- Store bounded `whatsappPreview` per completed run: kind ready/refused; ready body<=4096, wrapper provenance or null; refused bounded reason. Retain raw runner reply separately as 'Agent output' diagnostics. Default conversation assistant bubble shows final composed WhatsApp text; preserve raw view behind collapsed details. Distinguish formatting preview from moderation/delivery approval; no claim message was sent.
- For host verification reuse pure projection rules in Shared; re-fetch selected product/option/offer when production requires it, charge actual calls to existing budgets and display activity. Do not invent a cheaper preview-only verification path. Any production DB-only admission not evaluated is displayed explicitly rather than falsely marked compatible.
- Followup 'yes' without product identity asks clarification. On sizing use exact current-shop references, never guess numeric IDs from title/position. Keep existing price/stock/discount safety and model choice.

## Acceptance / validation
- [ ] Multi-message fixture matches Background common fixture; options present/missing/partial; stale/wrong-shop refs rejected; unchanged legacy conversation loads with empty context.
- [ ] Final WhatsApp body equals Background for same verified facts, wrapper revision, locale and context. Plain-text normalization removes Markdown markup without corrupting prices/URLs. No dangerouslySetInnerHTML.
- [ ] Oversized wrapper refuses or chooses same bounded candidate as Background; live moderation/billing/send not invoked. Configured invalid wrapper cannot silently show raw message as final.
- [ ] Existing preview/storage/purge/activity/lifecycle tests, new parity tests, production typecheck and scoped lint pass. Update `src/commerce/bootstrap/system-product-tools.ts`, its canonical product/shipping output-schema projections, the default conversational profile response details schema and the existing `scripts/sync-system-commerce-tools.mjs` publication path to include optional productOptionSelections and additive option outputs. Create new immutable revisions via the existing deterministic sync; never mutate published revisions or widen arbitrary unknown fields. Keep unchanged content idempotent; changed content receives the normal next revision/release. Record TEST dry-run/apply receipt and repeat unchanged sync proof. Existing active releases keep their old schema until the new release is activated. No live rollout in this task. Product option support is not accepted until the real default profile compiles and the published tool descriptors accept actual size outputs.

## Execution boundary
Definition only. Do not claim or implement until explicit dependency tasks are Complete. Use the canonical launcher-resolved parent and implementation task worktrees; execution_mode is agent and completion_mode remains developer. Do not change unrelated work or another repository. Record exact Shared package version/integrity, database migration and provider schema artifact used. No production customer messages, Meta registrations or live mutations are authorized by this task.

## Completion Report

### Status

Blocked — Attempt 1. Partial provider work only; not Ready for Review, not Accepted and not Complete. All acceptance checkboxes remain unchecked.

### Files Changed

Implementation `ac44a5a`: package.json, package-lock.json, src/commerce/preview/product-reads/{shopify-core,registrations}.ts, tests/arch066-provider-facts.test.ts. Parent: this task report only.

### Work Completed

Pinned exact accepted Shared5.7.0, matching integrity `sha512-2/Ew2Blo83eY/LKthULJh84kHoJfq701e3RCpjPEQNXYnSai6IEQO08n4QNct1QzwWGyNxf9M2lokLlCHKyoXg==`. Added native Shopify description/options/selected-option query projection and Woo description/short_description/attribute allowlists using published Shared normalization. Preserved parent facts and exact selected variant attributes. Added native identity, absent-product and parent-mismatch handling and focused fixture checks. No descriptors/releases were published or activated; these partial provider changes are not rollout-ready with active old strict descriptors.

### Validation Results

- `npx vitest run tests/arch066-provider-facts.test.ts tests/local-product-query-contracts.test.ts tests/local-product-woocommerce.test.ts tests/local-product-search-diagnostics.test.ts`: PASS, 4 files /20 tests, including pinned Shopify query validation and Woo HTML/native attribute fixtures.
- `npm run typecheck:build`: PASS after incomplete integration was removed; production types only. `npx prisma generate --schema database/prisma/schema.prisma` passed for the recorded nested schema.
- `npx eslint src/commerce/preview/product-reads/shopify-core.ts src/commerce/preview/product-reads/registrations.ts tests/arch066-provider-facts.test.ts`: PASS.
- `git diff --check`: PASS.
- Direct installed public-artifact check: `Object.keys(CommerceAnswerPresentationSelectionSchema.shape)` returns only productOptionSelections,responseDisposition,shippingInformationSelection. `safeParse({productDetailSelections:[{productId:'1',variantId:null}]})` returns success:false. `CommerceResponseDispositionSchema.options` returns STANDARD,OUT_OF_SCOPE_REDIRECT,SHIPPING_INFORMATION_UNVERIFIED,PRODUCT_OPTIONS; `safeParse('PRODUCT_DETAILS')` returns success:false. Both JS runtime and declarations prove the gap; initial integration compiler also reported TS2551 missing productDetailSelections. No consumer schema fork introduced.
- Provider schema artifact: Admin2026-07 from @shopify/dev-mcp1.15.4, SHA256 `2b507dc1f74c6157e0eb98500db0f3c3e238d69eaf0d98fd7657ac7ed3f6900b`.
- Existing nested database schema used at `039778a4a472db7d09e6b077bb8c8d7c82a58129`; no database migration/pin change made or needed for retained provider work.

### Unresolved Issues / Architectural Concerns

Normative consumer contract requires public productDetailSelections and PRODUCT_DETAILS in the default profile/response schema. Exact accepted5.7.0 exports the generic product facts renderer but omits those selection fields in its public commerce response schema. Adding a local field/schema would violate Shared ownership. Required owning Shared correction and accepted immutable publication must precede further consumer integration; architect must supply the new exact pin/integrity and reclaim path. Do not republish5.7.0 or weaken this acceptance contract.

Unfinished: atomic reference persistence, verified presentation/wrapper host integration, complete recommendation/shipping verification parity, final-text UI, immutable schema/profile sync, full multi-turn/storage/parity fixtures. Unfinished integration experiments were removed from published code; local recovery patch `/tmp/ARCH-066-COMMERCE-001-consumer-WIP.patch` is not completion evidence.

Developer live validation remains pending after implementation and schema correction: `npm run commerce:sync-tools -- --environment=test --dry-run`, then `npm run commerce:sync-tools -- --environment=test --apply`, then repeat unchanged dry-run/apply idempotence receipt under matching TEST configuration. Exact deployed/shared-environment execution needs explicit authorization under live-validation policy; none was attempted. No real provider/WhatsApp message, deployment or LIVE activation performed. Full existing lifecycle/storage and new parity checks remain pending, not passing by inference from the focused provider tests.

### Physical worktree / synchronization evidence

Canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace
Parent: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-066-COMMERCE-001
Implementation: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-066-COMMERCE-001
Both branches: task/ARCH-066-COMMERCE-001. Shared workspace and implementation checkouts switched/mutated for implementation: no. Another task worktree reused: no.
Launcher packet: prepared_execution true, dependency_gate passed; SHARED-005 and MCP-001 Complete. Parent reused /implementation created; both remote fast-forwards not-needed and origin/main already-current. Recursive implementation submodule sync/update passed, status ready; database `039778a4a472db7d09e6b077bb8c8d7c82a58129`. Attempt1 claim committed/pushed `c679b2b9be2e43e2728a451731ca15e5e3bda6ef`.

### Deviations / Assumptions

Stopped at a proven missing Shared public contract rather than silently creating a consumer fork. Retained only independently tested partial provider/pin work; acceptance remains incomplete and requires architect dependency disposition. No final completion decision requested or recorded.

## Release / Dependency Handoff - 2026-11-08
SHARED-003 accepted Attempt1 explicitly Complete. Pin @modainteract/moda-interact-shared exactly5.6.0; dist.integrity sha512-tDuW+C8MdteWMJWwmuFI2cTAugMejOJwTk0KkemBMwpN/lL92WPI8CX/A5dDa2nhG0RYiIeHSR490WPCrTz42w==. Downloadable archive and isolated public-import/browser checks verified in release record. Remain Pending until other explicit dependencies Complete. No claim or execution performed.

## Dependency Reconciliation - 2026-11-08
SHARED-003 and MCP-001 accepted/explicitly Complete. All explicit dependencies satisfied; Ready at unchanged Attempt0, executor/claimed_at null, no execution. Shared remains exact5.6.0; MCP implementation fd53bb52acaf6426b1a1e1793b8d4fc8ae54c2a4 published.

## Release dependency reconciliation — 2026-11-08

SHARED-005 is Complete at accepted Attempt1, with accepted immutable `@modainteract/moda-interact-shared@5.7.0` and integrity `sha512-2/Ew2Blo83eY/LKthULJh84kHoJfq701e3RCpjPEQNXYnSai6IEQO08n4QNct1QzwWGyNxf9M2lokLlCHKyoXg==` (source `09e249c5717c8866996624f8855a7d649dfd2c43`). Use this exact artifact and canonical consumer contract; never guess/latest/ranges. Remaining explicit blockers: None; every explicit prerequisite is Complete. Status Ready, unchanged Attempt0/unclaimed. No implementation, deployment or task claim is started by reconciliation.

### Execution ownership amendment — 2026-11-08

The developer explicitly authorized moda_architect to resolve synchronization and hand this task to moda_commerce for implementation, validation and publication. Agent execution is restored after mainline synchronization; explicit developer completion authority remains unchanged. Scope and dependency gates are unchanged.

## Checkout-led scope amendment — 2026-11-08

This amendment supersedes earlier standalone-production-conversation requirements, including consumer contract C1 and the standalone prerequisite reported by BACKGROUND-001. It preserves historical reports, attempts and acceptance evidence; it does not accept, complete, reclaim or start any task.

- Every production conversation in this scope originates from a real abandoned checkout/CheckoutRecovery. Initial outreach uses that checkout; subsequent CommerceAgent turns retain the same recovery identity even when discussing other products. No independent customer-start conversation, new admission/recipient/consent policy or fabricated recovery ID is required.
- Background resolves the current conversation's real CheckoutRecovery and its shop/customer through existing routing. Missing recovery or conflicting tenant/owner fails closed before model/provider I/O under existing admission rules. Preserve current consent/window/billing/outbox fences. Conversation.shopId, when populated, must agree with recovery ownership; it is not an alternate admission route.
- Studio conversational preview remains an isolated, explicitly synthetic test using its existing preview identity. Do not persist a fake production recovery/customer, weaken live MCP authorization, or add a production standalone route to accommodate preview. Initial-outreach testing remains COMMERCE-002: select an existing same-shop checkout recovery and verify its items using live product reads. Synthetic conversational preview must not claim production admission was evaluated.
- Retain generic product references, fresh authorized fact verification, shared WhatsApp composition, budgets, wrapper provenance, storage fencing and parity requirements. These apply to any merchant goods. No new table/schema is needed for standalone admission. Keep the existing ARCH-066 reference-context table and its recovery-linked owner checks.
- SHARED-007/008 and MCP-002 standalone support is withdrawn from the required acceptance/dependency path for this checkout-led scope. Any existing work is subject to review for removal of unused standalone-only identity/admission branches; do not remove existing supported recovery behaviour or rewrite immutable published artifacts. This does not withdraw SHARED-009/010's independent productDetailSelections/PRODUCT_DETAILS compatibility correction and immutable publication. Consumers must wait for that accepted correction when using those fields; do not locally fork Shared schemas.

### Mandatory review corrections

Review BACKGROUND-001 and COMMERCE-001 against this amendment before acceptance. Inspect the actual implementation and require corrections on their same task branches: remove newly introduced standalone-only routing/budget/authorization code that has no checkout-led or isolated-preview caller; retain real recovery ownership rejection; confirm product-context persistence and verified WhatsApp body composition; prove missing recovery is rejected and a later product question retains the original recovery. For Commerce also prove synthetic preview stays isolated, real-checkout outreach preview remains separate, and no fabricated production records or weakened grants were added. Preserve and re-run relevant existing tests after corrections; report exact files, package pin/integrity, call order and final body evidence. A historical standalone blocker alone is no longer grounds to reject recovery-linked behaviour. Other genuine blockers, unfinished acceptance work and manual system-test gates remain in force. Do not declare acceptance from partial provider tests.

## Architect Review
### Review Status
Changes Requested — reclaim same task at Attempt2 after shared blocker resolved.
### Review Notes
SHARED009 accepted correction and SHARED010 accepted immutable publication Complete. Use exact @modainteract/moda-interact-shared5.8.0, integrity sha512-LS6Tj4Jwsupe0qvsjcfrbt4vhGJkxfHm70bQvSbBdeOKpwsOpCoHRKvmyI4Tg4/lBDxH5QTSEF9fbGLjDnIifw==. This supersedes all earlier5.6/5.7 consumer pins. Preserve Attempt1 partial provider changes/history. Complete all unchecked original work and normative consumer contract A–C/E plus checkout-led amendment above. Use published verifyCommerceAnswerPresentationSelection before host verification; refuse mixed detail/option selections canonically. Implement atomic fenced context persistence, fresh budgeted fact/recommendation/shipping verification, wrapper provenance/refusal, final WhatsApp UI, strict descriptors/default profile publication and complete parity/lifecycle tests. Preserve synthetic preview isolation, no fake production records or standalone-only admission branches. Exact TEST dry-run/apply plus unchanged repeats are explicitly authorized by user; no LIVE activation.
### Reviewed Files
Attempt1 partial provider source/report, Shared009/010 source/release evidence.
### Validation Reviewed
Attempt1 focused provider tests; broader original required checks remain pending for Attempt2.
### Architecture Conformance
Scope unchanged except resolved dependency/pin; compatible checkout-led amendment preserved after review. completion_mode developer remains unchanged.
### Follow-up
Repository owner implements/validates/pushes both task branches and submits review; no self-completion.
