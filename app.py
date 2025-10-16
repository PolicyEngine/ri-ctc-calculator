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
    from ri_ctc_calc.calculations.reforms import create_ri_ctc_reform

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
            }
            # Clear cached charts if params changed
            if hasattr(st.session_state, "params") and st.session_state.params != new_params:
                st.session_state.income_range = None
                st.session_state.fig_comparison = None
                st.session_state.fig_delta = None
            st.session_state.params = new_params

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
                ) = create_chart(
                    params["age_head"],
                    params["age_spouse"],
                    tuple(params["dependent_ages"]),
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

        # Show tabs using cached charts
        if hasattr(st.session_state, "fig_delta") and st.session_state.fig_delta is not None:
            tab1, tab2, tab3 = st.tabs([
                "Benefit from reform",
                "Baseline vs. reform",
                "Your impact"
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
                st.markdown("Enter your annual household income to see your specific impact.")

                user_income = st.number_input(
                    "Annual household income:",
                    min_value=0,
                    value=50000,
                    step=1000,
                    help="Adjusted Gross Income (AGI). Includes: wages, self-employment income, capital gains, interest, dividends, pensions, and other income sources.",
                    format="%d",
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
                            help="Your RI CTC under current law (no RI CTC)",
                        )

                    with col_reform:
                        st.metric(
                            "With RI CTC reform",
                            f"${ctc_reform:,.0f}",
                            help="Your RI CTC if reform is enacted",
                        )

                    with col_diff:
                        if difference > 0:
                            st.metric(
                                "You gain",
                                f"${difference:,.0f} per year",
                                delta_color="normal",
                            )
                        else:
                            st.metric("No change", "$0")

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
):
    """Create income curve charts showing RI CTC across income range

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
        # Create reform
        reform = create_ri_ctc_reform()

        # Calculate both curves - baseline and reform for 2026
        sim_baseline = Simulation(situation=base_household)
        sim_reform = Simulation(situation=base_household, reform=reform)

        income_range = sim_baseline.calculate(
            "employment_income", map_to="household", period=2026
        )
        ctc_range_baseline = sim_baseline.calculate(
            "ri_ctc", map_to="tax_unit", period=2026
        )
        ctc_range_reform = sim_reform.calculate(
            "ri_ctc", map_to="tax_unit", period=2026
        )

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

        # Create hover text
        hover_text = []
        for i in range(len(income_range)):
            inc = income_range[i]
            ctc_base = ctc_range_baseline[i]
            ctc_ref = ctc_range_reform[i]
            delta = delta_range[i]

            text = f"<b>Income: ${inc:,.0f}</b><br><br>"
            text += f"<b>RI CTC (current law):</b> ${ctc_base:,.0f}<br>"
            text += f"<b>RI CTC (reform):</b> ${ctc_ref:,.0f}<br>"
            if delta > 0:
                text += f"<b>Benefit from reform:</b> ${delta:,.0f}"
            else:
                text += "<b>No change</b>"

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
                "text": "Rhode Island CTC by household income (2026)",
                "font": {"size": 20, "color": COLORS["primary"]},
            },
            xaxis_title="Annual household income",
            yaxis_title="Annual RI CTC value",
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
            text += f"<b>RI CTC (reform):</b> ${ctc_ref:,.0f}<br>"
            if delta > 0:
                text += f"<b>Benefit from reform:</b> ${delta:,.0f}"
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
                "text": "Benefit from RI CTC reform (2026)",
                "font": {"size": 20, "color": COLORS["primary"]},
            },
            xaxis_title="Annual household income",
            yaxis_title="Annual benefit (reform - current law)",
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
        )

    except Exception as e:
        st.error(f"Error generating charts: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None, None, None, None, None, None, 200000


if __name__ == "__main__":
    main()
