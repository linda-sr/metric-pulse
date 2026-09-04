interface RowCount {
  table: string;
  count: number;
}

export default function RowCountsTable({ rowCounts }: { rowCounts: RowCount[] }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Row Counts by Table</h2>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-left text-xs font-medium text-gray-500">
            <th className="pb-2">Table</th>
            <th className="pb-2 text-right">Rows</th>
          </tr>
        </thead>
        <tbody>
          {rowCounts.map((rc) => (
            <tr key={rc.table} className="border-b border-gray-100 last:border-0">
              <td className="py-2 font-mono text-gray-700">{rc.table}</td>
              <td className="py-2 text-right text-gray-900">{rc.count.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-3 text-xs text-gray-400">
        {/* Snapshot as of page load. Historical trend tracking will be added once the Day 24 scheduled pipeline begins logging row-count snapshots over time. */}
      </p>
    </div>
  );
}