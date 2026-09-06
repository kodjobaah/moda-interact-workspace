# ARCH-005 — Shared Tasks

| Task | Description | Status | Dependencies |
|---|---|---|---|
| ARCH-005-SHARED-001 | Define canonical international context contracts | Complete | — |
| ARCH-005-SHARED-002 | Publish internationalisation shared contract release | Complete | SHARED-001 |
| ARCH-005-SHARED-003 | Extend Shopify recovery events with canonical international context | Complete | SHARED-002 |
| ARCH-005-SHARED-004 | Publish Shopify international-context event contract | Complete | SHARED-003 |
| ARCH-005-SHARED-005 | Implement reusable ICU MessageFormat internationalisation runtime | Complete | SHARED-004 |
| ARCH-005-SHARED-006 | Publish shared ICU internationalisation runtime | Complete | SHARED-005 |

There is currently no executable ARCH-005 Shared task.

SHARED-006 is architect-accepted and published as:

```text
@modainteract/moda-interact-shared@0.6.3
```

Shopify and Admin may now consume that exact developer-published revision.

New ICU rollout:

```text
SHARED-005 implement ICU runtime
  -> SHARED-006 publish exact package revision
  -> SHOPIFY-002 / ADMIN-001 consumer adoption
```

The new tasks are required because the existing Shopify V2 recovery event
schemas are strict. SHARED-001 created `InternationalContext`, but intentionally
did not extend existing Shopify events. SHARED-003 adds the optional canonical
field and SHARED-004 publishes it before consumer adoption.

Required rollout:

```text
SHARED-003
  -> SHARED-004
  -> BACKGROUND-001 consumer adoption
  -> SHOPIFY-003 producer emission
```

This ordering prevents a new Shopify producer from sending a field to an older
strict Background parser.


## Architect review — SHARED-001 attempt 1

```text
Changes Requested
```

Exact ISO 3166-1 alpha-2 membership must replace the broader ICU/CLDR region
recognition heuristic.

Historical execution at that review:

```text
ARCH-005-SHARED-001   Ready — attempt 2 correction
ARCH-005-SHARED-002   Pending
```


## Architect review — SHARED-001 attempt 2

```text
Changes Requested
```

The exact ISO membership approach is correct, but the immutable table contains
248 assigned codes and omits valid ISO 3166-1 alpha-2 code `AX`.

Historical execution at that review:

```text
ARCH-005-SHARED-001   Ready — bounded completeness correction
ARCH-005-SHARED-002   Pending
```


## Architect review — SHARED-001 attempt 3

```text
Changes Requested
```

The requested `AX` correction was not present in the supplied source.

Historical execution at that review:

```text
ARCH-005-SHARED-001   Ready — source correction required
ARCH-005-SHARED-002   Pending
```


## Architect review — SHARED-001 attempt 4

```text
Accepted
```

Current Shared state:

```text
ARCH-005-SHARED-001   Complete
ARCH-005-SHARED-002   Ready
```


## Architect review — SHARED-002 attempt 1

```text
Accepted
```

Published release:

```text
@modainteract/moda-interact-shared@0.6.1
```


## Architect review — SHARED-003 attempt 1

```text
Accepted
```

The optional canonical `internationalContext` field is accepted on the existing
strict V2 recovery envelope. Because Moda Interact remains pre-production with
no queued/persisted V2 event population, the V2 contract is not being treated
as a frozen production compatibility boundary for this correction.

Current Shared state:

```text
ARCH-005-SHARED-003   Complete
ARCH-005-SHARED-004   Ready
```

Consumer-first runtime ordering remains mandatory:

```text
SHARED-004 publication
  -> BACKGROUND-001 consumer adoption
  -> SHOPIFY-003 producer emission
```


## Architect review — SHARED-004 attempt 1

```text
Accepted
```

Published release:

```text
@modainteract/moda-interact-shared@0.6.2
```

Dependency result:

```text
ARCH-005-BACKGROUND-001   Ready
ARCH-005-SHOPIFY-003      Pending
```

Background must adopt the published parser before Shopify begins emitting the
optional international context.


## Architect review — SHARED-005 attempt 1

```text
Changes Requested
```

The ICU architecture is retained, but explicit formatter dimensions must be
non-overridable, direction resolution must use the current `getTextInfo()` API
with legacy/deterministic fallback, and the built `./internationalization`
package subpath must be proven before acceptance.

Current Shared state:

```text
ARCH-005-SHARED-005   Ready — Attempt 2 bounded correction
ARCH-005-SHARED-006   Pending
```

Consumers remain blocked/pending until SHARED-006 publishes the architect-
accepted runtime.


## Architect review — SHARED-005 attempt 2

```text
Accepted
```

The explicit currency/percent/time-zone invariants, standards-aware direction
resolution and built `./internationalization` package-entrypoint validation are
accepted.

Current Shared state:

```text
ARCH-005-SHARED-005   Complete
ARCH-005-SHARED-006   Ready
```

Consumer adoption remains gated on the publication task.


## Architect review — SHARED-006 attempt 1

```text
Accepted
```

Published release:

```text
@modainteract/moda-interact-shared@0.6.3
```

Recorded registry integrity:

```text
sha512-QdGfpV+hX5ut/vmR+RD3fQ/Tyy978A1J58hVf9+Ro2f6jq+f09jB4Jf5fPFxzgsAIsXx0/ftO+FChpa+w1cAAg==
```

Dependency result:

```text
ARCH-005-SHOPIFY-002   Ready — next claim Attempt 5
ARCH-005-ADMIN-001     Ready — first claim Attempt 1
```
