# ARCH-058: Current-worktree implementation handoff — Attempt 7

Reviewed against `moda-interact-workspace-ARCH-058-MCP-001.zip` on 4 November 2026, with earlier `moda-interact-workspace(20261104-094947).zip` evidence retained explicitly for repositories absent from this task archive. The [execution baseline](execution-baseline.json) records both archive identities and the source associated with each inspected hash. [Contracts](contracts.md) remains the wire/behavior authority; each task specifies concrete edits in its owning repository.

## Scope and current state

This amendment clarifies MCP-001 at review/Attempt 2 and corrects five pending definitions: MCP-002, MCP-003, COMMERCE-001, BACKGROUND-001 and SYSTEM-TEST-001. It changes no application source, task lifecycle/claim, historical completion/review evidence, completed-task record, decision index, Database migration or Shared schema. All nine documents previously delivered in Attempt 5 were still at Attempt 4 in this upload. The consolidated Attempt 7 patch carries their complete correction, the current MCP-001 amendment and the explicit agent-instruction correction below. A separate from-Attempt-6 patch changes only the three instruction/validation task definitions and four common documents; choose the route matching the actual local baseline.

| Work | Observed state | Binding consequence |
| --- | --- | --- |
| DATABASE-001 | Complete; accepted implementation `ded8f14a60182f6b1443640f012caf0089b8a44c` | Consume its schema/migration through the normal Database submodule. Do not create a replacement taxonomy migration or rewrite the accepted one. |
| SHARED-001 | Complete; accepted source `0b5567c3e01748de1d5d8c7d3be0d84a55dfb139` | Shipping, browse, presentation, built-in grants and runner instructions already exist. Implement consumers against those actual exports. |
| SHARED-002 | Complete; published `@modainteract/moda-interact-shared@4.0.0`, runner `1.1.0` | Pin the existing artifact and verify its lock entry against the recorded receipt. No version selection or republication. |
| SHOPIFY-001 | Complete; accepted implementation `c3b580cec5acc46e5c53386dd94279ad97b02ee9` | Consume declared scope and existing installation lifecycle. The runtime still checks the actual session grant; a completed configuration task is not proof that every installation granted the scope. |
| MCP-001 | Current uploaded task is review, Attempt 2; implementation `30cdca4e62f768722388c1d94979a88ff24f7220` is recorded in its report | Clarify current requirements only. Preserve lifecycle, claim, code and all report/review history. Acceptance remains a separate review outcome; do not restart preparation or importer work for this amendment. |
| Remaining five tasks | Pending, Attempt 0 | Amend their implementation instructions only. Their dependencies, claims and execution modes remain unchanged. |

The current MCP worktree already pins Shared 4.0.0 with the accepted lock integrity and contains the accepted Database taxonomy migration. Its report records Database `ded8f14a60182f6b1443640f012caf0089b8a44c`. Reuse matching prepared execution evidence; do not repin or rerun source discovery solely for this correction. The earlier 094947 snapshot showed Commerce 2.7.2 and Background 3.0.0; those repositories are not included in this task archive, so those observations remain explicitly historical consumer-adoption requirements rather than new current-checkout claims.

## Binding correction: MCP is a tool provider and executor

Attempt 4 incorrectly assigned Background workflow responsibilities to MCP. The instruction to carry conversation/retained-grant projections and the proposed `conversation-discount-context.ts` adapter are withdrawn. The correction assigns these responsibilities to their existing owner, Background. The existing MCP source already states that its request identity needs no conversation/grant and that capability resolution has no conversation, turn lease or caller grant.

| Responsibility | Exact owner and boundary |
| --- | --- |
| Tool discovery and execution | MCP provides current shop-eligible descriptors, validates arguments, enforces current shop/plan/connection/data access, performs bounded reads and returns structured results. |
| Conversation lifecycle | Background alone reads conversation ownership, inbound version, processing lease, control mode/revision, language and retained grant. |
| Conversation permission to use discounts | Background resolves current recommendation policy, filters runnable tools and checks it around reads/final claims. |
| Discount tool data | The existing MCP executor returns its contracted shop-level configured mode/permitted catalogue and condition facts. It does not know which conversation or workflow requested those facts. |
| Tool identity versus current use | MCP advertises both canonical discount descriptors independently of mode. Background persists the full validated set for new grants and applies current use permission locally. |
| Optional unavailable data | MCP returns the same typed outcome for the same classified catalogue failure to every caller. Background decides product-only continuation or its existing conservative outreach failure. |
| Publication | Commerce publishes the four standard product/shipping definitions and source-owned instructions; it does not move conversation state into MCP. |

The conversational client validates its existing assertion locally, then sends exactly `{shopId}` in the existing trusted context header. No conversation ID, recovery ID, grant ID, inbound version, processing lease or human-control state is transmitted for this standard path. The server uses its configured environment. Existing opaque execution context for other already accepted adapters is preserved; no CONVERSATION-specific parsing or authorization is added.

MCP capability listing removes shop discount-policy/configuration reads that were only needed to decide whether to list the built-ins. Its actual catalogue executor still performs current shop configuration/data checks required by the existing result contract. Options under NONE is a truthful empty result with `mode:"NONE"`; details under NONE or outside FIXED scope is denied. Do not remove or fabricate the existing Shared `mode` field to imply that a contract change occurred.

For new conversations, the host retains both canonical built-in identities even under NONE, validates the complete generic manifest/list against that grant, and then gates current execution. NONE-to-AI changes current host permission without widening the stored identities; AI-to-NONE removes current use without deleting them. Preserve existing exact manifest/release equality and the pre-production fresh-conversation requirement for old incompatible grants. Do not create narrowed substitute grants or relax Shared equality. Shared 4.0.0's previously accepted `CommerceConversationToolContextSchema` is unused by this corrected design. Removing that obsolete export is a separate Shared cleanup/publication follow-up; this runtime boundary correction neither performs nor requires it. No Database migration is required.

MCP-002 now enumerates its exact generic projection changes and no-workflow-read tests. BACKGROUND-001 owns the local policy/turn/grant checks and header tests. SYSTEM-TEST-001 separates a generic MCP phase, including a disposable database role without workflow-table read permission, from actual host conversation-control tests. A generic tool call can succeed independently of a stale/HUMAN conversation; the host is responsible for not making or using that call for the invalid workflow.

## Where the CommerceAgent instructions are defined and loaded

Read [COMMERCE-001 section 3](../../decisions/commerce/ARCH-058/COMMERCE-001-provision-standard-product-discovery.md) for the complete literal shopping and response instructions, [BACKGROUND-001 sections 1 and 3](../../decisions/background/ARCH-058/BACKGROUND-001-ground-product-and-discount-recommendations.md) for their loading and exact recovery-string replacement, and [contracts section 1.1](contracts.md#11-where-commerceagent-instructions-live) for the source map. These are pending implementation requirements. They are not hidden in MCP-001 or already installed by this documentation patch.

The earlier full source shows `src/agents/commerce.agent.ts::runCommerceAgent` delegating to `executeCommerceHost`; the host supplies RECOVERY_INSTRUCTIONS to the existing Shared runner. The accepted runner already composes kernel, host, response and feature instructions. COMMERCE-001 creates the source-owned `src/commerce/bootstrap/system-product-response.ts` constants and publishes their exact bytes into the immutable product_search feature/response contract. BACKGROUND-001 adds the existing published Platform/Shop configuration load to the host array. The resulting assembly order is Shared kernel, Background recovery, Platform, optional Shop, response contract, then granted feature prompts. Order alone does not enforce permissions; existing host gates and composition do.

Attempt 7 closes two concrete gaps. The feature prompt now explicitly requires the permitted canonical options/details flow before a recommendation, matching the initial-outreach intent. Background replaces the exact existing third recovery string containing the blanket missing-evidence referral rule, so expected limitations can use the defined product/store fallback without contradicting another host instruction. Its other recovery/language strings remain intact. Product routing remains authored by Commerce; Background is not given a duplicate feature prompt.

The discount requirement has a deterministic host acceptance rule in [contracts section 5.2](contracts.md#52-required-permitted-discount-inspection-before-a-recommendation). NONE/empty FIXED is exempt and makes no discount calls. Other permitted modes require a current-turn options outcome; a nonempty union of retained permitted options requires at least one matching details outcome. Empty options, null details and typed optional UNAVAILABLE may complete the relevant bounded inspection but do not establish eligibility or catalogue-wide absence. If the model skipped a required call, the host discards product proposals and uses its existing controlled composition without products: a weather redirect becomes store-only, while independently valid shipping facts/reference retain their existing authorized refresh and rendering. Ordinary or shipping-only answers without a product recommendation do not require discount discovery. The host does not make post-final discovery calls. Preserve the six-call runner admission/ten-call total, current policy fences, terminal referral and independent selected-offer revalidation.

Owning-task tests capture the actual model request and publisher-consumer path. Existing system scenarios additionally cover missing options/details, current-turn identity, retained-page union and ordinary optional degradation. Scripted tests prove instruction delivery and enforcement, not general natural-language model quality. Database, Shared publication, Admin and MCP-001/002/003 definitions receive no new changes relative to Attempt 6.

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

## Submitted MCP-001 evidence and taxonomy source

The current source contains `src/data/reference-taxonomy-manifest.json`, the `src/execution/reference-taxonomy/` implementation, CLI, focused tests and PostgreSQL integration suite. Its manifest records Shopify `2026-08`, English, SHA256 `afc8f21242527a209622302bd99e29efe8cc2521ae949104c2c0dc3f931e461a`, 14,606 categories and 183,429 compressed bytes. The full distribution is absent from the ZIP; verification/count evidence comes from the submitted manifest and report, not a new source download by this review. Admin's independent Redis pipeline remains untouched.

The current report records implementation `30cdca4e62f768722388c1d94979a88ff24f7220`, dedicated parent/implementation worktrees, accepted dependency preparation and an authorized disposable PostgreSQL integration run with 25 passed, zero failed and one opt-in live test skipped. Cleanup is reported. The reported 3-category fixture timing is not full-corpus production performance. This amendment preserves all evidence without rerunning tests, accepting the implementation, changing task status or promoting dependants.

The source review found no conversation/grant/lease/control lookup in the taxonomy path. `WorkContext` has signal, deadline, request budget and optional provider timeout. `assertCurrent` checks RPC cancellation/deadline; the adapter checks the current published definition. The MCP-001 amendment makes those exact meanings binding. Existing generic registry/Prisma composition tests already exercise readiness-independent descriptors and changed-definition rejection. No new conversation authorization test or implementation module belongs in that task.

After acceptance, downstream tasks consume the same manifest, CLI and source receipt. Commerce forwards `--source` to the existing CLI; it does not parse taxonomy, own a second manifest, call Admin's Redis synchronizer or choose another release. Offline operator tests require the corresponding staged verified distribution. The actual test-only parser/service/main factory seams remain MCP-owned focused-test mechanisms; SystemTest does not inject them into the production CLI. Its full CLI import uses deterministic provider transport and the production manifest. Scripted transport tests do not certify real-model relevance.

## Present discount catalogue and Woo diagnostics

The earlier 094947 snapshot lacked the accepted discount catalogue and Woo diagnostic correction. This current worktree contains `src/execution/discount-catalogue.ts`, its registered execution port and tests, plus the original-error-preserving Woo reader. The previous missing-source blockers are superseded as source-presence findings. Their historical task acceptance receipts remain intact; no remote Git ancestry is inferred from a ZIP.

MCP-002 extends `createPrismaDiscountCatalogueReader(database, options).execute(call)` through the existing `executeDiscountTool` port. Its task now names the actual reader, registration, policy/cursor and execution-boundary changes. The existing reader still has outreach-purpose restrictions that MCP-002 must remove for generic shop use. Preserve its bounded catalogue projection, source diagnostics and cursor identity while implementing the agreed mode/denial/unavailable semantics. Do not create another catalogue or repeat source integration merely because an earlier archive omitted it.

The present built-in registration path calls the discount port directly and lacks the existing published-call execution bounds. MCP-002 therefore adds the narrow shared mechanism inside `src/mcp/execution.ts`, passes the actual RPC signal/deadline through the existing private port and reuses the already selected policy without another read. Only named post-authorization catalogue generation/page/detail query failures may become optional unavailable data, after transaction rollback and a current-RPC check. Configuration, transaction cleanup, cancellation, malformed results and unexpected failures remain hard.

MCP-003 and the product changes preserve the present Woo diagnostic helper and regression behavior. Actual failures keep original sanitized provider/SDK messages, response details and causes through the Shared logger. Any future prepared-base omission is reported as the concrete missing path; it is not permission to reconstruct accepted work or reset a newer Database/package baseline.

## Resolved gaps and implementation owners

| Gap in the earlier definitions | Explicit correction | Owner |
| --- | --- | --- |
| MCP was assigned conversation/grant/lease responsibilities | Remove those reads/context from MCP; retain generic descriptors and move workflow permission, retained state and caller-specific failure handling to Background | MCP-002 / BACKGROUND-001 / SYSTEM-TEST-001 |
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

The Commerce wrapper emits one JSON stdout receipt. The submitted MCP importer also emits one stdout JSON receipt with exactly one taxonomy stage and publication null; diagnostics remain on stderr. Pending-migration dry-run planning carries a null importFingerprint/generationId and verified source/categoryCount. COMMERCE-001 validates the exact current CLI success/failure shapes and preserves genuine nonzero/missing-receipt errors. The wrapper uses only PLANNED, APPLIED, UNCHANGED, FAILED and NOT_RUN, retains earlier successful stages and never converts a failed/partial apply into complete setup. The child's exact TAXONOMY_CONFIGURATION_MISSING failure after migration maps to wrapper taxonomy FAILED/TAXONOMY_CONFIGURATION_UNAVAILABLE and publication NOT_RUN/PREREQUISITE_FAILED, with the original source reason preserved in diagnostics. Existing configuration/actor workflows supply prerequisites before rerun.

Existing/future store access is validated against the standard required `product_search` feature on provisioned Free/paid plans. The current Admin plan authoring already loads active `systemRequired` features and calls `buildDesiredPlanFeatures` in `src/lib/admin/merchant-knowledge-plan-policy.ts`; it is not hardcoded to two features. The SystemTest fixture must likewise derive required features from actual database rows. Fixture SQL is not evidence that Admin's authoring UI was exercised; that existing generic path is static source evidence, and no Admin implementation task is added.

## Validation ownership and review gate

`docs/agent-validation-execution-policy.md` governs execution. Repository agents run the named bounded checks. Long Docker/migration/system suites have an exact developer-owned command and expected result in their task. Preparing that handoff is compliant; marking an unrun suite passed is not. The explicit exception is for a specifically authorized already-claimed task, so these pending definitions do not grant an open-ended override.

A task can enter `review` with a separate unchecked developer-validation section. Architect acceptance/automatic completion still requires its mandatory evidence. Preserve valid matching evidence already supplied by the developer; do not rerun a long suite solely because the model did not launch it. A terminal SYSTEM-TEST-001 invocation remains developer-controlled after its dependencies are complete.

Every execution report records the launcher-resolved parent/implementation worktrees, task branch and source SHA, Database pin where relevant, exact command/result/exit code and disposable resource cleanup. An excluded suite, zero matched tests, a mocked path replacing the real target, a missing prerequisite, or a skipped scenario is not a pass.

## Definition patch validation

The consolidated Attempt 7 patch must apply directly to a fresh extraction of the exact current MCP-001 ZIP; no previous patch is required. Separately apply the already delivered Attempt 6 patch followed by the from-Attempt-6 amendment to a second fresh extraction. Both routes must produce byte-identical final documentation. Reverse each route in order and verify every original file is restored. Each ZIP must contain its one corresponding byte-identical patch. Validate strict whitespace application, actual application, `git diff --check`, reverse check and actual byte-restoring reverse application. Compare all completed task files, all task frontmatter, MCP-001 content from Completion Report onward, every decision index and every implementation file with the archive. Validate all ten task routes/dependency edges and all inspected source hashes against their explicitly recorded archive. These are documentation checks, separate from implementation runtime validation.

## Separate Shared public-contract cleanup

The completed Shared implementation exported `CommerceConversationToolContextSchema` and `CommerceConversationToolContext`; the current generic MCP path does not consume them. Their obsolete purpose should be removed in a separately owned Shared correction, followed by acceptance, a new immutable publication under the repository's public-API version policy and coordinated consumer pins. Preserve the 4.0.0 receipt and legitimate host/runner conversation/grant schemas. This amendment does not claim that cleanup is complete, add an unverified package version, or block the submitted MCP-001 work on an unused export.
