# LlamaStash + llama-swap Local LLM Infrastructure

## Overview

This project provides a complete infrastructure for managing local LLMs with **LlamaStash** (Rust-based launcher) and **llama-swap** (Go-based proxy manager), integrated for seamless use with tools like **continue.dev** on VSCode and other AI coding agents.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    llama-swap (Port 8080)                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  /ui  →  Web playground                                 │ │
│  │  /logs/stream  →  Live logs                             │ │
│  │  /metrics  →  Prometheus metrics                        │ │
│  │  /v1/*  →  Proxy to LlamaStash                          │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              │                                │
│                              ▼                                │
│         ┌──────────────────────────────────────────┐         │
│         │  LlamaStash Daemon (Port 48134)         │         │
│         │  (Control Plane - JSON-RPC)             │         │
│         └──────────────────────────────────────────┘         │
│                              │                                │
│                              ▼                                │
│         ┌──────────────────────────────────────────┐         │
│         │  LlamaStash Proxy (Port 11435)          │         │
│         │  (OpenAI-compatible endpoint)           │         │
│         └──────────────────────────────────────────┘         │
│                              │                                │
│              ┌───────────────┴───────────────┐               │
│              ▼                                 ▼              │
│    ┌─────────────────────┐     ┌─────────────┐               │
│    │ llama-server 10001 │     │ llama-server│               │
│    │ (Qwen3.5-9B)       │     │ (managed)   │               │
│    └─────────────────────┘     └─────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Verify LlamaStash Daemon

```bash
cd /home/waflores/DevFolder/ai/local-config/llamastash
/home/waflores/.cargo/bin/llamastash daemon status
```

### 2. Start llama-swap with Integration

```bash
/home/waflores/.cargo/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integration.yaml \
  --listen 127.0.0.1:8080
```

### 3. Access Web UI

Open in browser: `http://localhost:8080/ui`

### 4. Verify Integration

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/models
```

## Available Skills

This project uses the **Agent Skills** format for extending AI agent capabilities:

- **llama-swap-config/** - Configure llama-swap for different scenarios
- **llamastash-integration/** - API-level integration setup
- **model-discovery/** - Discover and catalog models
- **health-monitoring/** - Monitor health endpoints
- **performance-benchmarking/** - Run performance benchmarks
- **log-analysis/** - Analyze logs and detect issues

## Documentation

- **[AGENTS.md](./AGENTS.md)** - Project-level guidance for AI agents
- **[INSTALL.md](./INSTALL.md)** - Installation guide
- **[QUICK-START.md](./QUICK-START.md)** - One-command setup
- **[CONFIG-STRUCTURE.md](./CONFIG-STRUCTURE.md)** - Configuration hierarchy
- **[API-SPECIFICATIONS.md](./API-SPECIFICATIONS.md)** - API endpoints
- **[INTEGRATION-PATTERNS.md](./INTEGRATION-PATTERNS.md)** - Integration strategies
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and solutions

## Technical Details

### LlamaStash Daemon
- **Control Plane:** `http://127.0.0.1:48134` (JSON-RPC)
- **Proxy:** `http://127.0.0.1:11435` (OpenAI-compatible)
- **Binary:** `/home/waflores/.cargo/bin/llamastash`

### llama-swap
- **Binary:** `/home/waflores/.cargo/bin/llama-swap`
- **Default Port:** 8080
- **Web UI:** `/ui`
- **Log Streaming:** `/logs/stream`
- **Metrics:** `/metrics`

## Supported Models

- Qwen3.5-9B-GGUF
- IBM Granite 4.0 Hybrid Tiny 7B
- NVIDIA Nemotron 3 Nano 4B
- Zerank 2.0 (reranking/embedding)

## Access Points

| Endpoint | URL | Description |
|----------|-----|-------------|
| Web UI | `http://localhost:8080/ui` | Model playground |
| Health | `http://localhost:8080/health` | Health check |
| Models | `http://localhost:8080/v1/models` | List available models |
| Logs | `/logs/stream` | Live log streaming |
| Metrics | `http://localhost:8080/metrics` | Prometheus metrics |

## Benefits

- ✅ **Auto-discovery:** LlamaStash discovers models from HF/Ollama/LM Studio caches
- ✅ **Web UI:** llama-swap provides interactive playground
- ✅ **Log streaming:** Real-time logs via `/logs/stream`
- ✅ **Metrics:** Prometheus-compatible metrics at `/metrics`
- ✅ **Hardware-aware:** LlamaStash uses RTX 5070 defaults
- ✅ **Debugging:** Request/response capture via `/capture`

## Status

**Integration Version:** 1.0  
**Last Updated:** 2024  
**Status:** Ready for deployment
