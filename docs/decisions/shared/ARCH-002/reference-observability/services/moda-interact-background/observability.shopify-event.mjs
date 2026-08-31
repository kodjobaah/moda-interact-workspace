import { initNodeObservability } from "@modainteract/moda-interact-shared/observability/node";

initNodeObservability({
  serviceName: "moda-shopify-event-worker",
  instrument: { http: true, fetch: true, prisma: true },
});
