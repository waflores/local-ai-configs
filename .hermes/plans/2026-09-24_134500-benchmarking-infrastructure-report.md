# Benchmarking Infrastructure Report — Re-issued

> **Status:** ⚠️ Re-issued with corrected facts (see §2)
> **Last reviewed:** 2026-10-24
> **Author:** Hermes Agent

______________________________________________________________________

## 1. Executive summary

The benchmarking infrastructure in this repo is **functionally incomplete** and **not being leveraged**:

- `llama-swap/run_benchmarks.py` is a **placeholder** (TODO-only, no real logic). ✅
- `llama-swap/run_llama_bench.sh` is a **generic shell wrapper** that does not measure throughput/latency at scale. ✅
- `parameter-optimizer/` scripts claim throughput benchmarking and config generation, but their outputs are **unverified** — they only produce results when a live llama-swap/llama-server is running and `LLAMA_SERVER_BIN`/`LLAMA_MODEL_PATH` are set. ✅
- `PERFORMANCE_NOTES.md` is **static documentation**, not live benchmark data. ✅
- `context-verification/*.json` is **validation metadata**, not performance data. ✅

This report recommends adopting a standard, open-source benchmarking tool (llama-bench / llama-benchy / llama.cpp `llama-bench`) rather than continuing to hand-roll a suite, and folding the existing `PERFORMANCE_NOTES.md` data into a normalized results pipeline.

______________________________________________________________________

## 2. What's actually in the repo (corrected facts)

### Model counts vs. what the plans claimed

| What the plans said | What's actually true |
|---------------------|----------------------|
| 22 models in `llama-swap/config.yaml` | **6 models** in `llama-swap/config.yaml` |
| `config.yaml` = 29 model definitions | `config.yaml` = 6 models |
| `context-verification/*.json` = model registry (22 files) | **22 files** — correct, this is the source of truth for `llm_manager` |
| `llama-swap/run_benchmarks.py` is a to-be-rewritten runner | Still a **placeholder** in the working tree (714 bytes, TODO comments) |

### Existing tooling

- `llama-swap/run_benchmarks.py` — **placeholder**, TODO-only. References hard-coded `/home/waflores/...` paths and `logs/benchmarks/`.
- `llama-swap/run_llama_bench.sh` — a shell wrapper that parses `config.yaml`, starts a temporary llama-server, sends one test request, and writes a markdown report. It does **not** measure throughput/latency at scale and is not wired into a real benchmark pipeline.
- `llama-swap/parameter-optimizer/parameter-optimizer.py` + `batch-analyzer.py` + `README.md` — claim throughput benchmarking and config generation, but:
  - The scripts only produce real results if a live llama-swap/llama-server is running and `LLAMA_SERVER_BIN` / `LLAMA_MODEL_PATH` are set.
  - The `llama-throughput-lab` dependency referenced in the code is **not** checked out in the repo.
  - The README claims ("Run throughput benchmarks", "Generate optimized configurations") are **unverified** — the scripts do not currently produce the promised `*_analysis.json`, `*_benchmark.json`, `optimized-*.json`, `optimized-config.yaml` outputs from a clean checkout.
- `PERFORMANCE_NOTES.md` — static markdown benchmark notes (historical, not timestamped, not linked to specific `config.yaml` checksums or outputs).
- `context-verification/*.json` — 22 model metadata verification files. These are **config/validation metadata**, not performance measurements.

### What the repo has that this plan should leverage

- `llm_manager/` — Flask app + FastAPI docs; hardware-aware profile generation; config/tuning persistence/export; ORM + SQLite; tests.
- `nix/` — treefmt-nix + blueprint flake (x86_64-linux), pre-commit hooks, CI.
- `scripts/check-md-links.py` — markdown link checker wired into `.pre-commit-config.yaml` and CI.
- `docs/`: `llama-swap.md` (performance targets), `monorepo.md` (layout + rules), `inference-tuning.md` (context sizing math).
- `docs/monorepo.md` and `docs/monorepo.md` rule set: `llama-swap/` gets first-class docs/review; `other_experiments/` is experimental/throwaway.

______________________________________________________________________

## 3. Recommendation

### Primary recommendation: adopt a standard benchmark tool

The most defensible, maintainable path is to **standardize on one open-source tool** and either:

1. **Adopt llama-bench** (`alexziskind1/llama-throughput-lab`, MIT, actively maintained) as the primary tool, or
1. **Wrap an existing tool** (llama-bench / llama-benchy / llama.cpp `llama-bench`) with a thin Python/Shell driver, and keep the hand-rolled `run_benchmarks.py` only as a deprecated placeholder.

Continue **not** to hand-roll a benchmark suite from scratch. The repo's existing scripts (`run_benchmarks.py`, `run_llama_bench.sh`, `parameter-optimizer/`) have produced **zero** committed benchmark results and are a maintenance burden without a clear, standardized output format.

### Data hygiene: don't mix validation with performance

- `context-verification/*.json` stays **config/validation metadata** (model size, declared vs. memory-safe context).
- `PERFORMANCE_NOTES.md` data should be **migrated into normalized benchmark results** with timestamps, config hash, and linkage — not kept as standalone markdown.
- New benchmark outputs should be **one canonical format** (JSON) under `logs/benchmark/`.

### Deprecate or fix the parameter-optimizer claims

- **Test the scripts now.** If they produce the promised outputs, fix the README to match reality and add a `logs/parameter-analysis/` output directory.
- If they don't, **mark the README claims as inaccurate** and deprecate the scripts, or leave them as config-tuning helpers without benchmark claims.

______________________________________________________________________

## 4. Migration plan (updated for current repo state)

### Week 1 — Setup & integration

- [ ] Install one standard benchmark tool (`llama-bench` / `llama-benchy` / llama.cpp `llama-bench`), or keep a thin wrapper around it.
- [ ] Replace `llama-swap/run_benchmarks.py` placeholder with a real idempotent benchmark driver (or document clearly that it is deprecated and wire the real tool).
- [ ] Run a first benchmark pass and produce a normalized JSON results file.
- [ ] Update `logs/benchmark/` with per-model results.
- [ ] Update `docs/llama-swap.md`, `SKILL.md`, and `llama-swap/README.md` to reference the real pipeline (not the placeholders).

### Week 2 — Data migration

- [ ] Migrate `PERFORMANCE_NOTES.md` historical data into the normalized results format (timestamps + linkage).
- [ ] Validate `context-verification` data is used only for validation, never mixed with performance data.
- [ ] Test the `parameter-optimizer` scripts; fix README claims or deprecate.

### Week 3 — Cleanup & documentation

- [ ] Deprecate the placeholder `run_benchmarks.py` and `run_llama_bench.sh` if the standard tool is adopted.
- [ ] Add a migration guide documenting the new workflow + canonical output format.
- [ ] Update `docs/monorepo.md`, `docs/llama-swap.md`, `README.md`, `AGENTS.md`, `SKILL.md`, `.hermes.md` to reflect the corrected model counts (22 in `context-verification`, 6 in `config.yaml`) and the live benchmark pipeline.

______________________________________________________________________

## 5. Expected benefits

### Immediate (Week 1)

- Standardized benchmarking with a recognized tool.
- Consistent metrics across models.
- Automated result collection in a canonical JSON format.
- No more ambiguous "placeholder" benchmark scripts.

### Short-term (Week 2–3)

- Historical data from `PERFORMANCE_NOTES.md` preserved and usable.
- Configuration-validation data stays separate from performance data.
- `parameter-optimizer` claims resolved (verified or deprecated).
- Full benchmark pipeline wired and documented.

### Long-term (Week 4+)

- Reproducible benchmark data → data-driven configuration decisions.
- Performance regression detection.
- Model comparison for selection.
- Baseline for CMMI Level 2 (repeatable) rather than Level 5.

______________________________________________________________________

## 6. Conclusion

The benchmarking infrastructure is **functionally incomplete**:

- `run_benchmarks.py` is a placeholder that must be retired or replaced.
- `run_llama_bench.sh` is a thin wrapper, not a pipeline.
- `parameter-optimizer` claims are unverified.
- `PERFORMANCE_NOTES.md` is static, not live data.
- `context-verification` is validation metadata, not performance data.

**Action items:**

1. **Adopt a standard benchmark tool** (llama-bench / llama-benchy / llama.cpp llama-bench).
1. **Integrate existing data** into a normalized, timestamped results pipeline.
1. **Deprecate the placeholder scripts** after migration.
1. **Correct documentation** (model counts, benchmark status, hardpaths).
1. **Resolve the unverified `parameter-optimizer` claims** — test, fix, or deprecate.

This approach uses free, open-source tooling, preserves existing data, and gives the repo a real, repeatable benchmark foundation.

______________________________________________________________________

**Report created:** 2026-09-24\
**Re-issued:** 2026-10-24\
**Status:** Ready for implementation (after re-baselining model counts & tool decision)
