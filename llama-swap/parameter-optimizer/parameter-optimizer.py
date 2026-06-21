#!/usr/bin/env python3
"""
Model Parameter Optimization Script
===================================

This script helps you find optimal parameters for your llama-swap models by:
1. Running throughput benchmarks using llama-throughput-lab patterns
2. Analyzing your current llama-swap configuration
3. Recommending parameter adjustments based on model characteristics
4. Generating optimized configuration files

Usage:
    ./parameter-optimizer.py --model Meta-Llama-3.1-8B-Instruct --benchmark
    ./parameter-optimizer.py --analyze-config
    ./parameter-optimizer.py --all
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple, List

# Add llama-throughput-lab to path
SCRIPT_DIR = Path(__file__).resolve().parent
THROUGHPUT_LAB = Path(SCRIPT_DIR.parent.parent, "llama-throughput-lab")

# llama-swap config path
CONFIG_FILE = Path(SCRIPT_DIR, "config.yaml")


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


def parse_model_name(name: str) -> Tuple[int, str]:
    """Parse model name to extract size and type.

    Examples:
        "Meta-Llama-3.1-8B-Instruct" -> (8, "llama")
        "CodeLlama-7B-Instruct" -> (7, "codellama")
        "Qwen3.5-9B-GGUF" -> (9, "qwen")
    """
    name_lower = name.lower()

    # Extract size (number before B)
    size_str = ""
    for char in name_lower:
        if char.isdigit():
            size_str += char
        elif char == "-":
            break
        else:
            break

    if not size_str:
        size_str = "7"  # default

    try:
        size = int(size_str)
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

    # Base parameters
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


def analyze_current_config(config: Dict[str, Any], model_name: str) -> Dict[str, Any]:
    """Analyze current configuration and identify issues."""
    model_info = get_model_info(config, model_name)
    defaults = get_default_params(model_name)

    issues: List[str] = []
    recommendations: List[str] = []

    if model_info:
        current_macros = model_info.get("macros", {})

        # Check context size
        current_ctx = current_macros.get("ctxSize", defaults["ctxSize"])
        recommended_ctx = defaults["ctxSize"]
        if current_ctx != recommended_ctx:
            if isinstance(current_ctx, (int, float)) and isinstance(
                recommended_ctx, (int, float)
            ):
                if current_ctx > recommended_ctx * 2:
                    issues.append(
                        f"Context size ({current_ctx}) is much larger than recommended ({recommended_ctx})"
                    )
                    recommendations.append(
                        f"Reduce context size to {recommended_ctx} for better VRAM efficiency"
                    )
                elif current_ctx < recommended_ctx * 0.5:
                    issues.append(
                        f"Context size ({current_ctx}) is smaller than recommended ({recommended_ctx})"
                    )
                    recommendations.append(
                        f"Consider increasing context size to {recommended_ctx}"
                    )

        # Check temperature
        current_temp = current_macros.get("temp", defaults["temp"])
        recommended_temp = defaults["temp"]
        if isinstance(current_temp, (int, float)) and isinstance(
            recommended_temp, (int, float)
        ):
            if abs(current_temp - recommended_temp) > 0.1:
                recommendations.append(
                    f"Consider adjusting temperature from {current_temp} to {recommended_temp}"
                )

        # Check top_k/top_p
        current_top_k = current_macros.get("top_k", defaults["top_k"])
        current_top_p = current_macros.get("top_p", defaults["top_p"])

        recommended_top_k = defaults["top_k"]
        recommended_top_p = defaults["top_p"]

        if isinstance(current_top_k, (int, float)) and isinstance(
            recommended_top_k, (int, float)
        ):
            if current_top_k != recommended_top_k:
                recommendations.append(
                    f"Consider adjusting top_k to {recommended_top_k}"
                )
        elif isinstance(current_top_k, str) and isinstance(recommended_top_k, str):
            if current_top_k != recommended_top_k:
                recommendations.append(
                    f"Consider adjusting top_k to {recommended_top_k}"
                )

        if isinstance(current_top_p, (int, float)) and isinstance(
            recommended_top_p, (int, float)
        ):
            if current_top_p != recommended_top_p:
                recommendations.append(
                    f"Consider adjusting top_p to {recommended_top_p}"
                )

    return {
        "issues": issues,
        "recommendations": recommendations,
        "current": current_macros if model_info else {},
        "recommended": defaults,
    }


def run_throughput_test(
    model_name: str, prompt: str, n_predict: int, temperature: float, output_dir: Path
) -> Dict[str, Any]:
    """Run a single throughput test using llama-throughput-lab patterns."""
    results = {
        "model": model_name,
        "prompt": prompt,
        "n_predict": n_predict,
        "temperature": temperature,
        "timestamp": datetime.now().isoformat(),
        "throughput_tps": None,
        "latency_ms": None,
        "errors": None,
    }

    # Prepare environment
    env = os.environ.copy()
    env["LLAMA_MODEL_PATH"] = os.environ.get("LLAMA_MODEL_PATH", "")
    env["LLAMA_N_PREDICT"] = str(n_predict)
    env["LLAMA_TEMPERATURE"] = str(temperature)
    env["LLAMA_PROMPT"] = prompt

    # Try to find llama-server
    llama_server = os.environ.get("LLAMA_SERVER_BIN", "")
    if not llama_server:
        llama_server = "/home/waflores/DevFolder/ai/llama.cpp/build/bin/llama-server"

    # Check if llama-swap is running
    try:
        response = subprocess.run(
            ["curl", "http://127.0.0.1:10001/health"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if response.returncode == 0:
            # llama-swap is running, use it
            base_url = "http://127.0.0.1:10001"
        else:
            print("llama-swap is not running. Please start it first.")
            print(
                "Run: /home/waflores/bin/llama-swap --config llama-swap/config.yaml --listen 127.0.0.1:10001"
            )
            return results
    except Exception as e:
        print(f"Could not connect to llama-swap: {e}")
        return results

    # Run benchmark
    num_requests = 10
    try:
        start_time = time.time()

        for i in range(num_requests):
            data = json.dumps(
                {
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": n_predict,
                    "temperature": temperature,
                }
            )

            result = subprocess.run(
                [
                    "curl",
                    "-X",
                    "POST",
                    f"{base_url}/v1/chat/completions",
                    "-H",
                    "Content-Type: application/json",
                    "-d",
                    data,
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                elapsed = time.time() - start_time
                # Simple throughput calculation
                results["throughput_tps"] = (i + 1) / elapsed if elapsed > 0 else None
            else:
                results["errors"] = f"Request {i+1} failed: {result.stderr[:100]}"

        if results["throughput_tps"]:
            results["latency_ms"] = (
                1000 / results["throughput_tps"] if results["throughput_tps"] else None
            )
            results["errors"] = None

        # Save results
        results_file = output_dir / f"throughput_{model_name.replace('/', '_')}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"Throughput test complete for {model_name}")
        print(f"  Throughput: {results['throughput_tps']:.2f} tokens/s")
        print(f"  Latency: {results['latency_ms']:.2f} ms")

    except Exception as e:
        results["errors"] = str(e)
        print(f"Throughput test failed for {model_name}: {e}")

    return results


def run_config_comparison(
    config: Dict[str, Any], model_name: str, output_dir: Path
) -> Dict[str, Any]:
    """Run configuration comparison with different parameter sets."""
    analysis = analyze_current_config(config, model_name)

    if not analysis["current"]:
        print(f"No configuration found for model: {model_name}")
        return {"comparison": None}

    comparison = {
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "current_config": analysis["current"],
        "recommended_config": analysis["recommended"],
        "issues": analysis["issues"],
        "recommendations": analysis["recommendations"],
    }

    # Save comparison
    comparison_file = (
        output_dir / f"config_comparison_{model_name.replace('/', '_')}.json"
    )
    with open(comparison_file, "w") as f:
        json.dump(comparison, f, indent=2)

    print(f"Configuration comparison saved to {comparison_file}")
    print("\nIssues found:")
    for issue in analysis["issues"]:
        print(f"  - {issue}")

    print("\nRecommendations:")
    for rec in analysis["recommendations"]:
        print(f"  - {rec}")

    return {"comparison": comparison}


def run_full_benchmark(
    config: Dict[str, Any], model_name: str, output_dir: Path
) -> Dict[str, Any]:
    """Run a full benchmark suite for a model."""
    print(f"\n{'='*60}")
    print(f"Running full benchmark for: {model_name}")
    print(f"{'='*60}\n")

    # Run configuration analysis
    analysis = run_config_comparison(config, model_name, output_dir)

    if not analysis["comparison"]:
        return {"benchmark": None}

    # Run throughput tests with different parameters
    test_configs = [
        {"temp": 0.5, "n_predict": 256},
        {"temp": 0.7, "n_predict": 256},
        {"temp": 0.7, "n_predict": 512},
        {"temp": 0.9, "n_predict": 256},
    ]

    all_results = []
    for test in test_configs:
        print(f"\nRunning test: temp={test['temp']}, n_predict={test['n_predict']}")
        result = run_throughput_test(
            model_name,
            "Write a short paragraph about why concurrency helps throughput.",
            test["n_predict"],
            test["temp"],
            output_dir,
        )
        all_results.append(result)

    return {
        "benchmark": {
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "config_analysis": analysis["comparison"],
            "throughput_tests": all_results,
        }
    }


def generate_optimized_config(
    config: Dict[str, Any], model_name: str, benchmark_results: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate optimized configuration based on benchmark results."""
    analysis = run_config_comparison(config, model_name, Path("/tmp"))

    # Start with recommended config
    optimized = analysis["recommended"].copy()

    # Apply benchmark results if available
    if benchmark_results and benchmark_results.get("benchmark"):
        throughput_tests = benchmark_results["benchmark"].get("throughput_tests", [])

        if throughput_tests:
            # Find best performing configuration
            best_test = max(throughput_tests, key=lambda x: x.get("throughput_tps", 0))

            if best_test.get("throughput_tps"):
                optimized["temp"] = best_test["temperature"]
                optimized["n_predict"] = best_test["n_predict"]

    return optimized


def main():
    parser = argparse.ArgumentParser(
        description="Model Parameter Optimization for llama-swap"
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Model name (e.g., Meta-Llama-3.1-8B-Instruct)",
    )
    parser.add_argument(
        "--config", type=str, default=CONFIG_FILE, help="Path to llama-swap config file"
    )
    parser.add_argument(
        "--benchmark", action="store_true", help="Run throughput benchmarks"
    )
    parser.add_argument(
        "--analyze", action="store_true", help="Analyze current configuration"
    )
    parser.add_argument(
        "--optimize", action="store_true", help="Generate optimized configuration"
    )
    parser.add_argument(
        "--all", action="store_true", help="Run all analyses and benchmarks"
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

    # Check if model exists in config
    if args.model not in config.get("models", {}):
        print(f"Error: Model '{args.model}' not found in configuration.")
        print(f"Available models: {', '.join(config.get('models', {}).keys())}")
        sys.exit(1)

    print(f"Model: {args.model}")
    print(f"Config: {args.config}")
    print(f"Output: {args.output_dir}")

    if args.all:
        # Run all analyses
        run_config_comparison(config, args.model, output_dir)
        benchmark = run_full_benchmark(config, args.model, output_dir)
        optimized = generate_optimized_config(config, args.model, benchmark)

        # Save optimized config
        optimized_file = output_dir / f"optimized_{args.model.replace('/', '_')}.json"
        with open(optimized_file, "w") as f:
            json.dump(optimized, f, indent=2)

        print(f"\nOptimized configuration saved to {optimized_file}")
        print("\nOptimized parameters:")
        for key, value in optimized.items():
            print(f"  {key}: {value}")

    elif args.benchmark:
        benchmark = run_full_benchmark(config, args.model, output_dir)

    elif args.analyze:
        run_config_comparison(config, args.model, output_dir)

    else:
        print(
            "Please specify at least one of --benchmark, --analyze, --optimize, or --all"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
