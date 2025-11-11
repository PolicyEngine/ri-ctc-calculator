# Rhode Island Child Tax Credit Calculator

Compare household impacts with and without Rhode Island CTC reform.

## Overview

This calculator models the Rhode Island Child Tax Credit reform proposal, showing how different household configurations would be affected by the CTC implementation. The calculator uses PolicyEngine US's microsimulation model to provide accurate benefit calculations.

**Key Features:**
- **Baseline vs. Reform**: Compare household finances with and without RI CTC
- **Income Analysis**: See how credits change across income levels
- **Household Flexibility**: Model different family configurations
- **RI-Specific**: Focused on Rhode Island residents

## Architecture

This project has two main components:
- **Backend**: FastAPI REST API (Python)
- **Frontend**: Next.js/React application (TypeScript)
- **Legacy**: Streamlit app (still available but deprecated)

## Quick Start

### Prerequisites

- **Python 3.10+** (Python 3.11 recommended)
- **Node.js 21+** (for frontend)
- **Windows**: Long path support enabled (see [Windows Setup](#windows-setup))

### Run the Full Application

You need to run both the backend and frontend:

#### Terminal 1: Backend

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Backend will be available at:
- **API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs

**Note**: First startup may take 30-60 seconds to download and load the RI microsimulation dataset from HuggingFace.

#### Terminal 2: Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start the Next.js dev server
npm run dev
```

Frontend will be available at:
- **App**: http://localhost:3000

### Legacy Streamlit App (Deprecated)

The original Streamlit version is still available but no longer maintained:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

The app will open at http://localhost:8501

## Rhode Island CTC Reform Parameters

Based on [PolicyEngine US PR #6643](https://github.com/PolicyEngine/policyengine-us/pull/6643):

- **Eligibility**: Children under age 18
- **Credit Structure**: Non-refundable child tax credit
- **Phase-out**: Based on AGI (Adjusted Gross Income)
- **State**: Rhode Island residents only

## Windows Setup

On Windows, you need to enable long path support for the PolicyEngine dataset:

1. **Enable Long Paths in Windows** (requires admin):
   ```powershell
   # Run PowerShell as Administrator
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```

2. **Enable Long Paths in Git** (if cloning the repo):
   ```bash
   git config --system core.longpaths true
   ```

3. **Restart your terminal** after making these changes.

Without long path support, you'll get `ModuleNotFoundError` when importing `policyengine_us`.

## Project Structure

```
.
├── backend/                        # FastAPI backend
│   ├── app/
│   │   ├── main.py                # FastAPI application
│   │   ├── api/
│   │   │   ├── routes/            # API endpoints
│   │   │   └── models/            # Request/response models
│   │   ├── core/
│   │   │   ├── config.py          # Configuration
│   │   │   └── dataset.py         # Dataset manager
│   │   └── services/
│   │       └── calculator.py      # Business logic
│   ├── requirements.txt           # Python dependencies
│   └── Dockerfile                 # Production deployment
├── frontend/                       # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx             # Root layout
│   │   ├── page.tsx               # Main page
│   │   └── globals.css            # Global styles
│   ├── components/                # React components
│   │   ├── HouseholdForm.tsx
│   │   ├── ImpactAnalysis.tsx
│   │   └── AggregateImpact.tsx
│   ├── hooks/                     # React hooks
│   ├── lib/
│   │   ├── api.ts                 # API client
│   │   └── types.ts               # TypeScript types
│   ├── package.json
│   └── Dockerfile                 # Production deployment
├── ri_ctc_calc/                   # Calculator package (shared)
│   ├── __init__.py
│   └── calculations/              # Calculation modules
│       ├── __init__.py
│       ├── household.py           # Household building
│       ├── ctc.py                 # CTC calculations
│       ├── microsimulation.py     # Aggregate calculations
│       └── reforms.py             # Reform definitions
├── app.py                         # Legacy Streamlit app
├── requirements.txt               # Python dependencies (legacy)
└── tests/                         # Test files
```

## API Endpoints

The backend provides the following REST API endpoints:

### `POST /api/household-impact`
Calculate household-specific impact across income range.

**Request**:
```json
{
  "age_head": 35,
  "age_spouse": null,
  "dependent_ages": [5, 8],
  "income": 50000,
  "reform_params": {
    "ri_ctc_amount": 1000,
    "phase_out_start": 200000,
    "phase_out_rate": 0.05
  }
}
```

### `POST /api/aggregate-impact`
Calculate statewide impact using RI microsimulation dataset.

**Note**: This endpoint takes **~90 seconds** to compute due to microsimulation calculations.

**Request**:
```json
{
  "reform_params": {
    "ri_ctc_amount": 1000,
    "phase_out_start": 200000,
    "phase_out_rate": 0.05
  }
}
```

### `GET /api/health`
Health check endpoint.

### `GET /api/dataset-summary`
Get RI dataset summary statistics.

**Interactive API Documentation**: http://localhost:8080/docs

## Troubleshooting

### "Network Error" on Frontend

**Problem**: Frontend shows "Network Error" when calculating aggregate impact.

**Cause**: The aggregate calculation takes ~90 seconds, which was exceeding the default 30-second timeout.

**Solution**: The timeout has been increased to 120 seconds in `frontend/lib/api.ts:27`. If you still see this error:
1. Check that the backend is running on port 8080
2. Check backend logs for errors
3. The first calculation may take longer (~2 minutes) as the dataset loads

### `ModuleNotFoundError: No module named 'policyengine_us.variables'`

**Problem**: Backend fails to start with module not found error.

**Cause**: Windows long path limit preventing proper package installation.

**Solution**: See [Windows Setup](#windows-setup) section above.

### Port Already in Use

**Problem**: `Error: Address already in use`

**Solution**:
```bash
# Windows - Find and kill process on port 8080
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Or use a different port
python -m uvicorn app.main:app --reload --port 8081
```

### Frontend Can't Connect to Backend

**Problem**: Frontend shows connection errors.

**Check**:
1. Backend is running: http://localhost:8080/api/health
2. CORS is configured correctly (already set up for localhost:3000)
3. Firewall isn't blocking the ports

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests (if available)
cd frontend
npm test
```

### Code Formatting

```bash
# Python
black .
isort .

# JavaScript/TypeScript
cd frontend
npm run lint
```

## Technical Details

Built with:
- **Backend**:
  - **[FastAPI](https://fastapi.tiangolo.com/)**: Modern Python web framework
  - **[PolicyEngine US](https://policyengine.org)**: Open-source tax-benefit microsimulation
  - **[Pydantic](https://pydantic.dev/)**: Data validation
  - **[Uvicorn](https://www.uvicorn.org/)**: ASGI server
- **Frontend**:
  - **[Next.js 14](https://nextjs.org/)**: React framework
  - **[React Query](https://tanstack.com/query)**: Data fetching and caching
  - **[Recharts](https://recharts.org/)**: Data visualization
  - **[Tailwind CSS](https://tailwindcss.com/)**: Styling
  - **[TypeScript](https://www.typescriptlang.org/)**: Type safety
- **Legacy**:
  - **[Streamlit](https://streamlit.io)**: Interactive web interface (deprecated)
  - **[Plotly](https://plotly.com)**: Data visualization

## License

Open source - see PolicyEngine US license for underlying calculations.

## Credits

Calculations powered by [PolicyEngine US](https://github.com/PolicyEngine/policyengine-us)
