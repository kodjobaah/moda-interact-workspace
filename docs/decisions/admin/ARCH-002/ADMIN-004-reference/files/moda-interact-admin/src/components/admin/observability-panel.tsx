import { Icon } from "./icons";
import type { GrafanaNavigation } from "@/lib/observability/grafana";

function environmentLabel(environment: string) {
  return environment.charAt(0).toUpperCase() + environment.slice(1);
}

export function ObservabilityPanel({ navigation }: { navigation: GrafanaNavigation }) {
  return (
    <div className="flex-1 overflow-auto bg-gray-50 p-5 sm:p-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--brand-700)]">Operations</p>
            <h1 className="mt-1 text-3xl font-bold tracking-tight text-gray-950">System observability</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-gray-600">
              Open Moda Interact&apos;s private Grafana Cloud dashboards, logs, traces and metrics.
              Grafana uses its own authenticated session and may ask you to sign in.
            </p>
          </div>

          <div className="inline-flex w-fit items-center rounded-full border border-[var(--brand-200)] bg-white px-3 py-1.5 text-sm font-semibold text-[var(--brand-900)] shadow-sm">
            {environmentLabel(navigation.environment)}
          </div>
        </div>

        {!navigation.configured ? (
          <div className="rounded-xl border border-amber-200 bg-amber-50 p-6">
            <h2 className="text-base font-semibold text-amber-950">Grafana access is not configured</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-amber-900/80">
              This Admin environment does not currently have a Grafana dashboard URL configured.
              Other administration features remain available.
            </p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {navigation.links.map((link) => (
              <a
                key={link.label}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="group rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition hover:border-[var(--brand-300)] hover:shadow-md"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-950">{link.label}</h2>
                    <p className="mt-2 text-sm leading-6 text-gray-600">{link.description}</p>
                  </div>
                  <Icon name="external" className="h-5 w-5 shrink-0 text-[var(--brand-700)]" />
                </div>
                <p className="mt-5 text-sm font-semibold text-[var(--brand-800)]">Open in Grafana ↗</p>
              </a>
            ))}

            {navigation.links.length === 0 && navigation.baseUrl ? (
              <a
                href={navigation.baseUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="group rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition hover:border-[var(--brand-300)] hover:shadow-md"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-950">Grafana Cloud</h2>
                    <p className="mt-2 text-sm leading-6 text-gray-600">Open the private Moda Interact Grafana Cloud workspace.</p>
                  </div>
                  <Icon name="external" className="h-5 w-5 shrink-0 text-[var(--brand-700)]" />
                </div>
              </a>
            ) : null}
          </div>
        )}

        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-5 text-sm leading-6 text-gray-600">
          Operational telemetry remains private. Do not create public/shared Grafana dashboards to bypass Grafana authentication.
        </div>
      </div>
    </div>
  );
}
