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
status: review
priority: 40
executor: codex
claimed_at: 2026-11-04T11:13:25Z
attempt: 2
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

This task is materialised in the canonical workspace with dedicated parent and implementation worktrees. Attempt 1 has a published implementation commit and a parent task report. No deployment, persistent import or capability publication has been performed.

## Objective

Provide the MCP-owned import and runtime read path for a shared public Shopify taxonomy in PostgreSQL/pgvector, then expose that path through the published `commerce_resolve_product_categories` policy operation. A phrase such as “hammer” must produce a small set of real reference category candidates; it must make no assertion about the current merchant's assortment. Make the required `product_search` feature selection agree with Shared so eligible stores do not need a preference opt-in.

## Context

- Admin already has an independent reference-taxonomy workflow and a `REFERENCE_TAXONOMY` embedding configuration. This task reads that existing configuration and credential through its authenticated purpose; it does not change Admin or copy its Redis corpus.
- `src/execution/merchant-knowledge/embedding-runtime.ts` currently hard-codes `MERCHANT_KNOWLEDGE` in the configuration lookup and credential authenticated data. Reusing that function unchanged would select the wrong purpose. Reuse narrow credential/embedding mechanics without changing the merchant-knowledge behavior.
- `src/runtime/service-ports.ts`, `src/runtime/prisma.ts` and `src/runtime/execution-registry.ts` compose actual published execution. Adding an authoring registration alone does not execute a tool.
- `src/capabilities/records.ts` omits the feature activation mode, and `src/capabilities/resolve.ts` currently requires a true merchant preference even for a required feature. DATABASE-001 prepares the feature and plan mappings; this task corrects the MCP projection and diagnostics.
- The submitted worktree now contains `src/data/reference-taxonomy-manifest.json`; the Completion Report records source verification against the pinned Shopify 2026-08 distribution. Preserve that manifest and the reported source identity/count. The full distribution is not checked into this archive; do not invent replacement bytes, choose another release or repeat source discovery solely for this definition amendment.

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

### Binding ownership clarification — 4 November 2026

This definition amendment clarifies the submitted Attempt 2 implementation's ownership boundary. It preserves the current review state, source/dependency identities, completed work and recorded validation. It does not accept the implementation, restart the task or require another taxonomy download, dependency selection, import or Docker run solely because this wording changed.

MCP accepts the authenticated shop identity and server-configured environment. The model supplies only the resolver's parsed query/limit. MCP checks the current shop, platform, subscription/plan, published capability/release/descriptor, registered executor, provider installation where applicable, RPC cancellation and deadline. Taxonomy reads use the environment's reference corpus and embedding configuration. Background owns conversation identity, inbound version, retained conversation grants, processing leases and human-control state. Do not add a conversation context parser, conversation/grant database read, retained-grant mutation or workflow-state authorization to this task.

The source review of the supplied Attempt 2 worktree found that `src/execution/reference-taxonomy/model.ts::WorkContext` contains `signal`, `deadlineAt`, `reserveProviderRequest` and optional `providerTimeoutMs`; `errors.ts::assertCurrent` checks RPC cancellation/deadline only. The taxonomy adapter and store do not consume conversation identity or conversation-grant rows. Preserve that implementation boundary. The existing composition assertions in `tests/unit/runtime/service-ports.test.ts` and `tests/integration/reference-taxonomy.integration.test.ts` use generic shop context, retain the manifest across missing corpus readiness and reject changed published definitions. Their recorded execution evidence remains in the Completion Report; this amendment adds no claim that those tests were rerun.

Existing outreach-purpose discount discovery/execution is outside this taxonomy correction. ARCH-058-MCP-002 owns its conversion to generic shop-level discount tools. Do not move that work, Background policy checks or the separate Shared public-contract cleanup into MCP-001.

### Contract and source gates

- Preserve the submitted implementation's exact published `@modainteract/moda-interact-shared@4.0.0` package/lockfile and accepted Database revision `ded8f14a60182f6b1443640f012caf0089b8a44c` through the normal database submodule. Their preparation and Shared integrity are already recorded below; this amendment does not reopen version selection, dependency installation or publication. An actual artifact mismatch is an explicit prerequisite failure. Do not import a sibling repository's source or write duplicate public schemas.
- The tool name/capability key is `commerce_resolve_product_categories`; definition version is `1.0.0`; operation is `taxonomy.resolveCategories` with operation version `1.0.0`. Use the input/output members and generic result envelope in the frozen contracts. The model supplies query/limit only; authenticated context supplies shop and environment.
- Retain the submitted `src/data/reference-taxonomy-manifest.json` for Shopify `2026-08`, English, with its recorded immutable source URL, SHA256 `afc8f21242527a209622302bd99e29efe8cc2521ae949104c2c0dc3f931e461a`, 14,606 categories and 183,429 compressed bytes. Its source verification is already recorded in the Completion Report. Runtime/import source bytes must still match that manifest. Do not select another release, regenerate the manifest or repeat a download solely for this amendment. An actual source/manifest mismatch is a concrete prerequisite failure; no placeholder checksum, guessed count, mutable main URL or fabricated category is acceptable.
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
- Readiness diagnostics and setup receipts must detect absent schema, no active corpus and incompatible provenance; readiness is an operational signal distinct from authorization. Keep the authorized resolver descriptor and advertised manifest identity stable when operational readiness changes. Do not remove the resolver from discovery because a corpus is temporarily unavailable. MCP does not read, validate, persist or mutate a retained conversation grant; Background owns that state. Recheck readiness at invocation and use only the frozen permitted `NOT_READY` / temporary-unavailable data branches; deterministic schema/contract errors retain the hard error path. The independent provider product tools remain independently eligible.
- Only classified optional operational failures enter the successful unavailable-data branch. Malformed provider/vector/result payloads, invalid contract/configuration identity, shop/provider authorization errors, an aborted or expired RPC, changed published release/descriptor and programming errors retain the existing hard failure path. These checks do not inspect conversation version, processing lease or human-control state. Do not convert these failures to `NO_CANDIDATES`, and do not weaken the generic runner's terminal-error handling.
- Extend `src/capabilities/records.ts` to carry the exact feature activation mode, and use the Shared selection rule in `src/capabilities/resolve.ts` and its exclusion diagnostics: active feature plus eligible subscription/plan mapping, with `ALWAYS_ENABLED` independent of absent/false merchant preference; optional features still require their preference. Preserve active-shop, supported-platform, ACTIVE/TRIALING subscription, active-plan and feature-mapping, current published release/descriptor and provider-installation checks. Provider permission means the current shop's installation/API authorization; it does not mean a conversation grant.
- Add a decisive parity fixture for eligible Shopify and Woo shops on free and paid plans with missing/false `product_search` preferences. Ineligible subscriptions, missing/disabled plan mappings, inactive shops and disconnected providers remain excluded. This task does not write preferences or bypass an entitlement failure.

### Logging and operational evidence

Follow `docs/observability/shared-logging.md` using `@modainteract/moda-interact-shared/logging`. At the owning source boundary, preserve actual sanitized provider/SDK/Prisma errors and causes, safe status/request IDs and a separate Moda reason code. Never invent provider errors for a database-only failure. Bound/redact source text before the generic logger; no secrets, vectors, full taxonomy or customer query text in receipts. Logger failure must not alter activation or tool results.

Use the frozen schema-versioned receipt, including target environment/mode, safe source fingerprint, generation/count and explicit stage status/code. Return nonzero on failure. Never report success for a partial import or hide an earlier completed stage. No exact corpus count or production execution claim is valid without recorded evidence.

## Work Items

- [x] Confirm accepted Database/Shared artifacts and approved source manifest; record their exact immutable identities.
- [x] Add bounded parser/manifest validation, deterministic text/fingerprint logic and purpose-correct embedding resolution.
- [x] Implement dry-run planning, identical-active no-op, outside-transaction preparation and atomic activation.
- [x] Implement the exact PostgreSQL reader, readiness diagnostics and published policy adapter.
- [x] Correct required-feature selection and diagnostic parity without changing optional features.
- [x] Add focused unit, actual composition and disposable PostgreSQL tests; document the operator command and rollback boundary.
- [x] Complete the Completion Report, set this task to `review`, return to the architect and stop.

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

- [x] Add focused tests at `tests/unit/execution/reference-taxonomy/{importer,reader,embedding,cli}.test.ts`; run `npm exec -- tsx --test tests/unit/execution/reference-taxonomy/*.test.ts tests/unit/capabilities/resolve.test.ts tests/unit/capabilities/prisma-reader.test.ts tests/unit/runtime/service-ports.test.ts`.
- [x] Add `tests/integration/reference-taxonomy.integration.test.ts` to the existing owned-fixture harness and run `npm run test:integration:docker`. This harness creates its own disposable database; never substitute a deployment `DATABASE_URL` or run tests against a live database.
- [x] Cover first import, existing import, config rotation, concurrent activation, input/vector failures, read consistency, dry-run no-provider behavior and structured error sinks; use embedding stubs, not a billable API.
- [x] Run `npm run typecheck`, `npm run lint`, `npm run build` and `git diff --check`; record exact outcomes and any existing accepted baseline separately.
- [x] Show the fixture-only CLI receipt and the actual composition proof. Do not run production/persistent `taxonomy:sync --apply` as validation.

## Stop Condition

Stop before implementation if accepted dependencies, the approved source distribution or the frozen contracts cannot be reconciled. Stop on unapproved schema/contract changes rather than editing another repository. After the authorized work and required validation, set status to `review`, record the Completion Report and return to `moda_architect`. Do not mark complete, deploy, import a persistent corpus, publish capabilities, reopen ARCH-052 tasks or start MCP-002.

## Implementation Notes

The existing Admin workflow and merchant-knowledge runtime are compatibility boundaries. A valid global category describes meaning only. The current shop's provider-backed product read remains the evidence for whether it sells a hammer. The Commerce-owned setup command calls this importer as a child stage after Database migration; this task supplies that command surface, not the orchestrator.

## Completion Report

### Status

Attempt 2 ready for architect review. The required disposable PostgreSQL integration gate has now passed under the explicit authorization in the Attempt 1 Architect Review. No architect acceptance or downstream promotion is claimed. Implementation commit: `30cdca4e62f768722388c1d94979a88ff24f7220` on `task/ARCH-058-MCP-001`.

### Corrections Completed

- **P1 — required PostgreSQL validation:** ran `npm run test:integration:docker` using the owned disposable fixture harness, fixed the exposed integration fixtures, and reran the entire command successfully. `tests/integration/reference-taxonomy.integration.test.ts` now gives a published revision matching creation/publication timestamps, snapshots the actual persisted Commerce feature configuration prompt, captures only CLI receipt strings while forwarding Node test protocol frames, and gives dry-run planning a fresh configuration identity. Dry-run assertions additionally compare persisted generations, category row count and embedding configuration before/after invocation. Production implementation and database schema are unchanged in this attempt.
- **P3 — materialization statement:** retained the architect's corrected statement. Existing parent and implementation worktrees were reused, not newly created. The earlier report below is explicitly historical; its NOT RUN/pending statements describe Attempt 1 and are superseded by this report.
- Corrected the implementation branch upstream to `origin/task/ARCH-058-MCP-001` during the normal task-branch push.

### Validation Results

Command, executed from `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-MCP-001` after the prescribed Node bootstrap:

```bash
export MODA_WORKSPACE_ROOT=/Users/kwadwoadomafriyie/project/moda-interact-workspace
command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
npm run test:integration:docker
```

**PASS, exit 0:** 26 tests reported; **25 passed, 0 failed, 1 skipped** (the explicitly opt-in live Shopify test). Output: `Disposable PostgreSQL integration tests passed.` The harness also passed `npm run typecheck:integration`, generated Prisma 6.19.3, and applied the accepted Database migrations only to its disposable PostgreSQL database.

All seven taxonomy subtests passed: source-backed hierarchy/first concurrent import and unchanged rerun; exact provenance lookup; checksum/vector/database-write rollback; concurrent replacement and inactive-fingerprint safeguards; changed configuration and mixed dimensions; actual Prisma registry advertisement/invocation and stable manifest across missing readiness with stale-definition rejection; CLI receipt and zero-provider/no-data-change assertions. Embedding calls used controlled fixtures, not a billable API.

Measured fixture diagnostic: `fixtureCategoryCount=3`, `resultLimit=2`, `roundTripMs=60.54875300000003`, `productionLatencyMeasured=false`. This is one observed service round trip against the tiny disposable fixture, not a production latency/corpus-size claim.

**PASS:** `npm run lint` and `git diff --check` after the final fixture correction. Earlier runs failed on integration-fixture setup/capture assumptions; those failures were resolved before the final full run. Final log: `/tmp/mcp058-attempt2-integration-verified.log`. Temporary fixture project `moda-mcp-it-b908b77c56f9` and its container, network and volume were removed successfully by the harness.

Attempt 1's 85 unit/regression passes (including the 45-test focused subset), main typecheck and build remain applicable to unchanged production sources; they were not rerun or counted as fresh Attempt 2 results. No live provider/model evaluation was run.

Fixture CLI receipt observed during the successful database run:

```json
{
  "schemaVersion": "1",
  "environment": "test",
  "mode": "DRY_RUN",
  "stages": [
    {
      "stage": "taxonomy",
      "status": "PLANNED",
      "code": "TAXONOMY_PREPARE_GENERATION"
    }
  ],
  "taxonomy": {
    "sourceSha256": "67c147cbc3540c0a595d72445daf4a5ce5ad044f0c6060d2a0640530d1ade822",
    "importFingerprint": "8135165990944ad4e3a78c88ba71bc864e590cc9a203d2ea0e12be121effaebc",
    "generationId": null,
    "categoryCount": 3
  },
  "publication": null
}
```

### Physical Worktree and Synchronization Evidence

Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Parent: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-MCP-001`; implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-MCP-001`. Both reused their dedicated `task/ARCH-058-MCP-001` branches; no other task's worktree or shared implementation checkout was used for edits.

Launcher packet: dependency gate passed for DATABASE-001/SHARED-002; parent remote task fast-forward not needed, origin/main incorporated; implementation remote task fast-forward not needed, origin/main already current. Recursive submodule sync/update and verification passed, Database pinned `ded8f14a60182f6b1443640f012caf0089b8a44c`. Parent prepared head `cf53d2390c70c92a779d0c620a1741010adebf49`; Attempt 2 claim `a658bf207249acb675814129f5a587f4491d0233`, pushed at claim; implementation start `66feebf2aeea53e6f4515a5899ad00c7bc550bce`, final `30cdca4e62f768722388c1d94979a88ff24f7220`. Only this task file changed in the parent; its implementation gitlink and Architect Review were preserved.

### Remaining Issues and Boundaries

The requested integration evidence gap is resolved. Independent architect acceptance remains pending and downstream tasks remain gated. No persistent database was migrated/imported, no tools were published, and no deployment/main merge was performed. Verified source/Shared/Database identities, implementation bounds and operator notes from Attempt 1 remain unchanged. No cross-repository change or new architecture decision was needed.

## Attempt 1 Completion Report (historical; superseded by Attempt 2 above)


### Status

Ready for architect review at Attempt 1; developer Docker validation pending. Implementation committed as `66feebf2aeea53e6f4515a5899ad00c7bc550bce` on `task/ARCH-058-MCP-001`. Acceptance criteria remain for independent architect assessment; this report makes no acceptance or PostgreSQL execution claim.

### Files Changed

- `src/data/reference-taxonomy-manifest.json` and `src/execution/reference-taxonomy/{model,errors,source,embedding,credentials,generation,store,service,adapter,sync.cli}.ts`: trusted source, import, reader, diagnostics, registry adapter and CLI.
- `scripts/sync-reference-taxonomy.mjs`, `package.json`, `package-lock.json`, `tsconfig.json`: installed TypeScript execution, exact Shared 4.0.0, JSON build assets.
- `src/runtime/{prisma,service-ports}.ts`, `src/capabilities/{records,prisma-reader,resolve,manifest}.ts`: real execution composition, independent readiness and Shared eligibility parity.
- Narrow compatibility updates in policy executors, sealed keyring diagnostics and existing test fixtures; removed one pre-existing unused `randomUUID` import from the Shopify provider to satisfy lint.
- `database` gitlink: accepted Database revision; no schema authored or applied.
- Reference taxonomy unit/integration tests and fixtures, existing capability/runtime regression tests, integration harness prerequisite, upstream fixture MIT license and README operator notes.

### Accepted Artifacts and Verified Source

- Database: `ded8f14a60182f6b1443640f012caf0089b8a44c` through this implementation's normal submodule.
- Shared: installed published `@modainteract/moda-interact-shared@4.0.0`; release metadata `2489824bb879caa8c463fd857728078642dd1fd9`, accepted source `0b5567c3e01748de1d5d8c7d3be0d84a55dfb139`. Lock integrity: `sha512-Zv78WX/AsN1lZWyaMirO2Ml/rOZknSv0cnJnxYBuyc368kzDZzswauKRPSe8GSXFfjkk3cQnr3wi4n49d9HTzw==`.
- Approved [Shopify 2026-08 release](https://github.com/Shopify/product-taxonomy/releases/tag/v2026-08), English asset `https://github.com/Shopify/product-taxonomy/releases/download/v2026-08/categories.en.txt.gz`. Release ID 375990317, asset ID 528193854, published 2026-08-24T21:25:13Z.
- Downloaded compressed bytes: **183429**; SHA-256 **afc8f21242527a209622302bd99e29efe8cc2521ae949104c2c0dc3f931e461a**, matching GitHub's asset digest. Expanded bytes 2091730. Actual compiled parser validated **14606 unique categories**, complete ancestors, maximum level 7, maximum category ID length 48 and full-path length 228. This read-only verification made zero embedding calls and zero database writes.
- Full distribution is not checked in. Three-category fixture and 130-row concurrency subset are explicitly fixture data derived from that release, with upstream license attribution.

### Work Completed

- Validates trusted source checksum/length, hierarchy, unique IDs and bounded deterministic text before embedding; fingerprint covers the frozen environment/source/model/index/text-format identity. Production cannot override the manifest. Matching complete active generations no-op before embedding/writes; stale/inactive fingerprints and source downgrades fail explicitly.
- Resolves the existing `REFERENCE_TAXONOMY` configuration and decrypted credential with matching Shared purpose AAD, sealed keyring and no merchant-purpose/API-key fallback. Vectors are prepared outside the transaction with bounded retries, provider budgets, sibling cancellation and finite nonzero float32 validation.
- Atomic activation uses transaction-scoped corpus advisory lock, active baseline re-read and configuration row lock through commit, parent-before-child inserts, count/vector-health checks and smoke search before active switch. Old generations are retained. Cancellation before commit rolls back; confirmed commits report truthfully.
- Reader pins provenance and tuple, rechecks compatibility after embedding, and materializes generation/dimension-filtered candidates before cosine distance. Parameterized exact search, deterministic category-ID ties, maximum ten results. SQL statement timeout is set server-side; result limit does not imply bounded scan count.
- Published resolver uses existing registry/descriptor/entitlement/deadline/output gates and Shared wire contracts. Readiness does not remove authorized descriptors or alter grants. Only classified operational failures become permitted unavailable data; malformed/configuration/cancellation/contract failures remain hard errors. Existing provider product eligibility stays independent.
- Capability eligibility and exclusion diagnostics use Shared selection semantics. Shopify/Woo, free/paid and missing/false preference parity covered; ALWAYS_ENABLED preserves ordinary shop/subscription/plan/release/provider gates, optional features retain opt-in.
- CLI validates all flags and environment before effects, emits schema-versioned stage receipt, uses stderr Shared logging and nonzero failures. Dry run performs no embeddings or mutations. Explicit operator rollback boundary documented; no automatic reactivation/deletion.
- Original sanitized errors/causes, database codes and safe provider status/request IDs remain separate from Moda reason codes. No query text, full corpus, vectors or secrets logged; logging failures do not change results.

Bounds: 4 MiB compressed / 8 MiB expanded source, 20000 categories, 8192 UTF-8 bytes per embedding text, batches of 64 with concurrency 2, maximum 4096 dimensions / 64 million prepared components, 8 MiB provider response, 10-second provider deadline, one retry, 15-minute overall import, provider-call cap 626. Database read statement 1500 ms, write statement 5000 ms, lock 1000 ms, final transaction 120000 ms, inserts at most 64 rows. These are implementation limits, not measured production performance.

### Validation Results

Node 24.19.0, npm 11.17, Prisma 6.19.3. Commands run in the isolated implementation worktree after the prescribed Node bootstrap:

- **PASS: 85 tests**, zero failures/skips: `npm exec -- tsx --test tests/unit/execution/reference-taxonomy/*.test.ts tests/unit/capabilities/*.test.ts tests/unit/runtime/service-ports.test.ts tests/unit/runtime/prisma.test.ts tests/unit/mcp/resources.test.ts tests/unit/execution/merchant-knowledge/*.test.ts tests/unit/execution/policy/*.test.ts`.
- **PASS: 45 focused tests**, zero failures/skips: `npm exec -- tsx --test tests/unit/execution/reference-taxonomy/*.test.ts tests/unit/capabilities/resolve.test.ts tests/unit/capabilities/prisma-reader.test.ts tests/unit/runtime/service-ports.test.ts`. These are a subset of the 85, not additional tests.
- **PASS:** `npm run typecheck`, `npm run typecheck:integration`, `npm run lint`, `npm run build`, script syntax checks and `git diff --check`.
- **PASS:** compiled parser read the actual approved full source with the identities/count above; zero provider/database effects.
- Actual service-port execution registry is exercised by passing unit tests: resolver remains advertised across readiness changes, executes the registered handler and validates output. Prisma composition readonly diagnostic test passes. Actual PostgreSQL-backed composition is authored in the integration suite and remains unexecuted.
- **NOT RUN:** `npm run test:integration:docker`. Integration source compiles, but PostgreSQL round-trip/locking/concurrency/mixed-dimension/query-work assertions and database-backed composition are not claimed passed. No production latency, live semantic/model quality or multilingual evaluation was measured.

Fixture-only CLI dry-run receipt (three fixture categories; not the full approved distribution and not a persistent import):

```json
{
  "schemaVersion": "1",
  "environment": "test",
  "mode": "DRY_RUN",
  "stages": [
    {
      "stage": "taxonomy",
      "status": "PLANNED",
      "code": "TAXONOMY_PREPARE_GENERATION"
    }
  ],
  "taxonomy": {
    "sourceSha256": "67c147cbc3540c0a595d72445daf4a5ce5ad044f0c6060d2a0640530d1ade822",
    "importFingerprint": "fc023ae553c960d1ad85e71ca1f4266d6033d4e265f1a4a03b8086aef5027f7a",
    "generationId": null,
    "categoryCount": 3
  },
  "publication": null
}
```

### Developer Validation Required

`docs/agent-validation-execution-policy.md` states: “Unless the developer or architect explicitly requests autonomous execution for the specific task, repository agents MUST NOT launch or wait on” multi-container Docker integration suites. It directs agents to return fast-checked work to review with the exact developer command. No task-specific override was supplied. Run:

```bash
export MODA_WORKSPACE_ROOT=/Users/kwadwoadomafriyie/project/moda-interact-workspace
cd /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-MCP-001
command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
npm run test:integration:docker
```

Required result: exit 0 and the disposable PostgreSQL integration suite success, including the newly added taxonomy suite. Use only the owned disposable harness, controlled embeddings and fixture database; no deployment DATABASE_URL substitution. Record actual output and fixture query timing before acceptance. This pending execution is the remaining evidence gap.

### Isolation and VCS Evidence

Prepared packet established canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`, parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-MCP-001` and implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-MCP-001`, both on `task/ARCH-058-MCP-001`. Both were newly created; origin/main was already current, task fast-forward not needed, dependency re-gate passed and recursive submodule initialization verified ready.

Parent initial `bafe199d25b8b2ad4ee9e9927675d7b4eecedda9`; durable claim `55d76f6361fd336befed7f15716612323c36ddc3`; implementation initial `a1df91670bbfb445bd07d3f3a58ba5eb23ad973d`, final `66feebf2aeea53e6f4515a5899ad00c7bc550bce`. Database initial `139765042baad3901682cfe9c54a3d6bba73e75c` explicitly advanced to the accepted revision above. Only the implementation's dependency gitlink and this parent task report were updated; no parent implementation gitlink, architecture, task index or canonical checkout was changed. No main merge, deployment, persistent migration/import, Commerce publication or billable embedding call occurred.

### Deviations and Unresolved Issues

The new Shared grant union and product input defaults required narrow existing fixture/type compatibility updates. Existing native product executor fails closed for newly recognized browse/category forms; actual provider support belongs to MCP-002. A pre-existing unused provider import was removed for the required lint check. No schema or public contract was changed. Developer Docker execution and independent architect review remain pending; downstream tasks remain gated.

### Architectural Concerns

No new architecture decision requested. Exact scans and import bounds are documented; production performance requires separately recorded measurements. Authorization stays independent of operational readiness.

## Architect Review

### Review Status

**Changes Requested — Attempt 1, 2026-11-04.** Returned to `ready`; executor and claim are cleared. Attempt remains 1. No architect acceptance or downstream promotion is made.

### Review Notes

1. **[P1] Required disposable PostgreSQL integration validation is incomplete.** Acceptance criterion 9 and the required validation item for `npm run test:integration:docker` remain unchecked. The report explicitly says the integration suite was not run, so PostgreSQL round-trip, transactional activation, concurrency, mixed-dimension reader safety, and database-backed composition have not been verified. Run the exact owned-fixture command from the report, record its exit status and results, and do not use a deployment `DATABASE_URL`. This review authorizes the assigned agent on the next attempt to launch and wait for this task's `npm run test:integration:docker` disposable integration suite; authorization is limited to the owned disposable harness and fixture database.
2. **[P3] The task definition's materialization statement was stale.** It claimed no task branch, worktree or commit existed despite the recorded Attempt 1 worktrees and commits. The statement is corrected above; keep the report consistent with observed VCS state in the next submission.

### Reviewed Files

- Implementation `66feebf2aeea53e6f4515a5899ad00c7bc550bce` and parent submission `d4e99df28`; both exact commits are present on their respective remote task branches. The implementation branch's upstream is configured as `origin/main`, although `origin/task/ARCH-058-MCP-001` points at the same implementation commit.
- Reviewed the task definition, source manifest and importer/reader/CLI implementation, registry and capability composition, focused tests, integration harness and Attempt 1 Completion Report.

### Validation Reviewed

- Reviewed the reported unit/typecheck/lint/build results and source-backed manifest verification. No test command was rerun during this review.
- `npm run test:integration:docker` is explicitly reported as NOT RUN; this is a required acceptance gate and prevents acceptance.
- Parent report whitespace was not independently rechecked in this review.

### Architecture Conformance

The reviewed implementation stays within the MCP repository scope, consumes the accepted Shared/Database artifacts, uses fixture-backed category identity, and makes no persistent import or publication claim. The required PostgreSQL behavior remains unverified; downstream MCP-002 and SYSTEM-TEST-001 stay gated.

### Follow-up

Complete the authorized disposable integration validation, correct the report/worktree evidence if needed, publish both task branches, and return the same task for architect review. Do not start or promote either enabled task before acceptance.


## Architect Dependency Handoff (2026-11-04)

DATABASE-001 and SHARED-002 are accepted and complete. MCP-001 is ready, unclaimed, at Attempt 0. Consume exact published `@modainteract/moda-interact-shared@4.0.0` (release metadata commit `2489824bb879caa8c463fd857728078642dd1fd9`, accepted source `0b5567c3e01748de1d5d8c7d3be0d84a55dfb139`) and accepted Database `ded8f14a60182f6b1443640f012caf0089b8a44c` through the normal package/lockfile and submodule workflow. Registry integrity is recorded in SHARED-002. This promotion neither installs dependencies nor starts implementation.
