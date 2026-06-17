'use client';

import { useEffect, useState } from 'react';
import { fetchPresetPayload } from '@/lib/api';
import {
  EXAMPLE_PROFILES,
  PRESET_YEAR,
  PRESETS,
  hasStaticPresetPayload,
  type ExampleProfile,
  type PresetId,
  type PrecomputedExample,
  type StaticPresetId,
} from '@/lib/presets';

interface Props {
  presetId: PresetId;
  /** Currently-selected example profile id (so the matching card is highlighted). */
  activeExampleId?: string | null;
  /** Called when the user clicks a sample-family card. The parent should
   * apply the profile to the household form so the impact chart below
   * hydrates from the precomputed JSON. */
  onSelectExample?: (profile: ExampleProfile) => void;
}

function formatUsd(value: number): string {
  const abs = Math.abs(value);
  const sign = value < 0 ? '\u2212' : '';
  if (abs >= 1000) {
    return `${sign}$${Math.round(abs).toLocaleString('en-US')}`;
  }
  return `${sign}$${abs.toFixed(0)}`;
}

/**
 * Three illustrative household outcomes rendered above the household
 * net-income chart. Every preset reads precomputed JSON. Clicking a card
 * applies that profile to the household form.
 */
export default function SampleFamilyImpacts({
  presetId,
  activeExampleId,
  onSelectExample,
}: Props) {
  const [staticPayload, setStaticPayload] = useState<{
    presetId: StaticPresetId;
    examples: PrecomputedExample[];
    year: number;
  } | null>(null);
  const [error, setError] = useState<{
    presetId: PresetId;
    message: string;
  } | null>(null);
  const preset = PRESETS[presetId];

  useEffect(() => {
    if (!hasStaticPresetPayload(presetId)) return undefined;

    let cancelled = false;
    fetchPresetPayload(presetId)
      .then((p) => {
        if (!cancelled) {
          setStaticPayload({
            presetId,
            examples: p.examples,
            year: p.year,
          });
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError({
            presetId,
            message:
              e instanceof Error ? e.message : 'Failed to load examples',
          });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [presetId]);

  const staticPayloadForPreset =
    staticPayload?.presetId === presetId ? staticPayload : null;
  const examples = staticPayloadForPreset?.examples;
  const year = staticPayloadForPreset?.year ?? PRESET_YEAR;
  const errorForPreset = error?.presetId === presetId ? error.message : null;

  if (errorForPreset) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
        Could not load the sample-family impacts ({errorForPreset}).
      </div>
    );
  }

  if (!examples) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-4 text-sm text-gray-500">
        Loading sample-family impacts&hellip;
      </div>
    );
  }

  return (
    <section className="bg-white border border-gray-200 rounded-lg p-5">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        Sample family impacts
      </h3>
      <p className="text-sm text-gray-500 mb-4">
        How {preset.label.replace(/'/g, '\u2019')} ($
        {preset.ctcAmount}/child) would affect three representative Rhode
        Island households in {year}. Click a card to load its
        net-income chart below.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {examples.map((ex) => {
          const profile =
            EXAMPLE_PROFILES.find((p) => p.id === ex.profile.id) ?? ex.profile;
          const change = ex.household.benefit_at_income.difference;
          const isActive = activeExampleId === ex.profile.id;
          return (
            <button
              key={ex.profile.id}
              type="button"
              onClick={() => onSelectExample?.(profile)}
              aria-pressed={isActive}
              className={`text-left rounded-lg border p-4 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                isActive
                  ? 'border-primary-500 bg-primary-50 shadow-sm'
                  : 'border-gray-200 bg-gray-50 hover:bg-white hover:border-primary-300'
              }`}
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
            </button>
          );
        })}
      </div>
    </section>
  );
}
