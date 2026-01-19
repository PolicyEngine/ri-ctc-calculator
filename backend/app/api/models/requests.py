"""Request models for API validation."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class ReformParams(BaseModel):
    """Reform parameter configuration."""

    # CTC parameters
    ctc_amount: float = Field(1000, ge=0, le=10000, description="CTC amount per eligible child")
    ctc_age_limit: int = Field(18, ge=0, le=26, description="Maximum age for CTC eligibility")
    ctc_refundability_cap: float = Field(0, ge=0, description="Refundability cap (0=non-refundable)")
    ctc_phaseout_rate: float = Field(0.0, ge=0.0, le=1.0, description="CTC phase-out rate (for rate-based phaseout)")
    ctc_phaseout_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "SINGLE": 0,
            "JOINT": 0,
            "HEAD_OF_HOUSEHOLD": 0,
            "SURVIVING_SPOUSE": 0,
            "SEPARATE": 0,
        },
        description="CTC phase-out thresholds by filing status (for rate-based phaseout)"
    )
    # Stepped phaseout parameters (Governor's proposal style)
    ctc_stepped_phaseout: bool = Field(False, description="Use stepped phaseout instead of rate-based")
    ctc_stepped_phaseout_threshold: float = Field(0, ge=0, description="AGI threshold where stepped phaseout begins")
    ctc_stepped_phaseout_increment: float = Field(0, ge=0, description="Income increment per step")
    ctc_stepped_phaseout_rate_per_step: float = Field(0.0, ge=0.0, le=1.0, description="Percentage point reduction per step")
    ctc_young_child_boost_amount: float = Field(0, ge=0, le=10000, description="Additional boost per young child")
    ctc_young_child_boost_age_limit: int = Field(6, ge=0, le=26, description="Maximum age for young child boost")

    # Dependent exemption parameters
    enable_exemption_reform: bool = Field(False, description="Enable dependent exemption reform")
    exemption_amount: float = Field(5200, ge=0, le=20000, description="Dependent exemption amount")
    exemption_age_limit_enabled: bool = Field(True, description="Enable age limit on exemptions")
    exemption_age_threshold: int = Field(18, ge=0, le=26, description="Age threshold for exemptions")
    exemption_phaseout_rate: float = Field(0.0, ge=0.0, le=1.0, description="Exemption phase-out rate")
    exemption_phaseout_thresholds: Optional[Dict[str, float]] = Field(
        None,
        description="Exemption phase-out thresholds by filing status"
    )


class HouseholdRequest(BaseModel):
    """Request for household-specific impact calculation."""

    age_head: int = Field(..., ge=18, le=100, description="Age of household head")
    age_spouse: Optional[int] = Field(None, ge=18, le=100, description="Age of spouse (if married)")
    dependent_ages: List[int] = Field(default_factory=list, description="List of dependent ages")
    income: int = Field(..., ge=0, description="Adjusted Gross Income (AGI) - combined household AGI")
    year: int = Field(2027, ge=2026, le=2030, description="Tax year for simulation (2026 or 2027)")
    reform_params: ReformParams


class AggregateImpactRequest(BaseModel):
    """Request for aggregate/statewide impact calculation."""

    year: int = Field(2027, ge=2026, le=2030, description="Tax year for simulation (2026 or 2027)")
    reform_params: ReformParams
