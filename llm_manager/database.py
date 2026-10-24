"""SQLAlchemy ORM for persisting LLM manager configurations.

Stores the generated configuration (hardware + models + profiles) so it can be
loaded later, listed, and re-emitted as llama-swap ``config.yaml`` files.

Database: SQLite file (``local_config.db``) by default. The engine is created at
import time; call :func:`init_db` to (re)create all tables.
"""

from __future__ import annotations

import logging

from sqlalchemy import Column, ForeignKey, Integer, String, Float, JSON, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

# Default SQLite file.  ``local_config.db`` is git-ignored.
DATABASE_URL = "sqlite:///local_config.db"

# SQLite requires ``check_same_thread=False`` when the session is used from a
# thread other than the one it was created in (e.g. Flask inside a request).
CONNECT_ARGS = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=CONNECT_ARGS)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# ORM models
# ---------------------------------------------------------------------------


class OrmModel(Base):
    """A row in the model registry (one per discovered model)."""

    __tablename__ = "model"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    size_gb = Column(Float, default=0.0)
    context_length = Column(Integer, default=0)
    quantization = Column(String, default="Q4_K_M")
    precision = Column(String, default="gguf")
    device = Column(String, default="auto")
    status = Column(String, default="available")
    version = Column(String, default="")
    hardware_constraint = Column(String, default="")
    memory_safe_context = Column(Integer, default=0)
    parameter_label = Column(String, default="")
    path = Column(String, default="")
    max_tokens = Column(Integer, default=512)
    extra = Column(JSON, default=dict)

    config_id = Column(Integer, ForeignKey("config.id"), nullable=True)
    config = relationship("OrmConfig", back_populates="models", lazy="selectin")

    def to_domain(self):  # pragma: no cover - simple mapping
        from .models import Model

        return Model(
            name=self.name,
            full_name=self.full_name,
            size_gb=self.size_gb,
            context_length=self.context_length,
            quantization=self.quantization,
            precision=self.precision,
            device=self.device,
            status=self.status,
            version=self.version,
            model_id=self.model_id,
            hardware_constraint=self.hardware_constraint,
            memory_safe_context=self.memory_safe_context,
            parameter_label=self.parameter_label,
            path=self.path,
            max_tokens=self.max_tokens,
            extra=dict(self.extra or {}),
        )


class OrmProfile(Base):
    """A generated configuration profile for a single model."""

    __tablename__ = "config_profile"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, ForeignKey("config.id"), index=True, nullable=False)
    model_id = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    quantization = Column(String, nullable=False)
    size_gb = Column(Float, default=0.0)
    ctx_size = Column(Integer, default=0)
    fit_status = Column(String, default="fits")
    vram_needed = Column(Float, default=0.0)
    device = Column(String, default="cpu")
    path = Column(String, default="")
    kv_gb = Column(Float, default=0.0)
    kv_bits = Column(Integer, default=8)
    vram_for_model = Column(Float, default=0.0)
    ram_gb = Column(Float, default=0.0)
    generated_at = Column(String, default="")
    temp = Column(Float, default=0.7)
    top_k = Column(Integer, default=40)
    top_p = Column(Float, default=0.9)
    n_predict = Column(Integer, default=512)
    n_gpu_layers = Column(String, default="all")
    max_tokens = Column(Integer, default=512)

    config = relationship("OrmConfig", back_populates="profiles", lazy="selectin")

    def to_domain(self):  # pragma: no cover - simple mapping
        from .configurator import ConfigProfile

        return ConfigProfile(
            model_id=self.model_id,
            model_name=self.model_name,
            quantization=self.quantization,
            size_gb=self.size_gb,
            ctx_size=self.ctx_size,
            fit_status=self.fit_status,
            vram_needed=self.vram_needed,
            device=self.device,
            path=self.path,
            kv_gb=self.kv_gb,
            kv_bits=self.kv_bits,
            vram_for_model=self.vram_for_model,
            ram_gb=self.ram_gb,
            generated_at=self.generated_at,
            temp=self.temp,
            top_k=self.top_k,
            top_p=self.top_p,
            n_predict=self.n_predict,
            n_gpu_layers=self.n_gpu_layers,
            max_tokens=self.max_tokens,
        )


class OrmConfig(Base):
    """A persisted configuration snapshot (top-level container)."""

    __tablename__ = "config"

    id = Column(Integer, primary_key=True, index=True)
    generated_at = Column(String, nullable=False)
    base_models_dir = Column(
        String,
        nullable=False,
        default="/home/waflores/.lmstudio/models/lmstudio-community",
    )
    ram_limit_gb = Column(Float, nullable=True)
    total_vram_gb = Column(Float, nullable=False)
    free_vram_gb = Column(Float, nullable=False)
    hardware = Column(JSON, default=dict)

    models = relationship(
        "OrmModel",
        back_populates="config",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    profiles = relationship(
        "OrmProfile",
        back_populates="config",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def to_domain(self):
        from .configurator import Config
        from .hardware_spec import HardwareSpec

        hardware = HardwareSpec()
        hw = self.hardware or {}
        for field in (
            "cpu_cores",
            "gpu_name",
            "gpu_memory_gb",
            "gpu_free_gb",
            "system_ram_gb",
            "system_disk_gb",
        ):
            if field in hw:
                setattr(hardware, field, hw[field])

        models = [m.to_domain() for m in self.models]
        profiles = [p.to_domain() for p in self.profiles]
        return Config(
            hardware=hardware,
            profiles=profiles,
            models=models,
            generated_at=self.generated_at,
            base_models_dir=self.base_models_dir,
            ram_limit_gb=self.ram_limit_gb,
        )

    @property
    def models_count(self):
        return len(self.models)

    def __repr__(self):
        return f"<OrmConfig(id={self.id}, generated_at={self.generated_at!r}, models_count={len(self.models)})>"


class OrmTuningProfile(Base):
    """A per-model, user-editable llama.cpp tuning profile.

    Stored in the database so the web app can present a form per model and
    persist the chosen quantization, context, layers and generation knobs.
    """

    __tablename__ = "tuning_profile"

    id = Column(Integer, primary_key=True, index=True)
    model_key = Column(String, unique=True, index=True, nullable=False)
    model_name = Column(String, nullable=False)
    quantization = Column(String, default="Q4_K_M")
    n_gpu_layers = Column(String, default="all")
    ctx_size = Column(Integer, default=0)
    temp = Column(Float, default=0.7)
    top_k = Column(Integer, default=40)
    top_p = Column(Float, default=0.9)
    n_predict = Column(Integer, default=512)
    n_threads = Column(Integer, default=4)
    path = Column(String, default="")
    created_at = Column(String, default="")
    updated_at = Column(String, default="")

    def to_domain(self):  # pragma: no cover - simple mapping
        from .tuning_store import TuningProfile

        return TuningProfile(
            model_key=self.model_key,
            model_name=self.model_name,
            quantization=self.quantization,
            n_gpu_layers=self.n_gpu_layers,
            ctx_size=self.ctx_size,
            temp=self.temp,
            top_k=self.top_k,
            top_p=self.top_p,
            n_predict=self.n_predict,
            n_threads=self.n_threads,
            path=self.path,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class OrmModelDir(Base):
    """A configured directory where llama.cpp models may live."""

    __tablename__ = "model_dir"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(String, default="")
    updated_at = Column(String, default="")

    def to_domain(self):  # pragma: no cover - simple mapping
        from .tuning_store import ModelDir

        return ModelDir(
            path=self.path, created_at=self.created_at, updated_at=self.updated_at
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def init_db() -> None:
    """Create all ORM tables (idempotent)."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Yield a transactional session scoped to the current request/thread."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
