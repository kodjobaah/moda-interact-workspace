import { createLogger } from "@modainteract/moda-interact-shared/logging";

import { resolveDeploymentEnvironmentName } from "@/lib/auth/environment";

const logger = createLogger({
  serviceNamespace: "moda-interact",
  serviceName: "moda-interact-admin",
  environment: resolveDeploymentEnvironmentName(),
});

export type AdminSecurityAudit = {
  adminId?: string;
  role?: string;
  action?: string;
  resourceType?: string;
  resourceId?: string;
  outcome: "allowed" | "denied" | "succeeded" | "failed";
  reasonCode?: string;
  developmentBypass?: boolean;
};

export function logAdminSecurityEvent(event: string, data: AdminSecurityAudit): void {
  // The shared logger owns redaction, output bounds, OTel Logs and optional Loki.
  // Do not pass cookies, auth headers, OAuth profiles/codes/tokens or raw payloads.
  logger.info(event, data);
}
