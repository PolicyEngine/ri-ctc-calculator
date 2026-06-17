"""Precompute statewide + sample-household impacts for the Governor's
proposals and write them to ``frontend/public/data/presets/{id}.json``.

Both presets share every CTC parameter except ``ctc_amount``. The
"original" preset uses $325/child; "revised" uses $650/child. Three
sample-household profiles are computed for each preset so the frontend
can render "how this would affect a representative family" cards
without hitting the live API on preset clicks.

Run locally:

    python scripts/precompute_presets.py

The output JSON shape matches the backend Pydantic response models
(``AggregateImpactResponse`` + ``HouseholdImpactResponse``) so the
frontend's TypeScript types are correct by construction.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

# Make the project root importable so ``ri_ctc_calc`` and ``backend.app``
# resolve when this script runs from anywhere.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from policyengine_us import Microsimulation

from app.api.models.responses import (  # type: ignore  # backend pkg
    AggregateImpactResponse,
    HouseholdImpactResponse,
)
from app.services.calculator import calculate_household_impact  # type: ignore
from ri_ctc_calc.calculations.microsimulation import (
    RI_DATASET_PATH,
    calculate_aggregate_impact,
)
from ri_ctc_calc.calculations.reforms import create_custom_reform


YEAR = 2027

# Mirror of ``frontend/lib/presets.ts``. Keep these in sync.
EXAMPLE_PROFILES = [
    {
        "id": "single-1kid-20k",
        "label": "Single filer, one child, $20k income",
        "age_head": 30,
        "age_spouse": None,
        "married": False,
        "dependent_ages": [5],
        "income": 20000,
    },
    {
        "id": "single-2kid-50k",
        "label": "Single filer, two children, $50k income",
        "age_head": 35,
        "age_spouse": None,
        "married": False,
        "dependent_ages": [5, 8],
        "income": 50000,
    },
    {
        "id": "married-2kid-150k",
        "label": "Married couple, two children, $150k income",
        "age_head": 35,
        "age_spouse": 35,
        "married": True,
        "dependent_ages": [5, 8],
        "income": 150000,
    },
]


EMPTY_THRESHOLDS = {
    "SINGLE": 0,
    "JOINT": 0,
    "HEAD_OF_HOUSEHOLD": 0,
    "SURVIVING_SPOUSE": 0,
    "SEPARATE": 0,
}

# Enacted 2027 law: $330/child, phaseout starts at $88,500 ($110,640 joint),
# dependent exemption stays in place. Mirror of
# ``ENACTED_CTC_PHASEOUT_THRESHOLDS`` / ``_INCREMENTS`` in presets.ts.
ENACTED_CTC_PHASEOUT_THRESHOLDS = {
    "SINGLE": 88500,
    "JOINT": 110640,
    "HEAD_OF_HOUSEHOLD": 88500,
    "SURVIVING_SPOUSE": 88500,
    "SEPARATE": 88500,
}

ENACTED_CTC_PHASEOUT_INCREMENTS = {
    "SINGLE": 2875,
    "JOINT": 3590,
    "HEAD_OF_HOUSEHOLD": 2875,
    "SURVIVING_SPOUSE": 2875,
    "SEPARATE": 2875,
}


def preset_reform_params(preset_id: str) -> dict[str, Any]:
    """Return the ``ReformParams`` dict for ``preset_id`` (mirror of
    ``presetReformParams`` in ``frontend/lib/presets.ts``)."""
    if preset_id == "enacted":
        return {
            "ctc_amount": 330,
            # The contrib CTC reform uses age < age_limit; 19 includes children
            # age 18 or under, matching the enacted statute.
            "ctc_age_limit": 19,
            "ctc_refundability_cap": 100000,
            "ctc_phaseout_rate": 0,
            "ctc_phaseout_thresholds": dict(EMPTY_THRESHOLDS),
            "ctc_stepped_phaseout": True,
            "ctc_stepped_phaseout_rate_per_step": 0.20,
            "ctc_stepped_phaseout_thresholds": dict(
                ENACTED_CTC_PHASEOUT_THRESHOLDS
            ),
            "ctc_stepped_phaseout_increments": dict(
                ENACTED_CTC_PHASEOUT_INCREMENTS
            ),
            "ctc_young_child_boost_amount": 0,
            "ctc_young_child_boost_age_limit": 6,
            # Enacted law keeps the dependent exemption in place.
            "enable_exemption_reform": False,
            "exemption_amount": 5200,
            "exemption_age_limit_enabled": True,
            "exemption_age_threshold": 19,
            "exemption_phaseout_rate": 0,
            "exemption_phaseout_thresholds": dict(EMPTY_THRESHOLDS),
        }

    ctc_amount = 650 if preset_id == "revised" else 325
    return {
        "ctc_amount": ctc_amount,
        "ctc_age_limit": 19,
        "ctc_refundability_cap": 100000,
        "ctc_phaseout_rate": 0,
        "ctc_phaseout_thresholds": dict(EMPTY_THRESHOLDS),
        "ctc_stepped_phaseout": True,
        "ctc_stepped_phaseout_rate_per_step": 0.20,
        "ctc_stepped_phaseout_thresholds": {
            "SINGLE": 265965,
            "JOINT": 265965,
            "HEAD_OF_HOUSEHOLD": 265965,
            "SURVIVING_SPOUSE": 265965,
            "SEPARATE": 265965,
        },
        "ctc_stepped_phaseout_increments": {
            "SINGLE": 7590,
            "JOINT": 7590,
            "HEAD_OF_HOUSEHOLD": 7590,
            "SURVIVING_SPOUSE": 7590,
            "SEPARATE": 7590,
        },
        "ctc_young_child_boost_amount": 0,
        "ctc_young_child_boost_age_limit": 6,
        "enable_exemption_reform": True,
        "exemption_amount": 0,
        "exemption_age_limit_enabled": True,
        "exemption_age_threshold": 19,
        "exemption_phaseout_rate": 0,
        "exemption_phaseout_thresholds": dict(EMPTY_THRESHOLDS),
    }


async def _household_for_profile(
    profile: dict[str, Any], reform_params: dict[str, Any]
) -> HouseholdImpactResponse:
    age_spouse = profile["age_spouse"] if profile["married"] else None
    return await calculate_household_impact(
        age_head=profile["age_head"],
        age_spouse=age_spouse,
        dependent_ages=profile["dependent_ages"],
        income=profile["income"],
        reform_params=reform_params,
        year=YEAR,
    )


def _aggregate_for_preset(
    reform_params: dict[str, Any],
    baseline_sim: Microsimulation,
) -> AggregateImpactResponse:
    reform = create_custom_reform(**reform_params, year=YEAR)
    impact = calculate_aggregate_impact(reform, year=YEAR, baseline_sim=baseline_sim)
    return AggregateImpactResponse(**impact)


async def _compute_preset(
    preset_id: str, baseline_sim: Microsimulation
) -> dict[str, Any]:
    reform_params = preset_reform_params(preset_id)
    print(f"[{preset_id}] aggregate microsim...")
    aggregate = _aggregate_for_preset(reform_params, baseline_sim)

    examples = []
    for profile in EXAMPLE_PROFILES:
        print(f"[{preset_id}] household: {profile['label']}")
        household = await _household_for_profile(profile, reform_params)
        examples.append(
            {
                "profile": profile,
                "household": household.model_dump(),
            }
        )

    return {
        "preset_id": preset_id,
        "year": YEAR,
        "reform_params": reform_params,
        "aggregate": aggregate.model_dump(),
        "examples": examples,
    }


async def main() -> None:
    out_dir = ROOT / "frontend" / "public" / "data" / "presets"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading baseline RI microsim from {RI_DATASET_PATH}...")
    baseline_sim = Microsimulation(dataset=RI_DATASET_PATH)
    print("Baseline loaded.")

    for preset_id in ("original", "revised", "enacted"):
        payload = await _compute_preset(preset_id, baseline_sim)
        out_path = out_dir / f"{preset_id}.json"
        out_path.write_text(json.dumps(payload, indent=2))
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
