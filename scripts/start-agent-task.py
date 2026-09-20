#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DOMAIN_CONFIG = {
    "ADMIN": {"folder": "admin", "agent": "moda_admin", "repository": "moda-interact-admin"},
    "BACKGROUND": {"folder": "background", "agent": "moda_background", "repository": "moda-interact-background"},
    "COMMERCE": {"folder": "commerce", "agent": "moda_commerce", "repository": "moda-interact-commerce"},
    "DATABASE": {"folder": "database", "agent": "moda_database", "repository": "moda-interact-database"},
    "GATEWAY": {"folder": "gateway", "agent": "moda_gateway", "repository": "moda-interact-gateway"},
    "MESSAGING": {"folder": "messaging", "agent": "moda_messaging", "repository": "moda-interact-messaging"},
    "SHARED": {"folder": "shared", "agent": "moda_shared", "repository": "moda-interact-shared"},
    "SHOPIFY": {"folder": "shopify", "agent": "moda_app", "repository": "moda-interact"},
    "SITE": {"folder": "site", "agent": "moda_site", "repository": "moda-interact-site"},
    "SYSTEM-TEST": {"folder": "system-test", "agent": "moda_system_test", "repository": "moda-interact-system-test"},
}

TASK_ID_PATTERN = re.compile(r"^(ARCH-\d{3})-([A-Z][A-Z-]*)-(\d{3})$")
TEMPLATE_PATH = Path("docs/agent-task-execution-template.md")
EXECUTION_MODES = {"agent", "developer"}
COMPLETION_MODES = {"automatic", "developer"}
EXECUTOR_ALIASES = {
    "copilot": "copilot",
    "github-copilot": "copilot",
    "github_copilot": "copilot",
    "codex": "codex",
    "claude": "claude",
    "claude-code": "claude",
    "claude_code": "claude",
    "continue": "continue",
}


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


class CommandError(LauncherError):
    def __init__(self, *, command: list[str], cwd: Path | None, stdout: str, stderr: str, message: str):
        self.command = command
        self.cwd = cwd
        self.stdout = stdout
        self.stderr = stderr
        location = f"\nWorking directory:\n  {cwd}" if cwd else ""
        details = stderr.strip() or stdout.strip() or "(no command output)"
        super().__init__(
            f"{message}{location}\n\nCommand:\n  {' '.join(command)}\n\nOutput:\n{details}"
        )


def run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    if check and completed.returncode != 0:
        raise CommandError(
            command=command,
            cwd=cwd,
            stdout=completed.stdout,
            stderr=completed.stderr,
            message="Command failed during deterministic task preparation.",
        )
    return completed


def _workspace_markers_exist(path: Path) -> bool:
    required = (
        path / ".nvmrc",
        path / ".codex" / "agents",
        path / ".claude" / "agents",
        path / "scripts" / "start-agent-task.py",
        path / "docs" / "agent-task-execution-template.md",
    )
    return all(item.exists() for item in required)


def _git_common_dir(path: Path) -> Path | None:
    completed = run_command(
        ["git", "-C", str(path), "rev-parse", "--path-format=absolute", "--git-common-dir"],
        check=False,
    )
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return Path(value).resolve() if value else None


def canonicalize_workspace_root(candidate: Path) -> Path:
    """Return the primary Moda workspace root, never a linked task worktree.

    A parent task worktree contains all normal workspace markers, so marker tests
    alone are insufficient. For a linked worktree Git's common-dir points back to
    the primary repository's .git directory. Walking upward from that common-dir
    gives the canonical primary workspace root and prevents sequential task names
    from being extended from the previous task worktree basename.
    """

    candidate = candidate.resolve()
    if not _workspace_markers_exist(candidate):
        raise LauncherError(
            "Unable to verify Moda Interact workspace root.\n\n"
            f"Candidate:\n  {candidate}"
        )

    common_dir = _git_common_dir(candidate)
    if common_dir is not None:
        probe = common_dir
        while True:
            if _workspace_markers_exist(probe):
                return probe.resolve()
            if probe.name == ".git" and _workspace_markers_exist(probe.parent):
                return probe.parent.resolve()
            if probe.parent == probe:
                break
            probe = probe.parent

    return candidate


def find_workspace_root() -> Path:
    script_candidate = Path(__file__).resolve().parent.parent
    return canonicalize_workspace_root(script_candidate)


def parse_task_id(task_id: str) -> tuple[str, str, str]:
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
        valid_domains = "\n".join(f"  - {name}" for name in DOMAIN_CONFIG)
        raise LauncherError(f"Unknown task domain: {domain}\n\nValid domains:\n{valid_domains}")
    return architecture_id, domain, task_number


def task_route(workspace_root: Path, architecture_id: str, domain: str, task_number: str) -> dict[str, Any]:
    config = DOMAIN_CONFIG[domain]
    folder = config["folder"]
    agent = config["agent"]
    repository = config["repository"]
    task_local_id = f"{domain}-{task_number}"
    full_task_id = f"{architecture_id}-{task_local_id}"

    workspace_root = canonicalize_workspace_root(workspace_root)
    workspace_parent = workspace_root.parent
    workspace_name = workspace_root.name
    task_branch = f"task/{full_task_id}"
    parent_worktree = workspace_parent / f"{workspace_name}-task-{full_task_id}"
    implementation_worktree = workspace_parent / f"{workspace_name}.worktrees" / full_task_id
    repository_path = workspace_root / repository
    task_directory_relative = Path("docs") / "decisions" / folder / architecture_id
    pattern = f"{task_local_id}-*.md"

    # Hard invariant: task paths are derived from the canonical primary workspace
    # name only. A previous task worktree basename must never appear as the base.
    if f"-task-ARCH-" in workspace_name or workspace_name.endswith(".worktrees"):
        raise LauncherError(
            "MODA_CANONICAL_ROOT_ERROR: resolved workspace root looks like a task-worktree path.\n\n"
            f"Resolved root:\n  {workspace_root}"
        )

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
        "workspace_name": workspace_name,
        "task_branch": task_branch,
        "parent_worktree": parent_worktree,
        "implementation_worktree": implementation_worktree,
        "repository_path": repository_path,
        "task_directory_relative": task_directory_relative,
        "task_pattern": pattern,
    }


def _find_task_matches_in_root(root: Path, route: dict[str, Any]) -> list[tuple[Path, Path]]:
    task_directory_relative = route["task_directory_relative"]
    pattern = route["task_pattern"]
    assert isinstance(task_directory_relative, Path)
    assert isinstance(pattern, str)
    task_directory = root / task_directory_relative
    return [(match.relative_to(root), match) for match in sorted(task_directory.glob(pattern))]


def _find_task_matches(route: dict[str, Any]) -> list[tuple[Path, Path]]:
    workspace_root = route["workspace_root"]
    parent_worktree = route["parent_worktree"]
    assert isinstance(workspace_root, Path)
    assert isinstance(parent_worktree, Path)
    roots = [workspace_root]
    if parent_worktree.is_dir():
        roots.insert(0, parent_worktree)
    by_relative: dict[Path, Path] = {}
    for root in roots:
        for relative, match in _find_task_matches_in_root(root, route):
            by_relative.setdefault(relative, match)
    return [(relative, by_relative[relative]) for relative in sorted(by_relative)]


def resolve_task_file(
    workspace_root: Path,
    architecture_id: str,
    domain: str,
    task_number: str,
    *,
    authoritative_root: Path | None = None,
) -> ResolvedTask:
    route = task_route(workspace_root, architecture_id, domain, task_number)
    matches = (
        _find_task_matches_in_root(authoritative_root, route)
        if authoritative_root is not None
        else _find_task_matches(route)
    )
    if not matches:
        raise LauncherError(
            f"Task file not found for {route['task_id']}.\n\n"
            "Expected exactly one file matching:\n"
            f"  {route['task_directory_relative']}/{route['task_pattern']}"
        )
    if len(matches) > 1:
        relative_matches = "\n".join(f"  - {relative}" for relative, _ in matches)
        raise LauncherError(
            f"Multiple task files found for {route['task_id']}:\n\n{relative_matches}\n\n"
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
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _frontmatter_bounds(path: Path) -> tuple[list[str], int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise LauncherError(f"Task file has no YAML frontmatter:\n  {path}")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines, index
    raise LauncherError(f"Task file has unterminated YAML frontmatter:\n  {path}")


def read_frontmatter(path: Path) -> dict[str, str]:
    lines, end_index = _frontmatter_bounds(path)
    result: dict[str, str] = {}
    for line in lines[1:end_index]:
        if not line or line[0].isspace():
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if not match:
            continue
        key, value = match.groups()
        result[key] = strip_yaml_scalar(value)
    return result


def read_frontmatter_list(path: Path, key: str) -> list[str]:
    lines, end_index = _frontmatter_bounds(path)
    key_pattern = re.compile(rf"^{re.escape(key)}:\s*(.*?)\s*$")
    for index in range(1, end_index):
        line = lines[index]
        if not line or line[0].isspace():
            continue
        match = key_pattern.match(line)
        if not match:
            continue
        inline = strip_yaml_scalar(match.group(1))
        if inline in {"", "[]"}:
            values: list[str] = []
            cursor = index + 1
            while cursor < end_index:
                child = lines[cursor]
                # Existing task files use both indented YAML sequences and
                # column-zero sequence items (`depends_on:\n- TASK`). Stop only
                # when the next top-level mapping key begins.
                if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:\s*", child):
                    break
                item = re.match(r"^\s*-\s+(.*?)\s*$", child)
                if item:
                    values.append(strip_yaml_scalar(item.group(1)))
                cursor += 1
            return values
        if inline.startswith("[") and inline.endswith("]"):
            body = inline[1:-1].strip()
            return [strip_yaml_scalar(part.strip()) for part in body.split(",") if part.strip()]
        return [inline]
    return []


def task_modes(metadata: dict[str, str]) -> tuple[str, str]:
    execution_mode = metadata.get("execution_mode") or "agent"
    completion_mode = metadata.get("completion_mode") or "automatic"
    if execution_mode not in EXECUTION_MODES:
        raise LauncherError(
            f"Invalid execution_mode: {execution_mode!r}. Expected one of: {', '.join(sorted(EXECUTION_MODES))}."
        )
    if completion_mode not in COMPLETION_MODES:
        raise LauncherError(
            f"Invalid completion_mode: {completion_mode!r}. Expected one of: {', '.join(sorted(COMPLETION_MODES))}."
        )
    return execution_mode, completion_mode


def verify_task_metadata(task: ResolvedTask, metadata: dict[str, str]) -> None:
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
            problems.append(f"{key}: missing (expected {expected_value})")
        elif actual_value != expected_value:
            problems.append(f"{key}: {actual_value!r} (expected {expected_value!r})")
    if problems:
        details = "\n".join(f"  - {problem}" for problem in problems)
        raise LauncherError(
            f"Task metadata is inconsistent with {task.task_id}:\n\n{details}\n\n"
            "The launcher will not repair task identity metadata automatically."
        )
    task_modes(metadata)


def normalize_executor(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in EXECUTOR_ALIASES:
        allowed = ", ".join(sorted({*EXECUTOR_ALIASES.values()}))
        raise LauncherError(f"Unsupported executor {value!r}. Expected one of: {allowed}.")
    return EXECUTOR_ALIASES[normalized]


def git(source: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run_command(["git", "-C", str(source), *args], check=check)


def git_ref_exists(source: Path, ref: str) -> bool:
    return git(source, "show-ref", "--verify", "--quiet", ref, check=False).returncode == 0


def git_head(source: Path) -> str:
    return git(source, "rev-parse", "HEAD").stdout.strip()


def git_common_identity(source: Path) -> Path:
    completed = git(source, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return Path(completed.stdout.strip()).resolve()


def parse_worktree_registry(source: Path) -> list[dict[str, str]]:
    output = git(source, "worktree", "list", "--porcelain").stdout
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in output.splitlines() + [""]:
        if not line:
            if current:
                records.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    return records


def _normalized_path(path: str | Path) -> Path:
    return Path(os.path.realpath(os.fspath(path)))


def ensure_task_worktree(
    *,
    source_repository: Path,
    task_worktree: Path,
    task_branch: str,
    label: str,
) -> dict[str, Any]:
    if not source_repository.exists():
        raise LauncherError(f"{label} source repository does not exist:\n  {source_repository}")
    if git(source_repository, "rev-parse", "--is-inside-work-tree", check=False).returncode != 0:
        raise LauncherError(f"{label} source is not a Git worktree:\n  {source_repository}")

    git(source_repository, "fetch", "origin", "--prune")
    registry = parse_worktree_registry(source_repository)
    expected_path = _normalized_path(task_worktree)
    branch_ref = f"refs/heads/{task_branch}"

    path_record = None
    branch_records: list[dict[str, str]] = []
    for record in registry:
        worktree_value = record.get("worktree")
        if worktree_value and _normalized_path(worktree_value) == expected_path:
            path_record = record
        if record.get("branch") == branch_ref:
            branch_records.append(record)

    wrong_branch_paths = [
        record.get("worktree", "<unknown>")
        for record in branch_records
        if _normalized_path(record.get("worktree", "/")) != expected_path
    ]
    if wrong_branch_paths:
        formatted = "\n".join(f"  - {path}" for path in wrong_branch_paths)
        raise LauncherError(
            "MODA_WORKTREE_ISOLATION_ERROR: task branch is registered at a non-canonical path.\n\n"
            f"Branch:\n  {task_branch}\n\nExpected:\n  {task_worktree}\n\nRegistered elsewhere:\n{formatted}"
        )

    if path_record is not None:
        if path_record.get("branch") != branch_ref:
            raise LauncherError(
                "MODA_WORKTREE_ISOLATION_ERROR: canonical task worktree is on the wrong branch.\n\n"
                f"Path:\n  {task_worktree}\nExpected branch:\n  {task_branch}\n"
                f"Actual:\n  {path_record.get('branch', '<detached>')}"
            )
        if not task_worktree.is_dir():
            raise LauncherError(
                "MODA_WORKTREE_REGISTRATION_STALE: Git still registers the canonical worktree but its directory is absent.\n\n"
                f"Path:\n  {task_worktree}"
            )
        if git_common_identity(task_worktree) != git_common_identity(source_repository):
            raise LauncherError(
                "MODA_WORKTREE_ISOLATION_ERROR: canonical task path belongs to a different Git repository.\n\n"
                f"Path:\n  {task_worktree}"
            )
        return {"created": False, "reused": True}

    if task_worktree.exists():
        raise LauncherError(
            "MODA_WORKTREE_ISOLATION_ERROR: canonical task path exists but is not registered as the expected Git worktree.\n\n"
            f"Path:\n  {task_worktree}"
        )

    task_worktree.parent.mkdir(parents=True, exist_ok=True)
    local_ref = f"refs/heads/{task_branch}"
    remote_ref = f"refs/remotes/origin/{task_branch}"

    if git_ref_exists(source_repository, local_ref):
        git(source_repository, "worktree", "add", str(task_worktree), task_branch)
    elif git_ref_exists(source_repository, remote_ref):
        git(
            source_repository,
            "worktree",
            "add",
            "--track",
            "-b",
            task_branch,
            str(task_worktree),
            f"origin/{task_branch}",
        )
    else:
        if not git_ref_exists(source_repository, "refs/remotes/origin/main"):
            raise LauncherError(
                f"Cannot create {label} task worktree because origin/main is unavailable in {source_repository}."
            )
        git(source_repository, "worktree", "add", "-b", task_branch, str(task_worktree), "origin/main")

    return {"created": True, "reused": False}


def ensure_clean_worktree(worktree: Path, *, label: str) -> None:
    status = git(worktree, "status", "--porcelain", "--untracked-files=all").stdout
    if status.strip():
        raise LauncherError(
            f"MODA_WORKTREE_ISOLATION_ERROR: {label} task worktree is unexpectedly dirty.\n\n"
            f"Path:\n  {worktree}\n\nStatus:\n{status.rstrip()}"
        )


def synchronize_task_worktree(worktree: Path, *, task_branch: str, label: str) -> dict[str, str]:
    ensure_clean_worktree(worktree, label=label)
    git(worktree, "fetch", "origin", "--prune")

    remote_fast_forwarded = "not-needed"
    remote_ref = f"refs/remotes/origin/{task_branch}"
    if git_ref_exists(worktree, remote_ref):
        before = git_head(worktree)
        merged = git(worktree, "merge", "--ff-only", f"origin/{task_branch}", check=False)
        if merged.returncode != 0:
            raise LauncherError(
                "MODA_TASK_BRANCH_DIVERGED: local task branch cannot fast-forward from its remote branch.\n\n"
                f"Repository: {label}\nWorktree: {worktree}\nBranch: {task_branch}\n\n"
                f"Git output:\n{(merged.stderr or merged.stdout).strip()}"
            )
        after = git_head(worktree)
        if after != before:
            remote_fast_forwarded = "yes"

    if not git_ref_exists(worktree, "refs/remotes/origin/main"):
        raise LauncherError(f"origin/main is unavailable while synchronizing {label}:\n  {worktree}")

    ancestor = git(worktree, "merge-base", "--is-ancestor", "origin/main", "HEAD", check=False)
    if ancestor.returncode == 0:
        main_incorporated = "already-current"
    elif ancestor.returncode == 1:
        merged = git(worktree, "merge", "--no-edit", "origin/main", check=False)
        if merged.returncode != 0:
            # This merge was initiated by the launcher. Abort it so a failed
            # preparation does not strand the canonical task worktree in a
            # half-merged state.
            git(worktree, "merge", "--abort", check=False)
            raise LauncherError(
                "MODA_TASK_MAIN_MERGE_CONFLICT: current origin/main cannot be incorporated automatically.\n\n"
                f"Repository: {label}\nWorktree: {worktree}\nBranch: {task_branch}\n\n"
                f"Git output:\n{(merged.stderr or merged.stdout).strip()}"
            )
        main_incorporated = "yes"
    else:
        raise LauncherError(f"Unable to determine origin/main ancestry for {label}:\n  {worktree}")

    ensure_clean_worktree(worktree, label=label)
    return {
        "remote_task_branch_fast_forwarded": remote_fast_forwarded,
        "origin_main_incorporated": main_incorporated,
        "head": git_head(worktree),
    }


def prepare_recursive_submodules(implementation_worktree: Path) -> dict[str, Any]:
    sync = git(implementation_worktree, "submodule", "sync", "--recursive", check=False)
    if sync.returncode != 0:
        raise LauncherError(
            "MODA_SUBMODULE_PREPARATION_ERROR: `git submodule sync --recursive` failed.\n\n"
            f"Implementation worktree:\n  {implementation_worktree}\n\n"
            f"Git output:\n{(sync.stderr or sync.stdout).strip()}"
        )

    update = git(
        implementation_worktree,
        "submodule",
        "update",
        "--init",
        "--recursive",
        check=False,
    )
    if update.returncode != 0:
        raise LauncherError(
            "MODA_SUBMODULE_PREPARATION_ERROR: `git submodule update --init --recursive` failed.\n\n"
            f"Implementation worktree:\n  {implementation_worktree}\n\n"
            f"Git output:\n{(update.stderr or update.stdout).strip()}\n\n"
            "The task has NOT been claimed."
        )

    status = git(implementation_worktree, "submodule", "status", "--recursive", check=False)
    if status.returncode != 0:
        raise LauncherError(
            "MODA_SUBMODULE_PREPARATION_ERROR: recursive submodule status could not be verified.\n\n"
            f"Implementation worktree:\n  {implementation_worktree}\n\n"
            f"Git output:\n{(status.stderr or status.stdout).strip()}"
        )

    entries: list[dict[str, Any]] = []
    bad_lines: list[str] = []
    for raw_line in status.stdout.splitlines():
        if not raw_line.strip():
            continue
        prefix = raw_line[0]
        body = raw_line[1:].strip() if prefix in {" ", "-", "+", "U"} else raw_line.strip()
        parts = body.split()
        commit = parts[0] if parts else ""
        path = parts[1] if len(parts) > 1 else ""
        initialized = prefix not in {"-", "+", "U"}
        entries.append({"path": path, "commit": commit, "initialized": initialized})
        if not initialized:
            bad_lines.append(raw_line)

    if bad_lines:
        formatted = "\n".join(f"  {line}" for line in bad_lines)
        raise LauncherError(
            "MODA_SUBMODULE_PREPARATION_ERROR: recursive submodules are not at the exact commits recorded by the implementation branch.\n\n"
            f"Implementation worktree:\n  {implementation_worktree}\n\nStatus:\n{formatted}\n\n"
            "The task has NOT been claimed."
        )

    ensure_clean_worktree(implementation_worktree, label="implementation")
    return {
        "sync_recursive": "passed",
        "update_init_recursive": "passed",
        "status": "ready",
        "recursive": True,
        "entries": entries,
    }


def resolve_dependency(parent_worktree: Path, dependency_id: str) -> tuple[ResolvedTask, dict[str, str]]:
    architecture_id, domain, task_number = parse_task_id(dependency_id)
    task = resolve_task_file(
        parent_worktree,
        architecture_id,
        domain,
        task_number,
        authoritative_root=parent_worktree,
    )
    metadata = read_frontmatter(task.task_file)
    verify_task_metadata(task, metadata)
    return task, metadata


def verify_execution_gate(task: ResolvedTask, parent_worktree: Path, *, executor: str) -> dict[str, Any]:
    metadata = read_frontmatter(task.task_file)
    verify_task_metadata(task, metadata)
    execution_mode, completion_mode = task_modes(metadata)

    if execution_mode != "agent":
        raise LauncherError(
            f"TASK_EXECUTION_MODE_DEVELOPER: {task.task_id} uses execution_mode: developer.\n"
            "Do not claim it through /moda-task; use /moda_developer_create or /moda_developer_update."
        )

    status = metadata.get("status")
    if status != "ready":
        existing_executor = metadata.get("executor") or "null"
        raise LauncherError(
            f"TASK_NOT_READY: {task.task_id} cannot be prepared.\n\n"
            f"status: {status or '<missing>'}\nexecutor: {existing_executor}\n"
            "The launcher will not reset or overwrite an active/non-Ready task."
        )

    assigned = metadata.get("assigned_agent")
    if assigned != task.agent:
        raise LauncherError(
            f"TASK_AGENT_MISMATCH: expected {task.agent}, task records {assigned!r}."
        )

    dependencies: list[dict[str, str]] = []
    blocked: list[str] = []
    for dependency_id in read_frontmatter_list(task.task_file, "depends_on"):
        dependency_task, dependency_metadata = resolve_dependency(parent_worktree, dependency_id)
        dependency_status = dependency_metadata.get("status") or "<missing>"
        dependencies.append({"id": dependency_task.task_id, "status": dependency_status})
        if dependency_status != "complete":
            blocked.append(f"{dependency_task.task_id}: {dependency_status}")

    if blocked:
        formatted = "\n".join(f"  - {item}" for item in blocked)
        raise LauncherError(
            f"TASK_DEPENDENCY_GATE_BLOCKED: {task.task_id} has explicit dependencies that are not Complete:\n{formatted}"
        )

    try:
        attempt = int(metadata.get("attempt") or "0")
    except ValueError as exc:
        raise LauncherError(f"Invalid attempt value in {task.task_file}: {metadata.get('attempt')!r}") from exc

    return {
        "status": status,
        "execution_mode": execution_mode,
        "completion_mode": completion_mode,
        "executor": executor,
        "attempt_before_claim": attempt,
        "dependencies": dependencies,
        "dependency_gate": "passed",
        "architect_review_present": "## Architect Review" in task.task_file.read_text(encoding="utf-8"),
    }


def update_frontmatter_scalars(path: Path, updates: dict[str, str | int]) -> None:
    lines, end_index = _frontmatter_bounds(path)
    positions: dict[str, int] = {}
    for index in range(1, end_index):
        line = lines[index]
        if not line or line[0].isspace():
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):", line)
        if match:
            positions[match.group(1)] = index

    insertion_index = end_index
    for key, value in updates.items():
        rendered = f"{key}: {value}"
        if key in positions:
            lines[positions[key]] = rendered
        else:
            lines.insert(insertion_index, rendered)
            insertion_index += 1
            end_index += 1

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def claim_task(
    *,
    parent_worktree: Path,
    task: ResolvedTask,
    task_branch: str,
    executor: str,
    attempt_before_claim: int,
) -> dict[str, Any]:
    # Final compare-and-refresh immediately before the claim. This closes the
    # longest race window (implementation-worktree/submodule preparation).
    final_sync = synchronize_task_worktree(parent_worktree, task_branch=task_branch, label="parent")
    refreshed_task = resolve_task_file(
        parent_worktree,
        task.architecture_id,
        task.domain,
        task.task_number,
        authoritative_root=parent_worktree,
    )
    final_gate = verify_execution_gate(refreshed_task, parent_worktree, executor=executor)
    current_attempt = final_gate["attempt_before_claim"]
    if current_attempt != attempt_before_claim:
        raise LauncherError(
            "MODA_TASK_CLAIM_RACE: task attempt changed during preparation; task was not claimed.\n\n"
            f"Before: {attempt_before_claim}\nNow: {current_attempt}"
        )

    now = datetime.now(timezone.utc)
    claimed_at = now.isoformat(timespec="seconds").replace("+00:00", "Z")
    claimed_attempt = current_attempt + 1
    pre_claim_head = git_head(parent_worktree)

    update_frontmatter_scalars(
        refreshed_task.task_file,
        {
            "status": "in_progress",
            "executor": executor,
            "claimed_at": claimed_at,
            "attempt": claimed_attempt,
            "updated": now.date().isoformat(),
        },
    )

    relative_task_file = refreshed_task.task_file_relative.as_posix()
    git(parent_worktree, "add", "--", relative_task_file)
    staged = [line.strip() for line in git(parent_worktree, "diff", "--cached", "--name-only").stdout.splitlines() if line.strip()]
    if staged != [relative_task_file]:
        git(parent_worktree, "restore", "--staged", "--", relative_task_file, check=False)
        git(parent_worktree, "restore", "--", relative_task_file, check=False)
        raise LauncherError(
            "MODA_TASK_CLAIM_ERROR: claim staging contains unexpected files.\n\n"
            f"Expected only:\n  {relative_task_file}\n\nStaged:\n" + "\n".join(f"  - {item}" for item in staged)
        )

    git(parent_worktree, "commit", "-m", f"task({task.task_id}): claim task")
    claim_commit = git_head(parent_worktree)
    pushed = git(parent_worktree, "push", "-u", "origin", task_branch, check=False)
    if pushed.returncode != 0:
        # The claim commit was created by this launcher and has not been
        # published. Restore the exact pre-claim state; never reset published
        # history. Then report the race/failure instead of starting an agent.
        git(parent_worktree, "reset", "--hard", pre_claim_head, check=False)
        git(parent_worktree, "fetch", "origin", "--prune", check=False)
        raise LauncherError(
            "MODA_TASK_CLAIM_PUSH_FAILED: durable claim push failed; the local launcher-owned claim commit was rolled back and no agent should start.\n\n"
            f"Task: {task.task_id}\nBranch: {task_branch}\n\n"
            f"Git output:\n{(pushed.stderr or pushed.stdout).strip()}"
        )

    return {
        "status_before": "ready",
        "status_after": "in_progress",
        "attempt_before": current_attempt,
        "attempt": claimed_attempt,
        "executor": executor,
        "claimed_at": claimed_at,
        "committed": True,
        "pushed": True,
        "commit": claim_commit,
        "final_parent_sync": final_sync,
    }


def render_template(
    workspace_root: Path,
    task: ResolvedTask,
    metadata: dict[str, str],
    *,
    preparation_packet: dict[str, Any] | None = None,
) -> str:
    template_file = workspace_root / TEMPLATE_PATH
    if not template_file.is_file():
        raise LauncherError(f"Canonical execution template not found:\n  {TEMPLATE_PATH}")
    template = template_file.read_text(encoding="utf-8")

    route = task_route(workspace_root, task.architecture_id, task.domain, task.task_number)
    execution_mode, completion_mode = task_modes(metadata)
    packet_text = json.dumps(preparation_packet or {"prepared_execution": False}, indent=2, sort_keys=True)
    replacements = {
        "<AGENT>": task.agent,
        "<ARCH_ID>": task.architecture_id,
        "<TASK_ID>": task.task_id,
        "<TASK_FILE>": task.task_file_relative.as_posix(),
        "<TASK_BRANCH>": str(route["task_branch"]),
        "<WORKSPACE_ROOT>": Path(route["workspace_root"]).as_posix(),
        "<WORKSPACE_PARENT>": Path(route["workspace_parent"]).as_posix(),
        "<PARENT_WORKTREE>": Path(route["parent_worktree"]).as_posix(),
        "<IMPLEMENTATION_WORKTREE>": Path(route["implementation_worktree"]).as_posix(),
        "<REPOSITORY_PATH>": Path(route["repository_path"]).as_posix(),
        "<EXECUTION_MODE>": execution_mode,
        "<COMPLETION_MODE>": completion_mode,
        "<PREPARATION_PACKET>": packet_text,
    }
    rendered = template
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)
    unresolved = sorted(set(re.findall(r"<[A-Z][A-Z0-9_]*>", rendered)))
    if unresolved:
        raise LauncherError(
            "The canonical execution template contains unresolved placeholders:\n" +
            "\n".join(f"  - {item}" for item in unresolved)
        )
    return rendered


def build_result(
    workspace_root: Path,
    task: ResolvedTask,
    metadata: dict[str, str],
    prompt: str,
    *,
    preparation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    route = task_route(workspace_root, task.architecture_id, task.domain, task.task_number)
    execution_mode, completion_mode = task_modes(metadata)
    result: dict[str, Any] = {
        "task_id": task.task_id,
        "architecture_id": task.architecture_id,
        "domain": task.domain,
        "folder": task.folder,
        "agent": task.agent,
        "repository": task.repository,
        "repository_path": Path(route["repository_path"]).as_posix(),
        "workspace_root": Path(route["workspace_root"]).as_posix(),
        "workspace_parent": Path(route["workspace_parent"]).as_posix(),
        "task_branch": route["task_branch"],
        "parent_worktree_path": Path(route["parent_worktree"]).as_posix(),
        "implementation_worktree_path": Path(route["implementation_worktree"]).as_posix(),
        "task_file": task.task_file_relative.as_posix(),
        "codex_agent_definition": f".codex/agents/{task.agent}.toml",
        "claude_agent_definition": f".claude/agents/{task.agent}.agent.md",
        "status": metadata.get("status"),
        "execution_mode": execution_mode,
        "completion_mode": completion_mode,
        "task_materialized": True,
        "task_definition_state": "materialized",
        "prepared_execution": preparation is not None,
        "preparation": preparation,
        "prompt": prompt,
    }
    return result


def prepare_task(workspace_root: Path, task_id: str, executor_value: str) -> dict[str, Any]:
    executor = normalize_executor(executor_value)
    architecture_id, domain, task_number = parse_task_id(task_id)
    route = task_route(workspace_root, architecture_id, domain, task_number)
    task_branch = str(route["task_branch"])
    parent_worktree = Path(route["parent_worktree"])
    implementation_worktree = Path(route["implementation_worktree"])
    repository_path = Path(route["repository_path"])

    parent_created = ensure_task_worktree(
        source_repository=workspace_root,
        task_worktree=parent_worktree,
        task_branch=task_branch,
        label="parent",
    )
    parent_sync = synchronize_task_worktree(parent_worktree, task_branch=task_branch, label="parent")

    # Resolve the task only from the synchronized canonical parent task worktree.
    # This allows an architect-authored task branch that is not on main yet while
    # preventing stale task definitions from a shared checkout from winning.
    task = resolve_task_file(
        workspace_root,
        architecture_id,
        domain,
        task_number,
        authoritative_root=parent_worktree,
    )
    gate = verify_execution_gate(task, parent_worktree, executor=executor)

    implementation_created = ensure_task_worktree(
        source_repository=repository_path,
        task_worktree=implementation_worktree,
        task_branch=task_branch,
        label="implementation",
    )
    implementation_sync = synchronize_task_worktree(
        implementation_worktree,
        task_branch=task_branch,
        label="implementation",
    )

    # Mandatory before claim: exact recursive submodule materialisation at the
    # commits recorded by the prepared implementation branch. Never use --remote.
    submodules = prepare_recursive_submodules(implementation_worktree)

    claim = claim_task(
        parent_worktree=parent_worktree,
        task=task,
        task_branch=task_branch,
        executor=executor,
        attempt_before_claim=gate["attempt_before_claim"],
    )

    claimed_task = resolve_task_file(
        workspace_root,
        architecture_id,
        domain,
        task_number,
        authoritative_root=parent_worktree,
    )
    claimed_metadata = read_frontmatter(claimed_task.task_file)

    preparation = {
        "prepared_execution": True,
        "task_id": claimed_task.task_id,
        "execution_state": "claimed",
        "dependency_gate": gate["dependency_gate"],
        "dependencies": gate["dependencies"],
        "rework": {
            "required": bool(gate["attempt_before_claim"] > 0 or gate["architect_review_present"]),
            "previous_attempt": gate["attempt_before_claim"],
            "architect_review_present": gate["architect_review_present"],
        },
        "parent_worktree": {
            "path": parent_worktree.as_posix(),
            "branch": task_branch,
            **parent_created,
            **parent_sync,
        },
        "implementation_worktree": {
            "path": implementation_worktree.as_posix(),
            "branch": task_branch,
            **implementation_created,
            **implementation_sync,
            "submodules": submodules,
        },
        "claim": claim,
        "workspace_root_resolution": {
            "canonical_primary_workspace": workspace_root.as_posix(),
            "derived_from_previous_task_worktree": False,
        },
    }

    prompt = render_template(
        workspace_root,
        claimed_task,
        claimed_metadata,
        preparation_packet=preparation,
    )
    return build_result(
        workspace_root,
        claimed_task,
        claimed_metadata,
        prompt,
        preparation=preparation,
    )


def print_human_result(result: dict[str, Any]) -> None:
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
    print(f"Prepared:      {result.get('prepared_execution', False)}")
    print()
    print("=" * 80)
    print("RENDERED AGENT PROMPT")
    print("=" * 80)
    print()
    print(result["prompt"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve a Moda Interact architecture task. With --prepare, deterministically "
            "prepare/synchronize both task worktrees, materialise recursive implementation "
            "submodules, verify dependencies, durably claim the task, and render the agent prompt."
        )
    )
    parser.add_argument("task_id", help="Architecture task ID, e.g. ARCH-002-BACKGROUND-009")
    parser.add_argument(
        "--route-only",
        action="store_true",
        help="Resolve task topology without preparing/claiming. Used by task-definition/developer flows.",
    )
    parser.add_argument(
        "--prepare",
        action="store_true",
        help="Prepare/synchronize/gate/submodule-initialize/claim the task before agent handoff.",
    )
    parser.add_argument(
        "--executor",
        help="Canonical/current executor identity for --prepare: codex, claude, copilot or continue.",
    )
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="Output machine-readable JSON.")
    output.add_argument("--prompt-only", action="store_true", help="Output only the rendered agent prompt.")
    output.add_argument("--agent-only", action="store_true", help="Output only the resolved logical agent name.")
    return parser.parse_args()


def route_only_result(workspace_root: Path, architecture_id: str, domain: str, task_number: str) -> dict[str, Any]:
    route = task_route(workspace_root, architecture_id, domain, task_number)
    matches = _find_task_matches(route)
    if len(matches) > 1:
        relative_matches = "\n".join(f"  - {relative}" for relative, _ in matches)
        raise LauncherError(f"Multiple task files found for {route['task_id']}:\n\n{relative_matches}")

    metadata: dict[str, str] = {}
    task_file_relative = None
    if matches:
        task = resolve_task_file(workspace_root, architecture_id, domain, task_number)
        task_file_relative = task.task_file_relative
        metadata = read_frontmatter(task.task_file)
        verify_task_metadata(task, metadata)
        execution_mode, completion_mode = task_modes(metadata)
    else:
        execution_mode, completion_mode = None, None

    return {
        "task_id": route["task_id"],
        "architecture_id": route["architecture_id"],
        "domain": route["domain"],
        "folder": route["folder"],
        "agent": route["agent"],
        "repository": route["repository"],
        "repository_path": Path(route["repository_path"]).as_posix(),
        "workspace_root": Path(route["workspace_root"]).as_posix(),
        "workspace_parent": Path(route["workspace_parent"]).as_posix(),
        "task_branch": route["task_branch"],
        "parent_worktree_path": Path(route["parent_worktree"]).as_posix(),
        "implementation_worktree_path": Path(route["implementation_worktree"]).as_posix(),
        "task_directory": Path(route["task_directory_relative"]).as_posix(),
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


def main() -> int:
    args = parse_args()
    try:
        if args.route_only and args.prepare:
            raise LauncherError("--route-only and --prepare are mutually exclusive.")
        if args.prepare and not args.executor:
            raise LauncherError("--prepare requires --executor <codex|claude|copilot|continue>.")
        if args.executor and not args.prepare:
            raise LauncherError("--executor is only valid together with --prepare.")

        workspace_root = find_workspace_root()
        architecture_id, domain, task_number = parse_task_id(args.task_id)

        if args.route_only:
            result = route_only_result(workspace_root, architecture_id, domain, task_number)
            if args.agent_only:
                print(result["agent"])
            else:
                print(json.dumps(result, indent=2))
            return 0

        if args.prepare:
            result = prepare_task(workspace_root, args.task_id, args.executor)
            if args.json:
                print(json.dumps(result, indent=2))
            elif args.prompt_only:
                print(result["prompt"])
            elif args.agent_only:
                print(result["agent"])
            else:
                print_human_result(result)
            return 0

        task = resolve_task_file(workspace_root, architecture_id, domain, task_number)
        metadata = read_frontmatter(task.task_file)
        verify_task_metadata(task, metadata)
        prompt = render_template(workspace_root, task, metadata)
        result = build_result(workspace_root, task, metadata, prompt)

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
        print(f"ERROR: Filesystem operation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
