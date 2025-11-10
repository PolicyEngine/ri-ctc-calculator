# RI CTC Calculator - Deployment Guide

## ✅ What's Been Built

### Backend (FastAPI)
- **Complete REST API** with 4 endpoints:
  - `POST /api/household-impact` - Calculate household-specific impact
  - `POST /api/aggregate-impact` - Calculate statewide impact
  - `GET /api/dataset-summary` - Get RI dataset statistics
  - `GET /api/health` - Health check

- **Features**:
  - Dataset caching (loads RI.h5 once at startup)
  - Pydantic validation for all requests/responses
  - CORS configured for frontend
  - Clean service layer wrapping existing calculations
  - Production-ready error handling

- **File Structure**:
  ```
  backend/
  ├── app/
  │   ├── main.py              # FastAPI application
  │   ├── api/
  │   │   ├── routes/
  │   │   │   ├── household.py # Household endpoints
  │   │   │   ├── aggregate.py # Aggregate endpoints
  │   │   │   └── health.py    # Health check
  │   │   └── models/
  │   │       ├── requests.py  # Request models
  │   │       └── responses.py # Response models
  │   ├── services/
  │   │   └── calculator.py    # Business logic
  │   └── core/
  │       ├── config.py        # Configuration
  │       └── dataset.py       # Dataset manager
  ├── requirements.txt
  └── Dockerfile
  ```

### Frontend (Next.js + React)
- **Complete UI** matching Streamlit functionality:
  - Household configuration form
  - Impact analysis with charts (Recharts)
  - Statewide aggregate impact
  - Tab navigation
  - Responsive design (Tailwind CSS)

- **Features**:
  - React Query for caching and state management
  - TypeScript for type safety
  - API client with Axios
  - Custom hooks for data fetching
  - Clean component architecture

- **File Structure**:
  ```
  frontend/
  ├── app/
  │   ├── layout.tsx           # Root layout with React Query
  │   ├── page.tsx             # Main calculator page
  │   └── globals.css          # Global styles
  ├── components/
  │   ├── HouseholdForm.tsx    # Configuration sidebar
  │   ├── ImpactAnalysis.tsx   # Impact charts & metrics
  │   └── AggregateImpact.tsx  # Statewide analysis
  ├── hooks/
  │   ├── useHouseholdImpact.ts
  │   └── useAggregateImpact.ts
  ├── lib/
  │   ├── api.ts               # API client
  │   └── types.ts             # TypeScript types
  ├── package.json
  ├── tsconfig.json
  ├── tailwind.config.js
  └── Dockerfile
  ```

## 🚀 Local Development

### Backend

```bash
# 1. Navigate to backend
cd backend

# 2. Install dependencies (virtual environment optional but recommended)
pip install -r requirements.txt

# 3. Run FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# API will be available at http://localhost:8080
# API docs at http://localhost:8080/docs
```

**Note**: First startup takes 30-60 seconds to download the RI dataset from HuggingFace.

### Frontend

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Run Next.js dev server
npm run dev

# Frontend will be available at http://localhost:3000
```

## 📦 Deployment to Google Cloud Run

### Step 1: Create GCP Project

```bash
# Create new project
gcloud projects create ri-ctc-calculator \
  --name="RI Child Tax Credit Calculator"

# Set as active project
gcloud config set project ri-ctc-calculator

# Link billing account (replace with your billing account ID)
BILLING_ACCOUNT=$(gcloud billing accounts list --format="value(name)" --limit=1)
gcloud billing projects link ri-ctc-calculator \
  --billing-account=$BILLING_ACCOUNT

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

### Step 2: Deploy Backend

```bash
# Navigate to project root
cd /Users/pavelmakarchuk/ri-ctc-calculator

# Deploy backend (Cloud Run builds from Dockerfile automatically)
gcloud run deploy ri-ctc-backend \
  --source ./backend \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 1 \
  --allow-unauthenticated \
  --project ri-ctc-calculator

# Get backend URL
BACKEND_URL=$(gcloud run services describe ri-ctc-backend \
  --region us-central1 \
  --format="value(status.url)")

echo "Backend deployed at: $BACKEND_URL"
```

**Important**: Min instances = 1 keeps the dataset loaded in memory (no cold starts).

### Step 3: Deploy Frontend

```bash
# Deploy frontend with backend URL as environment variable
gcloud run deploy ri-ctc-frontend \
  --source ./frontend \
  --region us-central1 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --max-instances 10 \
  --min-instances 0 \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_URL=$BACKEND_URL \
  --project ri-ctc-calculator

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe ri-ctc-frontend \
  --region us-central1 \
  --format="value(status.url)")

echo "Frontend deployed at: $FRONTEND_URL"
```

### Step 4: Update CORS (if needed)

If you get CORS errors, update backend CORS settings:

```python
# backend/app/core/config.py
cors_origins: List[str] = [
    "http://localhost:3000",
    "https://ri-ctc-frontend-HASH-uc.a.run.app",  # Add your frontend URL
]
```

Then redeploy backend:
```bash
gcloud run deploy ri-ctc-backend --source ./backend --region us-central1
```

## 💰 Cost Estimates

**Backend** (4GB RAM, 1 min instance):
- Always-on: ~$25-35/month
- Per-request: $0.40 per 100K requests

**Frontend** (512MB RAM, 0 min instances):
- Scales to zero: ~$0-10/month
- Per-request: $0.10 per 100K requests

**Total**: ~$25-45/month

## 🧪 Testing

### Test Backend API

```bash
# Health check
curl $BACKEND_URL/api/health

# Test household impact
curl -X POST $BACKEND_URL/api/household-impact \
  -H "Content-Type: application/json" \
  -d '{
    "age_head": 35,
    "age_spouse": null,
    "dependent_ages": [5],
    "income": 50000,
    "reform_params": {
      "ctc_amount": 1000,
      "ctc_age_limit": 18,
      "ctc_refundability_cap": 0,
      "ctc_phaseout_rate": 0,
      "ctc_phaseout_thresholds": {
        "SINGLE": 0,
        "JOINT": 0,
        "HEAD_OF_HOUSEHOLD": 0,
        "SURVIVING_SPOUSE": 0,
        "SEPARATE": 0
      },
      "enable_exemption_reform": false,
      "exemption_amount": 5200,
      "exemption_age_limit_enabled": true,
      "exemption_age_threshold": 18,
      "exemption_phaseout_rate": 0,
      "exemption_phaseout_thresholds": null
    }
  }'
```

### Test Frontend

1. Open $FRONTEND_URL in browser
2. Configure household
3. Click "Calculate Impact"
4. Verify charts and metrics display
5. Check "Statewide Impact" tab

## 📝 Next Steps

1. **Styling** - Update to match policyengine-app-v2 styling
2. **Custom Domain** - Map to ctc.policyengine.org
3. **Monitoring** - Set up Cloud Monitoring alerts
4. **CI/CD** - Add GitHub Actions for auto-deploy
5. **Optimization** - Add caching layers (Redis)

## 🔧 Maintenance

### View Logs

```bash
# Backend logs
gcloud run services logs tail ri-ctc-backend --region us-central1

# Frontend logs
gcloud run services logs tail ri-ctc-frontend --region us-central1
```

### Update Deployment

```bash
# After code changes, simply redeploy
gcloud run deploy ri-ctc-backend --source ./backend --region us-central1
gcloud run deploy ri-ctc-frontend --source ./frontend --region us-central1
```

### Scale Resources

```bash
# Increase backend memory if needed
gcloud run services update ri-ctc-backend \
  --memory 8Gi \
  --region us-central1
```

## ✅ Functionality Preserved

All Streamlit features have been preserved:
- ✅ Household configuration (income, married, dependents)
- ✅ Reform customization (CTC + exemption parameters)
- ✅ Income sweep charts
- ✅ Benefit breakdown (CTC vs exemption)
- ✅ Aggregate/statewide impact
- ✅ Poverty analysis
- ✅ Income bracket distribution
- ✅ Dataset summary statistics

## 🎨 Styling Notes

Currently using basic Tailwind CSS. To match policyengine-app-v2:
1. Copy color scheme from policyengine-app-v2
2. Update tailwind.config.js
3. Create matching UI components
4. Adjust spacing and typography

Let me know if you want help with this!
