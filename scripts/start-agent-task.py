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


def resolve_task_file(
    workspace_root: Path,
    architecture_id: str,
    domain: str,
    task_number: str,
) -> ResolvedTask:
    config = DOMAIN_CONFIG[domain]

    folder = config["folder"]
    agent = config["agent"]
    repository = config["repository"]

    task_local_id = f"{domain}-{task_number}"
    full_task_id = f"{architecture_id}-{task_local_id}"

    task_directory = (
        workspace_root
        / "docs"
        / "decisions"
        / folder
        / architecture_id
    )

    pattern = f"{task_local_id}-*.md"

    matches = sorted(task_directory.glob(pattern))

    if not matches:
        raise LauncherError(
            f"Task file not found for {full_task_id}.\n\n"
            "Expected exactly one file matching:\n"
            f"  docs/decisions/{folder}/{architecture_id}/{pattern}"
        )

    if len(matches) > 1:
        relative_matches = "\n".join(
            f"  - {path.relative_to(workspace_root)}"
            for path in matches
        )

        raise LauncherError(
            f"Multiple task files found for {full_task_id}:\n\n"
            f"{relative_matches}\n\n"
            "Task IDs must resolve to exactly one task file."
        )

    return ResolvedTask(
        task_id=full_task_id,
        architecture_id=architecture_id,
        domain=domain,
        task_number=task_number,
        task_local_id=task_local_id,
        folder=folder,
        agent=agent,
        repository=repository,
        task_file=matches[0],
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


def render_template(
    workspace_root: Path,
    task: ResolvedTask,
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

    task_file_relative = task.task_file.relative_to(workspace_root)

    replacements = {
        "<AGENT>": task.agent,
        "<ARCH_ID>": task.architecture_id,
        "<TASK_ID>": task.task_id,
        "<TASK_FILE>": task_file_relative.as_posix(),
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
    return {
        "task_id": task.task_id,
        "architecture_id": task.architecture_id,
        "domain": task.domain,
        "folder": task.folder,
        "agent": task.agent,
        "repository": task.repository,
        "repository_path": (workspace_root / task.repository).as_posix(),
        "task_file": task.task_file.relative_to(
            workspace_root
        ).as_posix(),
        "codex_agent_definition": f".codex/agents/{task.agent}.toml",
        "claude_agent_definition": f".claude/agents/{task.agent}.agent.md",
        "status": metadata.get("status"),
        "prompt": prompt,
    }


def print_human_result(result: dict) -> None:
    print(f"Task:          {result['task_id']}")
    print(f"Architecture:  {result['architecture_id']}")
    print(f"Domain:        {result['domain']}")
    print(f"Agent:         {result['agent']}")
    print(f"Repository:    {result['repository']}")
    print(f"Task file:     {result['task_file']}")
    print(f"Status:        {result['status'] or 'unknown'}")
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