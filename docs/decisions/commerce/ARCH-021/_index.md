# ARCH-021 Commerce Tasks

Architecture:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Assigned Agent:

`moda_commerce`

Coordinator:

`moda_architect`

## Phase 1 — real Studio service wiring and shop execution context

Phase 1 is deliberately Commerce-only. It does not introduce model/prompt persistence,
Shared contracts, Background changes or live provider execution.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-001](COMMERCE-001-expose-production-connections-studio-port.md) | Expose production Connections through Studio server actions | Complete | ARCH-020-COMMERCE-020, 024, 028 |
| [COMMERCE-002](COMMERCE-002-switch-connections-routes-to-production-port.md) | Switch U15/U16 routes from fixtures to production ConnectionPort | Complete | COMMERCE-001, ARCH-020-COMMERCE-022 |
| [COMMERCE-003](COMMERCE-003-expose-studio-shop-execution-context.md) | Expose server-validated selected-shop execution context | Complete | ARCH-020-COMMERCE-013, 018 |
| [COMMERCE-004](COMMERCE-004-add-studio-selected-shop-context.md) | Add Studio-wide selected-shop URL/navigation context | Complete | COMMERCE-003 |
| [COMMERCE-005](COMMERCE-005-wire-real-connections-into-tool-authoring.md) | Wire persisted connection revisions into U06 Tool authoring | Complete | COMMERCE-001, COMMERCE-004, ARCH-020-COMMERCE-023 |
| [COMMERCE-006](COMMERCE-006-install-javascript-response-panel-production-composition.md) | Install production JavaScript response-panel composition | Complete | COMMERCE-005, ARCH-020-COMMERCE-026, 027, 031 |

## Execution frontier

COMMERCE-001 through COMMERCE-006 are architect-accepted Complete. Phase 1 has no
remaining executable implementation task.

```text
Phase 1 frontier: none — implementation set complete
```

The parent ARCH-021 Phase 1 exit criteria are reconciled. Phase 2 is materialised below. DATABASE-001 and COMMERCE-007/008/009/010/011/012/014/015 are architect-accepted Complete. The current executable Phase 2 Commerce frontier on this branch is COMMERCE-013.

## Phase 1 dependency graph

```text
ARCH-021-COMMERCE-001 ─────> ARCH-021-COMMERCE-002
          |
          +------------------------------+
                                         |
ARCH-021-COMMERCE-003 -> COMMERCE-004 -> COMMERCE-005 -> COMMERCE-006
                                         ^
                                         |
                              COMMERCE-001+
```

Phase 1 is architect-accepted Complete: COMMERCE-001 through COMMERCE-006 are Complete
and the parent ARCH-021 Phase 1 exit criteria are reconciled. Phase 2 is materialised below
with DATABASE-001 as the initial Ready frontier.

## Phase 2 — model catalogue and platform/shop Agent Configuration

Phase 1 is architect-accepted Complete. Phase 2 adds the new Agent Configuration domain without
reopening the accepted Connections/shop-context/Tool-authoring composition.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-007](COMMERCE-007-implement-model-configuration-service.md) | Implement model catalogue/default/shop-override service | Complete | DATABASE-001, ARCH-020-COMMERCE-002 |
| [COMMERCE-008](COMMERCE-008-implement-prompt-template-service.md) | Implement category-organised reusable prompt-template service | Complete | DATABASE-001, ARCH-020-COMMERCE-002 |
| [COMMERCE-009](COMMERCE-009-implement-prompt-lifecycle-service.md) | Implement platform/shop prompt lifecycle and active pointers | Complete | DATABASE-001, COMMERCE-008, ARCH-020-COMMERCE-002 |
| [COMMERCE-010](COMMERCE-010-resolve-effective-agent-configuration.md) | Resolve effective shop/platform model + prompt independently | Complete | COMMERCE-003, COMMERCE-007, COMMERCE-009 |
| [COMMERCE-011](COMMERCE-011-build-platform-agent-configuration-ui.md) | Build Agent Configuration shell + platform model UI | Complete | COMMERCE-006, COMMERCE-007 |
| [COMMERCE-012](COMMERCE-012-build-shop-agent-configuration-ui.md) | Build selected-shop model/prompt override surface | Complete | COMMERCE-004, COMMERCE-007, COMMERCE-008, COMMERCE-009, COMMERCE-010, COMMERCE-011 |
| [COMMERCE-013](COMMERCE-013-build-platform-prompt-template-ui.md) | Build category-organised platform prompt-template library UI | Complete | COMMERCE-008, COMMERCE-011, COMMERCE-015 |
| [COMMERCE-014](COMMERCE-014-build-platform-prompt-authoring-ui.md) | Build application-wide CommerceAgent prompt authoring UI | Complete | COMMERCE-008, COMMERCE-009, COMMERCE-011, COMMERCE-015 |
| [COMMERCE-015](COMMERCE-015-expose-prompt-template-revision-history.md) | Expose prompt-template revision-history read contract | Complete | COMMERCE-008 |

Phase 2 is architect-accepted Complete. The authoritative task files record COMMERCE-007 through COMMERCE-015 Complete; there is no remaining Phase 2 Commerce execution frontier.

```text
Phase 2 frontier: none — implementation set complete
```

### 2026-09-23 - COMMERCE-013 Attempt 5 accepted

- Accepted canonical local revision reconciliation using COMMERCE-015 `revisionNumber DESC, id ASC` ordering and immediate newest-published revision/hash presentation.
- Accepted exact-operation `unknown -> ok` reconciliation with preservation of the original success reconciler and exact original `operationId`.
- Accepted the Attempt 5 launcher/worktree/synchronization/submodule evidence and focused 10-test UI/production validation.
- Marked COMMERCE-013 Complete. COMMERCE-012 remains the sole executable Phase 2 Commerce frontier.

### 2026-09-23 - COMMERCE-014 Attempt 2 accepted

- Accepted exact published template-revision selection/revalidation with category context and persisted copy provenance.
- Accepted dirty-editor guards for publish, new/copy/template draft creation and pointer activation.
- Accepted canonical COMMERCE-015 revision-history wiring, PLATFORM-only singleton lineage rediscovery, ADMIN-authenticated reads and real production prompt-action handoff.
- Marked COMMERCE-014 Complete. COMMERCE-012 and COMMERCE-013 remain the executable Phase 2 Commerce frontier.

### 2026-09-23 - COMMERCE-014 Attempt 1 changes requested

- Added the already-Complete COMMERCE-015 revision-history read as an explicit dependency for deterministic exact-revision selection.
- Returned COMMERCE-014 to Ready for Attempt 2 after architect review identified dirty-editor mutation safety, exact revision selection and focused validation requirements.

Prompt templates are platform-wide copy-on-use authoring assets in Phase 2. They are organised
under data-driven categories/classifications such as `Clothing & Fashion`; a category may contain
multiple templates. Categories are not a code enum. Using a published template revision copies
its exact text into a prompt draft and records provenance; later category/template changes do not
mutate that prompt.

Phase 2 also performs an incremental Studio decomposition. COMMERCE-011 creates the dedicated
Agent Configuration route/module and platform model UI. Once that shell exists, COMMERCE-012
(selected-shop overrides), COMMERCE-013 (template library) and COMMERCE-014 (platform prompt
authoring) are independently reviewable UI capabilities with their own service dependencies; they
must not be artificially serialized. All Agent Configuration state/actions stay outside
`StudioWorkspace`, and unrelated Studio domains are not rewritten merely to reduce file size.


## Phase 3 — complete Tool authoring

Phase 3 is contract/authoring only. It does not make a real Shopify or external provider call. The CommerceAgent's persisted `inputSchema` remains the argument contract; invocation values remain runtime-generated.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-016](COMMERCE-016-establish-commerce-tool-definition-contract.md) | Establish canonical Commerce-owned Tool-definition contract | Complete | ARCH-020-COMMERCE-021, 030 |
| [COMMERCE-017](COMMERCE-017-implement-request-javascript-processor.md) | Implement bounded `buildRequest({args})` QuickJS processor | Complete | COMMERCE-016, ARCH-020-COMMERCE-029, 026 |
| [COMMERCE-018](COMMERCE-018-implement-shopify-admin-graphql-compiler.md) | Implement pinned Shopify Admin GraphQL 2026-07 compiler + toolkit oracle | Complete | COMMERCE-016, ARCH-020-COMMERCE-011 |
| [COMMERCE-019](COMMERCE-019-implement-phase3-tool-authoring-validation.md) | Establish common validation/auth/error contract and `LIVE_TEST_REQUIRED` publication gate | Complete | COMMERCE-016, COMMERCE-027, ARCH-020-COMMERCE-030 |
| [COMMERCE-020](COMMERCE-020-extract-tool-authoring-domain.md) | Extract Tool authoring onto named Server Actions + explicit reconciliation | Complete | COMMERCE-016, 005, 006, 027, 029 |
| [COMMERCE-021](COMMERCE-021-complete-external-http-authoring-ui.md) | Complete External HTTP request/response authoring UI | Complete | COMMERCE-019, 020, 023, COMMERCE-005, 006 |
| [COMMERCE-022](COMMERCE-022-build-shopify-admin-tool-authoring-ui.md) | Build Shopify Admin GraphQL authoring UI | Complete | COMMERCE-019, 020, 024 |
| [COMMERCE-023](COMMERCE-023-implement-external-http-authoring-validation.md) | Implement External HTTP validation and safe request preview | Complete | COMMERCE-016, 017, 019, ARCH-020-COMMERCE-030 |
| [COMMERCE-024](COMMERCE-024-implement-shopify-admin-authoring-validation.md) | Implement Shopify Admin GraphQL authoring validation | Complete | COMMERCE-016, 018, 019 |
| [COMMERCE-036](COMMERCE-036-create-tool-with-initial-draft-atomically.md) | Create Tool + revision-1 DRAFT as one lifecycle operation | Complete | COMMERCE-016, COMMERCE-020 |
| [COMMERCE-037](COMMERCE-037-persist-initial-tool-with-narrow-transaction.md) | Persist initial Tool creation with a narrow PostgreSQL transaction | Complete | COMMERCE-036 |
| [COMMERCE-038](COMMERCE-038-expose-atomic-tool-creation-boundary.md) | Expose atomic initial Tool creation through the Studio boundary | Complete | COMMERCE-037 |
| [COMMERCE-039](COMMERCE-039-keep-new-tool-authoring-local-until-create.md) | Keep new Tool authoring local until final creation | Complete | COMMERCE-021, COMMERCE-022, COMMERCE-038 |

Phase 3 is Commerce-owned. Shared remains unchanged at exact `0.14.2`; no Phase 3 Shared publication is required.

```text
COMMERCE-016 is architect-accepted Complete and the simplification implementation is Complete. The developer is intentionally holding terminal `ARCH-021-SYSTEM-TEST-001` until the implementation phases are finished; terminal system testing does not gate implementation.

Current Phase 3 coordination frontier:

```text
No Ready Phase 3 implementation task remains. Developer manual validation may now proceed before deferred terminal system testing and any bounded follow-up tasks discovered during that validation.
```

COMMERCE-019, COMMERCE-020, COMMERCE-021, COMMERCE-022, COMMERCE-023, COMMERCE-024, COMMERCE-036, COMMERCE-037, COMMERCE-038 and COMMERCE-039 are architect-accepted Complete.
```



### COMMERCE-039 Attempt 6 accepted — 2026-09-26

COMMERCE-039 is **Complete / Accepted, Attempt 6**. New Tool authoring remains browser-local through Request/Response/Test/Agent contract/Review and persists only at final Create through the atomic COMMERCE-038 boundary. The accepted packet passed External UI 16/16, common authoring 85/85 and focused UI 60/60 with zero skips; focused ESLint, required source audits and diff checks passed with no Attempt 6 changed-file type diagnostics. The developer will now manually validate the completed Phase 3 flow; defects discovered there are follow-up tasks rather than unfinished COMMERCE-039 work unless they invalidate the core local-only creation contract.

## Manual-validation follow-up — External HTTP Request tab

Developer manual review of the completed COMMERCE-039 flow identified bounded Request-tab authoring defects. These follow-up tasks correct the Request contract and UI as one independent manual-validation workstream. They do not reopen COMMERCE-039 and they do not introduce Phase 2 tab gating.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-040](COMMERCE-040-add-javascript-request-bindings.md) | Add explicit Agent-input/Literal bindings to JavaScript HTTP request construction | Complete | COMMERCE-016, COMMERCE-017, COMMERCE-023, COMMERCE-039 |
| [COMMERCE-041](COMMERCE-041-make-external-request-tab-validating-and-previewable.md) | Make Request the validating/exact-preview checkpoint and remove Manage connections | Complete | COMMERCE-040 |
| [COMMERCE-042](COMMERCE-042-complete-javascript-request-authoring-ui.md) | Complete JavaScript bindings, resizable editor and mode-draft preservation | Complete | COMMERCE-041 |

Current manual-validation follow-up frontier:

```text
None — COMMERCE-040..042 are architect-accepted Complete.
```

The Request-tab follow-up remains zero-provider-I/O. Request validation/preview answers what request will be constructed; the later Test-tab review will determine the separate live-provider test behaviour.

## Manual-validation follow-up — External HTTP Response tab

Response-tab manual review identified a separate bounded workstream. It is independent of COMMERCE-040..042 and may execute in parallel because it consumes only already-Complete Phase 3 capabilities plus its own response-task chain.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-043](COMMERCE-043-derive-visual-response-result-contract.md) | Derive Visual result schemas from projection authoring instead of separately maintained shape JSON | Complete | COMMERCE-016, COMMERCE-021, COMMERCE-039 |
| [COMMERCE-044](COMMERCE-044-validate-external-http-response-authoring.md) | Add Response-only authoritative Direct/Visual/JavaScript validation with Response-local diagnostics | Complete | COMMERCE-043, COMMERCE-019, COMMERCE-023 |
| [COMMERCE-045](COMMERCE-045-complete-external-http-response-tab-authoring.md) | Complete Response-tab Source-path, JavaScript panel, derived-contract and per-mode local-draft UX | Complete | COMMERCE-043, COMMERCE-044, COMMERCE-006, COMMERCE-039 |
| [COMMERCE-048](COMMERCE-048-support-nested-visual-response-results.md) | Add bounded recursive Visual result trees with Commerce-owned result-schema validation | Complete | COMMERCE-045 |
| [COMMERCE-049](COMMERCE-049-support-primitive-scalar-arrays-in-visual-results.md) | Add an explicit Visual list-of-scalar-values node for results such as `{tags:["red","blue"]}` | Complete | COMMERCE-048 |
| [COMMERCE-050](COMMERCE-050-make-response-validation-diagnostics-actionable.md) | Replace raw Response validation parser errors with field-specific corrective diagnostics | Complete | COMMERCE-049 |

Current Response-tab manual-validation frontier:

```text
No implementation task currently Ready in this Response chain.
```

The zero-provider-I/O Response authoring chain through COMMERCE-050 is architect-accepted Complete. Invalid local Visual state is diagnosed locally, canonical candidates still use authoritative server validation, configuration issues are field/control-specific, and action-level validation-system failures no longer masquerade as Response-field errors. Direct/JavaScript sample-derived schema generation and real provider execution remain deferred to later Test-tab review. All authoring tabs remain freely navigable.

## Manual-validation follow-up — JavaScript Response helper runtime

JavaScript Response authoring now has one independent runtime-helper follow-up. It does not change provider execution or the Request JavaScript contract. The helper is a versioned Commerce-owned QuickJS guest API and is bundled at build time; authored Tool source still has no npm/module loader or host callbacks.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-059](COMMERCE-059-add-versioned-quickjs-text-helper-api.md) | Add `quickjs-sync.v2` Response helpers with immutable `moda.text.stripHtml(value)` backed by a packaged `string-strip-html` bundle | Ready | COMMERCE-045, COMMERCE-046, COMMERCE-047 |

Current JavaScript Response helper frontier:

```text
ARCH-021-COMMERCE-059
```

COMMERCE-059 is independent of the live-Test and Agent-contract follow-up workstreams and may execute in parallel under the normal task/worktree protocol. Request JavaScript remains `quickjs-sync.v1`. Existing Response `quickjs-sync.v1` definitions remain valid; new Response JavaScript authoring defaults to `quickjs-sync.v2`.

## Manual-validation follow-up — External HTTP live response generation and Test

The live work now has two independent branches sharing the accepted secure provider-observation primitive. Automatic Response generation remains separate from Test. Test consumes the already-implemented Request/Response contracts directly and has no task dependency on the earlier Request/Response UI chains.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-051](COMMERCE-051-add-live-external-http-authoring-observation.md) | Add bounded ADMIN-authorized live provider observation for the current Request candidate | Complete | COMMERCE-041, COMMERCE-047 |
| [COMMERCE-052](COMMERCE-052-infer-visual-response-tree-from-observed-json.md) | Infer the accepted recursive Visual tree from observed JSON using C049 `LIST` / `SCALAR_LIST` terminology | Complete | COMMERCE-049 |
| [COMMERCE-053](COMMERCE-053-add-automatic-response-generation.md) | Add authoring-only Automatic generation that hands generated proposals to existing Visual rules | Complete | COMMERCE-042, COMMERCE-050, COMMERCE-051, COMMERCE-052 |
| [COMMERCE-054](COMMERCE-054-execute-non-durable-external-http-candidate-live.md) | Backend: execute the current non-durable Request + Response candidate live with zero persistence | Complete | COMMERCE-051 |
| [COMMERCE-055](COMMERCE-055-build-external-http-live-test-tab-ui.md) | Frontend: build the decomposed live Test-tab UI over COMMERCE-054 | Ready | COMMERCE-054 |

Current live-authoring frontier:

```text
ARCH-021-COMMERCE-055
```

Dependency graph:

```text
Automatic:
COMMERCE-042 + COMMERCE-050 + COMMERCE-051 + COMMERCE-052
                                      |
                                      v
                                 COMMERCE-053

Live Test:
COMMERCE-051 -> COMMERCE-054 -> COMMERCE-055
```

Canonical Visual terminology remains:

```text
SCALAR       -> Scalar
OBJECT       -> Object
LIST         -> List of objects
SCALAR_LIST  -> List of values
```

The live Test branch is explicitly pre-creation. It tests the exact current in-memory Request + Response candidate, performs a real provider call and canonical response/result validation, but creates no Tool, ToolRevision, audit, publication receipt or publication proof. It requires no saved revision identifier. Synthetic/sample-response fixtures are not a Test-tab product mode.

COMMERCE-055 must be composed from bounded React responsibilities rather than one large Test component: argument authoring, Run action/state, execution-stage presentation, safe Request summary, bounded provider response, processed result and stage-specific failure presentation remain separable concerns.

## Manual-validation correction — provider diagnostics and Automatic failure state

Manual Automatic testing found that provider decode failures lose actionable response evidence and that the previous canonical Response-processing JSON remains visible while a later Automatic attempt is failing. These are bounded corrections to the accepted C051/C053 branch; they do not introduce another response-processing mode or clear existing authored Visual rules.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-057](COMMERCE-057-preserve-live-provider-response-diagnostics.md) | Preserve bounded provider status/media-type/decode-reason/body-preview evidence for live authoring decode failures | Complete | COMMERCE-051 |
| [COMMERCE-058](COMMERCE-058-make-automatic-failures-current-and-actionable.md) | Show only current Automatic failure evidence, hide stale underlying processing disclosure and preserve existing Response authoring | Complete | COMMERCE-053, COMMERCE-057 |

Correction frontier:

```text
COMMERCE-051 -> COMMERCE-057 -> COMMERCE-058
                                  ^
                                  |
                             COMMERCE-053
```

COMMERCE-057/058 remain independent of COMMERCE-055 and COMMERCE-056 and do not change either task. Any Test-specific consumption of the richer diagnostic is assessed after the current COMMERCE-055 attempt returns for review rather than by moving its goalposts.

### COMMERCE-057 Attempt 1 accepted — 2026-09-27

COMMERCE-057 is **Complete / Accepted, Attempt 1**. The shared External HTTP transport now preserves deterministic provider decode/body failure reasons for the live-authoring path, retains provider status/media-type evidence, and emits only a credential-redacted textual preview capped at 4096 UTF-8 bytes. Production execution continues to use the same transport without authoring diagnostics and retains its existing non-2xx/invalid-response semantics. The submitted focused packet passed 64/64 tests across authoring observation, Server Action, production executor and COMMERCE-054 live-Test coverage.

Both dependencies of COMMERCE-058 became Complete, allowing its correction work to execute independently of COMMERCE-055 and COMMERCE-056.

### COMMERCE-058 Attempt 2 accepted — 2026-09-27

COMMERCE-058 is **Complete / Accepted, Attempt 2**. The accepted Automatic UI now presents only current provider/decode evidence, hides stale canonical Response disclosures while Automatic is active, renders the bounded provider preview as escaped text, invalidates transient state when generation context changes and preserves the existing authored Response definition after failed regeneration. Successful Automatic generation continues to install the inferred Visual definition and switch to Visual rules. Attempt 2 was task-record reconciliation only: all ten Work Items are now durably checked and the implementation/test files remain byte-for-byte unchanged from the already-reviewed Attempt 1 snapshot. The accepted focused evidence remains 92/92 tests plus passing targeted ESLint, clean changed-file TypeScript diagnostics and `git diff --check`. COMMERCE-058 enables no additional task; COMMERCE-055 and COMMERCE-056 remain independent.

## Manual-validation follow-up — Agent contract tab

The Agent contract form is already extracted into `AgentContractTab`; the follow-up is validation/clarity rather than another component refactor.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-056](COMMERCE-056-validate-agent-contract-authoring.md) | Validate the Agent-facing contract in-tab, retain invalid local edits and clarify labels/help text | Complete | COMMERCE-016, COMMERCE-039, COMMERCE-043 |

Agent-contract follow-up status:

```text
ARCH-021-COMMERCE-056 — Complete
```

COMMERCE-056 is independent of COMMERCE-055. It validates Definition version, Agent description, Agent input schema and Agent response template against canonical rules without Request/Test completion, provider I/O, durable writes or tab gating. Validation operates on local authoring state and does not save a persisted DRAFT.


## Manual-validation follow-up — Shopify Admin result contracts and Result Template

Architecture review of the current Shopify/custom Tool flow establishes one source-neutral post-processing boundary:

```text
Shopify Admin GraphQL                 External HTTP
        |                                  |
        v                                  v
compiler-derived resultSchema       existing Response resultSchema
        |                                  |
        +---------------+------------------+
                        v
               ToolResultContract
                        |
                 Result Template
```

The work is decomposed so backend/compiler tasks and React/UI tasks remain independently reviewable. General tab traversal/gating is explicitly deferred. The only navigation coordination included here is the bounded Explore Shopify round trip required to return generated Admin GraphQL to the exact originating Tool authoring session.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-060](COMMERCE-060-execute-shopify-admin-graphql-tools.md) | Backend: execute canonical Shopify Admin GraphQL Tool definitions | Complete | COMMERCE-018 |
| [COMMERCE-061](COMMERCE-061-establish-admin-schema-exploration-domain.md) | Backend/domain: expose Admin schema exploration and bounded query-building primitives | Complete | COMMERCE-018 |
| [COMMERCE-062](COMMERCE-062-derive-shopify-admin-result-contract.md) | Backend/compiler: derive canonical Admin resultSchema and nullable normalization semantics | Complete | COMMERCE-018 |
| [COMMERCE-063](COMMERCE-063-compile-tool-result-contract.md) | Backend: compile source-neutral ToolResultContract and validate Result Templates | Complete | COMMERCE-043 |
| [COMMERCE-064](COMMERCE-064-rebuild-explore-shopify-admin-authoring.md) | UI: rebuild Explore Shopify on Admin API with sessionStorage authoring handoff | Ready | COMMERCE-039, COMMERCE-061 |
| [COMMERCE-065](COMMERCE-065-split-shopify-request-response-authoring.md) | UI: split Shopify Request invocation from Response result-contract authoring | Pending | COMMERCE-062, COMMERCE-064 |
| [COMMERCE-066](COMMERCE-066-build-result-template-authoring-ui.md) | UI: build reusable schema-backed Result Template authoring component | Complete | COMMERCE-063 |
| [COMMERCE-067](COMMERCE-067-separate-agent-and-result-template-validation.md) | Backend: separate Agent call-side and Result Template validation ownership | Complete | COMMERCE-063 |
| [COMMERCE-068](COMMERCE-068-integrate-result-template-tool-authoring.md) | UI: integrate Result Template tab and rebalance Agent Contract/Review | Pending | COMMERCE-065, COMMERCE-066, COMMERCE-067 |
| [COMMERCE-069](COMMERCE-069-remove-storefront-tool-architecture.md) | Backend cleanup: remove obsolete Storefront Tool execution/discovery architecture | Pending | COMMERCE-060, COMMERCE-064 |
| [COMMERCE-070](COMMERCE-070-enforce-shopify-admin-result-contract-runtime.md) | Backend integration: enforce compiler-derived Admin result contract at runtime | Ready | COMMERCE-060, COMMERCE-062 |

Initial executable frontier for this workstream:

```text
COMMERCE-060    COMMERCE-061    COMMERCE-062    COMMERCE-063
     |               |               |               |
     |               v               |               +-------> COMMERCE-066
     |          COMMERCE-064          |               +-------> COMMERCE-067
     |               |               |
     |               +-------> COMMERCE-065
     |                               |
     +----------+--------------------+-------> COMMERCE-070
     |          |
     |          +---- COMMERCE-064 ----------> COMMERCE-069
     |
     +----------------------------------------> COMMERCE-069

COMMERCE-065 + COMMERCE-066 + COMMERCE-067 ---> COMMERCE-068
```

COMMERCE-063 Attempt 1 is architect-accepted Complete. COMMERCE-066 Attempt 1 is now architect-accepted Complete; COMMERCE-067 remains Ready. COMMERCE-068 remains dependency-gated by COMMERCE-065 + COMMERCE-066 + COMMERCE-067, with the COMMERCE-066 dependency now satisfied.

Key invariants:

- new Shopify Tools use `SHOPIFY_ADMIN_GRAPHQL`; Explore Shopify is an Admin API explorer/query builder;
- manual Admin GraphQL remains first-class and the GraphQL document is authoritative after Explore returns;
- unfinished Tool authoring remains browser-local; the Explore round trip uses `StudioComposerContext + sessionStorage`, never a database draft created solely for navigation;
- Shopify resultSchema becomes a compiler-produced immutable Tool-definition artifact, while External HTTP keeps its already-accepted Response resultSchema behavior;
- Admin result-schema derivation is independent of live provider execution; COMMERCE-070 is the narrow runtime integration point;
- `ToolResultContract` is derived, not separately persisted;
- `responseTemplate` remains the runtime representation but moves to a dedicated Result Template authoring surface;
- Agent Contract becomes the call-side model contract only;
- Storefront Tool compatibility is removed only after Admin runtime and Admin Explore authoring replacements are in place;
- global tab traversal, gating, Next/Back coordination and cross-tab checkpoint orchestration remain out of scope.


### COMMERCE-062 Attempt 2 accepted — 2026-09-27

COMMERCE-062 is **Complete / Accepted, Attempt 2**. Compatible repeated Admin GraphQL response keys now merge recursively after the existing semantic-validation boundary, so complementary repeated aliased selections derive the same canonical Commerce result schema as the equivalent single merged selection. The real pinned `QueryRoot.nodes(ids: [...])` path now carries a truthful literal-ID bound far enough to reject its actual nullable list elements with `UNREPRESENTABLE_NULLABLE_LIST`. Submitted validation passed the required 42-test regression packet, targeted ESLint and diff checks; repository-wide TypeScript remains red only on unrelated files, with zero diagnostics in the two Attempt 2 changed files. COMMERCE-060 is already Complete, so COMMERCE-070 is promoted to **Ready**. COMMERCE-065 remains Pending until COMMERCE-064 is Complete.

### COMMERCE-062 Attempt 1 changes requested — 2026-09-27

The pure Admin result-contract derivation, scalar/nullability mapping, query-proven
list bounds, canonicalization, normalization helper and authenticated non-mutating
action are accepted in substance. COMMERCE-062 remains **Ready** for Attempt 2
because valid GraphQL repeated response-key selections with complementary child
selections are currently rejected instead of being merged according to GraphQL
field-merging semantics.

Attempt 2 must also add direct evidence for the already-implemented
`UNREPRESENTABLE_NULLABLE_LIST` path using the real pinned Admin schema.
COMMERCE-065 and COMMERCE-070 remain Pending on their other dependencies as well.
### COMMERCE-067 Attempt 1 accepted — 2026-09-27

COMMERCE-067 is **Complete / Accepted, Attempt 1**. Canonical Agent validation now owns only definition version, description and input schema; Result Template/output compatibility remains exclusively delegated to COMMERCE-063. The pre-C068 compatibility helper/action is explicitly deprecated and composes the two canonical validators without provider or persistence side effects. Final publication remains strict for both Agent and Result Template contracts. Submitted validation passed the 132-test contract/UI packet, targeted lint, changed-file diagnostics and diff checks.

COMMERCE-068 remains Pending because COMMERCE-065 and COMMERCE-066 are not both Complete in this snapshot.

### COMMERCE-061 Attempt 2 accepted — 2026-09-27

COMMERCE-061 is **Complete / Accepted, Attempt 2**. Admin exploration/query authoring remains pinned to the retained Admin `2026-07` artifact, and generated/manual Request authoring now shares the canonical Admin document/mapping compatibility path independently of Response-owned result state. Attempt 2 rejects incompatible Tool-input/literal bindings, composes multiple loaded pages for one parent type, and preserves representable manual queries even when `resultPath`/`resultSchema` are stale while continuing to reject invalid Admin pagination/query rules. Submitted validation passed the 56-test focused packet and 22-test canonical Admin compiler script, plus targeted lint, changed-file diagnostics and diff checks. COMMERCE-039 is already Complete, so COMMERCE-064 is promoted to **Ready**.


### COMMERCE-053 Attempt 2 accepted — 2026-09-27

COMMERCE-053 is **Complete / Accepted, Attempt 2**. Automatic remains transient browser-local authoring state over the canonical `DIRECT | VISUAL | JAVASCRIPT` response union, shares the single Sample Tool arguments state, uses COMMERCE-051 observation and COMMERCE-052 inference, and hands accepted candidates into the existing Visual editor through `deriveVisualTreeContract(...)`. Attempt 2 corrected abandonment of Automatic back to the unchanged persisted mode so it no longer dirties/mutates the Tool or invalidates successful Response validation, while intentional mode changes still do. Regression coverage now includes a sole root `LIST` candidate with `resultPath: ""` and explicit proof that Automatic generation creates no live-test receipt and publication remains gated by `LIVE_TEST_REQUIRED`. Submitted validation passed 69/69 External HTTP UI and 13/13 Tool-authoring tests; the common packet remains 85/86 on the pre-existing lifecycle expectation mismatch outside C053. COMMERCE-054 remains independently **Ready** because its authoritative dependency is COMMERCE-051 alone.

### COMMERCE-042 Attempt 3 accepted — 2026-09-27

COMMERCE-042 is **Complete / Accepted, Attempt 3**. The original blocked handoff
correctly stopped when QuickJS packaging was unavailable, but supplemental developer
evidence from the same implementation worktree subsequently proved the pinned
`quickjs-wasi@3.6.2` package/smoke path and the complete required five-file packet
(122/122). The common packet reproduced only the previously documented unrelated
lifecycle fixture failure (85/86). No Attempt 4 source change was required.

All COMMERCE-053 dependencies are now Complete, so COMMERCE-053 is **Ready**.

### COMMERCE-051 Attempt 1 accepted — 2026-09-27

COMMERCE-051 is **Complete / Accepted, Attempt 1**. Live External HTTP authoring now previews the exact current Declarative or JavaScript Request into the accepted safe descriptor, revalidates ADMIN/PER_SHOP scope, resolves credentials server-side and reuses the production descriptor transport/security primitive. Decodable 4xx/429/5xx responses are bounded authoring observations without changing production JavaScript gating or production non-2xx Tool semantics; credentials and provider response headers never enter the browser contract, and no Tool/Revision/Connection/Credential/audit/live-test-receipt mutation is introduced. Submitted validation passed the required executor, Request-runtime, authoring-validation/action and wiring suites plus focused security tests, lint and diff checks. Independent inspection of the submitted Commerce `tsconfig.tsbuildinfo` confirms zero diagnostics in all eight changed C051 files. With COMMERCE-042 and COMMERCE-052 also Complete, COMMERCE-053 is Ready.

### COMMERCE-050 Attempt 2 accepted — 2026-09-27

COMMERCE-050 is **Complete / Accepted, Attempt 2**. Invalid local Visual authoring
remains browser-local with field/control-specific corrective guidance, canonical
Response candidates retain authoritative zero-I/O validation, and action-level
`DATABASE_UNAVAILABLE` / `INTERNAL_ERROR` / `FORBIDDEN` / rejected-Promise failures
now render as bounded validation-system diagnostics without fabricated Response
paths or raw server messages. Submitted evidence includes 47/47 External HTTP UI and
54/54 Response-validation/Server Action tests, targeted lint/diff checks and zero
C050-owned TypeScript diagnostics. The one common-packet lifecycle fixture failure is
unchanged and outside C050's presentation scope. No downstream task is enabled.

### COMMERCE-049 Attempt 1 accepted — 2026-09-26

COMMERCE-049 is **Complete / Accepted, Attempt 1**. Visual response trees now support explicit `SCALAR_LIST` leaves for primitive arrays such as `{tags:["red","blue"]}` while preserving object-row `LIST` semantics. Item type remains owned by the Commerce result schema, runtime projection preserves source order and the accepted work/deadline bounds, Response validation/publication reuse the C048 helpers, and Studio clearly separates `List of values` from `List of objects` with browser-local branch retention. Submitted evidence totals 165 focused passing tests with lint/diff/source audits clean and no C049-owned type diagnostics. Manual review also identified a separate cross-Visual diagnostic-presentation issue: Validate response can currently show raw null-placeholder/Zod messages when the local Visual tree is invalid. COMMERCE-050 is promoted to **Ready** for that bounded UX correction.

### COMMERCE-045 Attempt 2 accepted — 2026-09-26

COMMERCE-045 is **Complete / Accepted, Attempt 2**. The final Response-tab composition now keeps Direct/Visual/JavaScript mode drafts and Visual OBJECT/LIST shape drafts independent, validates the exact active mode, invalidates prior Response-validation success on every relevant edit (including rejected local Visual edits), and renders Visual processing/derived-contract disclosures from the current local shape rather than stale canonical buffers. The accepted UI also retains invalid raw edits, uses the existing CodeMirror JavaScript response editor, derives Visual result contracts through COMMERCE-043, consumes COMMERCE-044 Response-only validation, performs no provider I/O and introduces no tab gating. Submitted validation passed 31 Response UI, 47 external validation/action, 85 common authoring, 12 New Tool and 14 CodeMirror tests plus targeted lint/diff/changed-file diagnostics. COMMERCE-048 is promoted to **Ready** for the separately scoped nested Visual result-tree extension.

### Nested Visual result follow-up — COMMERCE-048

COMMERCE-048 is **Complete / Accepted, Attempt 1**. It replaces the preproduction flat Visual root grammar with one canonical Commerce-owned recursive `kind:"VISUAL"` tree and moves Commerce result/output schema parsing and validation behind `CommerceResultSchemaSchema` / `compileCommerceResultSchema(...)`, while keeping genuine shared input/descriptor contracts in Shared 0.14.2. Nested OBJECT/LIST projection, relative paths, per-list filter/sort/limit, bounded work, recursive authoring/reconstruction, publication and fixture/live output validation are now composed through the accepted Commerce helpers. Submitted evidence includes a 182-test focused C048 batch and 33/33 External UI tests with zero task-owned type diagnostics. Primitive scalar arrays remain deliberately outside C048 and are now the Ready COMMERCE-049 follow-up.

### COMMERCE-043 Attempt 1 accepted — 2026-09-26

COMMERCE-043 is **Complete / Accepted, Attempt 1**. Visual OBJECT/LIST projected fields now carry bounded scalar result types, `omitIfMissing` deterministically controls requiredness, and one Commerce-owned helper derives the canonical OBJECT or `{ items: [...] }` LIST `resultSchema`. Compatible persisted Visual definitions reconstruct editable field types without new durable metadata; incompatible projection/schema pairs fail explicitly. Publication compatibility reuses the same rule, Visual mode no longer requires independently editable `Response shape JSON`, and Direct/JavaScript schema behavior remains unchanged. The submitted packet passed 41 focused Visual/UI/publication tests, 85 common Tool-authoring tests and 45 External authoring-validation tests, with targeted ESLint/diff checks clean and no task-owned type diagnostics. COMMERCE-044 is promoted to **Ready**; COMMERCE-045 remains Pending.

### COMMERCE-044 Attempt 1 accepted — 2026-09-26

COMMERCE-044 is **Complete / Accepted, Attempt 1**. Response now has a named ADMIN-authorized, non-mutating validator for Direct, Visual OBJECT/LIST and JavaScript authoring. Direct/Visual JSON and Source-path rules, bounded result schemas, Visual projection/filter/sort/limit rules and COMMERCE-043 derived-schema compatibility are checked at deterministic Response-local paths; compatible persisted LIST bounds remain accepted. JavaScript validation compiles `transform(response)` without executing it, and integration coverage proves the Response-only path performs no connection, credential, DNS, transport or Tool/ToolRevision write operations. The submitted focused validation/Server Action packet passed 52 tests with targeted ESLint and diff checks clean and no changed-file TypeScript diagnostics. COMMERCE-045 is promoted to **Ready** for final Response-tab UX wiring.

## Manual-validation follow-up — QuickJS runtime adapter

Manual Request-tab validation also exposed a lower-level runtime-loader defect independent of the Request/Response UI workstreams. The accepted sandbox contract remains valid, but the current `quickjs-emscripten` adapter fails when the real Next.js Server Action initializes the engine (`RUNTIME_UNAVAILABLE`) even though standalone runtime/package proofs pass.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-046](COMMERCE-046-replace-quickjs-emscripten-with-quickjs-ng-wasi.md) | Replace the Emscripten QuickJS adapter with one packaged QuickJS-NG/WASI runtime and shared structured runtime logging | Complete | COMMERCE-017, COMMERCE-040, COMMERCE-041 |
| [COMMERCE-047](COMMERCE-047-surface-bounded-javascript-compiler-diagnostics.md) | Preserve bounded QuickJS-NG compiler causes through Request validation and the Request UI | Complete | COMMERCE-046 |

Current runtime-adapter state:

```text
COMMERCE-046   Complete
      |
      v
COMMERCE-047   Complete
```

COMMERCE-046 is independent of COMMERCE-042 and COMMERCE-043..045 and may execute in parallel. It changes only the sandbox engine adapter/package/logging implementation; `quickjs-sync.v1`, Tool-definition shapes, Request/Response authoring semantics and the production JavaScript executor gate remain unchanged.

COMMERCE-046 and COMMERCE-047 are architect-accepted Complete. The bounded QuickJS runtime-adapter/compiler-diagnostic follow-up chain has no remaining implementation task.



### COMMERCE-047 Attempt 1 accepted — 2026-09-26

COMMERCE-047 is **Complete / Accepted, Attempt 1**. Bounded QuickJS-NG Request compiler causes now survive Worker -> KernelResult -> Request processor -> authoring validation -> Request UI, capped at 512 UTF-8 bytes and without source, stack, host-path, Tool-argument or provider/customer-data leakage. Operational runtime failures remain opaque and use the COMMERCE-046 shared structured logging boundary; expected guest syntax/entrypoint failures remain normal authoring validation results and do not emit error-level operational logs. The submitted packet passed packaging/smoke, 12 runtime proofs, 7 Request processor tests, 47 validation/Server Action tests, 21 External UI tests, targeted lint/source audits and diff checks with no task-owned type diagnostics. The runtime-adapter/compiler-diagnostic follow-up chain is now Complete.

### COMMERCE-046 Attempt 1 accepted — 2026-09-26

COMMERCE-046 is **Complete / Accepted, Attempt 1**. The Emscripten adapter is replaced by the packaged `quickjs-wasi@3.6.2` / QuickJS-NG runtime while preserving `quickjs-sync.v1`, request/response behavior, worker supervision and shared structured runtime logging. Packaging/smoke/runtime/request/response/authoring validation passed, and real Next.js manual validation now reaches the guest compiler rather than returning `RUNTIME_UNAVAILABLE`. COMMERCE-047 is promoted to **Ready** for bounded compiler-message propagation.
COMMERCE-047 completed the deliberately small diagnostic-fidelity follow-up discovered during manual validation of COMMERCE-046.


### COMMERCE-041 Attempt 1 accepted — 2026-09-26

COMMERCE-041 is **Complete / Accepted, Attempt 1**. Request is now the non-network validation/preview checkpoint: invalid intermediate Request edits remain visible with diagnostics, authoritative Request validation is bounded and zero-provider-I/O, exact safe request preview lives in Request, `Manage connections` is removed, Test no longer owns Request preview, and tabs remain freely navigable. The submitted packet passed 85 common, 17 External UI, 45 validation/Server Action and 10 new-tool tests with targeted lint/diff checks clean and no task-owned diagnostics. COMMERCE-042 is promoted to **Ready**.

### COMMERCE-040 Attempt 1 accepted — 2026-09-26

COMMERCE-040 is **Complete / Accepted, Attempt 1**. JavaScript External HTTP requests now persist an explicit bounded `bindings` map; Tool argument mapping and Request preview use the same resolver; only resolved declared bindings reach QuickJS; structured Agent-input values and bounded literals remain supported; unknown/forbidden input bindings fail at deterministic paths; and production JavaScript External HTTP execution remains disabled. The submitted packet passed 61 focused tests and 85 common authoring tests, with targeted ESLint/diff checks clean and no changed-file diagnostics. COMMERCE-041 is promoted to **Ready**; COMMERCE-042 remains Pending.

## Pre-Phase-3 simplification checkpoint — 2026-09-24

The checkpoint reduces Phase-2 configuration/reconciliation complexity before further Tool authoring. It preserves model catalogue, prompt revisions, prompt-template categories, immutable published artifacts, capabilities/releases/grants, server-owned credentials and future merchant Studio authorization. Errors must remain visible and transport-level uncertainty must be reconcilable through the UI; ordinary failures must not be swallowed into a generic unknown state.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-025](COMMERCE-025-simplify-agent-configuration-services.md) | Simplify Agent Configuration services and reconciliation | Complete | DATABASE-002, COMMERCE-007, 009, 010 |
| [COMMERCE-026](COMMERCE-026-simplify-prompt-template-authoring.md) | Simplify prompt-template authoring while retaining categories | Complete | DATABASE-002, COMMERCE-008, 015 |
| [COMMERCE-027](COMMERCE-027-unify-authjs-studio-authorization.md) | Unify Auth.js authorization across PlatformAdmin and shop-scoped merchant access | Complete | DATABASE-002 |
| [COMMERCE-028](COMMERCE-028-simplify-agent-configuration-ui-and-reconciliation.md) | Simplify Agent Configuration UI and explicit reconciliation | Complete | COMMERCE-025, 026, 027, 011..014, COMMERCE-031 |
| [COMMERCE-029](COMMERCE-029-remove-production-studio-service-function-props.md) | Remove production function-valued Studio service props | Complete | COMMERCE-028, COMMERCE-001..006 |
| [COMMERCE-030](COMMERCE-030-simplify-private-mcp-authentication.md) | Remove application-layer auth from private MCP; keep DB authorization | Complete | ARCH-020-COMMERCE-024 |
| [COMMERCE-031](COMMERCE-031-complete-retained-agent-configuration-read-contract.md) | Complete retained Agent Configuration read contract | Complete | COMMERCE-025 |
| [COMMERCE-032](COMMERCE-032-normalize-storefront-schema-graph.md) | Normalize real pinned Storefront introspection into one truthful schema graph contract | Complete | COMMERCE-029 |
| [COMMERCE-033](COMMERCE-033-build-recursive-storefront-schema-browser.md) | Build recursive schema-driven Storefront browser and selection tree | Complete | COMMERCE-032 |
| [COMMERCE-034](COMMERCE-034-generate-storefront-graphql-from-schema-selection.md) | Generate/merge Storefront GraphQL from dynamic schema selections | Complete | COMMERCE-033 |
| [COMMERCE-035](COMMERCE-035-render-shopify-documentation-readably.md) | Normalize Shopify docs into readable safe excerpts and structured article blocks | Complete | COMMERCE-034 |


Current checkpoint implementation frontier: none.

COMMERCE-032, COMMERCE-033, COMMERCE-034 and COMMERCE-035 are architect-accepted Complete. All terminal checkpoint implementation dependencies are Complete, so `ARCH-021-SYSTEM-TEST-001` remains Ready. The developer is intentionally holding terminal system tests until the implementation phases are finished and is using manual validation meanwhile; this Ready system-test task is not an implementation dependency and does not pause Phase 3.

### COMMERCE-021 Attempt 6 accepted — 2026-09-26

COMMERCE-021 is **Complete / Accepted, Attempt 6**. The final regression now proves that an already-visible authoritative validation success is invalidated by both Description and execution-path edits, remains absent after Save, and returns only after re-validating the current saved candidate. The External UI packet passed 16/16 and the focused four-file packet 68/68; targeted ESLint and diff checks passed, with 15 unrelated repository typecheck diagnostics and zero task-owned diagnostics. With COMMERCE-022 and COMMERCE-038 already Complete, COMMERCE-039 is promoted to **Ready**.

### COMMERCE-038 Attempt 2 accepted — 2026-09-26

COMMERCE-038 is **Complete / Accepted, Attempt 2**. The named atomic initial-Tool Server Action now calls a real mutation method, returns exact composite identity directly without publication snapshot reconstruction, preserves exact audit-only reconciliation, and has direct success/`CONFLICT` Server Action coverage. The common packet passed 84 tests, the focused packet passed 31, changed-file ESLint/diff checks passed, and no task-owned TypeScript diagnostics remain. COMMERCE-039 remains Pending because COMMERCE-021 is still in Review; COMMERCE-021 is its sole remaining dependency gate.

### COMMERCE-037 Attempt 2 accepted — 2026-09-26

COMMERCE-037 is **Complete / Accepted, Attempt 2**. The dedicated initial-Tool persistence path now uses one narrow Prisma transaction with operation-scoped advisory locking, exact audit replay lookup and direct Tool/revision/audit inserts. Attempt 2 proves a distinct narrow create completes while the legacy global publication lock is held, adds changed-actor replay rejection, and limits `P2002 -> CONFLICT` translation to the `CommerceTool.name` unique target. The common packet passed 81/81; the focused PostgreSQL correction test, changed-file ESLint and diff checks passed; retained backend/typecheck failures match the documented baseline. COMMERCE-038 is promoted to **Ready**.

### COMMERCE-036 Attempt 2 accepted — 2026-09-26

COMMERCE-036 is **Complete / Accepted, Attempt 2**. The accepted implementation creates the Tool and revision-1 `DRAFT` under one `CREATE_TOOL` lifecycle operation/audit identity, returns both durable identifiers directly, preserves replay/conflict semantics and proves lifecycle rollback. Attempt 2 was report-only: the submitted snapshots differ only in the COMMERCE-036 task record, with all 8 Work Items, 11 Acceptance Criteria and 5 Validation items reconciled and Completion Report status set to `Ready for Review`. COMMERCE-037 is promoted to **Ready**.


### COMMERCE-023 Attempt 3 accepted — 2026-09-25

COMMERCE-023 is **Complete / Accepted, Attempt 3**. Preview source now obeys the
canonical 16,384 UTF-8-byte ceiling; the focused Server Action suite proves missing
mapping / invalid descriptor / missing descriptor and compiler-runtime
classifications; strict forbidden top-level DTO fields are rejected; production
authoring validation proves zero DNS, transport and credential reads; and both OBJECT
and LIST incompatible visual projections use the canonical response-processing issue
path. The focused packet passed 37/37 with zero task-owned TypeScript diagnostics.
COMMERCE-021 remains Pending because COMMERCE-020 is still Ready rather than
Complete. Phase 3 Ready frontier is now COMMERCE-020 only.

### COMMERCE-024 Attempt 2 accepted — 2026-09-25

COMMERCE-024 is **Complete / Accepted, Attempt 2**. Compiler-origin diagnostics now
use the canonical slash-delimited `/execution/...` path contract, including exact
variable-specific paths, while preserving the pinned Admin 2026-07 compiler,
server-owned schema metadata, COMMERCE-019 action envelope and zero-provider-I/O
boundary. The focused C024 packet passed 9/9 and the COMMERCE-018 compiler packet
passed 22/22 with zero task-owned TypeScript diagnostics. COMMERCE-022 remains
Pending because COMMERCE-020 is not yet Complete.

### COMMERCE-019 Attempt 3 accepted — 2026-09-25

COMMERCE-019 is **Complete / Accepted, Attempt 3**. The common validation layer now
has executable proof that real validation Server Actions perform zero provider I/O,
alongside the accepted exact UTF-8 bounds, `INVALID_INPUT` mapping, role/bypass
authorization, `LIVE_TEST_REQUIRED` lifecycle/Studio propagation, synthetic-receipt
rejection and history invariants. The common focused packet passed 77/77 with zero
skips. All dependencies of COMMERCE-023 and COMMERCE-024 are now Complete, so both
are promoted to **Ready**. COMMERCE-021/022 remain Pending.

### COMMERCE-017 Attempt 3 accepted — 2026-09-25

COMMERCE-017 is **Complete / Accepted, Attempt 3**. The request-focused QuickJS suite
now explicitly proves non-finite, custom-prototype, accessor and oversized output
rejection plus the full minimum host/global unavailability set, while preserving the
existing response/runtime/package proofs. Runtime source was unchanged from Attempt
2. COMMERCE-023 remains Pending because COMMERCE-019 is still Ready rather than
Complete.

### Phase 3 resumed on simplified architecture — 2026-09-25

- COMMERCE-017 is architect-accepted Complete at Attempt 3; COMMERCE-018 is architect-accepted Complete at Attempt 4.
- COMMERCE-019 now consumes the COMMERCE-027 hierarchical Auth.js authorization boundary and exposes explicit validation/action failures with no generic unknown result.
- COMMERCE-020 now consumes the COMMERCE-029 named Server Action/serializable DTO boundary and owns Tool mutation UNCONFIRMED reconciliation through audit lookup without replay.
- COMMERCE-021..024 are revised to use those boundaries; validation/read errors remain explicit, and global Tool publication remains SUPER_ADMIN-only.
- Terminal SYSTEM-TEST-001 remains Ready by developer choice and is intentionally deferred; it is not added as a Phase 3 dependency.

### Documentation readability correction task materialised — 2026-09-24

Manual Explore validation also found that documentation search chunks were rendered
nearly verbatim and opened Shopify pages were flattened into one paragraph. The
cause is contractual: search exposes raw-ish MCP `content`, while direct HTML
extraction removes all block structure and globally collapses whitespace.

COMMERCE-035 is dependency-gated after COMMERCE-034 to avoid conflicting edits in
the Explore UI. It will normalize search content to safe plain-text excerpts and
verified Shopify HTML to bounded structured blocks, then render those blocks
semantically without `dangerouslySetInnerHTML`.

### Storefront dynamic-schema correction tasks materialised — 2026-09-24

Manual validation found that the real `browseSchema()` result is derived from the
pinned `@shopify/dev-mcp` introspection artifact but does not contain the synthetic
`field.path` required by the old flat UI contract. Because every production field
therefore had `path === undefined`, one checkbox selection could appear to select
the entire list.

The correction deliberately does not patch that symptom with `path ?? name`.
Instead:

```text
COMMERCE-032 -> real pinned introspection -> truthful normalized type graph
COMMERCE-033 -> recursive graph navigation -> nested selection tree
COMMERCE-034 -> selection tree + real args -> GraphQL AST -> existing compiler
```

Normal Studio browsing remains local to the pinned real introspection artifact; no
per-click Shopify network introspection is introduced. SYSTEM-TEST-001 returns to
Pending until this correction chain is Complete.

### COMMERCE-029 Attempt 3 accepted — 2026-09-24

COMMERCE-029 is architect-accepted **Complete**. Production Studio and Connections
React boundaries no longer expose test-only service/port/render-function injection
props. Tests configure fixture state behind the same named Server Action modules used
by production. The focused packet passed 9 files / 71 tests and the required source
audits passed with no production matches. Repository-wide typecheck/build remain
blocked only by the documented unrelated Commerce baseline.

All simplification checkpoint implementation dependencies are now Complete, so
`ARCH-021-SYSTEM-TEST-001` is Ready.

### COMMERCE-029 Attempt 2 changes requested — 2026-09-24

Attempt 2 fixes the original `StudioServices` prop, error visibility/logging, and stale
production-composition tests. COMMERCE-029 remains **Ready** for Attempt 3 because
production Client Component APIs still expose alternate function-valued seams used only
by tests (`StudioWorkspace.externalHttpPort`, `StudioWorkspace.renderCodePanel`, and
`ConnectionsPage.port`). The developer-confirmed invariant is now explicit: test helpers
may exist, but tests must mock the same named Server Action/module boundaries production
uses instead of adding test-only production React props. SYSTEM-TEST-001 remains Pending.

### COMMERCE-029 Attempt 1 changes requested — 2026-09-24

The production Server/Client function-prop removal is retained, but COMMERCE-029
returns to **Ready** for Attempt 2. `StudioWorkspace` must no longer accept
`StudioServices` even under a renamed fixture prop; task-owned client/server
exception paths must stop swallowing arbitrary failures and use the approved
shared structured logger on the server while rendering a bounded failure class
on the client; and stale production-composition tests must be migrated to the
new serializable DTO + named Server Action architecture. SYSTEM-TEST-001 remains
Pending.

### COMMERCE-028 Attempt 3 accepted — 2026-09-24

COMMERCE-028 is **Complete / Accepted, Attempt 3**. The selected-shop UI now consumes
the COMMERCE-031 retained configuration DTO as the canonical CAS source, preserves
independent model/prompt versions across set/clear/set, rediscoveries exact-shop
durable prompt lineage while inherited, and completes the required not-committed,
reconciliation-rejection and Studio navigation-lock proofs. The exact six-file
focused packet passed 18/18 with zero skips. All COMMERCE-029 dependencies are now
Complete, so COMMERCE-029 is promoted to **Ready**. Current independent checkpoint
frontier: COMMERCE-029 plus GATEWAY-001.

### COMMERCE-031 Attempt 2 accepted — 2026-09-24

COMMERCE-031 is **Complete / Accepted, Attempt 2**. The exact shared retained-row
model+prompt CAS regression executes and passes, all acceptance criteria are
reconciled, and the Attempt 2 launcher/worktree packet is recorded. Runtime source
remained unchanged from Attempt 1. COMMERCE-028 is returned to **Ready** at Attempt 2
for its already-defined Attempt 3 UI/reconciliation correction contract; COMMERCE-029
remains Pending. Current independent checkpoint frontier: COMMERCE-028 plus
GATEWAY-001.

### COMMERCE-031 Attempt 1 validation/evidence correction — 2026-09-24

COMMERCE-031's runtime read contract is retained, but the task returns to **Ready** at Attempt 1 because its submitted two-test packet does not execute the mandatory single-retained-row model + prompt CAS sequence and its Completion Report omits the launcher-prepared execution packet. Attempt 2 is test/report focused; no runtime redesign is requested. COMMERCE-028 remains **Blocked, Attempt 2** and COMMERCE-029 remains Pending.

### Checkpoint frontier reconciled after BACKGROUND-001 acceptance — 2026-09-24

All COMMERCE-028 dependencies are Complete and its authoritative task YAML is `ready`; the index now reflects that state. In parallel, BACKGROUND-001 acceptance makes GATEWAY-001 Ready. The current independent checkpoint frontier is therefore COMMERCE-028 plus GATEWAY-001.

### COMMERCE-025 Attempt 4 accepted — 2026-09-24

COMMERCE-025 is **Complete / Accepted, Attempt 4**. The reduced DATABASE-002 Agent Configuration services preserve mandatory platform model/prompt baselines, independent model/prompt CAS, nullable retained-row override clearing, real prompt-lineage identity, current-template provenance, immutable audit receipts, explicit reconciliation and shared structured database-unavailable logging. Architect-completed live validation passed 30/30 focused unit tests with zero skips, 3/3 model PostgreSQL concurrency cases and 5/5 prompt PostgreSQL concurrency cases using separate freshly migrated disposable databases to preserve immutable-audit semantics. Targeted ESLint is zero-error after the review-time fixture typing correction. COMMERCE-028 remains Pending only because COMMERCE-027 is not yet Complete; the active checkpoint frontier is COMMERCE-027 plus BACKGROUND-001.

### COMMERCE-025 Attempt 3 architect review — 2026-09-24

COMMERCE-025 remains **Ready** for Attempt 4. The reduced service implementation is close, but acceptance is blocked by a regressed mandatory platform-baseline rule, incomplete prompt unit coverage, a syntactically invalid prompt PostgreSQL suite, and missing required npm-based unit/PostgreSQL execution. COMMERCE-028 remains Pending.
ARCH-021-COMMERCE-025
ARCH-021-BACKGROUND-001
```

DATABASE-002, COMMERCE-026 and COMMERCE-027 are architect-accepted Complete. COMMERCE-025 remains Ready; COMMERCE-028 remains Pending until COMMERCE-025 is also Complete.

### COMMERCE-027 authorization hierarchy clarification — 2026-09-24

COMMERCE-027 Attempt 2 identity-binding and PostgreSQL corrections are retained, but the task remains **Ready** for Attempt 3 to make authorization explicitly hierarchical: `PLATFORM_SUPER_ADMIN > PLATFORM_ADMIN > MERCHANT_ADMIN > MERCHANT_EDITOR > MERCHANT_VIEWER`. Platform roles are global; merchant roles remain exact-shop scoped. Platform `ADMIN` therefore satisfies shop `publish`/merchant-ADMIN requirements for any shop, while platform-release activation/rollback and other explicitly global-sensitive operations remain SUPER_ADMIN-only. COMMERCE-028 remains Pending.
DATABASE-002 Attempt 2 and COMMERCE-026 Attempt 3 are architect-accepted Complete. The remaining independent Commerce checkpoint frontier is COMMERCE-025 and COMMERCE-027; COMMERCE-028 remains Pending until both are Complete.

### COMMERCE-027 Attempt 5 accepted — 2026-09-24

COMMERCE-027 is **Complete / Accepted, Attempt 5**. The final authorization model is hierarchical (`PLATFORM_SUPER_ADMIN > PLATFORM_ADMIN > MERCHANT_ADMIN > MERCHANT_EDITOR > MERCHANT_VIEWER`), platform roles are global, merchant roles are exact-shop scoped, and global merchant-access administration is SUPER_ADMIN-only. Focused authorization validation passed 62/62; the disposable PostgreSQL suite passed 3/3, including platform-ADMIN denial with no merchant/audit mutation, the SUPER_ADMIN lifecycle, and concurrent subject-binding. COMMERCE-028 remains Pending only on COMMERCE-025.

### COMMERCE-027 Attempt 4 architect review — 2026-09-24

Attempt 4 closes the hierarchy, direct-entrypoint and PostgreSQL-harness corrections, but COMMERCE-027 remains **Ready** for one bounded Attempt 5 security correction: the global merchant-access CLI must require an active `PLATFORM_SUPER_ADMIN`, not merely any active `PlatformAdmin`. Add a PostgreSQL denial proof for platform `ADMIN`; preserve the accepted SUPER_ADMIN lifecycle, subject-binding race proof and Attempt 4 test-safety harness. COMMERCE-028 remains Pending.


### COMMERCE-026 Attempt 3 accepted — 2026-09-24

COMMERCE-026 is **Complete / Accepted, Attempt 3**. Structured Prisma-code
classification replaces message parsing for `P2002`; CAS/P2002 losers reconcile once
after rollback through `CommerceAuditEvent.operationId`; reconciliation lookup
failure is explicit rather than swallowed; and translated infrastructure/unexpected
failures use the approved shared structured logger with raw `Error` objects and
bounded operation IDs. The isolated PostgreSQL proof executed and passed all three
required concurrency regressions. COMMERCE-028 remains Pending on COMMERCE-025 and
COMMERCE-027.

### COMMERCE-026 Attempt 1 changes requested — 2026-09-24

COMMERCE-026 remains **Ready** for Attempt 2. The revision-lifecycle removal is retained, but the correction must use `CommerceAuditEvent.operationId` rather than overloading the audit primary key, adopt the checkpoint's explicit no-replay error contract, make template enable/disable persist through CAS, remove the remaining task-owned `sourceTemplateRevisionId` UI references, update stale replay-oriented regressions, and restore the mandatory launcher/worktree evidence in the Completion Report. COMMERCE-028 remains Pending.
### COMMERCE-026 Attempt 2 changes requested — 2026-09-24

COMMERCE-026 remains **Ready** for Attempt 3. Attempt 2 closes the direct-content, canonical `operationId`, explicit-error, enabled-state, template-provenance and workflow-evidence corrections, but the PostgreSQL concurrency regression still contains the removed `kind: conflict` contract and was skipped. Attempt 3 must reconcile concurrent same-operation unique/CAS losers through the canonical audit receipt, must not silently swallow mutation or reconciliation exceptions, and must log translated infrastructure/unexpected failures through `@modainteract/moda-interact-shared/logging` by passing the raw `Error` field. All three isolated PostgreSQL concurrency regressions must execute and pass. COMMERCE-028 remains Pending.

### COMMERCE-030 Attempt 2 accepted — 2026-09-24

COMMERCE-030 is **Complete**. Attempt 2 removes secret-bearing configuration logging, preserves typed MCP authorization-domain failures through the production adapter, keeps unexpected storage/runtime failures fail-closed as `UNAVAILABLE`, reconciles Commerce-owned RSA/signed-context operational guidance, and records the required launcher/worktree/commit/push evidence. The private MCP remains context-only over the private service link with PostgreSQL shop/turn/grant/release/tool authorization intact. `ARCH-021-BACKGROUND-001` is promoted to **Ready**; GATEWAY-001 remains Pending on BACKGROUND-001.

### COMMERCE-030 Attempt 1 architect review — 2026-09-24

The core context-only private MCP refactor is accepted in substance, but COMMERCE-030 remains **Ready** for a bounded Attempt 2: remove credential-bearing configuration logs, preserve typed authorization-domain failures through the production MCP adapter, reconcile stale RSA/signed-context operational text, and restore the standard Completion Report workflow. BACKGROUND-001 remains Pending until COMMERCE-030 is Complete.

### COMMERCE-013 Attempt 1 architect review — 2026-09-23

COMMERCE-013 is **Blocked** because the accepted COMMERCE-008 read port cannot enumerate durable template revisions, so an existing DRAFT cannot be rediscovered after refresh/reopen and the required revision-history UI cannot be implemented without bypassing the canonical service. `ARCH-021-COMMERCE-015` is added **Ready** as the bounded read-only contract completion. COMMERCE-013 also retains local correction items for selected-template metadata reset and dirty template-switch guarding; it returns to Ready only after COMMERCE-015 is Complete.

### COMMERCE-013 Attempt 2 architect review — 2026-09-23

Attempt 2 accepts the COMMERCE-015 revision-history integration, DRAFT resume/history rendering, keyed template-editor reset, internal discard/stay guard and real production revision-history action handoff. The task returns to **Ready** for Attempt 3 because successful mutations currently clear the shared editor dirty state even when another independently persisted editor surface remains unsaved, and revision create/update/publish results do not reconcile `selected.revisions`, leaving history/published-hash presentation stale until reopen.

### COMMERCE-035 Attempt 5 accepted — 2026-09-25

COMMERCE-035 is architect-accepted **Complete**. Attempt 5 enforces unique
canonical documentation paths before React, raises only the semantic block ceiling
to 512, adds cause-specific parser-bound diagnostics and preserves the independent
64 KiB service-output limit.

All terminal implementation dependencies are Complete, so
SYSTEM-TEST-001 becomes **Ready** again.

### COMMERCE-035 Attempt 4 changes requested — 2026-09-25

Attempt 4 satisfies the semantic Shopify page-chrome/accessibility cleanup.
COMMERCE-035 remains **Ready** for Attempt 5 because additional developer manual
logs prove duplicate canonical documentation paths still reach React as duplicate
keys, and the parser still uses the original 256-block ceiling with an
indistinguishable generic parser-bound error.

Attempt 5 raises only the semantic block ceiling to 512 while retaining the
64 KiB serialized-output cap, enforces unique documentation paths before React
rendering, adds bound-specific diagnostics/regressions, and removes conflict-marker
residue from the task record.

SYSTEM-TEST-001 remains Pending.

### COMMERCE-035 reopened after manual validation — 2026-09-25

Developer manual validation showed that safe structured blocks still included
Shopify documentation chrome/accessibility text such as `Choose a version`,
`Anchor to ...`, feedback controls and duplicated anchor labels. The same C035
task is reopened **Ready** for Attempt 4; the accepted component/safety
architecture remains unchanged.

SYSTEM-TEST-001 returns to Pending until C035 is Complete again.

### COMMERCE-035 Attempt 3 accepted — 2026-09-25

COMMERCE-035 is architect-accepted **Complete**. Attempt 3 adds the final required
`No preview available.` fallback regressions and reconciles the task's Acceptance
Criteria / Validation record without changing the accepted Attempt 2 production
normalization implementation.

All implementation dependencies of terminal `ARCH-021-SYSTEM-TEST-001` are now
Complete, so SYSTEM-TEST-001 becomes **Ready**.

### COMMERCE-035 Attempt 2 changes requested — 2026-09-25

Attempt 2 fixes the three production normalization/readability defects correctly.
COMMERCE-035 remains **Ready** for a narrow Attempt 3 because the explicitly
required `No preview available.` fallback regression is still absent and the task
returned with the remaining Acceptance Criteria / Validation checklist
unreconciled.

Attempt 3 is expected to be test/evidence-only. SYSTEM-TEST-001 remains Pending.

### COMMERCE-035 Attempt 1 changes requested — 2026-09-25

The structured documentation DTO and extracted
`ShopifyDocumentationExplorer`/`ShopifyDocumentationArticle` component boundary
are accepted in substance. COMMERCE-035 remains **Ready** for a narrow Attempt 2
because entity-encoded HTML tags can reappear as literal markup after
normalization, UTF-8 byte trimming can stop on a dangling UTF-16 surrogate, and
`<br>` currently joins adjacent words instead of producing a readable separator.

Attempt 2 is bounded to those server-side normalization/parser cases and their
regressions. SYSTEM-TEST-001 remains Pending.

### COMMERCE-034 Attempt 5 accepted — 2026-09-25

COMMERCE-034 is architect-accepted **Complete**. Attempt 5 closes the final
generated-variable/mapping collision and non-truncating Int literal-authoring
cases. The full Storefront query-builder path is now schema-driven and validated
against the accepted compiler before application.

COMMERCE-035 is now **Ready**. Before promotion, its architect-owned task
definition was reconciled with the previously requested component boundary:
`ShopifyDocumentationExplorer` owns search/open state and
`ShopifyDocumentationArticle` is the pure structured document renderer.
SYSTEM-TEST-001 remains Pending.

### COMMERCE-034 Attempt 4 changes requested — 2026-09-25

Attempt 4 fixes scalar input-compatibility parity, genuinely generates the nested
`product.handle` candidate through the real compiler, and proves full-definition
validated/applied identity. COMMERCE-034 remains **Ready** for a narrow Attempt 5
because an existing deterministic generated-name GraphQL variable with no
`execution.variables` mapping can still silently acquire a new mapping, contrary
to the explicit collision contract.

Attempt 5 must also stop the Int argument editor from truncating values such as
`1.5`/`1e2` with `parseInt()` before the typed AST builder can reject them.
COMMERCE-035 remains Pending.

### COMMERCE-034 Attempt 3 changes requested — 2026-09-25

Attempt 3 fixes LIST-wrapper detection, first-only/last authoring parity and the
task-owned TS2367. COMMERCE-034 remains **Ready** for a narrow Attempt 4 because
the new shared input-compatibility helper currently accepts string Tool inputs for
real Boolean/Int/Float GraphQL arguments, so both builder and compiler can admit an
invalid mapping.

Attempt 4 must also make the nested-product compiler regression genuinely generate
its `product.handle` binding from a product-free base query and complete the
previously required full-definition validated/applied identity assertion.
COMMERCE-035 remains Pending.

### COMMERCE-034 Attempt 2 changes requested — 2026-09-25

Attempt 2 completes the main production argument-binding/schema-identity/compiler
architecture, but COMMERCE-034 remains **Ready** for Attempt 3.

The submitted typecheck still contains one C034-owned `TS2367`; that comparison
also leaves LIST literal authoring incorrectly exposed. The argument editor also
treats `first` as a connection bound only when `last` exists, while the real pinned
schema contains first-only pagination fields such as `productTags(first: Int!)`.

Attempt 3 is bounded to those source corrections plus the exact connected
regressions already required by the Attempt 1 review. COMMERCE-035 remains
Pending.

### COMMERCE-034 Attempt 1 changes requested — 2026-09-24

The GraphQL AST/merge foundation is accepted in substance, but COMMERCE-034
remains **Ready** for Attempt 2 because production Studio has no argument-binding
controls/state, literal generation is not schema-aware, connection `first`/`last`
authoring policy is not represented before validation, and the client builder
takes schema identity from the artifact module instead of the C032 `SchemaPage`.

Attempt 2 must complete the original argument-authoring/schema-identity contract,
remove generated-variable mapping collision risk, and prove the final candidate
against the real Storefront compiler. COMMERCE-035 remains Pending.

### COMMERCE-033 Attempt 3 accepted — 2026-09-24

COMMERCE-033 is architect-accepted **Complete**. Attempt 3 added the missing
deterministic regression evidence for recursive ancestor counting, the browser's
exact 100/101 total-field boundary and both schema-identity reset dimensions
without changing the accepted Attempt 2 production implementation.

COMMERCE-034 is now **Ready**. COMMERCE-035 and SYSTEM-TEST-001 remain
dependency-gated.

### COMMERCE-033 Attempt 2 changes requested — 2026-09-24

Attempt 2 fixes the production depth and total-selected-field bounds correctly.
COMMERCE-033 remains **Ready** for a narrow Attempt 3 because the new 100/101 test
only counts independent root nodes and does not exercise the browser rejection
branch/prior-tree preservation, while schema-identity reset is tested only for
`schemaHash` and not `apiVersion`.

Attempt 3 is expected to be regression/evidence-only unless those stronger tests
expose a source defect. COMMERCE-034 remains Pending.

### COMMERCE-033 Attempt 1 changes requested — 2026-09-24

The recursive real-schema browser and nested selection tree are accepted in
substance. COMMERCE-033 remains **Ready** for Attempt 2 because the UI depth bound
is off by one relative to the accepted Storefront compiler and the 100-field UI
bound counts only leaves instead of all selected GraphQL fields/ancestors.

The architect-authored task contract was also restored after the submitted task
file removed scope/requirement/dependency and validation content during execution.
COMMERCE-034 remains Pending.

### COMMERCE-032 Attempt 2 accepted — 2026-09-24

COMMERCE-032 is architect-accepted **Complete**. The real pinned Storefront 2026-07
introspection artifact is the sole field/type source, the obsolete hand-authored
subset is absent and guarded against reintroduction, and the normalized discovery
contract exposes no synthetic server path.

COMMERCE-033 is now **Ready**. COMMERCE-034/035 and SYSTEM-TEST-001 remain
dependency-gated.

### COMMERCE-022 Attempt 4 accepted — 2026-09-25

COMMERCE-022 is **Complete / Accepted, Attempt 4**. Admin variable-mapping validity is now derived exclusively from current visible GraphQL variables/mapping modes/input-schema properties/literal text, eliminating stale literal-history state while keeping type compatibility compiler-owned. The final Admin UI mapping packet passed 15/15; the affected C022/C020/workspace packet passed 53/54 with only the unrelated historical Storefront stale-CAS baseline remaining; compiler 22/22, authoring validation 9/9, targeted lint/diagnostics and diff checks passed. COMMERCE-021 remains the sole Ready Phase 3 Commerce implementation task.

### COMMERCE-020 Attempt 5 accepted — 2026-09-25

COMMERCE-020 is **Complete / Accepted, Attempt 5**. The extracted Tool domain now owns named Server Action mutation handling and transport-only serializable UNCONFIRMED state without mutation replay; real audit reconciliation is actor-authorized and fail closed; committed composite EXTERNAL_HTTP recovery cannot expose duplicate create/draft retries when canonical identity cannot be resolved; and newer edits remain dirty across earlier save completion. The final Tool/reconciliation packet passed 26 focused tests, the ARCH-020 external UI packet passed 13 tests, targeted lint/source audits/diff checks passed, and task-owned TypeScript diagnostics are zero. With C019/C023/C024 already Complete, COMMERCE-021 and COMMERCE-022 are promoted to **Ready**.

### COMMERCE-020 Attempt 4 changes requested — 2026-09-25

Attempt 4 preserves the corrected Tool mutation/result and transport-only UNCONFIRMED boundaries, but the required executable R8 suite is still incomplete: the reconciliation test does not invoke the real Server Action and the Tool screen lacks committed/not-committed/authorization/composite-recovery regressions. Committed external-create recovery also clears UNCONFIRMED when canonical Tool/DRAFT identity cannot be resolved, which can expose a duplicate retry after the audit row proves the original operation committed. COMMERCE-020 remains **Ready** for Attempt 5; COMMERCE-021/022 remain Pending.

### COMMERCE-020 Attempt 3 changes requested — 2026-09-25

Attempt 3 completes the direct outer-composer boundary, Tool-local UNCONFIRMED
state, audit-only reconciliation authorization/allow-list and independent
external create/draft operation identities. COMMERCE-020 remains **Ready** for
Attempt 4 because direct lifecycle `CONFLICT` still maps to `INTERNAL_ERROR`,
post-success canonical refresh failure can still be misclassified as
UNCONFIRMED, composite committed recovery is incomplete, and the required R8
executable behavior suite is still largely absent. COMMERCE-021/022 remain
Pending.

### COMMERCE-020 Attempt 1 changes requested — 2026-09-25

The Tool-domain extraction is accepted in substance, but COMMERCE-020 remains **Ready** for Attempt 2 because production still supplies the extracted screen with `StudioWorkspace` function-valued `controlled` orchestration and therefore still uses the old catch-to-unknown / replay-the-original-mutation path. Attempt 2 must complete the serializable Tool boundary, exact bounded Tool mutation results, audit-only reconciliation, composite external-create operation identity and the executable R8 regressions. COMMERCE-021/022 remain Pending.
