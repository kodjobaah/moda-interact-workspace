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
| [COMMERCE-042](COMMERCE-042-complete-javascript-request-authoring-ui.md) | Complete JavaScript bindings, resizable editor and mode-draft preservation | Ready | COMMERCE-041 |

Current manual-validation follow-up frontier:

```text
ARCH-021-COMMERCE-042
```

The Request-tab follow-up remains zero-provider-I/O. Request validation/preview answers what request will be constructed; the later Test-tab review will determine the separate live-provider test behaviour.

## Manual-validation follow-up — External HTTP Response tab

Response-tab manual review identified a separate bounded workstream. It is independent of COMMERCE-040..042 and may execute in parallel because it consumes only already-Complete Phase 3 capabilities plus its own response-task chain.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-043](COMMERCE-043-derive-visual-response-result-contract.md) | Derive Visual result schemas from projection authoring instead of separately maintained shape JSON | Complete | COMMERCE-016, COMMERCE-021, COMMERCE-039 |
| [COMMERCE-044](COMMERCE-044-validate-external-http-response-authoring.md) | Add Response-only authoritative Direct/Visual/JavaScript validation with Response-local diagnostics | Ready | COMMERCE-043, COMMERCE-019, COMMERCE-023 |
| [COMMERCE-045](COMMERCE-045-complete-external-http-response-tab-authoring.md) | Complete Response-tab Source-path, JavaScript panel, derived-contract and per-mode local-draft UX | Pending | COMMERCE-043, COMMERCE-044, COMMERCE-006, COMMERCE-039 |

Current Response-tab manual-validation frontier:

```text
ARCH-021-COMMERCE-044
```

The Response chain remains zero-provider-I/O. Visual result schemas are deterministically derived from Visual authoring; Direct/JavaScript sample-derived schema generation and real provider execution are deferred to the later Test-tab review. Errors remain visible in Response while all authoring tabs stay freely navigable.

### COMMERCE-043 Attempt 1 accepted — 2026-09-26

COMMERCE-043 is **Complete / Accepted, Attempt 1**. Visual OBJECT/LIST projected fields now carry bounded scalar result types, `omitIfMissing` deterministically controls requiredness, and one Commerce-owned helper derives the canonical OBJECT or `{ items: [...] }` LIST `resultSchema`. Compatible persisted Visual definitions reconstruct editable field types without new durable metadata; incompatible projection/schema pairs fail explicitly. Publication compatibility reuses the same rule, Visual mode no longer requires independently editable `Response shape JSON`, and Direct/JavaScript schema behavior remains unchanged. The submitted packet passed 41 focused Visual/UI/publication tests, 85 common Tool-authoring tests and 45 External authoring-validation tests, with targeted ESLint/diff checks clean and no task-owned type diagnostics. COMMERCE-044 is promoted to **Ready**; COMMERCE-045 remains Pending.


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
