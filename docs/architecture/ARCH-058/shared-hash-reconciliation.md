# ARCH-058 revision 10: Remove redundant built-in contract hashes

**Decision: remove the built-in `contractHash` mechanism rather than stabilize it.** The historical Shared 4.0.0 artifact proved that runtime-generated schema serialization can change underneath a fixed descriptor hash when a consumer resolves a different compatible Zod minor. ARCH-058 already has an immutable built-in identity: `toolName + definitionVersion`. The hash duplicates that identity and creates a second failure mode without authorizing or securing the tool.

This revision supersedes the unexecuted revision-9 Zod-pinning plan. Do not implement SHARED-003/004 from revision 9, do not pin MCP/Commerce/Background to Zod 4.4.3 because of the descriptor mismatch, and do not replace the recorded hashes with new values.

## Current source facts

The 2026-11-04 16:52 snapshot contains:

- accepted Shared 4.0.0 source with `contractHash` on `CommerceBuiltInToolDescriptorSchema` and `CommerceBuiltInToolGrantSchema`;
- `commerceBuiltInToolContractPayload()` generating output schema via runtime `z.toJSONSchema(...)`;
- accepted DATABASE-001 SQL requiring exactly `kind/toolName/definitionVersion/contractHash` for built-in grant JSON;
- unused public `CommerceConversationToolContextSchema` / type in Shared;
- Commerce `DateSchema = z.iso.datetime({offset:false})`, whose minute-only acceptance was observed to differ between the 4.4.3 and 4.6.5 consumer graphs;
- MCP-002 preserved at Attempt 1 with a WIP implementation and the reproduced hash blocker.

The historical reproduction evidence remains in `shared-hash-reconciliation-evidence.json`; only its previously selected Zod-pinning remedy is superseded.

## Selected correction

`toolName + definitionVersion` is the durable built-in contract identity. SHARED-003 may retain `1.0.0` only as an unpublished intermediate because it removes redundant metadata without changing wire semantics. SHARED-005 intentionally changes `CommerceOfferSchema` timestamp acceptance, so it must bump both discount built-ins to `2.0.0`; DATABASE-002 upgrades persisted development grants accordingly before consumers use Shared 5.0.0. No corrected consumer accepts the legacy `1.0.0` built-in identity.


| Task | Owner | Exact responsibility |
| --- | --- | --- |
| `ARCH-058-SHARED-003` | Shared | Remove `contractHash` and `commerceBuiltInToolContractPayload`; built-in identity becomes name + definitionVersion. |
| `ARCH-058-SHARED-004` | Shared | Remove the unused conversation-specific MCP tool-context export while preserving legitimate Background/runner and outreach contracts. |
| `ARCH-058-SHARED-005` | Shared | Replace version-sensitive discount option/detail timestamp validation with one explicit UTC seconds-based syntax and bump both changed discount built-ins to `2.0.0`. |
| `ARCH-058-SHARED-006` | Shared publication | Publish the accepted combined breaking correction as approved target 5.0.0, subject to registry availability at execution time. |
| `ARCH-058-DATABASE-002` | Database | Forward-migrate persisted built-in grants from hashed `1.0.0` to no-hash `2.0.0`, preserving existing rows/order and all published-grant invariants. |
| `ARCH-058-MCP-002` | MCP | Resume the preserved draft only after DATABASE-002 and SHARED-006 are accepted; consume 5.0.0 and remove hash assertions/use. |

No Admin work, taxonomy re-import, new database column, duplicate descriptor, package-wide Zod pin or compatibility union is introduced.

## Final built-in identity

Descriptor identity:

```text
commerce_get_discount_options@2.0.0
commerce_get_discount_details@2.0.0
```

Persisted built-in grant:

```json
{
  "kind": "BUILT_IN",
  "toolName": "commerce_get_discount_options",
  "definitionVersion": "2.0.0"
}
```

`definitionVersion` is the immutable wire/tool identity. A future change to a built-in's accepted input/output/meaning requires the owning architecture to change `definitionVersion`; an implementation or internal performance change does not.

## Why no compatibility branch

ARCH-058 is pre-production. The final Shared schemas and Database guard accept only the corrected no-hash shape. DATABASE-002 deterministically rewrites existing development grant rows before corrected consumers are deployed. Do not add `contractHash?: string`, an old/new union, a legacy matcher or a runtime fallback.

## Shared package version

Removing public fields/helper exports and narrowing a public datetime validator are breaking public API/package changes under Shared's own semantic-versioning policy. SHARED-006 therefore uses approved target **5.0.0**, not 4.0.1. The publication task must recheck registry availability immediately before release and stop for architect reconciliation if 5.0.0 is already occupied.

The two final Commerce built-in `definitionVersion` values are **2.0.0** because SHARED-005 changes their accepted output timestamp semantics. npm package version and tool definition version are separate identities.

## Zod decision

No ARCH-058 task pins MCP, Commerce or Background to Zod 4.4.3. Existing repository dependency choices remain under their owners. The observed semantic drift relevant to the two discount built-in outputs is removed by SHARED-005's internal Shared-owned timestamp validator in `src/commerce/schemas.ts`; the general `DateSchema` and unrelated contracts remain unchanged. Hashing generated JSON Schema is deleted rather than stabilized.

## MCP-002 continuation

MCP-002 remains preserved at Attempt 1 but is architecturally blocked until both corrected prerequisites are complete:

```text
ARCH-058-DATABASE-002
ARCH-058-SHARED-006
```

After those tasks are accepted and integrated, MCP-002 may be returned to Ready and reclaimed through the normal launcher. Its WIP source is not reverted. The resumed task removes the failed hash proof, installs exact Shared 5.0.0 through the normal package/lock workflow, keeps the repository's own Zod dependency unchanged unless independently required by that repository, regenerates Prisma against the accepted Database pin, then completes its original product/discount work and validation.
