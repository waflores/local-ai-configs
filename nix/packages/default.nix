# Local Python package built from pyproject.toml + uv.lock using uv2nix
# blueprint maps nix/packages/default.nix to packages.default
# The uv2nix builder is used to generate the package from the project's dependencies.

{ pkgs, uv2nix, ... }:
{
  default = import ../uv2nix.nix { inherit pkgs uv2nix; };
}
