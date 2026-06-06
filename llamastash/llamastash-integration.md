# LlamaStash + llama-swap Integration

This directory contains scripts and configurations for integrating **LlamaStash** (Rust-based launcher) with **llama-swap** (Go-based proxy manager).

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

### 3. Access Web UI

Open in browser: `http://localhost:8080/ui`

### 4. Check Health

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/models
```

## Available Scripts

### Integration Launcher

```bash
/home/waflores/.cargo/bin/llama-swap-integration.sh
```

**Purpose:** Starts llama-swap with LlamaStash integration configuration and verifies LlamaStash daemon is running.

**Usage:**
```bash
/home/waflores/.cargo/bin/llama-swap-integration.sh
```

### Auto-Discovery Tool

```bash
/home/waflores/.cargo/bin/llama-swap-integrate.sh
```

**Purpose:** Discovers models from LlamaStash and generates llama-swap configuration dynamically.

**Usage:**
```bash
/home/waflores/.cargo/bin/llama-swap-integrate.sh status      # Check daemon status
/home/waflores/.cargo/bin/llama-swap-integrate.sh discover   # Discover models
/home/waflores/.cargo/bin/llama-swap-integrate.sh generate   # Generate config
/home/waflores/.cargo/bin/llama-swap-integrate.sh all        # Run all commands
```

## Configuration Files

### llamastash-integration.yaml

Main configuration file for llama-swap integration:

- **healthCheckTimeout:** 60 seconds
- **startPort:** 10001
- **Proxy endpoint:** `http://127.0.0.1:10001`
- **Models:** Qwen3.5-9B, Granite 4.0, Nemotron 3 Nano, Zerank 2.0

### llama-swap-integration.sh

Integration launcher script that:
1. Checks LlamaStash daemon status
2. Verifies external model is running
3. Starts llama-swap with integration config

### llamastash-integrate.sh

Auto-discovery tool that:
1. Fetches LlamaStash status
2. Discovers available models
3. Generates llama-swap configuration

## Access Points

| Endpoint | URL | Description |
|----------|-----|-------------|
| Web UI | `http://localhost:8080/ui` | Model playground |
| Health | `http://localhost:8080/health` | Health check |
| Models | `http://localhost:8080/v1/models` | List available models |
| Logs | `/logs/stream` | Live log streaming |
| Metrics | `http://localhost:8080/metrics` | Prometheus metrics |

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

## Benefits of Integration

- ✅ **Auto-discovery:** LlamaStash discovers models from HF/Ollama/LM Studio caches
- ✅ **Web UI:** llama-swap provides interactive playground
- ✅ **Log streaming:** Real-time logs via `/logs/stream`
- ✅ **Metrics:** Prometheus-compatible metrics at `/metrics`
- ✅ **Hardware-aware:** LlamaStash uses RTX 5070 defaults
- ✅ **Debugging:** Request/response capture via `/capture`

## Troubleshooting

### LlamaStash daemon not running

```bash
/home/waflores/.cargo/bin/llamastash daemon start --listen 127.0.0.1:48134
```

### Model not responding on port 10001

Check if external model is running:
```bash
ps aux | grep llama-server
curl http://127.0.0.1:10001/health
```

### Port already in use

```bash
# Find process using port 10001
lsof -i :10001

# Or kill and restart
kill <PID>
/home/waflores/.cargo/bin/llama-swap --config <CONFIG> --listen 127.0.0.1:10002
```

## File Structure

```
/home/waflores/DevFolder/ai/local-config/llamastash/
├── llamastash-integration.yaml   # Main integration config
├── llama-swap-integration.sh     # Integration launcher
├── llamastash-integrate.sh       # Auto-discovery tool
├── llamastash-integration.md     # This documentation
└── logs/                         # Log files
    ├── llama-swap-integration.log
    └── llamastash-integration.log
```

## Next Steps

1. Start llama-swap with integration config
2. Access Web UI at `http://localhost:8080/ui`
3. Test model inference
4. Explore log streaming and metrics
5. Optionally enable auto-discovery for dynamic model management

---

**Status:** Integration ready for deployment
**Last Updated:** 2024
**Integration Version:** 1.0
