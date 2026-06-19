#!/bin/bash
# llama-bench: Comprehensive benchmark runner for all models in llama-swap
# Collates results into a single report

set -euo pipefail

# Configuration
CONFIG_FILE="${CONFIG_FILE:-/home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml}"
MODEL_ROOT="/home/waflores/.lmstudio/models"
LOG_DIR="logs/benchmark"
RESULTS_FILE="${LOG_DIR}/benchmark-results.md"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Create log directory
mkdir -p "${LOG_DIR}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  llama-swap Benchmark Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Config: ${CONFIG_FILE}${NC}"
echo -e "${BLUE}Model Root: ${MODEL_ROOT}${NC}"
echo -e "${BLUE}Timestamp: ${TIMESTAMP}${NC}"
echo -e "${BLUE}========================================${NC}"

# Extract model names from config using array to avoid word splitting issues
echo -e "\n${YELLOW}Extracting models from config...${NC}"
MODELS=()
while IFS= read -r line; do
  MODELS+=("${line}")
done < <(grep -E "^  [A-Za-z0-9_-]+:" "${CONFIG_FILE}" | sed 's/^  //' | grep -v "^models_directory:" | grep -v "^cmdPrefix:" | grep -v "^device:" | grep -v "^threads:" | grep -v "^nGpuLayers:" | grep -v "^flashAttn:" | grep -v "^ctxSize:" | grep -v "^nPredict:" | grep -v "^cacheRamSpillover:" | grep -v "^reasoning:" | grep -v "^reasoningBudget:" | grep -v "^reasoningFormat:" | grep -v "^jinja:" | grep -v "^tools:" | grep -v "^contextShift:" | grep -v "^swappable:" | grep -v "^disabled:" | grep -v "^every:" | grep -v "^models:")

echo -e "${GREEN}Found ${#MODELS[@]} models to benchmark:${NC}"
printf '%s\n' "${MODELS[@]}"

# Function to test a single model
test_model() {
  local model_name="$1"
  local model_path
  model_path="${MODEL_ROOT}/${model_name}"

  echo -e "\n${YELLOW}----------------------------------------${NC}"
  echo -e "${YELLOW}Testing: ${model_name}${NC}"
  echo -e "${YELLOW}Path: ${model_path}${NC}"

  # Check if model path exists
  if [[ ! -d ${model_path} ]]; then
    echo -e "${RED}❌ Model directory not found: ${model_path}${NC}"
    echo -e "${YELLOW}  Skipping (model not downloaded yet)${NC}"
    return 1
  fi

  # List available GGUF files
  echo -e "${YELLOW}Available GGUF files:${NC}"
  ls -la "${model_path}"/*.gguf 2>/dev/null || echo "  No .gguf files found"

  # Extract model info from llama-swap config
  model_config=$(awk -v model="${model_name}" '
        $0 ~ "^  " model ":[[:space:]]*$" {found=1; next}
        found && /^  [A-Za-z0-9_-]+:$/ {exit}
        found {print}
    ' "${CONFIG_FILE}")

  # Extract key parameters
  model_name_display=$(echo "${model_config}" | grep -A 5 "^[[:space:]]*name:" | grep "name:" | head -1 | sed 's/.*name:[[:space:]]*//' | tr -d '"')
  ttl=$(echo "${model_config}" | grep "^    ttl:" | sed 's/.*ttl:[[:space:]]*//' | tr -d '"')
  ctx_size=$(echo "${model_config}" | grep "^    macros:" -A 10 | grep "ctxSize:" | sed 's/.*ctxSize:[[:space:]]*//' | tr -d '"')

  echo -e "${GREEN}✓ Model info:${NC}"
  echo -e "  Display Name: ${model_name_display:-${model_name}}"
  echo -e "  TTL: ${ttl:-600}s"
  echo -e "  Context Size: ${ctx_size:-262144}"

  # Run benchmark test
  echo -e "${YELLOW}  Running load test...${NC}"
  test_output=$(mktemp)

  # Create a simple test prompt
  local test_prompt="What is the capital of France? Keep your answer concise."

  # Start the model server in background
  echo -e "${YELLOW}  Starting llama-server...${NC}"
  local server_port=$((10000 + RANDOM % 100))
  cmd=$(echo "${model_config}" | grep "^    cmd:" | sed 's/^    cmd:[[:space:]]*//' | tr -d '"')

  # Replace PORT placeholder
  cmd="${cmd//\${PORT/}/${server_port}/}"

  # Start server
  echo "${cmd}" >"${test_output}" &
  local server_pid=$!
  echo -e "  Server PID: ${server_pid}"
  echo -e "  Server port: ${server_port}"

  # Wait for server to start
  sleep 3

  # Test the model
  local test_url="http://localhost:${server_port}/v1/chat/completions"
  test_payload=$(
    cat <<EOF
{
  "model": "test",
  "messages": [
    {
      "role": "user",
      "content": "${test_prompt}"
    }
  ],
  "max_tokens": 100,
  "temperature": 0.7
}
EOF
  )

  echo -e "${YELLOW}  Sending test request...${NC}"
  response=$(curl -s -w "\n%{http_code}" -X POST "${test_url}" \
    -H "Content-Type: application/json" \
    -d "${test_payload}" 2>&1)

  http_code=$(echo "${response}" | tail -1)
  response_body=$(echo "${response}" | head -n -1)

  # Stop server
  kill "${server_pid}" 2>/dev/null || true
  wait "${server_pid}" 2>/dev/null || true

  # Record results - persist ${test_output} for inspection
  if [[ ${http_code} == "200" ]]; then
    echo -e "${GREEN}✓ Test successful!${NC}"
    echo "${response_body}" >>"${test_output}"
    echo -e "${YELLOW}  Response preview:${NC}"
    echo "${response_body}" | head -5 | sed 's/^/    /'
    echo -e "${YELLOW}  Full response saved to: ${test_output}${NC}"
    return 0
  else
    echo -e "${RED}✗ Test failed (HTTP ${http_code})${NC}"
    echo "${response_body}" >>"${test_output}"
    echo -e "${YELLOW}  Error output saved to: ${test_output}${NC}"
    return 1
  fi
}

# Function to run all benchmarks
run_all_benchmarks() {
  local passed=0
  local failed=0
  local skipped=0

  echo -e "\n${YELLOW}========================================${NC}"
  echo -e "${YELLOW}  Running Benchmarks${NC}"
  echo -e "${YELLOW}========================================${NC}"

  for model in "${MODELS[@]}"; do
    if test_model "${model}"; then
      ((passed++)) || true
    else
      ((failed++)) || true
    fi
  done

  # Generate report
  echo -e "\n${YELLOW}========================================${NC}"
  echo -e "${YELLOW}  Generating Report${NC}"
  echo -e "${YELLOW}========================================${NC}"

  {
    echo "# llama-swap Benchmark Results"
    echo ""
    echo "## Overview"
    echo ""
    echo "| Metric | Value |"
    echo "|--------|-------|"
    echo "| Timestamp | ${TIMESTAMP} |"
    echo "| Config File | ${CONFIG_FILE} |"
    echo "| Model Root | ${MODEL_ROOT} |"
    echo "| Total Models | ${#MODELS[@]} |"
    echo "| Passed | ${passed} |"
    echo "| Failed | ${failed} |"
    echo "| Skipped | ${skipped} |"
    echo ""
    echo "## Individual Results"
    echo ""

    for model in "${MODELS[@]}"; do
      echo "### ${model}"
      echo ""
      test_model "${model}" || true
      echo ""
      echo "---"
      echo ""
    done
  } >"${RESULTS_FILE}"

  echo -e "Results saved to: ${RESULTS_FILE}"
  echo -e "\n${GREEN}========================================${NC}"
  echo -e "${GREEN}  Summary:${NC}"
  echo -e "  Total: ${#MODELS[@]} | Passed: ${passed} | Failed: ${failed} | Skipped: ${skipped}"
  echo -e "${GREEN}========================================${NC}"
}

# Run benchmarks
run_all_benchmarks
