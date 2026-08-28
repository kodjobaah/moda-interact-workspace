from pathlib import Path
import tomllib
import json

# Codex agent definitions
CODEX_DIR = Path(".codex/agents")

# Claude agent definitions
CLAUDE_DIR = Path(".claude/agents")


def convert_toml_to_md(toml_path: Path, md_path: Path):
    with toml_path.open("rb") as f:
        data = tomllib.load(f)

    name = data.get("name", "unnamed_agent")
    description = data.get("description", "")
    instructions = data.get("developer_instructions", "").strip()

    # json.dumps produces safely quoted strings that are also valid YAML.
    md_content = f"""---
name: {json.dumps(name)}
description: {json.dumps(description)}
---

{instructions}
"""

    md_path.write_text(md_content, encoding="utf-8")

    print(f"✓ {toml_path} -> {md_path}")


def main():
    CLAUDE_DIR.mkdir(parents=True, exist_ok=True)

    toml_files = sorted(CODEX_DIR.glob("*.toml"))

    if not toml_files:
        print(f"No Codex agent TOML files found in {CODEX_DIR}")
        return

    for toml_path in toml_files:
        # moda_app.toml -> moda_app.agent.md
        md_filename = f"{toml_path.stem}.agent.md"
        md_path = CLAUDE_DIR / md_filename

        convert_toml_to_md(toml_path, md_path)

    print()
    print(f"Synced {len(toml_files)} agent(s).")


if __name__ == "__main__":
    main()
