## Architect Amendment — Shared Observability Runtime (2026-08-31)

**This amendment supersedes any conflicting service-local NodeSDK/provider/
exporter/bootstrap instructions earlier in this task.** Background still owns
worker/recovery/messaging/CommerceAgent semantic telemetry; generic runtime
plumbing is shared.

Do not resume implementation until:

```text
BACKGROUND-001 is Complete (actual worker entrypoints known)
ARCH-002-SHARED-010 is architect-accepted Complete
```

Then:

1. consume the exact published shared version from SHARED-010;
2. read `docs/observability/shared-observability-runtime.md`;
3. create one small preload/profile per actual production worker process:

```text
moda-shopify-event-worker
moda-recovery-worker
moda-messaging-worker
```

4. prefix each **real command produced by BACKGROUND-001** with its matching
   preload; do not invent a new worker entrypoint in this task;
5. final generic instrumentation is:

```text
BullMQ producer/consumer=true
Prisma=true where used
HTTP/fetch/Undici=true where external calls occur
```

6. construct BullMQ telemetry only through
   `@modainteract/moda-interact-shared/observability/bullmq` and pass it through
   Queue/Worker `telemetry` options;
7. use `.../observability/genai` for messaging/CommerceAgent agent/tool/turn
   helpers;
8. one inbound WhatsApp turn is one trace; never one trace for a whole customer
   conversation;
9. service-owned metrics must use bounded dimensions; arbitrary tool/agent/job/
   conversation/customer identifiers are prohibited metric attributes;
10. remove obsolete local provider/exporter/bootstrap logic only after parity is
    proven.

Reference code:
`docs/decisions/shared/ARCH-002/reference-observability/services/moda-interact-background/`.
