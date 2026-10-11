# Local Python package built from pyproject.toml
# blueprint maps nix/packages/default.nix to packages.default
# The pyproject.nix builder is used here directly.
{ pkgs, ... }:
{
  default = import ../pyproject.nix { inherit pkgs; };
}
