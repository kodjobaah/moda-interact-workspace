---
id: ARCH-066-MCP-001
architecture_id: ARCH-066
title: Expose provider product options and exact ID diagnostics
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-SHARED-003"]
enables: ["ARCH-066-BACKGROUND-001", "ARCH-066-COMMERCE-001"]
created: 2026-11-08
updated: 2026-11-08
---
# Expose provider product options and exact ID diagnostics

## Objective and read first
Implement only the owned work below. Read `docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md` first: its numbered contract decisions are normative and must not be redesigned by the implementor.

## Scope / touch points
`package.json`, lockfile; `src/execution/policy/shopify-core.ts`, `src/connections/woocommerce/direct-product-reader.ts`, product read ports/projections, matching pinned Shopify query artifacts and `tests/unit/execution/policy/`. Adopt exact published package from SHARED-003.

## Deterministic mapping
Architecture decision 1 is authoritative. Extend product and variant Shopify reads using the existing pinned Admin schema/version: parent option names/values -> options, variant selected option name/value pairs -> selectedOptions. Validate generated query against the pinned schema artifact; no new scope or API version change. Woo parent attributes{name,options,variation} -> options; variation attributes{name,option} -> selectedOptions. Simple products may have option attributes without variations; preserve empty/missing distinctly. Add only required fields to bounded read projections; retain no arbitrary raw descriptions/HTML.
- Exact-ID reads preserve parent/variant membership checks. Return NOT_FOUND with bounded correction text for an absent native product; invalid provider ID format returns INVALID_INPUT with correction text. Never resolve an arbitrary foreign ID by title or loosen tenant checks.
- Log native format/missing-parent/provider-not-found rejection reason plus shopId/toolName/request correlation through existing logger. Never raw credentials or raw argument/body dumps. Do not treat 404 as provider outage. Permission or auth rejection stays hard.
- Existing product output bounds and price/sale evidence validation remain. Options are current observations, not claims that every size is in stock.

## Acceptance / validation
- [ ] Native fixtures Shopify/Woo simple/variable: sizes, colour+size, no attributes, partial/oversized attributes, duplicate names, variant-parent mismatch and stale/deleted product.
- [ ] Published MCP result passes new Shared schema and original fields remain stable. Auth isolation and grant recheck tests continue to pass.
- [ ] Query artifact validation, scoped tests, typecheck and lint pass; no provider calls or writes to real merchants required.

## Execution boundary
Definition only. Do not claim or implement until explicit dependency tasks are Complete. Use the canonical launcher-resolved parent and implementation task worktrees; execution_mode and completion_mode are developer. Do not change unrelated work or another repository. Record exact Shared package version/integrity, database migration and provider schema artifact used. No production customer messages, Meta registrations or live mutations are authorized by this task.

## Completion Report
Status: Not started. Attempt: 0. Implementation commit: none. Validation evidence: none. Remaining work: all unchecked acceptance criteria. Document isolated worktree, package, test and deployment evidence when implemented; do not mark Complete merely from source inspection.

## Release / Dependency Handoff - 2026-11-08
SHARED-003 accepted Attempt1 explicitly Complete. Pin @modainteract/moda-interact-shared exactly5.6.0; dist.integrity sha512-tDuW+C8MdteWMJWwmuFI2cTAugMejOJwTk0KkemBMwpN/lL92WPI8CX/A5dDa2nhG0RYiIeHSR490WPCrTz42w==. Downloadable archive and isolated public-import/browser checks verified in release record. Sole dependency satisfied: Ready at unchanged Attempt0, unclaimed. No claim or execution performed.
