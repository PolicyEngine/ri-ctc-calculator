"""PolicyEngine reform definitions for RI CTC scenarios."""

from policyengine_core.reforms import Reform


def create_ri_ctc_reform():
    """Create reform enabling RI CTC.

    Based on https://github.com/PolicyEngine/policyengine-us/pull/6643

    This reform activates the Rhode Island Child Tax Credit with the following parameters:
    - Age limit: 18 years
    - Non-refundable credit
    - AGI-based phase-out
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
            # Set CTC amount (placeholder - will need actual values from policy)
            # This should be updated based on the actual reform proposal
            "gov.contrib.states.ri.ctc.amount": {
                "2026-01-01.2100-12-31": 1000  # Example amount - update as needed
            },
            # Age limit (already set in parameters to 18, but can override if needed)
            # Refundability cap remains at $0 (non-refundable)
            # Phase-out parameters (update as needed based on actual policy)
        },
        country_id="us",
    )


def create_ri_dependent_exemption_reform():
    """Create reform enabling RI dependent exemption changes.

    Based on https://github.com/PolicyEngine/policyengine-us/pull/6643

    This reform modifies the Rhode Island dependent exemption:
    - Amount: $5,050 (2025), $5,100 (2026)
    - Age limit: 18 years

    Returns:
        Reform: PolicyEngine reform object
    """
    return Reform.from_dict(
        {
            # Enable the dependent exemption reform
            "gov.contrib.states.ri.dependent_exemption.in_effect": {
                "2026-01-01.2100-12-31": True
            },
            # Enable age limit
            "gov.contrib.states.ri.dependent_exemption.age_limit.in_effect": {
                "2026-01-01.2100-12-31": True
            },
        },
        country_id="us",
    )


def create_combined_ri_reform():
    """Create combined reform with both RI CTC and dependent exemption changes.

    Returns:
        Reform: PolicyEngine reform object combining both reforms
    """
    return Reform.from_dict(
        {
            # Enable RI CTC
            "gov.contrib.states.ri.ctc.in_effect": {
                "2026-01-01.2100-12-31": True
            },
            "gov.contrib.states.ri.ctc.amount": {
                "2026-01-01.2100-12-31": 1000  # Update as needed
            },
            # Enable dependent exemption
            "gov.contrib.states.ri.dependent_exemption.in_effect": {
                "2026-01-01.2100-12-31": True
            },
            "gov.contrib.states.ri.dependent_exemption.age_limit.in_effect": {
                "2026-01-01.2100-12-31": True
            },
        },
        country_id="us",
    )
