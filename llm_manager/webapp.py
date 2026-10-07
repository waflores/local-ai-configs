"""Flask web application for managing downloaded LLMs.

Provides:
  - A model registry page showing every downloaded LLM and its verification
    metadata (declared context, memory-safe context, quantization).
  - A hardware page showing the detected machine.
  - A configuration page that generates hardware-aware profiles for every
    model, highlighting which ones fit in the available VRAM.
  - An export of the generated configurations as JSON.
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, render_template

from .configurator import Config, _to_serializable, build_config
from .hardware import detect_hardware
from .hardware_spec import HardwareSpec
from .loader import discover_models
from .models import ConfigProfile, Model

# This is the project root, one level above the package.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def create_app() -> Flask:
    # Use the package's templates/ directory regardless of CWD.
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "templates"),
    )
    app.config["JSON_SORT_KEYS"] = False

    # --- helpers -----------------------------------------------------------
    def _render(template: str, **ctx) -> str:
        return render_template(template, **ctx)

    # --- routes ------------------------------------------------------------
    @app.route("/")
    def index():
        return _render("index.html", title="LLM Manager")

    @app.route("/models")
    def models_page():
        models = discover_models()
        return _render("models.html", title="Models", models=models)

    @app.route("/hardware")
    def hardware_page():
        try:
            hw = detect_hardware()
        except Exception:
            hw = None
        return _render("hardware.html", title="Hardware", hardware=hw)

    @app.route("/configs")
    def configs_page():
        try:
            cfg = build_config()
        except Exception as e:
            # Building the config should never fail; on failure show the
            # exception so the user can report it.
            cfg = None
            error = str(e)
        else:
            error = None
        return _render(
            "configs.html",
            title="Configurations",
            cfg=cfg,
            error=error,
        )

    @app.route("/configs/export.json")
    def export_configs():
        cfg = build_config()
        return jsonify(_to_serializable(cfg))

    @app.route("/reload", methods=["POST"])
    def reload_data():
        """Force a fresh read of the model registry and hardware."""
        try:
            hw = detect_hardware()
        except Exception:
            hw = None
        models = discover_models()
        try:
            profiles = build_config().profiles
        except Exception:
            profiles = []
        return jsonify(
            {
                "hardware": _to_serializable(hw),
                "models": _to_serializable(models),
                "profiles": _to_serializable(profiles),
            }
        )

    return app


# Top-level Flask application instance for ``flask run`` / ``gunicorn``.
app = create_app()


# --- serialization helpers ---------------------------------------------------
def _to_serializable(obj) -> dict:
    """Convert domain objects to plain dicts for JSON templating."""
    if obj is None:
        return None
    if isinstance(obj, Config):
        return {
            "hardware": _to_serializable(obj.hardware),
            "profiles": [_to_serializable(p) for p in obj.profiles],
            "models": [_to_serializable(m) for m in obj.models],
            "generated_at": obj.generated_at,
            "base_models_dir": obj.base_models_dir,
        }
    if isinstance(obj, HardwareSpec):
        return {
            "cpu_cores": obj.cpu_cores,
            "gpu_name": obj.gpu_name,
            "gpu_memory_gb": obj.gpu_memory_gb,
            "gpu_free_gb": obj.gpu_free_gb,
            "system_ram_gb": obj.system_ram_gb,
            "system_disk_gb": obj.system_disk_gb,
        }
    if isinstance(obj, Model):
        return {
            "name": obj.name,
            "full_name": obj.full_name,
            "size_gb": obj.size_gb,
            "context_length": obj.context_length,
            "max_tokens": obj.max_tokens,
            "quantization": obj.quantization,
            "precision": obj.precision,
            "device": obj.device,
            "hardware": obj.hardware,
            "status": obj.status,
            "version": obj.version,
            "model_id": obj.model_id,
            "hardware_constraint": obj.hardware_constraint,
            "memory_safe_context": obj.memory_safe_context,
            "path": obj.path,
            "parameter_label": obj.parameter_label,
            "extra": obj.extra,
        }
    if isinstance(obj, ConfigProfile):
        return {
            "model_id": obj.model_id,
            "model_name": obj.model_name,
            "quantization": obj.quantization,
            "size_gb": obj.size_gb,
            "ctx_size": obj.ctx_size,
            "temp": obj.temp,
            "top_k": obj.top_k,
            "top_p": obj.top_p,
            "n_predict": obj.n_predict,
            "device": obj.device,
            "n_gpu_layers": obj.n_gpu_layers,
            "max_tokens": obj.max_tokens,
            "path": obj.path,
            "generated_at": obj.generated_at,
            "kv_gb": obj.kv_gb,
            "fit_status": obj.fit_status,
        }
    # Fall back to attribute lookup (dataclasses / simple objects).
    if hasattr(obj, "__dict__"):
        return {k: _to_serializable(v) for k, v in obj.__dict__.items()}
    return str(obj)


def shell() -> Flask:
    """Return the app without running the reloader."""
    app = create_app()
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
