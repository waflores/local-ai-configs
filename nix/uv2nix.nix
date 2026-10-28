# Local Python package built from pyproject.toml + uv.lock using uv2nix
# Uses github:pyproject-nix/uv2nix to convert uv.lock into a Nix build.
#
# The uv2nix input provides:
#   - uv2nix.lib.workspace.loadWorkspace: loads the uv workspace
#   - workspace.mkPyprojectOverlay: creates an overlay for the dependencies
#   - pyproject-nix builders (via pyproject-nix.build.packages)
#
# Configuration:
#   - uv2nix = github:pyproject-nix/uv2nix (flake input, see flake.nix)
#   - pyproject = ./pyproject.toml (project metadata)
#   - uv.lock = ./uv.lock (dependency lock file)

{ pkgs, uv2nix, ... }:
let
  # Load the uv workspace
  workspace = uv2nix.lib.workspace.loadWorkspace {
    workspaceRoot = ./.;
  };

  # Create a pyproject overlay from uv.lock
  # This generates an overlay that adds the uv.lock dependencies to the Python environment
  overlay = workspace.mkPyprojectOverlay {
    sourcePreference = "wheel";
  };

  # Create the Python package using buildPythonPackage
  # The overlay adds the uv.lock dependencies to the Python environment
  localConfig = pkgs.python3.pkgs.buildPythonPackage {
    pname = "local-config";
    version = "0.1.0";
    pyproject = true;
    src = ./.;

    # Dependencies from uv.lock (converted to Nix by uv2nix)
    # The overlay will provide the correct dependencies
    buildInputs = (workspace.deps.default or [ ]);

    # The local-config package is the python package itself.
    # buildPythonPackage with pyproject = true handles the build.
    # Installs the package via pyproject build backend.
  };

in
localConfig
