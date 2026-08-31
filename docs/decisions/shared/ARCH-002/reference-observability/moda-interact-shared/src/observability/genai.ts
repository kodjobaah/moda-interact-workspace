import { metrics } from "@opentelemetry/api";
import { withObservedSpan } from "./index.js";

const meter = metrics.getMeter("@modainteract/moda-interact-shared/observability/genai");
const agentDuration = meter.createHistogram("moda.agent.invocation.duration_ms", { unit: "ms" });
const toolDuration = meter.createHistogram("moda.agent.tool.duration_ms", { unit: "ms" });
const turnDuration = meter.createHistogram("moda.conversation.turn.duration_ms", { unit: "ms" });

export type AgentObservation = {
  agentName: string;
  provider?: string;
  model?: string;
};

export async function observeAgentInvocation<T>(
  observation: AgentObservation,
  work: () => Promise<T>,
): Promise<T> {
  const started = performance.now();
  try {
    return await withObservedSpan(
      `invoke_agent ${boundedSpanValue(observation.agentName)}`,
      compact({
        "gen_ai.operation.name": "invoke_agent",
        "gen_ai.agent.name": boundedSpanValue(observation.agentName),
        "gen_ai.provider.name": boundedSpanValue(observation.provider),
        "gen_ai.request.model": boundedSpanValue(observation.model),
      }),
      work,
    );
  } finally {
    // Deliberately no arbitrary agent/model metric labels. The histogram name
    // already describes the operation and keeps the series cardinality bounded.
    agentDuration.record(performance.now() - started);
  }
}

export async function observeAgentTool<T>(
  toolName: string,
  work: () => Promise<T>,
): Promise<T> {
  const started = performance.now();
  const safeToolName = boundedSpanValue(toolName) ?? "unknown";
  try {
    return await withObservedSpan(
      `execute_tool ${safeToolName}`,
      {
        "gen_ai.operation.name": "execute_tool",
        "gen_ai.tool.name": safeToolName,
      },
      work,
    );
  } finally {
    // Deliberately no arbitrary tool-name metric label.
    toolDuration.record(performance.now() - started);
  }
}

export async function observeConversationTurn<T>(
  channel: "whatsapp" | "other",
  work: () => Promise<T>,
): Promise<T> {
  const started = performance.now();
  try {
    return await withObservedSpan(
      `conversation.turn ${channel}`,
      { "moda.messaging.channel": channel },
      work,
    );
  } finally {
    // `channel` is a deliberately closed low-cardinality vocabulary.
    turnDuration.record(performance.now() - started, { channel });
  }
}

function boundedSpanValue(value: string | undefined): string | undefined {
  if (value === undefined) return undefined;
  const bounded = value.trim().slice(0, 80);
  return bounded || undefined;
}

function compact(input: Record<string, string | undefined>): Record<string, string> {
  return Object.fromEntries(
    Object.entries(input).filter(([, value]) => value !== undefined),
  ) as Record<string, string>;
}
