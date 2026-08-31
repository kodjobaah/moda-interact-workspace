import {
  observeAgentInvocation,
  observeAgentTool,
  observeConversationTurn,
} from "@modainteract/moda-interact-shared/observability/genai";

export async function processWhatsAppTurn() {
  return observeConversationTurn("whatsapp", async () => {
    return observeAgentInvocation(
      { agentName: "commerce-agent", provider: "deepseek", model: process.env.LLM_MODEL },
      async () => {
        // Wrap individual agent tool calls, not the whole customer conversation.
        return observeAgentTool("shopify.lookup", async () => {
          // existing tool invocation here
        });
      },
    );
  });
}
