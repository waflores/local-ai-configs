# Configuration Structure

This document explains the configuration file hierarchy and what each file controls in the LlamaStash + llama-swap integration.

## Configuration Files

### 1. Integration Configuration

**File:** `llamastash-integration.yaml`

**Location:** `/home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integration.yaml`

**Purpose:** Main llama-swap configuration for LlamaStash integration

**Controls:**

- Health check timeout
- Port configuration
- Model definitions
- Performance settings
- API keys
- Hooks

**Key Settings:**

```yaml
healthCheckTimeout: 60         # Health check timeout in seconds
logLevel: info                 # Logging level
logToStdout: "proxy"           # Log output destination
startPort: 10001               # External model serving port
models:                        # Model definitions
  Qwen3.5-9B-GGUF:             # Model entries
    name: "Qwen3.5 9B"         # Display name
    proxy: http://127.0.0.1:10001  # Proxy endpoint
    ttl: 600                   # Time-to-live in seconds
```

### 2. llama-swap Integration Script

**File:** `llama-swap-integration.sh`

**Location:** `/home/waflores/DevFolder/ai/local-config/llamastash/llama-swap-integration.sh`

**Purpose:** Launcher script that:
1. Checks LlamaStash daemon status
2. Verifies external model is running
3. Starts llama-swap with integration config

**Usage:**

```bash
/home/waflores/.cargo/bin/llama-swap-integration.sh
```

### 3. Auto-Discovery Script

**File:** `llamastash-integrate.sh`

**Location:** `/home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integrate.sh`

**Purpose:** Discovers models from LlamaStash and generates llama-swap configuration dynamically

**Commands:**

```bash
/home/waflores/.cargo/bin/llama-swap-integrate.sh status     # Check daemon status
/home/waflores/.cargo/bin/llama-swap-integrate.sh discover   # Discover models
/home/waflores/.cargo/bin/llama-swap-integrate.sh generate   # Generate config
/home/waflores/.cargo/bin/llama-swap-integrate.sh all        # Run all commands
```

## Environment Variables

### LlamaStash Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `LLAMASTASH_STATE_DIR` | Override state directory | `/tmp/llamastash` |
| `LLAMASTASH_CONFIG_DIR` | Override config directory | `/tmp/llama-swap-config` |
| `LLAMASTASH_CACHE_DIR` | Override cache directory | `/tmp/llamastash-cache` |
| `LLAMASTASH_IPC_URL` | Override IPC URL | `http://127.0.0.1:48134` |
| `LLAMASTASH_IPC_TOKEN` | Override IPC token | `secret-token` |

### llama-swap Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `LLAMA_SWAP_CONFIG` | Override config path | `/tmp/llama-swap-config.yaml` |
| `LLAMA_SWAP_LISTEN` | Override listen address | `127.0.0.1:8081` |
| `LLAMA_SWAP_PORT` | Override port | `8081` |

## Configuration Hierarchy

```
/home/waflores/DevFolder/ai/local-config/
├── llamastash/
│   ├── llamastash-integration.yaml   # Integration config
│   ├── llama-swap-integration.sh     # Launcher script
│   ├── llamastash-integrate.sh       # Auto-discovery tool
│   ├── llamastash-integration.md     # Documentation
│   └── logs/                         # Log files
├── llama-swap/                       # Existing llama-swap configs
├── inferhost/                        # Existing inferhost configs
└── continue-dev/                     # continue.dev configs
```

## Path Conventions

### Config Files

- **Integration config:** `/home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integration.yaml`
- **llama-swap default:** `/home/waflores/.config/llama-swap/config.yaml`
- **Logs:** `/home/waflores/DevFolder/ai/local-config/llamastash/logs/`

### Binary Paths

- **LlamaStash:** `/home/waflores/.cargo/bin/llamastash`
- **llama-swap:** `/home/waflores/.cargo/bin/llama-swap`

### Model Paths

- **External models:** `/home/waflores/.local/share/inferhost/bin/llama-server`
- **HF cache:** `/home/waflores/.cache/huggingface/hub`

## Configuration Override Pattern

### 1. Environment Variables (Highest Priority)

```bash
export LLAMA_SWAP_LISTEN="127.0.0.1:8081"
/home/waflores/.cargo/bin/llama-swap --config <CONFIG>
```

### 2. Command-line Flags (High Priority)

```bash
/home/waflores/.cargo/bin/llama-swap \
  --config /path/to/config.yaml \
  --listen 127.0.0.1:8080
```

### 3. Config File (Default)

```yaml
# /home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integration.yaml
healthCheckTimeout: 60
logLevel: info
```

## Configuration Examples

### Basic Configuration

```yaml
healthCheckTimeout: 60
logLevel: info
startPort: 10001
models:
  Qwen3.5-9B-GGUF:
    name: "Qwen3.5 9B"
    proxy: http://127.0.0.1:10001
    ttl: 600
```

### Advanced Configuration

```yaml
healthCheckTimeout: 60
logLevel: info
logToStdout: "proxy"
metricsMaxInMemory: 1000
startPort: 10001
sendLoadingState: true
includeAliasesInList: false
globalTTL: 0

models:
  Qwen3.5-9B-GGUF:
    name: "Qwen3.5 9B"
    description: "Qwen3.5 9B with reasoning capabilities"
    proxy: http://127.0.0.1:10001
    ttl: 600
    checkEndpoint: /health
    unlisted: false

performance:
  disabled: false
  every: 15s

sendLoadingState: true
apiKeys: []

hooks:
  on_startup:
    - "llama-swap-integration.sh"
```

## Configuration Validation

### Check Config Syntax

```bash
/home/waflores/.cargo/bin/llama-swap --config /path/to/config.yaml --help
```

### Verify Integration

```bash
/home/waflores/.cargo/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integration.yaml \
  --listen 127.0.0.1:8080
```

### Health Check

```bash
curl http://127.0.0.1:8080/health
```

## Status

**Configuration System:** Complete  
**Integration Version:** 1.0  
**Last Updated:** 2024
