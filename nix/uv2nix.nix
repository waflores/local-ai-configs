# Local Python package built from pyproject.toml + uv.lock
# Uses pyproject-nix/uv2nix to convert uv.lock into a Nix build.
#
# The uv2nix input provides:
#   - uv2nix.mkPyproject: function that reads uv.lock and generates
#     the dependency graph for buildPythonPackage.
#   - Each dependency from uv.lock is available as a Nix derivation.
#
# Configuration:
#   - uv2nix = pyproject-nix/uv2nix (flake input, see flake.nix)
#   - pyproject = ./pyproject.toml (project metadata)
#   - uv.lock = ./uv.lock (dependency lock file)

{ pkgs, uv2nix, ... }:
let
  # Generate the pyproject from uv.lock using the uv2nix function
  # This converts the uv.lock into a format compatible with
  # buildPythonPackage's dependency resolution.
  project = uv2nix.mkPyproject {
    pyproject = ./pyproject.toml;
    uv.lock = ./uv.lock;
  };

  # Extract the dependency list from the generated pyproject
  # The uv2nix output provides dependencies as a list of { name, pkg }
  # which can be passed directly to buildPythonPackage.
  buildDeps = project.dependencies or [ ];

in
pkgs.python3.pkgs.buildPythonPackage {
  pname = "local-config";
  version = "0.1.0";
  pyproject = true;
  src = ./.;

  # Dependencies from uv.lock (converted to Nix by uv2nix)
  buildInputs = buildDeps;

  # The local-config package is the python package itself.
  # buildPythonPackage with pyproject = true handles the build.
  # Installs the package via pyproject build backend.
}
