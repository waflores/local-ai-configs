# AGENTS.md

This file provides project-level guidance to AI agents (Claude Code, OpenCode, Codex, Copilot CLI, Cursor, etc.) working in this repository. Treat it as authoritative alongside `README.md`.

## Project Overview

**LlamaStash + llama-swap** is a local LLM infrastructure project that combines:

- **LlamaStash** (Rust-based launcher) - Model discovery, lifecycle management, auto-tuning
- **llama-swap** (Go-based proxy manager) - Web UI, concurrent model management, advanced proxy features

**Goal:** Create a seamless local LLM management system that integrates with AI coding agents like continue.dev on VSCode.

## Setup Commands

### 1. Verify LlamaStash Daemon

```bash
/home/waflores/.cargo/bin/llamastash daemon status
```

Expected output:

```json
{
  "proxy": { "enabled": true, "listen": "127.0.0.1:11435" },
  "external": [{ "pid": 132604, "port": 10001, ... }]
}
```

### 2. Start llama-swap with Integration

```bash
/home/waflores/.cargo/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integration.yaml \
  --listen 127.0.0.1:8080
```

### 3. Verify Integration

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/models
```

### 4. Access Web UI

```bash
open http://localhost:8080/ui
```

## Build/Test/Lint

### Available Commands

```bash
# Check LlamaStash daemon status
/home/waflores/.cargo/bin/llamastash daemon status --json

# Start llama-swap with integration
/home/waflores/.cargo/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integration.yaml \
  --listen 127.0.0.1:8080

# Auto-discovery tool
/home/waflores/.cargo/bin/llama-swap-integrate.sh status
/home/waflores/.cargo/bin/llama-swap-integrate.sh discover
/home/waflores/.cargo/bin/llama-swap-integrate.sh generate
/home/waflores/.cargo/bin/llama-swap-integrate.sh all

# Health checks
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/models

# Access logs
/home/waflores/.cargo/bin/llama-swap logs stream

# Access metrics
curl http://127.0.0.1:8080/metrics
```

### Testing

```bash
# Verify integration
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/models

# Test model inference
curl -X POST http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-9B-GGUF",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Conventions

### Configuration

- Use `llamastash-integration.yaml` for LlamaStash integration
- Use `llama-swap-integration.yaml` for llama-swap configuration
- Environment variables override config file settings
- Path conventions:
  - Config: `/home/waflores/DevFolder/ai/local-config/llamastash/`
  - Logs: `/home/waflores/DevFolder/ai/local-config/llamastash/logs/`

### API Endpoints

- **LlamaStash Control Plane:** `http://127.0.0.1:48134` (JSON-RPC)
- **LlamaStash Proxy:** `http://127.0.0.1:11435` (OpenAI-compatible)
- **llama-swap:** `http://127.0.0.1:8080` (Web UI + proxy)

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 64 | Bad CLI usage |
| 65 | Daemon unreachable |
| 66 | Model not found |
| 67 | Launch failed |
| 68 | Stop failed |

## Documentation Sync Requirements

After any change that alters user-visible behavior, update:

- **README.md** - Install, quickstart, feature list
- **AGENTS.md** (this file) - Scope boundaries, exit codes
- **INSTALL.md** - Installation paths, prerequisites
- **CONFIG-STRUCTURE.md** - Configuration keys, defaults
- **CHANGELOG.md** - User-visible changes

## Common Gotchas

1. **LlamaStash daemon must be running** - llama-swap proxies to LlamaStash's control plane
1. **Port 10001 must be available** - External model serving port
1. **Use `--json` for stable output** - Pin against `--json`, not TTY rendering
1. **Daemon restart required** - Changes to config require restarting llama-swap
1. **External models vs managed models** - LlamaStash manages models on its proxy port; external models are proxied separately

## Architecture

```
TUI / CLI ──HTTP+Bearer──► Control plane (127.0.0.1:48134, loopback, bearer token)
OpenCode / Pi / SDK ──HTTP──► Proxy listener (127.0.0.1:11435, loopback, no auth)
                          │
                          ├── Discovery (scan + watch + caches)
                          ├── GGUF parser (metadata + identity)
                          ├── Process supervisor (spawn / probe / stop)
                          ├── Resource monitor (RAM/VRAM/CPU)
                          └── Persisted state (favorites / presets / running)
```

## Skills Directory Structure

This project uses **Agent Skills** for extending AI agent capabilities:

```
llama-swap-config/       # Configure llama-swap for different scenarios
llamastash-integration/   # API-level integration setup
model-discovery/          # Discover and catalog models
health-monitoring/        # Monitor health endpoints
performance-benchmarking/ # Run performance benchmarks
log-analysis/             # Analyze logs and detect issues
```

Each skill folder contains:

- `SKILL.md` - Metadata and instructions
- Configuration files
- Scripts
- Templates

## Security Considerations

- API keys stored in config file (review before committing)
- Loopback-only connections (127.0.0.1)
- No LAN binding in current setup
- Bearer token auth for LlamaStash control plane

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `LLAMASTASH_STATE_DIR` | Override state directory | `/tmp/llamastash` |
| `LLAMASTASH_CONFIG_DIR` | Override config directory | `/tmp/llama-swap-config` |
| `LLAMASTASH_CACHE_DIR` | Override cache directory | `/tmp/llamastash-cache` |
| `HF_HOME` | Override HF cache | `/tmp/huggingface` |

## Next Steps

1. ✅ Verify LlamaStash daemon status
1. ✅ Start llama-swap with integration config
1. ✅ Access Web UI at `http://localhost:8080/ui`
1. ✅ Test model inference
1. ✅ Explore log streaming and metrics
1. ✅ Optionally enable auto-discovery

______________________________________________________________________

**Status:** Integration ready for deployment\
**Last Updated:** 2024\
**Integration Version:** 1.0
