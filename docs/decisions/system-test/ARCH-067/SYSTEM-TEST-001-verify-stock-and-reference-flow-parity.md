---
id: ARCH-067-SYSTEM-TEST-001
architecture_id: ARCH-067
title: Verify Studio and Background stock/reference parity
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-067-COMMERCE-001", "ARCH-067-BACKGROUND-001", "ARCH-067-MCP-001"]
created: 2026-11-09
updated: 2026-11-09
---
# Verify Studio and Background stock/reference parity

## Objective and binding specification
Implement the owned portion of [ARCH-067](../../../architecture/ARCH-067-product-reference-and-current-stock-parity.md). Every schema, mapping, persistence, rendering, diagnostic and compatibility rule there is normative. No merchandise-specific behavior. Dependencies must be complete before execution.

## Exact work and touch points
Own system-test existing commerce integration harness/fixtures and new tests/commerce/product-reference-stock-parity.test.ts (adapt only extension to existing test runner convention, record actual path). Execute same canonical provider fixtures through Studio local, Studio standalone MCP and recovery-linked Background subsequent interaction for Shopify and WooCommerce. Include arbitrary merchandise (tree height, varnish finish, shirt variant); three displayed products with IDs whose lexical order differs, then first/green/finish references; exact fresh stock7, mutate fixture to2 before follow-up =>2; known0, untracked,null/malformed,parent-managed and multiple variants; ambiguous selection asks clarification; foreign native pair rejected; legacy JSON loads; failed turn does not replace presentation; retry/replay preserves composed message. Assert exact normalized stock and selected pair, same localized composed WhatsApp body/limits and no real Meta send. Test initial-outreach regression from real fixture checkout via existing preview seam, without WABA/template approval validation additions. Document deployment sequence Shared → both context readers → adapters/hosts → enable emission after both reader checks; no roll-forward claim without receipts. Run harness named suites and record pass/fail, SHAs, artifact integrity. No unrequested live environment writes.

## Acceptance criteria
All owned requirements above and architecture contract are implemented and verified. List every actual changed path and test result. Shared behavior must be imported through published public exports; no copied cross-repository source. Unknown inventory remains distinct from zero. Existing authorization, checkout ownership, WhatsApp composition and replay rules pass regression checks. No unresolved design choices may be silently substituted; report a concrete contract conflict before implementing an alternative.

## Non-goals
No inventory mutation, new database table, token-refresh redesign, new template approval/WABA validation, category sequencing redesign or budget increase.

## Completion Report
Status: Not started.
Implementation SHA: Pending.
Validation: Pending.
Deployment/compatibility evidence: Pending.

## Architect Review
Status: Not reviewed.
