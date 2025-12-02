'use client';

import { useState } from 'react';
import HouseholdForm from '@/components/HouseholdForm';
import ImpactAnalysis from '@/components/ImpactAnalysis';
import AggregateImpact from '@/components/AggregateImpact';
import type { ReformParams } from '@/lib/types';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'impact' | 'aggregate'>('impact');
  const [calculationTriggered, setCalculationTriggered] = useState(false);

  // Household configuration (current form values)
  const [ageHead, setAgeHead] = useState(35);
  const [ageSpouse, setAgeSpouse] = useState<number | null>(null);
  const [married, setMarried] = useState(false);
  const [dependentAges, setDependentAges] = useState<number[]>([5]);
  const [income, setIncome] = useState(50000);

  // Reform parameters with defaults
  const [reformParams, setReformParams] = useState<ReformParams>({
    ctc_amount: 1000,
    ctc_age_limit: 18,
    ctc_refundability_cap: 0,
    ctc_phaseout_rate: 0,
    ctc_phaseout_thresholds: {
      SINGLE: 0,
      JOINT: 0,
      HEAD_OF_HOUSEHOLD: 0,
      SURVIVING_SPOUSE: 0,
      SEPARATE: 0,
    },
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

  // Last calculated params (the ones actually used for calculation)
  const [calculatedAgeHead, setCalculatedAgeHead] = useState(35);
  const [calculatedAgeSpouse, setCalculatedAgeSpouse] = useState<number | null>(null);
  const [calculatedMarried, setCalculatedMarried] = useState(false);
  const [calculatedDependentAges, setCalculatedDependentAges] = useState<number[]>([5]);
  const [calculatedIncome, setCalculatedIncome] = useState(50000);
  const [calculatedReformParams, setCalculatedReformParams] = useState<ReformParams>(reformParams);

  // Check if anything has changed since last calculation
  const hasChanges =
    ageHead !== calculatedAgeHead ||
    ageSpouse !== calculatedAgeSpouse ||
    married !== calculatedMarried ||
    JSON.stringify(dependentAges) !== JSON.stringify(calculatedDependentAges) ||
    income !== calculatedIncome ||
    JSON.stringify(reformParams) !== JSON.stringify(calculatedReformParams);

  const handleCalculate = () => {
    setCalculationTriggered(true);
    setCalculatedAgeHead(ageHead);
    setCalculatedAgeSpouse(ageSpouse);
    setCalculatedMarried(married);
    setCalculatedDependentAges(dependentAges);
    setCalculatedIncome(income);
    setCalculatedReformParams(reformParams);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-primary-500 text-white py-8 px-4 shadow-md">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-2">
            Rhode Island Child Tax Credit Calculator
          </h1>
          <p className="text-lg opacity-90">
            Design a Rhode Island child tax credit and see how it would affect your household and the state
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Left Sidebar: Configuration Form */}
          <div className="lg:col-span-1">
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
              reformParams={reformParams}
              setReformParams={setReformParams}
              onCalculate={handleCalculate}
              calculationTriggered={calculationTriggered}
              hasChanges={hasChanges}
            />
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-3">
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
                <div className="flex space-x-1 mb-4">
                  <button
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
                    onClick={() => setActiveTab('aggregate')}
                    className={`px-6 py-3 rounded-t-lg font-semibold transition-colors ${
                      activeTab === 'aggregate'
                        ? 'bg-white text-primary-600 border-t-4 border-primary-500'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    Statewide Impact
                  </button>
                </div>

                {/* Tab Content */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  {activeTab === 'impact' ? (
                    <ImpactAnalysis
                      ageHead={calculatedAgeHead}
                      ageSpouse={calculatedMarried ? calculatedAgeSpouse : null}
                      dependentAges={calculatedDependentAges}
                      income={calculatedIncome}
                      reformParams={calculatedReformParams}
                    />
                  ) : (
                    <AggregateImpact reformParams={calculatedReformParams} />
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
