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
