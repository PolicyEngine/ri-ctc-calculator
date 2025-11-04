'use client';

import { useAggregateImpact } from '@/hooks/useAggregateImpact';
import type { ReformParams } from '@/lib/types';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface Props {
  reformParams: ReformParams;
}

export default function AggregateImpact({ reformParams }: Props) {
  const { data, isLoading, error } = useAggregateImpact(reformParams);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Calculating statewide impact...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Error Calculating Aggregate Impact</h3>
        <p className="text-red-700">{(error as Error).message}</p>
      </div>
    );
  }

  if (!data) return null;

  const formatCurrency = (value: number) => `$${value.toLocaleString()}`;
  const formatMillion = (value: number) => `$${(value / 1e6).toFixed(1)}M`;

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-primary">Statewide Impact Analysis</h2>

      <p className="text-gray-700">
        This analysis uses the Rhode Island microsimulation dataset to estimate the aggregate
        impact of the RI CTC reform across all Rhode Island households.
      </p>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-primary-50 rounded-lg p-6 border border-primary-500">
          <p className="text-sm text-gray-700 mb-2">Total Cost</p>
          <p className="text-3xl font-bold text-primary-600">{formatMillion(data.total_cost)}</p>
          <p className="text-xs text-gray-600 mt-1">Total annual cost across all RI households</p>
        </div>

        <div className="bg-green-50 rounded-lg p-6 border border-success">
          <p className="text-sm text-gray-700 mb-2">Households Benefiting</p>
          <p className="text-3xl font-bold text-green-600">
            {data.beneficiaries.toLocaleString()}
          </p>
          <p className="text-xs text-gray-600 mt-1">Number of RI households that benefit</p>
        </div>

        <div className="bg-blue-50 rounded-lg p-6 border border-blue-500">
          <p className="text-sm text-gray-700 mb-2">Average Benefit</p>
          <p className="text-3xl font-bold text-blue-600">{formatCurrency(data.avg_benefit)}</p>
          <p className="text-xs text-gray-600 mt-1">Average annual benefit per household</p>
        </div>
      </div>

      {/* Poverty Impact */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-50 rounded-lg p-6 border border-gray-300">
          <p className="text-sm text-gray-600 mb-2">Poverty Rate Change</p>
          <p className="text-3xl font-bold text-gray-800">
            {data.poverty_percent_change.toFixed(2)}%
          </p>
        </div>

        <div className="bg-yellow-50 rounded-lg p-6 border border-yellow-500">
          <p className="text-sm text-gray-600 mb-2">Child Poverty Rate Change</p>
          <p className="text-3xl font-bold text-yellow-700">
            {data.child_poverty_percent_change.toFixed(2)}%
          </p>
        </div>

        <div className="bg-indigo-50 rounded-lg p-6 border border-indigo-500">
          <p className="text-sm text-gray-600 mb-2">Winners / Losers</p>
          <p className="text-3xl font-bold text-indigo-700">
            {data.winners_rate.toFixed(1)}% / {data.losers_rate.toFixed(1)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">Percentage of households that gain vs. lose</p>
        </div>
      </div>

      <hr className="border-gray-200" />

      {/* Impact by Income Bracket */}
      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-4">Impact by Income Bracket</h3>

        <div className="bg-white border rounded-lg p-6">
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={data.by_income_bracket}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="bracket" stroke="#666" />
              <YAxis tickFormatter={formatCurrency} stroke="#666" />
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Bar dataKey="avg_benefit" fill="#319795" name="Average Benefit" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Detailed Table */}
        <div className="mt-6">
          <details className="bg-gray-50 rounded-lg p-4">
            <summary className="cursor-pointer font-semibold text-gray-700 hover:text-primary">
              View detailed breakdown
            </summary>
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-300">
                <thead>
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                      Income Bracket
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                      Benefiting Households
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                      Total Cost
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                      Avg Benefit
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {data.by_income_bracket.map((bracket, index) => (
                    <tr key={index} className="hover:bg-gray-100">
                      <td className="px-4 py-3 text-sm text-gray-900">{bracket.bracket}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {bracket.beneficiaries.toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {formatCurrency(bracket.total_cost)}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {formatCurrency(bracket.avg_benefit)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        </div>
      </div>
    </div>
  );
}
