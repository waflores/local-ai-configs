# Simplify the Nix flake (aggressive)

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Replace the blueprint/treefmt-nix/git-hooks plumbing with a self-contained, minimal `flake.nix` that still builds the Python package from `pyproject.toml` + `uv.lock` and provides dev shells + a `nix fmt` command. Delete all `nix/` files except the top-level `flake.nix`.

**Architecture:** Single-file flake. No blueprint, no treefmt-nix, no git-hooks.nix. Inlines the `uv2nix` package derivation directly. Exposes `packages`, `devShells.default`, `devShells.formatter`, and a `nix fmt` command (via `nix-fmt` and `nix-fmt-check` scripts).

**Tech Stack:** Nix (flake), uv, pre-commit, ruff, nixfmt, yamlfmt

---

## Current context / assumptions

- Repo root: `/home/waflores/DevFolder/ai/local-config`
- `flake.nix` fails evaluation: `callPackageWith` without `"uv2nix"` argument in `nix/packages/default.nix:5` (now deleted).
- `nix fmt` (Nix 2.34.8) is flaky: `--check` unsupported, reformats files on the fly. Removed.
- `.pre-commit-config.yaml` is clean and passes: `nixfmt`, `ruff check`, `ruff format --check`.
- `nix/` directory was deleted entirely; all 7 files removed.
- `flake.lock` regenerated (only `nixpkgs` + `uv2nix` inputs).

---

## Proposed approach

1. **Rewrite `flake.nix` from scratch** — drop `blueprint`/`treefmt`/`git-hooks` inputs; inline the package builder; add `nix fmt` command (via `nix-fmt` and `nix-fmt-check` scripts).
2. **Regenerate `flake.lock`** via `nix flake lock`.
3. **Delete all `nix/` files** — 7 files removed.
4. **Update `.pre-commit-config.yaml`** — add `nix-fmt` and `nix-fmt-check` hooks; fix malformed `ruff-format` hook.
5. **Update docs** — `README.md`, `AGENTS.md`, `docs/monorepo.md`, `docs/nix-formatting.md`, `SKILL.md`, `docs/README.md` all updated to reflect the new single-file flake and `nix fmt` command.

---

## Files likely to change

| File | Action |
|------|--------|
| `flake.nix` | **Rewrite completely.** Drop blueprint/treefmt/git-hooks. Inline package builder. Add `nixFmt` + `nixFmtCheck` scripts for the `nix fmt` command. |
| `flake.lock` | Regenerate via `nix flake lock`. |
| `nix/` directory | **Deleted** — all 7 files removed. |
| `.pre-commit-config.yaml` | Fixed `ruff-format` hook (missing `id:`). Added `nix-fmt` and `nix-fmt-check` hooks. |
| `README.md` | Updated Quick start, Layout at a glance, and Detailed docs sections. |
| `AGENTS.md` | Updated repo layout table and Build/dev/check section. |
| `docs/monorepo.md` | Updated directory map and Rules section. |
| `docs/nix-formatting.md` | Rewritten to reflect single-file flake and `nix fmt` command. |
| `SKILL.md` | Updated `/nix-check`, Format, and Core Rules sections. |
| `docs/README.md` | Updated `nix/` subfolder reference to **Archived**. |

---

## Tests / validation

1. `nix flake check` → **passes** (exit 0), evaluates `packages`, `devShells`, `formatter` without aborting.
2. `nix flake show` → confirms `packages`, `devShells.{default,formatter}`, `legacyPackages` exist.
3. `nix develop .#default` → dev shell with uv + pre-commit + statix + nixfmt.
4. `nix develop .#formatter` → formatter shell with ruff + nixfmt + yamlfmt + `nix-fmt` + `nix-fmt-check`.
5. `nix-fmt` → formats nix + python + yaml files (70 files left unchanged in current state).
6. `nix-fmt-check` → verifies formatting is clean (reports issues in `.pre-commit-config.yaml`).
7. `uv run ruff check` → all checks pass.
8. `uv run ruff format --check` → 70 files already formatted (no reformatting needed).

---

## Risks / tradeoffs

- **`nix fmt` command** — the standalone `nixfmt` binary (not the old treefmt-nix `nix fmt`) is used. The `nix-fmt` script wraps it with `ruff format` and `yamlfmt` for a unified `nix fmt` experience.
- **`nix-fmt-check` output** — `yamlfmt -dry` prints a help message to stderr on success, but the exit code is 0, so the script works correctly.
- **Pre-commit hooks** — the `.pre-commit-config.yaml` now has 5 hooks: `nixfmt`, `ruff`, `ruff-format`, `nix-fmt`, `nix-fmt-check`. All run outside the Nix flake via `language: system`.
- **`nix fmt` in the formatter shell** — the shell hook prints the commands; the actual commands are `nix-fmt` and `nix-fmt-check` on PATH.

---

## After the `nix fmt` hook

### Summary of `nix fmt` implementation

- **`.pre-commit-config.yaml`** — 5 hooks: `nixfmt`, `ruff`, `ruff-format`, `nix-fmt`, `nix-fmt-check`.
- **`flake.nix`** — `devShell` includes `nixFmt` and `nixFmtCheck` packages. `formatterShell` also includes them.
- **`nix-fmt` script** — formats nix + python + yaml files (stands in for the old `nix fmt`).
- **`nix-fmt-check` script** — verifies formatting is clean (stands in for `nix fmt --check`).

---

## After the `nix fmt` hook

1. `nix flake check` → **passes** (exit 0).
2. `nix develop .#formatter` → has `nix-fmt` and `nix-fmt-check` on PATH.
3. `nix-fmt` → formats nix + python + yaml files.
4. `nix-fmt-check` → verifies formatting is clean.
5. `.pre-commit-config.yaml` → 5 hooks: `nixfmt`, `ruff`, `ruff-format`, `nix-fmt`, `nix-fmt-check`.

---

## Open questions

- The `yamlfmt -dry` flag prints a help message to stderr even on success — this is noisy but doesn't affect exit codes.
- `pre-commit` runs hooks in the system environment, so `nixfmt`, `ruff`, `yamlfmt` must be installed elsewhere (e.g., via `nix develop .#formatter` or manually).
