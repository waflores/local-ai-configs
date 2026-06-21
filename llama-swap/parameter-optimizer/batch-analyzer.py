#!/usr/bin/env python3
"""
Batch Model Parameter Analyzer
==============================

This script analyzes all models in your llama-swap configuration and generates
parameter recommendations based on model characteristics and llama-throughput-lab
best practices.

Usage:
    ./batch-analyzer.py --config llama-swap/config.yaml
    ./batch-analyzer.py --analyze-all --output-dir logs/parameter-analysis
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, TypedDict

# Add llama-throughput-lab to path
SCRIPT_DIR = Path(__file__).resolve().parent
THROUGHPUT_LAB = Path(SCRIPT_DIR.parent.parent, "llama-throughput-lab")

# llama-swap config path
CONFIG_FILE = Path(SCRIPT_DIR.parent, "config.yaml")


def load_llama_swap_config() -> Dict[str, Any]:
    """Load the llama-swap configuration file."""
    import yaml

    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)


def get_model_info(config: Dict[str, Any], model_name: str) -> Dict[str, Any]:
    """Extract model-specific configuration."""
    if model_name in config.get("models", {}):
        return config["models"][model_name]
    return {}


def parse_model_name(name: str) -> tuple[int, str]:
    """Parse model name to extract size and type."""
    name_lower = name.lower()

    # Extract size (number before B)
    size_str = ""
    for char in name_lower:
        if char.isdigit():
            size_str += char
        elif char == "-":
            break

    try:
        size = int(size_str) if size_str else 7
    except ValueError:
        size = 7

    # Extract model type
    model_type = "llama"
    if "codellama" in name_lower:
        model_type = "codellama"
    elif "qwen" in name_lower:
        model_type = "qwen"
    elif "mistral" in name_lower:
        model_type = "mistral"
    elif "phi" in name_lower:
        model_type = "phi"
    elif "gemma" in name_lower:
        model_type = "gemma"
    elif "nemotron" in name_lower:
        model_type = "nemotron"
    elif "olmocr" in name_lower:
        model_type = "olmocr"
    elif "devstral" in name_lower:
        model_type = "devstral"
    elif "granite" in name_lower:
        model_type = "granite"
    elif "zerank" in name_lower:
        model_type = "zerank"
    elif "rnj" in name_lower:
        model_type = "rnj"
    elif "minstral" in name_lower:
        model_type = "minstral"

    return (size, model_type)


def get_default_params(model_name: str) -> Dict[str, Any]:
    """Get default parameters based on model type and size."""
    size, model_type = parse_model_name(model_name)

    defaults: Dict[str, Any] = {
        "temp": 0.7,
        "top_k": 40,
        "top_p": 0.9,
        "ctxSize": 16384,
        "n_predict": 512,
        "nGpuLayers": "all",
        "threads": "-1",
        "flashAttn": "auto",
        "jinja": True,
        "tools": "all",
    }

    # Adjust for model type
    if model_type == "llama":
        if size <= 8:
            defaults["ctxSize"] = 16384
            defaults["temp"] = 0.7
        elif size <= 14:
            defaults["ctxSize"] = 32768
            defaults["temp"] = 0.7
        elif size <= 30:
            defaults["ctxSize"] = 65536
            defaults["temp"] = 0.6
        else:
            defaults["ctxSize"] = 131072
            defaults["temp"] = 0.6

    elif model_type == "codellama":
        defaults["ctxSize"] = 16384
        defaults["temp"] = 0.8
        defaults["top_k"] = 40

    elif model_type == "qwen":
        if size <= 4:
            defaults["ctxSize"] = 123333
            defaults["temp"] = 0.7
        elif size <= 9:
            defaults["ctxSize"] = 262144
            defaults["temp"] = 0.6
            defaults["min_p"] = 0
            defaults["top_k"] = 20
            defaults["top_p"] = 0.95
        elif size <= 27:
            defaults["ctxSize"] = 1024
            defaults["temp"] = 0.7

    elif model_type == "mistral":
        if size <= 3:
            defaults["ctxSize"] = 133333
            defaults["temp"] = 0.7
        elif size <= 12:
            defaults["ctxSize"] = 1024
            defaults["temp"] = 0.7

    elif model_type == "phi":
        if size <= 4:
            defaults["ctxSize"] = 123333
            defaults["temp"] = 0.7
        else:
            defaults["ctxSize"] = 1024
            defaults["temp"] = 0.7

    elif model_type == "nemotron":
        defaults["ctxSize"] = 113333
        defaults["reasoning"] = "auto"
        defaults["reasoningFormat"] = "deepseek"
        defaults["reasoningBudget"] = "-1"
        defaults["cacheRamSpillover"] = "4096"

    elif model_type == "olmocr":
        defaults["ctxSize"] = 32727
        defaults["temp"] = 0.7

    elif model_type == "devstral":
        defaults["ctxSize"] = 1024
        defaults["temp"] = 0.7

    elif model_type == "gemma":
        defaults["ctxSize"] = 18000
        defaults["temp"] = 0.7

    elif model_type == "zerank":
        defaults["ctxSize"] = "-1"
        defaults["device"] = "Vulkan0"
        defaults["reasoningBudget"] = 0
        defaults["reasoning"] = "off"
        defaults["gpuLayers"] = "-2"

    return defaults


def analyze_all_models(
    config: Dict[str, Any], output_dir: Path
) -> List[Dict[str, Any]]:
    """Analyze all models in the configuration."""
    results: List[Dict[str, Any]] = []

    for model_name in config.get("models", {}).keys():
        model_info = get_model_info(config, model_name)
        defaults = get_default_params(model_name)

        analysis: Dict[str, Any] = {
            "model": model_name,
            "name": model_info.get("name", ""),
            "current_macros": model_info.get("macros", {}),
            "recommended": defaults,
            "issues": [],
            "recommendations": [],
        }

        # Check context size
        current_ctx = model_info.get("macros", {}).get("ctxSize", defaults["ctxSize"])
        recommended_ctx = defaults["ctxSize"]
        if current_ctx != recommended_ctx:
            if isinstance(current_ctx, str) and current_ctx.isdigit():
                current_ctx_int = int(current_ctx)
                if recommended_ctx > 0 and current_ctx_int > recommended_ctx * 2:
                    analysis["issues"].append(
                        f"Context size ({current_ctx_int}) is much larger than recommended ({recommended_ctx})"
                    )
                    analysis["recommendations"].append(
                        f"Reduce context size to {recommended_ctx} for better VRAM efficiency"
                    )
                elif recommended_ctx > 0 and current_ctx_int < recommended_ctx * 0.5:
                    analysis["issues"].append(
                        f"Context size ({current_ctx_int}) is smaller than recommended ({recommended_ctx})"
                    )
                    analysis["recommendations"].append(
                        f"Consider increasing context size to {recommended_ctx}"
                    )
            else:
                analysis["recommendations"].append(
                    f"Context size differs from recommendation: current={current_ctx}, recommended={recommended_ctx}"
                )

        # Check temperature
        current_temp = model_info.get("macros", {}).get("temp", defaults["temp"])
        recommended_temp = defaults["temp"]
        if isinstance(current_temp, (int, float)) and isinstance(
            recommended_temp, (int, float)
        ):
            if abs(current_temp - recommended_temp) > 0.1:
                analysis["recommendations"].append(
                    f"Consider adjusting temperature from {current_temp} to {recommended_temp}"
                )

        # Check top_k/top_p
        current_top_k = model_info.get("macros", {}).get("top_k", defaults["top_k"])
        current_top_p = model_info.get("macros", {}).get("top_p", defaults["top_p"])

        recommended_top_k = defaults["top_k"]
        recommended_top_p = defaults["top_p"]

        if isinstance(current_top_k, (int, float)) and isinstance(
            recommended_top_k, (int, float)
        ):
            if current_top_k != recommended_top_k:
                analysis["recommendations"].append(
                    f"Consider adjusting top_k to {recommended_top_k}"
                )
        elif isinstance(current_top_k, str) and isinstance(recommended_top_k, str):
            if current_top_k != recommended_top_k:
                analysis["recommendations"].append(
                    f"Consider adjusting top_k to {recommended_top_k}"
                )

        if isinstance(current_top_p, (int, float)) and isinstance(
            recommended_top_p, (int, float)
        ):
            if current_top_p != recommended_top_p:
                analysis["recommendations"].append(
                    f"Consider adjusting top_p to {recommended_top_p}"
                )

        # Add model-specific notes
        model_notes = get_model_notes(model_name)
        if model_notes:
            analysis["notes"] = model_notes

        results.append(analysis)

    return results


def get_model_notes(model_name: str) -> List[str]:
    """Get model-specific notes and recommendations."""
    name_lower = model_name.lower()
    notes: List[str] = []

    # Size-based notes
    size_str = ""
    for char in name_lower:
        if char.isdigit():
            size_str += char
        elif char == "-":
            break

    try:
        size = int(size_str) if size_str else 7
    except ValueError:
        size = 7

    if size <= 4:
        notes.append("Small model - good for quick responses and low-latency tasks")
    elif size <= 8:
        notes.append("Medium-small model - balanced for general-purpose tasks")
    elif size <= 14:
        notes.append("Medium-large model - good for complex reasoning tasks")
    elif size <= 24:
        notes.append("Large model - suitable for advanced reasoning and long contexts")
    else:
        notes.append(
            "Very large model - best for specialized tasks with sufficient resources"
        )

    # Model-specific notes
    if "codellama" in name_lower:
        notes.append(
            "Code-focused model - may benefit from higher temperature for creative coding"
        )
    elif "qwen" in name_lower:
        notes.append("Qwen model - consider using min_p for better sampling")
    elif "mistral" in name_lower:
        notes.append("Mistral model - good balance of speed and quality")
    elif "phi" in name_lower:
        notes.append("Phi model - Microsoft's small but capable models")
    elif "nemotron" in name_lower:
        notes.append("Nemotron model - optimized for reasoning tasks")
    elif "olmocr" in name_lower:
        notes.append("OCR model - specialized for optical character recognition")
    elif "devstral" in name_lower:
        notes.append("Devstral model - optimized for development tasks")
    elif "gemma" in name_lower:
        notes.append("Gemma model - Google's open models")
    elif "zerank" in name_lower:
        notes.append("Zerank model - specialized reranking model")
    elif "minstral" in name_lower:
        notes.append("Minstral model - Microsoft's efficient models")

    return notes


class OptimizedConfig(TypedDict, total=False):
    globalTTL: int
    groups: dict[str, Any]
    healthCheckTimeout: int
    logLevel: str
    logToStdout: str
    macros: dict[str, Any]
    performance: dict[str, Any]
    sendLoadingState: bool
    startPort: int
    models: dict[str, Any]


def generate_optimized_config(config: Dict[str, Any], output_dir: Path) -> Path:
    """Generate optimized configuration file."""
    analyses = analyze_all_models(config, output_dir)

    cmd_prefix: str = "/home/waflores/DevFolder/ai/llama.cpp/build/bin/llama-server"
    models_directory: str = "/home/waflores/.lmstudio/models/lmstudio-community"

    optimized_config: OptimizedConfig = {
        "globalTTL": 0,
        "groups": {
            "swappable": {
                "exclusive": True,
                "members": config.get("groups", {})
                .get("swappable", {})
                .get("members", []),
                "swap": True,
            }
        },
        "healthCheckTimeout": 60,
        "logLevel": "debug",
        "logToStdout": "proxy",
        "macros": {
            "cacheRamSpillover": "4096",
            "cmdPrefix": cmd_prefix,
            "contextShift": "false",
            "ctxSize": "131072",
            "device": "CUDA0",
            "flashAttn": "auto",
            "jinja": "true",
            "models_directory": models_directory,
            "nGpuLayers": "all",
            "nPredict": "-1",
            "reasoning": "auto",
            "reasoningBudget": "-1",
            "reasoningFormat": "deepseek",
            "threads": "-1",
            "tools": "all",
        },
        "performance": {
            "disabled": False,
            "every": 15,
        },
        "sendLoadingState": True,
        "startPort": 10001,
        "models": {},
    }

    for analysis in analyses:
        model_name = analysis["model"]
        optimized_macros = analysis["recommended"].copy()

        # Add model info
        optimized_config["models"][model_name] = {
            "cmd": f"${{{{{cmd_prefix}}}}} --port ${{{{PORT}}}} --models-dir ${{{{models_directory}}}} --model ${{{{models_directory}}}}/{model_name}/optimized-model.Q4_K_M.gguf --n-gpu-layers ${{{{nGpuLayers}}}} --threads ${{{{threads}}}} --flash-attn ${{{{flashAttn}}}} --jinja --tools ${{{{tools}}}} --device ${{{{device}}}} --ctx-size ${{{{ctxSize}}}} --n-predict ${{{{nPredict}}}} --temp ${{{{temp}}}} --top-k ${{{{top_k}}}} --top-p ${{{{top_p}}}}",
            "env": [
                "GGML_CUDA_ENABLE_UNIFIED_MEMORY=1",
                "LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu",
            ],
            "macros": optimized_macros,
            "name": analysis.get("name", ""),
            "ttl": 600,
            "notes": analysis.get("notes", []),
            "issues": analysis.get("issues", []),
        }

    # Save optimized config
    output_file = output_dir / "optimized-config.yaml"
    with open(output_file, "w") as f:
        import yaml

        yaml.dump(optimized_config, f, default_flow_style=False, sort_keys=False)

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Batch Model Parameter Analyzer for llama-swap"
    )
    parser.add_argument(
        "--config", type=str, default=CONFIG_FILE, help="Path to llama-swap config file"
    )
    parser.add_argument(
        "--analyze-all", action="store_true", help="Analyze all models in configuration"
    )
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Generate optimized configuration file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="/home/waflores/DevFolder/ai/local-config/logs/parameter-analysis",
        help="Output directory for results",
    )

    args = parser.parse_args()

    # Load configuration
    config = load_llama_swap_config()

    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Analyzing models from: {args.config}")
    print(f"Output directory: {args.output_dir}")
    print()

    if args.analyze_all:
        analyses = analyze_all_models(config, output_dir)

        # Save individual analysis for each model
        for analysis in analyses:
            analysis_file = (
                output_dir / f"{analysis['model'].replace('/', '_')}_analysis.json"
            )
            with open(analysis_file, "w") as f:
                json.dump(analysis, f, indent=2)

        print(f"\n{'='*60}")
        print(f"Analysis complete for {len(analyses)} models")
        print(f"{'='*60}\n")

        # Print summary
        print("Model Analysis Summary:")
        print("-" * 60)
        for analysis in analyses:
            model = analysis["model"]
            name = analysis.get("name", "")
            issues = len(analysis.get("issues", []))
            recommendations = len(analysis.get("recommendations", []))
            notes = analysis.get("notes", [])

            print(f"\n{model}")
            print(f"  Name: {name}")
            print(f"  Issues: {issues}")
            print(f"  Recommendations: {recommendations}")
            if notes:
                print("  Notes:")
                for note in notes[:3]:  # Show first 3 notes
                    print(f"    - {note}")

        print(f"\n{'='*60}")
        print(f"Results saved to: {output_dir}")
        print(f"{'='*60}")

    elif args.generate_config:
        output_file = generate_optimized_config(config, output_dir)
        print(f"\nOptimized configuration saved to: {output_file}")

    else:
        print("Please specify at least one of --analyze-all or --generate-config")


if __name__ == "__main__":
    main()
