import { AdminShell } from "@/components/admin/admin-shell";
import { ObservabilityPanel } from "@/components/admin/observability-panel";
import { requirePlatformAdminPage } from "@/lib/auth/platform-admin";

export default async function ObservabilityPage() {
  await requirePlatformAdminPage();
  return (
    <AdminShell active="observability">
      <ObservabilityPanel />
    </AdminShell>
  );
}
