import "server-only";

type GrafanaLink = {
  label: string;
  description: string;
  href: string;
};

export type GrafanaNavigation = {
  environment: string;
  baseUrl: string | null;
  links: GrafanaLink[];
  configured: boolean;
};

function deploymentEnvironment(): string {
  return process.env.DEPLOYMENT_ENVIRONMENT_NAME?.trim() || process.env.NODE_ENV || "development";
}

function safeGrafanaUrl(raw: string | undefined, environment: string): string | null {
  if (!raw?.trim()) return null;

  try {
    const url = new URL(raw.trim());
    const localDevelopment = environment === "development" && ["localhost", "127.0.0.1"].includes(url.hostname);

    if (url.protocol !== "https:" && !(localDevelopment && url.protocol === "http:")) {
      return null;
    }

    url.username = "";
    url.password = "";
    return url.toString();
  } catch {
    return null;
  }
}

export function getGrafanaNavigation(): GrafanaNavigation {
  const environment = deploymentEnvironment();
  const baseUrl = safeGrafanaUrl(process.env.GRAFANA_BASE_URL, environment);

  const candidates: Array<[string, string, string | undefined]> = [
    ["Platform dashboard", "Open the main Moda Interact operational dashboard.", process.env.GRAFANA_PLATFORM_DASHBOARD_URL],
    ["Logs", "Search private application and infrastructure logs in Grafana.", process.env.GRAFANA_LOGS_URL],
    ["Traces", "Inspect distributed traces and request correlation in Grafana.", process.env.GRAFANA_TRACES_URL],
    ["Metrics", "Inspect platform and service metrics in Grafana.", process.env.GRAFANA_METRICS_URL],
  ];

  const links = candidates.flatMap(([label, description, raw]) => {
    const href = safeGrafanaUrl(raw, environment);
    return href ? [{ label, description, href }] : [];
  });

  return {
    environment,
    baseUrl,
    links,
    configured: links.length > 0 || baseUrl !== null,
  };
}
