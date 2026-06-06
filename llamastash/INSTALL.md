# Installing LlamaStash + llama-swap Integration

This guide covers installation of the LlamaStash + llama-swap integration for local LLM management.

## Prerequisites

### Required

- **LlamaStash daemon** running on ports 48134 (control) and 11435 (proxy)
- **llama-swap** binary installed
- **Port 10001** available for external model serving

### LlamaStash Daemon

Verify LlamaStash is installed and running:

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

### llama-swap

Verify llama-swap is installed:

```bash
/home/waflores/.cargo/bin/llama-swap --version
```

## Installation Steps

### 1. Verify LlamaStash Daemon

```bash
/home/waflores/.cargo/bin/llamastash daemon status
```

If not running:

```bash
/home/waflores/.cargo/bin/llamastash daemon start --listen 127.0.0.1:48134
```

### 2. Verify External Model

Check if external model is running on port 10001:

```bash
curl http://127.0.0.1:10001/health
```

If not running, start it:

```bash
/home/waflores/.local/share/inferhost/bin/llama-server \
  --port 10001 \
  --model /home/waflores/.lmstudio/models/lmstudio-community/Qwen3.5-9B-GGUF/Qwen3.5-9B-Q4_K_M.gguf \
  --n-gpu-layers all
```

### 3. Start llama-swap with Integration

```bash
/home/waflores/.cargo/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integration.yaml \
  --listen 127.0.0.1:8080
```

### 4. Verify Integration

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/models
```

Expected output:
```json
{"health":"ok"}
{"models":[{"id":"Qwen3.5-9B-GGUF",...}]}
```

## Configuration Files

### Integration Configuration

```bash
/home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integration.yaml
```

Key settings:
- `healthCheckTimeout: 60` - Health check timeout in seconds
- `startPort: 10001` - Port for external model serving
- `proxy: http://127.0.0.1:10001` - Proxy endpoint

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `LLAMA_SWAP_CONFIG` | Override config path | `/tmp/llama-swap-config.yaml` |
| `LLAMA_SWAP_LISTEN` | Override listen address | `127.0.0.1:8081` |
| `LLAMASTASH_STATE_DIR` | Override state directory | `/tmp/llamastash` |
| `LLAMASTASH_CONFIG_DIR` | Override config directory | `/tmp/llama-swap-config` |

## Verification

### Health Check

```bash
curl http://127.0.0.1:8080/health
```

Expected:
```json
{"health":"ok"}
```

### Models List

```bash
curl http://127.0.0.1:8080/v1/models
```

Expected:
```json
{"models":[{"id":"Qwen3.5-9B-GGUF","name":"Qwen3.5 9B"}]}
```

### Web UI Access

Open in browser: `http://localhost:8080/ui`

## Access Points

| Endpoint | URL | Description |
|----------|-----|-------------|
| Web UI | `http://localhost:8080/ui` | Model playground |
| Health | `http://localhost:8080/health` | Health check |
| Models | `http://localhost:8080/v1/models` | List available models |
| Logs | `/logs/stream` | Live log streaming |
| Metrics | `http://localhost:8080/metrics` | Prometheus metrics |

## Troubleshooting

### LlamaStash daemon not running

```bash
/home/waflores/.cargo/bin/llamastash daemon start --listen 127.0.0.1:48134
```

### Model not responding on port 10001

```bash
ps aux | grep llama-server
# Kill if needed
kill <PID>
```

### Port already in use

```bash
# Find process using port 10001
lsof -i :10001

# Or use different port
/home/waflores/.cargo/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integration.yaml \
  --listen 127.0.0.1:8081
```

## Uninstallation

### Stop llama-swap

```bash
# Kill the process
pkill -f llama-swap

# Or use PID
kill <PID>
```

### Remove configuration files

```bash
rm /home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integration.yaml
rm /home/waflores/.config/llama-swap/llama-swap-integration.yaml
```

### Clean up

```bash
rm -rf /home/waflores/DevFolder/ai/local-config/llamastash/logs/
```

## Status

**Installation Status:** Complete  
**Integration Version:** 1.0  
**Last Verified:** 2024
