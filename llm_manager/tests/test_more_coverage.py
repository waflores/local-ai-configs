"""Additional test coverage for llm_manager.

Covers:
- llm_manager/hardware.py (exception-handling branches)
- llm_manager/configurator.py (context-capping fallback branches)
- llm_manager/models.py (ModelLoader legacy class)
- llm_manager/webapp.py (Flask route handlers)
- llm_manager/loader.py (discovery/enrichment edge cases)
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm_manager import hardware
from llm_manager.configurator import Config
from llm_manager.loader import (
    discover_models_on_disk,
    discover_models_with_verification,
    enrich_from_config,
    enrich_with_verification,
    parse_verification_metadata,
)
from llm_manager.models import (
    Model,
    ModelLoader,
)
from llm_manager.webapp import create_app


# ============================================================================
# llm_manager/hardware.py
# ============================================================================
class TestHardwareExceptionHandling:
    """Tests for hardware.py exception-handling branches."""

    def test_nvidia_smi_fails(self, monkeypatch):
        monkeypatch.setattr(
            hardware,
            "_run",
            lambda cmd, **kwargs: (_ for _ in ()).throw(
                OSError("nvidia-smi not found")
            ),
        )
        spec = hardware.detect_hardware()
        assert spec.gpu_name == ""
        assert spec.gpu_memory_gb == 0.0
        assert spec.gpu_free_gb == 0.0

    def test_nvidia_smi_returns_invalid_memory(self, monkeypatch):
        monkeypatch.setattr(
            hardware,
            "_run",
            lambda cmd, **kwargs: types.SimpleNamespace(
                stdout="NVIDIA GeForce RTX 5070 Laptop GPU, not_a_number, 7787\n",
                stderr="",
                returncode=0,
            ),
        )
        spec = hardware.detect_hardware()
        assert spec.gpu_name == "NVIDIA GeForce RTX 5070 Laptop GPU"
        assert spec.gpu_memory_gb == 0.0
        assert spec.gpu_free_gb == 7.6044921875

    def test_nvidia_smi_returns_invalid_free(self, monkeypatch):
        monkeypatch.setattr(
            hardware,
            "_run",
            lambda cmd, **kwargs: types.SimpleNamespace(
                stdout="NVIDIA GeForce RTX 5070 Laptop GPU, 8151, not_a_number\n",
                stderr="",
                returncode=0,
            ),
        )
        spec = hardware.detect_hardware()
        assert spec.gpu_name == "NVIDIA GeForce RTX 5070 Laptop GPU"
        assert spec.gpu_memory_gb == 7.9599609375
        assert spec.gpu_free_gb == 0.0

    def test_free_is_empty(self, monkeypatch):
        monkeypatch.setattr(
            hardware,
            "_run",
            lambda cmd, **kwargs: types.SimpleNamespace(
                stdout="", stderr="", returncode=1
            ),
        )
        spec = hardware.detect_hardware()
        assert spec.system_ram_gb == 0.0

    def test_free_returns_invalid_memory(self, monkeypatch):
        monkeypatch.setattr(
            hardware,
            "_run",
            lambda cmd, **kwargs: types.SimpleNamespace(
                stdout="Mem: not_a_number, 5000\n", stderr="", returncode=0
            ),
        )
        spec = hardware.detect_hardware()
        assert spec.system_ram_gb == 0.0

    def test_nproc_fails(self, monkeypatch):
        monkeypatch.setattr(
            hardware,
            "_run",
            lambda cmd, **kwargs: types.SimpleNamespace(
                stdout="", stderr="", returncode=1
            ),
        )
        spec = hardware.detect_hardware()
        assert spec.cpu_cores == 0

    def test_nproc_returns_invalid_value(self, monkeypatch):
        monkeypatch.setattr(
            hardware,
            "_run",
            lambda cmd, **kwargs: types.SimpleNamespace(
                stdout="not_a_number\n", stderr="", returncode=0
            ),
        )
        spec = hardware.detect_hardware()
        assert spec.cpu_cores == 0


# ============================================================================
# llm_manager/configurator.py
# ============================================================================
class TestConfiguratorEdgeCases:
    """Tests for configurator.py fallback/capping branches."""

    def test_cap_context_with_negative_safe(self):
        model = Model(name="test", full_name="Test")
        model.memory_safe_context = -1
        from llm_manager.configurator import cap_context

        ctx, safe = cap_context(model, None)
        assert ctx == model.context_length
        assert safe == model.context_length

    def test_cap_context_with_zero_safe(self):
        model = Model(name="test", full_name="Test", context_length=4096)
        model.memory_safe_context = 0
        from llm_manager.configurator import cap_context

        ctx, safe = cap_context(model, None)
        assert ctx == 4096
        assert safe == 4096

    def test_detect_tier_with_high_free(self):
        from llm_manager.configurator import detect_tier

        spec = types.SimpleNamespace(gpu_free_gb=30.0, gpu_memory_gb=30.0)
        assert detect_tier(spec) == 20.0


class TestBuildConfig:
    """Tests for build_config() (normally covered by test_llm_manager.py)."""

    def test_build_config_returns_config_object(self):
        from llm_manager.configurator import build_config

        cfg = build_config()
        assert isinstance(cfg, Config)
        assert len(cfg.profiles) > 0
        assert cfg.hardware.cpu_cores > 0
        assert cfg.generated_at != ""


# ============================================================================
# llm_manager/models.py (ModelLoader legacy class)
# ============================================================================
class TestModelLoader:
    """Tests for the legacy ModelLoader class."""

    def test_model_loader_init_without_files(self, tmp_path, monkeypatch):
        loader = ModelLoader()
        loader._config_path = str(tmp_path / "no_config.yaml")
        loader._context_dir = str(tmp_path / "no_context")
        model_count = loader.model_count
        assert model_count == 0

    def test_model_loader_init_with_files(self, tmp_path, monkeypatch):
        loader = ModelLoader()
        config = tmp_path / "config.yaml"
        context = tmp_path / "context"
        config.parent.mkdir(parents=True, exist_ok=True)
        context.mkdir(exist_ok=True)

        config.write_text(
            "context: /fake/path\n"
            "context-dir: /fake/context\n"
            "base: /fake/base\n"
            "models:\n"
            "  - name: IBM Granite 4 Tiny\n"
            "    provider: llama.cpp\n"
            "    model: granite-4-h-tiny\n"
            "    quantization: Q4_K_M\n"
            "    ctx: 4096\n"
            "    device: auto\n"
            "    precision: gguf\n"
            "    disk: 2.0\n"
        )
        context.mkdir(exist_ok=True)
        json_file = context / "lms-lmstudio-community-ibm-granite-4-h-tiny-q4-k-m.json"
        json_file.write_text(
            json.dumps(
                {
                    "models": [
                        {
                            "model": "lms-lmstudio-community-ibm-granite-4-h-tiny-q4-k-m:latest",
                            "targetTokens": "4096",
                            "declaredContext": "4096",
                            "modelSizeGB": "2.0",
                            "memoryLimitedContext": "2048",
                            "recommendedContext": "4096",
                            "status": "available",
                        }
                    ]
                }
            )
        )
        loader._config_path = str(config)
        loader._context_dir = context  # Path object, not str

        models = loader.load_all()
        assert len(models) == 1
        model = models[0]
        # The JSON file's "model" field returns the full identifier
        # (lms-lmstudio-community-ibm-granite-4-h-tiny-q4-k-m), not just
        # the directory name.  The test asserts against the field value.
        assert model.name == "lms-lmstudio-community-ibm-granite-4-h-tiny-q4-k-m"
        assert model.context_length == 4096
        assert model.memory_safe_context == 2048

    def test_model_loader_get_available(self, tmp_path, monkeypatch):
        loader = ModelLoader()
        loader._config_path = str(tmp_path / "config.yaml")
        loader._context_dir = str(tmp_path / "context")
        loader._models = {
            "model1": type("M", (), {"status": "available", "name": "a"})(),
            "model2": type("M", (), {"status": "swapped", "name": "b"})(),
            "model3": type("M", (), {"status": "loaded", "name": "c"})(),
        }
        assert len(loader.get_available()) == 1
        assert len(loader.get_loaded()) == 1
        assert len(loader.get_swapped()) == 1

    def test_model_loader_get_models_auto(self, tmp_path, monkeypatch):
        loader = ModelLoader()
        loader._config_path = str(tmp_path / "config.yaml")
        loader._context_dir = str(tmp_path / "context")
        loader._models = {
            "a": type("M", (), {"status": "available", "name": "a"})(),
            "b": type("M", (), {"status": "available", "name": "b"})(),
        }
        assert len(loader.get_models()) == 2
        assert len(loader.get_models(device="auto")) == 2

    def test_model_loader_get_models_cpu(self, tmp_path, monkeypatch):
        loader = ModelLoader()
        loader._config_path = str(tmp_path / "config.yaml")
        loader._context_dir = str(tmp_path / "context")
        loader._models = {
            "a": type(
                "M", (), {"status": "available", "name": "a", "device": "cuda"}
            )(),
            "b": type("M", (), {"status": "available", "name": "b", "device": "cpu"})(),
            "c": type(
                "M", (), {"status": "available", "name": "c", "device": "cuda"}
            )(),
        }
        assert len(loader.get_models(device="cpu")) == 1
        assert loader.get_models(device="cpu")[0].name == "b"

    def test_model_loader_get_models_cuda(self, tmp_path, monkeypatch):
        loader = ModelLoader()
        loader._config_path = str(tmp_path / "config.yaml")
        loader._context_dir = str(tmp_path / "context")
        loader._models = {
            "a": type(
                "M", (), {"status": "available", "name": "a", "device": "cuda"}
            )(),
            "b": type("M", (), {"status": "available", "name": "b", "device": "cpu"})(),
            "c": type(
                "M", (), {"status": "available", "name": "c", "device": "cuda"}
            )(),
        }
        assert len(loader.get_models(device="cuda")) == 2

    def test_model_loader_print_model_summary(self, tmp_path, monkeypatch, capsys):
        loader = ModelLoader()
        loader._config_path = str(tmp_path / "config.yaml")
        loader._context_dir = str(tmp_path / "context")
        loader._models = {
            "a": type(
                "M",
                (),
                {
                    "full_name": "A",
                    "size_gb": 2.0,
                    "context_length": 4096,
                    "quantization": "Q4_K_M",
                },
            )(),
            "b": type(
                "M",
                (),
                {
                    "full_name": "B",
                    "size_gb": 1.0,
                    "context_length": 2048,
                    "quantization": "Q5_K_M",
                },
            )(),
        }
        loader.print_model_summary()
        output = capsys.readouterr().out
        assert "LLM Model Registry" in output

    def test_model_loader_save_load_model_list(self, tmp_path):
        loader = ModelLoader()
        loader._config_path = str(tmp_path / "config.yaml")
        loader._context_dir = str(tmp_path / "context")
        loader._models = {
            "a": type(
                "M",
                (),
                {
                    "model_id": "a",
                    "full_name": "A",
                    "parameters": "7B",
                    "size_gb": 2.0,
                    "context_length": 4096,
                    "quantization": "Q4_K_M",
                    "precision": "gguf",
                    "status": "available",
                    "version": "latest",
                    "hardware_constraint": "VRAM: 2.0 GB (needs 8.0 GB)",
                },
            )(),
        }
        loader.save_model_list(str(tmp_path / "models.json"))
        loaded = loader.load_model_list(str(tmp_path / "models.json"))
        assert "a" in loaded
        assert loaded["a"]["full_name"] == "A"

    def test_model_loader_parameters_b_property(self):
        model = Model(name="test", full_name="Test", size_gb=4.0, quantization="Q4_K_M")
        assert model.parameters_b == 8.0

    def test_model_loader_parameters_b_for_f16(self):
        model = Model(name="test", full_name="Test", size_gb=4.0, quantization="F16")
        assert model.parameters_b == 2.0

    def test_model_loader_fits_in(self):
        model = Model(
            name="test", full_name="Test", size_gb=4.0, memory_safe_context=4096
        )
        assert model.fits_in(vram_gb=5.0, ctx_size=4096)
        assert not model.fits_in(vram_gb=3.0, ctx_size=4096)

    def test_model_loader_fits_in_subcontext(self):
        model = Model(
            name="test", full_name="Test", size_gb=4.0, memory_safe_context=4096
        )
        assert model.fits_in(vram_gb=3.5, ctx_size=2048)


# ============================================================================
# llm_manager/webapp.py
# ============================================================================
class TestWebApp:
    """Tests for the Flask web app route handlers."""

    def test_create_app(self):
        app = create_app()
        assert app is not None
        assert hasattr(app, "route")

    def test_shell_returns_app_without_reloader(self):
        app = create_app()
        app2 = create_app()
        assert app is not app2

    def test_create_app_with_custom_config(self):
        app = create_app()
        assert app is not None

    def test_hardware_page_success(self, monkeypatch):
        """Test the /hardware route when hardware detection succeeds."""
        from llm_manager.webapp import create_app

        app = create_app()
        with app.test_client() as client:
            # Monkey-patch detect_hardware to return a known spec
            monkeypatch.setattr(
                "llm_manager.webapp.detect_hardware",
                lambda: types.SimpleNamespace(
                    cpu_cores=8,
                    gpu_name="Test GPU",
                    gpu_memory_gb=8.0,
                    gpu_free_gb=6.0,
                    system_ram_gb=16.0,
                    system_disk_gb=500.0,
                ),
            )
            response = client.get("/hardware")
            assert response.status_code == 200
            assert b"Test GPU" in response.data

    def test_hardware_page_fallback(self, monkeypatch):
        """Test the /hardware route when hardware detection fails."""
        from llm_manager.webapp import create_app

        app = create_app()
        with app.test_client() as client:
            monkeypatch.setattr(
                "llm_manager.webapp.detect_hardware",
                lambda: (_ for _ in ()).throw(RuntimeError("no GPU")),
            )
            response = client.get("/hardware")
            assert response.status_code == 200
            assert b"Hardware" in response.data

    def test_configs_page_success(self):
        """Test the /configs route when build_config succeeds."""
        from llm_manager.webapp import create_app

        app = create_app()
        with app.test_client() as client:
            response = client.get("/configs")
            assert response.status_code == 200
            assert b"Configurations" in response.data

    def test_configs_page_error(self, monkeypatch):
        """Test the /configs route when build_config raises."""
        from llm_manager.webapp import create_app

        app = create_app()
        with app.test_client() as client:
            monkeypatch.setattr(
                "llm_manager.webapp.build_config",
                lambda: (_ for _ in ()).throw(RuntimeError("boom")),
            )
            response = client.get("/configs")
            assert response.status_code == 200
            assert b"boom" in response.data

    def test_export_configs(self):
        """Test the /configs/export.json route."""
        from llm_manager.webapp import create_app

        app = create_app()
        with app.test_client() as client:
            response = client.get("/configs/export.json")
            assert response.status_code == 200
            assert b"profiles" in response.data

    def test_reload_endpoint(self, monkeypatch):
        """Test the POST /reload endpoint."""
        from llm_manager.webapp import create_app

        app = create_app()
        with app.test_client() as client:
            monkeypatch.setattr(
                "llm_manager.webapp.detect_hardware",
                lambda: types.SimpleNamespace(
                    cpu_cores=4,
                    gpu_name="Test",
                    gpu_memory_gb=4.0,
                    gpu_free_gb=2.0,
                    system_ram_gb=8.0,
                    system_disk_gb=250.0,
                ),
            )
            response = client.post("/reload")
            assert response.status_code == 200
            data = response.get_json()
            assert data is not None
            assert "hardware" in data

    def test_shell_function(self):
        """Test the shell() function returns the app."""
        from llm_manager.webapp import shell

        app = shell()
        assert app is not None


# ============================================================================
# llm_manager/loader.py edge cases
# ============================================================================
class TestLoaderEdgeCases:
    """Tests for loader.py edge cases and fallback branches."""

    def test_discover_models_with_verification_empty(self, tmp_path, monkeypatch):
        models_dir = tmp_path / "models"
        models_dir.mkdir()
        (models_dir / "empty").mkdir()
        result = discover_models_with_verification(models_dir=str(models_dir))
        assert result == []

    def test_enrich_with_verification_no_context_dir(self, tmp_path):
        models = [Model(name="test-model", full_name="Test Model")]
        context_dir = tmp_path / "no_such_dir"
        enrich_with_verification(models, context_dir=context_dir, config_yaml=None)
        assert len(models) == 1
        assert models[0].size_gb == 0.0
        assert models[0].context_length == 0

    def test_enrich_with_verification_json_decode_error(self, tmp_path, monkeypatch):
        models = [Model(name="test-model", full_name="Test Model")]
        context_dir = tmp_path / "context"
        context_dir.mkdir()
        bad_json = context_dir / "bad.json"
        bad_json.write_text("not valid json{{{")
        enrich_with_verification(models, context_dir=context_dir, config_yaml=None)
        assert len(models) == 1
        assert models[0].size_gb == 0.0

    def test_enrich_with_verification_empty_model_id(self, tmp_path, monkeypatch):
        models = [Model(name="test-model", full_name="Test Model")]
        context_dir = tmp_path / "context"
        context_dir.mkdir()
        json_file = context_dir / "empty.json"
        json_file.write_text(json.dumps({"model": ""}))
        enrich_with_verification(models, context_dir=context_dir, config_yaml=None)
        assert len(models) == 1

    def test_enrich_with_verification_no_matching_key(self, tmp_path, monkeypatch):
        models = [Model(name="different-model", full_name="Different Model")]
        context_dir = tmp_path / "context"
        context_dir.mkdir()
        json_file = context_dir / "test.json"
        json_file.write_text(
            json.dumps(
                {
                    "model": "lms-lmstudio-community-test-model-q4-k-m:latest",
                    "declaredContext": "4096",
                    "verification": {
                        "memoryLimitedContext": "2048",
                        "recommendedContext": "4096",
                    },
                }
            )
        )
        enrich_with_verification(models, context_dir=context_dir, config_yaml=None)
        assert len(models) == 1
        assert models[0].size_gb == 0.0

    def test_enrich_with_verification_hotswap_model_id(self, tmp_path, monkeypatch):
        models = [Model(name="hotswap-7b", full_name="HotSwap 7B")]
        context_dir = tmp_path / "context"
        context_dir.mkdir()
        # JSON filename determines the identifier via _json_identifier()
        json_file = context_dir / "hotswap-7b.json"
        json_file.write_text(
            json.dumps(
                {
                    "model": "hotswap-7b-gguf-hotswap-7b-q4-k-m:latest",
                    "declaredContext": "4096",
                    "modelSizeGB": "2.0",
                    "verification": {
                        "memoryLimitedContext": "2048",
                        "recommendedContext": "4096",
                        "status": "available",
                    },
                }
            )
        )
        enrich_with_verification(models, context_dir=context_dir, config_yaml=None)
        assert len(models) == 1
        assert models[0].size_gb == 2.0
        assert models[0].context_length == 4096
        assert models[0].memory_safe_context == 2048
        assert models[0].extra.get("recommended_context") == 4096
        assert models[0].extra.get("status") == "available"

    def test_enrich_from_config_missing_models_section(self, tmp_path):
        models = [Model(name="test-model", full_name="Test Model")]
        config_yaml = tmp_path / "no_models.yaml"
        config_yaml.write_text("context: /fake\n")
        enrich_from_config(models, config_yaml)
        assert len(models) == 1

    def test_enrich_from_config_empty_models_section(self, tmp_path):
        models = [Model(name="test-model", full_name="Test Model")]
        config_yaml = tmp_path / "empty.yaml"
        config_yaml.write_text("context: /fake\nmodels: []\n")
        enrich_from_config(models, config_yaml)
        assert len(models) == 1

    def test_parse_verification_metadata(self, tmp_path):
        models = {}
        json_path = tmp_path / "test.json"
        json_path.write_text(
            json.dumps(
                {
                    "model": "lms-lmstudio-community-test-q4-k-m:latest",
                    "declaredContext": "8192",
                    "modelSizeGB": "2.0",
                    "verification": {
                        "memoryLimitedContext": "4096",
                        "recommendedContext": "8192",
                        "status": "available",
                    },
                }
            )
        )
        parse_verification_metadata(
            json_path, json.loads(json_path.read_text()), models
        )
        assert len(models) == 1
        model = models["test"]
        assert model.size_gb == 2.0
        assert model.context_length == 8192
        assert model.memory_safe_context == 4096
        assert model.extra.get("recommended_context") == 8192
        assert model.extra.get("status") == "available"

    def test_extract_quantization_from_file_known_tags(self):
        from llm_manager.loader import extract_quantization_from_file

        assert extract_quantization_from_file("model-Q4_K_M.gguf") == "Q4_K_M"
        assert extract_quantization_from_file("model-Q5_K_M.gguf") == "Q5_K_M"
        assert extract_quantization_from_file("model-Q5_K_M_K_V.gguf") == "Q5_K_M_K_V"
        assert extract_quantization_from_file("model-Q8_0.gguf") == "Q8_0"
        assert extract_quantization_from_file("model-F16.gguf") == "F16"
        assert extract_quantization_from_file("model-BF16.gguf") == "BF16"
        assert extract_quantization_from_file("model-Q3_K_M.gguf") == "Q3_K_M"
        assert extract_quantization_from_file("model-Q2_K.gguf") == "Q2_K"

    def test_extract_quantization_from_file_unknown_tags(self):
        from llm_manager.loader import extract_quantization_from_file

        assert extract_quantization_from_file("model-unknown.gguf") == "Q4_K_M"
        assert extract_quantization_from_file("model.gguf") == "Q4_K_M"

    def test_discover_models_on_disk_empty_dir(self, tmp_path):
        models_dir = tmp_path / "empty"
        models_dir.mkdir()
        result = discover_models_on_disk(models_dir=str(models_dir))
        assert result == []

    def test_discover_models_on_disk_subdirectory(self, tmp_path):
        models_dir = tmp_path / "lmstudio-community"
        models_dir.mkdir()
        (models_dir / "CodeLlama-7B-Instruct-GGUF").mkdir()
        (models_dir / "other").mkdir()
        (models_dir / "CodeLlama-7B-Instruct-GGUF" / "model.gguf").write_bytes(b"x")
        (models_dir / "other" / "data.txt").write_bytes(b"x")
        result = discover_models_on_disk(models_dir=str(models_dir))
        assert len(result) == 1
        # The function strips the -GGUF suffix from directory names
        assert result[0].name == "CodeLlama-7B-Instruct"
        assert result[0].path.endswith("model.gguf")

    def test_discover_models_on_disk_skips_mmproj(self, tmp_path):
        models_dir = tmp_path / "lmstudio-community"
        models_dir.mkdir()
        (models_dir / "model-q4-k-m").mkdir()
        (models_dir / "model-q4-k-m" / "model.gguf").write_bytes(b"x")
        (models_dir / "model-q4-k-m" / "model-q4-k-m-mmproj.gguf").write_bytes(b"x")
        result = discover_models_on_disk(models_dir=str(models_dir))
        assert len(result) == 1

    def test_discover_models_on_disk_odd_quant_tag(self, tmp_path):
        models_dir = tmp_path / "lmstudio-community"
        models_dir.mkdir()
        (models_dir / "weird-model").mkdir()
        (models_dir / "weird-model" / "weird-model-q4-k-m.gguf").write_bytes(b"x")
        result = discover_models_on_disk(models_dir=str(models_dir))
        assert len(result) == 1
        assert result[0].quantization == "Q4_K_M"

    def test_enrich_with_verification_no_files(self, tmp_path):
        models = [Model(name="test-model", full_name="Test Model")]
        context_dir = tmp_path / "context"
        context_dir.mkdir()
        result = enrich_with_verification(
            models, context_dir=context_dir, config_yaml=None
        )
        assert result is None
        assert len(models) == 1
        assert models[0].size_gb == 0.0
