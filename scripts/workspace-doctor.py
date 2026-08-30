#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import subprocess
import sys

mode = sys.argv[1] if len(sys.argv) > 1 else "--quick"
if mode not in {"--quick", "--full", "--production"}:
    raise SystemExit("Usage: workspace-doctor.py [--quick|--full|--production]")

root = Path.cwd()
failures: list[str] = []
warnings: list[str] = []
infos: list[str] = []
passes: list[str] = []


def out(label: str, message: str) -> None:
    print(f"  {label:<5} {message}")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"{path}: invalid JSON: {exc}")
        return None


def runtime_dep(pkg: dict, name: str):
    for section in ("dependencies", "peerDependencies", "optionalDependencies"):
        value = (pkg.get(section) or {}).get(name)
        if value is not None:
            return section, value
    return None, None


def major_from_range(value: str | None):
    if not value:
        return None
    m = re.search(r"(?<!\d)(\d+)(?:\.\d+)?(?:\.\d+)?", value)
    return int(m.group(1)) if m else None


def installed_root_zod(repo: Path):
    path = repo / "node_modules" / "zod" / "package.json"
    if not path.is_file():
        return None
    data = load_json(path)
    return data.get("version") if data else None


print("Moda Interact workspace doctor")
print(f"Mode: {mode}")
print()

selector = (root / ".nvmrc").read_text(encoding="utf-8").strip()
actual = subprocess.check_output(["node", "--version"], text=True).strip()
out("PASS", f"Node selector: {selector}; active: {actual}")
passes.append("node")

shared_path = root / "moda-interact-shared" / "package.json"
shared_range = None
shared_major = None

if not shared_path.is_file():
    out("FAIL", "moda-interact-shared/package.json not found")
    failures.append("shared package missing")
else:
    shared = load_json(shared_path) or {}
    section, shared_range = runtime_dep(shared, "zod")
    if not shared_range:
        out("FAIL", "shared package has no runtime Zod dependency/peer contract")
        failures.append("shared Zod contract missing")
    else:
        shared_major = major_from_range(shared_range)
        out("PASS", f"shared Zod runtime contract: {section}.zod = {shared_range}")
        passes.append("shared zod")

repos = [
    "moda-interact",
    "moda-interact-background",
    "moda-interact-messaging",
    "moda-interact-admin",
    "moda-interact-gateway",
    "moda-interact-site",
]

print()
print("Runtime consumers")

for name in repos:
    repo = root / name
    pkg_path = repo / "package.json"
    if not pkg_path.is_file():
        continue
    pkg = load_json(pkg_path)
    if pkg is None:
        continue

    _, shared_value = runtime_dep(pkg, "@modainteract/moda-interact-shared")
    _, zod_value = runtime_dep(pkg, "zod")
    installed = installed_root_zod(repo)

    if shared_value:
        if not zod_value:
            out("FAIL", f"{name}: runtime consumer of shared but has no direct runtime Zod declaration")
            failures.append(f"{name}: missing direct zod")
        else:
            consumer_major = major_from_range(zod_value)
            if shared_major is not None and consumer_major is not None and consumer_major != shared_major:
                out("FAIL", f"{name}: Zod {zod_value} is incompatible with shared runtime range {shared_range}")
                failures.append(f"{name}: incompatible zod")
            elif installed and shared_major is not None and int(installed.split('.')[0]) != shared_major:
                out("FAIL", f"{name}: installed root Zod {installed} does not satisfy shared major {shared_major}")
                failures.append(f"{name}: wrong installed root zod")
            else:
                msg = f"{name}: direct Zod {zod_value}"
                if installed:
                    msg += f"; installed root {installed}"
                out("PASS", msg)
                passes.append(f"{name} zod")

        if isinstance(shared_value, str) and shared_value.startswith("file:"):
            if mode == "--production":
                out("FAIL", f"{name}: production check rejects local shared dependency {shared_value}")
                failures.append(f"{name}: local shared production dependency")
            else:
                out("INFO", f"{name}: local shared link {shared_value}; local-development condition only")
                infos.append(f"{name}: local shared link")
    else:
        if zod_value:
            out("INFO", f"{name}: direct Zod {zod_value}; no runtime shared dependency detected")
        elif installed:
            out("INFO", f"{name}: root Zod {installed} is transitive/tooling; no runtime shared dependency detected")
        else:
            out("INFO", f"{name}: no runtime shared/Zod dependency detected")

print()
print("Development-tool isolation")
for name in ("moda-interact", "moda-interact-background"):
    repo = root / name
    pkg_path = repo / "package.json"
    if not pkg_path.is_file():
        continue
    pkg = load_json(pkg_path) or {}
    erd = (pkg.get("devDependencies") or {}).get("prisma-generator-plantuml-erd")
    if not erd:
        continue
    nested = repo / "node_modules" / "prisma-generator-plantuml-erd" / "node_modules" / "zod" / "package.json"
    nested_version = None
    if nested.is_file():
        data = load_json(nested)
        nested_version = data.get("version") if data else None
    root_version = installed_root_zod(repo)
    if nested_version:
        out("PASS", f"{name}: ERD-generator Zod isolated at {nested_version}; root Zod {root_version or 'not installed'}")
        passes.append(f"{name} erd isolation")
    else:
        out("INFO", f"{name}: ERD generator present; nested Zod not currently inspectable")

print()
print("npm configuration")
found_shamefully = False
for candidate in (root / ".npmrc", root / "moda-interact" / ".npmrc"):
    if not candidate.is_file():
        continue
    text = candidate.read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?m)^\s*shamefully-hoist\s*=", text):
        out("WARN", f"{candidate.relative_to(root)} contains shamefully-hoist; npm reports this as an unknown project config")
        warnings.append("shamefully-hoist")
        found_shamefully = True
if not found_shamefully:
    out("PASS", "no known unsupported shamefully-hoist project config detected")
    passes.append("npm config")

if mode == "--full":
    print()
    print("Full Zod dependency trees")
    for name in repos:
        repo = root / name
        if not (repo / "package.json").is_file() or not (repo / "node_modules").is_dir():
            continue
        print()
        print(f"[{name}] npm ls zod --all")
        result = subprocess.run(
            ["npm", "ls", "zod", "--all"],
            cwd=repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        print(result.stdout.rstrip() or "(no output)")

print()
print("Summary")
out("PASS", f"{len(passes)} checks")
if infos:
    out("INFO", f"{len(infos)} informational condition(s)")
if warnings:
    out("WARN", f"{len(warnings)} warning(s)")
if failures:
    out("FAIL", f"{len(failures)} failure(s)")
    print()
    print("Read docs/development-baseline.md before investigating these conditions.")
    raise SystemExit(1)

print("Workspace development baseline is acceptable for this mode.")
