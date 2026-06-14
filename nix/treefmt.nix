_: {
  projectRootFile = "flake.nix";

  programs = {
    nixfmt.enable = true;
    yamlfmt.enable = true;
    deadnix.enable = true;
    shellcheck.enable = true;
    shfmt.enable = true;
    mdformat.enable = true;
    black.enable = true;
    ruff.enable = true;
  };
}
