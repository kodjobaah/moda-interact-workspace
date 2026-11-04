---
id: ARCH-058-COMMERCE-001
architecture_id: ARCH-058
title: Provision the standard product discovery tools and repeatable environment setup
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-058-MCP-002
- ARCH-058-MCP-003
enables:
- ARCH-058-BACKGROUND-001
- ARCH-058-SYSTEM-TEST-001
created: '2026-11-04'
updated: '2026-11-04'
---

# ARCH-058-COMMERCE-001: Provision the standard product discovery tools and repeatable environment setup

## Architecture

Architecture ID: `ARCH-058`. Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`. Normative contracts: `docs/architecture/ARCH-058/contracts.md`. Coordinator: `moda_architect`.

**Defined but not materialised.** No task branch, worktree, commit, migration, environment publication or deployment is established by this definition. Materialise through `/moda-task ARCH-058-COMMERCE-001 --definition <path-to-this-file>`; use the implementation worktree and `MODA_WORKSPACE_ROOT` supplied by the launcher.

## Objective

Extend the existing source-controlled Commerce system-tool sync to publish category resolution, product search/browse, exact product lookup and basic shipping information as standard capabilities for every otherwise authorized store. Publish the owned instructions and structured output fields for verified recommendations and bounded soft responses. Provide one explicit Commerce-owned setup command that invokes the accepted Database migration, MCP taxonomy import and Commerce publication stages in order, without manual Studio authoring or per-merchant opt-in.

## Context

- `scripts/sync-system-commerce-tools.mjs` and `src/commerce/bootstrap/system-commerce-tool-sync{,.cli}.ts` already implement explicit dry-run/apply, source ownership, content hashes, immutable publication and compare-and-set activation for two product tools. Extend this implementation.
- `src/commerce/bootstrap/system-product-tools.ts` currently declares `commerce_search_products` and `commerce_get_product`. Its feature guard expects `MERCHANT_OPT_IN` and not required; its receipt truncates actions to two. DATABASE-001 deliberately changes the existing feature to required/always enabled, and the new registry has four tools. These are proposed task changes, not proof of an already published registry.
- `CommerceLifecycle.createSuccessorRelease` appends a member but preserves existing behavior/response snapshots. `createRelease` selects latest published revisions and current feature configuration. Neither may be used blindly to install the new search revision and recommendation contract while preserving unrelated immutable pins.
- Commerce inspection in `src/commerce/integration/backend.ts` currently requires a true preference. It must agree with Shared/MCP required-feature selection, so a ready store is not falsely reported as disabled.
- Revision03 proposed a workspace-root setup script. ARCH-058 explicitly refines that location to **this Commerce repository** so every runtime implementation file has an existing task route. The wrapper calls child commands and does not become a cross-service implementation owner.

## Scope

In `moda-interact-commerce` only:

1. Extend the source-owned tool registry and existing sync planner/apply/CLI for the four frozen product capabilities.
2. Publish the declared product-discovery/soft-response behavior, nonempty owned response instructions and owned response-detail fields through an exact immutable successor, preserving unrelated release contents.
3. Correct required-feature inspection parity, matching response-contract composition for feature previews and any Commerce preview adapter narrowing required by Shared's new built-in grant/output branches. Label the existing raw runner transcript accurately.
4. Add `scripts/setup-commerce-product-discovery.mjs`, the `commerce:setup-discovery` package command, a thin testable orchestration module and operator documentation.
5. Validate dry-run, full fixture setup, repeat-run no-op, partial failure/resume, ownership conflicts and exact release preservation.

## Out of Scope

No Database migration/seed authoring, MCP importer/provider implementation, Admin/Gateway/Background changes, manual merchant preferences, per-shop provisioning, new tool registry, published discount tools, product mirror, deployment service, automatic startup/cron publication or customer send. Do not run `--apply` against a persistent LOCAL, TEST, DEVELOPMENT, STAGING or PRODUCTION environment in this implementation task. Only disposable isolated fixtures may be mutated. The developer runs the operator command after accepted compatible readers/hosts are deployed.

## Requirements

### Accepted versions and source-owned definitions

- Install the exact Shared package accepted/published by ARCH-058-SHARED-002. Target `4.0.0` only while the accepted source/registry baseline remains `3.1.0`; reconcile an occupied/changed version with the architect. Use the accepted Database revision through the normal submodule. Do not import sibling Shared source or create duplicate public validators.
- Extend `SYSTEM_COMMERCE_PRODUCT_TOOLS` and executable drafts in `src/commerce/bootstrap/system-product-tools.ts` to exactly the four identities below, all under existing `Feature.key = product_search` and equal tool/capability names:

| Tool/capability | Definition version | Policy operation | Operation version |
| --- | --- | --- | --- |
| `commerce_resolve_product_categories` | `1.0.0` | `taxonomy.resolveCategories` | `1.0.0` |
| `commerce_search_products` | `2.0.0` | `products.search` | `1.0.0` |
| `commerce_get_product` | unchanged `1.0.0` | `products.get` | unchanged `1.0.0` |
| `commerce_get_shipping_information` | `1.0.0` | `shipping.getInformation` | `1.0.0` |

- Keep get-product definition content byte/canonical-hash identical. If its immutable input/description/template must change, stop to reconcile a new definition version rather than changing existing `1.0.0` content. Definition and operation versions are independent.
- Register `taxonomy.resolveCategories` and `shipping.getInformation` in the existing `POLICY_OPERATIONS` tuple and `POLICY_OPERATION_CONTRACTS`/authoring registry. Derive input/output schemas from Shared and parse generated input with the existing subset validator. Map optional `query`, `category`, `browse`, `limit` and cursor/filter arguments with correct omission semantics; MCP applies the frozen defaults and browse exclusivity. Use the exact bounded shipping input/output from contracts section 2.3, including nullable product/variant IDs and independent normal data outcomes. Keep product-search and exact-get output contracts unchanged. Use only the approved details-subset depth change to 5; input depth remains 3. No general `oneOf` or other depth/property/result-size widening.
- Narrowly extend the existing projector in `src/commerce/execution/policy-operation-authoring.ts`, or construct the exact owned bounded fragments, so generated fixed string literals use a single-value `enum` instead of unsupported `const`, and fixed string enum/literal schemas have a finite `maxLength` derived from their allowed values. Apply this consistently to approved nullable string projections, presentation selections and recommendation fields while preserving existing nullable/default/`$schema` normalization. Do not weaken the subset validator, erase allowed-value restrictions, widen supported keywords or introduce a general schema engine. Prove the actual source-owned resolver/search/shipping drafts and combined response contract survive the complete generation/publication validator path; a hand-built substitute schema is insufficient.
- Update the feature precondition to active, `ALWAYS_ENABLED`, `systemRequired: true`. Missing/conflicting feature preparation is explicit and does not cause the sync to create a second feature, run seed or write per-shop preferences. All plan preparation is DATABASE-001-owned.
- Preserve audit/source ownership checks. A human-authored same-name tool/capability is a conflict, not an object to adopt. A stored definition with the same version and different content hash is a conflict. Inventory all existing `product_search` members before making that feature globally active; unexpected custom/manually authored members require architect reconciliation, not silent global enablement.

### Declared behavior and response contract

- Add source-controlled product-discovery behavior and the owned recommendation/presentation details fragments alongside the system registry. Behavior must explain: categories are reference meaning; read current-shop products before claiming assortment; use text search when category mapping is unavailable; clarify material ambiguity; preserve unknown price/currency/availability; check current-policy-permitted canonical discount options/details; and select structured identifiers/scopes for trusted host finalization.
- Authorize a bounded soft response to an out-of-scope request or expected missing merchant information: briefly acknowledge the limitation, then offer at most one verified relevant product and permitted supported promotion, or the product alone. Prefer current customer/product context and refreshed owned-basket context; use explicit bounded browse when there is no usable intent. Do not invent a query/category, popularity ranking, product availability, destination or discount. If no usable product is verified, the host uses its localized limitation and verified store-link fallback. Ordinary recommendations may still contain up to three independently evaluated alternatives.
- Describe the narrow optional taxonomy/discount unavailable-data branches and exact shipping normal outcomes accurately. They permit independently grounded content with no unsupported promotion; they do not clear a terminal tool error or prove an empty merchant catalogue. Missing policy permission is only the preflight-classified outcome defined by MCP-003; a provider authorization failure remains a hard error. Respect NONE/FIXED/AI and unknown/incomplete condition facts. The standard feature does not grant or enable optional Merchant Knowledge; use its retrieved content only when separately entitled and as untrusted reference data.
- Add the frozen `productRecommendationVersion` and `productRecommendations` fields to the existing release `detailsSchema`, using the Shared selection schema, approved nullable scalar support and the narrowly approved details maximum depth of 5 (root at depth 1, deepest `offerIds` string at depth 5). Keep the input maximum depth at 3 and every other bound unchanged. Preserve unrelated fields and bounds. Both fields are optional at the release schema level; the host enforces their paired presence and recommendation semantics. Do not add model-authored price, savings, currency or promotional prose fields.
- Also publish the two optional fields from `CommerceAnswerPresentationSelectionSchema`: `responseDisposition` with exactly `STANDARD`, `OUT_OF_SCOPE_REDIRECT`, `SHIPPING_INFORMATION_UNVERIFIED`, and `shippingInformationSelection` with nullable product/variant identifiers. Both null selects the shop-policy observation; any shipping selection requires an explicit disposition in host policy. Keep shipping selection free of model policy prose, price, cost/time, destination, URL and evidence fields. The host validates relevance and facts; a parsed selection is not proof.
- Publish nonempty source-owned response instructions together with the owned details fragment. Replace the known default instruction to always return empty details for this release with instructions describing the structured branches and their ordinary `ANSWER` envelope. A soft disposition, owned recommendation/shipping selection, registered product/discount observations, a product-bearing shipping observation (non-null requested productId), or a host-known recommendation branch must enter full host composition even if the model later omits its selection or labels it `STANDARD`. No raw model promotion prose is appended. A positive combined shipping/product reply uses only observed variant shipping facts and a verified policy link in the host composer; ordinary policy-only grounded answers retain their guarded existing path only outside the controlled branch. A null/null policy observation alone does not trigger the product branch. No global semantic verification of arbitrary prose, destination rate/speed promise, cart quote or mutation is claimed.
- Own only this feature behavior, the declared response instructions and these response fields. Compare approved source-owned prior/current hashes and the known default response baseline before replacing owned content. Conflicting pre-existing manual fields, instructions or behavior must fail for reconciliation, not be overwritten or dropped. Preserve the hard `REFER_TO_STORE` envelope and required-referral state; soft dispositions never permit details/evidence in a hard referral.
- New release runner compatibility is `>=1.1.0 <2.0.0`; keep `commerce.v1`. Validate exact installed runner/Shared compatibility and all retained unrelated members before creating/activating a release. Publication occurs only after accepted readers and host can consume the new contracts.

### Exact immutable successor and idempotence

- Extend the existing planner/apply functions; do not build a second publisher. Plan each named tool using the established `CREATE`, `PUBLISH`, `PIN_NEW_REVISION` or `NO_CHANGE` actions, and declare behavior/response changes explicitly in the plan. A behavior, response-instruction or owned-schema change alone must produce a new release even when all four tool pins are unchanged.
- Use authorized `CommerceLifecycle` and existing publication/feature-capability storage mechanisms for every mutation. Implement a narrowly scoped exact successor/delta operation if required: it takes the verified base release and explicit owned revision/behavior/response changes, preserves all unrelated immutable members/snapshots and publishes a new immutable release. Do not mutate an existing release or write release tables directly from the script.
- Preserve unrelated capability IDs, tool/revision pins, positions, feature behavior snapshots and response fields exactly. Existing owned member positions remain stable; append missing owned capabilities deterministically. Validate the completed successor against the base and explicit delta before activation.
- The append-only `createSuccessorRelease` is insufficient for replacing an existing search pin or owned behavior/response. Do not rebuild via `createRelease` unless exact preservation is proved; selecting latest unrelated revisions is prohibited. If unrelated revision/behavior changes or capacity/contract conflicts cannot be preserved, fail with a bounded reconciliation result.
- Read the environment pointer/edit version, recheck plan preconditions before writes, activate by existing compare-and-set and verify final pins/response hash/feature snapshot. A CAS race stops/replans explicitly; do not spin or silently activate over another operator's work.
- Reuse already-published identical owned revisions and recover valid partial publication safely. An unchanged second apply produces no new drafts, revisions, capabilities, releases, audits or pointer writes. It still verifies readiness and returns all four `NO_CHANGE` actions.
- Retained conversation grants are not rewritten by this CLI. Document the coordinated pre-production deployment and fresh-conversation/grant transition; do not broaden an existing grant to make a release migration appear compatible.

### Existing CLI, actor and selection parity

- Retain `"commerce:sync-tools": "node scripts/sync-system-commerce-tools.mjs"` and the existing `.mjs`/installed-esbuild standalone approach. Extend `src/commerce/bootstrap/system-commerce-tool-sync.cli.ts` rather than adding a second CLI. Keep generated bundles transient and outside tracked source; do not import Next server-only composition into the command.
- Preserve explicit environment identity, exactly one mode, `DATABASE_URL`, `COMMERCE_SYSTEM_TOOL_ACTOR_EMAIL` resolving to exactly one active `SUPER_ADMIN`, authorization recheck and production-apply `--confirm-production`. No development bypass, automatic administrator creation or secret-bearing arguments/logs.
- Replace the hard-coded two-tool action truncation/type union with the exact bounded four-tool registry. Emit the frozen schema-versioned publication receipt with every tool name/action/revision/hash, previous/new release IDs and stage status. Never report successful setup from an incomplete action list or omit a resolver/shipping failure.
- Dry-run does no writes, audits, publication, embedding calls or provider product/discount reads. In a setup plan with known pending migrations, distinguish deferred post-migration checks from genuine feature/ownership failures; do not claim a fresh database already satisfies runtime preconditions. Apply always requires the prepared schema/feature and rechecks them.
- Update Commerce inspection/candidate diagnostics to Shared's active feature + eligible plan mapping + (always enabled or merchant preference) rule. Absent/false preferences do not disable the core feature; optional features and all ordinary shop/provider/subscription/plan checks remain intact.
- Audit the existing Commerce preview/runner adapter for new Shared built-in grant and optional-output unions. Narrow deliberately to preserve existing published preview behavior and canonical successful discount outputs. Do not publish duplicate discount tools or treat built-in descriptors as database tool/revision identities. Stop if a required preview change would introduce a second runtime/proof engine.
- In `src/commerce/integration/backend.ts:createPrismaFeatureComposition.resolve`, replace the unconditional `EMPTY_RESPONSE_CONTRACT` for a selection containing the owned product-search capabilities with the compatible published or approved source-owned response contract/instructions used by the sync. Validate selected tool identities/versions against that contract, preserve unrelated selected-feature behavior, and fail an unresolved mismatch instead of mixing incompatible latest revisions. Keep existing RELEASE selection reads pinned to their stored response contract/hash. Reuse the owned fragment; do not invent a second schema or import Background's composer.
- In `src/studio/test-conversations/conversation-panel.tsx`, add only the narrow runtime-label clarification that this is runner/tool output and does not include Background's final customer composition/wrapper. Preserve existing FIXTURE/LOCAL/LIVE disclosure, workflow and controls. A matching schema fixes structured preview input; it does not establish final customer-message parity. No redesign or new preview delivery engine is included.

### Commerce-owned environment orchestrator

- Add `scripts/setup-commerce-product-discovery.mjs` and `"commerce:setup-discovery": "node scripts/setup-commerce-product-discovery.mjs"`. Place its testable orchestration logic under `src/commerce/bootstrap/product-discovery-setup.ts` (with a standalone CLI module if needed), reusing existing build/execution dependencies.
- Require `--workspace-root=<canonical-operator-checkout>` in addition to the frozen environment/mode/source/production flags. Resolve real paths and validate the canonical parent Git/workspace identity, expected repository/package names and accepted revision pins. The operator root must deliberately contain the accepted `moda-interact-database`, `moda-interact-mcp` and `moda-interact-commerce` checkouts. Reject accidental task/sibling checkout mismatches; never guess a `/Users/...` path or silently redirect repositories. Record safe immutable revisions in operator evidence.
- The executing Commerce code must belong to that explicitly selected accepted checkout. Run child commands with explicit cwd and argument arrays, never shell interpolation; preserve the selected environment/configuration and forward only each command's supported flags. No sibling application imports, source edits, package installation, administrator creation, credential synthesis or dependency deployment.
- Preflight checks repository/runtime/package identities, deployment environment, target database/pgvector support, approved source bytes, reference embedding configuration/credential access, Commerce actor, current publication ownership and pending migration scope. A fresh target may plan schema-dependent checks as pending; unexpected read errors are failures, not an empty target.
- Determine/list the normal Database runner's outstanding migrations before apply. Proceed only with the accepted planned migration set; stop on unapproved drift. Do not issue taxonomy-only ad hoc DDL or call broad `prisma/seed.mjs`, which rewrites unrelated plan mappings.
- Execute these subprocess stages in order: Database `npm run migrate:deploy`; MCP `npm run taxonomy:sync -- --environment=<env> --apply` with applicable verified source/production flags; Commerce `npm run commerce:sync-tools -- --environment=<env> --apply` with applicable production flag. The wrapper owns coordination and receipts, not those services' business rules.
- Dry run never executes `migrate:deploy`, a paid embedding request, mutation or publication. It may invoke read-only child planning commands and reads. On an empty database, report migrations and deferred validation for taxonomy/publication explicitly instead of calling nonexistent tables and reporting success or failure as if no migration were planned.
- Capture bounded child output safely, preserve each original sanitized failure/exit status and assemble the frozen ordered `preflight`, `migration`, `taxonomy`, `publication` receipt. Subcommand statuses are `PLANNED`, `APPLIED`, `UNCHANGED`, `FAILED` or `NOT_RUN`. A failed stage stops later stages and exits nonzero; previously successful stages remain reported and valid. Do not roll back a valid taxonomy because publication failed, and do not claim full success after partial completion.
- A rerun after failure reuses completed migrations/generation/published identities. An unchanged full rerun makes zero embedding calls and zero publication writes. Include all four standard tools, active compatible release, matching nonempty response instructions and complete corpus in the final readiness verification. A shipping tool can be ready while a particular store has the contract's explicit policy-scope/unsupported data outcome; do not hide the descriptor or claim that publication grants a provider scope.
- Do not wire provisioning into service startup, every customer request or new-shop onboarding. The shared corpus plus required feature/plan mapping covers future eligible connected stores without a new import or manual tool-authoring step.

### Diagnostics and operational handoff

Use `@modainteract/moda-interact-shared/logging` and `docs/observability/shared-logging.md`. Preserve safe original Prisma/child/provider errors and causes at the owning boundary with separate stage/reason; redact and bound connection strings, credentials, headers, corpus text, vectors and customer data. A logger failure must not alter release correctness. Keep command receipts distinct from diagnostic streams.

Document prerequisites and post-deployment invocation from the explicitly selected Commerce checkout:

```bash
npm run commerce:setup-discovery -- --workspace-root=<canonical-operator-checkout> --environment=test --dry-run
npm run commerce:setup-discovery -- --workspace-root=<canonical-operator-checkout> --environment=test --apply
```

These are future operator commands, not steps to run against a persistent target during this task. The operator supplies configured database/environment, accepted revision/package pins, verified source manifest, existing reference embedding configuration/keyring and authorized publication actor. The implementation must report missing prerequisites without inventing or modifying them. Production requires its additional explicit confirmation flag.

## Work Items

- [ ] Reconcile accepted Shared/Database/MCP source and install the exact published Shared dependency.
- [ ] Extend canonical definitions/operation registration and required-feature checks; keep unchanged get-product content immutable.
- [ ] Define and plan owned behavior/response-instruction/schema changes and implement exact immutable successor publication preserving unrelated pins/snapshots.
- [ ] Extend existing sync CLI/actions/receipts, current actor checks and full no-op behavior.
- [ ] Correct Commerce selection diagnostics and any necessary Shared-union preview narrowing.
- [ ] Implement the Commerce-owned setup wrapper with explicit validated workspace root, thin child stages, dry-run and partial-failure receipts.
- [ ] Add isolated tests, document future operator commands and deployment/grant transition, complete the report, set status to `review` and stop.

## Interfaces / Contracts

Use `docs/architecture/ARCH-058/contracts.md` for the complete tool/response/built-in/CLI/receipt contract. Shared owns schemas and runner identities; Database owns migration/plan data; MCP owns taxonomy/provider/discount execution; Commerce owns only authoring, immutable publication, inspection and operator orchestration. Runtime wrapper code stays in this repository, not workspace-root `scripts/`.

Primary paths: `src/commerce/bootstrap/{system-product-tools,system-commerce-tool-sync,system-commerce-tool-sync.cli,product-discovery-setup}.ts`, `scripts/{sync-system-commerce-tools,setup-commerce-product-discovery}.mjs`, `src/commerce/tool-definition/contracts.ts`, `src/commerce/execution/policy-operation-authoring.ts`, `src/commerce/publication/{lifecycle,ports,validation}.ts`, `src/commerce/integration/backend/publication-storage.ts`, `src/commerce/integration/backend.ts`, `src/commerce/integration/preview/adapters.ts` only for the necessary union narrowing, `src/studio/test-conversations/conversation-panel.tsx` only for the runtime label, `package.json` and lockfile. Internal lifecycle additions must preserve existing caller behavior; no new public cross-service contract is invented here.

## Dependencies

- `ARCH-058-MCP-002`: accepted actual product/category and canonical built-in discount execution. Its dependency chain provides MCP-001, DATABASE-001 and the published Shared contracts.
- `ARCH-058-MCP-003`: accepted basic shipping reader, independent data outcomes, scope preflight and published operation registration; its accepted chain includes SHOPIFY-001 where required.

The actual persistent setup also requires accepted compatible Background/runner deployment before publication. A task's implementation dependency does not authorize a deployment or persistent apply.

## Enables

- `ARCH-058-BACKGROUND-001`: consume the approved standard definitions/behavior/response contract in the existing conversation host.
- `ARCH-058-SYSTEM-TEST-001`: exercise the full operator and runtime composition with isolated deterministic fixtures.

## Acceptance Criteria

- [ ] The registry contains all four frozen product capabilities and no duplicate discount publication; feature policy requires no merchant opt-in for otherwise eligible stores and does not broaden Merchant Knowledge entitlement.
- [ ] Actual generated resolver/search/shipping drafts and the owned recommendation/presentation response contract pass the publication subset validators, including browse defaults, enum/literal bounds and nullable fields; existing get-product content and product outputs are unchanged or a separately approved version is recorded.
- [ ] Source ownership, immutable-version drift and unexpected custom feature members fail safely before global enablement/publication.
- [ ] New behavior, consistent nonempty response instructions and owned response fields appear in the active compatible release even when only those fields changed; all unrelated pins/positions/feature snapshots/response fields are exactly preserved. No active instruction still requires empty details for the new structured branches.
- [ ] Newer unrelated tool revisions and mutable feature edits do not get swept into the successor. CAS race, field collision, invalid hash/contract and revision capacity failures leave the active pointer unchanged.
- [ ] All four CLI actions appear in receipts; unchanged repeat apply creates no publication records/audits/pointer writes. Actor/environment/production checks remain effective.
- [ ] Shopify/Woo inspection and current manifest eligibility match Shared for missing/false core preferences, free/paid plans and excluded subscription/connection cases.
- [ ] Feature previews use compatible owned/published instructions and response fields; incompatible identity/contract pairs fail, stored RELEASE contracts remain pinned, and raw runner output is clearly distinguished from Background's final customer output.
- [ ] Fresh dry run reports planned migrations/deferred checks with zero writes/embeddings; isolated first apply and rerun produce a valid corpus, all four tools and the expected no-op.
- [ ] Failure at migration, import or publication stops subsequent stages; receipts preserve prior completion, and rerun finishes without duplicates. Invalid workspace roots/revisions cannot invoke sibling commands.
- [ ] Admin/Gateway behavior, unrelated plans/releases/tools and discount built-in ownership remain unchanged. No persistent environment was altered in this implementation task.

## Validation

Use the launcher's Commerce implementation worktree. Before the first Node command: `command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"`.

- [ ] Extend `tests/system-commerce-tool-sync.test.ts`, `tests/commerce-lifecycle.test.ts`, `tests/publication-storage-release-delta.test.ts` and `tests/policy-operation-registry.test.ts`; add `tests/commerce-product-discovery-setup.test.ts`. Run `npm test -- tests/system-commerce-tool-sync.test.ts tests/commerce-lifecycle.test.ts tests/publication-storage-release-delta.test.ts tests/policy-operation-registry.test.ts tests/commerce-product-discovery-setup.test.ts`.
- [ ] Extend `tests/system-commerce-tool-sync-postgres.test.ts` with the four-tool, owned response-instruction/schema/behavior, pin-preservation and no-op cases; run `node scripts/run-system-commerce-tool-sync-postgres.mjs`. Verify a response-instruction-only change creates the exact successor and a conflicting manual instruction fails before activation. Preserve its owned disposable PostgreSQL/container credentials/cleanup checks; never substitute a deployment database.
- [ ] In setup unit/process fixtures, assert exact subprocess cwd/argument order, explicit root validation, fresh-schema planning, zero paid embedding calls in dry run, migration drift, each stage failure, restart/resume, production confirmation and bounded receipts containing all four actions. Include actual Shared-generated browse/shipping/presentation fragments through authoring and publication, unchanged product output hashes, and unsupported/missing-scope store states that do not alter the four-tool inventory. Use injected child-process/fixture seams, not production flag bypasses.
- [ ] Add inspection and preview regression coverage to `tests/studio-integration.test.ts`, `tests/feature-preview-composition.test.ts`, `tests/preview-service.test.ts` and `tests/test-conversations-screen.test.tsx`; run `npm test -- tests/studio-integration.test.ts tests/feature-preview-composition.test.ts tests/preview-service.test.ts tests/test-conversations-screen.test.tsx`. Assert the actual selected response contract/instruction/hash, incompatible identity handling, stored RELEASE preservation and the raw-preview label; do not report this as host composition parity.
- [ ] Run `npm run typecheck`, `npm run lint`, `npm run build` and `git diff --check`. Record exact dependency/Database revisions and any accepted baseline separately.
- [ ] SYSTEM-TEST-001 owns the complete real-child-command disposable cross-repository setup proof. This task must supply its fixture/test seam and local stage tests; a mocked child process alone must not be reported as an actual end-to-end setup execution.
- [ ] Confirm no persistent `commerce:sync-tools --apply` / `commerce:setup-discovery --apply`, broad seed, service-startup hook, grant rewrite or customer send occurred.

## Stop Condition

Stop if accepted dependencies, source ownership, exact release preservation, frozen contracts or operator prerequisites cannot be reconciled without expanding scope. Return the concrete conflict to the architect. After scoped implementation and required validation, set status to `review`, complete the report and return to `moda_architect`; do not mark complete, deploy, publish to a persistent environment, run a downstream task or claim that the future operator setup has already happened.

## Implementation Notes

“All stores” means every otherwise authorized connected store admitted by current shop, plan, subscription, provider, release and turn controls. Database supplies the required feature and plan mappings; this task makes the standard capabilities and diagnostics honor them. The operator wrapper is explicit and repeatable, while the actual online conversation keeps using existing MCP and host controls.

## Completion Report

### Status

Not Started — defined but not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The developer will select a canonical operator checkout containing accepted revision pins and supply existing environment/actor/embedding configuration after compatible consumers are deployed.

### Unresolved Issues

No persistent environment prerequisites, migration state, actor configuration or actual publication have been verified by this task definition.

### Architectural Concerns

None beyond the explicit ownership, preservation and operational gates above.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
