# Data Architecture

Document shared data ownership, tenant boundaries and persistence decisions
here.

Key topics:

- `Shop` and `shopId` tenant isolation
- CheckoutRecovery and conversation state
- UsageEvent idempotency
- Prisma schema ownership
- PostgreSQL schemas, indexes and retention
- Redis and BullMQ as coordination infrastructure
