---
id: ARCH-066-COMMERCE-001
architecture_id: ARCH-066
title: Preview verified product context and final WhatsApp message
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-SHARED-003", "ARCH-066-MCP-001"]
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
Definition only. Do not claim or implement until explicit dependency tasks are Complete. Use the canonical launcher-resolved parent and implementation task worktrees; execution_mode and completion_mode are developer. Do not change unrelated work or another repository. Record exact Shared package version/integrity, database migration and provider schema artifact used. No production customer messages, Meta registrations or live mutations are authorized by this task.

## Completion Report
Status: Not started. Attempt: 0. Implementation commit: none. Validation evidence: none. Remaining work: all unchecked acceptance criteria. Document isolated worktree, package, test and deployment evidence when implemented; do not mark Complete merely from source inspection.
