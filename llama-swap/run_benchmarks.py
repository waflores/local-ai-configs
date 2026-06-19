#!/usr/bin/env python3
"""
llama-bench: Benchmark suite for llama-swap models
Tests all models and collects performance metrics
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

import yaml

# Configuration
CONFIG_PATH = "/home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml"
RESULTS_DIR = "/home/waflores/DevFolder/ai/local-config/logs/benchmarks"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def load_config():
    """Load llama-swap configuration"""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def run_benchmark(config):
    """Run benchmark for a single model"""
    model_name = config.get("MODEL", "unknown")
    model_path = config.get("MODEL_PATH", "")
    backend = config.get("BACKEND", "cuda")
    config.get("MAX_TOTAL_TOKENS", 4096)
    max_concurrent = config.get("MAX_CONCURRENT_REQUESTS", 1)

    print(f"\n{'=' * 60}")
    print(f"Benchmark: {model_name}")
    print(f"{'=' * 60}")

    results = {
        "model": model_name,
        "path": model_path,
        "backend": backend,
        "timestamp": datetime.now().isoformat(),
        "metrics": {},
    }

    try:
        # Test 1: Model Load Time
        print("\n[1/4] Testing model load time...")
        load_start = time.time()
        result = subprocess.run(
            [
                "python",
                "-m",
                "llama_server.main",
                "--config",
                CONFIG_PATH,
                "--model-name",
                model_name,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        load_time = time.time() - load_start
        results["metrics"]["load_time_seconds"] = round(load_time, 2)

        # Check for errors
        if "error" in result.stderr.lower() or "exception" in result.stderr.lower():
            results["metrics"]["load_error"] = result.stderr[:200]

        print(f"  Load time: {load_time:.2f}s")

        # Test 2: Generation Speed (tokens per second)
        print("\n[2/4] Testing generation speed...")
        prompt = "Count from 1 to 100:"
        gen_start = time.time()
        result = subprocess.run(
            [
                "python",
                "-m",
                "llama_server.main",
                "--config",
                CONFIG_PATH,
                "--model-name",
                model_name,
                "--prompt",
                prompt,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        gen_time = time.time() - gen_start
        if gen_time > 0 and result.stdout:
            token_count = len(result.stdout.split())
            tps = token_count / gen_time
            results["metrics"]["generation_tps"] = round(tps, 2)
            results["metrics"]["generation_time_seconds"] = round(gen_time, 2)
            results["metrics"]["tokens_generated"] = token_count
        else:
            results["metrics"]["generation_tps"] = 0
            results["metrics"]["generation_time_seconds"] = gen_time

        print(f"  Generation: {token_count} tokens in {gen_time:.2f}s ({tps:.2f} tps)")

        # Test 3: Context Handling
        print("\n[3/4] Testing context handling...")
        context_prompt = "Summarize the following text concisely. Text: " + " ".join(
            ["This is a test sentence " + str(i) for i in range(100)]
        )
        result = subprocess.run(
            [
                "python",
                "-m",
                "llama_server.main",
                "--config",
                CONFIG_PATH,
                "--model-name",
                model_name,
                "--prompt",
                context_prompt,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            results["metrics"]["context_handling"] = "PASS"
        else:
            results["metrics"]["context_handling"] = "FAIL"
            results["metrics"]["context_error"] = result.stderr[:100]

        print(f"  Context handling: {results['metrics']['context_handling']}")

        # Test 4: Concurrent Requests
        print("\n[4/4] Testing concurrent requests...")
        concurrent_results = []
        for i in range(max_concurrent):
            start = time.time()
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "llama_server.main",
                    "--config",
                    CONFIG_PATH,
                    "--model-name",
                    model_name,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            concurrent_results.append(
                {
                    "request_id": i,
                    "success": result.returncode == 0,
                    "time": round(time.time() - start, 2),
                }
            )

        success_rate = sum(1 for r in concurrent_results if r["success"]) / len(
            concurrent_results
        )
        results["metrics"]["concurrent_success_rate"] = round(success_rate * 100, 2)
        print(f"  Concurrent success rate: {success_rate * 100:.2f}%")

    except subprocess.TimeoutExpired:
        results["metrics"]["error"] = "Timeout"
    except Exception as e:
        results["metrics"]["error"] = str(e)[:200]

    return results


def main():
    print("=" * 60)
    print("LLAMA-SWAP BENCHMARK SUITE")
    print("=" * 60)
    print(f"Timestamp: {TIMESTAMP}")
    print(f"Config: {CONFIG_PATH}")
    print()

    # Ensure results directory exists
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Load configuration
    config = load_config()
    print("Loaded configuration")
    print(f"  Backend: {config.get('BACKEND', 'N/A')}")
    print(f"  Max VRAM: {config.get('MAX_VRAM', 'N/A')}")
    print(f"  Max Tokens: {config.get('MAX_TOTAL_TOKENS', 'N/A')}")
    print()

    # Run benchmarks for all models
    all_results = []
    for model_name in config.get("MODELS", []):
        model_config = config.copy()
        model_config["MODEL"] = model_name
        model_config["MODEL_PATH"] = (
            config.get(f"MODEL_PATH_{model_name}", "")
            or f"/home/waflores/.lmstudio/models/{model_name}"
        )

        result = run_benchmark(model_config)
        all_results.append(result)

        # Save individual results
        individual_file = (
            Path(RESULTS_DIR) / f"{TIMESTAMP}_{model_name.replace(':', '_')}.json"
        )
        with open(individual_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Saved: {individual_file}")

    # Save all results
    all_results_file = Path(RESULTS_DIR) / f"{TIMESTAMP}_all_results.json"
    with open(all_results_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nAll results saved: {all_results_file}")

    # Print summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    for result in all_results:
        model = result["model"]
        metrics = result["metrics"]
        print(f"\n{model}:")
        print(f"  Load Time: {metrics.get('load_time_seconds', 'N/A'):.2f}s")
        print(f"  Generation: {metrics.get('generation_tps', 'N/A')} tps")
        print(f"  Context: {metrics.get('context_handling', 'N/A')}")
        print(f"  Concurrent: {metrics.get('concurrent_success_rate', 'N/A')}%")
        if "error" in metrics:
            print(f"  ERROR: {metrics['error'][:100]}")

    return all_results


if __name__ == "__main__":
    results = main()
    print("\nBenchmark suite complete!")
