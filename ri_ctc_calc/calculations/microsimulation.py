"""Microsimulation-based calculations using the Rhode Island dataset."""

from policyengine_us import Microsimulation
import pandas as pd
import numpy as np


def calculate_aggregate_impact(reform):
    """Calculate aggregate impact of RI CTC reform on Rhode Island population.

    Uses the Rhode Island microsimulation dataset to estimate statewide impact.

    Args:
        reform: PolicyEngine reform object

    Returns:
        dict: Aggregate impact statistics including:
            - total_cost: Total cost of the reform
            - beneficiaries: Number of households benefiting
            - avg_benefit: Average benefit among beneficiaries
            - children_affected: Number of children affected
            - by_income_bracket: Impact broken down by income brackets
    """
    # Load baseline and reform simulations
    # We need to look at NET INCOME change to capture both CTC and exemption effects
    sim_baseline = Microsimulation(dataset="hf://policyengine/test/RI.h5")
    sim_reform = Microsimulation(dataset="hf://policyengine/test/RI.h5", reform=reform)

    # Calculate household net income for both scenarios
    # This captures the total impact: CTC + tax savings from exemption changes
    net_income_baseline = sim_baseline.calculate("household_net_income", period=2026, map_to="household")
    net_income_reform = sim_reform.calculate("household_net_income", period=2026, map_to="household")

    # Calculate the benefit (increase in net income)
    # Map to tax_unit level for analysis
    net_income_change_household = net_income_reform - net_income_baseline

    # Map to tax unit for analysis (using reform sim to get mapping)
    tax_unit_id = sim_reform.calculate("tax_unit_id", period=2026, map_to="household")
    household_id = sim_reform.calculate("household_id", period=2026, map_to="household")

    # For simplicity, use household-level change as the benefit
    ctc_change = net_income_change_household

    # Get household-level data for analysis
    household_weight = sim_reform.calculate("household_weight", period=2026)
    agi = sim_reform.calculate("adjusted_gross_income", period=2026, map_to="household")

    # Calculate eligible children counts (map to household for consistency)
    eligible_children = sim_reform.calculate("ri_ctc_eligible_children", period=2026, map_to="household")

    # Aggregate statistics
    total_cost = ctc_change.sum()
    beneficiaries = (ctc_change > 0).sum()
    avg_benefit = ctc_change[ctc_change > 0].mean() if beneficiaries > 0 else 0
    children_affected = eligible_children[ctc_change > 0].sum() if beneficiaries > 0 else 0

    # Income bracket analysis
    income_brackets = [
        (0, 50000, "Under $50k"),
        (50000, 100000, "$50k-$100k"),
        (100000, 150000, "$100k-$150k"),
        (150000, 200000, "$150k-$200k"),
        (200000, float('inf'), "Over $200k")
    ]

    by_income_bracket = []
    for min_income, max_income, label in income_brackets:
        mask = (agi >= min_income) & (agi < max_income) & (ctc_change > 0)
        bracket_beneficiaries = mask.sum()
        bracket_cost = ctc_change[mask].sum()
        bracket_avg = ctc_change[mask].mean() if bracket_beneficiaries > 0 else 0

        by_income_bracket.append({
            "bracket": label,
            "beneficiaries": float(bracket_beneficiaries),
            "total_cost": float(bracket_cost),
            "avg_benefit": float(bracket_avg)
        })

    return {
        "total_cost": float(total_cost),
        "beneficiaries": float(beneficiaries),
        "avg_benefit": float(avg_benefit),
        "children_affected": float(children_affected),
        "by_income_bracket": by_income_bracket
    }


def get_dataset_summary():
    """Get summary statistics about the Rhode Island dataset.

    Returns:
        dict: Dataset summary including household counts, children counts, etc.
    """
    sim = Microsimulation(dataset="hf://policyengine/test/RI.h5")

    # Calculate basic counts
    household_count = sim.calculate("household_count", period=2026, map_to="household").sum()
    person_count = sim.calculate("person_count", period=2026, map_to="household").sum()

    # Get income statistics
    agi = sim.calculate("adjusted_gross_income", period=2026, map_to="household")

    # Get children statistics using pandas (per notebook example)
    df = pd.DataFrame({
        "household_id": sim.calculate("household_id", map_to="person"),
        "is_child": sim.calculate("is_child", period=2026, map_to="person"),
        "age": sim.calculate("age", map_to="person"),
        "person_weight": sim.calculate("person_weight", map_to="person")
    })

    # Count children
    total_children = sim.calculate("is_child", period=2026).sum()
    children_under_18_df = df[df['age'] < 18]

    # Count households with children
    children_per_household = df.groupby('household_id').agg({
        'is_child': 'sum',
        'person_weight': 'first'
    }).reset_index()

    total_households_with_children = children_per_household[
        children_per_household['is_child'] > 0
    ]['person_weight'].sum()

    return {
        "household_count": float(household_count),
        "person_count": float(person_count),
        "median_agi": float(agi.median()),
        "p75_agi": float(agi.quantile(0.75)),
        "p90_agi": float(agi.quantile(0.90)),
        "total_children": float(total_children),
        "households_with_children": float(total_households_with_children)
    }


def calculate_impact_by_household_type(reform):
    """Calculate reform impact broken down by household composition.

    Args:
        reform: PolicyEngine reform object

    Returns:
        dict: Impact statistics by household type
    """
    # Load baseline and reform simulations
    sim_baseline = Microsimulation(dataset="hf://policyengine/test/RI.h5")
    sim_reform = Microsimulation(dataset="hf://policyengine/test/RI.h5", reform=reform)

    # Calculate household net income change (captures CTC + exemption effects)
    net_income_baseline = sim_baseline.calculate("household_net_income", period=2026, map_to="household")
    net_income_reform = sim_reform.calculate("household_net_income", period=2026, map_to="household")
    ctc_change = net_income_reform - net_income_baseline

    # Get household composition data - work at household level
    df = pd.DataFrame({
        "household_id": sim_reform.calculate("household_id", map_to="person"),
        "is_child": sim_reform.calculate("is_child", period=2026, map_to="person"),
        "household_weight": sim_reform.calculate("household_weight", map_to="person")
    })

    # Count children per household
    children_per_hh = df.groupby('household_id').agg({
        'is_child': 'sum',
        'household_weight': 'first'
    }).reset_index()

    # Get household IDs in the same order as ctc_change
    household_ids = sim_reform.calculate("household_id", map_to="household")

    # Create a mapping from household_id to number of children
    hh_to_children = dict(zip(children_per_hh['household_id'], children_per_hh['is_child']))

    # Analyze by number of children
    household_types = [
        (1, "1 child"),
        (2, "2 children"),
        (3, "3+ children")
    ]

    by_household_type = []
    for num_children, label in household_types:
        # Create mask at household level
        if num_children == 3:
            # 3+ children
            mask = np.array([hh_to_children.get(hh_id, 0) >= num_children for hh_id in household_ids])
        else:
            mask = np.array([hh_to_children.get(hh_id, 0) == num_children for hh_id in household_ids])

        type_beneficiaries = mask.sum()
        if type_beneficiaries > 0:
            type_cost = ctc_change[mask].sum()
            type_avg = ctc_change[mask].mean()

            by_household_type.append({
                "type": label,
                "beneficiaries": float(type_beneficiaries),
                "total_cost": float(type_cost),
                "avg_benefit": float(type_avg)
            })

    return by_household_type
