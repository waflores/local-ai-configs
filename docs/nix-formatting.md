# nix-formatting.md

How the Nix formatting infrastructure works and how to use it.

## Why this exists

The project uses [treefmt-nix](https://github.com/numtide/treefmt-nix) to pin the formatter
versions and wire them into the Nix flake. `nix fmt` is the single command that runs all
formatters (Ruff check + format, nixfmt, yamlfmt, etc.) and must pass before committing.

## Quick reference

```bash
nix fmt            # format all files
nix fmt --check    # verify formatting is clean (CI gate)
nix flake check    # run all flake checks
nix flake show     # show generated outputs (packages, devShells, formatter)
```

## Architecture

```
nix/
├── treefmt.nix     # treefmt-nix module: declares which formatters to enable
├── formatter.nix   # bridge: evaluates treefmt.nix and extracts the wrapped binary
flake.nix           # blueprint driver: wires nix/ into flake outputs (prefix = ./nix)
```

- `nix/treefmt.nix` is a **module**, not a flake. It accepts `{ pkgs, lib, ... }` because
  `formatter.nix` calls `inputs.treefmt.lib.evalModule pkgs ./treefmt.nix`.
- `nix/formatter.nix` evaluates the module and returns `config.build.wrapper` — the
  treefmt binary that reads `treefmt.toml` and runs the formatters.
- `flake.nix` restricts outputs to `x86_64-linux` only (no cross-compilation).

## Ruff configuration

All Python linting/formatting rules live in `pyproject.toml`:

```toml
[tool.ruff.lint]
select = ["B", "D3", "E", "F"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["PLW1510"]
```

- `ruff check` uses these rules via the flake's ruff formatter.
- `ruff format` applies the same rules (the formatter's bundled ruff reads
  `pyproject.toml`).

## Common gotchas

| Issue | Cause | Fix |
|-------|-------|-----|
| `module ... does not look like a module` | Wrong signature (`_: { ... }`) | Use `{ pkgs, lib, ... }:` |
| `programs.ruff-format.command` does not exist | `command` conflicts with auto-derived `command` from `package` | Use `package = pkgs.ruff` |

## When to edit

- Add a new formatter or change an include glob in `nix/treefmt.nix`.
- Change a Ruff rule in `pyproject.toml`.
- Both require re-running `nix fmt` and `nix flake check` to verify.
