"""Calculator service wrapping existing RI CTC calculation logic."""

import sys
from pathlib import Path
import numpy as np
from policyengine_us import Simulation

# Add parent directory to path to import ri_ctc_calc
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from ri_ctc_calc.calculations.household import build_household_situation
from ri_ctc_calc.calculations.reforms import create_custom_reform
from ri_ctc_calc.calculations.microsimulation import (
    calculate_aggregate_impact,
    get_dataset_summary,
)

from app.api.models.responses import (
    HouseholdImpactResponse,
    BenefitAtIncome,
    AggregateImpactResponse,
    DatasetSummary,
)


def calculate_range_based_rate(
    dependent_ages: list[int],
    reform_params: dict,
) -> dict:
    """
    Calculate the effective phaseout rate for range-based phaseout.

    For range-based phaseout, the rate is calculated as:
    rate = max_credit / (phaseout_end - phaseout_start)

    This means households with more children see faster phaseout per dollar
    of income since their total credit is larger but the range is fixed.

    Returns a modified copy of reform_params with the calculated rate.
    """
    params = reform_params.copy()

    # Only calculate if range-based phaseout is enabled
    if not params.get("ctc_phaseout_range_based", False):
        return params

    phaseout_end = params.get("ctc_phaseout_end", 0)
    # Use the first threshold as the start (they should all be the same for range-based)
    thresholds = params.get("ctc_phaseout_thresholds", {})
    phaseout_start = thresholds.get("SINGLE", 0) or thresholds.get("JOINT", 0) or 0

    # Need valid range
    if phaseout_end <= phaseout_start:
        return params

    # Count eligible children
    ctc_age_limit = params.get("ctc_age_limit", 18)
    eligible_children = sum(1 for age in dependent_ages if age < ctc_age_limit)

    # Count young children for boost
    young_child_age_limit = params.get("ctc_young_child_boost_age_limit", 6)
    young_children = sum(
        1 for age in dependent_ages
        if age < young_child_age_limit and age < ctc_age_limit
    )

    # Calculate maximum credit
    ctc_amount = params.get("ctc_amount", 1000)
    boost_amount = params.get("ctc_young_child_boost_amount", 0)
    max_credit = (eligible_children * ctc_amount) + (young_children * boost_amount)

    # Calculate effective rate
    if max_credit > 0:
        rate = max_credit / (phaseout_end - phaseout_start)
        params["ctc_phaseout_rate"] = rate

    return params


async def calculate_household_benefit_quick(
    age_head: int,
    age_spouse: int | None,
    dependent_ages: list[int],
    income: int,
    reform_params: dict,
) -> BenefitAtIncome:
    """
    Quick calculation of benefit at specific AGI level only (no income sweep).
    Much faster than full calculation.

    Args:
        income: Adjusted Gross Income (AGI) for the household
    """
    # Build household situation WITHOUT axes (single income point)
    household = build_household_situation(
        age_head=age_head,
        age_spouse=age_spouse,
        dependent_ages=dependent_ages,
        year=2026,
        with_axes=False,  # No income sweep for quick calculation
    )

    # Set AGI on the tax unit level
    household["tax_units"]["your tax unit"]["adjusted_gross_income"] = {"2026": income}

    # Calculate range-based rate if enabled
    effective_params = calculate_range_based_rate(dependent_ages, reform_params)

    # Create reform
    reform = create_custom_reform(**effective_params)

    # Create simulations (single point, no sweep)
    sim_baseline = Simulation(situation=household)
    sim_reform = Simulation(situation=household, reform=reform)

    # Calculate net income
    net_income_baseline = sim_baseline.calculate(
        "household_net_income", map_to="household", period=2026
    )[0]
    net_income_reform = sim_reform.calculate(
        "household_net_income", map_to="household", period=2026
    )[0]

    difference = float(net_income_reform - net_income_baseline)

    # Calculate components if there's a benefit
    ctc_amt = 0.0
    exemption_benefit = 0.0

    if difference > 0:
        # Exemption-only simulation
        exemption_only_reform = create_custom_reform(
            ctc_amount=0,
            enable_exemption_reform=reform_params.get("enable_exemption_reform", False),
            exemption_amount=reform_params.get("exemption_amount", 5200),
            exemption_age_limit_enabled=reform_params.get("exemption_age_limit_enabled", True),
            exemption_age_threshold=reform_params.get("exemption_age_threshold", 18),
            exemption_phaseout_rate=reform_params.get("exemption_phaseout_rate", 0),
            exemption_phaseout_thresholds=reform_params.get("exemption_phaseout_thresholds", None),
        )
        sim_exemption_only = Simulation(situation=household, reform=exemption_only_reform)
        net_income_exemption_only = sim_exemption_only.calculate(
            "household_net_income", map_to="household", period=2026
        )[0]

        exemption_benefit = float(net_income_exemption_only - net_income_baseline)
        ctc_amt = difference - exemption_benefit

    return BenefitAtIncome(
        baseline=float(net_income_baseline),
        reform=float(net_income_reform),
        difference=difference,
        ctc_component=ctc_amt,
        exemption_tax_benefit=exemption_benefit,
    )


async def calculate_household_impact(
    age_head: int,
    age_spouse: int | None,
    dependent_ages: list[int],
    income: int,
    reform_params: dict,
) -> HouseholdImpactResponse:
    """
    Calculate household impact with income sweep.

    This replicates the create_chart() function from the Streamlit app.

    Args:
        income: Adjusted Gross Income (AGI) - used to identify the household's position on charts
    """
    # Build household situation with axes for income sweep
    base_household = build_household_situation(
        age_head=age_head,
        age_spouse=age_spouse,
        dependent_ages=dependent_ages,
        year=2026,
        with_axes=True,
    )

    # Calculate range-based rate if enabled
    effective_params = calculate_range_based_rate(dependent_ages, reform_params)

    # Create reform with custom parameters
    reform = create_custom_reform(**effective_params)

    # Create simulations
    sim_baseline = Simulation(situation=base_household)
    sim_reform = Simulation(situation=base_household, reform=reform)

    # Get AGI range
    income_range = sim_baseline.calculate(
        "adjusted_gross_income", map_to="tax_unit", period=2026
    )

    # Calculate net income for both scenarios
    net_income_baseline = sim_baseline.calculate(
        "household_net_income", map_to="household", period=2026
    )
    net_income_reform = sim_reform.calculate(
        "household_net_income", map_to="household", period=2026
    )

    # Calculate benefits
    ctc_range_baseline = np.zeros(len(income_range))
    ctc_range_reform = net_income_reform - net_income_baseline

    # Calculate component breakdown only if exemption reform is enabled
    if reform_params.get("enable_exemption_reform", False):
        # Create exemption-only reform to isolate components
        exemption_only_reform = create_custom_reform(
            ctc_amount=0,  # No CTC
            enable_exemption_reform=True,
            exemption_amount=reform_params.get("exemption_amount", 5200),
            exemption_age_limit_enabled=reform_params.get("exemption_age_limit_enabled", True),
            exemption_age_threshold=reform_params.get("exemption_age_threshold", 18),
            exemption_phaseout_rate=reform_params.get("exemption_phaseout_rate", 0),
            exemption_phaseout_thresholds=reform_params.get("exemption_phaseout_thresholds", None),
        )
        sim_exemption_only = Simulation(situation=base_household, reform=exemption_only_reform)
        net_income_exemption_only = sim_exemption_only.calculate(
            "household_net_income", map_to="household", period=2026
        )

        # Isolate components
        exemption_tax_benefit = net_income_exemption_only - net_income_baseline
        ctc_component = ctc_range_reform - exemption_tax_benefit
    else:
        # No exemption reform - all benefit is from CTC
        exemption_tax_benefit = np.zeros(len(income_range))
        ctc_component = ctc_range_reform

    # Fixed x-axis max at $500k for household calculator
    x_axis_max = 500000

    # Interpolate values at user's income
    # With 10,001 points, interpolation is highly accurate (~$100 step size)
    ctc_baseline = float(np.interp(income, income_range, ctc_range_baseline))
    ctc_reform = float(np.interp(income, income_range, ctc_range_reform))
    difference = ctc_reform - ctc_baseline
    ctc_amt = float(np.interp(income, income_range, ctc_component))
    exemption_benefit = float(np.interp(income, income_range, exemption_tax_benefit))

    return HouseholdImpactResponse(
        income_range=income_range.tolist(),
        ctc_baseline_range=ctc_range_baseline.tolist(),
        ctc_reform_range=ctc_range_reform.tolist(),
        ctc_component=ctc_component.tolist(),
        exemption_tax_benefit=exemption_tax_benefit.tolist(),
        benefit_at_income=BenefitAtIncome(
            baseline=ctc_baseline,
            reform=ctc_reform,
            difference=difference,
            ctc_component=ctc_amt,
            exemption_tax_benefit=exemption_benefit,
        ),
        x_axis_max=float(x_axis_max),
    )


async def calculate_aggregate(reform_params: dict) -> AggregateImpactResponse:
    """
    Calculate aggregate/statewide impact using microsimulation.

    This wraps the existing calculate_aggregate_impact() function.
    """
    reform = create_custom_reform(**reform_params)
    impact = calculate_aggregate_impact(reform)

    return AggregateImpactResponse(**impact)


async def get_dataset_info() -> DatasetSummary:
    """Get RI dataset summary statistics."""
    summary = get_dataset_summary()
    return DatasetSummary(**summary)
