import { context, trace, SpanStatusCode, type Attributes } from "@opentelemetry/api";

const TRACER_NAME = "@modainteract/moda-interact-shared/observability";

export function getActiveTraceId(): string | undefined {
  return trace.getSpan(context.active())?.spanContext().traceId;
}

export async function withObservedSpan<T>(
  name: string,
  attributes: Attributes,
  work: () => Promise<T>,
): Promise<T> {
  const tracer = trace.getTracer(TRACER_NAME);
  return tracer.startActiveSpan(name, { attributes }, async (span) => {
    try {
      const result = await work();
      span.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (error) {
      span.recordException(error instanceof Error ? error : new Error(String(error)));
      span.setStatus({ code: SpanStatusCode.ERROR });
      throw error;
    } finally {
      span.end();
    }
  });
}
