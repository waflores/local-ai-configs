{ pkgs, ... }:
pkgs.python3.pkgs.buildPythonPackage {
  pname = "local-config";
  version = "0.1.0";
  pyproject = true;
  src = ../.;
  # The project's build-system requires uv_build (see pyproject.toml),
  # and the pre-commit hooks use `uv run` to run ruff. pkgs.uv is the
  # Python uv package (it ships the uv_build module and the uv CLI).
  # Add it to buildInputs so the pyproject-hooks step can import uv_build.
  buildInputs = [ pkgs.uv ];
}
