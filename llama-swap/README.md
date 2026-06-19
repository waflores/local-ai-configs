# llama-swap

## Purpose

llama-swap is a model management tool that allows you to load and unload large language models (LLMs) dynamically. It uses `llama-server` for inference and supports multiple GPU backends (CUDA, Vulkan).

## Core Stack

- `llama-server`: Inference engine
- `llama-swap`: Model management tool

## Authority

This project uses the `.continue` folder to define AI agent behavior. Agents should consult `.continue/agents/` for project-specific instructions.

## Getting Started

1. Start `llama-server` with `./inferhost/bin/llama-server --config /home/waflores/DevFolder/ai/local-config/inferhost/config.yaml`
1. Start `llama-swap` with `./inferhost/bin/llama-swap --config /home/waflores/DevFolder/ai/local-config/inferhost/config.yaml`
1. Use `cn` to chat with models.
