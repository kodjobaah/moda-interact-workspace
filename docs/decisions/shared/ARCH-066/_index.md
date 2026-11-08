# ARCH-066 shared tasks

Architecture: [contract decisions](../../../architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md).

SHARED-001 accepted Attempt2 and SHARED-002 accepted Attempt1 explicitly developer-completed. SHARED-003 accepted Attempt1 Complete; exact5.6.0 published and verified.

| Task | Status | Dependencies |
|---|---|---|
| [ARCH-066-SHARED-001](SHARED-001-define-product-context-and-recoverable-lookup-contracts.md) | Complete | None |
| [ARCH-066-SHARED-002](SHARED-002-extract-pure-whatsapp-response-composition.md) | Complete | ARCH-066-SHARED-001 |
| [ARCH-066-SHARED-003](SHARED-003-publish-product-context-and-presentation-package.md) | Complete | ARCH-066-SHARED-001, ARCH-066-SHARED-002 |
| [ARCH-066-SHARED-004](SHARED-004-extract-read-only-initial-outreach-preview.md) | Pending | ARCH-066-SHARED-001, ARCH-066-SHARED-002 |

SHARED-003 Complete publishes immutable5.6.0 for the original conversational scope. SHARED-004 outreach requires a future separately defined publication gate; it is not included in5.6.0 and cannot amend accepted SHARED-003 retroactively. BACKGROUND-002 and outreach consumers remain held until that release/dependency amendment. No self-dependency or automatic execution is authorized.
