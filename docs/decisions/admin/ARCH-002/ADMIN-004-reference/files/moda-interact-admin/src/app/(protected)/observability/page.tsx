import { AdminShell } from "@/components/admin/admin-shell";
import { ObservabilityPanel } from "@/components/admin/observability-panel";
import { getGrafanaNavigation } from "@/lib/observability/grafana";

export default function ObservabilityPage() {
  const navigation = getGrafanaNavigation();

  return (
    <AdminShell active="observability">
      <ObservabilityPanel navigation={navigation} />
    </AdminShell>
  );
}
