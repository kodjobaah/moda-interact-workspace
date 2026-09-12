# ARCH-010 upgrade-economics guardrail — required test matrix

This matrix is binding for `ARCH-010-ADMIN-007` and the integration cases are binding for `ARCH-010-ADMIN-009`.

## A. Source-algorithm preservation

1. `findCheapestTopUpCombination(..., 0)` returns zero cost/no purchases.
2. Empty offer list with positive need returns `null`.
3. One exact fixed pack finds the exact pack.
4. Multiple fixed offers choose a cheaper mixed combination rather than the fewest packs.
5. Overshoot is allowed when overshooting is cheaper than exact fill.
6. Invalid zero/negative pack credits are ignored/rejected safely.
7. Invalid zero/negative charge is ignored/rejected safely.
8. `summarisePurchases` groups identical offer IDs and increments quantity.
9. User-supplied Free→Starter example remains PASS at 20% policy.
10. User-supplied Starter→Growth example remains PASS at 20% policy.
11. User-supplied Growth→Scale example remains FAIL with `UPGRADE_ADVANTAGE_TOO_SMALL`.
12. Stay+top-up exactly equal to upgrade returns `TOPUPS_CHEAPER_THAN_UPGRADE`.
13. Stay+top-up cheaper than upgrade returns `TOPUPS_CHEAPER_THAN_UPGRADE`.
14. Exactly 20.00% premium passes when threshold is 2000 bps.
15. 19.99% (or nearest integer-minor equivalent below threshold) fails.
16. Threshold 0 bps accepts any strictly-more-expensive stay+top-up route.

## B. Fail-closed commercial evidence

17. Top-ups disabled returns PASS `NO_TOPUPS_AVAILABLE` even when no usage-price snapshot exists.
18. Top-ups enabled with no valid offer/pricing returns `UNVERIFIED/TOPUP_PRICING_UNAVAILABLE`.
19. Missing lower recurring price returns `UNVERIFIED/MISSING_PLAN_PRICE`.
20. Missing higher recurring price returns `UNVERIFIED/MISSING_PLAN_PRICE`.
21. Different lower/higher recurring currencies returns `UNVERIFIED/CURRENCY_MISMATCH`.
22. Different usage-meter currency returns `UNVERIFIED/CURRENCY_MISMATCH`.
23. Self-edge or higher plan with no larger monthly allowance returns `UNVERIFIED/INVALID_UPGRADE_EDGE`.
24. Invalid pack size (`null`, 0, negative, non-safe integer) returns `UNVERIFIED/TOPUP_PRICING_UNAVAILABLE`.
25. Malformed tiers return `UNVERIFIED/INVALID_USAGE_PRICING` through the single-pack adapter.
26. Final tier missing `upTo=null` is malformed.
27. Non-increasing finite `upTo` boundaries are malformed.

## C. Free/lifetime/promo separation

28. Free plan is passed to the evaluator with `monthlyIncludedConversations=0` even when `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance=5` (or another value).
29. Changing lifetime-Free grant policy does not change an existing Free→Starter economics result.
30. Promotional campaign quantity/expiry/selection is not an evaluator input and does not change the result.
31. Purchased-credit balance/refund state is not an evaluator input and does not change the result.
32. Merchant-specific usage/current balances are not evaluator inputs.

## D. Shopify usage-pricing mathematics

33. FIXED: `quantity * unitAmountMinor`.
34. FIXED quantity 0 costs 0.
35. GRADUATED one tier produces per-unit cost for units in that tier.
36. GRADUATED 150 units across 1–100 @ 1000 minor and 101+ @ 900 minor costs `100*1000 + 50*900` when flat amounts are zero.
37. GRADUATED applies each participating tier's `flatAmountMinor` exactly once.
38. VOLUME 150 units with 1–100 @ 1000 and 101–200 @ 900 costs `150*900` when flat amount is zero.
39. VOLUME applies only the selected tier's flat amount once.
40. Open-ended final tier prices large valid quantities.
41. `packUnitsNeeded = ceil(additionalCreditsNeeded / recoveryCreditsPerPack)`.
42. A pack that overshoots the next-plan allowance is still priced by whole meter units.

## E. Supplied example economics (regression fixtures)

Use the exact source fixture values as direct evaluator tests:

- Free: recurring 0, source fixture included=2, Starter=20, offers £5→1, £10→3, £20→7 => PASS, stay=£55 vs £35.
- Starter: £35/20, Growth £75/50, offers £5→2, £10→5, £20→10 => PASS, stay=£95 vs £75.
- Growth: £75/50, Scale £149/110, offers £5→3, £10→6, £20→12 => FAIL, stay=£175 vs £149.

Also add the ARCH-010 corrected Free fixture where recurring monthly included is **0**, proving the one-time lifetime-Free allowance is not treated as monthly capacity.

## F. Admin integration and hard gate

43. Only SUPER_ADMIN can record economics snapshots, edit upgrade edges or policy threshold.
44. Snapshot records exact local BillingPlan ID plus Shopify handle/meter-handle evidence; mismatched local current handles are rejected.
45. Plan ladder rejects lower==higher.
46. Plan ladder rejects branching lower edges and branching higher edges.
47. Creating/changing an edge whose higher plan has no larger monthly allowance is rejected or remains UNVERIFIED and cannot activate economics-affecting config.
48. Creating/enabling a top-up pack on a lower plan re-evaluates its lower→higher edge.
49. Changing `recoveryCreditsPerPack` re-evaluates lower→higher.
50. Changing lower plan monthly included allowance re-evaluates lower→higher and any previous→lower edge.
51. Changing higher plan monthly included allowance re-evaluates lower→higher and higher→next as applicable.
52. Toggling top-ups OFF allows mutation with `NO_TOPUPS_AVAILABLE` for that edge.
53. Toggling top-ups ON with no current economics snapshot is blocked `UNVERIFIED`.
54. PASS permits the server mutation and writes audit evidence containing evaluator inputs/result/snapshot IDs.
55. FAIL blocks the server mutation and leaves BillingPlan/features unchanged.
56. UNVERIFIED blocks the server mutation and leaves BillingPlan/features unchanged.
57. Client-side disabled button is not the security boundary: crafted action POST with FAIL is still blocked server-side.
58. Currency mismatch blocks activation server-side.
59. A plan with no configured next upgrade edge does not invent a next plan; document/display `NO_UPGRADE_EDGE` and do not run the guardrail for a nonexistent edge.
60. Updating Scale (top plan) does not invent a higher tier.
61. Changing an economics snapshot alone does not mutate merchant subscriptions or issue Shopify billing actions.
62. Guardrail never calls `appSubscriptionCreate`, `appPurchaseOneTimeCreate`, App Events, or merchant billing mutations.
63. Guardrail audit does not contain secrets/tokens/raw Partner credentials.
64. Existing merchant billing and promotional-credit flows are unchanged.

## G. UI explanation

65. PASS shows lower plan, higher plan, capacity gap, required pack units/top-up path, stay+top-up cost, upgrade cost, actual premium and required premium.
66. FAIL shows the same calculation and clearly says activation is blocked.
67. UNVERIFIED says what commercial evidence is missing/incompatible; never displays PASS.
68. Currency values are formatted for display only after integer-minor arithmetic is complete.
69. UI does not claim local snapshot data is Shopify charging authority; it labels it verified Shopify economics evidence used for the Admin guardrail.
