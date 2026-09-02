const DEVELOPMENT = "development";
const TEST = "test";
const PRODUCTION = "production";

export function resolveDeploymentEnvironmentName(): string {
  const explicit = process.env.DEPLOYMENT_ENVIRONMENT_NAME?.trim().toLowerCase();
  if (explicit) return explicit;

  const nodeEnvironment = process.env.NODE_ENV?.trim().toLowerCase();
  if (nodeEnvironment) return nodeEnvironment;

  // Unknown must never be interpreted as development.
  return "unknown";
}

export function isDevelopmentAuthBypass(): boolean {
  const environment = resolveDeploymentEnvironmentName();

  if (environment !== DEVELOPMENT) return false;

  if (process.env.NODE_ENV === PRODUCTION) {
    throw new Error(
      "Refusing platform-admin authentication bypass: " +
        "DEPLOYMENT_ENVIRONMENT_NAME=development is invalid when NODE_ENV=production.",
    );
  }

  return true;
}

export function assertPlatformAdminAuthConfiguration(): void {
  if (isDevelopmentAuthBypass()) return;

  const environment = resolveDeploymentEnvironmentName();
  const required = [
    "AUTH_SECRET",
    "AUTH_GOOGLE_ID",
    "AUTH_GOOGLE_SECRET",
    "AUTH_URL",
  ] as const;

  const missing = required.filter((name) => !process.env[name]?.trim());

  if (missing.length) {
    throw new Error(
      `Platform-admin authentication is not configured for ${environment}: missing ${missing.join(", ")}.`,
    );
  }
}

export function isHostedAdminEnvironment(): boolean {
  const environment = resolveDeploymentEnvironmentName();
  return environment === TEST || environment === PRODUCTION;
}
