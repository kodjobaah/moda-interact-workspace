# ARCH-043 portable task inventory

Source: `moda-interact-workspace(20261017-111156).zip` and `Moda_Interact_Environment_Configuration_Audit_2026-10-17.md`.

Definitions are **not materialised** in the developer's Git branches. Do not create domain `_index.md` until the architecture session is declared complete.

| Domain | Tasks | Ready without new dependencies |
|---|---:|---:|
| admin | 10 | 0 |
| api | 3 | 0 |
| background | 7 | 0 |
| commerce | 1 | 0 |
| database | 10 | 10 |
| gateway | 2 | 0 |
| shared | 4 | 2 |
| shopify | 1 | 0 |
| system-test | 2 | 0 |

## Canonical task files

- `ARCH-043-DATABASE-001` — `docs/decisions/database/ARCH-043/DATABASE-001-knowledge-upload-storage-policy.md` (`ready`)
- `ARCH-043-DATABASE-002` — `docs/decisions/database/ARCH-043/DATABASE-002-woo-coupon-sync-controls.md` (`ready`)
- `ARCH-043-DATABASE-003` — `docs/decisions/database/ARCH-043/DATABASE-003-transcription-selection-policy.md` (`ready`)
- `ARCH-043-DATABASE-004` — `docs/decisions/database/ARCH-043/DATABASE-004-commerce-preview-budget-policy.md` (`ready`)
- `ARCH-043-DATABASE-005` — `docs/decisions/database/ARCH-043/DATABASE-005-grafana-navigation-links.md` (`ready`)
- `ARCH-043-DATABASE-006` — `docs/decisions/database/ARCH-043/DATABASE-006-support-translation-policy.md` (`ready`)
- `ARCH-043-DATABASE-007` — `docs/decisions/database/ARCH-043/DATABASE-007-r2-credential-records.md` (`ready`)
- `ARCH-043-DATABASE-008` — `docs/decisions/database/ARCH-043/DATABASE-008-speech-credential-records.md` (`ready`)
- `ARCH-043-DATABASE-009` — `docs/decisions/database/ARCH-043/DATABASE-009-whatsapp-sender-credential-records.md` (`ready`)
- `ARCH-043-DATABASE-010` — `docs/decisions/database/ARCH-043/DATABASE-010-woo-billing-credential-records.md` (`ready`)
- `ARCH-043-SHARED-001` — `docs/decisions/shared/ARCH-043/SHARED-001-knowledge-policy-contract.md` (`ready`)
- `ARCH-043-SHARED-002` — `docs/decisions/shared/ARCH-043/SHARED-002-publish-knowledge-policy-contract.md` (`pending`)
- `ARCH-043-SHARED-003` — `docs/decisions/shared/ARCH-043/SHARED-003-external-provider-credential-aad.md` (`ready`)
- `ARCH-043-SHARED-004` — `docs/decisions/shared/ARCH-043/SHARED-004-publish-provider-credential-aad.md` (`pending`)
- `ARCH-043-ADMIN-001` — `docs/decisions/admin/ARCH-043/ADMIN-001-knowledge-policy-admin.md` (`pending`)
- `ARCH-043-ADMIN-002` — `docs/decisions/admin/ARCH-043/ADMIN-002-woo-coupon-sync-admin.md` (`pending`)
- `ARCH-043-ADMIN-003` — `docs/decisions/admin/ARCH-043/ADMIN-003-transcription-selection-admin.md` (`pending`)
- `ARCH-043-ADMIN-004` — `docs/decisions/admin/ARCH-043/ADMIN-004-preview-budget-admin.md` (`pending`)
- `ARCH-043-ADMIN-005` — `docs/decisions/admin/ARCH-043/ADMIN-005-grafana-link-admin.md` (`pending`)
- `ARCH-043-ADMIN-006` — `docs/decisions/admin/ARCH-043/ADMIN-006-support-translation-admin.md` (`pending`)
- `ARCH-043-ADMIN-007` — `docs/decisions/admin/ARCH-043/ADMIN-007-r2-credential-admin.md` (`pending`)
- `ARCH-043-ADMIN-008` — `docs/decisions/admin/ARCH-043/ADMIN-008-speech-credential-admin.md` (`pending`)
- `ARCH-043-ADMIN-009` — `docs/decisions/admin/ARCH-043/ADMIN-009-whatsapp-credential-admin.md` (`pending`)
- `ARCH-043-ADMIN-010` — `docs/decisions/admin/ARCH-043/ADMIN-010-woo-billing-credential-admin.md` (`pending`)
- `ARCH-043-BACKGROUND-001` — `docs/decisions/background/ARCH-043/BACKGROUND-001-woo-coupon-runtime-reader.md` (`pending`)
- `ARCH-043-BACKGROUND-002` — `docs/decisions/background/ARCH-043/BACKGROUND-002-knowledge-config-reader.md` (`pending`)
- `ARCH-043-BACKGROUND-003` — `docs/decisions/background/ARCH-043/BACKGROUND-003-transcription-policy-reader.md` (`pending`)
- `ARCH-043-BACKGROUND-004` — `docs/decisions/background/ARCH-043/BACKGROUND-004-support-translation-db-reader.md` (`pending`)
- `ARCH-043-BACKGROUND-005` — `docs/decisions/background/ARCH-043/BACKGROUND-005-r2-credential-reader.md` (`pending`)
- `ARCH-043-BACKGROUND-006` — `docs/decisions/background/ARCH-043/BACKGROUND-006-speech-credential-reader.md` (`pending`)
- `ARCH-043-BACKGROUND-007` — `docs/decisions/background/ARCH-043/BACKGROUND-007-whatsapp-sender-credential-reader.md` (`pending`)
- `ARCH-043-API-001` — `docs/decisions/api/ARCH-043/API-001-knowledge-policy-reader.md` (`pending`)
- `ARCH-043-API-002` — `docs/decisions/api/ARCH-043/API-002-r2-credential-writer.md` (`pending`)
- `ARCH-043-API-003` — `docs/decisions/api/ARCH-043/API-003-woo-billing-credential-reader.md` (`pending`)
- `ARCH-043-SHOPIFY-001` — `docs/decisions/shopify/ARCH-043/SHOPIFY-001-knowledge-upload-policy-reader.md` (`pending`)
- `ARCH-043-COMMERCE-001` — `docs/decisions/commerce/ARCH-043/COMMERCE-001-preview-budget-db-reader.md` (`pending`)
- `ARCH-043-GATEWAY-001` — `docs/decisions/gateway/ARCH-043/GATEWAY-001-remove-migrated-nonsecret-env.md` (`pending`)
- `ARCH-043-GATEWAY-002` — `docs/decisions/gateway/ARCH-043/GATEWAY-002-retire-migrated-provider-secrets.md` (`pending`)
- `ARCH-043-SYSTEM-TEST-001` — `docs/decisions/system-test/ARCH-043/SYSTEM-TEST-001-nonsecret-db-config-cutover.md` (`pending`)
- `ARCH-043-SYSTEM-TEST-002` — `docs/decisions/system-test/ARCH-043/SYSTEM-TEST-002-encrypted-provider-config-cutover.md` (`pending`)
