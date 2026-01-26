"""Response models for API responses."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class BenefitAtIncome(BaseModel):
    """Benefit breakdown at a specific income level."""

    baseline: float = Field(..., description="Benefit under current law")
    reform: float = Field(..., description="Benefit with reform")
    difference: float = Field(..., description="Net income increase")
    ctc_component: float = Field(..., description="CTC credit component")
    exemption_tax_benefit: float = Field(..., description="Tax savings from exemption changes")


class HouseholdImpactResponse(BaseModel):
    """Response for household impact calculation."""

    # Income sweep arrays for charts
    income_range: List[float] = Field(..., description="Array of income values")
    ctc_baseline_range: List[float] = Field(..., description="Baseline benefits across income range")
    ctc_reform_range: List[float] = Field(..., description="Reform benefits across income range")

    # Component breakdowns
    ctc_component: List[float] = Field(..., description="CTC credit component across income range")
    exemption_tax_benefit: List[float] = Field(..., description="Exemption tax benefit across income range")

    # Specific benefit at user's income
    benefit_at_income: BenefitAtIncome

    # Chart configuration
    x_axis_max: float = Field(..., description="Recommended max for x-axis")

    # Diagnostic data (optional, for debugging)
    diagnostics: Optional[Dict] = Field(None, description="Diagnostic information")


class IncomeBracket(BaseModel):
    """Impact by income bracket."""

    bracket: str = Field(..., description="Income bracket label")
    beneficiaries: float = Field(..., description="Number of benefiting households")
    total_cost: float = Field(..., description="Total cost for this bracket")
    avg_benefit: float = Field(..., description="Average benefit per household")


class AggregateImpactResponse(BaseModel):
    """Response for aggregate/statewide impact calculation."""

    # Top-level metrics
    total_cost: float = Field(..., description="Total annual cost of reform")
    beneficiaries: float = Field(..., description="Number of households benefiting")
    avg_benefit: float = Field(..., description="Average benefit among beneficiaries")
    children_affected: float = Field(..., description="Number of children affected")

    # Winners/losers
    winners: float = Field(..., description="Number of winning households")
    losers: float = Field(..., description="Number of losing households")
    winners_rate: float = Field(..., description="Percentage of winners")
    losers_rate: float = Field(..., description="Percentage of losers")

    # Poverty impacts
    poverty_baseline_rate: float = Field(..., description="Baseline poverty rate (%)")
    poverty_reform_rate: float = Field(..., description="Reform poverty rate (%)")
    poverty_rate_change: float = Field(..., description="Poverty rate change (percentage points)")
    poverty_percent_change: float = Field(..., description="Poverty percent change (relative)")

    child_poverty_baseline_rate: float = Field(..., description="Baseline child poverty rate (%)")
    child_poverty_reform_rate: float = Field(..., description="Reform child poverty rate (%)")
    child_poverty_rate_change: float = Field(..., description="Child poverty rate change (pp)")
    child_poverty_percent_change: float = Field(..., description="Child poverty percent change (relative)")

    # Deep poverty impacts (below 50% of poverty line)
    deep_poverty_baseline_rate: float = Field(..., description="Baseline deep poverty rate (%)")
    deep_poverty_reform_rate: float = Field(..., description="Reform deep poverty rate (%)")
    deep_poverty_rate_change: float = Field(..., description="Deep poverty rate change (pp)")
    deep_poverty_percent_change: float = Field(..., description="Deep poverty percent change (relative)")

    deep_child_poverty_baseline_rate: float = Field(..., description="Baseline deep child poverty rate (%)")
    deep_child_poverty_reform_rate: float = Field(..., description="Reform deep child poverty rate (%)")
    deep_child_poverty_rate_change: float = Field(..., description="Deep child poverty rate change (pp)")
    deep_child_poverty_percent_change: float = Field(..., description="Deep child poverty percent change (relative)")

    # Income bracket breakdown
    by_income_bracket: List[IncomeBracket] = Field(..., description="Impact by income bracket")


class DatasetSummary(BaseModel):
    """Summary of the RI dataset."""

    household_count: float = Field(..., description="Total households in dataset")
    person_count: float = Field(..., description="Total population")
    median_agi: float = Field(..., description="Median AGI")
    p75_agi: float = Field(..., description="75th percentile AGI")
    p90_agi: float = Field(..., description="90th percentile AGI")
    total_children: float = Field(..., description="Total children under 18")
    households_with_children: float = Field(..., description="Households with children")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    dataset_loaded: bool = Field(..., description="Whether RI dataset is loaded")
    version: str = Field(..., description="API version")
