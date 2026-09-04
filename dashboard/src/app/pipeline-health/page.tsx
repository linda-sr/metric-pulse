'use client';

import { useEffect, useState } from 'react';
import PipelineHealthCard from '@/components/PipelineHealthCard';
import RowCountsTable from '@/components/RowCountsTable';
import { Skeleton } from '@/components/Skeleton';
import { ErrorState } from '@/components/ErrorState';

export default function PipelineHealthPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/pipeline-health')
      .then((res) => res.json())
      .then((json) => {
        if (json.error) setError(json.error);
        else setData(json.data);
      })
      .catch(() => setError('Failed to load pipeline health data'));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!data) {
  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <Skeleton className="mb-6 h-8 w-64" />
      <div className="space-y-6">
        <Skeleton className="h-32 w-full rounded-lg" />
        <Skeleton className="h-64 w-full rounded-lg" />
      </div>
    </main>
  );
}

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Pipeline Observability</h1>
      <div className="space-y-6">
        <PipelineHealthCard dbtHealth={data.dbtHealth} />
        <RowCountsTable rowCounts={data.rowCounts} />
      </div>
    </main>
  );
}