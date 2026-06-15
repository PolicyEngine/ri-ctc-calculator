'use client';

import { useCallback, useState } from 'react';
import HouseholdForm from '@/components/HouseholdForm';
import ImpactAnalysis from '@/components/ImpactAnalysis';
import AggregateImpact from '@/components/AggregateImpact';
import SampleFamilyImpacts from '@/components/SampleFamilyImpacts';
import type { ReformParams } from '@/lib/types';
import {
  EXAMPLE_PROFILES,
  PRESET_YEAR,
  presetReformParams,
  type ExampleProfile,
  type PresetId,
} from '@/lib/presets';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'impact' | 'aggregate'>('impact');
  const [calculationTriggered, setCalculationTriggered] = useState(false);

  // Household configuration (current form values)
  const [ageHead, _setAgeHead] = useState(35);
  const [ageSpouse, _setAgeSpouse] = useState<number | null>(null);
  const [married, _setMarried] = useState(false);
  const [dependentAges, _setDependentAges] = useState<number[]>([5]);
  const [income, _setIncome] = useState(50000);
  const [year, _setYear] = useState(2027);

  // Reform parameters with defaults
  const [reformParams, _setReformParams] = useState<ReformParams>({
    ctc_amount: 1000,
    ctc_age_limit: 18,
    // Fully refundable by default: the refundability cap is set high
    // enough to cover any realistic per-tax-unit credit amount. The
    // user-facing toggle was intentionally removed — every custom
    // reform inherits the same fully-refundable behavior the presets use.
    ctc_refundability_cap: 100000,
    ctc_phaseout_rate: 0,
    ctc_phaseout_thresholds: {
      SINGLE: 0,
      JOINT: 0,
      HEAD_OF_HOUSEHOLD: 0,
      SURVIVING_SPOUSE: 0,
      SEPARATE: 0,
    },
    ctc_stepped_phaseout: false,
    ctc_stepped_phaseout_threshold: 0,
    ctc_stepped_phaseout_increment: 0,
    ctc_stepped_phaseout_rate_per_step: 0,
    ctc_stepped_phaseout_thresholds: null,
    ctc_stepped_phaseout_increments: null,
    ctc_young_child_boost_amount: 0,
    ctc_young_child_boost_age_limit: 6,
    enable_exemption_reform: false,
    exemption_amount: 5200,
    exemption_age_limit_enabled: true,
    exemption_age_threshold: 18,
    exemption_phaseout_rate: 0,
    exemption_phaseout_thresholds: {
      SINGLE: 0,
      JOINT: 0,
      HEAD_OF_HOUSEHOLD: 0,
      SURVIVING_SPOUSE: 0,
      SEPARATE: 0,
    },
  });

  // Which policy preset, if any, is currently active. Any
  // user edit to a reform or household field clears this back to null so
  // we fall through to the live calculator instead of the precomputed JSON.
  const [activePresetId, setActivePresetId] = useState<PresetId | null>(null);

  // Wrapped setters that clear the preset selection on any manual edit.
  const setAgeHead = useCallback((v: number) => {
    setActivePresetId(null);
    _setAgeHead(v);
  }, []);
  const setAgeSpouse = useCallback((v: number | null) => {
    setActivePresetId(null);
    _setAgeSpouse(v);
  }, []);
  const setMarried = useCallback((v: boolean) => {
    setActivePresetId(null);
    _setMarried(v);
  }, []);
  const setDependentAges = useCallback((v: number[]) => {
    setActivePresetId(null);
    _setDependentAges(v);
  }, []);
  const setIncome = useCallback((v: number) => {
    setActivePresetId(null);
    _setIncome(v);
  }, []);
  const setYear = useCallback((v: number) => {
    setActivePresetId(null);
    _setYear(v);
  }, []);
  const setReformParams = useCallback((v: ReformParams) => {
    setActivePresetId(null);
    _setReformParams(v);
  }, []);

  const applyPreset = useCallback((id: PresetId) => {
    // GA4 parity (PR #36).
    if (
      typeof window !== 'undefined' &&
      (window as unknown as { gtag?: (...args: unknown[]) => void }).gtag
    ) {
      (window as unknown as { gtag: (...args: unknown[]) => void }).gtag(
        'event',
        'preset_applied',
        { preset_id: id },
      );
    }
    _setReformParams(presetReformParams(id));
    _setYear(PRESET_YEAR);
    setActivePresetId(id);
  }, []);

  // Apply one of the precomputed example profiles to the household form
  // WITHOUT clearing the active preset (raw setters skip the dirty trigger).
  // The household chart below will then hydrate from the preset JSON via
  // useHouseholdImpact's matchingExampleId branch.
  const applyExample = useCallback((profile: ExampleProfile) => {
    _setAgeHead(profile.age_head);
    _setMarried(profile.married);
    _setAgeSpouse(profile.married ? profile.age_spouse : null);
    _setDependentAges([...profile.dependent_ages]);
    _setIncome(profile.income);
  }, []);

  // Last calculated params (the ones actually used for calculation)
  const [calculatedAgeHead, setCalculatedAgeHead] = useState(35);
  const [calculatedAgeSpouse, setCalculatedAgeSpouse] = useState<number | null>(null);
  const [calculatedMarried, setCalculatedMarried] = useState(false);
  const [calculatedDependentAges, setCalculatedDependentAges] = useState<number[]>([5]);
  const [calculatedIncome, setCalculatedIncome] = useState(50000);
  const [calculatedYear, setCalculatedYear] = useState(2027);
  const [calculatedReformParams, setCalculatedReformParams] = useState<ReformParams>(reformParams);
  const [calculatedPresetId, setCalculatedPresetId] = useState<PresetId | null>(null);

  // Check if anything has changed since last calculation
  const hasChanges =
    ageHead !== calculatedAgeHead ||
    ageSpouse !== calculatedAgeSpouse ||
    married !== calculatedMarried ||
    JSON.stringify(dependentAges) !== JSON.stringify(calculatedDependentAges) ||
    income !== calculatedIncome ||
    year !== calculatedYear ||
    JSON.stringify(reformParams) !== JSON.stringify(calculatedReformParams) ||
    activePresetId !== calculatedPresetId;

  const handleCalculate = () => {
    setCalculationTriggered(true);
    setCalculatedAgeHead(ageHead);
    setCalculatedAgeSpouse(ageSpouse);
    setCalculatedMarried(married);
    setCalculatedDependentAges(dependentAges);
    setCalculatedIncome(income);
    setCalculatedYear(year);
    setCalculatedReformParams(reformParams);
    setCalculatedPresetId(activePresetId);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-primary-500 text-white py-8 px-4 shadow-md">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-2">
            Rhode Island Child Tax Credit Calculator
          </h1>
          <p className="text-lg opacity-90">
            Design a Rhode Island child tax credit and see how it would affect your household and the state
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Left Sidebar: Configuration Form */}
          <aside className="lg:col-span-1" aria-label="Household configuration">
            <HouseholdForm
              ageHead={ageHead}
              setAgeHead={setAgeHead}
              ageSpouse={ageSpouse}
              setAgeSpouse={setAgeSpouse}
              married={married}
              setMarried={setMarried}
              dependentAges={dependentAges}
              setDependentAges={setDependentAges}
              income={income}
              setIncome={setIncome}
              year={year}
              setYear={setYear}
              reformParams={reformParams}
              setReformParams={setReformParams}
              onApplyPreset={applyPreset}
              activePresetId={activePresetId}
              onCalculate={handleCalculate}
              calculationTriggered={calculationTriggered}
              hasChanges={hasChanges}
            />
          </aside>

          {/* Main Content Area */}
          <section className="lg:col-span-3" aria-label="Results">
            {!calculationTriggered ? (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-primary mb-4">Get Started</h2>
                <p className="text-gray-700 mb-4">
                  Configure your household in the sidebar, then click{' '}
                  <span className="font-semibold">&ldquo;Calculate Impact&rdquo;</span> to see:
                </p>
                <ul className="list-disc list-inside space-y-2 text-gray-700">
                  <li>How the Rhode Island Child Tax Credit would benefit your household</li>
                  <li>The income range where you would receive the credit</li>
                  <li>Your specific benefit at any income level</li>
                  <li>Statewide impact across all Rhode Island households</li>
                </ul>
              </div>
            ) : (
              <>
                {/* Tabs */}
                <nav aria-label="Results tabs" className="flex space-x-1 mb-4" role="tablist">
                  <button
                    role="tab"
                    aria-selected={activeTab === 'impact'}
                    aria-controls="panel-impact"
                    onClick={() => setActiveTab('impact')}
                    className={`px-6 py-3 rounded-t-lg font-semibold transition-colors ${
                      activeTab === 'impact'
                        ? 'bg-white text-primary-600 border-t-4 border-primary-500'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    Impact Analysis
                  </button>
                  <button
                    role="tab"
                    aria-selected={activeTab === 'aggregate'}
                    aria-controls="panel-aggregate"
                    onClick={() => setActiveTab('aggregate')}
                    className={`px-6 py-3 rounded-t-lg font-semibold transition-colors ${
                      activeTab === 'aggregate'
                        ? 'bg-white text-primary-600 border-t-4 border-primary-500'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    Statewide Impact
                  </button>
                </nav>

                {/* Tab Content. Both panels are mounted at once so both
                    queries fire on Calculate; the inactive panel is hidden
                    via the HTML `hidden` attribute. This avoids the
                    "click the Statewide tab to start the calculation"
                    wait. */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <div
                    id="panel-impact"
                    role="tabpanel"
                    aria-label="Impact Analysis"
                    hidden={activeTab !== 'impact'}
                    className="space-y-6"
                  >
                    {calculatedPresetId && (
                      <SampleFamilyImpacts
                        presetId={calculatedPresetId}
                        activeExampleId={
                          EXAMPLE_PROFILES.find(
                            (p) =>
                              p.age_head === calculatedAgeHead &&
                              p.married === calculatedMarried &&
                              p.income === calculatedIncome &&
                              p.dependent_ages.length ===
                                calculatedDependentAges.length &&
                              p.dependent_ages.every(
                                (a, i) => a === calculatedDependentAges[i],
                              ),
                          )?.id ?? null
                        }
                        onSelectExample={(profile) => {
                          applyExample(profile);
                          setCalculationTriggered(true);
                          setCalculatedAgeHead(profile.age_head);
                          setCalculatedAgeSpouse(
                            profile.married ? profile.age_spouse : null,
                          );
                          setCalculatedMarried(profile.married);
                          setCalculatedDependentAges([
                            ...profile.dependent_ages,
                          ]);
                          setCalculatedIncome(profile.income);
                          setCalculatedYear(PRESET_YEAR);
                          setCalculatedReformParams(
                            presetReformParams(calculatedPresetId),
                          );
                          setCalculatedPresetId(calculatedPresetId);
                        }}
                      />
                    )}
                    <ImpactAnalysis
                      ageHead={calculatedAgeHead}
                      ageSpouse={calculatedMarried ? calculatedAgeSpouse : null}
                      dependentAges={calculatedDependentAges}
                      income={calculatedIncome}
                      year={calculatedYear}
                      reformParams={calculatedReformParams}
                      presetId={calculatedPresetId}
                    />
                  </div>
                  <div
                    id="panel-aggregate"
                    role="tabpanel"
                    aria-label="Statewide Impact"
                    hidden={activeTab !== 'aggregate'}
                  >
                    <AggregateImpact
                      year={calculatedYear}
                      reformParams={calculatedReformParams}
                      presetId={calculatedPresetId}
                    />
                  </div>
                </div>
              </>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
