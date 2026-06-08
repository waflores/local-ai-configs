# Quick Start Guide

Get up and running with LlamaStash + llama-swap in minutes.

## Prerequisites

- LlamaStash daemon installed and running
- llama-swap binary installed
- External model on port 10001

## One-Command Setup

### 1. Verify LlamaStash

```bash
/home/waflores/.cargo/bin/llamastash daemon status
```

### 2. Start llama-swap

```bash
/home/waflores/.cargo/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integration.yaml \
  --listen 127.0.0.1:8080
```

### 3. Access Web UI

```bash
open http://localhost:8080/ui
```

## Basic Commands

### Check Health

```bash
curl http://127.0.0.1:8080/health
```

### List Models

```bash
curl http://127.0.0.1:8080/v1/models
```

### View Logs

```bash
/home/waflores/.cargo/bin/llama-swap logs stream
```

### View Metrics

```bash
curl http://127.0.0.1:8080/metrics
```

## Auto-Discovery

### Discover Models

```bash
/home/waflores/.cargo/bin/llama-swap-integrate.sh status
```

### Generate Config

```bash
/home/waflores/.cargo/bin/llama-swap-integrate.sh generate
```

### All Commands

```bash
/home/waflores/.cargo/bin/llama-swap-integrate.sh all
```

## Integration Scripts

### Start Integration

```bash
/home/waflores/.cargo/bin/llama-swap-integration.sh
```

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Web UI | `http://localhost:8080/ui` | Model playground |
| Health | `http://localhost:8080/health` | Health check |
| Models | `http://localhost:8080/v1/models` | List models |
| Logs | `/logs/stream` | Live logs |
| Metrics | `http://localhost:8080/metrics` | Prometheus |

## Quick Troubleshooting

### LlamaStash not running

```bash
/home/waflores/.cargo/bin/llamastash daemon start
```

### Model not responding

```bash
# Check if running
ps aux | grep llama-server

# Restart if needed
kill <PID>
/home/waflores/.local/share/inferhost/bin/llama-server \
  --port 10001 \
  --model /home/waflores/.lmstudio/models/lmstudio-community/Qwen3.5-9B-GGUF/Qwen3.5-9B-Q4_K_M.gguf
```

### Port in use

```bash
# Use different port
/home/waflores/.cargo/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integration.yaml \
  --listen 127.0.0.1:8081
```

## Next Steps

1. ✅ **Access Web UI** - Open `http://localhost:8080/ui`
1. ✅ **Test inference** - Try the playground
1. ✅ **Explore logs** - Check `/logs/stream`
1. ✅ **View metrics** - Access `/metrics`
1. ✅ **Discover models** - Run auto-discovery

## Common Use Cases

### Chat with Model

```bash
curl -X POST http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-9B-GGUF",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### Stream Logs

```bash
/home/waflores/.cargo/bin/llama-swap logs stream
```

### Get Metrics

```bash
curl http://127.0.0.1:8080/metrics | grep "llama_server_requests_total"
```

## Status

**Setup Status:** Ready\
**Integration Version:** 1.0\
**Last Updated:** 2024
