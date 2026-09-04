'use client';

import { useEffect, useState } from 'react';
import MRRWaterfallChart from './MRRWaterfallChart';
import { transformToWaterfall, WaterfallRow } from '@/lib/transformMRR';
import { Skeleton } from '@/components/Skeleton';
import { ErrorState } from '@/components/ErrorState';

export default function MRRWaterfallSection() {
  const [data, setData] = useState<WaterfallRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/mrr')
      .then((res) => res.json())
      .then((json) => setData(transformToWaterfall(json.data)))
      .catch(() => setError('Failed to load MRR data'));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!data) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <Skeleton className="mb-4 h-6 w-56" />
      <Skeleton className="h-96 w-full" />
    </div>
  );
}

  return <MRRWaterfallChart data={data} />;
}