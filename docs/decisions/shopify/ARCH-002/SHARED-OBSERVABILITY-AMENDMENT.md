## Architect Amendment — Shared Observability Runtime (2026-08-31)

**This amendment supersedes any conflicting service-local NodeSDK/provider/
exporter/bootstrap instructions earlier in this task.** Shopify still owns its
business-semantic webhook spans/metrics; it no longer owns generic runtime
plumbing.

Do not resume implementation until `ARCH-002-SHARED-010` is architect-accepted
Complete and its exact published package version is recorded.

Then:

1. install/use that exact shared package version;
2. read `docs/observability/shared-observability-runtime.md`;
3. add a repository-owned preload importing
   `@modainteract/moda-interact-shared/observability/node`;
4. use the final profile:

```js
initNodeObservability({
  serviceName: "moda-interact",
  instrument: { http: true, fetch: true, prisma: true },
});
```

5. preload it before the existing React Router production entrypoint:

```text
node --import ./observability.mjs ./node_modules/@react-router/serve/bin.js ./build/server/index.js
```

6. where Shopify publishes BullMQ jobs, use
   `@modainteract/moda-interact-shared/observability/bullmq` and pass the shared
   telemetry object through the Queue's supported `telemetry` option;
7. preserve Shopify-specific acceptance/latency/error semantics using the global
   providers installed by shared runtime;
8. remove obsolete local heavy OTel provider/exporter/bootstrap modules only
   after equivalent shared behaviour is proven;
9. do not add Prisma/BullMQ/HTTP exporters or sampler logic locally.

Reference code:
`docs/decisions/shared/ARCH-002/reference-observability/services/moda-interact/`.
