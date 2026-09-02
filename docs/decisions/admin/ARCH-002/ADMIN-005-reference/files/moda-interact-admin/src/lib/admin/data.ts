import {
  CheckoutRecoveryStatus,
  Prisma,
  type ConversationMessage,
} from "@prisma/client";
import { requirePlatformAdminRead } from "@/lib/auth/platform-admin";
import { prisma } from "@/lib/prisma";
import type {
  CustomerListItem,
  PageResult,
  PlatformKpis,
  RecoveryDetail,
  RecoveryLineItem,
  RecoveryListItem,
  RecoveryMessage,
  TenantDetail,
  TenantListItem,
} from "./types";
import { customerName } from "./format";

const ACTIVE_RECOVERY_STATUSES: CheckoutRecoveryStatus[] = [
  CheckoutRecoveryStatus.DETECTED,
  CheckoutRecoveryStatus.MESSAGE_SENT,
  CheckoutRecoveryStatus.ENGAGED,
];

function pageResult<T>(
  items: T[],
  page: number,
  pageSize: number,
  totalItems: number,
): PageResult<T> {
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  return { items, page, pageSize, totalItems, totalPages };
}

function decimalToString(value: Prisma.Decimal | null): string | null {
  return value?.toString() ?? null;
}

function asJsonObject(value: Prisma.JsonValue | undefined): Record<string, Prisma.JsonValue> | null {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, Prisma.JsonValue>)
    : null;
}

function jsonString(value: Prisma.JsonValue | undefined): string | null {
  if (typeof value === "string") return value;
  if (typeof value === "number") return String(value);
  return null;
}

function safeHttpUrl(value: string | null): string | null {
  if (!value) return null;
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:" ? url.toString() : null;
  } catch {
    return null;
  }
}

function normalizeLineItems(value: Prisma.JsonValue | null, currency: string | null): RecoveryLineItem[] {
  let rawItems: Prisma.JsonValue[] = [];

  if (Array.isArray(value)) {
    rawItems = value;
  } else {
    const root = asJsonObject(value ?? undefined);
    if (root && Array.isArray(root.nodes)) {
      rawItems = root.nodes;
    } else if (root && Array.isArray(root.edges)) {
      rawItems = root.edges.flatMap((edge) => {
        const edgeObject = asJsonObject(edge);
        return edgeObject?.node ? [edgeObject.node] : [];
      });
    }
  }

  return rawItems.flatMap((item, index) => {
    const row = asJsonObject(item);
    if (!row) return [];

    const variantObject = asJsonObject(row.variant);
    const imageObject = asJsonObject(row.image);
    const priceObject = asJsonObject(row.price);
    const moneyObject = asJsonObject(row.originalUnitPriceSet) ?? asJsonObject(row.discountedUnitPriceSet);
    const shopMoney = moneyObject ? asJsonObject(moneyObject.shopMoney) : null;

    const title = jsonString(row.title ?? row.name ?? row.product_title ?? row.productTitle) ?? `Cart item ${index + 1}`;
    const variant = jsonString(row.variant_title ?? row.variantTitle) ?? jsonString(variantObject?.title);
    const quantityRaw = row.quantity;
    const quantity = typeof quantityRaw === "number" ? quantityRaw : Number(jsonString(quantityRaw) ?? 1) || 1;
    const price = jsonString(row.price ?? row.line_price ?? row.linePrice)
      ?? jsonString(priceObject?.amount)
      ?? jsonString(shopMoney?.amount);
    const imageUrl = safeHttpUrl(
      jsonString(row.imageUrl ?? row.image_url)
      ?? jsonString(imageObject?.url)
      ?? jsonString(variantObject?.image),
    );

    return [{ title, variant, quantity, price, currency, imageUrl }];
  });
}

function mapMessage(message: ConversationMessage): RecoveryMessage {
  return {
    id: message.id,
    direction: message.direction,
    senderType: message.senderType,
    status: message.status,
    content: message.content,
    createdAt: message.createdAt,
    sentAt: message.sentAt,
    deliveredAt: message.deliveredAt,
    readAt: message.readAt,
  };
}

export async function getTenantDirectory(input: {
  page: number;
  pageSize: number;
  search: string;
}): Promise<{ tenants: PageResult<TenantListItem>; kpis: PlatformKpis }> {
  await requirePlatformAdminRead();
  const { page, pageSize, search } = input;
  const where: Prisma.ShopWhereInput = search
    ? {
        OR: [
          { domain: { contains: search, mode: "insensitive" } },
          { brand: { is: { brandName: { contains: search, mode: "insensitive" } } } },
        ],
      }
    : {};

  const [totalItems, activeTenants, activeRecoveries] = await Promise.all([
    prisma.shop.count({ where }),
    prisma.shop.count({ where: { status: "ACTIVE" } }),
    prisma.checkoutRecovery.count({
      where: {
        status: { in: ACTIVE_RECOVERY_STATUSES },
        shop: { status: "ACTIVE" },
      },
    }),
  ]);
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const safePage = Math.min(page, totalPages);
  const rows = await prisma.shop.findMany({
    where,
    orderBy: [{ updatedAt: "desc" }, { domain: "asc" }],
    skip: (safePage - 1) * pageSize,
    take: pageSize,
    select: {
      id: true,
      domain: true,
      status: true,
      installedAt: true,
      brand: { select: { brandName: true, squareLogoUrl: true, logoUrl: true } },
      subscriptions: {
        orderBy: { updatedAt: "desc" },
        take: 1,
        select: { planHandle: true, plan: { select: { name: true } } },
      },
    },
  });

  const tenants: TenantListItem[] = rows.map((row) => {
    const subscription = row.subscriptions[0];
    return {
      id: row.id,
      domain: row.domain,
      status: row.status,
      installedAt: row.installedAt,
      brandName: row.brand?.brandName ?? null,
      logoUrl: row.brand?.squareLogoUrl ?? row.brand?.logoUrl ?? null,
      planName: subscription?.plan?.name ?? null,
      planHandle: subscription?.planHandle ?? null,
    };
  });

  return {
    tenants: pageResult(tenants, safePage, pageSize, totalItems),
    kpis: { activeTenants, activeRecoveries },
  };
}

export async function getTenantDetail(shopId: string): Promise<TenantDetail | null> {
  await requirePlatformAdminRead();
  const row = await prisma.shop.findUnique({
    where: { id: shopId },
    select: {
      id: true,
      domain: true,
      status: true,
      installedAt: true,
      uninstalledAt: true,
      brand: { select: { brandName: true, squareLogoUrl: true, logoUrl: true } },
      settings: {
        select: { onboardingCompleted: true, recoveryDelayMinutes: true },
      },
      subscriptions: {
        orderBy: { updatedAt: "desc" },
        take: 1,
        select: {
          planHandle: true,
          status: true,
          currentPeriodStart: true,
          currentPeriodEnd: true,
          plan: { select: { name: true } },
        },
      },
    },
  });

  if (!row) return null;
  const subscription = row.subscriptions[0];

  return {
    id: row.id,
    domain: row.domain,
    status: row.status,
    installedAt: row.installedAt,
    uninstalledAt: row.uninstalledAt,
    brandName: row.brand?.brandName ?? null,
    logoUrl: row.brand?.squareLogoUrl ?? row.brand?.logoUrl ?? null,
    planName: subscription?.plan?.name ?? null,
    planHandle: subscription?.planHandle ?? null,
    recoveryDelayMinutes: row.settings?.recoveryDelayMinutes ?? null,
    onboardingCompleted: row.settings?.onboardingCompleted ?? false,
    subscriptionStatus: subscription?.status ?? null,
    currentPeriodStart: subscription?.currentPeriodStart ?? null,
    currentPeriodEnd: subscription?.currentPeriodEnd ?? null,
  };
}

export async function getTenantCustomers(input: {
  shopId: string;
  page: number;
  pageSize: number;
  search: string;
}): Promise<PageResult<CustomerListItem>> {
  await requirePlatformAdminRead();
  const { shopId, page, pageSize, search } = input;
  const terms = search.split(/\s+/).filter(Boolean);
  const where: Prisma.CustomerWhereInput = {
    shopId,
    ...(terms.length
      ? {
          AND: terms.map((term) => ({
            OR: [
              { firstName: { contains: term, mode: "insensitive" } },
              { lastName: { contains: term, mode: "insensitive" } },
              { email: { contains: term, mode: "insensitive" } },
              { phone: { contains: term, mode: "insensitive" } },
              { phones: { some: { phone: { contains: term, mode: "insensitive" } } } },
            ],
          })),
        }
      : {}),
  };

  const totalItems = await prisma.customer.count({ where });
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const safePage = Math.min(page, totalPages);
  const rows = await prisma.customer.findMany({
    where,
    orderBy: { updatedAt: "desc" },
    skip: (safePage - 1) * pageSize,
    take: pageSize,
    select: {
      id: true,
      firstName: true,
      lastName: true,
      email: true,
      phone: true,
      phones: {
        where: { endedAt: null },
        orderBy: { startedAt: "desc" },
        take: 1,
        select: { phone: true },
      },
      _count: { select: { recoveries: true } },
    },
  });

  const items = rows.map((row) => ({
    id: row.id,
    firstName: row.firstName,
    lastName: row.lastName,
    email: row.email,
    phone: row.phone ?? row.phones[0]?.phone ?? null,
    recoveryCount: row._count.recoveries,
  }));

  return pageResult(items, safePage, pageSize, totalItems);
}

export async function getCustomerRecoveries(input: {
  shopId: string;
  customerId: string;
  page: number;
  pageSize: number;
}): Promise<{ customer: CustomerListItem | null; recoveries: PageResult<RecoveryListItem> }> {
  await requirePlatformAdminRead();
  const { shopId, customerId, page, pageSize } = input;

  const customer = await prisma.customer.findFirst({
    where: { id: customerId, shopId },
    select: {
      id: true,
      firstName: true,
      lastName: true,
      email: true,
      phone: true,
      phones: {
        where: { endedAt: null },
        orderBy: { startedAt: "desc" },
        take: 1,
        select: { phone: true },
      },
      _count: { select: { recoveries: true } },
    },
  });

  if (!customer) {
    return { customer: null, recoveries: pageResult([], page, pageSize, 0) };
  }

  const where: Prisma.CheckoutRecoveryWhereInput = { shopId, customerId };
  const totalItems = await prisma.checkoutRecovery.count({ where });
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const safePage = Math.min(page, totalPages);
  const rows = await prisma.checkoutRecovery.findMany({
    where,
    orderBy: { detectedAt: "desc" },
    skip: (safePage - 1) * pageSize,
    take: pageSize,
    select: {
      id: true,
      detectedAt: true,
      totalPrice: true,
      currency: true,
      status: true,
      conversation: { select: { outcome: true } },
    },
  });

  return {
    customer: {
      id: customer.id,
      firstName: customer.firstName,
      lastName: customer.lastName,
      email: customer.email,
      phone: customer.phone ?? customer.phones[0]?.phone ?? null,
      recoveryCount: customer._count.recoveries,
    },
    recoveries: pageResult(
      rows.map((row) => ({
        id: row.id,
        detectedAt: row.detectedAt,
        totalPrice: decimalToString(row.totalPrice),
        currency: row.currency,
        status: row.status,
        outcome: row.conversation?.outcome ?? null,
      })),
      safePage,
      pageSize,
      totalItems,
    ),
  };
}

export async function getRecoveryDetail(input: {
  shopId: string;
  recoveryId: string;
  messagePage: number;
  messagePageSize: number;
}): Promise<RecoveryDetail | null> {
  await requirePlatformAdminRead();
  const { shopId, recoveryId, messagePage, messagePageSize } = input;
  const recovery = await prisma.checkoutRecovery.findFirst({
    where: { id: recoveryId, shopId },
    select: {
      id: true,
      shopId: true,
      checkoutToken: true,
      checkoutUrl: true,
      detectedAt: true,
      totalPrice: true,
      currency: true,
      status: true,
      lineItems: true,
      customer: {
        select: {
          id: true,
          firstName: true,
          lastName: true,
          email: true,
          phone: true,
          phones: {
            where: { endedAt: null },
            orderBy: { startedAt: "desc" },
            take: 1,
            select: { phone: true },
          },
        },
      },
      conversation: {
        select: { id: true, outcome: true },
      },
      statusHistory: {
        orderBy: { occurredAt: "asc" },
        select: {
          id: true,
          fromStatus: true,
          toStatus: true,
          reason: true,
          source: true,
          occurredAt: true,
        },
      },
    },
  });

  if (!recovery) return null;

  const conversationId = recovery.conversation?.id ?? null;
  let messages = pageResult<RecoveryMessage>([], messagePage, messagePageSize, 0);

  if (conversationId) {
    const messageCount = await prisma.conversationMessage.count({ where: { conversationId } });
    const messageTotalPages = Math.max(1, Math.ceil(messageCount / messagePageSize));
    const safeMessagePage = Math.min(messagePage, messageTotalPages);
    const messageRows = await prisma.conversationMessage.findMany({
      where: { conversationId },
      orderBy: { createdAt: "asc" },
      skip: (safeMessagePage - 1) * messagePageSize,
      take: messagePageSize,
    });
    messages = pageResult(messageRows.map(mapMessage), safeMessagePage, messagePageSize, messageCount);
  }

  const currentPhone = recovery.customer?.phone ?? recovery.customer?.phones[0]?.phone ?? null;

  return {
    id: recovery.id,
    shopId: recovery.shopId,
    checkoutToken: recovery.checkoutToken,
    checkoutUrl: safeHttpUrl(recovery.checkoutUrl),
    detectedAt: recovery.detectedAt,
    totalPrice: decimalToString(recovery.totalPrice),
    currency: recovery.currency,
    status: recovery.status,
    outcome: recovery.conversation?.outcome ?? null,
    conversationId,
    customer: recovery.customer
      ? {
          id: recovery.customer.id,
          name: customerName(
            recovery.customer.firstName,
            recovery.customer.lastName,
            recovery.customer.email,
          ),
          email: recovery.customer.email,
          phone: currentPhone,
        }
      : null,
    messages,
    lifecycle: recovery.statusHistory.map((event) => ({
      id: event.id,
      fromStatus: event.fromStatus,
      toStatus: event.toStatus,
      reason: event.reason,
      source: event.source,
      occurredAt: event.occurredAt,
    })),
    lineItems: normalizeLineItems(recovery.lineItems, recovery.currency),
  };
}
