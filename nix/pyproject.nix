{ pkgs, ... }:
{
  # Python package generated from root pyproject.toml.
  # buildPythonPackage auto-discovers pyproject.toml when `pyproject = true`.
  local-config = pkgs.python3.pkgs.buildPythonPackage {
    pname = "local-config";
    version = "0.1.0";
    pyproject = true;
    src = ./.;
    # Dependencies are managed in pyproject.toml via uv; the nix build
    # derives them from the pyproject metadata.
  };
}
