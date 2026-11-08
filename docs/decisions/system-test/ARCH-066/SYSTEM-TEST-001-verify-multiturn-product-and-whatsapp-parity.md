---
id: ARCH-066-SYSTEM-TEST-001
architecture_id: ARCH-066
title: Verify multi-turn product recovery and WhatsApp parity
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-BACKGROUND-001", "ARCH-066-COMMERCE-001"]
enables: []
created: 2026-11-08
updated: 2026-11-08
---
# Verify multi-turn product recovery and WhatsApp parity

## Objective and read first
Implement only the owned work below. Read `docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md` first: its numbered contract decisions are normative and must not be redesigned by the implementor.

## Touch points
Existing `src/harness/aimock/`, `src/harness/mcp-production-image.js`, `src/whatsapp-emulator.js`, scenario registration and result reporting; NEW `src/scenarios/arch066-product-context-whatsapp-parity.js` plus deterministic fixtures using existing scenario conventions. Own system-test repository only.

## Required deterministic scenario matrix
- Script model outputs; do not rely on stochastic live model wording. Seed simple shirt, variable cream shirt with Size S/M and Colour Cream, no-size green shirt; known prices/sale evidence, allowlisted offer and configured AI wrapper with brand variable.
- Three turns: discovery -> ambiguous yes -> size question with explicit shirt. Compare complete rendered UTF-8 text, selected wrapper hash/locale and missing-checkout behavior from Studio vs Background. Background sends only to existing emulator; Studio sends nothing and creates no customer/outbox/template records.
- Deleted ID after discovery -> one NOT_FOUND -> corrected search -> verified size ANSWER. Malformed ID corrected. Wrong tenant/provider/parent, DENIED/revoked grant and stale turn must fail closed. No sizes must not invent values.
- Context expiry/CAS race/Redis purge/restart, legacy missing context, no active wrapper, configured malformed wrapper, unavailable locale, 4096/4097 full output and fixed token truncation diagnostic.
- Assert current price/availability/offer revalidation; old context IDs never serve as verified current facts. Assert no Markdown marker leakage on generated text and correct complete candidate shortening; never truncate a URL/offer term to meet limits.
- Report separate assertions for agent output, verified projection, composed body, moderation and emulated delivery. No claim local preview is Meta template registration validation. Keep initial-outreach regression scenario unchanged and passing.

## Acceptance / evidence
- [ ] Every matrix row reports PASS/FAIL with run IDs, tool names/statuses/counts, wrapper hash and composer artifact version; no secrets or raw customer payloads.
- [ ] Run disposable integration environment with pinned Shared/database/consumer commits; record command, fixture hashes and emulator outbound comparison artifact. Unit-only success does not complete this task.
- [ ] Final architect review confirms Studio/Background identical composition, explicit synthetic-context label, no permission weakening and no unresolved schema forks.

## Execution boundary
Definition only. Do not claim or implement until explicit dependency tasks are Complete. Use the canonical launcher-resolved parent and implementation task worktrees; execution_mode and completion_mode are developer. Do not change unrelated work or another repository. Record exact Shared package version/integrity, database migration and provider schema artifact used. No production customer messages, Meta registrations or live mutations are authorized by this task.

## Completion Report
Status: Not started. Attempt: 0. Implementation commit: none. Validation evidence: none. Remaining work: all unchecked acceptance criteria. Document isolated worktree, package, test and deployment evidence when implemented; do not mark Complete merely from source inspection.

## Deterministic implementation checklist
- [ ] Implement consumer contract E with registered scenario arch066-product-context-whatsapp-parity in src/scenario-catalogue.js/catalogue/scenarios.json and package script test:arch066:conversation using existing harness entrypoint. Record actual invocation; no invented independent test runner.
- [ ] Fixed fixture sequence per provider: discovery returns two same-title distinct IDs -> yes asks clarification with no inferred selection -> explicit ID/detail selection -> exactly one presentation-verification exact read -> expected current facts. Also one stale-ID NOT_FOUND then corrected search path; scripted hard DENIED remains referral.
- [ ] Repeat on Size, Shade/Volume, Species/Height/Pot size and custom label with description/attributes present/absent/partial. Assert exact labels/units and no claims unsupported by fixtures. No sizing-only pass criterion.
- [ ] Pin new SHARED-005, actual database migration and consumers; concurrent inbound versions run against real disposable DB/Redis. Compare exact composed UTF8 text with identical synthetic variables/provenance; separately assert final moderation/outbox emulator, not just model output.
- [ ] Record machine-readable per-case assertions, fixture hashes, calls/counts, diagnostics/stage, reference revision, artifact integrity, final body hash and emulator message hash. All required cases pass; skipped required integration case blocks completion. No live provider or customer send needed.
