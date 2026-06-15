"""Modal entrypoint that hosts the existing FastAPI app for the custom-
reform path.

This replaces the GCP Cloud Run deployment. Preset clicks bypass this
service entirely (they read precomputed JSON from
``frontend/public/data/presets/``); only the slider/custom-reform branch
hits this endpoint.

Deploy:

    modal deploy scripts/modal_serve.py

Run locally against the deployed image (good for first-load testing):

    modal serve scripts/modal_serve.py

The deployed URL has the shape
``https://<workspace>--ri-ctc-api-fastapi-app.modal.run`` — set that as
``NEXT_PUBLIC_API_URL`` in the Vercel project.
"""

from __future__ import annotations

from pathlib import Path

import modal

# -----------------------------------------------------------------------------
# Image
# -----------------------------------------------------------------------------
# Mirror of ``requirements.txt`` plus the package layout under ``backend/``
# and ``ri_ctc_calc/``. We pin ``policyengine-us`` so live calculations use
# the #8639 model behavior and stay ahead of RI CTC entering baseline.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "policyengine-us==1.729.2",
        "fastapi>=0.110.0",
        "uvicorn>=0.27.0",
        "pydantic>=2.0",
        "pydantic-settings>=2.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
    )
    .add_local_dir(str(PROJECT_ROOT / "backend"), remote_path="/app/backend")
    .add_local_dir(str(PROJECT_ROOT / "ri_ctc_calc"), remote_path="/app/ri_ctc_calc")
)

# Persistent volume mounted at the HuggingFace cache so RI.h5 doesn't
# re-download on every cold start.
hf_cache = modal.Volume.from_name("ri-ctc-hf-cache", create_if_missing=True)

app = modal.App("ri-ctc-api")


@app.function(
    image=image,
    memory=32768,  # 32 GiB — Microsimulation peaks past 8 GiB on RI.h5
    cpu=2.0,
    timeout=600,
    volumes={"/root/.cache/huggingface": hf_cache},
    scaledown_window=600,  # 10 min idle before scale-to-zero
    min_containers=0,
)
@modal.asgi_app(label="ri-ctc-api")
def fastapi_app():
    """Expose ``backend.app.main:app`` as a Modal ASGI app."""
    import sys

    sys.path.insert(0, "/app")
    sys.path.insert(0, "/app/backend")

    from app.main import app as fastapi  # noqa: E402

    return fastapi
