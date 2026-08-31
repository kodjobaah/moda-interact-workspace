import { initNodeObservability } from "@modainteract/moda-interact-shared/observability/node";

initNodeObservability({
  serviceName: "moda-interact-admin",
  instrument: { http: true, fetch: true, prisma: true },
});
