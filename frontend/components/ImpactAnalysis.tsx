'use client';

import { useState } from 'react';
import { useHouseholdImpact } from '@/hooks/useHouseholdImpact';
import type { ReformParams } from '@/lib/types';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface Props {
  ageHead: number;
  ageSpouse: number | null;
  dependentAges: number[];
  income: number;
  reformParams: ReformParams;
}

export default function ImpactAnalysis({
  ageHead,
  ageSpouse,
  dependentAges,
  income,
  reformParams,
}: Props) {
  const [breakdownExpanded, setBreakdownExpanded] = useState(false);

  // Load full impact data (includes chart and benefit at income)
  const { data, isLoading, error } = useHouseholdImpact({
    age_head: ageHead,
    age_spouse: ageSpouse,
    dependent_ages: dependentAges,
    income: income,
    reform_params: reformParams,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Calculating impact (this may take up to 2 minutes)...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Error Calculating Impact</h3>
        <p className="text-red-700">{(error as Error).message}</p>
      </div>
    );
  }

  if (!data) return null;

  // Transform data for recharts and filter to relevant range
  const chartData = data.income_range
    .map((inc, i) => ({
      income: inc,
      baseline: data.ctc_baseline_range[i],
      reform: data.ctc_reform_range[i],
      benefit: data.ctc_reform_range[i] - data.ctc_baseline_range[i],
    }))
    .filter(d => d.income <= data.x_axis_max);

  const formatCurrency = (value: number) => `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const formatIncome = (value: number) => `$${(value / 1000).toFixed(0)}k`;

  // Extract benefit data from the response
  const benefitData = data.benefit_at_income;

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-primary">Impact Analysis</h2>

      {/* Your Personal Impact */}
      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-4">Your Personal Impact</h3>
        <p className="text-gray-600 mb-4">
          Based on your adjusted gross income of <strong>{formatCurrency(income)}</strong>
        </p>

        {/* Change in Net Income */}
        <div className="bg-green-50 rounded-lg p-6 border border-success">
          <p className="text-sm text-gray-700 mb-2">Change in Net Income</p>
          <p className="text-3xl font-bold text-green-600">
            {benefitData.difference > 0
              ? `+${formatCurrency(benefitData.difference)}/year`
              : '$0'}
          </p>

          {/* Breakdown */}
          {benefitData.difference > 0 && (
            <div className="mt-4 pt-4 border-t border-green-200">
              <p className="text-xs text-gray-600 font-semibold mb-3">Breakdown:</p>
              <div className="space-y-2">
                {benefitData.ctc_component > 0 && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-700">• CTC credit:</span>
                    <span className="font-semibold text-gray-900">
                      +{formatCurrency(benefitData.ctc_component)}
                    </span>
                  </div>
                )}
                {benefitData.exemption_tax_benefit !== 0 && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-700">
                      • Change in income tax:
                    </span>
                    <span className="font-semibold text-gray-900">
                      {benefitData.exemption_tax_benefit > 0 ? '+' : ''}{formatCurrency(benefitData.exemption_tax_benefit)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <hr className="border-gray-200" />

      {/* Chart */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-800">
          Change in Net Income from RI CTC Reform by Adjusted Gross Income (2026)
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData} margin={{ left: 20, right: 20, top: 5, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis
              dataKey="income"
              type="number"
              tickFormatter={formatIncome}
              stroke="#666"
              domain={[0, data.x_axis_max]}
              allowDataOverflow={false}
            />
            <YAxis
              tickFormatter={formatCurrency}
              stroke="#666"
              width={80}
            />
            <Tooltip
              formatter={(value: number) => formatCurrency(value)}
              labelFormatter={(value: number) => `Income: ${formatCurrency(value)}`}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="benefit"
              stroke="#319795"
              strokeWidth={3}
              name="Change in Net Income"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
