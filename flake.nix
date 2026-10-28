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
    let
      # blueprint's packages.${system}.default is a set
      # { default, override, overrideDerivation } in newer nixpkgs,
      # instead of a raw derivation. Flatten it so flake check /
      # nix build / nix build .#packages.x86_64-linux.default work.
      flattenPackages = self: {
        x86_64-linux = {
          default = self.packages.x86_64-linux.default.default;
        };
      };
    in
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
      # Override the packages output, flattening the set produced by
      # blueprint's mkPackagesFor (packages.x86_64-linux.default is now
      # a set { default, override, overrideDerivation }, not a derivation).
      packages = flattenPackages blueprintOut;
      # Re-expose the remaining outputs the flake expects.
      lib = blueprintOut.lib;
      legacyPackages = blueprintOut.legacyPackages;
      nixosConfigurations = blueprintOut.nixosConfigurations;
      darwinConfigurations = blueprintOut.darwinConfigurations;
      systemConfigs = blueprintOut.systemConfigs;
      robotnixConfigurations = blueprintOut.robotnixConfigurations;
      nixOnDroidConfigurations = blueprintOut.nixOnDroidConfigurations;
      modules = blueprintOut.modules;
      devShells = blueprintOut.devShells;
      checks = blueprintOut.checks;
      formatter = blueprintOut.formatter;
      homeModules = blueprintOut.homeModules;
      nixosModules = blueprintOut.nixosModules;
      darwinModules = blueprintOut.darwinModules;
      templates = blueprintOut.templates;
    };
}
