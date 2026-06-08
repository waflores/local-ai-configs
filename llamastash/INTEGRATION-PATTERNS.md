# INTEGRATION-PATTERNS.md

# LlamaStash + llama-swap Integration Patterns

This document describes the different integration patterns available for combining LlamaStash and llama-swap, with working examples and trade-offs.

## Table of Contents

- [INTEGRATION-PATTERNS.md](#integration-patternsmd)
- [LlamaStash + llama-swap Integration Patterns](#llamastash--llama-swap-integration-patterns)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Pattern 1: API-Level Proxy](#pattern-1-api-level-proxy)
    - [Architecture](#architecture)
    - [Configuration](#configuration)
    - [Pros](#pros)
    - [Cons](#cons)
    - [Use Cases](#use-cases)
  - [Pattern 2: LlamaStash as Primary, llama-swap as UI](#pattern-2-llamastash-as-primary-llama-swap-as-ui)
    - [Architecture](#architecture-1)
    - [Configuration](#configuration-1)
    - [Pros](#pros-1)
    - [Cons](#cons-1)
    - [Use Cases](#use-cases-1)
  - [Pattern 3: llama-swap as Primary, LlamaStash as Model Manager](#pattern-3-llama-swap-as-primary-llamastash-as-model-manager)
    - [Architecture](#architecture-2)
    - [Configuration](#configuration-2)
    - [Pros](#pros-2)
    - [Cons](#cons-2)
    - [Use Cases](#use-cases-2)
  - [Pattern 4: Hybrid Architecture](#pattern-4-hybrid-architecture)
    - [Architecture](#architecture-3)
    - [Configuration](#configuration-3)
    - [Pros](#pros-3)
    - [Cons](#cons-3)
    - [Use Cases](#use-cases-3)
  - [Comparison Matrix](#comparison-matrix)
  - [Decision Framework](#decision-framework)
    - [Use Pattern 1 if:](#use-pattern-1-if)
    - [Use Pattern 2 if:](#use-pattern-2-if)
    - [Use Pattern 3 if:](#use-pattern-3-if)
    - [Use Pattern 4 if:](#use-pattern-4-if)
  - [Implementation Example](#implementation-example)
  - [See Also](#see-also)

______________________________________________________________________

## Overview

Both LlamaStash and llama-swap provide powerful local LLM management capabilities. The integration patterns below show how to combine them for different use cases.

| Pattern | Best For | Complexity |
|---------|----------|------------|
| **API-Level Proxy** | Unified API access, single entry point | Medium |
| **LlamaStash Primary** | Model management focus, LlamaStash UI | Low |
| **llama-swap Primary** | Multi-model deployments, Web UI focus | Medium |
| **Hybrid** | Maximum flexibility, advanced users | High |

______________________________________________________________________

## Pattern 1: API-Level Proxy

**Description:** llama-swap acts as a reverse proxy to LlamaStash's control plane or proxy endpoint.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   llama-swap (Port 8080)                │
│  ┌─────────────────────────────────────────────────────┐│
│  │  /v1/models → Forward to LlamaStash proxy           ││
│  │  /v1/chat/completions → Forward to LlamaStash       ││
│  │  /v1/embeddings → Forward to LlamaStash             ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                LlamaStash Daemon (Port 48134)           │
│         (Control Plane - JSON-RPC API)                  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                LlamaStash Proxy (Port 11435)            │
│         (OpenAI-compatible API)                         │
└─────────────────────────────────────────────────────────┘
```

### Configuration

**llama-swap config.yaml:**

```yaml
listen: 127.0.0.1:8080
models:
  - name: "llamastash-llm"
    url: "http://127.0.0.1:11435"
    prefix: "llamastash/"
    enabled: true
```

### Pros

- ✅ Single API endpoint for all operations
- ✅ Automatic model discovery via llama-swap
- ✅ Preserves LlamaStash model management
- ✅ Easy to add additional models later

### Cons

- ❌ llama-swap adds one hop (latency)
- ❌ Requires LlamaStash proxy running
- ❌ Limited to models LlamaStash manages

### Use Cases

- Unified API access from multiple clients
- Existing LlamaStash deployment
- Adding llama-swap Web UI to LlamaStash

______________________________________________________________________

## Pattern 2: LlamaStash as Primary, llama-swap as UI

**Description:** LlamaStash manages models and serves API; llama-swap provides Web UI and additional endpoints.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   llama-swap (Port 8080)                │
│  ┌─────────────────────────────────────────────────────┐│
│  │  /ui → Web playground (optional)                   ││
│  │  /logs/stream → Live logs                          ││
│  │  /metrics → Prometheus metrics                     ││
│  │  /health → Health check                            ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                LlamaStash Daemon (Port 48134)           │
└─────────────────────────────────────────────────────────┘
```

### Configuration

**llama-swap config.yaml:**

```yaml
listen: 127.0.0.1:8080
models:
  - name: "llamastash-llm"
    url: "http://127.0.0.1:11435"
    prefix: "llamastash/"
    enabled: true
```

### Pros

- ✅ LlamaStash handles model management
- ✅ llama-swap provides additional endpoints
- ✅ Simple setup
- ✅ Preserves LlamaStash's control plane

### Cons

- ❌ llama-swap doesn't manage models independently
- ❌ Limited to LlamaStash's model list

### Use Cases

- Want LlamaStash's model management
- Need llama-swap's Web UI and metrics
- Single-server deployment

______________________________________________________________________

## Pattern 3: llama-swap as Primary, LlamaStash as Model Manager

**Description:** llama-swap is the main API endpoint; LlamaStash manages model lifecycle.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   llama-swap (Port 8080)                │
│  ┌─────────────────────────────────────────────────────┐│
│  │  /v1/* → Direct model serving                       ││
│  │  /ui → Web playground                               ││
│  │  /logs/stream → Live logs                           ││
│  │  /metrics → Prometheus metrics                      ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                LlamaStash Daemon (Port 48134)           │
│         (Model lifecycle management only)               │
└─────────────────────────────────────────────────────────┘
```

### Configuration

**llama-swap config.yaml:**

```yaml
listen: 127.0.0.1:8080
models:
  - name: "qwen3.5-9b"
    url: "http://127.0.0.1:10001"
    prefix: "qwen3.5-9b/"
    enabled: true
  - name: "granite-4-h-tiny"
    url: "http://127.0.0.1:10002"
    prefix: "granite-4-h-tiny/"
    enabled: true
```

**LlamaStash config:**

```yaml
models:
  qwen3.5-9b:
    path: /home/waflores/.lmstudio/models/lmstudio-community/Qwen3.5-9B-GGUF/Qwen3.5-9B-Q4_K_M.gguf
    name: "Qwen3.5 9B"
    description: "Qwen3.5 9B with reasoning capabilities"
    ttl: 600
```

### Pros

- ✅ llama-swap is primary API endpoint
- ✅ Multiple models can be managed
- ✅ Full llama-swap feature set (logs, metrics, Web UI)
- ✅ LlamaStash handles model lifecycle

### Cons

- ❌ More complex setup
- ❌ Requires managing both systems
- ❌ Configuration synchronization needed

### Use Cases

- Multi-model deployments
- Want llama-swap's full feature set
- Need independent model management

______________________________________________________________________

## Pattern 4: Hybrid Architecture

**Description:** Both systems run independently with optional proxy chaining for specific use cases.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   llama-swap (Port 8080)                │
│  ┌─────────────────────────────────────────────────────┐│
│  │  /v1/* → llama-swap managed models                  ││
│  │  /proxy/* → Forward to LlamaStash                   ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                LlamaStash Daemon (Port 48134)           │
│         (Independent model management)                  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                LlamaStash Proxy (Port 11435)            │
│         (OpenAI-compatible API)                         │
└─────────────────────────────────────────────────────────┘
```

### Configuration

**llama-swap config.yaml:**

```yaml
listen: 127.0.0.1:8080
models:
  - name: "qwen3.5-9b"
    url: "http://127.0.0.1:10001"
    prefix: "qwen3.5-9b/"
    enabled: true
  - name: "llamastash-proxy"
    url: "http://127.0.0.1:11435"
    prefix: "llamastash-proxy/"
    enabled: true
```

### Pros

- ✅ Maximum flexibility
- ✅ Can use either system independently
- ✅ Can chain models across systems
- ✅ Best for advanced use cases

### Cons

- ❌ Most complex setup
- ❌ Requires careful configuration
- ❌ Higher maintenance overhead

### Use Cases

- Advanced deployment scenarios
- Need to use both systems' features
- Experimental or research use cases

______________________________________________________________________

## Comparison Matrix

| Feature | Pattern 1 | Pattern 2 | Pattern 3 | Pattern 4 |
|---------|-----------|-----------|-----------|-----------|
| **Single API Endpoint** | ✅ | ❌ | ✅ | ❌ |
| **Model Management** | LlamaStash | LlamaStash | llama-swap | Both |
| **Web UI** | llama-swap | llama-swap | llama-swap | llama-swap |
| **Prometheus Metrics** | llama-swap | llama-swap | llama-swap | llama-swap |
| **Log Streaming** | llama-swap | llama-swap | llama-swap | llama-swap |
| **Setup Complexity** | Medium | Low | Medium | High |
| **Maintenance** | Medium | Low | Medium | High |
| **Best For** | Unified API | LlamaStash focus | llama-swap focus | Advanced |

______________________________________________________________________

## Decision Framework

### Use Pattern 1 if:

- You want a single API endpoint
- You're already using LlamaStash
- You want to add llama-swap's Web UI

### Use Pattern 2 if:

- You primarily use LlamaStash
- You want llama-swap's additional endpoints
- You want minimal configuration changes

### Use Pattern 3 if:

- You want llama-swap as primary API
- You need multi-model deployments
- You want full llama-swap features

### Use Pattern 4 if:

- You need maximum flexibility
- You're comfortable with complex setups
- You want to use both systems' features

______________________________________________________________________

## Implementation Example

**Recommended for most users (Pattern 1):**

1. **Install llama-swap:**

   ```bash
   /home/waflores/.cargo/bin/llama-swap --config /home/waflores/DevFolder/ai/local-config/llamastash/llamastash-integration.yaml --listen 127.0.0.1:8080
   ```

1. **Verify integration:**

   ```bash
   curl http://127.0.0.1:8080/health
   curl http://127.0.0.1:8080/v1/models
   ```

1. **Access Web UI:**

   ```bash
   open http://127.0.0.1:8080/ui
   ```

______________________________________________________________________

## See Also

- [CONFIG-STRUCTURE.md](CONFIG-STRUCTURE.md) - Configuration hierarchy
- [API-SPECIFICATIONS.md](API-SPECIFICATIONS.md) - API endpoint documentation
- [INSTALL.md](INSTALL.md) - Installation guide
- [QUICK-START.md](QUICK-START.md) - Quick setup guide

______________________________________________________________________

*Last updated: 2025-01-17*
*Author: LlamaStash + llama-swap Integration Project*
*License: MIT*
