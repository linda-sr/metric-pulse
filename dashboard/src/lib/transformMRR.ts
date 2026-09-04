interface MRRRow {
  mrr_month: string;
  movement_type: string;
  total_delta: number;
}

export interface WaterfallRow {
  mrr_month: string;
  new: number;
  expansion: number;
  contraction: number;
  churn: number;
  resurrection: number;
  base: number;
  net: number;
}

export function transformToWaterfall(rows: MRRRow[]): WaterfallRow[] {
  // Group raw rows by month into a lookup, defaulting every movement type to 0.
  const byMonth = new Map<string, WaterfallRow>();

  for (const row of rows) {
    if (!byMonth.has(row.mrr_month)) {
      byMonth.set(row.mrr_month, {
        mrr_month: row.mrr_month,
        new: 0,
        expansion: 0,
        contraction: 0,
        churn: 0,
        resurrection: 0,
        base: 0,
        net: 0,
      });
    }
    const entry = byMonth.get(row.mrr_month)!;
    (entry as any)[row.movement_type] = row.total_delta;
  }

  // Sort chronologically — the API already orders by mrr_month, but
  // Map insertion order should match anyway; sorting explicitly is a
  // cheap guarantee rather than an assumption.
  const sorted = Array.from(byMonth.values()).sort((a, b) =>
    a.mrr_month.localeCompare(b.mrr_month)
  );

  // Running cumulative total, used to position each bar's invisible "base" spacer.
  let cumulative = 0;

  for (const row of sorted) {
    const positives = row.new + row.expansion + row.resurrection;
    const negatives = row.contraction + row.churn; // already negative values from the API

    const monthNet = positives + negatives;

    // The bar's floor is the cumulative total BEFORE this month's positive
    // movements are added — negatives are drawn hanging down from a base
    // ABOVE their own magnitude, positives drawn up from the base below them.
    // Simplification for a monthly waterfall (rather than a true single-bar-
    // per-event waterfall): treat each month's net effect as one step.
    row.base = cumulative;
    row.net = monthNet;
    cumulative += monthNet;
  }

  return sorted;
}