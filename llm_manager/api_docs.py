"""FastAPI application exposing the model-manager JSON API with auto-generated
documentation (:code:`/docs` - Swagger UI, :code:`/redoc` - ReDoc).

The routes mirror the JSON endpoints of the Flask app; the Pydantic models are
the request/response schemas consumed by the auto-generated documentation.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from .config_store import load_config
from .configurator import build_config
from .hardware import detect_hardware
from .loader import discover_models
from .tuning_store import (
    add_dir,
    delete_dir,
    save_tuning_profile,
)

app = FastAPI(
    title="LLM Manager API",
    description=(
        "JSON API for the local LLM model manager.\n\n"
        "Model registry and hardware-aware configuration are generated on the "
        "fly from the model directories, the llama-swap `config.yaml`, and the "
        "context-verification metadata. All `POST` request bodies are "
        "form-encoded (`application/x-www-form-urlencoded`), matching the "
        "legacy Flask app."
    ),
    version="0.1.0",
)

# --------------------------------------------------------------------------- #
# Request / response models
# --------------------------------------------------------------------------- #
class ModelOut(BaseModel):
    """A single LLM model in the registry."""

    name: str
    full_name: str
    size_gb: float = 0.0
    context_length: int = 0
    quantization: str = "Q4_K_M"
    precision: str = "gguf"
    device: str = "auto"
    status: str = "available"
    version: str = ""
    model_id: str = ""
    hardware_constraint: str = ""
    memory_safe_context: int = 0
    parameter_label: str = ""
    path: str = ""
    max_tokens: int = 512
    hardware: str | None = None
    extra: dict = Field(default_factory=dict)


class ConfigProfileOut(BaseModel):
    """A generated configuration profile for a single model."""

    model_id: str
    model_name: str
    quantization: str
    size_gb: float = 0.0
    ctx_size: int = 0
    fit_status: str = "fits"
    vram_needed: float = 0.0
    device: str = "cpu"
    path: str = ""
    kv_gb: float = 0.0
    kv_bits: int = 8
    vram_for_model: float = 0.0
    ram_gb: float = 0.0
    generated_at: str = ""
    temp: float = 0.7
    top_k: int = 40
    top_p: float = 0.9
    n_predict: int = 512
    n_gpu_layers: str = "all"
    max_tokens: int = 512


class TuningProfileOut(BaseModel):
    """A user-editable llama.cpp tuning knob set (the persisted profile)."""

    model_key: str
    model_name: str
    quantization: str = "Q4_K_M"
    n_gpu_layers: str = "all"
    ctx_size: int = 0
    temp: float = 0.7
    top_k: int = 40
    top_p: float = 0.9
    n_predict: int = 512
    n_threads: int = 4
    path: str = ""
    created_at: str = ""
    updated_at: str = ""


class HardwareSpecOut(BaseModel):
    cpu_cores: int = 0
    gpu_name: str = ""
    gpu_memory_gb: float = 0.0
    gpu_free_gb: float = 0.0
    system_ram_gb: float = 0.0
    system_disk_gb: float = 0.0


class ConfigOut(BaseModel):
    hardware: HardwareSpecOut
    profiles: list[ConfigProfileOut] = Field(default_factory=list)
    models: list[ModelOut] = Field(default_factory=list)
    generated_at: str = ""
    base_models_dir: str = ""
    ram_limit_gb: float | None = None
    total_vram_gb: float = 0.0
    free_vram_gb: float = 0.0
    models_count: int = 0
    profiles_count: int = 0


class TuningSaveResponse(BaseModel):
    ok: bool
    profile: TuningProfileOut | None = None
    error: str | None = None


class DirSaveResponse(BaseModel):
    ok: bool
    dir: dict | None = None
    error: str | None = None


# --------------------------------------------------------------------------- #
# Route handlers
# --------------------------------------------------------------------------- #
@app.get("/models", response_model=list[ModelOut])
def list_models():
    """Return the unified model registry (JSON files + config.yaml + disk)."""
    return [ModelOut(**m.__dict__) for m in discover_models()]


@app.get("/hardware", response_model=HardwareSpecOut)
def hardware():
    """Return the detected hardware (RTX 5070 Max-Q, Intel, 32 GB RAM...)."""
    return HardwareSpecOut(**detect_hardware().__dict__)


@app.get("/configs", response_model=ConfigOut)
def configs():
    """Return the last persisted configuration, or build a fresh one."""
    cfg = load_config()
    if cfg is None:
        cfg = build_config()
    return ConfigOut(
        hardware=HardwareSpecOut(**cfg.hardware.__dict__),
        profiles=[ConfigProfileOut(**p.__dict__) for p in cfg.profiles],
        models=[ModelOut(**m.__dict__) for m in cfg.models],
        generated_at=cfg.generated_at,
        base_models_dir=cfg.base_models_dir,
        ram_limit_gb=cfg.ram_limit_gb,
        total_vram_gb=cfg.total_vram_gb,
        free_vram_gb=cfg.free_vram_gb,
        models_count=len(cfg.models),
        profiles_count=len(cfg.profiles),
    )


@app.get("/configs/export.json")
def export_json():
    """Download the generated configuration as JSON."""
    cfg = load_config() or build_config()
    payload = {
        "hardware": cfg.hardware.__dict__,
        "profiles": [p.__dict__ for p in cfg.profiles],
        "models": [m.__dict__ for m in cfg.models],
        "generated_at": cfg.generated_at,
        "base_models_dir": cfg.base_models_dir,
        "ram_limit_gb": cfg.ram_limit_gb,
        "total_vram_gb": cfg.total_vram_gb,
        "free_vram_gb": cfg.free_vram_gb,
        "models_count": len(cfg.models),
        "profiles_count": len(cfg.profiles),
    }
    return JSONResponse(payload)


@app.get("/configs/export.yaml")
def export_yaml():
    """Download the generated configuration as YAML."""
    cfg = load_config() or build_config()
    from .config_store import export_llama_swap_config_bytes

    return Response(
        content=export_llama_swap_config_bytes(cfg),
        media_type="application/yaml",
        headers={"Content-Disposition": "attachment; filename=profiles_generated.yaml"},
    )


@app.post("/tuning", response_model=TuningSaveResponse)
def tuning_save(
    model_key: str = Form("", min_length=1),
    model_name: str = Form(""),
    quantization: str = Form("Q4_K_M"),
    n_gpu_layers: str = Form("all"),
    ctx_size: str = Form("0"),
    temp: str = Form("0.7"),
    top_k: str = Form("40"),
    top_p: str = Form("0.9"),
    n_predict: str = Form("512"),
    n_threads: str = Form("4"),
    path: str = Form(""),
):
    """Persist a per-model llama.cpp tuning profile.

    Form fields: model_key (required), model_name, quantization, n_gpu_layers,
    ctx_size, temp, top_k, top_p, n_predict, n_threads, path.
    """
    if not model_key:
        raise HTTPException(status_code=400, detail="missing model_key")
    data = {
        "model_name": model_name,
        "quantization": quantization,
        "n_gpu_layers": n_gpu_layers,
        "ctx_size": ctx_size,
        "temp": temp,
        "top_k": top_k,
        "top_p": top_p,
        "n_predict": n_predict,
        "n_threads": n_threads,
        "path": path,
    }
    profile = save_tuning_profile(model_key, data)
    return TuningSaveResponse(
        ok=True,
        profile=TuningProfileOut(**profile.__dict__),
        error=None,
    )


@app.post("/dirs", response_model=DirSaveResponse)
def dirs_save(action: str = Form(""), path: str = Form("")):
    """Add or delete a model directory.

    Body (form-encoded): action='add' | 'delete', path=<absolute path>.
    """
    action = (action or "").strip().lower()
    path = (path or "").strip().rstrip("/")
    if action == "add":
        if not path:
            raise HTTPException(status_code=400, detail="empty path")
        try:
            added = add_dir(path)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        return DirSaveResponse(
            ok=True,
            dir=added.__dict__ if added else None,
            error=None,
        )
    if action == "delete":
        if delete_dir(path):
            return DirSaveResponse(ok=True, dir=None, error=None)
        raise HTTPException(status_code=404, detail="not found")
    raise HTTPException(status_code=400, detail="unknown action")


@app.post("/reload", response_model=ConfigOut)
def reload_data():
    """Force a fresh read of the model registry and hardware.

    POST-only; returns the full serialised configuration (hardware, models,
    profiles, derived totals) so the frontend can update in place.
    """
    try:
        cfg = build_config()
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return ConfigOut(
        hardware=HardwareSpecOut(**cfg.hardware.__dict__),
        profiles=[ConfigProfileOut(**p.__dict__) for p in cfg.profiles],
        models=[ModelOut(**m.__dict__) for m in cfg.models],
        generated_at=cfg.generated_at,
        base_models_dir=cfg.base_models_dir,
        ram_limit_gb=cfg.ram_limit_gb,
        total_vram_gb=cfg.total_vram_gb,
        free_vram_gb=cfg.free_vram_gb,
        models_count=len(cfg.models),
        profiles_count=len(cfg.profiles),
    )


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5001)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _model_counts() -> dict[str, int]:
    """Count discovered models per directory (no longer exposed as a route)."""
    counts: dict[str, int] = {}
    for model in discover_models():
        parent = str(Path(model.path).parent) if model.path else ""
        if parent:
            counts[parent] = counts.get(parent, 0) + 1
    return counts
