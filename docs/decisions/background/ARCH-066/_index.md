# ARCH-066 background tasks

Architecture: [decisions](../../../architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md). Normative amendments: [consumer contract](../../../architecture/ARCH-066-consumer-contract.md), [outreach contract](../../../architecture/ARCH-066-initial-outreach-contract.md).

| Task | Status | Dependencies |
|---|---|---|
| [ARCH-066-BACKGROUND-001](BACKGROUND-001-integrate-trusted-product-context-and-whatsapp-composer.md) | ready | ARCH-066-DATABASE-001, ARCH-066-SHARED-005, ARCH-066-MCP-001 |
| [ARCH-066-BACKGROUND-002](BACKGROUND-002-adopt-shared-checkout-outreach-evaluation.md) | ready (rework; prior Attempt1 preserved) | ARCH-066-SHARED-005, ARCH-066-BACKGROUND-001, ARCH-066-SHARED-012 |

Definitions amended; no task claimed or implementation accepted by this review. Completed5.6.0 baseline is preserved; pending consumers require new SHARED-005 artifact.

2026-11-08: SHARED-005 explicitly Complete at accepted Attempt1 (verified5.7.0). BACKGROUND-001 and COMMERCE-001 Ready/Attempt0/unclaimed; later consumers and system tests retain remaining dependency/manual gates. No task started.

2026-11-08: BACKGROUND001 Complete AcceptedAttempt2 atb9470dd27; BACKGROUND002 newly Ready Attempt0/unclaimed. Canonical dependency records materialized, no implementation worktree/claim created.

2026-11-08: BACKGROUND002 Attempt1 blocked on published Shared frozen-brand compatibility. SHARED011 Ready and012 Pending; no source acceptance/completion, downstream Commerce002/SystemTest002 remain gated.
