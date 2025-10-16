# Rhode Island Child Tax Credit Calculator

Compare household impacts with and without Rhode Island CTC reform.

## Overview

This calculator models the Rhode Island Child Tax Credit reform proposal, showing how different household configurations would be affected by the CTC implementation. The calculator uses PolicyEngine US's microsimulation model to provide accurate benefit calculations.

**Key Features:**
- **Baseline vs. Reform**: Compare household finances with and without RI CTC
- **Income Analysis**: See how credits change across income levels
- **Household Flexibility**: Model different family configurations
- **RI-Specific**: Focused on Rhode Island residents

## Quick Start

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open at http://localhost:8501

## Rhode Island CTC Reform Parameters

Based on [PolicyEngine US PR #6643](https://github.com/PolicyEngine/policyengine-us/pull/6643):

- **Eligibility**: Children under age 18
- **Credit Structure**: Non-refundable child tax credit
- **Phase-out**: Based on AGI (Adjusted Gross Income)
- **State**: Rhode Island residents only

## Project Structure

```
.
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project configuration
├── ri_ctc_calc/                    # Calculator package
│   ├── __init__.py
│   └── calculations/               # Calculation modules
│       ├── __init__.py
│       ├── household.py            # Household building utilities
│       ├── ctc.py                  # CTC calculation functions
│       └── reforms.py              # Reform definitions
└── tests/                          # Test files
```

## Development

```bash
# Run tests
pytest tests/

# Format code
black .
```

## Technical Details

Built with:
- **[PolicyEngine US](https://policyengine.org)**: Open-source tax-benefit microsimulation
- **[Streamlit](https://streamlit.io)**: Interactive web interface
- **[Plotly](https://plotly.com)**: Data visualization

## License

Open source - see PolicyEngine US license for underlying calculations.

## Credits

Calculations powered by [PolicyEngine US](https://github.com/PolicyEngine/policyengine-us)
