---
id: ARCH-058-MCP-001
architecture_id: ARCH-058
title: Import and resolve a versioned PostgreSQL reference taxonomy
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 40
executor: codex
claimed_at: 2026-11-04T07:38:22Z
attempt: 1
depends_on:
- ARCH-058-DATABASE-001
- ARCH-058-SHARED-002
enables:
- ARCH-058-MCP-002
- ARCH-058-SYSTEM-TEST-001
created: '2026-11-04'
updated: 2026-11-04
---

# ARCH-058-MCP-001: Import and resolve a versioned PostgreSQL reference taxonomy

## Architecture

Architecture ID: `ARCH-058`. Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`. Normative contracts: `docs/architecture/ARCH-058/contracts.md`. Coordinator: `moda_architect`.

**Defined but not materialised.** This portable definition was prepared from a source snapshot. No task branch, implementation worktree, commit, deployment, import or publication has been performed. Materialise through `/moda-task ARCH-058-MCP-001 --definition <path-to-this-file>` in the canonical developer workspace; the launcher supplies the actual implementation worktree and `MODA_WORKSPACE_ROOT`.

## Objective

Provide the MCP-owned import and runtime read path for a shared public Shopify taxonomy in PostgreSQL/pgvector, then expose that path through the published `commerce_resolve_product_categories` policy operation. A phrase such as “hammer” must produce a small set of real reference category candidates; it must make no assertion about the current merchant's assortment. Make the required `product_search` feature selection agree with Shared so eligible stores do not need a preference opt-in.

## Context

- Admin already has an independent reference-taxonomy workflow and a `REFERENCE_TAXONOMY` embedding configuration. This task reads that existing configuration and credential through its authenticated purpose; it does not change Admin or copy its Redis corpus.
- `src/execution/merchant-knowledge/embedding-runtime.ts` currently hard-codes `MERCHANT_KNOWLEDGE` in the configuration lookup and credential authenticated data. Reusing that function unchanged would select the wrong purpose. Reuse narrow credential/embedding mechanics without changing the merchant-knowledge behavior.
- `src/runtime/service-ports.ts`, `src/runtime/prisma.ts` and `src/runtime/execution-registry.ts` compose actual published execution. Adding an authoring registration alone does not execute a tool.
- `src/capabilities/records.ts` omits the feature activation mode, and `src/capabilities/resolve.ts` currently requires a true merchant preference even for a required feature. DATABASE-001 prepares the feature and plan mappings; this task corrects the MCP projection and diagnostics.
- The supplied snapshot does not establish an approved full taxonomy distribution, its checksum or its category count. Do not invent these values or substitute a rolling upstream branch.

## Scope

In `moda-interact-mcp` only:

1. Add the pinned source manifest, bounded source parser, deterministic import fingerprint and an explicit `taxonomy:sync` command.
2. Implement atomic complete-generation activation using the schema accepted under DATABASE-001.
3. Implement a purpose-correct embedding adapter and exact PostgreSQL category lookup.
4. Wire `taxonomy.resolveCategories` into the existing published execution registry and readiness/diagnostic path.
5. Project required-feature eligibility using the Shared selection rule, preserving ordinary authorization and all optional-feature behavior.
6. Add focused unit and disposable PostgreSQL tests and operator documentation.

## Out of Scope

No schema or migration authored here; no Admin, Gateway, Background or Commerce implementation; no Redis fallback; no merchant product mirror; no per-shop taxonomy copy; no automatic startup import; no queue, import-job table, approximate vector index, automatic generation deletion or generalized vector platform. Do not publish Commerce tools or run the importer against a persistent environment during this implementation task. All mutation and embedding tests use an isolated fixture and a controlled embedding stub.

## Requirements

### Contract and source gates

- Consume the exact published Shared version accepted by ARCH-058-SHARED-002 (target `4.0.0` while the accepted baseline remains `3.1.0`, otherwise the architect-reconciled version), update this repository's package/lockfile, and consume the accepted Database revision through the normal database submodule. Do not import a sibling repository's source or write duplicate public schemas.
- The tool name/capability key is `commerce_resolve_product_categories`; definition version is `1.0.0`; operation is `taxonomy.resolveCategories` with operation version `1.0.0`. Use the input/output members and generic result envelope in the frozen contracts. The model supplies query/limit only; authenticated context supplies shop and environment.
- Add `src/data/reference-taxonomy-manifest.json` for the approved pinned Shopify `2026-08` English distribution, with the immutable source identity, taxonomy version, language, source URL and SHA-256 specified by the contracts. Obtain and verify the actual approved distribution before committing this manifest. No placeholder checksum, guessed count, mutable `main` URL or fabricated category is acceptable. If the approved source cannot be established, stop and report that concrete prerequisite to the architect.
- Preserve canonical category IDs, names, full paths, parent/ancestor identities and level. Validate the complete hierarchy, unique identities, missing parents and cycles before any embedding or database mutation. Keep reference IDs distinct from Shopify `productType`, collections, Woo native categories and Moda `StoreCategory`.
- Resolve source bytes only from the manifest's approved URL or an explicit local `--source` whose bytes match the same trusted manifest. No production `--manifest` override. Test manifest/embedding injection belongs to the isolated harness; it must not become a normal CLI bypass.

### Import command and preparation

- Add `scripts/sync-reference-taxonomy.mjs`, `src/execution/reference-taxonomy/sync.cli.ts`, and `"taxonomy:sync": "node scripts/sync-reference-taxonomy.mjs"` in `package.json`. Reuse the installed Node/TypeScript execution dependencies; do not introduce a second runtime or change normal service startup.
- Accept exactly one of `--dry-run` / `--apply`, require `--environment=local|test|development|staging|production`, and permit the frozen optional `--source=<path>`. Production apply also requires `--confirm-production`; reject unknown/duplicate/incompatible flags before side effects. Compare the explicit target with `DEPLOYMENT_ENVIRONMENT_NAME` and require the configured `DATABASE_URL`.
- The setup orchestrator remains Commerce-owned. This command performs only MCP taxonomy work and emits its stage receipt; it does not call migrations, publish tools, create actors or update embedding settings.
- Dry run uses reads only and performs zero embedding-provider requests, taxonomy writes, generation activation, audits or configuration mutations. Verify source/configuration identity and report the existing generation, planned work and prerequisite gaps. An absent fresh schema is a distinct pending-migration condition, not a successful runtime check or an empty corpus.
- Resolve the environment's `REFERENCE_TAXONOMY` row and credential with the same purpose in both the database lookup and Shared credential AAD. Preserve sealed-keyring lookup and all existing credential bounds. Missing or unsupported configuration must be explicit; do not fall back to merchant-knowledge settings or an environment API key with different authority.
- The fingerprint covers the complete frozen identity: environment, source/version/language, source checksum, embedding provider/model/dimension/index version and embedding-text format version. Produce canonical deterministic input text using the frozen format. An identical, complete, currently active, valid generation is a no-op before any embedding call or write.
- Prepare vectors outside a database transaction. Bound source bytes, category count, text bytes, in-flight batches, retries, provider response bytes and overall elapsed work; include the actual chosen bounds in tests and operator notes. Charge provider calls consistently, preserve cancellation and honor provider retry limits. Every vector must have the configured dimension, finite components and nonzero norm.

### Atomic activation and reader consistency

- Use the normal Database-owned tables and constraints. Do not issue ad hoc DDL or rewrite an applied migration. Before activation, validate exact expected count, every embedding and complete provenance.
- In one bounded final transaction, acquire a transaction-scoped advisory lock for the environment/source/language corpus, including first activation. Re-read the active-generation baseline, lock/read the existing embedding-configuration row through commit, and compare its embedding tuple with the prepared candidate. Credential rotation alone with an unchanged tuple does not require re-embedding.
- Insert the complete generation and categories in bounded parent-before-child statements so same-generation parent foreign keys hold. Validate stored count/constraints and a smoke lookup before atomically switching the active marker. An identical concurrent winner is a no-op; a different active winner or changed embedding tuple is an explicit conflict. A failed transaction preserves the previous active generation.
- Completed generations are immutable and retained. Do not automatically reactivate an older inactive fingerprint or silently roll back configuration; an intentional rollback needs the documented explicit operator procedure. No garbage collector in this increment.
- Runtime reads pin one active generation and its complete embedding tuple before embedding the query; enforce a bounded SQL statement deadline. Recheck compatibility after query embedding. Scope the candidate relation to that generation before calculating `<=>` distance so incompatible dimensions never reach the operator. Use parameterized values and deterministic category-ID tie-breaking; no model-provided SQL or identifiers.
- Start with exact cosine search and return at most ten candidates. The result limit bounds output, not the number of vectors scanned. Measure fixture query work without claiming an unmeasured production latency or corpus size.

### Execution, readiness and eligibility

- Implement the new adapter under `src/execution/reference-taxonomy/` and register it in the existing `src/runtime/service-ports.ts` / `src/runtime/prisma.ts` composition. Reuse the existing current-release, descriptor, entitlement, unique-handler, deadline and output validation checks in `src/runtime/execution-registry.ts`; do not route around them.
- Return the frozen success data: `CANDIDATES` or `NO_CANDIDATES` with generation/source/version/language and bounded candidates; or the narrow `UNAVAILABLE` data branch with `NOT_READY` / `TEMPORARY_UNAVAILABLE` where the frozen policy permits. Reference distance is retrieval ordering, not confidence, merchant coverage, stock or a product claim.
- Readiness diagnostics and setup receipts must detect absent schema, no active corpus and incompatible provenance; readiness is an operational signal distinct from authorization. Keep the authorized resolver descriptor and immutable grant/manifest identity stable when operational readiness changes. Do not remove it from discovery or churn a retained grant because a corpus is temporarily unavailable. Recheck readiness at invocation and use only the frozen permitted `NOT_READY` / temporary-unavailable data branches; deterministic schema/contract errors retain the hard error path. The independent provider product tools remain independently eligible.
- Only classified optional operational failures enter the successful unavailable-data branch. Malformed provider/vector/result payloads, invalid contract/configuration identity, authorization errors, cancellation, stale invocation and programming errors retain the existing hard failure path. Do not convert these to `NO_CANDIDATES`, and do not weaken the generic runner's terminal-error handling.
- Extend `src/capabilities/records.ts` to carry the exact feature activation mode, and use the Shared selection rule in `src/capabilities/resolve.ts` and its exclusion diagnostics: active feature plus eligible subscription/plan mapping, with `ALWAYS_ENABLED` independent of absent/false merchant preference; optional features still require their preference. Preserve active-shop, supported-platform, active/trial subscription, plan, current release, grant and provider-installation gates.
- Add a decisive parity fixture for eligible Shopify and Woo shops on free and paid plans with missing/false `product_search` preferences. Ineligible subscriptions, missing/disabled plan mappings, inactive shops and disconnected providers remain excluded. This task does not write preferences or bypass an entitlement failure.

### Logging and operational evidence

Follow `docs/observability/shared-logging.md` using `@modainteract/moda-interact-shared/logging`. At the owning source boundary, preserve actual sanitized provider/SDK/Prisma errors and causes, safe status/request IDs and a separate Moda reason code. Never invent provider errors for a database-only failure. Bound/redact source text before the generic logger; no secrets, vectors, full taxonomy or customer query text in receipts. Logger failure must not alter activation or tool results.

Use the frozen schema-versioned receipt, including target environment/mode, safe source fingerprint, generation/count and explicit stage status/code. Return nonzero on failure. Never report success for a partial import or hide an earlier completed stage. No exact corpus count or production execution claim is valid without recorded evidence.

## Work Items

- [ ] Confirm accepted Database/Shared artifacts and approved source manifest; record their exact immutable identities.
- [ ] Add bounded parser/manifest validation, deterministic text/fingerprint logic and purpose-correct embedding resolution.
- [ ] Implement dry-run planning, identical-active no-op, outside-transaction preparation and atomic activation.
- [ ] Implement the exact PostgreSQL reader, readiness diagnostics and published policy adapter.
- [ ] Correct required-feature selection and diagnostic parity without changing optional features.
- [ ] Add focused unit, actual composition and disposable PostgreSQL tests; document the operator command and rollback boundary.
- [ ] Complete the Completion Report, set this task to `review`, return to the architect and stop.

## Interfaces / Contracts

`docs/architecture/ARCH-058/contracts.md` is the single normative source for wire shapes, source identity, database invariants, embedding-text/fingerprint format, CLI flags and receipts. Shared owns structural schemas and serialization; MCP owns readiness, hierarchy, import consistency and retrieval business rules. Do not put those business rules into new Zod refinements or widen the Commerce schema subset beyond the explicit Shared-owned contract changes.

Primary implementation touchpoints are `src/data/reference-taxonomy-manifest.json`, `src/execution/reference-taxonomy/`, `scripts/sync-reference-taxonomy.mjs`, `src/runtime/prisma.ts`, `src/runtime/service-ports.ts`, `src/runtime/execution-registry.ts`, `src/capabilities/{records,resolve,prisma-reader}.ts`, `package.json` and its lockfile. Narrow reuse of `src/execution/merchant-knowledge/{embedding-runtime,embedding,sealed-commerce-keyring}.ts` is allowed only when its existing purpose and behavior remain tested.

## Dependencies

- `ARCH-058-DATABASE-001`: accepted schema, constraints and targeted required-feature/plan migration.
- `ARCH-058-SHARED-002`: published, installable Shared contracts accepted from SHARED-001.

A source manifest with verified immutable content and an existing authorized reference-embedding configuration are implementation/operational prerequisites, not fabricated task results. Deployment and persistent import happen after accepted compatible readers exist.

## Enables

- `ARCH-058-MCP-002`: category-aware merchant product reads and current-shop discount discovery.
- `ARCH-058-SYSTEM-TEST-001`: exercise the actual importer, database reader and operator composition.

## Acceptance Criteria

- [ ] A verified fixture taxonomy round-trips through PostgreSQL with its original IDs/hierarchy and exact count; `hammer` returns fixture-backed candidates with pinned provenance.
- [ ] An unchanged rerun makes no embedding requests and no writes; invalid source/checksum/hierarchy/vector leaves the active generation untouched.
- [ ] Concurrent first imports/replacements, changed configuration and rollback attempts obey the explicit activation/conflict rules; an in-flight reader can finish against its retained generation.
- [ ] Mixed-generation/dimension fixtures never enter the wrong distance calculation; rank ties are deterministic; result limit is enforced.
- [ ] Missing setup and classified temporary failure are distinct from empty candidates and hard errors; no tenant or product claim is inferred from the reference corpus.
- [ ] Actual registry composition lists the matching descriptor when authorized, preserves that identity across operational readiness changes, returns the precise permitted unavailable result at invocation when necessary, and rejects stale/mismatched descriptors.
- [ ] Required-feature eligibility matches Shared for both providers/free and paid plans without preference opt-in; optional-feature and existing auth tests remain intact.
- [ ] Dry run has zero side effects/billable embedding calls; CLI failures and original-source logging are bounded, truthful and secret-free.
- [ ] No persistent environment was migrated, imported or published by this implementation task.

## Validation

Run commands from the launcher-provided `moda-interact-mcp` implementation worktree. Before the first Node command, use `command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"`. Do not guess an absolute developer checkout.

- [ ] Add focused tests at `tests/unit/execution/reference-taxonomy/{importer,reader,embedding,cli}.test.ts`; run `npm exec -- tsx --test tests/unit/execution/reference-taxonomy/*.test.ts tests/unit/capabilities/resolve.test.ts tests/unit/capabilities/prisma-reader.test.ts tests/unit/runtime/service-ports.test.ts`.
- [ ] Add `tests/integration/reference-taxonomy.integration.test.ts` to the existing owned-fixture harness and run `npm run test:integration:docker`. This harness creates its own disposable database; never substitute a deployment `DATABASE_URL` or run tests against a live database.
- [ ] Cover first import, existing import, config rotation, concurrent activation, input/vector failures, read consistency, dry-run no-provider behavior and structured error sinks; use embedding stubs, not a billable API.
- [ ] Run `npm run typecheck`, `npm run lint`, `npm run build` and `git diff --check`; record exact outcomes and any existing accepted baseline separately.
- [ ] Show the fixture-only CLI receipt and the actual composition proof. Do not run production/persistent `taxonomy:sync --apply` as validation.

## Stop Condition

Stop before implementation if accepted dependencies, the approved source distribution or the frozen contracts cannot be reconciled. Stop on unapproved schema/contract changes rather than editing another repository. After the authorized work and required validation, set status to `review`, record the Completion Report and return to `moda_architect`. Do not mark complete, deploy, import a persistent corpus, publish capabilities, reopen ARCH-052 tasks or start MCP-002.

## Implementation Notes

The existing Admin workflow and merchant-knowledge runtime are compatibility boundaries. A valid global category describes meaning only. The current shop's provider-backed product read remains the evidence for whether it sells a hammer. The Commerce-owned setup command calls this importer as a child stage after Database migration; this task supplies that command surface, not the orchestrator.

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

Implementation will use the canonical launcher, accepted dependency artifacts and an approved immutable taxonomy distribution.

### Unresolved Issues

No approved full-distribution checksum/count or environment execution is established by this task definition.

### Architectural Concerns

None beyond the explicit prerequisite and compatibility gates above.

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


## Architect Dependency Handoff (2026-11-04)

DATABASE-001 and SHARED-002 are accepted and complete. MCP-001 is ready, unclaimed, at Attempt 0. Consume exact published `@modainteract/moda-interact-shared@4.0.0` (release metadata commit `2489824bb879caa8c463fd857728078642dd1fd9`, accepted source `0b5567c3e01748de1d5d8c7d3be0d84a55dfb139`) and accepted Database `ded8f14a60182f6b1443640f012caf0089b8a44c` through the normal package/lockfile and submodule workflow. Registry integrity is recorded in SHARED-002. This promotion neither installs dependencies nor starts implementation.
