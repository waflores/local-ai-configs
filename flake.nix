{
  description = "Minimal flake: builds the Python package from pyproject.toml + uv.lock (via uv2nix) and provides dev/format shells on x86_64-linux.";

  # x86_64-linux only. Keeps `nix flake show` fast and focused on our single
  # target platform. No cross-compilation machinery.
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    uv2nix.url = "github:pyproject-nix/uv2nix";
    uv2nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    inputs:
    let
      system = "x86_64-linux";
      pkgs = inputs.nixpkgs.legacyPackages.${system};

      # Build the local Python package from pyproject.toml + uv.lock.
      localPackage = (
        with pkgs;
        python3.pkgs.buildPythonPackage {
          pname = "local-config";
          version = "0.1.0";
          src = ./.;
          pyproject = true;
          nativeBuildInputs = [ uv ];
          buildPhase = ''
            runHook preBuild
            uv sync --locked --no-dev
            uv build
          '';
          meta = {
            description = "Toolkit for managing local models";
            license = "MIT";
            platforms = [ system ];
          };
        }
      );

      # Dev shell with all the tools developers need: uv, pre-commit, statix,
      # ruff, nixfmt, and the nix fmt / nix fmt --check commands.
      devShell = pkgs.mkShell {
        packages = [
          pkgs.uv
          pkgs.pre-commit
          pkgs.statix
          pkgs.ruff
          pkgs.nixfmt
        ];
        shellHook = ''
          echo "local-config dev shell"
          echo "  nix fmt                 # run nixfmt + ruff format + yamlfmt"
          echo "  nix fmt --check         # verify formatting is clean"
          echo "  ruff check .            # lint python files"
          echo "  ruff format --check .   # verify python formatting"
        '';
      };

      # Formatting tooling (alternative to the old treefmt wrapper).
      # The ruff + nixfmt + yamlfmt tools are available in the default dev
      # shell. The .pre-commit config provides the full lint set.
      legacyPackages = {
        "x86_64-linux" = pkgs;
      };
    in
    {
      packages = {
        "x86_64-linux" = {
          default = localPackage;
        };
      };
      devShells = {
        "x86_64-linux" = {
          default = devShell;
        };
      };
      formatter = {
        "x86_64-linux" = {
          default = devShell;
        };
      };
      legacyPackages = legacyPackages;
    };
}
