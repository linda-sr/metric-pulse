'use client';

import { CohortGridRow } from '@/lib/transformCohorts';
import { retentionColor } from '@/lib/heatmapColor';

interface Props {
  data: CohortGridRow[];
  maxMonths?: number;
}

export default function CohortHeatmap({ data, maxMonths = 12 }: Props) {
  const monthColumns = Array.from({ length: maxMonths + 1 }, (_, i) => i);

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Cohort Retention</h2>
      <table className="min-w-full border-separate border-spacing-1">
        <thead>
          <tr>
            <th className="p-2 text-left text-xs font-medium text-gray-500">Cohort</th>
            <th className="p-2 text-left text-xs font-medium text-gray-500">Users</th>
            {monthColumns.map((m) => (
              <th key={m} className="p-2 text-center text-xs font-medium text-gray-500">
                M{m}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.cohort_month}>
              <td className="whitespace-nowrap p-2 text-sm font-medium text-gray-700">
                {row.cohort_month}
              </td>
              <td className="p-2 text-sm text-gray-500">{row.cohort_users}</td>
              {row.retention.map((pct, i) => (
                <td
                  key={i}
                  className="h-10 w-14 rounded text-center text-xs font-medium"
                  style={{
                    backgroundColor: retentionColor(pct),
                    color: pct !== null && pct < 50 ? '#7f1d1d' : '#14532d',
                  }}
                  title={pct !== null ? `${pct}% retained` : 'No data yet'}
                >
                  {pct !== null ? `${pct}%` : '—'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}