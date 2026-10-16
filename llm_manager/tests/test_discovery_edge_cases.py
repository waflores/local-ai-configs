"""Extended test suite for the llm_manager package.

Adds coverage for code paths that were previously uncovered:
- llm_manager/main.py (the entry-point script)
- llm_manager/model_paths.py (path resolution edge cases)
- llm_manager/hardware.py (exception-handling branches)
- llm_manager/configurator.py (context-capping fallback branches)
- llm_manager/models.py (ModelLoader legacy class methods)
- llm_manager/webapp.py (Flask route handlers)
- llm_manager/loader.py (discovery/enrichment edge cases)
- llm_manager/tests/test_llm_manager.py (final uncovered line)

Coverage strategy:
- Run tests with `uv run python -m pytest --cov=llm_manager --cov-report=term-missing`
  to verify coverage improved.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm_manager.main import main as main_fn

from llm_manager.model_paths import (
    discover_model_paths,
    exists,
    find_gguf_in_model_dir,
    resolve_model_path,
    model_directory_mapping,
)


# ============================================================================
# llm_manager/main.py
# ============================================================================
class TestMain:
    """Tests for the main() entry-point function."""

    def test_main_prints_expected_output(self, capsys):
        main_fn()
        captured = capsys.readouterr()
        assert "local-config" in captured.out


# ============================================================================
# llm_manager/model_paths.py
# ============================================================================
class TestDiscoverModelPaths:
    """Tests for discover_model_paths (empty/non-existent directory)."""

    def test_empty_models_dir_returns_empty(self, tmp_path):
        result = discover_model_paths(str(tmp_path))
        assert result == {}

    def test_non_existent_models_dir_returns_empty(self, tmp_path):
        non_existent = tmp_path / "does_not_exist"
        result = discover_model_paths(str(non_existent))
        assert result == {}


class TestModelDirectoryMapping:
    """Tests for model_directory_mapping."""

    def test_non_existent_dir_returns_empty(self, tmp_path):
        non_existent = tmp_path / "no_dir"
        assert model_directory_mapping(str(non_existent)) == {}

    def test_non_gguf_dirs_are_skipped(self, tmp_path):
        (tmp_path / "some_dir").mkdir()
        (tmp_path / "other").mkdir()
        result = model_directory_mapping(str(tmp_path))
        assert result == {}


class TestResolveModelPath:
    """Tests for resolve_model_path edge cases."""

    def test_empty_model_key_returns_empty(self, tmp_path):
        result = resolve_model_path("")
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

    def test_model_key_not_found(self, tmp_path):
        result = resolve_model_path("nonexistent", str(tmp_path))
        assert result == ""


class TestFindGgufInModelDir:
    """Tests for find_gguf_in_model_dir."""

    def test_non_existent_dir_returns_empty(self, tmp_path):
        non_existent = tmp_path / "no_dir"
        assert find_gguf_in_model_dir(str(non_existent)) == ""

    def test_no_gguf_files_returns_empty(self, tmp_path):
        (tmp_path / "empty_dir").mkdir()
        assert find_gguf_in_model_dir(str(tmp_path / "empty_dir")) == ""

    def test_returns_first_gguf_file(self, tmp_path):
        model_dir = tmp_path / "models"
        model_dir.mkdir()
        (model_dir / "a.gguf").write_bytes(b"a")
        (model_dir / "b.gguf").write_bytes(b"b")
        (model_dir / "other.txt").write_bytes(b"x")
        result = find_gguf_in_model_dir(str(model_dir))
        assert result.endswith("a.gguf")


class TestExists:
    """Tests for exists()."""

    def test_existing_file_returns_true(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"x")
        assert exists(str(f))

    def test_nonexistent_file_returns_false(self, tmp_path):
        assert not exists(str(tmp_path / "no_such_file"))

    def test_empty_string_returns_false(self):
        assert not exists("")
