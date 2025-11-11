# Quick Start Guide

**Get the app running in under 5 minutes.**

## Prerequisites

- Python 3.10+ installed
- Node.js 21+ installed
- Windows: Long paths enabled (see below)

## Windows Users: Enable Long Paths First!

```powershell
# Run PowerShell as Administrator and run:
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force

# Then restart your terminal
```

**Why?** The PolicyEngine dataset has long file paths that Windows blocks by default. Without this, you'll get `ModuleNotFoundError`.

## Running the App

You need TWO terminals open:

### Terminal 1: Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

✅ Backend ready at: http://localhost:8080
📖 API docs at: http://localhost:8080/docs

**Note**: First startup takes 30-60 seconds to download the RI dataset.

### Terminal 2: Frontend

```bash
cd frontend
npm install
npm run dev
```

✅ App ready at: http://localhost:3000

## That's It!

Open http://localhost:3000 in your browser and start calculating.

## Troubleshooting

### "ModuleNotFoundError: No module named 'policyengine_us.variables'"
→ You forgot to enable long paths. See Windows section above.

### "Network Error" on aggregate calculations
→ Normal! These calculations take ~90 seconds. Be patient.

### Port already in use
```bash
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

## What's Running?

- **Backend** (port 8080): FastAPI server with PolicyEngine calculations
- **Frontend** (port 3000): Next.js React app with nice UI

Both need to be running for the app to work.

## Next Steps

- See [README.md](README.md) for full documentation
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production deployment
- See [API docs](http://localhost:8080/docs) for API details
