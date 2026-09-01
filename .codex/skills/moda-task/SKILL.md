---
name: moda-task
description: Launch a Moda Interact architecture task by task ID.
---

You are a task launcher only. Do not claim, implement or modify task state in
this launcher context.

Extract exactly one Moda Interact task ID from the invocation, e.g.
`ARCH-002-SHOPIFY-001`.

Establish the workspace root by walking upward only through the current parent
chain until `.nvmrc`, `.codex/agents` and
`docs/agent-task-execution-template.md` are present. Do not search the wider
filesystem.

Run:

```bash
python3 "$ROOT/scripts/start-agent-task.py" "$TASK_ID" --json
```

Read the returned JSON. `agent` identifies the configured logical Codex agent;
`prompt` is the complete rendered execution instruction.

Use the current Codex runtime's named custom-agent delegation mechanism to
invoke `agent` and pass `prompt` unchanged. Do not summarize or weaken it. If
this Codex surface cannot select the configured logical agent by name, stop and
report that named-agent delegation is unavailable; do not silently substitute a
generic worker with a different model/execution profile.
