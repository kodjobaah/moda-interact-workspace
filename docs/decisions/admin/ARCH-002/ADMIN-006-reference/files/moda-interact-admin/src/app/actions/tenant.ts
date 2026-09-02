"use server";

import { ShopStatus } from "@prisma/client";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";

import { requirePlatformAdminMutation } from "@/lib/auth/platform-admin";
import { prisma } from "@/lib/prisma";

function safeReturnTo(value: FormDataEntryValue | null): string {
  if (typeof value !== "string" || !value.startsWith("/") || value.startsWith("//")) {
    return "/";
  }
  return value;
}

export async function updateTenantAction(formData: FormData) {
  // Security boundary comes first. Do not rely on the page/layout having rendered.
  await requirePlatformAdminMutation();

  const shopId = formData.get("shopId");
  const rawStatus = formData.get("status");
  const rawDelay = formData.get("recoveryDelayMinutes");
  const returnTo = safeReturnTo(formData.get("returnTo"));

  if (typeof shopId !== "string" || !shopId) {
    throw new Error("A shop id is required.");
  }

  const editableStatuses: ShopStatus[] = [ShopStatus.ACTIVE, ShopStatus.SUSPENDED];
  if (typeof rawStatus !== "string" || !editableStatuses.includes(rawStatus as ShopStatus)) {
    throw new Error("Invalid shop status.");
  }

  const recoveryDelayMinutes = Number.parseInt(String(rawDelay ?? ""), 10);
  if (!Number.isFinite(recoveryDelayMinutes) || recoveryDelayMinutes < 0 || recoveryDelayMinutes > 10080) {
    throw new Error("Recovery delay must be between 0 and 10080 minutes.");
  }

  await prisma.$transaction([
    prisma.shop.update({
      where: { id: shopId },
      data: { status: rawStatus as ShopStatus },
    }),
    prisma.shopSettings.upsert({
      where: { shopId },
      create: { shopId, recoveryDelayMinutes },
      update: { recoveryDelayMinutes },
    }),
  ]);

  revalidatePath("/");
  redirect(returnTo.includes("?") ? `${returnTo}&saved=1` : `${returnTo}?saved=1`);
}
