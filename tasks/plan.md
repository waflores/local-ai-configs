# Implementation Plan: Integrate uv2nix for dependency management

## Overview

Integrate `uv2nix` (from https://github.com/pyproject-nix/uv2nix) into the local-config flake to manage Python dependencies. `uv2nix` is a tool that figures out whether it's simpler to integrate a Python project into the Nix system or try to fiddle with the vanilla configuration. The previous attempt (commit 064d303) was removed because it didn't fix `nix flake check`.

## Architecture Decisions

- **Use uv2nix as a flake input**: Add `uv2nix` to the flake inputs in `flake.nix`
- **Create a uv2nix builder**: Add `nix/uv2nix.nix` to handle the uv2nix integration
- **Replace current pyproject.nix approach**: The uv2nix builder will handle the Python package build differently than the current `buildPythonPackage` approach
- **Keep existing packages**: The `nix/packages/default.nix` will be updated to use the uv2nix output

## Dependency Graph

```
flake.nix (uv2nix input)
    │
    └── nix/uv2nix.nix (uv2nix builder)
            │
            └── nix/packages/default.nix (uses uv2nix output)
```

## Task List

### Phase 1: Setup uv2nix

- [ ] Task 1: Add `uv2nix` as a flake input in `flake.nix`
  - [ ] Verify: `nix flake show` includes uv2nix in inputs

- [ ] Task 2: Create `nix/uv2nix.nix` builder
  - [ ] Read uv2nix documentation to understand the API
  - [ ] Create a builder that calls uv2nix on the project's pyproject.toml
  - [ ] Verify: The builder produces a valid Nix derivation

### Phase 2: Update package output

- [ ] Task 3: Update `nix/packages/default.nix` to use uv2nix output
  - [ ] Replace `import ../pyproject.nix` with uv2nix output
  - [ ] Verify: `nix build .#packages.x86_64-linux.default` succeeds

- [ ] Task 4: Remove or update `nix/pyproject.nix` (no longer needed if uv2nix handles it)
  - [ ] Verify: No references to old pyproject.nix remain

### Phase 3: Verify and test

- [ ] Task 5: Run `nix flake check` to ensure all hooks pass
  - [ ] Verify: `nix flake check` exits 0

- [ ] Task 6: Verify `nix develop` works and provides expected tools
  - [ ] Verify: `nix develop` starts and `uv`, `pre-commit`, `statix` are on PATH

### Phase 4: Documentation and cleanup

- [ ] Task 7: Update `README.md` to mention uv2nix integration
  - [ ] Document the new build approach

- [ ] Task 8: Commit all changes
  - [ ] Verify: All modified files are committed

## Checkpoints

- [ ] After Task 2: uv2nix builder exists and is syntactically correct
- [ ] After Task 5: `nix flake check` passes
- [ ] After Task 6: `nix develop` works correctly
- [ ] After Task 8: All changes committed and pushed

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| uv2nix may not handle the project's build-system correctly | High | Test with `nix flake check` early; fall back to current approach if needed |
| uv2nix output may not match expected package structure | Medium | Read uv2nix documentation carefully; adjust builder as needed |
| Existing tools (uv, pre-commit) may not be available in uv2nix output | Medium | Check uv2nix output for available tools; add missing tools to buildInputs |
| Breaking changes to existing build pipeline | High | Test incrementally; keep old approach as fallback |

## Open Questions

- Should we keep `nix/pyproject.nix` as a reference implementation, or remove it entirely?
- Do we need to handle the `pre-commit-run` derivation differently with uv2nix?
- Should uv2nix be used for all Python packages in the flake, or just this one?

## Files likely touched

- `flake.nix` - Add uv2nix input
- `nix/uv2nix.nix` - New file: uv2nix builder
- `nix/packages/default.nix` - Update to use uv2nix output
- `nix/pyproject.nix` - May be removed or kept as reference
- `README.md` - Document the change

## Estimated scope

Medium: 3-5 files
