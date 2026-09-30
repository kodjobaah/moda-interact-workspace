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
| [COMMERCE-064](COMMERCE-064-rebuild-explore-shopify-admin-authoring.md) | UI: rebuild Explore Shopify on Admin API with sessionStorage authoring handoff | Complete | COMMERCE-039, COMMERCE-061 |
| [COMMERCE-065](COMMERCE-065-split-shopify-request-response-authoring.md) | UI: split Shopify Request invocation from Response result-contract authoring | Complete | COMMERCE-062, COMMERCE-064 |
| [COMMERCE-066](COMMERCE-066-build-result-template-authoring-ui.md) | UI: build reusable schema-backed Result Template authoring component | Complete | COMMERCE-063 |
| [COMMERCE-067](COMMERCE-067-separate-agent-and-result-template-validation.md) | Backend: separate Agent call-side and Result Template validation ownership | Complete | COMMERCE-063 |
| [COMMERCE-068](COMMERCE-068-integrate-result-template-tool-authoring.md) | UI: integrate Result Template tab and rebalance Agent Contract/Review | Complete | COMMERCE-065, COMMERCE-066, COMMERCE-067 |
| [COMMERCE-069](COMMERCE-069-remove-storefront-tool-architecture.md) | Backend cleanup: remove obsolete Storefront Tool execution/discovery architecture | Complete | COMMERCE-060, COMMERCE-064 |
| [COMMERCE-070](COMMERCE-070-enforce-shopify-admin-result-contract-runtime.md) | Backend integration: enforce compiler-derived Admin result contract at runtime | Complete | COMMERCE-060, COMMERCE-062 |
| [COMMERCE-071](COMMERCE-071-add-tool-authoring-structured-logging.md) | Observability: add shared structured diagnostics for Tool authoring, Admin Explore/schema derivation, live Test, mutations and reconciliation | Ready | COMMERCE-039, COMMERCE-054, COMMERCE-056, COMMERCE-060, COMMERCE-061, COMMERCE-062, COMMERCE-064, COMMERCE-065, COMMERCE-067 |
| [COMMERCE-076](COMMERCE-076-restore-result-template-tab-integration.md) | Superseded regression restoration; replaced by the 2026-09-28 authoring-flow refinement | Superseded | - |
| [COMMERCE-077](COMMERCE-077-start-tool-definition-authoring-flow.md) | UI/state: Create Tool launcher + first-class local Tool Definition | Complete | COMMERCE-039, COMMERCE-064 |
| [COMMERCE-078](COMMERCE-078-compose-new-tool-authoring-flow.md) | UI: exact new-Tool flow, Result Template before Test, derived Agent Contract in Review | Complete | COMMERCE-077, 063, 066, 067, 068 |
| [COMMERCE-079](COMMERCE-079-align-persisted-draft-authoring-flow.md) | UI: persisted-DRAFT parity, CAS Save and Cancel reset | Complete | COMMERCE-078 |
| [COMMERCE-080](COMMERCE-080-render-external-live-test-result-template.md) | Backend: render complete External live-Test candidate through production Result Template | Complete | COMMERCE-054, COMMERCE-063 |
| [COMMERCE-081](COMMERCE-081-show-rendered-template-in-external-test.md) | UI: show populated Result Template as primary External Test result | Complete | COMMERCE-078, COMMERCE-079, COMMERCE-080 |
| [COMMERCE-082](COMMERCE-082-execute-shopify-admin-candidate-live-test.md) | Backend: non-durable Shopify Admin candidate execution + production rendering | Complete | COMMERCE-060, 062, 063, 070 |
| [COMMERCE-083](COMMERCE-083-integrate-shopify-admin-test-tab.md) | UI: integrate Shopify Admin Test for new/persisted DRAFTs | Complete | COMMERCE-078, COMMERCE-079, COMMERCE-081, COMMERCE-082, COMMERCE-085, COMMERCE-087 |
| [COMMERCE-084](COMMERCE-084-result-template-nunjucks.md) | Runtime: replace Result Template grammar/renderer with constrained `nunjucks.v1` | Complete | COMMERCE-063, COMMERCE-078, COMMERCE-080, COMMERCE-082 |
| [COMMERCE-085](COMMERCE-085-result-template-editor.md) | UI: replace Text/Items authoring with generated CodeMirror Nunjucks source editor | Complete | COMMERCE-078, COMMERCE-084 |
| [COMMERCE-086](COMMERCE-086-add-result-template-guide-link.md) | UX/docs: package and link the Result Template user guide | Complete | COMMERCE-084, COMMERCE-085, COMMERCE-093, COMMERCE-094 |
| [COMMERCE-087](COMMERCE-087-make-generated-nunjucks-safe-for-optional-fields.md) | Runtime correction: make generated Nunjucks safe for schema-permitted optional omissions | Complete | COMMERCE-084 |
| [COMMERCE-095](COMMERCE-095-add-progressive-new-tool-tab-navigation.md) | UI: progressive Previous/Next and monotonic first-unlock traversal for new Tool authoring | Complete | COMMERCE-078, COMMERCE-083 |

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

### Tool-authoring diagnostic logging follow-up — 2026-09-27

Manual debugging of the completed Tool-authoring flows identified a semantic logging gap: the Commerce process already uses the shared structured logger and production execution has `commerce.definition.outcome` telemetry, but Studio authoring mostly logs unexpected exceptions. COMMERCE-071 adds bounded shared-logger diagnostics for Request/Response validation, Shopify Admin Explore schema browsing/query validation/result-contract derivation, non-durable live Test stages, Agent/Admin validation, Tool mutations and reconciliation without logging authored GraphQL/schema payloads, provider bodies or credentials. Existing discovery telemetry remains authoritative for metrics; the new structured logs add only correlation/timing and bounded safe compiler/schema metadata needed for debugging. It is independent of tab-gating/UI work and does not duplicate generic framework HTTP telemetry.

COMMERCE-071 is **Ready**; all of its dependencies are architect-accepted Complete.

### COMMERCE-082 Attempt 1 accepted — 2026-09-28

COMMERCE-082 is **Complete / Accepted, Attempt 1**. Studio can now execute the exact current non-durable Shopify Admin candidate against the server-authoritative selected shop using the existing production Admin execution port, compiler-derived result contract and canonical Result Template renderer. Candidate/result/template failures remain pre-I/O, browser-supplied shop credentials are rejected by the strict input boundary, one provider request is budgeted, browser-visible results are bounded, and no Tool/revision/audit/publication-proof write is created. Submitted validation passed 96/96 tests across the focused eight-file packet plus targeted ESLint and diff checks; changed C082 files are clean under the submitted TypeScript diagnostics.

C082's COMMERCE-083 UI follow-up is materialised. C078, C079 and C082 are Complete after C079 Attempt 2 acceptance, but COMMERCE-083 remains Pending until COMMERCE-081 is also Complete.

### Result Template integration regression follow-up — 2026-09-27

The accepted COMMERCE-068 Result Template integration has regressed in the current source: `ResultTemplateTab` survives, but the shared registry exposes only five tabs, Agent Contract again owns `responseTemplate`, and Review no longer presents Result Template separately.

COMMERCE-076 was originally defined to restore the old six-tab composition, but it is **Superseded before execution** by the 2026-09-28 product flow below.

### Tool creation authoring-flow refinement — 2026-09-28

Canonical product flow:

```text
Tools: Create Tool
        |
        v
Tool Definition -> Request -> Response -> Result Template -> Test -> Review
                                                                  |       |
                                                                Cancel   Save
```

Ownership:

- Tool Definition owns name/display name/description/SemVer/provider kind;
- Request owns input schema and provider request/mappings;
- Response owns canonical result contract;
- Result Template owns `responseTemplate`;
- Test executes the complete candidate and shows server-rendered `Result shown to agent`;
- Agent Contract is derived/read-only in Review, not a tab;
- new authoring/Cancel/Test are non-durable; new Save is the one atomic create;
- persisted DRAFT Save stays CAS-based.

Executable frontier:

```text
COMMERCE-077    COMMERCE-080    COMMERCE-082
```

Then:

```text
077 -> 078 -> 079 -> 081 -> 083 -> 095 -> SYSTEM-TEST-002
                  ^             ^
080 ---------------+             |
082 -----------------------------+
```

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
- progressive new-Tool traversal is owned by COMMERCE-095 after the six individual authoring surfaces are complete; persisted-DRAFT traversal remains unchanged.




### COMMERCE-080 Attempt 1 accepted — 2026-09-28

COMMERCE-080 is **Complete / Accepted, Attempt 1**. External HTTP live Test now consumes the complete current unsaved Tool definition, validates Result Template compatibility before provider I/O, validates processed values against the canonical result contract, builds the production `ExternalHttpResultDataSchema` `data.values` envelope and delegates final text rendering to `renderDefinitionResult`. Both existing External editors pass the current local candidate into Test; rendered-result presentation remains deferred to COMMERCE-081. Submitted validation passed the 24-test backend/action/integration packet, all 81 External Tools UI tests, targeted Test-tab assertions, ESLint and `git diff --check`. Repository TypeScript remains non-green only on the documented baseline; no new C080 payload/backend diagnostic is present.

COMMERCE-081 is materialised. After C079 Attempt 2 acceptance, C078, C079 and C080 are Complete, so COMMERCE-081 is Ready.


### COMMERCE-077 Attempt 2 accepted — 2026-09-28

COMMERCE-077 is **Complete / Accepted, Attempt 2**. The stale asynchronous provider-selection race is fixed with a monotonic local generation guard; deferred regressions prove late Shopify metadata cannot replace a newer External selection and older Shopify metadata cannot overwrite a newer Shopify selection. The local-first Tool Definition architecture, Explore handoff and final `createToolWithInitialDraft` write boundary remain unchanged.

COMMERCE-078 is Complete / Accepted, Attempt 4. Its new-Tool authoring session now includes the provider-neutral Test checkpoint/freshness model consumed by C081/C083.

### COMMERCE-068 Attempt 1 accepted — 2026-09-27

COMMERCE-068 is **Complete / Accepted, Attempt 1**. New Tool and persisted-DRAFT authoring now expose a dedicated Result Template tab backed by the source-neutral ToolResultContract boundary; Agent Contract is call-side only; and Review presents Agent contract, Result contract and Result Template separately. Free tab navigation, invalid local authoring retention, explicit Save/Create/Publish boundaries, External HTTP Response behavior and Shopify manual GraphQL remain unchanged. Submitted validation passed 127/127 focused UI tests, targeted ESLint, changed-file diagnostics and `git diff --check`. The recorded `npm ci` Node-engine/audit warnings did not alter manifests or lockfiles.

With COMMERCE-060 through COMMERCE-070 now architect-accepted Complete, this refinement workstream has no remaining executable task.

### COMMERCE-065 Attempt 2 accepted — 2026-09-27

COMMERCE-065 is **Complete / Accepted, Attempt 2**. Shopify Admin Request/Response ownership remains split as designed, and the remaining stale asynchronous derivation race is closed: an obsolete in-flight result must still match the latest committed identity/generation before it can promote schema or mark Response fresh. Deferred regressions prove stale completion cannot re-enable New Tool Create or persisted-DRAFT Save/Publish. Attempt 2 also supplies the required launcher/worktree/synchronization and VCS evidence. Submitted validation passed 49/49 focused tests, targeted ESLint, changed-file diagnostics and `git diff --check`; package-wide TypeScript remains red only on unrelated files.

COMMERCE-066 and COMMERCE-067 are already Complete, so COMMERCE-068 is promoted to **Ready**. COMMERCE-069 remains independently Ready.

### COMMERCE-064 Attempt 3 accepted — 2026-09-27

COMMERCE-064 is **Complete / Accepted, Attempt 3**. The Admin Explore authoring handoff now keeps Request literal buffers consistent with accepted variable mappings across the real New Tool Request -> Explore -> Validate -> Use in tool -> Request flow: semantically unchanged literals retain exact raw text, changed/new literals receive bounded canonical JSON, and stale entries are removed without disturbing unrelated editor buffers. The accepted Attempt 1/2 boundaries remain intact: browser-session authoring identity, Request-only validation, exact session isolation/return, manual GraphQL authority, Cancel semantics, no provider I/O and no durable Tool creation merely for Explore navigation. Submitted Attempt 3 validation passed 55 tests across five suites, targeted ESLint and `git diff --check`; neither Attempt 3 file has filtered TypeScript diagnostics.

COMMERCE-062 is already Complete, so COMMERCE-065 is promoted to **Ready**. COMMERCE-060 is already Complete, so COMMERCE-069 is also promoted to **Ready**. COMMERCE-068 remains Pending until COMMERCE-065 is Complete.

### COMMERCE-069 Attempt 1 accepted — 2026-09-27

COMMERCE-069 is **Complete / Accepted, Attempt 1**. The canonical Commerce Tool union, production executor/availability path and Studio authoring no longer support `SHOPIFY_STOREFRONT_QUERY`; obsolete Storefront compiler/query/runtime/schema-browser artifacts were removed while legitimate Storefront-named Shopify Admin schema/documentation concepts were preserved. The focused removal/regression packet passed 114 tests across 11 files, targeted ESLint and `git diff --check`; changed-file diagnostics are clean while workspace-wide TypeScript retains unrelated diagnostics. The disposable C20 PostgreSQL/Redis integration was unavailable and is non-blocking for this task. The task-record regression checkbox and stale review claim were clerical inconsistencies reconciled during acceptance.

C069 enables no downstream task. The remaining executable Shopify/Admin frontier is **COMMERCE-065**; COMMERCE-068 remains dependency-gated by COMMERCE-065.

### COMMERCE-070 Attempt 1 accepted — 2026-09-27

COMMERCE-070 is **Complete / Accepted, Attempt 1**. Production Shopify Admin execution now derives the authoritative result contract from the immutable Admin definition, rejects stale persisted schemas before provider output is exposed, normalizes nullable output through the shared COMMERCE-062 semantics, and validates the normalized value before assigning canonical `data.values`. Publication/authoring validation uses the same exact derived-schema equality. Submitted validation passed the 64-test focused regression packet, 30 adjacent Admin builder/contract tests, the targeted Admin executable-registry integration case, targeted ESLint, changed-file diagnostics and `git diff --check`. The full backend integration file retains two unrelated `getCommerceBackend()` process-global availability assertion failures; review found no C070 change to that initialization path.

C070 enables no downstream task. The current executable frontier for this Shopify/Admin workstream remains **COMMERCE-064**; COMMERCE-065 and COMMERCE-069 remain dependency-gated by COMMERCE-064, and COMMERCE-068 remains dependency-gated by COMMERCE-065.

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


### COMMERCE-078 Attempt 4 accepted — 2026-09-28

COMMERCE-078 is **Complete / Accepted, Attempt 4**. New Tool authoring now uses the agreed provider-aware six-step composition and browser-local Save boundary, and the shared new-Tool session owns exactly one provider-neutral Test checkpoint based on Tool Definition, Request, Response and Result Template validation revisions. C078 does not execute providers or store provider Test payloads; C081/C083 consume the C078 checkpoint while invoking the already-accepted C080/C082 backends.

Current executable refinement frontier after C079 Attempt 2 acceptance:

```text
COMMERCE-081
```

COMMERCE-083 is Ready after C081 Attempt 2 acceptance.


### COMMERCE-079 Attempt 1 review — Changes Requested — 2026-09-28

Manual validation confirms the persisted six-tab composition is present. Attempt 1 remains unaccepted for three bounded corrections: remove the unreachable duplicate legacy External DRAFT branch; keep Shopify durable Save/Validate/Publish/Cancel actions Review-owned only; and establish the persisted provider-neutral four-revision/Test freshness checkpoint required by C081/C083. C081 and C083 are therefore Pending until C079 is Complete.


### COMMERCE-079 Attempt 2 accepted — 2026-09-28

COMMERCE-079 is **Complete / Accepted, Attempt 2**. Persisted External HTTP and Shopify Admin DRAFTs now use the canonical six-step ownership model with one active supported editor path per provider, Review-only durable actions, one-CAS Save/Cancel restoration semantics and the shared four-revision provider-neutral Test freshness checkpoint inherited from C078. Test-only transient state remains separate from persistence dirtiness and C079 adds no provider Test backend.

C078, C079, C080 and C081 are Complete. COMMERCE-083 is **Ready**. SYSTEM-TEST-002 remains Pending until C083 is Complete.


### COMMERCE-081 Attempt 2 accepted — 2026-09-28

COMMERCE-081 is **Complete / Accepted, Attempt 2**. External live Test now combines the C078/C079 common authored-section checkpoint with a monotonic provider-local transient generation, so argument/shop A -> B -> A reversion cannot resurrect pending or displayed provider results. Server-rendered Result Template text remains the primary Test output, diagnostics remain bounded/secondary, and Test-only state stays non-durable.

C078, C079, C081 and C082 are Complete, so COMMERCE-083 is **Ready**. SYSTEM-TEST-002 remains Pending until C083 is Complete.


### COMMERCE-084 Attempt 1 changes requested — 2026-09-28

C084 is **Ready** for Attempt 2. The current one-runtime Nunjucks foundation is accepted in substance, but the canonical `nunjucks.v1` contract is expanded before acceptance to bounded `if`/`elif`/`else`, primitive literals, comparisons, boolean expressions and numeric arithmetic with schema-aware static typing. Attempt 2 must also use the installed Nunjucks parser/AST as syntax authority, remove the accidental default filesystem loader, make generated templates self-validating (including root scalar/parallel complexity cases), migrate the remaining C084-owned ARCH-020 fixture, and produce a durable committed/pushed Completion Report.

C085 remains **Pending** on C084 and owns the legacy Text/Items editor/state migration. C079/C081 are already Complete and must be preserved rather than re-executed. C083 is re-gated **Pending** on C085 so Shopify Admin Test UI integration consumes the final Nunjucks authoring surface.


### COMMERCE-084 Attempt 3 accepted — 2026-09-29

COMMERCE-084 is **Complete / Accepted, Attempt 3**. The constrained `nunjucks.v1` runtime now uses the installed Nunjucks AST as syntax authority plus Moda's schema-aware allowlist/type checker, explicit no-loader rendering, bounded control flow/expression semantics, deterministic self-validating generation and one shared publication/Test/production render boundary. The final comparison matrix is scalar-only, and combined `if`/`for` depth is correctly enforced through plain `else` bodies without counting repeated `elif` as additional nesting.

COMMERCE-085 is **Ready**. It owns the remaining Text/Items React/editor/state migration and generated CodeMirror authoring UX. COMMERCE-083 remains **Pending** on C085.


### COMMERCE-085 Attempt 2 accepted — 2026-09-29

COMMERCE-085 is **Complete / Accepted, Attempt 2**. The canonical Nunjucks Result Template authoring surface now uses controlled CodeMirror synchronization that distinguishes programmatic generation from user edits, reuses C084 loop-generation semantics for insertions, renders the canonical schema tree without synthetic object-array nodes, labels the actual CodeMirror textbox accessibly, and preserves the accepted C079/C081 lifecycle/Test boundaries. External and Shopify Admin UI integration suites now execute and pass after approved Prisma Client generation.

COMMERCE-086 is **Ready**.

Manual live-Test validation separately exposed a C084 generator/runtime mismatch for schema-permitted omitted optional fields. That correction is materialised as COMMERCE-087 and is **Ready**. COMMERCE-083 remains **Pending** until COMMERCE-087 is Complete.


### COMMERCE-087 Attempt 2 accepted — 2026-09-29

COMMERCE-087 is **Complete / Accepted, Attempt 2**. Generated Nunjucks templates now remain within the accepted C084 grammar while schema-permitted omissions are normalized only in a pure template-safe render context. Optional/effectively-optional scalar output uses the existing `!= null` guard, optional arrays normalize to empty collections for deterministic fallback, nested optional objects are schema-shaped safely, present values are preserved, required omissions remain invalid, and provider results are not mutated.

C078, C079, C081, C082, C085 and C087 are Complete, so COMMERCE-083 is **Ready**. SYSTEM-TEST-002 remains Pending until C083 is Complete.


### COMMERCE-083 Attempt 2 accepted — 2026-09-29

COMMERCE-083 is **Complete / Accepted, Attempt 2**. Attempt 1's missing-C082 integration blocker was resolved before Attempt 2. The final implementation consumes the accepted C082 Shopify Admin live-Test backend through one reusable new/persisted Test surface, reuses the common C078/C079 Test checkpoint with C081-style transient-generation protection, shows exact server-rendered Result Template output first, and requires a current Shopify Test PASS before new Create or persisted Save.

The authoritative C083 task file preserves the full Attempt 1 blocker, Attempt 2 Completion Report, validation evidence and Accepted Architect Review. SYSTEM-TEST-002 remains the terminal integrated Tool-authoring validation task.

### COMMERCE-095 Attempt 1 changes requested — 2026-09-29

C095 is **Ready** for Attempt 2. The six-step progressive-navigation implementation
is accepted in substance, but the provider-reset confirmation can be bypassed by
navigating to an already-enabled step before the confirmation is resolved, and
the pre-provider instruction still describes the old unlock model. Attempt 2 is
bounded to those corrections, focused regressions and durable launcher/worktree
evidence reconciliation.

SYSTEM-TEST-002 is terminally gated behind C095 as well as C079/C081/C083 and
remains Pending.

### COMMERCE-095 Attempt 2 accepted — 2026-09-29

C095 is **Complete / Accepted, Attempt 2**. Provider-reset confirmation now freezes
new-Tool traversal at Tool Definition until Cancel or successful replacement;
Cancel restores the existing unlock frontier, successful replacement resets the
frontier, and the fresh-session guidance describes progressive Next-based
unlocking. The required launcher/worktree/synchronization/submodule evidence is
recorded in the Completion Report.

The architect also repaired accidental Attempt-2 corruption of the architect-owned
R1/R2 Requirements block while reconciling this acceptance. No runtime rework was
required for that record repair.

All SYSTEM-TEST-002 implementation dependencies are now Complete, so terminal
`ARCH-021-SYSTEM-TEST-002` is **Ready**.

## Phase 5 — Feature Capability authoring simplification — 2026-09-29

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-088](COMMERCE-088-implement-direct-feature-capability-authoring.md) | Backend: direct Feature reads/Behaviour prompt and atomic Feature + Tool Capability creation | Complete | DATABASE-003 |
| [COMMERCE-089](COMMERCE-089-compose-releases-from-direct-capabilities.md) | Backend/runtime: releases pin exact Tool revisions and snapshot Feature Behaviour | Complete | DATABASE-003, SHARED-002, COMMERCE-088 |
| [COMMERCE-090](COMMERCE-090-build-feature-configuration-surface.md) | UI: Feature-centric Behaviour + current Capability/Tool surface | Complete | COMMERCE-088 |
| [COMMERCE-091](COMMERCE-091-build-local-first-add-capability-flow.md) | UI: local-first Capability -> Tool -> Review -> Create flow | Complete | COMMERCE-088, COMMERCE-090 |
| [COMMERCE-092](COMMERCE-092-remove-legacy-capability-architecture.md) | Delete old Capability revision/binding/routes/services/fixtures after replacement paths are complete | Complete | COMMERCE-089, COMMERCE-091, BACKGROUND-002 |


### COMMERCE-088 Attempt 2 accepted — 2026-09-29

COMMERCE-088 is **Complete / Accepted, Attempt 2**. The direct Feature-domain backend reads Admin-owned Features and current Feature Behaviour directly, applies monotonic CAS with immutable replay/audit semantics, and creates one Feature + Tool Capability atomically without legacy Capability revision/binding authoring. Attempt 2 reconciled the retained launcher/worktree evidence and cleared claim metadata; the synchronized implementation branch left every C088-owned source/test file byte-for-byte unchanged from the already validated Attempt-1 snapshot.

COMMERCE-090 is now **Ready** because its sole dependency, COMMERCE-088, is Complete. COMMERCE-089 remains **Pending** until SHARED-002 is Complete.

The two implementation branches after COMMERCE-088 are intentionally parallel: COMMERCE-089 owns release/runtime composition while COMMERCE-090/091 own the user-facing Feature authoring flow. COMMERCE-092 is the subtractive gate and must not execute until both replacement paths and Background consumption are accepted.


### COMMERCE-090 Attempt 3 accepted — 2026-09-29

COMMERCE-090 is **Complete / Accepted, Attempt 3**. The dedicated Feature configuration surface now has CAS-safe shared Behaviour editing across in-flight local edits and concurrent canonical refreshes, and unresolved admitted saves are non-discardable during navigation. The two Attempt-3 corrections are covered by focused regressions in the 13/13 Feature route/screen/shell packet.

COMMERCE-091 is now **Ready** because both of its dependencies, COMMERCE-088 and COMMERCE-090, are Complete. COMMERCE-092 remains Pending until all of its replacement-path and Background dependencies are Complete.

### COMMERCE-091 Attempt 2 accepted — 2026-09-29

COMMERCE-091 is **Complete / Accepted, Attempt 2**. The Feature-scoped local-first `Capability -> Tool -> Review` flow preserves unlocked phases through later upstream invalidation using one monotonic session frontier, while current candidate readiness independently controls the final Create action. The accepted exactly-one-create, candidate-preservation and uncertain-outcome reconciliation boundaries remain intact.

The C091 dependency of COMMERCE-092 is satisfied. COMMERCE-092 remains Pending until COMMERCE-089 and BACKGROUND-002 are also Complete.

### COMMERCE-089 Attempt 1 accepted — 2026-09-29

COMMERCE-089 is **Complete / Accepted, Attempt 1**. Release creation now consumes direct Capability identities, deterministically pins each Capability's exact published Tool revision and snapshots Feature Behaviour once per represented Feature. Runtime manifest production reads immutable release rows, supports zero eligible Capabilities and preserves deterministic reused-Tool provenance without restoring Capability revisions, bindings or per-Capability configuration.

The required disposable C20 proof passed 2/2 on the final post-merge implementation branch. The remaining repository typecheck/process-global test failures contain no C089-owned diagnostics or release/runtime regressions. ARCH-021-BACKGROUND-002 is now **Ready**; COMMERCE-092 remains Pending until BACKGROUND-002 is Complete.

### BACKGROUND-002 Attempt 1 accepted — 2026-09-29

BACKGROUND-002 is **Complete / Accepted, Attempt 1**. The Background Commerce host now consumes the published Shared 1.0.0 direct Feature/Capability/Tool manifest, removes MCP Capability-prompt retrieval, accepts valid zero-Capability grants and retains exact Tool/grant provenance authorization.

COMMERCE-089, COMMERCE-091 and BACKGROUND-002 are all Complete, so COMMERCE-092 is now **Ready** as the final Phase 5 subtractive cleanup task.

### COMMERCE-092 Attempt 1 accepted — 2026-09-29

COMMERCE-092 is **Complete / Accepted, Attempt 1**. Architect review traced the deleted standalone Capability revision/list/editor lifecycle against the current Feature-centric authoring, Tool publication, release composition, activation/rollback and MCP/runtime paths. Current Feature-owned Capability creation remains under `/features/[id]/capabilities/new`; releases still select direct Capabilities, snapshot Feature Behaviour and pin exact published Tool revisions. No supported caller remains for the removed Capability revision/draft/binding APIs.

The disposable C20 DB/Redis rehearsal remains explicitly unexecuted because disposable targets were not configured. Terminal SYSTEM-TEST-003 is now Ready and owns the end-to-end validation of the completed simplified architecture.




### COMMERCE-094 Attempt 3 accepted — 2026-09-29

COMMERCE-094 is **Complete / Accepted, Attempt 3**. The full repository TypeScript check now passes with zero diagnostics and the normal production build completes successfully. The final architect-approved scope expansion required only two test typing corrections because the renderer narrowing fix was already present in the synchronized baseline. No runtime/schema/dependency/C086 behavior was changed.

COMMERCE-086 is therefore promoted from **Blocked** to **Ready** for Attempt 2. It owns its own clean-build confirmation and production-start HTTP smoke.

### COMMERCE-086 Attempt 1 blocked / COMMERCE-093 materialised — 2026-09-29

C086 is **Blocked** after a clean production build reached Next compilation and failed only on three over-deep imports in the untouched Studio code-response validation route. C086's manual packaging/link implementation remains within scope and its passed Attempt 1 evidence is preserved.

COMMERCE-093 is **Complete / Accepted, Attempt 1**. Its three route imports resolve correctly and the build advances beyond that blocker. The remaining repository TypeScript/build gate is owned by separately materialised COMMERCE-094. C086 remains Blocked and depends on both C093 and C094.

After C093 is architect-accepted Complete, C086 will be returned to Ready for Attempt 2 to rerun the clean production build and bounded `npm run start` manual HTTP smoke. No already-passed C086 implementation work should be repeated absent a relevant intervening change.


### COMMERCE-093 Attempt 1 accepted / C094 build gate — 2026-09-29

COMMERCE-093 is **Complete / Accepted, Attempt 1**. The route correction is exactly three import-depth edits, all corrected imports resolve within Commerce, route behavior is unchanged, and the production build advances beyond the original route-import failure.

The newly exposed 23 TypeScript diagnostics across 12 unrelated files are outside C093 scope and are owned by COMMERCE-094, which the developer reports is materialised on its own task branch at parent commit `58f65e5b`.

C086 remains **Blocked** and now explicitly depends on both C093 and C094. C094 must be promoted to Ready on its canonical task branch now that C093 is Complete. C086 must not resume until C094 is architect-accepted Complete.


## Policy Operation Studio authoring — generic persisted Tool support

This bounded follow-up keeps `POLICY_OPERATION` as the existing Moda-owned execution kind and adds generic Studio support for already-persisted Policy Operation Tools. It does not add Policy Operation to New Tool creation and does not implement ARCH-023 Merchant Knowledge.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-096](COMMERCE-096-expose-policy-operation-authoring-descriptors.md) | Canonical policy registration owns runtime validators + browser-safe authoring descriptor | Complete | COMMERCE-095 |
| [COMMERCE-097](COMMERCE-097-render-persisted-policy-operation-tool-authoring.md) | Render persisted Policy Operation Tool authoring surfaces | Complete | COMMERCE-096 |
| [COMMERCE-098](COMMERCE-098-live-test-policy-operation-tool-candidates.md) | Live-test Policy Operation candidates through DefinitionExecutor | Complete | COMMERCE-096 |
| [COMMERCE-099](COMMERCE-099-round-trip-and-save-policy-operation-tool-drafts.md) | Round-trip/Test/CAS-save persisted Policy Operation DRAFTs | Complete | COMMERCE-097, COMMERCE-098 |
| [COMMERCE-100](COMMERCE-100-publish-and-regression-validate-policy-operation-tools.md) | Publish/reopen/regression-validate Policy Operation Tools | Complete | COMMERCE-099 |

```text
                    C096 Complete
                    /           \
                   v             v
          C097 Complete      C098 Complete
                   \             /
                    v           v
                    C099 Complete
                           |
                           v
                    C100 Complete
```

### COMMERCE-096 Attempt 1 accepted — 2026-09-29

C096 is **Complete / Accepted, Attempt 1**. The same server-side policy registry now owns exact operation/version runtime validation/adapters and a cloned browser-safe authoring descriptor. The descriptor uses a Commerce-local JSON-schema representation generated from the canonical runtime validators so nested inputs, nullable outputs and accepted collection bounds are not lost.

COMMERCE-097 and COMMERCE-098 are **Ready** and may execute independently. C099 remains Pending on both.


### COMMERCE-098 Attempt 1 accepted — 2026-09-29

COMMERCE-098 is **Complete / Accepted, Attempt 1**. Policy Operation candidate Test is now an ADMIN-authorized, non-durable Studio boundary over the production `DefinitionExecutor` and C096 registry. Shop context and preview identities are server-created, exact operation/version resolution is required, and canonical mapped-input/output/result-rendering semantics remain executor-owned.

Canonical business outcomes such as `NOT_FOUND` remain valid Test results when a policy operation requires production state that is intentionally absent from the synthetic preview context; C098 does not fabricate production recovery/grant identity.

COMMERCE-099 remains **Pending** because COMMERCE-097 is still Ready. No dependent task is promoted by C098 alone.

### COMMERCE-097 Attempt 2 accepted — 2026-09-29

COMMERCE-097 is **Complete / Accepted, Attempt 2**. Policy Operation Result Template authoring now shares the production Policy result-schema projection and exposes descriptor fields directly as `result.<field>`; External HTTP and Shopify Admin retain their existing `result.values.*` envelopes. Response/Review continue to show the exact descriptor schema read-only, and C097 remains local-only.

Because COMMERCE-098 is already Complete, both dependencies of COMMERCE-099 are now satisfied. COMMERCE-099 is **Ready**; COMMERCE-100 remains Pending on C099.

### COMMERCE-099 Attempt 2 accepted — 2026-09-29

COMMERCE-099 is **Complete / Accepted, Attempt 2**. Persisted Policy Operation DRAFTs now share the common four-section validation/Test freshness ledger, execute live Test through C098, and CAS-save the exact current candidate while preserving the original operation/version binding. Conflict and unknown mutation outcomes retain local work; successful Save restores the returned definition and edit version.

Attempt 2 adds the same monotonic transient-generation protection already accepted for Shopify Admin Test, so Test arguments/shop A -> B -> A reversion cannot resurrect an obsolete in-flight result or re-enable Save. The focused packet passes 175/175 tests and the synchronized package-wide TypeScript check exits 0.

COMMERCE-100 is now **Ready** as the final generic Policy Operation publication/reopen/regression-validation task.

### COMMERCE-100 Attempt 1 accepted — 2026-09-29

COMMERCE-100 is **Complete / Accepted, Attempt 1**. Registered Policy Operation DRAFTs now complete the normal Studio lifecycle through saved/current-validation/current-Test/SUPER_ADMIN/reason-gated canonical publication. Exact registry unavailability fails atomically before publication mutation, and published revisions reopen read-only with the exact fixed operation/version and saved definition.

The New Tool selector remains unchanged and does not expose Policy Operation creation. No schema/migration, Merchant Knowledge special case or ARCH-023 implementation was introduced.

The generic Policy Operation Studio follow-up C096-C100 is now fully Complete; there is no remaining executable task in this bounded ARCH-021 follow-up.


### COMMERCE-086 Attempt 2 accepted — 2026-09-29

COMMERCE-086 is **Complete / Accepted, Attempt 2**. The Result Template guide has one canonical Commerce-owned source, is deterministically packaged into `public/manuals/` by the normal build, and is linked from Result Template authoring without authoring-state mutation.

After accepted C093/C094 removed the unrelated production-build blockers, C086's clean `npm run build` completed and the normal `npm run start` application served `/manuals/result-template-guide.html` with HTTP 200, HTML content type and the exact required title. No manual deployment copy step or Attempt 2 source change was required.

## Manual-validation follow-up — Tool execution target and interaction safety — 2026-09-29

Manual Shopify Admin Test validation exposed two bounded interaction-safety defects in the accepted Tool-authoring flow: the shell validates the selected shop but the Tools workspace still receives the raw URL `shopId`, and several consequential authoring actions rely on React pending state rather than a synchronous re-entry gate.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-102](COMMERCE-102-harden-tool-authoring-execution-context-and-single-flight-actions.md) | Make validated selected-shop context authoritative and make consequential Tool-authoring actions single-flight | Complete | COMMERCE-083, COMMERCE-095 |

COMMERCE-102 is **Complete / Accepted, Attempt 1**. The validated selected-shop context is authoritative for Tool execution presentation, and consequential Tool-authoring actions use synchronous single-flight admission plus stale-completion protection while preserving the server-authoritative C082/C083 lifecycle boundaries.

`ARCH-021-SYSTEM-TEST-002` is now **Ready** because COMMERCE-102 and COMMERCE-103 are both architect-accepted Complete.

## Manual-validation follow-up — persisted Tool sequential traversal — 2026-09-29

Manual validation of an existing Shopify Admin DRAFT exposed the navigation parity gap deliberately left out of COMMERCE-095: persisted External HTTP, Shopify Admin and Policy Operation editors show all six canonical tabs but do not render the shared `Previous`/`Next` footer.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-103](COMMERCE-103-add-persisted-tool-previous-next-navigation.md) | Add side-effect-free Previous/Next traversal to all persisted DRAFT Tool authoring kinds | Complete | COMMERCE-095, COMMERCE-099 |

COMMERCE-103 reuses the C095 canonical six-step order/presentation but does **not** import progressive unlocking into persisted DRAFTs. All persisted tabs remain directly clickable; `Previous`/`Next` are pure section navigation and never validate, Test, save or publish. COMMERCE-103 is independent of COMMERCE-102.

### COMMERCE-103 accepted — 2026-09-30

COMMERCE-103 is **Complete / Accepted**. The persisted External HTTP, Shopify Admin and Policy Operation traversal implementation and its 163-test regression packet are accepted, and the final canonical `npm run typecheck` now passes with zero diagnostics.

`ARCH-021-SYSTEM-TEST-002` is **Ready** after COMMERCE-102 Attempt 1 acceptance; both C102 and C103 dependency edges are satisfied.

## Manual-validation follow-up — Add Capability direct phase readiness — 2026-09-29

Manual validation of the accepted COMMERCE-091 Add Capability flow exposed a first-entry navigation admission gap: `enabledThrough` is monotonic once a phase has been entered, but the visible Tool/Review phase buttons remain disabled until `Next` performs that first unlock even when the current local candidate already satisfies the destination readiness predicate.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-104](COMMERCE-104-make-add-capability-phases-directly-navigable-when-ready.md) | Make Tool/Review directly clickable as soon as their current first-entry prerequisites are satisfied while preserving the monotonic unlock frontier | Complete | COMMERCE-091 |

COMMERCE-104 is a bounded browser-navigation correction. Before first entry, Tool follows live `validCapability` and Review follows live `canReview`; direct entry monotonically advances the same `enabledThrough` frontier already accepted in C091. After first unlock, later invalidation never re-locks the phase, while `Create capability` remains gated by the current `canReview`. Navigation remains local-only and performs zero Capability mutation/reconciliation calls.

`ARCH-021-SYSTEM-TEST-003` is re-gated **Pending** on COMMERCE-104 so terminal Feature/Capability validation runs only after this direct-phase correction is architect-accepted.

## Manual-validation follow-up — Add Capability semantic tabs — 2026-09-30

COMMERCE-104 corrected first-entry and monotonic-unlock mechanics, but manual validation shows the phase selector is still an unstyled numbered ordered list rather than a tab interface.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-110](COMMERCE-110-render-add-capability-phases-as-tabs.md) | Render Capability / Tool / Review as semantic tabs while preserving C104 navigation mechanics | Complete | COMMERCE-104 |

C110 is presentation-only: it replaces the numbered list with a semantic `Capability setup` tablist plus matching tabpanels and a bounded three-column/responsive style. It must not change C104 readiness, unlock, Previous/Next, Create or persistence semantics.

`ARCH-021-SYSTEM-TEST-003` was re-gated Pending on C110.

### COMMERCE-110 Attempt 1 accepted — 2026-09-30

COMMERCE-110 is **Complete / Accepted, Attempt 1**. Add Capability now uses three semantic Capability/Tool/Review tabs with exact tabpanel relationships and the requested responsive presentation, while preserving the accepted C104 navigation/state model.

Every SYSTEM-TEST-003 dependency is now Complete, so SYSTEM-TEST-003 is **Ready** for terminal validation.

## Phase 6 — Feature-composed selected-shop Test Conversations — 2026-09-29

Product decision: Test Conversations is Feature-composed. Selecting a Feature means **all direct Capabilities under that Feature**; there is no per-Capability exclusion. The browser submits Feature IDs and selected shop ID only. Commerce resolves Capabilities/Tool revisions and effective Agent Configuration server-side and freezes them when the conversation starts.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-105](COMMERCE-105-resolve-feature-composed-preview-selections.md) | Resolve ordered selected Features to every direct Capability, exact current published Tool revisions and one Feature Behaviour entry per Feature | Ready | COMMERCE-092 |
| [COMMERCE-106](COMMERCE-106-freeze-selected-shop-agent-configuration-in-preview.md) | Require the selected shop and freeze its effective Model/Prompt into the Preview conversation | Pending | COMMERCE-010, COMMERCE-105 |
| [COMMERCE-107](COMMERCE-107-build-feature-composed-test-conversations-ui.md) | Replace Release/fixture composition controls with selected-shop multi-Feature Test Conversations UI | Pending | COMMERCE-105, COMMERCE-106 |
| [COMMERCE-108](COMMERCE-108-execute-feature-preview-tools-against-selected-shop.md) | Execute frozen Feature Tools through the production DefinitionExecutor against the selected shop | Pending | COMMERCE-105, COMMERCE-106 |
| [COMMERCE-109](COMMERCE-109-remove-redundant-human-facing-preview-functionality.md) | Delete obsolete Tool/Release/Fixture human Preview paths while retaining fixture seams with concrete internal/test consumers | Pending | COMMERCE-107, COMMERCE-108 |

Execution graph:

```text
COMMERCE-105
     |
     v
COMMERCE-106
     |
     +----------+
     |          |
     v          v
COMMERCE-107  COMMERCE-108
     |          |
     +----+-----+
          |
          v
COMMERCE-109
          |
          v
GATEWAY-002
          |
          v
SYSTEM-TEST-004
```

COMMERCE-105 is **Ready** because COMMERCE-092 is architect-accepted Complete. The remaining Phase-6 Commerce tasks stay Pending until their declared dependencies are Complete. C107/C108 are intentionally parallel after C106. C109 is the explicit cleanup/subtractive gate requested during manual validation; obsolete UI is deleted rather than hidden behind a mode flag.
`ARCH-021-SYSTEM-TEST-003` was re-gated on COMMERCE-104 so terminal Feature/Capability validation would run only after this direct-phase correction was architect-accepted.

### COMMERCE-104 Attempt 1 accepted — 2026-09-29

COMMERCE-104 is **Complete / Accepted, Attempt 1**. Tool and Review now become directly clickable from current first-entry readiness, direct click and Next share the same admission path, historical unlock remains monotonic, and final Create stays gated by the current candidate. Navigation remains browser-local and zero-write.

All SYSTEM-TEST-003 dependencies are now Complete, so SYSTEM-TEST-003 is **Ready** for terminal validation.
