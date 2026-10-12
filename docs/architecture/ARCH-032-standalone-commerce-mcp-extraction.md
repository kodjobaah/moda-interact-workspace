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
