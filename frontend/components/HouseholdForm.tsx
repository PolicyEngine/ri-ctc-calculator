'use client';

import { useState, useEffect } from 'react';
import type { ReformParams } from '@/lib/types';

interface Props {
  ageHead: number;
  setAgeHead: (age: number) => void;
  ageSpouse: number | null;
  setAgeSpouse: (age: number | null) => void;
  married: boolean;
  setMarried: (married: boolean) => void;
  dependentAges: number[];
  setDependentAges: (ages: number[]) => void;
  income: number;
  setIncome: (income: number) => void;
  reformParams: ReformParams;
  setReformParams: (params: ReformParams) => void;
  onCalculate: () => void;
  calculationTriggered: boolean;
  hasChanges: boolean;
}

export default function HouseholdForm({
  ageHead,
  setAgeHead,
  ageSpouse,
  setAgeSpouse,
  married,
  setMarried,
  dependentAges,
  setDependentAges,
  income,
  setIncome,
  reformParams,
  setReformParams,
  onCalculate,
  calculationTriggered,
  hasChanges,
}: Props) {
  // Accordion state
  const [expandedStep, setExpandedStep] = useState<number>(1);
  const [showCTCCustomization, setShowCTCCustomization] = useState(false);
  const [showExemptionCustomization, setShowExemptionCustomization] = useState(false);

  const handleMarriedChange = (value: boolean) => {
    setMarried(value);
    if (!value) {
      setAgeSpouse(null);
    } else {
      setAgeSpouse(35);
    }
  };

  const handleDependentCountChange = (count: number) => {
    const currentAges = [...dependentAges];
    if (count > currentAges.length) {
      // Add dependents
      while (currentAges.length < count) {
        currentAges.push(5);
      }
    } else {
      // Remove dependents
      currentAges.splice(count);
    }
    setDependentAges(currentAges);
  };

  const handleDependentAgeChange = (index: number, age: number) => {
    const newAges = [...dependentAges];
    newAges[index] = age;
    setDependentAges(newAges);
  };

  const toggleStep = (step: number) => {
    setExpandedStep(expandedStep === step ? 0 : step);
  };

  const StepHeader = ({
    stepNumber,
    title,
    isExpanded
  }: {
    stepNumber: number;
    title: string;
    isExpanded: boolean;
  }) => (
    <button
      onClick={() => toggleStep(stepNumber)}
      className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-all ${
        isExpanded
          ? 'bg-primary-50 border-2 border-primary-500'
          : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
      }`}
    >
      <div className="flex items-center space-x-3">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold ${
          isExpanded
            ? 'bg-primary-500 text-white'
            : 'bg-gray-300 text-gray-600'
        }`}>
          {stepNumber}
        </div>
        <span className={`font-semibold ${isExpanded ? 'text-primary-600' : 'text-gray-700'}`}>
          {title}
        </span>
      </div>
      <span className="text-gray-400">{isExpanded ? '▼' : '▶'}</span>
    </button>
  );

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-4 sticky top-4">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-primary mb-1">Household Configuration</h2>
        <p className="text-sm text-gray-600">Adjust any step to see updated results</p>
      </div>

      {/* STEP 1: Basic Information */}
      <div>
        <StepHeader
          stepNumber={1}
          title="Basic Information"
          isExpanded={expandedStep === 1}
        />
        {expandedStep === 1 && (
          <div className="mt-4 space-y-4 pl-2">
            {/* Income */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Annual Household Income
              </label>
              <input
                type="number"
                value={income}
                onChange={(e) => setIncome(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                min="0"
                max="1000000"
                step="1000"
              />
              <p className="text-xs text-gray-500 mt-1">
                Your total annual household income (AGI)
              </p>
            </div>

            {/* Married */}
            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={married}
                  onChange={(e) => handleMarriedChange(e.target.checked)}
                  className="w-4 h-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <span className="text-sm font-semibold text-gray-700">Are you married?</span>
              </label>
            </div>

            {/* Age Head */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                How old are you?
              </label>
              <input
                type="number"
                value={ageHead}
                onChange={(e) => setAgeHead(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                min="18"
                max="100"
              />
            </div>

            {/* Age Spouse */}
            {married && (
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  How old is your spouse?
                </label>
                <input
                  type="number"
                  value={ageSpouse || 35}
                  onChange={(e) => setAgeSpouse(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                  min="18"
                  max="100"
                />
              </div>
            )}
          </div>
        )}
      </div>

      {/* STEP 2: Dependents */}
      <div>
        <StepHeader
          stepNumber={2}
          title={`Dependents (${dependentAges.length})`}
          isExpanded={expandedStep === 2}
        />
        {expandedStep === 2 && (
          <div className="mt-4 space-y-4 pl-2">
            {/* Dependents Count */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                How many children or dependents?
              </label>
              <input
                type="number"
                value={dependentAges.length}
                onChange={(e) => handleDependentCountChange(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                min="0"
                max="10"
              />
            </div>

            {/* Dependent Ages */}
            {dependentAges.length > 0 && (
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  What are their ages?
                </label>
                <div className="space-y-2">
                  {dependentAges.map((age, index) => (
                    <div key={index}>
                      <label className="text-xs text-gray-600 mb-1 block">
                        Child {index + 1}
                      </label>
                      <input
                        type="number"
                        value={age}
                        onChange={(e) => handleDependentAgeChange(index, Number(e.target.value))}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                        min="0"
                        max="25"
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* STEP 3: Advanced Options */}
      <div>
        <StepHeader
          stepNumber={3}
          title="Advanced Options"
          isExpanded={expandedStep === 3}
        />
        {expandedStep === 3 && (
          <div className="mt-4 space-y-4 pl-2">

            {/* CTC Customization */}
            <div>
              <button
                onClick={() => setShowCTCCustomization(!showCTCCustomization)}
                className="w-full text-left px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-md text-sm font-semibold text-gray-700 flex items-center justify-between"
              >
                <span>Customize RI CTC</span>
                <span>{showCTCCustomization ? '−' : '+'}</span>
              </button>

              {showCTCCustomization && (
                <div className="mt-4 space-y-4 pl-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      CTC Amount per Child
                    </label>
                    <input
                      type="number"
                      value={reformParams.ctc_amount}
                      onChange={(e) =>
                        setReformParams({ ...reformParams, ctc_amount: Number(e.target.value) })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      min="0"
                      max="10000"
                      step="100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Age Limit</label>
                    <input
                      type="number"
                      value={reformParams.ctc_age_limit}
                      onChange={(e) =>
                        setReformParams({ ...reformParams, ctc_age_limit: Number(e.target.value) })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                      min="0"
                      max="26"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Refundability
                    </label>
                    <select
                      value={
                        reformParams.ctc_refundability_cap === 0
                          ? 'non-refundable'
                          : reformParams.ctc_refundability_cap === reformParams.ctc_amount
                          ? 'fully-refundable'
                          : 'partially-refundable'
                      }
                      onChange={(e) => {
                        const value = e.target.value;
                        if (value === 'non-refundable') {
                          setReformParams({ ...reformParams, ctc_refundability_cap: 0 });
                        } else if (value === 'fully-refundable') {
                          setReformParams({
                            ...reformParams,
                            ctc_refundability_cap: reformParams.ctc_amount,
                          });
                        } else {
                          setReformParams({
                            ...reformParams,
                            ctc_refundability_cap: reformParams.ctc_amount / 2,
                          });
                        }
                      }}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                    >
                      <option value="non-refundable">Non-refundable</option>
                      <option value="partially-refundable">Partially refundable</option>
                      <option value="fully-refundable">Fully refundable</option>
                    </select>
                  </div>
                </div>
              )}
            </div>

            {/* Exemption Customization */}
            <div>
              <button
                onClick={() => setShowExemptionCustomization(!showExemptionCustomization)}
                className="w-full text-left px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-md text-sm font-semibold text-gray-700 flex items-center justify-between"
              >
                <span>Customize Dependent Exemption</span>
                <span>{showExemptionCustomization ? '−' : '+'}</span>
              </button>

              {showExemptionCustomization && (
                <div className="mt-4 space-y-4 pl-4">
                  <div>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={reformParams.enable_exemption_reform}
                        onChange={(e) =>
                          setReformParams({
                            ...reformParams,
                            enable_exemption_reform: e.target.checked,
                          })
                        }
                        className="w-4 h-4 text-primary focus:ring-primary border-gray-300 rounded"
                      />
                      <span className="text-sm font-semibold text-gray-700">
                        Enable Dependent Exemption Reform
                      </span>
                    </label>
                  </div>

                  {reformParams.enable_exemption_reform && (
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Exemption Amount
                      </label>
                      <input
                        type="number"
                        value={reformParams.exemption_amount}
                        onChange={(e) =>
                          setReformParams({
                            ...reformParams,
                            exemption_amount: Number(e.target.value),
                          })
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                        min="0"
                        max="20000"
                        step="100"
                      />
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Calculate Button */}
      <button
        onClick={onCalculate}
        disabled={calculationTriggered && !hasChanges}
        className={`w-full font-bold py-3 px-6 rounded-md transition-colors shadow-md ${
          calculationTriggered && !hasChanges
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-primary-500 hover:bg-primary-600 text-white'
        }`}
      >
        {calculationTriggered ? 'Recalculate Impact' : 'Calculate Impact'}
      </button>
    </div>
  );
}
