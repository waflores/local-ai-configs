# devShell definition for blueprint
# This file is a blueprint module: blueprint imports this file and evaluates it
# as a Nix module with the scope { pkgs, system, flake, inputs, perSystem, pname }.
# The flake inputs (including uv2nix) are available via inputs.uv2nix.

{
  pkgs,
  uv2nix ? null,
  ...
}:
{
  default = import ../devshell.nix {
    inherit pkgs uv2nix;
  };
}
