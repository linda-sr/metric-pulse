interface DbtHealth {
  generated_at: string | null;
  total_tests: number;
  passed: number;
  failed: number;
  failing_tests: { unique_id: string; status: string; message: string | null }[];
}

export default function PipelineHealthCard({ dbtHealth }: { dbtHealth: DbtHealth }) {
  const allPassing = dbtHealth.failed === 0;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">dbt Test Results</h2>
        <span
          className={`rounded-full px-3 py-1 text-xs font-medium ${
            allPassing ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}
        >
          {allPassing ? 'All Passing' : `${dbtHealth.failed} Failing`}
        </span>
      </div>

      <p className="mt-2 text-sm text-gray-500">
        {dbtHealth.passed} / {dbtHealth.total_tests} tests passed
        {dbtHealth.generated_at && ` — last run ${new Date(dbtHealth.generated_at).toLocaleString()}`}
      </p>

      {!allPassing && (
        <ul className="mt-4 space-y-2">
          {dbtHealth.failing_tests.map((t) => (
            <li key={t.unique_id} className="rounded bg-red-50 p-3 text-sm text-red-700">
              <p className="font-medium">{t.unique_id}</p>
              {t.message && <p className="mt-1 text-xs">{t.message}</p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}