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
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 1
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
- [x] Native fixtures Shopify/Woo simple/variable: sizes, colour+size, no attributes, partial/oversized attributes, duplicate names, variant-parent mismatch and stale/deleted product.
- [x] Published MCP result passes new Shared schema and original fields remain stable. Auth isolation and grant recheck tests continue to pass.
- [x] Query artifact validation, scoped tests, typecheck and lint pass; no provider calls or writes to real merchants required.

## Execution boundary
Definition only. Do not claim or implement until explicit dependency tasks are Complete. Use the canonical launcher-resolved parent and implementation task worktrees; execution_mode and completion_mode are developer. Do not change unrelated work or another repository. Record exact Shared package version/integrity, database migration and provider schema artifact used. No production customer messages, Meta registrations or live mutations are authorized by this task.

## Completion Report

### Status
Complete — accepted Attempt1 explicitly developer-completed on 2026-11-08.

### Files Changed
12 task-owned paths in fd53bb5: exact Shared package/lock pin; Woo direct-product-reader; Shopify core/executor; MCP execution/ports/service request correlation; existing reader/core/service regression tests; new product-options.test.ts. No Shared/service sibling/schema edits.

### Work Completed
Adopted published Shared exactly5.6.0 with lock integrity sha512-tDuW+C8MdteWMJWwmuFI2cTAugMejOJwTk0KkemBMwpN/lL92WPI8CX/A5dDa2nhG0RYiIeHSR490WPCrTz42w==. Parent Shopify/Woo options map native labels/values through Shared bounded normalizers; native variant selections populate selectedOptions without parent inference. Bounded projections include required fields only; existing pricing/sale/visibility evidence unchanged. Missing/empty attributes remain distinct from partial malformed/oversized attributes.

Native ID format fails INVALID_INPUT before provider call; genuine absent/404 product returns NOT_FOUND with bounded correction text. Exact variant-parent checks retained; excluded/unsafe catalogue rows preserve prior empty-result behavior. Auth/permission/outage handling remains hard. Existing logger records safe reason/shop/tool and service-generated unique request UUID, wired through internal execution context; no raw args/provider bodies or credentials. No API version/scope expansion or new endpoint.

### Validation Results
- `npx tsx --test tests/unit/execution/policy/product-options.test.ts tests/unit/execution/policy/shopify-core.test.ts tests/unit/execution/policy/product-search-composition.test.ts tests/unit/connections/woocommerce/direct-product-reader.test.ts tests/unit/mcp/capability-invocation.test.ts tests/unit/mcp/authentication.test.ts tests/unit/mcp/service.test.ts`:72 passed,0 failed.
- Final updated service suite12 passed and native option suite8 passed after their last focused additions; no failures.
- `npm run typecheck`: passed.
- `npm run lint`: passed.
- `npm run build`: passed.
- `git diff --check`: passed.
- All4 Shopify query documents validate against local accepted pinned Admin2026-07 artifact and official Shopify skill helper; read_products unchanged. Existing featuredImage deprecation warning retained. Pinned schema SHA256 2b507dc1f74c6157e0eb98500db0f3c3e238d69eaf0d98fd7657ac7ed3f6900b. Skill official docs search and validation used pinned version; log_feedback invoked exactly once with instrumentation opted out, exit0.
Fixtures cover simple/variable native options, missing/partial/oversized/duplicate attributes, native selections, parent mismatch, stale/missing IDs and safe diagnostics, service request UUID uniqueness, existing auth/grant/capability rechecks and original product composition.

### Deviations / Assistance / Limits
Material moda_mcp assistance implemented/tests under explicit developer authorization; root handled publication/report. User publication wording resolved to actual MCP implementation scope; consumed existing release, no additional package published. Locked dependency/docs commands initially encountered restricted network; authorized access succeeded. Pinned artifact was absent in new worktree and installed through existing accepted installer from canonical artifact evidence. Initial temp query extraction CJS invocation failed before validation files; corrected ESM extraction and all4 validations passed. No live merchant/provider calls, production mutations, migration or deployment. Database/schema unchanged.

### Git / VCS
Canonical workspace /Users/kwadwoadomafriyie/project/moda-interact-workspace. Parent /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-066-MCP-001; implementation /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-066-MCP-001; matching task/ARCH-066-MCP-001 branches. Launcher synchronized/gated before developer Attempt1, then report-format check failed after setting claim; normalized/published claimc3ad9408f without duplicate attempt. Implementation baseline2e4c4dc33861bde831003fb9d1c8bc97827d302b; implementation fd53bb52acaf6426b1a1e1793b8d4fc8ae54c2a4 pushed matching task ref. Parent report committed/pushed matching branch, exact SHA in Git history. Shared checkout not switched, no other task worktree reused, no gitlink staged/main merge/push. Downstream tasks not started or promoted by review submission.

## Release / Dependency Handoff - 2026-11-08
SHARED-003 accepted Attempt1 explicitly Complete. Pin @modainteract/moda-interact-shared exactly5.6.0; dist.integrity sha512-tDuW+C8MdteWMJWwmuFI2cTAugMejOJwTk0KkemBMwpN/lL92WPI8CX/A5dDa2nhG0RYiIeHSR490WPCrTz42w==. Downloadable archive and isolated public-import/browser checks verified in release record. Sole dependency satisfied: Ready at unchanged Attempt0, unclaimed. No claim or execution performed.

## Developer Self-Review - Passed / Accepted Attempt 1
2026-11-08: Reconciled complete task/architecture mapping rules, actual provider option projections and exact-ID lookup branches, correlated service context and native fixtures. Implementation fd53bb52acaf6426b1a1e1793b8d4fc8ae54c2a4 matches published task ref; parent1d915eff0877792e1002a84e6d3b6fcbb93a6896 matches published report. Both canonical worktrees clean; recorded isolation/synchronization/claim and material assigned-agent assistance retained.

Scoped review passes: exact Shared5.6.0/integrity pinned, native parent options and selected variation fields mapped through bounded Shared parsers, simple Woo selections empty, missing/partial states truthful, no inferred stock or arbitrary description. Exact native ID checks precede provider reads; genuine absent/404 gets bounded correction, parent mismatch remains fail-closed, excluded catalogue behavior retained. Internal unique request correlation reaches policy diagnostics; no raw args/bodies or credential logs introduced. Auth/grant rechecks and existing price/sale evidence untouched.

Validation reviewed:72-pass scoped run plus final service12/native8 targeted checks, declared typecheck/lint/build, diff check, local pinned schema and all4 official Admin2026-07 query validations passed. read_products and API version unchanged; existing featuredImage warning remains. Pinned schema SHA2562b507dc1f74c6157e0eb98500db0f3c3e238d69eaf0d98fd7657ac7ed3f6900b recorded. No relevant changes after these checks justify redundant rerun. No live merchant/provider or deployment result asserted.

No outstanding scoped correction found. Accepted Attempt1 unchanged; status review, executor/claimed_at null, completion_mode developer retained. Explicit `/moda_developer_update ARCH-066-MCP-001 complete` pending. No downstream promotion, enabled execution, additional npm publication or main merge/push.

## Developer Completion Decision - 2026-11-08
Developer explicitly invoked `/moda_developer_update ARCH-066-MCP-001 complete`. Durable passing review45316cecf043254acbe425cf696f1a336918bf01 verified published. Implementation fd53bb52acaf6426b1a1e1793b8d4fc8ae54c2a4 matches published task ref; both canonical worktrees clean. All scoped requirements satisfied with recorded local validation limits. Status Complete, accepted Attempt1 unchanged, executor/claimed_at null. No new provider execution, deployment or main merge/push.

### Dependency-frontier reconciliation
COMMERCE-001 depends only on SHARED-003 and MCP-001, now Complete: promote to Ready at unchanged Attempt0/unclaimed. BACKGROUND-001 remains Pending because DATABASE-001 is Ready, not Complete. Terminal System Test remains Pending/manual-gated on Background/Commerce completion. No enabled task started; readiness records published on completion branch.
