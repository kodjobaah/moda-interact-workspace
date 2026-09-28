#!/usr/bin/env python3
from pathlib import Path
import shutil
import re

overlay = Path(__file__).resolve().parent
workspace = Path.cwd().resolve()

if not (workspace / ".codex" / "agents").is_dir():
    raise SystemExit(
        "ERROR: run this script from the moda-interact-workspace root."
    )

task_rel = Path(
    "docs/decisions/shopify/ARCH-002/"
    "SHOPIFY-005-eliminate-typescript-baseline-debt.md"
)
index_rel = Path("docs/decisions/shopify/ARCH-002/_index.md")

src_task = overlay / task_rel
dst_task = workspace / task_rel
index = workspace / index_rel

if not src_task.is_file():
    raise SystemExit(f"ERROR: overlay task missing: {task_rel}")

if not index.is_file():
    raise SystemExit(f"ERROR: workspace index missing: {index_rel}")

# Refuse to silently replace an existing different task.
if dst_task.exists():
    existing = dst_task.read_text(encoding="utf-8")
    supplied = src_task.read_text(encoding="utf-8")
    if existing != supplied:
        raise SystemExit(
            f"ERROR: {task_rel} already exists with different content. "
            "No files were changed."
        )
    print(f"UNCHANGED {task_rel}")
else:
    dst_task.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_task, dst_task)
    print(f"CREATED   {task_rel}")

text = index.read_text(encoding="utf-8")
row = (
    "| SHOPIFY-005 | Eliminate existing Shopify application TypeScript "
    "baseline debt | Ready | SHOPIFY-002 |"
)

if re.search(r"(?m)^\|\s*SHOPIFY-005\s*\|", text):
    # Idempotent only when our exact row is already present.
    if row not in text:
        raise SystemExit(
            "ERROR: SHOPIFY-005 already exists in the index with different "
            "content. Task file may have been created, but index was not changed."
        )
    print(f"UNCHANGED {index_rel}")
else:
    # Insert after SHOPIFY-004 where possible.
    pattern = re.compile(r"(?m)^(\|\s*SHOPIFY-004\s*\|.*\|)$")
    match = pattern.search(text)

    if match:
        text = text[:match.end()] + "\n" + row + text[match.end():]
    else:
        # Safe fallback: insert before Environment model only if task table is present.
        marker = "\nEnvironment model:"
        if marker not in text or "| Task | Description | Status | Dependencies |" not in text:
            raise SystemExit(
                "ERROR: could not find a safe insertion point in the Shopify "
                "ARCH-002 index. Index was not changed."
            )
        text = text.replace(marker, "\n" + row + "\n" + marker, 1)

    index.write_text(text, encoding="utf-8")
    print(f"UPDATED   {index_rel}")

print()
print("ARCH-002-SHOPIFY-005 is ready for moda_app.")
print()
print("Suggested handoff:")
print(
    "@moda_app start ARCH-002-SHOPIFY-005. Read the task file, "
    "eliminate the documented TypeScript baseline without weakening "
    "typechecking, validate npm run typecheck reaches zero, then return "
    "the task with status: review."
)
