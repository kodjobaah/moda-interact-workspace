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
