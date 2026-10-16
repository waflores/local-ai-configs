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

from .configurator import _to_serializable, build_config
from .hardware import detect_hardware
from .loader import discover_models

# This is the project root, one level above the package.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def create_app() -> Flask:
    # Use the package's templates/ directory regardless of CWD.
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "llm_manager" / "templates"),
    )
    app.config["JSON_SORT_KEYS"] = False

    # --- helpers -----------------------------------------------------------
    def _render(template: str, **ctx) -> str:
        return render_template(template, **ctx)

    # --- routes ------------------------------------------------------------
    @app.route("/")
    def index():
        # Populate hardware + config summary on the front page.
        try:
            hardware_info = detect_hardware()
        except Exception:
            hardware_info = None
        try:
            cfg = build_config()
        except Exception as e:
            cfg = None
            error = str(e)
        else:
            error = None
        return _render(
            "index.html",
            title="LLM Manager",
            hardware=hardware_info,
            cfg=cfg,
            error=error,
        )

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


def shell() -> Flask:
    """Return the app without running the reloader."""
    app = create_app()
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
