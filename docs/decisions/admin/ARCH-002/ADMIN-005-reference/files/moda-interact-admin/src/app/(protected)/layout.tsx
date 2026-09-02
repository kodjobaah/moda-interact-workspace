import type { ReactNode } from "react";

import { requirePlatformAdminPage } from "@/lib/auth/platform-admin";

export const dynamic = "force-dynamic";

export default async function ProtectedAdminLayout({ children }: { children: ReactNode }) {
  await requirePlatformAdminPage();
  return children;
}
