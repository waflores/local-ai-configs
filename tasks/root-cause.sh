#!/usr/bin/env bash
# Root-cause: inspect what pkgs.uv in nixpkgs actually is.
set -u
cd "$(dirname "$0")/.." || exit 1

echo "=== nixpkgs rev ==="
python3 - <<'PY'
import json
d = json.load(open("flake.lock"))
print(d["nodes"]["nixpkgs"]["locked"]["rev"])
PY

echo "=== pkgs.uv type in nixpkgs ==="
nix-instantiate --eval --raw --expr '
  with import (builtins.fetchTarball "github:NixOS/nixpkgs/6510408d147d8c5e6d76043e899e9251756f6a75") { };
  let u = pkgs.uv;
  in builtins.typeOf u
' 2>&1 | tail -8

echo "=== uv-0.13.4 drv (linked in failing pyproject-hooks drv) ==="
nix log /nix/store/j99d3cz8m58bz6bf7fpfq8rjcqjcvnmp-uv-0.13.4.drv 2>&1 | head -10

echo "=== python3.14-uv-0.11.26 drv (the uv Python package) ==="
nix log /nix/store/1gkgk630g1syvsa7n6n5fbjixnbyrm8d-python3.14-uv-0.11.26.drv 2>&1 | head -10

echo "=== python3.14-uv-build-0.11.28 drv (the uv_build module) ==="
nix log /nix/store/3mqq7zymmmsbs31gxb4vxfhk9lr5sqa6-python3.14-uv-build-0.11.28.drv 2>&1 | head -10
