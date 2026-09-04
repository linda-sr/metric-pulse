'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { WaterfallRow } from '@/lib/transformMRR';

interface Props {
  data: WaterfallRow[];
}

const COLORS = {
  new: '#22c55e',
  expansion: '#3b82f6',
  contraction: '#f97316',
  churn: '#ef4444',
  resurrection: '#a855f7',
};

export default function MRRWaterfallChart({ data }: Props) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">MRR Movement by Month</h2>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="mrr_month" tick={{ fontSize: 11 }} angle={-45} textAnchor="end" height={60} />
          <YAxis tick={{ fontSize: 12 }} />
          {/* <Tooltip
            formatter={(value: number, name: string) => [`$${value.toLocaleString()}`, name]}
          /> */}
          <Tooltip
                formatter={(value: any, name: any) => [`$${value.toLocaleString()}`,name] as [string, string]}
          />

          <Legend />

          {/* Invisible spacer: pushes visible segments up to the correct running-total height */}
          <Bar dataKey="base" stackId="waterfall" fill="transparent" isAnimationActive={false} legendType="none" />

          <Bar dataKey="new" stackId="waterfall" fill={COLORS.new} name="New" />
          <Bar dataKey="expansion" stackId="waterfall" fill={COLORS.expansion} name="Expansion" />
          <Bar dataKey="resurrection" stackId="waterfall" fill={COLORS.resurrection} name="Resurrection" />
          <Bar dataKey="contraction" stackId="waterfall" fill={COLORS.contraction} name="Contraction" />
          <Bar dataKey="churn" stackId="waterfall" fill={COLORS.churn} name="Churn" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}