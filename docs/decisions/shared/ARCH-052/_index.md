# ARCH-052 — Shared task index

Architecture: [`ARCH-052`](../../../architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md).

Assigned agent: `moda_shared`. Repository: `moda-interact-shared`. Coordinator: `moda_architect`.

Task definitions are **portable / not materialised** in the developer Git environment. Individual task YAML is authoritative for status.

| Task | Objective | Status | Depends on |
|---|---|---|---|
| [SHARED-001](SHARED-001-define-canonical-selected-discount-contract.md) | Define one shared merchant-selection and immutable-attempt snapshot contract | Ready | — |
| [SHARED-002](SHARED-002-define-checkout-template-binding-contract.md) | Define cross-service checkout summary and product-header binding contract | Ready | — |
| [SHARED-003](SHARED-003-publish-initial-outreach-shared-contracts.md) | Publish accepted initial-outreach Shared contracts | Pending | `ARCH-052-SHARED-001`, `ARCH-052-SHARED-002`, `ARCH-052-SHARED-004`, `ARCH-052-SHARED-005` |
| [SHARED-004](SHARED-004-define-private-read-authentication-contract.md) | Define signed private recovery product-read request authentication | Ready | — |
| [SHARED-005](SHARED-005-define-discount-proof-wire-contract.md) | Define strict version-one verified discount proof request and response | Ready | — |

Do not manually promote a dependent task until every dependency is marked `complete` in its individual task file and has an accepted review; external ARCH-049 dependencies use the same rule.
