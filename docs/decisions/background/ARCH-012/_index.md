# ARCH-012 background tasks

> Individual task files are authoritative. Preserve accepted ARCH-007 admission/coalescing/ordering and ARCH-010/014 runtime controls. Shopify recovery timing remains outside ARCH-012.

| Task | Status | Purpose |
|---|---|---|
| [BACKGROUND-001](BACKGROUND-001-consume-canonical-whatsapp-inbound.md) | Pending | Complete inbound pipeline: Shared event, both reply modes, text/unsupported handling, <=120s voice retrieval/transcription and exactly-once turn completion |
| [BACKGROUND-002](BACKGROUND-002-process-whatsapp-voice-notes.md) | Superseded | Voice work folded into BACKGROUND-001 |
| [BACKGROUND-003](BACKGROUND-003-moda-whatsapp-sender-transport.md) | Ready | Moda sender identity + outbound text/link/template media transport |
