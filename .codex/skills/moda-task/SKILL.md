---
name: moda-task
description: Launch a Moda Interact architecture task by task ID.
disable-model-invocation: true
---

You begin in a task-launcher phase.

The launcher phase exists only to resolve authoritative routing and prepare the
handoff. While that phase is active, do not claim, implement, modify task state
or perform architect review.

**A successful resolver response does not finish the `/moda-task` invocation.**
After successful resolution, continue immediately to the `
## Canonical executor identity

The resolved logical agent must use the workspace executor normalization policy:

```text
docs/agent-executor-normalization-policy.md
```

Before claiming, normalize the execution surface to exactly one of:

```text
copilot
codex
claude
continue
```

Required mappings include:

```text
GitHub Copilot / github-copilot / copilot -> copilot
Codex                                  -> codex
Claude Code / claude-code / claude     -> claude
Continue                               -> continue
```

Do not store raw provider/runtime labels in task YAML.

For GitHub Copilot Agent Mode specifically:

```yaml
executor: copilot
```

not:

```yaml
executor: github-copilot
```

When an existing active claim uses an alias-equivalent value, treat it as the
same executor identity rather than as a competing claim.


## Handoff` section.
Do not return a final response merely stating that routing succeeded or that no
claim/implementation was performed.

Extract exactly one fully qualified Moda Interact task ID from the invocation,
for example `ARCH-002-SHOPIFY-001`.

## Mandatory first action

After extracting `TASK_ID`, your **first tool action MUST** invoke the
deterministic resolver.

Before that action, do NOT:

- search/glob/grep for the task ID or task file;
- inspect implementation repositories;
- inspect Git history or VS Code/user prompts;
- inspect sibling/external directories;
- infer architecture, domain, agent or repository.

Resolve the workspace root only from:

1. a valid existing `MODA_WORKSPACE_ROOT`; or
2. the current directory's parent chain.

Do not search the wider filesystem.

Run this as one terminal action, replacing `<TASK_ID>`:

```bash
TASK_ID="<TASK_ID>"
ROOT="${MODA_WORKSPACE_ROOT:-}"

if [ -z "$ROOT" ]; then
  CANDIDATE="$PWD"
  while [ "$CANDIDATE" != "/" ]; do
    if [ -f "$CANDIDATE/.nvmrc" ] &&
       [ -f "$CANDIDATE/scripts/start-agent-task.py" ] &&
       [ -f "$CANDIDATE/docs/agent-task-execution-template.md" ]; then
      ROOT="$CANDIDATE"
      break
    fi
    CANDIDATE="$(dirname "$CANDIDATE")"
  done
fi

if [ -z "$ROOT" ] ||
   [ ! -f "$ROOT/scripts/start-agent-task.py" ] ||
   [ ! -f "$ROOT/docs/agent-task-execution-template.md" ]; then
  echo "MODA_TASK_ERROR: unable to resolve Moda Interact workspace root" >&2
  exit 64
fi

export MODA_WORKSPACE_ROOT="$ROOT"
python3 "$MODA_WORKSPACE_ROOT/scripts/start-agent-task.py" "$TASK_ID" --json
```

If workspace-root resolution or `start-agent-task.py` fails, STOP and report the
failure. Do not fall back to task search, repository search, Git history, prompt
search or model inference.

## Resolver contract

Read the returned JSON.

The resolver output is authoritative for:

- architecture;
- domain;
- task/task file;
- logical `agent`;
- `repository`;
- current task status;
- rendered `prompt`.

Do not rediscover or override those values.

`prompt` is the complete execution instruction. Do not summarize, weaken or
replace it.

## Handoff

Successful resolution ends the launcher phase, not the task invocation.

If the resolver returns a valid task route, the next required action is to
enter the resolved logical-agent execution context using the resolver's
authoritative `agent`, `repository` and rendered `prompt`.

The following are valid reasons to STOP before task execution:

- workspace-root resolution failed;
- `start-agent-task.py` failed;
- the resolved task is not executable after the explicit dependency gate;
- the runtime genuinely cannot perform either named delegation or same-context
  logical-agent adoption.

The following are **not** valid reasons to STOP:

- the resolver returned `status: ready`;
- the resolver successfully identified the agent/repository/task file;
- the launcher itself is prohibited from claiming during the pre-handoff phase;
- no implementation has happened yet immediately after resolver execution.


### Claude Code

For task metadata, the canonical executor value is:

```text
claude
```

Invoke the named custom subagent from `.claude/agents` and pass `prompt`
unchanged.

If named delegation is unavailable but the runtime can continue in the current
context, read the resolved generated agent definition and adopt that logical
agent in the current context using `prompt` unchanged.

Only report a delegation limitation and STOP when the runtime genuinely cannot
perform either named delegation or same-context logical-agent adoption.

### Codex

For task metadata, the canonical executor value is:

```text
codex
```

Read the resolved logical-agent definition from:

```text
.codex/agents/<resolved-agent>.toml
```

Adopt that logical agent and the resolver's rendered `prompt` unchanged in the
current execution context, then continue with eligibility verification, claim
and execution.

Do **not** stop after successful routing merely because the pre-handoff launcher
phase itself is not allowed to claim the task.

### GitHub Copilot Agent Mode

For task metadata, the canonical executor value is:

```text
copilot
```

Do not use `github-copilot`, `github_copilot`, or another provider display
label.

Copilot does not use Claude's named-subagent mechanism.

Use the resolver's `agent` and `repository` exactly, read the corresponding
generated definition under `.claude/agents/`, then adopt `prompt` unchanged in
the current Agent Mode context.

This same-context adoption is the handoff. After adopting the resolved logical
agent, continue with dependency verification, claim and execution. Do **not**
finish the `/moda-task` invocation after merely reporting the resolver output.

Before inspecting implementation source, the resolved repository-agent protocol
MUST verify:

```text
status: ready
assigned_agent: <resolved agent>
all tasks explicitly listed in depends_on: complete
```

The dependency gate is limited to the current task's explicit `depends_on` list.
Do not invent additional dependency gates from the parent architecture, indexes,
`enables` lists, sibling tasks, transitive references, historical notes, or
superseded task records.

A task marked `superseded` elsewhere does not block the resolved task merely
because it is mentioned. Treat a superseded task as relevant only when:

1. it is still explicitly present in the resolved task's `depends_on` list, in
   which case report coordination drift to `moda_architect`; or
2. the resolved task's own implementation scope directly duplicates the
   superseded capability, in which case report the concrete scope conflict.

When reporting a conflict, identify the exact current-task field, contract or
scope requirement that conflicts. Do not stop solely because a separate task is
marked `superseded`.

If the task is not executable, do not claim it, inspect implementation source,
modify task state or implement anything. Report the blocking state/dependency
and STOP.

Only after eligibility is verified and the task is claimed may normal
implementation-repository inspection begin.

Required flow:

```text
TASK_ID
  |
  v
start-agent-task.py
  |
  v
authoritative routing + prompt
  |
  v
resolved logical agent
  |
  v
explicit dependency verification
  |
  +--> not executable -> STOP
  |
  v
claim -> inspect -> implement -> validate -> review
```

A successful `status: ready` resolver result must proceed through this flow in
the same `/moda-task` invocation. A response such as:

```text
No claim, implementation, or task-state modification was performed.
```

is only appropriate when execution is actually blocked or handoff is genuinely
unavailable. It is not an acceptable terminal response after successful routing
to an executable task.
