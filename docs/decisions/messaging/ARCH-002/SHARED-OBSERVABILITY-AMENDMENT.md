## Architect Amendment — Shared Observability Runtime (2026-08-31)

**This amendment supersedes any conflicting service-local NodeSDK/provider/
exporter/bootstrap instructions earlier in this task.** Messaging owns Meta/
WhatsApp ingress semantics; generic runtime plumbing is shared.

Do not resume implementation until `ARCH-002-SHARED-010` is architect-accepted
Complete.

Then:

1. consume the exact published shared version;
2. read `docs/observability/shared-observability-runtime.md`;
3. add a process preload with:

```js
initNodeObservability({
  serviceName: "moda-interact-messaging",
  instrument: { http: true, fetch: true, prisma: false },
});
```

4. preload before the existing React Router production entrypoint;
5. use `@modainteract/moda-interact-shared/observability/bullmq` for inbound
   message Queue publication and pass the shared telemetry object through the
   Queue's supported `telemetry` option;
6. preserve messaging-specific acceptance/failure/latency semantics using the
   global provider installed by shared runtime;
7. do not create local NodeSDK/provider/exporter/sampler or BullMQOtel helpers;
8. validate HTTP -> Queue trace continuity and failure isolation.

Reference code:
`docs/decisions/shared/ARCH-002/reference-observability/services/moda-interact-messaging/`.
