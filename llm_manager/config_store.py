"""Persist and re-load generated configurations in the ORM database.

This is the bridge between the configurator's in-memory :class:`Config` and the
SQLite ORM tables. It exposes:

- :func:`build_and_persist`  - build a fresh config and write it to the DB.
- :func:`load_config`       - materialize a domain :class:`Config` from the DB.
- :func:`list_profiles`     - list the persisted profiles.
- :func:`delete_config`     - remove the current saved snapshot.
- :func:`export_llama_swap_config` - write a llama-swap ``config.yaml``.

All distances are in GB; everything else is per-profile. The DB is a simple
SQLite file (``local_config.db``) that can be versioned or discarded.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import yaml

from .configurator import Config, _to_serializable, build_config, Model
from .database import OrmConfig, OrmModel, OrmProfile, SessionLocal
from .loader import discover_models_on_disk

logger = logging.getLogger(__name__)

# Single "current" snapshot: the most recently persisted OrmConfig row.
_orm = OrmConfig


def build_and_persist() -> Config:
    """Build the hardware-aware config and persist it to the database.

    Returns the in-memory :class:`Config` so callers can render it without a
    second round trip.
    """
    cfg = build_config()
    _persist_config(cfg)
    return cfg


def _persist_config(cfg: Config) -> None:
    """Upsert the ORM rows for one :class:`Config` snapshot."""
    with SessionLocal() as session:
        session.query(OrmProfile).delete()
        session.query(OrmModel).delete()
        session.query(OrmConfig).delete()

        orm_cfg = OrmConfig(
            generated_at=cfg.generated_at,
            base_models_dir=cfg.base_models_dir,
            ram_limit_gb=cfg.ram_limit_gb,
            total_vram_gb=cfg.total_vram_gb,
            free_vram_gb=cfg.free_vram_gb,
            hardware=_to_serializable(cfg.hardware),
        )
        session.add(orm_cfg)
        session.flush()

        for model in cfg.models:
            session.add(_model_to_orm(model, orm_cfg.id))
        for profile in cfg.profiles:
            session.add(_profile_to_orm(profile, orm_cfg.id))

        session.commit()


def _model_to_orm(model, config_id: int):
    return OrmModel(
        model_id=model.model_id,
        name=model.name,
        full_name=model.full_name,
        size_gb=model.size_gb,
        context_length=model.context_length,
        quantization=model.quantization,
        precision=model.precision,
        device=model.device,
        status=model.status,
        version=model.version,
        hardware_constraint=model.hardware_constraint,
        memory_safe_context=model.memory_safe_context,
        parameter_label=model.parameter_label,
        path=model.path,
        max_tokens=model.max_tokens,
        extra=dict(model.extra or {}),
        config_id=config_id,
    )


def _profile_to_orm(profile, config_id: int):
    return OrmProfile(
        model_id=profile.model_id,
        model_name=profile.model_name,
        quantization=profile.quantization,
        size_gb=profile.size_gb,
        ctx_size=profile.ctx_size,
        fit_status=profile.fit_status,
        vram_needed=profile.vram_needed,
        device=profile.device,
        path=profile.path,
        kv_gb=profile.kv_gb,
        kv_bits=profile.kv_bits,
        vram_for_model=profile.vram_for_model,
        ram_gb=profile.ram_gb,
        generated_at=profile.generated_at,
        temp=profile.temp,
        top_k=profile.top_k,
        top_p=profile.top_p,
        n_predict=profile.n_predict,
        n_gpu_layers=profile.n_gpu_layers,
        max_tokens=profile.max_tokens,
        config_id=config_id,
    )


def load_config() -> Config | None:
    """Return the most recently persisted :class:`Config` as domain objects."""
    with SessionLocal() as session:
        orm_cfg = session.query(OrmConfig).order_by(OrmConfig.id.desc()).first()
        if orm_cfg is None:
            return None
        return orm_cfg.to_domain()


def list_profiles(
    *,
    fields: tuple[str, ...] = (
        "model_name",
        "model_id",
        "size_gb",
        "ctx_size",
        "kv_gb",
        "quantization",
        "fit_status",
        "path",
        "device",
    ),
) -> list[dict]:
    """Return every persisted profile as a plain dict (useful for a UI table)."""
    with SessionLocal() as session:
        orm_cfg = session.query(OrmConfig).order_by(OrmConfig.id.desc()).first()
        profiles = []
        if orm_cfg is not None:
            for p in orm_cfg.profiles:
                profiles.append({field: getattr(p, field) for field in fields})
        return profiles


def delete_config() -> None:
    """Remove the current saved snapshot (starting with the latest row)."""
    with SessionLocal() as session:
        orm_cfg = session.query(OrmConfig).order_by(OrmConfig.id.desc()).first()
        if orm_cfg is not None:
            session.query(OrmProfile).filter_by(config_id=orm_cfg.id).delete()
            session.query(OrmModel).filter_by(config_id=orm_cfg.id).delete()
            session.query(OrmConfig).filter_by(id=orm_cfg.id).delete()
            session.commit()


# ---------------------------------------------------------------------------
# Disk discovery from configured directories
# ---------------------------------------------------------------------------
def discover_models_in_dirs(
    dirs: list[dict], models_dir: str | None = None
) -> list[Model]:
    """Discover models by crawling each configured directory on disk.

    Uses :func:`discover_models_on_disk` to walk each configured directory
    recursively for :file:`.gguf` files. Returns a list of :class:`Model`
    objects (with ``path`` set to the on-disk location). Does NOT persist to
    the database; use :func:`persist_models` for that.
    """
    models: list[Model] = []
    seen: set[str] = set()
    for d in dirs:
        dir_path = d.path if hasattr(d, "path") else d.get("path", "")
        if not dir_path or not os.path.isdir(dir_path):
            continue
        try:
            found = discover_models_on_disk(dir_path)
        except Exception:
            continue
        for model in found:
            if model.path in seen:
                continue
            seen.add(model.path)
            models.append(model)
    return models


def discover_and_persist_models(dirs: list[dict]) -> int:
    """Scan configured directories for models and persist them to the DB.

    This is the disk discovery entrypoint. It uses :func:`discover_models_in_dirs`
    to crawl each configured directory, then :func:`persist_models` to write
    the discovered models to the ORM database (linked to the current snapshot).

    Returns the number of new rows added.
    """
    from .database import OrmConfig, SessionLocal

    # Use the current persisted snapshot as the anchor.
    with SessionLocal() as session:
        orm_cfg = session.query(OrmConfig).order_by(OrmConfig.id.desc()).first()
        if orm_cfg is None:
            return 0
        config_id = int(orm_cfg.id)

    models = discover_models_in_dirs(dirs)
    return persist_models(models, config_id)


def persist_models(models: list[Model], config_id: int) -> int:
    """Persist a list of :class:`Model` objects to the ORM database.

    Upserts by ``model_id`` within the given config snapshot. Returns the
    number of new rows added.
    """
    with SessionLocal() as session:
        existing = {
            m.model_id: m
            for m in session.query(OrmModel).filter_by(config_id=config_id).all()
        }
        new_count = 0
        for model in models:
            if not isinstance(model, Model):
                continue
            if model.model_id in existing:
                # Update existing row with latest disk info.
                orm = existing[model.model_id]
                orm.size_gb = model.size_gb
                orm.context_length = model.context_length
                orm.quantization = model.quantization
                orm.path = model.path
                orm.extra = dict(model.extra or {})
            else:
                session.add(
                    OrmModel(
                        model_id=model.model_id,
                        name=model.name,
                        full_name=model.full_name,
                        size_gb=model.size_gb,
                        context_length=model.context_length,
                        quantization=model.quantization,
                        precision=model.precision,
                        device=model.device,
                        status=model.status,
                        version=model.version,
                        hardware_constraint=model.hardware_constraint,
                        memory_safe_context=model.memory_safe_context,
                        parameter_label=model.parameter_label,
                        path=model.path,
                        max_tokens=model.max_tokens,
                        extra=dict(model.extra or {}),
                        config_id=config_id,
                    )
                )
                new_count += 1
        session.commit()
    return new_count


# ---------------------------------------------------------------------------
# llama-swap config emission
# ---------------------------------------------------------------------------


def export_llama_swap_config(config: Config, path: Path) -> Path:
    """Materialize the persisted configuration as a llama-swap ``config.yaml``.

    Each profile becomes one llama-swap *model* entry; the ``roles``/``capabilities``
    are derived from the profile's fit status so the file stays valid even when a
    model was only saved as a fallback (capped/over-VRAM). The ``context:`` block is
    regenerated from the detected hardware so the file is self-contained.
    """
    yaml_text = _build_llama_swap_yaml_bytes(config)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        fh.write(yaml_text)
    logger.info("Wrote llama-swap config to %s", path)
    return path


def export_llama_swap_config_bytes(config: Config) -> str:
    """Return the llama-swap ``config.yaml`` text for *config*.

    Public helper so the Flask app can return it as a downloadable response.
    """
    return _build_llama_swap_yaml_bytes(config)


def _build_llama_swap_yaml_bytes(config: Config) -> str:
    """Return the llama-swap ``config.yaml`` content for *config* as text."""
    model_entries = []
    for p in config.profiles:
        roles = (
            ["chat", "edit", "apply", "autocomplete"]
            if p.fit_status == "fits"
            else ["chat"]
        )
        capabilities = ["tool_use"] if p.fit_status == "fits" else []
        model_entries.append(
            {
                "name": p.model_name,
                "provider": "llama.cpp",
                "model": p.model_id,
                "roles": roles,
                "capabilities": capabilities,
            }
        )

    data = {
        "name": "llama-swap profiles (generated from ORM)",
        "version": "1.0.0",
        "schema": "v1",
        "models": model_entries,
        "context": [
            {"provider": "repo-map", "params": {"includeSignatures": True}},
            {"provider": "os"},
            {"provider": "diff"},
            {"provider": "file"},
            {"provider": "code"},
            {"provider": "open"},
            {"provider": "tree"},
            {"provider": "currentFile"},
        ],
    }
    return yaml.safe_dump(data, sort_keys=False, default_flow_style=False)


def list_db_models(config_id: int) -> list[dict]:
    """Return persisted models from the current config snapshot as dicts."""
    from .database import SessionLocal, OrmModel

    with SessionLocal() as session:
        models = session.query(OrmModel).filter_by(config_id=config_id).all()
    result = []
    for m in models:
        result.append(
            {
                "model_id": m.model_id,
                "name": m.name,
                "full_name": m.full_name,
                "size_gb": m.size_gb,
                "context_length": m.context_length,
                "quantization": m.quantization,
                "precision": m.precision,
                "device": m.device,
                "status": m.status,
                "version": m.version,
                "hardware_constraint": m.hardware_constraint,
                "memory_safe_context": m.memory_safe_context,
                "parameter_label": m.parameter_label,
                "path": m.path,
                "max_tokens": m.max_tokens,
                "extra": m.extra,
            }
        )
    return result
