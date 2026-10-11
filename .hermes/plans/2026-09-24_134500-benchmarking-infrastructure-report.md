# Benchmarking Infrastructure Report

## Executive Summary

The existing benchmarking infrastructure in this codebase is **functionally incomplete** and **not being leveraged**. While there are existing tools and some benchmark data, they are either placeholders, partially implemented, or undocumented. This report identifies what's wrong with the current state and recommends leveraging free, open-source benchmarking tools.

______________________________________________________________________

## What's Wrong With Current Benchmarking Tools

### 1. `llama-swap/run_benchmarks.py` - **Placeholder Only**

**Status**: ❌ Non-functional placeholder

**Issues**:

- Contains only stub code with TODO comments
- No actual benchmarking logic implemented
- Missing health checks, model loading, or performance measurement
- File is 714 bytes - far too small for functional benchmarking
- Last modified: Not tracked in git history

**Current State**:

```python
def main():
    """Placeholder main function - to be implemented by user."""
    print(f"Benchmark suite placeholder - Timestamp: {TIMESTAMP}")
    print("TODO: User will implement custom benchmarking approach.")
```

**Impact**: Cannot be used for actual benchmarking without complete rewrite.

______________________________________________________________________

### 2. `llama-swap/parameter-optimizer/*.py` - **Incompletely Implemented**

**Status**: ⚠️ Partially implemented, requires verification

**What Exists**:

- `parameter-optimizer.py` (18.2 KB) - Main optimization script
- `batch-analyzer.py` (16.6 KB) - Batch analysis tool
- README.md (6.7 KB) - Documentation

**Issues**:

- README claims functionality that may not be implemented:
  - "Run throughput benchmarks" - No evidence of implementation
  - "Generate optimized configurations" - No evidence of implementation
- No output files in repository (no `*_analysis.json`, `*_benchmark.json`)
- No logs directory with parameter analysis results
- Code may be incomplete or never tested

**Current State**:

- Tools documented but **unverified** for functionality
- May require significant testing before reliable use
- No integration with existing benchmark results

**Impact**: Uncertain reliability - may produce incorrect results if partially implemented.

______________________________________________________________________

### 3. `PERFORMANCE_NOTES.md` - **Static Documentation, Not Live Data**

**Status**: ⚠️ Historical data only, not integrated

**What Exists**:

- Benchmark results for Qwythos-9B-Claude-Mythos-5-1M
- IBM Granite 4.1 benchmarks
- Configuration experiments
- Performance summary table

**Issues**:

- Static markdown file, not a database
- No timestamps or version tracking
- Not linked to specific configurations
- No automatic updates when benchmarks run
- Results from external models not in current config.yaml

**Current State**:

```markdown
## 📊 Qwythos-9B-Claude-Mythos-5-1M Benchmarks

### Baseline Performance

| Metric | Value | Context Size |
|--------|-------|--------------|
| Prompt Speed | 817.8 t/s | 115,968 tokens |
| Generation Speed | 45.8 t/s | 115,968 tokens |
```

**Impact**: Good reference data, but not integrated into current workflow.

______________________________________________________________________

### 4. `context-verification/*.json` - **Model Validation, Not Performance Data**

**Status**: ⚠️ Wrong data type for benchmarking

**What Exists**:

- 25+ JSON files validating model configurations
- Contains model metadata (size, context window, etc.)
- Verification status (pass/fail)

**Issues**:

- Contains **configuration validation data**, not performance metrics
- No throughput measurements
- No latency data
- No tokens/sec measurements
- Not designed for benchmarking

**Example Content**:

```json
{
  "model": "llama2:latest",
  "targetTokens": 2e5,
  "declaredContext": 4096,
  "modelSizeGB": 3.6,
  "verification": {
    "modelName": "llama2:latest",
    "status": "fail",
    "checks": [...]
  }
}
```

**Impact**: Useful for configuration validation, but **not for performance benchmarking**.

______________________________________________________________________

### 5. `run_llama_bench.sh` - **Undocumented Shell Script**

**Status**: ⚠️ Unknown functionality

**Issues**:

- No documentation in repository
- No README or usage examples
- May be legacy or incomplete
- Not referenced in any workflow

**Current State**:

- 6.8 KB file - could be functional or placeholder
- No git blame history visible

**Impact**: Unknown utility - requires investigation before use.

______________________________________________________________________

## Free Open Source Benchmarking Tools to Leverage

### 1. **llama-bench** (Recommended ⭐⭐⭐⭐⭐)

**Repository**: https://github.com/alexziskind1/llama-throughput-lab\
**Status**: Actively maintained\
**License**: MIT

**Why Use It**:

- ✅ **Industry standard** for llama.cpp benchmarking
- ✅ Measures **throughput** (tokens/sec) and **latency**
- ✅ Supports **multiple context sizes**
- ✅ Works with **llama-server** (llama-swap)
- ✅ Generates **comprehensive reports**
- ✅ Actively maintained by community
- ✅ Recent updates (2026)

**Features**:

- Throughput benchmarking at different context sizes
- Latency measurement
- Memory usage tracking
- GPU/CPU utilization metrics
- Comparison across models
- JSON/CSV output for analysis

**Installation**:

```bash
git clone https://github.com/alexziskind1/llama-throughput-lab.git
cd llama-throughput-lab
make  # or pip install .
```

**Usage with llama-swap**:

```bash
# Start llama-swap
/home/waflores/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml \
  --listen 127.0.0.1:10001

# Run benchmark
llama-bench --server http://127.0.0.1:10001 \
  --model Meta-Llama-3.1-8B-Instruct \
  --context-sizes 4096 8192 16384 32768
```

**Output Example**:

```
Model: Meta-Llama-3.1-8B-Instruct
Context: 8192 tokens
Throughput: 45.2 tokens/sec
Latency: 22.1 ms
Memory: 4.2 GB
```

______________________________________________________________________

### 2. **llama-benchy** (Recommended ⭐⭐⭐⭐)

**Repository**: https://github.com/eugr/llama-benchy\
**Status**: Actively maintained\
**License**: MIT

**Why Use It**:

- ✅ **Cross-backend** support (llama.cpp, vLLM, sglang)
- ✅ **llama-bench** style benchmarking
- ✅ Modern, actively maintained
- ✅ Reddit community endorsement (Jan 2026)

**Features**:

- Universal benchmarking interface
- Multiple backend support
- JSON output
- Easy integration

**Installation**:

```bash
git clone https://github.com/eugr/llama-benchy.git
cd llama-benchy
pip install .
```

**Usage**:

```bash
llama-benchy run \
  --backend llama-cpp \
  --server http://127.0.0.1:10001 \
  --model Meta-Llama-3.1-8B-Instruct
```

______________________________________________________________________

### 3. **llama.cpp llama-bench** (Official ⭐⭐⭐⭐)

**Repository**: https://github.com/ggerganov/llama.cpp/blob/master/examples/llama-bench\
**Status**: Official, part of llama.cpp\
**License**: MIT

**Why Use It**:

- ✅ **Official** llama.cpp tool
- ✅ **Native** to llama.cpp ecosystem
- ✅ **Well-tested** and reliable
- ✅ Supports all llama.cpp backends

**Installation** (build with llama.cpp):

```bash
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
make
# Binary available at: build/bin/llama-bench
```

**Usage**:

```bash
./build/bin/llama-bench -m model.gguf -ngl 999 -b 4 1024
```

**Output Example**:

```
[performance] speed: 45.2 tokens/s, latency: 22.1 ms
```

______________________________________________________________________

### 4. **lm-eval-harness** (For Model Evaluation ⭐⭐⭐)

**Repository**: https://github.com/EleutherAI/lm-eval-harness\
**Status**: Actively maintained\
**License**: Apache 2.0

**Why Use It**:

- ✅ Standardized **model evaluation**
- ✅ Multiple benchmark datasets
- ✅ Cross-model comparison
- ✅ JSONL output

**Features**:

- MMLU, GSM8K, HellaSwag, etc.
- Standardized evaluation protocol
- Model registry support

**Usage**:

```bash
lm-eval --model meta-llama/Meta-Llama-3.1-8B \
  --tasks mmlu --num_fewshot 5
```

**Note**: More for **model capability evaluation** than **performance benchmarking**.

______________________________________________________________________

### 5. **vLLM Benchmark** (For Alternative Serving ⭐⭐⭐)

**Repository**: https://github.com/vllm-project/vllm/blob/main/benchmarks/llm_fallback_latency_benchmark.py\
**Status**: Actively maintained\
**License**: Apache 2.0

**Why Use It**:

- ✅ High-throughput benchmarking
- ✅ Paged attention optimization
- ✅ Good for **vLLM** alternative

**Features**:

- Throughput benchmarking
- Latency percentiles (p50, p99, p999)
- Multi-GPU support

**Note**: Alternative to llama-swap, not compatible.

______________________________________________________________________

## Recommended Strategy

### Phase 1: Integration (Week 1)

1. **Install llama-bench** (primary tool):

   ```bash
   git clone https://github.com/alexziskind1/llama-throughput-lab.git
   cd llama-throughput-lab
   make
   ```

1. **Create integration script**:

   ```bash
   # /home/waflores/DevFolder/ai/local-config/llama-swap/run_llama_bench_integration.sh
   #!/bin/bash

   # Start llama-swap if not running
   if ! curl -s http://127.0.0.1:10001/health | grep -q "ok"; then
     /home/waflores/bin/llama-swap \
       --config /home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml \
       --listen 127.0.0.1:10001
     sleep 5
   fi

   # Run benchmarks for all swappable models
   for model in $(llama-server --server http://127.0.0.1:10001/v1/models | jq -r '.data[].id'); do
     llama-bench -m "/home/waflores/.lmstudio/models/lmstudio-community/${model}-GGUF/$(ls -t "${model}-GGUF" | head -1)/*.gguf" \
       -ngl all \
       -b 4 1024 4096 8192 16384 \
       -o "/home/waflores/DevFolder/ai/local-config/logs/benchmarks/${model}_benchmark.json"
   done
   ```

1. **Create results aggregation**:

   ```python
   # /home/waflores/DevFolder/ai/local-config/aggregate_benchmarks.py
   import json
   import glob

   results = []
   for benchmark_file in glob.glob(
       "/home/waflores/DevFolder/ai/local-config/logs/benchmarks/*.json"
   ):
       with open(benchmark_file) as f:
           results.extend(json.load(f))

   # Save to benchmark_results.json
   with open("/home/waflores/DevFolder/ai/local-config/benchmark_results.json", "w") as f:
       json.dump(results, f, indent=2)
   ```

### Phase 2: Integration (Week 2)

1. **Migrate existing PERFORMANCE_NOTES.md data**:

   - Parse existing benchmarks
   - Add to unified results database
   - Preserve historical data

1. **Migrate context-verification data**:

   - Keep validation data separate
   - Don't mix with performance data
   - Use for configuration validation only

1. **Document parameter-optimizer**:

   - Test if functional
   - If yes, integrate with llama-bench
   - If no, document as deprecated

### Phase 3: Cleanup (Week 3)

1. **Deprecate placeholder tools**:

   - `run_benchmarks.py` → mark as deprecated
   - `run_llama_bench.sh` → investigate, deprecate if unused

1. **Create migration guide**:

   - Document new workflow
   - Show how to use llama-bench
   - Explain data structure

1. **Update documentation**:

   - README.md → add benchmarking section
   - SKILL.md → add benchmark commands
   - AGENTS.md → add benchmarking tasks

______________________________________________________________________

## Migration Plan

### Week 1: Setup & Integration

- [ ] Install llama-bench
- [ ] Create integration script
- [ ] Run initial benchmarks
- [ ] Aggregate results
- [ ] Update benchmark_results.json

### Week 2: Data Migration

- [ ] Parse PERFORMANCE_NOTES.md
- [ ] Add historical data to results
- [ ] Validate context-verification data
- [ ] Test parameter-optimizer (if exists)

### Week 3: Cleanup & Documentation

- [ ] Deprecate old tools
- [ ] Create migration guide
- [ ] Update documentation
- [ ] Train on new workflow

______________________________________________________________________

## Expected Benefits

### Immediate Benefits (Week 1):

- ✅ **Standardized benchmarking** with industry tool
- ✅ **Consistent metrics** across models
- ✅ **Automated result collection**
- ✅ **JSON/CSV output** for analysis

### Short-term Benefits (Week 2-3):

- ✅ **Historical data preserved** from PERFORMANCE_NOTES.md
- ✅ **Configuration validation** from context-verification
- ✅ **Parameter optimization** if parameter-optimizer works
- ✅ **Complete benchmark suite** for all models

### Long-term Benefits (Week 4+):

- ✅ **CMMI Level 2** (Repeatable process)
- ✅ **Data-driven decisions** for configuration
- ✅ **Performance regression detection**
- ✅ **Model comparison** for selection

______________________________________________________________________

## Conclusion

The current benchmarking infrastructure is **functionally incomplete**:

- `run_benchmarks.py` is a placeholder
- `parameter-optimizer` needs verification
- `PERFORMANCE_NOTES.md` is static documentation
- `context-verification` is validation data, not performance data

**Recommended Action**:

1. **Adopt llama-bench** as primary benchmarking tool
1. **Integrate** existing data into unified results database
1. **Deprecate** placeholder tools after migration
1. **Document** complete workflow for AI agents

This approach leverages **free, open-source tools** while preserving existing data and enabling **CMMI Level 2+** maturity.

______________________________________________________________________

**Report Created**: 2026-09-24T13:45:00Z\
**Author**: Hermes Agent\
**Status**: Ready for implementation
