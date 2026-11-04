---
id: ARCH-058-SYSTEM-TEST-001
architecture_id: ARCH-058
title: Validate discovery, shipping and grounded customer responses end to end
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-058-DATABASE-001
- ARCH-058-SHARED-001
- ARCH-058-SHARED-002
- ARCH-058-MCP-001
- ARCH-058-MCP-002
- ARCH-058-MCP-003
- ARCH-058-SHOPIFY-001
- ARCH-058-COMMERCE-001
- ARCH-058-BACKGROUND-001
enables: []
created: '2026-11-04'
updated: '2026-11-04'
---

# ARCH-058-SYSTEM-TEST-001: Validate discovery, shipping and grounded customer responses end to end

## Architecture and execution boundary

Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`. Binding contracts: `docs/architecture/ARCH-058/contracts.md`. Supporting review: `docs/architecture/reviews/commerce-agent-product-discovery-20261104-015544-r03/review.md`. This task consumes all nine accepted implementation/publication tasks; it implements no application behavior or migration.

Definition revision: 2. **Defined but not materialised.** Status remains Pending until all nine prerequisites are Complete and architect-accepted. No task claim, branch/worktree, implementation, deployment, import or passing test is asserted. The complete task bundle is portable; no earlier review patch is required.

Use the launcher-prepared dedicated parent/implementation worktrees and record synchronization, submodules and accepted source identities. Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md` and `docs/observability/shared-logging.md`. The prepared `workspace_root` is authoritative for locating the accepted service checkouts.

## Objective

Prove the real operator wrapper, PostgreSQL 17/pgvector persistence, four standard capabilities, MCP/provider adapters, shipping scope/data outcomes, retained grants and Background reply composition together using deterministic disposable fixtures. Observe complete moderated/emulated product, shipping and soft-redirect replies, current-shop isolation, supported promotions and original redacted diagnostics. Provide a separately opted-in, bounded real-model multilingual evaluation; scripted correctness does not certify semantic retrieval or unrestricted prose quality.

## Scope and exact file ownership

Only `moda-interact-system-test` is writable. All paths below are relative to that repository. No application source, dependency task, parent index, migration, live deployment or remote merchant data is editable under this task.

| Existing path / symbol | Exact change |
|---|---|
| `catalogue/scenarios.json` | Register the ten deterministic rows and one optional quality row below with complete metadata and `sourceRequirements: ["ARCH-058-SYSTEM-TEST-001"]`. |
| `catalogue/historical-system-test-map.json` | Add the symmetric mapping to those eleven IDs and this canonical task path; definition-baseline status is `pending`, not a fabricated completed review. |
| `docs/SHOPIFY-COVERAGE-MATRIX.md` | Regenerate through `npm run validate:catalogue -- --write`; no handwritten generated rows. |
| `src/harness/selection.js:SUITES` | Add fixed-ID `product-discovery` and `product-discovery-quality` suites from the new contracts module. Do not filter their membership by task metadata, implementation status or registered executors. |
| `src/harness/cli.js:usage` | Add the suite names to help; preserve current parser/environment/authorization rules. |
| `scripts/run-system-tests.js:createDefaultExecutors` | Merge the new executors through the existing duplicate guard. No registration in generic `runner.js`. |
| `scripts/run-system-tests.js:createDefaultProvenanceProvider` | For the new IDs include accepted Database, Shared, MCP, Commerce, Background, Shopify scope configuration/runtime and the actual ingress/messaging applications executed; capture nested Database gitlinks and avoid duplicate descriptors. |
| `scripts/run-system-tests.js:main` | Invoke the scoped completeness/sidecar adapter for these suites and preserve normal evidence/exit behavior; no generic result-schema relaxation. |
| `package.json` | Add the five scoped scripts defined under Validation; retain existing scripts and dependencies. |
| `README.md` | Document prerequisites, deterministic versus optional quality execution, approved commands, evidence and cleanup. |

Create only these modules; keep each source/test module below the existing 300-line limit and `index.js` at or below 120 lines:

| New paths | Responsibilities |
|---|---|
| `src/harness/product-discovery/index.js`, `contracts.js`, `runtime.js`, `setup.js` | Executor composition; frozen IDs/case obligations; existing runtime/image/data-plane orchestration; actual operator command invocation and receipt assertions. |
| `src/harness/product-discovery/fixtures.js`, `provider-runtime.js`, `fault-controls.js`, `observations.js` | Owned shop/policy fixtures; external provider/embedding transports; bounded barrier/failure controls; SQL/protocol/provider/output observations. |
| `src/harness/product-discovery/provision-scenario.js`, `availability-scenario.js`, `products-scenario.js`, `benefits-scenario.js` | The first four deterministic scenarios. |
| `src/harness/product-discovery/failures-scenario.js`, `revalidation-scenario.js`, `language-scenario.js`, `logging-scenario.js` | The other four deterministic scenarios. |
| `src/harness/product-discovery/fallback-scenario.js`, `shipping-scenario.js` | The two added deterministic scenarios for complete soft responses and native shipping/provider-scope truth. |
| `src/harness/product-discovery/quality-scenario.js`, `quality-evaluation.js` | Separately authorised real-model execution and predeclared semantic scoring/call limits. |
| `src/harness/product-discovery/evidence.js`, `diagnostics.js` | Suite completeness, redacted case/receipt/provenance sidecars and actual original-error sink assertions. |
| `test/harness/product-discovery-contracts.test.js`, `product-discovery-executors.test.js`, `product-discovery-runtime.test.js`, `product-discovery-provision.test.js`, `product-discovery-fallback.test.js`, `product-discovery-shipping.test.js`, `product-discovery-logging.test.js`, `product-discovery-quality.test.js` | Harness tests for exact selection, complete case execution, real-command routes, fault/cleanup handling, whole fallback/shipping output, evidence and optional authorization/budget gates. |
| `test/fixtures/product-discovery/categories.en.txt`, `taxonomy-manifest.json`, `products.json`, `discounts.json`, `shipping.json`, `knowledge.json`, `response-cases.json`, `model-steps.json`, `semantic-cases.json` | Pinned test source/hierarchy/checksum; two-provider products/conditions/shipping outcomes and authorized knowledge fixtures; deterministic model steps/complete response expectations; independently labelled multilingual semantic cases. |

Read/reuse the existing `src/ephemeral-postgres.js`, `src/ephemeral-redis.js`, `src/whatsapp-emulator.js`, `src/harness/data-plane.js`, `processes.js`, `cleanup.js`, `command-recorder.js`, `provenance.js`, `evidence.js`, `execution-errors.js`, `environment.js`, `evidence-classification.js`, `background-production-image.js`, `background-worker-container.js`, `mcp-production-image.js`, `src/harness/language/mcp-runtime.js`, `conversation-runtime.js`, `conversation-turn.js`, `src/harness/aimock/runtime.js` and approved provider transport/emulator helpers. Do not copy their general implementations or alter their defaults. If a missing reusable harness port prevents this scoped composition, report the exact gap before widening the allowlist.

## Fixed scenario contract

The ten `product-discovery` rows use domain `COMMERCE`, layer `L3`, `evidenceClass` and `requiredEvidenceClass` both `BLACK_BOX`, `automation: "automated"`, `liveAuthorizationRequired: false`, and existing `shopify-release` requirements. Their implementation must exercise actual CLI/private HTTP/ingress/worker routes, not import the application evaluator or reimplement it in the harness. External provider, model and embedding transports may be deterministic substitutes; disclose them precisely.

| ID | Required case families |
|---|---|
| `COMMERCE-DISCOVERY-PROVISION-001` | Empty-target dry-run, actual migrations/import/publication, identical repeat, restart/restore, interrupted/conflicting import, environment isolation, script receipts and Admin independence. |
| `COMMERCE-DISCOVERY-AVAILABILITY-001` | Existing/future Free and paid Shopify/Woo stores; absent/false preferences; all four standard tools; unchanged optional Merchant Knowledge/feature denial; published and built-in identity/grant cases. |
| `COMMERCE-DISCOVERY-PRODUCTS-001` | Taxonomy meaning versus inventory; provider-scoped exact category membership, direct text search, explicit bounded visible-product browse, product/variant identity, pagination, currency and no-result distinctions. |
| `COMMERCE-RECOMMENDATION-BENEFITS-001` | NONE/FIXED/AI, known and conditional offers, unknown facts, native sale, exact quantities/currency, independent alternatives, compatible/incompatible combinations and no mutations. |
| `COMMERCE-RECOMMENDATION-FAILURES-001` | Typed optional taxonomy/discount unavailability versus outer error, incomplete/null/empty facts, exhausted budgets and continued independently grounded product replies. |
| `COMMERCE-RECOMMENDATION-REVALIDATION-001` | Source/policy/price/quantity changes at host finalization; stale/takeover barriers; full-text removal of invalid claims; retained conversation grant transition and old evidence rules. |
| `COMMERCE-RECOMMENDATION-LANGUAGE-001` | Actual published instructions and complete host-composed recommendation text in all 20 supported fixed-message locales, preserved regional tags, wrapper/moderation/admission path and no model prose bypass. |
| `COMMERCE-RESPONSE-FALLBACK-001` | Out-of-scope and missing-information limitations; context/basket/browse precedence; one verified product with supported offer or product-only; no usable product/store fallback; rejection of repeated suggestions; full-text branch control. |
| `COMMERCE-SHIPPING-INFORMATION-001` | Actual shipping operation/provider guard, independent policy/product statuses, exact variant/measurement semantics, stored-scope preflight versus terminal denial, missing/oversized/untrusted policy, positive facts/link composition and unverifiable destination claims. |
| `COMMERCE-DISCOVERY-DIAGNOSTICS-001` | Original harmless provider/SDK/Prisma diagnostics at the actual emitted sink, stage/correlation, redaction before evidence writing, bounds, sink failure and source/image/package provenance. |

`COMMERCE-DISCOVERY-QUALITY-001` is the only `product-discovery-quality` row: domain `COMMERCE`, layer `L4`, `BLACK_BOX`, `automation: "developer-live"`, `liveAuthorizationRequired: true`, `requiredFor: []`. It uses local owned application fixtures and actual explicitly configured model/embedding providers, never a live customer or shop. It is optional release-quality evidence and not a mandatory cost-bearing acceptance prerequisite for the ten deterministic rows.

Freeze scenario/case IDs, required case sets and evidence obligations in `contracts.js`. Catalogue rows and historical mapping must agree with those IDs. Required cases cannot disappear because status is changed, an executor is absent or governance requirements are later supplemented. Undefined executor results, partial subcase execution and missing artifacts must not inherit the generic runner's default PASS.

## Requirements

### 1. Real accepted applications and operator command

1. Capture all nine accepted task revisions and the actual executed implementation images, consumed Shared package version/integrity/export evidence, runner version and nested Database revisions, including the accepted Shopify declared-scope/runtime changes. The parent targets Shared `4.0.0` conditional on its actual accepted baseline remaining `3.1.0`, and runner `1.1.0` with new release compatibility `>=1.1.0 <2.0.0`; obtain the exact published package from SHARED-002, not a sibling import or guessed version. Source SHA, image revision and installed artifact must agree or the affected run is BLOCKED. A declared permission or fixture session scope is not evidence that a real existing merchant completed reauthorization; report actual exercised scope routes separately.
2. Use existing disposable PostgreSQL infrastructure with an explicitly supplied approved PostgreSQL 17 image that includes pgvector. Record the resolved image digest and extension/server versions. Do not change the generic harness default, install managed-provider binaries, use `db push`, or create a task-private replacement schema. Apply the actual accepted Database migrations through the real Commerce-owned wrapper. Existing Redis may still support queues; taxonomy lookup itself must have zero dependency on Admin Redis keys/indexes.
3. Execute `npm run commerce:setup-discovery` in the accepted Commerce worktree with required `--workspace-root=<prepared root>`, explicit `--environment=test`, and `--dry-run` or `--apply`. Capture the real child commands (`migrate:deploy`, `taxonomy:sync`, `commerce:sync-tools`) and actual receipts. The parent workspace has no runtime wrapper. Do not use the broad database seed or fake publication rows to make the setup look successful.
4. The deterministic source is a bounded complete fixture graph, with known bytes/checksum/count and deterministic embedding transport. Inject its approved fixture manifest/provider only through the accepted test-only injection boundary, guarded by `NODE_ENV=test` and the test deployment. Run the same parser, validation, import, application services and CLI argument path. There is no production `--manifest`/URL override; `--source` bytes must match the trusted manifest. Do not weaken checks, substitute a separate importer or make mandatory deterministic tests depend on downloading the live corpus. Actual approved full-corpus deployment verification is separately reported.
5. Assert the exact parent receipt schema: environment/mode; ordered preflight/migration/taxonomy/publication stages; truthful status/code; source SHA/import fingerprint/generation/count; previous/current release; and actions for all four standard tools. Verify nonempty compatible response instructions and all owned recommendation/presentation fields in the actual immutable release. A source/configuration/embedding/publication failure must exit nonzero, preserve completed prior stages and mark unexecuted stages `NOT_RUN`. An exit code or partial receipt alone cannot certify readiness.

### 2. Durable corpus, repeatability and isolation

6. On a fresh disposable database, dry-run performs no migration/write/audit/publication/billable embedding call and reports post-migration checks as planned. First apply creates schema/constraints, targeted standard plan mappings, one complete active generation and the intended immutable release. Snapshot unrelated plan, release and feature state before/after; it must remain unchanged.
7. Repeat identical apply: no new embeddings, duplicate categories/generations/tools/capabilities/releases or audit events for unchanged work. Stop/restart PostgreSQL and MCP and resolve the same pinned corpus. Take a scoped dump and restore it to a second disposable PostgreSQL 17/pgvector instance through normal tools; verify generation/source/provenance, FK/constraint validity and equivalent lookup without rebuilding or Redis fallback. Always remove temporary dumps and containers.
8. Test known partial preparation failure, invalid hierarchy/checksum/dimensions, config change between preparation and activation, and concurrent identical/different candidates with deterministic barriers. The old active complete generation survives failures; identical winners no-op; different winners conflict; no partial generation becomes visible. Pin a running reader across replacement and prove no mixed embedding model/generation or early deletion. Initial exact cosine search is tested; no ANN behavior is assumed.
9. Exercise two logical environments against the same disposable database with identical source/model provenance. Canonical fingerprints include the environment and therefore differ for valid imports; also insert an explicitly adversarial same-fingerprint fixture to prove selection never relies on that hash alone. Create the second logical environment's rows and query state only inside the disposable database harness. All fixture-manifest/provider CLI injection remains guarded by `NODE_ENV=test`, deployment `TEST` and explicit `--environment=test`; do not run a fixture importer under another environment label or add a production manifest override. Configuration AAD, generation identity/active marker, release pointer and query selection remain environment-scoped. Wrong environment/target checks fail before mutation; one environment cannot reuse the other's active generation. Service fixtures remain loopback/disposable; no shared/live deployment is targeted.
10. Fingerprint the Admin taxonomy implementation files named by the reviewed baseline and record Redis command observations. Setup/import/search must not edit them, write Admin aliases/metadata, rebuild its corpus or depend on its process being available. Source/configuration may be read-only shared under the accepted `REFERENCE_TAXONOMY` contract; do not change that setting as a shortcut.

### 3. Standard capabilities and provider truth

11. For Shopify and Woo, create Free and paid stores both before and after provisioning, using existing plan/materialization entrypoints for future-plan behavior. Verify real `tools/list`, manifest and executable descriptors for resolver/search/get/shipping without merchant opt-in; absent and false obsolete preference rows do not disable the required feature. Missing policy permission or unsupported native policy does not remove the shipping descriptor or disable product reads. Optional unrelated features, including Merchant Knowledge, remain denied without their own entitlement/preference. Suspended shops, inactive/invalid plans, wrong shops and unavailable/revoked provider connections retain ordinary denial. Unexpected custom `product_search` members cause setup conflict instead of accidental global enablement.
12. Verify normal published descriptor hashes/revisions and canonical built-in name/version/hash identities. Built-ins have no synthetic Studio IDs. Observe the real encoded `{purpose: "CONVERSATION", conversationId, inboundVersion, grantId}` context: initial null-grant resolution, actual guarded grant insertion, then the retained database ID on subsequent reads/calls. Missing generic context does not expose conversational discount tools/degradation; forged/cross-shop/expired/wrong-version context or grant fails closed. Tampered hashes, unknown built-ins, collisions, a list/manifest mismatch and a descriptor revision change fail closed. Existing grants are not widened or deleted by setup. A fresh conversation receives the new approved set; retained conversations require the documented pre-production transition. A grant obtained under NONE does not gain discount tools merely because policy later changes. Check the updated Database JSON-shape/insert guards reject forbidden branches without a trigger bypass.
13. Use the actual Shopify query-builder/provider-read guard composition, including its corrected literal pagination bound. Assert exact Shopify taxonomy GID/version-to-native filter translation, returned assigned category membership and variant progress. Woo category IDs are positive shop-local identifiers with exact returned membership; identical numeric IDs in different shops never mix. Reject a Shopify reference ID used as a Woo native category before provider I/O. Product with no category remains findable by a supported title search.
14. Cover bounded empty-but-continuable pages, cursor filter/shop changes, genuine exhaustion, unavailable product reads and category ambiguity. A reference miss or similarity score cannot become “this merchant does not sell it.” Record actual provider request bounds. Unknown price currency/market remains unknown; never infer the customer's market price from a global taxonomy or another shop.
15. Exercise browse through the actual search input/projector/provider path: default false; true with null/omitted query and no category; contradictory arguments rejected before provider I/O; existing filters/defaults and page bounds retained; cursor binds browse/visibility/shop/filters and rejects cross-mode replay. Include active/published visible products, drafts/private/hidden/search-only Woo parents, unpublished variations, unknown availability and unsafe/null URLs. Soft fallback requests availableOnly and returns only verified available linked products; an empty continuable page cannot become exhaustion or invented bestseller status. Keep exact-get/search output schemas unchanged.

### 4. Benefits, final claims and existing send controls

16. Drive actual inbound turns through existing ingress/queue/application routes and capture the WhatsApp emulator's complete final text. Deterministic model responses use the accepted recommendation pair plus optional `responseDisposition`/`shippingInformationSelection`; no harness-side evaluator or final-message substitute. In addition to structured data, assert persisted prepared text, wrapper/moderation input and provider-emulator text agree on the supported claim. A raw Studio runner preview is not evidence of Background's composed customer output.
17. Cover current NONE/FIXED/AI and active override; exact product/null-variant identity, quantity and basket scope; a known supported percentage/amount promotion; a known unmet subtotal; unknown quantity/customer/usage conditions; currency mismatch; native sale; two independently assessed alternatives; pairwise-compatible offers and an incompatible pair. Missing material facts must produce terms/limitations or no promotion, never unsupported eligibility, additive percentages or invented final savings. Observe zero cart/code-application/discount-creation mutations.
18. Inject taxonomy `NOT_READY`/classified temporary failure and the exact conversation-only discount optional-unavailable object. Assert independently grounded product replies can continue with appropriate limitations and no stale promotion. Contrast empty complete results, `details: null`, partial discovery and outer terminal errors. A terminal ERROR followed by a successful product call still requires referral; malformed data, denial and stale/cancelled turns do not take the optional fallback. Budget exhaustion cannot become catalogue-wide absence.
19. Pause source responses at the accepted host finalization boundary, change selected IDs/offer status/source, price/currency/availability, quantity/variant, used shipping facts/policy reference or the owned basket, then release the barrier. Revalidation must remove/recompute the claim within the same call/deadline budget. Inspect the entire returned and emulated message for old code/amount/terms/shipping claims, not just changed details. Inject invented promotion or shipping prose with empty/missing/forged selections, plain text or STANDARD after product/discount or product-bearing shipping observations (request productId non-null), and shipping selection without disposition: none can bypass controlled composition. Contrast null/null policy-only observations outside any controlled branch. Validate latest same-argument shipping observation and current refresh identity. Legacy evidence unknown/expired/nonqualifying IDs remain rejected; canonical facts never fabricate legacy evidence IDs.
20. At existing cancellation/ownership boundaries race a new inbound message, HUMAN takeover and STOP/control change. Preserve current suppression/requeue/moderation/admission and one-message ordering behavior. Do not demand a new processor hook or provider-atomic redemption: this architecture revalidates current observed facts at host finalization, then preserves the existing processor guards. Observe the actual final send callsite and count, without changing application worker code.
21. Load published Platform/Shop instruction fixtures and verify host precedence/ownership; changing shop or using an unpublished revision cannot alter another shop. Check recommendation, out-of-scope, unverified-shipping, supported shipping and store-only fixed-message branches across the canonical 20 locales, including distinct `pt-BR`/`pt-PT` and `zh-Hans`/`zh-Hant`. Include an accepted same-turn detection before processor persistence, explicit preference, short/ambiguous input and same-base preservation: body and wrapper must use the same effective language. Assert placeholder/value/code integrity and known-currency formatting. English source taxonomy or scripted fluent text is not multilingual retrieval evidence.
22. Exercise the private hostComposedReplyCandidates route at the existing processor composition call, using long actual configured wrappers, valid URLs and material discount conditions. Candidates contain at most three complete bounded bodies, first equal to replyText, from full output to one product to minimal disposition/store reference; no sliced link, lost qualification, extra model/tool/send or raised 4096-character limit. Observe one actual wrapper context/slot/locale load in that stage, no host preflight wrapper reads, and advancement only on OUTPUT_TOO_LONG. Invalid input/variables/locale/definition or already-wrapped content must not become a successful shorter reply. No-wrapper returns the exact first body. Check selected-candidate digest/application replay, mismatch when the prior candidate is absent, ordinary one-body/HUMAN compatibility and malformed/model-forged candidate rejection. A minimal wrapped body that cannot fit retains the existing typed refusal. The chosen complete text alone enters the unchanged moderation/admission/delivery sequence.

### 5. Soft responses and native shipping truth

23. Drive an out-of-scope weather-in-France message through actual inbound routes. With current owned product context, show one verified shirt with a canonically supported permitted offer; with NONE or no usable permitted offer, show the verified product/link alone; with no product context, observe explicit bounded browse; with no usable product, show a verified store reference without a catalogue-wide absence claim. Assert no weather/general-web call, fabricated query/category/destination or bestseller/similarity claim. Verify refreshed basket precedence and honour rejection of repeated product suggestions. Keep all new discovery and refresh calls within the existing shared turn budget.
24. For missing shipping knowledge, cover separately ungranted/disabled Merchant Knowledge, an authorized empty result and an irrelevant returned chunk. Where granted and within budget, observe the relevant native/knowledge read before the limited statement. Shipping-information-unverified output acknowledges the specific uncertainty, gives a verified policy/store reference and may offer one separately validated related product/offer. A location in an unrelated request is not a supplied shipping destination. A hard auth/tool error after earlier useful facts still forces unchanged hard referral with empty details/evidence; no soft disposition clears requiredReferral.
25. Execute the real `commerce_get_shipping_information` / `shipping.getInformation` operation with policy-only null IDs, Shopify product-only existence/VARIANT_REQUIRED, exact Shopify variant facts, Woo simple and selected-variable product facts, and variable-parent VARIANT_REQUIRED. Verify source IDs, shop/provider scoping, nullable measurements/units, explicit virtual flag and authoritative requiresShipping rules, including unknown Woo variation requiresShipping. Reject variantId without productId, mismatches, Woo types outside the new explicit simple/standard-variable/exact-variation support policy, malformed/negative values and unsafe provider URLs through the existing outer error path. Do not infer physical delivery from virtual=false or print unitless measurements as kg/cm.
26. Exercise trusted offline stored scopes absent/null/blank versus granted. Missing read_legal_policies must yield policy SCOPE_NOT_GRANTED with zero policy HTTP requests while an authorized product fact can remain AVAILABLE. Native Woo policy is UNSUPPORTED with no guessed policy/WordPress request. A granted policy request returning 401/403/GraphQL failure remains terminal ERROR with original safe diagnostics. Successful no-policy, empty-body, exact bounded-body, oversized selected-body and oversized whole-response cases must distinguish NOT_CONFIGURED, EMPTY, AVAILABLE, TOO_LARGE and outer read failure respectively. Verify the 8000-character and 16384-UTF-8-byte policy-body limits, safe current-shop policy URL and source timestamps; no silent truncation or fabricated URL/time.
27. Assert positive combined STANDARD output contains only the exact supported requiresShipping statement, verified policy link and independently validated product/offer. Policy HTML, malicious runtime instructions, model summaries, embedded coupon text and unknown-unit values cannot enter that composed body. A requested destination-specific rate/speed these facts do not support remains SHIPPING_INFORMATION_UNVERIFIED, even when a policy exists. Ordinary policy-only grounded answers may use the existing answer path outside controlled composition; do not claim these deterministic checks semantically verify every legacy free-text answer. Observe zero cart/rate-calculator/write calls and zero Background-to-provider calls.

### 6. Original errors and truthful evidence

28. Capture actual application JSON output or the installed Shared logger sink at importer, MCP and Background boundaries. Inject harmless identifiable provider/SDK/Prisma messages alongside sensitive sentinels; original safe message/code/status/request ID, stage and available correlation must survive. Assert before generic evidence redaction that secrets, tokens, DSNs, customer data and unsafe payloads are absent. Never persist the sentinel/raw capture or treat a sanitized artifact as proof that the emitting application redacted correctly.
29. Test wrapping, optional degradation and terminal paths; do not accept a generic `UNAVAILABLE` record in place of the original available cause. Original source detail intentionally absent from the public tool result is proved in the owning MCP/importer sink, not invented in Background. Buffer truncation, wrong installed logger package, a mocked logger method or missing sink capture makes that assertion incomplete. Logging-sink failure must not alter the application result.
30. Retain normal harness run/summary/command evidence and add only `product-discovery-cases.json`, `product-discovery-provisioning.json`, `product-discovery-provenance.json`, `product-discovery-logging.json`, and optional `product-discovery-quality.json` in its normal run directory. Include actual case outcomes, source/image/package identities, safe fixture correlations, receipts, request counts and cleanup. Evidence modules add a strict suite-specific completeness check, without changing generic scenario/result schemas.
31. Setup unavailability uses existing `ScenarioBlockedError`; wrong behavior uses `ScenarioFailureError`, with safe original cause evidence. Every required case must return a truthful explicit result; FAIL/BLOCKED/NOT_RUN/NOT_APPLICABLE or an absent case prevents deterministic suite acceptance. A deliberately suppressed business reply may pass only when suppression is the asserted result. Cleanup failure is recorded and cannot be silently swallowed.

### 7. Separate real-model multilingual quality evidence

32. Freeze 60 synthetic semantic cases: direct noun, functional paraphrase and an ambiguous request for each of the 20 supported locales. Labels must be reviewed independently of the tested model against the pinned corpus: expected acceptable category branches/products, permitted clarification, and prohibited stock/discount claims. The actual approved corpus/version and real embedding/model identifiers are recorded; no fixture vector pretending to be a production embedding.
33. Run only when the operator explicitly selects `product-discovery-quality`, provides the existing live-authorization flag and configures provider credentials/cost limits. Keep application/merchant/send destinations disposable and use NONE mode to isolate relevance; there are no real customer sends or deployments. Enforce at most 60 cases, 240 total model invocations, 120 query embeddings, 600 tool calls and a 30-minute suite deadline, or stricter operator limits. Preserve smaller per-turn production limits. No unbounded retry or automatic paid rerun.
34. Report per-locale and overall top-five candidate recall for labelled noun/paraphrase cases, correct clarification/qualified-answer counts for ambiguity, actual shop/product identity fidelity, unsupported factual/promotional claims, latency, call/token usage and observed provider-reported cost when available. Store the predeclared scoring rubric and denominator, not an invented universal confidence threshold. Label the result a measured evaluation, not general semantic certification. The existing 60-case retrieval set does not establish semantic quality of new soft redirects or shipping summaries; report that coverage limit rather than silently increasing paid cases or claiming scripted fluency proves it. Missing credentials/budget/approved corpus yields explicit NOT_RUN or BLOCKED for this separate row; it does not become a scripted PASS and does not block acceptance of the ten deterministic runtime rows.

## Work items and acceptance criteria

- [ ] Verify all nine accepted revisions and executed image/installed package provenance, including nested Database state and Shopify scope source/runtime.
- [ ] Register fixed suites, eleven catalogue/mapping rows, executors, generated matrix and scoped completeness/sidecars.
- [ ] Execute the actual Commerce setup command on PostgreSQL 17/pgvector with no-op, partial failure, conflict, restart, restore and same-fingerprint environment isolation cases.
- [ ] Prove standard tools for existing/future Free/paid Shopify/Woo stores without broadening unrelated entitlements or retained grants.
- [ ] Exercise real MCP/provider composition and current-shop products/categories/variants, pagination and price-context behavior.
- [ ] Prove bounded visible-product browse and complete out-of-scope/missing-shipping replies with one verified offer/product or store-only fallback.
- [ ] Verify native shipping facts, independent policy outcomes, original permission preflight versus terminal denial, current revalidation and no destination/rate/cart inference.
- [ ] Prove known/conditional/unknown/native-sale/combination/failure/revalidation outcomes against the complete customer text and unchanged outbound controls.
- [ ] Verify all 20 fixed-message locales, same-turn effective language, actual instruction ownership, controlled-branch bypass resistance and the actual configured wrapper limit.
- [ ] Verify original safe error diagnostics and source-side redaction at the real sink; retain failed/blocked evidence truthfully.
- [ ] All ten deterministic rows and required subcases pass; no missing case or silently defaulted PASS.
- [ ] Provide the separately runnable quality suite and report whether its optional real-model evaluation was run; make no semantic-quality claim from deterministic fixtures.

## Validation commands

Inspect package scripts and use the workspace Node bootstrap if needed. The following scoped scripts are deliverables of this task, not presumed baseline commands:

| New script | Exact command |
|---|---|
| `test:product-discovery-harness` | `node --test test/harness/product-discovery-*.test.js` |
| `system:product-discovery:plan` | `node scripts/run-system-tests.js --suite product-discovery --list` |
| `system:product-discovery` | `node scripts/run-system-tests.js --suite product-discovery --execute` |
| `system:product-discovery:quality:plan` | `node scripts/run-system-tests.js --suite product-discovery-quality --environment LOCAL_APP --list` |
| `system:product-discovery:quality` | `node scripts/run-system-tests.js --suite product-discovery-quality --environment LOCAL_APP --execute` |

From the prepared implementation worktree:

```sh
npm ci
npm run validate:catalogue -- --write
npm run validate:catalogue
npm run lint
npm run test:product-discovery-harness
npm run test:harness
npm run system:product-discovery:plan -- --workspace-root "$MODA_WORKSPACE_ROOT" --json
npm run system:product-discovery -- --workspace-root "$MODA_WORKSPACE_ROOT" --json
npm run system:product-discovery:quality:plan -- --workspace-root "$MODA_WORKSPACE_ROOT" --json
git diff --check
```

The deterministic executors invoke the accepted Commerce command in its own worktree:

```sh
npm run commerce:setup-discovery -- --workspace-root "$MODA_WORKSPACE_ROOT" --environment=test --dry-run
npm run commerce:setup-discovery -- --workspace-root "$MODA_WORKSPACE_ROOT" --environment=test --apply --source="$PRODUCT_DISCOVERY_FIXTURE_SOURCE"
```

`PRODUCT_DISCOVERY_FIXTURE_SOURCE` is a task-owned temporary source path established by the test-only fixture boundary, not a production manifest override. The harness records each invocation and the explicit environment/accepted revision; it must not inherit a developer's live database accidentally.

Only after explicit operator opt-in and configured cost bounds, the separate quality run is:

```sh
npm run system:product-discovery:quality -- --workspace-root "$MODA_WORKSPACE_ROOT" --allow-live --json
```

Do not alter the existing live-environment gate. This task authorizes disposable execution, not production or deployed-test changes. Record exact failing/blocked commands and matching baseline conditions rather than replacing missing execution with static source assertions.

## Dependencies, overlap and stop condition

The nine frontmatter prerequisites are the complete implementation dependency set. Existing harness/source work from ARCH-056 and concurrent System-Test owners must be rebased and coordinated at the actual named shared files before editing. Preserve accepted scenario IDs, suite behavior and metadata; do not blanket reopen another task or add every historical suite as a prerequisite. Application defects return to the appropriate ARCH-058 owner; this task never patches applications to make its evidence green.

When the ten deterministic scenarios and required harness checks pass, complete the report with optional quality status, publish normal mirrored task evidence, set this task to Review through the established workflow and return to `moda_architect`. Do not mark the architecture Complete, deploy, merge to main, modify indexes or begin another task.

## Completion Report

Not started. Record worktree/synchronization evidence; parent/implementation branch and commit/push results; all accepted upstream SHAs and actual images/installed Shared/runner/Database/Shopify identities; exact changed paths; commands; ten fixed scenario/subcase outcomes; provisioning/no-op/restart/restore/environment evidence; complete recommendation/fallback/shipping replies, 20-locale results and wrapper-length outcomes; original-redacted sink assertions; cleanup; optional real-model status and measured scope; unresolved issues and owner handoffs. Do not prefill pass counts, receipt values, hashes or deployment claims.

## Architect Review

Pending. Review both histories, physical isolation, exact source/package execution, completeness of the fixed black-box cases, true application boundaries, unchanged Admin/Redis behavior, full-text/claim controls, source-side logging redaction and separation of optional semantic-quality evidence before acceptance.
