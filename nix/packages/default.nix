# Local Python package built from pyproject.toml + uv.lock.
# Uses pyproject-nix/uv2nix to convert uv.lock into a Nix build.
#
# This file is a blueprint module: blueprint imports this file and evaluates it
# as a Nix module with the scope { pkgs, system, flake, inputs, perSystem, pname }.
# The flake inputs (including uv2nix) are available via inputs.uv2nix.
# blueprint maps this file to packages.x86_64-linux.local-config.

{
  pkgs,
  uv2nix ? null,
  ...
}:
let
  # Generate the pyproject from uv.lock using the uv2nix function.
  # This converts uv.lock into a format compatible with buildPythonPackage.
  project =
    if uv2nix != null then
      uv2nix.mkPyproject {
        pyproject = ./pyproject.toml;
        uv.lock = ./uv.lock;
      }
    else
      { };
in
pkgs.python3.pkgs.buildPythonPackage {
  pname = "local-config";
  version = "0.1.0";
  pyproject = true;
  src = ./.;
  # Dependencies from uv.lock (converted to Nix by uv2nix)
  buildInputs = project.dependencies or [ ];
}
