# ARCH-014 system-test tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-014-SYSTEM-TEST-001](SYSTEM-TEST-001-admin-to-merchant-pricing.md) | ready | Terminal/developer-gated MerchantPricing validation is Ready after accepted ADMIN-006 pre-populated XLSX workflow; developer must invoke it explicitly. |
| [ARCH-014-SYSTEM-TEST-002](SYSTEM-TEST-002-multilingual-promotions.md) | ready | Terminal multilingual promotion XLSX -> 20-locale persistence -> exact merchant-locale validation; now also waits for ADMIN-010 parser hardening. |
| [ARCH-014-SYSTEM-TEST-003](SYSTEM-TEST-003-background-runtime-controls-horizontal-scaling.md) | pending | Terminal validation of version-safe runtime controls, retained monotonic leases, one global cadence window, last-known-good authority and fleet-wide BullMQ concurrency. |
