import { Skeleton } from '@/components/Skeleton';

export default function DashboardLoading() {
  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <Skeleton className="mb-6 h-8 w-48" />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="mt-3 h-8 w-32" />
          </div>
        ))}
      </div>
      <Skeleton className="mt-6 h-96 w-full rounded-lg" />
    </main>
  );
}