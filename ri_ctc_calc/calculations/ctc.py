"""Rhode Island Child Tax Credit calculation functions."""

import copy
from policyengine_us import Simulation

from ri_ctc_calc.calculations.household import build_household_situation
from ri_ctc_calc.calculations.reforms import create_ri_ctc_reform


def calculate_ri_ctc(
    age_head,
    age_spouse,
    income,
    dependent_ages,
    use_reform=False,
):
    """Calculate RI CTC for baseline or reform scenario.

    Args:
        age_head: Age of head of household
        age_spouse: Age of spouse (None if not married)
        income: Annual household income
        dependent_ages: List of dependent ages
        use_reform: If True, use RI CTC reform

    Returns:
        tuple: (ri_ctc, household_tax_before_refundable_credits, agi)
    """
    try:
        # Build base household situation
        situation = build_household_situation(
            age_head=age_head,
            age_spouse=age_spouse,
            dependent_ages=dependent_ages,
            year=2026,
            with_axes=False,
        )

        # Deep copy and inject income
        sit = copy.deepcopy(situation)

        # Set AGI at tax unit level (no need to split for married couples)
        sit["tax_units"]["your tax unit"]["adjusted_gross_income"] = {2026: income}

        # Create reform if requested
        reform = create_ri_ctc_reform() if use_reform else None

        # Run simulation
        sim = Simulation(situation=sit, reform=reform)

        # Get RI CTC amount
        ri_ctc = sim.calculate("ri_ctc", map_to="tax_unit", period=2026)[0]

        # Get household tax before refundable credits to understand impact
        household_tax = sim.calculate(
            "household_tax_before_refundable_credits",
            map_to="household",
            period=2026
        )[0]

        # Get AGI for reference
        agi = sim.calculate("adjusted_gross_income", map_to="tax_unit", period=2026)[0]

        return float(max(0, ri_ctc)), float(household_tax), float(agi)

    except Exception as e:
        raise Exception(f"RI CTC calculation error: {str(e)}") from e
