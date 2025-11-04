"""Household calculation endpoints."""

from fastapi import APIRouter, HTTPException
import logging

from app.api.models.requests import HouseholdRequest
from app.api.models.responses import HouseholdImpactResponse, BenefitAtIncome
from app.services.calculator import calculate_household_impact, calculate_household_benefit_quick

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/household-impact", response_model=HouseholdImpactResponse)
async def household_impact(request: HouseholdRequest):
    """
    Calculate RI CTC impact for a specific household across income range.

    This endpoint:
    - Sweeps income from $0 to $1M
    - Calculates baseline vs reform scenarios
    - Returns arrays for charting
    - Includes benefit at specified income

    Args:
        request: Household configuration and reform parameters

    Returns:
        Income curves and benefit breakdown
    """
    try:
        logger.info(f"Calculating household impact for age_head={request.age_head}, "
                   f"dependents={len(request.dependent_ages)}, income=${request.income}")

        result = await calculate_household_impact(
            age_head=request.age_head,
            age_spouse=request.age_spouse,
            dependent_ages=request.dependent_ages,
            income=request.income,
            reform_params=request.reform_params.model_dump(),
        )

        logger.info("✓ Household impact calculated successfully")
        return result

    except Exception as e:
        logger.error(f"Error calculating household impact: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/household-benefit-quick", response_model=BenefitAtIncome)
async def household_benefit_quick(request: HouseholdRequest):
    """
    Quick calculation of benefit at specific income only (no chart data).

    This is MUCH faster than /household-impact because it:
    - Only calculates at the single specified income point
    - No income sweep (no chart arrays)
    - Returns just the benefit breakdown

    Use this for immediate feedback, then call /household-impact for chart.

    Args:
        request: Household configuration and reform parameters

    Returns:
        Benefit breakdown at specified income only
    """
    try:
        logger.info(f"Quick benefit calculation for age_head={request.age_head}, "
                   f"income=${request.income}")

        result = await calculate_household_benefit_quick(
            age_head=request.age_head,
            age_spouse=request.age_spouse,
            dependent_ages=request.dependent_ages,
            income=request.income,
            reform_params=request.reform_params.model_dump(),
        )

        logger.info("✓ Quick benefit calculated successfully")
        return result

    except Exception as e:
        logger.error(f"Error calculating quick benefit: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
