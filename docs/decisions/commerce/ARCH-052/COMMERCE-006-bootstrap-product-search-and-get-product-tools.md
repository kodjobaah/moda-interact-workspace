---
id: ARCH-052-COMMERCE-006
architecture_id: ARCH-052
title: Implement version-controlled Commerce system-product-tool environment sync script
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-052-SHARED-010
enables:
- ARCH-052-COMMERCE-007
- ARCH-052-MCP-003
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: 2026-10-30
---

# ARCH-052-COMMERCE-006: Implement version-controlled Commerce system-product-tool environment sync script

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`.

Materialised and executed through the canonical task launcher in dedicated parent and implementation worktrees. This implementation adds an explicitly invoked sync command; no persistent Commerce environment was changed.

## Objective

Implement an **explicitly invoked, idempotent environment synchronisation command** that installs or updates the two version-controlled product MCP tool definitions through the **existing Commerce tool-authoring and immutable release lifecycle**, without manual Commerce Studio authoring or ordinary service-startup mutations. A read-only dry run must show the proposed changes before an operator applies them.

## Context

- `src/commerce/bootstrap/merchant-knowledge.ts` is the inspected example of idempotent tool identity creation, draft publication, capability binding and immutable release activation. Reuse its proven lifecycle **mechanics**, not its merchant-knowledge-specific settings.
- `src/commerce/execution/policy-operation-authoring.ts` already registers operations and derives publication schemas from Shared. `products.search` and `products.get` are **not yet registered** in the uploaded snapshot.
- The existing seeded billing Feature is **`product_search`** (`MERCHANT_OPT_IN`, `systemRequired: false`); no `recovery_initial_outreach` Feature exists in the seed. Associate both product tools with the existing `product_search` Feature. Do **not** create a second Feature or change pricing/merchant preferences in this task.
- `MCP-003` implements the provider-neutral `products.search`/`products.get` execution handlers. This task defines and prepares their published descriptors. `COMMERCE-007` runs the accepted sync against `TEST` **after** both implementation tasks are architect-accepted.
- The Commerce repository already uses `.mjs` operational scripts and has `esbuild` as an installed development dependency; it does **not** declare `tsx` or `ts-node`. Use the executable approach specified below, rather than inventing a TS runner.

## Scope

Implement the **one product-tool synchronisation capability** in `moda-interact-commerce`:

1. Source-controlled canonical product tool definitions with fixed names, feature/capability keys, versions, policy-operation mappings and response templates.
2. A read-only environment comparison/planning function and an authorised apply function, both using existing Prisma models, `CommerceLifecycle`, feature-capability authoring storage and release publication mechanisms.
3. One command-line script accepting an explicit target environment and mode (`--dry-run` or `--apply`) and writing a bounded structured outcome.
4. Tests for definitions, planning, release publication, CAS conflict, reconciliation, script arguments, multi-environment isolation and repeat-run idempotence, including disposable-database integration coverage.
5. Update the Commerce package script so an operator can run the command as documented below.

## Out of Scope

- **Do not execute `--apply` against a persistent TEST, STAGING, DEVELOPMENT or PRODUCTION environment in this implementation task.** That is the separate accepted publication operation in `COMMERCE-007` (TEST only).
- No generic new deployment service, background cron, startup auto-publisher, Commerce Studio manual tool creation, separate registry, table/column/migration, product database/cache, provider product reads, MCP handler implementation, published discount-tool authoring, merchant preference edits, feature entitlement changes, secret-bearing logs or other repository modifications.
- Do not modify the existing `merchant_knowledge_lookup` tool or replace the existing Shopify conversation `shopify.searchProducts` operation. No legacy adapters: this is pre-production work.

## Requirements

**Attempt 14 contract gate (normative):** Update the Commerce `@modainteract/moda-interact-shared` package/lockfile to the version published by SHARED-010 (expected 2.7.0). The canonical product drafts must use its `CommerceToolInputs`/`CommerceToolOutputs`, including nullable `variantId` and optional provider taxonomy ID data. Audit the existing Commerce `src/commerce/products/index.ts` and its tests for consumers that assume every product `variantId` is non-null; narrow safely at points requiring a real Shopify variant ID, and never fabricate a Woo variant ID. This is necessary for this repository to compile against SHARED-010. The existing `discounts.getOptions` preview producer may continue to omit the optional `cursor` field; do not add a second discount pagination engine in Commerce. Keep code-driven `product_search` feature entitlement; do not create an `initial_outreach` entitlement or bypass merchant opt-in. Existing Studio release lifecycle and script flags remain as already specified; this is not a discount-tool publication task.


**Canonical ownership and feature:**

- Fixed identities are `commerce_search_products` and `commerce_get_product` for both the **published tool name** and `CommerceCapability.key`; associate both with existing `Feature.key = "product_search"`.
- `CommerceToolDraftDefinition.definitionVersion` starts at `1.0.0`. The two policy-operation keys are `products.search` and `products.get`, both `operationVersion = "1.0.0"`. Definition version and operation version are different fields and must never be confused.
- `product_search` must exist, be active, have `activationMode = MERCHANT_OPT_IN` and `systemRequired = false`; otherwise fail with a bounded `FEATURE_CONFLICT` outcome. The script must not silently create a new Feature or change merchant entitlements.
- Only approved `CommerceLifecycle` and the existing feature-capability storage APIs may make publication mutations. A source-owned tool identity is **not** permission to overwrite a human-authored tool with the same name. Unexpected existing tool/capability ownership is a hard conflict.

**Executable CLI:**

- Add the exact npm script `"commerce:sync-tools": "node scripts/sync-system-commerce-tools.mjs"` to `moda-interact-commerce/package.json` (no new runtime package).
- Implement `scripts/sync-system-commerce-tools.mjs` as a Node `.mjs` wrapper using the repository's existing `esbuild` package to bundle `src/commerce/bootstrap/system-commerce-tool-sync.cli.ts` for Node 24, and execute its exported command. Keep generated output transient and outside Git-tracked source; do not import Next.js `server-only` composition inside the standalone CLI. Reuse `PrismaPublicationStorage`/`CommerceLifecycle` in the server-only-independent composition.
- The CLI accepts **exactly one** of `--dry-run` and `--apply`, and requires `--environment=local|test|development|staging|production`. Normalise to the existing `Environment` enum (`LOCAL`, `TEST`, `DEVELOPMENT`, `STAGING`, `PRODUCTION`). Unknown, duplicate or contradictory flags exit non-zero **before a database mutation**.
- Require a configured `DATABASE_URL` and `COMMERCE_SYSTEM_TOOL_ACTOR_EMAIL` for both modes. Resolve the latter to **exactly one active `SUPER_ADMIN`** from `PlatformAdmin` before applying; never treat the email alone as an authentication token or use the development bypass. Require an explicit external/operational privileged invocation with database access; this is **not** a public endpoint.
- For `--apply --environment=production`, additionally require `--confirm-production`; the ARCH-052 COMMERCE-007 release task must **not** use this combination. Enforce target environment identity against `DEPLOYMENT_ENVIRONMENT_NAME` (normalising case) and fail on mismatch so a TEST invocation cannot accidentally update a production database. Neither the CLI nor its tests should embed credentials.
- Publish/release mutations are disabled by default. `--dry-run` must use reads only: never create a tool, draft, capability, release, audit event or pointer. `--apply` must first compute the same plan and abort if preconditions have changed before mutation.

**Reconciliation and releases:**

- Read the `CommerceTool`, `CommerceToolRevision`, `CommerceCapability`, existing `Feature`, and environment-specific `CommerceReleasePointer` plus its immutable release members. Compare source definitions by canonical JSON/content hash using the existing Commerce publication helpers, **not** source-order/string formatting.
- Compute one deterministic action per canonical tool: `CREATE`, `PUBLISH`, `PIN_NEW_REVISION` or `NO_CHANGE`; do not create/update unrelated tools. A given `definitionVersion` whose stored content differs from the canonical content is a **conflict** (do not silently replace it).
- If a new version is explicitly approved in source, author and publish its new revision using existing draft and publish commands, and create a successor immutable release pinning it. Preserve every unrelated capability pin, response contract and Feature behaviour snapshot. Existing `createSuccessorRelease` only appends a capability: **do not use it to replace a pin already in a release**. Use the existing full `createRelease` path only when it can preserve these immutable contents; otherwise fail with `RELEASE_RECONCILIATION_UNSUPPORTED` and return to the architect. Do not rewrite existing releases.
- On first install, append missing product capabilities using existing `createSuccessorRelease` where appropriate; when there is no active release, use the existing approved initial-release mechanism, not an improvised release table write. Activate a new release with the existing compare-and-set pointer command. Detect CAS conflicts and abort/replan; do not blindly retry in a loop.
- A second `--apply` with unchanged definitions and the same active release must return `UNCHANGED`, creating **zero** new drafts, revisions, capabilities, releases, audits or pointer writes.
- Validate that product policy operations are registered with `createPolicyOperationAuthoringRegistrations()` and agree with the published Shared-008 input/output schemas. Do not call Shopify or WooCommerce or require MCP to be online during `--dry-run` or in-memory tests. A release activation may occur only after COMMERCE-007 confirms MCP-003 is accepted.

**Diagnostics:**

- Use `@modainteract/moda-interact-shared/logging` for new structured Node logging, log unexpected exceptions at the appropriate boundary and propagate non-zero failure. Include bounded action/error codes; do not log raw DB connection strings, credentials, provider tokens, personal data, product URLs, coupon values or unbounded definitions.
- Output a structured, human-readable plan/receipt containing target environment, mode, action names, definition versions/content hashes, previous and new release IDs, status and counts. Never print secret material.
- Follow mirrored task-branch/worktree isolation and the existing Completion Report and architect acceptance process; do not start `COMMERCE-007` from this task.

## Work Items

- [x] Define the two exact canonical tool descriptors and verify they parse with the existing `CommerceToolDraftDefinitionSchema`.
- [x] Add `products.search` and `products.get` to the existing `POLICY_OPERATIONS` literal union in `src/commerce/tool-definition/contracts.ts`, and register both in `POLICY_OPERATION_CONTRACTS` with published Shared-008 schemas. Do not replace the existing enum or any existing entries.
- [x] Implement a read-only `planSystemCommerceToolSync` and existing-lifecycle-backed `applySystemCommerceToolSync`, with no provider HTTP or private API requests.
- [x] Implement the `.mjs` CLI and its standalone composition, with explicit flags, environment checks, active `SUPER_ADMIN` resolution and safe output.
- [x] Add the `commerce:sync-tools` package command; do not wire the sync into `dev`, `build`, `start`, Render startup or cron.
- [x] Add focused in-memory tests and a disposable PostgreSQL integration run showing first apply, same-input no-op, changed-version plan, conflict, CAS race, dry-run isolation, unrelated-member preservation and rejection of production/mismatched environment.
- [x] Record exact changed files, test commands, validation and remaining issues. Set task to `review` and stop.

## Interfaces / Contracts

**1. Canonical source registry** — create `src/commerce/bootstrap/system-product-tools.ts`. Export `SYSTEM_COMMERCE_PRODUCT_TOOLS` exactly as this typed, immutable metadata (the complete executable drafts are derived in the same module from the published Shared schemas and `getPolicyOperationAuthoringDescriptor`):

```typescript
export const SYSTEM_COMMERCE_PRODUCT_TOOLS = [
  {
    name: "commerce_search_products",
    displayName: "Search Products",
    capabilityKey: "commerce_search_products",
    featureKey: "product_search",
    definitionVersion: "1.0.0",
    operation: "products.search",
    operationVersion: "1.0.0",
    inputContract: "commerce_search_products",
    outputContract: "commerce_search_products",
  },
  {
    name: "commerce_get_product",
    displayName: "Get Product",
    capabilityKey: "commerce_get_product",
    featureKey: "product_search",
    definitionVersion: "1.0.0",
    operation: "products.get",
    operationVersion: "1.0.0",
    inputContract: "commerce_get_product",
    outputContract: "commerce_get_product",
  },
] as const;
```

**Complete draft-construction contract:** use the existing `getPolicyOperationAuthoringDescriptor(...)` to obtain the exact published input schemas. Build these two drafts verbatim (only type imports/formatting may differ):

```typescript
import type { CommerceToolDraftDefinition } from "../tool-definition";
import { InputSchemaSchema } from "@modainteract/moda-interact-shared/commerce";
import { getPolicyOperationAuthoringDescriptor } from "../execution/policy-operation-authoring";

export const SYSTEM_PRODUCT_TOOL_DRAFTS: readonly CommerceToolDraftDefinition[] = [
  {
    name: "commerce_search_products",
    definitionVersion: "1.0.0",
    description: "Search products from the authorised shop using provider-backed reads.",
    inputSchema: InputSchemaSchema.parse(
      getPolicyOperationAuthoringDescriptor("products.search", "1.0.0").argumentsSchema,
    ),
    execution: {
      kind: "POLICY_OPERATION",
      operation: "products.search",
      operationVersion: "1.0.0",
      arguments: {
        query: { input: "query" },
        availableOnly: { input: "availableOnly", omitIfMissing: true },
        limit: { input: "limit", omitIfMissing: true },
        maximumPrice: { input: "maximumPrice", omitIfMissing: true },
        cursor: { input: "cursor", omitIfMissing: true },
      },
    },
    responseTemplate: {
      kind: "nunjucks",
      runtimeVersion: "nunjucks.v1",
      source: "Product search complete. Use the structured result for product details.",
      unavailable: "Product information is unavailable.",
    },
  },
  {
    name: "commerce_get_product",
    definitionVersion: "1.0.0",
    description: "Retrieve one product or variant from the authorised shop.",
    inputSchema: InputSchemaSchema.parse(
      getPolicyOperationAuthoringDescriptor("products.get", "1.0.0").argumentsSchema,
    ),
    execution: {
      kind: "POLICY_OPERATION",
      operation: "products.get",
      operationVersion: "1.0.0",
      arguments: {
        productId: { input: "productId" },
        variantId: { input: "variantId" },
      },
    },
    responseTemplate: {
      kind: "nunjucks",
      runtimeVersion: "nunjucks.v1",
      source: "Product lookup complete. Use the structured result for product details.",
      unavailable: "Product information is unavailable.",
    },
  },
];
```

The `InputSchemaSchema.parse(...)` call is required because the authoring descriptor has a generic JSON-schema TypeScript type while published tools require the constrained Commerce input subset. An incompatible generated schema must fail the task validation; never cast it to bypass the validator. Optional/defaulted product-search inputs must be omitted from the mapped operation arguments when not supplied, and MCP-003 must apply the published Shared defaults.

Add `"products.search"` and `"products.get"` to the existing `POLICY_OPERATIONS` tuple in `src/commerce/tool-definition/contracts.ts`, because **the inspected current enum excludes them** and the tool draft validator would otherwise reject both. Add corresponding registrations to `POLICY_OPERATION_CONTRACTS` in `src/commerce/execution/policy-operation-authoring.ts`, with `inputValidator` and `outputValidator` set to the respective `CommerceToolInputs` / `CommerceToolOutputs` members from the published Shared-008 contract. Preserve `shopify.searchProducts` and all other operations. MCP-003 owns runtime execution; Commerce's registrations are publication/authoring metadata only.

A standalone script must not introduce a second result envelope or imply that product search is only an outreach feature. These generic product tools use the existing `product_search` Feature, which already controls merchant entitlement. Do not manually author an additional Feature or capability in Studio.

**2. Sync engine** — create `src/commerce/bootstrap/system-commerce-tool-sync.ts` with these exported interfaces and entrypoints. Keep business/release rules in the engine, not in Zod refinements:

```typescript
import type { PrismaClient } from "@prisma/client";
import type { CommerceLifecycle } from "../publication/lifecycle";
import type { Environment, Principal } from "../publication/ports";

export type SystemToolSyncAction = {
  tool: "commerce_search_products" | "commerce_get_product";
  action: "CREATE" | "PUBLISH" | "PIN_NEW_REVISION" | "NO_CHANGE";
  definitionVersion: string;
  contentHash: string;
};

export type SystemToolSyncPlan = {
  environment: Environment;
  currentReleaseId: string | null;
  actions: SystemToolSyncAction[];
  status: "CHANGES_REQUIRED" | "UNCHANGED";
};

export type SystemToolSyncReceipt = Omit<SystemToolSyncPlan, "status"> & {
  status: "APPLIED" | "UNCHANGED";
  activeReleaseId: string;
  toolRevisionIds: Record<string, string>;
  capabilityIds: Record<string, string>;
};

export type SystemToolSyncDependencies = {
  prisma: PrismaClient;
  lifecycle: CommerceLifecycle;
  environment: Environment;
  principal: Principal;
};

export async function planSystemCommerceToolSync(
  dependencies: SystemToolSyncDependencies,
): Promise<SystemToolSyncPlan>;

export async function applySystemCommerceToolSync(
  dependencies: SystemToolSyncDependencies,
): Promise<SystemToolSyncReceipt>;
```

`plan...` is read-only. `apply...` rechecks the plan, applies existing audited lifecycle operations with deterministic operation IDs scoped to environment/tool/version/content and expected CAS values, verifies the resulting pointer and returns the receipt. Unsupported/conflicting state is an error, not a silent overwrite.

**3. CLI** — create `src/commerce/bootstrap/system-commerce-tool-sync.cli.ts` for standalone server-side dependency construction and argument handling, and `scripts/sync-system-commerce-tools.mjs` as the executable wrapper using the existing `esbuild` dependency. Export the two engine functions through `src/commerce/bootstrap/index.ts`. Add npm command:

```json
{
  "scripts": {
    "commerce:sync-tools": "node scripts/sync-system-commerce-tools.mjs"
  }
}
```

Required usage (these commands must work after implementation):

```bash
npm run commerce:sync-tools -- --environment=test --dry-run
npm run commerce:sync-tools -- --environment=test --apply
```

`--apply` is never part of normal startup. Production requires a separate explicit future authorisation and `--confirm-production`.

## Dependencies

- `ARCH-052-SHARED-010` — publish the required product and discount discovery contract update before this repository consumes it.

## Enables

- `ARCH-052-COMMERCE-007` — authorised TEST script execution, only after this implementation and MCP-003 are accepted.
- `ARCH-052-MCP-003` — handler implementation can use the named descriptors; it must not depend on live TEST publication.
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] Tool names, `product_search` Feature key, input/output contracts, versions and policy operation keys match exactly; no new Feature or database schema.
- [x] The CLI `--dry-run` is read-only, reports a deterministic plan and refuses invalid arguments, unapproved actor or mismatched environment.
- [x] The script's apply path uses existing audited Commerce publication lifecycle commands and preserves unrelated release members, response contract and Feature behaviour.
- [x] First installation is repeatable; a second identical apply makes zero changes. Canonical-content conflicts and stale CAS fail without overwriting state.
- [x] `--apply` is gated; no implicit startup or scheduled environment mutation is introduced.
- [x] Source-code tests and a disposable PostgreSQL rehearsal demonstrate the agreed behaviour; no persistent environment has been modified by this task.

## Validation

- [x] Unit tests for registry/definitions/CLI parser/planner/reconciliation (including wrong environment, SUPER_ADMIN denial and no-op) via the repository's existing Vitest setup.
- [x] Disposable PostgreSQL tests for audited tool creation, capability binding, release-member preservation, pointer activation, rerun no-op and conflict handling.
- [x] Run the Commerce repository's **existing declared** `typecheck`, `lint` and applicable build validation scripts, plus `git diff --check`. Record actual commands and results; do not invent nonexistent npm scripts.
- [x] Confirm `git diff --check` and no deployment state was mutated.

## Implementation Notes

Authorised workspace-relative source/test locations:

- `moda-interact-commerce/src/commerce/bootstrap/system-product-tools.ts` (new)
- `moda-interact-commerce/src/commerce/bootstrap/system-commerce-tool-sync.ts` (new)
- `moda-interact-commerce/src/commerce/bootstrap/system-commerce-tool-sync.cli.ts` (new)
- `moda-interact-commerce/src/commerce/bootstrap/index.ts` (exports)
- `moda-interact-commerce/src/commerce/execution/policy-operation-authoring.ts` (two registrations)
- `moda-interact-commerce/src/commerce/tool-definition/contracts.ts` (extend existing POLICY_OPERATIONS literal)
- `moda-interact-commerce/scripts/sync-system-commerce-tools.mjs` (new command wrapper)
- `moda-interact-commerce/package.json` (script only)
- `moda-interact-commerce/tests/system-commerce-tool-sync.test.ts` (new)
- `moda-interact-commerce/tests/system-commerce-tool-sync-postgres.test.ts` (new)

Read existing `src/commerce/publication/lifecycle.ts`, `src/commerce/integration/backend/publication-storage.ts` and `src/studio/features/persistence.ts` for **reuse**; do not rewrite these frameworks. If the required invariant cannot be achieved through an existing published operation, stop and report the exact missing operation to `moda_architect` rather than adding unapproved mutations.

Use the workspace's declared Node bootstrap. The `.mjs` wrapper must use `esbuild` to create a transient Node-only bundle from the `.cli.ts` entrypoint, with Node-compatible ESM output and package imports resolved from the Commerce installation. It must not import Next.js `server-only` composition or add a second TS execution dependency. Unhandled exceptions must be logged through the Shared logger and result in a non-zero exit.

## Stop Condition

After completing Work Items, Acceptance Criteria and required Validation, update Completion Report and status to `review`, return to `moda_architect` and **STOP**. Do not execute COMMERCE-007, change a live environment, merge or push `main`.

## Completion Report

### Status

Accepted Complete at Attempt 1. No persistent Commerce environment was changed, and COMMERCE-007 was not started.

### Files Changed

- `package.json`, `package-lock.json`
- `src/commerce/bootstrap/index.ts`
- `src/commerce/bootstrap/system-product-tools.ts` (new)
- `src/commerce/bootstrap/system-commerce-tool-sync.ts` (new)
- `src/commerce/bootstrap/system-commerce-tool-sync.cli.ts` (new)
- `src/commerce/execution/policy-operation-authoring.ts`
- `src/commerce/tool-definition/contracts.ts`
- `src/commerce/products/index.ts`, `src/commerce/products/recommendations.ts`, `src/commerce/discounts/evaluator/evaluator.ts` (Shared 2.7.0 nullable variant compatibility)
- `scripts/sync-system-commerce-tools.mjs` (new)
- `scripts/run-system-commerce-tool-sync-postgres.mjs` (new disposable test harness)
- `tests/system-commerce-tool-sync.test.ts` (new)
- `tests/system-commerce-tool-sync-postgres.test.ts` (new)
- `tests/policy-operation-registry.test.ts`

### Work Completed

- Added the exact source-owned `commerce_search_products` and `commerce_get_product` descriptors, both on the existing `product_search` Feature, with Shared 2.7.0 schemas and registered `products.search@1.0.0` / `products.get@1.0.0` authoring contracts.
- Implemented deterministic read-only planning and audited lifecycle application. The sync checks Feature policy, tool/capability ownership, canonical revision hashes, environment pointer and immutable release contents; it fails closed on identity/content/Feature conflicts or stale CAS and makes no provider requests.
- Added the standalone esbuild-backed CLI, exact `commerce:sync-tools` npm command, strict mode/environment parsing, production confirmation, deployment-environment matching, active `SUPER_ADMIN` resolution, shared structured logging and bounded output. It is not wired into startup, build or scheduled work.
- Added focused in-memory and disposable-PostgreSQL coverage. The PostgreSQL rehearsal verified dry-run isolation, audited tool/revision/capability creation, release activation, preservation of an unrelated release member/response contract/Feature snapshot, repeat-run no-op and Feature-conflict rejection.
- Updated existing product consumers for Shared 2.7.0's nullable `variantId`; recommendation operations narrow to non-null IDs where a real Shopify variant is required, without fabricating Woo variant IDs. Updated the existing registry contract test for the two new operation registrations.
- No schema/migration, Feature, entitlement, persistent Commerce environment or deployment state was changed. No COMMERCE-007 action was performed.

### Validation Results

- `npm exec -- vitest run tests/system-commerce-tool-sync.test.ts tests/policy-operation-registry.test.ts` — 2 files passed, 11 tests passed.
- `node scripts/run-system-commerce-tool-sync-postgres.mjs` — accepted migrations passed; disposable PostgreSQL test passed; cleanup passed with zero owned PostgreSQL containers remaining.
- `npm run commerce:sync-tools -- --environment=test --dry-run` with `DATABASE_URL` and `COMMERCE_SYSTEM_TOOL_ACTOR_EMAIL` removed and `DEPLOYMENT_ENVIRONMENT_NAME=test` — wrapper bundled/launched, emitted bounded `DATABASE_UNAVAILABLE`, and exited non-zero before database access.
- `npm run typecheck` — passed.
- `npm run lint` — 0 errors, 15 warnings in existing files outside the task's changed files.
- `npm run build` — passed; emitted the existing Nunjucks dynamic-dependency bundling warning.
- `git diff --check` — passed.
- `npm test` — not fully green: 200 files discovered, 179 passed, 6 skipped, 15 failed; 1,473 tests passed, 16 skipped and 13 failed. Failures included database/Redis suites requiring dedicated harnesses, UI/readiness failures or timeouts during the full parallel run, and the registry test's stale expected count of seven. That registry expectation was corrected and its test passed in the final focused rerun; the full suite was not rerun after the focused correction.
- No persistent environment or deployment state was mutated. The only `--apply` execution was against the invocation-owned disposable PostgreSQL database.

### Deviations

The requested database-backed cases are grouped in one disposable PostgreSQL test. CAS race and changed-version replacement reconciliation are covered by in-memory lifecycle tests; the PostgreSQL rehearsal covers first publication, immutable unrelated-member preservation, no-op, dry-run isolation and Feature-conflict handling. The full repository `npm test` remains non-green for the reasons recorded above.

### Assumptions

The launcher packet is authoritative: dependency `ARCH-052-SHARED-010` was complete, Shared 2.7.0 was installed, and task-owned parent/implementation worktrees and the database submodule were prepared at their recorded commits.

### Unresolved Issues

Full-suite failures outside the focused checks remain unresolved: database/Redis tests require their dedicated disposable harnesses, and several UI/readiness tests failed or timed out in the broad parallel run. No persistent database credentials/environment were used for a successful operator CLI invocation; parser/authorization rules and the fail-closed missing-database path were tested.

### Architectural Concerns

No contract/publication gap was found in the focused implementation checks. The sync uses the existing Commerce lifecycle/storage APIs and rejects unsupported immutable-release reconciliation rather than rewriting releases.

### Physical Worktree Evidence

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-COMMERCE-006`, branch `task/ARCH-052-COMMERCE-006`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-COMMERCE-006`, branch `task/ARCH-052-COMMERCE-006`.
- Database submodule was initialized by the launcher at `af77c594ecbfc78c26d01c0021a090830884bbff`.
- Attempt 1 claim was committed and pushed by the launcher as parent commit `b580bbc03c39c5f2d123b095c1f93ce18ac9a725`. Implementation commit `7c2979cbd90626275b70085b158e613957e33edf` and parent report commit `5e21cf73ec5a7d28753b05b734acf3abf040f4b3` are published on their respective `task/ARCH-052-COMMERCE-006` branches. The implementation remote ref was verified to match its commit; `origin/main` remains unchanged.
- No merge or push to `main` was performed.

## Architect Review

### Review Status

Accepted Complete at Attempt 1.

### Review Notes

Reviewed implementation commit `7c2979cbd90626275b70085b158e613957e33edf`, the task report and the defined scope. The two canonical product descriptors use the existing `product_search` Feature and Shared 2.7.0 contracts. The sync planner is read-only; apply uses the existing audited lifecycle and feature-capability storage, guards system ownership and Feature policy, preserves unrelated immutable release members and behavior snapshots, checks CAS, and verifies the activated release. The standalone CLI validates mode, environment and active SUPER_ADMIN selection, requires explicit apply, and has no startup or scheduled wiring. No persistent environment was changed and no blocking implementation issue was found.

The focused suite, disposable PostgreSQL rehearsal, typecheck, lint, build and diff check pass as reported. The exploratory full `npm test` run was not green: 13 failures were reported, including a registry expectation later corrected and database/Redis or UI/readiness failures and timeouts; the full suite was not rerun after that correction. This remains an explicit validation caveat and is not represented as a passing full-suite result. The task-required focused and disposable database validations are complete.

### Reviewed Files

- Canonical system product tool definitions and sync engine.
- Standalone CLI and `.mjs` wrapper.
- Policy-operation registrations and Commerce tool-definition contract.
- Nullable variant compatibility changes in product and discount consumers.
- Focused unit and disposable PostgreSQL tests.
- This task's Completion Report, implementation branch and VCS evidence.

### Validation Reviewed

Reviewed the report's 11 focused tests, disposable PostgreSQL rehearsal and cleanup, fail-closed CLI wrapper invocation, typecheck, lint (0 errors, 15 warnings in unchanged files), build, and `git diff --check`. The implementation branch is clean at `7c2979c` and its task remote ref matches. Validation was reviewed from the durable report; it was not rerun during architect review.

### Architecture Conformance

Conforms to ARCH-052 and the task boundary. No persistent Commerce environment or deployment was mutated; the only `--apply` reported was against the invocation-owned disposable PostgreSQL database. COMMERCE-007 remains a separate publication task and was not started.

### Follow-up

`ARCH-052-COMMERCE-007` remains Pending because `ARCH-052-MCP-003` is Pending. MCP-003 remains Pending because its separate dependency `ARCH-052-MCP-005` is Ready, not Complete. No enabled task was started or promoted by this review.
