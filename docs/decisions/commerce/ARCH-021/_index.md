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
| [COMMERCE-017](COMMERCE-017-implement-request-javascript-processor.md) | Implement bounded `buildRequest({args})` QuickJS processor | Blocked | COMMERCE-016, ARCH-020-COMMERCE-029, 026 |
| [COMMERCE-018](COMMERCE-018-implement-shopify-admin-graphql-compiler.md) | Implement pinned Shopify Admin GraphQL 2026-07 compiler + toolkit oracle | Blocked | COMMERCE-016, ARCH-020-COMMERCE-011 |
| [COMMERCE-019](COMMERCE-019-implement-phase3-tool-authoring-validation.md) | Establish common validation/auth contract and `LIVE_TEST_REQUIRED` publication gate | Blocked | COMMERCE-016, ARCH-020-COMMERCE-030 |
| [COMMERCE-020](COMMERCE-020-extract-tool-authoring-domain.md) | Extract Tool authoring domain from StudioWorkspace | Blocked | COMMERCE-016, COMMERCE-005, 006 |
| [COMMERCE-021](COMMERCE-021-complete-external-http-authoring-ui.md) | Complete External HTTP request/response authoring UI | Blocked | COMMERCE-019, 020, 023, COMMERCE-005, 006 |
| [COMMERCE-022](COMMERCE-022-build-shopify-admin-tool-authoring-ui.md) | Build Shopify Admin GraphQL authoring UI | Blocked | COMMERCE-019, 020, 024 |
| [COMMERCE-023](COMMERCE-023-implement-external-http-authoring-validation.md) | Implement External HTTP validation and safe request preview | Blocked | COMMERCE-016, 017, 019, ARCH-020-COMMERCE-030 |
| [COMMERCE-024](COMMERCE-024-implement-shopify-admin-authoring-validation.md) | Implement Shopify Admin GraphQL authoring validation | Blocked | COMMERCE-016, 018, 019 |

Phase 3 is Commerce-owned. Shared remains unchanged at exact `0.14.2`; no Phase 3 Shared publication is required.

```text
COMMERCE-016 is architect-accepted Complete.
Phase 3 is paused for the pre-Phase-3 simplification checkpoint. COMMERCE-017 through COMMERCE-024 are Blocked until architect reconciliation after the checkpoint; COMMERCE-016 remains Complete.
```



## Pre-Phase-3 simplification checkpoint — 2026-09-24

The checkpoint reduces Phase-2 configuration/reconciliation complexity before further Tool authoring. It preserves model catalogue, prompt revisions, prompt-template categories, immutable published artifacts, capabilities/releases/grants, server-owned credentials and future merchant Studio authorization. Errors must remain visible and transport-level uncertainty must be reconcilable through the UI; ordinary failures must not be swallowed into a generic unknown state.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-025](COMMERCE-025-simplify-agent-configuration-services.md) | Simplify Agent Configuration services and reconciliation | Complete | DATABASE-002, COMMERCE-007, 009, 010 |
| [COMMERCE-026](COMMERCE-026-simplify-prompt-template-authoring.md) | Simplify prompt-template authoring while retaining categories | Complete | DATABASE-002, COMMERCE-008, 015 |
| [COMMERCE-027](COMMERCE-027-unify-authjs-studio-authorization.md) | Unify Auth.js authorization across PlatformAdmin and shop-scoped merchant access | Complete | DATABASE-002 |
| [COMMERCE-028](COMMERCE-028-simplify-agent-configuration-ui-and-reconciliation.md) | Simplify Agent Configuration UI and explicit reconciliation | Pending | COMMERCE-025, 026, 027, 011..014 |
| [COMMERCE-029](COMMERCE-029-remove-production-studio-service-function-props.md) | Remove production function-valued Studio service props | Pending | COMMERCE-028, COMMERCE-001..006 |
| [COMMERCE-030](COMMERCE-030-simplify-private-mcp-authentication.md) | Remove application-layer auth from private MCP; keep DB authorization | Complete | ARCH-020-COMMERCE-024 |

Current checkpoint frontier:

```text
ARCH-021-COMMERCE-027
ARCH-021-BACKGROUND-001
```

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
