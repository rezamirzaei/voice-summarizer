#!/usr/bin/env bash
set -euo pipefail

MODEL_NAME="${1:-llama3}"

if ! command -v ollama >/dev/null 2>&1; then
  echo "ollama command is required on the host machine."
  exit 1
fi

echo "Pulling model: ${MODEL_NAME}"
ollama pull "${MODEL_NAME}"
echo "Model is ready."
