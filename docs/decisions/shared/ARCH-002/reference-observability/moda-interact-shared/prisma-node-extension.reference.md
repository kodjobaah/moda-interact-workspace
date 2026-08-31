# SHARED-008 Prisma extension to the accepted Node runtime

SHARED-007 deliberately ships the base `node.ts` without Prisma.

After SHARED-007 is accepted, SHARED-008 may extend that file with the following
bounded change:

```ts
import { PrismaInstrumentation } from "@prisma/instrumentation";

type InstrumentProfile = {
  http?: boolean;
  fetch?: boolean;
  prisma?: boolean;
};

// while building the instrumentation list, before sdk.start()
if (profile.prisma) {
  instrumentations.push(new PrismaInstrumentation());
}
```

The final package published by SHARED-010 therefore supports `prisma: true`, but
that support is owned and validated by SHARED-008.

Do not move BullMQ into the Node auto-instrumentation list. BullMQ uses the
shared `createBullMQTelemetry()` adapter and BullMQ's supported Queue/Worker
`telemetry` option.
