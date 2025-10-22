"""Test script to verify the personal exemption phase-out fix."""

from policyengine_us import Simulation
from ri_ctc_calc.calculations.reforms import create_custom_reform
import numpy as np

# Test at high income where exemptions should be fully phased out
test_income = 300_000

# Create household with 2 children
situation = {
    "people": {
        "parent": {
            "age": {"2026": 35},
            "employment_income": {"2026": test_income},
        },
        "child1": {
            "age": {"2026": 10},
        },
        "child2": {
            "age": {"2026": 12},
        },
    },
    "families": {
        "family": {
            "members": ["parent", "child1", "child2"],
        }
    },
    "marital_units": {
        "marital_unit": {
            "members": ["parent"],
        }
    },
    "tax_units": {
        "tax_unit": {
            "members": ["parent", "child1", "child2"],
            "filing_status": {"2026": "SINGLE"},
        }
    },
    "households": {
        "household": {
            "members": ["parent", "child1", "child2"],
            "state_name": {"2026": "RI"},
        }
    },
}

# Create reform with dependent exemption set to $0
reform = create_custom_reform(
    ctc_amount=1000,
    ctc_age_limit=18,
    ctc_refundability_cap=0,
    enable_exemption_reform=True,
    exemption_amount=0,  # Set to $0
    exemption_age_limit_enabled=True,
    exemption_age_threshold=18,
)

# Run simulations
sim_baseline = Simulation(situation=situation)
sim_reform = Simulation(situation=situation, reform=reform)

# Calculate exemptions
baseline_exemptions = sim_baseline.calculate("ri_exemptions", period=2026)
reform_exemptions = sim_reform.calculate("ri_exemptions", period=2026)

baseline_tax = sim_baseline.calculate("ri_income_tax", period=2026)
reform_tax = sim_reform.calculate("ri_income_tax", period=2026)

baseline_net_income = sim_baseline.calculate("household_net_income", period=2026)
reform_net_income = sim_reform.calculate("household_net_income", period=2026)

print(f"\n{'='*60}")
print(f"Testing Personal Exemption Phase-out Fix")
print(f"{'='*60}")
print(f"\nTest Income: ${test_income:,}")
print(f"\nReform Settings:")
print(f"  - CTC Amount: $1,000")
print(f"  - Dependent Exemption: $0 (disabled)")
print(f"\nResults:")
print(f"  Baseline RI Exemptions: ${baseline_exemptions[0]:,.0f}")
print(f"  Reform RI Exemptions:   ${reform_exemptions[0]:,.0f}")
print(f"  Exemption Change:       ${reform_exemptions[0] - baseline_exemptions[0]:,.0f}")
print(f"\n  Baseline RI Tax:        ${baseline_tax[0]:,.0f}")
print(f"  Reform RI Tax:          ${reform_tax[0]:,.0f}")
print(f"  Tax Change:             ${reform_tax[0] - baseline_tax[0]:,.0f}")
print(f"\n  Net Income Change:      ${reform_net_income[0] - baseline_net_income[0]:,.0f}")

# Verify the fix
print(f"\n{'='*60}")
if abs(baseline_exemptions[0] - reform_exemptions[0]) < 10:
    print("PASS: Personal exemptions correctly phase out in reform")
    print("  (Exemption change is ~$0, as expected)")
    print("\nThe fix is working correctly!")
else:
    print("FAIL: Personal exemptions NOT phasing out correctly")
    print(f"  Expected exemption change: ~$0")
    print(f"  Actual exemption change: ${reform_exemptions[0] - baseline_exemptions[0]:,.0f}")
    print("\nThe bug still exists!")

print(f"{'='*60}\n")
