"""Model file resolution.

The llama-swap ``config.yaml`` stores commands rather than explicit model file
paths, so we resolve concrete model file paths by scanning the actual on-disk
model directory. This keeps the manager decoupled from the config format.
"""

from __future__ import annotations

import os

DEFAULT_MODELS_DIR = "/home/waflores/.lmstudio/models/lmstudio-community"


def discover_model_paths(models_dir: str | None = None) -> dict[str, str]:
    """Walk ``models_dir`` and return ``{dir_name: full_path}``.

    Each model directory (a directory whose name ends with ``-GGUF``) is keyed
    by its name; the value is the path to the first ``.gguf`` file found inside
    that directory.  This gives a clean ``{model_dir: "/full/path/to/gguf"}``
    mapping that ``resolve_model_path`` can index in reverse.

    Only GGUF files inside model directories are returned.
    """
    models_dir = models_dir or DEFAULT_MODELS_DIR
    paths: dict[str, str] = {}
    if not os.path.isdir(models_dir):
        return paths

    for entry in sorted(os.listdir(models_dir)):
        full = os.path.join(models_dir, entry)
        if not os.path.isdir(full):
            continue
        gguf_files = sorted(
            os.path.join(full, n)
            for n in os.listdir(full)
            if n.lower().endswith(".gguf")
        )
        if not gguf_files:
            continue
        paths[entry] = gguf_files[0]

    return paths


def model_directory_mapping(models_dir: str | None = None) -> dict[str, str]:
    """Return ``{dir_name: dir_path}`` for the top-level model directories."""
    models_dir = models_dir or DEFAULT_MODELS_DIR
    mapping: dict[str, str] = {}
    if not os.path.isdir(models_dir):
        return mapping
    for entry in sorted(os.listdir(models_dir)):
        full = os.path.join(models_dir, entry)
        if os.path.isdir(full) and entry.lower().endswith("-gguf"):
            mapping[entry] = full
    return mapping


def resolve_model_path(model_key: str, models_dir: str | None = None) -> str:
    """Return the concrete model file path for a model directory key.

    ``model_key`` may be the directory name (e.g. ``CodeLlama-7B-Instruct-GGUF``),
    a full on-disk path (e.g.
    ``/home/waflores/.lmstudio/models/lmstudio-community/CodeLlama-7B-Instruct-GGUF``),
    or a relative path into the models directory (e.g.
    ``"mradermacher/zerank-1-small"``).  The returned path is the concrete GGUF
    file inside that directory.  This is the reverse of
    ``discover_model_paths``.
    """
    models_dir = models_dir or DEFAULT_MODELS_DIR
    # If the input is already a full path, just return it directly.
    if os.path.isabs(model_key):
        return model_key if os.path.exists(model_key) else ""
    bare = os.path.basename(model_key)
    if not bare:
        return ""

    paths = discover_model_paths(models_dir)

    # Try the full directory name first (may carry a trailing "-GGUF").
    if model_key in paths:
        return paths[model_key]
    # Try the directory name minus a trailing "-GGUF".
    if model_key.lower().endswith("-gguf"):
        candidate = model_key[: -len("-gguf")]
        if candidate in paths:
            return paths[candidate]
    # try lowercase match
    for key, full in paths.items():
        if key.lower() == model_key.lower():
            return full
        if key.lower().endswith(model_key.lower()):
            return full
    # Final fallback: substring search by directory name.
    for key, full in paths.items():
        if model_key.lower() in key.lower():
            return full
    return ""


def model_directory_mapping(models_dir: str | None = None) -> dict[str, str]:
    """Return ``{dir_name: dir_path}`` for the top-level model directories."""
    models_dir = models_dir or DEFAULT_MODELS_DIR
    mapping: dict[str, str] = {}
    if not os.path.isdir(models_dir):
        return mapping
    for entry in sorted(os.listdir(models_dir)):
        full = os.path.join(models_dir, entry)
        if os.path.isdir(full) and entry.lower().endswith("-gguf"):
            mapping[entry] = full
    return mapping


def find_gguf_in_model_dir(dir_path: str) -> str:
    """Return the path to the first ``.gguf`` file inside ``dir_path``."""
    if not os.path.isdir(dir_path):
        return ""
    gguf_files = sorted(
        os.path.join(dir_path, n)
        for n in os.listdir(dir_path)
        if n.lower().endswith(".gguf")
    )
    return gguf_files[0] if gguf_files else ""


def exists(model_path: str) -> bool:
    """Return True if the resolved model path points to an existing file."""
    return bool(model_path and os.path.exists(model_path))
