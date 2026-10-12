{
  description = "Flake with treefmt-nix, git-hooks.nix, and nixfmt";

  # x86_64-linux only. We keep the blueprint flake input but restrict the
  # systems blueprint generates outputs for to x86_64-linux, dropping the
  # cross-compilation machinery for aarch64-darwin and x86_64-darwin that
  # blueprint would otherwise emit. This keeps `nix flake show` fast and
  # focused on our single target platform.
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    blueprint.url = "github:numtide/blueprint";
    blueprint.inputs.nixpkgs.follows = "nixpkgs";
    treefmt.url = "github:numtide/treefmt-nix";
    treefmt.inputs.nixpkgs.follows = "nixpkgs";
    git-hooks.url = "github:cachix/git-hooks.nix";
    git-hooks.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    inputs:
    inputs.blueprint {
      inherit inputs;
      # Restrict systems to x86_64-linux only, so blueprint generates
      # outputs for a single platform (no cross-compilation machinery).
      systems = [ "x86_64-linux" ];
      nixpkgs.config.allowUnfreePredicate = pkg: builtins.elem (inputs.nixpkgs.lib.getName pkg) [ ];
      # Import the nix/ modules into blueprint's module scope.
      # The packages/ directory maps to packages.<system> (e.g.
      # packages.x86_64-linux), and devshells/ maps to devShells.<system>
      # (e.g. devShells.x86_64-linux).
      prefix = ./nix;
    };
}
