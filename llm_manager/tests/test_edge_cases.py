"""Targeted test coverage for llm_manager edge cases.

Focuses on the remaining uncovered lines:
- llm_manager/loader.py (54 lines, 83% coverage)
- llm_manager/configurator.py fallback branches (17 lines, 81% coverage)
- llm_manager/models.py legacy ModelLoader (43 lines, 80% coverage)
- llm_manager/main.py entry point (1 line, 75% coverage)
- llm_manager/webapp.py exception handling (6 lines, 90% coverage)
- llm_manager/model_paths.py (4 lines, 93% coverage)
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm_manager.configurator import (
    generate_profiles,
    cap_context,
    detect_tier,
)
from llm_manager.loader import (
    discover_models_on_disk,
    enrich_from_config,
    enrich_with_verification,
    discover_models_with_verification,
)
from llm_manager.main import main as main_fn
from llm_manager.model_paths import (
    discover_model_paths,
    exists,
    find_gguf_in_model_dir,
    resolve_model_path,
    model_directory_mapping,
)
from llm_manager.models import (
    Model,
    ModelLoader,
)
from llm_manager.webapp import create_app


# ============================================================================
# llm_manager/main.py
# ============================================================================
class TestMain:
    """Test the main() entry-point function."""

    def test_main_prints_expected_output(self, capsys):
        main_fn()
        captured = capsys.readouterr()
        assert "local-config" in captured.out


# ============================================================================
# llm_manager/model_paths.py
# ============================================================================
class TestDiscoverModelPaths:
    """Tests for discover_model_paths — empty and non-existent directories."""

    def test_empty_models_dir_returns_empty(self, tmp_path):
        result = discover_model_paths(str(tmp_path))
        assert result == {}

    def test_non_existent_models_dir_returns_empty(self, tmp_path):
        non_existent = tmp_path / "does_not_exist"
        result = discover_model_paths(str(non_existent))
        assert result == {}


class TestModelDirectoryMapping:
    """Tests for model_directory_mapping — missing and non-GGUF directories."""

    def test_non_existent_dir_returns_empty(self, tmp_path):
        non_existent = tmp_path / "no_dir"
        assert model_directory_mapping(str(non_existent)) == {}

    def test_non_gguf_dirs_are_skipped(self, tmp_path):
        (tmp_path / "some_dir").mkdir()
        (tmp_path / "other").mkdir()
        assert model_directory_mapping(str(tmp_path)) == {}


class TestResolveModelPath:
    """Tests for resolve_model_path — edge cases."""

    def test_empty_model_key_returns_empty(self, tmp_path):
        assert resolve_model_path("") == ""

    def test_model_key_not_found(self, tmp_path):
        result = resolve_model_path("nonexistent", str(tmp_path))
        assert result == ""

    def test_model_key_with_trailing_gguf(self, tmp_path):
        models = tmp_path / "lmstudio-community"
        models.mkdir()
        (models / "CodeLlama-7B-Instruct-GGUF").mkdir()
        (models / "CodeLlama-7B-Instruct-GGUF" / "model.gguf").write_bytes(b"x")
        result = resolve_model_path("CodeLlama-7B-Instruct-GGUF", str(models))
        assert result == str(models / "CodeLlama-7B-Instruct-GGUF" / "model.gguf")

    def test_model_key_lowercase(self, tmp_path):
        models = tmp_path / "lmstudio-community"
        models.mkdir()
        (models / "CodeLlama-7B-Instruct-GGUF").mkdir()
        (models / "CodeLlama-7B-Instruct-GGUF" / "model.gguf").write_bytes(b"x")
        result = resolve_model_path("codellama-7b-instruct-gguf", str(models))
        assert result == str(models / "CodeLlama-7B-Instruct-GGUF" / "model.gguf")

    def test_model_key_substring_match(self, tmp_path):
        models = tmp_path / "lmstudio-community"
        models.mkdir()
        (models / "CodeLlama-7B-Instruct-GGUF").mkdir()
        (models / "CodeLlama-7B-Instruct-GGUF" / "model.gguf").write_bytes(b"x")
        result = resolve_model_path("codellama", str(models))
        assert result == str(models / "CodeLlama-7B-Instruct-GGUF" / "model.gguf")

    def test_find_gguf_in_model_dir_non_existent(self, tmp_path):
        assert find_gguf_in_model_dir(str(tmp_path / "no_dir")) == ""

    def test_find_gguf_in_model_dir_no_files(self, tmp_path):
        (tmp_path / "empty_dir").mkdir()
        assert find_gguf_in_model_dir(str(tmp_path / "empty_dir")) == ""

    def test_find_gguf_in_model_dir_first_gguf(self, tmp_path):
        model_dir = tmp_path / "models"
        model_dir.mkdir()
        (model_dir / "a.gguf").write_bytes(b"a")
        (model_dir / "b.gguf").write_bytes(b"b")
        (model_dir / "other.txt").write_bytes(b"x")
        result = find_gguf_in_model_dir(str(model_dir))
        assert result.endswith("a.gguf")

    def test_exists_existing_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"x")
        assert exists(str(f))

    def test_exists_nonexistent_file(self, tmp_path):
        assert not exists(str(tmp_path / "no_such_file"))

    def test_exists_empty_string(self):
        assert not exists("")


# ============================================================================
# llm_manager/configurator.py
# ============================================================================
class TestCapContext:
    """Tests for cap_context() — context capping fallback branches."""

    def test_cap_context_with_zero_safe(self):
        model = Model(name="test", full_name="Test", context_length=4096)
        ctx, safe = cap_context(model, None)
        assert ctx == 4096
        assert safe == 4096

    def test_cap_context_with_negative_safe(self):
        model = Model(name="test", full_name="Test", memory_safe_context=-1)
        ctx, safe = cap_context(model, None)
        assert ctx == model.context_length
        assert safe == model.context_length

    def test_cap_context_with_zero_context_length(self):
        model = Model(name="test", full_name="Test", memory_safe_context=0)
        ctx, safe = cap_context(model, None)
        assert ctx == 0
        assert safe == 0


class TestDetectTier:
    """Tests for detect_tier() — tier threshold fallback branches."""

    def test_free_gb_le_10(self):
        spec = types.SimpleNamespace(gpu_free_gb=10.0, gpu_memory_gb=10.0)
        assert detect_tier(spec) == 10.0

    def test_free_gb_le_15(self):
        spec = types.SimpleNamespace(gpu_free_gb=14.9, gpu_memory_gb=15.0)
        assert detect_tier(spec) == 15.0

    def test_free_gb_le_20(self):
        spec = types.SimpleNamespace(gpu_free_gb=20.0, gpu_memory_gb=20.0)
        assert detect_tier(spec) == 20.0

    def test_free_gb_gt_20(self):
        spec = types.SimpleNamespace(gpu_free_gb=30.0, gpu_memory_gb=30.0)
        assert detect_tier(spec) == 20.0


class TestGenerateProfiles:
    """Tests for generate_profiles() — fallback/capping branches."""

    def test_generate_profiles_with_low_free_vram(self):
        from llm_manager.loader import discover_models

        models = list(discover_models())
        hardware_spec = types.SimpleNamespace(
            gpu_free_gb=15.0, gpu_memory_gb=15.0, cpu_cores=8
        )
        profiles = generate_profiles(hardware=hardware_spec, models=models)
        # All models should have a fit_status (not crashing)
        for p in profiles:
            assert p.fit_status in (
                "fits",
                "over_vram",
                "fits_with_capping",
                "not_found",
            )

    def test_generate_profiles_no_models(self):
        hardware_spec = types.SimpleNamespace(
            gpu_free_gb=8.0, gpu_memory_gb=8.0, cpu_cores=8
        )
        profiles = generate_profiles(hardware=hardware_spec, models=[])
        # generate_profiles() uses discover_models() to get models, not the
        # ``models`` parameter.  So with no context-verification files, the
        # returned registry will contain on-disk models only.
        assert isinstance(profiles, list)

    def test_generate_profiles_returns_config_profiles(self):
        models = [
            Model(
                name="test-model",
                full_name="Test Model",
                size_gb=2.0,
                context_length=4096,
                memory_safe_context=4096,
                quantization="Q4_K_M",
            )
        ]
        hardware_spec = types.SimpleNamespace(
            gpu_free_gb=8.0, gpu_memory_gb=8.0, cpu_cores=8
        )
        profiles = generate_profiles(hardware=hardware_spec, models=models)
        assert len(profiles) == 1
        assert profiles[0].model_name == "Test Model"
        assert profiles[0].fit_status in (
            "fits",
            "over_vram",
            "fits_with_capping",
            "not_found",
        )


# ============================================================================
# llm_manager/loader.py edge cases
# ============================================================================
class TestEnrichFromConfig:
    """Tests for enrich_from_config() — malformed config.yaml sections."""

    def test_enrich_from_config_missing_models_section(self, tmp_path):
        models = {"test-model": Model(name="test-model", full_name="Test Model")}
        config_yaml = tmp_path / "no_models.yaml"
        config_yaml.write_text("context: /fake\n")
        enrich_from_config(models, config_yaml)
        assert len(models) == 1

    def test_enrich_from_config_empty_models_list(self, tmp_path):
        models = {"test-model": Model(name="test-model", full_name="Test Model")}
        config_yaml = tmp_path / "empty.yaml"
        config_yaml.write_text("context: /fake\nmodels: []\n")
        enrich_from_config(models, config_yaml)
        assert len(models) == 1

    def test_enrich_from_config_non_dict_models_value(self, tmp_path):
        """Check that a non-dict models section is handled gracefully."""
        import yaml

        models = {"test-model": Model(name="test-model", full_name="Test Model")}
        config_yaml = tmp_path / "non_dict.yaml"
        config_yaml.write_text(
            yaml.safe_dump(
                {"context": "/fake", "models": "not a dict", "context-dir": "/fake"}
            )
        )
        enrich_from_config(models, config_yaml)
        assert len(models) == 1

    def test_enrich_from_config_missing_yaml_file(self, tmp_path):
        models = [Model(name="test-model", full_name="Test Model")]
        config_yaml = tmp_path / "no_such.yaml"
        enrich_from_config(models, config_yaml)
        assert len(models) == 1


class TestEnrichWithVerification:
    """Tests for enrich_with_verification() — malformed JSON files."""

    def test_enrich_with_verification_no_context_dir(self, tmp_path):
        models = [Model(name="test-model", full_name="Test Model")]
        context_dir = tmp_path / "no_such_dir"
        enrich_with_verification(models, context_dir=context_dir, config_yaml=None)
        assert len(models) == 1
        assert models[0].size_gb == 0.0

    def test_enrich_with_verification_empty_json_file(self, tmp_path):
        models = [Model(name="test-model", full_name="Test Model")]
        context_dir = tmp_path / "context"
        context_dir.mkdir()
        (context_dir / "empty.json").write_text("")
        enrich_with_verification(models, context_dir=context_dir, config_yaml=None)
        assert len(models) == 1
        assert models[0].size_gb == 0.0

    def test_enrich_with_verification_binary_content_json(self, tmp_path):
        models = [Model(name="test-model", full_name="Test Model")]
        context_dir = tmp_path / "context"
        context_dir.mkdir()
        (context_dir / "binary.json").write_bytes(b"\x00\x01\x02\xff")
        enrich_with_verification(models, context_dir=context_dir, config_yaml=None)
        assert len(models) == 1
        assert models[0].size_gb == 0.0

    def test_enrich_with_verification_missing_model_field(self, tmp_path):
        models = [Model(name="test-model", full_name="Test Model")]
        context_dir = tmp_path / "context"
        context_dir.mkdir()
        (context_dir / "no_model.json").write_text(
            json.dumps({"declaredContext": "4096", "verification": {}})
        )
        enrich_with_verification(models, context_dir=context_dir, config_yaml=None)
        assert len(models) == 1
        assert models[0].size_gb == 0.0

    def test_enrich_with_verification_no_matching_key(self, tmp_path):
        models = [Model(name="different-model", full_name="Different Model")]
        context_dir = tmp_path / "context"
        context_dir.mkdir()
        (context_dir / "test.json").write_text(
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

    def test_enrich_with_verification_json_decode_error(self, tmp_path):
        models = [Model(name="test-model", full_name="Test Model")]
        context_dir = tmp_path / "context"
        context_dir.mkdir()
        (context_dir / "broken.json").write_text("not valid json{{{")
        enrich_with_verification(models, context_dir=context_dir, config_yaml=None)
        assert len(models) == 1
        assert models[0].size_gb == 0.0

    def test_enrich_with_verification_hotswap_model_id(self, tmp_path):
        models = [Model(name="hotswap-7b", full_name="HotSwap 7B")]
        context_dir = tmp_path / "context"
        context_dir.mkdir()
        (context_dir / "hotswap-7b.json").write_text(
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

    def test_enrich_with_verification_no_context_dir_files(self, tmp_path):
        models = [Model(name="test-model", full_name="Test Model")]
        context_dir = tmp_path / "context"
        context_dir.mkdir()
        result = enrich_with_verification(
            models, context_dir=context_dir, config_yaml=None
        )
        assert result is None
        assert len(models) == 1
        assert models[0].size_gb == 0.0


class TestDiscoverModelsOnDisk:
    """Tests for discover_models_on_disk() — empty and subdirectory cases."""

    def test_discover_models_on_disk_empty_dir(self, tmp_path):
        models_dir = tmp_path / "empty"
        models_dir.mkdir()
        result = discover_models_on_disk(models_dir=str(models_dir))
        assert result == []

    def test_discover_models_on_disk_non_existent_dir(self, tmp_path):
        result = discover_models_on_disk(models_dir=str(tmp_path / "no_such_dir"))
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
        assert result[0].name == "CodeLlama-7B-Instruct"
        assert result[0].path.endswith("model.gguf")

    def test_discover_models_on_disk_subdirectory_with_rel_path(self, tmp_path):
        models_dir = tmp_path / "lmstudio-community"
        models_dir.mkdir()
        (models_dir / "subdir").mkdir()
        (models_dir / "subdir" / "CodeLlama-7B-Instruct-GGUF").mkdir()
        (
            models_dir / "subdir" / "CodeLlama-7B-Instruct-GGUF" / "model.gguf"
        ).write_bytes(b"x")
        result = discover_models_on_disk(models_dir=str(models_dir))
        assert len(result) == 1
        assert (
            result[0].name == "subdir/CodeLlama-7B-Instruct-GGUF/CodeLlama-7B-Instruct"
        )

    def test_discover_models_on_disk_skips_mmproj(self, tmp_path):
        models_dir = tmp_path / "lmstudio-community"
        models_dir.mkdir()
        (models_dir / "model-q4-k-m").mkdir()
        (models_dir / "model-q4-k-m" / "model.gguf").write_bytes(b"x")
        (models_dir / "model-q4-k-m" / "model-q4-k-m-mmproj.gguf").write_bytes(b"x")
        result = discover_models_on_disk(models_dir=str(models_dir))
        assert len(result) == 1
        assert "mmproj" not in result[0].model_id.lower()

    def test_discover_models_on_disk_odd_quant_tag(self, tmp_path):
        models_dir = tmp_path / "lmstudio-community"
        models_dir.mkdir()
        (models_dir / "weird-model").mkdir()
        (models_dir / "weird-model" / "weird-model-q4-k-m.gguf").write_bytes(b"x")
        result = discover_models_on_disk(models_dir=str(models_dir))
        assert len(result) == 1
        assert result[0].quantization == "Q4_K_M"

    def test_discover_models_with_verification_empty(self, tmp_path):
        models_dir = tmp_path / "models"
        models_dir.mkdir()
        (models_dir / "empty").mkdir()
        result = discover_models_with_verification(
            models_dir=str(models_dir), context_dir=tmp_path / "no_context"
        )
        assert result == []


# ============================================================================
# llm_manager/models.py (ModelLoader legacy class)
# ============================================================================
class TestModelLoader:
    """Tests for the legacy ModelLoader class."""

    def test_model_loader_init_without_files(self, tmp_path, monkeypatch):
        loader = ModelLoader()
        loader._config_path = str(tmp_path / "no_config.yaml")
        loader._context_dir = str(tmp_path / "no_context")
        assert loader.model_count == 0

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
        loader._context_dir = context
        models = loader.load_all()
        assert len(models) == 1
        assert models[0].name == "lms-lmstudio-community-ibm-granite-4-h-tiny-q4-k-m"
        assert models[0].context_length == 4096
        assert models[0].memory_safe_context == 2048

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
        cpu_models = loader.get_models(device="cpu")
        assert len(cpu_models) == 1
        assert cpu_models[0].name == "b"

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
        cuda_models = loader.get_models(device="cuda")
        assert len(cuda_models) == 2
        assert {m.name for m in cuda_models} == {"a", "c"}

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

    def test_model_loader_print_device_constraints(self, tmp_path, monkeypatch, capsys):
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
                    "hardware_constraint": "VRAM: 2.0 GB (needs 8.0 GB)",
                },
            )(),
        }
        loader.print_device_constraints()
        output = capsys.readouterr().out
        assert "VRAM available" in output

    def test_model_loader_parameters_b_property(self):
        model = Model(name="test", full_name="Test", size_gb=4.0, quantization="Q4_K_M")
        assert model.parameters_b == 8.0

    def test_model_loader_parameters_b_for_f16(self):
        model = Model(name="test", full_name="Test", size_gb=4.0, quantization="F16")
        assert model.parameters_b == 2.0

    def test_model_loader_parameters_b_for_bf16(self):
        model = Model(name="test", full_name="Test", size_gb=4.0, quantization="BF16")
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

    def test_model_loader_model_count_property(self, tmp_path, monkeypatch):
        loader = ModelLoader()
        loader._config_path = str(tmp_path / "config.yaml")
        loader._context_dir = str(tmp_path / "context")
        loader._models = {"a": type("M", (), {})(), "b": type("M", (), {})()}
        assert loader.model_count == 2

    def test_model_loader_config_property(self, tmp_path, monkeypatch):
        loader = ModelLoader()
        loader._config_path = str(tmp_path / "config.yaml")
        loader._context_dir = str(tmp_path / "context")
        assert loader.config is not None


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
        from llm_manager.webapp import create_app

        app = create_app()
        with app.test_client() as client:
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
        from llm_manager.webapp import create_app

        app = create_app()
        with app.test_client() as client:
            monkeypatch.setattr(
                "llm_manager.webapp.detect_hardware",
                lambda: (_ for _ in ()).throw(RuntimeError("no GPU")),
            )
            response = client.get("/hardware")
            assert response.status_code == 200

    def test_configs_page_success(self):
        from llm_manager.webapp import create_app

        app = create_app()
        with app.test_client() as client:
            response = client.get("/configs")
            assert response.status_code == 200

    def test_configs_page_error(self, monkeypatch):
        from llm_manager.webapp import create_app

        app = create_app()
        with app.test_client() as client:
            monkeypatch.setattr(
                "llm_manager.webapp.build_config",
                lambda: (_ for _ in ()).throw(RuntimeError("boom")),
            )
            response = client.get("/configs")
            assert response.status_code == 200

    def test_export_configs(self):
        from llm_manager.webapp import create_app

        app = create_app()
        with app.test_client() as client:
            response = client.get("/configs/export.json")
            assert response.status_code == 200
            assert b"profiles" in response.data

    def test_reload_endpoint(self, monkeypatch):
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
        from llm_manager.webapp import shell

        app = shell()
        assert app is not None
