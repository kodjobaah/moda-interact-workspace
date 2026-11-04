#!/usr/bin/env python3
"""Read-only ARCH-055 snapshot dependency audit; no install, DB, or git mutation.

Usage: python3 audit-schema-integration.py /absolute/path/to/workspace > evidence.json
This reports source compatibility, not a successful Prisma build or DB rehearsal.
"""

import argparse
import difflib
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def migrations(directory):
    return {
        str(path.relative_to(directory)): sha256(path.read_bytes())
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def source_lines(root, relative, needle):
    return [
        {"path": relative, "line": number, "text": line.strip()}
        for number, line in enumerate((root / relative).read_text().splitlines(), 1)
        if needle in line
    ]


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("workspace", type=Path)
args = parser.parse_args()
root = args.workspace.resolve(strict=True)
canonical_schema = root / "moda-interact-database/prisma/schema.prisma"
canonical_bytes = canonical_schema.read_bytes()
canonical_migrations = migrations(canonical_schema.parent / "migrations")
api_schema = root / "moda-interact-api/database/prisma/schema.prisma"
api_bytes = api_schema.read_bytes()
repositories = {
    "canonical": "moda-interact-database",
    "api": "moda-interact-api/database",
    "background": "moda-interact-background/database",
    "shopify": "moda-interact/database",
    "admin": "moda-interact-admin/database",
}
copies = {}
for label, relative in repositories.items():
    directory = root / relative
    schema = (directory / "prisma/schema.prisma").read_bytes()
    tree = migrations(directory / "prisma/migrations")
    common = tree.keys() & canonical_migrations.keys()
    copies[label] = {
        "path": str(Path(relative) / "prisma/schema.prisma"),
        "schema_bytes": len(schema),
        "schema_sha256": sha256(schema),
        "model_count": len(re.findall(rb"^model\s+\w+\s*\{", schema, flags=re.M)),
        "schema_equals_canonical": schema == canonical_bytes,
        "migration_file_count": len(tree),
        "sql_migration_count": sum(name.endswith("/migration.sql") for name in tree),
        "common_migration_files": len(common),
        "changed_common_migration_files": sorted(
            name for name in common if tree[name] != canonical_migrations[name]
        ),
        "missing_migration_files": sorted(canonical_migrations.keys() - tree.keys()),
        "extra_migration_files": sorted(tree.keys() - canonical_migrations.keys()),
        "git_metadata_present": (directory / ".git").exists(),
    }

field_contracts = []
for model, field in [
    ("MerchantConversationSendCommand", "followUpClaimKey"),
    ("MerchantKnowledgeUploadedAsset", "intentPurposeKey"),
]:
    def definition(data):
        match = re.search(
            rf"^model\s+{model}\s*\{{(.*?)^\}}", data.decode(), flags=re.M | re.S
        )
        if not match:
            return None
        return next((line.strip() for line in match[1].splitlines()
                     if re.match(rf"\s*{field}\s", line)), None)
    field_contracts.append({"model": model, "field": field,
                            "canonical_definition": definition(canonical_bytes),
                            "api_definition": definition(api_bytes)})

canonical_without_fields = b"".join(
    line for line in canonical_bytes.splitlines(keepends=True)
    if not re.match(rb"\s*(followUpClaimKey|intentPurposeKey)\s", line)
)
packages = {}
for repository in ["moda-interact-api", "moda-interact-background", "moda-interact", "moda-interact-database"]:
    directory = root / repository
    package = json.loads((directory / "package.json").read_text())
    packages[repository] = {
        "node_modules_present": (directory / "node_modules").is_dir(),
        "git_metadata_present": (directory / ".git").exists(),
        "prisma_client_dependency": package.get("dependencies", {}).get("@prisma/client"),
        "prisma_dev_dependency": package.get("devDependencies", {}).get("prisma"),
        "scripts": {key: value for key, value in package.get("scripts", {}).items()
                    if key in {"build", "typecheck", "prisma:generate", "test:arch026-woo-rest-read:postgres",
                               "test:arch035-knowledge-upload:postgres", "test:arch040-human-send:postgres",
                               "test:arch040-background-runtime:postgres", "test:arch040-recovery-conversation",
                               "test:arch055-database-contracts", "test:arch055-database-contracts:postgres:fresh",
                               "test:arch055-database-contracts:postgres:upgrade"}},
    }

selector = {"executed": False, "reason": "node not available"}
node = shutil.which("node")
if node:
    probe = """
      import { pathToFileURL } from 'node:url';
      const root = process.argv[1];
      const selector = await import(pathToFileURL(root + '/moda-interact-api/scripts/arch047-canonical-schema.mjs'));
      const cwd = root + '/moda-interact-api';
      const apiSchema = cwd + '/database/prisma/schema.prisma';
      const canonical = root + '/moda-interact-database/prisma/schema.prisma';
      console.log(JSON.stringify({
        defaultSelection: selector.findAcceptedArch047Schema({cwd,workspaceRoot:root}),
        explicitCanonicalSelection: selector.findAcceptedArch047Schema({cwd,explicitSchema:canonical}),
        staleApiAcceptedAsArch047: selector.isAcceptedArch047Schema(apiSchema),
        commonLineageMatches: selector.isCompatibleMigrationLineage(apiSchema,canonical)
      }));
    """
    result = subprocess.run([node, "--input-type=module", "--eval", probe, str(root)],
                            text=True, capture_output=True, check=False, timeout=20)
    selector = {"executed": True, "exit_code": result.returncode,
                "result": json.loads(result.stdout) if result.returncode == 0 else None,
                "stderr": result.stderr.strip(),
                "scope": "Existing built-in-only schema selector; no app import, Prisma generation, or database call."}

references = []
for relative, field in [
    ("moda-interact-api/src/merchant/conversations/messages/admission.service.ts", "followUpClaimKey"),
    ("moda-interact-api/src/merchant/merchant-knowledge/upload.service.ts", "intentPurposeKey"),
    ("moda-interact/app/services/recoveries/recovery-human-commands.server.ts", "followUpClaimKey"),
    ("moda-interact-background/src/services/recovery-conversation/merchant-send-command.service.ts", "followUpClaimKey"),
    ("moda-interact-background/src/services/recovery-conversation/human-command-dispatcher.service.ts", "followUpClaimKey"),
    ("moda-interact-background/src/services/recovery-conversation/outbound-send-fence.service.ts", "followUpClaimKey"),
    ("moda-interact-background/src/services/recovery-conversation/follow-up-claim-cancellation.service.ts", "followUpClaimKey"),
]:
    references.extend(source_lines(root, relative, field))

api_copy = copies["api"]
api_migration_difference_count = sum(len(api_copy[key]) for key in (
    "missing_migration_files", "extra_migration_files", "changed_common_migration_files"
))
api_field_difference_count = sum(
    contract["api_definition"] != contract["canonical_definition"]
    for contract in field_contracts
)
if api_copy["schema_equals_canonical"] and api_migration_difference_count == 0:
    source_compatibility = "API nested Database schema and migration files match canonical."
else:
    source_compatibility = (
        "API nested Database differs from canonical: "
        f"schema bytes {'match' if api_copy['schema_equals_canonical'] else 'differ'}; "
        f"{api_field_difference_count} differing inspected ARCH-055 field definitions; "
        f"{len(api_copy['missing_migration_files'])} missing migration files; "
        f"{len(api_copy['extra_migration_files'])} extra migration files; "
        f"{len(api_copy['changed_common_migration_files'])} changed common migration files."
    )

evidence = {
    "audit_version": 1,
    "workspace": str(root),
    "scope": "read-only source/dependency audit and existing selector execution",
    "source_compatibility": source_compatibility,
    "copies": copies,
    "field_contracts": field_contracts,
    "canonical_minus_two_field_lines_equals_api_schema": canonical_without_fields == api_bytes,
    "schema_diff_api_to_canonical": "".join(difflib.unified_diff(
        api_bytes.decode().splitlines(keepends=True), canonical_bytes.decode().splitlines(keepends=True),
        fromfile="moda-interact-api/database/prisma/schema.prisma", tofile="moda-interact-database/prisma/schema.prisma")),
    "arch055_migrations": [
        {"path": name, "sha256": digest,
         "bytes": len((canonical_schema.parent / "migrations" / name).read_bytes())}
        for name, digest in canonical_migrations.items() if "arch055" in name
    ],
    "packages": packages,
    "selector_probe": selector,
    "field_source_references": references,
    "not_executed": ["Prisma generation", "TypeScript build/typecheck", "application tests", "PostgreSQL rehearsal",
                     "deployment", "git submodule update", "dependency installation"],
    "limits": ["No real Git pins or merge ancestry can be verified from this source-only export.",
               "Schema/source mismatch is observed; actual compiler/runtime diagnostics were not produced.",
               "Historical task validation reports are documentary evidence, not rerun results."],
}
print(json.dumps(evidence, indent=2))
