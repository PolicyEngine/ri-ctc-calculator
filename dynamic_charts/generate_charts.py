"""Generate interactive Plotly charts for the Governor's Proposal blog post.

Creates two charts that match the calculator's visual style:
1. Household Impact Chart - Change in Net Income by AGI (preset household)
2. Income Range Chart - Average impact by income bracket (statewide)

Usage:
    python dynamic_charts/generate_charts.py
"""

import sys
from pathlib import Path
import numpy as np
import plotly.graph_objects as go

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from policyengine_us import Simulation
from ri_ctc_calc.calculations.household import build_household_situation
from ri_ctc_calc.calculations.reforms import create_custom_reform
from ri_ctc_calc.calculations.microsimulation import calculate_aggregate_impact

# Color scheme matching the calculator
TEAL = "#319795"
GRAY = "#64748B"
GRID_COLOR = "#e0e0e0"
AXIS_COLOR = "#666"
REFERENCE_LINE_COLOR = "#666"
WHITE = "#ffffff"
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"

# Governor's Proposal reform parameters
GOVERNOR_REFORM_PARAMS = dict(
    ctc_amount=325,
    ctc_age_limit=19,
    ctc_refundability_cap=100000,
    ctc_phaseout_rate=0,
    ctc_stepped_phaseout=True,
    ctc_stepped_phaseout_threshold=265965,
    ctc_stepped_phaseout_increment=7590,
    ctc_stepped_phaseout_rate_per_step=0.20,
    ctc_young_child_boost_amount=0,
    ctc_young_child_boost_age_limit=6,
    enable_exemption_reform=True,
    exemption_amount=0,
    exemption_age_limit_enabled=True,
    exemption_age_threshold=19,
    exemption_phaseout_rate=0,
    year=2027,
)

# Preset household: single, age 35, one child age 5
PRESET_HOUSEHOLD = dict(
    age_head=35,
    age_spouse=None,
    dependent_ages=[5],
)

YEAR = 2027
X_AXIS_MAX = 500_000


def generate_household_impact_chart():
    """Generate the household impact line chart (Change in Net Income by AGI)."""
    print("Generating household impact chart...")

    # Build household with income sweep axes
    household = build_household_situation(
        **PRESET_HOUSEHOLD,
        year=YEAR,
        with_axes=True,
    )

    # Create reform
    reform = create_custom_reform(**GOVERNOR_REFORM_PARAMS)

    # Run baseline and reform simulations
    sim_baseline = Simulation(situation=household)
    sim_reform = Simulation(situation=household, reform=reform)

    # Get income range
    income_range = sim_baseline.calculate(
        "adjusted_gross_income", map_to="tax_unit", period=YEAR
    )

    # Calculate net income for both
    net_income_baseline = sim_baseline.calculate(
        "household_net_income", map_to="household", period=YEAR
    )
    net_income_reform = sim_reform.calculate(
        "household_net_income", map_to="household", period=YEAR
    )

    # Change in net income
    benefit = net_income_reform - net_income_baseline

    # Filter to x-axis max
    mask = income_range <= X_AXIS_MAX
    x = np.array(income_range[mask])
    y = np.array(benefit[mask])

    # Build the chart
    fig = go.Figure()

    # Reference line at y=0
    fig.add_hline(
        y=0,
        line_color=REFERENCE_LINE_COLOR,
        line_width=2,
    )

    # Benefit line — matches calculator: type="monotone", strokeWidth={3},
    # stroke="#319795", dot={false}, name="Change in Net Income"
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            name="Change in Net Income",
            line=dict(color=TEAL, width=3, shape="spline"),
            # Tooltip matches calculator: label "Income: $X.XX", value "$X.XX"
            hovertemplate=(
                "Income: $%{x:,.2f}<br>"
                "Change in Net Income : $%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text=(
                f"<b>Change in Net Income from RI CTC Reform"
                f" by Adjusted Gross Income ({YEAR})</b>"
            ),
            font=dict(size=18, color="#1f2937", family=FONT_FAMILY),
        ),
        font=dict(family=FONT_FAMILY),
        xaxis=dict(
            title="",
            range=[0, X_AXIS_MAX],
            # Match calculator: tickFormatter={formatIncome} → "$Xk"
            tickvals=[150_000, 300_000, 500_000],
            ticktext=["$150k", "$300k", "$500k"],
            # Grid: strokeDasharray="3 3" stroke="#e0e0e0"
            gridcolor=GRID_COLOR,
            griddash="3px,3px",
            linecolor=AXIS_COLOR,
            tickcolor=AXIS_COLOR,
            tickfont=dict(color=AXIS_COLOR),
        ),
        yaxis=dict(
            title="",
            # Match calculator: formatCurrency → "$X.XX" (2 decimal places)
            tickformat="$,.2f",
            gridcolor=GRID_COLOR,
            griddash="3px,3px",
            linecolor=AXIS_COLOR,
            tickcolor=AXIS_COLOR,
            tickfont=dict(color=AXIS_COLOR),
            dtick=85,
            range=[0, 340],
        ),
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        # Match calculator: height={400}, margin={{ left: 20, right: 20, top: 5, bottom: 5 }}
        margin=dict(l=80, r=20, t=60, b=60),
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color=TEAL),
        ),
        hovermode="x unified",
    )

    output_path = Path(__file__).parent / "household_impact_chart.html"
    fig.write_html(str(output_path), auto_open=True)
    print(f"Household impact chart saved to {output_path}")
    return fig


def generate_income_range_chart():
    """Generate the income range bar chart (average impact by income bracket)."""
    print("Generating income range chart...")

    # Create reform and run microsimulation
    reform = create_custom_reform(**GOVERNOR_REFORM_PARAMS)
    impact = calculate_aggregate_impact(reform, year=YEAR)

    brackets = impact["by_income_bracket"]

    labels = [b["bracket"] for b in brackets]
    avg_benefits = [b["avg_benefit"] for b in brackets]

    # Color bars: teal for positive, gray for negative
    # Matches calculator: fill={entry.avg_benefit >= 0 ? '#319795' : '#64748B'}
    colors = [TEAL if v >= 0 else GRAY for v in avg_benefits]

    fig = go.Figure()

    # Reference line at y=0 — matches calculator: stroke="#666" strokeWidth={2}
    fig.add_hline(
        y=0,
        line_color=REFERENCE_LINE_COLOR,
        line_width=2,
    )

    # Tooltip matches calculator: formatCurrencyWithSign → "+$X.XX" / "-$X.XX"
    fig.add_trace(
        go.Bar(
            x=labels,
            y=avg_benefits,
            marker_color=colors,
            name="Average Impact",
            hovertemplate=(
                "%{x}<br>"
                "Average Impact : %{customdata}"
                "<extra></extra>"
            ),
            customdata=[
                f"+${v:,.2f}" if v >= 0 else f"-${abs(v):,.2f}"
                for v in avg_benefits
            ],
        )
    )

    fig.update_layout(
        title=dict(
            text="<b>Impact by Income Bracket</b>",
            font=dict(size=20, color="#1f2937", family=FONT_FAMILY),
        ),
        font=dict(family=FONT_FAMILY),
        xaxis=dict(
            title="",
            # Grid: strokeDasharray="3 3" stroke="#e0e0e0"
            gridcolor=GRID_COLOR,
            griddash="3px,3px",
            linecolor=AXIS_COLOR,
            tickcolor=AXIS_COLOR,
            tickfont=dict(color=AXIS_COLOR),
        ),
        yaxis=dict(
            title="",
            # Match calculator: formatCurrencyWithSign → "+$X.XX" / "-$X.XX"
            tickformat="+$,.2f",
            gridcolor=GRID_COLOR,
            griddash="3px,3px",
            linecolor=AXIS_COLOR,
            tickcolor=AXIS_COLOR,
            tickfont=dict(color=AXIS_COLOR),
            dtick=150,
            range=[0, 600],
        ),
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        margin=dict(l=80, r=20, t=60, b=60),
        height=400,
        showlegend=False,
        hovermode="x",
    )

    output_path = Path(__file__).parent / "income_range_chart.html"
    fig.write_html(str(output_path), auto_open=True)
    print(f"Income range chart saved to {output_path}")
    return fig


if __name__ == "__main__":
    generate_household_impact_chart()
    generate_income_range_chart()
    print("All charts generated successfully.")
