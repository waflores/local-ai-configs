# nix Formatting Infrastructure

## Overview

This directory (`nix/`) contains the Nix configuration for the **treefmt-nix**
formatting infrastructure. It defines how `nix fmt` discovers, runs, and applies
formatters across the project.

## Files

| File | Role |
|------|------|
| `nix/treefmt.nix` | The **treefmt-nix module** — declares which formatters to enable and their options |
| `nix/formatter.nix` | The **bridge** — evaluates `treefmt.nix` and extracts the wrapped `treefmt` binary |
| `flake.nix` | The **blueprint driver** — wires treefmt-nix into the flake outputs |

## `nix/treefmt.nix` — the module

This file is a **treefmt-nix module**, not a flake. It uses the raw submodule
signature `{ pkgs, lib, ... }:` because `nix/formatter.nix` calls
`inputs.treefmt.lib.evalModule pkgs ./treefmt.nix`.

### What it declares

- `projectRootFile = "flake.nix"` — the file treefmt uses to find the project root
- `programs.<name>.enable = true` — switches each formatter on
- `programs.ruff-format.package = pkgs.ruff` — the binary to invoke
- `programs.ruff-format.includes` — file globs the formatter applies to

### Key design points

- **`package`, not `command`**: the treefmt-nix ruff-format module derives
  `command` from `package` automatically. Specifying `command = pkgs.ruff`
  conflicts with the generated schema (the `command` option doesn't exist in
  the formatter's options).
- **`{ pkgs, lib, ... }` signature**: the module must accept `pkgs` because
  `evalModule` passes it. The original `_: { ... }` attrset signature was the
  cause of the `module does not look like a module` error.

## `nix/formatter.nix` — the bridge

```nix
{ inputs, pkgs, ... }:
let
  treefmtEval = inputs.treefmt.lib.evalModule pkgs ./treefmt.nix;
in
treefmtEval.config.build.wrapper
```

1. Evaluate the project's `treefmt.nix` module against the treefmt-nix library
1. Extract `config.build.wrapper` — the wrapped `treefmt` binary that reads
   `treefmt.toml` and invokes the formatters

This file is imported by `blueprint` and becomes the `formatter` output that
`nix fmt` uses.

## `flake.nix` — the driver

- Declares inputs: `nixpkgs`, `blueprint`, `treefmt`, `git-hooks`
- Passes them all to `inputs.blueprint { inherit inputs; prefix = "nix"; }`
- Blueprint generates the flake outputs, including `formatter` (from
  `nix/formatter.nix`), `checks`, `packages`, and `devShells`

`nix fmt` resolves to the treefmt-nix wrapper, which reads the generated
`treefmt.toml` and runs the formatters declared in `nix/treefmt.nix`.

## Running

```bash
# Format all files
nix fmt

# Re-run to confirm idempotency (should show "0 files (0 changed)")
nix fmt
```

## Ruff configuration

`pyproject.toml` centralizes Ruff rules that `ruff check` and `ruff format`
share:

```toml
[tool.ruff]
select = ["B", "D3", "E", "F"]
ignore = ["E501"]

[tool.ruff.per-file-ignores]
"tests/*" = ["PLW1510"]
```

- `ruff check` uses these rules via the flake's `ruff.enable` formatter
- `ruff format` uses the same rules (the formatter's bundled ruff applies
  the project's config from `pyproject.toml`)

## Verification

After a change:

```bash
nix fmt            # exit 0, formats files
nix fmt            # exit 0, 0 files changed (idempotent)
ruff format --check  # clean
```

## Known gotchas

| Issue | Cause | Fix |
|-------|-------|-----|
| `module ... does not look like a module` | Wrong signature (`_: { ... }` instead of `{ pkgs, lib, ... }:`) | Use `{ pkgs, lib, ... }` |
| `programs.ruff-format.command` does not exist | `command` conflicts with auto-derived `command` from `package` | Use `package = pkgs.ruff` |
