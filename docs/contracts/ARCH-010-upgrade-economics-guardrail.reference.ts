/**
 * ARCH-010 Upgrade Economics Guardrail — binding implementation reference.
 *
 * Source basis: user-supplied moda-upgrade-economics-guardrail/upgrade-economics-guardrail.js.
 * Preserved source behaviour:
 * - cheapest fixed-offer combination search;
 * - lower-plan monthly price + cheapest required top-ups;
 * - PASS only when stay+top-up is at least the configured premium above upgrade;
 * - FAIL when stay+top-up is as cheap/cheaper than upgrade or premium is insufficient.
 *
 * ARCH-010 integration additions:
 * - UNVERIFIED fail-closed state for missing/incomparable commercial evidence;
 * - basis-point threshold rather than floating percentage policy storage;
 * - current Moda single-pack Shopify usage-meter adapter;
 * - FIXED / GRADUATED / VOLUME usage-pricing cost helpers;
 * - Free monthly included allowance is supplied as 0 by the integration layer;
 * - promotional, purchased and lifetime-Free balances are never evaluator inputs.
 */

export type UpgradeEconomicsStatus = "PASS" | "FAIL" | "UNVERIFIED";

export type UpgradeEconomicsCode =
  | "UPGRADE_ECONOMICS_OK"
  | "NO_TOPUPS_AVAILABLE"
  | "TOPUPS_CHEAPER_THAN_UPGRADE"
  | "UPGRADE_ADVANTAGE_TOO_SMALL"
  | "MISSING_PLAN_PRICE"
  | "CURRENCY_MISMATCH"
  | "TOPUP_PRICING_UNAVAILABLE"
  | "INVALID_UPGRADE_EDGE"
  | "INVALID_TOPUP_CONFIGURATION"
  | "INVALID_USAGE_PRICING";

export interface FixedTopUpOffer {
  id: string;
  planId: string;
  chargeAmountMinor: number;
  creditsGranted: number;
}

export interface PlanEconomics {
  id: string;
  name: string;
  monthlyPriceMinor: number | null;
  monthlyIncludedConversations: number;
  currency: string | null;
}

export interface PurchaseSummary {
  offerId: string;
  chargeAmountMinor: number;
  creditsGranted: number;
  quantity: number;
}

export interface GuardrailDetails {
  additionalCreditsNeeded: number;
  topUpCostMinor?: number;
  stayAndTopUpCostMinor?: number;
  upgradeCostMinor?: number;
  requiredMinimumMinor?: number;
  premiumBps?: number;
  packUnitsNeeded?: number;
  packSummary?: PurchaseSummary[];
}

export interface UpgradeEconomicsResult {
  status: UpgradeEconomicsStatus;
  code: UpgradeEconomicsCode;
  message: string;
  details: GuardrailDetails;
}

export type UsagePricingSnapshot =
  | {
      mode: "FIXED";
      currency: string;
      unitAmountMinor: number;
    }
  | {
      mode: "GRADUATED" | "VOLUME";
      currency: string;
      tiers: Array<{
        upTo: number | null;
        amountPerUnitMinor: number;
        flatAmountMinor: number;
      }>;
    };

function isNonNegativeSafeInteger(value: number): boolean {
  return Number.isSafeInteger(value) && value >= 0;
}

function isPositiveSafeInteger(value: number): boolean {
  return Number.isSafeInteger(value) && value > 0;
}

function normalizeCurrency(value: string | null): string | null {
  const trimmed = value?.trim().toUpperCase() ?? "";
  return /^[A-Z]{3}$/.test(trimmed) ? trimmed : null;
}

export function findCheapestTopUpCombination(
  offers: FixedTopUpOffer[],
  creditsNeeded: number,
): { costMinor: number; creditsGranted: number; purchases: FixedTopUpOffer[] } | null {
  if (creditsNeeded <= 0) {
    return { costMinor: 0, creditsGranted: 0, purchases: [] };
  }

  const validOffers = offers.filter(
    (offer) =>
      isPositiveSafeInteger(offer.creditsGranted) &&
      isPositiveSafeInteger(offer.chargeAmountMinor),
  );

  if (!validOffers.length) return null;
  if (!isPositiveSafeInteger(creditsNeeded)) return null;

  const maxCreditsPerPack = Math.max(
    ...validOffers.map((offer) => offer.creditsGranted),
  );
  const maxCredits = creditsNeeded + maxCreditsPerPack;

  // Defensive bound: this is an Admin commercial validator, not an unbounded knapsack service.
  if (maxCredits > 1_000_000) return null;

  const dp: Array<{ costMinor: number; purchases: FixedTopUpOffer[] } | null> =
    Array(maxCredits + 1).fill(null);
  dp[0] = { costMinor: 0, purchases: [] };

  for (let credits = 0; credits <= maxCredits; credits += 1) {
    const current = dp[credits];
    if (!current) continue;

    for (const offer of validOffers) {
      const nextCredits = Math.min(
        maxCredits,
        credits + offer.creditsGranted,
      );
      const nextCost = current.costMinor + offer.chargeAmountMinor;
      const existing = dp[nextCredits];

      if (!existing || nextCost < existing.costMinor) {
        dp[nextCredits] = {
          costMinor: nextCost,
          purchases: [...current.purchases, offer],
        };
      }
    }
  }

  let best: {
    costMinor: number;
    creditsGranted: number;
    purchases: FixedTopUpOffer[];
  } | null = null;

  for (let credits = creditsNeeded; credits <= maxCredits; credits += 1) {
    const candidate = dp[credits];
    if (candidate && (!best || candidate.costMinor < best.costMinor)) {
      best = {
        costMinor: candidate.costMinor,
        creditsGranted: credits,
        purchases: candidate.purchases,
      };
    }
  }

  return best;
}

export function summarisePurchases(
  purchases: FixedTopUpOffer[],
): PurchaseSummary[] {
  const counts = new Map<string, PurchaseSummary>();

  for (const offer of purchases) {
    const existing = counts.get(offer.id);
    if (existing) {
      existing.quantity += 1;
    } else {
      counts.set(offer.id, {
        offerId: offer.id,
        chargeAmountMinor: offer.chargeAmountMinor,
        creditsGranted: offer.creditsGranted,
        quantity: 1,
      });
    }
  }

  return [...counts.values()];
}

function unverified(
  code: UpgradeEconomicsCode,
  message: string,
  additionalCreditsNeeded: number,
): UpgradeEconomicsResult {
  return {
    status: "UNVERIFIED",
    code,
    message,
    details: { additionalCreditsNeeded, packSummary: [] },
  };
}

export function evaluateUpgradeEconomicsCost({
  currentPlan,
  nextPlan,
  topUpCostMinor,
  additionalCreditsNeeded,
  minimumUpgradePremiumBps = 2000,
}: {
  currentPlan: PlanEconomics;
  nextPlan: PlanEconomics;
  topUpCostMinor: number;
  additionalCreditsNeeded: number;
  minimumUpgradePremiumBps?: number;
}): UpgradeEconomicsResult {
  const currentCurrency = normalizeCurrency(currentPlan.currency);
  const nextCurrency = normalizeCurrency(nextPlan.currency);

  if (
    !isNonNegativeSafeInteger(currentPlan.monthlyPriceMinor ?? -1) ||
    !isPositiveSafeInteger(nextPlan.monthlyPriceMinor ?? 0)
  ) {
    return unverified(
      "MISSING_PLAN_PRICE",
      "Upgrade economics cannot be verified because recurring plan pricing evidence is missing or invalid.",
      additionalCreditsNeeded,
    );
  }

  if (!currentCurrency || !nextCurrency || currentCurrency !== nextCurrency) {
    return unverified(
      "CURRENCY_MISMATCH",
      "Upgrade economics cannot be compared across missing or different currencies.",
      additionalCreditsNeeded,
    );
  }

  if (
    !isPositiveSafeInteger(additionalCreditsNeeded) ||
    nextPlan.monthlyIncludedConversations <=
      currentPlan.monthlyIncludedConversations ||
    nextPlan.id === currentPlan.id
  ) {
    return unverified(
      "INVALID_UPGRADE_EDGE",
      "Upgrade economics requires a higher plan with a strictly larger monthly included recovery allowance.",
      additionalCreditsNeeded,
    );
  }

  if (
    !isNonNegativeSafeInteger(topUpCostMinor) ||
    !isNonNegativeSafeInteger(minimumUpgradePremiumBps)
  ) {
    return unverified(
      "INVALID_TOPUP_CONFIGURATION",
      "Upgrade economics cannot be verified because top-up cost or policy threshold is invalid.",
      additionalCreditsNeeded,
    );
  }

  const currentPrice = currentPlan.monthlyPriceMinor as number;
  const upgradeCostMinor = nextPlan.monthlyPriceMinor as number;
  const stayAndTopUpCostMinor = currentPrice + topUpCostMinor;
  const requiredMinimumMinor = Math.ceil(
    (upgradeCostMinor * (10_000 + minimumUpgradePremiumBps)) / 10_000,
  );
  const premiumBps = Math.round(
    ((stayAndTopUpCostMinor - upgradeCostMinor) * 10_000) /
      upgradeCostMinor,
  );

  const format = (minor: number) => `${nextCurrency} ${(minor / 100).toFixed(2)}`;

  const details: GuardrailDetails = {
    additionalCreditsNeeded,
    topUpCostMinor,
    stayAndTopUpCostMinor,
    upgradeCostMinor,
    requiredMinimumMinor,
    premiumBps,
  };

  if (stayAndTopUpCostMinor <= upgradeCostMinor) {
    return {
      status: "FAIL",
      code: "TOPUPS_CHEAPER_THAN_UPGRADE",
      message:
        `BLOCKED: Staying on ${currentPlan.name} and adding top-ups costs ` +
        `${format(stayAndTopUpCostMinor)}, while ${nextPlan.name} costs ` +
        `${format(upgradeCostMinor)}. Staying would be as cheap as or cheaper than upgrading.`,
      details,
    };
  }

  if (stayAndTopUpCostMinor < requiredMinimumMinor) {
    return {
      status: "FAIL",
      code: "UPGRADE_ADVANTAGE_TOO_SMALL",
      message:
        `BLOCKED: Staying on ${currentPlan.name} and adding top-ups costs ` +
        `${format(stayAndTopUpCostMinor)} versus ${format(upgradeCostMinor)} ` +
        `for ${nextPlan.name}. The premium is ${(premiumBps / 100).toFixed(1)}%; ` +
        `policy requires at least ${(minimumUpgradePremiumBps / 100).toFixed(1)}%.`,
      details,
    };
  }

  return {
    status: "PASS",
    code: "UPGRADE_ECONOMICS_OK",
    message:
      `PASS: Staying on ${currentPlan.name} and adding the cheapest required ` +
      `top-ups costs ${format(stayAndTopUpCostMinor)} versus ` +
      `${format(upgradeCostMinor)} for ${nextPlan.name}. The stay-and-top-up ` +
      `route is ${(premiumBps / 100).toFixed(1)}% more expensive.`,
    details,
  };
}

/**
 * Preserves the user-supplied multi-offer algorithm. Use this if/when Moda has
 * multiple fixed-price packs for one plan. Current ARCH-010 integration uses
 * validateSinglePackShopifyEconomics because BillingPlan has one pack size/meter.
 */
export function validateUpgradeEconomics({
  currentPlan,
  nextPlan,
  allTopUpOffers,
  topUpsEnabled,
  minimumUpgradePremiumBps = 2000,
}: {
  currentPlan: PlanEconomics;
  nextPlan: PlanEconomics;
  allTopUpOffers: FixedTopUpOffer[];
  topUpsEnabled: boolean;
  minimumUpgradePremiumBps?: number;
}): UpgradeEconomicsResult {
  const additionalCreditsNeeded =
    nextPlan.monthlyIncludedConversations -
    currentPlan.monthlyIncludedConversations;

  if (!topUpsEnabled) {
    return {
      status: "PASS",
      code: "NO_TOPUPS_AVAILABLE",
      message:
        `${currentPlan.name} has no top-up path capable of replacing ` +
        `${nextPlan.name}, so the upgrade is not being undermined.`,
      details: { additionalCreditsNeeded, packSummary: [] },
    };
  }

  if (additionalCreditsNeeded <= 0) {
    return unverified(
      "INVALID_UPGRADE_EDGE",
      "Upgrade economics requires the higher plan to have more monthly included recoveries.",
      additionalCreditsNeeded,
    );
  }

  const currentPlanOffers = allTopUpOffers.filter(
    (offer) => offer.planId === currentPlan.id,
  );
  const cheapestTopUps = findCheapestTopUpCombination(
    currentPlanOffers,
    additionalCreditsNeeded,
  );

  if (!cheapestTopUps) {
    return unverified(
      "TOPUP_PRICING_UNAVAILABLE",
      "Top-ups are enabled but no complete positive pricing path is available for validation.",
      additionalCreditsNeeded,
    );
  }

  const result = evaluateUpgradeEconomicsCost({
    currentPlan,
    nextPlan,
    topUpCostMinor: cheapestTopUps.costMinor,
    additionalCreditsNeeded,
    minimumUpgradePremiumBps,
  });

  return {
    ...result,
    details: {
      ...result.details,
      packSummary: summarisePurchases(cheapestTopUps.purchases),
    },
  };
}

function validateTierSequence(
  tiers: Array<{
    upTo: number | null;
    amountPerUnitMinor: number;
    flatAmountMinor: number;
  }>,
): boolean {
  if (!tiers.length) return false;
  let previous = 0;
  for (let i = 0; i < tiers.length; i += 1) {
    const tier = tiers[i];
    if (
      !isNonNegativeSafeInteger(tier.amountPerUnitMinor) ||
      !isNonNegativeSafeInteger(tier.flatAmountMinor)
    ) return false;
    if (tier.upTo === null) return i === tiers.length - 1;
    if (!isPositiveSafeInteger(tier.upTo) || tier.upTo <= previous) return false;
    previous = tier.upTo;
  }
  return false; // final tier must be open-ended
}

/**
 * Cost of N Shopify App Event meter units from zero structural catalogue usage.
 * GRADUATED: units are charged through every tier they pass through.
 * VOLUME: all units use the tier containing the final quantity.
 * A tier flatAmountMinor is applied once when that tier participates.
 */
export function calculateUsagePricingCostMinor(
  pricing: UsagePricingSnapshot,
  quantity: number,
): number | null {
  if (!isNonNegativeSafeInteger(quantity)) return null;
  if (quantity === 0) return 0;

  if (pricing.mode === "FIXED") {
    if (!isNonNegativeSafeInteger(pricing.unitAmountMinor)) return null;
    return pricing.unitAmountMinor * quantity;
  }

  if (!validateTierSequence(pricing.tiers)) return null;

  if (pricing.mode === "VOLUME") {
    const tier = pricing.tiers.find(
      (candidate) => candidate.upTo === null || quantity <= candidate.upTo,
    );
    if (!tier) return null;
    return tier.flatAmountMinor + tier.amountPerUnitMinor * quantity;
  }

  let cost = 0;
  let previousUpper = 0;
  let remaining = quantity;

  for (const tier of pricing.tiers) {
    if (remaining <= 0) break;
    const tierCapacity =
      tier.upTo === null ? remaining : tier.upTo - previousUpper;
    const unitsInTier = Math.min(remaining, tierCapacity);
    if (unitsInTier > 0) {
      cost += tier.flatAmountMinor + tier.amountPerUnitMinor * unitsInTier;
      remaining -= unitsInTier;
    }
    if (tier.upTo !== null) previousUpper = tier.upTo;
  }

  return remaining === 0 ? cost : null;
}

export function validateSinglePackShopifyEconomics({
  currentPlan,
  nextPlan,
  topUpsEnabled,
  recoveryCreditsPerPack,
  usagePricing,
  minimumUpgradePremiumBps = 2000,
}: {
  currentPlan: PlanEconomics;
  nextPlan: PlanEconomics;
  topUpsEnabled: boolean;
  recoveryCreditsPerPack: number | null;
  usagePricing: UsagePricingSnapshot | null;
  minimumUpgradePremiumBps?: number;
}): UpgradeEconomicsResult {
  const additionalCreditsNeeded =
    nextPlan.monthlyIncludedConversations -
    currentPlan.monthlyIncludedConversations;

  if (!topUpsEnabled) {
    return {
      status: "PASS",
      code: "NO_TOPUPS_AVAILABLE",
      message:
        `${currentPlan.name} has no top-up path capable of replacing ` +
        `${nextPlan.name}, so the upgrade is not being undermined.`,
      details: { additionalCreditsNeeded, packSummary: [] },
    };
  }

  if (additionalCreditsNeeded <= 0) {
    return unverified(
      "INVALID_UPGRADE_EDGE",
      "Upgrade economics requires the higher plan to have more monthly included recoveries.",
      additionalCreditsNeeded,
    );
  }

  if (!isPositiveSafeInteger(recoveryCreditsPerPack ?? 0) || !usagePricing) {
    return unverified(
      "TOPUP_PRICING_UNAVAILABLE",
      "Top-ups are enabled but pack size or Shopify usage pricing evidence is unavailable.",
      additionalCreditsNeeded,
    );
  }

  const currentCurrency = normalizeCurrency(currentPlan.currency);
  const nextCurrency = normalizeCurrency(nextPlan.currency);
  const usageCurrency = normalizeCurrency(usagePricing.currency);
  if (
    !currentCurrency ||
    !nextCurrency ||
    !usageCurrency ||
    currentCurrency !== nextCurrency ||
    currentCurrency !== usageCurrency
  ) {
    return unverified(
      "CURRENCY_MISMATCH",
      "Recurring and top-up pricing must use the same currency before upgrade economics can be verified.",
      additionalCreditsNeeded,
    );
  }

  const packUnitsNeeded = Math.ceil(
    additionalCreditsNeeded / (recoveryCreditsPerPack as number),
  );
  const topUpCostMinor = calculateUsagePricingCostMinor(
    usagePricing,
    packUnitsNeeded,
  );

  if (topUpCostMinor === null) {
    return unverified(
      "INVALID_USAGE_PRICING",
      "Shopify usage pricing evidence is malformed or cannot price the required pack quantity.",
      additionalCreditsNeeded,
    );
  }

  const result = evaluateUpgradeEconomicsCost({
    currentPlan,
    nextPlan,
    topUpCostMinor,
    additionalCreditsNeeded,
    minimumUpgradePremiumBps,
  });

  return {
    ...result,
    details: {
      ...result.details,
      packUnitsNeeded,
    },
  };
}
