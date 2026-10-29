# ARCH-052 Shared Tasks

Architecture: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`
Owner: `moda_shared`
Coordinator: `moda_architect`

These are portable task definitions, **defined but not materialised**; the individual task YAML frontmatter is authoritative. Superseded tasks must never be executed.

**Attempt 8 contract review:** SHARED-002/005/006/008 now include complete proposed TypeScript/Zod source shapes and structural fixtures. Zod owns wire shape/type parsing only; Admin, Background, MCP and provider adapters own authorisation, eligibility, business consistency, product safety and final send decisions. SHARED-003 remains a publication-only gate. No consumer should introduce a parallel contract or infer unstated fields.

| Task | Bounded outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-052-SHARED-001](SHARED-001-define-canonical-selected-discount-contract.md) | Freeze discount authorization and delivered promotional offer in existing attempt JSON | Superseded | — |
| [ARCH-052-SHARED-002](SHARED-002-define-checkout-template-binding-contract.md) | Define exact WhatsApp semantic-key, target and binding schemas; service policy remains outside Zod | Ready | — |
| [ARCH-052-SHARED-003](SHARED-003-publish-initial-outreach-shared-contracts.md) | Publish the accepted initial-outreach contracts (including product search) | Pending | `ARCH-052-SHARED-002`, `ARCH-052-SHARED-005`, `ARCH-052-SHARED-006`, `ARCH-052-SHARED-008` |
| [ARCH-052-SHARED-004](SHARED-004-define-private-read-authentication-contract.md) | Define signed private recovery product-read request authentication | Superseded | — |
| [ARCH-052-SHARED-005](SHARED-005-define-discount-proof-wire-contract.md) | Create exact on-demand discount proof request/result shapes; runtime validates eligibility | Ready | — |
| [ARCH-052-SHARED-006](SHARED-006-define-outreach-mcp-discount-tool-contracts.md) | Create exact outreach MCP toolContext discriminator; reuse generic MCP results | Ready | — |
| [ARCH-052-SHARED-007](SHARED-007-reuse-commerce-runner-for-outreach-offer-choice.md) | Add outreach entrypoint to the existing Commerce runner | Superseded | — |
| [ARCH-052-SHARED-008](SHARED-008-define-product-search-and-alternative-promotion-contracts.md) | Extend existing product schema and add exact `commerce_get_product` input/output | Ready | — |
