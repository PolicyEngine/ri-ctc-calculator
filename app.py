"""
Rhode Island Child Tax Credit Calculator
==========================================
Explore how the Rhode Island CTC reform would affect your household.

This app calculates Rhode Island CTC under two scenarios:
1. Current law: No RI CTC
2. Reform: RI CTC enabled

Uses PolicyEngine US for accurate tax-benefit microsimulation.
"""

import streamlit as st

try:
    import pandas as pd
    import numpy as np
    import gc
    from policyengine_us import Simulation
    import plotly.graph_objects as go

    # Import calculation functions from package
    from ri_ctc_calc.calculations.ctc import calculate_ri_ctc
    from ri_ctc_calc.calculations.household import build_household_situation
    from ri_ctc_calc.calculations.reforms import (
        create_ri_ctc_reform,
        create_custom_reform,
    )
    from ri_ctc_calc.calculations.microsimulation import (
        calculate_aggregate_impact,
        get_dataset_summary,
        calculate_impact_by_household_type,
    )

    # Try to import reform capability
    try:
        from policyengine_core.reforms import Reform
        REFORM_AVAILABLE = True
    except ImportError:
        REFORM_AVAILABLE = False

    st.set_page_config(
        page_title="Rhode Island CTC Calculator",
        layout="wide",
        initial_sidebar_state="expanded",
    )

except Exception as e:
    st.error(f"Startup Error: {str(e)}")
    st.error("Please report this error with the details above.")
    import traceback
    st.code(traceback.format_exc())
    st.stop()


# PolicyEngine brand colors
COLORS = {
    "primary": "#2C6496",  # Blue for reform
    "secondary": "#39C6C0",
    "green": "#28A745",
    "gray": "#BDBDBD",  # Medium light gray for baseline
    "blue_gradient": ["#D1E5F0", "#92C5DE", "#2166AC", "#053061"],
}


def main():
    # Header
    st.markdown(
        f"""
        <style>
        .stApp {{
            font-family: 'Roboto', 'Helvetica', 'Arial', sans-serif;
        }}
        h1 {{
            color: {COLORS["primary"]};
            font-weight: 600;
        }}
        .subtitle {{
            color: #666;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }}
        </style>
    """,
        unsafe_allow_html=True,
    )

    st.title("How would Rhode Island CTC affect you?")

    # Sidebar for household configuration
    with st.sidebar:
        st.header("Household configuration")

        # Income input
        income_input = st.number_input(
            "Annual household income",
            min_value=0,
            max_value=1000000,
            value=50000,
            step=1000,
            help="Your total annual household income (AGI). This will be used in the 'Your impact' tab and to highlight your position on the charts."
        )

        married = st.checkbox("Are you married?", value=False)

        age_head = st.number_input(
            "How old are you?", min_value=18, max_value=100, value=35
        )

        if married:
            age_spouse = st.number_input(
                "How old is your spouse?",
                min_value=18,
                max_value=100,
                value=35,
            )
        else:
            age_spouse = None

        num_dependents = st.number_input(
            "How many children or dependents do you have?",
            min_value=0,
            max_value=10,
            value=1,
        )
        dependent_ages = []

        if num_dependents > 0:
            st.write("What are their ages?")
            for i in range(num_dependents):
                age_dep = st.number_input(
                    f"Child {i+1} age",
                    min_value=0,
                    max_value=25,
                    value=5,
                    key=f"dep_{i}",
                )
                dependent_ages.append(age_dep)

        st.markdown("---")

        # Reform parameter customization
        st.header("Reform Parameters")

        with st.expander("⚙️ Customize RI CTC", expanded=False):
            ctc_amount = st.number_input(
                "CTC Amount per Child",
                min_value=0,
                max_value=10000,
                value=1000,
                step=100,
                help="Credit amount per eligible child"
            )

            ctc_age_limit = st.number_input(
                "Age Limit",
                min_value=0,
                max_value=26,
                value=18,
                help="Maximum age for CTC eligibility"
            )

            refund_option = st.radio(
                "Refundability",
                options=["Non-refundable", "Partially refundable", "Fully refundable"],
                index=0,
                help="Non-refundable: Can only reduce tax to zero. Partially/Fully: Can result in refund"
            )

            if refund_option == "Fully refundable":
                ctc_refundability_cap = ctc_amount  # Cap equals amount = fully refundable
            elif refund_option == "Partially refundable":
                ctc_refundability_cap = st.number_input(
                    "Refundable Amount Cap",
                    min_value=0,
                    max_value=int(ctc_amount),
                    value=int(ctc_amount // 2),
                    step=100,
                    help="Maximum refundable portion of the credit"
                )
            else:  # Non-refundable
                ctc_refundability_cap = 0

            enable_phaseout = st.checkbox("Enable Income Phase-out", value=False)

            if enable_phaseout:
                ctc_phaseout_rate = st.slider(
                    "Phase-out Rate",
                    min_value=0.0,
                    max_value=0.20,
                    value=0.05,
                    step=0.01,
                    format="%.2f",
                    help="Rate at which credit phases out per dollar of AGI above threshold"
                )

                st.markdown("**Phase-out Thresholds by Filing Status**")
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    phaseout_single = st.number_input(
                        "Single",
                        min_value=0,
                        max_value=1000000,
                        value=75000,
                        step=5000,
                        key="phaseout_single"
                    )
                    phaseout_hoh = st.number_input(
                        "Head of Household",
                        min_value=0,
                        max_value=1000000,
                        value=112500,
                        step=5000,
                        key="phaseout_hoh"
                    )
                with col_p2:
                    phaseout_joint = st.number_input(
                        "Married Filing Jointly",
                        min_value=0,
                        max_value=1000000,
                        value=150000,
                        step=5000,
                        key="phaseout_joint"
                    )
                    phaseout_separate = st.number_input(
                        "Married Filing Separately",
                        min_value=0,
                        max_value=1000000,
                        value=75000,
                        step=5000,
                        key="phaseout_separate"
                    )

                ctc_phaseout_thresholds = {
                    "SINGLE": phaseout_single,
                    "JOINT": phaseout_joint,
                    "HEAD_OF_HOUSEHOLD": phaseout_hoh,
                    "SURVIVING_SPOUSE": phaseout_joint,
                    "SEPARATE": phaseout_separate,
                }
            else:
                ctc_phaseout_rate = 0
                ctc_phaseout_thresholds = {
                    "SINGLE": 0,
                    "JOINT": 0,
                    "HEAD_OF_HOUSEHOLD": 0,
                    "SURVIVING_SPOUSE": 0,
                    "SEPARATE": 0,
                }

        with st.expander("⚙️ Customize Dependent Exemption", expanded=False):
            enable_exemption_reform = st.checkbox(
                "Enable Dependent Exemption Reform",
                value=True,
                help="Modify dependent exemption rules"
            )

            if enable_exemption_reform:
                exemption_amount = st.number_input(
                    "Exemption Amount",
                    min_value=0,
                    max_value=20000,
                    value=5100,
                    step=100,
                    help="Dependent exemption amount per dependent"
                )

                exemption_age_limit_enabled = st.checkbox(
                    "Restrict to Children Under Age Limit",
                    value=True
                )

                if exemption_age_limit_enabled:
                    exemption_age_threshold = st.number_input(
                        "Age Threshold",
                        min_value=0,
                        max_value=26,
                        value=18,
                        help="Dependents must be under this age"
                    )
                else:
                    exemption_age_threshold = 18  # Default, won't be used

                enable_exemption_phaseout = st.checkbox(
                    "Enable Exemption Phase-out",
                    value=False
                )

                if enable_exemption_phaseout:
                    exemption_phaseout_rate = st.slider(
                        "Exemption Phase-out Rate",
                        min_value=0.0,
                        max_value=0.20,
                        value=0.05,
                        step=0.01,
                        format="%.2f"
                    )

                    st.markdown("**Exemption Phase-out Thresholds**")
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        exemption_phaseout_single = st.number_input(
                            "Single",
                            min_value=0,
                            max_value=1000000,
                            value=100000,
                            step=5000,
                            key="exemption_phaseout_single"
                        )
                        exemption_phaseout_hoh = st.number_input(
                            "Head of Household",
                            min_value=0,
                            max_value=1000000,
                            value=150000,
                            step=5000,
                            key="exemption_phaseout_hoh"
                        )
                    with col_e2:
                        exemption_phaseout_joint = st.number_input(
                            "Married Filing Jointly",
                            min_value=0,
                            max_value=1000000,
                            value=200000,
                            step=5000,
                            key="exemption_phaseout_joint"
                        )
                        exemption_phaseout_separate = st.number_input(
                            "Married Filing Separately",
                            min_value=0,
                            max_value=1000000,
                            value=100000,
                            step=5000,
                            key="exemption_phaseout_separate"
                        )

                    exemption_phaseout_thresholds = {
                        "SINGLE": exemption_phaseout_single,
                        "JOINT": exemption_phaseout_joint,
                        "HEAD_OF_HOUSEHOLD": exemption_phaseout_hoh,
                        "SURVIVING_SPOUSE": exemption_phaseout_joint,
                        "SEPARATE": exemption_phaseout_separate,
                    }
                else:
                    exemption_phaseout_rate = 0
                    exemption_phaseout_thresholds = None
            else:
                exemption_amount = 5100
                exemption_age_limit_enabled = False
                exemption_age_threshold = 18
                exemption_phaseout_rate = 0
                exemption_phaseout_thresholds = None

        st.markdown("---")

        calculate_button = st.button(
            "Analyze RI CTC impact",
            type="primary",
            use_container_width=True,
        )

        if calculate_button:
            st.session_state.calculate = True
            new_params = {
                "age_head": age_head,
                "age_spouse": age_spouse,
                "dependent_ages": dependent_ages,
                "married": married,
                "income": income_input,
            }
            new_reform_params = {
                "ctc_amount": ctc_amount,
                "ctc_age_limit": ctc_age_limit,
                "ctc_refundability_cap": ctc_refundability_cap,
                "ctc_phaseout_rate": ctc_phaseout_rate,
                "ctc_phaseout_thresholds": ctc_phaseout_thresholds,
                "enable_exemption_reform": enable_exemption_reform,
                "exemption_amount": exemption_amount,
                "exemption_age_limit_enabled": exemption_age_limit_enabled,
                "exemption_age_threshold": exemption_age_threshold,
                "exemption_phaseout_rate": exemption_phaseout_rate,
                "exemption_phaseout_thresholds": exemption_phaseout_thresholds,
            }
            # Clear cached charts if params changed
            if (hasattr(st.session_state, "params") and st.session_state.params != new_params) or \
               (hasattr(st.session_state, "reform_params") and st.session_state.reform_params != new_reform_params):
                st.session_state.income_range = None
                st.session_state.fig_comparison = None
                st.session_state.fig_delta = None
                st.session_state.aggregate_impact = None  # Clear aggregate impact too
            st.session_state.params = new_params
            st.session_state.reform_params = new_reform_params

    # Main content area
    if not hasattr(st.session_state, "calculate") or not st.session_state.calculate:
        # Show instructional text when first loading
        st.markdown(
            """
            ### Get started

            Enter your household information in the sidebar, then click **"Analyze RI CTC impact"** to see:

            - How the Rhode Island Child Tax Credit would benefit your household
            - The income range where you would receive the credit
            - Your specific benefit at any income level you choose

            The analysis compares two scenarios:
            - **Current law**: No Rhode Island CTC
            - **Reform**: Rhode Island CTC enabled
            """
        )
    else:
        params = st.session_state.params

        # Generate charts only if not already in session state
        if not hasattr(st.session_state, "income_range") or st.session_state.income_range is None:
            with st.spinner("Generating analysis..."):
                (
                    fig_comparison,
                    fig_delta,
                    benefit_info,
                    income_range,
                    ctc_baseline_range,
                    ctc_reform_range,
                    x_axis_max,
                    ri_exemptions_baseline,
                    ri_exemptions_reform,
                    exemption_change,
                    ri_tax_baseline,
                    ri_tax_reform,
                    tax_change,
                ) = create_chart(
                    params["age_head"],
                    params["age_spouse"],
                    tuple(params["dependent_ages"]),
                    st.session_state.reform_params,
                )

                # Store arrays and charts in session state
                if income_range is not None:
                    st.session_state.income_range = income_range
                    st.session_state.ctc_baseline_range = ctc_baseline_range
                    st.session_state.ctc_reform_range = ctc_reform_range
                    st.session_state.benefit_info = benefit_info
                    st.session_state.fig_comparison = fig_comparison
                    st.session_state.fig_delta = fig_delta
                    st.session_state.x_axis_max = x_axis_max
                    # Store diagnostic data
                    st.session_state.ri_exemptions_baseline = ri_exemptions_baseline
                    st.session_state.ri_exemptions_reform = ri_exemptions_reform
                    st.session_state.exemption_change = exemption_change
                    st.session_state.ri_tax_baseline = ri_tax_baseline
                    st.session_state.ri_tax_reform = ri_tax_reform
                    st.session_state.tax_change = tax_change

        # Show tabs using cached charts
        if hasattr(st.session_state, "fig_delta") and st.session_state.fig_delta is not None:
            tab1, tab2, tab3, tab4 = st.tabs([
                "Benefit from reform",
                "Baseline vs. reform",
                "Your impact",
                "Statewide impact"
            ])

            with tab1:
                st.plotly_chart(
                    st.session_state.fig_delta,
                    use_container_width=True,
                    config={"displayModeBar": False},
                    key="benefit_chart",
                )

            with tab2:
                st.plotly_chart(
                    st.session_state.fig_comparison,
                    use_container_width=True,
                    config={"displayModeBar": False},
                    key="comparison_chart",
                )

            with tab3:
                st.markdown("### Your Personal Impact")
                st.markdown(f"Based on your household income of **${params['income']:,}**")

                # Allow user to override the income
                user_income = st.number_input(
                    "Adjust income (optional):",
                    min_value=0,
                    value=params['income'],
                    step=1000,
                    help="Adjusted Gross Income (AGI). Defaults to the value you entered in the sidebar.",
                    format="%d",
                    key="user_income_override"
                )

                # Interpolate values at user's income
                if (
                    hasattr(st.session_state, "income_range")
                    and user_income is not None
                    and user_income > 0
                ):
                    ctc_baseline = np.interp(
                        user_income,
                        st.session_state.income_range,
                        st.session_state.ctc_baseline_range,
                    )
                    ctc_reform = np.interp(
                        user_income,
                        st.session_state.income_range,
                        st.session_state.ctc_reform_range,
                    )
                    difference = ctc_reform - ctc_baseline

                    # Display metrics
                    st.markdown(
                        """
                    <style>
                    [data-testid="stMetricValue"] {
                        font-size: 1.4rem !important;
                        white-space: nowrap !important;
                        overflow: visible !important;
                        line-height: 1.3 !important;
                    }
                    [data-testid="stMetricLabel"] {
                        font-size: 0.95rem !important;
                        line-height: 1.2 !important;
                    }
                    </style>
                    """,
                        unsafe_allow_html=True,
                    )

                    col_baseline, col_reform, col_diff = st.columns(3)

                    with col_baseline:
                        st.metric(
                            "Current law",
                            f"${ctc_baseline:,.0f}",
                            help="Your benefit under current law (none - no RI CTC exists)",
                        )

                    with col_reform:
                        st.metric(
                            "With reform",
                            f"${ctc_reform:,.0f}",
                            help="Your total annual benefit (CTC + tax savings from exemption changes)",
                        )

                    with col_diff:
                        if difference > 0:
                            st.metric(
                                "Net income increase",
                                f"${difference:,.0f} per year",
                                delta_color="normal",
                                help="How much more money in your pocket each year"
                            )
                        else:
                            st.metric("No change", "$0")

                    # Diagnostic breakdown
                    with st.expander("🔍 Detailed breakdown (for debugging)"):
                        # Find the index closest to user's income
                        income_idx = np.argmin(np.abs(st.session_state.income_range - user_income))

                        st.markdown("**Tax component analysis:**")
                        st.write(f"- **Baseline RI exemptions:** ${st.session_state.ri_exemptions_baseline[income_idx]:,.0f}")
                        st.write(f"- **Reform RI exemptions:** ${st.session_state.ri_exemptions_reform[income_idx]:,.0f}")
                        st.write(f"- **Exemption change:** ${st.session_state.exemption_change[income_idx]:,.0f}")
                        st.write("")
                        st.write(f"- **Baseline RI tax:** ${st.session_state.ri_tax_baseline[income_idx]:,.0f}")
                        st.write(f"- **Reform RI tax:** ${st.session_state.ri_tax_reform[income_idx]:,.0f}")
                        st.write(f"- **Tax change:** ${st.session_state.tax_change[income_idx]:,.0f} {'(increase)' if st.session_state.tax_change[income_idx] > 0 else '(decrease)'}")
                        st.write("")
                        st.write(f"- **Net income change:** ${difference:,.0f}")

                        st.markdown("**Expected behavior:**")
                        st.write("- If exemptions decrease → tax increases → net income decreases")
                        st.write("- If exemptions increase → tax decreases → net income increases")
                        st.write("- If CTC increases → net income increases (via credits)")

                    # Details
                    with st.expander("See calculation details"):
                        household_size = (
                            1
                            + (1 if params["age_spouse"] else 0)
                            + len(params["dependent_ages"])
                        )
                        eligible_children = sum(
                            1 for age in params["dependent_ages"] if age < 18
                        )

                        st.write(
                            f"""
                        ### Your household
                        - **Size:** {household_size} people
                        - **Eligible children (under 18):** {eligible_children}
                        - **Income (AGI):** ${user_income:,}
                        - **State:** Rhode Island

                        ### How Rhode Island CTC works

                        The Rhode Island Child Tax Credit provides tax relief for families with children under age 18.

                        **Key features:**
                        - **Non-refundable**: Can reduce your RI tax liability to zero, but not below
                        - **Age limit**: Children must be under 18
                        - **Phase-out**: Credit may be reduced at higher incomes based on AGI
                        - **RI residents**: Must be a Rhode Island resident to claim

                        **Note**: This is a non-refundable credit, meaning it can only reduce your Rhode Island tax liability. If you have no RI tax liability, you would not benefit from this credit.
                        """
                        )

            with tab4:
                st.markdown("### Statewide Impact Analysis")
                st.markdown(
                    """
                    This analysis uses the Rhode Island microsimulation dataset to estimate
                    the aggregate impact of the RI CTC reform across all Rhode Island households.
                    """
                )

                # Calculate aggregate impact (cached)
                if not hasattr(st.session_state, "aggregate_impact") or st.session_state.aggregate_impact is None:
                    with st.spinner("Calculating statewide impact..."):
                        reform = create_custom_reform(**st.session_state.reform_params)
                        st.session_state.aggregate_impact = calculate_aggregate_impact(reform)
                        st.session_state.dataset_summary = get_dataset_summary()
                        st.session_state.impact_by_household_type = calculate_impact_by_household_type(reform)

                impact = st.session_state.aggregate_impact
                dataset = st.session_state.dataset_summary

                # Display key metrics
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Total Cost",
                        f"${impact['total_cost'] / 1e6:.1f}M",
                        help="Total annual cost of the reform across all Rhode Island households"
                    )

                with col2:
                    st.metric(
                        "Households Benefiting",
                        f"{impact['beneficiaries']:,.0f}",
                        help="Number of Rhode Island households that would benefit from the reform"
                    )

                with col3:
                    st.metric(
                        "Average Benefit",
                        f"${impact['avg_benefit']:,.0f}",
                        help="Average annual benefit among households that receive the credit"
                    )

                st.markdown("---")

                # Impact by income bracket
                st.markdown("#### Impact by Income Bracket")

                bracket_df = pd.DataFrame(impact['by_income_bracket'])
                if len(bracket_df) > 0:
                    # Create visualization
                    fig_brackets = go.Figure()

                    fig_brackets.add_trace(
                        go.Bar(
                            x=bracket_df['bracket'],
                            y=bracket_df['avg_benefit'],
                            name="Average Benefit",
                            marker_color=COLORS["primary"],
                            text=bracket_df['avg_benefit'].apply(lambda x: f"${x:,.0f}"),
                            textposition="outside",
                        )
                    )

                    fig_brackets.update_layout(
                        title="Average Benefit by Income Bracket",
                        xaxis_title="Annual Income",
                        yaxis_title="Average Annual Benefit",
                        yaxis=dict(tickformat="$,.0f"),
                        height=400,
                        showlegend=False,
                    )

                    st.plotly_chart(fig_brackets, use_container_width=True)

                    # Show detailed table
                    with st.expander("View detailed breakdown"):
                        display_df = bracket_df.copy()
                        display_df['beneficiaries'] = display_df['beneficiaries'].apply(lambda x: f"{x:,.0f}")
                        display_df['total_cost'] = display_df['total_cost'].apply(lambda x: f"${x:,.0f}")
                        display_df['avg_benefit'] = display_df['avg_benefit'].apply(lambda x: f"${x:,.0f}")
                        display_df.columns = ['Income Bracket', 'Benefiting Households', 'Total Cost', 'Avg Benefit']
                        st.dataframe(display_df, use_container_width=True, hide_index=True)

                st.markdown("---")

                # Dataset information
                with st.expander("About the Rhode Island dataset"):
                    st.markdown(
                        f"""
                        This analysis uses PolicyEngine's Rhode Island microsimulation dataset,
                        which contains a representative sample of {dataset['household_count']:,.0f} Rhode Island households.

                        **Dataset statistics:**
                        - **Total households:** {dataset['household_count']:,.0f}
                        - **Total population:** {dataset['person_count']:,.0f}
                        - **Households with children:** {dataset['households_with_children']:,.0f}
                        - **Total children under 18:** {dataset['total_children']:,.0f}
                        - **Median AGI:** ${dataset['median_agi']:,.0f}
                        - **75th percentile AGI:** ${dataset['p75_agi']:,.0f}
                        - **90th percentile AGI:** ${dataset['p90_agi']:,.0f}

                        The dataset is weighted to represent the full Rhode Island population.
                        All statistics above reflect population estimates, not just the sample.
                        """
                    )

            # About section
            with st.expander("About this calculator"):
                from importlib.metadata import version

                pe_version = version("policyengine-us")

                st.markdown(
                    f"""
                This calculator models the Rhode Island Child Tax Credit reform proposal based on [PolicyEngine US PR #6643](https://github.com/PolicyEngine/policyengine-us/pull/6643).

                This calculator uses [PolicyEngine's open-source tax-benefit microsimulation model](https://github.com/PolicyEngine/policyengine-us) (version {pe_version}).

                **Reform parameters:**
                - **Eligibility**: Children under age 18
                - **Credit structure**: Non-refundable
                - **Phase-out**: AGI-based (Adjusted Gross Income)
                - **State**: Rhode Island residents only

                **Important notes:**
                - This calculator models the reform as implemented in PolicyEngine US
                - Actual policy details may differ from this model
                - The RI CTC is non-refundable, so benefits depend on having RI tax liability
                - Results assume standard household circumstances; actual benefits may vary

                📖 [Learn more about PolicyEngine](https://policyengine.org)
                """
                )


def create_chart(
    age_head,
    age_spouse,
    dependent_ages,
    reform_params,
):
    """Create income curve charts showing RI CTC across income range

    Args:
        age_head: Age of household head
        age_spouse: Age of spouse (or None)
        dependent_ages: Tuple of dependent ages
        reform_params: Dict of reform parameters

    Returns tuple of (comparison_fig, delta_fig, benefit_info, income_range,
                      ctc_baseline_range, ctc_reform_range, x_axis_max)
    """

    # Create base household structure for income sweep
    base_household = build_household_situation(
        age_head=age_head,
        age_spouse=age_spouse,
        dependent_ages=list(dependent_ages) if dependent_ages else [],
        year=2026,
        with_axes=True,
    )

    try:
        # Create reform with custom parameters
        reform = create_custom_reform(**reform_params)

        # Calculate both curves - baseline and reform for 2026
        # We need to look at NET INCOME change to capture both CTC and exemption effects
        sim_baseline = Simulation(situation=base_household)
        sim_reform = Simulation(situation=base_household, reform=reform)

        income_range = sim_baseline.calculate(
            "employment_income", map_to="household", period=2026
        )

        # Calculate detailed tax components for both scenarios
        # This helps us understand what's actually happening

        # RI income tax
        ri_tax_baseline = sim_baseline.calculate(
            "ri_income_tax", map_to="tax_unit", period=2026
        )
        ri_tax_reform = sim_reform.calculate(
            "ri_income_tax", map_to="tax_unit", period=2026
        )

        # RI exemptions
        ri_exemptions_baseline = sim_baseline.calculate(
            "ri_exemptions", map_to="tax_unit", period=2026
        )
        ri_exemptions_reform = sim_reform.calculate(
            "ri_exemptions", map_to="tax_unit", period=2026
        )

        # Household net income
        net_income_baseline = sim_baseline.calculate(
            "household_net_income", map_to="household", period=2026
        )
        net_income_reform = sim_reform.calculate(
            "household_net_income", map_to="household", period=2026
        )

        # The benefit is the increase in net income
        ctc_range_baseline = np.zeros(len(income_range))  # For labeling purposes
        ctc_range_reform = net_income_reform - net_income_baseline  # Total benefit

        # Store diagnostic data
        tax_change = ri_tax_reform - ri_tax_baseline  # Should be negative (tax savings) or positive (tax increase)
        exemption_change = ri_exemptions_reform - ri_exemptions_baseline

        # Find where CTC goes to zero for dynamic x-axis range
        max_income_with_ctc = 200000  # Default fallback
        for i in range(len(ctc_range_reform) - 1, -1, -1):
            if ctc_range_reform[i] > 0:
                max_income_with_ctc = income_range[i]
                break

        # Add 10% padding to the range
        x_axis_max = min(500000, max_income_with_ctc * 1.2)

        # Calculate delta
        delta_range = ctc_range_reform - ctc_range_baseline

        # Create hover text with diagnostic info
        hover_text = []
        for i in range(len(income_range)):
            inc = income_range[i]
            ctc_base = ctc_range_baseline[i]
            ctc_ref = ctc_range_reform[i]
            delta = delta_range[i]

            text = f"<b>Income: ${inc:,.0f}</b><br><br>"
            text += f"<b>Current law benefit:</b> ${ctc_base:,.0f}<br>"
            text += f"<b>With reform benefit:</b> ${ctc_ref:,.0f}<br>"

            # Add diagnostic information
            text += f"<br><b>Exemptions change:</b> ${exemption_change[i]:,.0f}<br>"
            text += f"<b>RI tax change:</b> ${tax_change[i]:,.0f}<br>"

            if delta > 0:
                text += f"<br><b>Total net income increase:</b> ${delta:,.0f}"
            elif delta < 0:
                text += f"<br><b>Total net income decrease:</b> ${-delta:,.0f}"
            else:
                text += "<br><b>No change</b>"

            hover_text.append(text)

        # Create comparison plot
        fig = go.Figure()

        # Add invisible hover trace
        fig.add_trace(
            go.Scatter(
                x=income_range,
                y=np.maximum(ctc_range_baseline, ctc_range_reform),
                mode="lines",
                line=dict(width=0),
                hovertext=hover_text,
                hoverinfo="text",
                showlegend=False,
                name="",
            )
        )

        # Add baseline line (current law)
        fig.add_trace(
            go.Scatter(
                x=income_range,
                y=ctc_range_baseline,
                mode="lines",
                name="Current law",
                line=dict(color=COLORS["gray"], width=3),
                hoverinfo="skip",
            )
        )

        # Add reform line
        fig.add_trace(
            go.Scatter(
                x=income_range,
                y=ctc_range_reform,
                mode="lines",
                name="With RI CTC reform",
                line=dict(color=COLORS["primary"], width=3),
                hoverinfo="skip",
            )
        )

        # Update layout for comparison chart
        fig.update_layout(
            title={
                "text": "Total benefit from RI reform by household income (2026)",
                "font": {"size": 20, "color": COLORS["primary"]},
            },
            xaxis_title="Annual household income",
            yaxis_title="Annual benefit (CTC + tax savings)",
            height=400,
            xaxis=dict(
                tickformat="$,.0f", range=[0, x_axis_max], automargin=True
            ),
            yaxis=dict(
                tickformat="$,.0f", rangemode="tozero", automargin=True
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Roboto, sans-serif"),
            legend=dict(
                orientation="h", yanchor="bottom", y=0.98, xanchor="right", x=1
            ),
            margin=dict(l=80, r=40, t=60, b=80),
        )

        # Create delta chart
        fig_delta = go.Figure()

        # Create hover text for delta chart
        delta_hover_text = []
        for i in range(len(income_range)):
            inc = income_range[i]
            delta = delta_range[i]
            ctc_ref = ctc_range_reform[i]

            text = f"<b>Income: ${inc:,.0f}</b><br><br>"
            text += f"<b>Total benefit:</b> ${ctc_ref:,.0f}<br>"
            if delta > 0:
                text += f"<b>Increase in net income:</b> ${delta:,.0f}"
            else:
                text += "<b>No change</b>"

            delta_hover_text.append(text)

        # Add delta line
        fig_delta.add_trace(
            go.Scatter(
                x=income_range,
                y=delta_range,
                mode="lines",
                name="RI CTC benefit",
                line=dict(color=COLORS["primary"], width=3),
                fill="tozeroy",
                fillcolor=f"rgba(44, 100, 150, 0.2)",
                hovertext=delta_hover_text,
                hoverinfo="text",
            )
        )

        fig_delta.update_layout(
            title={
                "text": "Total benefit from RI reform (2026)",
                "font": {"size": 20, "color": COLORS["primary"]},
            },
            xaxis_title="Annual household income",
            yaxis_title="Annual benefit (CTC + tax savings)",
            height=400,
            xaxis=dict(
                tickformat="$,.0f", range=[0, x_axis_max], automargin=True
            ),
            yaxis=dict(
                tickformat="$,.0f", rangemode="tozero", automargin=True
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Roboto, sans-serif"),
            showlegend=False,
            margin=dict(l=80, r=40, t=60, b=80),
        )

        # Calculate benefit range information
        benefit_indices = np.where(delta_range > 0)[0]
        if len(benefit_indices) > 0:
            min_benefit_income = income_range[benefit_indices[0]]
            max_benefit_income = income_range[benefit_indices[-1]]
            max_benefit = np.max(delta_range[benefit_indices])
            peak_benefit_index = benefit_indices[np.argmax(delta_range[benefit_indices])]
            peak_benefit_income = income_range[peak_benefit_index]

            benefit_info = {
                "min_income": float(min_benefit_income),
                "max_income": float(max_benefit_income),
                "max_benefit": float(max_benefit),
                "peak_income": float(peak_benefit_income),
            }
        else:
            benefit_info = None

        return (
            fig,
            fig_delta,
            benefit_info,
            income_range,
            ctc_range_baseline,
            ctc_range_reform,
            x_axis_max,
            # Diagnostic data
            ri_exemptions_baseline,
            ri_exemptions_reform,
            exemption_change,
            ri_tax_baseline,
            ri_tax_reform,
            tax_change,
        )

    except Exception as e:
        st.error(f"Error generating charts: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        # Return None for all values including diagnostic data
        return None, None, None, None, None, None, 200000, None, None, None, None, None, None


if __name__ == "__main__":
    main()
