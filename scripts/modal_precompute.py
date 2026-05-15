"""Modal wrapper for ``scripts/precompute_presets.py``.

Use this when running the precompute locally is impractical (e.g.,
NumPy / Python version mismatch, 32 GiB RAM not available). The Modal
function reuses the HuggingFace cache volume that the live serve
function uses, so the dataset only downloads once across both jobs.

Run:

    modal run scripts/modal_precompute.py::run
"""

from __future__ import annotations

import json
from pathlib import Path

import modal

PROJECT_ROOT = Path(__file__).resolve().parent.parent

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "policyengine[us]==4.4.4",
        "fastapi>=0.110.0",
        "pydantic>=2.0",
        "pydantic-settings>=2.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
    )
    .add_local_dir(str(PROJECT_ROOT / "backend"), remote_path="/app/backend")
    .add_local_dir(str(PROJECT_ROOT / "ri_ctc_calc"), remote_path="/app/ri_ctc_calc")
    .add_local_dir(str(PROJECT_ROOT / "scripts"), remote_path="/app/scripts")
)

hf_cache = modal.Volume.from_name("ri-ctc-hf-cache", create_if_missing=True)

app = modal.App("ri-ctc-precompute")


@app.function(
    image=image,
    memory=32768,
    cpu=2.0,
    timeout=3600,
    volumes={"/root/.cache/huggingface": hf_cache},
)
def precompute() -> dict[str, str]:
    """Run the precompute and return the two JSON payloads keyed by preset_id."""
    import asyncio
    import sys

    sys.path.insert(0, "/app")
    sys.path.insert(0, "/app/backend")
    sys.path.insert(0, "/app/scripts")

    # Reuse the local script's coroutines verbatim.
    from precompute_presets import _compute_preset  # type: ignore
    from ri_ctc_calc.calculations.microsimulation import RI_DATASET_PATH
    from policyengine_us import Microsimulation

    print(f"Loading baseline from {RI_DATASET_PATH}...")
    baseline_sim = Microsimulation(dataset=RI_DATASET_PATH)

    async def _run() -> dict[str, dict]:
        return {
            "original": await _compute_preset("original", baseline_sim),
            "revised": await _compute_preset("revised", baseline_sim),
        }

    payloads = asyncio.run(_run())
    return {pid: json.dumps(p) for pid, p in payloads.items()}


@app.local_entrypoint()
def run() -> None:
    """Local entrypoint — invokes the Modal function and writes JSON locally."""
    out_dir = PROJECT_ROOT / "frontend" / "public" / "data" / "presets"
    out_dir.mkdir(parents=True, exist_ok=True)
    serialized = precompute.remote()
    for preset_id, raw in serialized.items():
        out_path = out_dir / f"{preset_id}.json"
        out_path.write_text(raw)
        print(f"Wrote {out_path}")
