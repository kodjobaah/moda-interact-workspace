#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


DOMAIN_CONFIG = {
    "ADMIN": {
        "folder": "admin",
        "agent": "moda_admin",
        "repository": "moda-interact-admin",
    },
    "BACKGROUND": {
        "folder": "background",
        "agent": "moda_background",
        "repository": "moda-interact-background",
    },
    "DATABASE": {
        "folder": "database",
        "agent": "moda_database",
        "repository": "moda-interact-database",
    },
    "GATEWAY": {
        "folder": "gateway",
        "agent": "moda_gateway",
        "repository": "moda-interact-gateway",
    },
    "MESSAGING": {
        "folder": "messaging",
        "agent": "moda_messaging",
        "repository": "moda-interact-messaging",
    },
    "SHARED": {
        "folder": "shared",
        "agent": "moda_shared",
        "repository": "moda-interact-shared",
    },
    "SHOPIFY": {
        "folder": "shopify",
        "agent": "moda_app",
        "repository": "moda-interact",
    },
    "SITE": {
        "folder": "site",
        "agent": "moda_site",
        "repository": "moda-interact-site",
    },
    "SYSTEM-TEST": {
        "folder": "system-test",
        "agent": "moda_system_test",
        "repository": "moda-interact-system-test",
    },
}


TASK_ID_PATTERN = re.compile(
    r"^(ARCH-\d{3})-([A-Z][A-Z-]*)-(\d{3})$"
)


TEMPLATE_PATH = Path("docs/agent-task-execution-template.md")

EXECUTION_MODES = {"agent", "developer"}
COMPLETION_MODES = {"automatic", "developer"}


@dataclass(frozen=True)
class ResolvedTask:
    task_id: str
    architecture_id: str
    domain: str
    task_number: str
    task_local_id: str
    folder: str
    agent: str
    repository: str
    task_file: Path
    task_file_relative: Path


class LauncherError(RuntimeError):
    pass


def find_workspace_root() -> Path:
    script_path = Path(__file__).resolve()

    workspace_root = script_path.parent.parent

    required = [
        workspace_root / ".nvmrc",
        workspace_root / ".codex" / "agents",
        workspace_root / ".claude" / "agents",
        workspace_root / "docs" / "agent-task-execution-template.md",
    ]

    missing = [
        path.relative_to(workspace_root).as_posix()
        for path in required
        if not path.exists()
    ]

    if missing:
        formatted = "\n".join(
            f"  - {path}" for path in missing
        )

        raise LauncherError(
            "Unable to verify Moda Interact workspace root.\n\n"
            f"Derived root:\n  {workspace_root}\n\n"
            f"Missing:\n{formatted}"
        )

    return workspace_root


def parse_task_id(task_id: str) -> tuple[str, str, str]:
    """
    Example:

        ARCH-002-BACKGROUND-009

    becomes:

        architecture_id = ARCH-002
        domain          = BACKGROUND
        task_number     = 009

    SYSTEM-TEST works because the middle section is captured as a whole.
    """

    normalized = task_id.strip().upper()

    match = TASK_ID_PATTERN.fullmatch(normalized)

    if not match:
        raise LauncherError(
            f"Invalid task ID: {task_id}\n\n"
            "Expected format such as:\n"
            "  ARCH-002-BACKGROUND-009\n"
            "  ARCH-006-SHOPIFY-004\n"
            "  ARCH-008-SYSTEM-TEST-001"
        )

    architecture_id, domain, task_number = match.groups()

    if domain not in DOMAIN_CONFIG:
        valid_domains = "\n".join(
            f"  - {name}" for name in DOMAIN_CONFIG
        )

        raise LauncherError(
            f"Unknown task domain: {domain}\n\n"
            f"Valid domains:\n{valid_domains}"
        )

    return architecture_id, domain, task_number


def task_route(
    workspace_root: Path,
    architecture_id: str,
    domain: str,
    task_number: str,
) -> dict[str, object]:
    config = DOMAIN_CONFIG[domain]
    folder = config["folder"]
    agent = config["agent"]
    repository = config["repository"]
    task_local_id = f"{domain}-{task_number}"
    full_task_id = f"{architecture_id}-{task_local_id}"

    workspace_root = workspace_root.resolve()
    workspace_parent = workspace_root.parent
    task_branch = f"task/{full_task_id}"
    parent_worktree = workspace_parent / f"{workspace_root.name}-task-{full_task_id}"
    implementation_worktree = (
        workspace_parent / f"{workspace_root.name}.worktrees" / full_task_id
    )
    repository_path = workspace_root / repository
    task_directory_relative = Path("docs") / "decisions" / folder / architecture_id
    pattern = f"{task_local_id}-*.md"

    return {
        "task_id": full_task_id,
        "architecture_id": architecture_id,
        "domain": domain,
        "task_number": task_number,
        "task_local_id": task_local_id,
        "folder": folder,
        "agent": agent,
        "repository": repository,
        "workspace_root": workspace_root,
        "workspace_parent": workspace_parent,
        "task_branch": task_branch,
        "parent_worktree": parent_worktree,
        "implementation_worktree": implementation_worktree,
        "repository_path": repository_path,
        "task_directory_relative": task_directory_relative,
        "task_pattern": pattern,
    }


def _find_task_matches(route: dict[str, object]) -> list[tuple[Path, Path]]:
    workspace_root = route["workspace_root"]
    parent_worktree = route["parent_worktree"]
    task_directory_relative = route["task_directory_relative"]
    pattern = route["task_pattern"]

    assert isinstance(workspace_root, Path)
    assert isinstance(parent_worktree, Path)
    assert isinstance(task_directory_relative, Path)
    assert isinstance(pattern, str)

    roots = [workspace_root]
    if parent_worktree.is_dir():
        roots.insert(0, parent_worktree)

    by_relative: dict[Path, Path] = {}
    for root in roots:
        task_directory = root / task_directory_relative
        for match in sorted(task_directory.glob(pattern)):
            relative = match.relative_to(root)
            by_relative.setdefault(relative, match)

    return [(relative, by_relative[relative]) for relative in sorted(by_relative)]


def resolve_task_file(
    workspace_root: Path,
    architecture_id: str,
    domain: str,
    task_number: str,
) -> ResolvedTask:
    route = task_route(workspace_root, architecture_id, domain, task_number)
    matches = _find_task_matches(route)

    if not matches:
        raise LauncherError(
            f"Task file not found for {route['task_id']}.\n\n"
            "Expected exactly one file matching:\n"
            f"  {route['task_directory_relative']}/{route['task_pattern']}"
        )

    if len(matches) > 1:
        relative_matches = "\n".join(f"  - {relative}" for relative, _ in matches)
        raise LauncherError(
            f"Multiple task files found for {route['task_id']}:\n\n"
            f"{relative_matches}\n\n"
            "Task IDs must resolve to exactly one task file."
        )

    task_file_relative, task_file = matches[0]

    return ResolvedTask(
        task_id=str(route["task_id"]),
        architecture_id=architecture_id,
        domain=domain,
        task_number=task_number,
        task_local_id=str(route["task_local_id"]),
        folder=str(route["folder"]),
        agent=str(route["agent"]),
        repository=str(route["repository"]),
        task_file=task_file,
        task_file_relative=task_file_relative,
    )


def strip_yaml_scalar(value: str) -> str:
    value = value.strip()

    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in {"'", '"'}
    ):
        return value[1:-1]

    return value


def read_frontmatter(path: Path) -> dict[str, str]:
    """
    Reads only simple top-level YAML scalar values.

    We deliberately do not depend on PyYAML because the launcher only
    needs a few top-level fields:

      id
      architecture_id
      assigned_agent
      repository
      status
      execution_mode
      completion_mode
    """

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        raise LauncherError(
            f"Task file has no YAML frontmatter:\n  {path}"
        )

    end_index = None

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        raise LauncherError(
            f"Task file has unterminated YAML frontmatter:\n  {path}"
        )

    result: dict[str, str] = {}

    for line in lines[1:end_index]:
        # Only read top-level scalar fields.
        if not line or line[0].isspace():
            continue

        match = re.match(
            r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$",
            line,
        )

        if not match:
            continue

        key, value = match.groups()
        result[key] = strip_yaml_scalar(value)

    return result


def task_modes(metadata: dict[str, str]) -> tuple[str, str]:
    execution_mode = metadata.get("execution_mode") or "agent"
    completion_mode = metadata.get("completion_mode") or "automatic"

    if execution_mode not in EXECUTION_MODES:
        raise LauncherError(
            f"Invalid execution_mode: {execution_mode!r}. "
            f"Expected one of: {', '.join(sorted(EXECUTION_MODES))}."
        )

    if completion_mode not in COMPLETION_MODES:
        raise LauncherError(
            f"Invalid completion_mode: {completion_mode!r}. "
            f"Expected one of: {', '.join(sorted(COMPLETION_MODES))}."
        )

    return execution_mode, completion_mode


def verify_task_metadata(
    task: ResolvedTask,
    metadata: dict[str, str],
) -> None:
    expected = {
        "id": task.task_id,
        "architecture_id": task.architecture_id,
        "assigned_agent": task.agent,
        "repository": task.repository,
    }

    problems: list[str] = []

    for key, expected_value in expected.items():
        actual_value = metadata.get(key)

        if actual_value is None:
            problems.append(
                f"{key}: missing (expected {expected_value})"
            )
            continue

        if actual_value != expected_value:
            problems.append(
                f"{key}: {actual_value!r} "
                f"(expected {expected_value!r})"
            )

    if problems:
        details = "\n".join(f"  - {problem}" for problem in problems)

        raise LauncherError(
            f"Task metadata is inconsistent with {task.task_id}:\n\n"
            f"{details}\n\n"
            "The launcher will not repair task metadata automatically."
        )

    task_modes(metadata)


def render_template(
    workspace_root: Path,
    task: ResolvedTask,
    metadata: dict[str, str],
) -> str:
    template_file = workspace_root / TEMPLATE_PATH

    if not template_file.is_file():
        raise LauncherError(
            "Canonical execution template not found:\n"
            f"  {TEMPLATE_PATH}"
        )

    template = template_file.read_text(encoding="utf-8")

    required_placeholders = {
        "<AGENT>",
        "<ARCH_ID>",
        "<TASK_ID>",
        "<TASK_FILE>",
        "<TASK_BRANCH>",
        "<WORKSPACE_ROOT>",
        "<WORKSPACE_PARENT>",
        "<PARENT_WORKTREE>",
        "<IMPLEMENTATION_WORKTREE>",
        "<REPOSITORY_PATH>",
        "<EXECUTION_MODE>",
        "<COMPLETION_MODE>",
    }

    missing = sorted(
        placeholder
        for placeholder in required_placeholders
        if placeholder not in template
    )

    if missing:
        formatted = "\n".join(f"  - {item}" for item in missing)

        raise LauncherError(
            "The canonical execution template is not parameterised.\n\n"
            "Missing placeholders:\n"
            f"{formatted}\n\n"
            "The launcher never modifies the canonical template."
        )

    task_file_relative = task.task_file_relative
    workspace_root = workspace_root.resolve()
    workspace_parent = workspace_root.parent
    task_branch = f"task/{task.task_id}"
    parent_worktree = workspace_parent / f"{workspace_root.name}-task-{task.task_id}"
    implementation_worktree = (
        workspace_parent / f"{workspace_root.name}.worktrees" / task.task_id
    )
    repository_path = workspace_root / task.repository
    execution_mode, completion_mode = task_modes(metadata)

    replacements = {
        "<AGENT>": task.agent,
        "<ARCH_ID>": task.architecture_id,
        "<TASK_ID>": task.task_id,
        "<TASK_FILE>": task_file_relative.as_posix(),
        "<TASK_BRANCH>": task_branch,
        "<WORKSPACE_ROOT>": workspace_root.as_posix(),
        "<WORKSPACE_PARENT>": workspace_parent.as_posix(),
        "<PARENT_WORKTREE>": parent_worktree.as_posix(),
        "<IMPLEMENTATION_WORKTREE>": implementation_worktree.as_posix(),
        "<REPOSITORY_PATH>": repository_path.as_posix(),
        "<EXECUTION_MODE>": execution_mode,
        "<COMPLETION_MODE>": completion_mode,
    }

    rendered = template

    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)

    return rendered


def build_result(
    workspace_root: Path,
    task: ResolvedTask,
    metadata: dict[str, str],
    prompt: str,
) -> dict:
    workspace_root = workspace_root.resolve()
    workspace_parent = workspace_root.parent
    task_branch = f"task/{task.task_id}"
    parent_worktree = workspace_parent / f"{workspace_root.name}-task-{task.task_id}"
    implementation_worktree = (
        workspace_parent / f"{workspace_root.name}.worktrees" / task.task_id
    )
    repository_path = workspace_root / task.repository
    execution_mode, completion_mode = task_modes(metadata)

    return {
        "task_id": task.task_id,
        "architecture_id": task.architecture_id,
        "domain": task.domain,
        "folder": task.folder,
        "agent": task.agent,
        "repository": task.repository,
        # `repository_path` is the canonical repository source/reference checkout.
        # Task implementation MUST happen in `implementation_worktree_path`.
        "repository_path": repository_path.as_posix(),
        "workspace_root": workspace_root.as_posix(),
        "workspace_parent": workspace_parent.as_posix(),
        "task_branch": task_branch,
        "parent_worktree_path": parent_worktree.as_posix(),
        "implementation_worktree_path": implementation_worktree.as_posix(),
        "task_file": task.task_file_relative.as_posix(),
        "codex_agent_definition": f".codex/agents/{task.agent}.toml",
        "claude_agent_definition": f".claude/agents/{task.agent}.agent.md",
        "status": metadata.get("status"),
        "execution_mode": execution_mode,
        "completion_mode": completion_mode,
        "task_materialized": True,
        "task_definition_state": "materialized",
        "prompt": prompt,
    }


def print_human_result(result: dict) -> None:
    print(f"Task:          {result['task_id']}")
    print(f"Architecture:  {result['architecture_id']}")
    print(f"Domain:        {result['domain']}")
    print(f"Agent:         {result['agent']}")
    print(f"Repository:    {result['repository']}")
    print(f"Task file:     {result['task_file']}")
    print(f"Task branch:   {result['task_branch']}")
    print(f"Workspace:     {result['workspace_root']}")
    print(f"Parent WT:     {result['parent_worktree_path']}")
    print(f"Impl WT:       {result['implementation_worktree_path']}")
    print(f"Status:        {result['status'] or 'unknown'}")
    print(f"Execution:     {result['execution_mode']}")
    print(f"Completion:    {result['completion_mode']}")
    print(f"Materialized:  {result['task_materialized']}")
    print()
    print("=" * 80)
    print("RENDERED AGENT PROMPT")
    print("=" * 80)
    print()
    print(result["prompt"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve a Moda Interact architecture task and render "
            "the canonical repository-agent execution prompt."
        )
    )

    parser.add_argument(
        "task_id",
        help="Architecture task ID, e.g. ARCH-002-BACKGROUND-009",
    )

    parser.add_argument(
        "--route-only",
        action="store_true",
        help=(
            "Resolve task identity/topology without requiring an existing task "
            "definition. Used by architect/developer task-creation flows."
        ),
    )

    output = parser.add_mutually_exclusive_group()

    output.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON.",
    )

    output.add_argument(
        "--prompt-only",
        action="store_true",
        help="Output only the rendered agent prompt.",
    )

    output.add_argument(
        "--agent-only",
        action="store_true",
        help="Output only the resolved logical agent name.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        workspace_root = find_workspace_root()

        architecture_id, domain, task_number = parse_task_id(
            args.task_id
        )

        if args.route_only:
            route = task_route(
                workspace_root, architecture_id, domain, task_number
            )
            matches = _find_task_matches(route)
            if len(matches) > 1:
                relative_matches = "\n".join(
                    f"  - {relative}" for relative, _ in matches
                )
                raise LauncherError(
                    f"Multiple task files found for {route['task_id']}:\n\n"
                    f"{relative_matches}"
                )

            metadata: dict[str, str] = {}
            task_file_relative = None
            if matches:
                task = resolve_task_file(
                    workspace_root=workspace_root,
                    architecture_id=architecture_id,
                    domain=domain,
                    task_number=task_number,
                )
                task_file_relative = task.task_file_relative
                metadata = read_frontmatter(task.task_file)
                verify_task_metadata(task, metadata)
                execution_mode, completion_mode = task_modes(metadata)
            else:
                # Route-only resolution knows topology, not task execution/completion
                # policy. Those modes become authoritative only after a task
                # definition is materialised and its frontmatter is read.
                execution_mode, completion_mode = None, None

            result = {
                "task_id": route["task_id"],
                "architecture_id": route["architecture_id"],
                "domain": route["domain"],
                "folder": route["folder"],
                "agent": route["agent"],
                "repository": route["repository"],
                "repository_path": route["repository_path"].as_posix(),
                "workspace_root": route["workspace_root"].as_posix(),
                "workspace_parent": route["workspace_parent"].as_posix(),
                "task_branch": route["task_branch"],
                "parent_worktree_path": route["parent_worktree"].as_posix(),
                "implementation_worktree_path": route["implementation_worktree"].as_posix(),
                "task_directory": route["task_directory_relative"].as_posix(),
                "task_pattern": route["task_pattern"],
                "task_file": task_file_relative.as_posix() if task_file_relative else None,
                "task_exists": bool(matches),
                "task_materialized": bool(matches),
                "task_definition_state": "materialized" if matches else "unmaterialized",
                "portable_task_filename_pattern": route["task_pattern"],
                "status": metadata.get("status"),
                "execution_mode": execution_mode,
                "completion_mode": completion_mode,
            }

            if args.agent_only:
                print(result["agent"])
            elif args.json or args.prompt_only:
                print(json.dumps(result, indent=2))
            else:
                print(json.dumps(result, indent=2))
            return 0

        task = resolve_task_file(
            workspace_root=workspace_root,
            architecture_id=architecture_id,
            domain=domain,
            task_number=task_number,
        )

        metadata = read_frontmatter(task.task_file)

        verify_task_metadata(task, metadata)

        prompt = render_template(
            workspace_root=workspace_root,
            task=task,
            metadata=metadata,
        )

        result = build_result(
            workspace_root=workspace_root,
            task=task,
            metadata=metadata,
            prompt=prompt,
        )

        if args.json:
            print(json.dumps(result, indent=2))
        elif args.prompt_only:
            print(prompt)
        elif args.agent_only:
            print(task.agent)
        else:
            print_human_result(result)

        return 0

    except LauncherError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    except OSError as error:
        print(
            f"ERROR: Filesystem operation failed: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())