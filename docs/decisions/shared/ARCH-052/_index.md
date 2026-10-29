# ARCH-052 Shared Tasks

Architecture: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`
Owner: `moda_shared`
Coordinator: `moda_architect`

These are portable task definitions, **defined but not materialised**; the individual task YAML frontmatter is authoritative. Superseded tasks must never be executed.

| Task | Bounded outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-052-SHARED-001](SHARED-001-define-canonical-selected-discount-contract.md) | Freeze discount authorization and delivered promotional offer in existing attempt JSON | Superseded | — |
| [ARCH-052-SHARED-002](SHARED-002-define-checkout-template-binding-contract.md) | Define checkout and alternative-promotion WhatsApp bindings | Ready | — |
| [ARCH-052-SHARED-003](SHARED-003-publish-initial-outreach-shared-contracts.md) | Publish the accepted initial-outreach contracts (including product search) | Pending | `ARCH-052-SHARED-002`, `ARCH-052-SHARED-005`, `ARCH-052-SHARED-006`, `ARCH-052-SHARED-008` |
| [ARCH-052-SHARED-004](SHARED-004-define-private-read-authentication-contract.md) | Define signed private recovery product-read request authentication | Superseded | — |
| [ARCH-052-SHARED-005](SHARED-005-define-discount-proof-wire-contract.md) | Define a typed provider discount-evidence payload for on-demand MCP calls | Ready | — |
| [ARCH-052-SHARED-006](SHARED-006-define-outreach-mcp-discount-tool-contracts.md) | Define the minimal outreach MCP execution-context contract | Ready | — |
| [ARCH-052-SHARED-007](SHARED-007-reuse-commerce-runner-for-outreach-offer-choice.md) | Add outreach entrypoint to the existing Commerce runner | Superseded | — |
| [ARCH-052-SHARED-008](SHARED-008-define-product-search-and-alternative-promotion-contracts.md) | Define platform-neutral product search and exact-product MCP contracts | Ready | — |
