# ARCH-076 background tasks

Implementation authorized at the dependency frontier. Sender routing and allowance renewal remain independent. SYSTEM-TEST remains user-deferred.

| Task | Status | Dependencies |
| --- | --- | --- |
| [ARCH-076-BACKGROUND-001](BACKGROUND-001-allocate-and-release-recovery-senders.md) | complete | [ARCH-076-DATABASE-001] |
| [ARCH-076-BACKGROUND-002](BACKGROUND-002-pin-senders-through-provider-dispatch.md) | complete | [ARCH-076-BACKGROUND-001] |
| [ARCH-076-BACKGROUND-003](BACKGROUND-003-route-replies-and-status-by-sender.md) | complete | [ARCH-076-BACKGROUND-002] |
| [ARCH-076-BACKGROUND-004](BACKGROUND-004-resolve-same-shop-baskets-and-clarify-replies.md) | ready | [ARCH-076-BACKGROUND-003, ARCH-076-ADMIN-002, ARCH-076-ADMIN-003, ARCH-076-COMMERCE-001] |
| [ARCH-076-BACKGROUND-005](BACKGROUND-005-renew-funded-conversation-allowance.md) | complete | [ARCH-076-DATABASE-002] |
