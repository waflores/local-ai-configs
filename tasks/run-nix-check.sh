#!/usr/bin/env bash
# Reproduce / verify the `nix flake check` failure deterministically.
set -u
cd "$(dirname "$0")/.." || exit 1

echo "=== nix flake check (exit code = expected failure) ==="
nix flake check
rc=$?
echo "=== nix flake check exit code: $rc (1 = failure expected) ==="
exit $rc
