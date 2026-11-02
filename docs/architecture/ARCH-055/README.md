# ARCH-055 portable definition packet

Start with `../ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. This packet defines **13 tasks**, not 61 endpoint tasks.

- `review-report.md`: substantively unchanged Markdown of the completed review report, with trailing whitespace normalised.
- `review-ledger.md`: substantively unchanged cumulative thirteen-increment ledger, with trailing whitespace normalised.
- `review-endpoint-inventory.json`: frozen original inventory.
- `endpoint-task-map.csv`: all 61 routes assigned once to a primary API owner, with retained and measure-first treatment.
- `finding-task-map.json`: stable finding headings mapped to owners.
- `task-manifest.json`: paths, initial status, dependencies and enables.
- `source-baseline.json`: source/report provenance and additional inspected producer hashes.

## Additional producer check

The Shopify code at `moda-interact/app/services/recoveries/recovery-human-commands.server.ts:254` writes `initiationKey: input.idempotencyKey`; its command create follows at lines 260–278. Woo admission does the same at `moda-interact-api/src/merchant/conversations/messages/admission.service.ts:172`. Background compares these keys in its dispatcher, outbound fence and cancellation repair. These inspected touchpoints require a Shopify-owned producer task when the shared persisted claim contract changes. This narrow compatibility work is the sole scope extension beyond the 61 hosted API routes.

## Materialisation

All task definitions are currently external to the developer's Git state: **defined but not materialised**. Run the canonical `/moda-task <TASK_ID>` materialisation/preparation workflow with the supplied task file only when its dependencies are Complete. Do not claim an implementation branch/worktree exists just because the definition patch is applied.

No `_index.md`, existing task status, schema or runtime source file is part of this definition patch.

## Definition revision2

Read `task-definition-contract.md` and `deterministic-execution-map.json` with the canonical tasks. Database has exact Prisma fragments, complete expected forward SQL, package additions and F/U tests; consumer tasks have exact edit maps/interfaces/regression outcomes. Workflow policy stays in services. No new task or endpoint was added.

This revision is a documentation-only follow-up to the original attempt1 packet. Do not apply it over active implementation claims/reports or an already executed conflicting ARCH-055 migration without reconciliation. The frozen review-ledger/report/inventory files are unchanged.

## Definition revision 3

Small follow-up to unchanged revision-2 definitions: exact REST/billing current-principal error mappings, feature-preference C03a–c outcomes, and fixed API measurement profiles. Read the three amended task files and the shared `task-definition-contract.md`; `deterministic-execution-map.json` points to the authoritative contracts. The task manifest marks only API-001/003/007 as revision3; other task texts remain revision2. Thirteen tasks, all execution metadata/dependencies, Database SQL and frozen review files are unchanged. Do not apply over live claims/reports without reconciliation.
