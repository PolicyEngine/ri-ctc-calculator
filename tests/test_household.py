"""Tests for household building utilities."""

import pytest
from ri_ctc_calc.calculations.household import build_household_situation


def test_build_single_household():
    """Test building a single-person household."""
    situation = build_household_situation(
        age_head=35,
        age_spouse=None,
        dependent_ages=[],
        year=2026,
        with_axes=False,
    )

    assert "people" in situation
    assert "you" in situation["people"]
    assert situation["people"]["you"]["age"][2026] == 35
    assert situation["households"]["your household"]["state_name"][2026] == "RI"


def test_build_married_household():
    """Test building a married household."""
    situation = build_household_situation(
        age_head=35,
        age_spouse=33,
        dependent_ages=[],
        year=2026,
        with_axes=False,
    )

    assert "your partner" in situation["people"]
    assert situation["people"]["your partner"]["age"][2026] == 33
    assert "marital_units" in situation


def test_build_household_with_dependents():
    """Test building a household with dependents."""
    situation = build_household_situation(
        age_head=35,
        age_spouse=None,
        dependent_ages=[5, 10, 15],
        year=2026,
        with_axes=False,
    )

    assert "your first dependent" in situation["people"]
    assert "your second dependent" in situation["people"]
    assert "dependent_3" in situation["people"]
    assert situation["people"]["your first dependent"]["age"][2026] == 5
    assert situation["people"]["your second dependent"]["age"][2026] == 10
    assert situation["people"]["dependent_3"]["age"][2026] == 15


def test_build_household_with_axes():
    """Test building a household with income axes."""
    situation = build_household_situation(
        age_head=35,
        age_spouse=None,
        dependent_ages=[],
        year=2026,
        with_axes=True,
    )

    assert "axes" in situation
    assert len(situation["axes"]) == 1
    assert len(situation["axes"][0]) == 1
    assert situation["axes"][0][0]["name"] == "adjusted_gross_income"
    assert situation["axes"][0][0]["target"] == "tax_unit"
    assert situation["axes"][0][0]["count"] == 4_001
    assert situation["axes"][0][0]["min"] == 0
    assert situation["axes"][0][0]["max"] == 1_000_000
