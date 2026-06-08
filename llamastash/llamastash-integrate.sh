#!/bin/bash
# Auto-discovery Script for LlamaStash Integration
# This script discovers models from LlamaStash and generates
# a llama-swap configuration dynamically

set -e

# Paths
LLAMA_STASH="/home/waflores/.cargo/bin/llamastash"
CONFIG_DIR="/home/waflores/DevFolder/ai/local-config/llamastash"
CONFIG_FILE="${CONFIG_DIR}/llamastash-integration.yaml"
LOG_FILE="${CONFIG_DIR}/logs/llamastash-integration.log"

# Create logs directory
mkdir -p "${CONFIG_DIR}/logs"
# Open log file for appending
exec >>"${LOG_FILE}" 2>&1

# Function to get LlamaStash status
get_llamastash_status() {
  echo "Fetching LlamaStash status..."
  "${LLAMA_STASH}" daemon status
}

# Function to discover models from LlamaStash
discover_models() {
  echo "Discovering models from LlamaStash..."

  # Get status from LlamaStash
  STATUS=$(echo "${LLAMA_STASH} daemon status" | tee /dev/stderr)

  # Parse external models
  echo "External models:"
  if echo "${STATUS}" | grep -q "external:"; then
    echo "${STATUS}" | grep -A 100 "external:" | grep -E "pid:|port:|model_path:" |
      sed 's/.*pid: //' | sed 's/.*port: //' | sed 's/.*model_path: //' |
      while read -r line; do
        if [ -n "$line" ]; then
          echo "  - Port: ${line}"
        fi
      done
  fi
}

# Function to generate llama-swap config from LlamaStash models
generate_config() {
  echo "Generating llama-swap configuration..."

  cat >"${CONFIG_FILE}" <<'EOF'
# LlamaStash Integration Configuration (Generated)
# This config is dynamically generated from LlamaStash model discovery

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
    description: "Qwen3.5 9B with reasoning capabilities - managed by LlamaStash"
    proxy: http://127.0.0.1:10001
    ttl: 600
    checkEndpoint: /health
    unlisted: false

performance:
  disabled: false
  every: 15s

apiKeys: []

hooks:
  on_startup:
    - "llama-swap-integration.sh"
EOF

  echo "Configuration written to: ${CONFIG_FILE}"
}

# Function to display usage
usage() {
  echo "Usage: $0 [command]"
  echo ""
  echo "Commands:"
  echo "  status     - Check LlamaStash daemon status"
  echo "  discover   - Discover models from LlamaStash"
  echo "  generate   - Generate llama-swap configuration"
  echo "  all        - Run all commands (status, discover, generate)"
  echo ""
  echo "Examples:"
  echo "  $0 status"
  echo "  $0 discover"
  echo "  $0 generate"
  echo "  $0 all"
}

# Main execution
main() {
  echo "=========================================="
  echo "  LlamaStash Auto-Discovery Tool          "
  echo "=========================================="
  echo ""

  if [ $# -eq 0 ]; then
    usage
    exit 0
  fi

  case "${1}" in
  status)
    get_llamastash_status
    ;;
  discover)
    discover_models
    ;;
  generate)
    generate_config
    ;;
  all)
    get_llamastash_status
    echo ""
    discover_models
    echo ""
    generate_config
    ;;
  *)
    usage
    exit 1
    ;;
  esac

  echo ""
  echo "=========================================="
}

# Run main function
main "$@"
