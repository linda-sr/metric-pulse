'use client';

import { useEffect, useState } from 'react';
import CohortHeatmap from './CohortHeatmap';
import { transformToCohortGrid, CohortGridRow } from '@/lib/transformCohorts';
import { Skeleton } from '@/components/Skeleton';
import { ErrorState } from '@/components/ErrorState';

export default function CohortHeatmapSection() {
  const [data, setData] = useState<CohortGridRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/cohorts')
      .then((res) => res.json())
      .then((json) => setData(transformToCohortGrid(json.data)))
      .catch(() => setError('Failed to load cohort data'));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!data) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <Skeleton className="mb-4 h-6 w-48" />
      <Skeleton className="h-64 w-full" />
    </div>
  );
}

  return <CohortHeatmap data={data} />;
}