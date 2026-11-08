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
status: in_progress
priority: 50
executor: developer
claimed_at: 2026-11-08T13:39:57Z
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
- [ ] Golden fixtures compare legacy deterministic product/offer/shipping/wrapper outputs byte-for-byte except the deliberately specified new option/plain-text formatting cases.
- [ ] Boundary tests 4096/4097 including wrapper, Unicode, multiline replies, **bold**, ~~sale~~, links, malicious HTML displayed as inert text, wrapper missing/configured-invalid, locale fallback, checkout unavailable.
- [ ] Import built export in Node and browser-like runtime with no server dependencies. Preserve production moderation/send ownership. Typecheck, lint, build and package export tests pass. No publication here.

## Execution boundary
Definition only. Do not claim or implement until explicit dependency tasks are Complete. Use the canonical launcher-resolved parent and implementation task worktrees; execution_mode and completion_mode are developer. Do not change unrelated work or another repository. Record exact Shared package version/integrity, database migration and provider schema artifact used. No production customer messages, Meta registrations or live mutations are authorized by this task.

## Completion Report

### Status

In Progress — Attempt1; developer-authorized implementation and publication.

## Dependency Reconciliation - 2026-11-08
SHARED-001 accepted Attempt2 explicitly developer-completed; sole explicit dependency satisfied. Ready at unchanged Attempt0, executor/claimed_at null; no claim or execution. Accepted Shared source c3f9f07cfcf9ff60817f89d5c3d2aaca2dddfbf7 published on task/ARCH-066-SHARED-001; separate publication still gated on SHARED-002.
