interface CohortRow {
  cohort_month: string;
  months_since_signup: number;
  active_users: number;
  cohort_users: number;
  retention_pct: number;
}

export interface CohortGridRow {
  cohort_month: string;
  cohort_users: number;
  retention: (number | null)[]; // index 0-12, null = no data yet
}

export function transformToCohortGrid(rows: CohortRow[], maxMonths = 12): CohortGridRow[] {
  const byMonth = new Map<string, CohortGridRow>();

  for (const row of rows) {
    if (!byMonth.has(row.cohort_month)) {
      byMonth.set(row.cohort_month, {
        cohort_month: row.cohort_month,
        cohort_users: row.cohort_users,
        retention: new Array(maxMonths + 1).fill(null),
      });
    }
    const entry = byMonth.get(row.cohort_month)!;
    if (row.months_since_signup >= 0 && row.months_since_signup <= maxMonths) {
      entry.retention[row.months_since_signup] = row.retention_pct;
    }
  }

  return Array.from(byMonth.values()).sort((a, b) =>
    a.cohort_month.localeCompare(b.cohort_month)
  );
}