# ARCH-014 background tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-014-BACKGROUND-001](BACKGROUND-001-runtime-config-and-distributed-lease-foundation.md) | complete | Establish monotonic runtime-config observation, fenced DB leases, and dynamic non-overlapping leased scheduling. |
| [ARCH-014-BACKGROUND-002](BACKGROUND-002-billing-and-recovery-runtime-controls.md) | complete | Apply runtime intervals/batches/retries to billing and recovery while preserving billing and merchant recovery invariants. |
| [ARCH-014-BACKGROUND-003](BACKGROUND-003-translation-runtime-controls.md) | ready | Move translation scheduling/batching/retry tuning from environment variables to the shared runtime configuration. |
| [ARCH-014-BACKGROUND-004](BACKGROUND-004-messaging-abuse-runtime-controls.md) | pending | Apply runtime messaging settle timing and approved WhatsApp abuse-limit controls using last-known-good configuration. |
| [ARCH-014-BACKGROUND-005](BACKGROUND-005-fleet-wide-bullmq-concurrency.md) | pending | Enforce fleet-wide BullMQ queue concurrency across horizontally scaled worker replicas. |
