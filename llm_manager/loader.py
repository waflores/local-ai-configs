"""Model discovery and registry for the LLM manager.

Parses the ``context-verification/*.json`` files (which carry per-model
verification metadata such as size, verified context, and memory-safe context)
plus the llama-swap ``config.yaml`` so the app has a unified model registry.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from .model_paths import (
    DEFAULT_MODELS_DIR,
    model_directory_mapping,
    resolve_model_path,
)
from .models import Model
from .quantization import VALID_QUANTIZATIONS

# Default places the JSON files live, matching the existing repo layout.
DEFAULT_CONTEXT_DIR = Path(
    os.getenv(
        "LLM_MANAGER_CONTEXT_DIR",
        "/home/waflores/DevFolder/ai/local-config/context-verification",
    )
)
DEFAULT_CONFIG_YAML = Path(
    os.getenv(
        "LLM_MANAGER_CONFIG_YAML",
        "/home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml",
    )
)

# Matches the model identifier portion of a JSON filename, e.g.
# 'lms-lmstudio-community-codellama-7b-instruct-gguf-codellama-7b-instruct-q4-k-m'
# -> 'codellama-7b-instruct'. The identifier comes after the LAST '-gguf-' and
# before the final extension.
_JSON_ID_RE = re.compile(r"-(?:[a-z0-9]+-)+gguf-(?:[a-z0-9]+-)+\.json$")

# Map known sub-string patterns in the JSON identifier to the canonical
# config.yaml model key, e.g. 'codellama-7b-instruct' -> 'CodeLlama-7B-Instruct'.
# The value is the full config.yaml key INCLUDING the '-GGUF' suffix so it
# matches exactly what is stored in ``models.yaml``.
_CONFIG_KEY_ALIASES: dict[str, str] = {
    "codellama-7b-instruct": "CodeLlama-7B-Instruct",
    "deepseek-r1-0528-qwen3-8b": "DeepSeek-R1-0528-Qwen3-8B-GGUF",
    "devstral-small-2-24b-instruct-2512": "Devstral-Small-2-24B-Instruct-2512-GGUF",
    "lfm2-24b-a2b": "LFM2-24B-A2B-GGUF",
    "meta-llama-3-1-8b-instruct": "Meta-Llama-3.1-8B-Instruct",
    "ministral-3-14b-reasoning-2512": "Ministral-3-14B-Reasoning-2512-GGUF",
    "ministral-3-3b-instruct-2512": "Ministral-3-3B-Instruct-2512-GGUF",
    "mistral-nemo-instruct-2407": "Mistral-Nemo-Instruct-2407-GGUF",
    "nvidia-nemotron-3-nano-4b": "NVIDIA-Nemotron-3-Nano-4B-GGUF",
    "phi-4-mini-reasoning": "Phi-4-mini-reasoning-GGUF",
    "phi-4-reasoning-plus": "Phi-4-reasoning-plus-GGUF",
    "qwen3-4b-thinking-2507": "Qwen3-4B-Thinking-2507-GGUF",
    "qwen3-vl-8b-instruct": "Qwen3-VL-8B-Instruct-GGUF",
    "qwen3-5-9b": "Qwen3.5-9B-GGUF",
    "qwen3-6-27b": "Qwen3.6-27B-GGUF",
    "rnj-1-instruct": "rnj-1-instruct-GGUF",
    "granite-4-0-h-tiny": "granite-4-h-tiny",
    "fastcontext-1-0-4b-sft-q4-k-m": "FastContext-1.0-4B-SFT-Q4_K_M-GGUF",
    "gemma-4-e4b-it": "gemma-4-E4B-it-GGUF",
    "olmocr-2-7b-1025": "olmOCR-2-7B-1025-GGUF",
    "zerank-1-small": "zerank-1-small-gguf",
    "zerank-2": "zerank-2-gguf",
}

# Map a config.yaml model key to its canonical on-disk directory name,
# e.g. 'CodeLlama-7B-Instruct' -> 'CodeLlama-7B-Instruct-GGUF'.
# Populated at import time from the actual on-disk layout.
_CONFIG_DIR_NAME: dict[str, str] = {}


def _core_name(name: str) -> str:
    """Reduce a name to a comparable core: lowercase, dots in version numbers
    replaced by dashes ('4.0' -> '4-0').

    This is the canonical key we use to match config model names against the
    on-disk directory names.  We deliberately do NOT strip the suffix here, so
    'CodeLlama-7B-Instruct-GGUF' -> 'codellama-7b-instruct-gguf' and
    'granite-4-h-tiny' -> 'granite-4-h-tiny'.
    """
    n = name.lower().replace("_", "-")
    # Normalize dotted minor versions into dashes so that 'granite-4.0'
    # matches 'granite-4-0' and 'granite-4-h-tiny' matches '4.0-h-tiny'.
    n = re.sub(r"(\d+)\.(\d+)", r"\1-\2", n)
    return n


def _register_config_dir_name() -> None:
    """Populate a mapping from config.yaml model key to its on-disk directory name.

    The config.yaml keys (e.g. ``CodeLlama-7B-Instruct``) map to on-disk
    directories that carry a ``-GGUF`` suffix (e.g.
    ``CodeLlama-7B-Instruct-GGUF``).  We match on the base name and append
    ``-GGUF`` when needed.
    """
    import yaml

    config_path = Path(os.getenv("LLM_MANAGER_CONFIG_YAML", DEFAULT_CONFIG_YAML))
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return
    models_section = data.get("models", {}) if isinstance(data, dict) else {}
    models_dir = os.getenv("LLM_MANAGER_MODELS_DIR", DEFAULT_MODELS_DIR)
    try:
        if not models_dir or not os.path.isdir(models_dir):
            return {}
        on_disk: dict[str, str] = {}
        for entry in os.listdir(models_dir):
            full = os.path.join(models_dir, entry)
            if os.path.isdir(full):
                on_disk[entry] = entry
    except OSError:
        return
    # The ``models`` section of config.yaml is a list of entries; each entry
    # carries the config key in its ``model`` field.
    if isinstance(models_section, list):
        items = models_section
    else:
        items = list(models_section.items())
    for item in items:
        cfg_key = item.get("model", "") if isinstance(item, dict) else str(item)
        if not cfg_key:
            continue
        # Direct match: config key is already the on-disk directory name.
        if cfg_key in on_disk:
            _CONFIG_DIR_NAME[cfg_key] = on_disk[cfg_key]
        else:
            # Try exact directory name with a -GGUF suffix appended.
            candidate = cfg_key if cfg_key.endswith("-gguf") else cfg_key + "-GGUF"
            if candidate in on_disk:
                _CONFIG_DIR_NAME[cfg_key] = on_disk[candidate]
            else:
                # Fall back: match on the canonical low-level key (dots ->
                # dashes) plus a -GGUF suffix.
                core = _core_name(cfg_key)
                candidate = core if core.endswith("-gguf") else core + "-GGUF"
                if candidate in on_disk:
                    _CONFIG_DIR_NAME[cfg_key] = on_disk[candidate]
                else:
                    # Fall back: use the config key as the directory name.
                    _CONFIG_DIR_NAME[cfg_key] = cfg_key


_REGISTER_CONFIG_DIR_NAME = _register_config_dir_name()


def _json_identifier(key: str) -> str:
    """Return the model identifier portion of a JSON filename, e.g.
    ``lms-lmstudio-community-codellama-7b-instruct-gguf-codellama-7b-instruct-q4-k-m``
    -> ``codellama-7b-instruct``.
    """
    # Identifier is the part before '-gguf-'.
    id_part = key.split("-gguf-", 1)[0]
    # Strip a known site prefix if present (lmstudio-community, mradermacher, ...).
    for prefix in ("lms-lmstudio-community-", "lms-mradermacher-", "lms-"):
        if id_part.startswith(prefix):
            id_part = id_part[len(prefix) :]
            break
    return id_part


def _resolve_path_for_id(
    json_id: str,
    models_dir: str,
    dir_map: dict[str, str],
) -> str:
    """Resolve a concrete model file path from a JSON identifier.

    Tries the on-disk directory ``<json_id>-gguf`` via the directory map first,
    then falls back to a recursive scan of ``models_dir`` for a directory holding
    a Q4_K_M GGUF file whose base name matches the identifier.
    """
    dir_name = json_id.lower() + "-gguf"
    if dir_name in dir_map:
        return resolve_model_path(dir_map[dir_name], models_dir)

    for root, _dirs, files in os.walk(models_dir):
        rel = os.path.relpath(root, models_dir)
        if rel == ".":
            continue
        os.path.basename(rel)
        for name in files:
            if name.lower().endswith(".gguf"):
                base = os.path.splitext(name)[0]
                if base.rstrip("_0123456789").lower() == json_id:
                    return os.path.join(root, name)
    return ""


def _config_key_for(json_id: str) -> str | None:
    """Return the canonical config.yaml model key for a JSON identifier, if any."""
    # Direct match.
    if json_id in _CONFIG_KEY_ALIASES:
        return _CONFIG_KEY_ALIASES[json_id]
    # Try prefix match against longer aliases (longest first).
    for prefix in sorted(_CONFIG_KEY_ALIASES, key=len, reverse=True):
        if json_id.startswith(prefix + "-"):
            return _CONFIG_KEY_ALIASES[prefix]
    return None


def discover_models(
    context_dir: Path | None = None,
    config_yaml: Path | None = None,
) -> list[Model]:
    """Return a registry of all known models (excluding MMProj auxiliary files)."""
    context_dir = context_dir or DEFAULT_CONTEXT_DIR
    config_yaml = config_yaml or DEFAULT_CONFIG_YAML
    models: dict[str, Model] = {}

    # 1) Load verification metadata from JSON files.
    for json_path in sorted(context_dir.glob("*.json")):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError, OSError, UnicodeDecodeError:
            continue
        parse_verification_metadata(json_path, data, models)

    # 2) Enrich with name + path overrides from llama-swap config.yaml.
    enrich_from_config(models, config_yaml)

    # 3) Drop auxiliary MMProj files (not standalone models).
    return [m for m in models.values() if "mmproj" not in m.model_id.lower()]


def parse_verification_metadata(
    json_path: Path,
    data: dict,
    models: dict[str, Model],
) -> None:
    """Fill ``models`` with metadata from a verification JSON document.

    The JSON filename (without ``.json``) is the unique registry key, so that
    an mmproj sidecar file cannot collide with its paired model file.
    """
    model_id = data.get("model", "")
    if not model_id:
        return

    # Unique registry key from the file stem.
    key = json_path.stem

    size_gb = data.get("modelSizeGB", 0)
    size_gb = float(size_gb) if size_gb else 0.0

    declared_context = data.get("declaredContext", 0)
    declared_context = int(declared_context) if declared_context else 0

    verification = (
        data.get("verification", {})
        if isinstance(data.get("verification"), dict)
        else {}
    )
    memory_safe = verification.get("memoryLimitedContext", 0)
    memory_safe = int(memory_safe) if memory_safe else 0

    recommended = verification.get("recommendedContext", 0)
    recommended = int(recommended) if recommended else 0

    quantization = extract_quantization(model_id)
    model_readable = format_name(model_id)

    models[key] = Model(
        name=key,
        full_name=model_readable,
        size_gb=size_gb,
        context_length=declared_context,
        quantization=quantization,
        precision="gguf",
        device="auto",
        status="available",
        version="latest",
        model_id=model_id,
        hardware_constraint="",
        memory_safe_context=memory_safe,
        parameter_label=model_readable,
        extra={
            "declared_context": declared_context,
            "recommended_context": recommended,
            "status": verification.get("status", ""),
        },
    )


def _finalize_residual_paths(models: dict[str, Model], models_dir: str) -> None:
    """Final pass: fill in any paths not already set by enrichment.

    Models whose config.yaml key points at a sub-directory (e.g.
    zerank, ibm-granite, empero-ai) are resolved by scanning the full
    models directory tree for a matching GGUF file.
    """
    if not models_dir or not os.path.isdir(models_dir):
        return

    # Pre-compute json identifiers for all models to avoid re-deriving them.
    json_ids: dict[str, str] = {}
    for model_id in models:
        json_ids[model_id] = _json_identifier(model_id)

    for key, model in models.items():
        if model.path:
            continue
        # 'json_id' is the part before '-gguf-' in the JSON filename stem,
        # e.g. 'mistral-nemo-instruct-2407' from
        # 'lms-lmstudio-community-mistral-nemo-instruct-2407-gguf-mistral-nemo-ins-0972fd65'.
        json_id = json_ids[key]
        # 'json_id' is e.g. 'zerank-1-small'; strip the quant tag to get the
        # json identifier 'zerank-1-small', matching the file scan below.
        for tag in sorted(
            (
                "q5_k_m_k_v",
                "q4_k_m_k_v",
                "q5_k_m",
                "q4_k_m",
                "q4_k_s",
                "q4_k_f",
                "q3_k_m",
                "q2_k",
                "q8_0",
                "f16",
                "bf16",
                "fp8",
            ),
            key=len,
            reverse=True,
        ):
            if json_id.lower().endswith(tag):
                json_id = json_id[: -len(tag)]
                break
        matches = []
        for root, _dirs, files in os.walk(models_dir):
            for name in files:
                if not name.lower().endswith(".gguf"):
                    continue
                base = os.path.splitext(name)[0]
                # Strip the quantization suffix (e.g. '.Q8_0', '_Q8_0',
                # 'Q4_K_M') from the GGUF file base name so that
                # 'zerank-1-small.Q8_0' matches the json identifier
                # 'zerank-1-small'.  We strip whole known quant tags rather
                # than greedily consuming the tail, so that a model named
                # 'zerank-1-small' is not reduced to 'zerank'.
                core = base.lower()
                for tag in sorted(
                    (
                        "q5_k_m_k_v",
                        "q4_k_m_k_v",
                        "q5_k_m",
                        "q4_k_m",
                        "q4_k_s",
                        "q4_k_f",
                        "q3_k_m",
                        "q3_k_l",
                        "q2_k",
                        "q8_0",
                        "fp8",
                        "f16",
                        "bf16",
                    ),
                    key=len,
                    reverse=True,
                ):
                    if core.endswith(tag):
                        core = core[: -len(tag)].rstrip(".").rstrip("-")
                        break
                # Normalize dotted versions so that 'granite-4.0-h-tiny-Q4_K_M'
                # still matches the json identifier 'granite-4-0-h-tiny'.
                core = core.replace(".", "-")
                core = re.sub(r"\.", "", core)
                if core == json_id.lower():
                    matches.append(os.path.join(root, name))
        if matches:
            model.path = matches[0]


def enrich_from_config(models: dict[str, Model], config_yaml: Path) -> None:
    """Overlay model name + path overrides from the llama-swap config (if it exists)."""
    if not config_yaml.exists():
        return
    try:
        import yaml

        data = yaml.safe_load(config_yaml.read_text(encoding="utf-8")) or {}
    except Exception:
        return

    models_section = data.get("models", {}) if isinstance(data, dict) else {}
    if not models_section:
        return
    # The models section is a list of dicts (per llama-swap config.yaml).  Build
    # a lookup keyed by the model config key (the ``model`` field of each item).
    if isinstance(models_section, list):
        models_section = {
            item.get("model", ""): item
            for item in models_section
            if isinstance(item, dict)
        }
    elif isinstance(models_section, dict):
        models_section = {
            k: v for k, v in models_section.items() if isinstance(v, dict)
        }
    else:
        models_section = {}

    models_dir = os.getenv("LLM_MANAGER_MODELS_DIR", DEFAULT_MODELS_DIR)
    dir_map = model_directory_mapping(models_dir)

    for key, model in models.items():
        # Extract the model identifier from the JSON filename, e.g.
        # 'codellama-7b-instruct'.  This is the part between the site prefix
        # (e.g. 'lms-lmstudio-community-') and the '-gguf-' suffix.
        json_id = _json_identifier(key)
        # Map JSON identifier to config.yaml key (if any).
        config_key = _config_key_for(json_id)

        # Name override from config (only for models that exist in the
        # llama-swap config.yaml).
        if config_key is not None:
            model_cfg = models_section.get(config_key)
            if isinstance(model_cfg, dict) and model_cfg.get("name"):
                model.full_name = str(model_cfg["name"])

        # Path resolution: prefer an explicit `model_path` key if present in
        # the config.  Otherwise rely on on-disk directory resolution via the
        # directory mapping and a recursive fallback scan.  Models not listed
        # in config.yaml (e.g. community-submitted models) still get paths
        # from on-disk discovery.
        if not model.path:
            # Try config.yaml key first (if available).
            if config_key is not None:
                model_cfg = models_section.get(config_key)
                if isinstance(model_cfg, dict):
                    if model_cfg.get("model_path"):
                        model.path = resolve_model_path(
                            model_cfg["model_path"], models_dir
                        )
                    elif not model.path:
                        dir_name = _CONFIG_DIR_NAME.get(config_key)
                        if dir_name:
                            dir_path = model_directory_mapping().get(dir_name)
                            if dir_path and os.path.isdir(dir_path):
                                gguf_files = sorted(
                                    n
                                    for n in os.listdir(dir_path)
                                    if n.lower().endswith(".gguf")
                                )
                                if gguf_files:
                                    model.path = os.path.join(dir_path, gguf_files[0])
                            else:
                                full_dir = dir_map.get(dir_name)
                                if full_dir:
                                    model.path = resolve_model_path(
                                        full_dir, models_dir
                                    )
                        elif not model.path:
                            model.path = _resolve_path_for_id(
                                json_id, models_dir, dir_map
                            )

        # Final pass: any models still missing a path are resolved by scanning
        # the full models tree for a matching GGUF file.  This covers models
        # not listed in config.yaml (e.g. community-submitted models).  This
        # is a best-effort pass; models that cannot be resolved leave path
        # empty.
        if not model.path:
            models_root = os.getenv(
                "LLM_MANAGER_MODELS_DIR", os.path.dirname(DEFAULT_MODELS_DIR)
            )
            if not models_root or not os.path.isdir(models_root):
                models_root = os.path.dirname(DEFAULT_MODELS_DIR)
            _finalize_residual_paths({key: model}, models_root)


def format_name(model_id: str) -> str:
    """Convert a model id into readable text, e.g. 'CodeLlama 7B (Q4_K_M)'.

    The id has the shape ``lms-lmstudio-community-<model>-gguf-<display>:latest``
    where the readable name is derived from the ``<model>`` part plus the
    quantization tag found in the ``<display>`` part.
    """
    # Strip the leading site prefix.
    core = model_id
    for prefix in ("lms-lmstudio-community-", "lms-mradermacher-", "lms-"):
        if core.startswith(prefix):
            core = core[len(prefix) :]
            break

    # Separate the model identifier from its display + quantization.
    if "-gguf-" in core:
        model_part, _, display_part = core.rpartition("-gguf-")
    else:
        model_part = core
        display_part = ""

    # Build the readable model name from the identifier.
    # Model identifiers are lowercase kebab-case, e.g.:
    #   codellama-7b-instruct, deepseek-r1-0528-qwen3-8b, qwen3-vl-8b-instruct
    if model_part:
        model_tokens = model_part.split("-")
        if len(model_tokens) >= 3:
            # Family is the first token, e.g. 'codellama', 'deepseek-r1', 'qwen3'.
            family_parts = model_tokens[0]
            # CamelCase the family (e.g. 'codellama' -> 'CodeLlama',
            # 'deepseek-r1' -> 'DeepSeek R1').
            family = " ".join(p.capitalize() for p in family_parts.split("-"))
            # Size token is the second-to-last: '7b' in 'codellama-7b-instruct'.
            size_raw = model_tokens[-2]
            size = size_raw.replace("_", " ").capitalize()
            # Specialisation tokens come after the size.
            special_tokens = (
                model_tokens[-1:] if len(model_tokens) == 3 else model_tokens[-2:]
            )
            model_readable = f"{family} {size}"
            for tok in special_tokens:
                if tok.lower() in (
                    "instruct",
                    "reasoning",
                    "chat",
                    "vision",
                    "thinking",
                ):
                    pass  # already captured via capitalisation
                else:
                    model_readable += f" {tok.capitalize()}"
        elif len(model_tokens) == 2:
            family = model_tokens[0].capitalize()
            size = model_tokens[1].replace("_", " ").capitalize()
            model_readable = f"{family} {size}"
        else:
            model_readable = model_part.replace("-", " ").replace("_", " ")
    else:
        model_readable = ""

    # Extract the quantization tag from the display portion.  The display
    # portion embeds the quant as lowercase kebab-case (e.g. 'q4-k-m'), so we
    # normalise the display to underscores and match against canonical tags.
    display_clean = display_part.split(":")[0] if display_part else ""
    display_norm = display_clean.replace("-", "_").lower()
    quant = ""
    valid = sorted(VALID_QUANTIZATIONS, key=len, reverse=True)
    for valid_tag in valid:
        if valid_tag in display_norm:
            quant = valid_tag
            break

    if quant and model_readable:
        return f"{model_readable} ({quant})"
    return model_readable


def extract_quantization(model_id: str) -> str:
    """Extract a human-readable quantization tag from a model id."""
    for tag, text in (
        ("-q5_k_m_k_v", "Q5_K_M_K_V"),
        ("-q4_k_m_k_v", "Q4_K_M_K_V"),
        ("-q5_k_m", "Q5_K_M"),
        ("-q4_k_m", "Q4_K_M"),
        ("-q8_0", "Q8_0"),
        ("-fp8", "FP8"),
        ("-f16", "F16"),
        ("-bf16", "BF16"),
        ("-q3_k_m", "Q3_K_M"),
        ("-q2_k", "Q2_K"),
    ):
        if tag in model_id:
            return text
    return "Q4_K_M"


def extract_quantization_from_file(file_name: str) -> str:
    """Extract a human-readable quantization tag from a GGUF file name.

    e.g. 'CodeLlama-7B-Instruct-Q4_K_M.gguf' -> 'Q4_K_M'
    """
    lower = file_name.lower()
    for tag in sorted(
        (
            "q5_k_m_k_v",
            "q4_k_m_k_v",
            "q5_k_m",
            "q4_k_m",
            "q4_k_s",
            "q4_k_f",
            "q3_k_m",
            "q2_k",
            "q8_0",
            "fp8",
            "f16",
            "bf16",
        ),
        key=len,
        reverse=True,
    ):
        if tag in lower:
            return tag.upper().replace("-", "_")
    return "Q4_K_M"


def discover_models_on_disk(models_dir: str | None = None) -> list[Model]:
    """Discover all models on disk by scanning the models directory.

    Walks ``models_dir`` recursively for ``.gguf`` files (skipping mmproj
    auxiliary files), extracting model metadata (name, path, size from disk).
    Context and verification fields are filled in by
    :func:`enrich_with_verification`.

    The default ``models_dir`` is the parent of :data:`DEFAULT_MODELS_DIR`
    so that sub-directory models (e.g. ``ibm-granite``) are also discovered.
    """
    if models_dir is None:
        models_dir = os.path.dirname(DEFAULT_MODELS_DIR)
    models: list[Model] = []

    if not os.path.isdir(models_dir):
        return models

    for root, _dirs, files in os.walk(models_dir):
        for name in sorted(files):
            if not name.lower().endswith(".gguf"):
                continue
            # Skip mmproj auxiliary files (they are not standalone models).
            if "mmproj" in name.lower():
                continue

            model_path = os.path.join(root, name)
            size_gb = os.path.getsize(model_path) / (1024**3)

            # Model name: directory name without the -GGUF suffix; for
            # sub-directory models, prefix with the parent directory names.
            dir_name = os.path.basename(root)
            if dir_name.lower().endswith("-gguf"):
                base_name = dir_name[: -len("-gguf")]
            else:
                base_name = _strip_quant_tag_from_file(os.path.splitext(name)[0])

            rel = os.path.relpath(root, models_dir)
            if rel != "." and rel != dir_name:
                base_name = f"{rel.replace(os.sep, '/')}/{base_name}"

            models.append(
                Model(
                    name=base_name,
                    full_name=base_name,
                    size_gb=round(size_gb, 2),
                    context_length=0,
                    quantization=extract_quantization_from_file(name),
                    precision="gguf",
                    device="auto",
                    status="available",
                    version="",
                    model_id=base_name,
                    hardware_constraint="",
                    memory_safe_context=0,
                    parameter_label=base_name,
                    path=model_path,
                    extra={},
                )
            )

    return models


def _strip_quant_tag_from_file(file_name: str) -> str:
    """Strip the quantization tag from a GGUF file base name.

    e.g. 'granite-4.0-h-tiny.Q4_K_M' -> 'granite-4.0-h-tiny'.
    """
    lower = file_name.lower()
    for tag in sorted(
        (
            "q5_k_m_k_v",
            "q4_k_m_k_v",
            "q5_k_m",
            "q4_k_m",
            "q4_k_s",
            "q4_k_f",
            "q3_k_m",
            "q2_k",
            "q8_0",
            "fp8",
            "f16",
            "bf16",
        ),
        key=len,
        reverse=True,
    ):
        if lower.endswith(tag):
            return file_name[: -len(tag)]
    return file_name


def enrich_with_verification(
    models: list[Model],
    context_dir: Path | None = None,
    config_yaml: Path | None = None,
) -> None:
    """Enrich on-disk discovered models with context-verification metadata.

    Matches models to JSON verification files by normalized model name and
    merges verification metadata (context, memory-safe context, recommended
    context, status, size).  Modifies the input list in place.
    """
    context_dir = context_dir or DEFAULT_CONTEXT_DIR
    config_yaml = config_yaml or DEFAULT_CONFIG_YAML

    # Build a lookup of JSON files by normalized model name.
    json_by_name: dict[str, tuple[Path, dict]] = {}
    if context_dir.exists():
        for json_path in context_dir.glob("*.json"):
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError, OSError, UnicodeDecodeError:
                continue
            model_id = data.get("model", "")
            if not model_id:
                continue
            key = _json_identifier(json_path.stem)
            if not key:
                continue
            json_by_name[_normalize_model_name(key)] = (json_path, data)

    for model in models:
        name_key = _normalize_model_name(model.name)
        if name_key not in json_by_name:
            continue
        json_path, data = json_by_name[name_key]

        # Override size from JSON (may be more accurate than disk-derived).
        size_gb = data.get("modelSizeGB", 0)
        if size_gb:
            model.size_gb = float(size_gb)

        declared_context = data.get("declaredContext", 0)
        if declared_context:
            model.context_length = int(declared_context)

        verification = data.get("verification", {})
        if isinstance(verification, dict):
            memory_safe = verification.get("memoryLimitedContext", 0)
            if memory_safe:
                model.memory_safe_context = int(memory_safe)
            recommended = verification.get("recommendedContext", 0)
            if recommended:
                model.extra["recommended_context"] = int(recommended)
            status = verification.get("status", "")
            if status:
                model.extra["status"] = status


def _normalize_model_name(name: str) -> str:
    """Normalize a model name for matching: extract the model name (last part
    of the path), lowercase, strip -gguf suffix, and replace dots with dashes."""
    name = name.rsplit("/", 1)[-1]  # Extract the model name (last path segment)
    name = name.lower()
    name = name.replace(".", "-")
    if name.endswith("-gguf"):
        name = name[: -len("-gguf")]
    return name


def discover_models_with_verification(
    context_dir: Path | None = None,
    config_yaml: Path | None = None,
    models_dir: str | None = None,
) -> list[Model]:
    """Discover models on disk and combine with context-verification data.

    Scans the models directory for .gguf files, extracts model metadata
    (name, path, size from disk), then enriches with context-verification
    metadata from JSON files (context, memory-safe context, recommended
    context, status).  Returns a unified model registry.
    """
    models = discover_models_on_disk(models_dir)
    enrich_with_verification(models, context_dir, config_yaml)
    return models
