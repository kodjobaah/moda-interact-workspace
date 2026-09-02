---
name: moda-task
description: Launch a Moda Interact architecture task by task ID.
disable-model-invocation: true
---

You are a task launcher only. Do not claim, implement, modify task state or
perform architect review in this launcher context.

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

### Claude Code

Invoke the named custom subagent from `.claude/agents` and pass `prompt`
unchanged. If named delegation is unavailable, report that limitation.

### GitHub Copilot Agent Mode

Copilot does not use Claude's named-subagent mechanism.

Use the resolver's `agent` and `repository` exactly, read the corresponding
generated definition under `.claude/agents/`, then adopt `prompt` unchanged in
the current Agent Mode context.

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
