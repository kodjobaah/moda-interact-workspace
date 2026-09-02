## Architect Amendment — Shared Observability Runtime (2026-08-31)

**This amendment supersedes any conflicting service-local NodeSDK/provider/
exporter/bootstrap instructions earlier in this task.** Admin owns only additional Moda-specific request/database semantic telemetry;
generic runtime plumbing and equivalent framework/OpenTelemetry technical
signals are reused rather than duplicated.

Do not resume implementation until `ARCH-002-SHARED-010` is architect-accepted
Complete.

Then:

1. consume the exact published shared version;
2. read `docs/observability/shared-observability-runtime.md`;
3. add a process preload with:

```js
initNodeObservability({
  serviceName: "moda-interact-admin",
  instrument: { http: true, fetch: true, prisma: true },
});
```

4. for the current Next.js production shape, preload before the Next CLI:

```text
node --import ./observability.mjs ./node_modules/next/dist/bin/next start
```

5. preserve only admin-specific semantic telemetry that adds Moda domain meaning
   not already supplied by approved framework/OpenTelemetry instrumentation;
   do not create parallel generic HTTP request count/duration/status metrics;
6. remove obsolete local provider/exporter/bootstrap logic only after parity is
   proven;
7. do not put Grafana embedding/presentation code into the shared runtime;
8. validate tenant/admin data safety and database telemetry sensitivity.

Reference code:
`docs/decisions/shared/ARCH-002/reference-observability/services/moda-interact-admin/`.
