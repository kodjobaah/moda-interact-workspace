---
name: moda-task
description: Launch a Moda Interact architecture task by task ID.
disable-model-invocation: true
---

You are a task launcher only. Do not claim, implement or modify task state in
this launcher context.

Extract exactly one Moda Interact task ID from the invocation, e.g.
`ARCH-002-SHOPIFY-001`.

Establish the workspace root by walking upward only through the current parent
chain until `.nvmrc`, `.claude/agents` and
`docs/agent-task-execution-template.md` are present. Do not search the wider
filesystem.

Run:

```bash
python3 "$ROOT/scripts/start-agent-task.py" "$TASK_ID" --json
```

Read the returned JSON. `agent` is the logical Moda agent; `prompt` is the
complete rendered execution instruction.

In Claude Code, invoke the named custom subagent from `.claude/agents` and pass
`prompt` unchanged. In GitHub Copilot, where the Claude skill may be reused but
that named Claude subagent mechanism is not available, execute in the current
Agent Mode context only after reading the returned logical agent definition and
following its ownership/rules.

Do not summarize or weaken `prompt`. If the required execution/delegation
mechanism is unavailable, report that limitation instead of pretending an agent
was launched.
