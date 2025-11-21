"""Diagnostic script to test deployed app API with Test 9 parameters.

This script tests if the young child boost is being properly transmitted and processed
by the deployed application's API.
"""

import requests
import json

# You'll need to update this to the actual deployed URL
DEPLOYED_API_URL = "http://localhost:8080/api"  # UPDATE THIS to deployed URL
# Example: DEPLOYED_API_URL = "https://your-deployed-app.com/api"

print("=" * 80)
print("TEST 9 PARAMETERS - DEPLOYED API DIAGNOSTIC")
print("=" * 80)

# Test 9 parameters from notebook
test9_params = {
    "age_head": 35,
    "age_spouse": None,
    "dependent_ages": [5],  # One 5-year-old (eligible for young child boost)
    "income": 50000,
    "reform_params": {
        "ctc_amount": 300,
        "ctc_age_limit": 18,
        "ctc_refundability_cap": 999999,
        "ctc_phaseout_rate": 0.012,  # 1.2%
        "ctc_phaseout_thresholds": {
            "SINGLE": 250000,
            "JOINT": 250000,
            "HEAD_OF_HOUSEHOLD": 250000,
            "SURVIVING_SPOUSE": 250000,
            "SEPARATE": 250000
        },
        "ctc_young_child_boost_amount": 300,  # THIS IS THE KEY PARAMETER
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

print("\nRequest Payload:")
print(json.dumps(test9_params, indent=2))
print()

# Test 1: Household Benefit
print("=" * 80)
print("TEST 1: HOUSEHOLD BENEFIT ENDPOINT")
print("=" * 80)
print(f"\nEndpoint: {DEPLOYED_API_URL}/household-benefit-quick")
print()

try:
    response = requests.post(
        f"{DEPLOYED_API_URL}/household-benefit-quick",
        json=test9_params,
        timeout=60
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\nResponse:")
        print(json.dumps(data, indent=2))

        baseline = data.get('baseline', 0)
        reform = data.get('reform', 0)
        difference = data.get('difference', 0)
        ctc_component = data.get('ctc_component', 0)

        print("\n" + "-" * 80)
        print("ANALYSIS")
        print("-" * 80)
        print(f"\nBaseline net income: ${baseline:,.2f}")
        print(f"Reform net income: ${reform:,.2f}")
        print(f"Total benefit: ${difference:,.2f}")
        print(f"CTC component: ${ctc_component:,.2f}")

        print("\nExpected (from notebook Test 9):")
        print("  CTC base ($300) + Young child boost ($300) + Exemption ($0)")
        print("  Total benefit: ~$405 (accounting for tax interactions)")

        if ctc_component > 0:
            print(f"\nCTC Component Check:")
            print(f"  Actual: ${ctc_component:,.2f}")

            # Check if only getting base CTC
            if abs(ctc_component - 300) < 10:
                print("\n[ERROR] Only receiving BASE CTC ($300)")
                print("[ERROR] Young child boost ($300) is NOT being applied!")
                print("[ERROR] Expected CTC component: ~$600 (base + boost)")
            # Check if getting both
            elif abs(ctc_component - 600) < 10:
                print("\n[OK] Both base CTC and young child boost working!")
                print("[OK] CTC component matches expected $600")
            else:
                print(f"\n[WARNING] Unexpected CTC component value: ${ctc_component:,.2f}")
                print(f"[WARNING] Expected: $600 (base $300 + boost $300)")
    else:
        print(f"\n[ERROR] Request failed with status {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print(f"\n[ERROR] Could not connect to {DEPLOYED_API_URL}")
    print("Please update DEPLOYED_API_URL in this script to your actual deployed URL")
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")

# Test 2: Aggregate Impact
print("\n" + "=" * 80)
print("TEST 2: AGGREGATE IMPACT ENDPOINT")
print("=" * 80)
print(f"\nEndpoint: {DEPLOYED_API_URL}/aggregate-impact")
print()

aggregate_params = {
    "reform_params": test9_params["reform_params"]
}

print("Request Payload:")
print(json.dumps(aggregate_params, indent=2))
print()

try:
    response = requests.post(
        f"{DEPLOYED_API_URL}/aggregate-impact",
        json=aggregate_params,
        timeout=300  # Longer timeout for aggregate calculations
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\nResponse:")
        print(json.dumps(data, indent=2))

        total_cost = data.get('total_cost', 0)
        beneficiaries = data.get('beneficiaries', 0)
        avg_benefit = data.get('avg_benefit', 0)
        child_poverty_change = data.get('child_poverty_percent_change', 0)

        print("\n" + "-" * 80)
        print("ANALYSIS")
        print("-" * 80)
        print(f"\nActual (from API):")
        print(f"  Total Cost: ${total_cost:,.0f}")
        print(f"  Beneficiaries: {beneficiaries:,}")
        print(f"  Average Benefit: ${avg_benefit:,.2f}")
        print(f"  Child Poverty Change: {child_poverty_change:,.1f}%")

        print(f"\nExpected (from notebook Test 9):")
        print(f"  Total Cost: $51,199,974")
        print(f"  Beneficiaries: 117,829")
        print(f"  Average Benefit: $428.01")
        print(f"  Child Poverty Change: -3.1%")

        print(f"\nComparison:")
        cost_diff = total_cost - 51199974
        avg_diff = avg_benefit - 428.01

        print(f"  Cost difference: ${cost_diff:,.0f}")
        print(f"  Average benefit difference: ${avg_diff:,.2f}")

        # If cost is around $32.6M, young child boost is missing
        if 32000000 < total_cost < 33000000:
            print("\n[ERROR] Total cost matches app WITHOUT young child boost (~$32.6M)")
            print("[ERROR] Young child boost is NOT being applied in aggregate calculations!")
            print("[ERROR] Expected cost with boost: ~$51.2M")
            print("[ERROR] Missing impact: ~$18.6M")
        elif 50000000 < total_cost < 52000000:
            print("\n[OK] Total cost matches expected with young child boost (~$51.2M)")
            print("[OK] Young child boost is working in aggregate calculations!")
        else:
            print(f"\n[WARNING] Unexpected total cost: ${total_cost:,.0f}")
            print(f"[WARNING] Expected: ~$51.2M (with boost) or ~$32.6M (without boost)")

    else:
        print(f"\n[ERROR] Request failed with status {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print(f"\n[ERROR] Could not connect to {DEPLOYED_API_URL}")
    print("Please update DEPLOYED_API_URL in this script to your actual deployed URL")
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")

print("\n" + "=" * 80)
print("DIAGNOSTIC SUMMARY")
print("=" * 80)
print("\nThis script tests if ctc_young_child_boost_amount is being:")
print("  1. Sent by the frontend in the API request")
print("  2. Received by the backend")
print("  3. Applied correctly in calculations")
print("\nIf you see errors above, the young child boost is not working in the deployed app.")
print("If you see [OK] messages, the young child boost is working correctly.")
print()
