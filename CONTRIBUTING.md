# Contributing to RI CTC Calculator

Thank you for your interest in contributing to the Rhode Island Child Tax Credit Calculator!

## Development Setup

```bash
# Clone the repository
git clone <repo-url>
cd ri-ctc-calculator

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"
```

## Running the App

```bash
streamlit run app.py
```

## Running Tests

```bash
pytest tests/
```

## Code Style

We use Black for code formatting:

```bash
black .
```

## Making Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and formatting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Project Structure

```
ri-ctc-calculator/
├── app.py                      # Main Streamlit application
├── ri_ctc_calc/               # Calculator package
│   ├── __init__.py
│   └── calculations/          # Calculation modules
│       ├── __init__.py
│       ├── household.py       # Household building utilities
│       ├── ctc.py            # CTC calculation functions
│       └── reforms.py        # Reform definitions
└── tests/                     # Test files
```

## Questions?

Feel free to open an issue for any questions or concerns.
