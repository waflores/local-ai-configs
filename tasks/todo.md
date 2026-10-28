# Task List: uv2nix Integration

## Task 1: Add uv2nix as a flake input in flake.nix

**Description:** Add `uv2nix` (https://github.com/pyproject-nix/uv2nix) as a new flake input to the project.

**Acceptance criteria:**
- [x] `flake.nix` includes uv2nix in the inputs section
- [x] `nix flake show` includes uv2nix in the output

**Verification:**
- [x] Run `nix flake show` and verify uv2nix is listed
- [x] Run `nix flake check` and verify it passes

**Dependencies:** None

**Files likely touched:**
- `flake.nix`

**Estimated scope:** Small: 1-2 files

**Progress:** ✓ Complete

---

## Task 2: Create nix/uv2nix.nix builder

**Description:** Create a new Nix builder that uses uv2nix to convert the project's `pyproject.toml` into a Nix derivation.

**Acceptance criteria:**
- [x] `nix/uv2nix.nix` file exists with valid Nix syntax
- [x] The builder calls uv2nix on the project directory
- [x] The builder outputs a package derivation

**Verification:**
- [x] Run `nix eval '.#packages.x86_64-linux.default'` and verify it produces a derivation path
- [x] Check that the derivation has a valid `out` attribute

**Dependencies:** Task 1

**Files likely touched:**
- `nix/uv2nix.nix` (new file)

**Estimated scope:** Small: 1-2 files

**Progress:** ✓ Complete - The builder produces a valid derivation

---

## Task 3: Update nix/packages/default.nix to use uv2nix output

**Description:** Modify the package output to use the uv2nix builder instead of the current `pyproject.nix` approach.

**Acceptance criteria:**
- [x] `nix/packages/default.nix` imports from `nix/uv2nix.nix` instead of `nix/pyproject.nix`
- [x] The package output is correctly exposed through the flake
- [x] No references to the old `import ../pyproject.nix` remain

**Verification:**
- [x] Run `nix build .#packages.x86_64-linux.default` and verify it succeeds
- [ ] Check that the built package has the expected attributes

**Dependencies:** Task 2

**Files likely touched:**
- `nix/packages/default.nix`

**Estimated scope:** Small: 1-2 files

**Progress:** ○ In progress - The file was updated but needs to be tested with the correct flake.nix

---

## Task 4: Update or remove nix/pyproject.nix

**Description:** Decide whether to keep `nix/pyproject.nix` as a reference implementation or remove it entirely.

**Acceptance criteria:**
- [ ] If kept: It's documented as a reference implementation
- [ ] If removed: No broken references remain
- [ ] The flake builds correctly either way

**Verification:**
- [ ] Run `nix flake check` to ensure no broken references
- [ ] Verify `nix develop` works correctly

**Dependencies:** Task 3

**Files likely touched:**
- `nix/pyproject.nix` (may be removed)

**Estimated scope:** Small: 1 file

**Progress:** ○ Not started

---

## Task 5: Verify nix flake check passes

**Description:** Ensure that `nix flake check` passes with the new uv2nix integration.

**Acceptance criteria:**
- [ ] `nix flake check` exits 0
- [ ] No pre-commit hooks fail
- [ ] All pre-commit checks pass

**Verification:**
- [ ] Run `nix flake check` and capture the output
- [ ] Run `pre-commit run --all-files` to verify hooks work

**Dependencies:** Task 3, Task 4

**Files likely touched:** None (verification only)

**Estimated scope:** Small: verification only

**Progress:** ○ Not started

---

## Task 6: Verify nix develop works correctly

**Description:** Ensure that `nix develop` starts correctly and provides the expected tools.

**Acceptance criteria:**
- [ ] `nix develop` starts without errors
- [ ] `uv` is available on PATH
- [ ] `pre-commit` is available on PATH
- [ ] `statix` is available on PATH
- [ ] Running `uv run python -m llm_manager.webapp` works

**Verification:**
- [ ] Start `nix develop` and verify tools are available
- [ ] Test that the Python package can be imported

**Dependencies:** Task 5

**Files likely touched:** None (verification only)

**Estimated scope:** Small: verification only

**Progress:** ○ Not started

---

## Task 7: Update README.md to document uv2nix integration

**Description:** Update the documentation to mention the uv2nix integration and how it works.

**Acceptance criteria:**
- [ ] README.md mentions uv2nix in the stack
- [ ] Build commands are still documented correctly
- [ ] Any relevant architecture decisions are documented

**Verification:**
- [ ] Review the updated README for clarity
- [ ] Verify all build commands still work

**Dependencies:** Task 6

**Files likely touched:**
- `README.md`

**Estimated scope:** Small: 1-2 files

**Progress:** ○ Not started

---

## Task 8: Commit and push changes

**Description:** Commit all changes to the repository and push to the remote.

**Acceptance criteria:**
- [ ] All modified files are committed
- [ ] Commit message follows conventional commits format
- [ ] Changes are pushed to the remote repository

**Verification:**
- [ ] Run `git status` to verify working tree is clean
- [ ] Run `git log --oneline` to see the new commit
- [ ] Verify the commit is on the remote

**Dependencies:** Task 7

**Files likely touched:** Git history

**Estimated scope:** Small: commit operation

**Progress:** ○ Not started

---

## Checkpoint: After Tasks 1-3

- [x] uv2nix is integrated into flake.nix
- [x] nix/uv2nix.nix builder exists and works
- [x] nix/packages/default.nix uses uv2nix output
- [ ] nix flake check passes (needs to be tested with correct packages output)
- [ ] Review with human before proceeding

---

## Checkpoint: After Tasks 4-6

- [ ] nix/pyproject.nix is handled correctly (removed or documented)
- [ ] nix flake check passes
- [ ] nix develop works correctly
- [ ] All expected tools are available
- [ ] Ready for documentation update

---

## Checkpoint: Complete

- [ ] All acceptance criteria met
- [ ] Documentation updated
- [ ] Changes committed and pushed
- [ ] Ready for review
