#!/usr/bin/env python3
"""Produce a bounded, reproducible source inventory; not a runtime query counter.

Usage: python3 audit-source.py WORKSPACE_ROOT OUTPUT_DIRECTORY
Only files under the explicit output directory are written.
"""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import re
import sys

root = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)
app = root / 'moda-interact/app'
sources = sorted(p for p in app.rglob('*') if p.is_file() and p.suffix in {'.ts', '.tsx', '.js', '.jsx'})


def relative(path):
    return path.relative_to(root).as_posix()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name, value):
    (out / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def write_csv(name, fields, rows):
    with (out / name).open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


models = {}
schema_path = root / 'moda-interact/database/prisma/schema.prisma'
for match in re.finditer(r'^model\s+(\w+)\s*\{(.*?)^\}', schema_path.read_text(), re.M | re.S):
    model, body = match.groups()
    schema = re.search(r'@@schema\("([^"\n]+)"\)', body)
    mapped = re.search(r'@@map\("([^"\n]+)"\)', body)
    if schema:
        models[(schema[1], mapped[1] if mapped else model)] = model

# Search is deliberately lexical. Method uses on the known DB/client aliases
# are candidates, reviewed manually in the report. Calls inside helper loops
# appear once here. Includes, retries, SDK SQL and transaction-control SQL are
# not expanded, and the rows must never be summed as a per-request SQL budget.
client = r'(?P<client>(?:(?:this|deps|dependencies|options)\s*\.\s*)?(?:prisma|db|database|transaction|tx|client))'
methods = r'(?:findUniqueOrThrow|findFirstOrThrow|findUnique|findFirst|findMany|count|aggregate|groupBy|createManyAndReturn|updateManyAndReturn|createMany|updateMany|deleteMany|create|update|upsert|delete)'
model_call = re.compile(client + r'\s*\.\s*(?P<model>\w+)\s*\.\s*(?P<operation>' + methods + r')\s*\(')
raw_call = re.compile(client + r'\s*\.\s*(?P<operation>\$(?:queryRawUnsafe|executeRawUnsafe|queryRaw|executeRaw|transaction))\b')
calls, relations = [], []
for path in sources:
    text = path.read_text()
    for pattern in (model_call, raw_call):
        for match in pattern.finditer(text):
            op = match['operation']
            kind = ('transaction_wrapper' if op == '$transaction' else
                    'raw_query' if op.startswith('$') else
                    'read' if op.startswith('find') or op in {'count', 'aggregate', 'groupBy'} else 'write')
            calls.append({'file': relative(path), 'line': text.count('\n', 0, match.start()) + 1,
                          'client': re.sub(r'\s+', '', match['client']),
                          'model': match.groupdict().get('model') or '', 'operation': op, 'kind': kind})
    for match in re.finditer(r'\b(?:FROM|JOIN|UPDATE|INTO)\s+"(\w+)"\."(\w+)"', text, re.I):
        key = match[1], match[2]
        relations.append({'file': relative(path), 'line': text.count('\n', 0, match.start()) + 1,
                          'schema': key[0], 'table': key[1], 'exists_in_prisma': key in models})
calls.sort(key=lambda row: (row['file'], row['line'], row['operation']))
write_csv('database-call-inventory.csv', ['file', 'line', 'client', 'model', 'operation', 'kind'], calls)
write_csv('raw-sql-relation-inventory.csv', ['file', 'line', 'schema', 'table', 'exists_in_prisma'], relations)

routes, in_app = [], False
for line in (app / 'routes.ts').read_text().splitlines():
    if re.search(r'route\("app",', line):
        in_app = True
        parent = ''
    else:
        parent = '/app' if in_app else ''
    route = re.search(r'route\("([^"]+)"\s*,\s*"(\./routes/[^"]+)"', line)
    index = re.search(r'index\("(\./routes/[^"]+)"', line)
    if route or index:
        fragment, file = (route[1], route[2]) if route else ('', index[1])
        url = '/' + '/'.join(part.strip('/') for part in (parent, fragment) if part)
        path = app / file[2:]
        body = path.read_text()
        handlers = set(re.findall(r'export\s+(?:(?:async\s+)?function|const)\s+(loader|action)\b', body))
        for block in re.findall(r'export\s*\{([^}]+)\}', body):
            handlers.update(re.findall(r'\b(loader|action)\b', block))
        routes.append({'url': url, 'file': relative(path), 'handlers': ','.join(sorted(handlers)),
                       'app_layout': bool(parent), 'registered_module': True})
    if in_app and line.strip() == ']),':
        in_app = False
write_csv('route-inventory.csv', ['url', 'file', 'handlers', 'app_layout', 'registered_module'], routes)

nested = root / 'moda-interact/database/prisma/migrations'
canonical = root / 'moda-interact-database/prisma/migrations'
migration_files = sorted(p for p in nested.rglob('*') if p.is_file())
mismatches = [p.relative_to(nested).as_posix() for p in migration_files
              if not (canonical / p.relative_to(nested)).is_file()
              or p.read_bytes() != (canonical / p.relative_to(nested)).read_bytes()]
extra = [p.relative_to(canonical).as_posix() for p in canonical.rglob('*') if p.is_file()
         and not (nested / p.relative_to(canonical)).exists()]
lock = json.loads((root / 'moda-interact/package-lock.json').read_text())
packages = ['@modainteract/moda-interact-shared', '@prisma/client', 'prisma', 'react-router',
            '@react-router/dev', '@shopify/shopify-app-react-router',
            '@shopify/shopify-app-session-storage-prisma', 'bullmq', 'pg', 'vitest']
baseline_files = sources + [root / 'moda-interact/package.json', root / 'moda-interact/package-lock.json',
                           schema_path, root / 'moda-interact-database/prisma/schema.prisma'] + migration_files
write_json('source-baseline.json', {
    'scope': 'uploaded Shopify application source and its database snapshot',
    'git_history_present': (root / '.git').exists(),
    'node_modules_present': (root / 'moda-interact/node_modules').exists(),
    'source_files': len(sources), 'route_modules': len(routes),
    'lexical_database_candidates': len(calls),
    'candidate_kinds': dict(Counter(row['kind'] for row in calls)),
    'call_inventory_limitations': 'Lexical candidate inventory, manually reviewed; not AST-complete, runtime calls, SQL statements, latency or capacity.',
    'raw_relation_references': len(relations),
    'missing_raw_relations': [row for row in relations if not row['exists_in_prisma']],
    'nested_schema_identical_to_canonical': schema_path.read_bytes() == (root / 'moda-interact-database/prisma/schema.prisma').read_bytes(),
    'nested_migration_files': len(migration_files),
    'migration_mismatches': mismatches, 'canonical_extra_migration_files': extra,
    'locked_packages': {name: lock['packages'].get('node_modules/' + name, {}).get('version') for name in packages},
    'sha256': {relative(path): sha(path) for path in baseline_files},
})
print(json.dumps({'source_files': len(sources), 'routes': len(routes), 'candidate_calls': len(calls),
                  'candidate_kinds': dict(Counter(row['kind'] for row in calls)),
                  'raw_relation_references': len(relations),
                  'missing_raw_relations': [row for row in relations if not row['exists_in_prisma']],
                  'output_directory': str(out)}, indent=2))
