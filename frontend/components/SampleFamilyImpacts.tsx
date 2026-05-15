'use client';

import { useEffect, useState } from 'react';
import { fetchPresetPayload } from '@/lib/api';
import {
  PRESETS,
  type PresetId,
  type PresetPayload,
} from '@/lib/presets';

interface Props {
  presetId: PresetId;
}

function formatUsd(value: number): string {
  const abs = Math.abs(value);
  const sign = value < 0 ? '−' : '';
  if (abs >= 1000) {
    return `${sign}$${Math.round(abs).toLocaleString('en-US')}`;
  }
  return `${sign}$${abs.toFixed(0)}`;
}

/**
 * Three illustrative household outcomes rendered alongside the active
 * preset's impact analysis. Data is read from the precomputed preset
 * JSON so it appears instantly with no API call.
 */
export default function SampleFamilyImpacts({ presetId }: Props) {
  const [payload, setPayload] = useState<PresetPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const preset = PRESETS[presetId];

  useEffect(() => {
    let cancelled = false;
    setPayload(null);
    setError(null);
    fetchPresetPayload(presetId)
      .then((p) => {
        if (!cancelled) setPayload(p);
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Failed to load examples');
        }
      });
    return () => {
      cancelled = true;
    };
  }, [presetId]);

  if (error) {
    return (
      <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
        Could not load the sample-family impacts ({error}).
      </div>
    );
  }

  if (!payload) {
    return (
      <div className="mt-6 bg-white border border-gray-200 rounded-lg p-4 text-sm text-gray-500">
        Loading sample-family impacts…
      </div>
    );
  }

  return (
    <section className="mt-6 bg-white border border-gray-200 rounded-lg p-5">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        Sample family impacts
      </h3>
      <p className="text-sm text-gray-500 mb-4">
        How {preset.label.replace(/'/g, '\u2019')} ($
        {preset.ctcAmount}/child) would affect three representative Rhode
        Island households in {payload.year}.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {payload.examples.map((ex) => {
          const change = ex.household.benefit_at_income.difference;
          return (
            <div
              key={ex.profile.id}
              className="rounded-lg border border-gray-200 p-4 bg-gray-50"
            >
              <p className="text-sm font-medium text-gray-800 mb-2">
                {ex.profile.label}
              </p>
              <p
                className={`text-2xl font-bold ${
                  change > 0
                    ? 'text-green-600'
                    : change < 0
                      ? 'text-red-600'
                      : 'text-gray-700'
                }`}
              >
                {change > 0 ? '+' : ''}
                {formatUsd(change)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Annual change in net income
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
