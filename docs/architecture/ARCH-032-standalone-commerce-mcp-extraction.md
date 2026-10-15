# ARCH-032 — Standalone Commerce MCP Extraction

## Goal and invariant

Extract the existing private Commerce MCP endpoint into the independent
`moda-interact-mcp` repository, **without** removing, modifying or redirecting
the existing Commerce Studio MCP service until parity is proven and a
separate cutover is approved. Scope includes both Shopify and WooCommerce
shops; WooCommerce outbound REST credentials and grant authority remain
API-owned, not MCP-owned.

## Bounded domain ownership

- `moda_commerce`: tool authoring, publishing, previews, revision lifecycle.
- `moda_mcp`: private MCP protocol, runtime authorization, published release
  resolution and tool execution via explicit store connection interfaces.
- `moda_api`: WooCommerce REST-read authorization, encrypted grants,
  credential decryption and outbound broker; approved deterministic reads.
- `moda_shared`: canonical cross-service execution and publication contracts.
- `moda_background`: CommerceAgent client/orchestration; no change during
  extraction.
- `moda_gateway`: private Render service, deployment and routing; no public
  MCP domain and no early change to Background's `COMMERCE_MCP_URL`.
- `moda_database`: schema and migrations; no database edits in MCP-001.
- `moda_system_test`: black-box parity evidence for old/new MCP behaviour.

## Operational acceptance gate

Foundation MCP-001 provides Node/TypeScript startup, shared logging/OTel,
liveness and fail-closed readiness. It MUST respond 503 at `/api/mcp` until
the MCP protocol and authorization are implemented; `/health/ready` must
remain 503 until its actual dependencies have been verified.

Future extraction tasks must preserve authorisation/lease/entitlement and
published-revision semantics, plus MCP resources/prompts and zero eligible
tools behaviour; never infer platform from model parameters.

The separate Gateway deployment task can be planned now but must not
receive production traffic or redirect Background until end-to-end parity
evidence and explicit architect/developer sign-off. Gateway owns Render and
HAProxy only, not MCP runtime code.

## Task sequence

1. `ARCH-032-MCP-001`: standalone service foundation; additive only.
2. Subsequent MCP tasks: protocol and authorization, shared publication
   contract adoption, Shopify/Woo connection providers, execution parity.
3. `ARCH-032-GATEWAY-001`: private deployment wiring, gated until runtime
   readiness is meaningful. No traffic cutover.
4. System tests and separate approved cutover/removal tasks, to be defined
   after parity review.

No `docs/decisions/**/_index.md` reconciliation in this architecture session.


## Agreed 2026-10-12: mandatory platform execution policy

The MCP executor no longer owns fixed business-execution budgets. An explicit,
environment-scoped PostgreSQL **MCP Execution Policy** defines the required
`toolDeadlineMs`, `providerResponseTimeoutMs`, `maxProviderRequests` and
`maxResponseBytes`. No row or required value may be silently defaulted or seeded
by MCP. Admin provisions and audits policy; MCP reads the current policy and
uses it for both published calls and authorised Studio draft previews. HTTP
parsing, cancellation and tenant boundaries remain fixed technical protections.

Missing, invalid or unavailable policy fails closed before provider execution,
makes MCP readiness unavailable, writes a structured Shared log with a stable
reason and unique error ID, and attempts a **platform-wide** ARCH-033 generic
operational incident (null shop identity). Incident-write outage must not mask
the original policy error; it is logged separately. Repeated failures group by
environment and exact cause. Policy-limit exhaustion remains distinct from
missing-policy incidents. A new policy version must become effective without
a service redeploy. See the bounded policy tasks below.

## Agreed 2026-10-12: finish extracting Studio preview execution

Commerce Studio owns tool/feature authoring, GraphQL validation, publication
and orchestration of test conversations. Both published tests and frozen draft
previews must execute using the *same* standalone private MCP providers and
renderer as Background, with the same platform policy. Preview references are
server-resolved and bound to the selected administrator, shop and environment.
There is no separate preview-specific 30-minute TTL or second local execution
fallback. Existing Studio preview retention/closure remains authoritative.
Drafts never appear in ordinary published `tools/list` or become executable by
Background through draft references. Commerce's embedded MCP route/runtime is
removed only after the thin client has passed private-service parity checks.

This test-environment cutover keeps the existing trusted Render private-network
context assertion and the Background MCP protocol and `COMMERCE_MCP_URL` name.
Background URL changes and live cutover still require a separate verified
Gateway/developer checkpoint; this decision is not permission to redirect
traffic or remove fallback prematurely.

### Newly defined tasks (portable; not yet materialised)

| Task | Owner | Initial state | Depends on |
| --- | --- | --- | --- |
| ARCH-032-DATABASE-001 | moda_database | Ready | None |
| ARCH-032-ADMIN-001 | moda_admin | Pending | DATABASE-001 |
| ARCH-032-MCP-015 | moda_mcp | Pending | DATABASE-001 |
| ARCH-032-MCP-016 | moda_mcp | Pending | MCP-015 |
| ARCH-032-MCP-017 | moda_mcp | Ready | None (requires validated preview-core baseline) |
| ARCH-032-COMMERCE-001 | moda_commerce | Pending | MCP-017, MCP-016, ADMIN-001 |
| ARCH-032-COMMERCE-002 | moda_commerce | Pending | COMMERCE-001 |

Canonical task files determine execution eligibility; the previous ARCH-032
task YAML may still need explicit reconciliation with already validated patches.
Do not modify `docs/decisions/**/_index.md` until user sign-off.


## 2026-10-12 — final Commerce Studio extraction boundaries and prerequisites

- `runCommerceTurn()` and the CommerceAgent tool-call workflow stay in Shared; Commerce and Background supply a tool execution callback. Commerce Studio stays responsible for authoring, validation, publication, authenticated preview composition, model orchestration, Redis conversation/run state and the UI.
- Standalone MCP remains the only owner of tool provider execution, tool result rendering and configured execution policies. Commerce’s injected callback becomes a thin server-side private MCP SDK client; **no Commerce local execution fallback**.
- Studio selected-feature conversation tests can use a composition that is not the currently active shop release. Saved-tool tests may target draft revisions and use synthetic fixtures/External HTTP response samples. These MUST remain testable but MUST NOT appear in Background’s normal published `tools/list` or `tools/call`.
- Commerce freezes the selected definitions and writes a separately versioned immutable preview execution snapshot to PostgreSQL, using a canonical published Shared contract. Do not let MCP decode Commerce’s existing aggregate preview Redis key. MCP accepts only a short reference and loads/verifies owner, shop, environment, state, revision and hash server-side; callers cannot submit executable definitions during tool invocation.
- Preview snapshots have explicit CLOSE/invalidate lifecycle with **no arbitrary 30-minute TTL**; retain per-call cancellation and use the *same mandatory platform execution policy* as normal MCP calls. Fix the previously offered isolated preview core before wiring transport; that core does not appear in the 16:07 snapshot.
- Only after remote conversation, draft and fixture parity certification may Commerce remove its legacy `/api/mcp` route, `src/commerce/mcp` and proven-obsolete execution modules. Do not delete still-required authoring/publication/Shared runner/preview orchestration code.
- Background URL cutover is configuration-only and held until explicit approval and SYSTEM-TEST-001 evidence. Test environment before production; private ingress remains private.

### Dependency order (task IDs are defined, not yet claimed)

1. `ARCH-032-SHARED-001` -> `ARCH-032-SHARED-002` (frozen snapshot/reference contract + real publication).
2. `ARCH-032-DATABASE-002` (immutable preview snapshot store, depends on published Shared contract).
3. `ARCH-032-COMMERCE-003` (authenticated snapshot writer/close) and `ARCH-032-MCP-017` (private isolated preview transport) may then proceed in parallel.
4. `ARCH-032-MCP-018` provides fixture and response-sample execution parity within standalone MCP.
5. Separate execution policy chain: `ARCH-032-DATABASE-001`, `ARCH-032-ADMIN-001`, `ARCH-032-MCP-015`, `ARCH-032-MCP-016`. Missing or invalid policy fails closed, logs and attempts ARCH-033 generic incident reporting.
6. `ARCH-032-COMMERCE-001` changes only injected tool-execution callbacks to thin MCP client after preview/fixture and policy acceptance.
7. `ARCH-032-SYSTEM-TEST-001` certifies black-box Studio/Background parity; then `ARCH-032-COMMERCE-002` removes embedded Commerce MCP/executors.
8. `ARCH-032-GATEWAY-002` is a separately approved Render Test then production endpoint cutover, not an automatic result of previous tasks.

No decisions `_index.md` files may be created/updated until explicit architecture session closure.


## 2026-10-12 — AUTHORITATIVE CORRECTION: mock-first Commerce removal (supersedes remote-first Studio preview plan)

**This section overrides earlier 2026-10-12 language that requires a Commerce thin MCP client, immutable preview snapshots or parity with standalone MCP before removing Commerce's embedded service.** Those requirements are deferred until a separate future architecture review. Earlier task documents remain as historical definitions but are explicitly `blocked`; do not claim them in this phase.

User-directed development rule: **breaking removal is allowed**. Do not build compatibility wrappers, redirects, aliases or a deprecation period for the removed Commerce MCP server or local executor. Preserve functionality only for retained Commerce Studio authoring, publishing, test-conversation orchestration and deterministic fixture tests.

### Current phase — Commerce-only mock-first extraction

1. `ARCH-032-COMMERCE-001` (ready): define a deterministic Shared-result-compatible simulated tool executor, with explicit fixtures, strict failure for missing fixtures and zero real provider requests.
2. `ARCH-032-COMMERCE-002` (after 001): retain Shared `runCommerceTurn()` and Commerce model/conversation lifecycle; replace selected-shop conversation `tool.execute` callback with mock. No Commerce MCP client.
3. `ARCH-032-COMMERCE-003` (after 001; parallel with 002): replace saved draft/fixture tool tests and Policy Operation live-test action with clearly simulated or explicitly disabled paths, preserving pure authoring validation.
4. `ARCH-032-COMMERCE-004` (after 002+003): physically delete `app/api/mcp/route.ts`, `src/commerce/mcp/`, embedded server/authorization/provider execution assembly; move or remove runtime-only types according to retained authoring consumers. No redirect or shim.
5. `ARCH-032-COMMERCE-005` (after 004): remove obsolete dependencies and scripts, add a static no-MCP-in-Commerce boundary test and certify authoring, publication, conversations, single-tool fixtures and build.

The Shared CommerceAgent runner, Background `CommerceMcpClient`, standalone MCP production execution, existing Commerce Redis preview conversation lifecycle and all production publication contracts remain unchanged. **This phase intentionally tests only simulated tool results in Commerce Studio; it does NOT prove equivalent real-provider results.** Every Studio result must be visibly marked simulated and missing fixtures must fail explicitly.

### Independent / deferred work

- Independent, still active: mandatory platform MCP execution policy `ARCH-032-DATABASE-001`, `ARCH-032-ADMIN-001`, `ARCH-032-MCP-015`, `ARCH-032-MCP-016`. They do not block Commerce mock-first removal.
- Explicitly blocked/deferred: `ARCH-032-SHARED-001/002`, `ARCH-032-DATABASE-002`, `ARCH-032-MCP-017/018`, `ARCH-032-SYSTEM-TEST-001`, and `ARCH-032-GATEWAY-002`. Unblock only after a separate design and developer decision.
- No work in `moda-interact-background`, `moda-interact-mcp`, `moda-interact-shared`, `moda-interact-database`, Admin or Gateway is implied by the Commerce tasks. No `docs/decisions/**/_index.md` edits until explicit session closure.


## 2026-10-13 — Final Commerce Studio execution model and task reconciliation

**Authoritative override:** This section supersedes the previous mock-only and
remote-first Commerce Studio execution requirements above. Historical task
sequences remain documentary context, not new implementation instructions.

- Commerce Studio continues to author Features → Capabilities → Tools, validate
  and publish definitions, and drive the real Shared `runCommerceTurn()` with
  model invocation, selected-shop state and conversation history.
- **Local Preview (default):** a local MCP-*client-shaped* adapter discovers
  tools from the frozen selected-feature composition and executes those tool
  definitions against **real authorised providers** (including Shopify and
  External HTTP) directly, without contacting the standalone MCP server.
- **Live Test:** a thin client uses the private standalone MCP `tools/list` and
  `tools/call` flow for published eligible capabilities, like Background.
  Unpublished drafts must never be silently exposed through the production
  catalogue; failure to connect must never fall back to local execution.
- **Fixture mode:** explicit, deterministic simulated results remain available
  for isolated testing. Missing fixtures fail; simulated provenance is visible.
- The embedded Commerce MCP server and `/api/mcp` route remain **removed**.
  The remote client is not a new embedded server.
- Retain `createExternalIntegration()` and genuine External HTTP execution,
  authoring observation, credential management and existing live-test paths.
  The old Shopify Admin editor-specific Run Test/checkpoint is the particular
  retired UI pathway; Shopify real tool execution is **not** retired.
- Commerce Preview/Live/Fixture errors are logged through the Shared logger
  only. Commerce does not create ARCH-033 incidents. Standalone MCP independently
  owns its platform execution policy, fail-closed requirements and incident
  reporting.
- Breaking changes in development are permitted. Do not change Background,
  Shared runner, standalone MCP or unrelated ARCH-032 policy tasks from this
  Commerce documentation-only reconciliation.

### Commerce task administrative closure

`ARCH-032-COMMERCE-001` through `ARCH-032-COMMERCE-005` are set to
`status: complete` **at the developer's direction** after C001/C002/C003/C004
implementation work and C005 Attempt 1–6 extraction/correction patches. Their
Completion Reports record the actual validation available. This is not a claim
that the final assembled C005 Attempt 6 has a green full suite or passed
provider/MCP end-to-end certification. In particular, the last reported full
suite before Attempts 5–6 had 37 failures, and final reruns were not supplied.
Those checks remain outstanding for a separate verification pass.

Do not reconcile or edit `docs/decisions/**/_index.md` until explicit
architecture-session completion approval.


## 2026-10-15 — ARCH-032 snapshot reconciliation (review evidence; no task-state promotion)

The 2026-10-13 three-mode Commerce Studio decision remains the active execution
model: Local Preview runs real authorised tools locally without an embedded MCP
server; Live Test uses published capabilities through private standalone MCP;
Fixture execution is explicitly simulated. Older remote frozen-preview plans
remain historical and their tasks must not be claimed while deferred.

This review inspected `moda-interact-workspace(20261015-120806).zip`, rather than
the developer's canonical task branches. The snapshot contains 29 ARCH-032 task
files: 5 Complete (Commerce 001–005, developer administrative closure), 2 Ready,
15 Pending and 7 Blocked. Neither the early MCP source modules nor the private
Render service declarations constitute architect acceptance. MCP-002 and MCP-007
are referenced dependencies with no canonical task files in the snapshot.
Recover/reconcile their historical records before promoting dependent tasks.
Do not rewrite Completion Reports or mark tasks Complete without independent
worktree/implementation/review evidence.

The Messaging → Background → MCP system-test identified a missing MCP
`commerce://capabilities` resource registration. `ARCH-032-MCP-019` was defined
and implementation/correction patches were supplied separately, but acceptance
and final local validation are not established by this snapshot review. Further
static contract discrepancies require distinct work:

- MCP advertises `CommerceCapability.key` as `tools/list` name while Background
  and Commerce Live Test call by `toolDescriptor.name`. The values may differ;
  multiple capabilities may pin one tool. Maintain the underlying tool name for
  the Shared runner, and use a validated capability-key mapping at MCP boundaries
  with tenant/grant verification; decide/test exact deduplication before coding.
- MCP's `tools/call` returns JSON text `content` but both clients validate
  `structuredContent` as `CommerceToolResultSchema`. A bounded MCP result-envelope
  correction is needed, preserving `isError` and safe textual compatibility.
- Commerce Live Test currently uses direct HTTP JSON-RPC without a demonstrated
  SDK initialize handshake; verify protocol conformance, not just HTTP 200.

Proposed reviewable corrections, **not yet materialised or made Ready**:
`ARCH-032-MCP-020` for `structuredContent`, `ARCH-032-BACKGROUND-001` for tool
identity mapping and `ARCH-032-COMMERCE-006` for Live Test identity and SDK
transport parity. Then define terminal integrated `ARCH-032-SYSTEM-TEST-002` only
after accepted implementation/policy/infrastructure dependencies.

The mandatory execution-policy chain remains active and separately gated:
`DATABASE-001` → `ADMIN-001` and `MCP-015` → `MCP-016`. Snapshot MCP still uses
fixed execution constants. `GATEWAY-001` remains Pending in YAML although the
private MCP service appears in both Render blueprints: inspect task evidence
before any status correction. `GATEWAY-002` stays Blocked pending formal
environment-specific sign-off; when revised, remove its invalid dependency on
`SYSTEM-TEST-001`, since system-test tasks must be terminal. Require accepted
system-test evidence and developer permission as a cutover approval gate instead.

`SHARED-001/002`, `DATABASE-002`, `MCP-017/018` and `SYSTEM-TEST-001` are blocked
historical remote-preview work. They must be deliberately revised or superseded
under the latest model, not automatically unblocked. Commerce 001–005 remain
administratively Complete without asserting a final green full-suite run.

**No** `docs/decisions/**/_index.md` files, task statuses, implementation sources,
Git worktrees or deployment routing are changed by this reconciliation addendum.
Refer to `ARCH-032-architectural-reconciliation-20261015.md` for the complete
per-task inventory, evidence and proposed acceptance sequence. The report is a
portable review artifact, not a canonical Git document unless separately added.
