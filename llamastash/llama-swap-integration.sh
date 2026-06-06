#!/bin/bash
# LlamaStash Integration Script for llama-swap
# This script starts llama-swap with integration configuration
# and verifies LlamaStash daemon is running

set -e

# Paths
LLAMA_SWAP="/home/waflores/.cargo/bin/llama-swap"
CONFIG_DIR="/home/waflores/DevFolder/ai/local-config/llamastash"
CONFIG_FILE="${CONFIG_DIR}/llamastash-integration.yaml"
LOG_FILE="${CONFIG_DIR}/logs/llama-swap-integration.log"

# Create logs directory
mkdir -p "${CONFIG_DIR}/logs"

# Function to check LlamaStash daemon status
check_llamastash() {
    echo "Checking LlamaStash daemon status..."
    if ! pgrep -x "llamastash" > /dev/null; then
        echo "LlamaStash daemon not running. Starting..."
        /home/waflores/.cargo/bin/llamastash daemon start --listen 127.0.0.1:48134
    else
        echo "LlamaStash daemon already running"
    fi
    
    # Wait for LlamaStash to be ready
    sleep 2
    
    # Verify LlamaStash is responsive
    if curl -s http://127.0.0.1:48134/status > /dev/null 2>&1; then
        echo "✓ LlamaStash daemon is responsive"
    else
        echo "✗ LlamaStash daemon is not responsive"
        return 1
    fi
}

# Function to verify external model is running
check_external_model() {
    echo "Checking external model status on port 10001..."
    if curl -s http://127.0.0.1:10001/health > /dev/null 2>&1; then
        echo "✓ External model (Qwen3.5-9B) is running on port 10001"
    else
        echo "⚠ External model not responding on port 10001"
        echo "  This is expected if the model was started externally"
    fi
}

# Function to start llama-swap with integration config
start_llama_swap() {
    echo "Starting llama-swap with LlamaStash integration..."
    echo "  Config: ${CONFIG_FILE}"
    echo "  Port: 8080"
    echo "  Listen: 127.0.0.1"
    
    "${LLAMA_SWAP}" \
        --config "${CONFIG_FILE}" \
        --listen 127.0.0.1:8080 \
        --log-file "${LOG_FILE}" \
        --log-level info \
        2>&1 | tee "${LOG_FILE}"
}

# Main execution
main() {
    echo "=========================================="
    echo "  LlamaStash + llama-swap Integration    "
    echo "=========================================="
    echo ""
    
    echo "Step 1: Checking LlamaStash daemon..."
    check_llamastash
    echo ""
    
    echo "Step 2: Checking external model status..."
    check_external_model
    echo ""
    
    echo "Step 3: Starting llama-swap integration..."
    start_llama_swap
    echo ""
    
    echo "=========================================="
    echo "  Integration Started Successfully        "
    echo "=========================================="
    echo ""
    echo "Access points:"
    echo "  Web UI:     http://localhost:8080/ui"
    echo "  Health:     http://localhost:8080/health"
    echo "  Models:     http://localhost:8080/v1/models"
    echo "  Logs:       ${LOG_FILE}"
    echo "  Metrics:    http://localhost:8080/metrics"
    echo "=========================================="
}

# Run main function
main "$@"