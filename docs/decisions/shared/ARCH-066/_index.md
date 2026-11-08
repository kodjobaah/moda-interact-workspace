# ARCH-066 shared tasks

Architecture: [decisions](../../../architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md). Normative amendments: [consumer contract](../../../architecture/ARCH-066-consumer-contract.md), [outreach contract](../../../architecture/ARCH-066-initial-outreach-contract.md).

| Task | Status | Dependencies |
|---|---|---|
| [ARCH-066-SHARED-001](SHARED-001-define-product-context-and-recoverable-lookup-contracts.md) | complete | None |
| [ARCH-066-SHARED-002](SHARED-002-extract-pure-whatsapp-response-composition.md) | complete | ARCH-066-SHARED-001 |
| [ARCH-066-SHARED-003](SHARED-003-publish-product-context-and-presentation-package.md) | complete | ARCH-066-SHARED-001, ARCH-066-SHARED-002 |
| [ARCH-066-SHARED-004](SHARED-004-extract-read-only-initial-outreach-preview.md) | complete | ARCH-066-SHARED-001, ARCH-066-SHARED-002, ARCH-066-SHARED-006 |
| [ARCH-066-SHARED-005](SHARED-005-publish-initial-outreach-contract.md) | complete | ARCH-066-SHARED-004, ARCH-066-SHARED-006 |
| [ARCH-066-SHARED-006](SHARED-006-add-generic-merchant-product-facts.md) | complete | ARCH-066-SHARED-003 |

Definitions amended; no task claimed or implementation accepted by this review. Completed5.6.0 baseline is preserved; pending consumers require new SHARED-005 artifact.

2026-11-08: SHARED-006 accepted Attempt1 explicitly Complete; SHARED-004 newly Ready/unclaimed; SHARED-005 remains Pending. No publication or automatic execution.

2026-11-08: SHARED-005 explicitly Complete at accepted Attempt1 (verified5.7.0). BACKGROUND-001 and COMMERCE-001 Ready/Attempt0/unclaimed; later consumers and system tests retain remaining dependency/manual gates. No task started.

## Product detail selection correction
| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| ARCH-066-SHARED-009 | Complete public model selection contract | In Progress | ARCH-066-SHARED-005 |
| ARCH-066-SHARED-010 | Publish accepted immutable correction | Pending | ARCH-066-SHARED-005, ARCH-066-SHARED-009 |
