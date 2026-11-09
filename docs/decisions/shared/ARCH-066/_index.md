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

## Standalone identity correction

| Task | Status | Dependencies |
|---|---|---|
| ARCH-066-SHARED-007 | Superseded (scope withdrawn) | ARCH-066-SHARED-005 |

Canonical007 uniquely standalone; concurrent product-detail correction active009/010 preserved.

| ARCH-066-SHARED-008 | Superseded — do not publish | withdrawn checkout-led scope |

Explicit developer withdrawal supersedes historical standalone readiness/acceptance text; no successful completion or release implied.009/010 independent product-detail work unchanged.

## Frozen outreach binding correction — 2026-11-08
| Task | Status | Dependencies |
|---|---|---|
| SHARED-011 | Complete, Accepted Attempt1 | SHARED-010 Complete |
| SHARED-012 | Complete, Accepted Attempt1 | SHARED-010, SHARED-011 |
Four valid saved-brand bindings fail under immutable5.8.0; correction and publication separate. Canonical parent branches materialized/published, no implementation worktree/claim/release. Existing007/008 standalone withdrawal and009/010 identity preserved.

## Frozen outreach compatibility correction — 2026-11-08
| Task | Status | Dependencies |
|---|---|---|
| SHARED-011 | Complete, Accepted Attempt1 | SHARED-010 Complete |
| SHARED-012 | Complete, Accepted Attempt1 | SHARED-010, SHARED-011 |
Positive5.8.0 saved brand alt/dimension bindings refused; preserve semantic caps and strict host/Shared boundary.007/008 standalone scope remains withdrawn, no standalone package release. Definitions only, no implementation worktree/claim/release or consumer execution.
