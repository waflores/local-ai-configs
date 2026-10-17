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

from flask import Flask, jsonify, render_template, Response, request, redirect

from .configurator import _to_serializable, build_config
from .config_store import export_llama_swap_config_bytes, load_config
from .configurator import ConfigProfile
from .database import init_db
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

    # (Re)create ORM tables on startup so the persisted snapshots are ready.
    init_db()

    # --- helpers -----------------------------------------------------------
    def _render(template: str, **ctx) -> str:
        return render_template(template, **ctx)

    def _profile_dicts(profiles: list[ConfigProfile]) -> list[dict]:
        """Convert ConfigProfile objects to plain dicts for the UI template."""
        fields = (
            "model_name",
            "model_id",
            "size_gb",
            "ctx_size",
            "kv_gb",
            "quantization",
            "fit_status",
            "path",
            "device",
        )
        return [{field: getattr(p, field) for field in fields} for p in profiles]

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
        # Serve the last persisted configuration if one exists; otherwise
        # fall back to a freshly generated one. Persisted snapshots are the
        # UI's source of truth so the summary cards and profiles table stay
        # in sync with what was checked in to the database.
        cfg = load_config()
        if cfg is None:
            try:
                cfg = build_config()
            except Exception as e:
                cfg = None
                error = str(e)
            else:
                error = None
        else:
            error = None

        # Persist snapshots are the UI's source of truth so the summary cards
        # and profiles table stay in sync. When build_config() fails (e.g. no
        # tools or models), we keep cfg=None and pass an empty profiles list
        # so the template's `if cfg.profiles` guard still works.
        if cfg is not None:
            profiles = _profile_dicts(cfg.profiles)
        else:
            profiles = []
        return _render(
            "configs.html",
            title="Configurations",
            cfg=cfg,
            error=error,
            profiles=profiles,
        )

    @app.route("/configs/export.json")
    def export_configs_json():
        cfg = build_config()
        return jsonify(_to_serializable(cfg))

    @app.route("/configs/export.yaml")
    def export_configs_yaml():
        cfg = load_config() or build_config()
        return Response(
            export_llama_swap_config_bytes(cfg),
            mimetype="application/yaml",
            headers={
                "Content-Disposition": "attachment; filename=profiles_generated.yaml"
            },
        )

    # ------------------------------------------------------------------------
    # Model tuning
    # ------------------------------------------------------------------------

    @app.route("/tuning")
    def tuning_page():
        from .loader import discover_models
        from .tuning_store import list_tuning_profiles, list_dirs

        models = discover_models()
        profiles = list_tuning_profiles()
        profile_by_key = {p.model_key: p for p in profiles}

        # Present tuning profiles in registry order (models first, then any
        # stray profiles with no matching registry entry).
        ordered = [profile_by_key.pop(m.model_id, None) for m in models]
        ordered = [p for p in ordered if p is not None]
        ordered += list(profile_by_key.values())

        return _render(
            "tuning.html",
            title="Model Tuning",
            models=models,
            tuning=ordered,
            dirs=list_dirs(),
            profile_by_key=profile_by_key,
        )

    @app.route("/tuning", methods=["POST"])
    def tuning_save():
        from .tuning_store import save_tuning_profile
        from dataclasses import asdict

        model_key = request.form.get("model_key", "").strip()
        if not model_key:
            return jsonify({"ok": False, "error": "missing model_key"}), 400

        data = {
            "model_name": request.form.get("model_name", model_key),
            "quantization": request.form.get("quantization", "Q4_K_M"),
            "n_gpu_layers": request.form.get("n_gpu_layers", "all"),
            "ctx_size": request.form.get("ctx_size", "0"),
            "temp": request.form.get("temp", "0.7"),
            "top_k": request.form.get("top_k", "40"),
            "top_p": request.form.get("top_p", "0.9"),
            "n_predict": request.form.get("n_predict", "512"),
            "n_threads": request.form.get("n_threads", "4"),
            "path": request.form.get("path", ""),
        }
        profile = save_tuning_profile(model_key, data)
        return jsonify({"ok": True, "profile": asdict(profile)})

    # ------------------------------------------------------------------------
    # Model directories
    # ------------------------------------------------------------------------

    @app.route("/admin")
    def admin_page():
        from pathlib import Path

        from .loader import discover_models
        from .tuning_store import list_dirs

        dirs = list_dirs()
        # Number of discovered models sitting in each directory.
        model_counts: dict[str, int] = {}
        for model in discover_models():
            parent = str(Path(model.path).parent) if model.path else ""
            if parent:
                model_counts[parent] = model_counts.get(parent, 0) + 1

        return _render(
            "admin.html",
            title="Admin",
            dirs=dirs,
            model_counts=model_counts,
        )

    # ------------------------------------------------------------------------
    # Model directory configuration
    # ------------------------------------------------------------------------

    @app.route("/dirs")
    def dir_settings_page():
        # Consolidated admin portal lives at /admin.
        return redirect("/admin")

    @app.route("/dirs", methods=["POST"])
    def dir_settings_save():
        from .tuning_store import add_dir, delete_dir

        action = request.form.get("action", "")
        if action == "add":
            path = request.form.get("path", "").strip().rstrip("/")
            if not path:
                return jsonify({"ok": False, "error": "empty path"}), 400
            try:
                added = add_dir(path)
            except Exception as exc:  # noqa: BLE001
                return jsonify({"ok": False, "error": str(exc)}), 500
            return jsonify({"ok": True, "dir": added})
        if action == "delete":
            path = request.form.get("path", "").strip().rstrip("/")
            if delete_dir(path):
                return jsonify({"ok": True})
            return jsonify({"ok": False, "error": "not found"}), 404
        return jsonify({"ok": False, "error": "unknown action"}), 400

    # ------------------------------------------------------------------------
    # Model registry refresh
    # ------------------------------------------------------------------------

    @app.route("/reload", methods=["POST"])
    def reload_data():
        """Force a fresh read of the model registry and hardware.

        Returns the full serialized configuration (hardware, models, profiles,
        and derived totals) instead of a bare list, so the frontend can update
        the summary cards and profiles table in place without navigating away.

        A normal ``GET``/click on this endpoint returns nothing useful: it is a
        POST-only JSON API and has no rendered template of its own.
        """
        try:
            cfg = build_config()
        except Exception as e:
            # Building the config should never fail; mirror the index route's
            # behavior and surface the exception to the caller.
            return jsonify({"error": str(e)}), 502
        return jsonify(_to_serializable(cfg))

    @app.route("/api-docs")
    def api_docs():
        """Serve the API documentation page (Swagger UI / ReDoc served by FastAPI)."""
        # The FastAPI app runs on port 5001 as a separate server; the Flask app
        # proxies the docs here (iframe to the FastAPI Swagger UI).
        return render_template(
            "api_docs.html",
            fastapi_docs_url="http://127.0.0.1:5001/docs",
            fastapi_redoc_url="http://127.0.0.1:5001/redoc",
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
