---
id: ARCH-066-SHARED-002
architecture_id: ARCH-066
title: Extract the pure WhatsApp response composition contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-066-SHARED-001"]
enables: ["ARCH-066-SHARED-003"]
created: 2026-11-08
updated: 2026-11-08
---
# Extract the pure WhatsApp response composition contract

## Objective and read first
Implement only the owned work below. Read `docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md` first: its numbered contract decisions are normative and must not be redesigned by the implementor.

## Scope and touch points
Own new `src/commerce/presentation/` and package browser-safe export `@modainteract/moda-interact-shared/commerce/presentation`. Sources to port, not import across repositories: Background `src/commerce/recommendations/{render,messages,money,candidates,shipping}.ts` and `src/services/conversation-wrappers/{contracts,render,selection,projection}.ts`.

## Exact work items
- Implement architecture decisions 4 and 5. Export `composeCommerceWhatsAppPreview(input)` returning `{kind:'ready',body,candidates,wrapper:{definitionId,localeId,contentHash,slotEditVersion}|null}|{kind:'refused',reason}`. Input is validated final envelope + host-verified presentation projection + locale + saved brandName + prepared wrapper selection/context. No Prisma, server-only, service imports, fetch, Redis or Meta SDK in this export.
- Preserve existing deterministic recommendation price/offer/currency/localization behavior and three-candidate shortening. Add deterministic option lines: every option name followed by supplied values; partial lists explicitly labelled incomplete. Variant selectedOptions never imply availability for other combinations. Missing options says details unavailable, never invent S/M/L or colours.
- Port pure prepared wrapper rendering and slot/locale selection with existing rules unchanged. Preserve 4096 UTF-16 code-unit bound for complete conversational text including wrapper; preserve zero/one/multiple response-slot rejection, control character rejection, conditional checkout omissions and already-wrapped checks. Context, slot, hashes and provenance are passed by trusted hosts.
- Keep persisted wrapper application digest/replay ownership in Background. Shared returns no send authorization. No active wrapper => explicit unwrapped result; configured invalid wrapper => refusal, never raw passthrough.
- Make general model reply formatting WhatsApp-compatible by deterministic plain-text normalization (decision 4), not HTML injection or Markdown-to-HTML. Provide the same string for Studio display and Background delivery.
- Port all existing supported-language catalogue entries without losing locales; add translated option/unavailable/partial labels in that same catalogue. No untranslated English fallback over an existing resolved locale.

## Acceptance / validation
- [x] Golden fixtures compare legacy deterministic product/offer/shipping/wrapper outputs byte-for-byte except the deliberately specified new option/plain-text formatting cases.
- [x] Boundary tests 4096/4097 including wrapper, Unicode, multiline replies, **bold**, ~~sale~~, links, malicious HTML displayed as inert text, wrapper missing/configured-invalid, locale fallback, checkout unavailable.
- [x] Import built export in Node and browser-like runtime with no server dependencies. Preserve production moderation/send ownership. Typecheck, lint, build and package export tests pass. No publication here.

## Execution boundary
Definition only. Do not claim or implement until explicit dependency tasks are Complete. Use the canonical launcher-resolved parent and implementation task worktrees; execution_mode and completion_mode are developer. Do not change unrelated work or another repository. Record exact Shared package version/integrity, database migration and provider schema artifact used. No production customer messages, Meta registrations or live mutations are authorized by this task.

## Completion Report

### Status
Ready for Review — Attempt1. Implementation and available validation passed; lint unavailable as noted. Explicit acceptance/completion pending.

### Files Changed
21 task-owned paths: new src/commerce/presentation/ pure modules/catalogue/fixtures/tests; package.json subpath/script; tsup.config.ts build entry; additive src/commerce/schemas.ts presentation selections; scripts/validate-commerce-presentation.mjs. No consumer source, dependency lock or version changes.

### Work Completed
Browser-safe commerce/presentation export ports pure recommendation render/messages/money/candidates/shipping and wrapper contracts/projection/render/selection from Background d7e78bdb5e75248b9a15e2c84d07dcdc89027c19. Imports are local only; digest is injected; replay/applicationKey and I/O remain Background-owned. Strict host-verified projection checks current-shop URL consistency; exact product/variant selector provides typed limitations. Option renderer exposes only supplied facts, native selected variants and truthful unavailable/incomplete labels in all20 locales. Legacy absent options remain unknown/PARTIAL empty.

Composer preserves referral safety, three complete ordered candidates,4096 UTF16 units including wrapper, variable2048 bound, response slot/control/checkout/already-wrapped guards, no-active-wrapper unwrapped result and configured-invalid refusal. Returns wrapper provenance; no send authorization. Model reply normalization yields plain text for balanced emphasis/strike/safe HTTPS links while leaving unmatched markers/HTML inert and retaining URLs. Added identifier-only productOptionSelections max3 and PRODUCT_OPTIONS selection disposition; immutable response schema/release update remains consumer publication responsibility.

### Validation Results
- `npm run typecheck`: passed.
- `npx tsx --test src/commerce/presentation/presentation.test.ts src/commerce/product-discovery-contracts.test.ts src/commerce/product-discovery-projection.test.ts src/commerce/response.test.ts src/commerce/runner/runner.test.ts`:130 total,129 passed,1 existing consumer-environment skip,0 failed.
- `npm run build`: ESM/declarations passed.
- `npm run validate:commerce-entrypoints`: passed.
- `npm run validate:commerce-presentation`: passed built Node self-import and actual browser-platform bundle executed in VM without Node globals.
- Static legacy-golden.json captures60 byte-identical recommendation outputs from Background d7e78bd across20 locales/3 dispositions; no sibling runtime test imports.
- Boundary fixtures cover wrapper4096/4097, Unicode/multiline, plain-text markers/links/HTML, missing/configured-invalid wrapper, regional locale/checkout/variable/slot constraints, unknown/partial options and referral preservation.
- Final staged check found trailing blank line in newly tracked wrapper-contracts.ts; whitespace-only follow-up removes it. Aggregate implementation diff check passed; no semantic change after tests.
- Lint unavailable: package has no declared lint script or ESLint dependency. Not claimed passed; no unrelated tooling added.

### Deviations / Assistance / Limits
Material moda_shared assistance implemented source/tests; root reviewed composer boundaries and handled publication/report. Supporting package entry/build validator and additive selection schema are required by architecture decision4. No Background deletion here: downstream migration must adopt published exports and remove duplicated pure service implementations. No provider/model/network/customer/Meta mutation or deployment. No npm publication; source package remains5.5.0, immutable release integrity belongs to SHARED-003. No DB migration/provider schema artifact consumed by this pure port.

### Git / VCS
Canonical workspace /Users/kwadwoadomafriyie/project/moda-interact-workspace.
Parent /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-066-SHARED-002; implementation /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-066-SHARED-002; both task/ARCH-066-SHARED-002. Launcher synchronized before developer Attempt1 then failed report-format check after setting claim; normalized/published claimd8a0b7e4a without duplicate attempt. Implementation baseline7d48d05b519ac7c46a623c512278270f8522c4a1; main implementation7afdd9d147e507acd1d0c676784684d2a8c511e8 plus whitespace cleanup7255db5 published matching task branch. Parent report committed/pushed separately, exact SHA in Git history. Shared checkouts not switched, no other task worktree reused, no gitlink staged or main merge/push. No enabled task started.

## Dependency Reconciliation - 2026-11-08
SHARED-001 accepted Attempt2 explicitly developer-completed; sole explicit dependency satisfied. Ready at unchanged Attempt0, executor/claimed_at null; no claim or execution. Accepted Shared source c3f9f07cfcf9ff60817f89d5c3d2aaca2dddfbf7 published on task/ARCH-066-SHARED-001; separate publication still gated on SHARED-002.
