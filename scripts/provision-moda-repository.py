#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
LAUNCHER = SCRIPT_DIR / "start-agent-task.py"
GITHUB_REMOTE_RE = re.compile(
    r"^(?:https://github\.com/|git@github\.com:)(?P<owner>[^/ :]+)/(?P<repo>[^/]+?)(?:\.git)?$"
)


class ProvisionError(RuntimeError):
    pass


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    cwd: Path | None
    returncode: int
    stdout: str
    stderr: str


def run(
    command: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
) -> CommandResult:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    result = CommandResult(
        command=command,
        cwd=cwd,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    if check and completed.returncode != 0:
        location = f"\nWorking directory:\n  {cwd}" if cwd else ""
        output = completed.stderr.strip() or completed.stdout.strip() or "(no command output)"
        raise ProvisionError(
            "Repository provisioning command failed."
            f"{location}\n\nCommand:\n  {' '.join(command)}\n\nOutput:\n{output}"
        )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Provision a Moda implementation repository and register it as a canonical "
            "workspace Git submodule."
        )
    )
    parser.add_argument(
        "repository",
        help="Workspace repository/submodule name, e.g. moda-interact-woocommerce",
    )
    parser.add_argument(
        "--remote",
        required=True,
        help=(
            "Explicit Git remote URL for the implementation repository. Its basename "
            "must match the repository argument."
        ),
    )
    parser.add_argument(
        "--task",
        default=None,
        help=(
            "Optional fully-qualified architecture task ID. When supplied, the launcher "
            "route is validated against the requested repository but does not drive "
            "repository provisioning."
        ),
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help=(
            "If the remote is a github.com URL and does not exist, create it. "
            "Requires --visibility and authenticated gh."
        ),
    )
    parser.add_argument(
        "--visibility",
        choices=("public", "private"),
        default=None,
        help="GitHub repository visibility used only with --create.",
    )
    parser.add_argument(
        "--create-private",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--description",
        default=None,
        help="Description used only when --create creates a new GitHub repository.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Inspect repository/remote/workspace readiness without creating a remote, "
            "adding a submodule, committing, or pushing. Dirty workspace state is "
            "reported rather than rejected."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the final evidence packet as JSON.",
    )
    return parser.parse_args()


def parse_json_output(result: CommandResult, *, label: str) -> dict[str, Any]:
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ProvisionError(
            f"{label} did not return valid JSON.\n\nOutput:\n{result.stdout.strip()}"
        ) from exc
    if not isinstance(parsed, dict):
        raise ProvisionError(f"{label} returned JSON with an unexpected shape.")
    return parsed


def normalize_remote(remote: str) -> str:
    value = remote.strip()
    if value.endswith("/"):
        value = value[:-1]
    if value.endswith(".git"):
        value = value[:-4]
    return value


def remote_repository_basename(remote: str) -> str:
    normalized = normalize_remote(remote)
    if ":" in normalized and normalized.startswith("git@"):
        path = normalized.split(":", 1)[1]
    else:
        path = normalized.rsplit("/", 1)[-1]
        return path
    return path.rsplit("/", 1)[-1]


def github_slug(remote: str) -> str | None:
    match = GITHUB_REMOTE_RE.fullmatch(remote.strip())
    if not match:
        return None
    repo = match.group("repo")
    if repo.endswith(".git"):
        repo = repo[:-4]
    return f"{match.group('owner')}/{repo}"


def route_for_task(task_id: str) -> dict[str, Any]:
    result = run(
        [sys.executable, str(LAUNCHER), task_id, "--route-only", "--json"],
        cwd=SCRIPT_DIR.parent,
    )
    route = parse_json_output(result, label="start-agent-task.py --route-only")
    required = (
        "task_id",
        "repository",
        "repository_path",
        "workspace_root",
        "task_file",
        "task_materialized",
        "status",
        "agent",
        "domain",
    )
    missing = [key for key in required if key not in route]
    if missing:
        raise ProvisionError(
            "Launcher route output is missing required field(s): " + ", ".join(missing)
        )
    if not route["task_materialized"]:
        raise ProvisionError(
            "TASK_DEFINITION_NOT_MATERIALIZED: repository provisioning requires a "
            "materialized architecture task so repository ownership is authoritative."
        )
    return route


def git_output(workspace_root: Path, *args: str, check: bool = True) -> str:
    return run(["git", "-C", str(workspace_root), *args], check=check).stdout.strip()


def canonical_workspace_root() -> Path:
    candidate = SCRIPT_DIR.parent.resolve()
    result = run(
        ["git", "-C", str(candidate), "rev-parse", "--show-toplevel"],
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise ProvisionError(
            "Unable to resolve the canonical workspace from the provisioning script "
            f"location: {candidate}"
        )
    return Path(result.stdout.strip()).resolve()


def status_lines(workspace_root: Path) -> list[str]:
    raw = git_output(
        workspace_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    return [line for line in raw.splitlines() if line]


def staged_paths(workspace_root: Path) -> list[str]:
    raw = git_output(workspace_root, "diff", "--cached", "--name-only")
    return [line.strip() for line in raw.splitlines() if line.strip()]


def remote_tracking_main_sha(workspace_root: Path) -> str:
    remote = git_output(workspace_root, "remote", "get-url", "origin", check=False)
    if not remote:
        raise ProvisionError("Canonical workspace has no `origin` remote.")
    result = run(
        ["git", "ls-remote", remote, "refs/heads/main"],
        cwd=workspace_root,
        check=False,
    )
    if result.returncode != 0:
        output = result.stderr.strip() or result.stdout.strip() or "(no output)"
        raise ProvisionError(
            "Unable to read canonical workspace origin/main.\n\n"
            f"Origin:\n  {remote}\n\nOutput:\n{output}"
        )
    fields = result.stdout.strip().split()
    if len(fields) < 2 or fields[1] != "refs/heads/main":
        raise ProvisionError("Canonical workspace origin has no `main` branch.")
    return fields[0]


def inspect_primary_main(
    workspace_root: Path,
    *,
    dry_run: bool,
) -> dict[str, Any]:
    inside = git_output(workspace_root, "rev-parse", "--is-inside-work-tree", check=False)
    if inside != "true":
        raise ProvisionError(f"Canonical workspace is not a Git worktree: {workspace_root}")

    common_dir = git_output(
        workspace_root,
        "rev-parse",
        "--path-format=absolute",
        "--git-common-dir",
    )
    expected_git_dir = str((workspace_root / ".git").resolve())
    if str(Path(common_dir).resolve()) != expected_git_dir:
        raise ProvisionError(
            "Repository provisioning must run against the canonical primary workspace, "
            "not a linked task worktree.\n\n"
            f"Workspace:\n  {workspace_root}\n"
            f"Git common-dir:\n  {common_dir}"
        )

    branch = git_output(workspace_root, "branch", "--show-current")
    if branch != "main":
        raise ProvisionError(
            "Repository provisioning must run from canonical workspace branch `main`.\n\n"
            f"Current branch:\n  {branch or '(detached)'}"
        )

    local_head = git_output(workspace_root, "rev-parse", "HEAD")
    remote_main = remote_tracking_main_sha(workspace_root)
    if local_head != remote_main:
        raise ProvisionError(
            "Canonical workspace `main` must be synchronized exactly with remote "
            "`origin/main` before provisioning.\n\n"
            f"local HEAD:  {local_head}\n"
            f"origin/main: {remote_main}"
        )

    current_status = status_lines(workspace_root)
    current_staged = staged_paths(workspace_root)
    gitmodules_status = git_output(
        workspace_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        ".gitmodules",
    )

    blockers: list[str] = []
    if current_staged:
        blockers.append(
            "unrelated staged changes must be committed or unstaged before a real "
            "provisioning run"
        )
    if gitmodules_status:
        blockers.append(".gitmodules must be clean before adding a new submodule")

    if blockers and not dry_run:
        detail = "\n".join(f"- {item}" for item in blockers)
        raise ProvisionError(
            "Repository provisioning preflight failed.\n\n"
            f"{detail}\n\n"
            "Unstaged changes outside `.gitmodules` are allowed and will not be staged."
        )

    return {
        "branch": branch,
        "local_head": local_head,
        "remote_main": remote_main,
        "dirty": bool(current_status),
        "status": current_status,
        "staged_paths": current_staged,
        "gitmodules_dirty": bool(gitmodules_status),
        "real_run_blockers": blockers,
    }


def ensure_github_remote(
    remote: str,
    visibility: str,
    description: str | None,
    *,
    local_registration_present: bool,
) -> bool:
    slug = github_slug(remote)
    if slug is None:
        raise ProvisionError(
            "--create is supported only for github.com HTTPS or SSH remotes."
        )

    auth = run(["gh", "auth", "status"], check=False)
    if auth.returncode != 0:
        output = auth.stderr.strip() or auth.stdout.strip() or "(no output)"
        raise ProvisionError(
            "GitHub CLI is not authenticated. Run `gh auth login` first.\n\n" + output
        )

    view = run(
        ["gh", "repo", "view", slug, "--json", "nameWithOwner,isPrivate,defaultBranchRef,url"],
        check=False,
    )
    if view.returncode == 0:
        info = parse_json_output(view, label="gh repo view")
        is_private = info.get("isPrivate") is True
        actual_visibility = "private" if is_private else "public"
        if actual_visibility != visibility:
            raise ProvisionError(
                "Remote GitHub repository already exists with different visibility.\n\n"
                f"Repository: {slug}\n"
                f"Requested:  {visibility}\n"
                f"Actual:     {actual_visibility}"
            )
        return False

    if local_registration_present:
        raise ProvisionError(
            "Requested GitHub remote does not exist, but the workspace already contains "
            "a repository registration at the target path. Refusing to create a remote "
            "for ambiguous local state."
        )

    visibility_flag = "--private" if visibility == "private" else "--public"
    command = ["gh", "repo", "create", slug, visibility_flag, "--add-readme"]
    if description:
        command.extend(["--description", description])
    run(command)
    return True


def remote_main_sha(remote: str) -> str:
    result = run(["git", "ls-remote", "--symref", remote, "HEAD"], check=False)
    if result.returncode != 0:
        output = result.stderr.strip() or result.stdout.strip() or "(no output)"
        raise ProvisionError(
            "Unable to read the implementation repository remote.\n\n"
            f"Remote:\n  {remote}\n\nOutput:\n{output}"
        )

    head_ref: str | None = None
    head_sha: str | None = None
    for line in result.stdout.splitlines():
        if line.startswith("ref:") and line.endswith("\tHEAD"):
            head_ref = line.split()[1]
        else:
            fields = line.split()
            if len(fields) == 2 and fields[1] == "HEAD":
                head_sha = fields[0]

    if head_ref != "refs/heads/main":
        raise ProvisionError(
            "Implementation repository default branch must be `main` before it can be "
            "registered as a Moda workspace submodule.\n\n"
            f"Remote:\n  {remote}\n"
            f"Observed HEAD ref:\n  {head_ref or '(missing)'}"
        )
    if not head_sha:
        raise ProvisionError(
            "Implementation repository must contain an initial commit on `main` before "
            "workspace registration."
        )
    return head_sha


def gitmodules_entry(workspace_root: Path, repository: str) -> tuple[str, str] | None:
    gitmodules = workspace_root / ".gitmodules"
    if not gitmodules.is_file():
        return None
    path_key = f"submodule.{repository}.path"
    url_key = f"submodule.{repository}.url"
    path_result = run(
        ["git", "config", "-f", str(gitmodules), "--get", path_key],
        check=False,
    )
    url_result = run(
        ["git", "config", "-f", str(gitmodules), "--get", url_key],
        check=False,
    )
    if path_result.returncode != 0 and url_result.returncode != 0:
        return None
    if path_result.returncode != 0 or url_result.returncode != 0:
        raise ProvisionError(
            f".gitmodules contains an incomplete submodule entry for {repository}."
        )
    return path_result.stdout.strip(), url_result.stdout.strip()


def staged_gitlink_sha(workspace_root: Path, repository: str) -> tuple[str, str] | None:
    result = run(
        ["git", "-C", str(workspace_root), "ls-files", "--stage", "--", repository],
        check=False,
    )
    line = result.stdout.strip()
    if not line:
        return None
    fields = line.split()
    if len(fields) < 4:
        raise ProvisionError(f"Unable to parse workspace gitlink entry for {repository}: {line}")
    return fields[0], fields[1]



def local_registration_present(
    *,
    workspace_root: Path,
    repository_path: Path,
    repository: str,
) -> bool:
    entry = gitmodules_entry(workspace_root, repository)
    gitlink = staged_gitlink_sha(workspace_root, repository)
    path_exists = repository_path.exists()

    present_count = sum((entry is not None, gitlink is not None, path_exists))
    if present_count == 0:
        return False
    if present_count == 3:
        return True

    raise ProvisionError(
        "Repository provisioning is partially present. Refusing to guess or overwrite "
        "the workspace state. Inspect `.gitmodules`, the gitlink, and the repository "
        f"path manually for: {repository}"
    )

def verify_existing_registration(
    *,
    workspace_root: Path,
    repository_path: Path,
    repository: str,
    remote: str,
    expected_sha: str,
) -> dict[str, Any] | None:
    entry = gitmodules_entry(workspace_root, repository)
    gitlink = staged_gitlink_sha(workspace_root, repository)
    if entry is None and gitlink is None and not repository_path.exists():
        return None

    if entry is None or gitlink is None or not repository_path.exists():
        raise ProvisionError(
            "Repository provisioning is partially present. Refusing to guess or overwrite "
            "the workspace state. Inspect `.gitmodules`, the gitlink, and the repository "
            f"path manually for: {repository}"
        )

    path_value, url_value = entry
    if path_value != repository:
        raise ProvisionError(
            f".gitmodules path mismatch for {repository}: expected {repository!r}, got {path_value!r}"
        )
    if normalize_remote(url_value) != normalize_remote(remote):
        raise ProvisionError(
            f".gitmodules remote mismatch for {repository}.\n"
            f"Expected: {remote}\nObserved: {url_value}"
        )

    mode, gitlink_sha = gitlink
    if mode != "160000":
        raise ProvisionError(
            f"Workspace entry for {repository} is not a Git submodule gitlink (mode {mode})."
        )

    inside = run(
        ["git", "-C", str(repository_path), "rev-parse", "--is-inside-work-tree"],
        check=False,
    )
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        raise ProvisionError(f"Registered submodule path is not a Git worktree: {repository_path}")

    origin = run(
        ["git", "-C", str(repository_path), "remote", "get-url", "origin"]
    ).stdout.strip()
    if normalize_remote(origin) != normalize_remote(remote):
        raise ProvisionError(
            f"Implementation repository origin mismatch.\nExpected: {remote}\nObserved: {origin}"
        )

    child_head = run(
        ["git", "-C", str(repository_path), "rev-parse", "HEAD"]
    ).stdout.strip()
    if child_head != gitlink_sha:
        raise ProvisionError(
            "Implementation repository HEAD does not match the workspace gitlink.\n\n"
            f"child HEAD: {child_head}\ngitlink:    {gitlink_sha}"
        )
    if gitlink_sha != expected_sha:
        raise ProvisionError(
            "Existing workspace gitlink does not match the current remote `main` head. "
            "Repository provisioning does not update an existing pin implicitly.\n\n"
            f"gitlink:     {gitlink_sha}\nremote main: {expected_sha}"
        )

    return {
        "already_provisioned": True,
        "repository_sha": gitlink_sha,
    }


def provision_submodule(
    *,
    workspace_root: Path,
    repository: str,
    remote: str,
    expected_sha: str,
) -> str:
    run(["git", "submodule", "add", remote, repository], cwd=workspace_root)
    run(["git", "submodule", "sync", "--", repository], cwd=workspace_root)
    run(
        ["git", "submodule", "update", "--init", "--recursive", "--", repository],
        cwd=workspace_root,
    )

    repository_path = workspace_root / repository
    branch = run(
        ["git", "-C", str(repository_path), "branch", "--show-current"]
    ).stdout.strip()
    if branch != "main":
        raise ProvisionError(
            f"Provisioned implementation repository is not on `main`: {branch or '(detached)'}"
        )

    child_head = run(
        ["git", "-C", str(repository_path), "rev-parse", "HEAD"]
    ).stdout.strip()
    if child_head != expected_sha:
        raise ProvisionError(
            "Provisioned implementation repository does not match the validated remote main SHA.\n\n"
            f"child HEAD:  {child_head}\nremote main: {expected_sha}"
        )

    gitlink = staged_gitlink_sha(workspace_root, repository)
    if gitlink is None or gitlink[0] != "160000" or gitlink[1] != expected_sha:
        raise ProvisionError(
            "Workspace did not stage the expected submodule gitlink after `git submodule add`."
        )

    entry = gitmodules_entry(workspace_root, repository)
    if entry is None:
        raise ProvisionError("Workspace .gitmodules entry was not created.")
    path_value, url_value = entry
    if path_value != repository or normalize_remote(url_value) != normalize_remote(remote):
        raise ProvisionError("Workspace .gitmodules entry does not match the requested route/remote.")

    staged = {
        line.strip()
        for line in git_output(workspace_root, "diff", "--cached", "--name-only").splitlines()
        if line.strip()
    }
    expected_staged = {".gitmodules", repository}
    if staged != expected_staged:
        raise ProvisionError(
            "Provisioning staged unexpected workspace paths. Refusing to commit.\n\n"
            f"Expected: {sorted(expected_staged)}\nObserved: {sorted(staged)}"
        )

    message = f"chore(workspace): provision {repository} repository"
    run(["git", "commit", "-m", message], cwd=workspace_root)
    run(["git", "push", "origin", "main"], cwd=workspace_root)
    return git_output(workspace_root, "rev-parse", "HEAD")


def render_human(evidence: dict[str, Any]) -> str:
    task_id = evidence.get("task_id") or "(not supplied)"
    domain = evidence.get("domain") or "(not task-validated)"
    agent = evidence.get("agent") or "(not task-validated)"
    task_status = evidence.get("task_status") or "(not task-validated)"
    lines = [
        "Moda repository provisioning evidence",
        "",
        f"Repository:           {evidence['repository']}",
        f"Remote:               {evidence['remote']}",
        f"Repository SHA:       {evidence.get('repository_sha') or '(not created / unavailable)' }",
        f"Workspace root:       {evidence['workspace_root']}",
        f"Workspace commit:     {evidence.get('workspace_commit') or '(unchanged / dry-run)'}",
        f"Already provisioned:  {str(evidence['already_provisioned']).lower()}",
        f"Remote created:       {str(evidence['remote_created']).lower()}",
        f"Remote visibility:    {evidence.get('remote_visibility') or '(existing / not requested)'}",
        f"Dry run:              {str(evidence['dry_run']).lower()}",
        f"Workspace dirty:      {str(evidence.get('workspace_dirty', False)).lower()}",
        f"Task verification:    {task_id}",
        f"Domain:               {domain}",
        f"Agent:                {agent}",
        f"Task status:          {task_status}",
    ]
    blockers = evidence.get("real_run_blockers") or []
    if blockers:
        lines.extend(["", "Real-run blockers:"])
        lines.extend(f"  - {item}" for item in blockers)
    if evidence.get("dry_run"):
        lines.extend(
            [
                "",
                "Dry-run only: no remote, submodule, commit, or push was created.",
            ]
        )
    elif evidence.get("task_id"):
        lines.extend(
            [
                "",
                "Next architectural action:",
                "  moda_architect records the provisioning evidence and promotes the",
                "  task from pending to ready only when its dependency/readiness",
                "  conditions are satisfied.",
            ]
        )
    lines.extend(
        [
            "",
            "This provisioning workflow does not create task worktrees, claim a task,",
            "or change task status.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        if args.create_private:
            if args.create and args.visibility not in (None, "private"):
                raise ProvisionError(
                    "Deprecated --create-private conflicts with --visibility public."
                )
            args.create = True
            args.visibility = "private"

        if args.create and args.visibility is None:
            raise ProvisionError(
                "--create requires an explicit --visibility public|private."
            )
        if args.visibility is not None and not args.create:
            raise ProvisionError(
                "--visibility is valid only together with --create."
            )
        if args.description and not args.create:
            raise ProvisionError(
                "--description is valid only together with --create."
            )

        repository = args.repository.strip()
        if not repository or "/" in repository or "\\" in repository or repository in {".", ".."}:
            raise ProvisionError(
                "Repository must be a single workspace directory/submodule name, for "
                "example `moda-interact-woocommerce`."
            )

        remote = args.remote.strip()
        if remote_repository_basename(remote) != repository:
            raise ProvisionError(
                "Remote repository basename does not match the requested workspace "
                "repository.\n\n"
                f"Repository: {repository}\nRemote:     {remote}"
            )

        workspace_root = canonical_workspace_root()
        repository_path = (workspace_root / repository).resolve()
        try:
            repository_path.relative_to(workspace_root)
        except ValueError as exc:
            raise ProvisionError("Repository path escapes the canonical workspace.") from exc

        route: dict[str, Any] | None = None
        if args.task:
            route = route_for_task(args.task)
            route_repository = str(route["repository"])
            if route_repository != repository:
                raise ProvisionError(
                    "Optional task route does not match the requested repository.\n\n"
                    f"Task:            {route['task_id']}\n"
                    f"Task repository: {route_repository}\n"
                    f"Requested:       {repository}"
                )
            route_workspace = Path(str(route["workspace_root"])).resolve()
            if route_workspace != workspace_root:
                raise ProvisionError(
                    "Optional task route resolved a different canonical workspace.\n\n"
                    f"Provisioning workspace: {workspace_root}\n"
                    f"Task workspace:         {route_workspace}"
                )

        workspace_state = inspect_primary_main(workspace_root, dry_run=args.dry_run)
        initial_status = list(workspace_state["status"])
        registration_present = local_registration_present(
            workspace_root=workspace_root,
            repository_path=repository_path,
            repository=repository,
        )

        remote_created = False
        remote_visibility: str | None = None
        if args.create:
            assert args.visibility is not None
            remote_visibility = args.visibility
            if args.dry_run:
                slug = github_slug(remote)
                if slug is None:
                    raise ProvisionError(
                        "--create is supported only for github.com HTTPS or SSH remotes."
                    )
                auth = run(["gh", "auth", "status"], check=False)
                if auth.returncode != 0:
                    raise ProvisionError(
                        "GitHub CLI is not authenticated; dry-run cannot validate "
                        "private repository creation."
                    )
                view = run(
                    ["gh", "repo", "view", slug, "--json", "isPrivate"],
                    check=False,
                )
                if view.returncode == 0:
                    info = parse_json_output(view, label="gh repo view")
                    is_private = info.get("isPrivate") is True
                    actual_visibility = "private" if is_private else "public"
                    if actual_visibility != args.visibility:
                        raise ProvisionError(
                            "Remote GitHub repository already exists with different visibility.\n\n"
                            f"Repository: {slug}\n"
                            f"Requested:  {args.visibility}\n"
                            f"Actual:     {actual_visibility}"
                        )
                    remote_visibility = actual_visibility
                else:
                    if registration_present:
                        raise ProvisionError(
                            "Requested GitHub remote does not exist, but the workspace "
                            "already contains a repository registration at the target "
                            "path. Refusing to create a remote for ambiguous local state."
                        )
                    evidence = {
                        "task_id": route["task_id"] if route else None,
                        "domain": route["domain"] if route else None,
                        "agent": route["agent"] if route else None,
                        "repository": repository,
                        "remote": remote,
                        "repository_sha": None,
                        "workspace_root": str(workspace_root),
                        "workspace_commit": None,
                        "already_provisioned": False,
                        "remote_created": False,
                        "dry_run": True,
                        "task_status": route["status"] if route else None,
                        "route_verified": bool(route),
                        "remote_state": f"would_create_{args.visibility}",
                        "remote_visibility": args.visibility,
                        "workspace_dirty": workspace_state["dirty"],
                        "workspace_status": workspace_state["status"],
                        "workspace_staged_paths": workspace_state["staged_paths"],
                        "real_run_blockers": workspace_state["real_run_blockers"],
                    }
                    print(json.dumps(evidence, indent=2) if args.json else render_human(evidence))
                    return 0
            else:
                remote_created = ensure_github_remote(
                    remote,
                    args.visibility,
                    args.description,
                    local_registration_present=registration_present,
                )

        expected_sha = remote_main_sha(remote)

        existing = verify_existing_registration(
            workspace_root=workspace_root,
            repository_path=repository_path,
            repository=repository,
            remote=remote,
            expected_sha=expected_sha,
        )

        if args.dry_run:
            evidence = {
                "task_id": route["task_id"] if route else None,
                "domain": route["domain"] if route else None,
                "agent": route["agent"] if route else None,
                "repository": repository,
                "remote": remote,
                "repository_sha": expected_sha,
                "workspace_root": str(workspace_root),
                "workspace_commit": None,
                "already_provisioned": bool(existing),
                "remote_created": False,
                "dry_run": True,
                "task_status": route["status"] if route else None,
                "route_verified": bool(route),
                "remote_state": "ready",
                "remote_visibility": remote_visibility,
                "workspace_dirty": workspace_state["dirty"],
                "workspace_status": workspace_state["status"],
                "workspace_staged_paths": workspace_state["staged_paths"],
                "real_run_blockers": workspace_state["real_run_blockers"],
            }
            print(json.dumps(evidence, indent=2) if args.json else render_human(evidence))
            return 0

        if existing:
            workspace_commit = git_output(workspace_root, "rev-parse", "HEAD")
            already_provisioned = True
        else:
            workspace_commit = provision_submodule(
                workspace_root=workspace_root,
                repository=repository,
                remote=remote,
                expected_sha=expected_sha,
            )
            already_provisioned = False

        final_staged = staged_paths(workspace_root)
        if final_staged:
            raise ProvisionError(
                "Workspace still has staged paths after repository provisioning.\n\n"
                + "\n".join(final_staged)
            )

        final_gitmodules_status = git_output(
            workspace_root,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "--",
            ".gitmodules",
        )
        if final_gitmodules_status:
            raise ProvisionError(
                ".gitmodules is unexpectedly dirty after repository provisioning.\n\n"
                + final_gitmodules_status
            )

        child_status = run(
            ["git", "-C", str(repository_path), "status", "--porcelain=v1"],
            check=False,
        )
        if child_status.returncode != 0 or child_status.stdout.strip():
            raise ProvisionError(
                "Provisioned implementation repository is not clean after registration.\n\n"
                + (child_status.stdout.strip() or child_status.stderr.strip())
            )

        final_status = status_lines(workspace_root)
        if final_status != initial_status:
            raise ProvisionError(
                "Repository provisioning changed unrelated workspace status.\n\n"
                f"Before: {initial_status}\nAfter:  {final_status}"
            )

        final_origin_main = remote_tracking_main_sha(workspace_root)
        final_head = git_output(workspace_root, "rev-parse", "HEAD")
        if final_origin_main != final_head:
            raise ProvisionError(
                "Workspace provisioning commit is not synchronized with origin/main "
                "after push."
            )

        evidence = {
            "task_id": route["task_id"] if route else None,
            "domain": route["domain"] if route else None,
            "agent": route["agent"] if route else None,
            "repository": repository,
            "remote": remote,
            "repository_sha": expected_sha,
            "workspace_root": str(workspace_root),
            "workspace_commit": workspace_commit,
            "already_provisioned": already_provisioned,
            "remote_created": remote_created,
            "remote_visibility": remote_visibility,
            "dry_run": False,
            "task_status": route["status"] if route else None,
            "route_verified": bool(route),
            "workspace_dirty": bool(initial_status),
            "workspace_status_preserved": True,
            "real_run_blockers": [],
            "next_action": (
                "architect_readiness_reconciliation" if route else "optional_task_route_verification"
            ),
        }
        print(json.dumps(evidence, indent=2) if args.json else render_human(evidence))
        return 0
    except ProvisionError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
