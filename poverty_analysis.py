"""Analyze poverty impacts under Governor's proposal for 2026 vs 2027."""

from policyengine_us import Microsimulation
from policyengine_core.reforms import Reform
import numpy as np
import pandas as pd

def create_governors_proposal(year):
    """Create the Governor's proposal reform for a given year."""
    date_range = f"{year}-01-01.2100-12-31"

    return Reform.from_dict({
        # RI CTC parameters
        "gov.contrib.states.ri.ctc.in_effect": {date_range: True},
        "gov.contrib.states.ri.ctc.amount": {date_range: 325},
        "gov.contrib.states.ri.ctc.age_limit": {date_range: 19},
        "gov.contrib.states.ri.ctc.refundability.cap": {date_range: 100000},
        # Stepped phaseout
        "gov.contrib.states.ri.ctc.stepped_phaseout.threshold": {date_range: 261000},
        "gov.contrib.states.ri.ctc.stepped_phaseout.increment": {date_range: 7450},
        "gov.contrib.states.ri.ctc.stepped_phaseout.rate_per_step": {date_range: 0.20},
        # Dependent exemption zeroed
        "gov.contrib.states.ri.dependent_exemption.in_effect": {date_range: True},
        "gov.contrib.states.ri.dependent_exemption.amount": {date_range: 0},
        "gov.contrib.states.ri.dependent_exemption.age_limit.in_effect": {date_range: True},
        "gov.contrib.states.ri.dependent_exemption.age_limit.threshold": {date_range: 19},
    }, country_id="us")


def analyze_year(year):
    """Analyze poverty for a given year."""
    print(f"\n{'='*60}")
    print(f"YEAR: {year}")
    print(f"{'='*60}")

    # Load simulations
    print(f"Loading simulations for {year}...")
    sim_baseline = Microsimulation(dataset="hf://policyengine/policyengine-us-data/states/RI.h5")
    reform = create_governors_proposal(year)
    sim_reform = Microsimulation(dataset="hf://policyengine/policyengine-us-data/states/RI.h5", reform=reform)

    # Get person-level data
    person_id = np.arange(len(sim_baseline.calculate("age", period=year)))
    age = sim_baseline.calculate("age", period=year)
    is_child = sim_baseline.calculate("is_child", period=year)
    in_poverty_baseline = sim_baseline.calculate("person_in_poverty", period=year)
    in_poverty_reform = sim_reform.calculate("person_in_poverty", period=year)
    person_weight = sim_baseline.calculate("person_weight", period=year)
    household_id = sim_baseline.calculate("household_id", period=year, map_to="person")
    spm_unit_id = sim_baseline.calculate("spm_unit_id", period=year, map_to="person")

    # SPM resources and threshold
    spm_resources_baseline = sim_baseline.calculate("spm_unit_net_income", period=year, map_to="person")
    spm_resources_reform = sim_reform.calculate("spm_unit_net_income", period=year, map_to="person")
    spm_threshold = sim_baseline.calculate("spm_unit_spm_threshold", period=year, map_to="person")

    # CTC benefit (only exists in reform)
    try:
        ri_ctc_reform = sim_reform.calculate("ri_ctc", period=year, map_to="person")
    except:
        ri_ctc_reform = np.zeros(len(age))

    # Create person-level dataframe
    df = pd.DataFrame({
        "person_id": person_id,
        "age": age,
        "is_child": is_child,
        "household_id": household_id,
        "spm_unit_id": spm_unit_id,
        "in_poverty_baseline": in_poverty_baseline,
        "in_poverty_reform": in_poverty_reform,
        "spm_resources_baseline": spm_resources_baseline,
        "spm_resources_reform": spm_resources_reform,
        "spm_threshold": spm_threshold,
        "person_weight": person_weight,
        "ri_ctc_reform": ri_ctc_reform,
    })

    df["benefit"] = df["spm_resources_reform"] - df["spm_resources_baseline"]
    df["poverty_gap_baseline"] = df["spm_threshold"] - df["spm_resources_baseline"]

    # Aggregate to SPM unit level (poverty is measured at SPM unit)
    spm_df = df.groupby("spm_unit_id").agg({
        "in_poverty_baseline": "first",
        "in_poverty_reform": "first",
        "spm_resources_baseline": "first",
        "spm_resources_reform": "first",
        "spm_threshold": "first",
        "poverty_gap_baseline": "first",
        "benefit": "first",
        "is_child": "sum",  # Count children in SPM unit
        "ri_ctc_reform": "first",
        "person_weight": "first",
    }).reset_index()

    spm_df.rename(columns={"is_child": "num_children"}, inplace=True)
    spm_df["has_children"] = spm_df["num_children"] > 0

    # Count SPM units in poverty
    total_spm_units = len(spm_df)
    spm_in_poverty = spm_df[spm_df["in_poverty_baseline"]]
    spm_in_poverty_with_children = spm_df[(spm_df["in_poverty_baseline"]) & (spm_df["has_children"])]

    print(f"\n--- SPM UNIT COUNTS (UNWEIGHTED) ---")
    print(f"Total SPM units in dataset: {total_spm_units}")
    print(f"SPM units in poverty (baseline): {len(spm_in_poverty)}")
    print(f"SPM units in poverty WITH children: {len(spm_in_poverty_with_children)}")
    print(f"SPM units in poverty WITHOUT children: {len(spm_in_poverty) - len(spm_in_poverty_with_children)}")

    # Analyze benefit receipt among those in poverty
    poverty_with_benefit = spm_df[(spm_df["in_poverty_baseline"]) & (spm_df["benefit"] > 0)]
    poverty_with_children_and_benefit = spm_df[(spm_df["in_poverty_baseline"]) & (spm_df["has_children"]) & (spm_df["benefit"] > 0)]

    print(f"\n--- BENEFIT RECEIPT AMONG THOSE IN POVERTY ---")
    print(f"SPM units in poverty receiving ANY benefit: {len(poverty_with_benefit)}")
    print(f"SPM units in poverty with children receiving benefit: {len(poverty_with_children_and_benefit)}")

    # Transitions
    lifted_out = spm_df[(spm_df["in_poverty_baseline"]) & (~spm_df["in_poverty_reform"])]
    pushed_in = spm_df[(~spm_df["in_poverty_baseline"]) & (spm_df["in_poverty_reform"])]

    print(f"\n--- POVERTY TRANSITIONS (UNWEIGHTED SPM UNITS) ---")
    print(f"SPM units lifted OUT of poverty: {len(lifted_out)}")
    print(f"SPM units pushed INTO poverty: {len(pushed_in)}")

    # Analyze the lifted out
    if len(lifted_out) > 0:
        print(f"\n--- DETAILS OF SPM UNITS LIFTED OUT OF POVERTY ---")
        print(f"Avg children in lifted households: {lifted_out['num_children'].mean():.1f}")
        print(f"Avg benefit: ${lifted_out['benefit'].mean():.0f}")
        print(f"Avg poverty gap (before): ${lifted_out['poverty_gap_baseline'].mean():.0f}")

    # 10 closest to poverty line (in poverty, with children)
    print(f"\n--- 10 CLOSEST SPM UNITS TO POVERTY LINE (IN POVERTY, WITH CHILDREN) ---")
    closest = spm_in_poverty_with_children.sort_values("poverty_gap_baseline").head(10)

    print(f"\nSPM ID | Children | Threshold | Resources | Gap | Benefit | Still Poor?")
    print("-" * 80)
    for _, row in closest.iterrows():
        still_poor = "YES" if row["in_poverty_reform"] else "NO"
        print(f"{int(row['spm_unit_id']):>6} | {int(row['num_children']):>8} | ${row['spm_threshold']:>9,.0f} | ${row['spm_resources_baseline']:>9,.0f} | ${row['poverty_gap_baseline']:>5,.0f} | ${row['benefit']:>7,.0f} | {still_poor}")

    # Check why households with children aren't getting benefits
    poverty_children_no_benefit = spm_df[(spm_df["in_poverty_baseline"]) & (spm_df["has_children"]) & (spm_df["benefit"] <= 0)]
    print(f"\n--- SPM UNITS IN POVERTY WITH CHILDREN BUT NO BENEFIT: {len(poverty_children_no_benefit)} ---")

    if len(poverty_children_no_benefit) > 0:
        # Sample a few to understand why
        sample = poverty_children_no_benefit.head(5)
        print(f"Sample (first 5):")
        print(f"SPM ID | Children | Resources | RI CTC (reform)")
        print("-" * 50)
        for _, row in sample.iterrows():
            print(f"{int(row['spm_unit_id']):>6} | {int(row['num_children']):>8} | ${row['spm_resources_baseline']:>9,.0f} | ${row['ri_ctc_reform']:>7,.0f}")

    return {
        "year": year,
        "spm_in_poverty": len(spm_in_poverty),
        "spm_in_poverty_with_children": len(spm_in_poverty_with_children),
        "lifted_out": len(lifted_out),
        "poverty_with_benefit": len(poverty_with_benefit),
        "df": spm_df,
    }


if __name__ == "__main__":
    results_2026 = analyze_year(2026)
    results_2027 = analyze_year(2027)

    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(f"\n{'Metric':<45} {'2026':>10} {'2027':>10}")
    print("-" * 65)
    print(f"{'SPM units in poverty':<45} {results_2026['spm_in_poverty']:>10} {results_2027['spm_in_poverty']:>10}")
    print(f"{'SPM units in poverty WITH children':<45} {results_2026['spm_in_poverty_with_children']:>10} {results_2027['spm_in_poverty_with_children']:>10}")
    print(f"{'SPM units in poverty receiving benefit':<45} {results_2026['poverty_with_benefit']:>10} {results_2027['poverty_with_benefit']:>10}")
    print(f"{'SPM units lifted out of poverty':<45} {results_2026['lifted_out']:>10} {results_2027['lifted_out']:>10}")

    # Compare the same SPM units across years
    print(f"\n{'='*60}")
    print("SAME HOUSEHOLD COMPARISON")
    print(f"{'='*60}")

    df_2026 = results_2026["df"]
    df_2027 = results_2027["df"]

    # Merge on SPM unit ID
    merged = df_2026.merge(df_2027, on="spm_unit_id", suffixes=("_2026", "_2027"))

    # Households in poverty in 2026 but not 2027 (baseline)
    in_poverty_2026_only = merged[(merged["in_poverty_baseline_2026"]) & (~merged["in_poverty_baseline_2027"])]
    in_poverty_2027_only = merged[(~merged["in_poverty_baseline_2026"]) & (merged["in_poverty_baseline_2027"])]
    in_poverty_both = merged[(merged["in_poverty_baseline_2026"]) & (merged["in_poverty_baseline_2027"])]

    print(f"\nBaseline poverty status changes (same households):")
    print(f"  In poverty 2026 only (exited by 2027 baseline): {len(in_poverty_2026_only)}")
    print(f"  In poverty 2027 only (entered by 2027 baseline): {len(in_poverty_2027_only)}")
    print(f"  In poverty both years: {len(in_poverty_both)}")

    # Among those in poverty both years with children, compare benefits
    both_poverty_children = merged[
        (merged["in_poverty_baseline_2026"]) &
        (merged["in_poverty_baseline_2027"]) &
        (merged["has_children_2026"])
    ]

    print(f"\n  SPM units in poverty both years WITH children: {len(both_poverty_children)}")
    if len(both_poverty_children) > 0:
        print(f"  Avg benefit 2026: ${both_poverty_children['benefit_2026'].mean():.0f}")
        print(f"  Avg benefit 2027: ${both_poverty_children['benefit_2027'].mean():.0f}")

        # How many get benefit in each year?
        gets_benefit_2026 = (both_poverty_children["benefit_2026"] > 0).sum()
        gets_benefit_2027 = (both_poverty_children["benefit_2027"] > 0).sum()
        print(f"  Getting benefit in 2026: {gets_benefit_2026}")
        print(f"  Getting benefit in 2027: {gets_benefit_2027}")

        # Sample households with benefit in 2026 but not 2027
        benefit_2026_not_2027 = both_poverty_children[
            (both_poverty_children["benefit_2026"] > 0) &
            (both_poverty_children["benefit_2027"] <= 0)
        ]
        print(f"\n  Households with benefit in 2026 but NOT 2027: {len(benefit_2026_not_2027)}")

        if len(benefit_2026_not_2027) > 0:
            print(f"\n  Sample of these households:")
            print(f"  SPM ID | Children 2026 | Children 2027 | Benefit 2026 | Benefit 2027")
            print("  " + "-" * 70)
            for _, row in benefit_2026_not_2027.head(10).iterrows():
                print(f"  {int(row['spm_unit_id']):>6} | {int(row['num_children_2026']):>13} | {int(row['num_children_2027']):>13} | ${row['benefit_2026']:>11,.0f} | ${row['benefit_2027']:>11,.0f}")
