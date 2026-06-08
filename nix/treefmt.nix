_: {
  projectRootFile = "flake.nix";

  programs = {
    nixfmt.enable = true;
    # yamllint.enable = true;
    yamlfmt.enable = true;
    shellcheck.enable = true;
    shfmt.enable = true;
    mdformat.enable = true;
    black.enable = true;
    ruff.enable = true;
  };
}
