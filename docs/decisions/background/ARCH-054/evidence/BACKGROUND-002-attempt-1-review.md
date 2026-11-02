# BACKGROUND-002 Attempt 1 architect race reproduction

Implementation: `35772c5b3232c5fe7a7afbc523e2762e28068177`. Node 24.19.0. Run on 2 November 2026 in the canonical implementation worktree. This isolated diagnostic uses the existing processor test harness; it proves stale admission reaches the delivery boundary. Source inspection independently establishes that the real delivery/final permit has no original inbound-version comparison. It does not claim an actual Meta call occurred.

The test temporarily used `tests/unit/services/arch054-bg002-review-race.test.ts`; it was removed after the run. No implementation changes retained.

## Reproduction

```typescript
import { describe, expect, it, vi } from "vitest";
import type { RenderConversationResponseInput, WrapperRenderResult } from "../../../src/services/conversation-wrappers/contracts.js";

vi.mock("../../../src/lib/db.js", () => ({ default: {} }));
vi.mock(
  "../../../src/services/outbound-whatsapp-admission.service.js",
  () => ({
    runCommerceAgentAfterAdmission: async (input: any) => {
      if (input.admission.terminal) {
        await input.sendPreparedText({
          ...input.admission,
          to: input.to,
          text: "terminal response",
        });
        return null;
      }
      const result = await input.runAgent(input.context);
      return result;
    },
  }),
);

import {
  ConversationTurnProcessor,
  PROCESSING_LEASE_MS,
} from "../../../src/services/conversation-turn-processor.service.js";

import { registerSchedulingCases } from "./conversation-turn-processor/facade-scheduling.cases.js";
import { registerClaimAndStateCases } from "./conversation-turn-processor/facade-claims-and-state.cases.js";
import { registerContextCases } from "./conversation-turn-processor/facade-context.cases.js";
import { registerAbuseAdmissionCases } from "./conversation-turn-processor/facade-abuse-admission.cases.js";
import { registerOutboundCases } from "./conversation-turn-processor/facade-outbound.cases.js";
import { registerAgentRaceCases } from "./conversation-turn-processor/facade-agent-races.cases.js";
import { registerAiWrapperCases } from "./conversation-turn-processor/ai-wrapper.cases.js";

const first = new Date("2026-09-08T12:00:00.000Z");

function state(overrides: Partial<any> = {}) {
  return {
    inboundVersion: 3,
    lastProcessedVersion: 0,
    lastInboundAt: new Date(first.getTime() + 3_000),
    pendingTurnStartedAt: first,
    processingInboundVersion: null,
    processingStartedAt: null,
    ...overrides,
  };
}

function harness(overrides: Partial<any> = {}) {
  const queue = { add: vi.fn().mockResolvedValue(undefined) };
  const logger = {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    child: vi.fn(),
  };
  logger.child.mockReturnValue(logger);
  const conversation = {
    getTurnState: vi.fn().mockResolvedValue(state()),
    claimTurn: vi.fn().mockResolvedValue(true),
    completeTurn: vi.fn().mockResolvedValue(true),
    releaseTurn: vi.fn().mockResolvedValue(undefined),
    suppressStaleTurn: vi.fn().mockResolvedValue(true),
    hasChanged: vi.fn().mockResolvedValue(false),
    applyDetectedLanguage: vi.fn().mockResolvedValue(true),
  };
  const admission = {
    reserve: vi.fn().mockResolvedValue({
      kind: "admitted",
      messageId: "message-1",
      conversationId: "conversation-1",
      terminal: false,
    }),
    sendPreparedText: vi.fn().mockResolvedValue({
      kind: "admitted",
      messageId: "message-1",
      conversationId: "conversation-1",
      terminal: false,
    }),
    failPrepared: vi.fn().mockResolvedValue(undefined),
  };
  const abuseAdmission = {
    admitSettledTurn: vi.fn().mockResolvedValue({ kind: "allowed" }),
  };
  const aiWrapper = {
    renderConversationResponse: vi.fn(async (input: RenderConversationResponseInput): Promise<WrapperRenderResult> => ({
      kind: "no-wrapper" as const, body: input.responseBody, reason: "NOT_CONFIGURED" as const,
    })),
  };
  const runAgent = vi.fn().mockResolvedValue({
    replyText: "reply",
    detectedLanguageTag: null,
    detectedLanguageConfidence: null,
  });
  const loaded = {
    shopId: "shop-1",
    to: "+447700900000",
    customerPhone: "+447700900000",
    conversationType: "PRODUCT_SUPPORT" as const,
    checkoutRecoveryId: null,
    hasReplyContext: false,
    context: { conversation: { messages: [{ role: "user", content: "Hi" }] } },
    languageMessage: "Hi",
  };
  const now = overrides.now ?? (() => new Date(first.getTime() + 20_000));
  const runtimeConfig = overrides.runtimeConfig ?? {
    current: vi.fn().mockReturnValue({
      conversationQuietWindowMs: 3_000,
      conversationMaxSettleWindowMs: 10_000,
    }),
  };
  const processor = new ConversationTurnProcessor({
    queue,
    conversation,
    admission,
    abuseAdmission,
    loadTurn: vi.fn().mockResolvedValue(loaded),
    runAgent,
    aiWrapper,
    getResult: (result: any) => result,
    now,
    runtimeConfig,
    logger,
  });

  return {
    processor,
    queue,
    conversation,
    admission,
    abuseAdmission,
    runAgent,
    aiWrapper,
    loaded,
    runtimeConfig,
    logger,
    ...overrides,
  };
}


it("review: suppresses a version change during the final ownership await", async () => {
 const t = harness(); let version = 3;
 t.loaded.checkoutRecoveryId = "recovery";
 t.conversation.getTurnState.mockImplementation(async () => state({inboundVersion:version, pendingAiControlRevision:2, controlRevision:2, pendingAiNotBeforeAt:first}));
 t.conversation.hasChanged.mockImplementation(async () => version !== 3);
 t.conversation.completeTurn.mockImplementation(async () => version === 3);
 const ownership = {readTurnOwnership:vi.fn(), checkAutomatedTurn:vi.fn(async ({phase}) => {
   if(phase === "before-provider") version = 4; // customer ingress commits during this DB await
   return {kind:"allowed"}; // same AI mode and control revision, as in production
 })};
 const processor = new ConversationTurnProcessor({queue:t.queue, conversation:t.conversation, admission:t.admission, abuseAdmission:t.abuseAdmission, ownership,
 loadTurn:async()=>t.loaded, runAgent:t.runAgent, aiWrapper:t.aiWrapper, getResult:(x:any)=>x,
 now:()=>new Date(first.getTime()+20_000), runtimeConfig:t.runtimeConfig, logger:t.logger});
 await processor.process({conversationId:"conversation-1",observedVersion:3});
 expect(version).toBe(4);
 expect(t.admission.sendPreparedText).not.toHaveBeenCalled();
});

```

## Result

```text

> worker-kwadwos-gpt@1.0.0 test
> vitest run --reporter=dot tests/unit/services/arch054-bg002-review-race.test.ts


 RUN  v4.1.11 /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-054-BACKGROUND-002

x

⎯⎯⎯⎯⎯⎯⎯ Failed Tests 1 ⎯⎯⎯⎯⎯⎯⎯

 FAIL  tests/unit/services/arch054-bg002-review-race.test.ts > review: suppresses a version change during the final ownership await
AssertionError: expected "vi.fn()" to not be called at all, but actually been called 1 times

Received:

  1st vi.fn() call:

    Array [
      Object {
        "conversationId": "conversation-1",
        "expectedControlRevision": 2,
        "kind": "admitted",
        "messageId": "message-1",
        "terminal": false,
        "text": "reply",
        "to": "+447700900000",
      },
    ]


Number of calls: 1

 ❯ tests/unit/services/arch054-bg002-review-race.test.ts:159:43
    157|  await processor.process({conversationId:"conversation-1",observedVers…
    158|  expect(version).toBe(4);
    159|  expect(t.admission.sendPreparedText).not.toHaveBeenCalled();
       |                                           ^
    160| });
    161|

⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[1/1]⎯


 Test Files  1 failed (1)
      Tests  1 failed (1)
   Start at  15:10:14
   Duration  6.62s (transform 344ms, setup 0ms, import 4.87s, tests 80ms, environment 0ms)


```
