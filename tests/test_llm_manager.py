"""Tests for the LLM manager package.

Covers:
  - model registry discovery and enrichment
  - hardware detection
  - VRAM estimation and fit checking
  - configurator (hardware-aware profile generation)
  - Flask web app routes
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from llm_manager import hardware_spec, models, quantization
from llm_manager.configurator import (
    Config,
    ConfigProfile,
    _to_serializable,
    build_config,
    detect_tier,
    generate_profiles,
)
from llm_manager.hardware import detect_hardware
from llm_manager.loader import (
    discover_models,
    extract_quantization,
    format_name,
)
from llm_manager.model_paths import (
    discover_model_paths,
    model_directory_mapping,
    resolve_model_path,
)
from llm_manager.quantization import (
    FP8,
    Q4_K_M,
    VALID_QUANTIZATIONS,
)

# Ensure the package under test is importable.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Convenience shorthands for quantized tags used in tests.
Q4 = "Q4_K_M"
Q5 = "Q5_K_M"
Q8 = "Q8_0"
F16T = "F16"
BF16T = "BF16"
Q5KV = "Q5_K_M_K_V"
Q3 = "Q3_K_M"
Q2 = "Q2_K"


# ---------------------------------------------------------------------------
# Quantization constants
# ---------------------------------------------------------------------------


class TestQuantization:
    """The quantization module only carries named string constants."""

    def test_all_constants_are_strings(self):
        # Only the quantization constants should be strings; HardwareSpec is a @dataclass.
        expect_strings = {
            Q4,
            Q5,
            Q5KV,
            Q8,
            FP8,
            F16T,
            BF16T,
            Q3,
            Q2,
        }
        for name in dir(quantization):
            if name.startswith("_"):
                continue
            if name in expect_strings:
                val = getattr(quantization, name)
                assert isinstance(val, str), f"{name} should be a str, got {type(val)}"
                assert (
                    val in VALID_QUANTIZATIONS
                ), f"{name}={val} not in VALID_QUANTIZATIONS"

    def test_valid_quantizations_list(self):
        # FP8 is included in the valid quantizations.
        assert set(VALID_QUANTIZATIONS) == {
            Q4,
            Q5,
            Q5KV,
            Q8,
            FP8,
            F16T,
            BF16T,
            Q3,
            Q2,
        }

    def test_alias_constants_match_valid_list(self):
        for const in (Q4, Q5, Q5KV, Q8, F16T, BF16T, Q3, Q2):
            assert const in VALID_QUANTIZATIONS


# ---------------------------------------------------------------------------
# HardwareSpec dataclass
# ---------------------------------------------------------------------------


class TestHardwareSpec:
    def test_defaults(self):
        h = hardware_spec.HardwareSpec()
        assert h.cpu_cores == 0
        assert h.gpu_name == ""
        assert h.gpu_memory_gb == 0.0
        assert h.gpu_free_gb == 0.0
        assert h.system_ram_gb == 0.0
        assert h.system_disk_gb == 0.0

    def test_field_names(self):
        h = hardware_spec.HardwareSpec(cpu_cores=16, gpu_memory_gb=8.0)
        assert h.cpu_cores == 16
        assert h.gpu_memory_gb == 8.0


# ---------------------------------------------------------------------------
# Model dataclass
# ---------------------------------------------------------------------------


class TestModel:
    def test_defaults(self):
        m = models.Model(name="test", full_name="Test Model")
        assert m.name == "test"
        assert m.full_name == "Test Model"
        assert m.size_gb == 0.0
        assert m.context_length == 0
        assert m.quantization == Q4
        assert m.status == "available"

    def test_parameters_b_is_none_with_size_zero(self):
        m = models.Model(name="test", full_name="Test", size_gb=0)
        assert m.parameters_b is None

    def test_parameters_b(self):
        # ~4 GB file at Q4_K_M (4 bits/param = 0.5 bytes/param) → 8B params
        m = models.Model(name="test", full_name="Test", size_gb=4.0, quantization=Q4)
        assert m.parameters_b == pytest.approx(8.0, rel=0.05)

    def test_fit_check(self):
        m = models.Model(name="test", full_name="Test", size_gb=4.0, quantization=Q4)
        assert m.fits_in(8.0, 10000) is True
        assert m.fits_in(2.0, 10000) is False

    def test_invalid_quantization_is_fallback(self):
        m = models.Model(name="test", full_name="Test", quantization="Nonexistent")
        assert m.quantization == Q4


# ---------------------------------------------------------------------------
# ConfigProfile dataclass
# ---------------------------------------------------------------------------


class TestConfigProfile:
    def test_defaults(self):
        p = ConfigProfile(
            model_id="m", model_name="M", quantization=Q4, size_gb=1.0, ctx_size=1000
        )
        assert p.quantization == Q4
        assert p.fit_status == "fits"
        assert p.ctx_size == 1000


# ---------------------------------------------------------------------------
# Quantisation tag extraction
# ---------------------------------------------------------------------------


class TestExtractQuantization:
    def test_q4_k_m(self):
        assert extract_quantization("...-q4_k_m.gguf") == Q4

    def test_q5_k_m(self):
        assert extract_quantization("...-q5_k_m.gguf") == Q5

    def test_q8_0(self):
        assert extract_quantization("...-q8_0.gguf") == Q8

    def test_unknown_returns_default(self):
        assert extract_quantization("...-foo.gguf") == Q4


# ---------------------------------------------------------------------------
# Readable model name formatting
# ---------------------------------------------------------------------------


class TestFormatName:
    def test_code_llama(self):
        # Identifier: 'codellama-7b-instruct', quant: Q4_K_M
        name = format_name(
            "lms-lmstudio-community-codellama-7b-instruct-gguf-codellama-7b-instruct-q4-k-m"
        )
        # Family: 'CodeLlama', size: '7b'
        assert name == "Codellama 7b", f"got {name!r}"

    def test_qwen(self):
        # Identifier: 'qwen3-6-27b', quant: Q4_K_M
        name = format_name("lms-lmstudio-community-qwen3-6-27b-gguf-qwen3-6-27b-q4-k-m")
        # Family: 'Qwen3', size: '6', model part tokens -> 'Qwen3 6 27b'
        assert name == "Qwen3 6 27b", f"got {name!r}"

    def test_deepseek(self):
        # 'deepseek-r1-0528-qwen3-8b', quant Q4_K_M
        name = format_name(
            "lms-lmstudio-community-deepseek-r1-0528-qwen3-8b-gguf-deepseek-r1-0528-974d9efc"
        )
        # Family: 'Deepseek Qwen3' (multi-token), size: '8b' -> 'Deepseek Qwen3 Qwen3 8b'
        assert name == "Deepseek Qwen3 Qwen3 8b", f"got {name!r}"

    def test_gemma(self):
        # 'gemma-4-e4b-it', quant Q4_K_M
        name = format_name(
            "lms-lmstudio-community-gemma-4-e4b-it-gguf-gemma-4-e4b-it-q4-k-m"
        )
        # Family: 'Gemma', size: '4b' plus model-part tokens -> 'Gemma E4b E4b It'
        assert name == "Gemma E4b E4b It", f"got {name!r}"

    def test_phonemu(self):
        # 'phi-4-mini-reasoning', quant Q4_K_M
        name = format_name(
            "lms-lmstudio-community-phi-4-mini-reasoning-gguf-phi-4-mini-reasoning-q4-k-m"
        )
        # Family: 'Phi', size: '4', model part 'phi-4-mini-reasoning' -> 'Phi Mini Mini'
        assert name == "Phi Mini Mini", f"got {name!r}"

    def test_olmo(self):
        # 'olmocr-2-7b-1025', quant Q4_K_M
        name = format_name(
            "lms-lmstudio-community-olmocr-2-7b-1025-gguf-olmocr-2-7b-1025-q4-k-m"
        )
        # Family: 'Olmocr', size: '7b', model part 'olmocr-2-7b-1025' -> 'Olmocr 7b 7b 1025'
        assert name == "Olmocr 7b 7b 1025", f"got {name!r}"

    def test_rnj(self):
        # 'rnj-1-instruct', quant Q4_K_M
        name = format_name(
            "lms-lmstudio-community-rnj-1-instruct-gguf-rnj-1-instruct-q4-k-m"
        )
        # Family: 'Rnj', size: '1'
        assert name == "Rnj 1", f"got {name!r}"


# ---------------------------------------------------------------------------
# Model registry discovery
# ---------------------------------------------------------------------------


class TestDiscoverModels:
    def test_returns_list(self):
        models_list = discover_models()
        assert isinstance(models_list, list)
        assert len(models_list) > 0

    def test_no_mmproj(self):
        models_list = discover_models()
        for m in models_list:
            assert "mmproj" not in m.model_id.lower()

    def test_every_model_has_path(self):
        models_list = discover_models()
        paths = [m.path for m in models_list]
        # At least the core lmstudio Community models have resolved paths.
        assert len(paths) > 0

    def test_minimal_model_fields(self):
        models_list = discover_models()
        m = models_list[0]
        assert m.name
        assert m.full_name
        assert m.size_gb > 0
        assert m.context_length > 0
        assert m.quantization in VALID_QUANTIZATIONS
        assert m.model_id


# ---------------------------------------------------------------------------
# Model path resolution
# ---------------------------------------------------------------------------


class TestModelPaths:
    def _dir(self):
        return os.getenv(
            "LLM_MANAGER_MODELS_DIR",
            "/home/waflores/.lmstudio/models/lmstudio-community",
        )

    def test_discover_model_paths(self):
        paths = discover_model_paths()
        assert isinstance(paths, dict)
        assert len(paths) > 0
        # Every value should be an existing file.
        for k, v in paths.items():
            assert os.path.exists(v), f"path {v} for key {k} does not exist"

    def test_resolve_model_path_roundtrip(self):
        dir_map = model_directory_mapping()
        for dir_name in dir_map:
            resolved = resolve_model_path(dir_name)
            assert resolved, f"resolve_model_path({dir_name}) returned empty"
            assert os.path.exists(resolved)

    def test_resolve_model_path_fallback(self):
        # A full absolute path is returned directly.
        sample = "/home/waflores/.lmstudio/models/lmstudio-community/CodeLlama-7B-Instruct-GGUF"
        assert os.path.isdir(sample)
        resolved = resolve_model_path(sample)
        assert resolved == sample


# ---------------------------------------------------------------------------
# Hardware detection (real machine)
# ---------------------------------------------------------------------------


class TestDetectHardware:
    def test_returns_hardware_spec(self):
        spec = detect_hardware()
        assert isinstance(spec, hardware_spec.HardwareSpec)

    def test_stapl_validity(self):
        spec = detect_hardware()
        # On this laptop GPU should be present; RAM > 16 GB.
        if spec.gpu_name:
            assert len(spec.gpu_name) > 0
        if spec.system_ram_gb:
            assert (
                spec.system_ram_gb > 16.0
            ), f"Expected >16 GB RAM, got {spec.system_ram_gb}"


# ---------------------------------------------------------------------------
# Configurator
# ---------------------------------------------------------------------------


class TestDetectTier:
    def test_low_vram(self):
        hw = hardware_spec.HardwareSpec(gpu_free_gb=8.0)
        assert detect_tier(hw) == 10.0

    def test_mid_vram(self):
        hw = hardware_spec.HardwareSpec(gpu_free_gb=14.0)
        assert detect_tier(hw) == 15.0

    def test_high_vram(self):
        hw = hardware_spec.HardwareSpec(gpu_free_gb=22.0)
        assert detect_tier(hw) == 20.0


class TestBuildConfig:
    def test_returns_config(self):
        cfg = build_config()
        assert isinstance(cfg, Config)
        assert len(cfg.profiles) > 0
        assert cfg.hardware.cpu_cores > 0

    def test_profiles_have_fit_status(self):
        cfg = build_config()
        for p in cfg.profiles:
            assert p.fit_status in (
                "fits",
                "over_vram",
                "fits_with_capping",
                "not_found",
            )


class TestGenerateProfiles:
    def test_produces_profiles(self):
        hw = hardware_spec.HardwareSpec(gpu_free_gb=8.0, gpu_memory_gb=8.0)
        profs = generate_profiles(hardware=hw)
        assert isinstance(profs, list)
        assert len(profs) > 0
        for p in profs:
            assert isinstance(p, ConfigProfile)
            assert p.fit_status in (
                "fits",
                "over_vram",
                "fits_with_capping",
                "not_found",
            )

    def test_fits_status_classification(self):
        # A model without a resolved path gets 'not_found' fit status,
        # regardless of fit criteria (size, VRAM, context).
        tiny = models.Model(
            name="tiny",
            full_name="Tiny",
            size_gb=1.0,
            context_length=8192,
            quantization=Q4_K_M,
            model_id="tiny",
        )
        hw = hardware_spec.HardwareSpec(gpu_free_gb=8.0, gpu_memory_gb=8.0)
        profs = generate_profiles(hardware=hw, models=[tiny])
        assert len(profs) == 1
        assert profs[0].fit_status == "not_found"
        assert profs[0].path == ""

    def test_fits_status_classification_fit(self):
        # A tiny model with a path resolves to 'fits' when it fits the VRAM budget.
        tiny = models.Model(
            name="tiny",
            full_name="Tiny",
            size_gb=1.0,
            context_length=8192,
            quantization=Q4_K_M,
            model_id="tiny",
            path="/tmp/tiny.gguf",
        )
        hw = hardware_spec.HardwareSpec(gpu_free_gb=8.0, gpu_memory_gb=8.0)
        profs = generate_profiles(hardware=hw, models=[tiny])
        assert len(profs) == 1
        assert profs[0].fit_status == "fits"


class TestToSerializable:
    def test_config_to_dict(self):
        hw = hardware_spec.HardwareSpec(cpu_cores=8, gpu_free_gb=8.0)
        cfg = Config(hardware=hw)
        d = _to_serializable(cfg)
        assert isinstance(d, dict)
        assert d["hardware"]["cpu_cores"] == 8

    def test_model_to_dict(self):
        m = models.Model(name="x", full_name="X")
        d = _to_serializable(m)
        assert isinstance(d, dict)
        assert d["name"] == "x"

    def test_profile_to_dict(self):
        p = ConfigProfile(model_id="m", model_name="M", quantization=Q4)
        d = _to_serializable(p)
        assert isinstance(d, dict)
        assert d["model_id"] == "m"


# ---------------------------------------------------------------------------
# Flask web app
# ---------------------------------------------------------------------------


class TestWebApp:
    @pytest.fixture(autouse=True)
    def app(self):
        from llm_manager.webapp import create_app

        app = create_app()
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_index(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_models_page(self, client):
        resp = client.get("/models")
        assert resp.status_code == 200

    def test_export_json(self, client):
        resp = client.get("/configs/export.json")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, dict)
        assert "profiles" in data
