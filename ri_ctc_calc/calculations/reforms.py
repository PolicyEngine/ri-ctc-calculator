"""PolicyEngine reform definitions for RI CTC scenarios."""

from policyengine_core.reforms import Reform
from typing import Optional, Dict


def create_ri_ctc_reform():
    """Create reform enabling RI CTC.

    Based on https://github.com/PolicyEngine/policyengine-us/pull/6643

    This reform activates the Rhode Island Child Tax Credit with customizable parameters:
    - Age limit: Maximum age for eligible children
    - Refundability: Can be non-refundable (cap=0), partially refundable, or fully refundable
    - AGI-based phase-out: Income-based reduction by filing status
    - Rhode Island residents only

    Returns:
        Reform: PolicyEngine reform object
    """
    return Reform.from_dict(
        {
            # Enable the RI CTC
            "gov.contrib.states.ri.ctc.in_effect": {
                "2026-01-01.2100-12-31": True
            },
            # Credit amount per eligible child
            "gov.contrib.states.ri.ctc.amount": {
                "2026-01-01.2100-12-31": 1000  # Example: $1,000 per child
            },
            # Maximum age for eligible children (default: 18)
            "gov.contrib.states.ri.ctc.age_limit": {
                "2026-01-01.2100-12-31": 18  # Children must be under this age
            },
            # Refundability cap
            # - Set to 0: Credit is non-refundable (can only reduce tax to zero)
            # - Set to positive value: That amount is fully refundable
            # - Set equal to amount above: Entire credit is fully refundable
            "gov.contrib.states.ri.ctc.refundability.cap": {
                "2026-01-01.2100-12-31": 0  # Non-refundable by default
            },
            # Phase-out rate (as decimal, e.g., 0.05 = 5% reduction per dollar over threshold)
            "gov.contrib.states.ri.ctc.phaseout.rate": {
                "2026-01-01.2100-12-31": 0  # No phase-out by default
            },
            # Phase-out thresholds by filing status (AGI levels where credit starts reducing)
            "gov.contrib.states.ri.ctc.phaseout.threshold.SINGLE": {
                "2026-01-01.2100-12-31": 0  # Set to 0 to disable phase-out
            },
            "gov.contrib.states.ri.ctc.phaseout.threshold.JOINT": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.ctc.phaseout.threshold.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.ctc.phaseout.threshold.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.ctc.phaseout.threshold.SEPARATE": {
                "2026-01-01.2100-12-31": 0
            },
            # Young child boost parameters
            "gov.contrib.states.ri.ctc.young_child_boost.amount": {
                "2026-01-01.2100-12-31": 0  # Additional boost per young child
            },
            "gov.contrib.states.ri.ctc.young_child_boost.age_limit": {
                "2026-01-01.2100-12-31": 6  # Children must be under this age for boost
            },
        },
        country_id="us",
    )


def create_ri_dependent_exemption_reform():
    """Create reform enabling RI dependent exemption changes.

    Based on https://github.com/PolicyEngine/policyengine-us/pull/6643

    This reform modifies the Rhode Island dependent exemption:
    - Amount: Overrides baseline dependent exemption amount
    - Age limit: Can restrict exemption to dependents under a certain age
    - Phase-out: Income-based reduction by filing status

    Note: This reform modifies ONLY dependent exemptions, not personal exemptions.
    Personal exemptions continue to use baseline Rhode Island rules.

    Returns:
        Reform: PolicyEngine reform object
    """
    return Reform.from_dict(
        {
            # Enable the dependent exemption reform
            "gov.contrib.states.ri.dependent_exemption.in_effect": {
                "2026-01-01.2100-12-31": True
            },
            # Dependent exemption amount per dependent
            # Note: Baseline is $5,050 (2025), $5,200 (2026) with IRS uprating/projections
            # Override only if you want a different amount than baseline
            "gov.contrib.states.ri.dependent_exemption.amount": {
                "2026-01-01.2100-12-31": 5200  # Use 2026 projected amount
            },
            # Enable age limit on dependent exemptions
            "gov.contrib.states.ri.dependent_exemption.age_limit.in_effect": {
                "2026-01-01.2100-12-31": True
            },
            # Age threshold for dependent exemptions (dependents must be under this age)
            "gov.contrib.states.ri.dependent_exemption.age_limit.threshold": {
                "2026-01-01.2100-12-31": 18  # Restrict to dependents under 18
            },
            # Phase-out rate (as decimal, e.g., 0.05 = 5% reduction per dollar over threshold)
            "gov.contrib.states.ri.dependent_exemption.phaseout.rate": {
                "2026-01-01.2100-12-31": 0  # No phase-out by default
            },
            # Phase-out thresholds by filing status (AGI levels where exemption starts reducing)
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.SINGLE": {
                "2026-01-01.2100-12-31": 0  # Set to 0 to disable phase-out
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.JOINT": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.SEPARATE": {
                "2026-01-01.2100-12-31": 0
            },
        },
        country_id="us",
    )


def create_combined_ri_reform():
    """Create combined reform with both RI CTC and dependent exemption changes.

    Based on https://github.com/PolicyEngine/policyengine-us/pull/6643

    This combines both reforms into a single reform object. All parameters from
    both individual reforms can be customized here.

    Returns:
        Reform: PolicyEngine reform object combining both reforms
    """
    return Reform.from_dict(
        {
            # ===== RI CTC Parameters =====
            "gov.contrib.states.ri.ctc.in_effect": {
                "2026-01-01.2100-12-31": True
            },
            "gov.contrib.states.ri.ctc.amount": {
                "2026-01-01.2100-12-31": 1000
            },
            "gov.contrib.states.ri.ctc.age_limit": {
                "2026-01-01.2100-12-31": 18
            },
            "gov.contrib.states.ri.ctc.refundability.cap": {
                "2026-01-01.2100-12-31": 0  # Non-refundable
            },
            "gov.contrib.states.ri.ctc.phaseout.rate": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.ctc.phaseout.threshold.SINGLE": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.ctc.phaseout.threshold.JOINT": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.ctc.phaseout.threshold.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.ctc.phaseout.threshold.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.ctc.phaseout.threshold.SEPARATE": {
                "2026-01-01.2100-12-31": 0
            },
            # Young child boost parameters
            "gov.contrib.states.ri.ctc.young_child_boost.amount": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.ctc.young_child_boost.age_limit": {
                "2026-01-01.2100-12-31": 6
            },
            # ===== Dependent Exemption Parameters =====
            "gov.contrib.states.ri.dependent_exemption.in_effect": {
                "2026-01-01.2100-12-31": True
            },
            "gov.contrib.states.ri.dependent_exemption.amount": {
                "2026-01-01.2100-12-31": 5200
            },
            "gov.contrib.states.ri.dependent_exemption.age_limit.in_effect": {
                "2026-01-01.2100-12-31": True
            },
            "gov.contrib.states.ri.dependent_exemption.age_limit.threshold": {
                "2026-01-01.2100-12-31": 18
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.rate": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.SINGLE": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.JOINT": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.SEPARATE": {
                "2026-01-01.2100-12-31": 0
            },
        },
        country_id="us",
    )


def create_custom_reform(
    # CTC parameters
    ctc_amount: float = 1000,
    ctc_age_limit: int = 18,
    ctc_refundability_cap: float = 0,
    ctc_phaseout_rate: float = 0,
    ctc_phaseout_thresholds: Optional[Dict[str, float]] = None,
    ctc_young_child_boost_amount: float = 0,
    ctc_young_child_boost_age_limit: int = 6,
    # Dependent exemption parameters
    enable_exemption_reform: bool = False,
    exemption_amount: float = 5200,
    exemption_age_limit_enabled: bool = True,
    exemption_age_threshold: int = 18,
    exemption_phaseout_rate: float = 0,
    exemption_phaseout_thresholds: Optional[Dict[str, float]] = None,
):
    """Create a custom reform with user-specified parameters.

    Args:
        ctc_amount: CTC amount per eligible child
        ctc_age_limit: Maximum age for CTC eligibility
        ctc_refundability_cap: Refundability cap (0=non-refundable, higher=more refundable)
        ctc_phaseout_rate: CTC phase-out rate (0=no phaseout)
        ctc_phaseout_thresholds: Dict of phase-out thresholds by filing status
        ctc_young_child_boost_amount: Additional boost amount per young child
        ctc_young_child_boost_age_limit: Maximum age for young child boost eligibility
        enable_exemption_reform: Whether to enable dependent exemption reform
        exemption_amount: Dependent exemption amount
        exemption_age_limit_enabled: Whether to enable age limit on exemptions
        exemption_age_threshold: Age threshold for exemptions
        exemption_phaseout_rate: Exemption phase-out rate
        exemption_phaseout_thresholds: Dict of exemption phase-out thresholds by filing status

    Returns:
        Reform: PolicyEngine reform object with custom parameters
    """
    # Default phase-out thresholds if not provided
    if ctc_phaseout_thresholds is None:
        ctc_phaseout_thresholds = {
            "SINGLE": 0,
            "JOINT": 0,
            "HEAD_OF_HOUSEHOLD": 0,
            "SURVIVING_SPOUSE": 0,
            "SEPARATE": 0,
        }

    if exemption_phaseout_thresholds is None:
        exemption_phaseout_thresholds = {
            "SINGLE": 0,
            "JOINT": 0,
            "HEAD_OF_HOUSEHOLD": 0,
            "SURVIVING_SPOUSE": 0,
            "SEPARATE": 0,
        }

    reform_dict = {
        # ===== RI CTC Parameters =====
        "gov.contrib.states.ri.ctc.in_effect": {
            "2026-01-01.2100-12-31": True
        },
        "gov.contrib.states.ri.ctc.amount": {
            "2026-01-01.2100-12-31": ctc_amount
        },
        "gov.contrib.states.ri.ctc.age_limit": {
            "2026-01-01.2100-12-31": ctc_age_limit
        },
        "gov.contrib.states.ri.ctc.refundability.cap": {
            "2026-01-01.2100-12-31": ctc_refundability_cap
        },
        "gov.contrib.states.ri.ctc.young_child_boost.amount": {
            "2026-01-01.2100-12-31": ctc_young_child_boost_amount
        },
        "gov.contrib.states.ri.ctc.young_child_boost.age_limit": {
            "2026-01-01.2100-12-31": ctc_young_child_boost_age_limit
        },
    }

    # Only add CTC phase-out if user has enabled it (rate > 0 or thresholds > 0)
    if ctc_phaseout_rate > 0 or any(v > 0 for v in ctc_phaseout_thresholds.values()):
        reform_dict.update({
            "gov.contrib.states.ri.ctc.phaseout.rate": {
                "2026-01-01.2100-12-31": ctc_phaseout_rate
            },
            "gov.contrib.states.ri.ctc.phaseout.threshold.SINGLE": {
                "2026-01-01.2100-12-31": ctc_phaseout_thresholds["SINGLE"]
            },
            "gov.contrib.states.ri.ctc.phaseout.threshold.JOINT": {
                "2026-01-01.2100-12-31": ctc_phaseout_thresholds["JOINT"]
            },
            "gov.contrib.states.ri.ctc.phaseout.threshold.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": ctc_phaseout_thresholds["HEAD_OF_HOUSEHOLD"]
            },
            "gov.contrib.states.ri.ctc.phaseout.threshold.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": ctc_phaseout_thresholds["SURVIVING_SPOUSE"]
            },
            "gov.contrib.states.ri.ctc.phaseout.threshold.SEPARATE": {
                "2026-01-01.2100-12-31": ctc_phaseout_thresholds["SEPARATE"]
            },
        })

    # Add dependent exemption parameters if enabled
    if enable_exemption_reform:
        exemption_params = {
            "gov.contrib.states.ri.dependent_exemption.in_effect": {
                "2026-01-01.2100-12-31": True
            },
            "gov.contrib.states.ri.dependent_exemption.amount": {
                "2026-01-01.2100-12-31": exemption_amount
            },
            "gov.contrib.states.ri.dependent_exemption.age_limit.in_effect": {
                "2026-01-01.2100-12-31": exemption_age_limit_enabled
            },
            "gov.contrib.states.ri.dependent_exemption.age_limit.threshold": {
                "2026-01-01.2100-12-31": exemption_age_threshold
            },
        }

        # Always set phase-out parameters explicitly to ensure proper behavior
        # Setting to 0 means "no phase-out", not setting means "use baseline rules"
        exemption_params.update({
            "gov.contrib.states.ri.dependent_exemption.phaseout.rate": {
                "2026-01-01.2100-12-31": exemption_phaseout_rate
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.SINGLE": {
                "2026-01-01.2100-12-31": exemption_phaseout_thresholds["SINGLE"]
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.JOINT": {
                "2026-01-01.2100-12-31": exemption_phaseout_thresholds["JOINT"]
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": exemption_phaseout_thresholds["HEAD_OF_HOUSEHOLD"]
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": exemption_phaseout_thresholds["SURVIVING_SPOUSE"]
            },
            "gov.contrib.states.ri.dependent_exemption.phaseout.threshold.SEPARATE": {
                "2026-01-01.2100-12-31": exemption_phaseout_thresholds["SEPARATE"]
            },
        })

        reform_dict.update(exemption_params)

    return Reform.from_dict(reform_dict, country_id="us")
