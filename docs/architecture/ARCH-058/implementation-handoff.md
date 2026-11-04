# ARCH-058: Remaining implementation handoff — Attempt 4

Reviewed against `moda-interact-workspace(20261104-094947).zip` on 4 November 2026. The [execution baseline](execution-baseline.json) records exact archive/file hashes, accepted artifact receipts and observed source gaps. [Contracts](contracts.md) remains the wire/behavior authority; each task specifies the concrete edits in its own repository.

## Scope and current state

This amendment changes five pending definitions: MCP-002, MCP-003, COMMERCE-001, BACKGROUND-001 and SYSTEM-TEST-001. It changes no application source, task claim, completed-task history, decision index, Database migration or Shared schema.

| Work | Observed state | Binding consequence |
| --- | --- | --- |
| DATABASE-001 | Complete; accepted implementation `ded8f14a60182f6b1443640f012caf0089b8a44c` | Consume its schema/migration through the normal Database submodule. Do not create a replacement taxonomy migration or rewrite the accepted one. |
| SHARED-001 | Complete; accepted source `0b5567c3e01748de1d5d8c7d3be0d84a55dfb139` | Shipping, browse, presentation, built-in grants and runner instructions already exist. Implement consumers against those actual exports. |
| SHARED-002 | Complete; published `@modainteract/moda-interact-shared@4.0.0`, runner `1.1.0` | Pin the existing artifact and verify its lock entry against the recorded receipt. No version selection or republication. |
| SHOPIFY-001 | Complete; accepted implementation `c3b580cec5acc46e5c53386dd94279ad97b02ee9` | Consume declared scope and existing installation lifecycle. The runtime still checks the actual session grant; a completed configuration task is not proof that every installation granted the scope. |
| MCP-001 | User reports active development; uploaded canonical task still says ready/Attempt 0 | Preserve this task and its live worktree. This patch neither changes its import/source contract nor resets its claim. Downstream work consumes its accepted result after normal acceptance. |
| Remaining five tasks | Pending, Attempt 0 | Amend their implementation instructions only. Their dependencies, claims and execution modes remain unchanged. |

Accepted task records establish previous acceptance; the actual prepared source establishes whether that work has been integrated. The archive contains Shared 4.0.0, while MCP still pins 2.8.1, Commerce 2.7.2 and Background 3.0.0. MCP's nested Database snapshot also lacks the accepted taxonomy migration. These are recorded consumer integration deltas, not instructions to reopen completed tasks. MCP-001 already owns the MCP dependency adoption; MCP-002 must consume it instead of repeating publication or source discovery.

## Fixed dependencies and bounded checks

The exact Shared package is `@modainteract/moda-interact-shared@4.0.0`. Its recorded integrity is:

```text
sha512-Zv78WX/AsN1lZWyaMirO2Ml/rOZknSv0cnJnxYBuyc368kzDZzswauKRPSe8GSXFfjkk3cQnr3wi4n49d9HTzw==
```

The immutable publication receipt is in SHARED-002 and copied without alteration into `execution-baseline.json`. Consumer-owned package/lockfile upgrades install this exact version using their existing registry configuration. Check the installed/locked version and integrity once as part of that upgrade. Do not query `latest`, choose another version, use a sibling source path, or repeat SHARED-002's publication procedure. A different artifact is an explicit prerequisite mismatch.

When a task actually needs a Database gitlink change, preserve accepted later migrations. The prepared nested Database must contain the accepted commit and target migration; do not reset it to an older commit merely to reproduce the receipt. The bounded ancestry check is:

```bash
git -C database merge-base --is-ancestor ded8f14a60182f6b1443640f012caf0089b8a44c HEAD
```

Run it in the launcher-supplied implementation worktree only when its task owns or verifies that dependency. A missing object, non-ancestor or missing migration is reported as the concrete integration prerequisite; no guessed SHA, copied Prisma schema, remote-main pin or cross-repository merge is permitted. A developer-owned squash/rebase with different ancestry requires recorded equivalence, not automatic rejection of valid later work. Reuse matching launcher preparation evidence instead of repeating startup/worktree discovery.

The hashes in the baseline identify what this review inspected. They are not a rule that later accepted source must remain byte-identical. On a changed base, compare only the named touchpoints and contract surfaces affected by that change; preserve unrelated work and report a real conflict rather than restarting a broad architecture investigation.

## Taxonomy source: reuse the established owner

The uploaded archive contains `moda-interact-admin/src/data/shopify-taxonomy-manifest.json`, pinned to Shopify `2026-08` and `categories.en.txt.gz`, plus its existing distribution parser and Redis synchronizer. It contains no full category JSON/text/gzip distribution. The existing Admin pipeline remains unchanged and separate.

The user supplied an MCP-001 agent report of a verified pinned release, SHA-256 match, 14,606 unique categories and a complete hierarchy. That is an in-progress handoff report; its actual downloaded asset, new MCP manifest and final accepted receipt are not in this archive. This review does not invent their bytes, checksum, format or commit. A source integrity/hierarchy check is valid importer work; downstream tasks must not independently select or download another taxonomy merely because that check happened in a different task.

For the remaining tasks, the authority is the **accepted MCP-001** `src/data/reference-taxonomy-manifest.json`, `scripts/sync-reference-taxonomy.mjs` and source/import receipt. Commerce forwards the existing `--source` option to that CLI; it does not parse taxonomy, own a second manifest, invoke Admin's Redis synchronizer or choose a different release/format. The provided file must match the accepted manifest's distribution-byte checksum exactly. Compressed bytes and a derived/decompressed JSON file are not interchangeable checksums. Offline setup requires the corresponding verified source file to be staged; it does not require a new download.

SYSTEM-TEST-001 consumes the same staged asset for actual CLI tests and checks its checksum/count against the accepted MCP-001 receipt. Its deterministic embedding/provider transport supplies test responses without a paid model call. It must not assume an unimplemented production `--manifest` flag, importer hook or undocumented fixture configuration. Parser/hierarchy failure cases can use the accepted MCP-001 focused evidence; a black-box CLI checksum failure uses deliberately mismatched local bytes. Deterministic transport tests do not prove real-model retrieval quality.

## Accepted MCP implementations: integration prerequisites

`ARCH-052-MCP-002` is complete in the uploaded task history. It records initial implementation `7cbceee89b2ae0115bd2b948418b4169b977ea8f` and accepted correction `89e9ad3` on `task/ARCH-052-MCP-002`. However, the archive lacks `moda-interact-mcp/src/execution/discount-catalogue.ts`, and `src/mcp/registration.ts` still dispatches the unavailable stub. GitHub read attempts for the recorded correction returned 404; no full correction SHA or current remote integration is asserted here.

MCP-002 must extend the accepted catalogue implementation after that source is present in its prepared base. Its task names the required reader/projection/test surfaces. If they are absent, the handoff is specifically **integration of the accepted ARCH-052-MCP-002 implementation** through the normal developer-owned integration workflow. Do not build a competing catalogue, downgrade packages, revive `commerce_evaluate_discount`, mark the historical task incomplete or claim that a completion flag alone proves source availability. The task may perform independent product work, but its combined acceptance remains blocked on the actual accepted reader and its regression tests.

The accepted `ARCH-052-MCP-006` Woo original-error correction is also recorded complete at `1d18e6c866311d0a3238a919f335643ffbefd8c1`, but the uploaded `direct-product-reader.ts` still drops original transport/DNS/parser exceptions and maps HTTP error bodies without their diagnostic details. Its accepted correction and direct-reader regression tests must be integrated into the prepared MCP base and preserved. This is an additional observed source/history mismatch, not authorization to introduce another logger or reopen the accepted task.

## Resolved gaps and implementation owners

| Gap in the earlier definitions | Explicit correction | Owner |
| --- | --- | --- |
| Shared target remained conditional after publication | Fixed 4.0.0 artifact, recorded integrity and consumer upgrade responsibility | All remaining consumers |
| Category search/pagination delegated algorithm choices | Named fixed queries, literal page sizes, exact category checks, bounded progress/cursor rules and guard touchpoints | MCP-002 |
| New Woo private parameters omitted an intermediate allowlist | Enumerate every service, resolver and direct-reader boundary that must agree | MCP-002 / MCP-003 |
| Shipping permission outcomes could be inferred from a generic error | Read token/scope from the same validated offline session; preflight absence differs from an attempted request failure; product facts remain independent of policy availability | MCP-003 / BACKGROUND-001 |
| Tool-only no-op check missed response-instruction changes | Compare owned tool, prompt and response content; preserve unrelated pins in one immutable release; share the publication lock for the feature/activation precondition | COMMERCE-001 |
| Setup assumed configuration/actor in an empty database | Define deferred checks, ordered partial failure receipts, existing configuration bootstrap and repeat execution | COMMERCE-001 |
| Background had no concrete prompt/policy/basket integration | Assign exact readers/projections, fresh-turn observations, policy checks and finalization order; treat incomplete collection membership and absent sale status as unknown | BACKGROUND-001 |
| Final refresh budget was not reserved | Runner budget six retains its legacy evidence reservation; finalization stays within one total of ten, with four reserved calls and deterministic pruning | BACKGROUND-001 |
| Direct host-test command could exclude every intended test | Add a focused test configuration for the existing mocked host suite; use disposable integration only for actual database tests | BACKGROUND-001 |
| System-test model seed overwrote the real release with a fake one | Seed only fixture-owned configuration/model/actor rows; publish through the actual Commerce CLI | SYSTEM-TEST-001 |
| Test transport/mount seam was assumed | Name the SystemTest runtime constructor options and read-only harness mount; leave application binaries unmodified | SYSTEM-TEST-001 |
| Long validation had no clear executor/evidence boundary | Exact fast checks and developer commands, with pending evidence distinguished from a passing result | Every remaining task |

Discovery is performed inside the existing bounded model/tool loop. Published trusted instructions tell it when to resolve categories, search, browse, retrieve shipping information and inspect eligible discounts. Background validates the resulting selections and composes controlled replies exclusively from observed facts. A missing/invalid selection produces a verified store-link fallback; it does not create a second automatic discovery agent after the model responds. Natural-language relevance and intent are model behavior; data/permission validation and output composition are deterministic host behavior. The runner retains `discoveryAttempts + selectedLegacyEvidenceCount <= 6`; all actual final replay calls then share the remaining capacity under total ten. Four calls are reserved by the runner cap, and unused runner capacity remains available to the host within that same total.

## Fresh environment and repeatable setup

The wrapper stages are preflight, migration, taxonomy and publication. Existing configured environments validate actor/configuration before writes. A schema-empty target cannot pass database-dependent configuration checks before migrations exist. Its dry-run records those checks as deferred; its apply can complete migration and then fail explicitly on the missing configuration/actor, leaving publication `NOT_RUN`. Use the existing configuration lifecycle to provide the required actor and `REFERENCE_TAXONOMY` settings, then rerun the same wrapper. Do not invent credentials, silently seed an administrator or use the broad seed against an existing environment.

The Commerce wrapper emits one JSON stdout receipt. It preserves the accepted MCP importer emission interface and finds exactly one valid bounded receipt among its child output lines; missing, ambiguous or inconsistent receipts fail explicitly. The receipt uses only the existing `PLANNED`, `APPLIED`, `UNCHANGED`, `FAILED`, `NOT_RUN` statuses. Missing reference configuration after migration gives taxonomy `FAILED` / `TAXONOMY_CONFIGURATION_UNAVAILABLE`, publication `NOT_RUN` / `PREREQUISITE_FAILED` and nonzero exit. Missing required publisher actor is `ACTOR_UNAVAILABLE` at the stage that can actually check it. Earlier successful stages remain in the receipt. No failed/partial apply is reported as a complete setup.

Existing/future store access is validated against the standard required `product_search` feature on provisioned Free/paid plans. The current Admin plan authoring already loads active `systemRequired` features and calls `buildDesiredPlanFeatures` in `src/lib/admin/merchant-knowledge-plan-policy.ts`; it is not hardcoded to two features. The SystemTest fixture must likewise derive required features from actual database rows. Fixture SQL is not evidence that Admin's authoring UI was exercised; that existing generic path is static source evidence, and no Admin implementation task is added.

## Validation ownership and review gate

`docs/agent-validation-execution-policy.md` governs execution. Repository agents run the named bounded checks. Long Docker/migration/system suites have an exact developer-owned command and expected result in their task. Preparing that handoff is compliant; marking an unrun suite passed is not. The explicit exception is for a specifically authorized already-claimed task, so these pending definitions do not grant an open-ended override.

A task can enter `review` with a separate unchecked developer-validation section. Architect acceptance/automatic completion still requires its mandatory evidence. Preserve valid matching evidence already supplied by the developer; do not rerun a long suite solely because the model did not launch it. A terminal SYSTEM-TEST-001 invocation remains developer-controlled after its dependencies are complete.

Every execution report records the launcher-resolved parent/implementation worktrees, task branch and source SHA, Database pin where relevant, exact command/result/exit code and disposable resource cleanup. An excluded suite, zero matched tests, a mocked path replacing the real target, a missing prerequisite, or a skipped scenario is not a pass.

## Definition patch validation

The delivered patch must apply to a fresh extraction of the exact 094947 archive with strict whitespace checks; the applied tree must pass `git diff --check` and reverse-apply verification. Compare the completed task records, MCP-001, all `_index.md` files and all implementation files byte-for-byte with the archive. Validate all ten task metadata/routes/dependency edges without changing lifecycle fields. These are documentation-patch checks, separate from future runtime tests.
