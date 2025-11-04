"""Aggregate/statewide impact endpoints."""

from fastapi import APIRouter, HTTPException
import logging

from app.api.models.requests import AggregateImpactRequest
from app.api.models.responses import AggregateImpactResponse, DatasetSummary
from app.services.calculator import calculate_aggregate, get_dataset_info

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/aggregate-impact", response_model=AggregateImpactResponse)
async def aggregate_impact(request: AggregateImpactRequest):
    """
    Calculate aggregate/statewide impact of RI CTC reform.

    Uses the RI microsimulation dataset to estimate:
    - Total cost
    - Number of beneficiaries
    - Poverty impacts
    - Distribution by income bracket

    Args:
        request: Reform parameters

    Returns:
        Statewide impact statistics
    """
    try:
        logger.info("Calculating aggregate impact...")

        result = await calculate_aggregate(reform_params=request.reform_params.model_dump())

        logger.info(f"✓ Aggregate impact calculated: {result.beneficiaries:,.0f} households, "
                   f"${result.total_cost:,.0f} total cost")
        return result

    except Exception as e:
        logger.error(f"Error calculating aggregate impact: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dataset-summary", response_model=DatasetSummary)
async def dataset_summary():
    """
    Get summary statistics about the RI dataset.

    Returns:
        Dataset statistics (household counts, income percentiles, etc.)
    """
    try:
        logger.info("Fetching dataset summary...")
        result = await get_dataset_info()
        logger.info("✓ Dataset summary retrieved")
        return result

    except Exception as e:
        logger.error(f"Error fetching dataset summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
