{ pkgs, ... }:
pkgs.python3.pkgs.buildPythonPackage {
  pname = "local-config";
  version = "0.1.0";
  pyproject = true;
  src = ../.;
}
