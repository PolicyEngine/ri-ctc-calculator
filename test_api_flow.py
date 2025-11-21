"""Test the API flow to verify young child boost is transmitted correctly."""

import requests
import json

API_URL = "http://localhost:8080/api"

print("=" * 80)
print("Testing API Flow for Young Child Boost")
print("=" * 80)

# Test household configuration
household_request = {
    "age_head": 35,
    "age_spouse": None,
    "dependent_ages": [5],  # 5-year-old child
    "income": 50000,
    "reform_params": {
        "ctc_amount": 312,
        "ctc_age_limit": 18,
        "ctc_refundability_cap": 999999,
        "ctc_phaseout_rate": 0,
        "ctc_phaseout_thresholds": {
            "SINGLE": 0,
            "JOINT": 0,
            "HEAD_OF_HOUSEHOLD": 0,
            "SURVIVING_SPOUSE": 0,
            "SEPARATE": 0
        },
        "ctc_young_child_boost_amount": 1000,  # THIS IS THE KEY PARAMETER
        "ctc_young_child_boost_age_limit": 6,
        "enable_exemption_reform": True,
        "exemption_amount": 0,
        "exemption_age_limit_enabled": True,
        "exemption_age_threshold": 18,
        "exemption_phaseout_rate": 0,
        "exemption_phaseout_thresholds": {
            "SINGLE": 0,
            "JOINT": 0,
            "HEAD_OF_HOUSEHOLD": 0,
            "SURVIVING_SPOUSE": 0,
            "SEPARATE": 0
        }
    }
}

print("\nRequest payload:")
print(json.dumps(household_request, indent=2))
print()

try:
    print("Sending request to /api/household-benefit-quick...")
    response = requests.post(
        f"{API_URL}/household-benefit-quick",
        json=household_request,
        timeout=60
    )

    print(f"Status code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\nResponse:")
        print(json.dumps(data, indent=2))

        print("\n" + "=" * 80)
        print("ANALYSIS")
        print("=" * 80)

        baseline = data.get('baseline', 0)
        reform = data.get('reform', 0)
        difference = data.get('difference', 0)
        ctc_component = data.get('ctc_component', 0)
        exemption_benefit = data.get('exemption_tax_benefit', 0)

        print(f"\nBaseline net income: ${baseline:,.2f}")
        print(f"Reform net income: ${reform:,.2f}")
        print(f"Total difference: ${difference:,.2f}")
        print(f"\nBreakdown:")
        print(f"  CTC component: ${ctc_component:,.2f}")
        print(f"  Exemption benefit: ${exemption_benefit:,.2f}")

        print(f"\nExpected breakdown (from notebook):")
        print(f"  CTC base ($312) + Young child boost ($1,000) = $1,312")
        print(f"  Exemption ($0 set) = -$195")
        print(f"  Total expected = $1,117")

        print(f"\nActual total: ${difference:,.2f}")
        print(f"Match expected: {abs(difference - 1117) < 10}")

        if ctc_component > 0:
            print(f"\nCTC component breakdown:")
            print(f"  Expected: $1,312 (base $312 + boost $1,000)")
            print(f"  Actual: ${ctc_component:,.2f}")
            print(f"  Match: {abs(ctc_component - 1312) < 10}")

            if abs(ctc_component - 312) < 10:
                print("\n❌ WARNING: Only receiving BASE CTC ($312)")
                print("❌ Young child boost ($1,000) is NOT being applied!")
            elif abs(ctc_component - 1312) < 10:
                print("\n✓ SUCCESS: Both base CTC and young child boost are working!")

    else:
        print(f"Error: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to API at " + API_URL)
    print("Is the backend server running?")
    print("Start it with: cd backend && uvicorn app.main:app --reload")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
