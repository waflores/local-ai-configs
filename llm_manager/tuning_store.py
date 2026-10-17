"""Persistence layer for per-model llama.cpp tuning profiles and model directories.

This module bridges the SQLAlchemy ORM (``OrmTuningProfile``, ``OrmModelDir``)
and plain-data dictionaries / dataclasses that the web app and CLI consume.
It owns a single "current" snapshot for tuning profiles and the directory
list, matching the convention used by :mod:`config_store`.

Domain types
------------
:class:`TuningProfile`
    A per-model llama.cpp tuning configuration (quantization, context,
    layers, generation knobs, model path).
:class:`ModelDir`
    A configured directory where llama.cpp models may live.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC

from .database import SessionLocal, engine

# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------


@dataclass
class TuningProfile:
    """User-editable llama.cpp tuning knobs for one model."""

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


@dataclass
class ModelDir:
    """A directory where llama.cpp models may be found."""

    path: str
    created_at: str = ""
    updated_at: str = ""


_DEFAULT_DIRS = (
    "/home/waflores/.lmstudio/models/lmstudio-community",
)


def _now() -> str:
    return datetime.now(UTC).isoformat()


# ---------------------------------------------------------------------------
# Tuning profiles
# ---------------------------------------------------------------------------


def _session():
    return SessionLocal()


def list_tuning_profiles():
    """Return every persisted tuning profile as a plain dict."""
    from .database import OrmTuningProfile

    with _session() as session:
        rows = session.query(OrmTuningProfile).order_by(OrmTuningProfile.model_key).all()
        return [r.to_domain() for r in rows]


def get_tuning_profile(model_key: str):
    """Return one tuning profile as a plain dict, or ``None``."""
    from .database import OrmTuningProfile

    with _session() as session:
        row = (
            session.query(OrmTuningProfile)
            .filter(OrmTuningProfile.model_key == model_key)
            .first()
        )
        return row.to_domain() if row else None


def save_tuning_profile(model_key: str, data: dict) -> TuningProfile:
    """Create or update the tuning profile for *model_key*.

    *data* may only contain the tuning fields; everything else defaults.
    """
    from .database import OrmTuningProfile

    now = _now()
    with _session() as session:
        row = (
            session.query(OrmTuningProfile)
            .filter(OrmTuningProfile.model_key == model_key)
            .first()
        )
        if row is None:
            row = OrmTuningProfile(model_key=model_key, model_name=data.get("model_name", model_key))
            session.add(row)
        row.quantization = data.get("quantization", "Q4_K_M")
        row.n_gpu_layers = data.get("n_gpu_layers", "all")
        row.ctx_size = int(data.get("ctx_size", 0) or 0)
        row.temp = float(data.get("temp", 0.7) or 0.7)
        row.top_k = int(data.get("top_k", 40) or 40)
        row.top_p = float(data.get("top_p", 0.9) or 0.9)
        row.n_predict = int(data.get("n_predict", 512) or 512)
        row.n_threads = int(data.get("n_threads", 4) or 4)
        row.path = data.get("path", "") or ""
        row.updated_at = now
        session.commit()
        session.refresh(row)
        return row.to_domain()


def delete_tuning_profile(model_key: str) -> bool:
    """Remove the tuning profile for *model_key*. Returns ``True`` if deleted."""
    from .database import OrmTuningProfile

    with _session() as session:
        row = (
            session.query(OrmTuningProfile)
            .filter(OrmTuningProfile.model_key == model_key)
            .first()
        )
        if row is None:
            return False
        session.delete(row)
        session.commit()
        return True


# ---------------------------------------------------------------------------
# Model directories
# ---------------------------------------------------------------------------


def list_dirs():
    """Return every configured model directory as a list of ``ModelDir``."""
    from .database import OrmModelDir

    with _session() as session:
        rows = session.query(OrmModelDir).order_by(OrmModelDir.path).all()
        return [r.to_domain() for r in rows]


def add_dir(path: str) -> ModelDir:
    """Register a model directory. Returns the stored :class:`ModelDir`."""
    from .database import OrmModelDir

    normalized = path.strip().rstrip("/")
    with _session() as session:
        exists = session.query(OrmModelDir).filter(OrmModelDir.path == normalized).first()
        if exists:
            return exists.to_domain()
        row = OrmModelDir(path=normalized, created_at=_now(), updated_at=_now())
        session.add(row)
        session.commit()
        session.refresh(row)
        return row.to_domain()


def delete_dir(path: str) -> bool:
    """Remove a configured model directory. Returns ``True`` if deleted."""
    from .database import OrmModelDir

    normalized = path.strip().rstrip("/")
    with _session() as session:
        row = session.query(OrmModelDir).filter(OrmModelDir.path == normalized).first()
        if row is None:
            return False
        session.delete(row)
        session.commit()
        return True


# ---------------------------------------------------------------------------
# Bootstrapping the default models directory
# ---------------------------------------------------------------------------


def _bootstrap_default_dir():
    """Ensure the default models directory is registered on first run."""
    from .database import OrmModelDir

    with _session() as session:
        if not session.query(OrmModelDir).first():
            session.add(
                OrmModelDir(
                    path=_DEFAULT_DIRS[0],
                    created_at=_now(),
                    updated_at=_now(),
                )
            )
            session.commit()


def _ensure_tables():
    # Tables are created by the application on startup via ``init_db``.  These
    # helpers are also safe to call from ad-hoc scripts, so no-op if they are
    # already created.
    from .database import Base

    Base.metadata.create_all(bind=engine)


_ensure_tables()
_bootstrap_default_dir()
