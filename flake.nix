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
    uv2nix.url = "github:pyproject-nix/uv2nix";
    uv2nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    inputs:
    let
      # Evaluate blueprint once to access its outputs.
      blueprintOut = inputs.blueprint {
        inherit inputs;
        systems = [ "x86_64-linux" ];
        nixpkgs.config.allowUnfreePredicate = pkg: builtins.elem (inputs.nixpkgs.lib.getName pkg) [ ];
        # Import the nix/ modules into blueprint's module scope.
        prefix = ./nix;
      };
    in
    {
      # Override the packages output, using the blueprint's packages output
      # which is a function that takes the inputs as arguments.
      packages = (blueprintOut.packages.x86_64-linux).default {
        inherit inputs;
      };
      inherit (blueprintOut)
        lib
        legacyPackages
        nixosConfigurations
        darwinConfigurations
        systemConfigs
        robotnixConfigurations
        nixOnDroidConfigurations
        modules
        devShells
        checks
        formatter
        homeModules
        nixosModules
        darwinModules
        templates
        ;
    };
}
