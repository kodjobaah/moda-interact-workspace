-- Architect reference migration only. moda_database must generate/validate the
-- canonical migration from the accepted Prisma schema.

CREATE TYPE "public"."PlatformAdminRole" AS ENUM ('ADMIN', 'SUPER_ADMIN');

CREATE TABLE "public"."PlatformAdmin" (
    "id" TEXT NOT NULL,
    "provider" TEXT NOT NULL DEFAULT 'google',
    "providerSubject" TEXT,
    "email" TEXT NOT NULL,
    "displayName" TEXT,
    "role" "public"."PlatformAdminRole" NOT NULL DEFAULT 'ADMIN',
    "active" BOOLEAN NOT NULL DEFAULT true,
    "lastLoginAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "PlatformAdmin_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "PlatformAdmin_email_key"
    ON "public"."PlatformAdmin"("email");

CREATE UNIQUE INDEX "PlatformAdmin_provider_providerSubject_key"
    ON "public"."PlatformAdmin"("provider", "providerSubject");

CREATE INDEX "PlatformAdmin_active_role_idx"
    ON "public"."PlatformAdmin"("active", "role");
