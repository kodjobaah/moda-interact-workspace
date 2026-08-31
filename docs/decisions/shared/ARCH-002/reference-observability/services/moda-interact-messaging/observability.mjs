import { initNodeObservability } from "@modainteract/moda-interact-shared/observability/node";

initNodeObservability({
  serviceName: "moda-interact-messaging",
  instrument: { http: true, fetch: true, prisma: false },
});
