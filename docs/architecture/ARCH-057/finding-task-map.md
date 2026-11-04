# Finding disposition and task ownership

All F references identify the unchanged `shopify-database-20261103-235702-r01/review.md`. “Selected” means required implementation under the named task, not implemented or accepted. Every task includes its own server diagnostic matrix; SHOPIFY-011 reconciles the final coverage.

| Finding | Disposition | Owner / bounded outcome |
|---|---|---|
| F01 paid relation and lock order | Selected | ARCH-057-SHOPIFY-002: commerce.Shop and coherent lifecycle order, real migrated concurrency proof |
| F02 malformed provider absence | Selected | ARCH-057-SHOPIFY-002: explicit valid null versus malformed evidence, no projection clearing on malformed input |
| F03 refund network/root reads in transaction | Selected | ARCH-057-SHOPIFY-003: provider preflight and transaction-bound current local admission |
| F04 duplicate uninstall / reinstall credentials | Selected | ARCH-057-SHOPIFY-009: transition-owned cleanup and durable-session gate before scheduling reinstall |
| F05 subscription configuration mismatch | Selected | ARCH-057-SHOPIFY-009: intended named configuration with current handlers; no app-identity merge/version upgrade |
| F06 repeated authenticated resolution | Selected | ARCH-057-SHOPIFY-001, consumed by domain tasks: request-local facts, explicit page/auth profile refresh, local resource lookup |
| F07 badge / per-message acknowledgement / repeated thread write | Selected | ARCH-057-SHOPIFY-005: dedicated unread count, bounded visible-ID batch, atomic thread bookkeeping |
| F08 commercial read overlap / unused aggregate / premature route admission | Selected | ARCH-057-SHOPIFY-004 for read composition; SHOPIFY-003 for purchase replay/admission ownership |
| F09 purchase-history provider N+1 and nested refunds | Selected | ARCH-057-SHOPIFY-003: one provider context and bounded exact refund summaries |
| F10 repeated recovery ownership projection | Selected | ARCH-057-SHOPIFY-006: composed-page owner context, standalone resource authorization |
| F11 settings/source overlapping reads and unused data | Selected | ARCH-057-SHOPIFY-007/008; locked human-command status reuse in SHOPIFY-006 |
| F12 nominal no-op writes | Selected | Billing operations/period in SHOPIFY-002; policy selections in SHOPIFY-007; knowledge order in SHOPIFY-008 |
| F13 extra revalidation/poll lifecycle | Selected, with unconfirmed loop still labelled | ARCH-057-SHOPIFY-008 removes duplicate effect and verifies installed-router deadline; resource context cost reduced by SHOPIFY-001 |
| F14 promotion context/translation bound and usage aggregates | Selected | ARCH-057-SHOPIFY-004; preserve promotion eligibility and resolve test/policy drift explicitly |
| F15 generic ingress/queue work | Selected in part | ARCH-057-SHOPIFY-010 narrows Shop fields, removes unsupported-topic lookup, selects deterministic publication/deadline semantics; lifecycle consolidation in SHOPIFY-009 |
| F15 durable quarantine | Deferred policy | Current inactive/unknown outcome means ACK/discard with truthful diagnostics; no replay store, outbox or new admission policy is introduced |
| F16 suppressed/misclassified operational errors | Selected | Touchpoint owners plus ARCH-057-SHOPIFY-011; original safe messages/causes/codes tested in actual Shared records |
| F16 subscription-ended notice durability | Preserved policy, diagnostics selected | SHOPIFY-011 diagnoses failures; current best-effort notice semantics remain. A required durable notice needs a separate approved transition/retry contract |
| F17 customer export/redaction and Shop deletion graph | Deferred functional scope | Requires explicit retention/export/rehydration ownership across repositories. No automatic cascades, partial “privacy fix”, or revival of superseded ARCH-045 tasks. Remains an open production-functionality gap |
| F18 category lifecycle under lock | Selected | ARCH-057-SHOPIFY-007 requires ACTIVE at commit using existing Shop row lock |
| F18 onboarding/category milestone order | Preserved | ARCH-017/023 separation stays; missing Background activation hook remains with its acknowledged owner |
| New user requirement: runtime naming | Selected | ARCH-057-SHOPIFY-012 removes task labels from runtime names/comments and replaces all three billing namespaces with descriptive canonical names; the user confirmed no legacy preservation is needed; new-format vectors/replay and a zero-exception naming gate are required |
| Global capacity / additional indexes | Not claimed; measure only where selected | Same-fixture SQL/provider evidence is required; 20,000 events/min remains an assumption, not certification |

## Completion meaning

Completing ARCH-057 establishes the selected Shopify persistence, composition, diagnostic and naming outcomes. It does not complete ARCH-056, certify the entire platform, implement privacy fulfilment/erasure, change notice durability or prove a production event rate. The deferred rows remain visible and cannot be silently reported as fixed.
