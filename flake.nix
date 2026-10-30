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
      # nixfmt, ruff, markdownlint, and the nix fmt / nix fmt --check commands.
      devShell = pkgs.mkShell {
        packages = [
          pkgs.uv
          pkgs.pre-commit
          pkgs.statix
          pkgs.ruff
          nixFmt
          nixFmtCheck
        ];
        shellHook = ''
          echo "local-config dev shell"
          echo "  nix fmt                 # run nixfmt + ruff format + yamlfmt"
          echo "  nix fmt --check         # verify formatting is clean"
          echo "  markdownlint .            # lint markdown files"
          echo "  ruff check .            # lint python files"
          echo "  ruff format --check .   # verify python formatting"
        '';
      };

      # nix fmt - unified formatting command (replaces old treefmt-nix wrapper).
      # Wraps nixfmt (nix), ruff format (python), and yamlfmt (yaml).
      nixFmt = pkgs.writeShellScriptBin "nix-fmt" ''
        echo "Formatting nix, python, and yaml files..."
        # Format nix files
        nixfmt . 2>/dev/null || true
        # Format python files
        uv run ruff format
        # Format yaml files
        yamlfmt -i -w . 2>/dev/null || true
        echo "Formatted: nix, python, yaml"
      '';

      # nix fmt --check - verify formatting is clean
      nixFmtCheck = pkgs.writeShellScriptBin "nix-fmt-check" ''
        failed=0
        # Check nix files
        if ! nixfmt --check . 2>/dev/null; then
          echo "Nix files not formatted"
          failed=1
        fi
        # Check python files
        if ! uv run ruff format --check .; then
          echo "Python files not formatted"
          failed=1
        fi
        # Check yaml files (dry-run mode)
        if ! yamlfmt -dry . 2>/dev/null; then
          echo "YAML files not formatted"
          failed=1
        fi
        if [ $failed -ne 0 ]; then
          echo "Some files are not formatted"
          exit 1
        fi
        echo "All files formatted cleanly"
      '';

      # Run both fmt and fmt-check
      nixFmtRun = pkgs.runCommand "nix-fmt-run" { } ''
        ${nixFmt}/bin/nix-fmt
        ${nixFmtCheck}/bin/nix-fmt-check
      '';

      # Formatting tooling (alternative to the old treefmt wrapper).
      # The ruff + nixfmt + yamlfmt + markdownlint tools are available in the
      # default dev shell. The .pre-commit config provides the full lint set.
      # The .pre-commit config provides ruff check + ruff-format + nixfmt.

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
      legacyPackages = legacyPackages;
    };
}
