# ARCH-010 — Shared

| Task | Status | Purpose |
|---|---|---|
| ARCH-010-SHARED-001 | Complete | Define the canonical BullMQ subscription-reconciliation queue/job payload/deterministic job ID and App Pricing billing-period drain constant. |
| ARCH-010-SHARED-002 | Complete | Publish the accepted Shared reconciliation contract for Shopify/Background consumers as part of `@modainteract/moda-interact-shared@0.10.0`. |
| ARCH-010-SHARED-003 | Complete | Add the canonical recovery-capacity-exhausted merchant system-message code/source-key contract. |
| ARCH-010-SHARED-004 | Complete | Publication satisfied by the coordinated `0.10.0` co-release containing the accepted SHARED-003 contract. |
| ARCH-010-SHARED-005 | Complete | Add canonical merchant billing system-message codes for top-up refund request/completion/rejection. |
| ARCH-010-SHARED-006 | Complete | Publication satisfied by the coordinated `0.10.0` co-release containing the accepted SHARED-005 contract. |

All ARCH-010 Shared work is complete.

The coordinated published release is:

`@modainteract/moda-interact-shared@0.10.0`

Published shasum:

`219601ddc1689f5cbeb6a8b4ab82326445b16654`

SHARED-004 and SHARED-006 are Complete rather than Superseded because their required
publication outcomes were actually achieved by the same coordinated release. No
second semantically identical npm publication is required.
