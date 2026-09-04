import KPICard from '@/components/KPICard';
import MRRWaterfallSection from '@/components/MRRWaterfallSection';
import CohortHeatmapSection from '@/components/CohortHeatmapSection';
import Link from 'next/link';
import { ErrorState } from '@/components/ErrorState';

interface KPIData {
  active_mrr: number;
  active_users: number;
  nrr_pct: number | null;
  churn_rate_pct: number | null;
  latest_month: string | null;
}

async function getKPIs(): Promise<{ data: KPIData | null; error: string | null }> {
  try {
    const res = await fetch('http://localhost:3000/api/kpis', { cache: 'no-store' });
    const json = await res.json();
    if (!res.ok || json.error) {
      return { data: null, error: json.error || 'Failed to load KPI data' };
    }
    return { data: json.data, error: null };
  } catch (e) {
    return { data: null, error: 'Failed to connect to the API' };
  }
}

export default async function DashboardPage() {
  const { data: kpis, error } = await getKPIs();

  if (error || !kpis) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <h1 className="mb-6 text-2xl font-bold text-gray-900">MetricPulse</h1>
        <ErrorState message={error ?? 'Failed to load dashboard data'} />
      </main>
    );
  }

  const formatCurrency = (n: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n);

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">MetricPulse</h1>
      <Link href="/pipeline-health" className="text-sm text-blue-600 hover:underline">
          View Pipeline Health →
      </Link>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard label="Active MRR" value={formatCurrency(kpis.active_mrr)} />
        <KPICard label="Active Users" value={kpis.active_users.toLocaleString()} />
        <KPICard
          label="Net Revenue Retention"
          value={kpis.nrr_pct !== null ? `${kpis.nrr_pct}%` : 'N/A'}
          sublabel={kpis.latest_month ? `As of ${kpis.latest_month}` : undefined}
        />
        <KPICard
          label="Churn Rate"
          value={kpis.churn_rate_pct !== null ? `${kpis.churn_rate_pct}%` : 'N/A'}
          sublabel={kpis.latest_month ? `As of ${kpis.latest_month}` : undefined}
        />
      </div>
      
      <div className="mt-6">
        <MRRWaterfallSection />
      </div>
      <div className="mt-6">
        <CohortHeatmapSection />
      </div>

    </main>
  );
}