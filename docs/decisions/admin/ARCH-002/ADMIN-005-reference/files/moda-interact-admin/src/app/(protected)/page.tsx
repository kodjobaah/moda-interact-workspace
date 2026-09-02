import { AdminShell } from "@/components/admin/admin-shell";
import { KpiCard } from "@/components/admin/kpi-card";
import { RecoveryDrawer, type DrawerTab } from "@/components/admin/recovery-drawer";
import { TenantTable } from "@/components/admin/tenant-table";
import { requirePlatformAdminPage } from "@/lib/auth/platform-admin";
import {
  getCustomerRecoveries,
  getRecoveryDetail,
  getTenantCustomers,
  getTenantDetail,
  getTenantDirectory,
} from "@/lib/admin/data";
import type { CustomerListItem, PageResult, RecoveryListItem } from "@/lib/admin/types";
import {
  cleanSearch,
  firstParam,
  paramsToRecord,
  positiveInt,
  withParamUpdates,
  type SearchParamRecord,
} from "@/lib/admin/query";

export const dynamic = "force-dynamic";

const TENANT_PAGE_SIZE = 10;
const CUSTOMER_PAGE_SIZE = 8;
const RECOVERY_PAGE_SIZE = 8;
const MESSAGE_PAGE_SIZE = 20;

type PageProps = {
  searchParams: Promise<SearchParamRecord>;
};

export default async function Home({ searchParams }: PageProps) {
  await requirePlatformAdminPage();
  const rawParams = await searchParams;
  const params = paramsToRecord(rawParams);
  const search = cleanSearch(rawParams.q);
  const tenantPage = positiveInt(rawParams.page);
  const tenantId = firstParam(rawParams.tenant) ?? null;
  const tab = firstParam(rawParams.tab) === "logs" ? "logs" : "admin";
  const customerSearch = cleanSearch(rawParams.customerSearch);
  const customerPage = positiveInt(rawParams.customerPage);
  const customerId = firstParam(rawParams.customerId) ?? null;
  const recoveryPage = positiveInt(rawParams.recoveryPage);
  const recoveryId = firstParam(rawParams.recoveryId) ?? null;
  const messagePage = positiveInt(rawParams.messagePage);
  const rawDrawerTab = firstParam(rawParams.drawerTab);
  const drawerTab: DrawerTab = rawDrawerTab === "cart" || rawDrawerTab === "lifecycle" ? rawDrawerTab : "conversation";
  const saved = firstParam(rawParams.saved) === "1";

  const directory = await getTenantDirectory({
    page: tenantPage,
    pageSize: TENANT_PAGE_SIZE,
    search,
  });

  const selectedTenant = tenantId ? await getTenantDetail(tenantId) : null;

  let customers: PageResult<CustomerListItem> | null = null;
  let selectedCustomer: CustomerListItem | null = null;
  let recoveries: PageResult<RecoveryListItem> | null = null;

  if (selectedTenant && tab === "logs") {
    customers = await getTenantCustomers({
      shopId: selectedTenant.id,
      page: customerPage,
      pageSize: CUSTOMER_PAGE_SIZE,
      search: customerSearch,
    });

    if (customerId) {
      const recoveryData = await getCustomerRecoveries({
        shopId: selectedTenant.id,
        customerId,
        page: recoveryPage,
        pageSize: RECOVERY_PAGE_SIZE,
      });
      selectedCustomer = recoveryData.customer;
      recoveries = recoveryData.recoveries;
    }
  }

  const recovery = selectedTenant && recoveryId
    ? await getRecoveryDetail({
        shopId: selectedTenant.id,
        recoveryId,
        messagePage,
        messagePageSize: MESSAGE_PAGE_SIZE,
      })
    : null;

  const returnTo = withParamUpdates("/", params, { saved: null });

  return (
    <AdminShell active="tenants" search={search}>
      <div className="flex-1 overflow-auto p-4 sm:p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-[var(--brand-900)]">Tenant Directory</h1>
          <p className="mt-1 text-sm text-gray-500">Manage merchants and investigate abandoned-cart recovery activity.</p>
        </div>

        <section className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-4" aria-label="Platform summary">
          <KpiCard label="Active Tenants" value={directory.kpis.activeTenants.toLocaleString("en-GB")} />
          <KpiCard label="Active Recoveries (Now)" value={directory.kpis.activeRecoveries.toLocaleString("en-GB")} accent />
        </section>

        <TenantTable
          tenants={directory.tenants}
          selectedTenant={selectedTenant}
          tab={tab}
          customers={customers}
          customerSearch={customerSearch}
          selectedCustomer={selectedCustomer}
          recoveries={recoveries}
          params={params}
          returnTo={returnTo}
          saved={saved}
        />
      </div>

      {recovery ? <RecoveryDrawer recovery={recovery} tab={drawerTab} params={params} /> : null}
    </AdminShell>
  );
}
